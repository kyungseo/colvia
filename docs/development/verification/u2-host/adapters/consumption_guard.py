"""Cross-kind consumption guard, called while the existing task lock is held."""
from ..contracts import require
from . import fresh_codex_contract as fresh
from . import edit_codex_contract as edit

KINDS = {'v58-consumed': fresh.ALLOCATION, 'edit-consumed': edit.ALLOCATION}
PARENTS = {'v58-parent-reservation', 'edit-parent-reservation'}
IDENTIFIERS = ('reservation_id', 'activation_sha256', 'run_directory', 'snapshot_sha256')


def check_consumption(rows, anchor, activation, snapshot):
    proposed = {'reservation_id': activation['reservation_id'], 'activation_sha256': anchor['activation']['sha256'],
                'run_directory': anchor['run_directory'], 'snapshot_sha256': anchor['accounting_snapshot']['sha256']}
    for row in rows:
        kind, value = row['kind'], row['value']
        require(type(kind) is str and type(value) is dict, 'consumption-record-shape')
        if kind in PARENTS:
            fresh.exact(value, ('reservation_id', 'snapshot_sha256', 'allocation', 'owner_message_id',
                                'parent', 'counts_before', 'limits'), 'consumption-parent-fields')
            allocation = KINDS[kind.replace('parent-reservation', 'consumed')]
            require(fresh.text(value['reservation_id']) and fresh.text(value['owner_message_id'])
                    and fresh.sha(value['snapshot_sha256']) and value['allocation'] == allocation
                    and value['parent'] == ('C-Codex-live' if kind == 'v58-parent-reservation' else edit.KIND),
                    'consumption-parent-identity')
            before, limits = value['counts_before'], value['limits']
            require(type(before) is dict and type(limits) is dict and set(before) == set(limits)
                    and set(allocation) <= set(before) and all(fresh.number(v) and fresh.number(limits[k])
                    and v + allocation.get(k, 0) <= limits[k] for k, v in before.items()), 'consumption-parent-counts')
            continue
        if kind not in KINDS:
            require(not kind.startswith(('v58-', 'edit-')) and not (set(IDENTIFIERS) & set(value)),
                    'consumption-unknown-related-record')
            continue
        fresh.exact(value, ('version', 'activation_sha256', 'reservation_id', 'run_directory', 'allocation',
                           'snapshot_sha256', 'ledger_row_sha256', 'counts_before', 'counts_after'), 'consumption-fields')
        require(type(value['version']) is int and value['version'] == 1 and value['allocation'] == KINDS[kind]
                and fresh.text(value['reservation_id']) and edit.path(value['run_directory'])
                and all(fresh.sha(value[k]) for k in ('activation_sha256', 'snapshot_sha256', 'ledger_row_sha256')),
                'consumption-identity')
        before, after = value['counts_before'], value['counts_after']
        require(type(before) is dict and type(after) is dict and set(before) == set(after)
                and set(KINDS[kind]) <= set(before), 'consumption-count-fields')
        for key, used in before.items():
            require(fresh.number(used) and fresh.number(after[key]) and after[key] == used + KINDS[kind].get(key, 0),
                    'consumption-count-drift')
        require(not any(value[k] == proposed[k] for k in IDENTIFIERS), 'consumption-replay')
        require(value['reservation_id'] in snapshot['consumed_reservations'] and set(after) <= set(snapshot['counts'])
                and all(snapshot['counts'][key] >= used for key, used in after.items()), 'consumption-stale-snapshot')
