# Colvia 사용 안내

한국어 · [English](../en/README.md) · v0.1.0 · 첫 공개 Preview

Colvia는 사람과 AI가 함께 일하는 로컬 워크플로 도구입니다. Codex나 Claude Code와 작업을 계획하고, 맡길 범위를 승인하고, 결과를 검토해 받아들일지 결정합니다. Colvia는 승인 내역과 제출본을 내 기기에 보관합니다. 같은 프로젝트를 열면 새 대화나 다른 에이전트에서도 작업을 이어갈 수 있습니다.

1. [설치하고 폴더를 연결하세요](install.md). Git을 사용하는 프로젝트 폴더라면 먼저 에이전트에게 [Git 등록을 요청](git.md#git-register)하세요. 평소 쓰는 채팅에서 “이 폴더에 Colvia를 연결해 주세요.”라고 요청하세요. 미리보기에서 추가할 파일과 기록 저장 위치를 확인한 뒤 연결을 승인하세요.
2. [지금 대화에서 하려던 일을 알려주세요](work.md#start). 빈 폴더라면 “회의 결과를 한 페이지로 정리하고 싶어요”처럼 한두 문장으로 시작해 보세요. 이미 작업 중인 프로젝트도 연결할 수 있습니다. 에이전트는 앞서 설명한 목적과 기존 자료를 참고해 작업안을 제안합니다. 계획에 적은 기존 파일의 본문은 계획을 기록할 때 보관합니다. 제출한 본문도 기록과 백업에 남습니다.
3. [결과를 검토하고](work.md#review) [기록한 후속 결정을 확인하세요](work.md#follow-up). 새 대화에서 같은 프로젝트를 열고, 에이전트가 연결 폴더와 기록 폴더를 읽을 수 있으면 이어갈 수 있습니다.

짧은 질문과 직접 부탁한 작은 수정은 [Work 없이 처리할 수 있는 조건](work.md#without-work)을 확인하세요. 기존 Work에 속한 수정은 해당 Work의 기록에서 이어갑니다.

설치한 뒤에는 [업데이트와 복구](maintenance.md#update), [연결 해제](maintenance.md#disconnect), [기록을 보존하는 제거](maintenance.md#uninstall) 안내를 참고하세요.

폴더를 옮겼다면 새 작업 전에 [에이전트에게 새 위치에서 기존 기록을 이어 달라고 요청하세요](records.md#move).

사용 중인 운영체제와 에이전트의 [지원 환경과 접근 조건](reference.md#environments)을 확인하세요.

문제가 생겼다면 · [접근이 막혔을 때](install.md#access) · [설치나 업데이트가 중단됐을 때](maintenance.md#update-recovery) · [문제 상황별 안내](reference.md#problems)

더 알아보기 · [Colvia 한눈에 보기](overview.md) · [따라 하기](tutorial.md) · [Git과 함께 쓰기](git.md) · [기록과 백업](records.md) · [아키텍처](architecture.md) · [명령과 용어](reference.md)

[Colvia](../../README.md)
