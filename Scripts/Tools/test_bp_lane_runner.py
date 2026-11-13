"""BP-46..47 (C, implementer; Queue BP batch 10): checks for run_bp_lane_tests (static plus in-process; no main/subprocess).

  1. Every test_bp_* suite file is listed in the runner (completeness), and every listed suite exists.
  2. run_suites() runs a suite in-process and reports pass/fail; BP_SMOKE_EXECUTE is forced off even if set.
  3. The runner is classified (ALLOWLIST) and statically proven like every other command.
The full-lane run is not executed from inside this test (it would recurse); run_bp_lane_tests.run_suites is called on
one small suite only. Paths touched: the Scripts/Tools source files (read only).
"""
import os
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import cli_static_contract  # noqa: E402
import run_bp_lane_tests as runner  # noqa: E402
import test_bp_cli_smoke as smoke  # noqa: E402


class LaneRunner(unittest.TestCase):
    def test_every_bp_suite_is_listed_and_exists(self):
        on_disk = {p.stem for p in HERE.glob("test_bp_*.py")}
        self.assertEqual(on_disk, set(runner.BP_SUITES))

    def test_runs_a_suite_in_process_with_execution_forced_off(self):
        saved = os.environ.get("BP_SMOKE_EXECUTE")
        os.environ["BP_SMOKE_EXECUTE"] = "1"
        try:
            rows = runner.run_suites(["test_bp_exit_codes"])
            self.assertNotIn("BP_SMOKE_EXECUTE", os.environ, "the runner must force tool execution off")
        finally:
            if saved is not None:
                os.environ["BP_SMOKE_EXECUTE"] = saved
        self.assertEqual(len(rows), 1)
        self.assertTrue(rows[0]["ok"], rows[0])
        self.assertGreater(rows[0]["tests"], 0)

    def test_x2315_unknown_only_values_fail_closed(self):
        with self.assertRaises(ValueError) as caught:
            runner.select_suites(["test_bp_no_such_suite"])
        self.assertIn("unknown suite(s): test_bp_no_such_suite", str(caught.exception))
        with self.assertRaises(ValueError):
            runner.select_suites(["test_bp_exit_codes", "typo_suite"])
        self.assertEqual(runner.select_suites([]), list(runner.BP_SUITES))
        self.assertEqual(runner.select_suites(["test_bp_exit_codes"]), ["test_bp_exit_codes"])

    def test_x2315_main_routes_selection_errors_to_parser_error(self):
        import ast
        main = next(n for n in ast.parse((HERE / "run_bp_lane_tests.py").read_text(encoding="utf-8")).body
                    if isinstance(n, ast.FunctionDef) and n.name == "main")
        handlers = [h for n in ast.walk(main) if isinstance(n, ast.Try) for h in n.handlers]
        self.assertTrue(any(getattr(h.type, "id", "") == "ValueError" and any(
            isinstance(c, ast.Call) and getattr(c.func, "attr", "") == "error" for c in ast.walk(h)) for h in handlers))
        self.assertIn("select_suites(args.only)", ast.unparse(main))

    def test_runner_is_classified_and_proven(self):
        self.assertIn("run_bp_lane_tests", smoke.ALLOWLIST)
        ok, reason = cli_static_contract.analyse(HERE / "run_bp_lane_tests.py")
        self.assertTrue(ok, reason)


if __name__ == "__main__":
    unittest.main()
