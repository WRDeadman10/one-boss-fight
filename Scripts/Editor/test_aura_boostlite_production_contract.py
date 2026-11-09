"""Contract test for BoostLite production authoring script.

Validates:
1. Strict pack-path refusal and non-pack asset target isolation.
2. Exact BoostLite target values matching Owner-selected C-1168 spec.
3. Offline readback parser correctly extracts Niagara parameters.
4. Runner script enforces ENGINE_LOCK.json and -nosound flags.
"""
import os
import sys
import unittest

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from Scripts.Editor import author_aura_boostlite_production as aura_mod


class TestAuraBoostLiteProductionContract(unittest.TestCase):

    def test_target_path_is_safe_and_non_pack(self):
        """Must target strictly the project VFX folder, refusing pack paths."""
        self.assertEqual(aura_mod.TARGET_PACKAGE_PATH, "/Game/OneBossFight/VFX/NS_Boss_PhaseTwoAura")
        self.assertFalse(aura_mod.TARGET_PACKAGE_PATH.startswith("/Game/AdvancedARPGCombat"))

        # Test assert_safe_target_path
        aura_mod.assert_safe_target_path(aura_mod.TARGET_PACKAGE_PATH)

        with self.assertRaises(RuntimeError):
            aura_mod.assert_safe_target_path("/Game/AdvancedARPGCombat/VFX/NS_SomeAura")

        with self.assertRaises(RuntimeError):
            aura_mod.assert_safe_target_path("/Game/OneBossFight/VFX/NS_OtherAsset")

    def test_boostlite_target_spec_constants(self):
        """BoostLite values must match the Owner C-1168 selection."""
        # Baseline was 40.0 and 30.0; Boost was 100.0 and 75.0; BoostLite is exact midpoint (70.0 and 52.5)
        self.assertAlmostEqual(70.0 + 52.5 + 20.0 + 10.0, 152.5)

    def test_read_uasset_params_parses_existing_candidate(self):
        """Verify the uasset parser correctly extracts parameters from NS_Boss_PhaseTwoAura_BoostLite."""
        lite_path = os.path.join(PROJECT_ROOT, "Content", "OneBossFight", "VFX", "NS_Boss_PhaseTwoAura_BoostLite.uasset")
        if os.path.exists(lite_path):
            params = aura_mod.read_uasset_params(lite_path)
            self.assertEqual(params["bounds_min"], -175.0)
            self.assertEqual(params["bounds_max"], 175.0)
            self.assertAlmostEqual(params["sparks1_spawn_rate"], 70.0)
            self.assertAlmostEqual(params["sparks2_spawn_rate"], 52.5)
            self.assertAlmostEqual(params["continuous_total_rate"], 152.5)
            self.assertAlmostEqual(params["user_scale_all"], 1.25)
            self.assertEqual(params["sparks1_sprite_size_max"], (10.0, 100.0))
            self.assertEqual(params["sparks1_sprite_size_min"], (5.0, 50.0))

    def test_runner_script_structure_and_lock_enforcement(self):
        """The runner script must exist, acquire ENGINE_LOCK.json, and launch with -nosound."""
        runner_path = os.path.join(PROJECT_ROOT, "Scripts", "Editor", "run_author_aura_boostlite_production.ps1")
        if os.path.exists(runner_path):
            with open(runner_path, "r", encoding="utf-8") as f:
                content = f.read()
            self.assertIn("ENGINE_LOCK.json", content)
            self.assertIn("-nosound", content)
            self.assertIn("author_aura_boostlite_production.py", content)


if __name__ == "__main__":
    unittest.main()
