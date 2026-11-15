"""Windows Git protocol composition on macOS with explicit native API doubles.

Real synthetic Git subprocesses use the already-tested Darwin child port. These
checks exercise common authority/ref/index sequencing, not Windows APIs or Jobs.
"""
import os,unittest
from pathlib import Path
from unittest.mock import patch
from colvia.codec import RecordError,canonical_bytes,decode_canonical
from colvia.effects import PENDING
from colvia.git_integration import GitIntegration
from colvia.platforms.windows_git import WindowsGit
from colvia.platforms.windows_observation import Observer
from colvia.platforms.git_child import GitChild
from test_foundation_git_integration import IntegrationFixture
from test_foundation_windows_effects import Files,Move
from test_foundation_windows_git_index import TunnelingMove

class ProtocolChild(GitChild):
    """Explicit test double: real Darwin subprocess, simulated Windows Job receipt."""
    def run(self,*args,event=lambda *_:None,**kwargs):
        area=None
        def observed(phase,value):
            nonlocal area
            if phase=='spawn-intent':area=Path(value)
            event(phase,value)
        result=super().run(*args,event=observed,**kwargs)
        exited=decode_canonical(self.files.read(area/'exited.json'))
        assert exited['group_absent']
        self.files.create(area/'closed.json',canonical_bytes(dict(pid=exited['pid'],exit_code=result.code,job_active=0)))
        return result

class GitParentFiles(Files):
    # Model the actual Windows storage primitive: it must not create files
    # directly in a Git-owned directory with inherited access rules.
    def __init__(self,gitdir):super().__init__();self.gitdir=gitdir
    def create(self,path,raw):
        if Path(path).is_relative_to(self.gitdir):raise RecordError('windows-private-dacl-not-protected')
        return super().create(path,raw)

class WindowsFixture(IntegrationFixture):
    def command(self,*args,**kwargs):
        args=list(args)
        if args and args[0]=='commit' and '-qm' in args:
            n=args.index('-qm')+1;args[n]+='\n\nCo-authored-by: Codex <noreply@openai.com>'
        return super().command(*args,**kwargs)
    def prepare(self):
        from test_foundation_git_candidate import AUTHOR
        self.accepted()
        return self.integration.prepare(operation='integrate',works=['report'],
            message='Synthetic accepted result\n\nCo-authored-by: Codex <noreply@openai.com>',identity=AUTHOR)

    def setUp(self):
        super().setUp();self.files=GitParentFiles(self.root/'.git');self.mover=TunnelingMove(self.files.api)
        self.port=WindowsGit(self.root,self.scratch,self.git,files=self.files,observer=Observer(files=self.files),
            mover=self.mover,children=ProtocolChild(self.scratch/'children'),birth=lambda pid:'synthetic-owner' if pid==os.getpid() else None)
        self.integration=GitIntegration(self.store,self.service.workspace,self.port)
class WindowsGitCompositionTests(WindowsFixture,unittest.TestCase):
    def test_gate_move_guard_never_reopens_delete_locked_source(self):
        preview=self.prepare();original=self.mover.move
        def sharing_checked(source,destination,**kw):
            if source.name=='index.lock' or source.name.startswith('index-lock-'):
                guard=kw['before_effect'];read=self.port.observer.read_file;identity=self.port.file_id
                def no_source_read(path,*a,**k):
                    if path==source:raise AssertionError('DELETE-held source reopened by guard')
                    return read(path,*a,**k)
                def no_source_identity(path):
                    if path==source:raise AssertionError('DELETE-held source reopened for identity')
                    return identity(path)
                def checked():
                    with patch.object(self.port.observer,'read_file',side_effect=no_source_read),patch.object(self.port,'file_id',side_effect=no_source_identity):guard()
                kw['before_effect']=checked
            return original(source,destination,**kw)
        with patch.object(self.mover,'move',side_effect=sharing_checked):
            self.assertEqual('completed',self.integration.apply('integrate',receipt=preview['receipt'],statement='기록')['state'])
    def test_exact_commit_preserves_unselected_staging_and_retained_original(self):
        (self.root/'other').write_bytes(b'keep staged');self.command('add','other');preview=self.prepare()
        original=(self.root/'.git/index').read_bytes()
        result=self.integration.apply('integrate',receipt=preview['receipt'],statement='이 변경만 기록')
        self.assertEqual('completed',result['state']);self.assertIsNone(self.store.head(PENDING))
        self.assertEqual(original,(self.scratch/'integrate/index-original').read_bytes())
        self.assertEqual(b'other\n',self.command('diff','--cached','--name-only'));self.assertFalse((self.root/'.git/index.lock').exists())
        self.assertTrue((self.scratch/'integrate/index-lock-completed').exists())
    def test_evacuated_index_resumes_only_exact_prepared_transition(self):
        preview=self.prepare();original=(self.root/'.git/index').read_bytes();move=self.mover.move;crashed=False
        def interrupted(*args,**kw):
            nonlocal crashed
            result=move(*args,**kw)
            if not crashed and Path(args[1]).name=='index-original':crashed=True;raise RuntimeError('synthetic crash after original move')
            return result
        with patch.object(self.mover,'move',side_effect=interrupted),self.assertRaises(RuntimeError):
            self.integration.apply('integrate',receipt=preview['receipt'],statement='기록')
        self.assertFalse((self.root/'.git/index').exists());self.assertTrue((self.root/'.git/index.lock').exists())
        self.assertEqual(original,(self.scratch/'integrate/index-original').read_bytes())
        self.assertIsNotNone(self.store.head(PENDING))
        self.assertEqual('completed',self.integration.recover('integrate',statement='중단 반영 완료')['state'])
        self.assertFalse((self.root/'.git/index.lock').exists());self.assertIsNone(self.store.head(PENDING))
    def test_completed_index_keeps_gate_until_recovery_finishes(self):
        preview=self.prepare()
        def interrupted(phase):
            if phase=='index-replaced':raise RuntimeError('synthetic crash before gate close')
        with self.assertRaises(RuntimeError):self.integration.apply('integrate',receipt=preview['receipt'],statement='기록',event=interrupted)
        self.assertTrue((self.root/'.git/index.lock').exists());head=self.command('rev-parse','HEAD')
        self.assertEqual('completed',self.integration.recover('integrate',statement='완료 확인')['state'])
        self.assertEqual(head,self.command('rev-parse','HEAD'));self.assertFalse((self.root/'.git/index.lock').exists())
    def test_gate_moved_before_completion_ack_can_finish_without_new_effect(self):
        preview=self.prepare();finalize=self.port.finalize_index
        def interrupted(*args,**kw):finalize(*args,**kw);raise RuntimeError('synthetic lost completion')
        with patch.object(self.port,'finalize_index',side_effect=interrupted),self.assertRaises(RuntimeError):
            self.integration.apply('integrate',receipt=preview['receipt'],statement='기록')
        self.assertFalse((self.root/'.git/index.lock').exists());count=self.mover.count
        self.assertEqual('completed',self.integration.recover('integrate',statement='반영 완료 확인')['state'])
        self.assertEqual(count,self.mover.count)

    def test_nonexecutable_hook_is_not_assumed_inactive_on_windows(self):
        self.accepted();hook=self.root/'.git/hooks/pre-commit';hook.write_text('synthetic hook never executed');hook.chmod(0o600)
        from test_foundation_git_candidate import AUTHOR
        with self.assertRaisesRegex(RecordError,'hooks-require-manual'):
            self.integration.prepare(operation='integrate',works=['report'],message='synthetic',identity=AUTHOR)
        self.assertIsNone(self.store.head(PENDING));self.assertFalse((self.root/'.git/index.lock').exists())

    def test_recovery_recreates_missing_gate_without_private_git_parent(self):
        preview=self.prepare()
        def crash(phase):
            if phase=='ref-observed':raise RuntimeError('after ref')
        with self.assertRaisesRegex(RuntimeError,'after ref'):
            self.integration.apply('integrate',receipt=preview['receipt'],statement='synthetic',event=crash)
        gate=self.root/'.git/index.lock'
        self.mover.names[gate]=self.files.api.state(gate,gate)['identity'][2]
        gate.rename(self.home/'removed-gate')
        self.assertEqual('completed',self.integration.recover('integrate',statement='resume')['state'])
        self.assertFalse(gate.exists());self.assertIsNone(self.store.head(PENDING))

    def test_competing_gate_is_preserved_before_native_move(self):
        preview=self.prepare();move=self.mover.move;head=self.command('rev-parse','HEAD')
        def compete(source,target,**kw):
            if Path(target).name=='index.lock':Path(target).write_bytes(b'foreign')
            return move(source,target,**kw)
        with patch.object(self.mover,'move',side_effect=compete),self.assertRaisesRegex(RecordError,'lock-present'):
            self.integration.apply('integrate',receipt=preview['receipt'],statement='synthetic')
        self.assertEqual(b'foreign',(self.root/'.git/index.lock').read_bytes())
        self.assertEqual(head,self.command('rev-parse','HEAD'));self.assertEqual(0,self.mover.count)

    def test_unrecorded_gate_after_move_is_never_adopted_by_recovery(self):
        preview=self.prepare();move=self.mover.move;head=self.command('rev-parse','HEAD')
        def crash(source,target,**kw):
            result=move(source,target,**kw)
            if Path(target).name=='index.lock':raise RuntimeError('after gate move')
            return result
        with patch.object(self.mover,'move',side_effect=crash),self.assertRaisesRegex(RuntimeError,'after gate'):
            self.integration.apply('integrate',receipt=preview['receipt'],statement='synthetic')
        gate=self.root/'.git/index.lock';identity=self.port.file_id(gate)
        for intent in (self.scratch/'integrate').glob('gate-intent-*.json'):intent.unlink()
        with self.assertRaisesRegex(RecordError,'lock-unrecorded'):self.integration.recover('integrate',statement='resume')
        self.assertEqual(identity,self.port.file_id(gate));self.assertEqual(head,self.command('rev-parse','HEAD'))

    def test_sharing_refusal_preserves_ref_index_and_staged_gate(self):
        preview=self.prepare();head=self.command('rev-parse','HEAD');index=(self.root/'.git/index').read_bytes()
        with patch.object(self.mover,'move',side_effect=PermissionError('synthetic sharing refusal')),self.assertRaises(PermissionError):
            self.integration.apply('integrate',receipt=preview['receipt'],statement='synthetic')
        self.assertEqual(head,self.command('rev-parse','HEAD'));self.assertEqual(index,(self.root/'.git/index').read_bytes())
        self.assertFalse((self.root/'.git/index.lock').exists())
        self.assertEqual(1,len(list((self.scratch/'integrate').glob('index-lock-*'))))


    def test_foreign_name_cache_on_our_recreated_gate_is_not_a_foreign_file(self):
        preview=self.prepare()
        def crash(phase):
            if phase=='ref-observed':raise RuntimeError('after ref')
        with self.assertRaises(RuntimeError):
            self.integration.apply('integrate',receipt=preview['receipt'],statement='synthetic',event=crash)
        gate=self.root/'.git/index.lock';previous=self.files.api.state(gate,gate)['identity']
        gate.rename(self.home/'removed-gate')
        self.mover.names[gate]=previous[2]+17
        self.assertEqual('completed',self.integration.recover('integrate',statement='resume')['state'])
        self.assertFalse(gate.exists());self.assertIsNone(self.store.head(PENDING))

    def test_invalid_attempt_refuses_before_creating_staged_gate(self):
        self.prepare();m=decode_canonical((self.scratch/'integrate/manifest').read_bytes())
        area=self.scratch/'integrate';before=set(area.iterdir())
        for attempt in (None,{},dict(head={},sequence=1)):
            with self.subTest(attempt=attempt),self.assertRaises(RecordError):
                self.port.create_index_gate(m,attempt=attempt,live=lambda:None)
            self.assertEqual(before,set(area.iterdir()));self.assertFalse((self.root/'.git/index.lock').exists())

    def test_tunneled_index_lost_ack_recovers_without_republishing(self):
        preview=self.prepare();move=self.mover.move
        def lost(source,target,**kw):
            result=move(source,target,**kw)
            if Path(source).name=='index-prepared':raise RuntimeError('lost index ack')
            return result
        with patch.object(self.mover,'move',side_effect=lost),self.assertRaisesRegex(RuntimeError,'lost index ack'):
            self.integration.apply('integrate',receipt=preview['receipt'],statement='synthetic')
        count=self.mover.count
        self.assertEqual('completed',self.integration.recover('integrate',statement='resume')['state'])
        self.assertEqual(count+1,self.mover.count) # Only the already-owned gate is retained.
        self.assertIsNone(self.store.head(PENDING))



class GateIntentTests(WindowsFixture,unittest.TestCase):
    def crash_gate(self,preview):
        move=self.mover.move
        def lost(source,target,**kw):
            result=move(source,target,**kw)
            if Path(target).name=='index.lock':raise RuntimeError('gate ack lost')
            return result
        with patch.object(self.mover,'move',side_effect=lost),self.assertRaisesRegex(RuntimeError,'gate ack lost'):
            self.integration.apply('integrate',receipt=preview['receipt'],statement='synthetic')
    def test_initial_foreign_name_cache_keeps_our_identity_and_completes(self):
        preview=self.prepare();gate=self.root/'.git/index.lock'
        self.mover.names[gate]=123456789
        self.assertEqual('completed',self.integration.apply('integrate',receipt=preview['receipt'],statement='synthetic')['state'])
        self.assertFalse(gate.exists())
    def test_before_ref_lost_ack_releases_only_our_gate(self):
        preview=self.prepare();head=self.command('rev-parse','HEAD');index=(self.root/'.git/index').read_bytes()
        self.crash_gate(preview)
        self.assertEqual('not-applied',self.integration.recover('integrate',statement='recover')['state'])
        self.assertEqual(head,self.command('rev-parse','HEAD'));self.assertEqual(index,(self.root/'.git/index').read_bytes())
        self.assertFalse((self.root/'.git/index.lock').exists());self.assertIsNone(self.store.head(PENDING))
    def test_reacquire_lost_ack_uses_current_attempt_then_finishes(self):
        preview=self.prepare()
        def stop(phase):
            if phase=='ref-observed':raise RuntimeError('ref stop')
        with self.assertRaises(RuntimeError):
            self.integration.apply('integrate',receipt=preview['receipt'],statement='synthetic',event=stop)
        gate=self.root/'.git/index.lock';gate.rename(self.home/'retired-gate');self.mover.names[gate]=987654321
        move=self.mover.move
        def lost(source,target,**kw):
            result=move(source,target,**kw)
            if Path(target).name=='index.lock':raise RuntimeError('relock ack lost')
            return result
        with patch.object(self.mover,'move',side_effect=lost),self.assertRaisesRegex(RuntimeError,'relock ack lost'):
            self.integration.recover('integrate',statement='first recover')
        self.assertEqual(2,len(list((self.scratch/'integrate').glob('gate-intent-*.json'))))
        self.assertEqual('completed',self.integration.recover('integrate',statement='recover acknowledged intent')['state'])
        self.assertFalse(gate.exists());self.assertIsNone(self.store.head(PENDING))
    def test_interrupted_relock_intent_write_preserves_temporary_file(self):
        preview = self.prepare()
        def stop_after_ref(phase):
            if phase == 'ref-observed':
                raise RuntimeError('synthetic ref stop')

        with self.assertRaisesRegex(RuntimeError, 'synthetic ref stop'):
            self.integration.apply('integrate', receipt=preview['receipt'],
                                   statement='synthetic', event=stop_after_ref)
        gate = self.root / '.git/index.lock'
        gate.rename(self.home / 'retired-gate')
        create = self.files.create
        incomplete = b'{"version":'
        abandoned = []
        def stop_during_intent_write(path, raw, *args, **kwargs):
            if path.name.startswith('gate-intent-'):
                temporary = path.with_name(path.name + '.prepared-' + 'a' * 32)
                create(temporary, incomplete)
                abandoned.append(temporary)
                raise RuntimeError('synthetic temporary write stop')
            return create(path, raw, *args, **kwargs)

        with patch.object(self.files, 'create', side_effect=stop_during_intent_write):
            with self.assertRaisesRegex(RuntimeError, 'synthetic temporary write stop'):
                self.integration.recover('integrate', statement='relock')
        temporary, = abandoned
        self.assertFalse(gate.exists())
        self.assertIsNotNone(self.store.head(PENDING))
        result = self.integration.recover('integrate', statement='finish relock')
        self.assertEqual('completed', result['state'])
        self.assertEqual(incomplete, temporary.read_bytes())
        self.assertFalse(gate.exists())
        self.assertIsNone(self.store.head(PENDING))

    def test_changed_gate_bytes_are_preserved(self):
        preview=self.prepare();self.crash_gate(preview);gate=self.root/'.git/index.lock'
        gate.write_bytes(b'foreign');identity=self.port.file_id(gate)
        with self.assertRaisesRegex(RecordError,'foreign-lock'):self.integration.recover('integrate',statement='recover')
        self.assertEqual(b'foreign',gate.read_bytes());self.assertEqual(identity,self.port.file_id(gate))
    def test_replaced_empty_gate_is_not_adopted(self):
        preview=self.prepare();self.crash_gate(preview);gate=self.root/'.git/index.lock'
        gate.rename(self.home/'saved-own-gate');gate.write_bytes(b'')
        with self.assertRaisesRegex(RecordError,'foreign-lock'):self.integration.recover('integrate',statement='recover')
        self.assertTrue(gate.exists())
    def test_intent_bound_to_superseded_state_cannot_authorize(self):
        preview=self.prepare();self.crash_gate(preview)
        intent=next((self.scratch/'integrate').glob('gate-intent-*.json'));value=decode_canonical(intent.read_bytes())
        value['attempt']['head']['sha256']='0'*64;intent.write_bytes(canonical_bytes(value))
        with self.assertRaisesRegex(RecordError,'lock-unrecorded'):self.integration.recover('integrate',statement='recover')
        self.assertTrue((self.root/'.git/index.lock').exists())
    def test_malformed_or_changed_root_intent_is_not_used(self):
        preview=self.prepare();self.crash_gate(preview)
        intent=next((self.scratch/'integrate').glob('gate-intent-*.json'));value=decode_canonical(intent.read_bytes())
        value['roots'][0][0]+=1;intent.write_bytes(canonical_bytes(value))
        with self.assertRaisesRegex(RecordError,'intent-invalid'):self.integration.recover('integrate',statement='recover')
        self.assertTrue((self.root/'.git/index.lock').exists())
    def test_intent_write_failure_precedes_git_effect(self):
        preview=self.prepare();create=self.files.create;head=self.command('rev-parse','HEAD')
        def refuse(path,raw,*a,**kw):
            if Path(path).name.startswith('gate-intent-'):raise OSError('synthetic flush failure')
            return create(path,raw,*a,**kw)
        with patch.object(self.files,'create',side_effect=refuse),self.assertRaisesRegex(OSError,'flush failure'):
            self.integration.apply('integrate',receipt=preview['receipt'],statement='synthetic')
        self.assertFalse((self.root/'.git/index.lock').exists());self.assertEqual(head,self.command('rev-parse','HEAD'))
    def test_still_running_intent_owner_is_not_adopted(self):
        preview=self.prepare();self.crash_gate(preview)
        intent=next((self.scratch/'integrate').glob('gate-intent-*.json'));value=decode_canonical(intent.read_bytes())
        value['owner']['pid']=os.getpid()+1;intent.write_bytes(canonical_bytes(value))
        with patch.object(self.port,'birth',return_value=value['owner']['birth']),self.assertRaisesRegex(RecordError,'still-live'):
            self.integration.recover('integrate',statement='recover')
        self.assertTrue((self.root/'.git/index.lock').exists())

if __name__=='__main__':unittest.main()
