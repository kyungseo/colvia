import hashlib
import io
from pathlib import Path
import tempfile
import threading
import time
import unittest
from unittest.mock import patch

from colvia.bodies import body_bytes, descriptor, ingest_body, submission_size, validate_body
from colvia.codec import CHUNK_LIMIT, RecordError, decode_envelope, encode_envelope
from colvia.storage.sqlite import GenerationStore


class MemoryStager:
    def __init__(self): self.objects={}; self.batches=[]
    def stage(self, import_id, objects):
        self.batches.append((len(objects),sum(len(raw) for _,raw in objects)))
        self.objects.update(objects)


class BodyTests(unittest.TestCase):
    def test_raw_encodings_empty_and_chunk_boundaries(self):
        for raw in (b'',b'\xef\xbb\xbfhi\r\n',b'\xff\x00',b'a'*CHUNK_LIMIT,b'b'*(CHUNK_LIMIT+1)):
            with self.subTest(length=len(raw)):
                stager=MemoryStager(); ref,data=ingest_body(io.BytesIO(raw),stager,'i')
                stager.objects[ref]=data
                self.assertEqual(raw,b''.join(body_bytes(ref,stager.objects.__getitem__)))
                self.assertEqual(len(raw),descriptor(ref,data).payload['size'])

    def test_short_stream_reads_do_not_truncate_body(self):
        class Short(io.BytesIO):
            def read(self,n=-1): return super().read(min(n,73))
        raw=b'z'*(CHUNK_LIMIT+101); stager=MemoryStager()
        ref,data=ingest_body(Short(raw),stager,'i'); stager.objects[ref]=data
        self.assertEqual(raw,b''.join(body_bytes(ref,stager.objects.__getitem__)))

    def test_batches_bound_writes_and_dedup_is_not_size_discount(self):
        stager=MemoryStager(); raw=b'x'*(9*CHUNK_LIMIT)
        ref,data=ingest_body(io.BytesIO(raw),stager,'i')
        self.assertEqual([(4,4*CHUNK_LIMIT),(4,4*CHUNK_LIMIT),(1,CHUNK_LIMIT)],stager.batches)
        self.assertEqual(1,len(stager.objects))
        self.assertEqual(9,len(descriptor(ref,data).edges))
        self.assertEqual(1024*1024*1024,submission_size([256*1024*1024]*4))
        with self.assertRaisesRegex(RecordError,'submission-body-limit'): submission_size([256*1024*1024]*4+[1])

    def test_changed_input_size_limit_and_corrupt_content_refuse(self):
        for kwargs in ({'expected_size':4},{'expected_sha256':'0'*64}):
            with self.assertRaisesRegex(RecordError,'body-observation-changed'):
                ingest_body(io.BytesIO(b'abc'),MemoryStager(),'i',**kwargs)
        with patch('colvia.bodies.BODY_LIMIT',3):
            ingest_body(io.BytesIO(b'abc'),MemoryStager(),'i')
            with self.assertRaisesRegex(RecordError,'body-size-limit'): ingest_body(io.BytesIO(b'abcd'),MemoryStager(),'i')
        stager=MemoryStager(); ref,data=ingest_body(io.BytesIO(b'abc'),stager,'i')
        obj=decode_envelope(ref,data); obj.payload['sha256']='0'*64
        bad,bad_data=encode_envelope('body.complete',1,obj.payload,obj.edges)
        stager.objects[bad]=bad_data
        with self.assertRaisesRegex(RecordError,'body-identity-mismatch'): validate_body(bad,stager.objects.__getitem__)

    def test_overlapping_readonly_thread_and_writer_are_coordinated(self):
        with tempfile.TemporaryDirectory(prefix='threaded-bodies-') as directory:
            path=Path(directory)/'state.sqlite3'
            options=dict(project='p',instance='i',generation='g',active_check=lambda:None)
            writer=GenerationStore.create(path,**options); writer.begin_import('i','owner')
            ready=threading.Event(); stop=threading.Event(); observed=[]; errors=[]
            def read():
                reader=None
                try:
                    reader=GenerationStore(path,readonly=True,**options);ready.set()
                    while not stop.is_set():
                        observed.append(reader.root().sequence);time.sleep(.001)
                except BaseException as exc: errors.append(exc);ready.set()
                finally:
                    if reader is not None: reader.close()
            peer=threading.Thread(target=read);peer.start()
            try:
                self.assertTrue(ready.wait(5))
                for i in range(12):
                    ingest_body(io.BytesIO(bytes([i])*(1024*1024)),writer,'i')
                self.assertFalse(errors); self.assertTrue(observed)
                self.assertEqual({0},set(observed))
            finally:
                stop.set();peer.join(5);writer.close()
            self.assertFalse(peer.is_alive());self.assertFalse(errors)

    def test_store_reader_can_read_between_staging_batches(self):
        with tempfile.TemporaryDirectory(prefix='bodies-') as directory:
            path=Path(directory)/'state.sqlite3'
            options=dict(project='p',instance='i',generation='g',active_check=lambda:None)
            store=GenerationStore.create(path,**options)
            reader=GenerationStore(path,readonly=True,**options)
            try:
                store.begin_import('import-1','owner')
                root=reader.root(); observed=[]
                class Interleave:
                    def stage(self,import_id,objects):
                        store.stage(import_id,objects); observed.append(reader.root())
                raw=b'z'*(5*CHUNK_LIMIT)
                ref,data=ingest_body(io.BytesIO(raw),Interleave(),'import-1')
                self.assertEqual([root,root],observed)
                self.assertIsNone(reader.head('body'))
                store.commit_heads(operation='publish-1',expected={'body':None},changes={'body':ref},
                    objects=[(ref,data)],import_id='import-1',validate=lambda load:validate_body(ref,load))
                self.assertEqual(raw,b''.join(body_bytes(ref,reader.load)))
                self.assertEqual(1,reader.root().sequence)
            finally: reader.close(); store.close()


if __name__=='__main__': unittest.main()
