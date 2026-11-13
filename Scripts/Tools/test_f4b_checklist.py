"""BQ-54 in-process tests for f4b_checklist (real repo tree read-only, plus temp fixtures). Nothing is run or written."""
from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import f4b_checklist as F  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]


class F4bChecklistTests(unittest.TestCase):
    def test_real_tree_mapping(self):
        rows = {r["id"]: r for r in F.evaluate(ROOT)}
        self.assertEqual(len(rows), 7)
        for rid in ("F4b-1", "F4b-2", "F4b-3", "F4b-4", "F4b-5", "F4b-6"):
            self.assertEqual(rows[rid]["status"], "static-ok", rows[rid]["gaps"])
        # Greystone visuals has no native test by design: always reported as a gap
        self.assertEqual(rows["F4b-7"]["status"], "gap")
        self.assertIn("no native test mapped", rows["F4b-7"]["gaps"])

    def test_summary_never_claims_live(self):
        s = F.summary(F.evaluate(ROOT))
        self.assertEqual(s["live_verified"], 0)
        self.assertEqual(s["items"], 7)

    def test_missing_test_and_driver_are_gaps(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            tests = root / "Source" / "OneBossFight" / "Tests"
            tests.mkdir(parents=True)
            (tests / "A.cpp").write_text('IMPLEMENT_SIMPLE_AUTOMATION_TEST(F, "OneBossFight.X.Present", 0)', encoding="utf-8")
            (root / "drv.py").write_text("", encoding="utf-8")
            items = ({"id": "T1", "item": "ok", "native": ["OneBossFight.X.Present"], "drivers": ["drv.py"], "gate": "g"},
                     {"id": "T2", "item": "renamed", "native": ["OneBossFight.X.Gone"], "drivers": ["drv.py"], "gate": "g"},
                     {"id": "T3", "item": "no driver", "native": ["OneBossFight.X.Present"], "drivers": ["missing.py"], "gate": "g"})
            rows = {r["id"]: r for r in F.evaluate(root, items)}
            self.assertEqual(rows["T1"]["status"], "static-ok")
            self.assertTrue(any("not registered" in g for g in rows["T2"]["gaps"]))
            self.assertTrue(any("driver file missing" in g for g in rows["T3"]["gaps"]))

    def test_no_tests_dir_means_every_native_name_missing(self):
        with tempfile.TemporaryDirectory() as tmp:
            rows = F.evaluate(Path(tmp))
            self.assertTrue(all(r["status"] == "gap" for r in rows))


if __name__ == "__main__":
    unittest.main()
