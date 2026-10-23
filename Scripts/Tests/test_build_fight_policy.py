import importlib.util
import json
import math
from pathlib import Path
import sys
import tempfile
import types
import unittest
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[2]
DRIVER = ROOT / "Scripts/Editor/pie_build_fight.py"


class BuildFightPolicyTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.saved = Path(self.directory.name)
        self.logs = []
        fake_unreal = types.ModuleType("unreal")
        fake_unreal.SystemLibrary = types.SimpleNamespace(get_project_directory=lambda: str(ROOT))
        fake_unreal.log = self.logs.append
        fake_unreal.register_slate_post_tick_callback = lambda callback: None
        spec = importlib.util.spec_from_file_location("build_fight_under_test", DRIVER)
        self.bot = importlib.util.module_from_spec(spec)
        with patch.dict(sys.modules, {"unreal": fake_unreal}):
            spec.loader.exec_module(self.bot)
        self.bot.SAVED = str(self.saved)
        self.bot.BUILD = "Strength"
        self.bot.S["event_t"] = 5.0
        self.observation = {
            "t": 10.0, "riposting": False, "dodging": False, "pl_st": 100.0,
            "move": "None", "phase": "None", "pos": 0.0, "inst": 1,
            "dist": 120.0, "rate": 1.0, "bm_untracked": False,
            "transition": False, "stag": False, "stage": "none", "stag_n": 0,
            "neutral": True, "pmontage": None, "falling": False, "home_dist": 0.0,
        }

    def test_missing_and_invalid_build_never_default_to_strength(self):
        self.assertEqual(self.bot.read_build()[0], "Invalid")
        (self.saved / "build_fight_build.txt").write_text("Banana", encoding="utf-8")
        self.assertEqual(self.bot.read_build()[0], "Invalid")
        (self.saved / "build_fight_build.txt").write_text("Starter Dex", encoding="utf-8")
        self.assertEqual(self.bot.read_build()[0], "Invalid")

    def test_each_build_round_trips_with_bom(self):
        for build in self.bot.BUILDS:
            with self.subTest(build=build):
                (self.saved / "build_fight_build.txt").write_text(build, encoding="utf-8-sig")
                self.assertEqual(self.bot.read_build()[0], build)

    def test_short_recovery_still_closes_distance(self):
        self.observation["dist"] = 350.0
        action = self.bot.plan_punish(self.observation, ("rec:A1b", ("rec", 1), 0.15))
        self.assertEqual(action[:2], ("move", (0.0, 1.0)))

    def test_long_recovery_prefers_strength_heavy(self):
        action = self.bot.plan_punish(self.observation, ("rec:A2", ("rec", 1), 1.0))
        self.assertEqual(action[:2], ("swing", "Strong"))

    def test_measured_heavy_delay_prevents_late_swing(self):
        self.bot.M["swing_delays"]["Strong"] = [0.65, 0.69, 0.71]
        action = self.bot.plan_punish(self.observation, ("rec:A1", ("rec", 1), 0.5))
        self.assertEqual(action[1], "Light")

    def test_low_stamina_reserves_dodge_instead_of_heavy(self):
        self.observation["pl_st"] = 40.0
        self.assertEqual(self.bot.decide(self.observation)[1], "Light")
        self.observation["pl_st"] = 30.0
        self.assertEqual(self.bot.decide(self.observation)[0], "wait")

    def test_neutral_pressure_and_no_retreat_at_strike_range(self):
        self.assertEqual(self.bot.decide(self.observation)[:2], ("swing", "Strong"))
        self.bot.S["event_t"] = 10.0
        self.assertEqual(self.bot.decide(self.observation)[0], "wait")

    def test_dodge_takes_priority_over_opening(self):
        self.observation.update(move="A1", phase="Windup", pos=0.01, neutral=False)
        self.assertEqual(self.bot.decide(self.observation)[0], "dodge")
        self.observation["dodging"] = True
        self.assertEqual(self.bot.decide(self.observation)[0], "wait")

    def test_active_swing_is_not_repressed_in_neutral(self):
        self.observation["pmontage"] = "Ability_E_Anim_Montage"
        self.assertEqual(self.bot.decide(self.observation)[0], "wait")

    def test_flank_direction_is_normalized_and_forward(self):
        sideways, forward = self.bot.FLANK
        self.assertAlmostEqual(math.hypot(sideways, forward), 1.0, places=3)
        self.assertGreater(forward, sideways)

    def test_timeout_is_inconclusive_and_archived_with_identity(self):
        self.bot.M.update(outcome="timeout", boss_hp0=500.0, boss_hp_last=450.0)
        self.bot.S["O"] = {"style": "ClaymoreCombatStyle"}
        self.bot.report()
        archives = list((self.saved / "BalanceRuns").glob("*.json"))
        self.assertEqual(len(archives), 1)
        record = json.loads(archives[0].read_text(encoding="utf-8"))
        self.assertEqual(record["build"], "Strength")
        self.assertEqual(record["actual_style"], "ClaymoreCombatStyle")
        self.assertIn("no victory", record["coverage_gaps"])
        self.assertIn("less than 40 percent boss health removed", record["coverage_gaps"])
        self.assertEqual(len(record["source_sha256"]), 64)

    def test_report_uses_accumulated_fight_time_after_teardown(self):
        self.bot.M.update(outcome="timeout", fight_t=8.5, t0=15.0, end_t=2.0, boss_hp0=500.0, boss_hp_last=450.0)
        self.bot.S["O"] = {"style": "ClaymoreCombatStyle"}
        self.bot.report()
        metrics = (self.saved / "build_fight_result_Strength.txt").read_text(encoding="utf-8")
        self.assertIn("fight_seconds = 8.5", metrics)


if __name__ == "__main__":
    unittest.main()
