"""Product-owned structural schema table for the v1 storage primitives.

Application records extend this table explicitly. Unknown extension objects can
be preserved by generic audit/export without acquiring decision authority.
"""
from .bodies import descriptor, validate_body
from .codec import decode_envelope, encode_envelope, require
from .graph import Registry, Schema
from .maps import _node as map_node, verify_map, map_update
from .tree import LEAF_ENTRIES, PATH_RULE, canonical_entries


def _fields(p, keys):
    require(set(p) == set(keys) | {'links'}, 'invalid-typed-payload')


def _root(p):
    _fields(p, {'project','sequence','operation'})
    require(type(p['project']) is str and p['project'] and
            type(p['sequence']) is int and p['sequence']>=0 and
            p['links']['heads']==[0] and p['links']['operations']==[1] and
            p['links']['previous']==([] if p['sequence']==0 else [2]) and
            (p['operation'] is None if p['sequence']==0 else
             type(p['operation']) is str and 0<len(p['operation'])<=160 and p['operation'][0].isascii() and p['operation'][0].isalnum() and
             all(c.isascii() and (c.isalnum() or c in '-_.') for c in p['operation'])), 'invalid-state-root')


def _root_content(ref, load):
    obj=decode_envelope(ref,load(ref))
    verify_map(obj.edges[0].ref,load)
    verify_map(obj.edges[1].ref,load)
    if obj.payload['sequence']:
        previous=decode_envelope(obj.edges[2].ref,load(obj.edges[2].ref))
        require(obj.edges[2].ref.kind=='state.root' and obj.edges[2].ref.version==1,'invalid-root-predecessor')
        require(previous.payload.get('project')==obj.payload['project'] and
                type(previous.payload.get('sequence')) is int and
                previous.payload['sequence']==obj.payload['sequence']-1,
                'invalid-root-predecessor')
        rebuilt=map_update(previous.edges[1].ref,{obj.payload['operation']:obj.edges[2].ref},load)
        require(rebuilt.root==obj.edges[1].ref,'operation-map-history-mismatch')
    operations=decode_envelope(obj.edges[1].ref,load(obj.edges[1].ref))
    require(operations.payload['count']==obj.payload['sequence'],'operation-map-count-mismatch')


def _map(obj):
    _,raw=encode_envelope(obj.ref.kind,obj.ref.version,obj.payload,obj.edges)
    map_node(obj.ref,raw,())


def _tree(p, leaf):
    _fields(p, {'path_rule','entries' if leaf else 'buckets'})
    require(p['path_rule']==PATH_RULE,'path-rules-unavailable')
    if leaf:
        entries=p['entries']
        require(type(entries) is list and len(entries)<=LEAF_ENTRIES,'invalid-tree-leaf')
        require(canonical_entries(entries)==entries,'unordered-tree-leaf')
    else:
        keys=p['buckets']
        require(type(keys) is list and 0<len(keys)<=256 and
                all(type(k) is int and 0<=k<=255 for k in keys) and keys==sorted(set(keys)) and
                p['links']['children']==list(range(len(keys))), 'invalid-tree-branch')


def _body(obj):
    _,raw=encode_envelope(obj.ref.kind,obj.ref.version,obj.payload,obj.edges)
    descriptor(obj.ref,raw)


def foundation_registry(extra=()):
    return Registry([
        Schema('state.root',1,{'heads':'integrity','operations':'integrity','previous':'provenance'},_root,
               {'heads':frozenset({'map.leaf','map.branch'}),'operations':frozenset({'map.leaf','map.branch'}),'previous':frozenset({'state.root'})},content=_root_content),
        Schema('map.leaf',1,{'values':'decision'},lambda p:None,{'values':None},local=_map),
        Schema('map.branch',1,{'children':'integrity'},lambda p:None,
               {'children':frozenset({'map.leaf','map.branch'})},local=_map),
        Schema('tree.leaf',1,{},lambda p:_tree(p,True),{}),
        Schema('tree.branch',1,{'children':'integrity'},lambda p:_tree(p,False),
               {'children':frozenset({'tree.leaf','tree.branch'})}),
        Schema('body.complete',1,{'chunks':'integrity'},lambda p:None,
               {'chunks':frozenset({'body.chunk'})},local=_body,content=validate_body),
        *extra,
    ])
