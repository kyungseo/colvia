"""Fixed official runtime arguments and admission; no account content retained."""
from pathlib import Path
import json
import os
import re
import sys
import tomllib
from . import official_state as state
from .official_policy import prepare_launch

MODEL = 'gpt-6.1-sol'
PROFILE = 'official-no-tools'
DISABLED_FEATURES = ('apps','plugins','remote_plugin','hooks','multi_agent','multi_agent_v2','code_mode',
    'code_mode_host_grpc','memories','context_management','shell_tool','shell_snapshot','stable_environment_tools',
    'view_image','browser_use','browser_use_external','computer_use','image_generation','tool_suggest',
    'skill_mcp_dependency_install','skill_search','workspace_dependencies','daemon_auto_start','goals','artifact',
    'realtime_conversation','exec_permission_approvals','request_permissions_tool')
DIRECT_FALLBACK = 'Code Mode is unavailable because code-mode host is disabled. Falling back to direct tools; enable `features.code_mode_host` and install `codex-code-mode-host`.'


def diagnostic(value):
    # Only categories and numeric codes cross the diagnostic boundary.
    text = str(value).lower()
    groups = {'routing': ('routing',), 'timeout': ('timeout','timed out'), 'auth': ('unauthorized','authentication'),
              'tls': ('tls','ssl','certificate'), 'permission': ('permission','operation not permitted'),
              'protocol': ('unexpected','protocol'), 'limit': ('rate limit','usage limit')}
    result = {'categories': [k for k, needles in groups.items() if any(x in text for x in needles)],
              'source_content_retained': False, 'message_length': len(text)}
    if type(value) is dict and type(value.get('code')) is int:
        result['rpc_code'] = value['code']
    return result


def tool_specs(spec):
    ids = spec['request']['read_ids']; output = spec['request']['documents']['output']
    def tool(name, description, properties):
        return {'type':'function','name':name,'description':description,
                'inputSchema':{'type':'object','properties':properties,'required':list(properties),'additionalProperties':False}}
    return [tool('u2_read_file', 'Read the approved views once, in the declared file ID order.',
                 {'file_ids':{'type':'array','items':{'type':'string','enum':ids},'minItems':len(ids),'maxItems':len(ids)}}),
            tool('u2_write_file', 'Replace only the approved range once. Use its full file_sha256 from the read result.',
                 {'file_id':{'type':'string','enum':[output]},'expected_sha256':{'type':'string'},'content':{'type':'string'}}),
            tool('u2_verify', 'Run DOC-LINKS, DOC-GFM, DOC-CLAIMS sequentially after the one write.',
                 {'verifier_id':{'type':'string','enum':['DOC-LINKS','DOC-GFM','DOC-CLAIMS']}})]


def launch_spec(host):
    from .official_entry import runtime_input
    paths = runtime_input(host.spec['request']['runtime'])
    base = Path(host.spec['runtime_root'])
    session = state.directory(base / host.grant, create=True)
    for name in ('cwd','tmp','log','sqlite'):
        state.directory(session / name, create=True)
    config = tomllib.loads(state.regular(paths['CODEX_CONFIG']).decode())
    overrides = {**{'features.' + k: False for k in DISABLED_FEATURES},
        'features.code_mode_host':True, 'features.skip_host_skill_discovery':True,
        'web_search':'disabled','project_doc_max_bytes':0,'notify':[], 'history.persistence':'none',
        'suppress_unstable_features_warning':True, 'forced_login_method':'chatgpt',
        'model':MODEL,'model_reasoning_effort':'low','service_tier':'default','approval_policy':'never',
        'default_permissions':PROFILE, 'log_dir':str(session/'log'), 'sqlite_home':str(session/'sqlite')}
    args = []
    for key, value in overrides.items():
        args += ['-c', key + '=' + json.dumps(value)]
    args += ['-c', 'permissions.' + PROFILE + '={filesystem={":minimal"="read",":tmpdir"="deny",":slash_tmp"="deny"},network={enabled=false}}']
    for name in sorted(config.get('mcp_servers', {})):
        state.need(re.fullmatch('[A-Za-z0-9_-]+', name), 'mcp-name-unavailable')
        args += ['-c', 'mcp_servers.' + name + '.enabled=false']
    args += ['app-server','--strict-config','--listen','stdio://']
    bindings = dict(paths, PYROOT=str(Path(sys.executable).resolve().parent.parent), RUNTIME=str(base), SESSION=str(session))
    roots = (host.target, Path(host.spec['request']['worker_root']))
    state.need(not any(Path(p) == root or root in Path(p).parents for p in paths.values() for root in roots), 'runtime-input-project-overlap')
    protected = [v['path'] for v in host.spec['documents']['files'].values()] + [host.spec['host_control']['path']]
    protected += [str(host.target / '.hrn' / name) for name in ('executions','work','intents','format.json','product/binding.json')]
    bound = prepare_launch(bindings, args, protected=protected)
    env = {k:v for k,v in os.environ.items() if k in ('HOME','USER','LOGNAME')}
    env.update(LANG='C.UTF-8', PATH='/usr/bin:/bin:/usr/sbin:/sbin', TMPDIR=str(session/'tmp'), RUST_LOG='off')
    return {'argv':bound['argv'],'env':env,'cwd':str(session/'cwd'),'policy_sha256':bound['policy_sha256'],
            'tools':tool_specs(host.spec)}


def preflight(rpc):
    initialized = rpc.request('initialize', {'clientInfo':{'name':'colvia_official','title':'Colvia Official Execution','version':'1'},
                                            'capabilities':{'experimentalApi':True}})
    rpc.send({'method':'initialized'})
    config = rpc.request('config/read', {'cwd':rpc.spec['cwd'],'includeLayers':False})['config']
    features = config.get('features', {})
    state.need(all(features.get(k) is False for k in DISABLED_FEATURES) and features.get('code_mode_host') is True and
               features.get('skip_host_skill_discovery') is True, 'effective-feature-mismatch')
    state.need(config.get('web_search') == 'disabled' and config.get('project_doc_max_bytes') == 0 and
               config.get('notify') == [] and config.get('default_permissions') == PROFILE, 'effective-tool-permission-mismatch')
    state.need(config.get('model_provider') in ('openai',None) and
               all(v.get('enabled') is False for v in config.get('mcp_servers',{}).values()), 'effective-provider-or-mcp-mismatch')
    state.need(not any(config.get(k) for k in ('instructions','developer_instructions','model_instructions_file')), 'effective-instructions')
    account = rpc.request('account/read', {'refreshToken':False})
    state.need((account.get('account') or {}).get('type') == 'chatgpt', 'expected-chatgpt-account-unavailable')
    del account
    models = rpc.request('model/list', {'limit':100,'includeHidden':True})
    selected = next((m for m in models['data'] if m.get('model') == MODEL or m.get('id') == MODEL), None)
    state.need(selected is not None and any(e['reasoningEffort'] == 'low' for e in selected['supportedReasoningEfforts']), 'fixed-model-effort-unavailable')
    rpc.host.journal.append('admission', {'pass':True, 'account_type':'chatgpt', 'model_id':MODEL,
                                        'effort':'low', 'policy_digest':rpc.spec['policy_sha256']})
