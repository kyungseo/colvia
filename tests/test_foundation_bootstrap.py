import hashlib,subprocess,unittest,zipfile
from dataclasses import replace
from colvia.codec import RecordError
from colvia.updates.bootstrap import inspect_bundle,render,render_windows_preflight
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
    def test_mac_existing_home_uses_only_verified_installed_entry(self):
        import json,os,sys
        from pathlib import Path
        if sys.platform!='darwin':self.skipTest('Darwin shell and filesystem tools required')
        out,_=self.archive()
        script=render(inspect_bundle(out),'https://downloads.example.invalid/colvia/bundle.zip')
        # Abort on first-install branch entry, before any preparation or network.
        stage='stage="$parent/Colvia-bootstrap-'
        self.assertEqual(1,script.count(stage))
        script=script.replace(stage,'exit 91\n'+stage,1)
        base=out.parent
        home=base/'home';home.mkdir()
        parent=home/'Library'/'Application Support';parent.mkdir(parents=True)
        install=parent/'Colvia'; marker=home/'called'
        def run():
            return subprocess.run(['/bin/sh','-s'],input=script,text=True,capture_output=True,
                                  env=dict(os.environ,HOME=str(home)),timeout=10)
        if subprocess.check_output(['/usr/bin/uname','-m'],text=True).strip()!='arm64':
            self.skipTest('Apple Silicon shell required')
        self.assertEqual(91,run().returncode)
        install.mkdir(mode=0o700)
        self.assertEqual(2,run().returncode)
        bin_dir=install/'bin';bin_dir.mkdir(mode=0o700)
        launcher=bin_dir/'colvia-manage'
        launcher.write_bytes(b'#!/bin/sh\nprintf "%s\\n" "$@" > "$HOME/called"\nexit 19\n')
        launcher.chmod(0o700)
        record=install/'entry.json'
        identity=dict(version=1,os='macos',architecture='arm64',sha256=hashlib.sha256(launcher.read_bytes()).hexdigest())
        record.write_text(json.dumps(identity))
        record.chmod(0o600)
        result=run()
        self.assertEqual(19,result.returncode,result.stderr)
        self.assertEqual('update\n',marker.read_text())
        marker.unlink()
        raw=launcher.read_bytes()
        launcher.write_bytes(raw+b'\n# changed\n')
        result=run()
        self.assertEqual(2,result.returncode,result.stderr)
        self.assertIn('explicit Colvia installation recovery',result.stderr)
        self.assertFalse(marker.exists())
        launcher.write_bytes(raw)
        os.link(launcher,bin_dir/'second-name')
        self.assertEqual(2,run().returncode)
        self.assertFalse(marker.exists())
        (bin_dir/'second-name').unlink()
        launcher.unlink();launcher.symlink_to(base/'nonexistent')
        self.assertEqual(2,run().returncode)
        self.assertFalse(marker.exists())
        self.assertEqual({'Colvia'}, {p.name for p in parent.iterdir()})

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
    def test_windows_native_architecture_is_bound_before_path_and_space_probes(self):
        self.manifest['os']='windows';self.manifest['architecture']='x64'
        out,_=self.archive();bundle=inspect_bundle(out)
        for arch,machine in (('x64','0x8664'),('arm64','0xAA64')):
            with self.subTest(arch=arch):
                probe=render_windows_preflight(replace(bundle,architecture=arch))
                guard=probe.index(f'Assert-ColviaNativeArchitecture $native {machine}')
                self.assertLess(guard,probe.index('$parent = Get-ColviaInstallParent $native'))
                self.assertIn('IsWow64Process2',probe)
                self.assertNotIn('RuntimeInformation',probe)

    def test_windows_template_preserves_failure_and_passes_management_identity(self):
        self.manifest['os']='windows';self.manifest['architecture']='arm64';out,_=self.archive();bundle=inspect_bundle(out)
        script=render(bundle,'https://downloads.example.invalid/colvia/arm64.zip')
        self.assertIn("Assert-ColviaNativeArchitecture $native 0xAA64",script);self.assertIn('-MaximumRedirection 0',script)
        self.assertIn(bundle.manifest_sha256,script);self.assertIn('bootstrap-install-or-update',script)
        self.assertNotIn('Remove-Item',script)
        self.assertIn("[string]$RetryInstall = ''",script);self.assertIn('@managerArgs',script);self.assertIn("@('bootstrap-repair-runtime', '--operation', $RepairRuntime)",script)
        self.assertIn("@('bootstrap-resume-install', '--operation', $ResumeInstall)",script)
        self.assertIn("@('bootstrap-resume-repair', '--operation', $ResumeRepair)",script)
        with zipfile.ZipFile(out) as archive:
            expanded = sum(item.file_size for item in archive.infolist())
        allowance = 16 * 1024**2
        self.assertEqual(expanded, bundle.expanded_length)
        preflight=render_windows_preflight(bundle)
        self.assertIn(preflight.rsplit('Assert-ColviaFreeSpace',1)[0],script)
        lookup=script.index('$homeItem = Get-ColviaExistingHome')
        launch=script.index('& $installedPython @installedArgs')
        self.assertLess(script.index('$parent = Get-ColviaInstallParent'),lookup)
        self.assertLess(lookup,launch)
        self.assertLess(launch,script.index('exit $status'))
        self.assertLess(script.index('exit $status'),script.index("$stage = Join-Path"))
        self.assertIn('[IO.FileShare]::Read',script)
        self.assertIn("[Diagnostics.ProcessStartInfo]::new($launcher.FullName, '--inspect-only')",script)
        initial = script.index(f"Assert-ColviaFreeSpace $native $parent {out.stat().st_size + expanded + allowance} 'download-and-expand'")
        recheck = script.index(f"Assert-ColviaFreeSpace $native $stage {expanded + allowance} 'expand'")
        self.assertLess(initial, script.index('New-Item -ItemType Directory -Path $stage'))
        self.assertLess(initial, script.index('Invoke-WebRequest -Uri'))
        self.assertLess(script.index('Get-FileHash -LiteralPath'), recheck)
        self.assertLess(recheck, script.index('New-Item -ItemType Directory -Path $runtime'))
