import os
import unittest


class TestAuthorEmberMoveTimingContract(unittest.TestCase):
    def setUp(self):
        self.project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
        self.script_path = os.path.join(self.project_root, "Scripts", "Editor", "author_ember_move_timing.py")

    def test_script_exists(self):
        self.assertTrue(os.path.exists(self.script_path), f"Script missing: {self.script_path}")

    def test_refusal_rules_and_target_boundaries(self):
        with open(self.script_path, "r", encoding="utf-8") as f:
            code = f.read()

        # Must refuse AdvancedARPGCombat fail-closed
        self.assertIn('FORBIDDEN_ROOT = "/Game/AdvancedARPGCombat"', code)
        self.assertIn("validate_target_safety", code)
        self.assertIn("REFUSAL", code)

        # Must strictly target OneBossFight/Boss01/Animations
        self.assertIn('DEST_ROOT = "/Game/OneBossFight/Boss01/Animations"', code)
        self.assertIn("AM_Boss01_A1", code)
        self.assertIn("AM_Boss01_A3a", code)
        self.assertIn("AM_Boss01_A3b", code)

    def test_corrected_timing_coordinates(self):
        with open(self.script_path, "r", encoding="utf-8") as f:
            code = f.read()

        # A3b BranchRange must be 400.0 per C-1231
        self.assertIn('"branch_range": 400.0', code)
        # Check Commit values
        self.assertIn('"commit_time": 0.330', code)
        self.assertIn('"commit_time": 0.380', code)
        self.assertIn('"commit_time": 0.130', code)
        # Check Window values
        self.assertIn('"window_start_time": 0.350', code)
        self.assertIn('"window_end_time": 0.500', code)
        self.assertIn('"window_start_time": 0.400', code)
        self.assertIn('"window_end_time": 0.600', code)
        self.assertIn('"window_start_time": 0.150', code)
        self.assertIn('"window_end_time": 0.400', code)

    def test_static_class_resolution_and_nonzero_exit(self):
        with open(self.script_path, "r", encoding="utf-8") as f:
            code = f.read()

        # Must use static_class() per C-1232
        self.assertIn("static_class()", code)
        self.assertIn("resolve_timing_class", code)

        # Must exit non-zero on failure
        self.assertIn("sys.exit(1)", code)

    def test_pre_mutation_safety_and_preservation(self):
        with open(self.script_path, "r", encoding="utf-8") as f:
            code = f.read()

        # Codex X-1744 catch: pre-mutation check on dedicated track
        self.assertIn("Pre-existing track", code)
        self.assertIn("contains unrelated notify", code)
        self.assertIn("REFUSAL", code)

        # Preservation checks
        self.assertIn("non_timing_pre", code)
        self.assertIn("non_timing_post", code)
        self.assertIn("READBACK", code)


if __name__ == "__main__":
    unittest.main()
