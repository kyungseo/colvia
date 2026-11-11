"""Interrupted local initialization; fixed signed anchor, no installation/network."""
import hashlib,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
from colvia.codec import RecordError,canonical_bytes
from colvia.storage.files import PosixFiles
from colvia.updates.initial_home import initialize_home,initial_head,retry_claim
from colvia.updates.installation import FirstInstall
from colvia.updates.trust import Trust
from test_foundation_trust import FIXTURE,META,TARGET,MemoryFetcher,fixed_factory

class FixedTrust(Trust):
    def __init__(self,*args,**kwargs):
        kwargs.setdefault('factory',fixed_factory(2027));kwargs.setdefault('clock_ns',lambda:100)
        super().__init__(*args,**kwargs)
    @classmethod
    def initialize(cls,*args,**kwargs):
        kwargs['factory']=fixed_factory(2027);kwargs['clock_ns']=lambda:100
        return super().initialize(*args,**kwargs)

class InitialHomeTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(prefix='initial-home-');self.base=Path(self.tmp.name)
        self.files=PosixFiles();self.anchor=(FIXTURE/'metadata/root.json').read_bytes();self.fetch=MemoryFetcher()
        self.config=dict(version=1,channel='preview',metadata_url=META,target_url=TARGET,target='file1.txt')
    def tearDown(self):self.tmp.cleanup()
    def initialize(self,name='home',**kwargs):
        return initialize_home(self.base/name,os_name='macos',architecture='arm64',files=self.files,
            config=self.config,anchor=self.anchor,payload_digest='0'*64,fetcher=self.fetch,trust_type=FixedTrust,**kwargs)
    def test_each_interruption_retains_stage_but_never_publishes_incomplete_home(self):
        for i,phase in enumerate(('home-created','configuration-saved','identity-saved','intent-saved','trust-initialized','home-published')):
            def stop(current):
                if current==phase:raise RuntimeError('synthetic interruption')
            name='home-'+str(i)
            with self.assertRaises(RuntimeError) as raised:self.initialize(name,checkpoint=stop)
            error=raised.exception;root=self.base/name
            if phase=='home-published':
                self.assertTrue(root.is_dir());self.assertEqual('published',error.publication)
                self.assertTrue((root/'operations'/error.operation/'install-intent.json').is_file())
                self.assertTrue((root/'trust/state.json').is_file())
            else:
                self.assertFalse(root.exists());self.assertEqual('unpublished',error.publication)
                self.assertEqual(1,len(list(self.base.glob(name+'.initial-*'))))
        self.assertEqual([],self.fetch.calls)
    def test_published_home_rebinds_paths_and_retains_initial_attempt(self):
        home,trust,operation=self.initialize()
        self.assertEqual(self.base/'home',home.root);self.assertEqual(home.root/'trust',trust.root)
        self.assertEqual(operation,initial_head(home,trust,self.config,self.anchor))
        self.assertEqual([],self.fetch.calls)
    def test_foreign_destination_is_never_overwritten(self):
        root=self.base/'home';root.mkdir(mode=0o700);(root/'keep').write_bytes(b'foreign')
        with self.assertRaisesRegex(RecordError,'publication-unconfirmed') as raised:self.initialize()
        self.assertEqual('unknown',raised.exception.publication);self.assertEqual(b'foreign',(root/'keep').read_bytes())
        self.assertEqual(1,len(list(self.base.glob('home.initial-*'))))
    def test_lost_publication_ack_is_classified_without_retry(self):
        publish=self.files.publish_directory
        def lose(*args):publish(*args);raise OSError('lost ack')
        with patch.object(self.files,'publish_directory',side_effect=lose),self.assertRaises(OSError) as raised:self.initialize()
        self.assertEqual('published',raised.exception.publication)
        self.assertEqual(0,len(list(self.base.glob('home.initial-*'))))
    def test_explicit_retry_preserves_trust_and_previous_failure_no_fork(self):
        home,trust,first=self.initialize();before=trust.state()[0]
        def fail(*args,**kwargs):raise RuntimeError('synthetic download failure')
        service=FirstInstall(home,trust,self.config)
        with patch.object(trust,'stage',side_effect=fail),self.assertRaises(RuntimeError):service.perform(operation=first,claimed=True,anchor=self.anchor)
        with patch.object(trust,'stage',side_effect=fail),self.assertRaises(RuntimeError):
            service.perform(operation='second',retry_of=first,anchor=self.anchor)
        self.assertEqual('second',initial_head(home,trust,self.config,self.anchor));self.assertEqual(before,trust.state()[0])
        self.assertTrue((home.root/'operations'/first/'started.json').is_file())
        with self.assertRaisesRegex(RecordError,'not-current'):service.perform(operation='fork',retry_of=first,anchor=self.anchor)
        self.assertFalse((home.root/'operations/fork').exists())
    def test_prepared_unpublished_attempt_can_be_superseded_but_not_resumed(self):
        home,trust,first=self.initialize();old=home.root/'operations'/first
        home.files.create(old/'prepared.json',canonical_bytes({'version':1}))
        retry_claim(home,trust,self.config,self.anchor,previous=first,operation='second')
        self.assertTrue((old/'prepared.json').exists());self.assertEqual('second',initial_head(home,trust,self.config,self.anchor))
        from colvia.updates.reauthentication import forward_allowed
        with self.assertRaisesRegex(RecordError,'superseded'):forward_allowed(home,first)
        (home.root/'bin').mkdir(mode=0o700)
        with self.assertRaisesRegex(RecordError,'live-effects'):retry_claim(home,trust,self.config,self.anchor,previous='second',operation='third')
        self.assertFalse((home.root/'operations/third').exists())
    def test_status_finds_retry_head_and_prepared_receipt_without_manual_hashing(self):
        home,trust,first=self.initialize();retry_claim(home,trust,self.config,self.anchor,previous=first,operation='second')
        raw=canonical_bytes({'version':1});home.files.create(home.root/'operations/second/prepared.json',raw)
        result=FirstInstall(home,trust,self.config).status(anchor=self.anchor)
        self.assertEqual('second',result['operation']);self.assertEqual(hashlib.sha256(raw).hexdigest(),result['receipt'])
        self.assertFalse(result['live_files_present'])
    def test_changed_anchor_or_copied_home_identity_refuses(self):
        home,trust,first=self.initialize()
        with self.assertRaisesRegex(RecordError,'anchor-changed'):initial_head(home,trust,self.config,b'other')
        import shutil
        copied=self.base/'copied';shutil.copytree(home.root,copied,symlinks=True)
        from colvia.management import ManagerHome
        other=ManagerHome(copied,os_name='macos',architecture='arm64')
        with self.assertRaisesRegex(RecordError,'identity-changed'):initial_head(other,trust,self.config,self.anchor)
