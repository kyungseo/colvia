"""Fixed document operations; launched inside the operation's literal OS profile.

The trusted host supplies a sealed spec file and a request on stdin. Document text cannot select a
path, executable, parser, verifier, authority action or new filesystem permission.
"""
from __future__ import annotations

import argparse
import ctypes
import hashlib
from html.parser import HTMLParser
import json
import os
from pathlib import Path
import re
import stat
import sys
from urllib.parse import unquote, urlsplit

LIMIT = 65_536


class WorkerRefusal(RuntimeError):
    pass


def require(condition, code):
    if not condition:
        raise WorkerRefusal(code)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def canonical(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()


def exact_keys(value, keys):
    require(isinstance(value, dict) and set(value) == set(keys), "invalid-fields")


def parent_fd(path, identities, for_sync=False):
    """Walk all ancestors without following symlinks, retaining the parent fd."""
    require(path.is_absolute() and str(path) == os.path.normpath(str(path)), "noncanonical-path")
    require(hasattr(os, "O_SEARCH"), "directory-search-unavailable")
    flags = os.O_SEARCH | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC
    fd = os.open("/", flags)
    current = Path("/")
    try:
        for component in path.parts[1:-1]:
            next_fd = os.open(component, flags, dir_fd=fd)
            os.close(fd)
            fd = next_fd
            current /= component
            identity = identities.get(str(current))
            info = os.fstat(fd)
            require(identity == [info.st_dev, info.st_ino], "ancestor-drift")
        if for_sync:
            sync_fd = os.open(".", os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC, dir_fd=fd)
            require((os.fstat(sync_fd).st_dev, os.fstat(sync_fd).st_ino) == (os.fstat(fd).st_dev, os.fstat(fd).st_ino), "directory-fsync-identity")
            os.close(fd)
            fd = sync_fd
        return fd
    except BaseException:
        os.close(fd)
        raise


def document_stat_key(info):
    # A read may update atime; content/identity metadata must remain stable.
    return (info.st_dev, info.st_ino, info.st_mode, info.st_nlink, info.st_size,
            info.st_mtime_ns, info.st_ctime_ns)


def file_bytes(entry, identities):
    path = Path(entry["path"])
    directory = parent_fd(path, identities)
    try:
        if entry["identity"] is None:
            require(entry.get("view") == {"kind": "full"} and entry["sha256"] is None, "absence-contract")
            try:
                os.stat(path.name, dir_fd=directory, follow_symlinks=False)
            except FileNotFoundError:
                return b""
            raise WorkerRefusal("expected-absence-drift")
        fd = os.open(path.name, os.O_RDONLY | os.O_NOFOLLOW | os.O_CLOEXEC, dir_fd=directory)
        with os.fdopen(fd, "rb") as stream:
            before = os.fstat(stream.fileno())
            require(stat.S_ISREG(before.st_mode) and before.st_nlink == 1, "file-alias")
            require([before.st_dev, before.st_ino] == entry["identity"], "file-identity-drift")
            require(stat.S_IMODE(before.st_mode) == entry["mode"], "file-mode-drift")
            limit = 131_072 if "view" in entry else LIMIT
            require(before.st_size <= limit, "file-too-large")
            raw = stream.read(limit + 1)
            after = os.fstat(stream.fileno())
            require(document_stat_key(before) == document_stat_key(after) and len(raw) <= limit and sha(raw) == entry["sha256"], "file-bytes-drift")
            raw.decode("utf-8", errors="strict")
            return raw
    finally:
        os.close(directory)


def atomic_write(entry, identities, swap, expected, content):
    require(isinstance(content, str) and "\x00" not in content, "invalid-content")
    raw = content.encode("utf-8", errors="strict")
    require(len(raw) <= LIMIT and expected == entry["sha256"], "write-size-or-cas")
    prior = file_bytes(entry, identities)
    require(entry["identity"] is None or sha(prior) == expected, "prior-bytes-drift")
    view = entry.get("view", {"kind": "full"})
    if view["kind"] == "replace-range":
        document_view(entry, prior)
        begin, end = view["ranges"][0]
        raw = prior[:begin] + raw + prior[end:]
    else:
        require(view["kind"] == "full", "readonly-view")
    require(len(raw) <= (131_072 if "view" in entry else LIMIT), "assembled-file-too-large")
    target = Path(entry["path"])
    swap = Path(swap)
    require(target != swap, "swap-is-target")
    target_dir = parent_fd(target, identities, for_sync=True)
    swap_dir = parent_fd(swap, identities, for_sync=True)
    try:
        require(os.fstat(target_dir).st_dev == os.fstat(swap_dir).st_dev and
                (entry["identity"] is None or os.fstat(target_dir).st_dev == entry["identity"][0]), "swap-device")
        # Exclusive creation leaves any unexpected prior swap untouched.
        fd = os.open(swap.name, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW | os.O_CLOEXEC,
                     entry["mode"], dir_fd=swap_dir)
        with os.fdopen(fd, "wb") as stream:
            os.fchmod(stream.fileno(), entry["mode"])
            stream.write(raw)
            stream.flush()
            os.fsync(stream.fileno())
            new = os.fstat(stream.fileno())
            require(new.st_nlink == 1 and stat.S_ISREG(new.st_mode), "swap-alias")
        os.fsync(swap_dir)
        # The controller owns serialization and verifies writer quiescence. This
        # comparison is not advertised as a kernel compare-and-swap primitive.
        file_bytes(entry, identities)
        if entry["identity"] is not None:
            target_now = os.stat(target.name, dir_fd=target_dir, follow_symlinks=False)
            require([target_now.st_dev, target_now.st_ino] == entry["identity"] and target_now.st_nlink == 1,
                    "target-replaced-before-rename")
        swap_now = os.stat(swap.name, dir_fd=swap_dir, follow_symlinks=False)
        require((swap_now.st_dev, swap_now.st_ino, swap_now.st_nlink) == (new.st_dev, new.st_ino, 1), "swap-replaced")
        if entry["identity"] is None:
            # macOS SDK sys/stdio.h: RENAME_EXCL=0x4. Kernel no-clobber publication.
            libc = ctypes.CDLL(None, use_errno=True)
            rename = libc.renameatx_np
            rename.argtypes = [ctypes.c_int, ctypes.c_char_p, ctypes.c_int, ctypes.c_char_p, ctypes.c_uint]
            rename.restype = ctypes.c_int
            if rename(swap_dir, os.fsencode(swap.name), target_dir, os.fsencode(target.name), 0x4) != 0:
                raise OSError(ctypes.get_errno(), "exclusive-publication-failed")
        else:
            os.replace(swap.name, target.name, src_dir_fd=swap_dir, dst_dir_fd=target_dir)
        os.fsync(target_dir)
        os.fsync(swap_dir)
        after = dict(entry, identity=[new.st_dev, new.st_ino], sha256=sha(raw))
        require(file_bytes(after, identities) == raw, "write-postcondition")
        return {"sha256": sha(raw), "bytes": len(raw), "mode": entry["mode"], "identity": after["identity"]}
    finally:
        os.close(target_dir)
        os.close(swap_dir)


class GFM:
    """Pinned marked UMD evaluated with no process/require/fetch/host IO bindings."""
    def __init__(self, parser, expected):
        p = Path(parser)
        require(p.is_absolute() and p.resolve(strict=True) == p, "parser-path")
        source = p.read_bytes()
        require(sha(source) == expected, "parser-drift")
        c = ctypes
        self.lib = c.CDLL("/System/Library/Frameworks/JavaScriptCore.framework/JavaScriptCore")
        v = c.c_void_p
        signatures = [
            ("JSGlobalContextCreate", [v], v), ("JSGlobalContextRelease", [v], None),
            ("JSStringCreateWithUTF8CString", [c.c_char_p], v), ("JSStringRelease", [v], None),
            ("JSEvaluateScript", [v, v, v, v, c.c_int, c.POINTER(v)], v),
            ("JSValueToStringCopy", [v, v, c.POINTER(v)], v),
            ("JSStringGetMaximumUTF8CStringSize", [v], c.c_size_t),
            ("JSStringGetUTF8CString", [v, v, c.c_size_t], c.c_size_t),
        ]
        for name, args, result in signatures:
            function = getattr(self.lib, name)
            function.argtypes, function.restype = args, result
        self.context = self.lib.JSGlobalContextCreate(None)
        require(bool(self.context), "gfm-context")
        self.evaluate(source.decode("utf-8"))
        require(self.evaluate("typeof process+':'+typeof require+':'+typeof fetch") == "undefined:undefined:undefined",
                "gfm-host-bindings")

    def evaluate(self, source):
        c, lib = ctypes, self.lib
        script = lib.JSStringCreateWithUTF8CString(source.encode())
        error = c.c_void_p()
        try:
            value = lib.JSEvaluateScript(self.context, script, None, None, 1, c.byref(error))
            require(not error.value and bool(value), "gfm-evaluation")
            text = lib.JSValueToStringCopy(self.context, value, c.byref(error))
            require(not error.value and bool(text), "gfm-result")
            try:
                buffer = c.create_string_buffer(lib.JSStringGetMaximumUTF8CStringSize(text))
                lib.JSStringGetUTF8CString(text, buffer, len(buffer))
                return buffer.value.decode("utf-8")
            finally:
                lib.JSStringRelease(text)
        finally:
            lib.JSStringRelease(script)

    def render(self, text):
        return self.evaluate("marked.parse(" + json.dumps(text) + ", {gfm:true,async:false})")

    def close(self):
        if self.context:
            self.lib.JSGlobalContextRelease(self.context)
            self.context = None


class DocumentHTML(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.code = 0
        self.literal_emphasis = False
        self.links = []
        self.anchors = set()
        self.heading = None
        self.slugs = {}
        self.unsafe_html = False

    def handle_starttag(self, tag, attrs):
        values = dict(attrs)
        if tag in ("code", "pre"):
            self.code += 1
        if tag in ("script", "iframe", "object", "embed") or any(k.startswith("on") for k in values):
            self.unsafe_html = True
        if tag == "a" and "href" in values:
            self.links.append(values["href"])
        if tag == "img" and "src" in values:
            self.links.append(values["src"])
        if values.get("id"):
            self.anchors.add(values["id"])
        if re.fullmatch("h[1-6]", tag):
            self.heading = []

    def handle_endtag(self, tag):
        if tag in ("code", "pre"):
            self.code = max(0, self.code - 1)
        if re.fullmatch("h[1-6]", tag) and self.heading is not None:
            # GitHub-style heading anchors, Unicode letters retained.
            slug = re.sub(r"[^\w\- ]", "", "".join(self.heading).lower(), flags=re.UNICODE).replace(" ", "-")
            count = self.slugs.get(slug, 0)
            self.slugs[slug] = count + 1
            self.anchors.add(slug + (f"-{count}" if count else ""))
            self.heading = None

    def handle_data(self, text):
        if not self.code and "**" in text:
            self.literal_emphasis = True
        if self.heading is not None:
            self.heading.append(text)


def document_view(entry, raw):
    view = entry.get("view", {"kind": "full"})
    if view == {"kind": "full"}:
        return raw
    exact_keys(view, ("kind", "ranges"))
    require(view["kind"] in ("read-ranges", "replace-range") and isinstance(view["ranges"], list) and
            1 <= len(view["ranges"]) <= 4 and (view["kind"] != "replace-range" or len(view["ranges"]) == 1), "view-contract")
    previous, parts = 0, []
    for pair in view["ranges"]:
        require(isinstance(pair, list) and len(pair) == 2 and all(type(x) is int for x in pair), "view-range")
        begin, end = pair
        require(previous <= begin <= end <= len(raw) and (begin < end or view["kind"] == "replace-range"), "view-range-bounds")
        part = raw[begin:end]
        part.decode("utf-8", errors="strict")
        parts.append(part)
        previous = end
    return b"\n\n<!-- approved excerpt boundary -->\n\n".join(parts)


def read_item(key, entry, raw):
    visible = document_view(entry, raw)
    result = {"file_id": key, "sha256": sha(visible), "content": visible.decode("utf-8")}
    if "view" in entry:
        result.update(file_sha256=entry["sha256"], state="absent" if entry["identity"] is None else "present", view=entry["view"])
    return result


def validate_link_metadata(spec):
    metadata = spec.get("link_metadata", {})
    for name, entry in metadata.items():
        exact_keys(entry, ("identity", "mode", "size", "mtime_ns", "sha256", "anchors"))
        path = Path(name)
        fd = parent_fd(path, spec["parents"])
        try:
            info = os.stat(path.name, dir_fd=fd, follow_symlinks=False)
            require(stat.S_ISREG(info.st_mode) and info.st_nlink == 1 and
                    [info.st_dev, info.st_ino] == entry["identity"] and stat.S_IMODE(info.st_mode) == entry["mode"] and
                    info.st_size == entry["size"] and info.st_mtime_ns == entry["mtime_ns"], "link-metadata-drift")
            if entry["sha256"] is not None:
                require(info.st_size <= 131_072, "link-anchor-file-size")
                opened = os.open(path.name, os.O_RDONLY | os.O_NOFOLLOW | os.O_CLOEXEC, dir_fd=fd)
                with os.fdopen(opened, "rb") as stream:
                    require(document_stat_key(os.fstat(stream.fileno())) == document_stat_key(info), "link-open-drift")
                    raw = stream.read(131_073)
                    require(document_stat_key(os.fstat(stream.fileno())) == document_stat_key(info) and sha(raw) == entry["sha256"], "link-anchor-drift")
                parser = GFM(spec["parser"], spec["parser_sha256"])
                try:
                    doc = DocumentHTML(); doc.feed(parser.render(raw.decode("utf-8"))); doc.close()
                    require(set(entry["anchors"]) <= doc.anchors, "link-anchor-missing")
                finally:
                    parser.close()
            else:
                require(entry["anchors"] == [], "anchor-evidence-missing")
        finally:
            os.close(fd)
    return metadata


def verify(spec, verifier):
    require(verifier in ("DOC-LINKS", "DOC-GFM", "DOC-CLAIMS"), "unknown-verifier")
    entries = spec["files"]
    raw_content = {key: file_bytes(value, spec["parents"]) for key, value in entries.items()}
    content = {key: document_view(entries[key], raw).decode("utf-8") for key, raw in raw_content.items()}
    findings = []
    output_ids = spec["outputs"]
    if verifier == "DOC-CLAIMS":
        rules = spec["claims"]
        require(set(rules) == set(output_ids), "claims-coverage-unavailable")
        for key in output_ids:
            rule = rules[key]
            optional = ("exact_view_sha256",) if "exact_view_sha256" in rule else ()
            exact_keys(rule, ("required", "forbidden", "evidence") + optional)
            if optional:
                expected = rule["exact_view_sha256"]
                require(isinstance(expected, str) and re.fullmatch(r"[0-9a-f]{64}", expected), "claims-exact-view-digest")
                if sha(content[key].encode("utf-8")) != expected:
                    findings.append({"file_id": key, "code": "exact-view-mismatch"})
            require(rule["required"] and rule["evidence"], "claims-oracle-empty")
            for evidence in rule["evidence"]:
                exact_keys(evidence, ("file_id", "quote"))
                require(evidence["file_id"] in content and evidence["quote"] and
                        evidence["quote"] in content[evidence["file_id"]], "claims-evidence-drift")
            for index, item in enumerate(rule["required"]):
                if item not in content[key]:
                    findings.append({"file_id": key, "code": "required-claim-missing", "rule": index})
            for index, item in enumerate(rule["forbidden"]):
                if item in content[key]:
                    findings.append({"file_id": key, "code": "forbidden-claim-present", "rule": index})
    else:
        parser = GFM(spec["parser"], spec["parser_sha256"])
        try:
            rendered = {}
            for key, text in content.items():
                text = raw_content[key].decode("utf-8")
                document = DocumentHTML()
                document.feed(parser.render(text))
                document.close()
                rendered[key] = document
            by_path = {entry["path"]: key for key, entry in entries.items()}
            metadata = validate_link_metadata(spec) if verifier == "DOC-LINKS" else {}
            for key in output_ids:
                doc = rendered[key]
                if doc.unsafe_html:
                    findings.append({"file_id": key, "code": "active-html"})
                if verifier == "DOC-GFM" and doc.literal_emphasis:
                    findings.append({"file_id": key, "code": "literal-emphasis-outside-code"})
                if verifier == "DOC-LINKS":
                    for index, link in enumerate(doc.links):
                        parts = urlsplit(link)
                        if parts.scheme or parts.netloc:
                            if link not in spec["approved_external_links"] or parts.scheme not in ("https", "mailto"):
                                findings.append({"file_id": key, "code": "unapproved-external-link", "link": index})
                            continue
                        require(not parts.query and not unquote(parts.path).startswith("/"), "link-target-outside-scope")
                        destination = os.path.normpath(str(Path(entries[key]["path"]).parent / unquote(parts.path))) if parts.path else entries[key]["path"]
                        require(destination in by_path or destination in metadata, "link-target-outside-scope")
                        if destination in by_path:
                            target_id = by_path[destination]
                            require(entries[target_id]["identity"] is not None, "link-target-absent")
                            anchors = rendered[target_id].anchors
                        else:
                            anchors = metadata[destination]["anchors"]
                        if parts.fragment and unquote(parts.fragment) not in anchors:
                            findings.append({"file_id": key, "code": "missing-anchor", "link": index})
        finally:
            parser.close()
    return {"verifier_id": verifier, "pass": not findings, "findings": findings,
            "inputs": {key: value["sha256"] for key, value in entries.items()},
            "oracle_sha256": sha(canonical({key: spec[key] for key in ("outputs", "claims", "approved_external_links", "parser_sha256")})),
            "boundary": "fixed static checks; human factual review remains required"}


def execute(spec, request):
    fields = ("version", "files", "parents", "outputs", "swap", "parser", "parser_sha256", "claims", "approved_external_links")
    require(spec.get("version") in (1, 2), "worker-version")
    exact_keys(spec, fields + (("link_metadata",) if spec["version"] == 2 else ()))
    require(isinstance(spec["files"], dict), "worker-spec")
    require(set(spec["outputs"]) <= set(spec["files"]) and len(set(spec["outputs"])) == len(spec["outputs"]), "output-ids")
    identities = []
    for key, entry in spec["files"].items():
        require(re.fullmatch(r"[A-Za-z][A-Za-z0-9_-]{0,63}", key), "file-id")
        exact_keys(entry, ("path", "identity", "mode", "sha256") + (("view",) if spec["version"] == 2 else ()))
        require(entry["identity"] is not None or (spec["version"] == 2 and key in spec["outputs"]), "absent-input")
        if entry["identity"] is not None:
            identities.append(tuple(entry["identity"]))
    require(len({entry["path"] for entry in spec["files"].values()}) == len(spec["files"]), "duplicate-path")
    require(not (set(spec.get("link_metadata", {})) & {entry["path"] for entry in spec["files"].values()}), "metadata-scope-overlap")
    require(len(identities) == len(set(identities)), "duplicate-file-alias")
    exact_keys(request, ("tool", "arguments"))
    tool, args = request["tool"], request["arguments"]
    if tool == "u2_read_file":
        exact_keys(args, ("file_ids",))
        ids = args["file_ids"]
        require(isinstance(ids, list) and 1 <= len(ids) <= 8 and all(isinstance(k, str) for k in ids), "read-ids")
        require(len(set(ids)) == len(ids) and set(ids) <= set(spec["files"]), "read-scope")
        result = {"files": [read_item(key, spec["files"][key], file_bytes(spec["files"][key], spec["parents"])) for key in ids]}
        require(len(canonical(result)) <= LIMIT, "read-result-too-large")
        return result
    if tool == "u2_write_file":
        exact_keys(args, ("file_id", "expected_sha256", "content"))
        key = args["file_id"]
        require(key in spec["outputs"] and set(spec["swap"]) == {key}, "write-scope")
        result = atomic_write(spec["files"][key], spec["parents"], spec["swap"][key], args["expected_sha256"], args["content"])
        return {"file_id": key, **result}
    if tool == "u2_verify":
        exact_keys(args, ("verifier_id",))
        return verify(spec, args["verifier_id"])
    raise WorkerRefusal("worker-tool-unavailable")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--spec", type=Path, required=True)
    parser.add_argument("--operation", required=True, choices=["read", "write", "DOC-LINKS", "DOC-GFM", "DOC-CLAIMS"])
    args = parser.parse_args()
    try:
        raw = args.spec.read_bytes()
        require(len(raw) <= 1_048_576, "spec-size")
        spec = json.loads(raw)
        request_raw = sys.stdin.buffer.read(524_289)
        require(len(request_raw) <= 524_288, "request-size")
        request = json.loads(request_raw)
        expected = {"read": "u2_read_file", "write": "u2_write_file"}.get(args.operation, "u2_verify")
        require(request.get("tool") == expected and (expected != "u2_verify" or request.get("arguments", {}).get("verifier_id") == args.operation), "operation-drift")
        result = execute(spec, request)
        output = canonical({"ok": True, "result": result})
        require(len(output) <= 131_072, "result-size")
        sys.stdout.buffer.write(output + b"\n")
        return 0
    except Exception as error:
        # Never echo a filesystem path, document, arbitrary exception or payload.
        code = str(error) if isinstance(error, WorkerRefusal) else type(error).__name__
        print(json.dumps({"ok": False, "code": code}))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
