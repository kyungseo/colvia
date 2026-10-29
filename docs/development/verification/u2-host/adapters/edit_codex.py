"""Reusable preparation and one-shot edit session. No model call occurs during preparation."""
from copy import deepcopy
import json
import os
from pathlib import Path
import time

from ..contracts import (require, HostRefusal, canonical, wire_bytes, digest, control_read, checked_open,
                        durable_private, EffectJournal, closed_environment, sb_literal, artifact_read, end_process)
from ..execution_os import execution_os
from ..bounded_edit import prepare_scope, BoundedEditHost
from . import codex as native
from . import edit_codex_contract as policy
from .consumption_guard import check_consumption

PROXY_TEMPLATE_SHA256 = '52ec50c182f61d4dd86df1909c6ea62658a64b1e84899b11ccee9d7ecea70c39'


def reference(path):
    return {'path': str(path), 'sha256': digest(control_read(path, 1_048_576))}


def prepare_execution(cfg, execution, destination, *, snapshot_reader, baseline_reader):
    """One materializer for every task; only data identities vary, never executable code.

    This creates a proposal, not a reservation or permission to consume it. The
    Owner-bound parent row and launch-admission callback remain caller-owned.
    """
    runtime = execution_os(require, purpose='codex-v58')
    policy.exact(execution, ('kind', 'model', 'effort', 'platform', 'binary', 'binary_sha256', 'source_identity',
                            'auth_home', 'proxy_template', 'proxy_template_sha256', 'snapshot', 'owner_message_id',
                            'reservation_id', 'run_id', 'approval_wall_ms'), 'edit-preparation-fields')
    require(execution['kind'] == policy.KIND and execution['model'] == policy.PROFILE['model']
            and execution['effort'] == policy.PROFILE['effort'] and execution['platform'] == 'darwin', 'edit-preparation-profile')
    require(cfg['identity']['approval'] == 'owner-edit-' + execution['owner_message_id'], 'edit-preparation-owner')
    scope = prepare_scope(cfg, snapshot_reader, baseline_reader)
    binary = Path(execution['binary'])
    require(binary.resolve(strict=True) == binary and digest(artifact_read(binary, executable=True)) == execution['binary_sha256'], 'edit-binary-drift')
    proxy_text = control_read(execution['proxy_template'], 1_048_576).decode()
    require(digest(proxy_text.encode()) == execution['proxy_template_sha256'] == PROXY_TEMPLATE_SHA256, 'edit-proxy-template-drift')
    snapshot = native.Budget.fresh_bound(execution['snapshot'])
    root = Path(destination)
    require(root.is_absolute() and root.parent.resolve(strict=True) == root.parent and not os.path.lexists(root), 'edit-preparation-destination')
    epoch, packet, native_root = root / 'epoch', root / 'packet', root / 'runtime' / policy.START
    contract_path, profile_path = root / 'launch-contract.json', root / 'proxy-role.sb'
    controls = [epoch / n for n in ('anchor.json', 'append.lock', 'journal.jsonl')]
    controls += [packet / n for n in ('template.json', 'activation.json', 'consumption.json')]
    controls += [Path(execution['snapshot']['path']), Path(snapshot['record']['path']), native_root / 'candidate-receipt.json']
    for rule in ('(allow network-bind (local tcp "127.0.0.1:38971"))',
                 '(allow network-inbound (local tcp "127.0.0.1:38971"))',
                 '(allow network-outbound (literal "/private/var/run/mDNSResponder"))'):
        require(proxy_text.count(rule) == 1, 'edit-proxy-template-network-drift')
        proxy_text = proxy_text.replace(rule, '')
    deps = [binary, profile_path, *controls, root / 'proxy' / policy.SLOT / 'spec.json', root / 'proxy' / policy.SLOT / 'tmp']
    ancestors = sorted({str(parent) for p in deps for parent in p.parents})
    marker = '; @@ANCESTOR_METADATA_LITERALS@@'
    ip_marker = '; @@RESOLVED_CHATGPT_PUBLIC_TCP443_LITERALS@@'
    require(proxy_text.count(marker) == proxy_text.count(ip_marker) == 1, 'edit-proxy-markers')
    proxy_text = proxy_text.replace(marker, '(allow file-read-metadata ' + ' '.join(sb_literal(p) for p in ancestors) + ')')
    proxy_text = proxy_text.replace(ip_marker, '; Connected descriptors only.')
    proxy_text += '\n(allow file-read* ' + ' '.join(sb_literal(str(p)) for p in controls) + ')\n'
    require('@@' not in proxy_text and '(allow network-' not in proxy_text and '(allow mach-' not in proxy_text, 'edit-proxy-permission-drift')
    env = closed_environment({'TMPDIR': str(native_root / 'tmp')})
    launch = {'argv': [str(binary), '--role', 'runtime', '--spec', str(native_root / 'spec.json')],
              'cwd': str(native_root / 'cwd'), 'environment_keys': sorted(env)}
    role = {'path': cfg['documents']['profile_template'], 'sha256': cfg['documents']['profile_template_sha256']}
    direct = {'version': 1, 'mode': 'direct', 'model': policy.PROFILE['model'], 'profiles': ['clock', 'u2'], 'approval': cfg['identity']['approval']}
    launch_contract = {'version': 2, 'launch_mode': 'trusted-native-runtime', 'candidate': execution['binary_sha256'],
                       'source_identity': execution['source_identity'], 'launches': {str(native_root / 'spec.json'): launch},
                       'network': {'host': 'chatgpt.com', 'port': 443, 'peer': policy.PEER}, 'direct_tool_policy': direct,
                       'roles': {'worker': role, 'verifier': role, 'proxy': {'path': str(profile_path), 'sha256': digest(proxy_text.encode())}}}
    origin = time.time_ns() // 1_000_000
    elapsed = origin - snapshot['captured_wall_ms']
    total = snapshot['total_cap_ms'] - snapshot['charged_ms'] - elapsed
    phase = snapshot['phase_cap_ms'] - snapshot['phase_charged_ms'] - elapsed
    a = {'version': policy.VERSION, 'kind': policy.KIND, 'run_id': execution['run_id'],
         'approval': cfg['identity']['approval'], 'work': 'u2-edit-' + execution['run_id'],
         'candidate': execution['binary_sha256'], 'source_identity': execution['source_identity'],
         'input_identity': digest(canonical(cfg)), 'launch_contract_sha256': digest(canonical(launch_contract)),
         'execution_template': {'path': str(packet / 'template.json'), 'sha256': policy.TEMPLATE_SHA256},
         'activation': {'path': str(packet / 'activation.json'), 'sha256': '0' * 64},
         'accounting_snapshot': execution['snapshot'], 'consumption': {'path': str(packet / 'consumption.json'), 'sha256': '0' * 64},
         'edit_scope': scope, 'allocation': policy.ALLOCATION, 'origin_wall_ms': origin, 'origin_monotonic_ns': runtime.continuous_ns(),
         'approval_wall_ms': execution['approval_wall_ms'], 'total_deadline_ms': origin + total,
         'run_deadline_ms': origin + min(total, phase), 'activity_clock': 'mach_continuous_time_ns',
         'launch_mode': 'trusted-native-runtime', 'direct_tool_policy': direct, 'run_directory': str(epoch)}
    activation = {k: v for k, v in a.items() if k not in ('execution_template', 'activation', 'accounting_snapshot', 'consumption',
                                                        'activity_clock', 'launch_mode', 'direct_tool_policy')}
    activation.update(template_sha256=policy.TEMPLATE_SHA256, owner_message_id=execution['owner_message_id'],
                      reservation_id=execution['reservation_id'], snapshot_sha256=execution['snapshot']['sha256'],
                      profile=policy.PROFILE, platform='darwin')
    a['activation']['sha256'] = digest(canonical(activation))
    provisional = consumption_receipt(a, activation)
    probe = deepcopy(a)
    probe['consumption']['sha256'] = digest(canonical(provisional))
    documents = {str(packet / 'template.json'): policy.TEMPLATE, str(packet / 'activation.json'): activation,
                 str(packet / 'consumption.json'): provisional}
    policy.contract(probe, lambda ref: documents[ref['path']] if ref['path'] in documents else native.Budget.fresh_bound(ref))
    root.mkdir(mode=0o700)
    packet.mkdir(mode=0o700)
    (root / 'runtime').mkdir(mode=0o700)
    (root / 'proxy').mkdir(mode=0o700)
    for p in (native_root, root / 'proxy' / policy.SLOT):
        p.mkdir(mode=0o700)
        for n in ('home', 'cwd', 'config', 'tmp'):
            (p / n).mkdir(mode=0o700)
    for p, value in ((packet / 'template.json', policy.TEMPLATE), (packet / 'activation.json', activation),
                     (packet / 'anchor-proposal.json', a), (contract_path, launch_contract), (root / 'task.json', cfg)):
        durable_private(p, value)
    with profile_path.open('xb') as stream:
        os.fchmod(stream.fileno(), 0o600)
        stream.write(proxy_text.encode()); stream.flush(); os.fsync(stream.fileno())
    tools = json.loads(artifact_read(Path(__file__).parents[1] / 'tool-profile-v2.json'))
    blueprint = {'phase': policy.PHASE, 'start': policy.START, 'profile': 'u2', 'root': str(native_root),
                 'auth_home': execution['auth_home'], 'launch_contract': str(contract_path), 'launch_identity': launch,
                 'input_template_identity': a['input_identity'], 'document_policy': {'allowed_identifiers': cfg['documents']['allowed_identifiers'],
                     'sources': cfg['documents']['source_digests'], 'outputs': cfg['documents']['outputs'], 'approval': a['approval'],
                     'owner_input_sha256': cfg['owner_input_sha256']}, 'dynamic_tools': tools,
                 'expires_unix_ms': runtime_expiry(a)}
    prepared = {'anchor': a, 'blueprint': blueprint, 'binary': str(binary), 'binary_sha256': a['candidate'],
                'launch_contract': str(contract_path), 'launch_contract_sha256': a['launch_contract_sha256'],
                'task': reference(root / 'task.json'), 'proxy_profile': reference(profile_path)}
    durable_private(root / 'prepared.json', prepared)
    return prepared


def consumption_receipt(anchor, activation):
    return {'version': 1, 'activation_sha256': anchor['activation']['sha256'], 'reservation_id': activation['reservation_id'],
            'run_directory': anchor['run_directory'], 'allocation': policy.ALLOCATION,
            'snapshot_sha256': anchor['accounting_snapshot']['sha256'], 'ledger_row_sha256': '0' * 64}


def runtime_expiry(anchor):
    return min(anchor['origin_wall_ms'] + policy.RUNTIME_WINDOW_MS,
               min(anchor['run_deadline_ms'], anchor['total_deadline_ms']) - policy.RESERVE_MS)


def consumption_time(anchor, runtime):
    """Check the same continuous/wall clock before an irreversible ledger append."""
    now = time.time_ns() // 1_000_000
    elapsed = (runtime.continuous_ns() - anchor['origin_monotonic_ns']) // 1_000_000
    require(elapsed >= 0 and abs(now - anchor['origin_wall_ms'] - elapsed) <= 2000, 'edit-consumption-clock-drift')
    require(now + policy.STARTUP_MARGIN_MS < runtime_expiry(anchor), 'edit-consumption-expired')


def consume_activation(anchor, *, ledger_path, controller_lock_path, admission):
    runtime = execution_os(require, purpose='codex-v58')
    policy.anchor_fields(anchor)
    activation = native.Budget.fresh_bound(anchor['activation'])
    snapshot = native.Budget.fresh_bound(anchor['accounting_snapshot'])
    expected = {'version': 1, 'kind': policy.KIND, 'template_sha256': policy.TEMPLATE_SHA256,
                'activation_sha256': anchor['activation']['sha256'], 'candidate': anchor['candidate'],
                'source_identity': anchor['source_identity'], 'input_identity': anchor['input_identity'],
                'platform': 'darwin', 'profile': 'u2', 'phase': policy.PHASE, 'execution_authorized': True}
    require(admission() == expected, 'edit-launch-admission')
    preliminary = consumption_receipt(anchor, activation)
    probe = deepcopy(anchor)
    probe['consumption']['sha256'] = digest(canonical(preliminary))
    policy.contract(probe, lambda ref: preliminary if ref == probe['consumption'] else native.Budget.fresh_bound(ref))
    lock = runtime.controller_lock(controller_lock_path, checked_open, require)
    try:
        ledger = EffectJournal(ledger_path)
        rid = activation['reservation_id']
        parents = [r for r in ledger.rows if r['kind'] == 'edit-parent-reservation' and r['value'].get('reservation_id') == rid]
        parent = {'reservation_id': rid, 'snapshot_sha256': anchor['accounting_snapshot']['sha256'], 'allocation': policy.ALLOCATION,
                  'owner_message_id': activation['owner_message_id'], 'parent': policy.KIND,
                  'counts_before': snapshot['counts'], 'limits': snapshot['limits']}
        require(len(parents) == 1 and parents[0] == ledger.rows[-1] and parents[0]['value'] == parent, 'edit-parent-allocation-drift')
        check_consumption(ledger.rows, anchor, activation, snapshot)
        directory = Path(anchor['run_directory'])
        require(directory.parent.resolve(strict=True) == directory.parent and not os.path.lexists(directory), 'edit-run-consumed-or-aliased')
        consumption_time(anchor, runtime)
        after = {k: v + policy.ALLOCATION.get(k, 0) for k, v in snapshot['counts'].items()}
        row = ledger.append('edit-consumed', {**preliminary, 'counts_before': snapshot['counts'], 'counts_after': after})
        # Failure below retains the consumed reservation. No refund or retry.
        receipt = {**preliminary, 'ledger_row_sha256': row['sha256']}
        final = deepcopy(anchor)
        final['consumption']['sha256'] = digest(canonical(receipt))
        durable_private(final['consumption']['path'], receipt)
        return native.Budget.create(directory, final)
    finally:
        lock.close()


def materialize_runtime(prepared, budget, transport):
    policy.contract(budget.anchor, budget.fresh_bound)
    a, b = budget.anchor, prepared['blueprint']
    require(b['phase'] == policy.PHASE and b['start'] == policy.START and b['profile'] == 'u2', 'edit-blueprint')
    require(prepared['anchor'] == {**a, 'consumption': prepared['anchor']['consumption']}, 'edit-prepared-epoch')
    cfg = native.Budget.fresh_bound(prepared['task'])
    require(digest(canonical(cfg)) == a['input_identity'] and b['input_template_identity'] == a['input_identity']
            and b['document_policy'] == {'allowed_identifiers': cfg['documents']['allowed_identifiers'],
                'sources': cfg['documents']['source_digests'], 'outputs': cfg['documents']['outputs'],
                'approval': a['approval'], 'owner_input_sha256': cfg['owner_input_sha256']}, 'edit-blueprint-task-binding')
    tools = json.loads(artifact_read(Path(__file__).parents[1] / 'tool-profile-v2.json'))
    require(b['dynamic_tools'] == tools, 'edit-blueprint-tools')
    policy.exact(transport, ('path', 'nonce', 'slot', 'max_requests'), 'edit-runtime-transport')
    require(transport['slot'] == policy.SLOT and type(transport['max_requests']) is int and 0 < transport['max_requests'] <= 13,
            'edit-runtime-transport-cap')
    spec = {**b, 'version': 2, 'launch_mode': a['launch_mode'], 'candidate': a['candidate'], 'source_identity': a['source_identity'],
            'approval': a['approval'], 'work': a['work'], 'journal': str(budget.path), 'journal_lock': str(budget.lock_path),
            'journal_anchor': str(budget.directory / 'anchor.json'), 'journal_anchor_sha256': budget.anchor_sha256,
            'execution_template_sha256': policy.TEMPLATE_SHA256, 'launch_contract_sha256': a['launch_contract_sha256'],
            'direct_tool_policy': a['direct_tool_policy'], 'transport': transport}
    require(spec['expires_unix_ms'] == runtime_expiry(a), 'edit-runtime-expiry')
    p = Path(spec['root']) / 'spec.json'
    durable_private(p, spec)
    runtime = {k: prepared[k] for k in ('binary', 'binary_sha256', 'launch_contract', 'launch_contract_sha256')}
    runtime.update(spec=str(p), spec_sha256=digest(canonical(spec)), launch_mode=a['launch_mode'])
    result = {'version': 1, 'command': policy.PHASE, 'phase': policy.PHASE, 'start': policy.START, 'run': spec['root'],
              'runtime': runtime, 'budget_directory': str(budget.directory), 'budget_anchor_sha256': budget.anchor_sha256,
              'task': prepared['task'], 'owner_input': cfg['owner_input'], 'owner_input_sha256': cfg['owner_input_sha256'],
              'documents': {'allowed_identifiers': cfg['documents']['allowed_identifiers']}}
    durable_private(Path(spec['root']) / 'host-spec.json', result)
    return result


def materialize_proxy(budget, controller, destination, expires_wall_ms):
    state = budget.read()
    require(state['events'][-1]['kind'] == 'proxy-start' and controller.budget is budget and controller.slot == policy.SLOT, 'edit-proxy-order')
    require(type(expires_wall_ms) is int and time.time_ns() // 1_000_000 < expires_wall_ms <=
            min(budget.anchor['run_deadline_ms'], budget.anchor['total_deadline_ms']) - policy.RESERVE_MS, 'edit-proxy-expiry')
    spec = {'version': 2, 'candidate': budget.anchor['candidate'], 'slot': policy.SLOT, 'journal_anchor': budget.anchor,
            'journal_anchor_sha256': budget.anchor_sha256, 'journal_snapshot': state['rows'],
            'expires_wall_ms': expires_wall_ms, 'transport': controller.transport_spec()}
    durable_private(destination, spec)
    return reference(destination)


class WithheldCallback(HostRefusal):
    """Candidate is durable; do not send a tool result or error response."""


class EditAdmission(native.Admission):
    def __init__(self, cfg, spec, budget):
        self.identity = deepcopy(cfg['identity'])
        self.identity_hash = digest(canonical(self.identity))
        self.tools = spec['dynamic_tools']
        require(type(self.tools) is list and len(self.tools) == 4 and {t['name'] for t in self.tools} ==
                {'u2_read_file', 'u2_write_file', 'u2_verify', 'u2_accept'}, 'edit-four-tool-inventory')
        self.source, self.candidate, self.template = spec['source_identity'], spec['candidate'], spec['input_template_identity']
        self.budget, self.phase, self.start = budget, policy.PHASE, policy.START
        self.session = self.step = self.plan = self.manifest_sha = self.call = self.envelope_sha = None
        self.used_calls = set()
        self.completed, self.stopped, self.sealed = True, False, False

    def callback(self, params):
        require(not self.stopped and not self.completed and self.call is None and self.turn is not None, 'edit-callback-state')
        policy.exact(params, ('threadId', 'turnId', 'callId', 'namespace', 'tool', 'arguments'), 'edit-callback-fields')
        require(params['threadId'] == self.thread and params['turnId'] == self.turn and params['namespace'] is None
                and policy.text(params['callId']) and params['callId'] not in self.used_calls, 'edit-callback-identity')
        require(digest(canonical(self.identity)) == self.identity_hash, 'edit-identity-drift')
        self.budget.reserve('host-dispatch', self.dispatch_subject(params['callId']), self.phase, self.start)
        self.call = params['callId']
        self.used_calls.add(self.call)
        return params['tool'], params['arguments']


class EditSession(native.LiveSession):
    """Uses common prepared turns 1–4; the last callback intentionally never returns."""
    def __init__(self, spec, budget, run, *, gate, fd_controller):
        self.os = execution_os(require, purpose='codex-v58')
        require(isinstance(gate, BoundedEditHost) and budget.anchor['version'] == policy.VERSION, 'edit-session-kind')
        policy.contract(budget.anchor, budget.fresh_bound)
        state = budget.read()
        self.epoch_initially_unstarted = not state['slots'] and not state['counts'].get('start', 0)
        require(self.epoch_initially_unstarted and not state['stopped'], 'edit-session-already-started')
        require(not spec.get('resume_checkpoint'), 'edit-resume-forbidden')
        super().__init__(spec, budget, run, fd_controller)
        self.gate, self.closed, self.withheld = gate, False, False
        self.known, self.cleanup, self.spawned_process, self.receipt = {}, {}, None, None
        self.spawn_attempted = False
        self.admission = EditAdmission(gate.cfg, self.runtime_spec, budget)
        self.documents = gate.controller
        require(spec['owner_input'] == gate.cfg['owner_input'] and spec['owner_input_sha256'] == gate.cfg['owner_input_sha256']
                and self.runtime_spec['input_template_identity'] == budget.anchor['input_identity'], 'edit-session-task-binding')

    def proxy_identity(self):
        p = self.fd_controller
        require(p is not None and p.proxy is not None and p.proxy.poll() is None and p.thread is not None
                and p.thread.is_alive() and p.failed is None and not p.closed, 'edit-proxy-unavailable')
        return digest(canonical({'pid': p.proxy.pid, 'nonce': p.nonce, 'reservation': p.reservation,
                                 'anchor_sha256': p.budget.anchor_sha256, 'path': str(p.socket_path)}))

    def launch(self):
        self.gate.check_core()
        state = self.budget.read()
        require(not state['stopped'] and not state['pending'] and not state['slots'], 'edit-no-resume')
        runtime = self.spec['runtime']
        require(self.runtime_spec['journal_anchor_sha256'] == self.budget.anchor_sha256
                and self.runtime_spec['phase'] == policy.PHASE and self.runtime_spec['start'] == policy.START,
                'edit-runtime-epoch-phase')
        require(self.runtime_spec['transport'] == self.fd_controller.runtime_transport(), 'edit-FD-binding')
        env = closed_environment({'TMPDIR': str(Path(self.runtime_spec['root']) / 'tmp')})
        argv, identity, self.launch_contract = native.validate_native_launch(runtime, self.runtime_spec, self.budget.anchor, self.budget.anchor_sha256, env)
        role = {'path': self.gate.cfg['documents']['profile_template'], 'sha256': self.gate.cfg['documents']['profile_template_sha256']}
        require(all(self.launch_contract['roles'][r] == role for r in ('worker', 'verifier'))
                and self.fd_controller.selected_peer == self.launch_contract['network']['peer'] == policy.PEER, 'edit-role-peer-binding')
        self.execution_binding = {k: self.budget.anchor[k] for k in ('launch_mode', 'launch_contract_sha256', 'approval', 'direct_tool_policy')}
        self.execution_binding['epoch_sha256'] = self.budget.anchor_sha256
        root = Path(self.runtime_spec['root'])
        for name in ('home', 'cwd', 'config', 'tmp'):
            p = root / name
            require(p.is_dir() and p.resolve(strict=True) == p, 'edit-runtime-directory')
        require(not list((root / 'config').iterdir()) and self.runtime_spec['expires_unix_ms'] <= time.time_ns() // 1_000_000 + 1_800_000, 'edit-runtime-config-lifetime')
        self.auth_metadata_before = native.protected_auth_metadata(self.runtime_spec['auth_home'])
        durable_private(self.run / 'protected-metadata-before.json', self.auth_metadata_before)
        self.budget.reserve('start', {'execution_binding': self.execution_binding, 'proxy_identity_sha256': self.proxy_identity(),
                                     'runtime_spec_sha256': runtime['spec_sha256']}, self.phase, self.start)
        def register(process):
            self.spawned_process = process
            self.os.observe_owned(process, self.known)
            self.fd_controller.register_runtime(runtime, process)
        self.spawn_attempted = True
        self.client = native.LiveClient(argv, Path(identity['cwd']), self.run, min(self.deadline(), time.monotonic() + 30), env, on_spawn=register)
        native.bind_native_notifications(self.client, runtime, self.runtime_spec, self.budget.anchor)
        self.client.on_event, self.client.callback = self.on_event, self.callback
        self.client.request('initialize', {'clientInfo': {'name': 'colvia_u2_qualification', 'version': '0.1'}, 'capabilities': {'experimentalApi': True}})
        self.check_auth_metadata()
        self.client.deadline = self.deadline()
        self.client.send({'method': 'initialized', 'params': {}})
        self.client.validate_account_bootstrap()
        request_id = self.client.sequence + 1
        result = self.client.request('thread/start', {'ephemeral': True, 'dynamicTools': self.runtime_spec['dynamic_tools']})
        require(result['thread']['ephemeral'] is True and result['model'] == policy.PROFILE['model'] and result['modelProvider'] == 'openai'
                and result['reasoningEffort'] == policy.PROFILE['effort'] and result['approvalPolicy'] == 'never', 'edit-thread-admission')
        self.thread = result['thread']['id']
        self.budget.reserve('thread-bound', {'request': request_id, 'thread': self.thread}, self.phase, self.start)
        self.client.drain()
        return self.thread

    def callback(self, params):
        tool, args = self.admission.callback(params)
        subject = self.admission.dispatch_subject(params['callId'])
        result = self.gate.dispatch({'session': self.thread, 'step': self.admission.turn, 'call_id': params['callId'],
                                    'tool': tool, 'arguments': args, 'identity': self.gate.cfg['identity']})
        binding = {**subject, 'host_terminal_sha256': result['terminal']['sha256'], 'host_request_sha256': result['request']['sha256'],
                   'input_identity': self.budget.anchor['input_identity']}
        if not result['ok']:
            self.budget.reserve('host-refusal', {**binding, 'reason': result['code'], 'effects': 0}, self.phase, self.start)
            raise HostRefusal('edit-durable-refusal-no-response')
        worker_result = result['worker_result']
        self.budget.reserve('worker-result', {**binding, **worker_result, 'verifier_id': args.get('verifier_id')}, self.phase, self.start)
        if tool == 'u2_verify' and result['result'].get('pass') is False:
            raise HostRefusal('edit-verifier-failed-no-response')
        if self.gate.completed == 5:
            result_identity = self.gate.seal()
            oracle = self.documents.oracle_sha256
            self.budget.reserve('seal', {'result_identity': result_identity, 'oracle_sha256': oracle}, self.phase, self.start)
            self.receipt = {'version': policy.VERSION, 'kind': policy.KIND, 'anchor_sha256': self.budget.anchor_sha256,
                            'input_identity': self.budget.anchor['input_identity'], 'result_identity': result_identity, 'oracle_sha256': oracle,
                            'journal_sha256': self.budget.read()['prev'], **subject, 'host_terminal_sha256': result['terminal']['sha256'],
                            'output': self.budget.anchor['edit_scope']['output'], 'callback_response': 'withheld',
                            'path': str(self.run / 'candidate-receipt.json')}
            durable_private(self.receipt['path'], self.receipt)
            self.budget.reserve('candidate-receipt', {'receipt': self.receipt, 'sha256': digest(canonical(self.receipt))}, self.phase, self.start)
            self.withheld = True
            raise WithheldCallback('edit-sealed-callback-withheld')
        text = wire_bytes(result['result']).decode()
        require(len(text.encode()) <= 64_000, 'edit-callback-size')
        return {'contentItems': [{'type': 'inputText', 'text': text}], 'success': True}

    def turn(self, inputs):
        require(not self.closed and not self.withheld, 'edit-turn-closed')
        self.proxy_identity()
        try:
            return super().turn(inputs)
        except WithheldCallback:
            self.close()
            require(self.cleanup['complete'] and self.cleanup['terminal'] == 'sealed-terminated', 'edit-terminal-unavailable')
            return {'status': 'sealed-terminated', 'receipt_sha256': digest(canonical(self.receipt))}
        except BaseException as cause:
            self.close(primary_error=cause)
            raise

    def iterate(self):
        for ordinal, (tool, verifier) in enumerate(policy.STEPS):
            progress = self.documents.progress()
            instruction = {'step': ordinal + 1, 'tool': tool, 'verifier_id': verifier, 'read_ids': self.gate.cfg['read_ids'],
                           'output': self.gate.cfg['documents']['outputs'][0], 'progress': progress,
                           'authority': 'No accept, correction or recovery. Exactly one specified tool call per turn.'}
            inputs = [{'type': 'text', 'text': self.owner_text, 'text_elements': []},
                      {'type': 'text', 'text': wire_bytes(instruction).decode(), 'text_elements': []}]
            result = self.turn(inputs)
            if ordinal == 4:
                require(self.withheld and self.closed and result['status'] == 'sealed-terminated', 'edit-terminal-missing')
                return result
            require(self.gate.completed == ordinal + 1, 'edit-turn-did-not-complete-step')
        raise HostRefusal('edit-no-terminal')

    def close(self, *, primary_error=None):
        if self.closed:
            return self.cleanup
        self.closed = True
        failures, absent = [], False
        terminal = None
        try:
            if self.documents.active is not None:
                stopped = end_process(self.documents.active)
                require(stopped.get('process_group_absent') is True, 'edit-worker-cleanup-unconfirmed')
                self.documents.active = None
            self.gate.stop()
        except BaseException as error:
            failures.append(error)
        try:
            self.admission.stop()
        except BaseException as error:
            failures.append(error)
        process = self.client.process if self.client is not None else self.spawned_process
        try:
            self.fd_controller.revoke(self.start)
        except BaseException as error:
            failures.append(error)
        if process is not None:
            try:
                absent = self.os.stop_owned(process, self.known, lambda: self.os.observe_owned(process, self.known))
            except BaseException as error:
                failures.append(error)
            finally:
                try:
                    if self.client is not None:
                        self.client.selector.close()
                    for name in ('stdin', 'stdout', 'stderr'):
                        getattr(process, name).close()
                except BaseException as error:
                    failures.append(error)
        else:
            # A failure before the spawn call is known absence. An attempted
            # spawn without an owned handle remains unknown, never inferred safe.
            absent = not self.spawn_attempted and self.epoch_initially_unstarted
        try:
            self.fd_controller.close()
        except BaseException as error:
            failures.append(error)
        try:
            require(absent and proxy_absent(self.fd_controller)
                    and self.documents.active is None, 'edit-process-or-lease-unknown')
            if hasattr(self, 'auth_metadata_before'):
                self.check_auth_metadata()
            success = self.withheld and primary_error is None and not failures
            if success:
                self.budget.reserve('process-ended', {'start': self.start, 'process_group_absent': True,
                    'observed_descendants_absent': True, 'worker_absent': True, 'leases_absent': True,
                    'outcome': 'sealed-terminated', 'receipt_sha256': digest(canonical(self.receipt)), 'callback_response': 'withheld'},
                    self.phase, self.start, allow_closeout=True)
            self.budget.reserve('execution-stop', {'reason': 'sealed-terminated' if success else 'failed',
                'native_absent': True, 'proxy_absent': True, 'controller_absent': True}, allow_closeout=True)
            terminal = self.budget.read()['terminal']
            require(not success or terminal == 'sealed-terminated', 'edit-terminal-unavailable')
        except BaseException as error:
            failures.append(error)
        try:
            self.gate.close()
        except BaseException as error:
            failures.append(error)
        self.cleanup = {'complete': not failures, 'terminal': terminal if not failures else None,
                        'process_group_absent': absent, 'observed_descendants_absent': absent,
                        'callback_response': 'withheld' if self.withheld else 'unconfirmed',
                        'primary_error': failure_metadata(primary_error),
                        'rpc_failure': rpc_failure_metadata(self.client),
                        'cleanup_errors': [failure_metadata(e) for e in failures]}
        try:
            durable_private(self.run / 'edit-close.json', self.cleanup)
        except BaseException as error:
            failures.append(error)
            self.cleanup.update(complete=False, terminal=None)
        if failures and primary_error is None:
            raise failures[0]
        return self.cleanup


def rpc_failure_metadata(client):
    """Persist only bounded transport metadata; never an RPC body or message."""
    value = getattr(client, 'rpc_failure', None)
    if not isinstance(value, dict):
        return None
    method, stage = value.get('method'), value.get('stage')
    code, message_hash = value.get('error_code'), value.get('error_message_sha256')
    return {'method': method if isinstance(method, str) and method in native.LIVE_METHODS else None,
            'stage': stage if isinstance(stage, str) and stage in native.LIVE_METHODS else None,
            'id_matches': value.get('id_matches') if type(value.get('id_matches')) is bool else None,
            'has_error': value.get('has_error') if type(value.get('has_error')) is bool else None,
            'error_code': code if type(code) is int and -(2 ** 31) <= code < 2 ** 31 else None,
            'error_message_sha256': message_hash if isinstance(message_hash, str) and len(message_hash) == 64
                and all(c in '0123456789abcdef' for c in message_hash) else None}


def failure_metadata(error):
    if error is None:
        return None
    return {'type': type(error).__name__, 'code': str(error)[:256] if isinstance(error, HostRefusal) else None}


def proxy_absent(controller):
    return (controller.closed and (controller.proxy is None or controller.proxy.poll() is not None)
            and (controller.thread is None or not controller.thread.is_alive())
            and not controller.leases and not controller.lease_bindings)


def close_unstarted(budget, controller, gate, run, cause):
    """Close a never-started epoch; an earlier native start remains unknown."""
    errors = []
    if gate is not None:
        try:
            gate.stop()
        except BaseException as error:
            errors.append(error)
    try:
        controller.close()
        require(proxy_absent(controller), 'edit-proxy-close-unconfirmed')
        require(gate is None or gate.controller is None or gate.controller.active is None, 'edit-worker-close-unconfirmed')
        state = budget.read() if budget is not None else None
        require(state is None or (not state['slots'] and not state['counts'].get('start', 0)),
                'edit-prior-start-absence-unknown')
        if state is not None and not state['stopped']:
            budget.reserve('execution-stop', {'reason': 'failed', 'native_absent': True,
                'proxy_absent': True, 'controller_absent': True}, allow_closeout=True)
    except BaseException as error:
        errors.append(error)
    if gate is not None:
        try:
            gate.close()
        except BaseException as error:
            errors.append(error)
    metadata = {'complete': not errors and budget is not None, 'terminal': None,
                'native_spawn_attempted': False, 'primary_error': failure_metadata(cause),
                'cleanup_errors': [failure_metadata(e) for e in errors]}
    try:
        durable_private(run / 'edit-close.json', metadata)
    except BaseException:
        pass  # Preserve the original exception; never report success here.


def run_edit(spec, *, fd_controller, snapshot_reader, baseline_reader):
    require(spec['command'] == policy.PHASE and spec['phase'] == policy.PHASE and spec['start'] == policy.START
            and not spec.get('resume_checkpoint'), 'edit-entry-contract')
    require(fd_controller is not None and callable(snapshot_reader) and callable(baseline_reader), 'edit-trusted-controller-required')
    run = Path(spec['run'])
    # Refusing an earlier start must not run a cleanup writer that could claim
    # absence for a process owned by an earlier entry.
    budget = native.Budget(spec['budget_directory'], spec['budget_anchor_sha256'])
    state = budget.read()
    require(not state['stopped'], 'edit-execution-stopped')
    require(not state['slots'] and not state['counts'].get('start', 0), 'edit-entry-already-started')
    gate = session = None
    try:
        cfg = native.Budget.fresh_bound(spec['task'])
        gate = BoundedEditHost(cfg, budget, run / 'host', snapshot_reader, baseline_reader,
                              time.monotonic() + (budget.read()['remaining_ms'] - policy.RESERVE_MS) / 1000)
        session = EditSession(spec, budget, run, gate=gate, fd_controller=fd_controller)
        session.launch()
        result = session.iterate()
        require(session.cleanup.get('complete') is True and budget.read()['terminal'] == 'sealed-terminated',
                'edit-result-not-submittable')
        return result
    except BaseException as cause:
        if session is not None:
            session.close(primary_error=cause)
        else:
            close_unstarted(budget, fd_controller, gate, run, cause)
        raise
    finally:
        if session is not None and not session.closed:
            session.close()
