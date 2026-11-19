import hashlib,unittest
from pathlib import Path
from colvia.codec import RecordError
from colvia.platforms.darwin_git import DarwinGit
from colvia.git_index import parse
from test_foundation_git import GitFixture

AUTHOR=dict(name='Synthetic Owner',email='owner@example.invalid',date='1700000000 +0000')
class CandidateFixture(GitFixture):
    def setUp(self):
        super().setUp();self.scratch=self.home/'integration';self.scratch.mkdir(mode=0o700)
        self.port=DarwinGit(self.root,self.scratch,self.git)
    def changes(self,data=b'reviewed report\n'):
        (self.root/'report.md').write_bytes(data)
        return {'report.md':dict(path='report.md',kind='regular',mode='100644',size=len(data),sha256=hashlib.sha256(data).hexdigest())},lambda _:iter([data])
    def prepare(self,operation='one',data=b'reviewed report\n'):
        changes,body=self.changes(data)
        return self.port.prepare(operation,changes,body,message='Synthetic accepted report',identity=AUTHOR)

class CandidateTests(CandidateFixture,unittest.TestCase):
    def test_selected_commit_keeps_unrelated_index_and_worktree(self):
        (self.root/'other').write_bytes(b'staged');self.command('add','other');(self.root/'other').write_bytes(b'unstaged')
        original=(self.root/'.git/index').read_bytes();head=self.command('rev-parse','HEAD')
        with self.port.exclusion():
            m=self.prepare();self.assertEqual(original,(self.root/'.git/index').read_bytes());self.assertEqual(head,self.command('rev-parse','HEAD'))
            self.assertEqual(b'report.md\n',self.command('diff-tree','--no-commit-id','--name-only','-r',m['new']))
            owner=self.port.acquire_index(m);self.port.update_ref(m,owner,live=lambda:None,event=lambda *_:None)
            self.port.replace_index(m,owner,live=lambda:None)
        self.assertEqual(m['new'],self.command('rev-parse','HEAD').decode().strip())
        self.assertEqual(b'unstaged',(self.root/'other').read_bytes())
        self.assertEqual(b'other\n',self.command('diff','--cached','--name-only'))
        self.assertEqual(b'staged',self.command('show',':other'))
        data=(self.root/'report.md').read_bytes();(self.root/'report.md').write_bytes(b'X'+data[1:])
        self.assertIn(b'report.md',self.command('diff-files','--name-only'))
    def test_partial_staging_refuses_and_preserves_live_index(self):
        (self.root/'report.md').write_bytes(b'partial');self.command('add','report.md');old=(self.root/'.git/index').read_bytes()
        with self.port.exclusion(),self.assertRaisesRegex(RecordError,'partial-staging'):self.prepare()
        self.assertEqual(old,(self.root/'.git/index').read_bytes());self.assertFalse((self.root/'.git/index.lock').exists())
    def test_hook_appearance_stops_before_ref_mutation(self):
        with self.port.exclusion():
            m=self.prepare();owner=self.port.acquire_index(m)
            hook=self.root/'.git/hooks/pre-commit';hook.write_text('#!/bin/sh\nexit 99\n');hook.chmod(0o700)
            with self.assertRaisesRegex(RecordError,'hooks-require'):self.port.update_ref(m,owner,live=lambda:None,event=lambda *_:None)
            self.assertEqual(m['context']['ref'],self.command('rev-parse','HEAD').decode().strip())
    def test_foreign_lock_is_preserved(self):
        with self.port.exclusion():
            m=self.prepare();lock=self.root/'.git/index.lock';lock.write_bytes(b'foreign')
            with self.assertRaises(FileExistsError):self.port.acquire_index(m)
            self.assertEqual(b'foreign',lock.read_bytes())
    def test_file_changed_after_ref_completes_index_and_keeps_user_edit(self):
        with self.port.exclusion():
            m=self.prepare();owner=self.port.acquire_index(m);self.port.update_ref(m,owner,live=lambda:None,event=lambda *_:None)
            original=(self.root/'.git/index').read_bytes();(self.root/'report.md').write_bytes(b'late edit')
            self.port.replace_index(m,owner,live=lambda:None)
            self.assertNotEqual(original,(self.root/'.git/index').read_bytes())
            self.assertEqual(b'late edit',(self.root/'report.md').read_bytes())
            self.assertEqual(b'reviewed report\n',self.command('show',':report.md'))
            self.assertEqual(b'report.md\n',self.command('diff','--name-only'))
    def test_unborn_branch_refuses_binary_and_accepts_text(self):
        fresh=self.home/'fresh';fresh.mkdir();self.command('init','-q',root=fresh)
        self.root=fresh;self.port=DarwinGit(self.root,self.scratch,self.git)
        with self.port.exclusion():
            with self.assertRaisesRegex(RecordError, 'git-content-uninspectable'):
                self.prepare(data=b'\0\xffbinary')
            m=self.prepare(data=b'reviewed text');self.assertIsNone(m['context']['ref']);self.assertIsNone(m['context']['index'])
            owner=self.port.acquire_index(m);self.port.update_ref(m,owner,live=lambda:None,event=lambda *_:None);self.port.replace_index(m,owner,live=lambda:None)
        self.assertEqual(b'reviewed text',self.command('show','HEAD:report.md'))
    def test_filter_and_replacement_views_refuse(self):
        self.command('config','filter.synthetic.clean','cat')
        with self.port.exclusion(),self.assertRaisesRegex(RecordError,'transform-not-supported'):self.prepare()

if __name__=='__main__':unittest.main()
