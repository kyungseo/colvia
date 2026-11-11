"""Shared Git candidate semantics with platform-owned process and file effects.

The caller supplies native identity, index mode, hook and durability operations.
This layer does not select a platform or make an OS permission decision.
"""
from contextlib import contextmanager
from dataclasses import asdict
from pathlib import Path
import hashlib,os,stat
from ..adapters.git import read_file,_absolute
from ..codec import RecordError,canonical_bytes,decode_canonical,require
from ..git_index import Entry,Index,parse,emit,integrate,LIMIT
from .observation_port import location,file_stamp,selected
from ..storage.sqlite import _token

def digest(raw):return hashlib.sha256(raw).hexdigest()
def absent(path):return not os.path.lexists(path)

class GitCandidate:
    @contextmanager
    def exclusion(self):
        require(not self.locked,'git-integration-lock-reentry')
        lock=self.scratch/'integration.lock'
        try:self.files.create(lock,b'')
        except FileExistsError:require(self.files.read(lock)==b'','invalid-git-integration-lock')
        with self.files.exclusion(lock):
            self.locked=True
            try:yield
            finally:self.locked=False

    def command(self,args,*,input_bytes=b'',input_path=None,index=None,identity=None,allowed=(0,),event=lambda *_:None):
        require(file_stamp(self.git.executable)==self.git.stamp,'git-executable-changed')
        require(asdict(location(self.root))==self.root_identity,'git-workspace-moved')
        require(not any((self.scratch/'hooks').iterdir()),'git-hooks-staging-not-empty')
        env=dict(self.env)
        if index is not None:
            require(Path(index).is_relative_to(self.scratch),'git-private-index-required');env['GIT_INDEX_FILE']=str(index)
        if identity is not None:
            require(set(identity)=={'name','email','date'},'git-author-required')
            for value in identity.values():require(type(value) is str and 0<len(value)<=256 and not any(c in value for c in '\0\n\r'),'invalid-git-author')
            require(not any(c in identity['name']+identity['email'] for c in '<>'),'invalid-git-author')
            for prefix in ('GIT_AUTHOR_','GIT_COMMITTER_'):
                env.update({prefix+'NAME':identity['name'],prefix+'EMAIL':identity['email'],prefix+'DATE':identity['date']})
        command=[str(self.git.executable),'--no-optional-locks','-c','core.fsmonitor=false',
            '-c','core.untrackedCache=false','-c','core.hooksPath='+str(self.scratch/'hooks'),
            '-c','gc.auto=0','-c','maintenance.auto=false','-c','core.fsync=all','-c','core.fsyncMethod=fsync','-C',str(self.root),*args]
        result=self.children.run(command,cwd=self.root,env=env,input_bytes=input_bytes,input_path=input_path,event=event)
        require(file_stamp(self.git.executable)==self.git.stamp,'git-executable-changed')
        require(result.code in allowed,'git-integration-command-failed')
        return result

    def observe_config(self,top,paths):
        # Use the original read port so configured hook paths remain visible.
        raw=self.git._run(self.root,('config','--null','--list','--show-origin'),limit=4*1024*1024).stdout
        values=self.git._run(self.root,('config','--null','--list'),limit=4*1024*1024).stdout
        conf={}
        for entry in values.split(b'\0'):
            if not entry:continue
            key,sep,value=entry.partition(b'\n');key=key.decode('utf-8');value=value.decode('utf-8') if sep else 'true'
            conf.setdefault(key,[]).append(value)
        disabled=lambda v:v.lower() in ('false','no','off','0')
        for key,values in conf.items():
            if key in ('core.autocrlf','core.sparsecheckout','core.sparsecheckoutcone','index.sparse','index.skiphash','commit.gpgsign'):
                require(all(disabled(v) for v in values),'git-config-requires-manual-integration')
            if key=='core.sharedrepository':require(all(v in ('0','false','umask') for v in values),'git-shared-repository-manual-integration')
            if key=='core.eol':require(all(v=='native' for v in values),'git-transform-not-supported')
            if key.startswith('extensions.'):
                require(key in ('extensions.objectformat','extensions.worktreeconfig','extensions.refstorage'),'git-extension-not-supported')
                if key=='extensions.refstorage':require(values==['files'],'git-ref-storage-not-supported')
            require(not key.endswith('.promisor') or all(disabled(v) for v in values),'git-promisor-not-supported')
            require(not key.startswith('filter.'),'git-transform-not-supported')
        common=Path(top.common.path)
        for name in ('MERGE_HEAD','CHERRY_PICK_HEAD','REVERT_HEAD','REBASE_HEAD','BISECT_LOG','rebase-apply','rebase-merge','sequencer'):
            require(absent(Path(top.gitdir.path)/name),'git-operation-in-progress')
        for name in ('info/grafts','shallow','objects/info/alternates','objects/info/http-alternates'):
            require(absent(common/name),'git-alternate-history-not-supported')
        pack=common/'objects/pack'
        if not absent(pack):require(not any(p.name.endswith('.promisor') for p in pack.iterdir()),'git-promisor-not-supported')
        require(not self.command(['for-each-ref','--format=%(refname)','refs/replace/']).stdout,'git-replacement-history-not-supported')
        result=self.git._run(self.root,('config','--path','--get','core.hooksPath'),allowed=(0,1),limit=32768)
        hooks=_absolute(self.root,result.stdout.rstrip(b'\n')) if result.code==0 else common/'hooks'
        if not absent(hooks):
            location(hooks)
            for child in hooks.iterdir():
                if child.name.endswith('.sample'):continue
                self.require_inactive_hook(child)
        attrs=self.command(['check-attr','-z','--stdin','filter','text','eol','working-tree-encoding','ident'],
                           input_bytes=b'\0'.join(p.encode() for p in paths)+b'\0').stdout
        parts=attrs.split(b'\0');require(parts[-1]==b'' and (len(parts)-1)%3==0,'git-attributes-unavailable')
        require(all(parts[i] in (b'unspecified',b'unset') for i in range(2,len(parts)-1,3)),'git-transform-not-supported')
        return digest(raw+attrs),str(hooks)

    def ref(self,branch,algorithm):
        result=self.command(['show-ref','--verify','--hash',branch],allowed=(0,1,128))
        if result.code==0:
            value=result.stdout.strip().decode('ascii');require(len(value)==hashlib.new(algorithm).digest_size*2 and all(c in '0123456789abcdef' for c in value),'invalid-git-ref');return value
        require(not result.stdout,'git-ref-unavailable')
        # Absence is checked by rev-parse as well; malformed/broken loose refs
        # must not be confused with an unborn branch.
        top=self.git.topology(self.root);loose=Path(top.common.path)/branch
        require(absent(loose),'git-ref-unavailable')
        raw=self.command(['for-each-ref','--format=%(refname)',branch]).stdout
        require(not raw,'git-ref-unavailable');return None

    def snapshot(self,paths):
        require(self.locked,'git-integration-lock-required')
        top=self.git.topology(self.root);require(top.root.path==str(self.root),'git-root-required')
        algorithm=self.command(['rev-parse','--show-object-format']).stdout.strip().decode('ascii')
        require(algorithm in ('sha1','sha256'),'unsupported-git-object-format')
        rawhead=read_file(Path(top.gitdir.path)/'HEAD',4096)
        require(rawhead.startswith(b'ref: refs/heads/') and rawhead.endswith(b'\n') and rawhead.count(b'\n')==1,'attached-git-branch-required')
        branch=rawhead[5:-1].decode('utf-8');self.command(['check-ref-format',branch])
        require(self.command(['symbolic-ref','-q',branch],allowed=(0,1)).code==1,'symbolic-target-branch-not-supported')
        for target in (Path(top.common.path)/branch,Path(top.common.path)/'packed-refs'):
            for parent in target.parents:
                if not absent(parent):location(parent)
            if not absent(target):read_file(target,64*1024*1024)
        members=self.git._run(self.root,('worktree','list','--porcelain','-z')).stdout
        require(members.split(b'\0').count(b'branch '+branch.encode())==1,'git-branch-in-another-worktree')
        config,hooks=self.observe_config(top,paths);index=Path(top.gitdir.path)/'index'
        i0=None if absent(index) else read_file(index,LIMIT)
        parsed=Index(algorithm,()) if i0 is None else parse(i0,algorithm)
        topology=asdict(top);topology['members']=list(topology['members'])
        return dict(topology=topology,algorithm=algorithm,branch=branch,head=rawhead.hex(),
            ref=self.ref(branch,algorithm),index=None if i0 is None else digest(i0),
            index_native=None if i0 is None else self.file_id(index),index_mode=None if i0 is None else self.index_mode(index),config=config,hooks=hooks,
            selected=list(selected(self.root,paths,byte_limit=2*1024*1024*1024,
                modes={path:format(e.mode,'o') for path,e in parsed.by_path().items()})),tool=self.git.identity),i0,parsed

    def tree(self,oid,algorithm):
        if oid is None:return {}
        raw=self.command(['ls-tree','-r','-z','--full-tree',oid]).stdout;entries=[]
        for row in raw.split(b'\0'):
            if not row:continue
            header,name=row.split(b'\t',1);mode,kind,sha=header.split(b' ')
            require(kind in (b'blob',b'commit'),'unsupported-git-tree-entry')
            entries.append(Entry(name,int(mode,8),bytes.fromhex(sha.decode('ascii'))))
        value=parse(emit(Index(algorithm,tuple(entries))),algorithm)
        return value.by_path()

    def prepare(self,operation,changes,body,*,message,identity):
        require(self.locked,'git-integration-lock-required');_token(operation)
        require(type(message) is str and 0<len(message.encode())<=65536 and '\0' not in message,'invalid-git-message')
        paths=sorted(changes);require(0<len(paths)<=100000,'git-selection-limit')
        context,i0,index=self.snapshot(paths);head=self.tree(context['ref'],context['algorithm'])
        area=self.scratch/operation;self.files.create_directory(area);after={}
        for n,path in enumerate(paths):
            entry=changes[path]
            if entry is None:after[path]=None;continue
            source=area/('body-'+str(n));count=0;sha=hashlib.sha256()
            gitsha=hashlib.new(context['algorithm']);gitsha.update(('blob '+str(entry['size'])+'\0').encode())
            with self.files.create_stream(source) as stream:
                for chunk in body(path):
                    require(type(chunk) is bytes,'invalid-git-body');count+=len(chunk);sha.update(chunk);gitsha.update(chunk)
                    require(count<=entry['size'],'git-body-size-mismatch')
                    require(stream.write(chunk)==len(chunk),'git-body-short-write')
            require(count==entry['size'] and sha.hexdigest()==entry['sha256'],'git-body-mismatch')
            oid=self.command(['hash-object','-w','--no-filters','--stdin'],input_path=source).stdout.strip()
            require(oid.decode()==gitsha.hexdigest(),'git-blob-body-mismatch')
            native=(index.by_path().get(path) or head.get(path))
            after[path]=Entry(native.native if native else path.encode(),int(entry['mode'],8),bytes.fromhex(oid.decode()))
        i1,tree_index=integrate(index,head,after)
        for name,raw in [('i0',i0 or b''),('i1',i1),('candidate-index',tree_index)]:self.files.create(area/name,raw)
        tree=self.command(['write-tree'],index=area/'candidate-index').stdout.strip().decode()
        args=['commit-tree','--no-gpg-sign',tree]
        if context['ref'] is not None:args+=['-p',context['ref']]
        commit=self.command(args,input_bytes=message.encode(),identity=identity).stdout.strip().decode()
        # An empty tree is an object, not a ref. This is safe for an unborn HEAD.
        oldtree=context['ref'] or self.command(['hash-object','-t','tree','-w','--stdin']).stdout.strip().decode()
        require(not context['ref'] or tree!=self.command(['rev-parse',context['ref']+'^{tree}']).stdout.strip().decode(),'git-no-candidate-change')
        patch=self.command(['diff-tree','--no-commit-id','--no-ext-diff','--no-textconv','--binary','-r','-p',oldtree,tree]).stdout
        self.files.create(area/'diff',patch)
        now,_,_=self.snapshot(paths);require(now==context,'git-candidate-context-changed')
        manifest=dict(operation=operation,context=context,paths=paths,new=commit,tree=tree,i1=digest(i1),diff=digest(patch),message=message,author=identity)
        self.files.create(area/'manifest',canonical_bytes(manifest));return manifest

    def verify_manifest(self,m,*,objects=True):
        _token(m['operation']);area=self.scratch/m['operation']
        require(decode_canonical(self.files.read(area/'manifest',4*1024*1024))==m,'git-manifest-changed')
        require(digest(self.files.read(area/'i1',LIMIT))==m['i1'] and digest(self.files.read(area/'diff',16*1024*1024))==m['diff'],'git-staging-changed')
        require(self.files.read(area/'i0',LIMIT)==b'' if m['context']['index'] is None else
                digest(self.files.read(area/'i0',LIMIT))==m['context']['index'],'git-staging-changed')
        if not objects:return area
        # Verify the stored commit still names the prepared tree and parent.
        commit=self.command(['cat-file','commit',m['new']]).stdout
        require(self.command(['hash-object','-t','commit','--stdin'],input_bytes=commit).stdout.strip().decode()==m['new'],'git-candidate-object-changed')
        headers,separator,body=commit.partition(b'\n\n');require(separator,'git-candidate-object-invalid')
        lines=headers.split(b'\n');require(lines[0]==('tree '+m['tree']).encode(),'git-candidate-tree-changed')
        parents=[line[7:].decode() for line in lines if line.startswith(b'parent ')]
        require(parents==([] if m['context']['ref'] is None else [m['context']['ref']]),'git-candidate-parent-changed')
        require(body==m['message'].encode() or body==m['message'].encode()+b'\n','git-candidate-message-changed')
        self.verify_objects(m)
        return area

    def check(self,m,*,index='old',ref='old'):
        self.verify_manifest(m);now,_,_=self.snapshot(m['paths']);expected=dict(m['context'])
        expected['ref']=m['new'] if ref=='new' else expected['ref']
        if index=='new':
            expected['index']=m['i1'];expected['index_mode']=expected['index_mode'] if expected['index_mode'] is not None else 0o600
            now.pop('index_native');expected.pop('index_native')
        require(now==expected,'git-integration-context-changed')

    def locks(self,m):
        c=m['context']['topology'];gitdir=Path(c['gitdir']['path']);common=Path(c['common']['path'])
        return [gitdir/'HEAD.lock',common/'packed-refs.lock',common/(m['context']['branch']+'.lock')]

    def lock_path(self,m):return Path(m['context']['topology']['gitdir']['path'])/'index.lock'

    def update_ref(self,m,owner,*,live,event):
        self.owned_lock(m,owner);self.check(m);require(all(absent(p) for p in self.locks(m)),'git-child-lock-present');live()
        old=m['context']['ref'] or '0'*(hashlib.new(m['context']['algorithm']).digest_size*2)
        return self.command(['update-ref','--no-deref',m['context']['branch'],m['new'],old],event=event,allowed=(0,1,128))

    def placement(self,m):
        # Completion never reinterprets later user edits as accepted bytes.
        # It only finishes the already approved index transition. Recheck the
        # destination identity and attached branch without admitting a new ref.
        c=m['context'];top=self.git.topology(self.root)
        for name in ('root','common','gitdir'):
            require(asdict(getattr(top,name))==c['topology'][name],'git-destination-changed')
        require(read_file(Path(top.gitdir.path)/'HEAD',4096).hex()==c['head'],'git-head-changed')
        members=self.git._run(self.root,('worktree','list','--porcelain','-z')).stdout
        require(members.split(b'\0').count(b'branch '+c['branch'].encode())==1,'git-branch-in-another-worktree')
        require(self.command(['symbolic-ref','-q',c['branch']],allowed=(0,1)).code==1,'symbolic-target-branch-not-supported')
        return top

    def inspect_outcome(self,m):
        self.verify_manifest(m,objects=False);top=self.placement(m);old=m['context']
        actual_ref=self.ref(old['branch'],old['algorithm']);path=Path(top.gitdir.path)/'index'
        raw=None if absent(path) else read_file(path,LIMIT)
        index=None if raw is None else digest(raw);native=None if raw is None else self.file_id(path)
        mode=None if raw is None else self.index_mode(path)
        r='old' if actual_ref==old['ref'] else 'new' if actual_ref==m['new'] else 'other'
        i='old' if index==old['index'] and native==old['index_native'] and mode==old['index_mode'] else 'new' if index==m['i1'] and mode==(old['index_mode'] if old['index_mode'] is not None else 0o600) else 'other'
        return r,i

    def check_post(self,m):
        require(self.inspect_outcome(m)==('new','new'),'git-integration-postcondition-unconfirmed')
        self.verify_objects(m);self.flush_ref(m)

    def verify_objects(self,m):
        args=['rev-list','--objects','--no-object-names','--missing=error',m['new']]
        if m['context']['ref'] is not None:args+=['--not',m['context']['ref']]
        raw=self.command(args).stdout;oids=raw.splitlines();size=hashlib.new(m['context']['algorithm']).digest_size*2
        require(oids and len(oids)<=100000 and all(len(o)==size and all(c in b'0123456789abcdef' for c in o) for o in oids),'git-object-walk-unavailable')
        result=self.command(['cat-file','--batch-check'],input_bytes=raw).stdout.splitlines()
        require(len(result)==len(oids),'git-object-walk-unavailable')
        for oid,line in zip(oids,result,strict=True):
            parts=line.split();require(len(parts)==3 and parts[0]==oid and parts[1] in (b'commit',b'tree',b'blob',b'tag') and parts[2].isdigit(),'git-candidate-object-missing')
        common=Path(m['context']['topology']['common']['path']);packed=False
        for oid in oids:
            value=oid.decode();path=common/'objects'/value[:2]/value[2:]
            if absent(path):packed=True;continue
            self.flush_native(path)
        if packed:
            paths=list((common/'objects/pack').iterdir());require(len(paths)<=10000,'git-pack-count-limit')
            for path in paths:
                if path.suffix in ('.pack','.idx','.rev'):self.flush_native(path)
        self.files.sync_directory(common/'objects')

    def flush_ref(self,m):
        c=m['context'];common=Path(c['topology']['common']['path']);branch=common/c['branch']
        require(self.ref(c['branch'],c['algorithm'])==m['new'],'git-ref-update-unconfirmed')
        if not absent(branch):self.flush_native(branch)
        elif not absent(common/'packed-refs'):self.flush_native(common/'packed-refs')
        else:raise RecordError('git-ref-durability-unavailable')
        for path in (common/'logs'/c['branch'],Path(c['topology']['gitdir']['path'])/'logs/HEAD'):
            if not absent(path):self.flush_native(path)
        for parent in branch.parents:
            if not absent(parent):self.files.sync_directory(parent)
            if parent==common:break

    def lock_absent(self,m):return absent(self.lock_path(m))

