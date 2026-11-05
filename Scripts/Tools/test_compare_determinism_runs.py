import copy
import unittest

from compare_determinism_runs import compare


def receipt():
    arms = []
    for route in ("legacy", "data"):
        for repeat in (1, 2, 3):
            arms.append({
                "route": route, "repeat": repeat, "seed": 7, "status": "complete",
                "input_schedule": {"duration_seconds": 35},
                "inputs": [{"action": "attack", "scheduled_seconds": 3}],
                "events": [{"kind": "tracker_move", "move": "A1", "instance": 1}],
            })
    return {"schema": "u_c07_determinism_v1", "seed": 7, "status": "complete", "fatal": None,
            "input_schedule": {"duration_seconds": 35}, "runs": arms}


class DeterminismComparatorTests(unittest.TestCase):
    def test_matching_six_arm_receipts_pass(self):
        self.assertEqual([], compare(receipt(), receipt()))

    def test_event_difference_fails(self):
        changed = receipt()
        changed["runs"][0]["events"][0]["move"] = "A2"
        self.assertTrue(any("event trace differs" in e for e in compare(receipt(), changed)))

    def test_missing_and_duplicate_arm_fail(self):
        invalid = receipt()
        invalid["runs"].pop()
        invalid["runs"].append(copy.deepcopy(invalid["runs"][0]))
        errors = compare(receipt(), invalid)
        self.assertTrue(any("duplicate" in e for e in errors))
        self.assertTrue(any("missing" in e for e in errors))

    def test_seed_or_schedule_drift_fails(self):
        changed = receipt()
        changed["seed"] = 8
        self.assertTrue(any("seed mismatch" in e for e in compare(receipt(), changed)))
        changed = receipt()
        changed["input_schedule"]["duration_seconds"] = 36
        self.assertTrue(any("schedule mismatch" in e for e in compare(receipt(), changed)))

    def test_partial_receipt_fails_closed(self):
        changed = receipt()
        changed["status"] = "partial"
        self.assertTrue(any("not a clean complete run" in e for e in compare(receipt(), changed)))

    def test_non_object_run_fails_closed_without_exception(self):
        changed = receipt()
        changed["runs"][0] = "malformed arm"
        errors = compare(changed, receipt())
        self.assertTrue(any("each run must be an object" in error for error in errors))
        self.assertTrue(any("missing runs" in error for error in errors))

    def test_route_repeat_drift_fails_within_receipt(self):
        changed = receipt()
        changed["runs"][4]["events"][0]["move"] = "A2"
        self.assertTrue(any("differs from the first route/repeat trace" in e
                            for e in compare(changed, changed)))


if __name__ == "__main__":
    unittest.main()
