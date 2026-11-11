"""Complete source Host composition through explicit synthetic OS/runtime ports."""
from unittest.mock import patch
from colvia.codec import RecordError
from colvia.effects import PENDING
from colvia.execution.host import DocumentHost
from test_foundation_execution_supervisor import ConversationIntegrationTests

class HostTests(ConversationIntegrationTests):
    def host(self):
        old=self.supervisor;backend=self.controller.native;backend.journal=self.journal
        return DocumentHost(self.journal,'run',backend=backend,launch=old.launch,policy=self.policy,
            runtime_processes=self.runtime,worker_processes=self.workers,channel_factory=old.channel_factory,
            session_factory=old.session_factory,worker_exchange=self.controller.exchange)
    def test_composed_host_connects_selected_grant_to_five_steps_and_closure(self):
        self.setup_conversation();host=self.host();result=host.run()
        self.assertEqual('completed',result['status']);self.assertFalse(result['accepted']);self.assertEqual(5,self.workers.launches)
        self.assertIsNone(self.store.head(PENDING))
    def test_binding_drift_before_model_spawn_stops_without_process(self):
        self.setup_conversation();host=self.host();host.supervisor.launch.bad=True
        with self.assertRaisesRegex(RecordError,'resource-drift'):host.run()
        self.assertEqual(0,self.runtime.launches);self.assertEqual(0,self.workers.launches)
    def test_runtime_drift_after_write_preserves_applied_effect_without_completion(self):
        self.setup_conversation();host=self.host();backend=host.controller.native.backend;original=backend.validate_result
        def drift_after_write(grant,tool,*args):
            result=original(grant,tool,*args)
            if tool=='document_write':host.supervisor.launch.bad=True
            return result
        with patch.object(backend,'validate_result',side_effect=drift_after_write),self.assertRaisesRegex(RecordError,'resource-drift'):host.run()
        h=self.journal.read('run')[-1];self.assertEqual('applied',h.effect());self.assertNotEqual('completed',h.terminal)
        self.assertEqual(2,self.workers.launches);self.assertEqual('active',self.service._head('synthetic-work')[1].payload['phase'])

    def test_runtime_drift_before_write_result_collection_preserves_applied_evidence(self):
        self.setup_conversation();host=self.host();exchange=host.controller.exchange
        def drift_before_result(*args,**kwargs):
            result=exchange(*args,**kwargs)
            if host.controller.native.backend.tool=='document_write':host.supervisor.launch.bad=True
            return result
        host.controller.exchange=drift_before_result
        with self.assertRaisesRegex(RecordError,'resource-drift'):host.run()
        h=self.journal.read('run')[-1];self.assertEqual('applied',h.effect());self.assertEqual(2,len(h.completed_refs))
        self.assertNotEqual('completed',h.terminal);self.assertEqual(2,self.workers.launches)
