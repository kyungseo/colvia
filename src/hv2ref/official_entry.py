"""Explicit installed official execution entry. No source fallback or Core apply."""
from pathlib import Path
import json
import os
import stat
import sys
import time
import tomllib
from . import official_state as state
from .official_documents import file_record, initial_view_contracts, pack_reads, wire_bytes
from .official_policy import canonical_existing, PARAMETERS

CLI_SHA256 = 'a45099154d7fb4a5ed8a56f40966a95deb938e508bab23e6985035c709e9a85a'
HELPER_SHA256 = 'e723d01c65aba4b81451d486d57318232b2738889de67c35051734be917d96ba'
PATH_KEYS = PARAMETERS - {'PYROOT', 'RUNTIME', 'SESSION'}
PINNED_INPUTS = PATH_KEYS - {'CODEX_AUTH', 'INSTALLATION_ID', 'CODEX_RULES_DIR'}

def exact(value, keys, code):
    state.need(type(value) is dict and set(value) == set(keys), code)

def runtime_input(value):
    exact(value, {'paths', 'sha256'}, 'runtime-fields')
    exact(value['paths'], PATH_KEYS, 'runtime-path-set')
    exact(value['sha256'], PINNED_INPUTS, 'runtime-pin-set')
    paths = {key: canonical_existing(raw, key == 'CODEX_RULES_DIR') for key, raw in value['paths'].items()}
    home = Path.home().resolve()
    state.need(paths['CODEX_CONFIG'] == home / '.codex/config.toml' and
               paths['CODEX_AUTH'] == home / '.codex/auth.json' and
               paths['INSTALLATION_ID'] == home / '.codex/installation_id', 'default-auth-home-required')
    state.need(paths['CODEX_RULES_DIR'] == home / '.codex/rules' and
               paths['CODEX_RULES_FILE'].parent == paths['CODEX_RULES_DIR'], 'rules-home')
    state.need(paths['CODE_MODE_HOST'] == paths['BIN'].with_name('codex-code-mode-host'), 'helper-location')
    state.need(value['sha256']['BIN'] == CLI_SHA256 and value['sha256']['CODE_MODE_HOST'] == HELPER_SHA256, 'unqualified-cli-helper')
    for key in PINNED_INPUTS:
        state.need(state.digest(state.regular(paths[key], 512 * 1024 * 1024)) == value['sha256'][key], 'runtime-input-drift:' + key)
    config = tomllib.loads(state.regular(paths['CODEX_CONFIG']).decode())
    state.need(config.get('model_provider') in (None, 'openai') and not config.get('model_providers'), 'custom-provider-not-admitted')
    state.need(not any(config.get(k) for k in ('instructions', 'developer_instructions', 'model_instructions_file')), 'configured-instructions-not-admitted')
    state.need(not any(os.environ.get(k) for k in ('OPENAI_API_KEY', 'CODEX_API_KEY', 'OPENAI_BASE_URL', 'CODEX_API_BASE', 'CHATGPT_BASE_URL', 'HTTP_PROXY', 'HTTPS_PROXY', 'ALL_PROXY', 'CODEX_HOME')), 'api-auth-override-not-admitted')
    return {key: str(path) for key, path in paths.items()}

def observe_work(target, request, *, after_effect=False):
    from .product import require_workspace_runtime, verify_workspace_product
    from .work import WorkStore, snapshot, _git
    from .intent import require_no_pending_intents
    from .continuation import require_no_pending
    runtime = require_workspace_runtime(target)
    state.need(runtime['inventory_id'] == state.WINDOW, 'official-window-required')
    store = WorkStore(target)
    works = store._all()
    require_no_pending_intents(target); require_no_pending(target, works=works)
    state.need(all(not g['pending_decisions'] and not g['pending_selections'] for g in works.values()), 'pending-work')
    state.need(request['work_id'] in works, 'work-not-found')
    graph = works[request['work_id']]
    state.need(graph['state'] == 'active' and graph['current'] is not None, 'work-not-active')
    selected = graph['selections'][graph['current']['selection_ref']['id']]
    revision = graph['revisions'][selected['revision_ref']['id']]
    store._intent(revision, graph['identity'])
    state.need(revision['schema_version'] == 1, 'ordinary-work-only')
    worker_root = canonical_existing(request['worker_root'], True)
    if revision['execution_context']['mode'] == 'local':
        state.need(worker_root == target, 'local-worker-root')
    else:
        state.need(revision['execution_context']['mode'] == 'isolated-worktree', 'work-mode')
        from .workspace import classify_target
        state.need(classify_target(worker_root)['kind'] == 'linked-worktree', 'registered-worker-required')
        args = ('rev-parse', '--path-format=absolute', '--git-common-dir')
        state.need(_git(target, *args).stdout == _git(worker_root, *args).stdout, 'worker-repository')
        registrations = _git(target, 'worktree', 'list', '--porcelain', '-z').stdout.split(b'\0')
        state.need(b'worktree ' + os.fsencode(worker_root) in registrations, 'worker-registration')
    observed = snapshot(worker_root, verified_launcher_sha256=runtime['launcher_sha256'], verified_inventory_id=runtime['inventory_id'])
    if revision['execution_context']['mode'] == 'isolated-worktree':
        manifest = graph['manifests'][revision['result_refs']['manifest']['id']]
        state.need((after_effect or observed == manifest['result']) and _git(worker_root, 'rev-parse', 'HEAD').stdout.decode().strip() == manifest['candidate_commit'], 'worker-baseline')
    product = verify_workspace_product(target)
    return {'identity': graph['identity'], 'selection_ref': graph['current']['selection_ref'],
            'revision_ref': selected['revision_ref'], 'intent_ref': revision['intent_ref'],
            'scope': revision['scope'], 'mode': revision['execution_context']['mode'],
            'worker_snapshot': observed, 'product_ref': product['binding_ref'],
            'release_path': product['release_path'], 'inventory': product['inventory']}

def document_path(path, worker_root):
    p = canonical_existing(path, False)
    state.need(p.is_relative_to(worker_root) and
               not {'.git', '.hrn'} & {part.casefold() for part in p.relative_to(worker_root).parts} and
               p.name.casefold() != 'colvia', 'document-outside-worker')
    return p


def link_inputs(docs, records, worker_root, parser_path, parser_sha256):
    """Bind only original-output link targets; bodies remain outside model reads."""
    from urllib.parse import unquote, urlsplit
    from .official_documents import document_stat_key
    from .official_worker import GFM, DocumentHTML
    supplied = docs.get('link_targets', [])
    state.need(type(supplied) is list and len(supplied) <= 64 and
               ('link_targets' not in docs or bool(supplied)), 'link-target-list')
    by_path = {entry['path'] for entry in records.values()}
    output = records[docs['output']]
    parser = GFM(parser_path, parser_sha256)
    try:
        rendered = DocumentHTML()
        raw = state.regular(output['path'], 131072)
        state.need(state.digest(raw) == output['sha256'], 'output-link-input-drift')
        rendered.feed(parser.render(raw.decode('utf-8')))
        rendered.close()
        required = {}
        for link in rendered.links:
            parts = urlsplit(link)
            if parts.scheme or parts.netloc:
                continue  # The shared verifier checks external-link approval below.
            state.need(not parts.query and not unquote(parts.path).startswith('/'), 'link-target-outside-scope')
            destination = os.path.normpath(str(Path(output['path']).parent / unquote(parts.path))) if parts.path else output['path']
            if destination not in by_path:
                anchors = required.setdefault(destination, set())
                if parts.fragment:
                    anchors.add(unquote(parts.fragment))
        metadata, identities, anchored = {}, {tuple(v['identity']) for v in records.values()}, 0
        for item in supplied:
            exact(item, {'path', 'anchors'}, 'link-target-fields')
            path = document_path(item['path'], worker_root)
            name, anchors = str(path), item['anchors']
            state.need(name not in metadata and name not in by_path, 'link-target-alias')
            state.need(type(anchors) is list and len(anchors) <= 32 and
                       all(type(a) is str and 0 < len(a.encode()) <= 512 and
                           not any(c in a for c in ('\x00', '\r', '\n')) for a in anchors) and
                       len(set(anchors)) == len(anchors), 'link-anchor-list')
            state.need(name in required and set(anchors) == required[name], 'unreferenced-or-missing-link-target-anchor')
            before = path.lstat()
            identity = (before.st_dev, before.st_ino)
            state.need(stat.S_ISREG(before.st_mode) and before.st_nlink == 1 and identity not in identities, 'link-target-alias')
            identities.add(identity)
            content_sha = None
            if anchors:
                anchored += 1
                state.need(anchored <= 8, 'anchored-target-limit')
                record, raw = file_record(path, limit=131072)
                state.need(record['identity'] == list(identity) and
                           document_stat_key(path.lstat()) == document_stat_key(before), 'link-target-drift')
                target = DocumentHTML(); target.feed(parser.render(raw.decode('utf-8'))); target.close()
                state.need(set(anchors) <= target.anchors, 'link-anchor-missing')
                content_sha = record['sha256']
            metadata[name] = {'identity': list(identity), 'mode': stat.S_IMODE(before.st_mode),
                              'size': before.st_size, 'mtime_ns': before.st_mtime_ns,
                              'sha256': content_sha, 'anchors': sorted(anchors)}
        state.need(set(metadata) == set(required), 'link-target-outside-scope')
        return metadata
    finally:
        parser.close()


def prepare(target, request):
    target = canonical_existing(str(Path(target)), True)
    exact(request, {'work_id', 'worker_root', 'documents', 'read_ids', 'prompt', 'owner_statement',
                    'runtime', 'runtime_root', 'expires_wall_ns', 'seconds', 'worker_limit'}, 'request-fields')
    state.need(type(request['work_id']) is str and type(request['owner_statement']) is str and
               0 < len(request['owner_statement']) <= 4096 and type(request['prompt']) is str and
               0 < len(request['prompt'].encode()) <= 32768, 'owner-task-input')
    state.need(type(request['seconds']) is int and 30 <= request['seconds'] <= 600 and
               type(request['expires_wall_ns']) is int and time.time_ns() < request['expires_wall_ns'] <= time.time_ns() + 86400 * 10**9 and
               type(request['worker_limit']) is int and request['worker_limit'] in (1, 5), 'execution-bound')
    state.require_no_open(target)
    state.require_capacity(target)
    work = observe_work(target, request)
    paths = runtime_input(request['runtime'])
    runtime_root = canonical_existing(request['runtime_root'], True)
    state.need(stat.S_IMODE(runtime_root.stat().st_mode) & 0o077 == 0, 'private-runtime-root')
    worker_root = canonical_existing(request['worker_root'], True)
    for protected in (target, worker_root):
        state.need(runtime_root != protected and protected not in runtime_root.parents and runtime_root not in protected.parents, 'runtime-project-overlap')
    docs = request['documents']
    exact(docs, {'files', 'output', 'claims', 'approved_external_links'} |
          ({'link_targets'} if type(docs) is dict and 'link_targets' in docs else set()), 'document-request')
    ids = request['read_ids']
    state.need(type(ids) is list and 1 <= len(ids) <= 8 and all(type(i) is str and i.isascii() and i.isalnum() and len(i) <= 64 for i in ids)
               and len(set(ids)) == len(ids) and type(docs['files']) is dict and set(ids) == set(docs['files']), 'document-id-set')
    state.need(docs['output'] in ids, 'single-output')
    records = {}
    for key in ids:
        item = docs['files'][key]; exact(item, {'path', 'view'}, 'document-entry')
        p = document_path(item['path'], worker_root)
        record, raw = file_record(p, limit=131072)
        raw.decode('utf-8')
        record['view'] = item['view']; records[key] = record
        if key == docs['output']:
            state.need(p.relative_to(worker_root).as_posix() in work['scope'], 'output-outside-work-scope')
            exact(item['view'], {'kind', 'ranges'}, 'editable-view')
            ranges = item['view']['ranges']
            state.need(item['view']['kind'] == 'replace-range' and type(ranges) is list and len(ranges) == 1 and
                       type(ranges[0]) is list and len(ranges[0]) == 2 and all(type(n) is int for n in ranges[0]) and
                       0 <= ranges[0][0] < ranges[0][1] <= len(raw), 'single-edit-range')
        else:
            state.need(item['view'] == {'kind': 'full'}, 'reference-view')
    state.need(len({p['path'] for p in records.values()}) == len(records) and
               len({tuple(p['identity']) for p in records.values()}) == len(records), 'document-path-alias')
    from .official_documents import document_view, safe_text
    safe_text(request['prompt'])
    exact(docs['claims'], {docs['output']}, 'claims-output-coverage')
    rule = docs['claims'][docs['output']]
    exact(rule, {'required', 'forbidden', 'evidence'}, 'claims-fields')
    for name in ('required', 'forbidden'):
        state.need(type(rule[name]) is list and len(rule[name]) <= 32 and
                   all(type(x) is str and 0 < len(x.encode()) <= 4096 for x in rule[name]), 'claims-text')
    state.need(bool(rule['required']) and type(rule['evidence']) is list and 1 <= len(rule['evidence']) <= 32, 'claims-evidence')
    for evidence in rule['evidence']:
        exact(evidence, {'file_id', 'quote'}, 'claim-evidence-fields')
        state.need(evidence['file_id'] in records and evidence['file_id'] != docs['output'] and
                   type(evidence['quote']) is str and 0 < len(evidence['quote'].encode()) <= 4096, 'claim-evidence-source')
        record = records[evidence['file_id']]
        state.need(evidence['quote'] in document_view(record, state.regular(record['path'])).decode(), 'claim-evidence-missing')
    state.need(type(docs['approved_external_links']) is list and len(docs['approved_external_links']) <= 32 and
               all(type(x) is str and len(x) <= 2048 and x.startswith(('https://', 'mailto:')) for x in docs['approved_external_links']), 'external-links')
    for record in records.values():
        safe_text(document_view(record, state.regular(record['path'])).decode())
    payload = Path(work['release_path']) / 'payload'
    resources = {'python': str(Path(sys.executable).resolve()), 'worker': str(payload / 'src/hv2ref/official_worker.py'),
                 'parser': str(payload / 'runtime/official/marked.umd.js'), 'profile_template': str(payload / 'runtime/official/worker.sb.in')}
    documents = {'contract_version': 2, 'files': records, 'outputs': [docs['output']], 'claims': docs['claims'],
                 'approved_external_links': docs['approved_external_links'], 'allowed_identifiers': [],
                 'writer_attestation': True, 'source_digests': {k: v['sha256'] for k, v in records.items()},
                 'view_contracts': initial_view_contracts(records), 'link_metadata': {}, **resources}
    for key, p in resources.items():
        documents[key + '_sha256'] = state.digest(state.regular(p, 512 * 1024 * 1024))
    from .official_documents import parent_identities
    from .official_worker import verify, WorkerRefusal
    try:
        documents['link_metadata'] = link_inputs(docs, records, worker_root, resources['parser'], documents['parser_sha256'])
        preflight = dict(documents, parents=parent_identities([v['path'] for v in records.values()] + list(documents['link_metadata'])))
        findings = verify(preflight, 'DOC-LINKS')['findings']
    except UnicodeError:
        state.need(False, 'link-anchor-encoding')
    except WorkerRefusal:
        state.need(False, 'initial-document-links-failed')
    # Admission checks link scope. Active HTML cleanup retains the existing path:
    # the unchanged full post-write verifier must reject any remaining active HTML.
    state.need(all(item['code'] == 'active-html' for item in findings), 'initial-document-links-failed')
    state.need(pack_reads(records, origin={'sources': documents['source_digests'], 'approval': 'owner-official-' + '0' * 64}) == [ids], 'single-ordered-read-pack')
    spec = {'version': 1, 'target': str(target), 'request': request, 'work': work, 'documents': documents,
            'runtime_paths': paths, 'runtime_root': str(runtime_root), 'policy': 'official-cli-0.165.0-macos'}
    state.need(len(state.canonical(spec)) <= 1024 * 1024, 'execution-spec-size')
    grant = state.digest(state.canonical(spec))
    state.need(not os.path.lexists(state.capsule_path(target, grant)) and
               not os.path.lexists(target / '.hrn/locks' / ('official-' + grant + '.lock')), 'grant-already-consumed')
    return {'spec': spec, 'confirm_token': grant, 'effects': 'none',
            'meaning': 'confirmation is a trusted-local operator declaration, not human authentication'}

def execute(target, spec, confirm):
    from .workspace import writer_guard
    from .official_host import Host
    from .official_adapter import run
    with writer_guard(Path(target)):
        prepared = prepare(target, spec['request'])
        state.need(prepared['spec'] == spec and prepared['confirm_token'] == confirm, 'stale-execution-confirmation')
        host = Host(spec, confirm)
        try:
            return run(host)
        except BaseException as error:
            host.fail(error)
            raise
        finally:
            host.close()

def cli(target, args, value=None):
    from .product import require_workspace_runtime
    state.need(require_workspace_runtime(Path(target))['inventory_id'] == state.WINDOW, 'official-window-required')
    if args.action == 'prepare':
        return prepare(target, value)
    if args.action == 'execute':
        return execute(target, value, args.confirm)
    if args.action == 'status':
        return state.public_status(state.read_capsule(target, args.grant))
    if args.action == 'cancel':
        return state.cancel(target, args.grant, args.reason)
    if args.action == 'resolve':
        return state.resolve(target, args.grant, args.confirm) if args.confirm else state.resolution_preview(target, args.grant)
    state.need(False, 'unsupported-execution-action')
