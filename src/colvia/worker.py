"""Exact isolated-worker application with a project-wide durable effect barrier.

An ordinary Work acceptance only records a decision. This separate service
applies retained bytes into another verified workspace and, when explicitly
requested, accepts the named source result in the same terminal publication.
"""
from dataclasses import asdict
from .codec import require,RecordError
from .records import record,link,head_summary,encode_observation,decode_policy,text
from .maps import read_map,map_get
from .tree import read_tree
from .graph import validate_closure
from .connection import PROJECT_KEY,workspace_key
from .effects import PENDING,guard
from .worker_state import transitions,require_initial,classify
from .worker_records import validate_authorization
from .work import work_key
from .storage.sqlite import _token


def application_key(application):_token(application);return 'application:'+application

def grant_key(work):_token(work);return 'grant:'+work


class WorkerService:
    def __init__(self,source,destination,*,authority,port_factory=None):
        self.source=source;self.store=source.store;self.destination=destination;self.authority=authority
        require((destination.store.project,destination.store.instance,destination.store.generation)==
                (self.store.project,self.store.instance,self.store.generation),'worker-foreign-authority')
        if port_factory is None:
            from .platforms.effects_port import effects
            port_factory=effects
        self.port_factory=port_factory

    def _object(self,ref,load=None):return self.source._object(ref,load)

    def _connection(self,view,source_ref,destination_ref,project_ref):
        require(view.head(PROJECT_KEY)==project_ref and
                view.head(workspace_key(self.source.workspace.workspace))==source_ref and
                view.head(workspace_key(self.destination.workspace))==destination_ref,'worker-connection-changed')

    def _competitors(self,view,work):
        for key,ref in read_map(view.root().heads,view).items():
            if not key.startswith('work:'):continue
            head,_,_,_=head_summary(ref,view)
            if head.payload['workspace']==self.destination.workspace and head.payload['work']!=work:
                require(head.payload['phase'] not in ('approved','active','review','paused'),'worker-destination-has-active-work')

    def _binding(self,ref,load):
        validate_closure([ref],load,self.source.registry,self.source.closure)
        binding=self._object(ref,load);require(ref.kind=='worker.binding','worker-binding-required')
        plan=self._object(link(binding,'plan'),load);result=self._object(link(binding,'result'),load)
        require(result.ref.version==1,'attributed-result-not-supported')
        source_head,sp,sr,_=head_summary(link(binding,'source_head'),load)
        self.source._validate_head(source_head.ref,load)
        require(source_head.payload['phase'] in ('review','completed') and sp.ref==plan.ref and sr.ref==result.ref and
                link(source_head,'approval')==link(binding,'approval'),'worker-source-result-mismatch')
        context=link(source_head,'context')
        require(context is None or context.kind=='composition.membership','worker-parent-result-not-supported')
        require(binding.payload['work']==plan.payload['work'] and binding.payload['source']==plan.payload['workspace'] and
                binding.payload['scope']==plan.payload['scope'] and link(binding,'before')==link(plan,'before') and
                link(binding,'after')==link(result,'after'),'worker-binding-scope-mismatch')
        original,before=self.source._baseline(plan,load)
        result_observation=self._object(link(result,'observation'),load);after=read_tree(link(result_observation,'tree'),load)
        baseline=self._object(link(binding,'baseline'),load);destination_before=read_tree(link(baseline,'tree'),load)
        require(tuple(before)==tuple(destination_before),'worker-destination-baseline-changed')
        require(link(original,'policy')==link(baseline,'policy') and original.payload['opaque']==baseline.payload['opaque'],
                'worker-policy-context-mismatch')
        require(link(original,'workspace')==link(binding,'source_registration') and
                link(baseline,'workspace')==link(binding,'destination_registration'),'worker-registration-mismatch')
        for field,workspace in (('source_registration','source'),('destination_registration','destination')):
            require(self._object(link(binding,field),load).payload['workspace']==binding.payload[workspace],'worker-registration-mismatch')
        require(binding.payload['source']==self.source.workspace.workspace and binding.payload['destination']==self.destination.workspace,'worker-wrong-workspace')
        changed=transitions(before,after,binding.payload['scope'])
        require(not any(item['path'].split('/')[-1].casefold()=='.gitignore' for item in changed),'worker-policy-edit-unsupported')
        return binding,plan,result,baseline,before,after,changed

    def _observe(self,binding,baseline):
        before=read_tree(link(baseline,'tree'),self.store.load)
        _,current=self.destination.observe(protected=frozenset(e['path'] for e in before)|frozenset(binding.payload['scope']),
            previous_containers=frozenset(baseline.payload['containers']),previous_policy=decode_policy(link(baseline,'policy'),self.store.load))
        for field in ('root','common','gitdir'):
            actual=getattr(current.topology,field)
            require(baseline.payload[field]==(asdict(actual) if actual else None),'worker-destination-location-changed')
        require([[p,list(v)] for p,v in current.opaque]==baseline.payload['opaque'],'worker-opaque-context-changed')
        return current

    def _live(self,binding,view,*,source=True,destination=True):
        reviewing=self._object(link(binding,'source_head'),view).payload['phase']=='review'
        if destination:self.destination.verify()
        if source and reviewing:self.source.workspace.verify()
        require(view.head(work_key(binding.payload['work']))==link(binding,'source_head'),'worker-source-selection-changed')
        require(view.head(workspace_key(binding.payload['source']))==link(binding,'source_registration') and
                view.head(workspace_key(binding.payload['destination']))==link(binding,'destination_registration'),'worker-connection-changed')
        if source and reviewing:
            require(self.source._result_agrees(self._object(link(binding,'plan'),view),self._object(link(binding,'result'),view)),
                    'worker-source-files-changed')

    def prepare(self,*,operation,application,work):
        """Record an exact reviewable request; do not stage or alter user files."""
        _token(application);ref,head=self.source._head(work)
        require(head.payload['phase'] in ('review','completed'),'worker-source-not-reviewable')
        require(self.source.workspace.workspace!=self.destination.workspace,'worker-distinct-workspaces-required')
        require(link(head,'result').version==1,'attributed-result-not-supported')
        self.source._validate_head(ref,self.store.load)
        # Fail before authority reservation when this platform/volume has no port.
        self.port_factory(self.destination.root,self.authority)
        source_ref,_,_=self.source.workspace.verify();destination_ref,observed=self.destination.observe()
        project=self.store.head(PROJECT_KEY);plan=self._object(link(head,'plan'));result=self._object(link(head,'result'))
        self.store.begin_import(operation,'worker-binding')
        baseline,objects=encode_observation(observed,destination_ref,self.store,operation)
        pair=record('worker.binding',dict(application=application,work=work,source=self.source.workspace.workspace,
            destination=self.destination.workspace,scope=plan.payload['scope']),
            {'plan':('decision',plan.ref),'approval':('decision',link(head,'approval')),'result':('decision',result.ref),
             'source_registration':('decision',source_ref),'destination_registration':('decision',destination_ref),
             'baseline':('integrity',baseline),'before':('integrity',link(plan,'before')),'after':('integrity',link(result,'after')),
             'source_head':('decision',ref)})
        def validate(view):
            guard(view);self._connection(view,source_ref,destination_ref,project);self._competitors(view,work)
            binding,_,_,base,before,after,_=self._binding(pair[0],view);self._live(binding,view)
            current=self._observe(binding,base);require_initial(before,after,current.snapshot.entries,binding.payload['scope'])
        self.store.commit_heads(operation=operation,expected={application_key(application):None},changes={application_key(application):pair[0]},
            objects=[*objects,pair],import_id=operation,validate=validate)
        return self.preview(application)

    def preview(self,application):
        ref=self.store.head(application_key(application));require(ref is not None,'worker-application-not-found')
        require(ref.kind=='worker.binding','worker-application-already-started')
        binding,plan,result,_,_,_,changed=self._binding(ref,self.store.load)
        accepting=self._object(link(binding,'source_head')).payload['phase']=='review'
        return dict(application=application,work=binding.payload['work'],title=plan.payload['title'],files=[i['path'] for i in changed],
            accepts_result=accepting,destination_label=self.destination.root.name,
            summary=result.payload['summary'],source=binding.payload['source'],destination=binding.payload['destination'],
            receipt=self.source._receipt('apply-and-accept',binding.payload['work'],ref),
            question=('이 결과를 대상 폴더에 적용하고 결과 수락까지 기록할까요?' if accepting else '이미 수락한 결과를 대상 폴더에 적용할까요?'))

    def grant(self,*,operation,work,owner,delegate,statement,revoke=False):
        """Human-authorized sole isolated-worker exception; never ordinary accept."""
        text(statement);text(owner,256);text(delegate,256);require(owner!=delegate,'worker-distinct-delegate-required')
        ref,head=self.source._head(work);plan=self._object(link(head,'plan'))
        require(head.payload['phase'] not in ('paused','discarded'),'lifecycle-work-inactive')
        require(link(head,'approval') is not None,'worker-approved-plan-required')
        context=link(head,'context');require(context is None or context.kind=='composition.membership','worker-parent-grant-refused')
        self.destination.verify();require(plan.payload['workspace']!=self.destination.workspace,'worker-distinct-workspaces-required')
        old=self.store.head(grant_key(work))
        pair=record('worker.grant',dict(work=work,source=plan.payload['workspace'],destination=self.destination.workspace,
            scope=plan.payload['scope'],owner=owner,delegate=delegate,state='revoked' if revoke else 'active',statement=statement),
            {'plan':('decision',plan.ref),'previous':('provenance',old)})
        def validate(view):
            guard(view);require(view.head(work_key(work))==ref,'worker-source-selection-changed')
            self.source._validate_head(ref,view);self.source.workspace.verify();self.destination.verify()
            validate_closure([pair[0]],view,self.source.registry,self.source.closure)
        self.store.commit_heads(operation=operation,expected={grant_key(work):old},changes={grant_key(work):pair[0]},objects=[pair],validate=validate)
        return dict(work=work,delegation=True,state='revoked' if revoke else 'active')

    def _manifest(self,effect,load=None):
        obj=self._object(link(effect,'manifest'),load)
        require(obj.payload['application']==effect.payload['application'],'worker-manifest-application-mismatch')
        return {k:v for k,v in obj.payload.items() if k!='links'}

    def _effect(self,ref,load):
        effect=self._object(ref,load);require(ref.kind=='worker.effect','worker-effect-required')
        validate_closure([ref],load,self.source.registry,self.source.closure)
        binding,*parts=self._binding(link(effect,'binding'),load)
        auth,ab=validate_authorization(link(effect,'authorization'),load)
        require(ab.ref==binding.ref and effect.payload['application']==binding.payload['application'],'worker-effect-binding-mismatch')
        actual=[{k:i[k] for k in ('path','pre','post')} for i in self._manifest(effect,load)['items']]
        require(actual==list(parts[-1]),'worker-effect-transition-mismatch')
        return effect,binding,parts

    def _check_files(self,port,effect,binding,parts,*,cancelling=False,load=None):
        plan,result,baseline,before,after,changes=parts
        if cancelling:
            # No files are written or accepted. Exact current preimage content,
            # unaliased paths and absence of every evacuated original suffice.
            return tuple('pre' if port.cancellable(self._manifest(effect,load),i) else 'unknown' for i in range(len(changes)))
        current=self._observe(binding,baseline);state=classify(before,after,current.snapshot.entries,binding.payload['scope'])
        require(not state.outside,'worker-outside-scope-change')
        return tuple(port.state(self._manifest(effect,load),i) for i in range(len(changes)))

    def execute(self,*,operation,application,receipt,statement,actor='owner',authority='human',event=lambda stage:None):
        """Reserve under lock, then share the same executor used after interruption."""
        text(statement);text(actor,256);self._operation(operation)
        ref=self.store.head(application_key(application));require(ref is not None and ref.kind=='worker.binding','worker-binding-required')
        binding,plan,result,baseline,before,after,changes=self._binding(ref,self.store.load)
        require(receipt==self.source._receipt('apply-and-accept',binding.payload['work'],ref),'stale-worker-application-receipt')
        port=self.port_factory(self.destination.root,self.authority)
        with port.exclusion():
            require(self.store.head(PENDING) is None and self.store.head(application_key(application))==ref,'external-effect-pending')
            current=self._observe(binding,baseline);require_initial(before,after,current.snapshot.entries,binding.payload['scope'])
            grant=self.store.head(grant_key(binding.payload['work'])) if authority=='delegated' else None
            auth=record('worker.authorization',dict(authority=authority,actor=actor,statement=statement),
                        {'binding':('decision',ref),'grant':('decision',grant)})
            # Validate actor/grant before creating staging, with no current-head mutation.
            def authload(target):return auth[1] if target==auth[0] else self.store.load(target)
            self.source.registry.inspect(auth[0],auth[1],required=True);validate_authorization(auth[0],authload)
            from .bodies import body_bytes
            def body(path):
                bodyref=map_get(link(binding,'after'),path,self.store.load);require(bodyref is not None,'worker-post-body-required')
                return body_bytes(bodyref,self.store.load)
            from .storage.sqlite import ValidationView
            preflight=ValidationView(self.store.root(),authload)
            guard(preflight);self._live(binding,preflight);self._competitors(preflight,binding.payload['work'])
            validate_authorization(auth[0],preflight,live=True)
            manifest=port.prepare(application,changes,body)
            manifest_pair=record('worker.manifest',manifest,{})
            # For a result still in review, this reservation binds live source-file agreement.
            # Later effects retain exact record/grant and destination checks;
            # they never adopt newer source bytes or accept another result.
            pair=record('worker.effect',dict(application=application,state='pending'),
                {'binding':('decision',ref),'authorization':('decision',auth[0]),'manifest':('integrity',manifest_pair[0]),'progress':('integrity',None),'previous':('provenance',None)})
            def validate(view):
                guard(view);self._live(binding,view);self._competitors(view,binding.payload['work'])
                validate_authorization(auth[0],view,live=True)
                effect,_,parts=self._effect(pair[0],view)
                require(all(s=='pre' for s in self._check_files(port,effect,binding,parts,load=view)),'worker-initial-state-changed')
            self.store.commit_heads(operation=operation+'-reserve',expected={application_key(application):ref,PENDING:None},
                changes={application_key(application):pair[0],PENDING:pair[0]},objects=[auth,manifest_pair,pair],validate=validate)
            event('reserved')
            return self._run(operation,application,port,event)

    @staticmethod
    def _operation(operation):
        # Every derived publication must fit before the first external effect.
        _token(operation);_token(operation+'-progress-1000000')

    def resume(self,*,operation,application,event=lambda stage:None):
        self._operation(operation)
        port=self.port_factory(self.destination.root,self.authority)
        with port.exclusion():return self._run(operation,application,port,event)

    def _next(self,effect,state,*,progress=None):
        return record('worker.effect',dict(application=effect.payload['application'],state=state),
            {'binding':('decision',link(effect,'binding')),'authorization':('decision',link(effect,'authorization')),'manifest':('integrity',link(effect,'manifest')),
             'progress':('integrity',progress if progress is not None else link(effect,'progress')),'previous':('provenance',effect.ref)})

    def _pending(self,application):
        ref=self.store.head(application_key(application));require(ref is not None and self.store.head(PENDING)==ref,'worker-pending-application-required')
        effect,binding,parts=self._effect(ref,self.store.load);require(effect.payload['state']=='pending','worker-pending-application-required')
        return effect,binding,parts

    def _publish_effect(self,operation,effect,pair,port,*,objects=(),extra_expected=None,extra_changes=None,states=None):
        expected={PENDING:effect.ref,application_key(effect.payload['application']):effect.ref}
        changes={application_key(effect.payload['application']):pair[0],PENDING:pair[0] if self._object_from_pair(pair).payload['state']=='pending' else None}
        expected.update(extra_expected or {});changes.update(extra_changes or {})
        def validate(view):
            guard(view,expected_effect=effect.ref)
            new,binding,parts=self._effect(pair[0],view)
            cancelling=new.payload['state']=='cancelled'
            self._live(binding,view,source=False,destination=not cancelling)
            validate_authorization(link(new,'authorization'),view,live=True)
            actual=self._check_files(port,new,binding,parts,cancelling=new.payload['state']=='cancelled',load=view)
            if states is not None:require(all(s in states for s in actual),'worker-terminal-state-mismatch')
            for key,ref in (extra_changes or {}).items():
                if key.startswith('work:'):
                    self.source._validate_head(ref,view)
                    from .composition import validate_transition
                    h,p,r,_=head_summary(ref,view);validate_transition(expected[key],h,p,r,view)
        self.store.commit_heads(operation=operation,expected=expected,changes=changes,objects=[*objects,pair],validate=validate)

    def _object_from_pair(self,pair):return self.source.registry.inspect(pair[0],pair[1],required=True)

    def _pending_dependencies(self,effect,binding):
        from .storage.sqlite import ValidationView
        view=ValidationView(self.store.root(),self.store.load)
        guard(view,expected_effect=effect.ref)
        require(view.head(application_key(effect.payload['application']))==effect.ref,'worker-effect-selection-changed')
        self._live(binding,view,source=False);validate_authorization(link(effect,'authorization'),view,live=True)

    def _run(self,operation,application,port,event):
        effect,binding,parts=self._pending(application)
        # Every re-entry first proves the original dependencies. Read-only checks
        # do not clear the durable pending state on a failure.
        self._pending_dependencies(effect,binding)
        self._check_files(port,effect,binding,parts)
        for i in range(len(parts[-1])):
            try:
                port.apply_one(self._manifest(effect),i,before_effect=lambda:(self._pending_dependencies(effect,binding),self._check_files(port,effect,binding,parts)),event=event)
            except OSError:raise RecordError('effect-outcome-unknown') from None
            progress=record('worker.progress',dict(application=application,index=i,stage='verified'),{'previous':('provenance',link(effect,'progress'))})
            pair=self._next(effect,'pending',progress=progress[0])
            self._publish_effect(operation+'-progress-'+str(i),effect,pair,port,objects=[progress],states={'pre','post','evacuated'})
            effect=self._object(pair[0]);event('progress-published')
        try:
            for i in range(len(parts[-1])):port.sync(self._manifest(effect),i)
        except OSError:raise RecordError('effect-outcome-unknown') from None
        event('before-completion')
        source_ref=link(binding,'source_head');source_head,plan,result,_=head_summary(source_ref,self.store.load)
        expected={work_key(binding.payload['work']):source_ref};changes={};objects=[]
        if source_head.payload['phase']=='review':
            auth=self._object(link(effect,'authorization'))
            decision=record('work.decision',dict(work=binding.payload['work'],workspace=binding.payload['source'],action='accept',statement=auth.payload['statement']),
                            {'result':('decision',result.ref),'authorization':('decision',auth.ref)})
            head=self.source._head_record(plan.ref,plan.payload,'completed',approval=link(source_head,'approval'),result=result.ref,
                                          decision=decision[0],previous=source_ref)
            objects.extend([decision,head]);changes[work_key(binding.payload['work'])]=head[0]
        pair=self._next(effect,'completed')
        self._publish_effect(operation+'-complete',effect,pair,port,objects=objects,extra_expected=expected,extra_changes=changes,states={'post'})
        return dict(application=application,work=binding.payload['work'],state='completed')

    def cancel(self,*,operation,application):
        """No rollback: cancel only when every real target is still its preimage."""
        port=self.port_factory(self.destination.root,self.authority)
        with port.exclusion():
            effect,binding,parts=self._pending(application)
            require(all(s=='pre' for s in self._check_files(port,effect,binding,parts,cancelling=True)),'worker-cancel-requires-all-pre')
            pair=self._next(effect,'cancelled');self._publish_effect(operation,effect,pair,port,states={'pre'})
            return dict(application=application,work=binding.payload['work'],state='cancelled')

    def view(self,application):
        ref=self.store.head(application_key(application));require(ref is not None,'worker-application-not-found')
        if ref.kind=='worker.binding':return self.preview(application)
        effect,binding,parts=self._effect(ref,self.store.load);paths=[];modified=[];blocked=None
        try:
            port=self.port_factory(self.destination.root,self.authority)
            with port.exclusion(create=False):
                require(self.store.head(application_key(application))==ref,'worker-effect-selection-changed')
                manifest=self._manifest(effect)
                for i,item in enumerate(manifest['items']):
                    try:
                        observed=port.inspect_state(manifest,i)
                        paths.append(dict(path=item['path'],state=observed['state']))
                        if observed['retained_original_modified']:modified.append(item['path'])
                    except (RecordError,OSError) as error:
                        reason=error.code if isinstance(error,RecordError) else 'effect-path-unavailable'
                        paths.append(dict(path=item['path'],state='unknown',reason=reason))
                        if blocked is None:blocked=dict(path=item['path'],reason=reason)
                if effect.payload['state']=='pending':
                    try:self._pending_dependencies(effect,binding);self._check_files(port,effect,binding,parts)
                    except (RecordError,OSError) as error:
                        if blocked is None:blocked=dict(path=None,reason=error.code if isinstance(error,RecordError) else 'workspace-access-unavailable')
        except (RecordError,OSError) as error:
            blocked=dict(path=None,reason=error.code if isinstance(error,RecordError) else 'workspace-access-unavailable')
        return dict(application=application,work=binding.payload['work'],state=effect.payload['state'],paths=paths,
                    retained_original_modified=modified,blocked=blocked)
