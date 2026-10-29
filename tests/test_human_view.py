"""Human projection tests: actual installed CLI plus explicitly labeled graph fixtures."""
from __future__ import annotations
from tests.platform_fixtures import (
    fixture_is_link,
    fixture_snapshot_paths,
    fixture_temporary_directory,
    fixture_unlink,
    fixture_unsafe_link,
    fixture_window,
    posix_mechanism,
)
import sys
from test_productization_safety import verified_inventory_id
import ast
import copy
import hashlib
import html
import json
import os
import re
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest
from unittest.mock import patch

from hv2ref.errors import ContractError, InjectedCrash
from hv2ref.jsonio import canonical_json_bytes
from hv2ref.product import source_root, workspace_candidate
from hv2ref.view import bounded_bytes, render_view, text, reference_observation
from hv2ref.work import record_ref
import test_productization_safety as installed_fixtures
from test_productization_safety import exact_snapshot
import test_general_work_invariants as graph_fixtures


class HumanViewInstalledTests(unittest.TestCase):
    TIME = installed_fixtures.ActualWorkspaceInitTests.TIME
    setUp = installed_fixtures.ActualWorkspaceInitTests.setUp
    call = installed_fixtures.ActualWorkspaceInitTests.call
    preview = installed_fixtures.ActualWorkspaceInitTests.preview
    apply_init = installed_fixtures.ActualWorkspaceInitTests.apply_init
    installed = installed_fixtures.ActualWorkspaceInitTests.installed
    draft = installed_fixtures.ActualWorkspaceInitTests.draft
    accept_intent = installed_fixtures.ActualWorkspaceInitTests.accept_intent
    complete_work = installed_fixtures.ActualWorkspaceInitTests.complete_work
    switch_candidate = installed_fixtures.ActualWorkspaceInitTests.switch_candidate
    switch_preview = installed_fixtures.ActualWorkspaceInitTests.switch_preview
    switch_apply = installed_fixtures.ActualWorkspaceInitTests.switch_apply
    detach_preview = installed_fixtures.ActualWorkspaceInitTests.detach_preview
    detach_apply = installed_fixtures.ActualWorkspaceInitTests.detach_apply

    def screen(self, args, value=None, *, source=False, expected=0):
        before = exact_snapshot(self.target)
        if source: result = self.call(['view', '--target', self.target, *args], value, expected=expected)
        else: result = self.installed(['view', *args], value, expected=expected)
        self.assertEqual(before, exact_snapshot(self.target))
        self.assertTrue(result.stdout.startswith(b'# '), result.stdout)
        return re.sub(r"\\([\\`*_{}\[\]()!|#~])", r"\1", html.unescape(result.stdout.decode()))

    def test_empty_actual_source_installed_and_git_are_read_only(self):
        subprocess.run(['git','init','-q',str(self.target)], check=True)
        self.apply_init(self.preview())
        a=self.screen([]);b=self.screen([],source=True)
        self.assertIn('No Work',a);self.assertIn('natural_language_adapter',a);self.assertNotIn('inventory:',a);self.assertNotIn('src/hv2ref/view.py',a)
        self.assertIn('not the bound release',b)
        self.assertEqual(fixture_window('continuation-1'),workspace_candidate(self.source)['inventory']['inventory_id'])
        self.assertEqual(30,len(workspace_candidate(self.source)['inventory']['entries']))

    def test_draft_is_not_acceptance_and_hostile_facets_are_escaped(self):
        self.apply_init(self.preview());draft=self.draft()
        draft['facets']['goal']['value']={'계획':'<script>bad</script>\n# forged\x1b[2J\u202e', 'nested':['a|b','`code`']}
        self.installed(['intent','draft'],draft)
        before=exact_snapshot(self.target);r=self.installed(['view','intent','intent-a']);self.assertEqual(before,exact_snapshot(self.target))
        raw=r.stdout.decode();self.assertNotIn('<script>',raw);self.assertNotIn('\x1b',raw);self.assertNotIn('\u202e',raw);self.assertNotIn('\n# forged',raw)
        self.assertIn('Unaccepted draft',html.unescape(raw));self.assertIn('destination',raw);self.assertIn('expected',raw)
        for facet in ('goal','scope','expected_outcome','acceptance_oracle','destination','forbidden_scope'): self.assertIn(text(facet),raw)
        self.screen(['intent','intent-a','--revision','absent'],expected=65)

    def test_intent_optional_document_refs_exact_apply_and_stale_required_ref(self):
        self.apply_init(self.preview());path=self.target/'brief.md';path.write_text('Purpose\n')
        draft=self.draft();self.installed(['intent','draft'],draft)
        ref={'path':'brief.md','sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'role':'brief','required':True}
        value={'intent_id':'intent-a','revision_ref':record_ref(draft,'revision_id'),'actor':'owner','reason':'fixture','request_id':'accept-a','observed_at':self.TIME,'document_refs':[ref]}
        prepared=json.loads(self.installed(['intent','prepare'],value).stdout)
        view=self.screen(['confirmation','--input','-'],prepared['ticket']);self.assertIn('human decision required',view);self.assertIn(prepared['confirm_token'],view);self.assertIn('brief.md',view)
        self.screen(['confirmation','--input','-'],prepared,expected=65)
        bad=dict(value,unknown=True);self.installed(['intent','prepare'],bad,expected=65)
        path.write_text('Changed\n');view=self.screen(['confirmation','--input','-'],prepared['ticket']);self.assertIn('stale',view);advisory=view.split('### Advisory observations')[1];self.assertIn('required ticket references',advisory);self.assertIn('brief.md: stale',advisory);self.assertIn('unavailable or refused',advisory)
        before=exact_snapshot(self.target);self.installed(['intent','apply','--confirm',prepared['confirm_token']],prepared['ticket'],expected=65);self.assertEqual(before,exact_snapshot(self.target))
        path.write_text('Purpose\n');self.installed(['intent','apply','--confirm',prepared['confirm_token']],prepared['ticket'])
        self.assertIn('Current acceptance documents',self.screen(['intent','intent-a']))

    def test_completed_stored_result_live_drift_and_replay_confirmation(self):
        self.apply_init(self.preview());self.complete_work()
        result=self.screen(['work','work-a']);self.assertIn('completed',result);self.assertIn('matches stored result',result);self.assertIn('metadata only',result);self.assertIn('## Work revision documents and evidence',result);history=result.split('## Selected history')[1];self.assertIn('action: accept',history);self.assertIn('actor: owner',history);self.assertIn('reason: fixture',history);self.assertIn('recorded at publication',result)
        path=next((self.target/'.hrn/work/work-a/decisions').glob('*.json'));ticket=json.loads(path.read_text())['confirmation']
        result=self.screen(['confirmation','--input','-'],ticket);self.assertIn('already_applied: True',result);self.assertIn('do not revoke the historical decision',result)
        changed=copy.deepcopy(ticket);changed['actor']='agent'
        result=self.screen(['confirmation','--input','-'],changed);self.assertIn('request ID reused with different ticket',result)
        self.assertIn('already_applied: False',result)
        # A separate request reaches the no-grant actor rule, rather than the
        # earlier immutable request-ID reuse refusal. Both views stay read-only.
        changed['request_id']='distinct-unauthorized-request'
        result=self.screen(['confirmation','--input','-'],changed);self.assertIn('no grant for this Work',result)
        self.assertIn('already_applied: False',result)
        (self.target/'a').write_text('drift\n');self.assertIn('stale: current files differ',self.screen(['work','work-a']))
        self.assertIn('stored result',self.screen(['confirmation','--input','-'],ticket))

    def test_ticket_file_outside_project_and_symlink_refusal(self):
        self.apply_init(self.preview());draft=self.draft();self.installed(['intent','draft'],draft)
        value={'intent_id':'intent-a','revision_ref':record_ref(draft,'revision_id'),'actor':'owner','reason':'fixture','request_id':'accept-a','observed_at':self.TIME}
        p=json.loads(self.installed(['intent','prepare'],value).stdout);ticket=self.base/'ticket.json';ticket.write_bytes(canonical_json_bytes(p['ticket']))
        self.assertIn(p['confirm_token'],self.screen(['confirmation','--input',ticket]))
        link=self.base/'link';fixture_unsafe_link(link, ticket);self.screen(['confirmation','--input',link],expected=65)

    def test_partial_pending_and_malformed_selector_never_look_completed(self):
        self.apply_init(self.preview());self.complete_work()
        current=self.target/'.hrn/work/work-a/current.json';current.write_text('{}\n')
        result=self.screen(['work','work-a'],source=True,expected=10);self.assertNotIn('Stored state: completed',result);self.assertIn('degraded',result)

    def test_view_no_import_backedge_from_core(self):
        for name in ['work','intent','product','workspace','jsonio','candidates','continuation']:
            tree=ast.parse((self.source/'src/hv2ref'/f'{name}.py').read_text(encoding='utf-8'))
            for n in ast.walk(tree):
                if isinstance(n,ast.ImportFrom):self.assertNotEqual(n.module,'view')
        tree=ast.parse((self.source/'src/hv2ref/view.py').read_text(encoding='utf-8'))
        forbidden={'apply','prepare','publish','publish_draft','writer_guard','write_text','write_bytes','mkdir','unlink'}
        self.assertFalse([n.func.attr for n in ast.walk(tree) if isinstance(n,ast.Call) and isinstance(n.func,ast.Attribute) and n.func.attr in forbidden])

    def test_human_profile_refuses_serial_profile_before_writes(self):
        before=exact_snapshot(self.target)
        self.call(['init','--profile','serial-1','--target',self.target],expected=2)
        self.assertEqual(before,exact_snapshot(self.target))

    def test_unavailable_scope_provenance_preserves_required_reference_guard(self):
        from hv2ref.product import verify_workspace_product
        from hv2ref.work import snapshot, make_manifest
        self.apply_init(self.preview())
        brief=self.target/'brief.md';brief.write_bytes(b'Stable acceptance criteria\n')
        draft=self.draft();self.installed(['intent','draft'],draft)
        doc={'path':'brief.md','sha256':hashlib.sha256(brief.read_bytes()).hexdigest(),'role':'brief','required':True}
        req={'intent_id':'intent-a','revision_ref':record_ref(draft,'revision_id'),'actor':'owner','reason':'fixture','request_id':'intent-policy','observed_at':self.TIME,'document_refs':[doc]}
        ticket=json.loads(self.installed(['intent','prepare'],req).stdout)
        intent_graph=json.loads(self.installed(['intent','apply','--confirm',ticket['confirm_token']],ticket['ticket']).stdout)
        selected=intent_graph['selections'][intent_graph['current']['selection_ref']['id']]
        intent={'authority_home_id':'home-a','kind':'intent','id':'intent-a','revision_ref':selected['revision_ref'],'acceptance_ref':selected['acceptance_ref'],'selection_ref':intent_graph['current']['selection_ref']}
        launcher=verify_workspace_product(self.target)['launcher_sha256'];base=snapshot(self.target,verified_launcher_sha256=launcher, verified_inventory_id=verified_inventory_id(self.target))
        identity={'record_type':'work-identity','schema_version':1,'authority_home_id':'home-a','work_id':'work-a','work_type':'change','created_at':self.TIME,'acceptance_authority':'owner','lineage':None}
        prior=None;unavailable=['optional external platform probe not performed']
        for number,operation in [(1,'start'),(2,'submit-result')]:
            if number==2:(self.target/'a').write_bytes(b'after\n')
            manifest=make_manifest(base,snapshot(self.target,verified_launcher_sha256=launcher, verified_inventory_id=verified_inventory_id(self.target)),scope=['a']);digest=hashlib.sha256(canonical_json_bytes(manifest)).hexdigest()
            revision={'record_type':'work-revision','schema_version':1,'authority_home_id':'home-a','work_id':'work-a','record_id':f'revision-{number}','observed_at':self.TIME,'observed_scope':['fixture content'],'unavailable_scope':unavailable,'author':'agent','operation':operation,'expected_prior_selection':prior,'intent_ref':intent,'scope':['a'],'document_refs':[],'evidence_refs':[],'result_refs':{'manifest':{'id':digest,'sha256':digest}},'progress':'review' if number==2 else 'active','next_action':'owner review','relations':[],'rebind_from':None,'execution_context':{'mode':'local','attempt_id':f'attempt-{number}'}}
            graph=json.loads(self.installed(['work','publish'],{'identity':identity,'revision':revision,'manifest':manifest,'selection_id':f'selection-{number}','operation_id':f'publish-{number}'}).stdout);prior=graph['current']['selection_ref']
        prepared=json.loads(self.installed(['work','prepare'],{'work_id':'work-a','action':'accept','actor':'owner','reason':'synthetic nonessential observation decision','request_id':'accept-policy','observed_at':self.TIME,'revision_ref':None,'supersedes':None}).stdout)
        self.assertEqual(record_ref(revision),prepared['ticket']['target_revision_ref'])
        screen=self.screen(['work','work-a','--revision','revision-2']);self.assertIn(unavailable[0],screen)
        self.assertIn(prepared['confirm_token'],self.screen(['confirmation','--input','-'],prepared['ticket']))
        brief.write_bytes(b'Changed required criteria\n');before=exact_snapshot(self.target)
        refused=self.installed(['work','apply','--confirm',prepared['confirm_token']],prepared['ticket'],expected=65)
        failure=json.loads(refused.stdout);self.assertEqual('HV2-WORK-RECORD',failure['code']);self.assertEqual('required reference is stale',failure['message']);self.assertEqual(before,exact_snapshot(self.target))
        brief.write_bytes(b'Stable acceptance criteria\n')
        graph=json.loads(self.installed(['work','apply','--confirm',prepared['confirm_token']],prepared['ticket']).stdout)
        self.assertEqual('completed',graph['state'])
        selected=graph['selections'][graph['current']['selection_ref']['id']];self.assertEqual(unavailable,selected['unavailable_scope'])
        self.assertEqual('pass',json.loads(self.installed(['status']).stdout)['classification'])
        self.assertIn(unavailable[0],self.screen(['work','work-a']))

    def test_p_q_p_uses_current_adapter_path_and_detach_remains_readable(self):
        self.apply_init(self.preview());self.complete_work()
        p=self.screen([]);self.candidate=self.switch_candidate()
        self.switch_apply(self.switch_preview(installed=True),installed=True)
        q=self.screen([]);self.assertNotEqual(p,q)
        self.switch_apply(self.switch_preview('rollback',operation='back',installed=True),installed=True)
        back=self.screen([])
        import re
        paths=lambda x:re.findall(r'natural_language_adapter: ([^\n]+)',x)
        self.assertEqual(paths(p),paths(back));self.assertNotEqual(paths(p),paths(q))
        self.detach_apply(self.detach_preview())
        out=self.screen(['work','work-a'],source=True)
        self.assertIn('completed',out);self.assertIn('unavailable: no verified active product',out)
        self.assertNotIn('natural_language_adapter',out)

    def test_git_recorded_work_live_view_is_read_only_and_paths_are_readable(self):
        subprocess.run(['git','init','-q',str(self.target)],check=True)
        self.apply_init(self.preview());self.complete_work()
        result=self.screen(['work','work-a'])
        self.assertIn('matches stored result',result)
        raw=self.installed(['view','work','work-a']).stdout.decode()
        self.assertIn('.hrn/product/releases/',raw)
        self.assertNotIn('&#47;',raw);self.assertNotIn('&#45;',raw)

    def test_linked_worktree_view_is_non_authoritative_and_no_write(self):
        subprocess.run(['git','init','-q',str(self.target)],check=True)
        self.apply_init(self.preview())
        config=[('user.name','Fixture'),('user.email','fixture@example.invalid')]
        if sys.platform == 'win32':config += [('core.autocrlf','false'),('core.eol','lf')]
        for key,value in config:subprocess.run(['git','-C',str(self.target),'config',key,value],check=True)
        subprocess.run(['git','-C',str(self.target),'add','.'],check=True)
        # Isolate the view's no-write assertion from detached setup maintenance.
        subprocess.run(['git','-c','maintenance.auto=false','-c','gc.auto=0','-C',str(self.target),'commit','-qm','fixture'],check=True)
        worker=self.base/'worker';subprocess.run(['git','-C',str(self.target),'worktree','add','--detach',str(worker)],check=True,capture_output=True)
        before=exact_snapshot(self.base)
        result=self.call(['view'],launcher=worker/'colvia')
        after=exact_snapshot(self.base)
        changed=sorted(name for name in before.keys()|after.keys() if before.get(name)!=after.get(name))
        self.assertEqual(before,after,'Changed paths: '+repr(changed))
        out=html.unescape(result.stdout.decode());self.assertIn('authoritative\\_control: False',out)
        self.assertIn('linked',out)


class HumanViewGraphTests(unittest.TestCase):
    def setUp(self):
        self.f=graph_fixtures.IntentWriterTests();self.f.setUp();self.addCleanup(self.f.doCleanups)

    def view(self, **kw):
        before=self.f.bytes();out,code=render_view(self.f.target,**kw);self.assertEqual(before,self.f.bytes());self.assertEqual(14,code,out)
        return re.sub(r"\\([\\`*_{}\[\]()!|#~])", r"\1", html.unescape(out))

    def test_review_reject_rework_and_pending_are_distinct(self):
        f=self.f;f.accept();f.submitted()
        self.assertIn('Stored state: review',self.view(kind='work',object_id='work-a'))
        p=f.prepare()
        with self.assertRaises(InjectedCrash):f.apply(p,inject_at='after-decision')
        self.assertIn('pending_decisions',self.view(kind='work',object_id='work-a'))
        cancellation=f.prepare('reject',request_id='cancel',supersedes=record_ref(f.store._decision(p['ticket'])))
        f.apply(cancellation);out=self.view(kind='work',object_id='work-a');self.assertIn('Stored state: rejected',out);self.assertIn('cancel',out);self.assertIn('action: reject',out.split('## Selected history')[1])
        f.publish(f.proposal('rework'));self.assertIn('Rework retains',self.view(kind='work',object_id='work-a'))
        out=self.view(kind='confirmation',ticket=p['ticket']);self.assertIn('cancelled decision cannot resume',out)

    def test_changed_intent_requires_rebind_and_retains_discontinuity(self):
        f=self.f;first=f.draft();f.accept(first);f.submitted();f.apply(f.prepare('reject'))
        old_intent=copy.deepcopy(f.intent);f.accept(f.draft(2,prior=first));self.assertIn('Work rebind, new submit-result',self.view(kind='work',object_id='work-a'))
        # Existing fixture creates a rebind baseline from current project bytes.
        f.publish(f.proposal('rebind',old_intent=old_intent));graph=f.store._all()['work-a'];orphan=graph['orphan_revisions'][0]
        p=f.prepare('rebind',request_id='bind-new',revision_ref=record_ref(graph['revisions'][orphan]));f.apply(p)
        self.assertIn('Rebind discontinuity',self.view(kind='work',object_id='work-a'))

    def test_invalid_actor_and_material_gap_display_refusal_without_prepare(self):
        f=self.f;d=f.draft();f.intents.publish_draft(d);p=f.iprepare(d)
        p['ticket']['actor']='agent';out=self.view(kind='confirmation',ticket=p['ticket']);self.assertIn('intent cannot be accepted',out)
        with patch.object(f.intents.__class__,'prepare',side_effect=AssertionError('prepare invoked')):
            self.view(kind='intent',object_id='intent-a')

    def test_required_bound_intent_reference_is_visible_without_blocking_rejection(self):
        f=self.f;path=f.target/'brief.md';path.write_text('Purpose\n')
        draft=f.draft();f.intents.publish_draft(draft)
        ref={'path':'brief.md','role':'brief','required':True,'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}
        graph=f.iapply(f.iprepare(draft,document_refs=[ref]));selected=graph['selections'][graph['current']['selection_ref']['id']]
        f.intent={'authority_home_id':'home-a','kind':'intent','id':'intent-a','revision_ref':selected['revision_ref'],'acceptance_ref':selected['acceptance_ref'],'selection_ref':graph['current']['selection_ref']}
        f.submitted();prepared=f.prepare();path.write_text('Changed\n')
        result=self.view(kind='confirmation',ticket=prepared['ticket']);advisory=result.split('### Advisory observations')[1]
        self.assertIn('required bound intent references',advisory);self.assertIn('brief.md: stale',advisory)
        self.assertIn('Required intent document changed',self.view(kind='work',object_id='work-a'))
        with self.assertRaises(ContractError):f.apply(prepared)
        rejection=f.prepare('reject');result=self.view(kind='confirmation',ticket=rejection['ticket'])
        self.assertIn('not required for reject/revoke',result);self.assertNotIn('required bound intent references',result)
        f.apply(rejection)

    def test_unstable_two_observations_retry_then_fail_visible(self):
        from hv2ref import view
        with patch.object(view,'_observe',side_effect=[({'classification':'uninitialized'}, {}, {}),({'classification':'partial'}, {}, {})]*2):
            out,code=render_view(self.f.target)
        self.assertEqual(10,code);self.assertIn('unstable',out)


class HumanWorkerViewTests(unittest.TestCase):
    """Worker graph fixtures use an explicit runtime double, not installed proof."""
    def setUp(self):
        from test_worktree_execution import WorkerApplicationTests
        self.f=WorkerApplicationTests();self.f.setUp();self.addCleanup(self.f.doCleanups)

    def screen(self, *, ticket=None, revision=None):
        from hv2ref import view
        from hv2ref.intent import workspace_intents
        f=self.f;before=f.bytes();works=f.store._all();intents=workspace_intents(f.target)
        # An unverified runtime double keeps exact-blob proof; it does not enable delegation-1.
        # The native fixture supplies its required window, without a verified launcher.
        product={"binding_ref":f.binding,"launcher_sha256":None,"inventory":{"inventory_id":fixture_window()}}
        with patch.object(view.WorkStore,'prepare',side_effect=AssertionError('view called prepare')),patch.object(view.WorkStore,'apply',side_effect=AssertionError('view called apply')),patch.object(view.WorkStore,'publish',side_effect=AssertionError('view called publish')):
            lines=view._confirmation(f.target,ticket,works,intents,product) if ticket else view._work(f.target,works['work-a'],revision,product,intents,works)
        self.assertEqual(before,f.bytes())
        return re.sub(r"\\([\\`*_{}\[\]()!|#~])",r"\1",html.unescape('\n'.join(lines)))

    def test_worker_candidate_refs_baseline_and_lost_retention_are_distinct(self):
        f=self.f;f.result();p=f.prepare()
        work=self.screen();self.assertIn('whole_base_matches: True',work);self.assertIn('whole_result_matches: False',work)
        shown=self.screen(ticket=p['ticket']);advisory=shown.split('### Advisory observations')[1]
        self.assertIn('matches retained candidate',shown);self.assertIn('control_observation: stale',shown)
        self.assertIn('control matches baseline; candidate is not yet applied',advisory)
        self.assertNotIn('unavailable or refused',advisory);self.assertNotIn('local Work decision required',shown)
        f.git(f.target,'update-ref','refs/heads/retained-candidate',f.git(f.target,'rev-parse','retained-base'))
        shown=self.screen(ticket=p['ticket']);self.assertIn('unavailable: retained candidate could not be verified',shown)
        self.assertIn('unavailable or refused',shown.split('### Advisory observations')[1])

    def test_pending_mixed_cancel_and_outside_drift_are_observations_only(self):
        f=self.f;f.result(multiple=True);p=f.prepare()
        with self.assertRaises(InjectedCrash):f.apply(p,inject_at='after-file')
        shown=self.screen(ticket=p['ticket']);self.assertIn('pending decision; only remaining pre-images',shown)
        cancel=copy.deepcopy(p['ticket']);cancel.update(action='reject',request_id='cancel-view',supersedes_decision_ref=record_ref(f.store._decision(p['ticket'])))
        self.assertIn('cancellation refused: some changed path is not pre',self.screen(ticket=cancel))
        (f.target/'outside').write_bytes(b'drift\n')
        self.assertIn('recovery blocked by outside drift',self.screen(ticket=p['ticket']))
        (f.target/'a').write_bytes(b'before\n')
        shown=self.screen(ticket=cancel);self.assertIn('outside_drift: True',shown);self.assertIn('outside drift does not block cancellation',shown)
        self.assertIn('Stored state: review',self.screen())

    def test_baseline_refresh_compares_old_baseline_candidate_and_completed_matches(self):
        f=self.f;f.result();f.apply(f.prepare('reject'))
        original=copy.deepcopy(f.identity);f.identity={**original,'work_id':'work-b'}
        f.publish(f.proposal());(f.target/'a').write_bytes(b'human baseline\n')
        f.publish(f.proposal('submit-result'));f.apply(f.prepare())
        (f.target/'outside').write_bytes(b'unknown change\n');f.identity=original
        proposal=f.baseline('rebind');f.publish(proposal)
        p=f.prepare('rebind',revision_ref=record_ref(proposal[0]))
        shown=self.screen(ticket=p['ticket'])
        for text in ['not result acceptance','Previous baseline to proposed baseline','Previous submitted candidate to proposed baseline','IN-SCOPE CHANGE; origin unproven','outside Work scope; origin unproven','work: work-b','cause and timing unproven','baseline matches; result is not accepted']:
            self.assertIn(text,shown)
        self.assertIn('Human baseline refresh',self.screen(revision=proposal[0]['record_id']))


class HumanWorkerReferenceTests(unittest.TestCase):
    def test_candidate_reference_limits_and_worker_observed_are_not_upgraded(self):
        from hv2ref.view import _candidate_reference, READ_LIMIT
        ref={'path':'a','sha256':hashlib.sha256(b'post').hexdigest(),'required':True,'verification':'worker-observed'}
        candidate={'manifest':{'changes':[{'path':'a'}]},'sources':{'a':{'post':b'post'}},'source_error':None}
        self.assertEqual('worker-observed; not reverified on control',_candidate_reference(Path('/not-read'),ref,candidate,evidence=True))
        ref['verification']='control-required'
        self.assertEqual('matches retained candidate',_candidate_reference(Path('/not-read'),ref,candidate,evidence=True))
        candidate['sources']['a']['post']=None
        self.assertIn('deleted result',_candidate_reference(Path('/not-read'),ref,candidate,evidence=True))
        candidate['sources']['a']['post']=b'x'*(READ_LIMIT+1)
        self.assertIn('4 MiB advisory limit',_candidate_reference(Path('/not-read'),ref,candidate,evidence=True))
        candidate['source_error']='lost ref'
        self.assertIn('could not be verified',_candidate_reference(Path('/not-read'),ref,candidate,evidence=True))


class HumanViewInputTests(unittest.TestCase):
    def test_safe_reference_regular_missing_symlink_special_and_oversized(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp).resolve();p=root/'doc';p.write_text('hello')
            ref={'path':'doc','sha256':hashlib.sha256(b'hello').hexdigest(),'required':False,'role':'brief'}
            self.assertEqual('matches',reference_observation(root,ref));p.write_text('changed');self.assertEqual('stale',reference_observation(root,ref))
            fixture_unlink(p);fixture_unsafe_link(p, root/'absent');self.assertIn('unavailable',reference_observation(root,ref));fixture_unlink(p);
            p.write_bytes(b'x'*(4*1024*1024+1));self.assertIn('unavailable',reference_observation(root,ref))
            fixture_unlink(p);p.mkdir();self.assertIn('unavailable',reference_observation(root,ref))

    @posix_mechanism("filesystem FIFO; other reference forms run on both platforms")
    def test_posix_fifo_reference_is_unavailable(self):
        with fixture_temporary_directory() as tmp:
            root=Path(tmp).resolve();p=root/'fifo';os.mkfifo(p)
            ref={'path':'fifo','sha256':hashlib.sha256(b'hello').hexdigest(),'required':False,'role':'brief'}
            self.assertIn('unavailable',reference_observation(root,ref))

    def test_internal_observation_errors_stay_gfm(self):
        from hv2ref import view
        with tempfile.TemporaryDirectory() as tmp:
            for error in (TypeError, AttributeError, IndexError):
                with patch.object(view, '_observe', side_effect=error('fixture')):
                    output, status = render_view(Path(tmp).resolve())
                self.assertEqual(70, status);self.assertTrue(output.startswith('# Review unavailable'))

    def test_escape_markup_controls_and_nested_paths(self):
        value='한글<script>`|[click](x)\n# forged\x1b\u202e'
        rendered=text(value);self.assertNotIn('<script>',rendered);self.assertNotIn('\n',rendered);self.assertNotIn('\x1b',rendered);self.assertIn('한글',rendered);self.assertNotEqual(text('\x1b'),text(r'\u001b'));self.assertEqual('.hrn/work/work-a',text('.hrn/work/work-a'))
        for value in ['https://invalid.example','FTP://invalid.example','www.invalid.example','WWW.invalid.example','fixture@example.invalid']:
            self.assertNotRegex(text(value).lower(),r'https?://|ftp://|www\.|[a-z0-9]@')
        self.assertTrue(text('WWW.invalid.example').startswith('WWW'))
