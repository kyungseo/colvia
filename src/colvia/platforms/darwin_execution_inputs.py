"""Qualified native inputs for the bounded document host; no launch or write.

Resource paths are supplied by the verified platform adapter, not by model
arguments. Approval of retained bytes never makes a changed live file current.
"""
import hashlib,os,stat
from pathlib import Path
from ..codec import require
from ..records import link,head_summary
from ..maps import read_map
from ..bodies import body_bytes
from ..execution.documents import prepare_views,compose_output
from .posix import open_directory

RESOURCE_LIMIT=512*1024*1024

def _resource(path,limit,retain):
    path=Path(path);directory=open_directory(path.parent)
    try:
        fd=os.open(path.name,os.O_RDONLY|os.O_NOFOLLOW|os.O_NONBLOCK,dir_fd=directory)
        try:
            before=os.fstat(fd)
            require(stat.S_ISREG(before.st_mode) and before.st_nlink==1 and before.st_size<=limit,'execution-resource-kind-size')
            signature=lambda s:(s.st_dev,s.st_ino,s.st_mode,s.st_nlink,s.st_size,s.st_mtime_ns,s.st_ctime_ns)
            digest=hashlib.sha256();size=0;parts=[]
            while raw:=os.read(fd,min(1024*1024,limit+1-size)):
                size+=len(raw);require(size<=limit,'execution-resource-kind-size');digest.update(raw)
                if retain:parts.append(raw)
            require(size==before.st_size and signature(before)==signature(os.fstat(fd))==
                signature(os.stat(path.name,dir_fd=directory,follow_symlinks=False)),'execution-resource-drift')
            return digest.hexdigest(),b''.join(parts)
        finally:os.close(fd)
    finally:os.close(directory)

def resource_digest(path):return _resource(path,RESOURCE_LIMIT,False)[0]

def resource_bytes(path,expected,*,limit=1048576):
    require(type(limit) is int and 0<limit<=1048576,'execution-resource-read-limit')
    digest,raw=_resource(path,limit,True)
    require(digest==expected,'execution-resource-drift')
    return raw

class DarwinExecutionInputs:
    def __init__(self,journal,observer,resources,recovery=None):
        self.journal=journal;self.observer=observer
        self.resources={name:Path(path) for name,path in resources.items()}
        self.recovery=recovery
    def assert_held(self,grant,owner):self.observer.assert_held(grant,owner)
    def project_and_resources(self,grant):
        service=self.journal.service;contract=grant.payload['contract'];scope=contract['scope']
        require(set(self.resources)==set(scope['resources']),'execution-resource-set')
        for name,path in self.resources.items():
            require(resource_digest(path)==scope['resources'][name],'execution-resource-drift')
        _,plan,_,_=head_summary(link(grant,'head'),self.journal.store.load)
        _,entries,current=service._observe_from_plan(plan)
        output=scope['output_id'];relative=str(Path(scope['documents'][output]['path']).relative_to(Path(contract['target'])))
        require([e for e in entries if e['path']!=relative]==
            [e for e in current.snapshot.entries if e['path']!=relative],'outside-output-project-drift')
        return plan,current
    def preflight(self,grant,history):
        plan,current=self.project_and_resources(grant);scope=grant.payload['contract']['scope'];output=scope['output_id']
        expected={name:item['original_identity'] for name,item in scope['documents'].items()}
        for worker in history.workers.values():
            if worker['intent']['value']['role']=='write':
                require(worker['result'] is not None and worker['close'] is not None and
                    worker['result']['value']['effect']=='applied' and worker['close']['value']['returncode']==0,
                    'execution-write-unresolved')
                expected[output]=worker['result']['value']['after']
        for name,item in scope['documents'].items():
            require(self.observer.document(item['path'])==expected[name],'execution-document-drift')
        # Recheck the full observation after named/resource reads. Later writes
        # still need their own immediately-before syscall identity comparison.
        self.journal.service._recheck_observation(current,frozenset(plan.payload['scope']))
    def startup(self,grant,history,deadline):
        require(history.runtime_intent is None,'execution-runtime-already-reserved')
        self.preflight(grant,history)
        prepare_views(grant.payload['contract'],self.retained(grant),grant.payload['request']['prompt'],deadline=deadline)

    def retained(self,grant):
        refs=read_map(link(grant,'bodies'),self.journal.store.load)
        return {name:b''.join(body_bytes(ref,self.journal.store.load)) for name,ref in refs.items()}
    def callback_preflight(self,grant,history,tool,args,deadline):
        contract=grant.payload['contract'];raw=self.retained(grant)
        if tool=='document_read':
            prepare_views(contract,raw,grant.payload['request']['prompt'],deadline=deadline)
        elif tool=='document_write':
            compose_output(contract,raw[contract['scope']['output_id']],args['content'],deadline=deadline)
    def save_original(self,grant,history):
        require(self.recovery is not None,'recovery_unavailable')
        return self.recovery.save_original(grant,history)
