"""Current-window checks and an explicit retained-artifact transition factory.

Default discovery never substitutes synthetic current code for an older artifact.
The factory requires the exact retained source and its independently recorded hash.
"""
from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

from hv2ref.errors import ContractError, InjectedCrash
from hv2ref.jsonio import canonical_json_bytes
from hv2ref.product import (SERIAL_MANAGED_PATHS, source_root, workspace_candidate,
                           workspace_switch_preview, workspace_switch_apply,
                           verify_workspace_product, workspace_detach_preview,
                           workspace_detach_apply)
from hv2ref.work import make_manifest, record_ref, snapshot
from hv2ref.workspace import git_environment
import test_productization_safety as fixtures
import test_candidates as candidate_fixtures

PREFIXES = ('after-receipt', 'after-staged-inventory', 'after-staged-payload',
            'after-release', 'after-launcher', 'after-binding')


class CheckoutWindowTests(unittest.TestCase):
    def test_current_source_declares_checkout_window_with_same_membership(self):
        candidate = workspace_candidate(source_root())
        self.assertEqual('checkout-1', candidate['inventory']['inventory_id'])
        self.assertEqual(29, len(candidate['inventory']['entries']))
        self.assertEqual(list(SERIAL_MANAGED_PATHS), [e['path'] for e in candidate['inventory']['entries']])

    def test_old_and_unknown_source_declarations_are_not_current_candidates(self):
        from hv2ref.product import _launcher_inventory_window
        for window in ('human-1', 'worker-1', 'umbrella-1', 'planning-1', 'unknown'):
            with self.subTest(window=window), self.assertRaises(ContractError):
                _launcher_inventory_window(('WORKSPACE_INVENTORY_ID = '+repr(window)+'\n').encode())


class DetachVersionTests(unittest.TestCase):
    setUp = fixtures.ActualWorkspaceInitTests.setUp
    TIME = fixtures.ActualWorkspaceInitTests.TIME

    def seed(self):
        from hv2ref.product import workspace_init_preview,workspace_init_apply
        preview=workspace_init_preview(self.source,self.target,authority_home_id='home-a',operation_id='init-a',created_at=self.TIME)
        workspace_init_apply(self.source,self.target,preview['request'],confirm_token=preview['confirm_token'])
        preview=workspace_detach_preview(self.target,operation_id='detach-a',created_at=self.TIME)
        with self.assertRaises(InjectedCrash):workspace_detach_apply(self.target,preview['request'],confirm_token=preview['confirm_token'],inject_at='after-receipt')
        return preview

    def test_paired_version_reader_and_independent_auditor_reject_invalid_versions(self):
        from hv2ref.product import workspace_detached_status
        preview=self.seed();path=self.target/'.hrn/detached.json';raw=path.read_bytes();receipt=json.loads(raw)
        self.assertEqual(2,receipt['schema_version']);self.assertEqual(2,receipt['plan']['schema_version'])
        for outer,inner in ((1,2),(2,1),(3,3),(True,True),(None,None),(2,True)):
            bad=copy.deepcopy(receipt);bad['schema_version']=outer;bad['plan']['schema_version']=inner
            path.write_bytes(canonical_json_bytes(bad));before=fixtures.exact_snapshot(self.target)
            with self.subTest(outer=outer,inner=inner):
                with self.assertRaises(ContractError):workspace_detached_status(self.target)
                result=subprocess.run([sys.executable,'-I','-B',str(self.source/'tests/fixtures/product_plain_auditor.py'),str(self.target)],capture_output=True,timeout=30)
                self.assertNotEqual(0,result.returncode)
                self.assertEqual(before,fixtures.exact_snapshot(self.target))
        path.write_bytes(raw)
        self.assertEqual('partial',workspace_detached_status(self.target)['classification'])
        workspace_detach_apply(self.target,preview['request'],confirm_token=preview['confirm_token'],recover=True)
        result=subprocess.run([sys.executable,'-I','-B',str(self.source/'tests/fixtures/product_plain_auditor.py'),str(self.target)],capture_output=True,timeout=30)
        self.assertEqual(0,result.returncode,result.stdout+result.stderr)

    def test_older_synthetic_predecessors_refuse_preview_and_apply_before_writes(self):
        from unittest import mock
        import hv2ref.product as product
        preview=product.workspace_init_preview(self.source,self.target,authority_home_id='home-a',operation_id='init-a',created_at=self.TIME)
        product.workspace_init_apply(self.source,self.target,preview['request'],confirm_token=preview['confirm_token'])
        state=product._workspace_observe(self.target)
        counterpart=self.base/'counterpart'
        for name in SERIAL_MANAGED_PATHS:
            dest=counterpart/name;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(self.source/name,dest)
        with (counterpart/'README.md').open('a') as handle:handle.write('\nSynthetic counterpart.\n')
        plan=workspace_switch_preview(self.target,action='update',source=counterpart,operation_id='next-a',created_at=self.TIME)
        before=fixtures.exact_snapshot(self.target)
        for window in ('human-1','worker-1','umbrella-1'):
            old=copy.deepcopy(state);old['binding']['active_release']['inventory_id']=window
            # Synthetic validated-observation seam isolates admission policy;
            # The separate factory covers exact planning-1 only, not these older windows.
            with self.subTest(window=window),mock.patch.object(product,'_workspace_observe',return_value=old):
                with self.assertRaisesRegex(ContractError,'predecessor'):
                    workspace_switch_preview(self.target,action='update',source=self.source,operation_id='refuse-a',created_at=self.TIME)
                with self.assertRaisesRegex(ContractError,'predecessor'):
                    workspace_switch_apply(self.target,plan['request'],source=counterpart,confirm_token=plan['confirm_token'])
            self.assertEqual(before,fixtures.exact_snapshot(self.target))

    def test_legacy_version_is_read_only_for_new_source(self):
        from hv2ref.product import workspace_detached_status
        preview=self.seed();path=self.target/'.hrn/detached.json';receipt=json.loads(path.read_bytes())
        receipt['schema_version']=receipt['plan']['schema_version']=1;path.write_bytes(canonical_json_bytes(receipt))
        plan=receipt['plan'];token=hashlib.sha256(canonical_json_bytes(plan)).hexdigest()[:16]
        before=fixtures.exact_snapshot(self.target)
        self.assertEqual('partial',workspace_detached_status(self.target)['classification'])
        for recover in (False,True):
            with self.assertRaisesRegex(ContractError,'legacy detach writes'):
                workspace_detach_apply(self.target,plan,confirm_token=token,recover=recover)
        self.assertEqual(before,fixtures.exact_snapshot(self.target))


def make_exact_suite(old_source: Path, new_source: Path, old_sha256: str, *, phase: str):
    """Fixed exact-artifact entry; a missing or different P is an error, never a skip."""
    if phase not in ('checkout-early', 'checkout-exact'):
        raise ValueError('unsupported exact-artifact phase')
    old_source = old_source.resolve(strict=True)
    new_source = new_source.resolve(strict=True)
    entries = [{'path': n, 'sha256': hashlib.sha256((old_source/n).read_bytes()).hexdigest(),
                'size_bytes': len((old_source/n).read_bytes())} for n in SERIAL_MANAGED_PATHS]
    inventory = {'record_type': 'release-inventory', 'schema_version': 1,
                 'inventory_id': 'planning-1', 'entries': entries}
    if hashlib.sha256(canonical_json_bytes(inventory)).hexdigest() != old_sha256:
        raise ValueError('retained P does not reproduce the required inventory')
    new_candidate = workspace_candidate(new_source)
    observations = []

    class ExactCheckoutTransitionTests(unittest.TestCase):
        TIME = fixtures.ActualWorkspaceInitTests.TIME
        draft = fixtures.ActualWorkspaceInitTests.draft
        accept_intent = fixtures.ActualWorkspaceInitTests.accept_intent

        def setUp(self):
            self.temp = tempfile.TemporaryDirectory(prefix='checkout-transition-')
            self.addCleanup(self.temp.cleanup)
            self.base = Path(self.temp.name).resolve()
            self.target = self.base/'project'; self.target.mkdir()
            (self.target/'a').write_bytes(b'before\n')
            self.git('init', '-q')
            self.git('config', 'user.name', 'Fixture')
            self.git('config', 'user.email', 'fixture@example.invalid')
            init = ['init', '--profile', 'planning-1', '--target', self.target, '--source', old_source,
                    '--authority-home-id', 'home-a', '--operation-id', 'init-a', '--observed-at', self.TIME]
            self.init_preview = self.source_call(init)
            self.source_call(['init', '--profile', 'planning-1', '--target', self.target, '--source', old_source,
                              '--apply', '--input', '-', '--confirm', self.init_preview['confirm_token']], self.init_preview['request'])
            state = verify_workspace_product(self.target)
            self.assertEqual(old_sha256, hashlib.sha256(canonical_json_bytes(state['inventory'])).hexdigest())
            self.old_payload = Path(state['release_path'])/'payload'
            self.assertEqual((old_source/'hv2').read_bytes(), (self.target/'hv2').read_bytes())

        def git(self, *args):
            result = subprocess.run(['git', '-c', 'maintenance.auto=false', '-c', 'gc.auto=0', '-C', str(self.target), *map(str,args)],
                                    env=git_environment(), capture_output=True, timeout=30, check=True)
            return result.stdout

        def invoke(self, argv, value=None, expected=0):
            result = subprocess.run(list(map(str, argv)), cwd=self.target, env=git_environment(),
                                    input=None if value is None else canonical_json_bytes(value),
                                    capture_output=True, timeout=45)
            if expected is not None:
                self.assertEqual(expected, result.returncode, (result.stdout+result.stderr).decode(errors='replace'))
            return result

        def source_call(self, args, value=None):
            return json.loads(self.invoke([old_source/'hv2', '--source-checkout', *args], value).stdout)

        def installed(self, args, value=None, *, expected=0):
            return self.invoke([self.target/'hv2', *args], value, expected)

        def retained_runtime(self, args, value=None):
            # Load the exact retained installed P modules. This also tests the
            # older code's guard after the root launcher has already become Q.
            code = 'import sys;from pathlib import Path;sys.path.insert(0,sys.argv.pop(1));target=Path(sys.argv.pop(1));from hv2ref.cli import main;raise SystemExit(main(workspace_target=target))'
            return self.invoke([sys.executable, '-I', '-B', '-c', code, self.old_payload/'src', self.target, *args], value, None)

        def prepare_old_requests(self):
            intent = self.accept_intent()
            sha = verify_workspace_product(self.target)['launcher_sha256']
            identity = {'record_type':'work-identity','schema_version':1,'authority_home_id':'home-a','work_id':'work-a',
                        'work_type':'change','created_at':self.TIME,'acceptance_authority':'owner','lineage':None}
            base = snapshot(self.target, verified_launcher_sha256=sha); prior = None
            for number, operation in ((1,'start'), (2,'submit-result')):
                if number == 2: (self.target/'a').write_bytes(b'after\n')
                manifest = make_manifest(base, snapshot(self.target, verified_launcher_sha256=sha), scope=['a'])
                digest = hashlib.sha256(canonical_json_bytes(manifest)).hexdigest()
                revision = {'record_type':'work-revision','schema_version':1,'authority_home_id':'home-a','work_id':'work-a',
                            'record_id':f'revision-{number}','observed_at':self.TIME,'observed_scope':['fixture'],'unavailable_scope':[],
                            'author':'agent','operation':operation,'expected_prior_selection':prior,'intent_ref':intent,'scope':['a'],
                            'document_refs':[],'evidence_refs':[],'result_refs':{'manifest':{'id':digest,'sha256':digest}},
                            'progress':'active' if number==1 else 'review','next_action':'owner review','relations':[],
                            'rebind_from':None,'execution_context':{'mode':'local','attempt_id':f'attempt-{number}'}}
                publication = {'identity':identity,'revision':revision,'manifest':manifest,
                               'selection_id':f'selection-{number}','operation_id':f'publish-{number}'}
                graph = json.loads(self.installed(['work','publish'],publication).stdout)
                prior = graph['current']['selection_ref']
            work_prepare = {'work_id':'work-a','action':'accept','actor':'owner','reason':'fixture','request_id':'old-work-accept',
                            'observed_at':self.TIME,'revision_ref':None,'supersedes':None}
            work_ticket = json.loads(self.installed(['work','prepare'],work_prepare).stdout)
            draft = self.draft(); draft.update(intent_id='intent-b', revision_id='draft-b')
            self.installed(['intent','draft'],draft)
            intent_prepare = {'intent_id':'intent-b','revision_ref':record_ref(draft,'revision_id'),'actor':'owner','reason':'fixture',
                              'request_id':'old-intent-accept','observed_at':self.TIME}
            intent_ticket = json.loads(self.installed(['intent','prepare'],intent_prepare).stdout)
            self.installed(['candidate','add'],candidate_fixtures.proposal(self.target,cid='existing'))
            candidate = candidate_fixtures.proposal(self.target,cid='next')
            p2 = self.base/'p2'
            for name in SERIAL_MANAGED_PATHS:
                path = p2/name;path.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(old_source/name,path)
            with (p2/'README.md').open('a') as handle: handle.write('\nSynthetic old-window counterpart.\n')
            lifecycle = self.source_call(['update','--profile','planning-1','--target',self.target,'--source',p2,
                                          '--operation-id','old-update','--observed-at',self.TIME])
            detach = self.source_call(['detach','--profile','planning-1','--target',self.target,
                                       '--operation-id','old-detach','--observed-at',self.TIME])
            damaged = self.old_payload/'docs/REFERENCE.md'; original = damaged.read_bytes(); damaged.write_bytes(b'damaged fixture\n')
            repair = self.source_call(['repair','--target',self.target,'--source',old_source,'--backup',self.base/'repair-backup',
                                       '--operation-id','old-repair','--observed-at',self.TIME])
            damaged.write_bytes(original)
            self.git('add','.');self.git('commit','-qm','synthetic P baseline')
            installed_requests = [
                ('work-publish',['work','publish'],publication),
                ('work-prepare',['work','prepare'],work_prepare),
                ('work-apply',['work','apply','--confirm',work_ticket['confirm_token']],work_ticket['ticket']),
                ('intent-draft',['intent','draft'],draft),
                ('intent-prepare',['intent','prepare'],intent_prepare),
                ('intent-apply',['intent','apply','--confirm',intent_ticket['confirm_token']],intent_ticket['ticket']),
                ('candidate-add',['candidate','add'],candidate),
                ('update-preview',['update','--source',p2,'--operation-id','retry-preview','--observed-at',self.TIME],None),
                ('update-apply',['update','--source',p2,'--apply','--input','-','--confirm',lifecycle['confirm_token']],lifecycle['request']),
                ('detach-preview',['detach','--operation-id','retry-detach','--observed-at',self.TIME],None),
                ('detach-apply',['detach','--apply','--input','-','--confirm',detach['confirm_token']],detach['request'])]
            source_requests = [
                ('update-preview',['update','--profile','planning-1','--target',self.target,'--source',p2,'--operation-id','retry-source','--observed-at',self.TIME],None),
                ('update-apply',['update','--profile','planning-1','--target',self.target,'--source',p2,'--apply','--input','-','--confirm',lifecycle['confirm_token']],lifecycle['request']),
                ('repair-preview',['repair','--target',self.target,'--source',old_source,'--backup',self.base/'repair-new','--operation-id','repair-new','--observed-at',self.TIME],None),
                ('repair-apply',['repair','--target',self.target,'--source',old_source,'--apply','--input','-','--confirm',repair['confirm_token']],repair['request']),
                ('detach-preview',['detach','--profile','planning-1','--target',self.target,'--operation-id','detach-source','--observed-at',self.TIME],None),
                ('detach-apply',['detach','--profile','planning-1','--target',self.target,'--apply','--input','-','--confirm',detach['confirm_token']],detach['request'])]
            return installed_requests, source_requests

        def refused(self, label, command):
            before = fixtures.exact_snapshot(self.base)
            result = command()
            self.assertNotEqual(0, result.returncode, label)
            self.assertEqual(before, fixtures.exact_snapshot(self.base), label)
            try: outcome = json.loads(result.stdout)
            except (ValueError, UnicodeDecodeError): outcome = {'stdout':result.stdout.decode(errors='replace')[:250], 'stderr':result.stderr.decode(errors='replace')[:250]}
            observations.append({'test':self.id(),'entry':label,'exit':result.returncode,'outcome':outcome,'preserved':True})

        def prefix(self, point):
            installed_requests, source_requests = self.prepare_old_requests()
            preview = workspace_switch_preview(self.target,action='update',source=new_source,operation_id='to-checkout',created_at=self.TIME)
            truth = {n:v for n,v in fixtures.exact_snapshot(self.target).items() if n.startswith(('.hrn/intents/', '.hrn/work/', '.hrn/planning/', '.git/')) or n in ('a','.hrn/format.json')}
            with self.assertRaises(InjectedCrash):
                workspace_switch_apply(self.target, preview['request'],confirm_token=preview['confirm_token'],source=new_source,inject_at=point)
            p_root_launcher = (self.target/'hv2').read_bytes() == (old_source/'hv2').read_bytes()
            self.assertEqual(point in PREFIXES[:4], p_root_launcher)
            for label,args,value in installed_requests:
                with self.subTest(point=point,entry='retained-P-'+label):
                    self.refused('retained-P-'+label, lambda a=args,v=value:self.retained_runtime(a,v))
                if p_root_launcher:
                    with self.subTest(point=point,entry='root-P-'+label):
                        self.refused('root-P-'+label, lambda a=args,v=value:self.installed(a,v,expected=None))
            for label,args,value in source_requests:
                with self.subTest(point=point,entry='source-P-'+label):
                    self.refused('source-P-'+label,lambda a=args,v=value:self.invoke([old_source/'hv2','--source-checkout',*a],v,None))
            recovered = workspace_switch_apply(self.target,preview['request'],confirm_token=preview['confirm_token'],source=new_source,recover=True)
            self.assertIn(recovered['classification'],('updated','replayed'))
            self.assertEqual(new_candidate['inventory'],verify_workspace_product(self.target)['inventory'])
            after = fixtures.exact_snapshot(self.target)
            self.assertEqual(truth,{n:after[n] for n in truth})
            observations.append({'test':self.id(),'prefix':point,'root_was_P':p_root_launcher,'Q_recovered':True,'truth_and_git_preserved':True})

        def detach_prefix(self, point):
            preview = workspace_switch_preview(self.target,action='update',source=new_source,operation_id='to-checkout',created_at=self.TIME)
            workspace_switch_apply(self.target,preview['request'],confirm_token=preview['confirm_token'],source=new_source)
            detached = workspace_detach_preview(self.target,operation_id='detach-q',created_at=self.TIME)
            with self.assertRaises(InjectedCrash):
                workspace_detach_apply(self.target,detached['request'],confirm_token=detached['confirm_token'],inject_at=point)
            before = fixtures.exact_snapshot(self.target)
            args = [old_source/'hv2','--source-checkout','detach','--profile','planning-1','--target',self.target,
                    '--apply','--recover','--input','-','--confirm',detached['confirm_token']]
            result = self.invoke(args,detached['request'],None)
            after = fixtures.exact_snapshot(self.target)
            observations.append({'test':self.id(),'entry':'P-source-resume-Q-detach','exit':result.returncode,
                                 'request_sha256':hashlib.sha256(canonical_json_bytes(detached['request'])).hexdigest(),
                                 'outcome':json.loads(result.stdout),'removed_paths':sorted(set(before)-set(after)),
                                 'changed_paths':sorted(n for n in set(before)&set(after) if before[n]!=after[n]),
                                 'preserved':before==after})
            self.assertNotEqual(0,result.returncode,'old P resumed a checkout-1 detach')
            self.assertEqual(before,after,'old P changed a checkout-1 detach prefix')
            recovered = workspace_detach_apply(self.target,detached['request'],confirm_token=detached['confirm_token'],recover=True)
            self.assertEqual('detached', recovered['classification'])
            self.assertEqual(2, recovered['receipt']['schema_version'])
            observations.append({'test':self.id(),'entry':'Q-source-resume-Q-detach','Q_recovered':True})

        def to_q(self, operation='to-checkout'):
            preview=workspace_switch_preview(self.target,action='update',source=new_source,operation_id=operation,created_at=self.TIME)
            before=fixtures.exact_snapshot(self.target)
            result=workspace_switch_apply(self.target,preview['request'],confirm_token=preview['confirm_token'],source=new_source)
            after=fixtures.exact_snapshot(self.target)
            kept=[n for n in before if not n.startswith('.hrn/product/') and n != 'hv2']
            self.assertEqual({n:before[n] for n in kept},{n:after[n] for n in kept})
            self.assertEqual(new_candidate['inventory'],verify_workspace_product(self.target)['inventory'])
            return preview,result

        def test_non_git_transition_and_old_packager_refusal(self):
            original=self.target;self.target=self.base/'non-git';self.target.mkdir();(self.target/'a').write_bytes(b'non-git\n')
            init=self.source_call(['init','--profile','planning-1','--target',self.target,'--source',old_source,'--authority-home-id','home-a','--operation-id','init-a','--observed-at',self.TIME])
            self.source_call(['init','--profile','planning-1','--target',self.target,'--source',old_source,'--apply','--input','-','--confirm',init['confirm_token']],init['request'])
            self.accept_intent();self.installed(['candidate','add'],candidate_fixtures.proposal(self.target,cid='non-git'))
            self.refused('P-packages-Q',lambda:self.invoke([old_source/'hv2','--source-checkout','update','--profile','planning-1','--target',self.target,'--source',new_source,'--operation-id','wrong-packager','--observed-at',self.TIME],expected=None))
            self.to_q();observations.append({'test':self.id(),'non_git_transition':True,'intent_candidate_preserved':True})
            self.target=original

        def test_no_new_records_needed_to_refuse_downgrade_and_old_retry(self):
            self.to_q();before=fixtures.exact_snapshot(self.target)
            for action,source in (('rollback',None),('update',old_source)):
                with self.assertRaises(ContractError):workspace_switch_preview(self.target,action=action,source=source,operation_id='down-'+action,created_at=self.TIME)
            self.assertEqual(before,fixtures.exact_snapshot(self.target))
            self.refused('P-init-historical-replay',lambda:self.invoke([old_source/'hv2','--source-checkout','init','--profile','planning-1','--target',self.target,'--source',old_source,'--apply','--input','-','--confirm',self.init_preview['confirm_token']],self.init_preview['request'],None))

        def pending(self, kind):
            installed_requests,source_requests=self.prepare_old_requests()
            preview=workspace_switch_preview(self.target,action='update',source=new_source,operation_id='to-checkout',created_at=self.TIME)
            if kind == 'lifecycle':
                _,args,request=next(r for r in source_requests if r[0]=='update-apply')
                token=args[args.index('--confirm')+1];source=Path(args[args.index('--source')+1])
                code="import sys,json;from pathlib import Path;sys.path.insert(0,sys.argv[1]);from hv2ref.product import workspace_switch_apply;from hv2ref.errors import InjectedCrash;p=json.load(sys.stdin);\ntry: workspace_switch_apply(Path(sys.argv[2]),p,source=Path(sys.argv[3]),confirm_token=sys.argv[4],inject_at='after-receipt')\nexcept InjectedCrash: pass"
                self.invoke([sys.executable,'-I','-B','-c',code,old_source/'src',self.target,source,token],request)
            else:
                _,args,request=next(r for r in installed_requests if r[0]==kind+'-apply')
                token=args[args.index('--confirm')+1]
                # Instrument only the documented crash point in the real installed
                # P method; launcher path, loaded payload and all guards stay real.
                module,cls,point=('work','WorkStore','after-decision') if kind=='work' else ('intent','WorkspaceIntentStore','after-acceptance')
                code="import builtins,runpy,sys;from pathlib import Path;target=Path(sys.argv[1]);kind,mod,cls,point,token=sys.argv[2:];original=builtins.__import__;patched=False\ndef hook(*a,**kw):\n global patched\n result=original(*a,**kw);m=sys.modules.get('hv2ref.'+mod)\n if not patched and m is not None and hasattr(m,cls):\n  patched=True;c=getattr(m,cls);apply=c.apply\n  def injected(self,*a,**kw):return apply(self,*a,**{**kw,'inject_at':point})\n  c.apply=injected\n return result\nbuiltins.__import__=hook;sys.argv=[str(target/'hv2'),kind,'apply','--input','-','--confirm',token];runpy.run_path(str(target/'hv2'),run_name='__main__')"
                interrupted=self.invoke([sys.executable,'-I','-B','-c',code,self.target,kind,module,cls,point,token],request,None)
                self.assertNotEqual(0,interrupted.returncode)
            before=fixtures.exact_snapshot(self.target)
            for apply in (False,True):
                with self.subTest(kind=kind,apply=apply),self.assertRaises(ContractError):
                    if apply:workspace_switch_apply(self.target,preview['request'],confirm_token=preview['confirm_token'],source=new_source)
                    else:workspace_switch_preview(self.target,action='update',source=new_source,operation_id='new-transition',created_at=self.TIME)
                self.assertEqual(before,fixtures.exact_snapshot(self.target))
            if kind=='lifecycle':self.source_call([*args,'--recover'],request)
            else:self.installed(args,request)
            self.to_q('after-pending')
            observations.append({'test':self.id(),'pending_kind':kind,'Q_refused_preview_apply':True,'P_exact_resume':True})

        def test_existing_mixed_children_worker_rebind_and_candidate_continue(self):
            import test_umbrella_lifecycle as umbrella
            from hv2ref.work import read_work,WorkStore
            from hv2ref.intent import workspace_intents
            from hv2ref.umbrella import capture
            self.serial=0
            self.q=umbrella.InstalledUmbrellaLifecycleTests.q
            self.composition={'parent':self.q('work','parent'),'required_children':[{'work':self.q('work',n),'intent':self.q('intent','intent-a')} for n in ('child-a','work-a')]}
            intent=self.accept_intent();parent_draft=self.draft();parent_draft.update(intent_id='parent-intent',schema_version=2,composition=self.composition)
            parent=umbrella.InstalledUmbrellaLifecycleTests.accept(self,parent_draft)
            (self.target/'report.md').write_bytes(b'pending\n')
            publish=umbrella.InstalledUmbrellaLifecycleTests.publish
            prepare=umbrella.InstalledUmbrellaLifecycleTests.prepare
            apply=umbrella.InstalledUmbrellaLifecycleTests.apply
            publish(self,'parent',parent,'start',parent=True)
            publish(self,'child-a',intent,'start')
            self.installed(['candidate','add'],candidate_fixtures.proposal(self.target,cid='carry'))
            self.git('add','.');self.git('commit','-qm','synthetic P worker baseline');base=self.git('rev-parse','HEAD').decode().strip()
            self.git('branch','p-base',base)
            sha=verify_workspace_product(self.target)['launcher_sha256'];tree=snapshot(self.target,verified_launcher_sha256=sha)
            identity={'record_type':'work-identity','schema_version':1,'authority_home_id':'home-a','work_id':'work-a','work_type':'change','created_at':self.TIME,'acceptance_authority':'owner','lineage':None}
            revision={'record_type':'work-revision','schema_version':1,'authority_home_id':'home-a','work_id':'work-a','record_id':'p-start','observed_at':self.TIME,'observed_scope':[],'unavailable_scope':[],'author':'agent','operation':'start','expected_prior_selection':None,'intent_ref':intent,'scope':['a'],'document_refs':[],'evidence_refs':[],'progress':'active','next_action':'review','relations':[{'relation':'parent','target':self.q('work','parent')}],'rebind_from':None,'execution_context':{'mode':'isolated-worktree','attempt_id':'attempt-a'}}
            def send(revision,manifest,worker=None):
                revision=copy.deepcopy(revision);h=hashlib.sha256(canonical_json_bytes(manifest)).hexdigest();revision['result_refs']={'manifest':{'id':h,'sha256':h}}
                rid=revision['record_id'];args=['work','publish']+(['--worker',worker] if worker else [])
                return json.loads(self.installed(args,{'identity':identity,'revision':revision,'manifest':manifest,'selection_id':'s-'+rid,'operation_id':'o-'+rid}).stdout)
            m=make_manifest(tree,tree,scope=['a'],base_commit=base,candidate_commit=base,base_retention_ref='refs/heads/p-base',candidate_retention_ref='refs/heads/p-base')
            graph=send(revision,m);worker=self.base/'p-worker';self.git('worktree','add','-q','-b','p-candidate',worker,base)
            (worker/'a').write_bytes(b'old unique worker result\n')
            def worker_git(path,*args):return subprocess.run(['git','-C',str(path),'-c','maintenance.auto=false','-c','gc.auto=0',*map(str,args)],env=git_environment(),capture_output=True,timeout=30,check=True).stdout.decode().strip()
            worker_git(worker,'add','a');worker_git(worker,'commit','-qm','synthetic P result')
            m=make_manifest(tree,snapshot(worker,verified_launcher_sha256=sha),scope=['a'],base_commit=base,candidate_commit=worker_git(worker,'rev-parse','HEAD'),base_retention_ref='refs/heads/p-base',candidate_retention_ref='refs/heads/p-candidate')
            revision.update(record_id='p-result',operation='submit-result',progress='review',expected_prior_selection=graph['current']['selection_ref']);graph=send(revision,m,worker)
            old_ticket=prepare(self,'work-a')
            old_refs=self.git('show-ref');old_worker=fixtures.exact_snapshot(worker)
            self.to_q();self.assertEqual(old_refs,self.git('show-ref'));self.assertEqual(old_worker,fixtures.exact_snapshot(worker))
            before=fixtures.exact_snapshot(self.target)
            apply(self,old_ticket,expected=65)
            request={'work_id':'work-a','action':'accept','actor':'owner','reason':'fresh old candidate','request_id':'fresh-old','observed_at':self.TIME,'revision_ref':None,'supersedes':None}
            error=json.loads(self.installed(['work','prepare'],request,expected=65).stdout)
            self.assertIn('launcher',error['message']);self.assertEqual(before,fixtures.exact_snapshot(self.target))
            publish(self,'child-a',intent,'submit-result');self.assertEqual('completed',apply(self,prepare(self,'child-a'))['state'])
            self.installed(['candidate','select'],candidate_fixtures.proposal(self.target,cid='carry',action='select'))
            self.git('add','.');self.git('commit','-qm','synthetic approved Q baseline');base=self.git('rev-parse','HEAD').decode().strip();self.git('branch','q-base',base)
            sha=verify_workspace_product(self.target)['launcher_sha256'];tree=snapshot(self.target,verified_launcher_sha256=sha)
            m=make_manifest(tree,tree,scope=['a'],base_commit=base,candidate_commit=base,base_retention_ref='refs/heads/q-base',candidate_retention_ref='refs/heads/q-base')
            revision.update(record_id='q-rebind',operation='rebind',progress='active',expected_prior_selection=graph['current']['selection_ref'],rebind_from=intent)
            graph=send(revision,m);rebind_revision=graph['revisions']['q-rebind']
            graph=apply(self,prepare(self,'work-a','rebind',rebind_revision));self.assertEqual('active',graph['state'])
            qworker=self.base/'q-worker';self.git('worktree','add','-q','-b','q-candidate',qworker,base)
            (qworker/'a').write_bytes((worker/'a').read_bytes());worker_git(qworker,'add','a');worker_git(qworker,'commit','-qm','synthetic resubmission')
            m=make_manifest(tree,snapshot(qworker,verified_launcher_sha256=sha),scope=['a'],base_commit=base,candidate_commit=worker_git(qworker,'rev-parse','HEAD'),base_retention_ref='refs/heads/q-base',candidate_retention_ref='refs/heads/q-candidate')
            revision.update(record_id='q-result',operation='submit-result',progress='review',expected_prior_selection=graph['current']['selection_ref'],rebind_from=None)
            send(revision,m,qworker);self.assertEqual('completed',apply(self,prepare(self,'work-a'))['state'])
            next_parent=copy.deepcopy(parent_draft);next_parent.update(revision_id='parent-draft-2',sequence=2,prior_revision_ref=record_ref(parent_draft,'revision_id'))
            refreshed_parent=umbrella.InstalledUmbrellaLifecycleTests.accept(self,next_parent)
            rebind,_=publish(self,'parent',refreshed_parent,'rebind',parent=True,old_intent=parent);apply(self,prepare(self,'parent','rebind',rebind))
            parent=refreshed_parent
            (self.target/'report.md').write_bytes(b'local and preserved worker results verified\n')
            publish(self,'parent',parent,'submit-result',parent=True);self.assertEqual('completed',apply(self,prepare(self,'parent'))['state'])
            self.assertEqual(b'old unique worker result\n',(self.target/'a').read_bytes())
            self.assertEqual(old_worker,fixtures.exact_snapshot(worker))
            observations.append({'test':self.id(),'P_parent_local_worker_candidate_preserved':True,'old_worker_direct_accept_refused':True,'explicit_Q_rebind_resubmit_completed':True,'parent_completed':True})

        def test_real_legacy_detach_history_and_old_recovery_remain_available(self):
            from hv2ref.product import workspace_detached_status
            detach=self.source_call(['detach','--profile','planning-1','--target',self.target,'--operation-id','legacy-detach','--observed-at',self.TIME])
            code = "import sys,json;from pathlib import Path;sys.path.insert(0,sys.argv[1]);from hv2ref.product import workspace_detach_apply;from hv2ref.errors import InjectedCrash;p=json.load(sys.stdin);\ntry: workspace_detach_apply(Path(sys.argv[2]),p,confirm_token=sys.argv[3],inject_at='after-receipt')\nexcept InjectedCrash: pass"
            self.invoke([sys.executable,'-I','-B','-c',code,old_source/'src',self.target,detach['confirm_token']],detach['request'])
            before=fixtures.exact_snapshot(self.target)
            observed=workspace_detached_status(self.target);self.assertEqual(1,observed['receipt']['schema_version'])
            with self.assertRaisesRegex(ContractError,'legacy detach writes'):
                workspace_detach_apply(self.target,detach['request'],confirm_token=detach['confirm_token'],recover=True)
            self.assertEqual(before,fixtures.exact_snapshot(self.target))
            result=self.source_call(['detach','--profile','planning-1','--target',self.target,'--apply','--recover','--input','-','--confirm',detach['confirm_token']],detach['request'])
            self.assertEqual('detached',result['classification'])
            self.assertEqual('detached',workspace_detached_status(self.target)['classification'])
            audit=self.invoke([sys.executable,'-I','-B',new_source/'tests/fixtures/product_plain_auditor.py',self.target])
            self.assertEqual('detached',json.loads(audit.stdout)['classification'])
            observations.append({'test':self.id(),'exact_P_legacy_recovered':True,'Q_read_only':True,'plain_auditor':True})

        def test_detach_does_not_allow_old_reinstallation(self):
            preview = workspace_switch_preview(self.target,action='update',source=new_source,operation_id='to-checkout',created_at=self.TIME)
            workspace_switch_apply(self.target,preview['request'],confirm_token=preview['confirm_token'],source=new_source)
            detached = workspace_detach_preview(self.target,operation_id='detach-q',created_at=self.TIME)
            workspace_detach_apply(self.target,detached['request'],confirm_token=detached['confirm_token'])
            self.assertTrue((self.target/'.hrn/detached.json').is_file())
            self.assertFalse((self.target/'.hrn/product').exists())
            self.refused('P-init-preview-after-detach',lambda:self.invoke([old_source/'hv2','--source-checkout','init','--profile','planning-1','--target',self.target,'--source',old_source,'--authority-home-id','home-b','--operation-id','new-init','--observed-at',self.TIME],expected=None))
            for recover in (False,True):
                args=[old_source/'hv2','--source-checkout','init','--profile','planning-1','--target',self.target,'--source',old_source,'--apply','--input','-','--confirm',self.init_preview['confirm_token']]
                if recover:args.append('--recover')
                self.refused('P-old-init-apply-recover-'+str(recover),lambda a=args:self.invoke(a,self.init_preview['request'],None))
            self.refused('P-unsupported-attach',lambda:self.invoke([old_source/'hv2','--source-checkout','attach','--target',self.target],expected=None))

    for kind in ('work','intent','lifecycle'):
        def test(self, kind=kind): self.pending(kind)
        setattr(ExactCheckoutTransitionTests,'test_P_pending_'+kind+'_blocks_Q_transition',test)

    for point in ('after-receipt','after-launcher','after-file','after-files','after-directory','after-product'):
        def test(self, point=point): self.detach_prefix(point)
        name = 'test_old_source_cannot_resume_new_window_detach' if point == 'after-receipt' else 'test_detach_prefix_'+point.replace('-','_')
        setattr(ExactCheckoutTransitionTests,name,test)

    for point in PREFIXES:
        def test(self, point=point): self.prefix(point)
        setattr(ExactCheckoutTransitionTests,'test_prefix_'+point.replace('-','_'),test)
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(ExactCheckoutTransitionTests)
    if suite.countTestCases() != 20:
        raise AssertionError('exact artifact collection differs')
    return suite, observations
