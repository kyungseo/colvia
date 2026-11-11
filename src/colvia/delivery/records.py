"""Closed roles for delivery records; results never stand for acceptance."""
from ..codec import require
from ..graph import Schema
from ..storage.sqlite import _token
from ..binding import _uuid

ACTIONS=frozenset(('inspect','submit','execute'))
PHASES=frozenset(('queued','active','finished','cancelled','failed'))

def schemas():
    from ..records import fields,one,text
    def ident(p):_token(p['delivery'])
    def receiver(value):
        require(value is None or (type(value) is dict and set(value)=={'id','version'} and
            type(value['version']) is int and 1<=value['version']<=65535),'delivery-receiver-shape')
        if value is not None:_token(value['id'])
    def request(p):
        fields(p,{'delivery','work','workspace','action','deadline_ns','steps','receiver'});ident(p);_token(p['work']);_uuid(p['workspace'])
        require(p['action'] in ACTIONS and type(p['deadline_ns']) is int and 0<p['deadline_ns']<2**63 and
            type(p['steps']) is int and p['steps']==1,'delivery-request-shape');receiver(p['receiver'])
        for name in ('head','registration'):one(p,name)
        for name in ('prepared','grant'):one(p,name,True)
        require(bool(p['links']['prepared'])==(p['action']=='submit') and bool(p['links']['grant'])==(p['action']=='execute'),'delivery-action-input')
    def authorization(p):
        fields(p,{'delivery','statement'});ident(p);text(p['statement']);one(p,'request')
    def attempt(p):
        fields(p,{'delivery','attempt'});ident(p);_token(p['attempt']);one(p,'request');one(p,'authorization')
    def state(p):
        fields(p,{'delivery','phase'});ident(p);require(p['phase'] in PHASES,'delivery-phase')
        for name in ('request','authorization'):one(p,name)
        for name in ('attempt','owner','outcome','previous'):one(p,name,True)
        require(bool(p['links']['attempt'])==bool(p['links']['owner']),'delivery-owner-attempt')
        require((p['phase'] in ('finished','cancelled','failed'))==bool(p['links']['outcome']),'delivery-outcome-required')
        require(p['phase']!='queued' or not p['links']['attempt'],'delivery-queued-attempt')
        require(p['phase']!='active' or bool(p['links']['attempt']),'delivery-active-attempt')
    def cancel(p):
        fields(p,{'delivery','statement'});ident(p);text(p['statement']);one(p,'request')
    def outcome(p):
        fields(p,{'delivery','kind'});ident(p);require(p['kind'] in ('observed','submitted','executed','cancelled','failed'),'delivery-outcome-kind')
        one(p,'request')
        for name in ('head','execution'):one(p,name,True)
        require(bool(p['links']['head'])==(p['kind'] in ('observed','submitted')) and
            bool(p['links']['execution'])==(p['kind']=='executed'),'delivery-outcome-content')
    def notice(p):
        fields(p,{'delivery','project','instance','receiver'});ident(p);_uuid(p['project']);_uuid(p['instance']);receiver(p['receiver'])
        require(p['receiver'] is not None,'notice-receiver-required');one(p,'outcome');one(p,'authorization');one(p,'attempt',True)
    def emission(p):
        fields(p,{'delivery','phase'});ident(p);require(p['phase'] in ('intent','emitted','failed','unknown'),'notice-phase')
        one(p,'event');one(p,'previous',True)
        require(bool(p['links']['previous'])==(p['phase']!='intent'),'notice-emission-order')
    single=lambda kind:frozenset({kind})
    return [
        Schema('delivery.request',1,{'head':'decision','registration':'decision','prepared':'decision','grant':'decision'},request,
            {'head':single('work.head'),'registration':single('workspace.registration'),'prepared':single('work.head'),'grant':single('execution.grant')}),
        Schema('delivery.authorization',1,{'request':'decision'},authorization,{'request':single('delivery.request')}),
        Schema('delivery.attempt',1,{'request':'decision','authorization':'decision'},attempt,{'request':single('delivery.request'),'authorization':single('delivery.authorization')}),
        Schema('delivery.state',1,{'request':'decision','authorization':'decision','attempt':'decision','owner':'decision','outcome':'decision','previous':'provenance'},state,
            {'request':single('delivery.request'),'authorization':single('delivery.authorization'),'attempt':single('delivery.attempt'),'owner':single('effect.owner'),
             'outcome':single('delivery.outcome'),'previous':single('delivery.state')}),
        Schema('delivery.cancel',1,{'request':'decision'},cancel,{'request':single('delivery.request')}),
        Schema('delivery.outcome',1,{'request':'decision','head':'decision','execution':'decision'},outcome,
            {'request':single('delivery.request'),'head':single('work.head'),'execution':single('execution.state')}),
        Schema('notice.event',1,{'outcome':'decision','authorization':'decision','attempt':'decision'},notice,
            {'outcome':single('delivery.outcome'),'authorization':single('delivery.authorization'),'attempt':single('delivery.attempt')}),
        Schema('notice.emission',1,{'event':'decision','previous':'provenance'},emission,
            {'event':single('notice.event'),'previous':single('notice.emission')})]
