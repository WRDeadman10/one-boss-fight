import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


class W011DeadCodeSafetyTests(unittest.TestCase):
    def test_private_no_caller_helpers_are_removed(self):
        pack_h = (ROOT / "Source/OneBossFight/Pack/RPGPackTrace.h").read_text(encoding="utf-8")
        pack_cpp = (ROOT / "Source/OneBossFight/Pack/RPGPackTrace.cpp").read_text(encoding="utf-8")
        select_h = (ROOT / "Source/OneBossFight/UI/RPGBuildSelect.h").read_text(encoding="utf-8")
        select_cpp = (ROOT / "Source/OneBossFight/UI/RPGBuildSelect.cpp").read_text(encoding="utf-8")
        self.assertNotIn("RefreshPrevious", pack_h + pack_cpp)
        self.assertNotIn("URPGBuildSelect::Toggle", select_cpp)
        self.assertNotIn("void Toggle();", select_h)

    def test_public_native_apis_remain_until_external_callers_are_cleared(self):
        registry_h = (ROOT / "Source/OneBossFight/Player/RPGBossPreparationRegistry.h").read_text(encoding="utf-8")
        registry_cpp = (ROOT / "Source/OneBossFight/Player/RPGBossPreparationRegistry.cpp").read_text(encoding="utf-8")
        binding_h = (ROOT / "Source/OneBossFight/Player/RPGEncounterBinding.h").read_text(encoding="utf-8")
        binding_cpp = (ROOT / "Source/OneBossFight/Player/RPGEncounterBinding.cpp").read_text(encoding="utf-8")
        self.assertIn("GetQuarantineDiagnostics() const", registry_h)
        self.assertIn("FRPGBossPreparationRegistry::GetQuarantineDiagnostics() const", registry_cpp)
        self.assertIn("ResolveEncounter(const AActor& Requester) const", binding_h)
        self.assertIn("URPGCombatContextSubsystem::ResolveEncounter(const AActor& Requester) const", binding_cpp)


if __name__ == "__main__":
    unittest.main()
