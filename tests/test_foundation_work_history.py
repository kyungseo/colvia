"""An ordinary Work's decision trail, through the CLI dispatcher, with synthetic records."""
import json
from unittest import TestCase
from unittest.mock import patch

from colvia import work_history, work_lifecycle
from colvia.cli import command_readonly, dispatch, parser
from colvia.codec import RecordError
from colvia.presentation import human
from colvia.records import link
from test_foundation_scope_addition import ScopeCommands
from test_foundation_work import WorkFixture


class HistoryTests(ScopeCommands, WorkFixture, TestCase):
    def page(self, work='report', *, cursor=None, limit=20):
        args = ['ordinary', 'history', work, '--limit', str(limit)]
        if cursor is not None:
            args += ['--cursor', json.dumps(cursor)]
        parsed = parser(managed=True).parse_args(args)
        self.assertTrue(command_readonly(parsed))
        return dispatch(parsed, self.store, self.workspace)

    def test_returned_revision_and_later_acceptance_remain_distinct(self):
        self.start()
        path = self.root/'report.md'
        path.write_text('original estimate')
        first = self.submit()
        first_head = self.service._head('report')[1]
        self.service.accept(operation='accept-first', work='report', receipt=first['receipt'], statement='좋습니다')
        self.service.revise(operation='reopen', work='report', receipt=self.service.view('report')['reopen_receipt'],
                            statement='출처가 약하니 빼 주세요')
        path.write_text('revised without estimate')
        second = self.submit(operation='second')
        self.service.accept(operation='accept-second', work='report', receipt=second['receipt'], statement='좋습니다')
        self.service.archive(operation='archive', work='report', archived=True)
        self.plan('other', ('other.md',))
        before = self.store.root().ref
        with patch.object(self.workspace, 'observe', side_effect=AssertionError('must not inspect files')):
            page = self.page()
        self.assertEqual(before,self.store.root().ref)
        self.assertFalse(page['partial'])
        self.assertEqual(['accept','submit','request-changes','accept','submit','approve','plan'],
                         [row['kind'] for row in page['items']])
        request = page['items'][2]
        self.assertEqual((1,link(first_head,'result').sha256,'출처가 약하니 빼 주세요'),
                         (request['revision'],request['submission'],request['text']))
        self.assertNotEqual(request['submission'],page['items'][0]['submission'])
        self.assertEqual(2,page['items'][0]['revision'])
        self.assertIn(request['source'][:12],human(page))
        self.assertEqual(request, self.page(cursor=request['open'],limit=1)['items'][0])
        full = self.service.result_content('report','report.md',revision=request['revision'])
        self.assertEqual(request['submission'],full['submission'])
        self.assertEqual('original estimate',full['after']['text'])

    def test_note_scope_and_lifecycle_have_their_own_sources(self):
        self.start()
        from colvia.progress import save
        save(self.service,'report','one-note', self.service.view('report')['progress_receipt'],
             dict(done='가설: 출처가 약할 수 있음',checked='확인 전',remaining='자료 비교',next_action='출처 확인'))
        delta = ['--create','appendix.md']
        self.approve(self.preview(*delta)['receipt'],*delta)
        for action in ('pause','resume'):
            args = (self.service,'report',action,'자료 대기' if action=='pause' else '자료 도착','','')
            work_lifecycle.apply(*args,work_lifecycle.proposal(*args)[0]['receipt'],action)
        (self.root/'report.md').write_text('result')
        review=self.submit()
        self.service.revise(operation='revise',work='report',receipt=review['receipt'],statement='빼 주세요')
        page=self.page()
        self.assertFalse(page['partial'],page)
        self.assertEqual(['request-changes','submit','resume','pause','scope','progress','approve','plan'],
                         [i['kind'] for i in page['items']])
        self.assertEqual('빼 주세요',page['items'][0]['text'])
        self.assertNotIn('reason',page['items'][0])
        self.assertEqual('가설: 출처가 약할 수 있음',page['items'][5]['note']['done'])
        self.assertEqual('검사 자료 보강',page['items'][4]['reason'])
        self.assertNotEqual(page['items'][4]['plan'], page['items'][5]['plan'])

    def test_separate_work_sparse_pages_stale_cursor_and_missing_source(self):
        self.start()
        self.plan('other',('other.md',))
        self.service.approve(operation='approve-other',work='other',
                             receipt=self.service.plan_review('other')['receipt'],statement='타 작업 승인')
        with patch.object(work_history,'WINDOW',1):
            first=self.page()
            self.assertEqual([],first['items'])
            self.assertTrue(first['next'])
            rows = []
            page=first
            while page['next']:
                page=self.page(cursor=page['next'])
                rows.extend(page['items'])
            self.assertEqual(['approve','plan'],[r['kind'] for r in rows])
        with self.assertRaisesRegex(RecordError,'work-history-cursor'):
            self.page('other',cursor=first['next'])
        self.plan('third',('third.md',))
        with self.assertRaisesRegex(RecordError,'work-history-cursor'):
            self.page(cursor=first['next'])
        ref = link(self.service._head('report')[1], 'approval')
        load=self.store.load
        def blocked(selected):
            if selected==ref:
                raise RecordError('object-unavailable')
            return load(selected)
        with patch.object(self.store,'load',side_effect=blocked):
            incomplete=self.page()
        self.assertTrue(incomplete['partial'])
        self.assertEqual('object-unavailable',incomplete['unavailable'])
        self.assertIn('확인할 수 없습니다',human(incomplete))
        self.assertIn('plan', [i['kind'] for i in incomplete['items']])
        issues = [row for row in incomplete['items'] if row['kind'] == 'issue']
        self.assertTrue(issues)
        self.assertTrue(all(i['issue'] == 'unavailable' and i['sequence'] and i['operation'] for i in issues))
        self.assertFalse(incomplete['stopped'])
        self.assertTrue(page['continuation'])
        self.assertFalse(page['partial'])

    def test_two_events_in_one_publication_have_distinct_locators(self):
        from colvia import progress
        self.start()
        args = (self.service, 'report', 'pause', '자료 대기', '', '')
        with patch.object(self.store, 'commit_heads') as capture:
            progress.save(self.service, 'report', 'note', self.service.view('report')['progress_receipt'],
                          dict(done='초안', checked='확인', remaining='검토', next_action='검토'))
            note = capture.call_args.kwargs
            work_lifecycle.apply(*args, work_lifecycle.proposal(*args)[0]['receipt'], 'pause')
            pause = capture.call_args.kwargs
        # Exercise the reader at an atomic publication boundary, using genuine records.
        self.store.commit_heads(operation='both', expected={**note['expected'], **pause['expected']},
                                changes={**note['changes'], **pause['changes']},
                                objects=note['objects'] + pause['objects'],
                                validate=lambda view: (note['validate'](view), pause['validate'](view)))
        first = self.page(limit=1)
        second = self.page(limit=1, cursor=first['next'])
        self.assertEqual(['pause'], [i['kind'] for i in first['items']])
        self.assertEqual(['progress'], [i['kind'] for i in second['items']])
        self.assertEqual(first['items'][0]['sequence'], second['items'][0]['sequence'])
        for row in (first['items'][0], second['items'][0]):
            self.assertEqual([row], self.page(limit=1, cursor=row['open'])['items'])

        key = 'progress:report'
        self.store.commit_heads(operation='remove-note-link', expected={key:self.store.head(key)},
                                changes={key:None}, validate=lambda view: None)
        self.assertEqual('note-removed', self.page()['items'][0]['kind'])

    def test_other_head_transition_and_pause_in_review_are_not_acceptance(self):
        self.start()
        prior, head = self.service._head('report')
        plan = self.service._object(link(head,'plan'))
        pair = self.service._head_record(plan.ref, plan.payload, 'active', previous=prior,
                                         approval=link(head,'approval'))
        self.store.commit_heads(operation='carry-head', expected={'work:report':prior},
                                changes={'work:report':pair[0]}, objects=[pair],
                                validate=lambda view:self.service._validate_head(pair[0],view))
        self.assertEqual('other-change',self.page()['items'][0]['kind'])
        (self.root/'report.md').write_text('초안')
        self.submit()
        args = (self.service,'report','pause','기다림','','')
        work_lifecycle.apply(*args,work_lifecycle.proposal(*args)[0]['receipt'],'pause')
        page = self.page()
        self.assertNotIn('revision',page['items'][0])
        self.assertEqual(1,page['items'][1]['revision'])
        page['items'][0]['kind']='unknown-action'
        self.assertIn('작업 기록',human(page))

    def test_read_budget_continues_and_broken_lineage_stops_at_known_position(self):
        self.start()
        for i in range(5):
            (self.root/'report.md').write_text(str(i))
            receipt = self.submit(operation='submit-'+str(i))['receipt']
            self.service.revise(operation='revise-'+str(i),work='report',receipt=receipt,statement='더 자세히')
        full = self.page()
        original = work_history.PageReader.load
        sizes = []
        def measure(reader, ref):
            raw = original(reader, ref)
            sizes.append(reader.size)
            return raw
        with patch.object(work_history.PageReader,'load',measure):
            self.page()
        with patch.object(work_history, 'PAGE_BYTES', max(sizes)*2//3):
            rows = []
            cursor = None
            for _ in range(15):
                page = self.page(cursor=cursor)
                self.assertIsNone(page['unavailable'],page)
                rows.extend(i['source'] for i in page['items'])
                cursor = page['next']
                if cursor is None:
                    break
            self.assertTrue(page['continuation'])
            self.assertFalse(page['partial'])
            self.assertEqual([i['source'] for i in full['items']], rows)
        old = work_history.PageReader.publication
        calls = []
        def damaged(reader, ref):
            calls.append(ref)
            if len(calls)==3:
                raise RecordError('invalid-root-lineage')
            return old(reader,ref)
        with patch.object(work_history.PageReader,'publication', damaged):
            incomplete = self.page()
        self.assertTrue(incomplete['items'])
        self.assertEqual('invalid',incomplete['stopped']['issue'])
        self.assertTrue(incomplete['stopped']['sequence'])
        self.assertIsNone(incomplete['next'])
        self.assertIn('중단',human(incomplete))

    def test_discard_and_replace_never_turn_into_acceptance(self):
        for action in ('discard','replace'):
            self.plan(action,(action+'.md',))
        self.plan('target',('target.md',))
        for action in ('discard','replace'):
            target='target' if action=='replace' else ''
            args=(self.service,action,action,'목표 변경','',target)
            work_lifecycle.apply(*args,work_lifecycle.proposal(*args)[0]['receipt'],action)
            rows=self.page(action)['items']
            self.assertEqual([action,'plan'],[r['kind'] for r in rows])
            self.assertEqual(target,rows[0]['target'])
