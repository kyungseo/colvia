"""Pending external effects are writer barriers, including absent-head races."""
import unittest
from unittest.mock import patch
from colvia.codec import RecordError,encode_envelope
from colvia.effects import PENDING
from colvia.planning import Planning
from test_foundation_work import WorkFixture


class EffectBarrierTests(WorkFixture,unittest.TestCase):
    def setUp(self):
        super().setUp()
        # Only this test runtime knows the deliberately uninterpreted fixture.
        # Production capability admission remains unchanged.
        self.store.reader_capabilities |= {'schema:fixture.effect:1'}
        self.store.writer_capabilities |= {'schema:fixture.effect:1'}
    def reserve(self,operation='fixture-reserve'):
        # Trusted low-level injection deliberately avoids an application writer;
        # this tests admission even when pending kind cannot be interpreted.
        ref,raw=encode_envelope('fixture.effect',1,{'links':{}},())
        self.store.commit_heads(operation=operation,expected={PENDING:None},changes={PENDING:ref},objects=[(ref,raw)],validate=lambda view:None)
        return ref
    def test_pending_blocks_approval_but_keeps_status_readable(self):
        review=self.plan();self.reserve();before=self.store.root().ref
        with self.assertRaisesRegex(RecordError,'external-effect-pending'):
            self.service.approve(operation='approve',work='report',receipt=review['receipt'],statement='진행')
        self.assertEqual(before,self.store.root().ref);self.assertEqual('planned',self.service.view('report')['state'])
    def test_pending_blocks_submit_and_accept(self):
        self.start();(self.root/'report.md').write_bytes(b'result');self.reserve()
        with self.assertRaisesRegex(RecordError,'external-effect-pending'):self.submit()
        self.assertEqual('active',self.service.view('report')['state'])
    def test_pending_blocks_candidates_and_followup(self):
        self.plan();self.reserve();before=self.store.root().ref;p=Planning(self.store)
        with self.assertRaisesRegex(RecordError,'external-effect-pending'):
            p.save_candidate(operation='candidate',candidate='next',title='후속',reason='검토')
        with self.assertRaisesRegex(RecordError,'external-effect-pending'):
            p.choose_followup(operation='followup',work='report',choice='undecided',statement='미정')
        self.assertEqual(before,self.store.root().ref)
    def test_unconnected_store_cannot_connect_while_effect_pending(self):
        from pathlib import Path
        from colvia.storage.sqlite import GenerationStore
        from colvia.binding import ProjectBinding,Topology,WorkspaceRegistration
        from colvia.connection import Connections,PROJECT_KEY
        from colvia.platforms.posix import location
        fresh=GenerationStore.create(Path(self.tmp.name)/'unconnected.sqlite3',project=self.store.project,instance=self.store.instance,generation='g',active_check=lambda:None,reader_capabilities=self.store.reader_capabilities,writer_capabilities=self.store.writer_capabilities)
        try:
            ref,raw=encode_envelope('fixture.effect',1,{'links':{}},())
            fresh.commit_heads(operation='fixture-pending',expected={PENDING:None},changes={PENDING:ref},objects=[(ref,raw)],validate=lambda view:None)
            top=Topology('plain',location(self.root));before=fresh.root().ref
            with self.assertRaisesRegex(RecordError,'external-effect-pending'):
                Connections(fresh).connect(operation='cannot-connect',binding=ProjectBinding(self.locator,'plain',top.root),observed=top,
                    workspace=WorkspaceRegistration(self.workspace.workspace,top.root,None),verify_topology=lambda:top)
            self.assertEqual(before,fresh.root().ref);self.assertIsNone(fresh.head(PROJECT_KEY))
        finally:fresh.close()

    def test_reservation_after_absence_validation_prevents_commit(self):
        review=self.plan();commit=self.store.commit_heads
        ref,raw=encode_envelope('fixture.effect',1,{'links':{}},())
        def interleave(**kw):
            original=kw['validate']
            def validator(view):
                original(view)
                commit(operation='racing-reserve',expected={PENDING:None},changes={PENDING:ref},objects=[(ref,raw)],validate=lambda view:None)
            kw['validate']=validator
            return commit(**kw)
        with patch.object(self.store,'commit_heads',side_effect=interleave):
            with self.assertRaisesRegex(RecordError,'head-conflict'):
                self.service.approve(operation='approve',work='report',receipt=review['receipt'],statement='진행')
        self.assertEqual(ref,self.store.head(PENDING));self.assertEqual('planned',self.service.view('report')['state'])

if __name__=='__main__':unittest.main()
