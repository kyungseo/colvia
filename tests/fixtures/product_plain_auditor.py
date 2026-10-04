#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path


SERIAL_PATHS = ('.gitignore', 'AGENTS.md', 'CLAUDE.md', 'PRODUCT-CAPABILITIES.json', 'README.md', 'adapters/harness-v2-work/SKILL.md', 'docs/CONCEPTS.md', 'docs/GENERAL-WORK.md', 'docs/GETTING-STARTED.md', 'docs/GUIDED-INTENT-FORMATION.md', 'docs/MAINTAINING.md', 'docs/MANUAL-OPERATION.md', 'docs/OPERATIONS.md', 'docs/README.md', 'docs/REFERENCE.md', 'docs/SECURITY-AND-SUPPORT.md', 'docs/WORKSPACE-CONTRACT.md', 'hv2', 'src/hv2ref/__init__.py', 'src/hv2ref/cli.py', 'src/hv2ref/errors.py', 'src/hv2ref/intent.py', 'src/hv2ref/jsonio.py', 'src/hv2ref/product.py', 'src/hv2ref/view.py', 'src/hv2ref/work.py', 'src/hv2ref/workspace.py')


# Independent stdlib receipt/byte auditor. This intentionally does not import or
# duplicate the full Work/intent state-machine implementation.
import os
import re
import stat


def require(ok, message):
    if not ok: raise ValueError(message)


def raw_file(path):
    before=path.lstat()
    require(stat.S_ISREG(before.st_mode) and before.st_nlink==1,"unsafe-file")
    data=path.read_bytes();after=path.lstat()
    require((before.st_dev,before.st_ino,before.st_size,before.st_mtime_ns)==(after.st_dev,after.st_ino,after.st_size,after.st_mtime_ns),"unstable-file")
    return data


def canonical(value):
    return (json.dumps(value,ensure_ascii=False,allow_nan=False,sort_keys=True,indent=2)+"\n").encode()


def strict_json(data):
    def pairs(items):
        result={}
        for k,v in items:
            require(k not in result,"duplicate-json-key");result[k]=v
        return result
    value=json.loads(data,object_pairs_hook=pairs,parse_constant=lambda _:(_ for _ in ()).throw(ValueError("nonfinite-json")))
    require(data==canonical(value),"noncanonical-json")
    return value


def keys(value, expected):
    require(isinstance(value,dict) and set(value)==set(expected),"unknown-or-missing-fields")
    return value


def valid_id(value):return isinstance(value,str) and re.fullmatch(r"[a-zA-Z0-9][a-zA-Z0-9_-]{0,95}",value) is not None

def sha(value):return hashlib.sha256(value).hexdigest()

def valid_sha(value):return isinstance(value,str) and re.fullmatch(r"[0-9a-f]{64}",value) is not None


def ref(value):
    keys(value,{"id","sha256"});require(valid_id(value["id"]) and valid_sha(value["sha256"]),"invalid-ref")
    return value


def entries(value):
    require(isinstance(value,list),"inventory-list")
    result={};names=[]
    for e in value:
        keys(e,{"path","sha256","size_bytes"});name=e["path"]
        require(isinstance(name,str) and name and not name.startswith("/") and "\\" not in name and all(p not in ("", ".", "..") for p in name.split("/")),"inventory-path")
        require(valid_sha(e["sha256"]) and type(e["size_bytes"]) is int and e["size_bytes"]>=0,"inventory-digest-size")
        result[name]=e;names.append(name)
    require(names==sorted(set(names),key=lambda n:n.encode()) and len({n.casefold() for n in names})==len(names),"inventory-order-alias")
    return result


def safe_target(value):
    p=Path(os.path.abspath(value))
    for a in reversed((p,*p.parents)):require(stat.S_ISDIR(a.lstat().st_mode),"unsafe-target")
    return p


def scan(root,allowed_files,allowed_dirs):
    found={};dirs=set();todo=[root] if os.path.lexists(root) else []
    while todo:
        directory=todo.pop();require(stat.S_ISDIR(directory.lstat().st_mode),"unsafe-directory")
        name=directory.relative_to(root.parent.parent).as_posix()  # target/.hrn/<collection>
        require(name in allowed_dirs,"unknown-directory");dirs.add(name)
        for p in directory.iterdir():
            name=p.relative_to(root.parent.parent).as_posix()
            if name in allowed_dirs:
                require(stat.S_ISDIR(p.lstat().st_mode),"unsafe-directory");todo.append(p)
            else:
                require(name in allowed_files,"unknown-file");found[name]=raw_file(p)
    return found,dirs


def audit_once(target):
    home=target/".hrn";require(stat.S_ISDIR(home.lstat().st_mode),"unsafe-home")
    require(not any(p.name.casefold()==".hrn" and p.name!=".hrn" for p in target.iterdir()),"home-alias")
    require(set(p.name for p in home.iterdir())<={"format.json",".gitignore","detached.json","product","work","intents","planning","locks","staging"},"unknown-home-member")
    for name in ("locks","staging"):
        if os.path.lexists(home/name):require(stat.S_ISDIR((home/name).lstat().st_mode),"unsafe-ignored-directory")
    fmt_raw=raw_file(home/"format.json");fmt=strict_json(fmt_raw)
    keys(fmt,{"record_type","format_version","authority_home_id","created_at","lineage"})
    require(fmt["record_type"]=="workspace-format" and type(fmt["format_version"]) is int and fmt["format_version"]==1,"unsupported-format")
    require(valid_id(fmt["authority_home_id"]) and isinstance(fmt["created_at"],str) and fmt["created_at"].strip(),"format-identity")
    if fmt["lineage"] is not None:
        lineage=keys(fmt["lineage"],{"parent","reason"});parent=keys(lineage["parent"],{"authority_home_id","kind","id"})
        require(valid_id(parent["authority_home_id"]) and valid_id(parent["id"]) and parent["kind"] in ("intent","work") and isinstance(lineage["reason"],str) and lineage["reason"].strip(),"format-lineage")
    receipt_raw=raw_file(home/"detached.json");receipt=strict_json(receipt_raw)
    keys(receipt,{"record_type","schema_version","operation_id","plan","prior_binding_ref","result_binding_ref"})
    plan=keys(receipt["plan"],{"record_type","schema_version","operation_id","action","target_fingerprint","authority_home_id","expected_binding_ref","candidate_release","format_sha256","truth_refs","remove","preserve","created_at"})
    require(receipt["record_type"]=="lifecycle-receipt" and type(receipt["schema_version"]) is int and receipt["schema_version"] in (1, 2)
            and plan["record_type"]=="lifecycle-plan" and type(plan["schema_version"]) is int and plan["schema_version"]==receipt["schema_version"] and plan["action"]=="detach","detach-record-type")
    require(valid_id(plan["operation_id"]) and receipt["operation_id"]==plan["operation_id"] and isinstance(plan["created_at"],str) and plan["created_at"].strip(),"detach-operation")
    require(plan["authority_home_id"]==fmt["authority_home_id"] and plan["format_sha256"]==sha(fmt_raw) and valid_sha(plan["target_fingerprint"]),"detach-identity")
    require(receipt["prior_binding_ref"]==ref(plan["expected_binding_ref"]) and receipt["result_binding_ref"] is None and plan["candidate_release"] is None,"detach-binding")
    remove=entries(plan["remove"]);preserve=entries(plan["preserve"])
    expected={"hv2",".hrn/product/init-plan.json",".hrn/product/binding.json"};releases=set();receipt_ids=set()
    for name in set(remove)-expected:
        parts=name.split("/")
        if len(parts)==4 and parts[:3]==[".hrn","product","receipts"] and parts[3].endswith(".json"):
            require(valid_id(parts[3][:-5]),"receipt-id");receipt_ids.add(parts[3][:-5]);expected.add(name)
        else:
            require(len(parts)>=5 and parts[:3]==[".hrn","product","releases"] and re.fullmatch(r"product-release-[0-9a-f]{24}",parts[3]),"remove-path")
            releases.add(parts[3])
    require(bool(releases) and bool(receipt_ids) and plan["operation_id"].casefold() not in {n.casefold() for n in receipt_ids},"remove-release-receipt")
    for rid in releases:
        prefix=".hrn/product/releases/"+rid+"/"
        paths = set(SERIAL_PATHS) | {"src/hv2ref/umbrella.py"} if prefix+"payload/src/hv2ref/umbrella.py" in remove else SERIAL_PATHS
        if prefix+"payload/src/hv2ref/candidates.py" in remove:paths=set(paths)|{"src/hv2ref/candidates.py"}
        expected|={prefix+"inventory.json"}|{prefix+"payload/"+p for p in paths}
        require(prefix+"inventory.json" in remove and rid=="product-release-"+remove[prefix+"inventory.json"]["sha256"][:24],"release-inventory")
    require(set(remove)==expected and remove[".hrn/product/binding.json"]["sha256"]==plan["expected_binding_ref"]["sha256"],"remove-completeness")
    require(any((remove["hv2"]["sha256"], remove["hv2"]["size_bytes"]) ==
                (remove[".hrn/product/releases/"+rid+"/payload/hv2"]["sha256"],
                 remove[".hrn/product/releases/"+rid+"/payload/hv2"]["size_bytes"])
                for rid in releases),"launcher-not-bound-to-release")
    require(isinstance(plan["truth_refs"],list),"truth-list");truth={};truth_names=[]
    for t in plan["truth_refs"]:
        keys(t,{"path","sha256"});name=t["path"]
        require(isinstance(name,str) and (name=="planning/candidates.json" or (name.split("/")[0] in ("intents","work") and len(name.split("/"))>=3)) and valid_sha(t["sha256"]),"truth-path")
        truth[".hrn/"+name]=t["sha256"];truth_names.append(name)
    require(truth_names==sorted(set(truth_names),key=lambda n:n.encode()) and set(preserve)==set(truth)|{".hrn/format.json",".hrn/.gitignore"},"truth-preservation")
    saved={".hrn/format.json":fmt_raw,".hrn/.gitignore":raw_file(home/".gitignore")}
    require(saved[".hrn/.gitignore"]==b"staging/\nlocks/\n","ignore-bytes")
    for collection in ("intents","work","planning"):
        allowed={n for n in truth if n.startswith(".hrn/"+collection+"/")}
        dirs={".hrn/"+collection}|{p.as_posix() for n in allowed for p in Path(n).parents if p.as_posix().startswith(".hrn/"+collection)}
        files,_=scan(home/collection,allowed,dirs);require(set(files)==allowed,"missing-truth");saved.update(files)
    for name,data in saved.items():
        require(sha(data)==preserve[name]["sha256"] and len(data)==preserve[name]["size_bytes"],"changed-preserved-bytes")
        if name in truth:require(sha(data)==truth[name],"truth-ref-mismatch");strict_json(data)
    files_order=["hv2"]+[n for n in remove if n!="hv2"]
    dirs={p.as_posix() for n in files_order if n!="hv2" for p in Path(n).parents if p.as_posix().startswith(".hrn/product")}
    dir_order=sorted(dirs,key=lambda n:(-len(n.split("/")),n.encode()))
    remaining,present_dirs=scan(home/"product",set(remove),dirs)
    if os.path.lexists(target/"hv2"):remaining["hv2"]=raw_file(target/"hv2")
    for name,data in remaining.items():require(sha(data)==remove[name]["sha256"] and len(data)==remove[name]["size_bytes"],"changed-remaining-bytes")
    remaining_names=[n for n in files_order if n in remaining]
    require(remaining_names==files_order[len(files_order)-len(remaining_names):],"invalid-file-prefix")
    if remaining_names:require(present_dirs==dirs,"early-directory-removal")
    else:require([n for n in dir_order if n in present_dirs]==dir_order[len(dir_order)-len(present_dirs):],"invalid-directory-prefix")
    selected={}
    for name,data in saved.items():
        if not name.endswith("/current.json"):continue
        current=strict_json(data);selection_ref=ref(current["selection_ref"]);base=name.rsplit("/",1)[0]
        path=base+"/selections/"+selection_ref["id"]+".json"
        require(path in saved and sha(saved[path])==selection_ref["sha256"],"current-selection-ref")
        selection=strict_json(saved[path]);revision_ref=ref(selection["revision_ref"])
        collection="drafts" if base.startswith(".hrn/intents/") else "revisions"
        path=base+"/"+collection+"/"+revision_ref["id"]+".json"
        require(path in saved and sha(saved[path])==revision_ref["sha256"],"selected-revision-ref")
        selected[base]={"selection_ref":selection_ref,"revision_ref":revision_ref}
    return {"classification":"partial" if remaining_names or present_dirs else "detached", "authority_home_id":fmt["authority_home_id"],
            "receipt_sha256":sha(receipt_raw),"preserved_files":len(saved),"selected":selected,
            "remaining_files":remaining_names,"remaining_directories":[n for n in dir_order if n in present_dirs],
            "verification":"receipt-inventory-and-selected-refs", "full_record_semantics":"not-reimplemented", "mutation_authorized":False}


def main():
    try:
        if len(sys.argv)!=2:raise ValueError("usage: product_plain_auditor.py TARGET")
        target=safe_target(sys.argv[1])
        require(os.path.lexists(target/".hrn"),"missing .hrn; legacy layouts unsupported")
        result=audit_once(target);require(result==audit_once(target),"unstable-detached-state")
        print(json.dumps(result,ensure_ascii=False,sort_keys=True))
        return 14 if result["classification"]=="partial" else 0
    except (ValueError,OSError,KeyError,TypeError,RecursionError) as exc:
        print(json.dumps({"classification":"degraded","message":str(exc),"mutation_authorized":False},sort_keys=True))
        return 10


if __name__ == "__main__":
    raise SystemExit(main())
