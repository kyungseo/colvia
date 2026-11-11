"""Build the fixed document worker and its complete product-module dependency set.

Packaging tool only. No runtime, project connection or installation is selected.
The execution contract hashes this complete archive, not one member script.
"""
import ast,hashlib,importlib.util,io,json,os,stat,zipfile
from pathlib import Path

MEMBERS=('colvia/__init__.py','colvia/codec.py','colvia/platforms/__init__.py',
         'colvia/platforms/exclusive.py','colvia/platforms/darwin_document_worker.py')
MAIN=b'from colvia.platforms.darwin_document_worker import main\nraise SystemExit(main())\n'

def source_bytes(path):
    fd=os.open(path,os.O_RDONLY|os.O_NOFOLLOW|os.O_NONBLOCK)
    try:
        before=os.fstat(fd)
        if not stat.S_ISREG(before.st_mode) or before.st_nlink!=1 or before.st_size>1048576:raise ValueError('worker source shape')
        with os.fdopen(os.dup(fd),'rb') as stream:raw=stream.read(1048577)
        signature=lambda s:(s.st_dev,s.st_ino,s.st_mode,s.st_nlink,s.st_size,s.st_mtime_ns,s.st_ctime_ns)
        if len(raw)!=before.st_size or signature(before)!=signature(os.fstat(fd)) or signature(before)!=signature(os.stat(path,follow_symlinks=False)):
            raise ValueError('worker source changed')
        raw.decode('utf-8');return raw
    finally:os.close(fd)

def archive_bytes(files):
    """Fixed members, fixed builder Python: no reads or execution in this function."""
    if set(files)!=set(MEMBERS) or any(type(raw) is not bytes for raw in files.values()):raise ValueError('worker member set')
    files=dict(files)
    trees={name:ast.parse(raw,filename=name) for name,raw in files.items()}
    modules={name[:-3].replace('/','.') for name in MEMBERS}
    packages={name[:-12].replace('/','.'):trees[name] for name in MEMBERS if name.endswith('/__init__.py')}
    modules|=packages.keys()
    def bound_names(tree):
        names=set()
        for node in tree.body:
            if isinstance(node,(ast.FunctionDef,ast.AsyncFunctionDef,ast.ClassDef)):names.add(node.name)
            elif isinstance(node,(ast.Import,ast.ImportFrom)):
                names.update(alias.asname or alias.name.split('.')[0] for alias in node.names)
            elif isinstance(node,(ast.Assign,ast.AnnAssign)):
                targets=node.targets if isinstance(node,ast.Assign) else [node.target]
                def assigned(target):
                    if isinstance(target,ast.Name):return {target.id}
                    if isinstance(target,(ast.Tuple,ast.List)):return set().union(*(assigned(v) for v in target.elts))
                    if isinstance(target,ast.Starred):return assigned(target.value)
                    return set()
                names.update(set().union(*(assigned(target) for target in targets)))
        return names
    bindings={name:bound_names(tree) for name,tree in packages.items()}
    for name,tree in trees.items():
        module=name[:-3].replace('/','.');package=module.rsplit('.',1)[0]
        for node in ast.walk(tree):
            targets=[]
            if isinstance(node,ast.Import):targets=[alias.name for alias in node.names]
            elif isinstance(node,ast.ImportFrom):
                try:base=importlib.util.resolve_name('.'*node.level+(node.module or ''),package) if node.level else node.module
                except ImportError as exc:raise ValueError('worker dependency missing') from exc
                targets=[base]
                if base in packages:
                    for alias in node.names:
                        if base+'.'+alias.name not in modules and alias.name not in bindings[base]:
                            raise ValueError('worker dependency missing')
            for target in targets:
                if target and (target=='colvia' or target.startswith('colvia.')) and target not in modules:raise ValueError('worker dependency missing')
    files['__main__.py']=MAIN
    manifest=dict(version=1,files={name:hashlib.sha256(raw).hexdigest() for name,raw in sorted(files.items())})
    files['bundle-manifest.json']=(json.dumps(manifest,sort_keys=True,separators=(',',':'))+'\n').encode()
    buffer=io.BytesIO()
    with zipfile.ZipFile(buffer,'w',compression=zipfile.ZIP_STORED) as archive:
        for name,raw in sorted(files.items()):
            item=zipfile.ZipInfo(name,date_time=(1980,1,1,0,0,0));item.create_system=3;item.external_attr=(stat.S_IFREG|0o644)<<16
            archive.writestr(item,raw)
    return buffer.getvalue()


def build(source_root,output):
    source_root=Path(source_root);output=Path(output)
    files={name:source_bytes(source_root/name) for name in MEMBERS}
    raw=archive_bytes(files)
    # Recheck every input before publishing a new artifact. Never overwrite.
    if any(source_bytes(source_root/name)!=files[name] for name in MEMBERS):raise ValueError('worker source changed')
    with output.open('xb') as stream:stream.write(raw);stream.flush();os.fsync(stream.fileno())
    return dict(sha256=hashlib.sha256(raw).hexdigest(),size=len(raw),
        members={name:hashlib.sha256(body).hexdigest() for name,body in {**files,'__main__.py':MAIN}.items()})
