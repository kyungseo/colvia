"""Single-use Host orchestration over explicitly qualified runtime/process ports.

This is not a managed command or a runtime discovery fallback. The composition
root supplies a launch port that binds and rechecks executable, policy, paths and
environment against the grant. Persisted history never recreates this live owner.
Process closure is evidence, not result acceptance or a rollback of document bytes.
"""
from ..codec import RecordError,PublicationRefused,require
from . import schema


def stop_reason(error):
    code=getattr(error,'code',None)
    if code in schema.REASONS:return code
    if code in ('execution-cancel-requested','delivery-cancelled'):return 'cancelled'
    if isinstance(error,TimeoutError) or code=='execution-deadline':return 'deadline'
    return 'internal_error'


def revoke_reason(cancelled,error):return 'cancelled' if cancelled else stop_reason(error)


def terminal_value(history,cancelled,error,completed):
    """Pure outcome derivation shared by live and known-unstarted closure."""
    successful=completed and error is None and not cancelled and history.seal is not None
    certain=history.processes_closed() and history.pending is None and not history.latch and history.effect()!='unknown'
    status=('completed' if successful else 'revoked-before-launch' if history.runtime_failure or history.runtime_intent is None else 'interrupted') if certain else 'unknown'
    return dict(status=status,stop_reason=None if status=='completed' else revoke_reason(cancelled,error),
        document_write_effect=history.effect(),effect_refs=history.effect_refs(),closure_refs=history.closure_refs())


class RuntimeSupervisor:
    def __init__(self,gate,launch,processes,channel_factory,session_factory):
        self.gate=gate;self.launch=launch;self.processes=processes
        self.channel_factory=channel_factory;self.session_factory=session_factory
        self.used=False;self.process=None;self.known={};self.closure=None

    def _record_children(self):
        if self.gate.failed:return
        history=self.gate.journal.read(self.gate.run)[-1]
        if history.runtime_start is None:return
        for pid,row in sorted(self.known.items()):
            if pid==self.process.pid:continue
            child=dict(pid=pid,birth=row['birth'])
            if child not in history.children:
                self.gate.append('runtime-child',child)
                history=self.gate.journal.read(self.gate.run)[-1]

    def _close(self):
        gate=self.gate;process=self.process
        try:
            require(process.pid in self.known,'execution-runtime-identity-unavailable')
            closed=self.processes.stop(process,self.known,seconds=8)
            require(closed.get('group_absent') is True and closed.get('final_scan_confirmed') is True,'closure_unconfirmed')
            expected=[dict(pid=pid,birth=row['birth'],absent=True) for pid,row in sorted(self.known.items()) if pid!=process.pid]
            require(closed.get('children')==expected,'execution-child-closure-mismatch')
            self.closure=closed
        except BaseException:
            # An owned Popen handle can be killed/reaped without adopting an
            # unidentified process group. This NEVER proves descendant closure.
            try:self.processes.abort_owned(process,seconds=2)
            finally:self._record_children()
            raise
        self._record_children()
        if gate.failed:return
        history=gate.journal.read(gate.run)[-1]
        require(history.runtime_start is not None and history.runtime_start['value']==dict(ordinal=1,pid=process.pid,birth=self.known[process.pid]['birth']),'execution-runtime-identity-unavailable')
        require(all(child in [dict(pid=r['pid'],birth=r['birth']) for r in expected] for child in history.children),'execution-child-closure-mismatch')
        gate.append('processes-closed',dict(runtime_ref=history.runtime_start['seq'],group_absent=True,
            final_scan_confirmed=True,children=[dict(child,absent=True) for child in history.children]))

    def _terminal(self,error,completed):
        gate=self.gate
        if gate.failed:return
        history=gate.journal.read(gate.run)[-1]
        cancelled=gate.journal.cancel_requested(gate.run,gate.owner)
        successful=completed and error is None and not cancelled and history.seal is not None
        if not successful and not history.revoked:
            gate.append('revoked',dict(reason=revoke_reason(cancelled,error)))
            history=gate.journal.read(gate.run)[-1]
        value=terminal_value(history,cancelled,error,completed);status=value['status']
        try:gate.append('terminal',value)
        except PublicationRefused:
            # Only a proved non-commit and an actual cancel allow a different
            # terminal decision. Other conflicts still stop without a replay.
            if status!='completed' or not gate.journal.cancel_requested(gate.run,gate.owner):raise
            self._terminal(RecordError('cancelled'),False)

    def run(self,policy,controller):
        require(not self.used,'execution-supervisor-consumed');self.used=True
        gate=self.gate
        error=None;channel=None;session=None;completed=False;io_error=None
        try:
            policy.bind(gate.grant.payload['contract'])
            plan=self.launch.prepare(gate.grant,policy)
            self.launch.verify(plan,gate.grant,policy)
            host=self.launch.host_identity();schema.integer(host['pid'],2,(1<<31)-1);schema.birth(host['birth'])
            gate.authority()
            require(gate.journal.read(gate.run)[-1].runtime_intent is None,'execution-runtime-already-reserved')
            gate.append('runtime-reserved',dict(ordinal=1,host_pid=host['pid'],host_birth=host['birth']))
            try:
                # Reservation may take time. Recheck directly on both sides of
                # spawn; the port remains trusted, not hostile-same-user isolation.
                self.launch.verify(plan,gate.grant,policy);gate.authority()
            except BaseException:
                gate.append('runtime-spawn-failed',dict(ordinal=1,reason='spawn_failed',reaped=True))
                raise
            try:self.process=self.processes.launch(plan.argv,cwd=plan.cwd,env=plan.env)
            except (OSError,ValueError):
                gate.append('runtime-spawn-failed',dict(ordinal=1,reason='spawn_failed',reaped=True))
                raise
            try:
                self.processes.admit_io(self.process)
                identity=self.processes.identity(self.process)
                require(identity.get('pid')==self.process.pid,'execution-runtime-identity-unavailable')
                require(identity.get('birth') is not None,'execution-runtime-identity-unavailable')
                schema.birth(identity['birth'])
            except BaseException:
                gate.append('runtime-started',dict(ordinal=1,pid=self.process.pid,birth=None));raise
            self.known[self.process.pid]={'birth':identity['birth']}
            gate.append('runtime-started',dict(ordinal=1,pid=self.process.pid,birth=identity['birth']))
            self.launch.verify(plan,gate.grant,policy);gate.authority()
            channel=self.channel_factory(self.process,deadline=gate.deadline)
            session=self.session_factory(gate,policy,channel,cwd=plan.cwd)
            require(session.run(controller)=='completed','protocol_premature_completion')
            require(gate.journal.read(gate.run)[-1].seal is not None,'protocol_premature_completion')
            completed=True
        except BaseException as exc:
            error=exc
            # Only an identified live session may attempt its one bounded cancel.
            # A corrupt/failed session or elapsed deadline is not replayed.
            if session is not None and stop_reason(exc)=='cancelled' and not session.failed and session.thread is not None and session.turn is not None:
                try:session.interrupt()
                except BaseException as interrupt_error:
                    interrupt_error.__cause__=error;error=interrupt_error
        finally:
            if self.process is not None:
                try:self._close()
                except BaseException as close_error:
                    close_error.__cause__=error;error=close_error
                finally:
                    # Both concrete closers are non-flushing, owned-resource
                    # operations. IO diagnostics do not rewrite execution truth.
                    closers=([channel.close] if channel is not None else [])
                    closers.append(lambda:self.processes.close_io(self.process))
                    for close in closers:
                        try:close()
                        except BaseException as secondary:
                            if io_error is None:io_error=secondary
            try:self._terminal(error,completed)
            except BaseException as publication_error:
                publication_error.__cause__=error;error=publication_error
        if error is not None:
            if io_error is not None:error.add_note('owned-io-cleanup-failed')
            raise error
        value=gate.journal.status(gate.run)
        diagnostics=list(getattr(controller,'diagnostics',()))
        if io_error is not None:diagnostics.append('owned-io-cleanup-failed')
        if diagnostics:value=dict(value,diagnostics=sorted(set(diagnostics)))
        return value
