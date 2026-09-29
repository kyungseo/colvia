"""Test-only selected intent chain reader; no product import or writer authority.

This does not validate unselected history, pending publications, all schema fields,
or current project prerequisites. A pass is a bounded reading observation only.
"""
from __future__ import annotations
import hashlib
import json
from pathlib import Path
import re
import stat
import sys


def require(condition, message):
    if not condition: raise ValueError(message)


def encoded(value):
    return (json.dumps(value, allow_nan=False, ensure_ascii=False, sort_keys=True, indent=2) + "\n").encode()


def identifier(value):
    require(isinstance(value, str) and re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]{0,95}", value), "invalid-id")
    return value


def pairs(items):
    result = {}
    for key, value in items:
        require(key not in result, "duplicate-key"); result[key] = value
    return result


def load(path):
    require(stat.S_ISREG(path.lstat().st_mode), "unsafe-file")
    raw = path.read_bytes()
    value = json.loads(raw, object_pairs_hook=pairs)
    require(isinstance(value, dict) and encoded(value) == raw, "non-canonical-object")
    return value, raw


def record(value, kind, authority, iid):
    require(value.get("record_type") == kind and type(value.get("schema_version")) is int and value["schema_version"] == 1, "record-type")
    require(value.get("authority_home_id") == authority and value.get("intent_id") == iid, "record-identity")


def reference(home, folder, ref, id_key):
    require(isinstance(ref, dict) and set(ref) == {"id", "sha256"}, "invalid-ref")
    rid = identifier(ref["id"])
    value, raw = load(home / folder / (rid + ".json"))
    require(value.get(id_key) == rid and hashlib.sha256(raw).hexdigest() == ref["sha256"], "ref-digest-or-id")
    return value


def inspect(target, iid):
    iid = identifier(iid); root = target / ".hrn"; home = root / "intents" / iid
    for directory in (root, root / "intents", home, *(home / k for k in ("drafts", "acceptances", "selections"))):
        require(stat.S_ISDIR(directory.lstat().st_mode), "unsafe-directory")
    fmt, _ = load(root / "format.json")
    require(fmt.get("record_type") == "workspace-format" and type(fmt.get("format_version")) is int and fmt["format_version"] == 1, "format-version")
    authority = identifier(fmt.get("authority_home_id"))
    identity, _ = load(home / "identity.json"); record(identity, "intent-identity", authority, iid)
    current, _ = load(home / "current.json"); record(current, "intent-current", authority, iid)
    selection = reference(home, "selections", current["selection_ref"], "selection_id"); record(selection, "intent-selection", authority, iid)
    acceptance = reference(home, "acceptances", selection["acceptance_ref"], "acceptance_id"); record(acceptance, "intent-acceptance", authority, iid)
    draft = reference(home, "drafts", selection["revision_ref"], "revision_id"); record(draft, "intent-draft", authority, iid)
    ticket = acceptance["confirmation"]
    require(isinstance(ticket, dict), "ticket-type")
    digest = hashlib.sha256(encoded(ticket)).hexdigest()
    require(ticket.get("record_type") == "confirmation-ticket" and type(ticket.get("schema_version")) is int and ticket["schema_version"] == 1, "ticket-type")
    require(ticket.get("authority_home_id") == authority and ticket.get("object") == {"authority_home_id":authority,"kind":"intent","id":iid}, "ticket-object")
    require(ticket.get("action") == "accept" and ticket.get("actor") == draft.get("acceptance_authority"), "acceptance-actor")
    require(acceptance["acceptance_id"] == "acceptance-" + digest and selection["selection_id"] == "selection-" + digest, "ticket-bound-id")
    require(ticket.get("target_revision_ref") == selection["revision_ref"] and ticket.get("expected_selection_ref") == selection["prior_selection_ref"], "acceptance-selection-binding")
    return {"classification":"pass","scope":"selected-chain-only","authority_home_id":authority,"intent_id":iid,"revision_id":draft["revision_id"],"revision_ref":selection["revision_ref"],"selection_ref":current["selection_ref"]}


def main():
    try:
        require(len(sys.argv) == 3, "usage: intent_plain_auditor.py TARGET INTENT_ID")
        result = inspect(Path(sys.argv[1]).absolute(), sys.argv[2]); code = 0
    except (OSError, ValueError, KeyError, TypeError, RecursionError) as exc:
        result = {"classification":"fail","scope":"selected-chain-only","reason":str(exc)}; code = 1
    print(json.dumps(result, ensure_ascii=False, sort_keys=True)); return code


if __name__ == "__main__":
    raise SystemExit(main())
