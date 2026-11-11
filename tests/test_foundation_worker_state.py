"""RF-T12 exact bytes/mode/absence and immutable outside-scope baseline."""
import hashlib,unittest
from colvia.codec import RecordError
from colvia.worker_state import transitions,classify,require_initial


def file(path,raw=b'original',mode='100644'):
    return dict(path=path,kind='regular',mode=mode,size=len(raw),sha256=hashlib.sha256(raw).hexdigest())


class WorkerStateTests(unittest.TestCase):
    def test_add_delete_binary_and_mode_have_distinct_pre_post(self):
        before=[file('gone'),file('mode'),file('binary',b'\x00\xff')]
        after=[file('added',b''),file('mode',mode='100755'),file('binary',b'\xff\x00')]
        scope=['gone','mode','binary','added']
        changes=transitions(before,after,scope)
        self.assertEqual(['added','binary','gone','mode'],[c['path'] for c in changes])
        self.assertTrue(classify(before,after,before,scope).all_pre)
        self.assertTrue(classify(before,after,after,scope).all_post)
        mixed=[file('gone'),file('mode',mode='100755'),file('binary',b'\x00\xff')]
        state=classify(before,after,mixed,scope)
        self.assertTrue(state.resumable);self.assertFalse(state.all_pre);self.assertFalse(state.all_post)
        self.assertEqual('post',dict(state.paths)['mode'])
    def test_lost_destination_edit_is_not_a_valid_new_baseline(self):
        before=[file('report')];after=[file('report',b'worker')];other=[file('report',b'user')]
        with self.assertRaisesRegex(RecordError,'worker-destination-baseline-changed'):
            require_initial(before,after,other,['report'])
        self.assertEqual((('report','unknown'),),classify(before,after,other,['report']).paths)
    def test_unmodified_scope_path_still_protected(self):
        before=[file('report'),file('reference')];after=[file('report',b'worker'),file('reference')]
        now=[file('report',b'worker'),file('reference',b'changed')]
        state=classify(before,after,now,['report','reference'])
        self.assertEqual(('reference',),state.outside);self.assertFalse(state.resumable)
    def test_unrelated_new_or_deleted_file_prevents_resume(self):
        before=[file('a'),file('keep')];after=[file('a',b'new'),file('keep')]
        for current in ([file('a',b'new')],[*after,file('extra')]):
            state=classify(before,after,current,['a']);self.assertFalse(state.all_post);self.assertFalse(state.resumable)
    def test_aliases_between_images_and_ancestor_components_refuse(self):
        for before,after,scope in [([file('A')],[file('a')],['A','a']),
                                    ([file('Dir/a')],[file('Dir/a'),file('dir/b')],['dir/b']),
                                    ([file('a')],[file('a/b')],['a','a/b'])]:
            with self.assertRaisesRegex(RecordError,'worker-path-alias|worker-path-type-conversion'):
                transitions(before,after,scope)
    def test_unicode_alias_and_duplicate_scope_refuse(self):
        for scope in (['가','가'],['a','a']):
            with self.assertRaises(RecordError):transitions([],[],scope)
    def test_opaque_edit_and_ancestor_refuse(self):
        link=dict(path='link',kind='symlink',mode='120000',target='YQ==')
        with self.assertRaises(RecordError):transitions([link],[],['link'])
        with self.assertRaises(RecordError):transitions([link],[link],['link/report'])
    def test_outside_change_cannot_be_declared_as_result(self):
        with self.assertRaisesRegex(RecordError,'outside-scope-change'):
            transitions([file('a')],[file('a',b'new'),file('b')],['a'])
    def test_missing_old_file_is_unknown_not_progress(self):
        state=classify([file('a')],[file('a',b'new')],[],['a'])
        self.assertEqual((('a','unknown'),),state.paths);self.assertFalse(state.resumable)
    def test_empty_change_is_only_complete_when_full_tree_matches(self):
        before=[file('a')]
        self.assertTrue(classify(before,before,before,['a']).all_post)
        self.assertFalse(classify(before,before,[file('a',b'changed')],['a']).all_post)
    def test_detached_transition_values_do_not_mutate_input(self):
        before=[file('a')];after=[file('a',b'next')]
        changes=transitions(before,after,['a']);changes[0]['pre']['size']=100
        self.assertEqual(len(b'original'),before[0]['size'])

if __name__=='__main__':unittest.main()
