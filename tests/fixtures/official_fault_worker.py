"""Fixed synthetic pipe failures; used only instead of a worker in fault tests."""
import json
import sys
json.loads(sys.stdin.buffer.read())
mode=sys.argv[1]
if mode=='stderr':
    print('WORKER_STDERR_SECRET_MARKER',file=sys.stderr,flush=True)
    print(json.dumps({'ok':False,'error':'WORKER_RESPONSE_SECRET_MARKER'}),flush=True)
elif mode=='nonzero':raise SystemExit(17)
elif mode=='false':print(json.dumps({'ok':False,'error':'WORKER_RESPONSE_SECRET_MARKER'}),flush=True)
elif mode=='lost':pass
else:raise ValueError('unsupported fixed fixture mode')
