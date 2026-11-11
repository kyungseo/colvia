"""Select the native Git effect port; never fall back to another OS."""
import sys
from ..codec import require


def integration_port(root,scratch,git,*,create):
    if sys.platform=='win32':
        from .windows_git import WindowsGit
        return WindowsGit(root,scratch,git,create=create)
    require(sys.platform=='darwin','git-integration-platform-unavailable')
    from .darwin_git import DarwinGit
    return DarwinGit(root,scratch,git,create=create)
