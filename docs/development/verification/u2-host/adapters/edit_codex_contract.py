"""Single-document edit policy. Pure validation and reduction; no launch or effects."""
from ..contracts import require, canonical, digest, wire_bytes
from .fresh_codex_contract import exact, text, sha, number

VERSION = 59
KIND = 'single-document-edit-v1'
PHASE = 'edit-only'
START = 'edit-01'
SLOT = 's4'
PEER = '104.18.32.47'
RESERVE_MS = 120_000
STARTUP_MARGIN_MS = 30_000
RUNTIME_WINDOW_MS = 1_780_000
ALLOCATION = {'starts': 1, 'turns': 5, 'sends': 10, 'dispatch': 5, 'controls': 3,
              'worker_reads': 1, 'worker_writes': 1, 'worker_verifies': 3, 'seals': 1,
              'proxy_starts': 1, 'authority_apply': 0, 'recovery_apply': 0, 'content_correction': 0}
LIMITS = {'genesis': 1, 'proxy-start': 1, 'start': 1, 'runtime-entered': 1,
          'control': 3, 'policy-admission': 1, 'thread': 1, 'thread-bound': 1,
          'input': 5, 'turn': 5, 'generation': 10, 'dispatch': 5, 'host-dispatch': 5,
          'worker-result': 5, 'host-refusal': 1, 'seal': 1, 'candidate-receipt': 1,
          'process-ended': 1, 'execution-stop': 1}
STEPS = (('u2_read_file', None), ('u2_write_file', None), ('u2_verify', 'DOC-LINKS'),
         ('u2_verify', 'DOC-GFM'), ('u2_verify', 'DOC-CLAIMS'))
PROFILE = {'native_profile': 'u2', 'model': 'gpt-6-astra', 'effort': 'xhigh',
           'phase': PHASE, 'slot': SLOT, 'native_resume': False}
TEMPLATE = {'version': VERSION, 'kind': KIND, 'profile': PROFILE, 'start': START,
            'allocation': ALLOCATION, 'limits': LIMITS, 'steps': [list(s) for s in STEPS],
            'closeout_reserve_ms': RESERVE_MS, 'final_callback': 'withhold-and-terminate',
            'read_ids_min': 1, 'read_ids_max': 8, 'outputs': 1, 'replace_ranges': 1}
TEMPLATE_SHA256 = digest(canonical(TEMPLATE))
ANCHOR_FIELDS = {'version', 'kind', 'run_id', 'approval', 'work', 'candidate', 'source_identity',
                 'input_identity', 'launch_contract_sha256', 'execution_template', 'activation',
                 'accounting_snapshot', 'consumption', 'edit_scope', 'allocation', 'origin_wall_ms',
                 'origin_monotonic_ns', 'approval_wall_ms', 'total_deadline_ms', 'run_deadline_ms',
                 'activity_clock', 'launch_mode', 'direct_tool_policy', 'run_directory'}
SCOPE_FIELDS = {'home', 'work', 'intent_sha256', 'core_snapshot_sha256', 'worker_root',
                'worker_base_commit', 'worker_snapshot_sha256', 'identity_sha256', 'documents_sha256',
                'read_ids', 'files', 'output', 'verifier'}


def path(value):
    return text(value) and value.startswith('/') and all(p not in ('', '.', '..') for p in value[1:].split('/'))


def scope_fields(s):
    exact(s, SCOPE_FIELDS, 'edit-scope-fields')
    require(text(s['home']) and text(s['work']) and path(s['worker_root']), 'edit-scope-identity')
    require(type(s['worker_base_commit']) is str and len(s['worker_base_commit']) in (40, 64)
            and all(c in '0123456789abcdef' for c in s['worker_base_commit']), 'edit-worker-base')
    for k in ('intent_sha256', 'core_snapshot_sha256', 'worker_snapshot_sha256', 'identity_sha256', 'documents_sha256'):
        require(sha(s[k]), 'edit-scope-digest')
    ids, files = s['read_ids'], s['files']
    require(type(ids) is list and 1 <= len(ids) <= 8 and all(text(k) for k in ids)
            and len(set(ids)) == len(ids) and type(files) is dict and set(files) == set(ids)
            and all(sha(v) for v in files.values()), 'edit-read-ids')
    o = s['output']
    exact(o, ('id', 'path', 'sha256', 'range', 'prefix_sha256', 'suffix_sha256'), 'edit-output-fields')
    require(o['id'] in files and o['sha256'] == files[o['id']] and path(o['path'])
            and o['path'].startswith(s['worker_root'] + '/'), 'edit-output-binding')
    r = o['range']
    require(type(r) is list and len(r) == 2 and all(number(n) for n in r) and r[0] <= r[1], 'edit-output-range')
    require(sha(o['prefix_sha256']) and sha(o['suffix_sha256']), 'edit-outside-range')
    exact(s['verifier'], ('python_sha256', 'worker_sha256', 'parser_sha256', 'profile_template_sha256'), 'edit-verifier-fields')
    require(all(sha(v) for v in s['verifier'].values()), 'edit-verifier-digest')


def anchor_fields(a):
    exact(a, ANCHOR_FIELDS, 'edit-anchor-fields')
    require(type(a['version']) is int and a['version'] == VERSION and a['kind'] == KIND, 'edit-kind-version')
    require(a['activity_clock'] == 'mach_continuous_time_ns' and a['launch_mode'] == 'trusted-native-runtime', 'edit-mode')
    require(a['allocation'] == ALLOCATION and all(type(v) is int for v in a['allocation'].values()), 'edit-allocation')
    rid = a['run_id']
    require(text(rid) and len(rid) == 36 and [i for i, c in enumerate(rid) if c == '-'] == [8, 13, 18, 23]
            and all(c in '0123456789abcdef-' for c in rid), 'edit-run-id')
    require(a['work'] == 'u2-edit-' + rid and text(a['approval']) and a['approval'].startswith('owner-edit-')
            and path(a['run_directory']), 'edit-run-binding')
    for k in ('candidate', 'source_identity', 'input_identity', 'launch_contract_sha256'):
        require(sha(a[k]), 'edit-digest')
    for k in ('execution_template', 'activation', 'accounting_snapshot', 'consumption'):
        exact(a[k], ('path', 'sha256'), 'edit-reference')
        require(path(a[k]['path']) and sha(a[k]['sha256']), 'edit-reference')
    require(a['execution_template']['sha256'] == TEMPLATE_SHA256, 'edit-template')
    for k in ('origin_wall_ms', 'origin_monotonic_ns', 'approval_wall_ms', 'total_deadline_ms', 'run_deadline_ms'):
        require(number(a[k]) and a[k] > 0, 'edit-clock-type')
    require(a['approval_wall_ms'] <= a['origin_wall_ms'] < a['run_deadline_ms'] <= a['total_deadline_ms'], 'edit-deadline')
    require(a['direct_tool_policy'] == {'version': 1, 'mode': 'direct', 'model': PROFILE['model'],
            'profiles': ['clock', 'u2'], 'approval': a['approval']}, 'edit-direct-policy')
    scope_fields(a['edit_scope'])


def contract(a, bound):
    anchor_fields(a)
    require(bound(a['execution_template']) == TEMPLATE, 'edit-template-bytes')
    x, s, c = (bound(a[k]) for k in ('activation', 'accounting_snapshot', 'consumption'))
    fields = (ANCHOR_FIELDS - {'execution_template', 'activation', 'accounting_snapshot', 'consumption',
                              'activity_clock', 'launch_mode', 'direct_tool_policy'}) | {
        'template_sha256', 'owner_message_id', 'reservation_id', 'snapshot_sha256', 'profile', 'platform'}
    exact(x, fields, 'edit-activation-fields')
    require(x['template_sha256'] == TEMPLATE_SHA256 and x['snapshot_sha256'] == a['accounting_snapshot']['sha256']
            and text(x['owner_message_id']) and a['approval'] == 'owner-edit-' + x['owner_message_id']
            and text(x['reservation_id']) and x['profile'] == PROFILE and x['platform'] == 'darwin', 'edit-activation-binding')
    require(all(x[k] == a[k] for k in fields & set(a)), 'edit-activation-drift')
    exact(s, ('version', 'record', 'captured_wall_ms', 'total_cap_ms', 'charged_ms', 'phase_cap_ms',
              'phase_charged_ms', 'counts', 'limits', 'consumed_reservations'), 'edit-snapshot-fields')
    exact(s['record'], ('path', 'sha256'), 'edit-accounting-record')
    bound(s['record'])
    require(type(s['version']) is int and s['version'] == 1, 'edit-snapshot-version')
    for k in ('captured_wall_ms', 'total_cap_ms', 'charged_ms', 'phase_cap_ms', 'phase_charged_ms'):
        require(number(s[k]), 'edit-accounting-number')
    elapsed = a['origin_wall_ms'] - s['captured_wall_ms']
    total = s['total_cap_ms'] - s['charged_ms'] - elapsed
    phase = s['phase_cap_ms'] - s['phase_charged_ms'] - elapsed
    require(elapsed >= 0 and min(total, phase) > RESERVE_MS + 20_000
            and a['total_deadline_ms'] == a['origin_wall_ms'] + total
            and a['run_deadline_ms'] == a['origin_wall_ms'] + min(total, phase), 'edit-no-time-refund')
    require(type(s['counts']) is dict and type(s['limits']) is dict and set(s['counts']) == set(s['limits'])
            and set(ALLOCATION) <= set(s['counts']), 'edit-counter-keys')
    for k, used in s['counts'].items():
        require(number(used) and number(s['limits'][k]) and used + ALLOCATION.get(k, 0) <= s['limits'][k], 'edit-counter-cap')
    used = s['consumed_reservations']
    require(type(used) is list and all(text(r) for r in used) and len(set(used)) == len(used)
            and x['reservation_id'] not in used, 'edit-consumed-reservation')
    exact(c, ('version', 'activation_sha256', 'reservation_id', 'run_directory', 'allocation', 'snapshot_sha256', 'ledger_row_sha256'), 'edit-consumption-fields')
    require(type(c['version']) is int and c == {'version': 1, 'activation_sha256': a['activation']['sha256'],
        'reservation_id': x['reservation_id'], 'run_directory': a['run_directory'], 'allocation': ALLOCATION,
        'snapshot_sha256': a['accounting_snapshot']['sha256'], 'ledger_row_sha256': c['ledger_row_sha256']}
        and sha(c['ledger_row_sha256']), 'edit-consumption-binding')
    return x


def budget_state(budget, rows, now, *, validate_contract=True):
    a = budget.anchor
    if validate_contract:
        contract(a, budget.fresh_bound)
    else:
        anchor_fields(a)
    require(number(now) and type(rows) is list and 0 < len(rows) < 200, 'edit-journal-bound')
    prev, last, stopped, terminal = '', a['origin_wall_ms'], False, None
    counts, plans, events = {}, {}, []
    slot, current, receipt, sealed = None, None, None, None
    for i, row in enumerate(rows):
        exact(row, ('event', 'sha256'), 'edit-row')
        e = row['event']
        exact(e, ('seq', 'prev', 'approval', 'work', 'candidate', 'phase', 'start', 'kind', 'subject', 'at_ms'), 'edit-event')
        require(type(e['seq']) is int and e['seq'] == i and e['prev'] == prev
                and row['sha256'] == digest(wire_bytes(e)) and all(e[k] == a[k] for k in ('approval', 'work', 'candidate')), 'edit-chain')
        kind, sub, at = e['kind'], e['subject'], e['at_ms']
        require(kind in LIMITS and type(sub) is dict and number(at) and last <= at <= now and not stopped, 'edit-event-order')
        if kind not in ('genesis', 'process-ended', 'execution-stop'):
            require(at + RESERVE_MS < min(a['run_deadline_ms'], a['total_deadline_ms']), 'edit-execution-deadline')
        counts[kind] = counts.get(kind, 0) + 1
        require(counts[kind] <= LIMITS[kind], 'edit-cap')
        require((i == 0 and kind == 'genesis' and sub == {'anchor_sha256': budget.anchor_sha256}) or
                (i > 0 and kind != 'genesis'), 'edit-genesis')
        require((e['phase'], e['start']) == (('controller', 'controller') if kind in ('genesis', 'proxy-start', 'execution-stop')
                else (PHASE, START)), 'edit-phase-start')
        if kind == 'proxy-start':
            require(slot is None and sub == {'slot': SLOT, 'start_id': 'edit-' + a['run_id']}, 'edit-proxy')
        if kind == 'start':
            require(counts.get('proxy-start') == 1 and slot is None, 'edit-start-order')
            exact(sub, ('execution_binding', 'proxy_identity_sha256', 'runtime_spec_sha256'), 'edit-start-fields')
            require(sub['execution_binding'] == {'launch_mode': a['launch_mode'], 'launch_contract_sha256': a['launch_contract_sha256'],
                'epoch_sha256': budget.anchor_sha256, 'approval': a['approval'], 'direct_tool_policy': a['direct_tool_policy']}
                and sha(sub['proxy_identity_sha256']) and sha(sub['runtime_spec_sha256']), 'edit-start-binding')
            slot = {'entered': False, 'ended': False, 'controls': set(), 'policy': None, 'request': None,
                    'thread': None, 'plans': [], 'at': at, 'proxy': sub['proxy_identity_sha256']}
        if kind not in ('genesis', 'proxy-start', 'execution-stop'):
            require(slot is not None and not slot['ended'], 'edit-inactive-slot')
            if kind not in ('start', 'runtime-entered', 'process-ended'):
                require(slot['entered'] and at - slot['at'] <= 1_780_000, 'edit-runtime-deadline')
        if kind == 'runtime-entered':
            require(not slot['entered'] and sub == {'start': START}, 'edit-runtime-entry')
            slot['entered'] = True
        if kind == 'control':
            exact(sub, ('endpoint',), 'edit-control-fields')
            ep = sub['endpoint']
            require(ep in ('policy', 'models', 'accounts') and ep not in slot['controls'] and slot['request'] is None
                    and ((ep == 'policy' and slot['policy'] is None and not slot['controls'])
                         or (ep != 'policy' and slot['policy'] is not None)), 'edit-control-order')
            slot['controls'].add(ep)
        if kind == 'policy-admission':
            exact(sub, ('classification',), 'edit-policy-fields')
            c = sub['classification']
            require(c in ('applied', 'applicable-empty', 'known-not-applicable') and slot['policy'] is None
                    and slot['request'] is None and slot['controls'] == (set() if c == 'known-not-applicable' else {'policy'}), 'edit-policy-order')
            slot['policy'] = c
        if kind == 'thread':
            exact(sub, ('request',), 'edit-thread-fields')
            controls = {'models', 'accounts'} if slot['policy'] == 'known-not-applicable' else {'policy', 'models', 'accounts'}
            require(sub['request'] is not None and slot['request'] is None and slot['policy'] is not None
                    and slot['controls'] == controls, 'edit-thread-order')
            slot['request'] = sub['request']
        if kind == 'thread-bound':
            exact(sub, ('request', 'thread'), 'edit-thread-bound-fields')
            require(slot['request'] is not None and sub['request'] == slot['request'] and slot['thread'] is None
                    and text(sub['thread']), 'edit-thread-binding')
            slot['thread'] = sub['thread']
        if kind == 'input':
            exact(sub, ('plan', 'input_sha256', 'manifest_sha256'), 'edit-input-fields')
            require(slot['thread'] is not None and len(plans) < 5 and text(sub['plan']) and sub['plan'] not in plans
                    and (current is None or (plans[current]['generation'] == 2 and plans[current]['outcome'] == 'completed'))
                    and sha(sub['input_sha256']) and sha(sub['manifest_sha256']) and sealed is None, 'edit-input-order')
            current = sub['plan']
            plans[current] = {'ordinal': len(plans), 'thread': slot['thread'], 'began': False, 'turn': None,
                              'generation': 0, 'call': None, 'host': False, 'outcome': None, 'at': at}
            slot['plans'].append(current)
        if kind == 'turn':
            require(current is not None and not plans[current]['began'] and
                    sub == {'thread': slot['thread'], 'plan': current}, 'edit-turn-binding')
            plans[current]['began'] = True
        if kind in ('generation', 'dispatch', 'host-dispatch', 'worker-result', 'host-refusal'):
            require(current is not None, 'edit-effect-before-input')
            p = plans[current]
            require(p['began'] and sub.get('plan') == current and sub.get('thread') == p['thread'] and text(sub.get('turn'))
                    and p['turn'] in (None, sub['turn']) and at - p['at'] <= 880_000 and sealed is None, 'edit-effect-binding')
            if kind == 'generation':
                exact(sub, ('thread', 'turn', 'plan', 'generation'), 'edit-generation-fields')
                require(type(sub['generation']) is int and sub['generation'] == p['generation'] + 1 <= 2
                        and (p['generation'] == 0 or (p['outcome'] == 'completed' and p['ordinal'] < 4))
                        and all(other is p or other['turn'] != sub['turn'] for other in plans.values()), 'edit-generation-order')
                p['generation'], p['turn'] = sub['generation'], sub['turn']
            else:
                require(p['generation'] == 1 and text(sub.get('call')) and p['call'] in (None, sub['call']), 'edit-call-binding')
                if kind == 'dispatch':
                    exact(sub, ('thread', 'turn', 'plan', 'call'), 'edit-dispatch-fields')
                    require(p['call'] is None and all(o['call'] != sub['call'] for o in plans.values()), 'edit-call-reuse')
                    p['call'] = sub['call']
                elif kind == 'host-dispatch':
                    exact(sub, ('thread', 'turn', 'plan', 'call'), 'edit-host-fields')
                    require(p['call'] is not None and not p['host'], 'edit-host-order')
                    p['host'] = True
                else:
                    require(p['call'] is not None and p['host'] and p['outcome'] is None, 'edit-result-order')
                    base = ('thread', 'turn', 'plan', 'call', 'host_terminal_sha256', 'host_request_sha256', 'input_identity')
                    require(sub.get('input_identity') == a['input_identity'] and sha(sub.get('host_terminal_sha256'))
                            and sha(sub.get('host_request_sha256')), 'edit-host-correspondence')
                    if kind == 'worker-result':
                        exact(sub, base + ('tool', 'verifier_id', 'result_sha256', 'result_identity', 'oracle_sha256'), 'edit-result-fields')
                        require((sub['tool'], sub['verifier_id']) == STEPS[p['ordinal']]
                                and all(sha(sub[k]) for k in ('result_sha256', 'result_identity', 'oracle_sha256')), 'edit-result-step')
                        p['outcome'], p['result'] = 'completed', sub
                    else:
                        exact(sub, base + ('reason', 'effects'), 'edit-refusal-fields')
                        require(text(sub['reason']) and type(sub['effects']) is int and sub['effects'] == 0, 'edit-refusal')
                        p['outcome'] = 'refused'
        if kind == 'seal':
            exact(sub, ('result_identity', 'oracle_sha256'), 'edit-seal-fields')
            require(len(plans) == 5 and all(p['outcome'] == 'completed' for p in plans.values()) and sealed is None
                    and all(plans[current]['result'][k] == sub[k] for k in sub), 'edit-seal-order')
            require(all(p['result']['result_identity'] == sub['result_identity'] for p in list(plans.values())[1:]), 'edit-verifier-currentness')
            sealed = sub
        if kind == 'candidate-receipt':
            exact(sub, ('receipt', 'sha256'), 'edit-receipt-fields')
            r = sub['receipt']
            exact(r, ('version', 'kind', 'anchor_sha256', 'input_identity', 'result_identity', 'oracle_sha256',
                      'journal_sha256', 'thread', 'turn', 'plan', 'call', 'host_terminal_sha256',
                      'output', 'callback_response', 'path'), 'edit-receipt-shape')
            require(sealed is not None and receipt is None and sub['sha256'] == digest(canonical(r))
                    and r['version'] == VERSION and r['kind'] == KIND and r['anchor_sha256'] == budget.anchor_sha256
                    and r['input_identity'] == a['input_identity'] and r['journal_sha256'] == prev
                    and all(r[k] == sealed[k] for k in sealed) and r['callback_response'] == 'withheld'
                    and path(r['path']) and r['output'] == a['edit_scope']['output'], 'edit-receipt-binding')
            require(all(r[k] == plans[current]['result'][k] for k in ('thread', 'turn', 'plan', 'call', 'host_terminal_sha256')), 'edit-receipt-call')
            if validate_contract:
                require(budget.fresh_bound({'path': r['path'], 'sha256': sub['sha256']}) == r, 'edit-receipt-file')
            receipt = sub
        if kind == 'process-ended':
            exact(sub, ('start', 'process_group_absent', 'observed_descendants_absent', 'worker_absent', 'leases_absent',
                        'outcome', 'receipt_sha256', 'callback_response'), 'edit-process-ended-fields')
            require(receipt is not None and sub == {'start': START, 'process_group_absent': True, 'observed_descendants_absent': True,
                'worker_absent': True, 'leases_absent': True, 'outcome': 'sealed-terminated', 'receipt_sha256': receipt['sha256'],
                'callback_response': 'withheld'} and counts.get('dispatch') == counts.get('worker-result') == 5
                and plans[current]['generation'] == 1, 'edit-close-pending')
            slot['ended'] = True
        if kind == 'execution-stop':
            exact(sub, ('reason', 'native_absent', 'proxy_absent', 'controller_absent'), 'edit-stop-fields')
            require(sub['reason'] in ('sealed-terminated', 'failed')
                    and all(sub[k] is True for k in ('native_absent', 'proxy_absent', 'controller_absent')), 'edit-stop-absence')
            if sub['reason'] == 'sealed-terminated':
                require(slot is not None and slot['ended'] and sealed is not None and receipt is not None, 'edit-stop-terminal')
                terminal = 'sealed-terminated'
            stopped = True
        events.append(e)
        prev, last = row['sha256'], at
    pending = [key for key, p in plans.items() if p['began'] and p['generation'] != 2 and
               not (slot['ended'] and key == current and receipt is not None)]
    return {'events': events, 'history_events': events, 'rows': rows, 'prev': prev, 'counts': counts,
            'excluded_ms': 0, 'paused_at': None, 'stopped': stopped, 'active_ms': now,
            'remaining_ms': min(a['total_deadline_ms'], a['run_deadline_ms']) - now, 'pending': pending,
            'slots': {START: slot} if slot else {}, 'receipt': receipt, 'terminal': terminal}
