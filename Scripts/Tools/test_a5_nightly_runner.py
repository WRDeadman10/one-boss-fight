from __future__ import annotations

import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "Scripts/RunA5ParityNightly.ps1"


class A5NightlyRunnerTests(unittest.TestCase):
    def test_nightly_schedule_has_31_unique_pair_drivers_and_defaults_to_dry_run(self):
        source = SCRIPT.read_text(encoding="utf-8")
        block = source.split("$drivers = @(", 1)[1].split(")", 1)[0]
        drivers = re.findall(r"'([^']+)'", block)
        self.assertEqual(31, len(drivers))
        self.assertEqual(31, len(set(drivers)))
        self.assertIn("if (-not $Execute)", source)
        self.assertIn("summary.md", source)

    def test_nightly_prevents_overwriting_existing_capture_directory(self):
        source = SCRIPT.read_text(encoding="utf-8")
        self.assertIn("if (Test-Path -LiteralPath $OutRoot)", source)
        self.assertIn("Refusing existing nightly evidence directory", source)


if __name__ == "__main__":
    unittest.main()
