"""Installed wrappers must emit UTF-8 even with a legacy redirected stream."""
import importlib.util,json,subprocess,sys,tempfile,unittest
from pathlib import Path
spec=importlib.util.spec_from_file_location('bundle_encoding',Path(__file__).parents[1]/'distribution/foundation_bundle.py')
bundle=importlib.util.module_from_spec(spec);spec.loader.exec_module(bundle)

class WrapperEncodingTests(unittest.TestCase):
    def test_both_installed_entries_preserve_unicode_in_output_and_errors(self):
        for module in ('managed_entry','manager_entry'):
            for failure in (False,True):
                with self.subTest(module=module,failure=failure),tempfile.TemporaryDirectory(prefix='wrapper-encoding-') as tmp:
                    root=Path(tmp).resolve();lib=root/'lib/colvia';lib.mkdir(parents=True)
                    (lib/'__init__.py').write_bytes(b'')
                    code="import json,sys\ndef main():\n    print(json.dumps({'message':'한글 결과'},ensure_ascii=False))\n"
                    code+="    print('한글 오류\\udcff',file=sys.stderr)\n    return "+('2' if failure else '0')+'\n'
                    (lib/(module+'.py')).write_text(code,encoding='utf-8')
                    wrapper=root/'entry.py';wrapper.write_bytes(bundle.wrapper(module))
                    start="import sys,runpy;sys.stdout.reconfigure(encoding='cp1252');sys.stderr.reconfigure(encoding='cp1252',errors='backslashreplace');runpy.run_path(sys.argv[1],run_name='__main__')"
                    result=subprocess.run([sys.executable,'-I','-B','-X','warn_default_encoding','-W','error::EncodingWarning','-c',start,str(wrapper)],capture_output=True,timeout=10)
                    self.assertEqual(2 if failure else 0,result.returncode,result.stderr.decode('utf-8','replace'))
                    self.assertEqual({'message':'한글 결과'},json.loads(result.stdout.decode('utf-8')))
                    self.assertEqual('한글 오류\\udcff\n',result.stderr.decode('utf-8').replace('\r\n','\n'))
