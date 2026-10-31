"""test_fill_ledger.py - Unit test suite for fill_ledger.py.

Verifies:
- Round-trip with canonical D1/D2 milestone frames (W=447, C=456, A=465, E=472, R=479, RE=500):
  * Timing arithmetic: t_orig = round(105 + (f-1)/59.9401, 3), t_combat = round(t_orig - 105, 3).
  * Auto evidence filenames generation (6 canonical names).
  * Derived proposal matches hand-calculated ingest values exactly.
- 5 distinct refusal cases:
  1. Unknown clip ref_id refused with ValueError.
  2. Safety violation: out path equal to input template refused.
  3. Already-filled clip refused without --force flag.
  4. Invalid frame order (C > A) refused.
  5. Invalid confidence level refused.

Run: python -I test_fill_ledger.py
"""

import json
import os
import shutil
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(__file__))

from fill_ledger import (
    DEFAULT_TEMPLATE,
    compute_stage_timestamps,
    fill_clip_entry,
    process_ledger_fill
)


class TestFillLedger(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp(prefix="test_fill_ledger_")
        self.test_out_ledger = os.path.join(self.temp_dir, "test_measured_ledger.json")

    def tearDown(self):
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_compute_stage_timestamps_formula(self):
        """Tests canonical timestamp calculation formula."""
        # Frame 1 -> 105.000 s orig, 0.000 s combat
        t_orig, t_cbt = compute_stage_timestamps(1, fps=59.9401, combat_zero=105.0)
        self.assertEqual(t_orig, 105.000)
        self.assertEqual(t_cbt, 0.000)

        # Frame 447 -> 105 + 446/59.9401 = 112.441 s orig, 7.441 s combat
        t_orig, t_cbt = compute_stage_timestamps(447, fps=59.9401, combat_zero=105.0)
        self.assertEqual(t_orig, 112.441)
        self.assertEqual(t_cbt, 7.441)

    def test_round_trip_d1_example_matches_hand_values(self):
        """Tests that filling D1 frames produces exact hand-calculated proposal values."""
        proposal = process_ledger_fill(
            ledger_path=DEFAULT_TEMPLATE,
            out_path=self.test_out_ledger,
            clip_id="REF_CurvedSwordCombo_Chain1",
            W=447, C=456, A=465, E=472, R=479, RE=500,
            confidence="high",
            notes="camera: unobstructed track",
            evidence="auto",
            force=False
        )

        # Check proposal matches hand-computed ingest values
        self.assertEqual(proposal["MoveId"], "Move_EmberWarden_CurvedSlash_H1")
        self.assertEqual(proposal["Confidence"], "high")
        self.assertEqual(proposal["ActiveStartSeconds"], 0.3003)    # 18 / 59.9401 = 0.3003
        self.assertEqual(proposal["ActiveEndSeconds"], 0.4171)      # 25 / 59.9401 = 0.4171
        self.assertEqual(proposal["RecoveryEndSeconds"], 0.8842)    # 53 / 59.9401 = 0.8842
        self.assertEqual(proposal["WindupFrames"], 18)
        self.assertEqual(proposal["ActiveFrames"], 7)
        self.assertEqual(proposal["RecoveryFrames"], 28)            # RE - E = 500 - 472 = 28
        self.assertEqual(proposal["RecoveryTailFrames"], 21)        # RE - R = 500 - 479 = 21
        self.assertEqual(proposal["TotalAnimationFrames"], 53)
        self.assertEqual(
            proposal["DesignStatus"],
            "DESIGN INPUT (measured from owner footage, observation only)"
        )

        # Verify output file was created and contains the filled fields
        self.assertTrue(os.path.exists(self.test_out_ledger))
        with open(self.test_out_ledger, "r", encoding="utf-8") as fp:
            data = json.load(fp)

        entry = next(e for e in data["entries"] if e["ref_id"] == "REF_CurvedSwordCombo_Chain1")
        self.assertEqual(entry["W_frame"], 447)
        self.assertEqual(entry["RE_frame"], 500)
        self.assertEqual(entry["t_W_orig"], 112.441)
        self.assertEqual(entry["confidence"], "high")
        self.assertEqual(len(entry["evidence_pngs"]), 6)
        self.assertIn("morgott_c0_00447.png", entry["evidence_pngs"])
        self.assertIn("morgott_c0_00500.png", entry["evidence_pngs"])

    def test_refusal_1_unknown_clip_ref_id(self):
        """Refusal 1: Refuses clip ref_id not present in ledger."""
        with self.assertRaises(ValueError) as ctx:
            process_ledger_fill(
                ledger_path=DEFAULT_TEMPLATE,
                out_path=self.test_out_ledger,
                clip_id="REF_NonExistentClip_Unknown",
                W=447, C=456, A=465, E=472, R=479, RE=500,
                confidence="high"
            )
        self.assertIn("not found in ledger", str(ctx.exception))

    def test_refusal_2_out_path_identical_to_template(self):
        """Refusal 2: Safety violation: refuses out path equal to template ledger."""
        with self.assertRaises(ValueError) as ctx:
            process_ledger_fill(
                ledger_path=DEFAULT_TEMPLATE,
                out_path=DEFAULT_TEMPLATE,
                clip_id="REF_CurvedSwordCombo_Chain1",
                W=447, C=456, A=465, E=472, R=479, RE=500,
                confidence="high"
            )
        self.assertIn("Safety violation", str(ctx.exception))

    def test_refusal_3_already_filled_clip_without_force(self):
        """Refusal 3: Refuses overwriting an already-filled clip unless --force is set."""
        # Fill once
        process_ledger_fill(
            ledger_path=DEFAULT_TEMPLATE,
            out_path=self.test_out_ledger,
            clip_id="REF_CurvedSwordCombo_Chain1",
            W=447, C=456, A=465, E=472, R=479, RE=500,
            confidence="high"
        )

        # Attempt to fill again without force -> should raise ValueError
        with self.assertRaises(ValueError) as ctx:
            process_ledger_fill(
                ledger_path=DEFAULT_TEMPLATE,
                out_path=self.test_out_ledger,
                clip_id="REF_CurvedSwordCombo_Chain1",
                W=447, C=456, A=465, E=472, R=479, RE=500,
                confidence="high",
                force=False
            )
        self.assertIn("already filled", str(ctx.exception))

        # With force=True -> should succeed
        proposal = process_ledger_fill(
            ledger_path=DEFAULT_TEMPLATE,
            out_path=self.test_out_ledger,
            clip_id="REF_CurvedSwordCombo_Chain1",
            W=447, C=456, A=465, E=472, R=479, RE=500,
            confidence="high",
            force=True
        )
        self.assertEqual(proposal["MoveId"], "Move_EmberWarden_CurvedSlash_H1")

    def test_refusal_4_invalid_frame_ordering(self):
        """Refusal 4: Refuses frame sequence that violates W < C <= A <= E < R <= RE."""
        # C > A (466 > 465)
        with self.assertRaises(ValueError) as ctx:
            process_ledger_fill(
                ledger_path=DEFAULT_TEMPLATE,
                out_path=self.test_out_ledger,
                clip_id="REF_CurvedSwordCombo_Chain1",
                W=447, C=466, A=465, E=472, R=479, RE=500,
                confidence="high"
            )
        self.assertIn("Invalid frame order", str(ctx.exception))

        # W >= C (456 >= 456)
        with self.assertRaises(ValueError) as ctx:
            process_ledger_fill(
                ledger_path=DEFAULT_TEMPLATE,
                out_path=self.test_out_ledger,
                clip_id="REF_CurvedSwordCombo_Chain1",
                W=456, C=456, A=465, E=472, R=479, RE=500,
                confidence="high"
            )
        self.assertIn("Invalid frame order", str(ctx.exception))

    def test_refusal_5_invalid_confidence_level(self):
        """Refusal 5: Refuses confidence not in ('high', 'medium', 'low')."""
        with self.assertRaises(ValueError) as ctx:
            process_ledger_fill(
                ledger_path=DEFAULT_TEMPLATE,
                out_path=self.test_out_ledger,
                clip_id="REF_CurvedSwordCombo_Chain1",
                W=447, C=456, A=465, E=472, R=479, RE=500,
                confidence="uncertain"
            )
        self.assertIn("Invalid confidence", str(ctx.exception))


if __name__ == "__main__":
    unittest.main(verbosity=2)
