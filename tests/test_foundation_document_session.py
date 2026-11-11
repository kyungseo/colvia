"""Synthetic app-server responses exercise real persistent admission, no model."""
import copy,json,unittest
from colvia.codec import RecordError
from colvia.effects import PENDING
from colvia.execution.callbacks import CallbackGate
from colvia.adapters.document_session import DocumentSession
from test_foundation_execution_store import JournalFixture
from test_foundation_execution_history import BIRTH
from test_foundation_execution_callbacks import NativeDouble
import test_foundation_execution_admission as admission

class ChannelDouble:
    def __init__(self,responses):self.responses=responses;self.queue=[];self.sent=[];self.prefix={};self.failed=False
    def check(self):
        if self.failed:raise RecordError('protocol_refused')
    def write(self,raw):
        frame=json.loads(raw);self.sent.append(frame)
        if 'id' in frame and 'method' in frame:
            method=frame['method'];self.queue.extend(copy.deepcopy(self.prefix.get(method,[])))
            self.queue.append(dict(id=frame['id'],result=copy.deepcopy(self.responses[method])))
        return len(raw)
    def read(self,deadline):
        if not self.queue:raise TimeoutError('synthetic empty channel')
        return self.queue.pop(0)

class SessionTests(JournalFixture,unittest.TestCase):
    def setup_session(self):
        policy,contract,config,account,models=admission.AdmissionTests().fixture()
        self.contract['capability']=contract['capability']
        self.launch();self.gate=CallbackGate(self.journal,'run',NativeDouble())
        self.gate.append('runtime-reserved',dict(ordinal=1,host_pid=9000,host_birth=BIRTH))
        self.gate.append('runtime-started',dict(ordinal=1,pid=9001,birth=BIRTH))
        self.channel=ChannelDouble({'initialize':{},'config/read':{'config':config},'account/read':account,
            'model/list':models,'thread/start':{'model':policy.model,'thread':{'id':'thread'}},
            'turn/start':{'turn':{'id':'turn'}},'turn/interrupt':{}})
        self.session=DocumentSession(self.gate,policy,self.channel,cwd='/synthetic-runtime')
    def test_begin_records_admission_and_one_turn_without_accepting_work(self):
        self.setup_session();self.session.begin();history=self.journal.read('run')[-1]
        self.assertTrue(history.bound);self.assertEqual('thread',self.gate.thread)
        self.assertEqual(6,len(history.rpc));self.assertEqual(7,len(self.channel.sent))
        self.assertNotIn('synthetic@example.invalid',str(history.rows))
        self.assertEqual('active',self.service._head('synthetic-work')[1].payload['phase'])
        self.assertIsNotNone(self.store.head(PENDING))
    def test_enabled_native_tool_refuses_before_thread_or_model_turn(self):
        self.setup_session();self.channel.responses['config/read']['config']['features']['shell_tool']=True
        with self.assertRaisesRegex(RecordError,'feature-mismatch'):self.session.run(None)
        history=self.journal.read('run')[-1];self.assertNotIn('thread/start',history.rpc)
        self.assertNotIn('turn/start',history.rpc);self.assertTrue(self.session.failed)
    def test_callback_before_turn_response_is_held_until_exact_binding(self):
        self.setup_session();message=dict(id='callback',method='item/tool/call',params=dict(threadId='thread',turnId='turn',
            callId='first',tool='document_read',arguments={'file_ids':['Output','Reference']}))
        self.channel.prefix['turn/start']=[message];self.session.begin()
        self.assertEqual(message,self.session.event());self.assertIsNone(self.journal.read('run')[-1].pending)
        wrong=dict(message['params'],turnId='other')
        with self.assertRaisesRegex(RecordError,'caller_mismatch'):self.gate.reserve(wrong)
    def test_unsolicited_request_native_item_warning_and_wrong_turn_refuse(self):
        self.setup_session();self.session.begin()
        for message in (dict(id=7,method='command/exec',params={}),dict(method='warning',params={'message':'unqualified'}),
                dict(method='item/started',params={'item':{'type':'commandExecution'}}),
                dict(method='turn/completed',params={'threadId':'thread','turn':{'id':'other','status':'completed'}})):
            with self.subTest(method=message['method']),self.assertRaises(RecordError):self.session.notification(message)
    def test_cancel_sends_no_document_reply_but_can_confirm_interrupt(self):
        self.setup_session();self.session.begin()
        self.journal.cancel(operation='cancel-session',run='run',reason='cancelled')
        count=len(self.channel.sent)
        with self.assertRaisesRegex(RecordError,'cancelled'):self.session.reply({'id':10},{'files':[]})
        self.assertEqual(count,len(self.channel.sent))
        self.channel.prefix['turn/interrupt']=[dict(method='turn/completed',params={'threadId':'thread','turn':{'id':'turn','status':'interrupted'}})]
        self.assertEqual('interrupted',self.session.interrupt())
        self.assertIsNotNone(self.store.head(PENDING)) # completion still needs native closure
    def test_unexpected_rpc_id_cannot_complete_admission(self):
        self.setup_session();self.channel.prefix['initialize']=[dict(id=999,result={})]
        with self.assertRaises(RecordError):self.session.run(None)
        history=self.journal.read('run')[-1];self.assertIsNone(history.admission)
        self.assertTrue(self.session.failed)

    def test_cancel_inside_run_can_interrupt_without_replaying_document_reply(self):
        self.setup_session();message=dict(id='callback',method='item/tool/call',params=dict(threadId='thread',turnId='turn',
            callId='first',tool='document_read',arguments={'file_ids':['Output','Reference']}))
        self.channel.prefix['turn/start']=[message];fixture=self
        class Controller:
            def dispatch(self,reservation):
                fixture.journal.cancel(operation='cancel-in-run',run='run',reason='cancelled')
                return {'files':[]}
        with self.assertRaisesRegex(RecordError,'cancelled'):self.session.run(Controller())
        self.channel.prefix['turn/interrupt']=[dict(method='turn/completed',params={'threadId':'thread','turn':{'id':'turn','status':'interrupted'}})]
        self.assertEqual('interrupted',self.session.interrupt());self.assertFalse(self.session.failed)
        self.assertFalse(any(frame.get('id')=='callback' for frame in self.channel.sent))
        self.assertEqual(1,len([frame for frame in self.channel.sent if frame.get('method')=='turn/start']))
