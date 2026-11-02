"""A partial adapter with an already-closed stderr channel for transport unit tests."""
from hv2ref.official_adapter import Rpc


def quiet_rpc():
    rpc = Rpc.__new__(Rpc)
    rpc.stderr_eof = True
    rpc.stderr_refused = False
    rpc.in_initialize = False
    rpc.initialize_failure = None
    rpc.interrupted = False
    return rpc
