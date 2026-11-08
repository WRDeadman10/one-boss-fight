"""Offline source contract for the opt-in boss-camera collision switch."""
from pathlib import Path
import re
import unittest


ROOT = Path(__file__).resolve().parents[2]
CPP = ROOT / "Source/OneBossFight/Player/RPGCameraRig.cpp"
HEADER = ROOT / "Source/OneBossFight/Player/RPGCameraRig.h"


class BossCameraBlocksContract(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cpp = CPP.read_text(encoding="utf-8")
        cls.header = HEADER.read_text(encoding="utf-8")

    def test_development_cvar_is_named_and_defaults_off(self):
        self.assertRegex(self.cpp, r"#if\s+!UE_BUILD_SHIPPING[\s\S]*?rpg\.Camera\.BossBlocks[\s\S]*?\b0\s*,")

    def test_disabled_option_preserves_authored_capsule_response(self):
        self.assertIn("ApplyBossCameraCollisionOption", self.header)
        self.assertIn("OriginalBossCameraResponse", self.header)
        self.assertIn("GetCollisionResponseToChannel(ECC_Camera)", self.cpp)
        self.assertIn("SetCollisionResponseToChannel(ECC_Camera, OriginalBossCameraResponse)", self.cpp)

    def test_switch_finds_only_the_project_pack_boss_and_restores_on_target_change(self):
        self.assertIn("URPGPlayerMovesSubsystem::IsPackBoss", self.cpp)
        self.assertIn("RestoreBossCameraCollisionOption", self.cpp)
        self.assertRegex(self.cpp, r"TickComponent[\s\S]*?ApplyBossCameraCollisionOption\(\)")
        self.assertRegex(self.cpp, r"EndPlay[\s\S]*?RestoreBossCameraCollisionOption\(\)")

    def test_switch_does_not_modify_camera_or_capsule_when_disabled(self):
        method = self.cpp.split("void URPGCameraRig::ApplyBossCameraCollisionOption()", 1)[1].split(
            "void URPGCameraRig::RestoreBossCameraCollisionOption()", 1
        )[0]
        disabled = re.search(r"if\s*\(\s*!bEnabled\s*\)\s*\{(?P<body>[^}]+)\}", method)
        self.assertIsNotNone(disabled)
        self.assertIn("RestoreBossCameraCollisionOption();", disabled.group("body"))
        self.assertRegex(disabled.group("body"), r"return\s*;")
        self.assertLess(disabled.end(), method.index("TActorIterator<APawn>"))
        self.assertLess(disabled.end(), method.index("SetCollisionResponseToChannel"))
        self.assertIn("ECR_Block", method)

    def test_only_the_live_pack_boss_capsule_is_changed_and_logs_are_null_safe(self):
        method = self.cpp.split("void URPGCameraRig::ApplyBossCameraCollisionOption()", 1)[1].split(
            "void URPGCameraRig::RestoreBossCameraCollisionOption()", 1
        )[0]
        self.assertIn("Cast<ACharacter>(*It)", method)
        self.assertIn("PackBoss->GetCapsuleComponent()", method)
        self.assertIn("if (URPGPlayerMovesSubsystem::IsPackBoss(*It))", method)
        self.assertIn("if (AActor* BossOwner = Capsule->GetOwner())", method)

    def test_enabled_option_revalidates_target_instead_of_trusting_a_stale_live_cache(self):
        method = self.cpp.split("void URPGCameraRig::ApplyBossCameraCollisionOption()", 1)[1].split(
            "void URPGCameraRig::RestoreBossCameraCollisionOption()", 1
        )[0]
        search = method.index("TActorIterator<APawn>")
        cached = method.find("BossCameraCapsule.Get()")
        self.assertTrue(cached == -1 or search < cached)

    def test_application_writes_only_the_pack_capsule_and_restore_uses_the_saved_response(self):
        apply = self.cpp.split("void URPGCameraRig::ApplyBossCameraCollisionOption()", 1)[1].split(
            "void URPGCameraRig::RestoreBossCameraCollisionOption()", 1
        )[0]
        restore = self.cpp.split("void URPGCameraRig::RestoreBossCameraCollisionOption()", 1)[1].split(
            "void URPGCameraRig::Apply()", 1
        )[0]
        writes = re.findall(r"([A-Za-z_][A-Za-z0-9_]*)->SetCollisionResponseToChannel\(ECC_Camera,\s*([^\)]+)\)", apply)
        self.assertEqual(writes, [("Capsule", "ECR_Block")])
        self.assertIn("Capsule->GetCollisionResponseToChannel(ECC_Camera) == ECR_Block", restore)
        self.assertIn("Capsule->SetCollisionResponseToChannel(ECC_Camera, OriginalBossCameraResponse)", restore)


if __name__ == "__main__":
    unittest.main()
