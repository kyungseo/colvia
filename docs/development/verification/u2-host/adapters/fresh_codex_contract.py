"""Exact v58 policy and reducer. No OS detection, process launch or file writes here."""
from ..contracts import require, canonical, digest, wire_bytes

TEMPLATE_SHA256 = '2b3bf8ee01db992d066fbb4fd9ea43a8a6663e997bcecba4b5d20796d705ab5c'
KIND = 'tool-neutral-codex-readonly-v1'
STARTS = ('synthetic-01', 'synthetic-02')
ALLOCATION = {'starts': 2, 'turns': 4, 'sends': 6, 'dispatch': 4, 'controls': 6,
              'worker_reads': 2, 'proxy_starts': 1, 'authority_apply': 0,
              'recovery_apply': 0, 'content_correction': 0}
LIMITS = {'genesis': 1, 'proxy-start': 1, 'start': 2, 'runtime-entered': 2,
          'control': 6, 'policy-admission': 2, 'thread': 2, 'thread-bound': 2, 'input': 4, 'turn': 4,
          'generation': 6, 'dispatch': 4, 'host-dispatch': 4, 'worker-result': 2,
          'host-refusal': 2, 'process-ended': 2, 'execution-stop': 1}
ANCHOR_FIELDS = {'version', 'kind', 'run_id', 'approval', 'work', 'candidate', 'source_identity',
                 'input_identity', 'launch_contract_sha256', 'execution_template', 'activation',
                 'accounting_snapshot', 'consumption', 'read_scope', 'allocation', 'origin_wall_ms',
                 'origin_monotonic_ns', 'approval_wall_ms', 'total_deadline_ms', 'run_deadline_ms',
                 'activity_clock', 'launch_mode', 'direct_tool_policy', 'run_directory'}


def exact(value, fields, code):
    require(type(value) is dict and set(value) == set(fields), code)


def text(value):
    return type(value) is str and bool(value) and len(value) <= 4096


def sha(value):
    return type(value) is str and len(value) == 64 and all(c in '0123456789abcdef' for c in value)


def number(value):
    return type(value) is int and 0 <= value <= 2**63 - 1


def anchor_fields(a):
    exact(a, ANCHOR_FIELDS, 'v58-anchor-fields')
    require(type(a['version']) is int and a['version'] == 58 and a['kind'] == KIND, 'v58-version')
    require(a['activity_clock'] == 'mach_continuous_time_ns' and a['launch_mode'] == 'trusted-native-runtime', 'v58-mode')
    require(a['allocation'] == ALLOCATION and all(type(v) is int for v in a['allocation'].values()), 'v58-allocation')
    for key in ('approval', 'work', 'run_id', 'run_directory'):
        require(text(a[key]), 'v58-identity')
    run_id = a['run_id']
    require(len(run_id) == 36 and [i for i,c in enumerate(run_id) if c == '-'] == [8,13,18,23]
            and all(c in '0123456789abcdef-' for c in run_id), 'v58-run-id')
    require(a['work'] == 'u2-v58-' + run_id and a['approval'].startswith('owner-v58-'), 'v58-new-work')
    require(a['run_directory'].startswith('/') and all(p not in ('', '.', '..') for p in a['run_directory'][1:].split('/')), 'v58-run-path')
    for key in ('candidate', 'source_identity', 'input_identity', 'launch_contract_sha256'):
        require(sha(a[key]), 'v58-digest')
    for key in ('execution_template', 'activation', 'accounting_snapshot', 'consumption'):
        exact(a[key], ('path', 'sha256'), 'v58-reference')
        require(text(a[key]['path']) and a[key]['path'].startswith('/') and sha(a[key]['sha256']), 'v58-reference')
    require(a['execution_template']['sha256'] == TEMPLATE_SHA256, 'v58-template')
    for key in ('origin_wall_ms','origin_monotonic_ns','approval_wall_ms','total_deadline_ms','run_deadline_ms'):
        require(number(a[key]) and a[key] > 0, 'v58-clock-type')
    require(a['approval_wall_ms'] <= a['origin_wall_ms'] < a['run_deadline_ms'] <= a['total_deadline_ms'], 'v58-deadline')
    require(a['direct_tool_policy'] == {'version':1,'mode':'direct','model':'gpt-6-astra','profiles':['clock','u2'],'approval':a['approval']}, 'v58-direct-policy')
    exact(a['read_scope'], ('core_snapshot_sha256', 'identity_sha256', 'files'), 'v58-read-scope')
    require(sha(a['read_scope']['core_snapshot_sha256']) and sha(a['read_scope']['identity_sha256']), 'v58-read-scope')
    files = a['read_scope']['files']
    require(type(files) is dict and 0 < len(files) <= 16 and all(text(k) and sha(v) for k,v in files.items()), 'v58-read-files')


def contract(a, bound):
    """bound verifies private file identity, exact digest and canonical JSON."""
    anchor_fields(a)
    template = bound(a['execution_template'])
    require(digest(canonical(template)) == TEMPLATE_SHA256, 'v58-template-bytes')
    activation, snapshot, consumed = (bound(a[key]) for key in ('activation','accounting_snapshot','consumption'))
    af = {'version','kind','template_sha256','owner_message_id','reservation_id','snapshot_sha256',
          'run_id','work','approval','candidate','source_identity','input_identity','launch_contract_sha256',
          'run_directory','origin_wall_ms','origin_monotonic_ns','approval_wall_ms','total_deadline_ms',
          'run_deadline_ms','allocation','read_scope','profile','platform'}
    exact(activation, af, 'v58-activation-fields')
    require(activation['version'] == 58 and activation['kind'] == KIND and activation['template_sha256'] == TEMPLATE_SHA256
            and activation['snapshot_sha256'] == a['accounting_snapshot']['sha256'], 'v58-activation-binding')
    require(text(activation['owner_message_id']) and a['approval'] == 'owner-v58-' + activation['owner_message_id']
            and text(activation['reservation_id']), 'v58-Owner-receipt')
    for key in af & set(a):
        require(activation[key] == a[key], 'v58-activation-drift')
    require(activation['profile'] == {'native_profile':'u2','model':'gpt-6-astra','effort':'xhigh','phase':'synthetic',
                                    'slot':'s4','synthetic_u2_only':True,'native_resume':False}
            and activation['platform'] == 'darwin', 'v58-profile')
    exact(snapshot, ('version','record','captured_wall_ms','total_cap_ms','charged_ms','phase_cap_ms',
                     'phase_charged_ms','counts','limits','consumed_reservations'), 'v58-snapshot-fields')
    exact(snapshot['record'], ('path','sha256'), 'v58-accounting-record')
    # The original cumulative record remains immutable provenance, never a refunded parent epoch.
    bound(snapshot['record'])
    for key in ('captured_wall_ms','total_cap_ms','charged_ms','phase_cap_ms','phase_charged_ms'):
        require(number(snapshot[key]), 'v58-accounting-number')
    require(type(snapshot['version']) is int and snapshot['version'] == 1 and snapshot['captured_wall_ms'] <= a['origin_wall_ms']
            and snapshot['charged_ms'] <= snapshot['total_cap_ms']
            and snapshot['phase_charged_ms'] <= snapshot['phase_cap_ms'], 'v58-accounting-time')
    elapsed = a['origin_wall_ms'] - snapshot['captured_wall_ms']
    total = snapshot['total_cap_ms'] - snapshot['charged_ms'] - elapsed
    phase = snapshot['phase_cap_ms'] - snapshot['phase_charged_ms'] - elapsed
    require(min(total,phase) > 1_820_000 and a['total_deadline_ms'] == a['origin_wall_ms'] + total
            and a['run_deadline_ms'] == a['origin_wall_ms'] + min(total,phase), 'v58-no-time-refund')
    require(type(snapshot['counts']) is dict and type(snapshot['limits']) is dict
            and set(snapshot['counts']) == set(snapshot['limits']) and set(ALLOCATION) <= set(snapshot['counts']), 'v58-counter-keys')
    for key, used in snapshot['counts'].items():
        limit = snapshot['limits'][key]
        require(number(used) and number(limit) and used + ALLOCATION.get(key,0) <= limit, 'v58-counter-refund-or-cap')
    reservations = snapshot['consumed_reservations']
    require(type(reservations) is list and all(text(r) for r in reservations) and len(set(reservations)) == len(reservations)
            and activation['reservation_id'] not in reservations, 'v58-reservation-consumed')
    exact(consumed, ('version','activation_sha256','reservation_id','run_directory','allocation','snapshot_sha256','ledger_row_sha256'), 'v58-consumption-fields')
    require(consumed == {'version':1,'activation_sha256':a['activation']['sha256'],
            'reservation_id':activation['reservation_id'],'run_directory':a['run_directory'],'allocation':ALLOCATION,
            'snapshot_sha256':a['accounting_snapshot']['sha256'],'ledger_row_sha256':consumed['ledger_row_sha256']}
            and type(consumed['version']) is int and sha(consumed['ledger_row_sha256']), 'v58-consumption-binding')
    return activation


def budget_state(budget, rows, now, *, validate_contract=True):
    a = budget.anchor
    if validate_contract:
        contract(a, budget.fresh_bound)
    else:
        anchor_fields(a)
    require(number(now) and rows and len(rows) < 200, 'v58-bounded-journal')
    prev, last, stopped = '', a['origin_wall_ms'], False
    counts, slots, plans, events = {}, {}, {}, []
    current = None
    for i, row in enumerate(rows):
        exact(row, ('event','sha256'), 'v58-row')
        e = row['event']
        exact(e, ('seq','prev','approval','work','candidate','phase','start','kind','subject','at_ms'), 'v58-event')
        require(type(e['seq']) is int and e['seq'] == i and e['prev'] == prev and row['sha256'] == digest(wire_bytes(e))
                and all(e[k] == a[k] for k in ('approval','work','candidate')), 'v58-chain')
        kind, start, phase, sub, at = (e[k] for k in ('kind','start','phase','subject','at_ms'))
        require(kind in LIMITS and type(sub) is dict and number(at) and last <= at <= now and not stopped, 'v58-event-time-stop')
        if kind not in ('genesis','process-ended','execution-stop'):
            require(at + 1_800_000 < min(a['run_deadline_ms'], a['total_deadline_ms']), 'v58-execution-deadline')
        counts[kind] = counts.get(kind,0) + 1
        require(counts[kind] <= LIMITS[kind], 'v58-cap')
        require((i == 0 and kind == 'genesis' and sub == {'anchor_sha256':budget.anchor_sha256}) or (i > 0 and kind != 'genesis'), 'v58-genesis')
        if kind in ('genesis','proxy-start','execution-stop'):
            require(phase == start == 'controller', 'v58-controller')
        else:
            require(phase == 'synthetic' and start in STARTS, 'v58-slot')
        if kind == 'proxy-start':
            require(not slots and sub == {'slot':'s4','start_id':'v58-' + a['run_id']}, 'v58-proxy')
        if kind == 'start':
            require(counts.get('proxy-start') == 1 and start not in slots and start == STARTS[len(slots)]
                    and (not slots or slots[STARTS[0]]['ended']), 'v58-start-order')
            exact(sub, ('execution_binding','proxy_identity_sha256','runtime_spec_sha256'), 'v58-start-fields')
            require(sub['execution_binding'] == {'launch_mode':a['launch_mode'],'launch_contract_sha256':a['launch_contract_sha256'],
                    'epoch_sha256':budget.anchor_sha256,'approval':a['approval'],'direct_tool_policy':a['direct_tool_policy']}
                    and sha(sub['proxy_identity_sha256']) and sha(sub['runtime_spec_sha256']), 'v58-execution-binding')
            require(not slots or sub['proxy_identity_sha256'] == slots[STARTS[0]]['proxy'], 'v58-proxy-restart')
            slots[start] = {'entered':False,'ended':False,'controls':set(),'policy':None,'request':None,'thread':None,'plans':[],
                            'at':at,'proxy':sub['proxy_identity_sha256']}
            current = None
        if kind not in ('genesis','proxy-start','execution-stop'):
            require(start in slots and not slots[start]['ended'], 'v58-inactive-slot')
            slot = slots[start]
            if kind not in ('start','runtime-entered','process-ended'):
                require(slot['entered'] and at - slot['at'] <= 1_780_000, 'v58-native-deadline')
        if kind == 'runtime-entered':
            require(not slot['entered'] and sub == {'start':start}, 'v58-runtime-entry')
            slot['entered'] = True
        if kind == 'control':
            exact(sub, ('endpoint',), 'v58-control-fields')
            endpoint = sub['endpoint']
            require(endpoint in ('policy','models','accounts') and endpoint not in slot['controls'] and slot['request'] is None, 'v58-control-order')
            require((endpoint == 'policy' and slot['policy'] is None and not slot['controls'])
                    or (endpoint in ('models','accounts') and slot['policy'] is not None), 'v58-policy-control-order')
            slot['controls'].add(endpoint)
        if kind == 'policy-admission':
            exact(sub, ('classification',), 'v58-policy-fields')
            classification = sub['classification']
            require(classification in ('applied','applicable-empty','known-not-applicable')
                    and slot['policy'] is None and slot['request'] is None, 'v58-policy-admission')
            require(slot['controls'] == (set() if classification == 'known-not-applicable' else {'policy'}),
                    'v58-policy-correspondence')
            slot['policy'] = classification
        if kind == 'thread':
            exact(sub, ('request',), 'v58-thread-fields')
            expected_controls = {'models','accounts'} if slot['policy'] == 'known-not-applicable' else {'policy','models','accounts'}
            require(sub['request'] is not None and slot['request'] is None and slot['policy'] is not None
                    and slot['controls'] == expected_controls, 'v58-thread-order')
            slot['request'] = sub['request']
        if kind == 'thread-bound':
            exact(sub, ('request','thread'), 'v58-thread-binding-fields')
            require(slot['request'] is not None and sub['request'] == slot['request'] and slot['thread'] is None
                    and text(sub['thread']) and all(s['thread'] != sub['thread'] for s in slots.values()), 'v58-thread-binding')
            slot['thread'] = sub['thread']
        if kind == 'input':
            exact(sub, ('plan','input_sha256','manifest_sha256'), 'v58-input-fields')
            require(slot['thread'] is not None and len(slot['plans']) < 2 and text(sub['plan']) and sub['plan'] not in plans
                    and (current is None or plans[current]['generation'] == 2)
                    and sha(sub['input_sha256']) and sha(sub['manifest_sha256']), 'v58-input-order')
            current = sub['plan']
            plans[current] = {'start':start,'thread':slot['thread'],'began':False,'turn':None,'generation':0,'call':None,
                              'host':False,'outcome':None,'ordinal':len(slot['plans']),'at':at}
            slot['plans'].append(current)
        if kind == 'turn':
            require(current is not None, 'v58-turn-before-input')
            p = plans[current]
            require(sub == {'thread':p['thread'],'plan':current} and not p['began'] and p['start'] == start, 'v58-turn-binding')
            p['began'] = True
        if kind in ('generation','dispatch','host-dispatch','worker-result','host-refusal'):
            require(current is not None, 'v58-effect-before-input')
            p = plans[current]
            require(p['began'] and p['start'] == start and sub.get('plan') == current and sub.get('thread') == p['thread']
                    and text(sub.get('turn')) and p['turn'] in (None,sub['turn']) and at - p['at'] <= 880_000, 'v58-effect-binding')
            if kind == 'generation':
                exact(sub, ('thread','turn','plan','generation'), 'v58-generation-fields')
                require(type(sub['generation']) is int and sub['generation'] == p['generation'] + 1 <= 2
                        and (p['generation'] == 0 or p['outcome'] == 'completed')
                        and all(other is p or other['turn'] != sub['turn'] for other in plans.values()), 'v58-generation-order')
                p['generation'], p['turn'] = sub['generation'], sub['turn']
            else:
                require(p['generation'] == 1 and text(sub.get('call')) and (p['call'] is None or sub['call'] == p['call']), 'v58-call-binding')
                if kind == 'dispatch':
                    exact(sub, ('thread','turn','plan','call'), 'v58-dispatch-fields')
                    require(p['call'] is None and all(other['call'] != sub['call'] for other in plans.values()), 'v58-call-reuse')
                    p['call'] = sub['call']
                elif kind == 'host-dispatch':
                    exact(sub, ('thread','turn','plan','call'), 'v58-host-fields')
                    require(p['call'] is not None and not p['host'], 'v58-host-order')
                    p['host'] = True
                else:
                    require(p['call'] is not None and p['host'] and p['outcome'] is None, 'v58-result-order')
                    fields = ('thread','turn','plan','call','host_terminal_sha256','host_request_sha256','input_identity')
                    require(sub.get('input_identity') == a['input_identity'] and sha(sub.get('host_terminal_sha256'))
                            and sha(sub.get('host_request_sha256')), 'v58-Host-correspondence')
                    if kind == 'worker-result':
                        exact(sub, fields + ('tool','result_sha256','result_identity','oracle_sha256'), 'v58-result-fields')
                        require(p['ordinal'] == 0 and sub['tool'] == 'u2_read_file'
                                and all(sha(sub[k]) for k in ('result_sha256','result_identity','oracle_sha256')), 'v58-read-result')
                        p['outcome'] = 'completed'
                    else:
                        exact(sub, fields + ('reason','effects'), 'v58-refusal-fields')
                        require(p['ordinal'] == 1 and text(sub['reason']) and type(sub['effects']) is int and sub['effects'] == 0, 'v58-refusal')
                        p['outcome'] = 'refused'
        if kind == 'process-ended':
            exact(sub, ('start','process_group_absent','observed_descendants_absent','outcome'), 'v58-process-ended-fields')
            require(sub['start'] == start and sub['process_group_absent'] is True and sub['observed_descendants_absent'] is True
                    and sub['outcome'] == 'rejected-terminated' and len(slot['plans']) == 2
                    and plans[slot['plans'][0]]['generation'] == 2 and plans[slot['plans'][0]]['outcome'] == 'completed'
                    and plans[slot['plans'][1]]['generation'] == 1 and plans[slot['plans'][1]]['outcome'] == 'refused', 'v58-close-pending')
            slot['ended'] = True
        if kind == 'execution-stop':
            exact(sub, ('reason','native_absent','proxy_absent','controller_absent'), 'v58-stop-fields')
            require(text(sub['reason']) and sub['native_absent'] is True and sub['proxy_absent'] is True and sub['controller_absent'] is True, 'v58-stop-absence')
            # A failed run may be terminalized, but pending evidence is retained and never resumed.
            stopped = True
        events.append(e)
        prev, last = row['sha256'], at
    pending = [key for key,p in plans.items() if p['began'] and p['generation'] != 2 and p['outcome'] != 'refused']
    return {'events':events,'history_events':events,'rows':rows,'prev':prev,'counts':counts,'excluded_ms':0,
            'paused_at':None,'stopped':stopped,'active_ms':now,'remaining_ms':min(a['total_deadline_ms'],a['run_deadline_ms'])-now,
            'pending':pending,'slots':slots}
