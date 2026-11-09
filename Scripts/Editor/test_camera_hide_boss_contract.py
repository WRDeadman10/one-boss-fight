"""Offline source contracts for the opt-in local camera-inside-boss hide switch."""
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[2]
CPP = ROOT / "Source/OneBossFight/Player/RPGCameraRig.cpp"
HEADER = ROOT / "Source/OneBossFight/Player/RPGCameraRig.h"


class HideBossInsideContract(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cpp = CPP.read_text(encoding="utf-8")
        cls.header = HEADER.read_text(encoding="utf-8")

    def test_development_switch_defaults_off_and_is_independent(self):
        self.assertRegex(self.cpp, r"#if\s+!UE_BUILD_SHIPPING[\s\S]*?rpg\.Camera\.HideBossInside[\s\S]*?-1\s*,")

    def test_only_local_player_controller_hides_mesh_primitives(self):
        self.assertIn("HiddenPrimitiveComponents", self.cpp)
        self.assertIn("IsLocalController()", self.cpp)
        self.assertNotIn("SetActorHiddenInGame", self.cpp)
        self.assertNotIn("SetHiddenInGame", self.cpp)
        self.assertIn("Cast<USkeletalMeshComponent>(Component)", self.cpp)
        self.assertIn("Cast<UStaticMeshComponent>(Component)", self.cpp)

    def test_camera_uses_grown_capsule_with_separate_enter_exit_margins(self):
        self.assertIn("CameraHideEnterMarginCm", self.cpp)
        self.assertIn("CameraHideExitMarginCm", self.cpp)
        self.assertIn("GetScaledCapsuleSize", self.cpp)
        self.assertIn("IsPointWithinCameraCapsule", self.cpp)
        self.assertIn("bAlreadyHiddenByThisRig ? CameraHideExitMarginCm : -CameraHideEnterMarginCm", self.cpp)
        self.assertNotIn("Component->Bounds", self.cpp)

    def test_off_path_and_invalid_capsule_restore_without_hiding(self):
        self.assertIn("ApplyBossHideInsideOption", self.header)
        self.assertIn("RestoreBossHideInsideOption", self.header)
        method = self.cpp.split("void URPGCameraRig::ApplyBossHideInsideOption()", 1)[1].split(
            "void URPGCameraRig::RestoreBossHideInsideOption()", 1
        )[0]
        self.assertRegex(method, r"if\s*\(\s*!bEnabled\s*\)[\s\S]*?RestoreBossHideInsideOption\(\)[\s\S]*?return")
        self.assertIn("!BossCapsule || !BossCapsule->IsRegistered()", method)

    def test_switch_restores_only_components_it_added_on_disable_target_swap_and_endplay(self):
        self.assertIn("BossHideAddedComponents", self.header)
        self.assertRegex(self.cpp, r"EndPlay[\s\S]*?RestoreBossHideInsideOption\(\)")
        self.assertIn("BossHideActor.Get() != PackBoss || BossHideController.Get() != PlayerController", self.cpp)
        self.assertRegex(self.cpp, r"BossHideActor.Get\(\) != PackBoss[\s\S]*?RestoreBossHideInsideOption\(\)")
        method = self.cpp.split("void URPGCameraRig::RestoreBossHideInsideOption()", 1)[1].split(
            "void URPGCameraRig::Apply()", 1
        )[0]
        self.assertIn("RemoveSingle(Component)", method)
        self.assertIn("BossHideAddedComponents.Reset()", method)

    def test_transition_logs_are_gated_once_and_include_component_count_and_distance(self):
        apply = self.cpp.split("void URPGCameraRig::ApplyBossHideInsideOption()", 1)[1].split(
            "void URPGCameraRig::RestoreBossHideInsideOption()", 1
        )[0]
        restore = self.cpp.split("void URPGCameraRig::RestoreBossHideInsideOption()", 1)[1].split(
            "void URPGCameraRig::ApplyLockOnFramingOption", 1
        )[0]
        self.assertEqual(apply.count("HideBossInside enter"), 1)
        self.assertIn("if (!bBossHideActive)", apply)
        self.assertIn("meshes=%d camera_to_boss_cm=%.1f", apply)
        self.assertEqual(restore.count("HideBossInside exit_or_restore"), 1)
        self.assertIn("if (bBossHideActive)", restore)
        self.assertIn("meshes=%d camera_to_boss_cm=%.1f", restore)

    def test_capsule_enter_and_exit_geometry_uses_separate_margins(self):
        helper = self.cpp.split("bool IsPointWithinCameraCapsule(", 1)[1].split("\n\t}\n}", 1)[0]
        self.assertIn("Radius + MarginCm", helper)
        self.assertIn("ClosestPointOnSegment", helper)
        self.assertIn("? CameraHideExitMarginCm : -CameraHideEnterMarginCm", self.cpp)

    def test_minimum_hide_time_prevents_blinking_after_exit(self):
        self.assertIn("CameraHideMinimumSeconds", self.cpp)
        self.assertIn("BossHideStartedSeconds", self.header)
        method = self.cpp.split("void URPGCameraRig::ApplyBossHideInsideOption()", 1)[1].split(
            "void URPGCameraRig::RestoreBossHideInsideOption()", 1
        )[0]
        self.assertIn("bBossHideActive", method)
        self.assertIn("NowSeconds - BossHideStartedSeconds", method)

    def test_hide_option_does_not_touch_collision_or_gameplay_state(self):
        method = self.cpp.split("void URPGCameraRig::ApplyBossHideInsideOption()", 1)[1].split(
            "void URPGCameraRig::RestoreBossHideInsideOption()", 1
        )[0]
        for forbidden in ("SetCollision", "SetActorHiddenInGame", "SetHiddenInGame", "ApplyDamage", "GameplayStatics::Spawn"):
            self.assertNotIn(forbidden, method)
        self.assertIn("USkeletalMeshComponent", self.cpp)
        self.assertIn("UStaticMeshComponent", self.cpp)
        self.assertNotIn("Component->Bounds", method)

    def test_camera_switches_remain_independent_and_endplay_cleans_both(self):
        self.assertRegex(self.cpp, r"CVarCameraBossBlocks\(TEXT\(\"rpg\.Camera\.BossBlocks\"\), 0")
        self.assertRegex(self.cpp, r"CVarCameraHideBossInside\(TEXT\(\"rpg\.Camera\.HideBossInside\"\), -1")
        tick = self.cpp.split("void URPGCameraRig::TickComponent(", 1)[1]
        self.assertIn("ApplyBossCameraCollisionOption();", tick)
        self.assertIn("ApplyBossHideInsideOption();", tick)
        end_play = self.cpp.split("void URPGCameraRig::EndPlay(", 1)[1].split("void URPGCameraRig::ApplyBossCameraCollisionOption", 1)[0]
        self.assertIn("RestoreBossCameraCollisionOption();", end_play)
        self.assertIn("RestoreBossHideInsideOption();", end_play)


if __name__ == "__main__":
    unittest.main()
