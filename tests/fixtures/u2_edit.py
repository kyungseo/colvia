"""Synthetic edit inputs and a real Git/Core baseline reader, without provider access."""
from copy import deepcopy
import importlib
import json
import os
from pathlib import Path
import subprocess
import time
import uuid

from tests.test_u2_adapters import host
from hv2ref import work

edit = host.edit_codex
policy = edit.policy
native = host.codex


def publish(path, value):
    host.durable_private(path, value)
    return {'path': str(path), 'sha256': host.digest(host.canonical(value))}


def baseline(root):
    # This is the actual Core snapshot, including two observations and native Git.
    snapshot = work.snapshot(Path(root))
    commit = work._git(Path(root), 'rev-parse', 'HEAD').stdout.decode().strip()
    return {'commit': commit, 'snapshot': snapshot}


def snapshot_reader(root, work_id):
    value = json.loads(host.control_read(Path(root) / 'synthetic-core.json'))
    host.require(value['work'] == work_id, 'synthetic-core-work')
    return value


def real_task(root, tag, count, resources):
    """Same factory for A/B. All task-dependent variation is input data."""
    root = Path(root)
    root.mkdir(mode=0o700)
    worker = root / 'worker'; worker.mkdir(mode=0o700)
    git = resources['git']
    env = {'PATH': '/usr/bin:/bin', 'HOME': str(root), 'TMPDIR': str(root), 'LANG': 'en_US.UTF-8',
           'GIT_CONFIG_NOSYSTEM': '1', 'GIT_CONFIG_GLOBAL': '/dev/null', 'GIT_CONFIG_SYSTEM': '/dev/null',
           'GIT_TERMINAL_PROMPT': '0'}
    def command(*args):
        result = subprocess.run([git, *args], cwd=worker, env=env, capture_output=True, timeout=20, check=True)
        return result.stdout.decode().strip()
    command('init', '-q')
    prefix = ('<!-- fixed ' + tag + ' prefix -->\n').encode()
    middle = ('# ' + tag + '\n\nPrior content.\n').encode()
    suffix = ('\n<!-- fixed ' + tag + ' suffix -->\n').encode()
    output_id = tag + 'Output'
    output = worker / (tag.lower() + '-document.md')
    output.write_bytes(prefix + middle + suffix)
    inputs = {output_id: output}
    for i in range(count - 1):
        key = tag + 'Reference' + str(i)
        path = worker / (tag.lower() + '-reference-' + str(i) + '.md')
        path.write_text('# Reference\n\nApproved fact for ' + tag + '.\n')
        inputs[key] = path
    command('add', '--', '.')
    command('-c', 'user.name=Synthetic Fixture', '-c', 'user.email=fixture@example.invalid',
            '-c', 'commit.gpgsign=false', 'commit', '-q', '-m', 'synthetic baseline')
    entries = {}
    for key in sorted(inputs):
        entry, _ = host.file_record(inputs[key], limit=131_072)
        entry['view'] = {'kind': 'replace-range', 'ranges': [[len(prefix), len(prefix) + len(middle)]]} if key == output_id else {'kind': 'full'}
        entries[key] = entry
    state = {'home': 'home-' + tag, 'work': 'work-' + tag, 'state': 'active',
             'intent_ref': {'id': 'intent-' + tag, 'sha256': host.digest(('intent-' + tag).encode())}}
    publish(root / 'synthetic-core.json', state)
    owner = root / 'owner-input.txt'
    owner.write_text('Replace the selected range with the approved fact for ' + tag + '.\n')
    owner.chmod(0o600)
    ref = next(key for key in entries if key != output_id)
    content = '# ' + tag + '\n\nApproved fact for ' + tag + '.\n\n[Reference](' + inputs[ref].name + ')\n'
    docs = {'contract_version': 2, 'files': entries, 'outputs': [output_id],
            'claims': {output_id: {'required': ['Approved fact for ' + tag + '.'], 'forbidden': ['Unapproved'],
                                   'evidence': [{'file_id': ref, 'quote': 'Approved fact for ' + tag + '.'}],
                                   'exact_view_sha256': host.digest(content.encode())}},
            'approved_external_links': [], 'allowed_identifiers': [], 'scratch': str(root / 'worker-scratch'),
            'writer_attestation': True, 'source_digests': {k: e['sha256'] for k, e in entries.items()},
            'view_contracts': host.initial_view_contracts(entries), 'link_metadata': {}}
    for k in ('python', 'worker', 'parser', 'profile_template'):
        docs[k], docs[k + '_sha256'] = resources[k], host.digest(Path(resources[k]).read_bytes())
    scope = {'paths': {k: e['path'] for k, e in entries.items()}, 'outputs': [output_id], 'views': docs['view_contracts']}
    identity = {'approval': 'owner-edit-' + tag, 'home': state['home'], 'work': state['work'],
                'actor': 'synthetic-editor-' + tag, 'action': 'edit-only',
                'intent_sha256': host.digest(host.canonical(state['intent_ref'])), 'scope_identity': host.digest(host.wire_bytes(scope))}
    base = baseline(worker)
    cfg = {'core_project': str(root), 'core_snapshot_sha256': host.digest(host.canonical(state)),
           'worker_root': str(worker), 'worker_base_commit': base['commit'], 'worker_snapshot_sha256': host.digest(host.canonical(base['snapshot'])),
           'identity': identity, 'documents': docs, 'read_ids': list(entries), 'owner_input': str(owner), 'owner_input_sha256': host.digest(owner.read_bytes())}
    publish(root / 'task-input.json', cfg)
    return cfg, content, prefix, suffix


def execution(root, tag, resources):
    now = time.time_ns() // 1_000_000
    prior = publish(Path(root) / 'prior-accounting.json', {'version': 1, 'synthetic': True, 'task': tag})
    snapshot = {'version': 1, 'record': prior, 'captured_wall_ms': now, 'total_cap_ms': 3_600_000,
                'charged_ms': 0, 'phase_cap_ms': 1_800_000, 'phase_charged_ms': 0,
                'counts': {k: 0 for k in policy.ALLOCATION}, 'limits': dict(policy.ALLOCATION), 'consumed_reservations': []}
    ref = publish(Path(root) / 'accounting-snapshot.json', snapshot)
    return {'kind': policy.KIND, 'model': policy.PROFILE['model'], 'effort': policy.PROFILE['effort'], 'platform': 'darwin',
            'binary': resources['binary'], 'binary_sha256': host.digest(Path(resources['binary']).read_bytes()),
            'source_identity': resources['source_identity'], 'auth_home': str(Path(root) / 'unused-auth'),
            'proxy_template': resources['proxy_template'], 'proxy_template_sha256': edit.PROXY_TEMPLATE_SHA256,
            'snapshot': ref, 'owner_message_id': tag, 'reservation_id': 'synthetic-' + tag,
            'run_id': str(uuid.uuid4()), 'approval_wall_ms': now}


def parent_and_admission(anchor, root, *, ledger=None):
    p = policy if anchor['version'] == 59 else host.fresh_codex.policy
    x = native.Budget.fresh_bound(anchor['activation'])
    snapshot = native.Budget.fresh_bound(anchor['accounting_snapshot'])
    lock = Path(root) / 'controller.lock'
    publish(lock, {'version': 1})
    if ledger is None:
        ledger = host.EffectJournal(Path(root) / 'task-ledger.jsonl', create=True)
    prefix = 'edit' if anchor['version'] == 59 else 'v58'
    ledger.append(prefix + '-parent-reservation', {'reservation_id': x['reservation_id'],
        'snapshot_sha256': anchor['accounting_snapshot']['sha256'], 'allocation': p.ALLOCATION,
        'owner_message_id': x['owner_message_id'], 'parent': p.KIND if prefix == 'edit' else 'C-Codex-live',
        'counts_before': snapshot['counts'], 'limits': snapshot['limits']})
    admission = {'version': 1, 'template_sha256': p.TEMPLATE_SHA256, 'activation_sha256': anchor['activation']['sha256'],
                 'candidate': anchor['candidate'], 'source_identity': anchor['source_identity'], 'input_identity': anchor['input_identity'],
                 'platform': 'darwin', 'profile': 'u2'}
    admission.update({'kind': p.KIND, 'phase': p.PHASE, 'execution_authorized': True} if prefix == 'edit' else {'C_live_authorized': True})
    return ledger, lock, lambda: deepcopy(admission)


def contract_on_disk(root, version=59, *, snapshot_changes=None, activation_changes=None):
    fixture = Path(__file__).parent / ('u2-edit-v59.json' if version == 59 else 'u2-fresh-v58.json')
    f = json.loads(fixture.read_bytes()); a = deepcopy(f['anchor']); docs = f['documents']
    root = Path(root); root.mkdir(mode=0o700)
    old = lambda key: deepcopy(docs[a[key]['path']])
    a['run_directory'] = str(root / 'epoch')
    a['execution_template'] = publish(root / 'template.json', old('execution_template'))
    snapshot = old('accounting_snapshot')
    snapshot['record'] = publish(root / 'prior.json', docs[snapshot['record']['path']])
    if snapshot_changes: snapshot.update(deepcopy(snapshot_changes))
    a['accounting_snapshot'] = publish(root / 'snapshot.json', snapshot)
    x = old('activation')
    for k in set(x) & set(a): x[k] = deepcopy(a[k])
    x['snapshot_sha256'] = a['accounting_snapshot']['sha256']
    if activation_changes: x.update(deepcopy(activation_changes))
    a['activation'] = publish(root / 'activation.json', x)
    a['consumption'] = {'path': str(root / 'consumption.json'), 'sha256': '0' * 64}
    return a
