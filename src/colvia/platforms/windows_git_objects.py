"""Creation-time durability for immutable Windows Git objects.

A fresh, non-thin pack in the real object store covers the exact candidate walk,
including reused loose/packed objects. Git fsyncs its writable creation handles;
we never clear READONLY or reopen immutable objects for writing. The existing
integration manifest retains the receipt. Missing evidence refuses recovery.
"""
from contextlib import ExitStack
from pathlib import Path
import hashlib,os,re,shutil,uuid
from ..codec import canonical_bytes,decode_canonical,require,RecordError

MAX_BYTES=2*1024**3
FILE_LIMIT=MAX_BYTES+32*1024**2
ALLOWED_GIT={'GIT_OPTIONAL_LOCKS':'0','GIT_NO_LAZY_FETCH':'1','GIT_TERMINAL_PROMPT':'0',
             'GIT_PAGER':'cat','GIT_NO_REPLACE_OBJECTS':'1','GIT_CONFIG_NOSYSTEM':'1',
             'GIT_CONFIG_GLOBAL':os.devnull,'GIT_CONFIG_SYSTEM':os.devnull}

def sha(raw):return hashlib.sha256(raw).hexdigest()

def environment_digest(env):
    seen=set()
    for key,value in env.items():
        upper=key.upper()
        if upper.startswith('GIT_'):
            require(key==upper and upper not in seen and ALLOWED_GIT.get(upper)==value,
                    'git-object-durability-environment')
            seen.add(upper)
    require({'GIT_OPTIONAL_LOCKS','GIT_NO_LAZY_FETCH','GIT_TERMINAL_PROMPT','GIT_PAGER','GIT_NO_REPLACE_OBJECTS'}<=seen and env.get('LC_ALL')=='C', 'git-object-durability-environment')
    require(not (seen&{'GIT_CONFIG_NOSYSTEM','GIT_CONFIG_GLOBAL','GIT_CONFIG_SYSTEM'}) or {'GIT_CONFIG_NOSYSTEM','GIT_CONFIG_GLOBAL','GIT_CONFIG_SYSTEM'}<=seen,'git-object-durability-environment')
    return sha(canonical_bytes({k:v for k,v in env.items() if k.startswith('GIT_')}))

def inventory(port,m):
    raw,rows=port.object_inventory(m);items={};total=0
    for row in rows:
        oid,kind,size=row.split();oid=oid.decode('ascii');size=int(size)
        require(oid not in items,'git-object-walk-unavailable')
        total+=size;require(total<=MAX_BYTES,'git-object-durability-byte-limit')
        items[oid]=(kind.decode('ascii'),size)
    # Walk ordering is not authority. Use a stable exact set for the receipt.
    ordered=''.join(oid+'\n' for oid in sorted(items)).encode('ascii')
    return ordered,items,total

def pack_args(prefix):
    return ['-c','pack.writeReverseIndex=false','-c','pack.packSizeLimit=0',
            'pack-objects','-q','--index-version=2','--threads=1','--window=0','--depth=0',
            '--no-reuse-object','--no-reuse-delta','--non-empty','--no-thin',
            '--no-write-bitmap-index','--no-use-bitmap-index','--compression=0',str(prefix)]

def expected_args(port,prefix):
    return [str(port.git.executable),'--no-optional-locks','-c','core.fsmonitor=false',
            '-c','core.untrackedCache=false','-c','core.hooksPath='+str(port.scratch/'hooks'),
            '-c','gc.auto=0','-c','maintenance.auto=false','-c','core.fsync=all',
            '-c','core.fsyncMethod=fsync','-C',str(port.root),*pack_args(prefix)]


def held_file(port,path,stack,hash_size):
    try:handle,info=stack.enter_context(port.observer.opened(path,read=True))
    except FileNotFoundError:raise RecordError('git-object-durability-pack-gone') from None
    require(not info['directory'] and not info.get('symlink') and info['links']==1 and
            2*hash_size<=info['size']<=FILE_LIMIT,'git-object-durability-file-invalid')
    count=0;digest=hashlib.sha256()
    with port.files._stream_handle(handle) as stream:
        while raw:=stream.read(1024*1024):
            count+=len(raw);require(count<=FILE_LIMIT,'git-object-durability-byte-limit');digest.update(raw)
        stream.seek(-2*hash_size,2);tail=stream.read(2*hash_size)
    require(count==info['size'],'git-object-durability-file-changed')
    return dict(identity=list(info['identity']),size=count,sha256=digest.hexdigest()),tail

def verify_pack(port,index,items):
    out=port.command(['-c','pack.writeReverseIndex=false','verify-pack','-v',str(index)]).stdout
    found={};okay=False
    for line in out.splitlines():
        fields=line.split()
        if len(fields)==5 and re.fullmatch(rb'[0-9a-f]{40}|[0-9a-f]{64}',fields[0]):
            oid=fields[0].decode();require(oid not in found and all(v.isdigit() for v in fields[2:]),
                                       'git-object-durability-pack-invalid')
            found[oid]=(fields[1].decode('ascii'),int(fields[2]))
        elif re.fullmatch(rb'non delta: [0-9]+ objects?',line):pass
        elif line.endswith(b'.pack: ok'):
            require(not okay,'git-object-durability-pack-invalid');okay=True
        else:raise RecordError('git-object-durability-pack-invalid')
    require(okay and found==items,'git-object-durability-object-set-changed')

def directory(port,path):
    with port.api.opened(path,access=0x80,share=3) as handle:
        info=port.api.state(handle,path);require(info['directory'],'git-object-durability-directory-invalid')
        return list(info['identity'])

def prepare(port,m):
    require(port.locked,'git-integration-lock-required')
    raw,items,total=inventory(port,m);env=environment_digest(port.env)
    common=Path(m['context']['topology']['common']['path']);packdir=common/'objects/pack'
    require(packdir.is_dir(),'git-object-durability-directory-unavailable')
    require(shutil.disk_usage(packdir).free>=total+64*1024**2,'git-object-durability-space')
    name='pack-colvia-'+uuid.uuid4().hex;prefix=packdir/name;area=port.scratch/m['operation']
    require(not any(packdir.glob(name+'*')),'git-object-durability-prefix-exists')
    input_path=area/'durability-oids';port.files.create(input_path,raw)
    child=None
    def event(phase,value):
        nonlocal child
        if phase=='spawn-intent':child=Path(value).name
    with port.api.ancestors(packdir/'object-guard'):
        root=directory(port,packdir)
        def invocation(args,actual_env):
            require(args==expected_args(port,prefix),'git-object-durability-command-changed')
            require(environment_digest(actual_env)==env,'git-object-durability-environment')
        result=port.command(pack_args(prefix),input_path=input_path,event=event,invocation=invocation)
        lines=result.stdout.splitlines();require(len(lines)==1,'git-object-durability-output-invalid')
        h=lines[0].decode('ascii');length=hashlib.new(m['context']['algorithm']).digest_size
        require(re.fullmatch('[0-9a-f]{'+str(length*2)+'}',h) is not None and child is not None,
                'git-object-durability-output-invalid')
        names={name+'-'+h+'.pack',name+'-'+h+'.idx'}
        require({p.name for p in packdir.glob(name+'*')}==names,'git-object-durability-output-invalid')
        record={}
        with ExitStack() as stack:
            for ext in ('pack','idx'):
                path=packdir/(name+'-'+h+'.'+ext)
                record[ext],tail=held_file(port,path,stack,length)
                require((tail[-length:] if ext=='pack' else tail[:length]).hex()==h,
                        'git-object-durability-checksum-mismatch')
            verify_pack(port,packdir/(name+'-'+h+'.idx'),items)
            port.files.sync_directory(packdir);port.files.sync_directory(packdir.parent)
            require(directory(port,packdir)==root,'git-object-durability-directory-changed')
        intent=decode_canonical(port.files.read(port.scratch/'children'/child/'intent.json'))
        receipt=dict(version=1,prefix=name,hash=h,files=record,root=root,child=child,
                     command=sha(canonical_bytes(intent['args'])),environment=env,
                     objects=sha(raw),count=len(items),bytes=total,tool=port.git.identity,
                     candidate=m['new'],parent=m['context']['ref'])
        successful_child(port,receipt,prefix)
        return receipt

def successful_child(port,r,prefix):
    require(type(r['child']) is str and re.fullmatch('[0-9a-f]{32}',r['child']) is not None,
            'git-object-durability-receipt-invalid')
    area=port.scratch/'children'/r['child']
    try:
        intent=decode_canonical(port.files.read(area/'intent.json'))
        started=decode_canonical(port.files.read(area/'started.json'))
        final=decode_canonical(port.files.read(area/'closed.json'))
    except FileNotFoundError:raise RecordError('git-object-durability-child-unconfirmed') from None
    require(intent['args']==expected_args(port,prefix) and sha(canonical_bytes(intent['args']))==r['command'] and intent['cwd']==str(port.root) and
            final==dict(pid=started['pid'],exit_code=0,job_active=0) and
            not port.files.exists(area/'unknown.json') and not port.files.exists(area/'stopped.json') and not port.files.exists(area/'failure.json'),
            'git-object-durability-child-unconfirmed')
    require(port.files.read(area/'stdout',4096) in ((r['hash']+'\n').encode(),(r['hash']+'\r\n').encode()),
            'git-object-durability-child-unconfirmed')

def verify(port,m):
    require('native_objects' in m['context'],'git-object-durability-receipt-missing')
    r=m['context']['native_objects'];keys={'version','prefix','hash','files','root','child','command',
        'environment','objects','count','bytes','tool','candidate','parent'}
    require(type(r) is dict and set(r)==keys and r['version']==1 and
            type(r['prefix']) is str and re.fullmatch('pack-colvia-[0-9a-f]{32}',r['prefix']) is not None and
            type(r['hash']) is str and re.fullmatch('[0-9a-f]{40}|[0-9a-f]{64}',r['hash']) is not None and
            type(r['files']) is dict and set(r['files'])=={'pack','idx'},'git-object-durability-receipt-invalid')
    require(r['tool']==port.git.identity and r['environment']==environment_digest(port.env) and
            r['candidate']==m['new'] and r['parent']==m['context']['ref'],'git-object-durability-context-changed')
    raw,items,total=inventory(port,m)
    require(r['objects']==sha(raw) and r['count']==len(items) and r['bytes']==total,
            'git-object-durability-object-set-changed')
    packdir=Path(m['context']['topology']['common']['path'])/'objects/pack';length=hashlib.new(m['context']['algorithm']).digest_size
    successful_child(port,r,packdir/r['prefix'])
    require(len(r['hash'])==2*length,'git-object-durability-receipt-invalid')
    with port.api.ancestors(packdir/'object-guard'),ExitStack() as stack:
        require(directory(port,packdir)==r['root'],'git-object-durability-directory-changed')
        for ext in ('pack','idx'):
            actual,tail=held_file(port,packdir/(r['prefix']+'-'+r['hash']+'.'+ext),stack,length)
            require(actual==r['files'][ext] and (tail[-length:] if ext=='pack' else tail[:length]).hex()==r['hash'],
                    'git-object-durability-file-changed')
        verify_pack(port,packdir/(r['prefix']+'-'+r['hash']+'.idx'),items)
