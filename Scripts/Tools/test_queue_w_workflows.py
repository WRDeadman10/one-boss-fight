from __future__ import annotations

import unittest
import json
import re
import shutil
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


class QueueWWorkflowTests(unittest.TestCase):
    def test_full_review_gate_defaults_to_dry_run_and_names_five_reviewed_pairs(self):
        source = (ROOT / "Scripts/FullReviewGate.ps1").read_text(encoding="utf-8")
        for driver in ("pie_phase_reset", "pie_boss_death", "pie_authored_close_clips", "pie_legend", "pie_iframes"):
            self.assertIn(driver, source)
        self.assertIn("if (-not $Execute)", source)
        self.assertIn("Gate.ps1", source)
        self.assertIn("summarize_parity_set.py", source)

    def test_nightly_runner_checkpoints_after_each_pair_and_uses_fresh_attempt_paths(self):
        source = (ROOT / "Scripts/RunA5ParityNightly.ps1").read_text(encoding="utf-8")
        self.assertIn("resume.json", source)
        self.assertIn("Save-Checkpoint", source)
        self.assertIn("checkpoint PASS", source)
        self.assertIn("_attempt{1:D2}", source)
        self.assertIn("Refusing existing nightly evidence directory", source)

    @unittest.skipUnless(shutil.which("powershell.exe"), "Windows PowerShell is required for runner dry-run")
    def test_resume_dry_run_skips_checkpointed_pass(self):
        script = ROOT / "Scripts/RunA5ParityNightly.ps1"
        source = script.read_text(encoding="utf-8")
        body = re.search(r"(?s)\$drivers\s*=\s*@\((.*?)\)", source)
        self.assertIsNotNone(body)
        drivers = re.findall(r"'([^']+)'", body.group(1))
        with tempfile.TemporaryDirectory() as temp:
            output = Path(temp)
            state = {"schema": 1, "drivers": drivers,
                     "rows": [{"Driver": drivers[0], "Legacy": "14/14", "Data": "14/14",
                               "Result": "PASS", "Detail": "fixture", "PairOut": "fixture"}]}
            (output / "resume.json").write_text(json.dumps(state), encoding="utf-8")
            result = subprocess.run(
                ["powershell.exe", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", str(script),
                 "-OutRoot", str(output), "-Resume"],
                cwd=ROOT, capture_output=True, text=True, timeout=30, check=False,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("1 already PASS and 30 pending", result.stdout)
            self.assertIn("SKIP pie_a4_low_sweep (checkpoint PASS)", result.stdout)
            self.assertFalse((output / "summary.md").exists())


if __name__ == "__main__":
    unittest.main()
