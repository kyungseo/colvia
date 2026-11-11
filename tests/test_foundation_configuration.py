"""Feature selection preserves history and participates in writer admission."""
import unittest
from colvia.codec import RecordError
from colvia.configuration import Configuration,enabled
from test_foundation_execution_store import JournalFixture
from test_foundation_execution_history import Chain

class ConfigurationTests(JournalFixture,unittest.TestCase):
    def configure(self,features,operation='configure'):
        config=Configuration(self.store);p=config.preview(features)
        return config.apply(operation=operation,features=features,receipt=p['receipt'],statement='Use this feature selection')
    def test_disabled_execution_refuses_but_ordinary_work_remains(self):
        self.configure([])
        with self.assertRaisesRegex(RecordError,'feature-not-enabled'):self.prepare()
        self.assertEqual('active',self.service.view('synthetic-work')['state'])
    def test_prepared_grant_cannot_start_after_feature_disabled(self):
        p=self.prepare();self.configure([])
        with self.assertRaisesRegex(RecordError,'feature-not-enabled'):
            self.journal.start(operation='attempt',run='run',receipt=p['receipt'],statement='Run')
    def test_active_effect_blocks_configuration_mutation(self):
        self.launch();before=self.store.root().ref
        with self.assertRaisesRegex(RecordError,'external-effect-pending'):self.configure([])
        self.assertEqual(before,self.store.root().ref)
    def test_disable_after_closure_preserves_evidence_and_read_requirements(self):
        self.launch();chain=Chain(self.contract);chain.terminal('revoked-before-launch');self.publish(chain)
        before=self.store.requirements();status=self.journal.status('run');self.configure([])
        self.assertEqual(status,self.journal.status('run'));self.assertEqual(before,self.store.requirements())
        self.assertEqual(frozenset(),enabled(self.store))
    def test_stale_preview_and_unavailable_feature_refuse(self):
        config=Configuration(self.store);p=config.preview([]);self.configure(['official-execution'])
        with self.assertRaisesRegex(RecordError,'configuration-preview-changed'):
            config.apply(operation='stale',features=[],receipt=p['receipt'],statement='Change')
        with self.assertRaisesRegex(RecordError,'runtime-feature-unavailable'):
            Configuration(self.store,available=()).preview(['official-execution'])

    def test_configuration_change_after_preview_cannot_be_overwritten(self):
        from unittest.mock import patch
        config=Configuration(self.store);original=config.preview;receipt=original([])['receipt']
        def raced(features):
            result=original(features)
            self.configure(['official-execution'],operation='concurrent')
            return result
        with patch.object(config,'preview',side_effect=raced):
            with self.assertRaisesRegex(RecordError,'head-conflict'):
                config.apply(operation='raced',features=[],receipt=receipt,statement='Earlier selection')
        self.assertEqual(frozenset({'official-execution'}),enabled(self.store))
