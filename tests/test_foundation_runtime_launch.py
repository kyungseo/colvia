"""Pinned plan inspection in synthetic directories: no account or process use."""
import hashlib,os,shutil,tempfile,unittest
from pathlib import Path
from types import SimpleNamespace
from dataclasses import replace
from unittest.mock import patch
from colvia.codec import RecordError
from colvia.platforms.darwin_runtime_launch import DarwinRuntimeLaunch,PINNED,FORBIDDEN_ENV
from colvia.platforms.darwin_runtime_policy import POLICY_SHA256
from colvia.platforms.runtime_inventory import inventory
from colvia.adapters.codex_documents import Policy
from test_foundation_execution_history import grant

class RuntimeLaunchTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(prefix='runtime-launch-');self.root=Path(self.tmp.name)
        self.home=self.root/'home';codex=self.home/'.codex';codex.mkdir(parents=True);rules=codex/'rules';rules.mkdir()
        runtime=self.root/'runtime';runtime.mkdir(mode=0o700);session=runtime/'session';session.mkdir(mode=0o700)
        for name in ('cwd','tmp','log','sqlite'):(session/name).mkdir(mode=0o700)
        binary=self.root/'bin';binary.mkdir();py=self.root/'python';py.mkdir();self.project=self.root/'project';self.project.mkdir();self.authority=self.root/'authority';self.authority.mkdir()
        self.bindings=dict(BIN=str(binary/'codex'),PYROOT=str(py),RUNTIME=str(runtime),SESSION=str(session),
            CODEX_CONFIG=str(codex/'config.toml'),CODEX_AUTH=str(codex/'auth.json'),INSTALLATION_ID=str(codex/'installation_id'),
            CODEX_RULES_DIR=str(rules),CODEX_RULES_FILE=str(rules/'default.rules'),GLOBAL_INSTRUCTIONS=str(codex/'AGENTS.md'),CODE_MODE_HOST=str(binary/'codex-code-mode-host'))
        contents={'BIN':b'inert binary','CODE_MODE_HOST':b'inert helper','CODEX_CONFIG':b'[mcp_servers.fixture]\nenabled = true\n','CODEX_AUTH':b'not a credential','INSTALLATION_ID':b'inert id','CODEX_RULES_FILE':b'','GLOBAL_INSTRUCTIONS':b'fixture'}
        for key,raw in contents.items():Path(self.bindings[key]).write_bytes(raw)
        for key in ('BIN','CODE_MODE_HOST'):Path(self.bindings[key]).chmod(0o700)
        self.digests={key:hashlib.sha256(Path(self.bindings[key]).read_bytes()).hexdigest() for key in PINNED}
        self.profile=self.root/'runtime.sb';shutil.copyfile(Path(__file__).resolve().parents[1]/'runtime/official/official-codex-macos.sb',self.profile)
        self.environment=patch.dict(os.environ,{},clear=True);self.environment.start()
        self.inventories={key:inventory(Path(self.bindings[key]),content=True)[0] for key in ('PYROOT','CODEX_RULES_DIR')}
        self.port=self.create();self.policy=Policy(model='synthetic-model',runtime_digest=self.digests['BIN'],policy_digest=POLICY_SHA256,runtime_binding_digest=self.port.identity())
        value=grant(str(self.project));value['scope']['resources']['runtime_digest']=self.digests['BIN'];value['capability'].update(identity=self.policy.identity,policy_digest=POLICY_SHA256)
        self.grant=SimpleNamespace(payload={'contract':value})
    def tearDown(self):self.environment.stop();self.tmp.cleanup()
    def create(self):return DarwinRuntimeLaunch(bindings=self.bindings,digests=self.digests,policy_path=self.profile,authority_root=self.authority,home=self.home,qualified={key:self.digests[key] for key in ('BIN','CODE_MODE_HOST')},inventories=self.inventories)
    def test_fixed_argv_and_minimal_environment_without_process_or_credential_reads(self):
        import colvia.platforms.darwin_runtime_launch as module
        digest=module.resource_digest;read=module.resource_bytes;seen=[]
        def observe(path,*args,**kwargs):seen.append(str(path));return digest(path,*args,**kwargs)
        with patch.object(module,'resource_digest',side_effect=observe),patch('subprocess.Popen',side_effect=AssertionError('no spawn')):
            plan=self.port.prepare(self.grant,self.policy);self.port.verify(plan,self.grant,self.policy)
        self.assertEqual('/usr/bin/sandbox-exec',plan.argv[0]);self.assertEqual(('app-server','--strict-config','--listen','stdio://'),plan.argv[-4:])
        self.assertIn('mcp_servers.fixture.enabled=false',plan.argv);self.assertNotIn(self.bindings['CODEX_AUTH'],seen);self.assertNotIn(self.bindings['INSTALLATION_ID'],seen)
        self.assertEqual({'HOME','LANG','PATH','TMPDIR','RUST_LOG'},set(plan.env));self.assertEqual(self.home,Path(plan.env['HOME']))
    def test_no_path_search_or_new_directories(self):
        before={str(p) for p in self.root.rglob('*')}
        with patch('shutil.which',side_effect=AssertionError('no PATH lookup')):self.port.prepare(self.grant,self.policy)
        self.assertEqual(before,{str(p) for p in self.root.rglob('*')})
    def test_changed_binary_helper_config_rules_and_instructions_refuse(self):
        for key in PINNED:
            path=Path(self.bindings[key]);raw=path.read_bytes();path.write_bytes(raw+b'changed')
            try:
                with self.subTest(key=key),self.assertRaisesRegex(RecordError,'input-drift'):self.port.prepare(self.grant,self.policy)
            finally:path.write_bytes(raw)
    def test_changed_profile_or_tampered_argv_refuses(self):
        plan=self.port.prepare(self.grant,self.policy)
        with self.assertRaisesRegex(RecordError,'plan-changed'):self.port.verify(replace(plan,argv=('unapproved',)),self.grant,self.policy)
        self.profile.write_bytes(self.profile.read_bytes()+b'\n')
        with self.assertRaisesRegex(RecordError,'policy-drift'):self.port.prepare(self.grant,self.policy)
    def test_project_or_authority_overlap_refuses(self):
        original=self.port.authority_root
        self.port.authority_root=self.bindings['SESSION']
        # Even recomputing a future capability cannot authorize protected overlap.
        policy=Policy(model='synthetic-model',runtime_digest=self.digests['BIN'],policy_digest=POLICY_SHA256,runtime_binding_digest=self.port.identity())
        self.grant.payload['contract']['capability']['identity']=policy.identity
        with self.assertRaisesRegex(RecordError,'protected-overlap'):self.port.prepare(self.grant,policy)
        self.port.authority_root=original
    def test_symlink_or_hardlinked_mutable_auth_refuses_without_reading(self):
        auth=Path(self.bindings['CODEX_AUTH']);other=self.root/'other-auth';auth.rename(other);auth.symlink_to(other)
        with self.assertRaises(RecordError):self.port.prepare(self.grant,self.policy)
        auth.unlink();auth.hardlink_to(other)
        with self.assertRaisesRegex(RecordError,'file-alias'):self.port.prepare(self.grant,self.policy)
    def test_mutable_subscription_bytes_do_not_change_capability(self):
        identity=self.port.identity();Path(self.bindings['CODEX_AUTH']).write_bytes(b'another inert fixture')
        self.assertEqual(identity,self.port.identity());self.port.prepare(self.grant,self.policy)
    def test_api_proxy_and_custom_home_environment_refuse(self):
        for key in FORBIDDEN_ENV:
            with self.subTest(key=key),patch.dict(os.environ,{key:'synthetic'}),self.assertRaisesRegex(RecordError,'environment-override'):self.port.prepare(self.grant,self.policy)
    def test_unbound_or_changed_capability_cannot_prepare(self):
        policy=Policy(model='synthetic-model',runtime_digest=self.digests['BIN'],policy_digest=POLICY_SHA256)
        self.grant.payload['contract']['capability']['identity']=policy.identity
        with self.assertRaisesRegex(RecordError,'binding-mismatch'):self.port.prepare(self.grant,policy)
    def test_missing_or_nonprivate_session_refuses(self):
        directory=Path(self.bindings['SESSION'])/'cwd';directory.chmod(0o755)
        with self.assertRaisesRegex(RecordError,'session-private'):self.port.prepare(self.grant,self.policy)
    def test_unqualified_binary_digests_refuse_at_construction(self):
        with self.assertRaisesRegex(RecordError,'unqualified-binary'):
            DarwinRuntimeLaunch(bindings=self.bindings,digests=self.digests,policy_path=self.profile,authority_root=self.authority,home=self.home,qualified={'BIN':'a'*64,'CODE_MODE_HOST':'b'*64},inventories=self.inventories)

    def test_instruction_pin_must_be_actual_home_file_and_no_override(self):
        other=self.root/'unrelated-instructions.md';other.write_bytes(b'fixture')
        self.bindings['GLOBAL_INSTRUCTIONS']=str(other)
        with self.assertRaisesRegex(RecordError,'instruction-home'):self.create().identity()
        self.bindings['GLOBAL_INSTRUCTIONS']=str(self.home/'.codex/AGENTS.md')
        (self.home/'.codex/AGENTS.override.md').write_bytes(b'other instructions')
        with self.assertRaisesRegex(RecordError,'instruction-override'):self.create().identity()

    def test_unknown_config_profile_and_instruction_fallback_refuse_even_when_pinned(self):
        path=Path(self.bindings['CODEX_CONFIG']);original=path.read_bytes()
        for raw in (b'profile="other"',b'notify=["synthetic"]',b'project_doc_fallback_filenames=["note.md"]',b'[profiles.other]\nmodel="synthetic"'):
            with self.subTest(raw=raw):
                path.write_bytes(raw);self.digests['CODEX_CONFIG']=hashlib.sha256(raw).hexdigest()
                with self.assertRaisesRegex(RecordError,'config-unsupported'):self.create().identity()
        path.write_bytes(original)
    def test_initial_session_must_be_empty_but_owned_logs_may_grow(self):
        log=Path(self.bindings['SESSION'])/'log'/'log.txt';log.write_text('unexpected')
        with self.assertRaisesRegex(RecordError,'session-not-empty'):self.port.prepare(self.grant,self.policy)
        log.unlink();plan=self.port.prepare(self.grant,self.policy);log.write_text('synthetic runtime log')
        self.port.verify(plan,self.grant,self.policy)
    def test_replaced_session_directory_and_ancestor_instruction_refuse(self):
        plan=self.port.prepare(self.grant,self.policy);cwd=Path(plan.cwd);cwd.rename(cwd.with_name('old-cwd'));cwd.mkdir(mode=0o700)
        with self.assertRaisesRegex(RecordError,'session-replaced'):self.port.verify(plan,self.grant,self.policy)
        cwd.rmdir();cwd.with_name('old-cwd').rename(cwd)
        (cwd.parent/'AGENTS.override.md').write_text('unexpected')
        with self.assertRaisesRegex(RecordError,'ancestor-instructions'):self.port.verify(plan,self.grant,self.policy)
    def test_unlisted_tree_file_refuses_and_hot_verification_does_not_rehash_binary(self):
        plan=self.port.prepare(self.grant,self.policy)
        with patch('colvia.platforms.darwin_runtime_launch.resource_digest',side_effect=AssertionError('hot binary hash')):
            self.port.verify(plan,self.grant,self.policy)
        path=Path(self.bindings['PYROOT'])/'unlisted.py';path.write_text('unexpected')
        with self.assertRaisesRegex(RecordError,'inventory-drift'):self.port.verify(plan,self.grant,self.policy)
        with self.assertRaisesRegex(RecordError,'inventory-drift'):self.port.prepare(self.grant,self.policy)
    def test_tree_symlink_hardlink_and_depth_are_rejected(self):
        root=Path(self.bindings['PYROOT']);file=root/'alias';file.symlink_to(self.bindings['BIN'])
        with self.assertRaisesRegex(RecordError,'tree-kind'):inventory(root,content=True)
        file.unlink();file.hardlink_to(self.bindings['BIN'])
        with self.assertRaisesRegex(RecordError,'tree-kind'):inventory(root,content=True)
        file.unlink()
        for i in range(33):root=root/'d';root.mkdir()
        with self.assertRaisesRegex(RecordError,'tree-depth'):inventory(Path(self.bindings['PYROOT']),content=True)

    def test_runtime_root_requires_private_mode(self):
        Path(self.bindings['RUNTIME']).chmod(0o755)
        with self.assertRaisesRegex(RecordError,'root-private'):self.port.prepare(self.grant,self.policy)
    def test_symlinked_session_child_is_not_canonical(self):
        target=self.root/'elsewhere';target.mkdir(mode=0o700)
        child=Path(self.bindings['SESSION'])/'log';child.rmdir();child.symlink_to(target,target_is_directory=True)
        with self.assertRaises(RecordError):self.port.prepare(self.grant,self.policy)
    def test_used_session_in_new_port_and_extra_runtime_entry_refuse(self):
        self.port.prepare(self.grant,self.policy)
        (Path(self.bindings['SESSION'])/'log'/'trace').write_text('synthetic transient')
        with self.assertRaisesRegex(RecordError,'not-empty'):self.create().prepare(self.grant,self.policy)
        (Path(self.bindings['RUNTIME'])/'extra').mkdir()
        with self.assertRaisesRegex(RecordError,'session-isolation'):self.port.prepare(self.grant,self.policy)
