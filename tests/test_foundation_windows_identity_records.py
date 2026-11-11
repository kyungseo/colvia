"""Windows effect publication/reload boundary; APFS doubles, not NTFS qualification."""
import copy,hashlib,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
from colvia.codec import RecordError,canonical_bytes
from colvia.binding import Locator,ProjectBinding,Topology,WorkspaceRegistration
from colvia.connection import Connections,PROJECT_KEY
from colvia.effects import PENDING
from colvia.graph import validate_closure
from colvia.lifecycle import ConnectFiles,_plan,describe_manifest
from colvia.platforms.posix import location
from colvia.platforms.windows_connect import WindowsConnect
from colvia.platforms.windows_effects import WindowsEffects
from colvia.platforms.windows_observation import Observer
from colvia.records import application_registry,record,operation_closure,link
from colvia.storage.authority import Authority
from colvia.worker_records import schemas,native_identity_kind
from test_foundation_binding import P,I,W
from test_foundation_windows_effects import Files,Move

WIN=[2**64-1,'0123456789abcdef'*2,134386959037619337]
MAC=dict(volume='1',inode='2',birth_ns=3)

def manifest(identity):
    return dict(application='sample',root=copy.deepcopy(identity),authority=copy.deepcopy(identity),stage=copy.deepcopy(identity),ancestors={},items=[])

class IdentitySchemaTests(unittest.TestCase):
    def check(self,m):next(s for s in schemas() if s.kind=='worker.manifest').payload({**m,'links':{}})
    def test_exact_variants_and_integer_boundaries(self):
        for value in (MAC,WIN,[0,'0'*32,0],[2**63,'f'*32,2**63-1]):
            with self.subTest(value=value):self.check(manifest(value))
    def test_malformed_windows_variants_refused(self):
        bad=[(),tuple(WIN),WIN[:2],WIN+[0],{},[True,WIN[1],0],[-1,WIN[1],0],[2**64,WIN[1],0],
             [1.0,WIN[1],0],[1,WIN[1],True],[1,WIN[1],-1],[1,WIN[1],2**63],[1,WIN[1],1.0]]
        bad += [[1,x,0] for x in ('a'*31,'a'*33,'A'*32,'0x'+'0'*30,'a'*31+'\n','１'*32,123)]
        for value in bad:
            with self.subTest(value=value),self.assertRaisesRegex(RecordError,'invalid-effect-native-identity'):self.check(manifest(value))
    def test_mixed_manifest_refused(self):
        for field in ('authority','stage'):
            m=manifest(WIN);m[field]=MAC
            with self.subTest(field=field),self.assertRaisesRegex(RecordError,'mixed-effect-native-identity'):self.check(m)
        m=manifest(WIN);m['ancestors']={'folder':MAC}
        with self.assertRaisesRegex(RecordError,'mixed-effect-native-identity'):self.check(m)
    def test_darwin_acceptance_unchanged(self):
        self.assertEqual('darwin',native_identity_kind(MAC))
        with self.assertRaisesRegex(RecordError,'invalid-effect-native-identity'):self.check(manifest({**MAC,'inode':2}))

class WindowsPublicationTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(prefix='windows-publication-');self.base=Path(self.tmp.name)
        self.root=self.base/'project';self.root.mkdir()
        self.authority=Authority.create(self.base/'authority',project=P,instance=I,generation='initial');self.store=self.authority.store()
        top=Topology('plain',location(self.root));locator=Locator(P,I,1,'a'*64,W)
        Connections(self.store).connect(operation='binding',binding=ProjectBinding(locator,'plain',top.root),observed=top,
            workspace=WorkspaceRegistration(W,top.root,None),verify_topology=lambda:top)
        self.files=Files();original=self.files.api.state
        def high_volume(*args,**kw):
            state=original(*args,**kw);state['identity']=(2**64-1,*state['identity'][1:]);return state
        self.files.api.state=high_volume;self.mover=Move(self.files.api)
        self.effects=WindowsEffects(self.root,self.authority.root,files=self.files,observer=Observer(files=self.files),mover=self.mover)
        self.port=WindowsConnect(self.authority.root,{'project':self.root},files=self.files,effects=lambda *_:self.effects)
        self.service=ConnectFiles(self.store,self.port)
        self.changes=[dict(role='entry',root='project',path='AGENTS.md',before=None,after=b'entry',mode='100644'),
                      dict(role='locator',root='project',path='.colvia-link.json',before=None,after=b'locator',mode='100644')]
    def tearDown(self):self.store.close();self.tmp.cleanup()
    def start(self):
        preview=self.service.preview(self.changes)
        return self.service.begin(operation='connect-files',changes=self.changes,receipt=preview['receipt'],statement='Connect synthetic project')
    def reopen(self):
        self.store.close();self.store=self.authority.store();self.service=ConnectFiles(self.store,self.port)
    def test_connect_publication_reload_and_complete(self):
        self.start();self.reopen();registry=application_registry();ref=self.store.head('connect:connect-files')
        validate_closure([ref],self.store.load,registry,operation_closure(registry))
        state=registry.inspect(ref,self.store.load(ref),required=True);pref=link(state,'plan')
        plan=registry.inspect(pref,self.store.load(pref),required=True)
        native=plan.payload['manifest']['steps'][0]['native']['root']
        self.assertIs(type(native),list);self.assertEqual(2**64-1,native[0])
        self.service.advance('connect-files');self.reopen()
        self.assertEqual('connected',self.service.advance('connect-files')['state'])
        self.assertIsNone(self.store.head(PENDING));self.assertIsNotNone(self.store.head(PROJECT_KEY))
        self.assertEqual(b'entry',(self.root/'AGENTS.md').read_bytes());self.assertEqual(b'locator',(self.root/'.colvia-link.json').read_bytes())
    def test_interrupted_intent_reloads_before_explicit_recovery(self):
        self.start()
        def crash(event):
            if event=='intent':raise RuntimeError('synthetic interruption')
        with self.assertRaisesRegex(RuntimeError,'synthetic interruption'):self.service.advance('connect-files',event=crash)
        self.assertFalse((self.root/'AGENTS.md').exists());self.reopen()
        self.service.advance('connect-files');self.service.advance('connect-files')
        self.assertIsNone(self.store.head(PENDING));self.assertEqual(2,self.mover.count)
    def test_worker_manifest_publication_uint64_roundtrip(self):
        for number,volume in enumerate((2**63,2**64-1)):
            m=manifest([volume,WIN[1],WIN[2]]);pair=record('worker.manifest',m,{})
            registry=application_registry()
            self.store.commit_heads(operation='manifest-'+str(number),expected={'test:manifest':self.store.head('test:manifest')},
                changes={'test:manifest':pair[0]},objects=[pair],
                validate=lambda view:validate_closure([pair[0]],view,registry,operation_closure(registry)))
            self.reopen();obj=registry.inspect(pair[0],self.store.load(pair[0]),required=True)
            self.assertEqual(m['root'],obj.payload['root']);self.assertIs(type(obj.payload['root']),list)
    def test_bad_record_refuses_before_effect_reservation(self):
        original=self.port.prepare
        def bad(*args):
            m=original(*args);m['steps'][0]['native']['stage'][1]='not-hex';return m
        with patch.object(self.port,'prepare',bad),self.assertRaisesRegex(RecordError,'invalid-effect-native-identity'):self.start()
        self.assertIsNone(self.store.head(PENDING));self.assertIsNone(self.store.head('connect:connect-files'))
        self.assertFalse((self.root/'AGENTS.md').exists());self.assertEqual(0,self.mover.count)
    def test_mixed_steps_and_file_identity_refuse(self):
        with self.port.exclusion():m=self.port.prepare('mixed',self.changes)
        bad=copy.deepcopy(m);bad['steps'][0]['native']['items'][0]['post_native']=MAC
        check=next(s for s in schemas() if s.kind=='worker.manifest')
        with self.assertRaisesRegex(RecordError,'mixed-effect-native-identity'):check.payload({**bad['steps'][0]['native'],'links':{}})
        n=m['steps'][1]['native']
        for field in ('root','authority','stage'):n[field]=copy.deepcopy(MAC)
        for item in n['items']:
            for field in ('pre_native','post_native'):
                if item[field] is not None:item[field]=copy.deepcopy(MAC)
        p=dict(operation='mixed',manifest=m,statement='Connect',preview_sha256=hashlib.sha256(canonical_bytes(describe_manifest(m))).hexdigest(),links={'binding':[0]})
        with self.assertRaisesRegex(RecordError,'mixed-effect-native-identity'):_plan(p)

if __name__=='__main__':unittest.main()
