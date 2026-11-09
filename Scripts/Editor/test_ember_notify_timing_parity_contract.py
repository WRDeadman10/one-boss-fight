"""Offline contracts for the Lead-only Ember notify parity PIE driver."""
import importlib.util
import os
import sys
import tempfile
import types
import unittest

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
DRIVER_PATH = os.path.join(os.path.dirname(__file__), "pie_ember_notify_timing_parity.py")


class TestEmberNotifyTimingParityContract(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.previous_unreal = sys.modules.get("unreal")
        sys.modules["unreal"] = types.SimpleNamespace(
            log=lambda _message: None,
            register_slate_post_tick_callback=lambda _callback: None,
        )
        spec = importlib.util.spec_from_file_location("ember_notify_parity_under_test", DRIVER_PATH)
        cls.driver = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cls.driver)

    @classmethod
    def tearDownClass(cls):
        if cls.previous_unreal is None:
            sys.modules.pop("unreal", None)
        else:
            sys.modules["unreal"] = cls.previous_unreal

    def setUp(self):
        self.driver.S["rows"] = {}

    def test_native_attack_log_transitions_are_read(self):
        trial = ("timing", "off", "A3a")
        for line in (
            "LogRPGAttack: BP_ExampleGreatSwordBoss_C: attack A3a instance 4 begins (generation 1)",
            "LogRPGAttack: BP_ExampleGreatSwordBoss_C: attack A3a committed at 0.40 s, heading 90.0 deg",
            "LogRPGAttack: BP_ExampleGreatSwordBoss_C: attack A3a active window opens at 0.43 s",
            "LogRPGAttack: BP_ExampleGreatSwordBoss_C: attack A3a recovery from 0.61 s (heading lock released)",
            "LogRPGAttack: BP_ExampleGreatSwordBoss_C: attack A3a instance 4 ended (montage stopped) at 0.81 s, phase was Recovery, yaw drift after commit 0.0 deg",
        ):
            self.driver.parse_attack_line(line, trial)
        row = self.driver.S["rows"][("timing", "off", "A3a")]
        self.assertEqual(row["phases"], {"Committed": 0.40, "Active": 0.43,
                                         "Recovery": 0.61, "Complete": 0.81})
        self.assertTrue(row["natural_recovery_end"])

    def test_early_montage_stop_is_not_a_natural_recovery_end(self):
        line = ("LogRPGAttack: BP_ExampleGreatSwordBoss_C: attack A3b instance 2 "
                "ended (montage stopped) at 0.29 s, phase was Active, yaw drift after commit 0.0 deg")
        self.driver.parse_attack_line(line, ("timing", "on", "A3b"))
        row = self.driver.S["rows"][("timing", "on", "A3b")]
        self.assertTrue(row["ended"])
        self.assertFalse(row["natural_recovery_end"])
        self.assertEqual(row["phases"]["Complete"], 0.29)

    def test_driver_separates_timing_and_parry_arms_and_avoids_phase_polling(self):
        with open(DRIVER_PATH, encoding="utf-8") as source_file:
            source = source_file.read()
        self.assertIn('for arm in ("timing", "parry")', source)
        self.assertIn('if arm == "parry" and not parry_sent', source)
        self.assertIn('source=URPGPlayerParry.NotifyParried', source)
        self.assertIn('PARRY_PRESS_TARGET_SECONDS = {"A1": 0.27, "A3a": 0.42, "A3b": 0.10}', source)
        self.assertIn('encounter.is_dormant() or encounter.is_waking()', source)
        self.assertIn('yield from warmup_move(tracker, debug, pawn, boss)', source)
        self.assertLess(source.index('yield from warmup_move(tracker, debug, pawn, boss)'),
                        source.index('for arm, enabled, move in TASKS'))
        self.assertNotIn("tracker.get_phase_name()", source)
        self.assertNotIn("tracker.get_current_move()", source)

    def test_abslog_argument_handles_quoted_and_unquoted_paths(self):
        parse = self.driver.parse_abslog_argument
        self.assertEqual(parse('-unattended -abslog="C:\\Lead Run\\pie.log" -nosound'),
                         'C:\\Lead Run\\pie.log')
        self.assertEqual(parse('-abslog=C:\\Saved\\pie.log'), 'C:\\Saved\\pie.log')
        self.assertIsNone(parse('-unattended -nosound'))
        with tempfile.TemporaryDirectory() as folder:
            with self.assertRaisesRegex(RuntimeError, "-abslog is present"):
                self.driver.select_attack_log("-abslog= -nosound", folder)

    def test_log_selector_prefers_abslog_and_falls_back_only_when_absent(self):
        with tempfile.TemporaryDirectory() as folder:
            saved = os.path.join(folder, "Saved")
            logs = os.path.join(saved, "Logs")
            os.makedirs(logs)
            old_log = os.path.join(logs, "old.log")
            with open(old_log, "w", encoding="utf-8") as stream:
                stream.write("old")
            explicit = os.path.join(folder, "run-specific.log")
            with open(explicit, "w", encoding="utf-8") as stream:
                stream.write("current")
            self.assertEqual(str(self.driver.select_attack_log('-abslog="%s"' % explicit, saved)), explicit)
            self.assertEqual(str(self.driver.select_attack_log("-nosound", saved)), old_log)

    def test_selected_log_must_be_modified_after_pie_started(self):
        with tempfile.TemporaryDirectory() as folder:
            log_path = os.path.join(folder, "current.log")
            with open(log_path, "w", encoding="utf-8") as stream:
                stream.write("LogRPGAttack: fresh")
            self.driver.S["log_path"] = __import__("pathlib").Path(log_path)
            self.driver.S["pie_start_wall_time"] = os.path.getmtime(log_path) - 1
            self.assertTrue(self.driver.validate_attack_log_freshness())
            self.driver.S["pie_start_wall_time"] = os.path.getmtime(log_path) + 1
            self.assertFalse(self.driver.validate_attack_log_freshness())
            self.assertIn("predates PIE start", self.driver.S["log_error"])

    def test_confirmed_count_is_the_shared_notify_parried_counter(self):
        parry_cpp = os.path.join(PROJECT_ROOT, "Source", "OneBossFight", "Player", "RPGPlayerParry.cpp")
        parry_h = os.path.join(PROJECT_ROOT, "Source", "OneBossFight", "Player", "RPGPlayerParry.h")
        with open(parry_cpp, encoding="utf-8") as source_file:
            implementation = source_file.read()
        with open(parry_h, encoding="utf-8") as source_file:
            declaration = source_file.read()
        self.assertIn("bool URPGPlayerParry::NotifyParried(AActor* Actor, AActor* Boss", implementation)
        self.assertIn("++Parry->ParriedCount;", implementation)
        self.assertIn("int32 GetParriedCount() const { return ParriedCount; }", declaration)
        with open(DRIVER_PATH, encoding="utf-8") as source_file:
            self.assertIn("parry.get_parried_count()", source_file.read())


if __name__ == "__main__":
    unittest.main()
