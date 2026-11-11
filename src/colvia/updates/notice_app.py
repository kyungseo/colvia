"""Prepare the fixed macOS receiver files; never register or launch the app.

A signed release inventory authenticates these bytes. Replacement retains old
files and keeps a pending barrier until the runtime and app both agree.
"""
from pathlib import Path
import hashlib,os,plistlib
from ..codec import canonical_bytes,decode_canonical,require
from ..storage.sqlite import _token
from .preparation import pending_area,fresh_area
from ..platforms.effects_port import effects as effect_port

APP='ColviaWork.app'
PARTS=('Contents/Info.plist','Contents/MacOS/ColviaWork','Contents/Resources/Colvia.icns','Contents/_CodeSignature/CodeResources')
PREFIX='receiver/'+APP+'/'

class MacNoticeFiles:
    def __init__(self,home,target,operation,*,port=effect_port):
        _token(operation);self.home=home;self.files=home.files;self.target=target;self.operation=operation;self.port=port
        self.area=home.root/'operations'/(operation+'-notice-app');self.pending=home.root/'notice-app.pending'
    def pending_token(self):
        self.area,raw=pending_area(self.files,self.pending,self.home.root/'operations',self.operation+'-notice-app',self.operation,self.target)
        return raw
    def candidate(self):
        slot=self.home.slots.verify(self.target);location=self.home.slots.root/'slots'/slot.slot
        manifest=decode_canonical(self.files.read(location/'manifest.json',4*1024*1024))
        rows=[r for r in manifest['inventory'] if r['path'].startswith('receiver/')]
        if not rows:return None
        require(self.home.os_name=='macos' and {r['path'] for r in rows}=={PREFIX+p for p in PARTS},'notice-package-invalid')
        values=[];bodies={}
        for row in rows:
            path=APP+'/'+row['path'][len(PREFIX):];values.append(dict(row,path=path))
            bodies[path]=self.files.read(location/row['path'],64*1024*1024)
        info=plistlib.loads(bodies[APP+'/Contents/Info.plist'])
        require(info.get('CFBundleIdentifier')=='org.colvia.work.notice' and info.get('CFBundleExecutable')=='ColviaWork' and
                info.get('CFBundlePackageType')=='APPL' and type(info.get('CFBundleVersion')) is str and
                info['CFBundleVersion'].isascii() and info['CFBundleVersion'].replace('.','').isdigit(),'notice-package-identity')
        require(next(r for r in rows if r['path']==PREFIX+'Contents/MacOS/ColviaWork')['mode']=='100755','notice-package-not-executable')
        return sorted(values,key=lambda row:row['path']),bodies
    def record(self,rows):return canonical_bytes(dict(version=1,platform='macos',files=rows))
    def check_files(self,rows):
        base=self.home.root/'bin';app=base/APP;seen=set()
        if app.exists():
            require(not app.is_symlink(),'notice-app-symlink')
            for p in app.rglob('*'):
                require(not p.is_symlink(),'notice-app-symlink')
                if p.is_dir():continue
                require(p.is_file(),'notice-app-special-file');seen.add(p.relative_to(base).as_posix())
        require(seen=={r['path'] for r in rows},'notice-app-inventory-changed')
        for row in rows:
            raw=self.files.read(base/row['path'],64*1024*1024)
            require(len(raw)==row['size'] and hashlib.sha256(raw).hexdigest()==row['sha256'],'notice-app-bytes-changed')
            require(('100755' if (base/row['path']).stat().st_mode&0o111 else '100644')==row['mode'],'notice-app-mode-changed')
    def prepare(self):
        candidate=self.candidate()
        if candidate is None:return False
        rows,bodies=candidate;f=self.files;h=self.home
        if f.exists(self.pending):
            self.pending_token();require(f.exists(self.area/'prepared.json'),'notice-app-preparation-incomplete');return True
        old=f.read(h.root/'receiver.json') if f.exists(h.root/'receiver.json') else None
        previous=[]
        if old is not None:
            record=decode_canonical(old);require(set(record)=={'version','platform','files'} and record['version']==1 and record['platform']=='macos','notice-app-description-invalid')
            previous=record['files'];require({r['path'] for r in previous}=={APP+'/'+p for p in PARTS},'notice-app-description-invalid')
        self.check_files(previous)
        if old==self.record(rows):return False
        self.area,token=fresh_area(f,h.root/'operations',self.operation+'-notice-app',self.operation,self.target)
        before={r['path']:r for r in previous};after={r['path']:r for r in rows}
        changes=[dict(path=p,pre=before.get(p),post=after[p]) for p in sorted(after)]
        port=self.port(h.root/'bin',self.area)
        with port.exclusion():manifest=port.prepare(self.operation,changes,lambda p:iter((bodies[p],)))
        f.create(self.area/'prepared.json',canonical_bytes(dict(version=1,target=self.target,before=None if old is None else old.decode(),
            after=self.record(rows).decode(),effects=manifest)))
        f.create(self.pending,token);return True
    def apply(self,*,guard=lambda:None,checkpoint=lambda _:None):
        candidate=self.candidate()
        if candidate is None:return
        rows,_=candidate;f=self.files;h=self.home;after=self.record(rows)
        if not f.exists(self.pending):
            require(f.read(h.root/'receiver.json')==after,'notice-app-update-unprepared');self.check_files(rows);return
        token=self.pending_token()
        plan=decode_canonical(f.read(self.area/'prepared.json',4*1024*1024));manifest=plan['effects']
        require(plan['version']==1 and plan['target']==self.target and plan['after'].encode()==after and
                [r['post'] for r in manifest['items']]==rows,'notice-app-preparation-changed')
        before=None if plan['before'] is None else plan['before'].encode()
        actual=f.read(h.root/'receiver.json') if f.exists(h.root/'receiver.json') else None
        require(actual in (before,after),'notice-app-description-changed')
        port=self.port(h.root/'bin',self.area)
        with port.exclusion(create=False):
            for i in range(len(manifest['items'])):
                guard();require(not port.inspect_state(manifest,i)['retained_original_modified'],'notice-app-original-changed')
                port.apply_one(manifest,i,before_effect=guard,event=lambda phase:checkpoint('notice-app-'+phase))
            for i in range(len(manifest['items'])):port.sync(manifest,i)
            self.check_files(rows);guard()
            if actual!=after:
                if before is None:f.create(h.root/'receiver.json',after)
                else:f.replace(h.root/'receiver.json',after,before)
    def finish(self):
        candidate=self.candidate()
        if candidate is None:return
        rows,_=candidate;self.check_files(rows);f=self.files
        require(self.home.slots.selection()[1]['selected']==self.target and f.read(self.home.root/'receiver.json')==self.record(rows),'notice-app-runtime-not-selected')
        if f.exists(self.pending):
            token=self.pending_token()
            receipt=canonical_bytes(dict(version=1,target=self.target))
            if f.exists(self.area/'completed.json'):require(f.read(self.area/'completed.json')==receipt,'notice-app-completion-changed')
            else:f.create(self.area/'completed.json',receipt)
            f.remove(self.pending,token)
