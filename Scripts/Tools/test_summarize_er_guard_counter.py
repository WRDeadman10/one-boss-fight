"""Offline checks for exact-result and missing-field behavior."""

import unittest

try:
    from Scripts.Tools.summarize_er_guard_counter import summarize
except ModuleNotFoundError:
    from summarize_er_guard_counter import summarize


class CounterSummaryTests(unittest.TestCase):
    def test_missing_fields_stay_missing(self):
        summary = summarize("[ERGuardCounter] RESULT synthetic_arm_used=True boss_hp_delta=0.0")
        self.assertEqual(summary["fields"]["boss_hp_delta"], "0.0")
        self.assertIn("hit_count_after", summary["missing"])
        self.assertEqual(summary["hit_log_count"], 0)

    def test_duplicate_result_is_error(self):
        summary = summarize("[ERGuardCounter] RESULT boss_hp_delta=0\n[ERGuardCounter] RESULT boss_hp_delta=1")
        self.assertEqual(summary["result_count"], 2)
        self.assertIn("error", summary)


if __name__ == "__main__":
    unittest.main()
