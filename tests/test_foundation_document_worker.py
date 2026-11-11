"""New worker semantics: preserved original and exclusive publication.

Direct calls and an actual isolated Python subprocess use synthetic files.
These tests do not qualify the future literal OS profile or installed runtime.
"""
import hashlib,json,os,subprocess,sys,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
from colvia.platforms import darwin_document_worker as worker
from colvia.codec import RecordError

@unittest.skipUnless(sys.platform=='darwin','qualified Darwin writer primitive')
class WorkerTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(prefix='document-worker-');self.root=Path(self.tmp.name)
        self.path=self.root/'output.md';self.path.write_bytes(b'prefix OLD suffix')
        self.slot=self.root/'slot';self.slot.mkdir(mode=0o700);self.swap=self.slot/'new.post'
        self.entry=self.record(self.path);self.entry['view']={'kind':'replace-range','ranges':[[7,10]]}
        self.parents={str(p):[p.stat().st_dev,p.stat().st_ino] for v in (self.path,self.swap) for p in v.parents}
    def tearDown(self):self.tmp.cleanup()
    def record(self,path):
        st=path.stat();return dict(path=str(path),identity=[st.st_dev,st.st_ino],mode=st.st_mode&0o7777,sha256=hashlib.sha256(path.read_bytes()).hexdigest())
    def write(self):return worker.atomic_write(self.entry,self.parents,str(self.swap),self.entry['sha256'],'NEW')
    def test_changed_range_preserves_original_and_new_exact_bytes(self):
        old=self.path.stat().st_ino;result=self.write()
        self.assertEqual(b'prefix NEW suffix',self.path.read_bytes());self.assertEqual(b'prefix OLD suffix',self.swap.with_name('new.post.original').read_bytes())
        self.assertEqual(old,self.swap.with_name('new.post.original').stat().st_ino)
        self.assertEqual(hashlib.sha256(self.path.read_bytes()).hexdigest(),result['sha256']);self.assertFalse(self.swap.exists())
    def test_existing_staging_or_saved_original_refuses_without_clobber(self):
        saved=self.swap.with_name('new.post.original');saved.write_bytes(b'keep')
        with self.assertRaisesRegex(RecordError,'effect-destination-occupied'):self.write()
        self.assertEqual(b'prefix OLD suffix',self.path.read_bytes());self.assertEqual(b'keep',saved.read_bytes())
        self.assertTrue(self.swap.exists())
    def test_competing_target_after_evacuation_is_preserved(self):
        original=worker.exclusive_rename;calls=0
        def interleave(*args):
            nonlocal calls
            calls+=1;original(*args)
            if calls==1:self.path.write_bytes(b'concurrent edit')
        with patch.object(worker,'exclusive_rename',side_effect=interleave),self.assertRaisesRegex(RecordError,'effect-destination-occupied'):self.write()
        self.assertEqual(b'concurrent edit',self.path.read_bytes());self.assertEqual(b'prefix OLD suffix',self.swap.with_name('new.post.original').read_bytes())
        self.assertEqual(b'prefix NEW suffix',self.swap.read_bytes())
    def test_held_descriptor_late_edit_is_retained_and_refused(self):
        fd=os.open(self.path,os.O_RDWR);original=worker.exclusive_rename;calls=0
        def interleave(*args):
            nonlocal calls
            original(*args);calls+=1
            if calls==1:os.pwrite(fd,b'CHANGED',0)
        try:
            with patch.object(worker,'exclusive_rename',side_effect=interleave),self.assertRaisesRegex(worker.WorkerRefusal,'file-bytes-drift'):self.write()
        finally:os.close(fd)
        self.assertTrue(self.path.read_bytes().startswith(b'CHANGED'))
        self.assertTrue(self.swap.exists())
    def test_actual_module_process_reads_then_writes_only_fixed_request(self):
        spec=dict(version=1,files={'Output':self.entry},parents=self.parents,outputs=['Output'],swap={'Output':str(self.swap)},
            parser='/not-used',parser_sha256='a'*64,claims={},approved_external_links=[],link_metadata={})
        specfile=self.slot/'spec.json';specfile.write_text(json.dumps(spec))
        source=str(Path(__file__).resolve().parents[1]/'src')
        code='import sys,runpy;sys.path.insert(0,sys.argv.pop(1));runpy.run_module("colvia.platforms.darwin_document_worker",run_name="__main__")'
        argv=[sys.executable,'-I','-S','-B','-c',code,source,'--spec',str(specfile)]
        read=subprocess.run(argv+['--operation','read'],input=json.dumps({'tool':'document_read','arguments':{'file_ids':['Output']}}),
            capture_output=True,text=True,timeout=5,cwd=self.slot,env={'PATH':'/usr/bin:/bin'})
        self.assertEqual(0,read.returncode,read.stdout);self.assertIn('OLD',read.stdout)
        write=subprocess.run(argv+['--operation','write'],input=json.dumps({'tool':'document_write','arguments':{'file_id':'Output','expected_sha256':self.entry['sha256'],'content':'NEW'}}),
            capture_output=True,text=True,timeout=5,cwd=self.slot,env={'PATH':'/usr/bin:/bin'})
        self.assertEqual(0,write.returncode,write.stdout);self.assertEqual(b'prefix NEW suffix',self.path.read_bytes())
        self.assertEqual(b'prefix OLD suffix',self.swap.with_name('new.post.original').read_bytes())

    def verifier_spec(self,text):
        self.path.write_text(text);reference=self.root/'reference.md';reference.write_text('# Policy\nAllow changes.\n')
        files={'Output':dict(self.record(self.path),view={'kind':'full'}),'Reference':dict(self.record(reference),view={'kind':'full'})}
        parser=Path(__file__).resolve().parents[1]/'runtime/official/marked.umd.js'
        parents={str(p):[p.stat().st_dev,p.stat().st_ino] for v in (self.path,reference) for p in v.parents}
        return dict(files=files,parents=parents,outputs=['Output'],claims={'Output':dict(required=['Allow changes.'],forbidden=['guaranteed'],
            evidence=[dict(file_id='Reference',quote='Allow changes.')])},approved_external_links=[],link_metadata={},
            parser=str(parser),parser_sha256=hashlib.sha256(parser.read_bytes()).hexdigest())
    def test_actual_gfm_links_and_fixed_claim_checks_are_preserved(self):
        spec=self.verifier_spec('# Report\nAllow changes.\n[Policy](reference.md#policy)\n')
        for verifier in ('DOC-LINKS','DOC-GFM','DOC-CLAIMS'):
            with self.subTest(verifier=verifier):self.assertTrue(worker.verify(spec,verifier)['pass'])
        spec=self.verifier_spec('# Report\nAllow changes. guaranteed\n[x](https://example.invalid/)\n')
        self.assertFalse(worker.verify(spec,'DOC-LINKS')['pass']);self.assertFalse(worker.verify(spec,'DOC-CLAIMS')['pass'])
    def test_active_html_missing_anchor_and_literal_emphasis_fail(self):
        cases=[('<script>alert(1)</script>\n','DOC-LINKS','active-html'),
            ('[Policy](reference.md#missing)\n','DOC-LINKS','missing-anchor'),
            ('**broken\n','DOC-GFM','literal-emphasis-outside-code')]
        for text,verifier,code in cases:
            with self.subTest(code=code):
                value=worker.verify(self.verifier_spec(text),verifier)
                self.assertFalse(value['pass']);self.assertIn(code,[f['code'] for f in value['findings']])
    def test_duplicate_json_key_and_parent_alias_refuse(self):
        with self.assertRaisesRegex(worker.WorkerRefusal,'duplicate-json-key'):json.loads('{"tool":"read","tool":"write"}',object_pairs_hook=worker.unique)
        wrong=dict(self.parents);wrong[str(self.root)]=[0,0]
        with self.assertRaisesRegex(worker.WorkerRefusal,'ancestor-drift'):
            worker.atomic_write(self.entry,wrong,str(self.swap),self.entry['sha256'],'NEW')
        self.assertEqual(b'prefix OLD suffix',self.path.read_bytes())
