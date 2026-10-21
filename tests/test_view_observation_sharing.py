"""Observation-local sharing: installed writer data and explicit filesystem races."""
from __future__ import annotations
import copy
from contextlib import contextmanager
import json
from pathlib import Path
import shutil
import subprocess
import unittest
from unittest.mock import patch

from hv2ref import product, view, workspace
from hv2ref.intent import workspace_intents
from hv2ref.work import WorkStore, read_work
import test_productization_safety as fixtures
import test_worktree_execution as worker_fixtures
import test_umbrella_lifecycle as umbrella_fixtures


class ViewObservationSharingTests(unittest.TestCase):
    POINTS = ('after-graphs', 'render', 'before-after')

    def setUp(self):
        self.f = fixtures.ActualWorkspaceInitTests()
        self.f.setUp(); self.addCleanup(self.f.doCleanups)
        self.target = self.f.target
        (self.target/'a').write_bytes(b'after\n')
        self.f.apply_init(self.f.preview())
        self.intent = self.f.accept_intent()
        original_call = self.f.call
        def capture_current(command, *args, **kwargs):
            if list(command[:2]) == ['work','apply']:
                self.pre_apply_current = (self.target/'.hrn/work/work-a/current.json').read_bytes()
            return original_call(command,*args,**kwargs)
        self.f.call = capture_current
        self.f.complete_work(intent_ref=self.intent)
        self.f.call = original_call
        self.events = self.f.base/'race-evidence'; self.events.mkdir()

    @staticmethod
    def legacy_observe(target):
        status = product.workspace_status(target)
        if status['classification'] in ('degraded', 'uninitialized', 'incompatible', 'unstable'):
            return status, {}, {}
        if not (target/'.hrn/format.json').is_file(): return status, {}, {}
        return status, WorkStore(target)._all(), workspace_intents(target)

    @contextmanager
    def injection(self, point, mutation):
        helper = view._workspace_status_observation
        observed = view._observe
        rendered = view._product
        fired = []
        mutated_snapshot = []
        count = 0
        def change():
            if not fired:
                mutation(); fired.append(point)
                mutated_snapshot.append(fixtures.exact_snapshot(self.target))
        def after_graphs(target):
            result = helper(target)
            if result[1] is not None: change()
            return result
        def during_render(target):
            result = rendered(target); change(); return result
        def before_after(target):
            nonlocal count
            count += 1
            if count == 2: change()
            return observed(target)
        name, replacement = {'after-graphs': ('_workspace_status_observation', after_graphs),
                             'render': ('_product', during_render),
                             'before-after': ('_observe', before_after)}[point]
        with patch.object(view, name, replacement): yield fired
        self.assertEqual([point], fired)
        self.assertEqual(mutated_snapshot[0], fixtures.exact_snapshot(self.target))

    def corrupt(self, path, *, remove=False, expected=10):
        original = path.read_bytes()
        for point in self.POINTS:
            with self.subTest(path=str(path.relative_to(self.target)), point=point):
                def mutation():
                    if remove: path.unlink()
                    else: path.write_bytes(b'{}\n')
                with self.injection(point, mutation):
                    out, code = view.render_view(self.target)
                (self.events/(point+'-'+path.name+'.json')).write_text(json.dumps({
                    'path':str(path.relative_to(self.target)), 'point':point,
                    'bytes_after': None if remove else path.read_text(), 'exit':code, 'output':out}))
                self.assertEqual(expected, code, out)
                self.assertNotIn('classification: pass', out)
                self.assertIn('classification: degraded', out)
                self.assertNotIn('Observation unstable', out)
                path.write_bytes(original)
        self.assertEqual('pass', product.workspace_status(self.target)['classification'])

    def test_status_helper_branch_parity(self):
        status, bundle = product._workspace_status_observation(self.target)
        self.assertEqual(product.workspace_status(self.target), status)
        self.assertIsNotNone(bundle)
        self.assertEqual(status['work_states'], {k:g['state'] for k,g in bundle[0].items()})
        self.assertEqual(status['intent_count'], len(bundle[1]))
        for path in (self.target/'.hrn/product/binding.json', self.target/'.hrn/format.json'):
            original = path.read_bytes(); path.write_bytes(b'{}\n')
            a, graphs = product._workspace_status_observation(self.target)
            self.assertEqual(a, product.workspace_status(self.target)); self.assertIsNone(graphs)
            path.write_bytes(original)
        empty = self.f.base/'empty'; empty.mkdir()
        self.assertEqual('uninitialized', product._workspace_status_observation(empty)[0]['classification'])
        self.assertIsNone(product._workspace_status_observation(empty)[1])

    def test_no_graph_alias_between_status_and_observations(self):
        first = view._observe(self.target); second = view._observe(self.target)
        self.assertEqual(first, second)
        def identities(value):
            result = set()
            if isinstance(value, (dict,list,tuple)):
                result.add(id(value))
                for child in value.values() if isinstance(value,dict) else value: result |= identities(child)
            return result
        self.assertFalse(identities(first) & identities(second))
        self.assertFalse(identities(first[0]) & identities(first[1:]))
        preserved = copy.deepcopy(second)
        first[1]['work-a']['state'] = 'consumer-tamper'
        self.assertEqual(preserved, second)
        self.assertEqual('completed', first[0]['work_states']['work-a'])
        self.assertEqual(preserved, view._observe(self.target))

    def consumers(self, target, wid, ticket=None):
        works = WorkStore(target)._all(); intents = workspace_intents(target)
        runtime = product.verify_workspace_product(target)
        before = copy.deepcopy((works,intents)); files = fixtures.exact_snapshot(target)
        view._work(target,works[wid],None,runtime,intents,works)
        if ticket is not None: view._confirmation(target,ticket,works,intents,runtime)
        current = view._current_revision(works[wid])
        revision = works[wid]['revisions'][current]
        view._umbrella_lines(target,revision,works[wid],works,intents)
        self.assertEqual(before,(works,intents)); self.assertEqual(files,fixtures.exact_snapshot(target))

    def test_consumers_preserve_input_graphs(self):
        request={'work_id':'work-a','action':'revoke','actor':'owner','reason':'fixture',
                 'request_id':'observe-revoke','observed_at':self.f.TIME,'revision_ref':None,
                 'supersedes':read_work(self.target,'work-a')['selections'][read_work(self.target,'work-a')['current']['selection_ref']['id']]['decision_ref']}
        ticket=json.loads(self.f.installed(['work','prepare'],request).stdout)['ticket']
        self.consumers(self.target,'work-a',ticket)
        worker=worker_fixtures.InstalledWorkerPublicationTests()
        worker.setUp(); self.addCleanup(worker.doCleanups)
        p=worker.prepare_worker_result(); self.consumers(worker.target,'work-a',p['ticket'])
        parent=umbrella_fixtures.InstalledUmbrellaLifecycleTests()
        parent.setUp(); self.addCleanup(parent.doCleanups)
        parent.apply_init(parent.preview()); child=parent.accept(parent.draft())
        parent.composition={'parent':parent.q('work','parent'),'required_children':[
            {'work':parent.q('work','child-a'),'intent':parent.q('intent','intent-a')}]}
        draft={**parent.draft(intent_id='parent-intent'),'schema_version':2,'composition':parent.composition}
        bound=parent.accept(draft); parent.publish('parent',bound,'start',parent=True)
        self.consumers(parent.target,'parent'); parent.success=True

    def test_continuation_reuses_observation_readers_and_target_race_remains_unavailable(self):
        from hv2ref import intent
        self.f.complete_work("work-b",intent_ref=self.intent)
        subprocess.run(["git","init","-q",str(self.target)],check=True,timeout=30,capture_output=True)
        def measure():
            with patch.object(workspace,"_topology_probe",wraps=workspace._topology_probe) as topology, \
                 patch.object(intent,"read_workspace_intent_graph",wraps=intent.read_workspace_intent_graph) as intents:
                status,bundle=product._workspace_status_observation(self.target)
            self.assertEqual("pass",status["classification"]);self.assertIsNotNone(bundle)
            return topology.call_count,intents.call_count
        baseline=measure()
        packet=json.loads(self.f.installed(["continuation","prepare"],dict(
            work_id="work-a",action="select",actor="owner",owner_statement="Synthetic Owner",
            reason="Inspect target",request_id="observation-link",observed_at=self.f.TIME,
            choice={"kind":"work","target_work_id":"work-b"})).stdout)
        self.f.installed(["continuation","apply","--confirm",packet["confirm_token"]],packet["ticket"])
        self.assertEqual(baseline,measure())
        # Adding a selected continuation must not hide a changed target base Work.
        self.corrupt(self.target/".hrn/work/work-b/current.json")
        from hv2ref import continuation
        from hv2ref.errors import ContractError
        current=self.target/".hrn/work/work-a/current.json";saved=current.read_bytes()
        def change_base_and_refuse(*args,**kwargs):
            current.write_bytes(self.pre_apply_current)
            raise ContractError("HV2-CONTINUATION","synthetic continuation observation refusal")
        errors={}
        try:
            with patch.object(continuation,"read_continuation",side_effect=change_base_and_refuse):
                with self.assertRaisesRegex(ContractError,"base Work changed"):
                    read_work(self.target,"work-a",_continuation_errors=errors)
            self.assertEqual({},errors)
        finally:
            current.write_bytes(saved)

    def test_pass_reuses_only_observation_local_graphs(self):
        original = WorkStore._all; calls=[]
        def spy(store, **kwargs): calls.append(store); return original(store, **kwargs)
        with patch.object(WorkStore,'_all',spy):
            out,code=view.render_view(self.target,kind='work',object_id='work-a')
        self.assertEqual(0,code,out); self.assertEqual(2,len(calls))
        with patch.object(view,'_observe',self.legacy_observe), patch.object(WorkStore,'_all',spy):
            prior,oldcode=view.render_view(self.target,kind='work',object_id='work-a')
        self.assertEqual((out,code),(prior,oldcode)); self.assertEqual(6,len(calls))

    def test_pending_unsupported_detached_keep_fallback(self):
        with patch.object(workspace,'runtime_supported',return_value=False):
            status,bundle=product._workspace_status_observation(self.target)
            self.assertEqual('unsupported',status['classification']); self.assertIsNone(bundle)
            self.assertEqual(self.legacy_observe(self.target), view._observe(self.target))
        # Restore the actual writer's pre-apply selector to observe a pending final selection.
        path=self.target/'.hrn/work/work-a/current.json'
        raw=path.read_bytes(); path.write_bytes(self.pre_apply_current)
        status,bundle=product._workspace_status_observation(self.target)
        self.assertIsNone(bundle); self.assertEqual('partial',status['classification'])
        self.assertEqual(self.legacy_observe(self.target), view._observe(self.target))
        path.write_bytes(raw)
        self.f.detach_apply(self.f.detach_preview())
        status,bundle=product._workspace_status_observation(self.target)
        self.assertEqual('detached',status['classification']); self.assertIsNone(bundle)
        self.assertEqual(self.legacy_observe(self.target),view._observe(self.target))

    def test_persistent_record_corruption_at_three_points(self):
        self.corrupt(self.target/'.hrn/work/work-a/revisions/revision-2.json')

    def test_valid_record_transition_at_three_points(self):
        for number,point in enumerate(self.POINTS):
            draft={**self.f.draft(),'intent_id':f'intent-extra-{number}'}
            with self.injection(point,lambda:self.f.installed(['intent','draft'],draft)):
                out,code=view.render_view(self.target)
            self.assertEqual(0,code,out); self.assertIn(f'intent-extra-{number}',out)
            self.assertEqual((out,code),view.render_view(self.target))

    def test_current_change_at_three_points(self):
        self.corrupt(self.target/'.hrn/work/work-a/current.json')

    def test_intent_acceptance_change_at_three_points(self):
        root=self.target/'.hrn/intents/intent-a'
        self.corrupt(next((root/'acceptances').glob('*.json')))
        self.corrupt(root/'drafts/draft-a.json')

    def test_product_binding_change_at_three_points(self):
        self.corrupt(self.target/'.hrn/product/binding.json')

    def test_ignore_change_at_three_points(self):
        subprocess.run(['git','init','-q',str(self.target)],check=True,timeout=30,capture_output=True)
        path=self.target/'.git/info/exclude'; original=path.read_bytes()
        for point in self.POINTS:
            with self.injection(point,lambda:path.write_bytes(original+b'\n.hrn/\n')):
                out,code=view.render_view(self.target)
            self.assertEqual(10,code,out); self.assertIn('degraded',out)
            self.assertIn('classification: degraded',out)
            self.assertNotIn('Observation unstable',out)
            path.write_bytes(original)

    def test_content_change_at_three_points(self):
        path=self.target/'a'
        for point in self.POINTS:
            path.write_bytes(b'after\n')
            with self.injection(point,lambda:path.write_bytes(b'content drift\n')):
                out,code=view.render_view(self.target,kind='work',object_id='work-a')
            self.assertEqual(0,code,out)
            expected='matches stored result' if point=='before-after' else 'stale: current files differ'
            self.assertIn(expected,out)
            self.assertIn('stale: current files differ',view.render_view(self.target,kind='work',object_id='work-a')[0])

    def test_format_removal_at_three_points(self):
        # Removing format from an otherwise populated root is integrity failure, not empty bootstrap.
        self.corrupt(self.target/'.hrn/format.json',remove=True)

    def test_repeated_change_exhausts_retry(self):
        draft={**self.f.draft(),'intent_id':'intent-toggle'}
        self.f.installed(['intent','draft'],draft)
        path=self.target/'.hrn/intents/intent-toggle'; saved=self.f.base/'saved-toggle'; shutil.copytree(path,saved)
        original=view._observe; count=[]
        def changing(target):
            if path.exists(): shutil.rmtree(path)
            else: shutil.copytree(saved,path)
            count.append(1); return original(target)
        with patch.object(view,'_observe',changing): out,code=view.render_view(self.target)
        self.assertEqual(4,len(count)); self.assertEqual(10,code); self.assertIn('Observation unstable',out)

    def test_stationary_source_output_exact_parity(self):
        before=fixtures.exact_snapshot(self.target)
        for kw in ({},{'kind':'work','object_id':'work-a'},{'kind':'intent','object_id':'intent-a'}):
            actual=view.render_view(self.target,**kw)
            with patch.object(view,'_observe',self.legacy_observe): expected=view.render_view(self.target,**kw)
            self.assertEqual(expected,actual)
        self.assertEqual(before,fixtures.exact_snapshot(self.target))
