"""Success bytes, exact views and verifier oracles remain independently checked."""
import copy,hashlib,time,unittest
from colvia.codec import RecordError
from colvia.execution import results
from colvia.execution.documents import prepare_views
from colvia.execution.guards import wire_bytes
import test_foundation_execution_documents as fixture

class ResultTests(unittest.TestCase):
    def fixture(self):
        contract,raw=fixture.DocumentsTests().fixture();deadline=time.monotonic()+5
        request=dict(prompt='Edit the approved excerpt.',claims={'Output':dict(required=['NEW'],forbidden=[],evidence=[dict(file_id='Reference',quote='Policy')])},approved_external_links=[],link_metadata={})
        return contract,raw,request,deadline
    def test_read_contains_only_exact_approved_views_with_origin(self):
        contract,raw,request,deadline=self.fixture()
        value={'files':prepare_views(contract,raw,request['prompt'],deadline=deadline)}
        reply=results.read_result(contract,request,raw,value,deadline=deadline)
        self.assertEqual('OLD',reply['files'][0]['content']);self.assertIn('origin',reply['files'][0]);self.assertNotIn('prefix',str(reply))
        value['files'][0]['content']='prefix OLD suffix'
        with self.assertRaisesRegex(RecordError,'read-result-binding'):results.read_result(contract,request,raw,value,deadline=deadline)
    def written(self):
        contract,raw,request,deadline=self.fixture();before=contract['scope']['documents']['Output']['original_identity'];wanted=b'prefix NEW suffix'
        after=dict(before,ino=9,sha256=hashlib.sha256(wanted).hexdigest(),size=len(wanted),mtime_ns=11,ctime_ns=11)
        result=dict(file_id='Output',sha256=after['sha256'],identity=[after['dev'],after['ino']],bytes=len(wanted),mode=after['mode'])
        kwargs=dict(after=after,raw=wanted,saved=dict(before,ctime_ns=12),saved_raw=raw['Output'],swap_present=False,deadline=deadline)
        return contract,raw,result,kwargs
    def test_write_binds_bytes_saved_inode_and_changed_view(self):
        contract,raw,value,kwargs=self.written()
        reply,updated=results.write_result(contract,raw['Output'],'NEW',value,**kwargs)
        self.assertEqual([[7,10]],updated['view']['ranges']);self.assertEqual(len(kwargs['raw']),reply['bytes'])
        for change in (dict(raw=b'wrong bytes'),dict(swap_present=True),dict(saved_raw=b'late edit')):
            with self.subTest(change=list(change)),self.assertRaises(RecordError):results.write_result(contract,raw['Output'],'NEW',value,**dict(kwargs,**change))
    def test_claimed_success_cannot_hide_replaced_original_or_boolean_metadata(self):
        contract,raw,value,kwargs=self.written();changed=dict(kwargs,saved=dict(kwargs['saved'],ino=20))
        with self.assertRaisesRegex(RecordError,'saved-original-changed'):results.write_result(contract,raw['Output'],'NEW',value,**changed)
        for field in ('bytes','mode'):
            with self.assertRaisesRegex(RecordError,'result-shape'):results.write_result(contract,raw['Output'],'NEW',dict(value,**{field:True}),**kwargs)
    def test_verifier_binds_all_inputs_oracle_and_findings(self):
        contract,raw,request,deadline=self.fixture();files={name:dict(sha256=item['original_identity']['sha256']) for name,item in contract['scope']['documents'].items()}
        oracle=dict(outputs=['Output'],claims=request['claims'],approved_external_links=[],parser_sha256=contract['scope']['resources']['parser_digest'])
        value=dict(verifier_id='DOC-CLAIMS',inputs={name:item['sha256'] for name,item in files.items()},
            findings=[],oracle_sha256=hashlib.sha256(wire_bytes(oracle)).hexdigest(),boundary='fixed static checks; human factual review remains required')
        value['pass']=True
        self.assertEqual(value,results.verifier_result(contract,request,files,'DOC-CLAIMS',value,deadline=deadline))
        for change in (dict(oracle_sha256='0'*64),dict(inputs={}),dict(findings=[{'code':'failed'}])):
            with self.assertRaises(RecordError):results.verifier_result(contract,request,files,'DOC-CLAIMS',dict(value,**change),deadline=deadline)
