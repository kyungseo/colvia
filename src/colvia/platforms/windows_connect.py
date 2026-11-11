"""Native NTFS integration using common reviewed-file semantics."""
from .managed_files import ManagedFiles,ManagedConnect
from .windows_effects import WindowsEffects
from ..storage.windows import WindowsFiles

class WindowsDetach(ManagedFiles):
    def __init__(self,authority,locations,*,files=None,effects=WindowsEffects):
        super().__init__(authority,locations,files=files or WindowsFiles(),effects=effects)

class WindowsConnect(ManagedConnect,WindowsDetach):
    pass

class WindowsRebind(WindowsConnect):
    replace_locator=True
