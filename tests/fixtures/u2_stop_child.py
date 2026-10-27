"""Two bounded local signal fixtures; no files, network, credentials or descendants."""
import signal
import sys
import time

if sys.argv[1] == 'graceful':
    signal.signal(signal.SIGTERM, lambda *_: sys.exit(0))
elif sys.argv[1] == 'ignore-term':
    signal.signal(signal.SIGTERM, signal.SIG_IGN)
else:
    raise SystemExit(2)
print('ready', flush=True)
while True:
    time.sleep(1)
