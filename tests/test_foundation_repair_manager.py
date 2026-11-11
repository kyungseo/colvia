import unittest
from unittest.mock import patch
from colvia.codec import RecordError
from colvia.updates.repair import RecoveryManager
from colvia.configuration import Configuration
import test_foundation_management as fixture

class RepairManagerTests(unittest.TestCase):
    slot=fixture.ManagementTests.slot
    setUp=fixture.ManagementTests.setUp
    tearDown=fixture.ManagementTests.tearDown
    def recovery(self):
        self.home.update(operation='initial-update',target=self.two,expected_selection=self.manager.selection()[0])
        self.broken=self.manager.root/'slots/two/product.py';self.broken.write_bytes(b'broken selected runtime')
        with patch('colvia.updates.repair.process_runtime',return_value=(str(self.manager.root/'slots/one/python'),'3.14.7','3.54.0')):
            return RecoveryManager(self.home.root,pointer=self.one)
    def test_explicit_recovery_preserves_new_data_and_broken_slot(self):
        service=self.recovery();preview=service.preview();result=service.apply(operation='repair',receipt=preview['receipt'])
        self.assertTrue(result['records_preserved']);self.assertEqual(self.one,self.manager.selection()[1]['selected'])
        self.assertEqual(2,self.manager.selection()[1]['high_sequence']);self.assertIsNone(self.manager.selection()[1]['recovery'])
        self.assertEqual(b'broken selected runtime',self.broken.read_bytes())
        store=self.home.store(self.authority.project)
        try:self.assertEqual(self.root,store.root().ref)
        finally:store.close()
    def test_review_does_not_reuse_old_decision_after_new_record(self):
        service=self.recovery();preview=service.preview();store=self.authority.store()
        try:
            config=Configuration(store);p=config.preview([]);config.apply(operation='new-decision',features=[],receipt=p['receipt'],statement='변경')
        finally:store.close()
        with self.assertRaisesRegex(RecordError,'review-changed'):service.apply(operation='repair',receipt=preview['receipt'])
        self.assertEqual(self.two,self.manager.selection()[1]['selected'])
    def test_current_process_cannot_claim_recovery_python(self):
        self.recovery()
        with self.assertRaisesRegex(RecordError,'dedicated-runtime-mismatch'):RecoveryManager(self.home.root,pointer=self.one)
    def test_other_slot_is_not_authorized_recovery(self):
        self.recovery()
        with self.assertRaisesRegex(RecordError,'target-mismatch'):RecoveryManager(self.home.root,pointer=self.two)

if __name__=='__main__':unittest.main()
