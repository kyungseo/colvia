"""Bounded exposure checks reused from the existing qualified execution floor.

These fixed patterns are neither general secret detection nor human approval.
No rejected text or digest is logged. Payload and record integer bounds differ.
"""
import json,re,time
from ..codec import RecordError,require
from ..credentials import KEY_OR_BEARER, PROVIDER_TOKEN

HostRefusal=RecordError

def wire_bytes(value):
    return json.dumps(value,ensure_ascii=False,sort_keys=True,separators=(",",":"),allow_nan=False).encode()

def reject_duplicate_keys(pairs):
    result = {}
    for key, value in pairs:
        require(key not in result, "duplicate RPC/JSON key")
        result[key] = value
    return result

def safe_text(text, allowed_identifiers=()):
    require(isinstance(text, str) and "\x00" not in text, "nontext or NUL document")
    # These are exposure guards, not a proof of factual correctness. Approved
    # source identifiers are enumerated in the Owner's transmission packet.
    residue = text
    for literal in sorted(allowed_identifiers, key=len, reverse=True):
        require(isinstance(literal, str) and len(literal) >= 3, "invalid approved identifier")
        residue = residue.replace(literal, "[approved]")
    require(not re.search(r"(?i)(?:" + KEY_OR_BEARER + r"|(?:access_token|refresh_token|api_key)\s*[=:]\s*[^\s,}]{8,})", text), "credential-like content")
    require(not re.search(r"(?:/Users/[^\s<>\"']+|/home/[^\s<>\"']+|[A-Za-z]:\\[^\s<>\"']+|[\w.+-]+@[\w.-]+\.[A-Za-z]{2,})", residue), "unapproved document identifier")


_CREDENTIAL = re.compile(
    r"(?i)(?:[\"']?(?:password|passwd|secret|api_key|access_token|refresh_token)[\"']?"
    r"\s*[=:]\s*[\"']?[^\s,}\"']{8,}|" + PROVIDER_TOKEN + ")")


def checked_payload(value, *, limit=65536, deadline=None, protocol=False):
    """Return the exact checked JSON bytes. No IO, source text or hash logging.

    protocol permits required runtime paths, never credential patterns. Data
    payloads additionally retain the existing unapproved-identifier guard.
    Fixed bounds avoid recursion/size abuse; errors refuse before any sink write.
    """
    def clock():
        if deadline is not None and time.monotonic() >= deadline:
            raise TimeoutError('deadline')
    clock()
    todo = [(value, 0)]; nodes = size = 0
    try:
        while todo:
            clock()
            item, depth = todo.pop(); nodes += 1
            require(depth <= 16 and nodes <= 4096, 'content_rejected')
            if type(item) is str:
                require(len(item) <= limit, 'content_rejected')
                size += len(item.encode('utf-8'))
                require(size <= limit and not any(ord(c) < 32 and c not in '\n\r\t' for c in item), 'content_rejected')
                # Identifier exceptions never disable safe_text's secret check.
                safe_text(item, (item,) if len(item) >= 3 else ())
                if not protocol:
                    # Bound identifier components instead of running the legacy
                    # unbounded email expression over a long unbroken string.
                    require(not re.search(r'(?:/Users/|/home/|[A-Za-z]:\\|[\w.+-]{1,64}@[\w.-]{1,253}\.[A-Za-z]{2,63})', item),
                            'unapproved document identifier')
                require(_CREDENTIAL.search(item) is None, 'content_rejected')
            elif type(item) in (dict, list):
                require(len(item) <= 4096 and len(todo) + len(item) * 2 <= 8192, 'content_rejected')
                if type(item) is dict:
                    require(all(type(k) is str for k in item), 'content_rejected')
                    todo.extend((v, depth + 1) for pair in item.items() for v in pair)
                else:
                    todo.extend((v, depth + 1) for v in item)
            else:
                require(item is None or type(item) is bool or (type(item) is int and abs(item) < 2**64), 'content_rejected')
        raw = wire_bytes(value)
        require(len(raw) <= limit, 'content_rejected')
        require(_CREDENTIAL.search(raw.decode('utf-8')) is None, 'content_rejected')
    except (UnicodeError, ValueError, TypeError, RecursionError):
        raise HostRefusal('content_rejected') from None
    clock()
    return raw


def checked_preserved_output(record, raw, *, deadline=None):
    """Refuse immutable output context before granting or starting the CLI.

    Replacement boundaries are checked again against the complete new output
    before the writer. Inspecting context does not transmit it to the model.
    """
    require(record['view']['kind'] == 'replace-range', 'content_rejected')
    begin, end = record['view']['ranges'][0]
    for part in (raw[:begin], raw[end:]):
        checked_payload(part.decode('utf-8'), limit=262144, deadline=deadline)
