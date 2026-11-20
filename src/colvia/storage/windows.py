"""Native Windows lifecycle files: explicit ACL, no reparse traversal, bounded lock.

Only local NTFS is admitted. This adapter never changes an existing ACL, enables
privileges, changes machine settings or falls back to POSIX locking. Native
qualification on ARM64 and x64 is separate from import/static and fake-API tests.
"""
from contextlib import contextmanager,ExitStack
from pathlib import Path,PureWindowsPath
import ctypes as C
import ntpath,os,sys,time,uuid
from ..codec import RecordError,require


def local_path(value):
    s=os.fspath(value);p=PureWindowsPath(s)
    require(type(s) is str and len(p.drive)==2 and p.drive[1]==':' and p.root and
            not s.startswith(('\\\\','//')) and len(s.encode('utf-16-le'))//2<248,'windows-local-path-required')
    for part in p.parts[1:]:
        require(part not in ('.','..') and
                not part.endswith((' ','.')) and not any(c in part for c in ':<>"|?*') and
                not any(ord(c)<32 for c in part) and part.split('.')[0].upper() not in
                {'CON','PRN','AUX','NUL',*[f'COM{i}' for i in range(1,10)],*[f'LPT{i}' for i in range(1,10)]},'windows-path-alias')
    # PureWindowsPath normalizes dot/duplicate separators, so reject those in input.
    require(str(p)==s.replace('/','\\'),'windows-path-noncanonical')
    return str(p)


class API:
    def __init__(self):
        require(sys.platform=='win32','windows-native-unavailable')
        from ctypes import wintypes as W
        self.W=W;self.kernel=C.WinDLL('kernel32',use_last_error=True);self.adv=C.WinDLL('advapi32',use_last_error=True)
        class Tag(C.Structure):_fields_=[('attributes',W.DWORD),('tag',W.DWORD)]
        class Id(C.Structure):_fields_=[('volume',C.c_ulonglong),('identifier',C.c_ubyte*16)]
        class Standard(C.Structure):_fields_=[('allocation',C.c_longlong),('size',C.c_longlong),('links',W.DWORD),('deleted',C.c_ubyte),('directory',C.c_ubyte)]
        class Basic(C.Structure):_fields_=[('creation',C.c_longlong),('access',C.c_longlong),('write',C.c_longlong),('change',C.c_longlong),('attributes',W.DWORD)]
        class Overlapped(C.Structure):_fields_=[('Internal',C.c_size_t),('InternalHigh',C.c_size_t),('Offset',W.DWORD),('OffsetHigh',W.DWORD),('hEvent',W.HANDLE)]
        class Security(C.Structure):_fields_=[('length',W.DWORD),('descriptor',C.c_void_p),('inherit',W.BOOL)]
        class ACL(C.Structure):_fields_=[('revision',C.c_ubyte),('unused',C.c_ubyte),('size',W.WORD),('count',W.WORD),('reserved',W.WORD)]
        self.Tag,self.Id,self.Standard,self.Basic,self.Overlapped,self.Security,self.ACL=Tag,Id,Standard,Basic,Overlapped,Security,ACL
        self.invalid=C.c_void_p(-1).value
        for name,result,args in (
            ('CreateFileW',W.HANDLE,(W.LPCWSTR,W.DWORD,W.DWORD,C.c_void_p,W.DWORD,W.DWORD,W.HANDLE)),
            ('CreateDirectoryW',W.BOOL,(W.LPCWSTR,C.c_void_p)),('CloseHandle',W.BOOL,(W.HANDLE,)),
            ('DuplicateHandle',W.BOOL,(W.HANDLE,W.HANDLE,W.HANDLE,C.POINTER(W.HANDLE),W.DWORD,W.BOOL,W.DWORD)),
            ('GetCurrentProcess',W.HANDLE,()),('LocalFree',C.c_void_p,(C.c_void_p,)),
            ('GetFileInformationByHandleEx',W.BOOL,(W.HANDLE,C.c_int,C.c_void_p,W.DWORD)),
            ('GetFinalPathNameByHandleW',W.DWORD,(W.HANDLE,W.LPWSTR,W.DWORD,W.DWORD)),
            ('GetVolumeInformationByHandleW',W.BOOL,(W.HANDLE,W.LPWSTR,W.DWORD,C.POINTER(W.DWORD),C.POINTER(W.DWORD),C.POINTER(W.DWORD),W.LPWSTR,W.DWORD)),
            ('GetDriveTypeW',W.UINT,(W.LPCWSTR,)),('FlushFileBuffers',W.BOOL,(W.HANDLE,)),
            ('ReadFile',W.BOOL,(W.HANDLE,C.c_void_p,W.DWORD,C.POINTER(W.DWORD),C.c_void_p)),
            ('WriteFile',W.BOOL,(W.HANDLE,C.c_void_p,W.DWORD,C.POINTER(W.DWORD),C.c_void_p)),
            ('RemoveDirectoryW',W.BOOL,(W.LPCWSTR,)),('MoveFileExW',W.BOOL,(W.LPCWSTR,W.LPCWSTR,W.DWORD)),('DeleteFileW',W.BOOL,(W.LPCWSTR,)),
            ('LockFileEx',W.BOOL,(W.HANDLE,W.DWORD,W.DWORD,W.DWORD,W.DWORD,C.POINTER(Overlapped))),
            ('UnlockFileEx',W.BOOL,(W.HANDLE,W.DWORD,W.DWORD,W.DWORD,C.POINTER(Overlapped)))):
            self.bind(self.kernel,name,result,args)
        for name,result,args in (
            ('OpenProcessToken',W.BOOL,(W.HANDLE,W.DWORD,C.POINTER(W.HANDLE))),
            ('GetTokenInformation',W.BOOL,(W.HANDLE,C.c_int,C.c_void_p,W.DWORD,C.POINTER(W.DWORD))),
            ('ConvertSidToStringSidW',W.BOOL,(C.c_void_p,C.POINTER(W.LPWSTR))),
            ('ConvertStringSecurityDescriptorToSecurityDescriptorW',W.BOOL,(W.LPCWSTR,W.DWORD,C.POINTER(C.c_void_p),C.POINTER(W.DWORD))),
            ('GetSecurityInfo',W.DWORD,(W.HANDLE,C.c_int,W.DWORD,C.POINTER(C.c_void_p),C.POINTER(C.c_void_p),C.POINTER(C.c_void_p),C.POINTER(C.c_void_p),C.POINTER(C.c_void_p))),
            ('GetAce',W.BOOL,(C.c_void_p,W.DWORD,C.POINTER(C.c_void_p))),
            ('GetSecurityDescriptorControl',W.BOOL,(C.c_void_p,C.POINTER(W.WORD),C.POINTER(W.DWORD)))):
            self.bind(self.adv,name,result,args)
        token=W.HANDLE();self.ok(self.OpenProcessToken(self.GetCurrentProcess(),8,C.byref(token)))
        try:
            size=W.DWORD();self.GetTokenInformation(token,1,None,0,C.byref(size));require(0<size.value<=65536,'windows-token-size')
            buf=C.create_string_buffer(size.value);self.ok(self.GetTokenInformation(token,1,buf,size,C.byref(size)))
            sid=C.cast(buf,C.POINTER(C.c_void_p))[0];self.sid=self.sid_text(sid)
        finally:self.close(token)
    def bind(self,dll,name,result,args):
        fn=getattr(dll,name);fn.restype=result;fn.argtypes=args;setattr(self,name,fn)
    def ok(self,result):
        if not result:raise C.WinError(C.get_last_error())
        return result
    def close(self,h):self.ok(self.CloseHandle(h))
    def sid_text(self,sid):
        value=self.W.LPWSTR();self.ok(self.ConvertSidToStringSidW(sid,C.byref(value)))
        try:return value.value
        finally:self.LocalFree(C.cast(value,C.c_void_p))
    @contextmanager
    def security(self):
        sd=C.c_void_p();self.ok(self.ConvertStringSecurityDescriptorToSecurityDescriptorW(
            'O:'+self.sid+'D:P(A;OICI;FA;;;'+self.sid+')',1,C.byref(sd),None))
        sa=self.Security(C.sizeof(self.Security),sd,False)
        try:yield C.byref(sa)
        finally:self.LocalFree(sd)
    def private(self,h,*,directory=False):
        owner=C.c_void_p();acl=C.c_void_p();sd=C.c_void_p()
        error=self.GetSecurityInfo(h,1,5,C.byref(owner),None,C.byref(acl),None,C.byref(sd))
        if error:raise C.WinError(error)
        try:
            require(owner.value and self.sid_text(owner)==self.sid and acl.value,'windows-store-not-private')
            control=self.W.WORD();revision=self.W.DWORD();self.ok(self.GetSecurityDescriptorControl(sd,C.byref(control),C.byref(revision)))
            if directory:require(control.value&0x1000,'windows-private-dacl-not-protected')
            a=C.cast(acl,C.POINTER(self.ACL)).contents;require(0<a.count<=32,'windows-store-not-private');allowed=0
            for i in range(a.count):
                ace=C.c_void_p();self.ok(self.GetAce(acl,i,C.byref(ace)))
                header=C.string_at(ace,4);require(header[0]==0 and not header[1]&0x08,'windows-store-not-private')
                require(self.sid_text(ace.value+8)==self.sid,'windows-store-not-private')
                allowed|=C.cast(ace.value+4,C.POINTER(self.W.DWORD)).contents.value
            require(allowed&0x1f01ff==0x1f01ff,'windows-store-not-private')
        finally:self.LocalFree(sd)
    @contextmanager
    def opened(self,path,*,access=0x20080,share=3,disposition=3,security=None):
        h=self.CreateFileW(local_path(path),access,share,security,disposition,0x02200000,None)
        if h==self.invalid:raise C.WinError(C.get_last_error())
        try:yield h
        finally:self.close(h)
    def state(self,h,path,*,opaque_symlink=False):
        fs=C.create_unicode_buffer(32);self.ok(self.GetVolumeInformationByHandleW(h,None,0,None,None,None,fs,len(fs)))
        require(fs.value=='NTFS' and self.GetDriveTypeW(PureWindowsPath(local_path(path)).anchor)==3,'windows-local-ntfs-required')
        tag,id_,s,b=self.Tag(),self.Id(),self.Standard(),self.Basic()
        for kind,value in ((9,tag),(18,id_),(1,s),(0,b)):
            self.ok(self.GetFileInformationByHandleEx(h,kind,C.byref(value),C.sizeof(value)))
        reparse=bool(tag.attributes&0x400)
        require(not s.deleted and tag.attributes==b.attributes and
                ((not reparse and not tag.tag) or (opaque_symlink and reparse and tag.tag==0xa000000c)),
                'windows-reparse-or-changing-file')
        name=C.create_unicode_buffer(32768);n=self.GetFinalPathNameByHandleW(h,name,len(name),0)
        require(0<n<len(name) and name.value.startswith('\\\\?\\') and
                name.value[4:].casefold()==local_path(path).casefold(),'windows-final-path-mismatch')
        return dict(identity=(int(id_.volume),bytes(id_.identifier).hex(),int(b.creation)),directory=bool(s.directory),
                    links=int(s.links),size=int(s.size),write=int(b.write),change=int(b.change),symlink=reparse)
    @contextmanager
    def ancestors(self,path):
        path=PureWindowsPath(local_path(path))
        with ExitStack() as stack:
            for parent in reversed(path.parents):
                h=stack.enter_context(self.opened(str(parent)));s=self.state(h,str(parent));require(s['directory'],'windows-parent-not-directory')
            yield


class WindowsFiles:
    def __init__(self,*,api=None):self.api=api or API()
    def verify_runtime_inventory(self,root,expected,manifest_raw,manifest_sha256,*,cancelled=lambda:False):
        from ..updates.windows_payload import verify_inventory
        return verify_inventory(root,expected,manifest_raw,manifest_sha256,self,cancelled=cancelled)
    def private_directory(self,path):
        a=self.api
        with a.ancestors(path),a.opened(path) as h:
            require(a.state(h,path)['directory'],'windows-parent-not-directory');a.private(h,directory=True)
    def create_directory(self,path):
        a=self.api
        with a.ancestors(path),a.security() as sd:
            a.ok(a.CreateDirectoryW(local_path(path),sd))
            self.private_directory(path);self.sync_directory(Path(path).parent)
    def directory_identity(self,path):
        a=self.api
        with a.ancestors(path),a.opened(path) as handle:
            state=a.state(handle,path);a.private(handle,directory=True)
            require(state['directory'],'windows-parent-not-directory')
            return list(state['identity'])
    def publish_directory(self,source,destination,identity):
        source=Path(source);destination=Path(destination);a=self.api
        require(source.parent==destination.parent and source!=destination,'lifecycle-publication-parent')
        with a.ancestors(source),a.ancestors(destination):
            require(self.directory_identity(source)==identity,'lifecycle-directory-changed')
            try:
                a.ok(a.MoveFileExW(local_path(source),local_path(destination),8))
                self.sync_directory(destination.parent)
            except OSError as exc:raise RecordError('lifecycle-directory-publication-unconfirmed') from exc
            require(self.directory_identity(destination)==identity and not os.path.lexists(source),
                    'lifecycle-directory-publication-unconfirmed')

    def identity(self,path):
        a=self.api
        with a.ancestors(path),a.opened(path) as h:
            s=a.state(h,path);require(not s['directory'] and s['links']==1,'unsafe-store-file');a.private(h)
            return s['identity']
    def read(self,path,limit=16384):
        a=self.api
        with a.ancestors(path),a.opened(path,access=0x80020000,share=5) as h:
            before=a.state(h,path);a.private(h)
            require(not before['directory'] and before['links']==1 and 0<=before['size']<=limit,'invalid-lifecycle-file')
            parts=[];total=0
            while total<=limit:
                buf=C.create_string_buffer(min(1024*1024,limit+1-total));count=a.W.DWORD()
                a.ok(a.ReadFile(h,buf,len(buf),C.byref(count),None))
                if not count.value:break
                total+=count.value;parts.append(buf.raw[:count.value])
            require(total==before['size'] and a.state(h,path)==before,'lifecycle-file-changed')
            with a.opened(path,share=5) as current:
                require(a.state(current,path)['identity']==before['identity'],'lifecycle-file-changed')
            return b''.join(parts)
    def read_known_alias_pair(self,versioned,alias,limit):
        # Only the pinned TUF adapter requests this exact pair. It is not a
        # generic relaxation of the single-link authority/runtime rule.
        a=self.api;require(Path(versioned)!=Path(alias),'windows-alias-pair-invalid')
        with a.ancestors(versioned),a.ancestors(alias),a.opened(versioned,access=0x80020000,share=1) as first,a.opened(alias,access=0x80020000,share=1) as second:
            states=[a.state(first,versioned),a.state(second,alias)]
            for h,s in zip((first,second),states):
                a.private(h);require(not s['directory'] and s['size']<=limit,'invalid-lifecycle-file')
            same=states[0]['identity']==states[1]['identity']
            require(all(s['links']==(2 if same else 1) for s in states),'windows-alias-link-count')
            values=[]
            for h in (first,second):
                with self._stream_handle(h) as stream:values.append(stream.read(limit+1))
            require(values[0]==values[1] and len(values[0])==states[0]['size']==states[1]['size'] and
                a.state(first,versioned)==states[0] and a.state(second,alias)==states[1],'update-root-cache-changed')
            return values[0]

    @contextmanager
    def _stream_handle(self,handle,*,write=False):
        # Duplicate ownership: Python closes only the duplicate, while the native
        # context retains the original identity/share restrictions until exit.
        import msvcrt
        a=self.api;duplicate=a.W.HANDLE();process=a.GetCurrentProcess()
        a.ok(a.DuplicateHandle(process,handle,process,C.byref(duplicate),0,False,2))
        try:fd=msvcrt.open_osfhandle(duplicate.value,(0 if write else os.O_RDONLY)|os.O_BINARY|os.O_NOINHERIT)
        except BaseException:a.close(duplicate);raise
        with os.fdopen(fd,'r+b' if write else 'rb') as stream:yield stream

    @contextmanager
    def read_stream(self,path,limit):
        a=self.api
        with a.ancestors(path),a.opened(path,access=0x80020000,share=1) as handle:
            before=a.state(handle,path);a.private(handle)
            require(not before['directory'] and before['links']==1 and before['size']<=limit,'invalid-lifecycle-file')
            with self._stream_handle(handle) as stream:yield stream
            require(a.state(handle,path)==before,'lifecycle-file-changed')
            with a.opened(path,share=1) as current:require(a.state(current,path)['identity']==before['identity'],'lifecycle-file-changed')

    @contextmanager
    def create_stream(self,path,*,executable=False):
        a=self.api;self.private_directory(Path(path).parent)
        with a.ancestors(path),a.security() as sd,a.opened(path,access=0xc0020080,share=0,disposition=1,security=sd) as handle:
            before=a.state(handle,path);a.private(handle)
            require(not before['directory'] and before['links']==1,'unsafe-store-file')
            with self._stream_handle(handle,write=True) as stream:
                yield stream
                stream.flush();a.ok(a.FlushFileBuffers(handle))
            after=a.state(handle,path)
            require(after['identity']==before['identity'] and after['links']==1 and not after['directory'],'lifecycle-file-changed')
        # Executability on Windows is part of the signed inventory, not a POSIX
        # chmod bit. ACLs and the executable format determine native execution.
        self.sync_directory(Path(path).parent)

    def _write_new(self,path,raw):
        a=self.api;self.private_directory(Path(path).parent)
        with a.ancestors(path),a.security() as sd,a.opened(path,access=0x40020080,share=0,disposition=1,security=sd) as h:
            a.private(h);state=a.state(h,path);require(not state['directory'] and state['links']==1,'unsafe-store-file')
            offset=0
            while offset<len(raw):
                part=raw[offset:offset+1024*1024];buf=C.create_string_buffer(part);count=a.W.DWORD()
                a.ok(a.WriteFile(h,buf,len(part),C.byref(count),None));require(0<count.value<=len(part),'lifecycle-short-write');offset+=count.value
            a.ok(a.FlushFileBuffers(h))
        self.sync_directory(Path(path).parent)
    def exists(self,path):
        try:self.read(path)
        except FileNotFoundError:return False
        return True
    def create(self,path,raw,*,executable=False):
        a=self.api
        temporary=Path(path).with_name(Path(path).name+'.prepared-'+uuid.uuid4().hex)
        self._write_new(temporary,raw)
        with a.ancestors(path):
            # No replacement and no cross-volume copy. Partial bytes never take
            # a final marker name. Preserve prepared files on ambiguous failure.
            a.ok(a.MoveFileExW(local_path(temporary),local_path(path),8))
            try:self.sync_directory(Path(path).parent)
            except OSError as exc:raise RecordError('lifecycle-create-outcome-unknown') from exc
    def sync_directory(self,path):
        # No volume-wide flush or administrative privilege. If this OS/filesystem
        # cannot honor the directory flush, preserve the partial operation.
        a=self.api
        with a.ancestors(path),a.opened(path,access=0xc0020000) as h:
            require(a.state(h,path)['directory'],'windows-parent-not-directory');a.ok(a.FlushFileBuffers(h))
    def flush_file(self,fd):
        import msvcrt
        self.api.ok(self.api.FlushFileBuffers(msvcrt.get_osfhandle(fd)))
    def replace(self,path,raw,expected):
        a=self.api;require(self.read(path)==expected,'lifecycle-pointer-conflict')
        temporary=Path(path).with_name(Path(path).name+'.prepared-'+uuid.uuid4().hex);self.create(temporary,raw)
        with a.ancestors(path):
            require(self.read(path)==expected,'lifecycle-pointer-conflict')
            a.ok(a.MoveFileExW(local_path(temporary),local_path(path),9)) # REPLACE_EXISTING | WRITE_THROUGH, no copy
        try:
            self.sync_directory(Path(path).parent);require(self.read(path)==raw,'lifecycle-replace-unconfirmed')
        except (OSError,RecordError) as exc:raise RecordError('lifecycle-replace-durability-unknown') from exc
    def remove(self,path,expected):
        a=self.api
        with a.ancestors(path):
            require(self.read(path)==expected,'lifecycle-pointer-conflict');a.ok(a.DeleteFileW(local_path(path)))
        self.sync_directory(Path(path).parent)
    @contextmanager
    def exclusion(self,path,timeout=5,*,shared=False):
        require(type(timeout) in (int,float) and 0<timeout<=30,'invalid-lock-timeout');a=self.api
        with a.ancestors(path),a.opened(path,access=0x80020000 if shared else 0xc0020000,share=3,disposition=3) as h:
            before=a.state(h,path);a.private(h);require(not before['directory'] and before['links']==1,'unsafe-lifecycle-lock')
            overlap=a.Overlapped();deadline=time.monotonic()+timeout;locked=False
            try:
                while True:
                    if a.LockFileEx(h,1 if shared else 3,0,1,0,C.byref(overlap)):locked=True;break
                    error=C.get_last_error()
                    if error!=33:raise C.WinError(error)
                    if time.monotonic()>=deadline:raise RecordError('lifecycle-busy')
                    time.sleep(min(0.02,max(0,deadline-time.monotonic())))
                require(a.state(h,path)==before,'lifecycle-lock-replaced');yield
            finally:
                if locked:
                    primary=sys.exception()
                    try:a.ok(a.UnlockFileEx(h,0,1,0,C.byref(overlap)))
                    except OSError:
                        if primary is None:raise
                        primary.add_note('Native unlock failed; handle closure remains required.')


class NoticeReaderFiles(WindowsFiles):
    """Verify one inventory using live NTFS handles for its duration only."""

    def verify_runtime_inventory(self, root, expected, manifest_raw, manifest_sha256, *, cancelled=lambda: False):
        from ..updates.windows_payload import verify_pinned_inventory
        return verify_pinned_inventory(root, expected, manifest_raw, manifest_sha256, self, cancelled=cancelled)
