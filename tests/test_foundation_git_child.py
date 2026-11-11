import tempfile,unittest,json
from pathlib import Path
from unittest.mock import patch
from colvia.codec import canonical_bytes,RecordError
from colvia.platforms.git_child import GitChild

class ClosureTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(prefix='git-child-closure-');self.root=Path(self.tmp.name)
        self.child=GitChild(self.root);self.area=self.root/'synthetic';self.area.mkdir(mode=0o700)
    def tearDown(self):self.tmp.cleanup()
    def started(self):
        (self.area/'started.json').write_bytes(canonical_bytes(dict(pid=123456789,birth=None)))
    def test_fractional_budget_is_canonical_before_any_spawn(self):
        with patch('colvia.platforms.git_child.subprocess.Popen',side_effect=RuntimeError('synthetic before spawn')):
            with self.assertRaisesRegex(RuntimeError,'before spawn'):
                self.child.run(['/synthetic/unexecuted'],cwd=self.root,env={},seconds=0.5)
        intent=next(self.root.glob('*/intent.json'))
        self.assertEqual(500000000,json.loads(intent.read_text())['seconds_limit_ns'])

    def test_missing_spawn_identity_is_unknown(self):
        with patch('colvia.platforms.git_child.group_absent',return_value=True):self.assertFalse(self.child.closed(self.area))
    def test_late_closure_does_not_need_exit_callback(self):
        self.started()
        with patch('colvia.platforms.git_child.group_absent',return_value=True):self.assertTrue(self.child.closed(self.area))
    def test_historical_exit_does_not_override_live_group(self):
        self.started();(self.area/'exited.json').write_bytes(canonical_bytes(dict(group_absent=True)))
        with patch('colvia.platforms.git_child.group_absent',return_value=False):self.assertFalse(self.child.closed(self.area))
    def test_invalid_identity_refuses(self):
        (self.area/'started.json').write_bytes(canonical_bytes(dict(pid=1,birth=None)))
        with self.assertRaisesRegex(RecordError,'identity-invalid'):self.child.closed(self.area)

if __name__=='__main__':unittest.main()
