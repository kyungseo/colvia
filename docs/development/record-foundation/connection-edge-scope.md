<a id="연결-경계와-첫-공개-범위" name="연결-경계와-첫-공개-범위"></a>

# Project connection boundaries and first-release scope

상태: 2026-11-06 Driver 범위 제안. Owner는 추가 의견을 검토하되 모든 사례를 자동 처리하지 않고, 필요한 보호와 확장 경계만 지금 두도록 요청했다. 제품 구현이나 지원 검증 완료를 뜻하지 않는다. 진행 중인 R3b 입력은 수정하지 않는다. 결과가 도착하면 기존 [상세 계약](implementation-contracts.md), [구현 순서](implementation-plan.md), [검증표](validation.md)에 필요한 부분만 합친다. 진행 기록은 [기존 Work](../FEAT-20261106-002-record-foundation.md)가 소유한다.

English reference, 2026-11-19. The [original wording at the translation base](https://github.com/kyungseo/colvia/blob/eed271ad5aa665f0002c9eded69d82f224da9ce0/docs/development/record-foundation/connection-edge-scope.md) governs the dated decisions and evidence. The Owner [accepted this English reference](../document-language-result-review.md#owner-acceptance).

<a id="판단-기준" name="판단-기준"></a>

## Criteria for the first release

The first release must preserve records, prevent acceptance of the wrong result and support the promised ordinary Work flow. Detect uncommon transitions, preserve the affected state and explain the next step. The first release does not handle these transitions automatically. Retain the agreed scope for Git and non-Git folders, linked and registered nested app worktrees, the managed launcher, updates, recovery and disconnection.

추가 Claude 의견은 고정 입력을 가진 독립 리뷰가 아닌 보충 의견으로 받았다. 경로·기준점 쟁점은 유효하지만 세 기능의 추가 비용 3–6시간은 실측이 아니며 채택하지 않는다. 특히 기준점 갱신은 승인·검사·중단 복구 의미까지 걸려 단순한 안내 수정으로 계산할 수 없다.

<a id="첫-공개와-후속-기능" name="첫-공개와-후속-기능"></a>

## First-release recommendations and follow-ups

| Case | Recommended first-release behavior | Follow-up candidate |
| --- | --- | --- |
| Subdirectory of a monorepo | Connect at the Git workspace root. For a command inside a connected root, resolve the verified root and show the target and Work scope. If someone requests an independent subproject, explain how to connect the root and scope the Work to the subdirectory. Never silently broaden the scope. | Independent subprojects and the relationship between nested records and scopes. First establish demand and the cost of observing the entire root. |
| Git status of a connected folder changes | Detect the change and stop writing under the old binding. Preserve the records and bodies in OS data storage. Allow historical queries and export without claiming the folder still matches. Reconnect explicitly or start a new connection with the old records identifiable. Preserve an active Work's baseline and state. | An automatic transition tool could carry the same logical project and its active Work forward using the preservation and identity rules for explicit reconnection. |
| Files or the branch change during a Work | Compare files, policy, identity and check assumptions. Pause submission or acceptance if the change breaks scope protection or a check prerequisite. Show the difference and next action. Preserve current files and earlier evidence. Continue through the existing approval path, or have the user review a new baseline and continue in a new Work. Record the old Work as unfinished or blocked. | A separate decision to change the baseline within the same Work. Disjoint paths alone cannot establish safety. |
| External drives or unusual filesystems | Check workspace observation and file identity separately from the safety of the authoritative database. Refuse writes and explain the missing guarantee when it cannot be established. An external project folder does not imply an external database. | Qualify additional filesystems and alternative identity methods before claiming support. |

Each registered linked or app worktree has its own workspace root and can share the project authority. Root discovery must respect foreign repositories and unregistered nested boundaries. If a non-Git subfolder has a connected ancestor, do not silently create an independent nested connection.

A missing Git executable or denied access to `.git` calls for a different diagnosis from removal of Git metadata. Losing a locator must never replace history with a new empty authority. When reconnection cannot prove the old identity, permit only record preservation and an explicit new connection. Revalidate earlier bindings in other sessions or linked worktrees.

When external changes already prevent submission, asking the user to submit the old Work first leaves them stuck. Preserve unsubmitted files. Do not overwrite user files or replace the baseline to resolve the change. Do not run checkout, reset or stash automatically. Unrecorded earlier contents may be unrecoverable. Starting a new Work does not verify or accept an out-of-scope change from the old one.

<a id="지금-유지할-확장-경계" name="지금-유지할-확장-경계"></a>

## Boundaries for future extensions

- Keep project identity, workspace identity, invocation location and approved Work paths distinct. Independent subfolder connections and a namespace framework are outside this design.
- Git and non-Git observation adapters identify the connection kind, observation policy and binding generation. Preserve data across connection changes and reject stale-generation writes by checking expected state.
- Retain baselines and observations as immutable references, separate from results and acceptance. A future baseline change would add a decision and observation while preserving earlier facts. Use the existing capability/version contract for compatibility. Defer new enums and migration machinery until their semantics are defined.
- A difference query reports observations. Do not attribute unexplained changes to a collaborator. A future baseline change must account for input, settings and check dependencies, invalidated check and review receipts, interruptions and duplicate requests as well as approval.
- The filesystem port identifies required identity, locking and sync guarantees and explains when they are unavailable. Verify SQLite's locking and durability at the actual database location. [SQLite filesystem assumptions](https://www.sqlite.org/howtocorrupt.html)

Use the existing C1/C3/C5 boundaries for identity, expected state and observation. Specify the format for a baseline-change record when that feature is designed. The first public format must allow capability and version extensions that preserve published history and let older readers refuse safely.

<a id="필요한-최소-검사" name="필요한-최소-검사"></a>

## Minimum verification cases

Reuse the C1/C5, D1/D7 and scope checks. These additional cases were planned and had not been run in this design exercise.

1. Distinguish running inside a connected root from requesting an independent subfolder connection. Identify linked and app roots separately from foreign nested roots.
2. Distinguish Git initialization in a connected non-Git folder, loss of the Git locator and an unavailable Git executable. Verify record and body retention, refusal of stale-session writes and actionable recovery guidance.
3. Cover changes inside and outside scope and changes to check dependencies even at other paths. Verify that the baseline stays intact and review stays pending. For Git metadata changes with identical file contents, determine whether a contract prerequisite actually changed.
4. Refuse safely when file identity or observation cannot be established. Preserve user files and do not misreport the authority as corrupt. A physical external-drive matrix was outside this design correction.

“그 외 모든 사례는 처리됐다”는 결론은 채택하지 않는다. 회사 정책, 기기 이동, 프로젝트 삭제, 오랜만의 갱신 등은 계약에서 다루는 조건과 실제 qualification 상태를 기존 검증표로 구별한다. 새 기능이나 전수 환경 시험으로 범위를 늘리지는 않는다.

## 승인된 일반 재수정 예외

다른 Work가 같은 작업 폴더에 추가한 파일을 이미 제출했고 현재 내용도 일치하면, 기존 Work의 재수정 제출에서 그 근거를 대조할 수 있다. [재수정 계약](rework-context.md)의 제한된 예외이며, 원래 기준점은 보존한다. 출처가 불명확한 변경·기존 파일의 범위 밖 수정이나 삭제·일반 Git 외부 변경의 기준점 갱신은 계속 후속 범위로 남는다.


## 2026-11-14 승인된 중첩 이동 보호 보정

이번 소스 보정은 일반 폴더 이동을 자동으로 재연결하지 않는다. 이동 또는 복사 후 경로가 달라지면 기존 식별·경로 비교를 유지하고, 원래 위치와 현재 파일을 보존하도록 안내한다. 같은 경로의 macOS 식별 재검증이나 복원된 instance의 재연결을 일반 이동 절차로 안내하지 않는다.

독립 프로젝트 A를 B 안으로 옮긴 경우 A의 입력 폴더를 먼저 검사하므로 Git이 B를 실행 root로 선택하기 전에 상위 연결 표식을 거부할 수 있다. B의 일반 관측은 기존 한도 내 파일 열거에서 중첩 `.colvia-link.json`을 발견하면 중단한다. 무시 규칙으로 숨기거나, 파일·디렉터리·링크 표식의 이름 대소문자를 바꿔도 일반 파일로 수집하지 않는다. 오류는 실행 폴더와 충돌 폴더, 겹치지 않는 위치로 옮긴 뒤 상태를 확인할 행동을 제공한다. DB나 locator 수동 편집·삭제를 요구하지 않는다.

검증된 같은 프로젝트의 nested worktree는 기존 구조 증명으로 제외한다. 기존 gitlink는 불투명한 commit 참조로만 취급하며 내부 파일을 일반 Work의 파일로 수집하지 않는다. 이는 독립 프로젝트 병합 허용이 아니다. 유효하지 않은 표식도 임의로 무시하지 않으므로 참고용 clone이나 연결된 사본은 관측 root 밖에 둔다.

관측 전후와 제출 재검사에서 경계를 다시 확인한다. 파일시스템과 SQLite를 한 트랜잭션으로 잠그지는 않으므로 마지막 관측과 게시 사이의 외부 파일 변경을 완전히 배제한다고 주장하지 않는다. 실제 Windows 설치본 검증은 별도 후보 적용 승인 뒤 진행한다.

일반 프로젝트의 하위 폴더에서 실행한 경우에는 상위 프로젝트로 돌아가도록 안내하고, 실제 독립 프로젝트의 중첩 이동이라고 단정하지 않는다. 상위 경계를 확인할 수 없는 오류도 연결 생성 오류와 구분한다. Git root와 일반 폴더 연결 표식이 함께 있으면 한쪽을 자동 선택하거나 일반 파일로 흡수하지 않는다.


## 2026-11-16 · 일반 폴더에서 Git으로 전환하는 후속 후보

위 표의 ‘연결 뒤 Git 유무가 바뀜’ 가운데 일반 폴더를 Git 프로젝트로 전환하는 경로를 [첫 Preview 이후 P1](../plain-to-git-project-conversion-followup.md#owner-계획-결정--2026-11-16)로 등록했다. 기존 프로젝트와 기록을 이어 가는 최소 전환을 검토하며, 첫 Preview의 연결 경계는 이 등록의 적용 대상에서 제외한다.
