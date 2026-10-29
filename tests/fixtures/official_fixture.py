"""Synthetic fixture only: publish one actual active local Work via installed CLI."""
from pathlib import Path
import json,sys
sys.path.insert(0,str(Path(__file__).parent))
import delegation_process as f

def seed(target):
    binding=json.loads((target/'.hrn/product/binding.json').read_bytes())
    payload=target/'.hrn/product/releases'/binding['active_release']['id']/'payload'
    sys.path.insert(0,str(payload/'src'))
    from hv2ref.product import verify_workspace_product
    from hv2ref.work import snapshot,make_manifest
    runtime=verify_workspace_product(target)
    home=json.loads((target/'.hrn/format.json').read_bytes())['authority_home_id']
    wid='official-work';iid='official-intent'
    intent=f.select_draft(target,f.fixture_draft(target,iid,wid,grant=False))
    tree=snapshot(target,verified_launcher_sha256=runtime['launcher_sha256'],verified_inventory_id=runtime['inventory']['inventory_id'])
    manifest=make_manifest(tree,tree,scope=['a','b'])
    identity={'record_type':'work-identity','schema_version':1,'authority_home_id':home,'work_id':wid,'work_type':'change','created_at':f.TIME,'acceptance_authority':'owner','lineage':None}
    revision={'record_type':'work-revision','schema_version':1,'authority_home_id':home,'work_id':wid,'record_id':'local-1','observed_at':f.TIME,'observed_scope':[],'unavailable_scope':[],'author':'agent','operation':'start','expected_prior_selection':None,'intent_ref':intent,'scope':['a','b'],'document_refs':[],'evidence_refs':[],'result_refs':{'manifest':{'id':f.digest(manifest),'sha256':f.digest(manifest)}},'progress':'active','next_action':'synthetic official edit','relations':[],'rebind_from':None,'execution_context':{'mode':'local','attempt_id':'local-1'}}
    return f.InstalledWork(target).publish(identity,revision,manifest,selection_id='local-1',operation_id='local-1')

if __name__=='__main__':
    print(json.dumps(seed(Path(sys.argv[1]).resolve())))
