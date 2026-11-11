"""One admitted callback through a qualified native document worker port.

The port supplies a verified immutable launch plan and observes result bytes.
There is no shell-command fallback. A native process and history publication are
separate effects; uncertainty never turns into permission to repeat the spawn.
"""
import io,time,uuid
from ..codec import require,RecordError
from ..bodies import ingest_body
from .guards import wire_bytes,reject_duplicate_keys
from . import schema
import json

ROLES={'document_read':'read','document_write':'write','document_verify':'verify'}

class DocumentController:
    def __init__(self,gate,native,processes,exchange):
        self.gate=gate;self.native=native;self.processes=processes;self.exchange=exchange
        self.active=None;self.unclosed=False;self.diagnostics=[]
    def request(self,reservation,history):
        require(type(reservation) is dict and set(reservation)=={'callback_id','tool','arguments'},'input_shape')
        callback=history.pending;require(callback is not None and reservation['callback_id']==callback,'order_mismatch')
        item=history.callbacks[callback];expected=item['reservation']['value']
        require(item['worker'] is None and reservation['tool'] in ROLES and ROLES[reservation['tool']]==expected['tool'],'order_mismatch')
        args=reservation['arguments'];scope=self.gate.scope;output=scope['output_id']
        require(type(args) is dict,'input_shape')
        if expected['tool']=='read':require(args=={'file_ids':scope['read_ids']},'scope_mismatch')
        elif expected['tool']=='write':
            require(set(args)=={'file_id','expected_sha256','content'} and args['file_id']==output and
                args['expected_sha256']==scope['documents'][output]['original_identity']['sha256'] and type(args['content']) is str,'scope_mismatch')
        else:require(args=={'verifier_id':expected['verifier_id']},'order_mismatch')
        return callback,expected['tool'],args
    def dispatch(self,reservation):
        try:return self._dispatch(reservation)
        except BaseException:
            # The callback can exist even when its worker intent was refused.
            # Close only the proved no-worker case; never guess about a spawn.
            if not self.gate.failed and self.active is None and not self.unclosed:
                history=self.gate.journal.read(self.gate.run)[-1]
                if history.pending is not None and history.callbacks[history.pending]['worker'] is None:
                    self.gate.complete()
            raise
    def _dispatch(self,reservation):
        gate=self.gate;require(self.active is None and not self.unclosed,'execution-worker-unavailable')
        history=gate.authority();callback,role,args=self.request(reservation,history)
        ordinal=len(history.workers)+1;tool=reservation['tool']
        self.native.callback_preflight(gate.grant,history,tool,args,gate.deadline)
        plan=self.native.materialize(gate.grant,history,tool,args,ordinal)
        request=wire_bytes({'tool':tool,'arguments':args});require(len(request)<=131072,'input_shape')
        deadline=min(gate.deadline-5,time.monotonic()+60);require(deadline>time.monotonic(),'deadline')
        gate.authority();self.native.callback_preflight(gate.grant,history,tool,args,gate.deadline)
        self.native.verify_plan(plan)
        gate.append('worker-spawn-intent',dict(callback_id=callback,worker_ordinal=ordinal,role=role,
            code_identity=gate.scope['resources']['worker_digest']))
        try:self.active=self.processes.launch(plan.argv,cwd=plan.cwd,env=plan.env)
        except (OSError,ValueError):
            gate.append('worker-spawn-failed',dict(worker_ordinal=ordinal,reason='spawn_failed',reaped=True))
            raise
        process=self.active;known={};started=False;result_recorded=False;reply=None;after=None;body=None
        success=False;reason='worker_failed';original=gate.scope['documents'][gate.scope['output_id']]['original_identity'] if role=='write' else None
        error=None;publication_error=None;closed=None;io_error=None
        try:
            try:
                self.processes.admit_io(process)
                identity=self.processes.identity(process)
                require(identity.get('pid')==process.pid and identity.get('birth') is not None,'execution-worker-identity-unavailable')
                schema.birth(identity['birth'])
            except BaseException:
                gate.append('worker-started',dict(worker_ordinal=ordinal,pid=process.pid,birth=None));started=True
                raise
            if identity['birth'] is not None:known[process.pid]={'birth':identity['birth']}
            gate.append('worker-started',dict(worker_ordinal=ordinal,**identity));started=True
            require(identity['birth'] is not None,'execution-worker-identity-unavailable')
            # Cancellation prevents admission, not an already-admitted write's
            # bounded evidence collection. Deadline/unknown effects still stop.
            cancelled=(lambda:False) if role=='write' else (lambda:gate.journal.cancel_requested(gate.run,gate.owner))
            raw,diagnostic_bytes=self.exchange(process,request,deadline=deadline,cancelled=cancelled)
            if diagnostic_bytes:
                gate.append('diagnostic',dict(source='worker',phase='worker',reason='worker_failed',byte_count=diagnostic_bytes))
            require(process.returncode==0 and diagnostic_bytes==0,'worker_failed')
            response=json.loads(raw,object_pairs_hook=reject_duplicate_keys)
            require(type(response) is dict and set(response)=={'ok','result'} and response['ok'] is True,'worker_failed')
            reply,after,body=self.native.validate_result(gate.grant,tool,args,response['result'],plan,gate.deadline)
            success=role!='verify' or reply['pass'] is True;reason=None if success else 'verifier_failed'
        except BaseException as exc:error=exc
        finally:
            try:
                if started and not gate.failed:
                    options={}
                    if success and role=='write':
                        require(type(body) is bytes and after is not None,'execution-result-body-required')
                        operation='execution-body-'+uuid.uuid4().hex
                        gate.journal.store.begin_import(operation,'execution-result')
                        pair=ingest_body(io.BytesIO(body),gate.journal.store,operation)
                        options=dict(result_body=pair[0],objects=[pair],import_id=operation)
                    gate.append('worker-result',dict(worker_ordinal=ordinal,success=success,
                        effect=('applied' if success else 'unknown') if role=='write' else 'none',
                        before=original,after=after,verifier_id=args.get('verifier_id'),
                        verifier_pass=reply['pass'] if role=='verify' and reply is not None and reason in (None,'verifier_failed') else None,
                        reason=reason),**options)
                    result_recorded=True
            except BaseException as exc:
                publication_error=exc
                if error is not None:
                    publication_error.__cause__=error;publication_error.__suppress_context__=True
            finally:
                try:
                    closed=self.processes.stop(process,known,seconds=5)
                    require(closed['group_absent'] is True and closed['final_scan_confirmed'] is True,'closure_unconfirmed')
                    if started and result_recorded and not gate.failed:
                        gate.append('worker-closed',dict(worker_ordinal=ordinal,returncode=closed['returncode'],
                            group_absent=True,birth_absent=True))
                    self.active=None
                except BaseException as closure_error:
                    self.unclosed=True
                    # Same owned-handle fallback as the runtime supervisor. It
                    # never proves worker/group closure or clears uncertainty.
                    try:self.processes.abort_owned(process,seconds=2)
                    except BaseException as abort_error:
                        abort_error.__cause__=closure_error;closure_error=abort_error
                    # Keep the primary failure when closure also fails. Do not
                    # serialize exception text into records or runtime replies.
                    if publication_error is not None:raise closure_error from publication_error
                    if error is not None:raise closure_error from error
                    raise
                finally:
                    try:self.processes.close_io(process)
                    except BaseException as secondary:io_error=secondary
        if publication_error is not None:raise publication_error from error
        if error is not None:raise error
        require(closed is not None and closed['returncode']==0,'worker_failed')
        require(gate.complete(),'verifier_failed')
        if io_error is not None:self.diagnostics.append('worker-owned-io-cleanup-failed')
        return gate.checked_reply(reply)
