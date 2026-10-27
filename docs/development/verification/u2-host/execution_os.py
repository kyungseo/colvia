"""Minimum execution selection; detection never admits a profile or consumes budget.

Only the current macOS implementation is selected. Future OS work must preserve
operation semantics and qualify its profile; there is no placeholder backend.
"""
import sys


def execution_os(require, *, purpose='read-host', platform=None):
    selected = sys.platform if platform is None else platform
    require(selected == 'darwin', 'unsupported-execution-platform')
    require(purpose in ('read-host', 'claude-native', 'codex-v58'), 'unknown-execution-purpose')
    # Import after platform refusal: fcntl and native symbols are not portable.
    try:
        from ._macos_execution import MacExecution
    except (ImportError, OSError) as error:
        require(False, 'execution-capability-unavailable: ' + type(error).__name__)
    runtime = MacExecution(require)
    runtime.preflight(purpose)
    return runtime
