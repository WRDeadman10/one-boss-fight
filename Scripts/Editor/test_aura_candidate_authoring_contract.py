"""Static contracts for the offline-safe Phase Two aura candidate authoring paths."""
import ast
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[2]
AUTHOR_BOOST = ROOT / "Scripts/Editor/create_phase_two_aura_boost.py"
LAUNCHER_BOOST = ROOT / "Scripts/Editor/run_create_phase_two_aura_boost.ps1"
AUTHOR_LITE = ROOT / "Scripts/Editor/create_phase_two_aura_boost_lite.py"
LAUNCHER_LITE = ROOT / "Scripts/Editor/run_create_phase_two_aura_boost_lite.ps1"


class AuraCandidateAuthoringContracts(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.author_text = AUTHOR_BOOST.read_text(encoding="utf-8")
        cls.author_tree = ast.parse(cls.author_text)
        cls.launcher_text = LAUNCHER_BOOST.read_text(encoding="utf-8")

        cls.author_lite_text = AUTHOR_LITE.read_text(encoding="utf-8")
        cls.author_lite_tree = ast.parse(cls.author_lite_text)
        cls.launcher_lite_text = LAUNCHER_LITE.read_text(encoding="utf-8")

    def test_candidate_uses_distinct_source_and_destination_and_refuses_replacement(self):
        self.assertIn('SOURCE_PATH = "/Game/OneBossFight/VFX/NS_Boss_PhaseTwoAura"', self.author_text)
        self.assertIn('DEST_NAME = "NS_Boss_PhaseTwoAura_Boost"', self.author_text)
        self.assertIn("if eal.does_asset_exist(DEST_PATH):", self.author_text)
        self.assertIn("Leaving intact.", self.author_text)
        self.assertIn("asset_tools.duplicate_asset(DEST_NAME, DEST_DIR, source_asset)", self.author_text)
        self.assertIn("eal.save_loaded_asset(boost_asset)", self.author_text)
        self.assertNotIn("delete_asset", self.author_text)
        self.assertNotIn("rename_asset", self.author_text)

    def test_existing_target_path_returns_before_any_duplicate_or_save(self):
        create = next(node for node in self.author_tree.body if isinstance(node, ast.FunctionDef) and node.name == "create_candidate")
        existing = next(node for node in create.body if isinstance(node, ast.If))
        called = {
            node.func.attr if isinstance(node.func, ast.Attribute) else node.func.id
            for node in ast.walk(existing) if isinstance(node, ast.Call)
        }
        self.assertIn("does_asset_exist", called)
        self.assertIn("load_asset", called)
        self.assertNotIn("duplicate_asset", called)
        self.assertNotIn("save_loaded_asset", called)
        self.assertTrue(any(isinstance(node, ast.Return) for node in ast.walk(existing)))

    def test_launcher_acquires_exclusive_lock_before_engine_and_cleans_only_owned_lock(self):
        acquire = self.launcher_text.index("New-Item -Path $lockFile -ItemType File -ErrorAction Stop")
        launch = self.launcher_text.index("& $editor $project")
        cleanup = self.launcher_text.index("if ($lockAcquired -and (Test-Path $lockFile))")
        self.assertLess(acquire, launch)
        self.assertLess(launch, cleanup)
        self.assertIn("$lockAcquired = $true", self.launcher_text)
        self.assertNotIn("Test-Path $lockFile) {\n    Write-Error", self.launcher_text)

    def test_boost_lite_has_refuse_if_exists_and_distinct_dest(self):
        self.assertIn('SOURCE_PATH = "/Game/OneBossFight/VFX/NS_Boss_PhaseTwoAura"', self.author_lite_text)
        self.assertIn('DEST_NAME = "NS_Boss_PhaseTwoAura_BoostLite"', self.author_lite_text)
        self.assertIn("if eal.does_asset_exist(DEST_PATH):", self.author_lite_text)
        self.assertIn("Leaving intact.", self.author_lite_text)
        self.assertIn("asset_tools.duplicate_asset(DEST_NAME, DEST_DIR, source_asset)", self.author_lite_text)
        self.assertNotIn("delete_asset", self.author_lite_text)

    def test_boost_lite_patches_and_asserts_halfway_values(self):
        # Asserts halfway spawn rates (70.0, 52.5)
        self.assertIn("70.0", self.author_lite_text)
        self.assertIn("52.5", self.author_lite_text)
        # Asserts halfway sprite sizes (10.0, 100.0)
        self.assertIn("10.0, 100.0", self.author_lite_text)
        # Asserts halfway user parameters (1.25, 20.0, 200.0, 60.0)
        self.assertIn("1.25", self.author_lite_text)
        self.assertIn("200.0", self.author_lite_text)
        # Asserts bounds [-175, 175]
        self.assertIn("-175.0", self.author_lite_text)
        self.assertIn("175.0", self.author_lite_text)

    def test_boost_lite_launcher_structure(self):
        acquire = self.launcher_lite_text.index("New-Item -Path $lockFile -ItemType File -ErrorAction Stop")
        launch = self.launcher_lite_text.index("& $editor $project")
        cleanup = self.launcher_lite_text.index("if ($lockAcquired -and (Test-Path $lockFile))")
        self.assertLess(acquire, launch)
        self.assertLess(launch, cleanup)
        self.assertIn("create_phase_two_aura_boost_lite.py", self.launcher_lite_text)


if __name__ == "__main__":
    unittest.main(verbosity=2)
