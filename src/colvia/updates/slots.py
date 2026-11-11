"""Verified immutable runtime slots and small selection bindings.

This source API never downloads, installs, changes PATH, starts Python or deletes
an old slot. The trusted manager supplies the manifest digest learned from signed
metadata. Project-local configuration cannot choose that digest or capabilities.
"""
from dataclasses import dataclass
import hashlib,re,os,stat
from pathlib import Path
from ..codec import RecordError,require,canonical_bytes,decode_canonical
from ..entry import RuntimeBinding
from ..tree import canonical_entries,logical_path
from ..platforms.posix import snapshot,ObservationBudget
from ..storage.files import platform_files
from ..storage.sqlite import _token

def supported_python_version(os_name,architecture,version):
    """Exact candidate runtime versions, not arbitrary system-Python support."""
    return ((os_name,architecture) in (('macos','arm64'),('windows','arm64'),('windows','x64')) and
            (version in ('3.14.6','3.14.7') or
             ((os_name,architecture)==('macos','arm64') and version=='3.14.10')))


@dataclass(frozen=True)
class VerifiedSlot:
    slot:str
    manifest_sha256:str
    release:str
    sequence:int
    python:str
    manager:str
    product:str
    read_capabilities:frozenset
    write_capabilities:frozenset
    features:frozenset
    binding:RuntimeBinding

def _caps(value):
    require(type(value) is list and len(value)<=256 and value==sorted(set(value)) and
            all(type(v) is str and 0<len(v)<=160 and v.isascii() for v in value),'slot-capabilities')
    return frozenset(value)

def verify_slot(root,slot,manifest_sha256,*,os_name,architecture,files=None,observe=snapshot,cancelled=lambda:False):
    _token(slot);root=Path(root);files=files or platform_files()
    require(type(manifest_sha256) is str and re.fullmatch('[0-9a-f]{64}',manifest_sha256),'slot-manifest-identity')
    files.private_directory(root)
    return verify_payload(root/'slots'/slot,slot,manifest_sha256,os_name=os_name,architecture=architecture,
                          files=files,observe=observe,cancelled=cancelled)


def verify_payload(location,slot,manifest_sha256,*,os_name,architecture,files=None,observe=snapshot,cancelled=lambda:False):
    """Verify the extracted pinned bootstrap with the identical inventory rules."""
    _token(slot);location=Path(location);files=files or platform_files()
    for parent in (location,*location.parents):require(not parent.is_symlink(),'slot-path-symlink')
    native_inventory=getattr(files,'verify_runtime_inventory',None)
    if native_inventory is not None:files.private_directory(location)
    else:
        info=location.lstat()
        require(stat.S_ISDIR(info.st_mode) and info.st_uid==os.getuid() and info.st_mode&0o022==0,'slot-directory-not-private')
    require(type(manifest_sha256) is str and re.fullmatch('[0-9a-f]{64}',manifest_sha256),'slot-manifest-identity')
    raw=files.read(location/'manifest.json',4*1024*1024)
    require(hashlib.sha256(raw).hexdigest()==manifest_sha256,'slot-manifest-mismatch')
    m=decode_canonical(raw)
    require(type(m) is dict and set(m)=={'version','release','sequence','os','architecture','python_version','sqlite_version',
            'python','manager','product','read_capabilities','write_capabilities','features','inventory'} and
            type(m['version']) is int and m['version']==1 and type(m['sequence']) is int and m['sequence']>=1,
            'invalid-slot-manifest')
    _token(m['release'])
    require(m['os']==os_name and m['architecture']==architecture and
            (os_name,architecture) in (('macos','arm64'),('windows','arm64'),('windows','x64')),'slot-platform-unavailable')
    require(supported_python_version(m['os'],m['architecture'],m['python_version']) and type(m['sqlite_version']) is str and
            re.fullmatch(r'[0-9]+\.[0-9]+\.[0-9]+',m['sqlite_version']),'slot-runtime-version')
    require(tuple(int(n) for n in m['sqlite_version'].split('.'))>=(3,37,0),'slot-sqlite-version')
    readers=_caps(m['read_capabilities']);writers=_caps(m['write_capabilities']);features=_caps(m['features'])
    expected=canonical_entries(m['inventory'])
    require(expected==m['inventory'] and len(expected)<=100000 and
            all(e['kind']=='regular' and e['path']!='manifest.json' for e in expected),'slot-inventory')
    indexed={e['path']:e for e in expected}
    for name in ('python','manager','product'):
        require(type(m[name]) is str and logical_path(m[name])==m[name] and m[name] in indexed,'slot-entry-missing')
    require(indexed[m['python']]['mode']=='100755','slot-python-not-executable')
    size=sum(e['size'] for e in expected)
    require(size<=4*1024**3,'slot-size-limit')
    if native_inventory is not None:
        native_inventory(location,expected,raw,manifest_sha256,cancelled=cancelled)
    else:
        observed=observe(location,ObservationBudget(120000,size+len(raw)),cancelled=cancelled)
        contents=[e for e in observed.entries if e['path']!='manifest.json']
        require(contents==expected,'slot-inventory-mismatch')
        manifest_entry=next((e for e in observed.entries if e['path']=='manifest.json'),None)
        require(manifest_entry is not None and manifest_entry['kind']=='regular' and
                manifest_entry['sha256']==manifest_sha256 and manifest_entry['size']==len(raw),'slot-manifest-changed')
        for item in observed.stamps:
            native=(location/item.native_path).lstat()
            require(stat.S_ISREG(native.st_mode) and native.st_nlink==1 and native.st_uid==os.getuid() and native.st_mode&0o022==0,
                    'slot-file-not-private')
    binding=RuntimeBinding(m['release'],str(location/m['python']),indexed[m['python']]['sha256'],readers|writers)
    return VerifiedSlot(slot,manifest_sha256,m['release'],m['sequence'],str(location/m['python']),
                        str(location/m['manager']),str(location/m['product']),readers,writers,features,binding)

def pointer(slot):return dict(slot=slot.slot,manifest_sha256=slot.manifest_sha256)

class RuntimeSlots:
    def __init__(self,root,*,os_name,architecture,files=None):
        self.root=Path(root);self.files=files or platform_files();self.os_name=os_name;self.architecture=architecture
        require(self.root.is_absolute() and self.root.is_dir() and not self.root.is_symlink(),'runtime-root-unavailable')
    @classmethod
    def create(cls,root,*,os_name,architecture,files=None):
        root=Path(root);files=files or platform_files()
        require(root.is_absolute(),'runtime-root-required')
        for parent in root.parents:require(not parent.is_symlink(),'runtime-root-symlink')
        files.create_directory(root);files.create_directory(root/'slots')
        files.create(root/'runtime.lock',b'')
        files.create(root/'first-install.json',canonical_bytes(dict(version=1,os=os_name,architecture=architecture)))
        files.sync_directory(root.parent)
        return cls(root,os_name=os_name,architecture=architecture,files=files)
    def initialize(self,target):
        with self.files.exclusion(self.root/'runtime.lock'):
            claim=canonical_bytes(dict(version=1,os=self.os_name,architecture=self.architecture))
            require(self.files.read(self.root/'first-install.json')==claim,'runtime-first-install-claim')
            require(not (self.root/'runtime.json').exists(),'runtime-already-initialized')
            candidate=self.verify(target)
            state=dict(version=1,selected=target,recovery=None,high_sequence=candidate.sequence)
            self.files.create(self.root/'runtime.json',canonical_bytes(state))
            self.files.remove(self.root/'first-install.json',claim)
            return state
    def recovery_launch(self,*,read_requirements,write_requirements=()):
        _,state=self.selection()
        require(state['recovery'] is not None,'runtime-recovery-unavailable')
        slot=self.verify(state['recovery'])
        require(set(read_requirements)<=slot.read_capabilities and set(write_requirements)<=slot.write_capabilities,
                'runtime-recovery-capability-unavailable')
        return [slot.python,'-I','-B',slot.manager,'--repair']

    def verify(self,value):
        require(type(value) is dict and set(value)=={'slot','manifest_sha256'},'runtime-pointer-invalid')
        return verify_slot(self.root,**value,os_name=self.os_name,architecture=self.architecture,files=self.files)
    def selection(self):
        try:raw=self.files.read(self.root/'runtime.json')
        except FileNotFoundError:raise RecordError('runtime-repair-required') from None
        value=decode_canonical(raw)
        require(type(value) is dict and set(value)=={'version','selected','recovery','high_sequence'} and
                type(value['version']) is int and value['version']==1 and type(value['high_sequence']) is int and value['high_sequence']>=1,
                'runtime-pointer-invalid')
        require(value['recovery'] is None or type(value['recovery']) is dict,'runtime-pointer-invalid')
        return raw,value
    def launch(self,*,read_requirements,write_requirements=(),manager=False):
        _,state=self.selection();slot=self.verify(state['selected'])
        require(set(read_requirements)<=slot.read_capabilities and set(write_requirements)<=slot.write_capabilities,
                'runtime-capability-unavailable')
        # No updater lock or network request is used to run a verified slot.
        return [slot.python,'-I','-B',slot.manager if manager else slot.product]
    def activate(self,target,*,expected_selection,read_requirements,write_requirements=(),recovery=False,replacement=False,before_activate=None):
        with self.files.exclusion(self.root/'runtime.lock'):
            raw,state=self.selection();require(raw==expected_selection,'runtime-selection-changed')
            require(type(recovery) is bool and type(replacement) is bool and not (recovery and replacement),'runtime-repair-mode-conflict')
            candidate=self.verify(target)
            require(set(read_requirements)<=candidate.read_capabilities and set(write_requirements)<=candidate.write_capabilities,
                    'runtime-capability-unavailable')
            require(target!=state['selected'],'runtime-already-selected')
            if recovery:
                require(target==state['recovery'],'runtime-recovery-target-mismatch')
                # The selected slot may be broken. Never promote its unverified
                # bytes into the next recovery choice. Keep its files and the
                # exact prior binding in a durable, idempotent repair record.
                history=canonical_bytes(dict(version=1,before=state,target=target))
                name='repair-'+hashlib.sha256(history).hexdigest()+'.json'
                try:self.files.create(self.root/name,history)
                except FileExistsError:require(self.files.read(self.root/name)==history,'runtime-repair-record-conflict')
                next_recovery=None
            elif replacement:
                # An explicitly authenticated bootstrap replacement may repair
                # damaged slots, never reset the high-water mark or data.
                try:self.verify(state['selected'])
                except (RecordError,FileNotFoundError):pass
                else:raise RecordError('runtime-replacement-not-required')
                require(candidate.sequence>state['high_sequence'] or
                        (candidate.sequence==state['high_sequence'] and target['manifest_sha256']==state['selected']['manifest_sha256']),
                        'runtime-release-rollback')
                history=canonical_bytes(dict(version=1,before=state,target=target,kind='authenticated-replacement'))
                name='repair-'+hashlib.sha256(history).hexdigest()+'.json'
                try:self.files.create(self.root/name,history)
                except FileExistsError:require(self.files.read(self.root/name)==history,'runtime-repair-record-conflict')
                next_recovery=None
            else:
                selected=self.verify(state['selected'])
                require(candidate.sequence>state['high_sequence'],'runtime-release-rollback')
                next_recovery=pointer(selected)
            if before_activate is not None:
                additional_read,additional_write=before_activate(candidate)
                read_requirements=set(read_requirements)|set(additional_read)
                write_requirements=set(write_requirements)|set(additional_write)
                require(self.selection()[0]==raw,'runtime-selection-changed')
            require(set(read_requirements)<=candidate.read_capabilities and set(write_requirements)<=candidate.write_capabilities,
                    'runtime-capability-unavailable')
            next_state=dict(version=1,selected=target,recovery=next_recovery,
                            high_sequence=max(state['high_sequence'],candidate.sequence))
            self.files.replace(self.root/'runtime.json',canonical_bytes(next_state),raw)
            # Both slots remain present. A compatible rollback never rolls data back.
            require(self.selection()[1]==next_state,'runtime-activation-unconfirmed')
            return next_state
