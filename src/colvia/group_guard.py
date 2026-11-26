"""CAS-observed membership, shared by every member mutation entry point."""
from .codec import require
from .records import link, head_summary
from .group_records import get, key, member_key, plan_for, member_refs


def guard(view,work,transition='other',*,previous=None,candidate=None):
    load=view if callable(view) else view.load
    membership=view.head(member_key(work))
    if membership is None: return
    member=get(membership,load); selected=view.head(key(member.payload['group']))
    require(selected is not None and plan_for(selected,load).ref==link(member,'plan'), 'group-membership-changed')
    require(transition=='ordinary' and previous is not None and candidate is not None, 'group-shared-decision-required')
    old,_,_,_=head_summary(previous,load); new,_,_,_=head_summary(candidate,load)
    require(all(link(old,k)==link(new,k) for k in ('plan','approval','context')), 'group-approved-scope-fixed')
    result=link(new,'result')
    require(result is None or result.version==1,'group-ordinary-submission-required')
    phases=(old.payload['phase'],new.payload['phase'])
    if phases==('completed','completed'):
        require(all(link(old,k)==link(new,k) for k in ('result','decision')), 'group-shared-decision-required'); return
    require(phases[0]!='completed','group-completed-new-work-required')
    require(phases in (('approved','active'),('active','review'),('review','active')), 'group-shared-decision-required')
    obj=get(selected,load)
    if obj.ref.kind=='group.review': obj=get(link(obj,'candidate'),load)
    if obj.ref.kind=='group.candidate': obj=get(link(obj,'approval'),load)
    require(obj.ref.kind=='group.approval', 'group-live-approval-required')
    plan=plan_for(obj.ref,load); i=plan.payload['works'].index(work)
    require(link(new,'approval')==member_refs(obj,'approval',plan,load)[i], 'group-live-approval-required')



def guard_workspaces(view,workspaces,*,group_plan=None):
    """A live group reserves its source and destination workspace roles; terminal history does not."""
    from .maps import read_map
    for name,ref in read_map(view.root().heads,view).items():
        if not name.startswith('group:'): continue
        current=get(ref,view)
        if ref.kind=='group.effect' and current.payload['state']=='completed': continue
        plan=plan_for(ref,view)
        if plan.ref==group_plan: continue
        require(not set(workspaces).intersection([*plan.payload['sources'],plan.payload['destination']]),'group-workspace-in-use')
