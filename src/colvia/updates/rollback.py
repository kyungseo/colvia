"""Restore authenticated originals before runtime selection, never a downgrade.

No metadata refresh, trust reset, project/settings write, or OS registration.
Lock order matches forward activation: management, runtime, then file effects.
"""
from contextlib import contextmanager
import hashlib,uuid
from ..codec import canonical_bytes,decode_canonical,require
from .native_entry import NativeEntryUpdate
from .notice_app import MacNoticeFiles


def digest(raw):return hashlib.sha256(raw).hexdigest()

class ReleaseRollback:
    def __init__(self,release):self.release=release;self.home=release.home;self.files=self.home.files
    @contextmanager
    def locked(self):
        with self.files.exclusion(self.home.root/'management.lock'):
            with self.files.exclusion(self.home.slots.root/'runtime.lock'):yield
    def original(self,operation,receipt):
        plan,expected=self.release._read(operation)
        require(receipt==expected,'release-review-changed')
        require(self.home.slots.selection()[0]==canonical_bytes(plan['before']),'rollback-runtime-selection-changed')
        self.home.slots.verify(plan['before']['selected'])
        require(not plan['unchanged'] and not plan.get('replacement',False),'rollback-original-runtime-required')
        return plan
    def components(self,plan):
        h=self.home;old=plan['before']['selected'];operation=plan['operation']
        previous=NativeEntryUpdate(h,old,operation);current=NativeEntryUpdate(h,plan['target'],operation)
        oldraw=previous.candidate();newraw=current.candidate();values=[]
        if oldraw is not None and newraw is not None:
            mode='100644' if h.os_name=='windows' else '100755'
            def rows(raw):return [dict(path=n,kind='regular',mode=mode,size=len(raw),sha256=digest(raw)) for n in previous.names()]
            values.append(dict(name='entry',forward=current,description='entry.json',before=previous.description(oldraw),after=current.description(newraw),
                old=rows(oldraw),new=rows(newraw),bodies={n:oldraw for n in previous.names()}))
        previous=MacNoticeFiles(h,old,operation);current=MacNoticeFiles(h,plan['target'],operation)
        oldapp=previous.candidate();newapp=current.candidate()
        if newapp is not None:
            oldrows,oldbodies=oldapp if oldapp is not None else ([],{})
            values.append(dict(name='app',forward=current,description='receiver.json',before=None if oldapp is None else previous.record(oldrows),
                after=current.record(newapp[0]),old=oldrows,new=newapp[0],bodies=oldbodies))
        return values
    def bind(self,plan,*,saved=None,completed=False):
        result=[];components={v['name']:v for v in self.components(plan)}
        names=[row['name'] for row in saved] if saved is not None else [name for name,c in components.items() if self.files.exists(c['forward'].pending)]
        require(names and len(names)==len(set(names)) and set(names)<=set(components),'rollback-files-unavailable')
        for name in names:
            c=components[name];forward=c['forward']
            if saved is None:
                token=forward.pending_token();raw=self.files.read(forward.area/'prepared.json',4*1024*1024)
                binding=dict(name=name,area=forward.area.name,token=token.decode(),prepared_sha256=digest(raw))
            else:
                binding=next(row for row in saved if row['name']==name)
                token=binding['token'].encode();tokenvalue=decode_canonical(token)
                require(tokenvalue['operation']==plan['operation'] and tokenvalue['target']==plan['target'] and tokenvalue['area']==binding['area'],
                    'rollback-forward-binding-changed')
                # Live pending uses strict area-name validation; completed cleanup
                # uses the already receipt-bound retained area basename.
                if self.files.exists(forward.pending):
                    require(self.files.read(forward.pending)==token,'rollback-pending-changed');forward.pending_token()
                else:
                    require(completed,'rollback-pending-missing')
                    from ..storage.sqlite import _token
                    _token(binding['area']);forward.area=self.home.root/'operations'/binding['area'];self.files.private_directory(forward.area)
                raw=self.files.read(forward.area/'prepared.json',4*1024*1024)
                require(digest(raw)==binding['prepared_sha256'],'rollback-forward-preparation-changed')
            prepared=decode_canonical(raw);manifest=prepared['effects']
            before=None if prepared['before'] is None else prepared['before'].encode()
            require(prepared['version']==1 and prepared['target']==plan['target'] and before==c['before'] and prepared['after'].encode()==c['after'],
                    'rollback-description-not-authenticated')
            old={row['path']:row for row in c['old']}
            # Each producer owns the journal order. Windows native aliases
            # are product then manager, which differs from lexical order.
            expected=[dict(path=row['path'],pre=old.get(row['path']),post=row) for row in c['new']]
            require([{key:i[key] for key in ('path','pre','post')} for i in manifest['items']]==expected,'rollback-effects-not-authenticated')
            actual=self.files.read(self.home.root/c['description']) if self.files.exists(self.home.root/c['description']) else None
            require(actual in (c['before'],c['after']),'rollback-description-changed')
            c.update(binding=binding,manifest=manifest);result.append(c)
        # A foreign pending component must not disappear behind the intent.
        for name,path in (('entry','native-update.json'),('app','notice-app.pending')):
            require(name in names or not self.files.exists(self.home.root/path),'rollback-other-pending')
        return result
    def proposal(self,plan,receipt,components):
        return dict(version=1,operation=plan['operation'],receipt=receipt,selection_sha256=digest(canonical_bytes(plan['before'])),
                    components=[c['binding'] for c in components])
    def check_forward_states(self,components):
        for c in components:
            port=c['forward'].port(self.home.root/'bin',c['forward'].area)
            with port.exclusion(create=False):
                for i in range(len(c['manifest']['items'])):
                    require(not port.inspect_state(c['manifest'],i)['retained_original_modified'],'rollback-original-changed')

    def preview(self,*,operation,receipt):
        with self.locked():
            plan=self.original(operation,receipt);path=self.home.root/'operations'/operation/'rollback.json'
            if self.files.exists(path):raw=self.files.read(path,4*1024*1024)
            else:
                components=self.bind(plan)
                self.check_forward_states(components)
                raw=canonical_bytes(self.proposal(plan,receipt,components))
            return dict(state='rollback-review',operation=operation,rollback_receipt=digest(raw),
                question='중단된 갱신의 파일을 이전 실행기와 일치하도록 복구할까요? 기록과 설정은 그대로 유지합니다.')
    def apply(self,*,operation,receipt,rollback_receipt,checkpoint=lambda _:None):
        with self.locked():
            plan=self.original(operation,receipt);area=self.home.root/'operations'/operation
            intent=area/'rollback.json';complete=area/'rollback-completed.json';prepared_path=area/'rollback-prepared.json'
            if self.files.exists(intent):
                raw=self.files.read(intent,4*1024*1024);require(digest(raw)==rollback_receipt,'rollback-review-changed')
                proposal=decode_canonical(raw);components=self.bind(plan,saved=proposal['components'],completed=self.files.exists(complete))
                require(proposal==self.proposal(plan,receipt,components),'rollback-intent-changed')
            else:
                components=self.bind(plan);raw=canonical_bytes(self.proposal(plan,receipt,components))
                require(digest(raw)==rollback_receipt,'rollback-review-changed')
                self.check_forward_states(components)
                self.files.create(intent,raw);checkpoint('rollback-intent')
            if self.files.exists(prepared_path):prepared=decode_canonical(self.files.read(prepared_path,4*1024*1024))
            else:
                reverse_area=area/('reverse-'+uuid.uuid4().hex);self.files.create_directory(reverse_area);records=[]
                for c in components:
                    forward=c['forward'];port=forward.port(self.home.root/'bin',forward.area)
                    sub=reverse_area/c['name'];self.files.create_directory(sub)
                    reverse=forward.port(self.home.root/'bin',sub)
                    with port.exclusion(create=False),reverse.exclusion():
                        states=[];changes=[]
                        for i,item in enumerate(c['manifest']['items']):
                            observed=port.inspect_state(c['manifest'],i);require(not observed['retained_original_modified'],'rollback-original-changed')
                            state=observed['state'];states.append(state)
                            if state!='pre':changes.append(dict(path=item['path'],pre=item['post'] if state=='post' else None,post=item['pre']))
                        manifest=reverse.prepare('restore',changes,lambda path:iter((c['bodies'][path],)))
                        # Staging must not let a foreign same-byte replacement
                        # become a newly authorized original.
                        for i,state in enumerate(states):
                            observed=port.inspect_state(c['manifest'],i)
                            require(observed['state']==state and not observed['retained_original_modified'],'rollback-forward-state-changed')
                        records.append(dict(name=c['name'],states=states,effects=manifest))
                prepared=dict(version=1,intent_sha256=digest(raw),area=reverse_area.name,components=records)
                self.files.create(prepared_path,canonical_bytes(prepared));checkpoint('rollback-prepared')
            require(prepared['version']==1 and prepared['intent_sha256']==digest(raw) and
                    [v['name'] for v in prepared['components']]==[c['name'] for c in components],'rollback-preparation-changed')
            name=prepared['area'];require(type(name) is str and name.startswith('reverse-') and len(name)==40 and all(c in '0123456789abcdef' for c in name[8:]),'rollback-area-invalid')
            for c,record in zip(components,prepared['components']):
                forward=c['forward'];port=forward.port(self.home.root/'bin',forward.area)
                reverse=forward.port(self.home.root/'bin',area/name/c['name']);manifest=record['effects'];states=record['states']
                require(len(states)==len(c['manifest']['items']) and all(s in ('pre','post','evacuated') for s in states),'rollback-preparation-changed')
                expected=[dict(path=i['path'],pre=i['post'] if s=='post' else None,post=i['pre']) for s,i in zip(states,c['manifest']['items']) if s!='pre']
                require([{key:i[key] for key in ('path','pre','post')} for i in manifest['items']]==expected,'rollback-preparation-changed')
                with port.exclusion(create=False),reverse.exclusion(create=False):
                    def guard():
                        require(self.home.slots.selection()[0]==canonical_bytes(plan['before']),'rollback-runtime-selection-changed')
                        for i,state in enumerate(states):
                            if state=='pre':require(port.inspect_state(c['manifest'],i)['state']=='pre','rollback-untouched-file-changed')
                            else:require(port.retained_original_matches(c['manifest'],i),'rollback-original-changed')
                    guard()
                    for i in range(len(manifest['items'])):
                        require(not reverse.inspect_state(manifest,i)['retained_original_modified'],'rollback-displaced-update-changed')
                        reverse.apply_one(manifest,i,before_effect=guard,event=lambda phase:checkpoint('rollback-'+phase));reverse.sync(manifest,i)
                    guard()
                path=self.home.root/c['description'];actual=self.files.read(path) if self.files.exists(path) else None
                require(actual in (c['before'],c['after']),'rollback-description-changed')
                if actual!=c['before']:
                    if c['before'] is None:self.files.remove(path,actual)
                    else:self.files.replace(path,c['before'],actual)
                checkpoint('rollback-described')
            # Full old inventories, unchanged selection and exact descriptions.
            old=plan['before']['selected'];native=NativeEntryUpdate(self.home,old,operation);rawnative=native.candidate()
            if rawnative is not None:
                require(self.files.read(self.home.root/'entry.json')==native.description(rawnative) and
                    all(self.files.read(self.home.root/'bin'/n,64*1024*1024)==rawnative for n in native.names()),'rollback-old-entry-changed')
            app=MacNoticeFiles(self.home,old,operation);candidate=app.candidate()
            if self.home.os_name=='macos':app.check_files(candidate[0] if candidate is not None else [])
            require(self.home.slots.selection()[0]==canonical_bytes(plan['before']),'rollback-runtime-selection-changed')
            done=canonical_bytes(dict(version=1,intent_sha256=digest(raw)))
            if self.files.exists(complete):require(self.files.read(complete)==done,'rollback-completion-changed')
            else:self.files.create(complete,done)
            checkpoint('rollback-completed')
            for c in components:
                pending=c['forward'].pending
                if self.files.exists(pending):self.files.remove(pending,c['binding']['token'].encode())
            return dict(state='rolled-back',records_preserved=True,settings_preserved=True,runtime_selection_preserved=True)
