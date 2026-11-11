"""Optional execution choices; never remove readers for retained history."""
import hashlib
from .codec import require,canonical_bytes,ObjectRef
from .graph import Schema
from .records import fields,text,one,record,application_registry
from .effects import guard
KEY='configuration:features'
OPTIONAL=frozenset({'official-execution'})

def _features(value):
    require(type(value) is list and all(type(v) is str for v in value) and
            value==sorted(set(value)) and set(value)<=OPTIONAL,'unsupported-optional-feature')

def _schema(p):
    fields(p,{'enabled','actor','statement'});_features(p['enabled']);text(p['statement']);text(p['actor'],160);one(p,'previous',True)

def schemas():
    return [Schema('configuration.features',1,{'previous':'provenance'},_schema,
                   {'previous':frozenset({'configuration.features'})})]

def enabled(view):
    ref=view.head(KEY)
    if ref is None:return frozenset()
    load=view.load if hasattr(view,'load') else view
    obj=application_registry().inspect(ref,load(ref),required=True)
    require(obj.ref.kind=='configuration.features','configuration-kind')
    return frozenset(obj.payload['enabled'])

def require_enabled(view,feature):require(feature in enabled(view),'feature-not-enabled')

class Configuration:
    def __init__(self,store,*,available=OPTIONAL):self.store=store;self.available=frozenset(available)
    def preview(self,features):
        _features(features);require(set(features)<=self.available,'runtime-feature-unavailable')
        current=self.store.head(KEY)
        plan=dict(project=self.store.project,instance=self.store.instance,
                  previous=current.as_dict() if current else None,enabled=features)
        receipt=hashlib.sha256(canonical_bytes(plan)).hexdigest()
        current_enabled=enabled(self.store)
        require(self.store.head(KEY)==current,'configuration-preview-changed')
        return dict(receipt=receipt,previous=current.as_dict() if current else None,enabled=features,changed=set(features)!=current_enabled,
                    question='이 프로젝트의 선택 기능을 변경할까요?')
    def apply(self,*,operation,features,receipt,statement,actor='owner'):
        preview=self.preview(features);require(preview['receipt']==receipt,'configuration-preview-changed')
        current=ObjectRef.parse(preview['previous']) if preview['previous'] is not None else None
        text(statement);text(actor,160)
        pair=record('configuration.features',dict(enabled=features,statement=statement,actor=actor),
                    {'previous':('provenance',current)})
        def validate(view):
            guard(view);application_registry().inspect(pair[0],view(pair[0]),required=True)
        self.store.commit_heads(operation=operation,expected={KEY:current},changes={KEY:pair[0]},objects=[pair],validate=validate)
        return dict(enabled=features,history_preserved=True)
