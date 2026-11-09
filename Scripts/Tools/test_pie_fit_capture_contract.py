import ast
import json
import pathlib
import tempfile
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "Scripts" / "Editor" / "pie_fit_capture.py"


class PieFitCaptureContract(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = SCRIPT.read_text(encoding="utf-8")
        cls.tree = ast.parse(cls.source)
        cls.ns = {"__name__": "fit_capture_contract"}
        exec(compile(cls.tree, str(SCRIPT), "exec"), cls.ns)

    def fixture(self):
        return {"schema_version": 1, "blind_id": "Candidate_B",
                "candidate": "PrivateCharacterName",
                "target_mesh": "/Game/Characters/Target.Target",
                "source_mesh": "/Game/Mannequin/Body",
                "clips": [{"id": clip_id, "name": name,
                           "source": "/Game/Sources/" + name,
                           "output": "/Game/Fit/" + name}
                          for clip_id, name in (("ER-A1", "Backstep"),
                                                ("ER-A2", "AirLight"),
                                                ("ER-A3", "AirHeavy"),
                                                ("ER-A4", "GuardCounter"),
                                                ("PACK-ROLL", "ForwardRoll"),
                                                ("PACK-BLOCK", "BlockLoop"))]}

    def test_manifest_accepts_exact_six_slots_and_returns_only_blind_data(self):
        parsed = self.ns["validate_manifest"](self.fixture(), "Candidate_B")
        self.assertEqual(parsed["blind_id"], "Candidate_B")
        self.assertEqual(len(parsed["clips"]), 6)
        self.assertNotIn("candidate", parsed)
        self.assertNotIn("PrivateCharacterName", json.dumps(parsed))

    def test_manifest_fails_closed_on_blind_id_inventory_and_paths(self):
        validate = self.ns["validate_manifest"]
        with self.assertRaises(ValueError):
            validate(self.fixture(), "Candidate_A")
        data = self.fixture()
        data["clips"].pop()
        with self.assertRaises(ValueError):
            validate(data, "Candidate_B")
        data = self.fixture()
        data["clips"][0]["output"] = "/Game/../Private/Asset"
        with self.assertRaises(ValueError):
            validate(data, "Candidate_B")

    def test_cli_and_capture_filename_are_blind_and_unique_safe(self):
        parse = self.ns["command_line_blind_id"]
        self.assertEqual(parse("Editor -ERFitBlindId=Candidate_C -nosound"), "Candidate_C")
        with self.assertRaises(ValueError):
            parse("Editor -ERFitBlindId=Steel")
        name = self.ns["capture_filename"]("Backstep_Mixamo_V2", "three_quarter", 1)
        self.assertEqual(name, "Backstep_Mixamo_V2_three_quarter_001.png")
        self.assertEqual(self.ns["capture_filename"]("Backstep_Mixamo_V2", "side", 5),
                         "Backstep_Mixamo_V2_side_005.png")
        with self.assertRaises(ValueError):
            self.ns["capture_filename"]("../Steel", "side")

    def test_pie_capture_contract_is_transient_blind_and_has_required_markers(self):
        for token in ("set_skeletal_mesh_asset", "play_animation", "ANIMATION_SINGLE_NODE",
                      "slomo 0.5", "slomo 1.0", "HighResShot 960x540",
                      "D:/FightVideo/fit_test", "Candidate_0", "warmup", "finished:",
                      "H019_ENCOUNTER_DEFINITION"):
            self.assertIn(token, self.source)
        self.assertNotIn("EditorAssetLibrary.save", self.source)
        self.assertNotIn("candidate name", self.source.lower())
        self.assertIn("target_mesh", self.source)
        self.assertIn("output", self.source)

    def test_warmup_runs_after_mesh_animation_and_camera_setup(self):
        capture = self.source.split("def capture_sequence(", 1)[1].split("def run_capture(", 1)[0]
        self.assertLess(capture.index("aim_view("), capture.index("mesh.play_animation("))
        self.assertLess(capture.index("mesh.play_animation("), capture.index("for warm_index"))
        runner = self.source.split("def run_capture(", 1)[1].split("def tick(", 1)[0]
        self.assertLess(runner.index("set_mesh(mesh, body)"), runner.index("yield from capture_sequence"))

    def test_black_then_bright_capture_retries_same_frame_up_to_success(self):
        readings = iter((0.0, 52.0))
        attempted = []
        retries = []

        def fake_capture(attempt):
            attempted.append(attempt)
            yield None
            return next(readings)

        def note_retry(attempt, brightness):
            retries.append((attempt, brightness))

        capture = self.ns["retry_bright_capture"](fake_capture, note_retry)
        while True:
            try:
                next(capture)
            except StopIteration as result:
                self.assertEqual(result.value, (2, 52.0))
                break
        self.assertEqual(attempted, [1, 2])
        self.assertEqual(retries, [(1, 0.0)])

    def test_dark_capture_stops_after_ten_attempts(self):
        attempted = []

        def always_black(attempt):
            attempted.append(attempt)
            yield None
            return 0.0

        capture = self.ns["retry_bright_capture"](always_black, lambda *_: None,
                                                   max_attempts=10)
        with self.assertRaisesRegex(RuntimeError, "after 10 attempts"):
            while True:
                next(capture)
        self.assertEqual(attempted, list(range(1, 11)))

    def test_warmup_requires_three_consecutive_bright_frames(self):
        update = self.ns["update_bright_streak"]
        streak = 0
        for brightness in (0.0, 52.0, 52.0, 0.0, 52.0, 52.0):
            streak = update(streak, brightness)
        self.assertEqual(streak, 2)
        self.assertEqual(update(streak, 52.0), 3)

    def test_capture_spacing_requires_both_minimum_game_time_and_ticks(self):
        complete = self.ns["capture_spacing_complete"]
        self.assertFalse(complete(10.0, 10.3, 4))
        self.assertFalse(complete(10.0, 10.1, 5))
        self.assertTrue(complete(10.0, 10.2, 5))
        self.assertIn("MIN_CAPTURE_SPACING_GAME_SECONDS = 0.2", self.source)
        self.assertIn("MIN_CAPTURE_SPACING_TICKS = 5", self.source)
        self.assertEqual(self.source.count("yield from wait_capture_spacing(world)"), 2)

    def test_editor_game_time_uses_supported_gameplay_statics_api(self):
        self.assertIn("unreal.GameplayStatics.get_time_seconds(world)", self.source)
        self.assertNotIn("world.get_time_seconds()", self.source)

    def test_preview_pose_is_five_metres_radially_outward(self):
        class Point:
            def __init__(self, x, y, z):
                self.x, self.y, self.z = x, y, z

        pose = self.ns["preview_player_pose"](Point(10, 20, 100), Point(610, 820, 140), 0)
        self.assertAlmostEqual(((pose[0] - 10) ** 2 + (pose[1] - 20) ** 2) ** 0.5, 500)
        self.assertEqual(pose[2], 140)
        self.assertAlmostEqual(pose[3], 53.1301023542)

    def test_preview_pose_has_boss_facing_fallback_and_look_class_filter(self):
        class Point:
            x, y, z = 1, 2, 3

        pose = self.ns["preview_player_pose"](Point(), Point(), 90)
        self.assertAlmostEqual(pose[0], 1)
        self.assertAlmostEqual(pose[1], -498)
        self.assertTrue(self.ns["is_look_component_class"]("RPGLookSword"))
        self.assertTrue(self.ns["is_look_component_class"]("RPGLook"))
        self.assertFalse(self.ns["is_look_component_class"]("RPGCamera"))

    def test_boss_stays_in_world_and_warmup_logs_camera_state(self):
        runner = self.source.split("def run_capture(", 1)[1].split("def tick(", 1)[0]
        capture = self.source.split("def capture_sequence(", 1)[1].split("def run_capture(", 1)[0]
        self.assertIn("encounter.hold_for_test(True)", runner)
        self.assertIn("boss.set_actor_hidden_in_game(True)", runner)
        self.assertIn("is_look_component_class(class_name)", runner)
        self.assertIn("preview_player_pose(", runner)
        self.assertIn("warmup_state", capture)
        self.assertIn("camera_diagnostics(pc, pawn)", capture)
        self.assertIn("line_trace_single", self.source)
        self.assertIn("camera_player_trace", self.source)
        aim = self.source.split("def aim_view(", 1)[1].split("def capture_frame_with_retries(", 1)[0]
        self.assertIn("pc.set_control_rotation", aim)
        self.assertNotIn("pawn.set_actor_rotation", aim)
        self.assertIn("distance=500.0", self.source)
        self.assertIn("fade_amount", self.source)
        self.assertNotIn("50000.0", runner)

    def test_rerun_clears_only_numbered_driver_frames(self):
        with tempfile.TemporaryDirectory() as temp:
            folder = pathlib.Path(temp)
            (folder / "Backstep_side_001.png").write_bytes(b"failed capture")
            (folder / "Backstep_side_002_attempt_02.png").write_bytes(b"retry frame")
            self.assertEqual(self.ns["clear_owned_frames"](folder), 2)
            self.assertEqual(list(folder.iterdir()), [])
            (folder / "AG_notes.txt").write_text("keep", encoding="utf-8")
            with self.assertRaises(RuntimeError):
                self.ns["clear_owned_frames"](folder)
            self.assertTrue((folder / "AG_notes.txt").is_file())


if __name__ == "__main__":
    unittest.main()
