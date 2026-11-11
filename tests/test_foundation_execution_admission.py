"""Concrete policy tests use synthetic response objects, no account lookup."""
import copy,unittest
from colvia.codec import RecordError
from colvia.adapters.codex_documents import Policy,DISABLED_FEATURES,PROFILE
from test_foundation_execution_history import grant

class AdmissionTests(unittest.TestCase):
    def fixture(self):
        policy=Policy(model='synthetic-model',runtime_digest='a'*64,policy_digest='b'*64)
        value=grant();value['capability']['identity']=policy.identity;value['capability']['policy_digest']=policy.policy_digest
        config=dict(features={**{key:False for key in DISABLED_FEATURES},'code_mode_host':True,'skip_host_skill_discovery':True},
            web_search='disabled',project_doc_max_bytes=0,notify=[],default_permissions=PROFILE,model_provider='openai',mcp_servers={})
        account={'account':{'type':'chatgpt','email':'synthetic@example.invalid'}}
        models={'data':[dict(model='synthetic-model',supportedReasoningEfforts=[{'reasoningEffort':'low'}])]}
        return policy,value,config,account,models
    def test_exact_policy_retains_only_qualified_identity(self):
        policy,value,config,account,models=self.fixture();result=policy.admit(value,config,account,models)
        self.assertEqual({'pass':True,'capability_digest':policy.identity,'policy_digest':policy.policy_digest},result)
        self.assertNotIn('synthetic@example.invalid',str(result));self.assertNotIn('account',result)
        self.assertEqual(['document_read','document_write','document_verify'],[tool['name'] for tool in policy.tools(value)])
        self.assertEqual('never',policy.overrides()['approval_policy'])
    def test_any_enabled_native_feature_or_missing_profile_refuses(self):
        policy,value,config,account,models=self.fixture()
        for feature in DISABLED_FEATURES:
            changed=copy.deepcopy(config);changed['features'][feature]=True
            with self.assertRaisesRegex(RecordError,'feature-mismatch'):policy.admit(value,changed,account,models)
        for changed in ({**config,'default_permissions':'full'},{**config,'project_doc_max_bytes':False},
                {**config,'instructions':'unexpected'},{**config,'notify':['command']}):
            with self.assertRaises(RecordError):policy.admit(value,changed,account,models)
    def test_provider_external_tools_or_api_billing_route_refuses(self):
        policy,value,config,account,models=self.fixture()
        for changed in ({**config,'model_provider':'other'},{**config,'mcp_servers':{'external':{}}},
                {**config,'mcp_servers':{'external':{'enabled':True}}}):
            with self.assertRaises(RecordError):policy.admit(value,changed,account,models)
        with self.assertRaisesRegex(RecordError,'subscription-account'):policy.admit(value,config,{'account':{'type':'apiKey'}},models)
    def test_runtime_and_policy_identity_cannot_be_rebound(self):
        policy,value,config,account,models=self.fixture();value['scope']['resources']['runtime_digest']='0'*64
        with self.assertRaisesRegex(RecordError,'runtime-policy-mismatch'):policy.admit(value,config,account,models)
    def test_ambiguous_or_unavailable_model_is_not_fallback(self):
        policy,value,config,account,models=self.fixture()
        for bad in ({'data':[]},{'data':models['data']*2},{'data':[dict(id='synthetic-model',supportedReasoningEfforts=[])]}):
            with self.assertRaises(RecordError):policy.admit(value,config,account,bad)
