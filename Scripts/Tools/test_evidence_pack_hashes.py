from __future__ import annotations

import hashlib
import tempfile
import unittest
from pathlib import Path

from evidence_pack_hashes import write_manifest


class EvidencePackHashesTests(unittest.TestCase):
    def test_writes_relative_hash_manifests_for_separate_roots(self):
        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp)
            roots = [base / "build", base / "parity"]
            for root in roots:
                (root / "nested").mkdir(parents=True)
                (root / "nested" / "log.txt").write_text(root.name, encoding="utf-8")
            outputs = [write_manifest(root) for root in roots]
            for root, (manifest, count) in zip(roots, outputs):
                self.assertEqual(count, 1)
                expected = hashlib.sha256((root / "nested" / "log.txt").read_bytes()).hexdigest()
                self.assertEqual(manifest.read_text(encoding="utf-8"), f"{expected}  nested/log.txt\n")

    def test_refuses_to_overwrite_existing_manifest(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "evidence_sha256.txt").write_text("keep", encoding="utf-8")
            with self.assertRaises(FileExistsError):
                write_manifest(root)
            self.assertEqual((root / "evidence_sha256.txt").read_text(encoding="utf-8"), "keep")


if __name__ == "__main__":
    unittest.main()
