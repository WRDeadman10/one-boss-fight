"""BK-221..225 (C, implementer; X-2068): compatibility regressions for the E1-E8 hotfix in verify_evidence_manifest.py.

The E1-E8 behaviour itself is covered by test_bk216_220_evidence_manifest_audit.py (former expectedFailures, now
ordinary tests). This module pins the consumer contract: verify()'s signature and list-of-issues return, the existing
message phrases consumers and tests match on, and proof_report.evidence_stale_reasons() on top of it. Synthetic packs
in throwaway OS temp directories only; no real evidence pack, Unreal, build or PIE.
"""
import hashlib
import importlib.util
import inspect
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))  # proof_report does `from verify_evidence_manifest import verify`
import verify_evidence_manifest as M  # noqa: E402
import proof_report as PR  # noqa: E402
import evidence_pack as EP  # noqa: E402

DATA = b"run evidence\n"


def pack(manifest_obj=None, raw=None):
    tmp = tempfile.TemporaryDirectory()
    root = Path(tmp.name)
    (root / "run.log").write_bytes(DATA)
    manifest = root / "evidence_manifest.json"
    obj = manifest_obj if manifest_obj is not None else {
        "schema": 1, "files": [{"file": "run.log", "sha256": hashlib.sha256(DATA).hexdigest(), "bytes": len(DATA)}]}
    manifest.write_text(raw if raw is not None else json.dumps(obj), encoding="utf-8")
    return tmp, root, manifest


class VerifyContract(unittest.TestCase):
    def test_signature_is_unchanged(self):
        params = inspect.signature(M.verify).parameters
        self.assertEqual(list(params), ["manifest", "require_bytes", "verify_source_references", "strict_membership"])
        self.assertTrue(all(params[name].default is False for name in list(params)[1:]))

    def test_valid_pack_returns_an_empty_list(self):
        tmp, _root, manifest = pack()
        with tmp:
            result = M.verify(manifest, require_bytes=True, strict_membership=True)
            self.assertIsInstance(result, list)
            self.assertEqual(result, [])

    def test_invalid_pack_returns_string_issues_with_the_existing_phrases(self):
        cases = {
            "cannot read manifest": dict(raw='{"schema": 1, "files": [], "files": []}'),
            "invalid schema": dict(manifest_obj={"schema": True, "files": []}),
        }
        for phrase, kwargs in cases.items():
            tmp, _root, manifest = pack(**kwargs)
            with tmp, self.subTest(phrase=phrase):
                result = M.verify(manifest)
                self.assertTrue(result and all(isinstance(i, str) for i in result))
                self.assertTrue(any(phrase in i for i in result), result)

    def test_evidence_pack_output_is_accepted_and_malformed_label_refused(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            source = root / "source.log"
            output = root / "pack"
            source.write_bytes(DATA)
            with patch.object(sys, "argv", ["evidence_pack.py", str(source), str(output)]):
                self.assertEqual(EP.main(), 0)
            manifest = output / "evidence_manifest.json"
            data = json.loads(manifest.read_text(encoding="utf-8"))
            self.assertEqual(data["files"][0]["label"], "raw")
            self.assertEqual(M.verify(manifest, require_bytes=True, strict_membership=True), [])
            data["files"][0]["label"] = ["raw"]
            manifest.write_text(json.dumps(data), encoding="utf-8")
            self.assertTrue(any("label must be text" in issue for issue in M.verify(manifest)))


class ProofReportConsumer(unittest.TestCase):
    def test_fresh_valid_manifest_has_no_stale_reasons(self):
        tmp, root, manifest = pack()
        with tmp:
            self.assertEqual(PR.evidence_stale_reasons(root / "run.log", manifest), [])

    def test_empty_files_manifest_is_now_reported(self):
        tmp, root, manifest = pack(manifest_obj={"schema": 1, "files": []})
        with tmp:
            reasons = PR.evidence_stale_reasons(root / "run.log", manifest)
            self.assertTrue(any("files array is empty" in r for r in reasons), reasons)


if __name__ == "__main__":
    unittest.main()
