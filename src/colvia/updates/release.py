"""Signed-target preparation and explicit activation through the shared manager.

A download is not installation; preparation never changes runtime selection.
Activation reuses the exact signed target and backs up all registered authorities.
"""
from pathlib import Path
import hashlib,uuid
from ..codec import RecordError,canonical_bytes,decode_canonical,require
from ..storage.sqlite import _token
from .package import stage_archive,descriptor
from .slots import pointer
from .native_entry import NativeEntryUpdate
from .notice_app import MacNoticeFiles
from .reauthentication import forward_allowed,effective,renew

def inspect_release(home,operation):
    """Read release and activation evidence without fetching or changing state."""
    _token(operation);f=home.files;area=home.root/'operations'/operation
    f.private_directory(area)
    if not f.exists(area/'download-intent.json'):return home.inspect_update(operation)
    intent=decode_canonical(f.read(area/'download-intent.json'))
    result=dict(operation=operation,state='download-incomplete',prepared=False,automatic_retry=False)
    if not f.exists(area/'release.json'):return result
    raw=f.read(area/'release.json',4*1024*1024);plan=decode_canonical(raw)
    require(plan['operation']==operation and plan['channel']==intent['channel'] and
            plan['before']==intent['before'],'release-operation-mismatch')
    result.update(state='prepared',prepared=True,receipt=hashlib.sha256(raw).hexdigest(),target=plan['target'],activations=[])
    for child in sorted((home.root/'operations').iterdir(),key=lambda p:p.name):
        if child.name!=operation+'-activate' and not child.name.startswith(operation+'-resume-'):continue
        f.private_directory(child)
        if not f.exists(child/'intent.json'):continue
        value=decode_canonical(f.read(child/'intent.json'))
        require(value['operation']==child.name and value['target']==plan['target'],'release-child-operation-mismatch')
        result['activations'].append(dict(operation=child.name,**home.inspect_update(child.name)))
    if f.exists(area/'rollback.json'):
        rollback=decode_canonical(f.read(area/'rollback.json',4*1024*1024))
        own={row['name']:row['token'].encode() for row in rollback['components']}
        for name,path,key in (('entry','native-update.json','native_pending'),('app','notice-app.pending','app_pending')):
            token=f.read(home.root/path) if f.exists(home.root/path) else None
            result[key]=token is not None and token==own.get(name)
            if token is not None and token!=own.get(name):result['other_or_changed_pending']=True
        result['state']='rolled-back' if f.exists(area/'rollback-completed.json') and not result['native_pending'] and not result['app_pending'] else 'rollback-pending'
        result['forward_resume_allowed']=False
        return result
    result['selected']=home.slots.selection()[1]['selected']==plan['target']
    result['native_pending']=f.exists(home.root/'native-update.json')
    result['app_pending']=f.exists(home.root/'notice-app.pending')
    if result['selected'] and not result['native_pending'] and not result['app_pending']:result['state']='current' if plan['unchanged'] else 'updated'
    return result


class ReleaseUpdate:
    def __init__(self,home,trust,*,channel,replacement=False):
        self.home=home;self.trust=trust;_token(channel);self.channel=channel
        require(type(replacement) is bool,'runtime-repair-mode-invalid');self.replacement=replacement
    def _read(self,operation):
        _token(operation);area=self.home.root/'operations'/operation
        plan=decode_canonical(self.home.files.read(area/'release.json',4*1024*1024))
        require(plan['operation']==operation and plan['channel']==self.channel,'release-operation-mismatch')
        return plan,hashlib.sha256(canonical_bytes(plan)).hexdigest()
    def rollback_preview(self,*,operation,receipt):
        from .rollback import ReleaseRollback
        return ReleaseRollback(self).preview(operation=operation,receipt=receipt)
    def rollback(self,*,operation,receipt,rollback_receipt,checkpoint=lambda _:None):
        from .rollback import ReleaseRollback
        return ReleaseRollback(self).apply(operation=operation,receipt=receipt,rollback_receipt=rollback_receipt,checkpoint=checkpoint)

    def refresh(self,*,operation,receipt,renewal,cancelled=lambda:False):
        with self.home.files.exclusion(self.home.root/'management.lock'):
            plan,expected=self._read(operation);require(receipt==expected,'release-review-changed')
            return renew(self.home,self.trust,operation=operation,original=expected,download=plan['download'],
                         renewal=renewal,cancelled=cancelled)

    def prepare(self,*,operation,target,cancelled=lambda:False):
        _token(operation)
        with self.home.files.exclusion(self.home.root/'management.lock'):
            require(not self.home.files.exists(self.home.root/'native-update.json'),'native-entry-update-pending')
            require(not self.home.files.exists(self.home.root/'notice-app.pending'),'notice-app-update-pending')
            before,selection=self.home.slots.selection()
            if self.replacement:
                try:self.home.slots.verify(selection['selected'])
                except (RecordError,FileNotFoundError):pass
                else:raise RecordError('runtime-replacement-not-required')
            area=self.home.root/'operations'/operation;self.home.files.create_directory(area)
            self.home.files.create(area/'download-intent.json',canonical_bytes(dict(version=1,target=target,channel=self.channel,
                before=selection)))
            current=None
            def present(description):
                nonlocal current
                if self.replacement:return False
                info=descriptor(description.get('custom'),channel=self.channel,os_name=self.home.os_name,architecture=self.home.architecture)
                if info['manifest_sha256']!=selection['selected']['manifest_sha256']:return False
                current=self.home.slots.verify(selection['selected'])
                require((current.release,current.sequence)==(info['release'],info['sequence']),'release-descriptor-mismatch')
                return True
            download=self.trust.stage(target,destination=area/'release.zip',cancelled=cancelled,already_present=present)
            if download['staged'] is None:
                require(current is not None,'release-current-unverified');verified=current
            else:
                verified=stage_archive(area/'release.zip',root=self.home.slots.root,slot=operation,target=download,channel=self.channel,
                    os_name=self.home.os_name,architecture=self.home.architecture,files=self.home.files,cancelled=cancelled)

            require(self.home.slots.selection()[0]==before,'runtime-selection-changed')
            unchanged=not self.replacement and verified.manifest_sha256==selection['selected']['manifest_sha256']
            if unchanged:self.home.slots.verify(selection['selected'])
            plan=dict(version=1,operation=operation,channel=self.channel,before=selection,
                target=selection['selected'] if unchanged else pointer(verified),download=download,unchanged=unchanged,replacement=self.replacement)
            self.home.files.create(area/'release.json',canonical_bytes(plan))
            receipt=hashlib.sha256(canonical_bytes(plan)).hexdigest()
            return dict(operation=operation,state='current' if unchanged else 'prepared',release=verified.release,receipt=receipt,
                question='기록과 설정의 복구본을 남기고 갱신할까요?')
    def apply(self,*,operation,receipt,checkpoint=lambda _:None):
        plan,expected=self._read(operation);require(receipt==expected,'release-review-changed')
        forward_allowed(self.home,operation)
        self.trust.activation_check(plan['download'])
        if plan['unchanged']:
            with self.home.files.exclusion(self.home.root/'management.lock'):
                with self.home.files.exclusion(self.home.slots.root/'runtime.lock',shared=True):
                    forward_allowed(self.home,operation)
                    require(self.home.slots.selection()[0]==canonical_bytes(plan['before']),'runtime-selection-changed')
                    self.home.slots.verify(plan['target']);self.trust.activation_check(plan['download'])
                    NativeEntryUpdate(self.home,plan['target'],operation).apply()
                    MacNoticeFiles(self.home,plan['target'],operation).apply()
                    return dict(state='current',records_preserved=True,settings_preserved=True)
        return self._activate(plan,operation+'-activate',checkpoint)

    def _activate(self,plan,activation_operation,checkpoint):
        entries=NativeEntryUpdate(self.home,plan['target'],plan['operation']);notices=MacNoticeFiles(self.home,plan['target'],plan['operation'])
        def guard():
            forward_allowed(self.home,plan['operation']);self.trust.activation_check(plan['download'])
        def change_entries():
            guard()
            entries.prepare();entries.apply(guard=guard,checkpoint=checkpoint)
            notices.prepare();notices.apply(guard=guard,checkpoint=checkpoint)
        result=self.home.update(operation=activation_operation,target=plan['target'],expected_selection=canonical_bytes(plan['before']),
            checkpoint=checkpoint,replacement=plan.get('replacement',False),activation_guard=guard,
            entry_activation=change_entries)
        with self.home.files.exclusion(self.home.root/'management.lock'):
            with self.home.files.exclusion(self.home.slots.root/'runtime.lock'):
                forward_allowed(self.home,plan['operation']);entries.finish();notices.finish()
        return result

    def resume(self,*,operation,receipt,renewal=None,checkpoint=lambda _:None):
        """Explicit resume, never automatic retry or download.

        If activation has not happened, fresh backups cover the unchanged live
        record state before continuation. Previous backups/failure evidence stay.
        An already selected target only needs exact completion verification.
        """
        plan,expected=self._read(operation);require(receipt==expected,'release-review-changed')
        require(not plan['unchanged'],'release-resume-not-required')
        with self.home.files.exclusion(self.home.root/'management.lock'):
            forward_allowed(self.home,operation)
            with self.home.files.exclusion(self.home.slots.root/'runtime.lock'):
                raw,state=self.home.slots.selection()
                if state['selected']==plan['target']:
                    self.home.slots.verify(plan['target']);NativeEntryUpdate(self.home,plan['target'],operation).finish();MacNoticeFiles(self.home,plan['target'],operation).finish()
                    return dict(state='updated',records_preserved=True,settings_preserved=True,recovery_available=state['recovery'] is not None)
                require(raw==canonical_bytes(plan['before']),'runtime-selection-changed')
                plan=dict(plan,download=effective(self.home,self.trust,operation=operation,original=expected,download=plan['download'],renewal=renewal))
        return self._activate(plan,operation+'-resume-'+uuid.uuid4().hex,checkpoint)
