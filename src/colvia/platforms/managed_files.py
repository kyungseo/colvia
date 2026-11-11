"""Platform-independent owned-file connection/detachment protocol.

Native ports provide identity, retention, exclusion and exact move semantics.
The common code owns user scope, role ordering and reviewed bytes only.
"""
from contextlib import contextmanager
from pathlib import Path
import hashlib
from ..codec import require
from ..lifecycle import ORDER
from ..storage.sqlite import _token
from ..tree import logical_path

class ManagedFiles:
    def __init__(self,authority,locations,*,files,effects):
        self.authority=Path(authority);self.files=files;self.effects=effects;self.locations=dict(locations);self.locked=False
        require(0<len(self.locations)<=128,'detach-location-limit')
        for name,root in self.locations.items():
            _token(name);require(Path(root).is_absolute(),'detach-absolute-root-required')
            self.effects(root,self.authority)
    def _port(self,root):
        require(root in self.locations,'detach-root-unavailable')
        return self.effects(self.locations[root],self.authority)
    @contextmanager
    def exclusion(self):
        require(not self.locked,'detach-lock-reentry')
        lock=self.authority/'detach.lock'
        try:self.files.create(lock,b'')
        except FileExistsError:require(self.files.read(lock)==b'','detach-lock-invalid')
        with self.files.exclusion(lock):
            self.locked=True
            try:yield
            finally:self.locked=False
    def preview(self,changes):
        require(type(changes) is list and 0<len(changes)<=128,'detach-change-limit')
        result=[];targets=set();roles=[];total=0
        for change in changes:
            require(type(change) is dict and set(change)=={'role','root','path','before','after'} and change['role'] in ORDER,
                    'invalid-detach-change')
            root,path=change['root'],change['path'];require(logical_path(path)==path,'invalid-detach-path')
            require((root,path) not in targets,'duplicate-detach-target');targets.add((root,path));roles.append(ORDER[change['role']])
            before,after=change['before'],change['after']
            require(type(before) is bytes and len(before)<=1024*1024 and
                    (after is None or type(after) is bytes and len(after)<=1024*1024) and before!=after,'invalid-detach-body')
            total+=len(before)+(len(after) if after is not None else 0)
            require(total<=8*1024*1024,'detach-total-body-limit')
            if change['role']=='locator':require(after is None,'detach-locator-removal-required')
            port=self._port(root);ancestors=port._ancestors([dict(path=path)])
            pre,native=port.inspect_target(path,ancestors)
            require(pre is not None and pre['size']==len(before) and pre['sha256']==hashlib.sha256(before).hexdigest(),
                    'detach-files-changed')
            post=None if after is None else {**pre,'size':len(after),'sha256':hashlib.sha256(after).hexdigest()}
            result.append(dict(role=change['role'],root=root,path=path,pre=pre,post=post,native=native,
                               root_identity=port.root_identity,authority_identity=port.authority_identity))
        require(roles==sorted(roles) and roles[-1]==ORDER['locator'],'invalid-detach-order')
        return result
    def prepare(self,operation,changes):
        require(self.locked,'detach-lock-required');_token(operation);preview=self.preview(changes);steps=[]
        for n,(planned,change) in enumerate(zip(preview,changes)):
            port=self._port(planned['root'])
            with port.exclusion():
                m=port.prepare(operation+'-'+str(n),[dict(path=planned['path'],pre=planned['pre'],post=planned['post'])],
                               lambda _:iter(()) if change['after'] is None else iter([change['after']]))
            steps.append(dict(role=planned['role'],root=planned['root'],path=planned['path'],native=m))
        return dict(operation=operation,steps=steps)
    def state(self,manifest,index):
        require(self.locked,'detach-lock-required');step=manifest['steps'][index];port=self._port(step['root'])
        with port.exclusion(create=False):return port.state(step['native'],0)
    def apply(self,manifest,index,*,before_effect,event):
        require(self.locked,'detach-lock-required');step=manifest['steps'][index];port=self._port(step['root'])
        with port.exclusion(create=False):port.apply_one(step['native'],0,before_effect=before_effect,event=event)


class ManagedConnect(ManagedFiles):
    replace_locator=False
    def preview(self,changes):
        require(type(changes) is list and 0<len(changes)<=128,'connect-change-limit')
        result=[];targets=set();roles=[];total=0
        for change in changes:
            require(type(change) is dict and set(change)=={'role','root','path','before','after','mode'} and change['role'] in ORDER,
                    'invalid-connect-change')
            root,path=change['root'],change['path'];require(logical_path(path)==path,'invalid-connect-path')
            require((root,path) not in targets,'duplicate-connect-target');targets.add((root,path));roles.append(ORDER[change['role']])
            before,after=change['before'],change['after'];mode=change['mode']
            require((before is None or type(before) is bytes and len(before)<=1024*1024) and
                    type(after) is bytes and 0<len(after)<=1024*1024 and before!=after and mode in ('100644','100755'),'invalid-connect-body')
            total+=(len(before) if before else 0)+len(after);require(total<=8*1024*1024,'connect-total-body-limit')
            if change['role']=='locator' and not self.replace_locator:require(before is None,'connect-locator-already-present')
            port=self._port(root);ancestors=port._ancestors([dict(path=path)])
            pre,native=port.inspect_target(path,ancestors)
            require((pre is None and before is None) or (pre is not None and before is not None and
                    pre['size']==len(before) and pre['sha256']==hashlib.sha256(before).hexdigest()),'connect-files-changed')
            # Never change the executable bit of an existing user entry file.
            require(pre is None or pre['mode']==mode,'connect-mode-change-not-approved')
            post=dict(path=path,kind='regular',mode=mode,size=len(after),sha256=hashlib.sha256(after).hexdigest())
            result.append(dict(role=change['role'],root=root,path=path,pre=pre,post=post,native=native,
                               root_identity=port.root_identity,authority_identity=port.authority_identity))
        require(roles==sorted(roles) and roles[-1]==ORDER['locator'],'invalid-connect-order')
        return result
