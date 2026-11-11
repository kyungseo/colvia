"""Concrete Codex app-server policy for optional bounded document execution.

Ordinary Codex/Claude agent Work does not use this module. Its effective-policy
checks qualify only the exact runtime and policy digests supplied by a trusted
release adapter. No login, subscription, process or network action occurs here.
"""
import re
from ..codec import require
from ..execution import schema

PROFILE='official-no-tools'
DISABLED_FEATURES=('apps','plugins','remote_plugin','hooks','multi_agent','multi_agent_v2','code_mode',
    'code_mode_host_grpc','memories','context_management','shell_tool','shell_snapshot','stable_environment_tools',
    'view_image','browser_use','browser_use_external','computer_use','image_generation','tool_suggest',
    'skill_mcp_dependency_install','skill_search','workspace_dependencies','daemon_auto_start','goals','artifact',
    'realtime_conversation','exec_permission_approvals','request_permissions_tool')

class Policy:
    def __init__(self,*,model,runtime_digest,policy_digest,runtime_binding_digest=None):
        require(type(model) is str and re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9._-]{0,95}',model) is not None,'execution-model-identity')
        schema.sha(runtime_digest);schema.sha(policy_digest)
        if runtime_binding_digest is not None:schema.sha(runtime_binding_digest)
        self.runtime_binding_digest=runtime_binding_digest
        self.model=model;self.runtime_digest=runtime_digest;self.policy_digest=policy_digest
        identity=dict(adapter='codex-bounded-document-1',model=model,effort='low',
            runtime_digest=runtime_digest,policy_digest=policy_digest,profile=PROFILE,disabled=list(DISABLED_FEATURES),
            protocol='bounded-document-rpc-1',account_type='chatgpt')
        if runtime_binding_digest is not None:identity['runtime_binding_digest']=runtime_binding_digest
        self.identity=schema.digest(identity)
    def bind(self,contract):
        schema.grant_record(contract)
        require(contract['capability']==dict(identity=self.identity,policy_digest=self.policy_digest,
            protocol='bounded-document-rpc-1',observation_format='posix-document-process-1') and
            contract['scope']['resources']['runtime_digest']==self.runtime_digest,'execution-runtime-policy-mismatch')
    def overrides(self):
        return {**{'features.'+key:False for key in DISABLED_FEATURES},
            'features.code_mode_host':True,'features.skip_host_skill_discovery':True,'web_search':'disabled',
            'project_doc_max_bytes':0,'notify':[],'history.persistence':'none','suppress_unstable_features_warning':True,
            'forced_login_method':'chatgpt','model':self.model,'model_reasoning_effort':'low','service_tier':'default',
            'approval_policy':'never','default_permissions':PROFILE}
    def admit(self,contract,config,account,models):
        self.bind(contract)
        require(type(config) is dict and type(account) is dict and type(models) is dict,'execution-admission-shape')
        features=config.get('features');require(type(features) is dict,'effective-feature-mismatch')
        require(all(features.get(key) is False for key in DISABLED_FEATURES) and features.get('code_mode_host') is True and
            features.get('skip_host_skill_discovery') is True,'effective-feature-mismatch')
        require(config.get('web_search')=='disabled' and type(config.get('project_doc_max_bytes')) is int and
            config['project_doc_max_bytes']==0 and config.get('notify')==[] and config.get('default_permissions')==PROFILE,
            'effective-tool-permission-mismatch')
        servers=config.get('mcp_servers',{})
        require(type(servers) is dict and all(type(value) is dict and value.get('enabled') is False for value in servers.values()) and
            config.get('model_provider') in ('openai',None),'effective-provider-or-mcp-mismatch')
        require(not any(config.get(key) for key in ('instructions','developer_instructions','model_instructions_file')),'effective-instructions')
        value=account.get('account');require(type(value) is dict and value.get('type')=='chatgpt','expected-subscription-account-unavailable')
        rows=models.get('data');require(type(rows) is list and len(rows)<=100,'effective-model-list')
        choices=[row for row in rows if type(row) is dict and (row.get('model')==self.model or row.get('id')==self.model)]
        require(len(choices)==1,'fixed-model-unavailable');efforts=choices[0].get('supportedReasoningEfforts')
        require(type(efforts) is list and any(type(e) is dict and e.get('reasoningEffort')=='low' for e in efforts),'fixed-model-effort-unavailable')
        # Return no account identifier, token, model output or raw config.
        return {'pass':True,'capability_digest':self.identity,'policy_digest':self.policy_digest}
    def tools(self,contract):
        self.bind(contract);scope=contract['scope'];ids=scope['read_ids'];output=scope['output_id']
        def tool(name,description,properties):
            return dict(type='function',name=name,description=description,
                inputSchema=dict(type='object',properties=properties,required=list(properties),additionalProperties=False))
        return [tool('document_read','Read the approved views once, in declared file ID order.',
                {'file_ids':dict(type='array',items=dict(type='string',enum=ids),minItems=len(ids),maxItems=len(ids))}),
            tool('document_write','Replace only the approved range once, using its full file_sha256.',
                {'file_id':dict(type='string',enum=[output]),'expected_sha256':dict(type='string'),'content':dict(type='string')}),
            tool('document_verify','Run DOC-LINKS, DOC-GFM and DOC-CLAIMS sequentially.',
                {'verifier_id':dict(type='string',enum=list(schema.VERIFIERS))})]
