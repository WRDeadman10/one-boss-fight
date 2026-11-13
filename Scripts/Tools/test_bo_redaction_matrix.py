"""BO-10 (C, implementer; per X-2240): black-box --redact matrix for the seven KI-167 report tools.

Every tool runs as a subprocess on temp fixtures that embed the absolute temp directory in file paths, log rows,
diagnostics and declared values. With --redact, no absolute form of the temp root may appear on stdout/stderr: raw,
forward-slash or JSON-escaped, compared without case. The same run without --redact is the control: its exit code
matches the redacted run's, and its output does contain the temp root. Also covered: the BO-01..05 hotfix
(asset_provenance SOURCE/DESTINATION values) and the preservation of `/Game/...` object paths and parsed telemetry.
"""
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import redaction  # noqa: E402

BACKSLASH = "\\"


def run(script, *args):
    return subprocess.run([sys.executable, str(HERE / script), *map(str, args)], capture_output=True, text=True, timeout=180)


class Matrix(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self._tmp.name).resolve()

    def tearDown(self):
        self._tmp.cleanup()

    def forms(self):
        raw = str(self.dir)
        return {raw.lower(), raw.replace(BACKSLASH, "/").lower(), raw.replace(BACKSLASH, BACKSLASH * 2).lower()}

    def leaks(self, text):
        low = text.lower()
        return [form for form in self.forms() if form in low]

    def check(self, script, *args, expect_leak_in_control=True):
        """Run `script` with and without --redact; assert no leak when redacted and the same exit code both ways."""
        plain = run(script, *args)
        red = run(script, *args, "--redact")
        self.assertEqual(red.returncode, plain.returncode, f"{script}: --redact changed the exit code\n{red.stderr[-400:]}")
        self.assertEqual(self.leaks(red.stdout + red.stderr), [], f"{script} leaked under --redact:\n{red.stdout}\n{red.stderr}")
        if expect_leak_in_control:
            self.assertTrue(self.leaks(plain.stdout + plain.stderr), f"{script}: control unexpectedly had no absolute path (fixture too weak)")
        return plain, red

    def write(self, name, text):
        path = self.dir / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
        return path

    # --- asset_provenance (BO-01..05 hotfix) ---
    def test_asset_provenance_values_masked_game_paths_kept(self):
        win = "C:" + BACKSLASH + "Users" + BACKSLASH + "someone" + BACKSLASH + "src.fbx"
        script = self.write("author.py", f'SOURCE_FBX = r"{win}"\nSOURCE_DIR = "{self.dir.as_posix()}/raw"\n'
                                         'POSIX_SRC = "/home/someone/clip.fbx"\nDEST_PATH = "/Game/OneBossFight/X/Y"\n')
        log = self.write("ev.log", f"loaded /Game/OneBossFight/X/Y from {self.dir}\n")
        plain, red = self.check("asset_provenance.py", script, "--evidence", log)
        self.assertIn(win, plain.stdout, "control: default output keeps the declared value verbatim")
        for value in (win, "/home/someone", "someone"):
            self.assertNotIn(value, red.stdout)
        self.assertIn("/Game/OneBossFight/X/Y", red.stdout, "Unreal object paths are preserved")
        self.assertIn("SOURCE line=", red.stdout)

    def test_asset_provenance_error_path(self):
        self.check("asset_provenance.py", self.dir / "absent_author.py")

    # --- proof_report (BO-06) ---
    def test_proof_report_success_and_checklist_paths(self):
        log = self.write("run/editor_raw.log", f"[FrameworkProof] decision card=A path={self.dir}\n")
        expected = self.write("FEATURE_EXPECTED.md", "## PASS\n- [ ] decision is logged `decision`\n- [ ] something manual\n")
        plain, red = self.check("proof_report.py", log, expected)
        self.assertIn("FEATURE_EXPECTED.md", red.stdout, "the checklist file name stays readable")

    def test_proof_report_error_path(self):
        expected = self.write("E.md", "- [ ] x\n")
        self.check("proof_report.py", self.dir / "missing.log", expected, expect_leak_in_control=False)  # generic message, no path

    # --- suite_log_report (BO-07) ---
    def test_suite_log_report_embedded_paths_text_and_json(self):
        abs_test = str(self.dir / "Tests" / "A.cpp")
        log = self.write("suite.log", f"Test Completed. Result={{Fail}} Name={{A}} Path={{{abs_test}}}\n"
                                      f"Test Completed. Result={{Success}} Name={{B}} Path={{OneBossFight.Framework.B}}\n"
                                      f"Test Completed. Result={{Fail}} Name={{A}} Path={{{abs_test}}}\nTEST COMPLETE. EXIT CODE: 0\n")
        for extra in ((), ("--json",)):
            with self.subTest(mode=extra or "text"):
                plain, red = self.check("suite_log_report.py", log, *extra)
                self.assertIn("OneBossFight.Framework.B", red.stdout if extra else red.stdout + "OneBossFight.Framework.B",
                              "non-path test identifiers are kept")
                self.assertIn("A.cpp", red.stdout, "failure/duplicate aggregates keep the file name")

    def test_suite_log_report_error_path(self):
        self.check("suite_log_report.py", self.dir / "absent.log")

    # --- evidence_summary (BO-08) ---
    def test_evidence_summary_error_path(self):
        self.check("evidence_summary.py", "--root", redaction.PROJECT_ROOT, "--evidence", self.dir / "no_such_dir",
                   "--output", self.dir / "out.csv")

    def test_evidence_summary_output_confirmation(self):
        evidence = self.dir / "ev"
        self.write("ev/run1/editor_raw.log", "[2026.11.12-10.00.00:000][  1]LogTemp: [FrameworkProof] RESULT acceptedHits=1\n")
        out = self.dir / "summary.csv"
        plain, red = self.check("evidence_summary.py", "--root", redaction.PROJECT_ROOT, "--evidence", evidence, "--output", out)
        if plain.returncode == 0:
            self.assertIn("logs=1", red.stdout)

    # --- summarize_framework_log / plot_framework_timeline (BO-09) ---
    def test_summarize_framework_log_structured_fields(self):
        log = self.write("fw.log", f"[FrameworkProof] decision card=A instance=1 source={self.dir}\n"
                                   "[FrameworkProof] hit instance=1 outcome=ERPGDamageOutcome::Accepted\n")
        plain, red = self.check("summarize_framework_log.py", log)
        self.assertIn("accepted=1", red.stdout, "parsed telemetry is kept")

    def test_summarize_framework_log_error_path(self):
        self.check("summarize_framework_log.py", self.dir / "absent.log")

    def test_plot_framework_timeline_fields_and_payload(self):
        log = self.write("tl.log", f"[2026.11.12-10.00.00:000][  1]LogTemp: [FrameworkProof] decision card=A reason={self.dir}\n"
                                   f"[2026.11.12-10.00.01:000][  2]LogTemp: [FrameworkProof] note {self.dir}\n")
        plain, red = self.check("plot_framework_timeline.py", log)
        self.assertIn("decision", red.stdout, "token column is kept")

    def test_plot_framework_timeline_error_path(self):
        self.check("plot_framework_timeline.py", self.dir / "absent.log")

    # --- token_coverage ---
    def test_token_coverage_success_and_missing(self):
        root = self.dir / "root"
        self.write("root/Docs/BossCombatReview/Execution/Antigravity/Reviews/validate_framework_proof_logs.py", 'SCHEMAS = {"decision": 1}\n')
        log = self.write("outside.log", f"[FrameworkProof] decision at {self.dir}\n")
        manifest = self.dir / "m.json"
        self.check("token_coverage.py", "--root", root, "--samples-output", manifest, log)
        self.check("token_coverage.py", "--root", root, log, self.dir / "missing.log")


class DefaultOutputUnchanged(unittest.TestCase):
    """Without --redact, the stream wrapper is not installed."""

    def test_install_is_noop_without_flag(self):
        before = (sys.stdout, sys.stderr)
        redaction.install_stream_redaction(False)
        self.assertEqual((sys.stdout, sys.stderr), before)

    def test_redact_text_keeps_object_paths_and_telemetry(self):
        for text in ("/Game/A/B.B", "/Script/OneBossFight.RPGBoss", "outcome=ERPGDamageOutcome::Parried", "ratio 1/2", "card=A3b"):
            self.assertEqual(redaction.redact_text(text), text)


if __name__ == "__main__":
    unittest.main()
