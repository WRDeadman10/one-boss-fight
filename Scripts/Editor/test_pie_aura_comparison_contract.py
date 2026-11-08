"""Offline contracts for the Lead-only paired Tier 2 aura comparison."""
import ast
import subprocess
import shutil
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
        self.assertIn('restore_original_asset(S["component"], S["original"])', source)

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
        self.assertIn('component.set_asset(original)', source)
        self.assertIn('transient aura restore mismatch', source)
        self.assertIn('RESTORE asset=%s verified=true', source)
        self.assertIn('"rpg.Art.Tier2 0"', source)
        self.assertIn("plc.end_play()", source)
        self.assertIn("candidate missing", source)

    def test_each_serialized_frame_gets_a_provenance_manifest_line(self):
        source = self.source
        for key in ('"run": RUN_TAG', '"route": ROUTE', '"asset": asset',
                    '"capture_id": RUN_TAG + ":" + label', '"phase": phase',
                    '"health": health', '"max_health": maximum',
                    '"active": active', '"attach_parent": attach_parent',
                    '"attach_socket": attach_socket', '"component_position": component_position',
                    '"component_rotation": component_rotation',
                    '"camera_position"', '"pivot_position"', '"png": str(png)',
                    '"png_exists": Path(png).is_file()',
                    '"png_sha256": hashlib.sha256(Path(png).read_bytes()).hexdigest()'):
            self.assertIn(key, source)
        self.assertIn('manifest.jsonl', source)
        self.assertIn('write_manifest(label, S["pending"], brightness)', source)
        self.assertIn('FRAME_REQUEST run=%s route=%s phase=%s capture_id=%s', source)
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

    def test_failed_capture_stages_emit_same_run_failure_receipt(self):
        source = self.source
        self.assertIn('def capture_failure(label, reason):', source)
        self.assertIn('CAPTURE_FAILURE run=%s route=%s phase=%s capture_id=%s', source)
        self.assertGreaterEqual(source.count('capture_failure(label,'), 3)
        self.assertIn('"completion": "READY"', source)

    def test_render_settle_discard_brightness_gate_and_candidate_activation(self):
        source = self.source
        self.assertIn('yield from wait_game_seconds(3.0, world)', source)
        self.assertIn('for index in range(1, MAX_WARMUP_FRAMES + 1)', source)
        self.assertIn('yield from warmup_until_visible(world, "candidate_discard")', source)
        self.assertIn('FRAME_BRIGHTNESS label=%s mean_gray=%.3f threshold=5', source)
        self.assertIn('brightness < 5.0', source)
        self.assertIn('activate(True)', source)
        self.assertIn('CANDIDATE_READBACK asset=%s active=%s', source)
        self.assertIn('label = "%s_%d" % (label_prefix, index)', source)

    def test_approved_only_diagnostic_never_loads_or_swaps_candidate(self):
        source = self.source
        self.assertIn('APPROVED_ONLY = os.environ.get("AURA_COMPARE_APPROVED_ONLY", "0") == "1"', source)
        approved = source.index('yield from wait_capture("approved", world)')
        branch = source.index('if APPROVED_ONLY:', approved)
        candidate = source.index('candidate = unreal.load_asset(CANDIDATE_PATH)', branch)
        self.assertLess(approved, branch)
        self.assertLess(branch, candidate)
        self.assertIn('log("APPROVED_ONLY complete; candidate was not loaded or swapped")', source[branch:candidate])

    def test_transient_restore_helper_readback_and_failure_cleanup_are_explicit(self):
        source = self.source
        self.assertIn('restore_original_asset(S["component"], S["original"])', source)
        self.assertIn('finish("error")', source)
        self.assertIn('def restore_original_asset(component, original):', source)
        node = next(item for item in self.tree.body
                    if isinstance(item, ast.FunctionDef) and item.name == "restore_original_asset")
        isolated = ast.Module(body=[node], type_ignores=[])
        ast.fix_missing_locations(isolated)
        namespace = {"path_of": lambda value: value.path, "log": lambda _: None, "RuntimeError": RuntimeError}
        exec(compile(isolated, str(SCRIPT), "exec"), namespace)

        class Component:
            def __init__(self, asset):
                self.asset = asset
                self.active = False

            def set_asset(self, asset):
                self.asset = asset

            def activate(self, enabled):
                self.active = enabled

            def get_asset(self):
                return self.asset

        original = type("Asset", (), {"path": "/approved"})()
        candidate = type("Asset", (), {"path": "/candidate"})()
        component = Component(candidate)
        try:
            raise ValueError("injected comparison failure")
        except ValueError:
            restored = namespace["restore_original_asset"](component, original)
        self.assertEqual(restored, "/approved")
        self.assertTrue(component.active)
        self.assertIs(component.get_asset(), original)

    def test_frame_ready_log_uses_the_same_fake_manifest_record(self):
        self.assertIn('manifest = write_manifest(label, S["pending"], brightness)', self.source)
        self.assertIn('log_frame_ready(label, S["pending"], manifest)', self.source)
        node = next(item for item in self.tree.body
                    if isinstance(item, ast.FunctionDef) and item.name == "log_frame_ready")
        isolated = ast.Module(body=[node], type_ignores=[])
        ast.fix_missing_locations(isolated)
        output = []
        namespace = {"log": output.append}
        exec(compile(isolated, str(SCRIPT), "exec"), namespace)
        manifest = {"asset": "/Game/TestAura", "active": True,
                    "attach_parent": "CharacterMesh0", "attach_socket": "None",
                    "component_position": "(1,2,3)", "component_rotation": "(0,0,0)"}
        namespace["log_frame_ready"]("approved", "D:/capture.png", manifest)
        self.assertEqual(len(output), 1)
        self.assertIn("asset=/Game/TestAura active=True", output[0])
        self.assertIn("attach_parent=CharacterMesh0 attach_socket=None", output[0])
        self.assertIn("component_pos=(1,2,3) component_rot=(0,0,0)", output[0])

    def test_render_warmup_is_brightness_driven_and_bounded(self):
        self.assertIn("MAX_WARMUP_FRAMES = 20", self.source)
        self.assertIn("WARMUP_BRIGHTNESS_FLOOR = 5.0", self.source)
        self.assertIn("yield from warmup_until_visible(world)", self.source)
        self.assertIn("warmup brightness floor not reached", self.source)
        self.assertNotIn('for index in range(1, 4):\n        label = "warmup_discard_', self.source)

        node = next(item for item in self.tree.body
                    if isinstance(item, ast.FunctionDef) and item.name == "warmup_until_visible")
        isolated = ast.Module(body=[node], type_ignores=[])
        ast.fix_missing_locations(isolated)
        elapsed = {"seconds": 0.0}
        values = iter((0.0, 0.0, 8.0))
        labels = []

        def fake_capture(label, world, discarded=False):
            labels.append(label)
            elapsed["seconds"] += 0.2
            yield None
            return next(values)

        namespace = {"MAX_WARMUP_FRAMES": 20, "WARMUP_BRIGHTNESS_FLOOR": 5.0,
                     "plc": type("PLC", (), {"game_time": staticmethod(lambda _world: elapsed["seconds"])})(),
                     "wait_capture": fake_capture, "log": lambda _message: None,
                     "RuntimeError": RuntimeError}
        exec(compile(isolated, str(SCRIPT), "exec"), namespace)
        list(namespace["warmup_until_visible"]("world"))
        self.assertEqual(labels, ["warmup_discard_1", "warmup_discard_2", "warmup_discard_3"])

        elapsed["seconds"] = 0.0
        labels.clear()
        namespace["wait_capture"] = lambda label, world, discarded=False: fake_capture_black(label, world, labels, elapsed)

        def fake_capture_black(label, world, seen, clock):
            seen.append(label)
            clock["seconds"] += 0.21
            yield None
            return 0.0

        with self.assertRaisesRegex(RuntimeError, "brightness floor not reached"):
            list(namespace["warmup_until_visible"]("world"))
        self.assertEqual(len(labels), 20)


if __name__ == "__main__":
    unittest.main(verbosity=2)
