"""Read-only execution observation under the existing local APFS effect lock.

This is the qualified observation vocabulary, not a runner or supervisor. It
cannot prove absence for unidentified spawns or hostile detached descendants.
No signal other than killpg(..., 0) is sent by this module.
"""
from contextlib import contextmanager
import hashlib,os,stat,sys
from pathlib import Path
from ..codec import RecordError,require
from ..records import link
from ..execution import schema
from .selected import parent
from .process import run


def process_birth(pid):
    schema.integer(pid,2,(1<<31)-1)
    require(sys.platform=='darwin','execution-native-observer-unavailable')
    result=run(['/bin/ps','-p',str(pid),'-o','lstart='],cwd='/',env={'LC_ALL':'C','TZ':'UTC0'},seconds=3,output_limit=512)
    try:observed=result.stdout.decode('ascii').strip()
    except UnicodeError:raise RecordError('execution-process-observation-unavailable') from None
    require(not result.stderr and ((result.code==0 and bool(observed)) or (result.code==1 and not observed)),'execution-process-observation-unavailable')
    if observed:schema.birth(observed)
    return observed


def group_absent(pid):
    schema.integer(pid,2,(1<<31)-1)
    try:os.killpg(pid,0);return False
    except ProcessLookupError:return True
    except PermissionError:return False


def file_observation(directory,name):
    try:info=os.stat(name,dir_fd=directory,follow_symlinks=False)
    except FileNotFoundError:return None,None
    require(stat.S_ISREG(info.st_mode) and info.st_nlink==1 and info.st_size<=131072,'execution-document-kind-size')
    fd=os.open(name,os.O_RDONLY|os.O_NOFOLLOW|os.O_NONBLOCK,dir_fd=directory)
    try:
        signature=lambda i:(i.st_dev,i.st_ino,i.st_mode,i.st_nlink,i.st_size,i.st_mtime_ns,i.st_ctime_ns)
        before=os.fstat(fd);require(signature(info)==signature(before),'execution-document-drift')
        with os.fdopen(os.dup(fd),'rb') as stream:raw=stream.read(131073)
        require(len(raw)==before.st_size and signature(before)==signature(os.fstat(fd))==
            signature(os.stat(name,dir_fd=directory,follow_symlinks=False)),'execution-document-drift')
        value=dict(dev=before.st_dev,ino=before.st_ino,mode=stat.S_IMODE(before.st_mode),nlink=before.st_nlink,
            size=before.st_size,mtime_ns=before.st_mtime_ns,ctime_ns=before.st_ctime_ns,sha256=hashlib.sha256(raw).hexdigest())
        schema.identity(value);return value,raw
    finally:os.close(fd)

class DarwinExecutionObservation:
    def __init__(self,journal,effects,recovery=None):
        require(sys.platform=='darwin','execution-native-observer-unavailable')
        self.journal=journal;self.effects=effects;self.recovery_port=recovery
    @contextmanager
    def hold(self):
        # A real runner prepares this lock before reservation. Inspection must
        # never manufacture a missing recovery/lock area as if it existed.
        with self.effects.exclusion(create=False):yield
    def assert_held(self,grant,owner):
        require(self.effects.locked,'effect-lock-required')
        contract=grant.payload['contract']
        require(contract['capability']['observation_format']=='posix-document-process-1','execution-observation-unavailable')
        registration=self.journal.obj(link(grant,'registration')).payload['root']
        require(str(self.effects.root)==registration['path']==contract['target'],'execution-observer-root-mismatch')
        with self.effects._root() as fd,self.effects._authority():
            info=os.fstat(fd)
            require(str(info.st_dev)==registration['volume'] and str(info.st_ino)==registration['file_id'],'execution-observer-root-changed')
    def process_absent(self,pid,birth,*,group):
        schema.birth(birth)
        # A present reused PID is ambiguous. Do not infer absence from its new
        # birth string, including the separately observed runtime child list.
        return not process_birth(pid) and (not group or group_absent(pid))
    def document(self,path):return self.document_bytes(path)[0]
    def document_bytes(self,path):
        require(self.effects.locked,'effect-lock-required');schema.path(path)
        path=Path(path);root=self.effects.root
        require(path.is_relative_to(root) and path!=root,'execution-document-outside-root')
        with parent(root,str(path.relative_to(root))) as (directory,name):
            if directory is None:return None,None
            return file_observation(directory,name)
    def recovery(self,grant,history):
        require(self.effects.locked,'effect-lock-required')
        if self.recovery_port is None:return 'not_checked'
        return self.recovery_port.inspect(grant,history)
