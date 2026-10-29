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
    sys.path.insert(0,str(source/'src'))
    from hv2ref.product import workspace_candidate,OFFICIAL_MANAGED_PATHS
    from hv2ref.jsonio import canonical_json_bytes,sha256_bytes
    baseline=workspace_candidate(source)
    if baseline['release_ref']['inventory_id']!='continuation-1':parser.error('common source declaration required')
    data={}
    for name in OFFICIAL_MANAGED_PATHS:
        p=source/name
        if p.resolve(strict=True)!=p or not p.is_file() or p.stat().st_nlink!=1:parser.error('unsafe source member')
        data[name]=p.read_bytes()
    old=b'WORKSPACE_INVENTORY_ID = "continuation-1"'
    if data['colvia'].count(old)!=1:parser.error('declaration mismatch')
    data['colvia']=data['colvia'].replace(old,b'WORKSPACE_INVENTORY_ID = "official-execution-1"',1)
    output.mkdir(parents=True,mode=0o700)
    for name,raw in data.items():
        p=output/name;p.parent.mkdir(parents=True,exist_ok=True)
        with p.open('xb') as stream:stream.write(raw)
        shutil.copymode(source/name,p)
    observed=workspace_candidate(output)
    if observed['payload']!=data or workspace_candidate(source)!=baseline:raise RuntimeError('preparation drift')
    report={'preparation':'official-execution-1','input_release':baseline['release_ref'],'output_release':observed['release_ref'],'managed_paths':len(data),'activated':False}
    (output/'preparation.json').write_bytes(canonical_json_bytes(report))
    print(canonical_json_bytes(report).decode(),end='')

if __name__=='__main__':main()
