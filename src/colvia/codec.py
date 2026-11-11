"""Bounded canonical objects and schema-constrained dependency envelopes.

This module has no filesystem, Git, host, or acceptance effects. Content identity
is not authorization. Application schemas must validate payload fields and use
fixed field roles before interpreting an envelope.
"""
from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
import re
from typing import Callable, Mapping

METADATA_LIMIT = 4 * 1024 * 1024
CHUNK_LIMIT = 1024 * 1024
JSON_DEPTH_LIMIT = 64
JSON_NODE_LIMIT = 1_000_000
DOMAIN = b"colvia.object\x00v1\x00"
ROLES = frozenset({"decision", "integrity", "provenance", "display"})
_KIND = re.compile(r"[a-z][a-z0-9]*(?:[.-][a-z0-9]+)*\Z", re.ASCII)
_SHA = re.compile(r"[0-9a-f]{64}\Z", re.ASCII)


class RecordError(ValueError):
    """Untrusted record bytes cannot establish the requested fact."""

    def __init__(self, code: str):
        self.code = code
        super().__init__(code)


class PublicationRefused(RecordError):
    """Trusted publisher proved this attempt did not commit; no replay permission."""


def require(condition: bool, code: str) -> None:
    if not condition:
        raise RecordError(code)


def _check_json(value: object) -> None:
    stack = [(value, 0)]
    nodes = 0
    while stack:
        item, depth = stack.pop()
        nodes += 1
        require(nodes <= JSON_NODE_LIMIT and depth <= JSON_DEPTH_LIMIT,
                "metadata-structure-limit")
        if type(item) is dict:
            require(all(type(key) is str for key in item), "non-string-key")
            require(nodes + len(stack) + 2*len(item) <= JSON_NODE_LIMIT, "metadata-structure-limit")
            stack.extend((part, depth + 1) for pair in item.items() for part in pair)
        elif type(item) is list:
            require(nodes + len(stack) + len(item) <= JSON_NODE_LIMIT, "metadata-structure-limit")
            stack.extend((part, depth + 1) for part in item)
        elif type(item) is str:
            try:
                item.encode("utf-8", errors="strict")
            except UnicodeError:
                raise RecordError("invalid-unicode") from None
        else:
            require(item is None or type(item) in (bool, int), "unsupported-json-value")


def canonical_bytes(value: object) -> bytes:
    _check_json(value)
    try:
        raw = (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True,
                          allow_nan=False) + "\n").encode("utf-8")
    except (ValueError, RecursionError, UnicodeError):
        raise RecordError("metadata-encoding") from None
    require(len(raw) <= METADATA_LIMIT, "metadata-size-limit")
    return raw


def _pairs(pairs: list[tuple[str, object]]) -> dict:
    result = {}
    for key, value in pairs:
        require(key not in result, "duplicate-key")
        result[key] = value
    return result


def _constant(_: str) -> None:
    raise RecordError("non-finite-json")


def decode_canonical(raw: bytes) -> object:
    require(type(raw) is bytes and len(raw) <= METADATA_LIMIT, "metadata-size-limit")
    try:
        value = json.loads(raw.decode("utf-8"), object_pairs_hook=_pairs,
                           parse_constant=_constant)
    except RecordError:
        raise
    except (ValueError, UnicodeError, RecursionError):
        raise RecordError("invalid-json") from None
    require(canonical_bytes(value) == raw, "noncanonical-json")
    return value


@dataclass(frozen=True, slots=True)
class ObjectRef:
    kind: str
    version: int
    byte_length: int
    sha256: str

    def __post_init__(self) -> None:
        require(type(self.kind) is str and len(self.kind) <= 64 and
                _KIND.fullmatch(self.kind) is not None, "invalid-kind")
        require(type(self.version) is int and 1 <= self.version <= 0xFFFFFFFF,
                "invalid-version")
        limit = CHUNK_LIMIT if self.kind == "body.chunk" else METADATA_LIMIT
        require(type(self.byte_length) is int and 0 <= self.byte_length <= limit,
                "object-size-limit")
        require(type(self.sha256) is str and _SHA.fullmatch(self.sha256) is not None,
                "invalid-digest")

    def as_dict(self) -> dict:
        return dict(kind=self.kind, version=self.version,
                    byte_length=self.byte_length, sha256=self.sha256)

    @classmethod
    def parse(cls, value: object) -> ObjectRef:
        require(type(value) is dict and set(value) ==
                {"kind", "version", "byte_length", "sha256"}, "invalid-reference")
        return cls(**value)


def object_ref(kind: str, version: int, raw: bytes) -> ObjectRef:
    require(type(raw) is bytes, "non-byte-object")
    # Validate types/limits before encoding or hashing untrusted fields.
    shape = ObjectRef(kind, version, len(raw), "0" * 64)
    tag = shape.kind.encode("ascii")
    preimage = (DOMAIN + len(tag).to_bytes(2, "big") + tag +
                version.to_bytes(4, "big") + len(raw).to_bytes(8, "big") + raw)
    return ObjectRef(kind, version, len(raw), hashlib.sha256(preimage).hexdigest())


def verify_object(ref: ObjectRef, raw: bytes) -> None:
    require(object_ref(ref.kind, ref.version, raw) == ref, "object-identity-mismatch")


@dataclass(frozen=True, slots=True)
class Edge:
    role: str
    ref: ObjectRef

    def __post_init__(self) -> None:
        require(type(self.role) is str and self.role in ROLES, "unknown-edge-role")
        require(type(self.ref) is ObjectRef, "invalid-edge-reference")

    def as_dict(self) -> dict:
        return dict(role=self.role, ref=self.ref.as_dict())

    @classmethod
    def parse(cls, value: object) -> Edge:
        require(type(value) is dict and set(value) == {"role", "ref"}, "invalid-edge")
        return cls(value["role"], ObjectRef.parse(value["ref"]))


@dataclass(frozen=True, slots=True)
class Envelope:
    """Verified generic representation; interpretation still requires its schema."""
    ref: ObjectRef
    edges: tuple[Edge, ...]
    payload: dict


def encode_envelope(kind: str, version: int, payload: dict,
                    edges: tuple[Edge, ...] = ()) -> tuple[ObjectRef, bytes]:
    require(type(payload) is dict, "invalid-payload")
    require(kind != "body.chunk", "chunk-is-raw")
    require(type(edges) is tuple and all(type(edge) is Edge for edge in edges),
            "invalid-edges")
    raw = canonical_bytes(dict(envelope_version=1,
                               edges=[edge.as_dict() for edge in edges], payload=payload))
    return object_ref(kind, version, raw), raw


def decode_envelope(ref: ObjectRef, raw: bytes) -> Envelope:
    verify_object(ref, raw)
    require(ref.kind != "body.chunk", "chunk-is-raw")
    value = decode_canonical(raw)
    require(type(value) is dict and set(value) ==
            {"envelope_version", "edges", "payload"}, "invalid-envelope")
    require(type(value["envelope_version"]) is int and value["envelope_version"] == 1,
            "unknown-envelope-version")
    require(type(value["edges"]) is list and type(value["payload"]) is dict,
            "invalid-envelope")
    return Envelope(ref, tuple(Edge.parse(edge) for edge in value["edges"]), value["payload"])


def validate_schema(envelope: Envelope, *, kind: str, version: int,
                    fields: Mapping[str, str], validate_payload: Callable[[dict], None]) -> None:
    """Validate a known schema with exactly one fixed role per named field.

    `fields` and `validate_payload` are trusted, product-owned schema constants,
    never supplied by the record. Payload.links maps field names to edge-index
    lists. A schema's payload validator owns all other keys and their types.
    """
    require(envelope.ref.kind == kind and envelope.ref.version == version,
            "unknown-required-kind")
    require(all(type(name) is str and type(role) is str and role in ROLES
                for name, role in fields.items()), "invalid-schema")
    payload = envelope.payload
    links = payload.get("links")
    require(type(links) is dict and set(links) == set(fields), "invalid-edge-fields")
    used = set()
    for name, indices in links.items():
        require(type(indices) is list, "invalid-edge-indices")
        for index in indices:
            require(type(index) is int and 0 <= index < len(envelope.edges) and
                    index not in used, "invalid-edge-index")
            used.add(index)
            require(envelope.edges[index].role == fields[name], "edge-role-mismatch")
    require(len(used) == len(envelope.edges), "unbound-edge")
    # Known metadata must not hide raw object-reference dictionaries in payload.
    stack = [payload]
    while stack:
        item = stack.pop()
        if type(item) is dict:
            require(not {"kind", "version", "byte_length", "sha256"}.issubset(item),
                    "hidden-object-reference")
            stack.extend(item.values())
        elif type(item) is list:
            stack.extend(item)
    validate_payload(payload)
