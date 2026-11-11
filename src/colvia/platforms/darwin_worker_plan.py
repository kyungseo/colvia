"""Prepare exact per-worker native files; never execute an unqualified fallback.

The concrete release adapter supplies the verified dedicated Python root and
resource files. Preparation is not installed-runtime or sandbox qualification.
"""
import copy,os
from dataclasses import dataclass
from pathlib import Path
from ..codec import require
from ..execution.guards import wire_bytes
from .posix import open_directory
from .darwin_execution_inputs import resource_bytes
from .darwin_execution_recovery import publish_private,read_private


def literal(path):
    import json
    value=str(path)
    require(Path(value).is_absolute() and not any(c in value for c in ('\x00','\n','\r')),'execution-profile-path')
    return '(literal '+json.dumps(value,ensure_ascii=False)+')'

def parents(paths):
    values={}
    for path in paths:
        for parent in Path(path).parents:
            if str(parent) in values:continue
            fd=open_directory(parent)
            try:info=os.fstat(fd);values[str(parent)]=[info.st_dev,info.st_ino]
            finally:os.close(fd)
    return values

@dataclass(frozen=True)
class WorkerPlan:
    argv: tuple
    cwd: str
    env: dict
    name: str
    native: dict
    spec: dict
    spec_bytes: bytes
    profile_bytes: bytes

class DarwinWorkerPlan:
    def __init__(self,inputs,python_root):
        self.inputs=inputs;self.effects=inputs.observer.effects;self.python_root=Path(python_root)
        python=inputs.resources['python_digest']
        require(python.is_relative_to(self.python_root) and python!=self.python_root and len(self.python_root.parts)>=3,
            'execution-python-root')
        for root in (self.effects.root,self.effects.authority):
            require(not root.is_relative_to(self.python_root) and not self.python_root.is_relative_to(root),'execution-python-project-overlap')
        fd=open_directory(self.python_root);os.close(fd)
    def files(self,grant,history):
        scope=grant.payload['contract']['scope'];output=scope['output_id'];result={}
        for name,item in scope['documents'].items():
            observed=item['original_identity'];view=copy.deepcopy(item['view'])
            if name==output:
                for worker in history.workers.values():
                    if worker['intent']['value']['role']=='write':
                        require(worker['result'] is not None and worker['close'] is not None and
                            worker['result']['value']['effect']=='applied' and worker['close']['value']['returncode']==0,'execution-write-unresolved')
                        observed=worker['result']['value']['after']
                        view['ranges'][0][1]+=observed['size']-item['original_identity']['size']
            result[name]=dict(path=item['path'],identity=[observed['dev'],observed['ino']],mode=observed['mode'],
                sha256=observed['sha256'],view=view)
        return result
    def materialize(self,grant,history,tool,args,ordinal):
        require(self.effects.locked,'effect-lock-required')
        require(history.pending is not None and ordinal==len(history.workers)+1,'execution-worker-plan-order')
        resources=self.inputs.resources;scope=grant.payload['contract']['scope'];request=grant.payload['request']
        name='execution-worker-'+grant.ref.sha256+'-'+str(ordinal)
        with self.effects._stage(name,create=True) as (directory,native):
            slot=self.effects.authority/'effects'/name
            swap={scope['output_id']:str(slot/'output.post')} if tool=='document_write' else {}
            files=self.files(grant,history);read_paths=[item['path'] for item in files.values()]
            metadata_paths=list(request['link_metadata'])
            spec=dict(version=1,files=files,parents=parents([*read_paths,*swap.values(),*metadata_paths]),
                outputs=[scope['output_id']],swap=swap,parser=str(resources['parser_digest']),
                parser_sha256=scope['resources']['parser_digest'],claims=request['claims'],
                approved_external_links=request['approved_external_links'],link_metadata=request['link_metadata'])
            encoded=wire_bytes(spec);require(len(encoded)<=1048576,'execution-worker-spec-size')
            publish_private(directory,'spec.json',encoded)
            template=resource_bytes(resources['profile_digest'],scope['resources']['profile_digest']).decode('utf-8')
            markers=('; @@ANCESTOR_METADATA_LITERALS@@','; @@APPROVED_INPUT_READ_LITERALS@@',
                '; @@EXACT_WRITE_TARGET_AND_SWAP@@ only for write operation, omitted for read and all verifiers.')
            require(all(template.count(marker)==1 for marker in markers),'execution-profile-marker')
            extra=[path for path,item in request['link_metadata'].items() if item['sha256'] is not None]
            original=[value+'.original' for value in swap.values()]
            ancestors=set(parents([*read_paths,*extra,*resources.values(),slot/'spec.json',*swap.values(),*original]))|set(metadata_paths)|{str(slot)}
            rules=['(allow file-read-metadata '+' '.join(literal(path) for path in sorted(ancestors)) +')',
                '(allow file-read* '+' '.join(literal(path) for path in read_paths+extra)+')','']
            if swap:
                output=files[scope['output_id']]['path'];post=swap[scope['output_id']]
                require(os.stat(Path(output).parent).st_dev==os.fstat(directory).st_dev,'effect-staging-volume-mismatch')
                writable=[output,post,*original]
                rules[2]='(allow file-read* file-write* '+' '.join(literal(path) for path in writable)+')\n'+                    '(allow file-read-data file-write-data '+' '.join(literal(path) for path in sorted({str(Path(output).parent),str(slot)}))+')'
            for marker,rule in zip(markers,rules):template=template.replace(marker,rule)
            profile=template.encode();require(len(profile)<=1048576,'execution-worker-profile-size')
            publish_private(directory,'worker.sb',profile)
            parameters=dict(BIN=str(resources['python_digest']),SPEC=str(slot/'spec.json'),PARSER=str(resources['parser_digest']),
                WORKER=str(resources['worker_digest']),PYROOT=str(self.python_root))
            argv=['/usr/bin/sandbox-exec']
            for key,value in parameters.items():argv.extend(('-D',key+'='+value))
            operation={'document_read':'read','document_write':'write'}.get(tool,args.get('verifier_id'))
            require(operation in ('read','write','DOC-LINKS','DOC-GFM','DOC-CLAIMS'),'execution-worker-operation')
            argv.extend(('-f',str(slot/'worker.sb'),str(resources['python_digest']),'-I','-S','-B',str(resources['worker_digest']),
                '--spec',str(slot/'spec.json'),'--operation',operation))
            return WorkerPlan(tuple(argv),str(slot),dict(HOME=str(slot),TMPDIR=str(slot),PATH='/usr/bin:/bin',LANG='C.UTF-8'),
                name,native,spec,encoded,profile)
    def verify(self,plan):
        require(self.effects.locked,'effect-lock-required')
        with self.effects._stage(plan.name,expected=plan.native) as (directory,_):
            require(read_private(directory,'spec.json',1048576)==plan.spec_bytes and
                read_private(directory,'worker.sb',1048576)==plan.profile_bytes,'execution-worker-plan-drift')
