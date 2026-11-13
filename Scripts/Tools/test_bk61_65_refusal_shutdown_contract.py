"""BK-61..65 (C, implementer; assigned by X-1990): offline contract for the deferred-refusal shutdown path.

Read-only: parses the BK-56..60 runner, the live driver and the retained Codex receipts. It never launches Unreal,
touches assets or locks, or edits evidence. The two expectedFailure cases are test-first for corrections proposed in
Documentation/Boss/BK_61_65_DEFERRED_SHUTDOWN_CRASH.md; they live in BK-56..60 files claimed by the lead (X-1984), so
this batch does not apply them. When the lead applies them, remove the decorators.
"""
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RUNNER = ROOT / "Scripts/Editor/run_bk56_60_deferred_selection.ps1"
DRIVER = ROOT / "Scripts/Editor/pie_sevarog_framework_live.py"
RECEIPTS = ROOT / "Docs/BossCombatReview/Execution/Codex/BK_56_60"


def text(path):
    return path.read_text(encoding="utf-8", errors="replace")


def refusal_branch(source):
    """The driver block that handles a refused deferred activation (from `if not ok:` after activate() to its return)."""
    start = source.index("activated = activate()")
    branch = source.index("if not ok:", start)
    end = source.index("return None", branch)
    return source[branch:end + len("return None")]


class RefusalShutdownContract(unittest.TestCase):
    def test_refusal_marker_carries_diagnostic_and_snapshot_before_returning(self):
        block = refusal_branch(text(DRIVER))
        self.assertIn("get_selection_diagnostic", block)
        self.assertIn("build_encounter_parity_snapshot", block)
        marker = block.index("DEFERRED_TICK_RESULT")
        self.assertLess(block.index("snapshot ="), marker, "snapshot must be captured before the marker is logged")
        self.assertIn("outcome=ActivationRefused", block)
        self.assertIn("test_start_calls=0 saves=0", block)

    def test_refusal_branch_leaves_shutdown_to_the_runner(self):
        # Current deliberate design (driver comment): no raise and no callback unregister inside the refused tick.
        block = refusal_branch(text(DRIVER))
        self.assertNotIn("finish(", block)
        self.assertNotIn("unregister_slate_post_tick_callback", block)
        self.assertNotIn("raise ", block)
        self.assertIn('STATE["done"] = True', block)

    def test_runner_stops_polling_on_result_or_error_marker(self):
        runner = text(RUNNER)
        self.assertIn("[SevarogLive] DEFERRED_TICK_RESULT", runner)
        self.assertRegex(runner, r"Fatal error\|Assertion failed\|\\\[SevarogLive\\\] ERROR")

    def test_runner_closes_then_kills_and_releases_only_its_own_locks(self):
        runner = text(RUNNER)
        self.assertIn("CloseMainWindow()", runner)
        self.assertRegex(runner, r"if \(!\$pieProc\.HasExited\) \{ \$pieProc\.Kill\(\); \$pieProc\.WaitForExit\(\) \}")
        self.assertIn("$current.owner_token -eq $token", runner)
        finally_block = runner[runner.rindex("finally {"):]
        self.assertIn("lock_result.txt", finally_block)

    def test_retained_receipts_log_the_marker_before_editor_exit(self):
        logs = sorted(RECEIPTS.glob("Run_*/deferred_pie.log"))
        self.assertTrue(logs, "no retained BK-56..60 deferred receipts found")
        for log in logs:
            body = text(log).replace("\x00", "")
            exit_at = body.find("LogExit: Preparing to exit.")
            if exit_at < 0:
                continue
            markers = [body.find(m) for m in ("DEFERRED_TICK_RESULT", "[SevarogLive] finished:") if body.find(m) >= 0]
            self.assertTrue(markers, "%s: no result/finished marker" % log.parent.name)
            self.assertLess(min(markers), exit_at, "%s: marker must precede editor exit" % log.parent.name)

    def test_crash_is_specific_to_refused_deferred_runs_in_retained_receipts(self):
        crashed, refused = [], []
        for log in sorted(RECEIPTS.glob("Run_*/deferred_pie.log")):
            body = text(log).replace("\x00", "")
            if "python311.dll" in body:
                crashed.append(log.parent.name)
            if re.search(r"activation refused|outcome=ActivationRefused", body):
                refused.append(log.parent.name)
        self.assertTrue(crashed)
        self.assertEqual(set(crashed) - set(refused), set(), "a crash outside a refused deferred run would change the diagnosis")

    def test_proposed_runner_records_pie_process_exit_code(self):
        # BK-62 F1: the PIE process exit code (crash = nonzero) is never written to a receipt.
        self.assertRegex(text(RUNNER), r"\$pieProc\.ExitCode")

    def test_proposed_runner_writes_failure_status_on_throw(self):
        # BK-62 F2: status.txt is written only after every check passes; a refused run leaves no machine-readable status.
        runner = text(RUNNER)
        self.assertRegex(runner, r"catch \{[^}]*status|failure_status\.txt")


if __name__ == "__main__":
    unittest.main()
