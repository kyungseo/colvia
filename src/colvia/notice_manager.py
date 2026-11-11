"""Managed native notice composition; registration and emission are explicit."""
import sys
from .codec import require

def receiver(home):
    if sys.platform=='darwin':
        from .platforms.darwin_notices import DarwinNotices
        return DarwinNotices(home)
    if sys.platform=='win32':
        from .platforms.windows_notices import WindowsNotices
        return WindowsNotices(home)
    require(False,'notice-platform-not-prepared')

def send(entry,project,delivery):
    from .managed_entry import ManagedAuthority
    from .notice_routes import NoticeRoutes,RoutedReceiver,UnavailableWorkspace
    from .work import WorkService
    from .delivery.service import DeliveryService
    from .delivery.notices import Notices
    home=entry.home
    authority=ManagedAuthority(home.authority(project).root,project=project,slots=home.slots,pointer=entry.pointer,files=home.files)
    store=authority.store()
    try:
        service=WorkService(store,UnavailableWorkspace());port=RoutedReceiver(NoticeRoutes(home),receiver(home))
        import uuid
        return Notices(DeliveryService(service)).emit(operation='notice-'+uuid.uuid4().hex,delivery=delivery,port=port)
    finally:store.close()
