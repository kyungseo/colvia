# 공식 문서 실행의 링크 검증 정보 연결

## 승인 범위와 기준

2026-10-29 Owner가 기존 두 문서 view를 유지하는 링크 metadata 요청·preview 결속, 실행 전 링크 범위 확인, 기존 worker 계약 연결, 집중 검증과 독립 검토를 승인했다. 실제 adopter 문서나 식별정보는 이 기록과 검토 패킷에 포함하지 않는다. 이전 제품 연결 결과는 [완료 기록](FEAT-20261029-002-official-adapter-product.md)을 유지한다. 시작 commit은 `8f689746331edf1d848a626cc9364df77d40e29b`이며 source checkout은 clean이었다. 이 문서는 source-only 작업 기록이며 runtime Work를 만들지 않는다.

문서 읽기는 기존 1–8개·단일 pack·단일 출력 편집 구간을 유지한다. 추가 링크 대상은 명시한 절대 실제 경로와 anchor 목록으로만 받는다. 본문에 없는 추가 대상·anchor, 별칭·중복·관리 경로는 거절한다. anchor가 없으면 파일 존재/identity/권한/크기/mtime만 확인하고 본문을 읽지 않는다. anchor가 있으면 최대128KiB UTF-8 본문 digest와 지정 anchor를 검증한다. 이는 모델에 추가 본문을 보내는 권한이 아니다.

초기 출력파일 전체의 DOC-LINKS를 읽기 전용으로 먼저 확인한다. 기존 요청도 초기 링크 검사가 실패하면 prepare에서 거절한다. 깨진 링크를 편집 구간 안에서 복구하는 작업과 새로운 링크 대상 추가는 이번 제한된 진입점의 지원 범위 밖이다. 이 변경은 승인된 실행 전 불충분한 링크 입력 거절을 구체화한다. no-metadata 입력의 성공 spec 구조와 기존 capsule 형식은 유지한다.

OS 정책·worker schema·Core authority·설치 window·payload 경로 집합을 바꾸지 않는다. 실제 adopter 설치·모델 실행·Git 통합·결과 수락은 제외한다. 계정 모델 호출을 사용하는 제품 실증은 이번 작업에 없다.

## 검증 선택과 예산

누적 기준은 앞선 기록을 이어받으며 R0 전송 승인 재개 시432.816분이었다. 예상30–50분은 구현10–20분·집중/전환10–15분·검토/정리10–15분의 판단 추정이다. 기존 집중103초/전환494초는 참고 측정값이며 이번 시간을 보장하지 않는다. 병행시간은 한 번 계산하고 실제 Owner 대기만 제외한다. 신규 시작490분·중단500분을 유지한다.

완전 회귀 anchor는 이전 R3 양쪽 실행의 원본·실패1건·Windows 제외100개와 R4의 해당 실패/변경위험 보정 근거다. 이를 전체 PASS로 올리지 않는다. 누적 변경은 공식 요청 admission, metadata 전달, shipped 설명과 해당 테스트에 한정되므로 같은 runtime/OS/기존 격리 정책에서 영향을 받는 official admission/execution 및 새 링크 경계 사례를 일반/최적화 각각 검사한다. 그 뒤 exact 새 후보/직전 수락 후보 사이의10개 lifecycle factory를 두 모드로 실행한다. 이전/현재 capsule 판독과 metadata drift 뒤 status/resolve도 확인한다. source·정책 불변과 실제 종료를 별도로 대조한다. 시간초과·소비된 live 호출은 자동 재시도하지 않는다.

## R0 요청과 원문

요청은 최소 metadata 연결 계획과 관련 코드의 정적 검토다. 정확한 packet SHA-256은 `865cfa1db676ce41af2550f2d68d41489f7e5c02a7fdb318415877e3c6738359`이며24,016바이트다. Owner가 해당 Claude 구독 전송을 명시 승인했다. `claude.ai`/`firstParty`, API override 없음 확인 후 도구 없는 새 세션으로 실행했다. 실제 모델은 `claude-opus-5-5`, session은 `234af921-51ea-45b2-8842-072d7b735ed7`이다.139.537초 정상종료이며 실행 검증을 수행하지 않은 독립 정적 검토다. 원 패킷·identity·최종 응답은 결과 수락을 위한 private 근거로 보존한다.

# R0 Static Review: Bounded Link Metadata Correction Plan

**Verdict: Conditional.** The direction is sound. It reuses the existing controller and worker metadata contract, keeps the legacy spec byte-identical when `link_targets` is absent, gives no-anchor targets no read rights, and adds no new schema. However, five issues should be resolved in the plan before implementation. Without them the gate is either bypassable on macOS or narrows legacy behaviour without saying so.

This review does not accept any result, and it is limited to the supplied source and plan.

## Blocking findings

**B1. Case-insensitive aliases bypass the exclusion, duplicate and overlap checks.**
- **Problem:**
  - Default APFS is case-insensitive.
  - `canonical_existing` and `Path.resolve` do not case-fold.
  - So `.GIT/config`, `.Hrn/...` or `Colvia` pass the `parts`/`name` string tests in `official_entry.py` (the document admission loop).
  - `README.md` and `readme.md` are two distinct canonical strings for the same inode. Each has nlink 1, and each passes the controller's `path.resolve(strict=True) == path` check.
  - String-based duplicate detection and document-overlap detection therefore both fail.
- **Fix:**
  - Detect duplicates and overlap by `(st_dev, st_ino)` across all document records and link targets.
  - Apply the `.git`/`.hrn`/launcher exclusion with `casefold()`, or better, by comparing ancestor identities against the identities of `worker_root/.git`, `target/.hrn` and the launcher.
  - Require the requested path string to equal the canonical form exactly. That also gives you the planned symlink refusal; `canonical_existing` alone silently follows symlinks.
- **Note:** The existing `document-path-alias` check has the same gap. Record it, even if fixing it is out of scope.

**B2. Pre-flight `DOC-LINKS` on the full original output: semantics and side effects.**
- **Legacy narrowing:** Legacy requests whose original output links outside document scope used to prepare successfully. They will now be refused. The plan says this ("remain valid if…"), but it is a compatibility narrowing. The "unchanged legacy spec" test does not cover it, so it needs explicit Owner acknowledgement and a dedicated test.
- **Link-repair tasks:** A task whose purpose is fixing a broken link inside the replace-range is now unadmittable. Choose one of these and test it:
  - (a) Pre-flight only links whose source lies outside the editable range. Watch for reference definitions in the prefix or suffix.
  - (b) Explicitly declare repair tasks out of scope.
- **Side effects:** `prepare` returns `effects: 'none'` and is re-run inside `execute`. The pre-flight must run in-process and read-only. It must not materialise slot or scratch directories, `spec.json` or `.hrn` files, and must not spawn the sandbox runner unless that is proven write-free. Add a test asserting `prepare` creates no filesystem entries.

**B3. Requested targets must be minimal.**
- **Problem:** The plan limits targets to 64 beneath the worker root but does not require each entry to be needed. Extra entries give unneeded `file-read*` rights (anchored, up to 128 KiB each) or durable metadata (size and mtime of, say, `.env`) recorded in the spec and capsule.
- **Fix:** Require every requested path, and every requested anchor, to be referenced by a local link in the original output. Refuse anything extra with an error such as `unreferenced-link-target`. This makes "no broad directory read rights" true by construction.

**B4. `prepare` compares against the raw `worker_root`.**
- **Problem:** `worker_root = Path(request['worker_root'])` is used for `is_relative_to` and for the runtime-overlap check, but `observe_work` canonicalises its own copy.
  - For link targets, a non-canonical root (`..`, a symlinked prefix such as `/tmp` vs `/private/tmp`) causes spurious refusals.
  - It also leaves an existing hole: the runtime-root overlap check compares a canonical path against an alias, so a real overlap can pass.
- **Fix:** Return the canonical worker root from `observe_work` and use it everywhere, or require `request['worker_root'] == str(canonical)`.

**B5. Capsule lifecycle must not depend on rechecking link metadata.**
- **Problem:** Identify every reader of the stored spec: `public_status`, `cancel`, `resolve`/`resolution_preview` and `Host` reconstruction. None of these may re-run the link-metadata drift check or a strict request-shape check.
  - Otherwise, editing a linked file after a failure makes the capsule unresolvable.
  - Otherwise, a reader that does an exact-key check on `request.documents` rejects new capsules.
- **Tests:** The previous-P / new-Q cases should cover:
  - P reading a capsule written by Q.
  - Q reading a capsule written by P.
  - `resolve` after a link target has been touched.

## Non-blocking findings

1. **Limits of no-anchor evidence.** These should be stated in the plan, preview text and docs.
   - Identity, mode, size and mtime prove only that the same regular-file object existed with unchanged size and mtime at each check. They say nothing about content.
   - In-place rewrites with the same size and a restored mtime (`touch -d`) go undetected.
   - The check is point-in-time: the target can vanish after the final verification.
   - `st_ctime_ns` cannot be set from userland and would strengthen the check, but it changes the worker's `exact_keys`. Leave it as a deferred option rather than adding it here.
2. **A spurious drift failure consumes the run.** An editor, indexer or `touch` changing mtime mid-execution makes the run fail with `link metadata drift` after the capsule exists, and live runs are not retried. Document that operators should not touch linked files during execution. Make sure the failure classifies as drift, not as a model fault.
3. **Parser constructed once per entry.** In `official_worker.py:310`, `GFM(...)` is created inside the loop, so with up to 64 anchored entries, every verifier call starts 64 parser instances. Hoist the parser out of the loop, or cap anchored entries well below 64.
4. **Undecodable anchored targets crash.** In the worker, `raw.decode("utf-8")` raises `UnicodeDecodeError` instead of going through `require`. Prepare's check prevents it on admission, but drift to non-UTF-8 bytes with an unchanged digest is impossible while a changed digest is caught first. The crash is therefore unreachable today but fragile. Wrap the decode in `require`.
5. **Anchor and path normalisation must match `DOC-LINKS` exactly.** Specify whether anchors are given with or without `#` and whether they are percent-decoded and case-normalised. Require anchors to be unique, store them sorted, and refuse duplicates. Define request paths as worker-relative POSIX with no `./`, `..` or trailing slash. Links to directories cannot be admitted, so the 18-target README must contain no directory links.
6. **Explicit `link_targets: []`.** It produces a different grant from an absent key with the same meaning. Either refuse it or document it. Refusing keeps one canonical form.
7. **The model cannot see which targets are admitted.** The model can add new links inside the edit range, and those fail `DOC-LINKS` after the run is consumed. Consider putting the admitted target list (paths and anchors, no bodies) into the task constraints, or accept this failure mode explicitly.
8. **Sandbox evidence.** Add an assertion on the generated profile: no-anchor paths appear only in `file-read-metadata` and never in `file-read*`. If feasible, add a sandboxed negative read of a no-anchor target.
9. **Time budget.** "490 new-start / 500 stop" with 30–50 expected active minutes cannot be judged without the current cumulative figure. State it, and order the work so focused tests come before the 20 lifecycle cases, so the hard stop cannot cut off the evidence that matters most.

## Missing test cases

Add these to the planned set:
- Case-variant alias of a document or another target.
- `.GIT`/`.Hrn` case variants.
- A non-canonical `worker_root` string.
- An unreferenced extra target or anchor.
- An anchor list on a no-anchor-equivalent entry, and duplicate anchors.
- Explicit `[]`.
- A legacy request whose output now fails pre-flight.
- A link-repair task inside the edit range (with the outcome chosen in B2).
- `prepare` creates no filesystem entries.
- `resolve`/`status` after link-target drift.
- Cross-version capsule reads in both directions.
- A profile-literal assertion for no-anchor targets.

## Confirmed as correct in the supplied source

- When `link_targets` is absent, `request` and `link_metadata: {}` are unchanged, so the legacy grant digest is preserved.
- The request and the resulting metadata both fall inside `spec`, so both are bound by the grant digest.
- Controller and worker recheck identity, mode, size and mtime, and recheck content only when `sha256` is non-null. The sandbox gives data-read rights only to anchored targets.
- The model cannot write link targets; it can only write the output.

The scope claim holds: there are no Core, lifecycle-schema, OS-policy, provider or runtime-execution changes, provided B5 confirms no capsule reader re-validates request shape.

## Driver 처분

B1 accept: 문서와 metadata의 dev/inode 중복, casefold 관리 경로 거절을 추가한다. symlink가 canonical_existing에서 조용히 허용된다는 부연은 현재 코드의 resolve 동일성 및 ancestor symlink 검사와 달라 defend하며 음성 검사로 확인한다. B2 accept: 초기 전체 링크의 실패는 실행 전 거절하며 링크 복구 작업은 지원 밖임을 명시하고 무효과 테스트를 추가한다. 이것은 이미 승인된 초기 링크 admission의 구체화이며 검증 축소가 아니다. B3 accept: 초기 출력의 링크와 정확히 일치하는 추가 대상/anchor만 허용한다. B4 accept: prepare에서도 canonical worker root를 직접 사용한다. 기존 observe_work가 이미 raw 입력의 비정규·symlink 경로를 거절하므로 제시된 alias 우회는 확인된 재현이 아닌 정적 우려다. B5 accept: status/cancel/resolve/closed restore는 새 metadata를 재승인하지 않도록 기존 reader를 유지하고 drift 및 양방향 판독을 검사한다.

N1/N2 accept: no-anchor는 내용 동일성 증거가 아니며 같은 크기/복원 mtime 변경을 검출하지 못한다. 실행 중 linked file 변경은 drift로 중단될 수 있고 자동 재시도하지 않는다. N3 accept: anchor target 최대8개로 기존 parser 비용을 제한한다. N4는 digest와 admission UTF-8 검사가 앞서므로 현 범위에서 도달 불가능하다는 한계를 유지하고 기존 worker를 변경하지 않는다. N5 accept 부분: anchor는 # 없이 URL decode된 정확한 문자열이며 중복 거절·정렬 저장한다. 경로는 기존 공식 문서와 동일한 절대 실제 경로를 유지하므로 제안한 상대경로 형식 변경은 채택하지 않는다. N6 accept: 명시적 빈 목록은 거절하고 생략만 허용한다. N7 accept: 모델의 새 범위 밖 링크 추가는 결과 검증에서 실패할 수 있으며 자동 재시도 없음으로 명시한다. N8 accept: 생성된 profile의 정확한 metadata/data literal 차이를 검사한다. 새 native OS 적합성의 입증으로 확대하지 않는다. N9 accept: 집중검사를 전환검사보다 먼저 수행한다.

## 현재 상태와 다음 판단

R1 지적의 범위 내 보완과 아래 최종 검증을 완료했다. Driver가 제한된 source 결과를 제시할 준비가 됐으며 Owner 결과 수락·Work 완료는 아직 아니다. R1 보완본을 다시 외부 검토한 판정은 없고 원 revise 판정과 Driver 처분을 구분한다. 추가 자료의 소비자는 이번 결과 검토와 exact 후보 호환성 검증이며, 해당 판단 종료 시 보존 필요를 재평가한다. 실제 adopter 갱신 권고는 후보 자격 확인 전까지 보류한다.


## 첫 집중 검사의 관측과 보정

일반 모드64사례 중61개가 통과하고 새 테스트3개가 실패/오류였다. source·보호 sentinel은 불변이고123.653초에 정상종료·group 부재를 확인했다. 원 결과는 실패로 보존한다. 하나는 no-body-read mock이 기존 Work snapshot의 프로젝트 digest 읽기까지 금지한 테스트 범위 오류다. 기존 snapshot을 유지하고 새 metadata admission/worker에만 본문 읽기 미추가를 주장하며, 추가 경계와 전체 prepare 무효과를 따로 검사한다. 두 번째는 worker Popen mock이 Host의 선행 Git observer까지 가로챈 것이다. 실제 worker를 띄우지 않는 profile 생성 검사임을 명시하고 그 단계만 관측한다. 세 번째는 이전 후보가 기존 회귀 sandbox의 읽기 경계 밖에 있었다. 정확한 bytes/mode를 대조한 필요한 후보만 현재 RUN 안에 복사하고 정책은 그대로 유지한다. 기존 실행의 실패를 성공으로 덮어쓰거나 timeout을 재시도한 것이 아니다.

실제 원사례의 읽기 전용 첫 시도는 fragment 정보를 입력에 누락해 `unreferenced-or-missing-link-target-anchor`로 안전하게 거절됐다. runtime/worker/authority 효과는0이다. 원 스크립트와 실패를 보존하고 실제 링크의 URL decode된 fragment를 포함한 입력으로 바로잡는다. 이 작업의 성공 주장에는 제품 전체 prepare/실제 모델 실행과 helper·기존 verifier의 in-process 관측을 구분한다.


## R1 요청·정확한 입력·원문

R1은 변경 코드·합성 테스트·관련 계약75,192바이트의 정적 검토다. packet SHA-256은 `5c63fdef4ea16a8882e2851ff1badf5c6e7a1a3025ef4f00c0ddf5f2e737c9e7`이며 Owner의 해당 패킷 전송 승인 뒤 실행했다. 실제 adopter 문서나 자격증명은 포함하지 않았다. 새 Claude 구독 세션 `9007a359-5dd0-40cc-a8ab-1cade59fd664`, 모델 `claude-opus-5-5`, 도구 없음,227.367초 정상종료다. 입력은 검토 시작/종료 때 고정됐고 이후 아래 Driver 보정을 별도 적용했다. R1의 원 판정은 revise이며 이를 accept로 바꾸지 않는다.

# R1 static review: official link metadata entry correction

## Verdict: **revise**, with one needs-user item

I found no unsafe path alias, permission leak, or body-to-model leak in the product code under review. `canonical_existing`, the post-canonical casefold check, `nlink == 1`, the dev/inode de-duplication against documents and other targets, and the exact required-set equality together close the alias paths I could construct. The metadata and anchor split in the profile matches the worker contract. Drift after the capsule leaves the record readable.

However, three R0 dispositions (B1, B5, and the legacy-equality claim) rest on tests that either cannot fail for the stated reason or are not visibly executed. The docs also understate the new preflight narrowing.

## Blocking defects

**R1-1. The compatibility evidence is not a test (B5 and legacy spec/grant equality).**
`exercise_previous_reader_compatibility` has no `test_` prefix, and nothing in this diff calls it. Unittest will not collect it. Both claims depend on it: "EXACT spec/grant equality … in executed compatibility test" and "actual previous reader capsule/status/resolve/restore tested". The packet also says the newP/previousP lifecycle is still pending.

Fix:
- Identify the caller and the run record, or add a `test_…` wrapper.
- An unset `COLVIA_PREVIOUS_OFFICIAL_SOURCE` should be a recorded failure or a skip that blocks the claim, not a silent `KeyError`/error.
- Record the previous source path and its base-`8f68974` identity in the evidence.

Until then, B5 and the equality claim are unproven.

**R1-2. The managed-path test cannot prove B1.**
In `test_link_targets_reject_managed_case_variants_outside_and_directories`, output `a` still links only `linked-0.md`. Every protected path would therefore be refused by `unreferenced-or-missing-link-target-anchor` even if the casefold check were deleted. `assertRaises((ContractError, PolicyRefusal))` hides which check fired.

There is a second weakness: if `.Hrn/format.json` or `Colvia` do not exist as regular files, `canonical_existing` refuses them for an unrelated reason.

Fix:
- For each case, write a link to that path into the output (e.g. `../outside`, `.GIT/config`, `.Hrn/format.json`, `Colvia`, a real subdirectory).
- Assert that the precondition exists.
- Use `assertRaisesRegex(..., 'document-outside-worker')`. For the directory case, use the specific `canonical_existing` refusal.

**R1-3. The bounds tests do not isolate the bounds.**
- `['x']*33` is refused as a duplicate, so removing `len(anchors) <= 32` would not be detected. Use 33 distinct anchors.
- `['x'*513]`, `[False]`, the string value, and `['\x00']` would also be refused by the later required-set check. Use `assertRaisesRegex('link-anchor-list')`.
- In the unreferenced/empty-list test, use the specific codes too: `link-target-list` and `unreferenced-or-missing-link-target-anchor`.

**R1-4. The post-capsule drift test bypasses the Host.**
`test_metadata_drift_blocks_worker_…` calls `h.controller.check_files()` directly and accepts `FileNotFoundError`. That error comes from `path.resolve(strict=True)` in `official_documents.py` (~line 327). This change makes that pre-existing branch live for the first time.

Nothing shows what `Host` dispatch does with an unclassified `FileNotFoundError`:
- whether the worker is refused
- whether no `worker-NNN` slot or admission is created
- whether the journal or status stays consistent

The `ClosedHost` assertion at the end is always true and proves nothing about drift.

Fix: unlink, call `h.dispatch(self.envelope())`, then assert:
- `worker_admitted is False`
- no new slot
- the status the record will show
- that resolve still works

If the Host mishandles the error, wrapping it as `require(..., "link metadata drift")` is a Host-side change that needs owner scope.

**R1-5. The docs understate the preflight narrowing (needs-user).**
`verify(preflight, 'DOC-LINKS')` also reports two kinds of finding anywhere in the full initial output, including inside the edit range:
- `active-html`
- `unapproved-external-link`

So a request to remove inline active HTML or an unapproved external link in range is now refused at prepare. The docs only say "초기 링크가 부족하거나 깨졌으면". Also, a post-write link to an existing metadata target with a new anchor fails verification. The docs mention only new destinations.

Fix:
- List all refusal classes in the docs: missing/out-of-scope local targets, missing anchors, unapproved external links, active HTML, query/absolute links.
- State that new anchors are also unsupported.
- **Needs-user:** have the owner confirm that refusing active-HTML cleanup is within the approved narrowing. If not, filter the preflight findings to link codes only.

## Non-blocking defects (fix or record)

- **Output bytes are not bound to the record.** `link_inputs` re-reads the output with `state.regular` instead of using the bytes already bound in `records`. The preflight `verify` probably catches a mismatch through `file_bytes`. Still, use `need(digest(raw) == output['sha256'])` or pass the bytes in, so the required set comes from the approved bytes.
- **Refusal types are inconsistent.** A non-UTF-8 anchored target raises `UnicodeDecodeError`. Worker `require` failures inside the preflight raise the worker's exception type. Map both to `ContractError` codes such as `link-anchor-encoding` and `initial-document-links-failed`.
- **The 17-target no-read assertion is narrower than it reads.** The `os.open` guard does not cover `builtins.open`, `io.open`, or `Path.read_bytes`. Also, `assertNotIn('METADATA BODY', json.dumps(p))` is vacuous, because the bodies were overwritten before prepare. Either guard `io.open`/`builtins.open` too, or `chmod 000` the targets after prepare and compare metadata ignoring `mode`. Then assert that `'opaque metadata'` is absent from `p`.
- **The profile test checks only the first matching line.** It inspects one `file-read*` line. Assert that the opaque literal appears in no `file-read*` or `file-read-data` rule. Also confirm that no template `subpath` rule covers the temp project, because `/private/var/folders` can mask a production denial. The comment on the `Popen` patch should say it patches the global `subprocess.Popen` for the block.
- **Coverage gaps:**
  - a metadata target in a subdirectory, which exercises `parent_identities`/`parent_fd` for a directory with no document
  - an output in a subdirectory linking `../x.md`
  - `?query` and `/abs` links, checked with the specific code
  - anchored content drift detected by the Host after the capsule, not only by the re-prepare
- **Optional hardening.** Casefolding is adequate on APFS for these ASCII names. A (dev, ino) comparison of each ancestor against `worker_root/.git`, `.hrn`, and `colvia` would avoid relying on string folding.
- **Docs note.** Opaque-target size, mtime, and inode, and anchored-target digests, now land in the capsule, which Git can commit. The existing commit-review warning should name them.

## Evidence sufficiency for a bounded source result

Not sufficient yet:
- R1-1 through R1-3 leave B1, B5, and the legacy-equality claim without a test that fails for the stated reason.
- The optimized-64 run and the lifecycle runs are pending.

Reusing the 61 unchanged results is acceptable, on two conditions: product code is byte-identical since that run (state the digests), and the corrected tests changed only assertions.

The source result should state that the sandboxed worker has never run `validate_link_metadata` natively. This is a real execution risk, not just a qualification label: a profile or `parent_fd` denial would first appear in the post-write DOC-LINKS, leaving an `unknown` record with the effect retained. I recommend gating any adopter execution that uses `link_targets` on a synthetic native sandboxed DOC-LINKS worker run, with no model, covering:
- opaque and anchored targets
- a root and a subdirectory case
- an attempted data read of the opaque target

That remains separate from this source result, as you scoped.

## R1 Driver 처분과 최종 검증 선택

R1-1 defend/accept: compatibility 메서드는 자동 discovery 대상이 아니라 고정 controller가 unittest.loadTestsFromNames에 정확한 ID `test_official_execution.OfficialExecutionTests.exercise_previous_reader_compatibility`를 추가해 실행하는 명시 factory 사례다. 실제 일반 보정3개 실행과 최적화64개 실행의 collection/result/progress에 해당 ID와 PASS가 있다. packet에 caller가 빠져 검토자가 확인할 수 없었던 한계를 수락한다. 필요한 환경변수가 없으면 명시적 assertion failure를 내도록 보완했다. 이전 후보는 공식44파일의 수락된 `26e35d58cd28a49cae6c2342ee354efc16dfd4209a214de545974b28b6680c47`이며 base commit과의 파일 대조도 private 근거에 보존한다. 해시만으로 판독 성공을 주장하지 않는다.

R1-2/R1-3 accept: 관리 대상 경로를 실제 출력에서 참조하고 존재 조건과 정확한 `document-outside-worker`/`path-kind` 코드를 검사한다. Work의 Git topology에서 먼저 실패하지 않도록 추가 link admission 함수를 직접 검사하는 단위 경계를 명시했다. bounds는33개 고유 anchor와 정확한 오류 코드를 검사한다. R1-4 accept: 실제 삭제와 anchor 변경 뒤 Host.dispatch가 worker 예약/slot 없이 거절하고 기록/resolve가 유지되는지 검사한다. 프로젝트 snapshot이 먼저 잡는 경우와 metadata stat의 FileNotFoundError를 주입한 dispatcher 검사도 구분한다. Host 코드를 바꾸지 않는다.

R1-5 revise: 승인된 목적은 초기 링크 scope 보완이므로 active HTML 제거까지 막는 새 제한을 택하지 않는다. 사전검사의 findings 중 active-html만 보류하고 링크 오류는 모두 거절하도록 수정한다. 수정 후 전체 worker verifier는 그대로 active HTML을 거절한다. 이는 검증을 편집 구간으로 축소하거나 사후 검사를 생략하는 변경이 아니다. query/절대 경로/미승인 외부 링크/anchor 거절과 active HTML cleanup의 기존 admission을 테스트하고 설명한다. 이미 files에 포함된 문서와 새 metadata 대상/anchor의 차이도 명시했다. 이 처분으로 더 넓은 cleanup 거절에 대한 새 Owner 결정을 요청하지 않는다.

비차단 지적은 output digest 직접 결속, anchor encoding/worker refusal의 ContractError 분류, io/open/Path 읽기 guard, 모든 profile data rule/상위 subpath 검사, 하위 폴더와 parent-relative 링크, capsule 뒤 anchor drift, Git에 남는 metadata 설명으로 보완한다. ASCII 관리 이름의 casefold에 더해 ancestor inode를 비교하는 선택 hardening은 이번 최소 범위에서 보류한다.

최초 후보 `3e33f936a30a17e8e5363a70bf0dd0150a1a454a63e7dca6ca8e15be09fdd550`와 직전 수락 후보 사이10개 lifecycle 검사는 양쪽 각각 PASS(약505초)했다. R1 보정은 entry의 동일 초기 scope 검사·오류 분류와 shipped 설명/테스트에 한정되며 lifecycle/authority/worker/OS 코드와 schema는 그대로다. 최종 보정에 영향받는 official 두 모듈과 명시 compatibility 사례는 일반/O 전체 집중 묶음을 다시 검사한다. 최종 exact 새 artifact에서는 factory의05(P/Q rollback·기록/clone),07(fresh init·repair 복구),08(혼합 이력 detach 복구)을 두 모드로 검사한다. 나머지7개의 unchanged protocol 위험은 바로 앞10개씩의 고정 근거를 재사용한다. 최종 artifact에서10개 전체를 다시 실행했다는 뜻이 아니며 이름/문서 digest 변경만으로 동일한 old-writer matrix를 반복하지 않는다. 보정 후 새 실패나 uncovered risk가 있으면 그 영향 범위를 다시 평가한다.

실제 link_targets를 사용하는 adopter 실행 전에는 opaque/anchor·root/subdirectory·opaque 본문 거절을 포함한 합성 native sandbox worker 실행이 필요하다는 R1 권고를 수락한다. 이번 source 결과와 별도이며 현재 그 검증은 미수행이다. 실제 Worker validate_link_metadata는 이 작업에서 in-process만 실행했고 생성 profile은 정적으로 확인했다. 최초 실제 실행이 문서 수정 뒤 거절되어 unknown/effect-retained가 될 수 있으므로 그 native 증거 없이는 adopter 실행을 권고하지 않는다. 현재 scope의 source 검토·보정·집중 검증 결과를 먼저 제시하며 제품/OS 자격을 올리지 않는다.


## 최종 실행 결과와 남은 경계 — 2026-10-30

최종 후보는 `official-execution-1`의 `86f03156d06edd425dba454121aae30adf3e458dabd877ac6db578de6297d28a`다. 직전 수락 후보 `26e35d58…`와의 정확한 payload 비교·준비를 유지했다. 코드·OS 정책·기존 실행 이력은 최종 검증 중 불변이었다.

- 공식 admission/execution 및 명시 compatibility의69개 고유 사례를 일반/최적화 각각 확인했다. 양쪽 최초69실행은68통과·새 테스트의 복구폴더 기대값1실패였으며 원본은 그대로 유지한다. `original-outputs`는 필수 원문 복구 폴더이므로 없애지 않고 `worker-*` slot의 부재만 검사하도록 바로잡았다. profile의 PYROOT subpath 비교도 명시했다. 바뀐 메서드2개만 두 모드에서 다시 실행해 모두 통과했다. 나머지67개 메서드와 제품 바이트가 같음을 확인했다. 실패 실행을 전체 PASS로 바꾸거나 보정 후69개를 한 번에 다시 실행했다고 주장하지 않는다.
- 보정 전 고정 후보의10개 전환 factory는 모드별 모두 통과했다. 최종 exact 후보의05/07/08 세 사례도 양쪽에서 통과했다. 이 조합은 fresh 설치·P/Q update/rollback·기록/clone 판독·repair·혼합 이력 detach와 복구를 포함하며, unchanged old-writer/전환 프로토콜의 나머지7개는 앞선 고정 근거를 재사용했다.
- 모든 회귀 controller는 기존 credential-free/network-denied 정책 안에서 자연 종료했으며 소스·보호 sentinel 불변과 process group 부재를 확인했다. native Windows 또는 계정 모델 실행을 이 결과로 주장하지 않는다.
- 원사례 문서를 변경하지 않은 in-process link helper/기존 verifier에서17개 metadata와1개 anchor 본문 근거가 통과했다. 추가 본문을 모델에 보내지 않았고 새 runtime Work/intent, 실제 adopter 변경, 제품 account/model 호출은0이다. 이것은 실제 설치된 prepare 또는 sandbox worker 실증이 아니다.

R0/R1의 요청·입력 identity·원문·실행 결과와 Driver 보정을 분리해 보존했다. R1 보완본의 별도 재검토는 미수행이며 Driver 집중 검증으로 지적 처분을 확인했다. 원 판정은 revise다. R1-5의 needs-user는 더 넓은 active-HTML cleanup 거절을 선택하지 않고 사전검사를 링크 오류로 한정하는 대안으로 해소했다. 실제 결과 수락은 Owner에게 남는다.

전체 regression을 새로 실행하지 않았으며 기존 R3의 알려진 실패/Windows 제외를 성공으로 올리지 않는다. 새 metadata의 native OS 실행·opaque 본문 거절은 미검증이다. 실제 adopter 실행 전 이 합성 native 검증이 필요하다. OS 정책 확장, 실제 adopter 설치·모델 실증, Git commit/push/PR/merge는 이번 범위에서 수행하지 않았다.

일반 영향: 기존 성공한 no-metadata 요청의 spec/grant와 이전 capsule 판독을 유지하면서, 추가 로컬 링크 근거가 필요한 문서는 명시된 metadata 입력을 제공할 수 있게 됐다. 초기 link 오류가 있는 요청은 수정 전에 거절한다. 현재는 즉시 adopter update/실행을 권고하지 않는다. 설치 상태를 이번 단계에서 새로 검증하지 않았으며, 결과 수락 뒤 exact 후보의 native 검증과 실제 대상의 보존·update 결정을 별도로 준비해야 한다.

변경6파일과 고정 후보·원 review/실패/검증 자료는 Owner 결과 판단, Git 통합 또는 인계를 위한 복구 소비가 있어 보존한다. 재사용하는 고정 전환 artifact와 traces는 그 근거 확인이 끝날 때 재평가한다. 임시 socket binding과 재생 가능한 Python bytecode만 소유·종료·빈 경로를 확인한 뒤 정리했다. 소스/worktree의 활성 경로는 유지한다.


## Owner Source Result Acceptance — 2026-10-30

Owner가 직전 완료 보고에 대해 “승인”하여 위 제한된 소스 결과를 수락했다. 수락 대상은 최종 후보 `86f03156d06edd425dba454121aae30adf3e458dabd877ac6db578de6297d28a`와 위에 구분한 검증 근거·한계다. R1 원판정 revise와 이후 Driver 보정·검증, 수정본 독립 재검토 미수행은 그대로 유지한다. 앞선 수락 대기 문구는 당시의 역사적 상태이며 현재 소스 결과 수락은 완료됐다.

새 metadata의 native sandbox 검증, 실제 adopter 적용, 계정 모델 실증, Git commit·push·PR·merge는 이 수락에 포함되지 않는다. 실제 적용 전 합성 opaque/anchor 대상의 root/subdirectory 링크 검증과 opaque 본문 읽기 차단 확인이 남아 있다. 변경 파일과 복구 근거는 미커밋 소스의 통합·인계 및 해당 검증을 위해 계속 보존하며, 통합과 남은 검증 처분 후 보존 필요를 재평가한다.
