"""Explicit-root availability and durable raw-original boundaries, offline."""
from pathlib import Path
import copy
import os
import tempfile
import unittest
from unittest import mock

from hv2ref import official_recovery as recovery, official_state as state
from hv2ref.jsonio import canonical_json_bytes
from hv2ref.errors import ContractError
from test_official_v2 import Chain, grant, SHA


class RecoveryTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(); self.addCleanup(self.temp.cleanup)
        self.lab = Path(self.temp.name).resolve()
        self.root = self.lab / 'host-control'; self.root.mkdir(mode=0o700)
        self.target = self.lab / 'project'; self.target.mkdir()
        self.runtime = self.lab / 'runtime'; self.runtime.mkdir(mode=0o700)
        recovery.publish_private(self.root / recovery.MARKER, canonical_json_bytes({'schema_version': 1, 'store_id': 'b' * 32}))
        self.output = self.target / 'output.md'; self.output.write_bytes(b'PRIVATE_ORIGINAL_MARKER\n')
        self.original, self.raw = recovery.document_observation(self.output)
        self.spec = {'host_control': recovery.root_record(self.root), 'target': str(self.target),
                     'runtime_root': str(self.runtime), 'request': {'worker_root': str(self.target), 'documents': {'output': 'Output'}},
                     'documents': {'files': {'Output': {'path': str(self.output)}}}}
        self.value = {'recovery_locator': grant()['recovery_locator'], 'history': mock.Mock(ready=None)}

    def ready(self):
        metadata = recovery.save_original(self.spec, SHA, self.original)
        self.value['history'].ready = {'value': metadata}
        return metadata

    def test_marker_required_and_no_auto_root(self):
        missing = self.lab / 'not-created'
        with self.assertRaises((OSError, ContractError)): recovery.root_record(missing)
        self.assertFalse(missing.exists())
        (self.root / recovery.MARKER).unlink()
        with self.assertRaises((OSError, ContractError)): recovery.root_record(self.root)

    def test_root_private_and_outside_git_runtime_and_project(self):
        for kwargs in ({'target': self.root.parent}, {'runtime_root': self.root}, {'worker_root': self.root / 'nested'}):
            with self.subTest(kwargs=kwargs), self.assertRaisesRegex(ContractError, 'root-overlap'):
                recovery.root_record(self.root, **kwargs)
        self.root.chmod(0o755)
        with self.assertRaisesRegex(ContractError, 'directory-private'): recovery.root_record(self.root)
        self.root.chmod(0o700); (self.lab / '.git').mkdir()
        with self.assertRaisesRegex(ContractError, 'inside-git'): recovery.root_record(self.root)

    def test_not_required_orphan_present_missing_and_mismatch(self):
        self.assertEqual(recovery.inspect(self.value, self.root), 'not_required')
        metadata = self.ready()
        self.assertEqual(metadata['original_identity'], self.original)
        self.assertEqual(recovery.inspect(self.value, self.root), 'present')
        obj = self.root / 'recovery' / SHA / '1'
        self.assertEqual((obj / 'original.bin').read_bytes(), self.raw)
        self.value['history'].ready = None
        self.assertEqual(recovery.inspect(self.value, self.root), 'orphan_candidate')
        self.value['history'].ready = {'value': metadata}
        (obj / 'original.bin').write_bytes(b'tampered')
        self.assertEqual(recovery.inspect(self.value, self.root), 'mismatch')
        (obj / 'original.bin').unlink()
        self.assertEqual(recovery.inspect(self.value, self.root), 'missing')

    def test_root_identity_document_drift_and_reuse_refuse_before_write(self):
        self.output.write_bytes(b'different')
        with self.assertRaisesRegex(ContractError, 'document-drift'):
            recovery.save_original(self.spec, SHA, self.original)
        self.assertFalse((self.root / 'recovery').exists())
        self.original, self.raw = recovery.document_observation(self.output)
        self.ready()
        with self.assertRaises(FileExistsError): recovery.save_original(self.spec, SHA, self.original)
        bad = copy.deepcopy(self.spec); bad['host_control']['ino'] += 1
        with self.assertRaisesRegex(ContractError, 'root-drift'): recovery.save_original(bad, SHA, self.original)

    def test_partial_publication_preserved_and_reports_orphan(self):
        actual = recovery.publish_private
        def fail_manifest(path, raw):
            if Path(path).name == 'manifest.json': raise OSError('synthetic fsync failure')
            return actual(path, raw)
        with mock.patch.object(recovery, 'publish_private', side_effect=fail_manifest), self.assertRaises(OSError):
            recovery.save_original(self.spec, SHA, self.original)
        self.assertEqual(recovery.inspect(self.value, self.root), 'orphan_candidate')
        self.assertEqual((self.root / 'recovery' / SHA / '1/original.bin').read_bytes(), self.raw)

    def test_hardlink_or_extra_recovery_member_reports_mismatch(self):
        self.ready(); obj = self.root / 'recovery' / SHA / '1'
        os.link(obj / 'original.bin', self.lab / 'linked')
        self.assertEqual(recovery.inspect(self.value, self.root), 'mismatch')
        (self.lab / 'linked').unlink()
        (obj / 'unexpected').write_text('unexpected')
        self.assertEqual(recovery.inspect(self.value, self.root), 'mismatch')

    def test_transient_inspection_refuses_alias_and_wrong_store(self):
        self.assertEqual({'transient_presence':'absent','cleanup_marker_presence':'absent'},recovery.inspect_transient(self.value,self.root))
        container=self.root/'transient';container.mkdir(mode=0o700)
        (container/SHA).symlink_to(self.target,target_is_directory=True)
        self.assertEqual('unavailable',recovery.inspect_transient(self.value,self.root)['transient_presence'])
        (container/SHA).unlink();(container/SHA).mkdir(mode=0o700)
        self.assertEqual('present',recovery.inspect_transient(self.value,self.root)['transient_presence'])
        (self.root/recovery.MARKER).write_bytes(canonical_json_bytes({'schema_version':1,'store_id':'c'*32}))
        self.assertEqual('unavailable',recovery.inspect_transient(self.value,self.root)['transient_presence'])


if __name__ == '__main__': unittest.main()
