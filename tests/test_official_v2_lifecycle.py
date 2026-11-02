"""Explicit v2 exact-artifact lifecycle factory; no real adopter or model calls."""
from pathlib import Path
import json
import copy
import os
import signal
import fcntl
import threading
from unittest import mock
import time
import shutil
import subprocess
import sys
import unittest

from hv2ref import product, official_state as state
from hv2ref.errors import ContractError, InjectedCrash
from hv2ref.official_documents import EffectJournal, canonical
from hv2ref.jsonio import canonical_json_bytes

TIME = '2026-01-01T00:00:00Z'


def build_suite(candidate, predecessor, root, *, predecessor_python=None):
    # Preserve the exact historical payload runtime rather than widening its gate.
    predecessor_python = str(predecessor_python or sys.executable)
    candidate, predecessor, root = map(Path, (candidate, predecessor, root))
    if product.workspace_candidate(predecessor)['release_ref'] != product.OFFICIAL_V2_PREDECESSOR:
        raise RuntimeError('exact predecessor required')
    helper = Path(__file__).parent/'fixtures/delegation_process.py'

    class LifecycleV2Tests(unittest.TestCase):
        def setUp(self):
            self.base=root/self._testMethodName;self.base.mkdir();self.serial=0
        def directory(self):
            self.serial+=1;p=self.base/str(self.serial);p.mkdir();return p
        def call_old(self,target,request,expected=0,source=predecessor):
            result=subprocess.run([predecessor_python,'-I','-S','-B',*(['-O'] if sys.flags.optimize else []),str(helper),str(source),str(target)],
                input=canonical_json_bytes(request),capture_output=True,timeout=120)
            self.assertEqual(expected,result.returncode,(result.stdout+result.stderr).decode()[-3000:])
            return json.loads(result.stdout)
        def git(self,target,*args):
            return subprocess.run(['git','-C',str(target),*args],capture_output=True,check=True,timeout=30).stdout
        def init(self,*,old=False,git=False,cut=None):
            target=self.directory();(target/'sentinel').write_bytes(b'SYNTHETIC_SECRET_SENTINEL\n')
            (target/'a').write_text('Before.\n');(target/'b').write_text('Approved fact.\n')
            if git:self.git(target,'init','-q')
            if old:self.call_old(target,{'action':'init','operation_id':'initial'})
            else:
                p=product.workspace_init_preview(candidate,target,authority_home_id='home-a',operation_id='initial',created_at=TIME)
                if cut:
                    with self.assertRaises(InjectedCrash):product.workspace_init_apply(candidate,target,p['request'],confirm_token=p['confirm_token'],inject_at=cut)
                    product.workspace_init_apply(candidate,target,p['request'],confirm_token=p['confirm_token'],recover=True)
                else:product.workspace_init_apply(candidate,target,p['request'],confirm_token=p['confirm_token'])
            return target
        def truth(self,target):
            return {p.relative_to(target).as_posix():p.read_bytes() for p in target.rglob('*') if p.is_file() and
                    (p.name in ('sentinel','a','b') or p.is_relative_to(target/'.git') or p.is_relative_to(target/'.hrn/executions') or p.is_relative_to(target/'.hrn/work') or p.is_relative_to(target/'.hrn/intents'))}
        def preview(self,target,source=candidate,action='update',op='transition'):
            return product.workspace_switch_preview(target,action=action,source=source,operation_id=op,created_at=TIME)
        def apply(self,target,p,source=candidate,**kw):
            return product.workspace_switch_apply(target,p['request'],confirm_token=p['confirm_token'],source=source,**kw)
        def legacy_capsule(self,target):
            # A historical v1 fixture; never authorizes execution.
            spec={'target':str(target)};grant=state.digest(state.canonical(spec));folder=target/'.hrn/executions'/grant
            folder.mkdir(parents=True,mode=0o700)
            state.publish(folder/'grant.json',{'record_type':'official-execution-grant','schema_version':1,'grant':grant,'spec':spec})
            journal=EffectJournal(folder/'journal.jsonl',create=True);journal.append('granted',{'grant':grant});journal.append('terminal',{'status':'revoked-before-launch'})
            return grant
        def test_exact_transition_and_downgrade_refusal_preserve_v1(self):
            for git in (False,True):
                with self.subTest(git=git):
                    t=self.init(old=True,git=git);grant=self.legacy_capsule(t);before=self.truth(t)
                    p=self.preview(t);self.assertEqual(8,p['request']['schema_version']);self.apply(t,p)
                    self.assertEqual('official-execution-2',product.verify_workspace_product(t)['inventory']['inventory_id'])
                    self.assertEqual('revoked-before-launch',state.read_capsule(t,grant)['status']);self.assertEqual(before,self.truth(t))
                    with self.assertRaisesRegex(ContractError,'downgrade'):self.preview(t,None,'rollback','old-rollback')
                    self.assertEqual(before,self.truth(t));self.call_old(t,{'action':'verify'},65)
        def test_transition_then_detach_preserves_predecessor_history(self):
            for git in (False,True):
                with self.subTest(git=git):
                    t=self.init(old=True,git=git);grant=self.legacy_capsule(t);before=self.truth(t)
                    p=self.preview(t);self.apply(t,p)
                    p=product.workspace_detach_preview(t,operation_id='transition-detach',created_at=TIME)
                    product.workspace_detach_apply(t,p['request'],confirm_token=p['confirm_token'])
                    self.assertEqual(before,self.truth(t));self.assertFalse((t/'colvia').exists())
                    self.assertEqual('revoked-before-launch',state.read_capsule(t,grant)['status'])
                    audit=Path(__file__).parent/'fixtures/product_plain_auditor.py'
                    result=subprocess.run([sys.executable,'-I','-S','-B',str(audit),str(t)],capture_output=True,timeout=30)
                    self.assertEqual(0,result.returncode,result.stdout+result.stderr)

        def test_transition_prefixes_old_writer_refusal_and_exact_recovery(self):
            for cut in ('after-receipt','after-staged-inventory','after-release','after-launcher','after-binding'):
                with self.subTest(cut=cut):
                    t=self.init(old=True,git=cut in ('after-receipt','after-binding'));before=self.truth(t);p=self.preview(t)
                    old_detach=self.call_old(t,{'action':'detach-preview','operation_id':'old-detach'})
                    with self.assertRaises(InjectedCrash):self.apply(t,p,inject_at=cut)
                    self.call_old(t,{'action':'detach','packet':old_detach},65)
                    self.assertEqual(before,self.truth(t))
                    self.apply(t,p,recover=True);self.assertEqual(before,self.truth(t))
                    self.apply(t,p,recover=True);self.assertEqual(before,self.truth(t))
        def test_same_window_update_rollback_and_detach_preserve_v2(self):
            variant=self.base/'variant';shutil.copytree(candidate,variant)
            original=candidate/'docs/OFFICIAL-EXECUTION.md'
            original_bytes=original.read_bytes();original_mode=original.stat().st_mode
            doc=variant/'docs/OFFICIAL-EXECUTION.md';copied_mode=doc.stat().st_mode & 0o777
            doc.chmod(copied_mode | 0o200)
            try:doc.write_bytes(doc.read_bytes()+b'\n<!-- synthetic compatible variant -->\n')
            finally:doc.chmod(copied_mode)
            self.assertEqual(original_bytes,original.read_bytes())
            self.assertEqual(original_mode,original.stat().st_mode)
            self.assertEqual(copied_mode,doc.stat().st_mode & 0o777)
            for git in (False,True):
                with self.subTest(git=git):
                    t=self.init(git=git)
                    p=self.preview(t,variant,op='same-update');self.apply(t,p,variant)
                    seed=Path(__file__).parent/'fixtures/official_fixture.py'
                    result=subprocess.run([sys.executable,'-I','-S','-B',str(seed),str(t)],capture_output=True,timeout=60)
                    self.assertEqual(0,result.returncode,result.stdout+result.stderr)
                    runtime=self.directory();runtime.chmod(0o700);control=self.directory();control.chmod(0o700)
                    state.publish(control/'store.json',{'schema_version':1,'store_id':'b'*32})
                    request={'work_id':'official-work','worker_root':str(t),'documents':{
                        'files':{'Editable':{'path':str(t/'a'),'view':{'kind':'replace-range','ranges':[[0,len((t/'a').read_bytes())]]}},
                                 'Reference':{'path':str(t/'b'),'view':{'kind':'full'}}},'output':'Editable',
                        'claims':{'Editable':{'required':['Approved fact.'],'forbidden':[],'evidence':[{'file_id':'Reference','quote':'Approved fact.'}]}},'approved_external_links':[]},
                        'read_ids':['Editable','Reference'],'prompt':'Synthetic Q record','owner_statement':'Synthetic Q authorization',
                        'runtime':{'sha256':{'BIN':'a'*64}},'runtime_root':str(runtime),'host_control_root':str(control),
                        'expires_wall_ns':time.time_ns()+600*10**9,'seconds':90,'worker_limit':5}
                    reader=Path(__file__).parent/'fixtures/official_reader_compat.py'
                    result=subprocess.run([sys.executable,'-I','-S','-B',str(reader),str(variant),str(t),'closed'],input=json.dumps({'request':request}).encode(),capture_output=True,timeout=60)
                    self.assertEqual(0,result.returncode,result.stdout+result.stderr);grant=json.loads(result.stdout)['grant']
                    value=state.read_capsule(t,grant)
                    self.assertEqual(product.workspace_candidate(variant)['release_ref']['sha256'],value['scope']['installation']['release_digest'])
                    before=self.truth(t);rollback=self.preview(t,None,'rollback','same-rollback');self.apply(t,rollback,None)
                    self.assertEqual(before,self.truth(t));self.assertEqual('revoked-before-launch',state.read_capsule(t,grant)['status'])
                    p=product.workspace_detach_preview(t,operation_id='detach',created_at=TIME)
                    with self.assertRaises(InjectedCrash):product.workspace_detach_apply(t,p['request'],confirm_token=p['confirm_token'],inject_at='after-file')
                    product.workspace_detach_apply(t,p['request'],confirm_token=p['confirm_token'],recover=True)
                    self.assertEqual(before,self.truth(t));self.assertFalse((t/'colvia').exists())
                    audit=Path(__file__).parent/'fixtures/product_plain_auditor.py'
                    result=subprocess.run([sys.executable,'-I','-S','-B',str(audit),str(t)],capture_output=True,timeout=30)
                    self.assertEqual(0,result.returncode,(result.stdout+result.stderr).decode())
        def test_fresh_init_repair_failure_recovery_and_drift(self):
            for git in (False,True):
                with self.subTest(git=git):
                    t=self.init(git=git,cut='after-launcher');before=self.truth(t);launcher=t/'colvia';launcher.write_bytes(b'synthetic damage\n')
                    backup=self.base/('backup-'+str(git));p=product.workspace_repair_preview(candidate,t,backup,operation_id='repair',created_at=TIME)
                    with self.assertRaises(InjectedCrash):product.workspace_repair_apply(candidate,t,p['request'],confirm_token=p['confirm_token'],inject_at='after-file')
                    product.workspace_repair_apply(candidate,t,p['request'],confirm_token=p['confirm_token'],recover=True)
                    self.assertEqual(before,self.truth(t));product.verify_workspace_product(t)
                    p=product.workspace_detach_preview(t,operation_id='detach-drift',created_at=TIME)
                    launcher.write_bytes(launcher.read_bytes()+b'\n# drift\n')
                    with self.assertRaises(ContractError):product.workspace_detach_apply(t,p['request'],confirm_token=p['confirm_token'])
                    self.assertEqual(before,self.truth(t))
        def test_old_writer_families_refuse_first_v2_receipt_without_mutation(self):
            t=self.init(old=True);binding=product.verify_workspace_product(t)
            payload=Path(binding['release_path'])/'payload'
            material=self.call_old(t,{'action':'local'},source=payload)
            work_packet=self.call_old(t,{'action':'work-prepare','wid':'local-work','operation_id':'old-accept'},source=payload)
            draft=self.call_old(t,{'action':'draft','iid':'late-intent'},source=payload)['drafts']['draft-1']
            intent_packet=self.call_old(t,{'action':'intent-prepare','draft':draft,'operation_id':'old-intent-accept'},source=payload)
            detach=self.call_old(t,{'action':'detach-preview','operation_id':'old-detach'})
            variant=self.base/'old-compatible';shutil.copytree(predecessor,variant)
            doc=variant/'docs/OFFICIAL-EXECUTION.md';doc.write_bytes(doc.read_bytes()+b'\n<!-- old compatible fixture -->\n')
            switch=self.call_old(t,{'action':'switch-preview','candidate':str(variant),'operation_id':'old-update'})
            graph=material['graph'];selected=graph['selections'][graph['current']['selection_ref']['id']]
            revision=copy.deepcopy(graph['revisions'][selected['revision_ref']['id']]);revision.update(record_id='late-checkpoint',operation='checkpoint',progress='active',expected_prior_selection=graph['current']['selection_ref'])
            manifest=graph['manifests'][revision['result_refs']['manifest']['id']]
            requests=[{'action':'draft','iid':'new-intent'},{'action':'intent-apply','packet':intent_packet},
                {'action':'work-prepare','wid':'local-work'},{'action':'work-apply','packet':work_packet},
                {'action':'work-publish','identity':graph['identity'],'revision':revision,'manifest':manifest,'selection_id':'late-checkpoint','operation_id':'late-publish'},
                {'action':'switch','candidate':str(variant),'packet':switch},{'action':'detach','packet':detach}]
            from hv2ref.candidates import read_candidates
            requests.append({'action':'candidate','request':{'record_type':'candidate-request','schema_version':1,'authority_home_id':'home-a','request_id':'late-candidate','candidate_id':'idea-a','action':'add',
                'expected_sha256':read_candidates(t)['sha256'],'writer':'agent:fixture','owner_statement':'Synthetic','reason':'Synthetic','observed_at':TIME,
                'payload':{'title':'Synthetic','purpose':'Preserve','expected_effect':'Visible','related_candidates':[]}}})
            p=self.preview(t)
            with self.assertRaises(InjectedCrash):self.apply(t,p,inject_at='after-receipt')
            from tests.test_delegation_window_transition import snapshot
            before=snapshot(t)
            for source in (predecessor,payload):
                for request in requests:
                    with self.subTest(source='retained' if source==predecessor else 'installed',action=request['action']):
                        result=self.call_old(t,request,65,source)
                        self.assertIn(result['code'],('HV2-WORKSPACE-PRODUCT','HV2-WORKSPACE-LAUNCHER'))
                        self.assertEqual(before,snapshot(t))
            self.apply(t,p,recover=True)

        def test_old_rollback_and_completed_repair_retry_refuse_first_v2_receipt(self):
            from tests.test_delegation_window_transition import snapshot
            t = self.init(old=True)
            variant = self.base / 'old-compatible'; shutil.copytree(predecessor, variant)
            doc = variant / 'docs/OFFICIAL-EXECUTION.md'; doc.write_bytes(doc.read_bytes() + b'\n<!-- prior variant -->\n')
            self.call_old(t, {'action': 'switch', 'candidate': str(variant), 'operation_id': 'old-variant'})
            self.call_old(t, {'action': 'switch', 'candidate': str(predecessor), 'operation_id': 'exact-old'})
            rollback = self.call_old(t, {'action': 'switch-preview', 'switch_action': 'rollback', 'operation_id': 'old-rollback'})
            (t / 'colvia').write_bytes(b'synthetic damaged launcher\n')
            repair = self.call_old(t, {'action': 'repair-preview', 'backup': str(self.base / 'backup'), 'operation_id': 'old-repair'})
            self.call_old(t, {'action': 'repair', 'packet': repair})
            payload = Path(product.verify_workspace_product(t)['release_path']) / 'payload'
            packet = self.preview(t)
            with self.assertRaises(InjectedCrash): self.apply(t, packet, inject_at='after-receipt')
            before = snapshot(t); saved = snapshot(self.base / 'backup', scratch=True)
            for source in (predecessor, payload):
                for request in ({'action': 'switch', 'switch_action': 'rollback', 'packet': rollback},
                                {'action': 'repair', 'packet': repair, 'recover': True}):
                    with self.subTest(source='retained' if source == predecessor else 'installed', action=request['action']):
                        self.call_old(t, request, 65, source)
                        self.assertEqual(before, snapshot(t)); self.assertEqual(saved, snapshot(self.base / 'backup', scratch=True))
            self.apply(t, packet, recover=True)

        def test_actual_process_death_after_receipt_and_exact_recovery(self):
            t = self.init(old=True, git=True); before = self.truth(t); packet = self.preview(t)
            fixture = Path(__file__).parent / 'fixtures/official_transition_process.py'
            child = subprocess.Popen([sys.executable, '-I', '-S', '-B', str(fixture), str(candidate), str(t)],
                                     stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            try:
                out, err = child.communicate(canonical_json_bytes(packet), timeout=60)
                self.assertEqual(-signal.SIGKILL, child.returncode, out + err)
            finally:
                if child.poll() is None: child.kill(); child.wait(timeout=5)
            self.assertEqual(before, self.truth(t))
            self.call_old(t, {'action': 'draft', 'iid': 'after-death'}, 65)
            self.apply(t, packet, recover=True)
            self.assertEqual(before, self.truth(t)); product.verify_workspace_product(t)

        def test_actual_waiting_old_writer_refuses_after_first_new_receipt(self):
            from tests.test_delegation_window_transition import snapshot
            t = self.init(old=True); packet = self.preview(t)
            payload = Path(product.verify_workspace_product(t)['release_path']) / 'payload'
            lock = t / '.hrn/locks/writer.lock'; expected = lock.stat()
            attempt, acquired = self.base / 'attempt.json', self.base / 'acquired.json'
            request = {'action': 'draft', 'iid': 'waiting-old',
                       'lock_observation': {'attempt': str(attempt), 'acquired': str(acquired)}}
            ready, release = threading.Event(), threading.Event()
            errors, writer_id, before_unlock = [], [], []
            native = fcntl.flock
            def write_new():
                writer_id.append(threading.get_ident())
                try: self.apply(t, packet, inject_at='after-receipt')
                except BaseException as exc: errors.append(exc)
            def observe(fd, operation):
                info = os.fstat(fd.fileno() if hasattr(fd, 'fileno') else fd)
                belongs = writer_id and threading.get_ident() == writer_id[0] and (info.st_dev, info.st_ino) == (expected.st_dev, expected.st_ino)
                if belongs and operation & fcntl.LOCK_UN: before_unlock.append(snapshot(t))
                result = native(fd, operation)
                if belongs and operation & fcntl.LOCK_EX:
                    ready.set()
                    if not release.wait(30): raise RuntimeError('fixed waiter deadline')
                return result
            child = None
            with mock.patch.object(fcntl, 'flock', observe):
                thread = threading.Thread(target=write_new); thread.start()
                try:
                    self.assertTrue(ready.wait(30), errors)
                    child = subprocess.Popen([predecessor_python, '-I', '-S', '-B', str(helper), str(payload), str(t)],
                                             stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                    child.stdin.write(canonical_json_bytes(request)); child.stdin.close(); child.stdin = None
                    deadline = time.monotonic() + 30
                    while not attempt.exists():
                        self.assertIsNone(child.poll()); self.assertLess(time.monotonic(), deadline); time.sleep(.01)
                    self.assertFalse(acquired.exists())
                finally:
                    release.set(); thread.join(60)
            try:
                self.assertFalse(thread.is_alive()); self.assertEqual(len(errors), 1)
                self.assertIsInstance(errors[0], InjectedCrash); self.assertEqual(errors[0].point, 'after-receipt')
                out, err = child.communicate(timeout=60)
                self.assertEqual(child.returncode, 65, out + err)
                self.assertEqual(json.loads(out)['message'], 'invalid receipt identity/schema')
                self.assertEqual(len(before_unlock), 1); self.assertEqual(before_unlock[0], snapshot(t))
                a, b = json.loads(attempt.read_bytes()), json.loads(acquired.read_bytes())
                self.assertEqual((a['pid'], a['dev'], a['ino']), (child.pid, b['dev'], b['ino']))
            finally:
                if child is not None and child.poll() is None: child.kill(); child.wait(timeout=5)
            self.apply(t, packet, recover=True)

        def test_nonexact_predecessor_and_unsafe_target_refused(self):
            t=self.init(old=True);variant=self.base/'old-variant';shutil.copytree(predecessor,variant)
            doc=variant/'docs/OFFICIAL-EXECUTION.md';doc.write_bytes(doc.read_bytes()+b'\n<!-- synthetic old variant -->\n')
            self.call_old(t,{'action':'switch','candidate':str(variant),'operation_id':'old-update'})
            before=self.truth(t)
            with self.assertRaisesRegex(ContractError,'exact fixed predecessor'):self.preview(t)
            self.assertEqual(before,self.truth(t))
            alias=self.base/'alias';alias.symlink_to(t,target_is_directory=True)
            with self.assertRaises(ContractError):self.preview(alias)
            self.assertEqual(before,self.truth(t))
    return unittest.defaultTestLoader.loadTestsFromTestCase(LifecycleV2Tests)
