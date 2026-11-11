"""Compose the reviewed journal/session/worker ports without granting execution.

The caller has already started an exact authorized grant and holds the project
native effect lock. No CLI lookup, authentication, runtime selection or Work
acceptance happens here. A qualified installed composition root is still needed.
"""
from ..codec import require,RecordError,PublicationRefused
from .callbacks import CallbackGate
from .worker import DocumentController
from .supervisor import RuntimeSupervisor

class RuntimeBoundBackend:
    """Recheck the same runtime binding at every document admission/reply edge."""
    def __init__(self,backend,launch,policy):
        self.backend=backend;self.launch=launch;self.policy=policy
        self.grant=None;self.plan=None
    def _verify(self,grant):
        require(self.grant is not None and grant.ref==self.grant.ref and self.plan is not None,'execution-runtime-binding-unavailable')
        self.launch.verify(self.plan,grant,self.policy)
    def startup(self,grant,history,deadline):
        require(self.grant is None,'execution-runtime-binding-consumed')
        self.plan=self.launch.prepare(grant,self.policy);self.grant=grant
        self._verify(grant);self.backend.startup(grant,history,deadline)
    def assert_held(self,grant,owner):self.backend.assert_held(grant,owner)
    def preflight(self,grant,history):
        self._verify(grant);self.backend.preflight(grant,history)
    def callback_preflight(self,grant,history,tool,args,deadline):
        self._verify(grant);self.backend.callback_preflight(grant,history,tool,args,deadline)
    def save_original(self,grant,history):
        self._verify(grant);return self.backend.save_original(grant,history)
    def materialize(self,grant,history,tool,args,ordinal):
        self._verify(grant);return self.backend.materialize(grant,history,tool,args,ordinal)
    def verify_plan(self,plan):
        self._verify(self.grant);self.backend.verify_plan(plan)
    def validate_result(self,grant,tool,args,value,plan,deadline):
        # This is Host evidence collection after a possible write, not runtime
        # admission. Record the observable effect first; checked_reply/next gate
        # will recheck runtime identity before any further model interaction.
        return self.backend.validate_result(grant,tool,args,value,plan,deadline)

class DocumentHost:
    def __init__(self,journal,run,*,backend,launch,policy,runtime_processes,worker_processes,
                 channel_factory,session_factory,worker_exchange):
        require(backend.journal is journal,'execution-host-journal-mismatch')
        native=RuntimeBoundBackend(backend,launch,policy)
        gate=CallbackGate(journal,run,native)
        self.controller=DocumentController(gate,native,worker_processes,worker_exchange)
        self.supervisor=RuntimeSupervisor(gate,launch,runtime_processes,channel_factory,session_factory)
        self.policy=policy
    def run(self):return self.supervisor.run(self.policy,self.controller)


def run_document_host(journal,run,*,claim,lock,**ports):
    """A live caller holds lock across start/construction/run, never a resume.

    claim is the exact (state, grant, owner) returned by this caller's acknowledged
    start. Startup ports are read-only: no recovery write, intent or process.
    A failed start acknowledgement must not enter this function.
    """
    from .unstarted import close_unstarted
    require(lock.locked,'effect-lock-required')
    state,grant,_,owner,history=journal.read(run)
    require((state.ref,grant.ref,owner.ref)==claim and len(history.rows)==1,'execution-live-restore-refused')
    try:host=DocumentHost(journal,run,**ports)
    except BaseException as original:
        try:close_unstarted(journal,run,claim=claim,lock=lock,error=original)
        except BaseException as secondary:
            # Never hide a possibly committed revocation/terminal behind the
            # constructor error. Preserve the original exception and its cause.
            unchanged=False
            if isinstance(secondary,PublicationRefused):
                try:
                    current=journal.read(run)
                    unchanged=(current[0].ref,current[1].ref,current[3].ref)==claim
                except BaseException:pass
            elif isinstance(secondary,RecordError):
                unchanged=secondary.code in ('effect-lock-required','execution-startup-owner-changed','execution-startup-not-fresh')
            if unchanged:raise original
            raise RecordError('execution-startup-closure-unknown') from original
        raise
    return host.run()
