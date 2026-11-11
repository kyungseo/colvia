"""Synthetic factory wiring and owned descriptors; no subprocess/account use."""
import io,unittest,json,hashlib
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
from colvia.codec import RecordError,canonical_bytes
from colvia.execution import managed_factory,schema
from colvia.platforms.runtime_inventory import inventory
from colvia.platforms.darwin_runtime_policy import POLICY_SHA256
from colvia.storage.files import PosixFiles
import test_foundation_runtime_launch as launch_fixture

class FactoryTests(unittest.TestCase):
    setUp=launch_fixture.RuntimeLaunchTests.setUp
    tearDown=launch_fixture.RuntimeLaunchTests.tearDown
    create=launch_fixture.RuntimeLaunchTests.create
    def setup_factory(self):
        slots=self.root/'runtime-slots';slot=slots/'slots/one';python=slot/'runtime';python.mkdir(parents=True)
        self.bindings['PYROOT']=str(python)
        binary=python/'python';binary.write_bytes(b'inert Python')
        self.inventories['PYROOT']=inventory(Path(self.bindings['PYROOT']),content=True)[0]
        release=dict(version=1,bindings=self.bindings,digests=self.digests,inventories=self.inventories,
            qualified={k:self.digests[k] for k in ('BIN','CODE_MODE_HOST')},model='synthetic-model')
        manager=self.root/'manager';manager.mkdir()
        (manager/'execution-runtime.json').write_bytes(canonical_bytes(release))
        self.entry=SimpleNamespace(home=SimpleNamespace(root=manager,files=PosixFiles(),slots=SimpleNamespace(root=slots)),
            pointer={'slot':'one'},lease=SimpleNamespace(check=lambda:None,verified=SimpleNamespace(python=str(binary))),
            document_execution_readiness=lambda:{'assets_verified':True})
        self.release=release;self.key=schema.digest(dict(qualified=release['qualified'],python=self.inventories['PYROOT'],policy=POLICY_SHA256))
        self.journal=SimpleNamespace();self.effect=SimpleNamespace(root=self.project,authority=self.authority)
    def test_real_factory_constructs_fixed_ports_from_synthetic_qualified_input(self):
        from colvia.platforms.runtime_channel import RuntimeChannel
        from colvia.adapters.document_session import DocumentSession
        from colvia.platforms.worker_stdio import exchange
        self.setup_factory()
        with patch.object(managed_factory,'QUALIFIED_RUNTIME_KEYS',frozenset({self.key})),patch('pathlib.Path.home',return_value=self.home),patch('subprocess.Popen',side_effect=AssertionError('no process')):
            self.assertEqual(self.release,managed_factory.qualified_release(self.entry))
            adapter=managed_factory.NativeAdapter(self.entry,self.journal,SimpleNamespace(root=self.authority),self.effect,self.release)
            adapter.qualify()
            with patch.object(adapter,'_check') as checked:ports=adapter.ports(self.grant)
        checked.assert_called_once_with(self.grant.payload['contract'])
        self.assertIs(RuntimeChannel,ports['channel_factory']);self.assertIs(DocumentSession,ports['session_factory']);self.assertIs(exchange,ports['worker_exchange'])
        self.assertIs(self.journal,ports['backend'].journal);self.assertIs(self.effect,ports['backend'].observer.effects)
        self.assertEqual(Path(self.bindings['PYROOT']),ports['backend'].planner.python_root)
    def test_wrong_python_tree_and_malformed_inventory_refuse_before_ports(self):
        self.setup_factory()
        with patch.object(managed_factory,'QUALIFIED_RUNTIME_KEYS',frozenset({self.key})),patch('pathlib.Path.home',return_value=self.home):
            self.entry.lease.verified.python=str(self.root/'other-python')
            with self.assertRaisesRegex(RecordError,'python-tree-mismatch'):
                managed_factory.NativeAdapter(self.entry,self.journal,SimpleNamespace(root=self.authority),self.effect,self.release)
            self.release['inventories']=[]
            (self.entry.home.root/'execution-runtime.json').write_bytes(canonical_bytes(self.release))
            with self.assertRaisesRegex(RecordError,'runtime-configuration'):managed_factory.qualified_release(self.entry)
    def test_only_captured_fileio_is_closed_even_after_failed_admission(self):
        from colvia.platforms.darwin_processes import DarwinProcesses
        port=DarwinProcesses();streams=[]
        for n in range(3):
            p=self.root/('pipe-'+str(n));p.write_bytes(b'synthetic');streams.append(io.FileIO(p,'r'))
        foreign=SimpleNamespace(close=lambda:(_ for _ in ()).throw(AssertionError('foreign closer')))
        process=SimpleNamespace(stdin=foreign,stdout=streams[1],stderr=streams[2]);port._pipes[id(process)]=(process,tuple(streams))
        with self.assertRaisesRegex(RecordError,'owned-pipes'):port.admit_io(process)
        port.close_io(process);self.assertTrue(all(s.closed for s in streams))
        self.assertNotIn(id(process),port._pipes)

    def test_python_root_alias_refuses_at_factory_boundary(self):
        self.setup_factory();python=Path(self.bindings['PYROOT']);alias=python.parent/'alias';alias.symlink_to(python)
        for spelling in (str(alias),str(python)+'/../runtime'):
            self.bindings['PYROOT']=spelling
            with self.assertRaisesRegex(RecordError,'path-alias|path-spelling'):
                managed_factory.NativeAdapter(self.entry,self.journal,SimpleNamespace(root=self.authority),self.effect,self.release)

    def test_new_refusals_have_safe_display_fallback(self):
        from colvia.presentation import failure
        for code in ('execution-startup-closure-unknown','delivery-closure-unknown','execution-python-tree-mismatch',
                     'execution-assets-unavailable','execution-native-observer-unavailable','execution-runtime-session-alias'):
            self.assertIsInstance(failure(code),str);self.assertTrue(failure(code))
