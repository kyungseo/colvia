"""A progress note is an observation, never a Work transition."""
from unittest import TestCase
from unittest.mock import patch
from io import BytesIO
from pathlib import Path

from colvia.cli import parser, dispatch
from colvia.codec import RecordError
from colvia.presentation import human
from colvia.progress import save
from test_foundation_work import WorkFixture


class ProgressTests(WorkFixture, TestCase):
    def note(self, operation='note', receipt=None, **overrides):
        args = parser(managed=True).parse_args(['--operation', operation, 'ordinary', 'progress', 'report',
            '--receipt', receipt or self.service.view('report')['progress_receipt'],
            '--done', overrides.get('done', '집계표 작성'), '--checked', '미실행', '--remaining', '출처 확인',
            '--next-action', '표의 출처 확인'])
        return dispatch(args,self.store,self.workspace)

    def test_save_resume_submit_accept(self):
        paths=['a','b','c','d','e']
        self.start(scope=paths)
        for name in ('a','b','d'):
            (self.root/name).write_text('one')
        head=self.store.head('work:report')
        self.assertTrue(self.service.view('report')['first_project_note'])
        stored = self.note()
        self.assertTrue(stored['progress_saved'])
        self.assertIn('진척을 기록했습니다', human(stored))
        self.assertEqual(head,self.store.head('work:report'))
        self.assertFalse(self.service.view('report')['first_project_note'])
        old=self.store.root().ref
        (self.root/'b').write_text('two')
        (self.root/'c').write_text('three')
        (self.root/'d').unlink()
        (self.root/'e').symlink_to(self.root/'source.csv')
        value=self.service.view('report')
        self.assertEqual(old,self.store.root().ref)
        self.assertEqual(['unchanged','changed','created','deleted','unavailable'],
                         [v['status'] for v in value['progress']['files']])
        self.assertIn('출처 확인',human(value))
        (self.root/'e').unlink()
        submitted=self.submit()
        self.assertNotIn('progress',self.service.view('report'))
        self.assertEqual(self.service.accept(operation='accept',work='report',
            receipt=submitted['receipt'],statement='이 제출본 수락')['state'],'completed')

    def test_refuses_stale_replay_and_preserves_history(self):
        self.start()
        first=self.service.view('report')['progress_receipt']
        self.note(receipt=first); original=self.store.head('progress:report')
        with self.assertRaisesRegex(RecordError,'progress-view-stale'):
            self.note(receipt=first)
        with self.assertRaisesRegex(RecordError,'operation-already-recorded'):
            self.note()
        self.note(operation='second',done='둘째 메모')
        from colvia.records import link
        current=self.service._object(self.store.head('progress:report'))
        self.assertEqual(link(current,'previous'),original)
        self.assertEqual(self.service.view('report')['progress']['done'],'둘째 메모')

    def test_refuses_invalid_input_interruption_and_wrong_target(self):
        self.start()
        root=self.store.root().ref
        for invalid in ('   ', 'one\u2028two', 'x' * 2049):
            with self.subTest(invalid=invalid[:8]), self.assertRaisesRegex(RecordError, 'invalid-progress-text'):
                self.note(done=invalid)
        # Interrupt inside SQLite after inserting the note, before publishing its root.
        before = self.store.db.execute('SELECT count(*) FROM objects').fetchone()
        put = self.store._put
        def stop_after_insert(ref, raw, **kwargs):
            put(ref, raw, **kwargs)
            if ref.kind == 'work.progress':
                raise OSError('stop')
        with patch.object(self.store, '_put', side_effect=stop_after_insert), self.assertRaises(OSError):
            self.note()
        self.assertEqual(before, self.store.db.execute('SELECT count(*) FROM objects').fetchone())
        with patch.object(self.workspace,'workspace','other'),self.assertRaisesRegex(RecordError,'wrong-workspace'):
            save(self.service,'report','wrong','none',{})
        self.assertEqual(self.store.root().ref,root)
        self.assertIsNone(self.store.head('progress:report'))

    def test_submit_wins_race_and_rework_remains_distinct(self):
        self.start(); (self.root/'report.md').write_text('draft')
        receipt=self.service.view('report')['progress_receipt']
        commit=self.store.commit_heads
        def race(**kwargs):
            if kwargs['operation']=='note':
                self.submit()
            return commit(**kwargs)
        with patch.object(self.store,'commit_heads',side_effect=race),self.assertRaisesRegex(RecordError,'head-conflict'):
            self.note(receipt=receipt)
        self.assertIsNone(self.store.head('progress:report'))
        review=self.service.review('report')
        self.service.revise(operation='revise',work='report',receipt=review['receipt'],statement='출처를 추가')
        self.assertIn('rework',self.service.view('report'))
        with self.assertRaisesRegex(RecordError,'progress-first-submission-only'):self.note(receipt=receipt)

    def test_note_backup_roundtrip_and_previous_reader_refusal(self):
        from colvia.backup import ExportBudget, ImportedSnapshot, supported_requirements, write_export
        from colvia.graph import AuditBudget, GraphAudit, Registry
        from colvia.storage.restore import fill_candidate
        from colvia.storage.sqlite import GenerationStore
        from test_foundation_binding import P, I

        self.start()
        original_head = self.store.head('work:report')
        registry = self.service.registry
        old = Registry([schema for (kind, _), schema in registry._schemas.items() if kind != 'work.progress'])
        previous_caps = supported_requirements(old)
        base = Path(self.tmp.name)
        graph_budget = AuditBudget(50000, 100000, 64 * 1024**2)
        export_budget = ExportBudget(50000, 64 * 1024**2)

        def export():
            audit = GraphAudit(base / 'export.audit', graph_budget)
            try:
                audit.run(self.store.root().ref, self.store.load, registry, require_known=True)
                output = BytesIO()
                write_export(output, project=P, audit=audit, load=self.store.load)
                return output.getvalue()
            finally:
                audit.close()

        def restore(data, version, name):
            caps = supported_requirements(version)
            return ImportedSnapshot(base / name, BytesIO(data), budget=export_budget,
                graph_budget=graph_budget, registry=version, capabilities=caps, writable_capabilities=caps)

        handle = GenerationStore(self.store.path, project=P, instance=I, generation='g',
            active_check=lambda: None, reader_capabilities=previous_caps, writer_capabilities=previous_caps)
        self.addCleanup(handle.close)
        self.assertEqual(original_head, handle.head('work:report'))
        self.note()
        first = self.store.head('progress:report')
        self.note(operation='second', done='두 번째 메모')
        latest = self.store.head('progress:report')
        with self.assertRaisesRegex(RecordError, 'store-reader-capability-unavailable'):
            handle.root()
        data = export()
        with self.assertRaisesRegex(RecordError, 'import-capability-unavailable'):
            restore(data, old, 'old.import')
        snapshot = restore(data, registry, 'new.import')
        self.addCleanup(snapshot.close)
        caps = supported_requirements(registry)
        restored = GenerationStore.create(base / 'restored.sqlite3', project=P, instance='restore',
            generation='restore', active_check=lambda: None, reader_capabilities=caps, writer_capabilities=caps)
        self.addCleanup(restored.close)
        fill_candidate(restored, snapshot, operation='restore', unselected=lambda: None)
        self.assertEqual(original_head, restored.head('work:report'))
        self.assertEqual(latest, restored.head('progress:report'))
        for ref in (first, latest, original_head):
            self.assertEqual(self.store.load(ref), restored.load(ref))

    def test_only_first_bounded_approved_paths_are_observed(self):
        from colvia.progress import MAX_PATHS
        paths = [f'file-{i:03d}.md' for i in range(MAX_PATHS + 1)]
        self.start(scope=paths)
        self.note()
        result = self.service.view('report')['progress']
        self.assertEqual({p['path'] for p in result['files']}, set(paths[:MAX_PATHS]))
        self.assertEqual(result['additional_paths_unavailable'], 1)

    def test_nested_project_and_read_errors_are_unavailable(self):
        workdir = self.root / 'notes'
        workdir.mkdir()
        report = workdir / 'report.md'
        report.write_text('current')
        self.start(scope=['notes/report.md'])
        self.note()
        (workdir / '.colvia-link.json').write_text('{}')
        self.assertEqual('unavailable', self.service.view('report')['progress']['files'][0]['status'])
        (workdir / '.colvia-link.json').unlink()
        with patch('colvia.workspace.selected', side_effect=PermissionError()):
            self.assertEqual('unavailable', self.service.view('report')['progress']['files'][0]['status'])

    def test_changed_parent_during_posix_hash_is_unavailable(self):
        import os
        import sys
        if sys.platform == 'win32':
            self.skipTest('POSIX rename semantics')
        folder = self.root / 'draft'
        folder.mkdir()
        (folder / 'note.md').write_text('original')
        self.start(scope=['draft/note.md'])
        self.note()
        read = os.read
        def swap_parent(fd, size):
            raw = read(fd, size)
            if raw and not (self.root / 'old').exists():
                folder.rename(self.root / 'old')
                folder.mkdir()
                (folder / 'note.md').write_bytes(raw)
            return raw
        with patch('colvia.platforms.selected.os.read', side_effect=swap_parent):
            result = self.service.view('report')['progress']
        self.assertEqual(result['files'], [dict(path='draft/note.md', status='unavailable')])

    def test_windows_progress_observes_only_regular_files_in_same_project(self):
        from colvia.platforms.windows_observation import Observer
        from test_foundation_windows_observation import FilesDouble
        observer = Observer(files=FilesDouble())
        directory = self.root / 'notes'
        directory.mkdir()
        (directory / 'a').write_text('one')
        files = observer.selected(self.root, ['notes/a', 'notes/b'], byte_limit=32, verify_path=True)
        self.assertEqual([entry['path'] for entry in files], ['notes/a'])
        (directory / '.git').mkdir()
        with self.assertRaisesRegex(RecordError, 'progress-nested-project'):
            observer.selected(self.root, ['notes/a'], byte_limit=32, verify_path=True)

    def test_paginated_resume_keeps_review_and_active_work_choices_distinct(self):
        import json
        self.start()
        self.note()
        self.start(work='letter', scope=['letter.md'])
        self.assertFalse(self.service.view('letter')['first_project_note'])
        (self.root / 'letter.md').write_text('draft')
        self.submit(work='letter')
        root = self.store.root().ref

        def page(*options):
            args = parser(managed=True).parse_args(['--json', 'ordinary', 'list', '--limit', '1', *options])
            return dispatch(args, self.store, self.workspace)

        first = page()
        second = page('--cursor', json.dumps(first['next']))
        self.assertIsNone(second['next'])
        self.assertEqual({(item['work'], item['state']) for item in first['items'] + second['items']},
                         {('letter', 'review'), ('report', 'active')})
        self.assertNotIn('progress', self.service.view('letter'))
        self.assertIn('progress', self.service.view('report'))
        self.assertEqual(root, self.store.root().ref)

    def test_composition_roundtrip_preserves_note_and_requires_fresh_receipt(self):
        from colvia.composition import CompositionService
        self.start()
        self.note()
        initial = self.service.view('report')
        composition = CompositionService(self.service)
        self.plan('parent', scope=['integration.md'])
        self.plan('other', scope=['other.md'])
        composition.declare(operation='declare', parent='parent', children=['other'], document='integration.md',
                            checks=['집계 대조'], statement='하위 작업 연결')
        for n, children in enumerate((['other', 'report'], ['other'])):
            preview = composition.rebind_preview('parent', children=children)
            composition.rebind(operation=f'rebind-{n}', parent='parent', children=children,
                               receipt=preview['receipt'], statement='하위 작업 변경')
        final = self.service.view('report')
        self.assertEqual(initial['progress'], final['progress'])
        self.assertNotEqual(initial['progress_receipt'], final['progress_receipt'])
        with self.assertRaisesRegex(RecordError, 'progress-view-stale'):
            self.note(operation='stale', receipt=initial['progress_receipt'])
        self.note(operation='next', receipt=final['progress_receipt'], done='이어 쓴 메모')
        self.assertEqual(self.service.view('report')['progress']['done'], '이어 쓴 메모')

    def test_recorded_note_survives_git_observation_failure_but_connection_must_match(self):
        self.start()
        self.note()
        with patch('colvia.progress.fingerprints', side_effect=RecordError('git-observation-changed')):
            value = self.service.view('report')['progress']
            self.assertEqual(value['files'], [dict(path='report.md', status='unavailable')])
            self.assertEqual(value['checked'], '미실행')
            with patch.object(self.workspace, 'verify', side_effect=RecordError('wrong-workspace')):
                with self.assertRaisesRegex(RecordError, 'wrong-workspace'):
                    self.service.view('report')
