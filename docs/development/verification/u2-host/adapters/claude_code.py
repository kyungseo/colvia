"""Pinned Claude Code native CLI adapter for the source-only read/verify profile.

Internal API sends, retries and OAuth writes remain inside the explicitly approved
native trust boundary. Host reservations count starts/inputs/bridge calls only.
This adapter neither implements nor claims Codex prepared-sender guarantees.
"""
from __future__ import annotations
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import os
import signal
import time
import uuid

from ..execution_os import execution_os

from ..contracts import (HostRefusal, require, canonical, digest, control_read,
                         durable_private, reject_duplicate_keys)

MODEL = 'claude-sonnet-5-5'
CLI_SHA256 = 'ffb64331bc0ee1b69efb7c2c428bd3ab516bc31b75bf60886b356c97c1c25ffd'
SETTINGS = {'disableAllHooks': True, 'autoMemoryEnabled': False, 'disableClaudeAiConnectors': True,
            'enabledPlugins': {'cc-plugin-agents-md@builtin': False, 'cc-plugin-plugin-authoring@builtin': False}}
ENV_NAMES = frozenset({'HOME','PATH','LANG','LC_ALL','LC_CTYPE','USER','LOGNAME','SHELL','__CF_USER_TEXT_ENCODING'})
FORBIDDEN_ENV = frozenset({'ANTHROPIC_API_KEY','ANTHROPIC_AUTH_TOKEN','ANTHROPIC_BASE_URL','CLAUDE_CODE_OAUTH_TOKEN',
    'CLAUDE_CONFIG_DIR','ANTHROPIC_PROFILE','CLAUDE_CODE_USE_BEDROCK','CLAUDE_CODE_USE_VERTEX','CLAUDE_CODE_USE_FOUNDRY'})
need = require
wire = canonical

def now():
    return datetime.now(timezone.utc).isoformat()

def empty_heartbeat(value, session):
    if not isinstance(value, dict) or value.get('type') != 'keep_alive':
        return False
    if not set(value) <= {'type','session_id','uuid'} or ('session_id' in value and value['session_id'] != session):
        return False
    if 'uuid' in value:
        try:
            return str(uuid.UUID(value['uuid'])) == value['uuid']
        except (ValueError, TypeError, AttributeError):
            return False
    return True

def frame_metadata(raw, session, source, sequence):
    import re
    result = {'source':source,'sequence':sequence,'bytes':len(raw),'sha256':digest(raw)}
    try:
        value = json.loads(raw, object_pairs_hook=reject_duplicate_keys)
    except (ValueError, UnicodeError, HostRefusal):
        result['json_valid'] = False
        return result, None
    result['json_valid'], result['object'] = True, isinstance(value, dict)
    if isinstance(value, dict):
        for key in ('type','subtype','kind'):
            item = value.get(key)
            result[key] = item if isinstance(item,str) and re.fullmatch(r'[a-z][a-z0-9_]{0,47}',item) else None
        result['session_present'] = 'session_id' in value
        result['session_match'] = value.get('session_id') == session if 'session_id' in value else None
    return result, value


class ClaudeCodeAdapter:
    def validate(self):
        need(digest(canonical(self.spec)) == self.spec_sha256, 'adapter-config-drift')
        spec = self.spec
        need(spec['version'] == 1 and spec['model'] == MODEL and spec['effort'] == 'medium' and
             spec['cli_version'] == '2.1.310' and spec['inputs'].get(spec['cli']) == CLI_SHA256, 'pinned-runtime-drift')
        need(spec['inline_settings'] == SETTINGS and frozenset(spec['inherited_environment_allowlist']) == ENV_NAMES
             and frozenset(spec['forbidden_environment_names']) == FORBIDDEN_ENV, 'native-profile-drift')
        need(spec['native_trust_approved'] is True and spec['auth'] ==
             {'loggedIn': True, 'authMethod': 'claude.ai', 'apiProvider': 'firstParty', 'subscriptionType': 'pro'}, 'native-trust-auth-not-admitted')
        for path, expected in spec['inputs'].items():
            p = Path(path)
            need(p.is_absolute() and p.resolve(strict=True) == p and digest(p.read_bytes()) == expected, 'fixed-input-drift')
        for name in ('cli','python','relay'):
            need(spec[name] in spec['inputs'], 'unbound-native-executable')
        for path in spec['absent_policy_paths']:
            need(not Path(path).exists() and not Path(path).is_symlink(), 'managed-policy-appeared')
        for key in FORBIDDEN_ENV:
            need(not os.environ.get(key), 'auth-provider-override')
        need(time.time_ns() // 1_000_000 < spec['stop_at_ms'] and self.os.monotonic() < self.deadline, 'adapter-stop-deadline')
        self.g.check_core()

    def environment(self):
        value = {k:os.environ[k] for k in ENV_NAMES if k in os.environ}
        value.update(TMPDIR=self.spec['scratch'], CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC='1',
                     DISABLE_AUTOUPDATER='1', DISABLE_TELEMETRY='1', DISABLE_ERROR_REPORTING='1')
        return value

    def persist(self):
        partial, final = self.run / 'native-state.partial', self.run / 'native-state.json'
        self.os.replace_checkpoint(partial, final, self.record, durable_private)


    def reserve(self, kind, value):
        self.g.reserve_runtime(kind, value)
        # The caller may mirror reservations to the already-approved parent
        # allocation. Any failure stops before launch, Host input or dispatch.
        self.reservation_checkpoint(kind, value)

    def __init__(self, spec, spec_sha256, host, reservation_checkpoint, *, dispatch_transform=None):
        self.os = execution_os(need, purpose='claude-native')
        self.spec = json.loads(json.dumps(spec))
        self.spec_sha256, self.g = spec_sha256, host
        self.reservation_checkpoint = reservation_checkpoint
        self.dispatch_transform = dispatch_transform
        self.deadline = min(host.deadline - 20, self.os.monotonic() + 1780,
            self.os.monotonic() + (spec['stop_at_ms'] - time.time_ns() // 1_000_000) / 1000 - 20)
        self.validate()
        self.run = Path(spec['run'])
        need(self.run.is_absolute() and self.run.resolve() == self.run, 'adapter-run-alias')
        self.os.private_directory(self.run)
        durable_private(self.run / 'launch-spec.json', self.spec)
        self.session, self.nonce = spec['session'], spec['nonce']
        need(str(uuid.UUID(self.session)) == self.session and isinstance(self.nonce,str) and len(self.nonce) >= 32, 'native-identity')
        self.record = {'session_id':self.session,'started_at':now(),'safe_events':[],'relay_events':[],
                       'steps':[],'owned_processes':{},'stderr_bytes':0,'spec_sha256':spec_sha256}
        self.p, self.up, self.down = None, None, None
        self.rows, self.known, self.buffers, self.responses = {}, {}, {}, {}
        self.assistant_calls, self.awaiting = [], []
        self.current, self.last_scan = None, 0
        self.init_ok, self.actual_model, self.completed, self.closed = False, False, False, False
        self.stderr_hash = hashlib.sha256()
        self.sel, self.up, self.down = self.os.relay_channels(self.run)
        try:
            config = {'mcpServers':{'colvia':{'type':'stdio','command':spec['python'],
                'args':['-I','-S','-B',spec['relay'],str(self.run/'up.fifo'),str(self.run/'down.fifo'),self.nonce]}}}
            argv = [spec['cli'],'--print','--model',MODEL,'--effort','medium','--settings',json.dumps(SETTINGS,separators=(',',':')),
                '--tools','','--disable-slash-commands','--strict-mcp-config','--mcp-config',json.dumps(config,separators=(',',':')),
                '--setting-sources=','--permission-mode','dontAsk','--permission-prompts','none','--allowedTools',
                'mcp__colvia__u2_read_file,mcp__colvia__u2_verify','--input-format','stream-json','--output-format','stream-json',
                '--verbose','--no-session-persistence','--no-chrome','--session-id',self.session,'--system-prompt',spec['system_prompt'],'--max-turns','2']
            self.record['argv'], self.record['environment_names'] = argv, sorted(self.environment())
            self.persist()
            self.reserve('native-start', {'session':self.session,'spec_sha256':spec_sha256,'argv_sha256':digest(canonical(argv))})
            self.p = self.os.launch(argv, self.run, self.environment())
            self.record['pid'] = self.p.pid
            self.persist()
            self.os.watch_native(self.sel, self.p, self.up)
            self.scan()
            init = self.control('initialize', {'subtype':'initialize','hooks':None,'skills':[]}, 120)
            need(init.get('output_style') == 'default' and init.get('commands') == [], 'native-customization')
            agents = init.get('agents')
            need(isinstance(agents,list), 'agent-inventory-unavailable')
            names = [a.get('name') if isinstance(a,dict) else a for a in agents]
            need(all(isinstance(n,str) and n in ('Explore','Plan','general-purpose','claude','statusline-setup','claude-code-guide') for n in names), 'unexpected-custom-agents')
            self.record['initialize_summary'] = {'output_style':init.get('output_style'),'commands':[],'agent_names':names}
            connected = False
            for index in range(3):
                status = self.control('mcp-'+str(index), {'subtype':'mcp_status'}, 30)
                servers = status.get('mcpServers')
                if isinstance(servers,list) and len(servers)==1 and servers[0].get('name')=='colvia' and servers[0].get('status')=='connected':
                    inventory = servers[0].get('tools')
                    need(isinstance(inventory,list) and sorted(t.get('name') for t in inventory)==['u2_read_file','u2_verify'], 'MCP-schema-names')
                    self.record['mcp_connected'] = True
                    connected = True
                    break
                end = self.os.monotonic()+5
                while self.os.monotonic()<end:
                    self.pump(end)
            need(connected, 'MCP-not-connected')
            self.persist()
        except BaseException:
            self.close()
            raise

    def scan(self):
        self.rows = self.os.observe_owned(self.p, self.known)
        self.last_scan = self.os.monotonic()
        self.record['owned_processes'] = {str(k): v for k, v in self.known.items()}

    def process_snapshot(self):
        self.scan()
        return self.rows


    def send(self,value):
        raw=wire(value);need(len(raw)<=2097152 and self.os.monotonic()<self.deadline,'native-send-bound')
        self.os.send_process(self.p, raw)

    def control(self,ident,body,seconds):
        need(ident not in self.responses,'control-id-reuse');self.send({'type':'control_request','request_id':ident,'request':body});end=min(self.deadline,self.os.monotonic()+seconds)
        while ident not in self.responses:need(self.os.monotonic()<end,'control-timeout');self.pump(end)
        response=self.responses.pop(ident);need(response.get('subtype')=='success','control-refused');return response.get('response',{})

    def event(self,source,value):
        if source=='relay':
            need(value.pop('nonce',None)==self.nonce,'relay-nonce');self.record['relay_events'].append(value)
            if value.get('kind')=='tool-request':
                self.reserve('bridge-request',{'session':self.session,'request_id':value.get('request_id')});need(self.current is not None,'tool-outside-step');self.awaiting.append(value);need(len(self.awaiting)==1,'concurrent-native-requests')
            self.persist();return
        kind=value.get('type');sub=value.get('subtype')
        if kind=='control_response':self.responses[value.get('response',{}).get('request_id')]=value['response'];return
        if kind=='control_request':
            self.send({'type':'control_response','response':{'subtype':'error','request_id':value.get('request_id'),'error':'Host denies unexpected control effects'}});raise HostRefusal('unexpected-control-request')
        if kind=='system' and sub=='init':
            safe={k:value.get(k) for k in ['type','subtype','session_id','model','tools','mcp_servers','skills','plugins','slash_commands','permissionMode','apiKeySource']};self.record['safe_events'].append(safe);self.persist()
            need(value.get('session_id')==self.session and value.get('model')==MODEL,'native-init-model-session')
            need(sorted(value.get('tools',[]))==['mcp__colvia__u2_read_file','mcp__colvia__u2_verify'],'native-tool-inventory')
            need(value.get('skills')==[] and value.get('plugins')==[] and value.get('slash_commands')==[],'ambient-customization-inventory')
            need(value.get('permissionMode')=='dontAsk','native-permission-mode');self.init_ok=True
        elif kind=='command_lifecycle':
            need(set(value)=={'type','command_uuid','state','uuid','session_id'},'lifecycle-envelope')
            need(value.get('session_id')==self.session,'lifecycle-session')
            need(isinstance(value.get('uuid'),str) and str(uuid.UUID(value['uuid']))==value['uuid'],'lifecycle-event-id')
            matches=[step for step in self.record['steps'] if step['host_message_uuid']==value.get('command_uuid')]
            need(len(matches)==1,'lifecycle-unknown-command')
            state=value.get('state');need(state in ('queued','started','completed','cancelled','discarded','refused'),'lifecycle-unknown-state')
            matches[0].setdefault('command_lifecycle',[]).append({'state':state,'event_uuid':value['uuid'],'at':now()});self.persist()
            need(state in ('queued','started','completed'),'lifecycle-terminal-failure')
            # A lifecycle completion never completes a Host step or authorizes an effect.
        elif kind=='keep_alive':
            need(empty_heartbeat(value,self.session),'nonempty-or-wrong-session-heartbeat');self.record['empty_heartbeats']=self.record.get('empty_heartbeats',0)+1
        elif kind=='assistant':
            need(self.current is not None and value.get('session_id')==self.session and value.get('parent_tool_use_id') is None,'assistant-session')
            msg=value.get('message',{});need(msg.get('model')==MODEL,'actual-model-mismatch');self.actual_model=True
            self.current['actual_model']=msg['model'];self.current.setdefault('assistant_messages',[]).append({'message_id':msg.get('id'),'model':msg.get('model'),'content':msg.get('content'),'usage':msg.get('usage')});self.persist()
            for block in msg.get('content',[]):
                if block.get('type')=='tool_use':
                    need(block.get('name') in ('mcp__colvia__u2_read_file','mcp__colvia__u2_verify'),'assistant-tool-outside-inventory')
                    self.assistant_calls.append({'call_id':block['id'],'tool':block['name'].removeprefix('mcp__colvia__'),'arguments':block['input'],'message_id':msg.get('id')})
        elif kind=='result':
            need(self.current is not None and value.get('session_id')==self.session,'result-session')
            self.current['native_result']={k:value.get(k) for k in ['subtype','is_error','result','num_turns','usage','modelUsage','errors','duration_ms'] if k in value};self.persist();need(value.get('subtype')=='success' and value.get('is_error') is False,'native-result-not-success');self.completed=True
        elif kind=='rate_limit_event':
            info=value.get('rate_limit_info',{});self.record['safe_events'].append({'type':kind,'status':info.get('status'),'rateLimitType':info.get('rateLimitType')});self.persist();need(value.get('session_id')==self.session and info.get('status')=='allowed','usage-warning-or-limit')
        elif kind=='user':
            # Native tool-result echoes are not new Host inputs or authority.
            need(value.get('session_id')==self.session and self.current is not None,'user-echo-session')
            self.current.setdefault('native_echo_types',[]).append([b.get('type') for b in value.get('message',{}).get('content',[]) if isinstance(b,dict)])
        elif kind=='system':
            self.record['safe_events'].append({'type':kind,'subtype':sub})
            need(sub in ('status','task_notification','task_started','task_progress','hook_started','hook_progress','hook_response','api_retry','compact_boundary','session_state_changed'),'unknown-system-event')
            need(sub not in ('task_started','task_notification','task_progress','hook_started','hook_progress','hook_response','compact_boundary'),'unexpected-task-hook-compaction')
        else:raise HostRefusal('unknown-native-message-type')
        self.persist()

    def pump(self,end):
        need(self.os.monotonic()<min(end,self.deadline),'process-or-step-deadline')
        if self.os.monotonic()-self.last_scan>.5:self.scan()
        for source, fd, chunk in self.os.ready_chunks(self.sel, max(0, min(.2, end-self.os.monotonic()))):
            if not chunk:
                if source=='stdout':raise HostRefusal('native-stdout-closed')
                continue
            if source=='stderr':self.record['stderr_bytes']+=len(chunk);self.stderr_hash.update(chunk);need(self.record['stderr_bytes']<1048576,'stderr-bound');continue
            self.buffers[fd]=self.buffers.get(fd,b'')+chunk;need(len(self.buffers[fd])<2097152,'native-frame-bound')
            while b'\n' in self.buffers[fd]:
                line,self.buffers[fd]=self.buffers[fd].split(b'\n',1)
                if line.strip():
                    rows=self.record.setdefault('frame_metadata',[]);need(len(rows)<4096,'frame-count-bound');meta,value=frame_metadata(line,self.session,source,len(rows)+1);rows.append(meta);self.persist()
                    need(meta['json_valid'] and isinstance(value,dict),'invalid-native-frame');self.event(source,value)
        self.dispatch_ready();need(self.p.poll() is None,'native-exited-before-Host-stop')

    def close(self):
        if self.closed:
            return
        self.closed, failure = True, None
        try:
            self.g.stop()
        except BaseException as error:
            failure = error
        if self.p is not None:
            self.record['host_stop_started_while_cli_alive'] = self.p.poll() is None
            absent = self.os.stop_owned(self.p, self.known, self.process_snapshot)
            self.record['process_group_and_descendants_absent'] = absent
            self.record['exit_code'] = self.p.poll()
            for stream in (self.p.stdin, self.p.stdout, self.p.stderr):
                stream.close()
        else:
            absent = True
        self.os.close_channels(self.sel, self.up, self.down)
        self.record['finished_at'] = now()
        self.record['stderr_sha256'] = self.stderr_hash.hexdigest()
        try:
            self.persist()
            if self.session in self.g.starts:
                self.g.native_stopped(self.session, absent)
        except BaseException as error:
            if failure is None:
                failure = error
        need(absent, 'owned-process-remains')
        if failure is not None:
            raise failure


    def dispatch_ready(self):
        if not self.awaiting:return
        need(self.current is not None,'no-current-step')
        if not self.assistant_calls:return
        need(self.init_ok and self.actual_model,'effect-before-admission')
        req=self.awaiting.pop(0);call=self.assistant_calls.pop(0)
        need(req['name']==call['tool'] and req['arguments']==call['arguments'],'MCP-assistant-call-binding')
        need(not self.current.get('dispatch'),'second-dispatch-same-step')
        original={'session':self.session,'step':self.current['id'],'call_id':call['call_id'],'tool':call['tool'],
                                                'arguments':call['arguments'],'identity':self.g.cfg['identity']}
        mapped=json.loads(json.dumps(original))
        if self.dispatch_transform is not None:mapped=self.dispatch_transform(self.current['id'],mapped)
        self.current['dispatch']={'relay_request_id':req['request_id'],'original':original,'mapped':mapped,'mapping_at':now(),
                        'assistant_message_id':call['message_id'],'fault_source':'fixed-host-injection' if original!=mapped else None}
        self.persist()
        result=self.g.dispatch(mapped)
        self.current['dispatch']['outcome']=result;self.persist()
        reply={'content':[{'type':'text','text':json.dumps(result,ensure_ascii=False,separators=(',',':'))}],'isError':not result['ok']}
        raw=wire({'nonce':self.nonce,'request_id':req['request_id'],'result':reply})
        need(len(raw)<=65536,'relay-result-bound');self.os.send_relay(self.down,raw)

    def step(self,step_id):
        self.validate();need(not self.awaiting and not self.assistant_calls and self.current is None,'pending-native-request')
        matches=[s for s in self.spec['steps'] if s['id']==step_id]
        need(len(matches)==1 and len(self.record['steps'])<2,'unapproved-host-step')
        step=matches[0];prompt=step['input'];need(digest(prompt.encode())==step['sha256'],'host-input-drift')
        need(str(uuid.UUID(step['uuid']))==step['uuid'],'host-input-uuid')
        self.completed=False;self.actual_model=False
        self.current={'id':step_id,'input':prompt,'input_sha256':step['sha256'],'started_at':now(),'host_message_uuid':step['uuid']}
        self.record['steps'].append(self.current);self.g.open_step(self.session,step_id)
        self.reserve('host-input',{'session':self.session,'step':step_id,'input_sha256':step['sha256'],'uuid':step['uuid']})
        self.persist()
        self.send({'type':'user','session_id':self.session,'uuid':step['uuid'],'parent_tool_use_id':None,'message':{'role':'user','content':prompt}})
        end=min(self.deadline,self.os.monotonic()+880)
        while not self.completed:self.pump(end)
        need(self.current.get('dispatch') is not None and not self.awaiting and not self.assistant_calls,'missing-or-pending-dispatch')
        self.current['finished_at']=now();self.persist();result=self.current;self.current=None;return result
