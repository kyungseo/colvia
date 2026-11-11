"""Executed process/SQLite failures, isolated from installed authorities."""
import hashlib
from pathlib import Path
import os
import sqlite3
import subprocess
import sys
import tempfile
import time
import unittest
from unittest.mock import patch

from colvia.codec import RecordError, object_ref
from colvia.storage.sqlite import GenerationStore


class StoreFaultTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(prefix='fault-')
        self.path=Path(self.tmp.name)/'state.sqlite3'
        self.options=dict(project='p',instance='i',generation='g',active_check=lambda:None)
        self.store=GenerationStore.create(self.path,**self.options)
    def tearDown(self):
        if self.store is not None: self.store.close()
        self.tmp.cleanup()

    def test_disk_full_does_not_publish_or_corrupt_current_root(self):
        before=self.store.root()
        pages=self.store.db.execute('PRAGMA page_count').fetchone()[0]
        self.store.db.execute(f'PRAGMA max_page_count={pages+1}')
        self.store.begin_import('full','owner')
        raw=b'x'*(1024*1024);ref=object_ref('body.chunk',1,raw)
        with self.assertRaisesRegex(RecordError,'store-full'): self.store.stage('full',[(ref,raw)])
        self.assertEqual(before,self.store.root())
        self.assertEqual('ok',self.store.db.execute('PRAGMA integrity_check').fetchone()[0])
        self.assertEqual(0,self.store.db.execute('SELECT count(*) FROM claims').fetchone()[0])

    def test_busy_acquisition_is_bounded_and_not_implicitly_retried(self):
        second=GenerationStore(self.path,**self.options)
        try:
            second.db.execute('PRAGMA busy_timeout=30')
            self.store.db.execute('BEGIN IMMEDIATE')
            start=time.monotonic()
            with patch('colvia.storage.sqlite.BUSY_SECONDS',.03), self.assertRaisesRegex(RecordError,'store-busy'):
                second.begin_import('blocked','owner')
            self.assertLess(time.monotonic()-start,1)
            self.store.db.execute('ROLLBACK')
            self.assertIsNone(second.db.execute("SELECT id FROM imports WHERE id='blocked'").fetchone())
        finally: second.close()

    @unittest.skipUnless(os.name=='posix','POSIX subprocess signal fixture')
    def test_killed_writer_hot_journal_is_recovery_required_not_corrupt(self):
        before=self.store.root()
        self.store.db.execute('BEGIN IMMEDIATE')
        self.store.db.executemany('INSERT INTO imports VALUES(?,?,?)',
                                 [(f'i-{n}','a'*128,'active') for n in range(1000)])
        self.store.db.execute('COMMIT')
        self.store.close();self.store=None
        code="""import sqlite3,sys,time
c=sqlite3.connect(sys.argv[1],isolation_level=None)
c.execute('PRAGMA cache_size=2');c.execute('PRAGMA cache_spill=2');c.execute('PRAGMA synchronous=EXTRA')
if c.execute('PRAGMA cache_spill').fetchone()[0]!=2: raise RuntimeError('spill threshold not applied')
c.execute('BEGIN IMMEDIATE')
c.execute("UPDATE imports SET owner=?",('b'*128,))
c.execute('INSERT INTO objects VALUES(?,?,?,?,?,0)',('f'*64,'body.chunk',1,1048576,b'x'*1048576))
print('uncommitted-ready',flush=True)
time.sleep(30)
"""
        child=subprocess.Popen([sys.executable,'-I','-B','-c',code,str(self.path)],stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
        try:
            import select
            ready,_,_=select.select([child.stdout],[],[],5)
            self.assertTrue(ready,'writer readiness timeout')
            self.assertEqual('uncommitted-ready',child.stdout.readline().strip())
            child.kill();child.wait(timeout=5)
            journal=Path(str(self.path)+'-journal')
            self.assertTrue(journal.exists());self.assertGreater(journal.stat().st_size,512)
            self.assertEqual(bytes.fromhex('d9d505f920a163d7'),journal.read_bytes()[:8])
            with self.assertRaisesRegex(RecordError,'recovery-required'):
                GenerationStore(self.path,readonly=True,**self.options)
            recovered=GenerationStore(self.path,**self.options)
            try:
                self.assertEqual(before,recovered.root())
                self.assertIsNone(recovered.db.execute("SELECT 1 FROM objects WHERE digest=?",('f'*64,)).fetchone())
                self.assertEqual('ok',recovered.db.execute('PRAGMA integrity_check').fetchone()[0])
            finally: recovered.close()
        finally:
            if child.poll() is None: child.kill();child.wait(timeout=5)
            child.stdout.close();child.stderr.close()


if __name__=='__main__': unittest.main()
