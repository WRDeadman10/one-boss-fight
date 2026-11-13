import importlib.util
import math
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location(
    "pie_driver_support", ROOT / "Scripts" / "Editor" / "pie_driver_support.py")
SUPPORT = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(SUPPORT)


class FinalResultTests(unittest.TestCase):
    def test_emits_one_terminal_line_and_sanitizes_fields(self):
        lines = []
        result = SUPPORT.FinalResult(lines.append, "probe\nname")
        self.assertTrue(result.emit(True, "done", count=3))
        self.assertFalse(result.emit(False, "duplicate"))
        self.assertEqual(len(lines), 1)
        self.assertEqual(lines[0], "RESULT=PASS driver=probe name reason=done count=3")


class MappingReadinessTests(unittest.TestCase):
    def test_ready_immediately(self):
        gate = SUPPORT.MappingReadinessGate(1.0)
        self.assertEqual(gate.poll(0.01, lambda: True), "ready")

    def test_waits_then_becomes_ready(self):
        gate = SUPPORT.MappingReadinessGate(1.0)
        self.assertEqual(gate.poll(0.2, lambda: False), "waiting")
        self.assertEqual(gate.poll(0.2, lambda: True), "ready")

    def test_missing_mapping_times_out(self):
        gate = SUPPORT.MappingReadinessGate(0.3)
        self.assertEqual(gate.poll(0.2, lambda: False), "waiting")
        self.assertEqual(gate.poll(0.1, lambda: False), "timeout")

    def test_readiness_exception_and_invalid_delta_are_terminal(self):
        gate = SUPPORT.MappingReadinessGate(1.0)
        self.assertEqual(gate.poll(0.1, lambda: 1 / 0), "readiness_error")
        self.assertEqual(gate.poll(0.1, lambda: True), "already_finished")
        self.assertEqual(SUPPORT.MappingReadinessGate(1.0).poll(math.nan, lambda: False), "invalid_delta")

    def test_air_reach_waits_and_keeps_c1283_warmup_order(self):
        for filename, state_name, success_reason in (
                ("pie_er_air_reach.py", "STATE", "all reach cases recorded"),
                ("pie_er_air_hits.py", "S", "all control samples recorded"),
                ("pie_er_inputs.py", "state", "all input cases recorded")):
            source = (ROOT / "Scripts" / "Editor" / filename).read_text(encoding="utf-8")
            self.assertIn("MappingReadinessGate(5.0)", source)
            if filename != "pie_er_inputs.py":
                self.assertLess(source.index('== "mapping_ready"'), source.index('== "warmup"'))
                self.assertIn(state_name + '["elapsed"] > 12.0', source)
                self.assertIn(state_name + '["elapsed"] >= 1.2', source)
                self.assertIn(state_name + '["elapsed"] > 3.7', source)
                self.assertIn('FINAL_RESULT.emit(reason == "' + success_reason + '"', source)
            else:
                self.assertLess(source.index('== "mapping_ready"'), source.index('== "case"'))
                self.assertIn('FINAL_RESULT.emit(not bad and state.get("terminal_reason")', source)
                self.assertIn('"W0 warm-up R2 hold (not counted: draws the sword)"', source)

    def test_block_probe_gates_first_press_and_finishes_once(self):
        source = (ROOT / "Scripts" / "Editor" / "pie_er_block_probe.py").read_text(encoding="utf-8")
        self.assertIn("MappingReadinessGate(5.0)", source)
        self.assertLess(source.index('mapping_gate"].poll'), source.index('set_key_down(pc, "R", True)'))
        self.assertIn('FINAL_RESULT.emit(reason == "both guard input arms complete"', source)
        self.assertIn('finish("input mapping refused combat-toggle press")', source)

    def test_control_latency_gates_warmup_and_reports_one_terminal_result(self):
        source = (ROOT / "Scripts" / "Editor" / "pie_er_control_latency.py").read_text(encoding="utf-8")
        self.assertIn("MappingReadinessGate(5.0)", source)
        self.assertLess(source.index('== "mapping_ready"'), source.index('update(phase="warmup"'))
        self.assertIn('FINAL_RESULT.emit(reason == "all control samples recorded"', source)
        self.assertIn('finish("input mapping refused warmup release")', source)

    def test_a4_counter_gates_r2_and_emits_final_result_after_witness(self):
        source = (ROOT / "Scripts" / "Editor" / "pie_er_a4_guard_counter.py").read_text(encoding="utf-8")
        self.assertIn("MappingReadinessGate(5.0)", source)
        self.assertLess(source.index('mapping_gate"].poll'), source.index('key(pc, True)'))
        self.assertIn('FINAL_RESULT.emit(S["result"], reason', source)
        self.assertNotIn('raise RuntimeError("R2 input refused")', source)

    def test_full_fight_gates_before_draw_and_emits_boss_terminal_result(self):
        source = (ROOT / "Scripts" / "Editor" / "pie_full_fight.py").read_text(encoding="utf-8")
        self.assertIn("MappingReadinessGate(5.0)", source)
        self.assertLess(source.index('phase="mapping_ready"'), source.index('if S["phase"] == "draw"'))
        self.assertIn('FINAL_RESULT.emit(S["boss_dead"] and not S.get("input_error")', source)
        self.assertIn('S["input_error"] = message', source)

    def test_player_tags_probe_gates_dodge_and_reports_result(self):
        source = (ROOT / "Scripts" / "Editor" / "pie_player_tags.py").read_text(encoding="utf-8")
        self.assertIn("MappingReadinessGate(5.0)", source)
        self.assertIn('phase="mapping_ready"', source)
        self.assertIn('FINAL_RESULT.emit(reason == "probe complete"', source)
        self.assertIn('finish("input mapping refused release")', source)

    def test_jump_probe_gates_press_and_releases_on_terminal_path(self):
        source = (ROOT / "Scripts" / "Editor" / "pie_jump_probe.py").read_text(encoding="utf-8")
        self.assertIn("MappingReadinessGate(5.0)", source)
        self.assertIn('s["phase"] = "mapping_ready"', source)
        self.assertIn('FINAL_RESULT.emit(reason == "probe complete"', source)
        self.assertIn('finish("input mapping refused press")', source)
        self.assertIn('finish("input mapping refused release")', source)

    def test_remains_retry_gates_mapping_and_emits_terminal_result(self):
        source = (ROOT / "Scripts" / "Editor" / "pie_remains.py").read_text(encoding="utf-8")
        self.assertIn("MappingReadinessGate(5.0)", source)
        self.assertLess(source.index('phase"] == "retry_mapping"'), source.index('set_key_down(controller, "R", True)'))
        self.assertIn('FINAL_RESULT.emit(passed, reason', source)
        self.assertIn('finish("retry key press refused")', source)
        self.assertIn('finish("retry key release refused")', source)
        self.assertIn('finish("driver exception")', source)


if __name__ == "__main__":
    unittest.main()
