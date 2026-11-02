"""Exercise a submitted Work through fresh processes and the installed launcher."""
import hashlib
import json
import os
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import sqlite3
import subprocess
import sys
import tempfile
import time
import unittest

SOURCE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SOURCE / "src"))
from hv2ref.jsonio import canonical_json_bytes
from hv2ref.product import workspace_init_apply, workspace_init_preview, verify_workspace_product
from hv2ref.work import make_manifest, record_ref, snapshot

class LocalDeliveryJourney(unittest.TestCase):
    def exercise(self, source, lab, *, only_closure=False):
        project = lab / "project"
        project.mkdir()
        doc, other = project / "guide.md", project / "reference.md"
        doc.write_text("# Guide\n"); other.write_text("승인, 진행해\n",encoding="utf-8")
        ts = "2026-11-03T00:00:00Z"
        init = workspace_init_preview(source, project, authority_home_id="home-guide", operation_id="init", created_at=ts)
        workspace_init_apply(source,project,init["request"],confirm_token=init["confirm_token"])
        def cli(*args, data=None, code=0, rendered=False):
            output=subprocess.run([sys.executable,"-I","-B",str(project/"colvia"),*args],cwd=project,
                                  input=canonical_json_bytes(data) if data is not None else b"",
                                  capture_output=True,timeout=50)
            # Product CLI uses the platform's default stdout encoding.
            try: text=output.stdout.decode("utf-8")
            except UnicodeDecodeError: text=output.stdout.decode("mbcs")
            self.assertEqual(output.returncode,code,(args,text[-600:],output.stderr[-300:]))
            return text if rendered else json.loads(text)
        def state():
            pin=verify_workspace_product(project)
            return snapshot(project,verified_launcher_sha256=pin["launcher_sha256"],verified_inventory_id=pin["inventory"]["inventory_id"])
        facets={"goal":"Guide review","scope":"guide.md only","acceptance_oracle":"quote and link kept","destination":"guide.md",
                "expected_outcome":"public example and link","forbidden_scope":"reference.md"}
        draft={"record_type":"intent-draft","schema_version":1,"authority_home_id":"home-guide","intent_id":"intent-guide","revision_id":"draft-a",
               "sequence":1,"prior_revision_ref":None,"actor":"agent","acceptance_authority":"owner","observed_at":ts,
               "facets":{k:{"status":"known","value":v} for k,v in facets.items()},"gaps":[],"statements":[],"route":"direct-entry"}
        cli("intent","draft",data=draft)
        pre=cli("intent","prepare",data={"intent_id":"intent-guide","revision_ref":record_ref(draft,"revision_id"),"actor":"owner","reason":"Synthetic test",
                                         "request_id":"accept-guide","observed_at":ts})
        ig=cli("intent","apply","--confirm",pre["confirm_token"],data=pre["ticket"])
        sel=ig["selections"][ig["current"]["selection_ref"]["id"]]
        intent={"authority_home_id":"home-guide","kind":"intent","id":"intent-guide","revision_ref":sel["revision_ref"],
                "acceptance_ref":sel["acceptance_ref"],"selection_ref":ig["current"]["selection_ref"]}
        wid="work-guide"
        identity={"record_type":"work-identity","schema_version":1,"authority_home_id":"home-guide","work_id":wid,
                  "work_type":"change","created_at":ts,"acceptance_authority":"owner","lineage":None}
        base=state()
        def revision(op,prior):
            manifest=make_manifest(base,state(),scope=["guide.md"]); h=hashlib.sha256(canonical_json_bytes(manifest)).hexdigest()
            rev={"record_type":"work-revision","schema_version":1,"authority_home_id":"home-guide","work_id":wid,"record_id":op,"observed_at":ts,
                 "observed_scope":["guide.md"],"unavailable_scope":[],"author":"agent","operation":op,"expected_prior_selection":prior,"intent_ref":intent,
                 "scope":["guide.md"],"document_refs":[],"evidence_refs":[],"result_refs":{"manifest":{"id":h,"sha256":h}},
                 "progress":"review" if op=="submit-result" else "active","next_action":"Review guide" if op=="submit-result" else "Edit guide",
                 "relations":[],"rebind_from":None,"execution_context":{"mode":"local","attempt_id":"attempt-"+op}}
            return {"identity":identity,"revision":rev,"manifest":manifest,"selection_id":op+"-s","operation_id":op+"-o"}
        active=cli("work","publish",data=revision("start",None));prior=active["current"]["selection_ref"]
        wanted=b"# Guide\n\n> Approved example.\n\nSee [reference](reference.md).\n";doc.write_bytes(wanted)
        envelope=revision("submit-result",prior)
        req={"work_id":wid,"action":"submit","payload":envelope,"expires":int(time.time())+600,"notify":False,"ask":True}
        pkt=cli("handoff","prepare",data=req)
        token=pkt["confirm_token"]
        self.assertFalse(any(lab.glob(".colvia-inbox-*")))
        if only_closure:
            from hv2ref.continuation import _delivery_fence, require_delivery_idle
            from hv2ref.workspace import delivery_folder
            folder = delivery_folder(project)
            cli("handoff","start",token,data=pkt["plan"])
            end = time.monotonic()+40
            while cli("handoff","show",token)["status"] != "question":
                self.assertLess(time.monotonic(),end)
            # A dead worker consumed its one step without publishing evidence.
            with sqlite3.connect(folder/"inbox.db") as db:
                db.execute("UPDATE delivery SET phase='running',used=1,expires=1 WHERE id=?", (token,))
            uncertain = cli("handoff","inspect",token)
            self.assertEqual(uncertain["status"],"reconcile")
            stopped = cli("handoff","stop",token)
            confirm = stopped["close_token"]
            self.assertTrue(confirm)
            self.assertNotEqual(uncertain["close_token"],confirm)
            cli("handoff","close-unknown",token,"--confirm",uncertain["close_token"],code=65)
            with _delivery_fence(project):
                cli("handoff","close-unknown",token,"--confirm",confirm,code=65)
            closed = cli("handoff","close-unknown",token,"--confirm",confirm)
            self.assertEqual((closed["status"],closed["reserved_steps"],closed["result"]),("unresolved",1,None))
            require_delivery_idle(project)
            self.assertEqual(cli("handoff","start",token,data=pkt["plan"])["status"],"unresolved")
            changed = cli("handoff","prepare",data=dict(req,expires=req["expires"]-10))
            cli("handoff","start",changed["confirm_token"],data=changed["plan"],code=65)
            other_plan = cli("handoff","prepare",data=dict(req,action="summary",payload=None,ask=False))
            other_key = other_plan["confirm_token"]
            cli("handoff","start",other_key,data=other_plan["plan"])
            end = time.monotonic()+40
            while cli("handoff","show",other_key)["status"] != "done":
                self.assertLess(time.monotonic(),end)
            self.assertEqual(cli("handoff","inspect",token)["status"],"unresolved")
            self.assertEqual(doc.read_bytes(),wanted)
            self.assertEqual(other.read_text(encoding="utf-8"),"승인, 진행해\n")
            self.assertFalse((project/".hrn/work"/wid/"selections"/"submit-result-s.json").exists())
            return {"live_worker_excluded":True,"stale_confirmation_refused":True,"unknown_effect_retained":True,
                    "duplicate_effect_refused":True,"lifecycle_unblocked":True,"different_action_finished":True}
        changed=dict(req,work_id="other")
        cli("handoff","prepare",data=changed,code=65)
        cli("handoff","prepare",data=dict(req,expires=1),code=65)
        cli("handoff","start",token,data=dict(pkt["plan"],route="other"),code=65)
        # Run a real summary and notification. A failed notice never repeats the action.
        simple=dict(req,action="summary",payload=None,expires=req["expires"]-20,ask=False,notify=True)
        simple_preview=cli("handoff","prepare",data=simple)
        summary_key=simple_preview["confirm_token"]
        cli("handoff","start",summary_key,data=simple_preview["plan"])
        end=time.monotonic()+50
        while True:
            summary_row=cli("handoff","show",summary_key)
            if summary_row["status"]=="done" and summary_row["notification"] in ("api_returned","unavailable"):break
            self.assertLess(time.monotonic(),end,summary_row)
        self.assertIn("Guide",summary_row["result"]["view"])
        self.assertEqual(summary_row["reserved_steps"],1)
        # An expired waiting row represents sleep past the approved deadline.
        summary=dict(req,action="summary",payload=None,expires=req["expires"]-10)
        pause=cli("handoff","prepare",data=summary)
        cli("handoff","start",pause["confirm_token"],data=pause["plan"])
        from hv2ref.workspace import delivery_folder
        folder=delivery_folder(project);dbpath=folder/"inbox.db"
        limit=time.monotonic()+40
        while cli("handoff","show",pause["confirm_token"])["status"]!="question":
            self.assertLess(time.monotonic(),limit)
        deny=cli("handoff","start",token,data=pkt["plan"],code=65)
        self.assertEqual(deny["code"],"COLVIA-DELIVERY")
        from hv2ref.continuation import require_delivery_idle
        from hv2ref.errors import ContractError
        with self.assertRaises(ContractError):require_delivery_idle(project)
        # Explicitly stopping before the reserved step must free the project.
        stopped=cli("handoff","stop",pause["confirm_token"])
        self.assertEqual((stopped["status"],stopped["reserved_steps"]),("stopped",0))
        require_delivery_idle(project)
        # Inject a stale unused queue row into this isolated test store only.
        with sqlite3.connect(dbpath) as db:
            db.execute("UPDATE delivery SET phase='question',expires=1 WHERE id=?",(pause["confirm_token"],))
        self.assertEqual(cli("handoff","inspect",pause["confirm_token"])["status"],"stopped")
        cli("handoff","start",token,data=pkt["plan"])
        # Query the public receipt using the same idempotent request after sender exit.
        def wait(want):
            until=time.monotonic()+50
            while time.monotonic()<until:
                row=cli("handoff","show",token)
                if row["status"]==want:return row
                self.assertNotIn(row["status"],("stopped","reconcile"),row)
                time.sleep(.1)
            self.fail("deadline for "+want)
        question=wait("question")
        cli("handoff","answer",token,"--question","other.1",code=65)
        self.assertEqual(question["reserved_steps"],0)
        self.assertIn(wid,cli("view","inbox",wid,rendered=True))
        cli("handoff","answer",token,"--question",question["question_id"])
        done=wait("done")
        self.assertEqual(done["reserved_steps"],1)
        # Two new clients replay the same confirmation after settlement.
        with ThreadPoolExecutor(max_workers=2) as clients:
            replies=list(clients.map(lambda _:cli("handoff","start",token,data=pkt["plan"]),range(2)))
        self.assertEqual([r["result"] for r in replies],[done["result"]]*2)
        self.assertEqual(done["result"]["selection"]["id"],"submit-result-s")
        self.assertEqual(cli("handoff","start",token,data=pkt["plan"])["result"],done["result"])
        self.assertEqual(doc.read_bytes(),wanted)
        self.assertEqual(other.read_text(encoding="utf-8"),"승인, 진행해\n")
        self.assertIn("제출",cli("view","inbox",wid,rendered=True))
        # Lost final response after a real publish: inspect uses existing authority.
        with sqlite3.connect(dbpath) as db:
            db.execute("UPDATE delivery SET phase='reconcile',result=NULL WHERE id=?",(token,))
        restored=cli("handoff","inspect",token)
        self.assertEqual(restored["result"]["selection"],done["result"]["selection"])
        with sqlite3.connect(dbpath) as db:
            db.execute("UPDATE delivery SET phase='corrupt-fixture' WHERE id=?",(token,))
        self.assertIn("수신함",cli("view",rendered=True))
        self.assertIn("수신함",cli("view","inbox",code=10,rendered=True))
        return {"question":True,"submit_once":True,"reserved_steps":1,"reference_preserved":True,"notification":summary_row["notification"],"expiry_closed":True,"duplicate_queries":2,"recovered_submission":True,"damaged_inbox_isolated":True}
    def test_failed_notice_leaves_one_readable_result(self):
        from argparse import Namespace
        from unittest.mock import patch
        from hv2ref.continuation import _delivery_db, _delivery_notify, delivery_command, delivery_inbox
        from hv2ref.work import _digest
        # Faults after result publication cannot create another dispatch or OS attempt.
        with tempfile.TemporaryDirectory() as scratch:
            project=Path(scratch).resolve()/"project"
            project.mkdir()
            req={"work_id":"work-guide","action":"summary"}
            plan={"request":req,"source":{"project":str(project),"work_id":"work-guide","scope":["guide.md"],"label":"Guide"}}
            key=_digest(plan)
            db=_delivery_db(project,create=True)
            try:
                with patch("subprocess.run",side_effect=OSError("synthetic notice failure")) as os_call:
                    self.assertEqual(_delivery_notify(),"unavailable")
                    for notice in ("attempted","unavailable"):
                        with db:
                            db.execute("INSERT OR REPLACE INTO delivery VALUES (?,?,?,'done',1,1,?,?,?,1)",
                                       (key,req["work_id"],canonical_json_bytes(plan).decode(),1,json.dumps({"message":"saved"}),notice))
                        replay=delivery_command(project,Namespace(action="start",key=key),plan)
                        self.assertEqual((replay["notification"],replay["reserved_steps"]),(notice,1))
                        self.assertEqual(delivery_command(project,Namespace(action="_step",key=key,epoch=1))["status"],"already-handled")
                        self.assertEqual(delivery_inbox(project)[0]["result"],{"message":"saved"})
                    os_call.assert_called_once()
            finally:db.close()

    def test_explicit_close_without_replay(self):
        if os.name=="nt":self.skipTest("native runner supplies the explicitly prepared Windows profile")
        with tempfile.TemporaryDirectory() as scratch:self.exercise(SOURCE,Path(scratch),only_closure=True)

    def test_detached_question_and_submission(self):
        if os.name=="nt":self.skipTest("native runner supplies the explicitly prepared Windows profile")
        with tempfile.TemporaryDirectory() as scratch:self.exercise(SOURCE,Path(scratch))

if __name__=="__main__":
    unittest.main()
