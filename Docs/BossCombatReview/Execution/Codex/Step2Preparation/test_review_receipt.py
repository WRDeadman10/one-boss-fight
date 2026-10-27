"""Fake-file tests only, confined to a temporary child of this Codex-owned directory."""
import hashlib
from pathlib import Path
import tempfile
import unittest
from review_receipt import collect_receipt

class ReceiptTests(unittest.TestCase):
    def setUp(self):
        self.parent = Path(__file__).resolve().parent
        self.temp = tempfile.TemporaryDirectory(prefix='receipt_test_', dir=self.parent)
        self.root = Path(self.temp.name).resolve()
        assert self.root.is_relative_to(self.parent.resolve())
        self.raw = b'raw\r\nbytes\n\x00\xff'
        (self.root/'known.bin').write_bytes(self.raw)

    def tearDown(self):
        assert self.root.is_relative_to(self.parent.resolve())
        self.temp.cleanup()

    def test_raw_binary_and_eol_unchanged(self):
        result=collect_receipt(self.root,['known.bin'])
        self.assertEqual(result['errors'],[])
        self.assertEqual(result['files'][0]['sha256'],hashlib.sha256(self.raw).hexdigest())
        self.assertEqual((self.root/'known.bin').read_bytes(),self.raw)

    def test_expected_match(self):
        result=collect_receipt(self.root,[{'path':'known.bin','sha256':hashlib.sha256(self.raw).hexdigest().upper()}])
        self.assertEqual(result['errors'],[])
        self.assertTrue(result['files'][0]['matches_claim'])

    def test_expected_mismatch_preserves_actual(self):
        result=collect_receipt(self.root,[{'path':'known.bin','sha256':'0'*64}])
        self.assertTrue(result['errors'])
        self.assertFalse(result['files'][0]['matches_claim'])
        self.assertEqual(result['files'][0]['sha256'],hashlib.sha256(self.raw).hexdigest())

    def test_missing_and_directory(self):
        result=collect_receipt(self.root,['missing','known.bin','.'])
        self.assertEqual(len(result['errors']),2)
        self.assertEqual(len(result['files']),1)

    def test_invalid_claims(self):
        for claims in [[],None,[{}],[{'path':'known.bin','sha256':'short'}],[None]]:
            with self.subTest(claims=claims):
                self.assertTrue(collect_receipt(self.root,claims)['errors'])

    def test_escape_and_absolute_and_stream_refused(self):
        for path in ['../escape',str(self.root/'known.bin'),'known.bin:stream']:
            with self.subTest(path=path):
                self.assertTrue(collect_receipt(self.root,[path])['errors'])

    def test_duplicate_alias(self):
        result=collect_receipt(self.root,['known.bin','./known.bin'])
        self.assertEqual(len(result['files']),1)
        self.assertIn('duplicate',result['errors'][0])

    def test_unicode_filename(self):
        (self.root/'évidence.txt').write_bytes(self.raw)
        self.assertEqual(collect_receipt(self.root,['évidence.txt'])['errors'],[])

if __name__ == '__main__':
    unittest.main(verbosity=2)
