"""Live composition boundary: preparation, one start, and delivery ownership.

Adapters are selected by source-owned managed factories, never by command input.
Readonly status and independent cancellation deliberately bypass the native
execution lock. Persisted runs cannot reconstruct a live owner.
"""
from ..codec import require,RecordError
from ..records import link
from ..effects import PENDING
from .journal import prepared_key,key
from .host import run_document_host
from . import schema

class DocumentExecution:
    def __init__(self,journal,*,lease,effects,adapter):
        self.journal=journal;self.lease=lease;self.effects=effects;self.adapter=adapter
    def prepare(self,*,operation,run,contract,request):
        with self.lease.hold():
            self.adapter.qualify()
            schema.grant_record(contract);schema.request_record(request,contract)
            with self.effects.exclusion():
                material=self.adapter.material(contract,request)
                return self.journal.prepare(operation=operation,run=run,contract=contract,request=request,**material)
    def _prepared(self,run):
        require(self.journal.store.head(key(run)) is None,'execution-live-restore-refused')
        ref=self.journal.store.head(prepared_key(run));require(ref is not None,'execution-grant-required')
        grant=self.journal.grant(ref,self.journal.store.load)
        self.adapter.qualify();ports=self.adapter.ports(grant)
        return grant,ports
    def _start(self,*,operation,run,receipt,statement,ports,parent=None):
        self.journal.start(operation=operation,run=run,receipt=receipt,statement=statement,parent=parent)
        # Reached only after the publisher acknowledged start. A lost response
        # leaves inspection/recovery to the caller; never infer non-commit.
        state,grant,_,owner,history=self.journal.read(run)
        require(len(history.rows)==1 and link(owner,'parent')==parent,'execution-start-claim-changed')
        return run_document_host(self.journal,run,claim=(state.ref,grant.ref,owner.ref),lock=self.effects,**ports)
    def start(self,*,operation,run,receipt,statement):
        with self.lease.hold():
            self.adapter.qualify()
            with self.effects.exclusion():
                _,ports=self._prepared(run)
                return self._start(operation=operation,run=run,receipt=receipt,statement=statement,ports=ports)
    def delivery(self,*,operation,delivery):
        from ..delivery.service import DeliveryService
        service=DeliveryService(self.journal.service)
        with self.lease.hold():
            self.adapter.qualify()
            with self.effects.exclusion():
                state,request=service.read(delivery)
                require(request.payload['action']=='execute','delivery-not-execution')
                if state.payload['phase']=='active':
                    return service.finish_unstarted_execution(operation=operation+'-unstarted',delivery=delivery,effects=self.effects)
                require(state.payload['phase']=='queued','delivery-not-claimable')
                grant=self.journal.grant(link(request,'grant'),self.journal.store.load);run=grant.payload['run']
                prepared,ports=self._prepared(run);require(prepared.ref==grant.ref,'execution-grant-changed')
                service.claim(operation=operation+'-claim',delivery=delivery,effects=self.effects)
                parent=self.journal.store.head(PENDING)
                try:
                    receipt=self.journal.service._receipt('execution-start',grant.payload['work'],grant.ref)
                    result=self._start(operation=operation+'-start',run=run,receipt=receipt,
                        statement='Run the exact grant in the accepted delivery request.',ports=ports,parent=parent)
                except BaseException as original:
                    # Claim was acknowledged. Finalize only proved no-child or
                    # a closed matching child; never replay child publication.
                    try:
                        if self.journal.store.head(key(run)) is None:
                            service.finish_unstarted_execution(operation=operation+'-unstarted',delivery=delivery,effects=self.effects)
                        else:
                            _,_,_,owner,history=self.journal.read(run)
                            if link(owner,'parent')==parent and history.terminal in schema.CLOSED:
                                service.finish_execution(operation=operation+'-finish',delivery=delivery,run=run,effects=self.effects)
                    except BaseException:
                        raise RecordError('delivery-closure-unknown') from original
                    raise
                service.finish_execution(operation=operation+'-finish',delivery=delivery,run=run,effects=self.effects)
                return dict(result,delivery=service.status(delivery))

    def finish_delivery(self,*,operation,delivery):
        """Explicit metadata-only finish after a closed child, never a resume."""
        from ..delivery.service import DeliveryService
        service=DeliveryService(self.journal.service)
        with self.lease.hold(),self.effects.exclusion(create=False):
            _,request=service.read(delivery)
            require(request.payload['action']=='execute','delivery-not-execution')
            grant=self.journal.grant(link(request,'grant'),self.journal.store.load)
            if self.journal.store.head(key(grant.payload['run'])) is None:
                return service.finish_unstarted_execution(operation=operation,delivery=delivery,effects=self.effects)
            return service.finish_execution(operation=operation,delivery=delivery,run=grant.payload['run'],effects=self.effects)
