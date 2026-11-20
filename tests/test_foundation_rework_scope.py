"""A revision keeps its original decision, and cannot claim another Work's file."""
from unittest import TestCase
from unittest.mock import patch

from colvia import work_history, work_lifecycle
from colvia.codec import RecordError
from colvia.presentation import human
from colvia.records import link
from colvia.rework import SubmissionBlocked
from test_foundation_scope_addition import ScopeCommands
from test_foundation_work import WorkFixture


class ReworkScopeTests(ScopeCommands, WorkFixture, TestCase):
    def request_revision(self, accepted=False):
        self.start()
        self.note()
        (self.root/'report.md').write_text('first')
        result = self.submit()
        receipt = result['receipt']
        if accepted:
            self.service.accept(work='report', operation='accept-first', receipt=receipt, statement='수락합니다')
            receipt = self.service.view('report')['reopen_receipt']
        self.service.revise(work='report', operation='request', receipt=receipt, statement='근거를 보강해 주세요')

    def extend(self, path, *, edit=False):
        flags = ['--edit' if edit else '--create', path]
        preview = self.preview(*flags)
        self.assertIn('판 수정 요청', human(preview))
        self.approve(preview['receipt'], *flags, operation='add-' + path)
        return preview

    def lifecycle(self, action):
        args = (self.service, 'report', action, '자료 확인', '', '')
        preview = work_lifecycle.proposal(*args)[0]
        work_lifecycle.apply(*args, preview['receipt'], action)

    def test_multiple_grants_reopen_pause_and_three_revisions(self):
        self.request_revision(accepted=True)
        note = self.store.head('progress:report')
        stale = self.preview('--create', 'index.md')
        self.extend('appendix.md')
        with self.assertRaisesRegex(RecordError, 'scope-preview-stale'):
            self.approve(stale['receipt'], '--create', 'index.md')
        self.extend('index.md')
        self.lifecycle('pause')
        with self.assertRaisesRegex(RecordError, 'scope-first-submission-only'):
            self.preview('--create', 'other.md')
        self.lifecycle('resume')
        (self.root/'appendix.md').write_text('second')
        second = self.submit(operation='second')
        self.service.revise(work='report', operation='request-third', receipt=second['receipt'], statement='마지막 표 추가')
        self.extend('source.csv', edit=True)
        (self.root/'source.csv').write_text('third')
        third = self.submit(operation='third')
        self.service.accept(work='report', operation='accept-third', receipt=third['receipt'], statement='확인')
        self.assertEqual(note, self.store.head('progress:report'))
        self.assertEqual('first', self.service.result_content('report', 'report.md', revision=1)['after']['text'])
        with self.assertRaisesRegex(RecordError, 'path-not-in-work-scope'):
            self.service.result_content('report', 'appendix.md', revision=1)
        self.assertEqual('second', self.service.result_content('report', 'appendix.md', revision=2)['after']['text'])
        items = work_history.history(self.store, 'report')['items']
        self.assertEqual(3, sum(item['kind'] == 'scope' for item in items))
        self.assertEqual([3, 2, 1], [item['revision'] for item in items if item['kind'] == 'submit'])
        self.assertEqual([3, 1], [item['revision'] for item in items if item['kind'] == 'accept'])

    def test_peer_result_blocks_submission_after_archive(self):
        self.request_revision()
        self.extend('extra.md')
        self.start('peer', ('extra.md',))
        (self.root/'extra.md').write_text('peer result')
        review = self.submit('peer')
        self.service.accept(work='peer', operation='accept-peer', receipt=review['receipt'], statement='확인')
        self.service.archive(work='peer', operation='archive-peer', archived=True)
        before = self.store.root().ref
        with self.assertRaises(SubmissionBlocked) as blocked:
            self.submit(operation='second')
        self.assertEqual(blocked.exception.code, 'scope-peer-overlap')
        self.assertEqual(blocked.exception.details['items'][0]['peer_work'], 'peer')
        self.assertIn('extra.md', human(self.service.view('report')))
        self.assertEqual(before, self.store.root().ref)

    def test_peer_publication_between_scan_and_commit(self):
        self.request_revision()
        self.extend('extra.md')
        self.start('peer', ('extra.md',))
        (self.root/'extra.md').write_text('pending')
        before = self.store.head('work:report')
        publish = self.service._publish

        def race(*args, **kwargs):
            if args[1] == 'report':
                self.submit('peer')
            return publish(*args, **kwargs)

        with patch.object(self.service, '_publish', side_effect=race):
            with self.assertRaisesRegex(RecordError, 'attribution-heads-changed'):
                self.submit(operation='race')
        self.assertEqual(before, self.store.head('work:report'))
        self.assertEqual('review', self.service.view('peer')['state'])

    def test_carried_peer_proof_survives_an_unrelated_grant(self):
        self.request_revision()
        self.start('peer', ('peer.md',))
        (self.root/'peer.md').write_text('peer')
        self.submit('peer')
        second = self.submit(operation='second')
        self.service.revise(work='report', operation='request-again', receipt=second['receipt'], statement='더 고쳐 주세요')
        with self.assertRaisesRegex(RecordError, 'scope-peer-overlap'):
            self.preview('--edit', 'peer.md')
        self.extend('extra.md')
        (self.root/'extra.md').write_text('ours')
        result = self.submit(operation='third')
        self.assertEqual(result['files'], ['extra.md', 'report.md'])
        self.assertEqual('peer.md', result['attribution']['items'][0]['path'])

    def test_refuses_partial_peer_history_and_keeps_head(self):
        self.request_revision()
        self.extend('extra.md')
        self.plan('other', ('other.md',))
        before = self.store.root().ref
        with patch('colvia.scope_addition.MAX_HEADS', 0):
            with self.assertRaisesRegex(RecordError, 'scope-peer-read-limit'):
                self.submit(operation='uncertain')
        self.assertEqual(before, self.store.root().ref)

    def test_rejects_open_peer_before_approval_and_after_preview(self):
        self.request_revision()
        flags = ('--edit', 'source.csv')
        preview = self.preview(*flags)
        self.start('peer', ('source.csv',))
        before = self.store.root().ref
        with self.assertRaisesRegex(RecordError, 'scope-peer-overlap'):
            self.approve(preview['receipt'], *flags)
        self.assertEqual(before, self.store.root().ref)
        self.submit('peer')
        with self.assertRaisesRegex(RecordError, 'scope-peer-overlap'):
            self.preview(*flags)

    def test_later_separately_planned_peer_can_edit_accepted_file(self):
        self.request_revision()
        self.extend('shared.md')
        (self.root/'shared.md').write_text('accepted original')
        review = self.submit(operation='second')
        self.service.accept(work='report', operation='accept-second', receipt=review['receipt'], statement='확인')
        self.start('peer', ('shared.md',))
        (self.root/'shared.md').write_text('separately edited')
        self.submit('peer')
        old = self.service.result_content('report', 'shared.md', revision=2)
        self.assertEqual('accepted original', old['after']['text'])
        self.assertEqual('separately edited', self.service.result_content('peer','shared.md')['after']['text'])

    def test_peer_restoration_to_its_own_baseline_counts_as_a_change(self):
        (self.root/'report.md').write_text('first')
        shared = self.root/'source.csv'
        original = shared.read_bytes()
        self.start('peer', ('source.csv',))
        shared.write_text('accepted before our Work')
        peer = self.submit('peer')
        self.service.accept(work='peer', operation='peer-first', receipt=peer['receipt'], statement='확인')
        self.request_revision()
        self.extend('source.csv', edit=True)
        self.service.revise(work='peer', operation='peer-reopen',
                            receipt=self.service.view('peer')['reopen_receipt'], statement='원본 복원')
        shared.write_bytes(original)
        peer = self.submit('peer', operation='peer-second')
        self.assertEqual([], peer['files'])
        with self.assertRaisesRegex(SubmissionBlocked, 'scope-peer-overlap'):
            self.submit(operation='our-second')

    def test_approval_snapshot_must_match_its_published_operation(self):
        from colvia import scope_addition
        from colvia.records import record
        self.request_revision()
        self.extend('appendix.md')
        _,head = self.service._head('report')
        approval = self.service._object(link(head,'approval'))
        self.plan('peer', ('other.md',))
        snapshot = self.store.root()
        links = {name:(edge.role, edge.ref) for name, indices in approval.payload['links'].items()
                 for edge in [approval.edges[indices[0]]]}
        links['peer_heads'] = ('provenance',snapshot.heads)
        payload = {k:v for k,v in approval.payload.items() if k != 'links'}
        fake = record('work.approval', payload, links, version=3)
        alternate = self.service._object(fake[0], lambda _:fake[1])
        real = self.service._object
        with patch.object(self.service, '_object', side_effect=lambda ref: alternate if ref == approval.ref else real(ref)):
            with self.assertRaisesRegex(RecordError, 'scope-peer-history-uncertain'):
                scope_addition.check_peer_submissions(self.service, head, snapshot)

    def test_forged_heads_cannot_remove_or_exchange_a_returned_revision(self):
        from colvia.records import head_summary, record
        self.start()
        self.approve(self.preview('--create','early.md')['receipt'], '--create','early.md')
        earlier = self.service._head('report')[1]
        (self.root/'report.md').write_text('first')
        first = self.submit()
        self.service.revise(work='report', operation='request',receipt=first['receipt'],statement='출처 추가')
        self.extend('appendix.md')
        active = self.service._head('report')[1]
        (self.root/'appendix.md').write_text('appendix')
        second = self.submit(operation='second')
        self.service.revise(work='report', operation='again',receipt=second['receipt'],statement='다른 표 추가')
        self.extend('second.md')
        current = self.service._head('report')[1]
        self.lifecycle('pause')
        paused = self.service._head('report')[1]

        def refuse(template, replacements, phase=None):
            payload = {k:v for k,v in template.payload.items() if k!='links'}
            if phase:
                payload['phase'] = phase
            links = {name:('provenance' if name=='previous' else 'decision', replacements.get(name,link(template,name)))
                     for name in template.payload['links']}
            ref,raw = record('work.head',payload,links,version=template.ref.version)
            load = lambda r:raw if r==ref else self.store.load(r)
            with self.assertRaises(RecordError):
                head_summary(ref,load)
            with self.assertRaises(RecordError):
                self.service._validate_head(ref,load)
            if ref.version == 1 and link(template, 'approval').version == 3 and 'approval' not in replacements:
                with self.assertRaises(RecordError):
                    self.service.registry.content(ref,load)
        refuse(active, {'decision':None,'result':None})
        refuse(current, {'approval':link(earlier,'approval'),'plan':link(earlier,'plan')})
        swapped = {k:link(active,k) for k in ('result','decision')}
        refuse(current, swapped)
        refuse(paused, swapped)
        refuse(current, {}, phase='completed')

    def test_two_separately_approved_works_can_submit_in_reverse_order(self):
        self.request_revision()
        self.extend('shared.md')
        self.start('peer', ('shared.md',))
        (self.root/'shared.md').write_text('shared draft')
        self.submit(operation='our-second')
        self.submit('peer')
        for work, revision in [('report', 2), ('peer', 1)]:
            self.assertEqual('review', self.service.view(work)['state'])
            self.assertEqual('shared draft', self.service.result_content(work, 'shared.md', revision=revision)['after']['text'])
