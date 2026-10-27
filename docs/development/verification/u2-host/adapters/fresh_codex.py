"""v58 materialization and read-only native adapter; activation is a separate Owner action.

The task controller owns cross-journal consumption. Native checks are scoped to
one bound journal. No runtime is started by importing or materializing this module.
"""
import json
import os
from pathlib import Path
import time

from ..contracts import (require, HostRefusal, canonical, wire_bytes, digest, control_read,
    checked_open, durable_private, EffectJournal, ReadOnlyHost, closed_environment)
from ..execution_os import execution_os
from . import codex as native
from . import fresh_codex_contract as policy


def consume_activation(anchor, *, ledger_path, controller_lock_path, admission):
    """Under the existing task lock, consume its exact C allocation once, without refunds.

    admission is the trusted launch admission callable. Its returned receipt must
    bind the fixed source/build/check inventory; OS preflight always precedes it.
    The ledger must already contain the Owner-bound parent reservation. This
    function neither creates that reservation nor authorizes C from B approval.
    """
    runtime = execution_os(require, purpose='codex-v58')
    policy.anchor_fields(anchor)
    activation = native.Budget.fresh_bound(anchor['activation'])
    snapshot = native.Budget.fresh_bound(anchor['accounting_snapshot'])
    expected = {'version':1,'template_sha256':policy.TEMPLATE_SHA256,'activation_sha256':anchor['activation']['sha256'],
        'candidate':anchor['candidate'],'source_identity':anchor['source_identity'],'input_identity':anchor['input_identity'],
        'platform':'darwin','profile':'u2','C_live_authorized':True}
    require(admission() == expected, 'v58-C-launch-admission')
    # Validate every pre-consumption contract field using a synthetic receipt;
    # receipt creation is deferred until the ledger fsync has succeeded.
    preliminary = {'version':1,'activation_sha256':anchor['activation']['sha256'],
        'reservation_id':activation['reservation_id'],'run_directory':anchor['run_directory'],
        'allocation':policy.ALLOCATION,'snapshot_sha256':anchor['accounting_snapshot']['sha256'],
        'ledger_row_sha256':'0' * 64}
    probe = dict(anchor)
    probe['consumption'] = {'path':anchor['consumption']['path'],'sha256':digest(canonical(preliminary))}
    policy.contract(probe, lambda ref: preliminary if ref == probe['consumption'] else native.Budget.fresh_bound(ref))
    lock = runtime.controller_lock(controller_lock_path, checked_open, require)
    try:
        ledger = EffectJournal(ledger_path)
        rid = activation['reservation_id']
        rows = ledger.rows
        reservation = [r for r in rows if r['kind'] == 'v58-parent-reservation' and r['value'].get('reservation_id') == rid]
        require(len(reservation) == 1, 'v58-parent-reservation-unavailable')
        expected_parent = {'reservation_id':rid,'snapshot_sha256':anchor['accounting_snapshot']['sha256'],
            'allocation':policy.ALLOCATION,'owner_message_id':activation['owner_message_id'],'parent':'C-Codex-live',
            'counts_before':snapshot['counts'],'limits':snapshot['limits']}
        require(reservation[0]['value'] == expected_parent and reservation[0] == rows[-1], 'v58-parent-allocation-drift')
        require(not any(r['kind'] == 'v58-consumed' and (r['value'].get('reservation_id') == rid
            or r['value'].get('activation_sha256') == anchor['activation']['sha256']
            or r['value'].get('run_directory') == anchor['run_directory']
            or r['value'].get('snapshot_sha256') == anchor['accounting_snapshot']['sha256']) for r in rows), 'v58-replay-consumed')
        directory = Path(anchor['run_directory'])
        require(directory.parent.resolve(strict=True) == directory.parent and not os.path.lexists(directory), 'v58-run-consumed-or-aliased')
        counts_after = {k:v + policy.ALLOCATION.get(k,0) for k,v in snapshot['counts'].items()}
        row = ledger.append('v58-consumed', {**preliminary, 'counts_before':snapshot['counts'], 'counts_after':counts_after})
        # No rollback after this point. Any publication/creation failure stays consumed/Hold.
        receipt = {**preliminary,'ledger_row_sha256':row['sha256']}
        final = dict(anchor)
        final['consumption'] = {'path':anchor['consumption']['path'],'sha256':digest(canonical(receipt))}
        durable_private(final['consumption']['path'], receipt)
        budget = native.Budget.create(directory, final)
        return budget
    finally:
        lock.close()


class RefusedTurn(HostRefusal):
    """The durable Host refusal must never become a tool result sent to a model."""


class ReadAdmission(native.Admission):
    def __init__(self, cfg, spec, budget, start):
        # Reuse prepared-envelope validation, without inheriting an authority identity.
        self.identity = cfg['identity']
        self.identity_hash = digest(canonical(self.identity))
        self.tools = spec['dynamic_tools']
        require(isinstance(self.tools, list) and len(self.tools) == 4
                and {tool.get('name') for tool in self.tools if isinstance(tool, dict)}
                    == {'u2_read_file','u2_write_file','u2_verify','u2_accept'}, 'v58-four-tool-inventory')
        self.read_files = set(cfg['documents']['files'])
        self.source, self.candidate, self.template = spec['source_identity'], spec['candidate'], spec['input_template_identity']
        self.budget, self.phase, self.start = budget, 'synthetic', start
        self.session = self.step = self.plan = self.manifest_sha = None
        self.call = self.envelope_sha = None
        self.used_calls = set()
        self.completed, self.stopped, self.sealed = True, False, False

    def callback(self, params):
        require(not self.stopped and not self.completed and self.call is None and self.turn is not None, 'v58-callback-state')
        policy.exact(params, ('threadId','turnId','callId','namespace','tool','arguments'), 'v58-callback-fields')
        require(params['threadId'] == self.thread and params['turnId'] == self.turn and params['namespace'] is None
                and policy.text(params['callId']) and params['callId'] not in self.used_calls, 'v58-callback-identity')
        require(digest(canonical(self.identity)) == self.identity_hash, 'v58-Host-identity-drift')
        state = self.budget.read()
        plans = state['slots'].get(self.start, {}).get('plans', [])
        require(len(plans) in (1, 2) and plans[-1] == self.plan, 'v58-callback-plan-order')
        require(params['tool'] == 'u2_read_file', 'v58-unexpected-tool-before-effect')
        if len(plans) == 2:
            arguments = params['arguments']
            require(isinstance(arguments, dict) and set(arguments) == {'file_ids'}
                    and isinstance(arguments['file_ids'], list) and arguments['file_ids']
                    and all(isinstance(value, str) for value in arguments['file_ids'])
                    and any(value not in self.read_files for value in arguments['file_ids']),
                    'v58-unexpected-valid-read-before-effect')
        # The reducer requires the native dispatch reservation with the same identity.
        self.budget.reserve('host-dispatch', self.dispatch_subject(params['callId']), self.phase, self.start)
        self.call = params['callId']
        self.used_calls.add(self.call)
        return params['tool'], params['arguments']


class FreshCodexSession(native.LiveSession):
    """Two native slots share a living proxy and task controller, never a native session."""
    def __init__(self, spec, budget, run, *, gate, fd_controller):
        self.os = execution_os(require, purpose='codex-v58')
        require(budget.anchor['version'] == 58 and isinstance(gate, ReadOnlyHost), 'v58-session-contract')
        policy.contract(budget.anchor, budget.fresh_bound)
        super().__init__(spec, budget, run, fd_controller)
        self.gate = gate
        self.rejected = self.closed = False
        self.known = {}
        self.spawned_process = None
        self.cleanup = {}
        self.admission = ReadAdmission(gate.cfg, self.runtime_spec, budget, self.start)
        scope = budget.anchor['read_scope']
        require(scope == {'core_snapshot_sha256':gate.cfg['core_snapshot_sha256'], 'identity_sha256':gate.cfg['identity_sha256'],
                         'files':{k:v['sha256'] for k,v in gate.cfg['documents']['files'].items()}}, 'v58-Host-scope-binding')

    def proxy_identity(self):
        proxy = self.fd_controller
        require(proxy is not None and proxy.proxy is not None and proxy.proxy.poll() is None and proxy.thread is not None
                and proxy.thread.is_alive() and proxy.failed is None and not proxy.closed, 'v58-shared-proxy-unavailable')
        return digest(canonical({'pid':proxy.proxy.pid,'nonce':proxy.nonce,'reservation':proxy.reservation,
                                 'anchor_sha256':proxy.budget.anchor_sha256,'path':str(proxy.socket_path)}))

    def launch(self):
        self.gate.check_core()
        state = self.budget.read()
        require(not state['stopped'] and not state['pending'], 'v58-resume-pending-stop')
        if self.start == policy.STARTS[1]:
            require(not self.fd_controller.leases and not self.fd_controller.lease_bindings, 'v58-proxy-pending-lease')
            require(state['slots'].get(policy.STARTS[0],{}).get('ended') is True and not self.gate.pending
                    and self.gate.runtime_counts['native-start'] == 1, 'v58-fresh-resume-order')
        runtime = self.spec['runtime']
        require(self.runtime_spec.get('transport') == self.fd_controller.runtime_transport(), 'v58-FD-binding')
        env = closed_environment({'TMPDIR':str(Path(self.runtime_spec['root']) / 'tmp')})
        argv, identity, self.launch_contract = native.validate_native_launch(runtime, self.runtime_spec, self.budget.anchor, self.budget.anchor_sha256, env)
        require(self.fd_controller.selected_peer == self.launch_contract['network']['peer'] == '104.18.32.47',
                'v58-controller-contract-peer')
        self.execution_binding = {'launch_mode':self.budget.anchor['launch_mode'], 'launch_contract_sha256':self.budget.anchor['launch_contract_sha256'],
            'epoch_sha256':self.budget.anchor_sha256, 'approval':self.budget.anchor['approval'],'direct_tool_policy':self.budget.anchor['direct_tool_policy']}
        root = Path(self.runtime_spec['root'])
        for name in ('home','cwd','config','tmp'):
            path = root / name
            require(path.is_dir() and path.resolve(strict=True) == path, 'v58-runtime-directory')
        require(not list((root / 'config').iterdir()), 'v58-runtime-config')
        require(self.runtime_spec['start'] == self.start and self.runtime_spec['phase'] == 'synthetic'
                and self.runtime_spec['expires_unix_ms'] <= time.time_ns() // 1_000_000 + 1_800_000, 'v58-native-lifetime')
        self.auth_metadata_before = native.protected_auth_metadata(self.runtime_spec['auth_home'])
        durable_private(self.run / 'protected-metadata-before.json', self.auth_metadata_before)
        self.budget.reserve('start', {'execution_binding':self.execution_binding,'proxy_identity_sha256':self.proxy_identity(),
            'runtime_spec_sha256':runtime['spec_sha256']}, self.phase, self.start)
        self.gate.reserve_runtime('native-start', {'session':self.start})
        def register(process):
            # Retain ownership even if LiveClient's constructor never returns.
            self.spawned_process = process
            self.os.observe_owned(process, self.known)
            self.fd_controller.register_runtime(runtime, process)
        self.client = native.LiveClient(argv, Path(identity['cwd']), self.run, min(self.deadline(),time.monotonic()+30), env,
            on_spawn=register)
        self.os.observe_owned(self.client.process, self.known)
        native.bind_native_notifications(self.client, runtime, self.runtime_spec, self.budget.anchor)
        self.client.on_event, self.client.callback = self.on_event, self.callback
        self.client.request('initialize', {'clientInfo':{'name':'colvia_u2_qualification','version':'0.1'},'capabilities':{'experimentalApi':True}})
        self.check_auth_metadata()
        self.client.deadline = self.deadline()
        self.client.send({'method':'initialized','params':{}})
        self.client.validate_account_bootstrap()
        request_id = self.client.sequence + 1
        result = self.client.request('thread/start', {'ephemeral':True,'dynamicTools':self.runtime_spec['dynamic_tools']})
        require(result['thread']['ephemeral'] is True and result['model'] == 'gpt-6-astra' and result['modelProvider'] == 'openai'
                and result['reasoningEffort'] == 'xhigh' and result['approvalPolicy'] == 'never', 'v58-thread-admission')
        self.thread = result['thread']['id']
        self.budget.reserve('thread-bound', {'request':request_id,'thread':self.thread}, self.phase, self.start)
        self.client.drain()
        return self.thread

    def callback(self, params):
        tool, arguments = self.admission.callback(params)
        subject = self.admission.dispatch_subject(params['callId'])
        gate = self.gate
        gate.reserve_runtime('bridge-request', {'session':self.start,'request_id':params['callId']})
        if (gate.session,gate.step) != (self.thread,self.admission.turn):
            gate.open_step(self.thread,self.admission.turn)
        before = gate.effects
        result = gate.dispatch({'session':self.thread,'step':self.admission.turn,'call_id':params['callId'],
            'tool':tool,'arguments':arguments,'identity':gate.cfg['identity']})
        rows = gate.journal.rows
        terminal = rows[-1]
        require(terminal['kind'] in ('completed','refused') and gate.pending is None, 'v58-Host-terminal-unknown')
        request_seq = terminal['value']['request_seq']
        request = next((r for r in rows if r['seq'] == request_seq), None)
        require(request is not None and request['kind'] == 'request' and request['value']['call_id'] == params['callId'], 'v58-Host-request-correspondence')
        binding = {**subject,'host_terminal_sha256':terminal['sha256'],'host_request_sha256':request['sha256'],
                   'input_identity':self.budget.anchor['input_identity']}
        if not result['ok']:
            require(gate.effects == before, 'v58-refusal-effect-unknown')
            self.budget.reserve('host-refusal', {**binding,'reason':result['code'],'effects':0},self.phase,self.start)
            self.rejected = True
            # Raising prevents LiveClient from sending any result or further generation.
            raise RefusedTurn('v58-durable-refusal')
        require(tool == 'u2_read_file' and gate.effects == before + 1, 'v58-read-only-result')
        raw = canonical(result['result'])
        self.budget.reserve('worker-result', {**binding,'tool':tool,'result_sha256':digest(raw),
            'result_identity':digest(canonical({'request':request['sha256'],'result':digest(raw)})),
            'oracle_sha256':digest(canonical({'core':gate.cfg['core_snapshot_sha256'],'files':self.budget.anchor['read_scope']['files']}))},self.phase,self.start)
        text = wire_bytes(result['result']).decode()
        require(len(text.encode()) <= 64_000, 'v58-callback-size')
        return {'contentItems':[{'type':'inputText','text':text}], 'success':True}

    def iterate(self):
        raise HostRefusal('v58-requires-exact-read-and-refusal-inputs')

    def checkpoint(self):
        state = self.budget.read()
        self.checkpoint_number += 1
        value = {'version':58,'anchor_sha256':self.budget.anchor_sha256,'journal_seq':len(state['rows']) - 1,
            'journal_sha256':state['prev'],'input_identity':self.budget.anchor['input_identity'],
            'core_snapshot_sha256':self.gate.cfg['core_snapshot_sha256'],'config_sha256':self.gate.cfg_sha256,
            'start':self.start,'thread':self.thread,'pending':state['pending'],'counts':state['counts']}
        durable_private(self.run / ('checkpoint-%03d.json' % self.checkpoint_number), value)
        return value

    def turn(self, inputs):
        require(not self.closed and not self.rejected, 'v58-turn-closed')
        self.proxy_identity()
        self.gate.reserve_runtime('host-input', {'session':self.start,'step':'input-' + str(self.gate.runtime_counts['host-input'] + 1)})
        try:
            return super().turn(inputs)
        except RefusedTurn:
            self.close()
            return {'status':'rejected-terminated'}
        except BaseException:
            # A model deviation is a Hold, never a successful negative case.
            self.close()
            raise

    def close(self):
        if self.closed:
            return
        self.closed = True
        failure, absent = None, False
        try:
            self.gate.stop()
        except BaseException as error:
            failure = error
        # Preserve only transport-generated diagnostics; never raw responses or identifiers.
        try:
            if self.client is not None:
                rpc = getattr(self.client, 'rpc_failure', None)
                keys = ('method', 'stage', 'id_matches', 'has_error', 'error_code', 'error_message_sha256')
                durable_private(self.run / 'rpc-metadata.json', {
                    'version':58, 'stage':self.client.rpc_stage,
                    'initialized':self.client.initialized, 'failed':self.client.failed,
                    'rpc_failure':{key:rpc.get(key) for key in keys} if rpc is not None else None})
        except BaseException as error:
            failure = failure or error
        self.admission.stop()
        process = self.client.process if self.client is not None else self.spawned_process
        if process is not None:
            try:
                self.fd_controller.revoke(self.start)
            except BaseException as error:
                failure = failure or error
            try:
                absent = self.os.stop_owned(process, self.known, lambda:self.os.observe_owned(process,self.known))
            except BaseException as error:
                failure = failure or error
            finally:
                if self.client is not None:
                    self.client.selector.close()
                for name in ('stdin','stdout','stderr'):
                    getattr(process,name).close()
            self.cleanup = {'process_group_absent':absent,'observed_descendants_absent':absent}
            if self.client is not None:
                self.client.cleanup = dict(self.cleanup)
            try:
                durable_private(self.run / 'v58-native-close.json', {'start':self.start,'rejected':self.rejected,**self.cleanup})
                self.check_auth_metadata()
                require(absent, 'v58-native-absence-unknown')
                self.gate.native_stopped(self.start, True)
                if self.rejected and failure is None:
                    self.budget.reserve('process-ended', {'start':self.start,'process_group_absent':True,
                        'observed_descendants_absent':True,'outcome':'rejected-terminated'},self.phase,self.start,allow_closeout=True)
            except BaseException as error:
                failure = failure or error
        else:
            failure = failure or HostRefusal('v58-native-absence-unavailable')
        self.gate.close()
        if failure is not None:
            raise failure


def materialize_runtime(budget, blueprint, destination, transport):
    """Bind an already admitted static launch blueprint to the consumed epoch."""
    policy.contract(budget.anchor, budget.fresh_bound)
    a = budget.anchor
    require(blueprint['start'] in policy.STARTS and blueprint['phase'] == 'synthetic' and blueprint['profile'] == 'u2', 'v58-blueprint-profile')
    spec = {**blueprint,'version':2,'launch_mode':'trusted-native-runtime','candidate':a['candidate'],
        'source_identity':a['source_identity'],'approval':a['approval'],'work':a['work'],
        'journal':str(budget.path),'journal_lock':str(budget.lock_path),'journal_anchor':str(budget.directory / 'anchor.json'),
        'journal_anchor_sha256':budget.anchor_sha256,'execution_template_sha256':policy.TEMPLATE_SHA256,
        'launch_contract_sha256':a['launch_contract_sha256'],'direct_tool_policy':a['direct_tool_policy'],'transport':transport}
    require(spec['expires_unix_ms'] <= min(a['run_deadline_ms'], a['total_deadline_ms'] - 1_800_000), 'v58-blueprint-deadline')
    require(str(destination) == str(Path(spec['root']) / 'spec.json'), 'v58-spec-destination')
    policy.exact(transport, ('path','nonce','slot','max_requests'), 'v58-runtime-transport')
    require(transport['slot'] == 's4' and type(transport['max_requests']) is int and 0 < transport['max_requests'] <= 12, 'v58-runtime-transport')
    durable_private(destination, spec)
    return {'path':str(destination),'sha256':digest(canonical(spec))}


def materialize_proxy(budget, controller, destination, expires_wall_ms):
    state = budget.read()
    require(state['events'][-1]['kind'] == 'proxy-start' and controller.budget is budget and controller.slot == 's4', 'v58-proxy-materialization-order')
    require(type(expires_wall_ms) is int and time.time_ns() // 1_000_000 < expires_wall_ms <= min(
        budget.anchor['run_deadline_ms'], budget.anchor['total_deadline_ms'] - 1_800_000), 'v58-proxy-expiry')
    spec = {'version':2,'candidate':budget.anchor['candidate'],'slot':'s4','journal_anchor':budget.anchor,
        'journal_anchor_sha256':budget.anchor_sha256,'journal_snapshot':state['rows'],
        'expires_wall_ms':expires_wall_ms,'transport':controller.transport_spec()}
    durable_private(destination, spec)
    return {'path':str(destination),'sha256':digest(canonical(spec))}


def stop_execution(budget, controller, sessions, reason):
    """Whole-execution terminalization after native/proxy/controller absence is observed."""
    failures = []
    for session in sessions:
        try:
            session.close()
        except BaseException as error:
            failures.append(error)
    try:
        controller.close()
    except BaseException as error:
        failures.append(error)
    starts = {event['start'] for event in budget.read()['events'] if event['kind'] == 'start'}
    by_start = {session.start:session for session in sessions}
    require(len(by_start) == len(sessions) and starts <= set(by_start), 'v58-final-native-unrepresented')
    for start, session in by_start.items():
        process = session.client.process if session.client is not None else session.spawned_process
        if start in starts or process is not None:
            require(process is not None and process.poll() is not None
                    and session.cleanup.get('process_group_absent') is True
                    and session.cleanup.get('observed_descendants_absent') is True, 'v58-final-native-unknown')
    require(controller.closed and (controller.proxy is None or controller.proxy.poll() is not None)
            and (controller.thread is None or not controller.thread.is_alive()) and not controller.leases, 'v58-final-proxy-unknown')
    event = budget.reserve('execution-stop', {'reason':reason,'native_absent':True,'proxy_absent':True,'controller_absent':True}, allow_closeout=True)
    if failures:
        raise failures[0]
    return event
