"""Fixed two-tool MCP relay; only the parent Host can dispatch an effect.

Standalone stdlib entry for Python -I -S -B. It has no Core/worker credentials,
no authority writer and no backend selection. The parent pins these bytes.
"""
import json
import os
import stat
import sys

TOOLS = [
    {'name': 'u2_read_file', 'description': '승인된 파일 ID의 원문을 읽습니다.', 'inputSchema': {
        'type': 'object', 'properties': {'file_ids': {'type': 'array', 'items': {'type': 'string'},
        'minItems': 1, 'maxItems': 8, 'uniqueItems': True}}, 'required': ['file_ids'], 'additionalProperties': False}},
    {'name': 'u2_verify', 'description': '고정 문서 검증기 한 개를 실행합니다.', 'inputSchema': {
        'type': 'object', 'properties': {'verifier_id': {'enum': ['DOC-LINKS', 'DOC-GFM', 'DOC-CLAIMS']}},
        'required': ['verifier_id'], 'additionalProperties': False}},
]


def need(condition, reason):
    if not condition:
        raise RuntimeError(reason)


def unique(pairs):
    result = {}
    for key, value in pairs:
        need(key not in result, 'duplicate JSON key')
        result[key] = value
    return result


def wire(value):
    return (json.dumps(value, separators=(',', ':'), allow_nan=False) + '\n').encode()


def write_all(fd, raw):
    view = memoryview(raw)
    while view:
        written = os.write(fd, view)
        need(written > 0, 'channel short write')
        view = view[written:]


def main(argv):
    need(len(argv) == 3, 'relay arguments')
    up, down, nonce = argv
    need(len(nonce) >= 32, 'relay nonce')
    for name in (up, down):
        info = os.lstat(name)
        need(stat.S_ISFIFO(info.st_mode) and stat.S_IMODE(info.st_mode) == 0o600
             and info.st_nlink == 1 and info.st_uid == os.getuid(), 'private FIFO required')
    to_host = os.open(up, os.O_WRONLY | os.O_NOFOLLOW)
    from_host = None
    try:
        from_host = os.open(down, os.O_RDONLY | os.O_NOFOLLOW)
        def tell(kind, **fields):
            raw = wire({'nonce': nonce, 'pid': os.getpid(), 'kind': kind, **fields})
            need(len(raw) <= 65536, 'relay frame limit')
            write_all(to_host, raw)
        def reply(ident, result):
            sys.stdout.buffer.write(wire({'jsonrpc': '2.0', 'id': ident, 'result': result}))
            sys.stdout.buffer.flush()
        tell('started')
        while True:
            raw = sys.stdin.buffer.readline(65537)
            if not raw:
                break
            need(len(raw) <= 65536 and raw.endswith(b'\n'), 'MCP frame limit')
            msg = json.loads(raw, object_pairs_hook=unique)
            need(isinstance(msg, dict) and msg.get('jsonrpc') == '2.0', 'MCP message')
            method, ident = msg.get('method'), msg.get('id')
            if method == 'initialize':
                tell('initialize')
                reply(ident, {'protocolVersion': msg['params']['protocolVersion'],
                    'capabilities': {'tools': {'listChanged': False}}, 'serverInfo': {'name': 'colvia-fixed-read', 'version': '1'}})
            elif method == 'notifications/initialized':
                tell('initialized')
            elif method == 'ping':
                reply(ident, {})
            elif method == 'tools/list':
                tell('tools-list', names=[t['name'] for t in TOOLS])
                reply(ident, {'tools': TOOLS})
            elif method == 'tools/call':
                params = msg.get('params', {})
                need(isinstance(params, dict), 'MCP call params')
                tell('tool-request', request_id=ident, name=params.get('name'), arguments=params.get('arguments'))
                data = b''
                while b'\n' not in data:
                    part = os.read(from_host, 4096)
                    need(part, 'Host channel closed')
                    data += part
                    need(len(data) <= 65536, 'Host frame limit')
                need(data.count(b'\n') == 1 and data.endswith(b'\n'), 'Host extra frame')
                response = json.loads(data, object_pairs_hook=unique)
                need(response.get('nonce') == nonce and response.get('request_id') == ident, 'Host response identity')
                reply(ident, response['result'])
            elif method in ('resources/list', 'prompts/list'):
                reply(ident, {'resources': []} if method == 'resources/list' else {'prompts': []})
            elif ident is not None:
                sys.stdout.buffer.write(wire({'jsonrpc': '2.0', 'id': ident,
                    'error': {'code': -32601, 'message': 'Unsupported fixed relay method'}}))
                sys.stdout.buffer.flush()
    finally:
        os.close(to_host)
        if from_host is not None:
            os.close(from_host)


if __name__ == '__main__':
    main(sys.argv[1:])
