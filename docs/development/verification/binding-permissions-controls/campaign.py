"""Parent-only bounded campaign; no product imports or child access expansion."""
import fcntl
import math
import os
import re
from pathlib import Path
import stat
import time
from common import config, digest, exclusive_json, read_json, regular, require, unlinked_path, campaign_limits_disabled, attempt_number

MODES = {"complete-normal", "complete-parent-O"}
GIB = 1024**3


class ResourceGuard:
    """Observe this task's outputs; reserve is created before the reviewed run."""
    def __init__(self, root):
        self.root = unlinked_path(root).parent
        self.reserve = root / "campaign-cleanup-reserve.bin"
        self.reserve_info = self.reserve.lstat()
        info = self.reserve_info
        require(stat.S_ISREG(info.st_mode) and info.st_nlink == 1 and info.st_uid == os.geteuid()
                and info.st_size == 512*1024**2 and info.st_blocks*512 >= info.st_size,
                "physical campaign cleanup reserve absent")
        self.next_free = self.next_scan = 0
        self.latest = {}
        self.peak = {"logical_bytes":0,"allocated_bytes":0,"free_bytes":2**63}
    @staticmethod
    def threshold(observed, admission):
        maximum = 8*GIB if admission else 12*GIB
        minimum = 25*GIB if admission else 15*GIB
        require(max(observed["logical_bytes"],observed["allocated_bytes"]) < maximum, "task-output capacity threshold")
        require(observed["free_bytes"] >= minimum, "volume free-space threshold")
    def release_reserve(self):
        info=self.reserve.lstat()
        require((info.st_dev,info.st_ino,info.st_size,info.st_nlink)==
                (self.reserve_info.st_dev,self.reserve_info.st_ino,512*1024**2,1), "cleanup reserve changed")
        self.reserve.unlink()
    def check(self, *, admission=False, force=False):
        now=time.monotonic()
        if force or admission or now>=self.next_free:
            fs=os.statvfs(self.root)
            self.latest["free_bytes"]=fs.f_bavail*fs.f_frsize
            self.next_free=now+2
        if force or admission or now>=self.next_scan:
            logical=allocated=count=0
            for base,dirs,files in os.walk(self.root,followlinks=False):
                for name in files:
                    path=Path(base)/name
                    try:info=path.lstat()
                    except FileNotFoundError:continue  # A child may delete its own fixture.
                    if stat.S_ISREG(info.st_mode):
                        logical+=info.st_size;allocated+=info.st_blocks*512
                    count+=1
                    if count%256==0:require(time.monotonic()-now<=3,"output-size observation exceeded bound")
            self.latest.update(logical_bytes=logical,allocated_bytes=allocated)
            self.next_scan=now+15
        for key,value in self.latest.items():
            self.peak[key]=min(self.peak[key],value) if key=="free_bytes" else max(self.peak[key],value)
        self.threshold(self.latest,admission)
        return dict(self.latest)


def attempt_names(root):
    names = {"r%02d" % n for n in range(10)}
    for path in root.glob("r[0-9]*"):
        if not re.fullmatch(r"r[0-9]+", path.name):
            continue
        require(not path.is_symlink(), "linked campaign attempt")
        if not path.is_dir():
            continue
        attempt_number(path.name)
        names.add(path.name)
    return sorted(names, key=attempt_number)


def elapsed(root):
    total=0.0;failures=[];attempts=set()
    # Retain all historical accounting and discover later correction directories.
    for attempt in attempt_names(root):
        for call in sorted((root/attempt/"calls").glob("*")):
            inputs=read_json(unlinked_path(call/"inputs.json"))
            require((call/"result.json").is_file(),"unfinished campaign call; inspect process/recovery")
            result=read_json(call/"result.json")
            require(result["inputs_sha256"]==digest(regular(call/"inputs.json")),"parent receipt input drift")
            seconds=result["seconds"]
            require(type(seconds) in (int,float) and math.isfinite(seconds) and seconds>=0,"invalid elapsed time")
            total+=seconds
            if not result.get("admission_only",False):
                attempts.add(attempt)
                if attempt!="r00":
                    require(inputs["correction_sha256"]==digest(regular(root/attempt/"correction.json")),"executed correction note changed")
                if not result["execution_pass"]:
                    keys=result.get("failed_phases") or [[inputs["lane"],inputs["mode"],inputs["slot"]]]
                    failures.extend((attempt,*key) for key in keys)
                    if not result.get("process_cleanup_verified",result.get("group_absent",False)):
                        verify_process_recovery(root,call,inputs,result)
    return total,failures,attempts


def verify_process_recovery(root,call,inputs,result):
    note=read_json(call/"process-recovery.json")
    require(set(note)=={"schema","failed_result_sha256","children","driver_disposition"} and note["schema"]==1,"process recovery shape")
    require(note["failed_result_sha256"]==digest(regular(call/"result.json")),"process recovery receipt drift")
    expected={(x["pid"],x["pgid"]) for x in result.get("children",[]) if x.get("spawned")}
    require(expected and {(x["pid"],x["pgid"]) for x in note["children"]}==expected,"process recovery identities unknown")
    require(all(x["group_absent"] is True and x["direct_child_exit_known"] is True and x["errors"]==[] for x in note["children"]),"process recovery observation incomplete")
    ref=note["driver_disposition"];path=unlinked_path(ref["path"])
    require(path.is_relative_to(root) and digest(regular(path))==ref["sha256"],"process recovery disposition drift")


def correction(root,attempt,c,lane,mode,slot,failures,attempts,*,policy=None):
    """A reviewed bundle consumes one global correction, not one per prerequisite.

    affected_phases names previously executed primary phases, never a lane's
    unexecuted initial phases. A failure inside this attempt blocks every new
    call until the next reviewed bundle, even in another lane.
    """
    if attempt=="r00":
        require(not failures,"failed initial attempt requires reviewed correction")
        return None
    number=attempt_number(attempt)
    accounting_only = policy is not None and campaign_limits_disabled(policy)
    require((number > 0 if accounting_only else number in (1,2,3,4,5,6,7,8,9))
            and all("r%02d"%n in attempts for n in range(number)),"correction attempt order")
    require(not any(row[0]==attempt for row in failures),"unexpected failure blocks all new calls in this attempt")
    note=read_json(root/attempt/"correction.json")
    require(set(note)=={"schema","previous_attempt","reason","affected_phases","controls","prior_invocations","review"} and note["schema"]==2,"correction admission shape")
    require(note["previous_attempt"]=="r%02d"%(number-1) and note["reason"] in {"failed-phase","input-change"},"correction lineage")
    require(note["controls"]==c["controls"],"correction controls mismatch")
    affected={tuple(v) for v in note["affected_phases"]}
    require(affected and len(affected)==len(note["affected_phases"]) and all(len(v)==3 and v[0] in {"current","retained"} for v in affected),"invalid/duplicate affected phase")
    prior_notes=[]
    for n in range(1,number):
        old=read_json(root/("r%02d"%n)/"correction.json");prior_notes.append(("r%02d"%n,old))
    for phase in (() if accounting_only else affected):
        # Historical ceilings are unchanged. Owner's r09 extension adds only
        # a fourth current/transition correction and retains current/Core at 3.
        if phase==("current","focused","core"):limit={4:2,5:3,6:3,7:3,8:3,9:3}.get(number,1)
        elif phase==("current","focused","transition"):limit={7:2,8:3,9:4}.get(number,1)
        else:limit=1
        used=sum(phase in set(map(tuple,old["affected_phases"])) for _,old in prior_notes)
        require(used<limit,"corrected attempt allowance per affected phase exhausted")
    for failed_attempt,*key in failures:
        if attempt_number(failed_attempt)<number:
            resolved=any(attempt_number(failed_attempt)<attempt_number(na) and tuple(key) in set(map(tuple,no["affected_phases"])) for na,no in prior_notes)
            require(resolved or tuple(key) in affected,"unresolved earlier failure outside reviewed correction")
    review=note["review"]
    require(set(review)=={"packet","response","disposition"},"correction review identities missing")
    for key in ("packet","response"):
        item=review[key];require(set(item)=={"path","sha256"},"review ref keys")
        path=unlinked_path(item["path"])
        require(path.is_relative_to(root) and digest(regular(path))==item["sha256"],"correction review drift")
    disposition=review["disposition"]
    require(set(disposition)=={"record","text","sha256"} and isinstance(disposition["record"],str)
            and isinstance(disposition["text"],str) and disposition["text"].strip()
            and digest(disposition["text"].encode())==disposition["sha256"],"Driver disposition missing or changed")
    # Literal disposition is part of this sealed machine input, copied from the
    # single FEAT record. It is not an automatic Reviewer/Owner authorization.
    require(note["prior_invocations"],"prior invocation evidence missing")
    prior_lanes=set();executed_phases=set();changed=False
    for item in note["prior_invocations"]:
        pc,pp=config(item["path"],item["sha256"])
        require(pp["root"].parent.parent==root and attempt_number(pp["root"].parent.name)<number
                and all(pc[k]==c[k] for k in ("runtime","git","git_system_config")),"correction runtime/lineage drift")
        prior_lanes.add(pp["root"].name)
        for call in (pp["root"].parent/"calls").glob("*"):
            pi=read_json(call/"inputs.json");pr=read_json(call/"result.json")
            if pr.get("admission_only",False):continue
            require(pr["inputs_sha256"]==digest(regular(call/"inputs.json")),"prior phase receipt drift")
            if pi.get("invocations",{}).get(pp["root"].name)==item:
                executed_phases.add((pp["root"].name,pi["mode"],pi["slot"]))
        changed |= pc["controls"]!=c["controls"] or (pp["root"].name==lane and pc["source_digest"]!=c["source_digest"])
    require(changed or failures,"no reviewed input change or recorded failure")
    require({v[0] for v in affected}<=prior_lanes,"affected lane lacks prior input")
    require(affected<=executed_phases,"affected phase was never executed with the bound prior input")
    return note


def pair_budget(estimates,spent,pending,*,reused=(),accounting_only=False):
    if accounting_only:
        require(set(estimates)=={"current","retained"} and all(v is None or type(v) in (int,float) and math.isfinite(v) and v>0 for v in estimates.values()),"invalid complete estimate")
        require(set(reused)<=set(estimates) and len(set(reused))<2,"do not rerun a pair merely to rename completed evidence")
        return None
    require(set(estimates)=={"current","retained"} and all(type(v) in (int,float) and math.isfinite(v) and v>0 for v in estimates.values()),"complete estimate unavailable")
    require(estimates["retained"]<=5400 and sum(estimates.values())<=10800,"measured estimate exceeds approved complete ceiling")
    require(set(reused)<=set(estimates) and len(set(reused))<2,"do not rerun a pair merely to rename completed evidence")
    limit=math.ceil(sum(v for k,v in estimates.items() if k not in reused))
    require(28800-spent>=pending*limit+1800,"insufficient remaining mandatory complete/artifact reserve")
    return limit


def lane_budget(lane,estimates,remaining,*,reused=()):
    current_reserve=0 if "current" in reused else estimates["current"]
    budget=min(5400,estimates["retained"],remaining-current_reserve) if lane=="retained" else min(remaining,estimates["current"])
    require(budget>20,"no bounded lane budget remains")
    return budget


def prior_complete(root,attempt,expected,lane,mode,ref,note):
    """Parent-only reuse of a sealed, unaffected completed lane; no child launch."""
    import controller
    require(note is not None and set(ref)=={"invocation","result","parent_result"},"prior-evidence shape")
    require(ref["invocation"] in note["prior_invocations"],"prior input not in reviewed correction")
    for item in ref.values():
        require(set(item)=={"path","sha256"},"prior reference shape")
        p=unlinked_path(item["path"])
        require(p.is_relative_to(root) and digest(regular(p))==item["sha256"],"prior reference drift")
    old,p=config(ref["invocation"]["path"],ref["invocation"]["sha256"])
    require(p["root"].parent.parent==root and attempt_number(p["root"].parent.name)<attempt_number(attempt) and p["root"].name==lane,"prior lane/attempt mismatch")
    for key in ("schema","phase","source_digest","controls","runtime","git","git_system_config","collection_sha256","factory","selection"):
        require(old[key]==expected[key],"changed evidence cannot be reused: "+key)
    target=p["exec"]/"runs"/(mode+"-final")/"result.json"
    require(Path(ref["result"]["path"])==target,"prior mode/result mismatch")
    controller.completed(old,p,mode,"final",same_source=True)
    parent_path=Path(ref["parent_result"]["path"])
    require(parent_path==p["root"].parent/"calls"/("pair-"+mode+"-final")/"result.json","prior parent mode/attempt mismatch")
    parent=read_json(parent_path);parent_input=read_json(parent_path.parent/"inputs.json")
    require(parent["inputs_sha256"]==digest(regular(parent_path.parent/"inputs.json")) and parent["process_cleanup_verified"]
            and lane in parent.get("reusable_lanes",[]) and parent_input["mode"]==mode
            and parent_input["invocations"][lane]==ref["invocation"],"prior parent completion/cleanup is not reusable")
    return old,p,Path(ref["invocation"]["path"]),ref["invocation"]["sha256"]


def dispatch(c,p,input_path,input_sha,mode,slot,start):
    import controller
    from calibration import report
    policy=read_json(p["controls"]/"campaign.json")
    accounting_only=campaign_limits_disabled(policy)
    require(accounting_only or policy["pair_seconds"]==10800,"historical campaign is read-only; use reviewed continuation inputs")
    root=unlinked_path(policy["root"]);attempt,lane=p["root"].parent.name,p["root"].name
    with (root/"campaign.lock").open("a+b") as lock:
        fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
        spent,failures,attempts=elapsed(root)
        inputs={lane:(c,p,input_path,input_sha)};pair=mode in MODES;estimates=None;reused={};guard=None
        try:
            note=correction(root,attempt,c,lane,mode,slot,failures,attempts,policy=policy)
            require(accounting_only or spent<28800,"cumulative campaign budget exhausted")
            guard=ResourceGuard(root);initial_resources=guard.check(admission=True)
            if pair:
                require(lane=="current" and slot=="final","complete dispatch starts once from current lane")
                other_path=input_path.parent/("retained-"+mode+"-final.json")
                other_sha=digest(regular(other_path));oc,op=config(other_path,other_sha)
                require(oc["phase"]=="entry" and op["root"]==root/attempt/"retained","pair lane identity")
                require(all(oc[k]==c[k] for k in ("controls","runtime","git","git_system_config")),"pair controls/runtime mismatch")
                require(oc["source_files"]==c["predecessor_files"] and op["source"]==p["predecessor"],"pair predecessor mismatch")
                inputs["retained"]=(oc,op,other_path,other_sha)
                for name,(lc,lp,li,lh) in tuple(inputs.items()):
                    ref=c.get("prior_evidence",{}).get(name+"/"+mode+"/final")
                    if ref is not None:
                        inputs[name]=prior_complete(root,attempt,lc,name,mode,ref,note);reused[name]=ref
                    else:
                        controller.preflight(lc,lp,mode,slot,input_path=li)
                        for focused in (("core","transition") if name=="current" else ("p1",)):
                            controller.completed(lc,lp,"focused",focused,same_source=True)
                estimates={name:report(lc,lp)["complete_estimate"] for name,(lc,lp,_,_) in inputs.items()}
                pending=sum(not (root/attempt/"calls"/("pair-"+full+"-final")/"result.json").exists() for full in MODES)
                limit=pair_budget(estimates,spent,pending,reused=reused,accounting_only=accounting_only)
            else:
                require(not c.get("prior_evidence"),"prior complete links belong only to a complete pair")
                controller.preflight(c,p,mode,slot,input_path=input_path)
                limit=None if accounting_only else (1200 if lane=="current" and mode in {"smoke","focused"} else controller.LIMITS[mode])
            require(accounting_only or 28800-spent>=limit,"insufficient allowance for this mode")
            if mode=="artifact":
                for full in MODES:
                    anchor=root/attempt/"calls"/("pair-"+full+"-final")
                    r=read_json(anchor/"result.json");a=read_json(anchor/"inputs.json")
                    require(r["execution_pass"] and r["inputs_sha256"]==digest(regular(anchor/"inputs.json")),"artifact needs both combined modes")
                    pc,_=config(a["invocations"]["current"]["path"],a["invocations"]["current"]["sha256"])
                    require(all(pc[k]==c[k] for k in ("source_digest","controls","runtime","git","collection_sha256")),"artifact candidate drift")
        except Exception as exc:
            # Every admission is exclusive and charged, even repeated refusals.
            parent=root/attempt/"calls";parent.mkdir(parents=True,exist_ok=True)
            stem="admission-"+lane+"-"+mode+"-"+slot
            serial=1
            while (parent/(stem+"-"+str(serial))).exists():serial+=1
            rejected=parent/(stem+"-"+str(serial));rejected.mkdir(mode=0o700)
            exclusive_json(rejected/"inputs.json",{"lane":lane,"mode":mode,"slot":slot,"invocation_sha256":input_sha,"invocation_path":str(input_path)})
            exclusive_json(rejected/"result.json",{"inputs_sha256":digest(regular(rejected/"inputs.json")),"seconds":round(time.monotonic()-start,3),"execution_pass":False,"admission_only":True,"process_cleanup_verified":True,"error":type(exc).__name__+": "+str(exc)})
            raise
        name=("pair" if pair else lane)+"-"+mode+"-"+slot
        call=root/attempt/"calls"/name;call.parent.mkdir(parents=True,exist_ok=True);call.mkdir(mode=0o700)
        exclusive_json(call/"inputs.json",{"lane":lane,"mode":mode,"slot":slot,"limit_seconds":limit,"spent_before":spent,
            "correction_sha256":digest(regular(root/attempt/"correction.json")) if note else None,
            "invocations":{k:{"path":str(v[2]),"sha256":v[3]} for k,v in inputs.items()},"estimates":estimates,"reused":reused,"initial_resources":initial_resources})
        ok=False;error=None;cleanup=True;children=[];failed=[];eligible=list(reused)
        try:
            for name in (("retained","current") if pair else (lane,)):
                if name in reused:continue
                lc,lp,li,lh=inputs[name]
                guard.check(force=True)
                if mode=="acquire":
                    lp["root"].mkdir(mode=0o700);lp["exec"].mkdir(mode=0o700)
                    for dest in (lp["root"]/"denied-sentinel",lp["root"]/"credential-sentinel",lp["exec"]/"sibling-sentinel"):
                        with dest.open("x") as f:f.write("synthetic-not-a-credential\n")
                remaining=None if accounting_only else limit-(time.monotonic()-start)
                budget=None if accounting_only else (lane_budget(name,estimates,remaining,reused=reused) if pair else remaining)
                with (lp["root"]/"controller.lock").open("a+b") as lane_lock:
                    fcntl.flock(lane_lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
                    state={"spawned":False,"cleanup_verified":True,"pid":None,"pgid":None};children.append(state)
                    ok=controller.run(lc,lp,li,lh,mode,slot,time.monotonic(),budget_override=budget,process_state=state,resource_guard=guard,accounting_only=accounting_only)
                evidence=read_json(lp["exec"]/"runs"/(mode+"-"+slot)/"result.json")
                cleanup &= evidence["group_absent"] and not evidence["cleanup_errors"]
                if not ok:
                    failed.append([name,mode,slot]);break
                if pair:eligible.append(name)
            guard.check(force=True)
            within=accounting_only or time.monotonic()-start<=limit and spent+time.monotonic()-start<=28800
            if not within:
                error="aggregate-deadline-exhausted";eligible=[]
                failed=[[name,mode,slot] for name in inputs if name not in reused]
            ok=ok and within
        except Exception as exc:
            error=type(exc).__name__+": "+str(exc);ok=False;cleanup=all(x["cleanup_verified"] for x in children)
            failed=failed or [[name,mode,slot]];eligible=[]
        finally:
            # Release only this known, non-authority reserve if space has become
            # insufficient. The next call must allocate/verify a new reserve.
            reserve_error=None
            if guard.latest.get("free_bytes",25*GIB)<15*GIB:
                try:guard.release_reserve()
                except (OSError,RuntimeError) as exc:reserve_error=type(exc).__name__+": "+str(exc)
            exclusive_json(call/"result.json",{"inputs_sha256":digest(regular(call/"inputs.json")),"seconds":round(time.monotonic()-start,3),
                "execution_pass":ok,"error":error,"process_cleanup_verified":cleanup,"spawned":any(x["spawned"] for x in children),
                "children":children,"failed_phases":failed,"reusable_lanes":eligible if cleanup else [],"resources":guard.peak,"reserve_error":reserve_error})
        if error:print(error,flush=True)
        raise SystemExit(0 if ok else 2)
