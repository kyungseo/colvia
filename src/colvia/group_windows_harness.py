"""Supervise one approved Python file check in the existing Windows Job."""
import hashlib
import os
import subprocess
import sys


def require_protection(paths):
    for path in paths:
        for mode in (os.O_RDONLY, os.O_WRONLY):
            try:
                handle = os.open(path, mode)
            except PermissionError:
                continue
            else:
                os.close(handle)
                raise SystemExit('Protected file access was possible.')


def approved_program(paths):
    require_protection(paths)
    raw = sys.stdin.buffer.read(65537)
    if not raw or len(raw) > 65536:
        raise SystemExit('Approved file check input is unavailable.')
    scope = {'__name__': '__main__', '__file__': '<approved-file-check>'}
    exec(compile(raw.decode('utf-8'), scope['__file__'], 'exec', dont_inherit=True), scope)


def main():
    mode, *inputs = sys.argv[1:]
    if mode == 'check':
        approved_program(inputs)
        return 0
    if mode != 'supervise':
        raise SystemExit('Unrecognized file-check mode.')
    ready_nonce, *paths = inputs
    require_protection(paths)
    print('COLVIA-FILE-CHECK-READY', ready_nonce, os.getpid(), flush=True)
    # The parent supplies the payload only after authenticating this waiting
    # process. The check receives approved source but no result nonce.
    result_nonce, delimiter, raw = sys.stdin.buffer.read(65570).partition(b'\n')
    if delimiter != b'\n' or len(result_nonce) != 32 or not raw or len(raw) > 65536:
        raise SystemExit('Approved file check input is unavailable.')
    identity = hashlib.sha256(raw).hexdigest()
    child = subprocess.run([sys.executable, '-I', '-B', '-S', '-X', 'utf8', __file__, 'check', *paths], input=raw)
    print('\nCOLVIA-FILE-CHECK-RESULT', result_nonce.decode('ascii'), identity, child.returncode, flush=True)
    return child.returncode


if __name__ == '__main__':
    raise SystemExit(main())
