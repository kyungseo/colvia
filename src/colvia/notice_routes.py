"""Private native event-ID routing; an event is a pointer, never authority.

Only a supplied receiver port can emit. This module does not register apps,
request OS grants or start a process. Detail reads revalidate the retained event
and distinguish its original result from current state, even after disconnection.
"""
from pathlib import Path
import hashlib,re,uuid
from .codec import canonical_bytes,decode_canonical,decode_envelope,ObjectRef,RecordError,require
from .binding import _uuid
from .storage.sqlite import _token
from .records import link
from .connection import workspace_payload
from .work import WorkService
from .workspace import LocalWorkspace
from .delivery.service import DeliveryService
from .delivery.notices import Notices


def route_value(value):
    require(type(value) is dict and set(value)=={'version','project','instance','delivery','event','receiver'} and
            type(value['version']) is int and value['version']==1,'notice-route-invalid')
    _uuid(value['project']);_uuid(value['instance']);_token(value['delivery'])
    ref=ObjectRef.parse(value['event'])
    require(ref.kind=='notice.event' and ref.version==1,'notice-route-event-invalid')
    receiver=value['receiver']
    require(type(receiver) is dict and set(receiver)=={'id','version'} and type(receiver['version']) is int and receiver['version']>=1,'notice-route-receiver-invalid')
    _token(receiver['id']);return ref


class UnavailableWorkspace:
    def __init__(self,code='workspace-access-unavailable'):self.workspace='unavailable';self.code=code
    def verify(self):raise RecordError(self.code)
    def selected(self,*_):raise RecordError(self.code)


class NoticeRoutes:
    def __init__(self,home):self.home=home;self.files=home.files;self.root=home.root/'notice-events'
    def persist(self,route):
        value=dict(version=1,**route);route_value(value)
        with self.files.exclusion(self.home.root/'management.lock'):
            if not self.root.exists():self.files.create_directory(self.root)
            self.files.private_directory(self.root)
            event=uuid.uuid4().hex;self.files.create(self.root/(event+'.json'),canonical_bytes(value))
        return event
    def read(self,event):
        require(type(event) is str and re.fullmatch('[0-9a-f]{32}',event),'notice-event-id-invalid')
        self.files.private_directory(self.root)
        value=decode_canonical(self.files.read(self.root/(event+'.json')));route_value(value);return value
    def details(self,event,entry,*,original_only=False,route_digest=None):
        from .managed_entry import ManagedAuthority
        from .cli import read_locator
        value=self.read(event);ref=route_value(value)
        if route_digest is not None or original_only:
            require(hashlib.sha256(canonical_bytes(value)).hexdigest()==route_digest,'notice-route-changed')
        authority=ManagedAuthority(self.home.root/'authorities'/value['project'],project=value['project'],
            slots=self.home.slots,pointer=entry.pointer,files=self.files)
        store=authority.store(readonly=True)
        try:
            require(store.instance==value['instance'],'notice-instance-changed')
            with store.read_snapshot() as records:
                historical = Notices(DeliveryService(WorkService(records, UnavailableWorkspace())))
                recorded, request, original = historical.original_details(
                    value['delivery'], project=value['project'], instance=value['instance'], event_ref=ref)
                require(recorded.payload['receiver'] == value['receiver'], 'notice-receiver-mismatch')
                if original_only:
                    return original
                registration_ref = link(request, 'registration')
                registration = decode_envelope(registration_ref, records.load(registration_ref))
                workspace = workspace_payload(registration.payload)
                work = request.payload['work']
            service = WorkService(store, UnavailableWorkspace())
            try:
                git=entry.git();root=Path(workspace.root.path)
                service.workspace=LocalWorkspace(store,root,workspace.workspace,git=git,locator_reader=lambda:read_locator(root,git))
            except (OSError,RecordError) as exc:
                service.workspace=UnavailableWorkspace(exc.code if isinstance(exc,RecordError) else 'workspace-access-unavailable')
            notices = Notices(DeliveryService(service))
            from .delivery.service import notice_key
            for _ in range(2):
                before = store.root().ref
                details = notices.current_details(work, original)
                # A workspace refusal cannot conceal retirement or a route change.
                require(store.head(notice_key(value['delivery'])) == ref, 'notice-route-mismatch')
                if store.root().ref == before:
                    return details
            raise RecordError('notice-current-state-changed')
        finally:store.close()


class RoutedReceiver:
    """Adapt Core route fields to the native receiver's opaque 32-hex event ID."""
    def __init__(self,routes,receiver):self.routes=routes;self.receiver=receiver
    def check(self,identity):self.receiver.check(identity)
    def emit(self,route):
        event=self.routes.persist(route)
        # Exceptions and lost acknowledgements are handled by Notices.emit;
        # neither route creation nor an old event ever authorizes re-emission.
        if hasattr(self.receiver, 'emit_bound'):
            digest = hashlib.sha256(canonical_bytes(dict(version=1, **route))).hexdigest()
            return self.receiver.emit_bound(event, digest)
        return self.receiver.emit(event)


def detail_text(value):
    original=value['original'];current=value['current']
    title=original.get('title','맡긴 작업 결과')
    lines=[title,'',original.get('summary') or '맡긴 작업의 실행 결과가 준비되었습니다.']
    files=original.get('files',[])
    if files:
        lines.extend(['','결과 파일',*['• '+name for name in files[:20]]])
        if len(files)>20:lines.append(f'그 밖의 파일 {len(files)-20}개는 프로젝트에서 확인하세요.')
    states={'planned':'진행 승인 대기','active':'진행 중','review':'결과 검토 대기','completed':'결과 수락 완료','paused':'일시정지','discarded':'폐기'}
    lines.extend(['','현재 상태: '+states.get(current.get('state'),'현재 파일 상태 확인 필요')])
    if current.get('current_matches') is False:lines.append('현재 파일이 검토한 결과와 달라졌습니다.')
    if not value['workspace_connected']:lines.append('프로젝트 연결을 확인한 뒤 채팅에서 이 작업을 이어가세요. 보관된 결과는 남아 있습니다.')
    else:lines.append('프로젝트 채팅에서 “이 작업의 결과와 내가 확인할 부분을 보여줘”라고 요청하세요.')
    lines.append('알림을 열어도 결과가 자동 수락되지는 않습니다.')
    return '\n'.join(lines)
