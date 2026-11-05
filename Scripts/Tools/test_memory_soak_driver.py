from __future__ import annotations

import ast
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
DRIVER = ROOT / "Scripts" / "Editor" / "pie_memory_soak.py"


class MemorySoakDriverTests(unittest.TestCase):
    def test_driver_parses_as_python_without_importing_unreal(self):
        source = DRIVER.read_text(encoding="utf-8")
        ast.parse(source, filename=str(DRIVER))

    def test_driver_requires_fifty_resets_and_collects_before_samples(self):
        source = DRIVER.read_text(encoding="utf-8")
        for token in (
            "CYCLES = 50", 'execute_console_command(game_world, "obj gc")',
            "gc_before_sample_completed", "H019_ENCOUNTER_DEFINITION", "reset_for_test()",
            "GetProcessMemoryInfo", "WorkingSetSize", "PrivateUsage",
            "get_all_actors_of_class", "generation/count", "resets=%d/%d",
        ):
            with self.subTest(token=token):
                self.assertIn(token, source)


if __name__ == "__main__":
    unittest.main()
