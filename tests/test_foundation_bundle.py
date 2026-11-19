import hashlib,importlib.util,os,subprocess,sys,tempfile,unittest,zipfile
from pathlib import Path
from colvia.guide_topics import GUIDE_FILES, TOPIC_NAMES
from colvia.codec import RecordError,decode_canonical
from colvia.updates.bootstrap import inspect_bundle
from colvia.updates.package import stage_archive
from colvia.updates.slots import RuntimeSlots

spec=importlib.util.spec_from_file_location('foundation_bundle',Path(__file__).parents[1]/'distribution/foundation_bundle.py')
bundle=importlib.util.module_from_spec(spec);spec.loader.exec_module(bundle)

class BundleTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(prefix='bundle-');self.root=Path(self.tmp.name)
        self.runtime=self.root/'runtime';self.runtime.mkdir();(self.runtime/'python').write_bytes(b'fixture not interpreter');(self.runtime/'python').chmod(0o700)
        self.verifier=self.root/'verifier';self.verifier.mkdir();(self.verifier/'fixture_dependency.py').write_text('# fixture only\n')
        self.native=self.root/'native';self.native.write_bytes(b'fixture not executable format');self.native.chmod(0o700)
        self.anchor=self.root/'anchor';self.anchor.write_bytes(b'fixed fixture root; never verify as signed')
        self.guide=self.root/'guide';self.guide.write_text('# Start\n');self.notice=self.root/'notice';self.notice.write_text('Synthetic fixture notice\n')
        self.kw=dict(source=Path(__file__).parents[1],runtime=self.runtime,verifier=self.verifier,native_entry=self.native,anchor=self.anchor,
            configuration=dict(channel='preview',metadata_url='https://example.invalid/metadata/',target_url='https://example.invalid/targets/',target='release.zip'),
            guides={'manual/en/README.md':self.guide,'manual/ko/README.md':self.guide},licenses={'LICENSE':self.notice,'THIRD_PARTY_NOTICES.md':self.notice},
            output=self.root/'bundle.zip',release='synthetic',sequence=1,os_name='macos',architecture='arm64',python_entry='python',python_version='3.14.7',sqlite_version='3.54.0')
    def tearDown(self):self.tmp.cleanup()
    def test_packaged_wrappers_resolve_bundled_code_in_isolated_python(self):
        result=bundle.assemble(**self.kw);self.assertFalse(result['runtime_execution_verified'])
        with zipfile.ZipFile(self.kw['output']) as z:
            self.assertEqual((self.kw['source']/'adapters/foundation-work/SKILL.md').read_bytes(),
                             z.read('adapters/colvia-work/SKILL.md'))
            for name in ('product.py','manager.py'):self.assertIn(b"parent/'lib'",z.read(name))
        target=dict(length=result['length'],sha256=result['sha256'],custom={'colvia':dict(version=1,channel='preview',os='macos',architecture='arm64',release='synthetic',sequence=1,manifest_sha256=result['manifest_sha256'])})
        slots=RuntimeSlots.create(self.root/'slots',os_name='macos',architecture='arm64')
        staged=stage_archive(self.kw['output'],root=slots.root,slot='candidate',target=target,channel='preview',os_name='macos',architecture='arm64')
        self.assertEqual((self.kw['source']/'adapters/foundation-work/SKILL.md').read_bytes(),
                         (Path(staged.product).parent/'adapters/colvia-work/SKILL.md').read_bytes())
        # Host Python only checks packaged import/help. It is deliberately not
        # run as the fake pinned Python and cannot open a managed authority.
        env=dict(os.environ,PYTHONPATH='/invalid',PYTHONHOME='/invalid')
        p=subprocess.run([sys.executable,'-I','-B',staged.manager,'--help'],env=env,capture_output=True,text=True,timeout=10)
        self.assertEqual(0,p.returncode,p.stderr);self.assertIn('connect-preview',p.stdout)
    def stage_checked(self,result,slots=None):
        target=dict(length=result['length'],sha256=result['sha256'],custom={'colvia':dict(version=1,channel='preview',os=self.kw['os_name'],architecture=self.kw['architecture'],release='synthetic',sequence=1,manifest_sha256=result['manifest_sha256'])})
        if slots is None:
            slots=RuntimeSlots.create(self.root/('slots-'+self.kw['architecture']),os_name=self.kw['os_name'],architecture=self.kw['architecture'])
        return stage_archive(self.kw['output'],root=slots.root,slot='candidate',target=target,channel='preview',os_name=self.kw['os_name'],architecture=self.kw['architecture'])
    def test_windows_generated_manifest_passes_slot_validation(self):
        for architecture in ('arm64','x64'):
            self.kw.update(os_name='windows',architecture=architecture,output=self.root/(architecture+'.zip'))
            result=bundle.assemble(**self.kw)
            staged=self.stage_checked(result)
            for filename in GUIDE_FILES.values():
                self.assertEqual((self.kw['source']/'adapters/foundation-work'/filename).read_bytes(),
                                 (Path(staged.product).parent/'adapters/colvia-work'/filename).read_bytes())
    def test_receiver_inventory_is_packaged_without_registration(self):
        from colvia.updates.notice_app import PARTS,PREFIX
        app=self.root/'ColviaWork.app';app.mkdir()
        for part in PARTS:
            path=app/part;path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(b'inert receiver fixture')
            if part.endswith('/ColviaWork'):path.chmod(0o700)
        result=bundle.assemble(**self.kw,notice_app=app)
        with zipfile.ZipFile(self.kw['output']) as z:
            self.assertTrue({PREFIX+p for p in PARTS}<=set(z.namelist()))
            self.assertIn('native-notices',decode_canonical(z.read('manifest.json'))['features'])
        self.stage_checked(result)
        self.assertFalse(result['runtime_execution_verified'])

    def test_verified_guide_from_staged_bundle(self):
        import contextlib, io, json
        from unittest.mock import patch
        from colvia.cli import main
        from colvia.managed_entry import ManagedEntry
        from colvia.management import ManagerHome

        result = bundle.assemble(**self.kw)
        home = ManagerHome.create(self.root/'home', os_name='macos', architecture='arm64')
        slot = self.stage_checked(result, home.slots)
        pointer = dict(slot=slot.slot, manifest_sha256=result['manifest_sha256'])
        home.slots.initialize(pointer)
        with patch('colvia.managed_entry.process_runtime', return_value=(slot.python, '3.14.7', '3.54.0')), \
             patch('colvia.managed_entry.current_platform', return_value=('macos', 'arm64')):
            entry = ManagedEntry(home.root, pointer=pointer)
        with patch.object(entry, 'workspace', side_effect=AssertionError('guide opened records')):
            for topic, filename in GUIDE_FILES.items():
                args = ['guide'] + ([topic] if topic else [])
                expected = (self.kw['source']/'adapters/foundation-work'/filename).read_bytes().decode('utf-8')
                for structured in (False, True):
                    output = io.StringIO()
                    with contextlib.redirect_stdout(output):
                        self.assertEqual(0, main((['--json'] if structured else []) + args, entry=entry))
                    if structured:
                        self.assertEqual({'guide': expected}, json.loads(output.getvalue()))
                    else:
                        self.assertEqual(expected + '\n', output.getvalue())
            self.assertIn('read `guide management` before submitting', entry.guide('work'))
            short = entry.guide()
            self.assertLessEqual(len(short.encode()), 5000)
            self.assertLessEqual(len(short.splitlines()), 75)
            for topic in TOPIC_NAMES:
                self.assertIn('guide ' + topic, short)
            document = Path(slot.product).parent/'adapters/colvia-work/work.md'
            raw = document.read_bytes()
            document.write_bytes(b'X' + raw[1:])
            with self.assertRaisesRegex(RecordError, 'managed-guide-changed'):
                entry.guide('work')
            document.unlink()
            with self.assertRaisesRegex(RecordError, 'managed-guide-unavailable'):
                entry.guide('work')

    def test_foundation_guides_resolve_inside_the_prepared_archive(self):
        import posixpath,re
        from urllib.parse import unquote,urlsplit
        allowed_install_links = {
            'https://colvia.github.io/downloads/',
            'https://colvia.github.io/downloads/#en',
            'https://colvia.github.io/downloads/#ko',
            'https://colvia.github.io/downloads/preview/macos-arm64/install.sh',
            'https://colvia.github.io/downloads/preview/windows-x64/install.ps1',
            'https://colvia.github.io/downloads/preview/windows-arm64/install.ps1',
        }
        self.kw['guides']=bundle.guide_sources(self.kw['source'])
        guides={**self.kw['guides'],
                **{'adapters/colvia-work/'+name:self.kw['source']/'adapters/foundation-work'/name
                   for name in GUIDE_FILES.values()}}
        result=bundle.assemble(**self.kw)
        with zipfile.ZipFile(self.kw['output']) as archive:
            names=set(archive.namelist())
            inventory={entry['path']:entry for entry in decode_canonical(archive.read('manifest.json'))['inventory']}
            for name,source in guides.items():
                raw=archive.read(name)
                self.assertEqual(source.read_bytes(),raw,name)
                unexpected_controls = {byte for byte in raw if (byte < 32 and byte not in (9, 10, 13)) or byte == 127}
                self.assertFalse(unexpected_controls, (name, unexpected_controls))
                self.assertEqual(hashlib.sha256(raw).hexdigest(),inventory[name]['sha256'],name)
                # Only inspect prose links, not examples inside fenced blocks.
                body=re.sub(r'^```[^\n]*\n.*?^```[^\n]*$', '', raw.decode('utf-8'), flags=re.M|re.S)
                self.assertNotIn('docs/README.md',raw.decode('utf-8'))
                for link in re.findall(r'\[[^\]]*\]\(([^)]+)\)|href="([^"]+)"',body):
                    link=next(value for value in link if value)
                    url=urlsplit(link)
                    if url.scheme or url.netloc:
                        self.assertIn(link, allowed_install_links, (name, link))
                        continue
                    self.assertFalse(url.path.startswith('/'), (name, link))
                    target=posixpath.normpath(posixpath.join(posixpath.dirname(name),unquote(url.path))) if url.path else name
                    self.assertIn(target,names,(name,link))
                    if url.fragment:
                        target_body=archive.read(target).decode('utf-8')
                        target_body=re.sub(r'^```[^\n]*\n.*?^```[^\n]*$', '', target_body, flags=re.M|re.S)
                        explicit=set(re.findall(r'<a\s+(?:id|name)="([^"]+)"',target_body))
                        # Linked headings here use unique plain English or Korean text.
                        headings=re.findall(r'^#{1,6}\s+([^\n]+)$',target_body,re.M)
                        slugs={re.sub(r'[^\w -]','',heading.strip().lower()).replace(' ','-') for heading in headings}
                        self.assertIn(unquote(url.fragment),explicit|slugs,(name,link))
            entry=archive.read('README.md').decode('utf-8')
            self.assertIn('(manual/en/README.md)',entry)
            self.assertIn('(manual/ko/README.md)',entry)
        self.assertFalse(result['runtime_execution_verified'])

    def test_document_assets_match_lib_members_and_do_not_enable_dispatch(self):
        from distribution.document_worker import build,MEMBERS
        from colvia.execution.assets import inspect_assets
        from colvia.storage.files import PosixFiles
        result=bundle.assemble(**self.kw,document_assets=True)
        staged=self.stage_checked(result);slot=Path(staged.python).parent.parent
        with zipfile.ZipFile(self.kw['output']) as z:
            manifest=decode_canonical(z.read('manifest.json'));inventory={e['path']:e for e in manifest['inventory']}
            worker=self.root/'worker.pyz';build(self.kw['source']/'src',worker)
            self.assertEqual(worker.read_bytes(),z.read('execution/document-worker.pyz'))
            with zipfile.ZipFile(worker) as w:
                for name in MEMBERS:self.assertEqual(hashlib.sha256(w.read(name)).hexdigest(),inventory['lib/'+name]['sha256'])
            self.assertIn(b'execution/marked-LICENSE.md',z.read('THIRD_PARTY_NOTICES.md'))
            self.assertEqual('100644',inventory['execution/marked.umd.js']['mode'])
            status=inspect_assets(slot,manifest,PosixFiles(),platform=('macos','arm64'))
            self.assertFalse(status['dispatch_available']);self.assertEqual('prepared-dispatch-unavailable',status['state'])
        self.kw['output']=self.root/'without-assets.zip';bundle.assemble(**self.kw)
        with zipfile.ZipFile(self.kw['output']) as z:
            base=decode_canonical(z.read('manifest.json'))
            self.assertEqual(set(base),set(manifest))
            for key in ('features','read_capabilities','write_capabilities'):self.assertEqual(base[key],manifest[key])
            self.assertFalse(any(n.startswith('execution/') for n in z.namelist()))

    def test_reserved_namespace_cannot_be_injected_and_windows_refuses_assets(self):
        for name in ('execution/assets.json','Execution/assets.json','execution'):
            self.kw['guides'][name]=self.guide
            with self.assertRaisesRegex(RecordError,'bundle-execution-namespace'):bundle.assemble(**self.kw)
            del self.kw['guides'][name];self.assertFalse(self.kw['output'].exists())
        self.kw['licenses']['execution/worker.pyz']=self.notice
        with self.assertRaisesRegex(RecordError,'bundle-execution-namespace'):bundle.assemble(**self.kw)
        del self.kw['licenses']['execution/worker.pyz']
        for architecture in ('arm64','x64'):
            self.kw.update(os_name='windows',architecture=architecture)
            with self.assertRaisesRegex(RecordError,'bundle-document-platform'):bundle.assemble(**self.kw,document_assets=True)
        self.assertFalse(self.kw['output'].exists())

    def test_worker_static_dependencies_must_be_in_archive(self):
        from distribution.document_worker import archive_bytes,MEMBERS,source_bytes
        files={name:source_bytes(self.kw['source']/'src'/name) for name in MEMBERS}
        files['colvia/platforms/darwin_document_worker.py']+=b'\nfrom colvia.unbundled import unsafe\n'
        with self.assertRaisesRegex(ValueError,'dependency missing'):archive_bytes(files)

    def test_package_alias_dependencies_and_relative_import_errors(self):
        from distribution.document_worker import archive_bytes,MEMBERS,source_bytes
        original={name:source_bytes(self.kw['source']/'src'/name) for name in MEMBERS}
        member='colvia/platforms/darwin_document_worker.py'
        for line in (b'from colvia import missing',b'from colvia.platforms import missing',b'from ....missing import x'):
            files=dict(original);files[member]+=b'\n'+line+b'\n'
            with self.subTest(line=line),self.assertRaisesRegex(ValueError,'dependency missing'):archive_bytes(files)
        files=dict(original);files['colvia/platforms/__init__.py']+=b'\nconstant = 1\n'
        files[member]+=b'\nfrom . import constant\nfrom colvia import codec\n'
        self.assertTrue(archive_bytes(files))

    def test_symlink_runtime_is_refused_before_output(self):
        (self.runtime/'alias').symlink_to('python')
        with self.assertRaisesRegex(RecordError,'input-symlink'):bundle.assemble(**self.kw)
        self.assertFalse(self.kw['output'].exists())
    def test_verifier_cannot_replace_core_module(self):
        (self.verifier/'colvia').mkdir();(self.verifier/'colvia/codec.py').write_text('untrusted')
        with self.assertRaisesRegex(RecordError,'path-collision'):bundle.assemble(**self.kw)
    def test_required_guides_and_notices_cannot_be_omitted(self):
        self.kw['guides']={}
        with self.assertRaisesRegex(RecordError,'guides-required'):bundle.assemble(**self.kw)
    def test_output_is_reproducible_for_identical_inputs(self):
        first=bundle.assemble(**self.kw);self.kw['output']=self.root/'second.zip';second=bundle.assemble(**self.kw)
        self.assertEqual(first,second)

    def test_mac_candidate_patch_passes_builder_and_slot_together(self):
        self.kw.update(python_version='3.14.10',sqlite_version='3.53.1')
        result=bundle.assemble(**self.kw);self.stage_checked(result)
        self.assertFalse(result['runtime_execution_verified'])

    def test_candidate_patch_refused_on_windows_and_unknown_patch(self):
        for os_name,arch,version in (('windows','arm64','3.14.10'),('windows','x64','3.14.10'),('macos','arm64','3.14.11')):
            self.kw.update(os_name=os_name,architecture=arch,python_version=version)
            with self.assertRaisesRegex(RecordError,'bundle-python-version'):bundle.assemble(**self.kw)
            self.assertFalse(self.kw['output'].exists())

if __name__=='__main__':unittest.main()


class WorkerAssignmentBindingTests(unittest.TestCase):
    def test_subscript_target_is_not_a_package_export(self):
        from distribution.document_worker import archive_bytes,MEMBERS
        source=Path(__file__).resolve().parents[1]/'src'
        members={name:(source/name).read_bytes() for name in MEMBERS}
        members['colvia/__init__.py']=b"registry[name] = 1\n"
        members['colvia/codec.py']+=b"\nfrom colvia import name\n"
        with self.assertRaisesRegex(ValueError,'dependency'):archive_bytes(members)
