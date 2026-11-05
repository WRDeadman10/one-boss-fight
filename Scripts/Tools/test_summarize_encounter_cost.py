from __future__ import annotations

import copy
import unittest

import summarize_encounter_cost as cost


def sample(sample_id: str, phase: str, elapsed: float) -> dict[str, object]:
    return {
        "sample_id": sample_id, "run_id": "run-" + sample_id, "phase": phase,
        "build_id": "BUILD-1", "binary_sha256": "a" * 64, "content_sha256": "b" * 64,
        "elapsed_ms": elapsed, "source_log": sample_id + ".log", "source_log_sha256": "c" * 64,
    }


class EncounterCostTests(unittest.TestCase):
    def setUp(self) -> None:
        self.receipt = {
            "schema": cost.SCHEMA,
            "samples": [sample("c1", "cold", 10), sample("c2", "cold", 20),
                        sample("w1", "warm", 2), sample("w2", "warm", 4)],
        }

    def test_nearest_rank_percentiles_and_identities_are_preserved(self) -> None:
        report = cost.summarize(self.receipt, "lead.json")
        self.assertEqual(report["status"], "PASS")
        self.assertEqual(report["metrics_ms"]["cold"], {"sample_count": 2, "p50": 10.0, "p95": 20.0, "p99": 20.0})
        self.assertEqual(report["metrics_ms"]["warm"]["p50"], 2.0)
        self.assertEqual(report["samples"][0]["binary_sha256"], "a" * 64)
        self.assertEqual(report["source_receipt"], "lead.json")

    def test_missing_samples_and_invalid_digest_are_inconclusive(self) -> None:
        missing = copy.deepcopy(self.receipt)
        missing["samples"] = [sample("c1", "cold", 10)]
        self.assertEqual(cost.summarize(missing)["status"], "INCONCLUSIVE")
        malformed = copy.deepcopy(self.receipt)
        malformed["samples"][0]["source_log_sha256"] = "bad"  # type: ignore[index]
        report = cost.summarize(malformed)
        self.assertEqual(report["status"], "INCONCLUSIVE")
        self.assertTrue(any("hashes must be lowercase SHA-256" in issue for issue in report["issues"]))

    def test_mixed_builds_are_inconclusive(self) -> None:
        mixed = copy.deepcopy(self.receipt)
        mixed["samples"][2]["build_id"] = "BUILD-2"  # type: ignore[index]
        self.assertTrue(any("mix build IDs" in issue for issue in cost.summarize(mixed)["issues"]))


if __name__ == "__main__":
    unittest.main()
