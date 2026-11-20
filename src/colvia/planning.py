"""Candidates and follow-up choices share the authority without starting work."""
from .codec import decode_envelope,require
from .graph import Schema,validate_closure
from .maps import scan_map
from .records import fields,text,one,record,link,application_registry,operation_closure,head_summary
from .storage.sqlite import _token
from .work import work_key


def _candidate(p):
    fields(p,{'candidate','title','reason','state','work'})
    _token(p['candidate']);text(p['title'],256);text(p['reason'])
    require(p['state'] in ('open','dismissed'),'invalid-candidate-state')
    require((p['work'] is None)==(not p['links']['work']),'candidate-work-mismatch')
    if p['work'] is not None:_token(p['work'])
    one(p,'work',True);one(p,'previous',True)


def _followup(p):
    fields(p,{'work','choice','target','statement'});_token(p['work']);text(p['statement'])
    require(p['choice'] in ('candidate','work','none','undecided'),'invalid-followup-choice')
    require((p['target'] is None)==(p['choice'] in ('none','undecided')),'invalid-followup-target')
    if p['target'] is not None:_token(p['target'])
    one(p,'source');one(p,'target',True);one(p,'previous',True)
    require(bool(p['links']['target'])==(p['target'] is not None),'followup-link-mismatch')


def planning_schemas():
    from .candidate_priority import schema as priority_schema
    return [priority_schema(), Schema('planning.candidate',1,{'work':'provenance','previous':'provenance'},_candidate,
                   {'work':frozenset({'work.plan'}),'previous':frozenset({'planning.candidate'})}),
            Schema('planning.followup',1,{'source':'provenance','target':'provenance','previous':'provenance'},_followup,
                   {'source':frozenset({'work.head'}),'target':frozenset({'work.head','planning.candidate'}),'previous':frozenset({'planning.followup'})})]


def candidate_key(candidate):_token(candidate);return 'candidate:'+candidate

def followup_key(work):_token(work);return 'followup:'+work


def page_heads(store, prefix, *, limit=20, cursor=None, mode='all'):
    require(type(limit) is int and 1 <= limit <= 100, 'invalid-page-limit')
    require(mode in ('all','archived','current'), 'invalid-list-mode')
    root = store.root()
    offset = 0
    if cursor is not None:
        expected = {'root','offset'} if mode == 'all' else {'root','offset','mode'}
        require(isinstance(cursor, dict) and set(cursor) == expected
                and cursor.get('mode','all') == mode and cursor['root'] == root.ref.as_dict()
                and type(cursor['offset']) is int and 0 <= cursor['offset'] <= 1_000_000,
                'list-changed-or-invalid-cursor')
        offset = cursor['offset']
    values = []
    next_cursor = None
    registry = application_registry() if mode != 'all' else None
    entries = ((key,ref) for key,ref in scan_map(root.heads,store.load) if key.startswith(prefix))
    for index, (key,ref) in enumerate(entries):
        if index < offset:
            continue
        if registry is not None:
            require(ref.kind == 'work.head','wrong-work-head')
            head = registry.inspect(ref,store.load(ref),required=True)
            archived = head.payload['archived']
            if mode == 'archived' and not archived:
                continue
            if mode == 'current' and (archived or head.payload['phase']=='discarded'):
                continue
        if len(values) == limit:
            next_cursor = dict(root=root.ref.as_dict(),offset=index)
            if mode != 'all':
                next_cursor['mode'] = mode
            break
        values.append((key,ref))
    require(store.root().ref == root.ref,'list-changed')
    return values,next_cursor


class Planning:
    def __init__(self,store):self.store=store

    def _obj(self,ref):
        registry=application_registry();obj=registry.inspect(ref,self.store.load(ref),required=True)
        require(obj is not None,'required-record-unavailable');return obj

    def save_candidate(self,*,operation,candidate,title,reason,state='open',work=None,expected=None):
        key=candidate_key(candidate);current=self.store.head(key)
        require(current==expected,'candidate-changed')
        selected=self.store.head(work_key(work)) if work is not None else None
        require(work is None or selected is not None,'linked-work-not-found')
        plan=None
        if selected is not None:
            head=self._obj(selected);require(head.ref.kind=='work.head' and head.payload['work']==work,'wrong-linked-work')
            plan=link(head,'plan')
        ref,raw=record('planning.candidate',dict(candidate=candidate,title=title,reason=reason,state=state,work=work),
                       {'work':('provenance',plan),'previous':('provenance',current)})
        def validate(load):
            from .effects import guard
            guard(load)
            registry=application_registry();registry.inspect(ref,load(ref),required=True)
            if work is not None:require(load.head(work_key(work))==selected,'linked-work-changed')
        self.store.commit_heads(operation=operation,expected={key:current},changes={key:ref},objects=[(ref,raw)],validate=validate)
        return self.candidate(candidate)

    def _work_link_state(self,work,plan):
        current=self.store.head(work_key(work))
        if current is None:return 'unavailable'
        head,_,_,_=head_summary(current,self.store.load)
        require(head.payload['work']==work,'wrong-linked-work')
        if link(head,'plan')!=plan:return 'plan-changed'
        if head.payload['phase']=='completed':
            decision=self._obj(link(head,'decision'))
            require(decision.payload['action']=='accept' and link(decision,'result')==link(head,'result'),'linked-acceptance-unavailable')
        return head.payload['phase']

    def candidate(self,candidate,*,display=False):
        ref=self.store.head(candidate_key(candidate));require(ref is not None,'candidate-not-found')
        obj=self._obj(ref);require(obj.ref.kind=='planning.candidate' and obj.payload['candidate']==candidate,'wrong-candidate')
        work=obj.payload['work']
        result=dict(candidate=candidate,title=obj.payload['title'],reason=obj.payload['reason'],state=obj.payload['state'],linked_work=work)
        from .candidate_priority import current_event
        event = current_event(self.store, candidate, self.store.head('priority:' + candidate))
        result['priority'] = event.payload['new'] if event else 'unset'
        if work is not None:
            plan=link(obj,'work')
            result['linked_state']=self._work_link_state(work,plan)
            if display:
                selected=self._obj(plan)
                require(selected.ref.kind=='work.plan' and selected.payload['work']==work,'wrong-linked-work')
                result['linked_title']=selected.payload['title']
        return result

    def choose_followup(self,*,operation,work,choice,target=None,statement,expected=None):
        source=self.store.head(work_key(work));require(source is not None,'work-not-found')
        source_obj=self._obj(source);require(source_obj.payload['work']==work,'wrong-work-head')
        target_key=None
        if choice=='candidate':target_key=candidate_key(target)
        elif choice=='work':target_key=work_key(target)
        selected=self.store.head(target_key) if target_key is not None else None
        require(target_key is None or selected is not None,'followup-target-not-found')
        key=followup_key(work);current=self.store.head(key);require(current==expected,'followup-changed')
        ref,raw=record('planning.followup',dict(work=work,choice=choice,target=target,statement=statement),
            {'source':('provenance',source),'target':('provenance',selected),'previous':('provenance',current)})
        def validate(load):
            from .effects import guard
            guard(load)
            application_registry().inspect(ref,load(ref),required=True)
            require(load.head(work_key(work))==source,'followup-source-changed')
            if target_key is not None:require(load.head(target_key)==selected,'followup-target-changed')
        self.store.commit_heads(operation=operation,expected={key:current},changes={key:ref},objects=[(ref,raw)],validate=validate)
        return self.followup(work)

    def followup(self,work,*,display=False,source_head=None):
        ref=self.store.head(followup_key(work))
        if ref is None:return dict(work=work,choice='undecided',recorded=False,target=None)
        obj=self._obj(ref);require(obj.ref.kind=='planning.followup' and obj.payload['work']==work,'wrong-followup')
        choice,target=obj.payload['choice'],obj.payload['target']
        value=dict(work=work,choice=choice,recorded=True,target=target,statement=obj.payload['statement'])
        if not display:return value

        source=self._obj(link(obj,'source'))
        require(source.ref.kind=='work.head' and source.payload['work']==work,'wrong-followup-source')
        current=source_head if source_head is not None else self.store.head(work_key(work))
        if current is None:
            value['source_state']='unavailable'
        else:
            head=self._obj(current)
            require(head.ref.kind=='work.head' and head.payload['work']==work,'wrong-followup-source')
            if link(head,'plan')!=link(source,'plan'):
                value['source_state']='plan-changed'

        # Resolve the selected record, never a newer relationship sharing its ID.
        if choice=='candidate':
            selected_ref=link(obj,'target')
            selected=self._obj(selected_ref)
            require(selected.ref.kind=='planning.candidate' and selected.payload['candidate']==target,'wrong-followup-target')
            current=self.store.head(candidate_key(target))
            value.update(target_title=selected.payload['title'],
                         target_state=(selected.payload['state'] if current==selected_ref else
                                       'unavailable' if current is None else 'record-changed'))
        elif choice=='work':
            selected,plan,_,_=head_summary(link(obj,'target'),self.store.load)
            require(selected.payload['work']==target,'wrong-followup-target')
            value.update(target_title=selected.payload['title'],target_state=self._work_link_state(target,plan.ref))
        return value

    def candidates(self,*,limit=20,cursor=None,display=False):
        root=self.store.root().ref
        values,next_cursor=page_heads(self.store,'candidate:',limit=limit,cursor=cursor)
        items=[self.candidate(key[len('candidate:'):],display=display) for key,ref in values]
        require(self.store.root().ref==root,'list-changed')
        return dict(items=items,next=next_cursor)
