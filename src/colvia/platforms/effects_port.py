"""Native file-effect selection; unsupported hosts never use a POSIX fallback."""
import sys
from ..codec import require

def effects(root,authority):
    if sys.platform=='darwin':
        from .darwin_effects import DarwinEffects
        return DarwinEffects(root,authority)
    if sys.platform=='win32':
        from .windows_effects import WindowsEffects
        return WindowsEffects(root,authority)
    require(False,'effect-platform-unavailable')
