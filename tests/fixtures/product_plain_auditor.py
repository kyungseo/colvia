#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path


def load(path: Path) -> object:
    data = path.read_bytes()
    if not data.endswith(b"\n") or data.endswith(b"\n\n") or b"\r" in data:
        raise ValueError(f"non-canonical-line-ending:{path.name}")
    return json.loads(data.decode("utf-8"))


def main() -> int:
    target = Path(sys.argv[1]).resolve()
    receipt_path = target / ".harness-v2-detached.json"
    receipt = load(receipt_path)
    if not isinstance(receipt, dict) or receipt.get("record_type") != "product-detach-receipt":
        raise ValueError("detach-receipt")
    documentation = receipt.get("documentation")
    if not isinstance(documentation, dict) or set(documentation) != {
        "availability_after_detach", "release_ref", "required_relative_paths"
    }:
        raise ValueError("detach-documentation")
    if documentation["availability_after_detach"] != "not-guaranteed":
        raise ValueError("detach-documentation-availability")
    if documentation["release_ref"] != receipt.get("active_release_ref"):
        raise ValueError("detach-documentation-release")
    if "docs/MANUAL-OPERATION.md" not in documentation["required_relative_paths"]:
        raise ValueError("detach-documentation-manual")
    state = load(target / ".harness-v2/authority.json")
    intent = load(target / ".harness-v2-intents/authority.json")
    if state.get("authority_home_id") != receipt.get("state_authority_home_id"):
        raise ValueError("state-authority")
    if intent.get("authority_home_id") != receipt.get("intent_authority_home_id"):
        raise ValueError("intent-authority")
    if (target / "hv2").exists() or (target / ".harness-v2-product").exists():
        raise ValueError("product-bytes-remain")
    result = {
        "classification": "pass",
        "intent_authority_home_id": intent["authority_home_id"],
        "receipt_sha256": hashlib.sha256(receipt_path.read_bytes()).hexdigest(),
        "state_authority_home_id": state["authority_home_id"],
    }
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
