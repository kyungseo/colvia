"""Windows Git composition over owned Jobs and retained index transitions.

Only local, same-volume staging is admitted. OS permissions, hooks, filters and
native qualification are not waived. Injectable ports are used by explicit
cross-platform protocol tests; they are not CLI or project configuration options.
"""
from dataclasses import asdict
from pathlib import Path
import os,uuid
from ..codec import canonical_bytes,require
from ..git_index import LIMIT
from ..storage.windows import WindowsFiles
from .git_candidate import GitCandidate,absent,digest
from .observation_port import location
from .windows_child import WindowsGitChild
from .windows_rename import ExactMove,RenameAPI
from .windows_observation import Observer
from .windows_git_index import WindowsIndex
from .windows_process_identity import process_birth


class WindowsGit(GitCandidate):
    def __init__(self,root,scratch,git,*,create=True,files=None,observer=None,mover=None,children=None,birth=process_birth):
        self.root=Path(root);self.scratch=Path(scratch);self.git=git;self.locked=False
        self.files=files or WindowsFiles(api=RenameAPI());self.api=self.files.api
        self.observer=observer or Observer(files=self.files);self.mover=mover or ExactMove(api=self.api,files=self.files);self.birth=birth
        self.files.private_directory(self.scratch);self.root_identity=asdict(location(self.root))
        for name in ('children','hooks'):
            path=self.scratch/name
            if absent(path):require(create,'git-staging-unavailable');self.files.create_directory(path)
            self.files.private_directory(path)
        require(not any((self.scratch/'hooks').iterdir()),'git-hooks-staging-not-empty')
        self.children=children or WindowsGitChild(self.scratch/'children',files=self.files)
        self.env={**git.env,'GIT_NO_REPLACE_OBJECTS':'1','GIT_NO_LAZY_FETCH':'1'}
    def command(self,*args,**kwargs):
        from .windows_git_objects import environment_digest
        environment_digest(self.env)
        return super().command(*args,**kwargs)
    def verify_objects(self,m):
        from .windows_git_objects import verify
        verify(self,m)
    def file_id(self,path):
        with self.observer.opened(path) as (_,info):
            require(not info['directory'] and not info.get('symlink') and info['links']==1,'git-unsafe-effect-file')
            return dict(scheme='windows-file-id-v1',value=':'.join(str(v) for v in info['identity']))
    @staticmethod
    def index_mode(path):return 0o600 # Logical private gate mode, never POSIX permission emulation.
    @staticmethod
    def require_inactive_hook(path):
        require(False,'git-hooks-require-manual-integration') # Non-sample Windows hooks do not require a POSIX x bit.
    def index_port(self,m):
        port=WindowsIndex(Path(m['context']['topology']['gitdir']['path']),self.scratch/m['operation'],
            files=self.files,observer=self.observer,mover=self.mover)
        if 'native_index' in m['context']:
            require(port.roots==m['context']['native_index']['roots'],'git-index-directory-changed')
        return port
    def prepare(self,*args,**kwargs):
        m=super().prepare(*args,**kwargs);original=canonical_bytes(m);port=self.index_port(m)
        before=port.observe(port.gitdir/'index')
        require((before is None and m['context']['index'] is None) or
                (before is not None and before['sha256']==m['context']['index'] and self.file_id(port.gitdir/'index')==m['context']['index_native']),
                'git-index-preimage-changed')
        prepared=port.prepare(before,self.files.read(self.scratch/m['operation']/'i1',LIMIT))
        m['context']['native_index']=dict(roots=port.roots,manifest=prepared)
        from .windows_git_objects import prepare
        m['context']['native_objects']=prepare(self,m)
        self.files.replace(self.scratch/m['operation']/'manifest',canonical_bytes(m),original)
        return m
    def check(self,m,*,index='old',ref='old'):
        require(index=='old' and ref=='old','windows-git-admission-phase')
        self.verify_manifest(m);now,_,_=self.snapshot(m['paths']);expected=dict(m['context']);expected.pop('native_index');expected.pop('native_objects')
        require(now==expected and self.index_port(m).state(m['context']['native_index']['manifest'])=='old','git-integration-context-changed')
    def owner(self,path):
        birth=self.birth(os.getpid());require(birth is not None,'git-lock-owner-unavailable')
        return dict(native=self.file_id(path),pid=os.getpid(),birth=birth)
    def create_index_gate(self,m,*,attempt,live):
        from .windows_git_gate import create
        return create(self,m,attempt=attempt,live=live)
    def acquire_index(self,m,*,attempt,live):
        self.verify_manifest(m);require(all(absent(p) for p in self.locks(m)),'git-child-lock-present')
        return self.create_index_gate(m,attempt=attempt,live=live)
    def reconcile_owner(self,m,owner,*,attempt,live):
        from .windows_git_gate import reconcile
        return reconcile(self,m,owner,attempt=attempt,live=live)
    def owned_lock(self,m,owner):
        path=self.lock_path(m)
        require(owner is not None and not absent(path) and self.file_id(path)==owner['native'] and
                self.observer.read_file(path,LIMIT)==b'','git-index-lock-not-owned')
        return path
    def inspect_outcome(self,m):
        self.verify_manifest(m,objects=False);self.placement(m)
        actual=self.ref(m['context']['branch'],m['context']['algorithm'])
        ref='old' if actual==m['context']['ref'] else 'new' if actual==m['new'] else 'other'
        return ref,self.index_port(m).state(m['context']['native_index']['manifest'])
    def replace_index(self,m,owner,*,live):
        require(self.inspect_outcome(m) in (('new','old'),('new','evacuated')),'git-index-preimage-changed')
        def gate():
            self.owned_lock(m,owner);require(all(absent(p) for p in self.locks(m)),'git-child-lock-present')
            require(self.ref(m['context']['branch'],m['context']['algorithm'])==m['new'],'git-ref-update-unconfirmed')
        self.index_port(m).publish(m['context']['native_index']['manifest'],assert_owned=gate,live=live)
    def retain_lock(self,m,owner,name,*,live):
        path=self.owned_lock(m,owner);port=self.index_port(m);expected=port.observe(path)
        # ExactMove validates the held source handle. Reopening it here would
        # conflict with DELETE access under Windows sharing rules.
        def guard():require(all(absent(p) for p in self.locks(m)),'git-child-lock-present');live()
        self.mover.move(path,self.scratch/m['operation']/name,expected=expected,before_effect=guard,event=lambda _:None)
        self.files.sync_directory(path.parent);self.files.sync_directory(self.scratch/m['operation'])
        require(absent(path),'git-index-lock-not-owned')
    def finalize_index(self,m,owner,*,live):
        require(self.inspect_outcome(m)==('new','new'),'git-integration-postcondition-unconfirmed')
        if absent(self.lock_path(m)):
            # Completion after the exact gate move may have lost its DB ack.
            saved=self.scratch/m['operation']/'index-lock-completed'
            require(owner is not None and self.file_id(saved)==owner['native'],'git-index-lock-not-owned');return
        self.retain_lock(m,owner,'index-lock-completed',live=live)
    def require_owner_closed(self,owner):
        current=self.birth(owner['pid'])
        require(owner['pid']==os.getpid() and current==owner['birth'] or current!=owner['birth'],'git-lock-owner-still-live')
    def release_owned(self,m,owner):
        self.require_owner_closed(owner);self.retain_lock(m,owner,'index-lock-not-applied',live=lambda:None)
    def recovery_ready(self,m,owner,child):
        # Old or incomplete durability evidence never authorizes recovery effects.
        self.verify_objects(m)
        require(all(absent(p) for p in self.locks(m)),'git-child-lock-present')
        if child is not None:require(self.children.closed(self.scratch/'children'/child),'git-child-closure-unavailable')
        if owner is not None:self.require_owner_closed(owner)
    def recover_index(self,m,owner,*,live,attempt):
        require(self.inspect_outcome(m) in (('new','old'),('new','evacuated')),'git-index-preimage-changed');live()
        path=self.lock_path(m)
        if absent(path):return self.create_index_gate(m,live=live,attempt=attempt)
        self.owned_lock(m,owner)
        return self.owner(path)
    def flush_native(self,path):
        # Fail closed on a sharing/read-only/durability refusal. The actual
        # Windows Git attribute behavior still requires native qualification.
        with self.api.ancestors(path),self.api.opened(path,access=0xc0000080,share=1) as handle:
            before=self.api.state(handle,path);require(not before['directory'] and before['links']==1,'git-durability-file-unavailable')
            self.api.ok(self.api.FlushFileBuffers(handle))
            require(self.api.state(handle,path)==before,'git-durability-file-changed')
        self.files.sync_directory(Path(path).parent)
