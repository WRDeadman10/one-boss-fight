#!/usr/bin/env python3
"""Integration checks for F-AG expected sheets and the maintained sheet linter."""
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT / "Scripts/Tools"))
from lint_expected_sheets import lint, load_schemas


class FAgExpectedSheetLintTests(unittest.TestCase):
    def test_all_current_f_ag_expected_sheets_pass(self):
        codex = ROOT / "Docs/BossCombatReview/Execution/Codex"
        sheets = (
            codex / "F_AG2_AG3_COM004_EXPECTED.md",
            codex / "F_AG4_HIT008_BLOCK_EXPECTED.md",
            codex / "F_AG5_MOV001_EXPECTED.md",
        )
        schemas = load_schemas(ROOT)
        for sheet in sheets:
            with self.subTest(sheet=sheet.name):
                self.assertTrue(sheet.is_file())
                self.assertEqual(lint(sheet, schemas), [])

    def test_fixture_reports_both_unknown_token_and_missing_sections(self):
        schemas = load_schemas(ROOT)
        with tempfile.TemporaryDirectory() as temp:
            sheet = Path(temp) / "invalid_EXPECTED.md"
            sheet.write_text("## Setup\n[FrameworkProof] invented_token x=1\n", encoding="utf-8")
            issues = lint(sheet, schemas)
        self.assertIn("line 2: unregistered FrameworkProof token 'invented_token'", issues)
        self.assertEqual(set(issues) - {"line 2: unregistered FrameworkProof token 'invented_token'"}, {
            "missing required section: control", "missing required section: fail", "missing required section: pass"
        })


if __name__ == "__main__":
    unittest.main()
