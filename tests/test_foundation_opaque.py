import os,unittest
from colvia.codec import RecordError
from colvia.observe import observe
from colvia.observation import verify_scope
from colvia.platforms.posix import ObservationBudget
from test_foundation_git import GitFixture


class OpaqueTests(GitFixture,unittest.TestCase):
    def observe(self):return observe(self.root,ObservationBudget(200,8*1024*1024),git=self.git)
    def child(self):
        child=self.root/'module';child.mkdir();self.command('init','-q',root=child)
        (child/'file').write_bytes(b'synthetic submodule\n')
        self.command('add','file',root=child);self.command('commit','-qm','Synthetic submodule',root=child)
        oid=self.command('rev-parse','HEAD',root=child).strip().decode()
        self.command('update-index','--add','--cacheinfo','160000,'+oid+',module')
        return child,oid

    def test_unchanged_initialized_gitlink_does_not_block_unrelated_work(self):
        child,oid=self.child();first=self.observe()
        entry=next(e for e in first.snapshot.entries if e['path']=='module')
        self.assertEqual('gitlink',entry['kind']);self.assertEqual(oid,entry['oid'])
        (self.root/'report.md').write_bytes(b'updated report')
        second=self.observe()
        self.assertEqual(('report.md',),verify_scope(first.snapshot.entries,second.snapshot.entries,frozenset({'report.md'})))
        self.assertEqual(first.opaque,second.opaque)

    def test_parent_ignore_setting_cannot_hide_dirty_submodule(self):
        child,_=self.child();self.command('config','submodule.module.ignore','all')
        self.observe();(child/'file').write_bytes(b'changed')
        with self.assertRaisesRegex(RecordError,'gitlink-content-changed'):self.observe()

    def test_submodule_policy_and_initialization_have_separate_evidence(self):
        child,_=self.child();first=self.observe()
        with (child/'.git/info/exclude').open('ab') as out:out.write(b'build/\n')
        second=self.observe()
        self.assertEqual(first.snapshot.entries,second.snapshot.entries)
        self.assertNotEqual(first.opaque,second.opaque)
        (child/'untracked').write_bytes(b'new')
        with self.assertRaisesRegex(RecordError,'gitlink-untracked-or-missing'):self.observe()

    def test_empty_uninitialized_gitlink_is_opaque_and_not_editable(self):
        (self.root/'module').mkdir();oid='a'*40
        self.command('update-index','--add','--cacheinfo','160000,'+oid+',module')
        result=self.observe();self.assertEqual((('module',('uninitialized',)),),result.opaque)
        with self.assertRaisesRegex(RecordError,'opaque-edit-not-supported'):
            verify_scope(result.snapshot.entries,result.snapshot.entries,frozenset({'module/file'}))
        (self.root/'module/hidden').write_bytes(b'not empty')
        with self.assertRaisesRegex(RecordError,'uninitialized-gitlink-not-empty'):self.observe()

    def test_symlink_placeholder_is_opaque_even_when_native_file_is_regular(self):
        self.command('config','core.symlinks','false')
        target=b'outside'
        # Prepare the blob using a synthetic regular file, then give its index
        # entry Git's symlink mode without asking the OS to create a symlink.
        (self.root/'link').write_bytes(target)
        oid=self.command('hash-object','-w','link').strip().decode()
        self.command('update-index','--add','--cacheinfo','120000,'+oid+',link')
        result=self.observe();entry=next(e for e in result.snapshot.entries if e['path']=='link')
        self.assertEqual('symlink',entry['kind'])
        with self.assertRaisesRegex(RecordError,'opaque-edit-not-supported'):
            verify_scope(result.snapshot.entries,result.snapshot.entries,frozenset({'link'}))

    def test_native_symlink_is_not_followed(self):
        (self.root/'link').symlink_to('/synthetic/outside')
        result=self.observe();self.assertEqual('symlink',next(e for e in result.snapshot.entries if e['path']=='link')['kind'])

if __name__=='__main__':unittest.main()
