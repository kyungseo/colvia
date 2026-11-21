"""Explicit source-development entry; does not replace an installed launcher."""
import argparse,json,sys,uuid,time
from pathlib import Path

from .adapters.git import Git,discover,read_file
from .binding import Locator
from .guide_topics import TOPIC_NAMES
from .codec import RecordError,require
from .planning import Planning,page_heads
from .presentation import human,failure
from .records import head_summary
from .storage.authority import Authority
from .work import WorkService
from .workspace import LocalWorkspace


def read_locator(root,git):
    topology=discover(Path(root),git)
    path=Path(topology.common.path)/'colvia/connection.json' if topology.kind=='git' else Path(topology.root.path)/'.colvia-link.json'
    return Locator.parse(read_file(path,16384),kind=topology.kind)


class ExactParser(argparse.ArgumentParser):
    def __init__(self,*args,**kwargs):
        kwargs['allow_abbrev']=False;super().__init__(*args,**kwargs)

def parser(*,managed=False):
    p=ExactParser(prog='colvia' if managed else 'colvia-source',description='Work and project records.' if managed else 'Unactivated source foundation; installed launcher remains separate.')
    if managed:
        p.add_argument('--finish-plain-work', action='store_true', help='Finish existing ordinary Work after running git init')
        p.add_argument('--root',default=None,help='Project workspace; authority is resolved from its verified connection')
    else:
        p.add_argument('--source-development',action='store_true',required=True)
        for option in ('authority','project','workspace','root'):p.add_argument('--'+option,required=True)
        p.add_argument('--git',help='Qualified absolute Git executable; no PATH fallback')
    p.add_argument('--json',action='store_true');p.add_argument('--operation',default=None)
    sub=p.add_subparsers(dest='group',required=True)
    if managed:
        guide = sub.add_parser('guide', help='Read the startup guide or one verified topic without opening project records')
        guide.add_argument('topics', nargs='*', metavar='TOPIC', help='One of: ' + ', '.join(TOPIC_NAMES))
        manager=sub.add_parser('manage',add_help=False,help='Use this verified installation manager')
        manager.add_argument('--help',action='store_true',dest='manager_help');manager.add_argument('--json',action='store_true',dest='manager_json')
        manager.add_argument('arguments',nargs=argparse.REMAINDER)
    project = sub.add_parser('project').add_subparsers(dest='action', required=True)
    status = project.add_parser('status', help='Show the next action for current Work, read-only')
    status.add_argument('--limit', type=int, default=20)
    status.add_argument('--cursor')
    dependency = sub.add_parser('dependency').add_subparsers(dest='action', required=True)
    for action in ('show','history'):
        details = dependency.add_parser(action)
        details.add_argument('work')
        details.add_argument('--cursor')
    for action in ('preview', 'apply'):
        change = dependency.add_parser(action)
        change.add_argument('work', help='Work that needs the result')
        change.add_argument('--remove', metavar='PREVIOUS_PREREQUISITE')
        change.add_argument('--add', metavar='NEW_PREREQUISITE')
        if action == 'apply':
            change.add_argument('--basis', required=True)
            change.add_argument('--request', required=True)
            change.add_argument('--recorder', required=True, choices=('agent','operator'))
    operation=sub.add_parser('operation');operation.add_argument('identifier')
    configuration=sub.add_parser('configuration').add_subparsers(dest='action',required=True)
    configuration.add_parser('show')
    for action in ('preview','apply'):
        command=configuration.add_parser(action);command.add_argument('--enable',action='append',default=[])
        if action=='apply':
            command.add_argument('--receipt',required=True);command.add_argument('--statement',required=True)
    backup=sub.add_parser('backup').add_subparsers(dest='action',required=True)
    backup.add_parser('status')
    exported=backup.add_parser('export');exported.add_argument('--destination',required=True);exported.add_argument('--scratch',required=True)

    integration=sub.add_parser('git-integration').add_subparsers(dest='action',required=True)
    for action in ('prepare','show','apply','recover'):
        command=integration.add_parser(action);command.add_argument('integration');command.add_argument('--scratch',required=True)
        if action=='prepare':
            command.add_argument('--work',action='append',required=True);command.add_argument('--message',required=True)
            for name in ('author-name','author-email','author-date'):command.add_argument('--'+name,required=True)
        if action=='apply':command.add_argument('--receipt',required=True)
        if action in ('apply','recover'):command.add_argument('--statement',required=True)

    ordinary=sub.add_parser('ordinary').add_subparsers(dest='action',required=True)
    history = ordinary.add_parser('history', help='Read decisions and context for one Work, newest first')
    history.add_argument('work')
    history.add_argument('--limit', type=int, default=20)
    history.add_argument('--cursor')
    plan=ordinary.add_parser('plan');plan.add_argument('work')
    for name in ('title','goal'):plan.add_argument('--'+name,required=True)
    for name in ('path','check'):plan.add_argument('--'+name,action='append',required=True)
    plan.add_argument('--exclude',action='append',default=[]);plan.add_argument('--replace-receipt')
    for name in ('approve','accept','revise'):
        command=ordinary.add_parser(name);command.add_argument('work');command.add_argument('--receipt',required=True);command.add_argument('--statement',required=True)
        if name == 'approve':
            command.add_argument('--start', action='store_true',
                                 help='Start only when the user also approved carrying out this exact plan.')
    for name in ('start','review','view','plan-review'):
        ordinary.add_parser(name).add_argument('work')
    for action in ('scope-preview','scope-apply'):
        command = ordinary.add_parser(action)
        command.add_argument('work')
        for field in ('edit','create','check'):
            command.add_argument('--'+field, action='append', default=[])
        command.add_argument('--reason', required=True)
        if action == 'scope-apply':
            command.add_argument('--receipt', required=True)
            command.add_argument('--statement', required=True)
    for name in ('lifecycle-preview','lifecycle-apply'):
        change=ordinary.add_parser(name)
        change.add_argument('work')
        change.add_argument('decision',choices=('pause','resume','discard','replace'))
        change.add_argument('--reason',required=True)
        change.add_argument('--next-action',default='')
        change.add_argument('--target',default='')
        if name=='lifecycle-apply':
            change.add_argument('--receipt',required=True)
    progress=ordinary.add_parser('progress', help='Save a progress note before first submission')
    progress.add_argument('work')
    for name in ('receipt','done','checked','remaining','next-action'):
        progress.add_argument('--'+name, required=True)
    submit=ordinary.add_parser('submit');submit.add_argument('work');submit.add_argument('--summary',required=True)
    for name in ('passed','failed','unavailable'):submit.add_argument('--'+name,action='append',default=[],metavar='CHECK::DETAIL')
    content=ordinary.add_parser('content');content.add_argument('work');content.add_argument('path');content.add_argument('--revision',type=int)
    archive=ordinary.add_parser('archive');archive.add_argument('work');archive.add_argument('--restore',action='store_true')
    listed=ordinary.add_parser('list');listed.add_argument('--limit',type=int,default=20);listed.add_argument('--cursor')
    listed.add_argument('--list-mode',choices=('current','archived','all'))
    composition=sub.add_parser('composition').add_subparsers(dest='action',required=True)
    declare=composition.add_parser('declare');declare.add_argument('work')
    declare.add_argument('--child',action='append',required=True);declare.add_argument('--document',required=True)
    declare.add_argument('--check',action='append',required=True);declare.add_argument('--statement',required=True)
    preview=composition.add_parser('rebind-preview');preview.add_argument('work');preview.add_argument('--child',action='append')
    rebind=composition.add_parser('rebind');rebind.add_argument('work');rebind.add_argument('--receipt',required=True);rebind.add_argument('--statement',required=True);rebind.add_argument('--child',action='append')
    delivery=sub.add_parser('delivery').add_subparsers(dest='action',required=True)
    request=delivery.add_parser('prepare');request.add_argument('delivery');request.add_argument('--work',required=True)
    request.add_argument('--step',choices=('inspect','submit','execute') if managed else ('inspect','submit'),required=True);request.add_argument('--seconds',type=int,required=True)
    if managed:request.add_argument('--run')
    request.add_argument('--summary');request.add_argument('--receiver');request.add_argument('--receiver-version',type=int)
    for name in ('passed','failed','unavailable'):request.add_argument('--'+name,action='append',default=[],metavar='CHECK::DETAIL')
    for name in ('preview','view','run','details'):delivery.add_parser(name).add_argument('delivery')
    if managed:
        delivery.add_parser('notify').add_argument('delivery')
        delivery.add_parser('finish-execution').add_argument('delivery')
    start_delivery=delivery.add_parser('start');start_delivery.add_argument('delivery');start_delivery.add_argument('--receipt',required=True);start_delivery.add_argument('--statement',required=True)
    stop_delivery=delivery.add_parser('cancel');stop_delivery.add_argument('delivery');stop_delivery.add_argument('--statement',required=True)
    execution=sub.add_parser('execution').add_subparsers(dest='action',required=True)
    if managed:
        execution.add_parser('resolve-preview').add_argument('run')
        resolve_execution=execution.add_parser('resolve');resolve_execution.add_argument('run');resolve_execution.add_argument('--receipt',required=True);resolve_execution.add_argument('--statement',required=True)
        execution.add_parser('readiness',help='Inspect document assets without opening project records or starting execution')
        prepared=execution.add_parser('prepare');prepared.add_argument('run');prepared.add_argument('--request',required=True)
        start=execution.add_parser('start');start.add_argument('run');start.add_argument('--receipt',required=True);start.add_argument('--statement',required=True)
    execution.add_parser('view').add_argument('run')
    cancel_execution=execution.add_parser('cancel');cancel_execution.add_argument('run')
    worker=sub.add_parser('worker');worker.add_argument('--destination',required=True)
    workers=worker.add_subparsers(dest='action',required=True)
    prepare=workers.add_parser('prepare');prepare.add_argument('application');prepare.add_argument('--work',required=True)
    for name in ('preview','view','resume','cancel'):workers.add_parser(name).add_argument('application')
    execute=workers.add_parser('execute');execute.add_argument('application');execute.add_argument('--receipt',required=True)
    execute.add_argument('--statement',required=True);execute.add_argument('--actor',default='owner');execute.add_argument('--authority-kind',choices=('human','delegated'),default='human')
    grant=workers.add_parser('grant');grant.add_argument('work');grant.add_argument('--owner',required=True);grant.add_argument('--delegate',required=True)
    grant.add_argument('--statement',required=True);grant.add_argument('--revoke',action='store_true')
    candidate=sub.add_parser('candidate').add_subparsers(dest='action',required=True)
    save=candidate.add_parser('save');save.add_argument('candidate');save.add_argument('--title',required=True);save.add_argument('--reason',required=True);save.add_argument('--work');save.add_argument('--dismiss',action='store_true')
    listed=candidate.add_parser('list');listed.add_argument('--limit',type=int,default=20);listed.add_argument('--cursor')
    from .candidate_priority import LEVELS
    for name in ('priority-preview', 'priority-set'):
        change = candidate.add_parser(name)
        change.add_argument('candidate')
        change.add_argument('level', choices=LEVELS)
        if name == 'priority-set':
            change.add_argument('--basis', required=True)
            change.add_argument('--request', required=True)
            change.add_argument('--recorder', required=True, choices=('agent', 'operator'))
            change.add_argument('--reason')
    for name in ('priority-history', 'ranked'):
        query = candidate.add_parser(name)
        if name == 'priority-history':
            query.add_argument('candidate')
        query.add_argument('--limit', type=int, default=20)
        query.add_argument('--cursor')
    follow=sub.add_parser('followup');follow.add_argument('work');follow.add_argument('--choice',choices=('candidate','work','none','undecided'));follow.add_argument('--target');follow.add_argument('--statement')
    return p


def effect_authority(args,authority):
    if authority is not None:return authority.root
    # Source-only direct-dispatch fixtures retain their explicit authority. A
    # managed parser never supplies this option and must use its resolved object.
    require(getattr(args,'source_development',False),'effects-authority-required')
    return Path(args.authority)


def dispatch(args,store,workspace,authority=None,*,available_features=None,display=False):
    if args.group == 'project' and args.action == 'status':
        from .project_status import project_status
        return project_status(store, workspace.workspace, limit=args.limit, cursor=args.cursor)
    if args.group=='operation':
        value=store.operation_result(args.identifier)
        return dict(operation=args.identifier,recorded=value is not None,
                    message='기록에 반영된 실행입니다. 작업 상태를 확인해 주세요.' if value is not None else '기록된 완료를 찾지 못했습니다. 외부 효과 여부를 확인하기 전에는 재시도하지 마세요.')
    service=WorkService(store,workspace);planning=Planning(store)
    operation=args.operation or 'op-'+uuid.uuid4().hex
    if args.group == 'dependency':
        from . import work_dependencies
        if args.action == 'history':
            return work_dependencies.history(store,args.work,parse_cursor(args.cursor))
        if args.action == 'show':
            return work_dependencies.show(store,args.work,parse_cursor(args.cursor))
        if args.action == 'preview':
            return work_dependencies.preview(store,args.work,args.remove,args.add)
        return work_dependencies.apply(store,args.work,args.remove,args.add,basis=args.basis,
                                       request=args.request,recorder=args.recorder,operation=operation)
    if args.group=='git-integration':
        from .git_integration import GitIntegration
        from .platforms.git_port import integration_port
        require(workspace.git is not None,'git-prerequisite-required')
        port=integration_port(workspace.root,Path(args.scratch),workspace.git,create=args.action=='prepare')
        integration=GitIntegration(store,workspace,port)
        if args.action=='prepare':return integration.prepare(operation=args.integration,works=args.work,message=args.message,
            identity=dict(name=args.author_name,email=args.author_email,date=args.author_date))
        if args.action=='show':return integration.preview(args.integration)
        if args.action=='apply':return integration.apply(args.integration,receipt=args.receipt,statement=args.statement)
        return integration.recover(args.integration,statement=args.statement)
    if args.group=='configuration':
        from .configuration import Configuration,enabled,OPTIONAL
        config=Configuration(store,available=OPTIONAL if available_features is None else available_features)
        if args.action=='show':return dict(enabled=sorted(enabled(store)),history_preserved=True)
        features=sorted(set(args.enable))
        if args.action=='preview':return config.preview(features)
        return config.apply(operation=operation,features=features,receipt=args.receipt,statement=args.statement)
    if args.group=='backup':
        from .backup_service import export_backup,backup_status
        from .graph import AuditBudget
        from .records import application_registry
        require(authority is not None,'backup-authority-required')
        if args.action=='status':return backup_status(authority)
        return export_backup(authority,destination=Path(args.destination),scratch=Path(args.scratch),operation=operation,
            graph_budget=AuditBudget(100000,1000000,4*1024**3),registry=application_registry())
    if args.group=='ordinary':
        action=args.action
        if action == 'history':
            from .work_history import history
            return history(store, args.work, limit=args.limit, cursor=parse_cursor(args.cursor))
        if action=='plan':return service.plan(operation=operation,work=args.work,title=args.title,goal=args.goal,scope=args.path,checks=args.check,excludes=args.exclude,replace_receipt=args.replace_receipt)
        if action == 'approve':
            return service.approve(operation=operation, work=args.work, receipt=args.receipt,
                                   statement=args.statement, start=args.start)
        if action in ('accept','revise'):return getattr(service,action)(operation=operation,work=args.work,receipt=args.receipt,statement=args.statement)
        if action in ('scope-preview','scope-apply'):
            from . import scope_addition
            delta = dict(edit=args.edit, create=args.create, checks=args.check, reason=args.reason)
            if action == 'scope-preview':
                return scope_addition.review(service, args.work, **delta)[0]
            return scope_addition.apply(service, args.work, operation, **delta,
                                       receipt=args.receipt, statement=args.statement)
        if action in ('lifecycle-preview','lifecycle-apply'):
            from . import work_lifecycle
            inputs=(service,args.work,args.decision,args.reason,args.next_action,args.target)
            if action=='lifecycle-preview':
                return work_lifecycle.proposal(*inputs)[0]
            return work_lifecycle.apply(*inputs,args.receipt,operation)
        if action=='progress':
            from .progress import NOTE_FIELDS, save
            return save(service, args.work, operation, args.receipt, {key:getattr(args,key) for key in NOTE_FIELDS})
        if action=='start':return service.start(operation=operation,work=args.work)
        if action=='view' and display:
            root=store.root().ref
            value=service.view(args.work)
            detail=planning.followup(args.work,display=True)
            require(store.root().ref==root,'followup-view-changed')
            return dict(work_view=value,followup_detail=detail)
        if action in ('review','view','plan-review'):return getattr(service,action.replace('-','_'))(args.work)
        if action=='content':return service.result_content(args.work,args.path,revision=args.revision)
        if action=='archive':return service.archive(operation=operation,work=args.work,archived=not args.restore)
        if action=='submit':
            checks=[]
            for status in ('passed','failed','unavailable'):
                for item in getattr(args,status):
                    parts=item.split('::',1);require(len(parts)==2 and all(parts),'invalid-check-report')
                    checks.append(dict(name=parts[0],status=status,detail=parts[1]))
            return service.submit(operation=operation,work=args.work,summary=args.summary,checks=checks)
        root=store.root().ref
        mode=args.list_mode or ('current' if display else 'all')
        values,cursor=page_heads(store,'work:',limit=args.limit,cursor=parse_cursor(args.cursor),mode=mode)
        items=[]
        for key,ref in values:
            head,_,_,_=head_summary(ref,store.load)
            work=head.payload['work']
            item=dict(work=work,title=head.payload['title'],state=head.payload['phase'],workspace=head.payload['workspace'],archived=head.payload['archived'])
            if display:
                detail=planning.followup(work,display=True,source_head=ref)
                if detail['recorded']:item['followup_detail']=detail
            items.append(item)
        require(store.root().ref==root,'list-changed')
        return dict(items=items,next=cursor,**({'list_mode':mode} if mode!='all' else {}))
    if args.group=='execution':
        from .execution.journal import ExecutionJournal
        journal=ExecutionJournal(service)
        if args.action=='view':return journal.status(args.run)
        return journal.cancel(operation=operation,run=args.run,reason='cancelled')
    if args.group=='delivery':
        from .delivery.service import DeliveryService,notice_key
        from .delivery.notices import Notices
        delivery=DeliveryService(service)
        if args.action=='prepare':
            require(0<args.seconds<=86400,'delivery-request-bound')
            require((args.receiver is None)==(args.receiver_version is None),'delivery-receiver-shape')
            checks=[]
            for status in ('passed','failed','unavailable'):
                for item in getattr(args,status):
                    parts=item.split('::',1);require(len(parts)==2 and all(parts),'invalid-check-report')
                    checks.append(dict(name=parts[0],status=status,detail=parts[1]))
            require(args.step=='submit' or not checks,'delivery-unexpected-input')
            grant=None
            if args.step=='execute':
                from .execution.journal import prepared_key
                require(getattr(args,'run',None) is not None,'execution-grant-required')
                grant=store.head(prepared_key(args.run));require(grant is not None,'execution-grant-required')
            else:require(getattr(args,'run',None) is None,'delivery-unexpected-input')
            return delivery.prepare(operation=operation,delivery=args.delivery,work=args.work,action=args.step,
                deadline_ns=time.time_ns()+args.seconds*10**9,grant=grant,summary=args.summary,checks=checks if args.step=='submit' else None,
                receiver=None if args.receiver is None else dict(id=args.receiver,version=args.receiver_version))
        if args.action=='start':return delivery.start(operation=operation,delivery=args.delivery,receipt=args.receipt,statement=args.statement)
        if args.action=='cancel':return delivery.cancel(operation=operation,delivery=args.delivery,statement=args.statement)
        if args.action=='preview':return delivery.preview(args.delivery)
        if args.action=='view':return delivery.status(args.delivery)
        if args.action=='details':return Notices(delivery).details(args.delivery,project=store.project,instance=store.instance,event_ref=store.head(notice_key(args.delivery)))
        state,request=delivery.read(args.delivery)
        if state.payload['phase'] in ('finished','cancelled','failed'):return delivery.status(args.delivery)
        if request.payload['action']=='inspect':return delivery.inspect(operation=operation,delivery=args.delivery)
        require(request.payload['action']=='submit','execution-qualified-runtime-required')
        from .platforms.effects_port import effects as native_effects
        effects=native_effects(workspace.root,effect_authority(args,authority))
        with effects.exclusion():
            if state.payload['phase']=='queued':delivery.claim(operation=operation+'-claim',delivery=args.delivery,effects=effects)
            if delivery.status(args.delivery)['cancel_requested']:return delivery.cancel_unstarted(operation=operation,delivery=args.delivery,effects=effects)
            return delivery.submit(operation=operation,delivery=args.delivery,effects=effects)
    if args.group=='composition':
        from .composition import CompositionService
        composition=CompositionService(service)
        if args.action=='declare':return composition.declare(operation=operation,parent=args.work,children=args.child,document=args.document,checks=args.check,statement=args.statement)
        if args.action=='rebind-preview':return composition.rebind_preview(args.work,args.child)
        return composition.rebind(operation=operation,parent=args.work,receipt=args.receipt,statement=args.statement,children=args.child)
    if args.group=='worker':
        from .worker import WorkerService
        _,registration,_=workspace.connections.workspace(args.destination)
        target=LocalWorkspace(store,Path(registration.root.path),args.destination,git=workspace.git,
            locator_reader=lambda:read_locator(registration.root.path,workspace.git))
        worker=WorkerService(service,target,authority=effect_authority(args,authority))
        if args.action=='grant':return worker.grant(operation=operation,work=args.work,owner=args.owner,delegate=args.delegate,statement=args.statement,revoke=args.revoke)
        if args.action=='prepare':return worker.prepare(operation=operation,application=args.application,work=args.work)
        if args.action in ('preview','view'):return getattr(worker,args.action)(args.application)
        if args.action=='execute':return worker.execute(operation=operation,application=args.application,receipt=args.receipt,statement=args.statement,actor=args.actor,authority=args.authority_kind)
        return getattr(worker,args.action)(operation=operation,application=args.application)
    if args.group=='candidate':
        if args.action=='list':return planning.candidates(limit=args.limit,cursor=parse_cursor(args.cursor),display=display)
        from . import candidate_priority
        if args.action == 'priority-preview':
            return candidate_priority.preview(store, args.candidate, args.level)[0]
        if args.action == 'priority-set':
            return candidate_priority.apply(store, args.candidate, args.level, basis=args.basis,
                                            request=args.request, reason=args.reason,
                                            recorder=args.recorder, operation=operation)
        if args.action == 'priority-history':
            return candidate_priority.history(store, args.candidate, limit=args.limit, cursor=parse_cursor(args.cursor))
        if args.action == 'ranked':
            return candidate_priority.ranked(planning, limit=args.limit, cursor=parse_cursor(args.cursor), display=display)
        from .planning import candidate_key
        return planning.save_candidate(operation=operation,candidate=args.candidate,title=args.title,reason=args.reason,
            work=args.work,state='dismissed' if args.dismiss else 'open',expected=store.head(candidate_key(args.candidate)))
    if args.choice is None:
        if not display:return planning.followup(args.work)
        root=store.root().ref
        detail=planning.followup(args.work,display=True)
        require(store.root().ref==root,'followup-view-changed')
        return dict(followup_detail=detail)
    require(args.statement is not None,'followup-statement-required')
    from .planning import followup_key
    return planning.choose_followup(operation=operation,work=args.work,choice=args.choice,target=args.target,statement=args.statement,expected=store.head(followup_key(args.work)))


def parse_cursor(value):
    if value is None:return None
    try:return json.loads(value)
    except (ValueError,TypeError):raise RecordError('list-changed-or-invalid-cursor')


def command_readonly(args):
    if args.group == 'dependency':
        return args.action in ('show','history','preview')
    if args.group == 'project' and args.action == 'status':
        return True
    return (args.group=='git-integration' and args.action=='show') or args.group in ('operation','backup') or (args.group=='configuration' and args.action in ('show','preview')) or (args.group=='delivery' and args.action in ('view','preview','details')) or (args.group=='execution' and args.action in ('view','resolve-preview')) or (args.group=='composition' and args.action=='rebind-preview') or (args.group=='worker' and args.action in ('view','preview')) or (args.group=='ordinary' and args.action in ('view','review','plan-review','list','content','history','scope-preview','lifecycle-preview')) or (args.group=='candidate' and args.action in ('list','ranked','priority-preview','priority-history')) or (args.group=='followup' and args.choice is None)


def main(argv=None,*,entry=None):
    command_parser = parser(managed=entry is not None)
    args, extras = command_parser.parse_known_args(argv)
    if extras and args.group != 'guide':
        command_parser.error('unrecognized arguments: ' + ' '.join(extras))
    store = None
    args.operation=args.operation or 'op-'+uuid.uuid4().hex
    try:
        if getattr(args, 'finish_plain_work', False):
            from .external_init import finish
            value = finish(entry, args)
            print(json.dumps(value, ensure_ascii=False, sort_keys=True) if args.json else human(value))
            return 0
        if args.group=='guide':
            require(not extras and len(args.topics) <= 1, 'invalid-guide-topic')
            topic = args.topics[0] if args.topics else None
            value = entry.guide(topic)
            print(json.dumps(dict(guide=value),ensure_ascii=False) if args.json else value)
            return 0
        if entry is not None and args.group=='execution' and args.action=='readiness':
            value=entry.document_execution_readiness()
            print(json.dumps(value,ensure_ascii=False,sort_keys=True) if args.json else human(value))
            return 0
        if args.group=='manage':
            from .manager_entry import main as manager
            return manager((['--help'] if args.manager_help else [])+(['--json'] if args.json or args.manager_json else [])+args.arguments,entry=entry)
        if entry is not None and args.group=='execution' and args.action in ('prepare','start'):
            entry.require_document_execution()
        if entry is not None and args.group=='delivery' and args.action=='prepare' and args.step=='execute':
            entry.require_document_execution()
        available_features=None
        if entry is not None and args.root is None:args.root=str(Path.cwd())
        readonly=command_readonly(args)
        if entry is None:
            authority=Authority(Path(args.authority),project=args.project)
            store=authority.store(readonly=readonly)
            git=Git(Path(args.git)) if args.git else None
            def locator_reader():return read_locator(args.root,git)
            workspace=LocalWorkspace(store,Path(args.root),args.workspace,git=git,locator_reader=locator_reader)
        else:
            authority,store,workspace=entry.workspace(Path(args.root),readonly=readonly)
        if entry is not None and args.group=='configuration':
            from .configuration import enabled
            current=enabled(store)
            # Reading or removing retained choices must not depend on a healthy
            # optional runtime. New choices still require verified availability.
            available_features=current
            if args.action!='show' and set(args.enable)-current:
                available_features=current|entry.optional_features()
        if entry is not None and args.group=='execution' and args.action in ('resolve-preview','resolve'):
            value=entry.document_resolution(args,store,workspace,authority)
        elif entry is not None and args.group=='delivery' and args.action=='finish-execution':
            value=entry.finish_document_delivery(args,store,workspace,authority)
        elif args.group=='delivery' and args.action=='notify':
            from .notice_manager import send
            project=store.project;store.close();store=None
            value=send(entry,project,args.delivery)
        elif entry is not None and args.group=='execution' and args.action in ('prepare','start'):
            value=entry.document_execution(args,store,workspace,authority)
        elif entry is not None and args.group=='delivery' and args.action=='run':
            from .delivery.service import DeliveryService
            request=DeliveryService(WorkService(store,workspace)).read(args.delivery)[1]
            if request.payload['action']=='execute':value=entry.run_document_delivery(args,store,workspace,authority)
            else:value=dispatch(args,store,workspace,authority,available_features=available_features)
        else:value=dispatch(args,store,workspace,authority,available_features=available_features,display=not args.json)
        print(json.dumps(value,ensure_ascii=False,sort_keys=True) if args.json else human(value))
        return 0
    except (RecordError,OSError,ValueError,TypeError) as exc:
        code=exc.code if isinstance(exc,RecordError) else ('invalid-command-input' if isinstance(exc,(ValueError,TypeError)) else 'access-denied' if isinstance(exc,PermissionError) else 'workspace-access-unavailable')
        if entry is not None and args.group=='execution' and args.action=='readiness' and isinstance(exc,OSError) and not isinstance(exc,PermissionError):code='document-assets-inspection-failed'
        if not isinstance(exc,(RecordError,PermissionError)) and ((args.group=='execution' and args.action in ('start','resolve')) or (args.group=='delivery' and args.action in ('run','finish-execution'))):code=args.group+'-outcome-unknown'
        from .presentation import credential_finding_detail, display_path
        value=dict(error=code,message=failure(code))
        from .scope_addition import PathRefusal
        if isinstance(exc, PathRefusal):
            value['path'] = exc.path
            value['message'] += ' · ' + display_path(exc.path)
        from .credentials import GitContentRefusal
        if isinstance(exc, GitContentRefusal):
            value['finding'] = exc.finding
            value['message'] += f" ({credential_finding_detail(exc.finding)})"
        for name in ('directory','workspace','preparation_state'):
            if getattr(exc,name,None) is not None:value[name]=getattr(exc,name)
        if value.get('directory') is not None:
            value['message']+=' 확인할 폴더: '+display_path(value['directory'])
        if value.get('workspace') is not None:
            value['message']+=' 실행한 폴더: '+display_path(value['workspace'])
        if value.get('preparation_state')=='published':
            value['message']+=' 이 요청의 저장은 확인됐습니다. 같은 요청을 반복하지 말고 현재 작업 상태를 확인해 주세요.'
        if value.get('preparation_state')=='unconfirmed':
            value['message']+=' 준비 기록의 종료 상태는 확인되지 않았습니다. 기록을 보존하고 진단해 주세요.'
        from .storage.sqlite import StorageError
        if isinstance(exc,StorageError):value['storage_diagnostic']=dict(exc.diagnostic)
        from .rework import SubmissionBlocked
        if isinstance(exc,SubmissionBlocked):value["details"]=exc.details
        if args.group=='worker' and getattr(args,'application',None):
            value['application']=args.application
            if store is not None:
                try:
                    from .worker import application_key
                    from .codec import decode_envelope
                    selected=store.head(application_key(args.application))
                    value['pending']=selected is not None and selected.kind=='worker.effect' and decode_envelope(selected,store.load(selected)).payload['state']=='pending'
                except (RecordError,OSError):value['pending']=None
                if value['pending']:value['message']='이 적용 요청이 아직 끝나지 않았습니다. '+value['message']
            value['recovery_command']='worker --destination '+args.destination+' view '+args.application
            value['recovery_context']=('Use the same connected project folder and managed launcher.' if entry is not None else 'Use the same authority, project, source workspace, source root and Git options.')
            value['message']+=' 재실행 전에 적용 현황을 확인하세요: '+value['recovery_command']
        elif args.group=='execution' and getattr(args,'run',None):
            value['recovery_command']='execution view '+args.run
            value['message']+=' 같은 실행을 반복하지 말고 상태를 확인하세요: '+value['recovery_command']
        elif args.group=='delivery' and args.action in ('run','finish-execution'):
            value['recovery_command']='delivery view '+args.delivery
            value['message']+=' 전달 상태를 확인하세요: '+value['recovery_command']+'; 아직 진행 중인 전달의 시작 전 종료 또는 닫힌 실행은 delivery finish-execution '+args.delivery+'로 정리할 수 있습니다.'
        elif 'unknown' in code:
            value['operation']=args.operation;value['message']+=' 확인할 실행: '+args.operation
        print(json.dumps(value,ensure_ascii=False) if args.json else human(value))
        return 2
    except Exception:
        # An unexpected failure may occur after publication. Never report rollback
        # or repeat the writer automatically, and do not dump internals by default.
        if entry is not None and args.group=='execution' and args.action=='readiness':
            value=dict(error='document-assets-inspection-failed',message=failure('document-assets-inspection-failed'))
        elif args.group=='worker' and getattr(args,'application',None):
            value=dict(error='command-outcome-unknown',application=args.application,recovery_command='worker --destination '+args.destination+' view '+args.application,
                message='적용 결과를 확정하지 못했습니다. 같은 요청을 반복하지 말고 적용 현황을 확인하세요: worker --destination '+args.destination+' view '+args.application)
        else:
            value=dict(error='command-outcome-unknown',operation=args.operation,
                       message='처리를 확정하지 못했습니다. 재실행 전에 상태와 실행 기록을 확인해 주세요. 확인할 실행: '+args.operation)
        print(json.dumps(value,ensure_ascii=False) if args.json else human(value))
        return 2
    finally:
        if store is not None:store.close()
