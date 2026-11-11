"""Resolution services and native read-only observations; no model invocation."""
from contextlib import contextmanager
import copy,os,sys,unittest
from unittest.mock import patch
from colvia.codec import RecordError
from colvia.effects import PENDING
from colvia.execution.resolution import Resolution
from test_foundation_execution_store import JournalFixture
from test_foundation_execution_history import BIRTH

class Observer:
    """Explicit test double; its results never qualify the native observer."""
    def __init__(self,contract):
        self.documents={v['path']:copy.deepcopy(v['original_identity']) for v in contract['scope']['documents'].values()}
        self.locked=False;self.absent=True;self.availability='missing';self.calls=0
    @contextmanager
    def hold(self):
        if self.locked:raise RecordError('lock-reentry')
        self.locked=True
        try:yield
        finally:self.locked=False
    def assert_held(self,grant,owner):
        if not self.locked:raise RecordError('effect-lock-required')
    def process_absent(self,pid,birth,*,group):self.calls+=1;return self.absent
    def document(self,path):return copy.deepcopy(self.documents[path])
    def recovery(self,grant,history):return self.availability

class ResolutionTests(JournalFixture,unittest.TestCase):
    def make(self):
        self.launch();self.observer=Observer(self.contract);self.resolution=Resolution(self.journal,self.observer)
    def test_exact_observation_resolves_without_accepting_or_restoring(self):
        self.make();before=(self.root/'output.md').read_bytes();preview=self.resolution.preview('run')
        result=self.resolution.apply(operation='resolve',run='run',receipt=preview['receipt'],statement='Record this unresolved result')
        self.assertEqual('operator-resolved-unknown',result['status']);self.assertFalse(result['accepted'])
        self.assertIsNone(self.store.head(PENDING));self.assertEqual(before,(self.root/'output.md').read_bytes())
        self.assertEqual('active',self.service._head('synthetic-work')[1].payload['phase'])
    def test_changed_document_or_recovery_requires_new_confirmation(self):
        self.make();preview=self.resolution.preview('run');self.observer.availability='present'
        with self.assertRaisesRegex(RecordError,'stale-resolution-receipt'):
            self.resolution.apply(operation='resolve',run='run',receipt=preview['receipt'],statement='yes')
        self.observer.availability='missing';self.observer.documents[str(self.root/'output.md')]['sha256']='0'*64
        with self.assertRaisesRegex(RecordError,'stale-resolution-receipt'):
            self.resolution.apply(operation='resolve-doc',run='run',receipt=preview['receipt'],statement='yes')
        self.assertIsNotNone(self.store.head(PENDING))
    def test_missing_runtime_identity_cannot_be_declared_absent(self):
        self.make();self.journal.append(operation='intent',run='run',kind='runtime-reserved',value=dict(ordinal=1,host_pid=9000,host_birth=BIRTH))
        with self.assertRaisesRegex(RecordError,'runtime-identity-unavailable'):self.resolution.preview('run')
        self.assertEqual(0,self.observer.calls);self.assertIsNotNone(self.store.head(PENDING))
    def test_present_process_refuses_even_with_valid_identity(self):
        self.make();self.journal.append(operation='intent',run='run',kind='runtime-reserved',value=dict(ordinal=1,host_pid=9000,host_birth=BIRTH))
        self.journal.append(operation='started',run='run',kind='runtime-started',value=dict(ordinal=1,pid=9001,birth=BIRTH))
        self.observer.absent=False
        with self.assertRaisesRegex(RecordError,'process-present-or-unconfirmed'):self.resolution.preview('run')
        self.assertIsNotNone(self.store.head(PENDING))
    def test_change_during_publication_reobservation_refuses(self):
        self.make();preview=self.resolution.preview('run');observe=self.resolution.observation;calls=0
        def racing(run):
            nonlocal calls
            calls+=1
            if calls==2:self.observer.documents[str(self.root/'output.md')]=None
            return observe(run)
        with patch.object(self.resolution,'observation',side_effect=racing),self.assertRaisesRegex(RecordError,'observation-changed'):
            self.resolution.apply(operation='resolve-race',run='run',receipt=preview['receipt'],statement='yes')
        self.assertEqual('incomplete',self.journal.status('run')['status']);self.assertIsNotNone(self.store.head(PENDING))

@unittest.skipUnless(sys.platform=='darwin','qualified Darwin observer')
class NativeResolutionTests(JournalFixture,unittest.TestCase):
    def native(self):
        from colvia.platforms.darwin_effects import DarwinEffects
        from colvia.platforms.darwin_execution import DarwinExecutionObservation
        authority=self.root.parent/'effects';authority.mkdir(mode=0o700)
        effects=DarwinEffects(self.root,authority)
        with effects.exclusion():pass
        return DarwinExecutionObservation(self.journal,effects)
    def test_real_lock_and_document_observation_bind_confirmation(self):
        self.launch();observer=self.native();resolution=Resolution(self.journal,observer)
        preview=resolution.preview('run')
        self.assertEqual('not_checked',preview['observation']['recovery_availability'])
        self.assertEqual(os.stat(self.root/'output.md').st_ino,preview['observation']['documents']['Output']['ino'])
        (self.root/'output.md').write_bytes(b'changed')
        with self.assertRaisesRegex(RecordError,'stale-resolution-receipt'):
            resolution.apply(operation='stale',run='run',receipt=preview['receipt'],statement='yes')
        fresh=resolution.preview('run');resolution.apply(operation='fresh',run='run',receipt=fresh['receipt'],statement='Record unknown')
        self.assertEqual(b'changed',(self.root/'output.md').read_bytes())
    def test_live_pid_is_not_absent_and_symlink_document_refuses(self):
        from colvia.platforms.darwin_execution import process_birth
        self.launch();observer=self.native()
        self.assertFalse(observer.process_absent(os.getpid(),process_birth(os.getpid()),group=False))
        path=self.root/'output.md';path.unlink();path.symlink_to('reference.md')
        with self.assertRaisesRegex(RecordError,'document-kind-size'):Resolution(self.journal,observer).preview('run')
