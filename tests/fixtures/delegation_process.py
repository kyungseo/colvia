"""Fixed subprocess fixture operations; imported product belongs to one exact source.

No network, shell, credentials, runtime installation outside TARGET or independent
process group. The parent runner owns the sandbox, absolute roots and deadline.
Synthetic fault/lock observations never supply product authorization verdicts.
"""
from __future__ import annotations
import copy
import io
import runpy
from contextlib import redirect_stdout
from unittest import mock
import fcntl
import hashlib
import json
import os
from pathlib import Path
import stat
import subprocess
import sys

TIME = "2026-01-01T00:00:00Z"
ACTIONS = frozenset({"init-preview", "init", "switch-preview", "switch", "repair-preview", "repair",
    "detach-preview", "detach", "status", "verify", "draft", "intent-prepare", "intent-apply",
    "work-publish", "work-prepare", "work-apply", "candidate", "ordinary", "parent", "read-work", "local", "rebind-worker", "parent-readiness"})


def need(value, message):
    if not value: raise RuntimeError(message)


def canonical(value):
    return (json.dumps(value, sort_keys=True, indent=2, ensure_ascii=False, allow_nan=False)+"\n").encode()


def digest(value):
    return hashlib.sha256(canonical(value)).hexdigest()


def git(target, *args):
    from hv2ref.workspace import git_environment
    if args and args[0] == "commit": args = ("-c", "maintenance.auto=false", "-c", "gc.auto=0", *args)
    return subprocess.run(["git", "-C", str(target), *args], env=git_environment(), stdin=subprocess.DEVNULL,
        capture_output=True, check=True, timeout=30).stdout.decode().strip()


def installed_call(target,kind,action,value,*,confirm=None,worker=None,inject_at=None):
    """Run the actual control CLI; optional fault injection keeps its real gate."""
    from contextlib import nullcontext
    from hv2ref.errors import ContractError,InjectedCrash
    patch=nullcontext()
    if inject_at is not None:
        need(type(inject_at) is str and bool(inject_at.strip()),"invalid fixture injection point")
        from hv2ref.work import WorkStore
        from hv2ref.intent import WorkspaceIntentStore
        methods={("intent","draft"):(WorkspaceIntentStore,"publish_draft"),
            ("intent","apply"):(WorkspaceIntentStore,"apply"),("work","apply"):(WorkStore,"apply")}
        need((kind,action) in methods,"unsupported fixture injection route")
        cls,method=methods[kind,action]
        original=getattr(cls,method)  # Resolve before changing argv or stdin.
        def injected(self,*args,**kwargs):return original(self,*args,**kwargs,inject_at=inject_at)
        patch=mock.patch.object(cls,method,injected)
    argv=[str(target/"colvia"),kind,action,"--input","-"]
    if confirm is not None:argv += ["--confirm",confirm]
    if worker is not None:argv += ["--worker",str(worker)]
    output=io.StringIO();input_stream=io.TextIOWrapper(io.BytesIO(canonical(value)),encoding="utf-8")
    before_argv,before_stdin=sys.argv,sys.stdin
    try:
        with patch,redirect_stdout(output):
            sys.argv=argv;sys.stdin=input_stream
            try:runpy.run_path(str(target/"colvia"),run_name="__main__")
            except SystemExit as exc:code=exc.code
            else:code=0
    finally:
        sys.argv,sys.stdin=before_argv,before_stdin
        input_stream.close()
    need(type(code) is int and code in (0,65,75),"unexpected fixture CLI exit: "+repr(code))
    result=json.loads(output.getvalue())
    need(isinstance(result,dict),"fixture CLI output is not an object")
    if code==75:
        need(inject_at is not None and result.get("classification")=="injected-crash"
            and result.get("code")=="HV2-INJECTED-CRASH" and result.get("point")==inject_at,
            "unexpected fixture CLI interruption")
        raise InjectedCrash(inject_at)
    if code==65:
        need(result.get("classification")=="fail" and isinstance(result.get("code"),str)
            and isinstance(result.get("message"),str),"invalid fixture CLI refusal")
        raise ContractError(result["code"],result["message"])
    return result


class InstalledIntent:
    def __init__(self,target):self.target=target
    def publish_draft(self,draft,**kw):return installed_call(self.target,"intent","draft",draft,**kw)
    def prepare(self,iid,ref,**kw):return installed_call(self.target,"intent","prepare",{"intent_id":iid,"revision_ref":ref,**kw})
    def apply(self,ticket,*,confirm_token,**kw):return installed_call(self.target,"intent","apply",ticket,confirm=confirm_token,**kw)


class InstalledWork:
    def __init__(self,target):self.target=target
    def publish(self,identity,revision,manifest,*,selection_id,operation_id,worker=None):
        return installed_call(self.target,"work","publish",{"identity":identity,"revision":revision,"manifest":manifest,
            "selection_id":selection_id,"operation_id":operation_id},worker=worker)
    def prepare(self,wid,**kw):return installed_call(self.target,"work","prepare",{"work_id":wid,"revision_ref":None,"supersedes":None,**kw})
    def apply(self,ticket,*,confirm_token,**kw):return installed_call(self.target,"work","apply",ticket,confirm=confirm_token,**kw)
    def _decision(self,ticket):
        from hv2ref.work import WorkStore
        return WorkStore._decision(ticket)


def fixture_draft(target, iid, wid, *, grant=False, number=1, parent=None):
    from hv2ref.intent import read_workspace_intent_graph
    from hv2ref.work import record_ref
    fmt=json.loads((target/".hrn/format.json").read_bytes()); home=fmt["authority_home_id"]
    prior=None
    if number > 1:
        graph=read_workspace_intent_graph(target,iid)
        previous=[d for d in graph["drafts"].values() if d["sequence"] == number-1]
        need(len(previous)==1,"exact prior draft missing");prior=record_ref(previous[0],"revision_id")
    draft={"record_type":"intent-draft","schema_version":3 if grant else 2 if parent else 1,
        "authority_home_id":home,"intent_id":iid,"revision_id":"draft-"+str(number),"sequence":number,
        "prior_revision_ref":prior,"actor":"agent","acceptance_authority":"owner","observed_at":TIME,
        "facets":{k:{"status":"known","value":"synthetic"} for k in
            ("acceptance_oracle","destination","expected_outcome","forbidden_scope","goal","scope")},
        "gaps":[],"statements":[],"route":"direct-entry"}
    if grant:draft["acceptance_delegation"]={"action":"accept","delegate_actor":"delegate-1",
        "execution_mode":"isolated-worktree","scope":["a","b"],
        "work":{"authority_home_id":home,"kind":"work","id":wid}}
    if parent:draft["composition"]=parent
    return draft


def select_draft(target,draft):
    from hv2ref.intent import WorkspaceIntentStore
    from hv2ref.work import record_ref
    store=InstalledIntent(target)
    store.publish_draft(draft)
    packet=store.prepare(draft["intent_id"],record_ref(draft,"revision_id"),actor="owner",reason="synthetic exact acceptance",
        request_id=draft["intent_id"]+"-accept-"+str(draft["sequence"]),observed_at=TIME)
    graph=store.apply(packet["ticket"],confirm_token=packet["confirm_token"])
    current=graph["selections"][graph["current"]["selection_ref"]["id"]]
    return {"authority_home_id":draft["authority_home_id"],"kind":"intent","id":draft["intent_id"],
        "revision_ref":current["revision_ref"],"acceptance_ref":current["acceptance_ref"],"selection_ref":graph["current"]["selection_ref"]}


def work_fixture(target, request):
    from hv2ref.product import verify_workspace_product
    from hv2ref.work import WorkStore, snapshot, make_manifest, record_ref, read_work
    from hv2ref.errors import ContractError, InjectedCrash
    observed=verify_workspace_product(target)
    runtime={**observed,"inventory_id":observed["inventory"]["inventory_id"]}
    wid=request.get("wid","work-a");iid=request.get("iid","intent-a")
    need((target/".git").is_dir(),"ordinary worker fixture needs primary Git")
    home=json.loads((target/".hrn/format.json").read_bytes())["authority_home_id"]
    intent=select_draft(target,fixture_draft(target,iid,wid,grant=request.get("grant",True)))
    git(target,"add",".")
    if git(target,"diff","--cached","--name-only"):
        git(target,"commit","-qm","synthetic control baseline")
    oid=git(target,"rev-parse","HEAD");base_ref="refs/heads/base-"+wid;git(target,"branch",base_ref[len("refs/heads/"):],oid)
    identity={"record_type":"work-identity","schema_version":1,"authority_home_id":home,"work_id":wid,
        "work_type":"change","created_at":TIME,"acceptance_authority":"owner","lineage":None}
    tree=snapshot(target,verified_launcher_sha256=runtime["launcher_sha256"],verified_inventory_id=runtime["inventory_id"])
    manifest=make_manifest(tree,tree,scope=["a","b"],base_commit=oid,candidate_commit=oid,
        base_retention_ref=base_ref,candidate_retention_ref=base_ref)
    revision={"record_type":"work-revision","schema_version":1,"authority_home_id":home,"work_id":wid,
        "record_id":"revision-1","observed_at":TIME,"observed_scope":[],"unavailable_scope":[],"author":"agent",
        "operation":"start","expected_prior_selection":None,"intent_ref":intent,"scope":["a","b"],
        "document_refs":[],"evidence_refs":[],"result_refs":{"manifest":{"id":digest(manifest),"sha256":digest(manifest)}},
        "progress":"active","next_action":"synthetic worker","relations":request.get("relations",[]),"rebind_from":None,
        "execution_context":{"mode":"isolated-worktree","attempt_id":"attempt-1"}}
    store=InstalledWork(target)
    graph=store.publish(identity,revision,manifest,selection_id="selection-1",operation_id="operation-1")
    if request.get("stage")=="baseline":return {"graph":graph,"identity":identity,"revision":revision,"manifest":manifest}
    worker=Path(request["worker"]);need(worker.parent==target.parent and not worker.exists(),"worker root")
    branch="candidate-"+wid;git(target,"worktree","add","-q","-b",branch,str(worker),oid)
    (worker/"a").write_bytes((wid+" result-a\n").encode())
    if request.get("change_b",True):(worker/"b").write_bytes((wid+" result-b\n").encode())
    git(worker,"add","a","b");git(worker,"commit","-qm","synthetic worker result")
    result=snapshot(worker,verified_launcher_sha256=runtime["launcher_sha256"],verified_inventory_id=runtime["inventory_id"])
    candidate=make_manifest(tree,result,scope=["a","b"],base_commit=oid,candidate_commit=git(worker,"rev-parse","HEAD"),
        base_retention_ref=base_ref,candidate_retention_ref="refs/heads/"+branch)
    submitted={**revision,"record_id":"revision-2","operation":"submit-result","expected_prior_selection":graph["current"]["selection_ref"],
        "result_refs":{"manifest":{"id":digest(candidate),"sha256":digest(candidate)}},"progress":"review",
        "execution_context":{"mode":"isolated-worktree","attempt_id":"attempt-2"}}
    graph=store.publish(identity,submitted,candidate,selection_id="selection-2",operation_id="operation-2",worker=worker)
    if request.get("stage")=="submitted":return {"graph":graph,"identity":identity,"revision":submitted,"manifest":candidate}
    packet=store.prepare(wid,action="accept",actor=request.get("actor","delegate-1"),reason="synthetic delegated acceptance",
        request_id="accept-"+wid,observed_at=TIME)
    if request.get("stage")=="prepared":return packet
    stage=request.get("stage","accepted")
    if stage=='duplicate-checked':
        other=store.prepare(wid,action='accept',actor=request.get('actor','delegate-1'),reason='second valid request',request_id='duplicate-'+wid,observed_at=TIME)
        try:store.apply(packet['ticket'],confirm_token=packet['confirm_token'],inject_at='after-decision')
        except InjectedCrash:pass
        else:raise RuntimeError('missing installed interruption')
        def protected():
            return {str(p.relative_to(target)):(stat.S_IMODE(p.stat().st_mode),p.read_bytes()) for p in target.rglob('*') if p.is_file() and '.hrn/locks/' not in str(p)}
        for altered,reason in ((other,'delegation already consumed'),(copy.deepcopy(packet),'request ID reused with different ticket')):
            if altered['ticket']['request_id']==packet['ticket']['request_id']:
                altered['ticket']['reason']='same request ID, changed valid body';altered['confirm_token']=digest(altered['ticket'])[:16]
            before=protected()
            try:store.apply(altered['ticket'],confirm_token=altered['confirm_token'])
            except ContractError as exc:need(reason in exc.message,'wrong installed refusal: '+exc.message)
            else:raise RuntimeError('installed duplicate accepted')
            need(before==protected(),'installed refusal changed bytes/modes')
        graph=store.apply(packet['ticket'],confirm_token=packet['confirm_token'])
    elif stage=="cancelled":
        try:store.apply(packet["ticket"],confirm_token=packet["confirm_token"],inject_at="after-decision")
        except InjectedCrash:pass
        else:raise RuntimeError("missing expected interruption")
        decision=store._decision(packet["ticket"])
        cancel=store.prepare(wid,action="reject",actor="owner",reason="synthetic all-pre cancellation",
            request_id="cancel-"+wid,observed_at=TIME,supersedes=record_ref(decision))
        graph=store.apply(cancel["ticket"],confirm_token=cancel["confirm_token"])
    else:
        graph=store.apply(packet["ticket"],confirm_token=packet["confirm_token"])
        if stage=="revoked":
            revoke=store.prepare(wid,action="revoke",actor="owner",reason="synthetic revocation",
                request_id="revoke-"+wid,observed_at=TIME,supersedes=record_ref(store._decision(packet["ticket"])))
            graph=store.apply(revoke["ticket"],confirm_token=revoke["confirm_token"])
    return {"graph":graph,"acceptance":packet,"intent":intent}


def local_fixture(target,request):
    """Installed local schema1 baseline/result, with no content mutation."""
    from hv2ref.product import verify_workspace_product
    from hv2ref.work import snapshot,make_manifest,record_ref
    wid=request.get('wid','local-work');iid='intent-'+wid
    home=json.loads((target/'.hrn/format.json').read_bytes())['authority_home_id']
    intent=select_draft(target,fixture_draft(target,iid,wid))
    runtime=verify_workspace_product(target)
    tree=snapshot(target,verified_launcher_sha256=runtime['launcher_sha256'],verified_inventory_id=runtime['inventory']['inventory_id'])
    manifest=make_manifest(tree,tree,scope=['a','b'])
    identity={'record_type':'work-identity','schema_version':1,'authority_home_id':home,'work_id':wid,'work_type':'change','created_at':TIME,'acceptance_authority':'owner','lineage':None}
    revision={'record_type':'work-revision','schema_version':1,'authority_home_id':home,'work_id':wid,'record_id':'local-1','observed_at':TIME,'observed_scope':[],'unavailable_scope':[],'author':'agent','operation':'start','expected_prior_selection':None,'intent_ref':intent,'scope':['a','b'],'document_refs':[],'evidence_refs':[],'result_refs':{'manifest':{'id':digest(manifest),'sha256':digest(manifest)}},'progress':'active','next_action':'human review','relations':[],'rebind_from':None,'execution_context':{'mode':'local','attempt_id':'local-1'}}
    store=InstalledWork(target);graph=store.publish(identity,revision,manifest,selection_id='local-1',operation_id='local-1')
    revision={**revision,'record_id':'local-2','operation':'submit-result','progress':'review','expected_prior_selection':graph['current']['selection_ref']}
    graph=store.publish(identity,revision,manifest,selection_id='local-2',operation_id='local-2')
    return {'graph':graph,'snapshot':tree}


def rebind_worker(target,request):
    """Explicit control Git integration, Owner rebind and fresh submission."""
    from hv2ref.product import verify_workspace_product
    from hv2ref.work import snapshot,make_manifest,record_ref,read_work
    wid=request['wid'];graph=read_work(target,wid);identity=graph['identity']
    selected=graph['selections'][graph['current']['selection_ref']['id']]
    prior=graph['revisions'][selected['revision_ref']['id']]
    runtime=verify_workspace_product(target);store=InstalledWork(target)
    git(target,'add','colvia');git(target,'commit','-qm','synthetic integration of exact new launcher')
    oid=git(target,'rev-parse','HEAD');base_ref='refs/heads/rebind-base-'+wid;git(target,'branch',base_ref[len('refs/heads/'):],oid)
    tree=snapshot(target,verified_launcher_sha256=runtime['launcher_sha256'],verified_inventory_id=runtime['inventory']['inventory_id'])
    manifest=make_manifest(tree,tree,scope=prior['scope'],base_commit=oid,candidate_commit=oid,base_retention_ref=base_ref,candidate_retention_ref=base_ref)
    revision={**prior,'record_id':'revision-3','operation':'rebind','rebind_from':prior['intent_ref'],'progress':'active','expected_prior_selection':graph['current']['selection_ref'],'execution_context':{'mode':'isolated-worktree','attempt_id':'rebind-3'},'result_refs':{'manifest':{'id':digest(manifest),'sha256':digest(manifest)}}}
    store.publish(identity,revision,manifest,selection_id='unused-rebind-selection',operation_id='rebind-publication')
    packet=store.prepare(wid,action='rebind',actor='owner',reason='explicit post-transition baseline',request_id='rebind-'+wid,observed_at=TIME,revision_ref=record_ref(revision))
    graph=store.apply(packet['ticket'],confirm_token=packet['confirm_token'])
    worker=Path(request['worker']);need(worker.parent==target.parent and not worker.exists(),'fresh rebind worker root')
    branch='rebound-'+wid;git(target,'worktree','add','-q','-b',branch,str(worker),oid)
    old_worker=target.parent/(target.name+'-worker-'+wid)
    for name in ('a','b'):(worker/name).write_bytes((old_worker/name).read_bytes())
    git(worker,'add','a','b');git(worker,'commit','-qm','synthetic rebound result')
    result=snapshot(worker,verified_launcher_sha256=runtime['launcher_sha256'],verified_inventory_id=runtime['inventory']['inventory_id'])
    manifest=make_manifest(tree,result,scope=prior['scope'],base_commit=oid,candidate_commit=git(worker,'rev-parse','HEAD'),base_retention_ref=base_ref,candidate_retention_ref='refs/heads/'+branch)
    revision={**revision,'record_id':'revision-4','operation':'submit-result','rebind_from':None,'progress':'review','expected_prior_selection':graph['current']['selection_ref'],'execution_context':{'mode':'isolated-worktree','attempt_id':'resubmit-4'},'result_refs':{'manifest':{'id':digest(manifest),'sha256':digest(manifest)}}}
    store.publish(identity,revision,manifest,selection_id='selection-4',operation_id='submission-4',worker=worker)
    packet=store.prepare(wid,action='accept',actor='owner',reason='resubmitted exact source',request_id='new-accept-'+wid,observed_at=TIME)
    return store.apply(packet['ticket'],confirm_token=packet['confirm_token'])


def parent_fixture(target,request):
    from hv2ref.product import verify_workspace_product
    from hv2ref.work import snapshot,make_manifest
    home=json.loads((target/".hrn/format.json").read_bytes())["authority_home_id"]
    wid=request.get("wid","parent");child=request.get("child","accepted-work");iid=request.get("iid","parent-intent")
    composition={"parent":{"authority_home_id":home,"kind":"work","id":wid},"required_children":[
        {"work":{"authority_home_id":home,"kind":"work","id":child},"intent":{"authority_home_id":home,"kind":"intent","id":"intent-"+child}}]}
    intent=select_draft(target,fixture_draft(target,iid,wid,parent=composition))
    (target/"report.md").write_bytes(b"synthetic parent baseline\n")
    runtime=verify_workspace_product(target)
    tree=snapshot(target,verified_launcher_sha256=runtime["launcher_sha256"],verified_inventory_id=runtime["inventory"]["inventory_id"])
    manifest=make_manifest(tree,tree,scope=["report.md"])
    identity={"record_type":"work-identity","schema_version":1,"authority_home_id":home,"work_id":wid,
        "work_type":"integration","created_at":TIME,"acceptance_authority":"owner","lineage":None}
    revision={"record_type":"work-revision","schema_version":2,"authority_home_id":home,"work_id":wid,
        "record_id":"revision-1","observed_at":TIME,"observed_scope":[],"unavailable_scope":[],"author":"agent",
        "operation":"start","expected_prior_selection":None,"intent_ref":intent,"scope":["report.md"],
        "document_refs":[],"evidence_refs":[],"result_refs":{"manifest":{"id":digest(manifest),"sha256":digest(manifest)}},
        "progress":"active","next_action":"human integration","relations":[],"rebind_from":None,
        "execution_context":{"mode":"local","attempt_id":"parent-1"},"umbrella_evidence":{"children":[],"integration_document":None}}
    return InstalledWork(target).publish(identity,revision,manifest,selection_id="parent-selection",operation_id="parent-start")


def dispatch(source,target,request):
    from hv2ref import product as product
    from hv2ref.intent import WorkspaceIntentStore
    from hv2ref.work import WorkStore, read_work
    from hv2ref.candidates import CandidateStore
    action=request["action"];need(action in ACTIONS,"unlisted fixture action")
    binding_path=target/".hrn/product/binding.json"
    installed=False
    if binding_path.is_file():
        binding=json.loads(binding_path.read_bytes())
        installed=source==target/".hrn/product/releases"/binding["active_release"]["id"]/"payload"
    intents=InstalledIntent(target) if installed else WorkspaceIntentStore(target)
    works=InstalledWork(target) if installed else WorkStore(target)
    op=request.get("operation_id","fixture-"+action)
    if action in ("init-preview","init"):
        packet=request.get("packet") or product.workspace_init_preview(source,target,authority_home_id="home-a",operation_id=op,created_at=TIME)
        return packet if action=="init-preview" else product.workspace_init_apply(source,target,packet["request"],confirm_token=packet["confirm_token"],recover=request.get("recover",False),inject_at=request.get("inject_at"))
    if action in ("switch-preview","switch"):
        candidate=Path(request["candidate"]) if request.get("candidate") else None
        packet=request.get("packet") or product.workspace_switch_preview(target,action=request.get("switch_action","update"),source=candidate,operation_id=op,created_at=TIME)
        return packet if action=="switch-preview" else product.workspace_switch_apply(target,packet["request"],confirm_token=packet["confirm_token"],source=candidate,recover=request.get("recover",False),inject_at=request.get("inject_at"))
    if action in ("repair-preview","repair"):
        packet=request.get("packet") or product.workspace_repair_preview(source,target,Path(request["backup"]),operation_id=op,created_at=TIME)
        return packet if action=="repair-preview" else product.workspace_repair_apply(source,target,packet["request"],confirm_token=packet["confirm_token"],recover=request.get("recover",False),inject_at=request.get("inject_at"))
    if action in ("detach-preview","detach"):
        packet=request.get("packet") or product.workspace_detach_preview(target,operation_id=op,created_at=TIME)
        return packet if action=="detach-preview" else product.workspace_detach_apply(target,packet["request"],confirm_token=packet["confirm_token"],recover=request.get("recover",False),inject_at=request.get("inject_at"))
    if action=="status":return product.workspace_status(target)
    if action=="verify":return product.verify_workspace_product(target)
    if action=="read-work":return read_work(target,request.get("wid","work-a"))
    if action=="ordinary":return work_fixture(target,request)
    if action=="parent":return parent_fixture(target,request)
    if action=='local':return local_fixture(target,request)
    if action=='rebind-worker':return rebind_worker(target,request)
    if action=='parent-readiness':
        from hv2ref.intent import workspace_intents
        from hv2ref.umbrella import capture,check_history
        works=WorkStore(target)._all();intents=workspace_intents(target);parent=works[request.get('wid','parent')]
        selected=parent['selections'][parent['current']['selection_ref']['id']];revision=parent['revisions'][selected['revision_ref']['id']]
        intent=intents[revision['intent_ref']['id']];draft=intent['drafts'][revision['intent_ref']['revision_ref']['id']]
        composition=draft['composition'];captured=capture(composition,works,intents)
        check_history(composition,{'children':captured['children'],'integration_document':None},works,intents,submitted=False)
        return captured
    if action=="draft":
        draft=request.get("draft") or fixture_draft(target,request.get("iid","intent-a"),request.get("wid","work-a"),grant=request.get("grant",False),number=request.get("number",1))
        return select_draft(target,draft) if request.get("select") else intents.publish_draft(draft,inject_at=request.get("inject_at"))
    if action=="intent-prepare":
        from hv2ref.work import record_ref
        draft=request["draft"]
        return intents.prepare(draft["intent_id"],record_ref(draft,"revision_id"),actor="owner",reason="synthetic intent",request_id=op,observed_at=TIME)
    if action=="intent-apply":return intents.apply(request["packet"]["ticket"],confirm_token=request["packet"]["confirm_token"],inject_at=request.get("inject_at"))
    if action=="work-publish":return works.publish(request["identity"],request["revision"],request["manifest"],selection_id=request["selection_id"],operation_id=op)
    if action=="work-prepare":return works.prepare(request.get("wid","work-a"),action=request.get("decision_action","accept"),actor=request.get("actor","owner"),reason="synthetic work",request_id=op,observed_at=TIME)
    if action=="work-apply":return works.apply(request["packet"]["ticket"],confirm_token=request["packet"]["confirm_token"],inject_at=request.get("inject_at"))
    if action=="candidate":return installed_call(target,"candidate",request["request"]["action"],request["request"]) if installed else CandidateStore(target).mutate(request["request"])
    raise RuntimeError("unimplemented fixed fixture action")


def main():
    need(len(sys.argv)==3 and sys.flags.isolated and sys.flags.no_site and sys.dont_write_bytecode,"isolated SOURCE TARGET required")
    source,target=map(lambda v:Path(v).absolute(),sys.argv[1:])
    for path in (source,target):
        need(not path.is_symlink(),"linked fixture root")
    raw=sys.stdin.buffer.read(4*1024*1024+1);need(len(raw)<=4*1024*1024,"oversized fixture request")
    request=json.loads(raw)
    sys.path.insert(0,str(source/"src"))
    from hv2ref.errors import ContractError, InjectedCrash
    from hv2ref import product as product
    # Observe the native flock without changing its operation or return value.
    # A parent-held native guard supplies ordering; there is no sleep ordering.
    lock=request.pop("lock_observation",None)
    if lock:
        native=fcntl.flock; expected=(target/".hrn/locks/writer.lock").stat()
        def observed(fd,operation):
            number=fd.fileno() if hasattr(fd,"fileno") else fd
            info=os.fstat(number)
            matches=(info.st_dev,info.st_ino)==(expected.st_dev,expected.st_ino) and operation & fcntl.LOCK_EX
            if matches:
                with Path(lock["attempt"]).open("xb") as f:f.write(canonical({"pid":os.getpid(),"pgid":os.getpgrp(),"dev":info.st_dev,"ino":info.st_ino,"operation":operation}));f.flush();os.fsync(f.fileno())
            result=native(fd,operation)
            if matches:
                with Path(lock["acquired"]).open("xb") as f:f.write(canonical({"pid":os.getpid(),"pgid":os.getpgrp(),"dev":info.st_dev,"ino":info.st_ino}));f.flush();os.fsync(f.fileno())
            return result
        fcntl.flock=observed
    code=0
    try:result=dispatch(source,target,request)
    except InjectedCrash as exc:result={"injected":exc.point,"code":exc.code};code=86
    except ContractError as exc:result={"code":exc.code,"message":exc.message};code=65
    for name,module in tuple(sys.modules.items()):
        if name=="hv2ref" or name.startswith("hv2ref."):
            need(Path(module.__file__).is_relative_to(source/"src"),"cross-lane product import")
    print(json.dumps(result,sort_keys=True,ensure_ascii=False,default=str))
    return code


if __name__=="__main__":raise SystemExit(main())
