"""Explicit installed official execution entry. No source fallback or Core apply."""
from pathlib import Path
import json
import os
import stat
import sys
import time
import tomllib
from . import official_state as state
from .official_documents import file_record, document_record, initial_view_contracts, pack_reads, wire_bytes
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

def _diagnostic_input(path):
    """Bounded, explicit local input; never open known credential contents."""
    from .jsonio import decode_json_bytes
    state.need(not os.environ.get("CODEX_HOME"), "api-auth-override-not-admitted")
    path = canonical_existing(str(path.absolute()), False)
    home = Path.home().resolve()
    protected = (home / ".codex/auth.json", home / ".codex/installation_id")
    state.need(path not in protected, "credential-input")
    # No directory enumeration or credential content reads.
    protected_ids = set()
    for member in protected:
        try:
            info = member.stat()
        except FileNotFoundError:
            continue
        protected_ids.add((info.st_dev, info.st_ino))
    fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
    with os.fdopen(fd, "rb") as stream:
        before = os.fstat(stream.fileno())
        state.need(stat.S_ISREG(before.st_mode) and before.st_nlink == 1 and before.st_size <= 65536,
                   "diagnostic-input-kind-size")
        state.need((before.st_dev, before.st_ino) not in protected_ids, "credential-input")
        raw = stream.read(65537)
        after = os.fstat(stream.fileno())
        state.need(len(raw) <= 65536 and
                   (before.st_dev, before.st_ino, before.st_size, before.st_mtime_ns) ==
                   (after.st_dev, after.st_ino, after.st_size, after.st_mtime_ns), "diagnostic-input-changed")
    value = decode_json_bytes(raw, require_canonical=True)
    exact(value, {"paths", "sha256"}, "runtime-fields")
    exact(value["paths"], PATH_KEYS, "runtime-path-set")
    exact(value["sha256"], PINNED_INPUTS, "runtime-pin-set")
    state.need(all(type(v) is str for v in value["paths"].values()) and
               all(type(v) is str and len(v) == 64 and all(c in "0123456789abcdef" for c in v)
                   for v in value["sha256"].values()), "diagnostic-input-values")
    for value_path in value["paths"].values():
        value_path.encode("utf-8")
    # An instructions/rules path must not redirect a pinned content read to credentials.
    for key in PINNED_INPUTS:
        member = canonical_existing(value["paths"][key], False)
        info = member.stat()
        state.need(member not in protected and
                   (info.st_dev, info.st_ino) not in protected_ids, "credential-input")
    return value


def diagnose_runtime_input(path):
    """Observation only. No admission, network, writer or credential content."""
    from .errors import ContractError
    from .official_policy import PolicyRefusal
    reason = "input-invalid"
    try:
        try:
            value = _diagnostic_input(path)
        except UnicodeError:
            raise ValueError("input") from None
        runtime_input(value)  # Returned local paths are intentionally discarded.
    except ContractError as error:
        known = {"unqualified-cli-helper": "unqualified-cli-helper",
                 "default-auth-home-required": "input-location",
                 "rules-home": "input-location", "helper-location": "input-location",
                 "custom-provider-not-admitted": "config-not-admitted",
                 "configured-instructions-not-admitted": "config-not-admitted",
                 "api-auth-override-not-admitted": "environment-not-admitted",
                 "credential-input": "credential-input", "record-changed": "input-changed",
                 "diagnostic-input-changed": "input-changed"}
        if error.code == "HV2-OFFICIAL-EXECUTION":
            reason = known.get(error.message, "input-invalid")
            if error.message in {"runtime-input-drift:" + key for key in PINNED_INPUTS}:
                reason = "input-drift"
    except PolicyRefusal:
        reason = "input-location"
    except (UnicodeError, tomllib.TOMLDecodeError):
        reason = "config-invalid"
    except OSError:
        reason = "file-unavailable"
    except (ValueError, TypeError, KeyError, RecursionError):
        reason = "input-invalid"
    except Exception:
        reason = "check-failed"
    else:
        return {"local_check": "passed", "reason": "local-input-matches",
                "message": "이번 명령에서 확인한 실행 도구와 입력이 검증 기준에 맞습니다.",
                "next_action": "실행을 진행하려면 현재 Work의 승인·한도와 실행 미리보기를 확인하세요. 계정·모델 연결은 실제 실행 준비 단계에서 확인합니다."}
    guidance = {
        "unqualified-cli-helper": ("지정한 실행 도구가 기존 검증 조합과 다릅니다.", "기존에 검증된 CLI와 헬퍼 조합을 확인하세요."),
        "input-drift": ("현재 파일과 보존된 실행 입력이 다릅니다.", "입력의 원래 출처와 파일 변경 내용을 함께 확인하세요."),
        "input-location": ("실행 입력의 파일 위치를 확인해야 합니다.", "입력을 준비한 에이전트나 운영자에게 원래 파일 위치 확인을 요청하세요."),
        "config-not-admitted": ("현재 설정에 검증 범위 밖의 항목이 있습니다.", "실행 입력을 준비한 에이전트와 해당 설정의 사용 목적을 확인하세요."),
        "environment-not-admitted": ("이번 명령의 실행 환경에 허용 범위 밖의 설정이 있습니다.", "이번 명령에 전달된 환경 설정을 에이전트와 확인하세요."),
        "credential-input": ("인증 자료가 내용 검사 대상으로 지정돼 있습니다.", "입력을 준비한 에이전트에게 검사 대상 지정을 확인해 달라고 요청하세요."),
        "input-changed": ("확인하는 동안 입력 파일이 바뀌었습니다.", "변경 중인 작업과 입력의 원래 출처부터 확인하세요."),
        "file-unavailable": ("지정한 입력 파일을 읽지 못했습니다.", "입력을 준비한 에이전트나 운영자에게 파일 위치와 접근 상태 확인을 요청하세요."),
        "config-invalid": ("입력 설정을 해석하지 못했습니다.", "입력을 준비한 에이전트와 파일 형식을 확인하세요."),
        "input-invalid": ("제공된 실행 입력을 확인하지 못했습니다.", "입력을 준비한 에이전트에게 기존 입력의 형식과 출처 확인을 요청하세요."),
        "check-failed": ("로컬 입력 확인을 마치지 못했습니다.", "현재 입력을 보존하고 실행 환경을 확인하세요."),
    }
    message, next_action = guidance[reason]
    return {"local_check": "failed", "reason": reason, "message": message, "next_action": next_action}


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
                    'runtime', 'runtime_root', 'host_control_root', 'expires_wall_ns', 'seconds', 'worker_limit'}, 'request-fields')
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
    from .official_documents import document_view
    from .official_controller import checked_payload, checked_preserved_output
    checked_payload(request['prompt'])
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
    for key, record in records.items():
        observed, raw = document_record(record)
        state.need(observed == record, 'document-admission-drift')
        checked_payload(document_view(record, raw).decode(), limit=131072)
        if key == docs['output']:
            checked_preserved_output(observed, raw)
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
    from .official_recovery import root_record, document_observation
    host_control = root_record(request['host_control_root'], target=target, worker_root=worker_root,
                               runtime_root=runtime_root, output=records[docs['output']]['path'])
    from .official_policy import require_host_root_separation
    require_host_root_separation(host_control['path'], paths, runtime_root, Path(sys.executable).resolve().parent.parent)
    identities = {}
    for key, record in records.items():
        identity, _ = document_observation(record['path'])
        state.need([identity['dev'], identity['ino']] == record['identity'] and identity['mode'] == record['mode'] and
                   identity['sha256'] == record['sha256'], 'document-admission-drift')
        identities[key] = identity
    spec = {'version': 2, 'host_control': host_control, 'document_identities': identities, 'target': str(target), 'request': request, 'work': work, 'documents': documents,
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
        observed = state.read_capsule(target, args.grant); result = state.public_status(observed)
        if getattr(args, 'host_control_root', None) is not None:
            state.need(observed.get('schema_version') == 2, 'v1-external-recovery-not-supported')
            from .official_recovery import inspect, inspect_transient
            result['recovery_availability'] = inspect(observed, args.host_control_root)
            result.update(inspect_transient(observed, args.host_control_root))
        return result
    if args.action == 'cancel':
        return state.cancel(target, args.grant, args.reason)
    if args.action == 'resolve':
        return state.resolve(target, args.grant, args.confirm, host_control_root=getattr(args, 'host_control_root', None)) if args.confirm else state.resolution_preview(target, args.grant, host_control_root=getattr(args, 'host_control_root', None))
    state.need(False, 'unsupported-execution-action')
