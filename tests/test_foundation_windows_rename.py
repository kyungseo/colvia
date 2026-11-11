"""No-replace protocol and Windows ABI packing; no native Windows qualification."""
from contextlib import contextmanager
from io import BytesIO
import ctypes as C,hashlib,unittest
from colvia.codec import RecordError
from colvia.platforms.windows_rename import ExactMove,RenameAPI,RenameInfo,rename_info

SOURCE=r'C:\project\report.md'
TARGET=r'C:\authority\effects\original'
PARENT=r'C:\authority\effects'

class Stub:
    def __init__(self):
        self.nodes={SOURCE:dict(identity=(1,'source',1),directory=False,links=1,size=3,write=1,change=1,raw=b'old'),
                    PARENT:dict(identity=(1,'parent',1),directory=True,links=1,size=0,write=1,change=1)}
        self.handles={};self.calls=[];self.refuse=False
    @contextmanager
    def ancestors(self,path):self.calls.append(('ancestors',path));yield
    @contextmanager
    def opened(self,path,**kw):
        self.calls.append(('open',path,kw))
        if self.refuse and path==SOURCE:raise PermissionError('synthetic sharing violation')
        h=len(self.handles)+1;self.handles[h]=path
        try:yield h
        finally:self.calls.append(('close',h))
    def state(self,h,path):
        assert self.handles[h]==path
        return {k:v for k,v in self.nodes[path].items() if k!='raw'}
    def rename(self,h,target):
        self.calls.append(('rename',target))
        if target in self.nodes:raise FileExistsError(target)
        self.nodes[target]=self.nodes.pop(self.handles[h]);self.handles[h]=target
    @contextmanager
    def _stream_handle(self,h):yield BytesIO(self.nodes[self.handles[h]]['raw'])

class WindowsRenameTests(unittest.TestCase):
    def setUp(self):
        self.api=Stub();self.port=ExactMove(api=self.api,files=self.api)
        self.expected=dict(identity=[1,'source',1],size=3,sha256=hashlib.sha256(b'old').hexdigest())
    def move(self,**kw):return self.port.move(SOURCE,TARGET,expected=self.expected,**kw)
    def test_exact_handle_and_no_replace(self):
        self.assertEqual(self.expected,self.move());self.assertNotIn(SOURCE,self.api.nodes)
        self.assertEqual(b'old',self.api.nodes[TARGET]['raw'])
        opening=next(c for c in self.api.calls if c[:2]==('open',SOURCE))
        self.assertEqual(dict(access=0x80010080,share=1),opening[2])
        self.assertEqual([('ancestors',SOURCE),('ancestors',TARGET)],self.api.calls[:2])
        parent=next(c for c in self.api.calls if c[:2]==('open',PARENT))
        self.assertEqual(3,parent[2]['share'])
    def test_competing_target_preserved_without_retry(self):
        self.api.nodes[TARGET]={**self.api.nodes[SOURCE],'raw':b'new'}
        with self.assertRaises(FileExistsError):self.move()
        self.assertEqual(b'old',self.api.nodes[SOURCE]['raw']);self.assertEqual(b'new',self.api.nodes[TARGET]['raw'])
        self.assertEqual(1,len([c for c in self.api.calls if c[0]=='rename']))
    def test_changed_source_never_moved(self):
        self.api.nodes[SOURCE]['raw']=b'new'
        with self.assertRaisesRegex(RecordError,'source-changed'):self.move()
        self.assertFalse(any(c[0]=='rename' for c in self.api.calls))
    def test_journal_failure_prevents_effect(self):
        def refuse():raise RuntimeError('journal refused')
        with self.assertRaisesRegex(RuntimeError,'journal refused'):self.move(before_effect=refuse)
        self.assertFalse(any(c[0]=='rename' for c in self.api.calls))
    def test_after_move_failure_retains_unknown_effect_without_undo(self):
        def fail(name):
            if name=='after-native-move':raise RuntimeError('lost completion')
        with self.assertRaisesRegex(RuntimeError,'lost completion'):self.move(event=fail)
        self.assertEqual(b'old',self.api.nodes[TARGET]['raw']);self.assertNotIn(SOURCE,self.api.nodes)
        self.assertEqual(1,len([c for c in self.api.calls if c[0]=='rename']))
    def test_sharing_refusal_does_not_expand_permissions(self):
        self.api.refuse=True
        with self.assertRaises(PermissionError):self.move()
        self.assertEqual(1,len([c for c in self.api.calls if c[:2]==('open',SOURCE)]))
        self.assertFalse(any(c[0]=='rename' for c in self.api.calls))
    def test_cross_volume_and_hardlinks_refuse(self):
        self.api.nodes[PARENT]['identity']=(2,'parent',1)
        with self.assertRaisesRegex(RecordError,'volume-mismatch'):self.move()
        self.api.nodes[PARENT]['identity']=(1,'parent',1);self.api.nodes[SOURCE]['links']=2
        with self.assertRaisesRegex(RecordError,'source-invalid'):self.move()
    def test_mutation_at_effect_boundary_is_detected(self):
        def change():self.api.nodes[SOURCE]['write']=2
        with self.assertRaisesRegex(RecordError,'source-changed'):self.move(before_effect=change)
        self.assertFalse(any(c[0]=='rename' for c in self.api.calls))
    def test_utf16_buffer_has_false_replace_and_absolute_target(self):
        value=rename_info(r'C:\target\보고서-😀.md');h=RenameInfo.from_buffer(value)
        self.assertEqual(0,h.flags);self.assertIsNone(h.directory)
        raw=r'C:\target\보고서-😀.md'.encode('utf-16-le');self.assertEqual(len(raw),h.length)
        self.assertEqual(raw,value.raw[RenameInfo.name.offset:RenameInfo.name.offset+h.length])
        self.assertEqual(24,C.sizeof(RenameInfo))
        # Both supported Windows architectures use the 64-bit pointer ABI.
        self.assertEqual((8,16,20),(RenameInfo.directory.offset,RenameInfo.length.offset,RenameInfo.name.offset))
    def test_rename_api_uses_only_basic_no_replace_class(self):
        api=object.__new__(RenameAPI);seen=[]
        api.ok=lambda x:x
        def call(h,kind,value,size):
            info=RenameInfo.from_buffer(value);seen.append((h,kind,info.flags,info.directory));return 1
        api.SetFileInformationByHandle=call;api.rename(7,TARGET)
        self.assertEqual([(7,3,0,None)],seen)
    def test_noncanonical_target_rejected(self):
        for name in ('','..','a/b','a\\b','a\0b'):
            with self.subTest(name=name),self.assertRaises(RecordError):rename_info(name)

if __name__=='__main__':unittest.main()
