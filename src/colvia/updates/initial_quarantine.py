"""Offline retirement of exactly owned, unselected first-install files.

The caller is a verified bootstrap. No old code is executed, no trust state is
reset and no receiver registration is changed. A terminal receipt never revisits
live paths that may already belong to the successor.
"""
import hashlib,os,uuid
from ..codec import canonical_bytes,decode_canonical,require
from ..storage.sqlite import _token
from ..platforms.owned_install_files import present,capture,move,remove_empty
from .initial_files import InitialFiles
from .initial_home import initial_head,retry_claim
from .package import descriptor

FORBIDDEN=('native-update.json','notice-app.pending','notice-choice.json','notice-registration.json','notice-registration.pending')

def completed(home,operation):
    area=home.root/'operations'/operation;f=home.files
    raw=f.read(area/'quarantine-intent.json',4*1024*1024);intent=decode_canonical(raw)
    require(type(intent) is dict and set(intent)=={'version','operation','receipt','preview','successor','area','area_identity'} and
            type(intent['version']) is int and intent['version']==1 and intent['operation']==operation and
            type(intent['receipt']) is str and len(intent['receipt'])==64 and
            all(c in '0123456789abcdef' for c in intent['receipt']),'initial-quarantine-invalid')
    done=decode_canonical(f.read(area/'quarantine-complete.json'))
    require(done==dict(version=1,operation=operation,receipt=intent['receipt'],successor=intent['successor'],
        intent_sha256=hashlib.sha256(raw).hexdigest(),state='quarantined'),'initial-quarantine-completion-changed')
    _token(intent['successor']);return done

class InitialQuarantine:
    def __init__(self,home,trust,config,anchor):self.home=home;self.f=home.files;self.trust=trust;self.config=config;self.anchor=anchor
    def base(self,operation):
        _token(operation);h=self.home;f=self.f
        require(initial_head(h,self.trust,self.config,self.anchor)==operation,'initial-attempt-not-current')
        require(not present(h.slots.root/'runtime.json') and not h.projects(),'initial-quarantine-already-active')
        require(not f.exists(h.root/'operations'/operation/'completed.json'),'initial-quarantine-already-active')
        for name in FORBIDDEN:require(not present(h.root/name),'initial-quarantine-foreign-state')
    def publication(self,operation):
        from .installation import configuration
        h=self.home;f=self.f;area=h.root/'operations'/operation
        p=decode_canonical(f.read(area/'prepared.json',4*1024*1024))
        require(type(p) is dict and set(p)=={'version','target','download','native_sha256'} and p['version']==1,'installation-preparation-invalid')
        d=descriptor(p['download'].get('custom'),channel=self.config['channel'],os_name=h.os_name,architecture=h.architecture)
        slot=h.slots.verify(p['target'])
        require(p['download'].get('path')==self.config['target'] and p['target']['manifest_sha256']==d['manifest_sha256'] and
                slot.release==d['release'] and slot.sequence==d['sequence'],'installation-release-description-changed')
        location=h.slots.root/'slots'/slot.slot;c=configuration(f,location)
        require(all(c[k]==self.config[k] for k in ('channel','metadata_url','target_url','target')),'installation-channel-changed')
        raw=f.read(location/c['native_entry'],64*1024*1024)
        require(hashlib.sha256(raw).hexdigest()==p['native_sha256'],'native-entry-changed')
        service=InitialFiles(h,operation,p['target'],raw);plan=service.read()
        return service,plan
    def preview(self,*,operation):
        with self.f.exclusion(self.home.root/'management.lock'):
            self.base(operation);area=self.home.root/'operations'/operation
            require(not self.f.exists(area/'quarantine-intent.json'),'initial-quarantine-started')
            service,plan=self.publication(operation);states=service.states(plan)
            nodes=[node for node,state in zip(plan['nodes'],states) if state=='live']
            require(nodes,'initial-quarantine-no-live-files')
            value=dict(version=1,operation=operation,home=plan['home'],
                publication_sha256=hashlib.sha256(self.f.read(service.path,4*1024*1024)).hexdigest(),nodes=nodes)
            return dict(state='quarantine-preview',receipt=hashlib.sha256(canonical_bytes(value)).hexdigest(),
                operation=operation,paths=[n['path'] for n in nodes],automatic_retry=False,preview=value)
    def _intent(self,operation):
        area=self.home.root/'operations'/operation;f=self.f
        value=decode_canonical(f.read(area/'quarantine-intent.json',4*1024*1024))
        require(type(value) is dict and set(value)=={'version','operation','receipt','preview','successor','area','area_identity'} and
                value['version']==1 and value['operation']==operation,'initial-quarantine-invalid')
        _token(value['successor']);name=value['area']
        require(type(name) is str and name.startswith('quarantine-') and len(name)==43 and
                all(c in '0123456789abcdef' for c in name[11:]),'initial-quarantine-invalid')
        require(f.directory_identity(area/name)==value['area_identity'] and
                hashlib.sha256(canonical_bytes(value['preview'])).hexdigest()==value['receipt'],'initial-quarantine-changed')
        service,plan=self.publication(operation)
        require(value['preview']['operation']==operation and value['preview']['home']==plan['home'] and
                value['preview']['publication_sha256']==hashlib.sha256(f.read(service.path,4*1024*1024)).hexdigest(),
                'initial-quarantine-changed')
        known={n['path']:n for n in plan['nodes']};nodes=value['preview']['nodes']
        require(type(nodes) is list and nodes and len({n['path'] for n in nodes})==len(nodes) and
                all(known.get(n['path'])==n for n in nodes),'initial-quarantine-changed')
        return value
    def _states(self,operation,intent):
        h=self.home;f=self.f;area=h.root/'operations'/operation;quarantine=area/intent['area'];states=[];live_paths=set()
        require(f.directory_identity(h.root)==intent['preview']['home'] and f.directory_identity(quarantine)==intent['area_identity'],'initial-quarantine-changed')
        for i,node in enumerate(intent['preview']['nodes']):
            live=h.root/node['path'];saved=quarantine/str(i);a=present(live);b=present(saved)
            if node['snapshot']['kind']=='directory':
                require(not b,'initial-quarantine-unknown')
                if a:require(capture(f,live)==node['snapshot'],'initial-quarantine-file-changed');live_paths.add(node['path'])
                else:require(f.exists(quarantine/('remove-'+str(i)+'.json')) and
                    f.read(quarantine/('remove-'+str(i)+'.json'))==canonical_bytes(node),'initial-quarantine-unknown')
                states.append('live' if a else 'removed')
            else:
                require(a!=b,'initial-quarantine-unknown')
                require(capture(f,live if a else saved)==node['snapshot'],'initial-quarantine-file-changed')
                if a:live_paths.add(node['path'])
                states.append('live' if a else 'retained')
        observed=set()
        if present(h.root/'bin'):
            observed.add('bin')
            for p in (h.root/'bin').rglob('*'):capture(f,p);observed.add(p.relative_to(h.root).as_posix())
        for name in ('entry.json','receiver.json'):
            if present(h.root/name):observed.add(name)
        require(observed==live_paths,'initial-quarantine-extra-path')
        return states
    def apply(self,*,operation,receipt,checkpoint=lambda _:None):
        _token(operation);h=self.home;f=self.f;area=h.root/'operations'/operation
        with f.exclusion(h.root/'management.lock'):
            # Verify the home/chain, but terminal receipts never inspect live files.
            initial_head(h,self.trust,self.config,self.anchor)
            if f.exists(area/'quarantine-complete.json'):
                result=completed(h,operation);require(result['receipt']==receipt,'initial-quarantine-review-changed');return result
            self.base(operation)
            if not f.exists(area/'quarantine-intent.json'):
                service,plan=self.publication(operation);states=service.states(plan)
                nodes=[n for n,state in zip(plan['nodes'],states) if state=='live'];require(nodes,'initial-quarantine-no-live-files')
                preview=dict(version=1,operation=operation,home=plan['home'],
                    publication_sha256=hashlib.sha256(f.read(service.path,4*1024*1024)).hexdigest(),nodes=nodes)
                require(hashlib.sha256(canonical_bytes(preview)).hexdigest()==receipt,'initial-quarantine-review-changed')
                q=area/('quarantine-'+uuid.uuid4().hex);f.create_directory(q)
                require(f.directory_identity(q)[0]==plan['home'][0],'initial-node-volume-mismatch')
                intent=dict(version=1,operation=operation,receipt=receipt,preview=preview,successor='install-'+uuid.uuid4().hex,
                    area=q.name,area_identity=f.directory_identity(q))
                # Recheck after staging and before the irreversible retirement.
                require(service.states(plan)==states,'initial-quarantine-review-changed');self.base(operation)
                f.create(area/'quarantine-intent.json',canonical_bytes(intent));checkpoint('quarantine-intent')
            intent=self._intent(operation);require(intent['receipt']==receipt,'initial-quarantine-review-changed')
            q=area/intent['area'];nodes=intent['preview']['nodes']
            for i,node in enumerate(nodes):
                self.base(operation);states=self._states(operation,intent)
                if node['snapshot']['kind']!='file' or states[i]=='retained':continue
                marker=q/('move-'+str(i)+'.json');raw=canonical_bytes(node)
                if f.exists(marker):require(f.read(marker)==raw,'initial-quarantine-progress-changed')
                else:f.create(marker,raw)
                checkpoint('quarantine-before-move');self.base(operation);self._states(operation,intent)
                parent=(h.root/node['path']).parent
                parent_id=intent['preview']['home'] if parent==h.root else next(n['snapshot']['identity'] for n in nodes if h.root/n['path']==parent)
                if h.os_name!='windows':parent_id=parent_id[:2]
                move(f,h.root/node['path'],q/str(i),node['snapshot'],parent_identities={q:intent['area_identity'],parent:parent_id});checkpoint('quarantine-after-move')
            for i in reversed(range(len(nodes))):
                node=nodes[i];self.base(operation);states=self._states(operation,intent)
                if node['snapshot']['kind']!='directory' or states[i]=='removed':continue
                marker=q/('remove-'+str(i)+'.json');raw=canonical_bytes(node)
                if f.exists(marker):require(f.read(marker)==raw,'initial-quarantine-progress-changed')
                else:f.create(marker,raw)
                checkpoint('quarantine-before-rmdir');self.base(operation);self._states(operation,intent)
                remove_empty(f,h.root/node['path'],node['snapshot']);checkpoint('quarantine-after-rmdir')
            self.base(operation);require(all(s!='live' for s in self._states(operation,intent)),'initial-quarantine-incomplete')
            checkpoint('quarantine-before-complete');self.base(operation)
            require(all(s!='live' for s in self._states(operation,intent)),'initial-quarantine-incomplete')
            # A previously completed rename/rmdir may have failed its durability
            # acknowledgement. Sync the surviving parents again before completion.
            for parent in (q,area,h.root):f.sync_directory(parent)
            require(all(s!='live' for s in self._states(operation,intent)),'initial-quarantine-incomplete')
            raw=f.read(area/'quarantine-intent.json',4*1024*1024)
            done=dict(version=1,operation=operation,receipt=receipt,successor=intent['successor'],
                intent_sha256=hashlib.sha256(raw).hexdigest(),state='quarantined')
            f.create(area/'quarantine-complete.json',canonical_bytes(done));checkpoint('quarantine-completed');return done
    def claim(self,*,operation,receipt):
        h=self.home;f=self.f
        with f.exclusion(h.root/'management.lock'):
            result=completed(h,operation);require(result['receipt']==receipt,'initial-quarantine-review-changed')
            successor=result['successor'];head=initial_head(h,self.trust,self.config,self.anchor)
            if head==operation:retry_claim(h,self.trust,self.config,self.anchor,previous=operation,operation=successor)
            elif head!=successor:
                cursor=operation;seen=set()
                while cursor!=head:
                    require(cursor not in seen and len(seen)<4096,'initial-attempt-chain-invalid');seen.add(cursor)
                    edge=decode_canonical(f.read(h.root/'operations'/cursor/'retried-by.json'))
                    require(edge['previous']==cursor and (cursor!=operation or edge['next']==successor),'initial-attempt-chain-invalid')
                    cursor=edge['next'];_token(cursor)
                return dict(operation=head,state='replacement-superseded')
            area=h.root/'operations'/successor
            return dict(operation=successor,state='replacement-started' if f.exists(area/'started.json') else 'replacement-claimed')
