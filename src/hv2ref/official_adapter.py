"""Bounded App Server stdio adapter; model callbacks never carry authority."""
import json
import os
from pathlib import Path
import selectors
import signal
import subprocess
import time
from . import official_state as state
from .official_documents import reject_duplicate_keys
from .official_admission import MODEL, PROFILE, DIRECT_FALLBACK, launch_spec, preflight
from .official_host import reason_code
from .official_controller import checked_payload

LIMIT = 1048576

def signal_owned(pid, sig, *, group=False):
    try:
        (os.killpg if group else os.kill)(pid, sig)
        return True
    except ProcessLookupError:
        return True
    except PermissionError:
        return False

class CancelRequested(Exception):
    """Wake the turn loop to interrupt; not an execution success."""

class Rpc:
    def __init__(self, spec, host):
        self.spec, self.host = spec, host
        self.seq = self.trace_bytes = self.err_bytes = 0
        self.outgoing_bytes = self.outgoing_frames = 0
        self.outgoing_partial = False
        self.buf = b''; self.messages = []; self.held = []; self.known_children = {}
        self.consumed = set(); self.interrupted = False; self.direct_fallback_seen = False
        self.started = time.monotonic(); self.deadline = host.deadline
        self.last_scan = 0; self.p = None; self.closed = False
        self.reserved = self.spawn_failed = False
        self.sel = selectors.DefaultSelector()
        host.rpc = self  # Visible to finally even if spawn/identity publication fails.
        host.authority()
        self.reserved = True
        host.journal.append('runtime-reserved', {'ordinal':1,'host_pid':os.getpid(),
                                               'host_birth':state.process_birth(os.getpid())})
        try:
            self.p = subprocess.Popen(spec['argv'], cwd=spec['cwd'], env=spec['env'], stdin=subprocess.PIPE,
                                      stdout=subprocess.PIPE, stderr=subprocess.PIPE, start_new_session=True, close_fds=True)
        except (OSError, subprocess.SubprocessError):
            host.journal.append('runtime-spawn-failed', {'ordinal':1,'reason':'spawn_failed','reaped':True})
            self.spawn_failed = True
            raise
        try:
            birth = state.process_birth(self.p.pid)
        except BaseException:
            host.journal.append('runtime-started', {'ordinal':1,'pid':self.p.pid,'birth':None})
            raise
        self.runtime_ref = host.journal.append('runtime-started', {'ordinal':1,'pid':self.p.pid,'birth':birth or None})['seq']
        state.need(bool(birth), 'runtime-birth-unavailable')
        for stream, label in ((self.p.stdout,'out'), (self.p.stderr,'err')):
            os.set_blocking(stream.fileno(), False); self.sel.register(stream, selectors.EVENT_READ, label)

    def log(self, kind, value):
        # External method names/IDs/keys and exception content stay in memory.
        size = len(json.dumps(value, ensure_ascii=False).encode())
        self.trace_bytes += size; state.need(self.trace_bytes <= LIMIT, 'protocol-storage-limit')
        if kind in ('rpc-error', 'runtime-diagnostic'):
            self.host.diagnostic('runtime', 'worker', 'protocol_refused', size)

    def err(self, raw):
        self.err_bytes += len(raw)
        self.host.diagnostic('runtime', 'worker', 'protocol_refused', len(raw))
        state.need(self.err_bytes <= LIMIT, 'stderr-limit')
        state.need(not raw, 'protocol_refused')

    def send(self, value):
        # Serialize once, then inspect that same immutable frame before its first
        # byte can enter the CLI. Nested tool-result JSON is checked decoded too.
        # A failed partial frame cannot be completed by a later interrupt/reply.
        state.need(not self.outgoing_partial, 'protocol_refused')
        raw = checked_payload(value, limit=LIMIT - 1, deadline=self.deadline, protocol=True) + b'\n'
        frame = json.loads(raw, object_pairs_hook=reject_duplicate_keys)
        state.need(type(frame) is dict, 'content_rejected')
        if 'method' in frame:
            method = frame['method']
            state.need(type(method) is str, 'content_rejected')
            if method == 'initialized':
                state.need(set(frame) == {'method'}, 'content_rejected')
            else:
                state.need(set(frame) == {'id', 'method', 'params'} and type(frame['id']) is int and
                           type(frame['params']) is dict and method in
                           ('initialize', 'config/read', 'account/read', 'model/list', 'thread/start', 'turn/start', 'turn/interrupt'),
                           'content_rejected')
                if method == 'turn/start':
                    checked_payload(frame['params']['input'], deadline=self.deadline)
        else:
            state.need(set(frame) == {'id', 'result'} and type(frame['id']) in (int, str), 'content_rejected')
            checked_payload(frame['id'], deadline=self.deadline)
            result = frame['result']
            state.need(type(result) is dict and set(result) == {'contentItems', 'success'} and
                       type(result['success']) is bool, 'content_rejected')
            items = result['contentItems']
            state.need(type(items) is list and len(items) == 1 and type(items[0]) is dict and
                       set(items[0]) == {'type', 'text'} and items[0]['type'] == 'inputText' and
                       type(items[0]['text']) is str, 'content_rejected')
            checked_payload(json.loads(items[0]['text'], object_pairs_hook=reject_duplicate_keys), deadline=self.deadline)
        state.need(time.monotonic() < self.deadline, 'deadline')
        # A runtime that stops reading must not trap the Host before closure.
        fd = self.p.stdin.fileno(); os.set_blocking(fd, False); offset = 0
        with selectors.DefaultSelector() as writable:
            writable.register(fd, selectors.EVENT_WRITE)
            while offset < len(raw):
                remaining = self.deadline - time.monotonic()
                if remaining <= 0: raise TimeoutError('deadline')
                if not writable.select(min(.1, remaining)): continue
                try: sent = os.write(fd, raw[offset:offset + 16384])
                except BlockingIOError: continue
                state.need(sent > 0, 'protocol_refused')
                offset += sent
                self.outgoing_bytes += sent
                self.outgoing_partial = True
        self.outgoing_frames += 1
        self.outgoing_partial = False

    def descendants(self):
        if self.p is None:
            return
        todo = [self.p.pid]; visited = set()
        while todo:
            parent = todo.pop()
            output = subprocess.run(['/usr/bin/pgrep','-P',str(parent)], capture_output=True, text=True, timeout=2)
            state.need(output.returncode in (0,1), 'process-observation-unavailable')
            for item in output.stdout.split():
                pid = int(item)
                if pid in visited:
                    continue
                visited.add(pid); todo.append(pid)
                birth = state.process_birth(pid)
                if birth and pid not in self.known_children:
                    self.known_children[pid] = birth
                    self.host.journal.append('runtime-child', {'pid':pid,'birth':birth})

    def next(self, seconds=30, *, allow_cancel=True):
        until = min(time.monotonic() + seconds, self.deadline)
        while time.monotonic() < until:
            if allow_cancel and self.host.cancelled():
                raise CancelRequested()
            if self.messages:
                return self.messages.pop(0)
            if time.monotonic() - self.last_scan >= 1:
                self.descendants(); self.last_scan = time.monotonic()
            for key, _ in self.sel.select(min(.1, max(0, until - time.monotonic()))):
                raw = os.read(key.fileobj.fileno(), 65536)
                if not raw:
                    self.sel.unregister(key.fileobj); continue
                if key.data == 'err':
                    self.err(raw); continue
                self.buf += raw; state.need(len(self.buf) <= LIMIT, 'protocol-frame-limit')
                while b'\n' in self.buf:
                    line, self.buf = self.buf.split(b'\n', 1)
                    if line:
                        self.messages.append(json.loads(line, object_pairs_hook=reject_duplicate_keys))
                    state.need(len(self.messages) <= 1024, 'protocol-queue-limit')
            if self.p.poll() is not None and not self.messages:
                raise RuntimeError('App Server exited')
        raise TimeoutError('bounded RPC wait')

    def event(self, seconds=30, *, allow_cancel=True):
        return self.held.pop(0) if self.held else self.next(seconds, allow_cancel=allow_cancel)

    def notification(self, message, *, preflight_only=False):
        state.need(type(message) is dict and 'id' not in message, 'unexpected-server-request')
        method = message.get('method'); value = message.get('params', {})
        state.need(type(method) is str and type(value) is dict, 'notification-shape')
        self.log('notification', {'method':method,'keys':sorted(value),'item_type':value.get('item',{}).get('type')})
        if method == 'warning' and set(value) == {'message','threadId'} and value['message'] == DIRECT_FALLBACK:
            state.need(not self.direct_fallback_seen, 'duplicate-fallback-warning')
            self.direct_fallback_seen = True
            self.log('direct-tool-fallback', {'exact_warning':True,'permissions_changed':False})
            return None
        if method in ('warning','configWarning','error'):
            self.log('runtime-diagnostic', value); state.need(False, 'runtime-diagnostic-refusal')
        state.need(method != 'remoteControl/status/changed' or value.get('status') == 'disabled', 'remote-control-active')
        state.need(method != 'item/started' or value.get('item',{}).get('type') in
                   ('dynamicToolCall','reasoning','agentMessage','userMessage'), 'unexpected-native-item')
        if preflight_only:
            state.need(method in ('remoteControl/status/changed','account/updated','thread/started',
                                  'thread/status/changed','turn/started'), 'unexpected-preflight-event')
        return value.get('turn') if method == 'turn/completed' else None

    def request(self, method, params, seconds=30):
        if method in ('initialize','config/read','account/read','model/list','thread/start','turn/start','turn/interrupt'):
            state.need(method not in self.consumed, 'RPC-attempt-already-consumed')
            self.host.journal.append('rpc-reserved', {'method':method})
            self.consumed.add(method)
        self.seq += 1; ident = self.seq
        self.send({'id':ident,'method':method,'params':params}); self.log('request', {'id':ident,'method':method})
        until = time.monotonic() + seconds
        while True:
            message = self.next(max(.001, until - time.monotonic()), allow_cancel=method != 'turn/interrupt')
            if message.get('id') == ident and 'method' not in message:
                if 'error' in message:
                    self.log('rpc-error', message['error']); state.need(False, 'RPC-refused')
                self.log('response', {'id':ident,'method':method}); return message.get('result')
            if method == 'turn/interrupt' or (method == 'turn/start' and message.get('method') == 'item/tool/call'):
                self.held.append(message); state.need(len(self.held) <= 32, 'held-callback-limit')
            else:
                self.notification(message, preflight_only=True)

    def reply(self, message, result, success=True):
        text = checked_payload(result, deadline=self.deadline).decode('utf-8')
        self.send({'id':message['id'],'result':{'contentItems':[{'type':'inputText','text':text}],'success':success}})
        self.log('tool-response', {'id':message['id'],'success':success,'completed':self.host.completed})

    def interrupt(self):
        state.need(self.host.turn is not None, 'turn-identity-unavailable')
        self.interrupted = True
        self.request('turn/interrupt', {'threadId':self.host.thread,'turnId':self.host.turn}, seconds=15)
        until = min(time.monotonic() + 15, self.deadline)
        callbacks = 0
        while time.monotonic() < until:
            message = self.event(max(.001, until - time.monotonic()), allow_cancel=False)
            if message.get('method') == 'item/tool/call':
                callbacks += 1; state.need(callbacks <= 8, 'late-callback-limit')
                self.host.refuse(reason='cancelled')
                self.reply(message, {'ok':False,'effect_status':'not_started','reason':'authority-revoked'}, False)
            else:
                turn = self.notification(message)
                if turn is not None:
                    state.need(turn['id'] == self.host.turn and turn['status'] == 'interrupted', 'interrupt-unconfirmed')
                    self.log('interrupted', {'turnId':turn['id']}); return
        raise TimeoutError('interrupt completion unavailable')

    def close(self):
        if self.closed:
            state.need(hasattr(self, 'close_result'), 'previous-close-unconfirmed')
            return self.close_result
        self.closed = True
        scan_confirmed = True
        try:
            if self.p is None:
                self.close_result = {'observed_tree_absent':(not self.reserved) or self.spawn_failed,'runtime_spawn_failed':getattr(self, 'spawn_failed', False)}
                return self.close_result
            try:
                self.descendants()
            except BaseException:
                scan_confirmed = False
            if self.p.stdin and not self.p.stdin.closed:
                try:
                    self.p.stdin.close()
                except OSError:
                    pass  # A broken flush cannot skip owned-process termination.
            try:
                self.p.wait(timeout=2)
            except subprocess.TimeoutExpired:
                signal_owned(self.p.pid, signal.SIGTERM, group=True)
                try:
                    self.p.wait(timeout=2)
                except subprocess.TimeoutExpired:
                    signal_owned(self.p.pid, signal.SIGKILL, group=True)
                    try:
                        self.p.wait(timeout=2)
                    except subprocess.TimeoutExpired:
                        scan_confirmed = False
            for sig in (signal.SIGTERM, signal.SIGKILL):
                if state.group_absent(self.p.pid):
                    break
                scan_confirmed = signal_owned(self.p.pid, sig, group=True) and scan_confirmed
                until = time.monotonic() + 2
                while not state.group_absent(self.p.pid) and time.monotonic() < until:
                    time.sleep(.05)
            children = []
            for pid, birth in self.known_children.items():
                try:
                    for sig in (signal.SIGTERM, signal.SIGKILL):
                        if state.process_birth(pid) != birth:
                            break
                        scan_confirmed = signal_owned(pid, sig) and scan_confirmed
                        until = time.monotonic() + 2
                        while state.process_birth(pid) == birth and time.monotonic() < until:
                            time.sleep(.05)
                    children.append({'pid':pid,'birth':birth,'absent':state.process_birth(pid) != birth})
                except Exception:
                    scan_confirmed = False
                    children.append({'pid':pid,'birth':birth,'absent':False})
            absence = scan_confirmed and state.group_absent(self.p.pid) and all(x['absent'] for x in children)
            result = {'returncode':self.p.returncode,'observed_tree_absent':absence,'children':children,
                      'final_descendant_scan_confirmed':scan_confirmed,
                      'limitation':'owned descendant sampling does not prove absence of unseen detached daemons'}
            if absence:
                self.host.journal.append('processes-closed', {'runtime_ref':self.runtime_ref, 'group_absent':True,
                    'final_scan_confirmed':True, 'children':children})
            self.close_result = result
            return result
        finally:
            if self.p is not None:
                for stream in (self.p.stdout,self.p.stderr):
                    stream.close()
            self.sel.close()


def run(host):
    rpc = None; status = 'unknown'; error = None
    try:
        if host.cancelled():
            host.revoke('cancelled')
            return host.finish('revoked-before-launch')
        checked_payload(host.spec['request']['prompt'], deadline=host.deadline)
        host.controller.preflight_inputs()
        spec = launch_spec(host)
        rpc = Rpc(spec, host)
        preflight(rpc)
        response = rpc.request('thread/start', {'model':MODEL,'modelProvider':'openai','cwd':spec['cwd'],
            'approvalPolicy':'never','permissions':PROFILE,'ephemeral':True,'environments':[], 'runtimeWorkspaceRoots':[],
            'allowProviderModelFallback':False,'baseInstructions':'Use only the three supplied dynamic tools for the approved document task. The external Host owns every effect.',
            'developerInstructions':'Read the declared IDs once, replace the approved range once, verify DOC-LINKS then DOC-GFM then DOC-CLAIMS. Await each response. No parallel calls or retries. Finish after verification.',
            'dynamicTools':spec['tools']})
        state.need(response.get('model') == MODEL, 'model-mismatch')
        # Consume queued startup diagnostics before the only model turn.
        until = min(time.monotonic() + 2, host.deadline)
        while time.monotonic() < until:
            try:
                message = rpc.next(max(.001, until-time.monotonic()))
            except TimeoutError:
                break
            rpc.notification(message, preflight_only=True)
        thread = response['thread']['id']
        turn = rpc.request('turn/start', {'threadId':thread,'input':[{'type':'text','text':host.spec['request']['prompt']}],
                                        'model':MODEL,'effort':'low','environments':[],'permissions':PROFILE})['turn']['id']
        host.bind(thread, turn)
        while time.monotonic() < host.deadline:
            if host.revoked or host.cancelled():
                host.revoke('cancelled' if host.cancelled() else 'worker_budget_consumed')
                rpc.interrupt(); status = 'interrupted'; break
            try:
                message = rpc.event(min(30,host.deadline-time.monotonic()))
            except TimeoutError:
                continue
            except CancelRequested:
                host.revoke('cancelled'); rpc.interrupt(); status = 'interrupted'; break
            if message.get('method') == 'item/tool/call' and 'id' in message:
                result = host.dispatch(message['params'])
                if not result['ok']:
                    rpc.reply(message, result, False)
                    rpc.interrupt()
                    status = 'unknown' if host.pending is not None or host.journal.history().latch else 'interrupted'
                    break
                if host.completed == 5:
                    if host.cancelled():
                        host.revoke('cancelled'); rpc.reply(message, result['result'])
                        rpc.interrupt(); status = 'interrupted'; break
                    host.seal()
                rpc.reply(message, result['result'])
            else:
                completed = rpc.notification(message)
                if completed is not None:
                    state.need(completed['id'] == host.turn and completed['status'] == 'completed' and host.sealed, 'premature-completion')
                    status = 'completed'; break
        else:
            raise TimeoutError('deadline')
    except BaseException as caught:
        error = caught
        if not host.revoked:
            host.revoke(reason_code(caught, 'protocol_refused'))
        if host.pending is None and host.cancelled():
            rpc = rpc or host.rpc
            if rpc is not None and host.turn is not None:
                try:
                    rpc.interrupt(); status = 'interrupted'; error = None
                except BaseException as interrupt_error:
                    error = interrupt_error
            elif rpc is None or 'turn/start' not in rpc.consumed:
                status = 'revoked-before-launch'; error = None
            # Final effect/process evidence decides closure even without a turn ID.
    finally:
        rpc = rpc or host.rpc
        try:
            if rpc is not None:
                closed = rpc.close()
                if not closed.get('observed_tree_absent'):
                    status = 'unknown'
            elif host.cancelled():
                status = 'revoked-before-launch'
        except BaseException as close_error:
            error = error or close_error
            status = 'unknown'
        if error is not None:
            result = host.fail(error)
            if result is not None and result['status'] in state.TERMINAL:
                error = None
        elif not host.terminal:
            try:
                result = host.finish(status)
            except BaseException as finish_error:
                error = finish_error
                host.fail(error)
    if error is not None:
        raise error
    return result
