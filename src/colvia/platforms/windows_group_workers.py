"""Native external CLI admission and provider-specific direct-edit proof."""
from contextlib import ExitStack, contextmanager
from hashlib import file_digest
import json
import os
from pathlib import Path
import shutil
import sys
import threading
import time

from ..codec import RecordError, require


PINNED = {
    'claude': ('2.1.330', 'fa797c1bc7d4a3511da42622bae53a2b7f1276ae328c668f2bfef44635301caa'),
    'codex': ('0.172.0', '3f42b12274b353ecb3ec555e6c8d0a43f6c6cb29c3a546179bc12dee4855deb6'),
}


def native_required():
    require(sys.platform=='win32','group-worker-platform-unavailable')
    from .windows_architecture import native_x64
    require(native_x64(),'group-worker-platform-unavailable')


def identity(provider, executable):
    version,expected=PINNED[provider]
    p=Path(executable).resolve(strict=True)
    require(p.is_file() and p.suffix.casefold()=='.exe' and p.stat().st_nlink==1,
            'group-worker-executable-unqualified')
    with p.open('rb') as stream:
        require(file_digest(stream,'sha256').hexdigest()==expected,'group-worker-executable-unqualified')
    return dict(path=str(p),version=version,sha256=expected)


def paths_for(assignments, requested):
    native_required()
    require(set(requested)<=set(assignments.values()),'group-worker-executable-set-invalid')
    results={}
    for provider in sorted(set(assignments.values())):
        executable=requested.get(provider) or shutil.which(provider+'.exe')
        require(executable is not None,'group-worker-cli-unavailable')
        results[provider]=identity(provider,executable)
    return results


def env_for_worker():
    names=('SystemRoot','WINDIR','COMSPEC','USERNAME','USERPROFILE','LOCALAPPDATA','APPDATA',
           'PATHEXT','SYSTEMDRIVE','TEMP','TMP','NUMBER_OF_PROCESSORS','PROCESSOR_ARCHITECTURE','HOMEDRIVE','HOMEPATH')
    env={k:os.environ[k] for k in names if k in os.environ}
    env['PATH']=str(Path(env['SystemRoot'])/'System32')
    return env


def claude_managed_absent(env):
    import winreg
    for root in (winreg.HKEY_LOCAL_MACHINE,winreg.HKEY_CURRENT_USER):
        try:
            with winreg.OpenKey(root,r'SOFTWARE\Policies\ClaudeCode'):
                raise RecordError('group-worker-claude-managed-policy-unverified')
        except FileNotFoundError:
            pass
    for parent in ('Program Files','ProgramData'):
        for name in ('managed-settings.json','managed-settings.d','managed-mcp.json'):
            try:
                (Path(env['SYSTEMDRIVE']+'/')/parent/'ClaudeCode'/name).lstat()
            except FileNotFoundError:
                continue
            raise RecordError('group-worker-claude-managed-policy-unverified')


def examine(provider, cli, scratch, env, cancelled):
    from .windows_process import run
    if provider=='claude':
        claude_managed_absent(env)
        proof=run([str(cli),'auth','status'],cwd=scratch,env=env,seconds=20,output_limit=65536,
                  cancelled=cancelled.is_set)
        require(proof.code==0,'group-worker-subscription-unavailable')
        auth=json.loads(proof.stdout)
        require(tuple(auth.get(k) for k in ('loggedIn','authMethod','apiProvider','subscriptionType'))
                ==(True,'claude.ai','firstParty','pro'),'group-worker-subscription-unavailable')
    else:
        proof=run([str(cli),'login','status'],cwd=scratch,env=env,seconds=20,output_limit=65536,
                  cancelled=cancelled.is_set)
        require(proof.code==0 and b'logged in using chatgpt' in (proof.stdout+proof.stderr).lower(),
                'group-worker-subscription-unavailable')


def verified_scoped_paths(root, scope):
    approved=[root/p for p in scope]
    for file in approved:
        require(file==file.resolve(strict=True) and file.is_file() and file.stat().st_nlink==1,
                'group-worker-scope-unqualified')
        require(file.stat().st_size<=256*1024,'group-worker-scope-unqualified')
    return approved


def verify_codex_project_config(root, account_home):
    # Codex excludes its default home from project layers. The authenticated
    # exec also skips the user layer, while retaining managed policy.
    account_home = account_home.resolve(strict=True)
    require(root != account_home, 'group-worker-codex-project-config-unverified')
    for parent in (root, *root.parents):
        if parent == account_home:
            continue
        try:
            (parent / '.codex').lstat()
        except FileNotFoundError:
            continue
        raise RecordError('group-worker-codex-project-config-unverified')


@contextmanager
def managed_instruction(root, approved, *, observer=None):
    from ..project_setup import BLOCK
    from .project_launcher import project_block
    from .windows_observation import Observer

    path = root / 'AGENTS.md'
    expected = project_block(BLOCK, 'windows')
    code = 'group-worker-managed-instruction-unverified'
    observer = observer or Observer()
    with ExitStack() as guard:
        try:
            handle, info = guard.enter_context(observer.opened(path, read=True))
        except FileNotFoundError as exc:
            raise RecordError(code) from exc
        require(not info['directory'] and not info['symlink'] and info['links'] == 1
                and info['size'] == len(expected), code)
        resolved = path.resolve(strict=True)
        require(str(resolved) == str(path) and resolved.name == 'AGENTS.md', code)
        require(not any(path.samefile(file) for file in approved), code)
        with observer.files._stream_handle(handle) as stream:
            stream.seek(0)
            require(stream.read(len(expected) + 1) == expected, code)
        location = observer.location(root)
        yield path, expected
        require(observer.location(root) == location, code)


def check_instruction_inputs(members):
    if not any(member['provider'] == 'codex' for member in members):
        return
    for member in members:
        root = Path(member['source_path'])
        approved = verified_scoped_paths(root, member['scope'])
        path = root / 'AGENTS.md'
        require(not any(file.name.casefold() == 'agents.md' and file.parent == root
                        for file in approved), 'group-worker-instruction-in-write-scope')
        if member['provider'] == 'codex':
            with managed_instruction(root, approved):
                pass
        elif path.exists():
            require(not any(file.samefile(path) for file in approved),
                    'group-worker-instruction-in-write-scope')


def codex_policy(root, approved, scratch, canary, instruction):
    require(instruction == root / 'AGENTS.md' and instruction not in approved
            and not instruction.is_relative_to(scratch), 'group-worker-instruction-in-write-scope')
    permitted={root,*(parent for file in approved for parent in file.parents if parent.is_relative_to(root))}
    protected=[canary]
    for folder in sorted(permitted):
        for entry in sorted(folder.iterdir()):
            if folder == root and entry.name == 'AGENTS.md':
                continue
            if entry not in permitted and entry not in approved:
                protected.append(entry)
    require(len(protected)<=128,'group-worker-codex-policy-limit')
    grants=(':minimal','read'),(root,'read'),(instruction,'read'),(scratch,'write'),*((p,'write') for p in approved),*((p,'deny') for p in protected)
    fields=','.join(json.dumps(str(path))+'='+json.dumps(access) for path,access in grants)
    return 'permissions.colvia_worker={filesystem={'+fields+'},network={enabled=false}}'


def codex_probe_path(path):
    # cmd.exe commands use only literal filesystem arguments. Reject command
    # syntax that would otherwise be interpreted by this fixed shell probe.
    value = str(path)
    require(path.is_absolute() and not any(char in value for char in '%!&|<>^()"\r\n'),
            'group-worker-codex-probe-path-unqualified')
    return value


def read_codex_events(stdout):
    events=[json.loads(line) for line in stdout.splitlines() if line.strip()]
    sessions=[e.get('thread_id') for e in events if e.get('type')=='thread.started']
    turns=[e for e in events if e.get('type')=='turn.completed']
    require(len(sessions)==1 and type(sessions[0]) is str and 0<len(sessions[0])<=128
            and len(turns)==1 and not any(e.get('type') in ('error','turn.failed') for e in events)
            and any(e.get('type')=='item.completed' and e.get('item',{}).get('type') in ('file_change','command_execution')
                    for e in events),'group-worker-turn-incomplete')
    return sessions[0]


_CODEX_EVENTS = frozenset({
    'thread.started', 'turn.started', 'turn.completed', 'turn.failed', 'error',
    'item.started', 'item.updated', 'item.completed',
})
_CODEX_COUNTS = (
    'nonempty_lines', 'malformed_lines', 'unknown_events', 'threads', 'valid_threads',
    'completed_turns', 'failure_events', 'activity_events',
)
_CODEX_BYTE_BUCKETS = ('empty', 'up-to-1k', 'up-to-64k', 'over-64k')
_CODEX_COUNT_LIMIT = 255


def _byte_bucket(data):
    size = len(data)
    return _CODEX_BYTE_BUCKETS[bool(size) + (size > 1024) + (size > 65536)]


def _codex_result_diagnostics(result, starts):
    counts = dict.fromkeys(_CODEX_COUNTS, 0)
    last = 'none'
    for line in result.stdout.splitlines():
        if not line.strip():
            continue
        counts['nonempty_lines'] += 1
        try:
            event = json.loads(line)
        except (ValueError, RecursionError):
            counts['malformed_lines'] += 1
            continue
        kind = event.get('type') if type(event) is dict else None
        if type(kind) is not str:
            counts['malformed_lines'] += 1
            continue
        last = kind if kind in _CODEX_EVENTS else 'other'
        if last == 'other':
            counts['unknown_events'] += 1
        elif kind == 'thread.started':
            counts['threads'] += 1
            thread = event.get('thread_id')
            counts['valid_threads'] += type(thread) is str and 0 < len(thread) <= 128
        elif kind == 'turn.completed':
            counts['completed_turns'] += 1
        elif kind in ('turn.failed', 'error'):
            counts['failure_events'] += 1
        elif kind == 'item.completed':
            item = event.get('item', {})
            if type(item) is not dict:
                counts['malformed_lines'] += 1
            elif item.get('type') in ('file_change', 'command_execution'):
                counts['activity_events'] += 1
    return dict(version=1, stage='returned', exit_code=result.code, starts=min(starts, _CODEX_COUNT_LIMIT),
                controller_stop='none', stdout_size=_byte_bucket(result.stdout), stderr_size=_byte_bucket(result.stderr),
                last_event=last, unterminated_last_line=bool(result.stdout and not result.stdout.endswith(b'\n')),
                counts={key: min(count, _CODEX_COUNT_LIMIT) for key, count in counts.items()})


def verify_codex_diagnostics(value):
    code = 'group-worker-codex-diagnostics-invalid'
    require(type(value) is dict and type(value.get('version')) is int and value['version'] == 1
            and type(value.get('starts')) is int and 0 <= value['starts'] <= _CODEX_COUNT_LIMIT, code)
    common = {'version', 'stage', 'exit_code', 'starts', 'controller_stop'}
    if value.get('stage') == 'transport':
        require(set(value) == common and value['exit_code'] is None
                and value['controller_stop'] in ('timeout', 'cancel', 'unknown'), code)
        return
    if value.get('stage') == 'result-unavailable':
        require(set(value) == common and value['exit_code'] is None and value['controller_stop'] == 'none', code)
        return
    require(value.get('stage') == 'returned' and set(value) ==
            common | {'stdout_size', 'stderr_size', 'last_event', 'unterminated_last_line', 'counts'}, code)
    require(type(value['exit_code']) is int and 0 <= value['exit_code'] <= 0xffffffff
            and value['controller_stop'] == 'none' and value['stdout_size'] in _CODEX_BYTE_BUCKETS
            and value['stderr_size'] in _CODEX_BYTE_BUCKETS and type(value['last_event']) is str
            and value['last_event'] in _CODEX_EVENTS | {'none', 'other'}
            and type(value['unterminated_last_line']) is bool, code)
    counts = value['counts']
    require(type(counts) is dict and set(counts) == set(_CODEX_COUNTS)
            and all(type(count) is int and 0 <= count <= _CODEX_COUNT_LIMIT for count in counts.values()), code)


class CodexExecFailure(RecordError):
    def __init__(self, code, diagnostics):
        verify_codex_diagnostics(diagnostics)
        self.diagnostics = diagnostics
        super().__init__(code)


def codex_exec_identity(result, starts):
    try:
        require(result.code == 0 and starts == 1, 'group-worker-turn-incomplete')
        return read_codex_events(result.stdout)
    except (ValueError, AttributeError, RecursionError) as exc:
        reason = getattr(exc, 'code', 'group-worker-process-unavailable')
        try:
            failure = CodexExecFailure(reason, _codex_result_diagnostics(result, starts))
        except (ValueError, TypeError, AttributeError, RecursionError):
            failure = CodexExecFailure(reason, dict(version=1, stage='result-unavailable', exit_code=None,
                                                    starts=min(starts, _CODEX_COUNT_LIMIT), controller_stop='none'))
        raise failure from exc


def _codex_transport_failure(exc, starts):
    reason = getattr(exc, 'code', 'group-worker-process-unavailable')
    stop = {'process-timeout': 'timeout', 'process-cancelled': 'cancel'}.get(reason, 'unknown')
    return CodexExecFailure(reason, dict(version=1, stage='transport', exit_code=None,
                                        starts=min(starts, _CODEX_COUNT_LIMIT), controller_stop=stop))


class NativeWorkers:
    def __init__(self, executables):
        self.executables=executables
        self.cancelled=threading.Event()

    def __call__(self, item, session, area):
        provider=item['provider']
        want=self.executables[provider]
        require(identity(provider,want['path'])==want,'group-worker-executable-changed')
        cli=Path(want['path']); root=Path(item['source_path'])
        approved=verified_scoped_paths(root,item['scope'])
        env=env_for_worker()
        scratch=area/('scratch-'+session)
        scratch.mkdir()
        env['TEMP']=env['TMP']=str(scratch)
        require(not self.cancelled.is_set(), 'process-cancelled')
        if provider == 'codex':
            verify_codex_project_config(root, Path(env['USERPROFILE']))
        deadline = time.monotonic() + 160  # Preserve the previous Codex auth + probes + edit budget.
        examine(provider, cli, scratch, env, self.cancelled)
        prompt=('Carry out this approved Work goal: '+item['goal']+'\n'
                'Edit the listed files directly. Use the paths exactly as shown. Do not edit any other files.\n'
                +'\n'.join(str(p) for p in approved))
        require(len(prompt.encode())<=16*1024,'group-worker-input-limit')
        if provider=='claude':
            from .windows_claude_worker import run
            return run(cli,root,approved,session,env,prompt,cancelled=self.cancelled,seconds=90)
        with managed_instruction(root, approved) as (instruction, expected):
            return self._codex(cli, root, approved, scratch, env, prompt, instruction, expected, deadline)

    def _codex(self, cli, root, approved, scratch, env, prompt, instruction, expected, deadline):
        from .windows_process import run
        canary = scratch.parent / ('protected-' + scratch.name + '.txt')
        write_canary = scratch.parent / ('ungranted-' + scratch.name + '.txt')
        probe_source = scratch / 'probe-source.txt'
        allowed_copy = scratch / 'probe-copy.txt'
        read_source, denied_read, write_source, allowed_write, denied_write = map(
            codex_probe_path, (approved[0], canary, probe_source, allowed_copy, write_canary))
        control = b'Colvia synthetic sandbox control\n'
        marker = b'Synthetic denial marker\n'
        for path, data in ((canary, control), (write_canary, control), (probe_source, marker)):
            with path.open('xb') as out:
                out.write(data)
        prefix=[str(cli),'-c','windows.sandbox=mxc','-c',codex_policy(root,approved,scratch,canary,instruction)]
        shell=[*prefix,'sandbox','--include-managed-config','-P','colvia_worker','--','cmd.exe','/d','/c']
        def remaining(limit):
            seconds = min(limit, deadline - time.monotonic())
            require(seconds > 0, 'process-timeout')
            return seconds

        def checked(*args):
            return run([*shell,*args],cwd=root,env=env,seconds=remaining(20),output_limit=512*1024,
                       cancelled=self.cancelled.is_set)
        guide = checked('type', codex_probe_path(instruction))
        require(guide.code == 0 and guide.stdout == expected, 'group-worker-instruction-unreadable')
        # A positive read distinguishes an active profile from a broken runner.
        # A denied read prevents the known legacy fallback from qualifying.
        check=checked('type',read_source)
        require(check.code==0,'group-worker-codex-sandbox-unavailable')
        blocked=checked('type',denied_read)
        require(blocked.code!=0 and not blocked.stdout and canary.read_bytes()==control,
                'group-worker-codex-sandbox-unavailable')
        check=checked('copy','/b','/y',write_source,allowed_write)
        require(check.code==0 and allowed_copy.read_bytes()==marker,
                'group-worker-codex-sandbox-unavailable')
        blocked=checked('copy','/b','/y',write_source,denied_write)
        require(blocked.code!=0 and write_canary.read_bytes()==control,
                'group-worker-codex-sandbox-unavailable')
        stamps=[]
        try:
            result=run([*prefix,'-c','default_permissions="colvia_worker"','-c','web_search="disabled"',
                        '-c','mcp_servers={}','-a','never','exec','--ignore-user-config','--ignore-rules',
                        '--ephemeral','--json','-'],
                       cwd=root,env=env,input_bytes=prompt.encode(),seconds=remaining(60),output_limit=1024*1024,
                       started=lambda _pid:stamps.append(time.monotonic_ns()),cancelled=self.cancelled.is_set)
        except (OSError, RecordError) as exc:
            raise _codex_transport_failure(exc, len(stamps)) from exc
        thread = codex_exec_identity(result, len(stamps))
        return dict(identity=thread,provider='codex',started_ns=stamps[0],closed_ns=time.monotonic_ns(),
                    job_closed=True,exit=0)
