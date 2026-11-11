import hashlib,unittest
from colvia.codec import RecordError
from colvia.observation import Policy,PolicySource,literal_root_directory,policy_transition,verify_scope


def policy(exclude=b'',extra=()):
    return Policy((PolicySource('git:info/exclude',exclude),*extra),(('core.ignorecase','true'),),'synthetic-git')

def file(path,data=b'kept'):
    return dict(path=path,kind='regular',mode='100644',size=len(data),sha256=hashlib.sha256(data).hexdigest())


class PolicyTests(unittest.TestCase):
    def test_literal_parent_and_leading_slash_have_exact_root_semantics(self):
        for line in (b'.claude/worktrees/\n',b'/.claude/worktrees/\n'):
            self.assertEqual('.claude/worktrees',literal_root_directory(line))
            self.assertEqual('equivalent-structural-append',policy_transition(policy(),policy(line),
                verified_structural=frozenset({'.claude/worktrees'}),protected=frozenset()))
        for line in (b'worktrees/\n',b'/.claude/**/\n',b'!/.claude/worktrees/\n',b'/.claude/worktrees/ \n',b'/.claude/worktrees/\r\n'):
            with self.subTest(line=line),self.assertRaises(RecordError):literal_root_directory(line)

    def test_reorder_remove_negation_unverified_and_protected_refuse(self):
        for old,new in ((b'a\nb\n',b'b\na\n'),(b'a\n',b''),(b'!keep\n',b'/.agent/worktrees/\n')):
            with self.assertRaises(RecordError):policy_transition(policy(old),policy(new),verified_structural=frozenset(),protected=frozenset())
        with self.assertRaisesRegex(RecordError,'structural-proof-required'):
            policy_transition(policy(),policy(b'/.agent/worktrees/\n'),verified_structural=frozenset(),protected=frozenset())
        with self.assertRaisesRegex(RecordError,'boundary-swallows-protected'):
            policy_transition(policy(),policy(b'/.agent/worktrees/\n'),verified_structural=frozenset({'.agent/worktrees'}),protected=frozenset({'.agent/worktrees/old'}))

    def test_duplicate_occurrences_and_global_origin_never_disappear(self):
        source=PolicySource('global:ignore',b'file\nfile\n')
        self.assertNotEqual(source.occurrences()[0][:3],source.occurrences()[1][:3])
        with self.assertRaisesRegex(RecordError,'policy-origin-order-changed'):
            policy_transition(policy(extra=(source,)),policy(extra=(PolicySource('global:other',source.raw),)),
                verified_structural=frozenset(),protected=frozenset())

    def test_approved_policy_edit_still_requires_old_and_new_union(self):
        old=policy(extra=(PolicySource('workspace:.gitignore',b''),))
        new=policy(extra=(PolicySource('workspace:.gitignore',b'old.txt\n'),))
        self.assertEqual('approved-policy-edit-union-required',policy_transition(old,new,
            verified_structural=frozenset(),protected=frozenset({'old.txt'}),approved_policy_paths={'.gitignore'}))
        before=[file('.gitignore',b''),file('old.txt')]
        after=[file('.gitignore',b'old.txt\n'),file('old.txt',b'changed')]
        with self.assertRaisesRegex(RecordError,'outside-scope-change'):verify_scope(before,after,frozenset({'.gitignore'}))

    def test_scope_and_opaque_changes_are_independent_of_display(self):
        old=[file('report'),file('reference')];after=[file('report',b'new'),file('reference',b'else')]
        with self.assertRaisesRegex(RecordError,'outside-scope-change'):verify_scope(old,after,frozenset({'report'}))
        link=dict(path='link',kind='symlink',mode='120000',target='dGFyZ2V0')
        self.assertEqual((),verify_scope([*old,link],[*old,link],frozenset({'report'})))
        with self.assertRaisesRegex(RecordError,'opaque-edit-not-supported'):verify_scope([link],[link],frozenset({'link/child'}))
        with self.assertRaisesRegex(RecordError,'opaque-edit-not-supported'):verify_scope([], [link],frozenset({'link'}))

if __name__=='__main__':unittest.main()
