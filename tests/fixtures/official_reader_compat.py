"""Explicit offline cross-version reader fixture; no runtime/provider invocation."""
from pathlib import Path
import json,sys
from unittest import mock
source,target,action=Path(sys.argv[1]),Path(sys.argv[2]),sys.argv[3]
sys.path.insert(0,str(source/'src'))
from hv2ref import product,official_entry as entry,official_host as host,official_state as state
value=json.loads(sys.stdin.buffer.read())
if action in ('prepare','closed'):
    runtime=product.verify_workspace_product(target);runtime['inventory_id']=runtime['inventory']['inventory_id']
    with mock.patch.object(product,'require_workspace_runtime',return_value=runtime),mock.patch.object(entry,'runtime_input',return_value={}):
        result=entry.prepare(target,value['request'])
        if action=='closed':
            h=host.Host(result['spec'],result['confirm_token'])
            try:h.revoke('cancelled');h.finish('revoked-before-launch');result={'grant':h.grant}
            finally:h.close()
elif action=='status':result=state.public_status(state.read_capsule(target,value['grant']))
elif action=='resolve-preview':result=state.resolution_preview(target,value['grant'])
elif action=='restore':result=host.Host.restore_closed(target,value['grant']).status()
else:raise ValueError('unsupported fixed reader action')
print(json.dumps(result))
