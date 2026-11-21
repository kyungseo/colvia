"""Pinned bootstrap handoff and first signed release preparation.

An existing home always delegates to its already trusted manager. A partial home
is never discarded or treated as new. A first installation remains unpublished
until signature, inventory, native entry and trust-expiry checks all succeed.
"""
from ..platforms.owned_install_files import present
from pathlib import Path
import hashlib,os,uuid
from ..codec import canonical_bytes,decode_canonical,require
from ..management import ManagerHome
from ..managed_entry import current_platform,process_runtime
from ..storage.files import platform_files
from ..storage.sqlite import _token
from .slots import verify_payload,pointer
from .trust import Trust,_url,_target
from .fetch import https_fetcher
from .package import stage_archive,_portable,descriptor
from .reauthentication import forward_allowed,effective,renew,metadata_only
from .initial_home import initialize_home,retry_claim,initial_intent,initial_head


def configuration(files,location):
    value=decode_canonical(files.read(location/'installation.json'))
    require(type(value) is dict and set(value)=={'version','channel','metadata_url','target_url','target','anchor','native_entry'} and
            type(value['version']) is int and value['version']==1,'installation-configuration-invalid')
    _token(value['channel']);_target(value['target'])
    require(_url(value['metadata_url'])==value['metadata_url'] and _url(value['target_url'])==value['target_url'],'installation-origin-invalid')
    for key in ('anchor','native_entry'):require(_portable(value[key])==value[key],'installation-path-invalid')
    return value


def existing_manager(root,*,os_name,architecture,files=None):
    home=ManagerHome(root,os_name=os_name,architecture=architecture,files=files)
    _,state=home.slots.selection();slot=home.slots.verify(state['selected'])
    return [slot.python,'-I','-B',slot.manager,'--management-root',str(home.root),
            '--runtime-slot',slot.slot,'--runtime-manifest-sha256',slot.manifest_sha256,'update']


class FirstInstall:
    """Composition port accepts a verified-download service, never public JSON.

    Tests explicitly supply a verifier double; production supplies pinned Trust.
    """
    def __init__(self,home,trust,config):self.home=home;self.trust=trust;self.config=config
    def perform(self,*,operation,claimed=False,retry_of=None,anchor=None,cancelled=lambda:False,checkpoint=lambda _:None):
        _token(operation);home=self.home
        with home.files.exclusion(home.root/'management.lock'):
            require(not present(home.slots.root/'runtime.json'),'runtime-already-initialized')
            area=home.root/'operations'/operation
            forward_allowed(home,operation)
            if retry_of is not None:
                require(not claimed,'initial-attempt-mode-conflict')
                retry_claim(home,self.trust,self.config,anchor,previous=retry_of,operation=operation)
            elif not claimed:
                home.files.create_directory(area)
                home.files.create(area/'install-intent.json',canonical_bytes(initial_intent(operation,self.config['target'])))
            require(decode_canonical(home.files.read(area/'install-intent.json'))==initial_intent(operation,self.config['target']),
                    'installation-intent-changed')
            if home.files.exists(home.root/'initial-install.json'):
                require(anchor is not None,'initial-claim-anchor-required')
                require(initial_head(home,self.trust,self.config,anchor)==operation,'initial-attempt-not-current')
                if home.files.exists(area/'retry-of.json'):
                    previous=decode_canonical(home.files.read(area/'retry-of.json'))['previous']
                    if home.files.exists(home.root/'operations'/previous/'quarantine-intent.json'):
                        from .initial_quarantine import completed
                        require(completed(home,previous)['successor']==operation,'initial-quarantine-successor-mismatch')
            # Durable once-only start: a lost response requires a new explicit
            # retry, or exact resume if preparation completed. Never redownload.
            home.files.create(area/'started.json',canonical_bytes(dict(version=1,operation=operation)))
            download=self.trust.stage(self.config['target'],destination=area/'release.zip',cancelled=cancelled)
            slot=stage_archive(area/'release.zip',root=home.slots.root,slot=operation,target=download,channel=self.config['channel'],
                os_name=home.os_name,architecture=home.architecture,files=home.files,cancelled=cancelled)
            location=home.slots.root/'slots'/slot.slot
            config=configuration(home.files,location)
            # The signed release cannot silently redirect the first-install
            # origin/channel supplied by the externally pinned bootstrap.
            require(all(config[k]==self.config[k] for k in ('channel','metadata_url','target_url','target')),'installation-channel-changed')
            native=location/config['native_entry'];raw=home.files.read(native,64*1024*1024)
            manifest=decode_canonical(home.files.read(location/'manifest.json',4*1024*1024))
            require(any(e['path']==config['native_entry'] and e['mode']=='100755' for e in manifest['inventory']),'native-entry-not-executable')
            home.files.create(area/'prepared.json',canonical_bytes(dict(version=1,target=pointer(slot),download=download,native_sha256=hashlib.sha256(raw).hexdigest())))
            return self._publish(area,pointer(slot),download,raw,cancelled=cancelled,checkpoint=checkpoint)

    def _publish(self,area,target,download,raw,*,cancelled,checkpoint):
        home=self.home;files=home.files
        forward_allowed(home,area.name)
        self.trust.activation_check(download)
        from .initial_files import InitialFiles
        publication=InitialFiles(home,area.name,target,raw)
        publication.publish(guard=lambda:(forward_allowed(home,area.name),self.trust.activation_check(download)),checkpoint=checkpoint)
        checkpoint('entry-prepared');require(not cancelled(),'installation-cancelled');self.trust.activation_check(download)
        publication.verify_final()
        slot=home.slots.verify(target)
        if present(home.slots.root/'runtime.json'):
            _,state=home.slots.selection()
            require(state['selected']==target and state['recovery'] is None,'installation-selection-changed')
        else:state=home.slots.initialize(target)
        checkpoint('activated')
        completed=canonical_bytes(dict(version=1,selection=state))
        if present(area/'completed.json'):
            require(files.read(area/'completed.json')==completed,'installation-completion-changed')
        else:files.create(area/'completed.json',completed)
        return dict(state='installed',release=slot.release,project_connection_required=True)

    def status(self,*,anchor):
        home=self.home;files=home.files
        with files.exclusion(home.root/'management.lock'):
            operation=initial_head(home,self.trust,self.config,anchor)
            area=home.root/'operations'/operation
            result=dict(operation=operation,state='initial-preparation-incomplete',automatic_retry=False)
            if files.exists(area/'prepared.json'):
                result.update(state='initial-prepared',receipt=hashlib.sha256(files.read(area/'prepared.json',4*1024*1024)).hexdigest())
            if present(home.slots.root/'runtime.json'):
                result.update(state='runtime-selected',selection=home.slots.selection()[1])
            if files.exists(area/'quarantine-intent.json'):
                result['state']='initial-quarantined' if files.exists(area/'quarantine-complete.json') else 'initial-quarantine-pending'
                result['quarantine_receipt']=decode_canonical(files.read(area/'quarantine-intent.json',4*1024*1024))['receipt']
            result['live_files_present']=any(present(home.root/n) for n in ('bin','entry.json','receiver.json','native-update.json','notice-app.pending'))
            return result

    def refresh(self,*,operation,receipt,renewal,cancelled=lambda:False):
        _token(operation);home=self.home;files=home.files
        with files.exclusion(home.root/'management.lock'):
            area=home.root/'operations'/operation
            raw=files.read(area/'prepared.json',4*1024*1024)
            require(hashlib.sha256(raw).hexdigest()==receipt,'installation-review-changed')
            prepared=decode_canonical(raw)
            return renew(home,self.trust,operation=operation,original=receipt,download=prepared['download'],
                         renewal=renewal,cancelled=cancelled)

    def resume(self,*,operation,renewal=None,cancelled=lambda:False,checkpoint=lambda _:None):
        """Explicit completion of an already prepared exact install; no download retry.

        The caller must be a verified bootstrap/recovery runtime. Expired trust,
        incomplete staging or changed native bytes are retained and refused.
        """
        _token(operation);home=self.home;files=home.files
        with files.exclusion(home.root/'management.lock'):
            area=home.root/'operations'/operation;files.private_directory(area)
            intent=decode_canonical(files.read(area/'install-intent.json'))
            require(intent==dict(version=1,operation=operation,target=self.config['target']),'installation-intent-changed')
            prepared_raw=files.read(area/'prepared.json',4*1024*1024)
            prepared=decode_canonical(prepared_raw)
            require(type(prepared) is dict and set(prepared)=={'version','target','download','native_sha256'} and
                    type(prepared['version']) is int and prepared['version']==1,'installation-preparation-invalid')
            forward_allowed(home,operation)
            d=descriptor(prepared['download'].get('custom'),channel=self.config['channel'],os_name=home.os_name,architecture=home.architecture)
            require(prepared['download'].get('path')==self.config['target'] and prepared['target']['manifest_sha256']==d['manifest_sha256'],
                    'installation-release-description-changed')
            slot=home.slots.verify(prepared['target'])
            require(slot.release==d['release'] and slot.sequence==d['sequence'],'installation-release-description-changed')
            location=home.slots.root/'slots'/slot.slot
            config=configuration(files,location)
            require(all(config[k]==self.config[k] for k in ('channel','metadata_url','target_url','target')),'installation-channel-changed')
            manifest=decode_canonical(files.read(location/'manifest.json',4*1024*1024))
            require(any(e['path']==config['native_entry'] and e['mode']=='100755' for e in manifest['inventory']),'native-entry-not-executable')
            raw=files.read(location/config['native_entry'],64*1024*1024)
            require(hashlib.sha256(raw).hexdigest()==prepared['native_sha256'],'native-entry-changed')
            require(not cancelled(),'installation-cancelled')
            if present(home.slots.root/'runtime.json'):
                _,state=home.slots.selection()
                require(state['selected']==prepared['target'] and state['recovery'] is None,'installation-selection-changed')
                entries=[home.root/'bin'/name for name in (('colvia.exe','colvia-manage.exe') if home.os_name=='windows' else ('colvia','colvia-manage'))]
                expected=canonical_bytes(dict(version=1,os=home.os_name,architecture=home.architecture,sha256=hashlib.sha256(raw).hexdigest()))
                require(files.read(home.root/'entry.json')==expected and all(files.read(path,64*1024*1024)==raw for path in entries),'native-entry-changed')
                from .initial_files import InitialFiles
                InitialFiles(home,operation,prepared['target'],raw).verify_final(sync=True)
                done=canonical_bytes(dict(version=1,selection=state))
                if files.exists(area/'completed.json'):require(files.read(area/'completed.json')==done,'installation-completion-changed')
                else:files.create(area/'completed.json',done)
                return dict(state='installed',release=slot.release,project_connection_required=True)
            prepared=dict(prepared,download=effective(home,self.trust,operation=operation,original=hashlib.sha256(prepared_raw).hexdigest(),
                download=prepared['download'],renewal=renewal))
            return self._publish(area,prepared['target'],prepared['download'],raw,cancelled=cancelled,checkpoint=checkpoint)



def bootstrap(root,stage,digest,*,launch=os.execv,resume_operation=None,repair_operation=None,repair_resume=False,renewal=None,refresh_operation=None,refresh_receipt=None,retry_operation=None,rollback_operation=None,rollback_receipt=None,release_receipt=None,inspect_initial=False,quarantine_operation=None,quarantine_receipt=None,maintenance=None,exclude_unavailable=False):
    files=platform_files();os_name,architecture=current_platform();root=Path(root);stage=Path(stage)
    require(root.is_absolute() and stage.is_absolute(),'installation-absolute-path-required')
    require(type(inspect_initial) is bool and int(inspect_initial)+sum(v is not None for v in (resume_operation,repair_operation,refresh_operation,retry_operation,rollback_operation,quarantine_operation))<=1,'installation-repair-mode-conflict')
    require(quarantine_receipt is None or quarantine_operation is not None,'initial-quarantine-mode-conflict')
    require(renewal is None or resume_operation is not None or refresh_operation is not None,'installation-renewal-mode-conflict')
    require(type(repair_resume) is bool and (not repair_resume or repair_operation is not None),'installation-repair-mode-conflict')
    from .uninstall import MARKER, Uninstall
    maintenance_home=present(root/MARKER)
    ordinary=not inspect_initial and all(v is None for v in
        (resume_operation,repair_operation,refresh_operation,retry_operation,rollback_operation,quarantine_operation,maintenance))
    require(not maintenance_home or ordinary or maintenance is not None,'uninstall-transition-pending')
    require(maintenance is None or all(v is None for v in
        (resume_operation,repair_operation,refresh_operation,retry_operation,rollback_operation,quarantine_operation)),
        'installation-repair-mode-conflict')
    # A working installation never imports a new anchor, configuration or
    # executable from the bootstrap payload. Trust continues from its own root.
    if present(root) and ordinary and not maintenance_home:
        if files.exists(root/'initial-install.json') and not present(root/'runtime/runtime.json'):
            from ..codec import RecordError
            marker=decode_canonical(files.read(root/'initial-install.json'))
            error=RecordError('initial-install-recovery-required');error.operation=marker.get('operation');raise error
        command=existing_manager(root,os_name=os_name,architecture=architecture,files=files)
        return launch(command[0],command)
    files.private_directory(stage)
    slot=verify_payload(stage,'bootstrap',digest,os_name=os_name,architecture=architecture,files=files)
    manifest=decode_canonical(files.read(stage/'manifest.json',4*1024*1024))
    require(process_runtime()==(slot.python,manifest['python_version'],manifest['sqlite_version']),'dedicated-runtime-mismatch')
    config=configuration(files,stage);anchor=files.read(stage/config['anchor'],512*1024)
    if maintenance and maintenance[0] in ('purge-preview','purge','purge-resume'):
        from .purge import CompleteRemoval
        action, operation, receipt = maintenance
        removal = CompleteRemoval(root, files, os_name, architecture, operation)
        if action != 'purge-resume':
            from ..manager_entry import update_configuration
            own = update_configuration(removal._home())
            require(all(own[k] == config[k] for k in ('channel','metadata_url','target_url','target')),
                    'installation-channel-changed')
        if action == 'purge-preview':
            return removal.preview(exclude_unavailable, current_preparation=stage.parent)
        return removal.apply(receipt, resume=action=='purge-resume', exclude=exclude_unavailable)
    if maintenance_home or maintenance is not None:
        from ..manager_entry import update_configuration
        from .release import ReleaseUpdate
        home=ManagerHome(root,os_name=os_name,architecture=architecture,files=files)
        own=update_configuration(home)
        require(all(own[k]==config[k] for k in ('channel','metadata_url','target_url','target')),'installation-channel-changed')
        action,operation,receipt=maintenance or ('reinstall',None,None)
        transition=Uninstall(home)
        if action=='uninstall-preview':return transition.preview(operation)
        if action in ('uninstall','uninstall-resume'):
            return transition.apply(operation,receipt,resume=action=='uninstall-resume')
        if action=='uninstall-restore':return transition.restore(operation,receipt)
        require(action in ('reinstall','reinstall-resume'),'uninstall-maintenance-invalid')
        with files.exclusion(root/'management.lock'), files.exclusion(home.slots.root/'runtime.lock'):
            binding,run,resume=transition.prepare_reinstall(resume=action=='reinstall-resume')
        fetcher=https_fetcher(metadata_url=own['metadata_url'],target_url=own['target_url'])
        try:
            trust=Trust(root/'trust',metadata_url=own['metadata_url'],target_url=own['target_url'],fetcher=fetcher,files=files)
            service=ReleaseUpdate(home,trust,channel=own['channel'],replacement=True,reinstall=(transition,binding))
            if resume:
                plan,review=service._read(run)
                return service.resume(operation=run,receipt=review)
            preview=service.prepare(operation=run,target=own['target'])
            return service.apply(operation=run,receipt=preview['receipt'])
        finally:
            fetcher.close()
    if resume_operation is not None or repair_operation is not None or refresh_operation is not None or retry_operation is not None or rollback_operation is not None or quarantine_operation is not None or inspect_initial:
        if not inspect_initial:_token(resume_operation or repair_operation or refresh_operation or retry_operation or rollback_operation or quarantine_operation)
        # The externally verified bootstrap runs the recovery, but imports no
        # new root key, channel, runtime selection or update counters.
        from ..manager_entry import update_configuration
        home=ManagerHome(root,os_name=os_name,architecture=architecture,files=files)
        own=update_configuration(home)
        require(all(own[k]==config[k] for k in ('channel','metadata_url','target_url','target')),'installation-channel-changed')
        if quarantine_operation is not None:
            from .initial_quarantine import InitialQuarantine
            class NoNetwork:
                def fetch(self,*a,**kw):raise RuntimeError('initial-quarantine-network-forbidden')
            offline=Trust(home.root/'trust',metadata_url=own['metadata_url'],target_url=own['target_url'],fetcher=NoNetwork(),files=files)
            recovery=InitialQuarantine(home,offline,own,anchor)
            if quarantine_receipt is None:return recovery.preview(operation=quarantine_operation)
            recovery.apply(operation=quarantine_operation,receipt=quarantine_receipt)
            claimed=recovery.claim(operation=quarantine_operation,receipt=quarantine_receipt)
            if claimed['state']!='replacement-claimed':return claimed
            # Construct the network port only after retirement completion and
            # the unique successor edge are durable. No failed download loops.
            fetcher=https_fetcher(metadata_url=own['metadata_url'],target_url=own['target_url'])
            try:
                trust=Trust(home.root/'trust',metadata_url=own['metadata_url'],target_url=own['target_url'],fetcher=fetcher,files=files)
                return FirstInstall(home,trust,own).perform(operation=claimed['operation'],claimed=True,anchor=anchor)
            except Exception as exc:
                exc.operation=claimed['operation'];raise
            finally:fetcher.close()
        if rollback_operation is not None:
            from .release import ReleaseUpdate
            service=ReleaseUpdate(home,None,channel=own['channel'])
            if rollback_receipt is None:return service.rollback_preview(operation=rollback_operation,receipt=release_receipt)
            return service.rollback(operation=rollback_operation,receipt=release_receipt,rollback_receipt=rollback_receipt)
        if retry_operation is not None:
            fetcher=https_fetcher(metadata_url=own['metadata_url'],target_url=own['target_url'])
            operation='install-'+uuid.uuid4().hex
            try:
                trust=Trust(home.root/'trust',metadata_url=own['metadata_url'],target_url=own['target_url'],fetcher=fetcher,files=files)
                return FirstInstall(home,trust,own).perform(operation=operation,retry_of=retry_operation,anchor=anchor)
            except Exception as exc:
                exc.operation=operation;raise
            finally:fetcher.close()
        if repair_operation is not None:
            from .release import ReleaseUpdate
            fetcher=https_fetcher(metadata_url=own['metadata_url'],target_url=own['target_url'])
            try:
                trust=Trust(home.root/'trust',metadata_url=own['metadata_url'],target_url=own['target_url'],fetcher=fetcher,files=files)
                service=ReleaseUpdate(home,trust,channel=own['channel'],replacement=True)
                if repair_resume:
                    plan,receipt=service._read(repair_operation)
                    require(plan.get('replacement') is True,'runtime-repair-operation-required')
                    return service.resume(operation=repair_operation,receipt=receipt)
                preview=service.prepare(operation=repair_operation,target=own['target'])
                return service.apply(operation=repair_operation,receipt=preview['receipt'])
            finally:fetcher.close()
        if refresh_operation is not None:
            fetcher=https_fetcher(metadata_url=own['metadata_url'],target_url=own['target_url'])
            try:
                trust=Trust(home.root/'trust',metadata_url=own['metadata_url'],target_url=own['target_url'],fetcher=metadata_only(fetcher,own['metadata_url']),files=files)
                return FirstInstall(home,trust,own).refresh(operation=refresh_operation,receipt=refresh_receipt,renewal=renewal)
            finally:fetcher.close()
        class OfflineFetcher:
            def fetch(self,*args,**kwargs):raise RuntimeError('installation-resume-network-forbidden')
        trust=Trust(home.root/'trust',metadata_url=own['metadata_url'],target_url=own['target_url'],fetcher=OfflineFetcher(),files=files)
        service=FirstInstall(home,trust,own)
        if inspect_initial:return service.status(anchor=anchor)
        return service.resume(operation=resume_operation,renewal=renewal)
    fetcher=https_fetcher(metadata_url=config['metadata_url'],target_url=config['target_url'])
    try:
        home,trust,operation=initialize_home(root,os_name=os_name,architecture=architecture,files=files,
            config=config,anchor=anchor,payload_digest=digest,fetcher=fetcher,trust_type=Trust)
        try:return FirstInstall(home,trust,config).perform(operation=operation,claimed=True,anchor=anchor)
        except Exception as exc:
            exc.operation=operation
            raise
    finally:fetcher.close()
