"""Ordinary Work decisions preserve evidence across switching, termination and restoration."""
import unittest
from unittest.mock import patch

from colvia import work_lifecycle as lc
from colvia.cli import dispatch, parser
from colvia.codec import RecordError
from colvia.planning import page_heads
from colvia.presentation import human
from colvia.records import link
from test_foundation_scope_addition import ScopeCommands
from test_foundation_work import WorkFixture


class LifecycleTests(ScopeCommands, WorkFixture, unittest.TestCase):
    def decide(self, action, work='report', target='', receipt=None):
        flags=['--reason','목표 확인']
        if target:flags+=['--target',target]
        def call(command,*extra):
            args=parser(managed=True).parse_args(['ordinary','lifecycle-'+command,work,action,*flags,*extra])
            return dispatch(args,self.store,self.workspace)
        preview=call('preview')
        self.assertIn('목표 확인',human(preview))
        return call('apply','--receipt',receipt or preview['receipt'])

    def test_switch_pause_amended_work_and_resume_from_another_service(self):
        from colvia.work import WorkService
        self.start()
        self.start('B',['b.md'])
        self.start('C',['c.md'])
        self.note()
        self.approve(self.preview('--create','appendix.md')['receipt'],'--create','appendix.md')
        before=self.service._head('report')[1]
        root=self.store.root()
        for work in ('report','B','C','report'):
            self.assertEqual('active',self.service.view(work)['state'])
        self.assertEqual(root,self.store.root())
        self.decide('pause')
        self.service=WorkService(self.store,self.workspace)
        view=self.service.view('report')
        self.assertEqual(view['saved_progress']['done'],'초안')
        self.assertEqual('paused',view['state'])
        self.assertEqual('active',self.service.view('B')['state'])
        (self.root/'report.md').write_text('B edited the same path')
        (self.root/'source.csv').write_text('outside A')
        with self.assertRaises(RecordError):self.submit()
        self.assertIn({'path':'report.md','status':'created'},self.service.view('report')['since_pause'])
        self.decide('resume')
        for k in ('plan','approval','result','decision'):
            self.assertEqual(link(before,k),link(self.service._head('report')[1],k))
        self.assertEqual(self.service.view('report')['progress']['done'],'초안')
        with self.assertRaisesRegex(RecordError,'outside-scope-change'):self.submit()

    def test_ordinary_view_tolerates_unrelated_root_change_during_live_check(self):
        self.start()
        self.start('peer',['peer.md'])
        self.decide('pause','peer')
        (self.root/'report.md').write_text('submitted')
        self.submit()
        selected = self.workspace.selected

        def change_unrelated_head(paths):
            self.assertFalse(self.store.db.in_transaction)
            peer = self.store.head('work:peer')
            self.store.commit_heads(operation='unrelated',expected={'test:other':None},
                                    changes={'test:other':peer},validate=lambda _:None)
            return selected(paths)

        from unittest.mock import patch
        with patch.object(self.workspace,'selected',side_effect=change_unrelated_head):
            self.assertTrue(self.service.view('report')['current_matches'])

    def test_review_resume_changed_and_unchanged_and_rework(self):
        self.start(); self.note(); path=self.root/'report.md';path.write_text('submitted')
        first=self.submit()['receipt']
        self.decide('pause')
        path.write_text('changed')
        self.decide('resume')
        self.assertEqual('review',self.service.view('report')['state'])
        def accept(receipt):
            return self.service.accept(work='report',operation='accept',receipt=receipt,statement='ok')
        with self.assertRaisesRegex(RecordError,'stale-result-receipt'):accept(first)
        with self.assertRaisesRegex(RecordError,'reviewed-files-changed'):accept(self.service.review('report')['receipt'])
        self.assertEqual(self.service.result_content('report','report.md')['after']['text'],'submitted')
        path.write_text('submitted')
        self.decide('pause');self.decide('resume')
        self.service.revise(work='report',operation='revise',receipt=self.service.review('report')['receipt'],statement='correct it')
        prior=self.service._head('report')[1]
        self.decide('pause');self.decide('resume')
        self.assertEqual(link(self.service._head('report')[1],'decision'),link(prior,'decision'))
        self.assertEqual('초안',self.service.view('report')['saved_progress']['done'])
        self.submit(operation='submit-again')
        self.decide('pause');self.decide('resume')
        self.assertEqual('completed',accept(self.service.review('report')['receipt'])['state'])

    def test_replacement_chain_multiple_sources_and_discarded_history(self):
        for name in ('A','B','C','D'):self.plan(name,[name])
        self.decide('replace','D','B')
        self.decide('replace','A','B')
        self.assertEqual(self.service.view('B')['replaces'],['A','D'])
        self.assertEqual(self.service.view('B')['state'],'planned')
        self.decide('replace','B','C')
        self.assertEqual(self.service.view('A')['lifecycle']['target'],'B')
        with self.assertRaises(RecordError):self.decide('replace','C','A')
        with self.assertRaises(RecordError):self.decide('replace','C','C')
        self.assertEqual('planned',self.service.view('C')['state'])
        self.start();self.note();(self.root/'report.md').write_text('submitted')
        receipt=self.submit()['receipt']; self.decide('discard')
        with self.assertRaises(RecordError):
            self.service.accept(work='report',operation='late',receipt=receipt,statement='ok')
        self.assertEqual('초안',self.service.view('report')['saved_progress']['done'])
        self.assertEqual('submitted',self.service.result_content('report','report.md')['after']['text'])

    def test_stale_receipt_and_interrupted_replacement(self):
        self.start();self.plan('B',['b.md'])
        inputs=(self.service,'report','replace','new goal','','B')
        receipt=lc.proposal(*inputs)[0]['receipt'];root=self.store.root()
        with patch.object(self.store,'commit_heads',side_effect=OSError('interrupted')):
            with self.assertRaises(OSError):lc.apply(*inputs,receipt,'interrupted')
        self.assertEqual(root,self.store.root())
        self.decide('discard','B')
        with self.assertRaises(RecordError):lc.apply(*inputs,receipt,'stale')
        self.assertEqual('active',self.service.view('report')['state'])
        self.assertIsNone(self.store.head(lc.PREFIX+'report'))

    def test_archive_filters_cursor_and_machine_compatibility(self):
        self.start('A',['a.md']);(self.root/'a.md').write_text('result');review=self.submit('A')
        self.service.accept(work='A',operation='accept',receipt=review['receipt'],statement='ok')
        self.service.archive(work='A',operation='archive',archived=True)
        self.plan('B',['b.md']);self.decide('discard','B')
        self.plan('C',['c.md']);self.plan('D',['d.md'])
        args=parser(managed=True).parse_args(['ordinary','list'])
        ids=lambda v:[item['work'] for item in v['items']]
        self.assertEqual(ids(dispatch(args,self.store,self.workspace)),list('ABCD'))
        self.assertEqual(ids(dispatch(args,self.store,self.workspace,display=True)),list('CD'))
        page,cursor=page_heads(self.store,'work:',limit=1,mode='current')
        self.assertEqual(page[0][0],'work:C')
        with self.assertRaises(RecordError):page_heads(self.store,'work:',mode='archived',cursor=cursor)
        self.assertEqual(page_heads(self.store,'work:',mode='current',cursor=cursor)[0][0][0],'work:D')
        self.assertEqual(page_heads(self.store,'work:',mode='archived')[0][0][0],'work:A')
        self.service.archive(work='A',operation='unarchive',archived=False)
        self.assertEqual(self.service.view('A')['state'],'completed')


    def test_concurrent_target_change_and_file_change_preserve_work(self):
        self.start()
        self.plan('B',['b.md'])
        args=(self.service,'report','replace','new goal','','B')
        receipt=lc.proposal(*args)[0]['receipt']
        original=self.store.commit_heads
        work=self.store.head('work:report')
        def racing_commit(**kw):
            with patch.object(self.store,'commit_heads',original):
                self.decide('discard','B')
            return original(**kw)
        with patch.object(self.store,'commit_heads',side_effect=racing_commit):
            with self.assertRaisesRegex(RecordError,'lifecycle-preview-stale'):
                lc.apply(*args,receipt,'racing')
        self.assertEqual(work,self.store.head('work:report'))
        self.assertIsNone(self.store.head(lc.PREFIX+'report'))
        args=(self.service,'report','pause','stop','','')
        receipt=lc.proposal(*args)[0]['receipt']
        (self.root/'report.md').write_text('changed before confirmation')
        with self.assertRaisesRegex(RecordError,'lifecycle-preview-stale'):
            lc.apply(*args,receipt,'stale-file')
        self.assertEqual(work,self.store.head('work:report'))

    def test_parent_and_child_disposition_refused(self):
        from colvia.composition import CompositionService
        self.plan('parent',['p.md'])
        self.plan('child',['c.md'])
        CompositionService(self.service).declare(operation='bind',parent='parent',children=['child'],
            document='p.md',checks=['집계 대조'],statement='bind')
        for work in ('parent','child'):
            with self.assertRaisesRegex(RecordError,'lifecycle-independent-work-only'):
                self.decide('discard',work)

    def test_discard_approved_and_paused_work(self):
        p=self.plan()
        self.service.approve(work='report',operation='scope',receipt=p['receipt'],statement='ok')
        self.decide('discard')
        with self.assertRaises(RecordError):self.service.start(operation='late',work='report')
        self.start('B',['b.md'])
        self.decide('pause','B')
        self.decide('discard','B')
        with self.assertRaises(RecordError):self.decide('resume','B')
        self.assertEqual('discarded',self.service.view('B')['state'])

    def test_public_command_preview_and_list_are_read_only(self):
        from colvia.cli import command_readonly
        read=parser(managed=True).parse_args(['ordinary','lifecycle-preview','report','pause','--reason','break'])
        self.assertTrue(command_readonly(read))
        self.start()
        before=self.store.root().ref
        self.assertIn('receipt',dispatch(read,self.store,self.workspace))
        self.assertEqual(before,self.store.root().ref)
        self.assertEqual(self.store.requirements()['read'].count('schema:work.head:2'),0)

    def test_amended_edit_and_creation_observed_at_preview_apply_and_resume(self):
        (self.root/'table.md').write_text('original table')
        self.start()
        flags=('--edit','table.md','--create','appendix.md')
        self.approve(self.preview(*flags)['receipt'],*flags)
        args=(self.service,'report','pause','return later','','')
        preview=lc.proposal(*args)[0]
        self.assertEqual(set(preview['scope']),{'report.md','table.md','appendix.md'})
        (self.root/'appendix.md').write_text('new')
        with self.assertRaisesRegex(RecordError,'lifecycle-preview-stale'):
            lc.apply(*args,preview['receipt'],'stale')
        (self.root/'table.md').write_text('revised')
        preview=lc.proposal(*args)[0]
        self.assertEqual({entry['path']:entry['status'] for entry in preview['changes_from_plan']},
                         {'appendix.md':'created','table.md':'changed'})
        lc.apply(*args,preview['receipt'],'pause-edits')
        (self.root/'appendix.md').write_text('revised while paused')
        resume=(self.service,'report','resume','continue','','')
        shown=lc.proposal(*resume)[0]
        self.assertIn({'path':'appendix.md','status':'changed'},shown['since_pause'])
        (self.root/'table.md').write_text('later change')
        with self.assertRaisesRegex(RecordError,'lifecycle-preview-stale'):
            lc.apply(*resume,shown['receipt'],'stale-resume')

    def test_observation_cap_and_unreadable_path(self):
        from contextlib import contextmanager
        paths=['p%03d.md'%i for i in range(129)]
        self.start(scope=list(reversed(paths)))
        reader=self.workspace.selected_reader
        @contextmanager
        def controlled(**kwargs):
            with reader(**kwargs) as read:
                def read_one(selected,limit):
                    if selected==[paths[0]]:
                        raise RecordError('file-observation-changed')
                    return read(selected,limit)
                yield read_one
        args=(self.service,'report','pause','pause now','','')
        with patch.object(self.workspace,'selected_reader',controlled):
            shown=lc.proposal(*args)[0]
            self.assertEqual(1,shown['unobserved_paths'])
            self.assertEqual('unavailable',shown['files'][paths[0]])
            self.assertNotIn(paths[-1],shown['files'])
            lc.apply(*args,shown['receipt'],'limited')
            self.assertIn({'path':paths[0],'status':'unavailable'},self.service.view('report')['since_pause'])


class ExecutionBoundaryTests(unittest.TestCase):
    def test_prepared_execution_blocks_pause_and_paused_work_blocks_preparation(self):
        from test_foundation_execution_store import JournalFixture
        for prepared in (True, False):
            with self.subTest(prepared=prepared):
                fixture=JournalFixture()
                fixture.setUp()
                try:
                    args=(fixture.service,'synthetic-work','pause','break','','')
                    if prepared:
                        fixture.prepare()
                        with self.assertRaisesRegex(RecordError,'lifecycle-execution-prepared'):
                            lc.proposal(*args)
                    else:
                        lc.apply(*args,lc.proposal(*args)[0]['receipt'],'pause-execution-work')
                        with self.assertRaisesRegex(RecordError,'execution-active-work-required'):
                            fixture.prepare()
                finally:fixture.tearDown()
