"""Prepare the explicit macOS official payload; no install or execution."""
import argparse
from pathlib import Path
import shutil
import sys

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source',type=Path,default=Path(__file__).resolve().parents[1])
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args();source=args.source.absolute();output=args.output.absolute()
    if output.exists() or output.is_symlink() or output==source or source in output.parents:
        parser.error('output must be new and outside source')
    sys.path[:0]=[str(source/'distribution'),str(source/'src')]
    from source_layout import read_checkout, SOURCE_MAP
    from hv2ref.product import workspace_candidate,OFFICIAL_V2_MANAGED_PATHS
    from hv2ref.jsonio import canonical_json_bytes,sha256_bytes
    baseline=read_checkout(source)
    if baseline['release_ref']['inventory_id']!='continuation-1':parser.error('common source declaration required')
    official=read_checkout(source,OFFICIAL_V2_MANAGED_PATHS)
    data=dict(official['payload'])
    old=b'WORKSPACE_INVENTORY_ID = "continuation-1"'
    if data['colvia'].count(old)!=1:parser.error('declaration mismatch')
    data['colvia']=data['colvia'].replace(old,b'WORKSPACE_INVENTORY_ID = "official-execution-2"',1)
    output.mkdir(parents=True,mode=0o700)
    for name,raw in data.items():
        p=output/name;p.parent.mkdir(parents=True,exist_ok=True)
        with p.open('xb') as stream:stream.write(raw)
        p.chmod(official['source_modes'][name])
    observed=workspace_candidate(output)
    if observed['payload']!=data or read_checkout(source)!=baseline or read_checkout(source,OFFICIAL_V2_MANAGED_PATHS)!=official:raise RuntimeError('preparation drift')
    report={'preparation':'official-execution-2','input_release':baseline['release_ref'],'output_release':observed['release_ref'],'managed_paths':len(data),'activated':False,'source_paths':{n:SOURCE_MAP.get(n,n) for n in data}}
    (output/'preparation.json').write_bytes(canonical_json_bytes(report))
    print(canonical_json_bytes(report).decode(),end='')

if __name__=='__main__':main()
