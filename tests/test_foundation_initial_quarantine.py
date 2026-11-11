"""Retired initial target: synthetic APFS nodes only, no installation or model."""
import hashlib,json,os,unittest
from unittest.mock import patch
from colvia.codec import RecordError,canonical_bytes
from colvia.updates.installation import FirstInstall
from colvia.updates.initial_quarantine import InitialQuarantine
from colvia.updates.initial_home import initial_head,retry_claim
from colvia.platforms.owned_install_files import capture
import test_foundation_notice_app as fixture

class InitialQuarantineTests(unittest.TestCase):
    setUp=fixture.NoticeAppTests.setUp
    tearDown=fixture.NoticeAppTests.tearDown
    archive=fixture.NoticeAppTests.archive
    slot=fixture.NoticeAppTests.slot
    repack=fixture.NoticeAppTests.repack
    def partial(self,phase='entry-prepared',occurrence=1):
        count=0
        def stop(current):
            nonlocal count
            if current==phase:
                count+=1
                if count==occurrence:raise RuntimeError('synthetic interruption')
        self.service=FirstInstall(self.home,self.trust,self.config)
        with self.assertRaisesRegex(RuntimeError,'synthetic interruption'):
            self.service.perform(operation='first',checkpoint=stop)
        self.anchor=self.content['root.json'];anchor_hash=hashlib.sha256(self.anchor).hexdigest();f=self.home.files
        saved={k:self.config[k] for k in ('version','channel','metadata_url','target_url','target')}
        f.create(self.home.root/'initial-install.json',canonical_bytes(dict(version=1,operation='first',final_root=str(self.home.root),
            identity=f.directory_identity(self.home.root),payload_sha256='0'*64,config=saved,anchor_sha256=anchor_hash)))
        self.trust.state=lambda:(b'unchanged test trust floors',dict(anchor_sha256=anchor_hash))
        self.q=InitialQuarantine(self.home,self.trust,self.config,self.anchor)
        self.trust.expired=True
        self.trust.target=dict(self.trust.target,sha256='0'*64)
        return self.q.preview(operation='first')
    def apply(self,preview,**kw):return self.q.apply(operation='first',receipt=preview['receipt'],**kw)
    def fresh(self,result):
        saved=self.trust.state
        self.content['bin/colvia']=b'new signed-target fixture native entry';self.repack(2);self.trust.state=saved
        return FirstInstall(self.home,self.trust,self.config).perform(operation=result['operation'],claimed=True,anchor=self.anchor)
    def test_expired_retired_target_quarantine_then_fresh_target_without_reset(self):
        preview=self.partial();h=self.home;f=h.files
        original=(h.root/'operations/first/prepared.json').read_bytes();old_slot=(h.root/'runtime/slots/first/bin/colvia').read_bytes()
        files={n['path']:f.read(h.root/n['path'],64*1024*1024) for n in preview['preview']['nodes'] if n['snapshot']['kind']=='file'}
        trust=self.trust.state()[0];calls=self.trust.calls
        with patch.object(self.trust,'stage',side_effect=AssertionError('no fetch')),patch.object(self.trust,'activation_check',side_effect=AssertionError('no expired activation')):
            result=self.apply(preview)
        self.assertEqual('quarantined',result['state']);self.assertEqual(calls,self.trust.calls);self.assertEqual(trust,self.trust.state()[0])
        intent=json.loads((h.root/'operations/first/quarantine-intent.json').read_text());q=h.root/'operations/first'/intent['area']
        for i,node in enumerate(intent['preview']['nodes']):
            self.assertFalse((h.root/node['path']).exists())
            if node['snapshot']['kind']=='file':self.assertEqual(files[node['path']],(q/str(i)).read_bytes());self.assertEqual(node['snapshot'],capture(f,q/str(i)))
        claim=self.q.claim(operation='first',receipt=preview['receipt']);self.assertEqual('replacement-claimed',claim['state'])
        self.assertEqual('installed',self.fresh(claim)['state']);self.assertEqual(original,(h.root/'operations/first/prepared.json').read_bytes())
        self.assertEqual(old_slot,(h.root/'runtime/slots/first/bin/colvia').read_bytes());self.assertEqual(trust,self.trust.state()[0])
        final={p:p.read_bytes() for p in (h.root/'bin').rglob('*') if p.is_file()}
        self.assertEqual(result,self.apply(preview))
        self.assertEqual('replacement-started',self.q.claim(operation='first',receipt=preview['receipt'])['state'])
        self.assertEqual(final,{p:p.read_bytes() for p in (h.root/'bin').rglob('*') if p.is_file()})
    def test_each_quarantine_interruption_resumes_without_old_forward_or_fork(self):
        # Each independent fixture has one recorded failure and one explicit resume.
        for phase in ('quarantine-intent','quarantine-before-move','quarantine-after-move',
                      'quarantine-before-rmdir','quarantine-after-rmdir','quarantine-before-complete','quarantine-completed'):
            with self.subTest(phase=phase):
                if phase!='quarantine-intent':self.tearDown();self.setUp()
                p=self.partial()
                def stop(current):
                    if current==phase:raise RuntimeError('synthetic quarantine stop')
                with self.assertRaisesRegex(RuntimeError,'synthetic quarantine stop'):self.apply(p,checkpoint=stop)
                for operation in ('resume','refresh','perform'):
                    with self.assertRaises(RecordError):
                        if operation=='resume':self.service.resume(operation='first')
                        elif operation=='refresh':self.service.refresh(operation='first',receipt='invalid',renewal='blocked')
                        else:self.service.perform(operation='first',claimed=True,anchor=self.anchor)
                with self.assertRaises(RecordError):retry_claim(self.home,self.trust,self.config,self.anchor,previous='first',operation='fork')
                self.assertFalse((self.home.root/'operations/fork').exists())
                self.assertEqual('quarantined',self.apply(p)['state'])
    def test_every_partial_publication_position_is_owned_and_quarantinable(self):
        # Nine receiver files/descriptions plus their parent directories are all
        # captured before publication. Count from the first persisted plan.
        first=self.partial('initial-after-publish',1)
        count=len(json.loads((self.home.root/'operations/first/publication.json').read_text())['nodes'])
        self.apply(first)
        for n in range(2,count+1):
            with self.subTest(published=n):
                self.tearDown();self.setUp();p=self.partial('initial-after-publish',n)
                self.assertEqual('quarantined',self.apply(p)['state'])
    def test_unknown_file_and_foreign_pending_refuse_before_intent(self):
        p=self.partial();unknown=self.home.root/'bin/.DS_Store';unknown.write_bytes(b'foreign')
        with self.assertRaisesRegex(RecordError,'extra-path'):self.apply(p)
        self.assertFalse((self.home.root/'operations/first/quarantine-intent.json').exists());self.assertEqual(b'foreign',unknown.read_bytes())
    def test_each_registration_or_foreign_pending_is_refused_without_move(self):
        from colvia.updates.initial_quarantine import FORBIDDEN
        for n,name in enumerate(FORBIDDEN):
            if n:self.tearDown();self.setUp()
            p=self.partial();self.home.files.create(self.home.root/name,b'foreign evidence')
            with self.assertRaisesRegex(RecordError,'foreign-state'):self.apply(p)
            self.assertFalse((self.home.root/'operations/first/quarantine-intent.json').exists())
    def test_same_bytes_replaced_file_and_stale_receipt_are_not_adopted(self):
        p=self.partial();path=self.home.root/'bin/colvia';raw=path.read_bytes();path.rename(path.with_name('held'));path.write_bytes(raw);path.chmod(0o700)
        with self.assertRaisesRegex(RecordError,'native-entry-changed'):self.apply(p)
        self.assertFalse((self.home.root/'operations/first/quarantine-intent.json').exists())
    def test_changed_quarantine_bytes_and_missing_retained_file_refuse(self):
        p=self.partial()
        def stop(phase):
            if phase=='quarantine-after-move':raise RuntimeError('stop')
        with self.assertRaises(RuntimeError):self.apply(p,checkpoint=stop)
        intent=json.loads((self.home.root/'operations/first/quarantine-intent.json').read_text());area=self.home.root/'operations/first'/intent['area']
        retained=next(path for path in area.iterdir() if path.name.isdigit());retained.write_bytes(b'changed')
        with self.assertRaisesRegex(RecordError,'file-changed'):self.apply(p)
        self.assertFalse((self.home.root/'operations/first/quarantine-complete.json').exists())
    def test_extra_file_during_quarantine_is_never_moved_or_removed(self):
        p=self.partial();foreign=self.home.root/'bin/foreign'
        def race(phase):
            if phase=='quarantine-before-move':foreign.write_bytes(b'keep me')
        with self.assertRaisesRegex(RecordError,'extra-path'):self.apply(p,checkpoint=race)
        self.assertEqual(b'keep me',foreign.read_bytes());self.assertFalse((self.home.root/'operations/first/quarantine-complete.json').exists())
    def test_unreceipted_initial_files_are_refused(self):
        p=self.partial();receipt=self.home.root/'operations/first/publication.json';receipt.rename(receipt.with_suffix('.retained'))
        before=(self.home.root/'bin/colvia').read_bytes()
        with self.assertRaises(FileNotFoundError):self.apply(p)
        self.assertEqual(before,(self.home.root/'bin/colvia').read_bytes())
    def test_partial_successor_metadata_resumes_unique_reserved_claim(self):
        p=self.partial();done=self.apply(p);area=self.home.root/'operations'/done['successor'];self.home.files.create_directory(area)
        link=dict(version=1,previous='first',next=done['successor']);self.home.files.create(area/'retry-of.json',canonical_bytes(link))
        claim=self.q.claim(operation='first',receipt=p['receipt']);self.assertEqual(done['successor'],claim['operation'])
        self.assertEqual(claim,self.q.claim(operation='first',receipt=p['receipt']))
        with self.assertRaises(RecordError):retry_claim(self.home,self.trust,self.config,self.anchor,previous='first',operation='another')
    def test_no_new_attempt_before_quarantine_completion_even_when_live_paths_absent(self):
        p=self.partial()
        def stop(phase):
            if phase=='quarantine-before-complete':raise RuntimeError('stop')
        with self.assertRaises(RuntimeError):self.apply(p,checkpoint=stop)
        self.assertFalse((self.home.root/'bin').exists())
        with self.assertRaisesRegex(RecordError,'incomplete'):retry_claim(self.home,self.trust,self.config,self.anchor,previous='first',operation='fork')
        with self.assertRaisesRegex(RecordError,'anchor|required|not-current'):
            self.service.perform(operation='unlinked')
        self.assertFalse((self.home.root/'bin').exists())
    def test_bad_review_and_existing_runtime_preserve_files(self):
        p=self.partial()
        with self.assertRaisesRegex(RecordError,'review-changed'):self.q.apply(operation='first',receipt='0'*64)
        target=json.loads((self.home.root/'operations/first/prepared.json').read_text())['target'];self.home.slots.initialize(target)
        with self.assertRaisesRegex(RecordError,'already-active'):self.apply(p)
        self.assertTrue((self.home.root/'bin/colvia').exists())

    def test_unexpected_link_and_mode_changes_never_move_the_file(self):
        for kind in ('symlink','hardlink','mode','permissions'):
            with self.subTest(kind=kind):
                if kind!='symlink':self.tearDown();self.setUp()
                p=self.partial();path=self.home.root/'bin/colvia'
                if kind=='symlink':
                    path.rename(path.with_name('preserved'));path.symlink_to('preserved')
                elif kind=='hardlink':os.link(path,self.base/'other-hardlink')
                elif kind=='mode':path.chmod(0o600)
                else:path.chmod(0o777)
                with self.assertRaises(RecordError):self.apply(p)
                self.assertFalse((self.home.root/'operations/first/quarantine-intent.json').exists())
    def test_unacknowledged_move_is_inspected_and_not_repeated(self):
        p=self.partial()
        from colvia.updates import initial_quarantine as module
        original=module.move;calls=[]
        def lose(*args,**kwargs):
            calls.append(args[1]);original(*args,**kwargs);raise OSError('lost move acknowledgement')
        with patch.object(module,'move',side_effect=lose),self.assertRaises(OSError):self.apply(p)
        retained=calls[0]
        with patch.object(module,'move',wraps=original) as later:self.apply(p)
        self.assertNotIn(retained,[c.args[1] for c in later.call_args_list])
    def test_nonempty_directory_race_is_refused_by_native_rmdir(self):
        p=self.partial();foreign=self.home.root/'bin/foreign'
        from colvia.platforms import owned_install_files as native
        real=native.os.rmdir
        def race(name,**kwargs):
            if name=='bin':foreign.write_bytes(b'preserve foreign')
            return real(name,**kwargs)
        with patch.object(native.os,'rmdir',side_effect=race),self.assertRaises(OSError):self.apply(p)
        self.assertEqual(b'preserve foreign',foreign.read_bytes())
    def test_two_attempts_cannot_both_claim_the_preview(self):
        import concurrent.futures
        p=self.partial()
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
            futures=[pool.submit(self.apply,p) for _ in range(2)]
            results=[future.result() for future in futures]
        self.assertEqual(results[0],results[1])
        a=self.q.claim(operation='first',receipt=p['receipt']);b=self.q.claim(operation='first',receipt=p['receipt'])
        self.assertEqual(a,b)
    def test_verified_bootstrap_inspects_offline_and_fetches_only_after_link(self):
        from colvia.updates.installation import bootstrap
        from contextlib import ExitStack
        from types import SimpleNamespace
        p=self.partial();h=self.home;area=h.root/'operations/first'
        prepared=json.loads((area/'prepared.json').read_text());slot=h.slots.verify(prepared['target']);stage=h.slots.root/'slots/first'
        manifest=json.loads((stage/'manifest.json').read_text());self.home.files.create(h.root/'updates.json',canonical_bytes({k:self.config[k] for k in ('version','channel','metadata_url','target_url','target')}))
        events=[]
        def fetcher(**kw):
            self.assertTrue((area/'quarantine-complete.json').is_file());self.assertTrue((area/'retried-by.json').is_file())
            events.append('fetcher');return SimpleNamespace(close=lambda:events.append('close'))
        with ExitStack() as stack:
            stack.enter_context(patch('colvia.updates.installation.current_platform',return_value=('macos','arm64')))
            stack.enter_context(patch('colvia.updates.installation.process_runtime',return_value=(slot.python,manifest['python_version'],manifest['sqlite_version'])))
            stack.enter_context(patch('colvia.updates.installation.Trust',return_value=self.trust))
            network=stack.enter_context(patch('colvia.updates.installation.https_fetcher',side_effect=fetcher))
            view=bootstrap(h.root,stage,prepared['target']['manifest_sha256'],quarantine_operation='first')
            self.assertEqual(p['receipt'],view['receipt']);self.assertEqual([],events)
            with patch.object(FirstInstall,'perform',side_effect=RuntimeError('new download unavailable')):
                with self.assertRaises(RuntimeError):bootstrap(h.root,stage,prepared['target']['manifest_sha256'],quarantine_operation='first',quarantine_receipt=p['receipt'])
            self.assertEqual(['fetcher','close'],events)
            self.assertFalse((h.slots.root/'runtime.json').exists());self.assertTrue((area/'quarantine-complete.json').is_file())
    def test_same_receipt_after_new_download_failure_does_not_repeat_download(self):
        p=self.partial();self.apply(p);claim=self.q.claim(operation='first',receipt=p['receipt'])
        with patch.object(self.trust,'stage',side_effect=RuntimeError('download failed')) as stage:
            with self.assertRaises(RuntimeError):self.service.perform(operation=claim['operation'],claimed=True,anchor=self.anchor)
        self.assertEqual(1,stage.call_count)
        self.assertEqual('replacement-started',self.q.claim(operation='first',receipt=p['receipt'])['state'])
        self.assertTrue((self.home.root/'operations'/claim['operation']/'started.json').exists())

    def test_real_fixed_trust_metadata_and_floors_stay_byte_identical(self):
        from test_foundation_initial_home import FixedTrust
        from test_foundation_trust import FIXTURE,META,TARGET,MemoryFetcher
        p=self.partial();anchor=(FIXTURE/'metadata/root.json').read_bytes();fetch=MemoryFetcher()
        real=FixedTrust.initialize(self.home.root/'trust',anchor=anchor,anchor_sha256=hashlib.sha256(anchor).hexdigest(),
            metadata_url=META,target_url=TARGET,fetcher=fetch,files=self.home.files)
        # Learn authenticated metadata first, using the existing fixed keys.
        real.stage('file1.txt',destination=self.base/'fixed-fixture.txt',already_present=lambda _:True)
        marker=self.home.root/'initial-install.json';old=marker.read_bytes();value=json.loads(old)
        value['anchor_sha256']=hashlib.sha256(anchor).hexdigest();self.home.files.replace(marker,canonical_bytes(value),old)
        q=InitialQuarantine(self.home,real,self.config,anchor)
        before={x:x.read_bytes() for x in (self.home.root/'trust').rglob('*') if x.is_file()};calls=list(fetch.calls)
        with patch.object(real,'activation_check',side_effect=AssertionError('expired target must not be activated')):
            preview=q.preview(operation='first');q.apply(operation='first',receipt=preview['receipt']);q.claim(operation='first',receipt=preview['receipt'])
        self.assertEqual(before,{x:x.read_bytes() for x in (self.home.root/'trust').rglob('*') if x.is_file()})
        self.assertEqual(calls,fetch.calls)
    def test_identical_foreign_initial_directory_is_not_given_ownership(self):
        self.home.files.create_directory(self.home.root/'bin')
        self.home.files.create(self.home.root/'bin/colvia',self.content['bin/colvia'],executable=True)
        before=capture(self.home.files,self.home.root/'bin/colvia')
        with self.assertRaisesRegex(RecordError,'initial-publication-foreign'):
            FirstInstall(self.home,self.trust,self.config).perform(operation='first')
        self.assertEqual(before,capture(self.home.files,self.home.root/'bin/colvia'))
        self.assertFalse((self.home.root/'operations/first/publication.json').exists())

    def test_denied_lookup_never_becomes_absence(self):
        from colvia.platforms import owned_install_files as native
        p=self.partial();real=native.os.lstat;blocked=self.home.root/'notice-registration.json'
        def denied(path,*args,**kwargs):
            if str(path)==str(blocked):raise PermissionError('synthetic denied')
            return real(path,*args,**kwargs)
        with patch.object(native.os,'lstat',side_effect=denied),self.assertRaises(PermissionError):self.apply(p)
        self.assertFalse((self.home.root/'operations/first/quarantine-intent.json').exists())
        self.assertTrue((self.home.root/'bin/colvia').is_file())
    def test_replaced_quarantine_parent_refuses_before_first_move(self):
        p=self.partial();area=self.home.root/'operations/first'
        def swap(phase):
            if phase=='quarantine-before-move':
                intent=json.loads((area/'quarantine-intent.json').read_text());q=area/intent['area']
                q.rename(q.with_name(q.name+'-preserved'));self.home.files.create_directory(q)
        with self.assertRaisesRegex(RecordError,'quarantine-changed'):self.apply(p,checkpoint=swap)
        self.assertTrue((self.home.root/'bin/colvia').is_file());self.assertFalse((area/'quarantine-complete.json').exists())
    def test_returned_live_file_prevents_completion(self):
        p=self.partial();area=self.home.root/'operations/first'
        def return_file(phase):
            if phase=='quarantine-before-complete':
                intent=json.loads((area/'quarantine-intent.json').read_text())
                i=next(i for i,n in enumerate(intent['preview']['nodes']) if n['path']=='entry.json')
                (area/intent['area']/str(i)).rename(self.home.root/'entry.json')
        with self.assertRaisesRegex(RecordError,'incomplete'):self.apply(p,checkpoint=return_file)
        self.assertFalse((area/'quarantine-complete.json').exists());self.assertTrue((self.home.root/'entry.json').exists())
        self.assertEqual('quarantined',self.apply(p)['state'])
    def test_resume_resyncs_before_quarantine_completion(self):
        p=self.partial();f=self.home.files;real=f.sync_directory;ready=False;seen=[]
        def checkpoint(phase):
            nonlocal ready
            if phase=='quarantine-before-complete':ready=True
        def fail(path):
            if ready and path==self.home.root:raise OSError('synthetic sync failure')
            return real(path)
        with patch.object(f,'sync_directory',side_effect=fail),self.assertRaisesRegex(OSError,'sync failure'):
            self.apply(p,checkpoint=checkpoint)
        self.assertFalse((self.home.root/'operations/first/quarantine-complete.json').exists())
        def observe(path):seen.append(path);return real(path)
        with patch.object(f,'sync_directory',side_effect=observe):self.apply(p)
        self.assertIn(self.home.root,seen)
    def test_claim_refuses_new_registration_after_completed_quarantine(self):
        p=self.partial();self.apply(p);self.home.files.create(self.home.root/'notice-registration.json',b'foreign')
        with self.assertRaisesRegex(RecordError,'live-effects'):self.q.claim(operation='first',receipt=p['receipt'])
        self.assertFalse((self.home.root/'operations/first/retried-by.json').exists())
    def test_completed_malformed_intent_raises_record_error(self):
        from colvia.updates.initial_quarantine import completed
        p=self.partial();self.apply(p);path=self.home.root/'operations/first/quarantine-intent.json'
        self.home.files.replace(path,canonical_bytes({}),path.read_bytes())
        with self.assertRaisesRegex(RecordError,'invalid'):completed(self.home,'first')
    def test_old_receipt_reports_descendant_without_new_install(self):
        p=self.partial();self.apply(p);first=self.q.claim(operation='first',receipt=p['receipt'])
        retry_claim(self.home,self.trust,self.config,self.anchor,previous=first['operation'],operation='grandchild')
        self.assertEqual(dict(operation='grandchild',state='replacement-superseded'),self.q.claim(operation='first',receipt=p['receipt']))
        self.assertFalse((self.home.root/'operations/grandchild/started.json').exists())
    def test_publication_lost_sync_ack_is_resynced_before_runtime_selection(self):
        from colvia.updates import initial_files as module
        original=module.move;f=self.home.files;sync=f.sync_directory;seen=[]
        def lose(*args,**kwargs):original(*args,**kwargs);raise OSError('lost publication acknowledgement')
        service=FirstInstall(self.home,self.trust,self.config)
        with patch.object(module,'move',side_effect=lose),self.assertRaises(OSError):service.perform(operation='first')
        self.assertFalse((self.home.slots.root/'runtime.json').exists())
        def observed(path):seen.append(path);return sync(path)
        with patch.object(f,'sync_directory',side_effect=observed):result=service.resume(operation='first')
        self.assertEqual('installed',result['state']);self.assertIn(self.home.root,seen);self.assertIn(self.home.root/'bin',seen)
    def test_publication_parent_binding_refuses_substituted_destination(self):
        from colvia.platforms.owned_install_files import move
        f=self.home.files;left=self.base/'left';right=self.base/'right'
        f.create_directory(left);f.create_directory(right);f.create(left/'file',b'owned')
        snapshot=capture(f,left/'file');parents={left:f.directory_identity(left),right:f.directory_identity(right)}
        right.rename(self.base/'right-preserved');f.create_directory(right)
        with self.assertRaisesRegex(RecordError,'parent-changed'):move(f,left/'file',right/'file',snapshot,parent_identities=parents)
        self.assertTrue((left/'file').is_file());self.assertFalse((right/'file').exists())
