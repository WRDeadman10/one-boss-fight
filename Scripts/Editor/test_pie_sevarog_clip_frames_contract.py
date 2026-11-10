"""Offline checks for the Sevarog still-frame PIE driver; never imports Unreal."""
import ast
import sys
import unittest
from pathlib import Path


HERE = Path(__file__).resolve().parent
PROJECT_ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))

from sevarog_clip_frame_rules import sample_times  # noqa: E402


DRIVER_PATH = HERE / "pie_sevarog_clip_frames.py"
MESH_RELATIVE = Path(
    "Content/ParagonSevarog/Characters/Heroes/Sevarog/Meshes/Sevarog.uasset"
)
ANIMATION_RELATIVE = Path(
    "Content/ParagonSevarog/Characters/Heroes/Sevarog/Animations"
)
CLIPS = (
    "Swing1_Medium",
    "Swing2_Medium",
    "Swing3_Slow",
    "Swing1_FAST_v2",
    "Speedburst",
    "Ultimate_Swing_120fps",
    "Subjugation",
    "Soul_Siphon",
)


class SampleTimeRulesTests(unittest.TestCase):
    def test_fixed_rate_times_include_exact_end_once(self):
        self.assertEqual(sample_times(0.2, 15.0), [0.0, 1.0 / 15.0, 2.0 / 15.0, 0.2])
        times = sample_times(1.0, 15.0)
        self.assertEqual(len(times), 16)
        self.assertEqual(times[0], 0.0)
        self.assertEqual(times[-1], 1.0)
        self.assertEqual(len(set(times)), len(times))

    def test_invalid_duration_or_rate_refuses(self):
        for duration in (-0.01, float("nan"), float("inf")):
            with self.subTest(duration=duration), self.assertRaises(ValueError):
                sample_times(duration)
        for rate in (0.0, -1.0, float("nan"), float("inf")):
            with self.subTest(rate=rate), self.assertRaises(ValueError):
                sample_times(1.0, rate)


class DriverContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = DRIVER_PATH.read_text(encoding="utf-8")
        cls.tree = ast.parse(cls.source)

    def test_mesh_and_all_clip_assets_exist_on_disk(self):
        self.assertTrue((PROJECT_ROOT / MESH_RELATIVE).is_file())
        for clip in CLIPS:
            with self.subTest(clip=clip):
                self.assertTrue((PROJECT_ROOT / ANIMATION_RELATIVE / (clip + ".uasset")).is_file())
                self.assertIn('"%s"' % clip, self.source)

    def test_driver_holds_hides_and_temporarily_swaps_player_mesh(self):
        self.assertIn('"RPGBossEncounter"', self.source)
        self.assertIn("encounter.hold_for_test(True)", self.source)
        self.assertIn("boss.set_actor_hidden_in_game(True)", self.source)
        self.assertIn('get_name() == "CharacterMesh0"', self.source)
        self.assertIn('get_editor_property("skeletal_mesh")', self.source)
        self.assertIn("mesh.set_skeletal_mesh_asset(sevarog_mesh)", self.source)
        self.assertIn("mesh.set_skeletal_mesh_asset(original_mesh)", self.source)

    def test_side_view_fixed_position_capture_contract(self):
        self.assertIn("FRAME_RATE = 15.0", self.source)
        self.assertIn("mesh.set_position(float(t), False)", self.source)
        self.assertIn("mesh.set_play_rate(0.0)", self.source)
        self.assertIn("yaw = pawn.get_actor_rotation().yaw + 90.0", self.source)
        self.assertIn("OUT_ROOT = \"D:/FightVideo/sevarog_frames\"", self.source)
        self.assertIn('"%s_%03d_%.3f.png"', self.source)
        self.assertIn("BRIGHT_BYTES = 300000", self.source)
        self.assertIn("HighResShot %dx%d filename=%s", self.source)
        self.assertIn("[SevarogFrames] finished:", self.source)

    def test_pose_refresh_uses_ue55_verified_position_wait_pattern(self):
        # C-1243 confirmed set_position/wait against the passing Lead PIE run;
        # tick_animation and refresh_bone_transforms are not exposed in UE 5.5 Python.
        called_attributes = {
            node.func.attr for node in ast.walk(self.tree)
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
        }
        self.assertNotIn("tick_animation", called_attributes)
        self.assertNotIn("refresh_bone_transforms", called_attributes)
        position = self.source.index("mesh.set_position(float(t), False)")
        wait = self.source.index("yield from wait_game_seconds(0.15)", position)
        capture = self.source.index("size = yield from shot(path)", position)
        self.assertLess(position, wait)
        self.assertLess(wait, capture)

    def test_refuses_existing_outputs_and_never_saves_assets(self):
        self.assertIn("refusing to overwrite existing frame", self.source)
        self.assertIn("refusing to overwrite warm-up frame", self.source)
        self.assertIn("os.remove(path)", self.source)  # only driver-owned warm/retry PNGs
        self.assertNotRegex(self.source, r"(?i)\b(save_asset|save_loaded_asset)\s*\(")
        self.assertIn("finally:\n        restore_player_mesh()", self.source)
        self.assertIn("plc.end_play()", self.source)

    def test_both_python_files_parse(self):
        ast.parse(DRIVER_PATH.read_text(encoding="utf-8"))
        ast.parse((HERE / "sevarog_clip_frame_rules.py").read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
