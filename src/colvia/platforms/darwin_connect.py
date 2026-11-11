"""Local APFS integration and explicit restore rebind adapters."""
from .managed_files import ManagedConnect
from .darwin_detach import DarwinDetach

class DarwinConnect(ManagedConnect,DarwinDetach):
    pass

class DarwinRebind(DarwinConnect):
    replace_locator=True
