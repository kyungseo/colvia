"""Bounded document views and no-clobber creation; no authentication/provider use."""
from copy import deepcopy
import importlib.util
import os
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
def load(name):
    spec = importlib.util.spec_from_file_location('u2_v2_' + name, ROOT / ('docs/development/verification/u2-host/' + name + '.py'))
    module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
    return module
host, worker = load('host'), load('worker')

class DocumentV2Tests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name).resolve()

    def record(self, raw=None, view=None):
        p = self.root / 'document.md'
        if raw is not None:
            p.write_bytes(raw)
        entry, _ = host.file_record(p, limit=131_072, absent=raw is None)
        entry['view'] = view or {'kind':'full'}
        return entry

    def write(self, entry, text):
        swap = self.root / 'output.swap'
        parents = host.parent_identities([entry['path'], str(swap)])
        return worker.atomic_write(entry, parents, str(swap), entry['sha256'], text)

    def claims_spec(self, entry, expected):
        rule = {"required":["row"], "forbidden":[], "evidence":[{"file_id":"Doc","quote":"row"}], "exact_view_sha256":expected}
        return {"files":{"Doc":entry}, "parents":host.parent_identities([entry["path"]]), "outputs":["Doc"], "claims":{"Doc":rule}, "approved_external_links":[], "parser_sha256":"0"*64}

    def test_claims_exact_view_rejects_wrong_table_shape_and_extra_text(self):
        wanted=b"| date | row | scope | conclusion |\n"
        for actual in [b"| date | product | process | row | summary |\n", wanted+b"extra row\n"]:
            with self.subTest(actual=actual):
                p=self.root/'document.md'
                if p.exists(): p.unlink()
                entry=self.record(b"prefix\n"+actual+b"suffix\n", {'kind':'replace-range','ranges':[[7,7+len(actual)]]})
                result=worker.verify(self.claims_spec(entry,worker.sha(wanted)), 'DOC-CLAIMS')
                self.assertFalse(result['pass'])
                self.assertIn({'file_id':'Doc','code':'exact-view-mismatch'},result['findings'])

    def test_claims_exact_view_accepts_only_selected_bytes(self):
        wanted=b"| date | row | scope | conclusion |\n"
        entry=self.record(b"prefix\n"+wanted+b"suffix\n", {'kind':'replace-range','ranges':[[7,7+len(wanted)]]})
        spec=self.claims_spec(entry,worker.sha(wanted))
        self.assertTrue(worker.verify(spec,'DOC-CLAIMS')['pass'])
        del spec['claims']['Doc']['exact_view_sha256']
        self.assertTrue(worker.verify(spec,'DOC-CLAIMS')['pass'])

    def test_claims_exact_view_rejects_invalid_digest(self):
        entry=self.record(b"row\n")
        for invalid in [None,1,[],"", "A"*64,"g"*64,"0"*63]:
            with self.subTest(invalid=invalid):
                with self.assertRaises(worker.WorkerRefusal):
                    worker.verify(self.claims_spec(entry,invalid),'DOC-CLAIMS')

    def test_new_file_atomic_creation(self):
        entry = self.record()
        self.assertIsNone(host.document_item('New', entry, b'')['file_sha256'])
        result = self.write(entry, '# 새 문서\n')
        self.assertEqual(Path(entry['path']).read_text(), '# 새 문서\n')
        self.assertEqual(result['sha256'], host.digest('# 새 문서\n'.encode()))
        self.assertFalse((self.root/'output.swap').exists())
        self.assertEqual(Path(entry['path']).stat().st_mode & 0o777, 0o644)

    def test_absence_collision_file_and_symlink(self):
        for kind in ('file','symlink'):
            with self.subTest(kind=kind):
                entry = self.record()
                p = Path(entry['path'])
                if kind == 'file': p.write_text('existing')
                else: p.symlink_to(self.root/'missing')
                with self.assertRaises(host.HostRefusal): host.document_record(entry)
                with self.assertRaises(worker.WorkerRefusal): self.write(entry,'replacement')
                self.assertTrue(os.path.lexists(p)); p.unlink()

    def test_creation_race_uses_kernel_no_clobber(self):
        entry = self.record(); p=Path(entry['path'])
        original = worker.file_bytes; calls=0
        def race(e, parents):
            nonlocal calls
            data=original(e,parents);calls+=1
            if calls==2: p.write_text('concurrent writer')
            return data
        worker.file_bytes=race
        try:
            with self.assertRaises(OSError): self.write(entry,'new bytes')
        finally: worker.file_bytes=original
        self.assertEqual(p.read_text(),'concurrent writer')
        self.assertEqual((self.root/'output.swap').read_text(),'new bytes')

    def test_large_fixed_slice_preserves_nonselected_bytes(self):
        prefix=('앞\n'*12000).encode(); selected='## 대상\n변경 전\n'.encode(); suffix=('뒤\n'*12000).encode()
        raw=prefix+selected+suffix
        entry=self.record(raw,{'kind':'replace-range','ranges':[[len(prefix),len(prefix)+len(selected)]]})
        self.assertGreater(len(raw),65536)
        self.assertEqual(worker.document_view(entry,raw),selected)
        self.assertEqual(host.document_item('Doc',entry,raw),worker.read_item('Doc',entry,raw))
        self.write(entry,'## 대상\n변경 후\n')
        self.assertEqual(Path(entry['path']).read_bytes(),prefix+'## 대상\n변경 후\n'.encode()+suffix)

    def test_full_digest_cas_rejects_nonselected_drift(self):
        raw=b'prefix\nselected\nsuffix\n';entry=self.record(raw,{'kind':'replace-range','ranges':[[7,16]]})
        Path(entry['path']).write_bytes(b'PREFIX\nselected\nsuffix\n')
        with self.assertRaises(worker.WorkerRefusal): self.write(entry,'changed')
        self.assertEqual(Path(entry['path']).read_bytes(),b'PREFIX\nselected\nsuffix\n')

    def test_invalid_utf8_ranges_and_nonmonotonic_views(self):
        raw='한국어\n'.encode(); entry=self.record(raw)
        for ranges in ([[1,4]],[[3,6],[0,3]],[[0,99]],[[True,3]]):
            entry['view']={'kind':'read-ranges','ranges':ranges}
            with self.subTest(ranges=ranges):
                with self.assertRaises((host.HostRefusal,UnicodeError)): host.document_view(entry,raw)
                with self.assertRaises((worker.WorkerRefusal,UnicodeError)): worker.document_view(entry,raw)

    def test_readonly_ranges_reject_write(self):
        raw=b'head\nbody\ntail\n';entry=self.record(raw,{'kind':'read-ranges','ranges':[[0,5],[10,15]]})
        self.assertNotIn(b'body',worker.document_view(entry,raw))
        with self.assertRaises(worker.WorkerRefusal): self.write(entry,'change')
        self.assertEqual(Path(entry['path']).read_bytes(),raw)

    def test_hardlink_rejected(self):
        entry=self.record(b'original');os.link(entry['path'],self.root/'alias')
        with self.assertRaises(host.HostRefusal): host.document_record(entry)
        with self.assertRaises(worker.WorkerRefusal): self.write(entry,'change')

    def test_parent_symlink_rejected(self):
        entry=self.record(b'original');alias=self.root/'alias';alias.symlink_to(self.root,target_is_directory=True)
        entry['path']=str(alias/'document.md')
        with self.assertRaises(host.HostRefusal): host.document_record(entry)

    def test_unchanged_v1_size_limit_and_v2_wire_limit(self):
        entry=self.record(b'x'*70000,{'kind':'read-ranges','ranges':[[0,100]]})
        with self.assertRaises(host.HostRefusal): host.file_record(entry['path'])
        self.assertEqual(host.pack_reads({'Doc':entry}),[['Doc']])
        entry['view']={'kind':'full'}
        with self.assertRaises(host.HostRefusal): host.pack_reads({'Doc':entry})

    def test_fixed_insertion_and_empty_replacement(self):
        raw=b'header\nfooter\n';entry=self.record(raw,{'kind':'replace-range','ranges':[[7,7]]})
        self.assertEqual(worker.document_view(entry,raw),b'')
        self.write(entry,'new row\n')
        self.assertEqual(Path(entry['path']).read_bytes(),b'header\nnew row\nfooter\n')
        (self.root/'document.md').unlink()
        entry=self.record(raw,{'kind':'replace-range','ranges':[[0,7]]})
        self.write(entry,'')
        self.assertEqual(Path(entry['path']).read_bytes(),b'footer\n')

    def test_access_time_is_not_content_drift(self):
        from types import SimpleNamespace
        names=['st_dev','st_ino','st_mode','st_nlink','st_size','st_mtime_ns','st_ctime_ns']
        first=SimpleNamespace(**dict(zip(names,range(7))),st_atime_ns=1)
        second=SimpleNamespace(**dict(zip(names,range(7))),st_atime_ns=2)
        self.assertEqual(host.document_stat_key(first),host.document_stat_key(second))
        self.assertEqual(worker.document_stat_key(first),worker.document_stat_key(second))
        second.st_mtime_ns=99
        self.assertNotEqual(host.document_stat_key(first),host.document_stat_key(second))
        self.assertNotEqual(worker.document_stat_key(first),worker.document_stat_key(second))

    def test_resume_keeps_immutable_outside_slice_contract(self):
        raw=b'prefix\nold\nsuffix\n';entry=self.record(raw,{'kind':'replace-range','ranges':[[7,11]]})
        contracts=host.initial_view_contracts({'Doc':entry})
        self.write(entry,'longer new text\n')
        changed,_=host.file_record(entry['path'],limit=131072)
        changed['view']={'kind':'replace-range','ranges':[[7,23]]}
        controller=object.__new__(host.DocumentController)
        controller.files={'Doc':changed};controller.spec={'contract_version':2,'view_contracts':contracts,'outputs':['Doc'],'source_digests':{'Doc':entry['sha256']}}
        controller.check_files()
        changed['view']['ranges'][0][1]+=1
        with self.assertRaises(host.HostRefusal): controller.check_files()

    def test_metadata_drift_is_rejected(self):
        entry=self.record(b'link target');p=Path(entry['path']);st=p.stat()
        metadata={'identity':entry['identity'],'mode':entry['mode'],'size':st.st_size,'mtime_ns':st.st_mtime_ns,'sha256':None,'anchors':[]}
        spec={'parents':host.parent_identities([str(p)]),'link_metadata':{str(p):metadata}}
        self.assertEqual(worker.validate_link_metadata(spec),spec['link_metadata'])
        p.write_text('other bytes')
        with self.assertRaises(worker.WorkerRefusal): worker.validate_link_metadata(spec)

    def test_assembled_size_rejected_before_swap(self):
        raw=b'x'*120000;entry=self.record(raw,{'kind':'replace-range','ranges':[[0,1]]})
        with self.assertRaises(worker.WorkerRefusal): self.write(entry,'y'*20000)
        self.assertEqual(Path(entry['path']).read_bytes(),raw)
        self.assertFalse((self.root/'output.swap').exists())

if __name__=='__main__': unittest.main()
