from contextlib import redirect_stdout
from io import StringIO
import base64
import json
import unittest
from unittest.mock import Mock, patch

from colvia import cli

from colvia.credentials import GitContentRefusal, inspect_chunks, screen_candidate
from colvia.codec import RecordError
from colvia.git_integration import key
from colvia.effects import PENDING
from colvia.presentation import human
from test_foundation_git_candidate import AUTHOR
from test_foundation_git_integration import IntegrationFixture
from test_foundation_windows_git import WindowsFixture


class CredentialTests(unittest.TestCase):
    def test_cli_displays_readable_finding_and_preserves_machine_category(self):
        cases = (
            ('key-or-token', '키·토큰', 12),
            ('url-credential', 'URL에 넣은 비밀번호', 2),
            ('npm-auth-literal', '.npmrc 인증값', 1),
            ('credential-assignment', '설정에 직접 적은 비밀값', 5),
            ('protected-path', None, None),
            ('protected-copy', None, None),
            ('uninspectable', None, None),
            ('future-category', None, None),
        )
        entry = Mock()
        entry.workspace.return_value = (Mock(), Mock(), Mock())
        synthetic_value = 'sk-' + 'x' * 20
        inputs = {
            'key-or-token': ('app.py', synthetic_value),
            'url-credential': ('config', 'https://user:fixture-value@host.invalid/'),
            'npm-auth-literal': ('.npmrc', '_authToken=fixture-value'),
            'credential-assignment': ('config', 'password=fixture-value'),
        }
        for category, label, line in cases:
            location = 'example.conf'
            if category in inputs:
                location, text = inputs[category]
                with self.assertRaises(GitContentRefusal) as caught:
                    inspect_chunks([b'\n' * (line - 1) + text.encode()], location)
                error = caught.exception
            else:
                error = GitContentRefusal(category, location, line)
            details = [f'"{location}"']
            if line is not None:
                details.append(f'{line}행')
            if label:
                details.append(label)
            suffix = '(' + ', '.join(details) + ')'
            for as_json in (False, True):
                with self.subTest(category=category, json=as_json):
                    output = StringIO()
                    args = (['--json'] if as_json else []) + ['ordinary', 'list']
                    with patch.object(cli, 'dispatch', side_effect=error), redirect_stdout(output):
                        self.assertEqual(cli.main(args, entry=entry), 2)
                    message = output.getvalue().strip()
                    self.assertNotIn(synthetic_value, message)
                    self.assertNotIn('fixture-value', message)
                    if as_json:
                        receipt = json.loads(message)
                        self.assertEqual(receipt['finding'], dict(category=category, location=location, line=line))
                        message = receipt['message']
                    self.assertIn(suffix, message)
                    self.assertNotIn(category, message)

    def test_exact_paths_and_template_content(self):
        def screen(path, payload):
            screen_candidate({path: {}}, payload, 'Update', {}, 'test')
        for path in ('.env', 'app/.env.local', 'app/.ENV.PRODUCTION', 'secrets/value',
                     'app/Secrets/nested/.env.example', 'secrets/.env.template'):
            with self.subTest(path=path), self.assertRaises(GitContentRefusal) as caught:
                screen(path, lambda _: self.fail('protected file opened for content screening'))
            self.assertEqual(caught.exception.code, 'git-protected-path')
        for path in ('app/.env.example', '.env.template', 'mysecrets/data', 'secrets.md', '.env.test'):
            with self.subTest(path=path):
                screen(path, lambda _: [b'API_KEY=${VALUE}'])
                with self.assertRaisesRegex(GitContentRefusal, 'git-credential-blocked'):
                    screen(path, lambda _: [b'API_KEY=synthetic-only'])
        screen_candidate({'secrets/nested/value': None}, lambda _: self.fail('deleted body opened'), 'Remove', {}, 'test')

    def test_developer_credential_paths(self):
        for path in ('.netrc', 'client/_NETRC', 'ops/prod.tfstate', 'Prod.TFSTATE.BACKUP',
                     'nested/terraform.tfstate.1700000000.backup'):
            with self.subTest(path=path), self.assertRaisesRegex(GitContentRefusal, 'git-protected-path'):
                screen_candidate({path: {}}, lambda _: self.fail('read protected payload'), 'Add', {}, 'trial')
        for path in ('.netrc.example', 'main.tf', 'safe.tfvars', 'test.tfstate.json', 'main.tfstate.docs.backup'):
            screen_candidate({path: {}}, lambda _: [b'normal data'], 'Add', {}, 'trial')

    def test_npm_auth_literals_and_references(self):
        scope = '//registry.invalid:8443/team/:'
        for field in ('_authToken', '_auth', '_password', 'password', 'key'):
            for prefix in ('', scope):
                name = prefix + field
                for literal in ('synthetic-value', '"synthetic;value"', "'synthetic#value'", '${VAR}suffix',
                                '${VAR:-fallback}', r'\${VAR}', '"${VAR}" ; "literal"'):
                    with self.subTest(field=name, value=literal), self.assertRaises(GitContentRefusal) as refusal:
                        inspect_chunks([(name + '=' + literal).encode()], 'app/.NPMRC')
                    self.assertNotIn('synthetic', str(refusal.exception.finding))
                for value in ('', '${NPM_TOKEN}', '"${NPM_TOKEN?}"', "'${NPM_TOKEN}'", '${TOKEN} ; comment'):
                    inspect_chunks([(name + '=' + value).encode()], 'app/.npmrc')
        with self.assertRaisesRegex(GitContentRefusal, 'git-credential-blocked'):
            inspect_chunks([b'_authToken=${TOKEN} ; DB_PASSWORD=synthetic'], '.npmrc')
        for name in (scope + '_authToken[]', '"' + scope + '_authToken"', '"_auth\\u0054oken"'):
            with self.assertRaises(GitContentRefusal):
                inspect_chunks([(name + '=synthetic-only').encode()], '.npmrc')
        for key in (' \ufeff_authToken', '_authToken\ufeff', r'//registry.invalid/part\#name/:_authToken'):
            with self.assertRaises(GitContentRefusal):
                inspect_chunks([(key + '=synthetic').encode()], '.npmrc')
        with self.assertRaises(GitContentRefusal) as found:
            inspect_chunks([('\ufeff[section]\r\n' + scope + '_authToken=synthetic\r\n' +
                             scope + '_authToken=' + '${TOKEN}').encode()], '.npmrc')
        self.assertEqual(found.exception.finding, dict(category='npm-auth-literal', location='.npmrc', line=2))
        with self.assertRaisesRegex(GitContentRefusal, 'git-content-uninspectable'):
            inspect_chunks([b'registry=public\r_authToken=synthetic'], '.npmrc')
        inspect_chunks([b'registry=https://registry.invalid\nkeyfile=/path/to/key.pem\n; example'], '.npmrc')

    def test_split_tokens_and_unicode_lines(self):
        key = b'ghp_' + b'A' * 30
        content = '설정\r\n'.encode() + key
        for cut in range(len(content) + 1):
            with self.assertRaises(GitContentRefusal) as error:
                inspect_chunks([content[:cut], content[cut:]], 'config')
            self.assertEqual(error.exception.finding, dict(category='key-or-token', location='config', line=2))
            self.assertNotIn(key.decode(), str(error.exception))

    def test_literals_and_supported_references(self):
        for text in ['DB_PASSWORD="short"', '{"api_key":"example-secret"}', '{"api_key":\r\n "example-secret"}',
                     'https://bob:example-password@localhost/x', '-----BEGIN PRIVATE KEY-----',
                     'api_key=' + chr(36) + '{ENV}literal', 'token = ' + 'github_pat_' + 'a'*24]:
            with self.subTest(text=text), self.assertRaises(GitContentRefusal):
                inspect_chunks([text.encode()], 'message')
        for text in ['api_key=' + chr(36) + '{ENV}', 'password=""', 'password=%MY_SECRET%',
                     'Contact me@example.org', 'A task-management-system',
                     'API_KEY=<your-api-key>']:
            inspect_chunks([text.encode()], 'ordinary')

    def test_ordinary_source_and_configuration(self):
        for path, text in [
            ('app.py', 'if not password:\n    raise ValueError()'),
            ('app.py', 'def f(password: str):\n    return password == hashed'),
            ('app.py', 'password=None\napi_key = os.getenv("TOKEN")'),
            ('script.js', 'password: string;\npassword = process.env.NAME'),
            ('pipeline.yml', 'password: ${{ secrets.PASSWORD }}'),
            ('config.json', '{"password": {"type": "string"}, "token": null}'),
            ('app.py', '''password = request.form['password']'''),
            ('app.py', '''api_key = config["api_key"]'''),
            ('app.py', 'token = jwt.encode(payload, key)'),
            ('script.js', '''token = localStorage.getItem('token')'''),
            ('schema.yml', 'password:\n  type: string'),
            ('guide.md', 'This example uses Bearer authentication.')]:
            with self.subTest(path=path, text=text):
                inspect_chunks([text.encode()], path)
        for text in ['{"password":{"api_key":"nested-secret"}}', 'SECRET_KEY="demo-only"', 'aws_secret_access_key: dummy',
                     'auth_token=synthetic', 'password=${VAR:-literal}',
                     'sk_live_' + 'S' * 18, '-----BEGIN PGP PRIVATE KEY BLOCK-----',
                     'sk-' + '1' * 18, 'AKIA' + 'Z' * 16, 'Authorization: Bearer ' + 'T' * 20,
                     'password:\n  # comment\n  synthetic-literal']:
            with self.assertRaises(GitContentRefusal):
                inspect_chunks([text.encode()], 'settings.env')

    def test_asset_signatures_and_extensions(self):
        examples = {
            'logo.PNG': ('PNG', b'\x89PNG\r\n\x1a\n'),
            'photo.jpeg': ('JPEG', b'\xff\xd8\xff'), 'photo.jpg': ('JPEG', b'\xff\xd8\xff'),
            'badge.gif': ('GIF', b'GIF89a'), 'old.gif': ('GIF', b'GIF87a'),
            'cover.webp': ('WebP', b'RIFF1234WEBP'), 'favicon.ico': ('ICO', b'\0\0\1\0'),
            'font.woff': ('WOFF', b'wOFF'), 'font.woff2': ('WOFF2', b'wOF2'),
            'font.ttf': ('TTF', b'\0\1\0\0'), 'font.otf': ('OTF', b'OTTO'),
        }
        for path, (kind, prefix) in examples.items():
            with self.subTest(path=path):
                parts = [prefix[:1], prefix[1:], b'synthetic payload']
                self.assertEqual(screen_candidate({path: {}}, lambda _: iter(parts), 'Add', {}, 'trial'), {path: kind})
                with self.assertRaisesRegex(GitContentRefusal, 'uninspectable'):
                    screen_candidate({path: {}}, lambda _: [b'ordinary text'], 'Add', {}, 'trial')
        for path in ('file.p12', 'file.pfx', 'file.jks', 'file.keystore'):
            with self.subTest(path=path), self.assertRaisesRegex(GitContentRefusal, 'git-protected-path'):
                screen_candidate({path: {}}, lambda _: self.fail('opened protected keystore'), 'Add', {}, 'trial')
        for path in ('file.zip', 'file.DB', 'app.exe', 'file.pdf'):
            with self.subTest(path=path), self.assertRaisesRegex(GitContentRefusal, 'uninspectable'):
                screen_candidate({path: {}}, lambda _: [b'plain text'], 'Add', {}, 'trial')
        for path, data, code in (
            ('bad.webp', b'RIFF1234WAVE', 'uninspectable'),
            ('logo.png', b'PASSWORD=synthetic', 'uninspectable'),
            ('secrets/logo.png', examples['logo.PNG'][1], 'git-protected-path'),
            ('logo.svg', b'<svg>\npassword=synthetic-value\n</svg>', 'git-credential-blocked'),
            ('min.js', b'x' * (256 * 1024 + 1), 'uninspectable'),
        ):
            with self.subTest(path=path), self.assertRaisesRegex(GitContentRefusal, code):
                screen_candidate({path: {}}, lambda _: [data], 'Add', {}, 'trial')
        self.assertEqual(screen_candidate({'min.css': {}}, lambda _: [b'x' * (256 * 1024)], 'Add', {}, 'trial'), {})

    def test_uninspectable(self):
        for raw in [b'\xff', b'\x00', b'%PDF-1.7', b'x' * (256*1024+1)]:
            with self.assertRaisesRegex(GitContentRefusal, 'git-content-uninspectable'):
                inspect_chunks([raw], 'ordinary')


class GateFixture:
    secret = b'ghp_' + b'SyntheticOnlyForTest12' * 2

    def record(self, files):
        self.start(tuple(files))
        for name, data in files.items():
            path = self.root / name
            if data is None:
                path.unlink()
            else:
                path.write_bytes(data)
        review = self.submit()
        self.service.accept(operation='accept', work='report', receipt=review['receipt'], statement='accept')

    def candidate(self, message='Update report'):
        return self.integration.prepare(operation='candidate', works=['report'], message=message, identity=AUTHOR)

    def state(self):
        return (self.command('rev-parse','HEAD'), (self.root/'.git/index').read_bytes(),
                sorted(p.relative_to(self.root) for p in (self.root/'.git/objects').rglob('*')),
                sorted(p.relative_to(self.scratch) for p in self.scratch.rglob('*')))

    def check_refusal(self, message, location):
        before = self.state()
        with self.assertRaises(GitContentRefusal) as found:
            self.candidate(message)
        self.assertEqual(found.exception.finding['location'], location)
        self.assertNotIn(self.secret.decode(), json.dumps(found.exception.finding))
        self.assertEqual(before, self.state())
        self.assertIsNone(self.store.head(key('candidate')))
        self.assertIsNone(self.store.head(PENDING))
        self.assertFalse((self.root/'.git/index.lock').exists())

    def cleanup_change(self, original, replacement, name='report.md'):
        (self.root/name).write_bytes(original)
        self.command('add',name)
        self.command('commit','-m','Synthetic starting point')
        (self.root/'other').write_bytes(b'keep staged')
        self.command('add','other')
        self.record({name:replacement, 'notes.md':b'clean companion\n'})
        view = self.candidate()
        diff = base64.b64decode(view['diff_base64'])
        self.assertIn(b'previous content withheld', diff)
        self.assertIn(b'clean companion', diff)
        self.assertNotIn(self.secret, diff)
        self.assertNotIn(self.secret.decode(), human(view))
        if replacement:
            self.assertIn(replacement, diff)
        else:
            self.assertIn(b'file deleted', diff)
        # Reopen old accepted content without capturing its raw bytes in child logs.
        outcome = self.integration.apply('candidate', receipt=view['receipt'], statement='apply')
        self.assertEqual(outcome['state'], 'completed')
        self.assertEqual(self.command('diff','--cached','--name-only'), b'other\n')
        for path in self.scratch.rglob('*'):
            if path.is_file():
                self.assertNotIn(self.secret, path.read_bytes(), path.name)

class IntegrationTests(GateFixture, IntegrationFixture, unittest.TestCase):
    def test_image_and_source_share_a_reviewed_candidate(self):
        image = base64.b64decode('iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+jRZkAAAAASUVORK5CYII=')
        (self.root/'other').write_bytes(b'keep staged')
        self.command('add', 'other')
        self.record({'logo.png': image, 'report.md': b'updated summary\n'})
        view = self.candidate()
        self.assertEqual(view['unchecked_assets'], {'logo.png': 'PNG'})
        self.assertIn('내용 검사 안 함: "logo.png" (PNG)', human(view))
        diff = base64.b64decode(view['diff_base64'])
        self.assertNotIn(b'IHDR', diff)
        self.assertIn(b'updated summary', diff)
        self.assertEqual(view, self.integration.preview('candidate'))
        self.assertEqual(self.integration.apply('candidate', receipt=view['receipt'], statement='apply')['state'], 'completed')
        self.assertEqual(self.command('show','HEAD:logo.png'), image)
        self.assertEqual(self.command('diff','--cached','--name-only'), b'other\n')
        self.assertEqual(self.integration.preview('candidate')['unchecked_assets'], {'logo.png':'PNG'})

    def test_deleted_keystore_hides_old_plaintext(self):
        self.secret = b'synthetic private contents'
        self.cleanup_change(self.secret, None, 'project.p12')

    def test_deleted_env_exact_copy_as_image_stops_before_writes(self):
        image = b'\x89PNG\r\n\x1a\n' + b'synthetic private data'
        (self.root/'.env').write_bytes(image)
        self.command('add', '.env')
        self.command('commit', '-m', 'Synthetic protected file')
        self.record({'.env': None, 'logo.png': image})
        before = self.state()
        with self.assertRaisesRegex(GitContentRefusal, 'git-protected-copy'):
            self.candidate()
        after = self.state()
        self.assertEqual(before[:3], after[:3])  # HEAD, index and Git objects
        self.assertFalse((self.scratch/'candidate').exists())
        self.assertIsNone(self.store.head(key('candidate')))
        self.assertIsNone(self.store.head(PENDING))
        for relative in set(after[3]) - set(before[3]):
            audit_path = self.scratch/relative
            if audit_path.is_file():
                self.assertNotIn(image, audit_path.read_bytes())

    def test_old_keystore_deletion_requires_new_approval(self):
        self.assert_old_deletion_refused('project.p12', b'Colvia Git review v3\n')

    def test_ordinary_image_move_keeps_the_review_note(self):
        image = b'GIF89a' + b'synthetic image bytes'
        (self.root/'old.gif').write_bytes(image)
        self.command('add', 'old.gif')
        self.command('commit', '-m', 'Synthetic image')
        self.record({'old.gif': None, 'new.gif': image})
        view = self.candidate()
        self.assertEqual(view['unchecked_assets'], {'new.gif': 'GIF'})
        diff = base64.b64decode(view['diff_base64'])
        self.assertNotIn(image, diff)
        self.assertIn(b'"old.gif"', diff)
        self.assertIn(b'file deleted', diff)

    def test_directory_replaced_by_asset_keeps_child_deletion_visible(self):
        from types import SimpleNamespace
        parent = self.root/'logo.png'
        parent.mkdir()
        child = parent/'note.txt'
        child.write_text('old note')
        self.command('add', 'logo.png')
        self.command('commit', '-m', 'Original folder')
        old_tree = self.command('rev-parse', 'HEAD^{tree}').decode().strip()
        head = self.port.tree(old_tree, 'sha1')
        child.unlink()
        parent.rmdir()
        image = b'\x89PNG\r\n\x1a\n' + b'synthetic image bytes'
        parent.write_bytes(image)
        self.command('add', 'logo.png')
        self.command('commit', '-m', 'Replacement image')
        new_tree = self.command('rev-parse', 'HEAD^{tree}').decode().strip()
        after = {'logo.png': SimpleNamespace(native=b'logo.png'), 'logo.png/note.txt': None}
        diff = self.port.review_diff(old_tree, new_tree, head, after, lambda _: [image], {'logo.png': 'PNG'})
        self.assertIn(b'"logo.png/note.txt"', diff)
        self.assertIn(b'file deleted', diff)
        self.assertNotIn(image, diff)

    def test_old_image_preview_requires_new_approval(self):
        self.record({'logo.png': b'\x89PNG\r\n\x1a\n' + b'synthetic content'})
        with patch.object(self.port, 'review_diff', return_value=b'Colvia Git review v3\n'), patch.object(self.integration, '_screen_plan'):
            old = self.candidate()
        for call in (lambda: self.integration.preview('candidate'),
                     lambda: self.integration.apply('candidate', receipt=old['receipt'], statement='apply')):
            with self.assertRaisesRegex(RecordError, 'git-credential-new-preview-required'):
                call()
        self.assertIsNone(self.store.head(PENDING))

    def test_npm_literal_blocks_before_objects(self):
        self.record({'.npmrc': b'//registry.invalid/:_authToken=unstructured-synthetic'})
        self.check_refusal('Update', '.npmrc')

    def test_npm_replacement_hides_old_value(self):
        self.secret = b'unstructured-synthetic'
        self.cleanup_change(b'//registry.invalid/:_authToken=' + self.secret,
                            b'//registry.invalid/:_authToken=${TOKEN}\n', '.npmrc')

    def test_tfstate_backup_deletion_hides_plaintext(self):
        self.secret = b'unstructured-state-value'
        self.cleanup_change(self.secret, None, 'prod.tfstate.backup')

    def test_old_v2_preview_of_deleted_netrc_is_refused(self):
        self.assert_old_deletion_refused('.netrc', b'Colvia Git review v2\n')

    def test_replaced_npm_secret_cannot_be_copied_verbatim(self):
        self.assert_move_refused('.npmrc', b'_authToken=unstructured-synthetic', b'_authToken=${NPM_TOKEN}')

    def test_removed_npm_secret_cannot_be_moved_verbatim(self):
        self.assert_move_refused('.npmrc', b'_authToken=unstructured-synthetic')

    def test_env_add_is_refused_before_objects(self):
        self.record({'.env': b'PORT=8080'})
        self.check_refusal('Update', '.env')

    def test_env_edit_is_refused_before_objects(self):
        (self.root / '.env.local').write_text('PORT=8080')
        self.command('add', '.env.local')
        self.command('commit', '-m', 'Synthetic original')
        self.record({'.env.local': b'PORT=8081'})
        self.check_refusal('Update', '.env.local')

    def test_protected_deletion_without_recognizable_token(self):
        self.secret = b'synthetic-opaque-line-without-recognizable-shape'
        (self.root / 'secrets').mkdir()
        self.cleanup_change(self.secret, None, 'secrets/data')

    def test_protected_move_does_not_reprint_deleted_bytes(self):
        self.assert_move_refused('.env', b'synthetic-opaque-line')

    def assert_move_refused(self, name, payload, replacement=None):
        path = self.root / name
        path.write_bytes(payload)
        self.command('add', name)
        self.command('commit', '-m', 'Synthetic original')
        self.record({name: replacement, 'new.txt': payload})
        objects = self.state()[2]
        with self.assertRaisesRegex(GitContentRefusal, 'git-protected-copy'):
            self.candidate()
        self.assertEqual(objects, self.state()[2])
        self.assertIsNone(self.store.head(key('candidate')))
        for p in self.scratch.rglob('*'):
            if p.is_file():
                self.assertNotIn(payload, p.read_bytes())

    def test_old_v1_preview_of_deleted_protected_file_is_refused(self):
        self.assert_old_deletion_refused('.env', b'Colvia Git review v1\n')

    def assert_old_deletion_refused(self, name, header):
        payload = b'unrecognized-synthetic-text'
        (self.root / name).write_bytes(payload)
        self.command('add', name)
        self.command('commit', '-m', 'Synthetic original')
        self.record({name: None})
        old_patch = header + b'-' + payload
        with patch.object(self.port, 'review_diff', return_value=old_patch), patch.object(self.integration, '_screen_plan'):
            old = self.candidate()
        for call in (lambda: self.integration.preview('candidate'),
                     lambda: self.integration.apply('candidate', receipt=old['receipt'], statement='apply')):
            with self.assertRaisesRegex(RecordError, 'git-credential-new-preview-required'):
                call()
        self.assertIsNone(self.store.head(PENDING))

    def test_last_file_blocks_before_any_candidate_effect(self):
        self.record({'report.md':b'clean first', 'zz.txt':self.secret})
        self.check_refusal('Update', 'zz.txt')

    def test_message_blocks_before_any_candidate_effect(self):
        self.record({'report.md':b'clean'})
        self.check_refusal(self.secret.decode(), 'commit-message')

    def test_remove_secret_and_keep_new_content(self):
        self.cleanup_change(self.secret + b'\n', b'clean replacement\n')

    def test_remove_uninspectable_binary(self):
        self.cleanup_change(b'\x00' + self.secret, None)

    def test_workspace_change_during_preflight_refuses_before_writes(self):
        self.record({'report.md':b'reviewed'})
        original = self.integration._screen
        def change(*args):
            original(*args)
            (self.root/'report.md').write_bytes(b'changed after check')
        before = self.command('rev-parse','HEAD')
        with patch.object(self.integration, '_screen', side_effect=change), self.assertRaisesRegex(RecordError, 'accepted-files-changed'):
            self.candidate()
        self.assertEqual(before, self.command('rev-parse','HEAD'))
        self.assertIsNone(self.store.head(key('candidate')))
        self.assertFalse((self.scratch/'candidate').exists())

    def test_file_replaced_by_directory_displays_new_child(self):
        from types import SimpleNamespace
        path = self.root / 'foo'
        path.write_bytes(self.secret)
        self.command('add', 'foo')
        self.command('commit', '-m', 'Synthetic original')
        old_tree = self.command('rev-parse', 'HEAD^{tree}').decode().strip()
        head = self.port.tree(old_tree, 'sha1')
        path.unlink()
        path.mkdir()
        child = path / 'new.txt'
        child.write_bytes(b'line1\nline2')
        self.command('add', 'foo')
        self.command('commit', '-m', 'Synthetic replacement')
        new_tree = self.command('rev-parse', 'HEAD^{tree}').decode().strip()
        after = {'foo': None, 'foo/new.txt': SimpleNamespace(mode=0o100644)}
        preview = self.port.review_diff(old_tree, new_tree, head, after, lambda _: [child.read_bytes()])
        self.assertNotIn(self.secret, preview)
        self.assertIn(b'"foo/new.txt"', preview)
        self.assertIn(b'+line1\n+line2', preview)

    def test_legacy_old_secret_deletion_requires_new_confirmation(self):
        (self.root/'report.md').write_bytes(self.secret)
        self.command('add', 'report.md')
        self.command('commit', '-m', 'Synthetic original')
        self.record({'report.md':b'clean replacement'})
        # Simulate the old candidate format, where the removed line was stored.
        with patch.object(self.port, 'review_diff', return_value=b'diff --git a/report.md b/report.md\n-' + self.secret), \
             patch.object(self.integration, '_screen_plan'):
            old = self.candidate()
        for call in [lambda: self.integration.preview('candidate'),
                     lambda: self.integration.apply('candidate', receipt=old['receipt'], statement='apply')]:
            with self.assertRaisesRegex(RecordError, 'git-credential-new-preview-required'):
                call()
        self.assertIsNone(self.store.head(PENDING))
        fresh = self.integration.prepare(operation='clean-preview', works=['report'], message='Remove', identity=AUTHOR)
        self.assertIn(b'previous content withheld', base64.b64decode(fresh['diff_base64']))

    def test_clean_legacy_receipt_remains_usable(self):
        self.record({'report.md':b'clean'})
        with patch.object(self.port, 'review_diff', return_value=b'diff --git a/report.md b/report.md\n+clean'):
            old = self.candidate()
        self.assertEqual(old, self.integration.preview('candidate'))
        self.assertEqual('completed', self.integration.apply('candidate', receipt=old['receipt'], statement='apply')['state'])
        with patch.object(self.port, 'read_objects', side_effect=AssertionError('completed history read Git')):
            summary = self.integration.preview('candidate')
        self.assertEqual('completed', summary['state'])
        self.assertTrue(summary['historical_diff_withheld'])
        self.assertNotIn('diff_base64', summary)

    def test_legacy_prepared_secret_cannot_be_shown_or_applied(self):
        self.record({'report.md':self.secret})
        with patch.object(self.integration, '_screen', return_value={}), patch.object(self.integration, '_screen_plan'), \
             patch.object(self.port, 'review_diff', return_value=b'diff --git a/report.md b/report.md\n+' + self.secret):
            old = self.candidate()
        for call in [lambda: self.integration.preview('candidate'),
                     lambda: self.integration.apply('candidate', receipt=old['receipt'], statement='apply')]:
            with self.assertRaises(GitContentRefusal):
                call()
        self.assertIsNone(self.store.head(PENDING))

    def test_started_legacy_effect_recovers_without_new_disclosure(self):
        (self.root / 'other').write_bytes(b'keep staged')
        self.command('add', 'other')
        self.record({'report.md': b'clean'})
        def interrupted(phase):
            if phase == 'ref-observed':
                raise RuntimeError('synthetic interruption')
        with patch.object(self.integration, '_screen', return_value={}), patch.object(self.integration, '_screen_plan'):
            view = self.candidate(self.secret.decode())
            with self.assertRaisesRegex(RuntimeError, 'synthetic interruption'):
                self.integration.apply('candidate', receipt=view['receipt'], statement='apply', event=interrupted)
        previous = {p for p in self.scratch.rglob('*') if p.is_file()}
        result = self.integration.recover('candidate', statement='confirm prior commit')
        self.assertEqual('completed', result['state'])
        self.assertEqual(b'other\n', self.command('diff', '--cached', '--name-only'))
        for path in self.scratch.rglob('*'):
            if path.is_file() and path not in previous:
                self.assertNotIn(self.secret, path.read_bytes(), path.name)


class WindowsGateTests(GateFixture, WindowsFixture, unittest.TestCase):
    def test_font_with_text_shows_unchecked_asset(self):
        font = b'wOF2' + b'synthetic font payload'
        self.record({'label.woff2': font, 'report.md': b'plain summary'})
        view = self.candidate()
        self.assertEqual(view['unchecked_assets'], {'label.woff2': 'WOFF2'})
        self.assertIn('내용 검사 안 함: "label.woff2" (WOFF2)', human(view))
        self.assertNotIn(font, base64.b64decode(view['diff_base64']))


    def test_last_file_is_refused_before_effect(self):
        self.record({'report.md': b'clean first', 'zz.txt': self.secret})
        self.check_refusal('Update', 'zz.txt')

    def test_windows_netrc_deletion_hides_plaintext(self):
        self.secret = b'unstructured-windows-value'
        self.cleanup_change(self.secret, None, '_netrc')

    def test_protected_env_deletion_keeps_staging_and_journal_clean(self):
        self.secret = b'ordinary-looking-synthetic-text'
        self.cleanup_change(self.secret, None, '.env.production')

    def test_cleanup_keeps_staging_and_journal_clean(self):
        self.cleanup_change(self.secret + b'\n', b'safe new text\n')
