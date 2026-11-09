"""Static contracts for the offline-safe Greatsword socket authoring script (C-1172, C-1173)."""
import ast
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]
AUTHOR_SCRIPT = ROOT / "Scripts/Editor/author_boss01_greatsword_sockets.py"
LAUNCHER_SCRIPT = ROOT / "Scripts/Editor/run_author_boss01_greatsword_sockets.ps1"


class Boss01GreatswordSocketsContracts(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.author_text = AUTHOR_SCRIPT.read_text(encoding="utf-8")
        cls.author_tree = ast.parse(cls.author_text)
        cls.launcher_text = LAUNCHER_SCRIPT.read_text(encoding="utf-8")

    def test_target_mesh_path_is_exact(self):
        self.assertIn('ASSET_PATH = "/Game/OneBossFight/Boss01/Weapons/SM_Boss01_Greatsword"', self.author_text)

    def test_socket_definitions_contain_grip_and_trace_points(self):
        self.assertIn('"grip"', self.author_text)
        self.assertIn('"BladeStart"', self.author_text)
        self.assertIn('"MiddleSocket"', self.author_text)
        self.assertIn('"BladeEnd"', self.author_text)
        self.assertIn('"Trace_0"', self.author_text)
        self.assertIn('"Trace_1"', self.author_text)
        self.assertIn('"Trace_2"', self.author_text)
        self.assertIn('"Weapon Start"', self.author_text)
        self.assertIn('"Weapon End"', self.author_text)

    def test_author_has_readback_assertions(self):
        self.assertIn("probe.get_all_socket_names()", self.author_text)
        self.assertIn("assert name in readback_names", self.author_text)
        self.assertIn("assert dx < 1e-2 and dy < 1e-2 and dz < 1e-2", self.author_text)

    def test_launcher_acquires_exclusive_lock_and_cleans_up(self):
        acquire = self.launcher_text.index("New-Item -Path $lockFile -ItemType File -ErrorAction Stop")
        launch = self.launcher_text.index("& $editor $project")
        cleanup = self.launcher_text.index("if ($lockAcquired -and (Test-Path $lockFile))")
        self.assertLess(acquire, launch)
        self.assertLess(launch, cleanup)
        self.assertIn('owner = "A"', self.launcher_text)
        self.assertIn("-nosound", self.launcher_text)


if __name__ == "__main__":
    unittest.main(verbosity=2)
