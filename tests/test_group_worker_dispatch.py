from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path
from types import SimpleNamespace
import sys
import os
import tempfile
import tomllib
import threading
import time
import unittest
from unittest.mock import patch

from colvia.cli import parser
from colvia.codec import RecordError, canonical_bytes, decode_canonical
from colvia.group_worker_dispatch import Dispatch, RESULT_CHECK, digest, route
from colvia.platforms.windows_claude_worker import Conversation
from colvia.platforms.process import ProcessResult
from colvia.platforms.windows_group_workers import (
    CodexExecFailure, _codex_transport_failure, codex_exec_identity, codex_probe_path,
    read_codex_events, verify_codex_diagnostics, verify_codex_project_config,
    managed_instruction, codex_policy, check_instruction_inputs,
)
from colvia.work import WorkService
from test_grouped_acceptance import GroupFixture, available


class WorkerAdapterTests(unittest.TestCase):
    def test_managed_instruction_is_the_only_added_read(self):
        from colvia.project_setup import BLOCK
        from colvia.platforms.project_launcher import project_block
        from colvia.platforms.windows_observation import Observer
        from test_foundation_windows_observation import FilesDouble

        with tempfile.TemporaryDirectory() as area:
            base = Path(area).resolve()
            root = base / 'work'
            root.mkdir()
            guide = root / 'AGENTS.md'
            expected = project_block(BLOCK, 'windows')
            guide.write_bytes(expected)
            approved = root / 'sub' / 'owned.csv'
            approved.parent.mkdir()
            approved.touch()
            peers = [root / 'peer.csv', root / 'CLAUDE.md', root / 'AGENTS.override.md',
                     approved.parent / 'AGENTS.md']
            for peer in peers:
                peer.touch()
            observer = Observer(files=FilesDouble())
            with managed_instruction(root, [approved], observer=observer) as (instruction, raw):
                self.assertEqual((instruction, raw), (guide, expected))
                config = codex_policy(root, [approved], base / 'scratch', base / 'control', instruction)
            permissions = tomllib.loads(config)['permissions']['colvia_worker']['filesystem']
            self.assertEqual(permissions[str(guide)], 'read')
            self.assertEqual(permissions[str(approved)], 'write')
            self.assertTrue(all(permissions[str(peer)] == 'deny' for peer in peers))
            with self.assertRaises(RecordError), managed_instruction(root, [guide], observer=observer):
                self.fail('Managed instructions were admitted for writing')
            for wrong in (b'x' * len(expected), b'user preface' + expected, BLOCK, expected + b' '):
                guide.write_bytes(wrong)
                with self.assertRaises(RecordError), managed_instruction(root, [approved], observer=observer):
                    self.fail('Unrecognized instructions were admitted')
            guide.unlink()
            with self.assertRaisesRegex(RecordError, 'group-worker-managed-instruction-unverified'), managed_instruction(root, [approved], observer=observer):
                self.fail('Missing instructions were admitted')
            real = base / 'source'
            real.write_bytes(expected)
            os.link(real, guide)
            with self.assertRaises(RecordError), managed_instruction(root, [approved], observer=observer):
                self.fail('Multiple links were admitted')
            guide.unlink()
            guide.symlink_to(real)
            with self.assertRaises(RecordError), managed_instruction(root, [approved], observer=observer):
                self.fail('A symlink was admitted')

    def test_mixed_instruction_write_scope_is_rejected_before_launch(self):
        with tempfile.TemporaryDirectory() as area:
            root = Path(area).resolve()
            guide = root / 'agents.md'
            guide.write_bytes(b'test')
            item = dict(provider='claude', source_path=str(root), scope=[guide.name])
            check_instruction_inputs([item])
            with self.assertRaisesRegex(RecordError, 'group-worker-instruction-in-write-scope'):
                check_instruction_inputs([item, dict(item, provider='codex')])


    def test_three_routes_only(self):
        for coordinator, workers in (
            ('claude',{'one':'claude','two':'claude'}),
            ('codex',{'one':'codex','two':'codex'}),
            ('claude',{'one':'claude','two':'codex'}),
        ):
            self.assertEqual(route(coordinator,workers),workers)
        for coordinator, workers in (
            ('codex',{'one':'claude','two':'codex'}),
            ('codex',{'one':'claude','two':'claude'}),
            ('claude',{'one':'codex','two':'codex'}),
            ('claude',{'one':'claude','two':'other'}),
            ('claude',{'one':'claude'}),
        ):
            with self.assertRaisesRegex(RecordError,'group-worker-route-invalid'):
                route(coordinator,workers)

    def test_managed_group_help_preserves_the_qualified_surface(self):
        output = StringIO()
        with redirect_stdout(output), self.assertRaises(SystemExit) as exited:
            parser(managed=True).parse_args(['group', '--help'])
        self.assertEqual(exited.exception.code, 0)
        self.assertIn('accept', output.getvalue())
        self.assertNotIn('workers-', output.getvalue())

    def test_claude_denies_any_permission_request_before_tool_inventory(self):
        root=Path.cwd()
        worker=Conversation(root,[root/'unused.txt'],'synthetic','scope')
        request=dict(type='control_request',request_id='1',request=dict(
            subtype='can_use_tool',tool_name='Write',input={'file_path':str(root/'unused.txt')}))
        with self.assertRaisesRegex(RecordError,'group-worker-unknown-permission-request'):
            worker.receive(request)

    def test_codex_only_excludes_the_account_configuration(self):
        home = Path(Path.cwd().anchor) / 'synthetic-account'
        work = home / 'checkout' / 'worker'
        existing = {home / '.codex'}

        def lstat(path):
            if path not in existing:
                raise FileNotFoundError(path)

        with patch.object(type(home), 'resolve', return_value=home), \
             patch.object(type(home), 'lstat', autospec=True, side_effect=lstat) as inspect:
            verify_codex_project_config(work, home)
            self.assertNotIn(home / '.codex', [call.args[0] for call in inspect.call_args_list])
            rejected = 'group-worker-codex-project-config-unverified'
            with self.assertRaisesRegex(RecordError, rejected):
                verify_codex_project_config(home, home)
            for project in (work, work.parent):
                dot_codex = project / '.codex'
                existing.add(dot_codex)
                with self.assertRaisesRegex(RecordError, rejected):
                    verify_codex_project_config(work, home)
                existing.remove(dot_codex)

    def test_codex_probe_accepts_spaces_and_rejects_shell_syntax(self):
        root = Path(Path.cwd().anchor)
        self.assertEqual(codex_probe_path(root / 'folder with spaces' / 'file.csv'),
                         str(root / 'folder with spaces' / 'file.csv'))
        for path in ('a&b.csv', '%TEMP%', 'x^y.csv', 'x(y).csv', 'x|y.csv'):
            with self.assertRaisesRegex(RecordError, 'group-worker-codex-probe-path-unqualified'):
                codex_probe_path(root / path)

    def test_codex_incomplete_turn_has_no_claimed_result(self):
        values=(b'{"type":"thread.started","thread_id":"synthetic"}\n'
                b'{"type":"item.completed","item":{"type":"file_change"}}\n')
        with self.assertRaisesRegex(RecordError,'group-worker-turn-incomplete'):
            read_codex_events(values)
        self.assertEqual(read_codex_events(values+b'{"type":"turn.completed"}\n'),'synthetic')
        with self.assertRaisesRegex(RecordError,'group-worker-turn-incomplete'):
            read_codex_events(values+b'{"type":"turn.failed"}\n{"type":"turn.completed"}\n')


    def test_codex_returned_exit_and_protocol_are_independent(self):
        opened = b'{"type":"thread.started","thread_id":"do-not-record-thread"}\n'
        activity = b'{"type":"item.completed","item":{"type":"file_change","name":"do-not-record-path"}}\n'
        complete = b'{"type":"turn.completed","message":"do-not-record-message"}\n'
        failed = b'{"type":"error","message":"do-not-record-failure"}\n'
        valid = opened + activity + complete
        cases = (
            (0, 1, valid, True), (16, 1, valid, False), (0, 1, opened + activity, False),
            (16, 1, b'', False), (0, 1, opened + complete, False),
            (0, 1, opened + valid, False), (0, 1, valid + complete, False),
            (0, 1, valid + failed, False), (0, 1, valid.replace(b'do-not-record-thread', b''), False),
            (0, 1, valid.replace(b'\n', b'\r\n'), True),
            (0, 1, b'\xef\xbb\xbf' + valid, True), (0, 1, valid.rstrip(b'\n'), True),
            (0, 1, valid + b'\xff', False), (0, 1, valid + b'{', False),
            (0, 1, b'{"type":"item.completed","item":null}\n' + valid, False),
            (0, 1, b'{"type":"x"}\n' * 300 + b'q' * 70000, False), (0, 0, valid, False),
        )
        for exit_code, starts, stream, accepted in cases:
            with self.subTest(exit_code=exit_code, starts=starts, length=len(stream), accepted=accepted):
                # The r4 decision used the same parser after both process gates.
                try:
                    if exit_code != 0 or starts != 1:
                        raise RecordError('group-worker-turn-incomplete')
                    old = read_codex_events(stream)
                except (ValueError, AttributeError, RecursionError):
                    old = None
                self.assertEqual(old is not None, accepted)
                result = ProcessResult(exit_code, stream, b'do-not-record-stderr')
                if accepted:
                    self.assertEqual(codex_exec_identity(result, starts), old)
                    continue
                with self.assertRaises(CodexExecFailure) as refused:
                    codex_exec_identity(result, starts)
                observed = refused.exception.diagnostics
                self.assertEqual(observed['stage'], 'returned')
                self.assertEqual(observed['exit_code'], exit_code)
                self.assertEqual(observed['starts'], starts)
                self.assertEqual(observed['controller_stop'], 'none')
                self.assertEqual(observed['counts']['completed_turns'], min(stream.count(complete), 255))
                self.assertLessEqual(max(observed['counts'].values()), 255)
                self.assertNotIn(b'do-not-record', canonical_bytes(observed))

    def test_invalid_codex_result_keeps_original_worker_error(self):
        for result, reason in (
            (ProcessResult(-1, b'', b''), 'group-worker-turn-incomplete'),
            (ProcessResult(None, b'', b''), 'group-worker-turn-incomplete'),
            (SimpleNamespace(code=0, stderr=b''), 'group-worker-process-unavailable'),
        ):
            with self.subTest(reason=reason):
                with self.assertRaisesRegex(CodexExecFailure, reason) as refused:
                    codex_exec_identity(result, 1)
                observed = refused.exception.diagnostics
                self.assertEqual(observed['stage'], 'result-unavailable')
                self.assertIsNone(observed['exit_code'])
                verify_codex_diagnostics(observed)
        with self.assertRaises(CodexExecFailure) as refused:
            codex_exec_identity(ProcessResult(0xc0000005, b'', b''), 1)
        self.assertEqual(refused.exception.diagnostics['exit_code'], 0xc0000005)

    def test_codex_transport_does_not_claim_a_returned_exit(self):
        for reason, stop in (('process-timeout', 'timeout'), ('process-cancelled', 'cancel'),
                             ('windows-child-closure-unknown', 'unknown')):
            observed = _codex_transport_failure(RecordError(reason), 1)
            self.assertEqual(observed.code, reason)
            self.assertEqual(observed.diagnostics['stage'], 'transport')
            self.assertIsNone(observed.diagnostics['exit_code'])
            self.assertEqual(observed.diagnostics['controller_stop'], stop)
            with self.assertRaisesRegex(RecordError, 'group-worker-codex-diagnostics-invalid'):
                verify_codex_diagnostics(dict(observed.diagnostics, untrusted='do-not-record'))


@unittest.skipUnless(sys.platform=='darwin' and available(),'native common group fixture unavailable')
class GroupDispatchTests(GroupFixture,unittest.TestCase):
    def dispatch(self):
        for root in (self.root,*self.paths):
            (root/'second.csv').write_bytes(b'item,total\nbeta,0\n')
        self.checks[0]['argv']=[sys.executable,'-B','-c',
            "from pathlib import Path; assert Path('report.md').read_bytes()==b'alpha\\n'; "
            "assert Path('second.csv').read_bytes()==b'item,total\\nbeta,23\\n'"]
        for index,scope in enumerate(('report.md','second.csv')):
            self.sources[index].plan(operation=self.op(),work='member'+str(index),title='Edit one file',
                                     goal='Write the intended row',scope=[scope],checks=[RESULT_CHECK])
        group=self.create()
        journal=self.home/'dispatch';journal.mkdir(mode=0o700)
        plan=dict(group='pair',journal=str(journal),group_head=group['head'],group_receipt=group['receipt'],
                  members=[member | {'provider':'claude'} for member in group['members']])
        plan['dispatch_receipt']=digest(plan)
        return Dispatch(self.group,'pair',journal),plan

    def test_first_local_dispatch_validates_under_lock_before_reservation(self):
        controller, plan = self.dispatch()
        initial = self.store.root().ref
        def changed():
            raise RecordError('group-worker-dispatch-stale')
        with self.assertRaisesRegex(RecordError, 'group-worker-dispatch-stale'):
            controller.run(plan, receipt=plan['dispatch_receipt'], statement='Synthetic decision',
                           native=lambda *_: self.fail('No paid launch'), first_dispatch_check=changed)
        self.assertEqual(self.store.root().ref, initial)
        self.assertFalse(controller.path.exists())
        with self.assertRaisesRegex(RecordError, 'group-worker-dispatch-stale'):
            controller.run(plan, receipt=plan['dispatch_receipt'], statement='Fresh decision',
                           native=lambda *_: self.fail('No paid launch'), first_dispatch_check=changed)
        with controller._lock():
            controller._reserve(plan)
        with self.assertRaisesRegex(RecordError, 'group-worker-dispatch-already-reserved'):
            controller.run(plan, receipt=plan['dispatch_receipt'], statement='Repeated decision',
                           native=lambda *_: self.fail('No paid launch'), first_dispatch_check=changed)

    def test_exact_two_overlapping_results_recovered_and_group_accepted(self):
        controller,plan=self.dispatch()
        overlap=threading.Barrier(2)
        writes={'report.md':b'alpha\n','second.csv':b'item,total\nbeta,23\n'}
        def worker(item, session, _area):
            overlap.wait(5)
            path=item['scope'][0]
            (Path(item['source_path'])/path).write_bytes(writes[path])
            return dict(identity=session,provider=item['provider'],closed_ns=time.monotonic_ns(),exit=0,job_closed=True,writes=item['scope'])
        shown=controller.run(plan,receipt=plan['dispatch_receipt'],statement='Approve exact group and dispatch',native=worker)
        self.assertEqual(shown['submitted'],2)
        self.assertTrue(shown['ready_for_group_candidate'])
        before=self.store.root().ref
        self.assertEqual(controller.resume(),shown)
        self.assertEqual(self.store.root().ref,before)
        self.assertEqual((self.root/'report.md').read_bytes(),b'synthetic report\n')
        self.group.candidate(operation=self.op(),group='pair')
        checked=self.group.check(operation=self.op(),group='pair')
        self.assertEqual(checked['state'],'review')
        self.assertEqual(self.execute(checked)['accepted'],2)
        self.assertEqual((self.root/'second.csv').read_bytes(),writes['second.csv'])

    def test_failed_spawn_preserves_submitted_peer_without_relaunch(self):
        controller,plan=self.dispatch()
        seen=[]
        def worker(item,session,area):
            seen.append(item['work'])
            if item['work']=='member1':
                raise TypeError('synthetic malformed provider message')
            (Path(item['source_path'])/'report.md').write_bytes(b'alpha\n')
            return dict(identity=session,provider=item['provider'],closed_ns=time.monotonic_ns(),exit=0,job_closed=True,writes=item['scope'])
        result=controller.run(plan,receipt=plan['dispatch_receipt'],statement='Approve group and dispatch',native=worker)
        self.assertEqual(result['submitted'],1)
        self.assertFalse(result['ready_for_group_candidate'])
        self.assertEqual(result['workers']['member1']['phase'],'stopped')
        self.assertEqual(result['workers']['member1']['error_type'],'TypeError')
        self.assertEqual(controller.resume(),result)
        self.assertCountEqual(seen,['member0','member1'])
        with self.assertRaises(RecordError):
            self.group.candidate(operation=self.op(),group='pair')


    def test_approval_published_before_checkpoint_is_recovered_without_launch(self):
        controller, plan = self.dispatch()
        with patch.object(controller, '_save', side_effect=OSError('lost dispatch checkpoint')):
            with self.assertRaises(OSError):
                controller.run(plan, receipt=plan['dispatch_receipt'], statement='Approve exact fixtures',
                               native=lambda *_: self.fail('No worker may launch before the checkpoint'))
        recorded_head = self.store.root().ref
        recovered = controller.resume()
        self.assertEqual(recorded_head, self.store.root().ref)
        self.assertEqual(recovered['submitted'], 0)
        self.assertFalse(recovered['ready_for_group_candidate'])
        self.assertTrue(all(lane['phase'] == 'stopped' for lane in recovered['workers'].values()))
        self.assertEqual(controller.resume(), recovered)

    def test_unrecorded_approval_leaves_exact_prelaunch_reservation_reusable(self):
        controller, plan = self.dispatch()
        def no_worker(*_):
            self.fail('No worker may launch before approval')
        with patch.object(controller.grouped, 'approve', side_effect=RecordError('synthetic-approval-refusal')):
            with self.assertRaisesRegex(RecordError, 'synthetic-approval-refusal'):
                controller.run(plan, receipt=plan['dispatch_receipt'], statement='Approve exact fixtures', native=no_worker)
        reserved = controller.resume()
        self.assertTrue(all(lane['phase'] == 'reserved' for lane in reserved['workers'].values()))
        unrelated = dict(plan, group_receipt='unrelated')
        with self.assertRaisesRegex(RecordError, 'group-worker-dispatch-already-reserved'):
            controller.run(unrelated, receipt=plan['dispatch_receipt'], statement='Approve exact fixtures', native=no_worker)

        def worker(item, session, _area):
            path = item['scope'][0]
            (Path(item['source_path']) / path).write_bytes(b'Synthetic worker result\n')
            return dict(identity=session, provider=item['provider'], exit=0, job_closed=True, writes=[path])

        result = controller.run(plan, receipt=plan['dispatch_receipt'], statement='Approve exact fixtures', native=worker)
        self.assertEqual(result['submitted'], 2)
        for work, lane in result['workers'].items():
            self.assertEqual(lane['session'], reserved['workers'][work]['session'])

    def test_checked_submission_refusal_is_terminal_and_keeps_the_peer(self):
        controller, plan = self.dispatch()
        submits = []
        original = WorkService.submit

        def submit(worker, **kwargs):
            submits.append(kwargs['work'])
            if kwargs['work'] == 'member0':
                raise RecordError('worker-result-observation-changed')
            return original(worker, **kwargs)

        def worker(item, session, _area):
            path = item['scope'][0]
            (Path(item['source_path']) / path).write_bytes(b'Synthetic worker result\n')
            return dict(identity=session, provider=item['provider'], exit=0, job_closed=True, writes=[path])

        with patch.object(WorkService, 'submit', submit):
            result = controller.run(plan, receipt=plan['dispatch_receipt'], statement='Approve exact fixtures', native=worker)
            self.assertEqual(controller.resume(), result)
        self.assertCountEqual(submits, ['member0', 'member1'])
        self.assertEqual(result['submitted'], 1)
        self.assertEqual(result['workers']['member0']['phase'], 'stopped')
        self.assertEqual(result['workers']['member0']['reason'], 'worker-result-observation-changed')
        self.assertEqual(result['workers']['member1']['phase'], 'submitted')


    def test_checkpoint_failure_cancels_an_open_peer_and_prevents_submission(self):
        controller, plan = self.dispatch()
        both_started = threading.Barrier(2)
        peer_closed = threading.Event()

        def worker(item, session, _area):
            both_started.wait(5)
            if item['work'] == 'member1':
                if not worker.cancelled.wait(5):
                    self.fail('Peer did not receive the cancellation signal')
                peer_closed.set()
                raise RecordError('process-cancelled')
            path = item['scope'][0]
            (Path(item['source_path']) / path).write_bytes(b'Synthetic worker result\n')
            return dict(identity=session, provider=item['provider'], exit=0, job_closed=True, writes=[path])

        worker.cancelled = threading.Event()
        original = controller._save

        def save(raw, state):
            if state['work']['member0']['phase'] == 'ready':
                raise OSError('Synthetic checkpoint error during collection')
            return original(raw, state)

        with patch.object(controller, '_save', save):
            with self.assertRaisesRegex(OSError, 'checkpoint error'):
                controller.run(plan, receipt=plan['dispatch_receipt'], statement='Approve exact fixtures', native=worker)
        self.assertTrue(peer_closed.is_set())
        result = controller.resume()
        self.assertEqual(result['submitted'], 0)
        self.assertTrue(all(lane['phase'] == 'stopped' for lane in result['workers'].values()))


    def test_codex_failure_diagnostics_are_stopped_and_recovered_with_proved_peer(self):
        controller, plan = self.dispatch()
        plan['members'][1]['provider'] = 'codex'
        del plan['dispatch_receipt']
        plan['dispatch_receipt'] = digest(plan)
        attempts = []

        def worker(item, session, _area):
            attempts.append(item['provider'])
            if item['provider'] == 'codex':
                return codex_exec_identity(ProcessResult(9, b'', b'do-not-record'), 1)
            path = item['scope'][0]
            (Path(item['source_path']) / path).write_bytes(b'Synthetic worker result\n')
            return dict(identity=session, provider=item['provider'], exit=0, job_closed=True, writes=[path])

        result = controller.run(plan, receipt=plan['dispatch_receipt'], statement='Approve exact fixtures', native=worker)
        self.assertEqual(result['submitted'], 1)
        self.assertFalse(result['ready_for_group_candidate'])
        self.assertEqual(result['workers']['member0']['phase'], 'submitted')
        self.assertNotIn('codex_diagnostics', result['workers']['member0'])
        self.assertEqual(result['workers']['member1']['phase'], 'stopped')
        self.assertEqual(result['workers']['member1']['codex_diagnostics']['exit_code'], 9)
        self.assertEqual(controller.resume(), result)
        self.assertCountEqual(attempts, ['claude', 'codex'])
        captured = controller.files.read(controller.path, 256 * 1024)
        self.assertNotIn(b'do-not-record', captured)
        changed = decode_canonical(captured)
        changed['work']['member1']['codex_diagnostics']['unknown'] = 'field'
        controller.files.replace(controller.path, canonical_bytes(changed), captured)
        with self.assertRaisesRegex(RecordError, 'group-worker-codex-diagnostics-invalid'):
            controller.resume()
        self.assertCountEqual(attempts, ['claude', 'codex'])
