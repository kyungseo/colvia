"""Exercise registration through the manager with real synthetic Git state."""
import contextlib
import hashlib
import io
import json
import shlex
import shutil
import unittest
from unittest.mock import patch

from colvia.codec import RecordError, canonical_bytes, decode_canonical
from colvia.management import ManagerHome
from colvia.managed_entry import ManagedEntry
from colvia.manager_entry import main
from test_foundation_git import GitFixture
import test_foundation_slots as slot_fixture


class GitRegistrationTests(GitFixture, unittest.TestCase):
    slot = slot_fixture.SlotTests.slot

    def setUp(self):
        super().setUp()
        self.management = ManagerHome.create(self.home / 'manager', os_name='macos', architecture='arm64')
        self.manager = self.management.slots
        selected = self.slot('one', 1)
        self.manager.initialize(selected)
        native = self.management.root / 'bin' / 'colvia'
        native.parent.mkdir(mode=0o700)
        native.write_bytes(b'synthetic entry')
        native.chmod(0o700)
        self.management.files.create(self.management.root / 'entry.json', canonical_bytes(dict(
            version=1, os='macos', architecture='arm64', sha256=hashlib.sha256(native.read_bytes()).hexdigest())))
        runtime = (str(self.manager.root / 'slots/one/python'), '3.14.7', '3.54.0')
        with patch('colvia.managed_entry.process_runtime', return_value=runtime):
            self.entry = ManagedEntry(self.management.root, pointer=selected)
        self.registry = self.management.root / 'tools.json'

    def manager_command(self, *arguments):
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            code = main(['--json', *map(str, arguments)], entry=self.entry)
        return code, output.getvalue()

    def preview(self, path, name='registration.json'):
        with patch('colvia.adapters.git.run', side_effect=AssertionError('preview launched Git')):
            code, raw = self.manager_command('git-register-preview', path)
        self.assertEqual(0, code, raw)
        result = decode_canonical(raw.encode())
        target = self.home / name
        target.write_bytes(raw.encode())
        return target, result['receipt']

    def apply(self, path, receipt, *extra):
        code, raw = self.manager_command('git-register', '--plan', path, '--receipt', receipt, *extra)
        return code, json.loads(raw)

    def test_registration_and_real_connection_preserve_staging(self):
        for name in ('delete.md', 'rename.md', 'lines.txt'):
            (self.root / name).write_bytes(b'baseline\n')
        self.command('add', 'delete.md', 'rename.md', 'lines.txt')
        self.command('commit', '-qm', 'Additional synthetic fixture')
        linked = self.home / 'linked'
        self.command('worktree', 'add', '-qb', 'linked', str(linked))
        self.command('config', 'core.autocrlf', 'true')
        (self.root / 'report.md').write_bytes(b'staged\n')
        self.command('add', 'report.md')
        (self.root / 'report.md').write_bytes(b'unstaged after partial staging\n')
        self.command('rm', 'delete.md')
        self.command('mv', 'rename.md', 'renamed.md')
        (self.root / 'intent.md').write_bytes(b'new body\n')
        self.command('add', '-N', 'intent.md')
        (self.root / 'lines.txt').write_bytes(b'baseline\r\n')
        (self.root / 'untracked.md').write_bytes(b'untracked\n')
        (self.root / '.git' / 'info' / 'exclude').write_text('ignored.md\n', encoding='utf-8')
        (self.root / 'ignored.md').write_bytes(b'ignored\n')
        (linked / 'report.md').write_bytes(b'linked unstaged\n')

        gitdir = self.root / '.git'

        def inventory(folder):
            return {path.relative_to(folder).as_posix(): path.read_bytes()
                    for path in folder.rglob('*') if path.is_file()}

        def state():
            return tuple((self.command('--no-optional-locks', 'rev-parse', 'HEAD', root=path),
                          self.command('--no-optional-locks', 'diff', '--cached', '--binary', root=path),
                          self.command('--no-optional-locks', 'diff', '--binary', root=path))
                         for path in (self.root, linked))

        before_project = {path: path.read_bytes() for folder in (self.root, linked)
                          for path in folder.iterdir() if path.is_file()}
        before_git = inventory(gitdir)
        before_state = state()
        code, raw = self.manager_command('connect-preview', self.root)
        self.assertEqual((2, 'git-prerequisite-required'), (code, json.loads(raw)['error']))
        receipt_path, receipt = self.preview(self.git.executable)
        self.assertFalse(self.registry.exists())
        code, result = self.apply(receipt_path, 'wrong')
        self.assertEqual((2, 'git-registration-review-changed'), (code, result['error']))
        code, result = self.apply(receipt_path, receipt)
        self.assertEqual((0, 'registered'), (code, result['state']))
        self.assertEqual(self.git.sha256, result['sha256'])
        stream = io.BytesIO()
        with io.TextIOWrapper(stream, encoding='utf-8', newline='\r\n') as stdout:
            with contextlib.redirect_stdout(stdout):
                code = main(['--json', 'connect-preview', str(self.root)], entry=self.entry)
            stdout.flush()
            raw = stream.getvalue()
        self.assertEqual(0, code, raw)
        preview = json.loads(raw)
        self.assertEqual(before_git, inventory(gitdir))
        self.assertEqual(before_state, state())
        connect_path = self.home / 'connection.json'
        for bad_plan, receipt, error in (
            (b' ' + raw, preview['receipt'], 'noncanonical-json'),
            (canonical_bytes(preview), 'wrong', 'connect-review-changed'),
        ):
            connect_path.write_bytes(bad_plan)
            code, failure = self.manager_command('connect', '--plan', connect_path, '--receipt',
                                                 receipt, '--statement', 'Connect test', '--operation', 'refused')
            self.assertEqual((2, error), (code, json.loads(failure)['error']))
        self.assertEqual(before_git, inventory(gitdir))
        self.assertEqual(before_state, state())
        self.assertEqual(before_project, {path: path.read_bytes() for folder in (self.root, linked)
                                          for path in folder.iterdir() if path.is_file()})
        self.assertFalse(self.management.projects())
        connect_path.write_bytes(raw)
        code, raw = self.manager_command('connect', '--plan', connect_path, '--receipt',
                                         preview['receipt'], '--statement', 'Connect test', '--operation', 'connect')
        self.assertEqual((0, 'connected'), (code, json.loads(raw).get('state')), raw)
        after_git = inventory(gitdir)
        self.assertEqual({'colvia/connection.json'}, after_git.keys() - before_git.keys())
        self.assertEqual(before_git, {name: after_git[name] for name in before_git})
        self.assertEqual(before_state, state())
        after_project = {path: path.read_bytes() for folder in (self.root, linked)
                         for path in folder.iterdir() if path.is_file()}
        self.assertEqual({self.root / name for name in ('AGENTS.md', 'CLAUDE.md', 'colvia')},
                         after_project.keys() - before_project.keys())
        self.assertEqual(before_project, {path: after_project[path] for path in before_project})
        self.assertEqual(self.entry.git().topology(self.root).common, self.entry.git().topology(linked).common)
        self.assertNotEqual(self.entry.git().topology(self.root).gitdir, self.entry.git().topology(linked).gitdir)

    def test_preview_stdout_is_canonical_even_with_crlf_text_stdout(self):
        stream = io.BytesIO()
        stdout = io.TextIOWrapper(stream, encoding='utf-8', newline='\r\n')
        with contextlib.redirect_stdout(stdout):
            self.assertEqual(0, main(['git-register-preview', str(self.git.executable)], entry=self.entry))
        stdout.flush()
        self.assertEqual('preview', decode_canonical(stream.getvalue())['state'])
        self.assertNotIn(b'\r', stream.getvalue())

    def test_executable_changes_are_refused_before_canary_runs(self):
        candidate = self.home / 'git-copy'
        shutil.copyfile(self.git.executable, candidate)
        candidate.chmod(0o700)
        plan, receipt = self.preview(candidate)
        marker = self.home / 'executed'
        candidate.write_text('#!/bin/sh\n: > ' + shlex.quote(str(marker)) + '\necho git version fake\n', encoding='utf-8')
        code, result = self.apply(plan, receipt)
        self.assertEqual((2, 'git-registration-review-changed'), (code, result['error']))
        self.assertFalse(self.registry.exists())
        self.management.files.create(self.registry, canonical_bytes(dict(
            version=1, git=dict(path=str(candidate), sha256=self.git.sha256, version=self.git.version))))
        with self.assertRaisesRegex(RecordError, 'managed-git-changed'):
            self.entry.git()
        self.assertFalse(marker.exists())

    def test_post_write_readback_failure_reports_unknown_outcome(self):
        plan, receipt = self.preview(self.git.executable)
        files = self.entry.home.files
        read = files.read

        def fail_after_publication(path, *args, **kwargs):
            if path == self.registry and path.exists():
                raise OSError('synthetic readback failure')
            return read(path, *args, **kwargs)

        with patch.object(files, 'read', side_effect=fail_after_publication):
            code, result = self.apply(plan, receipt)
        self.assertEqual((2, 'git-registration-outcome-unknown'), (code, result['error']))
        self.assertEqual(self.git.sha256, decode_canonical(self.registry.read_bytes())['git']['sha256'])

    def test_receipt_expires_and_replacement_requires_confirmation(self):
        plan, receipt = self.preview(self.git.executable)
        with patch('colvia.git_registration.time.time', return_value=decode_canonical(plan.read_bytes())['plan']['expires_at']):
            code, result = self.apply(plan, receipt)
        self.assertEqual((2, 'git-registration-review-changed'), (code, result['error']))
        self.assertEqual(0, self.apply(plan, receipt)[0])
        before = self.registry.read_bytes()
        same, same_receipt = self.preview(self.git.executable, 'same.json')
        self.assertEqual('already-registered', self.apply(same, same_receipt)[1]['state'])
        self.assertEqual(before, self.registry.read_bytes())
        alternate = self.home / 'alternate-git'
        alternate.write_text('#!/bin/sh\necho git version synthetic\n', encoding='utf-8')
        alternate.chmod(0o700)
        replacement, replace_receipt = self.preview(alternate, 'replacement.json')
        code, result = self.apply(replacement, replace_receipt)
        self.assertEqual((2, 'git-registration-replacement-required'), (code, result['error']))
        self.assertEqual(before, self.registry.read_bytes())
        self.assertEqual('registered', self.apply(replacement, replace_receipt, '--replace')[1]['state'])
        self.assertEqual(str(alternate), self.entry.git().executable.as_posix())
        self.assertEqual(2, self.apply(replacement, replace_receipt, '--replace')[0])
