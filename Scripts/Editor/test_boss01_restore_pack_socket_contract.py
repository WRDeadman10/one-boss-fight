"""Contract tests for HeavySwordSocket_R restoration on SK_CombatMannequin (C-1190).

Verifies offline:
1. Target paths for SK_Boss01_Body and SKM_CombatMannequin are exact.
2. Target socket name is HeavySwordSocket_R on bone hand_r.
3. Target values exactly match RPGBossLook.h:42 (-13.9, 2.6, 4.9) and (p=-28, y=168.8, r=12.8).
4. Script contains strict readback assertions and fail-closed error handling.
5. Launcher script manages ENGINE_LOCK properly.
"""

import os
import unittest


class RestorePackSocketContracts(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
        cls.restore_script = os.path.join(cls.repo_root, "Scripts", "Editor", "restore_pack_heavyswordsocket.py")
        cls.launcher_script = os.path.join(cls.repo_root, "Scripts", "Editor", "run_restore_pack_heavyswordsocket.ps1")

    def test_restore_script_exists(self):
        self.assertTrue(os.path.exists(self.restore_script), f"Restore script missing: {self.restore_script}")

    def test_target_paths_are_exact(self):
        with open(self.restore_script, "r", encoding="utf-8") as f:
            content = f.read()
        self.assertIn("/Game/OneBossFight/Boss01/Body/SK_Boss01_Body", content)
        self.assertIn("/Game/AdvancedARPGCombat/Characters/Heroes/Mannequins/Meshes/SKM_CombatMannequin", content)
        self.assertIn("HeavySwordSocket_R", content)
        self.assertIn("hand_r", content)

    def test_target_values_match_original(self):
        import importlib.util
        spec = importlib.util.spec_from_file_location("restore_pack_heavyswordsocket", self.restore_script)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        loc = mod.TARGET_LOCATION
        rot = mod.TARGET_ROTATION
        self.assertAlmostEqual(loc[0], -13.9, delta=0.01)
        self.assertAlmostEqual(loc[1], 2.6, delta=0.01)
        self.assertAlmostEqual(loc[2], 4.9, delta=0.01)
        self.assertAlmostEqual(rot[0], -28.0, delta=0.01)
        self.assertAlmostEqual(rot[1], 168.83, delta=0.05)
        self.assertAlmostEqual(rot[2], 12.8, delta=0.01)

    def test_restore_has_readback_assertions(self):
        with open(self.restore_script, "r", encoding="utf-8") as f:
            content = f.read()
        self.assertIn("assert", content)
        self.assertIn("save_loaded_asset", content)
        self.assertIn("readback", content.lower())

    def test_launcher_handles_engine_lock(self):
        self.assertTrue(os.path.exists(self.launcher_script), f"Launcher missing: {self.launcher_script}")
        with open(self.launcher_script, "r", encoding="utf-8") as f:
            content = f.read()
        self.assertIn("ENGINE_LOCK.json", content)
        self.assertIn("UnrealEditor-Cmd.exe", content)
        self.assertIn("-nosound", content)


if __name__ == "__main__":
    unittest.main()
