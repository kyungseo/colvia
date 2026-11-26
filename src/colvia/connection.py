"""Authority-backed project/workspace registration without locator file writes.

Connection is an explicit caller-authorized operation. The recorded same-project
registration policy lets a later verified linked workspace acquire its distinct
identity without re-approving the already agreed project connection. It cannot
bind a clone, move, new instance or unregistered Git topology.
"""
from dataclasses import asdict

from .binding import (Locator,NativeLocation,ProjectBinding,WorkspaceRegistration,
                      resolve,require_registered,same_plain_location,persistent)
from .codec import Edge,decode_envelope,encode_envelope,require
from .graph import Schema
from . import connection_identity as identities
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
    from .git_transition_record import schema as transition_schema
    return [Schema('project.binding',1,{},binding_payload,{}),
            Schema('workspace.registration',1,{'project':'decision'},workspace_payload,{'project':frozenset({'project.binding'})}),
            Schema('connection.rebind',1,{'old':'decision','new':'decision'},rebind_payload,
                   {'old':frozenset({'project.binding'}),'new':frozenset({'project.binding'})}),
            identities.schema(), identities.move_schema(), transition_schema()]


def workspace_key(workspace):
    from .binding import _uuid
    _uuid(workspace);return 'workspace:'+workspace


def location_key(root):
    import hashlib
    from .codec import canonical_bytes
    return 'workspace-location:'+hashlib.sha256(canonical_bytes(asdict(root))).hexdigest()


class Connections:
    def __init__(self,store):self.store=store

    def binding_record(self):
        ref=self.store.head(PROJECT_KEY);require(ref is not None,'project-not-connected')
        obj=decode_envelope(ref,self.store.load(ref));connection_schemas()[0].check(obj)
        bound=binding_payload(obj.payload)
        require(bound.locator.project==self.store.project and bound.locator.instance==self.store.instance,'authority-binding-mismatch')
        return ref,bound

    def _effective(self, ref, resolved):
        if resolved is None:
            return identities.effective(ref, self.store.load)
        if ref in resolved:
            return resolved[ref]
        value = identities.effective(ref, self.store.load)
        if len(resolved) < 256:
            resolved[ref] = value
        return value

    def binding(self, *, _resolved=None):
        ref,bound=self.binding_record()
        anchor=self.store.head(identities.PROJECT_IDENTITY)
        if anchor is not None:
            project,wref,current,workspace=self._effective(anchor,_resolved)
            if project==ref:
                require(self.store.head(workspace_key(workspace.workspace))==wref and
                        self.store.head(identities.identity_key(workspace.workspace))==anchor and
                        self.store.head(location_key(workspace.root))==wref,'connection-identity-index-mismatch')
                return ref,current
        require(not persistent(bound.location),'connection-identity-required')
        return ref,bound

    def workspace_record(self,workspace,project=None):
        ref=self.store.head(workspace_key(workspace));require(ref is not None,'workspace-registration-required')
        obj=decode_envelope(ref,self.store.load(ref));connection_schemas()[1].check(obj)
        project=project or self.binding_record()[0]
        require(obj.edges[0].ref==project,'workspace-binding-stale')
        value=workspace_payload(obj.payload)
        require(value.workspace==workspace and self.store.head(location_key(value.root))==ref,
                'workspace-location-index-mismatch')
        return ref,value

    def identity(self,workspace_ref,*,_resolved=None):
        obj=decode_envelope(workspace_ref,self.store.load(workspace_ref));connection_schemas()[1].check(obj)
        registration=workspace_payload(obj.payload)
        ref=self.store.head(identities.identity_key(registration.workspace))
        if ref is not None:
            project,actual,_,current=self._effective(ref,_resolved)
            require(actual==workspace_ref and project==self.store.head(PROJECT_KEY) and
                    self.store.head(workspace_key(current.workspace))==actual and
                    self.store.head(location_key(registration.root))==actual and
                    self.store.head(location_key(current.root))==actual,'connection-identity-index-mismatch')
        else:require(not persistent(registration.root),'connection-identity-required')
        return ref

    def workspace(self,workspace,*,_resolved=None):
        project,bound=self.binding(_resolved=_resolved)
        ref,value=self.workspace_record(workspace,project)
        anchor=self.identity(ref,_resolved=_resolved)
        if anchor is not None:
            _,_,current,value=self._effective(anchor,_resolved)
            require(current==bound,'connection-identity-binding-mismatch')
        return ref,value,bound

    def _initial_identity(self,operation,project,wref,binding,workspace,*,primary):
        if not any(persistent(v) for v in (binding.location,workspace.root,workspace.gitdir)):
            return {},[]
        common=None
        project_anchor=self.store.head(identities.PROJECT_IDENTITY) if not primary else None
        if not primary and binding.kind=='git' and (
                not persistent(self.binding_record()[1].location) or
                (project_anchor is not None and project_anchor.version == 2)):
            common=project_anchor
            require(common is not None,'connection-identity-required')
        anchor=identities.create(operation,project,wref,identities.values(binding,workspace),common=common)
        heads={identities.identity_key(workspace.workspace):anchor[0]}
        if primary:heads[identities.PROJECT_IDENTITY]=anchor[0]
        return heads,[anchor]

    def revalidate(self,*,operation,project,updates,primary,receipt,statement,verify):
        expected={PROJECT_KEY:project,identities.PROJECT_IDENTITY:None};changes={};objects=[]
        for wref,workspace,locations in updates:
            anchor=identities.create(operation,project,wref,locations,receipt=receipt,statement=statement)
            key=identities.identity_key(workspace.workspace);alias=location_key(locations['root'])
            require(alias not in expected,'connection-identity-index-conflict')
            expected.update({key:None,alias:None,workspace_key(workspace.workspace):wref,location_key(workspace.root):wref})
            changes.update({key:anchor[0],alias:wref})
            if workspace.workspace==primary:changes[identities.PROJECT_IDENTITY]=anchor[0]
            objects.append(anchor)
        require(identities.PROJECT_IDENTITY in changes,'connection-identity-primary-required')
        def validate(view):
            from .effects import guard
            guard(view)
            require(verify()==view.root().ref,'identity-review-changed')
            for ref,_ in objects:identities.evidence(ref,view)
        self.store.commit_heads(operation=operation,expected=expected,changes=changes,objects=objects,
                                validate=validate,_no_active_imports=True)
        return changes

    def connect(self,*,operation,binding,observed,workspace,verify_topology):
        require(binding.locator.project==self.store.project and binding.locator.instance==self.store.instance,'authority-binding-mismatch')
        require(workspace.root==observed.root and workspace.gitdir==observed.gitdir,'workspace-location-changed')
        require_registered(resolve(binding.locator,binding,observed,(workspace,)))
        project,praw=encode_envelope('project.binding',1,
            dict(locator=binding.locator.payload(),kind=binding.kind,location=asdict(binding.location),registration_policy='same-project',links={}))
        wref,wraw=encode_envelope('workspace.registration',1,
            dict(workspace=workspace.workspace,root=asdict(workspace.root),gitdir=asdict(workspace.gitdir) if workspace.gitdir else None,links={'project':[0]}),
            (Edge('decision',project),))
        additions,anchors=self._initial_identity(operation,project,wref,binding,workspace,primary=True)
        objects=[(project,praw),(wref,wraw),*anchors]
        def validate(load):
            from .effects import guard
            guard(load)
            require(verify_topology()==observed,'workspace-observation-changed')
            for schema,(ref,raw) in zip(connection_schemas(),objects[:2]):schema.check(decode_envelope(ref,load(ref)))
            for ref,_ in anchors:identities.evidence(ref,load)
        self.store.commit_heads(operation=operation,expected={PROJECT_KEY:None,workspace_key(workspace.workspace):None,location_key(workspace.root):None,**dict.fromkeys(additions)},
            changes={PROJECT_KEY:project,workspace_key(workspace.workspace):wref,location_key(workspace.root):wref,**additions},objects=objects,validate=validate)
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
        additions,anchors=self._initial_identity(operation,project,wref,binding,workspace,primary=True)
        objects=[(project,praw),(wref,wraw),(decision,draw),*anchors]
        def validate(view):
            from .effects import guard
            guard(view);require(verify_topology()==observed,'workspace-observation-changed')
            for schema,(ref,_) in zip(connection_schemas(),objects[:3]):schema.check(decode_envelope(ref,view(ref)))
            for ref,_ in anchors:identities.evidence(ref,view)
        self.store.commit_heads(operation=operation,
            expected={PROJECT_KEY:old_ref,wk:None,lk:local,'restore:rebind':self.store.head('restore:rebind'),**{k:self.store.head(k) for k in additions}},
            changes={PROJECT_KEY:project,wk:wref,lk:wref,'restore:rebind':decision,**additions},objects=objects,validate=validate,_rebind=True)
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
        additions,anchors=self._initial_identity(operation,project,wref,bound,workspace,primary=False)
        def validate(load):
            from .effects import guard
            guard(load)
            require(self.binding()==(project,bound),'project-binding-changed')
            require(verify_topology()==observed,'workspace-observation-changed')
            require(load.head(PROJECT_KEY)==project,'project-binding-changed')
            connection_schemas()[1].check(decode_envelope(wref,load(wref)))
            for ref,_ in anchors:identities.evidence(ref,load)
        self.store.commit_heads(operation=operation,expected={key:None,identity_key:None,**dict.fromkeys(additions)},
            changes={key:wref,identity_key:wref,**additions},objects=[(wref,wraw),*anchors],validate=validate)
        return wref

    def registrations(self,topology,*,current_only=False,complete=False,_resolved=None):
        """Resolve only current Git members, without scanning all Work heads."""
        project,bound=self.binding(_resolved=_resolved);values=[]
        if topology.kind==bound.kind=='plain':
            # The locator already names exactly one workspace. Resolve that head,
            # then verify its ORIGINAL location index; never rewrite or search
            # other heads to accommodate Windows path spelling.
            _,value,_=self.workspace(bound.locator.workspace,_resolved=_resolved)
            require(value.gitdir is None and same_plain_location(value.root,bound.location),
                    'workspace-location-index-mismatch')
            return (value,) if same_plain_location(value.root,topology.root) else ()
        gitdirs={m.root:m.gitdir for m in topology.members} if topology.kind=='git' else {topology.root:topology.gitdir}
        if complete:
            # Before admitting a new registration or an independent project,
            # prove that a missing derived alias did not hide a live member.
            from .maps import scan_map
            by_path={root.path:root for root in gitdirs}
            move=self.store.head(identities.PROJECT_IDENTITY)
            primary=None
            if move is not None and move.version==2:
                p,w,_,effective=self._effective(move,_resolved)
                if p==project:primary=(w,effective.root)
            for key,ref in scan_map(self.store.root().heads,self.store.load):
                if not key.startswith('workspace:'):
                    continue
                obj=decode_envelope(ref,self.store.load(ref));connection_schemas()[1].check(obj)
                if obj.edges[0].ref!=project:
                    continue
                registration=workspace_payload(obj.payload)
                path=primary[1].path if primary is not None and primary[0]==ref else registration.root.path
                root=by_path.get(path)
                if root is not None:
                    _,effective,_=self.workspace(registration.workspace,_resolved=_resolved)
                    require(effective.root==root and effective.gitdir==gitdirs[root] and
                            self.store.head(location_key(root))==ref,'workspace-location-index-mismatch')
        for root in gitdirs:
            ref=self.store.head(location_key(root))
            if ref is None:continue
            obj=decode_envelope(ref,self.store.load(ref));connection_schemas()[1].check(obj)
            value=workspace_payload(obj.payload)
            require(self.store.head(workspace_key(value.workspace))==ref,'workspace-location-index-mismatch')
            owner=obj.edges[0].ref
            if current_only and owner!=project:
                old=decode_envelope(owner,self.store.load(owner));connection_schemas()[0].check(old)
                prior=binding_payload(old.payload).locator
                require(prior.project==bound.locator.project and prior.instance!=bound.locator.instance,
                        'workspace-binding-stale')
                continue
            require(owner==project,'workspace-binding-stale')
            _,value,_=self.workspace(value.workspace,_resolved=_resolved)
            require(value.root==root,'workspace-location-index-mismatch')
            if current_only:
                require(value.gitdir==gitdirs[root],'workspace-location-changed')
            values.append(value)
        return tuple(values)
