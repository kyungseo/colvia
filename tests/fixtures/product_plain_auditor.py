#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path


SERIAL_PATHS = ('.gitignore', 'AGENTS.md', 'CLAUDE.md', 'PRODUCT-CAPABILITIES.json', 'README.md', 'adapters/harness-v2-work/SKILL.md', 'docs/CONCEPTS.md', 'docs/GENERAL-WORK.md', 'docs/GETTING-STARTED.md', 'docs/GUIDED-INTENT-FORMATION.md', 'docs/MAINTAINING.md', 'docs/MANUAL-OPERATION.md', 'docs/OPERATIONS.md', 'docs/README.md', 'docs/REFERENCE.md', 'docs/SECURITY-AND-SUPPORT.md', 'docs/WORKSPACE-CONTRACT.md', 'hv2', 'src/hv2ref/__init__.py', 'src/hv2ref/cli.py', 'src/hv2ref/errors.py', 'src/hv2ref/intent.py', 'src/hv2ref/jsonio.py', 'src/hv2ref/product.py', 'src/hv2ref/view.py', 'src/hv2ref/work.py', 'src/hv2ref/workspace.py')
ENTRY_PATHS = ('.gitignore', 'AGENTS.md', 'CLAUDE.md', 'PRODUCT-CAPABILITIES.json', 'README.md', 'adapters/colvia-work/SKILL.md', 'colvia', 'docs/CONCEPTS.md', 'docs/GENERAL-WORK.md', 'docs/GETTING-STARTED.md', 'docs/GUIDED-INTENT-FORMATION.md', 'docs/MAINTAINING.md', 'docs/MANUAL-OPERATION.md', 'docs/OPERATIONS.md', 'docs/README.md', 'docs/REFERENCE.md', 'docs/SECURITY-AND-SUPPORT.md', 'docs/WORKSPACE-CONTRACT.md', 'src/hv2ref/__init__.py', 'src/hv2ref/candidates.py', 'src/hv2ref/cli.py', 'src/hv2ref/errors.py', 'src/hv2ref/intent.py', 'src/hv2ref/jsonio.py', 'src/hv2ref/product.py', 'src/hv2ref/umbrella.py', 'src/hv2ref/view.py', 'src/hv2ref/work.py', 'src/hv2ref/workspace.py')
DELEGATION_PATHS = ('.gitignore', 'AGENTS.md', 'CLAUDE.md', 'PRODUCT-CAPABILITIES.json', 'README.md', 'adapters/colvia-work/SKILL.md', 'colvia', 'docs/CONCEPTS.md', 'docs/GENERAL-WORK.md', 'docs/GETTING-STARTED.md', 'docs/GUIDED-INTENT-FORMATION.md', 'docs/MAINTAINING.md', 'docs/MANUAL-OPERATION.md', 'docs/OPERATIONS.md', 'docs/README.md', 'docs/REFERENCE.md', 'docs/SECURITY-AND-SUPPORT.md', 'docs/WORKSPACE-CONTRACT.md', 'src/hv2ref/__init__.py', 'src/hv2ref/candidates.py', 'src/hv2ref/cli.py', 'src/hv2ref/errors.py', 'src/hv2ref/intent.py', 'src/hv2ref/jsonio.py', 'src/hv2ref/product.py', 'src/hv2ref/umbrella.py', 'src/hv2ref/view.py', 'src/hv2ref/work.py', 'src/hv2ref/workspace.py')
CONTINUATION_PATHS = ('.gitignore', 'AGENTS.md', 'CLAUDE.md', 'PRODUCT-CAPABILITIES.json', 'README.md', 'adapters/colvia-work/SKILL.md', 'colvia', 'docs/CONCEPTS.md', 'docs/GENERAL-WORK.md', 'docs/GETTING-STARTED.md', 'docs/GUIDED-INTENT-FORMATION.md', 'docs/MAINTAINING.md', 'docs/MANUAL-OPERATION.md', 'docs/OPERATIONS.md', 'docs/README.md', 'docs/REFERENCE.md', 'docs/SECURITY-AND-SUPPORT.md', 'docs/WORKSPACE-CONTRACT.md', 'src/hv2ref/__init__.py', 'src/hv2ref/candidates.py', 'src/hv2ref/cli.py', 'src/hv2ref/continuation.py', 'src/hv2ref/errors.py', 'src/hv2ref/intent.py', 'src/hv2ref/jsonio.py', 'src/hv2ref/product.py', 'src/hv2ref/umbrella.py', 'src/hv2ref/view.py', 'src/hv2ref/work.py', 'src/hv2ref/workspace.py')

OFFICIAL_PATHS = tuple(sorted(CONTINUATION_PATHS + ('docs/OFFICIAL-EXECUTION.md', 'src/hv2ref/official_adapter.py', 'src/hv2ref/official_admission.py', 'src/hv2ref/official_documents.py', 'src/hv2ref/official_entry.py', 'src/hv2ref/official_host.py', 'src/hv2ref/official_os.py', 'src/hv2ref/official_policy.py', 'src/hv2ref/official_state.py', 'src/hv2ref/official_worker.py', 'runtime/official/marked-LICENSE.md', 'runtime/official/marked.umd.js', 'runtime/official/official-codex-macos.sb', 'runtime/official/worker.sb.in')))

# Independent stdlib receipt/byte auditor. This intentionally does not import or
# duplicate the full Work/intent state-machine implementation.
import os
import re
import stat


def require(ok, message):
    if not ok: raise ValueError(message)



def safe_present(path):
    """Missing means a missing component below already checked real directories."""
    parts=list(reversed((path,*path.parents)))
    for index,member in enumerate(parts):
        try: observed=member.lstat()
        except FileNotFoundError:return False
        require(not getattr(observed,"st_file_attributes",0)&0x400,"reparse-member")
        if index < len(parts)-1:require(stat.S_ISDIR(observed.st_mode),"unsafe-ancestor")
    return True


def safe_directory(path):
    require(safe_present(path) and stat.S_ISDIR(path.lstat().st_mode),"unsafe-directory")


def remaining_window(version,remove,remaining):
    if version not in (6,7):
        # Independent literal detection; do not add new validation to old pairs.
        import ast
        for name, data in remaining.items():
            seen = []
            if name.endswith("/inventory.json") or name == ".hrn/product/binding.json":
                try: value = strict_json(data)
                except (ValueError, TypeError, UnicodeError, RecursionError): continue
                if isinstance(value, dict):
                    seen.append(value.get("inventory_id"))
                    for field in ("active_release", "prior_release"):
                        ref = value.get(field)
                        if isinstance(ref, dict): seen.append(ref.get("inventory_id"))
            elif name == "colvia" or name.endswith("/payload/colvia"):
                if len(data) > 1024 * 1024: continue
                try: tree = ast.parse(data)
                except (SyntaxError, ValueError, UnicodeError, RecursionError, MemoryError): continue
                for node in tree.body:
                    if isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id == "WORKSPACE_INVENTORY_ID" for t in node.targets):
                        if isinstance(node.value, ast.Constant): seen.append(node.value.value)
            require(not any(isinstance(w, str) and w in ("windows-1", "windows-2", "official-execution-1") for w in seen), "legacy-pair-versus-Windows-witness")
        return
    expected_window="official-execution-1" if version==7 else "windows-2"
    allowed={"continuation-1","official-execution-1"} if version==7 else {"windows-2"}
    def admitted(window):return isinstance(window,str) and window in allowed
    for name,data in remaining.items():
        if name.endswith("/inventory.json"):
            inv=keys(strict_json(data),{"record_type","schema_version","inventory_id","entries"})
            require(inv["record_type"]=="release-inventory" and type(inv["schema_version"]) is int and inv["schema_version"]==1,"remaining-inventory-schema")
            window=inv["inventory_id"];require(admitted(window),"pair-versus-remaining-inventory")
            actual=entries(inv["entries"])
            expected=set(OFFICIAL_PATHS) if window=="official-execution-1" else set(CONTINUATION_PATHS) if window in ("continuation-1","windows-2") else set(DELEGATION_PATHS) if window=="delegation-1" else set(ENTRY_PATHS) if window=="entry-1" else set(SERIAL_PATHS)
            if window in ("umbrella-1","planning-1","checkout-1"):expected.add("src/hv2ref/umbrella.py")
            if window in ("planning-1","checkout-1"):expected.add("src/hv2ref/candidates.py")
            require(set(actual)==expected,"remaining-inventory-membership")
            prefix=name[:-len("inventory.json")]+"payload/"
            for item in actual.values():
                full=prefix+item["path"]
                require(remove.get(full)==dict(item,path=full),"remaining-inventory-remove-link")
        elif name=="colvia" or name.endswith("/payload/colvia"):
            import ast
            require(len(data)<=1024*1024,"launcher-limit")
            tree=ast.parse(data);declarations=[];stores=[]
            for node in tree.body:
                if isinstance(node,ast.Assign) and len(node.targets)==1 and isinstance(node.targets[0],ast.Name) and node.targets[0].id=="WORKSPACE_INVENTORY_ID":
                    declarations.append(node)
            for node in ast.walk(tree):
                if isinstance(node,ast.Name) and node.id=="WORKSPACE_INVENTORY_ID" and isinstance(node.ctx,(ast.Store,ast.Del)):stores.append(node)
            require(len(declarations)==1 and stores==[declarations[0].targets[0]] and isinstance(declarations[0].value,ast.Constant)
                    and (declarations[0].value.value==expected_window if name=="colvia" else admitted(declarations[0].value.value)),"pair-versus-remaining-launcher")
    if ".hrn/product/binding.json" in remaining:
        b=keys(strict_json(remaining[".hrn/product/binding.json"]),{"record_type","schema_version","authority_home_id","operation_id","active_release","prior_release"})
        require(b["record_type"]=="product-binding" and type(b["schema_version"]) is int and b["schema_version"]==1,"remaining-binding-schema")
        for field in ("active_release","prior_release"):
            value=b[field]
            if field=="prior_release" and value is None:continue
            value=keys(value,{"id","sha256","inventory_id"})
            require(admitted(value["inventory_id"]) and valid_sha(value["sha256"]) and value["id"]=="product-release-"+value["sha256"][:24],"pair-versus-remaining-binding")
            item=remove.get(".hrn/product/releases/"+value["id"]+"/inventory.json")
            require(item is not None and item["sha256"]==value["sha256"],"remaining-binding-inventory-link")
        require(b["active_release"]["inventory_id"]==expected_window,"active-window-pair")


def raw_file(path):
    require(safe_present(path),"missing-file")
    before=path.lstat()
    require(stat.S_ISREG(before.st_mode) and before.st_nlink==1,"unsafe-file")
    data=path.read_bytes();after=path.lstat()
    require((before.st_dev,before.st_ino,before.st_size,before.st_mtime_ns,before.st_ctime_ns,getattr(before,"st_file_attributes",0))==(after.st_dev,after.st_ino,after.st_size,after.st_mtime_ns,after.st_ctime_ns,getattr(after,"st_file_attributes",0)),"unstable-file")
    return data


def canonical(value):
    return (json.dumps(value,ensure_ascii=False,allow_nan=False,sort_keys=True,indent=2)+"\n").encode()


def strict_json(data):
    def pairs(items):
        result={}
        for k,v in items:
            require(k not in result,"duplicate-json-key");result[k]=v
        return result
    require(len(data)<=4*1024*1024,"json-byte-limit")
    def integer(value):
        require(len(value.lstrip("-"))<=1024,"json-integer-limit");return int(value)
    value=json.loads(data,parse_int=integer,object_pairs_hook=pairs,parse_constant=lambda _:(_ for _ in ()).throw(ValueError("nonfinite-json")))
    pending=[(value,1)]
    while pending:
        child,depth=pending.pop();require(depth<=128,"json-depth-limit")
        if isinstance(child,dict):pending.extend((v,depth+1) for v in child.values())
        elif isinstance(child,list):pending.extend((v,depth+1) for v in child)
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
    for a in reversed((p,*p.parents)):safe_directory(a)
    return p


def scan(root,allowed_files,allowed_dirs):
    found={};dirs=set();todo=[root] if safe_present(root) else []
    while todo:
        directory=todo.pop();safe_directory(directory)
        name=directory.relative_to(root.parent.parent).as_posix()  # target/.hrn/<collection>
        require(name in allowed_dirs,"unknown-directory");dirs.add(name)
        for p in directory.iterdir():
            name=p.relative_to(root.parent.parent).as_posix()
            if name in allowed_dirs:
                safe_directory(p);todo.append(p)
            else:
                require(name in allowed_files,"unknown-file");found[name]=raw_file(p)
    return found,dirs



def continuation_refs(saved,base,current):
    """Only selected references and effective choice; not full CONT semantics."""
    def resolve(directory,value):
        ref(value);name=directory+"/"+value["id"]+".json"
        require(name in saved and sha(saved[name])==value["sha256"],"continuation-selected-ref")
        return strict_json(saved[name])
    def work_snapshot(value):
        obj=keys(value["object"],{"authority_home_id","kind","id"})
        require(obj["kind"]=="work" and obj["authority_home_id"]==current["authority_home_id"],"continuation-snapshot-home")
        home=".hrn/work/"+obj["id"]
        selected=resolve(home+"/selections",value["selection_ref"])
        revision=resolve(home+"/revisions",value["revision_ref"])
        require(selected["revision_ref"]==value["revision_ref"] and revision["intent_ref"]==value["intent_ref"],"continuation-snapshot-ref")
    seen=set();ref_value=current["selection_ref"];effective=None;resolved=False
    while ref_value is not None:
        require(ref_value["id"] not in seen and len(seen)<512,"continuation-cycle-or-limit");seen.add(ref_value["id"])
        selection=resolve(base+"/selections",ref_value)
        keys(selection,{"record_type","schema_version","authority_home_id","work_id","record_id","parent_selection_ref","choice_ref"})
        choice=resolve(base+"/choices",selection["choice_ref"])
        keys(choice,{"record_type","schema_version","authority_home_id","work_id","record_id","confirmation"})
        for value,kind in ((selection,"continuation-selection"),(choice,"continuation-choice")):
            require(value["record_type"]==kind and type(value["schema_version"]) is int and value["schema_version"]==1
                    and value["authority_home_id"]==current["authority_home_id"] and value["work_id"]==current["work_id"],"continuation-record-identity")
        ticket=choice["confirmation"]
        require(selection["parent_selection_ref"]==ticket["expected_continuation_selection_ref"],"continuation-prior")
        work_snapshot(ticket["source"])
        action=ticket["action"];require(action in ("select","withdraw","cancel-pending"),"continuation-action")
        if action=="select" and ticket["choice"]["kind"]=="work":work_snapshot(ticket["choice"]["target"])
        if not resolved and action!="cancel-pending":
            effective=ticket["choice"] if action=="select" else None;resolved=True
        ref_value=selection["parent_selection_ref"]
    if current["selection_ref"] is None:
        require(not any(name.startswith((base+"/choices/",base+"/selections/")) for name in saved),"unselected-continuation-records")
    return {"selection_ref":current["selection_ref"],"effective_choice":effective,"verification":"selected-refs-only"}


def audit_once(target):
    home=target/".hrn";safe_directory(home)
    require(not any(p.name.casefold()==".hrn" and p.name!=".hrn" for p in target.iterdir()),"home-alias")
    require(set(p.name for p in home.iterdir())<={"format.json",".gitignore","detached.json","product","work","intents","planning","locks","staging","executions"},"unknown-home-member")
    for name in ("locks","staging"):
        if safe_present(home/name):safe_directory(home/name)
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
    require(receipt["record_type"]=="lifecycle-receipt" and type(receipt["schema_version"]) is int and receipt["schema_version"] in (1, 2, 3, 4, 5, 6, 7)
            and plan["record_type"]=="lifecycle-plan" and type(plan["schema_version"]) is int and plan["schema_version"]==receipt["schema_version"] and plan["action"]=="detach","detach-record-type")
    require(valid_id(plan["operation_id"]) and receipt["operation_id"]==plan["operation_id"] and isinstance(plan["created_at"],str) and plan["created_at"].strip(),"detach-operation")
    require(plan["authority_home_id"]==fmt["authority_home_id"] and plan["format_sha256"]==sha(fmt_raw) and valid_sha(plan["target_fingerprint"]),"detach-identity")
    require(receipt["prior_binding_ref"]==ref(plan["expected_binding_ref"]) and receipt["result_binding_ref"] is None and plan["candidate_release"] is None,"detach-binding")
    remove=entries(plan["remove"]);preserve=entries(plan["preserve"])
    launcher={1:"hv2",2:"hv2",3:"colvia",4:"colvia",5:"colvia",6:"colvia",7:"colvia"}[plan["schema_version"]]
    expected={launcher,".hrn/product/init-plan.json",".hrn/product/binding.json"};releases=set();receipt_ids=set()
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
        if plan["schema_version"]==6:require(prefix+"payload/colvia" in remove and prefix+"payload/src/hv2ref/continuation.py" in remove,"detach6-fixed-membership")
        paths = set(SERIAL_PATHS) | {"src/hv2ref/umbrella.py"} if prefix+"payload/src/hv2ref/umbrella.py" in remove else SERIAL_PATHS
        if prefix+"payload/src/hv2ref/candidates.py" in remove:paths=set(paths)|{"src/hv2ref/candidates.py"}
        if prefix+"payload/colvia" in remove:
            require(plan["schema_version"] in (3,4,5,6,7),"old-schema-entry-membership")
            paths=ENTRY_PATHS if plan["schema_version"]==3 else DELEGATION_PATHS
            if prefix+"payload/src/hv2ref/continuation.py" in remove:
                require(plan["schema_version"]in (5,6,7),"old-schema-continuation-membership")
                paths=CONTINUATION_PATHS
        if prefix+"payload/src/hv2ref/official_entry.py" in remove:
            require(plan["schema_version"]==7,"official-detach-schema")
            paths=OFFICIAL_PATHS
        expected|={prefix+"inventory.json"}|{prefix+"payload/"+p for p in paths}
        require(prefix+"inventory.json" in remove and rid=="product-release-"+remove[prefix+"inventory.json"]["sha256"][:24],"release-inventory")
    require(set(remove)==expected and remove[".hrn/product/binding.json"]["sha256"]==plan["expected_binding_ref"]["sha256"],"remove-completeness")
    require(any((remove[launcher]["sha256"], remove[launcher]["size_bytes"]) ==
                (remove[".hrn/product/releases/"+rid+"/payload/"+launcher]["sha256"],
                 remove[".hrn/product/releases/"+rid+"/payload/"+launcher]["size_bytes"])
                for rid in releases if ".hrn/product/releases/"+rid+"/payload/"+launcher in remove),"launcher-not-bound-to-release")
    require(isinstance(plan["truth_refs"],list),"truth-list");truth={};truth_names=[]
    for t in plan["truth_refs"]:
        keys(t,{"path","sha256"});name=t["path"]
        require(isinstance(name,str) and (name=="planning/candidates.json" or (name.split("/")[0] in ("intents","work","executions") and len(name.split("/"))>=3)) and valid_sha(t["sha256"]),"truth-path")
        truth[".hrn/"+name]=t["sha256"];truth_names.append(name)
    require(truth_names==sorted(set(truth_names),key=lambda n:n.encode()) and set(preserve)==set(truth)|{".hrn/format.json",".hrn/.gitignore"},"truth-preservation")
    saved={".hrn/format.json":fmt_raw,".hrn/.gitignore":raw_file(home/".gitignore")}
    require(saved[".hrn/.gitignore"]==b"staging/\nlocks/\n","ignore-bytes")
    for collection in ("intents","work","planning","executions"):
        allowed={n for n in truth if n.startswith(".hrn/"+collection+"/")}
        dirs={".hrn/"+collection}|{p.as_posix() for n in allowed for p in Path(n).parents if p.as_posix().startswith(".hrn/"+collection)}
        if collection=="executions" and safe_present(home/collection):
            # Lifecycle truth binds regular bytes; safe empty capsule subdirectories
            # are deliberately not records and may survive detach.
            capsules={"/".join(n.split("/")[:3]) for n in allowed}
            for p in (home/collection).rglob("*"):
                name=p.relative_to(target).as_posix()
                if p.is_dir():
                    safe_directory(p)
                    require(any(name==base or name.startswith(base+"/") for base in capsules),"unknown-execution-directory")
                    dirs.add(name)
        files,_=scan(home/collection,allowed,dirs);require(set(files)==allowed,"missing-truth");saved.update(files)
    for name,data in saved.items():
        require(sha(data)==preserve[name]["sha256"] and len(data)==preserve[name]["size_bytes"],"changed-preserved-bytes")
        if name in truth:
            require(sha(data)==truth[name],"truth-ref-mismatch")
            if not name.startswith(".hrn/executions/"):strict_json(data)
            else:require(plan["schema_version"]==7,"execution-truth-in-old-detach")
    files_order=[launcher]+[n for n in remove if n!=launcher]
    dirs={p.as_posix() for n in files_order if n!=launcher for p in Path(n).parents if p.as_posix().startswith(".hrn/product")}
    dir_order=sorted(dirs,key=lambda n:(-len(n.split("/")),n.encode()))
    remaining,present_dirs=scan(home/"product",set(remove),dirs)
    if safe_present(target/launcher):remaining[launcher]=raw_file(target/launcher)
    for name,data in remaining.items():require(sha(data)==remove[name]["sha256"] and len(data)==remove[name]["size_bytes"],"changed-remaining-bytes")
    remaining_window(plan["schema_version"],remove,remaining)
    for name in remove:
        if name not in remaining:require(not safe_present(target/name),"removed-path-not-safely-absent")
    remaining_names=[n for n in files_order if n in remaining]
    require(remaining_names==files_order[len(files_order)-len(remaining_names):],"invalid-file-prefix")
    if remaining_names:require(present_dirs==dirs,"early-directory-removal")
    else:require([n for n in dir_order if n in present_dirs]==dir_order[len(dir_order)-len(present_dirs):],"invalid-directory-prefix")
    if plan["schema_version"] in (3,4,5,6,7):
        import unicodedata
        require(not any(unicodedata.normalize("NFC",p.name).casefold()=="hv2" for p in target.iterdir()),"retired-entry-collision-preserved")
    capsule_prefixes={"/".join(n.split("/")[:3]) for n in saved if n.startswith(".hrn/executions/")}
    require(all(base+"/grant.json" in saved and base+"/journal.jsonl" in saved for base in capsule_prefixes),"execution-core-records-missing")
    execution_summaries={}
    for name,data in saved.items():
        if not name.startswith(".hrn/executions/") or not name.endswith("/grant.json"):continue
        value=keys(strict_json(data),{"record_type","schema_version","grant","spec"})
        base=name.rsplit("/",1)[0];grant=base.split("/")[-1]
        require(value["record_type"]=="official-execution-grant" and type(value["schema_version"]) is int and value["schema_version"]==1
                and value["grant"]==grant==sha((json.dumps(value["spec"],ensure_ascii=False,sort_keys=True,indent=2)+"\n").encode()),"execution-grant-binding")
        journal=saved.get(base+"/journal.jsonl");require(journal is not None and journal.endswith(b"\n"),"execution-journal")
        previous="0"*64;last=None
        for index,line in enumerate(journal.splitlines(),1):
            row=json.loads(line);keys(row,{"seq","previous","kind","value","sha256"})
            body={k:v for k,v in row.items() if k!="sha256"}
            compact=lambda x:(json.dumps(x,ensure_ascii=False,sort_keys=True,separators=(",",":"))+"\n").encode()
            require(type(row["seq"]) is int and row["seq"]==index and row["previous"]==previous and row["sha256"]==sha(compact(body)) and compact(row)==line+b"\n","execution-journal-chain")
            if index==1:require(row["kind"]=="granted" and row["value"]=={"grant":grant},"execution-first-row")
            previous=row["sha256"];last=row
        require(last is not None and (last["kind"]=="operator-resolved-unknown" or
                last["kind"]=="terminal" and last["value"]["status"] in ("completed","interrupted","revoked-before-launch")),"execution-not-closed")
        execution_summaries[grant]={"head":previous,"terminal_kind":last["kind"],"full_execution_semantics":"not-reimplemented"}
    selected={}
    for name,data in saved.items():
        if not name.endswith("/current.json"):continue
        current=strict_json(data);base=name.rsplit("/",1)[0]
        if base.endswith("/continuation"):
            require(plan["schema_version"] in (5,6,7),"continuation-truth-in-old-detach")
            keys(current,{"record_type","schema_version","authority_home_id","work_id","selection_ref"})
            wid=base.split("/")[-2]
            require(current["record_type"]=="continuation-current" and type(current["schema_version"]) is int
                    and current["schema_version"]==1 and current["authority_home_id"]==fmt["authority_home_id"]
                    and current["work_id"]==wid,"continuation-current-identity")
            selected[base]=continuation_refs(saved,base,current)
            continue
        selection_ref=ref(current["selection_ref"])
        path=base+"/selections/"+selection_ref["id"]+".json"
        require(path in saved and sha(saved[path])==selection_ref["sha256"],"current-selection-ref")
        selection=strict_json(saved[path]);revision_ref=ref(selection["revision_ref"])
        collection="drafts" if base.startswith(".hrn/intents/") else "revisions"
        path=base+"/"+collection+"/"+revision_ref["id"]+".json"
        require(path in saved and sha(saved[path])==revision_ref["sha256"],"selected-revision-ref")
        selected[base]={"selection_ref":selection_ref,"revision_ref":revision_ref}
    return {"classification":"partial" if remaining_names or present_dirs else "detached", "authority_home_id":fmt["authority_home_id"],
            "receipt_sha256":sha(receipt_raw),"execution_summaries":execution_summaries,"preserved_files":len(saved),"selected":selected,
            "remaining_files":remaining_names,"remaining_directories":[n for n in dir_order if n in present_dirs],
            "verification":"receipt-inventory-and-selected-refs", "full_record_semantics":"not-reimplemented", "mutation_authorized":False}


def main():
    try:
        if len(sys.argv)!=2:raise ValueError("usage: product_plain_auditor.py TARGET")
        target=safe_target(sys.argv[1])
        require(safe_present(target/".hrn"),"missing .hrn; legacy layouts unsupported")
        result=audit_once(target);require(result==audit_once(target),"unstable-detached-state")
        print(json.dumps(result,ensure_ascii=False,sort_keys=True))
        return 14 if result["classification"]=="partial" else 0
    except (ValueError,OSError,KeyError,TypeError,RecursionError,SyntaxError) as exc:
        print(json.dumps({"classification":"degraded","message":str(exc),"mutation_authorized":False},sort_keys=True))
        return 10


if __name__ == "__main__":
    raise SystemExit(main())
