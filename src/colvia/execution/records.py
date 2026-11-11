"""Fixed edge roles for bounded execution and stable effect ownership."""
from ..codec import require
from ..graph import Schema
from ..storage.sqlite import _token
from . import schema

MAX_EVENTS=8192
MAX_HISTORY_BYTES=16*1024*1024

def history_bounds(count,size):
    require(type(count) is int and 1<=count<=MAX_EVENTS,'execution-history-count-limit')
    require(type(size) is int and 0<size<=MAX_HISTORY_BYTES,'execution-history-byte-limit')

def schemas():
    from ..records import fields,one,text,MAP_KINDS
    from ..binding import _uuid
    def ident(p):_token(p['run'])
    def grant(p):
        fields(p,{'run','work','workspace','contract','request'});ident(p);_token(p['work']);_uuid(p['workspace'])
        schema.grant_record(p['contract']);schema.request_record(p['request'],p['contract']);require(p['contract']['scope']['work_id']==p['work'],'execution-work-mismatch')
        for field in ('head','registration','bodies'):one(p,field)
    def authorization(p):
        fields(p,{'run','statement'});ident(p);text(p['statement']);one(p,'grant')
    def event(p):
        fields(p,{'run','row'});ident(p);one(p,'grant');one(p,'result',True);one(p,'resolution',True)
        row=p['row'];schema.exact(row,'seq previous kind value sha256');schema.integer(row['seq'],1,MAX_EVENTS)
        schema.sha(row['previous']);schema.sha(row['sha256']);schema.event(row['kind'],row['value'])
        require(row['sha256']==schema.digest({k:row[k] for k in ('seq','previous','kind','value')}),'execution-row-digest')
        require(bool(p['links']['resolution'])==(row['kind']=='operator-resolved-unknown'),'execution-resolution-record-required')
        retained=bool(p['links']['result'])
        require(not retained or (row['kind']=='worker-result' and row['value']['after'] is not None),'execution-unexpected-result-body')
        require(not (row['kind']=='worker-result' and row['value']['effect']=='applied') or retained,'execution-result-body-required')
    def resolution(p):
        fields(p,{'run','statement','observation'});ident(p);text(p['statement'])
        schema.event('operator-resolved-unknown',p['observation']);one(p,'grant');one(p,'history')
    def history(p):
        fields(p,{'run','count','bytes'});ident(p);history_bounds(p['count'],p['bytes'])
        one(p,'events');one(p,'previous',True)
    def state(p):
        fields(p,{'run','status','effect','completed'});ident(p)
        schema.choice(p['status'],schema.CLOSED|{'incomplete','unknown'});schema.choice(p['effect'],schema.EFFECTS);schema.integer(p['completed'],0,5)
        for name in ('grant','authorization','history','owner'):one(p,name)
        one(p,'previous',True)
    def cancel(p):
        fields(p,{'run','reason'});ident(p);schema.choice(p['reason'],schema.REASONS);one(p,'grant')
    def owner(p):
        fields(p,{'kind','identifier','key'});_token(p['identifier'])
        require(p['kind'] in ('execution-run','delivery-attempt'),'effect-owner-kind-unavailable')
        prefix='execution:' if p['kind']=='execution-run' else 'delivery:'
        require(p['key']==prefix+p['identifier'],'effect-owner-key-mismatch');one(p,'identity');one(p,'parent',True)
        require(not p['links']['parent'] or p['kind']=='execution-run','effect-owner-parent-refused')
    single=lambda kind:frozenset({kind})
    return [
      Schema('execution.grant',1,{'head':'decision','registration':'decision','bodies':'integrity'},grant,
             {'head':single('work.head'),'registration':single('workspace.registration'),'bodies':MAP_KINDS}),
      Schema('execution.authorization',1,{'grant':'decision'},authorization,{'grant':single('execution.grant')}),
      Schema('execution.event',1,{'grant':'decision','result':'integrity','resolution':'decision'},event,{'grant':single('execution.grant'),'result':single('body.complete'),'resolution':single('execution.resolution')}),
      Schema('execution.resolution',1,{'grant':'decision','history':'decision'},resolution,{'grant':single('execution.grant'),'history':single('execution.history')}),
      Schema('execution.history',1,{'events':'integrity','previous':'provenance'},history,{'events':MAP_KINDS,'previous':single('execution.history')}),
      Schema('execution.state',1,{'grant':'decision','authorization':'decision','history':'integrity','owner':'decision','previous':'provenance'},state,
             {'grant':single('execution.grant'),'authorization':single('execution.authorization'),'history':single('execution.history'),'owner':single('effect.owner'),'previous':single('execution.state')}),
      Schema('execution.cancel',1,{'grant':'decision'},cancel,{'grant':single('execution.grant')}),
      Schema('effect.owner',1,{'identity':'decision','parent':'decision'},owner,
             {'identity':frozenset({'execution.grant','delivery.attempt'}),'parent':single('effect.owner')})]
