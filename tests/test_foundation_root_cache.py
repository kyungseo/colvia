"""Real signed TUF chain with a portable known-pair routing adapter.

This is not native Windows ACL/handle qualification.
"""
import datetime,hashlib,json,os,shutil,tempfile,unittest
from pathlib import Path
from colvia.codec import RecordError,canonical_bytes,require
from colvia.storage.files import PosixFiles
from colvia.updates.trust import Trust
from tuf.api.exceptions import RepositoryError

FIXTURE=Path(__file__).parent/'fixtures/foundation-root-cache'
NOW=int(datetime.datetime(2026,11,9,tzinfo=datetime.timezone.utc).timestamp()*10**9)

class PairFiles(PosixFiles):
    def read_known_alias_pair(self,versioned,alias,limit):
        a,b=versioned.stat(),alias.stat()
        same=(a.st_dev,a.st_ino)==(b.st_dev,b.st_ino)
        require(a.st_nlink==b.st_nlink==(2 if same else 1),'windows-alias-link-count')
        raw,other=versioned.read_bytes(),alias.read_bytes()
        require(raw==other and len(raw)<=limit,'windows-alias-content-changed')
        return raw

class RootCacheTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(prefix='root-cache-');self.root=Path(self.tmp.name).resolve()
        self.meta=self.root/'metadata';self.history=self.meta/'root_history';self.history.mkdir(parents=True)
        for name in ('1.root.json','2.root.json'):shutil.copyfile(FIXTURE/name,self.history/name)
        for role in ('timestamp','snapshot','targets'):shutil.copyfile(FIXTURE/(role+'.json'),self.meta/(role+'.json'))
        self.state=dict(version=1,anchor_sha256=hashlib.sha256((self.history/'1.root.json').read_bytes()).hexdigest(),
            verified_ns=NOW,versions=dict(root=2,timestamp=1,snapshot=1,targets=1),
            metadata_url='https://updates.example.invalid/metadata/',target_url='https://updates.example.invalid/targets/')
        self.save_state();(self.root/'update.lock').write_bytes(b'')
        self.trust=Trust(self.root,metadata_url=self.state['metadata_url'],target_url=self.state['target_url'],
            files=PairFiles(),fetcher=object(),clock_ns=lambda:NOW)
        self.link(2)
    def tearDown(self):self.tmp.cleanup()
    def save_state(self):(self.root/'state.json').write_bytes(canonical_bytes(self.state))
    def link(self,version):
        (self.meta/'root.json').unlink(missing_ok=True);os.link(self.history/(str(version)+'.root.json'),self.meta/'root.json')
    def description(self):
        target=json.loads((self.meta/'targets.json').read_bytes())['signed']['targets']['colvia-windows-arm64.zip']
        return dict(path='colvia-windows-arm64.zip',length=target['length'],sha256=target['hashes']['sha256'],
            custom=target['custom'],verified_ns=NOW,expires_ns=NOW+10**9,versions=dict(self.state['versions']),
            metadata=self.trust.metadata_digests(self.state['versions']))
    def test_current_linked_anchor_reauthenticates(self):
        self.link(1);self.state['versions']['root']=1;self.save_state()
        before=(self.root/'state.json').read_bytes();self.trust.activation_check(self.description())
        self.assertEqual(before,(self.root/'state.json').read_bytes())
    def test_current_linked_rotated_root_reauthenticates(self):self.trust.activation_check(self.description())
    def test_current_separate_equal_copy_reauthenticates(self):
        (self.meta/'root.json').unlink();shutil.copyfile(self.history/'2.root.json',self.meta/'root.json')
        self.trust.activation_check(self.description())
    def test_extra_link_rejected(self):
        description=self.description();os.link(self.history/'2.root.json',self.root/'extra')
        with self.assertRaisesRegex(RecordError,'link-count'):self.trust.activation_check(description)
    def test_prior_root_hardlink_uses_strict_read(self):
        description=self.description();os.link(self.history/'1.root.json',self.root/'extra')
        with self.assertRaisesRegex(RecordError,'invalid-lifecycle-file'):self.trust.activation_check(description)
    def test_alias_points_at_wrong_version(self):
        for current,alias in ((1,2),(2,1)):
            with self.subTest(current=current):
                self.state['versions']['root']=current;self.save_state();self.link(current);description=self.description()
                self.link(alias);before=(self.root/'state.json').read_bytes()
                with self.assertRaisesRegex(RecordError,'link-count'):self.trust.activation_check(description)
                self.assertEqual(before,(self.root/'state.json').read_bytes())
    def test_missing_alias_is_classified(self):
        description=self.description();(self.meta/'root.json').unlink()
        with self.assertRaisesRegex(RecordError,'update-root-cache-unavailable'):self.trust.activation_check(description)
    def test_different_copy_rejected(self):
        description=self.description();(self.meta/'root.json').unlink();(self.meta/'root.json').write_bytes(b'different')
        with self.assertRaises(RecordError):self.trust.activation_check(description)
    def test_current_signature_checked_even_with_new_digest(self):
        description=self.description();p=self.history/'2.root.json';value=json.loads(p.read_bytes())
        value['signatures'][0]['sig']='0'*128;p.write_bytes(json.dumps(value).encode())
        description['metadata']=self.trust.metadata_digests(self.state['versions'])
        with self.assertRaises(RepositoryError):self.trust.activation_check(description)
    def test_missing_chain_member_rejected(self):
        description=self.description();(self.meta/'root.json').unlink();(self.history/'2.root.json').unlink()
        with self.assertRaises(RecordError):self.trust.verified_cached_target(description['path'],self.state,NOW)
