"""Native document backend combining checked inputs, plans and observed results.

No model runtime or Work acceptance is implemented here. Each operation is
still admitted and journaled by the host, and process closure is separate.
"""
import os
from ..codec import require
from ..execution import results
from .darwin_execution import file_observation
from .darwin_execution_inputs import DarwinExecutionInputs
from .darwin_execution_recovery import DarwinExecutionRecovery
from .darwin_worker_plan import DarwinWorkerPlan

class DarwinDocumentBackend(DarwinExecutionInputs):
    def __init__(self,journal,observer,resources,python_root):
        super().__init__(journal,observer,resources,DarwinExecutionRecovery(journal,observer))
        observer.recovery_port=self.recovery
        self.planner=DarwinWorkerPlan(self,python_root)
    def materialize(self,grant,history,tool,args,ordinal):return self.planner.materialize(grant,history,tool,args,ordinal)
    def verify_plan(self,plan):self.planner.verify(plan)
    def validate_result(self,grant,tool,args,value,plan,deadline):
        require(self.observer.effects.locked,'effect-lock-required');self.planner.verify(plan)
        scope=grant.payload['contract']['scope'];contract=grant.payload['contract'];request=grant.payload['request']
        work_plan,observed=self.project_and_resources(grant)
        raw={};identities={}
        for name,item in scope['documents'].items():
            identities[name],raw[name]=self.observer.document_bytes(item['path'])
            if tool!='document_write' or name!=scope['output_id']:
                expected=plan.spec['files'][name]
                current=identities[name]
                require(current is not None and current['sha256']==expected['sha256'] and current['mode']==expected['mode'] and
                    [current['dev'],current['ino']]==expected['identity'],'execution-document-drift')
        after=body=None
        if tool=='document_write':
            output=scope['output_id'];swap=plan.spec['swap'][output]
            with self.observer.effects._stage(plan.name,expected=plan.native) as (stage,_):
                saved,saved_raw=file_observation(stage,'output.post.original')
                try:os.stat('output.post',dir_fd=stage,follow_symlinks=False);present=True
                except FileNotFoundError:present=False
                reply,_=results.write_result(contract,self.retained(grant)[output],args['content'],value,
                    after=identities[output],raw=raw[output],saved=saved,saved_raw=saved_raw,swap_present=present,deadline=deadline)
                after=identities[output];body=raw[output]
        elif tool=='document_read':reply=results.read_result(contract,request,raw,value,deadline=deadline)
        else:reply=results.verifier_result(contract,request,plan.spec['files'],args['verifier_id'],value,deadline=deadline)
        self.journal.service._recheck_observation(observed,frozenset(work_plan.payload['scope']))
        return reply,after,body
