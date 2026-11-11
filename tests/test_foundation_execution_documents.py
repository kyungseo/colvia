"""Actual approved-view and retained-context exposure boundaries."""
import hashlib,time,unittest
from colvia.codec import RecordError
from colvia.execution.documents import prepare_views,compose_output
from test_foundation_execution_history import grant

class DocumentsTests(unittest.TestCase):
    def fixture(self,output=b'prefix OLD suffix',range=(7,10),reference=b'Policy'):
        value=grant();raw={'Output':output,'Reference':reference}
        for name,data in raw.items():
            entry=value['scope']['documents'][name];entry['original_identity'].update(size=len(data),sha256=hashlib.sha256(data).hexdigest())
        value['scope']['documents']['Output']['view']['ranges']=[list(range)]
        return value,raw
    def test_only_approved_view_is_returned_and_context_is_preserved(self):
        value,raw=self.fixture();items=prepare_views(value,raw,'Summarize the policy.',deadline=time.monotonic()+2)
        self.assertEqual('OLD',items[0]['content']);self.assertNotIn('prefix',str(items));self.assertNotIn('/synthetic',str(items))
        self.assertEqual(b'prefix NEW suffix',compose_output(value,raw['Output'],'NEW',deadline=time.monotonic()+2))
    def test_retained_secret_prevents_launch_even_when_not_in_view(self):
        output=b'api_key=abcdefghijk OLD';value,raw=self.fixture(output,range=(20,len(output)))
        with self.assertRaises(RecordError):prepare_views(value,raw,'Edit',deadline=time.monotonic()+2)
    def test_secret_formed_across_boundary_refuses_before_write(self):
        value,raw=self.fixture(b'api_key= OLD',range=(9,12))
        with self.assertRaises(RecordError):compose_output(value,raw['Output'],'abcdefghijk',deadline=time.monotonic()+2)
    def test_changed_source_or_split_utf8_refuses(self):
        value,raw=self.fixture();raw['Reference']=b'changed'
        with self.assertRaisesRegex(RecordError,'document-drift'):prepare_views(value,raw,'Edit',deadline=time.monotonic()+2)
        value,raw=self.fixture('한글'.encode(),range=(1,4))
        with self.assertRaises(UnicodeError):prepare_views(value,raw,'Edit',deadline=time.monotonic()+2)
    def test_prompt_identifier_and_expired_deadline_refuse(self):
        value,raw=self.fixture()
        with self.assertRaises(RecordError):prepare_views(value,raw,'Mail person@example.invalid',deadline=time.monotonic()+2)
        with self.assertRaises(TimeoutError):prepare_views(value,raw,'Edit',deadline=time.monotonic()-1)
