"""Retained-original file effects on local NTFS, with explicit recovery states.

Every native move is exact-handle/no-replace. Same-volume private staging is
required; cross-volume copy/delete and ACL/privilege changes are not fallbacks.
Protocol tests on another OS are not native Windows qualification.
"""
from contextlib import contextmanager,ExitStack
from pathlib import Path
import hashlib,os
from ..codec import RecordError,require
from ..storage.windows import WindowsFiles
from ..storage.sqlite import _token
from ..tree import logical_path
from .windows_observation import Observer
from .windows_rename import ExactMove,RenameAPI


NATIVE_ALIASES=frozenset(('colvia.exe','colvia-manage.exe'))


class WindowsEffects:
    def __init__(self,root,authority,*,files=None,observer=None,mover=None,native_entries=False):
        self.root=Path(root);self.authority=Path(authority);self.locked=False
        self.native_entries=native_entries
        self.files=files or WindowsFiles(api=RenameAPI());self.api=self.files.api
        self.observer=observer or Observer(files=self.files);self.mover=mover or ExactMove(api=self.api,files=self.files)
        self.files.private_directory(self.authority)
        self.root_identity=self.identity(self.root);self.authority_identity=self.identity(self.authority)
        require(self.root_identity[0]==self.authority_identity[0],'effect-staging-volume-mismatch')
        require(not self.root.is_relative_to(self.authority) and not self.authority.is_relative_to(self.root),'effect-staging-overlaps-workspace')
    def identity(self,path):
        with self.api.ancestors(path),self.api.opened(path) as h:
            info=self.api.state(h,path);require(info['directory'],'effect-directory-required')
            return list(info['identity'])
    def verify_roots(self):
        require(self.identity(self.root)==self.root_identity and self.identity(self.authority)==self.authority_identity,'effect-root-changed')
        self.files.private_directory(self.authority)
        if self.native_entries:self.files.private_directory(self.root)
    @contextmanager
    def exclusion(self,*,create=True):
        require(not self.locked,'effect-lock-reentry');self.verify_roots();lock=self.authority/'effect.lock'
        if not self.files.exists(lock):
            require(create,'effect-lock-missing');self.files.create(lock,b'')
        require(self.files.read(lock)==b'','effect-lock-invalid')
        with self.files.exclusion(lock):
            self.locked=True
            try:self.verify_roots();yield
            finally:self.locked=False
    def inspect(self,path,logical):
        try:
            with self.observer.opened(path,read=True) as (h,info):
                require(not info['directory'] and not info.get('symlink') and info['links']==1,'unsafe-effect-file')
                size=0;digest=hashlib.sha256()
                with self.files._stream_handle(h) as stream:
                    while raw:=stream.read(1024*1024):
                        size+=len(raw);require(size<=1024**3,'effect-body-limit');digest.update(raw)
                require(size==info['size'],'effect-file-changed')
                return dict(path=logical,kind='regular',mode='100644',size=size,sha256=digest.hexdigest()),list(info['identity'])
        except FileNotFoundError:
            # Only a missing leaf is absence. Missing/replaced ancestors are
            # diagnosed separately by destination() and stage().
            require(not os.path.lexists(path),'effect-file-changed');return None,None
    def _name(self,directory,part):
        matches=[n for n in self.observer.names(directory,1_000_001) if logical_path(n).casefold()==part.casefold()]
        require(len(matches)<=1,'path-collision')
        if matches:require(logical_path(matches[0])==part,'path-collision');return matches[0]
        return part
    def _ancestors(self,changes):
        result={}
        for item in changes:
            path=item['path'];require(logical_path(path)==path,'invalid-worker-path');current=self.root;missing=False
            for n,part in enumerate(path.split('/')[:-1],1):
                logical='/'.join(path.split('/')[:n])
                if missing:result[logical]=None;continue
                current=current/self._name(current,part)
                try:identity=self.identity(current)
                except FileNotFoundError:identity=None;missing=True
                require(logical not in result or result[logical]==identity,'effect-ancestor-changed');result[logical]=identity
        return result
    @contextmanager
    def destination(self,path,ancestors,*,create=False,check_identity=True):
        require(logical_path(path)==path,'invalid-worker-path');self.verify_roots();current=self.root
        with ExitStack() as stack:
            stack.enter_context(self.api.ancestors(current))
            h=stack.enter_context(self.api.opened(current));require(list(self.api.state(h,current)['identity'])==self.root_identity,'effect-root-changed')
            for n,part in enumerate(path.split('/')[:-1],1):
                logical='/'.join(path.split('/')[:n]);require(logical in ancestors,'unplanned-effect-ancestor')
                current=current/self._name(current,part);expected=ancestors[logical]
                try:identity=self.identity(current)
                except FileNotFoundError:
                    if not create:yield None;return
                    require(expected is None,'effect-ancestor-missing')
                    self.api.ok(self.api.CreateDirectoryW(str(current),None));self.files.sync_directory(current.parent)
                    identity=self.identity(current)
                require(not check_identity or expected is None or identity==expected,'effect-ancestor-changed')
                h=stack.enter_context(self.api.opened(current));require(list(self.api.state(h,current)['identity'])==identity,'effect-ancestor-changed')
            yield current/self._name(current,path.split('/')[-1])
    def stage(self,application,*,create=False,expected=None):
        _token(application);self.verify_roots();parent=self.authority/'effects';stage=parent/application
        if create:
            try:self.identity(parent)
            except FileNotFoundError:self.files.create_directory(parent)
            self.files.private_directory(parent);self.files.create_directory(stage)
        self.files.private_directory(parent);self.files.private_directory(stage)
        identity=self.identity(stage);require(expected is None or expected==identity,'effect-staging-replaced')
        return stage,identity
    def inspect_target(self,path,ancestors):
        with self.destination(path,ancestors) as target:
            return self.inspect(target,path) if target is not None else (None,None)

    def prepare(self,application,changes,body):
        require(self.locked,'effect-lock-required');ancestors=self._ancestors(changes);stage,native=self.stage(application,create=True);items=[]
        for number,item in enumerate(changes):
            path=item['path'];pre=item['pre'];post=item['post']
            # Windows has no executable bit. Git executable-mode effects need
            # a separate reviewed index operation; never silently erase one.
            require(all(e is None or e.get('kind')=='regular' and e.get('mode')=='100644' for e in (pre,post)),
                    'windows-effect-mode-unavailable')
            with self.destination(path,ancestors) as target:
                observed,pre_native=self.inspect(target,path) if target is not None else (None,None)
                require(observed==pre,'worker-destination-baseline-changed')
            post_name=f'{number:06d}.post';saved_name=f'{number:06d}.original';post_native=None
            if post is not None:
                with self.files.create_stream(stage/post_name) as stream:
                    size=0
                    for raw in body(path):
                        size+=len(raw);require(size<=post['size'],'effect-body-limit');stream.write(raw)
                actual,post_native=self.inspect(stage/post_name,path);require(actual==post,'effect-staged-body-mismatch')
            items.append({**item,'post_name':post_name,'evacuated_name':saved_name,'pre_native':pre_native,'post_native':post_native})
        self.files.sync_directory(stage)
        return dict(application=application,root=self.root_identity,authority=self.authority_identity,stage=native,ancestors=ancestors,items=items)
    def inherited_creation(self,item):
        # Only an authenticated lifecycle caller may opt in, and only for
        # publishing a managed alias at its original name (never evacuation).
        if self.native_entries and item['path'] in NATIVE_ALIASES and item['pre_native'] is not None:
            return item['pre_native'][2]
        return None
    def published_identity(self,item,native):
        expected=item['post_native']
        if native==expected:return True
        prior=self.inherited_creation(item)
        return (prior is not None and native is not None and expected is not None and
                native[:2]==expected[:2] and native[2]==prior)
    def inspect_state(self,manifest,index):
        require(self.locked,'effect-lock-required');self.verify_roots();item=manifest['items'][index];path=item['path']
        require(manifest['root']==self.root_identity and manifest['authority']==self.authority_identity,'effect-port-identity-mismatch')
        stage,_=self.stage(manifest['application'],expected=manifest['stage'])
        with self.destination(path,manifest['ancestors']) as target:current,native=self.inspect(target,path) if target is not None else (None,None)
        saved,saved_native=self.inspect(stage/item['evacuated_name'],path);post,post_native=self.inspect(stage/item['post_name'],path)
        if saved is not None:require(saved_native==item['pre_native'],'effect-evacuated-file-changed')
        modified=saved is not None and saved!=item['pre']
        if post is not None:require(post==item['post'] and post_native==item['post_native'],'effect-staged-file-changed')
        if current==item['pre'] and native==item['pre_native'] and saved is None:
            require(post==item['post'] and post_native==item['post_native'],'effect-staged-file-missing');return dict(state='pre',retained_original_modified=False)
        if current==item['post'] and self.published_identity(item,native) and post is None:
            require(saved_native==item['pre_native'] and (saved is None)==(item['pre'] is None),'effect-evacuated-file-missing')
            return dict(state='post',retained_original_modified=modified)
        if current is None and item['pre'] is not None and saved is not None:
            require(post==item['post'] and post_native==item['post_native'],'effect-staged-file-missing');return dict(state='evacuated',retained_original_modified=modified)
        raise RecordError('effect-path-unknown')
    def retained_original_matches(self,manifest,index):
        require(self.locked,'effect-lock-required');self.verify_roots();item=manifest['items'][index]
        require(manifest['root']==self.root_identity and manifest['authority']==self.authority_identity,'effect-port-identity-mismatch')
        stage,_=self.stage(manifest['application'],expected=manifest['stage'])
        saved,native=self.inspect(stage/item['evacuated_name'],item['path'])
        return saved==item['pre'] and native==item['pre_native']

    def state(self,manifest,index):return self.inspect_state(manifest,index)['state']
    def _move(self,source,target,entry,identity,before_effect,event,*,inherited_creation=None):
        options={} if inherited_creation is None else dict(inherited_creation=inherited_creation)
        return self.mover.move(source,target,expected=dict(identity=identity,size=entry['size'],sha256=entry['sha256']),
                               before_effect=before_effect,event=event,**options)
    def apply_one(self,manifest,index,*,before_effect=lambda:None,event=lambda _:None):
        state=self.inspect_state(manifest,index);item=manifest['items'][index]
        require(not state['retained_original_modified'],'effect-evacuated-file-changed')
        if state['state']=='post':self.sync(manifest,index);return
        stage,_=self.stage(manifest['application'],expected=manifest['stage'])
        with self.api.ancestors(stage),self.api.opened(stage) as held:
            require(list(self.api.state(held,stage)['identity'])==manifest['stage'],'effect-staging-replaced')
            with self.destination(item['path'],manifest['ancestors'],create=True) as target:
                if state['state']=='pre' and item['pre'] is not None:
                    self._move(target,stage/item['evacuated_name'],item['pre'],item['pre_native'],before_effect,event)
                if item['post'] is not None:
                    self._move(stage/item['post_name'],target,item['post'],item['post_native'],before_effect,event,
                               inherited_creation=self.inherited_creation(item))
                self.files.sync_directory(target.parent);self.files.sync_directory(stage)
        self.sync(manifest,index)
    def sync(self,manifest,index):
        state=self.inspect_state(manifest,index);require(state['state']=='post' and not state['retained_original_modified'],'effect-post-state-required')
        item=manifest['items'][index];stage,_=self.stage(manifest['application'],expected=manifest['stage'])
        with self.destination(item['path'],manifest['ancestors']) as target:
            paths=([stage/item['evacuated_name']] if item['pre'] is not None else [])+([target] if item['post'] is not None else [])
            for path in paths:
                with self.api.ancestors(path),self.api.opened(path,access=0x40000080,share=1) as h:
                    self.api.state(h,path);self.api.ok(self.api.FlushFileBuffers(h))
            if target is not None:self.files.sync_directory(target.parent)
            self.files.sync_directory(stage)
        final=self.inspect_state(manifest,index)
        require(final['state']=='post' and not final['retained_original_modified'],'effect-post-state-required')
    def cancellable(self,manifest,index):
        state=self.inspect_state(manifest,index)
        require(state['state']=='pre' and not state['retained_original_modified'],'worker-cancel-requires-all-pre')
