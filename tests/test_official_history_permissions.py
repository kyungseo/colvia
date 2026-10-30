"""Read-only terminal journal observation; synthetic fixtures do not grant execution."""
from pathlib import Path
import hashlib
import json
import os
import stat
import tempfile
import unittest
from unittest import mock

from hv2ref import official_documents as documents, official_state as state, official_host
from hv2ref.errors import ContractError


def bytes_for(events):
    rows = []
    for kind, value in events:
        row = {'seq': len(rows) + 1, 'previous': rows[-1]['sha256'] if rows else '0' * 64,
               'kind': kind, 'value': value}
        row['sha256'] = documents.digest(documents.canonical(row))
        rows.append(row)
    return b''.join(documents.canonical(row) for row in rows)


class HistoryPermissionTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.target = Path(self.tmp.name).resolve()
        self.spec = {'target': str(self.target), 'documents': {'files': {}}, 'request': {'worker_limit': 5}}
        self.grant = state.digest(state.canonical(self.spec))
        self.root = state.capsule_path(self.target, self.grant)
        self.root.mkdir(parents=True, mode=0o700)
        state.publish(self.root / 'grant.json', {'record_type': 'official-execution-grant', 'schema_version': 1,
                                               'grant': self.grant, 'spec': self.spec})
        self.path = self.root / 'journal.jsonl'

    def events(self, status):
        events = [('granted', {'grant': self.grant})]
        if status == 'completed':
            for i in range(5):
                events += [('callback-reserved', {'callId': str(i)}), ('callback-completed', {'callId': str(i)})]
            events += [('seal', {})]
        if status == 'operator-resolved-unknown':
            events += [('terminal', {'status': 'unknown'})]
            head = json.loads(bytes_for(events).splitlines()[-1])['sha256']
            events += [('operator-resolved-unknown', {'grant': self.grant, 'journal_head': head, 'status': 'unknown',
                       'documents': {}, 'process_absence': True, 'action': 'record-unknown-resolution'})]
        elif status != 'incomplete':
            events += [('terminal', {'status': status})]
        return events

    def write(self, status='completed', mode=0o600, events=None):
        if self.path.exists(): self.path.chmod(0o600)
        self.path.write_bytes(bytes_for(self.events(status) if events is None else events))
        self.path.chmod(mode)

    def snapshot(self):
        return {p.name: (p.read_bytes(), stat.S_IMODE(p.stat().st_mode), p.stat().st_mtime_ns)
                for p in self.root.iterdir() if p.is_file()}

    def test_terminal_kinds_accept_only_readonly_history_without_mutation(self):
        for status in sorted(state.TERMINAL):
            for mode in (0o600, 0o644):
                with self.subTest(status=status, mode=oct(mode)):
                    self.write(status, mode); before = self.snapshot()
                    value = state.read_capsule(self.target, self.grant)
                    self.assertEqual(status, value['status']); self.assertIsNone(value['journal'])
                    restored = official_host.Host.restore_closed(self.target, self.grant)
                    for call in ('same', 'new'):
                        self.assertFalse(restored.dispatch({'callId': call})['worker_admitted'])
                    with self.assertRaisesRegex(ContractError, 'execution-already-terminal'):
                        state.cancel(self.target, self.grant, 'late')
                    with self.assertRaisesRegex(ContractError, 'resolution-requires-unresolved-state'):
                        state.resolution_preview(self.target, self.grant)
                    self.assertEqual(before, self.snapshot())

    def test_live_unknown_incomplete_keep_private_gate_and_no_mutable_0644(self):
        for status in ('incomplete', 'unknown'):
            for mode in (0o600, 0o700, 0o400):
                with self.subTest(status=status, mode=oct(mode)):
                    self.write(status, mode)
                    value = state.read_capsule(self.target, self.grant)
                    self.assertEqual(status, value['status']); self.assertIsInstance(value['journal'], documents.EffectJournal)
            self.path.chmod(0o644); before = self.snapshot()
            with self.assertRaisesRegex(documents.HostRefusal, 'aliased or nonprivate control file'):
                state.read_capsule(self.target, self.grant)
            with self.assertRaisesRegex(documents.HostRefusal, 'aliased or nonprivate control file'):
                value['journal'].append('refused', {})
            self.assertEqual(before, self.snapshot())

    def test_nonstandard_terminal_modes_are_refused_without_chmod(self):
        for mode in (0o400, 0o640, 0o664, 0o666, 0o700):
            with self.subTest(mode=oct(mode)):
                self.write(mode=mode); before = self.snapshot()
                with self.assertRaises((documents.HostRefusal, ContractError)):
                    state.read_capsule(self.target, self.grant)
                self.assertEqual(before, self.snapshot())

    def test_actual_special_mode_terminal_files_are_refused(self):
        root = Path(os.environ['HISTORY_SPECIAL_FIXTURES'])
        for mode in (0o4600, 0o4644):
            target = root / oct(mode)
            grant, = (target / '.hrn/executions').iterdir()
            path = grant / 'journal.jsonl'
            before = (path.read_bytes(), path.stat().st_mode, path.stat().st_mtime_ns)
            self.assertEqual(mode, stat.S_IMODE(before[1]))
            error, reason = ((ContractError, 'closed-journal-mode') if mode == 0o4600
                             else (documents.HostRefusal, 'unsafe journal observation'))
            with self.assertRaisesRegex(error, reason):
                state.read_capsule(target, grant.name)
            self.assertEqual(before, (path.read_bytes(), path.stat().st_mode, path.stat().st_mtime_ns))

    def test_alias_type_owner_and_hardlink_refuse(self):
        self.write(); raw = self.path.read_bytes()
        extra = self.root / 'alias'
        os.link(self.path, extra)
        with self.assertRaisesRegex(documents.HostRefusal, 'unsafe journal observation'): documents.observe_journal(self.path)
        extra.unlink(); self.path.rename(extra); self.path.symlink_to(extra)
        with self.assertRaisesRegex(documents.HostRefusal, 'noncanonical control file'): documents.observe_journal(self.path)
        self.path.unlink(); self.path.mkdir()
        with self.assertRaisesRegex(documents.HostRefusal, 'unsafe journal observation'): documents.observe_journal(self.path)
        self.path.rmdir(); os.mkfifo(self.path)
        with self.assertRaisesRegex(documents.HostRefusal, 'unsafe journal observation'): documents.observe_journal(self.path)
        self.path.unlink(); self.path.write_bytes(raw); self.path.chmod(0o600)
        uid = os.getuid()
        with mock.patch.object(documents.os, 'getuid', return_value=uid+1):
            with self.assertRaisesRegex(documents.HostRefusal, 'unsafe journal observation'): documents.observe_journal(self.path)
        alias = self.target / 'aliased-root'; alias.symlink_to(self.root, target_is_directory=True)
        with self.assertRaisesRegex(documents.HostRefusal, 'noncanonical control file'): documents.observe_journal(alias / self.path.name)

    def test_same_bytes_replacement_and_mode_drift_during_observation_refuse(self):
        for change in ('replace', 'mode'):
            with self.subTest(change=change):
                self.write(); native = os.fstat; calls = []
                def drift(fd):
                    calls.append(fd)
                    if len(calls) == 2:
                        if change == 'mode': self.path.chmod(0o644)
                        else:
                            replacement = self.root / 'replacement'; replacement.write_bytes(self.path.read_bytes())
                            replacement.chmod(0o600); replacement.replace(self.path)
                    return native(fd)
                with mock.patch.object(documents.os, 'fstat', side_effect=drift):
                    with self.assertRaisesRegex(documents.HostRefusal, 'journal-observation-drift'): documents.observe_journal(self.path)

    def test_live_identity_is_rechecked_after_private_journal_construction(self):
        self.write('unknown'); original = documents.EffectJournal
        def replaced(path):
            journal = original(path)
            replacement = self.root / 'replacement'; replacement.write_bytes(self.path.read_bytes())
            replacement.chmod(0o600); replacement.replace(self.path)
            return journal
        with mock.patch.object(documents, 'EffectJournal', side_effect=replaced):
            with self.assertRaisesRegex(documents.HostRefusal, 'journal-observation-drift'):
                state.read_capsule(self.target, self.grant)

    def test_canonical_hashchain_partial_duplicate_and_size_limits(self):
        self.write(); raw = self.path.read_bytes()
        broken = [raw[:-1], raw.replace(b'"seq":1', b'"seq":2', 1),
                  raw.replace(b'"seq":1', b'"seq":1,"seq":1', 1), b' ' + raw]
        for value in broken:
            self.path.write_bytes(value); self.path.chmod(0o644)
            with self.assertRaises(documents.HostRefusal): state.read_capsule(self.target, self.grant)
        self.path.write_bytes(bytes_for([('granted', {'grant': self.grant})] * 8193))
        with self.assertRaisesRegex(documents.HostRefusal, 'journal-count-limit'): documents.observe_journal(self.path)
        with self.path.open('wb') as stream: stream.truncate(16*1024*1024+1)
        with self.assertRaisesRegex(documents.HostRefusal, 'control file too large'): documents.observe_journal(self.path)

    def test_false_terminal_missing_seal_process_close_and_pending_refuse(self):
        cases = [
            [('granted', {'grant': self.grant}), ('terminal', {'status': 'completed'})],
            [('granted', {'grant': self.grant}), ('runtime-reserved', {}), ('terminal', {'status': 'interrupted'})],
            [('granted', {'grant': self.grant}), ('callback-reserved', {'callId': 'pending'}), ('terminal', {'status': 'interrupted'})],
            [('granted', {'grant': self.grant}), ('terminal', {'status': []})],
        ]
        for events in cases:
            with self.subTest(events=events):
                self.write(mode=0o644, events=events); before = self.snapshot()
                with self.assertRaises((ContractError, TypeError, KeyError)):
                    state.read_capsule(self.target, self.grant)
                self.assertEqual(before, self.snapshot())

    def test_grant_digest_and_target_mismatch_remain_refused(self):
        self.write(mode=0o644)
        grant_path = self.root / 'grant.json'; value = json.loads(grant_path.read_bytes())
        value['spec']['target'] = str(self.target / 'other')
        grant_path.write_bytes(state.canonical(value)); before = self.snapshot()
        with self.assertRaisesRegex(ContractError, 'grant-record'):
            state.read_capsule(self.target, self.grant)
        self.assertEqual(before, self.snapshot())

    def test_existing_private_parser_is_the_same_parser(self):
        self.write('unknown')
        self.assertEqual(documents.EffectJournal(self.path).read(), documents.observe_journal(self.path)[0])
        self.path.chmod(0o644)
        with self.assertRaisesRegex(documents.HostRefusal, 'aliased or nonprivate control file'):
            documents.EffectJournal(self.path)


from tests import test_official_execution as existing
import copy
import subprocess
import sys
import time
from hv2ref import work, workspace


class InstalledHistoryCheckoutTests(unittest.TestCase):
    setUpClass = classmethod(existing.OfficialExecutionTests.setUpClass.__func__)
    tearDownClass = classmethod(existing.OfficialExecutionTests.tearDownClass.__func__)
    def setUp(self):
        self.folder=self.root/self._testMethodName;self.folder.mkdir()
        self.target=self.folder/'project';self.target.mkdir()
        # Establish Git membership before the Work baseline is published.
        self.git('init', '-q'); self.git('config', 'user.name', 'Synthetic Fixture')
        self.git('config', 'user.email', 'synthetic@example.invalid'); self.git('config', 'commit.gpgsign', 'false')
        (self.target/'a').write_bytes(existing.PREFIX+existing.BEFORE+existing.SUFFIX)
        (self.target/'b').write_text('# Policy\n\nApproved fact.\n')
        (self.target/'sentinel').write_text('protected synthetic\n')
        packet=existing.product.workspace_init_preview(self.candidate,self.target,authority_home_id='home-a',operation_id='init-a',created_at=existing.TIME)
        existing.product.workspace_init_apply(self.candidate,self.target,packet['request'],confirm_token=packet['confirm_token'])
        seed=subprocess.run([sys.executable,'-I','-S','-B',str(existing.SOURCE/'tests/fixtures/official_fixture.py'),str(self.target)],capture_output=True,timeout=60)
        if seed.returncode:self.fail((seed.stdout+seed.stderr).decode())
        self.runtime=existing.product.verify_workspace_product(self.target)
        self.runtime['inventory_id']=state.WINDOW
        self.binding_patch=mock.patch.object(existing.product,'require_workspace_runtime',return_value=self.runtime)
        self.binding_patch.start();self.addCleanup(self.binding_patch.stop)
        # Offline unit seam only. Installed CLI provenance is tested separately; live admission remains unmodified.
        self.input_patch=mock.patch.object(existing.entry,'runtime_input',return_value={})
        self.input_patch.start();self.addCleanup(self.input_patch.stop)
        runtime=self.folder/'runtime';runtime.mkdir(mode=0o700)
        self.request={'work_id':'official-work','worker_root':str(self.target),'documents':{
            'files':{'Editable':{'path':str(self.target/'a'),'view':{'kind':'replace-range','ranges':[[len(existing.PREFIX),len(existing.PREFIX+existing.BEFORE)]]}},
                     'Reference':{'path':str(self.target/'b'),'view':{'kind':'full'}}},
            'output':'Editable','claims':{'Editable':{'required':['Approved fact.'],'forbidden':['Unapproved'],
                'evidence':[{'file_id':'Reference','quote':'Approved fact.'}]}},'approved_external_links':[]},
            'read_ids':['Editable','Reference'],'prompt':'Read, replace with Approved fact., then verify.',
            'owner_statement':'Synthetic bounded execution authorization','runtime':{},'runtime_root':str(runtime),
            'expires_wall_ns':time.time_ns()+600*10**9,'seconds':90,'worker_limit':5}

    prepare = existing.OfficialExecutionTests.prepare
    new_host = existing.OfficialExecutionTests.new_host
    installed = existing.OfficialExecutionTests.installed

    def git(self, *args):
        result = subprocess.run(['git', '-c', 'maintenance.auto=false', '-c', 'gc.auto=0', '-C', str(self.target), *args],
                                env=workspace.git_environment(), capture_output=True, timeout=30)
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        return result.stdout.decode().strip()

    def fixture_call(self, request):
        binding = json.loads((self.target / '.hrn/product/binding.json').read_bytes())
        payload = self.target / '.hrn/product/releases' / binding['active_release']['id'] / 'payload'
        result = subprocess.run([sys.executable, '-I', '-S', '-B', str(existing.SOURCE / 'tests/fixtures/delegation_process.py'),
                                 str(payload), str(self.target)], input=json.dumps(request).encode(), capture_output=True, timeout=60)
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        return json.loads(result.stdout)

    def complete_work(self):
        graph = work.read_work(self.target, 'official-work')
        selected = graph['selections'][graph['current']['selection_ref']['id']]
        revision = copy.deepcopy(graph['revisions'][selected['revision_ref']['id']])
        manifest = graph['manifests'][revision['result_refs']['manifest']['id']]
        revision.update(record_id='result-1', operation='submit-result', progress='review',
                        expected_prior_selection=graph['current']['selection_ref'])
        self.fixture_call({'action': 'work-publish', 'identity': graph['identity'], 'revision': revision, 'manifest': manifest,
                           'selection_id': 'result-1', 'operation_id': 'submit-result'})
        packet = self.fixture_call({'action': 'work-prepare', 'wid': 'official-work', 'operation_id': 'accept-result'})
        self.fixture_call({'action': 'work-apply', 'packet': packet})

    def observed_files(self):
        return {p.relative_to(self.target).as_posix(): (p.read_bytes(), stat.S_IMODE(p.stat().st_mode), p.stat().st_mtime_ns)
                for p in (self.target / '.hrn').rglob('*') if p.is_file() and '.hrn/locks/' not in p.relative_to(self.target).as_posix()}

    def assert_readable(self, grant):
        before = self.observed_files()
        result = self.installed('status')
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        observed = json.loads(result.stdout)
        self.assertTrue(observed['official_execution']['available'], observed)
        self.assertTrue(observed['official_execution']['ready_for_new_grant'], observed)
        self.assertEqual([grant], [x['grant'] for x in observed['official_execution']['records']])
        self.assertEqual('completed', observed['official_execution']['records'][0]['status'])
        self.assertEqual('completed', observed['work_states']['official-work'])
        for args in [('doctor',), ('run', 'status', '--grant', grant), ('view', 'work', 'official-work', '--revision', 'result-1')]:
            result = self.installed(*args)
            self.assertEqual(0, result.returncode, result.stdout + result.stderr)
            if args[0] == 'view':
                text = result.stdout.decode()
                self.assertIn('Stored state: completed', text)
                self.assertIn('matches stored result', text)
                self.assertNotIn('unreadable execution', text)
            elif args[0] == 'doctor':
                self.assertTrue(json.loads(result.stdout)['official_execution']['available'])
            else: self.assertEqual('completed', json.loads(result.stdout)['status'])
        with workspace.writer_guard(self.target): pass
        restored = official_host.Host.restore_closed(self.target, grant)
        for call in ('same', 'new'):
            self.assertFalse(restored.dispatch({'callId': call})['worker_admitted'])
        self.assertEqual(before, self.observed_files())

    def roundtrip(self, mask):
        self.git('add', '.'); self.git('commit', '-qm', 'synthetic initial state')
        baseline = self.git('rev-parse', 'HEAD')
        self.git('checkout', '-qb', 'history')
        h = self.new_host()
        # Durable synthetic terminal state; no model, RPC or worker execution.
        for i in range(5):
            h.journal.append('callback-reserved', {'callId': str(i)})
            h.journal.append('callback-completed', {'callId': str(i)})
        h.journal.append('seal', {}); h.journal.append('terminal', {'status': 'completed'}); h.close()
        self.complete_work(); self.assert_readable(h.grant)
        self.git('add', '.'); self.git('commit', '-qm', 'synthetic completed history')
        original = {k: v[0] for k, v in self.observed_files().items()}
        journal = h.run / 'journal.jsonl'
        old_mask = os.umask(mask)
        try:
            self.git('checkout', '-qb', 'before-history', baseline)
            self.assertFalse(journal.exists())
            self.git('checkout', '-q', 'history')
            self.assertEqual(0o644 if mask == 0o022 else 0o600, stat.S_IMODE(journal.stat().st_mode))
            self.assertEqual(original, {k: v[0] for k, v in self.observed_files().items()})
            self.assert_readable(h.grant)
            self.git('checkout', '-q', 'before-history'); self.assertFalse(journal.exists())
            self.git('merge', '--ff-only', 'history')
            self.assertEqual(0o644 if mask == 0o022 else 0o600, stat.S_IMODE(journal.stat().st_mode))
            self.assertEqual(original, {k: v[0] for k, v in self.observed_files().items()})
            self.assert_readable(h.grant)
        finally: os.umask(old_mask)
        self.assertEqual('', self.git('status', '--porcelain'))

    def test_same_target_checkout_and_ff_umask022(self): self.roundtrip(0o022)
    def test_same_target_checkout_and_ff_umask077(self): self.roundtrip(0o077)

    def test_exact_previous_reader_keeps_0600_and_refuses_0644_new_history(self):
        previous = Path(os.environ['COLVIA_PREVIOUS_OFFICIAL_SOURCE'])
        h = self.new_host(); h.finish('revoked-before-launch'); h.close()
        path = h.run / 'journal.jsonl'
        for mode in (0o600, 0o644):
            path.chmod(mode); before = self.observed_files()
            result = subprocess.run([sys.executable, '-I', '-S', '-B',
                                     str(existing.SOURCE / 'tests/fixtures/delegation_process.py'),
                                     str(previous), str(self.target)],
                                    input=b'{"action":"status"}', capture_output=True, timeout=30)
            self.assertEqual(0, result.returncode, result.stdout + result.stderr)
            old_status = json.loads(result.stdout)['official_execution']
            self.assertEqual(mode == 0o600, old_status['available'])
            self.assertEqual(mode == 0o600, old_status['ready_for_new_grant'])
            self.assertEqual('revoked-before-launch', state.read_capsule(self.target, h.grant)['status'])
            self.assertEqual(before, self.observed_files())
