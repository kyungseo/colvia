"""Authority-backed project/workspace registration without locator file writes.

Connection is an explicit caller-authorized operation. The recorded same-project
registration policy lets a later verified linked workspace acquire its distinct
identity without re-approving the already agreed project connection. It cannot
bind a clone, move, new instance or unregistered Git topology.
"""
from dataclasses import asdict

from .binding import (Locator,NativeLocation,ProjectBinding,WorkspaceRegistration,
                      resolve,require_registered,same_plain_location)
from .codec import Edge,decode_envelope,encode_envelope,require
from .graph import Schema
from .storage.sqlite import _token

PROJECT_KEY='project:binding'


def native(value):
    require(type(value) is dict and set(value)=={'path','volume','file_id'},'invalid-native-record')
    return NativeLocation(**value)


def binding_payload(value):
    require(set(value)=={'locator','kind','location','registration_policy','links'} and value['links']=={},'invalid-binding-record')
    require(value['registration_policy']=='same-project','unknown-registration-policy')
    from .codec import canonical_bytes
    locator=Locator.parse(canonical_bytes(value['locator']),kind=value['kind'])
    return ProjectBinding(locator,value['kind'],native(value['location']))


def workspace_payload(value):
    require(set(value)=={'workspace','root','gitdir','links'} and value['links']=={'project':[0]},'invalid-workspace-record')
    return WorkspaceRegistration(value['workspace'],native(value['root']),None if value['gitdir'] is None else native(value['gitdir']))


def rebind_payload(p):
    from .binding import _uuid
    require(set(p)=={'instance','statement','links'} and type(p['statement']) is str and 0<len(p['statement'])<=16384,
            'invalid-rebind-record')
    _uuid(p['instance'])
    require(p['links']=={'old':[0],'new':[1]},'invalid-rebind-links')


def connection_schemas():
    return [Schema('project.binding',1,{},binding_payload,{}),
            Schema('workspace.registration',1,{'project':'decision'},workspace_payload,{'project':frozenset({'project.binding'})}),
            Schema('connection.rebind',1,{'old':'decision','new':'decision'},rebind_payload,
                   {'old':frozenset({'project.binding'}),'new':frozenset({'project.binding'})})]


def workspace_key(workspace):
    from .binding import _uuid
    _uuid(workspace);return 'workspace:'+workspace


def location_key(root):
    import hashlib
    from .codec import canonical_bytes
    return 'workspace-location:'+hashlib.sha256(canonical_bytes(asdict(root))).hexdigest()


class Connections:
    def __init__(self,store):self.store=store

    def binding(self):
        ref=self.store.head(PROJECT_KEY);require(ref is not None,'project-not-connected')
        obj=decode_envelope(ref,self.store.load(ref));connection_schemas()[0].check(obj)
        bound=binding_payload(obj.payload)
        require(bound.locator.project==self.store.project and bound.locator.instance==self.store.instance,'authority-binding-mismatch')
        return ref,bound

    def workspace(self,workspace):
        ref=self.store.head(workspace_key(workspace));require(ref is not None,'workspace-registration-required')
        obj=decode_envelope(ref,self.store.load(ref));connection_schemas()[1].check(obj)
        project,bound=self.binding()
        require(obj.edges[0].ref==project,'workspace-binding-stale')
        return ref,workspace_payload(obj.payload),bound

    def connect(self,*,operation,binding,observed,workspace,verify_topology):
        require(binding.locator.project==self.store.project and binding.locator.instance==self.store.instance,'authority-binding-mismatch')
        require(workspace.root==observed.root and workspace.gitdir==observed.gitdir,'workspace-location-changed')
        require_registered(resolve(binding.locator,binding,observed,(workspace,)))
        project,praw=encode_envelope('project.binding',1,
            dict(locator=binding.locator.payload(),kind=binding.kind,location=asdict(binding.location),registration_policy='same-project',links={}))
        wref,wraw=encode_envelope('workspace.registration',1,
            dict(workspace=workspace.workspace,root=asdict(workspace.root),gitdir=asdict(workspace.gitdir) if workspace.gitdir else None,links={'project':[0]}),
            (Edge('decision',project),))
        objects=[(project,praw),(wref,wraw)]
        def validate(load):
            from .effects import guard
            guard(load)
            require(verify_topology()==observed,'workspace-observation-changed')
            for schema,(ref,raw) in zip(connection_schemas(),objects):schema.check(decode_envelope(ref,load(ref)))
        self.store.commit_heads(operation=operation,expected={PROJECT_KEY:None,workspace_key(workspace.workspace):None,location_key(workspace.root):None},
            changes={PROJECT_KEY:project,workspace_key(workspace.workspace):wref,location_key(workspace.root):wref},objects=objects,validate=validate)
        return project,wref

    def rebind_restored(self,*,operation,binding,observed,workspace,statement,expected_binding,verify_topology):
        """Explicit local identity decision; no locator file write or grant replay."""
        require(self.store.needs_rebind(),'instance-rebind-not-pending')
        old_ref=self.store.head(PROJECT_KEY)
        require(old_ref is not None and old_ref==expected_binding,'restore-binding-changed')
        old_obj=decode_envelope(old_ref,self.store.load(old_ref));connection_schemas()[0].check(old_obj)
        old=binding_payload(old_obj.payload)
        require(binding.locator.project==self.store.project and binding.locator.instance==self.store.instance and
                old.locator.project==self.store.project and old.locator.instance!=self.store.instance,
                'authority-binding-mismatch')
        require(binding.kind==old.kind and binding.locator.epoch==old.locator.epoch+1 and
                binding.locator.nonce!=old.locator.nonce,'invalid-restore-rebind')
        require(workspace.root==observed.root and workspace.gitdir==observed.gitdir,'workspace-location-changed')
        require_registered(resolve(binding.locator,binding,observed,(workspace,)))
        project,praw=encode_envelope('project.binding',1,
            dict(locator=binding.locator.payload(),kind=binding.kind,location=asdict(binding.location),registration_policy='same-project',links={}))
        wref,wraw=encode_envelope('workspace.registration',1,
            dict(workspace=workspace.workspace,root=asdict(workspace.root),gitdir=asdict(workspace.gitdir) if workspace.gitdir else None,links={'project':[0]}),
            (Edge('decision',project),))
        decision,draw=encode_envelope('connection.rebind',1,
            dict(instance=self.store.instance,statement=statement,links={'old':[0],'new':[1]}),
            (Edge('decision',old_ref),Edge('decision',project)))
        wk=workspace_key(workspace.workspace);lk=location_key(workspace.root);local=self.store.head(lk)
        objects=[(project,praw),(wref,wraw),(decision,draw)]
        def validate(view):
            from .effects import guard
            guard(view);require(verify_topology()==observed,'workspace-observation-changed')
            for schema,(ref,_) in zip(connection_schemas(),objects):schema.check(decode_envelope(ref,view(ref)))
        self.store.commit_heads(operation=operation,
            expected={PROJECT_KEY:old_ref,wk:None,lk:local,'restore:rebind':self.store.head('restore:rebind')},
            changes={PROJECT_KEY:project,wk:wref,lk:wref,'restore:rebind':decision},objects=objects,validate=validate,_rebind=True)
        return project,wref

    def register(self,*,operation,locator,observed,workspace,registrations,verify_topology):
        project,bound=self.binding()
        require(bound.kind=='git','new-plain-workspace-not-supported')
        require(workspace.root==observed.root and workspace.gitdir==observed.gitdir,'workspace-location-changed')
        resolution=resolve(locator,bound,observed,registrations)
        require(resolution.registration_required,'workspace-already-registered')
        key=workspace_key(workspace.workspace)
        # A stable location key is a uniqueness/CAS guard shared by concurrent
        # registration attempts with different proposed workspace IDs.
        identity_key=location_key(workspace.root)
        wref,wraw=encode_envelope('workspace.registration',1,
            dict(workspace=workspace.workspace,root=asdict(workspace.root),gitdir=asdict(workspace.gitdir),links={'project':[0]}),
            (Edge('decision',project),))
        def validate(load):
            from .effects import guard
            guard(load)
            require(verify_topology()==observed,'workspace-observation-changed')
            require(load.head(PROJECT_KEY)==project,'project-binding-changed')
            connection_schemas()[1].check(decode_envelope(wref,load(wref)))
        self.store.commit_heads(operation=operation,expected={key:None,identity_key:None},
            changes={key:wref,identity_key:wref},objects=[(wref,wraw)],validate=validate)
        return wref

    def registrations(self,topology,*,current_only=False):
        """Resolve only current Git members, without scanning all Work heads."""
        project,bound=self.binding();values=[]
        if topology.kind==bound.kind=='plain':
            # The locator already names exactly one workspace. Resolve that head,
            # then verify its ORIGINAL location index; never rewrite or search
            # other heads to accommodate Windows path spelling.
            ref=self.store.head(workspace_key(bound.locator.workspace))
            require(ref is not None,'workspace-registration-required')
            obj=decode_envelope(ref,self.store.load(ref));connection_schemas()[1].check(obj)
            require(obj.edges[0].ref==project,'workspace-binding-stale')
            value=workspace_payload(obj.payload)
            require(value.workspace==bound.locator.workspace and value.gitdir is None and
                    same_plain_location(value.root,bound.location) and
                    self.store.head(location_key(value.root))==ref,'workspace-location-index-mismatch')
            if not same_plain_location(value.root,topology.root):return ()
            return (value,)
        gitdirs={m.root:m.gitdir for m in topology.members} if topology.kind=='git' else {topology.root:topology.gitdir}
        for root in gitdirs:
            ref=self.store.head(location_key(root))
            if ref is None:continue
            obj=decode_envelope(ref,self.store.load(ref));connection_schemas()[1].check(obj)
            value=workspace_payload(obj.payload);require(value.root==root,'workspace-location-index-mismatch')
            require(self.store.head(workspace_key(value.workspace))==ref,'workspace-location-index-mismatch')
            owner=obj.edges[0].ref
            if current_only and owner!=project:
                old=decode_envelope(owner,self.store.load(owner));connection_schemas()[0].check(old)
                prior=binding_payload(old.payload).locator
                require(prior.project==bound.locator.project and prior.instance!=bound.locator.instance,
                        'workspace-binding-stale')
                continue
            require(owner==project,'workspace-binding-stale')
            if current_only:
                require(value.gitdir==gitdirs[root],'workspace-location-changed')
            values.append(value)
        return tuple(values)
