"""Fixed signed upstream fixture; no keys, network or installation."""
import datetime,hashlib,json,tempfile,unittest
from pathlib import Path
from tuf.ngclient import Updater
from tuf.ngclient.fetcher import FetcherInterface
from tuf.api.exceptions import RepositoryError,DownloadHTTPError,DownloadError
from colvia.updates.trust import Trust
from colvia.codec import RecordError,canonical_bytes
FIXTURE=Path(__file__).parent/'fixtures/tuf-fixed'
META='https://updates.example.invalid/metadata/'
TARGET='https://updates.example.invalid/targets/'
class MemoryFetcher(FetcherInterface):
    def __init__(self):
        self.calls=[];self.bad_target=False;self.bad_timestamp=False
    def _fetch(self,url):
        self.calls.append(url)
        if url.startswith(META):path=FIXTURE/'metadata'/url[len(META):]
        elif url.startswith(TARGET):path=FIXTURE/'targets'/url[len(TARGET):]
        else:raise AssertionError('Unexpected fetch origin')
        if not path.is_file():raise DownloadHTTPError('missing fixture',404)
        raw=path.read_bytes()
        if self.bad_target and url.startswith(TARGET):raw=b'corrupt target'
        if self.bad_timestamp and url.endswith('timestamp.json'):
            value=json.loads(raw);value['signed']['version']=9;raw=json.dumps(value).encode()
        yield raw

def fixed_factory(year):
    def factory(**kw):
        u=Updater(**kw)
        # Pinned-client test seam only. Never exposed in user input/production.
        u._trusted_set.reference_time=datetime.datetime(year,1,1,tzinfo=datetime.timezone.utc)
        return u
    return factory

class TrustTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(prefix='trust-');self.base=Path(self.tmp.name)
        self.anchor=(FIXTURE/'metadata/root.json').read_bytes();self.fetch=MemoryFetcher();self.clock=[100]
    def tearDown(self):self.tmp.cleanup()
    def initialize(self,year=2027):
        return Trust.initialize(self.base/'trust',anchor=self.anchor,anchor_sha256=hashlib.sha256(self.anchor).hexdigest(),
            metadata_url=META,target_url=TARGET,fetcher=self.fetch,clock_ns=lambda:self.clock[0],factory=fixed_factory(year))
    def test_metadata_only_port_refuses_target_even_under_shared_url_prefix(self):
        from colvia.updates.reauthentication import metadata_only
        fetcher=metadata_only(self.fetch,META)
        list(fetcher.fetch(META+'timestamp.json'))
        count=len(self.fetch.calls)
        for url in (TARGET+'file1.txt',META+'targets/file1.txt',META+'file1.txt',META+'timestamp.json?other=1'):
            with self.assertRaises(DownloadError) as raised:list(fetcher.fetch(url))
            self.assertIsInstance(raised.exception.__cause__,RecordError)
            self.assertEqual('renewal-target-download-forbidden',raised.exception.__cause__.code)
        self.assertEqual(count,len(self.fetch.calls))

    def test_missing_target_preserves_learned_counters_and_clock(self):
        t=self.initialize()
        with self.assertRaisesRegex(RecordError,'target-unavailable'):t.stage('missing.txt',destination=self.base/'missing')
        state=t.state()[1]
        self.assertEqual(1,state['versions']['targets']);self.assertEqual(100,state['verified_ns'])
        self.assertFalse(any(url.startswith(TARGET) for url in self.fetch.calls))

    def test_metadata_only_exact_target_renewal_has_no_target_fetch(self):
        from colvia.management import ManagerHome
        from colvia.updates.reauthentication import renew,effective
        t=self.initialize();original=t.stage('file1.txt',destination=self.base/'asset')
        home=ManagerHome.create(self.base/'home',os_name='macos',architecture='arm64')
        home.files.create_directory(home.root/'operations/update');self.fetch.calls=[];self.clock[0]=101
        renewal=renew(home,t,operation='update',original='0'*64,download=original,renewal='fresh')
        self.assertFalse(any(url.startswith(TARGET) for url in self.fetch.calls))
        self.assertEqual(101,effective(home,t,operation='update',original='0'*64,download=original,renewal=renewal['renewal'])['verified_ns'])
        with self.assertRaises(RecordError):t.activation_check(original)
        self.clock[0]=100
        with self.assertRaisesRegex(RecordError,'clock-rollback'):
            renew(home,t,operation='update',original='0'*64,download=original,renewal='backward')

    def test_fixed_signature_hash_and_counter_persistence(self):
        t=self.initialize();out=self.base/'asset';r=t.stage('file1.txt',destination=out)
        self.assertEqual((FIXTURE/'targets/file1.txt').read_bytes(),out.read_bytes())
        self.assertEqual(hashlib.sha256(out.read_bytes()).hexdigest(),r['sha256'])
        self.assertEqual(dict(root=1,timestamp=1,snapshot=1,targets=1),t.state()[1]['versions'])
        self.assertEqual(100,t.state()[1]['verified_ns']);self.assertEqual({'file_permissions':'0644'},r['custom'])
    def test_windows_signed_length_blocks_target_before_fetch_or_file_creation(self):
        from types import SimpleNamespace
        from unittest.mock import patch
        from colvia.updates.space import SpaceError
        trust = self.initialize()
        required = (FIXTURE/'targets/file1.txt').stat().st_size
        destination = self.base/'asset'
        with patch('colvia.updates.trust.sys', SimpleNamespace(platform='win32')), \
             patch('colvia.updates.space.shutil.disk_usage', return_value=SimpleNamespace(free=required-1)) as usage:
            with self.assertRaisesRegex(SpaceError, 'update-space-insufficient') as raised:
                trust.stage('file1.txt', destination=destination)
            usage.assert_called_once_with(destination.parent)
            self.assertEqual(required, raised.exception.diagnostic['required_bytes'])
            self.assertEqual(required-1, raised.exception.diagnostic['available_bytes'])
        self.assertEqual(1, trust.state()[1]['versions']['targets'])
        self.assertFalse(destination.exists())
        self.assertFalse(any(url.startswith(TARGET) for url in self.fetch.calls))

    def test_windows_exact_target_skips_space_and_exact_free_space_can_download(self):
        from types import SimpleNamespace
        from unittest.mock import patch
        trust = self.initialize()
        destination = self.base/'asset'
        payload = (FIXTURE/'targets/file1.txt').read_bytes()
        with patch('colvia.updates.trust.sys', SimpleNamespace(platform='win32')), \
             patch('colvia.updates.space.shutil.disk_usage', return_value=SimpleNamespace(free=len(payload))) as usage:
            present = trust.stage('file1.txt', destination=destination, already_present=lambda _: True)
            self.assertIsNone(present['staged'])
            usage.assert_not_called()
            self.assertFalse(any(url.startswith(TARGET) for url in self.fetch.calls))
            self.assertFalse(destination.exists())
            downloaded = trust.stage('file1.txt', destination=destination)
            usage.assert_called_once_with(destination.parent)
        self.assertEqual(str(destination), downloaded['staged'])
        self.assertEqual(payload, destination.read_bytes())

    def test_windows_target_disk_full_retains_partial_bytes_and_counters(self):
        from contextlib import contextmanager
        from types import SimpleNamespace
        from unittest.mock import patch
        import errno
        from colvia.updates.space import SpaceError
        trust = self.initialize()
        destination = self.base/'asset'
        original = trust.files.create_stream
        payload = (FIXTURE/'targets/file1.txt').read_bytes()

        @contextmanager
        def limit_write(path, *args, **kwargs):
            with original(path, *args, **kwargs) as stream:
                if path != destination:
                    yield stream
                    return
                def write_partial(data):
                    stream.write(data[:1])
                    raise OSError(errno.ENOSPC, 'simulated disk exhausted')
                yield SimpleNamespace(write=write_partial)

        with patch('colvia.updates.trust.sys', SimpleNamespace(platform='win32')), \
             patch('colvia.updates.space.shutil.disk_usage', return_value=SimpleNamespace(free=len(payload))), \
             patch.object(trust.files, 'create_stream', side_effect=limit_write):
            with self.assertRaisesRegex(SpaceError, 'update-disk-full') as raised:
                trust.stage('file1.txt', destination=destination)
        self.assertEqual('target-download', raised.exception.diagnostic['phase'])
        self.assertEqual(payload[:1], destination.read_bytes())
        self.assertEqual(1, trust.state()[1]['versions']['targets'])

    def test_prepared_activation_reuses_exact_unexpired_metadata(self):
        t=self.initialize();download=t.stage('file1.txt',destination=self.base/'asset')
        t.activation_check(download)
        self.clock[0]=download['expires_ns']
        with self.assertRaisesRegex(RecordError,'preparation-expired'):t.activation_check(download)
        self.clock[0]=100
        path=t.root/'metadata/targets.json';path.write_bytes(path.read_bytes()+b' ')
        with self.assertRaisesRegex(RecordError,'metadata-changed'):t.activation_check(download)

    def test_activation_reauthenticates_prepared_target_without_network(self):
        import copy
        t=self.initialize();download=t.stage('file1.txt',destination=self.base/'asset');calls=list(self.fetch.calls)
        for key,value in (('length',999),('sha256','0'*64),('custom',{'different':True})):
            changed=copy.deepcopy(download);changed[key]=value
            with self.assertRaisesRegex(RecordError,'prepared-target-changed'):t.activation_check(changed)
        self.assertEqual(calls,self.fetch.calls)
    def test_changed_cached_signature_cannot_be_hidden_by_prepared_digest(self):
        t=self.initialize();download=t.stage('file1.txt',destination=self.base/'asset')
        path=t.root/'metadata/targets.json';value=json.loads(path.read_bytes())
        value['signed']['targets']['file1.txt']['length']=999;raw=json.dumps(value).encode();path.write_bytes(raw)
        download['metadata']['targets']=hashlib.sha256(raw).hexdigest();download['length']=999
        with self.assertRaises(RepositoryError):t.activation_check(download)
    def test_missing_anchor_history_refuses_recovered_activation(self):
        t=self.initialize();download=t.stage('file1.txt',destination=self.base/'asset')
        raw,state=t.state();state['anchor_sha256']='0'*64;t.files.replace(t.root/'state.json',canonical_bytes(state),raw)
        with self.assertRaisesRegex(RecordError,'anchor-history-unavailable'):t.activation_check(download)

    def test_known_verifier_failures_have_short_manager_messages(self):
        import contextlib,io
        from unittest.mock import patch
        from colvia.manager_entry import main
        for error in (RepositoryError('synthetic internal cache path'),DownloadHTTPError('synthetic internal endpoint',404)):
            output=io.StringIO()
            with patch('colvia.updates.installation.bootstrap',side_effect=error),contextlib.redirect_stdout(output):
                code=main(['bootstrap-install-or-update','--management-root',str(self.base/'home'),
                    '--bootstrap-stage',str(self.base/'stage'),'--bootstrap-manifest-sha256','0'*64])
            self.assertEqual(2,code);self.assertNotIn('synthetic internal',output.getvalue());self.assertLess(len(output.getvalue()),150)

    def test_bad_signature_is_not_a_verified_target(self):
        t=self.initialize();self.fetch.bad_timestamp=True
        with self.assertRaises(RepositoryError):t.stage('file1.txt',destination=self.base/'asset')
        self.assertFalse((self.base/'asset').exists())
    def test_expiry_blocks_update_without_resetting_trust(self):
        t=self.initialize(year=2031)
        with self.assertRaises(RepositoryError):t.stage('file1.txt',destination=self.base/'asset')
        self.assertTrue((t.root/'state.json').is_file());self.assertFalse((self.base/'asset').exists())
    def test_corrupt_target_retains_failure_and_never_returns_success(self):
        t=self.initialize();self.fetch.bad_target=True
        with self.assertRaises((RepositoryError,RecordError)):t.stage('file1.txt',destination=self.base/'asset')
        self.assertEqual(1,t.state()[1]['versions']['timestamp'])
    def test_existing_target_and_existing_install_are_not_overwritten(self):
        t=self.initialize();out=self.base/'asset';out.write_bytes(b'original')
        with self.assertRaisesRegex(RecordError,'update-stage-exists'):t.stage('file1.txt',destination=out)
        self.assertEqual(b'original',out.read_bytes())
        with self.assertRaises(FileExistsError):self.initialize()
    def test_missing_trust_requires_repair_not_bootstrap(self):
        t=self.initialize();(t.root/'metadata/root.json').unlink()
        with self.assertRaisesRegex(RecordError,'update-trust-repair-required'):t.stage('file1.txt',destination=self.base/'asset')
        self.assertEqual([],self.fetch.calls)
    def test_clock_rollback_refuses_before_network(self):
        t=self.initialize();t.stage('file1.txt',destination=self.base/'one');n=len(self.fetch.calls);self.clock[0]=99
        with self.assertRaisesRegex(RecordError,'update-clock-rollback'):t.stage('file1.txt',destination=self.base/'two')
        self.assertEqual(n,len(self.fetch.calls))
    def test_preserved_counters_reject_older_valid_metadata(self):
        t=self.initialize();raw,s=t.state();s['versions']['targets']=2
        t.files.replace(t.root/'state.json',canonical_bytes(s),raw)
        with self.assertRaisesRegex(RecordError,'update-version-rollback'):t.stage('file1.txt',destination=self.base/'asset')
        self.assertEqual(2,t.state()[1]['versions']['targets'])
    def test_wrong_bootstrap_pin_refuses_before_creating_directory(self):
        with self.assertRaisesRegex(RecordError,'bootstrap-anchor-mismatch'):
            Trust.initialize(self.base/'trust',anchor=self.anchor,anchor_sha256='0'*64,
                metadata_url=META,target_url=TARGET,fetcher=self.fetch)
        self.assertFalse((self.base/'trust').exists())

    def test_production_factory_enforces_pinned_verifier_before_refresh(self):
        from colvia.updates.trust import updater_factory
        from unittest.mock import patch
        t=Trust.initialize(self.base/'trust',anchor=self.anchor,anchor_sha256=hashlib.sha256(self.anchor).hexdigest(),
            metadata_url=META,target_url=TARGET,fetcher=self.fetch)
        self.assertEqual(1,t.state()[1]['versions']['root'])
        with patch('tuf.__version__','0.0.0'):
            with self.assertRaisesRegex(RecordError,'update-verifier-version'):
                updater_factory(metadata_dir=str(t.root/'metadata'),metadata_base_url=META,fetcher=self.fetch,bootstrap=None)
