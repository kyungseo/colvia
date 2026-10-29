"""Explicit delegation-1 matrix; no tests or product imports at discovery time.

Only build_delegation_suite constructs the class, from verified lane inputs.
All native children inherit the controller's sandbox and process group.
"""
from __future__ import annotations
import copy
try:
    import fcntl
except ImportError:
    fcntl = None  # Historical POSIX-only matrix; native Windows uses its separate factory.
import hashlib
import json
import os
from pathlib import Path
import signal
import stat
import subprocess
import sys
import time
import threading
from types import MappingProxyType
import unittest
from unittest import mock

TIME="2026-01-01T00:00:00Z"
NATIVE_TRACE_LIMIT = 32 * 1024 * 1024
PREDECESSOR_SHA="2216a2634eb3fa5d6a8bfa7c7d4847b29fb2443ba7b367156c15b15ddb5a17e0"
SUFFIXES=("fresh_git_non_git","entry_transition","pending_admission","draft_before_acceptance",
    "old_window_rollback","old_writer_prefixes","late_lock_processes","transition_cutpoints",
    "same_window_p_q","repair_detach","historical_pairs","runtime_entries","plain_auditors",
    "capability_inheritance","truth_drift_replay","artifact_inventory")


def need(ok,message):
    if not ok:raise RuntimeError(message)


def canonical(value):
    return (json.dumps(value,sort_keys=True,indent=2,ensure_ascii=False,allow_nan=False)+"\n").encode()


def sha(value):return hashlib.sha256(value).hexdigest()


def snapshot(root, *, scratch=False):
    """Byte/mode snapshot includes Git refs/index; scratch is explicit, not truth."""
    result={}
    for path in sorted(root.rglob("*")):
        name=path.relative_to(root).as_posix()
        if not scratch and (name in {".hrn/locks",".hrn/staging"} or name.startswith((".hrn/locks/",".hrn/staging/"))):continue
        st=path.lstat()
        if stat.S_ISDIR(st.st_mode):result[name]=["directory",stat.S_IMODE(st.st_mode)]
        elif stat.S_ISLNK(st.st_mode):result[name]=["symlink",os.readlink(path)]
        else:
            need(stat.S_ISREG(st.st_mode) and st.st_nlink==1,"special/hardlinked fixture member")
            data=path.read_bytes();result[name]=["file",stat.S_IMODE(st.st_mode),len(data),sha(data)]
    return result


def build_delegation_suite(*, candidate_source, predecessor_source, artifact_source, execution_context):
    """Pure construction; exact context is rechecked without creating fixtures."""
    import common,controller
    need(isinstance(execution_context,MappingProxyType),"immutable context required")
    ctx=dict(execution_context)
    need(set(ctx)=={"schema","phase","invocation_path","invocation_sha256","controls_dir","work_root",
        "runtime_path","runtime_sha256"} and type(ctx["schema"]) is int and ctx["schema"]==2 and ctx["phase"]=="delegation","context shape")
    c,p=common.config(ctx["invocation_path"],ctx["invocation_sha256"])
    need(c["schema"]==4 and c["phase"]=="delegation" and c["factory"] is True,"delegation invocation required")
    need(tuple(map(Path,(candidate_source,predecessor_source,artifact_source)))==(p["source"],p["predecessor"],p["artifacts"]),"factory source mismatch")
    need(Path(common.__file__)==p["controls"]/"common.py" and Path(controller.__file__)==p["controls"]/"controller.py","control import mismatch")
    work=common.unlinked_path(ctx["work_root"])
    need(work.name=="work" and work.parent.name in controller.DELEGATION_RUN_NAMES and work.parent.parent==p["exec"]/"runs","factory work boundary")
    need(ctx["controls_dir"]==str(p["controls"]) and ctx["runtime_path"]==c["runtime"]["path"] and ctx["runtime_sha256"]==c["runtime"]["sha256"],"factory runtime mismatch")
    candidate,old,variant=p["source"],p["predecessor"],p["artifacts"]/"q"
    old_q=p["artifacts"]/"old-q"
    helper=candidate/"tests/fixtures/delegation_process.py"

    class DelegationWindowTests(unittest.TestCase):
        def setUp(self):
            self.base=work/"DelegationWindowTests"/self._testMethodName;self.base.mkdir(parents=True)
            self.children=[];self.serial=0
            self.addCleanup(self.cleanup)

        def cleanup(self):
            errors=[]
            for child in self.children:
                try:
                    if child.poll() is None:
                        child.terminate()
                        try:child.wait(timeout=3)
                        except subprocess.TimeoutExpired:child.kill();child.wait(timeout=3)
                    else:child.wait()
                except (OSError,subprocess.TimeoutExpired) as exc:errors.append((child.pid,type(exc).__name__))
            self.assertEqual([],errors,"child cleanup unavailable; outer controller must verify group absence")

        def directory(self,label):
            self.serial+=1;p=self.base/(str(self.serial)+"-"+label);p.mkdir();return p

        def git(self,target,*args):
            from hv2ref.workspace import git_environment
            if args and args[0]=="commit":args=("-c","maintenance.auto=false","-c","gc.auto=0",*args)
            return subprocess.run([c["git"]["path"],"-C",str(target),*args],capture_output=True,check=True,timeout=30,env=git_environment()).stdout.decode().strip()

        def spawn(self,source,target,request):
            self.serial+=1;input_path=self.base/(str(self.serial)+".input.json");log=self.base/(str(self.serial)+".log")
            input_path.write_bytes(canonical(request))
            command=[ctx["runtime_path"],"-I","-S","-B",*(["-O"] if sys.flags.optimize else []),str(helper),str(source),str(target)]
            with input_path.open("rb") as inp,log.open("xb") as out:
                child=subprocess.Popen(command,stdin=inp,stdout=out,stderr=subprocess.STDOUT,cwd=candidate)
            self.children.append(child);return child,log

        def finish(self,child,log,expected=0):
            code=child.wait(timeout=150)
            self.assertLessEqual(log.stat().st_size,4*1024*1024)
            raw=log.read_bytes()
            if expected is not None:self.assertEqual(expected,code,raw.decode(errors="replace")[-8000:])
            return code,json.loads(raw)

        def call(self,source,target,request,expected=0):return self.finish(*self.spawn(source,target,request),expected)[1]

        def installed(self,target):
            binding=json.loads((target/".hrn/product/binding.json").read_bytes())
            return target/".hrn/product/releases"/binding["active_release"]["id"]/"payload"

        def init(self,source=candidate,*,git=False,label="project"):
            target=self.directory(label);(target/"a").write_bytes(b"before\n");(target/"b").write_bytes(b"before-b\n")
            if git:
                self.git(target,"init","-q");self.git(target,"config","user.name","Synthetic Fixture")
                self.git(target,"config","user.email","synthetic@example.invalid");self.git(target,"config","commit.gpgsign","false")
            self.call(source,target,{"action":"init","operation_id":"init-a"})
            return target

        def transition(self,target,*,source=candidate,op="transition"):
            return self.call(source,target,{"action":"switch-preview","candidate":str(source),"operation_id":op})

        def switch(self,target,packet,*,source=candidate,recover=False,inject=None):
            return self.call(source,target,{"action":"switch","candidate":str(source),"packet":packet,"recover":recover,"inject_at":inject},86 if inject else 0)

        def refusal(self,source,target,request,*,whole=False,reason=None,code=None):
            before=snapshot(target,scratch=whole);result=self.call(source,target,request,65)
            self.assertEqual(before,snapshot(target,scratch=whole));self.assertTrue(result["code"].startswith("HV2-"))
            if reason is not None:self.assertRegex(result['message'],reason)
            if code is not None:self.assertEqual(code,result['code'])
            return result

        def barrier(self,source,target,request,*,whole=False):
            result=self.refusal(source,target,request,whole=whole)
            # Old history rejects schema4 before provenance or request staleness.
            # At T4 the new root launcher refuses its still-old binding instead.
            allowed={('HV2-WORKSPACE-PRODUCT','invalid receipt identity/schema'),
                ('HV2-WORKSPACE-LAUNCHER','invalid or unavailable binding/payload; a pending transition may require recovery from independent trusted source')}
            self.assertIn((result['code'],result['message']),allowed)
            return result

        def positive_before_guard(self,source,target,request):
            # A native lock witness proves the same request passes pre-guard
            # validation before transition. It supplies no runtime verdict.
            if request['action']=='work-prepare':
                self.call(source,target,request);return
            lock=target/'.hrn/locks/writer.lock';self.assertTrue(lock.is_file())
            self.serial+=1;attempt=self.base/('positive-'+str(self.serial)+'.json');acquired=self.base/('positive-acquired-'+str(self.serial)+'.json')
            before=snapshot(target,scratch=True)
            with lock.open('a+b') as held:
                fcntl.flock(held,fcntl.LOCK_EX)
                child,log=self.spawn(source,target,{**request,'lock_observation':{'attempt':str(attempt),'acquired':str(acquired)}})
                try:
                    deadline=time.monotonic()+10
                    while not attempt.exists():
                        self.assertIsNone(child.poll(),log.read_text(errors='replace'));self.assertLess(time.monotonic(),deadline);time.sleep(.01)
                    self.assertFalse(acquired.exists())
                finally:
                    if child.poll() is None:child.terminate()
                    try:child.wait(timeout=5)
                    except subprocess.TimeoutExpired:child.kill();child.wait(timeout=5)
            self.assertEqual(-signal.SIGTERM,child.returncode);self.assertEqual(before,snapshot(target,scratch=True))

        def truth(self,target):
            return {name:value for name,value in snapshot(target).items() if name in {"a","b",".hrn/format.json",".hrn/.gitignore"}
                or name.startswith((".hrn/intents/",".hrn/work/",".hrn/planning/",".git/"))}

        def record(self,target,*,grant=True,stage="accepted",wid="work-a",iid="intent-a",relations=None,change_b=True):
            return self.call(self.installed(target),target,{"action":"ordinary","grant":grant,"stage":stage,
                "actor":"delegate-1" if grant else "owner","wid":wid,"iid":iid,"relations":relations or [],"change_b":change_b,"worker":str(target.parent/(target.name+"-worker-"+wid))})

        def candidate_request(self,target):
            from hv2ref.candidates import read_candidates
            return {"record_type":"candidate-request","schema_version":1,"authority_home_id":"home-a","request_id":"candidate-add",
                "candidate_id":"idea-a","action":"add","expected_sha256":read_candidates(target)["sha256"],"writer":"agent:fixture",
                "owner_statement":"synthetic planning request","reason":"synthetic","observed_at":TIME,
                "payload":{"title":"Synthetic","purpose":"Preserve planning","expected_effect":"Visible","related_candidates":[]}}

        def test_c01_fresh_git_non_git(self):
            for is_git in (False,True):
                with self.subTest(git=is_git):
                    target=self.init(git=is_git);result=self.call(candidate,target,{"action":"verify"})
                    self.assertEqual("delegation-1",result["inventory"]["inventory_id"])
                    plan=json.loads((target/".hrn/product/init-plan.json").read_bytes());receipt=json.loads((target/".hrn/product/receipts/init-a.json").read_bytes())
                    self.assertEqual((4,4),(plan["schema_version"],receipt["schema_version"]))
                    if is_git:self.assertEqual("completed",self.record(target,grant=False)["graph"]["state"])
                    else:self.call(self.installed(target),target,{"action":"draft","select":True})
                    before=snapshot(target);self.assertEqual("pass",self.call(candidate,target,{"action":"status"})["classification"]);self.assertEqual(before,snapshot(target))

        def test_c02_entry_transition(self):
            for is_git in (False,True):
                with self.subTest(git=is_git):
                    target=self.init(old,git=is_git);state=self.call(old,target,{"action":"verify"})
                    self.assertEqual(PREDECESSOR_SHA,sha(canonical(state["inventory"])))
                    self.call(self.installed(target),target,{"action":"draft","select":True})
                    if is_git:
                        self.call(self.installed(target),target,{'action':'parent','child':'worker-a'})
                        local=self.call(self.installed(target),target,{'action':'local'})
                        worker_packet=self.record(target,grant=False,stage='prepared',wid='worker-a',iid='intent-worker-a')
                        worker_path=target.parent/(target.name+'-worker-worker-a');old_worker=snapshot(worker_path,scratch=True)
                    before=self.truth(target);packet=self.transition(target);self.switch(target,packet)
                    self.assertEqual(before,self.truth(target));self.assertEqual("delegation-1",self.call(candidate,target,{"action":"verify"})["inventory"]["inventory_id"])
                    self.assertEqual("home-a",json.loads((target/".hrn/format.json").read_bytes())["authority_home_id"])
                    if is_git:
                        installed=self.installed(target)
                        # Local and parent snapshots remain readable and exclude
                        # the verified same-path launcher; Git refs/index are unchanged above.
                        self.assertEqual('active',self.call(installed,target,{'action':'read-work','wid':'parent'})['state'])
                        packet=self.call(installed,target,{'action':'work-prepare','wid':'local-work','operation_id':'local-after-update'})
                        self.assertEqual('completed',self.call(installed,target,{'action':'work-apply','packet':packet})['state'])
                        refused=self.refusal(installed,target,{'action':'work-apply','packet':worker_packet})
                        self.assertIn('active binding changed',refused['message'])
                        refused=self.refusal(installed,target,{'action':'work-prepare','wid':'worker-a','operation_id':'new-worker-accept'})
                        self.assertIn('commit launcher differs',refused['message'])
                        self.assertEqual('review',self.call(installed,target,{'action':'read-work','wid':'worker-a'})['state'])
                        rebound=self.call(installed,target,{'action':'rebind-worker','wid':'worker-a','worker':str(target.parent/(target.name+'-rebound'))})
                        self.assertEqual('completed',rebound['state']);self.assertEqual(old_worker,snapshot(worker_path,scratch=True))
                        for name in ('a','b'):self.assertEqual((worker_path/name).read_bytes(),(target/name).read_bytes())

        def test_c03_pending_admission(self):
            from hv2ref.product import workspace_init_preview,workspace_init_apply
            from hv2ref.errors import InjectedCrash
            # Old durable switch/detach and incomplete init have visible ownership.
            for action,cut in (("switch","after-receipt"),("detach","after-receipt")):
                with self.subTest(action=action):
                    target=self.init(old)
                    request={"action":action,"operation_id":"old-pending","inject_at":cut}
                    if action=="switch":request["candidate"]=str(old_q)
                    packet=self.call(old,target,{**request,"action":action+"-preview","inject_at":None})
                    self.call(old,target,{**request,"packet":packet},86)
                    self.refusal(candidate,target,{"action":"switch-preview","candidate":str(candidate),"operation_id":"new-transition"})
                    self.call(old,target,{**request,"packet":packet,"inject_at":None,"recover":True})
            for cut in ('after-plan','after-format','after-work','after-receipt','after-launcher-bytes','after-binding'):
                with self.subTest(pending_init=cut):
                    target=self.directory('old-init');packet=self.call(old,target,{'action':'init-preview'})
                    self.call(old,target,{'action':'init','packet':packet,'inject_at':cut},86)
                    if cut!='after-binding':self.refusal(candidate,target,{'action':'switch-preview','candidate':str(candidate)})
                    # after-binding is a completed target with replay sync pending;
                    # no target-only claim of an external pending operation.
                    self.call(old,target,{'action':'init','packet':packet,'recover':True})
                    self.transition(target)
            for kind in ("intent","work"):
                with self.subTest(pending=kind):
                    target=self.init(old,git=kind=="work");payload=self.installed(target)
                    if kind=="intent":
                        graph=self.call(payload,target,{"action":"draft"})
                        packet=self.call(payload,target,{"action":"intent-prepare","draft":graph["drafts"]["draft-1"]})
                        point="after-acceptance"
                    else:packet=self.record(target,grant=False,stage="prepared");point="after-decision"
                    request={"action":kind+"-apply","packet":packet}
                    self.call(payload,target,{**request,"inject_at":point},86)
                    self.refusal(candidate,target,{"action":"switch-preview","candidate":str(candidate)})
                    self.call(payload,target,request)
                    self.transition(target)
            for cut in ('after-backup-request','after-backup'):
                with self.subTest(pending_repair=cut):
                    target=self.init(old);(target/'colvia').write_bytes(b'damaged\n');backup=self.base/(target.name+'-early-backup')
                    packet=self.call(old,target,{'action':'repair-preview','backup':str(backup)})
                    self.call(old,target,{'action':'repair','packet':packet,'inject_at':cut},86)
                    saved=snapshot(backup,scratch=True)
                    self.refusal(candidate,target,{'action':'switch-preview','candidate':str(candidate)})
                    self.assertEqual(saved,snapshot(backup,scratch=True))
                    self.call(old,target,{'action':'repair','packet':packet,'recover':True});self.transition(target)
            # Owner-approved repair tail: no pending marker exists in the target.
            target=self.init(old);launcher=target/"colvia";launcher.write_bytes(b"damaged\n")
            backup=self.base/"repair-backup";packet=self.call(old,target,{"action":"repair-preview","backup":str(backup)})
            self.refusal(candidate,target,{"action":"switch-preview","candidate":str(candidate)})
            self.call(old,target,{"action":"repair","packet":packet,"inject_at":"after-file"},86)
            self.assertFalse((backup/"receipt.json").exists());saved=snapshot(backup,scratch=True)
            transition=self.transition(target);self.switch(target,transition)
            self.barrier(old,target,{"action":"repair","packet":packet,"recover":True},whole=True)
            self.assertEqual(saved,snapshot(backup,scratch=True))

        def test_c04_draft_before_acceptance(self):
            target=self.init(old)
            self.positive_before_guard(self.installed(target),target,{'action':'draft','iid':'other'})
            self.call(old,target,{'action':'switch-preview','candidate':str(old_q)})
            self.call(old,target,{'action':'detach-preview'})
            packet=self.transition(target);self.switch(target,packet)
            self.call(self.installed(target),target,{"action":"draft","grant":True})
            self.assertFalse((target/".hrn/intents/intent-a/current.json").exists())
            for action in ("draft","switch-preview","detach-preview","status"):
                with self.subTest(action=action):
                    request={"action":action,"iid":"other","candidate":str(old_q)}
                    if action=="status":
                        before=snapshot(target);result=self.call(old,target,request);self.assertNotEqual("pass",result["classification"]);self.assertEqual(before,snapshot(target))
                    else:self.barrier(old,target,request)

        def test_c05_old_window_rollback(self):
            positive=self.init(old);self.call(old,positive,{'action':'switch','candidate':str(old_q),'operation_id':'lawful-old-update'})
            self.call(old,positive,{'action':'switch','switch_action':'rollback','operation_id':'lawful-old-rollback'})
            self.assertEqual(PREDECESSOR_SHA,sha(canonical(self.call(old,positive,{'action':'verify'})['inventory'])))
            for cut in ("after-receipt","after-staged-inventory","after-release","after-launcher","after-binding",None):
                with self.subTest(prefix=cut):
                    target=self.init(old)
                    init_bytes=(target/".hrn/product/init-plan.json").read_bytes();init_plan=json.loads(init_bytes)
                    self.assertIs(type(init_plan["schema_version"]),int)
                    self.assertEqual((1,"entry-1"),(init_plan["schema_version"],init_plan["candidate_release"]["inventory_id"]))
                    older_request={"action":"switch-preview","candidate":str(p["old"]),"operation_id":"older-update"}
                    # checkout-1 already cannot read an entry-1 home. This paired
                    # refusal is general incompatibility, not a T1 barrier proof.
                    before=self.refusal(p["old"],target,older_request,code="HV2-WORKSPACE-PRODUCT",reason=r"^root is not ready$")
                    packet=self.transition(target);self.switch(target,packet,inject=cut)
                    binding=json.loads((target/".hrn/product/binding.json").read_bytes())
                    switched=cut in ("after-binding",None)
                    self.assertEqual(packet["request"]["candidate_release"] if switched else init_plan["candidate_release"],binding["active_release"])
                    if switched:self.assertEqual(init_plan["candidate_release"],binding["prior_release"])
                    rollback=self.refusal(candidate,target,{"action":"switch-preview","switch_action":"rollback","operation_id":"downgrade"},code="HV2-WORKSPACE-PRODUCT")
                    expected=("new source switches only to delegation-1; old-window rollback refused" if switched else
                        "pending lifecycle blocks product use; recover exact plan from independent source")
                    self.assertEqual(expected,rollback["message"])
                    self.barrier(old,target,{"action":"switch-preview","candidate":str(old_q),"operation_id":"old-update"})
                    self.assertEqual(init_bytes,(target/".hrn/product/init-plan.json").read_bytes())
                    after=self.refusal(p["old"],target,older_request,code="HV2-WORKSPACE-PRODUCT",reason=r"^root is not ready$")
                    self.assertEqual((before["code"],before["message"]),(after["code"],after["message"]))

        def test_c06_old_writer_prefixes(self):
            for cut in ('after-receipt','after-staged-inventory','after-release','after-launcher','after-binding',None):
                with self.subTest(prefix=cut):
                    target=self.init(old,git=True);payload=self.installed(target)
                    draft=self.call(payload,target,{'action':'draft'})['drafts']['draft-1']
                    intent_packet=self.call(payload,target,{'action':'intent-prepare','draft':draft})
                    material=self.record(target,grant=False,stage='baseline',wid='baseline-work',iid='baseline-intent')
                    work_packet=self.record(target,grant=False,stage='prepared',wid='submitted-work',iid='submitted-intent')
                    revision={**material['revision'],'record_id':'later-checkpoint','operation':'checkpoint','expected_prior_selection':material['graph']['current']['selection_ref'],'execution_context':{'mode':'isolated-worktree','attempt_id':'later'}}
                    requests=[{'action':'draft','iid':'new-intent'}, {'action':'intent-apply','packet':intent_packet},
                        {'action':'candidate','request':self.candidate_request(target)},
                        {'action':'work-publish','identity':material['identity'],'revision':revision,'manifest':material['manifest'],'selection_id':'later-checkpoint','operation_id':'later-checkpoint'},
                        {'action':'work-prepare','wid':'submitted-work','operation_id':'later-prepare'}, {'action':'work-apply','packet':work_packet}]
                    detach=self.call(old,target,{'action':'detach-preview'})
                    update=self.call(old,target,{'action':'switch-preview','candidate':str(old_q),'operation_id':'old-update'})
                    # Precompute a lawful completed repair replay; T1 must block it.
                    (target/'colvia').write_bytes(b'damage\n');backup=self.base/(target.name+'-backup')
                    repair=self.call(old,target,{'action':'repair-preview','backup':str(backup)})
                    self.call(old,target,{'action':'repair','packet':repair});saved=snapshot(backup,scratch=True)
                    for request in requests:self.positive_before_guard(payload,target,request)
                    for request in ({'action':'detach','packet':detach},{'action':'switch','candidate':str(old_q),'packet':update},{'action':'repair','packet':repair,'recover':True}):self.positive_before_guard(old,target,request)
                    packet=self.transition(target);self.switch(target,packet,inject=cut)
                    for source in (old,payload):
                        for request in requests:
                            with self.subTest(source='installed' if source==payload else 'independent',action=request['action']):self.barrier(source,target,request)
                    for request in ({'action':'detach','packet':detach},{'action':'switch','candidate':str(old_q),'packet':update},{'action':'repair','packet':repair,'recover':True}):
                        with self.subTest(lifecycle=request['action']):self.barrier(old,target,request)
                    self.assertEqual(saved,snapshot(backup,scratch=True))
            for cut in ('after-plan','after-format','after-work','after-receipt','after-launcher-bytes','after-binding'):
                with self.subTest(init_prefix=cut):
                    target=self.directory('fresh');packet=self.call(candidate,target,{'action':'init-preview'})
                    self.call(candidate,target,{'action':'init','packet':packet,'inject_at':cut},86)
                    self.refusal(old,target,{'action':'init'},code='HV2-WORKSPACE-PRODUCT',reason='different initialization plan')

        def test_c07_late_lock_processes(self):
            from hv2ref.product import workspace_switch_apply
            from hv2ref.errors import InjectedCrash
            for family in ("draft","intent-apply","candidate","work-publish","work-apply","switch","rollback","repair","detach"):
                with self.subTest(family=family):
                    target=self.init(old_q if family=="rollback" else old,git=family.startswith("work"))
                    if family=="rollback":self.call(old,target,{"action":"switch","candidate":str(old),"operation_id":"prior-update"})
                    payload=self.installed(target)
                    if family=="draft":request={"action":"draft","iid":"late-intent"};source=payload
                    elif family=="intent-apply":
                        graph=self.call(payload,target,{"action":"draft"});draft=graph["drafts"]["draft-1"]
                        packet=self.call(payload,target,{"action":"intent-prepare","draft":draft})
                        request={"action":"intent-apply","packet":packet};source=payload
                    elif family=="candidate":request={"action":"candidate","request":self.candidate_request(target)};source=payload
                    elif family=="work-apply":
                        packet=self.record(target,grant=False,stage="prepared");request={"action":"work-apply","packet":packet};source=payload
                    elif family=="work-publish":
                        material=self.record(target,grant=False,stage="baseline")
                        revision={**material["revision"],"record_id":"late-revision","operation":"checkpoint",
                            "expected_prior_selection":material["graph"]["current"]["selection_ref"],
                            "execution_context":{"mode":"isolated-worktree","attempt_id":"late-attempt"}}
                        request={"action":"work-publish","identity":material["identity"],"revision":revision,
                            "manifest":material["manifest"],"selection_id":"late-selection","operation_id":"late-publish"};source=payload
                    else:
                        request={"action":"switch" if family=="rollback" else family,"operation_id":"late-"+family};source=old
                        if family=="switch":request["candidate"]=str(old_q)
                        if family=="rollback":
                            request["switch_action"]="rollback"
                        if family=="repair":
                            (target/"colvia").write_bytes(b"synthetic damage\n");request["backup"]=str(self.base/(target.name+"-backup"))
                        packet=self.call(source,target,{**request,"action":request["action"]+"-preview"})
                        request["packet"]=packet
                        if family=="repair":self.call(source,target,request);request["recover"]=True
                    transition=self.transition(target)
                    lock=target/".hrn/locks/writer.lock";lock.parent.mkdir(exist_ok=True);lock.touch(exist_ok=True)
                    attempt=self.base/(target.name+"-attempt.json");acquired=self.base/(target.name+"-acquired.json")
                    request["lock_observation"]={"attempt":str(attempt),"acquired":str(acquired)}
                    ready=threading.Event();release=threading.Event();errors=[];new_ident=[];pre_unlock=[]
                    native=fcntl.flock;expected=lock.stat()
                    def new_writer():
                        new_ident.append(threading.get_ident())
                        try:workspace_switch_apply(target,transition["request"],confirm_token=transition["confirm_token"],source=candidate,inject_at="after-receipt")
                        except BaseException as exc:errors.append(exc)
                    def observed(fd,operation):
                        number=fd.fileno() if hasattr(fd,"fileno") else fd;info=os.fstat(number)
                        belongs=new_ident and threading.get_ident()==new_ident[0] and (info.st_dev,info.st_ino)==(expected.st_dev,expected.st_ino)
                        if belongs and operation & fcntl.LOCK_UN:
                            # Capture while the new writer still owns the native lock;
                            # the old waiter cannot mutate before this observation.
                            pre_unlock.append(snapshot(target))
                        result=native(fd,operation)
                        if belongs and operation & fcntl.LOCK_EX:
                            ready.set();need(release.wait(30),"new writer observation deadline")
                        return result
                    with mock.patch.object(fcntl,"flock",observed):
                        thread=threading.Thread(target=new_writer);thread.start()
                        try:
                            self.assertTrue(ready.wait(30),repr(errors));child,log=self.spawn(source,target,request);deadline=time.monotonic()+30
                            while not attempt.exists():
                                self.assertIsNone(child.poll());self.assertLess(time.monotonic(),deadline);time.sleep(0.01)
                            self.assertFalse(acquired.exists())
                        finally:release.set();thread.join(60)
                    self.assertFalse(thread.is_alive());self.assertEqual(1,len(errors));self.assertIsInstance(errors[0],InjectedCrash)
                    self.assertEqual("after-receipt",errors[0].point);self.assertEqual(1,len(pre_unlock))
                    _,refused=self.finish(child,log,65)
                    self.assertEqual(("HV2-WORKSPACE-PRODUCT","invalid receipt identity/schema"),(refused["code"],refused["message"]))
                    self.assertEqual(pre_unlock[0],snapshot(target))
                    row=json.loads(attempt.read_bytes());after=json.loads(acquired.read_bytes())
                    self.assertEqual((child.pid,os.getpgrp(),row["dev"],row["ino"]),(after["pid"],after["pgid"],after["dev"],after["ino"]))

        def native_transition(self,target,packet,event,path,*,length=None):
            self.serial+=1;tag='native-'+self._testMethodName+'-'+str(self.serial)
            scenarios=work/'entry-scenarios';scenarios.mkdir(exist_ok=True)
            scenario=scenarios/(tag+'.json');events=self.base/(tag+'.events.jsonl');request=self.base/(tag+'.stdin');log=self.base/(tag+'.log')
            fault={'event':event,'path':path,'occurrence':1,'write_bytes':length}
            args=['--source-checkout','update','--profile','delegation-1','--target',str(target),'--source',str(candidate),'--apply','--input','-','--confirm',packet['confirm_token']]
            value={'entry':'new-source','target':str(target),'argv':args,'events':str(events),'fault':fault}
            scenario.write_bytes(canonical(value));request.write_bytes(canonical(packet['request']))
            command=common.python_command(c,p,'delegation_observer.py',ctx['invocation_path'],ctx['invocation_sha256'],scenario,sha(canonical(value)),optimized=bool(sys.flags.optimize))
            with request.open('rb') as inp,log.open('xb') as out:child=subprocess.Popen(command,stdin=inp,stdout=out,stderr=subprocess.STDOUT,cwd=candidate)
            self.children.append(child);self.assertEqual(-signal.SIGKILL,child.wait(timeout=150),log.read_text(errors='replace')[-8000:])
            with events.open('rb') as trace:
                self.assertLessEqual(os.fstat(trace.fileno()).st_size,NATIVE_TRACE_LIMIT)
                raw=trace.read(NATIVE_TRACE_LIMIT+1)
            self.assertLessEqual(len(raw),NATIVE_TRACE_LIMIT)
            self.assertTrue(raw.endswith(b'\n'))
            rows=[json.loads(line) for line in raw.splitlines()]
            self.assertEqual(list(range(1,len(rows)+1)),[r['seq'] for r in rows]);self.assertTrue(all(r['pid']==child.pid and r['pgid']==os.getpgrp() for r in rows))
            self.assertFalse(any(r['event']=='observer-refusal' for r in rows));self.assertEqual((event,path),(rows[-1]['event'],rows[-1]['path']))
            self.assertEqual(1,sum((r['event'],r['path'])==(event,path) for r in rows))
            return rows

        def test_c08_transition_cutpoints(self):
            from hv2ref import product
            from hv2ref.errors import ContractError,InjectedCrash
            for cut in ("after-receipt","after-staged-inventory","after-staged-payload","after-release","after-launcher","after-binding"):
                with self.subTest(cut=cut):
                    target=self.init(old);packet=self.transition(target);preserved=self.truth(target)
                    self.switch(target,packet,inject=cut);self.assertEqual(preserved,self.truth(target))
                    self.switch(target,packet,recover=True);after=snapshot(target);self.switch(target,packet,recover=True);self.assertEqual(after,snapshot(target))
            for fault in ("unavailable","oserror"):
                with self.subTest(sync=fault):
                    target=self.init(old);packet=self.transition(target);before=snapshot(target)
                    patch=mock.patch.object(product,"sync_directory",return_value="unavailable") if fault=="unavailable" else mock.patch.object(product,"sync_directory",side_effect=OSError(5,"synthetic sync failure"))
                    with patch,self.assertRaisesRegex(ContractError,"d3-sync"):
                        product.workspace_switch_apply(target,packet["request"],confirm_token=packet["confirm_token"],source=candidate)
                    self.assertEqual(before,snapshot(target))
            # Observe actual receipt/candidate/launcher/binding syscalls and
            # native SIGKILL, including zero and one-byte immutable prefixes.
            from hv2ref.product import workspace_candidate
            rid=workspace_candidate(candidate)['release_ref']['id']
            receipt='.hrn/product/receipts/transition.json'
            inventory='.hrn/staging/switch-transition/'+rid+'/inventory.json'
            release='.hrn/product/releases/'+rid
            cases=[('create-after',receipt,None,False),('raw-write-after',receipt,1,False),('fsync-after',receipt,None,True),
                ('create-after',inventory,None,False),('raw-write-after',inventory,1,False),('fsync-after',inventory,None,True),
                ('rename-after',release,None,True),('replace-after','colvia',None,True),('replace-after','.hrn/product/binding.json',None,True)]
            for event,path,length,recoverable in cases:
                with self.subTest(native_event=event,path=path,length=length):
                    target=self.init(old);packet=self.transition(target);preserved=self.truth(target)
                    rows=self.native_transition(target,packet,event,path,length=length);self.assertEqual(preserved,self.truth(target))
                    if length is not None:self.assertEqual(length,(target/path).stat().st_size)
                    if event=='create-after':self.assertEqual(0,(target/path).stat().st_size)
                    if recoverable:
                        self.switch(target,packet,recover=True);after=snapshot(target);self.switch(target,packet,recover=True);self.assertEqual(after,snapshot(target))
                    else:self.refusal(candidate,target,{'action':'switch','candidate':str(candidate),'packet':packet,'recover':True})
            # Neither/unsafe mode must not be overwritten after launcher publication.
            for damage in ('neither','mode','symlink'):
                with self.subTest(recovery_drift=damage):
                    target=self.init(old);packet=self.transition(target);self.switch(target,packet,inject='after-launcher')
                    if damage=='neither':(target/'colvia').write_bytes(b'foreign\n')
                    elif damage=='mode':(target/'colvia').chmod(0o644)
                    else:(target/'colvia').unlink();(target/'colvia').symlink_to('a')
                    self.refusal(candidate,target,{'action':'switch','candidate':str(candidate),'packet':packet,'recover':True})
            # Synthetic damaged receipt prefixes are refusal fixtures, not killed-write evidence.
            for keep in (0,1,-1):
                with self.subTest(receipt_prefix=keep):
                    target=self.init(old);packet=self.transition(target);self.switch(target,packet,inject="after-receipt")
                    path=target/".hrn/product/receipts/transition.json";raw=path.read_bytes();path.write_bytes(raw[:keep])
                    self.refusal(candidate,target,{"action":"switch","candidate":str(candidate),"packet":packet,"recover":True})

        def test_c09_same_window_p_q(self):
            target=self.init(git=True);p_binding=json.loads((target/".hrn/product/binding.json").read_bytes())["active_release"]
            q=self.transition(target,source=variant,op="to-q");self.switch(target,q,source=variant)
            self.assertNotEqual(p_binding,json.loads((target/".hrn/product/binding.json").read_bytes())["active_release"])
            self.call(self.installed(target),target,{"action":"parent"})
            for wid,stage in (("accepted-work","accepted"),("cancelled-work","cancelled"),("revoked-work","revoked"),("duplicate-work","duplicate-checked")):
                relations=[{"relation":"parent","target":{"authority_home_id":"home-a","kind":"work","id":"parent"}}] if wid=="accepted-work" else []
                self.record(target,wid=wid,iid="intent-"+wid,stage=stage,relations=relations)
            self.call(self.installed(target),target,{"action":"candidate","request":self.candidate_request(target)})
            before=self.truth(target);packet=self.call(candidate,target,{"action":"switch-preview","switch_action":"rollback","operation_id":"back-to-p"})
            self.call(candidate,target,{"action":"switch","switch_action":"rollback","packet":packet})
            self.assertEqual(p_binding,json.loads((target/".hrn/product/binding.json").read_bytes())["active_release"]);self.assertEqual(before,self.truth(target))
            self.assertEqual("active",self.call(candidate,target,{"action":"read-work","wid":"parent"})["state"])
            ready=self.call(self.installed(target),target,{'action':'parent-readiness'})
            self.assertEqual([],ready['unavailable']);self.assertEqual(1,len(ready['children']))
            for wid,outcome in (("accepted-work","completed"),("cancelled-work","rejected"),("revoked-work","revoked"),("duplicate-work","completed")):
                self.assertEqual(outcome,self.call(candidate,target,{"action":"read-work","wid":wid})["state"])

        def test_c10_repair_detach(self):
            for cut in ("after-backup-request","after-backup","after-file","after-receipt"):
                with self.subTest(repair=cut):
                    target=self.init();(target/"colvia").write_bytes(b"damage\n");backup=self.base/(target.name+"-backup")
                    packet=self.call(candidate,target,{"action":"repair-preview","backup":str(backup)})
                    self.call(candidate,target,{"action":"repair","packet":packet,"inject_at":cut},86)
                    self.call(candidate,target,{"action":"repair","packet":packet,"recover":True})
                    before=snapshot(target);saved=snapshot(backup,scratch=True)
                    self.call(candidate,target,{"action":"repair","packet":packet,"recover":True});self.assertEqual(before,snapshot(target));self.assertEqual(saved,snapshot(backup,scratch=True))
            for cut in ("after-receipt","after-launcher","after-file","after-files","after-directory","after-product"):
                with self.subTest(detach=cut):
                    target=self.init();self.call(self.installed(target),target,{"action":"draft","select":True,"grant":True})
                    preserved=self.truth(target);packet=self.call(candidate,target,{"action":"detach-preview"})
                    self.call(candidate,target,{"action":"detach","packet":packet,"inject_at":cut},86)
                    self.call(candidate,target,{"action":"detach","packet":packet,"recover":True})
                    self.assertEqual(preserved,self.truth(target));before=snapshot(target)
                    self.call(candidate,target,{"action":"detach","packet":packet,"recover":True});self.assertEqual(before,snapshot(target))

            with self.subTest(history='transitioned-entry-home'):
                target=self.init(old)
                old_product=self.call(old,target,{'action':'verify'})
                old_binding=json.loads((target/'.hrn/product/binding.json').read_bytes())
                self.assertEqual(old_product['binding_ref']['sha256'],sha(canonical(old_binding)))
                old_release=old_binding['active_release']
                packet=self.transition(target);self.switch(target,packet)
                active=self.call(candidate,target,{'action':'verify'})
                self.assertEqual('delegation-1',active['inventory']['inventory_id'])
                active_binding=json.loads((target/'.hrn/product/binding.json').read_bytes())
                self.assertEqual(active['binding_ref']['sha256'],sha(canonical(active_binding)))
                self.assertEqual(old_release,active_binding['prior_release'])
                retained=target/'.hrn/product/releases'/old_release['id']/'inventory.json'
                self.assertEqual(old_release['sha256'],hashlib.sha256(retained.read_bytes()).hexdigest())
                self.call(self.installed(target),target,{'action':'draft','select':True,'grant':True})
                preserved=self.truth(target)
                (target/'colvia').write_bytes(b'damage transferred launcher\n')
                backup=self.base/(target.name+'-transitioned-repair')
                packet=self.call(candidate,target,{'action':'repair-preview','backup':str(backup)})
                self.call(candidate,target,{'action':'repair','packet':packet,'inject_at':'after-file'},86)
                self.call(candidate,target,{'action':'repair','packet':packet,'recover':True})
                self.assertEqual(preserved,self.truth(target))
                before=snapshot(target);saved=snapshot(backup,scratch=True)
                self.call(candidate,target,{'action':'repair','packet':packet,'recover':True})
                self.assertEqual(before,snapshot(target));self.assertEqual(saved,snapshot(backup,scratch=True))
                packet=self.call(candidate,target,{'action':'detach-preview'})
                self.call(candidate,target,{'action':'detach','packet':packet,'inject_at':'after-files'},86)
                self.call(candidate,target,{'action':'detach','packet':packet,'recover':True})
                self.assertEqual(preserved,self.truth(target));before=snapshot(target)
                self.call(candidate,target,{'action':'detach','packet':packet,'recover':True})
                self.assertEqual(before,snapshot(target));self.assertEqual(saved,snapshot(backup,scratch=True))

            from hv2ref.product import workspace_repair_apply
            from hv2ref.errors import ContractError
            target=self.init();(target/'colvia').write_bytes(b'damage\n');backup=self.base/(target.name+'-missing-source-backup')
            packet=self.call(candidate,target,{'action':'repair-preview','backup':str(backup)});before=snapshot(target)
            with self.assertRaises(ContractError):workspace_repair_apply(self.base/'missing-source',target,packet['request'],confirm_token=packet['confirm_token'])
            self.assertEqual(before,snapshot(target));self.assertFalse(backup.exists())
            for kind in ('unknown-member','retired-entry-collision','linked-member'):
                with self.subTest(unsafe=kind):
                    target=self.init()
                    if kind=='unknown-member':(target/'.hrn/product/foreign.bin').write_bytes(b'keep unknown\n')
                    elif kind=='retired-entry-collision':(target/'hv2').write_bytes(b'keep user entry\n')
                    else:(target/'.hrn/product/foreign').symlink_to('../../a')
                    # Unknown product members and retired-entry collisions are
                    # preserved refusals; none is a deletion target.
                    self.refusal(candidate,target,{'action':'detach-preview'})
                    self.refusal(candidate,target,{'action':'repair-preview','backup':str(self.base/(target.name+'-refused-backup'))})

        def test_c11_historical_pairs(self):
            from hv2ref.product import _detach_plan_shape,_detach_receipt,workspace_detached_status
            from hv2ref.errors import ContractError
            for source,version in ((p["old"],2),(old,3),(candidate,4)):
                with self.subTest(version=version):
                    target=self.init(source);packet=self.call(source,target,{"action":"detach-preview"})
                    self.call(source,target,{"action":"detach","packet":packet})
                    self.assertEqual("detached",workspace_detached_status(target)["classification"])
                    path=target/".hrn/detached.json";original=path.read_bytes()
                    for rv,pv in ((True,True),(4,3),(3,4),(0,0),(5,5),("4",4)):
                        with self.subTest(receipt=rv,plan=pv):
                            value=json.loads(original);value["schema_version"]=rv;value["plan"]["schema_version"]=pv;path.write_bytes(canonical(value));before=snapshot(target)
                            with self.assertRaises(ContractError):workspace_detached_status(target)
                            self.assertEqual(before,snapshot(target));path.write_bytes(original)
            from hv2ref import product
            from hv2ref.workspace import _validate_plan_shape
            for source,window in ((p['old'],'checkout-1'),(old,'entry-1'),(candidate,'delegation-1')):
                with self.subTest(history_window=window):
                    target=self.init(source);self.assertEqual(window,product.verify_workspace_product(target)['inventory']['inventory_id'])
                    plan=json.loads((target/'.hrn/product/init-plan.json').read_bytes());_validate_plan_shape(plan)
                    for version in (True,0,2,3,5,'4',1 if window=='delegation-1' else 4):
                        with self.subTest(invalid_init_schema=version),self.assertRaises(ContractError):_validate_plan_shape({**plan,'schema_version':version})
                    launcher='hv2' if window=='checkout-1' else 'colvia';(target/launcher).write_bytes(b'damage\n')
                    backup=self.base/(target.name+'-historical-repair');packet=self.call(source,target,{'action':'repair-preview','backup':str(backup)})
                    self.call(source,target,{'action':'repair','packet':packet});receipt=json.loads((backup/'receipt.json').read_bytes())
                    self.assertEqual(4 if window=='delegation-1' else 1,receipt['schema_version']);self.assertEqual(receipt['schema_version'],receipt['plan']['schema_version'])
                    saved=snapshot(backup,scratch=True);self.call(source,target,{'action':'repair','packet':packet,'recover':True});self.assertEqual(saved,snapshot(backup,scratch=True))
            # Explicit validator matrix covers historical init/switch windows;
            # these are shape checks, not executed older-artifact histories.
            target=self.init();fmt=json.loads((target/'.hrn/format.json').read_bytes())
            initial=json.loads((target/'.hrn/product/init-plan.json').read_bytes())
            switch=self.transition(target,source=variant)['request']
            for window in ('human-1','worker-1','umbrella-1','planning-1','checkout-1','entry-1','delegation-1'):
                init_version=4 if window=='delegation-1' else 1
                switch_version=4 if window=='delegation-1' else 2 if window=='entry-1' else 1
                ref={**initial['candidate_release'],'inventory_id':window}
                _validate_plan_shape({**initial,'schema_version':init_version,'candidate_release':ref})
                for action in ('update','rollback'):
                    good={**switch,'action':action,'schema_version':switch_version,'candidate_release':ref};product._switch_plan_shape(good,fmt)
                    for version in (True,0,3,5,'4',2 if switch_version!=2 else 4):
                        with self.subTest(window=window,action=action,schema=version),self.assertRaises(ContractError):product._switch_plan_shape({**good,'schema_version':version},fmt)
            # No historical window provenance is inferred from identical removed names.
            target=self.init();packet=self.call(candidate,target,{"action":"detach-preview"});self.call(candidate,target,{"action":"detach","packet":packet})
            self.assertEqual(4,workspace_detached_status(target)["receipt"]["schema_version"])

        def cli(self,entry,target,args,*,source=False,expected=0):
            command=[ctx["runtime_path"],"-I","-S","-B",*(["-O"] if sys.flags.optimize else []),str(entry),*(["--source-checkout"] if source else []),*args]
            result=subprocess.run(command,cwd=target,stdin=subprocess.DEVNULL,capture_output=True,timeout=150)
            self.assertEqual(expected,result.returncode,result.stdout.decode(errors="replace")+result.stderr.decode(errors="replace"));return result.stdout

        def test_c12_runtime_entries(self):
            from hv2ref.work import WorkStore
            from hv2ref.errors import ContractError
            target=self.init(git=True);self.record(target)
            for entry,source in ((candidate/"colvia",True),(variant/"colvia",True),(target/"colvia",False)):
                with self.subTest(entry="source" if source else "installed"):
                    before=snapshot(target)
                    self.assertIn(b"pass",self.cli(entry,target,["status","--target",str(target)],source=source))
                    self.assertIn(b"delegate-1",self.cli(entry,target,["view","work","work-a","--target",str(target)],source=source))
                    self.assertEqual(before,snapshot(target))
            with self.assertRaises(ContractError):WorkStore(target)._runtime()
            self.assertEqual("completed",self.call(self.installed(target),target,{"action":"read-work"})["state"])
            from hv2ref.work import read_work
            from hv2ref.intent import workspace_intents
            from hv2ref import candidates,view
            intents=workspace_intents(target);graph=read_work(target,'work-a');before=snapshot(target)
            self.assertEqual(graph,read_work(target,'work-a',_intent_graph_reader=lambda iid:intents[iid]))
            self.assertEqual(graph,candidates._graphs(target)[0]['work-a'])
            self.assertIn('delegate-1','\n'.join(view._work(target,graph,None,None,intents,{'work-a':graph})))
            self.assertEqual(before,snapshot(target))

        def test_c13_plain_auditors(self):
            target=self.init(git=True);self.record(target)
            before=snapshot(target)
            command=[ctx["runtime_path"],"-I","-S","-B",str(candidate/"tests/fixtures/intent_plain_auditor.py"),str(target),"intent-a"]
            result=subprocess.run(command,capture_output=True,timeout=60);self.assertEqual(0,result.returncode,result.stdout)
            value=json.loads(result.stdout);self.assertEqual("not-verified",value["delegation_authorization"]);self.assertEqual(before,snapshot(target))
            packet=self.call(candidate,target,{"action":"detach-preview"});self.call(candidate,target,{"action":"detach","packet":packet})
            before=snapshot(target)
            command=[ctx["runtime_path"],"-I","-S","-B",str(candidate/"tests/fixtures/product_plain_auditor.py"),str(target)]
            result=subprocess.run(command,capture_output=True,timeout=60);self.assertEqual(0,result.returncode,result.stdout)
            value=json.loads(result.stdout);self.assertEqual("not-reimplemented",value["full_record_semantics"]);self.assertEqual(before,snapshot(target))

        def test_c14_capability_inheritance(self):
            from hv2ref.work import _verified_launcher_path,_allows_unchanged_crlf,WorkStore,snapshot as content_snapshot
            for window in ('checkout-1','entry-1','delegation-1'):
                self.assertTrue(_allows_unchanged_crlf(window))
            self.assertEqual('colvia',_verified_launcher_path('a'*64,'delegation-1'))
            WorkStore._umbrella_runtime({'inventory_id':'delegation-1'})
            target=self.init(git=True);(target/'.gitattributes').write_bytes(b'b text eol=crlf\n');(target/'b').write_bytes(b'unchanged\r\n')
            raw=(target/'b').read_bytes();self.call(self.installed(target),target,{'action':'parent'})
            relations=[{'relation':'parent','target':{'authority_home_id':'home-a','kind':'work','id':'parent'}}]
            self.record(target,wid='accepted-work',iid='intent-accepted-work',relations=relations,change_b=False)
            self.assertEqual(raw,(target/'b').read_bytes());self.assertEqual(raw,(target.parent/(target.name+'-worker-accepted-work')/'b').read_bytes())
            ready=self.call(self.installed(target),target,{'action':'parent-readiness'});self.assertEqual([],ready['unavailable']);self.assertEqual(1,len(ready['children']))
            runtime=self.call(candidate,target,{'action':'verify'})
            observed=content_snapshot(target,verified_launcher_sha256=runtime['launcher_sha256'],verified_inventory_id=runtime['inventory']['inventory_id'])
            self.assertNotIn('colvia',{row['path'] for row in observed['entries']})
            self.call(self.installed(target),target,{'action':'candidate','request':self.candidate_request(target)})
            before=snapshot(target);self.assertEqual('pass',self.call(candidate,target,{'action':'status'})['classification']);self.assertEqual(before,snapshot(target))

        def test_c15_truth_drift_replay(self):
            target=self.init(old);packet=self.transition(target)
            self.call(self.installed(target),target,{"action":"draft","iid":"after-preview"})
            self.refusal(candidate,target,{"action":"switch","candidate":str(candidate),"packet":packet},code="HV2-WORKSPACE-PRODUCT",reason="truth changed since lifecycle preview")
            packet=self.transition(target,op="current-transition");self.switch(target,packet)
            q=self.transition(target,source=variant,op="to-q");self.switch(target,q,source=variant)
            before=snapshot(target);self.switch(target,packet,recover=True);self.assertEqual(before,snapshot(target))
            self.barrier(old,target,{"action":"init","operation_id":"init-a"})

        def test_c16_artifact_inventory(self):
            from hv2ref.product import workspace_candidate,DELEGATION_MANAGED_PATHS,ENTRY_MANAGED_PATHS,_launcher_inventory_window
            for source in (candidate,variant):
                with self.subTest(source="p" if source==candidate else "q"):
                    release=workspace_candidate(source);self.assertEqual("delegation-1",release["inventory"]["inventory_id"])
                    self.assertEqual(29,len(release["payload"]));self.assertEqual(set(DELEGATION_MANAGED_PATHS),set(release["payload"]))
                    self.assertEqual(tuple(ENTRY_MANAGED_PATHS),tuple(DELEGATION_MANAGED_PATHS))
                    for entry in release["inventory"]["entries"]:
                        data=release["payload"][entry["path"]];self.assertEqual((entry["sha256"],entry["size_bytes"]),(sha(data),len(data)))
                    self.assertEqual("delegation-1",_launcher_inventory_window(release["payload"]["colvia"],allow_legacy=False))
                    self.assertFalse(any(b"synthetic-not-a-credential" in data for data in release["payload"].values()))
                    sentinel=self.base/('sentinel-p' if source==candidate else 'sentinel-q');sentinel.write_bytes(b'synthetic-secret-never-package\n');sentinel_before=sentinel.read_bytes()
                    target=self.init(source);installed=self.installed(target)
                    for name,data in release['payload'].items():self.assertEqual(data,(installed/name).read_bytes())
                    for name in ('README.md','docs/MAINTAINING.md','docs/OPERATIONS.md','adapters/colvia-work/SKILL.md'):
                        self.assertIn(b'delegation-1',(installed/name).read_bytes())
                    self.assertTrue(all(sentinel_before not in data for data in release['payload'].values()));self.assertEqual(sentinel_before,sentinel.read_bytes())
                    self.assertIn(b"delegation-1",self.cli(target/"colvia",target,["status","--target",str(target)]))

    DelegationWindowTests.__qualname__="DelegationWindowTests"
    names={"test_c"+str(i).zfill(2)+"_"+name for i,name in enumerate(SUFFIXES,1)}
    need({n for n in vars(DelegationWindowTests) if n.startswith("test_") }==names,"exact C01-C16 method inventory")
    return unittest.defaultTestLoader.loadTestsFromTestCase(DelegationWindowTests)
