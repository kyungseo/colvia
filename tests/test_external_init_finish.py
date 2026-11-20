"""Managed recovery entry with an isolated selected slot, native Git and real Work."""
from contextlib import closing, redirect_stdout
from io import StringIO
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from colvia.adapters.git import Git
from colvia.cli import main
from colvia.codec import decode_envelope
from colvia.git_transition import GitTransition
from colvia.managed_entry import ManagedEntry
from colvia.records import link
from colvia.storage.sqlite import runtime_capabilities
from colvia.updates.lease import RuntimeLease
from test_foundation_git import EXECUTABLE
from test_foundation_move import MoveFixture


class ExternalInitTests(MoveFixture, unittest.TestCase):
    def setUp(self):
        from test_foundation_slots import SlotTests
        if not EXECUTABLE.is_file():
            self.skipTest('native Git fixture unavailable')
        area = tempfile.TemporaryDirectory()
        self.addCleanup(area.cleanup)
        self.base = Path(area.name).resolve()
        self.root = self.base / 'project'
        self.root.mkdir()
        self.report = self.root / 'report.md'
        self.report.write_text('original')
        (self.root / '.gitignore').write_text('ignored/\n')
        self.hidden = self.root / 'ignored'
        self.hidden.mkdir()
        (self.hidden / 'old').write_text('original')
        git = Git(EXECUTABLE, environment=dict(os.environ, GIT_CONFIG_NOSYSTEM='1'))
        self.manager_fixture(self.base, git)
        self.connect()
        slots = self.manager.slots
        pointer = SlotTests.slot(SimpleNamespace(manager=slots), 'recovery', 1,
                                 extra=runtime_capabilities() - {'foundation-v1'})
        slots.initialize(pointer)
        self.entry = object.__new__(ManagedEntry)
        self.entry.home = self.manager
        self.entry.pointer = pointer
        self.entry.lease = RuntimeLease(slots, expected_pointer=pointer)
        self.entry.git = lambda: git
        self.active_head, self.approval = self.active()

    def git(self, *args):
        return subprocess.check_output([str(EXECUTABLE), '--no-optional-locks', '-C', str(self.root), *args],
                                       env=self.setup.git.env)

    def init(self):
        self.git('init', '--quiet', '--template=')
        self.git('add', '--', 'report.md')
        self.index = (self.root / '.git/index').read_bytes()

    def command(self, *args, error=None, root=None, finish=True):
        out = StringIO()
        with redirect_stdout(out):
            code = main(['--root', str(root or self.root), '--json',
                         *(['--finish-plain-work'] if finish else []), *args], entry=self.entry)
        self.assertEqual(2 if error else 0, code, out.getvalue())
        value = json.loads(out.getvalue())
        if error:
            self.assertEqual(error, value['error'], value)
        return value

    def convert(self):
        convert = GitTransition(self.manager, self.setup.git)
        preview = convert.preview(self.project, self.root)
        result = convert.start(operation='convert', plan=preview['plan'], receipt=preview['receipt'],
                               statement='Adopt this Git repository')
        self.assertEqual('converted', result['state'])
        self.assertEqual(self.index, (self.root / '.git/index').read_bytes())
        self.assertEqual(b'original', self.git('show', ':report.md'))

    def test_backup_finish_and_convert_preserves_decisions_and_index(self):
        self.init()
        self.command('ordinary', 'list', finish=False, error='workspace-connection-kind-changed')
        self.assertEqual('active', self.command('ordinary', 'view', 'report')['state'])
        with closing(self.authority.store()) as store:
            before = store.root().ref
            plan = link(decode_envelope(self.active_head, store.load(self.active_head)), 'plan')
        self.command('backup', 'export', '--destination', str(self.root/'.git/export'), '--scratch', str(self.base),
                     error='external-init-backup-outside')
        backup = self.command('backup', 'export', '--destination', str(self.base/'saved'), '--scratch', str(self.base))
        self.assertEqual(before.as_dict(), backup['root'])
        self.assertTrue(backup['published'] and (self.base/'saved').is_file())
        self.report.write_text('updated')
        submit = ('ordinary', 'submit', 'report', '--summary', 'Updated', '--passed', 'content::Checked')
        for name in ('old', 'new'):
            ignored = self.hidden/name
            ignored.write_text('outside scope')
            self.assertEqual(('ignored/'+name+'\n').encode(), self.git('check-ignore', '--', 'ignored/'+name))
            self.command(*submit, error='outside-scope-change')
            with closing(self.authority.store()) as store:
                self.assertEqual(before, store.root().ref)
            if name == 'old':
                ignored.write_text('original')
            else:
                ignored.unlink()
        review = self.command(*submit)
        self.command('ordinary', 'accept', 'report', '--receipt', 'stale', '--statement', 'Accept',
                     error='stale-result-receipt')
        self.command('ordinary', 'accept', 'report', '--receipt', review['receipt'], '--statement', 'Accept')
        with closing(self.authority.store()) as store:
            done = store.head('work:report')
            saved = decode_envelope(done, store.load(done))
            self.assertEqual(self.approval, link(saved, 'approval'))
            self.assertEqual(plan, link(saved, 'plan'))
            result = link(saved, 'result')
            self.assertEqual(result, link(decode_envelope(link(saved, 'decision'), store.load(link(saved, 'decision'))), 'result'))
        self.convert()
        self.assertEqual('completed', self.command('ordinary', 'view', 'report', finish=False)['state'])
        with closing(self.authority.store()) as store:
            self.assertEqual(done, store.head('work:report'))
            self.assertEqual('updated', self.work(store).result_content('report','report.md')['after']['text'])

    def test_discard_submitted_work_requires_current_decision_and_retains_result(self):
        self.report.write_text('submitted')
        with closing(self.authority.store()) as store:
            self.submit(self.work(store), 'submitted')
            current = store.head('work:report')
            result = link(decode_envelope(current, store.load(current)), 'result')
        self.init()
        args = ('report', 'discard', '--reason', 'Owner stopped this Work')
        self.command('ordinary', 'lifecycle-apply', *args, '--receipt', 'stale', error='lifecycle-preview-stale')
        with closing(self.authority.store()) as store:
            self.assertEqual(current, store.head('work:report'))
        review = self.command('ordinary', 'lifecycle-preview', *args)
        self.command('ordinary', 'lifecycle-apply', *args, '--receipt', review['receipt'])
        self.assertEqual(self.index, (self.root / '.git/index').read_bytes())
        self.assertEqual(b'submitted', self.git('show', ':report.md'))
        convert = GitTransition(self.manager, self.setup.git)
        approved = convert.preview(self.project, self.root)
        convert.start(operation='convert', plan=approved['plan'], receipt=approved['receipt'], statement='Adopt')
        self.assertEqual(self.index, (self.root / '.git/index').read_bytes())
        with closing(self.authority.store()) as store:
            head = decode_envelope(store.head('work:report'), store.load(store.head('work:report')))
            self.assertEqual('discarded', head.payload['phase'])
            self.assertEqual(result, link(head, 'result'))
            self.assertEqual(self.approval, link(head, 'approval'))

    def test_paused_review_resumes_and_returns_to_same_approval(self):
        self.report.write_text('first version')
        with closing(self.authority.store()) as store:
            self.submit(self.work(store), 'first-submission')
        pause = ('report', 'pause', '--reason', 'Waiting for edits')
        preview = self.command('ordinary', 'lifecycle-preview', *pause, finish=False)
        self.command('ordinary', 'lifecycle-apply', *pause, '--receipt', preview['receipt'], finish=False)
        self.init()
        resume = ('report', 'resume', '--reason', 'Continue reviewing')
        preview = self.command('ordinary', 'lifecycle-preview', *resume)
        self.command('ordinary', 'lifecycle-apply', *resume, '--receipt', preview['receipt'])
        review = self.command('ordinary', 'review', 'report')
        self.command('ordinary', 'revise', 'report', '--statement', 'Revise this result', '--receipt', review['receipt'])
        self.report.write_text('revised')
        review = self.command('ordinary', 'submit', 'report', '--summary', 'Revised', '--passed', 'content::Read again')
        self.command('ordinary', 'accept', 'report', '--statement', 'Accept revision', '--receipt', review['receipt'])
        detail = self.command('ordinary', 'view', 'report')
        self.command('ordinary', 'revise', 'report', '--statement', 'Reopen', '--receipt', detail['reopen_receipt'],
                     error='stale-result-receipt')
        self.assertEqual('first version', self.command('ordinary', 'content', 'report', 'report.md',
                                                      '--revision', '1')['after']['text'])
        with closing(self.authority.store()) as store:
            current = store.head('work:report')
            self.assertEqual(self.approval, link(decode_envelope(current, store.load(current)), 'approval'))
        self.assertEqual(self.index, (self.root / '.git/index').read_bytes())

    def test_approved_start_and_remaining_planned_work_block_conversion(self):
        from colvia.codec import RecordError
        with closing(self.authority.store()) as store:
            work = self.work(store)
            for key in ('second', 'waiting'):
                preview = work.plan(operation='plan-'+key, work=key, title=key, goal='Check report',
                                    scope=['report.md'], checks=['content'])
                if key == 'second':
                    work.approve(operation='approve-second', work=key, receipt=preview['receipt'], statement='Approved')
        self.init()
        self.command('ordinary', 'start', 'second')
        self.assertEqual('planned', self.command('ordinary', 'view', 'waiting')['state'])
        self.command('ordinary', 'approve', 'waiting', '--receipt', preview['receipt'], '--statement', 'Approve',
                     error='external-init-finish-action')
        with self.assertRaisesRegex(RecordError, 'git-transition-unfinished-work'):
            GitTransition(self.manager, self.setup.git).preview(self.project, self.root)
        self.assertEqual(self.index, (self.root/'.git/index').read_bytes())

    def test_cancelled_transition_allows_later_work_and_manual_init(self):
        self.report.write_text('ready')
        with closing(self.authority.store()) as store:
            service = self.work(store)
            review = self.submit(service, 'first-result')
            service.accept(operation='accept-first', work='report', receipt=review['receipt'], statement='Accept')
        converter = GitTransition(self.manager, self.setup.git)
        preview = converter.preview(self.project, self.root)
        def interrupt(phase):
            if phase == 'reserved':
                raise InterruptedError()
        with self.assertRaises(InterruptedError):
            converter.start(operation='abandoned', plan=preview['plan'], receipt=preview['receipt'],
                            statement='Convert', checkpoint=interrupt)
        self.assertEqual('cancelled', converter.resume('abandoned', cancel=True)['state'])
        with closing(self.authority.store()) as store:
            service = self.work(store)
            plan = service.plan(operation='later-plan', work='later', title='Later', goal='Edit again',
                                scope=['report.md'], checks=['read'])
            service.approve(operation='later-approved', work='later', receipt=plan['receipt'], statement='Approve')
            service.start(operation='later-start', work='later')
        self.init()
        self.report.write_text('later version')
        review = self.command('ordinary','submit','later','--summary','Ready','--passed','read::Read all')
        self.assertEqual('completed', self.command('ordinary','accept','later','--receipt',review['receipt'],
                                                  '--statement','Accept later result')['state'])
        self.assertIsNotNone(converter.preview(self.project, self.root)['receipt'])

    def test_repository_change_during_submit_keeps_old_work(self):
        from colvia.work import WorkService
        self.init()
        self.report.write_text('new body')
        old_admin = self.base/'original-admin'
        recheck = WorkService._recheck_observation
        def change_then_recheck(service, *args, **kwargs):
            (self.root/'.git').rename(old_admin)
            self.git('init','--quiet','--template=')
            return recheck(service, *args, **kwargs)
        with patch.object(WorkService, '_recheck_observation', change_then_recheck):
            self.command('ordinary','submit','report','--summary','Updated','--passed','content::Checked',
                         error='workspace-observation-changed')
        with closing(self.authority.store()) as store:
            self.assertEqual(self.active_head, store.head('work:report'))
        self.assertEqual(self.index, (old_admin/'index').read_bytes())

    def test_read_published_work_and_backup_after_interrupted_import(self):
        self.init()
        with closing(self.authority.store()) as store:
            store.begin_import('earlier-import', 'test')
            before = store.root().ref
        self.assertEqual('active', self.command('ordinary', 'view', 'report')['state'])
        self.assertFalse(self.command('operation','earlier-import')['recorded'])
        archive = self.base/'safe-backup'
        backup = self.command('backup','export','--destination',str(archive),'--scratch',str(self.base))
        self.assertEqual(before.as_dict(), backup['root'])
        self.assertTrue(self.command('backup','status')['verified_export_recorded'])
        self.command('ordinary','submit','report','--summary','Ready','--passed','content::Checked',
                     error='connection-move-work-pending')
        with closing(self.authority.store()) as store:
            self.assertTrue(store.has_active_imports())

    def test_backup_destination_and_commands_are_confined(self):
        from colvia.external_init import finish
        from colvia.codec import RecordError
        self.init()
        for group, action in [('backup','restore'), ('operation','resume')]:
            with self.assertRaisesRegex(RecordError, 'external-init-finish-action'):
                finish(self.entry, SimpleNamespace(group=group, action=action))
        destination = self.base/'existing'
        destination.symlink_to(self.report)
        self.command('backup','export','--destination',str(destination),'--scratch',str(self.base),
                     error='backup-destination-exists')
        self.assertTrue(destination.is_symlink())
        self.assertEqual('original', self.report.read_text())
        self.command('backup','export','--destination',str(self.base/'missing'/'out'),'--scratch',str(self.base),
                     error='workspace-access-unavailable')
        self.assertEqual(self.index, (self.root/'.git/index').read_bytes())

    def test_stale_runtime_refused_in_both_modes(self):
        self.entry.pointer = dict(self.entry.pointer, manifest_sha256='0'*64)
        self.command('ordinary', 'list', finish=False, error='runtime-entry-selection-changed')
        self.init()
        self.command('ordinary', 'list', error='runtime-entry-selection-changed')
        self.assertEqual(self.index, (self.root/'.git/index').read_bytes())

    def test_git_metadata_cannot_be_selected_as_old_work_files(self):
        from colvia.codec import RecordError
        from colvia.external_init import FinishingWorkspace, plain_locator, single_repository
        self.init()
        with closing(self.authority.store(readonly=True)) as store:
            git = self.setup.git
            workspace = FinishingWorkspace(store, self.root, plain_locator(self.root), git,
                                           single_repository(self.root, git))
            with workspace.selected_reader(verify_path=True) as read:
                with self.assertRaisesRegex(RecordError, 'boundary-swallows-protected'):
                    read(['.Git/HEAD'], 4096)
        self.assertEqual(self.index, (self.root/'.git/index').read_bytes())

    def test_reject_copied_marker_foreign_namespace_and_unrelated_actions(self):
        self.init()
        copy = self.base/'copy'
        shutil.copytree(self.root, copy)
        self.command('ordinary', 'list', root=copy, error='git-transition-folder-changed')
        self.command('ordinary', 'archive', 'report', error='external-init-finish-action')
        self.command('ordinary', 'lifecycle-preview', 'report', 'replace', '--reason', 'new goal',
                     error='external-init-finish-action')
        (self.root/'.git/colvia').mkdir()
        self.command('ordinary', 'view', 'report', error='git-transition-foreign-locator')
        self.assertEqual(self.index, (self.root / '.git/index').read_bytes())
