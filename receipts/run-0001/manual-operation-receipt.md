# Run 0001 Manual Operation Receipt

## Identity

- Implementation: `HV2-REPO-IMPL-001`, private local Git root, no remote, no commit.
- Target: `HV2-REPO-TARGET-run-0001`, fresh disposable private Git root.
- Authority home: `7d854f54-6538-4cd4-8961-2e2f50ef9653`.
- Payload: `HV2-PAYLOAD-001`, SHA-256 `ff8981affe108aad57156f52739b71558dd51f951ccf8609a63adf9cc1a54354`.
- Runtime: CPython `3.14.6`, stdlib only.

## Operator Boundary

Codex Driver가 human-repeatable core CLI sequence를 직접 실행했다. Agent/provider adapter와 provider transcript를 사용하지 않았다.
Project CLI는 이 lane에서만 사용했다. Blind auditor lane은 별도 capsule에서 project CLI/source/tests/transcript를 제공하지 않았다.

## Sequence

1. Darwin same-filesystem probe: file `fsync` pass, `F_FULLFSYNC` pass, directory fsync pass; power-loss claim 없음.
2. One authority home과 `item-0001` initialized.
3. `release-0001` create → `revision-0001`, binding complete, Git unfinalized 관측 뒤 target commit.
4. 첫 update 입력은 `after-pointer-assertion` typo로 argparse exit `2`, mutation `0`.
5. Corrected update는 `after_pointer_assertion`에서 exit `75`; active pointer는 `revision-0001` 유지.
6. Resume → `revision-0002`, binding complete/Git unfinalized 관측 뒤 target commit.
7. Forward rollback of `revision-0001` → 새 `revision-0003`, prior history 보존 뒤 target commit.
8. Logical detach → `revision-0004`, tombstone append, payload/history 보존, plain continuation 뒤 target commit.
9. Final target: classification pass, lifecycle detached, record 50, Git commit 5, tree
   `844ed60e0ea1af02e87f8d93e816414b88188405`, status clean, staging ignored.
10. Fresh-clone blind audit: pass, current `revision-0004`, payload/contract equality, zero-pack/provider true.

## Verification

- Stdlib `unittest`: baseline-red/contract `18/18`, full vertical `1/1`, total `19/19`.
- Carrier: release `5dc8e932...d39c`, inventory `1e03710d...feb`, payload `ff8981af...354`.
- Source revision: 16-entry relative-path SHA-256 inventory `80e72ebb...923a`.
- Blind auditor procedure: `e1dd8bfa...bf87`; implementation source/project CLI/runtime transcript unavailable to lane.
- Public/default/adopter/runtime support/TD-ACC/three-arm/population and hardware power-loss claims: `0`.
