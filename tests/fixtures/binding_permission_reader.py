"""Closed read-only typed-record observation using one exact retained runtime."""
import json
import sys
from pathlib import Path

if len(sys.argv) != 4 or sys.argv[3] != 'typed-records':
    raise RuntimeError('SOURCE TARGET typed-records required')
source, target = map(Path, sys.argv[1:3])
if not source.is_absolute() or not target.is_absolute():
    raise RuntimeError('literal absolute paths required')
sys.path.insert(0, str(source / 'src'))
from hv2ref.product import verify_workspace_product
from hv2ref.work import read_work
from hv2ref.intent import workspace_intents
from hv2ref.candidates import read_candidates

state = verify_workspace_product(target)
if state['inventory']['inventory_id'] != 'entry-1':
    raise RuntimeError('entry-1 required')
works = {name: read_work(target, name) for name in ('bp-local', 'bp-parent', 'bp-worker')}
intents = workspace_intents(target)
candidates = read_candidates(target)
for name, module in tuple(sys.modules.items()):
    if name == 'hv2ref' or name.startswith('hv2ref.'):
        if not Path(module.__file__).is_relative_to(source / 'src'):
            raise RuntimeError('mixed reader runtime')
# Typed objects are resolved by the real reader. Product binding changes are
# deliberately reported separately from the stable record graph comparison.
print(json.dumps({'records': {'works': works, 'intents': intents, 'planning': candidates},
                  'binding_ref': state['binding_ref'],
                  'runtime_source': str(source)}, sort_keys=True))
