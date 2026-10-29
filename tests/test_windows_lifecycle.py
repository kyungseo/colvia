"""Windows lifecycle contracts. Native cases require the fixed runner inputs.

Portable cases validate record relationships, not native execution. Native
fixtures stay under COLVIA_NATIVE_TEST_ROOT for independent prefix inspection.
"""
from __future__ import annotations

import copy
from contextlib import contextmanager
import hashlib
import json
import os
from pathlib import Path
import shutil
import stat
import subprocess
import sys
import time
import unittest
from unittest import mock

from hv2ref import jsonio, product, workspace
from hv2ref.errors import ContractError, InjectedCrash

SOURCE = Path(__file__).resolve().parents[1]
TIME = "2026-01-01T00:00:00Z"
MANAGED = tuple(sorted((
    '.gitignore', 'AGENTS.md', 'CLAUDE.md', 'PRODUCT-CAPABILITIES.json', 'README.md',
    'adapters/colvia-work/SKILL.md', 'colvia', 'docs/CONCEPTS.md', 'docs/GENERAL-WORK.md',
    'docs/GETTING-STARTED.md', 'docs/GUIDED-INTENT-FORMATION.md', 'docs/MAINTAINING.md',
    'docs/MANUAL-OPERATION.md', 'docs/OPERATIONS.md', 'docs/README.md', 'docs/REFERENCE.md',
    'docs/SECURITY-AND-SUPPORT.md', 'docs/WORKSPACE-CONTRACT.md',
    'src/hv2ref/__init__.py', 'src/hv2ref/candidates.py', 'src/hv2ref/cli.py', 'src/hv2ref/continuation.py',
    'src/hv2ref/errors.py', 'src/hv2ref/intent.py', 'src/hv2ref/jsonio.py',
    'src/hv2ref/product.py', 'src/hv2ref/umbrella.py', 'src/hv2ref/view.py',
    'src/hv2ref/work.py', 'src/hv2ref/workspace.py',
), key=lambda value: value.encode()))


def canonical(value):
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2, allow_nan=False) + "\n").encode()


def sha(data):
    return hashlib.sha256(data).hexdigest()


def physical(root):
    """Independent bytes/type/attribute inventory; no product observation helper."""
    rows = {}
    for path in sorted(root.rglob('*')):
        info = path.lstat(); name = path.relative_to(root).as_posix()
        if stat.S_ISDIR(info.st_mode): rows[name] = ('directory',)
        elif stat.S_ISREG(info.st_mode): rows[name] = ('file', path.read_bytes(), getattr(info, 'st_file_attributes', 0))
        else: rows[name] = ('other', info.st_mode)
    return rows


@contextmanager
def fail_native_flush_for(path, *, name_prefix=None):
    """Inject error5 for an exact file or a named staging family in an exact parent."""
    api = jsonio._windows_api(); original = api.FlushFileBuffers; calls = []
    suffix = str(path).replace('/', '\\').casefold()
    def flush(handle):
        state = jsonio._windows_handle_state(handle)
        name = state['final_name'].casefold()
        match = name.endswith(suffix) if name_prefix is None else (name.rsplit('\\', 1)[0].endswith(suffix) and name.rsplit('\\', 1)[-1].startswith(name_prefix.casefold()))
        if not state['directory'] and match:
            calls.append({'path': state['final_name'], 'injected_winerror': 5})
            api.C.set_last_error(5)
            return False
        return original(handle)
    with mock.patch.object(api, 'FlushFileBuffers', side_effect=flush):
        yield calls


@contextmanager
def fail_native_replace_for(destination):
    """One exact replacement fault; native path/preflight IO still executes."""
    original = os.replace; calls = []; expected = os.path.normcase(os.path.abspath(destination))
    def replace(source, target, *args, **kwargs):
        if os.path.normcase(os.path.abspath(target)) == expected:
            calls.append({'source': str(source), 'destination': str(target), 'injected_winerror': 32})
            error = OSError('synthetic sharing violation'); error.winerror = 32
            raise error
        return original(source, target, *args, **kwargs)
    with mock.patch.object(os, 'replace', side_effect=replace): yield calls


def native_event_name(path):
    value = os.fspath(path).replace('/', '\\')
    return (value[4:] if value.startswith('\\\\?\\') else value).casefold()


@contextmanager
def record_native_publication():
    """Pass through real API calls; record completed flushes and publication attempts."""
    from contextlib import ExitStack
    api = jsonio._windows_api(); original_flush = api.FlushFileBuffers; events = []
    original_path_open = Path.open
    def path_open(path, mode='r', *args, **kwargs):
        if 'x' in mode:
            events.append({'kind': 'create', 'path': native_event_name(path), 'phase': 'attempt'})
        return original_path_open(path, mode, *args, **kwargs)
    def flush(handle):
        state = jsonio._windows_handle_state(handle)
        result = original_flush(handle)
        error = 0 if result else api.C.get_last_error()
        events.append({'kind': 'flush', 'path': native_event_name(state['final_name']),
                       'directory': state['directory'], 'success': bool(result), 'winerror': error})
        return result
    def publication(kind, original):
        def observed(*args, **kwargs):
            if kind != 'create' or args[1] & os.O_CREAT:
                destination = args[1] if kind in ('replace', 'rename') else args[0]
                event = {'kind': kind, 'path': native_event_name(destination), 'phase': 'attempt'}
                if kind in ('replace', 'rename'): event['source'] = native_event_name(args[0])
                events.append(event)
            return original(*args, **kwargs)
        return observed
    with ExitStack() as stack:
        stack.enter_context(mock.patch.object(api, 'FlushFileBuffers', side_effect=flush))
        stack.enter_context(mock.patch.object(Path, 'open', new=path_open))
        for kind, attr in (('create', 'open'), ('replace', 'replace'), ('rename', 'rename'), ('unlink', 'unlink')):
            stack.enter_context(mock.patch.object(os, attr, side_effect=publication(kind, getattr(os, attr))))
        yield events


def assert_native_reflush_before(case, events, path, next_publication):
    name, parent, destination = native_event_name(path), native_event_name(path.parent), native_event_name(next_publication)
    boundary = next((i for i, e in enumerate(events) if e['kind'] in ('create', 'replace', 'rename', 'unlink') and e['path'] == destination), None)
    case.assertIsNotNone(boundary, ('required next publication missing', destination, events))
    files = [i for i, e in enumerate(events[:boundary]) if e['kind'] == 'flush' and e['path'] == name and not e['directory'] and e['success']]
    case.assertTrue(files, ('required file reflush missing before publication', name, events))
    parents = [i for i, e in enumerate(events[:boundary]) if e['kind'] == 'flush' and e['path'] == parent and e['directory'] and (e['success'] or e['winerror'] in (1, 50)) and i > files[0]]
    case.assertTrue(parents, ('required parent sync missing after file reflush', parent, events))


def assert_native_staging_flush_before_replace(case, events, destination):
    name = native_event_name(destination)
    replacements = [(i, e) for i, e in enumerate(events) if e['kind'] == 'replace' and e['path'] == name]
    case.assertTrue(replacements, ('replace attempt missing', name, events))
    for position, replacement in replacements:
        source = replacement['source']; parent = source.rsplit('\\', 1)[0]
        files = [i for i, e in enumerate(events[:position]) if e['kind'] == 'flush' and e['path'] == source and not e['directory'] and e['success']]
        case.assertTrue(files, ('staging content flush missing before replace', source, events))
        case.assertTrue(any(e['kind'] == 'flush' and e['path'] == parent and e['directory'] and (e['success'] or e['winerror'] in (1, 50)) for e in events[files[0] + 1:position]), ('staging parent sync missing before replace', parent, events))


def release(label, window='windows-2'):
    digest = sha(label.encode())
    return {'id': 'product-release-' + digest[:24], 'sha256': digest, 'inventory_id': window}


def plan_fixture():
    fmt = {'record_type': 'workspace-format', 'format_version': 1,
           'authority_home_id': 'home-a', 'created_at': TIME, 'lineage': None}
    binding = {'record_type': 'product-binding', 'schema_version': 1,
               'authority_home_id': 'home-a', 'operation_id': 'init-a',
               'active_release': release('P'), 'prior_release': None}
    plan = {'record_type': 'lifecycle-plan', 'schema_version': 6, 'operation_id': 'update-a',
            'action': 'update', 'authority_home_id': 'home-a',
            'expected_binding_ref': {'id': 'init-a', 'sha256': sha(canonical(binding))},
            'candidate_release': release('Q'), 'format_sha256': sha(canonical(fmt)),
            'truth_refs': [], 'remove': [], 'preserve': [], 'created_at': TIME,
            'target_fingerprint': sha(b'synthetic target')}
    return fmt, binding, plan


class PortableWindowsLifecycleTests(unittest.TestCase):

    def test_scoped_fault_helpers_hit_only_selected_file_or_staging_family(self):
        from types import SimpleNamespace
        import tempfile
        errors = []; forwarded = []
        api = SimpleNamespace(C=SimpleNamespace(set_last_error=errors.append), FlushFileBuffers=lambda handle: forwarded.append(handle) or True)
        states = {1: {'directory': False, 'final_name': r'\\?\C:\fixture\staging\candidate-first'},
                  2: {'directory': False, 'final_name': r'\\?\C:\fixture\other\candidate-first'},
                  3: {'directory': False, 'final_name': r'\\?\C:\fixture\staging\other-first'},
                  4: {'directory': True, 'final_name': r'\\?\C:\fixture\staging\candidate-directory'}}
        with mock.patch.object(jsonio, '_windows_api', return_value=api), mock.patch.object(jsonio, '_windows_handle_state', side_effect=states.__getitem__):
            with fail_native_flush_for(Path(r'C:\fixture\staging'), name_prefix='candidate-') as failures:
                self.assertFalse(api.FlushFileBuffers(1))
                for handle in (2, 3, 4): self.assertTrue(api.FlushFileBuffers(handle))
            self.assertEqual(1, len(failures)); self.assertEqual([5], errors); self.assertEqual([2, 3, 4], forwarded)
        root = Path(tempfile.mkdtemp(prefix='f-', dir=os.environ['COLVIA_NATIVE_TEST_ROOT'] if sys.platform == 'win32' else None))
        source = root / 'source'; target = root / 'target'; unrelated = root / 'unrelated'
        source.write_bytes(b'source bytes'); target.write_bytes(b'target bytes')
        with fail_native_replace_for(target) as replacements:
            with self.assertRaises(OSError) as caught: os.replace(source, target)
            self.assertEqual(32, caught.exception.winerror); self.assertEqual(b'source bytes', source.read_bytes()); self.assertEqual(b'target bytes', target.read_bytes())
            os.replace(source, unrelated)
        self.assertEqual(1, len(replacements)); self.assertEqual(b'source bytes', unrelated.read_bytes()); self.assertEqual(b'target bytes', target.read_bytes())

    def test_native_publication_recorder_and_order_oracle_negative_controls(self):
        from types import SimpleNamespace
        file, parent, destination = Path(r'C:\fixture\record'), Path(r'C:\fixture'), Path(r'C:\fixture\next')
        calls = []; api = SimpleNamespace(C=SimpleNamespace(get_last_error=lambda: 50), FlushFileBuffers=lambda h: calls.append(h) or h == 1)
        states = {1: {'directory': False, 'final_name': r'\\?\C:\fixture\record'}, 2: {'directory': True, 'final_name': r'\\?\C:\fixture'}}
        with mock.patch.object(jsonio, '_windows_api', return_value=api), mock.patch.object(jsonio, '_windows_handle_state', side_effect=states.__getitem__), mock.patch.object(os, 'open', return_value=99) as opened, mock.patch.object(os, 'replace') as replaced, mock.patch.object(os, 'unlink') as unlinked:
            with record_native_publication() as events:
                self.assertTrue(api.FlushFileBuffers(1)); self.assertFalse(api.FlushFileBuffers(2))
                self.assertEqual(99, os.open(destination, os.O_CREAT | os.O_WRONLY, 0o600))
                os.replace(file, destination); os.unlink(destination)
            self.assertEqual([1, 2], calls); opened.assert_called_once_with(destination, os.O_CREAT | os.O_WRONLY, 0o600)
            replaced.assert_called_once_with(file, destination); unlinked.assert_called_once_with(destination)
        self.assertEqual(['flush', 'flush', 'create', 'replace', 'unlink'], [e['kind'] for e in events])
        # Use native-shaped names directly: Path.parent follows the host platform.
        class NativePath:
            def __init__(self, value): self.value = value
            def __fspath__(self): return self.value
            @property
            def parent(self): return NativePath(self.value.rsplit('\\', 1)[0])
        original = NativePath(r'C:\fixture\record'); next_path = NativePath(r'C:\fixture\next')
        assert_native_reflush_before(self, events, original, next_path)
        assert_native_staging_flush_before_replace(self, events, next_path)
        for changed in (events[1:], [events[0], *events[2:]], [events[1], events[0], *events[2:]], [events[2], *events[:2], *events[3:]]):
            with self.assertRaises(AssertionError): assert_native_reflush_before(self, changed, original, next_path)
        for changed in (events[1:], [events[0], *events[2:]], [events[3], *events[:3], events[4]]):
            with self.assertRaises(AssertionError): assert_native_staging_flush_before_replace(self, changed, next_path)

        # Exercise the real exclusive file API used by product publication.
        import tempfile
        root = Path(tempfile.mkdtemp(prefix='recorder-', dir=os.environ['COLVIA_NATIVE_TEST_ROOT'] if sys.platform == 'win32' else None))
        file, destination = root / 'record', root / 'next'
        file.write_bytes(b'original bytes')
        states = {1: {'directory': False, 'final_name': str(file)}, 2: {'directory': True, 'final_name': str(root)}}
        with mock.patch.object(jsonio, '_windows_api', return_value=api), mock.patch.object(jsonio, '_windows_handle_state', side_effect=states.__getitem__):
            with record_native_publication() as events:
                self.assertTrue(api.FlushFileBuffers(1)); self.assertFalse(api.FlushFileBuffers(2))
                with destination.open(mode='xb') as handle: handle.write(b'next bytes')
                with destination.open('rb') as handle: self.assertEqual(b'next bytes', handle.read())
                with self.assertRaises(FileExistsError):
                    with destination.open('xb'): pass
        self.assertEqual(b'next bytes', destination.read_bytes())
        self.assertEqual(b'original bytes', file.read_bytes())
        self.assertEqual(['flush', 'flush', 'create', 'create'], [e['kind'] for e in events])
        self.assertTrue(all(e['path'] == native_event_name(destination) and e['phase'] == 'attempt' for e in events[2:]))
        assert_native_reflush_before(self, events, file, destination)
        for changed in (events[:2], [events[2], *events[:2], events[3]]):
            with self.assertRaises(AssertionError): assert_native_reflush_before(self, changed, file, destination)

    def test_windows_switch_pair_has_no_cross_window_rank(self):
        fmt, binding, plan = plan_fixture()
        product._switch_plan_shape(plan, fmt)
        new, receipt = product._switch_binding_receipt(plan, binding)
        self.assertEqual(6, receipt['schema_version'])
        self.assertEqual(binding['active_release'], new['prior_release'])
        for side in ('prior', 'candidate'):
            for old in ('entry-1', 'checkout-1', 'planning-1', 'delegation-1', 'continuation-1', 'windows-1'):
                with self.subTest(side=side, window=old):
                    before, changed = copy.deepcopy(binding), copy.deepcopy(plan)
                    if side == 'prior':
                        before['active_release']['inventory_id'] = old
                        changed['expected_binding_ref']['sha256'] = sha(canonical(before))
                    else: changed['candidate_release']['inventory_id'] = old
                    with self.assertRaises(ContractError):
                        product._switch_binding_receipt(changed, before)
        for version in (1, 2, True, 3, 4, 5):
            changed = copy.deepcopy(plan); changed['schema_version'] = version
            with self.assertRaises(ContractError): product._switch_plan_shape(changed, fmt)
        changed = copy.deepcopy(plan)
        changed['remove'] = [{'path': 'hv2', 'sha256': sha(b'x'), 'size_bytes': 1}]
        with self.assertRaises(ContractError): product._switch_plan_shape(changed, fmt)

    def test_windows_rollback_requires_exact_recorded_prior(self):
        fmt, binding, plan = plan_fixture()
        binding['prior_release'] = release('Q')
        plan['expected_binding_ref']['sha256'] = sha(canonical(binding))
        plan['action'] = 'rollback'
        product._switch_plan_shape(plan, fmt)
        new, _ = product._switch_binding_receipt(plan, binding)
        self.assertEqual(binding['prior_release'], new['active_release'])
        plan['candidate_release'] = release('arbitrary retained')
        with self.assertRaises(ContractError): product._switch_binding_receipt(plan, binding)

    def test_detach6_binds_full_layout_and_internal_links(self):
        fmt, binding, plan = plan_fixture()
        inventory_hash = sha(b'exact inventory bytes'); rid = 'product-release-' + inventory_hash[:24]
        prefix = '.hrn/product/releases/' + rid + '/'
        raw = {'colvia': b'launcher', '.hrn/product/init-plan.json': b'init',
               '.hrn/product/binding.json': canonical(binding), '.hrn/product/receipts/init-a.json': b'receipt',
               prefix + 'inventory.json': b'exact inventory bytes'}
        raw.update({prefix + 'payload/' + name: b'launcher' if name == 'colvia' else name.encode() for name in MANAGED})
        plan.update(action='detach', schema_version=6, operation_id='detach-a', candidate_release=None)
        plan['remove'] = [{'path': name, 'sha256': sha(data), 'size_bytes': len(data)} for name, data in sorted(raw.items())]
        preserved = {'.hrn/format.json': canonical(fmt), '.hrn/.gitignore': b'staging/\nlocks/\n'}
        plan['preserve'] = [{'path': name, 'sha256': sha(data), 'size_bytes': len(data)} for name, data in sorted(preserved.items())]
        product._detach_plan_shape(plan, fmt)
        self.assertEqual(6, product._detach_receipt(plan)['schema_version'])
        self.assertEqual(30, len(MANAGED))
        for corruption in ('member', 'binding', 'launcher', 'inventory', 'old-payload', 'boolean', 'unknown'):
            changed = copy.deepcopy(plan)
            if corruption == 'member': changed['remove'].pop(2)
            elif corruption == 'binding':
                next(e for e in changed['remove'] if e['path'] == '.hrn/product/binding.json')['sha256'] = sha(b'wrong')
            elif corruption == 'launcher':
                next(e for e in changed['remove'] if e['path'] == 'colvia')['size_bytes'] += 1
            elif corruption == 'inventory':
                next(e for e in changed['remove'] if e['path'] == prefix + 'inventory.json')['sha256'] = sha(b'wrong')
            elif corruption == 'old-payload':
                next(e for e in changed['remove'] if e['path'] == prefix + 'payload/colvia')['path'] = prefix + 'payload/hv2'
                changed['remove'].sort(key=lambda e: e['path'].encode())
            else: changed['schema_version'] = True if corruption == 'boolean' else 7
            with self.subTest(corruption=corruption), self.assertRaises(ContractError):
                product._detach_plan_shape(changed, fmt)


# Independent original literal; never derive history from the new window.
HISTORICAL_ENTRY_MANAGED = tuple(sorted((
    '.gitignore', 'AGENTS.md', 'CLAUDE.md', 'PRODUCT-CAPABILITIES.json', 'README.md',
    'adapters/colvia-work/SKILL.md', 'colvia', 'docs/CONCEPTS.md', 'docs/GENERAL-WORK.md',
    'docs/GETTING-STARTED.md', 'docs/GUIDED-INTENT-FORMATION.md', 'docs/MAINTAINING.md',
    'docs/MANUAL-OPERATION.md', 'docs/OPERATIONS.md', 'docs/README.md', 'docs/REFERENCE.md',
    'docs/SECURITY-AND-SUPPORT.md', 'docs/WORKSPACE-CONTRACT.md',
    'src/hv2ref/__init__.py', 'src/hv2ref/candidates.py', 'src/hv2ref/cli.py',
    'src/hv2ref/errors.py', 'src/hv2ref/intent.py', 'src/hv2ref/jsonio.py',
    'src/hv2ref/product.py', 'src/hv2ref/umbrella.py', 'src/hv2ref/view.py',
    'src/hv2ref/work.py', 'src/hv2ref/workspace.py',
), key=lambda value: value.encode()))

def historical_detach_fixture(target, version, *, detached=True, retained_checkout=False, window=None, launcher_bytes=None):
    """Independent literal records; no current/old product writer creates these bytes.

    Versions 1/2 use planning-1/checkout-1 examples with the retired hv2 entry,
    not a unique schema-to-window mapping. The retained checkout-1 reader
    accepts both paired versions with the same legacy membership contract.
    Version 3 uses entry-1; 4/5 retain delegation/continuation memberships.
    Version 6 and explicit Windows witnesses exercise portable pair refusal.
    Synthetic payloads are never executed and do not qualify native Windows.
    """
    if version not in (1, 2, 3, 4, 5, 6) or list(target.iterdir()):
        raise ValueError('empty target and known literal pair required')
    window = window or {1: 'planning-1', 2: 'checkout-1', 3: 'entry-1', 4: 'delegation-1', 5: 'continuation-1', 6: 'windows-2'}[version]
    launcher = 'colvia' if version >= 3 else 'hv2'
    names = (MANAGED if version >= 5 else HISTORICAL_ENTRY_MANAGED) if version >= 3 else tuple(sorted(
        ('hv2' if n == 'colvia' else 'adapters/harness-v2-work/SKILL.md'
         if n == 'adapters/colvia-work/SKILL.md' else n for n in HISTORICAL_ENTRY_MANAGED), key=lambda n: n.encode()))
    if version < 3 and sha(('\n'.join(names) + '\n').encode()) != '55662c7bdf478101b4e06d5af824e307eb1eb1ad543946c5df1c5f37507aa780':
        raise ValueError('historical literal membership drift')
    payload = {name: ('synthetic historical ' + window + ': ' + name + '\n').encode() for name in names}
    payload[launcher] = ('WORKSPACE_INVENTORY_ID = ' + repr(window) + '\n').encode()
    if launcher_bytes is not None: payload[launcher] = launcher_bytes
    inventory = {'record_type': 'release-inventory', 'schema_version': 1, 'inventory_id': window,
                 'entries': [{'path': n, 'sha256': sha(payload[n]), 'size_bytes': len(payload[n])} for n in names]}
    digest = sha(canonical(inventory)); ref = {'id': 'product-release-' + digest[:24], 'sha256': digest, 'inventory_id': window}
    fmt = {'record_type': 'workspace-format', 'format_version': 1, 'authority_home_id': 'historical-home', 'created_at': TIME, 'lineage': None}
    init_version = 6 if window == 'windows-2' else 5 if window == 'continuation-1' else 4 if window == 'delegation-1' else 1
    init = {'record_type': 'lifecycle-plan', 'schema_version': init_version, 'operation_id': 'historical-init', 'action': 'init',
            'authority_home_id': fmt['authority_home_id'], 'expected_binding_ref': None, 'candidate_release': ref,
            'format_sha256': sha(canonical(fmt)), 'truth_refs': [], 'remove': [], 'preserve': [],
            'created_at': TIME, 'target_fingerprint': sha(os.fsencode(target.resolve()))}
    binding = {'record_type': 'product-binding', 'schema_version': 1, 'authority_home_id': fmt['authority_home_id'],
               'operation_id': init['operation_id'], 'active_release': ref, 'prior_release': None}
    binding_ref = {'id': binding['operation_id'], 'sha256': sha(canonical(binding))}
    receipt = {'record_type': 'lifecycle-receipt', 'schema_version': init_version, 'operation_id': init['operation_id'],
               'plan': init, 'prior_binding_ref': None, 'result_binding_ref': binding_ref}
    prefix = '.hrn/product/releases/' + ref['id'] + '/'
    data = {launcher: payload[launcher], '.hrn/format.json': canonical(fmt), '.hrn/.gitignore': b'staging/\nlocks/\n',
            '.hrn/product/init-plan.json': canonical(init), '.hrn/product/binding.json': canonical(binding),
            '.hrn/product/receipts/historical-init.json': canonical(receipt), prefix + 'inventory.json': canonical(inventory)}
    data.update({prefix + 'payload/' + n: payload[n] for n in names})
    if retained_checkout:
        old_names = tuple(sorted(('hv2' if n == 'colvia' else 'adapters/harness-v2-work/SKILL.md'
                                 if n == 'adapters/colvia-work/SKILL.md' else n for n in HISTORICAL_ENTRY_MANAGED), key=lambda n: n.encode()))
        old_payload = {n: ('synthetic retained checkout-1: ' + n + '\n').encode() for n in old_names}
        old_payload['hv2'] = b"WORKSPACE_INVENTORY_ID = 'checkout-1'\n"
        old_inventory = {'record_type': 'release-inventory', 'schema_version': 1, 'inventory_id': 'checkout-1',
                         'entries': [{'path': n, 'sha256': sha(old_payload[n]), 'size_bytes': len(old_payload[n])} for n in old_names]}
        old_raw = canonical(old_inventory); old_prefix = '.hrn/product/releases/product-release-' + sha(old_raw)[:24] + '/'
        data[old_prefix + 'inventory.json'] = old_raw
        data.update({old_prefix + 'payload/' + n: old_payload[n] for n in old_names})
    preserved = {'.hrn/format.json', '.hrn/.gitignore'}
    def entries(selected):
        return [{'path': n, 'sha256': sha(data[n]), 'size_bytes': len(data[n])} for n in sorted(selected, key=lambda n: n.encode())]
    plan = {'record_type': 'lifecycle-plan', 'schema_version': version, 'operation_id': 'historical-detach', 'action': 'detach',
            'authority_home_id': fmt['authority_home_id'], 'expected_binding_ref': binding_ref, 'candidate_release': None,
            'format_sha256': sha(canonical(fmt)), 'truth_refs': [], 'remove': entries(set(data) - preserved),
            'preserve': entries(preserved), 'created_at': TIME, 'target_fingerprint': init['target_fingerprint']}
    receipt = {'record_type': 'lifecycle-receipt', 'schema_version': version, 'operation_id': plan['operation_id'],
               'plan': plan, 'prior_binding_ref': binding_ref, 'result_binding_ref': None}
    for name, raw in data.items():
        path = target / name; path.parent.mkdir(parents=True, exist_ok=True); path.write_bytes(raw)
        if sys.platform != 'win32': path.chmod(0o755 if name == launcher or name.endswith('/payload/' + launcher) else 0o644)
    for name in ('intents', 'work', 'staging', 'locks'): (target / '.hrn' / name).mkdir()
    if detached: (target / '.hrn/detached.json').write_bytes(canonical(receipt))
    order = [launcher] + [e['path'] for e in plan['remove'] if e['path'] != launcher]
    dirs = sorted({p.as_posix() for name in order if name != launcher for p in Path(name).parents
                   if p.as_posix().startswith('.hrn/product')}, key=lambda n: (-len(n.split('/')), n.encode()))
    return {'plan': plan, 'receipt': receipt, 'inventory': inventory, 'binding': binding, 'data': data,
            'remove_order': order, 'directory_order': dirs, 'inventory_path': prefix + 'inventory.json'}


class HistoricalDetachTests(unittest.TestCase):
    """Portable literal compatibility and actual native readers, identified separately."""
    def setUp(self):
        import tempfile
        self.root = Path(tempfile.mkdtemp(prefix='h-', dir=os.environ['COLVIA_NATIVE_TEST_ROOT'] if sys.platform == 'win32' else None))
        self.sentinel = self.root / 'outside-sentinel'; self.sentinel.write_bytes(b'historical-sentinel\n')

    def tearDown(self):
        self.assertEqual(b'historical-sentinel\n', self.sentinel.read_bytes())
        print('HISTORICAL_FIXTURE ' + json.dumps({'test': self.id(), 'fixture_directory': self.root.name, 'platform': sys.platform,
              'provenance': 'independent literal records; no historical writer executed'}), flush=True)

    def fixture(self, version):
        target = self.root / str(version); target.mkdir()
        return target, historical_detach_fixture(target, version)

    def audit(self, target, code):
        result = subprocess.run([sys.executable, '-I', '-B', str(SOURCE / 'tests/fixtures/product_plain_auditor.py'), str(target)],
                                capture_output=True, timeout=60)
        self.assertEqual(code, result.returncode, result.stdout + result.stderr)
        self.assertEqual(b'', result.stderr)
        return json.loads(result.stdout)

    def test_historical_123_readers_preserve_original_bytes_at_bound_prefixes(self):
        for version in (1, 2, 3):
            target, fixture = self.fixture(version); raw = canonical(fixture['receipt']); order = fixture['remove_order']
            inventory_index = order.index(fixture['inventory_path']) + 1
            removed = 0
            for label, count in (('marker-before-removal', 0), ('inventory-removed', inventory_index), ('complete', len(order))):
                with self.subTest(version=version, prefix=label):
                    for name in order[removed:count]: (target / name).unlink()
                    removed = count
                    if label == 'complete':
                        for name in fixture['directory_order']: (target / name).rmdir()
                    before = physical(target); expected = 'detached' if label == 'complete' else 'partial'
                    observed = product.workspace_detached_status(target)
                    self.assertEqual(expected, observed['classification']); self.assertEqual(fixture['receipt'], observed['receipt'])
                    self.assertEqual(order[count:], observed['remaining_files'])
                    self.assertEqual(expected, self.audit(target, 0 if expected == 'detached' else 14)['classification'])
                    if version < 3 or sys.platform == 'win32':
                        for recover in (False, True):
                            reason = 'legacy detach writes require retained old source'
                            code = 'HV2-WORKSPACE-PRODUCT'
                            with self.assertRaisesRegex(ContractError, reason) as caught:
                                product.workspace_detach_apply(target, fixture['plan'], confirm_token=sha(canonical(fixture['plan']))[:16], recover=recover)
                            self.assertEqual(code, caught.exception.code)
                    self.assertEqual(before, physical(target)); self.assertEqual(raw, (target / '.hrn/detached.json').read_bytes())
                    print('HISTORICAL_PREFIX ' + json.dumps({'version': version, 'prefix': label, 'classification': expected,
                          'reader_unchanged': True, 'old_writer_executed': False}), flush=True)

    def test_historical_123_relabel_corruption_and_nonprefix_refuse_without_mutation(self):
        for version in (1, 2, 3):
            target, fixture = self.fixture(version); path = target / '.hrn/detached.json'; raw = path.read_bytes()
            before = physical(target)
            self.assertEqual('partial', product.workspace_detached_status(target)['classification'])
            self.assertEqual('partial', self.audit(target, 14)['classification']); self.assertEqual(before, physical(target))
            variants = []
            mixed = copy.deepcopy(fixture['receipt']); mixed['schema_version'] = 4
            variants.append((mixed, 'detach receipt does not bind plan'))
            relabel = copy.deepcopy(fixture['receipt']); relabel['schema_version'] = relabel['plan']['schema_version'] = 4
            if version < 3: variants.append((relabel, 'detach removal outside managed product'))
            digest = copy.deepcopy(fixture['receipt']); digest['plan']['remove'][0]['sha256'] = '0' * 64
            variants.append((digest, 'detach incomplete removal/binding set'))
            for index, (value, reason) in enumerate(variants):
                with self.subTest(version=version, corruption=index):
                    path.write_bytes(canonical(value)); before = physical(target)
                    with self.assertRaisesRegex(ContractError, reason) as caught: product.workspace_detached_status(target)
                    self.assertEqual('HV2-WORKSPACE-PRODUCT', caught.exception.code)
                    self.assertEqual('degraded', self.audit(target, 10)['classification']); self.assertEqual(before, physical(target))
            path.write_bytes(raw); (target / fixture['remove_order'][2]).unlink(); before = physical(target)
            with self.assertRaisesRegex(ContractError, 'not an exact detach file-removal prefix'): product.workspace_detached_status(target)
            self.assertEqual('degraded', self.audit(target, 10)['classification']); self.assertEqual(before, physical(target))

    def test_legacy_paired_12_relabel_retains_read_contract_without_writer_authority(self):
        # Retained checkout-1 contract: root/schema/window versions are independent;
        # readers accept paired 1/2 with the same exact legacy memberships. Current
        # source cannot recover either pair, regardless of this readable relabel.
        for original, changed in ((1, 2), (2, 1)):
            target, fixture = self.fixture(original); path = target / '.hrn/detached.json'
            self.assertEqual('partial', product.workspace_detached_status(target)['classification'])
            self.assertEqual('partial', self.audit(target, 14)['classification'])
            receipt = copy.deepcopy(fixture['receipt']); receipt['schema_version'] = receipt['plan']['schema_version'] = changed
            raw = canonical(receipt); path.write_bytes(raw); order = fixture['remove_order']; removed = 0
            for count in (0, order.index(fixture['inventory_path']) + 1, len(order)):
                for member in order[removed:count]: (target / member).unlink()
                removed = count
                if count == len(order):
                    for directory in fixture['directory_order']: (target / directory).rmdir()
                before = physical(target); expected = 'detached' if count == len(order) else 'partial'
                result = product.workspace_detached_status(target)
                self.assertEqual(expected, result['classification']); self.assertEqual(receipt, result['receipt'])
                self.assertEqual(expected, self.audit(target, 0 if expected == 'detached' else 14)['classification'])
                with self.assertRaisesRegex(ContractError, 'legacy detach writes require retained old source'):
                    product.workspace_detach_apply(target, receipt['plan'], confirm_token=sha(canonical(receipt['plan']))[:16], recover=True)
                self.assertEqual(before, physical(target)); self.assertEqual(raw, path.read_bytes())

    def test_historical_45_mixed_checkout_prefixes_and_exact_recovery(self):
        # Canonical literal reader/recovery contract; no historical writer ran.
        for version in (4, 5):
            for prefix in ('marker', 'launcher-removed', 'inventory-removed', 'files-removed'):
                target = self.root / (str(version) + '-' + prefix); target.mkdir()
                fixture = historical_detach_fixture(target, version, retained_checkout=True)
                order = fixture['remove_order']
                count = {'marker': 0, 'launcher-removed': 1,
                         'inventory-removed': order.index(fixture['inventory_path']) + 1,
                         'files-removed': len(order)}[prefix]
                for member in order[:count]: (target / member).unlink()
                before = physical(target); raw = canonical(fixture['receipt'])
                self.assertEqual('partial', product.workspace_detached_status(target)['classification'])
                self.assertEqual('partial', self.audit(target, 14)['classification'])
                self.assertEqual(before, physical(target)); self.assertEqual(raw, (target / '.hrn/detached.json').read_bytes())
                if version == 5 and sys.platform != 'win32':
                    result = product.workspace_detach_apply(target, fixture['plan'], confirm_token=sha(canonical(fixture['plan']))[:16], recover=True)
                    self.assertEqual('detached', result['classification'])
                    self.assertEqual('detached', self.audit(target, 0)['classification'])
                    self.assertEqual(raw, (target / '.hrn/detached.json').read_bytes())
                    for member in fixture['plan']['preserve']:
                        self.assertEqual(member['sha256'], sha((target / member['path']).read_bytes()))
                elif version == 4:
                    with self.assertRaisesRegex(ContractError, 'legacy detach writes require retained old source'):
                        product.workspace_detach_apply(target, fixture['plan'], confirm_token=sha(canonical(fixture['plan']))[:16], recover=True)
                    self.assertEqual(before, physical(target))

    def test_historical_34_paired_relabel_keeps_original_reader_scope(self):
        for original, changed in ((3, 4), (4, 3)):
            target, fixture = self.fixture(original)
            receipt = copy.deepcopy(fixture['receipt']); receipt['schema_version'] = receipt['plan']['schema_version'] = changed
            (target / '.hrn/detached.json').write_bytes(canonical(receipt)); before = physical(target)
            self.assertEqual('partial', product.workspace_detached_status(target)['classification'])
            self.assertEqual('partial', self.audit(target, 14)['classification'])
            with self.assertRaisesRegex(ContractError, 'legacy detach writes require retained old source'):
                product.workspace_detach_apply(target, receipt['plan'], confirm_token=sha(canonical(receipt['plan']))[:16], recover=True)
            self.assertEqual(before, physical(target))

    def test_windows_witnesses_refuse_legacy_pair_without_restricting_old_history(self):
        for version, window in ((4, 'windows-1'), (5, 'windows-2')):
            target = self.root / window; target.mkdir()
            fixture = historical_detach_fixture(target, version, window=window)
            for removed_launcher in (False, True):
                if removed_launcher: (target / 'colvia').unlink()
                before = physical(target)
                with self.assertRaisesRegex(ContractError, 'detach pair conflicts with remaining Windows window'):
                    product.workspace_detached_status(target)
                self.assertEqual('degraded', self.audit(target, 10)['classification'])
                self.assertEqual(before, physical(target))

    def test_literal_schema6_to5_relabel_refuses_each_remaining_witness(self):
        target, fixture = self.fixture(6); receipt = target / '.hrn/detached.json'
        original = canonical(fixture['receipt']); changed = copy.deepcopy(fixture['receipt'])
        changed['schema_version'] = changed['plan']['schema_version'] = 5
        order = fixture['remove_order']; removed = 0
        witness_ends = [order.index(n) + 1 for n in order if n == '.hrn/product/binding.json' or n.endswith('/inventory.json') or n.endswith('/payload/colvia')]
        for count in sorted({0, 1, *witness_ends}):
            for member in order[removed:count]: (target / member).unlink()
            removed = count; receipt.write_bytes(original); before = physical(target)
            self.assertEqual('partial', product.workspace_detached_status(target)['classification'])
            self.assertEqual('partial', self.audit(target, 14)['classification']); self.assertEqual(before, physical(target))
            witness = any(n == 'colvia' or n == '.hrn/product/binding.json' or n.endswith('/inventory.json') or n.endswith('/payload/colvia') for n in order[count:])
            if witness:
                receipt.write_bytes(canonical(changed)); before = physical(target)
                with self.assertRaisesRegex(ContractError, 'detach pair conflicts with remaining Windows window'):
                    product.workspace_detached_status(target)
                self.assertEqual('degraded', self.audit(target, 10)['classification']); self.assertEqual(before, physical(target))

    def test_legacy_launcher_witness_scan_bounds_optional_parsing(self):
        import ast
        import runpy
        oversized = b"WORKSPACE_INVENTORY_ID = 'entry-1'\n#" + b'x' * (1024 * 1024) + b'\n'
        target = self.root / 'large'; target.mkdir()
        historical_detach_fixture(target, 3, launcher_bytes=oversized)
        before = physical(target)
        parse = ast.parse
        def bounded(data, *args, **kwargs):
            if len(data) > 1024 * 1024: raise AssertionError('oversized legacy launcher parsed')
            return parse(data, *args, **kwargs)
        with mock.patch.object(ast, 'parse', side_effect=bounded):
            self.assertEqual('partial', product.workspace_detached_status(target)['classification'])
        self.assertEqual('partial', self.audit(target, 14)['classification']); self.assertEqual(before, physical(target))
        independent = runpy.run_path(str(SOURCE / 'tests/fixtures/product_plain_auditor.py'))['remaining_window']
        with mock.patch.object(ast, 'parse', side_effect=AssertionError('oversized launcher parsed')):
            product._detach_remaining_window({'schema_version': 5}, {'colvia': oversized})
            independent(5, {}, {'colvia': oversized})
        with mock.patch.object(ast, 'parse', side_effect=MemoryError('synthetic parser resource limit')):
            product._detach_remaining_window({'schema_version': 5}, {'colvia': b'opaque old launcher'})
            independent(5, {}, {'colvia': b'opaque old launcher'})

    def test_literal_historical_release_bytes_are_valid_without_execution(self):
        for version in (1, 2, 3):
            target = self.root / str(version); target.mkdir(); fixture = historical_detach_fixture(target, version, detached=False)
            before = physical(target); expected = fixture['binding']['active_release']
            result = product.verify_workspace_release(target / '.hrn/product/releases' / expected['id'])
            self.assertEqual(expected, result['release_ref']); self.assertEqual(fixture['inventory'], result['inventory'])
            if sys.platform != 'win32':
                self.assertEqual(fixture['inventory'], product.verify_workspace_product(target)['inventory'])
            else:
                reason = 'historical ' + expected['inventory_id'] + ' executable-bit observation is unavailable on native Windows'
                with self.assertRaisesRegex(ContractError, reason) as caught: product.verify_workspace_product(target)
                self.assertEqual('HV2-WORKSPACE-PRODUCT', caught.exception.code)
            self.assertEqual(before, physical(target))


class NativeLifecycleFixture:
    @classmethod
    def setUpClass(cls):
        root = Path(os.environ['COLVIA_NATIVE_TEST_ROOT']) / hashlib.sha256(cls.__name__.encode()).hexdigest()[:4]
        root.mkdir(parents=True, exist_ok=False); cls.suite_root = root
        cls.p = root / 'P'; cls.q = root / 'Q'; common_q = root / 'common-Q'; common_q.mkdir()
        for name in MANAGED:
            path = common_q / name; path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes((SOURCE / name).read_bytes())
        with (common_q / 'README.md').open('ab') as stream: stream.write(b'\nSynthetic same-window compatibility fixture Q.\n')
        with (common_q / 'colvia').open('ab') as stream: stream.write(b'\n# Synthetic same-window compatibility fixture Q.\n')
        for source, output in ((SOURCE, cls.p), (common_q, cls.q)):
            started = time.monotonic()
            print('NATIVE_SETUP_START ' + json.dumps({'class': cls.__name__, 'stage': 'prepare', 'candidate': output.name, 'limit_seconds': 45}), flush=True)
            try:
                result = subprocess.run([sys.executable, '-I', '-B', str(SOURCE / 'scripts/prepare-windows.py'),
                                         '--source', str(source), '--output', str(output)], capture_output=True, timeout=45)
            finally:
                print('NATIVE_SETUP_TIMING ' + json.dumps({'class': cls.__name__, 'stage': 'prepare', 'candidate': output.name,
                      'elapsed_seconds': time.monotonic() - started}), flush=True)
            if result.returncode: raise RuntimeError((result.stdout + result.stderr).decode(errors='replace'))
        started = time.monotonic()
        print('NATIVE_SETUP_START ' + json.dumps({'class': cls.__name__, 'stage': 'verify-PQ'}), flush=True)
        cls.p_candidate = product.workspace_candidate(cls.p); cls.q_candidate = product.workspace_candidate(cls.q)
        print('NATIVE_SETUP_TIMING ' + json.dumps({'class': cls.__name__, 'stage': 'verify-PQ', 'elapsed_seconds': time.monotonic() - started}), flush=True)
        if cls.p_candidate['release_ref'] == cls.q_candidate['release_ref']: raise AssertionError('P/Q must differ')
        for output in (cls.p, cls.q):
            report = json.loads((output / 'preparation.json').read_bytes())
            if report['output_release']['inventory_id'] != 'windows-2': raise AssertionError('prepared identity')
        print('NATIVE_PQ ' + json.dumps({'class': cls.__name__, 'P': cls.p_candidate['release_ref'],
              'Q': cls.q_candidate['release_ref']}), flush=True)

    def setUp(self):
        self.root = self.suite_root / hashlib.sha256(self._testMethodName.encode()).hexdigest()[:8]; self.root.mkdir()
        self.target = self.root / 'project'; self.target.mkdir()
        self.sentinel = self.root / 'outside-sentinel'; self.sentinel.write_bytes(b'untouched synthetic sentinel\n')
        self.secret = self.root / 'synthetic-secret'; self.secret.write_bytes(b'DISPOSABLE_SECRET_SENTINEL\n')
        (self.target / 'sample.txt').write_bytes(b'before\r\n')

    def tearDown(self):
        self.assertEqual(b'untouched synthetic sentinel\n', self.sentinel.read_bytes())
        self.assertEqual(b'DISPOSABLE_SECRET_SENTINEL\n', self.secret.read_bytes())
        print('NATIVE_FIXTURE ' + json.dumps({'test': self.id(), 'root': str(self.root)}), flush=True)

    def init(self, target=None, point=None):
        target = target or self.target
        preview = product.workspace_init_preview(self.p, target, authority_home_id='home-a', operation_id='init-a', created_at=TIME)
        try:
            result = product.workspace_init_apply(self.p, target, preview['request'], confirm_token=preview['confirm_token'], inject_at=point)
        except InjectedCrash:
            if point is None: raise
            result = None
        return preview, result

    def assert_product(self, expected):
        root = self.target / '.hrn/product'; binding = json.loads((root / 'binding.json').read_bytes())
        self.assertEqual(expected['release_ref'], binding['active_release'])
        release_path = root / 'releases' / binding['active_release']['id']
        data = (release_path / 'inventory.json').read_bytes(); inventory = json.loads(data)
        self.assertEqual(binding['active_release']['sha256'], sha(data))
        self.assertEqual(MANAGED, tuple(e['path'] for e in inventory['entries']))
        for entry in inventory['entries']:
            actual = (release_path / 'payload' / entry['path']).read_bytes()
            self.assertEqual((entry['sha256'], entry['size_bytes']), (sha(actual), len(actual)))
            self.assertEqual(expected['payload'][entry['path']], actual)
        self.assertEqual(expected['payload']['colvia'], (self.target / 'colvia').read_bytes())
        self.assertEqual(b'before\r\n', (self.target / 'sample.txt').read_bytes())


    def assert_old_writers_refuse(self, target, state):
        rows = json.loads(Path(os.environ['COLVIA_TEST_OLD_WRITERS']).read_bytes())
        self.assertEqual({'first-b1', 'checkout-1', 'retained-L', 'retained-P'}, {r['label'] for r in rows})
        families = {'local': 'work', 'worker': 'work', 'parent': 'umbrella', 'intent': 'intent',
                    'planning': 'candidates', 'lifecycle': 'product'}
        for row in rows:
            old = Path(row['root']); self.assertEqual(set(row['files']), {p.relative_to(old).as_posix() for p in old.rglob('*') if p.is_file()})
            for name, digest in row['files'].items(): self.assertEqual(digest, sha((old / name).read_bytes()))
            before = physical(target)
            for family, module in families.items():
                # intent is import-safe; its actual writer constructor imports
                # WorkStore lazily. The other frozen writer modules import the
                # unavailable native dependency before any entry can dispatch.
                program = ("import sys;from pathlib import Path;sys.path.insert(0,sys.argv[1]);"
                           "module=__import__('hv2ref.'+sys.argv[2],fromlist=['*'])\n"
                           "if sys.argv[2]=='intent': module.WorkspaceIntentStore(Path(sys.argv[3]))\n"
                           "raise RuntimeError('old writer entry unexpectedly became available')")
                command = [sys.executable, '-I', '-B', '-c', program, str(old / 'src'), module, str(target), family]
                access = 'exact-source-or-retained-constructor' if family == 'intent' else 'exact-source-or-retained-module'
                attempt = {'writer': row['label'], 'family': family, 'access': access, 'state': state, 'argv': command}
                print('OLD_WRITER_NATIVE_ATTEMPT ' + json.dumps(attempt), flush=True)
                result = subprocess.run(command, cwd=target, capture_output=True, timeout=15)
                self.assertEqual(before, physical(target), attempt)
                self.assertNotEqual(0, result.returncode, attempt)
                self.assertIn(b"ModuleNotFoundError: No module named 'fcntl'", result.stderr, attempt)
                self.assertIn(str(old / 'src/hv2ref/jsonio.py').encode(), result.stderr, attempt)
                print('OLD_WRITER_NATIVE_REFUSAL ' + json.dumps({**attempt,
                      'exit': result.returncode, 'reason': 'native fcntl dependency unavailable before writer entry',
                      'target_unchanged': True}), flush=True)
            launcher = old / ('hv2' if row['label'] == 'checkout-1' else 'colvia')
            # Execute the exact historical launcher in explicit source mode;
            # its actual native import failure precedes command dispatch.
            command = [sys.executable, '-I', '-B', str(launcher), '--source-checkout', 'init', '--target', str(target)]
            result = subprocess.run(command, cwd=target, capture_output=True, timeout=15)
            self.assertNotEqual(0, result.returncode)
            self.assertIn(b"No module named 'fcntl'", result.stderr)
            self.assertEqual(before, physical(target))
            print('OLD_LAUNCHER_NATIVE_REFUSAL ' + json.dumps({'writer': row['label'], 'state': state,
                  'argv': command, 'exit': result.returncode, 'target_unchanged': True}), flush=True)


@unittest.skipUnless(sys.platform == 'win32', 'native Windows lifecycle; excluded from POSIX execution matrix')
class WindowsEarlyAdmissionTests(NativeLifecycleFixture, unittest.TestCase):
    def test_fresh_and_incomplete_init_reject_each_exposed_old_writer(self):
        prefix = self.root / 'incomplete'; prefix.mkdir(); self.init(prefix, 'after-plan')
        self.init(); self.assert_product(self.p_candidate)
        self.assert_old_writers_refuse(prefix, 'init-incomplete')
        self.assert_old_writers_refuse(self.target, 'init-complete')
        # The installed tree contains only the fixed prepared P payload. This
        # does not claim that every interpreter elsewhere in the VM is absent.
        self.assert_product(self.p_candidate)


@unittest.skipUnless(sys.platform == 'win32', 'native predecessor runtime gate; not all writer-family qualification')
class WindowsIntegrationPredecessorTests(NativeLifecycleFixture, unittest.TestCase):
    def test_additional_predecessor_guards_refuse_exact_schema6_prefixes(self):
        rows = json.loads(Path(os.environ['COLVIA_TEST_INTEGRATION_OLD_WRITERS']).read_bytes())
        self.assertEqual({'delegation-main', 'continuation-main', 'windows-1-original'}, {row['label'] for row in rows})
        program = """import sys,json
from pathlib import Path
sys.path.insert(0,sys.argv[1])
try:
 from hv2ref.workspace import writer_guard
 from hv2ref.errors import ContractError
 with writer_guard(Path(sys.argv[2])):
  raise RuntimeError('predecessor guard admitted new schema')
except ModuleNotFoundError as exc:
 if exc.name != 'fcntl': raise
 print(json.dumps({'refused':True,'kind':'unavailable-native-dependency','name':exc.name}))
except ContractError as exc:
 print(json.dumps({'refused':True,'kind':'contract-gate','code':exc.code,'message':exc.message}))
"""
        for state in ('init-incomplete', 'switch-receipt', 'detach-receipt', 'detach-complete'):
            self.target = self.root / state; self.target.mkdir()
            self.init(point='after-plan' if state == 'init-incomplete' else None)
            if state == 'switch-receipt':
                preview = product.workspace_switch_preview(self.target, action='update', source=self.q, operation_id='switch-old-gate', created_at=TIME)
                with self.assertRaises(InjectedCrash):
                    product.workspace_switch_apply(self.target, preview['request'], source=self.q, confirm_token=preview['confirm_token'], inject_at='after-receipt')
            if state.startswith('detach-'):
                preview = product.workspace_detach_preview(self.target, operation_id='detach-old-gate', created_at=TIME)
                if state == 'detach-receipt':
                    with self.assertRaises(InjectedCrash):
                        product.workspace_detach_apply(self.target, preview['request'], confirm_token=preview['confirm_token'], inject_at='after-receipt')
                else:
                    product.workspace_detach_apply(self.target, preview['request'], confirm_token=preview['confirm_token'])
            before = physical(self.target)
            for row in rows:
                old = Path(row['root'])
                self.assertEqual(set(row['files']), {p.relative_to(old).as_posix() for p in old.rglob('*') if p.is_file()})
                for name, digest in row['files'].items(): self.assertEqual(digest, sha((old / name).read_bytes()))
                result = subprocess.run([sys.executable, '-I', '-B', '-c', program, str(old / 'src'), str(self.target)],
                                        capture_output=True, cwd=self.target, timeout=30)
                self.assertEqual(0, result.returncode, result.stdout + result.stderr)
                observed = json.loads(result.stdout); self.assertTrue(observed['refused'])
                if row['label'] == 'windows-1-original':
                    self.assertEqual('contract-gate', observed['kind'])
                    # Exact pinned predecessor: both gates precede lock/scratch creation.
                    code, message = (('HV2-WORKSPACE-RUNTIME', 'native Windows mutation requires a verified windows-1 window')
                                     if state == 'detach-complete' else
                                     ('HV2-WORKSPACE-CONTRACT', 'not a supported init plan'))
                    self.assertEqual(code, observed['code']); self.assertIn(message, observed['message'])
                else:
                    self.assertEqual('unavailable-native-dependency', observed['kind'])
                self.assertEqual(before, physical(self.target))
                scope = ('module import / dependency only' if observed['kind'] == 'unavailable-native-dependency'
                         else 'actual common guard, not every writer apply family')
                print('NATIVE_PREDECESSOR_GUARD ' + json.dumps({'writer':row['label'], 'state':state, 'observation':observed,
                      'scope':scope, 'target_unchanged':True}), flush=True)


@unittest.skipUnless(sys.platform == 'win32', 'native Windows lifecycle; excluded from POSIX execution matrix')
class WindowsLifecycleTests(NativeLifecycleFixture, unittest.TestCase):

    def test_historical_installed_targets_refuse_current_native_writers_without_publication(self):
        for version in (1, 2, 3):
            target = self.root / ('old-' + str(version)); target.mkdir()
            fixture = historical_detach_fixture(target, version, detached=False)
            release = fixture['binding']['active_release']
            self.assertEqual(release, product.verify_workspace_release(target / '.hrn/product/releases' / release['id'])['release_ref'])
            before = physical(target)
            with self.assertRaises(ContractError) as caught:
                with workspace.writer_guard(target): self.fail('historical native writer guard admitted')
            self.assertEqual('HV2-WORKSPACE-RUNTIME', caught.exception.code)
            self.assertEqual(before, physical(target)); self.assertFalse((target / '.hrn/locks/writer.lock').exists())
            actions = {
                'init': lambda: product.workspace_init_preview(self.p, target, authority_home_id='new-home', operation_id='new-init', created_at=TIME),
                'update': lambda: product.workspace_switch_preview(target, action='update', source=self.p, operation_id='new-update', created_at=TIME),
                'rollback': lambda: product.workspace_switch_preview(target, action='rollback', source=None, operation_id='new-rollback', created_at=TIME),
                'repair': lambda: product.workspace_repair_preview(self.p, target, self.root / ('backup-' + str(version)), operation_id='new-repair', created_at=TIME),
                'detach': lambda: product.workspace_detach_preview(target, operation_id='new-detach', created_at=TIME),
            }
            # Native old-launcher observation refuses before later switch/detach
            # gates. Pin the actual boundary rather than crediting those gates.
            historical_reason = 'historical ' + release['inventory_id'] + ' executable-bit observation is unavailable on native Windows'
            reasons = {'init': 'different initialization plan', 'update': historical_reason,
                       'rollback': historical_reason, 'detach': historical_reason,
                       'repair': 'older-window repair requires the exact retained old source'}
            with self.assertRaisesRegex(ContractError, historical_reason): product.verify_workspace_product(target)
            for action, call in actions.items():
                with self.subTest(version=version, action=action):
                    with self.assertRaisesRegex(ContractError, reasons[action]) as refusal: call()
                    self.assertEqual('HV2-WORKSPACE-PRODUCT', refusal.exception.code)
                    self.assertEqual(before, physical(target))
                    print('NATIVE_HISTORICAL_WRITER_REFUSAL ' + json.dumps({'version': version, 'action': action,
                          'code': refusal.exception.code, 'message': refusal.exception.message, 'target_unchanged': True,
                          'provenance': 'literal valid historical release; no old binary execution or migration'}), flush=True)
            self.assertFalse((self.root / ('backup-' + str(version))).exists())

    def test_current_native_update_refuses_common_source_window_before_receipt(self):
        self.init(); before = physical(self.target)
        self.assertEqual('continuation-1', product.workspace_candidate(SOURCE)['release_ref']['inventory_id'])
        with self.assertRaisesRegex(ContractError, 'cannot cross the Windows boundary'):
            product.workspace_switch_preview(self.target, action='update', source=SOURCE, operation_id='cross-window', created_at=TIME)
        self.assertEqual(before, physical(self.target))
        self.assertFalse((self.target / '.hrn/product/receipts/cross-window.json').exists())

    def test_long_publication_path_refused_before_first_write(self):
        target = self.root / ('x' * 60); target.mkdir()
        (target / 'sample.txt').write_bytes(b'preserve before admission')
        before = physical(target)
        preview = product.workspace_init_preview(self.p, target, authority_home_id='home-a', operation_id='init-long', created_at=TIME)
        with self.assertRaisesRegex(ContractError, '247 UTF-16'):
            product.workspace_init_apply(self.p, target, preview['request'], confirm_token=preview['confirm_token'])
        self.assertEqual(before, physical(target))
        self.assertFalse((target / '.hrn').exists())

    def test_init_owned_prefixes_recover_and_unowned_prefixes_preserve(self):
        points = ('after-root', 'after-product-dir', 'after-plan', 'after-format', 'after-ignore', 'after-intents',
                  'after-work', 'after-staged-inventory', 'after-staged-payload', 'after-release', 'after-receipt',
                  'after-launcher-bytes', 'after-launcher', 'after-binding')
        for point in points:
            with self.subTest(point=point):
                self.target = self.root / hashlib.sha256(point.encode()).hexdigest()[:4]; self.target.mkdir()
                (self.target / 'sample.txt').write_bytes(b'before\r\n')
                preview, _ = self.init(point=point)
                before = physical(self.target)
                if point in ('after-root', 'after-product-dir'):
                    with self.assertRaises(ContractError):
                        product.workspace_init_apply(self.p, self.target, preview['request'], confirm_token=preview['confirm_token'], recover=True)
                    self.assertEqual(before, physical(self.target))
                else:
                    product.workspace_init_apply(self.p, self.target, preview['request'], confirm_token=preview['confirm_token'], recover=True)
                    self.assert_product(self.p_candidate)
                    before = physical(self.target)
                    product.workspace_init_apply(self.p, self.target, preview['request'], confirm_token=preview['confirm_token'], recover=True)
                    self.assertEqual(before, physical(self.target))

    def test_same_window_update_and_rollback_each_prefix(self):
        points = ('after-receipt', 'after-staged-inventory', 'after-staged-payload', 'after-release', 'after-launcher', 'after-binding')
        for point in points:
            with self.subTest(point=point):
                self.target = self.root / hashlib.sha256(point.encode()).hexdigest()[:4]; self.target.mkdir(); (self.target / 'sample.txt').write_bytes(b'before\r\n')
                self.init()
                preview = product.workspace_switch_preview(self.target, action='update', source=self.q, operation_id='update-a', created_at=TIME)
                self.assertEqual(6, preview['request']['schema_version'])
                with self.assertRaises(InjectedCrash):
                    product.workspace_switch_apply(self.target, preview['request'], confirm_token=preview['confirm_token'], source=self.q, inject_at=point)
                self.assert_old_writers_refuse(self.target, 'switch-' + point)
                product.workspace_switch_apply(self.target, preview['request'], confirm_token=preview['confirm_token'], source=self.q, recover=True)
                self.assert_product(self.q_candidate)
                rollback = product.workspace_switch_preview(self.target, action='rollback', source=None, operation_id='rollback-a', created_at=TIME)
                self.assertEqual(self.p_candidate['release_ref'], rollback['request']['candidate_release'])
                product.workspace_switch_apply(self.target, rollback['request'], confirm_token=rollback['confirm_token'])
                self.assert_product(self.p_candidate)

    def test_lifecycle_required_flush_failure_preserves_exact_recovery_prefix(self):
        for action in ('init', 'update', 'repair', 'detach'):
            with self.subTest(action=action):
                self.target = self.root / action; self.target.mkdir()
                (self.target / 'sample.txt').write_bytes(b'before\r\n')
                if action == 'init':
                    preview = product.workspace_init_preview(self.p, self.target, authority_home_id='home-a', operation_id='init-flush', created_at=TIME)
                    failed_file = self.target / '.hrn/product/init-plan.json'
                    invoke = lambda recover: product.workspace_init_apply(self.p, self.target, preview['request'], confirm_token=preview['confirm_token'], recover=recover)
                else:
                    self.init()
                    if action == 'update':
                        preview = product.workspace_switch_preview(self.target, action='update', source=self.q, operation_id='update-flush', created_at=TIME)
                        failed_file = self.target / '.hrn/product/receipts/update-flush.json'
                        invoke = lambda recover: product.workspace_switch_apply(self.target, preview['request'], confirm_token=preview['confirm_token'], source=self.q, recover=recover)
                    elif action == 'repair':
                        (self.target / 'colvia').write_bytes(b'original damaged launcher')
                        backup = self.root / 'flush-backup'
                        preview = product.workspace_repair_preview(self.p, self.target, backup, operation_id='repair-flush', created_at=TIME)
                        failed_file = backup / 'request.json'
                        invoke = lambda recover: product.workspace_repair_apply(self.p, self.target, preview['request'], confirm_token=preview['confirm_token'], recover=recover)
                    else:
                        preview = product.workspace_detach_preview(self.target, operation_id='detach-flush', created_at=TIME)
                        preserved = {entry['path']: (self.target / entry['path']).read_bytes() for entry in preview['request']['preserve']}
                        failed_file = self.target / '.hrn/detached.json'
                        invoke = lambda recover: product.workspace_detach_apply(self.target, preview['request'], confirm_token=preview['confirm_token'], recover=recover)
                original_request = canonical(preview)
                with fail_native_flush_for(failed_file) as failures:
                    with self.assertRaisesRegex(ContractError, 'created-file-content.*winerror=5'):
                        invoke(False)
                self.assertEqual(1, len(failures)); self.assertTrue(failed_file.is_file())
                self.assertEqual(b'before\r\n', (self.target / 'sample.txt').read_bytes())
                prefix = physical(self.target); saved_prefix = failed_file.read_bytes()
                if action == 'repair':
                    self.assertEqual(canonical(preview['request']), saved_prefix)
                    self.assertEqual(b'original damaged launcher', (self.target / 'colvia').read_bytes())
                elif action == 'init':
                    self.assertEqual(preview['request']['plan'], json.loads(saved_prefix))
                    self.assertFalse((self.target / '.hrn/product/binding.json').exists())
                else:
                    self.assertEqual(preview['request'], json.loads(saved_prefix)['plan'])
                next_publication = {'init': self.target / '.hrn/format.json',
                                    'update': self.target / '.hrn/product/binding.json',
                                    'repair': self.root / 'flush-backup/original/colvia',
                                    'detach': self.target / 'colvia'}[action]
                with record_native_publication() as events: invoke(True)
                assert_native_reflush_before(self, events, failed_file, next_publication)
                for destination in {e['path'] for e in events if e['kind'] == 'replace'}:
                    assert_native_staging_flush_before_replace(self, events, destination)
                self.assertEqual(original_request, canonical(preview))
                self.assertEqual(saved_prefix, failed_file.read_bytes())
                if action == 'detach':
                    self.plain_audit('detached')
                    for name, data in preserved.items(): self.assertEqual(data, (self.target / name).read_bytes())
                else:
                    self.assert_product(self.q_candidate if action == 'update' else self.p_candidate)
                if action == 'repair':
                    self.assertEqual(b'original damaged launcher', (backup / 'original/colvia').read_bytes())
                print('NATIVE_LIFECYCLE_FLUSH_PREFIX ' + json.dumps({'action': action, 'phase': 'created-file-content', 'injected_winerror': 5, 'prefix_paths': len(prefix), 'original_request_recovered': True}), flush=True)

    def test_same_launcher_readonly_update_and_completed_replay(self):
        self.init()
        candidate = self.root / 'same-entry'; candidate.mkdir()
        for name in MANAGED:
            path = candidate / name; path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes((self.p / name).read_bytes())
        with (candidate / 'README.md').open('ab') as stream: stream.write(b'\nSynthetic documentation-only update.\n')
        launcher = self.target / 'colvia'; original = launcher.read_bytes()
        self.assertEqual(original, (candidate / 'colvia').read_bytes())
        os.chmod(launcher, stat.S_IREAD)
        preview = product.workspace_switch_preview(self.target, action='update', source=candidate, operation_id='update-same-entry', created_at=TIME)
        original_sync = product.sync_directory; sync_results = []; phase = [None]
        def observe_sync(path):
            result = original_sync(path)
            sync_results.append({'phase': phase[0], 'relative_path': path.relative_to(self.target).as_posix(), 'result': result})
            return result
        for expected in ('updated', 'replayed'):
            phase[0] = expected
            with mock.patch.object(product, 'sync_directory', side_effect=observe_sync):
                result = product.workspace_switch_apply(self.target, preview['request'], source=candidate, confirm_token=preview['confirm_token'])
            self.assertEqual(expected, result['classification'])
            self.assertEqual(original, launcher.read_bytes())
            self.assertTrue(launcher.stat().st_file_attributes & stat.FILE_ATTRIBUTE_READONLY)
        self.assertTrue([r for r in sync_results if r['phase'] == 'updated'])
        self.assertEqual([], [r for r in sync_results if r['phase'] == 'replayed'])
        print('NATIVE_SWITCH_DIRECTORY_SYNC ' + json.dumps({'scope': 'product switch sync_directory calls', 'observations': sync_results}), flush=True)

    def test_switch_readonly_binding_refuses_before_receipt(self):
        self.init()
        preview = product.workspace_switch_preview(self.target, action='update', source=self.q, operation_id='update-a', created_at=TIME)
        binding = self.target / '.hrn/product/binding.json'; os.chmod(binding, stat.S_IREAD)
        before = physical(self.target)
        with self.assertRaises(ContractError) as caught:
            product.workspace_switch_apply(self.target, preview['request'], confirm_token=preview['confirm_token'], source=self.q)
        self.assertEqual('HV2-WINDOWS-READONLY', caught.exception.code)
        self.assertEqual(before, physical(self.target))
        self.assertFalse((self.target / '.hrn/product/receipts/update-a.json').exists())

    def test_repair_exact_attributes_backup_prefix_and_completed_replay(self):
        for point in ('after-backup-request', 'after-backup', 'after-file', 'after-receipt'):
            with self.subTest(point=point):
                self.target = self.root / hashlib.sha256(point.encode()).hexdigest()[:4]; self.target.mkdir(); (self.target / 'sample.txt').write_bytes(b'before\r\n'); self.init()
                (self.target / 'colvia').write_bytes(b'damaged launcher\n')
                member = self.target / '.hrn/product/releases' / self.p_candidate['release_ref']['id'] / 'payload/README.md'
                member.unlink(); backup = self.root / (point + '-backup')
                preview = product.workspace_repair_preview(self.p, self.target, backup, operation_id='repair-a', created_at=TIME)
                self.assertEqual(6, preview['request']['plan']['schema_version'])
                self.assertTrue(all(f['after']['mode'] == 0 and (f['before'] is None or f['before']['mode'] == 0) for f in preview['request']['files']))
                with self.assertRaises(InjectedCrash):
                    product.workspace_repair_apply(self.p, self.target, preview['request'], confirm_token=preview['confirm_token'], inject_at=point)
                product.workspace_repair_apply(self.p, self.target, preview['request'], confirm_token=preview['confirm_token'], recover=True)
                self.assertEqual(b'damaged launcher\n', (backup / 'original/colvia').read_bytes())
                self.assert_product(self.p_candidate)
                before = physical(self.target)
                product.workspace_repair_apply(self.p, self.target, preview['request'], confirm_token=preview['confirm_token'], recover=True)
                self.assertEqual(before, physical(self.target))
                os.chmod(self.target / 'colvia', stat.S_IREAD); before = physical(self.target)
                with self.assertRaises(ContractError):
                    product.workspace_repair_apply(self.p, self.target, preview['request'], confirm_token=preview['confirm_token'], recover=True)
                self.assertEqual(before, physical(self.target))

    def test_repair_readonly_damage_refuses_but_unlisted_readonly_is_preserved(self):
        self.init(); launcher = self.target / 'colvia'; launcher.write_bytes(b'damaged')
        os.chmod(launcher, stat.S_IREAD); before = physical(self.target)
        with self.assertRaises(ContractError) as caught:
            product.workspace_repair_preview(self.p, self.target, self.root / 'blocked-backup', operation_id='repair-a', created_at=TIME)
        self.assertEqual('HV2-WINDOWS-READONLY', caught.exception.code); self.assertEqual(before, physical(self.target))
        self.assertFalse((self.root / 'blocked-backup').exists())
        os.chmod(launcher, stat.S_IWRITE)  # Deliberate external fixture change, never a product recovery step.
        member = self.target / '.hrn/product/releases' / self.p_candidate['release_ref']['id'] / 'payload/README.md'
        os.chmod(member, stat.S_IREAD)
        preview = product.workspace_repair_preview(self.p, self.target, self.root / 'backup', operation_id='repair-b', created_at=TIME)
        self.assertEqual(['colvia'], [f['path'] for f in preview['request']['files']])
        product.workspace_repair_apply(self.p, self.target, preview['request'], confirm_token=preview['confirm_token'])
        self.assertTrue(member.stat().st_file_attributes & 1); self.assert_product(self.p_candidate)

    def test_repair_mode_shapes_and_preview_attribute_drift_preserve_targets(self):
        self.init(); launcher = self.target / 'colvia'; launcher.write_bytes(b'damaged mode fixture')
        member = self.target / '.hrn/product/releases' / self.p_candidate['release_ref']['id'] / 'payload/README.md'
        member.unlink(); backup = self.root / 'mode-backup'
        preview = product.workspace_repair_preview(self.p, self.target, backup, operation_id='repair-mode', created_at=TIME)
        by_path = {f['path']: f for f in preview['request']['files']}
        self.assertEqual(0, by_path['colvia']['before']['mode'])
        self.assertIsNone(by_path[member.relative_to(self.target).as_posix()]['before'])
        self.assertTrue(all(f['after']['mode'] == 0 for f in by_path.values()))
        for side in ('before', 'after'):
            for value in (True, False, -1, 2, '0', None, 1):
                with self.subTest(side=side, mode=value):
                    changed = copy.deepcopy(preview['request'])
                    next(f for f in changed['files'] if f['path'] == 'colvia')[side]['mode'] = value
                    before = physical(self.target)
                    with self.assertRaises(ContractError):
                        product.workspace_repair_apply(self.p, self.target, changed, confirm_token=sha(canonical(changed))[:16])
                    self.assertEqual(before, physical(self.target)); self.assertFalse(backup.exists())
        os.chmod(launcher, stat.S_IREAD)
        self.assertEqual(1, product._repair_file_observation(launcher, 'windows-2')['mode'])
        before = physical(self.target)
        with self.assertRaises(ContractError):
            product.workspace_repair_apply(self.p, self.target, preview['request'], confirm_token=preview['confirm_token'])
        self.assertEqual(before, physical(self.target)); self.assertFalse(backup.exists())
        with self.assertRaisesRegex(ContractError, 'read-only'):
            product.workspace_repair_preview(self.p, self.target, self.root / 'blocked-new', operation_id='repair-new', created_at=TIME)
        self.assertEqual(before, physical(self.target)); self.assertFalse((self.root / 'blocked-new').exists())
        os.chmod(launcher, stat.S_IWRITE)  # Deliberate external fixture correction.
        fresh = product.workspace_repair_preview(self.p, self.target, self.root / 'fresh-backup', operation_id='repair-new', created_at=TIME)
        self.assertNotEqual(preview['confirm_token'], fresh['confirm_token'])
        self.assertNotEqual(preview['request']['backup'], fresh['request']['backup'])
        # Restoring the attribute permits the original exact request, not an edited request.
        product.workspace_repair_apply(self.p, self.target, preview['request'], confirm_token=preview['confirm_token'])
        self.assert_product(self.p_candidate)
        self.assertEqual(b'damaged mode fixture', (backup / 'original/colvia').read_bytes())
        self.assertEqual(canonical(preview['request']), (backup / 'request.json').read_bytes())

    def test_repair_fresh_preview_cannot_bypass_pending_switch(self):
        self.init()
        switch = product.workspace_switch_preview(self.target, action='update', source=self.q, operation_id='pending-update', created_at=TIME)
        with self.assertRaises(InjectedCrash):
            product.workspace_switch_apply(self.target, switch['request'], confirm_token=switch['confirm_token'], source=self.q, inject_at='after-receipt')
        before = physical(self.target)
        backup = self.root / 'fresh-during-pending'
        with self.assertRaises(ContractError):
            product.workspace_repair_preview(self.p, self.target, backup, operation_id='new-repair', created_at=TIME)
        self.assertEqual(before, physical(self.target)); self.assertFalse(backup.exists())
        self.assertEqual('partial', product.workspace_status(self.target)['classification'])
        product.workspace_switch_apply(self.target, switch['request'], confirm_token=switch['confirm_token'], source=self.q, recover=True)
        self.assert_product(self.q_candidate)
        (self.target / 'colvia').write_bytes(b'damaged after exact switch recovery')
        before = physical(self.target)
        fresh = product.workspace_repair_preview(self.q, self.target, backup, operation_id='new-repair', created_at=TIME)
        self.assertEqual('new-repair', fresh['request']['plan']['operation_id'])
        self.assertEqual(str(backup.resolve()), fresh['request']['backup'])
        self.assertEqual(before, physical(self.target)); self.assertFalse(backup.exists())

    def test_repair_backup_required_reflush_readonly_refuses_exact_resume(self):
        for number, name in enumerate(('request.json', 'original/colvia')):
            with self.subTest(backup_file=name):
                self.target = self.root / ('r' + str(number)); self.target.mkdir()
                (self.target / 'sample.txt').write_bytes(b'before\r\n'); self.init()
                (self.target / 'colvia').write_bytes(b'original damaged bytes')
                backup = self.root / ('b' + str(number))
                preview = product.workspace_repair_preview(self.p, self.target, backup, operation_id='repair-backup', created_at=TIME)
                with self.assertRaises(InjectedCrash):
                    product.workspace_repair_apply(self.p, self.target, preview['request'], confirm_token=preview['confirm_token'], inject_at='after-backup')
                original_request = (backup / 'request.json').read_bytes()
                original_bytes = (backup / 'original/colvia').read_bytes()
                os.chmod(backup / name, stat.S_IREAD)
                before, saved = physical(self.target), physical(backup)
                with self.assertRaises(ContractError) as caught:
                    product.workspace_repair_apply(self.p, self.target, preview['request'], confirm_token=preview['confirm_token'], recover=True)
                self.assertEqual('HV2-WINDOWS-READONLY', caught.exception.code)
                self.assertEqual(before, physical(self.target)); self.assertEqual(saved, physical(backup))
                os.chmod(backup / name, stat.S_IWRITE)  # External fixture correction only.
                product.workspace_repair_apply(self.p, self.target, preview['request'], confirm_token=preview['confirm_token'], recover=True)
                self.assert_product(self.p_candidate)
                self.assertEqual(original_request, (backup / 'request.json').read_bytes())
                self.assertEqual(original_bytes, (backup / 'original/colvia').read_bytes())
                before, saved = physical(self.target), physical(backup)
                product.workspace_repair_apply(self.p, self.target, preview['request'], confirm_token=preview['confirm_token'], recover=True)
                self.assertEqual(before, physical(self.target)); self.assertEqual(saved, physical(backup))

    def test_native_read_entries_preserve_fresh_partial_installed_and_detached_state(self):
        observations = []
        def check(classification, *, installed=False, retained=()):
            anchor = self.target / '.hrn/locks/writer.lock'
            if anchor.exists():
                self.assertEqual(0, anchor.stat().st_size); anchor.unlink()  # Quiescent fixture setup.
            entries = [('source-P', self.p / 'colvia', True), ('source-Q', self.q / 'colvia', True)]
            entries += [('retained-' + str(i), path, True) for i, path in enumerate(retained) if path.is_file()]
            if installed: entries += [('installed', self.target / 'colvia', False)]
            expected = {'uninitialized': 15, 'partial': 14, 'pass': 0, 'detached': 0}[classification]
            before = physical(self.target)
            for entry, launcher, source_mode in entries:
                for command in ('doctor', 'status', 'view'):
                    argv = [sys.executable, '-I', '-B', str(launcher)]
                    if source_mode: argv.append('--source-checkout')
                    argv += [command, '--target', str(self.target)]
                    result = subprocess.run(argv, cwd=self.target, capture_output=True, timeout=60)
                    row = {'state': classification, 'entry': entry, 'argv': argv, 'exit': result.returncode,
                           'stdout': result.stdout.decode('utf-8', errors='replace'), 'stderr': result.stderr.decode('utf-8', errors='replace')}
                    observations.append(row); (self.root / 'read-observations.json').write_bytes(canonical(observations))
                    self.assertEqual(expected, result.returncode, row); self.assertEqual(b'', result.stderr, row)
                    if command != 'view':
                        self.assertEqual(classification, json.loads(result.stdout)['classification'], row)
                    else: self.assertIn(classification.encode(), result.stdout, row)
                    self.assertFalse(anchor.exists(), row); self.assertEqual(before, physical(self.target), row)
        check('uninitialized')
        initial, _ = self.init(point='after-plan'); check('partial')
        product.workspace_init_apply(self.p, self.target, initial['request'], confirm_token=initial['confirm_token'], recover=True)
        with workspace.writer_guard(self.target):
            with self.assertRaisesRegex(ContractError, 'recursive writer guard'):
                with workspace.writer_guard(self.target):
                    self.fail('recursive guard entered')
        retained_p = self.target / '.hrn/product/releases' / self.p_candidate['release_ref']['id'] / 'payload/colvia'
        check('pass', installed=True, retained=(retained_p,))
        up = product.workspace_switch_preview(self.target, action='update', source=self.q, operation_id='read-update', created_at=TIME)
        with self.assertRaises(InjectedCrash):
            product.workspace_switch_apply(self.target, up['request'], confirm_token=up['confirm_token'], source=self.q, inject_at='after-receipt')
        check('partial', installed=True, retained=(retained_p,))
        self.assertNotIn('OLD source', product.workspace_status(self.target)['next_action'])
        product.workspace_switch_apply(self.target, up['request'], confirm_token=up['confirm_token'], source=self.q, recover=True)
        retained_q = self.target / '.hrn/product/releases' / self.q_candidate['release_ref']['id'] / 'payload/colvia'
        check('pass', installed=True, retained=(retained_p, retained_q))
        detach = product.workspace_detach_preview(self.target, operation_id='read-detach', created_at=TIME)
        with self.assertRaises(InjectedCrash):
            product.workspace_detach_apply(self.target, detach['request'], confirm_token=detach['confirm_token'], inject_at='after-launcher')
        check('partial', retained=(retained_p, retained_q)); self.plain_audit('partial')
        product.workspace_detach_apply(self.target, detach['request'], confirm_token=detach['confirm_token'], recover=True)
        check('detached'); self.plain_audit('detached')

    def plain_audit(self, classification):
        result = subprocess.run([sys.executable, '-I', '-B', str(SOURCE / 'tests/fixtures/product_plain_auditor.py'), str(self.target)],
                                capture_output=True, timeout=30)
        self.assertEqual({'partial': 14, 'detached': 0, 'degraded': 10}[classification], result.returncode, result.stdout + result.stderr)
        self.assertEqual(classification, json.loads(result.stdout)['classification'])
        self.assertEqual(b'', result.stderr)

    def test_detach6_each_prefix_preserves_truth_and_requires_exact_pair(self):
        for point in ('after-receipt', 'after-launcher', 'after-file', 'after-files', 'after-directory', 'after-product'):
            with self.subTest(point=point):
                self.target = self.root / hashlib.sha256(point.encode()).hexdigest()[:4]; self.target.mkdir(); (self.target / 'sample.txt').write_bytes(b'before\r\n'); self.init()
                preview = product.workspace_detach_preview(self.target, operation_id='detach-a', created_at=TIME)
                self.assertEqual(6, preview['request']['schema_version'])
                preserved = {e['path']: (self.target / e['path']).read_bytes() for e in preview['request']['preserve']}
                with self.assertRaises(InjectedCrash):
                    product.workspace_detach_apply(self.target, preview['request'], confirm_token=preview['confirm_token'], inject_at=point)
                self.assert_old_writers_refuse(self.target, 'detach-' + point)
                receipt_path = self.target / '.hrn/detached.json'; raw = receipt_path.read_bytes(); receipt = json.loads(raw)
                self.assertEqual(6, receipt['schema_version']); self.assertEqual(preview['request'], receipt['plan'])
                before = physical(self.target); state = product.workspace_detached_status(self.target)
                self.plain_audit(state['classification']); self.assertEqual(before, physical(self.target))
                # Surviving metadata must reject schema5 despite the same 30 paths.
                witnesses = [n for n in state['remaining_files'] if n == 'colvia' or n == '.hrn/product/binding.json'
                             or n.endswith('/inventory.json') or n.endswith('/payload/colvia')]
                if witnesses:
                    wrong = copy.deepcopy(receipt); wrong['schema_version'] = 5; wrong['plan']['schema_version'] = 5
                    receipt_path.write_bytes(canonical(wrong)); corrupt = physical(self.target)
                    with self.assertRaises(ContractError): product.workspace_detached_status(self.target)
                    self.plain_audit('degraded'); self.assertEqual(corrupt, physical(self.target)); receipt_path.write_bytes(raw)
                # Complete removal membership remains required even after all files are gone.
                wrong = copy.deepcopy(receipt); wrong['plan']['remove'].pop()
                receipt_path.write_bytes(canonical(wrong)); corrupt = physical(self.target)
                with self.assertRaises(ContractError): product.workspace_detached_status(self.target)
                self.plain_audit('degraded'); self.assertEqual(corrupt, physical(self.target)); receipt_path.write_bytes(raw)
                receipt['schema_version'] = 3; receipt_path.write_bytes(canonical(receipt)); corrupt = physical(self.target)
                with self.assertRaises(ContractError): product.workspace_detached_status(self.target)
                self.plain_audit('degraded'); self.assertEqual(corrupt, physical(self.target)); receipt_path.write_bytes(raw)
                result = product.workspace_detach_apply(self.target, preview['request'], confirm_token=preview['confirm_token'], recover=True)
                self.assertEqual('detached', result['classification'])
                self.plain_audit('detached')
                for name, data in preserved.items(): self.assertEqual(data, (self.target / name).read_bytes())
                for item in preview['request']['remove']: self.assertFalse((self.target / item['path']).exists())
                self.assertEqual(b'before\r\n', (self.target / 'sample.txt').read_bytes())
                before = physical(self.target)
                product.workspace_detach_apply(self.target, preview['request'], confirm_token=preview['confirm_token'], recover=True)
                self.assertEqual(before, physical(self.target))
                with self.assertRaises(ContractError): self.init()
                self.assertEqual(before, physical(self.target))

    def test_detach_readonly_union_precedes_marker_and_keeps_preserved_flag(self):
        self.init(); preview = product.workspace_detach_preview(self.target, operation_id='detach-a', created_at=TIME)
        member = self.target / '.hrn/product/releases' / self.p_candidate['release_ref']['id'] / 'payload/README.md'
        os.chmod(member, stat.S_IREAD); before = physical(self.target)
        with self.assertRaises(ContractError) as caught:
            product.workspace_detach_apply(self.target, preview['request'], confirm_token=preview['confirm_token'])
        self.assertEqual('HV2-WINDOWS-READONLY', caught.exception.code); self.assertEqual(before, physical(self.target))
        self.assertFalse((self.target / '.hrn/detached.json').exists())
        os.chmod(member, stat.S_IWRITE)
        os.chmod(self.target / '.hrn/format.json', stat.S_IREAD)
        product.workspace_detach_apply(self.target, preview['request'], confirm_token=preview['confirm_token'])
        self.assertTrue((self.target / '.hrn/format.json').stat().st_file_attributes & 1)
        self.assertEqual('detached', product.workspace_detached_status(self.target)['classification'])


    def test_detach_every_reachable_removal_prefix_plain_reader_and_exact_resume(self):
        self.init();preview=product.workspace_detach_preview(self.target,operation_id='detach-all',created_at=TIME)
        plan=preview['request'];preserved={e['path']:(self.target/e['path']).read_bytes() for e in plan['preserve']}
        with self.assertRaises(InjectedCrash):
            product.workspace_detach_apply(self.target,plan,confirm_token=preview['confirm_token'],inject_at='after-receipt')
        original_files=product.workspace_detached_status(self.target)['remaining_files']
        observed=[]
        while True:
            before=physical(self.target);state=product.workspace_detached_status(self.target)
            self.plain_audit(state['classification']);self.assertEqual(before,physical(self.target))
            for name,data in preserved.items():self.assertEqual(data,(self.target/name).read_bytes())
            if state['classification']=='detached':break
            files=state['remaining_files'];directories=state['remaining_directories']
            if files:
                name=files[0];point='after-launcher' if name=='colvia' else 'after-file'
            else:
                self.assertTrue(directories);name=directories[0];point='after-directory'
            with self.assertRaises(InjectedCrash):
                product.workspace_detach_apply(self.target,plan,confirm_token=preview['confirm_token'],recover=True,inject_at=point)
            self.assertFalse((self.target/name).exists());observed.append(name)
            after=product.workspace_detached_status(self.target)
            if files:self.assertEqual(files[1:],after['remaining_files'])
            else:self.assertEqual(directories[1:],after['remaining_directories'])
            print('NATIVE_DETACH_REMOVAL_PREFIX '+json.dumps({'removed':name,'remaining_files':after['remaining_files'],'remaining_directories':after['remaining_directories'],'classification':after['classification']}),flush=True)
        self.assertEqual(original_files,observed[:len(original_files)])
        before=physical(self.target)
        self.assertEqual('detached',product.workspace_detach_apply(self.target,plan,confirm_token=preview['confirm_token'],recover=True)['classification'])
        self.assertEqual(before,physical(self.target))
