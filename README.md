# Harness v2 First Private Reference Implementation

`HV2-REPO-IMPL-001`은 Harness v2 minimum production vertical의 private reference implementation이다.
Toolstead control plane이나 disposable target repository가 아니다. Public/default/runtime support claim을 만들지 않는다.

## Runtime

- CPython `3.14.6`
- Python standard library only
- Tests: `unittest`
- Third-party runtime/dev dependency: `0`

## Commands

```sh
PYTHONPATH=src python3 -m unittest discover -s tests -v
PYTHONPATH=src python3 -m hv2ref.cli --help
```

Manual-operation lane은 `docs/MANUAL-OPERATION.md`를 따른다. Plain auditor는 project CLI/source/tests 없이 accepted
generation contract, presealed expected/staging input과 disposable target bytes만 소비한다. `receipts/run-0001`과
`run-0002`는 preliminary authority `0`으로 보존하며 current source hardening은 fresh `run-0003`으로만 검증한다.

## Authority Boundary

- Durable implementation: this repository, logical ID `HV2-REPO-IMPL-001`.
- Disposable target: one fresh Git root per run, logical ID `HV2-REPO-TARGET-{run_id}`.
- Target `.harness-v2/` persisted bytes are project-owned truth.
- No remote is configured. Automatic or implicit public promotion is forbidden.
