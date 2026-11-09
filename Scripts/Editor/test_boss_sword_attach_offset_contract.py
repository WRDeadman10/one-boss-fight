import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


class BossSwordAttachOffsetContract(unittest.TestCase):
    def test_optional_data_offset_defaults_to_identity_and_round_trips(self):
        binding = (ROOT / "Source/OneBossFight/Player/RPGEncounterBinding.h").read_text()
        look_header = (ROOT / "Source/OneBossFight/Player/RPGBossLook.h").read_text()
        adapters = (ROOT / "Source/OneBossFight/Player/RPGBossLookAdapters.cpp").read_text()
        tests = (ROOT / "Source/OneBossFight/Tests/RPGBossLookAdaptersTests.cpp").read_text()
        self.assertRegex(binding, r"FTransform\s+SwordAttachOffset\s*=\s*FTransform::Identity\b")
        self.assertRegex(look_header, r"FTransform\s+SwordAttachOffset\s*=\s*FTransform\(FRotator\(19\.84f,\s*-1\.84f,\s*-10\.48f\),\s*FVector::ZeroVector\)")
        self.assertRegex(look_header, r"FName\s+SwordSocket\s*=\s*TEXT\(\"hand_r\"\)")
        self.assertRegex(adapters, r"Look->SwordAttachOffset\s*=\s*Config\.Look\.SwordAttachOffset")
        self.assertIn("R.SwordAttachOffset = Look.SwordAttachOffset;", tests)
        self.assertIn("Look->SwordAttachOffset.Equals(FTransform(FRotator(19.84f, -1.84f, -10.48f), FVector::ZeroVector))", tests)

    def test_runtime_applies_offset_after_attachment_and_warns_on_bone_fallback(self):
        look = (ROOT / "Source/OneBossFight/Player/RPGBossLook.cpp").read_text()
        attach = look.index("SwordComponent->AttachToComponent")
        apply_offset = look.index("SwordComponent->SetRelativeTransform(SwordAttachOffset)")
        self.assertLess(attach, apply_offset)
        fallback = look[look.index("if (!BodyComponent->DoesSocketExist(AttachName))"):attach]
        self.assertIn("hand_r", fallback)
        self.assertIn("HeavySwordSocket_R", fallback)
        self.assertIn("Warning", fallback)

    def test_explicit_ember_config_uses_hand_and_tuned_offset(self):
        tests = (ROOT / "Source/OneBossFight/Tests/RPGBossLookAdaptersTests.cpp").read_text()
        self.assertIn("R.SwordSocket = TEXT(\"hand_r\")", tests)
        self.assertIn("FTransform(FRotator(19.84f, -1.84f, -10.48f), FVector::ZeroVector)", tests)


if __name__ == "__main__":
    unittest.main()
