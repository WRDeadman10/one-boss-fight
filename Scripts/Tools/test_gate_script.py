"""Offline contract checks for the one-command local gate."""
from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


class GateScriptTests(unittest.TestCase):
    def test_gate_runs_required_steps_in_sequence(self):
        script = (ROOT / "Scripts/Gate.ps1").read_text(encoding="utf-8")
        ordered = [
            "build_and_native_tests",
            "offline_tool_suite",
            "make_bench_kit_dependency_test",
            "shipping_debug_guard",
            "documentation_line_count_guard",
        ]
        offsets = [script.index("Name = '" + name + "'") for name in ordered]
        self.assertEqual(offsets, sorted(offsets))
        self.assertIn("Rebuild.ps1'),'-Tests','-NoRelaunch'", script)
        self.assertIn("CheckShippingBinary.py", script)

    def test_gate_refuses_open_editor_and_dry_run_writes_no_receipt(self):
        script = (ROOT / "Scripts/Gate.ps1").read_text(encoding="utf-8")
        editor_guard = script.index("if ($editors.Count -gt 0)")
        dry_run = script.index("if ($DryRun)")
        receipt_write = script.index("Set-Content -LiteralPath $ReceiptPath")
        self.assertLess(editor_guard, dry_run)
        self.assertLess(dry_run, receipt_write)
        self.assertIn("no gate commands ran and no receipt was written", script)

    def test_doc_line_count_guard_only_checks_tracked_markdown_against_head(self):
        script = (ROOT / "Scripts/Tools/CheckDocLineCounts.ps1").read_text(encoding="utf-8")
        self.assertIn("diff --name-only -- Documentation", script)
        self.assertIn("show \"HEAD:$repoPath\"", script)
        self.assertIn("$current.Count -lt $baseline.Count", script)


if __name__ == "__main__":
    unittest.main()
