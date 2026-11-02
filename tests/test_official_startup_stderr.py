"""Startup diagnostic, bounded suffix, and cancellation boundaries on real adapter methods."""
import contextlib
import os
import selectors
import time
import unittest
from types import SimpleNamespace
from unittest import mock

from fixtures.official_rpc_fixture import quiet_rpc
from hv2ref import official_adapter as adapter
from hv2ref import official_entry
from hv2ref.errors import ContractError


WARNING = (b'WARNING: proceeding, even though we could not create PATH aliases: '
           b'Operation not permitted (os error 1)\n')
PINS = {'BIN': official_entry.CLI_SHA256, 'CODE_MODE_HOST': official_entry.HELPER_SHA256}


def initializing_rpc():
    rpc = quiet_rpc()
    rpc.in_initialize = True
    rpc.stderr_eof = False
    rpc.err_bytes = rpc.trace_bytes = 0
    rpc.path_warning_mode = None
    rpc.deadline = 2.0
    rpc.host = SimpleNamespace(
        spec={'request': {'runtime': {'sha256': PINS.copy()}, 'expires_wall_ns': 2_000_000_000}},
        cancelled=lambda: False, diagnostic=mock.Mock())
    return rpc


class WarningTests(unittest.TestCase):
    def test_exact_line_is_single_use_only_for_pinned_initialize(self):
        for pin in (None, 'BIN', 'CODE_MODE_HOST'):
            for raw in (WARNING, WARNING[:101]):
                if pin is None and len(raw) == 101:
                    continue  # Split reception is exercised below.
                rpc = initializing_rpc()
                if pin is not None:
                    rpc.host.spec['request']['runtime']['sha256'][pin] = 'different'
                with self.subTest(pin=pin, length=len(raw)):
                    if pin is None:
                        rpc.err(raw)
                        self.assertEqual('single_read', rpc.path_warning_mode)
                        self.assertIsNone(rpc.initialize_failure)
                        rpc.host.diagnostic.assert_not_called()
                    with self.assertRaisesRegex(ContractError, 'protocol_refused'):
                        rpc.err(raw)
                    self.assertTrue(rpc.stderr_refused)
        rpc = initializing_rpc()
        rpc.in_initialize = False
        with self.assertRaisesRegex(ContractError, 'protocol_refused'):
            rpc.err(WARNING)
        self.assertIsNone(rpc.path_warning_mode)

    def test_only_the_101_byte_prefix_can_wait(self):
        for n in range(1, len(WARNING)):
            for raw in (WARNING[:n], WARNING[:n-1] + b'\xff'):
                if raw == WARNING[:101]:
                    continue
                rpc = initializing_rpc()
                with self.subTest(length=n), self.assertRaisesRegex(ContractError, 'protocol_refused'):
                    rpc.err(raw)
                self.assertIsNone(rpc.path_warning_mode)
        for raw in (WARNING + WARNING, WARNING[:-1] + b'\r\n', WARNING + b'X'):
            rpc = initializing_rpc()
            with self.assertRaisesRegex(ContractError, 'protocol_refused'):
                rpc.err(raw)
            self.assertEqual('unclassified', rpc.initialize_failure['code'])

    def split_result(self, arrivals, *, rpc_deadline=1.0, cancel_at=3., read_lag=0.):
        # A virtual clock makes the 50 ms cutoff and comparisons at equality deterministic.
        rpc = initializing_rpc()
        rpc.p = SimpleNamespace(stderr=SimpleNamespace(fileno=lambda: 7))
        clock = mock.Mock()
        clock.now = 0.
        clock.monotonic.side_effect = lambda: clock.now
        clock.time_ns.return_value = 0
        rpc.host.cancelled = lambda: clock.now >= cancel_at
        chunks = list(arrivals)
        poller = mock.MagicMock()
        poller.__enter__.return_value = poller

        def wait(duration):
            self.assertGreater(duration, 0.)
            ready = bool(chunks and chunks[0][0] <= clock.now + duration)
            clock.now = max(clock.now, chunks[0][0]) if ready else clock.now + duration
            return [True] if ready else []

        def read(fd, limit):
            self.assertEqual(7, fd)
            self.assertGreater(limit, 3)  # overlong tails must be visible
            clock.now += read_lag
            return chunks.pop(0)[1]

        poller.select.side_effect = wait
        with mock.patch.object(adapter, 'time', clock), mock.patch.object(adapter.selectors, 'DefaultSelector', return_value=poller), mock.patch.object(os, 'read', side_effect=read):
            try:
                rpc.err(WARNING[:101], rpc_deadline=rpc_deadline)
            except (ContractError, TimeoutError) as error:
                self.assertTrue(rpc.stderr_refused)
                return rpc, adapter.reason_code(error)
        return rpc, None

    def test_split_forms_deadlines_and_refusal_classes(self):
        tail = WARNING[101:]
        for parts in ([tail], [tail[:1], tail[1:]], [tail[:2], tail[2:]], [tail[i:i+1] for i in range(len(tail))]):
            with self.subTest(parts=len(parts)):
                rpc, error = self.split_result([(.005 + i*.006, val) for i, val in enumerate(parts)])
                self.assertIsNone(error)
                self.assertEqual(('joined_101', 104), (rpc.path_warning_mode, rpc.err_bytes))
                with self.assertRaisesRegex(ContractError, 'protocol_refused'):
                    rpc.err(WARNING)
        rpc, error = self.split_result([(.049999, tail)])
        self.assertIsNone(error)
        self.assertEqual('joined_101', rpc.path_warning_mode)
        for arrivals, lag, code in (
                ([(.05, tail)], 0, 'path_suffix_timeout'), ([(.051, tail)], 0, 'path_suffix_timeout'),
                ([(.0499, tail)], .0002, 'path_suffix_timeout'),
                ([(.02, tail[:1]), (.043, tail[1:2]), (.051, tail[2:])], 0, 'path_suffix_timeout'),
                ([], 0, 'path_suffix_timeout'), ([(.002, b'')], 0, 'path_suffix_eof'),
                ([(.002, tail + b'X')], 0, 'path_suffix_extra'), ([(.002, b'bad')], 0, 'path_suffix_mismatch')):
            with self.subTest(code=code):
                rpc, error = self.split_result(arrivals, read_lag=lag)
                self.assertEqual('protocol_refused', error)
                self.assertEqual({'source':'stderr','phase':'initialize','code':code,'byte_count':101}, rpc.initialize_failure)
                self.assertIsNone(rpc.path_warning_mode)
        for options, expected in (({'rpc_deadline': .01}, 'deadline'), ({'cancel_at': .01}, 'cancelled')):
            rpc, error = self.split_result([(.03, tail)], **options)
            self.assertEqual(expected, error)
            self.assertIsNone(rpc.path_warning_mode)

    def test_queued_callback_and_response_cannot_hide_stderr(self):
        for held in (True, False):
            with self.subTest(held=held), contextlib.ExitStack() as stack:
                reader, writer = os.pipe()
                stderr = stack.enter_context(os.fdopen(reader, 'rb', buffering=0))
                output = stack.enter_context(os.fdopen(writer, 'wb', buffering=0))
                os.set_blocking(reader, False)
                rpc = initializing_rpc()
                rpc.p = SimpleNamespace(stderr=stderr)
                rpc.sel = stack.enter_context(selectors.DefaultSelector())
                rpc.sel.register(stderr, selectors.EVENT_READ)
                rpc.deadline = time.monotonic() + 1
                rpc.host.spec['request']['expires_wall_ns'] = time.time_ns() + 10**9
                rpc.held, rpc.messages = [], []
                queued = rpc.held if held else rpc.messages
                queued.append({'method': 'item/tool/call' if held else 'turn/completed'})
                output.write(WARNING[:101] + b'bad')
                # Force the actual pipe to expose the prefix as its first read.
                native_read = os.read
                lengths = []
                def split(fd, size):
                    part = native_read(fd, min(size, 101) if not lengths else size)
                    lengths.append(len(part))
                    return part
                with mock.patch.object(os, 'read', side_effect=split), self.assertRaisesRegex(ContractError, 'protocol_refused'):
                    rpc.event()
                self.assertEqual([101, 3], lengths)
                self.assertEqual(1, len(queued))
                self.assertEqual('path_suffix_mismatch', rpc.initialize_failure['code'])

    def test_read_window_honors_grant_expiry_deadline_and_boundary(self):
        for now, expiry, seen, outcome in (
                (4.9, 10, True, 'cancelled'), (5., 10, True, 'worker_budget_consumed'),
                (5.1, 10, True, 'worker_budget_consumed'), (.02, .01, True, 'deadline')):
            rpc = initializing_rpc()
            rpc.deadline = 10.
            rpc.host.spec['request']['expires_wall_ns'] = round(expiry * 10**9)
            rpc.host.cancelled = lambda: seen
            rpc.p = SimpleNamespace(poll=lambda: None)
            rpc.check_stderr = mock.Mock()
            rpc.cancel_seen_after_read = False
            with self.subTest(now=now, expiry=expiry), mock.patch.object(adapter, 'time') as clock:
                clock.monotonic.side_effect = [0., now]
                clock.time_ns.return_value = round(now * 10**9)
                if outcome == 'deadline':
                    with self.assertRaisesRegex(ContractError, 'deadline'):
                        rpc.read_limit_reason()
                else:
                    self.assertEqual(outcome, rpc.read_limit_reason())
                self.assertEqual(outcome == 'cancelled', rpc.cancel_seen_after_read)

    def test_open_stderr_at_close_is_unconfirmed(self):
        with contextlib.ExitStack() as stack:
            reader, writer = os.pipe()
            stderr = stack.enter_context(os.fdopen(reader, 'rb', buffering=0))
            stack.enter_context(os.fdopen(writer, 'wb', buffering=0))
            os.set_blocking(reader, False)
            rpc = initializing_rpc()
            rpc.p = SimpleNamespace(stderr=stderr)
            with self.assertRaisesRegex(ContractError, 'closure_unconfirmed'):
                rpc.check_stderr(require_eof=True)
