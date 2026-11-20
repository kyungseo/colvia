"""Ordinary Work application service over immutable records and workspace ports.

A plan approval is not result acceptance. Submission includes review preparation;
no second submit request or acceptance ticket is required. Receipts bind the exact
shown record and local authority instance; they are not human authentication.
"""
from __future__ import annotations
import hashlib
from contextlib import contextmanager

from .bodies import descriptor,submission_size
from .codec import RecordError,decode_envelope,canonical_bytes,require
from .connection import PROJECT_KEY,workspace_key
from .graph import validate_closure
from .maps import read_map
from .observation import verify_scope,policy_transition,relocated_policy
from .connection_identity import contexts_match, ROLES
from .connection import Connections
from .records import (observation_identity, application_registry,operation_closure,record,link,encode_observation,
                      decode_policy,text,head_summary,submission_input)
from .storage.sqlite import _token
from .tree import read_tree


_CARRY_CONTEXT=object()


def work_key(work):_token(work);return 'work:'+work


class WorkService:
    def __init__(self,store,workspace):
        self.store=store;self.workspace=workspace
        self.registry=application_registry();self.closure=operation_closure(self.registry)

    def _object(self,ref,load=None):
        load=load or self.store.load
        obj=self.registry.inspect(ref,load(ref),required=True)
        require(obj is not None,'required-record-unavailable');return obj

    def _head(self,work,*,same_workspace=True):
        ref=self.store.head(work_key(work));require(ref is not None,'work-not-found')
        obj,_,_,_=head_summary(ref,self.store.load);require(obj.payload['work']==work,'wrong-work-head')
        if same_workspace:require(obj.payload['workspace']==self.workspace.workspace,'wrong-workspace')
        return ref,obj

    def _receipt(self,action,work,ref):
        return hashlib.sha256(canonical_bytes(dict(action=action,project=self.store.project,
            instance=self.store.instance,work=work,head=ref.as_dict()))).hexdigest()

    def _head_record(self,plan_ref,plan,phase,*,approval=None,result=None,decision=None,previous=None,archived=False,context=_CARRY_CONTEXT):
        if context is _CARRY_CONTEXT:
            context=link(self._object(previous),'context') if previous is not None else None
        return record('work.head',dict(work=plan['work'],workspace=plan['workspace'],title=plan['title'],phase=phase,archived=archived),
            {'plan':('decision',plan_ref),'approval':('decision',approval),'result':('decision',result),
             'decision':('decision',decision),'previous':('provenance',previous),'context':('decision',context)})

    def _baseline(self,plan,load=None):
        load=load or self.store.load
        obj=self._object(link(plan,'baseline'),load)
        return obj,read_tree(link(obj,'tree'),load)

    def _body_map(self,scope,entries,map_ref,load):
        expected={e['path']:e for e in entries if e['path'] in scope}
        require(all(e['kind']=='regular' for e in expected.values()),'opaque-edit-not-supported')
        bodies=read_map(map_ref,load)
        require(set(bodies)==set(expected),'body-map-scope-mismatch')
        sizes=[]
        for path,ref in bodies.items():
            obj=descriptor(ref,load(ref));entry=expected[path]
            require(obj.payload['size']==entry['size'] and obj.payload['sha256']==entry['sha256'],'body-tree-mismatch')
            sizes.append(entry['size'])
        return sizes

    def _validate_head(self,ref,load):
        validate_closure([ref],load,self.registry,self.closure)
        head,plan,_,_=head_summary(ref,load);planref=plan.ref
        common=lambda obj:require(all(obj.payload[k]==plan.payload[k] for k in ('work','workspace')),'work-reference-mismatch')
        common(head);require(head.payload['title']==plan.payload['title'],'work-title-mismatch')
        baseline,entries=self._baseline(plan,load)
        registration=self._object(link(baseline,'workspace'),load)
        require(registration.payload['workspace']==plan.payload['workspace'],'work-workspace-mismatch')
        scope=frozenset(plan.payload['scope']);verify_scope(entries,entries,scope)
        sizes=self._body_map(scope,entries,link(plan,'before'),load)
        approval=link(head,'approval')
        if approval is not None:
            approved=self._object(approval,load);common(approved)
            require(link(approved,'plan')==planref,'approval-plan-mismatch')
        resultref=link(head,'result')
        if resultref is not None:
            result=self._object(resultref,load);common(result)
            require(link(result,'plan')==planref and link(result,'approval')==approval,'submission-approval-mismatch')
            sizes+=self._validate_result(plan,result,load)
        from .composition import validate_context
        validate_context(head,plan,self._object(resultref,load) if resultref else None,load,validate_capture=self._validate_capture)
        submission_size(sizes)
        decision=link(head,'decision')
        if decision is not None:
            decided=self._object(decision,load);common(decided)
            require(link(decided,'result')==resultref,'decision-result-mismatch')
            if head.payload['phase']=='completed':require(decided.payload['action']=='accept','acceptance-required')
            authorization=link(decided,'authorization')
            if authorization is not None:
                from .worker_records import validate_authorization
                _,binding=validate_authorization(authorization,load)
                require(decided.payload['action']=='accept' and link(binding,'result')==resultref and
                        link(binding,'plan')==planref and binding.payload['work']==plan.payload['work'] and
                        binding.payload['source']==plan.payload['workspace'],'worker-decision-authorization-mismatch')

    def _validate_result(self,plan,result,load):
        common=lambda obj:require(all(obj.payload[k]==plan.payload[k] for k in ('work','workspace')),'work-reference-mismatch')
        common(result);require(link(result,'plan')==plan.ref,'submission-plan-mismatch')
        approval=self._object(link(result,'approval'),load);common(approval)
        require(link(approval,'plan')==plan.ref,'approval-plan-mismatch')
        baseline,original=self._baseline(plan,load);scope=frozenset(plan.payload['scope'])
        from .rework import effective_entries
        entries=effective_entries(self,plan,result,load)
        before_sizes=self._body_map(scope,original,link(plan,'before'),load);sizes=[]
        observed=self._object(link(result,'observation'),load)
        require(link(observed,'workspace')==link(baseline,'workspace'),'submission-workspace-mismatch')
        require(contexts_match(baseline.payload,observed.payload,(*ROLES,'kind','opaque'),load=load,
                               workspace=link(baseline,'workspace'),
                               anchors=(observation_identity(baseline),observation_identity(observed))),
                'observation-context-changed')
        after=read_tree(link(observed,'tree'),load)
        changed=verify_scope(entries,after,scope)
        require(list(changed)==result.payload['changed'],'submission-change-mismatch')
        require({c['name'] for c in result.payload['checks']}==set(plan.payload['checks']) and
                len(result.payload['checks'])==len(plan.payload['checks']),'check-report-mismatch')
        old_policy=decode_policy(link(baseline,'policy'),load);new_policy=decode_policy(link(observed,'policy'),load)
        old_policy=relocated_policy(old_policy,baseline.payload['common'],observed.payload['common'])
        policy_transition(old_policy,new_policy,verified_structural=frozenset(observed.payload['containers']+observed.payload['nested']),
            protected=frozenset(e['path'] for e in entries)|scope,approved_policy_paths=scope)
        sizes+=self._body_map(scope,after,link(result,'after'),load)
        previous=link(result,'previous')
        if previous is not None:
            older=self._object(previous,load);common(older)
            require(older.ref.version!=2 or result.ref.version==2,'attribution-protection-removed')
            require(older.payload['revision']+1==result.payload['revision'],'submission-sequence-mismatch')
        else:require(result.payload['revision']==1,'submission-sequence-mismatch')
        if result.ref.version==2:require(all(c["status"]=="passed" for c in result.payload["checks"]),"attribution-checks-required")
        submission_size(before_sizes+sizes)
        return sizes

    def _validate_capture(self,capture,load):
        plan=self._object(link(capture,'plan'),load);result=self._object(link(capture,'result'),load)
        # A synthetic validation root adds no authority. The saved typed acceptance,
        # approval and exact content references carry the decision, not provenance.
        ref,raw=self._head_record(plan.ref,plan.payload,'completed',approval=link(result,'approval'),
            result=result.ref,decision=link(capture,'decision'),context=None)
        def captured_load(target):return raw if target==ref else load(target)
        self._validate_head(ref,captured_load)

    def _publish(self,operation,work,expected,head_pair,objects=(),*,import_id=None,recheck=lambda:None,pinned=None,pinned_root=None):
        ref,raw=head_pair
        workspace_ref,_,_=self.workspace.verify()
        project_ref=self.store.head(PROJECT_KEY)
        def validate(load):
            from .effects import guard
            guard(load)
            require(load.head(workspace_key(self.workspace.workspace))==workspace_ref and load.head(PROJECT_KEY)==project_ref,
                    'connection-changed')
            for key,value in (pinned or {}).items():require(load.head(key)==value,"attribution-peer-changed")
            if pinned_root is not None:require(load.root().ref==pinned_root,'attribution-heads-changed')
            self._validate_head(ref,load)
            from .composition import validate_transition
            candidate,plan,result,_=head_summary(ref,load)
            validate_transition(expected,candidate,plan,result,load)
            recheck()
        self.store.commit_heads(operation=operation,expected={work_key(work):expected},changes={work_key(work):ref},
            objects=[*objects,(ref,raw)],import_id=import_id,validate=validate)
        return ref

    def plan(self,*,operation,work,title,goal,scope,checks,excludes=(),replace_receipt=None):
        _token(operation);_token(work)
        from .tree import logical_path
        scope=list(scope)
        require(0<len(scope)<=100000 and all(type(p) is str for p in scope) and len(set(scope))==len(scope),'invalid-scope')
        require(all(logical_path(p)==p for p in scope),'invalid-scope-path')
        scope.sort()
        for path in scope:
            folded=path.casefold()
            require(not any(p in ('.git','.colvia') for p in folded.split('/')) and folded!='.colvia-link.json','managed-path-not-editable')
        prior=self.store.head(work_key(work))
        if prior is not None:
            _,previous=self._head(work)
            require(previous.payload['phase']=='planned' and replace_receipt==self._receipt('approve',work,prior),'work-already-exists')
        workspace_ref,observed=self.workspace.observe(protected=frozenset(scope))
        verify_scope(observed.snapshot.entries,observed.snapshot.entries,frozenset(scope))
        self.store.begin_import(operation,'ordinary-plan')
        before,objects,total=self.workspace.capture(scope,observed,operation)
        observation,extra=encode_observation(observed,workspace_ref,self.store,operation);objects.extend(extra)
        payload=dict(work=work,workspace=self.workspace.workspace,title=title,goal=goal,scope=scope,checks=list(checks),excludes=list(excludes))
        planref,raw=record('work.plan',payload,{'baseline':('integrity',observation),'before':('integrity',before)})
        objects.append((planref,raw));head=self._head_record(planref,payload,'planned',previous=prior)
        self._publish(operation,work,prior,head,objects,import_id=operation,recheck=lambda:self._recheck_observation(observed,frozenset(scope)))
        return self.plan_review(work)

    def plan_review(self,work):
        ref,head=self._head(work);require(head.payload['phase']=='planned','plan-not-awaiting-approval')
        plan=self._object(link(head,'plan'))
        return dict(work=work,title=plan.payload['title'],goal=plan.payload['goal'],scope=plan.payload['scope'],
                    checks=plan.payload['checks'],excludes=plan.payload['excludes'],state='planned',
                    receipt=self._receipt('approve',work,ref),question='이 범위로 진행할까요?')

    def approve(self,*,operation,work,receipt,statement):
        ref,head=self._head(work);require(head.payload['phase']=='planned','plan-not-awaiting-approval')
        require(receipt==self._receipt('approve',work,ref),'stale-plan-receipt');text(statement)
        planref=link(head,'plan');plan=self._object(planref)
        approved,raw=record('work.approval',dict(work=work,workspace=self.workspace.workspace,statement=statement),{'plan':('decision',planref)})
        newhead=self._head_record(planref,plan.payload,'approved',approval=approved,previous=ref)
        self._publish(operation,work,ref,newhead,[(approved,raw)])
        return dict(work=work,state='approved')

    def _observe_from_plan(self,plan,extra=()):
        baseline,entries=self._baseline(plan)
        registration,current=self.workspace.observe(protected=frozenset(e['path'] for e in entries)|frozenset(plan.payload['scope'])|frozenset(extra),
            previous_containers=frozenset(baseline.payload['containers']))
        from dataclasses import asdict
        now={k:asdict(v) if (v:=getattr(current.topology,k)) is not None else None for k in ROLES}
        require(contexts_match(baseline.payload,now,ROLES,load=self.store.load,
                               workspace=link(baseline,'workspace'),
                               anchors=(Connections(self.store).identity(registration),)),
                'workspace-location-changed')
        previous=relocated_policy(decode_policy(link(baseline,'policy'),self.store.load),baseline.payload['common'],now['common'])
        policy_transition(previous,current.policy,verified_structural=current.structural.containers|current.structural.nested,
            protected=frozenset(e['path'] for e in entries)|frozenset(plan.payload['scope'])|frozenset(extra),
            approved_policy_paths=frozenset(plan.payload['scope']))
        require([[p,list(v)] for p,v in current.opaque]==baseline.payload['opaque'],'opaque-context-changed')
        return baseline,entries,current

    def _recheck_observation(self,observed,scope=frozenset()):
        _,now=self.workspace.observe(protected=frozenset(e['path'] for e in observed.snapshot.entries)|scope,
            previous_containers=observed.structural.containers,previous_policy=observed.policy)
        require(now.snapshot.entries==observed.snapshot.entries and now.topology==observed.topology and
                now.opaque==observed.opaque,'workspace-observation-changed')

    def start(self,*,operation,work):
        ref,head=self._head(work);require(head.payload['phase']=='approved','plan-approval-required')
        planref=link(head,'plan');plan=self._object(planref)
        _,entries,current=self._observe_from_plan(plan)
        require(tuple(entries)==current.snapshot.entries,'plan-baseline-changed')
        newhead=self._head_record(planref,plan.payload,'active',approval=link(head,'approval'),previous=ref)
        self._publish(operation,work,ref,newhead,recheck=lambda:self._recheck_observation(current,frozenset(plan.payload['scope'])))
        return dict(work=work,state='active')

    @contextmanager
    def _prepare_submission(self,*,operation,work,summary,checks):
        ref,head=self._head(work);require(head.payload['phase']=='active','work-not-active')
        planref=link(head,'plan');plan=self._object(planref);scope=frozenset(plan.payload['scope'])
        from .rework import attribution,select
        prior=self._object(link(head,'result')) if link(head,'result') else None
        carried=attribution(prior,self.store.load)
        _,entries,current=self._observe_from_plan(plan,carried)
        entries,adopted,pinned,pinned_root=select(self,head,plan,current)
        changed=verify_scope(entries,current.snapshot.entries,scope)
        submission_input(summary,checks)
        require({c['name'] for c in checks}==set(plan.payload['checks']) and
                len(checks)==len(plan.payload['checks']),'check-report-mismatch')
        if adopted:require(bool(checks) and all(c['status']=='passed' for c in checks),'attribution-checks-required')
        with self.store.import_attempt(operation,'ordinary-result'):
            after,objects,total=self.workspace.capture(scope,current,operation)
            workspace_ref,_,_=self.workspace.verify()
            observed,extra=encode_observation(current,workspace_ref,self.store,operation);objects.extend(extra)
            previous=link(head,'result');revision=1 if previous is None else self._object(previous).payload['revision']+1
            links={'plan':('decision',planref),'approval':('decision',link(head,'approval')),
                   'observation':('integrity',observed),'after':('integrity',after),'previous':('provenance',previous)}
            if adopted:
                from .maps import build_map
                proof=build_map(adopted.items());objects.extend(proof.objects);links['attribution']=('decision',proof.root)
            result,raw=record('work.submission',dict(work=work,workspace=self.workspace.workspace,revision=revision,summary=summary,
                checks=checks,changed=list(changed)),links,version=2 if adopted else 1)
            objects.append((result,raw));newhead=self._head_record(planref,plan.payload,'review',approval=link(head,'approval'),result=result,previous=ref)
            yield dict(expected=ref,head=newhead,objects=objects,current=current,scope=scope,pinned=pinned,pinned_root=pinned_root)

    def submit(self,*,operation,work,summary,checks):
        with self._prepare_submission(operation=operation,work=work,summary=summary,checks=checks) as prepared:
            self._publish(operation,work,prepared['expected'],prepared['head'],prepared['objects'],import_id=operation,
                recheck=lambda:self._recheck_observation(prepared['current'],prepared['scope']),pinned=prepared['pinned'],pinned_root=prepared['pinned_root'])
        return self.review(work)

    def _result_agrees(self,plan,result):
        require(plan.payload['workspace']==self.workspace.workspace,'wrong-workspace')
        observed=self._object(link(result,'observation'))
        from .tree import entry_at
        scope=frozenset(plan.payload['scope']);tree=link(observed,'tree')
        entries=[entry_at(tree,path,self.store.load) for path in sorted(scope)]
        return self.workspace.selected(scope)==tuple(e for e in entries if e is not None)

    def review(self,work):
        ref,head=self._head(work,same_workspace=False);require(head.payload['phase']=='review','result-not-awaiting-review')
        plan=self._object(link(head,'plan'));result=self._object(link(head,'result'))
        value=dict(work=work,title=head.payload['title'],state='review',summary=result.payload['summary'],
            files=result.payload['changed'],checks=result.payload['checks'],
            receipt=self._receipt('accept',work,ref),question='이대로 마무리할까요, 아니면 고칠 부분이 있을까요?')
        try:value['current_matches']=self._result_agrees(plan,result)
        except (OSError,RecordError) as exc:
            value['current_matches']=None
            value['current_unavailable']=exc.code if isinstance(exc,RecordError) else 'workspace-access-unavailable'
        if result.ref.version==2:
            from .rework import attribution_summary
            value['attribution']=attribution_summary(self,result)
        return value

    def accept(self,*,operation,work,receipt,statement):
        ref,head=self._head(work);text(statement)
        if head.payload['phase']=='completed':
            decision=link(head,'decision');cursor=head;steps=0
            while cursor.payload['phase']=='completed' and link(cursor,'decision')==decision:
                previous=link(cursor,'previous');require(previous is not None,'acceptance-origin-unavailable')
                cursor,_,_,_=head_summary(previous,self.store.load);steps+=1
                require(steps<=10000 and cursor.payload['work']==work and cursor.payload['workspace']==self.workspace.workspace,'acceptance-origin-unavailable')
            require(cursor.payload['phase']=='review' and link(cursor,'result')==link(head,'result') and
                    receipt==self._receipt('accept',work,cursor.ref),'stale-result-receipt')
            return self.view(work)
        require(head.payload['phase']=='review','result-not-awaiting-review')
        require(receipt==self._receipt('accept',work,ref),'stale-result-receipt')
        planref=link(head,'plan');plan=self._object(planref);resultref=link(head,'result');result=self._object(resultref)
        require(self._result_agrees(plan,result),'reviewed-files-changed')
        decision,raw=record('work.decision',dict(work=work,workspace=self.workspace.workspace,action='accept',statement=statement),
                            {'result':('decision',resultref),'authorization':('decision',None)})
        newhead=self._head_record(planref,plan.payload,'completed',approval=link(head,'approval'),result=resultref,decision=decision,previous=ref)
        self._publish(operation,work,ref,newhead,[(decision,raw)],recheck=lambda:require(self._result_agrees(plan,result),'reviewed-files-changed'))
        return self.view(work)

    def revise(self,*,operation,work,receipt,statement):
        ref,head=self._head(work);require(head.payload['phase'] in ('review','completed'),'work-not-reviewable');text(statement)
        require(receipt==self._receipt('accept' if head.payload['phase']=='review' else 'reopen',work,ref),'stale-result-receipt')
        planref=link(head,'plan');plan=self._object(planref);result=link(head,'result')
        from .git_transition_record import require_current_approval
        require_current_approval(self.store, plan)
        decision,raw=record('work.decision',dict(work=work,workspace=self.workspace.workspace,action='request-changes',statement=statement),{'result':('decision',result),'authorization':('decision',None)})
        newhead=self._head_record(planref,plan.payload,'active',approval=link(head,'approval'),result=result,decision=decision,previous=ref)
        self._publish(operation,work,ref,newhead,[(decision,raw)])
        return dict(work=work,state='active')

    def view(self,work):
        ref,head=self._head(work,same_workspace=False);plan=self._object(link(head,'plan'))
        value=dict(work=work,title=head.payload['title'],state=head.payload['phase'],archived=head.payload['archived'],scope=plan.payload['scope'],checks=plan.payload['checks'])
        from .scope_addition import history
        amendments = history(head, self.store.load)
        if amendments:
            value['scope_additions'] = [{k:amendment.payload[k] for k in ('edit','create','checks','reason','statement')}
                                        for amendment,_ in reversed(amendments)]
        result=link(head,'result')
        if result is not None:
            obj=self._object(result);value.update(summary=obj.payload['summary'],files=obj.payload['changed'],revision=obj.payload['revision'])
            try:value['current_matches']=self._result_agrees(plan,obj)
            except (OSError,RecordError) as exc:
                value['current_matches']=None
                value['current_unavailable']=exc.code if isinstance(exc,RecordError) else 'workspace-access-unavailable'
        if head.payload['phase']=='active' and link(head,'decision') is not None:
            from .rework import resume_context
            value['rework']=resume_context(self,head,plan)
        if result is not None and obj.ref.version==2:
            from .rework import attribution_summary
            value['attribution']=attribution_summary(self,obj)
        from . import progress
        if progress.eligible(head) and head.payload['workspace'] == self.workspace.workspace:
            value.update(progress.view(self, work, head, plan.payload['scope'], amendments))
        if 'schema:work.head:2' in self.store.requirements()['read']:
            from .work_lifecycle import detail
            value.update(detail(self,work,head))
        if head.payload['phase']=='completed':value['reopen_receipt']=self._receipt('reopen',work,ref)
        return value

    def archive(self,*,operation,work,archived):
        ref,head=self._head(work);require(head.payload['phase']=='completed' and type(archived) is bool,'archive-completed-work-only')
        if head.payload['archived']==archived:return self.view(work)
        planref=link(head,'plan');plan=self._object(planref)
        newhead=self._head_record(planref,plan.payload,'completed',approval=link(head,'approval'),result=link(head,'result'),
                                  decision=link(head,'decision'),previous=ref,archived=archived)
        self._publish(operation,work,ref,newhead)
        return self.view(work)


    def result_content(self,work,path,*,revision=None,text_limit=65536):
        """Explicit historical body lookup; never infer old bytes from current files."""
        from .bodies import body_bytes
        from .maps import map_get
        require(type(text_limit) is int and 0<=text_limit<=1024*1024,'invalid-text-limit')
        ref,head=self._head(work,same_workspace=False);plan=self._object(link(head,'plan'))
        require(path in plan.payload['scope'],'path-not-in-work-scope')
        current=link(head,'result');require(current is not None,'work-result-required')
        result=self._object(current)
        if revision is not None:
            require(type(revision) is int and 1<=revision<=result.payload['revision'],'result-revision-not-found')
            steps=0
            while result.payload['revision']!=revision:
                previous=link(result,'previous');require(previous is not None,'result-revision-not-found')
                older=self._object(previous)
                require(older.ref.kind=='work.submission' and older.payload['work']==work and
                        older.payload['workspace']==plan.payload['workspace'] and link(older,'plan')==plan.ref and
                        older.payload['revision']+1==result.payload['revision'],'submission-sequence-mismatch')
                steps+=1;require(steps<=10000,'history-page-limit');result=older
        def value(mapping):
            body=map_get(mapping,path,self.store.load)
            if body is None:return dict(exists=False)
            payload=descriptor(body,self.store.load(body)).payload;data=bytearray();large=False
            for chunk in body_bytes(body,self.store.load):
                if len(data)+len(chunk)<=text_limit and not large:data.extend(chunk)
                else:large=True;data.clear()
            text_value=None
            if not large:
                try:
                    decoded=bytes(data).decode('utf-8')
                    if '\x00' not in decoded:text_value=decoded
                except UnicodeDecodeError:pass
            return dict(exists=True,size=payload['size'],sha256=payload['sha256'],text=text_value,
                        display='text' if text_value is not None else ('too-large' if large else 'binary'))
        from .scope_addition import history
        created_later = any(path in amendment.payload['create'] for amendment,_ in history(result, self.store.load))
        return dict(work=work,title=plan.payload['title'],path=path,revision=result.payload['revision'],
                    submission=result.ref.sha256,
                    before_basis='absent-at-additional-approval' if created_later else 'original-plan',
                    before=value(link(plan,'before')),after=value(link(result,'after')))
