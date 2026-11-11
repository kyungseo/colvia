"""Retained-original native entry replacement under the management/runtime lease.

Version 1 installation packages use the stable version 1 runtime-pointer and
argument protocol. Both aliases must keep that protocol while either runtime
selection remains usable. A future incompatible entry needs a new contract.
"""
from pathlib import Path
import hashlib,os
from ..codec import canonical_bytes,decode_canonical,require
from ..storage.sqlite import _token
from .preparation import pending_area,fresh_area

LIMIT=64*1024*1024

from ..platforms.effects_port import effects as effect_port

class NativeEntryUpdate:
    def __init__(self,home,target,operation,*,port=effect_port):
        _token(operation);self.home=home;self.files=home.files;self.target=target;self.operation=operation;self.port=port
        self.area=home.root/'operations'/(operation+'-entry');self.pending=home.root/'native-update.json'
    def pending_token(self):
        self.area,raw=pending_area(self.files,self.pending,self.home.root/'operations',self.operation+'-entry',self.operation,self.target)
        return raw
    def candidate(self):
        from .installation import configuration
        h=self.home;slot=h.slots.verify(self.target);location=h.slots.root/'slots'/slot.slot
        if not self.files.exists(location/'installation.json'):
            # Bare runtime composition fixtures have no native entry. A real
            # installed home must never silently lose its installation contract.
            require(not self.files.exists(h.root/'entry.json'),'native-entry-configuration-required');return None
        config=configuration(self.files,location);raw=self.files.read(location/config['native_entry'],LIMIT)
        manifest=decode_canonical(self.files.read(location/'manifest.json',4*1024*1024))
        require(any(e['path']==config['native_entry'] and e['mode']=='100755' for e in manifest['inventory']),'native-entry-not-executable')
        return raw
    def names(self):return ('colvia.exe','colvia-manage.exe') if self.home.os_name=='windows' else ('colvia','colvia-manage')
    def description(self,raw):
        return canonical_bytes(dict(version=1,os=self.home.os_name,architecture=self.home.architecture,sha256=hashlib.sha256(raw).hexdigest()))
    def prepare(self):
        raw=self.candidate()
        if raw is None:return False
        h=self.home;f=self.files;old=f.read(h.root/'entry.json');record=decode_canonical(old)
        require(set(record)=={'version','os','architecture','sha256'} and record['version']==1 and
                record['os']==h.os_name and record['architecture']==h.architecture,'native-entry-description-invalid')
        if f.exists(self.pending):
            self.pending_token()
            require(f.exists(self.area/'prepared.json'),'native-entry-preparation-incomplete');return True
        bodies={name:f.read(h.root/'bin'/name,LIMIT) for name in self.names()}
        require(all(hashlib.sha256(b).hexdigest()==record['sha256'] for b in bodies.values()),'native-entry-changed')
        if all(b==raw for b in bodies.values()):return False
        self.area,token=fresh_area(f,h.root/'operations',self.operation+'-entry',self.operation,self.target)
        mode='100644' if h.os_name=='windows' else '100755'
        def entry(name,b):return dict(path=name,kind='regular',mode=mode,size=len(b),sha256=hashlib.sha256(b).hexdigest())
        changes=[dict(path=n,pre=entry(n,bodies[n]),post=entry(n,raw)) for n in self.names()]
        effects=self.port(h.root/'bin',self.area)
        with effects.exclusion():manifest=effects.prepare(self.operation,changes,lambda _:iter((raw,)))
        f.create(self.area/'prepared.json',canonical_bytes(dict(version=1,target=self.target,before=old.decode('utf-8'),
            after=self.description(raw).decode('utf-8'),effects=manifest)))
        # A preparation interruption has made no live changes. Once pending is
        # published, every subsequent update must acknowledge this operation.
        f.create(self.pending,token);return True
    def apply(self,*,guard=lambda:None,checkpoint=lambda _:None):
        raw=self.candidate()
        if raw is None:return
        f=self.files;h=self.home
        if not f.exists(self.pending):
            require(f.read(h.root/'entry.json')==self.description(raw) and all(f.read(h.root/'bin'/n,LIMIT)==raw for n in self.names()),
                    'native-entry-update-unprepared');return
        token=self.pending_token()
        plan=decode_canonical(f.read(self.area/'prepared.json',4*1024*1024))
        require(plan['version']==1 and plan['target']==self.target and plan['after'].encode()==self.description(raw),'native-entry-preparation-changed')
        manifest=plan['effects'];mode='100644' if h.os_name=='windows' else '100755'
        require([i['path'] for i in manifest['items']]==list(self.names()) and all(i['post']==dict(path=i['path'],kind='regular',mode=mode,
            size=len(raw),sha256=hashlib.sha256(raw).hexdigest()) for i in manifest['items']),'native-entry-preparation-changed')
        before=plan['before'].encode();after=plan['after'].encode()
        require(f.read(h.root/'entry.json') in (before,after),'native-entry-description-changed')
        effects=self.port(h.root/'bin',self.area)
        with effects.exclusion(create=False):
            for i in range(len(manifest['items'])):
                guard();require(not effects.inspect_state(manifest,i)['retained_original_modified'],'native-entry-original-changed')
                effects.apply_one(manifest,i,before_effect=guard,event=lambda phase:checkpoint('native-entry-'+phase))
            for i in range(len(manifest['items'])):effects.sync(manifest,i)
            require(all(f.read(h.root/'bin'/n,LIMIT)==raw for n in self.names()),'native-entry-changed')
            guard()
            if f.read(h.root/'entry.json')==before:f.replace(h.root/'entry.json',after,before)
            checkpoint('native-entry-described')
        # Keep the pending barrier through runtime activation. Completion is a
        # separate call, so a crash cannot authorize a different release.
    def finish(self):
        raw=self.candidate()
        if raw is None:return
        f=self.files;h=self.home
        require(h.slots.selection()[1]['selected']==self.target,'native-entry-runtime-not-selected')
        require(f.read(h.root/'entry.json')==self.description(raw) and all(f.read(h.root/'bin'/n,LIMIT)==raw for n in self.names()),'native-entry-changed')
        if f.exists(self.pending):
            token=self.pending_token()
            completed=canonical_bytes(dict(version=1,target=self.target))
            if f.exists(self.area/'completed.json'):require(f.read(self.area/'completed.json')==completed,'native-entry-completion-changed')
            else:f.create(self.area/'completed.json',completed)
            f.remove(self.pending,token)
