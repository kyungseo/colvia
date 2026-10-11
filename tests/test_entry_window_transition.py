"""Explicit entry-1 factory. Default discovery has no TestCase or product import.

P1a control/fixture assertions and future product assertions have separate IDs.
No result is implied by constructing this suite. Children inherit the reviewed
controller sandbox/process group; this module never opens a shell or a session.
"""
from __future__ import annotations

import ast
import copy
import fcntl
import hashlib
import json
import os
from pathlib import Path
import signal
import stat
import subprocess
import sys
import time
from types import MappingProxyType
import unittest

OLD_PATHS = (
    '.gitignore', 'AGENTS.md', 'CLAUDE.md', 'PRODUCT-CAPABILITIES.json', 'README.md',
    'adapters/harness-v2-work/SKILL.md', 'docs/CONCEPTS.md', 'docs/GENERAL-WORK.md',
    'docs/GETTING-STARTED.md', 'docs/GUIDED-INTENT-FORMATION.md', 'docs/MAINTAINING.md',
    'docs/MANUAL-OPERATION.md', 'docs/OPERATIONS.md', 'docs/README.md', 'docs/REFERENCE.md',
    'docs/SECURITY-AND-SUPPORT.md', 'docs/WORKSPACE-CONTRACT.md', 'hv2',
    'src/hv2ref/__init__.py', 'src/hv2ref/candidates.py', 'src/hv2ref/cli.py',
    'src/hv2ref/errors.py', 'src/hv2ref/intent.py', 'src/hv2ref/jsonio.py',
    'src/hv2ref/product.py', 'src/hv2ref/umbrella.py', 'src/hv2ref/view.py',
    'src/hv2ref/work.py', 'src/hv2ref/workspace.py',
)
OLD_PATHS_SHA256 = '55662c7bdf478101b4e06d5af824e307eb1eb1ad543946c5df1c5f37507aa780'
FIXTURE_TIME = '2026-01-01T00:00:00Z'
PREFIX_IDS = ('S1-01', 'S1-02', 'S2-01', 'S2-02', 'S3-01', 'N-01', 'N-02', 'N-03',
              'N-04', 'N-05', 'O-01', 'O-02', 'B-01', 'B-02', 'B-03', 'B-04', 'B-05', 'B-06', 'B-07')
CONTEXT_FIELDS = frozenset({'schema', 'phase', 'invocation_path', 'invocation_sha256',
    'controls_dir', 'observer_sha256', 'work_root', 'runtime_path', 'runtime_sha256', 'observer_command_prefix'})


def canonical(value):
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + '\n').encode()


def sha(data):
    return hashlib.sha256(data).hexdigest()


def need(ok, message):
    if not ok:
        raise RuntimeError(message)


def ref(value, key):
    return {'id': value[key], 'sha256': sha(canonical(value))}


def snapshot(root, *, allow_hardlinks=False):
    """Synthetic fixture bytes/types/modes, including dirs; not a product oracle."""
    result = {}
    for p in sorted(root.rglob('*')):
        st = p.lstat(); name = p.relative_to(root).as_posix()
        if stat.S_ISLNK(st.st_mode):
            result[name] = ('symlink', os.readlink(p))
        elif stat.S_ISDIR(st.st_mode):
            result[name] = ('directory', stat.S_IMODE(st.st_mode))
        else:
            need(stat.S_ISREG(st.st_mode) and (allow_hardlinks or st.st_nlink == 1), 'special/linked fixture member')
            b = p.read_bytes(); result[name] = ('file', stat.S_IMODE(st.st_mode), len(b), sha(b))
            if allow_hardlinks: result[name] += (st.st_nlink,)
    return result


def write_file(path, data, mode=0o600):
    path.parent.mkdir(parents=True, exist_ok=True)
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, mode)
    try:
        while data:
            n = os.write(fd, data); need(n > 0, 'fixture zero write'); data = data[n:]
        os.fsync(fd)
    finally:
        os.close(fd)


def schema1_fixture(target):
    """Independent literal planning-1 construction, never an old executable."""
    need(target.is_dir() and not list(target.iterdir()), 'schema1 target must be empty')
    need(sha(('\n'.join(OLD_PATHS) + '\n').encode()) == OLD_PATHS_SHA256, 'literal old inventory drift')
    payload = {p: ('synthetic planning-1 fixture: ' + p + '\n').encode() for p in OLD_PATHS}
    payload['hv2'] = b'WORKSPACE_INVENTORY_ID = "planning-1"\n'
    inventory = {'record_type': 'release-inventory', 'schema_version': 1, 'inventory_id': 'planning-1',
        'entries': [{'path': p, 'sha256': sha(payload[p]), 'size_bytes': len(payload[p])} for p in OLD_PATHS]}
    digest = sha(canonical(inventory)); release = {'id': 'product-release-' + digest[:24],
        'sha256': digest, 'inventory_id': 'planning-1'}
    fmt = {'record_type': 'workspace-format', 'format_version': 1,
        'authority_home_id': 'fixture-home', 'created_at': FIXTURE_TIME, 'lineage': None}
    init = {'record_type': 'lifecycle-plan', 'schema_version': 1, 'operation_id': 'fixture-init',
        'action': 'init', 'authority_home_id': fmt['authority_home_id'], 'expected_binding_ref': None,
        'candidate_release': release, 'format_sha256': sha(canonical(fmt)), 'truth_refs': [],
        'remove': [], 'preserve': [], 'created_at': FIXTURE_TIME, 'target_fingerprint': sha(os.fsencode(target))}
    binding = {'record_type': 'product-binding', 'schema_version': 1, 'authority_home_id': fmt['authority_home_id'],
        'active_release': release, 'prior_release': None, 'operation_id': init['operation_id']}
    init_receipt = {'record_type': 'lifecycle-receipt', 'schema_version': 1, 'operation_id': init['operation_id'],
        'plan': init, 'prior_binding_ref': None, 'result_binding_ref': ref(binding, 'operation_id')}
    data = {'hv2': payload['hv2'], '.hrn/format.json': canonical(fmt), '.hrn/.gitignore': b'staging/\nlocks/\n',
        '.hrn/product/init-plan.json': canonical(init), '.hrn/product/binding.json': canonical(binding),
        '.hrn/product/receipts/fixture-init.json': canonical(init_receipt),
        '.hrn/product/releases/' + release['id'] + '/inventory.json': canonical(inventory)}
    data.update({'.hrn/product/releases/' + release['id'] + '/payload/' + p: b for p, b in payload.items()})
    preserve_names = ('.hrn/.gitignore', '.hrn/format.json')
    def entries(names):
        return [{'path': p, 'sha256': sha(data[p]), 'size_bytes': len(data[p])} for p in sorted(names, key=lambda n: n.encode())]
    plan = {'record_type': 'lifecycle-plan', 'schema_version': 1, 'operation_id': 'fixture-detach',
        'action': 'detach', 'authority_home_id': fmt['authority_home_id'], 'expected_binding_ref': ref(binding, 'operation_id'),
        'candidate_release': None, 'format_sha256': sha(canonical(fmt)), 'truth_refs': [],
        'remove': entries(set(data) - set(preserve_names)), 'preserve': entries(preserve_names),
        'created_at': FIXTURE_TIME, 'target_fingerprint': sha(os.fsencode(target))}
    receipt = {'record_type': 'lifecycle-receipt', 'schema_version': 1, 'operation_id': plan['operation_id'],
        'plan': plan, 'prior_binding_ref': plan['expected_binding_ref'], 'result_binding_ref': None}
    for name, content in data.items():
        write_file(target / name, content, 0o755 if name == 'hv2' or name.endswith('/payload/hv2') else 0o644)
    for name in ('intents', 'work', 'staging', 'locks'):
        (target / '.hrn' / name).mkdir(exist_ok=True)
    write_file(target / '.hrn/detached.json', canonical(receipt), 0o644)
    order = ['hv2'] + [e['path'] for e in plan['remove'] if e['path'] != 'hv2']
    directories = sorted({p.as_posix() for name in order if name != 'hv2' for p in Path(name).parents
                          if p.as_posix().startswith('.hrn/product')}, key=lambda n: (-len(n.split('/')), n.encode()))
    return {'plan': plan, 'receipt': receipt, 'inventory': inventory, 'binding': binding,
            'remove_order': order, 'directory_order': directories, 'data': data}


# Fixed OLD init/detach programs; OLD/src is their sole product import root.
# P2 old_local has a separately reviewed fixed literal with an enumerated scope
# argument. No program/command text arrives through argv in either path.
_OLD_PROGRAM_BASE = r'''
import hashlib,json,os,stat,sys
from pathlib import Path
if len(sys.argv)!=3:raise RuntimeError('OLD_SRC TARGET required')
old,target=map(Path,sys.argv[1:]);sys.path.insert(0,str(old/'src'))
from hv2ref.product import workspace_init_preview,workspace_init_apply,verify_workspace_product,workspace_detach_preview,workspace_detach_apply
from hv2ref.errors import InjectedCrash
from hv2ref.jsonio import canonical_json_bytes
TIME='2026-01-01T00:00:00Z'
def need(ok,message):
 if not ok:raise RuntimeError(message)
def snap():
 out={}
 for p in sorted(target.rglob('*')):
  s=p.lstat();n=p.relative_to(target).as_posix()
  need(not p.is_symlink(),'linked fixture member')
  if p.is_dir():out[n]=['directory',stat.S_IMODE(s.st_mode)]
  else:
   need(stat.S_ISREG(s.st_mode) and s.st_nlink==1,'special fixture member')
   b=p.read_bytes();out[n]=['file',stat.S_IMODE(s.st_mode),len(b),hashlib.sha256(b).hexdigest()]
 return out
need(target.is_dir() and not list(target.iterdir()),'nonempty target')
need(not any((p/'.git').exists() for p in (target,*target.parents)),'fixture topology must be non-Git')
(target/'a').write_bytes(b'preserved project content\n')
preview=workspace_init_preview(old,target,authority_home_id='fixture-home',operation_id='fixture-init',created_at=TIME)
workspace_init_apply(old,target,preview['request'],confirm_token=preview['confirm_token'])
state=verify_workspace_product(target)
need(state['inventory']['inventory_id']=='checkout-1','not OLD window')
need(hashlib.sha256(canonical_json_bytes(state['inventory'])).hexdigest()=='8bd0eeac55fb0af92b61a7a36a98adb9957b880c791b957b20c319a51c5577f3','wrong OLD release')
for name,module in tuple(sys.modules.items()):
 if name=='hv2ref' or name.startswith('hv2ref.'):
  need(Path(module.__file__).is_relative_to(old/'src'),'non-OLD product import')
before=snap()
'''
OLD_INIT_PROGRAM = _OLD_PROGRAM_BASE + r'''
print(json.dumps({'kind':'actual-old-init','pid':os.getpid(),'pgid':os.getpgrp(),'binding_ref':state['binding_ref'],'inventory':state['inventory'],'snapshot':before},sort_keys=True))
'''
OLD_DETACH_PROGRAM = _OLD_PROGRAM_BASE + r'''
preview=workspace_detach_preview(target,operation_id='fixture-detach',created_at=TIME)
try:
 workspace_detach_apply(target,preview['request'],confirm_token=preview['confirm_token'],inject_at='after-receipt')
except InjectedCrash as exc:
 need(exc.point=='after-receipt' and exc.code=='HV2-INJECTED-CRASH','wrong injected point')
else:raise RuntimeError('missing exact InjectedCrash')
receipt=json.loads((target/'.hrn/detached.json').read_bytes())
need(type(receipt['schema_version']) is int and receipt['schema_version']==2 and type(receipt['plan']['schema_version']) is int and receipt['plan']['schema_version']==2,'not paired schema2')
need(receipt['plan']==preview['request'] and receipt['prior_binding_ref']==state['binding_ref'] and receipt['result_binding_ref'] is None,'wrong canonical binding')
need((target/'.hrn/detached.json').read_bytes()==canonical_json_bytes(receipt),'noncanonical receipt')
after=snap();need(set(after)==set(before)|{'.hrn/detached.json'},'unexpected prefix member')
need(all(after[k]==v for k,v in before.items()),'OLD root/product/truth changed')
print(json.dumps({'kind':'actual-old-schema2-prefix','pid':os.getpid(),'pgid':os.getpgrp(),'receipt':receipt,'binding_ref':state['binding_ref'],'before':before,'after':after},sort_keys=True))
'''
# The controller/runner are imported with a write/process audit guard before any
# test/product module. The fixed probe permits reads needed by config later, but
# import itself must not call config, launch children, or mutate paths.
IMPORT_PROBE_PROGRAM = r'''
import os,sys
from pathlib import Path
if len(sys.argv)!=3:raise RuntimeError("CONTROLS SOURCE required")
controls,source=map(Path,sys.argv[1:]);sys.path.append(str(controls))
def audit(event,args):
 if event in ('subprocess.Popen','os.system','os.posix_spawn','os.fork','os.mkdir','os.remove','os.rename','os.chmod','os.rmdir','os.link','os.symlink','os.truncate','os.exec','os.forkpty'):
  raise RuntimeError('import side effect '+event)
 if event=='open' and len(args)>2 and isinstance(args[2],int) and args[2] & (os.O_WRONLY|os.O_RDWR|os.O_CREAT|os.O_TRUNC):
  raise RuntimeError('import write')
sys.addaudithook(audit)
import common
common.config=lambda *a,**k: (_ for _ in ()).throw(RuntimeError('import config execution'))
import controller,runner,observer
if any(n=='hv2ref' or n.startswith('hv2ref.') for n in sys.modules):raise RuntimeError('product import')
sys.path.insert(0,str(source/'tests'))
import test_entry_window_transition as factory_module
import unittest
if unittest.TestLoader().loadTestsFromModule(factory_module).countTestCases()!=0:raise RuntimeError('default factory leakage')
if any(n=='hv2ref' or n.startswith('hv2ref.') for n in sys.modules):raise RuntimeError('factory product import')
if set(controller.ENTRY_RUN_NAMES)!={m+'-'+s for m,slots in controller.ENTRY_MODE_SLOTS.items() for s in slots}:raise RuntimeError('slot drift')
print('CONTROL_IMPORT_PURE',os.getpgrp())
'''


RUNNER_FAILFAST_PROBE_PROGRAM = "# Fixed test-only runner orchestration probe. Real config/OLD admission first;\n# only synthetic discovery/selection metadata are substituted in this child.\nimport hashlib, json, os, sys, unittest\nfrom pathlib import Path\nfrom unittest import mock\nif len(sys.argv) != 6: raise RuntimeError('CONTROLS INPUT SHA OUT KIND required')\ncontrols, input_path, input_sha, out, kind = sys.argv[1:]\ncontrols = Path(controls); out = Path(out)\nif kind not in ('failure', 'error', 'subtest', 'success'): raise RuntimeError('probe kind')\nsys.path.append(str(controls))\nimport runner\nfrom common import canonical, config, digest, verify_old, read_json\nif Path(runner.__file__) != controls / 'runner.py': raise RuntimeError('runner identity')\nactual, paths = config(input_path, input_sha)\nverify_old(paths['old'], read_json(controls / 'baseline-inputs.json'))\nif not out.is_relative_to(paths['exec'] / 'runs') or not out.is_dir(): raise RuntimeError('probe output boundary')\nclass Probe(unittest.TestCase):\n    def setUp(self):\n        self.base = out / self._testMethodName\n        self.base.mkdir()\n        (self.base / 'before.bin').write_bytes(b'fixed synthetic failure preservation\\n')\n    def tearDown(self):\n        (out / ('cleanup-' + self._testMethodName)).write_bytes(b'cleanup completed\\n')\n    def test_01_selected(self):\n        if kind == 'failure': self.fail('EXPECTED_SYNTHETIC_FAILURE')\n        if kind == 'error': raise RuntimeError('EXPECTED_SYNTHETIC_ERROR')\n        if kind == 'subtest':\n            with self.subTest(fixed='first'):\n                self.fail('EXPECTED_SYNTHETIC_SUBTEST')\n            (out / 'continued-after-subtest').write_bytes(b'must not execute\\n')\n    def test_02_sentinel(self):\n        (out / 'second-test-started').write_bytes(b'normal success control only\\n')\nProbe.__module__ = 'runner_failfast_probe'; Probe.__qualname__ = 'Probe'\ntests = [Probe('test_01_selected'), Probe('test_02_sentinel')]\nids = [test.id() for test in tests]\nsynthetic = dict(actual, phase='base', factory=False, selection=ids)\ncollection = {'source_digest': actual['source_digest'], 'source_root_entries': actual['source_root_entries'],\n    'controls': actual['controls'], 'default_ids': ids, 'factory_ids': [],\n    'ordered': [{'id': name, 'occurrence': 1} for name in ids], 'duplicates': {}}\nsynthetic['collection_sha256'] = digest(canonical(collection))\ndef checked_fixture_config(path, sha):\n    if (path, sha) != (input_path, input_sha): raise RuntimeError('probe input mismatch')\n    current, current_paths = config(path, sha)\n    if current != actual or current_paths != paths: raise RuntimeError('probe admission drift')\n    return synthetic, paths\nwith mock.patch.object(runner, 'config', checked_fixture_config), mock.patch.object(unittest.TestLoader, 'discover', return_value=unittest.TestSuite(tests)):\n    sys.argv = [str(controls / 'runner.py'), input_path, input_sha, str(out), 'focused']\n    runner.main()\n"

OBSERVER_DIRFD_PROBE_PROGRAM = "# Fixed synthetic read/negative probes through the admitted actual observer.\n# Only the final product dispatch is substituted; config, hooks and faults run.\nimport errno, json, os, sys\nfrom pathlib import Path\nfrom unittest import mock\nif len(sys.argv) != 7: raise RuntimeError('CONTROLS INPUT SHA SCENARIO SHA KIND required')\ncontrols, inp, inp_sha, scenario, scenario_sha, kind = sys.argv[1:]\nif kind not in ('reads', 'mutation', 'paths', 'before', 'after'): raise RuntimeError('probe kind')\ncontrols = Path(controls); sys.path.append(str(controls))\nimport observer\nfrom common import config, digest, regular, read_json, require\nrequire(Path(observer.__file__) == controls / 'observer.py', 'observer identity')\nc, paths = config(inp, inp_sha)\nrequire(digest(regular(Path(scenario))) == scenario_sha, 'probe scenario drift')\ns = read_json(Path(scenario)); target = Path(s['target'])\nrequire(target.is_relative_to(paths['exec'] / 'runs'), 'probe target boundary')\noriginal_open, original_close = os.open, os.close\nparent = original_open(target, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)\nseen = []\ndef dispatch(entry, run_name):\n    require(entry == str(paths['source'] / 'colvia') and run_name == '__main__', 'fixed product dispatch')\n    flags = os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK\n    if kind in ('reads', 'before', 'after'):\n        operands = ('payload.bin', b'payload.bin', Path('payload.bin')) if kind == 'reads' else ('payload.bin',)\n        for operand in operands:\n            fd = os.open(operand, flags, dir_fd=parent)\n            try:\n                require(os.read(fd, 4096) == b'fixed-dirfd-read\\n', 'wrong descriptor-relative bytes')\n                require(os.fstat(fd).st_ino == (target / 'payload.bin').stat().st_ino, 'wrong descriptor inode')\n            finally: os.close(fd)\n        if kind == 'reads':\n            directory = os.open('nested', os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=parent)\n            try:\n                leaf = os.open('child.bin', flags, dir_fd=directory)\n                try: require(os.read(leaf, 4096) == b'nested-dirfd-read\\n', 'nested bytes')\n                finally: os.close(leaf)\n            finally: os.close(directory)\n        print('READ_COMPLETED', flush=True)\n    elif kind == 'mutation':\n        cases = (os.O_WRONLY | os.O_NOFOLLOW, os.O_RDWR | os.O_NOFOLLOW,\n                 os.O_WRONLY | os.O_CREAT | os.O_NOFOLLOW,\n                 os.O_RDONLY | os.O_TRUNC | os.O_NOFOLLOW,\n                 os.O_RDONLY | os.O_APPEND | os.O_NOFOLLOW,\n                 os.O_RDONLY | os.O_NOFOLLOW | os.O_EXCL)\n        for value in cases:\n            try: fd = os.open('payload.bin', value, dir_fd=parent)\n            except RuntimeError as exc:\n                require(str(exc) == 'relative-fd read flags unsupported', 'unexpected flags refusal')\n                seen.append(value)\n            else:\n                os.close(fd); raise AssertionError('relative mutation unexpectedly admitted')\n        require(len(seen) == len(cases), 'missing mutation refusal')\n    else:\n        for value in ('.', '..', '../payload.bin', 'nested/child.bin', str(target / 'payload.bin'), ''):\n            try: fd = os.open(value, flags, dir_fd=parent)\n            except RuntimeError as exc:\n                require(str(exc) == 'relative-fd read component unsupported', 'unexpected component refusal')\n            else:\n                os.close(fd); raise AssertionError('unsupported component admitted')\n        try: fd = os.open('link.bin', flags, dir_fd=parent)\n        except OSError as exc: require(exc.errno == errno.ELOOP, 'nofollow error changed')\n        else:\n            os.close(fd); raise AssertionError('symlink followed')\n        try: fd = os.open('payload.bin', os.O_RDONLY, dir_fd=parent)\n        except RuntimeError as exc: require(str(exc) == 'relative-fd read flags unsupported', 'nofollow guard')\n        else:\n            os.close(fd); raise AssertionError('nofollow omission admitted')\n    return {}\ntry:\n    with mock.patch.object(observer.runpy, 'run_path', side_effect=dispatch):\n        sys.argv = [str(controls / 'observer.py'), inp, inp_sha, scenario, scenario_sha]\n        observer.main()\nfinally:\n    original_close(parent)\nprint(json.dumps({'kind': kind, 'pid': os.getpid(), 'pgid': os.getpgrp(), 'status': 'probe-complete'}))\n"

D3_SYNC_PROGRAM = r'''
# Fixed child: instrument real sync aliases, then call the real CLI once.
# No input-provided code, commands, imports or output paths are accepted.
import contextlib, errno, hashlib, io, json, os, stat, sys
from pathlib import Path
from unittest import mock
if len(sys.argv) != 4: raise RuntimeError('SOURCE TARGET CANDIDATE required')
source, target, candidate = map(Path, sys.argv[1:])
request = json.load(sys.stdin)
if set(request) != {'preview', 'recover', 'selector', 'fault', 'truth_change'}: raise RuntimeError('D3 request keys')
if request['fault'] not in (None, 'unavailable', 'oserror'): raise RuntimeError('D3 fault')
if type(request['recover']) is not bool or type(request['truth_change']) is not bool: raise RuntimeError('D3 booleans')
sys.path.insert(0, str(source / 'src'))
from hv2ref import product, workspace, jsonio, cli
preview = request['preview']; plan = preview['request']; rid = plan['candidate_release']['id']; op = plan['operation_id']
release = target / '.hrn/product/releases' / rid
switch = target / '.hrn/staging' / ('switch-' + op); staged = switch / rid
binding_stage = target / '.hrn/staging' / ('entry-' + op); next_binding = binding_stage / 'binding.next'
receipt = target / '.hrn/product/receipts' / (op + '.json')
binding = target / '.hrn/product/binding.json'
def tree():
    result = {}
    for path in sorted(target.rglob('*')):
        st = path.lstat(); name = path.relative_to(target).as_posix()
        if stat.S_ISLNK(st.st_mode): value = ['symlink', os.readlink(path)]
        elif stat.S_ISDIR(st.st_mode): value = ['directory', stat.S_IMODE(st.st_mode)]
        else:
            if not stat.S_ISREG(st.st_mode) or st.st_nlink != 1: raise RuntimeError('special D3 fixture')
            data = path.read_bytes(); value = ['file', stat.S_IMODE(st.st_mode), len(data), hashlib.sha256(data).hexdigest()]
        result[name] = value
    return result
selectors = ('admission_root', 'admission_locks', 'receipt_parent', 'candidate_directory_parent',
    'candidate_directory_self', 'candidate_member_parent', 'release_parent', 'release_operation_parent',
    'new_entry_parent', 'old_retirement_parent', 'binding_directory_parent', 'binding_directory_self',
    'binding_member_parent', 'binding_product_parent', 'binding_operation_parent', 'replay_release', 'recovery_release', 'same_entry_receipt',
    'recovery_release_parent', 'recovery_operation_parent', 'recovery_new_parent', 'recovery_old_parent')
if request['selector'] not in (None, *selectors): raise RuntimeError('D3 selector')
if (request['selector'] is None) != (request['fault'] is None): raise RuntimeError('D3 selector/fault pair')
rows = []; hits = {}; injected = []; initial = tree()
def facts():
    return {'receipt': receipt.is_file(), 'staged': staged.is_dir(),
            'inventory': (staged / 'inventory.json').is_file(), 'release': release.is_dir(),
            'old': (target / 'hv2').is_file(),
            'new_mode': stat.S_IMODE((target / 'colvia').stat().st_mode) if (target / 'colvia').is_file() else None,
            'binding_directory': binding_stage.is_dir(),
            'next_size': next_binding.stat().st_size if next_binding.is_file() else None,
            'b1': json.loads(binding.read_bytes())['operation_id'] == op}
initial_facts = facts()
def matches(path, alias, s):
    if alias != 'product':
        return ['same_entry_receipt'] if alias == 'jsonio' and path == receipt.parent and s['receipt'] else []
    options = {
        'admission_root': path == target and not s['receipt'],
        'admission_locks': path == target / '.hrn/locks' and not s['receipt'],
        'receipt_parent': path == receipt.parent and s['receipt'] and not s['staged'] and not s['release'],
        'candidate_directory_parent': path == switch and s['staged'] and not s['inventory'],
        'candidate_directory_self': path == staged and not s['inventory'],
        'candidate_member_parent': path == staged and s['inventory'],
        'release_parent': path == release.parent and s['release'] and s['new_mode'] is None,
        'release_operation_parent': path == switch and s['release'] and s['new_mode'] is None,
        'new_entry_parent': path == target and s['new_mode'] == 0o755 and s['old'],
        'old_retirement_parent': path == target and s['new_mode'] == 0o755 and not s['old'] and not s['b1'],
        'binding_directory_parent': path == binding_stage.parent and s['binding_directory'] and s['next_size'] is None and not s['b1'],
        'binding_directory_self': path == binding_stage and s['next_size'] is None and not s['b1'],
        'binding_member_parent': path == binding_stage and s['next_size'] is not None and not s['b1'],
        'binding_product_parent': path == binding.parent and s['b1'],
        'binding_operation_parent': path == binding_stage and s['b1'] and s['next_size'] is None,
        'replay_release': path == release and s['b1'],
        # S5/B0: admission already visited release once; the existing receipt
        # was then re-synced. Select the later recovery pass, not admission.
        'recovery_release': request['recover'] and path == release
            and initial_facts['receipt'] and initial_facts['release']
            and initial_facts['new_mode'] == 0o755 and not initial_facts['old']
            and not initial_facts['b1'] and not initial_facts['binding_directory']
            and initial_facts['next_size'] is None and s == initial_facts
            and sum(r['alias'] == 'product' and r['path'] == release.relative_to(target).as_posix() for r in rows) == 1
            and sum(r['alias'] == 'product' and r['path'] == '.hrn/product/receipts' for r in rows) == 2
            and max(i for i, r in enumerate(rows) if r['alias'] == 'product' and r['path'] == '.hrn/product/receipts')
                > max(i for i, r in enumerate(rows) if r['alias'] == 'product' and r['path'] == release.relative_to(target).as_posix()),
    }
    # The fixed S5 fixture has no staging binding yet. Admission has already
    # synced the existing receipt; its second product receipt sync starts recovery.
    receipts = [i for i, r in enumerate(rows) if r['alias'] == 'product' and r['path'] == '.hrn/product/receipts' and not r['facts']['b1']]
    in_recovery = (request['recover'] and initial_facts['release'] and initial_facts['receipt']
        and not initial_facts['old'] and initial_facts['new_mode'] == 0o755
        and not initial_facts['b1'] and not initial_facts['binding_directory']
        and s == initial_facts and len(receipts) == 2)
    if in_recovery:
        root_syncs = sum(r['alias'] == 'product' and r['path'] == '.' for r in rows[receipts[-1] + 1:])
        options.update(recovery_release_parent=path == release.parent,
            recovery_operation_parent=path == switch,
            recovery_new_parent=path == target and root_syncs == 0,
            recovery_old_parent=path == target and root_syncs == 1)
    return [name for name, yes in options.items() if yes]
def observe(alias, original):
    def sync(path):
        path = Path(path); s = facts(); names = matches(path, alias, s)
        for name in names: hits[name] = hits.get(name, 0) + 1
        row = {'path': path.relative_to(target).as_posix(), 'alias': alias, 'facts': s,
               'selectors': names, 'occurrences': {name: hits[name] for name in names}}
        rows.append(row)
        if request['selector'] in names and hits[request['selector']] == 1:
            injected.append({'index': len(rows) - 1, 'snapshot': tree(), 'facts': s})
            row['result'] = request['fault']
            if request['fault'] == 'oserror': raise OSError(errno.EIO, 'fixed D3 directory sync fault')
            return 'unavailable:' + str(errno.EINVAL)
        result = original(path); row['result'] = result; return result
    return sync
compare = product._entry_compare_local; comparisons = []
def change_truth(root, **kwargs):
    result = compare(root, **kwargs); comparisons.append(result)
    draft = {'record_type': 'intent-draft', 'schema_version': 1, 'authority_home_id': 'fixture-home',
        'intent_id': 'during-comparison', 'revision_id': 'during-draft', 'sequence': 1, 'prior_revision_ref': None,
        'actor': 'agent', 'acceptance_authority': 'owner', 'observed_at': '2026-01-01T00:00:00Z',
        'facets': {k: {'status': 'known', 'value': 'fixture'} for k in
            ('acceptance_oracle', 'destination', 'expected_outcome', 'forbidden_scope', 'goal', 'scope')},
        'gaps': [], 'statements': [], 'route': 'direct-entry'}
    # Synthetic non-cooperating file mutation while the real guard stays held.
    # Do not recursively invoke a writer or disable its guard.
    home = root / '.hrn/intents/during-comparison'
    home.mkdir(); (home / 'drafts').mkdir()
    identity = {'record_type': 'intent-identity', 'schema_version': 1,
                'authority_home_id': 'fixture-home', 'intent_id': 'during-comparison'}
    for path, value in ((home / 'identity.json', identity), (home / 'drafts/during-draft.json', draft)):
        with path.open('xb') as handle:
            handle.write(jsonio.canonical_json_bytes(value)); handle.flush(); os.fsync(handle.fileno())
    return result
if request['truth_change'] and (request['selector'] is not None or not request['recover']): raise RuntimeError('D3 truth seam only for clean replay')
# cli.main() receives parser arguments; the launcher alone consumes --source-checkout.
args = ['d3-fixed-cli', 'update', '--profile', 'entry-1', '--target', str(target),
        '--source', str(candidate), '--apply', '--input', '-', '--confirm', preview['confirm_token']]
if request['recover']: args.append('--recover')
output = io.StringIO(); errors = io.StringIO(); diagnostic = None
with contextlib.ExitStack() as stack:
    for name, module in (('product', product), ('workspace', workspace), ('jsonio', jsonio)):
        stack.enter_context(mock.patch.object(module, 'sync_directory', observe(name, module.sync_directory)))
    if request['truth_change']: stack.enter_context(mock.patch.object(product, '_entry_compare_local', change_truth))
    stack.enter_context(mock.patch.object(sys, 'argv', args))
    stack.enter_context(mock.patch.object(sys, 'stdin', io.TextIOWrapper(io.BytesIO(jsonio.canonical_json_bytes(plan)))))
    stack.enter_context(contextlib.redirect_stdout(output)); stack.enter_context(contextlib.redirect_stderr(errors))
    try:
        code = cli.main()
    except SystemExit as exc:
        code = exc.code if type(exc.code) is int else (0 if exc.code is None else 1)
        diagnostic = {'kind': 'unexpected-SystemExit', 'message': str(exc)}
cli_exit = code
try:
    parsed = json.loads(output.getvalue())
except json.JSONDecodeError as exc:
    parsed = None
    if diagnostic is None:
        diagnostic = {'kind': 'invalid-CLI-JSON', 'message': str(exc)}
        code = 70
if diagnostic is None and not isinstance(parsed, dict):
    diagnostic = {'kind': 'invalid-CLI-result-shape', 'message': type(parsed).__name__}
    code = 70
value = {'exit': code, 'cli_exit': cli_exit, 'diagnostic': diagnostic, 'stdout': output.getvalue(),
         'result': parsed, 'stderr': errors.getvalue(), 'rows': rows,
         'injected': injected, 'before': initial, 'after': tree(), 'comparisons': comparisons}
print(json.dumps(value, sort_keys=True, separators=(',', ':')))
raise SystemExit(code)
'''


def _validated_context(old_source, candidate_source, expected_predecessor, prefix_oracle, execution_context):
    need(isinstance(execution_context, MappingProxyType) and set(execution_context) == CONTEXT_FIELDS, 'readonly exact context required')
    ctx = dict(execution_context)
    need(type(ctx['schema']) is int and ctx['schema'] == 1 and ctx['phase'] == 'entry', 'context schema/phase')
    need(all(isinstance(ctx[k], str) for k in CONTEXT_FIELDS - {'schema', 'observer_command_prefix'}) and
         isinstance(ctx['observer_command_prefix'], tuple) and all(isinstance(x, str) for x in ctx['observer_command_prefix']), 'context types')
    import common
    import controller
    controls = common.unlinked_path(ctx['controls_dir'])
    need(Path(common.__file__) == controls / 'common.py' and Path(controller.__file__) == controls / 'controller.py', 'unverified control module')
    c, p = common.config(ctx['invocation_path'], ctx['invocation_sha256'])
    need(c['phase'] == 'entry' and c['factory'] is True, 'factory invocation phase')
    need(Path(old_source) == p['old'] and Path(candidate_source) == p['source'] and controls == p['controls'], 'factory source/context mismatch')
    need(expected_predecessor == common.read_json(controls / 'baseline-inputs.json') and
         prefix_oracle == common.read_json(controls / 'prefix-oracle.json'), 'factory control input mismatch')
    common.verify_old(p['old'], expected_predecessor)
    need(ctx['observer_sha256'] == c['controls']['observer.py'] and ctx['runtime_path'] == c['runtime']['path'] and
         ctx['runtime_sha256'] == c['runtime']['sha256'] and ctx['observer_command_prefix'] == tuple(common.python_command(c, p, 'observer.py')), 'derived context mismatch')
    work = common.unlinked_path(ctx['work_root'])
    need(work.is_dir() and work.name == 'work' and work.parent.name in controller.ENTRY_RUN_NAMES and
         work.parent.parent == p['exec'] / 'runs', 'factory WORK mismatch')
    need(tuple(expected_predecessor['literal_paths']['planning-1']) == OLD_PATHS and
         expected_predecessor['path_list_sha256']['planning-1'] == OLD_PATHS_SHA256, 'historical literal mismatch')
    need(tuple(item['id'] for item in prefix_oracle['steps']) == PREFIX_IDS, 'numbered prefix oracle mismatch')
    return MappingProxyType(ctx), c, p


def build_entry_suite(old_source, candidate_source, expected_predecessor, prefix_oracle, *, execution_context):
    """Read-only identification and pure suite construction. No fixture creation."""
    ctx, config, paths = _validated_context(old_source, candidate_source, expected_predecessor, prefix_oracle, execution_context)
    old_source, candidate_source, work_root = paths['old'], paths['source'], Path(ctx['work_root'])
    oracle = json.loads(canonical(prefix_oracle))  # Do not retain caller-owned mutable values.

    class FixtureBase(unittest.TestCase):
        COORDINATOR_SECONDS = 90

        def setUp(self):
            self.deadline = time.monotonic() + self.COORDINATOR_SECONDS
            self.base = work_root / self.__class__.__name__ / self._testMethodName
            self.base.mkdir(parents=True, exist_ok=False)
            self.children = []; self.serial = 0
            self.addCleanup(self.cleanup_children)

        def cleanup_children(self):
            errors = []
            for child in self.children:
                try:
                    if child.poll() is None:
                        child.terminate()
                        try: child.wait(timeout=3)
                        except subprocess.TimeoutExpired:
                            child.kill(); child.wait(timeout=3)
                    else:
                        child.wait()
                except Exception as exc:
                    errors.append((child.pid, type(exc).__name__, str(exc)))
            # Reaping a direct child does not prove grandchild/group absence.
            # Attempt every cleanup before reporting; the outer controller owns
            # process-group absence after this runner exits.
            self.assertEqual([], errors, 'one or more child cleanups failed')

        def remaining(self, maximum):
            value = min(maximum, self.deadline - time.monotonic())
            self.assertGreater(value, 0, 'coordinator deadline exhausted')
            return value

        def directory(self, name):
            p = self.base / name; p.mkdir(); return p

        def spawn(self, argv, label, value=None):
            self.serial += 1
            log = self.base / (str(self.serial) + '-' + label + '.log')
            # stdin is a pre-created bounded file, avoiding pipe deadlocks.
            input_path = self.base / (str(self.serial) + '-' + label + '.stdin')
            write_file(input_path, b'' if value is None else canonical(value))
            with input_path.open('rb') as input_file, log.open('xb') as output:
                child = subprocess.Popen(list(map(str, argv)), cwd=candidate_source,
                    stdin=input_file, stdout=output, stderr=subprocess.STDOUT)
            self.children.append(child)
            return child, log

        def finish(self, child, log, timeout=60, expected=0):
            try: code = child.wait(timeout=self.remaining(timeout))
            except subprocess.TimeoutExpired:
                child.terminate()
                try: child.wait(timeout=3)
                except subprocess.TimeoutExpired:
                    child.kill(); child.wait(timeout=3)
                self.fail('bounded child timed out; no automatic retry')
            self.assertLessEqual(log.stat().st_size, 1024 * 1024, 'child output exceeds fixture cap')
            data = log.read_bytes()
            if expected is not None:
                self.assertEqual(code, expected, data.decode(errors='replace')[-8000:])
            return code, data

        def fixed_old(self, target, detach=False):
            program = OLD_DETACH_PROGRAM if detach else OLD_INIT_PROGRAM
            child, log = self.spawn((ctx['runtime_path'], '-I', '-S', '-B', '-c', program, old_source, target), 'old-fixture')
            code, data = self.finish(child, log, timeout=90)
            value = json.loads(data)
            self.assertEqual('actual-old-schema2-prefix' if detach else 'actual-old-init', value['kind'])
            self.assertEqual((child.pid, os.getpgrp()), (value['pid'], value['pgid']))
            return value

        def scenario(self, target, entry='lock-prefix-canary', argv=(), fault=None, pause=True):
            self.serial += 1; tag = self.__class__.__name__ + '-' + self._testMethodName + '-' + str(self.serial)
            scenario_dir = work_root / 'entry-scenarios'; scenario_dir.mkdir(exist_ok=True)
            scenario = scenario_dir / (tag + '.json'); events = self.base / (tag + '.events')
            value = {'entry': entry, 'target': str(target), 'argv': list(map(str, argv)), 'events': str(events), 'fault': fault}
            ready, release = self.base / (tag + '.ready'), self.base / (tag + '.release')
            if pause:
                value['pause'] = {'event': 'lock-acquired', 'path': '.hrn/locks/writer.lock', 'occurrence': 1,
                    'ready': ready.relative_to(work_root).as_posix(), 'release': release.relative_to(work_root).as_posix(),
                    'timeout_seconds': 60 if self.COORDINATOR_SECONDS == 180 else 15}
            write_file(scenario, canonical(value))
            command = (*ctx['observer_command_prefix'], ctx['invocation_path'], ctx['invocation_sha256'], str(scenario), sha(canonical(value)))
            return command, events, ready, release, value

        def lock_target(self):
            target = self.directory('target'); (target / '.hrn/locks').mkdir(parents=True)
            write_file(target / '.hrn/locks/writer.lock', b'')
            return target

        def event_rows(self, events):
            raw = events.read_bytes()
            lines = raw.splitlines()
            if raw and not raw.endswith(b'\n'): lines = lines[:-1]
            rows = [json.loads(line) for line in lines]
            self.assertEqual(list(range(1, len(rows) + 1)), [r['seq'] for r in rows])
            self.assertTrue(all(r['pgid']==os.getpgrp() for r in rows), 'observer escaped controller group')
            return rows

        def wait_ready(self, child, ready, target):
            deadline = time.monotonic() + self.remaining(60 if self.COORDINATOR_SECONDS == 180 else 15)
            from common import regular, unlinked_path
            while True:
                self.assertIsNone(child.poll(), 'observer exited before ready')
                self.assertLess(time.monotonic(), deadline, 'ready deadline exceeded')
                if ready.exists():
                    before=unlinked_path(ready).stat();raw=regular(ready);after=ready.stat()
                    if (before.st_ino,before.st_size,before.st_mtime_ns,before.st_ctime_ns)==(after.st_ino,after.st_size,after.st_mtime_ns,after.st_ctime_ns):
                        try:value=json.loads(raw)
                        except (json.JSONDecodeError,UnicodeError):pass
                        else:break
                time.sleep(0.02)
            self.assertEqual(canonical(value), raw)
            self.assertEqual({'scenario_sha256','sequence','event','pid','pgid','lock','target'}, set(value))
            self.assertEqual(child.pid, value['pid']); self.assertEqual(os.getpgrp(), value['pgid'])
            self.assertEqual('lock-acquired', value['event'])
            lock_stat = (target / '.hrn/locks/writer.lock').stat(); target_stat = target.stat()
            self.assertEqual({'dev':lock_stat.st_dev,'ino':lock_stat.st_ino,'path':'.hrn/locks/writer.lock'}, value['lock'])
            self.assertEqual({'dev':target_stat.st_dev,'ino':target_stat.st_ino}, value['target'])
            return value

        def release_pause(self, release, token, wrong=False):
            write_file(release, canonical({'scenario_sha256': '0' * 64 if wrong else token['scenario_sha256'],
                'sequence': token['sequence'], 'action': 'continue'}))

        def assert_lock_free(self, target):
            with (target / '.hrn/locks/writer.lock').open('rb') as f:
                fcntl.flock(f.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
                fcntl.flock(f.fileno(), fcntl.LOCK_UN)

    class EntryControlTests(FixtureBase):

        def observer_dir_fd_probe(self, kind):
            target = self.directory('dirfd-target')
            write_file(target / 'payload.bin', b'fixed-dirfd-read\n')
            (target / 'nested').mkdir()
            write_file(target / 'nested/child.bin', b'nested-dirfd-read\n')
            if kind == 'paths': (target / 'link.bin').symlink_to('payload.bin')
            before = snapshot(target)
            fault = {'event': 'open-' + kind, 'path': 'payload.bin', 'occurrence': 1, 'write_bytes': None} if kind in ('before', 'after') else None
            command, events, _, _, _ = self.scenario(target, entry='new-source',
                argv=['--source-checkout', 'status', '--target', target], pause=False, fault=fault)
            child, log = self.spawn((ctx['runtime_path'], '-I', '-S', '-B', '-c', OBSERVER_DIRFD_PROBE_PROGRAM,
                paths['controls'], *command[-4:], kind), 'observer-dirfd')
            _, data = self.finish(child, log, timeout=60, expected=-signal.SIGKILL if fault else 0)
            self.assertEqual(before, snapshot(target)); rows = self.event_rows(events)
            if fault:
                self.assertNotIn(b'READ_COMPLETED', data)
                self.assertEqual('open-' + kind, rows[-1]['event']); self.assertEqual('payload.bin', rows[-1]['path'])
                self.assertEqual(1, sum(r['event'] == 'open-' + kind for r in rows))
            else:
                result = json.loads(data.splitlines()[-1]); self.assertEqual('probe-complete', result['status'])
                self.assertEqual((child.pid, os.getpgrp()), (result['pid'], result['pgid']))
            if kind == 'reads':
                expected = ['payload.bin'] * 3 + ['nested', 'nested/child.bin']
                for event in ('open-before', 'audit-before:open', 'open-after'):
                    self.assertEqual(expected, [r['path'] for r in rows if r['event'] == event])
                self.assertEqual([e for _ in expected for e in ('open-before', 'audit-before:open', 'open-after')], [r['event'] for r in rows])
            elif kind == 'mutation': self.assertEqual([], rows)
            elif kind == 'paths':
                self.assertEqual([('open-before', 'link.bin'), ('audit-before:open', 'link.bin')], [(r['event'], r['path']) for r in rows])

        def test_observer_dir_fd_read_paths(self):
            self.observer_dir_fd_probe('reads')

        def test_observer_dir_fd_rejects_relative_mutation(self):
            self.observer_dir_fd_probe('mutation')

        def test_observer_dir_fd_symlink_and_component_refusal(self):
            self.observer_dir_fd_probe('paths')

        def test_observer_dir_fd_fault_before(self):
            self.observer_dir_fd_probe('before')

        def test_observer_dir_fd_fault_after(self):
            self.observer_dir_fd_probe('after')


        def actual_runner_failfast_case(self, kind):
            out = self.directory('probe-output')
            child, log = self.spawn((ctx['runtime_path'], '-I', '-S', '-B', '-c', RUNNER_FAILFAST_PROBE_PROGRAM,
                paths['controls'], ctx['invocation_path'], ctx['invocation_sha256'], out, kind), 'runner-failfast')
            code, data = self.finish(child, log, timeout=60, expected=0 if kind == 'success' else 1)
            counts = json.loads((out / 'counts.json').read_bytes())
            self.assertEqual(2, counts['selected']); self.assertEqual(2, counts['discovered'])
            self.assertEqual(2 if kind == 'success' else 1, counts['run'])
            self.assertEqual(0 if kind == 'success' else 1, counts['unstarted'])
            for key in ('unfinished', 'skips', 'expected_failures', 'unexpected_successes'): self.assertEqual(0, counts[key], key)
            self.assertEqual(1 if kind in ('failure', 'subtest') else 0, counts['failures'])
            self.assertEqual(1 if kind == 'error' else 0, counts['errors'])
            rows = [json.loads(line) for line in (out / 'executed.jsonl').read_text().splitlines()]
            self.assertEqual(counts['run'], len(rows))
            expected = {'success': 'pass', 'failure': 'fail', 'error': 'error', 'subtest': 'subtest-failure'}[kind]
            self.assertEqual(expected, rows[0]['outcome'])
            self.assertTrue((out / 'cleanup-test_01_selected').is_file())
            self.assertEqual(kind == 'success', (out / 'second-test-started').exists())
            self.assertFalse((out / 'continued-after-subtest').exists())
            self.assertEqual([], json.loads((out / 'unfinished.json').read_bytes()))
            unstarted = json.loads((out / 'unstarted.json').read_bytes())
            self.assertEqual([] if kind == 'success' else [{'id': 'runner_failfast_probe.Probe.test_02_sentinel', 'occurrence': 1}], unstarted)
            if kind != 'success':
                self.assertIn(('EXPECTED_SYNTHETIC_' + kind.upper()).encode(), data)
                preserved = [json.loads(line) for line in (out / 'preservation.jsonl').read_text().splitlines()]
                self.assertEqual(1, len(preserved)); self.assertEqual('copied', preserved[0]['status'])
                self.assertEqual(b'fixed synthetic failure preservation\n', (Path(preserved[0]['copy']) / 'before.bin').read_bytes())
            else:
                self.assertTrue(all(r['outcome'] == 'pass' for r in rows))
                self.assertFalse((out / 'preservation.jsonl').exists())

        def test_actual_runner_failfast_error(self):
            self.actual_runner_failfast_case('error')

        def test_actual_runner_failfast_failure(self):
            self.actual_runner_failfast_case('failure')

        def test_actual_runner_failfast_subtest(self):
            self.actual_runner_failfast_case('subtest')

        def test_actual_runner_failfast_success_control(self):
            self.actual_runner_failfast_case('success')

        verification_stage = "p1-controls"
        def test_readonly_context_and_command_identity(self):
            with self.assertRaises(TypeError): ctx['phase'] = 'base'
            self.assertEqual(config['runtime']['path'], ctx['observer_command_prefix'][0])
            self.assertEqual(('-I','-S','-B','-c'), ctx['observer_command_prefix'][1:5])
            self.assertEqual((str(paths['controls']), 'observer.py'), ctx['observer_command_prefix'][-2:])
            for field, bad in (('phase','base'),('observer_sha256','0'*64),('runtime_sha256','0'*64),
                               ('work_root',str(work_root.parent)),('observer_command_prefix',('sh','-c','true'))):
                with self.subTest(field=field):
                    altered = dict(ctx); altered[field] = bad
                    with self.assertRaises(RuntimeError):
                        _validated_context(old_source, candidate_source, expected_predecessor, prefix_oracle, MappingProxyType(altered))

        def test_factory_construction_has_no_writes_or_processes(self):
            from unittest import mock
            before = snapshot(work_root, allow_hardlinks=True)
            with mock.patch.object(subprocess, 'Popen', side_effect=AssertionError('factory spawned process')), \
                 mock.patch.object(Path, 'mkdir', side_effect=AssertionError('factory created directory')), \
                 mock.patch.object(Path, 'write_bytes', side_effect=AssertionError('factory wrote bytes')):
                other = build_entry_suite(old_source, candidate_source, expected_predecessor, prefix_oracle, execution_context=ctx)
            self.assertGreater(other.countTestCases(), 0)
            self.assertEqual(before, snapshot(work_root, allow_hardlinks=True))
            import runner
            self.assertEqual([t.id() for t in runner.flatten(other)], [t.id() for t in runner.flatten(
                build_entry_suite(old_source,candidate_source,expected_predecessor,prefix_oracle,execution_context=ctx))])

        def test_control_imports_are_pure(self):
            child, log = self.spawn((ctx['runtime_path'],'-I','-S','-B','-c',IMPORT_PROBE_PROGRAM,paths['controls'],candidate_source), 'import-probe')
            _, data = self.finish(child, log)
            self.assertEqual(('CONTROL_IMPORT_PURE '+str(os.getpgrp())+'\n').encode(), data)

        def test_factory_membership_rejects_empty_overlap_and_duplicate(self):
            import runner
            class Probe(unittest.TestCase):
                def runTest(self): pass
            one = Probe()
            for suite, ordinary in ((unittest.TestSuite(), []), (unittest.TestSuite([one,one]), []),
                                    (unittest.TestSuite([one]), [one])):
                with self.assertRaises(RuntimeError): runner.factory_members(suite, ordinary)
            self.assertEqual([one], runner.factory_members(unittest.TestSuite([one]), []))

        def test_single_slot_allowlist(self):
            import controller
            self.assertEqual(controller.ENTRY_RUN_NAMES, frozenset(m+'-'+slot for m,slots in controller.ENTRY_MODE_SLOTS.items() for slot in slots))
            for mode, slots in controller.ENTRY_MODE_SLOTS.items():
                for slot in slots: controller.allowed(mode,slot,'entry')
            for args in (('focused','base','entry'),('collect','p1-controls','base'),('focused','p1-controls','unknown'),('shell','p1','entry')):
                with self.assertRaises(RuntimeError): controller.allowed(*args)

        def test_collection_phase_duplicate_contract(self):
            import controller
            current={'source_digest':'a'*64,'controls':{'runner.py':'b'*64},'phase':'entry'}
            prior={**current,'phase':'base'}
            controller.require_new_collection(current,prior)
            with self.assertRaisesRegex(RuntimeError,'already attempted'):
                controller.require_new_collection(current,dict(current))
            prior.pop('phase')
            with self.assertRaisesRegex(RuntimeError,'phase-less'):
                controller.require_new_collection(current,prior)

        def test_pause_shape_and_closed_timeout(self):
            target=self.lock_target()
            for invalid in (True,0,14,16,61):
                command,events,ready,release,value=self.scenario(target)
                value['pause']['timeout_seconds']=invalid
                scenario=Path(command[-2]);scenario.write_bytes(canonical(value));command=(*command[:-1],sha(canonical(value)))
                child,log=self.spawn(command,'pause-shape');code,data=self.finish(child,log,expected=None)
                self.assertNotEqual(0,code);self.assertIn(b'pause contract',data);self.assertFalse(events.exists())

        def test_file_and_fd_pause_selectors(self):
            target=self.lock_target()
            for selector in ('lock-canary','lock-fd-canary'):
                command,events,ready,release,value=self.scenario(target,entry=selector)
                child,log=self.spawn(command,'lock-operand');token=self.wait_ready(child,ready,target)
                self.release_pause(release,token);self.finish(child,log)
                rows=self.event_rows(events)
                self.assertEqual(['lock-attempt','lock-acquired'],[r['event'] for r in rows])
                self.assert_lock_free(target)

        def test_observer_rejects_cross_work_target(self):
            target = self.lock_target(); command,events,ready,release,value = self.scenario(target,pause=False)
            # Same EXEC but not this scenario's WORK, rejected before opening it.
            collection_slot = 'collect-p2' if work_root.parent.name == 'focused-p2' else 'collect-p1-controls'
            value['target'] = str(work_root.parent.parent / collection_slot / 'work')
            self.assertNotEqual(work_root,Path(value['target']))
            self.assertTrue(Path(value['target']).is_dir(), 'prior collect WORK is required for this negative control')
            scenario = Path(command[-2]); scenario.write_bytes(canonical(value)); command=(*command[:-1],sha(canonical(value)))
            child,log=self.spawn(command,'boundary-negative');code,data=self.finish(child,log,expected=None)
            self.assertNotEqual(0,code); self.assertIn(b'entry paths outside current WORK',data)
            self.assertFalse(events.exists()); self.assertFalse(ready.exists())
            self.assertFalse((target/'prefix-probe.bin').exists())

        def test_pause_resume_holds_real_lock(self):
            target=self.lock_target();command,events,ready,release,value=self.scenario(target)
            child,log=self.spawn(command,'pause');token=self.wait_ready(child,ready,target)
            self.assertEqual(command[-1],token['scenario_sha256'])
            with (target/'.hrn/locks/writer.lock').open('rb') as f:
                with self.assertRaises(BlockingIOError):fcntl.flock(f.fileno(),fcntl.LOCK_EX|fcntl.LOCK_NB)
            self.assertFalse((target/'prefix-probe.bin').exists())
            self.release_pause(release,token);self.finish(child,log)
            self.assertEqual(b'synthetic-prefix-only\n',(target/'prefix-probe.bin').read_bytes())
            rows=self.event_rows(events);lock=next(r['seq'] for r in rows if r['event']=='lock-acquired')
            self.assertTrue(all(r['seq']>lock for r in rows if r['path']=='prefix-probe.bin'))
            self.assertFalse(any('ready' in r['path'] or 'release' in r['path'] for r in rows))
            self.assert_lock_free(target)

        def _pause_fault(self, length):
            target=self.lock_target();fault={'event':'write-after','path':'prefix-probe.bin','occurrence':1,'write_bytes':length}
            command,events,ready,release,value=self.scenario(target,fault=fault)
            child,log=self.spawn(command,'pause-fault');token=self.wait_ready(child,ready,target)
            self.assertFalse((target/'prefix-probe.bin').exists());self.release_pause(release,token)
            self.finish(child,log,expected=-signal.SIGKILL)
            self.assertEqual(b'synthetic-prefix-only\n' if length is None else b's',(target/'prefix-probe.bin').read_bytes())
            rows=self.event_rows(events);self.assertEqual('write-after',rows[-1]['event'])
            self.assertEqual(child.pid,rows[-1]['pid']);self.assert_lock_free(target)

        def test_pause_then_after_write_kill(self): self._pause_fault(None)
        def test_pause_then_one_byte_short_write(self): self._pause_fault(1)

        def _pause_error(self, wrong):
            target=self.lock_target();command,events,ready,release,value=self.scenario(target)
            child,log=self.spawn(command,'pause-error');token=self.wait_ready(child,ready,target)
            if wrong:self.release_pause(release,token,wrong=True)
            code,data=self.finish(child,log,expected=None)
            self.assertNotEqual(0,code)
            self.assertIn(b'pause release token mismatch' if wrong else b'pause release timeout',data)
            self.assertFalse((target/'prefix-probe.bin').exists());self.assert_lock_free(target)

        def test_pause_wrong_token_refuses(self): self._pause_error(True)
        def test_pause_timeout_releases_lock(self): self._pause_error(False)

        def test_release_links_and_reused_paths_refuse(self):
            for kind in ('symlink','hardlink','existing'):
                target=self.directory('target-'+kind);(target/'.hrn/locks').mkdir(parents=True)
                write_file(target/'.hrn/locks/writer.lock',b'')
                command,events,ready,release,value=self.scenario(target)
                if kind=='existing':
                    write_file(release,b'preexisting')
                    child,log=self.spawn(command,'reuse-negative');code,data=self.finish(child,log,expected=None)
                    self.assertNotEqual(0,code);self.assertIn(b'pause paths must be exclusive',data)
                    self.assertFalse(events.exists());continue
                child,log=self.spawn(command,'link-negative');token=self.wait_ready(child,ready,target)
                backing=self.base/('release-backing-'+kind)
                write_file(backing,canonical({'scenario_sha256':token['scenario_sha256'],'sequence':token['sequence'],'action':'continue'}))
                if kind=='symlink':release.symlink_to(backing)
                else:os.link(backing,release)
                code,data=self.finish(child,log,expected=None)
                self.assertNotEqual(0,code)
                self.assertIn(b'linked path' if kind=='symlink' else b'handshake file kind/size',data)
                self.assertNotIn(b'pause release timeout',data)
                self.assertFalse((target/'prefix-probe.bin').exists());self.assert_lock_free(target)

        def primitive_target(self, name):
            target = self.directory(name)
            write_file(target/'hv2', b'synthetic-old-launcher\n')
            write_file(target/'.hrn/product/binding.json', b'synthetic-old-binding\n')
            (target/'.hrn/staging/entry-canary').mkdir(parents=True)
            return target

        def _primitive_fault_edges(self, operations):
            paths = {'open':'colvia', 'write':'colvia', 'fsync':'colvia', 'fchmod':'colvia',
                'unlink':'hv2', 'replace':'.hrn/product/binding.json', 'mkdir':'primitive-dir',
                'rename':'primitive-renamed', 'rmdir':'primitive-renamed', 'chmod':'primitive-dir'}
            for operation in operations:
                for edge in ('before', 'after'):
                    with self.subTest(operation=operation, edge=edge):
                        target = self.primitive_target(operation+'-'+edge)
                        event = operation+'-'+edge
                        fault = {'event':event, 'path':paths[operation], 'occurrence':1, 'write_bytes':None}
                        command,events,_,_,_ = self.scenario(target,entry='primitive-canary',fault=fault,pause=False)
                        child,log = self.spawn(command,'primitive-edge')
                        self.finish(child,log,expected=-signal.SIGKILL)
                        rows = self.event_rows(events)
                        self.assertEqual((event,paths[operation],child.pid),
                            (rows[-1]['event'],rows[-1]['path'],rows[-1]['pid']))
                        matched = [r['event'] for r in rows if r['path']==paths[operation] and
                                   r['event'] in {operation+'-before',operation+'-after'}]
                        self.assertEqual([operation+'-before'] + ([operation+'-after'] if edge=='after' else []),matched)
                        if operation=='open': self.assertEqual(edge=='after',(target/'colvia').exists())
                        elif operation=='write': self.assertEqual(b'' if edge=='before' else b'synthetic-launcher\n',(target/'colvia').read_bytes())
                        elif operation=='fchmod': self.assertEqual(0o600 if edge=='before' else 0o755,stat.S_IMODE((target/'colvia').stat().st_mode))
                        elif operation=='unlink': self.assertEqual(edge=='before',(target/'hv2').exists())
                        elif operation=='replace': self.assertEqual(b'synthetic-old-binding\n' if edge=='before' else b'{"synthetic": "B1"}\n',(target/'.hrn/product/binding.json').read_bytes())
                        elif operation=='mkdir': self.assertEqual(edge=='after',(target/'primitive-dir').exists())
                        elif operation=='rename':
                            self.assertEqual(edge=='before',(target/'primitive-dir').exists())
                            self.assertEqual(edge=='after',(target/'primitive-renamed').exists())
                        elif operation=='rmdir': self.assertEqual(edge=='before',(target/'primitive-renamed').exists())
                        elif operation=='chmod' and edge=='after': self.assertEqual(0o700,stat.S_IMODE((target/'primitive-dir').stat().st_mode))
                        # fsync traces establish call boundaries, never power-loss persistence.

        def test_primitive_file_fault_before_after(self):
            self._primitive_fault_edges(('open','write','fsync','fchmod','unlink'))

        def test_primitive_namespace_fault_before_after(self):
            self._primitive_fault_edges(('replace','mkdir','rename','rmdir','chmod'))

        def test_root_fsync_pause_and_fault_edges(self):
            for edge in ('before','after'):
                target=self.directory('root-'+edge);(target/'.hrn/locks').mkdir(parents=True)
                write_file(target/'.hrn/locks/writer.lock',b'')
                fault={'event':'fsync-'+edge,'path':'.','occurrence':1,'write_bytes':None}
                command,events,ready,release,_=self.scenario(target,fault=fault)
                child,log=self.spawn(command,'root-sync');token=self.wait_ready(child,ready,target)
                self.assertFalse((target/'prefix-probe.bin').exists());self.release_pause(release,token)
                self.finish(child,log,expected=-signal.SIGKILL)
                self.assertEqual(b'synthetic-prefix-only\n',(target/'prefix-probe.bin').read_bytes())
                rows=self.event_rows(events)
                self.assertEqual(('fsync-'+edge,'.'),(rows[-1]['event'],rows[-1]['path']))
                matched=[r['event'] for r in rows if r['path']=='.' and r['event'].startswith('fsync-')]
                self.assertEqual(['fsync-before']+(['fsync-after'] if edge=='after' else []),matched)
                self.assert_lock_free(target)

        def test_root_fault_rejects_other_events_and_unsafe_paths(self):
            target=self.lock_target()
            for event,path,message in (('open-before','.',b'root fault requires fsync'),
                    ('write-after','.',b'root fault requires fsync'),
                    ('fsync-before','../outside',b'unsafe input member')):
                fault={'event':event,'path':path,'occurrence':1,'write_bytes':None}
                command,events,ready,_,_=self.scenario(target,fault=fault)
                child,log=self.spawn(command,'root-negative');code,data=self.finish(child,log,expected=None)
                self.assertNotEqual(0,code);self.assertIn(message,data)
                self.assertFalse(events.exists());self.assertFalse(ready.exists())

        def test_pause_rejects_overlapping_or_target_handshakes(self):
            target=self.lock_target()
            for kind in ('same','inside-target'):
                command,events,ready,release,value=self.scenario(target)
                if kind=='same':value['pause']['release']=value['pause']['ready']
                else:value['pause']['ready']=(target/'ready').relative_to(work_root).as_posix()
                scenario=Path(command[-2]);scenario.write_bytes(canonical(value));command=(*command[:-1],sha(canonical(value)))
                child,log=self.spawn(command,'pause-path-negative');code,data=self.finish(child,log,expected=None)
                self.assertNotEqual(0,code);self.assertIn(b'pause paths',data)
                self.assertNotIn(b'must be exclusive',data)
                self.assertFalse(events.exists());self.assertFalse(ready.exists());self.assertFalse(release.exists())

        def test_unobserved_fault_is_not_success(self):
            target=self.primitive_target('unobserved')
            fault={'event':'fchmod-after','path':'colvia','occurrence':2,'write_bytes':None}
            command,events,_,_,_=self.scenario(target,entry='primitive-canary',fault=fault,pause=False)
            child,log=self.spawn(command,'unobserved-fault');code,data=self.finish(child,log,expected=None)
            self.assertNotEqual(0,code);self.assertIn(b'requested fault was not observed',data)
            self.assertEqual(1,sum(r['event']=='fchmod-after' and r['path']=='colvia' for r in self.event_rows(events)))

        def test_old_selectors_refuse_pause_and_fault(self):
            target=self.lock_target()
            for kind in ('pause','fault'):
                fault={'event':'write-after','path':'a','occurrence':1,'write_bytes':1} if kind=='fault' else None
                command,events,ready,release,value=self.scenario(target,entry='old-source',argv=('--source-checkout','status','--target',target),pause=kind=='pause',fault=fault)
                child,log=self.spawn(command,'old-negative');code,data=self.finish(child,log,expected=None)
                self.assertNotEqual(0,code);self.assertIn(b'no old-code fault substitution' if kind=='fault' else b'pause selector/phase',data)
                self.assertFalse(events.exists())

        def test_schema1_independent_inventory_binding_and_suffix(self):
            target=self.directory('schema1');fixture=schema1_fixture(target)
            self.assertEqual(29,len(fixture['inventory']['entries']))
            self.assertEqual(OLD_PATHS,tuple(e['path'] for e in fixture['inventory']['entries']))
            self.assertEqual('planning-1',fixture['inventory']['inventory_id'])
            self.assertEqual(ref(fixture['binding'],'operation_id'),fixture['receipt']['prior_binding_ref'])
            self.assertEqual(1,fixture['receipt']['schema_version']);self.assertEqual(1,fixture['plan']['schema_version'])
            self.assertEqual('hv2',fixture['remove_order'][0])
            self.assertEqual(sorted([e['path'] for e in fixture['plan']['remove'] if e['path']!='hv2'],key=lambda n:n.encode()),fixture['remove_order'][1:])
            before=snapshot(target)
            for entry in fixture['plan']['remove']+fixture['plan']['preserve']:
                data=(target/entry['path']).read_bytes();self.assertEqual((entry['sha256'],entry['size_bytes']),(sha(data),len(data)))
            self.assertEqual(before,snapshot(target))
            # Removal-order construction is independent; reader validation is P2.
            for path in fixture['remove_order'][:2]:(target/path).unlink()
            self.assertEqual(fixture['remove_order'][2:],[n for n in fixture['remove_order'] if (target/n).exists()])

        def test_numbered_oracle_and_closed_pause_contract(self):
            self.assertEqual(PREFIX_IDS,tuple(x['id'] for x in oracle['steps']))
            contract=oracle['control_contract'];self.assertEqual([15,60],contract['pause_timeout_seconds'])
            self.assertEqual((60,90,90,120,150,180,1200),tuple(contract[k] for k in
                ('synthetic_child_seconds','synthetic_coordinator_seconds','old_fixture_child_seconds','old_fixture_coordinator_seconds','product_child_seconds','product_coordinator_seconds','focused_seconds')))
            self.assertIn('new executor',oracle['late_lock']['required'][1])
            self.assertNotIn('parent demonstrably holds',canonical(oracle).decode())

    class OldFixtureTests(FixtureBase):
        verification_stage = "p1-controls"
        COORDINATOR_SECONDS=120
        def test_actual_old_schema2_prefix(self):
            target=self.directory('target');result=self.fixed_old(target,detach=True)
            self.assertEqual(result['before'],{k:v for k,v in result['after'].items() if k!='.hrn/detached.json'})
            self.assertEqual(result['receipt'],json.loads((target/'.hrn/detached.json').read_bytes()))
            self.assertEqual(2,result['receipt']['schema_version']);self.assertEqual(2,result['receipt']['plan']['schema_version'])
            self.assertEqual(result['binding_ref'],result['receipt']['plan']['expected_binding_ref'])

    # Product tests deliberately fail on checkout-1. They are not P1a controls,
    # must not be selected for p1-controls, and receive real product assertions.
    class EntryProductTests(FixtureBase):
        verification_stage = "p2"
        COORDINATOR_SECONDS=180

        def product(self):
            import hv2ref.product as product
            self.assertEqual(candidate_source/'src/hv2ref/product.py',Path(product.__file__))
            self.assertEqual('entry-1',product.workspace_candidate(candidate_source)['inventory']['inventory_id'])
            return product

        def call(self,target,argv,value=None,entry='new-source',fault=None,pause=False):
            command,events,ready,release,scenario=self.scenario(target,entry=entry,argv=argv,fault=fault,pause=pause)
            child,log=self.spawn(command,'product',value)
            if pause:return child,log,events,ready,release,command
            code,data=self.finish(child,log,timeout=150,expected=None)
            return code,data,events

        def new_init(self,target):
            product=self.product()
            preview=product.workspace_init_preview(candidate_source,target,authority_home_id='fixture-home',operation_id='entry-init',created_at=FIXTURE_TIME)
            result=product.workspace_init_apply(candidate_source,target,preview['request'],confirm_token=preview['confirm_token'])
            self.assertEqual('entry-1',product.verify_workspace_product(target)['inventory']['inventory_id'])
            return preview,result

        def old_target(self,name='target'):
            target=self.directory(name);self.fixed_old(target);return target

        def transition(self,target):
            product=self.product();preview=product.workspace_switch_preview(target,action='update',source=candidate_source,operation_id='entry-transition',created_at=FIXTURE_TIME)
            self.assertEqual(2,preview['request']['schema_version'])
            return preview

        def apply_args(self,target,preview,recover=False):
            return ['--source-checkout','update','--profile','entry-1','--target',str(target),'--source',str(candidate_source),
                '--apply','--input','-','--confirm',preview['confirm_token'],*(['--recover'] if recover else [])]

        def test_current_candidate_uses_entry_membership(self):
            product=self.product();candidate=product.workspace_candidate(candidate_source)
            expected=tuple(sorted((set(OLD_PATHS)-{'hv2','adapters/harness-v2-work/SKILL.md'})|{'colvia','adapters/colvia-work/SKILL.md'},key=lambda n:n.encode()))
            self.assertEqual(expected,tuple(e['path'] for e in candidate['inventory']['entries']))
            self.assertEqual(OLD_PATHS,product.SERIAL_MANAGED_PATHS)

        def test_fresh_init_collision_before_any_write(self):
            product=self.product()
            positive=self.directory('positive');self.new_init(positive)
            for index,(name,kind) in enumerate((('hv2','file'),('HV2','file'),('hv2','directory'),('hv2','dangling-link'))):
                target=self.directory('negative-'+str(index)+'-'+kind+'-'+name)
                if kind=='file':write_file(target/name,b'project-owned\n')
                elif kind=='directory':(target/name).mkdir()
                else:(target/name).symlink_to('missing-project-content')
                before=snapshot(target)
                code,data,_=self.call(target,['--source-checkout','init','--profile','entry-1','--target',target,'--source',candidate_source,
                    '--authority-home-id','fixture-home','--operation-id','entry-init','--observed-at',FIXTURE_TIME])
                self.assertEqual(65,code,data);self.assertIn(b'HV2-WORKSPACE-PRODUCT',data);self.assertEqual(before,snapshot(target))

        def test_live_collision_diagnostics_and_lifecycle_preservation(self):
            target=self.directory('target');self.new_init(target)
            code,data,_=self.call(target,['--source-checkout','status','--target',target]);self.assertEqual(0,code,data)
            write_file(target/'hv2',b'project-owned retired name\n');before=snapshot(target)
            for command in ('status','doctor'):
                code,data,_=self.call(target,['--source-checkout',command,'--target',target]);self.assertEqual(12,code,data)
                state=json.loads(data);self.assertEqual('conflict',state['classification']);self.assertIs(state['lifecycle_ready'],False)
                self.assertEqual(['hv2'],state['retired_entry_collision']['observed_names'])
                self.assertEqual(before,snapshot(target))
            code,data,_=self.call(target,['--source-checkout','detach','--profile','entry-1','--target',target,'--operation-id','blocked-detach','--observed-at',FIXTURE_TIME])
            self.assertEqual(65,code,data);self.assertIn(b'HV2-WORKSPACE-PRODUCT',data);self.assertEqual(before,snapshot(target))

        def test_old_detach_readers_and_new_writer_refusal(self):
            product=self.product()
            for version in (1,2):
                target=self.directory('schema'+str(version))
                if version==1:schema1_fixture(target)
                else:self.fixed_old(target,detach=True)
                before=snapshot(target);state=product.workspace_detached_status(target)
                self.assertEqual('partial',state['classification'])
                plan=state['receipt']['plan'];token=sha(canonical(plan))[:16]
                from hv2ref.errors import ContractError
                for recover in (False,True):
                    with self.assertRaises(ContractError):product.workspace_detach_apply(target,plan,confirm_token=token,recover=recover)
                self.assertEqual(before,snapshot(target))

        def test_schema1_reader_rejects_mixed_and_malformed_receipts(self):
            product=self.product();target=self.directory('schema1');fixture=schema1_fixture(target)
            path=target/'.hrn/detached.json';raw=path.read_bytes()
            self.assertEqual('partial',product.workspace_detached_status(target)['classification'])
            from hv2ref.errors import ContractError
            bad_values=[]
            for outer,inner in ((1,3),(2,1),(3,1),(True,True),(4,4)):
                value=copy.deepcopy(fixture['receipt']);value['schema_version']=outer;value['plan']['schema_version']=inner;bad_values.append(value)
            for mutate in ('digest','member','suffix','new-entry'):
                value=copy.deepcopy(fixture['receipt'])
                if mutate=='digest':value['plan']['remove'][0]['sha256']='0'*64
                elif mutate=='member':value['plan']['remove']=value['plan']['remove'][1:]
                elif mutate=='suffix':value['plan']['remove'].reverse()
                else:
                    item=next(x for x in value['plan']['remove'] if x['path']=='hv2');item['path']='colvia'
                bad_values.append(value)
            for number,value in enumerate(bad_values):
                with self.subTest(number=number):
                    path.write_bytes(canonical(value));before=snapshot(target)
                    with self.assertRaises(ContractError):product.workspace_detached_status(target)
                    self.assertEqual(before,snapshot(target))
            path.write_bytes(raw)
            # A non-prefix removal cannot be blessed as a valid suffix.
            victim=fixture['remove_order'][2];(target/victim).unlink();before=snapshot(target)
            with self.assertRaises(ContractError):product.workspace_detached_status(target)
            self.assertEqual(before,snapshot(target))

        def test_source_operation_matrix(self):
            self.product();old=self.old_target('old');new=self.directory('new');self.new_init(new)
            for selector,source,profile,label in (('new-source',old_source,'entry-1','new-rejects-old-init'),
                                                  ('old-source',candidate_source,'checkout-1','old-rejects-entry-init')):
                target=self.directory(label);before=snapshot(target)
                args=['--source-checkout','init','--profile',profile,'--target',target,'--source',source,
                      '--authority-home-id','fixture-home','--operation-id','matrix-init','--observed-at',FIXTURE_TIME]
                code,data,_=self.call(target,args,entry=selector)
                failure=json.loads(data)
                if selector=='new-source':
                    self.assertEqual(65,code,data);self.assertEqual('HV2-WORKSPACE-PRODUCT',failure['code'])
                    self.assertEqual('candidate managed bytes unavailable; preserve source and target',failure['message'])
                else:
                    # Exact retained OLD encounters the absent old adapter first.
                    # Preserve its historical missing-member failure; this is not
                    # an entry-window fence or a newly stable Product refusal.
                    self.assertEqual(70,code,data);self.assertEqual('HV2-INTERNAL',failure['code'])
                    self.assertEqual('FileNotFoundError',failure['exception_type'])
                self.assertEqual(before,snapshot(target))
            before=snapshot(old)
            for command in ('rollback','repair','detach'):
                args=['--source-checkout',command,'--target',old,'--operation-id','matrix-'+command,'--observed-at',FIXTURE_TIME]
                if command!='repair':args+=['--profile','entry-1']
                else:args+=['--source',candidate_source,'--backup',self.base/'repair-backup']
                code,data,_=self.call(old,args)
                self.assertEqual(65,code,data);self.assertIn(b'HV2-WORKSPACE-PRODUCT',data)
                self.assertEqual(before,snapshot(old))
            before=snapshot(new)
            code,data,_=self.call(new,['--source-checkout','detach','--profile','checkout-1','--target',new,'--operation-id','wrong-profile','--observed-at',FIXTURE_TIME])
            # A parser choice refusal and an explicit profile ContractError are
            # distinct preexisting paths. Neither is a lifecycle refusal claim.
            if code==2:
                self.assertIn(b'invalid choice',data);self.assertIn(b'checkout-1',data)
            else:
                self.assertEqual(65,code,data);self.assertIn(b'HV2-WORKSPACE-COMMAND',data)
            self.assertEqual(before,snapshot(new))

        def transition_prefix_case(self, event, path, length):
            product=self.product();candidate=product.workspace_candidate(candidate_source)
            target=self.old_target();preview=self.transition(target)
            truth=(target/'a').read_bytes();fmt=(target/'.hrn/format.json').read_bytes()
            fault={'event':event,'path':path,'occurrence':1,'write_bytes':length}
            code,data,events=self.call(target,self.apply_args(target,preview),preview['request'],fault=fault)
            self.assertEqual(-signal.SIGKILL,code,data)
            rows=self.event_rows(events);self.assertEqual((event,path),(rows[-1]['event'],rows[-1]['path']))
            self.assertEqual(truth,(target/'a').read_bytes());self.assertEqual(fmt,(target/'.hrn/format.json').read_bytes())
            code,data,_=self.call(target,self.apply_args(target,preview,recover=True),preview['request'])
            self.assertEqual(0,code,data)
            self.assertFalse((target/'hv2').exists());self.assertEqual(candidate['payload']['colvia'],(target/'colvia').read_bytes())
            self.assertEqual(0o755,stat.S_IMODE((target/'colvia').stat().st_mode))
            self.assertEqual('entry-1',product.verify_workspace_product(target)['inventory']['inventory_id'])
            self.assertEqual(truth,(target/'a').read_bytes());self.assertEqual(fmt,(target/'.hrn/format.json').read_bytes())

        def test_transition_prefix_01_recovers(self):
            self.transition_prefix_case('open-after', 'colvia', None)

        def test_transition_prefix_02_recovers(self):
            self.transition_prefix_case('write-after', 'colvia', 1)

        def test_transition_prefix_03_recovers(self):
            self.transition_prefix_case('write-after', 'colvia', None)

        def test_transition_prefix_04_recovers(self):
            self.transition_prefix_case('fsync-after', 'colvia', None)

        def test_transition_prefix_05_recovers(self):
            self.transition_prefix_case('fchmod-after', 'colvia', None)

        def test_transition_prefix_06_recovers(self):
            self.transition_prefix_case('unlink-after', 'hv2', None)

        def test_transition_prefix_07_recovers(self):
            self.transition_prefix_case('open-after', '.hrn/staging/entry-entry-transition/binding.next', None)

        def test_transition_prefix_08_recovers(self):
            self.transition_prefix_case('write-after', '.hrn/staging/entry-entry-transition/binding.next', 1)

        def test_transition_prefix_09_recovers(self):
            self.transition_prefix_case('replace-after', '.hrn/product/binding.json', None)


        def binding_prefix_case(self, stop, short=None):
            """Instrumented S5 publication kill, then one exact recovery or replay.

            The fixed events witness Python calls, not power-loss durability.
            Expected binding/receipt bytes are assembled from the public shape,
            independently of product binding construction and prefix readers.
            """
            operation = '.hrn/staging/entry-entry-transition'
            member = operation + '/binding.next'
            published = '.hrn/product/binding.json'
            # event, target-relative path, global occurrence, directory, member, B1
            flow = (
                ('mkdir-before', '.hrn/staging', 1, False, None, False),
                ('fsync-before', '.hrn', 3, False, None, False),
                ('fsync-after', '.hrn', 3, False, None, False),
                ('fsync-before', '.hrn/staging', 2, False, None, False),
                ('fsync-after', '.hrn/staging', 2, False, None, False),
                ('mkdir-before', '.hrn/staging/entry-entry-transition', 1, False, None, False),
                ('mkdir-after', '.hrn/staging/entry-entry-transition', 1, True, None, False),
                ('fsync-before', '.hrn/staging', 3, True, None, False),
                ('fsync-after', '.hrn/staging', 3, True, None, False),
                ('fsync-before', '.hrn/staging/entry-entry-transition', 1, True, None, False),
                ('fsync-after', '.hrn/staging/entry-entry-transition', 1, True, None, False),
                ('open-before', '.hrn/staging/entry-entry-transition/binding.next', 1, True, None, False),
                ('open-after', '.hrn/staging/entry-entry-transition/binding.next', 1, True, 'zero', False),
                ('write-before', '.hrn/staging/entry-entry-transition/binding.next', 1, True, 'zero', False),
                ('write-after', '.hrn/staging/entry-entry-transition/binding.next', 1, True, 'full', False),
                ('fsync-before', '.hrn/staging/entry-entry-transition/binding.next', 1, True, 'full', False),
                ('fsync-after', '.hrn/staging/entry-entry-transition/binding.next', 1, True, 'full', False),
                ('fsync-before', '.hrn/staging/entry-entry-transition', 2, True, 'full', False),
                ('fsync-after', '.hrn/staging/entry-entry-transition', 2, True, 'full', False),
                ('replace-before', '.hrn/product/binding.json', 1, True, 'full', False),
                ('replace-after', '.hrn/product/binding.json', 1, True, None, True),
                ('fsync-before', '.hrn/product', 2, True, None, True),
                ('fsync-after', '.hrn/product', 2, True, None, True),
                ('fsync-before', '.hrn/staging/entry-entry-transition', 3, True, None, True),
                ('fsync-after', '.hrn/staging/entry-entry-transition', 3, True, None, True),
            )
            self.assertIn(stop, range(len(flow)))
            event, path, occurrence, directory, content, committed = flow[stop]
            self.assertIn(short, (None, 'one', 'middle', 'last'))
            if short is not None:
                self.assertEqual(('write-after', member, 'full'), (event, path, content))
            product = self.product(); candidate = product.workspace_candidate(candidate_source)
            target = self.old_target(); preview = self.transition(target)
            request_bytes = canonical(preview['request'])
            token = preview['confirm_token']; candidate_ref = copy.deepcopy(candidate['release_ref'])
            b0 = (target / published).read_bytes(); prior = json.loads(b0)
            b1_value = {'record_type': 'product-binding', 'schema_version': 1,
                'authority_home_id': prior['authority_home_id'], 'active_release': candidate_ref,
                'prior_release': prior['active_release'], 'operation_id': 'entry-transition'}
            b1 = canonical(b1_value)
            receipt_value = {'record_type': 'lifecycle-receipt', 'schema_version': 2,
                'operation_id': 'entry-transition', 'plan': preview['request'],
                'prior_binding_ref': ref(prior, 'operation_id'), 'result_binding_ref': ref(b1_value, 'operation_id')}
            self.assertEqual(ref(prior, 'operation_id'), preview['request']['expected_binding_ref'])
            # This fixture has empty typed truth; exact absence is preserved too.
            self.assertEqual([], preview['request']['truth_refs'])
            initial = snapshot(target)
            self.interrupted_api(target, preview, 'after-launcher')
            s5 = snapshot(target)
            self.assertFalse((target / operation).exists())
            self.assertFalse((target / 'hv2').exists())
            self.assertEqual(b0, (target / published).read_bytes())
            self.assertEqual(candidate['payload']['colvia'], (target / 'colvia').read_bytes())
            self.assertEqual(0o755, stat.S_IMODE((target / 'colvia').stat().st_mode))
            self.assertEqual(canonical(receipt_value), (target / '.hrn/product/receipts/entry-transition.json').read_bytes())
            for name, value in initial.items():
                if name != 'hv2':
                    self.assertEqual(value, s5[name], name)
            release = target / '.hrn/product/releases' / candidate_ref['id']
            self.assertEqual(candidate_ref, product.verify_workspace_release(release)['release_ref'])
            length = None if short is None else {'one': 1, 'middle': len(b1) // 2, 'last': len(b1) - 1}[short]
            if length is not None: self.assertTrue(0 < length < len(b1))
            fault = {'event': event, 'path': path, 'occurrence': occurrence, 'write_bytes': length}
            code, data, events = self.call(target, self.apply_args(target, preview, recover=True), preview['request'], fault=fault)
            self.assertEqual(-signal.SIGKILL, code, data)
            self.assertTrue(events.read_bytes().endswith(b'\n'), 'incomplete last witness')
            rows = self.event_rows(events)
            matches = [r for r in rows if (r['event'], r['path']) == (event, path)]
            self.assertEqual(occurrence, len(matches))
            self.assertEqual(rows[-1], matches[-1])
            self.assertEqual(self.children[-1].pid, rows[-1]['pid'])
            self.assertTrue(all(r['pid'] == rows[-1]['pid'] for r in rows))
            starts = [i for i, r in enumerate(rows) if (r['event'], r['path']) == ('mkdir-before', '.hrn/staging')]
            self.assertEqual(1, len(starts))
            keys = {(r[0], r[1]) for r in flow}
            witnessed = [r for r in rows[starts[0]:] if (r['event'], r['path']) in keys and
                (not r['event'].startswith('open-') or r['detail']['flags'] & os.O_CREAT)]
            self.assertEqual([(r[0], r[1]) for r in flow[:stop + 1]], [(r['event'], r['path']) for r in witnessed])
            for r in witnessed:
                if r['event'].startswith('open-'):
                    self.assertEqual({'flags': os.O_RDWR | os.O_NOFOLLOW | os.O_CREAT | os.O_EXCL, 'mode': 0o600}, r['detail'])
                if r['event'] == 'write-before': self.assertEqual({'requested': len(b1)}, r['detail'])
                if r['event'] == 'write-after': self.assertEqual({'written': len(b1) if length is None else length}, r['detail'])
                if r['event'].startswith('replace-'): self.assertEqual({'from': member}, r['detail'])
            expected = dict(s5)
            if directory: expected[operation] = ('directory', 0o755)
            if content is not None:
                prefix = b'' if content == 'zero' else b1[:length] if length is not None else b1
                expected[member] = ('file', 0o600, len(prefix), sha(prefix))
                self.assertEqual(prefix, (target / member).read_bytes())
            if committed: expected[published] = ('file', 0o600, len(b1), sha(b1))
            self.assertEqual(expected, snapshot(target), 'exact killed prefix including all preserved members')
            self.assert_lock_free(target)
            self.assertEqual(request_bytes, canonical(preview['request']))
            self.assertEqual(token, preview['confirm_token'])
            self.assertEqual(candidate_ref, product.workspace_candidate(candidate_source)['release_ref'])
            # Exactly one follow-up: recover B0, replay B1 without --recover.
            code, data, _ = self.call(target, self.apply_args(target, preview, recover=not committed), preview['request'])
            self.assertEqual(0, code, data)
            result = json.loads(data)
            self.assertEqual('replayed' if committed else 'updated', result['classification'])
            self.assertEqual(ref(b1_value, 'operation_id'), result['product']['binding_ref'])
            self.assertEqual({'classification': 'not-applicable', 'work_ids': [],
                'reason': 'no unfinished selected local Work'}, result['transition_content_verification'])
            completed = dict(s5)
            completed[operation] = ('directory', 0o755)
            completed[published] = ('file', 0o600, len(b1), sha(b1))
            self.assertEqual(completed, snapshot(target), 'only exact B1 and empty deterministic staging may remain')
            self.assertFalse((target / member).exists())
            self.assertFalse((target / 'hv2').exists())
            self.assertEqual(b1, (target / published).read_bytes())
            self.assertEqual(ref(b1_value, 'operation_id'), product.verify_workspace_product(target)['binding_ref'])
            self.assertEqual(completed, snapshot(target), 'read-only verification mutated fixture')

        def test_binding_b01_staging_mkdir_before(self):
            self.binding_prefix_case(0)

        def test_binding_b01_staging_parent_sync_before(self):
            self.binding_prefix_case(1)

        def test_binding_b01_staging_parent_sync_after(self):
            self.binding_prefix_case(2)

        def test_binding_b01_staging_self_sync_before(self):
            self.binding_prefix_case(3)

        def test_binding_b01_staging_self_sync_after(self):
            self.binding_prefix_case(4)

        def test_binding_b01_operation_mkdir_before(self):
            self.binding_prefix_case(5)

        def test_binding_b01_operation_mkdir_after(self):
            self.binding_prefix_case(6)

        def test_binding_b01_operation_parent_sync_before(self):
            self.binding_prefix_case(7)

        def test_binding_b01_operation_parent_sync_after(self):
            self.binding_prefix_case(8)

        def test_binding_b01_operation_self_sync_before(self):
            self.binding_prefix_case(9)

        def test_binding_b01_operation_self_sync_after(self):
            self.binding_prefix_case(10)

        def test_binding_b02_next_open_before(self):
            self.binding_prefix_case(11)

        def test_binding_b02_next_open_after(self):
            self.binding_prefix_case(12)

        def test_binding_b03_next_write_before(self):
            self.binding_prefix_case(13)

        def test_binding_b03_next_write_full(self):
            self.binding_prefix_case(14)

        def test_binding_b03_next_write_one(self):
            self.binding_prefix_case(14, 'one')

        def test_binding_b03_next_write_middle(self):
            self.binding_prefix_case(14, 'middle')

        def test_binding_b03_next_write_last(self):
            self.binding_prefix_case(14, 'last')

        def test_binding_b04_next_file_sync_before(self):
            self.binding_prefix_case(15)

        def test_binding_b04_next_file_sync_after(self):
            self.binding_prefix_case(16)

        def test_binding_b04_next_parent_sync_before(self):
            self.binding_prefix_case(17)

        def test_binding_b04_next_parent_sync_after(self):
            self.binding_prefix_case(18)

        def test_binding_b05_replace_before(self):
            self.binding_prefix_case(19)

        def test_binding_b05_replace_after(self):
            self.binding_prefix_case(20)

        def test_binding_b06_binding_parent_sync_before(self):
            self.binding_prefix_case(21)

        def test_binding_b06_binding_parent_sync_after(self):
            self.binding_prefix_case(22)

        def test_binding_b06_operation_parent_sync_before(self):
            self.binding_prefix_case(23)

        def test_binding_b06_operation_parent_sync_after(self):
            self.binding_prefix_case(24)

        def launcher_prefix_case(self, stop, short=None):
            """S3 named-seam preparation, observed N/O kill, then one recovery.

            Literal record shapes and exact fixture snapshots constrain expected
            changes; candidate payload/ref and preview request are product-derived.
            Observed Python call edges do not prove power-loss durability.
            """
            operation = '.hrn/staging/entry-entry-transition'
            published = '.hrn/product/binding.json'
            # event, target-relative path, global occurrence, N content/mode, O
            flow = (
                ('open-before', 'colvia', 1, None, None, True),
                ('open-after', 'colvia', 1, 'zero', 384, True),
                ('write-before', 'colvia', 1, 'zero', 384, True),
                ('write-after', 'colvia', 1, 'full', 384, True),
                ('fsync-before', 'colvia', 1, 'full', 384, True),
                ('fsync-after', 'colvia', 1, 'full', 384, True),
                ('fchmod-before', 'colvia', 1, 'full', 384, True),
                ('fchmod-after', 'colvia', 1, 'full', 493, True),
                ('fsync-before', 'colvia', 2, 'full', 493, True),
                ('fsync-after', 'colvia', 2, 'full', 493, True),
                ('fsync-before', '.', 2, 'full', 493, True),
                ('fsync-after', '.', 2, 'full', 493, True),
                ('unlink-before', 'hv2', 1, 'full', 493, True),
                ('unlink-after', 'hv2', 1, 'full', 493, False),
                ('fsync-before', '.', 3, 'full', 493, False),
                ('fsync-after', '.', 3, 'full', 493, False),
            )
            self.assertIn(stop, range(len(flow)))
            event, path, occurrence, content, mode, old_present = flow[stop]
            self.assertIn(short, (None, 'one', 'middle', 'last'))
            if short is not None:
                self.assertEqual(('write-after', 'colvia', 'full'), (event, path, content))
            product = self.product(); candidate = product.workspace_candidate(candidate_source)
            target = self.old_target(); preview = self.transition(target)
            request_bytes = canonical(preview['request']); token = preview['confirm_token']
            candidate_ref = copy.deepcopy(candidate['release_ref']); launcher = candidate['payload']['colvia']
            b0 = (target / published).read_bytes(); prior = json.loads(b0)
            b1_value = {'record_type': 'product-binding', 'schema_version': 1,
                'authority_home_id': prior['authority_home_id'], 'active_release': candidate_ref,
                'prior_release': prior['active_release'], 'operation_id': 'entry-transition'}
            b1 = canonical(b1_value)
            receipt_value = {'record_type': 'lifecycle-receipt', 'schema_version': 2,
                'operation_id': 'entry-transition', 'plan': preview['request'],
                'prior_binding_ref': ref(prior, 'operation_id'), 'result_binding_ref': ref(b1_value, 'operation_id')}
            self.assertEqual(ref(prior, 'operation_id'), preview['request']['expected_binding_ref'])
            self.assertEqual([], preview['request']['truth_refs'])
            initial = snapshot(target); root_mode = stat.S_IMODE(target.stat().st_mode)
            old_bytes = (target / 'hv2').read_bytes()
            self.assertEqual(('file', 0o755, len(old_bytes), sha(old_bytes)), initial['hv2'])
            self.assertNotIn('colvia', initial)
            release_name = '.hrn/product/releases/' + candidate_ref['id']
            self.assertNotIn(release_name, initial)
            # Enumerate the complete allowed S3 delta instead of blessing any
            # additions merely because the named preparation seam made them.
            s3 = dict(initial)
            s3['.hrn/staging/switch-entry-transition'] = ('directory', 0o755)
            new_files = {release_name + '/inventory.json': canonical(candidate['inventory']),
                '.hrn/product/receipts/entry-transition.json': canonical(receipt_value)}
            new_files.update({release_name + '/payload/' + n: b for n, b in candidate['payload'].items()})
            for name, value in new_files.items():
                self.assertNotIn(name, initial)
                for parent in Path(name).parents:
                    if str(parent) != '.':
                        s3.setdefault(parent.as_posix(), ('directory', 0o755))
                s3[name] = ('file', 0o644, len(value), sha(value))
            self.interrupted_api(target, preview, 'after-release')
            self.assertEqual(s3, snapshot(target), 'exact S3 preparation delta')
            self.assertEqual(root_mode, stat.S_IMODE(target.stat().st_mode))
            self.assertFalse((target / operation).exists())
            self.assertEqual(b0, (target / published).read_bytes())
            self.assertEqual(candidate_ref, product.verify_workspace_release(target / release_name)['release_ref'])
            self.assertEqual(s3, snapshot(target), 'release verification changed S3')
            length = None if short is None else {'one': 1, 'middle': len(launcher) // 2, 'last': len(launcher) - 1}[short]
            if length is not None: self.assertTrue(0 < length < len(launcher))
            fault = {'event': event, 'path': path, 'occurrence': occurrence, 'write_bytes': length}
            code, data, events = self.call(target, self.apply_args(target, preview, recover=True), preview['request'], fault=fault)
            self.assertEqual(-signal.SIGKILL, code, data)
            self.assertTrue(events.read_bytes().endswith(b'\n'), 'incomplete last witness')
            rows = self.event_rows(events)
            matches = [r for r in rows if (r['event'], r['path']) == (event, path)]
            self.assertEqual(occurrence, len(matches)); self.assertEqual(rows[-1], matches[-1])
            self.assertEqual(self.children[-1].pid, rows[-1]['pid'])
            self.assertTrue(all(r['pid'] == rows[-1]['pid'] for r in rows))
            starts = [i for i, r in enumerate(rows) if (r['event'], r['path']) == ('open-before', 'colvia')
                and r['detail']['flags'] & os.O_CREAT]
            self.assertEqual(1, len(starts))
            keys = {(r[0], r[1]) for r in flow}; seen = {}; witnessed = []
            for index, row in enumerate(rows):
                key = (row['event'], row['path']); seen[key] = seen.get(key, 0) + 1
                if index >= starts[0] and key in keys and (not row['event'].startswith('open-') or row['detail']['flags'] & os.O_CREAT):
                    witnessed.append((row, seen[key]))
            self.assertEqual([r[:3] for r in flow[:stop + 1]],
                [(r['event'], r['path'], number) for r, number in witnessed])
            for row, _ in witnessed:
                if row['event'].startswith('open-'):
                    self.assertEqual({'flags': os.O_RDWR | os.O_NOFOLLOW | os.O_CREAT | os.O_EXCL, 'mode': 0o600}, row['detail'])
                if row['event'] == 'write-before': self.assertEqual({'requested': len(launcher)}, row['detail'])
                if row['event'] == 'write-after': self.assertEqual({'written': len(launcher) if length is None else length}, row['detail'])
                if row['event'].startswith('fchmod-'): self.assertEqual({'mode': 0o755}, row['detail'])
            expected = dict(s3)
            if content is not None:
                prefix = b'' if content == 'zero' else launcher[:length] if length is not None else launcher
                expected['colvia'] = ('file', mode, len(prefix), sha(prefix))
                self.assertEqual(prefix, (target / 'colvia').read_bytes())
            if old_present: self.assertEqual(old_bytes, (target / 'hv2').read_bytes())
            else: del expected['hv2']
            self.assertEqual(expected, snapshot(target), 'exact killed prefix and B0 preservation')
            self.assertEqual(root_mode, stat.S_IMODE(target.stat().st_mode))
            self.assertEqual(b0, (target / published).read_bytes()); self.assert_lock_free(target)
            self.assertEqual(request_bytes, canonical(preview['request'])); self.assertEqual(token, preview['confirm_token'])
            self.assertEqual(candidate_ref, product.workspace_candidate(candidate_source)['release_ref'])
            # B0 holds for every N/O edge: exactly one identical explicit recovery.
            code, data, _ = self.call(target, self.apply_args(target, preview, recover=True), preview['request'])
            self.assertEqual(0, code, data); result = json.loads(data)
            self.assertEqual('updated', result['classification'])
            self.assertEqual(ref(b1_value, 'operation_id'), result['product']['binding_ref'])
            self.assertEqual({'classification': 'not-applicable', 'work_ids': [],
                'reason': 'no unfinished selected local Work'}, result['transition_content_verification'])
            completed = dict(s3); del completed['hv2']
            completed['colvia'] = ('file', 0o755, len(launcher), sha(launcher))
            completed[operation] = ('directory', 0o755)
            completed[published] = ('file', 0o600, len(b1), sha(b1))
            self.assertEqual(completed, snapshot(target), 'only exact launcher, B1 and empty binding staging may change')
            self.assertFalse((target / (operation + '/binding.next')).exists())
            self.assertFalse((target / 'hv2').exists()); self.assertEqual(b1, (target / published).read_bytes())
            self.assertEqual(root_mode, stat.S_IMODE(target.stat().st_mode))
            self.assertEqual(ref(b1_value, 'operation_id'), product.verify_workspace_product(target)['binding_ref'])
            self.assertEqual(completed, snapshot(target), 'read-only verification mutated fixture')

        def test_launcher_n01_open_before(self):
            self.launcher_prefix_case(0)

        def test_launcher_n01_open_after(self):
            self.launcher_prefix_case(1)

        def test_launcher_n02_write_before(self):
            self.launcher_prefix_case(2)

        def test_launcher_n02_write_full(self):
            self.launcher_prefix_case(3)

        def test_launcher_n02_write_one(self):
            self.launcher_prefix_case(3, 'one')

        def test_launcher_n02_write_middle(self):
            self.launcher_prefix_case(3, 'middle')

        def test_launcher_n02_write_last(self):
            self.launcher_prefix_case(3, 'last')

        def test_launcher_n03_file_sync_before(self):
            self.launcher_prefix_case(4)

        def test_launcher_n03_file_sync_after(self):
            self.launcher_prefix_case(5)

        def test_launcher_n04_chmod_before(self):
            self.launcher_prefix_case(6)

        def test_launcher_n04_chmod_after(self):
            self.launcher_prefix_case(7)

        def test_launcher_n05_file_sync_before(self):
            self.launcher_prefix_case(8)

        def test_launcher_n05_file_sync_after(self):
            self.launcher_prefix_case(9)

        def test_launcher_n05_root_sync_before(self):
            self.launcher_prefix_case(10)

        def test_launcher_n05_root_sync_after(self):
            self.launcher_prefix_case(11)

        def test_launcher_o01_unlink_before(self):
            self.launcher_prefix_case(12)

        def test_launcher_o01_unlink_after(self):
            self.launcher_prefix_case(13)

        def test_launcher_o02_root_sync_before(self):
            self.launcher_prefix_case(14)

        def test_launcher_o02_root_sync_after(self):
            self.launcher_prefix_case(15)

        def release_publication_case(self, stop):
            """Complete S2 named seam, observed S3 call edge, one recovery.

            Expected record shapes/deltas are assembled here. Candidate payload,
            release identity and preview request remain product-derived inputs.
            Python call-edge observations do not qualify power-loss durability.
            """
            self.assertIn(stop, range(6))
            product = self.product(); candidate = product.workspace_candidate(candidate_source)
            target = self.old_target(); preview = self.transition(target)
            request_bytes = canonical(preview['request']); token = preview['confirm_token']
            candidate_ref = copy.deepcopy(candidate['release_ref']); launcher = candidate['payload']['colvia']
            operation = '.hrn/staging/switch-entry-transition'
            staged = operation + '/' + candidate_ref['id']
            release = '.hrn/product/releases/' + candidate_ref['id']
            binding_stage = '.hrn/staging/entry-entry-transition'
            published = '.hrn/product/binding.json'
            b0 = (target / published).read_bytes(); prior = json.loads(b0)
            b1_value = {'record_type': 'product-binding', 'schema_version': 1,
                'authority_home_id': prior['authority_home_id'], 'active_release': candidate_ref,
                'prior_release': prior['active_release'], 'operation_id': 'entry-transition'}
            b1 = canonical(b1_value)
            receipt_value = {'record_type': 'lifecycle-receipt', 'schema_version': 2,
                'operation_id': 'entry-transition', 'plan': preview['request'],
                'prior_binding_ref': ref(prior, 'operation_id'), 'result_binding_ref': ref(b1_value, 'operation_id')}
            self.assertEqual(ref(prior, 'operation_id'), preview['request']['expected_binding_ref'])
            self.assertEqual([], preview['request']['truth_refs'])
            initial = snapshot(target); root_mode = stat.S_IMODE(target.stat().st_mode)
            old_bytes = (target / 'hv2').read_bytes()
            self.assertEqual(('file', 0o755, len(old_bytes), sha(old_bytes)), initial['hv2'])
            for name in ('colvia', operation, release, binding_stage): self.assertNotIn(name, initial)
            # One inventory plus 29 payload members. Every member iteration
            # revisits staged root; its parent is the switch operation directory.
            members = {'inventory.json': canonical(candidate['inventory'])}
            members.update({'payload/' + n: b for n, b in candidate['payload'].items()})
            self.assertEqual(30, len(members))
            s2 = dict(initial)
            new_files = {staged + '/' + n: b for n, b in members.items()}
            new_files['.hrn/product/receipts/entry-transition.json'] = canonical(receipt_value)
            for name, value in new_files.items():
                self.assertNotIn(name, initial)
                for parent in Path(name).parents:
                    if str(parent) != '.': s2.setdefault(parent.as_posix(), ('directory', 0o755))
                s2[name] = ('file', 0o644, len(value), sha(value))
            self.interrupted_api(target, preview, 'after-staged-payload')
            self.assertEqual(s2, snapshot(target), 'exact complete S2 preparation delta')
            self.assertEqual(root_mode, stat.S_IMODE(target.stat().st_mode))
            self.assertEqual(b0, (target / published).read_bytes())
            self.assertFalse((target / release).exists()); self.assertFalse((target / 'colvia').exists())
            self.assertEqual(candidate_ref, product.verify_workspace_release(target / staged)['release_ref'])
            self.assertEqual(s2, snapshot(target), 'staged release verification changed S2')
            s3 = dict(s2)
            for name in tuple(s2):
                if name == staged or name.startswith(staged + '/'):
                    s3[release + name[len(staged):]] = s3.pop(name)
            self.assertEqual(('directory', 0o755), s3[operation])
            # Global counts for recovery from complete S2: releases admission1
            # then publication2. Operation admission1 + durable(operation)1 +
            # durable(staged)1 + 30 member-root revisits = 33, publication34.
            flow = (
                ('rename-before', release, 1),
                ('rename-after', release, 1),
                ('fsync-before', '.hrn/product/releases', 2),
                ('fsync-after', '.hrn/product/releases', 2),
                ('fsync-before', operation, 34),
                ('fsync-after', operation, 34),
            )
            event, path, occurrence = flow[stop]
            fault = {'event': event, 'path': path, 'occurrence': occurrence, 'write_bytes': None}
            code, data, events = self.call(target, self.apply_args(target, preview, recover=True), preview['request'], fault=fault)
            self.assertEqual(-signal.SIGKILL, code, data)
            self.assertTrue(events.read_bytes().endswith(b'\n'), 'incomplete last witness')
            rows = self.event_rows(events)
            matches = [r for r in rows if (r['event'], r['path']) == (event, path)]
            self.assertEqual(occurrence, len(matches)); self.assertEqual(rows[-1], matches[-1])
            self.assertEqual(self.children[-1].pid, rows[-1]['pid'])
            self.assertTrue(all(r['pid'] == rows[-1]['pid'] for r in rows))
            starts = [i for i, r in enumerate(rows) if (r['event'], r['path']) == ('rename-before', release)]
            self.assertEqual(1, len(starts))
            keys = {(e, p) for e, p, _ in flow}; seen = {}; witnessed = []
            for index, row in enumerate(rows):
                key = (row['event'], row['path']); seen[key] = seen.get(key, 0) + 1
                if index >= starts[0] and key in keys: witnessed.append((row, seen[key]))
            self.assertEqual(list(flow[:stop + 1]), [(r['event'], r['path'], n) for r, n in witnessed])
            for row, _ in witnessed:
                self.assertEqual({'from': staged} if row['event'].startswith('rename-') else None, row['detail'])
            expected = s2 if stop == 0 else s3
            self.assertEqual(expected, snapshot(target), 'exact S3 killed namespace and B0 preservation')
            self.assertEqual(root_mode, stat.S_IMODE(target.stat().st_mode))
            self.assertEqual(b0, (target / published).read_bytes())
            self.assertEqual(old_bytes, (target / 'hv2').read_bytes())
            self.assertFalse((target / 'colvia').exists()); self.assert_lock_free(target)
            self.assertEqual(request_bytes, canonical(preview['request'])); self.assertEqual(token, preview['confirm_token'])
            self.assertEqual(candidate_ref, product.workspace_candidate(candidate_source)['release_ref'])
            # No request changes and exactly one explicit recovery after the kill.
            code, data, _ = self.call(target, self.apply_args(target, preview, recover=True), preview['request'])
            self.assertEqual(0, code, data); result = json.loads(data)
            self.assertEqual('updated', result['classification'])
            self.assertEqual(ref(b1_value, 'operation_id'), result['product']['binding_ref'])
            self.assertEqual({'classification': 'not-applicable', 'work_ids': [],
                'reason': 'no unfinished selected local Work'}, result['transition_content_verification'])
            completed = dict(s3); del completed['hv2']
            completed['colvia'] = ('file', 0o755, len(launcher), sha(launcher))
            completed[binding_stage] = ('directory', 0o755)
            completed[published] = ('file', 0o600, len(b1), sha(b1))
            self.assertEqual(completed, snapshot(target), 'only exact publication, launcher and binding deltas')
            self.assertFalse((target / staged).exists()); self.assertFalse((target / 'hv2').exists())
            self.assertFalse((target / (binding_stage + '/binding.next')).exists())
            self.assertEqual(b1, (target / published).read_bytes())
            self.assertEqual(root_mode, stat.S_IMODE(target.stat().st_mode))
            self.assertEqual(candidate_ref, product.verify_workspace_release(target / release)['release_ref'])
            self.assertEqual(ref(b1_value, 'operation_id'), product.verify_workspace_product(target)['binding_ref'])
            self.assertEqual(completed, snapshot(target), 'read-only verification mutated fixture')

        def test_release_s3_rename_before(self):
            self.release_publication_case(0)

        def test_release_s3_rename_after(self):
            self.release_publication_case(1)

        def test_release_s3_release_sync_before(self):
            self.release_publication_case(2)

        def test_release_s3_release_sync_after(self):
            self.release_publication_case(3)

        def test_release_s3_operation_sync_before(self):
            self.release_publication_case(4)

        def test_release_s3_operation_sync_after(self):
            self.release_publication_case(5)

        def release_sync_failure_case(self, selector, fault):
            """Complete S2, one simulated publication sync failure, one recovery.

            Expected record shapes/deltas are test-local; payload/ref/request
            remain product-derived. D3 rows witness sync calls and snapshots,
            not every write syscall or power-loss persistence.
            """
            import errno
            self.assertIn(selector, ('release_parent', 'release_operation_parent'))
            self.assertIn(fault, ('unavailable', 'oserror'))
            product = self.product(); candidate = product.workspace_candidate(candidate_source)
            target = self.old_target(); preview = self.transition(target)
            request_bytes = canonical(preview['request']); token = preview['confirm_token']
            candidate_ref = copy.deepcopy(candidate['release_ref']); launcher = candidate['payload']['colvia']
            operation = '.hrn/staging/switch-entry-transition'
            staged = operation + '/' + candidate_ref['id']
            release = '.hrn/product/releases/' + candidate_ref['id']
            binding_stage = '.hrn/staging/entry-entry-transition'
            published = '.hrn/product/binding.json'
            b0 = (target / published).read_bytes(); prior = json.loads(b0)
            b1_value = {'record_type': 'product-binding', 'schema_version': 1,
                'authority_home_id': prior['authority_home_id'], 'active_release': candidate_ref,
                'prior_release': prior['active_release'], 'operation_id': 'entry-transition'}
            b1 = canonical(b1_value)
            receipt_value = {'record_type': 'lifecycle-receipt', 'schema_version': 2,
                'operation_id': 'entry-transition', 'plan': preview['request'],
                'prior_binding_ref': ref(prior, 'operation_id'), 'result_binding_ref': ref(b1_value, 'operation_id')}
            self.assertEqual(ref(prior, 'operation_id'), preview['request']['expected_binding_ref'])
            self.assertEqual([], preview['request']['truth_refs'])
            initial = snapshot(target); root_mode = stat.S_IMODE(target.stat().st_mode)
            old_bytes = (target / 'hv2').read_bytes()
            self.assertEqual(('file', 0o755, len(old_bytes), sha(old_bytes)), initial['hv2'])
            for name in ('colvia', operation, release, binding_stage): self.assertNotIn(name, initial)
            # One inventory plus 29 payload members. Every member iteration
            # revisits staged root; its parent is the switch operation directory.
            members = {'inventory.json': canonical(candidate['inventory'])}
            members.update({'payload/' + n: b for n, b in candidate['payload'].items()})
            self.assertEqual(30, len(members))
            s2 = dict(initial)
            new_files = {staged + '/' + n: b for n, b in members.items()}
            new_files['.hrn/product/receipts/entry-transition.json'] = canonical(receipt_value)
            for name, value in new_files.items():
                self.assertNotIn(name, initial)
                for parent in Path(name).parents:
                    if str(parent) != '.': s2.setdefault(parent.as_posix(), ('directory', 0o755))
                s2[name] = ('file', 0o644, len(value), sha(value))
            self.interrupted_api(target, preview, 'after-staged-payload')
            self.assertEqual(s2, snapshot(target), 'exact complete S2 preparation delta')
            self.assertEqual(root_mode, stat.S_IMODE(target.stat().st_mode))
            self.assertEqual(b0, (target / published).read_bytes())
            self.assertFalse((target / release).exists()); self.assertFalse((target / 'colvia').exists())
            self.assertEqual(candidate_ref, product.verify_workspace_release(target / staged)['release_ref'])
            self.assertEqual(s2, snapshot(target), 'staged release verification changed S2')
            s3 = dict(s2)
            for name in tuple(s2):
                if name == staged or name.startswith(staged + '/'):
                    s3[release + name[len(staged):]] = s3.pop(name)
            self.assertEqual(('directory', 0o755), s3[operation])
            expected_s2 = json.loads(json.dumps(s2))
            expected_s3 = json.loads(json.dumps(s3))
            result = self.d3_run(target, preview, recover=True, selector=selector, fault=fault)
            self.assertEqual(65, result['exit'])
            self.assertEqual('HV2-WORKSPACE-PRODUCT', result['result']['code'])
            role = selector.replace('_', '-')
            detail = 'unavailable:' + str(errno.EINVAL) if fault == 'unavailable' else 'oserror:' + str(errno.EIO)
            self.assertEqual('d3-sync:publication:' + role + '; directory synchronization ' + detail +
                '; B1 publication observed=no; current product verification=not-requested; '
                'preserve receipt, prefix and binding; use the exact admitted retry or separately authorized disposition',
                result['result']['message'])
            self.assertEqual(expected_s2, result['before'])
            self.assertEqual(1, len(result['injected']))
            injection = result['injected'][0]; rows = result['rows']; index = injection['index']
            self.assertEqual(len(rows) - 1, index, 'sync sequence advanced after failure')
            row = rows[index]
            self.assertEqual('product', row['alias'])
            self.assertEqual('.hrn/product/releases' if selector == 'release_parent' else operation, row['path'])
            self.assertEqual([selector], row['selectors']); self.assertEqual({selector: 1}, row['occurrences'])
            self.assertEqual(fault, row['result'])
            self.assertTrue(all(r['result'] == 'pass' for r in rows[:index]))
            expected_facts = {'receipt': True, 'staged': False, 'inventory': False, 'release': True,
                'old': True, 'new_mode': None, 'binding_directory': False, 'next_size': None, 'b1': False}
            self.assertEqual(expected_facts, injection['facts']); self.assertEqual(expected_facts, row['facts'])
            # Match one is after rename, not S2 admission: no earlier row had this selector.
            self.assertFalse(any(selector in r['selectors'] for r in rows[:index]))
            publication_rows = [r for r in rows if 'release_parent' in r['selectors'] or 'release_operation_parent' in r['selectors']]
            expected_roles = ['release_parent'] if selector == 'release_parent' else ['release_parent', 'release_operation_parent']
            self.assertEqual(expected_roles, [r['selectors'][0] for r in publication_rows])
            self.assertEqual(expected_s3, injection['snapshot'])
            self.assertEqual(injection['snapshot'], result['after'], 'end snapshot differs from failed-sync snapshot')
            self.assertEqual(s3, snapshot(target)); self.assertEqual(root_mode, stat.S_IMODE(target.stat().st_mode))
            self.assertEqual(b0, (target / published).read_bytes()); self.assertEqual(old_bytes, (target / 'hv2').read_bytes())
            self.assertFalse((target / 'colvia').exists()); self.assert_lock_free(target)
            self.assertEqual(request_bytes, canonical(preview['request'])); self.assertEqual(token, preview['confirm_token'])
            self.assertEqual(candidate_ref, product.workspace_candidate(candidate_source)['release_ref'])
            # One explicit no-fault recovery of the exact same request; no candidate correction.
            recovered = self.d3_run(target, preview, recover=True)
            self.assertEqual(0, recovered['exit']); self.assertEqual([], recovered['injected'])
            self.assertEqual(expected_s3, recovered['before'])
            self.assertEqual('updated', recovered['result']['classification'])
            self.assertTrue(all(r['result'] == 'pass' for r in recovered['rows']))
            syncs = [r for r in recovered['rows'] if r['alias'] == 'product' and not r['facts']['b1']]
            receipt_syncs = [j for j, r in enumerate(syncs) if r['path'] == '.hrn/product/receipts']
            self.assertEqual(2, len(receipt_syncs), 'admission and existing-receipt synchronization')
            last_receipt = receipt_syncs[-1]
            first_new = next(j for j, r in enumerate(syncs) if r['facts']['new_mode'] is not None)
            required = (release, '.hrn/product/releases', operation)
            positions = []
            for name in required:
                matches = [j for j, r in enumerate(syncs) if last_receipt < j < first_new and r['path'] == name]
                self.assertEqual(1, len(matches), name)
                positions.append(matches[0]); facts = syncs[matches[0]]['facts']
                self.assertTrue(facts['old']); self.assertIsNone(facts['new_mode']); self.assertFalse(facts['b1'])
            self.assertEqual(sorted(positions), positions)
            self.assertEqual(ref(b1_value, 'operation_id'), recovered['result']['product']['binding_ref'])
            self.assertEqual({'classification': 'not-applicable', 'work_ids': [],
                'reason': 'no unfinished selected local Work'}, recovered['result']['transition_content_verification'])
            completed = dict(s3); del completed['hv2']
            completed['colvia'] = ('file', 0o755, len(launcher), sha(launcher))
            completed[binding_stage] = ('directory', 0o755)
            completed[published] = ('file', 0o600, len(b1), sha(b1))
            self.assertEqual(json.loads(json.dumps(completed)), recovered['after'])
            self.assertEqual(completed, snapshot(target)); self.assertEqual(root_mode, stat.S_IMODE(target.stat().st_mode))
            self.assertFalse((target / staged).exists()); self.assertFalse((target / 'hv2').exists())
            self.assertFalse((target / (binding_stage + '/binding.next')).exists())
            self.assertEqual(b1, (target / published).read_bytes())
            self.assertEqual(request_bytes, canonical(preview['request'])); self.assertEqual(token, preview['confirm_token'])
            self.assertEqual(candidate_ref, product.verify_workspace_release(target / release)['release_ref'])
            self.assertEqual(ref(b1_value, 'operation_id'), product.verify_workspace_product(target)['binding_ref'])
            self.assertEqual(completed, snapshot(target), 'read-only verification mutated fixture')

        def test_release_s3_sync_failure_release_parent_unavailable(self):
            self.release_sync_failure_case('release_parent', 'unavailable')

        def test_release_s3_sync_failure_release_parent_oserror(self):
            self.release_sync_failure_case('release_parent', 'oserror')

        def test_release_s3_sync_failure_release_operation_parent_unavailable(self):
            self.release_sync_failure_case('release_operation_parent', 'unavailable')

        def test_release_s3_sync_failure_release_operation_parent_oserror(self):
            self.release_sync_failure_case('release_operation_parent', 'oserror')

        def interrupted_api(self,target,preview,point):
            # Existing named product seam is labelled separately from observer kill.
            from hv2ref.errors import InjectedCrash
            with self.assertRaises(InjectedCrash) as caught:
                self.product().workspace_switch_apply(target,preview['request'],confirm_token=preview['confirm_token'],
                    source=candidate_source,inject_at=point)
            self.assertEqual(point,caught.exception.point)
            self.assertEqual('HV2-INJECTED-CRASH',caught.exception.code)

        def test_synthetic_receipt_tears_are_preserved_refusals(self):
            for label in ('zero','one','middle','last'):
                target=self.old_target('receipt-'+label);preview=self.transition(target)
                self.interrupted_api(target,preview,'after-receipt')
                receipt=target/'.hrn/product/receipts/entry-transition.json';full=receipt.read_bytes()
                value=json.loads(full);self.assertEqual(2,value['schema_version']);self.assertEqual(2,value['plan']['schema_version'])
                length={'zero':0,'one':1,'middle':len(full)//2,'last':len(full)-1}[label]
                receipt.write_bytes(full[:length]);before=snapshot(target)
                code,data,_=self.call(target,self.apply_args(target,preview,recover=True),preview['request'])
                self.assertEqual(65,code,data)
                self.assertIn(json.loads(data)['code'],('HV2-JSON-EOF','HV2-JSON-SYNTAX','HV2-JSON-NONCANONICAL'))
                self.assertEqual(before,snapshot(target));self.assertEqual(full[:length],receipt.read_bytes())

        def test_synthetic_staging_tears_are_preserved_refusals(self):
            candidate=self.product().workspace_candidate(candidate_source)
            for member in ('inventory.json','payload/colvia'):
                for label in ('zero','one','middle','last'):
                    target=self.old_target('stage-'+member.replace('/','-')+'-'+label);preview=self.transition(target)
                    self.interrupted_api(target,preview,'after-staged-payload')
                    # Existing deterministic switch staging, derived only from the reviewed plan.
                    staged=target/'.hrn/staging'/('switch-'+preview['request']['operation_id'])/candidate['release_ref']['id']
                    path=staged/member;full=path.read_bytes()
                    self.assertEqual(canonical(candidate['inventory']) if member=='inventory.json' else candidate['payload']['colvia'],full)
                    length={'zero':0,'one':1,'middle':len(full)//2,'last':len(full)-1}[label]
                    path.write_bytes(full[:length]);before=snapshot(target)
                    code,data,_=self.call(target,self.apply_args(target,preview,recover=True),preview['request'])
                    self.assertEqual(65,code,data);failure=json.loads(data)
                    self.assertEqual('HV2-WORKSPACE-PRODUCT',failure['code'])
                    self.assertEqual('torn or changed init bytes: '+member,failure['message'])
                    self.assertEqual(before,snapshot(target));self.assertEqual(full[:length],path.read_bytes())

        def test_late_new_entry_collision_needs_explicit_operator_relocation(self):
            target=self.old_target();preview=self.transition(target)
            self.interrupted_api(target,preview,'after-release')
            collision=b'synthetic operator-owned entry\n';write_file(target/'colvia',collision)
            before=snapshot(target)
            code,data,_=self.call(target,self.apply_args(target,preview,recover=True),preview['request'])
            self.assertEqual(65,code,data);self.assertIn(b'HV2-WORKSPACE-PRODUCT',data);self.assertEqual(before,snapshot(target))
            # Explicit synthetic operator action: retain the exact conflicting bytes outside target.
            relocated=self.base/'operator-retained-colvia';(target/'colvia').rename(relocated)
            self.assertEqual(collision,relocated.read_bytes())
            code,data,_=self.call(target,self.apply_args(target,preview,recover=True),preview['request'])
            self.assertEqual(0,code,data);self.assertEqual('entry-1',self.product().verify_workspace_product(target)['inventory']['inventory_id'])
            self.assertEqual(collision,relocated.read_bytes())

        def test_unsupported_umask_refuses_before_receipt(self):
            from hv2ref.errors import ContractError
            target=self.old_target();preview=self.transition(target);before=snapshot(target)
            previous=os.umask(0o777)
            try:
                with self.assertRaises(ContractError) as caught:
                    self.product().workspace_switch_apply(target,preview['request'],confirm_token=preview['confirm_token'],source=candidate_source)
            finally:os.umask(previous)
            self.assertEqual('HV2-WORKSPACE-PRODUCT',caught.exception.code)
            self.assertIn('umask',caught.exception.message.lower())
            self.assertEqual(before,snapshot(target));self.assertFalse((target/'.hrn/product/receipts/entry-transition.json').exists())

        def test_entry_detach_schema3_positive_and_mixed_rejection(self):
            from hv2ref.errors import ContractError,InjectedCrash
            product=self.product();target=self.directory('target');self.new_init(target)
            preview=product.workspace_detach_preview(target,operation_id='entry-detach',created_at=FIXTURE_TIME)
            self.assertEqual(3,preview['request']['schema_version'])
            with self.assertRaises(InjectedCrash) as caught:
                product.workspace_detach_apply(target,preview['request'],confirm_token=preview['confirm_token'],inject_at='after-receipt')
            self.assertEqual('after-receipt',caught.exception.point)
            path=target/'.hrn/detached.json';raw=path.read_bytes();receipt=json.loads(raw)
            self.assertEqual(3,receipt['schema_version']);self.assertEqual('partial',product.workspace_detached_status(target)['classification'])
            for outer,inner in ((3,1),(3,2),(2,3),(True,True),(4,4)):
                bad=copy.deepcopy(receipt);bad['schema_version']=outer;bad['plan']['schema_version']=inner
                path.write_bytes(canonical(bad));before=snapshot(target)
                with self.assertRaises(ContractError):product.workspace_detached_status(target)
                self.assertEqual(before,snapshot(target))
            path.write_bytes(raw)
            product.workspace_detach_apply(target,preview['request'],confirm_token=preview['confirm_token'],recover=True)
            self.assertEqual('detached',product.workspace_detached_status(target)['classification'])
            self.assertFalse((target/'colvia').exists());self.assertFalse((target/'hv2').exists())

        def test_new_executor_pause_then_old_lock_attempt(self):
            target=self.old_target();preview=self.transition(target)
            old_args=['--source-checkout','detach','--profile','checkout-1','--target',target,'--operation-id','late-old-detach','--observed-at',FIXTURE_TIME]
            # Old preview is a positive on S0, but only apply takes writer_guard.
            code,data,_=self.call(target,old_args,entry='old-source');self.assertEqual(0,code,data);old_preview=json.loads(data)
            apply_old=['--source-checkout','detach','--profile','checkout-1','--target',target,'--apply','--input','-','--confirm',old_preview['confirm_token']]
            # Separate S0 target exercises the same OLD apply and lock witness.
            positive=self.old_target('positive');code,data,_=self.call(positive,[*old_args[:5],positive,*old_args[6:]],entry='old-source')
            self.assertEqual(0,code,data);positive_preview=json.loads(data)
            positive_apply=['--source-checkout','detach','--profile','checkout-1','--target',positive,'--apply','--input','-','--confirm',positive_preview['confirm_token']]
            code,data,ev=self.call(positive,positive_apply,positive_preview['request'],entry='old-source');self.assertEqual(0,code,data)
            self.assertTrue({'lock-attempt','lock-acquired'}<={r['event'] for r in self.event_rows(ev)})
            initial=snapshot(target);prior=json.loads((target/'.hrn/product/binding.json').read_bytes())
            plan=preview['request']
            result_binding={'record_type':'product-binding','schema_version':1,'authority_home_id':plan['authority_home_id'],
                'active_release':plan['candidate_release'],'prior_release':prior['active_release'],'operation_id':plan['operation_id']}
            expected_receipt={'record_type':'lifecycle-receipt','schema_version':2,'operation_id':plan['operation_id'],
                'plan':plan,'prior_binding_ref':ref(prior,'operation_id'),'result_binding_ref':ref(result_binding,'operation_id')}
            fault={'event':'fsync-after','path':'.hrn/product/receipts/entry-transition.json','occurrence':1,'write_bytes':None}
            new_child,new_log,new_events,ready,release,command=self.call(target,self.apply_args(target,preview),preview['request'],fault=fault,pause=True)
            token=self.wait_ready(new_child,ready,target)
            old_cmd,old_events,_,_,_=self.scenario(target,entry='old-source',argv=apply_old,pause=False)
            old_child,old_log=self.spawn(old_cmd,'late-old',old_preview['request'])
            deadline=time.monotonic()+self.remaining(60)
            while not old_events.exists() or not any(r['event']=='lock-attempt' for r in self.event_rows(old_events)):
                self.assertIsNone(old_child.poll());self.assertLess(time.monotonic(),deadline);time.sleep(0.02)
            old_rows=self.event_rows(old_events);self.assertFalse(any(r['event']=='lock-acquired' for r in old_rows))
            self.release_pause(release,token);self.finish(new_child,new_log,timeout=150,expected=-signal.SIGKILL)
            code,data=self.finish(old_child,old_log,timeout=150,expected=None)
            self.assertEqual(65,code,data);failure=json.loads(data)
            self.assertEqual('HV2-WORKSPACE-PRODUCT',failure['code']);self.assertEqual('invalid receipt identity/schema',failure['message'])
            after=snapshot(target);receipt_name='.hrn/product/receipts/entry-transition.json'
            self.assertEqual(set(initial)|{receipt_name},set(after))
            self.assertEqual(initial,{k:v for k,v in after.items() if k!=receipt_name})
            self.assertEqual(canonical(expected_receipt),(target/receipt_name).read_bytes())
            rows=self.event_rows(old_events)
            acquired=next(r for r in rows if r['event']=='lock-acquired');attempt=next(r for r in rows if r['event']=='lock-attempt')
            self.assertEqual(token['lock']['dev'],attempt['detail']['dev']);self.assertEqual(token['lock']['ino'],attempt['detail']['ino'])
            self.assertEqual(attempt['detail'],acquired['detail']);self.assertEqual(old_child.pid,attempt['pid'])
            self.assertLess(attempt['seq'],acquired['seq']);self.assertGreaterEqual(acquired['monotonic_ns'],self.event_rows(new_events)[-1]['monotonic_ns'])


        def old_local(self, target, *, scope='a'):
            # Fixed OLD API fixture with an explicit verified-runtime seam.
            # This is not evidence of an old installed executor invocation.
            program = r'''
import hashlib,json,os,sys
from pathlib import Path
old,target=map(Path,sys.argv[1:3]);scope=sys.argv[3]
if scope not in ('a','hv2','colvia'):raise RuntimeError('fixture scope')
sys.path.insert(0,str(old/'src'))
from hv2ref.product import verify_workspace_product
from hv2ref.work import WorkStore,snapshot,make_manifest,record_ref
from hv2ref.intent import WorkspaceIntentStore
from hv2ref.jsonio import canonical_json_bytes
TIME='2026-01-01T00:00:00Z'
def runtime(root):
 state=verify_workspace_product(root)
 return {'binding_ref':state['binding_ref'],'launcher_sha256':state['launcher_sha256'],'inventory_id':state['inventory']['inventory_id']}
store=WorkspaceIntentStore(target,runtime)
draft={'record_type':'intent-draft','schema_version':1,'authority_home_id':'fixture-home','intent_id':'local-intent',
 'revision_id':'local-draft','sequence':1,'prior_revision_ref':None,'actor':'agent','acceptance_authority':'owner','observed_at':TIME,
 'facets':{k:{'status':'known','value':'fixture'} for k in ('acceptance_oracle','destination','expected_outcome','forbidden_scope','goal','scope')},
 'gaps':[],'statements':[],'route':'direct-entry'}
store.publish_draft(draft)
preview=store.prepare('local-intent',record_ref(draft,'revision_id'),actor='owner',reason='fixture',request_id='local-accept',observed_at=TIME)
graph=store.apply(preview['ticket'],confirm_token=preview['confirm_token'])
selected=graph['selections'][graph['current']['selection_ref']['id']]
intent={'authority_home_id':'fixture-home','kind':'intent','id':'local-intent','revision_ref':selected['revision_ref'],
 'acceptance_ref':selected['acceptance_ref'],'selection_ref':graph['current']['selection_ref']}
base=snapshot(target,verified_launcher_sha256=runtime(target)['launcher_sha256'])
manifest=make_manifest(base,base,scope=[scope]);digest=hashlib.sha256(canonical_json_bytes(manifest)).hexdigest()
identity={'record_type':'work-identity','schema_version':1,'authority_home_id':'fixture-home','work_id':'local-work','work_type':'change',
 'created_at':TIME,'acceptance_authority':'owner','lineage':None}
revision={'record_type':'work-revision','schema_version':1,'authority_home_id':'fixture-home','work_id':'local-work','record_id':'local-start',
 'observed_at':TIME,'observed_scope':['fixture'],'unavailable_scope':[],'author':'agent','operation':'start','expected_prior_selection':None,
 'intent_ref':intent,'scope':[scope],'document_refs':[],'evidence_refs':[],'result_refs':{'manifest':{'id':digest,'sha256':digest}},
 'progress':'active','next_action':'owner review','relations':[],'rebind_from':None,'execution_context':{'mode':'local','attempt_id':'local-attempt'}}
graph=WorkStore(target,runtime).publish(identity,revision,manifest,selection_id='local-selection',operation_id='local-publish')
for name,module in tuple(sys.modules.items()):
 if name=='hv2ref' or name.startswith('hv2ref.'):
  if not Path(module.__file__).is_relative_to(old/'src'):raise RuntimeError('non-OLD import')
print(json.dumps({'kind':'actual-old-api-local','pid':os.getpid(),'pgid':os.getpgrp(),'state':graph['state'],'manifest':manifest}))
'''
            child,log=self.spawn((ctx['runtime_path'],'-I','-S','-B','-c',program,old_source,target,scope),'old-local')
            _,data=self.finish(child,log,timeout=90);result=json.loads(data)
            self.assertEqual('actual-old-api-local',result['kind'])
            self.assertEqual((child.pid,os.getpgrp()),(result['pid'],result['pgid']))
            self.assertEqual('active',result['state'])
            return result

        def test_local_baseline_survives_actual_cutover_and_replay(self):
            product=self.product();target=self.old_target();self.old_local(target)
            preview=self.transition(target)
            truth={n:v for n,v in snapshot(target).items() if n.startswith(('.hrn/intents/','.hrn/work/'))}
            code,data,_=self.call(target,self.apply_args(target,preview),preview['request'])
            self.assertEqual(0,code,data);result=json.loads(data)
            self.assertEqual({'classification':'verified','work_ids':['local-work'],'observation':'actual project snapshot'},result['transition_content_verification'])
            self.assertEqual(truth,{n:v for n,v in snapshot(target).items() if n.startswith(('.hrn/intents/','.hrn/work/'))})
            before=snapshot(target)
            code,data,events=self.call(target,self.apply_args(target,preview,recover=True),preview['request'])
            self.assertEqual(0,code,data);self.assertEqual('replayed',json.loads(data)['classification'])
            self.assertEqual(before,snapshot(target))
            synced={r['path'] for r in self.event_rows(events) if r['event']=='fsync-after'}
            self.assertTrue({'colvia','.hrn/product/binding.json'}<=synced)
            self.assertEqual('entry-1',product.verify_workspace_product(target)['inventory']['inventory_id'])

        def test_local_dirty_baseline_and_entry_scope_refuse_before_receipt(self):
            from hv2ref.errors import ContractError
            product=self.product()
            for kind in ('dirty','hv2','colvia'):
                target=self.old_target(kind);self.old_local(target,scope='a' if kind=='dirty' else kind)
                if kind=='dirty':(target/'a').write_bytes(b'local edits must be preserved\n')
                before=snapshot(target)
                with self.assertRaises(ContractError) as caught:self.transition(target)
                self.assertEqual('HV2-WORKSPACE-PRODUCT',caught.exception.code)
                self.assertIn('baseline differs' if kind=='dirty' else 'entry path dependency',caught.exception.message)
                self.assertIn('local-work',caught.exception.message)
                self.assertEqual(before,snapshot(target))
                self.assertFalse((target/'.hrn/product/receipts/entry-transition.json').exists())

        def test_local_drift_after_s5_is_nonpass_with_b1_preserved(self):
            product=self.product();target=self.old_target();self.old_local(target);preview=self.transition(target)
            self.interrupted_api(target,preview,'after-launcher')
            (target/'a').write_bytes(b'concurrent project change\n')
            code,data,_=self.call(target,self.apply_args(target,preview,recover=True),preview['request'])
            self.assertEqual(65,code,data);self.assertIn(b'baseline differs',data)
            state=product._workspace_observe(target)  # Verified internal observation, not the public four-key proof.
            self.assertEqual('entry-1',state['inventory']['inventory_id']);self.assertIsNone(state['pending'])
            self.assertEqual('entry-transition',state['binding']['operation_id'])
            self.assertEqual(b'concurrent project change\n',(target/'a').read_bytes())
            self.assertFalse((target/'hv2').exists())
            before=snapshot(target)
            code,data,_=self.call(target,self.apply_args(target,preview,recover=True),preview['request'])
            self.assertEqual(65,code,data);self.assertIn(b'baseline differs',data);self.assertEqual(before,snapshot(target))

        def test_changed_truth_replay_reports_unavailable_and_keeps_binding(self):
            from hv2ref.intent import WorkspaceIntentStore
            product=self.product();target=self.old_target();preview=self.transition(target)
            product.workspace_switch_apply(target,preview['request'],confirm_token=preview['confirm_token'],source=candidate_source)
            def runtime(root):
                state=product.verify_workspace_product(root)
                return {'binding_ref':state['binding_ref'],'launcher_sha256':state['launcher_sha256'],'inventory_id':'entry-1'}
            draft={'record_type':'intent-draft','schema_version':1,'authority_home_id':'fixture-home','intent_id':'after-cutover',
                'revision_id':'after-draft','sequence':1,'prior_revision_ref':None,'actor':'agent','acceptance_authority':'owner','observed_at':FIXTURE_TIME,
                'facets':{k:{'status':'known','value':'fixture'} for k in ('acceptance_oracle','destination','expected_outcome','forbidden_scope','goal','scope')},
                'gaps':[],'statements':[],'route':'direct-entry'}
            WorkspaceIntentStore(target,runtime).publish_draft(draft)
            before=snapshot(target);binding=product.verify_workspace_product(target)['binding_ref']
            code,data,_=self.call(target,self.apply_args(target,preview,recover=True),preview['request'])
            self.assertEqual(10,code,data);result=json.loads(data)
            self.assertEqual('degraded',result['classification'])
            self.assertEqual('unavailable',result['transition_content_verification']['classification'])
            self.assertEqual(binding,result['product']['binding_ref']);self.assertIsNone(product._workspace_observe(target)['pending'])
            self.assertEqual(before,snapshot(target))
            code,data,_=self.call(target,['--source-checkout','status','--target',target])
            self.assertEqual(0,code,data);self.assertEqual('pass',json.loads(data)['classification'])
            self.assertEqual(before,snapshot(target))

        def test_invalid_new_entry_prefixes_preserve_exact_bytes(self):
            product=self.product();payload=product.workspace_candidate(candidate_source)['payload']['colvia']
            cases=(('wrong-bytes',b'foreign',0o600),('executable-prefix',payload[:1],0o755),
                   ('wrong-mode',payload,0o644),('symlink',None,None),('unknown-binding-stage',None,None))
            for label,data,mode in cases:
                target=self.old_target(label);preview=self.transition(target);self.interrupted_api(target,preview,'after-release')
                if label=='symlink':(target/'colvia').symlink_to('a')
                elif label=='unknown-binding-stage':
                    write_file(target/'.hrn/staging/entry-entry-transition/foreign',b'preserve')
                else:write_file(target/'colvia',data,mode)
                before=snapshot(target)
                code,data,_=self.call(target,self.apply_args(target,preview,recover=True),preview['request'])
                self.assertEqual(65,code,data)
                failure=json.loads(data)
                self.assertEqual('HV2-WORKSPACE-CONTRACT' if label=='symlink' else 'HV2-WORKSPACE-PRODUCT',failure['code'])
                if label=='symlink':self.assertEqual('wrong file type: colvia',failure['message'])
                self.assertEqual(before,snapshot(target))

        def test_s6_rejects_binding_next_and_wrong_modes(self):
            product=self.product()
            for label in ('binding-next','binding-mode','new-mode'):
                target=self.old_target(label);preview=self.transition(target);self.interrupted_api(target,preview,'after-binding')
                if label=='binding-next':
                    write_file(target/'.hrn/staging/entry-entry-transition/binding.next',(target/'.hrn/product/binding.json').read_bytes(),0o600)
                elif label=='binding-mode':(target/'.hrn/product/binding.json').chmod(0o644)
                else:(target/'colvia').chmod(0o700)
                before=snapshot(target)
                code,data,_=self.call(target,self.apply_args(target,preview,recover=True),preview['request'])
                self.assertEqual(65,code,data);self.assertIn(b'HV2-WORKSPACE-PRODUCT',data);self.assertEqual(before,snapshot(target))

        def test_same_entry_update_rollback_and_exact_repair(self):
            product=self.product();target=self.directory('target');self.new_init(target)
            first=product._workspace_observe(target)['binding']['active_release']
            other=self.directory('other-source');candidate=product.workspace_candidate(candidate_source)
            for name,data in candidate['payload'].items():write_file(other/name,data,0o755 if name=='colvia' else 0o644)
            with (other/'colvia').open('ab') as stream:stream.write(b'\n# Fixture candidate identity change.\n')
            update=product.workspace_switch_preview(target,action='update',source=other,operation_id='entry-update',created_at=FIXTURE_TIME)
            self.assertEqual([],update['request']['remove'])
            product.workspace_switch_apply(target,update['request'],confirm_token=update['confirm_token'],source=other)
            self.assertNotEqual(first,product._workspace_observe(target)['binding']['active_release'])
            self.assertEqual((other/'colvia').read_bytes(),(target/'colvia').read_bytes())
            rollback=product.workspace_switch_preview(target,action='rollback',source=None,to_release_id=first['id'],operation_id='entry-rollback',created_at=FIXTURE_TIME)
            self.assertEqual([],rollback['request']['remove'])
            product.workspace_switch_apply(target,rollback['request'],confirm_token=rollback['confirm_token'])
            self.assertEqual(first,product._workspace_observe(target)['binding']['active_release'])
            self.assertEqual(candidate['payload']['colvia'],(target/'colvia').read_bytes())
            (target/'colvia').write_bytes(b'damaged managed launcher\n')
            repair=product.workspace_repair_preview(candidate_source,target,self.base/'repair-backup',operation_id='entry-repair',created_at=FIXTURE_TIME)
            product.workspace_repair_apply(candidate_source,target,repair['request'],confirm_token=repair['confirm_token'])
            self.assertEqual(candidate['payload']['colvia'],(target/'colvia').read_bytes())
            self.assertFalse((target/'hv2').exists());self.assertEqual(first,product._workspace_observe(target)['binding']['active_release'])

        def test_retired_collision_blocks_completed_transition_replay(self):
            product=self.product();target=self.old_target();preview=self.transition(target)
            product.workspace_switch_apply(target,preview['request'],confirm_token=preview['confirm_token'],source=candidate_source)
            write_file(target/'hv2',b'new project occupant\n');before=snapshot(target)
            for recover in (False,True):
                code,data,_=self.call(target,self.apply_args(target,preview,recover=recover),preview['request'])
                self.assertEqual(65,code,data);self.assertIn(b'preserve historical result',data)
                self.assertEqual(before,snapshot(target))
            state=product._workspace_observe(target)
            self.assertEqual('entry-transition',state['binding']['operation_id']);self.assertIsNone(state['pending'])

        def test_first_entry_transition_cannot_rollback_to_old_window(self):
            from hv2ref.errors import ContractError
            product=self.product();target=self.old_target();preview=self.transition(target)
            product.workspace_switch_apply(target,preview['request'],confirm_token=preview['confirm_token'],source=candidate_source)
            before=snapshot(target)
            with self.assertRaises(ContractError) as caught:
                product.workspace_switch_preview(target,action='rollback',source=None,operation_id='forbidden-old-rollback',created_at=FIXTURE_TIME)
            self.assertEqual('HV2-WORKSPACE-PRODUCT',caught.exception.code)
            self.assertIn('first transition cannot roll back to checkout-1',caught.exception.message)
            self.assertEqual(before,snapshot(target))

        def test_s5_exact_old_entry_reappearance_recovers_from_s4(self):
            # Synthetic namespace re-observation, not a power-loss experiment.
            product=self.product();target=self.old_target();preview=self.transition(target)
            old=(target/'hv2').read_bytes();self.interrupted_api(target,preview,'after-launcher')
            self.assertFalse((target/'hv2').exists())
            self.assertFalse((target/'.hrn/staging/entry-entry-transition/binding.next').exists())
            write_file(target/'hv2',old,0o755)
            code,data,_=self.call(target,self.apply_args(target,preview,recover=True),preview['request'])
            self.assertEqual(0,code,data);self.assertFalse((target/'hv2').exists())
            self.assertEqual('entry-1',product.verify_workspace_product(target)['inventory']['inventory_id'])


        def d3_run(self, target, preview, *, selector=None, fault=None, recover=False, truth_change=False, source=None):
            value = {'preview': preview, 'selector': selector, 'fault': fault, 'recover': recover, 'truth_change': truth_change}
            child, log = self.spawn((ctx['runtime_path'], '-I', '-S', '-B', '-c', D3_SYNC_PROGRAM,
                                     candidate_source, target, source or candidate_source), 'd3-sync', value)
            code, data = self.finish(child, log, timeout=150, expected=None)
            try:
                result = json.loads(data)
            except json.JSONDecodeError:
                self.fail('D3 child did not emit an envelope; exit=' + str(code) + '; output=' + repr(data[-8000:]))
            self.assertEqual(code, result['exit'], data[-8000:])
            self.assertIsNone(result['diagnostic'], data[-8000:])
            self.assertEqual('', result['stderr'], data[-8000:])
            self.assertEqual(code, result['cli_exit'], data[-8000:])
            return result

        def d3_fault(self, selector, fault):
            import errno
            product = self.product(); target = self.old_target(); preview = self.transition(target)
            before = snapshot(target)
            result = self.d3_run(target, preview, selector=selector, fault=fault)
            self.assertEqual(65, result['exit']); self.assertEqual('HV2-WORKSPACE-PRODUCT', result['result']['code'])
            phase = 'admission' if selector.startswith('admission_') else 'publication'
            role = {'admission_root': 'target', 'admission_locks': 'locks'}.get(selector, selector.replace('_', '-'))
            message = result['result']['message']
            self.assertTrue(message.startswith('d3-sync:' + phase + ':' + role + ';'), message)
            self.assertIn('directory synchronization ' + ('unavailable:' + str(errno.EINVAL) if fault == 'unavailable' else 'oserror:' + str(errno.EIO)), message)
            self.assertIn('preserve receipt, prefix and binding', message)
            self.assertEqual(1, len(result['injected']))
            injection = result['injected'][0]; row = result['rows'][injection['index']]
            self.assertEqual(1, row['occurrences'][selector]); self.assertEqual(fault, row['result'])
            self.assertEqual(injection['snapshot'], result['after'], 'publication after failed sync')
            self.assertEqual([], result['rows'][injection['index'] + 1:], 'sync sequence advanced after failure')
            after = snapshot(target)
            self.assertEqual(result['after'], json.loads(json.dumps(after)))
            b1 = selector in ('binding_product_parent', 'binding_operation_parent')
            self.assertEqual(b1, injection['facts']['b1'])
            self.assertIn('B1 publication observed=' + ('yes' if b1 else 'no'), message)
            self.assertIn('current product verification=' + ('verified' if b1 else 'not-requested'), message)
            binding = json.loads((target / '.hrn/product/binding.json').read_bytes())
            self.assertEqual('entry-transition' if b1 else preview['request']['expected_binding_ref']['id'], binding['operation_id'])
            for name, value in before.items():
                if name not in ('hv2', '.hrn/product/binding.json'):
                    self.assertEqual(value, after[name], name)
            if phase == 'admission':
                anchors = {'.hrn/locks', '.hrn/locks/writer.lock'}
                self.assertEqual({n: v for n, v in before.items() if n not in anchors},
                                 {n: v for n, v in after.items() if n not in anchors})
                self.assertFalse(injection['facts']['receipt']); self.assertFalse((target / 'colvia').exists())
            else:
                receipt = json.loads((target / '.hrn/product/receipts/entry-transition.json').read_bytes())
                self.assertEqual(preview['request'], receipt['plan'])
                self.assertEqual(before['a'], after['a'])
            if selector in ('receipt_parent', 'candidate_directory_parent', 'candidate_directory_self', 'candidate_member_parent', 'release_parent', 'release_operation_parent'):
                self.assertFalse((target / 'colvia').exists()); self.assertEqual(before['hv2'], after['hv2'])
                self.assertFalse((target / '.hrn/staging/entry-entry-transition').exists())
            if selector == 'new_entry_parent':
                self.assertEqual(0o755, stat.S_IMODE((target / 'colvia').stat().st_mode))
                self.assertEqual(before['hv2'], after['hv2'])
            if selector in ('old_retirement_parent', 'binding_directory_parent', 'binding_directory_self', 'binding_member_parent') or b1:
                self.assertFalse((target / 'hv2').exists())
            if selector == 'binding_member_parent':
                next_path = target / '.hrn/staging/entry-entry-transition/binding.next'
                self.assertEqual(0o600, stat.S_IMODE(next_path.stat().st_mode))
                self.assertEqual('entry-transition', json.loads(next_path.read_bytes())['operation_id'])
            if b1:
                self.assertEqual('entry-transition', product.verify_workspace_product(target)['binding_ref']['id'])
                self.assertFalse((target / '.hrn/staging/entry-entry-transition/binding.next').exists())

            # Before the receipt there is no pending transaction to recover.
            # Retry the same admitted request normally; retain --recover only
            # after receipt publication. No request/token/content is changed.
            if phase == 'admission':
                self.assertFalse((target / '.hrn/product/receipts/entry-transition.json').exists())
            recovered = self.d3_run(target, preview, recover=phase != 'admission')
            self.assertEqual(0, recovered['exit']); self.assertEqual([], recovered['injected'])
            self.assertEqual('replayed' if b1 else 'updated', recovered['result']['classification'])
            self.assertEqual(result['after'], recovered['before'])
            self.assertTrue(all(r['result'] == 'pass' for r in recovered['rows']))
            self.assertEqual('entry-transition', product.verify_workspace_product(target)['binding_ref']['id'])
            self.assertFalse((target / 'hv2').exists())
            self.assertFalse((target / '.hrn/staging/entry-entry-transition/binding.next').exists())
            if b1: self.assertEqual(after, snapshot(target))
            for name, value in before.items():
                if name not in ('hv2', '.hrn/product/binding.json'):
                    self.assertEqual(value, snapshot(target)[name], name)

        def d3_replay_paths(self, target, preview):
            # Independent literal fixture oracle; never call the production path-set helper.
            rid = preview['request']['candidate_release']['id']; release = Path('.hrn/product/releases') / rid
            paths = {'.', '.hrn', '.hrn/product', '.hrn/product/receipts', '.hrn/product/releases', '.hrn/locks', release.as_posix()}
            inventory = json.loads((target / release / 'inventory.json').read_bytes())
            for item in inventory['entries']:
                for parent in (Path('payload') / item['path']).parents:
                    if parent != Path('.'): paths.add((release / parent).as_posix())
            for name in ('.hrn/staging', '.hrn/staging/switch-entry-transition', '.hrn/staging/entry-entry-transition'):
                if (target / name).is_dir(): paths.add(name)
            return sorted(paths, key=lambda name: (-len(Path(name).parts), name.encode('utf-8')))

        def d3_other_source(self):
            source = self.directory('other-source')
            for name, data in self.product().workspace_candidate(candidate_source)['payload'].items():
                write_file(source / name, data, 0o755 if name == 'colvia' else 0o644)
            with (source / 'colvia').open('ab') as handle: handle.write(b'\n# D3 same-entry fixture.\n')
            return source

        def d3_new_truth(self, target):
            from hv2ref.intent import WorkspaceIntentStore
            product = self.product()
            def runtime(root):
                value = product.verify_workspace_product(root)
                return {'binding_ref': value['binding_ref'], 'launcher_sha256': value['launcher_sha256'], 'inventory_id': 'entry-1'}
            draft = {'record_type': 'intent-draft', 'schema_version': 1, 'authority_home_id': 'fixture-home',
                'intent_id': 'd3-after-cutover', 'revision_id': 'd3-after-draft', 'sequence': 1, 'prior_revision_ref': None,
                'actor': 'agent', 'acceptance_authority': 'owner', 'observed_at': FIXTURE_TIME,
                'facets': {k: {'status': 'known', 'value': 'fixture'} for k in
                    ('acceptance_oracle', 'destination', 'expected_outcome', 'forbidden_scope', 'goal', 'scope')},
                'gaps': [], 'statements': [], 'route': 'direct-entry'}
            WorkspaceIntentStore(target, runtime).publish_draft(draft)

        def test_d3_normal_sync_set_and_order(self):
            target = self.old_target(); preview = self.transition(target); before = snapshot(target)
            result = self.d3_run(target, preview)
            self.assertEqual(0, result['exit']); self.assertEqual('updated', result['result']['classification'])
            admission = [r['path'] for r in result['rows'] if r['alias'] == 'product' and not r['facts']['receipt']]
            expected = ['.', '.hrn', '.hrn/product', '.hrn/product/receipts', '.hrn/product/releases', '.hrn/locks']
            if '.hrn/staging' in before: expected.append('.hrn/staging')
            self.assertEqual(expected, admission)
            order = ['receipt_parent', 'candidate_directory_parent', 'candidate_directory_self', 'candidate_member_parent',
                     'release_parent', 'release_operation_parent', 'new_entry_parent', 'old_retirement_parent',
                     'binding_directory_parent', 'binding_directory_self', 'binding_member_parent',
                     'binding_product_parent', 'binding_operation_parent']
            first = [next(i for i, row in enumerate(result['rows']) if name in row['selectors']) for name in order]
            self.assertEqual(sorted(first), first); self.assertEqual(len(first), len(set(first)))
            self.assertTrue(all(row['result'] == 'pass' for row in result['rows']))
            self.assertEqual('entry-transition', self.product().verify_workspace_product(target)['binding_ref']['id'])
            self.assertEqual('not-applicable', result['result']['transition_content_verification']['classification'])

        def test_d3_complete_prefix_retry_resynchronizes(self):
            target = self.old_target(); preview = self.transition(target)
            self.interrupted_api(target, preview, 'after-launcher')
            self.assertFalse((target / 'hv2').exists()); before = snapshot(target)
            result = self.d3_run(target, preview, recover=True)
            self.assertEqual(0, result['exit'])
            rows = [r for r in result['rows'] if r['alias'] == 'product' and not r['facts']['b1']]
            receipt_index = max(i for i, r in enumerate(rows) if r['path'] == '.hrn/product/receipts')
            release = '.hrn/product/releases/' + preview['request']['candidate_release']['id']
            after_receipt = rows[receipt_index + 1:]
            self.assertTrue(any(r['path'] == release for r in after_receipt))
            self.assertTrue(any(r['path'] == '.hrn/product/releases' for r in after_receipt))
            self.assertTrue(any(r['path'] == '.hrn/staging/switch-entry-transition' for r in after_receipt))
            self.assertGreaterEqual(sum(r['path'] == '.' for r in after_receipt), 2, 'N parent and absent-O parent both required')
            self.assertTrue(all(not r['facts']['old'] for r in rows))
            self.assertEqual(before['.hrn/product/receipts/entry-transition.json'], snapshot(target)['.hrn/product/receipts/entry-transition.json'])
            self.assertEqual('entry-transition', self.product().verify_workspace_product(target)['binding_ref']['id'])

        def d3_complete_prefix_retry_fault(self, fault):
            import errno
            target = self.old_target(); preview = self.transition(target)
            self.interrupted_api(target, preview, 'after-launcher')
            before = snapshot(target)
            release = '.hrn/product/releases/' + preview['request']['candidate_release']['id']
            receipt = '.hrn/product/receipts/entry-transition.json'
            operation = '.hrn/staging/switch-entry-transition'
            self.assertFalse((target / 'hv2').exists())
            self.assertEqual(0o755, stat.S_IMODE((target / 'colvia').stat().st_mode))
            self.assertTrue((target / release).is_dir()); self.assertTrue((target / receipt).is_file())
            self.assertTrue((target / operation).is_dir()); self.assertEqual([], list((target / operation).iterdir()))
            self.assertFalse((target / '.hrn/staging/entry-entry-transition').exists())
            self.assertEqual(preview['request']['expected_binding_ref']['id'],
                             json.loads((target / '.hrn/product/binding.json').read_bytes())['operation_id'])
            result = self.d3_run(target, preview, recover=True, selector='recovery_release', fault=fault)
            self.assertEqual(65, result['exit']); self.assertEqual('HV2-WORKSPACE-PRODUCT', result['result']['code'])
            message = result['result']['message']
            self.assertTrue(message.startswith('d3-sync:recovery:release-directory;'), message)
            self.assertIn('directory synchronization ' + ('unavailable:' + str(errno.EINVAL) if fault == 'unavailable' else 'oserror:' + str(errno.EIO)), message)
            self.assertIn('B1 publication observed=no; current product verification=not-requested', message)
            self.assertIn('preserve receipt, prefix and binding', message)
            self.assertEqual(1, len(result['injected'])); injection = result['injected'][0]
            row = result['rows'][injection['index']]
            self.assertEqual('product', row['alias']); self.assertEqual(release, row['path'])
            self.assertEqual(1, row['occurrences']['recovery_release']); self.assertEqual(fault, row['result'])
            prefix = result['rows'][:injection['index']]
            admitted = [i for i, r in enumerate(prefix) if r['alias'] == 'product' and r['path'] == release]
            receipts = [i for i, r in enumerate(prefix) if r['alias'] == 'product' and r['path'] == '.hrn/product/receipts']
            self.assertEqual(1, len(admitted)); self.assertEqual(2, len(receipts))
            self.assertLess(receipts[0], admitted[0]); self.assertLess(admitted[0], receipts[1])
            self.assertTrue(all(r['result'] == 'pass' for r in prefix))
            self.assertFalse(injection['facts']['b1']); self.assertFalse(injection['facts']['old'])
            self.assertEqual(0o755, injection['facts']['new_mode'])
            self.assertEqual([], result['rows'][injection['index'] + 1:], 'sync advanced after recovery failure')
            self.assertEqual(json.loads(json.dumps(before)), result['before'])
            self.assertEqual(result['before'], injection['snapshot'])
            self.assertEqual(injection['snapshot'], result['after'], 'publication advanced after recovery failure')
            self.assertEqual(before, snapshot(target), 'receipt, release, N, B0, operation or truth changed')
            self.assertFalse((target / '.hrn/staging/entry-entry-transition').exists())

            recovered = self.d3_run(target, preview, recover=True)
            self.assertEqual(0, recovered['exit']); self.assertEqual('updated', recovered['result']['classification'])
            self.assertEqual(result['after'], recovered['before']); self.assertEqual([], recovered['injected'])
            self.assertTrue(all(r['result'] == 'pass' for r in recovered['rows']))
            self.assertEqual(before[receipt], snapshot(target)[receipt])
            self.assertEqual('entry-transition', self.product().verify_workspace_product(target)['binding_ref']['id'])

        def test_d3_complete_prefix_retry_sync_unavailable(self):
            self.d3_complete_prefix_retry_fault('unavailable')

        def test_d3_complete_prefix_retry_sync_oserror(self):
            self.d3_complete_prefix_retry_fault('oserror')

        def test_d3_current_replay_sync_set_and_retired_staging(self):
            target = self.old_target(); preview = self.transition(target)
            result = self.d3_run(target, preview); self.assertEqual(0, result['exit'])
            for retire in (False, True):
                if retire:
                    for name in ('entry-entry-transition', 'switch-entry-transition'):
                        directory = target / '.hrn/staging' / name
                        self.assertEqual([], list(directory.iterdir())); directory.rmdir()
                    # Retire the staging root only when it is empty; preserve unrelated history.
                    staging = target / '.hrn/staging'
                    if not any(staging.iterdir()): staging.rmdir()
                before = snapshot(target); expected = self.d3_replay_paths(target, preview)
                result = self.d3_run(target, preview, recover=True)
                self.assertEqual(0, result['exit']); self.assertEqual('replayed', result['result']['classification'])
                actual = [r['path'] for r in result['rows'] if r['alias'] == 'product']
                self.assertEqual(expected, actual); self.assertEqual(len(actual), len(set(actual)))
                self.assertEqual(before, snapshot(target))

        def test_d3_replay_sync_failure_precedes_truth_unavailable(self):
            target = self.old_target(); preview = self.transition(target)
            self.assertEqual(0, self.d3_run(target, preview)['exit']); self.d3_new_truth(target)
            before = snapshot(target)
            for fault in ('unavailable', 'oserror'):
                result = self.d3_run(target, preview, recover=True, selector='replay_release', fault=fault)
                self.assertEqual(65, result['exit']); self.assertEqual('HV2-WORKSPACE-PRODUCT', result['result']['code'])
                self.assertTrue(result['result']['message'].startswith('d3-sync:replay:release-directory;'))
                self.assertEqual(1, len(result['injected'])); injection = result['injected'][0]
                self.assertEqual(injection['snapshot'], result['after']); self.assertEqual([], result['rows'][injection['index'] + 1:])
                self.assertEqual(before, snapshot(target)); self.assertNotIn('transition_content_verification', result['result'])
                self.assertIn('B1 publication observed=yes; current product verification=verified', result['result']['message'])
            result = self.d3_run(target, preview, recover=True)
            self.assertEqual(10, result['exit']); self.assertEqual('unavailable', result['result']['transition_content_verification']['classification'])
            self.assertEqual(before, snapshot(target))

        def test_d3_historical_operation_does_not_sync_new_binding(self):
            product = self.product(); target = self.old_target(); preview = self.transition(target)
            self.assertEqual(0, self.d3_run(target, preview)['exit']); source = self.d3_other_source()
            update = product.workspace_switch_preview(target, action='update', source=source, operation_id='newer-entry', created_at=FIXTURE_TIME)
            product.workspace_switch_apply(target, update['request'], confirm_token=update['confirm_token'], source=source)
            before = snapshot(target); current = product.verify_workspace_product(target)
            result = self.d3_run(target, preview, recover=True)
            self.assertEqual(0, result['exit']); self.assertEqual('replayed', result['result']['classification'])
            self.assertEqual(current, result['result']['product']); self.assertEqual('newer-entry', current['binding_ref']['id'])
            self.assertEqual([], [r for r in result['rows'] if r['alias'] == 'product'])
            self.assertEqual(before, snapshot(target))

        def test_d3_same_entry_scope_unchanged(self):
            product = self.product(); source = self.d3_other_source(); outputs = []
            for name, fault in (('baseline', None), ('unavailable', 'unavailable')):
                target = self.directory(name); self.new_init(target)
                preview = product.workspace_switch_preview(target, action='update', source=source, operation_id='same-entry', created_at=FIXTURE_TIME)
                self.assertEqual([], preview['request']['remove'])
                result = self.d3_run(target, preview, source=source, selector='same_entry_receipt' if fault else None, fault=fault)
                self.assertEqual(0, result['exit']); self.assertEqual('updated', result['result']['classification'])
                self.assertNotIn('d3-sync:', json.dumps(result['result']))
                if fault: self.assertEqual(1, len(result['injected']))
                outputs.append(product._workspace_observe(target)['binding']['active_release'])
                self.assertEqual((source / 'colvia').read_bytes(), (target / 'colvia').read_bytes())
            self.assertEqual(outputs[0], outputs[1])

        def test_d3_collision_precedes_replay_sync(self):
            target = self.old_target(); preview = self.transition(target)
            self.assertEqual(0, self.d3_run(target, preview)['exit'])
            write_file(target / 'hv2', b'new project occupant\n'); before = snapshot(target)
            result = self.d3_run(target, preview, recover=True)
            self.assertEqual(65, result['exit']); self.assertEqual('HV2-WORKSPACE-PRODUCT', result['result']['code'])
            self.assertIn('preserve historical result', result['result']['message'])
            self.assertEqual([], [r for r in result['rows'] if r['alias'] == 'product'])
            self.assertEqual(before, snapshot(target))

        def d3_composite(self, complete):
            product = self.product(); target = self.old_target(); preview = self.transition(target)
            self.interrupted_api(target, preview, 'after-release')
            release = target / '.hrn/product/releases' / preview['request']['candidate_release']['id']
            write_file(target / 'colvia', (release / 'payload/colvia').read_bytes(), 0o755)
            prior = json.loads((target / '.hrn/product/binding.json').read_bytes())
            staged_binding, _ = product._switch_binding_receipt(preview['request'], prior)
            member = target / '.hrn/staging/entry-entry-transition/binding.next'
            write_file(member, canonical(staged_binding) if complete else b'')
            before = snapshot(target)
            result = self.d3_run(target, preview, recover=True)
            self.assertEqual(65, result['exit']); self.assertEqual('HV2-WORKSPACE-PRODUCT', result['result']['code'])
            self.assertEqual('binding staging is not an expected physical prefix', result['result']['message'])
            self.assertEqual([], result['rows']); self.assertEqual(before, snapshot(target))
            self.assertEqual(canonical(staged_binding) if complete else b'', member.read_bytes())

        def test_d3_composite_zero_byte_preserved(self):
            self.d3_composite(False)

        def test_d3_composite_complete_member_preserved(self):
            self.d3_composite(True)

        def test_d3_truth_changes_during_comparison_refused(self):
            product = self.product(); target = self.old_target(); preview = self.transition(target)
            self.assertEqual(0, self.d3_run(target, preview)['exit']); before = snapshot(target)
            result = self.d3_run(target, preview, recover=True, truth_change=True)
            self.assertEqual(65, result['exit']); self.assertEqual('HV2-WORKSPACE-PRODUCT', result['result']['code'])
            self.assertEqual('truth changed during completed transition comparison; preserve B1', result['result']['message'])
            self.assertEqual([{'classification': 'not-applicable', 'work_ids': [], 'reason': 'no unfinished selected local Work'}], result['comparisons'])
            after = snapshot(target)
            for name, value in before.items(): self.assertEqual(value, after[name], name)
            added = set(after) - set(before); self.assertTrue(added)
            self.assertTrue(all(n.startswith('.hrn/intents/') for n in added), added)
            self.assertEqual('entry-transition', product.verify_workspace_product(target)['binding_ref']['id'])

        def test_d3_admission_root_unavailable(self):
            self.d3_fault('admission_root', 'unavailable')

        def test_d3_admission_root_oserror(self):
            self.d3_fault('admission_root', 'oserror')

        def test_d3_admission_locks_unavailable(self):
            self.d3_fault('admission_locks', 'unavailable')

        def test_d3_admission_locks_oserror(self):
            self.d3_fault('admission_locks', 'oserror')

        def test_d3_receipt_parent_unavailable(self):
            self.d3_fault('receipt_parent', 'unavailable')

        def test_d3_receipt_parent_oserror(self):
            self.d3_fault('receipt_parent', 'oserror')

        def test_d3_candidate_directory_parent_unavailable(self):
            self.d3_fault('candidate_directory_parent', 'unavailable')

        def test_d3_candidate_directory_parent_oserror(self):
            self.d3_fault('candidate_directory_parent', 'oserror')

        def test_d3_candidate_directory_self_unavailable(self):
            self.d3_fault('candidate_directory_self', 'unavailable')

        def test_d3_candidate_directory_self_oserror(self):
            self.d3_fault('candidate_directory_self', 'oserror')

        def test_d3_candidate_member_parent_unavailable(self):
            self.d3_fault('candidate_member_parent', 'unavailable')

        def test_d3_candidate_member_parent_oserror(self):
            self.d3_fault('candidate_member_parent', 'oserror')

        def test_d3_release_parent_unavailable(self):
            self.d3_fault('release_parent', 'unavailable')

        def test_d3_release_parent_oserror(self):
            self.d3_fault('release_parent', 'oserror')

        def test_d3_release_operation_parent_unavailable(self):
            self.d3_fault('release_operation_parent', 'unavailable')

        def test_d3_release_operation_parent_oserror(self):
            self.d3_fault('release_operation_parent', 'oserror')

        def test_d3_new_entry_parent_unavailable(self):
            self.d3_fault('new_entry_parent', 'unavailable')

        def test_d3_new_entry_parent_oserror(self):
            self.d3_fault('new_entry_parent', 'oserror')

        def test_d3_old_retirement_parent_unavailable(self):
            self.d3_fault('old_retirement_parent', 'unavailable')

        def test_d3_old_retirement_parent_oserror(self):
            self.d3_fault('old_retirement_parent', 'oserror')

        def test_d3_binding_directory_parent_unavailable(self):
            self.d3_fault('binding_directory_parent', 'unavailable')

        def test_d3_binding_directory_parent_oserror(self):
            self.d3_fault('binding_directory_parent', 'oserror')

        def test_d3_binding_directory_self_unavailable(self):
            self.d3_fault('binding_directory_self', 'unavailable')

        def test_d3_binding_directory_self_oserror(self):
            self.d3_fault('binding_directory_self', 'oserror')

        def test_d3_binding_member_parent_unavailable(self):
            self.d3_fault('binding_member_parent', 'unavailable')

        def test_d3_binding_member_parent_oserror(self):
            self.d3_fault('binding_member_parent', 'oserror')

        def test_d3_binding_product_parent_unavailable(self):
            self.d3_fault('binding_product_parent', 'unavailable')

        def test_d3_binding_product_parent_oserror(self):
            self.d3_fault('binding_product_parent', 'oserror')

        def test_d3_binding_operation_parent_unavailable(self):
            self.d3_fault('binding_operation_parent', 'unavailable')

        def test_d3_binding_operation_parent_oserror(self):
            self.d3_fault('binding_operation_parent', 'oserror')


        def remaining_staging_member_tears(self, label):
            candidate = self.product().workspace_candidate(candidate_source)
            members = sorted(set(candidate['payload']) - {'colvia'})
            self.assertEqual(28, len(members))
            for index, member in enumerate(members):
                with self.subTest(member=member, length=label):
                    target = self.old_target('member-' + str(index)); preview = self.transition(target)
                    self.interrupted_api(target, preview, 'after-staged-payload')
                    relative = 'payload/' + member
                    path = target / '.hrn/staging/switch-entry-transition' / candidate['release_ref']['id'] / relative
                    full = candidate['payload'][member]; self.assertEqual(full, path.read_bytes())
                    length = {'zero': 0, 'one': 1, 'middle': len(full) // 2, 'last': len(full) - 1}[label]
                    self.assertLess(length, len(full)); path.write_bytes(full[:length]); before = snapshot(target)
                    code, data, _ = self.call(target, self.apply_args(target, preview, recover=True), preview['request'])
                    self.assertEqual(65, code, data); result = json.loads(data)
                    self.assertEqual('HV2-WORKSPACE-PRODUCT', result['code'])
                    self.assertEqual('torn or changed init bytes: ' + relative, result['message'])
                    self.assertEqual(before, snapshot(target)); self.assertEqual(full[:length], path.read_bytes())

        def test_remaining_staging_members_zero_tear_refused(self):
            self.remaining_staging_member_tears('zero')

        def test_remaining_staging_members_one_tear_refused(self):
            self.remaining_staging_member_tears('one')

        def test_remaining_staging_members_middle_tear_refused(self):
            self.remaining_staging_member_tears('middle')

        def test_remaining_staging_members_last_tear_refused(self):
            self.remaining_staging_member_tears('last')

        def test_completed_staging_unknown_members_preserved(self):
            for kind in ('switch', 'entry'):
                target = self.old_target(kind); preview = self.transition(target)
                self.interrupted_api(target, preview, 'after-binding')
                directory = target / '.hrn/staging' / (kind + '-entry-transition')
                self.assertEqual([], list(directory.iterdir()))
                member = directory / 'foreign'; write_file(member, b'preserve foreign staging member\n', 0o600)
                before = snapshot(target)
                result = self.d3_run(target, preview, recover=True)
                self.assertEqual(65, result['exit']); self.assertEqual('HV2-WORKSPACE-PRODUCT', result['result']['code'])
                expected = 'unknown switch staging member; preserve' if kind == 'switch' else 'unknown entry staging member; preserve'
                self.assertEqual(expected, result['result']['message'])
                # Completed switch staging is checked under writer_guard. Its
                # three lock-preparation syncs are allowed; publication is not.
                allowed = [('workspace', '.hrn'), ('workspace', '.hrn/locks'), ('jsonio', '.hrn/locks')] if kind == 'switch' else []
                self.assertEqual(allowed, [(r['alias'], r['path']) for r in result['rows']])
                self.assertTrue(all(r['result'] == 'pass' for r in result['rows']))
                self.assertEqual([], result['injected']); self.assertEqual(result['before'], result['after'])
                self.assertEqual(before, snapshot(target))

        def remaining_recovery_fault(self, selector, fault):
            import errno
            target = self.old_target(); preview = self.transition(target)
            self.interrupted_api(target, preview, 'after-launcher'); before = snapshot(target)
            request_bytes = canonical(preview); result = self.d3_run(target, preview, recover=True, selector=selector, fault=fault)
            self.assertEqual(65, result['exit']); self.assertEqual('HV2-WORKSPACE-PRODUCT', result['result']['code'])
            role = {'recovery_release_parent': 'release-parent', 'recovery_operation_parent': 'release-operation-parent',
                    'recovery_new_parent': 'new-entry-parent', 'recovery_old_parent': 'old-retirement-parent'}[selector]
            detail = 'unavailable:' + str(errno.EINVAL) if fault == 'unavailable' else 'oserror:' + str(errno.EIO)
            self.assertEqual('d3-sync:recovery:' + role + '; directory synchronization ' + detail +
                '; B1 publication observed=no; current product verification=not-requested; '
                'preserve receipt, prefix and binding; use the exact admitted retry or separately authorized disposition', result['result']['message'])
            self.assertEqual(1, len(result['injected'])); injection = result['injected'][0]
            self.assertEqual(len(result['rows']) - 1, injection['index']); row = result['rows'][injection['index']]
            self.assertEqual(1, row['occurrences'][selector]); self.assertEqual(fault, row['result'])
            self.assertTrue(all(r['result'] == 'pass' for r in result['rows'][:-1]))
            receipts = [i for i, r in enumerate(result['rows'][:-1]) if r['alias'] == 'product' and r['path'] == '.hrn/product/receipts']
            self.assertEqual(2, len(receipts)); self.assertLess(receipts[-1], injection['index'])
            self.assertEqual(json.loads(json.dumps(before)), result['before'])
            self.assertEqual(result['before'], injection['snapshot']); self.assertEqual(injection['snapshot'], result['after'])
            self.assertEqual(before, snapshot(target)); self.assertEqual(request_bytes, canonical(preview))
            recovered = self.d3_run(target, preview, recover=True)
            self.assertEqual(0, recovered['exit']); self.assertEqual('updated', recovered['result']['classification'])
            self.assertEqual(result['after'], recovered['before']); self.assertEqual([], recovered['injected'])
            self.assertTrue(all(r['result'] == 'pass' for r in recovered['rows']))
            self.assertEqual('entry-transition', self.product().verify_workspace_product(target)['binding_ref']['id'])
            self.assertEqual(request_bytes, canonical(preview))
            for name, value in before.items():
                if name != '.hrn/product/binding.json': self.assertEqual(value, snapshot(target)[name], name)

        def test_remaining_recovery_release_parent_unavailable(self):
            self.remaining_recovery_fault('recovery_release_parent', 'unavailable')

        def test_remaining_recovery_release_parent_oserror(self):
            self.remaining_recovery_fault('recovery_release_parent', 'oserror')

        def test_remaining_recovery_operation_parent_unavailable(self):
            self.remaining_recovery_fault('recovery_operation_parent', 'unavailable')

        def test_remaining_recovery_operation_parent_oserror(self):
            self.remaining_recovery_fault('recovery_operation_parent', 'oserror')

        def test_remaining_recovery_new_parent_unavailable(self):
            self.remaining_recovery_fault('recovery_new_parent', 'unavailable')

        def test_remaining_recovery_new_parent_oserror(self):
            self.remaining_recovery_fault('recovery_new_parent', 'oserror')

        def test_remaining_recovery_old_parent_unavailable(self):
            self.remaining_recovery_fault('recovery_old_parent', 'unavailable')

        def test_remaining_recovery_old_parent_oserror(self):
            self.remaining_recovery_fault('recovery_old_parent', 'oserror')


        def writer_request(self, target, kind, entry):
            if kind == 'intent':
                return ['intent', 'draft'], {'record_type': 'intent-draft', 'schema_version': 1,
                    'authority_home_id': 'fixture-home', 'intent_id': 'fence-intent', 'revision_id': 'fence-draft',
                    'sequence': 1, 'prior_revision_ref': None, 'actor': 'agent', 'acceptance_authority': 'owner',
                    'observed_at': FIXTURE_TIME, 'facets': {k: {'status': 'known', 'value': 'fixture'} for k in
                        ('acceptance_oracle', 'destination', 'expected_outcome', 'forbidden_scope', 'goal', 'scope')},
                    'gaps': [], 'statements': [], 'route': 'direct-entry'}
            if kind == 'candidate':
                from hv2ref.candidates import read_candidates
                return ['candidate', 'add'], {'record_type': 'candidate-request', 'schema_version': 1,
                    'authority_home_id': 'fixture-home', 'request_id': 'fence-add', 'candidate_id': 'fence-candidate',
                    'action': 'add', 'expected_sha256': read_candidates(target)['sha256'], 'writer': 'agent:fixture',
                    'owner_statement': 'synthetic explicit fixture request', 'reason': 'writer fence fixture',
                    'observed_at': FIXTURE_TIME, 'payload': {'title': 'fixture', 'purpose': 'writer fence',
                        'expected_effect': 'preserved refusal', 'related_candidates': []}}
            if kind == 'work':
                from hv2ref.work import read_work
                graph = read_work(target, 'local-work'); prior = graph['current']['selection_ref']
                revision = copy.deepcopy(graph['revisions'][graph['selections'][prior['id']]['revision_ref']['id']])
                revision.update(record_id='fence-submit', operation='submit-result', expected_prior_selection=prior,
                    progress='review', next_action='fixture Owner review')
                manifest = graph['manifests'][revision['result_refs']['manifest']['id']]
                return ['work', 'publish'], {'identity': graph['identity'], 'revision': revision, 'manifest': manifest,
                    'selection_id': 'fence-selection', 'operation_id': 'fence-publish'}
            self.assertEqual('lifecycle', kind)
            code, data, _ = self.call(target, ['detach', '--operation-id', 'fence-detach', '--observed-at', FIXTURE_TIME], entry=entry)
            self.assertEqual(0, code, data); preview = json.loads(data)
            return ['detach', '--apply', '--input', '-', '--confirm', preview['confirm_token']], preview['request']

        def writer_fixture(self, name, kind, *, new=False):
            target = self.old_target(name); self.old_local(target)
            if new:
                preview = self.transition(target)
                self.product().workspace_switch_apply(target, preview['request'], confirm_token=preview['confirm_token'], source=candidate_source)
            entry = 'installed-new' if new else 'installed-old'
            args, value = self.writer_request(target, kind, entry)
            return target, entry, args, value

        def writer_family_fence(self, kind):
            # The same valid installed writer is observed successful before its
            # pending-prefix refusals. Source record writers are unsupported.
            for new in (False, True):
                positive, entry, args, value = self.writer_fixture('positive-' + str(new), kind, new=new)
                before = snapshot(positive)
                code, data, events = self.call(positive, args, value, entry=entry)
                self.assertEqual(0, code, data); self.assertNotEqual(before, snapshot(positive))
                self.assertTrue({'lock-attempt', 'lock-acquired'} <= {r['event'] for r in self.event_rows(events)})
            for point in ('after-receipt', 'after-staged-inventory', 'after-staged-payload', 'after-release'):
                target, entry, args, value = self.writer_fixture(point, kind)
                request_bytes = canonical(value); preview = self.transition(target)
                self.interrupted_api(target, preview, point); before = snapshot(target)
                code, data, _ = self.call(target, args, value, entry=entry)
                self.assertEqual(65, code, data); error = json.loads(data)
                self.assertEqual('HV2-WORKSPACE-PRODUCT', error['code'])
                self.assertEqual('invalid receipt identity/schema', error['message'])
                self.assertEqual(before, snapshot(target)); self.assertEqual(request_bytes, canonical(value))

        def test_writer_family_intent_pending_fence(self):
            self.writer_family_fence('intent')

        def test_writer_family_candidate_pending_fence(self):
            self.writer_family_fence('candidate')

        def test_writer_family_work_pending_fence(self):
            self.writer_family_fence('work')

        def test_writer_family_lifecycle_pending_fence(self):
            self.writer_family_fence('lifecycle')

        def installed_old_writer_late_lock(self, kind):
            positive, entry, args, value = self.writer_fixture('positive', kind)
            code, data, events = self.call(positive, args, value, entry=entry)
            self.assertEqual(0, code, data)
            self.assertTrue({'lock-attempt', 'lock-acquired'} <= {r['event'] for r in self.event_rows(events)})
            target, entry, args, value = self.writer_fixture('target', kind)
            preview = self.transition(target); before = snapshot(target)
            prior = json.loads((target / '.hrn/product/binding.json').read_bytes()); plan = preview['request']
            binding = {'record_type': 'product-binding', 'schema_version': 1, 'authority_home_id': plan['authority_home_id'],
                'active_release': plan['candidate_release'], 'prior_release': prior['active_release'], 'operation_id': plan['operation_id']}
            receipt = {'record_type': 'lifecycle-receipt', 'schema_version': 2, 'operation_id': plan['operation_id'],
                'plan': plan, 'prior_binding_ref': ref(prior, 'operation_id'), 'result_binding_ref': ref(binding, 'operation_id')}
            fault = {'event': 'fsync-after', 'path': '.hrn/product/receipts/entry-transition.json', 'occurrence': 1, 'write_bytes': None}
            new_child, new_log, new_events, ready, release, _ = self.call(target, self.apply_args(target, preview), preview['request'], fault=fault, pause=True)
            token = self.wait_ready(new_child, ready, target)
            command, events, _, _, _ = self.scenario(target, entry=entry, argv=args, pause=False)
            old_child, old_log = self.spawn(command, 'late-installed-old-' + kind, value)
            deadline = time.monotonic() + self.remaining(60)
            while not events.exists() or not any(r['event'] == 'lock-attempt' for r in self.event_rows(events)):
                self.assertIsNone(old_child.poll()); self.assertLess(time.monotonic(), deadline); time.sleep(0.02)
            self.assertFalse(any(r['event'] == 'lock-acquired' for r in self.event_rows(events)))
            self.release_pause(release, token); self.finish(new_child, new_log, timeout=150, expected=-signal.SIGKILL)
            code, data = self.finish(old_child, old_log, timeout=150, expected=65)
            error = json.loads(data); self.assertEqual('HV2-WORKSPACE-PRODUCT', error['code'])
            self.assertEqual('invalid receipt identity/schema', error['message'])
            after = snapshot(target); receipt_name = '.hrn/product/receipts/entry-transition.json'
            self.assertEqual(set(before) | {receipt_name}, set(after))
            self.assertEqual(before, {n: v for n, v in after.items() if n != receipt_name})
            self.assertEqual(canonical(receipt), (target / receipt_name).read_bytes())
            rows = self.event_rows(events); attempt = next(r for r in rows if r['event'] == 'lock-attempt')
            acquired = next(r for r in rows if r['event'] == 'lock-acquired')
            self.assertEqual(old_child.pid, attempt['pid']); self.assertEqual(attempt['detail'], acquired['detail'])
            self.assertEqual((token['lock']['dev'], token['lock']['ino']), (attempt['detail']['dev'], attempt['detail']['ino']))
            self.assertLess(attempt['seq'], acquired['seq'])
            self.assertGreaterEqual(acquired['monotonic_ns'], self.event_rows(new_events)[-1]['monotonic_ns'])

        def test_installed_old_intent_late_lock(self):
            self.installed_old_writer_late_lock('intent')

        def test_installed_old_candidate_late_lock(self):
            self.installed_old_writer_late_lock('candidate')

        def test_installed_old_work_late_lock(self):
            self.installed_old_writer_late_lock('work')

        def test_installed_old_lifecycle_late_lock(self):
            self.installed_old_writer_late_lock('lifecycle')

        def test_four_executor_entry_boundaries(self):
            target = self.old_target(); preview = self.transition(target)
            # Explicit trusted sources both read S0. The installed NEW entry does
            # not exist at S0; its absence is not a writer-fence success.
            before = snapshot(target)
            for selector in ('old-source', 'new-source', 'installed-old'):
                args = ['status'] if selector.startswith('installed') else ['--source-checkout', 'status', '--target', target]
                code, data, _ = self.call(target, args, entry=selector)
                self.assertEqual(0, code, data); self.assertEqual('pass', json.loads(data)['classification'])
                self.assertEqual(before, snapshot(target))
            self.assertFalse((target / 'colvia').exists())
            # Source mode does not expose installed record commands. Count its
            # parser refusal separately from a valid writer under a guard.
            for selector in ('old-source', 'new-source'):
                for family in ('intent', 'work', 'candidate'):
                    action = {'intent': 'draft', 'work': 'publish', 'candidate': 'add'}[family]
                    code, data, _ = self.call(target, ['--source-checkout', family, action, '--target', target], {}, entry=selector)
                    self.assertEqual(2, code, data); self.assertIn(b'invalid choice', data)
                    self.assertEqual(before, snapshot(target))
            self.interrupted_api(target, preview, 'after-launcher'); before = snapshot(target)
            self.assertFalse((target / 'hv2').exists()); self.assertTrue((target / 'colvia').is_file())
            code, data, _ = self.call(target, ['status'], entry='installed-new')
            self.assertEqual(65, code, data); self.assertEqual('HV2-WORKSPACE-LAUNCHER', json.loads(data)['code'])
            self.assertEqual(before, snapshot(target))
            code, data, _ = self.call(target, self.apply_args(target, preview, recover=True), preview['request'])
            self.assertEqual(0, code, data)
            before = snapshot(target)
            for selector in ('new-source', 'installed-new'):
                args = ['status'] if selector == 'installed-new' else ['--source-checkout', 'status', '--target', target]
                code, data, _ = self.call(target, args, entry=selector)
                self.assertEqual(0, code, data); self.assertEqual('pass', json.loads(data)['classification'])
                self.assertEqual(before, snapshot(target))
            self.assertFalse((target / 'hv2').exists())


    class EntryFoundationTests(FixtureBase):
        verification_stage = "p1"
        COORDINATOR_SECONDS = 180
        product = EntryProductTests.product
        call = EntryProductTests.call
        new_init = EntryProductTests.new_init

        def auditor(self, target, expected):
            child,log=self.spawn((ctx['runtime_path'],'-I','-S','-B',
                candidate_source/'tests/fixtures/product_plain_auditor.py',target),'plain-auditor')
            _,data=self.finish(child,log,timeout=30,expected=expected)
            return json.loads(data)

        def test_literal_windows_and_source_identity(self):
            product=self.product()
            self.assertEqual(OLD_PATHS,product.SERIAL_MANAGED_PATHS)
            self.assertEqual(tuple(p for p in OLD_PATHS if p!='src/hv2ref/candidates.py'),product.UMBRELLA_MANAGED_PATHS)
            self.assertEqual(tuple(p for p in OLD_PATHS if p not in ('src/hv2ref/candidates.py','src/hv2ref/umbrella.py')),product.LEGACY_MANAGED_PATHS)
            new=product.workspace_candidate(candidate_source)
            self.assertEqual(29,len(new['inventory']['entries']))
            expected=tuple(sorted((set(OLD_PATHS)-{'hv2','adapters/harness-v2-work/SKILL.md'})|{'colvia','adapters/colvia-work/SKILL.md'},key=lambda n:n.encode()))
            self.assertEqual(expected,tuple(e['path'] for e in new['inventory']['entries']))
            from hv2ref.errors import ContractError
            for window in ('human-1','worker-1','umbrella-1','planning-1','checkout-1','unknown'):
                with self.subTest(window=window):
                    raw=('WORKSPACE_INVENTORY_ID = '+repr(window)+'\n').encode()
                    with self.assertRaises(ContractError):product._launcher_inventory_window(raw)
            self.assertEqual('checkout-1',product._launcher_inventory_window((old_source/'hv2').read_bytes(),allow_legacy=True))
            from hv2ref.work import _verified_launcher_path
            for window,launcher in product.WINDOW_LAUNCHERS.items():
                self.assertEqual(launcher,_verified_launcher_path('0'*64,window))

        def test_fresh_git_and_non_git_init_installed_reader(self):
            for kind in ('git','non-git'):
                target=self.directory(kind)
                if kind=='git':
                    child,log=self.spawn((config['git']['path'],'init','-q',target),'git-init')
                    self.finish(child,log,timeout=15)
                write_file(target/'project.txt',b'preserved project\n')
                self.new_init(target)
                self.assertFalse((target/'hv2').exists())
                self.assertEqual(0o755,stat.S_IMODE((target/'colvia').stat().st_mode))
                self.assertEqual(b'preserved project\n',(target/'project.txt').read_bytes())
                code,data,_=self.call(target,['status'],entry='installed-new')
                self.assertEqual(0,code,data);self.assertEqual('pass',json.loads(data)['classification'])

        def test_initial_retired_occupants_refuse_without_writes(self):
            product=self.product()
            from hv2ref.errors import ContractError
            for number,(name,kind) in enumerate((('hv2','file'),('HV2','file'),('hv2','directory'),('hv2','dangling'))):
                target=self.directory('occupant-'+str(number))
                if kind=='file':write_file(target/name,b'project bytes\n')
                elif kind=='directory':(target/name).mkdir()
                else:(target/name).symlink_to('missing')
                before=snapshot(target)
                with self.assertRaises(ContractError) as caught:
                    product.workspace_init_preview(candidate_source,target,authority_home_id='fixture-home',operation_id='entry-init',created_at=FIXTURE_TIME)
                self.assertEqual('HV2-WORKSPACE-PRODUCT',caught.exception.code)
                self.assertIn(repr([name]),caught.exception.message)
                self.assertEqual(before,snapshot(target))

        def test_init_index_and_ignore_admission(self):
            product=self.product()
            from hv2ref.errors import ContractError
            for label,name in (('exact','colvia'),('alias','COLVIA'),('descendant','colvia/file')):
                target=self.directory(label)
                child,log=self.spawn((config['git']['path'],'init','-q',target),'git-init');self.finish(child,log,timeout=15)
                write_file(target/name,b'index-only collision\n')
                child,log=self.spawn((config['git']['path'],'-C',target,'add','--',name),'git-add');self.finish(child,log,timeout=15)
                (target/name).unlink()
                if '/' in name:(target/'colvia').rmdir()
                before=snapshot(target)
                with self.assertRaises(ContractError) as caught:product.workspace_init_preview(candidate_source,target,authority_home_id='fixture-home',operation_id='entry-init',created_at=FIXTURE_TIME)
                self.assertEqual('HV2-WORKSPACE-PRODUCT',caught.exception.code)
                self.assertIn('tracked',caught.exception.message)
                self.assertEqual(before,snapshot(target))
            target=self.directory('ignored')
            child,log=self.spawn((config['git']['path'],'init','-q',target),'git-init');self.finish(child,log,timeout=15)
            write_file(target/'.gitignore',b'colvia\n');before=snapshot(target)
            with self.assertRaises(ContractError) as caught:product.workspace_init_preview(candidate_source,target,authority_home_id='fixture-home',operation_id='entry-init',created_at=FIXTURE_TIME)
            self.assertIn('truth hidden by effective Git ignore policy',caught.exception.message)
            self.assertEqual(before,snapshot(target))
            positive=self.directory('unrelated-index')
            child,log=self.spawn((config['git']['path'],'init','-q',positive),'git-init');self.finish(child,log,timeout=15)
            write_file(positive/'unrelated',b'index only\n')
            child,log=self.spawn((config['git']['path'],'-C',positive,'add','--','unrelated'),'git-add');self.finish(child,log,timeout=15)
            (positive/'unrelated').unlink();before=snapshot(positive)
            product.workspace_init_preview(candidate_source,positive,authority_home_id='fixture-home',operation_id='entry-init',created_at=FIXTURE_TIME)
            self.assertEqual(before,snapshot(positive))

        def test_exact_init_prefixes_recover_and_replay(self):
            product=self.product()
            from hv2ref.errors import InjectedCrash
            for point in ('after-plan','after-work','after-staged-inventory','after-staged-payload','after-release','after-receipt','after-launcher-bytes','after-launcher','after-binding'):
                with self.subTest(point=point):
                    target=self.directory(point)
                    preview=product.workspace_init_preview(candidate_source,target,authority_home_id='fixture-home',operation_id='entry-init',created_at=FIXTURE_TIME)
                    with self.assertRaises(InjectedCrash) as caught:
                        product.workspace_init_apply(candidate_source,target,preview['request'],confirm_token=preview['confirm_token'],inject_at=point)
                    self.assertEqual(point,caught.exception.point)
                    product.workspace_init_apply(candidate_source,target,preview['request'],confirm_token=preview['confirm_token'],recover=True)
                    before=snapshot(target)
                    replay=product.workspace_init_apply(candidate_source,target,preview['request'],confirm_token=preview['confirm_token'])
                    self.assertIs(replay['replayed'],True);self.assertEqual(before,snapshot(target))
                    self.assertEqual('entry-1',product.verify_workspace_product(target)['inventory']['inventory_id'])

        def test_init_recovery_and_completed_replay_preserve_collision(self):
            product=self.product()
            from hv2ref.errors import ContractError,InjectedCrash
            for label in ('prefix','complete'):
                target=self.directory(label)
                preview=product.workspace_init_preview(candidate_source,target,authority_home_id='fixture-home',operation_id='entry-init',created_at=FIXTURE_TIME)
                if label=='prefix':
                    with self.assertRaises(InjectedCrash):product.workspace_init_apply(candidate_source,target,preview['request'],confirm_token=preview['confirm_token'],inject_at='after-receipt')
                else:product.workspace_init_apply(candidate_source,target,preview['request'],confirm_token=preview['confirm_token'])
                write_file(target/'hv2',b'late project occupant\n');before=snapshot(target)
                with self.assertRaises(ContractError) as caught:
                    product.workspace_init_apply(candidate_source,target,preview['request'],confirm_token=preview['confirm_token'],recover=True)
                self.assertEqual('HV2-WORKSPACE-PRODUCT',caught.exception.code);self.assertEqual(before,snapshot(target))

        def test_late_init_collision_preserves_exact_bootstrap_prefix(self):
            from unittest.mock import patch
            import hv2ref.workspace as workspace
            from hv2ref.errors import ContractError
            product=self.product();target=self.directory('target')
            preview=product.workspace_init_preview(candidate_source,target,authority_home_id='fixture-home',operation_id='entry-init',created_at=FIXTURE_TIME)
            original=workspace.bootstrap_root;observed={}
            def collide(*args,**kwargs):
                result=original(*args,**kwargs)
                write_file(target/'hv2',b'appeared after bootstrap\n')
                observed.update(snapshot(target))
                return result
            with patch.object(workspace,'bootstrap_root',collide):
                with self.assertRaises(ContractError) as caught:
                    product.workspace_init_apply(candidate_source,target,preview['request'],confirm_token=preview['confirm_token'])
            self.assertEqual('HV2-WORKSPACE-PRODUCT',caught.exception.code)
            after=snapshot(target);anchors={'.hrn/locks','.hrn/locks/writer.lock'}
            self.assertEqual(observed,{k:v for k,v in after.items() if k in observed})
            self.assertLessEqual(set(after)-set(observed),anchors)
            if '.hrn/locks/writer.lock' in after:
                self.assertEqual(b'',(target/'.hrn/locks/writer.lock').read_bytes())
                self.assertEqual(1,(target/'.hrn/locks/writer.lock').stat().st_nlink)
            self.assertFalse((target/'.hrn/product/binding.json').exists())
            self.assertFalse((target/'colvia').exists())
            for label in ('alias','index'):
                target=self.directory('late-'+label)
                if label=='index':
                    child,log=self.spawn((config['git']['path'],'init','-q',target),'git-init');self.finish(child,log,timeout=15)
                preview=product.workspace_init_preview(candidate_source,target,authority_home_id='fixture-home',operation_id='entry-init',created_at=FIXTURE_TIME)
                from hv2ref.errors import InjectedCrash
                with self.assertRaises(InjectedCrash):product.workspace_init_apply(candidate_source,target,preview['request'],confirm_token=preview['confirm_token'],inject_at='after-plan')
                write_file(target/'COLVIA',b'late occupant\n')
                if label=='index':
                    child,log=self.spawn((config['git']['path'],'-C',target,'add','--','COLVIA'),'git-add');self.finish(child,log,timeout=15)
                    (target/'COLVIA').unlink()
                before=snapshot(target)
                with self.assertRaises(ContractError) as caught:product.workspace_init_apply(candidate_source,target,preview['request'],confirm_token=preview['confirm_token'],recover=True)
                self.assertEqual('HV2-WORKSPACE-PRODUCT',caught.exception.code)
                self.assertIn('alias',caught.exception.message)
                self.assertEqual(before,snapshot(target))

        def test_verified_window_exclusion_preserves_retired_project_file(self):
            from hv2ref.work import snapshot as content_snapshot
            from hv2ref.errors import ContractError
            target=self.directory('target');self.new_init(target)
            observed=self.product().verify_workspace_product(target)
            write_file(target/'hv2',b'project-owned retired entry\n')
            tree=content_snapshot(target,verified_launcher_sha256=observed['launcher_sha256'],verified_inventory_id='entry-1')
            self.assertEqual(['hv2'],[e['path'] for e in tree['entries']])
            self.assertEqual(sha(b'project-owned retired entry\n'),tree['entries'][0]['sha256'])
            for window in (None,'unknown','checkout-1'):
                with self.assertRaises(ContractError):content_snapshot(target,verified_launcher_sha256=observed['launcher_sha256'],verified_inventory_id=window)
            unexcluded=content_snapshot(target)
            self.assertEqual(['colvia','hv2'],[e['path'] for e in unexcluded['entries']])

        def test_required_refs_and_runtime_test_seam(self):
            from hv2ref.work import _live_external_refs,WorkStore
            from hv2ref.errors import ContractError
            target=self.directory('target');self.new_init(target)
            product=self.product().verify_workspace_product(target);digest=product['launcher_sha256']
            write_file(target/'hv2',b'project data\n')
            revision={'document_refs':[{'path':'hv2','sha256':sha(b'project data\n'),'required':True}],'evidence_refs':[]}
            _live_external_refs(target,revision,digest,verified_inventory_id='entry-1')
            revision['document_refs'][0]={'path':'colvia','sha256':digest,'required':True}
            with self.assertRaises(ContractError):_live_external_refs(target,revision,digest,verified_inventory_id='entry-1')
            _live_external_refs(target,revision,None)  # Explicit historical/no-exclusion seam.
            runtime={'binding_ref':product['binding_ref'],'launcher_sha256':None}
            self.assertEqual(runtime,WorkStore(target,runtime_check=lambda _:runtime)._runtime())
            runtime={**runtime,'launcher_sha256':digest}
            with self.assertRaises(ContractError):WorkStore(target,runtime_check=lambda _:runtime)._runtime()
            runtime={**runtime,'inventory_id':'entry-1'}
            self.assertEqual(runtime,WorkStore(target,runtime_check=lambda _:runtime)._runtime())

        def test_historical_detach_reader_and_independent_auditor(self):
            product=self.product()
            for version in (1,2):
                target=self.directory('schema-'+str(version))
                if version==1:schema1_fixture(target)
                else:self.fixed_old(target,detach=True)
                before=snapshot(target)
                self.assertEqual('partial',product.workspace_detached_status(target)['classification'])
                self.assertEqual('partial',self.auditor(target,14)['classification'])
                self.assertEqual(before,snapshot(target))

        def test_schema1_malformed_pair_membership_and_suffix_refuse(self):
            product=self.product();target=self.directory('schema1');fixture=schema1_fixture(target)
            from hv2ref.errors import ContractError
            path=target/'.hrn/detached.json';raw=path.read_bytes()
            cases=[]
            for outer,inner in ((1,3),(2,1),(3,1),(True,True),(4,4)):
                value=copy.deepcopy(fixture['receipt']);value['schema_version']=outer;value['plan']['schema_version']=inner;cases.append(value)
            for mutation in ('digest','member','order','new-entry'):
                value=copy.deepcopy(fixture['receipt'])
                if mutation=='digest':value['plan']['remove'][0]['sha256']='0'*64
                elif mutation=='member':value['plan']['remove']=value['plan']['remove'][1:]
                elif mutation=='order':value['plan']['remove'].reverse()
                else:next(e for e in value['plan']['remove'] if e['path']=='hv2')['path']='colvia'
                cases.append(value)
            for number,value in enumerate(cases):
                with self.subTest(number=number):
                    path.write_bytes(canonical(value));before=snapshot(target)
                    with self.assertRaises(ContractError):product.workspace_detached_status(target)
                    self.assertEqual('degraded',self.auditor(target,10)['classification']);self.assertEqual(before,snapshot(target))
            path.write_bytes(raw);(target/fixture['remove_order'][2]).unlink();before=snapshot(target)
            with self.assertRaises(ContractError):product.workspace_detached_status(target)
            self.assertEqual('degraded',self.auditor(target,10)['classification']);self.assertEqual(before,snapshot(target))

    # Stable module/class/method IDs; locals never become default discovery cases.
    for cls in (FixtureBase,EntryControlTests,OldFixtureTests,EntryProductTests,EntryFoundationTests):
        cls.__qualname__=cls.__name__
    loader=unittest.TestLoader()
    suites=[loader.loadTestsFromTestCase(cls) for cls in (EntryControlTests,OldFixtureTests,EntryProductTests,EntryFoundationTests)]
    need(not loader.errors,'factory load errors')
    return unittest.TestSuite(suites)
