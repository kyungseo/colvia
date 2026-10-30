# Official Guard Selection Across Init History

## Scope And Authorization

Owner가 2026-10-30 현재 공식 설치의 쓰기 보호 정책 선택 보정, 집중 검증, 승인된 기존 프로젝트 반영과 이미 성공한 문서 결과 제출 재개를 승인했다. 새 모델/Reviewer 호출, 결과 자동 수락과 Git 작업은 제외했다. 최초 설치가 `planning-1`이고 현재 검증된 설치가 `official-execution-1`인 대상에서, 종료된 공식 실행 기록이 생긴 뒤 일반 Work 게시가 `execution records require the official window`로 거절된 실제 관측이 입력이다. 기존 결과와 오류·시도 기록은 private 실행 근거에 보존한다.

시작 source commit은 `b2a694ff8b1b54b1d3786148b458c8110ceec2ca`이며 clean 상태였다. 이 source-only 기록은 runtime Work를 만들지 않는다. 변경은 `workspace._guard_runtime_window`, 그 경계의 합성 회귀검사와 이 작업의 기록/index다. 실제 기존 프로젝트 문서나 식별정보는 source에 포함하지 않는다.

## Change And Safety Boundary

최초 init 기록은 정상 갱신 후에도 유지된다. 기존 코드는 최초 init이 continuation-1일 때만 현재 official binding의 정책 hint를 선택해 이전 POSIX 계열에서 갱신된 대상을 놓쳤다. 같은 더 엄격한 official barrier 선택을 기존 POSIX init 계열에 적용한다. 이 hint는 권한 증명이 아니다. 실제 현재 binding/receipt 검증, lock 안 window 재확인과 미종료 capsule 거절은 그대로이며 windows-2·detach 정책과 OS 권한을 바꾸지 않는다.

## Evidence Selection And Limit

누적 변경은 해당 정책 선택 분기다. 기존 source/최종86f031 후보의 metadata, worker, RPC, authority schema 코드는 유지한다. 새 selector 역사 행렬, 미종료/종료 capsule, 거짓 binding hint의 실제 verifier 거절, 잘못된 JSON 보존, lock 중 window drift와 기존 workspace/official 실행 사례를 일반·최적화로 실행한다. 이 합성 fixture는 최초 이력 선택과 쓰기 보호의 단위 증거이며 실제 upgrade history나 모델 성공 증거로 올리지 않는다. exact 새 후보의 same-window lifecycle 사례와 승인된 실제 대상의 update/Work publication을 별도 확인한다.

이전 전체 회귀의 알려진 실패/Windows 제외는 그대로이고, 집중 검사를 새로운 전체 PASS로 부르지 않는다. 새 모델 호출을 제외한 Owner 승인에 따라 이번 보정의 새 R0/R1 독립 검토는 수행하지 않는다. Driver의 코드 확인과 실행 검증으로 그 검토를 수행했다고 주장하지 않는다. Source 결과 수락과 일반 지원성은 별도다.

예상20–30분은 구현·집중 검증·대상 반영·결과 준비를 포함한 판단 추정이다. 알려진 Owner 대기를 제외하고 병행시간은 한 번 계산한다. 누적 착수540분·중단550분을 적용한다. 시간초과·새 실패·drift는 보존하고 무단 재시도하지 않는다. 현재 상태는 실행 중이며 source 결과 수락 전이다.


## Execution Result And Remaining Decisions

최종 후보는 `official-execution-1`의 `0fe20f09626e7ea0c6aa1950a2f016507bf21954d56e6a78cb89a59c0baf8dcd`다. 직전 후보86f03156과 비교해 managed payload에서는 `src/hv2ref/workspace.py` 한 파일만 변경됐다. 모델·worker·RPC·문서 검증기와 OS 정책은 그대로다.

일반·parent-optimized 집중 검사 각각106개 중105개는 처음 실행에서 통과했다. 새 fixture의 journal 생성 누락으로1개가 검사 본문 전에 오류를 냈으며 원 로그를 보존했다. 기존 EffectJournal의 create=True를 지정하도록 fixture만 보정한 뒤 해당1개를 양쪽에서 재검증해 통과했다. 다른105개와 제품 바이트의 불변을 확인했으며 첫 실패를 전체 PASS로 고쳐 쓰지 않는다. 새 후보의 factory05/07/08도 두 모드에서 각각 통과했다. 이는 P/Q update·rollback·기록/clone 판독, fresh init·repair 복구, 혼합 이력 detach 복구와 capsule 보존의 집중 증거다. 모든 실행은 기존 credential-free/network-denied 정책에서 자연 종료했고 process group 부재와 보호 sentinel 불변을 확인했다.

Owner가 승인한 기존 프로젝트에 exact 새 후보를 적용했다. 설치47개 경로만 바뀌었고 기존 문서 결과 manifest와 authority/capsule의 bytes·mode가 유지됐다. 이어 실제 설치 CLI에서 기존 문서 결과를 게시하고 Work를 review 상태로 전환했으며, paired Work/confirmation view에서 whole result·현재 binding·참조·선택 일치를 확인했다. 새 모델 호출은0이다. 기존 모델 실행 성공을 새 후보에서 재실행했다고 주장하지 않는다.

이 소스 결과의 새 독립 R0/R1 검토는 수행하지 않았다. 이전 전체 회귀의 알려진 실패/Windows 제외와 일반 지원성 미검증을 유지한다. Source 결과 수락, 대상 결과의 Owner 수락·Core 완료, Git commit/push/PR/merge는 수행하지 않았다. Source 변경과 실제 설치 변경은 미커밋이며 Owner의 결과 처분과 별도 Git 결정이 남아 있다.

Adopter 영향은 정상 공식 설치로 갱신한 오래된 init 이력의 일반 writer가 종료된 실행 기록 때문에 잘못 거절되는 문제의 보정이다. 같은 증상이 확인된 설치에는 이 exact 후보의 적용을 검토할 수 있다. 모든 과거 init의 실제 migration이나 다른 OS·일반 사용성을 자격화한 것은 아니다. 새 source·candidate·실행/오류 로그는 Owner 결과 처분과 후속 Git 판단을 위해 보존한다. 전용 worktree는 그 근접 후속 작업에 재사용하며 처분 뒤 cleanup 조건을 다시 확인한다.


## Owner Result Acceptance And Source Completion — 2026-10-30

Owner가 소스 보정과 기존 문서 결과의 두 수락 대상을 명시한 제안에 “승인”했다. 소스 수락 대상은 후보 `0fe20f09626e7ea0c6aa1950a2f016507bf21954d56e6a78cb89a59c0baf8dcd`와 위 실행 결과·제한이다. 새 독립 R0/R1 미수행, 최초 fixture 오류와 보정 후 재검증, 기존 전체 회귀의 실패/Windows 제외는 그대로 유지한다. 해당 bounded source 작업은 Owner 결과 수락 후 Done으로 정리한다. 앞선 수락 대기 문구는 당시 상태다.

실제 대상의 결과 수락은 해당 프로젝트의 exact ticket으로 별도 반영한다. 이번 결정은 커밋 범위·메시지 준비까지 포함하며 commit·push·PR·merge는 승인하지 않는다. 변경 소스와 복구 근거는 근접 Git 보존 판단이 남아 있어 유지한다.
