# Copyright One Boss Fight. All Rights Reserved.
"""
test_reopen_ki145_range_calibration.py
Offline re-open validation test for KI-145 Move Card Range Calibration and Reach Analysis.
Authority: Lead Order [C-461], REACH_TO_RANGE_RULES.md
"""

import hashlib
import json
import os
import sys
import unittest
from pathlib import Path

# Support isolated python -I invocation
sys.path.insert(0, str(Path(__file__).resolve().parent))

from compute_ki145_ranges import (
    run_ki145_evaluation,
    dist_point_to_segment_2d,
    R_TARGET,
    R_BOSS,
    PHYS_MIN_D,
    SAFETY_OUTER,
    SAFETY_INNER
)


class TestReopenKI145RangeCalibration(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.repo_root = Path(__file__).resolve().parents[5]
        cls.reviews_dir = Path(__file__).resolve().parent

    def test_crlf_line_endings(self):
        """Verifies that all authored KI-145 files use pure CRLF line endings without bare LFs."""
        target_files = [
            self.reviews_dir / "compute_ki145_ranges.py",
            self.reviews_dir / "KI145_RANGE_CALIBRATION.md",
            self.reviews_dir / "test_reopen_ki145_range_calibration.py"
        ]
        for tf in target_files:
            if not tf.exists():
                continue
            raw_bytes = tf.read_bytes()
            self.assertNotIn(b"\r\r\n", raw_bytes, f"Corrupted double CR in {tf.name}")
            # Replace CRLF with empty, then check if any bare \n or \r remain
            stripped = raw_bytes.replace(b"\r\n", b"")
            self.assertNotIn(b"\n", stripped, f"Bare LF detected in {tf.name}")
            self.assertNotIn(b"\r", stripped, f"Bare CR detected in {tf.name}")

    def test_input_files_exist(self):
        """Verifies that all input files referenced in C-461 are present and non-empty."""
        reach_path = self.repo_root / "Docs/BossCombatReview/Execution/Claude/F5/reach_run1/reach_summary.json"
        f5_path = self.repo_root / "Docs/BossCombatReview/Execution/Antigravity/MoveCards/move_cards_f5_set.json"
        f7_path = self.repo_root / "Docs/BossCombatReview/Execution/Claude/F7/move_cards_f7_baked.json"
        p2_path = self.repo_root / "Docs/BossCombatReview/Execution/Antigravity/MoveCards/move_cards_f7_phase2_set.json"
        rules_path = self.repo_root / "Docs/BossCombatReview/Execution/Antigravity/MoveCards/REACH_TO_RANGE_RULES.md"

        self.assertTrue(reach_path.exists(), "reach_summary.json missing")
        self.assertTrue(f5_path.exists(), "move_cards_f5_set.json missing")
        self.assertTrue(f7_path.exists(), "move_cards_f7_baked.json missing")
        self.assertTrue(p2_path.exists(), "move_cards_f7_phase2_set.json missing")
        self.assertTrue(rules_path.exists(), "REACH_TO_RANGE_RULES.md missing")

    def test_core_dimensions(self):
        """Verifies physical constants match specifications."""
        self.assertEqual(R_TARGET, 42.0, "Player target capsule radius must be 42 cm")
        self.assertEqual(R_BOSS, 60.0, "Boss capsule radius must be 60 cm")
        self.assertEqual(PHYS_MIN_D, 102.0, "Physical non-penetration floor must be 102.0 cm")

    def test_evaluation_completeness(self):
        """Verifies that run_ki145_evaluation processes exactly 10 cards across F5, F7, and Phase2."""
        results = run_ki145_evaluation(str(self.repo_root))
        self.assertEqual(len(results), 10, "Must evaluate exactly 10 cards")

        f5_count = sum(1 for r in results if r['Set'] == 'F5')
        f7_count = sum(1 for r in results if r['Set'] == 'F7')
        p2_count = sum(1 for r in results if r['Set'] == 'Phase2')

        self.assertEqual(f5_count, 4, "Must have 4 F5 cards")
        self.assertEqual(f7_count, 4, "Must have 4 F7 cards")
        self.assertEqual(p2_count, 2, "Must have 2 Phase 2 cards")

    def test_pie_prediction_matrix(self):
        """Verifies the exact (distance, hit/miss) predictions for Lead Claude's PIE confirmation."""
        results = run_ki145_evaluation(str(self.repo_root))
        card_map = {r['MoveId']: r for r in results}

        # 1. SwingSlow_F7: Hits at 100, 130, 160, 167 cm
        slow = card_map["Move_Sevarog_SwingSlow_F7"]
        self.assertTrue(slow['PieProbes'][100.0]['hit'], "SwingSlow must hit at 100cm")
        self.assertTrue(slow['PieProbes'][130.0]['hit'], "SwingSlow must hit at 130cm")
        self.assertTrue(slow['PieProbes'][160.0]['hit'], "SwingSlow must hit at 160cm")
        self.assertTrue(slow['PieProbes'][167.0]['hit'], "SwingSlow must hit at 167cm")

        # 2. SwingMedium_F7: Hits at 100, 130 cm; MISSES at 160, 167 cm
        med = card_map["Move_Sevarog_SwingMedium_F7"]
        self.assertTrue(med['PieProbes'][100.0]['hit'], "SwingMedium must hit at 100cm")
        self.assertTrue(med['PieProbes'][130.0]['hit'], "SwingMedium must hit at 130cm")
        self.assertFalse(med['PieProbes'][160.0]['hit'], "SwingMedium must MISS at 160cm")
        self.assertFalse(med['PieProbes'][167.0]['hit'], "SwingMedium must MISS at 167cm")

        # 3. HeavySlam_F7: Hits at 100 cm (grazes right side); MISSES at 130, 160, 167 cm
        slam = card_map["Move_Sevarog_HeavySlam_F7"]
        self.assertTrue(slam['PieProbes'][100.0]['hit'], "HeavySlam must hit at 100cm")
        self.assertFalse(slam['PieProbes'][130.0]['hit'], "HeavySlam must MISS at 130cm")
        self.assertFalse(slam['PieProbes'][160.0]['hit'], "HeavySlam must MISS at 160cm")
        self.assertFalse(slam['PieProbes'][167.0]['hit'], "HeavySlam must MISS at 167cm")

    def test_dead_zone_detection(self):
        """Verifies that upper dead zones are correctly flagged for HeavySlam and SwingMedium."""
        results = run_ki145_evaluation(str(self.repo_root))
        card_map = {r['MoveId']: r for r in results}

        # HeavySlam: Authored [90, 180], Geom max ~108.5 cm -> >70 cm dead zone
        slam = card_map["Move_Sevarog_HeavySlam_F7"]
        self.assertLess(slam['GeomMaxCm'], 109.0)
        self.assertTrue(any("Upper dead zone" in dz for dz in slam['DeadZones']))

        # SwingMedium: Authored [90, 180], Geom max ~149.0 cm -> >30 cm dead zone
        med = card_map["Move_Sevarog_SwingMedium_F7"]
        self.assertLess(med['GeomMaxCm'], 150.0)
        self.assertTrue(any("Upper dead zone" in dz for dz in med['DeadZones']))

        # All cards author MinRange < 102.0 cm -> all flag Sub-physical floor
        for r in results:
            self.assertTrue(any("Sub-physical floor" in dz for dz in r['DeadZones']))

    def test_review_document_contents(self):
        """Verifies that KI145_RANGE_CALIBRATION.md contains required sections and analysis."""
        doc_path = self.reviews_dir / "KI145_RANGE_CALIBRATION.md"
        self.assertTrue(doc_path.exists(), "Review document missing")
        text = doc_path.read_text(encoding="utf-8")

        required_tokens = [
            "KI-145",
            "[C-461]",
            "REACH_TO_RANGE_RULES.md",
            "Move_Sevarog_HeavySlam",
            "Move_Sevarog_SwingMedium",
            "Move_Sevarog_SwingSlow",
            "Move_Sevarog_AntiGreed",
            "102.0",
            "149.0",
            "108.5",
            "Unverified Items & Boundary Conditions"
        ]
        for token in required_tokens:
            self.assertIn(token, text, f"Token '{token}' missing from KI145_RANGE_CALIBRATION.md")


if __name__ == "__main__":
    unittest.main()
