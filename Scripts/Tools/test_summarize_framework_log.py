"""Synthetic parsing and aggregation contracts for FrameworkProof summaries."""
from pathlib import Path
import tempfile
import unittest

from Scripts.Tools.summarize_framework_log import summarize


class FrameworkLogSummaryTests(unittest.TestCase):
    def test_counts_tokens_outcomes_and_groups_instances_by_card(self):
        lines = [
            "[2026.01.01-00.00.00:001][1] [FrameworkProof] playback_start instance=3 card=Move_A",
            "[2026.01.01-00.00.01:001][2] [FrameworkProof] decision instance=3 chosen=Move_A",
            "[2026.01.01-00.00.02:001][3] [FrameworkProof] hit instance=3 window=Window_Move_A_Primary outcome=ERPGDamageOutcome::Parried",
            "[2026.01.01-00.00.03:001][4] [FrameworkProof] RESULT outcome=Completed acceptedHits=0",
        ]
        with tempfile.TemporaryDirectory() as temporary:
            log = Path(temporary) / "pie.log"
            log.write_text("\n".join(lines), encoding="utf-8")
            result = summarize(log)
        self.assertEqual(result["decisions"], 1)
        self.assertEqual(result["parried_outcomes"], 1)
        self.assertEqual(result["reported_accepted_hits"], 0)
        self.assertEqual(result["per_card"][0]["card"], "Move_A")
        self.assertEqual(result["per_card"][0]["parried"], 1)


if __name__ == "__main__":
    unittest.main(verbosity=2)
