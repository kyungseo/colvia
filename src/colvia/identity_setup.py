"""Manager-only approval and restart for exact legacy location revalidation."""
from contextlib import closing
from pathlib import Path

from . import connection_identity as identities
from .adapters.git import discover, read_file
from .binding import Locator, legacy_darwin, revalidates
from .codec import ObjectRef, canonical_bytes, decode_canonical, decode_envelope, require
from .connection import Connections, PROJECT_KEY, connection_schemas, native
from .connection_boundary import (ConnectionBoundaryError, _ancestor_ids, _identity,
                                  _integration_workspace, occupied)
from .effects import guard
from .maps import map_get, scan_map
from .project_setup import ProjectSetup, sha, topology_value
from .records import link
from .platforms.observation_port import directory_location
from .storage.sqlite import _token

_LIMIT = 8 * 1024 * 1024


class IdentitySetup(ProjectSetup):
    def _candidate(self, store, project, binding, integration):
        # An incomplete connect, detach or restored instance is not revalidated.
        guard(store)
        require(not store.has_active_imports(),'identity-import-pending')
        require(legacy_darwin(binding.location) and integration[0] == project,
                'identity-legacy-connection-required')
        primary = integration[1]
        root = Path(primary.root.path)
        top = discover(root, self.git)
        self.require_identity_capability(top)
        require(top.kind == binding.kind and top.root.path == str(root), 'identity-topology-changed')
        locator_root = Path(top.common.path) if top.kind == 'git' else root
        marker = locator_root / ('colvia/connection.json' if top.kind == 'git' else '.colvia-link.json')
        locator_raw = read_file(marker, 16384)
        require(Locator.parse(locator_raw, kind=top.kind) == binding.locator, 'stale-or-foreign-binding')
        if top.kind == 'git':
            require(revalidates(binding.location, top.common), 'identity-location-unverified')
        members = {member.root.path: (member.root, member.gitdir) for member in top.members}
        if top.kind == 'plain':
            members = {top.root.path: (top.root, None)}
        entries = []; absent=[]
        connections = Connections(store)
        for key, ref in scan_map(store.root().heads, store.load):
            if not key.startswith('workspace:'):
                continue
            obj = decode_envelope(ref, store.load(ref))
            connection_schemas()[1].check(obj)
            if obj.edges[0].ref != project:
                continue
            _, workspace = connections.workspace_record(key.split(':', 1)[1], project)
            require(len(entries)+len(absent)<10000,'identity-membership-unverified')
            if workspace.root.path not in members:
                require(top.kind=='git' and workspace!=primary and workspace.gitdir is not None,
                        'identity-membership-unverified')
                # Historical only if Git no longer lists it and both paths
                # are absent. An existing replacement or denied read refuses.
                for old in (workspace.root,workspace.gitdir):
                    try:directory_location(Path(old.path))
                    except FileNotFoundError:continue
                    require(False,'identity-membership-unverified')
                absent.append(ref.as_dict())
                continue
            current, gitdir = members[workspace.root.path]
            require(revalidates(workspace.root, current) and
                    (revalidates(workspace.gitdir, gitdir) if gitdir else workspace.gitdir is None),
                    'identity-location-unverified')
            entries.append((ref, workspace, dict(root=current, gitdir=gitdir, common=top.common)))
        require(any(w == primary for _, w, _ in entries) and
                len({loc['root'] for _, _, loc in entries}) == len(entries) and
                (top.kind == 'git' or len(entries) == 1), 'identity-membership-unverified')
        require(discover(root,self.git)==top and read_file(marker,16384)==locator_raw,
                'identity-topology-changed')
        observed={}
        for native_location in (top.root,top.common,top.gitdir,*(loc for m in top.members for loc in (m.root,m.gitdir))):
            if native_location is None or native_location.path in observed:
                continue
            fresh,live=directory_location(Path(native_location.path))
            require(fresh==native_location,'identity-topology-changed')
            observed[native_location.path]=list(live)
        return top, sha(locator_raw), entries, absent, observed

    @staticmethod
    def _ids(projects):
        from .binding import _uuid
        projects=tuple(sorted(projects))
        require(0<len(projects)<=128 and len(set(projects))==len(projects),'identity-project-selection-invalid')
        for project in projects:_uuid(project)
        return projects

    @staticmethod
    def _operation(operation,project):
        _token(operation)
        return 'identity-' + sha(canonical_bytes([operation,project]))

    def _confirmed(self,store,row,operation,receipt,statement):
        op=self._operation(operation,row['project'])
        published=store.operation_result(op)
        if published is None:
            return False
        result=decode_envelope(published[1],store.load(published[1]))
        heads=link(result,'heads')
        connections=Connections(store)
        binding_ref,binding=connections.binding()
        require(binding_ref==ObjectRef.parse(row['binding']),'identity-publication-unconfirmed')
        for entry in row['registrations']:
            wref=ObjectRef.parse(entry['ref'])
            loc={k:native(v) if v is not None else None for k,v in entry['locations'].items()}
            anchor=identities.create(op,binding_ref,wref,loc,receipt=receipt,statement=statement)[0]
            require(map_get(heads,identities.identity_key(entry['workspace']),store.load)==anchor and
                    connections.identity(wref)==anchor and binding.location==(loc['common'] or loc['root']),
                    'identity-publication-unconfirmed')
        return True

    def _census(self, projects, *, operation=None, receipt=None, statement=None):
        from dataclasses import asdict
        require(self.home.os_name=='macos','identity-platform-unavailable')
        projects=self._ids(projects);selection=set(projects)
        known=self.home.projects()
        require(selection<=set(known),'identity-project-unavailable')
        rows=[];occupied_rows=[];updates={};completed=[]
        for project in known:
            authority=self.home.authority(project)
            with closing(authority.store(readonly=True)) as store:
                connections=Connections(store)
                binding_ref=store.head(PROJECT_KEY);pointer=authority.pointer_value()
                row=dict(project=project,pointer=pointer,binding=binding_ref.as_dict() if binding_ref else None,
                         integration=None,roots=[],common=None,selected=project in selection)
                rows.append(row)
                live=binding_ref is not None and not store.needs_rebind()
                require(live or project not in selection,'identity-live-connection-required')
                if not live:
                    continue
                raw=connections.binding_record()[1]
                integration=_integration_workspace(store)
                iref=store.head('project:integration')
                row['integration']=iref.as_dict() if iref else None
                if project in selection:
                    require(not authority.files.exists(authority.root/'pending.json') and
                            store.lifecycle_state()=={'fence':None,'quiescent':None},'identity-lifecycle-pending')
                    top,locator_digest,entries,absent,observed=self._candidate(store,binding_ref,raw,integration)
                    common=top.common;roots=tuple(loc['root'] for _,_,loc in entries)
                    primary=integration[1].workspace
                    row.update(locator=locator_digest,topology=topology_value(top),live=observed,
                               absent=absent,registrations=[
                        dict(ref=ref.as_dict(),workspace=w.workspace,locations={
                            role:asdict(v) if v else None for role,v in loc.items()}) for ref,w,loc in entries])
                    if operation is not None and self._confirmed(store,row,operation,receipt,statement):
                        completed.append(project)
                    else:
                        require(store.head(identities.PROJECT_IDENTITY) is None,'identity-already-revalidated')
                        updates[project]=(binding_ref,entries,primary)
                else:
                    _,binding=connections.binding()
                    roots=occupied(connections,binding_ref,binding,integration,self.git)
                    common=binding.location if binding.kind=='git' else None
                row['roots']=[asdict(root) for root in roots]
                row['common']=asdict(common) if common else None
                root_ids={_identity(root) for root in roots}
                ancestors=set()
                for root in roots:ancestors.update(_ancestor_ids(root))
                for previous,prior_roots,prior_ancestors,prior_common in occupied_rows:
                    if project in selection or previous in selection:
                        common_id=_identity(common) if common is not None else None
                        common_overlap=(common_id is not None and (common_id==prior_common or common_id in prior_roots) or
                                        prior_common is not None and prior_common in root_ids)
                        if common_overlap or root_ids & prior_ancestors or prior_roots & ancestors:
                            raise ConnectionBoundaryError('identity-project-overlap',roots[0].path)
                occupied_rows.append((project,root_ids,ancestors,_identity(common) if common is not None else None))
        require(self.home.projects()==known,'identity-review-changed')
        return dict(version=1,projects=list(projects),census=rows),updates,completed

    def preview(self, projects):
        # Preview is read-only; exact input is re-observed under exclusion on apply.
        from contextlib import nullcontext
        with self.runtime_lease.hold() if self.runtime_lease else nullcontext():
            plan,_,_=self._census(projects)
        require(len(canonical_bytes(plan))<_LIMIT//2,'identity-review-size-limit')
        return dict(state='review',plan=plan,receipt=sha(canonical_bytes(plan)),
                    question='표시된 폴더를 기존 프로젝트의 현재 작업 위치로 확인할까요? 작업 범위와 결과 승인은 그대로입니다.')

    def _journal(self,operation):
        _token(operation)
        value=decode_canonical(self.home.files.read(self.home.root/'operations'/operation/'identity.json',_LIMIT))
        require(type(value) is dict and set(value)=={'operation','plan','receipt','statement'} and
                value['operation']==operation and value['receipt']==sha(canonical_bytes(value['plan'])),
                'identity-journal-changed')
        return value

    def _check(self,value):
        plan,updates,completed=self._census(value['plan']['projects'],operation=value['operation'],
                                           receipt=value['receipt'],statement=value['statement'])
        require(canonical_bytes(plan)==canonical_bytes(value['plan']),'identity-review-changed')
        return updates,completed

    def start(self, *, operation, plan, receipt, statement):
        _token(operation)
        require(len(canonical_bytes(plan))<_LIMIT//2 and receipt==sha(canonical_bytes(plan)),
                'identity-review-changed')
        require(type(statement) is str and 0<len(statement)<=16384 and '\x00' not in statement,
                'identity-statement-required')
        value=dict(operation=operation,plan=plan,receipt=receipt,statement=statement)
        with self.management():
            updates,completed=self._check(value)
            require(not completed and updates,'identity-already-started')
            area=self.home.root/'operations'/operation
            self.home.files.create_directory(area)
            self.home.files.create(area/'identity.json',canonical_bytes(value))
            return self._apply(value)

    def _apply(self,value,*,checkpoint=lambda _:None):
        if (status:=self._status(value))['state']=='revalidated':
            return status
        projects=value['plan']['projects']
        for project in projects:
            updates,completed=self._check(value)
            if project in completed:
                continue
            authority=self.home.authority(project)
            store=(self.home.store(project) if self.runtime_lease else authority.store())
            with closing(store):
                binding_ref,entries,primary=updates[project]
                root=store.root().ref
                def verify():
                    pending,_=self._check(value)
                    require(pending.get(project)==updates[project],'identity-review-changed')
                    return root
                Connections(store).revalidate(operation=self._operation(value['operation'],project),
                    project=binding_ref,updates=entries,primary=primary,receipt=value['receipt'],
                    statement=value['statement'],verify=verify)
            checkpoint(project)
        return self._status(value)

    def _status(self,value):
        completed=[];remaining=[]
        for row in value['plan']['census']:
            if not row['selected']:
                continue
            project=row['project'];authority=self.home.authority(project)
            require(authority.pointer_value()==row['pointer'],'identity-review-changed')
            with closing(authority.store(readonly=True)) as store:
                done=self._confirmed(store,row,value['operation'],value['receipt'],value['statement'])
            (completed if done else remaining).append(project)
        return dict(state='pending' if remaining else 'revalidated',operation=value['operation'],
                    completed=completed,remaining=remaining)

    def status(self,operation):
        with self.management():return self._status(self._journal(operation))

    def resume(self,operation):
        with self.management():return self._apply(self._journal(operation))
