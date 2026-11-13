"""Lead regression guard for the BK-81 encounter dependency-validation gap; no Unreal import."""
import ast
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
AUTHOR = ROOT / "Scripts/Editor/author_framework_encounter_definition.py"


class EncounterPrewriteGuardTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = AUTHOR.read_text(encoding="utf-8")
        cls.tree = ast.parse(cls.source)
        cls.functions = {node.name: node for node in cls.tree.body if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))}

    def test_write_branch_validates_boss_before_any_asset_creation(self):
        main = self.functions["main"]
        guard_calls = [n.lineno for n in ast.walk(main) if isinstance(n, ast.Call) and isinstance(n.func, ast.Name)
                       and n.func.id == "validate_boss_definition_for_write"]
        create_calls = [n.lineno for n in ast.walk(main) if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)
                        and n.func.attr == "create_asset"]
        self.assertEqual(len(guard_calls), 1)
        self.assertEqual(len(create_calls), 1)
        self.assertLess(guard_calls[0], create_calls[0])
        self.assertIn("if WRITE or READBACK", self.source)

    def test_guard_checks_stats_phase_identity_and_finite_ranges(self):
        guard = self.functions["validate_boss_definition_for_write"]
        source = ast.get_source_segment(self.source, guard)
        for token in ("max_health", "max_posture", "posture_regen_delay", "posture_regen_rate",
                      '== PHASE', "entry_health_fraction", "speed_multiplier", "rate_multiplier",
                      "attack_multiplier", "math.isfinite", "refusing encounter write"):
            self.assertIn(token, source)
        self.assertIn("len(matches) == 1", source)


if __name__ == "__main__":
    unittest.main()
