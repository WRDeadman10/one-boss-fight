"""test_ingest_measurements.py - Tests validation and card proposal derivation for combat ledgers.

Verifies:
- 2 good entries validate cleanly and produce exact hand-calculated card proposals.
- Clean output rule: strictly NO reference names (REF_*, Morgott, Elden) in emitted proposals.
- Design status banner: 'DESIGN INPUT (measured from owner footage, observation only)'.
- RecoveryFrames definition: RE - E (active finish to actionable complete).
- RecoveryTailFrames definition: RE - R (blend-out / recovery marker to actionable).
- 10 bad entries (one distinct defect each) are properly refused with ValueError:
  1. Null field (W_frame is None).
  2. Non-integer frame (A_frame is float 465.5).
  3. Invalid frame order (C > A).
  4. Timestamp formula mismatch (t_combat != t_orig - 105.0).
  5. Elapsed seconds vs frame count mismatch (> 1 ms drift).
  6. Malformed evidence PNG name (fails pattern).
  7. Invalid move ID format (fails ^Move_[A-Za-z0-9]+_[A-Za-z0-9_]+$).
  8. Move ID contains forbidden reference name (Morgott/REF/Elden).
  9. Move ID collides with existing Cards/.uasset without id_status == 'existing'.
  10. Invalid or missing confidence level (must be 'high', 'medium', or 'low').

Run: python -I test_ingest_measurements.py
"""

import copy
import json
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(__file__))

from ingest_measurements import (
    FPS,
    COMBAT_ZERO,
    DEFAULT_CARDS_DIR,
    validate_entry,
    derive_card_proposal,
    ingest_ledger
)

# Hand-calculated Good Entry 1 (Curved Sword H1 -> Move_EmberWarden_CurvedSlash_H1)
GOOD_ENTRY_1 = {
    "priority": 1,
    "ref_id": "REF_CurvedSwordCombo_Chain1",
    "ref_to_original": "Move_EmberWarden_CurvedSlash_H1",
    "id_status": "proposed_new",
    "attack_family": "Curved sword 1-2-3 chain",
    "t_W_orig": 112.438,
    "t_W_combat": 7.438,
    "t_C_orig": 112.588,
    "t_C_combat": 7.588,
    "t_A_orig": 112.738,
    "t_A_combat": 7.738,
    "t_E_orig": 112.855,
    "t_E_combat": 7.855,
    "t_R_orig": 112.972,
    "t_R_combat": 7.972,
    "t_RE_orig": 113.322,
    "t_RE_combat": 8.322,
    "W_frame": 447,
    "C_frame": 456,
    "A_frame": 465,
    "E_frame": 472,
    "R_frame": 479,
    "RE_frame": 500,
    "evidence_pngs": "morgott_c0_00447.png, morgott_c0_00465.png, morgott_c0_00472.png, morgott_c0_00500.png",
    "confidence": "high",
    "notes": "Hand-calculated test fixture 1"
}

# Hand-calculated Good Entry 2 (Dagger Flurry -> Move_EmberWarden_DaggerFlurry)
GOOD_ENTRY_2 = {
    "priority": 2,
    "ref_id": "REF_DaggerFlurry_TapClose",
    "ref_to_original": "Move_EmberWarden_DaggerFlurry",
    "id_status": "proposed_new",
    "attack_family": "Conjured dagger close press",
    "t_W_orig": 125.018,
    "t_W_combat": 20.018,
    "t_C_orig": 125.168,
    "t_C_combat": 20.168,
    "t_A_orig": 125.218,
    "t_A_combat": 20.218,
    "t_E_orig": 125.318,
    "t_E_combat": 20.318,
    "t_R_orig": 125.418,
    "t_R_combat": 20.418,
    "t_RE_orig": 125.718,
    "t_RE_combat": 20.718,
    "W_frame": 1201,
    "C_frame": 1210,
    "A_frame": 1213,
    "E_frame": 1219,
    "R_frame": 1225,
    "RE_frame": 1243,
    "evidence_pngs": "morgott_c0_01201.png, morgott_c0_01213.png, morgott_c0_01219.png, morgott_c0_01243.png",
    "confidence": "high",
    "notes": "Hand-calculated test fixture 2"
}


class TestIngestMeasurements(unittest.TestCase):
    def test_good_entries_validate_cleanly(self):
        """Tests that two valid entries pass validation without error."""
        self.assertTrue(validate_entry(GOOD_ENTRY_1))
        self.assertTrue(validate_entry(GOOD_ENTRY_2))

    def test_hand_calculated_card_proposals(self):
        """Tests that derived card proposal fields match hand-calculated numbers exactly."""
        p1 = derive_card_proposal(GOOD_ENTRY_1)
        self.assertEqual(p1["MoveId"], "Move_EmberWarden_CurvedSlash_H1")
        self.assertEqual(p1["Confidence"], "high")
        self.assertEqual(p1["ActiveStartSeconds"], 0.3003)      # (465 - 447) / 59.9401 = 18 / 59.9401 = 0.3003
        self.assertEqual(p1["ActiveEndSeconds"], 0.4171)        # (472 - 447) / 59.9401 = 25 / 59.9401 = 0.4171
        self.assertEqual(p1["RecoveryEndSeconds"], 0.8842)      # (500 - 447) / 59.9401 = 53 / 59.9401 = 0.8842
        self.assertEqual(p1["WindupFrames"], 18)
        self.assertEqual(p1["ActiveFrames"], 7)
        self.assertEqual(p1["RecoveryFrames"], 28)              # RE - E = 500 - 472 = 28 (Lead Claude Decision)
        self.assertEqual(p1["RecoveryTailFrames"], 21)          # RE - R = 500 - 479 = 21
        self.assertEqual(p1["TotalAnimationFrames"], 53)
        self.assertEqual(p1["DesignStatus"], "DESIGN INPUT (measured from owner footage, observation only)")

        p2 = derive_card_proposal(GOOD_ENTRY_2)
        self.assertEqual(p2["MoveId"], "Move_EmberWarden_DaggerFlurry")
        self.assertEqual(p2["Confidence"], "high")
        self.assertEqual(p2["ActiveStartSeconds"], 0.2002)      # (1213 - 1201) / 59.9401 = 12 / 59.9401 = 0.2002
        self.assertEqual(p2["ActiveEndSeconds"], 0.3003)        # (1219 - 1201) / 59.9401 = 18 / 59.9401 = 0.3003
        self.assertEqual(p2["RecoveryEndSeconds"], 0.7007)      # (1243 - 1201) / 59.9401 = 42 / 59.9401 = 0.7007
        self.assertEqual(p2["WindupFrames"], 12)
        self.assertEqual(p2["ActiveFrames"], 6)
        self.assertEqual(p2["RecoveryFrames"], 24)              # RE - E = 1243 - 1219 = 24 (Lead Claude Decision)
        self.assertEqual(p2["RecoveryTailFrames"], 18)          # RE - R = 1243 - 1225 = 18
        self.assertEqual(p2["TotalAnimationFrames"], 42)
        self.assertEqual(p2["DesignStatus"], "DESIGN INPUT (measured from owner footage, observation only)")

    def test_clean_output_no_reference_names_leaked(self):
        """Tests that full ledger ingestion produces output with strictly NO reference identifiers."""
        ledger = {"entries": [GOOD_ENTRY_1, GOOD_ENTRY_2]}
        proposals = ingest_ledger(ledger)
        self.assertEqual(len(proposals), 2)
        
        serialized = json.dumps(proposals)
        self.assertNotIn("REF_", serialized, "Reference identifier 'REF_' leaked into output!")
        self.assertNotIn("Morgott", serialized, "Reference name 'Morgott' leaked into output!")
        self.assertNotIn("morgott", serialized, "Reference name 'morgott' leaked into output!")
        self.assertNotIn("Elden", serialized, "Reference name 'Elden' leaked into output!")
        self.assertNotIn("elden", serialized, "Reference name 'elden' leaked into output!")

    def test_bad_entry_1_null_field_refused(self):
        """Defect 1: Refuses entry when a required frame field is null."""
        bad = copy.deepcopy(GOOD_ENTRY_1)
        bad["W_frame"] = None
        with self.assertRaises(ValueError) as ctx:
            validate_entry(bad)
        self.assertIn("null or missing", str(ctx.exception))

    def test_bad_entry_2_non_integer_frame_refused(self):
        """Defect 2: Refuses entry when a frame value is a float."""
        bad = copy.deepcopy(GOOD_ENTRY_1)
        bad["A_frame"] = 465.5
        with self.assertRaises(ValueError) as ctx:
            validate_entry(bad)
        self.assertIn("must be integer", str(ctx.exception))

    def test_bad_entry_3_invalid_frame_order_refused(self):
        """Defect 3: Refuses entry when frame order violates W < C <= A <= E < R <= RE."""
        bad = copy.deepcopy(GOOD_ENTRY_1)
        bad["C_frame"] = 466  # C > A (466 > 465)
        with self.assertRaises(ValueError) as ctx:
            validate_entry(bad)
        self.assertIn("Invalid frame order", str(ctx.exception))

    def test_bad_entry_4_timestamp_conversion_mismatch_refused(self):
        """Defect 4: Refuses entry when t_combat != t_orig - 105.0."""
        bad = copy.deepcopy(GOOD_ENTRY_1)
        bad["t_W_combat"] = 12.000  # Should be 112.438 - 105.0 = 7.438
        with self.assertRaises(ValueError) as ctx:
            validate_entry(bad)
        self.assertIn("Combat time mismatch", str(ctx.exception))

    def test_bad_entry_5_seconds_vs_frames_drift_refused(self):
        """Defect 5: Refuses entry when elapsed seconds drift from frame delta by > 1 ms."""
        bad = copy.deepcopy(GOOD_ENTRY_1)
        bad["t_A_orig"] = 113.200  # Drifts from frame count (465 - 447)/59.9401 = 0.300 s
        bad["t_A_combat"] = 8.200
        with self.assertRaises(ValueError) as ctx:
            validate_entry(bad)
        self.assertIn("mismatch", str(ctx.exception))

    def test_bad_entry_6_malformed_evidence_png_refused(self):
        """Defect 6: Refuses entry when evidence PNG filename fails naming convention."""
        bad = copy.deepcopy(GOOD_ENTRY_1)
        bad["evidence_pngs"] = "morgott_c0_00447.png, invalid_screenshot.png, morgott_c0_00472.png, morgott_c0_00500.png"
        with self.assertRaises(ValueError) as ctx:
            validate_entry(bad)
        self.assertIn("Malformed evidence PNG", str(ctx.exception))

    def test_bad_entry_7_invalid_move_id_format_refused(self):
        """Defect 7: Refuses entry when move ID fails '^Move_[A-Za-z0-9]+_[A-Za-z0-9_]+$' regex."""
        bad = copy.deepcopy(GOOD_ENTRY_1)
        bad["ref_to_original"] = "DA_Move_Sevarog_InvalidFormat"
        with self.assertRaises(ValueError) as ctx:
            validate_entry(bad)
        self.assertIn("Invalid move ID format", str(ctx.exception))

    def test_bad_entry_8_forbidden_reference_name_in_id_refused(self):
        """Defect 8: Refuses entry when move ID contains forbidden reference word (Morgott/REF/Elden)."""
        bad = copy.deepcopy(GOOD_ENTRY_1)
        bad["ref_to_original"] = "Move_EmberWarden_MorgottSlash"
        with self.assertRaises(ValueError) as ctx:
            validate_entry(bad)
        self.assertIn("contains forbidden reference name", str(ctx.exception))

        bad["ref_to_original"] = "Move_EmberWarden_EldenFlurry"
        with self.assertRaises(ValueError) as ctx:
            validate_entry(bad)
        self.assertIn("contains forbidden reference name", str(ctx.exception))

    def test_bad_entry_9_collision_with_existing_card_refused(self):
        """Defect 9: Refuses entry when move ID collides with existing Cards/.uasset unless id_status == 'existing'."""
        bad = copy.deepcopy(GOOD_ENTRY_1)
        # Move_Sevarog_SwingSlow_F4.uasset exists in Content/OneBossFight/FrameworkProof/Cards/
        bad["ref_to_original"] = "Move_Sevarog_SwingSlow_F4"
        bad["id_status"] = "proposed_new"  # Collides without existing flag
        with self.assertRaises(ValueError) as ctx:
            validate_entry(bad)
        self.assertIn("collides with existing card", str(ctx.exception))

        # When id_status is 'existing', the collision is permitted
        bad["id_status"] = "existing"
        self.assertTrue(validate_entry(bad))

    def test_bad_entry_10_invalid_confidence_refused(self):
        """Defect 10: Refuses entry when confidence is missing or not in ('high', 'medium', 'low')."""
        bad = copy.deepcopy(GOOD_ENTRY_1)
        bad["confidence"] = None
        with self.assertRaises(ValueError) as ctx:
            validate_entry(bad)
        self.assertIn("confidence", str(ctx.exception))

        bad["confidence"] = "uncertain"
        with self.assertRaises(ValueError) as ctx:
            validate_entry(bad)
        self.assertIn("confidence", str(ctx.exception))

        bad["confidence"] = "medium"
        self.assertTrue(validate_entry(bad))
        bad["confidence"] = "low"
        self.assertTrue(validate_entry(bad))


if __name__ == "__main__":
    unittest.main(verbosity=2)
