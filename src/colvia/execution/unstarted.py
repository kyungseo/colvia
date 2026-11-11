"""Close only a proved fresh caller-owned run whose constructors never spawned."""
import uuid
from ..codec import require,PublicationRefused
from ..effects import PENDING
from .supervisor import terminal_value,revoke_reason


def close_unstarted(journal,run,*,claim,lock,error):
    require(lock.locked,'effect-lock-required')
    state,grant,_,owner,history=journal.read(run)
    require((state.ref,grant.ref,owner.ref)==claim and journal.store.head(PENDING)==owner.ref,
        'execution-startup-owner-changed')
    require(len(history.rows)==1 and not history.revoked and history.terminal is None and
        history.runtime_intent is None and not history.workers and not history.bound,
        'execution-startup-not-fresh')
    cancelled=journal.cancel_requested(run,owner)
    try:
        journal.append(operation='startup-revoked-'+uuid.uuid4().hex,run=run,kind='revoked',
            value=dict(reason=revoke_reason(cancelled,error)),expected_state=state.ref)
        state2,grant2,_,owner2,history2=journal.read(run)
        require(lock.locked and grant2.ref==grant.ref and owner2.ref==owner.ref and
            len(history2.rows)==2 and history2.rows[-1]['kind']=='revoked' and history2.runtime_intent is None,
            'execution-startup-state-changed')
        journal.append(operation='startup-terminal-'+uuid.uuid4().hex,run=run,kind='terminal',
            value=terminal_value(history2,cancelled,error,False),expected_state=state2.ref)
    except PublicationRefused:
        # Inspection only; never replay either event under a new operation ID.
        journal.read(run)
        raise
