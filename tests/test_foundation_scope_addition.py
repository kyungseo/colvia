"""User-approved scope changes use an existing Work and preserve its original evidence."""
import base64
from unittest import TestCase
from unittest.mock import patch

from colvia.cli import dispatch, parser
from colvia.codec import RecordError
from colvia.presentation import human
from colvia.records import link
from test_foundation_work import WorkFixture
from test_foundation_git_integration import IntegrationFixture, AUTHOR


class ScopeCommands:
    def action(self, name, *options, operation='change'):
        args = parser(managed=True).parse_args(['--operation', operation, 'ordinary', name, 'report', *options])
        return dispatch(args, self.store, self.service.workspace)

    def preview(self, *options):
        return self.action('scope-preview', '--reason', '검사 자료 보강', *options)

    def approve(self, receipt, *options, operation='change'):
        return self.action('scope-apply', '--reason', '검사 자료 보강', '--receipt', receipt,
                           '--statement', '표 수정과 부록 생성을 승인합니다', *options, operation=operation)

    def note(self, operation='note'):
        from colvia.progress import save
        return save(self.service, 'report', operation, self.service.view('report')['progress_receipt'],
                    dict(done='초안',checked='미실행',remaining='출처 확인',next_action='표 대조'))


class ScopeTests(ScopeCommands, WorkFixture, TestCase):
    def test_mixed_scope_preserves_note_originals_and_protects_submission(self):
        a,b,c = [self.root/p for p in ('report.md','table.md','appendix.md')]
        a.write_text('original A')
        b.write_text('original B')
        self.start()
        a.write_text('edited A')
        self.note()
        previous = self.store.head('work:report')
        root = self.store.root().ref
        delta = ['--edit',b.name,'--create',c.name,'--check','부록 확인']
        preview = self.preview(*delta)
        self.assertIn('이전 실행기', human(preview))
        self.assertEqual(root,self.store.root().ref)
        self.note('newer-note')
        memo = self.store.head('progress:report')
        self.approve(preview['receipt'],*delta)
        self.assertFalse(c.exists())
        self.assertEqual('edited A',a.read_text())
        self.assertEqual(memo,self.store.head('progress:report'))
        _,head=self.service._head('report')
        self.assertEqual(previous,link(head,'previous'))
        self.assertEqual(previous,link(self.service._object(link(head,'approval')),'basis'))
        view=self.service.view('report')
        self.assertEqual(view['progress']['files'],[dict(path=a.name,status='unchanged')])
        self.assertEqual(view['progress']['added_after_note'],[c.name,b.name])
        self.assertEqual(view['scope_additions'][0]['create'],[c.name])
        with self.assertRaises(RecordError):
            self.approve(preview['receipt'],*delta,operation='duplicate')
        extra = self.preview('--create','index.md')
        self.assertFalse(extra['first_scope_addition'])
        self.approve(extra['receipt'],'--create','index.md',operation='another')
        b.write_text('new table')
        c.write_text('appendix')
        self.note('after-addition')
        self.assertTrue(self.service.view('report')['progress']['same_approval'])
        checks = [dict(name=k,status='passed',detail='확인') for k in view['checks']]
        with self.assertRaisesRegex(RecordError,'check-report-mismatch'):
            self.submit()
        d=self.root/'other.md'
        d.write_text('independent change')
        with self.assertRaisesRegex(RecordError,'outside-scope-change'):
            self.service.submit(work='report',operation='outside',summary='수정',checks=checks)
        d.unlink()
        result=self.service.submit(work='report',operation='submit-all',summary='수정',checks=checks)
        self.assertEqual([c.name,a.name,b.name],result['files'])
        self.assertEqual('original A',self.service.result_content('report',a.name)['before']['text'])
        self.assertEqual('original B',self.service.result_content('report',b.name)['before']['text'])
        content=self.service.result_content('report',c.name)
        self.assertFalse(content['before']['exists'])
        self.assertEqual(content['before_basis'],'absent-at-additional-approval')
        self.assertIn('추가 승인 시점', human(content))
        self.service.accept(work='report',operation='accept',receipt=result['receipt'],statement='모두 수락')
        self.assertEqual('completed',self.service.view('report')['state'])
        with self.assertRaisesRegex(RecordError,'scope-first-submission-only'):
            self.preview('--create','other.md')

    def test_amendment_cannot_replace_goal_or_drop_an_old_check(self):
        from colvia.records import record
        from colvia.scope_addition import validate_content
        self.start()
        self.approve(self.preview('--create','appendix.md')['receipt'],'--create','appendix.md')
        _,head=self.service._head('report')
        approved=self.service._object(link(head,'approval'))
        plan=self.service._object(link(head,'plan'))
        from colvia.scope_addition import validate_active_link
        basis=self.service._object(link(approved,'basis'))
        forged_head=self.service._head_record(plan.ref,plan.payload,'active',approval=approved.ref,
                                               previous=link(basis,'previous'))
        with self.assertRaisesRegex(RecordError,'scope-history-mismatch'):
            validate_active_link(forged_head[0],lambda ref:forged_head[1] if ref==forged_head[0] else self.store.load(ref))
        for alteration in [dict(goal='different'),dict(checks=plan.payload['checks'][:1]),dict(excludes=[])]:
            data={k:v for k,v in plan.payload.items() if k!='links'} | alteration
            forged_plan=record('work.plan',data,{k:('integrity',link(plan,k)) for k in ('baseline','before')})
            forged=record('work.approval',{k:v for k,v in approved.payload.items() if k!='links'},
                          {'plan':('decision',forged_plan[0]),'basis':('decision',link(approved,'basis'))},version=2)
            objects=dict([forged_plan,forged])
            with self.subTest(alteration=alteration),self.assertRaisesRegex(RecordError,'scope-history-mismatch'):
                validate_content(forged[0],lambda ref:objects[ref] if ref in objects else self.store.load(ref))

    def test_previous_note_keeps_its_128_observations_when_new_path_sorts_first(self):
        from colvia.progress import MAX_PATHS
        paths=[f'r-{i:03}.md' for i in range(MAX_PATHS+1)]
        self.start(scope=paths)
        self.note()
        self.approve(self.preview('--create','appendix.md')['receipt'],'--create','appendix.md')
        view=self.service.view('report')['progress']
        self.assertEqual({row['path'] for row in view['files']},set(paths[:MAX_PATHS]))
        self.assertEqual(view['added_after_note'],['appendix.md'])
        self.assertEqual(view['additional_paths_unavailable'],1)

    def test_rejects_changed_absent_occupied_and_aliases(self):
        b=self.root/'table.md'
        b.write_text('before')
        (self.root/'Docs').mkdir()
        (self.root/'Docs'/'empty').mkdir()
        self.start()
        root=self.store.root().ref
        b.write_text('after')
        for flag,path in [('--edit',b.name),('--create',b.name),('--edit','missing'),('--create','Docs/empty'),
                          ('--create','docs/readme'),('--create','.git/config'),('--create','secrets/token'),
                          ('--create','Docs/missing/child'),('--create','REPORT.md')]:
            with self.subTest(path=path), self.assertRaises(RecordError):
                self.preview(flag,path)
        b.unlink()
        with self.assertRaisesRegex(RecordError,'scope-create-occupied'):
            self.preview('--create',b.name)
        self.assertEqual(root,self.store.root().ref)

    def test_unknown_reader_and_mixed_backup_roundtrip(self):
        from io import BytesIO
        from pathlib import Path
        from colvia.backup import ExportBudget, ImportedSnapshot, supported_requirements, write_export
        from colvia.graph import AuditBudget, GraphAudit, Registry
        from colvia.storage.restore import fill_candidate
        from colvia.storage.sqlite import GenerationStore
        from colvia.work import WorkService
        from test_foundation_binding import P,I

        (self.root/'table.md').write_text('원문')
        self.start()
        self.note()
        note, active = self.store.head('progress:report'),self.store.head('work:report')
        reg=self.service.registry
        old=Registry([v for k,v in reg._schemas.items() if k!=('work.approval',2)])
        caps, earlier = supported_requirements(reg),supported_requirements(old)
        reader=GenerationStore(self.store.path,project=P,instance=I,generation='g',active_check=lambda:None,
                               reader_capabilities=earlier,writer_capabilities=earlier)
        self.addCleanup(reader.close)
        delta=['--edit','table.md','--create','appendix.md']
        preview=self.preview(*delta)
        self.assertEqual(reader.head('work:report'),active)
        self.approve(preview['receipt'],*delta)
        with self.assertRaisesRegex(RecordError,'store-reader-capability-unavailable'):
            reader.root()
        with self.assertRaisesRegex(RecordError,'store-reader-capability-unavailable'):
            reader.commit_heads(operation='oldwrite',expected={},changes={},objects=[],validate=lambda _:None)
        base=Path(self.tmp.name)
        budget=AuditBudget(50000,100000,64*1024**2)
        audit=GraphAudit(base/'audit',budget)
        self.addCleanup(audit.close)
        audit.run(self.store.root().ref,self.store.load,reg,require_known=True)
        output=BytesIO()
        write_export(output,project=P,audit=audit,load=self.store.load)
        def imported(name,registry,capabilities):
            return ImportedSnapshot(base/name,BytesIO(output.getvalue()),budget=ExportBudget(50000,64*1024**2),
                                    graph_budget=budget,registry=registry,capabilities=capabilities,
                                    writable_capabilities=capabilities)
        with self.assertRaisesRegex(RecordError,'import-capability-unavailable'):
            imported('old',old,earlier)
        saved=imported('new',reg,caps)
        self.addCleanup(saved.close)
        restored=GenerationStore.create(base/'restored.sqlite3',project=P,instance='copy',generation='copy',
                    active_check=lambda:None,reader_capabilities=caps,writer_capabilities=caps)
        self.addCleanup(restored.close)
        fill_candidate(restored,saved,operation='import',unselected=lambda:None)
        self.assertEqual(restored.head('progress:report'),note)
        service=WorkService(restored,self.workspace)
        state=service.view('report')
        self.assertEqual(state['scope_additions'][0]['create'],['appendix.md'])
        self.assertEqual(restored.load(active),self.store.load(active))
        self.assertFalse((self.root/'appendix.md').exists())

    def test_submit_or_external_write_before_commit_does_not_grant_scope(self):
        self.start()
        receipt=self.preview('--create','appendix.md')['receipt']
        from colvia.scope_addition import apply
        def apply_bound(operation):
            return apply(self.service,'report',operation,[],['appendix.md'],[],'검사 자료 보강',receipt,'승인')
        publish=self.service._publish
        def race(*args,**kwargs):
            (self.root/'appendix.md').write_text('someone else')
            return publish(*args,**kwargs)
        head=self.store.head('work:report')
        with patch.object(self.service,'_publish',side_effect=race),self.assertRaisesRegex(RecordError,'scope-create-occupied'):
            apply_bound('race-file')
        self.assertEqual(head,self.store.head('work:report'))
        (self.root/'appendix.md').unlink()
        (self.root/'report.md').write_text('ready')
        def racing_submit(*args,**kwargs):
            with patch.object(self.service,'_publish',publish):
                self.submit()
            return publish(*args,**kwargs)
        with patch.object(self.service,'_publish',side_effect=racing_submit),self.assertRaises(RecordError):
            apply_bound('race-submit')
        self.assertEqual(self.service.view('report')['state'],'review')
        self.assertNotIn('scope_additions',self.service.view('report'))

    def test_observation_and_approval_races(self):
        self.start()
        (self.root/'docs').mkdir()
        p=self.preview('--create','docs/appendix')
        (self.root/'docs').rename(self.root/'old')
        (self.root/'docs').mkdir()
        with self.assertRaisesRegex(RecordError,'scope-preview-stale'):
            self.approve(p['receipt'],'--create','docs/appendix')
        p=self.preview('--create','docs/appendix')
        (self.root/'docs'/'appendix').write_text('external')
        with self.assertRaisesRegex(RecordError,'scope-create-occupied'):
            self.approve(p['receipt'],'--create','docs/appendix')
        p=self.preview('--create','other')
        with self.assertRaisesRegex(RecordError,'scope-preview-stale'):
            self.approve(p['receipt'],'--create','changed-target')
        head=self.store.head('work:report')
        with patch.object(self.store,'commit_heads',side_effect=OSError('interrupted')), self.assertRaises(OSError):
            self.approve(p['receipt'],'--create','other')
        self.assertEqual(head,self.store.head('work:report'))
        self.assertEqual('external',(self.root/'docs'/'appendix').read_text())


class ScopeGitTests(ScopeCommands, IntegrationFixture, TestCase):
    def test_linked_worktree_cannot_extend_scope(self):
        from colvia.connection import Connections
        from colvia.workspace import LocalWorkspace
        from colvia.work import WorkService
        from colvia.binding import resolve, require_registered
        parent=self.nested()
        root=parent/'child'
        topology=self.git.topology(root)
        connections=Connections(self.store)
        _,binding=connections.binding()
        wid=require_registered(resolve(self.locator,binding,topology,connections.registrations(topology)))
        self.service=WorkService(self.store,LocalWorkspace(self.store,root,wid,
                                 locator_reader=lambda:self.locator,git=self.git))
        self.start()
        with self.assertRaisesRegex(RecordError,'scope-primary-workspace-only'):
            self.preview('--create','appendix.md')

    def test_ignore_rule_with_decomposed_name_blocks_canonical_new_path(self):
        import unicodedata
        path = 'café.md'
        (self.root/'.gitignore').write_text(unicodedata.normalize('NFD',path)+'\n')
        self.start()
        with self.assertRaisesRegex(RecordError,'scope-protected-path'):
            self.preview('--create',path)

    def test_staged_deletion_cannot_be_created(self):
        (self.root/'obsolete.md').write_text('old')
        self.command('add','obsolete.md')
        self.command('commit','-qm','fixture')
        self.command('rm','-q','obsolete.md')
        self.start()
        with self.assertRaisesRegex(RecordError,'scope-create-occupied'):
            self.preview('--create','obsolete.md')

    def test_joint_git_preview_and_ignored_paths(self):
        (self.root/'table.md').write_text('original table')
        (self.root/'.gitignore').write_text('ignored*\n')
        self.command('add','table.md','.gitignore')
        self.command('commit','-qm','fixture')
        self.start()
        with self.assertRaisesRegex(RecordError,'scope-protected-path'):
            self.preview('--create','ignored-document')
        delta=['--edit','table.md','--create','appendix.md']
        self.approve(self.preview(*delta)['receipt'],*delta)
        (self.root/'table.md').write_text('changed table')
        (self.root/'appendix.md').write_text('new appendix')
        review=self.submit()
        self.service.accept(operation='accept',work='report',receipt=review['receipt'],statement='수락')
        preview=self.integration.prepare(operation='integrate',works=['report'],message='Reviewed',identity=AUTHOR)
        diff=base64.b64decode(preview['diff_base64'])
        self.assertIn(b'new appendix',diff)
        self.assertIn(b'changed table',diff)

