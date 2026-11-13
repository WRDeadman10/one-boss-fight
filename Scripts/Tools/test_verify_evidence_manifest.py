from __future__ import annotations

import hashlib
import json
from pathlib import Path
import tempfile
import unittest

from Scripts.Tools import verify_evidence_manifest as verifier


class EvidenceManifestSafetyTests(unittest.TestCase):
    def test_manifest_reports_invalid_utf8_instead_of_raising(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            manifest = Path(temp) / "evidence_manifest.json"
            manifest.write_bytes(b"\xff\xfe")
            issues = verifier.verify(manifest)
            self.assertEqual(len(issues), 1)
            self.assertIn("cannot read manifest", issues[0])

    def test_manifest_rejects_parent_traversal_and_absolute_paths(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            outside = root.parent / (root.name + "_outside.txt")
            outside.write_text("outside", encoding="utf-8")
            manifest = root / "evidence_manifest.json"
            manifest.write_text(json.dumps({"schema": 1, "files": [
                {"file": "../" + outside.name, "sha256": hashlib.sha256(b"outside").hexdigest()},
                {"file": str(outside), "sha256": hashlib.sha256(b"outside").hexdigest()},
            ]}), encoding="utf-8")
            issues = verifier.verify(manifest, require_bytes=True)
            self.assertEqual(len([issue for issue in issues if "unsafe path" in issue]), 2)

    def test_source_reference_requires_listed_identity_and_matching_hash(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            source = root / "source.log"
            source.write_text("same run", encoding="utf-8")
            receipt = root / "receipt.json"
            receipt.write_text(json.dumps({"source_log": "source.log",
                                          "source_log_sha256": hashlib.sha256(b"wrong").hexdigest()}), encoding="utf-8")
            manifest = root / "evidence_manifest.json"
            manifest.write_text(json.dumps({"schema": 1, "files": [
                {"file": "receipt.json", "sha256": hashlib.sha256(receipt.read_bytes()).hexdigest()}
            ]}), encoding="utf-8")
            issues = verifier.verify(manifest, verify_source_references=True)
            self.assertTrue(any("source is not listed" in issue for issue in issues))

            manifest.write_text(json.dumps({"schema": 1, "files": [
                {"file": "receipt.json", "sha256": hashlib.sha256(receipt.read_bytes()).hexdigest()},
                {"file": "source.log", "sha256": hashlib.sha256(source.read_bytes()).hexdigest()}
            ]}), encoding="utf-8")
            issues = verifier.verify(manifest, verify_source_references=True)
            self.assertTrue(any("SHA-256 mismatch" in issue for issue in issues))

    def test_source_reference_parent_traversal_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            outside = root.parent / (root.name + "_outside.log")
            outside.write_text("outside", encoding="utf-8")
            receipt = root / "receipt.json"
            receipt.write_text(json.dumps({"source_log": "../" + outside.name,
                                          "source_log_sha256": "0" * 64}), encoding="utf-8")
            manifest = root / "evidence_manifest.json"
            manifest.write_text(json.dumps({"schema": 1, "files": [
                {"file": "receipt.json", "sha256": hashlib.sha256(receipt.read_bytes()).hexdigest()}
            ]}), encoding="utf-8")
            issues = verifier.verify(manifest, verify_source_references=True)
            self.assertTrue(any("path escapes evidence root" in issue for issue in issues))
            outside.unlink()

    def test_manifest_symlink_escape_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            outside = root.parent / (root.name + "_outside.txt")
            outside.write_text("outside", encoding="utf-8")
            link = root / "linked.txt"
            try:
                link.symlink_to(outside)
            except (OSError, NotImplementedError) as error:
                self.skipTest(f"symlink creation unavailable: {error}")
            manifest = root / "evidence_manifest.json"
            manifest.write_text(json.dumps({"schema": 1, "files": [
                {"file": "linked.txt", "sha256": hashlib.sha256(b"outside").hexdigest()}
            ]}), encoding="utf-8")
            issues = verifier.verify(manifest)
            self.assertTrue(any("unsafe path" in issue and "linked.txt" in issue for issue in issues))
            outside.unlink()


if __name__ == "__main__":
    unittest.main(verbosity=2)
