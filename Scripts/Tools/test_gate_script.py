"""Offline contract checks for the one-command local gate."""
from __future__ import annotations

import unittest
import json
import shutil
import subprocess
import tempfile
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
        self.assertIn("Scripts/Tools/run_offline_suite_timed.py", script)

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

    @unittest.skipUnless(shutil.which("powershell.exe") or shutil.which("powershell"),
                         "Windows PowerShell is required for Gate.ps1 path-space fixture")
    def test_gate_passes_each_script_argument_when_root_contains_spaces(self):
        powershell = shutil.which("powershell.exe") or shutil.which("powershell")
        with tempfile.TemporaryDirectory(prefix="One Boss Fight Gate ") as temporary:
            root = Path(temporary)
            scripts = root / "Scripts"
            tools = scripts / "Tools"
            tools.mkdir(parents=True)
            (root / "OneBossFight.uproject").write_text("{}", encoding="utf-8")
            (scripts / "Gate.ps1").write_text((ROOT / "Scripts/Gate.ps1").read_text(encoding="utf-8"), encoding="utf-8")
            (scripts / "Rebuild.ps1").write_text("Write-Output 'rebuild-stub'\n", encoding="utf-8")
            (tools / "run_offline_suite_timed.py").write_text("print('offline-stub')\n", encoding="utf-8")
            (tools / "CheckDocLineCounts.ps1").write_text("Write-Output 'docs-stub'\n", encoding="utf-8")
            (scripts / "CheckShippingBinary.py").write_text(
                "import sys\nprint('shipping-arg=' + sys.argv[1])\n", encoding="utf-8")
            staged_binary = root / "Saved" / "StagedBuilds_Shipping" / "Windows" / "OneBossFight" / "Binaries" / "Win64" / "OneBossFight-Win64-Shipping.exe"

            result = subprocess.run(
                [powershell, "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", str(scripts / "Gate.ps1")],
                cwd=root, capture_output=True, text=True, timeout=45, check=False,
            )

            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn("offline-stub", result.stdout)
            self.assertIn("shipping-arg=", result.stdout)
            self.assertIn("One Boss Fight Gate", result.stdout)
            self.assertIn("OneBossFight-Win64-Shipping.exe", result.stdout)
            self.assertIn("docs-stub", result.stdout)
            receipt_paths = list((root / "Saved/LocalGate").glob("gate_*.json"))
            self.assertEqual(len(receipt_paths), 1)
            receipt = json.loads(receipt_paths[0].read_text(encoding="utf-8-sig"))
            self.assertTrue(receipt["passed"])
            self.assertEqual(len(receipt["steps"]), 5)


if __name__ == "__main__":
    unittest.main()
