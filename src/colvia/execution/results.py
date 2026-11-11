"""Fixed worker result validation; observations come from the native host port.

A JSON success flag alone never proves a write or a completed execution. These
functions do not publish records, accept Work or establish process closure.
"""
import copy,hashlib
from ..codec import require
from . import schema
from .documents import prepare_views,compose_output
from .guards import checked_payload,wire_bytes

def read_result(contract,request,raw_documents,result,*,deadline):
    expected=prepare_views(contract,raw_documents,request['prompt'],deadline=deadline)
    require(type(result) is dict and set(result)=={'files'} and result['files']==expected,'execution-read-result-binding')
    reply=copy.deepcopy(result)
    for item in reply['files']:
        item['origin']=dict(kind='approved-document',source_sha256=contract['scope']['documents'][item['file_id']]['original_identity']['sha256'],
            approval=contract['grant'])
    checked_payload(reply,limit=64000,deadline=deadline);return reply

def write_result(contract,prior,content,result,*,after,raw,saved,saved_raw,swap_present,deadline):
    scope=contract['scope'];output=scope['output_id'];entry=scope['documents'][output];before=entry['original_identity']
    schema.identity(after);schema.identity(saved)
    require(type(result) is dict and set(result)=={'file_id','sha256','identity','bytes','mode'} and
        result['file_id']==output and type(result['bytes']) is int and type(result['mode']) is int and
        type(result['identity']) is list and len(result['identity'])==2 and all(type(n) is int for n in result['identity']),
        'execution-write-result-shape')
    wanted=compose_output(contract,prior,content,deadline=deadline)
    require(type(raw) is bytes and raw==wanted and len(raw)==after['size'] and hashlib.sha256(raw).hexdigest()==after['sha256'] and
        after['mode']==before['mode'] and after['nlink']==1 and result['mode']==after['mode'] and
        result['bytes']==len(raw) and result['sha256']==after['sha256'] and result['identity']==[after['dev'],after['ino']] and
        type(swap_present) is bool and not swap_present,'execution-write-postcondition')
    require(type(saved_raw) is bytes and saved_raw==prior and all(saved[k]==before[k]
        for k in ('dev','ino','mode','nlink','size','mtime_ns','sha256')),'execution-saved-original-changed')
    require((after['dev'],after['ino'])!=(before['dev'],before['ino']),'execution-output-not-replaced')
    begin,_=entry['view']['ranges'][0]
    updated=dict(path=entry['path'],identity=[after['dev'],after['ino']],mode=after['mode'],sha256=after['sha256'],
        view=dict(kind='replace-range',ranges=[[begin,begin+len(content.encode('utf-8'))]]))
    reply=dict(file_id=output,sha256=after['sha256'],bytes=len(raw))
    checked_payload(reply,limit=64000,deadline=deadline);return reply,updated

def verifier_result(contract,request,files,verifier,result,*,deadline):
    schema.choice(verifier,schema.VERIFIERS)
    oracle=dict(outputs=[contract['scope']['output_id']],claims=request['claims'],
        approved_external_links=request['approved_external_links'],parser_sha256=contract['scope']['resources']['parser_digest'])
    require(type(result) is dict and set(result)=={'verifier_id','inputs','pass','findings','oracle_sha256','boundary'} and
        result['verifier_id']==verifier and result['inputs']=={name:item['sha256'] for name,item in files.items()} and
        type(result['pass']) is bool and type(result['findings']) is list and
        result['oracle_sha256']==hashlib.sha256(wire_bytes(oracle)).hexdigest() and
        result['boundary']=='fixed static checks; human factual review remains required','execution-verifier-result-binding')
    require(result['pass']==(not result['findings']),'execution-verifier-findings-mismatch')
    checked_payload(result,limit=64000,deadline=deadline);return copy.deepcopy(result)
