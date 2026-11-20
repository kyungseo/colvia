"""Dedicated-runtime manager entry; mutations are explicit commands.

User installation authorization covers update preparation and activation. Project
connection and detach retain their own concrete review receipts. This module
never edits host grants, searches PATH, requests OS privileges or creates keys.
"""
import argparse,json,uuid,sys
from pathlib import Path
from .codec import canonical_bytes,decode_canonical,require,RecordError
from .managed_entry import ManagedEntry,RuntimeOptionOnce
from .project_setup import ProjectSetup
from .connection_boundary import ConnectionBoundaryError
from .updates.release import ReleaseUpdate
from .updates.trust import Trust,_url,_target
from .updates.fetch import https_fetcher
from .updates.space import SpaceError
from .presentation import failure


def space_message(error, message):
    if not isinstance(error, SpaceError):
        return message
    detail = error.diagnostic
    phase = {'target-download': '배포 파일 다운로드', 'slot-expand': '배포 파일 풀기'}[detail['phase']]
    parts = [message, f"단계 {phase}"]
    if detail['volume']:
        parts.append(f"볼륨 {detail['volume']}")
    if 'available_bytes' in detail:
        parts.append(f"사용 가능 {detail['available_bytes']:,}바이트")
    if 'required_bytes' in detail:
        parts.append(f"필요 {detail['required_bytes']:,}바이트")
    return ' · '.join(parts)


def trust_failure(error):
    # The dependency is optional for source-only Work tests, mandatory in a
    # release. Preserve unexpected programming failures instead of disguising
    # every exception as an ordinary update refusal.
    try:from tuf.api.exceptions import RepositoryError,DownloadError
    except ImportError:return None
    if isinstance(error,RepositoryError):return 'update-trust-verification-failed'
    if isinstance(error,DownloadError):return 'update-download-failed'
    return None


def update_configuration(home):
    value=decode_canonical(home.files.read(home.root/'updates.json'))
    require(type(value) is dict and set(value)=={'version','channel','metadata_url','target_url','target'} and
            type(value['version']) is int and value['version']==1,'managed-update-configuration-invalid')
    from .storage.sqlite import _token
    _token(value['channel']);_target(value['target'])
    require(_url(value['metadata_url'])==value['metadata_url'] and _url(value['target_url'])==value['target_url'],
            'managed-update-configuration-invalid')
    return value


def parser(*,bound=False):
    p=argparse.ArgumentParser(prog='colvia manage',allow_abbrev=False)
    if not bound:
        p.add_argument('--management-root',required=True,action=RuntimeOptionOnce)
        p.add_argument('--runtime-slot',required=True,action=RuntimeOptionOnce)
        p.add_argument('--runtime-manifest-sha256',required=True,action=RuntimeOptionOnce)
        p.add_argument('--repair',nargs=0,action=RuntimeOptionOnce)
        p.add_argument('--receiver-source',type=Path,action=RuntimeOptionOnce)
    else:p.set_defaults(receiver_source=None,repair=False)
    p.add_argument('--json',action='store_true')
    commands=p.add_subparsers(dest='command',required=True)
    commands.add_parser('status')
    git_preview = commands.add_parser('git-register-preview')
    git_preview.add_argument('executable')
    git_register = commands.add_parser('git-register')
    git_register.add_argument('--plan', type=Path, required=True)
    git_register.add_argument('--receipt', required=True)
    git_register.add_argument('--replace', action='store_true')
    for command in ('notice-detail','notice-original'):
        detail=commands.add_parser(command)
        detail.add_argument('--event',required=True)
        detail.add_argument('--route-sha256',required=command=='notice-original')
    for name in ('notice-enable','notice-disable','notice-check','notice-registration-resume','notice-identity','notice-registration-status'):commands.add_parser(name)
    notice=commands.add_parser('notice-send');notice.add_argument('project');notice.add_argument('delivery')
    restore=commands.add_parser('restore-prepare');restore.add_argument('archive',type=Path);restore.add_argument('--operation',required=True)
    restore=commands.add_parser('restore-apply');restore.add_argument('operation');restore.add_argument('--receipt',required=True)
    restore=commands.add_parser('restore-status');restore.add_argument('operation')
    restore=commands.add_parser('restore-resume');restore.add_argument('operation');restore.add_argument('--receipt',required=True)
    restored=commands.add_parser('rebind-preview');restored.add_argument('project');restored.add_argument('root',type=Path)
    restored=commands.add_parser('rebind');restored.add_argument('--plan',type=Path,required=True);restored.add_argument('--receipt',required=True)
    restored.add_argument('--statement',required=True);restored.add_argument('--operation',required=True)
    restored=commands.add_parser('rebind-resume');restored.add_argument('operation')
    identity=commands.add_parser('identity-preview');identity.add_argument('projects',nargs='+')
    identity=commands.add_parser('identity-apply');identity.add_argument('--plan',type=Path,required=True)
    identity.add_argument('--receipt',required=True);identity.add_argument('--statement',required=True)
    identity.add_argument('--operation',required=True)
    for name in ('identity-status','identity-resume'):
        commands.add_parser(name).add_argument('operation')
    preview = commands.add_parser('git-transition-preview')
    preview.add_argument('root', type=Path)
    apply = commands.add_parser('git-transition-apply')
    apply.add_argument('--plan', type=Path, required=True)
    apply.add_argument('--receipt', required=True)
    apply.add_argument('--statement', required=True)
    apply.add_argument('--operation', required=True)
    commands.add_parser('git-transition-cancel').add_argument('operation')
    commands.add_parser('git-transition-resume-preview').add_argument('operation')
    resume = commands.add_parser('git-transition-resume')
    resume.add_argument('operation')
    resume.add_argument('--receipt')
    resume.add_argument('--statement')
    preview=commands.add_parser('move-preview');preview.add_argument('project');preview.add_argument('root',type=Path)
    apply=commands.add_parser('move-apply');apply.add_argument('--plan',type=Path,required=True)
    apply.add_argument('--receipt',required=True);apply.add_argument('--statement',required=True)
    apply.add_argument('--operation',required=True)
    for name in ('move-status','move-resume'):
        commands.add_parser(name).add_argument('operation')
    commands.add_parser('repair-preview')
    repair=commands.add_parser('repair-apply');repair.add_argument('--receipt',required=True);repair.add_argument('--operation',required=True)
    connect=commands.add_parser('connect-preview');connect.add_argument('root',type=Path);connect.add_argument('--init-git',action='store_true',help='Preview creating a local Git repository for a first connection')
    connect.add_argument('--git-executable',help='Also preview registering this absolute Git executable for the account')
    apply=commands.add_parser('connect');apply.add_argument('--plan',type=Path,required=True)
    apply.add_argument('--receipt',required=True);apply.add_argument('--statement',required=True);apply.add_argument('--operation',required=True)
    resume=commands.add_parser('connect-resume');resume.add_argument('operation')
    cancel=commands.add_parser('connect-cancel',help='Cancel first Git setup before connection files are applied');cancel.add_argument('operation')
    detach=commands.add_parser('detach-preview');detach.add_argument('project');detach.add_argument('root',type=Path)
    detach=commands.add_parser('detach');detach.add_argument('project');detach.add_argument('root',type=Path)
    detach.add_argument('--receipt',required=True);detach.add_argument('--statement',required=True);detach.add_argument('--operation',required=True)
    resume=commands.add_parser('detach-resume');resume.add_argument('operation')
    # A single command can prepare and activate the signed update when the user
    # has requested an update. An interrupted operation is inspected, not rerun.
    update=commands.add_parser('update');update.add_argument('--operation',default=None)
    inspect=commands.add_parser('update-status');inspect.add_argument('operation')
    resume=commands.add_parser('update-resume');resume.add_argument('operation');resume.add_argument('--receipt',required=True);resume.add_argument('--renewal')
    refresh=commands.add_parser('update-refresh');refresh.add_argument('operation');refresh.add_argument('--receipt',required=True);refresh.add_argument('--renewal',required=True)
    rollback=commands.add_parser('update-rollback-preview');rollback.add_argument('operation');rollback.add_argument('--receipt',required=True)
    rollback=commands.add_parser('update-rollback');rollback.add_argument('operation');rollback.add_argument('--receipt',required=True);rollback.add_argument('--rollback-receipt',required=True)
    return p


def finish(advance,operation):
    # Advance distinct recorded steps; this loop never catches/retries failure.
    for _ in range(128):
        result=advance(operation)
        if result['state']!='pending':return result
    raise RecordError('manager-step-limit')


def run(args,entry):
    entry.lease.check();home=entry.home
    if args.command.startswith('notice-') and args.command not in ('notice-original','notice-detail'):
        from .notice_manager import receiver,send
        if args.command=='notice-send':return send(entry,args.project,args.delivery)
        port=receiver(home)
        if args.command in ('notice-enable','notice-disable'):return port.change(enable=args.command=='notice-enable')
        if args.command=='notice-registration-resume':return port.resume()
        if args.command=='notice-registration-status':return port.inspect()
        if args.command=='notice-identity':
            require(args.receiver_source is not None,'notice-receiver-source-required');return port.identity(args.receiver_source)
        return port.check(port.receiver_identity)
    if args.command in ('notice-original','notice-detail'):
        if args.command=='notice-original':
            require(args.receiver_source is not None,'notice-receiver-source-required')
        if args.receiver_source is not None:
            from .notice_manager import receiver
            receiver(home).identity(args.receiver_source)
        from .notice_routes import NoticeRoutes
        return NoticeRoutes(home).details(args.event,entry,original_only=args.command=='notice-original',
                                          route_digest=args.route_sha256)
    if args.command=='status':
        _,selected=home.slots.selection()
        return dict(state='ready',release=entry.lease.verified.release,projects=len(home.projects()),
                    recovery_available=selected['recovery'] is not None)
    if args.command in ('git-register-preview', 'git-register'):
        from .git_registration import preview_registration, register_git
        if args.command == 'git-register-preview':
            return preview_registration(home, entry.lease, args.executable)
        envelope = decode_canonical(home.files.read(args.plan, 32 * 1024))
        require(type(envelope) is dict and envelope.get('receipt') == args.receipt and
                'plan' in envelope, 'git-registration-review-changed')
        return register_git(home, entry.lease, envelope['plan'], args.receipt, replace=args.replace)
    if args.command.startswith('restore-'):
        from .restore_manager import RestoreManager
        service=RestoreManager(home,lease=entry.lease)
        if args.command=='restore-prepare':return service.prepare(operation=args.operation,archive=args.archive)
        if args.command=='restore-apply':return service.apply(operation=args.operation,receipt=args.receipt)
        if args.command=='restore-resume':return service.resume(operation=args.operation,receipt=args.receipt)
        return service.inspect(args.operation)
    if args.command.startswith('identity-'):
        from .identity_setup import IdentitySetup
        setup=IdentitySetup(home,entry.git(),runtime_lease=entry.lease)
        if args.command=='identity-preview':return setup.preview(args.projects)
        if args.command=='identity-apply':
            value=decode_canonical(home.files.read(args.plan,8*1024*1024))
            require(type(value) is dict and 'plan' in value and value.get('receipt')==args.receipt,
                    'identity-review-changed')
            return setup.start(operation=args.operation,plan=value['plan'],receipt=args.receipt,statement=args.statement)
        return setup.status(args.operation) if args.command=='identity-status' else setup.resume(args.operation)
    if args.command.startswith('git-transition-'):
        from .git_transition import GitTransition
        setup = GitTransition(home, entry.git(), runtime_lease=entry.lease)
        if args.command == 'git-transition-preview':
            from .adapters.git import read_file
            from .binding import Locator
            from .git_transition import MARKER
            owner = Locator.parse(read_file(args.root/MARKER, 16384), kind='plain')
            return setup.preview(owner.project, args.root)
        if args.command == 'git-transition-cancel':
            return setup.resume(args.operation, cancel=True)
        if args.command == 'git-transition-resume-preview':
            return setup.resume(args.operation, preview=True)
        if args.command == 'git-transition-resume':
            require(bool(args.receipt) == bool(args.statement), 'git-transition-review-changed')
            return setup.resume(args.operation, receipt=args.receipt, statement=args.statement)
        value = decode_canonical(home.files.read(args.plan, 8 * 1024 * 1024))
        require(value['receipt'] == args.receipt, 'git-transition-review-changed')
        return setup.start(operation=args.operation, plan=value['plan'], receipt=args.receipt, statement=args.statement)
    if args.command.startswith('move-'):
        from .move_setup import MoveSetup
        setup=MoveSetup(home,entry.git(),runtime_lease=entry.lease)
        if args.command=='move-preview':return setup.preview(args.project,args.root)
        if args.command=='move-apply':
            value=decode_canonical(home.files.read(args.plan,8*1024*1024))
            require(type(value) is dict and value.get('receipt')==args.receipt and 'plan' in value,
                    'connection-move-review-changed')
            return setup.start(operation=args.operation,plan=value['plan'],receipt=args.receipt,statement=args.statement)
        return setup.status(args.operation) if args.command=='move-status' else setup.resume(args.operation)
    if args.command.startswith('rebind'):
        from .restored_setup import RestoredSetup
        setup=RestoredSetup(home,entry.git(),runtime_lease=entry.lease)
        if args.command=='rebind-preview':return setup.preview(args.project,args.root)
        if args.command=='rebind':
            value=decode_canonical(home.files.read(args.plan,8*1024*1024))
            require(type(value) is dict and 'plan' in value and value.get('receipt')==args.receipt,'restore-rebind-review-changed')
            setup.start(operation=args.operation,plan=value['plan'],receipt=args.receipt,statement=args.statement)
        return finish(setup.resume,args.operation)
    if args.command=='update-status':
        from .updates.release import inspect_release
        return inspect_release(home,args.operation)
    if args.command == 'connect-cancel':
        from .first_git import cancel
        return cancel(ProjectSetup(home, runtime_lease=entry.lease), args.operation)
    setup=ProjectSetup(home,entry.git(),runtime_lease=entry.lease)
    if args.command=='connect-preview':return setup.preview(args.root,init_git=args.init_git,git_executable=args.git_executable)
    if args.command=='connect':
        value=decode_canonical(home.files.read(args.plan,8*1024*1024))
        # Accept the exact preview envelope, never an executable command file.
        require(type(value) is dict and 'plan' in value and value.get('receipt')==args.receipt,'connect-review-changed')
        setup.start(operation=args.operation,plan=value['plan'],receipt=args.receipt,statement=args.statement)
        return finish(setup.resume,args.operation)
    if args.command=='connect-resume':return finish(setup.resume,args.operation)
    if args.command=='detach-preview':
        with setup.management():
            authority,store,service,changes=setup.detach_context(args.project,args.root)
            try:return service.preview(changes)
            finally:store.close()
    if args.command=='detach':
        setup.detach_begin(operation=args.operation,project=args.project,root=args.root,receipt=args.receipt,statement=args.statement)
        return finish(setup.detach_resume,args.operation)
    if args.command=='detach-resume':return finish(setup.detach_resume,args.operation)
    require(args.command in ('update','update-resume','update-refresh','update-rollback-preview','update-rollback'),'manager-command-unavailable')
    config=update_configuration(home)
    if args.command in ('update-rollback-preview','update-rollback'):
        release=ReleaseUpdate(home,None,channel=config['channel'])
        if args.command=='update-rollback-preview':return release.rollback_preview(operation=args.operation,receipt=args.receipt)
        return release.rollback(operation=args.operation,receipt=args.receipt,rollback_receipt=args.rollback_receipt)
    fetcher=https_fetcher(metadata_url=config['metadata_url'],target_url=config['target_url'])
    try:
        from .updates.reauthentication import metadata_only
        verifier_fetcher=metadata_only(fetcher,config['metadata_url']) if args.command=='update-refresh' else fetcher
        trust=Trust(home.root/'trust',metadata_url=config['metadata_url'],target_url=config['target_url'],fetcher=verifier_fetcher,files=home.files)
        release=ReleaseUpdate(home,trust,channel=config['channel'])
        operation=args.operation or 'update-'+uuid.uuid4().hex
        if args.command=='update-resume':return release.resume(operation=operation,receipt=args.receipt,**({'renewal':args.renewal} if args.renewal is not None else {}))
        if args.command=='update-refresh':return release.refresh(operation=operation,receipt=args.receipt,renewal=args.renewal)
        preview=release.prepare(operation=operation,target=config['target'])
        return release.apply(operation=operation,receipt=preview['receipt'])
    finally:fetcher.close()


def main(argv=None,*,entry=None):
    argv=list(sys.argv[1:] if argv is None else argv)
    if entry is None and argv and argv[0] in ('bootstrap-connect-repair-prepare','bootstrap-connect-repair-preview','bootstrap-connect-repair-apply','bootstrap-connect-repair-resume'):
        p=argparse.ArgumentParser(prog='colvia connection recovery',allow_abbrev=False)
        p.add_argument('--management-root',required=True,type=Path,action=RuntimeOptionOnce)
        p.add_argument('--bootstrap-stage',required=True,type=Path,action=RuntimeOptionOnce)
        p.add_argument('--bootstrap-manifest-sha256',required=True,action=RuntimeOptionOnce);p.add_argument('--connection',required=True)
        p.add_argument('--release-operation',required=True);p.add_argument('--renewal')
        applying=argv[0] in ('bootstrap-connect-repair-apply','bootstrap-connect-repair-resume')
        if applying:p.add_argument('--operation',required=True);p.add_argument('--receipt',required=True)
        a=p.parse_args(argv[1:])
        try:
            from .updates.connection_repair import bootstrap_connection_repair
            result=bootstrap_connection_repair(a.management_root,a.bootstrap_stage,a.bootstrap_manifest_sha256,
                connection=a.connection,release_operation=a.release_operation,operation=getattr(a,'operation',None),receipt=getattr(a,'receipt',None),
                resume=argv[0]=='bootstrap-connect-repair-resume',prepare=argv[0]=='bootstrap-connect-repair-prepare',renewal=a.renewal)
            print(json.dumps(result,ensure_ascii=False,sort_keys=True));return 0
        except (RecordError,OSError,ValueError,TypeError,KeyError) as exc:
            code=exc.code if isinstance(exc,RecordError) else 'connect-repair-unavailable'
            detail=dict(error=code,message='연결 복구를 완료하지 못했습니다. 기존 기록을 보존했습니다. 같은 명령을 반복하지 말고 복구 상태를 확인해 주세요.')
            if isinstance(exc, ConnectionBoundaryError):
                detail['message'] = failure(code)
                if exc.directory is not None:
                    detail['directory'] = exc.directory
            if isinstance(exc,OSError):detail.update(exception=type(exc).__name__,errno=exc.errno,winerror=getattr(exc,'winerror',None))
            print(json.dumps(detail,ensure_ascii=False));return 2
        except Exception as exc:
            code=trust_failure(exc)
            if code is None:raise
            print(json.dumps(dict(error=code,message='복구 후보의 신뢰를 확인하지 못했습니다. 기존 기록과 설치본은 보존됩니다.'),ensure_ascii=False));return 2
    if entry is None and argv and argv[0] in ('bootstrap-uninstall-preview','bootstrap-uninstall',
                                               'bootstrap-uninstall-resume','bootstrap-uninstall-restore',
                                               'bootstrap-reinstall-resume'):
        command=argv[0].removeprefix('bootstrap-')
        p=argparse.ArgumentParser(prog='colvia installation maintenance',allow_abbrev=False)
        p.add_argument('--management-root',required=True,type=Path,action=RuntimeOptionOnce)
        p.add_argument('--bootstrap-stage',required=True,type=Path,action=RuntimeOptionOnce)
        p.add_argument('--bootstrap-manifest-sha256',required=True,action=RuntimeOptionOnce)
        if command!='reinstall-resume':p.add_argument('--operation',required=True,action=RuntimeOptionOnce)
        if command in ('uninstall','uninstall-resume','uninstall-restore'):
            p.add_argument('--receipt',required=True,action=RuntimeOptionOnce)
        a=p.parse_args(argv[1:])
        try:
            from .updates.installation import bootstrap
            result=bootstrap(a.management_root,a.bootstrap_stage,a.bootstrap_manifest_sha256,
                             maintenance=(command,getattr(a,'operation',None),getattr(a,'receipt',None)))
            print(json.dumps(result,ensure_ascii=False,sort_keys=True));return 0
        except (RecordError,OSError,ValueError,TypeError,KeyError) as exc:
            print(failure(exc.code if isinstance(exc,RecordError) else 'installation-unavailable'));return 2
    if entry is None and argv and argv[0] in ('bootstrap-install-or-update','bootstrap-resume-install','bootstrap-repair-runtime','bootstrap-resume-repair','bootstrap-refresh-install','bootstrap-retry-install','bootstrap-rollback-preview','bootstrap-rollback','bootstrap-install-status','bootstrap-quarantine-preview','bootstrap-replace-install'):
        p=argparse.ArgumentParser(prog='colvia install',allow_abbrev=False)
        p.add_argument('--management-root',required=True,type=Path,action=RuntimeOptionOnce)
        p.add_argument('--bootstrap-stage',required=True,type=Path,action=RuntimeOptionOnce)
        p.add_argument('--bootstrap-manifest-sha256',required=True,action=RuntimeOptionOnce)
        resuming=argv[0]=='bootstrap-resume-install';repairing=argv[0] in ('bootstrap-repair-runtime','bootstrap-resume-repair')
        refreshing=argv[0]=='bootstrap-refresh-install';retrying=argv[0]=='bootstrap-retry-install';inspecting=argv[0]=='bootstrap-install-status'
        quarantining=argv[0] in ('bootstrap-quarantine-preview','bootstrap-replace-install')
        rolling=argv[0] in ('bootstrap-rollback-preview','bootstrap-rollback')
        if resuming or repairing or refreshing or retrying or rolling or quarantining:p.add_argument('--operation',required=True)
        if resuming or refreshing:p.add_argument('--renewal',required=refreshing)
        if refreshing or rolling or argv[0]=='bootstrap-replace-install':p.add_argument('--receipt',required=True)
        if argv[0]=='bootstrap-rollback':p.add_argument('--rollback-receipt',required=True)
        a=p.parse_args(argv[1:])
        try:
            from .updates.installation import bootstrap
            result=bootstrap(a.management_root,a.bootstrap_stage,a.bootstrap_manifest_sha256,
                             resume_operation=a.operation if resuming else None,repair_operation=a.operation if repairing else None,
                             **({'repair_resume':True} if argv[0]=='bootstrap-resume-repair' else {}),
                             **({'renewal':a.renewal} if (resuming or refreshing) and a.renewal is not None else {}),
                             **({'refresh_operation':a.operation,'refresh_receipt':a.receipt} if refreshing else {}),
                             **({'retry_operation':a.operation} if retrying else {}),
                             **({'rollback_operation':a.operation,'release_receipt':a.receipt,'rollback_receipt':getattr(a,'rollback_receipt',None)} if rolling else {}),
                             **({'inspect_initial':True} if inspecting else {}),
                             **({'quarantine_operation':a.operation,'quarantine_receipt':getattr(a,'receipt',None)} if quarantining else {}))
            if refreshing or rolling or inspecting or quarantining:
                print(json.dumps(result,ensure_ascii=False,sort_keys=True));return 0
            print('Colvia 실행환경을 복구했습니다. 기존 기록과 설정은 그대로 유지했습니다.' if repairing else 'Colvia 실행환경을 준비했습니다. 사용할 프로젝트 폴더를 연결해 주세요.');return 0
        except (RecordError,OSError,ValueError,TypeError,KeyError) as exc:
            message=space_message(exc, failure(exc.code if isinstance(exc,RecordError) else 'installation-unavailable'))
            operation=getattr(exc,'operation',getattr(a,'operation',None))
            if operation:message+=' 확인할 실행: '+operation
            print(message);return 2
        except Exception as exc:
            code=trust_failure(exc)
            if code is None:raise
            message=failure(code);operation=getattr(exc,'operation',getattr(a,'operation',None))
            if operation:message+=' 확인할 실행: '+operation
            print(message);return 2
    args=parser(bound=entry is not None).parse_args(argv)
    args.repair=args.repair is True
    if args.command=='update' and args.operation is None:args.operation='update-'+uuid.uuid4().hex
    try:
        pointer=None if entry is not None else dict(slot=args.runtime_slot,manifest_sha256=args.runtime_manifest_sha256)
        if args.repair:
            from .updates.repair import RecoveryManager
            require(args.command in ('repair-preview','repair-apply','update-status'),'recovery-manager-command-only')
            recovery=RecoveryManager(args.management_root,pointer=pointer)
            if args.command=='repair-preview':result=recovery.preview()
            elif args.command=='repair-apply':result=recovery.apply(operation=args.operation,receipt=args.receipt)
            else:result=recovery.home.inspect_update(args.operation)
        else:
            require(args.command not in ('repair-preview','repair-apply'),'explicit-recovery-entry-required')
            if entry is None:
                files=None
                if sys.platform=='win32' and args.receiver_source is not None and args.command in ('notice-identity','notice-detail','notice-original'):
                    from .storage.windows import NoticeReaderFiles
                    files=NoticeReaderFiles()
                entry=ManagedEntry(args.management_root,pointer=pointer,files=files)
            result=run(args,entry)
        if args.command=='git-register-preview' or (args.json and args.command in ('connect-preview','move-preview','git-transition-preview')):
            raw = canonical_bytes(result)
            if hasattr(sys.stdout, 'buffer'):
                sys.stdout.buffer.write(raw)
            else:
                sys.stdout.write(raw.decode('utf-8'))
        elif args.json:print(json.dumps(result,ensure_ascii=False,sort_keys=True))
        elif args.command=='notice-original':
            print(result.get('title') or '맡긴 작업 결과')
            print(result.get('summary') or '맡긴 작업의 실행 결과가 준비되었습니다.')
        elif args.command=='notice-detail':
            from .notice_routes import detail_text
            print(detail_text(result))
        elif args.command=='notice-identity':print(result['app']+' '+result['cls'])
        elif args.command=='notice-registration-status':print('알림 등록 확인: '+result['state']+' — 자동 변경하지 않았습니다. 자세한 값은 --json으로 확인할 수 있습니다.')
        elif args.command=='update-status':print('갱신 상태: '+result['state']+' — 확인할 실행: '+args.operation+'; 재개 정보는 --json으로 확인하세요.')
        elif args.command=='notice-send':print('Colvia 알림을 보냈습니다. 알림을 누르면 해당 작업의 결과를 볼 수 있습니다.' if result['notification']=='emitted' else '알림 전달을 확인하지 못했습니다. 재전송하지 않았으며 결과는 프로젝트 채팅에서 확인할 수 있습니다.')
        elif args.command=='notice-enable':print('Colvia 알림 연결을 준비했습니다. 운영체제에서 알림을 허용해야 배너를 받을 수 있습니다.')
        elif args.command=='notice-disable':print('새 Colvia 알림을 껐습니다. 기존 작업 기록과 알림은 그대로 남습니다.')
        elif args.command=='notice-check':print('현재 설치본의 알림 연결을 확인했습니다. 운영체제의 알림 허용 여부는 별도입니다.')
        elif args.command=='status':print(f"Colvia {result['release']} 준비됨 · 연결된 프로젝트 {result['projects']}개")
        elif args.command=='git-register':
            print('Colvia Git 등록 확인: '+result['version'])
        elif args.command=='connect-preview':
            if result['plan'].get('action') == 'first-connect-git':
                print('연결할 폴더: '+repr(result['plan']['basis']['root']))
                git = result['plan']['git']
                print('Git: '+repr(git['path'])+' · SHA-256 '+git['sha256'])
            print('변경할 파일: '+', '.join(result['files']));print(result['question'])
        elif args.command=='connect-cancel':print('첫 연결 예약을 취소했습니다. 기존 자료와 이미 생성된 Git 저장소·계정 등록은 그대로입니다.')
        elif args.command=='detach-preview':print('Colvia가 추가한 연결과 안내를 제거하고 작업 기록은 보존합니다. 해제할까요?')
        elif args.command=='identity-preview':
            for row in result['plan']['census']:
                if row['selected']:
                    for root in row['roots']:print(repr(root['path']))
            print(result['question'])
        elif args.command in ('identity-apply','identity-status','identity-resume'):
            print(f"연결 재검증: 완료 {len(result['completed'])}개 · 남음 {len(result['remaining'])}개")
        elif args.command == 'git-transition-preview':
            from .presentation import display_path
            print(display_path(result['plan']['root']['path']))
            print(result['question'])
        elif args.command == 'git-transition-cancel':
            print('전환 예약을 취소했습니다. 현재 Git 저장소와 작업 파일은 그대로입니다.')
        elif args.command == 'git-transition-resume-preview':
            from .presentation import display_path
            print(display_path(result['root']))
            changes = result['changes_since_first_review']
            print('첫 확인 뒤 작업 파일 변경: ' + ('있음' if changes['working_files'] else '없음'))
            for path in changes['examples']:
                print('  ' + display_path(path))
            if changes['git_fields']:
                print('Git 변경 항목: ' + ', '.join(changes['git_fields']))
            print('현재 스테이징한 경로 수: ' + str(changes['staged_count']))
            for path in changes['staged_examples']:
                print('  ' + display_path(path))
            print(result['question'])
        elif args.command in ('git-transition-apply', 'git-transition-resume'):
            print('기존 작업 기록을 보존하고 Git 연결로 전환했습니다.')
        elif args.command=='move-preview':
            from .presentation import display_path
            plan=result['plan']
            print('기존 위치 '+display_path(plan['before']['root']['path']))
            print('새 위치 '+display_path(plan['after']['root']['path']))
            print(result['question'])
        elif args.command in ('move-apply','move-status','move-resume'):
            print({'moved':'프로젝트의 새 위치를 확인했습니다.', 'pending':'이동 승인이 기록됐습니다. 같은 실행을 재개할 수 있습니다.',
                   'subsequently-changed':'이동을 완료한 뒤 연결 상태가 달라졌습니다.'}[result['state']])
        elif args.command in ('restore-prepare','rebind-preview'):print(result['question'])
        elif args.command=='restore-apply':print('기록을 복원했습니다. 작업 파일은 변경하지 않았습니다. 이어서 프로젝트 연결을 확인해 주세요.')
        elif args.command=='repair-preview':print(result['question'])
        elif args.command=='repair-apply':print('호환되는 이전 실행기로 복구했습니다. 작업 기록과 설정은 그대로 유지했습니다.')
        elif args.command=='update-rollback-preview':print(json.dumps(result,ensure_ascii=False,sort_keys=True))
        elif args.command=='update-rollback':print('중단된 갱신 파일을 이전 실행기와 일치하도록 복구했습니다. 기록과 설정은 그대로입니다.')
        elif args.command=='update-refresh':print(json.dumps(result,ensure_ascii=False,sort_keys=True))
        elif args.command in ('update','update-resume'):print('이미 최신 Colvia입니다. 기록과 설정을 그대로 유지했습니다.' if result['state']=='current' else 'Colvia를 갱신했습니다. 기록과 설정, 갱신 전 복구본을 보존했습니다.')
        else:print('관리 작업 상태: '+result.get('state','확인됨'))
        return 0
    except (RecordError,OSError,ValueError,TypeError,KeyError) as exc:
        code=exc.code if isinstance(exc,RecordError) else 'manager-access-unavailable'
        message=space_message(exc, failure(code));operation=getattr(args,'operation',None)
        if operation:message+=' 확인할 실행: '+operation
        result=dict(error=code,message=message,operation=operation)
        if isinstance(exc, SpaceError):
            result['diagnostic']=exc.diagnostic
        if isinstance(exc, ConnectionBoundaryError) and exc.directory is not None:
            result['directory'] = exc.directory
            message += ' 확인할 폴더: ' + repr(exc.directory)
        if isinstance(exc,OSError):
            # Numeric OS diagnostics only; exception messages can expose paths.
            result['diagnostic']={k:v for k in ('errno','winerror')
                                  if type(v:=getattr(exc,k,None)) is int}
        print(json.dumps(result,ensure_ascii=False) if args.json else message);return 2

    except Exception as exc:
        code=trust_failure(exc)
        if code is None:raise
        message=failure(code);operation=getattr(args,'operation',None)
        if operation:message+=' 확인할 실행: '+operation
        print(json.dumps(dict(error=code,message=message,operation=operation),ensure_ascii=False) if args.json else message);return 2
