import hashlib,subprocess,unittest
from dataclasses import replace
from colvia.codec import RecordError
from colvia.updates.bootstrap import inspect_bundle,render
from test_foundation_package import PackageTests

class BootstrapTests(unittest.TestCase):
    setUp=PackageTests.setUp
    tearDown=PackageTests.tearDown
    archive=PackageTests.archive
    def test_mac_script_is_syntax_valid_and_uses_pinned_runtime_only(self):
        out,_=self.archive();bundle=inspect_bundle(out);script=render(bundle,'https://downloads.example.invalid/colvia/bundle.zip')
        p=subprocess.run(['/bin/sh','-n'],input=script,text=True,capture_output=True,timeout=5)
        self.assertEqual(0,p.returncode,p.stderr);self.assertIn(bundle.sha256,script)
        self.assertIn(' -I -B ',script);self.assertNotIn('python3 ',script);self.assertNotIn('curl |',script)
    def test_mac_resume_rejects_bad_arguments_before_preparation(self):
        out,_=self.archive();script=render(inspect_bundle(out),'https://downloads.example.invalid/colvia/bundle.zip')
        for args in (['--resume-install'],['--resume-install','bad;operation'],['--unexpected','first'],['--resume-install','a'*161],['--resume-repair','bad;operation']):
            result=subprocess.run(['/bin/sh','-s','--',*args],input=script,text=True,capture_output=True,timeout=5)
            self.assertEqual(2,result.returncode);self.assertNotIn('Preparing Colvia',result.stdout)
        self.assertIn('set -- --operation "$operation"',script);self.assertIn('"$command"',script)

    def test_unverified_bundle_cannot_generate_installer(self):
        out,_=self.archive(mutate=lambda name,raw:b'altered' if name=='product.py' else raw)
        with self.assertRaisesRegex(RecordError,'bootstrap-content-mismatch'):inspect_bundle(out)
    def test_non_https_and_shell_spelling_are_refused(self):
        out,_=self.archive();bundle=inspect_bundle(out)
        for url in ('http://example.invalid/a','https://user@example.invalid/a','https://example.invalid/a?token=x',"https://example.invalid/a'bad"):
            with self.subTest(url=url),self.assertRaises(RecordError):render(bundle,url)
    def test_windows_template_preserves_failure_and_passes_management_identity(self):
        self.manifest['os']='windows';self.manifest['architecture']='arm64';out,_=self.archive();bundle=inspect_bundle(out)
        script=render(bundle,'https://downloads.example.invalid/colvia/arm64.zip')
        self.assertIn("$expectedArchitecture = 'Arm64'",script);self.assertIn('-MaximumRedirection 0',script)
        self.assertIn(bundle.manifest_sha256,script);self.assertIn('bootstrap-install-or-update',script)
        self.assertNotIn('Remove-Item',script)
        self.assertIn("[string]$RetryInstall = ''",script);self.assertIn('@managerArgs',script);self.assertIn("@('bootstrap-repair-runtime', '--operation', $RepairRuntime)",script)
        self.assertIn("@('bootstrap-resume-install', '--operation', $ResumeInstall)",script)
        self.assertIn("@('bootstrap-resume-repair', '--operation', $ResumeRepair)",script)
