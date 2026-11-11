"""Explicit, pinned runtime launch plan; no discovery, directory creation or spawn.

A trusted composition root supplies release-qualified binary/helper digests and
existing private session paths. Credential contents are never read or hashed.
The binding digest participates in the concrete capability identity, while the
record vocabulary and result-acceptance semantics remain unchanged. Path rechecks
are cooperative-scope checks, not atomic execution against hostile same-user swaps.
"""
from dataclasses import dataclass
import json,os,re,stat,tomllib
from pathlib import Path
from ..codec import require
from ..execution import schema
from ..adapters.codex_documents import PROFILE
from .darwin_runtime_policy import prepare_launch,canonical_existing,PARAMETERS,DIRECTORIES,POLICY_SHA256
from .darwin_execution_inputs import resource_digest,resource_bytes
from .darwin_execution import process_birth
from .runtime_inventory import inventory,signature,session_directories,MAX_ENTRIES

TREE_ROOTS=frozenset({'PYROOT','CODEX_RULES_DIR'})
CONFIG_KEYS=frozenset({'model','model_provider','model_reasoning_effort','model_verbosity','service_tier','mcp_servers'})
PINNED=PARAMETERS-DIRECTORIES-{'CODEX_AUTH','INSTALLATION_ID'}
FORBIDDEN_ENV=('OPENAI_API_KEY','CODEX_API_KEY','OPENAI_BASE_URL','CODEX_API_BASE','CHATGPT_BASE_URL',
    'HTTP_PROXY','HTTPS_PROXY','ALL_PROXY','http_proxy','https_proxy','all_proxy','CODEX_HOME')

@dataclass(frozen=True)
class RuntimePlan:
    argv:tuple
    cwd:str
    environment:tuple
    binding_digest:str
    @property
    def env(self):return dict(self.environment)

class DarwinRuntimeLaunch:
    def __init__(self,*,bindings,digests,policy_path,authority_root,home,qualified,inventories):
        require(type(bindings) is dict and set(bindings)==PARAMETERS,'execution-runtime-parameter-set')
        require(type(digests) is dict and set(digests)==PINNED,'execution-runtime-pin-set')
        require(type(qualified) is dict and set(qualified)=={'BIN','CODE_MODE_HOST'},'execution-runtime-qualification')
        for value in [*digests.values(),*qualified.values()]:schema.sha(value)
        require(all(digests[key]==value for key,value in qualified.items()),'execution-runtime-unqualified-binary')
        require(type(inventories) is dict and set(inventories)==TREE_ROOTS,'execution-runtime-inventory-set')
        require(all(type(rows) is list and len(rows)<=MAX_ENTRIES for rows in inventories.values()),'execution-runtime-inventory-shape')
        self.inventories=json.loads(json.dumps(inventories));self._trees={};self._files={};self._session=None
        self.bindings=dict(bindings);self.digests=dict(digests);self.qualified=dict(qualified)
        self.policy_path=str(policy_path);self.authority_root=str(authority_root);self.home=str(home)

    def _inputs(self,*,cold=True):
        require(not any(os.environ.get(key) for key in FORBIDDEN_ENV),'execution-runtime-environment-override')
        home=canonical_existing(self.home,True)
        paths={key:canonical_existing(value,key in DIRECTORIES) for key,value in self.bindings.items()}
        require(paths['CODEX_CONFIG']==home/'.codex/config.toml' and paths['CODEX_AUTH']==home/'.codex/auth.json' and
            paths['INSTALLATION_ID']==home/'.codex/installation_id' and paths['CODEX_RULES_DIR']==home/'.codex/rules','execution-runtime-auth-home')
        require(paths['GLOBAL_INSTRUCTIONS']==home/'.codex/AGENTS.md','execution-runtime-instruction-home')
        require(not os.path.lexists(home/'.codex/AGENTS.override.md'),'execution-runtime-instruction-override')
        require(paths['CODE_MODE_HOST']==paths['BIN'].with_name('codex-code-mode-host'),'execution-runtime-helper-location')
        for key,path in paths.items():
            if key not in DIRECTORIES:require(path.stat().st_nlink==1,'execution-runtime-file-alias')
        for key in PINNED:
            if cold:
                before=signature(paths[key].lstat())
                require(resource_digest(paths[key])==self.digests[key],'execution-runtime-input-drift')
                require(signature(paths[key].lstat())==before,'execution-runtime-input-drift');self._files[key]=before
            else:require(signature(paths[key].lstat())==self._files.get(key),'execution-runtime-input-drift')
        for key in TREE_ROOTS:
            rows,identities=inventory(paths[key],content=cold)
            if cold:
                require(rows==self.inventories[key],'execution-runtime-inventory-drift');self._trees[key]=identities
            else:require(identities==self._trees.get(key),'execution-runtime-inventory-drift')
        config=tomllib.loads(resource_bytes(paths['CODEX_CONFIG'],self.digests['CODEX_CONFIG'],limit=65536).decode('utf-8'))
        require(set(config)<=CONFIG_KEYS,'execution-runtime-config-unsupported')
        require(all(type(value) is str for key,value in config.items() if key!='mcp_servers'),'execution-runtime-config-shape')
        require(config.get('model_provider') in (None,'openai') and not config.get('model_providers'),'execution-runtime-custom-provider')
        require(not any(config.get(k) for k in ('instructions','developer_instructions','model_instructions_file')),'execution-runtime-configured-instructions')
        servers=config.get('mcp_servers',{})
        require(type(servers) is dict and all(re.fullmatch(r'[A-Za-z0-9_-]+',name) for name in servers),'execution-runtime-mcp-shape')
        # Only identity is exposed. Mutable subscription files have no content pin.
        identity=schema.digest(dict(version=1,paths=self.bindings,digests=self.digests,inventories=self.inventories,policy=POLICY_SHA256,
            authority=self.authority_root,home=self.home))
        return paths,servers,identity

    def identity(self):
        # For proposal/grant preparation only, never permission to launch.
        return self._inputs()[2]

    def prepare(self,grant,policy):return self._plan(grant,policy,cold=True)

    def _plan(self,grant,policy,*,cold):
        policy.bind(grant.payload['contract']);paths,servers,identity=self._inputs(cold=cold)
        require(policy.runtime_digest==self.digests['BIN'] and policy.policy_digest==POLICY_SHA256 and
            policy.runtime_binding_digest==identity,'execution-runtime-binding-mismatch')
        runtime_info=paths['RUNTIME'].lstat()
        require(runtime_info.st_uid==os.getuid() and stat.S_IMODE(runtime_info.st_mode)&0o077==0,'execution-runtime-root-private')
        require(paths['SESSION'].parent==paths['RUNTIME'] and
            set(os.listdir(paths['RUNTIME']))=={paths['SESSION'].name},'execution-runtime-session-isolation')
        children,session_identity=session_directories(paths['SESSION'],self._session)
        overrides={**policy.overrides(),'log_dir':str(children['log']),'sqlite_home':str(children['sqlite'])}
        args=[]
        for key,value in overrides.items():args.extend(('-c',key+'='+json.dumps(value)))
        args.extend(('-c','permissions.'+PROFILE+'={filesystem={":minimal"="read",":tmpdir"="deny",":slash_tmp"="deny"},network={enabled=false}}'))
        for name in sorted(servers):args.extend(('-c','mcp_servers.'+name+'.enabled=false'))
        args.extend(('app-server','--strict-config','--listen','stdio://'))
        bound=prepare_launch(self.bindings,args,protected=[grant.payload['contract']['target'],self.authority_root],policy_path=self.policy_path)
        env=dict(HOME=self.home,LANG='C.UTF-8',PATH='/usr/bin:/bin:/usr/sbin:/sbin',TMPDIR=str(children['tmp']),RUST_LOG='off')
        self._session=session_identity
        return RuntimePlan(tuple(bound['argv']),str(children['cwd']),tuple(sorted(env.items())),identity)

    def verify(self,plan,grant,policy):
        require(type(plan) is RuntimePlan and self._plan(grant,policy,cold=False)==plan,'execution-runtime-plan-changed')

    def host_identity(self):
        pid=os.getpid();birth=process_birth(pid);require(bool(birth),'execution-host-identity-unavailable')
        return dict(pid=pid,birth=birth)
