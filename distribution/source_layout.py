"""Explicit repository-to-installed source mapping. Build-time only; never shipped."""
from pathlib import Path

SOURCE_MAP = {"README.md": "distribution/README-installed.md"}


def source_path(source: Path, name: str) -> Path:
    return source / SOURCE_MAP.get(name, name)


def read_checkout(source: Path, paths=None) -> dict:
    """Read a developer checkout, never guess or fall back to a public README."""
    from hv2ref.product import _serial_file, _serial_require, _launcher_inventory_window, _managed_paths
    from hv2ref.workspace import safe_target, _require_kind
    from hv2ref.jsonio import canonical_json_bytes, sha256_bytes
    source = safe_target(source)
    declaration = _serial_file(source / "colvia")
    window = _launcher_inventory_window(declaration)
    names = tuple(_managed_paths(window) if paths is None else paths)
    # Callers may request the official profile's additional files, but not arbitrary paths.
    from hv2ref.product import OFFICIAL_V2_MANAGED_PATHS
    _serial_require(names in (tuple(_managed_paths(window)), tuple(OFFICIAL_V2_MANAGED_PATHS)),
                    "unknown source preparation inventory")
    _serial_require(set(SOURCE_MAP).issubset(names) and not set(SOURCE_MAP.values()).intersection(names),
                    "source mapping conflicts with installed inventory")
    payload, modes = {}, {}
    for name in names:
        path = source_path(source, name)
        for parent in reversed(path.relative_to(source).parents):
            _require_kind(source / parent, True)
        _require_kind(path, False)
        payload[name] = _serial_file(path)
        modes[name] = path.stat().st_mode & 0o777
    for name, raw in payload.items():
        path = source_path(source, name)
        _serial_require(_serial_file(path) == raw and path.stat().st_mode & 0o777 == modes[name],
                        "checkout changed during source preparation")
    _serial_require(payload["colvia"] == declaration, "launcher changed during source preparation")
    inventory = {"record_type": "release-inventory", "schema_version": 1, "inventory_id": window,
                 "entries": [{"path": name, "sha256": sha256_bytes(raw), "size_bytes": len(raw)}
                             for name, raw in payload.items()]}
    digest = sha256_bytes(canonical_json_bytes(inventory))
    candidate_ref = {"id": "product-release-" + digest[:24], "sha256": digest, "inventory_id": window}
    if names != tuple(_managed_paths(window)):
        # An extended input set is not a release until its launcher is transformed.
        inventory, candidate_ref = None, None
    return {"inventory": inventory, "payload": payload, "source_modes": modes,
            "release_ref": candidate_ref}


def prepare_source(source: Path, output: Path) -> dict:
    """Materialize a new ordinary managed tree, preserving installed names and bytes."""
    from hv2ref.product import workspace_candidate
    from hv2ref.jsonio import canonical_json_bytes, sha256_bytes
    source, output = source.absolute(), output.absolute()
    if output.exists() or output.is_symlink() or output.resolve() == source.resolve() or source.resolve() in output.resolve().parents:
        raise ValueError("new output outside the checkout required")
    baseline = read_checkout(source)
    if baseline["release_ref"]["inventory_id"] != "continuation-1":
        raise ValueError("common source declaration required")
    output.mkdir(parents=True, mode=0o700)
    for name, raw in baseline["payload"].items():
        dest = output / name
        dest.parent.mkdir(parents=True, exist_ok=True)
        with dest.open("xb") as stream:
            stream.write(raw)
        dest.chmod(baseline["source_modes"][name])
    observed = workspace_candidate(output)
    if observed["payload"] != baseline["payload"] or read_checkout(source) != baseline:
        raise RuntimeError("source preparation drift; preserve output")
    report = {"schema_version": 1, "preparation": "common-source", "output_release": observed["release_ref"],
              "entries": [{"path": n, "source_path": SOURCE_MAP.get(n, n), "sha256": sha256_bytes(raw),
                           "source_mode": baseline["source_modes"][n]} for n, raw in baseline["payload"].items()]}
    (output / "preparation.json").write_bytes(canonical_json_bytes(report))
    return report
