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
        self.driver.S["clean_rows"] = {}
        self.driver.S["hitch_retries"] = []
        self.driver.S["hitch_exhausted"] = []
        self.driver.S["checks"] = []
        self.driver.S["current_trial"] = None
        self.driver.S["result_emitted"] = False

    def test_native_attack_log_transitions_are_read(self):
        trial = ("timing", "off", "A3a", 1)
        for line in (
            "LogRPGAttack: BP_ExampleGreatSwordBoss_C: attack A3a instance 4 begins (generation 1)",
            "LogRPGAttack: BP_ExampleGreatSwordBoss_C: attack A3a committed at 0.40 s, heading 90.0 deg",
            "LogRPGAttack: BP_ExampleGreatSwordBoss_C: attack A3a active window opens at 0.43 s",
            "LogRPGAttack: BP_ExampleGreatSwordBoss_C: attack A3a recovery from 0.61 s (heading lock released)",
            "LogRPGAttack: BP_ExampleGreatSwordBoss_C: attack A3a instance 4 ended (montage stopped) at 0.81 s, phase was Recovery, yaw drift after commit 0.0 deg",
        ):
            self.driver.parse_attack_line(line, trial)
        row = self.driver.S["rows"][("timing", "off", "A3a", 1)]
        self.assertEqual(row["phases"], {"Committed": 0.40, "Active": 0.43,
                                         "Recovery": 0.61, "Complete": 0.81})
        self.assertTrue(row["natural_recovery_end"])

    def test_early_montage_stop_is_not_a_natural_recovery_end(self):
        line = ("LogRPGAttack: BP_ExampleGreatSwordBoss_C: attack A3b instance 2 "
                "ended (montage stopped) at 0.29 s, phase was Active, yaw drift after commit 0.0 deg")
        self.driver.parse_attack_line(line, ("timing", "on", "A3b", 1))
        row = self.driver.S["rows"][("timing", "on", "A3b", 1)]
        self.assertTrue(row["ended"])
        self.assertFalse(row["natural_recovery_end"])
        self.assertEqual(row["phases"]["Complete"], 0.29)

    def test_a3a_pack_chain_stop_in_active_is_accepted_as_terminal(self):
        line = ("LogRPGAttack: BP_ExampleGreatSwordBoss_C: attack A3a instance 8 "
                "ended (montage stopped) at 0.54 s, phase was Active, yaw drift after commit 0.0 deg")
        self.driver.parse_attack_line(line, ("timing", "off", "A3a", 1))
        row = self.driver.S["rows"][("timing", "off", "A3a", 1)]
        self.assertEqual(row["end_reason"], "montage stopped")
        self.assertEqual(row["end_phase"], "Active")
        self.assertFalse(row["natural_recovery_end"])

    def test_terminal_comparison_requires_matching_end_reason(self):
        evaluate = self.driver.evaluate_terminal_parity
        off = {"ended": True, "end_reason": "montage stopped", "phases": {"Complete": 0.54}}
        on = {"ended": True, "end_reason": "montage stopped", "phases": {"Complete": 0.58}}
        self.assertEqual(evaluate("A3a", off, on)[0], "PASS")
        on["phases"]["Complete"] = 0.70
        self.assertEqual(evaluate("A3a", off, on)[0], "FAIL")
        on["end_reason"] = "interrupted"
        self.assertEqual(evaluate("A3a", off, on)[0], "INFO")
        on["end_reason"] = None
        self.assertEqual(evaluate("A3a", off, on)[0], "INFO")

    def test_tick_over_limit_marks_trial_hitch_and_exact_limit_is_clean(self):
        self.driver.S["current_trial"] = {"enabled": False, "label": "off", "move": "A1", "attempt": 1}
        self.driver.note_trial_tick(0.1)
        row = self.driver.S["rows"][("timing", "off", "A1", 1)]
        self.assertFalse(row["hitch"])
        self.driver.note_trial_tick(0.100001)
        self.assertTrue(row["hitch"])
        self.assertAlmostEqual(row["max_tick_delta"], 0.100001)

    def test_hitch_retry_limit_and_result_receipt_are_explicit(self):
        self.assertEqual(self.driver.MAX_HITCH_RETRIES, 3)
        with open(DRIVER_PATH, encoding="utf-8") as source_file:
            source = source_file.read()
        self.assertIn("range(1, MAX_HITCH_RETRIES + 2)", source)
        self.assertIn('"RESULT %s clean_trials=%d/6 hitch_retries=%d retry_log=%s', source)
        self.assertIn('"TRIAL_TICK mode=%s move=%s attempt=%d delta=%.6f"', source)
        self.assertIn('outcome=%s max_delta=%.6f', source)

    def test_result_counts_only_selected_clean_trials_and_lists_retries(self):
        messages = []
        old_log = self.driver.unreal.log
        self.driver.unreal.log = messages.append
        try:
            self.driver.S["clean_rows"] = {("off", "A1"): {"clean": True}}
            self.driver.S["rows"] = {("timing", "on", "A1", 1): {"hitch": True}}
            self.driver.S["hitch_retries"] = [{"mode": "on", "move": "A1", "retry_attempt": 2}]
            self.driver.S["checks"] = [True]
            self.driver.emit_result()
        finally:
            self.driver.unreal.log = old_log
        result = next(message for message in messages if "RESULT " in message)
        self.assertIn("clean_trials=1/6 hitch_retries=1", result)
        self.assertIn('retry_log=[{"mode":"on","move":"A1","retry_attempt":2}]', result)

    def test_hitched_attempt_is_repeated_and_clean_attempt_is_selected(self):
        calls = []

        def fake_attempt(enabled, move, attempt, _tracker, _debug, _pawn, _boss):
            calls.append(attempt)
            row = {"hitch": attempt == 1, "max_tick_delta": 0.25 if attempt == 1 else 0.02,
                   "started": True, "ended": True, "clean": attempt > 1,
                   "timing_flag_ok": True, "completion_ok": True, "phases": {},
                   "natural_recovery_end": True}
            if False:
                yield 0.0
            return row, enabled

        original = self.driver.run_attempt
        self.driver.run_attempt = fake_attempt
        try:
            task = self.driver.run_one(False, "A1", None, None, None, None)
            self.assertEqual(next(task), 0.35)
            with self.assertRaises(StopIteration):
                next(task)
        finally:
            self.driver.run_attempt = original
        self.assertEqual(calls, [1, 2])
        self.assertEqual(self.driver.S["clean_rows"][("off", "A1")]["max_tick_delta"], 0.02)
        self.assertEqual(self.driver.S["hitch_retries"][0]["retry_attempt"], 2)

    def test_hitch_retries_stop_after_three_repeats(self):
        calls = []

        def always_hitch(enabled, move, attempt, _tracker, _debug, _pawn, _boss):
            calls.append(attempt)
            row = {"hitch": True, "max_tick_delta": 0.2, "started": True, "ended": True,
                   "clean": False, "phases": {}}
            if False:
                yield 0.0
            return row, enabled

        original = self.driver.run_attempt
        self.driver.run_attempt = always_hitch
        try:
            list(self.driver.run_one(False, "A1", None, None, None, None))
        finally:
            self.driver.run_attempt = original
        self.assertEqual(calls, [1, 2, 3, 4])
        self.assertEqual(len(self.driver.S["hitch_retries"]), 3)
        self.assertEqual(len(self.driver.S["hitch_exhausted"]), 1)
        self.assertIsNone(self.driver.S["clean_rows"][("off", "A1")])
        self.assertFalse(self.driver.S["checks"][-1])

    def test_driver_is_timing_only_and_avoids_phase_polling(self):
        with open(DRIVER_PATH, encoding="utf-8") as source_file:
            source = source_file.read()
        self.assertIn('TASKS = [(enabled, move) for enabled in (False, True) for move in MOVES]', source)
        self.assertIn('for enabled, move in TASKS', source)
        self.assertNotIn('"parry"', source)
        self.assertNotIn("parry.press()", source)
        self.assertNotIn("get_parried_count", source)
        self.assertNotIn("URPGPlayerParry", source)
        self.assertIn("evaluate_terminal_parity(move, off, on)", source)
        self.assertIn('encounter.is_dormant() or encounter.is_waking()', source)
        self.assertIn('yield from warmup_move(tracker, debug, pawn, boss)', source)
        self.assertLess(source.index('yield from warmup_move(tracker, debug, pawn, boss)'),
                        source.index('for enabled, move in TASKS'))
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

if __name__ == "__main__":
    unittest.main()
