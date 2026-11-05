"""Fixtures for manifest verification, expected-sheet linting, and tool index audit."""
import hashlib
import json
import os
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path
from unittest.mock import patch

from audit_tool_index import indexed_commands, indexed_tools
from lint_expected_sheets import lint, main as lint_main
from proof_report import evidence_stale_reasons
from verify_evidence_manifest import verify


class QueueCS36S40Tests(unittest.TestCase):
    def test_manifest_valid_altered_missing_and_escaping_paths(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            payload = root / "raw.log"
            payload.write_text("original", encoding="utf-8")
            digest = hashlib.sha256(payload.read_bytes()).hexdigest()
            manifest = root / "evidence_manifest.json"
            manifest.write_text(json.dumps({"schema": 1, "files": [{"file": "raw.log", "bytes": 8, "sha256": digest}]}), encoding="utf-8")
            self.assertEqual(verify(manifest), [])
            payload.write_text("changed", encoding="utf-8")
            self.assertTrue(any("hash mismatch 'raw.log'" in item for item in verify(manifest)))
            payload.unlink()
            self.assertTrue(any("missing file 'raw.log'" in item for item in verify(manifest)))
            manifest.write_text(json.dumps({"schema": 1, "files": [{"file": "../outside.log", "sha256": digest}]}), encoding="utf-8")
            self.assertTrue(any("unsafe path" in item for item in verify(manifest)))

    def test_expected_sheet_lint_preserves_manual_items_and_finds_typos(self):
        schema = {"hit", "RESULT"}
        valid = """## Setup
## Control
## PASS
- Manual compare health values with the authored target.
- `[FrameworkProof] hit` appears after the control.
## FAIL
- Any missing outcome is a failure.
"""
        self.assertEqual(lint_text(valid, schema), [])
        typo = valid.replace("[FrameworkProof] hit", "[FrameworkProof] hti")
        self.assertTrue(any("unregistered FrameworkProof token 'hti'" in item for item in lint_text(typo, schema)))
        no_control = valid.replace("## Control\n", "")
        self.assertTrue(any("missing required section: control" in item for item in lint_text(no_control, schema)))

    def test_expected_sheet_lint_reports_each_missing_required_section(self):
        valid = "## Setup\n## Control\n## PASS\n- Manual check\n## FAIL\n"
        for heading in ("Setup", "Control", "PASS", "FAIL"):
            with self.subTest(missing=heading):
                reduced = valid.replace("## " + heading + "\n", "")
                self.assertEqual(lint_text(reduced, set()), ["missing required section: " + heading.casefold()])

    def test_expected_sheet_cli_invalid_token_reports_exact_line_and_nonzero(self):
        with tempfile.TemporaryDirectory() as tmp:
            sheet = Path(tmp) / "BAD_EXPECTED.md"
            sheet.write_text("## Setup\n## Control\n## PASS\n- `[FrameworkProof] typo_token`\n## FAIL\n", encoding="utf-8")
            output = StringIO()
            with patch.object(sys, "argv", ["lint_expected_sheets.py", str(sheet)]), \
                 patch("lint_expected_sheets.load_schemas", return_value={"valid_token"}), \
                 redirect_stdout(output):
                result = lint_main()
        self.assertEqual(result, 1)
        self.assertIn("FAIL %s: line 4: unregistered FrameworkProof token 'typo_token'" % sheet, output.getvalue())

    def test_expected_sheet_cli_accepts_valid_manual_only_sheet(self):
        with tempfile.TemporaryDirectory() as tmp:
            sheet = Path(tmp) / "MANUAL_EXPECTED.md"
            sheet.write_text("## Setup\n## Control\n## PASS\n- Manual visual check\n## FAIL\n", encoding="utf-8")
            output = StringIO()
            with patch.object(sys, "argv", ["lint_expected_sheets.py", str(sheet)]), \
                 patch("lint_expected_sheets.load_schemas", return_value=set()), \
                 redirect_stdout(output):
                result = lint_main()
        self.assertEqual(result, 0)
        self.assertIn("PASS %s:" % sheet, output.getvalue())

    def test_tool_index_extracts_real_tool_paths(self):
        sample = "- `py Scripts/Tools/x.py --flag`\n- `python3 Scripts/Tools/y.py`"
        self.assertEqual(indexed_tools(sample),
                         ["Scripts/Tools/x.py", "Scripts/Tools/y.py"])
        self.assertEqual(indexed_commands(sample)["Scripts/Tools/x.py"], {"--flag"})

    def test_proof_freshness_is_separate_from_gameplay_failures(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            log = root / "editor_raw.log"
            manifest = root / "evidence_manifest.json"
            log.write_text("same bytes", encoding="utf-8")
            digest = hashlib.sha256(log.read_bytes()).hexdigest()
            manifest.write_text(json.dumps({"schema": 1, "files": [{"file": log.name, "bytes": log.stat().st_size, "sha256": digest}]}), encoding="utf-8")
            self.assertEqual(evidence_stale_reasons(log, manifest), [])
            os.utime(log, (manifest.stat().st_mtime + 3, manifest.stat().st_mtime + 3))
            self.assertTrue(any("mtime is newer" in item for item in evidence_stale_reasons(log, manifest)))


def lint_text(text, schema):
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "EXPECTED.md"
        path.write_text(text, encoding="utf-8")
        return lint(path, schema)


if __name__ == "__main__":
    unittest.main()
