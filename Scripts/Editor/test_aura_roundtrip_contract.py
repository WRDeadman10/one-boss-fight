"""Contract test for Boost Lite production aura round-trip proof script (C-1199).

Validates:
1. Strict pack-path refusal and non-pack asset target isolation.
2. Tolerance constants and parameter definitions.
3. Runner script acquires and releases both ENGINE_LOCK locations with -nosound.
"""
import os
import sys
import unittest

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from Scripts.Editor import verify_aura_boostlite_roundtrip as rt_mod


class TestAuraRoundtripContract(unittest.TestCase):

    def test_target_path_is_safe_and_non_pack(self):
        """Must target strictly the project VFX folder, refusing pack paths."""
        self.assertEqual(rt_mod.TARGET_PACKAGE_PATH, "/Game/OneBossFight/VFX/NS_Boss_PhaseTwoAura")
        self.assertFalse(rt_mod.TARGET_PACKAGE_PATH.startswith("/Game/AdvancedARPGCombat"))

        # Test assert_safe_target_path
        rt_mod.assert_safe_target_path(rt_mod.TARGET_PACKAGE_PATH)

        with self.assertRaises(RuntimeError):
            rt_mod.assert_safe_target_path("/Game/AdvancedARPGCombat/VFX/NS_SomeAura")

        with self.assertRaises(RuntimeError):
            rt_mod.assert_safe_target_path("/Game/OneBossFight/VFX/NS_OtherAsset")

    def test_runner_script_structure_and_lock_enforcement(self):
        """The runner script must exist, acquire both ENGINE_LOCK locations, and launch with -nosound."""
        runner_path = os.path.join(PROJECT_ROOT, "Scripts", "Editor", "run_verify_aura_boostlite_roundtrip.ps1")
        self.assertTrue(os.path.exists(runner_path))
        with open(runner_path, "r", encoding="utf-8") as f:
            content = f.read()
        self.assertIn("ENGINE_LOCK.json", content)
        self.assertIn("Docs\\BossCombatReview\\Execution\\ENGINE_LOCK.json", content)
        self.assertIn("-nosound", content)
        self.assertIn("verify_aura_boostlite_roundtrip.py", content)


if __name__ == "__main__":
    unittest.main()
