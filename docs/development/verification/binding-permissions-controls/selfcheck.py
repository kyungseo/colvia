"""No-product mock checks for admission, identity and cleanup semantics.

Run with the fixed isolated bootstrap; no fixture creation or host signals.
Executed result must be recorded by the enclosing bounded launcher.
"""
import importlib
import json
import campaign
import common
import stat
import calibration
from common import canonical,digest
import signal
import subprocess
import sys
import unittest
from unittest import mock
from pathlib import Path
import controller
import runner
from common import require_isolated

class ControlSelfChecks(unittest.TestCase):
    def test_closed_modes(self):
        for phase, mapping in (("entry",controller.ENTRY_MODE_SLOTS),("delegation",controller.DELEGATION_MODE_SLOTS)):
            for mode,slots in mapping.items():
                for slot in slots:controller.allowed(mode,slot,phase)
        for args in (("complete-normal","base","delegation"),("focused","p1","delegation"),("focused","core","entry"),("bogus","final","delegation"),("collect","final","unknown")):
            with self.subTest(args=args),self.assertRaises(RuntimeError):controller.allowed(*args)
    def test_duplicate_factory_refused(self):
        case=unittest.FunctionTestCase(lambda:None)
        with self.assertRaises(RuntimeError):runner.factory_members(unittest.TestSuite([case,case]),[])
        with self.assertRaises(RuntimeError):runner.factory_members(unittest.TestSuite([]),[])
        with self.assertRaises(RuntimeError):runner.factory_members(unittest.TestSuite([case]),[case])
    def test_unknown_group_never_absent(self):
        child=mock.Mock(pid=123,returncode=0)
        child.poll.return_value=0
        with mock.patch.object(controller.os,'killpg',side_effect=PermissionError(1,'synthetic')),mock.patch.object(controller.time,'monotonic',return_value=100):
            reason,natural,absent,errors=controller.settle_child(child,0,90,None,True)
        self.assertFalse(absent);self.assertTrue(errors);self.assertIsNotNone(reason)
    def test_eperm_resolves_only_with_reaped_exact_parent_snapshot(self):
        for output,exitcode,expected in (('1 1\n',0,True),('1 123\n',0,False),('malformed\n',0,False),('',1,False)):
            child=mock.Mock(pid=123,returncode=0);child.poll.return_value=0;clock=[0.0];observations=[]
            def sleep(seconds):clock[0]+=max(seconds,0.01)
            with mock.patch.object(controller.os,'killpg',side_effect=PermissionError(1,'synthetic')),mock.patch.object(controller.time,'monotonic',side_effect=lambda:clock[0]),mock.patch.object(controller.time,'sleep',side_effect=sleep),mock.patch.object(controller.subprocess,'run',return_value=mock.Mock(returncode=exitcode,stdout=output)):
                reason,natural,absent,errors=controller.settle_child(child,0,1,None,True,observations=observations,parent_snapshot=True)
            self.assertEqual(expected,absent)
            if expected:self.assertIsNone(reason);self.assertEqual([],errors);self.assertTrue(observations)
            else:self.assertIsNotNone(reason);self.assertTrue(errors)
    def test_original_reason_preserved(self):
        child=mock.Mock(pid=123,returncode=-9)
        child.poll.return_value=-9
        with mock.patch.object(controller.os,'killpg',side_effect=ProcessLookupError()),mock.patch.object(controller.time,'monotonic',return_value=100):
            reason,natural,absent,errors=controller.settle_child(child,0,120,'budget-exhausted',False)
        self.assertEqual('budget-exhausted',reason);self.assertFalse(natural);self.assertTrue(absent);self.assertEqual([],errors)
    def test_wait_failure_never_passes(self):
        child=mock.Mock(pid=123,returncode=0)
        child.wait.side_effect=subprocess.TimeoutExpired('synthetic',0)
        with mock.patch.object(controller.os,'killpg',side_effect=ProcessLookupError()),mock.patch.object(controller.time,'monotonic',return_value=100):
            reason,natural,absent,errors=controller.settle_child(child,0,120,None,True)
        self.assertIsNotNone(reason);self.assertEqual('child-wait',errors[0]['stage'])
    def test_collection_identity_phase(self):
        c={'phase':'delegation','source_digest':'a','controls':{'x':'a'}}
        with self.assertRaises(RuntimeError):controller.require_new_collection(c,c)
        with self.assertRaises(RuntimeError):controller.require_new_collection(c,dict(c,phase='unknown'))
        controller.require_new_collection(c,dict(c,phase='entry'))
    def test_exact_campaign_ancestors(self):
        root=Path('/Users/example/dev-home/agent-artifacts/task/implementation/r00/current')
        p={'root':root,'exec':root/'exec'}
        result=controller.test_ancestor_parameters(p,p['exec']/'runs/collect-final')
        self.assertEqual(12,len(result));self.assertEqual(Path('/'),result['ANCESTOR_11'])
        with self.assertRaises(RuntimeError):controller.test_ancestor_parameters(p,root/'collect-final')
    def test_no_product_import(self):
        self.assertFalse(any(x=='hv2ref' or x.startswith('hv2ref.') for x in sys.modules))


    def test_pair_aggregate_budget(self):
        self.assertEqual(5460,campaign.pair_budget({'retained':2730,'current':2730},0,2))
        with self.assertRaises(RuntimeError):campaign.pair_budget({'retained':5401,'current':100},0,2)
        with self.assertRaises(RuntimeError):campaign.pair_budget({'retained':5000,'current':5801},0,2)
        with self.assertRaises(RuntimeError):campaign.pair_budget({'retained':2730,'current':2730},20000,2)
        with self.assertRaises(RuntimeError):campaign.pair_budget({'retained':None,'current':2730},0,2)
        self.assertEqual(5460,campaign.pair_budget({'retained':2730,'current':2730},20000,1))
    def test_retained_cannot_spend_current_share(self):
        estimates={'retained':3000,'current':2000}
        self.assertEqual(3000,campaign.lane_budget('retained',estimates,5000))
        self.assertEqual(2500,campaign.lane_budget('retained',estimates,4500))
        self.assertEqual(1900,campaign.lane_budget('current',estimates,1900))
        with self.assertRaises(RuntimeError):campaign.lane_budget('retained',estimates,2020)
    def test_calibration_partial_is_not_complete(self):
        ids=['m.A.test_1','m.A.test_2','m.B.test_1']
        r=calibration.summarize(ids,{'m.A.test_1':10},{},5)
        self.assertEqual(500,r['measured_family_estimate_subtotal'])
        self.assertEqual(['m.B'],r['unmeasured_families']);self.assertIsNone(r['complete_estimate'])
        self.assertIsNone(r['families'][1]['extrapolated_seconds'])
    def test_heterogeneous_unmeasured_kind_stays_unknown(self):
        ids=['m.C.test_p2_b1_0001','m.C.test_p2_b1_0002']
        r=calibration.summarize(ids,{ids[0]:10},{ids[0]:'record',ids[1]:'lifecycle'},0)
        self.assertIsNone(r['complete_estimate']);self.assertEqual(['lifecycle'],r['families'][0]['unmeasured_kinds'])
        r=calibration.summarize(ids,{ids[0]:10,ids[1]:12},{ids[0]:'record',ids[1]:'lifecycle'},0)
        self.assertEqual(494,r['complete_estimate'])
    def test_parent_exact_selection(self):
        collection={'ordered':[{'id':'a','occurrence':1},{'id':'b','occurrence':1}],'factory_ids':['b']}
        with self.assertRaises(RuntimeError):controller.selected_identities({'selection':[]},collection,'smoke')
        with self.assertRaises(RuntimeError):controller.selected_identities({'selection':['missing']},collection,'focused')
        with self.assertRaises(RuntimeError):controller.selected_identities({'selection':['a']},collection,'artifact')
        self.assertEqual([{'id':'b','occurrence':1}],controller.selected_identities({'selection':['b']},collection,'artifact'))
        self.assertEqual(collection['ordered'],controller.selected_identities({'selection':[]},collection,'complete-normal'))
    def evidence_fixture(self):
        collection={'source_digest':'source','source_root_entries':{},'controls':{},'default_ids':['a'],'factory_ids':['b'],'ordered':[{'id':'a','occurrence':1},{'id':'b','occurrence':1}],'duplicates':{}}
        selected=collection['ordered']
        files={'collection.json':canonical(collection),'selected.json':canonical(selected),'counts.json':canonical({'discovered':2,'selected':2,'run':2,'unstarted':0,'unfinished':0,'failures':0,'errors':0,'skips':0,'expected_failures':0,'unexpected_successes':0}),'unstarted.json':canonical([]),'unfinished.json':canonical([]),'executed.jsonl':b''.join((json.dumps({**v,'outcome':'pass','seconds':1})+'\n').encode() for v in selected)}
        c={'source_digest':'source','source_root_entries':{},'controls':{},'factory':True,'selection':[],'collection_sha256':digest(files['collection.json'])}
        return c,files
    def test_parent_completion_rejects_early_zero_exit(self):
        c,files=self.evidence_fixture();files.pop('counts.json')
        with mock.patch.object(controller,'read_json',side_effect=lambda p:json.loads(files[p.name])),mock.patch.object(controller,'regular',side_effect=lambda p:files[p.name]):
            with self.assertRaises(KeyError):controller.child_evidence(c,{},Path('/synthetic-run'),'complete-normal')
    def test_parent_completion_seals_all_executed_ids(self):
        c,files=self.evidence_fixture()
        with mock.patch.object(controller,'read_json',side_effect=lambda p:json.loads(files[p.name])),mock.patch.object(controller,'regular',side_effect=lambda p:files[p.name]),mock.patch.object(Path,'exists',return_value=False):
            sealed=controller.child_evidence(c,{},Path('/synthetic-run'),'complete-normal')
            self.assertEqual(set(files),set(sealed));self.assertEqual(digest(files['executed.jsonl']),sealed['executed.jsonl'])
            files['executed.jsonl']=files['executed.jsonl'].splitlines(keepends=True)[0]
            with self.assertRaises(RuntimeError):controller.child_evidence(c,{},Path('/synthetic-run'),'complete-normal')
    def test_parent_missing_evidence_cannot_pass_write_result(self):
        child=mock.Mock(returncode=0);recorded=[]
        with mock.patch.object(controller,'config'),mock.patch.object(controller,'verify_old'),mock.patch.object(controller,'regular',return_value=b'inputs'),mock.patch.object(controller,'child_evidence',side_effect=RuntimeError('incomplete')),mock.patch.object(controller,'exclusive_json',side_effect=lambda p,v:recorded.append(v)),mock.patch.object(controller.time,'monotonic',return_value=100):
            ok=controller.write_result({}, {'old':Path('/old')},Path('/input'),'sha',Path('/out'),digest(b'inputs'),None,{},'source',child,99,300,'complete-normal','final',None,True,True,[])
        self.assertFalse(ok);self.assertFalse(recorded[0]['execution_pass']);self.assertIn('incomplete',recorded[0]['reason'])
    def test_preflight_missing_collection_spawns_nothing(self):
        p={'root':Path('/synthetic-root'),'exec':Path('/synthetic-root/exec'),'controls':Path('/controls')}
        c={'phase':'entry','collection_sha256':None}
        with mock.patch.object(Path,'exists',return_value=False),mock.patch.object(Path,'is_dir',return_value=True),mock.patch.object(controller,'completed'),mock.patch.object(controller,'regular',return_value=b'x'),mock.patch.object(controller.subprocess,'Popen') as spawn:
            with self.assertRaises(RuntimeError):controller.preflight(c,p,'focused','p1')
            spawn.assert_not_called()
    def test_admission_failure_is_charged_without_execution_correction(self):
        root=Path('/synthetic-root');call=root/'r00/calls/admission-retained-focused-p1';raw=b'inputs'
        inputs={'lane':'retained','mode':'focused','slot':'p1'}
        result={'inputs_sha256':digest(raw),'seconds':2.5,'execution_pass':False,'admission_only':True}
        with mock.patch.object(Path,'glob',autospec=True,side_effect=lambda path,pattern: [call] if path==root/'r00/calls' and pattern=='*' else []),mock.patch.object(campaign,'unlinked_path',side_effect=lambda p:p),mock.patch.object(Path,'is_file',return_value=True),mock.patch.object(campaign,'regular',return_value=raw),mock.patch.object(campaign,'read_json',side_effect=lambda p:inputs if p.name=='inputs.json' else result):
            total,failures,attempts=campaign.elapsed(root)
        self.assertEqual(2.5,total);self.assertEqual([],failures);self.assertEqual(set(),attempts)
    def correction_fixture(self):
        root=Path('/synthetic-root');c={'controls':{'x':'new'},'source_digest':'source','runtime':{},'git':{},'git_system_config':{}}
        ref={'path':str(root/'review'),'sha256':digest(b'review')}
        oldref={'path':str(root/'old-input'),'sha256':'old'}
        note={'schema':2,'previous_attempt':'r00','reason':'input-change','affected_phases':[['retained','canary','base']],'controls':c['controls'],'prior_invocations':[oldref],
              'review':{'packet':ref,'response':ref,'disposition':{'record':'FEAT','text':'reviewed','sha256':digest(b'reviewed')}}}
        old={**c,'controls':{'x':'old'}}
        def read(path):
            if path.name=='correction.json':return note
            if path.name=='inputs.json':return {'invocations':{'retained':oldref},'mode':'canary','slot':'base'}
            return {'inputs_sha256':digest(b'review'),'admission_only':False}
        return root,c,note,old,read
    def test_reviewed_input_change_does_not_require_deliberate_failure(self):
        root,c,note,old,read=self.correction_fixture()
        with mock.patch.object(campaign,'read_json',side_effect=read),mock.patch.object(campaign,'unlinked_path',side_effect=Path),mock.patch.object(campaign,'regular',return_value=b'review'),mock.patch.object(campaign,'config',return_value=(old,{'root':root/'r00/retained'})),mock.patch.object(Path,'glob',return_value=[root/'r00/calls/retained-canary-base']):
            for lane in ('retained','current'):
                campaign.correction(root,'r01',c,lane,'canary','base',[],{'r00'})
            note['affected_phases']=[['retained','focused','p1']]
            with self.assertRaisesRegex(RuntimeError,'never executed'):
                campaign.correction(root,'r01',c,'current','acquire','base',[],{'r00'})
    def test_correction_failure_scope_and_global_order(self):
        root,c,note,old,read=self.correction_fixture()
        with mock.patch.object(campaign,'read_json',side_effect=read),mock.patch.object(campaign,'unlinked_path',side_effect=Path),mock.patch.object(campaign,'regular',return_value=b'review'),mock.patch.object(campaign,'config',return_value=(old,{'root':root/'r00/retained'})),mock.patch.object(Path,'glob',return_value=[root/'r00/calls/retained-canary-base']):
            for failures,attempts,pattern in (([('r00','retained','focused','p1')],{'r00'},'unresolved'),([('r01','current','focused','core')],{'r00','r01'},'blocks all'),([],set(),'order')):
                with self.subTest(pattern=pattern),self.assertRaisesRegex(RuntimeError,pattern):
                    campaign.correction(root,'r01',c,'current','acquire','base',failures,attempts)
            note['previous_attempt']='r01'
            with self.assertRaisesRegex(RuntimeError,'per affected phase'):
                campaign.correction(root,'r02',c,'current','acquire','base',[],{'r00','r01'})
    def test_r09_elapsed_keeps_all_prior_charges_and_failures(self):
        root=Path('/synthetic-root');raw=b'bound';h=digest(raw)
        seconds={'r00':1.25,'r01':2.5,'r02':3.75,'r03':4.0,'r04':5.0,'r05':6.0,'r06':7.0,'r07':8.0,'r08':9.0,'r09':10.0}
        calls={root/a/'calls':[root/a/'calls/current-focused-core'] for a in seconds}
        def read(path):
            if path.name=='inputs.json':return {'lane':'current','mode':'focused','slot':'core','correction_sha256':h}
            return {'inputs_sha256':h,'seconds':seconds[path.parents[2].name],
                    'execution_pass':False,'process_cleanup_verified':True}
        with mock.patch.object(Path,'glob',autospec=True,side_effect=lambda path,pattern:calls.get(path,[])),mock.patch.object(campaign,'unlinked_path',side_effect=Path),mock.patch.object(Path,'is_file',return_value=True),mock.patch.object(campaign,'regular',return_value=raw),mock.patch.object(campaign,'read_json',side_effect=read):
            total,failures,attempts=campaign.elapsed(root)
        self.assertEqual(56.5,total);self.assertEqual(set(seconds),attempts)
        self.assertEqual([(a,'current','focused','core') for a in seconds],failures)
    def test_r03_reviewed_correction_and_unchanged_stop_boundaries(self):
        root,c,note,old,_=self.correction_fixture()
        note.update(previous_attempt='r02',reason='failed-phase',affected_phases=[['current','focused','core']])
        oldref=note['prior_invocations'][0]
        prior={'r01':{'affected_phases':[['retained','focused','p1']]},
               'r02':{'affected_phases':[['current','smoke','base']]}}
        def read(path):
            if path.name=='correction.json':return note if path.parent.name=='r03' else prior[path.parent.name]
            if path.name=='inputs.json':return {'invocations':{'current':oldref},'mode':'focused','slot':'core'}
            return {'inputs_sha256':digest(b'review'),'admission_only':False}
        failures=[('r00','retained','focused','p1'),('r01','current','smoke','base'),('r02','current','focused','core')]
        attempts={'r00','r01','r02'}
        with mock.patch.object(campaign,'read_json',side_effect=read),mock.patch.object(campaign,'unlinked_path',side_effect=Path),mock.patch.object(campaign,'regular',return_value=b'review'),mock.patch.object(campaign,'config',return_value=(old,{'root':root/'r02/current'})),mock.patch.object(Path,'glob',return_value=[root/'r02/calls/current-focused-core']):
            self.assertIs(note,campaign.correction(root,'r03',c,'current','selfcheck','base',failures,attempts))
            for attempt,fs,ats,pattern in (
                    ('r03',failures+[('r03','current','focused','core')],attempts|{'r03'},'blocks all'),
                    ('r03',failures,{'r00','r02'},'order'),
                    ('r10',failures,attempts|{'r03','r04','r05','r06','r07','r08','r09'},'order')):
                with self.subTest(pattern=pattern),self.assertRaisesRegex(RuntimeError,pattern):
                    campaign.correction(root,attempt,c,'retained','acquire','base',fs,ats)
            prior['r02']['affected_phases']=[['current','focused','core']]
            with self.assertRaisesRegex(RuntimeError,'per affected phase'):
                campaign.correction(root,'r03',c,'current','selfcheck','base',failures,attempts)
    def test_campaign_r03_policy_accepts_only_exact_legacy_or_extended_bound(self):
        home=Path('/Users/example/dev-home/agent-artifacts/task/implementation')
        keys={'schema','phase','paths','runtime','git','source_files','controls','selection','collection_sha256','factory','source_digest','git_system_config','source_root_entries'}
        base={key:None for key in keys};base.update(schema=3,phase='base')
        def check(corrections,attempts,attempt,pattern):
            root=home/attempt/'retained'
            value={**base,'paths':{'source':str(root/'exec/source'),'controls':'/controls','root':str(root),'old':str(root/'old'),'exec':str(root/'exec'),'common_git':'/git'}}
            policy={'schema':1,'root':str(home),'attempts':attempts,'total_seconds':28800,'pair_seconds':10800,'corrections':corrections}
            with mock.patch.object(common,'unlinked_path',side_effect=lambda path,**kw:Path(path)),mock.patch.object(common,'regular',return_value=b'input'),mock.patch.object(common,'read_json',side_effect=lambda path:policy if path.name=='campaign.json' else value),mock.patch.object(Path,'exists',return_value=True),self.assertRaisesRegex(RuntimeError,pattern):
                common.config('/input',digest(b'input'))
        # Reaching the next independent gate proves historical and new policy admission.
        check(2,['r00','r01','r02'],'r02','read/write overlap')
        check(3,['r00','r01','r02','r03'],'r03','read/write overlap')
        check(2,['r00','r01','r02','r03'],'r03','fixed campaign attempts')
        check(3,['r00','r01','r02'],'r02','fixed campaign attempts')
        check(3,['r00','r01','r02','r03'],'r04','campaign lane root')
        check(4,['r00','r01','r02','r03','r04'],'r04','read/write overlap')
        check(4,['r00','r01','r02','r03'],'r03','fixed campaign attempts')
        check(4,['r00','r01','r02','r03','r04'],'r05','campaign lane root')
        check(5,['r00','r01','r02','r03','r04','r05'],'r05','read/write overlap')
        check(5,['r00','r01','r02','r03','r04'],'r04','fixed campaign attempts')
        check(5,['r00','r01','r02','r03','r04','r05'],'r06','campaign lane root')
        check(6,['r00','r01','r02','r03','r04','r05','r06'],'r06','read/write overlap')
        check(6,['r00','r01','r02','r03','r04','r05'],'r05','fixed campaign attempts')
        check(6,['r00','r01','r02','r03','r04','r05','r06'],'r07','campaign lane root')
        check(7,['r00','r01','r02','r03','r04','r05','r06','r07'],'r07','read/write overlap')
        check(7,['r00','r01','r02','r03','r04','r05','r06'],'r06','fixed campaign attempts')
        check(7,['r00','r01','r02','r03','r04','r05','r06','r07'],'r08','campaign lane root')
        check(8,['r00','r01','r02','r03','r04','r05','r06','r07','r08'],'r08','read/write overlap')
        check(8,['r00','r01','r02','r03','r04','r05','r06','r07'],'r07','fixed campaign attempts')
        check(8,['r00','r01','r02','r03','r04','r05','r06','r07','r08'],'r09','campaign lane root')
        check(9,['r00','r01','r02','r03','r04','r05','r06','r07','r08','r09'],'r09','read/write overlap')
        check(9,['r00','r01','r02','r03','r04','r05','r06','r07','r08'],'r08','fixed campaign attempts')
        check(9,['r00','r01','r02','r03','r04','r05','r06','r07','r08','r09'],'r10','campaign lane root')
        check(10,['r00','r01','r02','r03','r04','r05','r06','r07','r08','r09','r10'],'r10','campaign shape/bounds')
        check(9.0,['r00','r01','r02','r03','r04','r05','r06','r07','r08','r09'],'r09','campaign shape/bounds')
        check(8.0,['r00','r01','r02','r03','r04','r05','r06','r07','r08'],'r08','campaign shape/bounds')
        check(7.0,['r00','r01','r02','r03','r04','r05','r06','r07'],'r07','campaign shape/bounds')
        check(6.0,['r00','r01','r02','r03','r04','r05','r06'],'r06','campaign shape/bounds')
        check(5.0,['r00','r01','r02','r03','r04','r05'],'r05','campaign shape/bounds')
        check(True,['r00','r01'],'r01','campaign shape/bounds')
        check(4.0,['r00','r01','r02','r03','r04'],'r04','campaign shape/bounds')
        check(3.0,['r00','r01','r02','r03'],'r03','campaign shape/bounds')

    def test_r04_second_core_correction_preserves_other_caps_and_failure_stop(self):
        root,c,note,old,_=self.correction_fixture()
        note.update(previous_attempt='r03',reason='failed-phase',affected_phases=[['current','focused','core']])
        oldref=note['prior_invocations'][0]
        prior={'r01':{'affected_phases':[['retained','focused','p1']]},
               'r02':{'affected_phases':[['current','smoke','base']]},
               'r03':{'affected_phases':[['current','focused','core']]}}
        def read(path):
            if path.name=='correction.json':return note if path.parent.name=='r04' else prior[path.parent.name]
            if path.name=='inputs.json':return {'invocations':{'current':oldref},'mode':'focused','slot':'core'}
            return {'inputs_sha256':digest(b'review'),'admission_only':False}
        failures=[('r00','retained','focused','p1'),('r01','current','smoke','base'),
                  ('r02','current','focused','core'),('r03','current','focused','core')]
        attempts={'r00','r01','r02','r03'}
        with mock.patch.object(campaign,'read_json',side_effect=read),mock.patch.object(campaign,'unlinked_path',side_effect=Path),mock.patch.object(campaign,'regular',return_value=b'review'),mock.patch.object(campaign,'config',return_value=(old,{'root':root/'r03/current'})),mock.patch.object(Path,'glob',return_value=[root/'r03/calls/current-focused-core']):
            for lane in ('current','retained'):
                self.assertIs(note,campaign.correction(root,'r04',c,lane,'selfcheck','base',failures,attempts))
            for fs,ats,pattern in ((failures+[('r04','current','focused','core')],attempts|{'r04'},'blocks all'),
                    (failures,attempts-{'r02'},'order'),
                    (failures+[('r03','current','focused','transition')],attempts,'unresolved')):
                with self.subTest(pattern=pattern),self.assertRaisesRegex(RuntimeError,pattern):
                    campaign.correction(root,'r04',c,'retained','acquire','base',fs,ats)
            for affected in ([['current','smoke','base']],[['retained','focused','p1']]):
                note['affected_phases']=affected
                with self.subTest(affected=affected),self.assertRaisesRegex(RuntimeError,'per affected phase'):
                    campaign.correction(root,'r04',c,'current','selfcheck','base',failures,attempts)
            note['affected_phases']=[['current','focused','core']]*2
            with self.assertRaisesRegex(RuntimeError,'duplicate'):
                campaign.correction(root,'r04',c,'current','selfcheck','base',failures,attempts)
            note['affected_phases']=[['current','focused','core']]
            prior['r02']['affected_phases'].append(['current','focused','core'])
            with self.assertRaisesRegex(RuntimeError,'per affected phase'):
                campaign.correction(root,'r04',c,'current','selfcheck','base',failures,attempts)

    def test_r05_third_core_correction_preserves_other_caps_and_failure_stop(self):
        root,c,note,old,_=self.correction_fixture()
        note.update(previous_attempt='r04',reason='failed-phase',affected_phases=[['current','focused','core']])
        oldref=note['prior_invocations'][0]
        prior={'r01':{'affected_phases':[['retained','focused','p1']]},
               'r02':{'affected_phases':[['current','smoke','base']]},
               'r03':{'affected_phases':[['current','focused','core']]},
               'r04':{'affected_phases':[['current','focused','core']]}}
        def read(path):
            if path.name=='correction.json':return note if path.parent.name=='r05' else prior[path.parent.name]
            if path.name=='inputs.json':return {'invocations':{'current':oldref},'mode':'focused','slot':'core'}
            return {'inputs_sha256':digest(b'review'),'admission_only':False}
        failures=[('r00','retained','focused','p1'),('r01','current','smoke','base'),
                  ('r02','current','focused','core'),('r03','current','focused','core'),('r04','current','focused','core')]
        attempts={'r00','r01','r02','r03','r04'}
        with mock.patch.object(campaign,'read_json',side_effect=read),mock.patch.object(campaign,'unlinked_path',side_effect=Path),mock.patch.object(campaign,'regular',return_value=b'review'),mock.patch.object(campaign,'config',return_value=(old,{'root':root/'r04/current'})),mock.patch.object(Path,'glob',return_value=[root/'r04/calls/current-focused-core']):
            for lane in ('current','retained'):
                self.assertIs(note,campaign.correction(root,'r05',c,lane,'selfcheck','base',failures,attempts))
            for fs,ats,pattern in ((failures+[('r05','current','focused','core')],attempts|{'r05'},'blocks all'),
                    (failures,attempts-{'r02'},'order'),
                    (failures+[('r03','current','focused','transition')],attempts,'unresolved')):
                with self.subTest(pattern=pattern),self.assertRaisesRegex(RuntimeError,pattern):
                    campaign.correction(root,'r05',c,'retained','acquire','base',fs,ats)
            for affected in ([['current','smoke','base']],[['retained','focused','p1']]):
                note['affected_phases']=affected
                with self.subTest(affected=affected),self.assertRaisesRegex(RuntimeError,'per affected phase'):
                    campaign.correction(root,'r05',c,'current','selfcheck','base',failures,attempts)
            note['affected_phases']=[['current','focused','core']]*2
            with self.assertRaisesRegex(RuntimeError,'duplicate'):
                campaign.correction(root,'r05',c,'current','selfcheck','base',failures,attempts)
            note['affected_phases']=[['current','focused','core']]
            prior['r02']['affected_phases'].append(['current','focused','core'])
            with self.assertRaisesRegex(RuntimeError,'per affected phase'):
                campaign.correction(root,'r05',c,'current','selfcheck','base',failures,attempts)

    def test_r06_transition_correction_preserves_core_three_and_other_caps(self):
        root,c,note,old,_=self.correction_fixture()
        note.update(previous_attempt='r05',reason='failed-phase',affected_phases=[['current','focused','transition']])
        oldref=note['prior_invocations'][0]
        prior={'r01':{'affected_phases':[['retained','focused','p1']]},
               'r02':{'affected_phases':[['current','smoke','base']]},
               'r03':{'affected_phases':[['current','focused','core']]},
               'r04':{'affected_phases':[['current','focused','core']]},
               'r05':{'affected_phases':[['current','focused','core']]}}
        def read(path):
            if path.name=='correction.json':return note if path.parent.name=='r06' else prior[path.parent.name]
            if path.name=='inputs.json':return {'invocations':{'current':oldref},'mode':'focused','slot':'transition'}
            return {'inputs_sha256':digest(b'review'),'admission_only':False}
        failures=[('r00','retained','focused','p1'),('r01','current','smoke','base'),
                  ('r02','current','focused','core'),('r03','current','focused','core'),
                  ('r04','current','focused','core'),('r05','current','focused','transition')]
        attempts={'r00','r01','r02','r03','r04','r05'}
        with mock.patch.object(campaign,'read_json',side_effect=read),mock.patch.object(campaign,'unlinked_path',side_effect=Path),mock.patch.object(campaign,'regular',return_value=b'review'),mock.patch.object(campaign,'config',return_value=(old,{'root':root/'r05/current'})),mock.patch.object(Path,'glob',return_value=[root/'r05/calls/current-focused-transition']):
            for lane in ('current','retained'):
                self.assertIs(note,campaign.correction(root,'r06',c,lane,'selfcheck','base',failures,attempts))
            for fs,ats,pattern in ((failures+[('r06','current','focused','transition')],attempts|{'r06'},'blocks all'),
                    (failures,attempts-{'r02'},'order'),
                    (failures+[('r05','current','focused','core')],attempts,'unresolved')):
                with self.subTest(pattern=pattern),self.assertRaisesRegex(RuntimeError,pattern):
                    campaign.correction(root,'r06',c,'retained','acquire','base',fs,ats)
            for affected in ([['current','smoke','base']],[['retained','focused','p1']],[['current','focused','core']]):
                note['affected_phases']=affected
                with self.subTest(affected=affected),self.assertRaisesRegex(RuntimeError,'per affected phase'):
                    campaign.correction(root,'r06',c,'current','selfcheck','base',failures,attempts)
            note['affected_phases']=[['current','focused','transition']]*2
            with self.assertRaisesRegex(RuntimeError,'duplicate'):
                campaign.correction(root,'r06',c,'current','selfcheck','base',failures,attempts)
            note['affected_phases']=[['current','focused','transition']]
            prior['r03']['affected_phases'].append(['current','focused','transition'])
            with self.assertRaisesRegex(RuntimeError,'per affected phase'):
                campaign.correction(root,'r06',c,'current','selfcheck','base',failures,attempts)

    def test_r07_transition_second_correction_preserves_core_three_and_other_caps(self):
        root,c,note,old,_=self.correction_fixture()
        note.update(previous_attempt='r06',reason='failed-phase',affected_phases=[['current','focused','transition']])
        oldref=note['prior_invocations'][0]
        prior={'r01':{'affected_phases':[['retained','focused','p1']]},
               'r02':{'affected_phases':[['current','smoke','base']]},
               'r03':{'affected_phases':[['current','focused','core']]},
               'r04':{'affected_phases':[['current','focused','core']]},
               'r05':{'affected_phases':[['current','focused','core']]},
               'r06':{'affected_phases':[['current','focused','transition']]}}
        def read(path):
            if path.name=='correction.json':return note if path.parent.name=='r07' else prior[path.parent.name]
            if path.name=='inputs.json':return {'invocations':{'current':oldref},'mode':'focused','slot':'transition'}
            return {'inputs_sha256':digest(b'review'),'admission_only':False}
        failures=[('r00','retained','focused','p1'),('r01','current','smoke','base'),
                  ('r02','current','focused','core'),('r03','current','focused','core'),
                  ('r04','current','focused','core'),('r05','current','focused','transition'),('r06','current','focused','transition')]
        attempts={'r00','r01','r02','r03','r04','r05','r06'}
        with mock.patch.object(campaign,'read_json',side_effect=read),mock.patch.object(campaign,'unlinked_path',side_effect=Path),mock.patch.object(campaign,'regular',return_value=b'review'),mock.patch.object(campaign,'config',return_value=(old,{'root':root/'r06/current'})),mock.patch.object(Path,'glob',return_value=[root/'r06/calls/current-focused-transition']):
            for lane in ('current','retained'):
                self.assertIs(note,campaign.correction(root,'r07',c,lane,'selfcheck','base',failures,attempts))
            for fs,ats,pattern in ((failures+[('r07','current','focused','transition')],attempts|{'r07'},'blocks all'),
                    (failures,attempts-{'r02'},'order'),
                    (failures+[('r05','current','focused','core')],attempts,'unresolved')):
                with self.subTest(pattern=pattern),self.assertRaisesRegex(RuntimeError,pattern):
                    campaign.correction(root,'r07',c,'retained','acquire','base',fs,ats)
            for affected in ([['current','smoke','base']],[['retained','focused','p1']],[['current','focused','core']]):
                note['affected_phases']=affected
                with self.subTest(affected=affected),self.assertRaisesRegex(RuntimeError,'per affected phase'):
                    campaign.correction(root,'r07',c,'current','selfcheck','base',failures,attempts)
            note['affected_phases']=[['current','focused','transition']]*2
            with self.assertRaisesRegex(RuntimeError,'duplicate'):
                campaign.correction(root,'r07',c,'current','selfcheck','base',failures,attempts)
            note['affected_phases']=[['current','focused','transition']]
            prior['r03']['affected_phases'].append(['current','focused','transition'])
            with self.assertRaisesRegex(RuntimeError,'per affected phase'):
                campaign.correction(root,'r07',c,'current','selfcheck','base',failures,attempts)

    def test_r08_transition_third_correction_preserves_core_three_and_other_caps(self):
        root,c,note,old,_=self.correction_fixture()
        note.update(previous_attempt='r07',reason='failed-phase',affected_phases=[['current','focused','transition']])
        oldref=note['prior_invocations'][0]
        prior={'r01':{'affected_phases':[['retained','focused','p1']]},
               'r02':{'affected_phases':[['current','smoke','base']]},
               'r03':{'affected_phases':[['current','focused','core']]},
               'r04':{'affected_phases':[['current','focused','core']]},
               'r05':{'affected_phases':[['current','focused','core']]},
               'r06':{'affected_phases':[['current','focused','transition']]},
               'r07':{'affected_phases':[['current','focused','transition']]}}
        def read(path):
            if path.name=='correction.json':return note if path.parent.name=='r08' else prior[path.parent.name]
            if path.name=='inputs.json':return {'invocations':{'current':oldref},'mode':'focused','slot':'transition'}
            return {'inputs_sha256':digest(b'review'),'admission_only':False}
        failures=[('r00','retained','focused','p1'),('r01','current','smoke','base'),
                  ('r02','current','focused','core'),('r03','current','focused','core'),
                  ('r04','current','focused','core'),('r05','current','focused','transition'),('r06','current','focused','transition'),('r07','current','focused','transition')]
        attempts={'r00','r01','r02','r03','r04','r05','r06','r07'}
        with mock.patch.object(campaign,'read_json',side_effect=read),mock.patch.object(campaign,'unlinked_path',side_effect=Path),mock.patch.object(campaign,'regular',return_value=b'review'),mock.patch.object(campaign,'config',return_value=(old,{'root':root/'r07/current'})),mock.patch.object(Path,'glob',return_value=[root/'r07/calls/current-focused-transition']):
            for lane in ('current','retained'):
                self.assertIs(note,campaign.correction(root,'r08',c,lane,'selfcheck','base',failures,attempts))
            for fs,ats,pattern in ((failures+[('r08','current','focused','transition')],attempts|{'r08'},'blocks all'),
                    (failures,attempts-{'r02'},'order'),
                    (failures+[('r05','current','focused','core')],attempts,'unresolved')):
                with self.subTest(pattern=pattern),self.assertRaisesRegex(RuntimeError,pattern):
                    campaign.correction(root,'r08',c,'retained','acquire','base',fs,ats)
            for affected in ([['current','smoke','base']],[['retained','focused','p1']],[['current','focused','core']]):
                note['affected_phases']=affected
                with self.subTest(affected=affected),self.assertRaisesRegex(RuntimeError,'per affected phase'):
                    campaign.correction(root,'r08',c,'current','selfcheck','base',failures,attempts)
            note['affected_phases']=[['current','focused','transition']]*2
            with self.assertRaisesRegex(RuntimeError,'duplicate'):
                campaign.correction(root,'r08',c,'current','selfcheck','base',failures,attempts)
            note['affected_phases']=[['current','focused','transition']]
            prior['r03']['affected_phases'].append(['current','focused','transition'])
            with self.assertRaisesRegex(RuntimeError,'per affected phase'):
                campaign.correction(root,'r08',c,'current','selfcheck','base',failures,attempts)

    def test_r09_transition_fourth_correction_preserves_core_three_and_other_caps(self):
        root,c,note,old,_=self.correction_fixture()
        note.update(previous_attempt='r08',reason='failed-phase',affected_phases=[['current','focused','transition']])
        oldref=note['prior_invocations'][0]
        prior={'r01':{'affected_phases':[['retained','focused','p1']]},
               'r02':{'affected_phases':[['current','smoke','base']]},
               'r03':{'affected_phases':[['current','focused','core']]},
               'r04':{'affected_phases':[['current','focused','core']]},
               'r05':{'affected_phases':[['current','focused','core']]},
               'r06':{'affected_phases':[['current','focused','transition']]},
               'r07':{'affected_phases':[['current','focused','transition']]},
               'r08':{'affected_phases':[['current','focused','transition']]}}
        def read(path):
            if path.name=='correction.json':return note if path.parent.name=='r09' else prior[path.parent.name]
            if path.name=='inputs.json':return {'invocations':{'current':oldref},'mode':'focused','slot':'transition'}
            return {'inputs_sha256':digest(b'review'),'admission_only':False}
        failures=[('r00','retained','focused','p1'),('r01','current','smoke','base'),
                  ('r02','current','focused','core'),('r03','current','focused','core'),
                  ('r04','current','focused','core'),('r05','current','focused','transition'),('r06','current','focused','transition'),('r07','current','focused','transition'),('r08','current','focused','transition')]
        attempts={'r00','r01','r02','r03','r04','r05','r06','r07','r08'}
        with mock.patch.object(campaign,'read_json',side_effect=read),mock.patch.object(campaign,'unlinked_path',side_effect=Path),mock.patch.object(campaign,'regular',return_value=b'review'),mock.patch.object(campaign,'config',return_value=(old,{'root':root/'r08/current'})),mock.patch.object(Path,'glob',return_value=[root/'r08/calls/current-focused-transition']):
            for lane in ('current','retained'):
                self.assertIs(note,campaign.correction(root,'r09',c,lane,'selfcheck','base',failures,attempts))
            for fs,ats,pattern in ((failures+[('r09','current','focused','transition')],attempts|{'r09'},'blocks all'),
                    (failures,attempts-{'r02'},'order'),
                    (failures+[('r05','current','focused','core')],attempts,'unresolved')):
                with self.subTest(pattern=pattern),self.assertRaisesRegex(RuntimeError,pattern):
                    campaign.correction(root,'r09',c,'retained','acquire','base',fs,ats)
            for affected in ([['current','smoke','base']],[['retained','focused','p1']],[['current','focused','core']]):
                note['affected_phases']=affected
                with self.subTest(affected=affected),self.assertRaisesRegex(RuntimeError,'per affected phase'):
                    campaign.correction(root,'r09',c,'current','selfcheck','base',failures,attempts)
            note['affected_phases']=[['current','focused','transition']]*2
            with self.assertRaisesRegex(RuntimeError,'duplicate'):
                campaign.correction(root,'r09',c,'current','selfcheck','base',failures,attempts)
            note['affected_phases']=[['current','focused','transition']]
            prior['r03']['affected_phases'].append(['current','focused','transition'])
            with self.assertRaisesRegex(RuntimeError,'per affected phase'):
                campaign.correction(root,'r09',c,'current','selfcheck','base',failures,attempts)

    def test_config_unknown_keys_versions_and_phase_refused(self):
        keys={'schema','phase','paths','runtime','git','source_files','controls','selection','collection_sha256','factory','source_digest','git_system_config','source_root_entries'}
        base={key:None for key in keys};base.update(schema=3,phase='base')
        invalid=[{**base,'extra':1},{k:v for k,v in base.items() if k!='paths'},
                 {**base,'schema':True},{**base,'schema':5},{**base,'phase':'delegation'}]
        with mock.patch.object(common,'unlinked_path',side_effect=lambda path,**kw:Path(path)),mock.patch.object(common,'regular',return_value=b'input'):
            for value in invalid:
                with self.subTest(value=value),mock.patch.object(common,'read_json',return_value=value),self.assertRaises(RuntimeError):
                    common.config('/input',digest(b'input'))
    def test_config_actual_control_hash_drift_refused(self):
        root=Path('/agent-worktrees/task');source=Path('/source');controls=source/'controls'
        c={'schema':3,'phase':'base','paths':{'source':str(source),'controls':str(controls),'root':str(root),'old':str(root/'old'),'exec':str(root/'exec'),'common_git':'/git'},
           'runtime':{},'git':{},'source_files':{},'controls':{'common.py':digest(b'expected')},'selection':[],'collection_sha256':None,'factory':False,'source_digest':'source','git_system_config':{},'source_root_entries':{}}
        with mock.patch.object(common,'unlinked_path',side_effect=lambda path,**kw:Path(path)),mock.patch.object(common,'regular',return_value=b'input'),mock.patch.object(common,'read_json',return_value=c),mock.patch.object(Path,'exists',return_value=False),mock.patch.object(Path,'glob',return_value=[controls/'common.py']),mock.patch.object(Path,'rglob',side_effect=lambda pattern:[] if pattern=='*.pyc' else [controls/'common.py']),mock.patch.object(Path,'is_file',return_value=True):
            with self.assertRaisesRegex(RuntimeError,'control drift: common.py'):common.config('/input',digest(b'input'))
    def test_physical_reserve_validation_and_scan_bound(self):
        valid={'st_mode':stat.S_IFREG|0o600,'st_nlink':1,'st_uid':campaign.os.geteuid(),'st_size':512*1024**2,'st_blocks':1024**2}
        with mock.patch.object(campaign,'unlinked_path',side_effect=Path):
            for delta in ({'st_nlink':2},{'st_size':1},{'st_blocks':0},{'st_mode':stat.S_IFLNK|0o777}):
                with self.subTest(delta=delta),mock.patch.object(Path,'lstat',return_value=mock.Mock(**(valid|delta))),self.assertRaisesRegex(RuntimeError,'physical campaign cleanup reserve'):
                    campaign.ResourceGuard(Path('/task/implementation'))
            with mock.patch.object(Path,'lstat',return_value=mock.Mock(**valid)):
                guard=campaign.ResourceGuard(Path('/task/implementation'))
                with mock.patch.object(campaign.os,'statvfs',return_value=mock.Mock(f_bavail=30*campaign.GIB,f_frsize=1)),mock.patch.object(campaign.os,'walk',return_value=[('/task',[],[str(n) for n in range(256)])]),mock.patch.object(campaign.time,'monotonic',side_effect=[0,4]):
                    with self.assertRaisesRegex(RuntimeError,'observation exceeded bound'):guard.check(admission=True)

    def test_storage_thresholds_are_fail_closed(self):
        for admission,logical,allocated,free in ((True,8,0,30),(True,0,8,30),(True,0,0,24),(False,12,0,30),(False,0,12,30),(False,0,0,14)):
            with self.subTest(admission=admission,logical=logical,allocated=allocated,free=free),self.assertRaises(RuntimeError):
                campaign.ResourceGuard.threshold({'logical_bytes':logical*campaign.GIB,'allocated_bytes':allocated*campaign.GIB,'free_bytes':free*campaign.GIB},admission)
        campaign.ResourceGuard.threshold({'logical_bytes':1,'allocated_bytes':1,'free_bytes':25*campaign.GIB},True)
    def test_prior_complete_binds_every_identity_and_parent(self):
        root=Path('/synthetic-root');lane='retained';mode='complete-normal';out=root/'r00/retained';data=b'prior'
        old={key:key for key in ('schema','phase','source_digest','controls','runtime','git','git_system_config','collection_sha256','factory','selection')}
        ref={key:{'path':str(path),'sha256':digest(data)} for key,path in {'invocation':root/'old-input','result':out/'exec/runs'/f'{mode}-final/result.json','parent_result':root/'r00/calls'/f'pair-{mode}-final/result.json'}.items()}
        note={'prior_invocations':[ref['invocation']]}
        parent={'inputs_sha256':digest(data),'process_cleanup_verified':True,'reusable_lanes':[lane]}
        inp={'mode':mode,'invocations':{lane:ref['invocation']}}
        with mock.patch.object(campaign,'unlinked_path',side_effect=Path),mock.patch.object(campaign,'regular',return_value=data),mock.patch.object(campaign,'config',return_value=(old,{'root':out,'exec':out/'exec'})),mock.patch.object(controller,'completed') as completion,mock.patch.object(campaign,'read_json',side_effect=lambda path:inp if path.name=='inputs.json' else parent):
            campaign.prior_complete(root,'r01',old,lane,mode,ref,note);completion.assert_called_once()
            for key in old:
                with self.subTest(key=key),self.assertRaisesRegex(RuntimeError,'changed evidence'):
                    campaign.prior_complete(root,'r01',{**old,key:'changed'},lane,mode,ref,note)
            parent['reusable_lanes']=[]
            with self.assertRaisesRegex(RuntimeError,'not reusable'):campaign.prior_complete(root,'r01',old,lane,mode,ref,note)
            parent['reusable_lanes']=[lane];parent['process_cleanup_verified']=False
            with self.assertRaisesRegex(RuntimeError,'not reusable'):campaign.prior_complete(root,'r01',old,lane,mode,ref,note)
        with self.assertRaisesRegex(RuntimeError,'merely to rename'):campaign.pair_budget({'retained':100,'current':100},0,1,reused=['retained','current'])

    def dispatch_mock(self, *, dac_failure=False, successful=False, overrun=False, accounting_only=False):
        root=Path('/synthetic-root');p={'root':root/'r00/retained','exec':root/'r00/retained/exec','controls':root/'controls'}
        c={'phase':'base','schema':3};written={};opened=mock.mock_open();now=[0]
        guard=mock.Mock(latest={'free_bytes':30*campaign.GIB},peak={});guard.check.return_value={}
        def run_child(*args,**kwargs):
            if not successful:raise RuntimeError('synthetic before Popen')
            now[0]=9999 if overrun else 1
            return True
        def read(path):
            if path.name=='campaign.json':return self.continuous_policy() if accounting_only else {'schema':1,'root':str(root),'attempts':['r00','r01','r02'],'total_seconds':28800,'pair_seconds':10800,'corrections':2}
            if path not in written:return {'group_absent':True,'cleanup_errors':[]}
            return written[path]
        with mock.patch.object(campaign,'read_json',side_effect=read),mock.patch.object(campaign,'regular',return_value=b'parent-input'),mock.patch.object(campaign,'unlinked_path',side_effect=Path),mock.patch.object(campaign,'elapsed',return_value=(0,[],set())),mock.patch.object(campaign,'correction',return_value=None),mock.patch.object(campaign,'ResourceGuard',return_value=guard),mock.patch.object(campaign.time,'monotonic',side_effect=lambda:now[0]),mock.patch.object(campaign,'exclusive_json',side_effect=lambda path,value:written.__setitem__(path,value)),mock.patch.object(Path,'open',opened),mock.patch.object(Path,'mkdir'),mock.patch.object(Path,'exists',return_value=False),mock.patch.object(campaign.fcntl,'flock'),mock.patch.object(controller,'preflight',side_effect=RuntimeError('canary positive-control DAC unavailable') if dac_failure else None),mock.patch.object(controller,'run',side_effect=run_child) as run:
            with self.assertRaises(RuntimeError if dac_failure else SystemExit):
                campaign.dispatch(c,p,root/'input','input-sha','canary','base',controller.time.monotonic())
            if dac_failure:run.assert_not_called()
        return [value for path,value in written.items() if path.name=='result.json'][0]
    def test_parent_aggregate_deadline_overrides_child_pass(self):
        result=self.dispatch_mock(successful=True,overrun=True)
        self.assertFalse(result['execution_pass']);self.assertEqual('aggregate-deadline-exhausted',result['error']);self.assertTrue(result['process_cleanup_verified'])
        self.assertTrue(self.dispatch_mock(successful=True)['execution_pass'])
    def test_dispatch_no_spawn_failure_is_not_permanent_unknown_cleanup(self):
        result=self.dispatch_mock()
        self.assertFalse(result['execution_pass']);self.assertFalse(result['spawned']);self.assertTrue(result['process_cleanup_verified'])
    def test_dispatch_canary_dac_rejects_before_execution_slot(self):
        result=self.dispatch_mock(dac_failure=True)
        self.assertTrue(result['admission_only']);self.assertTrue(result['process_cleanup_verified']);self.assertFalse(result['execution_pass'])
    def test_canary_dac_actual_predicate_rejects_readonly_target(self):
        p={'source':Path('/source'),'controls':Path('/controls'),'exec':Path('/exec'),'old':Path('/old')}
        info=mock.Mock(st_uid=controller.os.geteuid(),st_mode=0o100444)
        with mock.patch.object(controller,'unlinked_path',side_effect=lambda value:value),mock.patch.object(Path,'stat',return_value=info),mock.patch.object(controller.os,'access',return_value=True):
            with self.assertRaisesRegex(RuntimeError,'DAC unavailable'):controller.check_canary_dac({'schema':3},p,Path('/input'))

    def continuous_policy(self):
        return {'schema':2,'root':'/synthetic-root','attempts':None,'total_seconds':None,'pair_seconds':None,'corrections':None,'approval_sha256':'a'*64}
    def test_continuation_policy_requires_explicit_null_limits_and_exact_shape(self):
        policy=self.continuous_policy();self.assertTrue(common.campaign_limits_disabled(policy))
        for key,value in (('schema',True),('corrections',10),('attempts',['r00']),('total_seconds',float('inf')),('approval_sha256','x'*64)):
            with self.subTest(key=key),self.assertRaises(RuntimeError):common.campaign_limits_disabled({**policy,key:value})
        with self.assertRaises(RuntimeError):common.campaign_limits_disabled({**policy,'extra':True})
        for name in ('r9','r-1','r01/../r00','r０９','r001'):
            with self.subTest(name=name),self.assertRaises(RuntimeError):common.attempt_number(name)
        self.assertEqual(100,common.attempt_number('r100'))
    def test_continuation_large_or_unknown_estimates_do_not_become_caps_or_zero(self):
        for estimates in ({'current':999999,'retained':999999},{'current':None,'retained':None}):
            self.assertIsNone(campaign.pair_budget(estimates,999999,2,accounting_only=True))
        with self.assertRaises(RuntimeError):campaign.pair_budget({'current':float('nan'),'retained':1},0,1,accounting_only=True)
        with self.assertRaises(RuntimeError):campaign.pair_budget({'current':1,'retained':1},0,1,reused=('current','retained'),accounting_only=True)
    def test_continuation_allows_later_reviewed_correction_but_keeps_failure_and_order_gates(self):
        root,c,note,old,_=self.correction_fixture();note['previous_attempt']='r09';ref=note['prior_invocations'][0]
        def read(path):
            if path.name=='correction.json':return note if path.parent.name=='r10' else {'affected_phases':note['affected_phases']}
            if path.name=='inputs.json':return {'invocations':{'retained':ref},'mode':'canary','slot':'base'}
            return {'inputs_sha256':digest(b'review'),'admission_only':False}
        attempts={'r%02d'%n for n in range(10)}
        with mock.patch.object(campaign,'read_json',side_effect=read),mock.patch.object(campaign,'unlinked_path',side_effect=Path),mock.patch.object(campaign,'regular',return_value=b'review'),mock.patch.object(campaign,'config',return_value=(old,{'root':root/'r09/retained'})),mock.patch.object(Path,'glob',return_value=[root/'r09/calls/retained-canary-base']):
            self.assertIs(note,campaign.correction(root,'r10',c,'retained','canary','base',[],attempts,policy=self.continuous_policy()))
            with self.assertRaisesRegex(RuntimeError,'blocks all'):campaign.correction(root,'r10',c,'retained','canary','base',[('r10','retained','canary','base')],attempts,policy=self.continuous_policy())
            with self.assertRaisesRegex(RuntimeError,'order'):campaign.correction(root,'r10',c,'retained','canary','base',[],attempts-{'r04'},policy=self.continuous_policy())
    def test_continuation_elapsed_discovers_later_attempt_without_losing_history(self):
        root=Path('/synthetic-root');raw=b'bound';h=digest(raw)
        values={'r00':1.0,'r09':2.0,'r10':3.0,'r100':4.0}
        def glob(path,pattern):
            if path==root:return [root/name for name in values]
            return [path/'call'] if path.parent.name in values else []
        def read(path):
            if path.name=='inputs.json':return {'lane':'current','mode':'focused','slot':'core','correction_sha256':h}
            return {'inputs_sha256':h,'seconds':values[path.parents[2].name],'execution_pass':False,'process_cleanup_verified':True}
        with mock.patch.object(Path,'is_dir',return_value=True),mock.patch.object(Path,'is_symlink',return_value=False),mock.patch.object(Path,'glob',autospec=True,side_effect=glob),mock.patch.object(campaign,'unlinked_path',side_effect=Path),mock.patch.object(Path,'is_file',return_value=True),mock.patch.object(campaign,'regular',return_value=raw),mock.patch.object(campaign,'read_json',side_effect=read):
            total,failures,attempts=campaign.elapsed(root)
        self.assertEqual(10,total);self.assertEqual(set(values),attempts);self.assertEqual(['r00','r09','r10','r100'],[x[0] for x in failures])
    def test_continuation_unlimited_phase_still_reaps_exact_group_with_fresh_cleanup_window(self):
        child=mock.Mock(pid=4242,returncode=0)
        with mock.patch.object(controller.os,'killpg',side_effect=ProcessLookupError),mock.patch.object(controller.time,'monotonic',return_value=999999):
            reason,natural,absent,errors=controller.settle_child(child,0,None,None,True)
        self.assertIsNone(reason);self.assertTrue(natural);self.assertTrue(absent);self.assertEqual([],errors)
        child.wait.assert_called_once_with(timeout=20)
    def test_continuation_elapsed_time_alone_does_not_reject_complete_evidence(self):
        child=mock.Mock(returncode=0);records=[]
        with mock.patch.object(controller,'config'),mock.patch.object(controller,'verify_old'),mock.patch.object(controller,'regular',return_value=b'inputs'),mock.patch.object(controller,'partial_child_evidence',return_value={}),mock.patch.object(controller,'child_evidence',return_value={'counts.json':'sealed'}),mock.patch.object(controller,'exclusive_json',side_effect=lambda p,v:records.append(v)),mock.patch.object(controller.time,'monotonic',return_value=999999):
            ok=controller.write_result({}, {'old':Path('/old')},Path('/input'),'sha',Path('/out'),digest(b'inputs'),None,{},'source',child,0,None,'complete-normal','final',None,True,True,[])
        self.assertTrue(ok);self.assertEqual(999999,records[0]['seconds']);self.assertEqual({'counts.json':'sealed'},records[0]['child_evidence'])

    def test_continuation_dispatch_ignores_only_aggregate_deadlines(self):
        self.assertTrue(self.dispatch_mock(successful=True,overrun=True,accounting_only=True)['execution_pass'])
        self.assertFalse(self.dispatch_mock(accounting_only=True)['execution_pass'])
        refused=self.dispatch_mock(dac_failure=True,accounting_only=True)
        self.assertTrue(refused['admission_only']);self.assertFalse(refused['execution_pass'])

    def test_continuation_attempt_discovery_ignores_files_but_rejects_aliases(self):
        root=Path('/synthetic-root')
        names=['r09-runtime-environment.json','r08-C08.patch','r09-continuation-launcher-identity.json','r10','r100','r11']
        with mock.patch.object(Path,'glob',return_value=[root/n for n in names]),mock.patch.object(Path,'is_symlink',return_value=False),mock.patch.object(Path,'is_dir',autospec=True,side_effect=lambda p:p.name in {'r10','r100'}):
            self.assertEqual(['r%02d'%n for n in range(11)]+['r100'],campaign.attempt_names(root))
        with mock.patch.object(Path,'glob',return_value=[root/'r001']),mock.patch.object(Path,'is_symlink',return_value=False),mock.patch.object(Path,'is_dir',return_value=True):
            with self.assertRaisesRegex(RuntimeError,'campaign attempt name'):campaign.attempt_names(root)
        with mock.patch.object(Path,'glob',return_value=[root/'r10']),mock.patch.object(Path,'is_symlink',return_value=True):
            with self.assertRaisesRegex(RuntimeError,'linked campaign attempt'):campaign.attempt_names(root)

if __name__=='__main__':
    require_isolated()
    unittest.main()
