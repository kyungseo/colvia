"""Read-path regressions across Work, its guarded store and live workspace."""
from dataclasses import replace
from hashlib import sha256
import unittest
from unittest.mock import patch

from colvia.bodies import validate_body
from colvia.codec import CHUNK_LIMIT, Edge, RecordError, encode_envelope, object_ref, verify_object
from colvia.observation import Policy, PolicySource
from colvia.records import application_registry, decode_policy
from colvia.storage import sqlite
from colvia.work import work_key
from colvia.workspace import observe
from test_foundation_work import WorkFixture


class PhaseBWorkTests(WorkFixture, unittest.TestCase):
    def test_approval_and_start_check_body_descriptors_accept_reads_full_bytes(self):
        file = self.root / 'source.csv'
        file.write_bytes(b'a' * CHUNK_LIMIT + b'b' * CHUNK_LIMIT)
        draft = self.plan(scope=('source.csv',))
        with patch.object(self.store, '_load', wraps=self.store._load) as loads, patch.object(
                self.store, '_chunk_identity', wraps=self.store._chunk_identity) as identities:
            self.service.approve(operation='approve', work='report', receipt=draft['receipt'], statement='yes')
            self.service.start(operation='start', work='report')
        self.assertTrue({call.args[0] for call in identities.call_args_list})
        self.assertFalse(any(call.args[0].kind == 'body.chunk' for call in loads.call_args_list))

        file.write_bytes(b'c' * CHUNK_LIMIT + b'd' * CHUNK_LIMIT)
        saved = self.submit()
        before = self.store.root().ref
        load = self.store._load

        def changed(ref, *args):
            if ref.kind == 'body.chunk':
                verify_object(ref, b'!' * ref.byte_length)
            return load(ref,*args)

        with patch.object(self.store, '_load', side_effect=changed), self.assertRaisesRegex(
                RecordError, 'object-identity-mismatch'):
            self.service.accept(operation='refused', work='report', receipt=saved['receipt'], statement='accept')
        self.assertEqual(before, self.store.root().ref)
        self.assertIsNone(self.store.operation_result('refused'))
        self.assertEqual('review', self.service.view('report')['state'])
        self.assertEqual('completed', self.service.accept(operation='accepted', work='report',
                                                         receipt=saved['receipt'], statement='accept')['state'])

    def test_work_view_closes_snapshot_before_live_files_and_rechecks_exact_head(self):
        self.start()
        (self.root/'report.md').write_text('new body\n')
        self.submit()
        selected = self.workspace.selected

        def changed(paths):
            self.assertFalse(self.store.db.in_transaction)
            original = self.store.head(work_key('report'))
            self.store.commit_heads(operation='change-head', expected={work_key('report'):original},
                                    changes={work_key('report'):None}, validate=lambda _: None)
            return selected(paths)

        with patch.object(self.workspace, 'selected', side_effect=changed), self.assertRaisesRegex(
                RecordError, 'work-view-changed'):
            self.service.view('report')

    def test_work_view_snapshot_budget_falls_back_before_live_files(self):
        self.start()
        (self.root/'report.md').write_text('new body\n')
        self.submit()
        selected = self.workspace.selected

        def check(paths):
            self.assertFalse(self.store.db.in_transaction)
            return selected(paths)

        with patch.object(sqlite._RecordSnapshot, '_bounded_load', side_effect=sqlite.SnapshotBudget), patch.object(
                self.workspace, 'selected', side_effect=check) as live:
            self.assertTrue(self.service.view('report')['current_matches'])
        live.assert_called_once()

    def test_middle_check_reuses_only_while_native_and_store_inputs_match(self):
        workspace = self.workspace
        with patch.object(workspace, '_verify', wraps=workspace._verify) as full:
            workspace.observe(reuse_middle=True)
        self.assertEqual(1, full.call_count)
        with patch.object(workspace, '_verify', wraps=workspace._verify) as full:
            workspace.observe()
        self.assertEqual(2, full.call_count)

        def stage_during_observation(*args, **kwargs):
            result = observe(*args, **kwargs)
            self.store.begin_import('write-during-observe', 'synthetic')
            return result

        with patch('colvia.workspace.observe', side_effect=stage_during_observation), patch.object(
                workspace, '_verify', wraps=workspace._verify) as full:
            workspace.observe(reuse_middle=True)
        self.assertEqual(2, full.call_count)

        def replace_locator(*args, **kwargs):
            result = observe(*args, **kwargs)
            self.locator = replace(self.locator, nonce='b'*64)
            return result

        with patch('colvia.workspace.observe', side_effect=replace_locator), self.assertRaisesRegex(
                RecordError, 'stale-or-foreign-binding'):
            workspace.observe(reuse_middle=True)

    def test_immutable_pages_bound_reads_and_close_before_return_or_store_write(self):
        self.plan()
        ref = self.store.head(work_key('report'))
        with patch.object(sqlite, '_PAGE_READS', 3), patch.object(
                self.store, '_transaction_inner', wraps=self.store._transaction_inner) as transactions:
            with self.store.immutable_reads():
                for _ in range(7):
                    self.store.load(ref)
                self.assertTrue(self.store.db.in_transaction)
                self.store.begin_import('after-page', 'synthetic')
                self.assertFalse(self.store.db.in_transaction)
                self.store.load(ref)
            self.assertFalse(self.store.db.in_transaction)
        self.assertEqual([False,False,False,True,False], [call.kwargs['write'] for call in transactions.call_args_list])

    def test_immutable_page_guard_detects_generation_drift_at_exit(self):
        self.plan()
        ref = self.store.head(work_key('report'))
        active = True

        def guard():
            if not active:
                raise RecordError('active-generation-changed')

        with patch.object(self.store, 'read_active_check', side_effect=guard), self.assertRaisesRegex(
                RecordError, 'active-generation-changed'):
            with self.store.immutable_reads():
                self.store.load(ref)
                active = False
        self.assertFalse(self.store.db.in_transaction)


    def test_cross_store_page_and_view_close_the_previous_read_transaction(self):
        self.plan()
        ref = self.store.head(work_key('report'))
        peer = sqlite.GenerationStore(self.store.path, project=self.store.project, instance=self.store.instance,
                                      generation=self.store.generation, readonly=True, active_check=lambda: None)
        try:
            with self.store.immutable_reads():
                self.store.load(ref)
                self.assertTrue(self.store.db.in_transaction)
                with peer.immutable_reads():
                    self.assertFalse(self.store.db.in_transaction)
                    peer.load(ref)
                    self.assertTrue(peer.db.in_transaction)
                    self.assertEqual(ref,self.store.head(work_key('report')))
                    self.assertFalse(peer.db.in_transaction)
                self.store.load(ref)
                self.assertEqual('planned',self.service.view('report')['state'])
                self.assertFalse(self.store.db.in_transaction)
        finally:
            peer.close()

    def test_descriptor_proof_cannot_satisfy_full_publication_in_same_operation(self):
        raw = b'protected synthetic content'
        chunk = object_ref('body.chunk',1,raw)
        body,described = encode_envelope('body.complete',1,dict(size=len(raw),sha256=sha256(raw).hexdigest(),
            links={'chunks':[0]}),(Edge('integrity',chunk),))
        self.store.begin_import('seed-body','synthetic')
        self.store.stage('seed-body',[(chunk,raw)])
        self.store.commit_heads(operation='publish-body',expected={'body':None},changes={'body':body},
            objects=[(body,described)],import_id='seed-body',validate=lambda load: validate_body(body,load))
        with patch.object(self.store,'_load',wraps=self.store._load) as loads:
            with self.store.reuse_operation_reads():
                with self.assertRaisesRegex(RecordError,'descriptor-only-cannot-import'):
                    self.store.commit_heads(operation='refused',expected={'body':body},changes={'body':body},
                        objects=[(body,described)],validate=lambda _:None,descriptor_only=True)
                self.store.commit_heads(operation='descriptor',expected={'body':body},changes={'body':body},
                    validate=lambda load:validate_body(body,load),descriptor_only=True)
                self.assertFalse(any(call.args[0]==chunk for call in loads.call_args_list))
                self.store.commit_heads(operation='full',expected={'body':body},changes={'body':body},
                    validate=lambda load:validate_body(body,load))
                self.assertTrue(any(call.args[0]==chunk for call in loads.call_args_list))


class PhaseBSmallCosts(unittest.TestCase):
    def test_policy_loaded_once_and_application_schema_reused_immutably(self):
        ref,raw = encode_envelope('observation.policy',1,dict(sources=[],config=[],tool='synthetic',links={'sources':[]}))
        seen=[]
        def load(target):
            seen.append(target)
            return raw

        self.assertEqual('synthetic',decode_policy(ref,load).tool)
        self.assertEqual([ref],seen)
        registry=application_registry()
        self.assertIs(registry,application_registry())
        with self.assertRaises(TypeError):
            registry._schemas[('observation.policy',1)].fields['extra']='decision'


    def test_start_policy_uses_exact_observed_prefix_without_reading_saved_chunks(self):
        raw = b"/existing/\n"
        digest = sha256(raw).hexdigest()
        chunk = object_ref('body.chunk',1,raw)
        body,described = encode_envelope('body.complete',1,dict(size=len(raw),sha256=digest,
            links={'chunks':[0]}),(Edge('integrity',chunk),))
        ref,policy = encode_envelope('observation.policy',1,dict(
            sources=[dict(origin='git:info/exclude',sha256=digest,size=len(raw))],
            config=[],tool='synthetic',links={'sources':[0]}),(Edge('integrity',body),))

        def load(target):
            if target==ref:
                return policy
            if target==body:
                return described
            self.fail('start read retained bytes despite a live exact policy prefix')

        observed = Policy((PolicySource('git:info/exclude',raw+b'/new-worktree/\n'),),(),'synthetic')
        self.assertEqual(raw,decode_policy(ref,load,observed=observed).sources[0].raw)
