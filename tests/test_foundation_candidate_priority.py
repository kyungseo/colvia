"""Priority reorders candidates without changing their Work or evidence of user identity."""
from concurrent.futures import ThreadPoolExecutor
from io import BytesIO
import json
from pathlib import Path
from threading import Barrier
from unittest import TestCase
from unittest.mock import patch

from colvia import candidate_priority as priority
from colvia.backup import ExportBudget, ImportedSnapshot, supported_requirements, write_export
from colvia.cli import command_readonly, dispatch, parser
from colvia.codec import RecordError
from colvia.graph import AuditBudget, GraphAudit, Registry
from colvia.planning import Planning
from colvia.presentation import human
from colvia.records import application_registry
from colvia.storage.restore import fill_candidate
from colvia.storage.sqlite import GenerationStore
from test_foundation_binding import I, P
from test_foundation_work import WorkFixture


class PriorityTests(WorkFixture, TestCase):
    def setUp(self):
        super().setUp()
        self.planning = Planning(self.store)

    def candidate(self, name, **kw):
        return self.planning.save_candidate(operation='add-' + name, candidate=name,
                                            title=name, reason='trial', **kw)

    def command(self, action, *args, op=None):
        argv = (['--operation', op] if op else []) + ['candidate', action, *args]
        parsed = parser(managed=True).parse_args(argv)
        self.assertEqual(action != 'priority-set', command_readonly(parsed))
        return dispatch(parsed, self.store, self.workspace)

    def basis(self, name, level):
        return self.command('priority-preview', name, level)['basis']

    def change(self, name, level, operation, basis=None, **kw):
        return self.command('priority-set', name, level, '--basis', basis or self.basis(name, level),
                            '--recorder', kw.get('recorder', 'agent'), '--request', kw.get('request', '동료 체험 순위 변경'),
                            *(['--reason', kw['reason']] if 'reason' in kw else []), op=operation)

    def test_set_change_clear_and_open_exact_work(self):
        self.start('guide', ('guide.md',))
        self.candidate('coworker', work='guide')
        self.candidate('other', work='guide')
        head = self.store.head('work:guide')
        candidate = self.store.head('candidate:coworker')
        root = self.store.root().ref
        self.assertEqual('unset', self.planning.candidate('coworker')['priority'])
        self.assertEqual([], self.command('priority-history','coworker')['items'])
        self.assertEqual('priority-unchanged', self.change('coworker','unset','clear-empty')['kind'])
        self.assertEqual(root, self.store.root().ref)
        warning = '이 프로젝트와 이후 백업을 열 수 없습니다.'
        self.assertNotIn(warning, human(self.command('priority-preview', 'coworker', 'unset')))
        preview = human(self.command('priority-preview', 'coworker', 'high'))
        self.assertIn(warning, preview)
        self.assertIn('순위를 모두 지워도', preview)
        first = self.change('coworker', 'high', 'first')
        self.assertNotIn(warning, human(self.command('priority-preview', 'other', 'high')))
        self.assertIsNone(first['change']['reason'])
        self.assertIn('에이전트가 전달한 사용자 요청', human(first))
        self.change('coworker','low','second',reason='다음 주 체험')
        self.change('coworker','unset','third',recorder='operator')
        history = self.command('priority-history','coworker','--limit','2')
        tail = self.command('priority-history','coworker','--cursor',json.dumps(history['next']))
        rows = history['items'] + tail['items']
        self.assertEqual([('low','unset'),('high','low'),('unset','high')],[(r['old'],r['new']) for r in rows])
        self.assertEqual('operator', rows[0]['recorder'])
        self.assertEqual(priority.BASIS, rows[0]['authority'])
        self.assertEqual('다음 주 체험', rows[1]['reason'])
        self.assertTrue(all(r['as_of'] > 0 for r in rows))
        self.assertEqual(head, self.store.head('work:guide'))
        self.assertEqual(candidate, self.store.head('candidate:coworker'))
        self.assertEqual('unset', self.planning.candidate('other')['priority'])
        self.assertEqual('active', self.service.view('guide')['state'])

    def test_stale_basis_target_dismissal_and_exact_retry(self):
        self.candidate('a')
        self.candidate('b')
        basis = self.basis('a','high')
        stale = self.basis('a','low')
        before = self.store.root().ref
        for name,level in [('a','low'),('b','high')]:
            with self.assertRaisesRegex(RecordError,'priority-preview-stale'):
                self.change(name, level, 'wrong-target', basis)
        with self.assertRaisesRegex(RecordError,'priority-request-required'):
            self.change('a','high','empty',request=' ')
        self.assertEqual(before,self.store.root().ref)
        original = self.change('a','high','same',basis)
        with self.assertRaisesRegex(RecordError,'priority-preview-stale'):
            self.change('a','low','race',stale)
        self.change('a','low','later')
        now = self.store.root().ref
        replay = self.change('a','high','same',basis)
        self.assertTrue(replay['replayed'])
        self.assertEqual(original['change'],replay['change'])
        with self.assertRaisesRegex(RecordError,'priority-operation-conflict'):
            self.change('a','high','same',basis,request='다른 요청')
        self.assertEqual(now,self.store.root().ref)
        self.assertEqual('low',self.planning.candidate('a')['priority'])
        self.planning.save_candidate(operation='dismiss',candidate='a',title='a',reason='done',
                                     state='dismissed',expected=self.store.head('candidate:a'))
        with self.assertRaisesRegex(RecordError,'priority-candidate-closed'):
            self.basis('a','high')
        self.assertEqual(['b'],[r['candidate'] for r in self.command('ranked')['items']])

    def test_ranked_paging_order_and_stale_list(self):
        for key in ('c','d','a','b','e'):
            self.candidate(key)
        for key,level in [('d','high'),('b','high'),('a','low'),('e','normal')]:
            self.change(key,level,'rank-'+key)
        before = self.store.root().ref
        page = self.command('ranked','--limit','2')
        first_cursor = page['next']
        found = []
        while True:
            found.extend((r['candidate'],r['priority']) for r in page['items'])
            if not page['next']:
                break
            self.assertIn('일부 후보',human(page))
            page = self.command('ranked','--limit','2','--cursor',json.dumps(page['next']))
        self.assertEqual(found,[('b','high'),('d','high'),('e','normal'),('a','low'),('c','unset')])
        self.assertEqual(before,self.store.root().ref)
        self.change('a','high','updated')
        with self.assertRaisesRegex(RecordError,'invalid-cursor'):
            self.command('ranked','--cursor',json.dumps(first_cursor))

    def test_separate_scan_windows_keep_all_candidates_and_mark_partial_results(self):
        for key in ('a','b','c','d','e','f'):
            self.candidate(key)
        self.change('f','high','first')
        with patch.object(priority, 'SCAN_WINDOW', 3):
            page = self.command('ranked','--limit','1')
            rows = []
            while True:
                self.assertTrue(page['partial'])
                rows.extend(page['items'])
                if not page['next']:
                    break
                page = self.command('ranked','--limit','1','--cursor',json.dumps(page['next']))
        order = sorted(rows, key=lambda r:(priority.LEVELS.index(r['priority']), r['candidate']))
        self.assertEqual(['f','a','b','c','d','e'], [row['candidate'] for row in order])

    def test_concurrent_edits_publish_one_change_and_same_operation_replays(self):
        for key, same in [('independent', False), ('repeated', True)]:
            self.candidate(key)
            levels = ['high', 'high' if same else 'normal']
            bases = [self.basis(key, level) for level in levels]
            ready = Barrier(2, timeout=10)
            def writer(index):
                db = GenerationStore(self.store.path, project=P, instance=I, generation='g', active_check=lambda:None)
                try:
                    ready.wait()
                    return priority.apply(db, key, levels[index], basis=bases[index], request='시험 요청',
                                          reason=None, recorder='agent', operation=key+str(0 if same else index))
                except RecordError as exc:
                    return exc.code
                finally:
                    db.close()
            with ThreadPoolExecutor(max_workers=2) as pool:
                outcomes = list(pool.map(writer, (0,1)))
            self.assertEqual(1,len(priority.history(self.store,key)['items']))
            if same:
                self.assertEqual([False,True],sorted(r['replayed'] for r in outcomes))
            else:
                self.assertEqual(1,sum(isinstance(r,dict) for r in outcomes),outcomes)
                self.assertIn(next(r for r in outcomes if isinstance(r,str)), ('head-conflict','priority-preview-stale'))

    def test_revised_candidate_requires_fresh_preview_and_unrelated_work_approval_is_refused(self):
        self.candidate('trial')
        old_basis = self.basis('trial','normal')
        current = self.store.head('candidate:trial')
        self.planning.save_candidate(operation='edit', candidate='trial', title='updated', reason='updated',
                                     expected=current)
        work = self.plan()
        before = self.store.root().ref
        for invalid_basis in (old_basis, work['receipt']):
            with self.assertRaisesRegex(RecordError, 'priority-preview-stale'):
                self.change('trial','normal','invalid',invalid_basis)
        with self.assertRaisesRegex(RecordError, 'invalid-priority-source'):
            priority.apply(self.store,'trial','normal', basis=self.basis('trial','normal'),
                           request='시험', reason=None, recorder='delegated-acceptance', operation='unrelated')
        self.assertEqual(before, self.store.root().ref)
        self.assertTrue(self.command('priority-preview','trial','normal')['first_project_priority'])
        self.change('trial','normal','valid')
        self.assertFalse(self.command('priority-preview','trial','normal')['first_project_priority'])

    def test_backup_restore_history_and_old_capability_boundary(self):
        self.check_backup_compatibility(clear_priority=False)

    def test_clearing_all_priorities_preserves_old_reader_and_backup_boundary(self):
        self.check_backup_compatibility(clear_priority=True)

    def check_backup_compatibility(self, *, clear_priority):
        self.candidate('trial')
        registry = application_registry()
        old = Registry([s for (k,_),s in registry._schemas.items() if k != priority.KIND])
        caps = supported_requirements(old)
        handle = GenerationStore(self.store.path, project=P, instance=I, generation='g',
                                 active_check=lambda:None, reader_capabilities=caps,writer_capabilities=caps)
        self.addCleanup(handle.close)
        old_head = handle.head('candidate:trial')
        self.change('trial','high','one')
        self.change('trial','normal','two')
        if clear_priority:
            self.change('trial', 'unset', 'clear')
            for role in ('read', 'write'):
                self.assertIn('schema:planning.priority:1', self.store.requirements()[role])
        with self.assertRaisesRegex(RecordError,'store-reader-capability-unavailable'):
            handle.root()
        gb = AuditBudget(50000,100000,64*1024**2)
        eb = ExportBudget(50000,64*1024**2)
        base = Path(self.tmp.name)
        audit = GraphAudit(base/'export.audit',gb)
        buf = BytesIO()
        try:
            audit.run(self.store.root().ref,self.store.load,registry,require_known=True)
            write_export(buf,project=P,audit=audit,load=self.store.load)
        finally:
            audit.close()
        def snapshot(name, reg, supported):
            return ImportedSnapshot(base/name,BytesIO(buf.getvalue()),budget=eb,graph_budget=gb,
                                    registry=reg,capabilities=supported,writable_capabilities=supported)
        with self.assertRaisesRegex(RecordError,'import-capability-unavailable'):
            snapshot('old.import',old,caps)
        restored_caps = supported_requirements(registry)
        snap = snapshot('new.import',registry,restored_caps)
        self.addCleanup(snap.close)
        copy = GenerationStore.create(base/'restore.db',project=P,instance='restored',generation='copy',
                                      active_check=lambda:None,reader_capabilities=restored_caps,writer_capabilities=restored_caps)
        self.addCleanup(copy.close)
        fill_candidate(copy,snap,operation='restore',unselected=lambda:None)
        self.assertEqual(old_head,copy.head('candidate:trial'))
        self.assertEqual(self.store.head('priority:trial'),copy.head('priority:trial'))
        self.assertEqual(priority.history(self.store,'trial'),priority.history(copy,'trial'))
        expected_priority = 'unset' if clear_priority else 'normal'
        self.assertEqual(expected_priority, Planning(copy).candidate('trial')['priority'])
