"""BQ-86 in-process tests for sevarog_sfx_cue_plan, using the real authored card rows (read-only). Nothing is authored."""
from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
import sevarog_sfx_cue_plan as P  # noqa: E402

_spec = importlib.util.spec_from_file_location("sevarog_author_for_sfx", ROOT / "Scripts" / "Editor" / "author_sevarog_draft_cards.py")
AUTHOR = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(AUTHOR)


class SfxCuePlan(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows = AUTHOR.build_candidate_specs(AUTHOR.read_f5_cards(ROOT))
        cls.slots = P.cue_slots(cls.rows)
        cls.by = {(s["move_id"], s["cue_id"]): s for s in cls.slots}

    def test_every_card_has_a_windup_slot_and_no_sound_yet(self):
        self.assertEqual(sum(s["cue_id"] == "Cue_Windup" for s in self.slots), len(self.rows))
        self.assertTrue(all(s["sound"] is None for s in self.slots))

    def test_slot_times_follow_card_timings(self):
        s6 = self.by[("Move_Sevarog_Ultimate_Swing_120fps_C1277", "Cue_Swing")]
        self.assertAlmostEqual(s6["time_seconds"], 0.667)
        s7 = self.by[("Move_Sevarog_Subjugation_C1277", "Cue_AreaResolve")]
        self.assertAlmostEqual(s7["time_seconds"], 0.8 + 0.75)
        s8 = self.by[("Move_Sevarog_Soul_Siphon_C1277", "Cue_ChannelStart")]
        self.assertAlmostEqual(s8["time_seconds"], 0.267)
        self.assertNotIn(("Move_Sevarog_Subjugation_C1277", "Cue_Swing"), self.by)   # no hit window, no swing cue

    def test_slots_are_inside_each_card(self):
        recovery = {r["move_id"]: float(r["recovery_end_seconds"]) for r in self.rows}
        for s in self.slots:
            self.assertGreaterEqual(s["time_seconds"], 0.0)
            self.assertLessEqual(s["time_seconds"], recovery[s["move_id"]], s)

    def test_validate_picks(self):
        key = ("Move_Sevarog_Soul_Siphon_C1277", "Cue_ChannelStart")
        ok = P.validate_picks(self.slots, {key: "/Game/OneBossFight/Audio/SFX/S_Siphon.S_Siphon"})
        self.assertEqual(ok["errors"], [])
        self.assertIn(("Move_Sevarog_Subjugation_C1277", "Cue_Windup"), ok["missing"])   # missing reported, not filled
        bad = P.validate_picks(self.slots, {
            key: "/Game/AdvancedARPGCombat/Sounds/S_X.S_X",
            ("Move_Nope", "Cue_Windup"): "/Game/A/B.B",
            ("Move_Sevarog_Subjugation_C1277", "Cue_Windup"): "C:/sounds/x.wav",
        })
        self.assertEqual(len(bad["errors"]), 3)


if __name__ == "__main__":
    unittest.main()
