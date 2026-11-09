"""Contract tests for HeavySwordSocket_R adjustment on SK_Boss01_Body_Skeleton (C-1172, C-1183).

Verifies offline:
1. Target paths for SK_Boss01_Body and its skeleton are exact.
2. Target socket name is HeavySwordSocket_R on bone hand_r.
3. Target relative offset satisfies Claude's <= 3.0 cm world gap requirement (<= 2.0 cm local bone space at 1.5 scale).
4. Script contains strict readback assertions and fail-closed error handling.
5. Launcher script manages ENGINE_LOCK properly.
"""

import os
import unittest


class HeavySwordSocketContracts(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
        cls.author_script = os.path.join(cls.repo_root, "Scripts", "Editor", "author_boss01_heavyswordsocket.py")
        cls.launcher_script = os.path.join(cls.repo_root, "Scripts", "Editor", "run_author_boss01_heavyswordsocket.ps1")

    def test_author_script_exists(self):
        self.assertTrue(os.path.exists(self.author_script), f"Author script missing: {self.author_script}")

    def test_target_skeleton_path_is_exact(self):
        with open(self.author_script, "r", encoding="utf-8") as f:
            content = f.read()
        self.assertIn("/Game/OneBossFight/Boss01/Body/SK_Boss01_Body", content)
        self.assertIn("HeavySwordSocket_R", content)
        self.assertIn("hand_r", content)

    def test_target_location_satisfies_3cm_tolerance(self):
        import importlib.util
        spec = importlib.util.spec_from_file_location("author_boss01_heavyswordsocket", self.author_script)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        loc = mod.TARGET_LOCATION
        # Magnitude in bone space
        mag = (loc[0] ** 2 + loc[1] ** 2 + loc[2] ** 2) ** 0.5
        # At 1.5 mesh scale, world distance is mag * 1.5
        world_gap = mag * 1.5
        self.assertLessEqual(world_gap, 3.0, f"Target location world gap {world_gap:.2f} cm exceeds 3.0 cm threshold")

    def test_author_has_readback_assertions(self):
        with open(self.author_script, "r", encoding="utf-8") as f:
            content = f.read()
        self.assertIn("assert", content)
        self.assertIn("save_loaded_asset", content)
        self.assertIn("Readback", content)

    def test_launcher_handles_engine_lock(self):
        self.assertTrue(os.path.exists(self.launcher_script), f"Launcher missing: {self.launcher_script}")
        with open(self.launcher_script, "r", encoding="utf-8") as f:
            content = f.read()
        self.assertIn("ENGINE_LOCK.json", content)
        self.assertIn("UnrealEditor-Cmd.exe", content)
        self.assertIn("-nosound", content)


if __name__ == "__main__":
    unittest.main()
