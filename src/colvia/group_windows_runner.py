"""Run the approved file check with the pinned Windows process-container policy."""
from contextlib import contextmanager, ExitStack
import ctypes as C
import hashlib
import json
from pathlib import Path
import os
import subprocess
import time
from uuid import uuid4

from .codec import RecordError, decode_canonical, require
from .platforms.windows_architecture import native_x64
from .platforms.windows_process import run
from .storage.windows import local_path


MXC_RUNNER = 'native/group-checks/wxc-exec.exe'
MXC_SHA256 = '6d466c6b0109bab4bcace6738e11f886d801ea977346db49707488fcbd3afc8a'
HARNESS = 'lib/colvia/group_windows_harness.py'
DLLS = ('kernel32.dll', 'ntdll.dll', 'ucrtbase.dll', 'ws2_32.dll', 'mswsock.dll', 'nsi.dll')
DIAGNOSTIC_LIMIT = 64 * 1024


def _system_root():
    kernel = C.WinDLL('kernel32', use_last_error=True)
    kernel.GetWindowsDirectoryW.argtypes = (C.c_wchar_p, C.c_uint32)
    kernel.GetWindowsDirectoryW.restype = C.c_uint32
    path = C.create_unicode_buffer(32768)
    length = kernel.GetWindowsDirectoryW(path, len(path))
    require(0 < length < len(path), 'group-check-system-root-unavailable')
    return Path(local_path(path.value))


def _input_ready(child, transcript, nonce, executable):
    prefix = b'COLVIA-FILE-CHECK-READY ' + nonce + b' '
    received = [line.rstrip(b'\r\n')[len(prefix):] for line in transcript.splitlines(keepends=True)
                if line.endswith(b'\n') and line.startswith(prefix)]
    if not received:
        return False
    require(len(received) == 1 and 0 < len(received[0]) <= 10 and received[0].isdigit(),
            'group-check-runtime-handshake-invalid')
    require(child.contains_process(int(received[0]), executable), 'group-check-runtime-process-unowned')
    return True


def _policy(python, harness, nonce, canaries, cwd, root, scratch, windows, protected, seconds):
    paths = [python, harness, *canaries, cwd, root, scratch, windows, *protected]
    for path in paths:
        local_path(path)
    env = {'SystemRoot': str(windows), 'LOCALAPPDATA': str(scratch), 'TEMP': str(scratch), 'TMP': str(scratch)}
    return dict(version='1.0.0', containment='processcontainer',
                lifecycle={'destroyOnExit': True, 'preservePolicy': False},
                process={'commandLine': subprocess.list2cmdline([str(python), '-I', '-B', '-S', '-X', 'utf8',
                         str(harness), 'supervise', nonce.decode('ascii'), *map(str, canaries)]),
                         'cwd': str(cwd), 'env': [name+'='+value for name,value in env.items()],
                         'inheritDefaultEnv': False, 'timeout': seconds * 1000},
                filesystem={'readwritePaths': [str(root), str(scratch)],
                            'readonlyPaths': [str(python.parent), str(harness), *[str(windows/'System32'/dll) for dll in DLLS]],
                            'deniedPaths': [str(path) for path in protected]},
                network={'egress': {'default': 'deny'}, 'ingress': {'default': 'deny', 'hostLoopback': 'deny'}},
                ui={'disable': True, 'clipboard': 'none', 'injection': False})


class ManagedFileCheck:
    """Resolve inputs only through the selected and verified private slot."""

    def __init__(self, entry):
        self.entry = entry

    def _manifest(self):
        lease = self.entry.lease
        slot = lease.verified
        location = self.entry.home.slots.root / 'slots' / slot.slot
        raw = self.entry.home.files.read(location/'manifest.json', 4*1024*1024)
        require(hashlib.sha256(raw).hexdigest() == slot.manifest_sha256, 'slot-manifest-mismatch')
        value = decode_canonical(raw)
        inputs = {item['path']: item for item in value['inventory']}
        require(value['os'] == 'windows' and value['architecture'] == 'x64' and
                inputs.get(MXC_RUNNER, {}).get('sha256') == MXC_SHA256 and HARNESS in inputs,
                'group-check-runtime-unavailable')
        require(Path(slot.python) == location/value['python'] and value['python'].startswith('runtime/'),
                'group-check-runtime-unavailable')
        return location, value['python'], inputs

    def available(self):
        if not native_x64():
            return False
        try:
            self._manifest()
        except (OSError, RecordError):
            return False
        return True

    @contextmanager
    def _pinned(self):
        with self.entry.lease.hold(), ExitStack() as handles:
            location, python, manifest = self._manifest()
            files = self.entry.home.files
            api = files.api
            inputs = {name: row for name, row in manifest.items()
                      if name.startswith(('runtime/', 'native/group-checks/')) or name == HARNESS}
            require(len(inputs) <= 512 and set(n for n in inputs if n.startswith('native/group-checks/')) == {MXC_RUNNER},
                    'group-check-runtime-inventory')
            opened = {}

            def pin(relative):
                if relative in opened:
                    return opened[relative]
                path = location / relative
                want = inputs.get(relative)
                handle = handles.enter_context(api.opened(path, access=0x80020080 if want else 0x20080, share=1))
                state = api.state(handle, path)
                api.private(handle)
                require(state['directory'] == (want is None), 'group-check-runtime-inventory')
                if want:
                    require(state['links'] == 1 and state['size'] == want['size'], 'group-check-runtime-inventory')
                    digest = hashlib.sha256()
                    total = 0
                    with files._stream_handle(handle) as stream:
                        while chunk := stream.read(1024*1024):
                            total += len(chunk)
                            require(total <= want['size'], 'group-check-runtime-inventory')
                            digest.update(chunk)
                    require(total == want['size'] and digest.hexdigest() == want['sha256'],
                            'group-check-runtime-inventory')
                opened[relative] = (handle, state)
                return handle,state

            handles.enter_context(api.ancestors(location))
            pin('.')
            for relative in inputs:
                for parent in reversed(Path(relative).parents):
                    pin(parent.as_posix())
                pin(relative)

            def check_inventory():
                for relative,(handle,state) in opened.items():
                    path = location / relative
                    require(api.state(handle, path) == state, 'group-check-runtime-changed')
                    if state['directory'] and (relative == 'runtime' or relative.startswith('runtime/') or
                                               relative == 'native/group-checks'):
                        names = {name for name in opened if Path(name).parent.as_posix() == relative and name != relative}
                        with os.scandir(path) as entries:
                            require({(Path(relative)/entry.name).as_posix() for entry in entries} == names,
                                    'group-check-runtime-inventory')

            check_inventory()
            runtime = dict(manifest=self.entry.lease.verified.manifest_sha256, runner=MXC_SHA256,
                           harness=inputs[HARNESS]['sha256'])
            yield (location/MXC_RUNNER, location/python, location/HARNESS), runtime
            check_inventory()

    def __call__(self, port, definition, root, scratch):
        start = time.monotonic_ns()
        stdout = stderr = b''
        state, code, runtime = 'unavailable', None, None
        limit = definition['output_bytes']
        try:
            require(native_x64(), 'group-platform-unqualified')
            control = scratch.parent/'control'
            port.files.create_directory(control)
            canaries = (control/'protected.txt', scratch.parent/'unlisted.txt')
            payload = b'Colvia file-check protection control\n'
            for canary in canaries:
                port.files.create(canary, payload)
                require(port.files.read(canary) == payload, 'group-check-protection-control-unavailable')
            nonce = uuid4().hex.encode('ascii')
            result_nonce = uuid4().hex.encode('ascii')
            script = definition['script'].encode('utf-8')
            cwd = root/definition['cwd']
            require(port.observer.location(cwd) is not None, 'group-check-cwd-unavailable')
            windows = _system_root()
            seconds = definition['timeout_seconds']
            with self._pinned() as ((runner, python, harness), runtime):
                require(not any(p.is_relative_to(root) or p.is_relative_to(scratch) for p in (runner, python, harness)),
                        'group-check-runtime-overlap')
                protected = [port.root, port.authority/'stores', port.authority/'lifecycle',
                             port.authority/'active.json', port.authority/'effect.lock',
                             port.authority/'lifecycle.lock', control]
                stage = port.authority/'effects'
                try:
                    port.files.private_directory(stage)
                except FileNotFoundError:
                    pass
                else:
                    protected.append(stage)
                request = _policy(python, harness, nonce, canaries, cwd, root, scratch, windows, protected, seconds)
                raw = json.dumps(request, ensure_ascii=False, separators=(',', ':')).encode('utf-8')
                request_file = scratch.parent/'request.json'
                port.files.create(request_file, raw)
                with port.api.ancestors(request_file), port.api.opened(request_file, share=1):
                    env = {'SystemRoot': str(windows), 'TEMP': str(scratch), 'TMP': str(scratch)}
                    result = run([str(runner),str(request_file)], cwd=runner.parent, env=env,
                                 seconds=seconds+5, output_limit=limit+DIAGNOSTIC_LIMIT,
                                 input_bytes=result_nonce+b'\n'+script,
                                 admit_input=lambda child, data: _input_ready(child, data, nonce, python))
                require(all(port.files.read(canary) == payload for canary in canaries)
                        and port.files.read(request_file, 65536) == raw,
                        'group-check-protection-control-changed')
            stdout, stderr = result.stdout, result.stderr
            marker = (b'COLVIA-FILE-CHECK-RESULT '+result_nonce+b' '+hashlib.sha256(script).hexdigest().encode('ascii')
                      +b' '+str(result.code).encode('ascii'))
            lines = stdout.splitlines()
            if lines.count(marker) == 1:
                state, code = 'exited', result.code
            else:
                stderr += b'\nIsolated file-check result missing.'
        except (OSError, RecordError) as error:
            reason = error.code if isinstance(error, RecordError) else 'group-check-runtime-unavailable'
            state = {'process-timeout': 'timeout', 'process-output-limit': 'output-limit'}.get(reason, 'unavailable')
            code = None
            stderr = reason.encode('ascii')
        if len(stdout)+len(stderr)>limit:
            state,code='output-limit',None
            stdout = stdout[:limit]
            stderr = stderr[:limit-len(stdout)]
        return dict(outcome=state, exit_code=code, elapsed_ns=time.monotonic_ns()-start, runtime=runtime),stdout,stderr
