"""Local NTFS observation port; project ACLs are never rewritten or made private.

Native handles pin ancestors and inspected leaves. Symlink leaves are opaque;
reparse ancestors and other reparse kinds refuse. Tests with a POSIX API double
check the algorithm only, not native Windows handle/filesystem qualification.
"""
from pathlib import Path
from contextlib import contextmanager
import os,stat,hashlib,base64
from ..binding import NativeLocation
from ..codec import require,RecordError,canonical_bytes
from ..tree import logical_path,canonical_entries
from ..storage.windows import WindowsFiles
from .posix import Snapshot,NativeStamp


class Observer:
    def __init__(self,*,files=None):self.files=files or WindowsFiles();self.api=self.files.api

    @staticmethod
    def identity(info):
        volume,file_id,creation=info['identity']
        return str(volume),str(file_id)+':'+str(creation)

    def stamp(self,name,info):
        mode=stat.S_IFLNK if info.get('symlink') else (stat.S_IFDIR if info['directory'] else stat.S_IFREG)
        return NativeStamp(name,*self.identity(info),mode,info['size'],info['write'],info['change'])

    def location(self,path):
        path=Path(path);a=self.api
        with a.ancestors(path),a.opened(path,share=3) as h:
            info=a.state(h,path);require(info['directory'],'workspace-not-directory')
            return NativeLocation(str(path),*self.identity(info))

    @contextmanager
    def opened(self,path,*,read=False,opaque=False):
        a=self.api
        with a.ancestors(path),a.opened(path,access=0x80000080 if read else 0x80,share=1) as h:
            info=a.state(h,path,opaque_symlink=opaque)
            yield h,info
            require(a.state(h,path,opaque_symlink=opaque)==info,'file-observation-changed')

    def names(self,path,limit):
        names=[];aliases=set()
        with os.scandir(path) as scan:
            for entry in scan:
                require(len(names)<limit,'observation-entry-limit')
                name=logical_path(entry.name)
                require('/' not in name and name.casefold() not in aliases,'path-collision')
                aliases.add(name.casefold());names.append(entry.name)
        return sorted(names,key=lambda x:x.encode('utf-8'))

    def regular(self,path,info,*,limit,cancelled,algorithm=None,mode='100644'):
        used=0;digest=hashlib.sha256();blob=hashlib.new(algorithm) if algorithm else None
        require(not info.get('symlink') and not info['directory'] and info['size']<=limit,'observation-byte-limit')
        if blob is not None:blob.update(b'blob '+str(info['size']).encode()+b'\0')
        with self.opened(path,read=True) as (h,current):
            require(current==info,'file-observation-changed')
            with self.files._stream_handle(h) as stream:
                while raw:=stream.read(1024*1024):
                    require(not cancelled(),'observation-cancelled');used+=len(raw)
                    require(used<=limit,'observation-byte-limit');digest.update(raw)
                    if blob is not None:blob.update(raw)
        require(used==info['size'],'file-observation-changed')
        return dict(kind='regular',mode=mode,size=used,sha256=digest.hexdigest()),blob.hexdigest() if blob else None

    def read_file(self,path,limit):
        require(type(limit) is int and 0<=limit<=128*1024*1024,'metadata-file-limit')
        with self.opened(Path(path),read=True) as (h,info):
            require(not info['directory'] and info['links']==1 and info['size']<=limit,'unsafe-metadata-file')
            with self.files._stream_handle(h) as stream:raw=stream.read(limit+1)
            require(len(raw)==info['size'] and len(raw)<=limit,'metadata-file-limit')
            return raw

    @contextmanager
    def opened_git_executable(self, path):
        """Read the caller-selected Windows Git executable under a read-share-only handle."""
        path = Path(path)
        require(path.suffix.lower() == '.exe', 'git-not-executable')
        with self.opened(path, read=True) as (handle, info):
            require(not info['directory'] and 1 <= info['links'] and
                    64 <= info['size'] <= 128 * 1024**2, 'git-not-executable')
            with self.files._stream_handle(handle) as stream:
                raw = stream.read(info['size'] + 1)
            require(len(raw) == info['size'], 'git-executable-changed')
            offset = int.from_bytes(raw[60:64], 'little')
            require(raw.startswith(b'MZ') and 64 <= offset <= len(raw) - 24 and
                    raw[offset:offset + 4] == b'PE\x00\x00', 'git-not-executable')
            observed = self.stamp('', info)
            digest = hashlib.sha256(raw).hexdigest()
            del raw
            yield observed, digest

    def symlink(self,path,*,algorithm=None):
        # The caller holds the reparse-point handle without FILE_SHARE_DELETE.
        raw=os.readlink(path).encode('utf-8',errors='strict')
        entry=dict(kind='symlink',mode='120000',target=base64.b64encode(raw).decode('ascii'))
        blob=None
        if algorithm:
            h=hashlib.new(algorithm);h.update(b'blob '+str(len(raw)).encode()+b'\0'+raw);blob=h.hexdigest()
        return entry,blob

    def snapshot(self,root,budget,*,admit=lambda _:True,protected=frozenset(),boundaries=None,
                 cancelled=lambda:False,reject_nested_git=False,reject_nested_colvia=False,git_algorithm=None,opaque_entries=None,modes=None):
        require(type(budget.entries) is int and 0<budget.entries<=1000000 and type(budget.read_bytes) is int and budget.read_bytes>=0,'invalid-observation-budget')
        require(git_algorithm in (None,'sha1','sha256'),'unsupported-git-object-format')
        root=Path(root);root_location=self.location(root);boundaries=dict(boundaries or {});opaque_entries=dict(opaque_entries or {});modes=dict(modes or {})
        require(all(logical_path(p)==p and type(pair) is tuple and len(pair)==2 for p,pair in boundaries.items()),'invalid-boundary')
        require(all(logical_path(p)==p and mode in ('100644','100755') for p,mode in modes.items()),'invalid-file-mode')
        entries=[];stamps=[];inventory=[];blobs=[];visited=0;used=0;metadata=0;aliases=set()
        def visit(directory,parts,depth):
            nonlocal visited,used,metadata
            require(depth<=128,'observation-depth-limit')
            with self.opened(directory) as (_,dinfo):
                require(dinfo['directory'],'workspace-not-directory');names=self.names(directory,budget.entries-visited)
                for name in names:
                    require(not cancelled(),'observation-cancelled')
                    native='/'.join((*parts,name));path=directory/name;logical=logical_path(native)
                    folded=logical.casefold()
                    require(folded not in aliases,'path-collision');aliases.add(folded)
                    visited+=1;require(visited<=budget.entries,'observation-entry-limit')
                    git_marker=reject_nested_git and (folded=='.git' or folded.endswith('/.git'))
                    root_git_marker=git_marker and not parts
                    # The listing has already refused case-fold collisions.
                    boundary='.git' if root_git_marker and native not in boundaries else native
                    with self.opened(path,opaque=True) as (_,info):
                        if boundary in boundaries:
                            require(not any(p==logical or p.startswith(logical+'/') or
                                            (root_git_marker and p.partition('/')[0].casefold()=='.git')
                                            for p in protected),'boundary-swallows-protected')
                            require(not info.get('symlink') and self.identity(info)==boundaries[boundary],
                                    'structural-boundary-changed')
                            continue
                        if git_marker:
                            from ..connection_boundary import ConnectionBoundaryError
                            raise ConnectionBoundaryError('unregistered-nested-git',str(root.joinpath(*parts)),str(root))
                        if reject_nested_colvia and name.casefold()=='.colvia-link.json' and (parts or name!='.colvia-link.json'):
                            from ..connection_boundary import ConnectionBoundaryError
                            raise ConnectionBoundaryError('workspace-nested-project',str(root.joinpath(*parts)),str(root))
                        itemstamp=self.stamp(native,info);inventory.append(itemstamp)
                        if native in opaque_entries:
                            pair,entry=opaque_entries[native]
                            require(info['directory'] and not info.get('symlink') and self.identity(info)==pair,'opaque-entry-changed')
                            require(entry['path']==logical and entry['kind']=='gitlink','invalid-opaque-entry');canonical_entries([entry]);blob=None
                        elif info.get('symlink'):
                            if not (admit(logical) or logical in protected):continue
                            entry,blob=self.symlink(path,algorithm=git_algorithm);entry=dict(path=logical,**entry)
                        elif info['directory']:
                            visit(path,(*parts,name),depth+1);continue
                        else:
                            if not (admit(logical) or logical in protected):continue
                            entry,blob=self.regular(path,info,limit=budget.read_bytes-used,cancelled=cancelled,algorithm=git_algorithm,mode=modes.get(logical,'100644'))
                            used+=entry['size'];entry=dict(path=logical,**entry)
                        metadata+=len(canonical_bytes(entry));require(metadata<=512*1024*1024,'observation-metadata-limit')
                        entries.append(entry);stamps.append(itemstamp)
                        if blob is not None:blobs.append((logical,blob))
                require(names==self.names(directory,len(names)),'directory-observation-changed')
        visit(root,(),0);require(self.location(root)==root_location,'root-observation-changed')
        return Snapshot(root_location,tuple(canonical_entries(entries)),tuple(stamps),used,tuple(inventory),tuple(blobs))

    def resolve_selected(self,root,path,*,verify_path=False):
        require(logical_path(path)==path,'invalid-scope-path');directory=Path(root)
        parts=path.split('/')
        for i,part in enumerate(parts):
            with self.opened(directory) as (_,info):
                require(info['directory'] and not info.get('symlink'),'unsafe-scope-ancestor')
                names={logical_path(name):name for name in self.names(directory,1000000)}
                if verify_path and i:
                    require({n.casefold() for n in names}.isdisjoint({'.git', '.colvia-link.json'}), 'progress-nested-project')
                if part not in names:return None
                directory=directory/names[part]
        return directory

    def selected(self,root,paths,*,byte_limit,modes=None,verify_path=False):
        entries=[];used=0;modes=dict(modes or {})
        for path in sorted(paths):
            native=self.resolve_selected(root,path,verify_path=verify_path)
            if native is None:
                if verify_path:
                    require(self.resolve_selected(root,path,verify_path=True) is None, 'file-observation-changed')
                continue
            with self.opened(native,opaque=True) as (_,info):
                if info.get('symlink'):entry,_=self.symlink(native)
                else:
                    require(not info['directory'],'scope-entry-not-regular')
                    entry,_=self.regular(native,info,limit=byte_limit-used,cancelled=lambda:False,mode=modes.get(path,'100644'));used+=entry['size']
                if verify_path:
                    again = self.resolve_selected(root, path, verify_path=True)
                    require(again == native, 'file-observation-changed')
                    with self.opened(again, opaque=True) as (_, live):
                        require(self.stamp('', live) == self.stamp('', info), 'file-observation-changed')
                entries.append(dict(path=path,**entry))
        return tuple(entries)

    def capture(self,root,path,expected,store,import_id):
        from ..bodies import ingest_body
        require(expected['kind']=='regular','opaque-edit-not-supported')
        native=self.resolve_selected(root,path);require(native is not None,'body-observation-changed')
        with self.opened(native,read=True) as (h,info):
            require(not info['directory'] and not info.get('symlink'),'body-observation-changed')
            with self.files._stream_handle(h) as stream:
                return ingest_body(stream,store,import_id,expected_size=expected['size'],expected_sha256=expected['sha256'])
