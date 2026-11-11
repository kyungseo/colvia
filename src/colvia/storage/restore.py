"""Bounded transfer into an unpublished generation; never replace a live DB."""
from ..codec import ObjectRef, RecordError, require, decode_envelope
from ..maps import map_get, scan_map
from .sqlite import _token


def fill_candidate(store, snapshot, *, operation, unselected,
                   cancelled=lambda:False, checkpoint=lambda _:None):
    _token(operation)
    require(snapshot.complete and snapshot.writable, 'import-not-writable')
    root=ObjectRef.parse(snapshot.header['root'])
    require(snapshot.header['project']==store.project,'import-project-mismatch')
    require(set(snapshot.header['read_requirements'])<=store.reader_capabilities and
            set(snapshot.header['write_requirements'])<=store.writer_capabilities,
            'import-capability-unavailable')
    marker='restore-'+operation
    _token(marker)
    def guard():
        unselected()
        require(not cancelled(),'import-cancelled')
    guard()
    with store._transaction(write=True,lifecycle=True):
        guard()
        require(store._root().sequence==0 and
                store.db.execute('SELECT count(*) FROM objects').fetchone()[0]==2 and
                all(store.db.execute('SELECT count(*) FROM '+name).fetchone()[0]==0
                    for name in ('imports','claims','operations','restore_origin')),
                'restore-target-not-fresh')
        row=store.db.execute('SELECT fence,quiescent FROM generation').fetchone()
        require(row['fence'] is None and row['quiescent'] is None,'restore-target-not-fresh')
        store.db.execute('INSERT INTO restore_origin VALUES(1,?,?,?,0)',
                         (operation,root.sha256,snapshot.manifest['sha256']))
        store.db.execute('UPDATE generation SET quiescent=?',(marker,))
    checkpoint('claimed')
    def owned():
        guard()
        row=store.db.execute('SELECT * FROM restore_origin').fetchone()
        state=store.db.execute('SELECT fence,quiescent FROM generation').fetchone()
        require(row is not None and row['operation']==operation and row['complete']==0 and
                state['fence'] is None and state['quiescent']==marker,'restore-target-diverged')
    def flush(batch):
        with store._transaction(write=True,lifecycle=True):
            owned()
            for ref,raw in batch: store._put(ref,raw,published=True)
        checkpoint('object-batch')
    batch=[];size=count=0
    for ref,raw in snapshot.objects():
        guard()
        if batch and (len(batch)>=64 or size+len(raw)>4*1024*1024):
            flush(batch);batch=[];size=0
        batch.append((ref,raw));size+=len(raw);count+=1
    if batch:flush(batch)
    require(count==snapshot.audit.count,'restore-object-count-mismatch')
    # Rebuild the disposable operation index from retained lineage, not archive IDs.
    current=store._decode_root(root,store.load)
    require(current.sequence<=1_000_000,'restore-history-limit')
    cursor=current;rows=[];operation_count=0
    def index_batch(rows):
        with store._transaction(write=True,lifecycle=True):
            owned()
            store.db.executemany('INSERT INTO operations VALUES(?,?,?)',rows)
        checkpoint('index-batch')
    while cursor.sequence:
        guard()
        env=decode_envelope(cursor.ref,store.load(cursor.ref))
        previous=store._decode_root(env.edges[2].ref,store.load)
        require(previous.sequence+1==cursor.sequence,'invalid-root-lineage')
        op=env.payload['operation']
        require(map_get(current.operations,op,store.load)==previous.ref,'operation-index-mismatch')
        rows.append((op,previous.ref.sha256,cursor.ref.sha256));operation_count+=1
        if len(rows)>=64:index_batch(rows);rows=[]
        cursor=previous
    if rows:index_batch(rows)
    require(sum(1 for _ in scan_map(current.operations,store.load))==operation_count,
            'operation-index-mismatch')
    checkpoint('objects-copied')
    from ..graph import GraphAudit
    from ..backup import audit_requirements
    audit_path=store.path.parent/'restore-readback.sqlite3'
    audit=GraphAudit(audit_path,snapshot.audit.budget)
    info=audit_path.lstat()
    try:
        audit.run(root,store.load,snapshot.registry,cancelled=cancelled,require_known=True)
        require(audit.count==snapshot.audit.count and audit_requirements(audit)==
                {key:snapshot.header[key] for key in ('read_requirements','write_requirements')},
                'restore-readback-mismatch')
    finally:audit.close()
    # The completed read-back index is reproducible scratch, not authority.
    current=audit_path.lstat()
    require((current.st_dev,current.st_ino)==(info.st_dev,info.st_ino),'restore-audit-replaced')
    audit_path.unlink()
    checkpoint('validated')
    with store._transaction(write=True,lifecycle=True):
        owned()
        store.db.executemany('INSERT OR IGNORE INTO requirements VALUES(?,?)',
            [(role,cap) for role in ('read','write') for cap in snapshot.header[role+'_requirements']])
        require({(r['role'],r['capability']) for r in store.db.execute('SELECT role,capability FROM requirements')}==
                {(role,cap) for role in ('read','write') for cap in snapshot.header[role+'_requirements']},'restore-requirements-mismatch')
        require(store.db.execute('SELECT count(*) FROM operations').fetchone()[0]==operation_count and
                store.db.execute('SELECT count(*) FROM restore_origin').fetchone()[0]==1,'restore-index-count-mismatch')
        changed=store.db.execute('UPDATE current_root SET digest=? WHERE singleton=1',(root.sha256,))
        require(changed.rowcount==1,'restore-root-missing')
        store.db.execute('UPDATE restore_origin SET complete=1 WHERE singleton=1')
        store.db.execute('UPDATE generation SET quiescent=NULL WHERE singleton=1')
    checkpoint('sealed')
    require(store.root().ref==root,'restore-seal-mismatch')
    return root
