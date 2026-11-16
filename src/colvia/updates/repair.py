"""Explicit verified recovery manager; never a normal-launch fallback."""
import hashlib
from ..codec import canonical_bytes,decode_canonical,require
from ..management import ManagerHome
from ..managed_entry import current_platform,process_runtime

class RecoveryManager:
    def __init__(self,root,*,pointer):
        os_name,architecture=current_platform();self.home=ManagerHome(root,os_name=os_name,architecture=architecture)
        require(not self.home.files.exists(self.home.root/'uninstall.json'),'uninstall-transition-pending')
        raw,state=self.home.slots.selection();require(state['recovery']==pointer,'runtime-recovery-target-mismatch')
        self.slot=self.home.slots.verify(pointer);self.expected=raw;self.target=pointer
        m=decode_canonical(self.home.files.read(self.home.slots.root/'slots'/self.slot.slot/'manifest.json',4*1024*1024))
        require(process_runtime()==(self.slot.python,m['python_version'],m['sqlite_version']),'dedicated-runtime-mismatch')
    def preview(self):
        with self.home.files.exclusion(self.home.root/'management.lock'):
            with self.home.files.exclusion(self.home.slots.root/'runtime.lock',shared=True):
                raw,state=self.home.slots.selection();require(raw==self.expected,'runtime-selection-changed')
                slot=self.home.slots.verify(self.target);read,write,states=self.home.requirements()
                require(read<=slot.read_capabilities and write<=slot.write_capabilities,'runtime-recovery-capability-unavailable')
                review=dict(version=1,before=state,target=self.target,states=states)
                return dict(review=review,receipt=hashlib.sha256(canonical_bytes(review)).hexdigest(),
                    question='기록과 설정을 보존하고 호환되는 이전 실행기로 복구할까요?')
    def apply(self,*,operation,receipt):
        preview=self.preview();require(receipt==preview['receipt'],'recovery-review-changed')
        return self.home.update(operation=operation,target=self.target,expected_selection=self.expected,recovery=True,
                                expected_states=preview['review']['states'])
