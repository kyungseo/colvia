"""Local synthetic RPC fixture only. No network, credentials, provider, or native agent."""
import fcntl
import hashlib
import json
import os
from pathlib import Path
import select
import signal
import sys

cfg = json.loads(Path(sys.argv[1]).read_text())
out = Path(cfg['evidence'])
seen = []
buffer = b''
refusal_wait = False
refusal_bytes = 0
plan_no = 0
thread = cfg['start'] + '-thread'

def wire(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':')).encode()

def record():
    value = {'messages':seen, 'refusal_bytes':refusal_bytes, 'refusal_wait':refusal_wait}
    with out.open('w') as stream:
        json.dump(value, stream, sort_keys=True)
        stream.flush()
        os.fsync(stream.fileno())

def terminate(sig, frame):
    global refusal_bytes
    if refusal_wait:
        while select.select([0], [], [], 0)[0]:
            raw = os.read(0, 65536)
            if not raw:
                break
            refusal_bytes += len(raw)
    record()
    raise SystemExit(0)

signal.signal(signal.SIGTERM, terminate)

def event(kind, subject):
    with open(cfg['journal_lock'], 'r+') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        rows = [json.loads(line) for line in Path(cfg['journal']).read_bytes().splitlines()]
        last = rows[-1]
        e = {'kind':kind,'subject':subject,'phase':'synthetic','start':cfg['start'],
             'seq':len(rows),'prev':last['sha256'],'approval':cfg['approval'],'work':cfg['work'],
             'candidate':cfg['candidate'],'at_ms':cfg['now_ms']}
        row = {'event':e,'sha256':hashlib.sha256(wire(e)).hexdigest()}
        with open(cfg['journal'], 'ab', buffering=0) as f:
            f.write(wire(row)+b'\n')
            os.fsync(f.fileno())

def send(value):
    os.write(1, wire(value)+b'\n')

def result(message, value):
    send({'id':message['id'],'result':value})

while True:
    if b'\n' not in buffer:
        raw = os.read(0, 65536)
        if not raw:
            record()
            break
        if refusal_wait:
            refusal_bytes += len(raw)
        buffer += raw
        continue
    line, buffer = buffer.split(b'\n', 1)
    message = json.loads(line)
    method = message.get('method')
    seen.append(method or ('result' if 'result' in message else 'error'))
    record()
    if method == 'initialize':
        event('runtime-entered', {'start':cfg['start']})
        classification = cfg.get('policy_classification', 'applied')
        if classification != 'known-not-applicable':
            event('control', {'endpoint':'policy'})
        event('policy-admission', {'classification':classification})
        for ep in ('models','accounts'):
            event('control', {'endpoint':ep})
        result(message, {})
    elif method == 'initialized':
        pass
    elif method == 'account/read':
        result(message, {'account':{'type':'chatgpt','email':None,'planType':'pro'},
                         'requiresOpenaiAuth':True,'workspaceRouting':{'chatgptAccountId':'synthetic',
                         'backendOrigin':'https://chatgpt.com','accountRoutingOverride':'NO_CONSTRAINT'}})
    elif method == 'thread/start':
        event('thread', {'request':message['id']})
        result(message, {'thread':{'id':thread,'ephemeral':True},'model':'gpt-6-astra',
                         'modelProvider':'openai','reasoningEffort':'xhigh','approvalPolicy':'never'})
    elif method == 'turn/prepare':
        plan_no += 1
        plan = cfg['start']+'-plan-'+str(plan_no)
        turn = cfg['start']+'-turn-'+str(plan_no)
        call = cfg['start']+'-call-'+str(plan_no)
        inputs = message['params']['input']
        core_input = [{'type':'text','text':v['text'],'text_elements':[]} for v in inputs]
        manifest = {'version':1,'planId':plan,'sourceIdentity':cfg['source_identity'],
                    'buildIdentity':'sha256:'+cfg['candidate'],
                    'snapshot':{'initial_input':core_input,'history_binding':{
                        'input_template':cfg['input_template_identity'],
                        'input_sha256':hashlib.sha256(wire(core_input)).hexdigest(),'count':0,'sha256':'a'*64},
                        'context':{'model':{'slug':'gpt-6-astra'},'reasoning_effort':'xhigh',
                          'wire_profile':{'api':'responses_http','include_internal':False,
                            'compression':'none','authentication':'native_read_only'},
                          'execution_binding':cfg['execution_binding']}},
                    'toolEnvelope':cfg['tool_envelope']}
        result(message, {'handle':'synthetic-handle-'+str(plan_no),'manifest':manifest})
    elif method == 'turn/startPrepared':
        subject = {'thread':thread,'turn':turn,'plan':plan}
        event('turn', {'thread':thread,'plan':plan})
        event('generation', {**subject,'generation':1})
        event('dispatch', {**subject,'call':call})
        result(message, {'turn':{'id':turn}})
        send({'method':'turn/started','params':{'threadId':thread,'turn':{'id':turn}}})
        refusal_wait = plan_no == 2
        send({'id':100+plan_no,'method':'item/tool/call','params':{
            'threadId':thread,'turnId':turn,'callId':call,'namespace':None,'tool':'u2_read_file',
            'arguments':{'file_ids':['Outside' if refusal_wait else 'Reference']}}})
    elif method == 'thread/read':
        result(message, {})
    elif 'result' in message:
        event('generation', {**subject,'generation':2})
        send({'method':'turn/completed','params':{'threadId':thread,
              'turn':{'id':turn,'status':'completed','error':None}}})
    else:
        raise RuntimeError('unplanned synthetic RPC')
