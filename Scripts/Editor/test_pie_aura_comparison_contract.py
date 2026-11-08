"""Offline contracts for the Lead-only paired Tier 2 aura comparison."""
import ast
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "Scripts" / "Editor" / "pie_aura_comparison.py"


class AuraComparisonContracts(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = SCRIPT.read_text(encoding="utf-8")
        cls.tree = ast.parse(cls.source)

    def test_candidate_is_separate_and_both_assets_are_read_back(self):
        source = self.source
        self.assertIn("NS_Boss_PhaseTwoAura.NS_Boss_PhaseTwoAura", source)
        self.assertIn("NS_Boss_PhaseTwoAura_Boost.NS_Boss_PhaseTwoAura_Boost", source)
        self.assertIn("path_of(S[\"original\"]) != APPROVED_PATH", source)
        self.assertIn("path_of(actual) != CANDIDATE_PATH", source)
        self.assertIn('S["component"].set_asset(S["original"])', source)

    def test_comparison_controls_health_framing_resolution_and_capture_completion(self):
        source = self.source
        for marker in ('maximum * 0.5', 'fraction=%.4f', 'distance=260.0',
                       'HighResShot 960x540 filename=', 'FRAME_READY label=%s',
                       'camera_pos=%s control_rot=%s', 'warmup_discard', 'approved', 'boost_candidate'):
            self.assertIn(marker, source)
        self.assertIn('Path(S["pending"]).is_file()', source)
        self.assertIn('refusing to overwrite prior capture', source)
        self.assertIn('re.fullmatch(r"[A-Za-z0-9_-]{1,64}", RUN_TAG)', source)

    def test_transient_only_and_safe_failure_boundaries(self):
        source = self.source
        self.assertNotIn("set_editor_property", source)
        self.assertIn('getattr(S["component"], "set_asset", None)', source)
        self.assertIn("refusing editor-property mutation", source)
        self.assertIn('set_asset(S["original"])', source)
        self.assertIn('"rpg.Art.Tier2 0"', source)
        self.assertIn("plc.end_play()", source)
        self.assertIn("candidate missing", source)

    def test_each_serialized_frame_gets_a_provenance_manifest_line(self):
        source = self.source
        for key in ('"run": RUN_TAG', '"route": ROUTE', '"asset": asset',
                    '"health": health', '"max_health": maximum',
                    '"camera_position"', '"pivot_position"', '"png": str(png)',
                    '"png_exists": Path(png).is_file()'):
            self.assertIn(key, source)
        self.assertIn('manifest.jsonl', source)
        self.assertIn('write_manifest(label, S["pending"], brightness)', source)
        self.assertIn('return "UNKNOWN"', source)

    def test_approved_and_candidate_frames_use_one_setup_and_distinct_assets(self):
        source = self.source
        self.assertIn('attribute(boss, "Set Current Attribute Value", maximum * 0.5)', source)
        self.assertIn('lane(pc, pawn, boss)', source)
        approved = source.index('yield from wait_capture("approved", world)')
        swap = source.index('setter(candidate)', approved)
        candidate = source.index('yield from wait_capture("boost_candidate", world)', swap)
        self.assertLess(approved, swap)
        self.assertLess(swap, candidate)
        self.assertIn('if path_of(S["original"]) != APPROVED_PATH', source)
        self.assertIn('if path_of(actual) != CANDIDATE_PATH', source)

    def test_highres_shot_uses_absolute_forward_slash_path_and_20_second_wait(self):
        source = self.source
        self.assertIn('"D:/FightVideo/aura_compare"', source)
        self.assertIn('target.resolve().as_posix()', source)
        self.assertIn('log("CAPTURE_COMMAND " + command)', source)
        self.assertIn('command = "HighResShot 960x540 filename=%s" % S["pending"]', source)
        self.assertIn('time.perf_counter() + 20.0', source)
        self.assertIn('while not capture(label, world)', source)
        self.assertIn('stable_polls >= 2', source)

    def test_render_settle_discard_brightness_gate_and_candidate_activation(self):
        source = self.source
        self.assertIn('yield from wait_game_seconds(3.0, world)', source)
        self.assertIn('range(1, 4)', source)
        self.assertIn('FRAME_BRIGHTNESS label=%s mean_gray=%.3f threshold=5', source)
        self.assertIn('brightness < 5.0', source)
        self.assertIn('activate(True)', source)
        self.assertIn('CANDIDATE_READBACK asset=%s active=%s', source)
        self.assertIn('candidate_discard_%d', source)


if __name__ == "__main__":
    unittest.main(verbosity=2)
