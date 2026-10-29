# Windows detach 성능 개선 후속

State: Deferred / Unselected. 현재 Windows 본 검증의 선행 조건이 아니다.

## Owner Planning Authorization — 2026-10-28

Owner는 detach가 자주 실행되는 작업이 아니며 약 2분 소요만으로 문제로 보지 않는다고 확인했다. 정상 동작을 검증한 뒤 원래 작업을 계속하고, 실제 성능 개선은 잊히지 않도록 백로그에 남기라고 요청했다. 이어 “1번으로 하고, 담에 또 까먹지 않게 뭔가 기록을 해둬야 하지 않을까? 실제 개선 작업도 언젠가 재개할 수 있도록 묻히지 않게... 백로그에 기록해두던지...”라고 명시했다.

이 승인은 후속 후보 등록과 본 검증 재개에 관한 것이다. 이 문서는 성능 구현 착수, 새 latency SLA, 제품 계약 변경, 자동 재시도 또는 결과 수락을 만들지 않는다. source 기준 HEAD: `7d012f5297de1d9a77aa0b8187406f4785221573`. New Source Candidates 항목 변경의 이전 SHA-256은 `977948b126296d64aa48a67005e61b60d2caf329aaad9effb13756eab8423298`, 이후는 `a4f94dd3712f4dbbbb69a4f2065183d77839d27124c8effc3453262d670a5f2f`, 해당 bounded diff는 `599a431749f54c5afe48ad974befca654274883f9ec915c7d3717af8eeacfa23`다. 자세한 현재 진행·시간 원장은 기존 [Windows Work](FEAT-20261018-003-windows-native-implementation.md#windows-detach-performance-deferral--2026-10-28)가 계속 소유한다.

## 현재 결정과 근거

- 안전한 정상 완료, truth/content/Git 보존과 최종 detached 상태 검증을 우선한다. 120초 시험 공통 timeout은 제품 성능 요구가 아니다. 기존에 결정한 native detach apply 전용180초 watchdog을 본 검증에 연결하고, 실제 소요시간은 별도 관측한다. 180초는 완료 보장이나 새로운 SLA가 아니다.
- 기존120초 timeout 이력은 보존한다. 마지막 상태에서 계획된 파일68개가 제거되고 디렉터리17개가 남았지만, 이것만으로 정상 완료를 수락하지 않았다.
- 읽기 전용 복사본1회는1.586초, 계측1회는1.892초였다. 계측에서 Git helper16회, 경로 관찰3,957회, handle 상태 관찰7,032회를 보았다. 적용 코드가 각 파일·디렉터리 제거 전에 전체 상태를 반복 확인한다. 이것은 개선 후보이며 정확한 apply 중단 지점이나 성능 분포를 확정한 증거가 아니다.
- 정본 raw evidence는 Windows Work의 D53 실패 기록과 D54 `profile-analysis.json`, 원 ZIP·프로파일·bytes/hash 회수 검증이다. 단일 복사본 계측을 적용 성능·다른 환경 지원·최적화 성공으로 승격하지 않는다.

## 재검토 조건과 책임

Driver는 현재 Windows 검증 결과를 처분한 뒤 다음 작업을 제안할 때 이 후보를 반드시 함께 비교한다. Owner가 선택하면 기존 근거·당시 source를 대조해 별도 bounded 구현 계획을 만든다. 실제 사용 지연, 더 큰 retained history, 반복 detach 수요 또는 watchdog 내 정상 완료 실패가 관측되면 우선순위를 다시 판단한다. 단순히 다음 세션이 시작됐다는 이유로 본 검증의 blocker로 되돌리지 않는다.

## 선택 후 완료 기준

1. 같은 합성 작업·자료 규모와 고정 환경에서 원본/후보의 전체 detach 시간, 단계별 비용, 반복 관측 수를 비교한다. 표본 수·분산·계측 overhead를 명시한다.
2. 독립된 두 번의 상태 관찰, leaf/content/ancestor freshness, Git visibility, exact removal prefix, interruption/recovery·보존 검증을 유지한다.
3. 예상 효과와 변경 위험에 맞춘 집중 검사를 먼저 실행하고, 영향 없는 기존 검증을 재사용한다. 안전성·정확성 assertion이나 미리 고정한 중단 한도를 느슨하게 하여 속도 개선으로 보고하지 않는다.
4. 실제 개선폭·회귀·미측정 범위와 남은 비용을 기록하고 Owner 결과 수락을 받는다. 달성 latency 목표는 구현 계획에서 따로 합의하며 이 후보에는 새 숫자 목표를 만들지 않는다.


## 정상 완료 관측 — 2026-10-28 D55

후속 history 사례에서 detach apply가 기존180초 watchdog 아래139.075초에 exit0으로 완료했다. 이후 truth/content/Git 보존, 기존 local/worker 기록 읽기와 최종 detached 상태까지 통과했다. 원문과 metadata의 bytes/hash 회수를 확인했다. 단일 표본이므로 시간 분포나 SLA를 새로 정하지 않으며 기존120초 timeout 이력도 유지한다. 최적화는 계속 Deferred / Unselected이며 Windows 본 검증의 선행 조건이 아니다. 기존 Windows Work의 D55 결과와 원로그가 정본이다.
