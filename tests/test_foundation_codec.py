"""Pure C2 regression oracles: no repository, platform or authority writes."""
import unittest

from colvia.codec import (
    CHUNK_LIMIT, METADATA_LIMIT, Edge, ObjectRef, RecordError, canonical_bytes,
    decode_canonical, decode_envelope, encode_envelope, object_ref,
    validate_schema, verify_object,
)


class CanonicalRecordTests(unittest.TestCase):
    def test_order_and_unicode_have_one_encoding(self):
        a = {"제목": "보고서", "a": [1, True, None, {"x": -3}]}
        b = {"a": [1, True, None, {"x": -3}], "제목": "보고서"}
        self.assertEqual(canonical_bytes(a), canonical_bytes(b))
        self.assertEqual(a, decode_canonical(canonical_bytes(a)))

    def test_noncanonical_or_ambiguous_json_refused(self):
        for raw in (b'{"a": 1}\n', b'{"a":1,"a":2}', b'{}', b'{}\n\n',
                    b'\xef\xbb\xbf{}\n', b'NaN\n', b'Infinity\n', b'1.0\n',
                    b'"\\ud800"\n', b'\xff'):
            with self.subTest(raw=raw), self.assertRaises(RecordError):
                decode_canonical(raw)

    def test_encoder_rejects_non_contract_types_and_size(self):
        recursive = []; recursive.append(recursive)
        for value in ({1: "key"}, (1, 2), 1.2, float('nan'), b'raw', "\ud800", recursive):
            with self.subTest(type=type(value).__name__), self.assertRaises(RecordError):
                canonical_bytes(value)
        with self.assertRaisesRegex(RecordError, 'metadata-size-limit'):
            canonical_bytes('a' * METADATA_LIMIT)

    def test_content_domain_separates_kind_and_version(self):
        raw = canonical_bytes({})
        refs = [object_ref('test.a', 1, raw), object_ref('test.b', 1, raw),
                object_ref('test.a', 2, raw)]
        self.assertEqual(3, len({r.sha256 for r in refs}))
        verify_object(refs[0], raw)
        with self.assertRaisesRegex(RecordError, 'object-identity-mismatch'):
            verify_object(refs[0], raw + b' ')

    def test_reference_exact_fields_and_boolean_rejection(self):
        valid = object_ref('test.a', 1, b'{}\n').as_dict()
        self.assertEqual(valid, ObjectRef.parse(valid).as_dict())
        for key, value in [('version', True), ('byte_length', False), ('sha256', 'A'*64),
                           ('kind', 'Bad'), ('version', 0), ('extra', 1)]:
            with self.subTest(key=key), self.assertRaises(RecordError):
                ObjectRef.parse(dict(valid, **{key: value}))

    def test_raw_chunk_preserves_bytes_and_bound(self):
        raw = bytes(range(256)) * (CHUNK_LIMIT // 256)
        ref = object_ref('body.chunk', 1, raw)
        verify_object(ref, raw)
        with self.assertRaises(RecordError): object_ref('body.chunk', 1, raw + b'x')
        with self.assertRaisesRegex(RecordError, 'chunk-is-raw'):
            decode_envelope(ref, raw)


class EnvelopeRoleTests(unittest.TestCase):
    def setUp(self):
        self.child = object_ref('body.chunk', 1, b'synthetic')

    def envelope(self, role='integrity', **changes):
        payload = dict(links={'content': [0]}, title='Report')
        payload.update(changes)
        ref, raw = encode_envelope('result', 1, payload, (Edge(role, self.child),))
        return decode_envelope(ref, raw)

    def validate(self, obj):
        def payload_check(payload):
            if set(payload) != {'links', 'title'} or type(payload['title']) is not str:
                raise RecordError('invalid-result-payload')
        validate_schema(obj, kind='result', version=1,
                        fields={'content': 'integrity'}, validate_payload=payload_check)

    def test_role_demotion_rejected_on_read(self):
        self.validate(self.envelope())
        with self.assertRaisesRegex(RecordError, 'edge-role-mismatch'):
            self.validate(self.envelope('display'))
        self.assertNotEqual(self.envelope().ref.sha256, self.envelope('display').ref.sha256)

    def test_unknown_optional_kind_preserved_without_interpretation(self):
        ref, raw = encode_envelope('future.note', 2, {'links': {}, 'note': 'opaque'})
        obj = decode_envelope(ref, raw)
        self.assertEqual((ref, raw), encode_envelope(ref.kind, ref.version, obj.payload, obj.edges))
        with self.assertRaisesRegex(RecordError, 'unknown-required-kind'):
            self.validate(obj)

    def test_unknown_role_and_hidden_reference_refused(self):
        with self.assertRaisesRegex(RecordError, 'unknown-edge-role'):
            Edge('optional-secretly-required', self.child)
        with self.assertRaisesRegex(RecordError, 'hidden-object-reference'):
            self.validate(self.envelope(title={'nested': self.child.as_dict()}))

    def test_indices_are_complete_unique_and_typed(self):
        for links in ({'content': []}, {'content': [0, 0]}, {'content': [True]},
                      {'content': [-1]}, {'content': [1]}, {'different': [0]}):
            with self.subTest(links=links), self.assertRaises(RecordError):
                self.validate(self.envelope(links=links))

    def test_tamper_and_unknown_envelope_fields_refused(self):
        ref, raw = encode_envelope('result', 1, {'links': {}})
        value = decode_canonical(raw)
        for patch in ({'envelope_version': True}, {'envelope_version': 2}, {'extra': 1}):
            modified = canonical_bytes(dict(value, **patch))
            with self.subTest(patch=patch), self.assertRaises(RecordError):
                decode_envelope(object_ref('result', 1, modified), modified)
        with self.assertRaises(RecordError):
            decode_envelope(ref, raw.replace(b'payload', b'changed'))


if __name__ == '__main__':
    unittest.main()
