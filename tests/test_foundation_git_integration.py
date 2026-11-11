import unittest,base64
from unittest.mock import patch
from colvia.codec import RecordError
from colvia.effects import PENDING
from colvia.git_integration import GitIntegration
from colvia.platforms.darwin_git import DarwinGit
from test_foundation_work_git import GitWorkFixture
from test_foundation_git_candidate import AUTHOR

class IntegrationFixture(GitWorkFixture):
    def setUp(self):
        super().setUp();self.scratch=self.home/'integration';self.scratch.mkdir(mode=0o700)
        self.port=DarwinGit(self.root,self.scratch,self.git)
        self.integration=GitIntegration(self.store,self.service.workspace,self.port)
    def accepted(self):
        self.start();(self.root/'report.md').write_bytes(b'reviewed result\n');review=self.submit()
        self.service.accept(operation='accept',work='report',receipt=review['receipt'],statement='수락')
    def prepare(self):
        self.accepted();return self.integration.prepare(operation='integrate',works=['report'],message='Synthetic accepted result',identity=AUTHOR)

class IntegrationTests(IntegrationFixture,unittest.TestCase):
    def test_acceptance_is_separate_one_git_approval(self):
        old=self.command('rev-parse','HEAD');preview=self.prepare()
        self.assertEqual(old,self.command('rev-parse','HEAD'));self.assertIsNone(self.store.head(PENDING))
        self.assertIn(b'reviewed result',base64.b64decode(preview['diff_base64']))
        result=self.integration.apply('integrate',receipt=preview['receipt'],statement='이 변경만 기록')
        self.assertEqual('completed',result['state']);self.assertIsNone(self.store.head(PENDING))
        self.assertEqual('completed',self.service.view('report')['state'])
        self.assertEqual(result,self.integration.recover('integrate',statement='확인'))
    def test_before_lock_crash_has_no_foreign_effect_and_can_close_not_applied(self):
        preview=self.prepare()
        def fail(phase):
            if phase=='lock-intent':raise RuntimeError('synthetic interruption')
        with self.assertRaisesRegex(RuntimeError,'synthetic'):
            self.integration.apply('integrate',receipt=preview['receipt'],statement='기록',event=fail)
        self.assertIsNotNone(self.store.head(PENDING))
        self.assertEqual('not-applied',self.integration.recover('integrate',statement='반영 안 됨 확인')['state'])
        self.assertIsNone(self.store.head(PENDING))
    def test_ref_then_crash_recovery_preserves_index_staging(self):
        (self.root/'other').write_bytes(b'keep staged');self.command('add','other')
        preview=self.prepare();old=(self.root/'.git/index').read_bytes()
        def fail(phase):
            if phase=='ref-observed':raise RuntimeError('synthetic interruption')
        with self.assertRaisesRegex(RuntimeError,'synthetic'):
            self.integration.apply('integrate',receipt=preview['receipt'],statement='기록',event=fail)
        self.assertEqual(old,(self.root/'.git/index').read_bytes());self.assertIsNotNone(self.store.head(PENDING))
        with self.assertRaisesRegex(RecordError,'external-effect-pending'):
            self.service.plan(operation='blocked',work='blocked',title='다음',goal='추가',scope=['new'],checks=['확인'])
        self.assertEqual('completed',self.integration.recover('integrate',statement='중단한 반영 완료')['state'])
        self.assertEqual(b'other\n',self.command('diff','--cached','--name-only'))
    def test_index_completed_before_authority_can_be_recorded_once(self):
        preview=self.prepare()
        def fail(phase):
            if phase=='index-replaced':raise RuntimeError('synthetic interruption')
        with self.assertRaises(RuntimeError):self.integration.apply('integrate',receipt=preview['receipt'],statement='기록',event=fail)
        head=self.command('rev-parse','HEAD');self.assertEqual('completed',self.integration.recover('integrate',statement='반영 확인')['state'])
        self.assertEqual(head,self.command('rev-parse','HEAD'))
    def test_platform_identity_scheme_does_not_bypass_lock_ownership(self):
        preview=self.prepare()
        def fail(phase):
            if phase=='locked':raise RuntimeError('synthetic stop')
        with self.assertRaises(RuntimeError):self.integration.apply('integrate',receipt=preview['receipt'],statement='기록',event=fail)
        _,state,plan=self.integration._state('integrate');owner=dict(state.payload['owner'])
        self.assertEqual('macos-inode-v1',owner['native']['scheme'])
        owner['native']=dict(scheme='windows-file-id-v1',value=owner['native']['value'])
        with self.assertRaisesRegex(RecordError,'lock-not-owned'):self.port.owned_lock(plan.payload['manifest'],owner)
        self.assertTrue((self.root/'.git/index.lock').exists())

    def test_unowned_lock_after_creation_intent_is_never_deleted(self):
        preview=self.prepare()
        original=self.port.acquire_index
        def unrecorded(manifest):
            original(manifest)
            raise RuntimeError('synthetic interruption before ownership record')
        with patch.object(self.port,'acquire_index',side_effect=unrecorded),self.assertRaises(RuntimeError):
            self.integration.apply('integrate',receipt=preview['receipt'],statement='기록')
        lock=self.root/'.git/index.lock';inode=lock.stat().st_ino
        with self.assertRaisesRegex(RecordError,'lock-unrecorded'):self.integration.recover('integrate',statement='확인')
        self.assertEqual(inode,lock.stat().st_ino);self.assertIsNotNone(self.store.head(PENDING))
    def test_stale_receipt_or_changed_file_does_not_reserve(self):
        preview=self.prepare()
        with self.assertRaisesRegex(RecordError,'review-changed'):self.integration.apply('integrate',receipt='wrong',statement='기록')
        (self.root/'report.md').write_text('changed')
        with self.assertRaisesRegex(RecordError,'context-changed'):self.integration.apply('integrate',receipt=preview['receipt'],statement='기록')
        self.assertIsNone(self.store.head(PENDING))

if __name__=='__main__':unittest.main()
