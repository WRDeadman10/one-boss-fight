"""Offline contract test for C-1174 Player Fit Test Rubric & Capture Plan (C1174_PLAYER_FIT_TEST_VISUAL_RUBRIC_AND_CAPTURE_PLAN.md).

Validates that:
1. All 6 ER evaluation clips exist on disk under Content/OneBossFight/Player/Animations/.
2. The 3 candidate characters (Greystone, Steel, Grux) are named.
3. The 5 visual scoring criteria (0-2 scale, max 10/clip, 60 total) are defined.
4. Capture parameters (Side + 3/4, Slomo 0.5, off-repo D:/FightVideo/fit_test/) are specified.
5. Blind evaluation protocol is documented.
"""

import os
import re
import unittest

PROJECT_ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", ".."))
SPEC_PATH = os.path.join(PROJECT_ROOT, "Documentation", "Boss", "C1174_PLAYER_FIT_TEST_VISUAL_RUBRIC_AND_CAPTURE_PLAN.md")
ANIM_ROOT = os.path.join(PROJECT_ROOT, "Content", "OneBossFight", "Player", "Animations")


class TestPlayerFitTestRubricContract(unittest.TestCase):
    def setUp(self):
        self.assertTrue(os.path.exists(SPEC_PATH), f"Rubric plan missing: {SPEC_PATH}")
        with open(SPEC_PATH, "r", encoding="utf-8") as f:
            self.content = f.read()

    def test_candidates_named(self):
        """Must cover Greystone, Steel, and Grux."""
        self.assertIn("Greystone", self.content)
        self.assertIn("Steel", self.content)
        self.assertIn("Grux", self.content)

    def test_all_six_clips_exist_on_disk(self):
        """All 6 ER evaluation clips must exist in Content/OneBossFight/Player/Animations/."""
        clips = [
            "AM_ER_Attack_Air_Light",
            "AM_ER_Attack_Air_Heavy_Plunge",
            "AM_ER_Attack_GuardCounter",
            "AM_ER_Backstep_Back",
            "AM_ER_Backstep_Mixamo",
            "AM_ER_Backstep_Mixamo_V2",
        ]
        for c in clips:
            self.assertIn(c, self.content, f"Clip {c} missing from spec text")
            uasset_path = os.path.join(ANIM_ROOT, f"{c}.uasset")
            self.assertTrue(os.path.exists(uasset_path), f"Asset missing on disk: {uasset_path}")

    def test_five_scoring_criteria_defined(self):
        """Must document the 5 visual criteria specified in C-1215."""
        self.assertIn("Weapon in Hand", self.content)
        self.assertIn("No Foot Sliding", self.content)
        self.assertIn("No Armor / Weapon Clipping", self.content)
        self.assertIn("ER Silhouette & Stance", self.content)
        self.assertIn("Root-Motion Fidelity", self.content)
        self.assertIn("60", self.content)  # Max score across 6 clips

    def test_capture_plan_parameters(self):
        """Must specify side + 3/4 views, slomo 0.5, and D:/FightVideo/fit_test/."""
        self.assertIn("Side Profile", self.content)
        self.assertIn("Three-Quarter", self.content)
        self.assertIn("0.5", self.content)
        self.assertIn("D:/FightVideo/fit_test/", self.content)

    def test_blind_evaluation_protocol(self):
        """Must document blind anonymized evaluation and Candidate_0 control baseline."""
        self.assertIn("Blind Evaluation Protocol", self.content)
        self.assertIn("Candidate_A", self.content)
        self.assertIn("Candidate_0", self.content)


if __name__ == "__main__":
    unittest.main()
