"""The project overview reads recorded next steps and pins its follow-up to a submission."""
from contextlib import redirect_stdout
from hashlib import sha256
from io import StringIO
import json
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from colvia import cli, progress, work_lifecycle
from colvia.codec import RecordError
from colvia.maps import build_map, scan_map
from colvia.presentation import human
from colvia.project_status import project_status
from colvia.storage.sqlite import GenerationStore
from test_foundation_binding import I, P, W
from test_foundation_work import WorkFixture


class ProjectStatusTests(WorkFixture, unittest.TestCase):
    def output(self, *args):
        def open_workspace(path, *, readonly):
            self.assertTrue(readonly)
            db = GenerationStore(self.store.path, project=P, instance=I, generation='g',
                                 readonly=True, active_check=lambda: None)
            return None, db, self.workspace
        buffer = StringIO()
        with redirect_stdout(buffer):
            self.assertEqual(0, cli.main(list(args), entry=SimpleNamespace(workspace=open_workspace)))
        return buffer.getvalue().rstrip()

    def status(self, **kw):
        return project_status(self.store, W, **kw)

    def change_state(self, work, action):
        def call(step, *flags):
            args = cli.parser(managed=True).parse_args([
                'ordinary','lifecycle-' + step,work,action,'--reason','응답 대기',*flags])
            return cli.dispatch(args, self.store, self.workspace)
        receipt = call('preview')['receipt']
        return call('apply', '--receipt', receipt)

    def test_single_and_empty_readonly_including_files_and_database(self):
        self.assertFalse(self.status()['partial'])
        self.assertIn('없습니다', human(self.status()))
        self.start('proposal')
        (self.root/'report.md').write_text('first version')
        self.submit('proposal')
        def snapshot():
            return (self.store.root().ref, sha256(self.store.path.read_bytes()).digest(),
                    {p.relative_to(self.root): p.read_bytes() for p in self.root.rglob('*') if p.is_file()})
        before = snapshot()
        data = json.loads(self.output('--json', 'project', 'status'))
        screen = self.output('project', 'status')
        self.assertEqual(human(data), screen)
        self.assertEqual(1, len(screen.splitlines()))
        self.assertEqual('내 검토 · 팀 회의 보고서 — 제출본 1판 검토하기', screen)
        self.assertEqual(1, data['counts']['review'])
        self.assertEqual(before, snapshot())

    def test_followup_with_duplicate_titles_keeps_the_shown_work_and_revision(self):
        for name in ('proposal', 'schedule'):
            self.start(name, (name+'.md',))
            (self.root/(name+'.md')).write_text(name+' first')
            self.submit(name)
        rows = self.status()['items']
        self.assertEqual(rows[0]['title'], rows[1]['title'])
        self.assertNotEqual(rows[0]['submitted_paths'], rows[1]['submitted_paths'])
        original = rows[0]
        self.assertEqual('proposal', original['work'])
        receipt = self.service.review('proposal')['receipt']
        self.service.revise(operation='revision-request', work='proposal', receipt=receipt, statement='출처 추가')
        path, = original['submitted_paths']
        (self.root/path).write_text('proposal second')
        self.submit('proposal', operation='second-submission')
        ref = json.loads(self.output('--json','ordinary','content',original['work'],path,
                                     '--revision',str(original['revision'])))
        self.assertEqual(original['submission'], ref['submission'])
        self.assertEqual('proposal first', ref['after']['text'])
        self.assertEqual(2, self.status()['items'][0]['revision'])

    def test_paused_review_is_not_counted_again_and_terminal_items_are_hidden(self):
        self.start()
        (self.root/'report.md').write_text('result')
        self.submit()
        self.change_state('report','pause')
        data = self.status()
        self.assertEqual((0, 1), (data['counts']['review'], data['counts']['paused']))
        self.assertEqual('응답 대기', data['items'][0]['reason'])
        self.change_state('report','resume')
        receipt = self.service.review('report')['receipt']
        self.service.accept(operation='accept', work='report', receipt=receipt, statement='수락')
        self.assertEqual([], self.status()['items'])
        self.service.archive(operation='archive', work='report', archived=True)
        self.plan('abandoned')
        self.change_state('abandoned','discard')
        self.assertEqual([], self.status()['items'])

    def test_partial_counts_only_shown_items_and_cursor_is_bound_to_a_root(self):
        for work in ('a','b'):
            self.start(work, (work+'.md',))
            (self.root/(work+'.md')).write_text(work)
            self.submit(work)
        summaries = []
        page = self.status(limit=1)
        cursor = page['next']
        while True:
            self.assertTrue(page['partial'])
            self.assertIn('다른 검토 요청이 있을 수 있습니다', human(page))
            self.assertEqual(1, page['counts']['review'])
            summaries.extend(i['work'] for i in page['items'])
            if not page['next']:
                break
            page = self.status(limit=1, cursor=page['next'])
        self.assertEqual(['a', 'b'], summaries)
        self.plan('later')
        with self.assertRaisesRegex(RecordError, 'invalid-cursor'):
            self.status(cursor=cursor)
        with self.assertRaisesRegex(RecordError, 'invalid-cursor'):
            self.status(cursor='invalid')

    def test_latest_note_or_explicit_resumption_next_action(self):
        self.start()
        def note(operation, next_action):
            progress.save(self.service, 'report', operation, self.service.view('report')['progress_receipt'],
                          dict(done='자료 확인', checked='원본 확인', remaining='문장 정리', next_action=next_action))
        note('first-note', '첫 초안')
        self.change_state('report', 'pause')
        args = (self.service, 'report', 'resume', '답변 도착', '답변 반영', '')
        preview, *_ = work_lifecycle.proposal(*args)
        work_lifecycle.apply(*args, preview['receipt'], 'resume-action')
        reopened, = self.status()['items']
        self.assertTrue(reopened['resumed'])
        self.assertEqual('답변 반영', reopened['next_action'])
        note('new-note', '맞춤법 확인')
        self.assertEqual('맞춤법 확인', self.status()['items'][0]['next_action'])

    def test_scan_window_can_hide_a_review_and_seek_without_duplicates(self):
        self.start()
        (self.root/'report.md').write_text('submitted')
        self.submit()
        with patch('colvia.project_status.WINDOW', 1):
            page = self.status()
            seen = []
            found_before_review = False
            while True:
                seen.extend(row['work'] for row in page['items'])
                if not seen and page['next']:
                    found_before_review = True
                    self.assertTrue(page['partial'])
                    self.assertIn('다른 검토 요청', human(page))
                    self.assertNotIn('없습니다', human(page))
                if not page['next']:
                    break
                page = self.status(cursor=page['next'])
            self.assertEqual(['report'], seen)
            self.assertTrue(found_before_review)

    def test_unreadable_and_other_workspace_are_not_treated_as_absence(self):
        self.plan()
        self.assertFalse(project_status(self.store, 'elsewhere')['items'][0]['here'])
        self.assertIn('다른 작업 폴더', human(project_status(self.store, 'elsewhere')))
        ref, original = self.store.head('work:report'), self.store.load
        def broken(obj):
            if obj == ref:
                raise RecordError('synthetic-damage')
            return original(obj)
        with patch.object(self.store, 'load', broken):
            page = self.status()
        self.assertEqual('unavailable', page['items'][0]['group'])
        self.assertTrue(page['partial'])
        self.assertNotIn('없습니다', human(page))

    def test_map_seek_matches_the_full_traversal_at_every_position(self):
        sample = self.store.root().ref
        tree = build_map((f'key:{i}', sample) for i in range(95))
        load = dict(tree.objects).__getitem__
        entries = list(scan_map(tree.root, load))
        for i, (key, _) in enumerate(entries):
            self.assertEqual(entries[i+1:], list(scan_map(tree.root, load, after=key)))
