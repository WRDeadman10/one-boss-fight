"""X-2037 hotfix regressions (C, implementer) for runner_status_receipt_proposal_v1_1.py: malformed caller
`required_measured` must make the result invalid instead of raising. Synthetic only; no I/O beyond test discovery.
"""
import importlib.util
import math
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("v1_1_fixtures_hotfix", HERE / "test_runner_status_receipt_proposal_v1_1.py")
F = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(F)
V = F.V


class RequiredMeasuredFailsClosed(unittest.TestCase):
    def test_malformed_requirements_are_invalid_not_exceptions(self):
        bad = (None, 0, 1, 1.5, math.nan, True, "BUILD_EXIT", b"BUILD_EXIT", {"BUILD_EXIT": 1}, [None], ["BUILD_EXIT", 3],
               [3, "x"], ["build_exit"], ["BUILD EXIT"], [["BUILD_EXIT"]], (1, "A"), {("A",)}, [""])
        for value in bad:
            for outcome in ("PASS", "FAIL"):
                with self.subTest(value=value, outcome=outcome):
                    try:
                        verdict = V.validate_receipt(F.receipt(outcome), value)
                    except Exception as exc:  # noqa: BLE001 - "never raises" is the property under test
                        self.fail("required_measured=%r raised %s" % (value, type(exc).__name__))
                    self.assertFalse(verdict["valid"])
                    self.assertEqual(verdict["errors"], ["required_measured must be a list/tuple/set of UPPER_SNAKE keys"])

    def test_well_formed_requirement_collections_still_work(self):
        for value in ((), [], set(), frozenset(), ["SUITE_PASSED"], ("BUILD_EXIT", "SUITE_PASSED"), {"SUITE_PASSED"},
                      frozenset({"BUILD_EXIT"}), ["SUITE_PASSED", "SUITE_PASSED"]):
            with self.subTest(value=value):
                self.assertTrue(V.validate_receipt(F.receipt(), value)["valid"])
        verdict = V.validate_receipt(F.receipt(), {"NO_ASSETS", "ZZ_MISSING"})
        self.assertIn("PASS requires measured fields: NO_ASSETS, ZZ_MISSING", verdict["errors"])

    def test_docstring_names_the_v1_1_schema(self):
        self.assertIn("Schema `onebossfight.runner-status-receipt/v1.1`", V.__doc__)
        self.assertNotIn("Schema `onebossfight.runner-status-receipt/v1` ", V.__doc__)


if __name__ == "__main__":
    unittest.main()
