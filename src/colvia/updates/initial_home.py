"""Publish a fully initialized home; preserve every interrupted staging attempt."""
from ..platforms.owned_install_files import present
from pathlib import Path
import hashlib,os,uuid
from ..codec import RecordError,canonical_bytes,decode_canonical,require
from ..management import ManagerHome
from ..storage.sqlite import _token
from .trust import Trust


def initial_intent(operation,target):
    return dict(version=1,operation=operation,target=target)


def initialize_home(root,*,os_name,architecture,files,config,anchor,payload_digest,fetcher,
                    checkpoint=lambda _:None,trust_type=Trust):
    root=Path(root);operation='install-'+uuid.uuid4().hex
    stage=root.with_name(root.name+'.initial-'+uuid.uuid4().hex)
    marker=None
    try:
        home=ManagerHome.create(stage,os_name=os_name,architecture=architecture,files=files)
        checkpoint('home-created')
        saved={k:config[k] for k in ('version','channel','metadata_url','target_url','target')}
        files.create(stage/'updates.json',canonical_bytes(saved));checkpoint('configuration-saved')
        marker=dict(version=1,operation=operation,final_root=str(root),identity=files.directory_identity(stage),
                    payload_sha256=payload_digest,config=saved,anchor_sha256=hashlib.sha256(anchor).hexdigest())
        files.create(stage/'initial-install.json',canonical_bytes(marker));checkpoint('identity-saved')
        area=stage/'operations'/operation;files.create_directory(area)
        files.create(area/'install-intent.json',canonical_bytes(initial_intent(operation,config['target'])))
        checkpoint('intent-saved')
        trust_type.initialize(stage/'trust',anchor=anchor,anchor_sha256=marker['anchor_sha256'],
            metadata_url=config['metadata_url'],target_url=config['target_url'],fetcher=fetcher,files=files)
        checkpoint('trust-initialized')
        files.publish_directory(stage,root,marker['identity']);checkpoint('home-published')
        # Never carry a path-bound staging object into the final installation.
        home=ManagerHome(root,os_name=os_name,architecture=architecture,files=files)
        trust=trust_type(root/'trust',metadata_url=config['metadata_url'],target_url=config['target_url'],fetcher=fetcher,files=files)
        return home,trust,operation
    except Exception as exc:
        exc.operation=operation
        # Classification is read-only; unknown identity never becomes adoption.
        try:
            if present(stage) and not present(root):exc.publication='unpublished'
            elif marker is not None and not present(stage) and files.directory_identity(root)==marker['identity']:exc.publication='published'
            else:exc.publication='unknown'
        except (OSError,ValueError,RecordError):exc.publication='unknown'
        raise


def initial_head(home,trust,config,anchor):
    f=home.files;marker=decode_canonical(f.read(home.root/'initial-install.json'))
    saved={k:config[k] for k in ('version','channel','metadata_url','target_url','target')}
    require(type(marker) is dict and set(marker)=={'version','operation','final_root','identity','payload_sha256','config','anchor_sha256'} and
            type(marker['version']) is int and marker['version']==1 and marker['final_root']==str(home.root) and
            marker['identity']==f.directory_identity(home.root) and marker['config']==saved,'initial-install-identity-changed')
    require(marker['anchor_sha256']==hashlib.sha256(anchor).hexdigest()==trust.state()[1]['anchor_sha256'],'initial-install-anchor-changed')
    operation=marker['operation'];seen=set()
    while True:
        _token(operation);require(operation not in seen and len(seen)<4096,'initial-attempt-chain-invalid');seen.add(operation)
        area=home.root/'operations'/operation;f.private_directory(area)
        require(decode_canonical(f.read(area/'install-intent.json'))==initial_intent(operation,config['target']),'installation-intent-changed')
        if not f.exists(area/'retried-by.json'):return operation
        link=decode_canonical(f.read(area/'retried-by.json'))
        require(type(link) is dict and set(link)=={'version','previous','next'} and link['version']==1 and link['previous']==operation,'initial-attempt-chain-invalid')
        _token(link['next'])
        require(decode_canonical(f.read(home.root/'operations'/link['next']/'retry-of.json'))==link,'initial-attempt-chain-invalid')
        operation=link['next']


def retry_claim(home,trust,config,anchor,*,previous,operation):
    # Caller owns management.lock throughout validation, claim and preparation.
    _token(previous);_token(operation);f=home.files
    require(initial_head(home,trust,config,anchor)==previous,'initial-attempt-not-current')
    require(not present(home.slots.root/'runtime.json') and not home.projects(),'initial-retry-already-active')
    for name in ('bin','entry.json','receiver.json','native-update.json','notice-app.pending','notice-choice.json','notice-registration.json','notice-registration.pending'):
        require(not present(home.root/name),'initial-retry-live-effects')
    old=home.root/'operations'/previous
    require(not f.exists(old/'completed.json'),'initial-retry-already-completed')
    quarantined=f.exists(old/'quarantine-intent.json')
    if quarantined:
        from .initial_quarantine import completed
        require(f.exists(old/'quarantine-complete.json'),'initial-quarantine-incomplete')
        require(completed(home,previous)['successor']==operation,'initial-quarantine-successor-mismatch')
    # A prepared-but-unpublished attempt may be superseded explicitly. All live
    # paths above must still be absent; old preparations/signatures are retained.
    area=home.root/'operations'/operation
    if quarantined and present(area):
        f.private_directory(area)
        require({p.name for p in area.iterdir()}<= {'retry-of.json','install-intent.json'},'initial-retry-area-changed')
    else:f.create_directory(area)
    link=dict(version=1,previous=previous,next=operation)
    for name,value in (('retry-of.json',link),('install-intent.json',initial_intent(operation,config['target']))):
        raw=canonical_bytes(value)
        if f.exists(area/name):require(f.read(area/name)==raw,'initial-retry-area-changed')
        else:f.create(area/name,raw)
    # Unlinked orphan preparation has no effects and remains evidence. Publishing
    # this no-replace edge is the only claim; a previous attempt cannot fork.
    f.create(old/'retried-by.json',canonical_bytes(link))
