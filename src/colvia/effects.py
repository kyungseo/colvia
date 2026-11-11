"""Project-wide external-effect barrier shared by application writers.

A durable pending effect is independent of an OS process lock. Reading None
through ValidationView is intentional: reservation racing publication must CAS
fail, not slip past the guard. Read-only queries do not call this function.
"""
from .codec import require

PENDING='effect:pending'


def guard(view, *, expected_effect=None):
    require(view.head(PENDING)==expected_effect,'external-effect-pending')
