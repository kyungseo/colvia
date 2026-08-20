from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path


def load(path: Path) -> tuple[dict[str, object], bytes]:
    data = path.read_bytes()
    if not data.endswith(b"\n") or data.endswith(b"\n\n") or b"\r" in data:
        raise ValueError(f"non-canonical-line-ending:{path}")
    value = json.loads(data)
    canonical = (json.dumps(value, allow_nan=False, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode()
    if data != canonical:
        raise ValueError(f"non-canonical-json:{path}")
    return value, data


def check_ref(ref: object, path: Path) -> tuple[dict[str, object], bytes]:
    if not isinstance(ref, dict) or set(ref) != {"id", "sha256"}:
        raise ValueError(f"invalid-ref:{path}")
    value, data = load(path)
    if hashlib.sha256(data).hexdigest() != ref["sha256"]:
        raise ValueError(f"digest-mismatch:{path}")
    return value, data


def main() -> int:
    if len(sys.argv) != 3:
        raise ValueError("usage: intent_plain_auditor.py TARGET INTENT_ID")
    target = Path(sys.argv[1]).resolve()
    intent_id = sys.argv[2]
    root = target / ".harness-v2-intents"
    intent_root = root / intent_id
    authority, _ = load(root / "authority.json")
    identity, _ = load(intent_root / "identity.json")
    current, _ = load(intent_root / "current-selection.json")
    if identity["authority_home_id"] != authority["authority_home_id"] or identity["intent_id"] != intent_id:
        raise ValueError("identity-mismatch")
    selection_ref = current["selection_ref"]
    selection, _ = check_ref(selection_ref, intent_root / "selection-assertions" / f"{selection_ref['id']}.json")
    acceptance_ref = selection["acceptance_ref"]
    acceptance, _ = check_ref(acceptance_ref, intent_root / "acceptances" / f"{acceptance_ref['id']}.json")
    revision_ref = selection["revision_ref"]
    draft, _ = check_ref(revision_ref, intent_root / "drafts" / f"{revision_ref['id']}.json")
    if acceptance["revision_ref"] != revision_ref or acceptance["actor"] != draft["acceptance_authority"]:
        raise ValueError("acceptance-mismatch")
    unresolved = [gap for gap in draft["gaps"] if gap["status"] == "unresolved"]
    print(
        json.dumps(
            {
                "actionable": True,
                "authority_home_id": authority["authority_home_id"],
                "classification": "pass",
                "intent_id": intent_id,
                "revision_id": revision_ref["id"],
                "route": draft["route"],
                "unresolved": unresolved,
            },
            allow_nan=False,
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
