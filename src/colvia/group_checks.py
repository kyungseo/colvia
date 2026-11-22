"""Bounded checks on fresh retained unions, never on the original folder.

Commands run with the explicitly approved environment, read access to local
runtime inputs, writes confined to a private candidate, and loopback networking.
This is a check runner, not an agent or a general untrusted-code service.
"""
import hashlib, io, os, selectors, signal, stat, subprocess, time
from pathlib import Path
from uuid import uuid4
from .codec import require, RecordError
from .bodies import body_bytes, ingest_body
from .records import record, link
from .platforms.posix import open_directory
from .platforms.selected import parent, selected
from . import group_records as gr


def _directory(authority):
    try:
        root=open_directory(authority)
        try:
            try: os.mkdir('group-checks',0o700,dir_fd=root)
            except FileExistsError: pass
            fd=os.open('group-checks',os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW,dir_fd=root)
            try:
                info=os.fstat(fd)
                require(info.st_uid==os.getuid() and info.st_mode&0o077==0,'group-check-directory-unsafe')
                name=uuid4().hex; os.mkdir(name,0o700,dir_fd=fd); os.fsync(fd)
            finally: os.close(fd)
        finally: os.close(root)
        return authority/'group-checks'/name
    except OSError: raise RecordError('group-check-environment-unavailable') from None


def _original(root,entry):
    try:
        with parent(root,entry['path'],verify_path=True) as (directory,name):
            require(directory is not None,'group-baseline-file-missing')
            fd=os.open(name,os.O_RDONLY|os.O_NOFOLLOW|os.O_NONBLOCK,dir_fd=directory)
            try:
                info=os.fstat(fd); require(stat.S_ISREG(info.st_mode),'group-baseline-file-not-regular')
                while raw:=os.read(fd,1024*1024): yield raw
            finally: os.close(fd)
    except OSError: raise RecordError('group-baseline-content-changed') from None


def materialize(service,parts,root):
    try:
        _,_,_,_,before,after,_,bodies,_=parts
        baseline={e['path']:e for e in before}
        # Opaque entries are excluded, not followed or silently converted to files.
        for entry in after:
            if entry['kind']!='regular': continue
            path=root/entry['path']; path.parent.mkdir(parents=True,exist_ok=True)
            chunks=body_bytes(bodies[entry['path']],service.store.load) if entry['path'] in bodies else _original(service.destination.root,baseline[entry['path']])
            size=0; digest=hashlib.sha256()
            fd=os.open(path,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600)
            try:
                for raw in chunks:
                    size+=len(raw); require(size<=entry['size'],'group-baseline-content-changed'); digest.update(raw)
                    data=memoryview(raw)
                    while data:
                        n=os.write(fd,data); require(n>0,'group-candidate-short-write'); data=data[n:]
                require(size==entry['size'] and digest.hexdigest()==entry['sha256'],'group-baseline-content-changed')
                os.fchmod(fd,0o755 if entry['mode']=='100755' else 0o644); os.fsync(fd)
            finally: os.close(fd)
    except OSError: raise RecordError('group-check-environment-unavailable') from None


def unchanged(parts,root):
    before,after=parts[4:6]
    regular=[e for e in after if e['kind']=='regular']
    paths={e['path'] for e in before+after}
    try:
        observed=selected(root,paths,byte_limit=sum(e['size'] for e in regular)+1,verify_path=True)
        return list(observed)==sorted(regular,key=lambda e:e['path'])
    except (OSError,RecordError): return False


def _kill(process):
    try: os.killpg(process.pid,signal.SIGKILL)
    except ProcessLookupError: pass
    process.wait()


def execute_check(definition,root):
    # The profile is passed as text, not as a mutable file inside the child root.
    profile='''(version 1)
(allow default)
(deny file-write* (require-all (require-not (subpath (param "CANDIDATE"))) (require-not (literal "/dev/null")) (require-not (literal "/dev/tty"))))
(deny network-outbound (require-not (remote ip "localhost:*")))
(deny network-inbound (require-not (local ip "localhost:*")))
(deny network-bind (require-not (local ip "localhost:*")))
'''
    cwd=root/definition['cwd']
    try: fd=open_directory(cwd)
    except OSError: raise RecordError('group-check-environment-unavailable') from None
    else: os.close(fd)
    scratch=root/'.colvia-check-tmp'; require(not scratch.exists(),'group-check-reserved-path')
    try: scratch.mkdir(mode=0o700)
    except OSError: raise RecordError('group-check-environment-unavailable') from None
    env={**definition['env'],'TMPDIR':str(scratch)}
    argv=['/usr/bin/sandbox-exec','-D','CANDIDATE='+str(root),'-p',profile,*definition['argv']]
    started=time.monotonic_ns(); outputs=[bytearray(),bytearray()]; process=None; outcome='unavailable'; code=None
    try:
        process=subprocess.Popen(argv,cwd=cwd,env=env,stdin=subprocess.DEVNULL,stdout=subprocess.PIPE,stderr=subprocess.PIPE,start_new_session=True)
        deadline=time.monotonic()+definition['timeout_seconds']
        with selectors.DefaultSelector() as selector:
            for i,stream in enumerate((process.stdout,process.stderr)):
                os.set_blocking(stream.fileno(),False); selector.register(stream,selectors.EVENT_READ,i)
            while selector.get_map():
                remaining=deadline-time.monotonic()
                if remaining<=0: outcome='timeout'; break
                for event,_ in selector.select(min(remaining,0.1)):
                    raw=os.read(event.fileobj.fileno(),65536)
                    if not raw: selector.unregister(event.fileobj); continue
                    available=definition['output_bytes']-sum(map(len,outputs))
                    outputs[event.data].extend(raw[:available])
                    if len(raw)>available: outcome='output-limit'; break
                if outcome=='output-limit': break
            else:
                try: result=process.wait(timeout=max(0.001,deadline-time.monotonic()))
                except subprocess.TimeoutExpired: outcome='timeout'
                else:
                    if result>=0: outcome='exited'; code=result
                    else: outcome='interrupted'
    except (OSError,RecordError): outcome='unavailable'
    except BaseException:
        if process is not None: _kill(process)
        raise
    finally:
        if process is not None:
            # Also remove descendants that inherited pipes or detached a server.
            _kill(process)
            process.stdout.close(); process.stderr.close()
    return dict(outcome=outcome,exit_code=code,elapsed_ns=time.monotonic_ns()-started),bytes(outputs[0]),bytes(outputs[1])


def run_checks(service,candidate,parts,operation):
    objects=[]; evidence=[]
    # The native lock excludes other original-folder effects while copying the baseline.
    with service._port().exclusion():
        for definition in parts[2].payload['checks']:
            root=_directory(service.authority)
            materialize(service,parts,root)
            require(unchanged(parts,root),'group-candidate-content-changed')
            outcome,stdout,stderr=execute_check(definition,root)
            same=unchanged(parts,root)
            logs=[]
            for raw in (stdout,stderr):
                pair=ingest_body(io.BytesIO(raw),service.store,operation); objects.append(pair); logs.append(pair[0])
            pair=record('group.evidence',dict(name=definition['name'],definition=gr.digest(definition),**outcome,
                tree_unchanged=same,environment_inputs='system runtime and approved environment; ignored and opaque files excluded'),
                dict(candidate=('decision',candidate.ref),stdout=('integrity',logs[0]),stderr=('integrity',logs[1])))
            objects.append(pair); evidence.append((definition['name'],pair[0]))
    return evidence,objects
