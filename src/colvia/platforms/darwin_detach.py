"""Local APFS retained-original detachment adapter."""
from .managed_files import ManagedFiles

class DarwinDetach(ManagedFiles):
    def __init__(self,authority,locations):
        from ..storage.files import PosixFiles
        from .darwin_effects import DarwinEffects
        super().__init__(authority,locations,files=PosixFiles(),effects=DarwinEffects)
