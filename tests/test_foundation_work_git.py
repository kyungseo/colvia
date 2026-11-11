"""Git topology changes during one Work, using synthetic local fixtures only."""
from pathlib import Path
import unittest,uuid
from colvia.binding import Locator,ProjectBinding,WorkspaceRegistration
from colvia.codec import RecordError
from colvia.connection import Connections
from colvia.storage.sqlite import GenerationStore
from colvia.workspace import LocalWorkspace
from colvia.work import WorkService
from test_foundation_binding import P,I,W
from test_foundation_git import GitFixture

class GitWorkFixture(GitFixture):
    def setUp(self):
        super().setUp();self.store=GenerationStore.create(self.home/'state.sqlite3',project=P,instance=I,generation='g',active_check=lambda:None)
        top=self.git.topology(self.root);self.locator=Locator(P,I,1,'a'*64)
        Connections(self.store).connect(operation='connect',binding=ProjectBinding(self.locator,'git',top.common),observed=top,
            workspace=WorkspaceRegistration(W,top.root,top.gitdir),verify_topology=lambda:self.git.topology(self.root))
        self.service=WorkService(self.store,LocalWorkspace(self.store,self.root,W,git=self.git,locator_reader=lambda:self.locator))
    def tearDown(self):self.store.close();super().tearDown()
    def start(self,scope=('report.md',)):
        plan=self.service.plan(operation='plan',work='report',title='보고서',goal='본문 보완',scope=scope,checks=['본문 확인'])
        self.service.approve(operation='approve',work='report',receipt=plan['receipt'],statement='진행')
        self.service.start(operation='start',work='report')
    def submit(self):
        return self.service.submit(operation='submit',work='report',summary='본문 보완',checks=[dict(name='본문 확인',status='passed',detail='확인')])
    def nested(self):
        parent=self.root/'.claude/worktrees';parent.mkdir(parents=True)
        child=parent/'child';self.command('worktree','add','-q','-b','child',str(child))
        top=self.git.topology(child);connections=Connections(self.store)
        connections.register(operation='register',locator=self.locator,observed=top,
            workspace=WorkspaceRegistration(str(uuid.uuid4()),top.root,top.gitdir),registrations=connections.registrations(top),verify_topology=lambda:self.git.topology(child))
        return parent


class GitWorkTests(GitWorkFixture,unittest.TestCase):
    def test_parent_exclude_after_app_nested_worktree_does_not_block_submission(self):
        self.start();self.nested()
        with (self.root/'.git/info/exclude').open('ab') as out:out.write(b'.claude/worktrees/\n')
        (self.root/'report.md').write_text('new report')
        self.assertEqual('review',self.submit()['state'])
    def test_individual_exclude_with_nonworkspace_parent_sibling(self):
        parent=self.nested();(parent/'ordinary.txt').write_text('keep visible')
        self.start()
        with (self.root/'.git/info/exclude').open('ab') as out:out.write(b'.claude/worktrees/child/\n')
        (self.root/'report.md').write_text('new report');self.assertEqual('review',self.submit()['state'])
    def test_policy_edit_cannot_hide_scope_escape_at_publication(self):
        (self.root/'.gitignore').write_text('');(self.root/'reference.md').write_text('original')
        self.start(('report.md','.gitignore'))
        (self.root/'.gitignore').write_text('reference.md\n');(self.root/'reference.md').write_text('changed')
        with self.assertRaisesRegex(RecordError,'outside-scope-change'):self.submit()
    def test_unchanged_symlink_allows_regular_work_but_retarget_refuses(self):
        (self.root/'link').symlink_to('report.md');self.start();(self.root/'report.md').write_text('new report')
        (self.root/'link').unlink();(self.root/'link').symlink_to('elsewhere')
        with self.assertRaisesRegex(RecordError,'outside-scope-change|opaque-context-changed'):self.submit()

if __name__=='__main__':unittest.main()
