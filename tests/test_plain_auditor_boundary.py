from pathlib import Path
import json,subprocess,sys,tempfile,unittest

class PlainAuditorBoundaryTests(unittest.TestCase):
    def test_missing_or_legacy_authority_is_degraded_without_fallback(self):
        auditor=Path(__file__).parent/'fixtures/product_plain_auditor.py'
        with tempfile.TemporaryDirectory() as folder:
            base=Path(folder)
            for form in ('empty','legacy','missing-target'):
                with self.subTest(form=form):
                    target=base/form
                    if form!='missing-target': target.mkdir()
                    if form=='legacy':
                        def save(name,value):
                            p=target/name;p.parent.mkdir(parents=True,exist_ok=True)
                            p.write_text(json.dumps(value)+'\n')
                        release={'id':'old-release','sha256':'0'*64}
                        save('.harness-v2-detached.json',{'record_type':'product-detach-receipt','active_release_ref':release,
                            'state_authority_home_id':'old-state','intent_authority_home_id':'old-intent',
                            'documentation':{'availability_after_detach':'not-guaranteed','release_ref':release,
                                             'required_relative_paths':['docs/MANUAL-OPERATION.md']}})
                        save('.harness-v2/authority.json',{'authority_home_id':'old-state'})
                        save('.harness-v2-intents/authority.json',{'authority_home_id':'old-intent'})
                    def snap():
                        return {str(p.relative_to(base)):(p.is_dir(),None if p.is_dir() else p.read_bytes()) for p in base.rglob('*')}
                    before=snap()
                    result=subprocess.run([sys.executable,'-I','-B',str(auditor),str(target)],capture_output=True)
                    self.assertEqual(10,result.returncode,result.stdout+result.stderr)
                    self.assertNotIn(b'Traceback',result.stderr)
                    value=json.loads(result.stdout)
                    self.assertEqual('degraded',value['classification']);self.assertFalse(value['mutation_authorized'])
                    if form!='missing-target':self.assertEqual('missing .hrn; legacy layouts unsupported',value['message'])
                    self.assertEqual(before,snap())

if __name__=='__main__':unittest.main(verbosity=2)
