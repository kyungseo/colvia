"""Operation locality and complete-history integrity are different contracts."""
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch, MagicMock

from colvia.codec import Edge, RecordError, encode_envelope, object_ref, require
from colvia.graph import AuditBudget, ClosurePolicy, GraphAudit, Registry, Schema, validate_closure


def registry():
    def payload(p):
        require(set(p)=={'links','number'} and type(p['number']) is int,'bad-node')
    return Registry([Schema('test.node',1,{'previous':'provenance','body':'integrity'},payload,
                            {'previous':frozenset({'test.node'}),'body':None})])


def node(previous=None, body=None, number=0):
    edges=[]; links={'previous':[],'body':[]}
    for field,role,ref in [('previous','provenance',previous),('body','integrity',body)]:
        if ref:
            links[field]=[len(edges)]; edges.append(Edge(role,ref))
    return encode_envelope('test.node',1,dict(links=links,number=number),tuple(edges))


class GraphTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(prefix='graph-'); self.handles=[]
    def tearDown(self):
        for handle in self.handles: handle.close()
        self.tmp.cleanup()
    def audit(self, **limits):
        h=GraphAudit(Path(self.tmp.name)/f'audit-{len(self.handles)}.sqlite3',
                     AuditBudget(**(dict(objects=10000,edges=10000,total_bytes=8*1024*1024)|limits)))
        self.handles.append(h); return h
    def history(self,count):
        values={}; root=None
        for i in range(count):
            root,raw=node(root,number=i); values[root]=raw
        return root,values

    def test_selected_query_does_not_expand_provenance(self):
        root,values=self.history(200); seen=[]
        def load(ref): seen.append(ref); return values[ref]
        validate_closure([root],load,registry(),ClosurePolicy({('test.node',1):frozenset({'body'})}))
        self.assertEqual([root],seen)
        with self.assertRaisesRegex(RecordError,'decision-depth-limit'):
            validate_closure([root],load,registry(),ClosurePolicy({('test.node',1):frozenset({'body','previous'})}))

    def test_full_audit_preserves_deep_history_without_depth64(self):
        root,values=self.history(300)
        audit=self.audit().run(root,values.__getitem__,registry())
        self.assertEqual(300,audit.count)
        self.assertEqual(set(values),set(audit.refs()))
        self.assertEqual(sorted(values,key=lambda r:(r.kind,r.version,r.sha256)),list(audit.refs()))

    def test_unknown_optional_payload_and_edges_preserved(self):
        chunk=object_ref('body.chunk',1,b'opaque'); values={chunk:b'opaque'}
        future,raw=encode_envelope('future.note',9,{'uninterpreted':True},(Edge('provenance',chunk),))
        values[future]=raw
        audit=self.audit().run(future,values.__getitem__,registry())
        self.assertEqual({future,chunk},set(audit.refs()))
        with self.assertRaisesRegex(RecordError,'unknown-required-kind'):
            validate_closure([future],values.__getitem__,registry(),ClosurePolicy({}))

    def test_required_role_cannot_be_omitted_or_demoted(self):
        root,values=self.history(1)
        with self.assertRaisesRegex(RecordError,'operation-omits-required-field'):
            validate_closure([root],values.__getitem__,registry(),ClosurePolicy({('test.node',1):frozenset()}))
        chunk=object_ref('body.chunk',1,b'x')
        ref,raw=encode_envelope('test.node',1,dict(number=0,links={'previous':[],'body':[0]}),
                               (Edge('display',chunk),))
        with self.assertRaisesRegex(RecordError,'edge-role-mismatch'):
            self.audit().run(ref,{ref:raw,chunk:b'x'}.__getitem__,registry())

    def test_missing_or_corrupt_optional_history_refuses_complete_audit(self):
        root,values=self.history(3)
        oldest=next(iter(values)); values[oldest]+=b' '
        with self.assertRaisesRegex(RecordError,'object-identity-mismatch'):
            self.audit().run(root,values.__getitem__,registry())
        values.pop(oldest)
        def load(ref):
            if ref not in values: raise RecordError('object-unavailable')
            return values[ref]
        with self.assertRaisesRegex(RecordError,'object-unavailable'):
            self.audit().run(root,load,registry())

    def test_limits_at_below_above_and_cancel_do_not_report_success(self):
        root,values=self.history(5); total=sum(map(len,values.values()))
        self.audit(objects=5,edges=4,total_bytes=total).run(root,values.__getitem__,registry())
        for limits in [dict(objects=4),dict(edges=3),dict(total_bytes=total-1)]:
            audit=self.audit(**limits)
            with self.assertRaises(RecordError): audit.run(root,values.__getitem__,registry())
            with self.assertRaisesRegex(RecordError,'audit-incomplete'): list(audit.refs())
        audit=self.audit()
        with self.assertRaisesRegex(RecordError,'audit-cancelled'):
            audit.run(root,values.__getitem__,registry(),cancelled=lambda:True)

    def test_shared_fanin_counted_once(self):
        child,raw=node(); values={child:raw}
        parent,raw=encode_envelope('future.parent',1,{},tuple(Edge('display',child) for _ in range(500)))
        values[parent]=raw
        audit=self.audit().run(parent,values.__getitem__,registry())
        self.assertEqual((2,1),(audit.count,audit.edge_count))

    def test_windows_audit_journal_boundary_refuses_before_create(self):
        base='/synthetic-audit-boundary/'
        for units in (251,252):
            path=Path(base+'a'*(units-len(base)))
            with patch('colvia.graph.sys.platform','win32'), patch('colvia.graph.os.open',side_effect=RuntimeError('creation reached')) as create:
                if units==251:
                    with self.assertRaisesRegex(RuntimeError,'creation reached'):GraphAudit(path,AuditBudget(10000,10000,8*1024*1024))
                    create.assert_called_once()
                else:
                    with self.assertRaisesRegex(RecordError,'audit-path-too-long'):GraphAudit(path,AuditBudget(10000,10000,8*1024*1024))
                    create.assert_not_called()
            self.assertFalse(path.exists())

    def test_initial_schema_error_closes_connection_preserves_file(self):
        path=Path(self.tmp.name)/'failed.db';db=MagicMock()
        db.executescript.side_effect=RuntimeError('synthetic ddl error')
        with patch('colvia.graph.sqlite3.connect',return_value=db),self.assertRaisesRegex(RuntimeError,'synthetic ddl error'):
            GraphAudit(path,AuditBudget(10000,10000,8*1024*1024))
        db.close.assert_called_once();self.assertTrue(path.exists())


if __name__=='__main__': unittest.main()
