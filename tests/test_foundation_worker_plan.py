"""Literal worker plans; these tests do not execute the OS sandbox profile."""
import sys,unittest
from pathlib import Path
from colvia.codec import RecordError
from colvia.platforms.darwin_worker_plan import DarwinWorkerPlan
from test_foundation_execution_store import JournalFixture
from test_foundation_execution_history import Chain
import test_foundation_execution_inputs as inputs

@unittest.skipUnless(sys.platform=='darwin','native staging')
class PlanTests(JournalFixture,unittest.TestCase):
    native=inputs.InputTests.native
    def plan_fixture(self,write=False):
        template=(Path(__file__).resolve().parents[1]/'runtime/official/worker.sb.in').read_bytes()
        effects,native,grant,owner,history=self.native({'profile_digest':template})
        chain=Chain(self.contract).launch()
        if write:
            chain.successful(1)
            identity=self.contract['scope']['documents']['Output']['original_identity']
            chain.add('recovery-ready',output_id='Output',recovery_ordinal=1,original_identity=identity,
                original_sha256=identity['sha256'],byte_count=identity['size'])
            chain.add('callback-reserved',callback_id=2,ordinal=2,tool='write',file_ids=['Output'],verifier_id=None,expected_identity=identity)
        else:chain.reserve(1)
        self.publish(chain);history=self.journal.read('run')[-1]
        maker=DarwinWorkerPlan(native,native.resources['python_digest'].parent)
        tool='document_write' if write else 'document_read';args={'file_id':'Output','content':'new','expected_sha256':self.contract['scope']['documents']['Output']['original_identity']['sha256']} if write else {'file_ids':['Output','Reference']}
        return effects,native,grant,history,maker,tool,args
    def test_read_profile_has_no_project_write_target_or_shell_fallback(self):
        effects,native,grant,history,maker,tool,args=self.plan_fixture()
        with effects.exclusion(create=False):
            plan=maker.materialize(grant,history,tool,args,1);maker.verify(plan)
            self.assertEqual('/usr/bin/sandbox-exec',plan.argv[0]);self.assertEqual({},plan.spec['swap'])
            self.assertNotIn('@@',plan.profile_bytes.decode());self.assertNotIn('file-read* file-write*',plan.profile_bytes.decode())
            self.assertNotIn('PYTHONPATH',plan.env);self.assertEqual('read',plan.argv[-1])
            active=[line.strip() for line in plan.profile_bytes.decode().splitlines() if line.strip() and not line.lstrip().startswith(';')]
            self.assertTrue(all(line.startswith('(') for line in active))
            self.assertEqual(['(allow file-write-data (literal "/dev/null"))'],[line for line in active if 'file-write' in line])
            for forbidden in ('network','mach-','process-fork','ipc-'):
                self.assertNotIn(forbidden,'\n'.join(active))
            self.assertEqual(1,'\n'.join(active).count('process-exec'))
            self.assertNotIn('only for write operation','\n'.join(active))
    def test_write_profile_names_original_and_post_and_preserves_existing_stage(self):
        effects,native,grant,history,maker,tool,args=self.plan_fixture(True)
        with effects.exclusion(create=False):
            plan=maker.materialize(grant,history,tool,args,2);maker.verify(plan)
            self.assertIn('output.post.original',plan.profile_bytes.decode());self.assertEqual('write',plan.argv[-1])
            active=[line.strip() for line in plan.profile_bytes.decode().splitlines() if line.strip() and not line.lstrip().startswith(';')]
            self.assertTrue(all(line.startswith('(') for line in active))
            self.assertTrue(any(line.startswith('(allow file-read* file-write* ') and 'output.post.original' in line for line in active))
            self.assertNotIn('only for write operation','\n'.join(active))
            with self.assertRaisesRegex(RecordError,'staging-already-exists'):maker.materialize(grant,history,tool,args,2)
            (Path(plan.cwd)/'spec.json').write_bytes(b'changed')
            with self.assertRaisesRegex(RecordError,'plan-drift'):maker.verify(plan)
    def test_runtime_root_cannot_expose_the_project_or_recovery_area(self):
        effects,native,grant,history,maker,tool,args=self.plan_fixture()
        with self.assertRaisesRegex(RecordError,'python-project-overlap'):DarwinWorkerPlan(native,self.root.parent)

    def test_profile_bytes_used_to_generate_plan_must_match_the_grant(self):
        effects,native,grant,history,maker,tool,args=self.plan_fixture()
        native.resources['profile_digest'].write_text('(allow default)')
        with effects.exclusion(create=False),self.assertRaisesRegex(RecordError,'resource-drift'):
            maker.materialize(grant,history,tool,args,1)

    def test_candidate_cache_reads_are_exact_and_have_no_external_runtime_fallback(self):
        # Qualified on one OS/runtime candidate only; not installed-release support.
        import re
        template=(Path(__file__).resolve().parents[1]/'runtime/official/worker.sb.in').read_text()
        self.assertNotIn('/opt/homebrew/',template)
        self.assertIn('(deny default)',template)
        self.assertIn('(subpath (param "PYROOT"))',template)
        self.assertEqual(1,template.count('; @@APPROVED_INPUT_READ_LITERALS@@'))
        extra=template.split('; Bounded startup condition C\n',1)[1]
        for forbidden in ('subpath','regex','file-write','process-','network','mach-','file-read*'):
            self.assertNotIn(forbidden,extra)
        lines=extra.splitlines()
        self.assertEqual(3,len(lines))
        self.assertTrue(lines[0].startswith('(allow file-read-metadata '))
        self.assertTrue(lines[1].startswith('(allow file-read-data '))
        self.assertEqual('(allow file-read-data (require-all (literal "/") (vnode-type DIRECTORY)))',lines[2])
        roots=('/System/Cryptexes/OS/System/Library/dyld','/System/Volumes/Preboot/Cryptexes/OS/System/Library/dyld')
        metadata={str(p) for root in roots for p in (Path(root),*Path(root).parents)}
        self.assertEqual(metadata,set(re.findall(r'\(literal "([^"]+)"\)',lines[0])))
        paths=re.findall(r'\(literal "([^"]+)"\)',lines[1])
        self.assertTrue(paths)
        for value in paths:
            path=Path(value)
            self.assertTrue(value in roots or (str(path.parent) in roots and re.fullmatch(r'dyld_shared_cache_arm64e(?:\.[A-Za-z0-9]+)*',path.name)),value)
        self.assertEqual(len(paths),len(set(paths)))

class ContractBoundsTests(unittest.TestCase):
    def test_document_and_read_id_count_bounds_are_independently_enforced(self):
        from colvia.execution.schema import grant_record
        from test_foundation_execution_history import grant
        for field in ('documents','read_ids'):
            for count in (0,9):
                with self.subTest(field=field,count=count):
                    value=grant()
                    if field=='documents':value['scope'][field]={f'D{i}':value['scope']['documents']['Output'] for i in range(count)}
                    else:value['scope'][field]=[f'D{i}' for i in range(count)]
                    with self.assertRaisesRegex(RecordError,'execution-document-count'):
                        grant_record(value)
