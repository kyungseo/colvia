"""Fixed worker application, authorization and recovery records."""
from .codec import require
from .graph import Schema
from .storage.sqlite import _token
from .tree import logical_path,canonical_entries


def native_identity_kind(p):
    """Validate the platform's exact identity representation without conversion."""
    if type(p) is list:
        require(len(p)==3 and type(p[0]) is int and 0<=p[0]<2**64 and
                type(p[1]) is str and len(p[1])==32 and all(c in '0123456789abcdef' for c in p[1]) and
                type(p[2]) is int and 0<=p[2]<2**63,'invalid-effect-native-identity')
        return 'windows'
    require(type(p) is dict and set(p)=={'volume','inode','birth_ns'} and
            all(type(p[k]) is str and p[k].isdigit() for k in ('volume','inode')) and type(p['birth_ns']) is int,
            'invalid-effect-native-identity')
    return 'darwin'


def schemas():
    from .records import fields,one,text,MAP_KINDS
    from .binding import _uuid
    def binding(p):
        fields(p,{'application','work','source','destination','scope'})
        _token(p['application']);_token(p['work']);_uuid(p['source']);_uuid(p['destination'])
        require(p['source']!=p['destination'],'worker-distinct-workspaces-required')
        require(type(p['scope']) is list and p['scope'] and p['scope']==sorted(set(p['scope'])),'invalid-worker-scope')
        for path in p['scope']:require(logical_path(path)==path,'invalid-worker-path')
        for name in ('plan','approval','result','source_registration','destination_registration','baseline','before','after','source_head'):one(p,name)
    def authorization(p):
        fields(p,{'authority','actor','statement'});text(p['actor'],256);text(p['statement'])
        require(p['authority'] in ('human','delegated'),'invalid-worker-authority');one(p,'binding');one(p,'grant',True)
        require(bool(p['links']['grant'])==(p['authority']=='delegated'),'worker-grant-required')
    def grant(p):
        fields(p,{'work','source','destination','scope','owner','delegate','state','statement'})
        _token(p['work']);_uuid(p['source']);_uuid(p['destination'])
        require(p['source']!=p['destination'],'worker-distinct-workspaces-required')
        for field in ('owner','delegate'):text(p[field],256)
        text(p['statement']);require(p['owner']!=p['delegate'],'worker-distinct-delegate-required')
        require(p['state'] in ('active','revoked'),'invalid-worker-grant-state')
        require(type(p['scope']) is list and p['scope']==sorted(set(p['scope'])) and p['scope'],'invalid-worker-scope')
        for path in p['scope']:require(logical_path(path)==path,'invalid-worker-path')
        one(p,'plan');one(p,'previous',True)
    def manifest(p):
        fields(p,{'application','root','authority','stage','ancestors','items'});_token(p['application'])
        m=p
        kind=native_identity_kind(m['root'])
        def native(value):require(native_identity_kind(value)==kind,'mixed-effect-native-identity')
        for k in ('authority','stage'):native(m[k])
        require(type(m['ancestors']) is dict and type(m['items']) is list and len(m['items'])<=100000,'invalid-effect-manifest')
        for path,value in m['ancestors'].items():
            require(logical_path(path)==path,'invalid-effect-ancestor')
            if value is not None:native(value)
        paths=[];ancestors=set()
        for n,item in enumerate(m['items']):
            require(type(item) is dict and set(item)=={'path','pre','post','post_name','evacuated_name','pre_native','post_native'},'invalid-effect-item')
            path=item['path'];require(logical_path(path)==path,'invalid-worker-path');paths.append(path)
            parts=path.split('/');ancestors.update('/'.join(parts[:i]) for i in range(1,len(parts)))
            require(item['post_name']==f'{n:06d}.post' and item['evacuated_name']==f'{n:06d}.original','invalid-effect-staging-name')
            require(item['pre']!=item['post'],'effect-no-change-item')
            for side in ('pre','post'):
                value=item[side];location=item[side+'_native'];require((value is None)==(location is None),'effect-native-state-mismatch')
                if value is not None:
                    require(canonical_entries([value])==[value] and value['path']==path and value['kind']=='regular','invalid-effect-entry');native(location)
        require(paths==sorted(set(paths)) and set(m['ancestors'])==ancestors,'invalid-effect-path-order')
    def effect(p):
        fields(p,{'application','state'});_token(p['application'])
        require(p['state'] in ('pending','completed','cancelled'),'invalid-worker-effect-state')
        for name in ('binding','authorization','manifest'):one(p,name)
        for name in ('previous','progress'):one(p,name,True)
    def progress(p):
        fields(p,{'application','index','stage'});_token(p['application'])
        require(type(p['index']) is int and 0<=p['index']<100000 and p['stage']=='verified','invalid-effect-progress')
        one(p,'previous',True)
    return [
      Schema('worker.binding',1,{k:('integrity' if k in ('baseline','before','after') else 'decision') for k in
        ('plan','approval','result','source_registration','destination_registration','baseline','before','after','source_head')},binding,
        {'plan':frozenset({'work.plan'}),'approval':frozenset({'work.approval'}),'result':frozenset({'work.submission'}),
         'source_registration':frozenset({'workspace.registration'}),'destination_registration':frozenset({'workspace.registration'}),
         'baseline':frozenset({'observation.snapshot'}),'before':MAP_KINDS,'after':MAP_KINDS,'source_head':frozenset({'work.head'})}),
      Schema('worker.authorization',1,{'binding':'decision','grant':'decision'},authorization,
        {'binding':frozenset({'worker.binding'}),'grant':frozenset({'worker.grant'})}),
      Schema('worker.grant',1,{'plan':'decision','previous':'provenance'},grant,{'plan':frozenset({'work.plan'}),'previous':frozenset({'worker.grant'})}),
      Schema('worker.manifest',1,{},manifest,{}),
      Schema('worker.effect',1,{'binding':'decision','authorization':'decision','manifest':'integrity','progress':'integrity','previous':'provenance'},effect,
        {'binding':frozenset({'worker.binding'}),'authorization':frozenset({'worker.authorization'}),'manifest':frozenset({'worker.manifest'}),'progress':frozenset({'worker.progress'}),'previous':frozenset({'worker.effect'})}),
      Schema('worker.progress',1,{'previous':'provenance'},progress,{'previous':frozenset({'worker.progress'})})]


def validate_authorization(ref,load,*,live=False):
    from .records import application_registry,link
    def obj(ref):return application_registry().inspect(ref,load(ref),required=True)
    auth=obj(ref);binding=obj(link(auth,'binding'));grantref=link(auth,'grant')
    if grantref is not None:
        grant=obj(grantref)
        require(grant.payload['state']=='active' and grant.payload['delegate']==auth.payload['actor'] and
                all(grant.payload[k]==binding.payload[k] for k in ('work','source','destination','scope')) and
                link(grant,'plan')==link(binding,'plan'),'worker-grant-mismatch')
        if live:require(load.head('grant:'+binding.payload['work'])==grantref,'worker-grant-changed')
    return auth,binding
