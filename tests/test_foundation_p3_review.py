"""Reviewer counterexamples; no installed app or external effects."""
import unittest,uuid
from colvia.binding import WorkspaceRegistration
from colvia.codec import RecordError,object_ref,decode_envelope
from colvia.connection import Connections
from colvia.maps import build_map,map_update
from colvia.work import WorkService,work_key
from colvia.workspace import LocalWorkspace
from test_foundation_work import WorkFixture
from test_foundation_work_git import GitWorkFixture
from test_foundation_git import GitFixture

class ReviewWorkTests(WorkFixture,unittest.TestCase):
    def test_unreadable_current_result_still_returns_review_and_rework_receipt(self):
        self.start();(self.root/'report.md').write_text('submitted');self.submit()
        (self.root/'report.md').unlink();(self.root/'report.md').mkdir()
        review=self.service.review('report');self.assertIsNone(review['current_matches'])
        with self.assertRaises(RecordError):self.service.accept(operation='accept',work='report',receipt=review['receipt'],statement='수락')
        self.assertEqual('active',self.service.revise(operation='revise',work='report',receipt=review['receipt'],statement='다시 고쳐줘')['state'])
    def test_same_receipt_after_archive_observes_original_acceptance(self):
        self.start();(self.root/'report.md').write_text('submitted');review=self.submit()
        self.service.accept(operation='accept',work='report',receipt=review['receipt'],statement='수락')
        self.service.archive(operation='archive',work='report',archived=True)
        current=self.store.root().ref
        self.service.archive(operation='same-archive',work='report',archived=True)
        self.assertEqual(current,self.store.root().ref)
        self.assertEqual('completed',self.service.accept(operation='repeat',work='report',receipt=review['receipt'],statement='수락')['state'])
        self.assertEqual(current,self.store.root().ref)
    def test_casefold_managed_scope_is_refused_before_approval(self):
        with self.assertRaisesRegex(RecordError,'managed-path-not-editable'):self.plan(scope=('.GIT/config',))
    def test_duplicate_scope_is_refused_before_staging(self):
        original=self.store.begin_import;called=[]
        def begin(*args,**kwargs):called.append(True);return original(*args,**kwargs)
        self.store.begin_import=begin
        with self.assertRaisesRegex(RecordError,'invalid-scope'):self.plan(scope=('report.md','report.md'))
        self.assertFalse(called)

class ReviewGitTests(GitWorkFixture,unittest.TestCase):
    def test_approved_ignored_new_file_can_be_submitted_and_accepted(self):
        (self.root/'.gitignore').write_text('out/\n')
        self.start(('out/report.md',));(self.root/'out').mkdir();(self.root/'out/report.md').write_text('new')
        review=self.submit();self.assertEqual(['out/report.md'],review['files'])
        self.assertEqual('completed',self.service.accept(operation='accept',work='report',receipt=review['receipt'],statement='수락')['state'])
    def test_structural_child_scope_is_rejected_before_a_plan_is_published(self):
        self.nested()
        with self.assertRaisesRegex(RecordError,'boundary-swallows-protected'):
            self.service.plan(operation='plan',work='nested',title='다른 작업 폴더',goal='수정',scope=['.claude/worktrees/child/report.md'],checks=['확인'])
        self.assertIsNone(self.store.head(work_key('nested')))

    def test_other_workspace_can_read_retained_result_but_cannot_accept(self):
        self.start();(self.root/'report.md').write_text('submitted');review=self.submit()
        other=WorkService(self.store,LocalWorkspace(self.store,self.root,str(uuid.uuid4()),git=self.git,locator_reader=lambda:self.locator))
        shown=other.review('report');self.assertIsNone(shown['current_matches']);self.assertEqual('wrong-workspace',shown['current_unavailable'])
        self.assertEqual('submitted',other.result_content('report','report.md')['after']['text'])
        with self.assertRaisesRegex(RecordError,'wrong-workspace'):
            other.accept(operation='wrong-place',work='report',receipt=review['receipt'],statement='수락')

    def test_other_workspace_cannot_replace_plan_even_with_known_receipt(self):
        planned=self.service.plan(operation='plan',work='report',title='원래 계획',goal='보완',scope=['report.md'],checks=['확인'])
        sibling=self.home/'sibling';self.command('worktree','add','-q','-b','sibling',str(sibling))
        top=self.git.topology(sibling);workspace=str(uuid.uuid4());connections=Connections(self.store)
        connections.register(operation='register',locator=self.locator,observed=top,workspace=WorkspaceRegistration(workspace,top.root,top.gitdir),
            registrations=connections.registrations(top),verify_topology=lambda:self.git.topology(sibling))
        other=WorkService(self.store,LocalWorkspace(self.store,sibling,workspace,git=self.git,locator_reader=lambda:self.locator))
        with self.assertRaisesRegex(RecordError,'wrong-workspace'):
            other.plan(operation='replace',work='report',title='다른 계획',goal='교체',scope=['report.md'],checks=['확인'],replace_receipt=planned['receipt'])
        self.assertEqual('원래 계획',self.service.plan_review('report')['title'])

class ReviewMapTests(unittest.TestCase):
    def test_collapse_returns_only_reachable_new_objects(self):
        value=object_ref('body.chunk',1,b'x');values={f'k{i}':value for i in range(17)}
        built=build_map(values.items());stored=dict(built.objects)
        updated=map_update(built.root,{'k0':None},stored.__getitem__)
        reachable=set();pending=[updated.root];staged=dict(updated.objects)
        while pending:
            ref=pending.pop()
            if ref not in staged or ref in reachable:continue
            reachable.add(ref);obj=decode_envelope(ref,staged[ref])
            pending.extend(e.ref for e in obj.edges if e.ref.kind.startswith('map.'))
        self.assertEqual(reachable,set(staged))

if __name__=='__main__':unittest.main()
