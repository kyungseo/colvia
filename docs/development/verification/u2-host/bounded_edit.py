"""Bounded effect host over the existing document controller; never applies authority."""
from copy import deepcopy
from pathlib import Path
import time
import unicodedata

from .contracts import (require, HostRefusal, canonical, wire_bytes, core_bytes, digest, control_read, checked_open,
                        durable_private, DocumentController, EffectJournal, pack_reads, document_record)
from .execution_os import execution_os
from .adapters import edit_codex_contract as policy


def prepare_scope(cfg, snapshot_reader, baseline_reader):
    """Validate task data before activation. Readers are trusted functions, never loaded from input."""
    policy.exact(cfg, ('core_project', 'core_snapshot_sha256', 'worker_root', 'worker_base_commit',
                      'worker_snapshot_sha256', 'identity', 'documents', 'read_ids', 'owner_input', 'owner_input_sha256'), 'edit-config-fields')
    identity, docs, ids = cfg['identity'], cfg['documents'], cfg['read_ids']
    policy.exact(identity, ('approval', 'home', 'work', 'actor', 'action', 'intent_sha256', 'scope_identity'), 'edit-identity-fields')
    actor = identity['actor']
    require(policy.text(actor) and actor == actor.strip() and not any(unicodedata.category(c).startswith('C') for c in actor)
            and unicodedata.normalize('NFKC', actor).casefold() not in ('owner', 'human')
            and identity['action'] == 'edit-only' and identity['approval'].startswith('owner-edit-'), 'edit-authority-boundary')
    require(docs.get('contract_version') == 2 and docs.get('writer_attestation') is True
            and type(docs['outputs']) is list and len(docs['outputs']) == 1, 'edit-one-output')
    require(type(ids) is list and 1 <= len(ids) <= 8 and all(policy.text(k) for k in ids)
            and len(set(ids)) == len(ids) and set(ids) == set(docs['files']), 'edit-read-scope')
    require(set(docs['view_contracts']) == set(ids) and set(docs['source_digests']) == set(ids), 'edit-file-coverage')
    root = Path(cfg['worker_root'])
    require(root.is_absolute() and root.resolve(strict=True) == root, 'edit-worker-root')
    base = baseline_reader(root)
    require(base['commit'] == cfg['worker_base_commit'] and digest(canonical(base['snapshot'])) == cfg['worker_snapshot_sha256'], 'edit-worker-baseline-drift')
    snapshot = snapshot_reader(cfg['core_project'], identity['work'])
    require(digest(canonical(snapshot)) == cfg['core_snapshot_sha256'] and snapshot['home'] == identity['home']
            and snapshot['work'] == identity['work'] and digest(canonical(snapshot['intent_ref'])) == identity['intent_sha256'], 'edit-core-binding')
    require(digest(control_read(cfg['owner_input'], 65_536)) == cfg['owner_input_sha256'], 'edit-owner-input-drift')
    output = docs['outputs'][0]
    require(output in ids, 'edit-output-not-read')
    entry, view = docs['files'][output], docs['view_contracts'][output]
    require(entry['view']['kind'] == 'replace-range' and len(entry['view']['ranges']) == 1
            and view['initial_state'] == 'present' and entry['view'] == view['view']
            and Path(entry['path']).is_relative_to(root) and entry['identity'] is not None, 'edit-existing-range')
    for key, item in docs['files'].items():
        observed, raw = document_record(item)
        require(observed == item and docs['source_digests'][key] == item['sha256'], 'edit-file-drift')
        if key != output:
            require(item['view']['kind'] != 'replace-range', 'edit-extra-editable-input')
    _, raw = document_record(entry)
    begin, end = entry['view']['ranges'][0]
    require(digest(raw[:begin]) == view['prefix_sha256'] and digest(raw[end:]) == view['suffix_sha256'], 'edit-range-binding')
    scope = {'paths': {key: value['path'] for key, value in docs['files'].items()}, 'outputs': docs['outputs'], 'views': docs['view_contracts']}
    require(identity['scope_identity'] == digest(wire_bytes(scope)), 'edit-approved-scope')
    # This uses the actual controller packer, including provenance envelope overhead.
    require(pack_reads(docs['files'], origin={'sources': docs['source_digests'], 'approval': identity['approval']}) == [ids], 'edit-single-ordered-pack')
    for k in ('python', 'worker', 'parser', 'profile_template'):
        p = Path(docs[k])
        require(p.resolve(strict=True) == p and digest(p.read_bytes()) == docs[k + '_sha256'], 'edit-worker-dependency-drift')
    result = {'home': identity['home'], 'work': identity['work'], 'intent_sha256': identity['intent_sha256'],
              'core_snapshot_sha256': cfg['core_snapshot_sha256'], 'worker_root': str(root),
              'worker_base_commit': cfg['worker_base_commit'], 'worker_snapshot_sha256': cfg['worker_snapshot_sha256'],
              'identity_sha256': digest(canonical(identity)), 'documents_sha256': digest(canonical(docs)),
              'read_ids': ids, 'files': docs['source_digests'],
              'output': {'id': output, 'path': entry['path'], 'sha256': entry['sha256'], 'range': [begin, end],
                         'prefix_sha256': view['prefix_sha256'], 'suffix_sha256': view['suffix_sha256']},
              'verifier': {k + '_sha256': docs[k + '_sha256'] for k in ('python', 'worker', 'parser', 'profile_template')}}
    policy.scope_fields(result)
    return result


class EditWorkerBudget:
    def __init__(self, host):
        self.host = host
        self.anchor = host.budget.anchor

    def check_worker_result(self, subject, phase, start, timeout):
        h = self.host
        require(h.pending is not None and (phase, start) == (policy.PHASE, policy.START), 'edit-worker-unreserved')
        remaining = min(h.deadline - time.monotonic(), (h.budget.read()['remaining_ms'] - policy.RESERVE_MS) / 1000)
        require(timeout > 0 and remaining > 20, 'edit-worker-deadline')
        return min(timeout, 300, remaining - 20)

    def reserve(self, kind, subject, phase, start):
        h = self.host
        require((phase, start) == (policy.PHASE, policy.START), 'edit-worker-phase')
        if kind == 'worker-result':
            require(h.pending is not None and not h.worker_reported, 'edit-worker-result-order')
            row = h.journal.append(kind, subject)
            h.worker_reported = row
            return row
        require(kind == 'seal' and h.pending is None and h.completed == 5, 'edit-no-correction-or-authority')
        return h.journal.append(kind, subject)


class BoundedEditHost:
    def __init__(self, cfg, budget, run, snapshot_reader, baseline_reader, deadline):
        self.os = execution_os(require, purpose='codex-v58')  # Existing native capability preflight.
        self.cfg, self.budget = deepcopy(cfg), budget
        self.cfg_sha256 = digest(canonical(cfg))
        self.snapshot_reader, self.baseline_reader = snapshot_reader, baseline_reader
        self.deadline = deadline
        require(prepare_scope(cfg, snapshot_reader, baseline_reader) == budget.anchor['edit_scope'], 'edit-activation-scope-drift')
        require(budget.anchor['input_identity'] == digest(canonical(cfg)), 'edit-task-input-drift')
        self.baseline = baseline_reader(Path(cfg['worker_root']))
        require(self.baseline['commit'] == cfg['worker_base_commit']
                and digest(canonical(self.baseline['snapshot'])) == cfg['worker_snapshot_sha256'], 'edit-worker-baseline-drift')
        self.run = Path(run)
        self.os.private_directory(self.run, resume=False)
        durable_private(self.run / 'controller.lock', {})
        self.lock = self.os.controller_lock(self.run / 'controller.lock', checked_open, require)
        self.pending, self.worker_reported, self.last_terminal = None, None, None
        self.completed, self.stopped, self.seen = 0, False, set()
        self.controller = None
        try:
            self.journal = EffectJournal(self.run / 'journal.jsonl', create=True)
            self.journal.append('anchor', {'config_sha256': self.cfg_sha256, 'budget_anchor_sha256': budget.anchor_sha256})
            wd = self.run / 'workers'
            wd.mkdir(mode=0o700)
            scratch = Path(cfg['documents']['scratch'])
            require(not scratch.exists() and scratch.parent.resolve(strict=True) == scratch.parent, 'edit-scratch-collision')
            scratch.mkdir(mode=0o700)
            self.controller = DocumentController(cfg['documents'], wd, EditWorkerBudget(self), policy.PHASE, policy.START, deadline)
            require(self.controller.scope_sha256 == cfg['identity']['scope_identity']
                    and self.controller.read_packs == [cfg['read_ids']], 'edit-controller-scope')
        except BaseException:
            self.lock.close()
            raise

    def check_core(self):
        require(time.monotonic() < self.deadline and digest(canonical(self.cfg)) == self.cfg_sha256, 'edit-host-drift-or-deadline')
        value = self.snapshot_reader(self.cfg['core_project'], self.cfg['identity']['work'])
        require(digest(canonical(value)) == self.cfg['core_snapshot_sha256'], 'edit-core-state-drift')
        base = self.baseline_reader(Path(self.cfg['worker_root']))
        expected = deepcopy(self.baseline)
        if self.controller is not None:
            self.controller.check_files()
            output = self.cfg['documents']['outputs'][0]
            record, raw = document_record(self.controller.files[output])
            relative = str(Path(record['path']).relative_to(self.cfg['worker_root']))
            entries = expected['snapshot']['entries']
            selected = [entry for entry in entries if entry['path'] == relative]
            require(len(selected) == 1, 'edit-output-not-in-worker-baseline')
            selected[0].update(sha256=record['sha256'], size_bytes=len(raw))
            # Preserve Core's separate, indented canonical tree identity.
            tree = {k: v for k, v in expected['snapshot'].items() if k != 'sha256'}
            expected['snapshot']['sha256'] = digest(core_bytes(tree))
        require(base == expected, 'edit-worker-outside-scope-drift')
        return value

    def dispatch(self, envelope):
        require(not self.stopped and self.pending is None and self.completed < 5, 'edit-host-stopped-or-pending')
        self.check_core()
        policy.exact(envelope, ('session', 'step', 'call_id', 'tool', 'arguments', 'identity'), 'edit-request-fields')
        require(envelope['identity'] == self.cfg['identity'] and all(policy.text(envelope[k]) for k in ('session', 'step', 'call_id'))
                and envelope['call_id'] not in self.seen, 'edit-request-identity')
        self.seen.add(envelope['call_id'])
        request = self.journal.append('request', envelope)
        self.pending, self.worker_reported = request, None
        tool, args = envelope['tool'], envelope['arguments']
        try:
            wanted, verifier = policy.STEPS[self.completed]
            require(tool == wanted and type(args) is dict, 'edit-request-order')
            if self.completed == 0:
                require(args == {'file_ids': self.cfg['read_ids']}, 'edit-exact-read-order')
            elif self.completed == 1:
                require(set(args) == {'file_id', 'expected_sha256', 'content'} and args['file_id'] == self.cfg['documents']['outputs'][0]
                        and args['expected_sha256'] == self.budget.anchor['edit_scope']['output']['sha256'], 'edit-exact-write')
            else:
                require(args == {'verifier_id': verifier}, 'edit-exact-verifier-order')
        except HostRefusal as error:
            self.last_terminal = self.journal.append('refused', {'request_seq': request['seq'], 'code': str(error), 'effects': 0})
            self.pending = None
            self.stopped = True
            return {'ok': False, 'code': str(error), 'request': request, 'terminal': self.last_terminal}
        # Worker failure after admission is unknown, never a safely refused effect.
        result = self.controller.dispatch(tool, args)
        require(self.worker_reported is not None, 'edit-worker-result-missing')
        self.check_core()
        self.last_terminal = self.journal.append('completed', {'request_seq': request['seq'],
            'worker_result_sha256': self.worker_reported['sha256'], 'result_sha256': digest(wire_bytes(result))})
        self.pending = None
        self.completed += 1
        return {'ok': True, 'result': result, 'request': request, 'terminal': self.last_terminal,
                'worker_result': self.worker_reported['value']}

    def seal(self):
        require(not self.stopped and self.pending is None and self.completed == 5, 'edit-seal-state')
        self.check_core()
        return self.controller.seal()

    def stop(self):
        self.stopped = True
        require(self.controller is None or self.controller.active is None, 'edit-worker-still-active')

    def close(self):
        self.lock.close()
