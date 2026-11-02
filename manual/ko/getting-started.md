# Colvia와 프로젝트 준비하기

[목차](README.md) · [English](../en/getting-started.md) · [다음: 첫 Work](first-work.md)

프로젝트에서 얻고 싶은 결과부터 정하세요. macOS arm64 배포 후보는 Colvia와 전용 Python을 준비한 뒤, 별도의 미리보기와 결정으로 프로젝트에 연결합니다. 공개 배포와 최종 검증은 진행 전입니다. 실제 프로젝트에는 승인한 검증 배포본을 사용하세요. Windows 검증도 공개 전에 완료해야 합니다.

## 도구 준비하기

배포본에 명시된 버전과 bootstrap 해시를 사용합니다. bootstrap을 지속 보관할 위치에 내려받고 별도로 제공된 SHA-256과 대조한 뒤, 인수 없이 실행하세요. 저장 위치와 보존 범위를 검토하고 표시된 정확한 확인값으로 적용합니다. 도구와 Python은 `~/Library/Application Support/Colvia`에 준비됩니다. 이 경로는 저장소 clone, Homebrew 설치, shell 설정 편집을 요구하지 않습니다.

## 프로젝트 연결하기

에이전트에게 요청하세요.

> 검증된 배포본으로 이 프로젝트에 Colvia를 연결할 내용을 미리 보여줘. 대상과 바뀔 파일, 보존할 내용을 설명하고 설치 결정을 기다려줘. 첫 작업은 별도로 정하자.

새 non-Git 폴더나 primary Git checkout을 사용합니다. 기존 설치본, 연결 해제 뒤 남은 기록, 확인할 수 없는 상태, linked worktree에는 해당 상태의 지원 절차가 필요합니다. 정확한 요청은 프로젝트 밖에 보관합니다. 에이전트가 관리 명령의 `install --target PROJECT --json --save REQUEST_FILE`로 요청을 준비하고 설명한 뒤, 사용자의 결정에 따라 같은 요청과 확인값으로 적용합니다. 명령·지원 전환·복구 상세는 [Getting Started](../../docs/GETTING-STARTED.md#macos-managed-distribution-candidate)를 참고하세요.

첫 Work 전에 프로젝트 목적과 계획을 정하고, 기존 지침을 보존하며 [프로젝트 ignore 규칙](../../docs/GETTING-STARTED.md#prepare-project-ignore-rules)을 확인합니다. 공통 지침은 프로젝트 소유 `AGENTS.md`에 두고, Claude 진입 파일은 고유 지침을 유지하면서 이를 가리킬 수 있습니다. runtime update는 이 파일들을 그대로 둡니다. 관리형 배포에서는 프로젝트 config와 ignore 규칙을 사용하므로, 공유하려던 ignore 규칙도 첫 기준 상태를 기록하기 전에 확인하세요.

## 현재 상태 확인하기

프로젝트 폴더에서 `./colvia view`를 실행하면 현재 작업과 다음 안내를 볼 수 있습니다. 에이전트는 `./colvia view --details`에서 검증된 manual과 adapter를 읽습니다. 새 연결에는 수락된 작업 요청이나 Work가 아직 없습니다. 프로젝트 지침에는 기억해 둔 release 경로 대신 고정된 view 명령을 남기세요.

설치가 멈추면 요청·정확한 배포본·부분 상태를 보존합니다. 다시 실행하기 전에 현재 상태와 지원되는 복구 방법을 설명하도록 요청하세요. 연결 해제가 완료된 프로젝트는 남은 기록을 읽을 수 있으며, 새 설치 대상이 되지는 않습니다.

이제 [첫 Work의 범위](first-work.md)를 정합니다. 2026-10-05의 checkout-1 관측은 당시 실습에 해당하며, 이 배포본과 첫 사용 흐름의 검증은 별도로 기록합니다.

<!-- en_content_sha256: 0431718b8ab9f23f9c45518f83eb69e8e6b69d81b9cea4a37f7ddb57c591a726 -->
