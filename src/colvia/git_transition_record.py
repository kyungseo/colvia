"""Recorded approval for changing a connected project's binding kind."""
from .codec import require
from .graph import Schema


KEY = 'connection:git-transition'
KIND = 'connection.git-transition'


def schema():
    from .records import fields, one, text
    from .storage.sqlite import _token

    def check(payload):
        fields(payload, {'operation', 'receipt', 'statement', 'phase', 'observed'})
        _token(payload['operation'])
        text(payload['statement'])
        digest = payload['receipt']
        require(isinstance(digest, str) and len(digest) == 64 and
                all(c in '0123456789abcdef' for c in digest), 'git-transition-invalid-record')
        require(payload['phase'] in ('pending', 'confirmed', 'completed'), 'git-transition-invalid-record')
        observed = payload['observed']
        if payload['phase'] == 'confirmed':
            require(isinstance(observed, dict) and set(observed) == {'files', 'git'} and
                    all(isinstance(v, str) and len(v) == 64 and all(c in '0123456789abcdef' for c in v)
                        for v in (observed['files'], observed['git'])), 'git-transition-invalid-record')
        else:
            require(observed is None, 'git-transition-invalid-record')
        one(payload, 'prior', optional=True)
        require(bool(payload['links']['prior']) == (payload['phase'] != 'pending'), 'git-transition-invalid-record')
        one(payload, 'old')
        one(payload, 'new', optional=True)
        require(bool(payload['links']['new']) == (payload['phase'] == 'completed'), 'git-transition-invalid-record')

    return Schema(KIND, 1, {'old': 'decision', 'new': 'decision', 'prior': 'decision'}, check,
                  {'old': frozenset({'project.integration'}), 'new': frozenset({'project.integration'}), 'prior': frozenset({KIND})})


def require_current_approval(store, plan):
    from .codec import decode_envelope
    from .records import link

    if store.head(KEY) is not None:
        baseline = link(plan, 'baseline')
        observed = decode_envelope(baseline, store.load(baseline))
        workspace = link(observed, 'workspace')
        owner = link(decode_envelope(workspace, store.load(workspace)), 'project')
        bound = decode_envelope(owner, store.load(owner))
        require(bound.ref.kind == 'project.binding' and bound.payload['kind'] == 'git',
                'git-transition-new-work-required')

