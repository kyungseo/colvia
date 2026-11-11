# Focused Diagnostics Result

2026-11-06. 승인된 시간 분해와 index 독립 확인 결과.

## Measured Breakdown

기존 합성 자료만 사용했다. 첫 계측은 `__main__.__file__`가 계측 도구를 가리켜 제품의 실행기 identity 검사에서 거부됐다. 원 실패는 보존했고, Owner가 수정 계측1회를 승인한 뒤 `runpy(..., run_name="__main__")`로 실제 실행기 진입을 유지한 r2가 완료됐다. 제품 guard를 끄거나 source를 수정하지 않았다.

단위 초. 각 조합 정상 실행1회와 계측1회다. 기존4회 중앙값을 대체하는 성능 benchmark가 아니다. 선택한 경계 함수의 중첩 시간을 차감해 exclusive category 합계+기타=main wall이 된다. graph의 inclusive 합계는 중첩되므로 합산하지 않는다.

| 사례 / 명령 | 정상 process | 계측 main | graph | topology | content | runtime binding | 기타 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| scale-f100 / ordinary | 2.522 | 2.401 | 1.165 | 1.134 | 0.000 | 0.085 | 0.016 |
| scale-f100 / view | 4.766 | 4.790 | 2.997 | 1.465 | 0.100 | 0.000 | 0.228 |
| scale-f1000 / ordinary | 2.583 | 2.615 | 1.922 | 0.596 | 0.000 | 0.075 | 0.022 |
| scale-f1000 / view | 5.316 | 5.053 | 3.964 | 0.718 | 0.141 | 0.000 | 0.230 |

main 전에 정확한 설치 payload를 확인해 import하는 계측 준비가 있다. binding 약0.0015초, import 약0.061초로 관측됐으나 이것을 일반 launcher의 전체 시작 비용이라고 하지 않는다. 계측 main은 source launcher 검사를 다시 수행한다. 실제 managed Python의 runtime 해시 비용은 이번 범위에서 측정하지 않았다. 두 원 fixture의 프로젝트 bytes와 Git index hash는 전후 같다.

분석: 선택 Work 조회에서 graph와 반복 topology 비용이 크고 content snapshot은0.10–0.14초였다. 100파일/69Work View에서 topology435회, graph 경계418회, 1,000파일/30Work View에서 topology201회, graph184회였다. graph 경계 횟수는 서로 다른 Work 수가 아니며 중첩 호출을 포함한다. 단일 명령 context 재사용과 선택 Work dependency closure 조회를 먼저 구현한다. checkpoint hash만 보는 검증 생략이나 데이터 삭제를 성능 대책으로 쓰지 않는다.

## Independent Index Check

원 실패 fixture는 건드리지 않았다. 새6파일 합성 Git 프로젝트에서 원 index를 먼저 파일로 보존하고 단계별 사본을 남겼다.

- Core plan→수락: index bytes 그대로.
- git show: 그대로.
- git write-tree: index bytes 변경.43개 entry의 bytes hash와 entry 수·version은 같다. TREE extension만404→443bytes로 바뀌었고 index SHA-1 checksum은 전후 모두 유효하다. 그 외 extension은 같다.
- git diff-tree: write-tree 이후 index 그대로.
- 후보에는 승인한 파일과 무관한 기존 staged 파일이 함께 있고, 승인 파일의 staged 내용은 수락한 working-tree 내용과 다르다.

따라서 원 셀과 같은 현상의 원인 후보였던 TREE cache 변경을 새 독립 사례에서 재현했다. 원 실패 시점의 최초 index bytes를 소급 복원한 것은 아니다. Core 수락 자체의 index 변경은 재현되지 않았다. 공개 Git 후보 관측에는 사용자 index를 읽기 전용으로 취급하고, tree 생성이 필요하면 별도 private index 사본에서 실행해 원 index bytes 불변을 확인해야 한다.

## Disposition

시간 분해와 index 독립 확인은 완료. 기존 실패·미측정 managed 경계는 그대로 기록한다. 새로운 guard/index/본문 설계가 구현됐다는 뜻은 아니다. 다음은 구조 리뷰 뒤 승인 범위 구현이다. 실행 로그와 고정 진단 스크립트는 저장소 밖 유지보수자 비공개 근거에 보존한다. 이 문서의 재현 조건·관측·한계는 그 경로 없이도 읽을 수 있어야 한다. 자동 추가 재시도 없음.
