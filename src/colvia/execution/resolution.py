"""Exact human resolution, using a qualified local observer under effect lock.

The observer is an internal platform port, never a request-supplied boolean or
plugin selected by model output. Resolving records uncertainty; it does not
restore document bytes, accept Work, or launch a previously interrupted run.
"""
from ..codec import canonical_bytes,require
from ..records import record,text
from ..effects import PENDING
from . import schema

class Resolution:
    def __init__(self,journal,observer):self.journal=journal;self.observer=observer
    def observation(self,run):
        state,grant,h,owner,history=self.journal.read(run)
        require(history.terminal not in schema.CLOSED,'execution-resolution-requires-unresolved')
        require(self.journal.store.head(PENDING)==owner.ref,'execution-owner-changed')
        history.identified_processes()
        self.observer.assert_held(grant,owner)
        processes=[]
        if history.runtime_start is not None:processes.append(history.runtime_start['value'])
        processes.extend(w['start']['value'] for w in history.workers.values() if w['start'] is not None)
        for process in processes:
            require(self.observer.process_absent(process['pid'],process['birth'],group=True),'execution-process-present-or-unconfirmed')
        for child in history.children:
            require(self.observer.process_absent(child['pid'],child['birth'],group=False),'execution-child-present-or-unconfirmed')
        documents={name:self.observer.document(item['path']) for name,item in history.scope['documents'].items()}
        availability=self.observer.recovery(grant,history)
        value=dict(grant=history.grant['grant'],journal_head=history.rows[-1]['sha256'],previous_status=history.terminal or 'incomplete',
            documents=documents,process_absence=True,recovery_availability=availability,action='record-unknown-resolution')
        schema.event('operator-resolved-unknown',value)
        return state,grant,h,owner,value
    def receipt(self,run,state,value):
        import hashlib
        return hashlib.sha256(canonical_bytes(dict(project=self.journal.store.project,instance=self.journal.store.instance,
            run=run,state=state.ref.as_dict(),observation=value))).hexdigest()
    def preview(self,run):
        with self.observer.hold():
            state,_,_,_,value=self.observation(run)
            return dict(run=run,observation=value,receipt=self.receipt(run,state,value),accepted=False)
    def apply(self,*,operation,run,receipt,statement):
        text(statement)
        with self.observer.hold():
            state,grant,h,owner,value=self.observation(run)
            require(receipt==self.receipt(run,state,value),'execution-stale-resolution-receipt')
            decision=record('execution.resolution',dict(run=run,statement=statement,observation=value),
                {'grant':('decision',grant.ref),'history':('decision',h.ref)})
            def reobserve():return self.observation(run)[4]
            return self.journal._append(operation=operation,run=run,kind='operator-resolved-unknown',value=value,
                objects=[decision],resolution=decision[0],reobserve=reobserve)
