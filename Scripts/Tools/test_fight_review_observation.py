"""Offline fail-closed contracts for full-fight visual review annotations."""
import unittest

from Scripts.Tools.fight_review_observation import validate_observation, validate_review


RUN = "BUILD-TEST-RUN"
FRAMES = {RUN + ":frame:00001", RUN + ":frame:00002"}


class FightReviewObservationTests(unittest.TestCase):
    def row(self, state, **values):
        return {"run": RUN, "state": state, "frame_ids": [RUN + ":frame:00001"], **values}

    def test_seen_requires_reviewed_image_evidence(self):
        valid = self.row("seen", evidence="decoded_frame_review", visual_observed=True,
                         component_active=True)
        self.assertEqual(validate_observation(valid, RUN, FRAMES)["state"], "seen")
        with self.assertRaisesRegex(ValueError, "component activation"):
            validate_observation(self.row("seen", evidence="decoded_frame_review", component_active=True,
                                          visual_observed=False), RUN, FRAMES)
        with self.assertRaisesRegex(ValueError, "decoded frame review"):
            validate_observation(self.row("seen", evidence="component_readback", visual_observed=True), RUN, FRAMES)

    def test_not_seen_obscured_and_inconclusive_remain_distinct(self):
        self.assertEqual(validate_observation(self.row("not_seen", evidence="decoded_frame_review"),
                                              RUN, FRAMES)["state"], "not_seen")
        self.assertEqual(validate_observation(self.row("obscured", reason="camera inside mantle"),
                                              RUN, FRAMES)["state"], "obscured")
        self.assertEqual(validate_observation(self.row("inconclusive", reason="frame too dark"),
                                              RUN, FRAMES)["state"], "inconclusive")

    def test_missing_reason_frame_or_run_fails_closed(self):
        with self.assertRaisesRegex(ValueError, "requires a reason"):
            validate_observation(self.row("obscured"), RUN, FRAMES)
        with self.assertRaisesRegex(ValueError, "frame id"):
            validate_observation({"run": RUN, "state": "not_seen", "frame_ids": []}, RUN, FRAMES)
        with self.assertRaisesRegex(ValueError, "foreign frame"):
            validate_observation(self.row("not_seen", frame_ids=["other:frame:00001"]), RUN, FRAMES)
        with self.assertRaisesRegex(ValueError, "run mismatch"):
            validate_observation(self.row("not_seen"), "other", FRAMES)

    def test_review_batch_must_contain_rows(self):
        with self.assertRaisesRegex(ValueError, "non-empty list"):
            validate_review([], RUN, FRAMES)


if __name__ == "__main__":
    unittest.main(verbosity=2)
