"""Generation activation with an irreversible old-store fence and small pointer.

No existing database pathname is replaced, and no old generation is deleted.
This low-level protocol is reused by later restore/update commands; it does not
perform installation, old-trial migration, locator rebinding or key management.
"""
from pathlib import Path
from typing import Callable

from ..codec import ObjectRef, RecordError, canonical_bytes, decode_canonical, require
from .sqlite import GenerationStore, _token
from .files import platform_files


class Authority:
    def __init__(self,root:Path,*,project:str,files=None,reader_capabilities=None,writer_capabilities=None):
        self.root=Path(root); self.project=project; _token(project)
        self.capabilities=dict(reader_capabilities=reader_capabilities,writer_capabilities=writer_capabilities)
        require(self.root.is_absolute() and self.root.is_dir() and not self.root.is_symlink(),
                'invalid-authority-root')
        self.files=files or platform_files()
        self.files.private_directory(self.root)
        self.pointer=self.root/'active.json'
        self.pointer_value()

    def pointer_value(self):
        value=decode_canonical(self.files.read(self.pointer))
        require(type(value) is dict and set(value)=={'version','project','instance','generation'} and
                type(value['version']) is int and value['version']==1 and value['project']==self.project,
                'invalid-active-pointer')
        for field in ('project','instance','generation'): _token(value[field])
        return value

    @classmethod
    def create(cls,root:Path,*,project:str,instance:str,generation:str,files=None,reader_capabilities=None,writer_capabilities=None):
        for value in (project,instance,generation): _token(value)
        root=Path(root); files=files or platform_files()
        require(root.is_absolute(),'absolute-authority-path-required')
        for parent in root.parents: require(not parent.is_symlink(),'symlink-authority-path')
        files.create_directory(root)
        files.create_directory(root/'stores'); files.create_directory(root/'lifecycle')
        location=root/'stores'/generation; files.create_directory(location)
        store=GenerationStore.create(location/'state.sqlite3',project=project,instance=instance,
                                      generation=generation,active_check=lambda:None,reader_capabilities=reader_capabilities,writer_capabilities=writer_capabilities)
        store.close()
        files.sync_directory(location); files.sync_directory(root/'stores')
        files.create(root/'lifecycle.lock',b'')
        files.create(root/'active.json',canonical_bytes(dict(version=1,project=project,instance=instance,generation=generation)))
        files.sync_directory(root.parent)
        return cls(root,project=project,files=files,reader_capabilities=reader_capabilities,writer_capabilities=writer_capabilities)

    def store(self,*,readonly=False):
        expected=self.pointer_value()
        def active():
            require(self.pointer_value()==expected,'active-generation-changed')
        return GenerationStore(self.root/'stores'/expected['generation']/'state.sqlite3',project=self.project,
            instance=expected['instance'],generation=expected['generation'],readonly=readonly,active_check=active,
            write_check=lambda:require(not self.files.exists(self.root/'pending.json'),'activation-pending'),**self.capabilities)

    def prepare_empty(self,generation:str,*,instance=None):
        """Allocate a new candidate, never reuse a path or select it as active."""
        _token(generation); current=self.pointer_value()
        instance=current['instance'] if instance is None else instance;_token(instance)
        require(generation!=current['generation'],'generation-already-active')
        active=self.store(readonly=True)
        try:needs_rebind=instance!=current['instance'] or active.needs_rebind()
        finally:active.close()
        require(self.pointer_value()==current,'active-generation-changed')
        path=self.root/'stores'/generation; self.files.create_directory(path)
        store=GenerationStore.create(path/'state.sqlite3',project=self.project,instance=instance,needs_rebind=needs_rebind,
            generation=generation,active_check=lambda:require(self.pointer_value()==current,'active-generation-changed'),**self.capabilities)
        self.files.sync_directory(path); self.files.sync_directory(path.parent)
        return store

    def import_candidate(self, generation, snapshot, *, operation, cancelled=lambda:False,
                         checkpoint=lambda _:None, instance=None):
        """Restore only into a newly allocated, unpublished generation."""
        from .restore import fill_candidate
        _token(operation)
        require(snapshot.complete and snapshot.writable, 'import-not-writable')
        require(snapshot.header['project']==self.project, 'import-project-mismatch')
        expected=self.pointer_value()
        candidate=self.prepare_empty(generation,instance=instance)
        try:
            def unselected():
                require(self.pointer_value()==expected and generation!=expected['generation'],
                        'restore-candidate-became-active')
            return fill_candidate(candidate,snapshot,operation=operation,
                                  unselected=unselected,cancelled=cancelled,checkpoint=checkpoint)
        finally: candidate.close()

    def _plan(self,operation):
        _token(operation)
        raw=self.files.read(self.root/'lifecycle'/(operation+'.json'))
        p=decode_canonical(raw)
        require(type(p) is dict and set(p)=={'version','kind','operation','old','new','old_root','new_root'} and
                type(p['version']) is int and p['version']==1 and p['operation']==operation,'invalid-activation-plan')
        for field in ('old','new'):
            pointer=p[field]
            require(type(pointer) is dict and set(pointer)=={'version','project','instance','generation'} and
                    type(pointer['version']) is int and pointer['version']==1 and pointer['project']==self.project,
                    'invalid-activation-plan')
            for key in ('project','instance','generation'): _token(pointer[key])
        require(p['kind'] in ('same-state','instance-restore') and p['old']['generation']!=p['new']['generation'],
                'invalid-generation-transition')
        require((p['old']['instance']==p['new']['instance'])==(p['kind']=='same-state'),'invalid-instance-transition')
        ObjectRef.parse(p['old_root']); ObjectRef.parse(p['new_root'])
        if p['kind']=='same-state':require(p['old_root']==p['new_root'],'generation-state-not-preserved')
        return p

    def _open_recorded(self,pointer,plan,*,readonly,retired=False):
        def active():
            require(self.pointer_value() in (plan['old'],plan['new']),'activation-pointer-diverged')
        return GenerationStore(self.root/'stores'/pointer['generation']/'state.sqlite3',project=self.project,
            instance=pointer['instance'],generation=pointer['generation'],readonly=readonly,active_check=active,
            _retirement_operation=plan['operation'] if retired else None,**self.capabilities)

    def activate(self,operation:str,*,target_generation:str,expected_root:ObjectRef,
                 validate_effects:Callable,validate_target:Callable,
                 checkpoint:Callable[[str],None]=lambda _:None):
        """Caller has already authorized this exact transition, not an arbitrary latest candidate."""
        return self._activate(operation,target_generation=target_generation,expected_root=expected_root,
            target_root=expected_root,instance=None,kind='same-state',validate_effects=validate_effects,
            validate_target=validate_target,checkpoint=checkpoint)

    def activate_restore(self,operation,*,target_generation,instance,expected_root,target_root,
                         validate_effects,validate_target,checkpoint=lambda _:None):
        _token(instance)
        require(instance!=self.pointer_value()['instance'],'restore-instance-must-be-new')
        return self._activate(operation,target_generation=target_generation,expected_root=expected_root,
            target_root=target_root,instance=instance,kind='instance-restore',validate_effects=validate_effects,
            validate_target=validate_target,checkpoint=checkpoint)

    def _activate(self,operation,*,target_generation,expected_root,target_root,instance,kind,
                  validate_effects,validate_target,checkpoint):
        _token(operation); _token(target_generation)
        with self.files.exclusion(self.root/'lifecycle.lock'):
            require(not self.files.exists(self.root/'pending.json'),'activation-already-pending')
            old=self.pointer_value(); new=dict(old,generation=target_generation,instance=old['instance'] if instance is None else instance)
            require(old!=new,'generation-already-active')
            tentative=dict(operation=operation,old=old,new=new)
            target=self._open_recorded(new,tentative,readonly=True)
            try:
                require(target.root().ref==target_root,'generation-state-not-preserved')
                if kind=='instance-restore':
                    require(target.needs_rebind(),'restore-rebind-marker-required')
                    origin=target.db.execute('SELECT root,complete FROM restore_origin').fetchone()
                    require(origin is not None and origin['complete']==1 and origin['root']==target_root.sha256,'restore-origin-unavailable')
                    require(target.head('effect:pending') is None,'imported-effect-inspection-only')
                require(target.lifecycle_state()=={'fence':None,'quiescent':None},'target-not-ready')
                validate_target(target)
            finally: target.close()
            source=self.store()
            try:
                require(source.root().ref==expected_root,'lifecycle-root-conflict')
                if kind=='same-state':
                    candidate=self._open_recorded(new,tentative,readonly=True)
                    try:require(candidate.needs_rebind()==source.needs_rebind(),'generation-rebind-state-not-preserved')
                    finally:candidate.close()
                from ..maps import map_get
                def checked_effects(observed):
                    require(map_get(observed.heads,'effect:pending',source.load) is None,'external-effect-pending')
                    validate_effects(observed)
                checked_effects(source.root())
                plan=dict(version=1,kind=kind,operation=operation,old=old,new=new,
                          old_root=expected_root.as_dict(),new_root=target_root.as_dict())
                self.files.create(self.root/'lifecycle'/(operation+'.json'),canonical_bytes(plan))
                self.files.create(self.root/'pending.json',canonical_bytes(dict(version=1,operation=operation)))
                checkpoint('intent')
                self._seal_target(plan)
                checkpoint('target-ready')
                try:
                    source.quiesce(operation,expected_root,checked_effects)
                except RecordError as exc:
                    if exc.code in ('lifecycle-root-conflict','external-effect-pending','effects-unresolved'):
                        self._abort_prefence(plan)
                    raise
                checkpoint('quiescent')
                source.retire(operation,expected_root)
                checkpoint('fenced')
            finally: source.close()
            return self._finish(plan,validate_target,checkpoint)

    def _abort_prefence(self,plan):
        """Only called under the existing lifecycle exclusion after known refusal."""
        require(self.pointer_value()==plan['old'],'activation-pointer-diverged')
        expected=canonical_bytes(dict(version=1,operation=plan['operation']))
        require(self.files.read(self.root/'pending.json')==expected,'activation-operation-mismatch')
        source=self._open_recorded(plan['old'],plan,readonly=False)
        target=self._open_recorded(plan['new'],plan,readonly=False)
        try:
            state=source.lifecycle_state()
            require(state['fence'] is None and state['quiescent'] in (None,plan['operation']),
                    'activation-source-diverged')
            target_state=target.lifecycle_state()
            require(target_state['fence'] is None and target_state['quiescent'] in (None,plan['operation']),
                    'activation-target-diverged')
            if target_state['quiescent'] is not None:
                target.cancel_quiescence(plan['operation'],ObjectRef.parse(plan['new_root']))
            if state['quiescent'] is not None:
                source.cancel_quiescence(plan['operation'],ObjectRef.parse(plan['old_root']))
            self.files.remove(self.root/'pending.json',expected)
        finally:source.close();target.close()

    def _seal_target(self,plan):
        if plan['kind']=='same-state':require(plan['old_root']==plan['new_root'],'generation-state-not-preserved')
        target=self._open_recorded(plan['new'],plan,readonly=False)
        try:
            with target._transaction(write=True,lifecycle=True):
                root=target._root();row=target.db.execute('SELECT * FROM generation WHERE singleton=1').fetchone()
                require(root.ref==ObjectRef.parse(plan['new_root']) and row['fence'] is None and
                        row['quiescent'] in (None,plan['operation']),'activation-target-diverged')
                if plan['kind']=='instance-restore':
                    from ..maps import map_get
                    origin=target.db.execute('SELECT root,complete FROM restore_origin').fetchone()
                    require(row['needs_rebind']==1 and origin is not None and origin['complete']==1 and
                            origin['root']==root.ref.sha256,'restore-origin-unavailable')
                    require(map_get(root.heads,'effect:pending',target._load) is None,'imported-effect-inspection-only')
                changed=target.db.execute('UPDATE generation SET quiescent=? WHERE singleton=1',(plan['operation'],))
                require(changed.rowcount==1,'target-not-ready')
        finally:target.close()

    def _finish(self,plan,validate_target,checkpoint):
        old=self._open_recorded(plan['old'],plan,readonly=True,retired=True)
        target=self._open_recorded(plan['new'],plan,readonly=True)
        try:
            require(old.root().ref==ObjectRef.parse(plan['old_root']) and
                    old.lifecycle_state()=={'fence':plan['operation'],'quiescent':plan['operation']},
                    'activation-source-diverged')
            require(target.root().ref==ObjectRef.parse(plan['new_root']) and
                    target.lifecycle_state() in ({'fence':None,'quiescent':plan['operation']},
                        {'fence':None,'quiescent':None} if self.pointer_value()==plan['new'] else {}),
                    'activation-target-diverged')
            validate_target(target)
        finally: old.close(); target.close()
        current=self.pointer_value()
        if current==plan['old']:
            self.files.replace(self.pointer,canonical_bytes(plan['new']),canonical_bytes(plan['old']))
        else: require(current==plan['new'],'activation-pointer-diverged')
        checkpoint('pointer')
        active=self.store(readonly=True)
        try: require(active.root().ref==ObjectRef.parse(plan['new_root']),'activation-target-diverged')
        finally: active.close()
        checkpoint('confirmed')
        target=self._open_recorded(plan['new'],plan,readonly=False)
        try:
            if target.lifecycle_state()['quiescent'] is not None:
                target.cancel_quiescence(plan['operation'],ObjectRef.parse(plan['new_root']))
        finally: target.close()
        checkpoint('target-released')
        self.files.remove(self.root/'pending.json',canonical_bytes(dict(version=1,operation=plan['operation'])))
        checkpoint('complete')
        return ObjectRef.parse(plan['new_root'])

    def historical_store(self,operation):
        """Explicit retired history reader, also after later active generations."""
        plan=self._plan(operation);old=plan['old']
        store=GenerationStore(self.root/'stores'/old['generation']/'state.sqlite3',project=self.project,
            instance=old['instance'],generation=old['generation'],readonly=True,
            active_check=lambda:self.pointer_value(),_retirement_operation=operation,**self.capabilities)
        try:
            require(store.lifecycle_state()['fence']==operation and store.root().ref==ObjectRef.parse(plan['old_root']),
                    'historical-generation-not-retired')
        except BaseException:store.close();raise
        return store

    def _recover_recorded_journals(self, plan):
        # Called only under lifecycle.lock, after validating the exact operation.
        for pointer in (plan['old'],plan['new']):
            try:
                store=self._open_recorded(pointer,plan,readonly=True,retired=pointer==plan['old'])
            except RecordError as exc:
                if exc.code!='recovery-required': raise
                GenerationStore.recover_journal(
                    self.root/'stores'/pointer['generation']/'state.sqlite3',project=self.project,
                    instance=pointer['instance'],generation=pointer['generation'],operation=plan['operation'],
                    active_check=lambda:require(self.pointer_value() in (plan['old'],plan['new']),
                                                'activation-pointer-diverged'))
                store=self._open_recorded(pointer,plan,readonly=True,retired=pointer==plan['old'])
            store.close()

    def recover(self,operation:str,*,complete:bool,validate_effects:Callable,validate_target:Callable):
        """Explicit recovery: never auto-unfence or select a candidate by timestamp."""
        with self.files.exclusion(self.root/'lifecycle.lock'):
            require(self.files.read(self.root/'pending.json')==canonical_bytes(dict(version=1,operation=operation)),
                    'activation-operation-mismatch')
            plan=self._plan(operation)
            self._recover_recorded_journals(plan)
            old=self._open_recorded(plan['old'],plan,readonly=True,retired=True)
            try:
                require(old.root().ref==ObjectRef.parse(plan['old_root']),'activation-source-diverged')
                state=old.lifecycle_state()
            finally: old.close()
            if state['fence'] is not None:
                require(complete,'retired-generation-cannot-resume')
                return self._finish(plan,validate_target,lambda _:None)
            require(self.pointer_value()==plan['old'],'unfenced-pointer-diverged')
            source=self.store()
            try:
                if not complete:
                    target=self._open_recorded(plan['new'],plan,readonly=False)
                    try:
                        if target.lifecycle_state()['quiescent'] is not None:
                            target.cancel_quiescence(operation,ObjectRef.parse(plan['new_root']))
                    finally: target.close()
                    if state['quiescent'] is not None:
                        source.cancel_quiescence(operation,ObjectRef.parse(plan['old_root']))
                    self.files.remove(self.root/'pending.json',canonical_bytes(dict(version=1,operation=operation)))
                    return source.root().ref
                self._seal_target(plan)
                if state['quiescent'] is None:
                    source.quiesce(operation,ObjectRef.parse(plan['old_root']),validate_effects)
                else:
                    require(state['quiescent']==operation,'lifecycle-operation-mismatch')
                    validate_effects(source.root())
                target=self._open_recorded(plan['new'],plan,readonly=True)
                try:
                    require(target.root().ref==ObjectRef.parse(plan['new_root']),'activation-target-diverged')
                    validate_target(target)
                finally: target.close()
                source.retire(operation,ObjectRef.parse(plan['old_root']))
            finally: source.close()
            return self._finish(plan,validate_target,lambda _:None)
