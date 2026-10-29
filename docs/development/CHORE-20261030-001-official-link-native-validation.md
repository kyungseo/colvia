# Official Link Metadata Native Validation

## Scope And Authorization

Owner가 2026-10-30 합성 native sandbox 검증을 진행하도록 승인했다. [수락된 링크 metadata 구현](PATCH-20261029-003-official-link-metadata.md)의 후속 검증이며, 그 원결과나 R1 revise 판정을 소급 변경하지 않는다. 제품 코드·정책·실제 adopter·모델·Git 변경은 검증 범위에 포함하지 않았다. 검증 결과 보고 뒤 Owner가 Git 통합과 실제 대상 업데이트 준비를 계속하도록 요청했다. 이 기록은 source-only 후속이며 runtime Work를 생성하지 않는다.

## Fixed Inputs And Execution

대상은 official-execution-1 후보 `86f03156d06edd425dba454121aae30adf3e458dabd877ac6db578de6297d28a`다. 실제 DocumentController가 생성한 기존 정책으로 제품 worker 1회와 같은 정책의 고정 권한 probe 1회를 실행했다. macOS sandbox 중첩 제약으로 신뢰된 controller만 외부에서 실행했으며 합성 HOME과 전용 durable 폴더를 사용했다. 계정·모델·reviewer 호출과 실제 adopter 쓰기는 0이다.

합성 budget을 사용한 DocumentController/worker 경계의 검증이다. 전체 Host의 grant/admission이나 실제 설치에서의 실행을 검증했다고 주장하지 않는다. worker와 probe는 각각30초, controller는150초 상한, 자동재시도0으로 고정했다.

## Results And Limits

- 실제 DOC-LINKS worker가 루트·하위 폴더의 opaque/anchor 네 대상을 모두 검증했고 findings는 없었다.
- 같은 생성 정책에서 opaque 두 파일의 본문 열기는 각각 EPERM으로 거절됐다. anchor 두 파일은 정확한 합성 본문을 읽어 positive control을 확인했다.
- worker·probe·controller의 정상 종료와 process group 부재, 입력·source·후보·정책 불변을 확인했다. 실행 전체는 약0.38초, 준비·확인·정리는 약3분28초였다.
- 일반/최적화 집중69사례와 전환 근거는 이전 구현 결과의 분리된 실행·재사용 설명을 유지한다. 이번 읽기 전용 검증 때문에 전체 회귀를 반복하지 않았다.

native worker의 해당 metadata 경로와 읽기 차단 증거는 확보했다. 실제 adopter의 전체 실행, Windows 자격, 원 R1 보완본의 독립 재검토는 이 결과 밖이다. 소스 결과 수락은 앞선 기록에 있으며 Git 통합과 실제 적용은 정확한 대상별 승인으로 진행한다.

## Preservation And Follow-Up

고정 script·합성 입력·spec·생성 정책·원 결과·process 종료 근거는 native 결과 판단과 후속 통합/적용을 위해 private task artifact에 보존했다. 고유 증거가 없는 빈 전용 디렉터리4개만 정리했고 활성 source 경로는 바꾸지 않았다. 해당 판단과 통합/적용 선택 후 보존 필요를 재평가한다.

예상10–15분은 준비·정리의 판단 추정이었고 실제 단계는 약3분28초였다. 기존 누적 신규시작490분·중단500분 한도는 유지했다. 이전 수락 기록 정리의 정확한 active/wait 분리가 없어 그 구간을 보수적으로 포함한 누적 상한은 약480.29분이며 측정된 순수 active 시간으로 표시하지 않는다. 확인된 Owner 대기는 제외했다.
