"""Approved peer additions do not hide unrelated changes during rework."""
import unittest
from colvia.codec import RecordError
from colvia.records import link
from colvia.rework import attribution
from test_foundation_work import WorkFixture

class ReworkTests(WorkFixture,unittest.TestCase):
    def scenario(self):
        self.start();(self.root/'report.md').write_text('first')
        first=self.submit()
        self.start('other',('other.md',));(self.root/'other.md').write_text('other result');self.submit('other')
        self.service.revise(operation='revise',work='report',receipt=first['receipt'],statement='확인 날짜 한 줄만 추가해줘. 검토 제출까지 진행해.')
        (self.root/'report.md').write_text('first\ncheck date')
        return first

    def test_submitted_peer_addition_allows_same_work_resubmission(self):
        first=self.scenario();other=self.service.view('other');second=self.submit(operation='again')
        self.assertEqual('review',second['state']);self.assertTrue(second['current_matches'])
        result=self.result();self.assertEqual(2,result.ref.version);self.assertEqual(['report.md'],result.payload['changed'])
        self.assertEqual({'other.md'},set(attribution(result,self.store.load)))
        self.assertEqual('first',self.service.result_content('report','report.md',revision=1)['after']['text'])
        self.assertEqual(other,self.service.view('other'))
        with self.assertRaisesRegex(RecordError,'stale-result-receipt'):
            self.service.accept(operation='old',work='report',receipt=first['receipt'],statement='수락')

    def test_unsubmitted_addition_is_not_attributed(self):
        self.scenario();(self.root/'unknown.md').write_text('not submitted');before=self.store.root().ref
        with self.assertRaisesRegex(RecordError,'outside-scope-change'):self.submit(operation='blocked')
        self.assertEqual(before,self.store.root().ref)

    def test_peer_modified_after_submission_refuses(self):
        self.scenario();(self.root/'other.md').write_text('different')
        with self.assertRaisesRegex(RecordError,'outside-scope-change'):self.submit(operation='blocked')

    def test_original_outside_modification_refuses_even_with_known_peer(self):
        self.scenario();(self.root/'source.csv').write_text('outside')
        with self.assertRaisesRegex(RecordError,'outside-scope-change'):self.submit(operation='blocked')

    def test_carry_protects_later_deletion(self):
        self.scenario();second=self.submit(operation='again')
        self.service.revise(operation='again-revise',work='report',receipt=second['receipt'],statement='한 줄 더')
        (self.root/'report.md').write_text('third');(self.root/'other.md').unlink()
        with self.assertRaisesRegex(RecordError,'outside-scope-change'):self.submit(operation='third')

    def test_repeated_rework_carries_flat_map(self):
        self.scenario();second=self.submit(operation='again');proof=attribution(self.result(),self.store.load)
        self.service.revise(operation='again-revise',work='report',receipt=second['receipt'],statement='한 줄 더')
        (self.root/'report.md').write_text('third');self.submit(operation='third')
        self.assertEqual(proof,attribution(self.result(),self.store.load))
        self.assertEqual(3,self.result().payload['revision'])

    def test_missing_checks_cannot_admit_peer(self):
        self.scenario()
        checks = [dict(name='원본 보존', status='unavailable', detail='미확인')]
        before = self.store.root().ref
        with self.assertRaisesRegex(RecordError, 'check-report-mismatch'):
            self.service.submit(operation='incomplete', work='report', summary='내용', checks=checks)
        checks.append(dict(name='집계 대조', status='passed', detail='확인'))
        with self.assertRaisesRegex(RecordError, 'attribution-checks-required'):
            self.service.submit(operation='checks', work='report', summary='내용', checks=checks)
        self.assertEqual(before, self.store.root().ref)


    def test_new_service_reads_request_diff_and_current_block_without_writing(self):
        from colvia.work import WorkService
        from colvia.presentation import human
        self.scenario();(self.root/'unknown.md').write_text('unapproved')
        before=self.store.root().ref
        resumed=WorkService(self.store,self.workspace).view('report');context=resumed['rework']
        self.assertIn('확인 날짜',context['approved_request']);self.assertEqual(['report.md'],context['approved_scope'])
        self.assertEqual(['원본 보존','집계 대조'],context['checks'])
        self.assertEqual('retained-history-not-pending-review',context['last_submission_status'])
        self.assertEqual('not-established-by-this-read',context['check_execution_status'])
        self.assertEqual([dict(path='report.md',change='modification')],context['differences']['items'])
        self.assertEqual(['unknown.md'],[i['path'] for i in context['submission_check']['items']])
        self.assertIn('unknown.md',human(resumed));self.assertNotIn('plan-review',human(resumed))
        self.assertEqual(before,self.store.root().ref)
        # Fixture cleanup is not a recovery recommendation to a user.
        (self.root/'unknown.md').unlink()
        self.assertEqual('scope-checked',WorkService(self.store,self.workspace).view('report')['rework']['submission_check']['status'])
        self.assertEqual(before,self.store.root().ref)

    def test_current_diagnostic_cannot_hide_unavailable_observation(self):
        from unittest.mock import patch
        self.scenario()
        with patch.object(self.service,'_observe_from_plan',side_effect=RecordError('policy-changed')):
            result=self.service.view('report')['rework']
        self.assertEqual('unavailable',result['submission_check']['status'])
        self.assertNotIn('differences',result)

    def test_new_additions_after_first_attributed_revision_are_flat_and_protected(self):
        self.scenario();second=self.submit(operation='again')
        self.start('third',('third.md',));(self.root/'third.md').write_text('third work');self.submit('third')
        self.service.revise(operation='revise-third',work='report',receipt=second['receipt'],statement='또 한 줄')
        (self.root/'report.md').write_text('third report');self.submit(operation='third-report')
        self.assertEqual({'other.md','third.md'},set(attribution(self.result(),self.store.load)))

    def test_active_peer_and_instruction_addition_refuse(self):
        self.scenario();self.start('pending',('pending.md',));(self.root/'pending.md').write_text('not submitted')
        before=self.store.root().ref
        with self.assertRaisesRegex(RecordError,'outside-scope-change'):self.submit(operation='pending-block')
        self.assertEqual(before,self.store.root().ref)
        (self.root/'pending.md').unlink();(self.root/'AGENTS.md').write_text('new instruction')
        with self.assertRaises(RecordError):self.submit(operation='instruction-block')

    def test_peer_and_file_races_leave_work_active(self):
        from unittest.mock import patch
        self.scenario();peer=self.service.review('other');self.service.accept(operation='accept-peer',work='other',receipt=peer['receipt'],statement='수락');original=self.service._publish
        def changed_peer(*args,**kwargs):
            self.service.archive(operation='peer-archive',work='other',archived=True)
            return original(*args,**kwargs)
        # Archive is a real peer head change; the original bytes do not change.
        def wrapper(*args,**kwargs):
            if args[1]=='report':return changed_peer(*args,**kwargs)
            return original(*args,**kwargs)
        with patch.object(self.service,'_publish',side_effect=wrapper):
            with self.assertRaisesRegex(RecordError,'attribution-peer-changed'):self.submit(operation='peer-race')
        self.assertEqual('active',self.service.view('report')['state'])
        def changed_file(*args,**kwargs):
            (self.root/'other.md').write_text('unapproved modification')
            return original(*args,**kwargs)
        with patch.object(self.service,'_publish',side_effect=changed_file):
            with self.assertRaises(RecordError):self.submit(operation='file-race')
        self.assertEqual('active',self.service.view('report')['state'])

    def test_v2_content_checker_rejects_forged_attribution_and_changed_claim(self):
        from colvia.records import record,application_registry
        from colvia.maps import build_map
        self.scenario();self.submit(operation='again');result=self.result()
        original_links={name:(result.edges[indices[0]].role,result.edges[indices[0]].ref) if indices else ('provenance',None)
                        for name,indices in result.payload['links'].items()}
        for path in ('unknown.md','report.md'):
            forged_map=build_map([(path,next(iter(attribution(result,self.store.load).values())))])
            objects=dict(forged_map.objects);links=dict(original_links);links['attribution']=('decision',forged_map.root)
            ref,raw=record('work.submission',{k:v for k,v in result.payload.items() if k!='links'},links,version=2)
            objects[ref]=raw
            with self.assertRaises(RecordError):
                application_registry().content(ref,lambda r:objects[r] if r in objects else self.store.load(r))
        payload={k:v for k,v in result.payload.items() if k!='links'};payload['changed']=['other.md','report.md']
        ref,raw=record('work.submission',payload,original_links,version=2)
        with self.assertRaisesRegex(RecordError,'submission-change-mismatch'):
            application_registry().content(ref,lambda r:raw if r==ref else self.store.load(r))

    def test_v2_export_import_retains_bodies_and_old_reader_refuses(self):
        from io import BytesIO
        from pathlib import Path
        from colvia.graph import GraphAudit,AuditBudget,Registry
        from colvia.backup import write_export,ImportedSnapshot,ExportBudget,supported_requirements
        from colvia.records import application_registry
        from colvia.maps import map_get
        from colvia.bodies import body_bytes
        self.scenario();self.submit(operation='again');registry=application_registry()
        audit=GraphAudit(Path(self.tmp.name)/'audit.sqlite3',AuditBudget(10000,10000,32*1024*1024))
        try:
            audit.run(self.store.root().ref,self.store.load,registry)
            stream=BytesIO();write_export(stream,project=self.store.project,audit=audit,load=self.store.load)
        finally:audit.close()
        caps=supported_requirements(registry)
        incoming=ImportedSnapshot(Path(self.tmp.name)/'incoming.sqlite3',BytesIO(stream.getvalue()),
            budget=ExportBudget(10000,32*1024*1024),graph_budget=AuditBudget(10000,10000,32*1024*1024),
            registry=registry,capabilities=caps,writable_capabilities=caps)
        try:
            self.assertTrue(incoming.complete);self.assertTrue(incoming.writable)
            self.assertEqual(self.store.load(self.store.root().ref),incoming.load(self.store.root().ref))
        finally:incoming.close()
        result=self.result();body=map_get(link(result,'after'),'report.md',self.store.load)
        self.assertEqual(b'first\ncheck date',b''.join(body_bytes(body,self.store.load)))
        old=Registry(s for key,s in registry._schemas.items() if key!=('work.submission',2))
        audit=GraphAudit(Path(self.tmp.name)/'old-audit.sqlite3',AuditBudget(10000,10000,32*1024*1024))
        try:
            with self.assertRaisesRegex(RecordError,'unknown-required-kind'):
                audit.run(self.store.root().ref,self.store.load,old,require_known=True)
        finally:audit.close()

    def test_acceptance_git_selection_and_composition_capture_own_scope_only(self):
        from colvia.git_integration import GitIntegration
        from colvia.records import record,application_registry
        self.scenario();review=self.submit(operation='again')
        self.service.accept(operation='finish',work='report',receipt=review['receipt'],statement='수락')
        selected=GitIntegration(self.store,self.workspace,None)._selected(['report'])
        self.assertEqual({'report.md'},set(selected[1]));self.assertEqual({'report.md'},set(selected[2]))
        ref,head=self.service._head('report')
        cap,raw=record('composition.capture',dict(child='report'),{'plan':('decision',link(head,'plan')),
            'result':('decision',link(head,'result')),'decision':('decision',link(head,'decision')),'observed':('provenance',ref)})
        self.service._validate_capture(application_registry().inspect(cap,raw,required=True),self.store.load)

    def test_worker_v2_refuses_before_port_or_record_write(self):
        from types import SimpleNamespace
        from colvia.worker import WorkerService
        self.scenario();self.submit(operation='again');before=self.store.root().ref
        worker=object.__new__(WorkerService);worker.source=self.service;worker.store=self.store
        worker.destination=SimpleNamespace(workspace='different');worker.port_factory=lambda *a:self.fail('port invoked')
        with self.assertRaisesRegex(RecordError,'attributed-result-not-supported'):
            worker.prepare(operation='apply',application='application',work='report')
        self.assertEqual(before,self.store.root().ref)

    def test_delivery_prepare_pins_peer_before_effects(self):
        from colvia.delivery.service import DeliveryService
        from unittest.mock import patch
        import time
        self.scenario();peer=self.service.review('other');self.service.accept(operation='accept-peer',work='other',receipt=peer['receipt'],statement='수락');original=self.store.commit_heads
        def race(**kwargs):
            if kwargs['operation']=='prepare-delivery':self.service.archive(operation='archive-peer',work='other',archived=True)
            return original(**kwargs)
        with patch.object(self.store,'commit_heads',side_effect=race):
            with self.assertRaisesRegex(RecordError,'attribution-peer-changed'):
                DeliveryService(self.service).prepare(operation='prepare-delivery',delivery='one',work='report',action='submit',
                    deadline_ns=time.time_ns()+60*10**9,summary='ready',checks=[dict(name=n,status='passed',detail='checked') for n in ('원본 보존','집계 대조')])
        self.assertEqual('active',self.service.view('report')['state'])


    def test_v1_downgrade_cannot_remove_carried_protection(self):
        from colvia.records import record
        self.scenario();first=self.result();self.submit(operation='again');second=self.result()
        links={name:(first.edges[indices[0]].role,first.edges[indices[0]].ref) if indices else ('provenance',None)
               for name,indices in first.payload['links'].items()}
        links['previous']=('provenance',second.ref)
        payload={k:v for k,v in first.payload.items() if k!='links'};payload['revision']=3
        ref,raw=record('work.submission',payload,links)
        with self.assertRaisesRegex(RecordError,'attribution-protection-removed'):
            self.service.registry.inspect(ref,raw,required=True)

    def test_discovery_limit_refuses_without_authority_change(self):
        from unittest.mock import patch
        self.scenario();before=self.store.root().ref
        with patch('colvia.rework.MAX_HEADS',1):
            with self.assertRaisesRegex(RecordError,'attribution-discovery-limit'):self.submit(operation='limit')
        self.assertEqual(before,self.store.root().ref)

    def test_diagnostics_bound_output_and_name_only_offending_modification(self):
        from colvia.rework import SubmissionBlocked
        from colvia.presentation import human,failure
        items=[dict(path=f'file-{i}.md',change='addition') for i in range(35)]
        exc=SubmissionBlocked('outside-scope-change',items,'출처 확인 필요')
        self.assertEqual(30,len(exc.details['items']));self.assertEqual(5,exc.details['omitted'])
        shown=human(dict(error=exc.code,message=failure(exc.code),details=exc.details))
        self.assertIn('5개',shown);self.assertNotIn('file-34.md',shown)
        self.scenario();(self.root/'source.csv').write_text('unauthorized')
        with self.assertRaises(SubmissionBlocked) as blocked:self.submit(operation='bad-source')
        self.assertEqual(['source.csv'],[i['path'] for i in blocked.exception.details['items']])

    def test_prepared_delivery_submits_attributed_result_without_notification(self):
        from colvia.delivery.service import DeliveryService
        from test_foundation_delivery import EffectsDouble
        import time
        self.scenario();delivery=DeliveryService(self.service)
        prepared=delivery.prepare(operation='prepare-delivery',delivery='one',work='report',action='submit',
            deadline_ns=time.time_ns()+60*10**9,summary='ready',checks=[dict(name=n,status='passed',detail='checked') for n in ('원본 보존','집계 대조')])
        delivery.start(operation='start-delivery',delivery='one',receipt=prepared['receipt'],statement='합성 제출 승인')
        effects=EffectsDouble(self.root);delivery.claim(operation='claim-delivery',delivery='one',effects=effects)
        result=delivery.submit(operation='finish-delivery',delivery='one',effects=effects)
        self.assertEqual('finished',result['state']);self.assertEqual('review',self.service.view('report')['state'])
        self.assertEqual(2,self.result().ref.version);self.assertFalse(result['accepted'])

if __name__=='__main__':unittest.main()
