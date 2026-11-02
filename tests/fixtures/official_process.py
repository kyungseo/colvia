"""Actual processes/locks/installed entry; transport is an explicit offline seam."""
from pathlib import Path
import io,json,os,runpy,sys,time
from unittest import mock
TARGET=Path(sys.argv[1]);FOLDER=Path(sys.argv[2]);MODE=sys.argv[3]
binding=json.loads((TARGET/'.hrn/product/binding.json').read_bytes())
payload=TARGET/'.hrn/product/releases'/binding['active_release']['id']/'payload'
sys.path.insert(0,str(payload/'src'))
from hv2ref import official_entry as entry, official_adapter as adapter, official_state as state
from hv2ref.workspace import writer_guard
from hv2ref.errors import ContractError

def signal(name,value):state.publish(FOLDER/(name+'.json'),value)

def offline(host):
    signal('ready',{'pid':os.getpid(),'grant':host.grant,'actual_model_calls':0,'transport':'offline-test-seam'})
    deadline=time.monotonic()+30
    while time.monotonic()<deadline and not host.cancelled():time.sleep(.01)
    state.need(host.cancelled(),'test-cancel-not-observed')
    host.revoke('cancelled')
    def envelope(call):return {'threadId':'offline-thread','turnId':'offline-turn','callId':call,
                               'tool':'u2_read_file','arguments':{'file_ids':['Editable','Reference']}}
    with mock.patch.object(host.controller,'dispatch',side_effect=RuntimeError('late worker forbidden')):
        answers=[host.dispatch(envelope('same')),host.dispatch(envelope('new'))]
    signal('late',{'all_refused_before_worker':all(not x['ok'] and not x['worker_admitted'] for x in answers),'origin':'host-injected offline callback'})
    return host.finish('interrupted')

if MODE=='host':
    p=state.load(FOLDER/'preview.json')
    sys.argv=[str(TARGET/'colvia'),'run','execute','--input',str(FOLDER/'spec.json'),'--confirm',p['confirm_token']]
    with mock.patch.object(entry,'runtime_input',return_value={}),mock.patch.object(adapter,'run',offline):
        runpy.run_path(str(TARGET/'colvia'),run_name='__main__')
elif MODE=='writer':
    signal('attempt',{'pid':os.getpid()})
    try:
        with writer_guard(TARGET):signal('acquired',{'pid':os.getpid()})
    except ContractError as exc:
        signal('refused',{'code':exc.code,'reason':exc.message});raise SystemExit(65)
else:raise ValueError('mode')
