"""Explicit management of the executable used for read-only Git observation."""
from dataclasses import asdict
import hashlib
import time

from .adapters.git import Git, inspect_executable
from .codec import RecordError, canonical_bytes, require
from .managed_entry import read_git_registration
from .platforms.observation_port import location


_REVIEW_SECONDS = 900


def _sha256(raw):
    return hashlib.sha256(raw).hexdigest()


def _registration_plan(home, lease, executable, expires_at):
    raw, previous = read_git_registration(home)
    path, stamp, digest = inspect_executable(executable)
    plan = {
        'version': 1,
        'home': asdict(location(home.root)),
        'runtime_sha256': _sha256(lease.expected),
        'previous_sha256': _sha256(raw) if raw is not None else None,
        'executable': str(path),
        'executable_stamp': asdict(stamp),
        'sha256': digest,
        'expires_at': expires_at,
    }
    return plan, raw, previous, stamp


def preview_registration(home, lease, executable):
    with lease.hold():
        plan, _, previous, _ = _registration_plan(home, lease, executable, int(time.time()) + _REVIEW_SECONDS)
    return dict(state='preview', plan=plan, receipt=_sha256(canonical_bytes(plan)),
                previous=previous)


def register_git(home, lease, plan, receipt, *, replace=False):
    require(type(plan) is dict and type(plan.get('executable')) is str and
            type(plan.get('expires_at')) is int and _sha256(canonical_bytes(plan)) == receipt,
            'git-registration-review-changed')
    with home.files.exclusion(home.root / 'management.lock'), lease.hold():
        require(0 < plan['expires_at'] - int(time.time()) <= _REVIEW_SECONDS,
                'git-registration-review-changed')
        current, previous_raw, previous, stamp = _registration_plan(
            home, lease, plan['executable'], plan['expires_at'])
        require(current == plan, 'git-registration-review-changed')
        same = previous is not None and previous['path'] == plan['executable'] and previous['sha256'] == plan['sha256']
        if same:
            return dict(state='already-registered', **previous)
        require(previous is None or replace, 'git-registration-replacement-required')
        git = Git(plan['executable'], expected_sha256=plan['sha256'], expected_stamp=stamp)
        tool = dict(path=str(git.executable), sha256=git.sha256, version=git.version)
        path = home.root / 'tools.json'
        data = canonical_bytes(dict(version=1, git=tool))
        if previous_raw is None:
            home.files.create(path, data)
        else:
            home.files.replace(path, data, previous_raw)
        try:
            saved = home.files.read(path, 32 * 1024)
        except (OSError, RecordError) as error:
            raise RecordError('git-registration-outcome-unknown') from error
        require(saved == data, 'git-registration-outcome-unknown')
        return dict(state='registered', **tool)
