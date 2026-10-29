"""Native environment observations under the already approved synthetic fixture boundary.

Unavailable mounted or loopback fixtures remain explicit non-pass observations.
These cases do not create disks, shares, credentials, or runtime installations.
"""
from __future__ import annotations
import json
import hashlib
import os
from pathlib import Path
import subprocess
import sys
import unittest
from hv2ref import jsonio, product, workspace
from hv2ref.errors import ContractError
from test_candidates import proposal as candidate_request
from test_windows_lifecycle import NativeLifecycleFixture, TIME, canonical, physical


@unittest.skipUnless(sys.platform == 'win32', 'native Windows environment; excluded from POSIX execution matrix')
class WindowsEnvironmentTests(NativeLifecycleFixture, unittest.TestCase):
    def windows_shell(self):
        shell = Path(os.environ['SYSTEMROOT']) / 'System32/WindowsPowerShell/v1.0/powershell.exe'
        self.assertTrue(shell.is_absolute() and shell.is_file(), str(shell))
        return str(shell)

    def volume_root(self, kind):
        config=json.loads(Path(os.environ['COLVIA_TEST_ENVIRONMENT']).read_bytes())
        volume=config[kind]
        root=Path(volume['DriveLetter'] + ':\\')
        if kind == 'fat32':
            # Setup uses independent volume identity, not the product's NTFS observer.
            letter = volume['DriveLetter']; self.assertRegex(letter, r'^[A-Z]$')
            command = ("$ErrorActionPreference='Stop'; $v=Get-Volume -DriveLetter " + letter +
                       "; [ordered]@{UniqueId=$v.UniqueId;FileSystem=$v.FileSystem;DriveType=$v.DriveType.ToString()} | ConvertTo-Json -Compress")
            query = subprocess.run([self.windows_shell(), '-NoProfile', '-NonInteractive', '-Command', command],
                                   capture_output=True, timeout=30)
            self.assertEqual(0, query.returncode, query.stdout + query.stderr)
            self.assertEqual(b'', query.stderr)
            observed = json.loads(query.stdout)
            self.assertEqual(volume['UniqueId'], observed['UniqueId'])
            self.assertEqual('FAT32', observed['FileSystem'])
            self.assertEqual('Fixed', observed['DriveType'])
        else:
            self.assertEqual('ntfs', kind)
            try:
                observed=jsonio.windows_path_observation(root,mutation=True)
            except (OSError,ContractError) as exc:
                print('NATIVE_ENVIRONMENT_UNAVAILABLE '+json.dumps({'kind':kind,'error':str(exc)}),flush=True)
                self.skipTest(kind+' fixture unavailable; no native PASS: '+str(exc))
            self.assertEqual(volume['UniqueId'].rstrip('\\'),observed['volume'])
        result=root/'colvia-windows-utm'/config['batch']/self._testMethodName
        result.mkdir(parents=True,exist_ok=False)
        return result

    def test_other_verified_local_ntfs_backup_is_allowed(self):
        root=self.volume_root('ntfs'); self.init()
        primary=jsonio.windows_path_observation(self.target,mutation=True)
        other=jsonio.windows_path_observation(root,mutation=True)
        self.assertNotEqual(primary['volume'],other['volume'])
        (self.target/'colvia').write_bytes(b'damaged synthetic launcher\n')
        preview=product.workspace_repair_preview(self.p,self.target,root/'backup',operation_id='other-volume',created_at=TIME)
        product.workspace_repair_apply(self.p,self.target,preview['request'],confirm_token=preview['confirm_token'])
        self.assertEqual(b'damaged synthetic launcher\n',(root/'backup/original/colvia').read_bytes())
        self.assert_product(self.p_candidate)
        saved=self.root/'other-ntfs-backup';saved.mkdir();rows=[]
        for original in sorted((root/'backup').rglob('*')):
            if not original.is_file():continue
            rel=original.relative_to(root/'backup');data=original.read_bytes();info=original.stat()
            copy=saved/rel;copy.parent.mkdir(parents=True,exist_ok=True);copy.write_bytes(data)
            self.assertEqual(data,copy.read_bytes());self.assertEqual(data,original.read_bytes())
            rows.append({'path':rel.as_posix(),'sha256':hashlib.sha256(data).hexdigest(),'size':len(data),
                         'creation_time':info.st_ctime_ns,'mtime_ns':info.st_mtime_ns,'attributes':info.st_file_attributes})
        (saved/'observed-metadata.json').write_bytes(canonical(rows))
        print('NATIVE_OTHER_NTFS_BACKUP '+json.dumps({'source_volume':primary['volume'],'backup_volume':other['volume'],'backup':str(root/'backup')}),flush=True)

    def test_fat32_mutation_refused_without_product_publication(self):
        root=self.volume_root('fat32'); (root/'sentinel').write_bytes(b'preserve')
        before=physical(root)
        with self.assertRaises(ContractError) as caught:
            preview=product.workspace_init_preview(self.p,root,authority_home_id='home-a',operation_id='fat32-init',created_at=TIME)
            product.workspace_init_apply(self.p,root,preview['request'],confirm_token=preview['confirm_token'])
        self.assertEqual('HV2-WINDOWS-FILESYSTEM',caught.exception.code)
        self.assertEqual(before,physical(root));self.assertFalse((root/'.hrn').exists())
        print('NATIVE_FAT32_REFUSAL '+json.dumps({'target':str(root),'code':caught.exception.code,'target_unchanged':True}),flush=True)

    def test_loopback_remote_reachability_and_mutation_refusal(self):
        config=json.loads(Path(os.environ['COLVIA_TEST_ENVIRONMENT']).read_bytes())
        target=Path(config['remote_sentinel'])
        try: before=target.read_bytes()
        except OSError as exc:
            print('NATIVE_ENVIRONMENT_UNAVAILABLE '+json.dumps({'kind':'remote','errno':exc.errno,'winerror':getattr(exc,'winerror',None),'error':str(exc)}),flush=True)
            self.skipTest('remote fixture unreachable; required native evidence unavailable')
        with self.assertRaises(ContractError) as caught:
            jsonio.windows_path_observation(target,mutation=True)
        self.assertEqual('HV2-WINDOWS-PATH',caught.exception.code)
        self.assertEqual(before,target.read_bytes())
        print('NATIVE_REMOTE_REFUSAL '+json.dumps({'reachable':True,'code':caught.exception.code,'sentinel_unchanged':True}),flush=True)


    def test_ntfs_role_primitives_and_cross_volume_replace(self):
        root = self.volume_root('ntfs')
        for name in ('staging', 'guard-scratch'):
            path = root / name
            before = jsonio.windows_path_observation(path, mutation=True, allow_missing=True)
            self.assertFalse(before['exists']); workspace._durable_directory(path)
            observed = jsonio.windows_path_observation(path, mutation=True)
            self.assertTrue(observed['exists']); self.assertTrue(observed['directory'])
        anchor = root / 'guard-scratch/writer.lock'
        with jsonio.exclusive_file_lock(anchor):
            # A second handle cannot read bytes while the exclusive lock is held.
            self.assertEqual(0, anchor.stat().st_size)
        self.assertEqual(b'', anchor.read_bytes())
        source = root / 'staging/input'; source.write_bytes(b'other-volume original\r\n')
        destination = self.root / 'destination'; destination.write_bytes(b'primary-volume original\n')
        self.assertNotEqual(jsonio.windows_path_observation(source, mutation=True)['volume'],
                            jsonio.windows_path_observation(destination, mutation=True)['volume'])
        before = physical(root); original = destination.read_bytes()
        with self.assertRaisesRegex(ContractError, 'cross-volume replace'):
            jsonio.replace_file(source, destination)
        self.assertEqual(before, physical(root)); self.assertEqual(original, destination.read_bytes())
        print('NATIVE_ROLE_PATHS ' + json.dumps({'roles': ['absent-staging', 'existing-staging', 'guard-scratch', 'anchor'],
              'filesystem': 'NTFS', 'cross_volume_replace': 'refused', 'unchanged': True}), flush=True)

    def test_fat32_staging_guard_and_external_backup_refuse(self):
        root = self.volume_root('fat32'); (root / 'sentinel').write_bytes(b'fat32 role sentinel\n')
        (root / 'guard-scratch').mkdir(); before = physical(root)
        for role, path in (('absent-staging', root / 'staging'), ('existing-scratch', root / 'guard-scratch')):
            with self.subTest(role=role), self.assertRaises(ContractError) as caught:
                workspace._durable_directory(path)
            self.assertEqual('HV2-WINDOWS-FILESYSTEM', caught.exception.code); self.assertEqual(before, physical(root))
        with self.assertRaises(ContractError) as caught:
            with jsonio.exclusive_file_lock(root / 'guard-scratch/writer.lock'): self.fail('FAT32 lock admitted')
        self.assertEqual('HV2-WINDOWS-FILESYSTEM', caught.exception.code); self.assertEqual(before, physical(root))
        self.init(); (self.target / 'colvia').write_bytes(b'damaged, retained original\n')
        # The already-established guard anchor is scratch. Freeze it before the
        # backup failure so the equality check covers the whole target namespace.
        with workspace.writer_guard(self.target): pass
        target_before = physical(self.target)
        with self.assertRaises(ContractError) as caught:
            preview = product.workspace_repair_preview(self.p, self.target, root / 'backup', operation_id='fat32-backup', created_at=TIME)
            product.workspace_repair_apply(self.p, self.target, preview['request'], confirm_token=preview['confirm_token'])
        self.assertEqual('HV2-WINDOWS-FILESYSTEM', caught.exception.code)
        self.assertEqual(target_before, physical(self.target)); self.assertEqual(before, physical(root))
        self.assertFalse((root / 'backup').exists())
        print('NATIVE_ROLE_PATHS ' + json.dumps({'roles': ['absent-staging', 'existing-scratch', 'anchor', 'external-backup'],
              'filesystem': 'FAT32', 'mutation': 'refused', 'unchanged': True}), flush=True)

    def test_powershell51_utf8_stdin_file_argv_and_exit(self):
        self.init()
        python=sys.executable; launcher=str(self.target/'colvia')
        def quote(value): return "'"+str(value).replace("'","''")+"'"
        prefix=("$ErrorActionPreference='Stop'; if($PSVersionTable.PSVersion.Major -ne 5 -or $PSVersionTable.PSVersion.Minor -ne 1){throw 'PS5.1 required'}; "
                "$enc=New-Object System.Text.UTF8Encoding $false; [Console]::InputEncoding=$enc; [Console]::OutputEncoding=$enc; $OutputEncoding=$enc; ")
        for mode in ('file','stdin'):
            with self.subTest(mode=mode):
                request=candidate_request(self.target,cid='idea-'+mode)
                request['payload']['title']='한글 공백 "quote" & $ 입력 '+mode
                path=self.root/("입력 '값' & $ "+mode+'.json');path.write_bytes(canonical(request))
                args=' & '+quote(python)+" -I -B "+quote(launcher)+" candidate add --input "
                if mode=='file':
                    command=prefix+args+quote(path)+'; exit $LASTEXITCODE'
                else:
                    # PS5.1's text pipeline adds a line ending. Preserve the
                    # canonical JSON input bytes through the child's stdin.
                    arguments='-I -B "'+launcher+'" candidate add --input -'
                    command=(prefix+"$si=New-Object Diagnostics.ProcessStartInfo; $si.FileName="+quote(python)+
                             "; $si.Arguments="+quote(arguments)+"; $si.UseShellExecute=$false; "
                             "$si.RedirectStandardInput=$true; $si.RedirectStandardOutput=$true; $si.RedirectStandardError=$true; "
                             "$si.StandardOutputEncoding=$enc; $si.StandardErrorEncoding=$enc; $p=[Diagnostics.Process]::Start($si); "
                             "$bytes=[IO.File]::ReadAllBytes("+quote(path)+"); $p.StandardInput.BaseStream.Write($bytes,0,$bytes.Length); "
                             "$p.StandardInput.Close(); $out=$p.StandardOutput.ReadToEnd(); $err=$p.StandardError.ReadToEnd(); "
                             "$p.WaitForExit(); [Console]::Out.Write($out); [Console]::Error.Write($err); exit $p.ExitCode")
                result=subprocess.run([self.windows_shell(),'-NoProfile','-NonInteractive','-Command',command],cwd=self.target,capture_output=True,timeout=60)
                self.assertEqual(0,result.returncode,result.stdout+result.stderr)
                self.assertEqual(b'',result.stderr)
                self.assertEqual('saved',json.loads(result.stdout)['classification'])
                print('NATIVE_POWERSHELL_INPUT '+json.dumps({'mode':mode,'utf8':True,'exit':result.returncode}),flush=True)
        before=physical(self.target)
        command=prefix+' & '+quote(python)+' -I -B '+quote(launcher)+' unknown-command; exit $LASTEXITCODE'
        result=subprocess.run([self.windows_shell(),'-NoProfile','-NonInteractive','-Command',command],cwd=self.target,capture_output=True,timeout=30)
        self.assertEqual(2,result.returncode,result.stdout+result.stderr);self.assertEqual(before,physical(self.target))
