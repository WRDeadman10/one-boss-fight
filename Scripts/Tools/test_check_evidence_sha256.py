"""Synthetic containment contracts for SHA-256 evidence manifests."""
import hashlib
from pathlib import Path
import tempfile
import unittest

from Scripts.Tools.check_evidence_sha256 import check_manifest


class EvidenceSha256ManifestTests(unittest.TestCase):
    def test_valid_in_root_entry_passes(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary) / "pack"
            root.mkdir()
            payload = root / "receipt.txt"
            payload.write_text("synthetic evidence", encoding="utf-8")
            digest = hashlib.sha256(payload.read_bytes()).hexdigest()
            manifest = root / "evidence_sha256.txt"
            manifest.write_text(f"{digest}  receipt.txt\n", encoding="utf-8")
            self.assertEqual(check_manifest(manifest), [])

    def test_utf8_bom_manifest_passes(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary) / "pack"
            root.mkdir()
            payload = root / "receipt.txt"
            payload.write_text("synthetic evidence", encoding="utf-8")
            digest = hashlib.sha256(payload.read_bytes()).hexdigest()
            manifest = root / "evidence_sha256.txt"
            manifest.write_text(f"\ufeff{digest}  receipt.txt\n", encoding="utf-8")
            self.assertEqual(check_manifest(manifest), [])

    def test_parent_traversal_is_rejected_even_when_hash_matches(self):
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            root = base / "pack"
            root.mkdir()
            outside = base / "outside.txt"
            outside.write_text("must not be admitted", encoding="utf-8")
            digest = hashlib.sha256(outside.read_bytes()).hexdigest()
            manifest = root / "evidence_sha256.txt"
            manifest.write_text(f"{digest}  ../outside.txt\n", encoding="utf-8")
            issues = check_manifest(manifest)
            self.assertEqual(len(issues), 1)
            self.assertIn("unsafe path escapes manifest root", issues[0])

    def test_unreadable_manifest_returns_a_failure(self):
        with tempfile.TemporaryDirectory() as temporary:
            missing = Path(temporary) / "missing.txt"
            issues = check_manifest(missing)
            self.assertEqual(len(issues), 1)
            self.assertIn("cannot read manifest", issues[0])


if __name__ == "__main__":
    unittest.main(verbosity=2)
