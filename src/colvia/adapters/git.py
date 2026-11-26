"""Read-only Git topology and index port with a caller-pinned executable.

No PATH fallback, fetch, index refresh, hook, checkout or Git metadata writes.
A future managed launcher resolves the qualified executable; this adapter never
starts an OS developer-tools installer to discover it.
"""
from contextlib import contextmanager, nullcontext
from dataclasses import dataclass
from pathlib import Path
import hashlib,os,stat,sys

from ..binding import Membership,Topology
from ..codec import RecordError,require
from ..tree import logical_path
from ..platforms.posix import open_directory,stamp
from ..platforms.observation_port import location,file_stamp
from ..platforms.process import run


def read_file(path:Path,limit:int,*,missing=None):
    if sys.platform=='win32':
        from ..platforms.windows_observation import Observer
        try:return Observer().read_file(path,limit)
        except FileNotFoundError:
            if missing is not None:return missing
            raise
    try:parent=open_directory(path.parent)
    except FileNotFoundError:
        if missing is not None:return missing
        raise
    try:
        try:fd=os.open(path.name,os.O_RDONLY|os.O_NOFOLLOW,dir_fd=parent)
        except FileNotFoundError:
            if missing is not None:return missing
            raise
        try:
            before=os.fstat(fd)
            require(stat.S_ISREG(before.st_mode) and before.st_nlink==1 and before.st_size<=limit,'unsafe-metadata-file')
            data=bytearray()
            while raw:=os.read(fd,min(65536,limit+1-len(data))):
                data.extend(raw);require(len(data)<=limit,'metadata-file-limit')
            require(stamp('',before)==stamp('',os.fstat(fd)) and
                    stamp('',before)==stamp('',os.stat(path.name,dir_fd=parent,follow_symlinks=False)),
                    'metadata-file-changed')
            return bytes(data)
        finally:os.close(fd)
    finally:os.close(parent)


def _text(raw):
    try:text=raw.decode('utf-8')
    except UnicodeError:raise RecordError('git-path-encoding-unavailable') from None
    require('\x00' not in text and '\n' not in text and '\r' not in text,'git-path-encoding-unavailable')
    return text


def _absolute(base,raw):
    path=Path(_text(raw))
    return Path(os.path.normpath(str(path if path.is_absolute() else base/path)))


@dataclass(frozen=True)
class IndexEntry:
    native_path:str
    path:str
    mode:str
    oid:str


def inspect_executable(executable):
    """Read the selected executable without launching it."""
    if sys.platform == 'win32':
        from ..platforms.windows_observation import Observer
        from ..storage.windows import local_path

        path = Path(local_path(executable))
        with Observer().opened_git_executable(path) as (observed, digest):
            canonical = Path(local_path(os.path.realpath(path, strict=True)))
            require(str(canonical).casefold() == str(path).casefold() and
                    file_stamp(canonical) == observed, 'git-executable-changed')
            return canonical, observed, digest

    path = Path(executable)
    require(path.is_absolute(), 'qualified-git-required')
    before = file_stamp(path)
    raw = read_file(path, 128 * 1024 * 1024)
    require(file_stamp(path) == before, 'git-executable-changed')
    require(bool(before.mode & 0o111), 'git-not-executable')
    return path, before, hashlib.sha256(raw).hexdigest()


class Git:
    def __init__(self,executable:Path,*,environment=None,expected_sha256=None,expected_stamp=None):
        self.executable, self.stamp, self.sha256 = inspect_executable(executable)
        require(expected_sha256 is None or self.sha256 == expected_sha256, 'managed-git-changed')
        require(expected_stamp is None or self.stamp == expected_stamp, 'git-registration-review-changed')
        self.env={k:v for k,v in (os.environ if environment is None else environment).items() if not k.startswith('GIT_')}
        self.env.update(GIT_OPTIONAL_LOCKS='0',GIT_NO_LAZY_FETCH='1',GIT_TERMINAL_PROMPT='0',GIT_PAGER='cat',LC_ALL='C')
        # A fixture may explicitly remove only user/system configuration, never
        # inject a foreign worktree/index/alternate object store through GIT_*.
        if environment is not None and environment.get('GIT_CONFIG_NOSYSTEM')=='1':
            self.env.update(GIT_CONFIG_NOSYSTEM='1',GIT_CONFIG_GLOBAL=os.devnull,GIT_CONFIG_SYSTEM=os.devnull)
        result=self._run(self.executable.parent,('--version',),limit=4096)
        self.version=_text(result.stdout.removesuffix(b'\n').removesuffix(b'\r'))
        require(self.version.startswith('git version '),'git-version-unavailable')

    @property
    def identity(self):return self.version+' sha256:'+self.sha256

    @contextmanager
    def guard_executable(self):
        guard = nullcontext()
        if sys.platform == 'win32':
            from ..platforms.windows_observation import Observer

            # Hold the selected name and ancestor handles through child execution.
            # Other hard-link names may change while this handle is held.
            guard = Observer().opened_git_executable(self.executable)
        with guard as observed:
            if observed is not None:
                require(observed == (self.stamp, self.sha256), 'git-executable-changed')
            require(file_stamp(self.executable) == self.stamp, 'git-executable-changed')
            yield
            require(file_stamp(self.executable) == self.stamp, 'git-executable-changed')

    def _run(self,root,args,*,allowed=(0,),input_bytes=b'',limit=64*1024*1024):
        with self.guard_executable():
            result=run([str(self.executable),'--no-optional-locks','-c','core.fsmonitor=false',
                        '-c','core.untrackedCache=false','-C',str(root),*args],cwd=root,env=self.env,
                       input_bytes=input_bytes,output_limit=limit)
        require(result.code in allowed,'git-observation-unavailable')
        return result

    def topology(self,target:Path):
        return self._topology(target, with_exclude=False)[0]

    def _topology(self,target:Path,*,with_exclude):
        target=Path(target);location(target)
        args=('rev-parse','--path-format=absolute','--show-toplevel','--absolute-git-dir',
              '--git-common-dir','--show-superproject-working-tree')
        limit=131072
        if with_exclude:
            args+=('--git-path','info/exclude')
            limit+=32768
        result=self._run(target,args,limit=limit)
        raw=result.stdout
        exclude_raw=None
        if with_exclude:
            # The superproject line is optional. Remove the final --git-path
            # line first so a submodule still fails the original topology check.
            raw,separator,exclude_raw=raw.removesuffix(b'\n').rpartition(b'\n')
            diagnostics=len(result.stderr)
            if not separator or not exclude_raw or len(raw)+1+diagnostics>131072 or len(exclude_raw)+1+diagnostics>32768:
                # Preserve the old independent output/error budgets if the
                # combined result cannot be partitioned unambiguously.
                topology=self.topology(target)
                return topology,self._info_exclude_path(Path(topology.root.path))
        lines=raw.splitlines()
        require(len(lines)==3,'nested-submodule-project-not-supported')
        root,gitdir,common=(_absolute(target,p) for p in lines)
        exclude=_absolute(root,exclude_raw) if exclude_raw is not None else None
        rootloc,gitloc,commonloc=location(root),location(gitdir),location(common)
        raw=self._run(root,('worktree','list','--porcelain','-z'),limit=8*1024*1024).stdout
        groups=raw.split(b'\0\0');members=[]
        for group in groups:
            if not group:continue
            fields=group.split(b'\0');first=fields[0]
            require(first.startswith(b'worktree '),'invalid-worktree-list')
            require(not any(f==b'bare' or f.startswith(b'prunable') for f in fields[1:]),'stale-or-bare-worktree')
            require(all(f.startswith((b'HEAD ',b'branch ',b'locked ')) or f in (b'detached',b'locked') for f in fields[1:]),
                    'unknown-worktree-field')
            member_root=_absolute(root,first[len(b'worktree '):]);memberloc=location(member_root)
            marker=member_root/'.git';info=marker.lstat()
            require(not stat.S_ISLNK(info.st_mode),'unsafe-git-marker')
            if stat.S_ISDIR(info.st_mode):member_git=marker
            else:
                data=read_file(marker,16384)
                require(data.startswith(b'gitdir: ') and data.endswith(b'\n') and data.count(b'\n')==1,'invalid-git-marker')
                member_git=_absolute(member_root,data[8:-1])
            member_gitloc=location(member_git)
            common_file=member_git/'commondir'
            data=read_file(common_file,16384,missing=b'')
            member_common=_absolute(member_git,data.rstrip(b'\n')) if data else member_git
            require(location(member_common)==commonloc,'foreign-worktree-common-dir')
            if data:
                backlink=read_file(member_git/'gitdir',16384)
                require(_absolute(member_git,backlink.rstrip(b'\n'))==marker,'worktree-backlink-mismatch')
            members.append(Membership(memberloc,member_gitloc))
            require(len(members)<=10000,'worktree-count-limit')
        require(raw==self._run(root,('worktree','list','--porcelain','-z'),limit=8*1024*1024).stdout,'git-topology-changed')
        return Topology('git',rootloc,commonloc,gitloc,tuple(members)),exclude

    def index(self,root:Path):
        raw=self._run(root,('ls-files','--stage','--full-name','-z')).stdout
        values={};aliases=set()
        for line in raw.split(b'\0'):
            if not line:continue
            parts=line.split(b'\t',1);require(len(parts)==2,'invalid-index-record')
            header=parts[0].split(b' ');require(len(header)==3,'invalid-index-record')
            mode,oid,stage=(_text(p) for p in header)
            require(stage=='0','unmerged-index')
            require(mode in ('100644','100755','120000','160000') and len(oid) in (40,64) and
                    all(c in '0123456789abcdef' for c in oid),'unsupported-index-entry')
            native=_text(parts[1]);path=logical_path(native)
            require(path.casefold() not in aliases,'index-path-collision')
            aliases.add(path.casefold());values[path]=IndexEntry(native,path,mode,oid)
            require(len(values)<=1_000_000,'index-entry-limit')
        return values

    def _global_ignore_path(self,root,*,has_configured_excludes=True):
        def line(raw):
            require(raw.endswith(b'\0'),'git-path-encoding-unavailable')
            return raw[:-1]
        def variable(name):
            values={v for k,v in self.env.items()
                    if (k.upper() if sys.platform=='win32' else k)==name}
            require(len(values)<=1,'git-global-ignore-location-unavailable')
            return next(iter(values),'')
        if has_configured_excludes:
            # Git owns interpretation of every configured path, including ones
            # using expanding syntax that depends on the pinned Git build.
            configured=self._run(root,('config','-z','--path','--get','core.excludesfile'),allowed=(0,1),limit=32768)
            if configured.code==0:
                return _absolute(root,line(configured.stdout))
        home,xdg=variable('HOME'),variable('XDG_CONFIG_HOME')
        if sys.platform=='win32' and not home and not xdg:
            # Git for Windows resolves its own home when the parent has no HOME.
            # Query the pinned Git with the same environment; do not inject one.
            expanded=self._run(root,('config','-z','--path','--default','~/.config/git/ignore',
                                    '--get','core.excludesfile'),limit=32768)
            path=Path(_text(line(expanded.stdout)))
            require(path.is_absolute(),'git-global-ignore-location-unavailable')
            return path
        base=xdg or str(Path(home)/'.config')
        require(Path(base).is_absolute(),'git-global-ignore-location-unavailable')
        return Path(base)/'git/ignore'

    def _info_exclude_path(self,root):
        info=self._run(root,('rev-parse','--path-format=absolute','--git-path','info/exclude'),limit=32768)
        return _absolute(root,info.stdout.rstrip(b'\n'))

    def policy(self,topology,inventory,*,info_path=None):
        from ..observation import Policy,PolicySource
        root=Path(topology.root.path)
        pattern=r'^(core\.(ignorecase|precomposeunicode|filemode|symlinks|excludesfile|sparsecheckout|sparsecheckoutcone)|extensions\.(worktreeconfig|partialclone))$'
        result=self._run(root,('config','--null','--show-origin','--get-regexp',pattern),allowed=(0,1),limit=1024*1024)
        fields=result.stdout.split(b'\0');require(fields[-1]==b'','invalid-git-config')
        fields=fields[:-1];require(len(fields)%2==0,'invalid-git-config')
        config=[]
        has_configured_excludes=False
        for n in range(0,len(fields),2):
            keyvalue=fields[n+1].split(b'\n',1);require(len(keyvalue)==2,'invalid-git-config')
            origin,key,value=_text(fields[n]),_text(keyvalue[0]),_text(keyvalue[1])
            # Git renders the same common config relatively in the primary checkout
            # and absolutely in a linked worktree. Preserve the exact resolved
            # origin and value; never drop origin or merge different overrides.
            if origin.startswith('file:'):origin='file:'+str(_absolute(root,origin[5:].encode('utf-8')))
            config.append((origin+' '+key,value))
            if key=='core.excludesfile':
                has_configured_excludes=True
            if key in ('core.sparsecheckout','core.sparsecheckoutcone'):
                require(value.lower() in ('false','no','off','0'),'sparse-worktree-not-supported')
            if key=='extensions.partialclone':raise RecordError('partial-clone-not-supported')
        config.extend((('forced:core.fsmonitor','false'),('forced:core.untrackedcache','false')))
        global_path=self._global_ignore_path(root,has_configured_excludes=has_configured_excludes)
        if info_path is None:
            info_path=self._info_exclude_path(root)
        sources=[PolicySource('global:'+str(global_path),read_file(global_path,4*1024*1024,missing=b'')),
                 PolicySource('git:info/exclude',read_file(info_path,4*1024*1024,missing=b''))]
        paths=sorted((s.native_path for s in inventory if Path(s.native_path).name=='.gitignore'),
                     key=lambda p:(p.count('/'),p.encode('utf-8')))
        for native in paths:
            sources.append(PolicySource('workspace:'+logical_path(native),read_file(root/native,4*1024*1024)))
        return Policy(tuple(sources),tuple(config),self.identity)

    def tracked_for_creation(self, root):
        """Include staged deletions which vanished from the index but still exist in HEAD."""
        paths = set(self.index(root))
        head = self._run(root, ('rev-parse','--verify','--quiet','HEAD^{tree}'), allowed=(0,1))
        if head.code == 0:
            tree = _text(head.stdout.strip())
            require(len(tree) in (40,64) and all(c in '0123456789abcdef' for c in tree), 'invalid-git-tree')
            files = self._run(root, ('ls-tree','-rz','--name-only',tree)).stdout
            paths.update(logical_path(_text(raw)) for raw in files.split(b'\0') if raw)
        return paths

    def ignored(self,root:Path,native_paths):
        result=set();batch=[];size=0
        def flush():
            if not batch:return
            output=self._run(root,('check-ignore','--no-index','-z','--stdin'),allowed=(0,1),
                             input_bytes=b'\0'.join(batch)+b'\0').stdout
            for raw in output.split(b'\0'):
                if raw:result.add(logical_path(_text(raw)))
        for path in native_paths:
            raw=path.encode('utf-8');require(b'\0' not in raw,'invalid-path')
            if size+len(raw)>65536:flush();batch=[];size=0
            batch.append(raw);size+=len(raw)+1
        flush();return frozenset(result)


def discover(target:Path,git:Git|None,*,with_exclude=False):
    """Plain folders need no Git executable. Ambiguous markers never become plain."""
    target=Path(target);location(target)
    for parent in (target,*target.parents):
        marker=parent/'.git'
        if os.path.lexists(marker):
            require(git is not None,'git-prerequisite-required')
            if with_exclude:return git._topology(target,with_exclude=True)
            return git.topology(target)
        if (parent/'HEAD').is_file() and (parent/'objects').is_dir() and (parent/'refs').is_dir():
            raise RecordError('bare-or-ambiguous-git-root')
    topology=Topology('plain',location(target))
    return (topology,None) if with_exclude else topology
