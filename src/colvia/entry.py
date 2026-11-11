"""Managed-entry selection contract for the later signed installer/composition.

No host/product-name switch, PATH search or installer side effect belongs here.
Source diagnostics must label themselves source-only. A caller cannot convert a
source run into an installed qualification merely by selecting the same Python.
"""
from dataclasses import dataclass
from pathlib import PurePath
from .codec import require


@dataclass(frozen=True)
class RuntimeBinding:
    release:str
    executable:str
    executable_sha256:str
    supported_capabilities:frozenset[str]

    def __post_init__(self):
        require(type(self.release) is str and 0<len(self.release)<=160,'invalid-runtime-release')
        require(type(self.executable) is str and PurePath(self.executable).is_absolute(),'managed-runtime-required')
        require(type(self.executable_sha256) is str and len(self.executable_sha256)==64 and
                all(c in '0123456789abcdef' for c in self.executable_sha256),'invalid-runtime-digest')
        require(type(self.supported_capabilities) is frozenset and
                all(type(c) is str and c for c in self.supported_capabilities),'invalid-capabilities')


@dataclass(frozen=True)
class AccessEvidence:
    runtime_readable:bool
    runtime_executable:bool
    authority_readable:bool
    authority_writable:bool
    context:str  # actual qualified host/mode/location evidence identifier


def entry_check(binding:RuntimeBinding,*,verify_binding,access:AccessEvidence,required:frozenset[str],write:bool):
    """Return one actionable prerequisite; never expand a sandbox or install."""
    require(required<=binding.supported_capabilities,'runtime-capability-unavailable')
    require(verify_binding(binding),'managed-runtime-binding-unverified')
    if not access.runtime_readable or not access.runtime_executable:
        return {'ready':False,'reason':'runtime-access','message':'Colvia 실행기를 읽고 실행할 수 있도록 이 호스트의 접근 설정을 확인해 주세요.'}
    if not access.authority_readable or (write and not access.authority_writable):
        return {'ready':False,'reason':'authority-access','message':'이 프로젝트의 Colvia 기록 폴더에 접근 권한이 필요합니다. 안내된 폴더만 허용해 주세요.'}
    return {'ready':True,'release':binding.release,'context':access.context}
