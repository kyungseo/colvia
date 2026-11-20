import os
import subprocess
import tempfile
import unittest
from pathlib import Path
from contextlib import nullcontext
from types import SimpleNamespace
from unittest.mock import patch

from colvia.adapters.git import Git
from colvia.cli import read_locator
from colvia.codec import RecordError, canonical_bytes
from colvia.manager_entry import parser, run
from colvia.project_setup import ProjectSetup
from colvia.storage.sqlite import runtime_capabilities
from test_foundation_git import EXECUTABLE
from test_foundation_project_setup import SetupFixture


class FirstGitTests(SetupFixture, unittest.TestCase):
    def setUp(self):
        if not EXECUTABLE.is_file():
            self.skipTest('qualified macOS fixture Git unavailable')
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.base = Path(temp.name).resolve()
        self.root = self.base/'project'
        self.root.mkdir()
        self.git = Git(EXECUTABLE)
        self.manager_fixture(self.base, self.git)

    def begin_git(self):
        value = self.setup.preview(self.root, init_git=True)
        self.setup.start(operation='first', plan=value['plan'], receipt=value['receipt'], statement='Use Git')
        return value

    def complete(self):
        setup = ProjectSetup(self.manager, self.git)
        for _ in range(8):
            if setup.resume('first')['state'] == 'connected':
                return
        self.fail('never completed')

    def lease(self):
        caps = runtime_capabilities()
        return SimpleNamespace(check=lambda:None, hold=nullcontext, expected=b'synthetic selection',
                               verified=SimpleNamespace(read_capabilities=caps, write_capabilities=caps))

    def test_combined_registration_is_reviewed_before_any_effect(self):
        from colvia.managed_entry import configured_git
        from colvia.git_registration import read_git_registration
        lease = self.lease()
        entry = SimpleNamespace(home=self.manager,lease=lease,git=lambda:configured_git(self.manager))
        def command(*args):return run(parser(bound=True).parse_args(args),entry)
        plan = command('connect-preview',str(self.root),'--init-git','--git-executable',str(EXECUTABLE))
        self.assertIsNone(read_git_registration(self.manager)[1])
        self.assertFalse((self.root/'.git').exists())
        self.assertIn('이 계정에 등록',plan['question'])
        setup = ProjectSetup(self.manager,None,runtime_lease=lease)
        setup.start(operation='first',plan=plan['plan'],receipt=plan['receipt'],statement='Use this Git here')
        def stop(phase):
            if phase == 'first-git-registered':raise InterruptedError()
        with self.assertRaises(InterruptedError):setup.resume('first', event=stop)
        self.assertEqual(str(EXECUTABLE),read_git_registration(self.manager)[1]['path'])
        self.assertFalse((self.root/'.git').exists())
        self.assertEqual('connected',command('connect-resume','first')['state'])

    def test_failed_private_init_can_resume_without_a_partial_project_repository(self):
        self.begin_git()
        with patch('colvia.first_git.run',side_effect=InterruptedError()):
            with self.assertRaises(InterruptedError):self.setup.resume('first')
        self.assertEqual([],list(self.root.iterdir()))
        self.complete()

    def test_changed_guidance_before_apply_is_preserved(self):
        preview = self.setup.preview(self.root, init_git=True)
        (self.root/'CLAUDE.md').write_text('new instructions')
        with self.assertRaisesRegex(RecordError,'connect-review-changed'):
            self.setup.start(operation='first',plan=preview['plan'],receipt=preview['receipt'],statement='Use Git')
        self.assertEqual('new instructions',(self.root/'CLAUDE.md').read_text())
        self.assertFalse((self.root/'.git').exists())

    def test_git_init_ignores_global_template_and_default_branch(self):
        template=self.base/'template';template.mkdir()
        (template/'unexpected').write_bytes(b'controlled fixture')
        config=self.base/'user-config'
        config.write_text(f'[init]\n\ttemplateDir = {template}\n\tdefaultBranch = other\n')
        with patch.dict(self.git.env, GIT_CONFIG_GLOBAL=str(config)):
            self.begin_git()
            self.complete()
        self.assertEqual(b'ref: refs/heads/main',(self.root/'.git/HEAD').read_bytes().strip())
        self.assertFalse((self.root/'.git/unexpected').exists())

    def test_plain_or_git_preview_is_side_effect_free(self):
        for populated in (False, True):
            if populated:
                (self.root/'notes.md').write_bytes(b'notes')
            before = list(self.root.iterdir())
            plain = self.setup.preview(self.root)
            self.assertTrue(plain['git_choice_available'])
            value = self.setup.preview(self.root, init_git=True)
            self.assertIn('.git/colvia/connection.json', value['files'])
            self.assertNotIn('.colvia-link.json', value['files'])
            self.assertNotEqual(plain['receipt'], value['receipt'])
            with self.assertRaisesRegex(RecordError,'connect-review-changed'):
                self.setup.start(operation='wrong',plan=value['plan'],receipt=plain['receipt'],statement='Plain')
            self.assertEqual(before, list(self.root.iterdir()))
            self.assertFalse(list((self.manager.root/'operations').iterdir()))
            self.assertEqual((),self.manager.projects())

    def test_from_manager_entry_with_existing_documents(self):
        raw = b'author rules\r\n' * 2000
        (self.root/'AGENTS.md').write_bytes(raw)
        (self.root/'notes.md').write_bytes(b'notes')
        lease = self.lease()
        self.manager.files.create(self.manager.root/'tools.json',canonical_bytes(dict(version=1,git=dict(path=str(self.git.executable),sha256=self.git.sha256,version=self.git.version))))
        entry = SimpleNamespace(home=self.manager,lease=lease,git=lambda:self.git)
        def command(*args):return run(parser(bound=True).parse_args(args),entry)
        value = command('connect-preview',str(self.root),'--init-git')
        envelope=self.base/'preview.json'
        self.manager.files.create(envelope,canonical_bytes(value))
        result=command('connect','--plan',str(envelope),'--receipt',value['receipt'],'--operation','first','--statement','Connect')
        self.assertEqual('connected',result['state'])
        self.assertEqual(value['plan']['basis']['project'],read_locator(self.root,self.git).project)
        self.assertTrue((self.root/'AGENTS.md').read_bytes().startswith(raw))
        self.assertEqual(b'notes',(self.root/'notes.md').read_bytes())
        self.assertEqual(b'',subprocess.check_output([str(EXECUTABLE),'-C',str(self.root),'ls-files','--stage']))
        self.assertEqual(b'',subprocess.check_output([str(EXECUTABLE),'-C',str(self.root),'remote']))
        self.assertFalse((self.root/'.git/refs/heads/main').exists())
        self.assertEqual('connected',command('connect-resume','first')['state'])

    def test_restarts_across_init_publish_authority_and_entry(self):
        value=self.begin_git()
        for phase in ('first-git-prepared','first-git-published','first-git-connect-planned','first-git-authority-prepared','first-git-authority-ready','applied'):
            def interrupt(actual):
                if actual==phase:raise InterruptedError(phase)
            with self.assertRaises(InterruptedError):
                ProjectSetup(self.manager,self.git).resume('first',event=interrupt)
            with self.assertRaises(RecordError):self.setup.preview(self.root)
        self.complete()
        self.assertEqual((value['plan']['basis']['project'],),self.manager.projects())

    def test_external_init_after_approval_is_preserved(self):
        self.begin_git()
        subprocess.run([str(EXECUTABLE),'init','-q',str(self.root)],check=True)
        head=(self.root/'.git/HEAD').read_bytes()
        with self.assertRaisesRegex(RecordError,'first-git-repository-changed'):self.setup.resume('first')
        self.assertEqual(head,(self.root/'.git/HEAD').read_bytes())
        self.assertFalse((self.root/'.git/colvia').exists())
        self.assertEqual((),self.manager.projects())

    def test_changed_index_after_publication_is_preserved(self):
        self.begin_git()
        def interrupt(phase):
            if phase=='first-git-published':raise InterruptedError()
        with self.assertRaises(InterruptedError):self.setup.resume('first',event=interrupt)
        (self.root/'notes').write_bytes(b'staged')
        subprocess.run([str(EXECUTABLE),'-C',str(self.root),'add','--','notes'],check=True)
        index=(self.root/'.git/index').read_bytes()
        with self.assertRaisesRegex(RecordError,'first-git-repository-changed'):self.setup.resume('first')
        self.assertEqual(index,(self.root/'.git/index').read_bytes())

    def test_mid_connection_can_resume_after_other_staging(self):
        self.begin_git()
        def stop(phase):
            if phase == 'applied':
                raise InterruptedError()
        with self.assertRaises(InterruptedError):
            self.setup.resume('first', event=stop)
        (self.root/'notes').write_bytes(b'stage this')
        subprocess.run([str(EXECUTABLE), '-C', str(self.root), 'add', '--', 'notes'], check=True)
        index = (self.root/'.git/index').read_bytes()
        self.complete()
        self.assertEqual(index, (self.root/'.git/index').read_bytes())
        self.assertEqual(b'stage this', (self.root/'notes').read_bytes())

    def test_cancel_after_external_init_releases_only_this_reservation(self):
        from colvia.first_git import cancel
        value = self.begin_git()
        with self.assertRaisesRegex(RecordError, 'first-git-connection-pending'):
            self.setup.preview(self.root)
        subprocess.run([str(EXECUTABLE), 'init', '-q', str(self.root)], check=True)
        (self.root/'notes').write_bytes(b'keep staging')
        subprocess.run([str(EXECUTABLE), '-C', str(self.root), 'add', 'notes'], check=True)
        index = (self.root/'.git/index').read_bytes()
        with self.assertRaises(RecordError):
            self.setup.resume('first')
        entry = SimpleNamespace(lease=self.lease(), home=self.manager, git=lambda: self.fail('cancel should not invoke Git'))
        args = parser(bound=True).parse_args(['connect-cancel','first'])
        self.assertEqual('cancelled', run(args,entry)['state'])
        self.assertEqual('cancelled', cancel(self.setup, 'first')['state'])
        with self.assertRaisesRegex(RecordError,'first-git-cancelled'):
            self.setup.resume('first')
        self.assertEqual(index, (self.root/'.git/index').read_bytes())
        self.assertEqual('git', self.setup.preview(self.root)['plan']['topology']['kind'])
        self.assertNotIn(value['plan']['basis']['project'], self.manager.projects())

    def test_cancel_keeps_published_git_but_refuses_after_authority(self):
        from colvia.first_git import cancel
        self.begin_git()
        def stop(phase):
            if phase == 'first-git-published':
                raise InterruptedError()
        with self.assertRaises(InterruptedError):
            self.setup.resume('first', event=stop)
        identity = self.manager.files.directory_identity(self.root/'.git')
        self.assertEqual('cancelled', cancel(self.setup,'first')['state'])
        self.assertEqual(identity,self.manager.files.directory_identity(self.root/'.git'))
        self.assertEqual('git',self.setup.preview(self.root)['plan']['topology']['kind'])

    def test_cancel_after_entry_work_requires_resume(self):
        from colvia.first_git import cancel
        self.begin_git()
        def stop(phase):
            if phase == 'first-git-authority-ready':
                raise InterruptedError()
        with self.assertRaises(InterruptedError):
            self.setup.resume('first', event=stop)
        with self.assertRaisesRegex(RecordError,'first-git-cancel-too-late'):
            cancel(self.setup,'first')
        self.complete()

    def test_finished_inner_connection_survives_new_staging(self):
        self.begin_git()
        def interrupt(phase):
            if phase == 'first-git-files-connected':
                raise InterruptedError()
        with self.assertRaises(InterruptedError):
            for _ in range(8):
                self.setup.resume('first', event=interrupt)
        (self.root/'notes').write_bytes(b'new work')
        subprocess.run([str(EXECUTABLE), '-C', str(self.root), 'add', '--', 'notes'], check=True)
        index = (self.root/'.git/index').read_bytes()
        self.complete()
        self.assertEqual(index, (self.root/'.git/index').read_bytes())

    def test_existing_connection_and_git_prerequisite(self):
        plain=ProjectSetup(self.manager)
        self.assertTrue(plain.preview(self.root)['git_choice_available'])
        with self.assertRaisesRegex(RecordError,'git-prerequisite-required'):plain.preview(self.root,init_git=True)
        self.begin();self.finish()
        with self.assertRaises(RecordError):self.setup.preview(self.root,init_git=True)
        self.assertFalse((self.root/'.git').exists())

    def test_git_choice_is_hidden_when_operation_home_overlaps(self):
        child = self.manager.root/'inside'
        child.mkdir()
        value = self.setup.preview(child)
        self.assertFalse(value['git_choice_available'])
        self.assertEqual('effect-staging-overlaps-workspace', value['git_choice_unavailable_reason'])
        with self.assertRaisesRegex(RecordError, 'effect-staging-overlaps-workspace'):
            self.setup.preview(child, init_git=True)

    def test_ineligible_volume_hides_git_choice(self):
        from colvia.platforms.observation_port import location
        original = location(self.manager.root)
        alternate = SimpleNamespace(volume=original.volume + '-other')
        with patch('colvia.first_git.location',return_value=alternate):
            offer = self.setup.preview(self.root)
            self.assertFalse(offer['git_choice_available'])
            self.assertEqual('effect-staging-volume-mismatch', offer['git_choice_unavailable_reason'])

    def test_old_git_default_branch_normalized_privately(self):
        from colvia.first_git import run as real_run
        def old_init(*args, **kwargs):
            result = real_run(*args, **kwargs)
            self.assertFalse((self.root/'.git').exists())
            (kwargs['cwd']/'.git/HEAD').write_bytes(b'ref: refs/heads/master\n')
            return result
        self.begin_git()
        with patch('colvia.first_git.run', side_effect=old_init):
            self.complete()
        self.assertEqual(b'ref: refs/heads/main', (self.root/'.git/HEAD').read_bytes().strip())

    def test_existing_repository_keeps_standard_preview(self):
        subprocess.run([str(EXECUTABLE),'init','-q',str(self.root)],check=True)
        self.assertNotIn('git_choice_available',self.setup.preview(self.root))
        with self.assertRaisesRegex(RecordError,'first-git-unconnected-folder-required'):
            self.setup.preview(self.root,init_git=True)
