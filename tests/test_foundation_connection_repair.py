"""Synthetic connection repair; no installed bootstrap, OS grant or real key."""
import tempfile,unittest,json,hashlib
from pathlib import Path
from unittest.mock import patch
from colvia.codec import RecordError,canonical_bytes
from colvia.effects import PENDING
from colvia.storage.sqlite import runtime_capabilities
from colvia.updates.connection_repair import ConnectionRepair
from test_foundation_project_setup import SetupFixture
import test_foundation_slots as slot_fixture

class TrustDouble:
    def __init__(self):self.expired=False
    def activation_check(self,download):
        if self.expired and not download.get('renewed'):raise RecordError('update-preparation-expired')

class RepairTests(SetupFixture,unittest.TestCase):
    slot=slot_fixture.SlotTests.slot
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(prefix='connect-repair-');self.base=Path(self.tmp.name)
        self.root=self.base/'project';self.root.mkdir();(self.root/'AGENTS.md').write_bytes(b'User rules\n')
        self.manager_fixture(self.base);self.home=self.manager;self.manager=self.home.slots
        caps=tuple(x for x in runtime_capabilities() if x!='foundation-v1')
        self.one=self.slot('one',1,extra=caps);self.two=self.slot('two',2,extra=caps);self.manager.initialize(self.one)
        self.begin();self.trust=TrustDouble();slot=self.manager.verify(self.two)
        self.release=dict(operation='signed-release',target=self.two,channel='preview',download=dict(path='bundle.zip',length=1,sha256='1'*64,custom={'colvia':dict(version=1,channel='preview',os='macos',architecture='arm64',
                 release=slot.release,sequence=slot.sequence,manifest_sha256=slot.manifest_sha256)}))
        self.repair=ConnectionRepair(self.home,self.trust,slot,self.release,connection='connect')
        self.selection=self.manager.selection()[0]
        self.home.files.create_directory(self.home.root/'operations/signed-release')
    def tearDown(self):self.tmp.cleanup()
    def review(self):return self.repair.preview()['receipt']
    def apply(self,**kw):return self.repair.apply(operation='r',receipt=self.review(),**kw)
    def test_completes_original_manifest_preserves_rules_and_selection(self):
        authority=self.home.authority(self.preview['plan']['project']);store=authority.store(readonly=True)
        try:before=store.head('connect:connect')
        finally:store.close()
        result=self.apply();self.assertEqual('connected',result['state']);self.assertEqual(self.selection,self.manager.selection()[0])
        self.assertTrue((self.home.root/'operations/r/b.colvia-export').is_file())
        self.assertEqual(b'User rules\n',(self.home.root/'operations/r/o0').read_bytes())
        store=authority.store(readonly=True)
        try:self.assertIsNone(store.head(PENDING));self.assertIsNotNone(store.load(before))
        finally:store.close()
        self.assertTrue((self.root/'AGENTS.md').read_bytes().startswith(b'User rules\n'))
        self.assertTrue(self.home.requirements())
    def test_overlap_refuses_repair_before_snapshots_or_effects(self):
        child = self.root / 'child'
        child.mkdir()
        with patch('colvia.project_setup.check_connection_boundary'):
            p = self.setup.preview(child)
            self.setup.start(operation='older-child', plan=p['plan'], receipt=p['receipt'], statement='Synthetic connection')
            for _ in p['plan']['changes']:
                self.setup.resume('older-child')
        locator = (child / '.colvia-link.json').read_bytes()
        with self.assertRaisesRegex(RecordError, 'connect-resume-project-overlap'):
            self.repair.preview()
        self.assertEqual(b'User rules\n', (self.root / 'AGENTS.md').read_bytes())
        self.assertFalse((self.root / 'CLAUDE.md').exists())
        self.assertEqual(locator, (child / '.colvia-link.json').read_bytes())

    def test_disjoint_git_project_does_not_block_connection_repair(self):
        from colvia.updates.connection_repair import _RepairGit
        from colvia.project_setup import ProjectSetup
        from test_foundation_git import GitTests

        fixture = GitTests()
        fixture.setUp()
        self.addCleanup(fixture.tearDown)
        setup = ProjectSetup(self.home, fixture.git)
        preview = setup.preview(fixture.root)
        setup.start(operation='git-project', plan=preview['plan'], receipt=preview['receipt'],
                    statement='Synthetic independent Git project')
        for _ in preview['plan']['changes']:
            result = setup.resume('git-project')
        self.assertEqual('connected', result['state'])
        git = fixture.git
        self.home.files.create(self.home.root / 'tools.json', canonical_bytes({
            'version': 1, 'git': {'path': str(git.executable), 'sha256': git.sha256, 'version': git.version},
        }))
        with self.assertRaisesRegex(RecordError, 'connect-boundary-unavailable'):
            self.repair.preview()
        repair = ConnectionRepair(self.home, self.trust, self.manager.verify(self.two), self.release,
                                  connection='connect', git=_RepairGit(self.home))
        receipt = repair.preview()['receipt']
        self.assertEqual('connected', repair.apply(operation='r', receipt=receipt)['state'])
        self.assertEqual(self.selection, self.manager.selection()[0])

    def test_plain_repair_ignores_an_unused_stale_git_registration(self):
        from colvia.updates.connection_repair import _RepairGit

        self.home.files.create(self.home.root / 'tools.json', canonical_bytes({
            'version': 1, 'git': {'path': str(self.base / 'missing-git'), 'sha256': '0' * 64, 'version': 'old'},
        }))
        repair = ConnectionRepair(self.home, self.trust, self.manager.verify(self.two), self.release,
                                  connection='connect', git=_RepairGit(self.home))
        receipt = repair.preview()['receipt']
        self.assertEqual('connected', repair.apply(operation='r', receipt=receipt)['state'])
        self.assertEqual(self.selection, self.manager.selection()[0])

    def test_wrong_receipt_refuses_before_snapshot_or_effect(self):
        with self.assertRaisesRegex(RecordError,'review-changed'):self.repair.apply(operation='r',receipt='0'*64)
        self.assertFalse((self.home.root/'operations/r').exists());self.assertFalse((self.root/'CLAUDE.md').exists())
    def test_signature_expiry_and_different_signed_code_refuse(self):
        self.trust.expired=True
        with self.assertRaisesRegex(RecordError,'expired'):self.review()
        self.trust.expired=False;self.release['download']['custom']['colvia']['manifest_sha256']='0'*64
        with self.assertRaisesRegex(RecordError,'code-target'):self.review()
        self.assertFalse((self.root/'CLAUDE.md').exists())
    def test_second_pending_connection_refuses_without_effects(self):
        other=self.base/'other';other.mkdir();p=self.setup.preview(other)
        self.setup.start(operation='other',plan=p['plan'],receipt=p['receipt'],statement='Synthetic separate approval')
        with self.assertRaisesRegex(RecordError,'other-pending'):self.review()
        self.assertFalse((self.root/'CLAUDE.md').exists())
    def test_initial_partial_connection_refuses_but_original_resume_still_exists(self):
        self.setup.resume('connect')
        with self.assertRaisesRegex(RecordError,'requires-unapplied'):self.review()
    def test_interruption_after_effect_then_old_runtime_progress_can_resume_exact_chain(self):
        receipt=self.review()
        def stop(phase):
            if phase=='applied':raise RuntimeError('injected after native effect')
        with self.assertRaisesRegex(RuntimeError,'injected'):self.repair.apply(operation='r',receipt=receipt,event=stop)
        self.assertEqual(self.selection,self.manager.selection()[0]);self.setup.resume('connect')
        result=self.repair.apply(operation='r',receipt=receipt,resume=True)
        self.assertEqual('connected',result['state']);self.assertEqual(self.selection,self.manager.selection()[0])
    def test_existing_user_file_evacuated_window_resumes_without_overwrite(self):
        receipt=self.review()
        def stop(phase):
            if phase=='after-evacuate':raise RuntimeError('evacuated window')
        with self.assertRaisesRegex(RuntimeError,'evacuated'):self.repair.apply(operation='r',receipt=receipt,event=stop)
        self.assertFalse((self.root/'AGENTS.md').exists())
        result=self.repair.apply(operation='r',receipt=receipt,resume=True)
        self.assertEqual('connected',result['state']);self.assertTrue((self.root/'AGENTS.md').read_bytes().startswith(b'User rules\n'))
    def test_changed_file_refuses_and_original_update_guard_remains(self):
        receipt=self.review();(self.root/'CLAUDE.md').write_bytes(b'External user change')
        with self.assertRaises(RecordError):self.repair.apply(operation='r',receipt=receipt)
        self.assertEqual(b'External user change',(self.root/'CLAUDE.md').read_bytes())
        with self.assertRaisesRegex(RecordError,'effect-pending'):self.home.requirements()
    def test_changed_journal_cannot_redirect_original_manifest(self):
        path=self.home.root/'operations/connect/connect.json';raw=json.loads(path.read_bytes())
        raw['plan']['changes'][0]['after']='d3Jvbmc='
        raw['receipt']=hashlib.sha256(canonical_bytes(raw['plan'])).hexdigest();path.write_bytes(canonical_bytes(raw))
        with self.assertRaisesRegex(RecordError,'journal-body'):self.review()
    def test_failed_backup_does_not_apply_any_file(self):
        receipt=self.review()
        with patch('colvia.updates.connection_repair.export_backup',side_effect=OSError('snapshot unavailable')):
            with self.assertRaisesRegex(OSError,'snapshot'):self.repair.apply(operation='r',receipt=receipt)
        self.assertFalse((self.root/'CLAUDE.md').exists());self.assertFalse((self.home.root/'operations/r/prepared.json').exists())
    def test_changed_snapshot_refuses_resume(self):
        receipt=self.review()
        def stop(phase):
            if phase=='prepared':raise RuntimeError('before first effect')
        with self.assertRaises(RuntimeError):self.repair.apply(operation='r',receipt=receipt,event=stop)
        (self.home.root/'operations/r/s0').write_bytes(b'changed')
        with self.assertRaisesRegex(RecordError,'snapshot-mismatch'):self.repair.apply(operation='r',receipt=receipt,resume=True)
        self.assertFalse((self.root/'CLAUDE.md').exists())
    def test_modified_logical_backup_refuses_resume(self):
        receipt=self.review()
        def stop(phase):
            if phase=='prepared':raise RuntimeError('before effect')
        with self.assertRaises(RuntimeError):self.repair.apply(operation='r',receipt=receipt,event=stop)
        p=self.home.root/'operations/r/b.colvia-export';raw=p.read_bytes();p.write_bytes(bytes([raw[0]^1])+raw[1:])
        with self.assertRaisesRegex(RecordError,'backup-mismatch'):self.repair.apply(operation='r',receipt=receipt,resume=True)
        self.assertFalse((self.root/'CLAUDE.md').exists())

    def test_exclusive_runtime_lock_is_held_during_effect(self):
        receipt=self.review();seen=[]
        def check(phase):
            if phase=='prepared':
                with self.assertRaises((RecordError,TimeoutError)):
                    with self.home.files.exclusion(self.manager.root/'runtime.lock',timeout=0.02,shared=True):pass
                seen.append(phase)
        self.repair.apply(operation='r',receipt=receipt,event=check)
        self.assertEqual(['prepared'],seen)

    def test_changed_selection_between_preview_and_apply_refuses(self):
        receipt=self.review();raw,_=self.manager.selection()
        self.manager.activate(self.two,expected_selection=raw,read_requirements=[])
        with self.assertRaisesRegex(RecordError,'review-changed'):
            self.repair.apply(operation='r',receipt=receipt)
        self.assertFalse((self.root/'CLAUDE.md').exists())

    def test_changed_prepared_payload_refuses_before_effect(self):
        receipt=self.review();(self.manager.root/'slots/two/product.py').write_bytes(b'changed')
        with self.assertRaisesRegex(RecordError,'slot-inventory-mismatch'):
            self.repair.apply(operation='r',receipt=receipt)
        self.assertFalse((self.root/'CLAUDE.md').exists())

    def test_selected_runtime_must_understand_repair_records(self):
        from dataclasses import replace
        original=self.manager.verify
        def verify(value):
            result=original(value)
            return replace(result,write_capabilities=frozenset()) if value==self.one else result
        with patch.object(self.manager,'verify',side_effect=verify):
            with self.assertRaisesRegex(RecordError,'capability-unavailable'):self.review()
        self.assertFalse((self.root/'CLAUDE.md').exists())

    def test_expiry_after_evacuation_requires_exact_existing_metadata_renewal(self):
        from colvia.updates.reauthentication import renew
        receipt=self.review()
        def expire(phase):
            if phase=='after-evacuate':self.trust.expired=True
        with self.assertRaisesRegex(RecordError,'expired'):
            self.repair.apply(operation='n',receipt=receipt,event=expire)
        with self.assertRaisesRegex(RecordError,'expired'):
            self.repair.apply(operation='n',receipt=receipt,resume=True)
        original=hashlib.sha256(canonical_bytes(self.release)).hexdigest()
        def stage(path,**kwargs):
            fresh=dict(self.release['download'],renewed=True,staged=None)
            self.assertTrue(kwargs['already_present'](fresh));return fresh
        self.trust.stage=stage
        renewed=renew(self.home,self.trust,operation='signed-release',original=original,
                      download=self.release['download'],renewal='fresh')
        self.repair.renewal=renewed['renewal']
        result=self.repair.apply(operation='n',receipt=receipt,resume=True)
        self.assertEqual('connected',result['state'])
        self.assertTrue((self.root/'AGENTS.md').read_bytes().startswith(b'User rules'))
        a=self.home.authority(self.preview['plan']['project'])
        self.assertEqual('n',json.loads((a.root/'last-export.json').read_bytes())['operation'])

    def test_failed_snapshot_can_use_new_explicit_operation_without_effect_replay(self):
        receipt=self.review()
        with patch('colvia.updates.connection_repair.export_backup',side_effect=OSError('backup')):
            with self.assertRaises(OSError):self.repair.apply(operation='first',receipt=receipt)
        self.assertFalse((self.root/'CLAUDE.md').exists())
        self.assertEqual('connected',self.repair.apply(operation='second',receipt=receipt)['state'])
        self.assertTrue((self.home.root/'operations/first/connection-repair.json').is_file())

    def test_completed_reinspection_does_not_apply_again(self):
        receipt=self.review();self.repair.apply(operation='r',receipt=receipt)
        with patch.object(self.repair.setup,'_resume_locked',side_effect=AssertionError('no replay')):
            self.assertEqual('connected',self.repair.apply(operation='r',receipt=receipt,resume=True)['state'])

class DispatcherTests(unittest.TestCase):
    def test_exact_bootstrap_mode_cannot_fall_through_or_accept_install_flags(self):
        from colvia.manager_entry import main
        args=['bootstrap-connect-repair-preview','--management-root','/synthetic/home','--bootstrap-stage','/synthetic/stage',
              '--bootstrap-manifest-sha256','0'*64,'--connection','connect','--release-operation','k']
        with patch('colvia.updates.connection_repair.bootstrap_connection_repair',return_value={'state':'synthetic-preview'}) as repair,patch('colvia.updates.installation.bootstrap',side_effect=AssertionError('no ordinary fallback')):
            self.assertEqual(0,main(args));self.assertFalse(repair.call_args.kwargs['prepare'])
        with self.assertRaises(SystemExit):main(args+['--repair-operation','unrelated'])

if __name__=='__main__':unittest.main()
