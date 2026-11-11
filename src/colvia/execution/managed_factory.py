"""Source-owned managed composition; qualification is not inferred from hashes.

An installed release must explicitly qualify its runtime binaries, Python inventory and fixed policy.
This source candidate intentionally declares none. Tests may supply synthetic
release records through the Python test boundary, never a CLI import/port option.
Ordinary Work remains available independently of this optional engine.
"""
import hashlib,io,os,uuid
from pathlib import Path
from types import SimpleNamespace
from ..codec import decode_canonical,require
from ..bodies import ingest_body
from ..maps import build_map
from ..work import WorkService
from ..records import head_summary
from .journal import ExecutionJournal
from .driver import DocumentExecution
from . import schema

# Add only after the exact runtime/configuration and installed host have been
# qualified. An empty table must not be populated by discovery or user input.
QUALIFIED_RUNTIME_KEYS=frozenset()

def qualified_release(entry):
    from ..managed_entry import current_platform
    require(current_platform()==('macos','arm64'),'execution-platform-unqualified')
    require(bool(QUALIFIED_RUNTIME_KEYS),'execution-qualified-runtime-required')
    entry.lease.check()
    raw=entry.home.files.read(entry.home.root/'execution-runtime.json',4*1024*1024)
    value=decode_canonical(raw)
    require(type(value) is dict and set(value)=={'version','bindings','digests','inventories','qualified','model'} and
            type(value['version']) is int and value['version']==1,'execution-runtime-configuration')
    require(all(type(value[k]) is dict for k in ('bindings','digests','inventories','qualified')) and type(value['model']) is str,'execution-runtime-configuration')
    from ..platforms.darwin_runtime_policy import POLICY_SHA256
    require(schema.digest(dict(qualified=value['qualified'],python=value['inventories'].get('PYROOT'),policy=POLICY_SHA256)) in QUALIFIED_RUNTIME_KEYS,
            'execution-qualified-runtime-required')
    return value

class NativeAdapter:
    def __init__(self,entry,journal,authority,effects,release):
        from ..platforms.darwin_execution import DarwinExecutionObservation
        from ..platforms.darwin_document_backend import DarwinDocumentBackend
        from ..platforms.darwin_runtime_launch import DarwinRuntimeLaunch
        from ..platforms.darwin_runtime_policy import POLICY_SHA256
        from ..adapters.codex_documents import Policy
        self.entry=entry;self.journal=journal;self.release=release;self.effects=effects
        slot=entry.home.slots.root/'slots'/entry.pointer['slot']
        bindings=release['bindings']
        # Dedicated worker Python and packaged resources come only from the
        # selected immutable slot; the external model runtime is separately pinned.
        self.resources={'python_digest':Path(entry.lease.verified.python),
            'worker_digest':slot/'execution/document-worker.pyz','parser_digest':slot/'execution/marked.umd.js',
            'profile_digest':slot/'execution/worker.sb.in','runtime_digest':Path(bindings['BIN'])}
        from ..platforms.darwin_runtime_policy import canonical_existing
        self.python_root=canonical_existing(bindings['PYROOT'],True)
        require(self.python_root.is_relative_to(slot) and self.python_root!=slot,'execution-python-slot-required')
        require(Path(entry.lease.verified.python).is_relative_to(self.python_root),'execution-python-tree-mismatch')
        self.launch=DarwinRuntimeLaunch(bindings=bindings,digests=release['digests'],inventories=release['inventories'],
            qualified=release['qualified'],policy_path=slot/'execution/runtime.sb',
            authority_root=authority.root,home=str(Path.home()))
        self.policy=Policy(model=release['model'],runtime_digest=release['digests']['BIN'],
            policy_digest=POLICY_SHA256,runtime_binding_digest=self.launch.identity())
        observer=DarwinExecutionObservation(journal,effects)
        self.backend=DarwinDocumentBackend(journal,observer,self.resources,self.python_root)
    def qualify(self):
        require(qualified_release(self.entry)==self.release,'execution-runtime-qualification-changed')
        value=self.entry.document_execution_readiness()
        require(value.get('assets_verified') is True,'execution-assets-unavailable')
    def _check(self,contract):
        from ..platforms.darwin_execution_inputs import resource_digest
        self.policy.bind(contract)
        require(contract['target']==str(self.effects.root),'execution-target-registration-mismatch')
        require(all(resource_digest(path)==contract['scope']['resources'][name] for name,path in self.resources.items()),'execution-resource-drift')
        self.launch.prepare(SimpleNamespace(payload={'contract':contract}),self.policy)
    def material(self,contract,request):
        self._check(contract);schema.request_record(request,contract)
        _,head=self.journal.service._head(contract['scope']['work_id']);_,plan,_,_=head_summary(head.ref,self.journal.store.load)
        output=Path(contract['scope']['documents'][contract['scope']['output_id']]['path'])
        require(output.is_relative_to(self.effects.root) and str(output.relative_to(self.effects.root)) in plan.payload['scope'],
                'execution-output-outside-scope')
        bodies={}
        for name,item in contract['scope']['documents'].items():
            identity,raw=self.backend.observer.document_bytes(item['path'])
            require(identity==item['original_identity'],'execution-document-drift');bodies[name]=raw
        # Reject secret/identifier patterns before importing source bodies.
        from .documents import prepare_views
        import time
        prepare_views(contract,bodies,request['prompt'],deadline=time.monotonic()+30)
        operation='execution-input-'+uuid.uuid4().hex;self.journal.store.begin_import(operation,'execution-input')
        objects=[];refs=[]
        for name,raw in bodies.items():
            body=ingest_body(io.BytesIO(raw),self.journal.store,operation);objects.append(body);refs.append((name,body[0]))
        mapping=build_map(refs)
        return dict(bodies=mapping.root,objects=[*objects,*mapping.objects],import_id=operation)
    def ports(self,grant):
        from ..platforms.darwin_processes import DarwinProcesses
        from ..platforms.runtime_channel import RuntimeChannel
        from ..platforms.worker_stdio import exchange
        from ..adapters.document_session import DocumentSession
        self._check(grant.payload['contract'])
        return dict(backend=self.backend,launch=self.launch,policy=self.policy,
            runtime_processes=DarwinProcesses(),worker_processes=DarwinProcesses(),
            channel_factory=RuntimeChannel,session_factory=DocumentSession,worker_exchange=exchange)

def create_driver(entry,store,workspace,authority):
    release=qualified_release(entry)
    from ..platforms.effects_port import effects
    native=effects(workspace.root,authority.root);journal=ExecutionJournal(WorkService(store,workspace))
    adapter=NativeAdapter(entry,journal,authority,native,release)
    return DocumentExecution(journal,lease=entry.lease,effects=native,adapter=adapter)
