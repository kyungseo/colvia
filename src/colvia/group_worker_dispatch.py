"""Dispatch exactly two approved registered Work members and recover their results."""
from concurrent.futures import FIRST_COMPLETED, ThreadPoolExecutor, wait
from pathlib import Path
from uuid import uuid4

from .codec import RecordError, canonical_bytes, decode_canonical, decode_envelope, require
from .group_records import WINDOWS_GROUP_VERSION, digest, key as group_key, windows_path
from .maps import map_get
from .records import link, text
from .work import work_key
from .storage.files import platform_files
from .platforms.windows_group_workers import CodexExecFailure, verify_codex_diagnostics


RESULT_CHECK = "worker-result"
PROVIDERS = {"claude", "codex"}


def route(coordinator, assignments):
    require(coordinator in PROVIDERS and type(assignments) is dict and len(assignments)==2
            and set(assignments.values()) <= PROVIDERS and coordinator in assignments.values(),
            'group-worker-route-invalid')
    require(coordinator=='claude' or set(assignments.values())=={'codex'},'group-worker-route-invalid')
    return assignments


def dispatch_plan(grouped, name, coordinator, assignments, paths, journal_root):
    route(coordinator, assignments)
    require(set(paths)==set(assignments.values()),'group-worker-executable-set-invalid')
    current=grouped._selected(name)
    require(current.ref.kind=='group.plan' and current.ref.version==WINDOWS_GROUP_VERSION,
            'group-workers-require-windows-plan')
    view=grouped.view(name)
    require(view['head']==current.ref.sha256,'group-view-changed')
    require({member['work'] for member in view['members']}==set(assignments),'group-worker-members-changed')
    members=[]
    target=Path(view['destination_path']).resolve(strict=True)
    roots=[target]
    for item in view['members']:
        require(item['state']=='planned' and item['checks']==[RESULT_CHECK],
                'group-workers-require-one-worker-result-check')
        require(0<len(item['scope'])<=16,'group-worker-scope-unqualified')
        root=Path(item['source_path'])
        require(root==root.resolve(strict=True) and not any(root.is_relative_to(p) or p.is_relative_to(root) for p in roots),
                'group-worker-workspace-overlap')
        roots.append(root)
        grouped._source(item['workspace']).workspace.verify()
        for name_in_scope in item['scope']:
            windows_path(name_in_scope)
            require(all(part and all(c.isascii() and (c.isalnum() or c in '._-') for c in part)
                    for part in name_in_scope.split('/')),'group-worker-scope-unqualified')
            approved=root/name_in_scope
            require(approved==approved.resolve(strict=True) and approved.is_file()
                    and not approved.is_symlink() and approved.stat().st_nlink==1,'group-worker-scope-unqualified')
        members.append({key:item[key] for key in ('work','workspace','head','plan','scope','goal','source_path')})
        members[-1]['provider']=assignments[item['work']]
    journal=Path(journal_root)
    require(journal.is_absolute() and journal.resolve()==journal
            and not any(journal.is_relative_to(p) or p.is_relative_to(journal)
                         for p in [*roots,grouped.authority]),'group-worker-journal-overlap')
    plan=dict(group=name,destination=view['destination'],target=str(target),coordinator=coordinator,journal=str(journal),
              group_head=view['head'],group_receipt=view['receipt'],members=members,executables=paths)
    return plan | {'dispatch_receipt':digest(plan)}


class Dispatch:
    def __init__(self, grouped, name, journal_root, *, files=None):
        self.grouped=grouped
        self.name=name
        self.files=files or platform_files()
        self.journal=Path(journal_root)
        self.area=self.journal/('group-workers-'+digest({'project':grouped.store.project,'group':name})[:32])
        self.path=self.area/'dispatch.json'

    def _save(self, old, state):
        raw=canonical_bytes(state)
        self.files.replace(self.path,raw,old)
        return raw

    def _member(self, item):
        worker=self.grouped._source(item['workspace'])
        worker.workspace.verify()
        require(str(worker.workspace.root)==item['source_path'],'group-worker-registration-changed')
        return worker

    def _head(self):
        return self.grouped._selected(self.name).ref.sha256

    def _lock(self):
        self.files.private_directory(self.area)
        return self.files.empty_lock(self.area / 'dispatch.lock')

    @staticmethod
    def _operation(plan, suffix):
        return 'group-worker-'+digest(dict(dispatch=plan['dispatch_receipt'],stage=suffix))[:32]

    def _operation_heads(self, operation, key):
        store = self.grouped.store
        roots = store.operation_result(operation)
        if roots is None:
            return None
        return tuple(map_get(link(decode_envelope(ref, store.load(ref)), 'heads'), key, store.load)
                     for ref in roots)

    def _recorded_approval(self, plan):
        recorded = self._operation_heads(self._operation(plan, 'approve'), group_key(self.name))
        if recorded is None:
            return None
        before, after = recorded
        require(before is not None and before.sha256 == plan['group_head'] and after is not None
                and after.kind == 'group.approval'
                and link(self.grouped._object(after), 'plan') == before,
                'group-worker-approval-changed')
        return after.sha256

    def _reserve(self, plan):
        try:
            raw = self.files.read(self.path, 256 * 1024)
        except FileNotFoundError:
            work = {item['work']: dict(phase='reserved', session=str(uuid4())) for item in plan['members']}
            state = dict(plan=plan, work=work, group_approval=None)
            raw = canonical_bytes(state)
            self.files.create(self.path, raw)
        else:
            state = decode_canonical(raw)
            require(state['plan'] == plan and state['group_approval'] is None
                    and set(state['work']) == {item['work'] for item in plan['members']}
                    and all(lane['phase'] == 'reserved' for lane in state['work'].values()),
                    'group-worker-dispatch-already-reserved')
        return raw, state

    def run(self, plan, *, receipt, statement, native, first_dispatch_check=None):
        require(plan['group']==self.name and plan['journal']==str(self.journal)
                and receipt==plan['dispatch_receipt'],'group-worker-dispatch-stale')
        text(statement)
        try:
            self.files.create_directory(self.area)
        except FileExistsError:
            pass
        with self._lock():
            if first_dispatch_check is not None:
                # The reservation file is created under this lock before any approval or launch.
                # A lock directory can survive validation failure without a reservation.
                try:
                    self.files.read(self.path, 256 * 1024)
                except FileNotFoundError:
                    pass
                else:
                    raise RecordError('group-worker-dispatch-already-reserved')
                first_dispatch_check()
            require(self._head()==plan['group_head'],'group-worker-dispatch-stale')
            raw, state = self._reserve(plan)
            work = state['work']
            self.grouped.approve(operation=self._operation(plan,'approve'),group=self.name,
                                 receipt=plan['group_receipt'],statement=statement)
            state['group_approval'] = self._recorded_approval(plan)
            require(state['group_approval'] is not None, 'group-worker-approval-unconfirmed')
            raw=self._save(raw,state)
            for item in plan['members']:
                worker=self._member(item)
                key=item['work']
                approved,head=worker._head(key)
                require(head.payload['phase']=='approved' and link(head,'plan').as_dict()==item['plan'],
                        'group-worker-approval-changed')
                with worker.workspace.selected_reader(verify_path=True) as read:
                    before=read(item['scope'],worker.workspace.budget.read_bytes)
                require(len(before)==len(item['scope']) and all(e['kind']=='regular' for e in before),
                        'group-worker-scope-unqualified')
                worker.start(operation=self._operation(plan,'start-'+key),work=key,expected_approval_head=approved)
                active,_=worker._head(key)
                work[key].update(phase='active',head=active.as_dict(),before=list(before))
                raw=self._save(raw,state)
            require(self._head()==state['group_approval'],'group-worker-approval-changed')
            with ThreadPoolExecutor(max_workers=2) as pool:
                finished = False
                try:
                    futures = {pool.submit(native, item, work[item['work']]['session'], self.area): item
                               for item in plan['members']}
                    pending = set(futures)
                    while pending:
                        done, pending = wait(pending, timeout=.1, return_when=FIRST_COMPLETED)
                        for future in done:
                            item = futures[future]
                            self._worker_result(future, item, work)
                            raw = self._save(raw, state)
                    finished = True
                finally:
                    cancelled = getattr(native, 'cancelled', None)
                    if not finished and cancelled is not None:
                        cancelled.set()
            return self._collect(raw,state)

    def _worker_result(self, future, item, work):
        key = item['work']
        lane = work[key]
        try:
            evidence = future.result()
        except Exception as exc:
            lane.update(phase='stopped', reason=getattr(exc, 'code', 'group-worker-process-unavailable'),
                        error_type=type(exc).__name__)
            if item['provider'] == 'codex' and isinstance(exc, CodexExecFailure):
                lane['codex_diagnostics'] = exc.diagnostics
            return
        try:
            require(type(evidence) is dict and evidence.get('provider') == item['provider']
                    and evidence.get('job_closed') is True and evidence.get('exit') == 0
                    and type(evidence.get('identity')) is str and bool(evidence['identity'])
                    and all(x.get('evidence', {}).get('identity') != evidence['identity'] for x in work.values()),
                    'group-worker-result-identity-unverified')
            worker = self._member(item)
            current, _ = worker._head(key)
            require(current.as_dict() == lane['head'], 'group-worker-active-head-changed')
            with worker.workspace.selected_reader(verify_path=True) as read:
                observed = read(item['scope'], worker.workspace.budget.read_bytes)
            require(len(observed) == len(lane['before']) and all(e['kind'] == 'regular' for e in observed)
                    and observed != tuple(lane['before']), 'group-worker-result-unavailable')
            if item['provider'] == 'claude':
                prior = {entry['path']: entry for entry in lane['before']}
                changed = {entry['path'] for entry in observed if prior[entry['path']] != entry}
                writes = evidence.get('writes')
                require(type(writes) is list and all(type(path) is str for path in writes)
                        and changed <= set(writes) <= prior.keys(), 'group-worker-write-proof-mismatch')
            lane.update(phase='ready', observed=list(observed), evidence=evidence)
        except (OSError, ValueError) as exc:
            lane.update(phase='stopped', reason=getattr(exc, 'code', 'group-worker-process-unavailable'))

    def resume(self):
        with self._lock():
            raw=self.files.read(self.path,256*1024)
            state=decode_canonical(raw)
            plan = state['plan']
            require(plan['group'] == self.name and plan['journal'] == str(self.journal),
                    'group-worker-dispatch-stale')
            for item in plan['members']:
                lane = state['work'][item['work']]
                if 'codex_diagnostics' in lane:
                    require(item['provider'] == 'codex' and lane['phase'] == 'stopped',
                            'group-worker-codex-diagnostics-invalid')
                    verify_codex_diagnostics(lane['codex_diagnostics'])
            if state['group_approval'] is None:
                state['group_approval'] = self._recorded_approval(plan)
                if state['group_approval'] is None:
                    require(self._head() == plan['group_head'], 'group-worker-approval-changed')
                    return self._result(state)
            require(self._head() == state['group_approval'], 'group-worker-approval-changed')
            changed = canonical_bytes(state) != raw
            for lane in state['work'].values():
                if lane['phase'] in ('reserved','active'):
                    lane.update(phase='stopped',reason='group-worker-incomplete')
                    changed = True
            if changed:
                raw = self._save(raw, state)
            return self._collect(raw,state)

    def _collect(self, raw, state):
        plan=state['plan']
        require(state['group_approval'] is not None and self._head()==state['group_approval'],
                'group-worker-approval-changed')
        for item in plan['members']:
            key=item['work'];lane=state['work'][key]
            if lane['phase'] not in ('ready','publishing','submitted'):
                continue
            worker=self._member(item)
            op=self._operation(plan,'submit-'+key)
            if lane['phase']=='submitted':
                require(worker.review(key)['receipt']==lane['receipt'],'group-worker-submission-changed')
                continue
            refusal = 'group-worker-submit-unconfirmed'
            if lane['phase']=='ready':
                prior,_=worker._head(key)
                if prior.as_dict() != lane['head']:
                    lane.update(phase='stopped', reason='group-worker-active-head-changed')
                    raw = self._save(raw, state)
                    continue
                require(worker.store.operation_result(op) is None, 'group-worker-submission-changed')
                lane['phase']='publishing'
                raw=self._save(raw,state)
                try:
                    worker.submit(operation=op,work=key,summary='Exact recorded worker edit',
                                  checks=[dict(name=RESULT_CHECK,status='passed',
                                               detail='Owned process closed and the approved file delta was observed. '
                                                      'The required group integration check is separate.')],
                                  expected_active_head=prior,expected_scope=lane['observed'])
                except RecordError as exc:
                    refusal = exc.code
                except OSError:
                    # Reconcile through the recorded operation without submitting again.
                    pass
            published = self._operation_heads(op, work_key(key))
            if published is None:
                lane.update(phase='stopped', reason=refusal)
                raw=self._save(raw,state)
                continue
            before, after = published
            current, _ = worker._head(key)
            require(before is not None and before.as_dict() == lane['head'] and after == current,
                    'group-worker-submission-changed')
            shown=worker.review(key)
            require(shown['current_matches'],'group-worker-submission-changed')
            for e in lane['observed']:
                old=next(x for x in lane['before'] if x['path']==e['path'])
                if old==e:continue
                kept=worker.result_content(key,e['path'],revision=1)
                require(kept['after']['sha256']==e['sha256'] and kept['after']['size']==e['size'],
                        'group-worker-submission-changed')
            lane.pop('reason',None)
            lane.update(phase='submitted',receipt=shown['receipt'])
            raw=self._save(raw,state)
        return self._result(state)

    def _result(self, state):
        phases={k:v['phase'] for k,v in state['work'].items()}
        return dict(group=self.name,workers=state['work'],submitted=sum(p=='submitted' for p in phases.values()),
                    ready_for_group_candidate=all(p=='submitted' for p in phases.values()))
