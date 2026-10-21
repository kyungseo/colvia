"""Synthetic fresh-reader inputs; no reader answers or hidden conversation."""
from __future__ import annotations
import hashlib
import json
from pathlib import Path
import subprocess

TIME = "2026-01-01T00:00:00Z"
ENTRY = """# Project Agent Entry

This is an installed project. Start with `./colvia view`, then read the verified manual and natural-language adapter it displays. Follow those instructions and this project's existing documents. The project plan is `docs/plan.md`; Work narratives are under `docs/work/`. Use the verified installed entry. This project is not Colvia source development.
"""


def prepare_reader_cases(source, root):
    from hv2ref.jsonio import canonical_json_bytes
    from hv2ref.product import verify_workspace_product
    from hv2ref.work import snapshot, make_manifest, record_ref, read_work
    from hv2ref.candidates import read_candidates
    from hv2ref.continuation import records, current_record, read_continuation
    source, root = Path(source), Path(root)
    root.mkdir()

    def put(path, value):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(canonical_json_bytes(value))

    def call(target, args, value=None, *, external=False, expected=0):
        cmd = [str(source/"colvia"), "--source-checkout", *args] if external else [str(target/"colvia"), *args]
        result = subprocess.run(cmd, cwd=target, input=None if value is None else canonical_json_bytes(value),
                                capture_output=True, timeout=45)
        if result.returncode != expected:
            raise RuntimeError((result.stdout+result.stderr).decode(errors="replace")[-6000:])
        return json.loads(result.stdout)

    def init(name, plan, works):
        target = root/name; target.mkdir()
        (target/"AGENTS.md").write_text(ENTRY)
        (target/"docs/work").mkdir(parents=True)
        (target/"docs/plan.md").write_text(plan)
        for wid, title, body in works:
            (target/"docs"/(wid+".md")).write_text("# "+title+"\n\n"+body+"\n")
            (target/"docs/work"/(wid+".md")).write_text("# "+title+"\n\n계획: `docs/plan.md`\n대상: `docs/"+wid+".md`\n요청: 문서 검토와 남은 보완 사항 정리. 수락 상태와 후속 선택은 Work 기록을 확인한다.\n")
        args = ["init","--profile","continuation-1","--target",str(target),"--source",str(source),
                "--authority-home-id","home-reader","--operation-id","init-reader","--observed-at",TIME]
        packet=call(target,args,external=True)
        call(target,["init","--profile","continuation-1","--target",str(target),"--source",str(source),
                     "--apply","--input","-","--confirm",packet["confirm_token"]],packet["request"],external=True)
        return target

    def work(target,wid,title,*,completed):
        iid="intent-"+wid
        draft={"record_type":"intent-draft","schema_version":1,"authority_home_id":"home-reader","intent_id":iid,
               "revision_id":"draft-1","sequence":1,"prior_revision_ref":None,"actor":"agent","acceptance_authority":"owner",
               "observed_at":TIME,"facets":{key:{"status":"known","value":value} for key,value in {
                   "acceptance_oracle":"문서 검토 결과와 남은 항목을 Owner가 확인한다.","destination":"docs/"+wid+".md",
                   "expected_outcome":title+" 검토 결과","forbidden_scope":"다른 문서의 구현과 게시",
                   "goal":title+" 검토","scope":"docs/"+wid+".md"}.items()},"gaps":[],"statements":[],"route":"direct-entry"}
        call(target,["intent","draft"],draft)
        packet=call(target,["intent","prepare"],{"intent_id":iid,"revision_ref":record_ref(draft,"revision_id"),"actor":"owner",
            "reason":"합성 문서 검토 범위 승인","request_id":"accept-"+iid,"observed_at":TIME})
        selected=call(target,["intent","apply","--confirm",packet["confirm_token"]],packet["ticket"])
        current=selected["selections"][selected["current"]["selection_ref"]["id"]]
        intent={"authority_home_id":"home-reader","kind":"intent","id":iid,"revision_ref":current["revision_ref"],
                "acceptance_ref":current["acceptance_ref"],"selection_ref":selected["current"]["selection_ref"]}
        product=verify_workspace_product(target)
        tree=snapshot(target,verified_launcher_sha256=product["launcher_sha256"],verified_inventory_id=product["inventory"]["inventory_id"])
        manifest=make_manifest(tree,tree,scope=["docs/"+wid+".md"])
        digest=hashlib.sha256(canonical_json_bytes(manifest)).hexdigest()
        identity={"record_type":"work-identity","schema_version":1,"authority_home_id":"home-reader","work_id":wid,
                  "work_type":"review","created_at":TIME,"acceptance_authority":"owner","lineage":None}
        prior=None
        refs=[{"path":name,"sha256":hashlib.sha256((target/name).read_bytes()).hexdigest(),"role":role,"required":False}
              for name,role in (("docs/plan.md","plan"),("docs/work/"+wid+".md","narrative"))]
        for number,operation in ((1,"start"),(2,"submit-result")) if completed else ((1,"start"),):
            revision={"record_type":"work-revision","schema_version":1,"authority_home_id":"home-reader","work_id":wid,
                "record_id":"revision-"+str(number),"observed_at":TIME,"observed_scope":["synthetic document review"],"unavailable_scope":[],
                "author":"agent","operation":operation,"expected_prior_selection":prior,"intent_ref":intent,
                "scope":["docs/"+wid+".md"],"document_refs":refs,"evidence_refs":[],"result_refs":{"manifest":{"id":digest,"sha256":digest}},
                "progress":"review" if completed and number==2 else "active","next_action":"Owner가 검토 결과와 잔여를 판단한다.",
                "relations":[],"rebind_from":None,"execution_context":{"mode":"local","attempt_id":"attempt-"+str(number)}}
            selected=call(target,["work","publish"],{"identity":identity,"revision":revision,"manifest":manifest,
                "selection_id":"selection-"+str(number),"operation_id":"publish-"+wid+"-"+str(number)})
            prior=selected["current"]["selection_ref"]
        if completed:
            packet=call(target,["work","prepare"],{"work_id":wid,"action":"accept","actor":"owner","reason":"합성 문서 검토 결과 수락",
                "request_id":"accept-"+wid,"observed_at":TIME,"revision_ref":None,"supersedes":None})
            call(target,["work","apply","--confirm",packet["confirm_token"]],packet["ticket"])
        return read_work(target,wid)

    def follow(target,wid,choice,*,pending=False):
        packet=call(target,["continuation","prepare"],{"work_id":wid,"action":"select","actor":"owner",
            "owner_statement":"이 문서 검토의 다음 항목으로 기록한다.","reason":"검토 결과에 따른 다음 판단을 보존한다.",
            "request_id":"follow-"+wid,"observed_at":TIME,"choice":choice})
        if pending:
            # Explicit retained-prefix fixture; process-death evidence has its own tests.
            choice_record,_=records(packet["ticket"])
            base=read_work(target,wid);home=target/".hrn/work"/wid/"continuation"
            put(home/"current.json",current_record(base["identity"],None))
            put(home/"choices"/(choice_record["record_id"]+".json"),choice_record)
        else:
            call(target,["continuation","apply","--confirm",packet["confirm_token"]],packet["ticket"])
        return read_continuation(target,wid)

    first_works=[("guide-review","안내 문구 검토","안내 문구를 검토했다. 용어 예시 추가는 별도 보완 항목이다."),
                 ("glossary-review","용어 표 검토","용어 표를 검토했다."),("links-review","링크 검토","링크를 검토 중이다.")]
    first=init("resume-case-01","# 문서 정리 계획\n\n- 안내 문구 검토: 진행 중 (`guide-review`).\n- 남은 보완: 용어 예시 추가.\n- 용어 표 검토: 결과 확인.\n- 링크 검토: 진행 중.\n",first_works)
    for wid,title,_ in first_works:work(first,wid,title,completed=wid!="links-review")
    follow(first,"guide-review",{"kind":"proposal","goal":"용어 예시를 보완한다.","scope":"안내 문서의 용어 예시",
        "next_step":"예시 범위와 검증 방법을 정리해 intent를 제안한다.","decision_needed":"Owner가 새 범위와 intent를 수락해야 한다."})
    follow(first,"glossary-review",{"kind":"none"})

    second_works=[("entry-review","진입 문서 검토","진입 순서를 검토했다."),("examples-review","예시 검토","예시 검토를 진행한다.")]
    second=init("resume-case-02","# 문서 개선 계획\n\n- 진입 문서 검토: 결과 수락 (`entry-review`).\n- 예시 검토: 진행 중 (`examples-review`).\n- 오류 안내 보완: 후보에서 선택한 항목 확인.\n",second_works)
    for wid,title,_ in second_works:work(second,wid,title,completed=wid=="entry-review")
    follow(second,"entry-review",{"kind":"work","target_work_id":"examples-review"})
    for action in ("add","select"):
        request={"record_type":"candidate-request","schema_version":1,"authority_home_id":"home-reader","request_id":"candidate-"+action,
            "candidate_id":"error-guide","action":action,"expected_sha256":read_candidates(second)["sha256"],
            "writer":"owner","owner_statement":"오류 안내 보완을 다음 후보로 선택한다.","reason":"오류 대응 안내가 먼저 필요하다.",
            "observed_at":TIME,"payload":{"title":"오류 안내 보완","purpose":"오류 발생 시 다음 행동을 안내한다.","expected_effect":"재질문을 줄인다.","related_candidates":[]} if action=="add" else {}}
        call(second,["candidate",action],request)

    for label,damage in (("comparison-01",False),("comparison-02",True)):
        target=init(label,"# 안내 검토\n\n- 안내 검토: 결과 확인.\n",[("notice-review","안내 검토","안내 내용을 검토했다.")])
        work(target,"notice-review","안내 검토",completed=True)
        follow(target,"notice-review",{"kind":"none"},pending=not damage)
        if damage:(target/".hrn/work/notice-review/continuation/current.json").write_bytes(b"{")

    if read_work(first,"guide-review")["state"]!="completed":raise RuntimeError("source fixture is not completed")
    if read_continuation(first,"links-review")["effective_choice"] is not None:raise RuntimeError("fixture choice drift")
    return {"case_01":{"project":str(first),"comparison":str(root/"comparison-01")},
            "case_02":{"project":str(second),"comparison":str(root/"comparison-02")},
            "all_synthetic":True,"reader_answers_included":False}
