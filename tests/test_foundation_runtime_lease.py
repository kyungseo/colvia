import threading,unittest
from colvia.codec import RecordError
from colvia.storage.authority import Authority
from colvia.storage.sqlite import runtime_capabilities
from colvia.updates.lease import open_managed_store
import test_foundation_slots as slot_fixture
from test_foundation_binding import P,I

class RuntimeLeaseTests(unittest.TestCase):
    setUp=slot_fixture.SlotTests.setUp
    tearDown=slot_fixture.SlotTests.tearDown
    slot=slot_fixture.SlotTests.slot
    def managed(self):
        caps=tuple(c for c in runtime_capabilities() if c!='foundation-v1')
        self.third=self.slot('complete',3,extra=caps);self.fourth=self.slot('next',4,extra=caps)
        before,_=self.manager.selection();self.manager.activate(self.third,expected_selection=before,read_requirements=[])
        self.authority=Authority.create(self.base/'authority',project=P,instance=I,generation='initial')
        return open_managed_store(self.authority,self.manager)
    def test_old_process_cannot_read_or_write_after_runtime_switch(self):
        store=self.managed()
        try:
            store.begin_import('before','synthetic')
            raw,_=self.manager.selection();self.manager.activate(self.fourth,expected_selection=raw,read_requirements=runtime_capabilities())
            for action in (store.root,lambda:store.begin_import('after','synthetic')):
                with self.assertRaisesRegex(RecordError,'runtime-selection-changed'):action()
            fresh=open_managed_store(self.authority,self.manager)
            try:fresh.begin_import('new-runtime','synthetic');self.assertEqual(0,fresh.root().sequence)
            finally:fresh.close()
        finally:store.close()
    def test_runtime_switch_waits_for_short_inflight_transaction(self):
        store=self.managed();started=threading.Event();finished=threading.Event();errors=[]
        raw,_=self.manager.selection()
        def update():
            started.set()
            try:self.manager.activate(self.fourth,expected_selection=raw,read_requirements=runtime_capabilities())
            except BaseException as exc:errors.append(exc)
            finally:finished.set()
        try:
            with store._transaction(write=True):
                thread=threading.Thread(target=update);thread.start();self.assertTrue(started.wait(1))
                self.assertFalse(finished.wait(.08));self.assertEqual(raw,self.manager.selection()[0])
            self.assertTrue(finished.wait(3));thread.join();self.assertEqual([],errors)
            with self.assertRaisesRegex(RecordError,'runtime-selection-changed'):store.root()
        finally:store.close()
    def test_readonly_managed_store_uses_shared_lease_without_writing_authority(self):
        store=self.managed();store.close();raw,_=self.manager.selection()
        readonly=open_managed_store(self.authority,self.manager,readonly=True)
        try:
            self.assertEqual(0,readonly.root().sequence)
            with self.assertRaisesRegex(RecordError,'store-readonly'):readonly.begin_import('blocked','synthetic')
        finally:readonly.close()
        self.assertEqual(raw,self.manager.selection()[0])

    def test_nested_instances_keep_outer_shared_lease_until_run_ends(self):
        from colvia.updates.lease import RuntimeLease
        store=self.managed();outer=RuntimeLease(self.manager);other=RuntimeLease(self.manager)
        started=threading.Event();finished=threading.Event();errors=[];raw,_=self.manager.selection()
        def update():
            started.set()
            try:self.manager.activate(self.fourth,expected_selection=raw,read_requirements=runtime_capabilities())
            except BaseException as e:errors.append(e)
            finally:finished.set()
        try:
            with outer.hold():
                with outer.hold(),other.hold():
                    store.root()
                thread=threading.Thread(target=update);thread.start();self.assertTrue(started.wait(1))
                self.assertFalse(finished.wait(.08));outer.check();self.assertEqual(raw,self.manager.selection()[0])
            self.assertTrue(finished.wait(3));thread.join();self.assertEqual([],errors)
        finally:store.close()
