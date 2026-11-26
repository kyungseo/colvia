"""Byte-preserving body descriptors and bounded streaming ingestion.

Staging is not submission. An application publishes the descriptor only with its
validated result and expected Work/workspace heads. Abandoned bytes are retained
until a separate repair proves their imports inactive and unreferenced.
"""
from __future__ import annotations
import hashlib
from typing import BinaryIO, Callable, Iterator, Protocol

from .codec import (CHUNK_LIMIT, Edge, ObjectRef, decode_envelope,
                    encode_envelope, object_ref, require, validate_schema, verify_object)

BODY_LIMIT = 256 * 1024 * 1024
SUBMISSION_LIMIT = 1024 * 1024 * 1024
BATCH_BYTES = 4 * 1024 * 1024
BATCH_COUNT = 64


class ChunkStager(Protocol):
    def stage(self, import_id: str, objects: list[tuple[ObjectRef,bytes]]) -> None: ...


def _chunks(stream: BinaryIO) -> Iterator[bytes]:
    buffer=bytearray()
    while True:
        wanted=CHUNK_LIMIT-len(buffer)
        raw=stream.read(wanted)
        require(type(raw) is bytes and len(raw)<=wanted,'invalid-body-stream')
        if not raw:
            if buffer: yield bytes(buffer)
            return
        buffer.extend(raw)
        if len(buffer)==CHUNK_LIMIT:
            yield bytes(buffer)
            buffer.clear()


def ingest_body(stream: BinaryIO, stager: ChunkStager, import_id: str,
                *, expected_size: int|None=None, expected_sha256: str|None=None) -> tuple[ObjectRef,bytes]:
    if expected_size is not None:
        require(type(expected_size) is int and 0<=expected_size<=BODY_LIMIT,'body-size-limit')
    refs=[]; batch=[]; batch_size=0; total=0; digest=hashlib.sha256()
    for raw in _chunks(stream):
        total+=len(raw); require(total<=BODY_LIMIT,'body-size-limit')
        digest.update(raw); ref=object_ref('body.chunk',1,raw)
        refs.append(ref)
        if batch and (batch_size+len(raw)>BATCH_BYTES or len(batch)>=BATCH_COUNT):
            stager.stage(import_id,batch); batch=[]; batch_size=0
        batch.append((ref,raw)); batch_size+=len(raw)
    actual=digest.hexdigest()
    require(expected_size is None or total==expected_size,'body-observation-changed')
    require(expected_sha256 is None or actual==expected_sha256,'body-observation-changed')
    if batch: stager.stage(import_id,batch)
    return encode_envelope('body.complete',1,
        dict(size=total,sha256=actual,links={'chunks':list(range(len(refs)))}),
        tuple(Edge('integrity',ref) for ref in refs))


def descriptor(ref: ObjectRef, raw: bytes):
    obj=decode_envelope(ref,raw)
    def check(p):
        require(set(p)=={'size','sha256','links'} and type(p['size']) is int and
                0<=p['size']<=BODY_LIMIT and type(p['sha256']) is str and len(p['sha256'])==64 and
                all(c in '0123456789abcdef' for c in p['sha256']) and
                p['links']['chunks']==list(range(len(obj.edges))),'invalid-body-descriptor')
    validate_schema(obj,kind='body.complete',version=1,fields={'chunks':'integrity'},validate_payload=check)
    length=obj.payload['size']
    count=(length+CHUNK_LIMIT-1)//CHUNK_LIMIT
    require(len(obj.edges)==count,'body-chunk-count')
    for index,edge in enumerate(obj.edges):
        require(edge.ref.kind=='body.chunk' and edge.ref.version==1 and
                edge.ref.byte_length==min(CHUNK_LIMIT,length-index*CHUNK_LIMIT),'body-chunk-shape')
    return obj


def body_bytes(ref: ObjectRef, load: Callable[[ObjectRef],bytes]) -> Iterator[bytes]:
    """Completion verifies the whole body; consumers must exhaust before claiming success."""
    obj=descriptor(ref,load(ref)); digest=hashlib.sha256(); total=0
    for edge in obj.edges:
        raw=load(edge.ref); verify_object(edge.ref,raw)
        total+=len(raw); digest.update(raw)
        yield raw
    require(total==obj.payload['size'] and digest.hexdigest()==obj.payload['sha256'],'body-identity-mismatch')


def validate_body(ref: ObjectRef, load: Callable[[ObjectRef],bytes]) -> None:
    verify_body = getattr(load, 'verify_body', None)
    if verify_body is not None and verify_body(ref) is True:
        return
    for _ in body_bytes(ref,load): pass


def submission_size(sizes: list[int]) -> int:
    total=0
    for size in sizes:
        require(type(size) is int and 0<=size<=BODY_LIMIT,'body-size-limit')
        total+=size
        require(total<=SUBMISSION_LIMIT,'submission-body-limit')
    return total
