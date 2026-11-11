"""Managed CLI/desktop composition. No PATH fallback, setup or permission changes.

The native launcher chooses an immutable slot. The selected Python revalidates
that exact choice before opening authority, and every transaction retains the
runtime lease. A source fixture is not installed-entry qualification.
"""
from pathlib import Path
import argparse,platform,sqlite3,sys,uuid,hashlib,os
from .codec import decode_canonical,require,RecordError
from .management import ManagerHome
from .storage.authority import Authority
from .updates.lease import RuntimeLease,open_managed_store
from .adapters.git import Git,discover
from .binding import WorkspaceRegistration,resolve,require_registered
from .connection import Connections
from .workspace import LocalWorkspace


def process_runtime():return str(Path(sys.executable).absolute()),platform.python_version(),sqlite3.sqlite_version

def current_platform():
    require(not (sys.platform=='win32' and any(os.environ.get(k) for k in ('WSL_INTEROP','WSL_DISTRO_NAME'))),
            'wsl-native-interop-unqualified')
    machine=platform.machine().lower()
    if sys.platform=='darwin' and machine in ('arm64','aarch64'):return 'macos','arm64'
    if sys.platform=='win32' and machine in ('arm64','aarch64','amd64','x86_64'):return 'windows','arm64' if machine in ('arm64','aarch64') else 'x64'
    raise RecordError('runtime-platform-unavailable')

class ManagedAuthority(Authority):
    def __init__(self,root,*,project,slots,pointer,files):
        super().__init__(root,project=project,files=files);self.slots=slots;self.runtime_pointer=pointer
    def store(self,*,readonly=False):
        return open_managed_store(self,self.slots,readonly=readonly,expected_pointer=self.runtime_pointer)

def configured_git(home):
    path = home.root / 'tools.json'
    try:
        tools = decode_canonical(home.files.read(path))
    except FileNotFoundError:
        return None
    require(type(tools) is dict and set(tools) == {'version', 'git'} and tools['version'] == 1,
            'managed-tools-invalid')
    if tools['git'] is None:
        return None
    tool = tools['git']
    require(type(tool) is dict and set(tool) == {'path', 'sha256', 'version'}, 'managed-git-invalid')
    git = Git(Path(tool['path']))
    require(git.sha256 == tool['sha256'] and git.version == tool['version'], 'managed-git-changed')
    return git


class ManagedEntry:
    def __init__(self,root,*,pointer):
        os_name,architecture=current_platform()
        self.home=ManagerHome(root,os_name=os_name,architecture=architecture);self.pointer=pointer
        self.lease=RuntimeLease(self.home.slots,expected_pointer=pointer);slot=self.lease.verified
        manifest=decode_canonical(self.home.files.read(self.home.slots.root/'slots'/slot.slot/'manifest.json',4*1024*1024))
        require(process_runtime()==(slot.python,manifest['python_version'],manifest['sqlite_version']),'dedicated-runtime-mismatch')
        self.lease.check()
    def optional_features(self):
        from .execution.managed_factory import qualified_release
        with self.lease.hold():
            try:qualified_release(self)
            except RecordError as error:
                if error.code in ('execution-platform-unqualified','execution-qualified-runtime-required'):return frozenset()
                raise
            require(self.document_execution_readiness().get('assets_verified') is True,'execution-assets-unavailable')
            # Availability is not project opt-in or authorization for a run.
            return frozenset({'official-execution'})
    def require_document_execution(self):
        from .execution.managed_factory import qualified_release
        with self.lease.hold():return qualified_release(self)
    def document_execution(self,args,store,workspace,authority):
        from .execution.managed_factory import create_driver
        from .codec import decode_canonical
        with self.lease.hold():
            driver=create_driver(self,store,workspace,authority)
            if args.action=='prepare':
                value=decode_canonical(self.home.files.read(Path(args.request),1024*1024))
                require(type(value) is dict and set(value)=={'contract','request'},'execution-request-shape')
                return driver.prepare(operation=args.operation,run=args.run,contract=value['contract'],request=value['request'])
            require(args.action=='start','execution-action-unavailable')
            return driver.start(operation=args.operation,run=args.run,receipt=args.receipt,statement=args.statement)
    def run_document_delivery(self,args,store,workspace,authority):
        from .execution.managed_factory import create_driver
        with self.lease.hold():
            return create_driver(self,store,workspace,authority).delivery(operation=args.operation,delivery=args.delivery)
    def finish_document_delivery(self,args,store,workspace,authority):
        from .execution.driver import DocumentExecution
        from .execution.journal import ExecutionJournal
        from .work import WorkService
        from .platforms.effects_port import effects
        with self.lease.hold():
            driver=DocumentExecution(ExecutionJournal(WorkService(store,workspace)),lease=self.lease,
                effects=effects(workspace.root,authority.root),adapter=None)
            return driver.finish_delivery(operation=args.operation,delivery=args.delivery)
    def document_resolution(self,args,store,workspace,authority):
        from .execution.resolution import Resolution
        from .execution.journal import ExecutionJournal
        from .work import WorkService
        from .platforms.effects_port import effects
        from .platforms.darwin_execution import DarwinExecutionObservation
        require(current_platform()==('macos','arm64'),'execution-native-observer-unavailable')
        with self.lease.hold():
            journal=ExecutionJournal(WorkService(store,workspace))
            observer=DarwinExecutionObservation(journal,effects(workspace.root,authority.root))
            resolution=Resolution(journal,observer)
            if args.action=='resolve-preview':return resolution.preview(args.run)
            require(args.action=='resolve','execution-action-unavailable')
            return resolution.apply(operation=args.operation,run=args.run,receipt=args.receipt,statement=args.statement)
    def document_execution_readiness(self):
        from .execution.assets import inspect_assets
        with self.lease.hold():
            slot=self.home.slots.root/'slots'/self.pointer['slot']
            raw=self.home.files.read(slot/'manifest.json',4*1024*1024)
            require(hashlib.sha256(raw).hexdigest()==self.pointer['manifest_sha256'],'slot-manifest-mismatch')
            return inspect_assets(slot,decode_canonical(raw),self.home.files,platform=current_platform())

    def guide(self):
        with self.lease.hold():
            slot=self.home.slots.root/'slots'/self.pointer['slot']
            raw_manifest=self.home.files.read(slot/'manifest.json',4*1024*1024)
            require(hashlib.sha256(raw_manifest).hexdigest()==self.pointer['manifest_sha256'],'slot-manifest-mismatch')
            manifest=decode_canonical(raw_manifest)
            name='adapters/colvia-work/SKILL.md'
            matches=[row for row in manifest['inventory'] if row['path']==name]
            require(len(matches)==1,'managed-guide-unavailable')
            raw=self.home.files.read(slot/name,128*1024)
            require(len(raw)==matches[0]['size'] and hashlib.sha256(raw).hexdigest()==matches[0]['sha256'],'managed-guide-changed')
            return raw.decode('utf-8')
    def git(self):
        return configured_git(self.home)
    def workspace(self,root,*,readonly):
        from .cli import read_locator
        self.lease.check();git=self.git();topology=discover(root,git)
        root=Path(topology.root.path);locator=read_locator(root,git)
        authority=ManagedAuthority(self.home.root/'authorities'/locator.project,project=locator.project,
            slots=self.home.slots,pointer=self.pointer,files=self.home.files)
        require(authority.pointer_value()['instance']==locator.instance,'stale-or-foreign-binding')
        store=authority.store(readonly=readonly)
        try:
            connections=Connections(store);_,binding=connections.binding()
            registrations=connections.registrations(topology);resolution=resolve(locator,binding,topology,registrations)
            if resolution.registration_required:
                require(not readonly,'workspace-registration-required')
                registration=WorkspaceRegistration(str(uuid.uuid4()),topology.root,topology.gitdir)
                connections.register(operation='register-'+uuid.uuid4().hex,locator=locator,observed=topology,
                    workspace=registration,registrations=registrations,verify_topology=lambda:discover(root,git))
                workspace_id=registration.workspace
            else:workspace_id=require_registered(resolution)
            workspace=LocalWorkspace(store,root,workspace_id,git=git,locator_reader=lambda:read_locator(root,git))
            workspace.verify();self.lease.check();return authority,store,workspace
        except BaseException:store.close();raise

def main(argv=None):
    from .cli import main as product
    from .presentation import failure
    p=argparse.ArgumentParser(add_help=False,allow_abbrev=False)
    p.add_argument('--management-root',required=True);p.add_argument('--runtime-slot',required=True)
    p.add_argument('--runtime-manifest-sha256',required=True)
    prefix,rest=p.parse_known_args(argv)
    try:
        entry=ManagedEntry(Path(prefix.management_root),pointer=dict(slot=prefix.runtime_slot,manifest_sha256=prefix.runtime_manifest_sha256))
        return product(rest,entry=entry)
    except (RecordError,OSError,ValueError,TypeError) as exc:
        code=exc.code if isinstance(exc,RecordError) else 'runtime-access-unavailable'
        print(failure(code));return 2
