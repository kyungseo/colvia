"""Explicit, account-scoped complete removal from the external verified installer."""
from contextlib import ExitStack
import hashlib
import os
from pathlib import Path
import re

from ..codec import METADATA_LIMIT, canonical_bytes, decode_canonical, require
from ..management import ManagerHome
from ..managed_entry import configured_git
from ..platforms.owned_install_files import present
from ..project_setup import ProjectSetup
from ..storage.sqlite import _token
from .purge_inventory import check_tree, fingerprint, inventory
from .purge_progress import pending_path, publish, read_record
from .purge_projects import detach_approved, project_list
from .uninstall import MARKER, OTHER_PENDING, Uninstall, _recorder

# Reserve space for the file identity attached when publishing the record.
MAX_PLAN = METADATA_LIMIT - 512


def digest(value):
    return hashlib.sha256(canonical_bytes(value)).hexdigest()


def standard_account(root, os_name):
    if os_name == 'windows':
        import ctypes
        from ..platforms.windows_paths import local_appdata
        expected = Path(local_appdata())/'Colvia'
        require(not ctypes.windll.shell32.IsUserAnAdmin(), 'uninstall-standard-account-required')
    else:
        from ..platforms.darwin_notices import standard_root
        expected = standard_root()
        require(os.getuid() != 0 and os.getuid() == os.geteuid(), 'uninstall-standard-account-required')
    require(root == expected, 'uninstall-default-home-required')


class CompleteRemoval:
    def __init__(self, root, files, os_name, architecture, operation):
        _token(operation)
        require(re.fullmatch(r'[a-z0-9][a-z0-9-]{0,63}', operation), 'purge-operation-id')
        standard_account(root, os_name)
        self.root, self.files = root, files
        self.os_name, self.architecture = os_name, architecture
        self.operation = operation
        self.journal = root.with_name('Colvia-removal-' + operation)
        self.held = root.with_name('Colvia-retired-' + operation)

    def _home(self):
        return ManagerHome(self.root, files=self.files, os_name=self.os_name, architecture=self.architecture)

    def _locks(self, home, stack):
        paths = [home.root/'management.lock', home.slots.root/'runtime.lock']
        if present(home.root/'trust/update.lock'):
            paths.append(home.root/'trust/update.lock')
        for path in paths:
            stack.enter_context(self.files.exclusion(path, timeout=1))

    def _claim_path(self, name):
        return self.journal/('entry-'+hashlib.sha256(name.encode()).hexdigest())

    def _park_windows_locks(self, nodes, stack, checkpoint):
        # NTFS refuses to rename a directory with open descendant handles. Move
        # the locked guard *files* out first. Old clients require the original
        # paths; there is no unlock/relock interval. Resume recognizes either
        # position by the previewed file identity.
        from ..storage.windows import local_path
        f = self.files
        for name in ('management.lock','runtime/runtime.lock','trust/update.lock'):
            if name not in nodes:
                continue
            source, parked = self.root/name, self._claim_path(name)
            require(present(source) != present(parked), 'purge-lock-position-changed')
            actual = source if present(source) else parked
            stack.enter_context(f.exclusion(actual, timeout=1, allow_parent_move=True))
            require(fingerprint(f,actual) == nodes[name], 'purge-lock-replaced')
            if actual == source:
                with f.api.ancestors(source), f.api.ancestors(parked):
                    f.api.ok(f.api.MoveFileExW(local_path(source),local_path(parked),8))
                require(fingerprint(f, parked) == nodes[name], 'purge-lock-replaced')
                checkpoint('lock-parked')

    def _plan(self, home, exclude, *, startup=None):
        startup = {} if startup is None else startup
        require(not any(present(self.root/p) for p in (MARKER, *OTHER_PENDING) if p not in startup), 'purge-maintenance-pending')
        home.requirements()
        projects = project_list(home, ProjectSetup(home, configured_git(home)), exclude)
        nodes = inventory(home)
        check_tree(self.root, self.files, nodes | startup)
        recorder = _recorder(home)
        return dict(version=1, operation=self.operation, installation=fingerprint(self.files, self.root),
                    projects=projects, nodes=nodes, exclude_unavailable=exclude,
                    notice=recorder.current() if recorder else None)

    def preview(self, exclude=False, *, current_preparation=None):
        require(not present(self.journal) and not present(self.held), 'purge-operation-already-used')
        home = self._home()
        with ExitStack() as stack:
            self._locks(home, stack)
            if present(self.root/MARKER):
                current = decode_canonical(self.files.read(self.root/MARKER))
                if isinstance(current, dict) and 'purge' in current:
                    return dict(state='purge-resume-required', receipt=None)
                _, _, prior = Uninstall(home).check_reinstall()
                return dict(state='records-retained-after-uninstall', receipt=None,
                            operation=prior['operation'], next_action='manual-cleanup-or-restore')
            plan = self._plan(home, exclude)
        # These paths are informational: enumeration alone grants no ownership.
        previous_preparations = sorted(str(p) for p in self.root.parent.iterdir()
                                       if p.name.startswith('Colvia-bootstrap-') and p != current_preparation)
        require(len(canonical_bytes(plan)) <= MAX_PLAN, 'purge-inventory-limit')
        ready = all(p['state'] != 'unavailable' for p in plan['projects'])
        groups = {'project_databases': 0, 'backups': 0, 'runtime_files': 0, 'other_account_files': 0}
        for path, item in plan['nodes'].items():
            if item['kind'] == 'directory':
                continue
            if path.startswith('authorities/') and path.endswith('/state.sqlite3'):
                group = 'project_databases'
            elif path.startswith('backups/'):
                group = 'backups'
            elif path.startswith('runtime/slots/'):
                group = 'runtime_files'
            else:
                group = 'other_account_files'
            groups[group] += 1
        return dict(state='purge-preview' if ready else 'purge-unavailable-folders',
                    operation=self.operation, projects=plan['projects'], account_file_counts=groups, retained_preparation_paths=previous_preparations, permanent_account_items=sorted(plan['nodes']),
                    receipt=digest(plan) if ready else None)

    def apply(self, receipt, *, resume=False, exclude=False, checkpoint=lambda _: None):
        require(type(receipt) is str and re.fullmatch('[a-f0-9]{64}', receipt), 'purge-receipt-invalid')
        f, journal = self.files, self.journal
        approved = journal/'approved.json'
        done = journal.with_name(journal.name+'-'+receipt+'.done')
        if resume and present(done):
            return self._close(done, receipt)
        if not resume or not present(approved):
            self._initialize(receipt, resume, exclude, checkpoint)
        f.private_directory(journal)
        # The approved plan is also the operation lock. No anonymous empty lock
        # file can strand a half-created journal. Read its bytes before taking
        # the Windows lock because NTFS enforces byte-range locks for reads.
        proof = fingerprint(f, approved)
        plan = decode_canonical(read_record(f, approved, receipt))
        require(plan['version'] == 1 and plan['operation'] == self.operation and digest(plan) == receipt,
                'purge-review-changed')
        with f.exclusion(approved, timeout=1):
            from ..platforms.owned_install_files import _info
            require(_info(f, approved)['identity'] == proof['identity'], 'purge-journal-changed')
            result = self._continue(plan, receipt, checkpoint)
            names = ('approved.json','final.json','retired.json')
            draft = pending_path(journal, receipt, 'completion')
            entries = {p.name for p in journal.iterdir()}
            require(entries - {draft.name} == set(names), 'purge-journal-changed')
            terminal = dict(receipt=receipt, result=result, directory=fingerprint(f, journal),
                            files={n:proof if n == 'approved.json' else fingerprint(f, journal/n) for n in names})
            publish(f, done, canonical_bytes(terminal), draft, checkpoint, 'completion', receipt)
        return self._close(done, receipt)

    def _initialize(self, receipt, resume, exclude, checkpoint):
        f, home = self.files, self._home()
        fence = self.root/MARKER
        marker = canonical_bytes(dict(purge=receipt, operation=self.operation))
        pending = pending_path(self.root, receipt, 'fence')
        approved = self.journal/'approved.json'
        require(not present(self.held), 'purge-installation-replaced')
        with ExitStack() as locks:
            self._locks(home, locks)
            require(not present(self.held), 'purge-installation-replaced')
            startup = {}
            for path in (pending, fence):
                if present(path):
                    require(resume and read_record(f, path, receipt) == marker, 'purge-other-operation')
                    startup[path.name] = fingerprint(f, path)
            require(len(startup) <= 1, 'purge-preparation-changed')
            require(not resume or bool(startup), 'purge-operation-not-started')
            fenced = MARKER in startup
            if present(self.journal):
                require(resume and fenced, 'purge-unconfirmed-journal')
                f.private_directory(self.journal)
                if present(approved):
                    return
                draft = pending_path(self.journal, receipt, 'approval')
                require(all(p == draft for p in self.journal.iterdir()), 'purge-journal-changed')
            # Before the first plan copy is durable, recover the missing exclude
            # choice solely by reproducing the receipt from the live account.
            plan = self._plan(home, True if resume else exclude, startup=startup)
            if resume and digest(plan) != receipt and all(p['state'] != 'excluded' for p in plan['projects']):
                plan['exclude_unavailable'] = False
            raw = canonical_bytes(plan)
            require(digest(plan) == receipt and all(p['state'] != 'unavailable' for p in plan['projects']),
                    'purge-review-changed')
            require(len(raw) <= MAX_PLAN, 'purge-inventory-limit')
            if not fenced:
                publish(f, fence, marker, pending, checkpoint, 'fence', receipt)
                checkpoint('fenced')
            if not present(self.journal):
                f.create_directory(self.journal)
                checkpoint('journal-created')
            publish(f, approved, raw, pending_path(self.journal, receipt, 'approval'), checkpoint, 'approval', receipt)

    def _continue(self, plan, receipt, checkpoint):
        f = self.files
        marker = canonical_bytes(dict(purge=receipt, operation=self.operation))
        final = self.journal/'final.json'
        if not present(final) or (not present(self.held) and not present(self.journal/'retired.json')
                                      and present(self.root/MARKER) and read_record(f, self.root/MARKER, receipt) == marker):
            require(fingerprint(f, self.root) == plan['installation'] and not present(self.held),
                    'purge-installation-replaced')
            home = self._home()
            with ExitStack() as locks:
                self._locks(home, locks)
                fence = self.root/MARKER
                require(read_record(f, fence, receipt) == marker, 'purge-other-operation')
                setup = ProjectSetup(home, configured_git(home))
                additions = set()
                for n, row in enumerate(plan['projects']):
                    if row['state'] == 'connected':
                        additions.update(detach_approved(home, setup, row, 'purge-'+receipt[:24]+'-'+str(n), checkpoint))
                recorder = _recorder(home)
                if recorder:
                    recorder.disable_for_uninstall(self.operation, plan['notice'])
                nodes = inventory(home)
                mutable_dbs = set()
                for n, row in enumerate(plan['projects']):
                    if row['state'] != 'connected':
                        continue
                    authority = home.authority(row['project'])
                    base = 'authorities/'+row['project']
                    mutable_dbs.add(base+'/stores/'+authority.pointer_value()['generation']+'/state.sqlite3')
                if plan['notice']:
                    suffix = hashlib.sha256(('uninstall:'+self.operation).encode()).hexdigest()[:32]
                    area = 'operations/notice-'+suffix
                    additions.update((area, area+'/intent.json', area+'/completed.json'))
                require(set(nodes) - set(plan['nodes']) <= additions, 'purge-unapproved-new-item')
                for name, old in plan['nodes'].items():
                    now = nodes.get(name)
                    if name in mutable_dbs or (plan['notice'] and name == 'notice-registration.json'):
                        require(now is not None and (name == 'notice-registration.json' or
                                now['identity'] == old['identity']), 'purge-records-replaced')
                    else:
                        require(old == now, 'purge-account-item-changed')
                check_tree(self.root, f, dict(nodes, **{MARKER:fingerprint(f, fence)}))
                raw = canonical_bytes(dict(receipt=receipt, nodes=nodes))
                require(len(raw) <= MAX_PLAN, 'purge-inventory-limit')
                if present(final):
                    require(read_record(f, final, receipt) == raw, 'purge-final-list-changed')
                else:
                    publish(f, final, raw, pending_path(self.journal, receipt, 'inventory'), checkpoint, 'inventory', receipt)
                    checkpoint('inventory-saved')
                publish(f, fence, canonical_bytes(dict(purge=receipt, inventory=digest(decode_canonical(raw)))),
                        pending_path(self.journal, receipt, 'seal'), checkpoint, 'seal', receipt, replace=marker)
        saved = decode_canonical(read_record(f, final, receipt))
        require(saved['receipt'] == receipt, 'purge-final-list-changed')
        seal = canonical_bytes(dict(purge=receipt, inventory=digest(saved)))
        retired = self.journal/'retired.json'
        if not present(retired):
            base = self.held if present(self.held) else self.root
            require(fingerprint(f, base) == plan['installation'] and read_record(f, base/MARKER, receipt) == seal,
                    'purge-final-list-changed')
            fence_node = fingerprint(f, base/MARKER)
        else:
            retirement = decode_canonical(read_record(f, retired, receipt))
            require(retirement['inventory'] == digest(saved) and retirement['receipt'] == receipt,
                    'purge-final-list-changed')
            fence_node = retirement['fence']
        nodes = dict(saved['nodes'], **{MARKER:fence_node})
        if not present(self.held) and not present(retired):
            parked = {self._claim_path(n).name for n in ('management.lock','runtime/runtime.lock','trust/update.lock')
                      if self.os_name == 'windows' and n in nodes}
            require({p.name for p in self.journal.iterdir()} - parked == {'approved.json','final.json'},
                    'purge-journal-changed')
            with ExitStack() as locks:
                if self.os_name == 'windows':
                    self._park_windows_locks(nodes, locks, checkpoint)
                else:
                    self._locks(self._home(), locks)
                require(fingerprint(f, self.root) == plan['installation'] and read_record(f, self.root/MARKER, receipt) == seal,
                        'purge-installation-replaced')
                visible = dict(nodes)
                if self.os_name == 'windows':
                    for name in ('management.lock','runtime/runtime.lock','trust/update.lock'):
                        visible.pop(name, None)
                check_tree(self.root, f, visible)
                identity = plan['installation']['identity']
                f.publish_directory(self.root, self.held, identity if self.os_name=='windows' else identity[:2])
                f.sync_directory(self.root.parent)
            checkpoint('retired')
        seal = canonical_bytes(dict(receipt=receipt, inventory=digest(saved), fence=fence_node))
        if not present(retired):
            require(fingerprint(f, self.held) == plan['installation'], 'purge-installation-replaced')
            visible = dict(nodes)
            if self.os_name == 'windows':
                for name in ('management.lock','runtime/runtime.lock','trust/update.lock'):
                    if name in visible:
                        require(fingerprint(f,self._claim_path(name)) == visible.pop(name), 'purge-lock-replaced')
            check_tree(self.held, f, visible)
            publish(f, retired, seal, pending_path(self.journal, receipt, 'retirement'), checkpoint, 'retirement', receipt)
        require(read_record(f, retired, receipt) == seal, 'purge-retirement-changed')
        if present(self.held):
            require(fingerprint(f, self.held) == plan['installation'], 'purge-installation-replaced')
            remaining = check_tree(self.held, f, nodes, partial=True)
            def order(name):
                # Keep project DBs, backups, then the admission fence until last.
                return (name == MARKER, name.split('/')[0] in ('authorities','backups'),
                        -name.count('/'), name)
            # Claim each exact object in the owner's private operation directory.
            # Recheck its identity and bytes *after* the exclusive move, before
            # deleting, so a swapped-in path cannot authorize erasing a new file.
            journal_identity = f.directory_identity(self.journal)
            for name in sorted(nodes, key=order):
                path = self.held/name
                claimed = self._claim_path(name)
                if name in remaining:
                    require(not present(claimed) and fingerprint(f, path, nodes[name]) == nodes[name],
                            'purge-account-item-changed')
                    if self.os_name == 'windows':
                        from ..storage.windows import local_path
                        with f.api.ancestors(path), f.api.ancestors(claimed):
                            f.api.ok(f.api.MoveFileExW(local_path(path), local_path(claimed), 8))
                    else:
                        from ..platforms.exclusive import rename
                        with ExitStack() as handles:
                            descriptors = []
                            for parent in (path.parent,self.journal):
                                fd = os.open(parent, os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW)
                                handles.callback(os.close, fd)
                                if parent == self.journal:
                                    expected = journal_identity
                                elif parent == self.held:
                                    expected = plan['installation']['identity'][:2]
                                else:
                                    expected = nodes[parent.relative_to(self.held).as_posix()]['identity'][:2]
                                require([os.fstat(fd).st_dev,os.fstat(fd).st_ino] == expected,
                                        'purge-parent-changed')
                                descriptors.append(fd)
                            rename(descriptors[0],path.name,descriptors[1],claimed.name)
                    checkpoint('claimed')
                if present(claimed):
                    require(fingerprint(f, claimed, nodes[name]) == nodes[name], 'purge-account-item-changed')
                    if nodes[name]['kind'] == 'directory':
                        claimed.rmdir()
                    else:
                        claimed.unlink()
                    f.sync_directory(self.journal)
                    if name.endswith('/state.sqlite3'):
                        checkpoint('after-db')
            self.held.rmdir()
            f.sync_directory(self.held.parent)
        return dict(state='account-removed', excluded=[p for p in plan['projects'] if p['state']=='excluded'])

    def _close(self, done, receipt):
        f, journal = self.files, self.journal
        terminal = decode_canonical(read_record(f, done, receipt))
        require(terminal['receipt'] == receipt, 'purge-completion-changed')
        if present(journal):
            require(fingerprint(f, journal) == terminal['directory'], 'purge-journal-changed')
            names = ('final.json','retired.json','approved.json')
            require(set(names) == set(terminal['files']) and
                    {p.name for p in journal.iterdir()} <= set(names), 'purge-journal-changed')
            for name in names:
                path = journal/name
                if present(path):
                    require(fingerprint(f, path) == terminal['files'][name], 'purge-journal-changed')
                    path.unlink()
                    f.sync_directory(journal)
            journal.rmdir()
            f.sync_directory(journal.parent)
        done.unlink()
        f.sync_directory(done.parent)
        return terminal['result']
