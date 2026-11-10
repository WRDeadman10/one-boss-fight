"""Timestamp-insensitive RESULT and hit-outcome comparison contracts."""
from pathlib import Path
import tempfile
import unittest

from Scripts.Tools.compare_parry_runs import read_run


class ParryRunComparisonTests(unittest.TestCase):
    def write_log(self, root: Path, name: str, timestamp: str, result: str) -> Path:
        path = root / name
        path.write_text(
            f"[{timestamp}][7] [FrameworkProof] hit instance=1 outcome=ERPGDamageOutcome::Parried\n"
            f"[{timestamp}][8] [FrameworkProof] RESULT outcome={result} acceptedHits=2 attacks=3\n",
            encoding="utf-8")
        return path

    def test_timestamps_are_ignored_but_result_and_outcomes_are_compared(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            baseline = read_run(self.write_log(root, "a.log", "2026.01.01-00.00.00:001", "Completed"))
            candidate = read_run(self.write_log(root, "b.log", "2026.02.02-01.02.03:456", "Completed"))
            changed = read_run(self.write_log(root, "c.log", "2026.02.02-01.02.03:456", "Aborted"))
        self.assertEqual(baseline["results"], candidate["results"])
        self.assertEqual(baseline["hits"], candidate["hits"])
        self.assertEqual(baseline["outcomes"], candidate["outcomes"])
        self.assertNotEqual(baseline["results"], changed["results"])
        self.assertEqual(candidate["outcomes"].get("Parried"), 1)


if __name__ == "__main__":
    unittest.main(verbosity=2)
