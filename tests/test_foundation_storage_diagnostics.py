"""Engine diagnostic privacy and unchanged failure/uncertain outcome contracts."""
import contextlib
import io
import json
import sqlite3
import threading
import unittest
from unittest.mock import patch

from colvia.codec import PublicationRefused
from colvia.storage.sqlite import GenerationStore, StorageError, _sql_error, _refused
from colvia.cli import main


def engine(name):
    exc=sqlite3.OperationalError('SECRET /private/account/db.sqlite SELECT password')
    exc.sqlite_errorname=name
    exc.sqlite_errorcode=getattr(sqlite3,name)
    return exc


class StorageDiagnosticsTests(unittest.TestCase):
    def test_allowed_engine_facts_do_not_include_raw_message_or_path(self):
        cases={'SQLITE_BUSY':'store-busy','SQLITE_LOCKED':'store-busy',
               'SQLITE_READONLY_ROLLBACK':'recovery-required',
               'SQLITE_READONLY_DBMOVED':'store-file-replaced','SQLITE_CORRUPT':'store-corrupt',
               'SQLITE_FULL':'store-full','SQLITE_CANTOPEN':'store-io-unavailable',
               'SQLITE_READONLY':'store-io-unavailable','SQLITE_IOERR':'store-io-unavailable'}
        for name,code in cases.items():
            with self.subTest(name=name):
                err=_sql_error(engine(name),'/private/SECRET',stage='open')
                self.assertEqual(code,err.code)
                self.assertEqual({'stage':'open','sqlite_code':getattr(sqlite3,name),'sqlite_name':name},err.diagnostic)
                self.assertNotIn('SECRET',str(err)+json.dumps(err.diagnostic))
                self.assertEqual('store-outcome-unknown',_sql_error(engine(name),None,uncertain=True).code)

    def test_missing_or_invalid_attributes_remain_unavailable(self):
        for name,code in [(None,None),('SQLITE_IOERR_SECRET',10),('SQLITE_IOERR',True),
                          ('SQLITE_IOERR','10'),('SQLITE_IOERR',-1),('SQLITE_IOERR',2**40),
                          ('SQLITE_IOERR',sqlite3.SQLITE_BUSY)]:
            exc=sqlite3.Error('SECRET');exc.sqlite_errorname=name;exc.sqlite_errorcode=code
            err=_sql_error(exc,'SECRET',stage='SECRET')
            self.assertIsNone(err.diagnostic['sqlite_name'])
            self.assertEqual('transaction',err.diagnostic['stage'])
            self.assertNotIn('SECRET',json.dumps(err.diagnostic))

    def test_publication_refusal_preserves_diagnostic_and_refusal_semantics(self):
        err=_sql_error(engine('SQLITE_FULL'),None)
        wrapped=_refused(err)
        self.assertIsInstance(wrapped,PublicationRefused)
        self.assertIsInstance(wrapped,StorageError)
        self.assertEqual(err.diagnostic,wrapped.diagnostic)

    def test_commit_failure_stays_unknown_even_after_rollback(self):
        class DB:
            in_transaction=False
            def execute(self,sql):
                if sql=='BEGIN IMMEDIATE':self.in_transaction=True
                if sql=='COMMIT':raise engine('SQLITE_IOERR')
                if sql=='ROLLBACK':self.in_transaction=False
        store=object.__new__(GenerationStore);store.db=DB();store.readonly=False
        store.path=None;store.process_lock=threading.RLock();store._guard=lambda **kw:None
        with self.assertRaises(StorageError) as caught:
            with store._transaction_inner(write=True):pass
        self.assertEqual('store-outcome-unknown',caught.exception.code)
        self.assertEqual('commit',caught.exception.diagnostic['stage'])
        self.assertNotIsInstance(caught.exception,PublicationRefused)

    def test_failed_rollback_never_reports_safe_retry(self):
        class DB:
            in_transaction=False
            def execute(self,sql):
                if sql=='BEGIN IMMEDIATE':self.in_transaction=True
                if sql=='ROLLBACK':raise engine('SQLITE_IOERR')
        store=object.__new__(GenerationStore);store.db=DB();store.readonly=False
        store.path=None;store.process_lock=threading.RLock();store._guard=lambda **kw:None
        with self.assertRaises(StorageError) as caught:
            with store._transaction_inner(write=True):raise engine('SQLITE_FULL')
        self.assertEqual('store-outcome-unknown',caught.exception.code)
        self.assertEqual('transaction',caught.exception.diagnostic['stage'])

    def test_cli_json_keeps_details_and_human_does_not_guess_permissions(self):
        args=['--source-development','--authority','unused','--project','p',
              '--workspace','w','--root','unused','ordinary','list']
        for machine in (False,True):
            out=io.StringIO()
            with patch('colvia.cli.Authority',side_effect=_sql_error(engine('SQLITE_CANTOPEN'),None,stage='open')),contextlib.redirect_stdout(out):
                code=main((['--json'] if machine else [])+args)
            self.assertEqual(2,code)
            value=json.loads(out.getvalue()) if machine else None
            if machine:self.assertEqual('SQLITE_CANTOPEN',value['storage_diagnostic']['sqlite_name'])
            for private in ('SECRET','/private/','허용해 주세요','권한 문제','SQLITE_CANTOPEN' if not machine else 'SELECT password'):
                self.assertNotIn(private,out.getvalue())
            self.assertIn('원인은 아직 확정되지 않았습니다',out.getvalue())

    def test_unknown_cli_failure_without_explicit_operation_still_reports_id(self):
        out=io.StringIO()
        with patch('colvia.cli.Authority',side_effect=RuntimeError('SECRET')),contextlib.redirect_stdout(out):
            code=main(['--source-development','--json','--authority','unused','--project','p',
                       '--workspace','w','--root','unused','ordinary','list'])
        value=json.loads(out.getvalue());self.assertEqual(2,code)
        self.assertEqual('command-outcome-unknown',value['error'])
        self.assertTrue(value['operation'].startswith('op-'))
        self.assertNotIn('SECRET',out.getvalue())

if __name__=='__main__':unittest.main()
