"""Approved document views and composed-output guards, without filesystem IO.

Only returned views may be sent to a runtime. Full retained source bytes remain
local, including context outside an approved replacement range.
"""
import hashlib
from ..codec import require
from . import schema
from .guards import checked_payload,checked_preserved_output


def original(entry,raw):
    require(type(raw) is bytes,'execution-document-bytes')
    expected=entry['original_identity']
    require(len(raw)==expected['size'] and hashlib.sha256(raw).hexdigest()==expected['sha256'],'execution-document-drift')
    raw.decode('utf-8');return raw


def view(entry,raw):
    original(entry,raw)
    if entry['view']['kind']=='full':return raw
    begin,end=entry['view']['ranges'][0]
    # Decoding every segment also rejects a split UTF-8 codepoint.
    for part in (raw[:begin],raw[begin:end],raw[end:]):part.decode('utf-8')
    return raw[begin:end]


def prepare_views(contract,raw_documents,prompt,*,deadline):
    schema.grant_record(contract);scope=contract['scope']
    require(type(raw_documents) is dict and set(raw_documents)==set(scope['documents']),'execution-document-set')
    checked_payload(prompt,deadline=deadline);items=[]
    for name in scope['read_ids']:
        entry=scope['documents'][name];raw=raw_documents[name];visible=view(entry,raw)
        if name==scope['output_id']:checked_preserved_output(entry,raw,deadline=deadline)
        item=dict(file_id=name,sha256=hashlib.sha256(visible).hexdigest(),content=visible.decode('utf-8'),
            file_sha256=entry['original_identity']['sha256'],state='present',view=entry['view'])
        checked_payload(item,deadline=deadline);items.append(item)
    # A bounded tool reply must fit as a whole, not only entry-by-entry.
    checked_payload({'files':items},limit=64000,deadline=deadline)
    return items


def compose_output(contract,prior,content,*,deadline):
    schema.grant_record(contract);scope=contract['scope'];entry=scope['documents'][scope['output_id']]
    view(entry,prior);checked_payload(content,deadline=deadline)
    require(type(content) is str,'content_rejected');begin,end=entry['view']['ranges'][0]
    result=prior[:begin]+content.encode('utf-8')+prior[end:]
    require(len(result)<=131072,'content_rejected')
    checked_payload(result.decode('utf-8'),limit=262144,deadline=deadline)
    return result
