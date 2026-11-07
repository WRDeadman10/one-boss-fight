from __future__ import annotations

import unittest
from pathlib import Path

import validate_queue_batches as validator


ROOT = Path(__file__).resolve().parents[2]


def make_ab_queue() -> str:
    parts = []
    for batch in range(1, 11):
        parts.append(f"## Batch {batch} — test")
        for offset in range(1, 6):
            number = (batch - 1) * 5 + offset
            parts.append(f"| AB-C{number:02d} | Task {number} | accepts |")
    return "\n".join(parts)


def make_aa_queue() -> str:
    rows = []
    for number in range(1, 51):
        task = "X- batch" if number % 5 == 0 and number < 45 else f"Task {number}"
        rows.append(f"| AA-C{number:02d} | {task} | accepts |")
    return "\n".join(rows)


class QueueBatchValidatorTests(unittest.TestCase):
    def test_current_aa_and_ab_queues_pass(self):
        for prefix, path in (("AA-C", ROOT / "Documentation/Boss/QUEUE_AA.md"),
                             ("AB-C", ROOT / "Documentation/Boss/QUEUE_AB.md")):
            with self.subTest(prefix=prefix):
                self.assertEqual(validator.validate_queue(path.read_text(encoding="utf-8"), prefix), [])

    def test_fixtures_accept_exact_ten_groups_of_five(self):
        self.assertEqual(validator.validate_queue(make_aa_queue(), "AA-C"), [])
        self.assertEqual(validator.validate_queue(make_ab_queue(), "AB-C"), [])

    def test_duplicate_missing_and_bad_grouping_are_rejected(self):
        duplicate = make_aa_queue().replace("| AA-C02 |", "| AA-C01 |", 1)
        self.assertTrue(any("duplicate IDs" in issue for issue in validator.validate_queue(duplicate, "AA-C")))

        missing = make_ab_queue().replace("| AB-C17 | Task 17 | accepts |\n", "", 1)
        self.assertTrue(any("missing IDs" in issue for issue in validator.validate_queue(missing, "AB-C")))

        regrouped = make_ab_queue().replace("## Batch 3 — test", "## Group 3 — test", 1)
        self.assertTrue(any("batch headings" in issue for issue in validator.validate_queue(regrouped, "AB-C")))
        self.assertTrue(any("counts=" in issue for issue in validator.validate_queue(regrouped, "AB-C")))


if __name__ == "__main__":
    unittest.main()
