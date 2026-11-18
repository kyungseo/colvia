"""Local credential rules. Findings contain locations and categories only."""
import json
import re

from .codec import RecordError

# These two patterns retain the exact token families used by the execution gate.
KEY_OR_BEARER = r"sk-[A-Za-z0-9_-]{16,}|-----BEGIN [A-Z ]*PRIVATE KEY-----|Bearer\s+[A-Za-z0-9._-]{12,}"
PROVIDER_TOKEN = r"gh[pousr]_[a-z0-9]{20,}|github_pat_[a-z0-9_]{20,}|AKIA[A-Z0-9]{16}"

_TOKEN = re.compile(r"(?<![a-z0-9])(?:" + KEY_OR_BEARER + "|" + PROVIDER_TOKEN +
                    r"|-----BEGIN PGP PRIVATE KEY BLOCK-----|sk_live_[a-z0-9]{16,})", re.I | re.ASCII)
_URL = re.compile(r"[a-z][a-z0-9+.-]{0,30}://[^/\s:@]+:([^/@\s]+)@", re.I | re.ASCII)
_FIELD = (r"""(?<![\w-])["']?(?:[a-z][a-z0-9]*[_-])*(?:password|passwd|secret|"""
          r"""api[_-]?key|(?:secret|private|access)[_-]key|(?:auth|access|refresh)[_-]?token|token)["']?[ \t]*""")
_ASSIGN = re.compile(_FIELD + r"(?:=(?!=|>)|:)[ \t]*", re.I | re.ASCII)
_VALUE = re.compile(r"""(?:"([^"\n]*)"|'([^'\n]*)'|([^\s,;\]#]+))""")
_CONTINUED = re.compile(r"^[ \t]*[{,]?[ \t]*" + _FIELD + r":[ \t]*\Z", re.I | re.ASCII)
_ENV_READ = re.compile(
    r"(?:process\.env\.[A-Za-z_]\w*|os\.(?:getenv|environ\.get)\(['\"][A-Za-z_]\w*['\"]\)"
    r"|os\.environ\[['\"][A-Za-z_]\w*['\"]\]|\$\{\{[ \t]*(?:secrets|env)\.[A-Za-z_]\w*[ \t]*\}\})"
    r"(?=[ \t]*(?:$|[,;#)}\]]))", re.ASCII)
_CODE_SUFFIXES = ('.py', '.js', '.ts', '.tsx', '.jsx', '.go', '.java', '.cs', '.rs', '.kt')
_IDENT = r"[A-Za-z_]\w*(?:\.[A-Za-z_]\w*)*"
_LOOKUP_KEY = r"""['"][A-Za-z_]\w*['"]"""
_NAME_ARGS = _IDENT + r"(?:[ \t]*,[ \t]*" + _IDENT + r")*"
# Accept plain references, indexed settings, and calls with variable arguments.
# Match the complete expression so a literal fallback still receives scrutiny.
_CODE_EXPRESSION = re.compile(
    rf"(?:{_IDENT}(?:\(\)|\[{_LOOKUP_KEY}\]|\([ \t]*{_NAME_ARGS}[ \t]*\))?"
    rf"|{_IDENT}\.getItem\({_LOOKUP_KEY}\))(?=[ \t]*(?:$|[,;#:)}}\]]))", re.ASCII)
_MAPPING_CHILD = re.compile(r"""^(?:[A-Za-z_][\w.-]*|"[^"]+"|'[^']+'):(?=[ \t]|$)""")

_REFERENCE = re.compile(
    r"(?:\$\{[A-Za-z_]\w*\}|\$(?:env:)?[A-Za-z_]\w*|%[A-Za-z_]\w*%|"
    r"<(?:your-api-key|your-password|redacted)>)\Z", re.ASCII)

REVIEW_HEADER = b'Colvia Git review v3\n'
LINE_LIMIT = 256 * 1024


class GitContentRefusal(RecordError):
    def __init__(self, category, where, line):
        codes = {'uninspectable': 'git-content-uninspectable', 'protected-path': 'git-protected-path',
                 'protected-copy': 'git-protected-copy'}
        super().__init__(codes.get(category, 'git-credential-blocked'))
        self.finding = dict(category=category, location=where, line=line)


def protected_git_path(path):
    """Match complete components in Colvia's canonical repository-relative path."""
    *parents, filename = path.lower().split('/')
    return (filename in ('.env', '.env.local', '.env.production', '.netrc', '_netrc')
            or filename.endswith(('.tfstate', '.tfstate.backup'))
            or re.search(r'\.tfstate\.[0-9]+\.backup\Z', filename) is not None
            or 'secrets' in parents)


_NPM_AUTH = {'_auth', '_authtoken', '_password', 'password', 'key'}
_NPM_ENV = re.compile(r"\$\{[A-Za-z_][A-Za-z_0-9]*\??\}")


def _npm_uncomment(text):
    # In an unquoted INI value a backslash escapes the next delimiter.
    escaped = False
    for index, char in enumerate(text):
        if not escaped and char in ';#':
            return text[:index].rstrip()
        escaped = char == '\\' and not escaped
    return text


def npm_auth_value(line):
    """Return the raw value for each auth assignment, including duplicates."""
    # npm's INI reader treats a BOM like whitespace when trimming a key.
    line = line.replace('\ufeff', ' ').strip()
    if not line or line.startswith(('#', ';', '[')):
        return None
    key, separator, value = line.partition('=')
    key = key.strip()
    if len(key) >= 2 and key[0] == key[-1] and key[0] in "\"'":
        key = key[1:-1] if key[0] == "'" else key
        if key.startswith('"'):
            try:
                key = json.loads(key)
            except ValueError:
                pass
    else:
        key = _npm_uncomment(key)
    name = key.rsplit(':', 1)[-1].removesuffix('[]').lower()
    if name not in _NPM_AUTH:
        return None
    if not separator:
        return 'true'  # An INI setting without an equals sign has an implicit value.
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
        return value[1:-1]
    # Escaped delimiters are literal data. Leave them in the value to fail closed.
    value = _npm_uncomment(value)
    if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
        return value[1:-1]
    return value


def category(line, where=''):
    for match in _TOKEN.finditer(line):
        if match[0].casefold().rstrip('.') != 'bearer authentication' or line[:match.start()].rstrip().endswith(':'):
            return 'key-or-token'
    for match in _URL.finditer(line):
        if not _REFERENCE.fullmatch(match[1]):
            return 'url-credential'
    if where.rsplit('/', 1)[-1].lower() == '.npmrc':
        value = npm_auth_value(line)
        if value is not None:
            if value and not _NPM_ENV.fullmatch(value):
                return 'npm-auth-literal'
            # Keep the ordinary assignment check for other values in the line,
            # including configuration examples written in a trailing comment.
            line = line.partition('=')[2]
    for field in _ASSIGN.finditer(line):
        match = _VALUE.match(line, field.end())
        if match is None:
            continue
        value = next(group for group in match.groups() if group is not None)
        quoted = match[3] is None
        if quoted and value.startswith('${{') and _ENV_READ.fullmatch(value):
            continue
        if not quoted:
            if _ENV_READ.match(line, match.start(3)):
                continue
            if where.lower().endswith(_CODE_SUFFIXES) and _CODE_EXPRESSION.match(line, field.end()):
                continue
            if value.rstrip('}') in ('null', 'true', 'false') or value.startswith(('{"', "{'")) or value in ('{', '['):
                # Nested fields and recognized tokens still receive their own checks.
                continue
        if value and not _REFERENCE.fullmatch(value):
            return 'credential-assignment'
    return None


def screen_candidate(changes, body, message, identity, operation):
    inspect_chunks([operation.encode()], 'operation')
    inspect_chunks([message.encode()], 'commit-message')
    for field, value in identity.items():
        inspect_chunks([value.encode()], 'author-' + field)
    for number, path in enumerate(sorted(changes), 1):
        inspect_chunks([path.encode()], 'path-' + str(number))
        if changes[path] is not None:
            if protected_git_path(path):
                raise GitContentRefusal('protected-path', path, None)
            inspect_chunks(body(path), path)


def inspect_chunks(chunks, where):
    """Stream bounded UTF-8 lines; keep split UTF-8 and split tokens together."""
    pending = bytearray()
    number = 1
    continued = False

    def inspect_line(raw):
        nonlocal continued
        try:
            text = raw.decode('utf-8')
        except UnicodeDecodeError:
            raise GitContentRefusal('uninspectable', where, number) from None
        if any((ord(c) < 32 or 127 <= ord(c) <= 159) and c not in '\r\t' for c in text):
            raise GitContentRefusal('uninspectable', where, number)
        if number == 1 and text.lstrip('\ufeff').startswith(('%PDF-', '-----BEGIN PGP MESSAGE-----')):
            raise GitContentRefusal('uninspectable', where, number)
        # A quoted JSON scalar may follow the field on the next line.
        text = text.rstrip('\r')
        if '\r' in text and where.rsplit('/', 1)[-1].lower() == '.npmrc':
            raise GitContentRefusal('uninspectable', where, number)
        child = text.lstrip()
        if continued and child and not child.startswith('#') and not _MAPPING_CHILD.match(child):
            found = category('password: ' + child, where)
            if found:
                raise GitContentRefusal(found, where, number)
        if child and not child.startswith('#'):
            continued = bool(_CONTINUED.search(text))
        found = category(text, where)
        if found:
            raise GitContentRefusal(found, where, number)

    for chunk in chunks:
        parts = chunk.split(b'\n')
        for i, part in enumerate(parts):
            if i:
                inspect_line(pending)
                pending.clear()
                number += 1
            if len(pending) + len(part) > LINE_LIMIT:
                raise GitContentRefusal('uninspectable', where, number)
            pending.extend(part)
    inspect_line(pending)
