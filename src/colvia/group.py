"""Independent member plans and one human acceptance/application decision."""
from pathlib import Path
from types import SimpleNamespace
from uuid import uuid4
import sys
from .codec import require, RecordError, decode_canonical, ObjectRef
from .records import record, link, head_summary, encode_observation, text
from .graph import validate_closure
from .maps import build_map, read_map
from .tree import build_tree, read_tree
from .connection import PROJECT_KEY, workspace_key
from .effects import guard, PENDING
from .work import WorkService, work_key
from .worker import WorkerService
from .worker_state import require_initial
from .storage.sqlite import _token, fresh_view_reads, reuse_operation_reads
from . import group_records as gr

ACTIVATION='group-activation'
ACTIVATION_V2='group-activation-v2'
CURRENT_VERSION=2

def activation_key(version):
    return {1: ACTIVATION, 2: ACTIVATION_V2, gr.WINDOWS_GROUP_VERSION: 'group-activation-v3'}[version]


class GroupService:
    def __init__(self,store,destination,*,authority,lifecycle_authority=None,port_factory=None,windows_runner=None):
        self.store=store; self.destination=destination; self.authority=Path(authority)
        self.lifecycle_authority=lifecycle_authority
        self.windows_runner=windows_runner
        self.work=WorkService(store,destination)
        self.native=WorkerService(self.work,destination,authority=self.authority,port_factory=port_factory)

    def _object(self,ref,load=None): return self.work._object(ref,load)

    def _source(self,workspace):
        from .workspace import LocalWorkspace
        from .cli import read_locator
        _,registration,_=self.destination.connections.workspace(workspace)
        root=Path(registration.root.path)
        return WorkService(self.store,LocalWorkspace(self.store,root,workspace,git=self.destination.git,
                           locator_reader=lambda:read_locator(root,self.destination.git)))

    def _port(self, *, version=CURRENT_VERSION):
        if version == gr.WINDOWS_GROUP_VERSION:
            from .platforms.effects_port import effects
            from .platforms.windows_architecture import native_x64
            require(native_x64(), 'group-platform-unqualified')
            if self.native.port_factory is effects:
                return effects(self.destination.root,self.authority,grouped=True)
        else:
            require(sys.platform == 'darwin', 'group-platform-unqualified')
        return self.native.port_factory(self.destination.root,self.authority)

    def _receipt(self,action,group,ref): return self.work._receipt('group-'+action,group,ref)

    def _selected(self,group):
        ref=self.store.head(gr.key(group)); require(ref is not None,'group-not-found')
        require(gr.plan_for(ref,self.store.load).payload['destination']==self.destination.workspace,'group-wrong-destination')
        return self._object(ref)

    def _live_plan(self,plan,view):
        require(plan.payload['destination']==self.destination.workspace,'group-wrong-destination')
        baseline=self._object(link(plan,'baseline'),view)
        require(view.head(workspace_key(self.destination.workspace))==link(plan,'destination_registration'),'group-connection-changed')
        self.destination.verify()
        with self.store.immutable_reads():
            original_heads=gr.member_refs(plan,'head',plan,view)
            for i,work in enumerate(plan.payload['works']):
                membership=view.head(gr.member_key(work)); require(membership is not None,'group-membership-changed')
                require(link(self._object(membership,view),'plan')==plan.ref,'group-membership-changed')
                _,wp,_,_=head_summary(original_heads[i],view)
                original=self._object(link(wp,'baseline'),view)
                require(view.head(workspace_key(plan.payload['sources'][i]))==link(original,'workspace'),'group-connection-changed')
        return baseline

    def _observe(self,plan,baseline):
        with self.store.immutable_reads():
            scope=[]
            for ref in gr.member_refs(plan,'head',plan,self.store.load): scope.extend(head_summary(ref,self.store.load)[1].payload['scope'])
        return self.native._observe(SimpleNamespace(payload={'scope':scope}),baseline)

    def _initial(self,plan,load):
        baseline=self._object(link(plan,'baseline'),load); before=read_tree(link(baseline,'tree'),load)
        require(tuple(before)==self._observe(plan,baseline).snapshot.entries,'group-destination-baseline-changed')

    def _prepared(self,plan,view):
        with self.store.immutable_reads():
            works=set(plan.payload['works']); spaces=set(plan.payload['sources'])|{plan.payload['destination']}
            from .group_guard import guard_workspaces
            guard_workspaces(view,spaces,group_plan=plan.ref)
            for k,ref in read_map(view.root().heads,view).items():
                if k.startswith('work:'):
                    h,_,_,_=head_summary(ref,view)
                    if h.payload['workspace']==plan.payload['destination'] and h.payload['work'] not in works:
                        require(h.payload['phase'] not in ('approved','active','review','paused'),'worker-destination-has-active-work')
                elif k.startswith('grant:') and ref.kind=='worker.grant':
                    grant=self._object(ref,view)
                    require(grant.payload['work'] not in works or grant.payload['state']!='active','group-prepared-authority-in-use')
                elif k.startswith('application:'):
                    obj=self._object(ref,view)
                    if ref.kind=='worker.effect':
                        if obj.payload['state'] in ('completed','cancelled'): continue
                        binding=self._object(link(obj,'binding'),view)
                    else: binding=obj
                    require(binding.payload['work'] not in works and binding.payload['destination'] not in spaces,'group-prepared-authority-in-use')
                elif k.startswith(('execution-prepared:','delivery-prepared:')):
                    obj=self._object(ref,view)
                    require(obj.payload['work'] not in works,'group-prepared-authority-in-use')

    def _backup(self,view,version):
        enabled=view.head(activation_key(version))
        if enabled: return link(self._object(enabled,view),'backup_root')
        authority=self.lifecycle_authority
        require(authority is not None,'group-pre-feature-backup-required')
        from .backup_service import backup_status
        status=backup_status(authority)
        require(status.get('verified_export_recorded') and status.get('same_instance') and not status.get('different_root'), 'group-pre-feature-backup-required')
        receipt=decode_canonical(authority.files.read(authority.root/'last-export.json'))
        require(receipt['project']==self.store.project and receipt['instance']==self.store.instance and
                ObjectRef.parse(receipt['root'])==view.root().ref,'group-pre-feature-backup-required')
        required={f'schema:{schema.kind}:{version}' for schema in gr.schemas() if schema.version==version}
        required.add('schema:work.decision:'+str(version+1))
        require(not required.intersection(self.store.requirements()['read']), 'group-activation-record-required')
        return ObjectRef.parse(receipt['root'])

    @reuse_operation_reads
    def create(self,*,operation,group,works,checks,acknowledgement):
        _token(operation); _token(group); text(acknowledgement)
        version=CURRENT_VERSION
        platform={}
        if sys.platform == 'win32' and self.windows_runner is not None:
            version=gr.WINDOWS_GROUP_VERSION
            platform={'platform': gr.WINDOWS_GROUP_PLATFORM}
            gr.windows_definitions(checks)
        else:
            require(sys.platform != 'win32', 'group-platform-unqualified')
            gr.definitions(checks)
        require(type(works) in (list,tuple) and all(type(w) is str for w in works),'group-member-count-unsupported')
        works=sorted(works)
        require((len(works)==2 if version==1 else 2<=len(works)<=gr.MAX_MEMBERS) and len(set(works))==len(works),
                'group-two-distinct-works-required' if version==1 else 'group-member-count-unsupported')
        self._port(version=version)
        heads=[self.work._head(w,same_workspace=False)[1] for w in works]
        for h in heads:
            require(h.payload['phase']=='planned' and link(h,'context') is None,'group-planned-member-required')
            self._source(h.payload['workspace']).workspace.verify()
        registration,observed=self.destination.observe()
        from .storage.sqlite import ValidationView
        before=self.store.root(); backup=self._backup(ValidationView(before,self.store.load),version)
        with self.store.import_attempt(operation,'group-plan'):
            baseline,objects=encode_observation(observed,registration,self.store,operation)
            member_links,mapping=gr.member_links(version,'head',works,[h.ref for h in heads]); objects.extend(mapping)
            pair=record('group.plan',dict(group=group,works=works,sources=[h.payload['workspace'] for h in heads],
                destination=self.destination.workspace,checks=checks,acknowledgement=acknowledgement,**platform),
                dict(member_links,baseline=('integrity',baseline),destination_registration=('decision',registration),backup_root=('provenance',backup)),version=version)
            expected={gr.key(group):None}; changes={gr.key(group):pair[0]}
            for work,h in zip(works,heads):
                member=record('group.member',dict(group=group,work=work),{'plan':('decision',pair[0])},version=version)
                objects.append(member); expected[gr.member_key(work)]=None; changes[gr.member_key(work)]=member[0]
                expected[work_key(work)]=h.ref
            activation=activation_key(version); enabled=self.store.head(activation)
            expected[activation]=enabled
            if enabled is None: changes[activation]=pair[0]
            project=self.store.head(PROJECT_KEY)
            def validate(view):
                guard(view); self._port(version=version)
                require(view.head(PROJECT_KEY)==project,'group-connection-changed')
                require(self._backup(view,version)==backup,'group-backup-changed')
                validate_closure([pair[0],*(r for k,r in changes.items() if k.startswith('group-member:'))],view,self.work.registry,self.work.closure)
                plan=self._object(pair[0],view); self._prepared(plan,view)
                for h in heads:
                    self.work._validate_head(h.ref,view)
                    baseline_ref=link(self._object(link(head_summary(h.ref,view)[1],'baseline'),view),'workspace')
                    require(view.head(workspace_key(h.payload['workspace']))==baseline_ref,'group-connection-changed')
                    self._source(h.payload['workspace']).workspace.verify()
                require(view.head(workspace_key(self.destination.workspace))==registration,'group-connection-changed')
                self.work._recheck_observation(observed)
            self.store.commit_heads(operation=operation,expected=expected,changes=changes,objects=[*objects,pair],import_id=operation,validate=validate)
        return self.view(group)

    @reuse_operation_reads
    def approve(self,*,operation,group,receipt,statement):
        plan=self._selected(group); require(plan.ref.kind=='group.plan','group-plan-approval-required')
        require(receipt==self._receipt('approve',group,plan.ref),'group-stale-receipt'); text(statement)
        objects=[]; expected={gr.key(group):plan.ref}; changes={}; approvals=[]
        original_heads=gr.member_refs(plan,'head',plan,self.store.load)
        for i,work in enumerate(plan.payload['works']):
            h,wp,_,_=head_summary(original_heads[i],self.store.load)
            a=record('work.approval',dict(work=work,workspace=wp.payload['workspace'],statement=statement),{'plan':('decision',wp.ref)})
            new=self.work._head_record(wp.ref,wp.payload,'approved',approval=a[0],previous=h.ref)
            objects.extend([a,new]); approvals.append(a[0]); expected[work_key(work)]=h.ref; changes[work_key(work)]=new[0]
        member_links,mapping=gr.member_links(plan.ref.version,'approval',plan.payload['works'],approvals); objects.extend(mapping)
        pair=record('group.approval',dict(statement=statement),dict(member_links,plan=('decision',plan.ref)),version=plan.ref.version)
        changes[gr.key(group)]=pair[0]
        def validate(view):
            guard(view); self._live_plan(plan,view); self._initial(plan,view); self._prepared(plan,view)
            with self.store.immutable_reads():
                validate_closure([pair[0]],view,self.work.registry,self.work.closure)
                for work in plan.payload['works']:
                    self.work._validate_head(changes[work_key(work)],view)
        self.store.commit_heads(operation=operation,expected=expected,changes=changes,objects=[*objects,pair],
                                validate=validate,descriptor_only=True)
        return self.view(group)

    @reuse_operation_reads
    def candidate(self,*,operation,group):
        selected=self._selected(group)
        if selected.ref.kind=='group.review': selected=self._object(link(selected,'candidate'))
        approval=self._object(link(selected,'approval')) if selected.ref.kind=='group.candidate' else selected
        require(approval.ref.kind=='group.approval','group-approved-plans-required')
        plan=self._object(link(approval,'plan')); baseline=self._object(link(plan,'baseline'))
        after={e['path']:e for e in read_tree(link(baseline,'tree'),self.store.load)}; bodies={}; heads=[]
        for i,work in enumerate(plan.payload['works']):
            h,wp,result,_=head_summary(self.store.head(work_key(work)),self.store.load)
            require(h.payload['phase']=='review' and result is not None,'group-two-submissions-required' if plan.ref.version==1 else 'group-all-submissions-required')
            heads.append(h.ref); entries={e['path']:e for e in read_tree(link(self._object(link(result,'observation')),'tree'),self.store.load)}
            for path in wp.payload['scope']:
                after.pop(path,None)
                if path in entries: after[path]=entries[path]
            bodies.update(read_map(link(result,'after'),self.store.load))
        tree=build_tree(after.values()); mapping=build_map(bodies.items())
        member_links,member_objects=gr.member_links(plan.ref.version,'head',plan.payload['works'],heads)
        pair=record('group.candidate',dict(group=group),dict(member_links,approval=('decision',approval.ref),tree=('integrity',tree.root),after=('integrity',mapping.root)),version=plan.ref.version)
        previous=self.store.head(gr.key(group))
        def validate(view):
            guard(view); self._live_plan(plan,view); self._initial(plan,view)
            validate_closure([pair[0]],view,self.work.registry,self.work.closure)
            for work,head in zip(plan.payload['works'],heads): require(view.head(work_key(work))==head,'group-submission-changed')
        self.store.commit_heads(operation=operation,expected={gr.key(group):previous},changes={gr.key(group):pair[0]},objects=[*tree.objects,*mapping.objects,*member_objects,pair],validate=validate)
        return self.view(group)

    def _live_candidate(self,candidate,view,*,source_files=False):
        with self.store.immutable_reads():
            parts=gr.candidate_parts(candidate.ref,view)
        plan=parts[2]; self._live_plan(plan,view)
        for h,wp,result in parts[-1]:
            require(view.head(work_key(wp.payload['work']))==h.ref,'group-submission-changed')
            if source_files:
                source=self._source(wp.payload['workspace'])
                require(source._result_agrees(wp,result),'worker-source-files-changed')
        return parts

    @reuse_operation_reads
    def check(self,*,operation,group):
        from .group_checks import run_checks
        selected=self._selected(group)
        candidate=self._object(link(selected,'candidate')) if selected.ref.kind=='group.review' else selected
        require(candidate.ref.kind=='group.candidate','group-candidate-required')
        from .storage.sqlite import ValidationView
        view=ValidationView(self.store.root(),self.store.load); guard(view)
        parts=self._live_candidate(candidate,view); self._initial(parts[2],view)
        with self.store.import_attempt(operation,'group-check-evidence'):
            evidence,objects=run_checks(self,candidate,parts,operation)
            mapping=build_map(evidence); pair=record('group.review',{},dict(candidate=('decision',candidate.ref),evidence=('decision',mapping.root)),version=candidate.ref.version)
            def validate(view):
                guard(view); self._live_candidate(candidate,view); self._initial(parts[2],view)
                validate_closure([pair[0]],view,self.work.registry,self.work.closure)
            self.store.commit_heads(operation=operation,expected={gr.key(group):selected.ref},changes={gr.key(group):pair[0]},objects=[*objects,*mapping.objects,pair],import_id=operation,validate=validate)
        return self.view(group)

    @reuse_operation_reads
    def dissolve(self,*,operation,group,receipt,statement):
        text(statement); selected=self._selected(group); plan=gr.plan_for(selected.ref,self.store.load)
        require(selected.ref.kind!='group.effect','group-application-already-started')
        require(receipt==self._receipt('dissolve',group,selected.ref),'group-stale-receipt')
        dissolution=record('group.dissolution',dict(group=group,statement=statement),dict(plan=('decision',plan.ref),selection=('decision',selected.ref)),version=plan.ref.version)
        history='group-dissolved:'+group
        expected={gr.key(group):selected.ref,history:self.store.head(history)}; changes={gr.key(group):None,history:dissolution[0]}
        for w in plan.payload['works']: expected[gr.member_key(w)]=self.store.head(gr.member_key(w)); changes[gr.member_key(w)]=None
        def validate(view):
            guard(view)
            require(view.head(gr.key(group))==selected.ref,'group-membership-changed')
            for work in plan.payload['works']:
                membership=view.head(gr.member_key(work))
                require(membership is not None and link(self._object(membership,view),'plan')==plan.ref,'group-membership-changed')
            validate_closure([dissolution[0]],view,self.work.registry,self.work.closure)
            for k,ref in read_map(view.root().heads,view).items():
                if k.startswith('group-application:') and gr.plan_for(ref,view).ref==plan.ref:
                    require(self._object(ref,view).payload['state']=='cancelled','group-application-already-started')
        self.store.commit_heads(operation=operation,expected=expected,changes=changes,objects=[dissolution],validate=validate)
        return dict(group=group,state='dissolved',accepted=0)

    @fresh_view_reads
    def view(self,group):
        from .group_view import view
        return view(self,group)

    @reuse_operation_reads
    def execute(self,**options):
        from .group_effects import execute
        return execute(self,**options)

    @reuse_operation_reads
    def cancel(self,**options):
        from .group_effects import cancel
        return cancel(self,**options)
