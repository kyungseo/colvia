"""Restricted Claude file tools over a bounded, owned Windows pipe session."""
import json
import os
from queue import Empty, Queue
import threading
import time

from ..codec import require


TOOLS = frozenset({'Read','Edit','Write'})
PERMISSION = {'disableAllHooks':True,'autoMemoryEnabled':False,'permissions':{
    'ask':['Read','Edit','Write'],'blockReadsOutsideWorkingDirectories':True,'blockWritesOutsideWorkingDirectories':True}}
OPTIONS = ('-p','--safe-mode','--restricted','--tools','Read,Edit,Write','--permission-mode','manual',
           '--permission-prompts','host','--permission-prompt-tool','stdio','--setting-sources','',
           '--strict-mcp-config','--mcp-config','{"mcpServers":{}}','--no-session-persistence','--no-chrome',
           '--disable-slash-commands','--input-format','stream-json','--output-format','stream-json','--verbose')


def path_key(path):
    require(type(path) is str and 0<len(path)<=1024 and os.path.isabs(path),'group-worker-path-invalid')
    return os.path.normcase(os.path.normpath(path))


class Conversation:
    def __init__(self, root, allowed, session, prompt):
        self.root=path_key(str(root))
        self.allowed={path_key(str(path)):path for path in allowed}
        self.session=session
        self.prompt=prompt
        self.started=False
        self.result=False
        self.calls={}
        self.edits=set()

    @staticmethod
    def request(request_id, subtype):
        return dict(type='control_request',request_id=request_id,request=dict(subtype=subtype))

    def receive(self, event):
        kind=event.get('type')
        if kind=='control_response':
            response=event['response']
            require(response['subtype']=='success','group-worker-initialization-refused')
            body=response['response']
            if response['request_id']=='startup':
                require(body.get('current_permission_mode') in ('default','manual'),'group-worker-permission-mode-unverified')
                return self.request('mcp','mcp_status')
            require(response['request_id']=='mcp' and body.get('mcpServers')==[],
                    'group-worker-mcp-unverified')
            return dict(type='user',session_id=self.session,parent_tool_use_id=None,
                        message=dict(role='user',content=self.prompt))
        if kind=='system' and event.get('subtype')=='init':
            require(not self.started and set(event.get('tools',()))==TOOLS and event.get('mcp_servers')==[]
                    and event.get('permissionMode') in ('manual','default') and event.get('session_id')==self.session
                    and path_key(event.get('cwd'))==self.root,'group-worker-claude-inventory-mismatch')
            self.started=True
        elif kind=='control_request':
            req=event['request']; payload=req.get('input')
            require(self.started and req.get('subtype')=='can_use_tool','group-worker-unknown-permission-request')
            name=req.get('tool_name')
            path=payload.get('file_path') if type(payload) is dict else None
            key=path_key(path) if type(path) is str and os.path.isabs(path) else None
            allowed=name in TOOLS and key in self.allowed and self.allowed[key].resolve(strict=True)==self.allowed[key]
            if allowed and name in {'Edit','Write'}:
                require(self.allowed[key].stat().st_nlink==1,'group-worker-scope-unqualified')
            reply=dict(behavior='allow',updatedInput=payload) if allowed else dict(behavior='deny',message='Outside the exact approved Work scope.')
            return dict(type='control_response',response=dict(subtype='success',request_id=event['request_id'],response=reply))
        elif kind in ('assistant','user'):
            content=event.get('message',{}).get('content',())
            if not isinstance(content,list):
                return None
            for part in content:
                if part.get('type')=='tool_use':
                    require(self.started and part.get('name') in TOOLS,'group-worker-claude-inventory-mismatch')
                    payload=part.get('input',{})
                    name=part['name']
                    given=payload.get('file_path')
                    key=path_key(given) if type(given) is str and os.path.isabs(given) else None
                    self.calls[part['id']]=(name,key)
                elif part.get('type')=='tool_result' and not part.get('is_error'):
                    name,key=self.calls.get(part.get('tool_use_id'),(None,None))
                    require(self.started and key in self.allowed,'group-worker-tool-result-outside-scope')
                    if name in {'Edit','Write'}:
                        self.edits.add(key)
        elif kind=='result':
            require(self.started and not self.result and event.get('session_id')==self.session
                    and event.get('subtype')=='success' and not event.get('is_error'),
                    'group-worker-turn-incomplete')
            self.result=True
        return None


def run(cli, root, paths, session, env, prompt, *, cancelled, seconds):
    from .windows_job import JobAPI
    convo=Conversation(root,paths,session,prompt)
    argv=[str(cli),*OPTIONS,'--settings',json.dumps(PERMISSION,separators=(',',':')),
          '--session-id',session,'--model','sonnet','--max-turns','20']
    a=JobAPI(); handles=set(); threads=[]; queue=Queue(); job=None; complete=False
    def pipe():
        pair=a.pipe(); handles.update(pair); return pair
    def close(handle):
        a.close(handle); handles.remove(handle)
    def drain(handle, label):
        data=bytearray(); total=0
        try:
            while piece:=a.read_pipe(handle,16384):
                total+=len(piece)
                require(total<=1024*1024,'group-worker-output-limit')
                data.extend(piece)
                if label=='stdout':
                    while (end:=data.find(b'\n'))>=0:
                        line=bytes(data[:end]);del data[:end+1]
                        queue.put(('line',line))
            require(label!='stdout' or not data.strip(),'group-worker-output-truncated')
        except (OSError,ValueError) as exc:
            queue.put(('error',exc))
        finally:
            try:
                a.close(handle)
            except OSError as exc:
                queue.put(('error',exc))
            finally:
                queue.put(('eof',label))
    def send(handle,event):
        raw=json.dumps(event,ensure_ascii=True,separators=(',',':')).encode()+b'\n'
        require(len(raw)<=32768,'group-worker-input-limit')
        while raw:
            raw=raw[a.write_pipe(handle,raw):]
    try:
        inp=pipe(); out=pipe(); err=pipe()
        job=a.start(argv,str(root),env,(inp[0],out[1],err[1]))
        started=time.monotonic_ns()
        for handle in (inp[0],out[1],err[1]):
            close(handle)
        for handle,label in ((out[0],'stdout'),(err[0],'stderr')):
            thread=threading.Thread(target=drain,args=(handle,label),daemon=True)
            thread.start();threads.append(thread);handles.remove(handle)
        send(inp[1],convo.request('startup','initialize'))
        end=time.monotonic()+seconds
        eof=set()
        while len(eof)<2 or not (job.exited() and job.active()==0):
            require(not cancelled.is_set(),'process-cancelled')
            require(time.monotonic()<end,'process-timeout')
            try:
                kind,value=queue.get(timeout=.03)
            except Empty:
                continue
            if kind=='error':
                raise value
            if kind=='eof':
                eof.add(value)
            if kind=='line' and value.strip():
                reply=convo.receive(json.loads(value))
                if reply is not None:
                    require(inp[1] in handles,'group-worker-output-after-completion')
                    send(inp[1],reply)
                if convo.result and inp[1] in handles:
                    close(inp[1])
        require(job.code()==0 and convo.result and bool(convo.edits),'group-worker-turn-incomplete')
        complete=True
        return dict(identity=session,provider='claude',started_ns=started,closed_ns=time.monotonic_ns(),
                    writes=[str(convo.allowed[key].relative_to(root).as_posix()) for key in sorted(convo.edits)],
                    job_closed=True,exit=0)
    finally:
        try:
            if job is not None:
                try:
                    if not complete:
                        job.stop()
                        end=time.monotonic()+5
                        while not (job.exited() and job.active()==0):
                            require(time.monotonic()<end,'windows-child-closure-unknown')
                            time.sleep(.02)
                finally:
                    job.close()
        finally:
            for handle in handles:
                a.close(handle)
            for thread in threads:
                thread.join(5)
            require(not any(thread.is_alive() for thread in threads),'windows-pipe-closure-unknown')
