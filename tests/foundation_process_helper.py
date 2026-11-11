"""Synthetic subprocess peer; no model, install or external project interaction."""
from pathlib import Path
import json
import sys
import time

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from colvia.codec import RecordError, decode_envelope, encode_envelope
from colvia.storage.authority import Authority
from colvia.storage.sqlite import runtime_capabilities
TEST_CAPS=runtime_capabilities()|{'schema:test.value:1'}

root,mode,name,key = Path(sys.argv[1]),*sys.argv[2:5]
authority=Authority(root/'authority',project='p',reader_capabilities=TEST_CAPS,writer_capabilities=TEST_CAPS)
store=authority.store()
try:
    before=store.root().ref
    (root/(name+'.ready')).write_text('ready')
    deadline=time.monotonic()+15
    while not (root/'go').exists():
        if time.monotonic()>deadline: raise RuntimeError('test barrier timeout')
        time.sleep(.01)
    if mode=='cas':
        ref,raw=encode_envelope('test.value',1,dict(links={},label=name))
        store.commit_heads(operation=name,expected={key:None},changes={key:ref},objects=[(ref,raw)],
                           validate=lambda load:decode_envelope(ref,load(ref)))
        result={'status':'committed','root':store.root().ref.as_dict()}
    elif mode=='hold':
        store.root(); result={'status':'unexpected-old-read'}
    else: raise RuntimeError('invalid test mode')
except RecordError as exc:
    result={'status':'refused','code':exc.code}
finally: store.close()
print(json.dumps(result))
