from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import discover_focused_player_tests as discovery


class FocusedPlayerDiscoveryTests(unittest.TestCase):
    def test_fixture_discovery_is_stable_and_reports_test_lines(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            for _, relative in discovery.CONTRACT_FILES:
                target = root / relative
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_text("class Contract:\n    def test_beta(self): pass\n    def test_alpha(self): pass\n", encoding="utf-8")

            first, issues = discovery.discover(root)
            second, second_issues = discovery.discover(root)

        self.assertEqual(issues, [])
        self.assertEqual(second_issues, [])
        self.assertEqual(first, second)
        self.assertEqual(len(first), 10)
        self.assertEqual(first[0]["test"], "Contract.test_alpha")
        self.assertEqual(first[0]["line"], 3)

    def test_missing_or_invalid_contract_is_reported(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            for _, relative in discovery.CONTRACT_FILES[1:]:
                target = root / relative
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_text("class Empty: pass\n", encoding="utf-8")
            bad = root / discovery.CONTRACT_FILES[0][1]
            bad.parent.mkdir(parents=True, exist_ok=True)
            bad.write_text("def broken(:\n", encoding="utf-8")

            rows, issues = discovery.discover(root)

        self.assertEqual(rows, [])
        self.assertTrue(any("cannot parse" in issue for issue in issues))
        self.assertTrue(any("no test methods" in issue for issue in issues))


if __name__ == "__main__":
    unittest.main()
