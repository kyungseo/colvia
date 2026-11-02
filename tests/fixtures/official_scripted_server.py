"""Offline stdio fixture; drives the real adapter, never contacts a provider."""
from pathlib import Path
import json
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'src'))
from hv2ref.official_admission import DISABLED_FEATURES, MODEL, PROFILE

scenario = json.loads(Path(sys.argv[1]).read_text())
thread = scenario.get('thread', 'SCRIPT_THREAD_MARKER')
turn = scenario.get('turn', 'SCRIPT_TURN_MARKER')
call_prefix = scenario.get('call', 'SCRIPT_CALL_MARKER')
step = 0
expected = None


def send(value):
    print(json.dumps(value), flush=True)


def callback():
    global step
    step += 1
    if step == 1:
        tool, args = 'u2_read_file', {'file_ids': ['Editable', 'Reference']}
    elif step == 2:
        tool, args = 'u2_write_file', {'file_id': 'Editable', 'expected_sha256': expected, 'content': scenario['content']}
    else:
        tool, args = 'u2_verify', {'verifier_id': ('DOC-LINKS', 'DOC-GFM', 'DOC-CLAIMS')[step - 3]}
    envelope = {'threadId': thread, 'turnId': turn, 'callId': call_prefix + str(step), 'tool': tool, 'arguments': args}
    if scenario.get('mode') == 'wrong-caller': envelope['threadId'] = 'REFUSED_CALLER_MARKER'
    send({'id': 'CALLBACK_ENVELOPE_MARKER' + str(step), 'method': 'item/tool/call', 'params': envelope})


for line in sys.stdin:
    value = json.loads(line)
    method = value.get('method')
    if method == 'initialized': continue
    if method is not None:
        if scenario.get('mode') == 'rpc-error' and method == 'model/list':
            send({'id': value['id'], 'error': {'code': -1, 'message': 'RPC_ERROR_MARKER'}}); continue
        if method == 'initialize':
            result = {'platformFamily': 'fixture', 'platformOs': 'offline'}
        elif method == 'config/read':
            result = {'config': {'features': {**dict.fromkeys(DISABLED_FEATURES, False), 'code_mode_host': True, 'skip_host_skill_discovery': True},
                'web_search': 'disabled', 'project_doc_max_bytes': 0, 'notify': [], 'default_permissions': PROFILE, 'model_provider': 'openai', 'mcp_servers': {}}}
        elif method == 'account/read': result = {'account': {'type': 'chatgpt'}}
        elif method == 'model/list': result = {'data': [{'model': MODEL, 'supportedReasoningEfforts': [{'reasoningEffort': 'low'}]}]}
        elif method == 'thread/start': result = {'model': MODEL, 'thread': {'id': thread}}
        elif method == 'turn/start': result = {'turn': {'id': turn}}
        elif method == 'turn/interrupt': result = {}
        else: raise ValueError('unexpected fixture method')
        send({'id': value['id'], 'result': result})
        if method == 'turn/start':
            if scenario.get('mode') == 'stderr': print('RUNTIME_STDERR_MARKER', file=sys.stderr, flush=True)
            else: callback()
        elif method == 'turn/interrupt':
            send({'method': 'turn/completed', 'params': {'turn': {'id': turn, 'status': 'interrupted'}}})
    elif 'result' in value:
        reply = value['result']
        if not reply['success']: continue
        result = json.loads(reply['contentItems'][0]['text'])
        if step == 1: expected = result['files'][0]['file_sha256']
        if step < 5: callback()
        else: send({'method': 'turn/completed', 'params': {'turn': {'id': turn, 'status': 'completed'}}})
