"""Fixed offline transition child: real SIGKILL after durable schema8 receipt."""
from pathlib import Path
import json, os, signal, sys
source, target = map(Path, sys.argv[1:])
sys.path.insert(0, str(source / 'src'))
from hv2ref import product
request = json.load(sys.stdin)
original = product._entry_write_exact
receipt = target / '.hrn/product/receipts' / (request['request']['operation_id'] + '.json')
def observed(home, path, data, *, role):
    result = original(home, path, data, role=role)
    if path == receipt:
        if json.loads(path.read_bytes())['schema_version'] != 8:
            raise RuntimeError('unexpected fixed transition receipt')
        os.kill(os.getpid(), signal.SIGKILL)
    return result
product._entry_write_exact = observed
product.workspace_switch_apply(target, request['request'], confirm_token=request['confirm_token'], source=source)
raise RuntimeError('fixed kill point was not reached')
