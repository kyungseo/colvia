# 프로젝트 규칙 확장과 Colvia 제거

이 문서는 활성화 전 `entry-1` 후보를 설명합니다. 사용하려면 정확한 artifact의 별도 qualification과 설치 승인이 필요하며, 아래의 과거 checkout-1 실습은 현재 명령의 검증 근거가 아닙니다.

[매뉴얼 처음으로](README.md) · [English](../en/rules-and-removal.md)

프로젝트에 맞춘 지침은 프로젝트가 소유하는 파일에 둡니다. Colvia는 공통 규칙과 managed adapter를 제공합니다. Adapter는 agent가 사용자의 요청을 지원되는 작업 절차로 이어 가도록 돕는 지침입니다. 설치된 runtime을 제거하면 그 안의 지침도 제거되지만, 프로젝트가 작성한 규칙과 작업 이력은 남습니다.

프로젝트 규칙을 추가하거나 agent의 작업 방식을 보완할 때, runtime을 갱신하거나 Colvia 사용을 끝낼 때 이 안내를 읽으세요. 예시는 프로젝트 Owner와 검토해 적용할 문안입니다. 자동 확장 기능이나 native agent에서 동작을 확인한 연동 방식은 아닙니다.

## 1. 파일의 소유자 확인하기

| 대상 | 위치 | 갱신·제거 시 처리 |
| --- | --- | --- |
| 공통 규칙과 adapter source | 별도의 Colvia source checkout | Source 유지보수 절차로 수정합니다. 다른 프로젝트의 detach로 이 checkout이 지워지지 않습니다. |
| 설치된 공통 규칙과 adapter | `.hrn/product/` 아래 검증된 release | Runtime lifecycle이 관리하며 exact detach의 제거 대상입니다. |
| 프로젝트 규칙과 local agent 지침 | 기존 프로젝트 지침이나 프로젝트 소유 문서 | Owner가 승인한 변경으로 갱신·폐기합니다. Detach 후에도 남습니다. |
| Agent 진입 지침 | 프로젝트 `AGENTS.md`, `CLAUDE.md` 또는 기존 진입 문서 | 현재 managed adapter와 프로젝트 규칙을 연결합니다. Detach가 이 연결을 고치지 않습니다. |
| 수락 이력과 작성 문서 | `.hrn/` authority와 참조된 프로젝트 문서 | Detach가 보존합니다. 제거 승인이 이력 수정 권한은 아닙니다. |

현재 설치본의 manual과 adapter는 `./colvia view`로 찾습니다. Release 디렉터리 경로를 진입 문서에 고정하거나 설치된 payload를 직접 수정하지 마세요. 변경되거나 예상하지 못한 product 파일이 있으면 lifecycle 작업이 거부될 수 있습니다. 별도의 사용자·전역 agent 규칙도 detach 대상이 아닙니다. 다른 프로젝트에 미칠 영향을 포함해 그 규칙의 소유자가 변경 여부를 결정합니다.

## 2. 작은 프로젝트 규칙 추가하기

먼저 같은 상황을 다루는 기존 규칙을 확인합니다. 있다면 해당 절을 보완하세요. 목적, 유지보수 담당, 적용할 변경, 근거 source 절·revision, 프로젝트의 선택과 확인 방법을 적습니다. 기존 문서 구조를 사용하며 새 규칙 디렉터리나 registry를 만들 필요는 없습니다.

CLI 프로젝트라면 “CLI 옵션을 바꿀 때 사용법 페이지와 관련 예제를 승인된 범위에 포함하고, 바뀐 명령과 검사 결과를 보고한다”는 규칙을 제안할 수 있습니다. 정확한 문서 경로와 검사 방법은 해당 프로젝트의 코드·문서에서 정합니다. 이 예시가 다른 종류의 프로젝트에도 CLI 검사를 요구하는 것은 아닙니다.

규칙과 진입 연결의 변경안을 Owner에게 보여 주세요. 적용 전 [Check Before Writing](../../docs/REFERENCE.md#check-before-writing)을 따릅니다. 필수 문서 참조나 제출된 결과에 영향을 주면 새 수락 또는 지원되는 재작업 절차가 먼저 필요할 수 있습니다. 기록 권한이 있다면 기존 Work 서술에 결과를 남기고, 별도의 진행 로그를 만들지 않습니다.

## 3. Agent 지침에 연결하기

Local adapter는 어떤 규칙을 읽고 무엇을 설명할지 알려 주는 짧은 프로젝트 소유 절로 시작할 수 있습니다. 먼저 기존 문서에 둘 수 있는지 확인하세요. 지침을 별도 페이지로 나눌 필요가 있다면 다음과 같이 연결할 수 있습니다. 아래 경로는 예시이며 필수 디렉터리 구조가 아닙니다.

```text
AGENTS.md
  -> ./colvia view -> current managed adapter
  -> docs/agent-guide.md -> relevant project rule and checks
```

예를 들어 `docs/agent-guide.md`에 다음 지침을 검토해 넣을 수 있습니다. 아래 영어 문안은 “승인된 CLI 변경 전에 프로젝트 문서 규칙과 영향받는 페이지·예제를 확인하고, 결과 검토 때 변경된 명령·실행한 검사·남은 한계를 기존 Work에서 설명한다”는 뜻입니다.

```text
For an authorized CLI change, read the project's CLI documentation rule.
Identify the affected usage page and examples before editing.
At result review, explain changed commands, executed checks and remaining limits.
Use the existing Work narrative; follow its scope and reference requirements.
```

기존 agent 진입 문서에는 CLI 변경 시 `docs/agent-guide.md`의 해당 지침을 읽으라는 짧은 연결을 추가합니다. 도구에만 필요한 지침은 해당 도구의 진입 문서에 유지합니다. Managed adapter 전문을 복제하지 마세요. Local 지침으로 수락 권한을 부여하거나 불변 기록을 바꾸고 무결성 검사를 우회할 수는 없습니다. Runtime의 거부를 실행 허가로 해석할 수도 없습니다. 지침이 충돌하면 행동하기 전에 Owner에게 차이를 보여 주세요.

연결 경로가 열리는지 확인하고, 새 세션에서 어떤 지침을 읽었고 언제 적용하는지 설명하도록 요청하세요. 이 세션 확인을 실행할 수 없었다면 미검증으로 기록합니다. Markdown에 연결을 썼다는 사실만으로 특정 도구의 자동 로드를 확인한 것은 아닙니다. Native skill 포장이나 discovery는 해당 도구의 설정과 별도 검증이 필요합니다.

## 4. Runtime 갱신 시 비교하기

Runtime을 갱신하면 managed release와 `./colvia view`가 안내하는 경로가 바뀝니다. 프로젝트 규칙이나 local adapter는 자동 갱신되지 않습니다. 전에 채택한 source 절·revision, 새 지침, 현재 프로젝트 규칙을 비교하세요. 의도한 프로젝트 선택은 보존하고 충돌을 설명한 뒤, 프로젝트 수정에 필요한 승인을 받습니다. 이전 source를 복원할 수 없다면 그 한계를 밝히고 비교가 끝났다고 말하지 않습니다.

Runtime 설치와 프로젝트 규칙 편집은 별개의 작업·승인으로 다룹니다. 어느 쪽을 바꾸든 pending 작업과 문서 참조에 미치는 영향을 먼저 살펴보세요. Update 승인은 제출된 결과를 고칠 권한이 아닙니다. 승인된 갱신 뒤에는 현재 adapter 경로, 관련 프로젝트 연결과 검사를 확인합니다. 이력이나 복구에 필요한 과거 참조 판본은 보존합니다.

checkout-1→entry-1 전환은 허용 목록의 정확한 predecessor만 지원합니다. 적용 전에 협력하는 writer를 멈추고, 정확한 old/new source와 원래 request·token, 복원을 확인한 외부 복구 자료를 보존하세요. 첫 switch receipt가 영속화되는 S1부터는 새 기록이 없어도 checkout-1이나 이전 window로 rollback할 수 없습니다. Local/parent manifest와 직접 포착한 child 참조 검사 때문에 전환이 거부될 수 있습니다. 기존 worker 결과는 별도 Git 승인, 명시적인 same-intent worker rebind와 재제출이 필요합니다. Runtime은 프로젝트 진입 지침을 수정하거나 Git 작업을 수행하지 않습니다. [Entry-1 transition](../../docs/OPERATIONS.md#entry-1-transition)을 참고하세요.

첫 receipt나 S2 파일의 torn bytes, 지원하지 않는 O-plus-binding.next 조합은 제품 안에서 복구할 경로가 없을 수 있습니다. 원본을 보존하고 외부 복구·처분 승인을 별도로 받으세요. OLD pending init/repair/detach는 새로운 entry-1 요청이 아니라, 일치하는 보존 OLD source와 원래 요청으로 처리합니다. 적용 대상인 은퇴 경로 `hv2`의 점유물은 보존합니다. 그 밖의 검증이 유효한 live 진단은 conflict/12, lifecycle 호출은65로 거부하고, schema-3 detach로 binding이 사라진 뒤의 source 진단은 충돌 오류를 동반한 degraded/10을 사용합니다. Confirmation 표시나 정상적인 현재 status가 과거 내용 비교 또는 이전 동기화의 성공을 증명하지는 않습니다. 현재 detach는 paired schema3을 사용합니다. Paired1/2 이력은 읽을 수 있지만 복구에는 일치하는 OLD source가 필요합니다.

## 5. Colvia 제거와 진입 지침 정리하기

정확한 명령과 복구 계약은 [Operations](../../docs/OPERATIONS.md#detach)에 있습니다. 현재 개발판은 detach 후 남은 authority 위에 재설치하거나 attach하는 절차를 지원하지 않습니다. 제거를 승인하기 전에 Colvia 없이 프로젝트 작업을 계속하고 남은 이력을 읽을 방법을 정하세요. 다시 설치하려고 이력을 삭제하면 안 됩니다.

1. **제거를 준비합니다.** 현재 설치본과 pending Work·intent·lifecycle 작업을 확인하고, pending 작업은 지원되는 절차로 해결합니다. 제거 승인을 받기 전에 미완료 Work와 결정 대기 결과를 어떻게 처리할지 정합니다. Detach가 모든 미완료 Work 상태를 차단하는 것은 아닙니다. Colvia를 호출하는 관련 진입 연결·프로젝트 규칙·도구 지침·hook만 찾아 무엇을 유지하고 교체할지 제안합니다. Runtime이 있는 동안 Check Before Writing에 따라 5단계에서 고칠 진입·규칙 파일이 남는 기록에서 참조되는지 추적하고, 그 결과를 승인받을 편집안에 포함합니다. 프로젝트 지침 변경은 별도로 검토하고, 제거 전에 할 편집은 Check Before Writing에 따라 승인받아 마친 뒤 요청을 준비합니다. `./colvia view` 연결 제거는 5단계까지 남겨 둡니다. Detach 적용 전에 호환되는 독립 source와 필요한 매뉴얼을 대상 밖에 확보하고, 필요한 역사·참조 원본을 보존합니다. 저장소 전체를 정리하는 작업으로 넓히지 않습니다.
2. **Preview를 검토합니다.** Agent에게 exact detach 요청을 준비하고 제거·보존 목록을 설명하도록 합니다. 적용 전 원 요청과 confirmation token을 대상 밖에 보관합니다. 일부만 제거된 상태의 복구 중에도, 제거 완료를 확인할 때까지 추가 프로젝트 편집은 예방 차원에서 미룹니다. 편집을 기록하는 Work 발행이 요청에 묶인 truth를 바꿀 수 있기 때문입니다. 제거가 시작되기 전에 확인한 상태가 달라졌다면 멈추고 적절한 새 요청을 준비해 승인받습니다.
3. **정확한 작업을 승인하고 적용합니다.** Owner가 대상과 요청을 승인합니다. 문서의 confirmation 절차로 한 번 적용합니다. 일부만 제거된 채 실패했다면 원 요청과 confirmation token을 보존하고 지정된 독립 source로 복구합니다. 대상 디렉터리는 원래 경로에 그대로 둡니다. 사본이나 clone은 읽기 전용 확인용이며 복구 대상이 아닙니다. Launcher가 없다는 이유만으로 제거 완료로 판단하거나 파일을 임의로 지우지 않습니다.
4. **제거와 보존 결과를 확인합니다.** 독립 source의 검사로 detached 상태를 확인합니다. Receipt가 있거나 launcher가 없다는 사실만으로 완료를 판단하지 않습니다. Launcher와 managed product 파일은 제거되고, `.hrn/detached.json`, format, planning, intent/Work 이력, 작성 문서와 ignored scratch는 남습니다. Replay나 복구에 아직 필요한 정확한 입력도 유지합니다.
5. **승인된 프로젝트 편집을 마칩니다.** 1단계에서 찾은 진입 연결·도구 지침·hook 중 승인된 범위의 불필요한 Colvia 호출을 제거하거나 교체합니다. `./colvia view`와 managed adapter 지침도 포함합니다. 확인된 detach 완료와 남은 이력의 위치를 사실로 적고, 조건에 따라 검사를 건너뛰는 문구는 쓰지 않습니다. 여전히 필요한 프로젝트 규칙은 유지하고 이후 작업 방식을 설명합니다. 필요한 역사·참조 원본은 보존합니다. 참조된 규칙을 고정해야 한다면 그대로 두고 별도의 현행 지침을 제안합니다. Colvia 연결이 있다는 이유로 도구 디렉터리나 전역 설정 전체를 삭제하지 않습니다.
6. **재진입을 확인합니다.** 새 진입 문서의 연결이 열리고, 새 세션이 제거된 runtime을 호출하도록 안내받지 않는지, 남은 hook도 그 runtime을 호출하지 않는지 확인합니다. 남겨 둔 이력은 읽기 전용으로 확인할 수 있어야 합니다. 프로젝트 편집이 남았거나 세션 확인을 하지 못했다면 그 상태를 알립니다. Runtime 제거 성공만으로 진입 지침 정리까지 완료됐다고 말하지 않습니다.

프로젝트 진입 지침은 확인된 detach 완료와 예상 밖 설치 고장을 구분해야 합니다. `AGENTS.md`·`CLAUDE.md`의 유용한 비Colvia 지침은 유지하세요. Runtime이 없으면 자동으로 무시하고 진행하는 fallback을 추가하지 않습니다.

## 근거와 확인 범위

이 안내는 현행 [Repository-Owned Rules](../../docs/REFERENCE.md#repository-owned-rules), [프로젝트 진입 준비](../../docs/GETTING-STARTED.md#prepare-project-agent-entry), [detach 계약](../../docs/WORKSPACE-CONTRACT.md#receipt-bound-detach), [남은 이력 읽기](../../docs/MANUAL-OPERATION.md)를 연결합니다. Repository에서 읽는 문서이며 설치 payload에는 포함되지 않습니다. 이 페이지는 매뉴얼 README에 명시된 실습 기준 release보다 뒤의 source 지침을 참조하므로, 그 설치본에는 추가된 절이 없을 수 있습니다. Detach 전에 `./colvia view`로 실제 대상의 검증된 문서 위치와 내용을 확인하세요. 이 안내를 읽었다고 설치본이 갱신되는 것은 아닙니다.

예제 local adapter와 사람이 agent와 함께 수행하는 전체 제거 순서는 native agent 세션에서 시험하지 않았습니다. 문서 검사와 합성 lifecycle 테스트만으로 실제 사용자의 이해도나 모든 agent의 지침 준수를 확인할 수는 없습니다.

[매뉴얼 처음으로](README.md)

<!-- en_content_sha256: fc785eac9b9880492a50a37d54b19a7abe0de9279e07bfb8749418f71e0f840d -->
