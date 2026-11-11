"""Explicit signed-bootstrap repair of one already approved connection.

Normal launch/update guards are unchanged. The executing payload is authenticated
before entry and bound again to retained-home signed metadata. Preview/apply never
fetch; preparation is a separate explicit signed-target operation.
"""
from functools import cached_property
from pathlib import Path
from contextlib import contextmanager
import hashlib
from ..codec import canonical_bytes,decode_canonical,decode_envelope,ObjectRef,require
from ..records import application_registry,operation_closure,link
from ..graph import validate_closure,AuditBudget
from ..maps import map_get
from ..effects import PENDING
from ..connection import PROJECT_KEY,workspace_key
from ..project_setup import ProjectSetup,unpack
from ..backup_service import export_backup
from ..storage.sqlite import _token
from .package import descriptor


def digest(raw):return hashlib.sha256(raw).hexdigest()


class ConnectionRepair:
    def __init__(self,home,trust,slot,release,*,connection,git=None,authenticate=lambda:None,renewal=None):
        _token(connection);self.home=home;self.trust=trust;self.slot=slot;self.release=release
        self.connection=connection;self.setup=ProjectSetup(home,git);self.authenticate=authenticate;self.renewal=renewal
        self.files=home.files;self.registry=application_registry()

    @contextmanager
    def hold(self):
        with self.files.exclusion(self.home.root/'management.lock'):
            with self.files.exclusion(self.home.slots.root/'runtime.lock'):
                self.authenticate();self._trust()
                verified=self.home.slots.verify(self.release['target'])
                require(verified.manifest_sha256==self.slot.manifest_sha256,'connect-repair-code-target-mismatch')
                yield

    def _trust(self):
        from .reauthentication import effective
        effective(self.home,self.trust,operation=self.release['operation'],original=digest(canonical_bytes(self.release)),
                  download=self.release['download'],renewal=self.renewal)
        d=descriptor(self.release['download']['custom'],channel=self.release['channel'],
                     os_name=self.home.os_name,architecture=self.home.architecture)
        require(d['manifest_sha256']==self.slot.manifest_sha256 and d['release']==self.slot.release and
                d['sequence']==self.slot.sequence,'connect-repair-code-target-mismatch')

    def _chain(self,store,service,admission=None):
        """Prove lifecycle lineage, not which process produced valid progress."""
        head=store.head(service.key(self.connection));ref=head;rows=[]
        for _ in range(258):
            obj=service._load(ref);rows.append(obj)
            require(obj.ref.kind=='lifecycle.connect-state' and obj.payload['operation']==self.connection,'connect-repair-chain-invalid')
            previous=link(obj,'previous')
            if previous is None:break
            ref=previous
        else:require(False,'connect-repair-chain-limit')
        rows.reverse();plan=service._load(link(rows[0],'plan'));count=len(plan.payload['manifest']['steps'])
        require(rows[0].payload['phase']=='ready' and rows[0].payload['next']==0,'connect-repair-chain-invalid')
        for i,obj in enumerate(rows):
            require(link(obj,'plan')==plan.ref,'connect-repair-plan-changed')
            if i:
                prev=rows[i-1];n=prev.payload['next']
                expected=('intent',n) if prev.payload['phase']=='ready' else ('completed' if n+1==count else 'ready',n+1)
                require(prev.payload['phase']!='completed' and (obj.payload['phase'],obj.payload['next'])==expected,'connect-repair-chain-invalid')
            suffix='-reserve' if i==0 else ('-intent-'+str(obj.payload['next']) if obj.payload['phase']=='intent' else '-done-'+str(obj.payload['next']-1))
            result=store.operation_result(self.connection+suffix);require(result is not None,'connect-repair-operation-missing')
            root=decode_envelope(result[1],store.load(result[1]))
            require(map_get(root.edges[0].ref,service.key(self.connection),store.load)==obj.ref,'connect-repair-operation-mismatch')
        if admission is not None:require(ObjectRef.parse(admission) in [row.ref for row in rows],'connect-repair-admission-not-ancestor')
        validate_closure([head],store.load,self.registry,operation_closure(self.registry))
        return head,rows[-1],plan

    def _observe(self,*,initial,admission=None):
        f=self.files
        for name in ('native-update.json','notice-app.pending'):
            require(not f.exists(self.home.root/name),'connect-repair-other-pending')
        raw,selection=self.home.slots.selection();selected=self.home.slots.verify(selection['selected'])
        require(self.slot.sequence>=selection['high_sequence'],'connect-repair-runtime-rollback')
        authority,store,service,journal,journal_raw=self.setup._resume_context(self.connection,readonly=True)
        try:
            head,state,plan=self._chain(store,service,admission)
            project=journal['plan']['project'];pointer=authority.pointer_value()
            require(not f.exists(authority.root/'pending.json'),'connect-repair-other-pending')
            require(store.head(PENDING)==(None if state.payload['phase']=='completed' else head),'connect-repair-pending-mismatch')
            require(link(plan,'binding')==store.head(PROJECT_KEY) and store.head('project:integration') is not None,'connect-repair-binding-changed')
            integration=service._load(store.head('project:integration'))
            require(link(integration,'binding')==store.head(PROJECT_KEY) and
                    link(integration,'workspace')==store.head(workspace_key(journal['plan']['workspace'])),'connect-repair-integration-changed')
            manifest=plan.payload['manifest'];changes=self.setup._changes(journal['plan'])
            require(len(changes)==len(manifest['steps']),'connect-repair-journal-plan-mismatch')
            for c,step in zip(changes,manifest['steps']):
                item=step['native']['items'][0]
                require((c['root'],c['path'],c['role'])==(step['root'],step['path'],step['role']),'connect-repair-journal-plan-mismatch')
                for key,body in (('pre',c['before']),('post',c['after'])):
                    m=item[key]
                    require((body is None and m is None) or (body is not None and m is not None and len(body)==m['size'] and digest(body)==m['sha256']),
                            'connect-repair-journal-body-mismatch')
                require(item['post']['mode']==c['mode'],'connect-repair-journal-mode-mismatch')
            with service.port.exclusion():
                states=[service.port.state(manifest,i) for i in range(len(changes))]
            if initial:
                require(state.payload['phase'] in ('ready','intent') and state.payload['next']==0 and all(x=='pre' for x in states),'connect-repair-requires-unapplied')
            else:
                n=state.payload['next']
                for i,x in enumerate(states):
                    require(x==('post' if i<n else 'pre') or (i==n and state.payload['phase']=='intent' and x in ('post','evacuated')),'connect-repair-files-changed')
            rows=[]
            for other in self.home.projects():
                a=self.home.authority(other);st=a.store(readonly=True)
                try:
                    require(not f.exists(a.root/'pending.json'),'connect-repair-other-pending')
                    if other!=project:require(st.head(PENDING) is None,'connect-repair-other-pending')
                    req=st.requirements()
                    require(set(req['read'])<=selected.read_capabilities and set(req['read'])<=self.slot.read_capabilities and
                            set(req['write'])<=selected.write_capabilities and set(req['write'])<=self.slot.write_capabilities,'connect-repair-capability-unavailable')
                    rows.append(dict(project=other,pointer=a.pointer_value(),root=st.root().ref.as_dict()))
                finally:st.close()
            return dict(version=1,connection=self.connection,home=str(self.home.root),selection=selection,
                        selection_sha256=digest(raw),target=self.release['target'],download=self.release['download'],
                        journal_sha256=digest(journal_raw),project=project,pointer=pointer,head=head.as_dict(),
                        plan=plan.ref.as_dict(),state=dict(state.payload),states=states,authorities=rows)
        finally:store.close()

    def preview(self):
        with self.hold():
            review=self._observe(initial=True)
            return dict(review=review,receipt=digest(canonical_bytes(review)),question='보존된 원본과 승인한 연결 내용을 확인하고 중단된 연결만 복구할까요?')

    def _invariants(self,before,now):
        for key in ('connection','home','selection','selection_sha256','target','download','journal_sha256','project','pointer','plan'):
            require(now[key]==before[key],'connect-repair-review-changed')
        a={x['project']:x for x in before['authorities']};b={x['project']:x for x in now['authorities']}
        require(a.keys()==b.keys(),'connect-repair-projects-changed')
        for project in a:
            require(a[project]['pointer']==b[project]['pointer'],'connect-repair-generation-changed')
            if project!=before['project']:require(a[project]==b[project],'connect-repair-other-authority-changed')

    def _snapshot(self,area,review):
        authority,store,service,journal,raw=self.setup._resume_context(self.connection,readonly=True)
        try:
            manifest=service._load(ObjectRef.parse(review['plan'])).payload['manifest'];copies=[]
            def copy(name,data,identity=None):
                self.files.create(area/name,data);require(self.files.read(area/name,16*1024*1024)==data,'connect-repair-snapshot-mismatch')
                copies.append(dict(name=name,sha256=digest(data),size=len(data),native_identity=identity))
            copy('c.json',raw)
            with service.port.exclusion():
                for n,(step,change) in enumerate(zip(manifest['steps'],self.setup._changes(journal['plan']))):
                    require(service.port.state(manifest,n)=='pre','connect-repair-files-changed');item=step['native']['items'][0]
                    staged=authority.root/'effects'/step['native']['application']/item['post_name']
                    body=self.files.read(staged,1024*1024)
                    require(body==change['after'],'connect-repair-snapshot-mismatch');copy('s'+str(n),body,item['post_native'])
                    if change['before'] is not None:
                        from ..adapters.git import read_file
                        body=read_file(Path(journal['plan']['root'] if step['root']=='project' else journal['plan']['locator_root'])/step['path'],1024*1024)
                        require(body==change['before'],'connect-repair-snapshot-mismatch');copy('o'+str(n),body,item['pre_native'])
            self.files.create(area/'snapshot.json',canonical_bytes(dict(version=1,files=copies,manifest=manifest)))
        finally:store.close()
        scratch=area/'a';self.files.create_directory(scratch)
        result=export_backup(authority,destination=area/'b.colvia-export',scratch=scratch,operation=area.name,
                             graph_budget=AuditBudget(2_000_000,8_000_000,64*1024**3),registry=self.registry)
        require(result['published'] and result['root']==next(x['root'] for x in review['authorities'] if x['project']==review['project']),'connect-repair-backup-unconfirmed')
        result['file_sha256']=self._backup_digest(area/'b.colvia-export',result['bytes'])
        self.files.create(area/'backup.json',canonical_bytes(result))

    def _backup_digest(self,path,size):
        require(type(size) is int and 0<size<=64*1024**3,'connect-repair-backup-size')
        hashed=hashlib.sha256();count=0
        with self.files.read_stream(path,size) as stream:
            while raw:=stream.read(1024*1024):
                count+=len(raw);require(count<=size,'connect-repair-backup-size');hashed.update(raw)
        require(count==size,'connect-repair-backup-size');return hashed.hexdigest()

    def _verify_snapshot(self,area):
        snapshot=decode_canonical(self.files.read(area/'snapshot.json',16*1024*1024))
        for item in snapshot['files']:
            require(item['name']=='c.json' or (item['name'][:1] in ('s','o') and item['name'][1:].isdigit()),'connect-repair-snapshot-name')
            raw=self.files.read(area/item['name'],16*1024*1024)
            require(len(raw)==item['size'] and digest(raw)==item['sha256'],'connect-repair-snapshot-mismatch')
        backup=decode_canonical(self.files.read(area/'backup.json'))
        require(self._backup_digest(area/'b.colvia-export',backup['bytes'])==backup['file_sha256'],'connect-repair-backup-mismatch')

    def apply(self,*,operation,receipt,resume=False,event=lambda _:None):
        _token(operation)
        with self.hold():
            area=self.home.root/'operations'/operation
            if resume:
                intent=decode_canonical(self.files.read(area/'connection-repair.json',16*1024*1024))
                require(intent['operation']==operation and intent['receipt']==receipt and digest(canonical_bytes(intent['review']))==receipt,'connect-repair-receipt-changed')
                review=intent['review'];self._verify_snapshot(area)
                now=self._observe(initial=False,admission=review['head']);self._invariants(review,now)
            else:
                review=self._observe(initial=True);require(digest(canonical_bytes(review))==receipt,'connect-repair-review-changed')
                self.files.create_directory(area)
                self.files.create(area/'connection-repair.json',canonical_bytes(dict(version=1,operation=operation,receipt=receipt,review=review)))
                self._snapshot(area,review)
                require(self._observe(initial=True)==review,'connect-repair-review-changed')
                self.files.create(area/'prepared.json',canonical_bytes(dict(version=1,receipt=receipt)))
            require(decode_canonical(self.files.read(area/'prepared.json'))==dict(version=1,receipt=receipt),'connect-repair-not-prepared')
            self._verify_snapshot(area);event('prepared')
            # Authority provenance is the only progress source. An interrupted
            # native effect is inspected by the existing advance protocol.
            for _ in range(129):
                self._trust();now=self._observe(initial=False,admission=review['head']);self._invariants(review,now)
                if now['state']['phase']=='completed':break
                def check(phase):
                    self._trust()
                    require(digest(self.home.slots.selection()[0])==review['selection_sha256'],'connect-repair-selection-changed')
                    a=self.home.authority(review['project']);require(a.pointer_value()==review['pointer'] and not self.files.exists(a.root/'pending.json'),'connect-repair-generation-changed')
                    event(phase)
                self.setup._resume_locked(self.connection,event=check)
            else:require(False,'connect-repair-step-limit')
            require(all(x=='post' for x in now['states']),'connect-repair-post-unconfirmed')
            self._invariants(review,now);self.authenticate();self._trust()
            completed=canonical_bytes(dict(version=1,receipt=receipt,connection=self.connection,head=now['head'],target=review['target']))
            if self.files.exists(area/'completed.json'):require(self.files.read(area/'completed.json')==completed,'connect-repair-completion-changed')
            else:self.files.create(area/'completed.json',completed)
            return dict(state='connected',runtime_changed=False,normal_update_required=True,target=review['target'],records_preserved=True)


class _RepairGit:
    """Resolve the configured Git only when repair must inspect a Git root."""
    def __init__(self, home):
        self.home = home

    @cached_property
    def git(self):
        from ..managed_entry import configured_git
        return configured_git(self.home)

    def topology(self, root):
        require(self.git is not None, 'git-prerequisite-required')
        return self.git.topology(root)


def bootstrap_connection_repair(root,stage,digest_value,*,connection,release_operation,operation=None,receipt=None,resume=False,prepare=False,renewal=None):
    from ..management import ManagerHome
    from ..managed_entry import current_platform,process_runtime
    from ..storage.files import platform_files
    from ..manager_entry import update_configuration
    from .slots import verify_payload
    from .installation import configuration
    from .trust import Trust
    from .release import ReleaseUpdate
    from .fetch import https_fetcher
    from .initial_home import initial_head
    files=platform_files();os_name,architecture=current_platform();root=Path(root);stage=Path(stage)
    require(root.is_absolute() and stage.is_absolute(),'installation-absolute-path-required')
    require(not (prepare and (operation is not None or receipt is not None or resume or renewal is not None)) and (not resume or receipt is not None),'installation-repair-mode-conflict')
    def authenticate():
        slot=verify_payload(stage,'bootstrap',digest_value,os_name=os_name,architecture=architecture,files=files)
        manifest=decode_canonical(files.read(stage/'manifest.json',4*1024*1024))
        require(process_runtime()==(slot.python,manifest['python_version'],manifest['sqlite_version']),'dedicated-runtime-mismatch')
        return slot
    slot=authenticate();home=ManagerHome(root,os_name=os_name,architecture=architecture,files=files)
    config=configuration(files,stage);own=update_configuration(home)
    require(all(config[k]==own[k] for k in ('channel','metadata_url','target_url','target')),'installation-channel-changed')
    class Offline:
        def fetch(self,*a,**kw):raise RuntimeError('connection-repair-network-forbidden')
    fetcher=https_fetcher(metadata_url=own['metadata_url'],target_url=own['target_url']) if prepare else Offline()
    try:
        trust=Trust(home.root/'trust',metadata_url=own['metadata_url'],target_url=own['target_url'],fetcher=fetcher,files=files)
        if files.exists(home.root/'initial-install.json'):
            first=initial_head(home,trust,config,files.read(stage/config['anchor'],512*1024))
            complete=decode_canonical(files.read(home.root/'operations'/first/'completed.json'))
            require(complete['version']==1 and complete['selection']['selected'] is not None,'connect-repair-initial-install-incomplete')
        release=ReleaseUpdate(home,trust,channel=own['channel'])
        if prepare:release.prepare(operation=release_operation,target=own['target'])
        plan,_=release._read(release_operation)
        service=ConnectionRepair(home,trust,slot,plan,connection=connection,git=_RepairGit(home),
                                 authenticate=authenticate,renewal=renewal)
        if receipt is None:
            require(operation is None and not resume,'connect-repair-operation-without-receipt')
            return service.preview()
        require(operation is not None and not prepare,'connect-repair-operation-required')
        return service.apply(operation=operation,receipt=receipt,resume=resume)
    finally:
        if hasattr(fetcher,'close'):fetcher.close()
