from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from summarize_parity_set import DRIVERS, summarize


class SelectedParitySummaryTests(unittest.TestCase):
    def test_reports_all_five_and_fails_closed_on_missing(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            for driver in DRIVERS[:4]:
                folder = root / (driver + "_test")
                folder.mkdir()
                (folder / "parity_report.json").write_text(json.dumps({"status": "PASS", "exit_code": 0, "issues": []}), encoding="utf-8")
            result = summarize(root, "_test")
            self.assertEqual(result["passed"], 4)
            self.assertEqual(result["failed_or_missing"], 1)
            self.assertEqual(result["pairs"][-1]["status"], "MISSING")

    def test_rejects_nonpassing_comparator_report(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            for driver in DRIVERS:
                folder = root / (driver + "_test")
                folder.mkdir()
                status = "FAIL" if driver == DRIVERS[0] else "PASS"
                (folder / "parity_report.json").write_text(json.dumps({"status": status, "exit_code": int(status != "PASS"), "issues": []}), encoding="utf-8")
            self.assertEqual(summarize(root, "_test")["failed_or_missing"], 1)


if __name__ == "__main__":
    unittest.main()
