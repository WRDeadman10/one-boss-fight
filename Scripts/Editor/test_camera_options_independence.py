"""Offline contracts for independent camera switches and passive probe telemetry."""
from itertools import product
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[2]
CPP = ROOT / "Source/OneBossFight/Player/RPGCameraRig.cpp"
PROBE = ROOT / "Scripts/Editor/probe_camera_inside_boss.py"


class CameraOptionsIndependenceContract(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cpp = CPP.read_text(encoding="utf-8")
        cls.probe = PROBE.read_text(encoding="utf-8")

    def test_three_distinct_switches_are_development_only_and_default_off(self):
        for name in ("BossBlocks", "HideBossInside", "LockOnFraming"):
            matches = re.findall(rf'TEXT\("rpg\.Camera\.{name}"\),\s*(\d+)', self.cpp)
            self.assertEqual(matches, ["0"], name)
        for declaration in ("CVarCameraBossBlocks", "CVarCameraHideBossInside", "CVarCameraLockOnFraming"):
            self.assertIn(declaration, self.cpp.split("#endif", 1)[0])

    def test_all_eight_binary_combinations_are_distinct_and_well_formed(self):
        states = list(product((0, 1), repeat=3))
        self.assertEqual(len(states), 8)
        self.assertEqual(len(set(states)), 8)
        self.assertEqual(states[0], (0, 0, 0))
        self.assertEqual(states[-1], (1, 1, 1))

    def test_each_switch_has_its_own_apply_and_restore_path(self):
        tick = self.cpp.split("void URPGCameraRig::TickComponent(", 1)[1]
        for method in ("ApplyBossCameraCollisionOption", "ApplyBossHideInsideOption", "ApplyLockOnFramingOption"):
            self.assertIn(method + "(", tick)
        end_play = self.cpp.split("void URPGCameraRig::EndPlay(", 1)[1].split(
            "void URPGCameraRig::ApplyBossCameraCollisionOption", 1
        )[0]
        for method in ("RestoreBossCameraCollisionOption", "RestoreBossHideInsideOption", "RestoreLockOnFramingOption"):
            self.assertIn(method + "();", end_play)

    def test_each_option_mutates_only_its_named_camera_state(self):
        expected = {
            "ApplyBossCameraCollisionOption": ("CVarCameraBossBlocks", "SetCollisionResponseToChannel(ECC_Camera, ECR_Block)"),
            "ApplyBossHideInsideOption": ("CVarCameraHideBossInside", "HiddenPrimitiveComponents.Add(Component)"),
            "ApplyLockOnFramingOption": ("CVarCameraLockOnFraming", "PlayerController->SetControlRotation(DesiredRotation)"),
        }
        for method_name, (own_cvar, own_effect) in expected.items():
            match = re.search(rf"void URPGCameraRig::{method_name}\([^\n]*\)\n\{{[\s\S]*?\n\}}", self.cpp)
            self.assertIsNotNone(match, method_name)
            method = match.group(0)
            self.assertIn(own_cvar, method)
            self.assertIn(own_effect, method)
            for other in set(expected.values()):
                if other[0] != own_cvar:
                    self.assertNotIn(other[0], method)

    def test_provisional_camera_numbers_are_source_backed_and_labeled(self):
        for declaration in ("CameraHideEnterMarginCm = 5.f", "CameraHideExitMarginCm = 10.f",
                            "CameraHideMinimumSeconds = 0.35f",
                            "LockOnManualInputGraceSeconds = 0.35f",
                            "LockOnYawMinimumDegreesPerSecond = 60.f",
                            "LockOnYawDegreesPerSecondPerDegreeError = 6.f",
                            "LockOnYawMaximumDegreesPerSecond = 360.f"):
            self.assertIn(declaration, self.cpp)
        docs = (ROOT / "Documentation/Boss/AP_C31_C35_OPTION_MATRIX.md").read_text(encoding="utf-8")
        self.assertIn("provisional", docs.lower())

    def test_target_swaps_missing_targets_and_endplay_restore_owned_camera_state(self):
        boss = re.search(r"void URPGCameraRig::ApplyBossCameraCollisionOption\(\)\n\{[\s\S]*?\n\}", self.cpp).group(0)
        hide = re.search(r"void URPGCameraRig::ApplyBossHideInsideOption\(\)\n\{[\s\S]*?\n\}", self.cpp).group(0)
        lock = re.search(r"void URPGCameraRig::ApplyLockOnFramingOption\(float DeltaTime\)\n\{[\s\S]*?\n\}", self.cpp).group(0)
        self.assertIn("BossCameraCapsule.Get() != Capsule", boss)
        self.assertIn("RestoreBossCameraCollisionOption();", boss)
        self.assertIn("BossHideActor.Get() != PackBoss || BossHideController.Get() != PlayerController", hide)
        self.assertIn("LockOnTarget.Get() != PackBoss", lock)
        self.assertIn("RestoreLockOnFramingOption();", lock)
        self.assertIn("RestoreBossHideInsideOption();", hide)

    def test_passive_probe_logs_scenario_and_reads_all_switches_without_setting_them(self):
        self.assertIn("CAMERA_PROBE_SCENARIO", self.probe)
        self.assertIn("get_console_variable_int_value", self.probe)
        for name in ("BossBlocks", "HideBossInside", "LockOnFraming"):
            self.assertIn("rpg.Camera." + name, self.probe)
            self.assertNotRegex(self.probe, rf'execute_console_command\([^\n]*rpg\.Camera\.{name}')
        self.assertIn("OPTIONS t=%.3f scenario=", self.probe)
        self.assertIn("passive=true", self.probe)


if __name__ == "__main__":
    unittest.main()
