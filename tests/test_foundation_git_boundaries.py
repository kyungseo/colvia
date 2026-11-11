import base64,unittest
from unittest.mock import patch
from colvia.codec import RecordError
from colvia.effects import PENDING
from colvia.cli import parser,dispatch
from colvia.presentation import human
from test_foundation_git_integration import IntegrationFixture
from test_foundation_git_candidate import CandidateFixture,AUTHOR

class Boundaries(IntegrationFixture,unittest.TestCase):
    def test_source_cli_and_human_output_keep_separate_git_decision(self):
        self.accepted()
        prefix=['--source-development','--authority',str(self.home),'--project',self.store.project,
                '--workspace',self.service.workspace.workspace,'--root',str(self.root),'--git',str(self.git.executable)]
        args=parser().parse_args(prefix+['git-integration','prepare','integrate','--scratch',str(self.scratch),'--work','report',
            '--message','Synthetic record','--author-name',AUTHOR['name'],'--author-email',AUTHOR['email'],'--author-date',AUTHOR['date']])
        preview=dispatch(args,self.store,self.service.workspace);shown=human(preview)
        self.assertIn('이 변경만 Git에 기록할까요',shown);self.assertIn('reviewed result',shown)
        self.assertNotIn('receipt',shown);self.assertNotIn(str(self.home),shown)
    def test_foreign_index_lock_replacement_during_recovery_is_preserved(self):
        preview=self.prepare()
        def fail(phase):
            if phase=='ref-observed':raise RuntimeError('synthetic')
        with self.assertRaises(RuntimeError):self.integration.apply('integrate',receipt=preview['receipt'],statement='기록',event=fail)
        lock=self.root/'.git/index.lock';lock.rename(self.scratch/'retained-lock');lock.write_bytes(b'foreign')
        with self.assertRaisesRegex(RecordError,'lock-not-owned'):self.integration.recover('integrate',statement='확인')
        self.assertEqual(b'foreign',lock.read_bytes());self.assertIsNotNone(self.store.head(PENDING))
    def test_ref_child_lock_is_never_removed(self):
        preview=self.prepare()
        def fail(phase):
            if phase=='ref-observed':raise RuntimeError('synthetic')
        with self.assertRaises(RuntimeError):self.integration.apply('integrate',receipt=preview['receipt'],statement='기록',event=fail)
        lock=self.root/'.git/packed-refs.lock';lock.write_bytes(b'foreign')
        with self.assertRaisesRegex(RecordError,'child-lock-present'):self.integration.recover('integrate',statement='확인')
        self.assertEqual(b'foreign',lock.read_bytes())
    def test_another_live_owner_blocks_recovery(self):
        preview=self.prepare()
        def fail(phase):
            if phase=='ref-observed':raise RuntimeError('synthetic')
        with self.assertRaises(RuntimeError):self.integration.apply('integrate',receipt=preview['receipt'],statement='기록',event=fail)
        with patch('colvia.platforms.darwin_git.os.getpid',return_value=123),self.assertRaisesRegex(RecordError,'owner-still-live'):
            self.integration.recover('integrate',statement='확인')
    def test_old_ref_and_new_index_are_not_automatic_success(self):
        preview=self.prepare()
        def fail(phase):
            if phase=='index-replaced':raise RuntimeError('synthetic')
        with self.assertRaises(RuntimeError):self.integration.apply('integrate',receipt=preview['receipt'],statement='기록',event=fail)
        self.command('update-ref',preview['branch'],preview['parent'],preview['commit'])
        with self.assertRaisesRegex(RecordError,'external-divergence'):self.integration.recover('integrate',statement='확인')
        self.assertIsNotNone(self.store.head(PENDING))

class RecoveryCorrections(IntegrationFixture,unittest.TestCase):
    def interrupted(self,phase):
        preview=self.prepare()
        def fail(current):
            if current==phase:raise RuntimeError('synthetic interruption')
        with self.assertRaises(RuntimeError):
            self.integration.apply('integrate',receipt=preview['receipt'],statement='기록',event=fail)
        return preview
    def test_edit_after_ref_does_not_wedge_or_overwrite_worktree(self):
        self.interrupted('ref-observed')
        (self.root/'report.md').write_bytes(b'later human edit\n')
        result=self.integration.recover('integrate',statement='중단 반영 확인')
        self.assertEqual('completed',result['state'])
        self.assertEqual(b'later human edit\n',(self.root/'report.md').read_bytes())
        self.assertEqual(b'reviewed result\n',self.command('show','HEAD:report.md'))
        self.assertEqual(b'report.md\n',self.command('diff','--name-only'))
        self.assertIsNone(self.store.head(PENDING))
    def test_edit_before_ref_can_close_without_applying(self):
        preview=self.interrupted('locked')
        (self.root/'report.md').write_bytes(b'later human edit\n')
        result=self.integration.recover('integrate',statement='미반영 확인')
        self.assertEqual('not-applied',result['state'])
        self.assertEqual(preview['parent'],self.command('rev-parse','HEAD').decode().strip())
        self.assertEqual(b'later human edit\n',(self.root/'report.md').read_bytes())
        self.assertFalse((self.root/'.git/index.lock').exists())
    def test_absent_owned_lock_after_ref_can_be_reacquired(self):
        self.interrupted('ref-observed');(self.root/'.git/index.lock').unlink()
        self.assertEqual('completed',self.integration.recover('integrate',statement='확인')['state'])
    def test_replaced_equal_index_refuses_recovery(self):
        self.interrupted('ref-observed');index=self.root/'.git/index';raw=index.read_bytes()
        index.rename(self.scratch/'retained-index');index.write_bytes(raw)
        with self.assertRaisesRegex(RecordError,'external-divergence'):
            self.integration.recover('integrate',statement='확인')
        self.assertIsNotNone(self.store.head(PENDING))
    def test_missing_candidate_blob_refuses_before_ref_write(self):
        preview=self.prepare();oid=self.command('rev-parse',preview['commit']+':report.md').decode().strip()
        path=self.root/'.git/objects'/oid[:2]/oid[2:];path.rename(self.scratch/'retained-object')
        with self.assertRaises(RecordError):self.integration.apply('integrate',receipt=preview['receipt'],statement='기록')
        self.assertEqual(preview['parent'],self.command('rev-parse','HEAD').decode().strip())
        self.assertIsNone(self.store.head(PENDING))
    def test_final_index_preserves_original_mode(self):
        (self.root/'.git/index').chmod(0o640);preview=self.prepare()
        self.integration.apply('integrate',receipt=preview['receipt'],statement='기록')
        self.assertEqual(0o640,(self.root/'.git/index').stat().st_mode&0o777)

class Admission(CandidateFixture,unittest.TestCase):
    def test_merge_state_refuses(self):
        (self.root/'.git/MERGE_HEAD').write_bytes(b'pending')
        with self.port.exclusion(),self.assertRaisesRegex(RecordError,'operation-in-progress'):self.prepare()
    def test_symlink_unrelated_remains_in_tree(self):
        (self.root/'link').symlink_to('report.md');self.command('add','link');self.command('commit','-qm','Synthetic link')
        with self.port.exclusion():m=self.prepare()
        self.assertEqual(b'report.md',self.command('show',m['new']+':link'))
    def test_delete_and_executable_mode(self):
        data=b'#!/bin/sh\nexit 0\n';(self.root/'script').write_bytes(data);(self.root/'script').chmod(0o755)
        changes,body=self.changes();(self.root/'report.md').unlink()
        import hashlib
        changes={'report.md':None,'script':dict(path='script',kind='regular',mode='100755',size=len(data),sha256=hashlib.sha256(data).hexdigest())}
        with self.port.exclusion():
            m=self.port.prepare('modes',changes,lambda _:iter([data]),message='Synthetic delete and mode',identity=AUTHOR)
            owner=self.port.acquire_index(m);self.port.update_ref(m,owner,live=lambda:None,event=lambda *_:None);self.port.replace_index(m,owner,live=lambda:None)
        self.assertIn(b'100755',self.command('ls-tree','HEAD','script'));self.assertEqual(b'',self.command('ls-tree','HEAD','report.md'))
    def test_unrelated_index_assume_unchanged_flag_survives(self):
        (self.root/'other').write_bytes(b'other');self.command('add','other');self.command('update-index','--assume-unchanged','other')
        with self.port.exclusion():
            m=self.prepare();owner=self.port.acquire_index(m);self.port.update_ref(m,owner,live=lambda:None,event=lambda *_:None);self.port.replace_index(m,owner,live=lambda:None)
        self.assertTrue(self.command('ls-files','-v','other').startswith(b'h '))

if __name__=='__main__':unittest.main()
