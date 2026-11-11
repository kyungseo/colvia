"""Synthetic runtime files; never execute or install the selected interpreter."""
import hashlib,tempfile,unittest,json
from pathlib import Path
from unittest.mock import patch
from colvia.codec import RecordError,canonical_bytes
from colvia.updates.slots import RuntimeSlots
from colvia.platforms.posix import snapshot,ObservationBudget

class SlotTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(prefix='slots-');self.base=Path(self.tmp.name)
        self.manager=RuntimeSlots.create(self.base/'managed',os_name='macos',architecture='arm64')
        self.one=self.slot('one',1);self.two=self.slot('two',2,extra=('schema:future.record:1',))
        self.manager.initialize(self.one)
    def tearDown(self):self.tmp.cleanup()
    def slot(self,name,seq,extra=()):
        root=self.manager.root/'slots'/name;root.mkdir()
        for filename in ('python','manager.py','product.py'):(root/filename).write_bytes((name+filename).encode())
        (root/'python').chmod(0o700)
        inv=list(snapshot(root,ObservationBudget(100,10000)).entries)
        caps=sorted(('foundation-v1',*extra))
        m=dict(version=1,release='release-'+name,sequence=seq,os='macos',architecture='arm64',
               python_version='3.14.7',sqlite_version='3.54.0',python='python',manager='manager.py',product='product.py',
               read_capabilities=caps,write_capabilities=caps,features=['ordinary'],inventory=inv)
        raw=canonical_bytes(m);(root/'manifest.json').write_bytes(raw)
        return dict(slot=name,manifest_sha256=hashlib.sha256(raw).hexdigest())
    def test_shared_native_python_version_boundary_matrix(self):
        from colvia.updates.slots import supported_python_version
        rows=json.loads((Path(__file__).parent/'fixtures/foundation-runtime-versions.json').read_text())
        self.assertGreaterEqual(len(rows),40)
        for row in rows:
            with self.subTest(**row):
                self.assertEqual(row['allowed'],supported_python_version(row['os'],row['architecture'],row['version']))

    def test_cli_and_app_select_same_isolated_runtime_without_path(self):
        with patch.dict('os.environ',{'PATH':'/wrong/python'}):
            for _host in ('cli','app','sibling','nested'):
                cmd=self.manager.launch(read_requirements=['foundation-v1'])
                self.assertEqual(['-I','-B'],cmd[1:3]);self.assertTrue(cmd[0].endswith('/one/python'))
    def test_changed_file_missing_file_extra_file_and_symlink_refuse(self):
        product=self.manager.root/'slots/one/product.py';original=product.read_bytes()
        product.write_bytes(b'changed')
        with self.assertRaisesRegex(RecordError,'slot-inventory-mismatch'):self.manager.launch(read_requirements=[])
        product.write_bytes(original);extra=product.parent/'unexpected.py';extra.write_bytes(b'')
        with self.assertRaisesRegex(RecordError,'slot-inventory-mismatch'):self.manager.launch(read_requirements=[])
        extra.unlink();product.unlink()
        with self.assertRaisesRegex(RecordError,'slot-inventory-mismatch'):self.manager.launch(read_requirements=[])
        product.symlink_to('../two/product.py')
        with self.assertRaisesRegex(RecordError,'slot-inventory-mismatch'):self.manager.launch(read_requirements=[])
    def test_update_preserves_old_slot_and_exact_recovery(self):
        old,_=self.manager.selection()
        state=self.manager.activate(self.two,expected_selection=old,read_requirements=['foundation-v1'])
        self.assertEqual(self.one,state['recovery'])
        self.assertTrue((self.manager.root/'slots/one/python').is_file())
        self.assertTrue(self.manager.recovery_launch(read_requirements=['foundation-v1'])[0].endswith('/one/python'))
        raw,_=self.manager.selection();r=self.manager.activate(self.one,expected_selection=raw,read_requirements=['foundation-v1'],recovery=True)
        self.assertEqual(2,r['high_sequence'])
    def test_old_runtime_cannot_write_new_record_semantics(self):
        old,_=self.manager.selection();self.manager.activate(self.two,expected_selection=old,read_requirements=['foundation-v1'])
        raw,before=self.manager.selection()
        with self.assertRaisesRegex(RecordError,'runtime-capability-unavailable'):
            self.manager.activate(self.one,expected_selection=raw,read_requirements=['foundation-v1'],write_requirements=['schema:future.record:1'],recovery=True)
        self.assertEqual(before,self.manager.selection()[1])
    def test_same_sequence_update_and_stale_selection_refuse(self):
        three=self.slot('three',1);old,_=self.manager.selection()
        with self.assertRaisesRegex(RecordError,'runtime-release-rollback'):
            self.manager.activate(three,expected_selection=old,read_requirements=[])
        self.manager.activate(self.two,expected_selection=old,read_requirements=[])
        with self.assertRaisesRegex(RecordError,'runtime-selection-changed'):
            self.manager.activate(self.one,expected_selection=old,read_requirements=[],recovery=True)
    def test_broken_current_can_use_only_verified_recovery_manager(self):
        old,_=self.manager.selection();self.manager.activate(self.two,expected_selection=old,read_requirements=[])
        (self.manager.root/'slots/two/python').write_bytes(b'broken')
        with self.assertRaisesRegex(RecordError,'slot-inventory-mismatch'):self.manager.launch(read_requirements=[])
        self.assertTrue(self.manager.recovery_launch(read_requirements=[])[0].endswith('/one/python'))
        (self.manager.root/'slots/one/python').write_bytes(b'also broken')
        with self.assertRaisesRegex(RecordError,'slot-inventory-mismatch|observation-byte-limit'):self.manager.recovery_launch(read_requirements=[])
    def test_authenticated_replacement_preserves_broken_slots_and_high_water(self):
        old,_=self.manager.selection();self.manager.activate(self.two,expected_selection=old,read_requirements=[])
        for name in ('one','two'):(self.manager.root/'slots'/name/'python').write_bytes(b'broken')
        fresh=self.slot('fresh',3);before=self.manager.selection()[0]
        result=self.manager.activate(fresh,expected_selection=before,read_requirements=['foundation-v1'],replacement=True)
        self.assertEqual(3,result['high_sequence']);self.assertIsNone(result['recovery'])
        self.assertEqual(b'broken',(self.manager.root/'slots/two/python').read_bytes())
        self.assertTrue(list(self.manager.root.glob('repair-*.json')))
    def test_replacement_does_not_bypass_healthy_selection_or_sequence(self):
        before=self.manager.selection()[0]
        with self.assertRaisesRegex(RecordError,'replacement-not-required'):
            self.manager.activate(self.two,expected_selection=before,read_requirements=[],replacement=True)
        (self.manager.root/'slots/one/python').write_bytes(b'broken')
        other=self.slot('different',1)
        with self.assertRaisesRegex(RecordError,'release-rollback'):
            self.manager.activate(other,expected_selection=before,read_requirements=[],replacement=True)
        self.assertEqual(before,self.manager.selection()[0])

    def test_missing_binding_is_repair_not_first_install(self):
        (self.manager.root/'runtime.json').unlink()
        with self.assertRaisesRegex(RecordError,'runtime-repair-required'):self.manager.launch(read_requirements=[])
        with self.assertRaises(FileExistsError):RuntimeSlots.create(self.manager.root,os_name='macos',architecture='arm64')

    def test_shared_writable_file_and_hardlink_refuse(self):
        product=self.manager.root/'slots/one/product.py';product.chmod(0o666)
        with self.assertRaisesRegex(RecordError,'slot-file-not-private'):self.manager.launch(read_requirements=[])
        product.chmod(0o644)
        import os
        os.link(product,self.base/'outside-hardlink')
        with self.assertRaisesRegex(RecordError,'slot-file-not-private'):self.manager.launch(read_requirements=[])

    def test_broken_selected_repair_switches_only_to_verified_recorded_slot(self):
        old,_=self.manager.selection();self.manager.activate(self.two,expected_selection=old,read_requirements=[])
        bad=self.manager.root/'slots/two/python';bad.write_bytes(b'broken')
        raw,before=self.manager.selection()
        three=self.slot('three',3)
        with self.assertRaisesRegex(RecordError,'runtime-recovery-target-mismatch'):
            self.manager.activate(three,expected_selection=raw,read_requirements=[],recovery=True)
        self.assertEqual(before,self.manager.selection()[1])
        result=self.manager.activate(self.one,expected_selection=raw,read_requirements=[],recovery=True)
        self.assertEqual(2,result['high_sequence']);self.assertIsNone(result['recovery'])
        self.assertTrue(self.manager.launch(read_requirements=[])[0].endswith('/one/python'))
        self.assertEqual(b'broken',bad.read_bytes())
        records=list(self.manager.root.glob('repair-*.json'));self.assertEqual(1,len(records))
        from colvia.codec import decode_canonical
        self.assertEqual(before,decode_canonical(records[0].read_bytes())['before'])

    def test_exact_candidate_versions_keep_old_platforms_and_limit_new_patch(self):
        from colvia.updates.slots import supported_python_version
        for os_name,arch in (('macos','arm64'),('windows','arm64'),('windows','x64')):
            for version in ('3.14.6','3.14.7'):
                self.assertTrue(supported_python_version(os_name,arch,version))
            self.assertEqual(os_name=='macos',supported_python_version(os_name,arch,'3.14.10'))
            for version in ('3.14.8','3.14.11','3.15.0','3.14.10-custom'):
                self.assertFalse(supported_python_version(os_name,arch,version))
        self.assertFalse(supported_python_version('linux','arm64','3.14.10'))
        self.assertFalse(supported_python_version('macos','x64','3.14.10'))

    def test_new_mac_patch_does_not_bypass_inventory_or_sqlite_floor(self):
        from colvia.codec import decode_canonical
        root=self.manager.root/'slots/one';path=root/'manifest.json';m=decode_canonical(path.read_bytes())
        m.update(python_version='3.14.10',sqlite_version='3.53.1')
        def pointer():
            raw=canonical_bytes(m);path.write_bytes(raw)
            return dict(slot='one',manifest_sha256=hashlib.sha256(raw).hexdigest())
        target=pointer();self.manager.verify(target)
        (root/'product.py').write_bytes(b'drift')
        with self.assertRaisesRegex(RecordError,'slot-inventory-mismatch'):self.manager.verify(target)
        (root/'product.py').write_bytes(b'oneproduct.py')
        m['sqlite_version']='3.36.0'
        with self.assertRaisesRegex(RecordError,'slot-sqlite-version'):self.manager.verify(pointer())
        m.update(os='windows',architecture='arm64',sqlite_version='3.53.1')
        from colvia.updates.slots import verify_slot
        target=pointer()
        with self.assertRaisesRegex(RecordError,'slot-runtime-version'):
            verify_slot(self.manager.root,**target,os_name='windows',architecture='arm64')
