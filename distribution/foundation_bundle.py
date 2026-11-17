"""Prepare an unsigned normalized release bundle, without installation/signing.

Inputs are explicit normalized runtime and verifier trees, native entry, trust
anchor and public-guide mapping. Upstream archive interpretation, entitlement and
release trust are separate steps. The output is not a publicly qualified asset.
"""
from pathlib import Path
import hashlib,os,stat,zipfile
from colvia.codec import canonical_bytes,require
from colvia.tree import canonical_entries
from colvia.worker_state import path_namespace
from colvia.updates.bootstrap import inspect_bundle
from colvia.updates.package import _portable
from colvia.updates.slots import supported_python_version
from colvia.storage.sqlite import runtime_capabilities,_token


GUIDE_PAGES=('overview','install','tutorial','work','git','records','maintenance','architecture','reference')


def guide_sources(source):
    """Map foundation guides to installed destinations; never reuse the legacy index."""
    source=Path(source)
    return {'README.md':source/'distribution/foundation-guides/README.md',
            'manual/en/README.md':source/'distribution/foundation-guides/en.md',
            'manual/ko/README.md':source/'distribution/foundation-guides/ko.md',
            **{f'manual/{language}/{page}.md':source/'manual'/language/f'{page}.md'
               for language in ('en','ko') for page in GUIDE_PAGES}}


def wrapper(module):
    require(module in ('managed_entry','manager_entry'),'bundle-wrapper-module')
    return ("# Colvia dedicated-runtime entry; invoked with -I -B.\n"
            "from pathlib import Path\nimport sys\n"
            "# Keep redirected output independent of the host ANSI code page.\n"
            "sys.stdout.reconfigure(encoding='utf-8', errors=sys.stdout.errors)\n"
            "sys.stderr.reconfigure(encoding='utf-8', errors=sys.stderr.errors)\n"
            "sys.path.insert(0,str(Path(__file__).absolute().parent/'lib'))\n"
            f"from colvia.{module} import main\n"
            "if __name__=='__main__':raise SystemExit(main())\n").encode()


def _identity(path):
    info=path.lstat()
    require(stat.S_ISREG(info.st_mode) and info.st_nlink==1,'bundle-input-not-regular')
    return info.st_dev,info.st_ino,info.st_size,info.st_mtime_ns,info.st_ctime_ns,info.st_mode


def assemble(*,source,runtime,verifier,native_entry,anchor,configuration,guides,licenses,output,
             release,sequence,os_name,architecture,python_entry,python_version,sqlite_version,notice_app=None,document_assets=False):
    source,runtime,verifier,native_entry,anchor,output=map(Path,(source,runtime,verifier,native_entry,anchor,output))
    _token(release);require(type(sequence) is int and sequence>0,'bundle-sequence-invalid')
    require((os_name,architecture) in (('macos','arm64'),('windows','arm64'),('windows','x64')),'bundle-platform-unavailable')
    require(supported_python_version(os_name,architecture,python_version),'bundle-python-version')
    require(output.is_absolute() and output.parent.is_dir() and not os.path.lexists(output),'bundle-new-output-required')
    require(type(guides) is dict and {'manual/en/README.md','manual/ko/README.md'}<=set(guides),'bundle-guides-required')
    require(type(licenses) is dict and {'LICENSE','THIRD_PARTY_NOTICES.md'}<=set(licenses),'bundle-notices-required')
    require(type(configuration) is dict and set(configuration)=={'channel','metadata_url','target_url','target'},'bundle-update-configuration')
    from colvia.updates.trust import _url,_target
    _token(configuration['channel']);_target(configuration['target'])
    require(all(_url(configuration[k])==configuration[k] for k in ('metadata_url','target_url')),'bundle-update-origin')
    require(type(document_assets) is bool,'bundle-document-option')
    require(not document_assets or (os_name,architecture)==('macos','arm64'),'bundle-document-platform')
    inputs={};generated={};identities={};captured={}
    def add(name,path,*,execution_asset=False):
        name=_portable(name);path=Path(path)
        require(execution_asset or not (name.casefold()=='execution' or name.casefold().startswith('execution/')),'bundle-execution-namespace')
        require(name not in inputs and name not in generated,'bundle-path-collision')
        require(path.is_absolute(),'bundle-input-absolute-required')
        for parent in (path,*path.parents):require(not parent.is_symlink(),'bundle-input-symlink')
        identities[name]=_identity(path);inputs[name]=path
    def tree(root,prefix,*,python_only=False):
        require(root.is_absolute() and root.is_dir() and not root.is_symlink(),'bundle-tree-required')
        require(output!=root and root not in output.parents,'bundle-output-inside-input')
        for path in sorted(root.rglob('*')):
            relative=path.relative_to(root)
            # Interpreter-created cache is not a release input.
            if '__pycache__' in relative.parts:continue
            require(not path.is_symlink(),'bundle-input-symlink')
            if path.is_dir():continue
            if python_only and path.suffix!='.py':continue
            add(prefix+'/'+relative.as_posix(),path)
    tree(source/'src/colvia','lib/colvia',python_only=True)
    tree(runtime,'runtime');tree(verifier,'lib')
    add('adapters/colvia-work/SKILL.md',source/'adapters/foundation-work/SKILL.md')
    executable='native/colvia.exe' if os_name=='windows' else 'native/colvia'
    add(executable,native_entry);add('trust/root.json',anchor)
    if notice_app is not None:
        from colvia.updates.notice_app import PARTS,PREFIX
        require(os_name=='macos','bundle-notice-platform')
        notice_app=Path(notice_app);found={p.relative_to(notice_app).as_posix() for p in notice_app.rglob('*') if not p.is_dir()}
        require(found==set(PARTS),'bundle-notice-inventory')
        for part in PARTS:add(PREFIX+part,notice_app/part)
    for name,path in {**guides,**licenses}.items():add(name,path)
    require(not set(guides)&set(licenses),'bundle-path-collision')
    generated.update({'manager.py':wrapper('manager_entry'),'product.py':wrapper('managed_entry'),
        'installation.json':canonical_bytes(dict(version=1,**configuration,anchor='trust/root.json',native_entry=executable))})
    worker_members={}
    if document_assets:
        from distribution.document_worker import MEMBERS,archive_bytes
        from colvia.execution.assets import ASSETS,DESCRIPTOR
        def capture(name,limit):
            path=inputs[name];require(identities[name][2]<=limit,'bundle-capture-limit')
            with path.open('rb') as stream:raw=stream.read(limit+1)
            require(_identity(path)==identities[name] and len(raw)==identities[name][2] and len(raw)<=limit,'bundle-input-changed')
            captured[name]=(path,hashlib.sha256(raw).hexdigest());return raw
        worker_members={name:capture('lib/'+name,1048576) for name in MEMBERS}
        generated[ASSETS['worker'][0]]=archive_bytes(worker_members)
        for role,source_name in (('parser','marked.umd.js'),('parser_license','marked-LICENSE.md'),('profile','worker.sb.in'),('runtime_profile','official-codex-macos.sb')):
            name,limit=ASSETS[role];add(name,source/'runtime/official'/source_name,execution_asset=True)
            raw=capture(name,limit)
            require(identities[name][-1]&0o111==0,'bundle-document-mode')
        # Preserve the exact reviewed template, including necessary OS paths.
        # Installation-specific substitutions belong to the future supervisor.
        profile=capture(ASSETS['profile'][0],ASSETS['profile'][1]).decode('utf-8')
        for raw_profile in (profile,capture(ASSETS['runtime_profile'][0],ASSETS['runtime_profile'][1]).decode('utf-8')):
            require('/Users/' not in raw_profile and '/home/' not in raw_profile and str(source) not in raw_profile,'bundle-profile-private-path')
        for marker in ('@@ANCESTOR_METADATA_LITERALS@@','@@APPROVED_INPUT_READ_LITERALS@@','@@EXACT_WRITE_TARGET_AND_SWAP@@'):
            require(profile.count(marker)==1,'bundle-profile-template')
        notice=capture('THIRD_PARTY_NOTICES.md',1048576)
        generated['THIRD_PARTY_NOTICES.md']=notice+b'\nDocument Markdown parser attribution: execution/marked-LICENSE.md (bundled marked JavaScript library).\n'
        del inputs['THIRD_PARTY_NOTICES.md']
        resources={}
        for role,(name,limit) in ASSETS.items():
            raw=generated[name] if name in generated else capture(name,limit)
            require(0<len(raw)<=limit,'bundle-document-size')
            resources[role]=dict(path=name,size=len(raw),sha256=hashlib.sha256(raw).hexdigest(),mode='100644')
        generated[DESCRIPTOR]=canonical_bytes(dict(version=1,os=os_name,architecture=architecture,resources=resources))
    require(not set(generated)&set(inputs),'bundle-path-collision')
    names=sorted(set(inputs)|set(generated));path_namespace(names)
    require(len(names)<=100000 and 'runtime/'+_portable(python_entry) in inputs,'bundle-python-entry-missing')
    inventory=[];total=0
    for name in names:
        h=hashlib.sha256();size=0
        if name in generated:raw=generated[name];h.update(raw);size=len(raw);mode='100644'
        else:
            path=inputs[name]
            with path.open('rb') as stream:
                while raw:=stream.read(1024*1024):h.update(raw);size+=len(raw);require(size<=1024**3,'bundle-file-limit')
            require(_identity(path)==identities[name] and size==identities[name][2],'bundle-input-changed')
            mode='100755' if identities[name][-1]&0o111 else '100644'
        if name in (executable,'runtime/'+python_entry):require(mode=='100755','bundle-executable-required')
        total+=size;require(total<=4*1024**3,'bundle-size-limit')
        inventory.append(dict(path=name,kind='regular',size=size,sha256=h.hexdigest(),mode=mode))
    indexed_inputs={row['path']:row for row in inventory}
    for name,raw in worker_members.items():require(indexed_inputs['lib/'+name]['sha256']==hashlib.sha256(raw).hexdigest(),'bundle-worker-source-drift')
    for name,(path,digest) in captured.items():require(_identity(path)==identities[name] and hashlib.sha256(path.read_bytes()).hexdigest()==digest,'bundle-input-changed')
    caps=sorted(runtime_capabilities());manifest=canonical_bytes(dict(version=1,release=release,sequence=sequence,os=os_name,architecture=architecture,
        python='runtime/'+python_entry,python_version=python_version,sqlite_version=sqlite_version,
        manager='manager.py',product='product.py',read_capabilities=caps,write_capabilities=caps,features=sorted(['official-execution','managed-uninstall']+(['native-notices'] if notice_app is not None or os_name=='windows' else [])),inventory=canonical_entries(inventory)))
    require(len(manifest)<=4*1024**2,'bundle-manifest-limit')
    generated['manifest.json']=manifest;indexed={e['path']:e for e in inventory}
    # Preserve incomplete output on any failure for diagnosis; never publish an
    # asset URL or signing metadata from a partially prepared ZIP.
    with output.open('xb') as destination:
        with zipfile.ZipFile(destination,'w',compression=zipfile.ZIP_DEFLATED) as archive:
            for name in sorted(set(inputs)|set(generated)):
                item=zipfile.ZipInfo(name,(1980,1,1,0,0,0));item.compress_type=zipfile.ZIP_DEFLATED
                mode=0o755 if name in indexed and indexed[name]['mode']=='100755' else 0o644
                item.external_attr=(stat.S_IFREG|mode)<<16;item.file_size=len(generated[name]) if name in generated else indexed[name]['size']
                h=hashlib.sha256();size=0
                with archive.open(item,'w') as target:
                    if name in generated:raw=generated[name];target.write(raw);h.update(raw);size=len(raw)
                    else:
                        with inputs[name].open('rb') as stream:
                            while raw:=stream.read(1024*1024):target.write(raw);h.update(raw);size+=len(raw)
                if name in indexed:require(size==indexed[name]['size'] and h.hexdigest()==indexed[name]['sha256'],'bundle-input-changed')
                if name in inputs:require(_identity(inputs[name])==identities[name],'bundle-input-changed')
        destination.flush();os.fsync(destination.fileno())
    for name,(path,digest) in captured.items():require(_identity(path)==identities[name] and hashlib.sha256(path.read_bytes()).hexdigest()==digest,'bundle-input-changed')
    bundle=inspect_bundle(output)
    return dict(state='prepared-unsigned',length=bundle.length,sha256=bundle.sha256,manifest_sha256=bundle.manifest_sha256,
                os=os_name,architecture=architecture,entries=len(inventory),runtime_execution_verified=False)
