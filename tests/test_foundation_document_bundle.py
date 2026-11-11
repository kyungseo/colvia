"""Fixed dependency archive with real isolated Python entry; not installation."""
import hashlib,json,os,subprocess,sys,tempfile,unittest,zipfile
from pathlib import Path
from distribution.document_worker import build,MEMBERS
import test_foundation_document_worker as fixture

class BundleTests(unittest.TestCase):
    def test_deterministic_complete_dependency_identity_and_no_overwrite(self):
        with tempfile.TemporaryDirectory(prefix='worker-bundle-') as name:
            root=Path(name);source=Path(__file__).resolve().parents[1]/'src'
            first=build(source,root/'one.pyz');second=build(source,root/'two.pyz')
            self.assertEqual(first,second);self.assertEqual((root/'one.pyz').read_bytes(),(root/'two.pyz').read_bytes())
            with zipfile.ZipFile(root/'one.pyz') as archive:
                manifest=json.loads(archive.read('bundle-manifest.json'))
                self.assertEqual(set(MEMBERS)|{'__main__.py'},set(manifest['files']))
                for path,digest in manifest['files'].items():self.assertEqual(digest,hashlib.sha256(archive.read(path)).hexdigest())
            with self.assertRaises(FileExistsError):build(source,root/'one.pyz')

@unittest.skipUnless(sys.platform=='darwin','document operation qualification')
class BundleExecutionTests(unittest.TestCase):
    def test_isolated_archive_entry_has_no_source_checkout_import(self):
        case=fixture.WorkerTests();case.setUp()
        try:
            archive=case.root/'worker.pyz';build(Path(__file__).resolve().parents[1]/'src',archive)
            spec=dict(version=1,files={'Output':case.entry},parents=case.parents,outputs=['Output'],swap={},
                parser='',parser_sha256='0'*64,claims={},approved_external_links=[],link_metadata={})
            path=case.root/'spec.json';path.write_text(json.dumps(spec))
            request=json.dumps(dict(tool='document_read',arguments={'file_ids':['Output']})).encode()
            result=subprocess.run([sys.executable,'-I','-S','-B',str(archive),'--spec',str(path),'--operation','read'],
                input=request,cwd=case.slot,env={'PATH':'/usr/bin:/bin','TMPDIR':str(case.slot)},capture_output=True,timeout=5)
            self.assertEqual(0,result.returncode,result.stderr);value=json.loads(result.stdout)
            self.assertTrue(value['ok']);self.assertEqual('OLD',value['result']['files'][0]['content'])
            self.assertEqual(b'prefix OLD suffix',case.path.read_bytes())
        finally:case.tearDown()
