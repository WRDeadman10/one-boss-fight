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

import hashlib
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


    def test_template_ledger_has_10_entries_including_gap_pounce(self):
        """Tests that template ledger contains 10 entries including REF_MaceSlam_Sweep and REF_GapPounce_Close."""
        with open(DEFAULT_TEMPLATE, "r", encoding="utf-8") as fp:
            data = json.load(fp)
        self.assertEqual(len(data["entries"]), 10)
        
        # Verify 9th entry
        entry9 = next((e for e in data["entries"] if e["ref_id"] == "REF_MaceSlam_Sweep"), None)
        self.assertIsNotNone(entry9)
        self.assertEqual(entry9["priority"], 9)
        self.assertEqual(entry9["ref_to_original"], "Move_EmberWarden_MaceSlam")
        self.assertEqual(entry9["id_status"], "proposed_new")
        self.assertEqual(entry9["attack_family"], "Conjured mace raised hold then ground sweep")
        self.assertIsNone(entry9["W_frame"])

        # Verify 10th entry
        entry10 = next((e for e in data["entries"] if e["ref_id"] == "REF_GapPounce_Close"), None)
        self.assertIsNotNone(entry10)
        self.assertEqual(entry10["priority"], 10)
        self.assertEqual(entry10["ref_to_original"], "Move_EmberWarden_GapPounce")
        self.assertEqual(entry10["id_status"], "proposed_new")
        self.assertEqual(entry10["attack_family"], "Boss closes distance with a fast pounce then strikes")
        self.assertIsNone(entry10["W_frame"])

    def test_round_trip_c501_mace_slam_sweep_proposal(self):
        """Tests filling the 9th clip (REF_MaceSlam_Sweep) with Claude's C-501 marks."""
        proposal = process_ledger_fill(
            ledger_path=DEFAULT_TEMPLATE,
            out_path=self.test_out_ledger,
            clip_id="REF_MaceSlam_Sweep",
            W=1703, C=1787, A=1796, E=1801, R=1835, RE=1871,
            confidence="medium",
            notes="camera: steady, boss in frame the whole time, sweep slam",
            evidence="auto"
        )
        self.assertEqual(proposal["MoveId"], "Move_EmberWarden_MaceSlam")
        self.assertEqual(proposal["Confidence"], "medium")
        self.assertEqual(proposal["WindupFrames"], 93)            # A - W = 1796 - 1703 = 93
        self.assertEqual(proposal["ActiveFrames"], 5)             # E - A = 1801 - 1796 = 5
        self.assertEqual(proposal["RecoveryFrames"], 70)          # RE - E = 1871 - 1801 = 70
        self.assertEqual(proposal["RecoveryTailFrames"], 36)      # RE - R = 1871 - 1835 = 36
        self.assertEqual(proposal["TotalAnimationFrames"], 168)   # RE - W = 1871 - 1703 = 168
        self.assertEqual(proposal["ActiveStartSeconds"], 1.5515)  # 93 / 59.9401 = 1.5515
        self.assertEqual(proposal["ActiveEndSeconds"], 1.635)     # 98 / 59.9401 = 1.6350
        self.assertEqual(proposal["RecoveryEndSeconds"], 2.8028)  # 168 / 59.9401 = 2.8028



    def test_sync_appends_and_fills_10th_entry_preserving_prior_entries(self):
        """Tests that syncing a 9-entry ledger with 10-entry template appends 10th and fills it."""
        with open(DEFAULT_TEMPLATE, "r", encoding="utf-8") as fp:
            tmpl_data = json.load(fp)

        # Create 9-entry ledger
        partial_data = {"entries": tmpl_data["entries"][:9]}
        # Mark an entry in 1-9 to confirm custom values are preserved
        partial_data["entries"][0]["notes"] = "preserved note"
        with open(self.test_out_ledger, "w", encoding="utf-8") as fp:
            json.dump(partial_data, fp, indent=2)

        prior_entries_json = json.dumps(partial_data["entries"], sort_keys=True)
        prior_sha = hashlib.sha256(prior_entries_json.encode("utf-8")).hexdigest()

        # Fill the 10th entry (REF_GapPounce_Close)
        proposal = process_ledger_fill(
            ledger_path=DEFAULT_TEMPLATE,
            out_path=self.test_out_ledger,
            clip_id="REF_GapPounce_Close",
            W=100, C=110, A=120, E=125, R=130, RE=150,
            confidence="high",
            notes="sync test fill",
            evidence="auto"
        )
        self.assertEqual(proposal["MoveId"], "Move_EmberWarden_GapPounce")

        with open(self.test_out_ledger, "r", encoding="utf-8") as fp:
            after_data = json.load(fp)

        self.assertEqual(len(after_data["entries"]), 10)
        # Verify 1-9 entries are unchanged
        after_prior_json = json.dumps(after_data["entries"][:9], sort_keys=True)
        after_prior_sha = hashlib.sha256(after_prior_json.encode("utf-8")).hexdigest()
        self.assertEqual(prior_sha, after_prior_sha)
        self.assertEqual(after_data["entries"][0]["notes"], "preserved note")

        # Verify 10th entry is populated
        entry10 = after_data["entries"][9]
        self.assertEqual(entry10["ref_id"], "REF_GapPounce_Close")
        self.assertEqual(entry10["W_frame"], 100)
        self.assertEqual(entry10["confidence"], "high")

    def test_sync_unknown_clip_still_refused(self):
        """Tests that unknown clip is still refused even with sync."""
        with self.assertRaises(ValueError) as ctx:
            process_ledger_fill(
                ledger_path=DEFAULT_TEMPLATE,
                out_path=self.test_out_ledger,
                clip_id="REF_UnknownNonExistent_Move",
                W=100, C=110, A=120, E=125, R=130, RE=150,
                confidence="high"
            )
        self.assertIn("not found in ledger", str(ctx.exception))

    def test_sync_noop_when_equal(self):
        """Tests that sync is a no-op when out ledger already has all template entries."""
        with open(DEFAULT_TEMPLATE, "r", encoding="utf-8") as fp:
            tmpl_data = json.load(fp)

        with open(self.test_out_ledger, "w", encoding="utf-8") as fp:
            json.dump(tmpl_data, fp, indent=2)

        before_json = json.dumps(tmpl_data["entries"], sort_keys=True)
        before_sha = hashlib.sha256(before_json.encode("utf-8")).hexdigest()

        # Run sync-only
        process_ledger_fill(
            ledger_path=DEFAULT_TEMPLATE,
            out_path=self.test_out_ledger,
            sync_only=True
        )

        with open(self.test_out_ledger, "r", encoding="utf-8") as fp:
            after_data = json.load(fp)

        self.assertEqual(len(after_data["entries"]), len(tmpl_data["entries"]))
        after_json = json.dumps(after_data["entries"], sort_keys=True)
        after_sha = hashlib.sha256(after_json.encode("utf-8")).hexdigest()
        self.assertEqual(before_sha, after_sha)

    def test_template_file_hash_unchanged(self):
        """Tests that template file hash is completely untouched across sync and fill."""
        with open(DEFAULT_TEMPLATE, "rb") as fp:
            initial_sha = hashlib.sha256(fp.read()).hexdigest()

        # Run sync-only
        process_ledger_fill(
            ledger_path=DEFAULT_TEMPLATE,
            out_path=self.test_out_ledger,
            sync_only=True
        )
        # Run fill
        process_ledger_fill(
            ledger_path=DEFAULT_TEMPLATE,
            out_path=self.test_out_ledger,
            clip_id="REF_CurvedSwordCombo_Chain1",
            W=447, C=456, A=465, E=472, R=479, RE=500,
            confidence="high",
            force=True
        )

        with open(DEFAULT_TEMPLATE, "rb") as fp:
            final_sha = hashlib.sha256(fp.read()).hexdigest()

        self.assertEqual(initial_sha, final_sha)

    def test_d3_measured_ledger_sync_and_subtree_integrity(self):
        """Tests real D3 ledger: 10 entries present, filled entries subtree identical."""
        d3_path = os.path.normpath(
            os.path.join(os.path.dirname(__file__), "..", "..", "Claude", "D3", "D3_MEASURED_LEDGER.json")
        )
        self.assertTrue(os.path.exists(d3_path), f"D3 ledger not found at {d3_path}")

        with open(d3_path, "r", encoding="utf-8") as fp:
            d3_data = json.load(fp)

        self.assertEqual(len(d3_data["entries"]), 10)
        entry10 = d3_data["entries"][-1]
        self.assertEqual(entry10["ref_id"], "REF_GapPounce_Close")
        self.assertEqual(entry10["priority"], 10)
        self.assertIsNone(entry10["W_frame"])

        # Check filled entries subtrees
        filled = [e for e in d3_data["entries"] if e.get("confidence") is not None]
        self.assertEqual(len(filled), 2)
        filled_ids = {e["ref_id"] for e in filled}
        self.assertEqual(filled_ids, {"REF_HolySwordRain_Setup", "REF_MaceSlam_Sweep"})

        mace = next(e for e in filled if e["ref_id"] == "REF_MaceSlam_Sweep")
        self.assertEqual(mace["W_frame"], 1703)
        self.assertEqual(mace["A_frame"], 1796)
        self.assertEqual(mace["confidence"], "medium")

        rain = next(e for e in filled if e["ref_id"] == "REF_HolySwordRain_Setup")
        self.assertEqual(rain["W_frame"], 2381)
        self.assertEqual(rain["A_frame"], 2566)
        self.assertEqual(rain["confidence"], "low")

if __name__ == "__main__":
    unittest.main(verbosity=2)
