"""A notification always opens its original question/result in its own project."""
import hashlib
import json
import sys
import subprocess
import tempfile
import time
import unittest
from contextlib import closing
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from hv2ref import continuation as notice, work
from hv2ref.errors import ContractError
from hv2ref.product import workspace_init_apply, workspace_init_preview, verify_workspace_product
from tests.fixtures.delegation_process import TIME


class NoticeDetailTests(unittest.TestCase):
    def test_duplicate_ids_question_history_and_replaced_project(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            store = root / "store"
            store.mkdir(mode=0o700)
            events = {}
            for name in ("Alpha", "Bravo"):
                target = root / name
                target.mkdir()
                for filename in ("a","b"):
                    (target / filename).write_text(name)
                home = "home-" + name
                init = workspace_init_preview(ROOT,target,authority_home_id=home,operation_id="init",created_at=TIME)
                workspace_init_apply(ROOT,target,init["request"],confirm_token=init["confirm_token"])
                installed = Path(verify_workspace_product(target)["release_path"]) / "payload"
                proc = subprocess.run([sys.executable,"-ISB",str(ROOT/"tests/fixtures/delegation_process.py"),
                                       str(installed),str(target)],input=b'{"action":"local","wid":"same-work"}',
                                      capture_output=True,timeout=45)
                self.assertEqual(proc.returncode,0,proc.stdout[-400:])
                graph = json.loads(proc.stdout)["graph"]
                source = {"project":str(target),"home":home,"binding":verify_workspace_product(target)["binding_ref"],
                          "work_id":"same-work","scope":["a","b"],"label":name+" (same-work)",
                          "selection":work.record_ref(graph["selections"]["local-1"])}
                plan = {"source":source,"request":{"action":"submit","ask":True}}
                key = work._digest(plan)
                with closing(notice._delivery_db(target,create=True)) as db:
                    with db:
                        db.execute("INSERT INTO delivery VALUES (?,?,?,'question',1,0,?,?,?,1)",
                                   (key,"same-work",json.dumps(plan),int(time.time())+120,None,"attempted"))
                    question = notice.record_notification(store,target,db,key,1,"question")
                    result = {"message":"Submitted "+name, "selection":graph["current"]["selection_ref"]}
                    with db:
                        db.execute("UPDATE delivery SET phase='done',epoch=2,used=1,result=? WHERE id=?",
                                   (json.dumps(result),key))
                    done = notice.record_notification(store,target,db,key,2,"done")
                    self.assertNotEqual(question,done)
                    events[name] = (question,done)
            def authority():
                return {f.relative_to(root):hashlib.sha256(f.read_bytes()).digest()
                        for name in ("Alpha","Bravo") for f in (root/name/".hrn").rglob("*") if f.is_file()}
            before = authority()
            for name,(question,done) in events.items():
                historic = notice.notification_detail(store,question)
                detail = notice.notification_detail(store,done)
                self.assertIn("알림 당시의 질문",historic)
                self.assertIn("이 질문은 닫혔습니다. 결과가 준비됐습니다",historic)
                self.assertNotIn("Submitted",historic)
                self.assertIn("Submitted "+name,detail)
                self.assertIn("당시 제출 내용 · human review", detail)
                self.assertIn("현재 검토할 내용 · human review", detail)
                self.assertNotIn("이전 제출에 대한 알림", detail)
                self.assertIn(name+" (same-work)",detail)
            self.assertEqual(before,authority())
            for unknown in ("../other","0"*32):
                with self.assertRaises(ContractError):
                    notice.notification_detail(store,unknown)
            (root/"Alpha").rename(root/"moved")
            (root/"Bravo").rename(root/"Alpha")
            with self.assertRaises(ContractError):
                notice.notification_detail(store,events["Alpha"][1])
