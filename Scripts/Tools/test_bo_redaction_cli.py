"""BO-26..29 (C, implementer; per X-2249): command-line, invocation and artifact-failure redaction tests. Synthetic only.

  BO-26  argparse failures and --help when --redact is in argv: no absolute path leaks; no-flag behaviour unchanged.
  BO-27  invalid/missing output paths and unknown/missing arguments across all seven tools: same exit codes in both
         modes, no leaks in redacted mode.
  BO-28  direct-script vs `python -m Scripts.Tools.<tool>` invocation: both import and redact identically.
  BO-29  injected atomic artifact-write failures (token_coverage, evidence_summary): no artifact, no temp file and no
         unredacted traceback is left.
"""
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
sys.path.insert(0, str(HERE))
import redaction  # noqa: E402

B = "\\"
TOOLS = ("proof_report", "asset_provenance", "evidence_summary", "token_coverage", "suite_log_report",
         "summarize_framework_log", "plot_framework_timeline")


def run_script(tool, *args, cwd=None):
    return subprocess.run([sys.executable, str(HERE / f"{tool}.py"), *map(str, args)], capture_output=True, text=True,
                          timeout=180, cwd=cwd)


def run_module(tool, *args):
    return subprocess.run([sys.executable, "-m", f"Scripts.Tools.{tool}", *map(str, args)], capture_output=True, text=True,
                          timeout=180, cwd=REPO)


class TempCase(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self._tmp.name).resolve()

    def tearDown(self):
        self._tmp.cleanup()

    def leaks(self, text):
        low = text.lower()
        return [f for f in {str(self.dir), str(self.dir).replace(B, "/"), str(self.dir).replace(B, B * 2)} if f.lower() in low]


class Bo26ArgparseAndHelp(TempCase):
    def test_unrecognized_argument_with_absolute_path(self):
        """Each tool gets its required arguments plus one extra absolute-path positional that argparse rejects and echoes."""
        bogus = str(self.dir / "bogus.txt")
        req = {"proof_report": ["a.log", "E.md"], "asset_provenance": ["a.py"], "evidence_summary": ["--output", "o.csv"],
               "token_coverage": ["--zzz"], "suite_log_report": ["a.log"], "summarize_framework_log": ["--zzz", "a.log"],
               "plot_framework_timeline": ["a.log"]}
        echoed = 0
        for tool in TOOLS:
            with self.subTest(tool=tool):
                plain = run_script(tool, *req[tool], bogus)
                red = run_script(tool, "--redact", *req[tool], bogus)
                self.assertEqual(plain.returncode, red.returncode)
                self.assertEqual(self.leaks(red.stdout + red.stderr), [], red.stderr[-300:])
                if "unrecognized arguments" in plain.stderr and self.leaks(plain.stderr):
                    echoed += 1
                    self.assertEqual(red.returncode, 2)
                    self.assertIn("bogus.txt", red.stderr)
        self.assertGreaterEqual(echoed, 4, "the control must actually echo the absolute path for most tools (non-vacuous)")

    def test_abbreviated_flag_also_redacts(self):
        bogus = str(self.dir / "bogus.txt")
        red = run_script("suite_log_report", "--reda", "a.log", bogus)
        self.assertEqual(red.returncode, 2)
        self.assertEqual(self.leaks(red.stderr), [])

    def test_help_has_no_absolute_paths_and_is_unchanged_by_flag_position(self):
        for tool in TOOLS:
            with self.subTest(tool=tool):
                plain = run_script(tool, "--help")
                red = run_script(tool, "--redact", "--help")
                self.assertEqual((plain.returncode, red.returncode), (0, 0))
                self.assertNotIn(str(REPO).lower(), (plain.stdout + red.stdout).lower())
                self.assertEqual(plain.stdout, red.stdout, "help text is identical with --redact (no paths to mask)")
                self.assertIn("--redact", plain.stdout)


class Bo26UniquePrefixHotfix(TempCase):
    """X-2250/X-2251: every abbreviation argparse accepts for --redact must enable redaction before parsing; ambiguous ones must not."""
    REQ = {"proof_report": ["a.log", "E.md"], "asset_provenance": ["a.py"], "evidence_summary": ["--output", "o.csv"],
           "token_coverage": ["--zzz"], "suite_log_report": ["a.log"], "summarize_framework_log": ["--zzz", "a.log"],
           "plot_framework_timeline": ["a.log"]}
    PREFIXES = ("--r", "--re", "--red", "--reda", "--redac", "--redact")

    def test_lead_repro_suite_log_report_re(self):
        safe, sensitive = self.dir / "safe.log", self.dir / "sensitive.log"
        red = run_script("suite_log_report", safe, "--re", sensitive)
        self.assertEqual(red.returncode, 2)
        self.assertIn("unrecognized arguments", red.stderr)
        self.assertIn("sensitive.log", red.stderr)
        self.assertEqual(self.leaks(red.stderr), [], red.stderr)
        plain = run_script("suite_log_report", safe, sensitive)  # control without any redact token: verbatim path
        self.assertEqual(plain.returncode, 2)
        self.assertTrue(self.leaks(plain.stderr))

    def test_every_prefix_every_tool(self):
        """For each prefix argparse resolves to --redact (`usage` shows it was accepted or the extra path is echoed),
        nothing may leak. For an ambiguous prefix argparse reports the ambiguity, and no path is printed either way."""
        bogus = str(self.dir / "bogus.txt")
        accepted = 0
        for tool in TOOLS:
            for prefix in self.PREFIXES:
                with self.subTest(tool=tool, prefix=prefix):
                    r = run_script(tool, *self.REQ[tool], prefix, bogus)
                    self.assertEqual(self.leaks(r.stdout + r.stderr), [], f"{tool} {prefix}: {r.stderr[-300:]}")
                    if "ambiguous option" not in r.stderr:
                        accepted += 1
        self.assertGreaterEqual(accepted, 7 * 3, "most prefixes resolve uniquely in most tools (non-vacuous)")

    def test_ambiguous_prefix_control(self):
        """proof_report has --require-complete-run, so --re is ambiguous. argparse rejects it and redaction is not pre-enabled."""
        r = run_script("proof_report", "a.log", "E.md", "--re")
        self.assertEqual(r.returncode, 2)
        self.assertIn("ambiguous option", r.stderr)
        self.assertIn("--require-complete-run", r.stderr)

    def test_resolver_unit(self):
        import argparse
        p = argparse.ArgumentParser()
        p.add_argument("--require-complete-run", action="store_true")
        p.add_argument("--root")
        saved = (sys.stdout, sys.stderr)
        try:
            redaction.add_redact_argument(p, argv=[])
            action = p._option_string_actions["--redact"]
            cases = {"--redact": True, "--reda": True, "--red": True, "--re": False, "--r": False, "--redact=1": True,
                     "--ro": False, "-r": False, "--": False, "x--redact": False}
            for token, want in cases.items():
                with self.subTest(token=token):
                    self.assertEqual(redaction._resolves_to(p, token, action), want)
            q = argparse.ArgumentParser(allow_abbrev=False)
            redaction.add_redact_argument(q, argv=[])
            qa = q._option_string_actions["--redact"]
            self.assertFalse(redaction._resolves_to(q, "--reda", qa), "allow_abbrev=False: only the exact flag")
            self.assertTrue(redaction._resolves_to(q, "--redact", qa))
            self.assertIs(sys.stdout, saved[0], "argv=[] must not enable redaction")
            redaction.add_redact_argument(argparse.ArgumentParser(), argv=["--", "--redact"])
            self.assertIs(sys.stdout, saved[0], "a token after a bare -- is positional")
        finally:
            sys.stdout, sys.stderr = saved

    def test_no_flag_behaviour_unchanged(self):
        bogus = str(self.dir / "bogus.txt")
        for tool in ("suite_log_report", "plot_framework_timeline"):
            with self.subTest(tool=tool):
                r = run_script(tool, *self.REQ[tool], bogus)
                self.assertEqual(r.returncode, 2)
                self.assertTrue(self.leaks(r.stderr), "without any redact token, argparse output stays verbatim")


class Bo27ErrorMessagesAcrossTools(TempCase):
    def test_missing_required_arguments(self):
        for tool in TOOLS:
            with self.subTest(tool=tool):
                plain = run_script(tool)
                red = run_script(tool, "--redact")
                if tool == "token_coverage":  # no required positional: runs with defaults instead of a usage error
                    self.assertEqual(plain.returncode, red.returncode)
                    continue
                self.assertEqual((plain.returncode, red.returncode), (2, 2), red.stderr)
                self.assertIn("required", red.stderr)

    def test_invalid_output_paths(self):
        blocker = self.dir / "file_not_dir"
        blocker.write_text("x", encoding="utf-8")
        bad_out = blocker / "sub" / "out.json"  # parent is a file: mkdir/write must fail
        root = self.dir / "root"
        val = root / "Docs/BossCombatReview/Execution/Antigravity/Reviews/validate_framework_proof_logs.py"
        val.parent.mkdir(parents=True)
        val.write_text('SCHEMAS = {"decision": 1}\n', encoding="utf-8")
        log = self.dir / "g.log"
        log.write_text("[FrameworkProof] decision x\n", encoding="utf-8")
        ev = self.dir / "ev" / "r1"
        ev.mkdir(parents=True)
        (ev / "editor_raw.log").write_text("[FrameworkProof] RESULT acceptedHits=1\n", encoding="utf-8")
        cases = {
            "token_coverage": ("--root", root, "--samples-output", bad_out, log),
            "evidence_summary": ("--root", redaction.PROJECT_ROOT, "--evidence", self.dir / "ev", "--output", bad_out),
        }
        for tool, args in cases.items():
            with self.subTest(tool=tool):
                plain = run_script(tool, *args)
                red = run_script(tool, *args, "--redact")
                self.assertNotEqual(plain.returncode, 0)
                self.assertEqual(plain.returncode, red.returncode, red.stderr[-300:])
                self.assertTrue(self.leaks(plain.stdout + plain.stderr), "control shows the absolute path")
                self.assertEqual(self.leaks(red.stdout + red.stderr), [], red.stderr)
                self.assertFalse(bad_out.exists())


class Bo28InvocationStyles(TempCase):
    def test_script_and_module_invocation_match(self):
        log = self.dir / "fw.log"
        log.write_text(f"[FrameworkProof] decision card=A source={self.dir}\n", encoding="utf-8")
        suite = self.dir / "s.log"
        suite.write_text(f"Test Completed. Result={{Fail}} Name={{A}} Path={{{self.dir / 'A.cpp'}}}\nTEST COMPLETE. EXIT CODE: 0\n",
                         encoding="utf-8")
        tl = self.dir / "tl.log"
        tl.write_text(f"[2026.11.12-10.00.00:000][  1]LogTemp: [FrameworkProof] decision reason={self.dir}\n", encoding="utf-8")
        root = self.dir / "root"
        val = root / "Docs/BossCombatReview/Execution/Antigravity/Reviews/validate_framework_proof_logs.py"
        val.parent.mkdir(parents=True)
        val.write_text('SCHEMAS = {"decision": 1}\n', encoding="utf-8")
        script = self.dir / "a.py"
        script.write_text(f'SOURCE_PATH = r"{self.dir / "src.fbx"}"\n', encoding="utf-8")
        cases = {
            "summarize_framework_log": (log,), "suite_log_report": (suite,), "plot_framework_timeline": (tl,),
            "token_coverage": ("--root", root, log), "asset_provenance": (script,),
            "evidence_summary": ("--root", redaction.PROJECT_ROOT, "--evidence", self.dir / "nodir", "--output", self.dir / "o.csv"),
            "proof_report": (self.dir / "missing.log", self.dir / "E.md"),
        }
        for tool, args in cases.items():
            for extra in ((), ("--redact",)):
                with self.subTest(tool=tool, redact=bool(extra)):
                    a = run_script(tool, *args, *extra, cwd=REPO)
                    m = run_module(tool, *args, *extra)
                    self.assertNotIn("ModuleNotFoundError", m.stderr, m.stderr[-300:])
                    self.assertEqual(a.returncode, m.returncode, m.stderr[-300:])
                    self.assertEqual(a.stdout, m.stdout)
                    if extra:
                        self.assertEqual(self.leaks(m.stdout + m.stderr), [])


class Bo29AtomicWriteFailure(TempCase):
    INJECT = ("import os, sys\n"
              "sys.path.insert(0, {here!r})\n"
              "import atomic_io\n"
              "def failing_replace(src, dst):\n"
              "    raise OSError(f'injected replace failure for {{dst}}')\n"
              "atomic_io.os.replace = failing_replace\n"
              "import runpy\n"
              "sys.argv = [{script!r}] + {argv!r}\n"
              "runpy.run_path({script!r}, run_name='__main__')\n")

    def run_injected(self, tool, argv):
        code = self.INJECT.format(here=str(HERE), script=str(HERE / f"{tool}.py"), argv=[str(a) for a in argv])
        return subprocess.run([sys.executable, "-c", code], capture_output=True, text=True, timeout=180)

    def leftovers(self, folder):
        return sorted(p.name for p in folder.iterdir() if p.name not in self.inputs)

    def test_token_coverage_and_evidence_summary(self):
        root = self.dir / "root"
        val = root / "Docs/BossCombatReview/Execution/Antigravity/Reviews/validate_framework_proof_logs.py"
        val.parent.mkdir(parents=True)
        val.write_text('SCHEMAS = {"decision": 1}\n', encoding="utf-8")
        log = self.dir / "g.log"
        log.write_text("[FrameworkProof] decision x\n", encoding="utf-8")
        ev = self.dir / "ev" / "r1"
        ev.mkdir(parents=True)
        (ev / "editor_raw.log").write_text("[FrameworkProof] RESULT acceptedHits=1\n", encoding="utf-8")
        out_dir = self.dir / "out"
        out_dir.mkdir()
        self.inputs = set()
        cases = {
            "token_coverage": ["--root", root, "--samples-output", out_dir / "m.json", log],
            "evidence_summary": ["--root", redaction.PROJECT_ROOT, "--evidence", self.dir / "ev", "--output", out_dir / "s.csv"],
        }
        for tool, argv in cases.items():
            for extra in ([], ["--redact"]):
                with self.subTest(tool=tool, redact=bool(extra)):
                    r = self.run_injected(tool, argv + extra)
                    self.assertNotEqual(r.returncode, 0, r.stdout + r.stderr)
                    self.assertIn("injected replace failure", r.stderr)
                    self.assertEqual(self.leftovers(out_dir), [], "no artifact and no temp file left behind")
                    if extra:
                        self.assertEqual(r.returncode, 1)
                        self.assertEqual(self.leaks(r.stdout + r.stderr), [], r.stderr[-400:])
                    else:
                        self.assertTrue(self.leaks(r.stderr), "control: the default traceback shows the absolute path")


if __name__ == "__main__":
    unittest.main()
