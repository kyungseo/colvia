"""Resolve removable account files from installation, backup and connection receipts.

No account-wide recursive deletion. Unknown files and unclaimed directories block
the transition before the account is retired.
"""
from contextlib import closing
import hashlib
import os
import re
import stat
import sqlite3
from pathlib import Path
from ..codec import decode_canonical, require
from ..maps import scan_map
from ..platforms.owned_install_files import _info, present
from ..records import application_registry, link
from ..tree import logical_path
from .initial_files import InitialFiles
from .installation import configuration
from .uninstall import LIMIT


def fingerprint(files, path, expected=None):
    if expected and expected.get('cache_directory'):
        # TUF creates root_history with the parent metadata directory's
        # owner-only inheritable ACE. Verify its effective owner and every ACE.
        api = files.api
        with api.ancestors(path), api.opened(path) as h:
            state = api.state(h,path)
            require(state['directory'], 'purge-root-cache-changed')
            api.private(h)
            return dict(kind='directory', identity=list(state['identity']), cache_directory=True)
    kind = (expected or {}).get('kind')
    if kind == 'root-cache-symlink':
        st = path.lstat()
        files.private_directory(path.parent)
        require(stat.S_ISLNK(st.st_mode) and st.st_uid == os.getuid() and st.st_nlink == 1,
                'purge-root-alias-changed')
        return dict(kind=kind, identity=[st.st_dev,st.st_ino,getattr(st,'st_birthtime_ns',round(st.st_birthtime*1000000000))],
                    target=os.readlink(path))
    if kind == 'root-cache-file':
        api = files.api
        with api.ancestors(path), api.opened(path,access=0x80020000,share=1) as h:
            state = api.state(h,path)
            api.private(h)
            require(not state['directory'] and state['links'] in (1,2) and state['size'] <= 512*1024,
                    'purge-root-alias-changed')
            with files._stream_handle(h) as stream:
                digest = hashlib.file_digest(stream,'sha256').hexdigest()
            require(api.state(h,path)==state,'purge-root-alias-changed')
            return dict(kind=kind,identity=list(state['identity']),sha256=digest)
    node = _info(files, path)
    if node['kind'] == 'directory':
        return node
    size = path.lstat().st_size
    if size == 0:
        # Windows runtime locks permit shared metadata handles but not a second
        # deny-write content handle while this process owns the writer lock.
        require(_info(files, path) == node and path.lstat().st_size == 0, 'purge-file-changed')
        return dict(node, sha256=hashlib.sha256(b'').hexdigest())
    with files.read_stream(path, size) as stream:
        digest = hashlib.file_digest(stream, 'sha256').hexdigest()
    require(_info(files, path) == node, 'purge-file-changed')
    return dict(node, sha256=digest)


def inventory(home):
    files, root = home.files, home.root
    allowed = {}

    def claim(path, digest=None, *, kind=None):
        name = path.relative_to(root).as_posix()
        require(logical_path(name) == name, 'purge-invalid-account-path')
        node = fingerprint(files, path, dict(kind=kind))
        if digest is not None:
            require(node.get('sha256') == digest, 'purge-owned-file-changed')
        allowed[name] = node
        for ancestor in path.parents:
            if ancestor == root:
                break
            key = ancestor.relative_to(root).as_posix()
            if key not in allowed:
                hint = None
                if hasattr(files,'api') and ancestor == root/'trust/metadata/root_history':
                    files.private_directory(ancestor.parent)
                    hint = dict(cache_directory=True)
                allowed[key] = fingerprint(files, ancestor, hint)

    def record(path):
        value = decode_canonical(files.read(path, LIMIT))
        require(isinstance(value, dict), 'purge-invalid-account-record')
        claim(path)
        return value

    def known_regular(path, content):
        claim(path, hashlib.sha256(content).hexdigest())

    for name in ('authorities', 'operations', 'backups', 'runtime/slots'):
        claim(root / name)
    for name in ('home.json','updates.json','trust/state.json','runtime/runtime.json'):
        record(root / name)
    for name in ('management.lock', 'runtime/runtime.lock'):
        known_regular(root / name, b'')
    for name in ('tools.json', 'notice-registration.json'):
        if present(root / name):
            record(root / name)
    if present(root/'initial-install.json'):
        initial = record(root/'initial-install.json')
        require(initial['final_root'] == str(root) and
                initial['identity'] == files.directory_identity(root), 'purge-initial-home-changed')
    if present(root/'notice-choice.json'):
        from ..platforms.darwin_notices import DarwinNotices
        DarwinNotices(home).choice()
        claim(root/'notice-choice.json')
    if present(root/'notice-events'):
        from ..notice_routes import NoticeRoutes
        routes = NoticeRoutes(home)
        claim(routes.root)
        for path in routes.root.iterdir():
            require(path.suffix == '.json', 'purge-notice-route-changed')
            routes.read(path.stem)
            claim(path)
    metadata = root/'trust/metadata'
    if present(metadata):
        from .trust import Trust
        from ..manager_entry import update_configuration
        cfg = update_configuration(home)
        trust = Trust(root/'trust', metadata_url=cfg['metadata_url'], target_url=cfg['target_url'],
                      fetcher=object(),files=files)
        _, state = trust.state()
        versions = state['versions']
        hashes = trust.metadata_digests(versions)
        known_regular(root/'trust/update.lock', b'')
        for role in ('timestamp','snapshot','targets'):
            claim(metadata/(role+'.json'),hashes[role])
        alias = metadata/'root.json'
        for path in (metadata/'root_history').iterdir():
            require(re.fullmatch(r'[1-9][0-9]*\.root\.json',path.name), 'purge-root-history-changed')
            version = int(path.name.split('.')[0])
            require(version <= versions['root'], 'purge-root-history-changed')
            raw = trust._read_root_history(version,current=versions['root'])
            current = version == versions['root']
            kind = 'root-cache-file' if current and hasattr(files,'api') else None
            claim(path, hashlib.sha256(raw).hexdigest(), kind=kind)
            if current:
                if alias.is_symlink() and not hasattr(files,'api'):
                    claim(alias, kind='root-cache-symlink')
                else:
                    claim(alias, hashes['root'], kind=kind)
    selection = home.slots.selection()[1]
    pointers = {p['slot']:p for p in (selection['selected'], selection['recovery']) if p}
    projects = home.projects()
    for project in projects:
        authority = home.authority(project)
        base = authority.root
        pointer = authority.pointer_value()
        record(base / 'active.json')
        claim(base / 'stores' / pointer['generation'] / 'state.sqlite3')
        for name in ('lifecycle.lock','effect.lock','detach.lock'):
            if present(base / name):
                known_regular(base / name, b'')
        claim(base / 'lifecycle')
        if present(base / 'last-export.json'):
            record(base / 'last-export.json')
        with closing(authority.store(readonly=True)) as store:
            registry = application_registry()
            for key, ref in scan_map(store.root().heads, store.load):
                if not key.startswith(('connect:', 'detach:')):
                    continue
                state = registry.inspect(ref, store.load(ref), required=True)
                plan_ref = link(state, 'plan')
                plan = registry.inspect(plan_ref, store.load(plan_ref), required=True)
                for step in plan.payload['manifest']['steps']:
                    native = step['native']
                    stage = base / 'effects' / native['application']
                    claim(stage)
                    for item in native['items']:
                        for name, content in (('evacuated_name','pre'), ('post_name','post')):
                            path = stage / item[name]
                            if present(path):
                                require(item[content] is not None, 'purge-unclaimed-effect')
                                claim(path, item[content]['sha256'])
    for area in sorted((root / 'operations').iterdir()):
        files.private_directory(area)
        first = area / 'prepared.json'
        release = area / 'release.json'
        if present(release) or present(first):
            rec = record(release if present(release) else first)
            if 'download' in rec:
                pointer = rec['target']
                pointers[pointer['slot']] = pointer
                if rec['download'].get('staged') is not None:
                    claim(area / 'release.zip', rec['download']['sha256'])
            if present(first):
                prepared = record(first)
                if 'effects' in prepared:
                    effect = prepared['effects']
                    op = effect['application']
                    require(area.name in (op+'-entry', op+'-notice-app') and
                            logical_path(op) == op and '/' not in op, 'purge-operation-changed')
                    complete = record(area/'completed.json')
                    require(complete['target'] == prepared['target'], 'purge-operation-changed')
                    known_regular(area/'effect.lock', b'')
                    stage = area/'effects'/op
                    claim(stage)
                    for index, item in enumerate(effect['items']):
                        for suffix, key, state in (('original','evacuated_name','pre'),('post','post_name','post')):
                            name = f'{index:06d}.{suffix}'
                            require(item[key] == name, 'purge-effect-path-changed')
                            path = stage/name
                            if present(path):
                                require(item[state] is not None, 'purge-unclaimed-effect')
                                claim(path, item[state]['sha256'])
                for backup in prepared.get('backups', []):
                    destination = Path(backup['destination'])
                    require(destination.parent == root/'backups'/area.name and
                            destination.name in {p+'.colvia-export' for p in projects},
                            'purge-backup-path-changed')
                    with files.read_stream(destination, backup['bytes']) as stream:
                        from ..backup import ExportBudget, ExportReader
                        reader = ExportReader(stream, ExportBudget(backup['manifest']['objects'], backup['bytes']))
                        for _ in reader.objects():
                            pass
                        require(reader.manifest == backup['manifest'], 'purge-backup-changed')
                    claim(destination)
                    project = destination.stem
                    audit = area/project/(area.name+'-'+project+'-audit.sqlite3')
                    if present(audit):
                        before = fingerprint(files, audit)
                        with closing(sqlite3.connect(audit.as_uri()+'?mode=ro&immutable=1',uri=True)) as db:
                            db.execute('PRAGMA trusted_schema=OFF')
                            tables = {r[0] for r in db.execute("SELECT name FROM sqlite_schema WHERE type='table'")}
                            require(tables in ({'nodes','edges','ready'}, {'nodes','edges','ready','map_checks'}) and
                                    db.execute('SELECT count(*) FROM nodes').fetchone()[0] == backup['manifest']['objects']
                                    and db.execute('SELECT 1 FROM nodes WHERE digest=? AND kind=?',
                                                   (backup['root']['sha256'], 'state.root')).fetchone(),
                                    'purge-backup-audit-changed')
                        claim(audit, before['sha256'])
                if present(root/'backups'/area.name) and 'backups' in prepared:
                    claim(root/'backups'/area.name)
                for p in projects:
                    if present(area/p) and 'backups' in prepared:
                        claim(area/p)
            for n in ('started.json','completed.json','install-intent.json','download-intent.json','intent.json','publication.json'):
                path = area/n
                if present(path):
                    info = record(path)
                    if n == 'publication.json':
                        stage = area/info['stage']
                        require(stage.parent == area and files.directory_identity(stage) == info['stage_identity'],
                                'purge-publication-changed')
                        claim(stage)
        for name in ('connect.json', 'detach.json'):
            path = area/name
            if present(path):
                info = record(path)
                require(info['operation'] == area.name, 'purge-operation-changed')
        if area.name.startswith('notice-') and present(area/'intent.json'):
            receipt = record(area/'intent.json')
            require(receipt['operation'] == area.name, 'purge-notice-changed')
            record(area/'completed.json')
    receiver_hashes = set()
    for pointer in pointers.values():
        slot = home.slots.verify(pointer)
        folder = home.slots.root/'slots'/slot.slot
        manifest = record(folder/'manifest.json')
        for item in manifest['inventory']:
            if item['path'] in ('native/colvia-notice.exe', 'native/colvia.exe'):
                receiver_hashes.add(item['sha256'])
            claim(folder/item['path'], item['sha256'])
        if pointer == selection['selected']:
            config = configuration(files, folder)
            native = files.read(folder/config['native_entry'], 64*1024*1024)
            _, entries = InitialFiles(home, slot.slot, pointer, native).expected()
            for name, (content, _) in entries.items():
                known_regular(root/name, content)
    tools = root/'notification-tools'
    if present(tools):
        claim(tools)
        for path in tools.iterdir():
            require(path.suffix == '.exe' and path.stem in receiver_hashes, 'purge-unclaimed-notice-tool')
            claim(path, path.stem)
    return allowed


def check_tree(root, files, approved, *, partial=False):
    remaining = {}
    def visit(directory):
        for path in directory.iterdir():
            name = path.relative_to(root).as_posix()
            require(name in approved, 'purge-unclaimed-account-item')
            node = fingerprint(files, path, approved[name])
            require(node == approved[name], 'purge-account-item-changed')
            remaining[name] = node
            if node['kind'] == 'directory':
                visit(path)
    visit(root)
    require(partial or remaining == approved, 'purge-account-item-missing')
    return remaining
