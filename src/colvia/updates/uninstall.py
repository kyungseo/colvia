"""Record-preserving removal, driven by the verified installer, outside the live slot."""

import hashlib
import os
import re
import uuid
from contextlib import closing
from pathlib import Path, PurePosixPath

from ..codec import canonical_bytes, decode_canonical, decode_envelope, require
from ..maps import scan_map
from ..platforms.owned_install_files import capture, move, present
from ..storage.sqlite import _token
from .initial_files import InitialFiles
from .slots import verify_payload

MARKER = 'uninstall.json'
LIMIT = 4 * 1024 * 1024
OTHER_PENDING = ('native-update.json', 'notice-app.pending',
                 'connection-repair.pending', 'notice-registration.pending')


def require_default_home(home):
    if home.os_name == 'windows':
        import ctypes
        from ..platforms.windows_paths import local_appdata
        standard = Path(local_appdata()) / 'Colvia'
        require(not ctypes.windll.shell32.IsUserAnAdmin(), 'uninstall-standard-account-required')
    else:
        from ..platforms.darwin_notices import standard_root
        standard = standard_root()
        require(os.geteuid() == os.getuid() and os.getuid() != 0, 'uninstall-standard-account-required')
    require(home.files.directory_identity(standard) == home.files.directory_identity(home.root),
            'uninstall-default-home-required')


def _sha(raw):
    return hashlib.sha256(raw).hexdigest()


def _recorder(home):
    if home.os_name == 'windows':
        from ..platforms.windows_notices import WindowsNotices
        return WindowsNotices(home)
    return None


class Uninstall:
    def __init__(self, home):
        require_default_home(home)
        self.home = home
        self.root = home.root
        self.f = home.files
        self.marker = self.root / MARKER

    def _area(self, operation):
        _token(operation)
        require(len(operation) <= 110, 'uninstall-operation-limit')
        return self.root / 'operations' / operation

    def _installed_target(self, pointer):
        from .package import descriptor
        from ..manager_entry import update_configuration
        slot = self.home.slots.verify(pointer)
        require('managed-uninstall' in slot.features, 'uninstall-runtime-not-supported')
        area = self.root / 'operations' / slot.slot
        if self.f.exists(area / 'release.json'):
            record = decode_canonical(self.f.read(area / 'release.json', LIMIT))
        else:
            record = decode_canonical(self.f.read(area / 'prepared.json', LIMIT))
        require(record['target'] == pointer, 'uninstall-release-receipt-changed')
        download = record['download']
        config = update_configuration(self.home)
        info = descriptor(download['custom'], channel=config['channel'], os_name=self.home.os_name,
                          architecture=self.home.architecture)
        require(download['path'] == config['target'] and info['manifest_sha256'] == slot.manifest_sha256
                and info['sequence'] == slot.sequence and info['release'] == slot.release,
                'uninstall-release-receipt-changed')
        return download['sha256']

    def _bin_inventory(self, root):
        bin_root = root / 'bin'
        names = set()
        if present(bin_root):
            self.f.private_directory(bin_root)
            for path in bin_root.rglob('*'):
                names.add(path.relative_to(root).as_posix())
        return names

    def _snapshot(self, operation):
        from .installation import configuration
        h, f = self.home, self.f
        require(not present(self.marker), 'uninstall-already-started')
        require(not any(present(self.root / name) for name in OTHER_PENDING), 'uninstall-other-operation-pending')
        selection = h.slots.selection()[1]
        selected = selection['selected']
        target_hash = self._installed_target(selected)
        _, _, states = h.requirements()
        for state in states:
            with closing(h.authority(state['project']).store(readonly=True)) as store:
                for key, ref in scan_map(store.root().heads, store.load):
                    if key.startswith('work:'):
                        require(ref.kind == 'work.head' and decode_envelope(ref, store.load(ref)).payload['phase'] not in ('active','paused'),
                                'uninstall-active-work')
        receipt = decode_canonical(f.read(self.root / 'trust/state.json'))
        slot = h.slots.verify(selected)
        location = h.slots.root / 'slots' / slot.slot
        config = configuration(f, location)
        native = f.read(location / config['native_entry'], 64 * 1024 * 1024)
        dirs, files = InitialFiles(h, operation, selected, native).expected()
        require(self._bin_inventory(self.root) == (dirs | set(files)) - {'bin', 'entry.json', 'receiver.json'},
                'uninstall-extra-installed-file')
        nodes = []
        for name, (expected, executable) in sorted(files.items()):
            path = self.root / name
            observed = capture(f, path)
            mode = '100755' if executable and h.os_name != 'windows' else '100644'
            require(observed['sha256'] == _sha(expected) and observed['mode'] == mode,
                    'uninstall-owned-file-changed')
            nodes.append(dict(path=name, snapshot=observed))
        # Empty descendants are relocated after their children. In particular,
        # the retained receiver executable never remains in a recognized .app.
        for name in sorted(dirs, key=lambda item: (-len(PurePosixPath(item).parts), item)):
            nodes.append(dict(path=name, snapshot=capture(f, self.root / name)))
        for pointer in (selected, selection['recovery']):
            if pointer is None:
                continue
            slot = h.slots.verify(pointer)
            name = 'runtime/slots/' + slot.slot
            nodes.append(dict(path=name, snapshot=capture(f, self.root / name), slot=pointer))
        recorder = _recorder(h)
        notice = recorder.current() if recorder is not None else None
        if notice is not None:
            source = recorder.executable(notice)
            nodes.append(dict(path=source.relative_to(self.root).as_posix(), snapshot=capture(f, source)))
        plan = dict(version=1, operation=operation, home=f.directory_identity(self.root),
                    selected=selection, target_sha256=target_hash, trust=receipt, records=states,
                    notice=notice, nodes=nodes)
        self._validate_paths(plan)
        return plan

    def preview(self, operation):
        require(not present(self._area(operation)), 'uninstall-operation-already-used')
        with self.f.exclusion(self.root / 'management.lock'), self.f.exclusion(self.home.slots.root / 'runtime.lock'):
            plan = self._snapshot(operation)
        return dict(state='uninstall-preview', operation=operation, receipt=_sha(canonical_bytes(plan)),
                    remove=[row['path'] for row in plan['nodes']], retained=['Work, records, backups, settings, project links and update trust'],
                    projects=len(plan['records']))

    def _validate_paths(self, plan):
        from .notice_app import APP, PARTS
        aliases = ('bin/colvia.exe', 'bin/colvia-manage.exe') if self.home.os_name == 'windows' else (
            'bin/colvia', 'bin/colvia-manage')
        files = {*aliases, 'entry.json'}
        recorded = {node['path']: node for node in plan['nodes']}
        require(len(recorded) == len(plan['nodes']), 'uninstall-intent-invalid')
        if 'receiver.json' in recorded:
            require(self.home.os_name == 'macos', 'uninstall-intent-invalid')
            files.update({'receiver.json', *('bin/' + APP + '/' + part for part in PARTS)})
        directories = {str(path) for name in files for path in PurePosixPath(name).parents if str(path) != '.'}
        pointers = {}
        for pointer in (plan['selected']['selected'], plan['selected']['recovery']):
            if pointer is None:
                continue
            _token(pointer['slot'])
            pointers['runtime/slots/' + pointer['slot']] = pointer
        if plan['notice'] is not None:
            require(self.home.os_name == 'windows' and re.fullmatch('[0-9a-f]{64}', plan['notice']),
                    'uninstall-intent-invalid')
            files.add('notification-tools/' + plan['notice'] + '.exe')
        require(set(recorded) == files | directories | set(pointers), 'uninstall-intent-invalid')
        for name, node in recorded.items():
            if name in pointers:
                require(node.get('slot') == pointers[name] and node['snapshot']['kind'] == 'directory',
                        'uninstall-intent-invalid')
            else:
                kind = 'directory' if name in directories else 'file'
                require('slot' not in node and node['snapshot']['kind'] == kind, 'uninstall-intent-invalid')

    def _record(self):
        raw = self.f.read(self.marker, LIMIT)
        marker = decode_canonical(raw)
        require(type(marker) is dict and set(marker) == {'version', 'operation', 'sha256'} and marker['version'] == 1,
                'uninstall-marker-invalid')
        area = self._area(marker['operation'])
        self.f.private_directory(area)
        intent = self.f.read(area / 'uninstall-intent.json', LIMIT)
        require(_sha(intent) == marker['sha256'], 'uninstall-intent-changed')
        value = decode_canonical(intent)
        plan = value['plan']
        require(plan['operation'] == marker['operation'] and plan['home'] == self.f.directory_identity(self.root) and
                value['retained'] == self.f.directory_identity(area / 'retired'), 'uninstall-intent-changed')
        self._validate_paths(plan)
        return raw, area, value

    def _position(self, area, node, index):
        old, held = self.root / node['path'], area / 'retired' / str(index)
        live = present(old)
        require(live != present(held), 'uninstall-file-position-unknown')
        path = old if live else held
        require(capture(self.f, path) == node['snapshot'], 'uninstall-owned-file-changed')
        if 'slot' in node:
            pointer = node['slot']
            verify_payload(path, pointer['slot'], pointer['manifest_sha256'], files=self.f,
                           os_name=self.home.os_name, architecture=self.home.architecture)
        return old if live else None

    def apply(self, operation, receipt, *, resume=False, checkpoint=lambda _: None):
        area = self._area(operation)
        with self.f.exclusion(self.root / 'management.lock'), self.f.exclusion(self.home.slots.root / 'runtime.lock'):
            if not present(self.marker):
                require(not resume, 'uninstall-operation-not-started')
                plan = self._snapshot(operation)
                require(_sha(canonical_bytes(plan)) == receipt, 'uninstall-review-changed')
                self.f.create_directory(area)
                self.f.create_directory(area / 'retired')
                record = canonical_bytes(dict(plan=plan, retained=self.f.directory_identity(area / 'retired')))
                self.f.create(area / 'uninstall-intent.json', record)
                self.f.create(self.marker, canonical_bytes(dict(version=1, operation=operation, sha256=_sha(record))))
                checkpoint('uninstall-intent')
            else:
                require(resume, 'uninstall-resume-required')
            marker, recorded_area, value = self._record()
            plan = value['plan']
            require(recorded_area == area and _sha(canonical_bytes(plan)) == receipt, 'uninstall-review-changed')
            require(not present(area / 'reinstall-intent.json'), 'uninstall-reinstall-pending')
            require(not present(area / 'restore-removal.json'), 'uninstall-restore-pending')
            require(self.home.slots.selection()[1] == plan['selected'] and self.home.requirements()[2] == plan['records'],
                    'uninstall-state-changed')
            locations = [self._position(area, node, index) for index, node in enumerate(plan['nodes'])]
            expected = {node['path'] for node, location in zip(plan['nodes'], locations)
                        if location is not None and node['path'].startswith('bin/')}
            require(self._bin_inventory(self.root) == expected, 'uninstall-extra-installed-file')
            recorder = _recorder(self.home)
            if recorder is not None:
                recorder.disable_for_uninstall(operation, plan['notice'])
            for index, node in enumerate(plan['nodes']):
                live = self._position(area, node, index)
                if live is not None:
                    checkpoint('uninstall-before-move')
                    require(self._position(area, node, index) == live, 'uninstall-state-changed')
                    move(self.f, live, area / 'retired' / str(index), node['snapshot'],
                         verified_tree='slot' in node)
                    checkpoint('uninstall-after-move')
            require(not any(self._position(area, node, index) is not None
                            for index, node in enumerate(plan['nodes'])), 'uninstall-not-complete')
            done = canonical_bytes(dict(version=1, intent_sha256=_sha(marker)))
            path = area / 'uninstall-complete.json'
            if present(path):
                require(self.f.read(path) == done, 'uninstall-completion-changed')
            else:
                self.f.create(path, done)
            return dict(state='removed', operation=operation, records_preserved=True)

    def restore(self, operation, receipt, *, checkpoint=lambda _: None):
        area = self._area(operation)
        with self.f.exclusion(self.root / 'management.lock'), self.f.exclusion(self.home.slots.root / 'runtime.lock'):
            marker, recorded_area, value = self._record()
            plan = value['plan']
            require(area == recorded_area and _sha(canonical_bytes(plan)) == receipt, 'uninstall-review-changed')
            require(not present(area / 'reinstall-intent.json'), 'uninstall-reinstall-pending')
            require(self.home.slots.selection()[1] == plan['selected'] and self.home.requirements()[2] == plan['records'],
                    'uninstall-state-changed')
            locations = [self._position(area, node, index) for index, node in enumerate(plan['nodes'])]
            live = {node['path'] for node, location in zip(plan['nodes'], locations)
                    if location is not None and node['path'].startswith('bin/')}
            require(self._bin_inventory(self.root) == live, 'uninstall-extra-installed-file')
            intent = area / 'restore-removal.json'
            if present(intent):
                require(self.f.read(intent) == marker, 'uninstall-restore-intent-changed')
            else:
                self.f.create(intent, marker)
            # Restore directories before their contents; unpublished paths never
            # appear in the receipt and are never overwritten.
            for index in reversed(range(len(plan['nodes']))):
                node = plan['nodes'][index]
                if self._position(area, node, index) is None:
                    checkpoint('uninstall-before-restore')
                    move(self.f, area / 'retired' / str(index), self.root / node['path'], node['snapshot'],
                         verified_tree='slot' in node)
                    checkpoint('uninstall-after-restore')
            require(all(self._position(area, node, index) is not None
                        for index, node in enumerate(plan['nodes'])), 'uninstall-restore-incomplete')
            recorder = _recorder(self.home)
            if recorder is not None:
                recorder.disable_for_uninstall(operation, plan['notice'])
            done = area / 'restore-removal-complete.json'
            if present(done):
                require(self.f.read(done) == marker, 'uninstall-restore-intent-changed')
            else:
                self.f.create(done, marker)
            self.f.remove(self.marker, marker)
            return dict(state='removal-restored', operation=operation, records_preserved=True,
                        windows_notifications_require_enable=plan['notice'] is not None)

    def check_reinstall(self):
        marker, area, value = self._record()
        require(not present(area / 'restore-removal.json'), 'uninstall-restore-pending')
        done = dict(version=1, intent_sha256=_sha(marker))
        require(present(area / 'uninstall-complete.json') and decode_canonical(self.f.read(area / 'uninstall-complete.json')) == done,
                'uninstall-not-complete')
        return marker, area, value['plan']

    def _removed_state(self, area, plan):
        require(self.home.slots.selection()[1] == plan['selected'] and self.home.requirements()[2] == plan['records'],
                'uninstall-state-changed')
        require(not any(self._position(area, node, index) is not None
                        for index, node in enumerate(plan['nodes'])), 'uninstall-not-complete')
        recorder = _recorder(self.home)
        if recorder is not None:
            require(recorder.current() is None, 'notice-registration-foreign')

    def prepare_reinstall(self, *, resume=False):
        """Choose a single attempt under management and runtime exclusion."""
        marker, area, plan = self.check_reinstall()
        binding = _sha(marker)
        claim = area / 'reinstall-intent.json'
        prior = None
        if present(claim):
            require(resume, 'uninstall-reinstall-resume-required')
            prior = self.f.read(claim)
            saved = decode_canonical(prior)
            _token(saved['operation'])
            require(re.fullmatch('reinstall-[0-9a-f]{32}', saved['operation']) and saved['binding'] == binding,
                    'uninstall-reinstall-intent-changed')
            old_area = self._area(saved['operation'])
            if present(old_area / 'release.json'):
                return binding, saved['operation'], True
            require(not present(old_area / 'publication.json') and
                    not present(self._area(saved['operation'] + '-activate')), 'uninstall-reinstall-unknown')
        else:
            require(not resume, 'uninstall-reinstall-not-started')
        # An explicitly requested resume may restart a lost download. All
        # earlier staged bytes/results remain in their original operation.
        self._removed_state(area, plan)
        operation = 'reinstall-' + uuid.uuid4().hex
        raw = canonical_bytes(dict(version=1, binding=binding, operation=operation))
        if prior is None:
            self.f.create(claim, raw)
        else:
            self.f.replace(claim, raw, prior)
        return binding, operation, False

    def reinstall_guard(self, binding, operation):
        marker, area, plan = self.check_reinstall()
        claim = canonical_bytes(dict(version=1, binding=binding, operation=operation))
        require(_sha(marker) == binding and self.f.read(area / 'reinstall-intent.json') == claim,
                'uninstall-reinstall-intent-changed')
        return marker, area, plan

    def verify_reinstall_download(self, binding, operation, download, verified):
        _, _, plan = self.reinstall_guard(binding, operation)
        high = plan['selected']['high_sequence']
        require(verified.sequence > high or (verified.sequence == high and
                verified.manifest_sha256 == plan['selected']['selected']['manifest_sha256'] and
                download['sha256'] == plan['target_sha256']), 'uninstall-reinstall-target-changed')
        require(all(download['versions'][role] >= version for role, version in plan['trust']['versions'].items()),
                'uninstall-reinstall-trust-regressed')

    def finish_reinstall(self, binding, operation):
        marker, area, _ = self.reinstall_guard(binding, operation)
        path = area / 'reinstall-complete.json'
        if present(path):
            require(self.f.read(path) == marker, 'uninstall-reinstall-completion-changed')
        else:
            self.f.create(path, marker)
        self.f.remove(self.marker, marker)
