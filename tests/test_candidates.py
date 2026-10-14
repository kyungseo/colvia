"""Planning behavior/authority/refusal tests. Runtime doubles are labelled; installed tests are separate."""
from __future__ import annotations
from test_productization_safety import verified_inventory_id
import copy
import json
import os
from pathlib import Path
import subprocess
import sys
import shutil
import unittest
from unittest.mock import patch

from hv2ref.candidates import CandidateStore, read_candidates, validate_store
from hv2ref.view import render_candidates
from hv2ref.errors import ContractError, InjectedCrash
from hv2ref.jsonio import canonical_json_bytes
from hv2ref.work import snapshot, record_ref, read_work, project_path
from hv2ref.intent import workspace_intents
import test_general_work_recovery as serial
import test_productization_safety as fixtures
import test_worktree_execution as worker_fixtures

TIME = serial.TIME


def proposal(target, action='add', cid='idea-a', *, request_id=None, payload=None):
    observed = read_candidates(target)
    if payload is None:
        payload = {'title': '후보 '+cid, 'purpose': '다음 일을 짧게 찾기', 'expected_effect': '보류 이유를 잃지 않음', 'related_candidates': []} if action in ('add', 'amend') else {}
    return {'record_type': 'candidate-request', 'schema_version': 1, 'authority_home_id': 'home-a', 'request_id': request_id or action+'-'+cid,
            'candidate_id': cid, 'action': action, 'expected_sha256': observed['sha256'], 'writer': 'agent:fixture', 'owner_statement': 'synthetic Owner request '+action,
            'reason': 'fixture: 명시적 선택/조건', 'observed_at': TIME, 'payload': payload}


def truth_bytes(target):
    return {str(p.relative_to(target)): p.read_bytes() for kind in ('intents','work') for p in (target/'.hrn'/kind).rglob('*') if p.is_file()}


class CandidateContractTests(unittest.TestCase):
    proposal=serial.SerialWriterTests.proposal
    publish=serial.SerialWriterTests.publish
    accept_intent=serial.SerialWriterTests.accept_intent
    submitted=serial.SerialWriterTests.submitted
    prepare=serial.SerialWriterTests.prepare
    apply=serial.SerialWriterTests.apply
    bytes=serial.SerialWriterTests.bytes
    def setUp(self):
        serial.SerialWriterTests.setUp(self)
        self.candidates=CandidateStore(self.target, lambda target:{'inventory_id':'entry-1','binding_ref':self.binding,'launcher_sha256':None})
    def act(self,action='add',cid='idea-a',**kw):
        return self.candidates.mutate(proposal(self.target,action,cid,**kw))
    def lines(self):
        return '\n'.join(render_candidates(self.target,works=self.store._all(),intents=workspace_intents(self.target))[0])

    def test_add_select_defer_resume_is_durable_and_does_not_create_work(self):
        before=truth_bytes(self.target);content=snapshot(self.target)
        for cid in ('a','b','c'):self.act(cid=cid)
        self.act('select','a');self.act('defer','b',payload={'resume_condition':'Owner가 다시 요청할 때'})
        fresh=read_candidates(self.target)['store'];self.assertEqual('a',fresh['selected']);self.assertEqual('deferred',fresh['candidates']['b']['disposition'])
        text=self.lines();self.assertIn('Owner가 다시 요청할 때',text);self.assertIn('실행 승인 아님',text)
        self.act('resume','b',payload={'condition_observation':'Owner가 명시적으로 재검토 요청'})
        after=read_candidates(self.target)['store'];self.assertEqual('a',after['selected']);self.assertEqual('open',after['candidates']['b']['disposition'])
        self.assertEqual(before,truth_bytes(self.target));self.assertEqual(content,snapshot(self.target))

    def test_duplicate_request_exact_retry_and_stale_parallel_request(self):
        r=proposal(self.target);other=proposal(self.target,cid='other')
        first=self.candidates.mutate(r);before=self.bytes()
        self.assertEqual('unchanged',self.candidates.mutate(r)['classification']);self.assertEqual(before,self.bytes())
        with self.assertRaisesRegex(ContractError,'STALE'):self.candidates.mutate(other)
        r['reason']='different'
        with self.assertRaisesRegex(ContractError,'different bytes'):self.candidates.mutate(r)
        self.assertEqual(before,self.bytes());self.assertEqual(1,len(first['store']['decisions']))

    def test_case_alias_duplicate_id_refused_and_related_candidate_preserved(self):
        self.act(cid='Idea');before=self.bytes()
        with self.assertRaises(ContractError):self.act(cid='idea')
        self.assertEqual(before,self.bytes())
        self.act(cid='other',payload={'title':'관련 아이디어','purpose':'기존과 별개 범위','expected_effect':'중복 여부 Owner 판단','related_candidates':['Idea']})
        self.assertEqual(['Idea'],read_candidates(self.target)['store']['candidates']['other']['related_candidates'])

    def test_select_replacement_defer_and_unknown_condition(self):
        self.act(cid='a');self.act(cid='b');self.act('select','a');self.act('select','b')
        d=read_candidates(self.target)['store']['decisions'][-1]
        self.assertEqual('a',d['before']['selected']);self.assertEqual('b',d['after']['selected'])
        self.act('defer','b',payload={'resume_condition':''});self.assertIsNone(read_candidates(self.target)['store']['selected'])
        self.assertIn('미정',self.lines())
        with self.assertRaises(ContractError):self.act('select','b',request_id='premature')

    def test_link_consumes_selection_and_work_defer_is_not_a_work_pause(self):
        self.act();self.act('select');self.submitted();g=read_work(self.target,'work-a')
        ref={'authority_home_id':'home-a','kind':'work','id':'work-a','revision_ref':g['selections'][g['current']['selection_ref']['id']]['revision_ref']}
        self.act('link',payload={'target':ref});before=truth_bytes(self.target)
        with self.assertRaisesRegex(ContractError,'linked to a Work'):self.act('defer',payload={'resume_condition':'later'})
        self.assertEqual(before,truth_bytes(self.target));self.assertIn('선택 소진',self.lines());self.assertIn('review',self.lines())
        self.apply(self.prepare());self.assertIn('completed',self.lines());self.assertIn('선택 소진',self.lines())
        with self.assertRaises(ContractError):self.act('select',request_id='reselect')

    def test_dangling_cross_home_and_wrong_digest_link_refused(self):
        self.act();self.submitted();g=read_work(self.target,'work-a')
        ref={'authority_home_id':'home-a','kind':'work','id':'work-a','revision_ref':g['selections'][g['current']['selection_ref']['id']]['revision_ref']}
        before=self.bytes()
        for change in ('home','id','digest'):
            r=copy.deepcopy(ref)
            if change=='home':r['authority_home_id']='foreign'
            elif change=='id':r['id']='missing'
            else:r['revision_ref']['sha256']='0'*64
            with self.subTest(change=change),self.assertRaises(ContractError):self.act('link',payload={'target':r})
            self.assertEqual(before,self.bytes())

    def test_links_cannot_mix_work_and_different_accepted_intent_revision(self):
        self.act(cid='a');self.act(cid='b');self.submitted();g=read_work(self.target,'work-a')
        work={'authority_home_id':'home-a','kind':'work','id':'work-a','revision_ref':g['selections'][g['current']['selection_ref']['id']]['revision_ref']}
        self.act('link','a',payload={'target':work})
        second=self.accept_intent(2);intent={k:second[k] for k in ('authority_home_id','kind','id','revision_ref')}
        before=self.bytes()
        with self.assertRaisesRegex(ContractError,'another intent revision'):self.act('link','a',request_id='intent-a',payload={'target':intent})
        self.assertEqual(before,self.bytes());self.act('link','b',payload={'target':intent});before=self.bytes()
        with self.assertRaisesRegex(ContractError,'linked intent revision'):self.act('link','b',request_id='work-b',payload={'target':work})
        self.assertEqual(before,self.bytes())

    def test_reject_reopen_and_amend_keep_history_without_authority(self):
        self.act();self.act('disposition',payload={'disposition':'rejected','target':None});old=read_candidates(self.target)['store']['decisions']
        self.act('reopen');self.act('amend',payload={'title':'수정','purpose':'다른 설명','expected_effect':'명확화','related_candidates':[]})
        g=read_candidates(self.target)['store'];self.assertEqual(old,g['decisions'][:len(old)]);self.assertEqual('open',g['candidates']['idea-a']['disposition']);self.assertEqual({},self.store._all())

    def test_successful_candidate_writes_preserve_submitted_acceptance_and_real_content_guard(self):
        self.submitted();ticket=self.prepare();truth=truth_bytes(self.target);content=snapshot(self.target)
        self.act();self.act('select');self.act('defer',payload={'resume_condition':'later'})
        self.assertEqual(truth,truth_bytes(self.target));self.assertEqual(content,snapshot(self.target))
        (self.target/'a').write_text('outside mutation\n')
        with self.assertRaises(ContractError):self.apply(ticket)
        (self.target/'a').write_bytes(b'after\n');self.assertEqual('completed',self.apply(ticket)['state'])

    def test_interrupted_candidate_writes_do_not_block_original_exact_acceptance(self):
        for point in ('after-temporary','after-directory','before-replace','after-replace'):
            if hasattr(self, "intent"): del self.intent
            self.setUp();self.submitted();ticket=self.prepare();truth=truth_bytes(self.target)
            r=proposal(self.target,cid=point)
            with self.subTest(point=point),self.assertRaises(InjectedCrash):self.candidates.mutate(r,inject_at=point)
            self.assertEqual(truth,truth_bytes(self.target))
            # The original ticket remains prepare/apply-valid even with candidate scratch.
            self.assertEqual('completed',self.apply(ticket)['state'])
            self.candidates.mutate(r)

    def test_pending_work_refuses_candidate_write_and_exact_recovery_still_works(self):
        self.submitted();ticket=self.prepare()
        with self.assertRaises(InjectedCrash):self.apply(ticket,inject_at='after-decision')
        before=self.bytes()
        with self.assertRaisesRegex(ContractError,'PENDING'):self.act()
        self.assertEqual(before,self.bytes());self.assertEqual('completed',self.apply(ticket)['state'])

    def test_corrupt_unknown_history_projection_and_merge_conflict_never_become_empty(self):
        self.act();path=self.target/'.hrn/planning/candidates.json';original=path.read_bytes()
        variants=[b'<<<<<<< branch\n',b'{}\n',canonical_json_bytes({'record_type':'candidate-planning','schema_version':1,'authority_home_id':'home-a','candidates':{},'selected':None,'decisions':[]})]
        for field,value in [('schema_version',2),('schema_version',True),('authority_home_id','other'),('selected','fake'),('extra',True)]:
            d=json.loads(original);d[field]=value;variants.append(canonical_json_bytes(d))
        for data in variants:
            path.write_bytes(data)
            with self.subTest(data=data[:30]),self.assertRaises(ContractError):read_candidates(self.target)
            self.assertEqual(data,path.read_bytes())
        path.write_bytes(original)

    def test_linked_and_unsafe_planning_paths_refuse_without_overwriting(self):
        self.act();path=self.target/'.hrn/planning/candidates.json';old=path.read_bytes();outside=self.target.parent/'outside';path.rename(outside)
        path.symlink_to(outside)
        with self.assertRaises(ContractError):read_candidates(self.target)
        self.assertEqual(old,outside.read_bytes());path.unlink();os.link(outside,path)
        with self.assertRaises(ContractError):read_candidates(self.target)
        self.assertEqual(old,outside.read_bytes())

    def test_read_view_is_byte_immutable_and_escapes_untrusted_prose(self):
        self.act(payload={'title':'<script>\x1b[31m **태그**','purpose':'[link](https://example.invalid)','expected_effect':'확인','related_candidates':[]})
        before=self.bytes();text=self.lines();self.assertEqual(before,self.bytes())
        self.assertNotIn('<script>',text);self.assertNotIn('\x1b',text);self.assertIn('&lt;script&gt;',text)

    def test_planning_path_cannot_be_a_work_input_or_result(self):
        for path in ('.hrn/planning/candidates.json','.HRN/planning/candidates.json'):
            with self.assertRaises(ContractError):project_path(path)

    def test_limit_refusals_are_unchanged_and_not_silent_compaction(self):
        self.act();before=self.bytes()
        with patch('hv2ref.candidates.MAX_CANDIDATES',1):
            with self.assertRaisesRegex(ContractError,'LIMIT'):self.act(cid='second')
        with patch('hv2ref.candidates.MAX_DECISIONS',1):
            with self.assertRaisesRegex(ContractError,'LIMIT'):self.act('select')
        with patch('hv2ref.candidates.MAX_BYTES',len((self.target/'.hrn/planning/candidates.json').read_bytes())+1):
            with self.assertRaisesRegex(ContractError,'LIMIT'):self.act('select')
        self.assertEqual(before,self.bytes())

    def test_empty_checkout_explains_branch_boundary(self):
        before=self.bytes();self.assertIn('다른 branch일 수 있습니다',self.lines());self.assertEqual(before,self.bytes())


    def test_after_replace_retry_pending_reports_prior_publication_truthfully(self):
        self.submitted();ticket=self.prepare();request=proposal(self.target)
        with self.assertRaises(InjectedCrash):self.candidates.mutate(request,inject_at='after-replace')
        with self.assertRaises(InjectedCrash):self.apply(ticket,inject_at='after-decision')
        before=self.bytes()
        with self.assertRaisesRegex(ContractError,'this call made no new write; read planning'):
            self.candidates.mutate(request)
        self.assertEqual(before,self.bytes())
        self.assertEqual(request,read_candidates(self.target)['store']['decisions'][0]['request'])
        self.assertEqual('completed',self.apply(ticket)['state'])
        self.assertEqual('unchanged',self.candidates.mutate(request)['classification'])

    def test_historical_cas_digest_is_not_a_verified_prefix_chain(self):
        self.act(cid='a');self.act(cid='b')
        path=self.target/'.hrn/planning/candidates.json';store=read_candidates(self.target)['store']
        store['decisions'][1]['request']['expected_sha256']='0'*64
        # An internally consistent manually edited history is accepted: an explicit limit,
        # not evidence of tamper detection. Live writer CAS still has separate tests.
        path.write_bytes(canonical_json_bytes(store));before=self.bytes()
        self.assertEqual(store,read_candidates(self.target)['store']);self.assertEqual(before,self.bytes())

    def test_deferred_work_link_shows_work_not_unusable_candidate_resume(self):
        self.act();self.act('defer',payload={'resume_condition':'old condition'})
        self.submitted();g=read_work(self.target,'work-a')
        ref={'authority_home_id':'home-a','kind':'work','id':'work-a','revision_ref':g['selections'][g['current']['selection_ref']['id']]['revision_ref']}
        self.act('link',payload={'target':ref});text=self.lines()
        self.assertIn('deferred',text);self.assertIn('review',text);self.assertNotIn('재개 조건:',text)
        before=self.bytes()
        with self.assertRaises(ContractError):self.act('resume',payload={'condition_observation':'requested'})
        self.assertEqual(before,self.bytes())

    def test_old_checkout_candidate_writer_refuses_without_publication(self):
        self.candidates.runtime=lambda target:{'inventory_id':'checkout-1','binding_ref':self.binding,'launcher_sha256':None}
        before=self.bytes();shape=fixtures.exact_snapshot(self.target)
        with self.assertRaises(ContractError) as error:self.act()
        self.assertEqual('HV2-CANDIDATE-WINDOW',error.exception.code)
        # This runtime double can create only the shared guard's exact scratch anchors.
        self.assertEqual({**before,'.hrn/locks/writer.lock':b''},self.bytes())
        after=fixtures.exact_snapshot(self.target)
        self.assertEqual(shape,{path:value for path,value in after.items() if path in shape})
        self.assertEqual({'.hrn/locks','.hrn/locks/writer.lock'},set(after)-set(shape))
        self.assertEqual(('directory',0o755),after['.hrn/locks'])
        lock=self.target/'.hrn/locks/writer.lock'
        self.assertFalse(lock.is_symlink());self.assertTrue(lock.is_file())
        self.assertEqual(0o600,lock.lstat().st_mode&0o777)
        self.assertEqual(1,lock.lstat().st_nlink)
        self.assertFalse((self.target/'.hrn/planning').exists())


class InstalledCandidateTests(unittest.TestCase):
    """Unmodified current managed launcher; separate from the unit runtime doubles."""
    TIME=fixtures.ActualWorkspaceInitTests.TIME
    call=fixtures.ActualWorkspaceInitTests.call
    preview=fixtures.ActualWorkspaceInitTests.preview
    apply_init=fixtures.ActualWorkspaceInitTests.apply_init
    installed=fixtures.ActualWorkspaceInitTests.installed
    draft=fixtures.ActualWorkspaceInitTests.draft
    accept_intent=fixtures.ActualWorkspaceInitTests.accept_intent
    complete_work=fixtures.ActualWorkspaceInitTests.complete_work
    def setUp(self):
        fixtures.ActualWorkspaceInitTests.setUp(self)
        self.apply_init(self.preview())
    def act(self,action='add',cid='idea-a',**kw):
        r=proposal(self.target,action,cid,**kw)
        return json.loads(self.installed(['candidate',action],r).stdout)
    def test_installed_three_candidates_select_defer_resume_and_read_only_fresh_process(self):
        for cid in ('a','b','c'):self.act(cid=cid)
        self.act('select','a');self.act('defer','b',payload={'resume_condition':'Owner 요청 뒤 재검토'})
        before=fixtures.exact_snapshot(self.target)
        text=self.installed(['view','candidates']).stdout.decode()
        self.assertIn('Owner 요청 뒤 재검토',text);self.assertIn('발화 근거',text);self.assertIn('intent 구체화',text)
        self.assertEqual(before,fixtures.exact_snapshot(self.target))
        self.act('resume','b',payload={'condition_observation':'Owner 명시적 재검토 요청'})
        self.assertEqual('a',read_candidates(self.target)['store']['selected'])
        self.assertIn('후보 계획',self.installed(['view']).stdout.decode())
    def test_installed_command_mismatch_and_source_writer_are_refused(self):
        before=fixtures.exact_snapshot(self.target)
        self.installed(['candidate','select'],proposal(self.target),expected=65)
        self.call(['candidate','add','--target',self.target],proposal(self.target),expected=2)
        self.assertEqual(before,fixtures.exact_snapshot(self.target))
    def test_installed_selection_link_completion_and_no_auto_work(self):
        self.act();self.act('select');self.assertEqual({},read_work_map(self.target))
        intent=self.accept_intent();self.act('link',payload={'target':{k:intent[k] for k in ('authority_home_id','kind','id','revision_ref')}})
        self.complete_work(intent_ref=intent)
        g=read_work(self.target,'work-a');ref={'authority_home_id':'home-a','kind':'work','id':'work-a','revision_ref':g['selections'][g['current']['selection_ref']['id']]['revision_ref']}
        self.act('link',payload={'target':ref},request_id='link-work')
        text=self.installed(['view','candidates']).stdout.decode();self.assertIn('completed',text);self.assertIn('선택 소진',text)
        self.installed(['candidate','defer'],proposal(self.target,'defer',payload={'resume_condition':'later'}),expected=65)
    def test_installed_missing_work_link_reports_existing_work_without_creation_prompt(self):
        self.act();self.act('select');intent=self.accept_intent()
        self.act('link',payload={'target':{k:intent[k] for k in ('authority_home_id','kind','id','revision_ref')}})
        self.complete_work(intent_ref=intent);before=fixtures.exact_snapshot(self.target)
        text=self.installed(['view','candidates']).stdout.decode()
        self.assertIn('work-a',text);self.assertIn('completed',text);self.assertIn('후보 연결 미완료',text)
        self.assertNotIn('Work 준비',text);self.assertEqual(before,fixtures.exact_snapshot(self.target))
        self.assertFalse(any(r['kind']=='work' for r in read_candidates(self.target)['store']['candidates']['idea-a']['links']))

    def test_installed_planning_failure_keeps_work_readable_but_writes_refused(self):
        self.act();self.complete_work();request=proposal(self.target,cid='b')
        path=self.target/'.hrn/planning/candidates.json';original=path.read_bytes()
        for variant in ('malformed','unknown-member'):
            with self.subTest(variant=variant):
                path.write_bytes(b'<<<<<<< branch\n' if variant=='malformed' else original)
                extra=self.target/'.hrn/planning/.DS_Store'
                if variant=='unknown-member':extra.write_bytes(b'unknown')
                before=fixtures.exact_snapshot(self.target)
                status=json.loads(self.installed(['status'],expected=14).stdout)
                self.assertEqual('partial',status['classification']);self.assertFalse(status['planning']['available'])
                self.assertNotIn('candidate_count',status['planning']);self.assertEqual('completed',status['work_states']['work-a'])
                for args in (['view'],['view','work','work-a'],['view','candidates']):
                    text=self.installed(args,expected=14).stdout.decode()
                    self.assertIn('후보 계획 — 확인 불가',text);self.assertNotIn('후보 기록이 없습니다',text)
                    if args!=['view','candidates']:self.assertIn('completed',text)
                self.installed(['candidate','add'],request,expected=65)
                self.installed(['detach','--operation-id','bad-plan','--observed-at',TIME],expected=65)
                self.assertEqual(before,fixtures.exact_snapshot(self.target))
                if extra.exists():extra.unlink()
        path.write_bytes(original)

    def test_installed_unaccepted_intent_draft_cannot_be_linked(self):
        self.act();draft=self.draft();self.installed(['intent','draft'],draft)
        target={'authority_home_id':'home-a','kind':'intent','id':'intent-a','revision_ref':record_ref(draft,'revision_id')}
        before=fixtures.exact_snapshot(self.target)
        result=self.installed(['candidate','link'],proposal(self.target,'link',payload={'target':target}),expected=65)
        self.assertIn(b'current selected/accepted',result.stdout+result.stderr)
        self.assertEqual(before,fixtures.exact_snapshot(self.target))

    def test_installed_detach_preserves_planning_and_independent_view(self):
        self.act();before=(self.target/'.hrn/planning/candidates.json').read_bytes()
        self.installed(['candidate','add','--inject-at','after-temporary'],proposal(self.target,cid='interrupted'),expected=75)
        residue=list((self.target/'.hrn/staging').glob('candidate-*'));self.assertTrue(residue)
        residue_bytes={p:p.read_bytes() for p in residue}
        p=json.loads(self.installed(['detach','--operation-id','detach-candidate','--observed-at',TIME]).stdout)
        self.assertIn('planning/candidates.json',[r['path'] for r in p['request']['truth_refs']])
        self.installed(['detach','--apply','--input','-','--confirm',p['confirm_token']],p['request'])
        self.assertEqual(before,(self.target/'.hrn/planning/candidates.json').read_bytes())
        text=self.call(['view','candidates','--target',self.target]).stdout.decode();self.assertIn('후보 idea-a',text)
        plain=subprocess.run([sys.executable,'-I','-B',str(self.source/'tests/fixtures/product_plain_auditor.py'),str(self.target)],capture_output=True,timeout=30)
        self.assertEqual(0,plain.returncode,plain.stdout+plain.stderr)
        self.assertEqual('detached',json.loads(plain.stdout)['classification'])
        self.assertEqual(residue_bytes,{p:p.read_bytes() for p in residue})
    def test_lifecycle_preview_drift_refuses_without_losing_plan(self):
        self.act();p=json.loads(self.installed(['detach','--operation-id','detach-stale','--observed-at',TIME]).stdout)
        self.act('select');before=fixtures.exact_snapshot(self.target)
        self.installed(['detach','--apply','--input','-','--confirm',p['confirm_token']],p['request'],expected=65)
        self.assertEqual(before,fixtures.exact_snapshot(self.target))


def read_work_map(target):
    from hv2ref.work import WorkStore
    return WorkStore(target)._all()


class InstalledCandidateNoninterferenceTests(unittest.TestCase):
    setUp=fixtures.ActualWorkspaceInitTests.setUp
    TIME=fixtures.ActualWorkspaceInitTests.TIME
    call=worker_fixtures.InstalledWorkerPublicationTests.call
    preview=fixtures.ActualWorkspaceInitTests.preview
    apply_init=fixtures.ActualWorkspaceInitTests.apply_init
    draft=fixtures.ActualWorkspaceInitTests.draft
    accept_intent=fixtures.ActualWorkspaceInitTests.accept_intent
    complete_work=fixtures.ActualWorkspaceInitTests.complete_work
    prepare_worker_result=worker_fixtures.InstalledWorkerPublicationTests.prepare_worker_result
    git=worker_fixtures.InstalledWorkerPublicationTests.git
    act=InstalledCandidateTests.act

    def installed(self,args,value=None,**kw):
        if getattr(self,'intercept',False) and args[:2]==['work','apply']:
            self.prepared=(args,value);raise StopBeforeApply()
        result=fixtures.ActualWorkspaceInitTests.installed(self,args,value,**kw)
        if getattr(self,'note_while_editing',False) and args[:2]==['work','publish'] and value['revision']['operation']=='start':
            before=truth_bytes(self.target);self.act(cid='editing-note');self.assertEqual(before,truth_bytes(self.target))
        return result

    def submitted_local(self):
        self.git(self.target,'init','-q');self.git(self.target,'config','user.name','Fixture');self.git(self.target,'config','user.email','fixture@example.invalid')
        self.apply_init(self.preview())
        self.intercept=True
        try:
            with self.assertRaises(StopBeforeApply):self.complete_work()
        finally:self.intercept=False
        return self.prepared

    def test_installed_serial_each_interruption_preserves_exact_acceptance_and_record_commit(self):
        from hv2ref.product import verify_workspace_product
        for point in ('after-temporary','after-directory','before-replace','after-replace'):
            with self.subTest(point=point):
                self.setUp();self.note_while_editing=(point=='after-temporary');args,ticket=self.submitted_local()
                sha=verify_workspace_product(self.target)['launcher_sha256'];content=snapshot(self.target,verified_launcher_sha256=sha, verified_inventory_id=verified_inventory_id(self.target));truth=truth_bytes(self.target)
                self.act();self.act('select');self.act('defer',payload={'resume_condition':'later'})
                req=proposal(self.target,cid='interrupted')
                self.installed(['candidate','add','--inject-at',point],req,expected=75)
                self.assertEqual(truth,truth_bytes(self.target));self.assertEqual(content,snapshot(self.target,verified_launcher_sha256=sha, verified_inventory_id=verified_inventory_id(self.target)))
                self.git(self.target,'add','.hrn');self.git(self.target,'commit','-qm','fixture: planning records\n\nCo-authored-by: Codex <noreply@openai.com>')
                self.assertEqual('completed',json.loads(self.installed(args,ticket).stdout)['state'])
                self.installed(['candidate','add'],req)
                self.assertIn('interrupted',read_candidates(self.target)['store']['candidates'])

    def test_installed_worker_each_interruption_preserves_apply_and_planning_bytes(self):
        from hv2ref.product import verify_workspace_product
        for point in ('after-temporary','after-directory','before-replace','after-replace'):
            with self.subTest(point=point):
                self.setUp();self.note_while_editing=(point=='after-temporary');prepared=self.prepare_worker_result();sha=verify_workspace_product(self.target)['launcher_sha256']
                truth=truth_bytes(self.target);content=snapshot(self.target,verified_launcher_sha256=sha, verified_inventory_id=verified_inventory_id(self.target))
                self.act();self.act('select');self.act('defer',payload={'resume_condition':'later'})
                req=proposal(self.target,cid='interrupted')
                self.installed(['candidate','add','--inject-at',point],req,expected=75)
                self.assertEqual(truth,truth_bytes(self.target));self.assertEqual(content,snapshot(self.target,verified_launcher_sha256=sha, verified_inventory_id=verified_inventory_id(self.target)))
                plan=(self.target/'.hrn/planning/candidates.json').read_bytes()
                self.git(self.target,'add','.hrn');self.git(self.target,'commit','-qm','fixture: planning records\n\nCo-authored-by: Codex <noreply@openai.com>')
                args=['work','apply','--confirm',prepared['confirm_token']]
                # Real content still cannot be waived by planning.
                (self.target/'a').write_bytes(b'unreviewed drift\n')
                self.installed(args,prepared['ticket'],expected=65);(self.target/'a').write_bytes(b'before\n')
                self.assertEqual('completed',json.loads(self.installed(args,prepared['ticket']).stdout)['state'])
                self.assertEqual(plan,(self.target/'.hrn/planning/candidates.json').read_bytes());self.assertEqual(b'installed worker result\n',(self.target/'a').read_bytes())
                self.installed(['candidate','add'],req)
                before=fixtures.exact_snapshot(self.target)
                self.call(['candidate','add','--target',self.target],proposal(self.target,cid='worker-idea'),launcher=self.base/'worker/colvia',expected=65)
                self.assertEqual(before,fixtures.exact_snapshot(self.target))

    def test_installed_two_processes_same_digest_one_wins_one_stale(self):
        self.apply_init(self.preview());requests=[proposal(self.target,cid=k) for k in ('a','b')];children=[]
        try:
            for request in requests:
                p=subprocess.Popen([sys.executable,'-I','-B',str(self.target/'colvia'),'candidate','add'],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,cwd=self.target)
                p.stdin.write(canonical_json_bytes(request));p.stdin.close();p.stdin=None;children.append(p)
            results=[(p.returncode,out,err) for p in children for out,err in [p.communicate(timeout=60)]]
            self.assertEqual([0,65],sorted(code for code,_,_ in results),results)
            loser=next(json.loads(out) for code,out,_ in results if code==65);self.assertEqual('HV2-CANDIDATE-STALE',loser['code'])
            self.assertEqual(1,len(read_candidates(self.target)['store']['decisions']))
        finally:
            for p in children:
                if p.poll() is None:p.kill();p.wait(timeout=5)

    def test_clone_discovery_divergent_branches_and_conflict_preserve_both(self):
        self.git(self.target,'init','-q');self.git(self.target,'config','user.name','Fixture');self.git(self.target,'config','user.email','fixture@example.invalid')
        self.apply_init(self.preview());self.git(self.target,'add','.');self.git(self.target,'commit','-qm','fixture: initial\n\nCo-authored-by: Codex <noreply@openai.com>');self.git(self.target,'branch','before-planning');original_branch=self.git(self.target,'branch','--show-current')
        self.act();self.git(self.target,'add','.hrn');self.git(self.target,'commit','-qm','fixture: candidate\n\nCo-authored-by: Codex <noreply@openai.com>')
        clone=self.base/'clone';self.git(self.target,'clone','--no-local',str(self.target),str(clone))
        self.assertEqual(read_candidates(self.target)['store'],read_candidates(clone)['store'])
        self.git(self.target,'checkout','-q','before-planning');self.assertIn('다른 branch일 수 있습니다',self.installed(['view','candidates']).stdout.decode())
        self.act(cid='other');self.git(self.target,'add','.hrn');self.git(self.target,'commit','-qm','fixture: divergent candidate\n\nCo-authored-by: Codex <noreply@openai.com>')
        # Both complete histories have durable refs; perform a real add/add Git merge conflict.
        p=self.target/'.hrn/planning/candidates.json';right=(clone/'.hrn/planning/candidates.json').read_bytes()
        merged=subprocess.run(['git','-C',str(self.target),'merge','--no-edit',original_branch],capture_output=True,timeout=30)
        self.assertEqual(1,merged.returncode,merged.stdout+merged.stderr);self.assertIn(b'<<<<<<<',p.read_bytes());before=fixtures.exact_snapshot(self.target)
        self.installed(['view','candidates'],expected=14)
        self.installed(['candidate','add'],requests_for_conflict(),expected=65)
        self.assertEqual(before,fixtures.exact_snapshot(self.target));self.assertEqual(right,(clone/'.hrn/planning/candidates.json').read_bytes())


class StopBeforeApply(Exception):pass

def requests_for_conflict():
    return {'record_type':'candidate-request','schema_version':1,'authority_home_id':'home-a','request_id':'conflicted','candidate_id':'c','action':'select','expected_sha256':'a'*64,'writer':'fixture','owner_statement':'synthetic','reason':'synthetic','observed_at':TIME,'payload':{}}


class CandidateLifecycleTests(unittest.TestCase):
    setUp=InstalledCandidateTests.setUp
    TIME=fixtures.ActualWorkspaceInitTests.TIME
    call=worker_fixtures.InstalledWorkerPublicationTests.call
    preview=fixtures.ActualWorkspaceInitTests.preview
    apply_init=fixtures.ActualWorkspaceInitTests.apply_init
    installed=fixtures.ActualWorkspaceInitTests.installed
    switch_candidate=fixtures.ActualWorkspaceInitTests.switch_candidate
    switch_preview=fixtures.ActualWorkspaceInitTests.switch_preview
    switch_apply=fixtures.ActualWorkspaceInitTests.switch_apply
    act=InstalledCandidateTests.act

    def test_new_release_created_plan_survives_rollback_and_exact_repair(self):
        from hv2ref.product import verify_workspace_product
        initial=verify_workspace_product(self.target);self.candidate=self.switch_candidate()
        up=self.switch_preview(installed=True);self.switch_apply(up,installed=True)
        self.act();self.act('select');plan=(self.target/'.hrn/planning/candidates.json').read_bytes()
        down=self.switch_preview('rollback',installed=True,operation='return-p');self.switch_apply(down,installed=True)
        self.assertEqual(initial['inventory'],verify_workspace_product(self.target)['inventory']);self.assertEqual(plan,(self.target/'.hrn/planning/candidates.json').read_bytes())
        self.assertIn('기록된 Owner 선택',self.installed(['view','candidates']).stdout.decode())
        # Exact active source repair after deliberately damaged launcher.
        (self.target/'colvia').write_text('damaged launcher\n')
        p=json.loads(self.call(['repair','--target',self.target,'--source',self.source,'--backup',self.base/'backup','--operation-id','repair-candidate','--observed-at',TIME]).stdout)
        self.call(['repair','--target',self.target,'--source',self.source,'--apply','--input','-','--confirm',p['confirm_token']],p['request'])
        self.assertEqual(plan,(self.target/'.hrn/planning/candidates.json').read_bytes());self.installed(['view','candidates'])
        self.act('defer',payload={'resume_condition':'explicit fixture continuation'})
        self.act('resume',payload={'condition_observation':'fixture Owner resumed'})

    def test_pending_lifecycle_refuses_plan_then_exact_recovery_preserves_it(self):
        self.act();original=(self.target/'.hrn/planning/candidates.json').read_bytes();self.candidate=self.switch_candidate()
        up=self.switch_preview(installed=True);req=proposal(self.target,cid='later')
        self.switch_apply(up,point='after-receipt',expected=75);before=fixtures.exact_snapshot(self.target)
        self.installed(['candidate','add'],req,expected=65);self.assertEqual(before,fixtures.exact_snapshot(self.target))
        self.switch_apply(up,recover=True);self.assertEqual(original,(self.target/'.hrn/planning/candidates.json').read_bytes())
        self.installed(['candidate','add'],req)


class CandidateCapacityTests(unittest.TestCase):
    setUp=CandidateContractTests.setUp
    accept_intent=serial.SerialWriterTests.accept_intent
    act=CandidateContractTests.act
    lines=CandidateContractTests.lines
    bytes=serial.SerialWriterTests.bytes

    def test_real_candidate_limit_warns_and_preserves_full_history(self):
        for i in range(100):self.act(cid='c-'+str(i))
        text=self.lines();self.assertIn('한도 근접',text);self.assertIn('100/100',text)
        before=self.bytes()
        with self.assertRaisesRegex(ContractError,'LIMIT'):self.act(cid='overflow')
        self.assertEqual(before,self.bytes())
        print('CAPACITY',len((self.target/'.hrn/planning/candidates.json').read_bytes()),'bytes; 100 candidates',flush=True)

    def test_oversize_read_never_claims_empty_and_work_reader_is_independent(self):
        self.act();p=self.target/'.hrn/planning/candidates.json';p.write_bytes(b' '*1048577);before=self.bytes()
        with self.assertRaisesRegex(ContractError,'LIMIT'):read_candidates(self.target)
        self.assertEqual({},self.store._all());self.assertEqual(before,self.bytes())

    def test_pending_intent_refuses_then_original_exact_recovery(self):
        from hv2ref.intent import WorkspaceIntentStore
        import test_general_work_invariants as intent_fixtures
        # Isolated runtime double: interrupted intent acceptance, no installed claim.
        runtime=lambda target:{'binding_ref':self.binding,'launcher_sha256':None}
        intents=WorkspaceIntentStore(self.target,runtime)
        draft=intent_fixtures.IntentWriterTests.draft(self,intent_id='another-intent');intents.publish_draft(draft)
        p=intents.prepare('another-intent',record_ref(draft,'revision_id'),actor='owner',reason='synthetic',request_id='another-accept',observed_at=TIME)
        with self.assertRaises(InjectedCrash):intents.apply(p['ticket'],confirm_token=p['confirm_token'],inject_at='after-acceptance')
        before=self.bytes()
        with self.assertRaisesRegex(ContractError,'PENDING'):self.act()
        self.assertEqual(before,self.bytes());intents.apply(p['ticket'],confirm_token=p['confirm_token']);self.act()


    def test_actual_decision_and_byte_limits_do_not_delete_history(self):
        from hv2ref.candidates import empty_store,transition,MAX_BYTES
        from hv2ref.jsonio import sha256_bytes
        # Build canonical synthetic histories without repeated disk I/O. Every expected digest
        # is the exact prior store; live writes at the boundary still use CandidateStore.
        for boundary in ('decisions','bytes'):
            if hasattr(self,'intent'):del self.intent
            self.setUp();store=empty_store('home-a');raw=None
            for n in range(999 if boundary=='decisions' else 1000):
                action='add' if n==0 else 'amend'
                request=proposal(self.target,action,request_id='request-'+str(n))
                request['expected_sha256']=sha256_bytes(raw) if raw is not None else None
                if boundary=='bytes':
                    for key in ('writer','owner_statement','reason','observed_at'):request[key]='x'*2000
                    for key in ('title','purpose','expected_effect'):request['payload'][key]='x'*2000
                rows,selected,before,after=transition(store['candidates'],store['selected'],request)
                updated={**store,'candidates':rows,'selected':selected,'decisions':store['decisions']+[{'request':request,'before':before,'after':after}]}
                candidate=canonical_json_bytes(updated)
                if len(candidate)>MAX_BYTES:break
                store=updated;raw=candidate
            path=self.target/'.hrn/planning/candidates.json';path.parent.mkdir();path.write_bytes(raw)
            read_candidates(self.target)
            # A history produced by real writers already has this cooperating lock scratch.
            from hv2ref.workspace import writer_guard
            with writer_guard(self.target):pass
            if boundary=='decisions':
                self.act('amend',request_id='last-decision');self.assertEqual(1000,len(read_candidates(self.target)['store']['decisions']))
                bad=proposal(self.target,'amend',request_id='overflow')
            else:
                bad=request
                self.assertGreater(len(candidate),MAX_BYTES);self.assertGreater(len(raw),MAX_BYTES*.8)
            before=self.bytes()
            with self.assertRaisesRegex(ContractError,'LIMIT'):self.candidates.mutate(bad)
            self.assertEqual(before,self.bytes());self.assertIn('한도 근접',self.lines())
            print('CAPACITY',boundary,len(read_candidates(self.target)['store']['decisions']),len(path.read_bytes()),flush=True)
