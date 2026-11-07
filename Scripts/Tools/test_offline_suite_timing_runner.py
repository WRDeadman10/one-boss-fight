"""Contract checks for the offline suite's time-budget wrapper."""
from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


class OfflineSuiteTimingRunnerTests(unittest.TestCase):
    def test_runner_uses_discovery_and_twenty_second_default(self):
        source = (ROOT / "Scripts/Tools/run_offline_suite_timed.py").read_text(encoding="utf-8")
        self.assertIn("DEFAULT_MAX_SECONDS = 20.0", source)
        self.assertIn('"discover", "-s", "Scripts/Tools"', source)
        self.assertIn("time.monotonic()", source)
        self.assertIn("elapsed >= args.max_seconds", source)


if __name__ == "__main__":
    unittest.main()
