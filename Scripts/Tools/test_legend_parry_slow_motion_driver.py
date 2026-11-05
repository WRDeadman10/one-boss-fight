from __future__ import annotations

import ast
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


class LegendParrySlowMotionDriverTests(unittest.TestCase):
    def test_l8_uses_real_parry_contact_and_tracks_live_time_dilation(self) -> None:
        path = ROOT / "Scripts/Editor/pie_legend.py"
        source = path.read_text(encoding="utf-8")
        tree = ast.parse(source, filename=str(path))
        functions = {node.name for node in tree.body if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))}
        self.assertIn("l8_perfect_parry_slow_motion", functions)
        self.assertIn('parry = comp(p["pawn"], "RPGPlayerParry")', source)
        self.assertIn("parry.press()", source)
        self.assertIn('sweep.get_parried_count()', source)
        self.assertIn('dil_span(t_attack, time.perf_counter(), 2)', source)
        self.assertIn('("l8", l8_perfect_parry_slow_motion)', source)
        self.assertIn('console("rpg.Legend 0")', source)

    def test_l8_precedes_kill_and_guards_destroyed_boss_before_component_lookup(self) -> None:
        source = (ROOT / "Scripts/Editor/pie_legend.py").read_text(encoding="utf-8")
        tree = ast.parse(source)
        script = next(node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name == "script")
        groups_assignment = next(
            node.value for node in ast.walk(script)
            if isinstance(node, ast.Assign)
            and any(isinstance(target, ast.Name) and target.id == "groups" for target in node.targets)
        )
        group_names = [ast.literal_eval(item.elts[0]) for item in groups_assignment.elts]
        self.assertLess(group_names.index("l8"), group_names.index("l7"))

        l8 = next(node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name == "l8_perfect_parry_slow_motion")
        body_source = ast.get_source_segment(source, l8)
        self.assertIn('if p["boss"] is None:', body_source)
        self.assertIn('"boss not found; refusing to dereference a destroyed boss"', body_source)
        self.assertLess(body_source.index('if p["boss"] is None:'), body_source.index('comp(p["boss"], "RPGBossLowSweep")'))

    def test_runner_minimum_and_policy_cooldowns_expose_the_timing_constraint(self) -> None:
        run_drivers = (ROOT / "Scripts/RunDrivers.ps1").read_text(encoding="utf-8")
        pair = (ROOT / "Scripts/RunA5ParityPair.ps1").read_text(encoding="utf-8")
        parry_rules = (ROOT / "Source/OneBossFight/Player/RPGParryRules.h").read_text(encoding="utf-8")
        policy = (ROOT / "Source/OneBossFight/Player/RPGEncounterBinding.h").read_text(encoding="utf-8")
        self.assertIn("N = 'pie_legend';              K = 'R'; Min = 25; T = 900", run_drivers)
        self.assertIn("pie_legend = 25", pair)
        self.assertIn("DefaultCooldownSeconds=.7", parry_rules)
        self.assertIn("CooldownSeconds = 0.60f", policy)


if __name__ == "__main__":
    unittest.main()
