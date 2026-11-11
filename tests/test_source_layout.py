"""Source README assembly and explicit source selection; no real installation."""
import argparse
import contextlib
import hashlib
import importlib.util
import io
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tarfile
import tempfile
import unittest
from unittest.mock import patch
from distribution.source_layout import read_checkout, prepare_source, source_path
from hv2ref import product
from hv2ref.errors import ContractError

ROOT = Path(__file__).resolve().parents[1]


def module(name, rel):
    spec = importlib.util.spec_from_file_location(name, ROOT / rel)
    obj = importlib.util.module_from_spec(spec); spec.loader.exec_module(obj)
    return obj


class SourceLayoutTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='readme-layout-')
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name).resolve()

    def checkout(self):
        source = self.base / 'checkout'
        for name in product.OFFICIAL_V2_MANAGED_PATHS:
            p = source / name; p.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(ROOT / name, p)
        p = source / 'distribution/README-installed.md'; p.parent.mkdir(); shutil.copy2(ROOT / p.relative_to(source), p)
        return source

    def test_public_readme_never_enters_prepared_inventory(self):
        checkout = read_checkout(ROOT)
        self.assertEqual(checkout['payload']['README.md'], (ROOT / 'distribution/README-installed.md').read_bytes())
        self.assertNotEqual(checkout['payload']['README.md'], (ROOT / 'README.md').read_bytes())
        self.assertEqual(tuple(checkout['payload']), product.CONTINUATION_MANAGED_PATHS)
        target = self.base / 'prepared'; prepare_source(ROOT, target)
        observed = product.workspace_candidate(target)
        self.assertEqual(observed['payload'], checkout['payload'])
        self.assertEqual(observed['release_ref'], checkout['release_ref'])
        self.assertFalse((target / 'assets').exists())
        self.assertFalse((target / 'distribution').exists())
        self.assertEqual(next(e['source_path'] for e in json.loads((target / 'preparation.json').read_text())['entries'] if e['path']=='README.md'), 'distribution/README-installed.md')

    def test_missing_unsafe_or_shared_mapped_input_does_not_fall_back(self):
        source = self.checkout(); p=source/'distribution/README-installed.md'; raw=p.read_bytes();p.unlink()
        with self.assertRaises((OSError,ContractError)):read_checkout(source)
        p.symlink_to(source/'README.md')
        with self.assertRaises((OSError,ContractError)):read_checkout(source)
        p.unlink();p.write_bytes(raw);os.link(p,self.base/'shared')
        with self.assertRaises((OSError,ContractError)):read_checkout(source)

    def test_drift_during_read_is_refused(self):
        source=self.checkout();p=source/'distribution/README-installed.md';original=product._serial_file;seen=0
        def changing(path):
            nonlocal seen
            value=original(path)
            if path==p:
                seen+=1
                if seen==1:p.write_bytes(value+b'changed\n')
            return value
        with patch.object(product,'_serial_file',side_effect=changing),self.assertRaises(ContractError):read_checkout(source)

    def test_existing_output_is_preserved(self):
        out=self.base/'out';out.mkdir();(out/'keep').write_text('keep')
        with self.assertRaises(ValueError):prepare_source(ROOT,out)
        self.assertEqual((out/'keep').read_text(),'keep')

    def test_source_init_requires_explicit_source_without_writing(self):
        target=self.base/'target';target.mkdir();(target/'keep').write_text('keep')
        cmd=[sys.executable,'-I','-B',str(ROOT/'colvia'),'--source-checkout','init','--profile','continuation-1','--target',str(target)]
        before={str(p.relative_to(target)):p.read_bytes() for p in target.rglob('*') if p.is_file()}
        result=subprocess.run(cmd,capture_output=True,timeout=20)
        self.assertEqual(result.returncode,2,result.stderr);self.assertIn(b'--source',result.stderr)
        self.assertEqual(before,{str(p.relative_to(target)):p.read_bytes() for p in target.rglob('*') if p.is_file()})
        source=self.base/'prepared';prepare_source(ROOT,source)
        args=cmd+['--source',str(source),'--authority-home-id','home-test','--operation-id','init-test','--observed-at','2026-01-01T00:00:00Z']
        result=subprocess.run(args,capture_output=True,timeout=20)
        self.assertEqual(result.returncode,0,result.stdout+result.stderr)
        request=json.loads(result.stdout)['request'];self.assertEqual(request['plan']['candidate_release'],product.workspace_candidate(source)['release_ref'])
        self.assertEqual(before,{str(p.relative_to(target)):p.read_bytes() for p in target.rglob('*') if p.is_file()})

    def test_windows_and_official_preparation_use_mapped_input(self):
        for kind,window in [('windows','windows-2'),('official','official-execution-2')]:
            out=self.base/kind
            result=subprocess.run([sys.executable,'-I','-B',str(ROOT/f'scripts/prepare-{kind}.py'),'--source',str(ROOT),'--output',str(out)],capture_output=True,timeout=30)
            self.assertEqual(result.returncode,0,result.stdout+result.stderr)
            candidate=product.workspace_candidate(out)
            self.assertEqual(candidate['release_ref']['inventory_id'],window)
            self.assertEqual(candidate['payload']['README.md'],(ROOT/'distribution/README-installed.md').read_bytes())

    def test_macos_both_profiles_use_mapped_readme(self):
        mac=module('mac_readme','distribution/macos.py');supply=self.base/'supply';supply.mkdir();(supply/mac.ARCHIVE).write_bytes(b'synthetic')
        out=self.base/'mac'
        with patch.object(mac,'runtime_catalog',return_value=(b'objects',b'checksums')),patch.object(mac,'licenses',return_value={'license':b'synthetic'}),patch.object(mac,'build_notice_app',return_value={}):
            result=mac.prepare(ROOT,supply,out,version='test-readme',notice_build_version='2',origin='https://github.com/example/example/releases/download/test',fixture_root=self.base/'store')
        with tarfile.open(out/'product.tar') as archive:
            readmes=[archive.extractfile(m).read() for m in archive if m.name.endswith('/README.md') and m.name.count('/')==1]
        self.assertEqual(len(readmes),2)
        self.assertTrue(all(b==(ROOT/'distribution/README-installed.md').read_bytes() for b in readmes))
        self.assertEqual(set(result['profiles']),{'continuation-1','official-execution-2'})

    def test_windows_manager_supplies_source(self):
        mod=module('windows_readme_manage','distribution/windows/manage.py')
        args=argparse.Namespace(command='install',apply=False,input=None,confirm=None,recover=False,to=None)
        argv=mod.lifecycle_args(args,self.base/'project')
        self.assertEqual(argv[argv.index('--source')+1],str(mod.CORE))

    def test_macos_manager_supplies_source(self):
        mod=module('mac_readme_manage','distribution/manager.py')
        args=argparse.Namespace(command='install',target=self.base/'project',profile='continuation-1',apply=False,input=None,confirm=None,recover=False,save=None,to=None,backup=None)
        store=self.base/'store';source=store/'releases'/'test-release';source.mkdir(parents=True); captured=[]
        def stop(argv):captured.append(argv);raise RuntimeError('captured-before-execution')
        with patch.dict(mod.CONFIG,{'profiles':{'continuation-1':{'release':{'id':'test-release'}}}}),patch.object(mod,'selected_profile',return_value='continuation-1'),patch.object(mod,'validate_payload'),patch.object(mod,'runtime_path',return_value=self.base/'runtime'),patch.object(mod,'run_lifecycle',side_effect=stop):
            with self.assertRaisesRegex(RuntimeError,'captured-before-execution'):mod.lifecycle(args,store)
        self.assertEqual(captured[0][captured[0].index('--source')+1],str(source))

if __name__=='__main__':unittest.main()
