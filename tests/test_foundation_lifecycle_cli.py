"""Source entry only: no installed launcher, permissions, notifications or models."""
import unittest
from pathlib import Path
from test_foundation_cli import CLITests

class LifecycleCLITests(unittest.TestCase):
    setUp=CLITests.setUp
    tearDown=CLITests.tearDown
    call=CLITests.call
    def test_feature_selection_has_exact_confirmation_and_short_human_output(self):
        self.assertEqual([],self.call('configuration','show')['enabled'])
        preview=self.call('configuration','preview','--enable','official-execution')
        reply=self.call('configuration','apply','--enable','official-execution','--receipt',preview['receipt'],
                        '--statement','문서 실행 기능을 켜줘',machine=False)
        self.assertIn('문서 작업 실행',reply)
        self.assertNotIn('receipt',reply);self.assertNotIn('sha256',reply)
        self.assertEqual(['official-execution'],self.call('configuration','show')['enabled'])
    def test_logical_backup_preserves_source_and_reports_local_receipt(self):
        destination=self.home/'backup.colvia';scratch=self.home/'backup-scratch';scratch.mkdir()
        first=self.call('backup','status');self.assertFalse(first['verified_export_recorded'])
        result=self.call('backup','export','--destination',str(destination),'--scratch',str(scratch))
        self.assertTrue(result['published']);self.assertTrue(destination.is_file())
        status=self.call('backup','status');self.assertTrue(status['verified_export_recorded']);self.assertFalse(status['different_root'])
        refused=self.call('backup','export','--destination',str(destination),'--scratch',str(scratch),code=2)
        self.assertEqual('backup-destination-exists',refused['error'])
