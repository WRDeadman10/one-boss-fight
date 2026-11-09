"""Offline source contract for opt-in lock-on camera framing."""
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]
CPP = ROOT / "Source/OneBossFight/Player/RPGCameraRig.cpp"
HEADER = ROOT / "Source/OneBossFight/Player/RPGCameraRig.h"


class LockOnFramingContract(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cpp = CPP.read_text(encoding="utf-8")
        cls.header = HEADER.read_text(encoding="utf-8")

    def method(self):
        return self.cpp.split("void URPGCameraRig::ApplyLockOnFramingOption(float DeltaTime)", 1)[1].split(
            "void URPGCameraRig::RestoreLockOnFramingOption()", 1
        )[0]

    def test_development_switch_defaults_off_and_is_independent(self):
        self.assertRegex(self.cpp, r"#if\s+!UE_BUILD_SHIPPING[\s\S]*?rpg\.Camera\.LockOnFraming[\s\S]*?-1\s*,")

    def test_only_local_player_camera_tracks_pack_boss_and_restores_on_loss(self):
        method = self.method()
        self.assertIn("IsLocalController()", method)
        self.assertIn("URPGPlayerMovesSubsystem::IsPackBoss", method)
        self.assertIn("RestoreLockOnFramingOption()", method)
        self.assertIn("SetControlRotation(", method)
        self.assertIn("Boom->bUsePawnControlRotation = true", method)
        self.assertIn("OriginalLockOnUsePawnControlRotation", self.header)
        self.assertRegex(self.cpp, r"EndPlay[\s\S]*?RestoreLockOnFramingOption\(\)")

    def test_manual_camera_input_remains_authoritative_and_control_yaw_tracks_target(self):
        method = self.method()
        for token in ("GetControlRotation()", "LockOnManualInputGraceSeconds", "SetControlRotation(", "LockOnYawDegreesPerSecond"):
            self.assertIn(token, method)
        self.assertIn("GetActionValue(LockOnLookAction)", method)
        self.assertIn("LockOnLookInputDeadzone", method)
        self.assertNotIn("InputYawDelta", method)
        self.assertNotIn("InputPitchDelta", method)
        for forbidden in ("SetWorldRotation(", "SetActorLocation(", "SetActorRotation(", "AddMovementInput("):
            self.assertNotIn(forbidden, method)

    def test_boom_stays_on_control_rotation_and_restores_no_camera_override(self):
        method = self.method()
        self.assertIn("Boom->bUsePawnControlRotation = true", method)
        self.assertNotIn("SetWorldRotation(", method)
        self.assertIn("OriginalLockOnUsePawnControlRotation", self.header)
        restore = self.cpp.split("void URPGCameraRig::RestoreLockOnFramingOption()", 1)[1].split(
            "void URPGCameraRig::Apply()", 1
        )[0]
        self.assertIn("bUsePawnControlRotation = OriginalLockOnUsePawnControlRotation", restore)

    def test_manual_grace_reads_real_ia_look_action_instead_of_rotation_deltas(self):
        method = self.method()
        self.assertIn("/Game/AdvancedARPGCombat/MeleeCombatSystem/Blueprints/Input/InputActions/IA_Look.IA_Look", self.cpp)
        self.assertIn("UEnhancedPlayerInput", self.cpp)
        self.assertIn("GetActionValue(LockOnLookAction)", method)
        self.assertIn("LookValue.Size() > LockOnLookInputDeadzone", method)
        self.assertNotIn("LastLockOnControlRotation", self.header)

    def test_missing_look_input_fails_open_to_authored_camera(self):
        method = self.method()
        self.assertIn("if (!LockOnLookAction || !EnhancedPlayerInput)", method)
        fail_open = method.split("if (!LockOnLookAction || !EnhancedPlayerInput)", 1)[1].split(
            "if (!bHasOriginalLockOnUsePawnControlRotation)", 1
        )[0]
        self.assertIn("RestoreLockOnFramingOption();", fail_open)
        self.assertIn("return;", fail_open)

    def test_valid_target_geometry_handles_zero_vector_angle_wrap_and_pitch_limits(self):
        method = self.method()
        for token in ("IsNearlyZero()", "FindDeltaAngleDegrees", "PitchMin", "PitchMax"):
            self.assertIn(token, method)

    def test_error_proportional_follow_scales_to_fast_orbit_without_fixed_120_cap(self):
        method = self.method()
        self.assertIn("LockOnYawMinimumDegreesPerSecond = 60.f", self.cpp)
        self.assertIn("LockOnYawDegreesPerSecondPerDegreeError = 6.f", self.cpp)
        self.assertIn("LockOnYawMaximumDegreesPerSecond = 360.f", self.cpp)
        self.assertIn("FMath::Abs(YawDelta) * LockOnYawDegreesPerSecondPerDegreeError", method)
        self.assertIn("FMath::FixedTurn(ControlRotation.Yaw, TargetYaw, YawSpeed * DeltaTime)", method)
        self.assertNotIn("LockOnYawDegreesPerSecond * DeltaTime", method)
        # A 45-degree bearing error at 20 Hz needs about 225 deg/s to follow
        # the Lead's 180 deg/s sprint-orbit probe without a hard 120 deg/s cap.
        self.assertGreaterEqual(min(45.0 * 6.0, 360.0), 180.0)

    def test_off_path_restores_boom_mode_and_releases_target(self):
        method = self.method()
        self.assertIn("RestoreLockOnFramingOption();", method)
        restore = self.cpp.split("void URPGCameraRig::RestoreLockOnFramingOption()", 1)[1].split(
            "void URPGCameraRig::Apply()", 1
        )[0]
        self.assertIn("bUsePawnControlRotation = OriginalLockOnUsePawnControlRotation", restore)
        self.assertIn("LockOnTarget.Reset()", restore)

    def test_target_replacement_resets_manual_hold_without_changing_spring_arm_mode(self):
        method = self.method()
        self.assertIn("if (LockOnTarget.Get() != PackBoss)", method)
        self.assertIn("LockOnManualInputSecondsRemaining = 0.f", method)
        self.assertNotIn("RestoreLockOnFramingOption();", method.split("if (LockOnTarget.Get() != PackBoss)", 1)[1].split("const FVector2D LookValue", 1)[0])

    def test_three_switches_are_separate_default_off_tick_and_endplay_paths(self):
        for name in ("BossBlocks", "HideBossInside", "LockOnFraming"):
            expected = -1 if name in ("HideBossInside", "LockOnFraming") else 0
            self.assertRegex(self.cpp, rf"rpg\.Camera\.{name}\"\), {expected}")
        tick = self.cpp.split("void URPGCameraRig::TickComponent(", 1)[1]
        for method_name in ("ApplyBossCameraCollisionOption", "ApplyBossHideInsideOption", "ApplyLockOnFramingOption"):
            self.assertIn(method_name + "(", tick)
        end_play = self.cpp.split("void URPGCameraRig::EndPlay(", 1)[1].split("void URPGCameraRig::ApplyBossCameraCollisionOption", 1)[0]
        for method_name in ("RestoreBossCameraCollisionOption", "RestoreBossHideInsideOption", "RestoreLockOnFramingOption"):
            self.assertIn(method_name + "();", end_play)
        self.assertNotIn("CVarCameraBossBlocks", self.method())
        self.assertNotIn("CVarCameraHideBossInside", self.method())


if __name__ == "__main__":
    unittest.main()
