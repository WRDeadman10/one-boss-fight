from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from audit_source_test_coverage import inventory, render


class SourceTestCoverageAuditTests(unittest.TestCase):
    def test_reports_primary_type_without_direct_native_test_reference(self):
        with tempfile.TemporaryDirectory(dir=Path(__file__).resolve().parents[2]) as temp:
            root = Path(temp) / "Source" / "OneBossFight"
            (root / "Player").mkdir(parents=True)
            tests = root / "Tests"
            tests.mkdir(parents=True)
            (root / "Player" / "RPGExample.h").write_text(
                "class ONEBOSSFIGHT_API URPGExample {};", encoding="utf-8")
            (root / "Player" / "RPGExample.cpp").write_text(
                '#include "Player/RPGExample.h"\n', encoding="utf-8")
            tests = root / "Tests"
            (tests / "RPGExampleTests.cpp").write_text("// no type mention", encoding="utf-8")
            rows = inventory(root, tests)
            self.assertEqual(len(rows), 1)
            self.assertEqual(rows[0].types, ("URPGExample",))
            self.assertFalse(rows[0].matching_tests)
            self.assertIn("`URPGExample`", render(rows))

    def test_finds_exact_type_token_in_native_test(self):
        with tempfile.TemporaryDirectory(dir=Path(__file__).resolve().parents[2]) as temp:
            root = Path(temp) / "Source" / "OneBossFight"
            tests = root / "Tests"
            tests.mkdir(parents=True)
            (root / "RPGExample.h").write_text("class URPGExample {};", encoding="utf-8")
            (root / "RPGExample.cpp").write_text('#include "RPGExample.h"\n', encoding="utf-8")
            (tests / "RPGExampleTests.cpp").write_text("URPGExample* Subject;", encoding="utf-8")
            rows = inventory(root, tests)
            self.assertEqual(rows[0].matching_tests, ("RPGExampleTests.cpp",))


if __name__ == "__main__":
    unittest.main()
