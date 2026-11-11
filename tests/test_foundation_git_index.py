import hashlib,struct,unittest
from dataclasses import replace
from colvia.codec import RecordError
from colvia.git_index import Entry,Index,parse,emit,integrate
from test_foundation_git import GitFixture

class CodecTests(unittest.TestCase):
    def entry(self,path='a',value=b'a',mode=0o100644):return Entry(path.encode(),mode,hashlib.sha1(value).digest())
    def test_flags_unrelated_preserved_selected_zeroes_stat(self):
        a=self.entry();b=replace(self.entry('b'),assume=True,extended=0x4000,stat=(0,1,2,3,4,5,0o100644,7,8,9))
        after=replace(a,oid=b'1'*20)
        raw,tree=integrate(Index('sha1',(a,b)),{'a':a},{'a':after})
        parsed=parse(raw);self.assertEqual(3,parsed.version);self.assertEqual(b.content,parsed.by_path()['b'].content);self.assertEqual((b.assume,b.extended),(parsed.by_path()['b'].assume,parsed.by_path()['b'].extended))
        self.assertEqual((0,0,0,0,0,0,0o100644,0,0,0),parsed.by_path()['a'].stat)
        self.assertEqual(['a'],list(parse(tree).by_path()))
        self.assertEqual((0,0,0,0,0,0,0o100644,0,0,0),parsed.by_path()['b'].stat)
    def test_selected_partial_flags_and_opaque_refuse(self):
        a=self.entry();after=replace(a,oid=b'2'*20)
        for changed,code in [(replace(a,oid=b'3'*20),'partial-staging'),(replace(a,mode=0o100755),'partial-staging'),(replace(a,assume=True),'flags'),
                             (replace(a,extended=0x2000),'flags'),(replace(a,mode=0o120000),'opaque')]:
            with self.assertRaisesRegex(RecordError,code):integrate(Index('sha1',(changed,)),{'a':a},{'a':after})
    def test_checksums_extensions_and_padding(self):
        raw=emit(Index('sha1',(self.entry(),)))
        with self.assertRaisesRegex(RecordError,'checksum'):parse(raw[:-1]+b'x')
        body=raw[:-20]+b'TREE'+struct.pack('!I',3)+b'abc';valid=body+hashlib.sha1(body).digest()
        self.assertEqual(raw,emit(parse(valid)))
        for sig in (b'link',b'sdir',b'REUC',b'ABCD'):
            body=raw[:-20]+sig+struct.pack('!I',0)
            with self.assertRaisesRegex(RecordError,'extension'):parse(body+hashlib.sha1(body).digest())
    def test_sha256_long_unicode_and_deletion(self):
        a=Entry(('긴이름/'+'a'*200+'/next').encode(),0o100755,b'1'*32)
        raw=emit(Index('sha256',(a,)));self.assertEqual(a.content,parse(raw,'sha256').entries[0].content)
        i,t=integrate(parse(raw,'sha256'),{a.logical:a},{a.logical:None})
        self.assertEqual((),parse(i,'sha256').entries);self.assertEqual(i,t)
    def test_collision_and_parent_entry(self):
        for entries in [(self.entry('a'),self.entry('a/b')),(self.entry('A'),self.entry('a'))]:
            with self.assertRaisesRegex(RecordError,'collision'):emit(Index('sha1',entries))

class NativeIndexTests(GitFixture,unittest.TestCase):
    def test_roundtrip_real_index_tree_and_unrelated_staging(self):
        (self.root/'other').write_bytes(b'unrelated');self.command('add','other')
        original=parse((self.root/'.git/index').read_bytes());old=self.command('write-tree').strip()
        scratch=self.home/'private-index';scratch.write_bytes(emit(original))
        import subprocess
        result=subprocess.run([str(self.git.executable),'-C',str(self.root),'write-tree'],
            env={**self.env,'GIT_INDEX_FILE':str(scratch)},capture_output=True,check=True,timeout=10)
        self.assertEqual(old,result.stdout.strip())
        self.assertIn('other',original.by_path())

if __name__=='__main__':unittest.main()
