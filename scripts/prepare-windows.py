"""Explicit source-only Windows preparation; never packages or activates a release.

Only the declared managed subset is copied. The common source and default continuation-1
launcher stay unchanged. Common implementation/document edits must precede this
step; packaging later consumes these exact prepared bytes without rewriting them.
"""
import argparse
import json
from pathlib import Path
import shutil
import sys


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    source, output = args.source.absolute(), args.output.absolute()
    if output.exists() or output.is_symlink():
        parser.error("output must not exist; preserve prior preparation")
    if output == source or source in output.parents:
        parser.error("output must be outside the common source")
    sys.path.insert(0, str(source / "src"))
    from hv2ref.product import workspace_candidate
    from hv2ref.jsonio import canonical_json_bytes, sha256_bytes
    candidate = workspace_candidate(source)
    if candidate["release_ref"]["inventory_id"] != "continuation-1":
        parser.error("preparation requires the unchanged continuation-1 common declaration")
    original = candidate["payload"]
    before = b'WORKSPACE_INVENTORY_ID = "continuation-1"'
    after = b'WORKSPACE_INVENTORY_ID = "windows-2"'
    if original["colvia"].count(before) != 1:
        parser.error("expected exactly one literal declaration; preserve input")
    prepared = dict(original)
    prepared["colvia"] = original["colvia"].replace(before, after, 1)
    # This revision has one explicit transformation. Future payload changes must
    # update this declaration before preparing another candidate.
    report = {"schema_version": 1, "preparation": "windows-2",
              "input_release": candidate["release_ref"], "transformations": [
                  {"path": "colvia", "before": before.decode(), "after": after.decode()}],
              "entries": [{"path": name, "input_sha256": sha256_bytes(data),
                           "output_sha256": sha256_bytes(prepared[name]),
                           "input_size": len(data), "output_size": len(prepared[name]),
                           "source_mode": (source / name).stat().st_mode & 0o777}
                          for name, data in original.items()]}
    output.mkdir(parents=True)
    for name, data in prepared.items():
        path = output / name
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("xb") as handle:
            handle.write(data)
        shutil.copymode(source / name, path)
    observed = workspace_candidate(output)
    if observed["payload"] != prepared or observed["release_ref"]["inventory_id"] != "windows-2":
        raise RuntimeError("prepared payload verification failed; preserve output")
    if workspace_candidate(source) != candidate:
        raise RuntimeError("common source changed during preparation; preserve output")
    report["output_release"] = observed["release_ref"]
    (output / "preparation.json").write_bytes(canonical_json_bytes(report))
    print(json.dumps({"prepared": str(output), "managed_paths": len(prepared),
                      "release_ref": observed["release_ref"], "activated": False}, sort_keys=True))


if __name__ == "__main__":
    main()
