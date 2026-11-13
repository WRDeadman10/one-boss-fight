"""BK-211..215 (C, implementer; X-2060): stage/evidence matrix for PIE_EXIT, pie_exit.txt and file_exit in
verify_bk56_60_receipts.verify_failure, and regressions for the two A-854 missing-receipt asymmetries.

Both asymmetries already ended as FAILURE / NOT_PROVEN (never a false success); the fix adds strict evidence
diagnostics. Synthetic receipts in throwaway OS temp folders (the existing verifier suite's Bundle fixture); no real
log, lock, asset, Unreal, build or PIE. X-1991 remains open.
"""
import importlib.util
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("verifier_fixtures_bk211", HERE / "test_verify_bk56_60_receipts.py")
F = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(F)
V = F.V
MISSING_RECEIPT = "has no pie_exit.txt receipt"
PRE_PIE_EXIT = "must have an empty PIE_EXIT"
PRE_PIE_FILE = "must not have a pie_exit.txt"
EMPTY_WITH_FILE = "PIE_EXIT is empty"


def outcome(stage, pie_field, pie_file):
    error = "synthetic failure"
    log = F.REFUSAL_LOG if stage in V.PIE_OR_LATER else None
    with F.failure_bundle(stage=stage, error=error, pie_field=pie_field, pie_file=pie_file, log=log) as folder:
        return V.verify_bundle(folder)


class Bk211StageEvidenceMatrix(unittest.TestCase):
    """Rows: (stage class, PIE_EXIT field, pie_exit.txt) -> outcome and the diagnostic, per runner :161-162/:198."""

    MATRIX = [
        # pre-PIE stage: PIE never ran -> neither evidence may exist
        ("Development build", "", None, "FAILURE", None),
        ("Development build", "0", None, "INVALID", PRE_PIE_EXIT),         # BK-213
        ("Development build", "1", None, "INVALID", PRE_PIE_EXIT),
        ("Development build", "", "PIE_EXIT=0\n", "INVALID", PRE_PIE_FILE),
        ("lock acquisition", "", None, "FAILURE", None),
        # deferred PIE: either PIE had not exited (neither) or it had (both, equal)
        ("deferred PIE", "", None, "FAILURE", None),
        ("deferred PIE", "1", "PIE_EXIT=1\n", "FAILURE", None),
        ("deferred PIE", "1", None, "INVALID", MISSING_RECEIPT),           # BK-212
        ("deferred PIE", "0", None, "INVALID", MISSING_RECEIPT),
        ("deferred PIE", "", "PIE_EXIT=1\n", "INVALID", EMPTY_WITH_FILE),
        ("deferred PIE", "1", "PIE_EXIT=2\n", "INVALID", "disagrees"),
        # after PIE: same pairing rule
        ("Content asset delta verification", "0", "PIE_EXIT=0\n", "FAILURE", None),
        ("Content asset delta verification", "0", None, "INVALID", MISSING_RECEIPT),
    ]

    def test_matrix(self):
        for stage, field, file_text, expected, needle in self.MATRIX:
            with self.subTest(stage=stage, PIE_EXIT=field, file=file_text):
                result = outcome(stage, field, file_text)
                self.assertEqual(result["outcome"], expected, result["errors"])
                self.assertEqual(result["live_route"], "NOT_PROVEN")
                if needle:
                    self.assertTrue(any(needle in e for e in result["errors"]), result["errors"])
                else:
                    self.assertEqual(result["errors"], [])


class Bk212Bk213Reproductions(unittest.TestCase):
    def test_a854_deferred_pie_nonzero_exit_without_receipt(self):
        result = outcome("deferred PIE", "1", None)
        self.assertEqual((result["outcome"], result["live_route"]), ("INVALID", "NOT_PROVEN"))
        self.assertIn("failure_status.txt PIE_EXIT=1 has no pie_exit.txt receipt (the runner writes both together)",
                      result["errors"])

    def test_a854_development_build_with_pie_exit_marker(self):
        result = outcome("Development build", "0", None)
        self.assertEqual((result["outcome"], result["live_route"]), ("INVALID", "NOT_PROVEN"))
        self.assertIn("pre-PIE failure stage 'Development build' must have an empty PIE_EXIT (PIE never ran), got '0'",
                      result["errors"])

    def test_malformed_pie_exit_file_is_reported_once(self):
        result = outcome("deferred PIE", "1", "garbage\n")
        self.assertEqual(result["outcome"], "INVALID")
        self.assertFalse(any(MISSING_RECEIPT in e for e in result["errors"]), result["errors"])


class Bk214ExistingClassificationsStayFailClosed(unittest.TestCase):
    def test_existing_failure_and_invalid_paths(self):
        # the original well-formed failures are unchanged
        self.assertEqual(outcome("deferred PIE", "1", "PIE_EXIT=1\n")["outcome"], "FAILURE")
        self.assertEqual(outcome("Development build", "", None)["outcome"], "FAILURE")
        # no PIE_EXIT combination can ever yield SUCCESS or a proven live route from a failure receipt
        for stage in V.STAGES:
            for field, file_text in (("", None), ("0", None), ("1", None), ("0", "PIE_EXIT=0\n"), ("1", "PIE_EXIT=1\n")):
                with self.subTest(stage=stage, field=field, file=file_text):
                    result = outcome(stage, field, file_text)
                    self.assertIn(result["outcome"], ("FAILURE", "INVALID"))
                    self.assertEqual(result["live_route"], "NOT_PROVEN")

    def test_exit_codes_unchanged(self):
        self.assertEqual(V.EXIT_CODES, {"SUCCESS": 0, "FAILURE": 1, "INVALID": 2})


if __name__ == "__main__":
    unittest.main()
