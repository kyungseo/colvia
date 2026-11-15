"""Native index transition protocol using APFS doubles, never Windows execution."""
from pathlib import Path
import tempfile,unittest
from colvia.codec import RecordError,require
from colvia.platforms.windows_git_index import WindowsIndex
from colvia.platforms.windows_observation import Observer
from test_foundation_windows_effects import Files,Move


class TunnelingMove(Move):
    def __init__(self,api):
        super().__init__(api);self.names={};self.creations={};state=api.state
        def observed(h,path,**kw):
            result=state(h,path,**kw);identity=result['identity']
            if identity[:2] in self.creations:
                result['identity']=(*identity[:2],self.creations[identity[:2]])
            return result
        api.state=observed
    def move(self,source,target,*,expected,before_effect,event,inherited_creation=None,gate_intent=None):
        source,target=Path(source),Path(target)
        previous=self.api.state(source,source)
        self.names[source]=previous['identity'][2]
        def moved(phase):
            if phase=='after-native-move' and target in self.names:
                now=self.api.state(target,target)
                self.creations[now['identity'][:2]]=self.names[target]
                require(inherited_creation==self.names[target] or (gate_intent==expected['identity'] and expected['size']==0),'windows-rename-result-changed')
            event(phase)
        return super().move(source,target,expected=expected,before_effect=before_effect,event=moved,gate_intent=gate_intent)

class WindowsIndexTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(prefix='windows-index-');self.root=Path(self.tmp.name)
        self.gitdir=self.root/'gitdir';self.area=self.root/'private';self.gitdir.mkdir();self.area.mkdir(mode=0o700)
        self.files=Files();self.mover=TunnelingMove(self.files.api)
        self.port=WindowsIndex(self.gitdir,self.area,files=self.files,observer=Observer(files=self.files),mover=self.mover)
        self.lock=self.gitdir/'index.lock';self.lock.write_bytes(b'');self.lock_identity=self.port.observe(self.lock)
    def tearDown(self):self.tmp.cleanup()
    def own(self):require(self.port.observe(self.lock)==self.lock_identity,'git-index-lock-not-owned')
    def prepare(self,before=b'old index'):
        if before is not None:(self.gitdir/'index').write_bytes(before)
        return self.port.prepare(self.port.observe(self.gitdir/'index'),b'approved index')
    def publish(self,m,**kwargs):return self.port.publish(m,assert_owned=self.own,live=lambda:None,**kwargs)
    def test_original_and_lock_survive_exact_publication(self):
        m=self.prepare();self.assertEqual('new',self.publish(m));self.assertEqual(b'old index',(self.area/'index-original').read_bytes())
        self.assertEqual(b'approved index',(self.gitdir/'index').read_bytes());self.own()
        self.publish(m);self.assertEqual(2,self.mover.count)
    def test_crash_after_evacuating_is_not_a_missing_original(self):
        m=self.prepare()
        def crash(phase):
            if phase=='after-native-move':raise RuntimeError('synthetic crash')
        with self.assertRaises(RuntimeError):self.publish(m,event=crash)
        self.assertEqual('evacuated',self.port.state(m));self.assertFalse((self.gitdir/'index').exists());self.own()
        self.assertEqual('new',self.publish(m));self.assertEqual(2,self.mover.count)
    def test_competing_index_preserved_and_no_replacement(self):
        m=self.prepare()
        def competing(phase):
            if phase=='after-native-move':(self.gitdir/'index').write_bytes(b'foreign index')
        with self.assertRaisesRegex(RecordError,'external-divergence'):self.publish(m,event=competing)
        self.assertEqual(b'foreign index',(self.gitdir/'index').read_bytes());self.assertEqual(1,self.mover.count)
    def test_changed_retained_original_prevents_resume(self):
        m=self.prepare()
        def crash(phase):
            if phase=='after-native-move':raise RuntimeError('synthetic crash')
        with self.assertRaises(RuntimeError):self.publish(m,event=crash)
        (self.area/'index-original').write_bytes(b'changed')
        with self.assertRaisesRegex(RecordError,'external-divergence'):self.publish(m)
        self.assertEqual(1,self.mover.count)
    def test_missing_or_replaced_gate_refuses_before_effect(self):
        m=self.prepare();self.lock.unlink();self.lock.write_bytes(b'foreign')
        with self.assertRaisesRegex(RecordError,'lock-not-owned'):self.publish(m)
        self.assertEqual(0,self.mover.count)
    def test_initially_absent_index_needs_one_move(self):
        m=self.prepare(None);self.assertEqual('new',self.publish(m));self.assertEqual(1,self.mover.count)
        self.assertFalse((self.area/'index-original').exists())


    def test_tunneled_publication_lost_ack_is_classified_without_second_move(self):
        m=self.prepare()
        def lost(phase):
            if phase=='after-native-move' and (self.gitdir/'index').exists():raise RuntimeError('lost ack')
        with self.assertRaisesRegex(RuntimeError,'lost ack'):self.publish(m,event=lost)
        current=self.port.observe(self.gitdir/'index')
        self.assertEqual(m['after']['identity'][:2],current['identity'][:2])
        self.assertEqual(m['before']['identity'][2],current['identity'][2])
        self.assertEqual('new',self.port.state(m));count=self.mover.count
        self.publish(m);self.assertEqual(count,self.mover.count)

    def test_published_match_requires_id_hash_size_and_known_creation(self):
        from colvia.platforms.windows_git_index import matches_published
        expected=dict(identity=[1,'prepared',2],sha256='approved',size=8)
        actual={**expected,'identity':[1,'prepared',1]}
        self.assertTrue(matches_published(actual,expected,1))
        for bad in ({**actual,'identity':[2,'prepared',1]},
                    {**actual,'identity':[1,'foreign',1]},
                    {**actual,'identity':[1,'prepared',9]},
                    {**actual,'sha256':'foreign'},{**actual,'size':9}):
            self.assertFalse(matches_published(bad,expected,1))
        self.assertFalse(matches_published(actual,expected,None))

    def test_tunneled_current_does_not_hide_changed_saved_original(self):
        m=self.prepare();self.publish(m)
        (self.area/'index-original').write_bytes(b'changed original')
        self.assertEqual('other',self.port.state(m))
        with self.assertRaisesRegex(RecordError,'external-divergence'):self.publish(m)


if __name__=='__main__':unittest.main()
