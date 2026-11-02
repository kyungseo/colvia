"""V2 document worker boundary: private transient inputs, metadata-only journal."""
from pathlib import Path
import copy
import json
import os
import re
import selectors
import subprocess
import time

from . import official_state as state, official_schema as schema, official_recovery as recovery
from .official_documents import (DocumentController, HostRefusal, canonical, closed_environment,
    digest, document_record, document_item, end_process, file_record, parent_identities,
    reject_duplicate_keys, require, safe_text, sb_literal, wire_bytes, worker_file_limit)


# Fixed local detectors: not a general secret classifier or human authorization.
# Kept in the v2-only module; no old-window inventory or persisted shape change.
_CREDENTIAL = re.compile(
    r"(?i)(?:[\"']?(?:password|passwd|secret|api_key|access_token|refresh_token)[\"']?"
    r"\s*[=:]\s*[\"']?[^\s,}\"']{8,}|gh[pousr]_[a-z0-9]{20,}|"
    r"github_pat_[a-z0-9_]{20,}|AKIA[A-Z0-9]{16})")


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


class Controller:
    # Reuse the established document/view/link checks without its v1 raw writers.
    def check_files(self):
        DocumentController.check_files(self)
        for key, entry in self.files.items():
            observed, _ = recovery.document_observation(entry['path'])
            require(observed == self.identities[key], 'document full identity drift')

    def __init__(self, host):
        self.host = host
        self.spec = copy.deepcopy(host.spec['documents'])
        self.files = copy.deepcopy(self.spec['files'])
        self.identities = copy.deepcopy(host.spec['document_identities'])
        self.active = None; self.sealed = False
        self.written_ids = set(); self.verifiers = {}; self.read_ids = set()
        self.root = Path(host.spec['host_control']['path'])
        self.transient = None
        self.check_files()
        self.check_dependencies()

    def check_dependencies(self):
        for key in ('python', 'worker', 'parser', 'profile_template'):
            require(digest(state.regular(self.spec[key], 512 * 1024 * 1024)) == self.spec[key + '_sha256'], 'worker dependency drift')

    def preflight_inputs(self):
        # Read only pinned views through the existing canonical descriptor checks.
        self.check_files(); self.check_dependencies()
        checked_payload(self.host.spec['request']['prompt'], limit=65536, deadline=self.host.deadline)
        for key, expected in self.files.items():
            observed, raw = document_record(expected)
            require(observed == expected, 'document input drift')
            if key in self.spec['outputs']:
                checked_preserved_output(observed, raw, deadline=self.host.deadline)
            checked_payload(document_item(key, observed, raw), deadline=self.host.deadline)

    def preflight(self, tool, args):
        require(self.active is None and not self.sealed, 'worker unavailable')
        self.check_files(); self.check_dependencies()
        if tool == 'u2_write_file':
            key = args['file_id']
            require(key in self.spec['outputs'] and args['expected_sha256'] == self.files[key]['sha256'], 'write scope/CAS')
            checked_payload(args['content'], deadline=self.host.deadline)
            observed, raw = document_record(self.files[key])
            require(observed == self.files[key], 'document write drift')
            begin, end = observed['view']['ranges'][0]
            # A credential can straddle the replacement/preserved-byte boundary.
            # Scan the resulting full file before recovery reservation or spawn.
            combined = raw[:begin] + args['content'].encode() + raw[end:]
            require(len(combined) <= 131072, 'content_rejected')
            checked_payload(combined.decode('utf-8'), limit=262144, deadline=self.host.deadline)
        return True

    def materialize(self, tool, args, ordinal):
        recorded = self.host.spec['host_control']
        output = self.files[self.spec['outputs'][0]]['path']
        require(recovery.root_record(self.root, target=self.host.target,
                worker_root=self.host.spec['request']['worker_root'], runtime_root=self.host.spec['runtime_root'], output=output) == recorded,
                'recovery root drift')
        if self.transient is None:
            base = recovery.child_container(self.root, 'transient')
            self.transient = recovery.create_private(base / self.host.grant)
        slot = recovery.create_private(self.transient / f'worker-{ordinal:03d}')
        swap = {args['file_id']: str(slot / (args['file_id'] + '.swap'))} if tool == 'u2_write_file' else {}
        worker_spec = {'version': 2, 'files': self.files,
            'parents': parent_identities([v['path'] for v in self.files.values()] + list(swap.values()) + list(self.spec['link_metadata'])),
            'outputs': self.spec['outputs'], 'swap': swap, 'parser': self.spec['parser'], 'parser_sha256': self.spec['parser_sha256'],
            'claims': self.spec['claims'], 'approved_external_links': self.spec['approved_external_links'], 'link_metadata': self.spec['link_metadata']}
        spec_path = slot / 'spec.json'; raw = canonical(worker_spec)
        require(len(raw) <= 1048576, 'worker-record-size')
        recovery.publish_private(spec_path, raw)
        template = state.regular(self.spec['profile_template']).decode()
        require(digest(template.encode()) == self.spec['profile_template_sha256'], 'worker profile drift')
        metadata_paths = list(self.spec['link_metadata'])
        reads = [v['path'] for v in self.files.values()] + [p for p,e in self.spec['link_metadata'].items() if e['sha256'] is not None]
        dependencies = [self.spec[k] for k in ('python', 'worker', 'parser')] + [str(spec_path)]
        ancestors = set(parent_identities(reads + dependencies + list(swap.values()) + metadata_paths))
        ancestors.update(metadata_paths)
        common = ['/System/Library', '/usr/lib', '/private/var/db/dyld', '/private/var/db/timezone',
                  '/dev/null', '/dev/random', '/dev/urandom', '/opt/homebrew/opt/gettext/lib/libintl.8.dylib',
                  '/opt/homebrew/Cellar/gettext/1.0/lib/libintl.8.dylib']
        for name in common: ancestors.update(str(p) for p in Path(name).parents)
        ancestors.add(str(slot))
        metadata = '(allow file-read-metadata ' + ' '.join(sb_literal(p) for p in sorted(ancestors)) + ')'
        read_rules = '(allow file-read* ' + ' '.join(sb_literal(p) for p in reads) + ')'
        writes = ''
        if swap:
            target, swap_path = self.files[args['file_id']]['path'], next(iter(swap.values()))
            require(Path(target).parent.stat().st_dev == slot.stat().st_dev, 'swap device differs')
            parents = {str(Path(target).parent), str(slot)}
            writes = '(allow file-write* ' + sb_literal(target) + ' ' + sb_literal(swap_path) + ')\n' + \
                '(allow file-read-data file-write-data ' + ' '.join(sb_literal(p) for p in sorted(parents)) + ')'
            template += '(allow file-read-metadata ' + sb_literal(swap_path) + ')\n'
        template = template.replace('; @@ANCESTOR_METADATA_LITERALS@@', metadata).replace('; @@APPROVED_INPUT_READ_LITERALS@@', read_rules)
        marker = '; @@EXACT_WRITE_TARGET_AND_SWAP@@ only for write operation, omitted for read and all verifiers.'
        require(marker in template, 'worker profile marker drift')
        template = template.replace(marker, writes)
        require(len(template.encode()) <= 1048576, 'worker-profile-size')
        profile = slot / 'worker.sb'; recovery.publish_private(profile, template.encode())
        params = {'BIN': self.spec['python'], 'SPEC': str(spec_path), 'PARSER': self.spec['parser'],
                  'WORKER': self.spec['worker'], 'PYROOT': str(Path(self.spec['python']).parent.parent)}
        argv = ['/usr/bin/sandbox-exec']
        for key, value in params.items(): argv += ['-D', key + '=' + value]
        operation = {'u2_read_file': 'read', 'u2_write_file': 'write'}.get(tool, args.get('verifier_id'))
        argv += ['-f', str(profile), self.spec['python'], '-I', '-S', '-B', self.spec['worker'], '--spec', str(spec_path), '--operation', operation]
        return slot, swap, argv

    def exchange(self, request, timeout):
        """Drain stdout/stderr concurrently and bound all three pipes in memory."""
        raw = canonical(request); require(len(raw) <= 131072, 'worker-request-size')
        p = self.active; outputs = {'out': bytearray(), 'err': bytearray()}; offset = 0
        until = time.monotonic() + timeout
        with selectors.DefaultSelector() as selector:
            for stream, label, event in ((p.stdin, 'in', selectors.EVENT_WRITE), (p.stdout, 'out', selectors.EVENT_READ), (p.stderr, 'err', selectors.EVENT_READ)):
                os.set_blocking(stream.fileno(), False); selector.register(stream, event, label)
            while selector.get_map():
                require(time.monotonic() < until, 'worker timeout')
                for key, _ in selector.select(min(.1, max(0, until - time.monotonic()))):
                    if key.data == 'in':
                        try: written = os.write(key.fileobj.fileno(), raw[offset:offset + 16384])
                        except BrokenPipeError:
                            selector.unregister(key.fileobj); key.fileobj.close(); continue
                        offset += written
                        if offset == len(raw): selector.unregister(key.fileobj); key.fileobj.close()
                    else:
                        chunk = os.read(key.fileobj.fileno(), 65536)
                        if not chunk:
                            selector.unregister(key.fileobj); continue
                        limit = 131072 if key.data == 'out' else 1048576
                        if key.data == 'err': self.host.diagnostic('worker', 'worker', 'worker_failed', len(chunk))
                        require(len(outputs[key.data]) + len(chunk) <= limit, 'worker output limit')
                        outputs[key.data].extend(chunk)
            p.wait(timeout=max(.001, until - time.monotonic()))
        return bytes(outputs['out']), bytes(outputs['err'])

    def validate_result(self, tool, args, result, prior, swap):
        if tool == 'u2_write_file':
            key = args['file_id']; old = self.files[key]
            require(type(result) is dict and set(result) == {'file_id', 'sha256', 'identity', 'bytes', 'mode'} and result['file_id'] == key, 'write result shape')
            observed, raw = file_record(old['path'], limit=131072)
            wanted = args['content'].encode(); begin, end = old['view']['ranges'][0]
            observed['view'] = {'kind': 'replace-range', 'ranges': [[begin, begin + len(wanted)]]}
            wanted = prior[:begin] + wanted + prior[end:]
            require(raw == wanted and observed['mode'] == old['mode'] and observed['sha256'] == result['sha256'] and
                    observed['identity'] == result['identity'] and type(result['mode']) is int and result['mode'] == old['mode'] and type(result['bytes']) is int and result['bytes'] == len(raw) and
                    not os.path.lexists(swap[key]), 'worker write postcondition')
            self.files[key] = observed
            self.identities[key], _ = recovery.document_observation(old['path'])
            require(self.identities[key]['sha256'] == observed['sha256'] and [self.identities[key]['dev'], self.identities[key]['ino']] == observed['identity'], 'write observation drift')
            self.written_ids.add(key); self.verifiers.clear()
            result = {'file_id': key, 'sha256': observed['sha256'], 'bytes': len(raw)}
        elif tool == 'u2_read_file':
            require(type(result) is dict and set(result) == {'files'} and type(result['files']) is list and
                    len(result['files']) == len(args['file_ids']), 'read result shape')
            require([row['file_id'] for row in result['files']] == args['file_ids'], 'read result IDs')
            for row in result['files']:
                entry, raw = document_record(self.files[row['file_id']])
                require(row == document_item(row['file_id'], entry, raw), 'read result binding')
                checked_payload(row['content'], deadline=self.host.deadline)
            for row in result['files']:
                row['origin'] = {'kind': 'approved-document', 'source_sha256': self.spec['source_digests'][row['file_id']], 'approval': 'owner-official-' + self.host.grant}
            self.read_ids.update(args['file_ids'])
        else:
            require(type(result) is dict and set(result) == {'verifier_id', 'inputs', 'pass', 'findings', 'oracle_sha256', 'boundary'} and
                    result['verifier_id'] == args['verifier_id'] and
                    result['inputs'] == {key: value['sha256'] for key, value in self.files.items()} and type(result['pass']) is bool and
                    type(result['findings']) is list and
                    result['oracle_sha256'] == digest(wire_bytes({k: self.spec[k] for k in ('outputs', 'claims', 'approved_external_links', 'parser_sha256')})) and
                    result['boundary'] == 'fixed static checks; human factual review remains required', 'verifier input identity')
            self.verifiers[args['verifier_id']] = result
        checked_payload(result, limit=64000, deadline=self.host.deadline)
        self.check_files()
        require(len(wire_bytes(result)) <= 64000, 'tool output does not fit native result envelope')
        return result

    def dispatch(self, tool, args):
        h = self.host; ordinal = len(h.journal.history().workers) + 1
        role = {'u2_read_file': 'read', 'u2_write_file': 'write', 'u2_verify': 'verify'}[tool]
        self.preflight(tool, args)
        before = prior = None
        if role == 'write':
            before, prior = recovery.document_observation(self.files[args['file_id']]['path'])
            require(before == h.storage['scope']['documents'][args['file_id']]['original_identity'], 'write identity drift')
        slot, swap, argv = self.materialize(tool, args, ordinal)
        timeout = min(60, h.deadline - time.monotonic() - 5)
        require(timeout > 0, 'worker time exhausted')
        h.authority(); self.preflight(tool, args)
        require(ordinal <= h.spec['request']['worker_limit'], 'worker budget exhausted')
        # No fallible preparation between the durable intent and Popen.
        env = closed_environment({'HOME': str(slot), 'TMPDIR': str(slot)})
        h.journal.append('worker-spawn-intent', {'callback_id': h.pending, 'worker_ordinal': ordinal, 'role': role,
                                             'code_identity': self.spec['worker_sha256']})
        try:
            self.active = subprocess.Popen(argv, cwd=slot, env=env, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                stderr=subprocess.PIPE, start_new_session=True, close_fds=True, preexec_fn=worker_file_limit)
        except (OSError, subprocess.SubprocessError):
            h.journal.append('worker-spawn-failed', {'worker_ordinal': ordinal, 'reason': 'spawn_failed', 'reaped': True})
            raise
        birth = None; result = None; success = False; failure = 'worker_failed'; after = None
        started_recorded = result_recorded = False
        try:
            try:
                birth = state.process_birth(self.active.pid) or None
            except BaseException:
                h.journal.append('worker-started', {'worker_ordinal': ordinal, 'pid': self.active.pid, 'birth': None})
                started_recorded = True
                raise
            h.journal.append('worker-started', {'worker_ordinal': ordinal, 'pid': self.active.pid, 'birth': birth})
            started_recorded = True
            require(birth is not None, 'worker process identity unavailable')
            out, err = self.exchange({'tool': tool, 'arguments': args}, timeout)
            require(self.active.returncode == 0 and not err, 'worker refused/unavailable')
            response = json.loads(out, object_pairs_hook=reject_duplicate_keys)
            require(type(response) is dict and set(response) == {'ok', 'result'} and response['ok'] is True, 'worker result shape')
            result = self.validate_result(tool, args, response['result'], prior, swap)
            success = role != 'verify' or result['pass'] is True
            failure = None if success else 'verifier_failed'
            if role == 'write': after, _ = recovery.document_observation(self.files[args['file_id']]['path'])
        except BaseException:
            success = False; failure = 'worker_failed'
            if role == 'write':
                try: after, _ = recovery.document_observation(self.files[args['file_id']]['path'])
                except Exception: after = None
            raise
        finally:
            process = self.active; absent = False
            try:
                if started_recorded:
                    h.journal.append('worker-result', {'worker_ordinal': ordinal, 'success': success,
                        'effect': ('applied' if success else 'unknown') if role == 'write' else 'none',
                        'before': before, 'after': after, 'verifier_id': args.get('verifier_id'),
                        'verifier_pass': result['pass'] if role == 'verify' and result is not None else None, 'reason': failure})
                    result_recorded = True
            finally:
                try:
                    closed = end_process(process)
                    absent = birth is not None and state.process_birth(process.pid) != birth and state.group_absent(process.pid)
                    if started_recorded and result_recorded and absent:
                        h.journal.append('worker-closed', {'worker_ordinal': ordinal, 'returncode': closed['exit_code'],
                                                         'group_absent': True, 'birth_absent': True})
                    elif started_recorded:
                        require(False, 'worker closure unavailable')
                finally:
                    for stream in (process.stdin, process.stdout, process.stderr):
                        if stream is not None and not stream.closed:
                            stream.close()
                    if absent:
                        self.active = None
        return result
