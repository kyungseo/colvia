from pathlib import Path
import tempfile
import unittest
from colvia.codec import RecordError, canonical_bytes
from colvia.storage.authority import Authority


class InjectedCrash(Exception): pass


class GenerationTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(prefix='authority-')
        self.root=Path(self.tmp.name)/'authority'
        self.authority=Authority.create(self.root,project='p',instance='i',generation='g1')
        candidate=self.authority.prepare_empty('g2'); candidate.close()
        self.old=self.authority.store(); self.reader=self.authority.store(readonly=True)
        self.before=self.old.root().ref
    def tearDown(self):
        self.reader.close(); self.old.close(); self.tmp.cleanup()
    def validate(self,store): self.assertEqual(self.before,store.root().ref)
    def activate(self,phase=None):
        def checkpoint(current):
            if current==phase: raise InjectedCrash(current)
        return self.authority.activate('op',target_generation='g2',expected_root=self.before,
            validate_effects=lambda _:None,validate_target=self.validate,checkpoint=checkpoint)
    def recover(self,complete=True):
        return self.authority.recover('op',complete=complete,validate_effects=lambda _:None,validate_target=self.validate)

    def test_activation_keeps_old_database_and_stops_old_handles(self):
        inode=(self.root/'stores/g1/state.sqlite3').stat().st_ino
        self.assertEqual(self.before,self.activate())
        self.assertEqual(inode,(self.root/'stores/g1/state.sqlite3').stat().st_ino)
        self.assertEqual('g2',self.authority.pointer_value()['generation'])
        for handle in (self.old,self.reader):
            with self.assertRaisesRegex(RecordError,'active-generation-changed'): handle.root()
        self.assertFalse((self.root/'pending.json').exists())

    def test_quiescent_failure_leaves_reads_and_blocks_writes_until_explicit_cancel(self):
        with self.assertRaises(InjectedCrash): self.activate('quiescent')
        self.assertEqual(self.before,self.reader.root().ref)
        with self.assertRaisesRegex(RecordError,'generation-quiescent'): self.old.begin_import('i1','owner')
        self.assertEqual(self.before,self.recover(complete=False))
        self.old.begin_import('i1','owner')
        self.assertEqual('g1',self.authority.pointer_value()['generation'])

    def test_fenced_failure_cannot_unfence_and_completes_only_recorded_target(self):
        with self.assertRaises(InjectedCrash): self.activate('fenced')
        self.assertEqual('g1',self.authority.pointer_value()['generation'])
        for handle in (self.old,self.reader):
            with self.assertRaisesRegex(RecordError,'generation-retired'): handle.root()
        with self.assertRaisesRegex(RecordError,'retired-generation-cannot-resume'): self.recover(False)
        self.assertEqual(self.before,self.recover())
        self.assertEqual('g2',self.authority.pointer_value()['generation'])

    def test_after_pointer_failure_recovers_without_replacing_either_db(self):
        before={p:p.stat().st_ino for p in (self.root/'stores').glob('*/state.sqlite3')}
        with self.assertRaises(InjectedCrash): self.activate('pointer')
        self.assertEqual('g2',self.authority.pointer_value()['generation'])
        self.recover()
        self.assertEqual(before,{p:p.stat().st_ino for p in before})

    def test_intent_failure_can_explicitly_cancel_or_complete(self):
        with self.assertRaises(InjectedCrash): self.activate('intent')
        self.assertEqual(self.before,self.old.root().ref)
        self.recover()
        self.assertEqual('g2',self.authority.pointer_value()['generation'])

    def test_pending_activation_cannot_be_restarted(self):
        with self.assertRaises(InjectedCrash): self.activate('quiescent')
        with self.assertRaisesRegex(RecordError,'activation-already-pending'): self.activate()
        self.assertEqual('g1',self.authority.pointer_value()['generation'])

    def test_target_change_or_unresolved_effects_refuse_before_fence(self):
        def refuse(_): raise RecordError('effects-unresolved')
        with self.assertRaisesRegex(RecordError,'effects-unresolved'):
            self.authority.activate('op',target_generation='g2',expected_root=self.before,
                validate_effects=refuse,validate_target=self.validate)
        self.assertEqual(self.before,self.old.root().ref)
        self.assertIsNone(self.old.lifecycle_state()['fence'])
        self.assertFalse((self.root/'pending.json').exists())
        self.old.begin_import('still-writable','owner')

    def test_target_is_sealed_and_pending_active_writes_refuse(self):
        with self.assertRaises(InjectedCrash): self.activate('target-ready')
        candidate=self.authority._open_recorded(self.authority._plan('op')['new'],self.authority._plan('op'),readonly=False)
        try:
            with self.assertRaisesRegex(RecordError,'generation-quiescent'):
                candidate.begin_import('late','owner')
        finally: candidate.close()
        self.recover()
        active=self.authority.store()
        try: active.begin_import('after','owner')
        finally: active.close()

    def test_released_target_stays_blocked_until_pending_marker_removed(self):
        with self.assertRaises(InjectedCrash): self.activate('target-released')
        active=self.authority.store()
        try:
            with self.assertRaisesRegex(RecordError,'activation-pending'):
                active.begin_import('late','owner')
        finally: active.close()
        self.recover()
        active=self.authority.store()
        try: active.begin_import('after','owner')
        finally: active.close()


    def test_explicit_recovery_rolls_back_hot_journals_on_both_recorded_stores(self):
        import os, select, subprocess, sys
        if os.name!='posix': self.skipTest('POSIX subprocess signal fixture')
        candidate=self.authority._open_recorded(
            dict(self.authority.pointer_value(),generation='g2'),
            dict(old=self.authority.pointer_value(),new=dict(self.authority.pointer_value(),generation='g2'),operation='op'),
            readonly=False)
        try:
            for handle in (self.old,candidate):
                handle.db.execute('BEGIN IMMEDIATE')
                handle.db.executemany('INSERT INTO imports VALUES(?,?,?)',
                    [(f'i-{n}','a'*128,'active') for n in range(1000)])
                handle.db.execute('COMMIT')
        finally: candidate.close()
        with self.assertRaises(InjectedCrash): self.activate('fenced')
        code="""import sqlite3,sys,time
c=sqlite3.connect(sys.argv[1],isolation_level=None)
c.execute('PRAGMA cache_size=2');c.execute('PRAGMA cache_spill=2');c.execute('PRAGMA synchronous=EXTRA')
c.execute('BEGIN IMMEDIATE');c.execute('UPDATE imports SET owner=?',('b'*128,))
c.execute('INSERT INTO objects VALUES(?,?,?,?,?,0)',('f'*64,'body.chunk',1,1048576,b'x'*1048576))
print('ready',flush=True);time.sleep(30)
"""
        for generation in ('g1','g2'):
            path=self.root/'stores'/generation/'state.sqlite3'
            child=subprocess.Popen([sys.executable,'-I','-B','-c',code,str(path)],
                stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
            try:
                ready,_,_=select.select([child.stdout],[],[],5)
                self.assertTrue(ready,'writer readiness timeout')
                self.assertEqual('ready',child.stdout.readline().strip())
                child.kill();child.wait(timeout=5)
                journal=Path(str(path)+'-journal')
                self.assertEqual(bytes.fromhex('d9d505f920a163d7'),journal.read_bytes()[:8])
            finally:
                if child.poll() is None: child.kill();child.wait(timeout=5)
                child.stdout.close();child.stderr.close()
        self.assertEqual(self.before,self.recover())
        active=self.authority.store()
        try:
            self.assertEqual('ok',active.db.execute('PRAGMA integrity_check').fetchone()[0])
            self.assertEqual({'a'*128},{row[0] for row in active.db.execute('SELECT owner FROM imports')})
            self.assertIsNone(active.db.execute('SELECT digest FROM objects WHERE digest=?',('f'*64,)).fetchone())
        finally: active.close()

    def test_generation_names_cannot_escape_store_directory(self):
        for name in ("..", ".", "../other", "/other", "a/b", "\\server", ""): 
            with self.subTest(name=name), self.assertRaises(RecordError): self.authority.prepare_empty(name)

    def test_no_path_reuse_or_symlink_pointer(self):
        with self.assertRaises(FileExistsError): self.authority.prepare_empty('g2')
        pointer=self.root/'active.json'; raw=pointer.read_bytes()
        pointer.unlink(); (self.root/'elsewhere').write_bytes(raw); pointer.symlink_to('elsewhere')
        with self.assertRaises(OSError): self.old.root()


    def test_second_effect_check_refusal_aborts_only_owned_pre_fence_state(self):
        calls=[]
        def effects(_):
            calls.append(True)
            if len(calls)==2:raise RecordError('external-effect-pending')
        with self.assertRaisesRegex(RecordError,'external-effect-pending'):
            self.authority.activate('op',target_generation='g2',expected_root=self.before,
                validate_effects=effects,validate_target=self.validate)
        self.assertEqual(2,len(calls))
        self.assertFalse((self.root/'pending.json').exists())
        self.assertEqual({'fence':None,'quiescent':None},self.old.lifecycle_state())
        self.old.begin_import('after-refusal','fixture')
        self.assertTrue((self.root/'lifecycle/op.json').exists())

    def test_permission_failure_during_second_effect_check_keeps_recovery_pending(self):
        calls=[]
        def effects(_):
            calls.append(True)
            if len(calls)==2:raise PermissionError('synthetic permission refusal')
        with self.assertRaises(PermissionError):
            self.authority.activate('op',target_generation='g2',expected_root=self.before,
                validate_effects=effects,validate_target=self.validate)
        self.assertTrue((self.root/'pending.json').exists())
        self.assertIsNone(self.old.lifecycle_state()['fence'])
        with self.assertRaisesRegex(RecordError,'activation-pending'):
            self.old.begin_import('not-retried','fixture')


if __name__=='__main__': unittest.main()
