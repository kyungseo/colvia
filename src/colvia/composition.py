"""Direct-child composition records and mandatory Work publication checks.

The parent owns its own result and human acceptance. Child readiness does not
apply child bytes or approve the parent. Historical checks use sealed references;
live gates compare semantic references, so archive alone does not invalidate them.
"""
from .codec import require,decode_envelope,Edge,encode_envelope
from .graph import Schema
from .storage.sqlite import _token
from .tree import logical_path


def declaration_key(parent):_token(parent);return 'composition:'+parent

def membership_key(child):_token(child);return 'membership:'+child


def schemas():
    from .records import fields,one,text
    def declaration(p):
        fields(p,{'parent','children','document','checks'});_token(p['parent'])
        children=p['children']
        require(type(children) is list and 0<len(children)<=256 and children==sorted(children),'invalid-composition-children')
        for child in children:_token(child)
        require(len({c.casefold() for c in children})==len(children) and p['parent'].casefold() not in {c.casefold() for c in children},'composition-self-or-alias')
        require(logical_path(p['document'])==p['document'],'invalid-integration-document')
        require(type(p['checks']) is list and p['checks'] and len(set(p['checks']))==len(p['checks']),'invalid-integration-checks')
        for check in p['checks']:text(check,2048)
        one(p,'plan');one(p,'previous',True)
        require(len(p['links']['children'])==len(children),'composition-child-plan-count')
    def membership(p):
        fields(p,{'parent','child'});_token(p['parent']);_token(p['child']);one(p,'declaration');one(p,'plan')
        require(p['parent'].casefold()!=p['child'].casefold(),'composition-self-or-alias')
    def capture(p):
        fields(p,{'child'});_token(p['child'])
        for name in ('plan','result','decision'):one(p,name)
        one(p,'observed')
    def binding(p):
        fields(p,{'parent','action','statement'});_token(p['parent']);text(p['statement']);require(p['action'] in ('declare','rebind'),'invalid-composition-action');one(p,'declaration');one(p,'previous',True)
        require(len(p['links']['captures'])<=256,'composition-capture-limit')
    return [
      Schema('composition.declaration',1,{'plan':'decision','children':'decision','previous':'provenance'},declaration,
        {'plan':frozenset({'work.plan'}),'children':frozenset({'work.plan'}),'previous':frozenset({'composition.declaration'})}),
      Schema('composition.membership',1,{'declaration':'decision','plan':'decision'},membership,
        {'declaration':frozenset({'composition.declaration'}),'plan':frozenset({'work.plan'})}),
      Schema('composition.capture',1,{'plan':'decision','result':'decision','decision':'decision','observed':'provenance'},capture,
        {'plan':frozenset({'work.plan'}),'result':frozenset({'work.submission'}),'decision':frozenset({'work.decision'}),'observed':frozenset({'work.head'})}),
      Schema('composition.binding',1,{'declaration':'decision','captures':'decision','previous':'provenance'},binding,
        {'declaration':frozenset({'composition.declaration'}),'captures':frozenset({'composition.capture'}),'previous':frozenset({'composition.binding'})})]


def refs(obj,name):return [obj.edges[n].ref for n in obj.payload['links'][name]]


def many_record(kind,payload,links):
    edges=[];indices={}
    for name,(role,values) in links.items():
        indices[name]=list(range(len(edges),len(edges)+len(values)))
        edges.extend(Edge(role,ref) for ref in values)
    return encode_envelope(kind,1,{**payload,'links':indices},tuple(edges))


def _get(ref,load):
    from .records import application_registry
    obj=application_registry().inspect(ref,load(ref),required=True)
    require(obj is not None,'composition-reference-unavailable');return obj


def validate_context(head,plan,result,load,*,live=False,validate_capture=None):
    from .records import link
    context=link(head,'context')
    if context is None:return
    obj=_get(context,load);declaration=_get(link(obj,'declaration'),load)
    parent=declaration.payload['parent'];children=declaration.payload['children']
    child_plans=dict(zip(children,refs(declaration,'children')))
    for child,child_plan in child_plans.items():
        require(_get(child_plan,load).payload['work']==child,'composition-declared-plan-mismatch')
    if obj.ref.kind=='composition.membership':
        require(obj.payload=={'parent':parent,'child':plan.payload['work'],'links':obj.payload['links']} and
                child_plans.get(plan.payload['work'])==plan.ref==link(obj,'plan'),'composition-membership-mismatch')
        if live:
            require(load.head(membership_key(plan.payload['work']))==obj.ref and
                    load.head(declaration_key(parent))==declaration.ref,'composition-membership-stale')
        return
    require(obj.ref.kind=='composition.binding' and obj.payload['parent']==plan.payload['work']==parent and
            link(declaration,'plan')==plan.ref,'composition-parent-mismatch')
    require(declaration.payload['document'] in plan.payload['scope'] and
            set(declaration.payload['checks'])<=set(plan.payload['checks']),'composition-integration-scope')
    if live:require(load.head(declaration_key(parent))==declaration.ref,'composition-declaration-stale')
    seen=set()
    from .records import head_summary
    from .work import work_key
    for ref in refs(obj,'captures'):
        cap=_get(ref,load);child=cap.payload['child'];require(child in child_plans and child not in seen,'composition-capture-identity')
        seen.add(child);cp=_get(link(cap,'plan'),load);cr=_get(link(cap,'result'),load);cd=_get(link(cap,'decision'),load)
        require(cp.ref==child_plans[child] and cp.payload['work']==cr.payload['work']==cd.payload['work']==child and
                cp.payload['workspace']==cr.payload['workspace']==cd.payload['workspace'] and
                link(cr,'plan')==cp.ref and link(cd,'result')==cr.ref and cd.payload['action']=='accept','composition-capture-chain')
        # Observed head is provenance, never required to establish a decision.
        # Validate the exact retained plan/result/accept chain independently.
        if validate_capture is not None:validate_capture(cap,load)
        if live and head.payload['phase'] in ('review','completed'):
            current=load.head(work_key(child));require(current is not None,'composition-child-unavailable')
            ch,pp,rr,dd=head_summary(current,load)
            require(ch.payload['phase']=='completed' and pp.ref==cp.ref and rr.ref==cr.ref and dd.ref==cd.ref,'composition-child-changed')
            membership=link(ch,'context');require(membership is not None and membership.kind=='composition.membership','composition-child-membership-required')
            require(load.head(membership_key(child))==membership,'composition-child-membership-stale')
            member=_get(membership,load)
            require(link(member,'declaration')==declaration.ref,'composition-child-membership-stale')
    if head.payload['phase'] in ('review','completed'):
        require(seen==set(children),'composition-required-child-missing')
        require(result is not None,'composition-result-required')
        from .maps import map_get
        require(map_get(link(result,'after'),declaration.payload['document'],load) is not None,'composition-report-required')
        statuses={c['name']:c['status'] for c in result.payload['checks']}
        require(all(statuses.get(c)=='passed' for c in declaration.payload['checks']),'composition-integration-check-failed')


def validate_transition(previous,head,plan,result,load):
    from .records import link
    # Common Work API cannot strip role metadata or replace a bound plan.
    historical_archive=False
    if previous is not None:
        old=_get(previous,load)
        require(link(old,'context')==link(head,'context'),'composition-transition-required')
        if link(old,'context') is not None:require(link(old,'plan')==plan.ref,'composition-rebind-required')
        historical_archive=(old.payload['phase']==head.payload['phase']=='completed' and
            {k:v for k,v in old.payload.items() if k not in ('archived','links')}==
            {k:v for k,v in head.payload.items() if k not in ('archived','links')} and
            all(link(old,key)==link(head,key) for key in ('plan','approval','result','decision','context')))
    if link(head,'context') is None:
        require(load.head(declaration_key(plan.payload['work'])) is None and
                load.head(membership_key(plan.payload['work'])) is None,'composition-context-required')
    validate_context(head,plan,result,load,live=not historical_archive)


class _Prospective:
    """Read the CAS snapshot while validating an atomic set of new heads."""
    def __init__(self,base,changes):self.base=base;self.changes=changes
    def __call__(self,ref):return self.base(ref)
    def head(self,key):
        original=self.base.head(key)
        return self.changes.get(key,original)


class CompositionService:
    def __init__(self,work_service):
        self.work=work_service;self.store=work_service.store

    def _head_with_context(self,old,context):
        from .records import link
        plan=self.work._object(link(old,'plan'))
        return self.work._head_record(plan.ref,plan.payload,old.payload['phase'],
            approval=link(old,'approval'),result=link(old,'result'),decision=link(old,'decision'),
            previous=old.ref,archived=old.payload['archived'],context=context)

    def _publish(self,operation,expected,changes,objects,*,import_id=None,recheck=lambda:None):
        from .effects import guard
        from .connection import PROJECT_KEY,workspace_key
        registration,_,_=self.work.workspace.verify();project=self.store.head(PROJECT_KEY)
        def validate(view):
            guard(view)
            require(view.head(PROJECT_KEY)==project and view.head(workspace_key(self.work.workspace.workspace))==registration,'connection-changed')
            prospective=_Prospective(view,changes)
            from .work_dependencies import check_composition_change
            for key in changes:
                if key.startswith('composition:'):
                    check_composition_change(key.removeprefix('composition:'), view, prospective, self.store.project)
            for key,ref in changes.items():
                if not key.startswith('work:'):continue
                from .group_guard import guard as group_guard
                group_guard(view,key.removeprefix('work:'))
                self.work._validate_head(ref,prospective)
                from .records import head_summary,link
                head,plan,result,_=head_summary(ref,prospective)
                baseline=self.work._object(link(plan,'baseline'),prospective)
                require(view.head(workspace_key(plan.payload['workspace']))==link(baseline,'workspace'),'composition-workspace-changed')
                validate_context(head,plan,result,prospective,live=True)
            recheck()
        self.store.commit_heads(operation=operation,expected=expected,changes=changes,objects=objects,
                                import_id=import_id,validate=validate)

    def declare(self,*,operation,parent,children,document,checks,statement):
        """Attach direct-child roles before approval; this accepts no result."""
        from .records import link,record,text
        from .work import work_key
        text(statement);children=sorted(children);checks=list(checks)
        parent_ref,ph=self.work._head(parent)
        require(ph.payload['phase']=='planned' and link(ph,'context') is None,'composition-parent-must-be-unbound-plan')
        require(0<len(children)<=256 and len(set(c.casefold() for c in children))==len(children) and
                parent.casefold() not in {c.casefold() for c in children},'composition-self-or-alias')
        plan=self.work._object(link(ph,'plan'))
        heads=[]
        for child in children:
            _,head=self.work._head(child,same_workspace=False)
            require(head.payload['phase']=='planned' and link(head,'context') is None,'composition-child-must-be-unbound-plan')
            heads.append(head)
        declaration= many_record('composition.declaration',dict(parent=parent,children=children,document=document,checks=checks),
            {'plan':('decision',[plan.ref]),'children':('decision',[link(h,'plan') for h in heads]),'previous':('provenance',[])})
        binding=many_record('composition.binding',dict(parent=parent,action='declare',statement=statement),
            {'declaration':('decision',[declaration[0]]),'captures':('decision',[]),'previous':('provenance',[])})
        objects=[declaration,binding];expected={work_key(parent):parent_ref,declaration_key(parent):None,membership_key(parent):None}
        newhead=self._head_with_context(ph,binding[0]);objects.append(newhead)
        changes={work_key(parent):newhead[0],declaration_key(parent):declaration[0]}
        for child,head in zip(children,heads):
            member=record('composition.membership',dict(parent=parent,child=child),
                {'declaration':('decision',declaration[0]),'plan':('decision',link(head,'plan'))})
            childhead=self._head_with_context(head,member[0]);objects.extend([member,childhead])
            expected.update({work_key(child):head.ref,membership_key(child):None,declaration_key(child):None})
            changes.update({work_key(child):childhead[0],membership_key(child):member[0]})
        self._publish(operation,expected,changes,objects)
        return self.work.plan_review(parent)

    def _rebind_selection(self,parent,children):
        from .records import link
        pref,ph=self.work._head(parent);context=link(ph,'context')
        require(context is not None and context.kind=='composition.binding','composition-parent-required')
        binding=self.work._object(context);declaration=self.work._object(link(binding,'declaration'))
        selected=sorted(declaration.payload['children'] if children is None else children)
        require(0<len(selected)<=256 and len({c.casefold() for c in selected})==len(selected) and
                parent.casefold() not in {c.casefold() for c in selected},'composition-self-or-alias')
        heads={}
        for child in sorted(set(selected)|set(declaration.payload['children'])):
            _,head=self.work._head(child,same_workspace=False);heads[child]=head
            child_context=link(head,'context')
            if child in declaration.payload['children']:
                require(child_context is not None and child_context.kind=='composition.membership','composition-child-membership-stale')
                member=self.work._object(child_context)
                require(member.payload['parent']==parent and link(member,'declaration')==declaration.ref,'composition-child-membership-stale')
            else:require(child_context is None,'composition-child-already-bound')
        return ph,binding,declaration,selected,heads

    def rebind_preview(self,parent,children=None):
        """Bind the exact old and proposed children; replacing roles is explicit."""
        from .codec import canonical_bytes
        import hashlib
        ph,binding,declaration,selected,heads=self._rebind_selection(parent,children)
        shown=[dict(work=child,title=heads[child].payload['title'],state=heads[child].payload['phase'],
                    ready=heads[child].payload['phase']=='completed') for child in selected]
        receipt=hashlib.sha256(canonical_bytes(dict(action='composition-rebind',project=self.store.project,
            instance=self.store.instance,parent=ph.ref.as_dict(),selection=selected,
            heads=[[child,head.ref.as_dict()] for child,head in heads.items()]))).hexdigest()
        removed=[dict(work=child,title=heads[child].payload['title']) for child in declaration.payload['children'] if child not in selected]
        return dict(work=parent,children=shown,removed=removed,receipt=receipt,
                    question='이 구성으로 하위 결과를 연결하고 통합 작업의 새 계획을 확인할까요?')

    def rebind(self,*,operation,parent,receipt,statement,children=None):
        """New parent plan and roles; old child decisions and parent history remain."""
        from .records import link,record,text,encode_observation
        from .work import work_key
        from .observation import verify_scope
        text(statement)
        require(receipt==self.rebind_preview(parent,children)['receipt'],'stale-composition-rebind-receipt')
        ph,old_binding,old_declaration,selected,heads=self._rebind_selection(parent,children)
        pref=ph.ref;old_plan=self.work._object(link(ph,'plan'))
        # New binding/head requires approval even if identical plan bytes deduplicate.
        scope=frozenset(old_plan.payload['scope']);registration,observed=self.work.workspace.observe(protected=scope)
        verify_scope(observed.snapshot.entries,observed.snapshot.entries,scope)
        self.store.begin_import(operation,'composition-rebind')
        before,objects,_=self.work.workspace.capture(scope,observed,operation)
        baseline,extra=encode_observation(observed,registration,self.store,operation);objects.extend(extra)
        payload={key:value for key,value in old_plan.payload.items() if key!='links'}
        plan=record('work.plan',payload,{'baseline':('integrity',baseline),'before':('integrity',before)})
        objects.append(plan);captures=[]
        for child in selected:
            head=heads[child]
            if head.payload['phase']=='completed':
                self.work._validate_head(head.ref,self.store.load)
                cap=record('composition.capture',dict(child=child),{'plan':('decision',link(head,'plan')),
                    'result':('decision',link(head,'result')),'decision':('decision',link(head,'decision')),'observed':('provenance',head.ref)})
                objects.append(cap);captures.append(cap[0])
        declaration=many_record('composition.declaration',
            {**{key:value for key,value in old_declaration.payload.items() if key!='links'},'children':selected},
            {'plan':('decision',[plan[0]]),'children':('decision',[link(heads[c],'plan') for c in selected]),'previous':('provenance',[old_declaration.ref])})
        binding=many_record('composition.binding',dict(parent=parent,action='rebind',statement=statement),
            {'declaration':('decision',[declaration[0]]),'captures':('decision',captures),'previous':('provenance',[old_binding.ref])})
        newhead=self.work._head_record(plan[0],payload,'planned',previous=pref,context=binding[0]);objects.extend([declaration,binding,newhead])
        expected={work_key(parent):pref,declaration_key(parent):old_declaration.ref,membership_key(parent):None}
        changes={work_key(parent):newhead[0],declaration_key(parent):declaration[0]}
        for child,head in heads.items():
            member=None
            if child in selected:
                membership=record('composition.membership',dict(parent=parent,child=child),
                    {'declaration':('decision',declaration[0]),'plan':('decision',link(head,'plan'))})
                objects.append(membership);member=membership[0]
            childhead=self._head_with_context(head,member);objects.append(childhead)
            expected.update({work_key(child):head.ref,membership_key(child):link(head,'context'),declaration_key(child):None})
            changes.update({work_key(child):childhead[0],membership_key(child):member})
        self._publish(operation,expected,changes,objects,import_id=operation,
            recheck=lambda:(require(receipt==self.rebind_preview(parent,children)['receipt'],'stale-composition-rebind-receipt'),
                            self.work._recheck_observation(observed,scope)))
        return self.work.plan_review(parent)
