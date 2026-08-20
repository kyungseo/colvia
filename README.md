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

Generation 1의 one-item 명령은 그대로 유지한다. Generation 2 parallel safety는 별도 additive 명령
`activate-parallel`, `register-item`, `claim-work`, `reassign-claim`, `finalize-work`, `verify-repository`를 사용한다.
Worktree/branch 생성·삭제와 Git integration commit은 caller 책임이며, harness는 제공된 identity를 검증하고 persisted
claim/finalization state만 소유한다.

Guided Intent Formation은 별도 add-only `.harness-v2-intents/` home과 non-interactive 명령
`classify-intent-entry`, `init-intent-home`, `create-intent-draft`, `show-intent`, `accept-intent`, `verify-intent`를 사용한다.
Existing `.harness-v2/` StateStore·Generation 1/2 schema와 verifier는 변경하지 않는다. Exact REQ-002 mapping,
whole-revision acceptance, explicit supersede와 plain manual recovery는 `docs/GUIDED-INTENT-FORMATION.md`를 따른다.
질문 품질, item integration, adopter/public/default/runtime support는 이 vertical의 검증 claim이 아니다.

Manual-operation lane은 `docs/MANUAL-OPERATION.md`를 따른다. Plain auditor는 project CLI/source/tests 없이 accepted
generation contract, presealed expected/staging input과 disposable target bytes만 소비한다. `receipts/run-0001`과
`run-0002`는 preliminary authority `0`으로 보존하며 current source hardening은 fresh `run-0003`으로만 검증한다.

## Authority Boundary

- Durable implementation: this repository, logical ID `HV2-REPO-IMPL-001`.
- Canonical remote: private `kyungseo/hv2-reference-private`; default/only admitted branch is `main` until a separate gate.
- Disposable target: one fresh Git root per run, logical ID `HV2-REPO-TARGET-{run_id}`.
- Target `.harness-v2/` persisted bytes are project-owned truth.
- Remote mutation and automatic or implicit public promotion are forbidden without an Owner gate.
- Generation 2 actor/finalizer values are local logical declarations, not authentication or untrusted multi-user authorization.
