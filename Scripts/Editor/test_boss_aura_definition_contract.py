"""C-1210 contracts for the typed per-boss phase-two aura selection."""
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]


class TestBossAuraDefinitionContract(unittest.TestCase):
    def test_typed_definition_and_runtime_config_carry_optional_aura(self):
        header = (ROOT / "Source/OneBossFight/Player/RPGEncounterBinding.h").read_text(encoding="utf-8")
        compiler = (ROOT / "Source/OneBossFight/Player/RPGEncounterBinding.cpp").read_text(encoding="utf-8")
        runtime = (ROOT / "Source/OneBossFight/Player/RPGPlayerMovesSubsystem.cpp").read_text(encoding="utf-8")
        self.assertIn("TSoftObjectPtr<UNiagaraSystem> PhaseTwoAuraEffect", header)
        self.assertGreaterEqual(header.count("TSoftObjectPtr<UNiagaraSystem> PhaseTwoAuraEffect"), 2)
        self.assertIn("Value->PhaseTwoAuraEffect = D.PhaseTwoAuraEffect", compiler)
        self.assertIn("if (!BossDefinition->PhaseTwoAuraEffect.IsNull())", runtime)
        self.assertIn("Presentation->PhaseTwoAuraEffect = BossDefinition->PhaseTwoAuraEffect", runtime)
        self.assertIn("ActiveSelectionDefinition->BossDefinition.LoadSynchronous()", runtime)

    def test_tier_two_component_default_uses_authored_candidate(self):
        source = (ROOT / "Source/OneBossFight/Boss/RPGTier2BossPresentation.cpp").read_text(encoding="utf-8")
        self.assertIn("/Game/OneBossFight/VFX/NS_Boss_PhaseTwoAura_BoostLite_Authored.NS_Boss_PhaseTwoAura_BoostLite_Authored", source)
        self.assertNotIn("/Game/OneBossFight/VFX/NS_Boss_PhaseTwoAura.NS_Boss_PhaseTwoAura", source)

    def test_selected_definition_overrides_are_manifested_and_refresh_selection(self):
        author = (ROOT / "Scripts/Editor/apply_c1210_ember_aura_definition.py").read_text(encoding="utf-8")
        validator = (ROOT / "Scripts/Tools/validate_encounter_manifest.py").read_text(encoding="utf-8")
        for path in ("BOSS_PATH", "SELECTION_PATH", "EFFECT_PATH", "encounter_manifest.json"):
            self.assertIn(path, author)
        self.assertIn('"phase_two_aura_effect"', author)
        self.assertIn('"PhaseTwoAuraEffect"', author)
        self.assertIn("stable_manifest_hash", author)
        self.assertIn('"phase_two_aura_effect"', validator)
        self.assertIn('"PhaseTwoAuraEffect" not in seen_fields', validator)
        self.assertIn("backup", author)


if __name__ == "__main__":
    unittest.main()
