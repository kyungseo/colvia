"""Retain the original native index, then publish into its vacant name.

The matching Git port must hold the exact index.lock and the authority barrier
throughout. Native no-replace moves avoid ReplaceFileW's partial replacement
states and ACL-merging behavior. An interrupted evacuated index is recoverable
only from the exact retained original, prepared bytes and still-owned lock.
This component alone does not authorize ref updates or integration completion.
"""
from pathlib import Path
import hashlib
from ..codec import require
from ..git_index import LIMIT
from ..storage.windows import WindowsFiles
from .windows_observation import Observer
from .windows_rename import ExactMove,RenameAPI

def matches_published(actual,expected,inherited_creation=None):
    if actual==expected:return True
    if actual is None or expected is None or type(inherited_creation) is not int:return False
    a,e=actual['identity'],expected['identity']
    return (a[:2]==e[:2] and a[2]==inherited_creation and
            actual['size']==expected['size'] and actual['sha256']==expected['sha256'])


class WindowsIndex:
    def __init__(self,gitdir,area,*,files=None,observer=None,mover=None):
        self.gitdir=Path(gitdir);self.area=Path(area)
        self.files=files or WindowsFiles(api=RenameAPI());self.api=self.files.api
        self.observer=observer or Observer(files=self.files);self.mover=mover or ExactMove(api=self.api,files=self.files)
        self.files.private_directory(self.area)
        self.roots=[self.directory(p) for p in (self.gitdir,self.area)]
        require(self.roots[0][0]==self.roots[1][0],'git-index-staging-volume-mismatch')
    def directory(self,path):
        with self.observer.opened(path) as (_,info):
            require(info['directory'],'git-index-directory-required');return list(info['identity'])
    def verify_roots(self):
        require([self.directory(p) for p in (self.gitdir,self.area)]==self.roots,'git-index-directory-changed')
        self.files.private_directory(self.area)
    def observe(self,path):
        try:
            with self.observer.opened(path,read=True) as (handle,info):
                require(not info['directory'] and not info.get('symlink') and info['links']==1 and info['size']<=LIMIT,'git-unsafe-index-file')
                digest=hashlib.sha256();count=0
                with self.files._stream_handle(handle) as stream:
                    while raw:=stream.read(1024*1024):
                        count+=len(raw);require(count<=LIMIT,'git-index-size-limit');digest.update(raw)
                require(count==info['size'] and self.api.state(handle,path)==info,'git-index-file-changed')
                return dict(identity=list(info['identity']),size=count,sha256=digest.hexdigest())
        except FileNotFoundError:return None
    def prepare(self,expected,raw):
        self.verify_roots();require(type(raw) is bytes and len(raw)<=LIMIT,'git-index-size-limit')
        require(self.observe(self.gitdir/'index')==expected,'git-index-preimage-changed')
        require(self.observe(self.area/'index-original') is None,'git-index-original-exists')
        self.files.create(self.area/'index-prepared',raw)
        after=self.observe(self.area/'index-prepared')
        require(after['sha256']==hashlib.sha256(raw).hexdigest() and after['size']==len(raw),'git-index-staging-changed')
        return dict(before=expected,after=after)
    def state(self,manifest):
        self.verify_roots()
        require(type(manifest) is dict and set(manifest)=={'before','after'},'git-index-manifest-invalid')
        current=self.observe(self.gitdir/'index');saved=self.observe(self.area/'index-original');staged=self.observe(self.area/'index-prepared')
        before,after=manifest['before'],manifest['after']
        require(after is not None,'git-index-manifest-invalid')
        if current==before and saved is None and staged==after:return 'old'
        if before is not None and current is None and saved==before and staged==after:return 'evacuated'
        if saved==before and staged is None and matches_published(current,after,
                before['identity'][2] if before is not None else None):return 'new'
        return 'other'
    def publish(self,manifest,*,assert_owned,live,event=lambda _:None):
        assert_owned();live();state=self.state(manifest)
        require(state in ('old','evacuated','new'),'git-index-external-divergence')
        def guard():assert_owned();live();self.verify_roots()
        if state=='old' and manifest['before'] is not None:
            self.mover.move(self.gitdir/'index',self.area/'index-original',expected=manifest['before'],before_effect=guard,event=event)
            require(self.state(manifest)=='evacuated','git-index-external-divergence')
        if state!='new':
            guard();require(self.state(manifest) in ('old','evacuated'),'git-index-external-divergence')
            self.mover.move(self.area/'index-prepared',self.gitdir/'index',expected=manifest['after'],before_effect=guard,event=event,
                inherited_creation=manifest['before']['identity'][2] if manifest['before'] is not None else None)
        require(self.state(manifest)=='new','git-index-publication-unconfirmed')
        self.files.sync_directory(self.gitdir);self.files.sync_directory(self.area)
        require(self.state(manifest)=='new','git-index-publication-unconfirmed')
        # The caller still owns index.lock. Closing that gate and the authority
        # transaction are separate recorded steps; never hide them here.
        return 'new'
