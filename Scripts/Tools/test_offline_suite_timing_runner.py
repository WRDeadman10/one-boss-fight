"""Contract checks for the offline suite's time-budget wrapper."""
from __future__ import annotations

import sys
import unittest
from contextlib import redirect_stderr, redirect_stdout
from io import StringIO
from pathlib import Path
from unittest.mock import patch

try:
    from Scripts.Tools import run_offline_suite_timed as runner
except ModuleNotFoundError:
    # Isolated discover adds Scripts/Tools to sys.path, but omits repo root.
    import run_offline_suite_timed as runner


ROOT = Path(__file__).resolve().parents[2]


class OfflineSuiteTimingRunnerTests(unittest.TestCase):
    def test_runner_uses_discovery_and_twenty_second_default(self):
        source = (ROOT / "Scripts/Tools/run_offline_suite_timed.py").read_text(encoding="utf-8")
        self.assertIn("DEFAULT_MAX_SECONDS = 20.0", source)
        self.assertIn('"discover", "-s", "Scripts/Tools"', source)
        self.assertIn("time.monotonic()", source)
        self.assertIn("elapsed >= args.max_seconds", source)
        self.assertIn("timeout=args.max_seconds", source)

    def test_timeout_is_bounded_and_returns_failure(self):
        out, err = StringIO(), StringIO()
        with patch.object(runner.sys, "argv", ["run_offline_suite_timed"]), \
             patch.object(runner.subprocess, "run", side_effect=runner.subprocess.TimeoutExpired("suite", 20.0)) as run, \
             redirect_stdout(out), redirect_stderr(err):
            result = runner.main()
        self.assertEqual(result, 2)
        self.assertEqual(run.call_args.kwargs["timeout"], 20.0)
        self.assertIn("OFFLINE_SUITE_TIMING FAIL", err.getvalue())

    def test_nonzero_suite_exit_is_preserved(self):
        out, err = StringIO(), StringIO()
        completed = runner.subprocess.CompletedProcess(args=["suite"], returncode=7)
        with patch.object(runner.sys, "argv", ["run_offline_suite_timed", "--max-seconds", "3"]), \
             patch.object(runner.subprocess, "run", return_value=completed) as run, \
             redirect_stdout(out), redirect_stderr(err):
            result = runner.main()
        self.assertEqual(result, 7)
        self.assertEqual(run.call_args.kwargs["timeout"], 3.0)
        self.assertNotIn("OFFLINE_SUITE_TIMING PASS", out.getvalue())

    def test_keyboard_interrupt_is_not_reported_as_success(self):
        out, err = StringIO(), StringIO()
        with patch.object(runner.sys, "argv", ["run_offline_suite_timed"]), \
             patch.object(runner.subprocess, "run", side_effect=KeyboardInterrupt), \
             redirect_stdout(out), redirect_stderr(err):
            with self.assertRaises(KeyboardInterrupt):
                runner.main()
        self.assertNotIn("OFFLINE_SUITE_TIMING PASS", out.getvalue())
        self.assertEqual(err.getvalue(), "")

    def test_child_output_is_inherited_and_success_is_reported_after_exit(self):
        out, err = StringIO(), StringIO()

        def emit_child_output(*args, **kwargs):
            print("child stdout")
            print("child stderr", file=sys.stderr)
            return runner.subprocess.CompletedProcess(args=args[0], returncode=0)

        with patch.object(runner.sys, "argv", ["run_offline_suite_timed", "--max-seconds", "3"]), \
             patch.object(runner.subprocess, "run", side_effect=emit_child_output), \
             redirect_stdout(out), redirect_stderr(err):
            result = runner.main()
        self.assertEqual(result, 0)
        self.assertIn("child stdout", out.getvalue())
        self.assertIn("child stderr", err.getvalue())
        self.assertIn("OFFLINE_SUITE_TIMING PASS", out.getvalue())


if __name__ == "__main__":
    unittest.main()
