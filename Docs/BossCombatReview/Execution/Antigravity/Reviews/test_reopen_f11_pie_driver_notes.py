"""Re-open test suite for F11_PIE_DRIVER_NOTES.md.

Verifies:
1. File exists, pure CRLF, 0 TABs.
2. Driver source citations (Claude/F4/drive_pie.py, Claude/F4/run_pie.ps1).
3. Test plan citations (BUILD-69, BUILD-72, BUILD-73, BUILD-78, BUILD-79, BUILD-80, BUILD-82).
4. Content map and profile citations.
5. Injected hit mechanisms (current_inject.txt, current_inject_pie.txt, current_inject_row.txt).
6. Phase 2 crossing mechanisms.
7. Exact command lines and log markers.

Run:
    python -I test_reopen_f11_pie_driver_notes.py
"""
import hashlib
import os
import unittest

ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", ".."))
NOTES_PATH = os.path.join(os.path.dirname(__file__), "F11_PIE_DRIVER_NOTES.md")
TEST_PLAN_PATH = os.path.join(ROOT, "Documentation", "TEST_PLAN.md")
DRIVER_PY = os.path.join(ROOT, "Docs", "BossCombatReview", "Execution", "Claude", "F4", "drive_pie.py")
RUN_PIE_PS1 = os.path.join(ROOT, "Docs", "BossCombatReview", "Execution", "Claude", "F4", "run_pie.ps1")


def read_text(path):
    with open(path, "rb") as f:
        return f.read().decode("utf-8", errors="replace")


class TestF11PieDriverNotesIntegrity(unittest.TestCase):
    def test_file_exists(self):
        self.assertTrue(os.path.exists(NOTES_PATH), "F11_PIE_DRIVER_NOTES.md missing")

    def test_pure_crlf_and_no_tabs(self):
        with open(NOTES_PATH, "rb") as f:
            raw = f.read()
        self.assertNotIn(b"\t", raw, "Found TAB character in F11_PIE_DRIVER_NOTES.md")
        lone_lf = raw.count(b"\n") - raw.count(b"\r\n")
        self.assertEqual(lone_lf, 0, f"Found {lone_lf} lone LF characters in F11_PIE_DRIVER_NOTES.md")
        self.assertTrue(raw.endswith(b"\r\n"), "File must end with CRLF")

    def test_no_latex_formatting(self):
        content = read_text(NOTES_PATH)
        self.assertNotIn("\\text{", content, "Found LaTeX \\text in notes")
        self.assertNotIn("\\frac{", content, "Found LaTeX \\frac in notes")
        self.assertNotIn("$$", content, "Found LaTeX display math $$ in notes")


class TestDriverSourceCitations(unittest.TestCase):
    def setUp(self):
        self.notes = read_text(NOTES_PATH)
        self.driver_code = read_text(DRIVER_PY)
        self.run_pie_code = read_text(RUN_PIE_PS1)

    def test_driver_files_exist_on_disk(self):
        self.assertTrue(os.path.exists(DRIVER_PY), "drive_pie.py missing")
        self.assertTrue(os.path.exists(RUN_PIE_PS1), "run_pie.ps1 missing")

    def test_control_files_cited_in_driver(self):
        control_files = [
            "current_map.txt",
            "current_log.txt",
            "current_inject.txt",
            "current_inject_pie.txt",
            "current_inject_row.txt",
            "current_real_swing.txt",
            "current_real_build.txt",
            "current_restart.txt",
        ]
        for cf in control_files:
            self.assertIn(cf, self.notes, f"Missing control file citation: {cf}")
            self.assertIn(cf, self.driver_code, f"Control file {cf} not referenced in drive_pie.py")

    def test_run_pie_parameters_cited(self):
        params = ["-Map", "-OutDir", "-Task", "-Inject", "-InjectPie", "-Restart"]
        for p in params:
            self.assertIn(p, self.notes, f"run_pie parameter {p} not cited in notes")
            var_name = "$" + p.lstrip("-")
            self.assertIn(var_name, self.run_pie_code, f"run_pie parameter {var_name} missing from run_pie.ps1")

    def test_full_raw_log_exit_code_line(self):
        full_raw_path = os.path.join(ROOT, "Docs", "BossCombatReview", "Execution", "Claude", "F11", "full_raw.log")
        self.assertTrue(os.path.exists(full_raw_path), "full_raw.log missing")
        with open(full_raw_path, "r", encoding="utf-8", errors="replace") as f:
            lines = f.readlines()
        self.assertGreaterEqual(len(lines), 4012, f"full_raw.log has only {len(lines)} lines")
        line_4012 = lines[4011].strip()
        self.assertIn("TEST COMPLETE. EXIT CODE: 0", line_4012, f"Line 4012 did not contain expected text. Actual: {line_4012}")


class TestTestPlanCitations(unittest.TestCase):
    def setUp(self):
        self.notes = read_text(NOTES_PATH)
        self.test_plan = read_text(TEST_PLAN_PATH)

    def test_f8_rows_cited(self):
        self.assertIn("BUILD-78", self.notes, "Missing BUILD-78 citation")
        self.assertIn("BUILD-79", self.notes, "Missing BUILD-79 citation")
        self.assertIn("BUILD-80", self.notes, "Missing BUILD-80 citation")
        self.assertIn("BUILD-78", self.test_plan, "BUILD-78 not found in TEST_PLAN.md")
        self.assertIn("BUILD-79", self.test_plan, "BUILD-79 not found in TEST_PLAN.md")
        self.assertIn("BUILD-80", self.test_plan, "BUILD-80 not found in TEST_PLAN.md")

    def test_f6c_rows_cited(self):
        self.assertIn("BUILD-69", self.notes, "Missing BUILD-69 citation")
        self.assertIn("BUILD-72", self.notes, "Missing BUILD-72 citation")
        self.assertIn("BUILD-73", self.notes, "Missing BUILD-73 citation")
        self.assertIn("BUILD-69", self.test_plan, "BUILD-69 not found in TEST_PLAN.md")
        self.assertIn("BUILD-72", self.test_plan, "BUILD-72 not found in TEST_PLAN.md")
        self.assertIn("BUILD-73", self.test_plan, "BUILD-73 not found in TEST_PLAN.md")


class TestF11ExecutionCommandsAndTokens(unittest.TestCase):
    def setUp(self):
        self.notes = read_text(NOTES_PATH)

    def test_map_asset_paths_cited(self):
        maps = [
            "/Game/OneBossFight/FrameworkProof/L_SevarogFrameworkProofF11",
            "/Game/OneBossFight/FrameworkProof/L_SevarogFrameworkProofF8",
            "/Game/OneBossFight/FrameworkProof/L_SevarogFrameworkProofF6c",
        ]
        for m in maps:
            self.assertIn(m, self.notes, f"Proof map {m} not cited in notes")

    def test_expected_log_tokens_present(self):
        tokens = [
            "[FrameworkProof] stance_break",
            "[FrameworkProof] stagger_anim state=Start",
            "[FrameworkProof] stagger_anim state=Loop",
            "[FrameworkProof] stagger_anim state=End",
            "[FrameworkProof] stagger_anim state=Finished",
            "[FrameworkProof] stagger_recovery",
            "[FrameworkProof] phase_transition",
            "[FrameworkProof] phase_anim state=Start",
            "[FrameworkProof] phase_anim state=Finished",
            "[FrameworkProof] RESULT",
        ]
        for t in tokens:
            self.assertIn(t, self.notes, f"Expected log token {t} missing from notes")


if __name__ == "__main__":
    unittest.main()
