"""Windows Git protocol composition on macOS with explicit native API doubles.

Real synthetic Git subprocesses use the already-tested Darwin child port. These
checks exercise common authority/ref/index sequencing, not Windows APIs or Jobs.
"""
import os,unittest
from unittest.mock import patch
from colvia.codec import RecordError
from colvia.effects import PENDING
from colvia.git_integration import GitIntegration
from colvia.platforms.windows_git import WindowsGit
from colvia.platforms.windows_observation import Observer
from colvia.platforms.git_child import GitChild
from test_foundation_git_integration import IntegrationFixture
from test_foundation_windows_effects import Files,Move

class WindowsGitCompositionTests(IntegrationFixture,unittest.TestCase):
    def setUp(self):
        super().setUp();self.files=Files();self.mover=Move(self.files.api)
        self.port=WindowsGit(self.root,self.scratch,self.git,files=self.files,observer=Observer(files=self.files),
            mover=self.mover,children=GitChild(self.scratch/'children'),birth=lambda pid:'synthetic-owner' if pid==os.getpid() else None)
        self.integration=GitIntegration(self.store,self.service.workspace,self.port)
    def test_gate_move_guard_never_reopens_delete_locked_source(self):
        preview=self.prepare();original=self.mover.move
        def sharing_checked(source,destination,**kw):
            if source.name=='index.lock':
                guard=kw['before_effect'];read=self.port.observer.read_file;identity=self.port.file_id
                def no_source_read(path,*a,**k):
                    if path==source:raise AssertionError('DELETE-held source reopened by guard')
                    return read(path,*a,**k)
                def no_source_identity(path):
                    if path==source:raise AssertionError('DELETE-held source reopened for identity')
                    return identity(path)
                def checked():
                    with patch.object(self.port.observer,'read_file',side_effect=no_source_read),patch.object(self.port,'file_id',side_effect=no_source_identity):guard()
                kw['before_effect']=checked
            return original(source,destination,**kw)
        with patch.object(self.mover,'move',side_effect=sharing_checked):
            self.assertEqual('completed',self.integration.apply('integrate',receipt=preview['receipt'],statement='기록')['state'])
    def test_exact_commit_preserves_unselected_staging_and_retained_original(self):
        (self.root/'other').write_bytes(b'keep staged');self.command('add','other');preview=self.prepare()
        original=(self.root/'.git/index').read_bytes()
        result=self.integration.apply('integrate',receipt=preview['receipt'],statement='이 변경만 기록')
        self.assertEqual('completed',result['state']);self.assertIsNone(self.store.head(PENDING))
        self.assertEqual(original,(self.scratch/'integrate/index-original').read_bytes())
        self.assertEqual(b'other\n',self.command('diff','--cached','--name-only'));self.assertFalse((self.root/'.git/index.lock').exists())
        self.assertTrue((self.scratch/'integrate/index-lock-completed').exists())
    def test_evacuated_index_resumes_only_exact_prepared_transition(self):
        preview=self.prepare();original=(self.root/'.git/index').read_bytes();move=self.mover.move;crashed=False
        def interrupted(*args,**kw):
            nonlocal crashed
            move(*args,**kw)
            if not crashed:crashed=True;raise RuntimeError('synthetic crash after original move')
        with patch.object(self.mover,'move',side_effect=interrupted),self.assertRaises(RuntimeError):
            self.integration.apply('integrate',receipt=preview['receipt'],statement='기록')
        self.assertFalse((self.root/'.git/index').exists());self.assertTrue((self.root/'.git/index.lock').exists())
        self.assertEqual(original,(self.scratch/'integrate/index-original').read_bytes())
        self.assertIsNotNone(self.store.head(PENDING))
        self.assertEqual('completed',self.integration.recover('integrate',statement='중단 반영 완료')['state'])
        self.assertFalse((self.root/'.git/index.lock').exists());self.assertIsNone(self.store.head(PENDING))
    def test_completed_index_keeps_gate_until_recovery_finishes(self):
        preview=self.prepare()
        def interrupted(phase):
            if phase=='index-replaced':raise RuntimeError('synthetic crash before gate close')
        with self.assertRaises(RuntimeError):self.integration.apply('integrate',receipt=preview['receipt'],statement='기록',event=interrupted)
        self.assertTrue((self.root/'.git/index.lock').exists());head=self.command('rev-parse','HEAD')
        self.assertEqual('completed',self.integration.recover('integrate',statement='완료 확인')['state'])
        self.assertEqual(head,self.command('rev-parse','HEAD'));self.assertFalse((self.root/'.git/index.lock').exists())
    def test_gate_moved_before_completion_ack_can_finish_without_new_effect(self):
        preview=self.prepare();finalize=self.port.finalize_index
        def interrupted(*args,**kw):finalize(*args,**kw);raise RuntimeError('synthetic lost completion')
        with patch.object(self.port,'finalize_index',side_effect=interrupted),self.assertRaises(RuntimeError):
            self.integration.apply('integrate',receipt=preview['receipt'],statement='기록')
        self.assertFalse((self.root/'.git/index.lock').exists());count=self.mover.count
        self.assertEqual('completed',self.integration.recover('integrate',statement='반영 완료 확인')['state'])
        self.assertEqual(count,self.mover.count)

    def test_nonexecutable_hook_is_not_assumed_inactive_on_windows(self):
        self.accepted();hook=self.root/'.git/hooks/pre-commit';hook.write_text('synthetic hook never executed');hook.chmod(0o600)
        from test_foundation_git_candidate import AUTHOR
        with self.assertRaisesRegex(RecordError,'hooks-require-manual'):
            self.integration.prepare(operation='integrate',works=['report'],message='synthetic',identity=AUTHOR)
        self.assertIsNone(self.store.head(PENDING));self.assertFalse((self.root/'.git/index.lock').exists())

if __name__=='__main__':unittest.main()
