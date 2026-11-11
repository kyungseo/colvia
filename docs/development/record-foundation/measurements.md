# Verification Result

Status: 승인된 합성 측정 종료, 새 형식은 미구현. 2026-11-06. 이 결과는 현재 기록 방식의 기준값과 설계 반례다. 공개 지원 한도나 새 형식의 성능을 입증하지 않는다.

## Conclusion

공개 전 기록 위치·본문 보존·누적 판독 방식을 함께 정비할 근거가 확인됐다. 파일 수만 늘어나는 문제가 아니다. 파일100개에서도 Work가30→69개로 늘 때 선택한 Work 조회가2.65→5.30초로 늘었고, 모델 호출 없는 일반 Work6단계도 길어졌다. branch에 추적된 기록은 branch 전환과 함께 이전 상태로 돌아갔다. 사용자 Git commit만으로 모든 검토 당시 본문이 보존되지는 않았다.

권장안은 공용 authority + workspace별 수락 결과 + 제출 변경 전후 본문 보존 + 공유 불변 객체/명시적 transaction + 별도 Git 통합이다. 구조·archive·동시성은 [구조 초안](structure.md), 실제 구현 조건은 [명세](design.md)에 연결한다.

## Scope And Evidence

- 기준 source: the prepared Colvia source input, HEAD `37ec0752fd7b1854c4f2765243826f2a73e57a6a` + 고정한 미커밋 보강. 준비한30개 관리 파일의 hash/mode를 보존했다.
- 이 Mac의 CPython3.14.7, continuation-1 source 경로, 별도 HOME/Git 설정, 네트워크 차단·fixture 내부 쓰기만 허용한 실행이다. 실제 Core plan/approve/start/submit/review/accept를 사용했고 성공한 권위 이력을 가짜 JSON으로 만들지 않았다.
- 합성 Markdown 작은 변경을 반복했다. 사용자 판단·모델 대기·본문 작성 시간은 없다. 명령 시간에는 CLI 시작과 Core I/O가 들어간다. 이 측정에서는 내부 함수별 비용을 분해하지 않았다. 후속 [집중 진단](diagnostics.md)에서 별도로 확인했다.
- 조회는 initial1+warm3의 중앙값이다. initial을 OS cold-cache라 하지 않는다. 같은 호스트의 일반 background 부하는 통제하지 않았다.
- 원 로그·분석 JSON·마감 대조·실패 fixture·명령은 저장소 밖 유지보수자 비공개 근거에 보존한다. 이 문서의 조건·수치·한계가 제품 소유 요약이며, 비공개 로그 경로를 저장소 파일로 요구하지 않는다.
- 준비 시작16:48:52KST, 측정 queue 종료18:28:27KST. 문서 분석은 이후 수행했다. 누적6시간 상한 내이며 모델·VM·네트워크·실제 설치·제품 수정·실제 저장소 commit은0회다. Git commit/pack은 승인된 합성 fixture에만 있다.

## Scale Results

시간 단위는 초, 기록 bytes는 `.hrn/work`의 raw 합계다. intent·payload·Git을 포함한 총용량과 같지 않다.

| 경로 / 파일 / 완료 Work | Work bytes | 전체 View | 선택 Work View | ordinary status | 첫→마지막 Work6단계 |
| --- | ---: | ---: | ---: | ---: | ---: |
| Git / 100 / 30 | 2,567,040 | 2.473 | 2.654 | 1.248 | 6.44 → 28.95 |
| Git / 100 / 69 | 5,904,192 | 4.900 | 5.296 | 2.590 | 30.24 → 60.23 |
| Git / 1,000 / 30 | 23,087,430 | 5.415 | 5.632 | 2.799 | 7.93 → 45.01 |
| Git / 3,000 / 30 | 68,687,430 | 11.512 | 12.073 | 5.822 | 11.08 → 73.65 |
| non-Git / 100 / 30 | 2,569,770 | 1.961 | 1.913 | 0.812 | 3.84 → 14.75 |

69Work 행의 첫6단계는 연장 구간의31번째 Work다. 최초 Work는6.44초였다. 여섯 단계의 합은 명령별 실제 wall time이며 사람 대화 전체 시간이 아니다.

100파일의100Work 목표는 생성30분 상한 전 안전한 완료 지점인69Work에서 멈췄다. 100/300Work 통과로 기록하지 않았고300은 시작하지 않았다. 1,000파일은30Work에서 조회 목표를 넘고 더 큰 이력을 만들기 위한 예산이 부족해 증량하지 않았다. 3,000파일30Work는 완료했다. 이는 제품 최대치가 아닌 이번 실행 한도다. 기존 로컬 목표 중앙값5초/최대10초는 설계 진단 기준이며 공개 SLA가 아니다.

Git pack은 프로젝트 전체의 initial·측정 checkpoint commit에 대한 값이다: 100/30은539KiB, 100/69는738KiB, 1,000/30은1,197KiB, 3,000/30은2,586KiB. raw Work 합계를 Git 이력 크기로 외삽하지 않는다. st_blocks 기반 할당량은 APFS 공유 extent의 고유 물리 사용량과 같지 않다.

## Correctness And Stopped Cell

| 사례 | 결과 | 해석/남은 경계 |
| --- | --- | --- |
| primary·sibling worktree·branch 전환 | primary completed, 복사된 sibling은 review 이력. ordinary status/쓰기 exit65로 linked-worktree 거부. 일반 View는 환경 경고와 authoritative_control=False를 표시하며 copied review를 보여줌. primary를 옛 branch로 바꾸면 review, 원 branch 복귀 후 completed | 기록 손상은 아니다. branch 사본과 프로젝트 공용 최신 정본을 구별할 필요가 재현됨. 조회 bytes 불변 |
| 부분 staging·범위 밖 staged | ordinary 수락 직후 index bytes 불변 확인. staged 대상 내용은 수락 내용과 다르고, commit 후보에는 무관한 staged 파일도 존재함을 확인 | 마지막 assertion이 실패해 셀은 중단. 그 전에 실행한 git write-tree의 cache-tree 변경이 원인 후보이나 초기 index 사본을 파일로 남기지 않아 확정 못함. 제품 index 손상이나 전체 통과로 표시하지 않음; 재시도 없음 |
| 한 Work에30회 제출 | 오래된 receipt 거부·거부 후 bytes 불변, 최신 결과 수락. 시작 시 보존한 불변11기록 유지 | 30번째 조회 중앙값: 전체0.995, 선택1.110, status0.762초. 신규30Work와 명령 구성이 달라 전체 작업시간 직접 비교 금지 |
| non-Git100파일30Work | 기존 첫 Work completed, 불변13기록 보존, 조회 bytes 불변 | Git 없이도 수락 기록 의미 유지. 과거 본문 보존을 입증하는 시험은 아님 |
| 합성 배포물5회 갱신 | Git/non-Git 각각 initial+5=6개 release. 원 불변13기록·수락 결과 유지 | 문서 한 줄만 바꾼 합성 release. 실제 관리 도구·플랫폼 갱신 자격과 다름 |

## Storage And Retention

3,000파일30Work의60개 manifest에는 tree가120회 들어 있어 canonical tree bytes만64,106,040이다. 서로 다른 tree31개로 세면16,560,727bytes, entry 값은3,030종이다. 동일 값의 반복 저장이 크다는 진단이며 새 형식의 실제 공간·성능 개선 수치는 아니다.

6개 합성 release의 payload는180파일, raw7,214,954bytes다. 서로 다른 내용35종의 합은1,208,689bytes다. Git pack376KiB와도 구별한다. 실제 release가 코드를 얼마나 바꾸는지는 이 사례로 예측하지 않는다.

1,000파일 사례에서 첫 Work의 이전 본문은 현재 파일에도, `.hrn`의 그대로인 본문에도, 해당 SHA-1 Git blob에도 없었다. initial+30번째 batch commit 정책의 결과다. 모든 사용자 저장소에서 사라진다는 주장이 아니라, 사용자 commit 주기와 독립적인 제출 본문 보존이 필요하다는 반례다. hash와 수락 기록만으로 옛 내용을 복원할 수는 없다.

## Static Baseline And New Inputs

구조 기준값(원본 실행 근거에 보존)은 hv2ref Python·adapter SKILL·manual Markdown·지정 진입/레퍼런스56파일, 19,343줄, 1,450,583bytes를 대상으로 한다. 전체 repo 크기가 아니다. AGENTS56줄, CLAUDE14줄, colvia-work adapter253줄, docs/README577줄, work.py2,289줄, workspace.py806줄이다. 빈 줄·주석 포함 splitlines, exact literal 빈도와 SHA-256을 함께 남겼다. 실제 새 세션 읽기량이나 AST 분기 수를 측정한 것은 아니다.

D1/D7 데스크톱 결과는 Owner/Claude 전달 근거이며 이번 Driver 재현이 아니다. 기존 측정 queue를 변경하지 않았다. 구조 제안S1–S11은 측정 종료 뒤의 설계 처분에 반영했고 제품을 고치거나 새 경쟁 시험을 실행하지 않았다.

## Follow-up And Evidence Boundary

시간 분해와 index 독립 확인은 이후 [집중 진단](diagnostics.md)에서 완료했다. 원 실패를 소급 통과로 변경하지 않는다. 새 형식, 공용 위치, 갱신, 경쟁, D1/D7 수정과 실제 배포·호스트 검증은 아직 미구현/미실행이며 기존 수치를 그 성공으로 사용하지 않는다.

이 문서는 익명 합성 측정의 설계 근거다. 원 실행 입력·로그·실패 fixture와 상세 source/payload 식별자는 유지보수자의 검증 근거에 보존한다. 이 요약만으로 후속 후보 qualification을 선언하지 않는다. 공개 재현이 필요하면 개인정보 없는 고정 입력과 실행기를 별도로 선별한다. 현재 결과에 모델 시간·실사용 판단 시간·새 형식 성능을 추가로 추정하지 않는다.
