"""Finish existing plain Work after external Git initialization, before adoption."""
from contextlib import closing, contextmanager
from pathlib import Path

from .adapters.git import read_file
from .binding import Locator, Membership, Topology
from .codec import decode_envelope, require
from .connection import Connections
from .connection_boundary import check_connection_boundary
from .effects import guard
from .git_transition import MARKER, _repository
from .git_transition_record import KEY
from .maps import scan_map
from .move_setup import _check_idle
from .platforms.observation_port import location
from .platforms.owned_install_files import present
from .records import link
from .workspace import LocalWorkspace


def plain_locator(root):
    return Locator.parse(read_file(root / MARKER, 16384), kind='plain')


def single_repository(root, git):
    require(git is not None, 'git-prerequisite-required')
    top = git.topology(root)
    require(top.root == location(root) and top.gitdir == top.common
            and top.gitdir == location(root / '.git')
            and top.members == (Membership(top.root, top.gitdir),),
            'git-transition-single-root-required')
    require(not present(root / '.git' / 'colvia'), 'git-transition-foreign-locator')
    return top


class FinishingWorkspace(LocalWorkspace):
    def __init__(self, store, root, locator, git, repository):
        super().__init__(store, root, locator.workspace, git=git, locator_reader=lambda: plain_locator(root))
        self.repository = repository

    def topology(self):
        require(single_repository(self.root, self.git) == self.repository, 'workspace-observation-changed')
        return Topology('plain', self.repository.root)

    def observe(self, **options):
        return super().observe(plain_repository=self.repository, **options)

    @contextmanager
    def selected_reader(self, *, verify_path=False):
        with super().selected_reader(verify_path=verify_path) as read:
            def read_files(paths, byte_limit):
                # A path planned before init can now be a native alias for .git.
                paths = tuple(paths)
                for first in {p.split('/')[0] for p in paths}:
                    require(first.casefold() != '.git', 'boundary-swallows-protected')
                    candidate = self.root / first
                    if candidate.is_dir():
                        require(not candidate.samefile(self.root / '.git'), 'boundary-swallows-protected')
                return read(paths, byte_limit)
            yield read_files


def finish(entry, args):
    from .cli import command_readonly, dispatch
    from .managed_entry import authority_for_locator

    allowed = ((args.group == 'backup' and args.action in ('status', 'export'))
               or (args.group == 'operation' and getattr(args, 'action', None) is None)
               or (args.group == 'ordinary' and args.action in (
                   'list', 'view', 'review', 'content', 'plan-review', 'start', 'submit', 'accept', 'revise'))
               or (args.group == 'ordinary' and args.action in ('lifecycle-preview', 'lifecycle-apply')
                   and args.decision in ('resume', 'discard')))
    require(allowed, 'external-init-finish-action')
    git = entry.git()
    root = Path(args.root or Path.cwd()).absolute()
    with entry.home.files.exclusion(entry.home.root / 'management.lock'), entry.lease.hold():
        repo = single_repository(root, git)
        locator = plain_locator(root)
        authority = authority_for_locator(entry, locator)
        readonly = command_readonly(args)
        with closing(authority.store(readonly=readonly)) as store:
            connections = Connections(store)
            project_ref, bound = connections.binding()
            workspace_ref, registration, _ = connections.workspace(locator.workspace)
            require(bound.locator == locator and bound.kind == 'plain' and
                    bound.location == registration.root == repo.root and registration.gitdir is None,
                    'git-transition-folder-changed')
            integration = store.head('project:integration')
            require(integration is not None, 'managed-integration-unavailable')
            config = decode_envelope(integration, store.load(integration))
            require(link(config, 'binding') == project_ref and link(config, 'workspace') == workspace_ref,
                    'managed-integration-stale')
            require(all(ref == workspace_ref for key, ref in scan_map(store.root().heads, store.load)
                        if key.startswith('workspace:')), 'git-transition-single-root-required')
            require(not present(authority.root / 'pending.json') and store.head(KEY) is None,
                    'git-transition-lifecycle-pending')
            if readonly:
                # A stopped import may retain private chunks. Read the published root only.
                guard(store)
                require(not store.needs_rebind() and store.lifecycle_state() == {'fence': None, 'quiescent': None},
                        'connection-move-lifecycle-pending')
            else:
                _check_idle(store)
            check_connection_boundary(entry.home, git, repo, overlap_code='connect-project-overlap',
                                      own=(store.project, store.instance, project_ref))
            _repository(git, repo, ())
            workspace = FinishingWorkspace(store, root, locator, git, repo)
            workspace.verify()
            if args.group == 'ordinary' and args.action == 'revise':
                from .work import WorkService
                work = WorkService(store, workspace)
                ref, head = work._head(args.work)
                require(head.payload['phase'] == 'review' and args.receipt == work._receipt('accept', args.work, ref),
                        'stale-result-receipt')
            if args.group == 'backup' and args.action == 'export':
                for directory in (Path(args.destination).parent, Path(args.scratch)):
                    directory = directory.resolve(strict=True)
                    require(not any(parent.samefile(root) for parent in (directory, *directory.parents)),
                            'external-init-backup-outside')
            return dispatch(args, store, workspace, authority, display=not args.json)
