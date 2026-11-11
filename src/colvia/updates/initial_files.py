"""Prospective first-install ownership, captured before each live publication."""
import hashlib,os,uuid
from pathlib import PurePosixPath
from ..codec import canonical_bytes,decode_canonical,require
from ..platforms.owned_install_files import present,capture,move,LIMIT
from .notice_app import MacNoticeFiles

class InitialFiles:
    def __init__(self,home,operation,target,raw):
        self.home=home;self.f=home.files;self.operation=operation;self.target=target;self.raw=raw
        self.area=home.root/'operations'/operation;self.path=self.area/'publication.json'
    def expected(self):
        h=self.home;raw=self.raw
        names=('colvia.exe','colvia-manage.exe') if h.os_name=='windows' else ('colvia','colvia-manage')
        content={'bin/'+n:(raw,h.os_name!='windows') for n in names}
        content['entry.json']=(canonical_bytes(dict(version=1,os=h.os_name,architecture=h.architecture,
            sha256=hashlib.sha256(raw).hexdigest())),False)
        app=MacNoticeFiles(h,self.target,self.operation);candidate=app.candidate()
        if candidate:
            rows,bodies=candidate
            content.update({'bin/'+r['path']:(bodies[r['path']],r['mode']=='100755') for r in rows})
            content['receiver.json']=(app.record(rows),False)
        directories={str(p) for name in content for p in PurePosixPath(name).parents if str(p)!='.'}
        return directories,content
    def read(self):
        p=decode_canonical(self.f.read(self.path,4*1024*1024));dirs,content=self.expected()
        require(type(p) is dict and set(p)=={'version','operation','target','home','stage','stage_identity','nodes'} and
                p['version']==1 and p['operation']==self.operation and p['target']==self.target and
                p['home']==self.f.directory_identity(self.home.root),'initial-publication-invalid')
        require(type(p['stage']) is str and p['stage'].startswith('publication-') and len(p['stage'])==44 and
                all(c in '0123456789abcdef' for c in p['stage'][12:]),'initial-publication-invalid')
        stage=self.area/p['stage'];require(self.f.directory_identity(stage)==p['stage_identity'],'initial-stage-changed')
        names=sorted(dirs|set(content),key=lambda v:(len(PurePosixPath(v).parts),v))
        require(type(p['nodes']) is list and len(p['nodes'])==len(names),'initial-publication-invalid')
        for i,(node,name) in enumerate(zip(p['nodes'],names)):
            require(set(node)=={'path','stage','snapshot'} and node['path']==name and node['stage']==str(i),'initial-publication-invalid')
            v=node['snapshot'];require(type(v) is dict and type(v.get('identity')) is list and len(v['identity'])==3,'initial-publication-invalid')
            if name in dirs:require(set(v)=={'kind','identity','mode','permissions'} and v['kind']=='directory' and v['permissions']==(0 if self.home.os_name=='windows' else 0o700),'initial-publication-invalid')
            else:
                raw,executable=content[name];mode='100755' if executable and self.home.os_name!='windows' else '100644'
                require(set(v)=={'kind','identity','mode','permissions','size','sha256'} and v['kind']=='file' and v['mode']==mode and
                        v['permissions']==(0 if self.home.os_name=='windows' else (0o700 if executable else 0o600)) and v['size']==len(raw) and v['sha256']==hashlib.sha256(raw).hexdigest(),'initial-publication-invalid')
        return p
    def prepare(self):
        if self.f.exists(self.path):return self.read()
        dirs,content=self.expected()
        for name in ('bin','entry.json','receiver.json','native-update.json','notice-app.pending'):
            require(not present(self.home.root/name),'initial-publication-foreign')
        stage=self.area/('publication-'+uuid.uuid4().hex);self.f.create_directory(stage);nodes=[]
        for i,name in enumerate(sorted(dirs|set(content),key=lambda v:(len(PurePosixPath(v).parts),v))):
            path=stage/str(i)
            if name in dirs:self.f.create_directory(path)
            else:
                raw,executable=content[name];self.f.create(path,raw,executable=executable)
            nodes.append(dict(path=name,stage=str(i),snapshot=capture(self.f,path)))
        value=dict(version=1,operation=self.operation,target=self.target,home=self.f.directory_identity(self.home.root),
                   stage=stage.name,stage_identity=self.f.directory_identity(stage),nodes=nodes)
        self.f.create(self.path,canonical_bytes(value));return self.read()
    def states(self,plan):
        states=[];h=self.home;f=self.f;expected=set()
        require(f.directory_identity(h.root)==plan['home'] and f.directory_identity(self.area/plan['stage'])==plan['stage_identity'],'initial-stage-changed')
        for node in plan['nodes']:
            staged=self.area/plan['stage']/node['stage'];live=h.root/node['path']
            a=present(staged);b=present(live)
            require(a!=b,'initial-publication-unknown')
            require(capture(f,staged if a else live)==node['snapshot'],'native-entry-changed')
            states.append('staged' if a else 'live')
            if b:expected.add(node['path'])
        observed=set()
        if present(h.root/'bin'):
            observed.add('bin')
            for path in (h.root/'bin').rglob('*'):
                capture(f,path);observed.add(path.relative_to(h.root).as_posix())
        for name in ('entry.json','receiver.json'):
            if present(h.root/name):observed.add(name)
        require(observed==expected,'initial-publication-extra-path');return states
    def publish(self,*,guard,checkpoint):
        p=self.prepare();self.states(p)
        for node in p['nodes']:
            guard();states=self.states(p)
            if states[p['nodes'].index(node)]=='staged':
                checkpoint('initial-before-publish')
                # Guard and inventory again after an injectable/racing boundary.
                guard();self.states(p)
                parent=self.home.root/node['path'];parent=parent.parent
                snapshots={n['path']:n['snapshot'] for n in p['nodes']}
                parent_id=p['home'] if parent==self.home.root else snapshots[parent.relative_to(self.home.root).as_posix()]['identity']
                if self.home.os_name!='windows':parent_id=parent_id[:2]
                move(self.f,self.area/p['stage']/node['stage'],self.home.root/node['path'],node['snapshot'],
                     parent_identities={self.area/p['stage']:p['stage_identity'],parent:parent_id})
                checkpoint('initial-after-publish')
        self.verify_final(sync=True)
    def verify_final(self,*,sync=False):
        p=self.read();require(all(x=='live' for x in self.states(p)),'initial-publication-incomplete')
        if sync:
            # Re-establish durability even when a previous move lost its sync ack.
            parents={self.home.root,self.area/p['stage'],*(self.home.root/n['path'] for n in p['nodes'] if n['snapshot']['kind']=='directory')}
            for parent in sorted(parents,key=str):self.f.sync_directory(parent)
            require(all(x=='live' for x in self.states(p)),'initial-publication-incomplete')
