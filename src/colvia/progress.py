"""User-requested progress on ordinary Work before its first submission."""
import re

from .bodies import BODY_LIMIT
from .codec import RecordError, decode_envelope, require
from .connection import PROJECT_KEY, workspace_key
from .effects import guard
from .graph import Schema
from .records import fields, head_summary, identity, link, one, record
from .tree import logical_path

NOTE_FIELDS = ('done', 'checked', 'remaining', 'next_action')
MAX_PATHS = 128
UNAVAILABLE = 'unavailable'
MISSING = 'missing'


def eligible(head):
    return (head.payload['phase'] == 'active' and not head.payload['archived']
            and link(head, 'approval') is not None
            and link(head, 'result') is None and link(head, 'context') is None)


def validate_fingerprints(files):
    require(isinstance(files, dict) and len(files) <= MAX_PATHS, 'invalid-progress-files')
    for path, fingerprint in files.items():
        require(logical_path(path) == path and isinstance(fingerprint, str) and
                (fingerprint in (UNAVAILABLE, MISSING) or re.fullmatch('[0-9a-f]{64}', fingerprint)),
                'invalid-progress-files')


def validate_payload(payload):
    fields(payload, {'work', 'workspace', 'files', *NOTE_FIELDS})
    identity(payload)
    for name in NOTE_FIELDS:
        value = payload[name]
        require(isinstance(value, str) and 0 < len(value) <= 2048, 'invalid-progress-text')
        require(value.strip() and value.isprintable(), 'invalid-progress-text')
    validate_fingerprints(payload['files'])
    one(payload, 'active')
    one(payload, 'previous', True)


def validate_content(ref, load):
    note = decode_envelope(ref, load(ref))
    active = link(note, 'active')
    head, plan, _, _ = head_summary(active, load)
    require(eligible(head) and all(note.payload[k] == head.payload[k] for k in ('work', 'workspace')),
            'progress-work-mismatch')
    scope = plan.payload['scope']
    require(set(note.payload['files']) == set(scope[:MAX_PATHS]), 'invalid-progress-files')
    previous = link(note, 'previous')
    if previous is not None:
        prior = decode_envelope(previous, load(previous))
        require(previous.kind == 'work.progress' and previous.version == 1 and
                all(prior.payload[k] == note.payload[k] for k in ('work', 'workspace')), 'progress-work-mismatch')
    return head


def schema():
    return Schema('work.progress', 1, {'active':'decision', 'previous':'provenance'},
                  validate_payload, {'active':frozenset({'work.head'}), 'previous':frozenset({'work.progress'})},
                  content=validate_content)


def fingerprints(workspace, scope):
    """Only hash approved individual files. Unknown observations never imply equality."""
    files = {}
    remaining = workspace.budget.read_bytes
    with workspace.selected_reader(verify_path=True) as read:
        for path in scope[:MAX_PATHS]:
            limit = min(BODY_LIMIT, remaining)
            try:
                entries = read([path], limit)
            except (OSError, RecordError) as exc:
                if isinstance(exc, RecordError) and exc.code not in FILE_ERRORS:
                    raise
                # A failed read can consume its full allowance before failing.
                remaining = max(0, remaining - limit)
                files[path] = UNAVAILABLE
                continue
            if not entries:
                files[path] = MISSING
            elif entries[0]['kind'] == 'regular':
                remaining -= entries[0]['size']
                files[path] = entries[0]['sha256']
            else:
                files[path] = UNAVAILABLE
    return files


FILE_ERRORS = frozenset(('unsafe-scope-ancestor', 'scope-entry-not-regular', 'file-observation-changed',
                         'observation-byte-limit', 'path-collision', 'opaque-entry-changed',
                         'opaque-entry-type-changed', 'observation-entry-limit', 'windows-reparse-or-changing-file',
                         'progress-nested-project', 'file-identity-unavailable', 'invalid-path',
                         'path-size-or-component', 'windows-final-path-mismatch', 'windows-parent-not-directory'))


def difference(before, after):
    if UNAVAILABLE in (before, after):
        return UNAVAILABLE
    if before == after:
        return 'unchanged'
    if before == MISSING:
        return 'created'
    if after == MISSING:
        return 'deleted'
    return 'changed'


def receipt(service, work, active, latest):
    return service._receipt('progress:' + (latest.sha256 if latest else 'first'), work, active)


def save(service, work, operation, expected_receipt, contents):
    from .work import work_key
    active, head = service._head(work)
    require(eligible(head), 'progress-first-submission-only')
    key = 'progress:' + work
    store, workspace = service.store, service.workspace
    previous = store.head(key)
    require(expected_receipt == receipt(service, work, active, previous), 'progress-view-stale')
    registration, _, _ = workspace.verify()
    expected = {work_key(work):active, key:previous, workspace_key(workspace.workspace):registration,
                PROJECT_KEY:store.head(PROJECT_KEY)}
    scope = service._object(link(head, 'plan')).payload['scope']
    payload = dict(work=work, workspace=workspace.workspace, files=fingerprints(workspace, scope), **contents)
    pair = record('work.progress', payload, {'active':('decision', active), 'previous':('provenance', previous)})

    service.registry.inspect(*pair, required=True)

    def validate(load):
        guard(load)
        validate_content(pair[0], load)
        workspace.verify()

    store.commit_heads(operation=operation, expected=expected, changes={key:pair[0]},
                       objects=[pair], validate=validate)
    return dict(work=work, state='active', progress_saved=True)


def compare_files(workspace, scope, saved):
    try:
        current = fingerprints(workspace, scope)
    except (OSError, RecordError) as exc:
        # Keep the note readable if file observation alone fails. The project
        # identity, storage capabilities and integrity checks still have to pass.
        if isinstance(exc, RecordError) and exc.code not in ('git-observation-changed', 'invalid-git-tree'):
            raise
        workspace.verify()
        current = dict.fromkeys(saved, UNAVAILABLE)
    return [{'path': path, 'status': difference(before, current[path])} for path, before in saved.items()]


def view(service, work, head, scope, amendments=()):
    key = 'progress:' + work
    latest = service.store.head(key)
    value = dict(progress_receipt=receipt(service, work, head.ref, latest),
                 first_project_note=latest is None and 'schema:work.progress:1' not in service.store.requirements()['read'])
    if latest is not None:
        note = service._object(latest)
        require(latest.kind == 'work.progress' and
                all(note.payload[k] == head.payload[k] for k in ('work', 'workspace')), 'progress-work-mismatch')
        original = validate_content(latest, service.store.load)
        same_approval = all(link(original, k) == link(head, k) for k in ('plan', 'approval'))
        inherited = not same_approval and any(link(basis,'approval') == link(original,'approval')
                                             for _,basis in amendments)
        saved = note.payload['files']
        files = compare_files(service.workspace, sorted(saved), saved) if same_approval or inherited else []
        appended = sorted(set(scope) - set(service._object(link(original,'plan')).payload['scope'])) if inherited else []
        value['progress'] = {**{k: note.payload[k] for k in NOTE_FIELDS}, 'files': files,
                             'same_approval': same_approval, 'added_after_note': appended,
                             'additional_paths_unavailable': len(scope) - len(files) - len(appended)}
    require(service.store.head(key) == latest and service.store.head('work:' + work) == head.ref, 'progress-view-stale')
    return value
