"""Explicit exact-artifact qualification; no tests or product imports at discovery.

The controller supplies pinned managed artifacts inside its existing write boundary.
The retained delegation fixture is reused unchanged; it executes the actual gates.
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
import subprocess
import sys
import threading
import time
import unittest
from unittest import mock

from tests.test_delegation_window_transition import canonical, snapshot

PREDECESSOR_SHA = "fd1a49a6f62cc1fc6ee84f649bec8c95fe5ce1b4b30b76d032e56eb41031735b"
TIME = "2026-01-01T00:00:00Z"


def build_official_suite(*, candidate_source, predecessor_source, variant_source,
                             old_variant_source, work_root, identities):
    from hv2ref.product import workspace_candidate
    candidate, old, variant, old_q = map(Path, (candidate_source, predecessor_source, variant_source, old_variant_source))
    root = Path(work_root)
    if identities["predecessor"]["sha256"] != PREDECESSOR_SHA:
        raise RuntimeError("unexpected retained predecessor")
    for key, source in (("candidate", candidate), ("q", variant)):
        if workspace_candidate(source)["release_ref"] != identities[key]:
            raise RuntimeError("artifact identity drift")
    if identities["candidate"] == identities["q"]:
        raise RuntimeError("P and Q must be distinct")
    helper = Path(__file__).parent / "fixtures/delegation_process.py"

    class OfficialWindowTests(unittest.TestCase):
        def setUp(self):
            self.base = root / self._testMethodName
            self.base.mkdir(parents=True)
            self.serial = 0
            self.children = []
            self.addCleanup(self.cleanup)

        def cleanup(self):
            for child in self.children:
                if child.poll() is None:
                    child.terminate()
                    try: child.wait(timeout=5)
                    except subprocess.TimeoutExpired: child.kill(); child.wait(timeout=5)
                else: child.wait()
            self.assertTrue(all(p.poll() is not None for p in self.children))

        def directory(self, label):
            self.serial += 1
            path = self.base / (str(self.serial) + "-" + label)
            path.mkdir()
            return path

        def spawn(self, source, target, request):
            self.serial += 1
            inp = self.base / (str(self.serial) + ".input.json")
            log = self.base / (str(self.serial) + ".log")
            inp.write_bytes(canonical(request))
            command = [sys.executable, "-I", "-S", "-B", *(["-O"] if sys.flags.optimize else []),
                       str(helper), str(source), str(target)]
            with inp.open("rb") as stdin, log.open("xb") as stdout:
                child = subprocess.Popen(command, stdin=stdin, stdout=stdout, stderr=subprocess.STDOUT,
                                         cwd=candidate)
            self.children.append(child)
            return child, log

        def finish(self, child, log, expected=0):
            self.assertEqual(expected, child.wait(timeout=120), log.read_text(errors="replace")[-6000:])
            self.assertLessEqual(log.stat().st_size, 8 * 1024 * 1024)
            return json.loads(log.read_bytes())

        def call(self, source, target, request, expected=0):
            return self.finish(*self.spawn(source, target, request), expected)

        def installed(self, target):
            binding = json.loads((target / ".hrn/product/binding.json").read_bytes())
            return target / ".hrn/product/releases" / binding["active_release"]["id"] / "payload"

        def git(self, target, *args):
            from hv2ref.workspace import git_environment
            return subprocess.run(["git", "-C", str(target), *args], capture_output=True, check=True,
                                  timeout=30, env=git_environment()).stdout.decode().strip()

        def init(self, source=old, *, git=False):
            target = self.directory("project")
            (target / "a").write_bytes(b"before\n")
            (target / "b").write_bytes(b"before-b\n")
            if git:
                self.git(target, "init", "-q")
                self.git(target, "config", "user.name", "Synthetic Fixture")
                self.git(target, "config", "user.email", "synthetic@example.invalid")
                self.git(target, "config", "commit.gpgsign", "false")
            self.call(source, target, {"action": "init", "operation_id": "init-a"})
            locks=target/'.hrn/locks'
            staging=locks/('official-'+'a'*64+'.d');staging.mkdir()
            (staging/'grant.json').write_bytes(b'partial staging evidence')
            (staging/'journal.jsonl').write_bytes(b'partial staging journal')
            (locks/'cancel-staged.json').write_bytes(b'partial cancellation staging')
            return target

        def transition(self, target, source=candidate, op="transition"):
            return self.call(candidate, target, {"action": "switch-preview", "candidate": str(source), "operation_id": op})

        def switch(self, target, packet, source=candidate, *, recover=False, cut=None):
            return self.call(candidate, target, {"action": "switch", "candidate": str(source), "packet": packet,
                                                "recover": recover, "inject_at": cut}, 86 if cut else 0)

        def truth(self, target):
            return {k: v for k, v in snapshot(target).items()
                    if k in {"a", "b", ".hrn/format.json", ".hrn/.gitignore"}
                    or k.startswith((".hrn/intents/", ".hrn/work/", ".hrn/planning/", ".hrn/executions/", ".git/"))}

        def refuse(self, source, target, request):
            before = snapshot(target)
            result = self.call(source, target, request, 65)
            self.assertEqual(before, snapshot(target))
            self.assertTrue(result["code"].startswith("HV2-"))
            return result

        def candidate_request(self, target):
            from hv2ref.candidates import read_candidates
            return {"record_type": "candidate-request", "schema_version": 1, "authority_home_id": "home-a",
                    "request_id": "candidate-add", "candidate_id": "idea-a", "action": "add",
                    "expected_sha256": read_candidates(target)["sha256"], "writer": "agent:fixture",
                    "owner_statement": "synthetic planning request", "reason": "synthetic", "observed_at": TIME,
                    "payload": {"title": "Synthetic", "purpose": "Preserve planning", "expected_effect": "Visible", "related_candidates": []}}

        def continuation(self, target, *, wid="local-work", request="cont-a", action="select", choice=None, packet=None):
            from hv2ref.jsonio import canonical_json_bytes
            if packet is None:
                value = {"work_id": wid, "action": action, "actor": "owner", "owner_statement": "Synthetic Owner selection",
                         "reason": "Synthetic exact-artifact case", "request_id": request, "observed_at": TIME,
                         "choice": ({"kind": "none"} if action == "select" and choice is None else choice)}
                before = snapshot(target)
                run = subprocess.run([str(target / "colvia"), "continuation", "prepare"],
                    input=canonical_json_bytes(value), capture_output=True, timeout=30)
                self.assertEqual(0, run.returncode, run.stdout + run.stderr)
                self.assertEqual(before, snapshot(target)); packet = json.loads(run.stdout)
            run = subprocess.run([str(target / "colvia"), "continuation", "apply", "--confirm", packet["confirm_token"]],
                                 input=canonical_json_bytes(packet["ticket"]), capture_output=True, timeout=30)
            self.assertEqual(0, run.returncode, run.stdout + run.stderr)
            return packet, json.loads(run.stdout)

        def closed_capsule(self, target):
            from hv2ref import product, official_entry as entry, official_host as hostmod
            runtime=product.verify_workspace_product(target);runtime['inventory_id']='official-execution-1'
            root=self.directory('runtime');root.chmod(0o700)
            seed=subprocess.run([sys.executable,'-I','-S','-B',str(Path(__file__).parent/'fixtures/official_fixture.py'),str(target)],capture_output=True,timeout=60)
            self.assertEqual(0,seed.returncode,seed.stdout+seed.stderr)
            request={'work_id':'official-work','worker_root':str(target),'documents':{
                'files':{'Editable':{'path':str(target/'a'),'view':{'kind':'replace-range','ranges':[[0,len((target/'a').read_bytes())]]}},
                         'Reference':{'path':str(target/'b'),'view':{'kind':'full'}}},
                'output':'Editable','claims':{'Editable':{'required':[(target/'b').read_text().strip()],'forbidden':[],
                    'evidence':[{'file_id':'Reference','quote':(target/'b').read_text().strip()}]}},'approved_external_links':[]},
                'read_ids':['Editable','Reference'],'prompt':'Synthetic lifecycle fixture',
                'owner_statement':'Synthetic capsule only','runtime':{},'runtime_root':str(root),
                'expires_wall_ns':time.time_ns()+600*10**9,'seconds':90,'worker_limit':1}
            with mock.patch.object(product,'require_workspace_runtime',return_value=runtime),mock.patch.object(entry,'runtime_input',return_value={}):
                p=entry.prepare(target,request)
                h=hostmod.Host(p['spec'],p['confirm_token'])
                try:h.finish('revoked-before-launch')
                finally:h.close()
            return h.grant

        def test_01_exact_predecessor_and_new_window_admission(self):
            for is_git in (False, True):
                with self.subTest(git=is_git):
                    target = self.init(git=is_git)
                    self.assertEqual(PREDECESSOR_SHA, hashlib.sha256(canonical(self.call(old, target, {"action":"verify"})["inventory"])).hexdigest())
                    payload = self.installed(target)
                    self.call(payload, target, {"action":"local"})
                    # Historical schema-3 grant is valid with the retained runtime.
                    self.call(payload, target, {"action":"draft", "iid":"granted-intent", "wid":"granted-work", "grant":True, "select":True})
                    self.call(payload, target, {"action":"candidate", "request":self.candidate_request(target)})
                    before = self.truth(target); packet = self.transition(target)
                    self.assertEqual(7, packet["request"]["schema_version"])
                    self.switch(target, packet)
                    self.assertEqual(before, self.truth(target))
                    self.assertEqual("official-execution-1", self.call(candidate, target, {"action":"verify"})["inventory"]["inventory_id"])
                    self.continuation(target)
                    self.assertFalse(any("/continuation/" in k for k in before))
                    self.refuse(candidate, target, {"action":"switch-preview", "switch_action":"rollback", "operation_id":"downgrade"})
            target = self.init(old_q)
            self.refuse(candidate, target, {"action":"switch-preview", "candidate":str(candidate), "operation_id":"wrong-predecessor"})

        def test_02_old_writers_refuse_every_new_receipt_prefix(self):
            for cut in ("after-receipt", "after-staged-inventory", "after-release", "after-launcher", "after-binding", None):
                with self.subTest(prefix=cut):
                    target = self.init(); payload = self.installed(target)
                    self.call(payload, target, {"action":"local"})
                    work_packet = self.call(payload, target, {"action":"work-prepare", "wid":"local-work"})
                    draft = self.call(payload, target, {"action":"draft", "iid":"late-intent"})["drafts"]["draft-1"]
                    intent_packet = self.call(payload, target, {"action":"intent-prepare", "draft":draft})
                    requests = [{"action":"draft", "iid":"new-intent"}, {"action":"intent-apply", "packet":intent_packet},
                                {"action":"work-prepare", "wid":"local-work"}, {"action":"work-apply", "packet":work_packet},
                                {"action":"candidate", "request":self.candidate_request(target)}]
                    detach = self.call(old, target, {"action":"detach-preview"})
                    update = self.call(old, target, {"action":"switch-preview", "candidate":str(old_q), "operation_id":"old-update"})
                    packet = self.transition(target); self.switch(target, packet, cut=cut)
                    before = self.truth(target)
                    self.assertFalse(any("/continuation/" in k for k in before))
                    for source in (old, payload):
                        for request in requests:
                            with self.subTest(source="retained-installed" if source==payload else "retained-source", action=request["action"]):
                                result = self.refuse(source, target, request)
                                self.assertIn(result["code"], {"HV2-WORKSPACE-PRODUCT", "HV2-WORKSPACE-LAUNCHER"})
                    for request in ({"action":"detach", "packet":detach}, {"action":"switch", "candidate":str(old_q), "packet":update}):
                        self.refuse(old, target, request)
                    self.assertEqual(before, self.truth(target))
                    if cut: self.switch(target, packet, recover=True)
                    # The full retained reader also refuses the completed new window.
                    self.refuse(old, target, {"action":"verify"})

        def test_03_waiting_old_writers_recheck_after_schema7_receipt(self):
            from hv2ref.product import workspace_switch_apply
            from hv2ref.errors import InjectedCrash
            for family in ("draft", "intent-apply", "candidate", "work-publish", "work-apply", "switch", "rollback", "repair", "detach"):
                with self.subTest(family=family):
                    target = self.init(old_q if family=="rollback" else old)
                    if family=="rollback": self.call(old, target, {"action":"switch", "candidate":str(old), "operation_id":"to-exact-old"})
                    payload = self.installed(target)
                    if family == "draft": request={"action":"draft", "iid":"late-intent"}; source=payload
                    elif family == "intent-apply":
                        draft=self.call(payload,target,{"action":"draft"})["drafts"]["draft-1"]
                        packet=self.call(payload,target,{"action":"intent-prepare","draft":draft})
                        request={"action":"intent-apply","packet":packet};source=payload
                    elif family == "candidate": request={"action":"candidate","request":self.candidate_request(target)};source=payload
                    elif family in ("work-publish","work-apply"):
                        material=self.call(payload,target,{"action":"local"});source=payload
                        if family=="work-apply":request={"action":"work-apply","packet":self.call(payload,target,{"action":"work-prepare","wid":"local-work"})}
                        else:
                            graph=material["graph"];selected=graph["selections"][graph["current"]["selection_ref"]["id"]]
                            revision=copy.deepcopy(graph["revisions"][selected["revision_ref"]["id"]])
                            revision.update(record_id="late-checkpoint",operation="checkpoint",progress="active",expected_prior_selection=graph["current"]["selection_ref"])
                            manifest=graph["manifests"][revision["result_refs"]["manifest"]["id"]]
                            request={"action":"work-publish","identity":graph["identity"],"revision":revision,"manifest":manifest,"selection_id":"late-selection","operation_id":"late-publish"}
                    else:
                        source=old;request={"action":"switch" if family=="rollback" else family,"operation_id":"late-"+family}
                        if family=="switch":request["candidate"]=str(old_q)
                        if family=="rollback":request["switch_action"]="rollback"
                        if family=="repair":
                            (target/"colvia").write_bytes(b"damage\n");request["backup"]=str(self.base/(target.name+"-backup"))
                        packet=self.call(source,target,{**request,"action":request["action"]+"-preview"});request["packet"]=packet
                        if family=="repair":self.call(source,target,request);request["recover"]=True
                    transition=self.transition(target)
                    lock=target/".hrn/locks/writer.lock";expected=lock.stat()
                    attempt=self.base/(target.name+"-attempt.json");acquired=self.base/(target.name+"-acquired.json")
                    request["lock_observation"]={"attempt":str(attempt),"acquired":str(acquired)}
                    ready=threading.Event();release=threading.Event();errors=[];ident=[];before_unlock=[];native=fcntl.flock
                    def new_writer():
                        ident.append(threading.get_ident())
                        try:workspace_switch_apply(target,transition["request"],confirm_token=transition["confirm_token"],source=candidate,inject_at="after-receipt")
                        except BaseException as exc:errors.append(exc)
                    def observed(fd,op):
                        number=fd.fileno() if hasattr(fd,"fileno") else fd;info=os.fstat(number)
                        belongs=ident and threading.get_ident()==ident[0] and (info.st_dev,info.st_ino)==(expected.st_dev,expected.st_ino)
                        if belongs and op & fcntl.LOCK_UN:before_unlock.append(snapshot(target))
                        result=native(fd,op)
                        if belongs and op & fcntl.LOCK_EX:
                            ready.set()
                            if not release.wait(30):raise RuntimeError("new writer barrier deadline")
                        return result
                    with mock.patch.object(fcntl,"flock",observed):
                        thread=threading.Thread(target=new_writer);thread.start()
                        try:
                            self.assertTrue(ready.wait(30),repr(errors));child,log=self.spawn(source,target,request);deadline=time.monotonic()+30
                            while not attempt.exists():
                                self.assertIsNone(child.poll(),log.read_text(errors="replace"));self.assertLess(time.monotonic(),deadline);time.sleep(.01)
                            self.assertFalse(acquired.exists())
                        finally:release.set();thread.join(60)
                    self.assertFalse(thread.is_alive());self.assertEqual(1,len(errors));self.assertIsInstance(errors[0],InjectedCrash)
                    self.assertEqual("after-receipt",errors[0].point);self.assertEqual(1,len(before_unlock))
                    result=self.finish(child,log,65);self.assertEqual(("HV2-WORKSPACE-PRODUCT","invalid receipt identity/schema"),(result["code"],result["message"]))
                    self.assertEqual(before_unlock[0],snapshot(target));self.assertTrue(acquired.is_file())

        def test_04_transition_recovery_and_torn_receipt_preserve_truth(self):
            for cut in ("after-receipt","after-staged-inventory","after-staged-payload","after-release","after-launcher","after-binding"):
                with self.subTest(cut=cut):
                    target=self.init();self.call(self.installed(target),target,{"action":"local"});before=self.truth(target)
                    packet=self.transition(target);self.switch(target,packet,cut=cut);self.assertEqual(before,self.truth(target))
                    self.switch(target,packet,recover=True);done=snapshot(target);self.switch(target,packet,recover=True)
                    self.assertEqual(done,snapshot(target));self.assertEqual(before,self.truth(target))
            for length in (0,1,-1):
                with self.subTest(torn_receipt=length):
                    target=self.init();packet=self.transition(target);self.switch(target,packet,cut="after-receipt")
                    receipt=target/".hrn/product/receipts/transition.json";raw=receipt.read_bytes();receipt.write_bytes(raw[:length])
                    self.refuse(candidate,target,{"action":"switch","candidate":str(candidate),"packet":packet,"recover":True})

        def test_05_q_records_survive_p_rollback_and_clone_read(self):
            from hv2ref.continuation import read_continuation
            from hv2ref.work import read_work
            target=self.init(candidate,git=True);original_binding=json.loads((target/".hrn/product/binding.json").read_bytes())["active_release"]
            q=self.transition(target,variant,"to-q");self.switch(target,q,variant)
            payload=self.installed(target)
            self.call(payload,target,{"action":"local"})
            self.call(payload,target,{"action":"parent"})
            stages = {"accepted-work": "accepted", "cancelled-work": "cancelled",
                      "revoked-work": "revoked", "duplicate-work": "duplicate-checked"}
            for wid, stage in stages.items():
                relation = [{"relation": "parent", "target": {"authority_home_id": "home-a", "kind": "work", "id": "parent"}}] if wid == "accepted-work" else []
                self.call(payload,target,{"action":"ordinary","wid":wid,"iid":"intent-"+wid,
                    "worker":str(target.parent/(target.name+"-worker-"+wid)),"stage":stage,
                    "grant":True,"actor":"delegate-1","relations":relation})
            # Q creates proposal and explicit-none history through its installed CLI.
            first,_=self.continuation(target,choice={"kind":"proposal","goal":"Next result","scope":"One item","next_step":"Prepare intent","decision_needed":"Owner approves intent"})
            self.continuation(target,request="cont-b")
            self.continuation(target,request="cont-c",action="withdraw")
            self.call(payload,target,{"action":"candidate","request":self.candidate_request(target)})
            grant=self.closed_capsule(target)
            before=self.truth(target);state=read_continuation(target,"local-work")
            packet=self.call(candidate,target,{"action":"switch-preview","switch_action":"rollback","operation_id":"back-to-p"})
            self.call(candidate,target,{"action":"switch","switch_action":"rollback","packet":packet})
            self.assertEqual(original_binding,json.loads((target/".hrn/product/binding.json").read_bytes())["active_release"])
            self.assertEqual(before,self.truth(target));self.assertEqual(state,read_continuation(target,"local-work"))
            frozen=snapshot(target);_,replay=self.continuation(target,packet=first)
            self.assertEqual("resolved",replay["replay"]);self.assertEqual(frozen,snapshot(target))
            for wid, expected in (("accepted-work","completed"),("cancelled-work","rejected"),
                                  ("revoked-work","revoked"),("duplicate-work","completed")):
                self.assertEqual(expected,read_work(target,wid)["state"])
            readiness=self.call(self.installed(target),target,{"action":"parent-readiness"})
            self.assertEqual([],readiness["unavailable"]);self.assertEqual(1,len(readiness["children"]))
            # Clone a real Git bundle without a transport shell; scratch is omitted.
            self.git(target,"add",".");self.git(target,"commit","-qm","synthetic continuation history")
            clone=self.base/"clone";bundle=self.base/"project.bundle"
            self.git(target,"bundle","create",str(bundle),"--all")
            result=subprocess.run(["git","clone","-q",str(bundle),str(clone)],capture_output=True,timeout=30)
            self.assertEqual(0,result.returncode,result.stdout+result.stderr)
            self.assertEqual(self.git(target,"rev-parse","HEAD"),self.git(clone,"rev-parse","HEAD"))
            self.assertEqual(state,read_continuation(clone,"local-work"))
            before=snapshot(clone)
            result=subprocess.run([str(clone/"colvia"),"view","continuation","local-work"],capture_output=True,timeout=30)
            self.assertEqual(0,result.returncode,result.stdout+result.stderr);self.assertEqual(before,snapshot(clone))
            # A relocated grant remains unsupported: CLI exit zero must not hide
            # its unavailable execution history or imply new execution readiness.
            status=subprocess.run([str(clone/"colvia"),"status"],capture_output=True,timeout=30)
            self.assertEqual(0,status.returncode,status.stdout+status.stderr)
            observation=json.loads(status.stdout)
            self.assertFalse(observation["official_execution"]["available"])
            self.assertFalse(observation["official_execution"]["ready_for_new_grant"])
            self.assertFalse(observation["lifecycle_ready"])
            detail=subprocess.run([str(clone/"colvia"),"run","status","--grant",grant],capture_output=True,timeout=30)
            self.assertNotEqual(0,detail.returncode)
            self.assertIn("grant-target",(detail.stdout+detail.stderr).decode())
            self.assertEqual(before,snapshot(clone))

        def test_06_new_detach_and_plain_auditor_preserve_continuation(self):
            target=self.init(candidate);self.call(self.installed(target),target,{"action":"local"});self.continuation(target)
            grant=self.closed_capsule(target)
            before=self.truth(target);packet=self.call(candidate,target,{"action":"detach-preview"})
            self.assertEqual(7,packet["request"]["schema_version"])
            self.call(candidate,target,{"action":"detach","packet":packet})
            self.assertEqual(before,self.truth(target))
            result=subprocess.run([sys.executable,"-I","-S","-B",str(Path(__file__).parent/"fixtures/product_plain_auditor.py"),str(target)],capture_output=True,timeout=30)
            self.assertEqual(0,result.returncode,result.stdout+result.stderr)
            audit=json.loads(result.stdout);self.assertEqual("detached",audit["classification"])
            self.assertEqual(before,self.truth(target))
            journal=target/".hrn/executions"/grant/"journal.jsonl"
            journal.write_bytes(journal.read_bytes()+b"corrupt\n")
            for optimized in (False,True):
                bad=subprocess.run([sys.executable,"-I","-S","-B",*(["-O"] if optimized else []),str(Path(__file__).parent/"fixtures/product_plain_auditor.py"),str(target)],capture_output=True,timeout=30)
                self.assertNotEqual(0,bad.returncode)
                self.assertNotIn(b"Traceback",bad.stderr)
            self.refuse(old,target,{"action":"detach","packet":packet,"recover":True})

        def test_07_fresh_init_and_repair_resume(self):
            for cut in ('after-staged-inventory','after-launcher-bytes','after-binding'):
                with self.subTest(init=cut):
                    target=self.directory('fresh');(target/'a').write_text('before\n');(target/'b').write_text('before-b\n')
                    packet=self.call(candidate,target,{'action':'init-preview','operation_id':'fresh-init'})
                    self.call(candidate,target,{'action':'init','packet':packet,'inject_at':cut},86)
                    self.call(candidate,target,{'action':'init','packet':packet,'recover':True})
                    done=snapshot(target);self.call(candidate,target,{'action':'init','packet':packet,'recover':True})
                    self.assertEqual(done,snapshot(target));self.assertEqual(b'before\n',(target/'a').read_bytes())
            for cut in ('after-backup','after-file'):
                with self.subTest(repair=cut):
                    target=self.init(candidate);self.call(self.installed(target),target,{'action':'local'})
                    grant=self.closed_capsule(target)
                    (target/'.hrn/executions'/grant/'journal.jsonl').chmod(0o644)
                    before=self.truth(target)
                    (target/'colvia').write_bytes(b'damaged launcher\n');backup=self.base/(target.name+'-backup')
                    packet=self.call(candidate,target,{'action':'repair-preview','operation_id':'repair','backup':str(backup)})
                    self.call(candidate,target,{'action':'repair','packet':packet,'backup':str(backup),'inject_at':cut},86)
                    self.call(candidate,target,{'action':'repair','packet':packet,'backup':str(backup),'recover':True})
                    self.assertEqual(before,self.truth(target));self.call(candidate,target,{'action':'verify'})

        def test_08_mixed_history_detach_resume_preserves_capsule(self):
            for cut in ('after-receipt','after-file','after-product'):
                with self.subTest(detach=cut):
                    target=self.init();packet=self.transition(target);self.switch(target,packet)
                    self.call(self.installed(target),target,{'action':'local'});self.continuation(target)
                    grant=self.closed_capsule(target)
                    (target/'.hrn/executions'/grant/'journal.jsonl').chmod(0o644)
                    before=self.truth(target)
                    packet=self.call(candidate,target,{'action':'detach-preview','operation_id':'mixed-detach'})
                    self.call(candidate,target,{'action':'detach','packet':packet,'inject_at':cut},86)
                    auditor=Path(__file__).parent/'fixtures/product_plain_auditor.py'
                    partial=subprocess.run([sys.executable,'-I','-S','-B',str(auditor),str(target)],capture_output=True,timeout=30)
                    self.assertEqual(0 if cut=='after-product' else 14,partial.returncode,partial.stdout+partial.stderr)
                    self.call(candidate,target,{'action':'detach','packet':packet,'recover':True})
                    self.assertEqual(before,self.truth(target));done=snapshot(target)
                    self.call(candidate,target,{'action':'detach','packet':packet,'recover':True});self.assertEqual(done,snapshot(target))
                    for optimized in (False,True):
                        check=subprocess.run([sys.executable,'-I','-S','-B',*(['-O'] if optimized else []),str(auditor),str(target)],capture_output=True,timeout=30)
                        self.assertEqual(0,check.returncode,check.stdout+check.stderr)
                    self.refuse(candidate,target,{'action':'init-preview','operation_id':'overwrite-retained'})

        def test_09_cross_windows_window_refused(self):
            import shutil
            windows=self.base/'windows-candidate';shutil.copytree(old,windows)
            p=windows/'colvia';raw=p.read_bytes();before=b'WORKSPACE_INVENTORY_ID = "continuation-1"'
            self.assertEqual(1,raw.count(before));p.write_bytes(raw.replace(before,b'WORKSPACE_INVENTORY_ID = "windows-2"'))
            self.assertEqual('windows-2',workspace_candidate(windows)['release_ref']['inventory_id'])
            target=self.init(candidate)
            result=self.refuse(candidate,target,{'action':'switch-preview','candidate':str(windows),'operation_id':'cross-windows'})
            self.assertEqual('HV2-WORKSPACE-PRODUCT',result['code'])
            self.assertIn('cannot cross the Windows boundary or downgrade',result['message'])

        def test_10_pending_continuation_blocks_same_window_switch(self):
            from hv2ref.continuation import ContinuationStore
            from hv2ref.errors import InjectedCrash
            from hv2ref import product
            self.assertEqual(product._managed_paths('windows-2'),product.CONTINUATION_MANAGED_PATHS)
            target=self.init(candidate);self.call(self.installed(target),target,{'action':'local'})
            request={'work_id':'local-work','action':'select','actor':'owner','owner_statement':'Synthetic pending CONT',
                'reason':'gate test','request_id':'pending','observed_at':TIME,'choice':{'kind':'none'}}
            run=subprocess.run([str(target/'colvia'),'continuation','prepare'],input=canonical(request),capture_output=True,timeout=30)
            self.assertEqual(0,run.returncode,run.stdout+run.stderr);packet=json.loads(run.stdout)
            runtime=product.verify_workspace_product(target)
            check=lambda _: {'binding_ref':runtime['binding_ref'],'launcher_sha256':runtime['launcher_sha256'],'inventory_id':'official-execution-1'}
            # Explicit runtime seam solely for creating the pending prefix. The
            # switch that must refuse it runs in the real retained source process.
            with self.assertRaises(InjectedCrash):ContinuationStore(target,runtime_check=check).apply(packet['ticket'],confirm_token=packet['confirm_token'],inject_at='after-choice')
            result=self.refuse(candidate,target,{'action':'switch-preview','candidate':str(variant),'operation_id':'pending-switch'})
            self.assertIn('CONTINUATION',result['code'])

    expected={"test_01_exact_predecessor_and_new_window_admission","test_02_old_writers_refuse_every_new_receipt_prefix",
              "test_03_waiting_old_writers_recheck_after_schema7_receipt","test_04_transition_recovery_and_torn_receipt_preserve_truth",
              "test_05_q_records_survive_p_rollback_and_clone_read","test_06_new_detach_and_plain_auditor_preserve_continuation",
              "test_07_fresh_init_and_repair_resume","test_08_mixed_history_detach_resume_preserves_capsule","test_09_cross_windows_window_refused","test_10_pending_continuation_blocks_same_window_switch"}
    if {n for n in vars(OfficialWindowTests) if n.startswith("test_")} != expected:
        raise RuntimeError("window qualification collection changed")
    return unittest.defaultTestLoader.loadTestsFromTestCase(OfficialWindowTests)
