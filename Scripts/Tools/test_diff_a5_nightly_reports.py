from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from diff_a5_nightly_reports import compare, parse_report


def report(rows=None):
    rows = rows or {}
    lines = ["# A5 parity nightly summary", "", "| Driver | Legacy checks | Data checks | Result | Detail |",
             "|---|---:|---:|---|---|"]
    for index in range(31):
        name = f"pie_driver_{index:02d}"
        value = rows.get(name, {"legacy": "10/10", "data": "10/10", "result": "PASS", "detail": "both fresh-process arms met minimum"})
        lines.append(f"| {name} | {value['legacy']} | {value['data']} | {value['result']} | {value['detail']} |")
    return "\n".join(lines) + "\n"


class NightlyReportDiffTests(unittest.TestCase):
    def test_matching_complete_reports_have_no_changes(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "summary.md"
            path.write_text(report(), encoding="utf-8")
            self.assertEqual([], compare(parse_report(path), parse_report(path)))

    def test_new_fail_and_check_count_change_are_reported(self):
        before, after = {}, {"pie_driver_03": {"legacy": "10/10", "data": "8/10", "result": "FAIL", "detail": "data checks failed"}}
        changes = compare(parse_text(report(before)), parse_text(report(after)))
        self.assertTrue(any(change.startswith("NEW_FAIL pie_driver_03") for change in changes))
        self.assertTrue(any(change.startswith("CHECK_COUNT_CHANGED pie_driver_03") for change in changes))

    def test_partial_report_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "summary.md"
            path.write_text("\n".join(report().splitlines()[:-1]), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "expected 31"):
                parse_report(path)


def parse_text(text):
    with tempfile.TemporaryDirectory() as directory:
        path = Path(directory) / "summary.md"
        path.write_text(text, encoding="utf-8")
        return parse_report(path)


if __name__ == "__main__":
    unittest.main()
