"""BO-16..20 (C, implementer; per X-2245): redaction lifecycle, JSON, artifact and near-miss boundary tests. Synthetic temp files only.

  BO-16  --redact JSON stdout stays parseable while absolute values are masked (suite_log_report --json).
  BO-17  newline, flush, exception exit, argparse/parser.error exit and partial tails across stdout and stderr.
  BO-18  several tool mains in one process across redact on/off transitions: no stale wrapper, no state leakage.
  BO-19  failing evidence_summary / token_coverage runs leave no partial or redacted artifact behind.
  BO-20  cross-tool near-miss matrix: POSIX near-miss roots, Unreal/plugin mounts, path tokens with spaces (pinned limits).
"""
import contextlib
import importlib
import io
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import redaction  # noqa: E402

B = "\\"


def run(script, *args):
    return subprocess.run([sys.executable, str(HERE / script), *map(str, args)], capture_output=True, text=True, timeout=180)


def run_code(code):
    prefix = f"import sys; sys.path.insert(0, {str(HERE)!r}); import redaction\n"
    return subprocess.run([sys.executable, "-c", prefix + code], capture_output=True, text=True, timeout=60)


class TempCase(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self._tmp.name).resolve()

    def tearDown(self):
        self._tmp.cleanup()

    def leaks(self, text):
        low = text.lower()
        return [f for f in {str(self.dir), str(self.dir).replace(B, "/"), str(self.dir).replace(B, B * 2)} if f.lower() in low]


class Bo16JsonStaysParseable(TempCase):
    def test_suite_log_report_json(self):
        abs_test = str(self.dir / "Tests" / "A Spaced.cpp")
        other = "D:" + B + "Build" + B + "B.cpp"
        log = self.dir / "suite.log"
        log.write_text(f"Test Completed. Result={{Fail}} Name={{A}} Path={{{abs_test}}}\n"
                       f"Test Completed. Result={{Fail}} Name={{B}} Path={{{other}}}\n"
                       "Test Completed. Result={Success} Name={C} Path={OneBossFight.Framework.C}\nTEST COMPLETE. EXIT CODE: 0\n",
                       encoding="utf-8")
        plain = run("suite_log_report.py", log, "--json")
        red = run("suite_log_report.py", log, "--json", "--redact")
        self.assertEqual(red.returncode, plain.returncode)
        p, r = json.loads(plain.stdout), json.loads(red.stdout)  # both must parse
        self.assertEqual(self.leaks(red.stdout), [])
        self.assertEqual(sorted(p), sorted(r), "same keys")
        self.assertEqual((r["finished"], r["passed"], r["failed"]), (p["finished"], p["passed"], p["failed"]))
        paths = [t["path"] for t in r["tests"]]
        self.assertEqual(paths[2], "OneBossFight.Framework.C")
        self.assertEqual(paths[1], "<external>/B.cpp")
        self.assertTrue(paths[0].startswith("<tmp>/") and paths[0].endswith("A Spaced.cpp"), paths[0])
        self.assertEqual(r["file"], "<external>/suite.log")


class Bo17StreamEdges(unittest.TestCase):
    P = str(redaction.PROJECT_ROOT / "Source" / "x.cpp")

    def test_partial_tails_on_both_streams_flush_at_exit(self):
        r = run_code(f"redaction.install_stream_redaction(True); sys.stdout.write({self.P!r}); sys.stderr.write({self.P!r})")
        self.assertEqual((r.stdout, r.stderr), ("Source" + B + "x.cpp", "Source" + B + "x.cpp"))

    def test_exception_exit_traceback_is_redacted(self):
        r = run_code(f"redaction.install_stream_redaction(True); print('before', flush=True); raise RuntimeError({self.P!r})")
        self.assertEqual(r.returncode, 1)
        self.assertIn("RuntimeError: Source" + B + "x.cpp", r.stderr)
        self.assertNotIn(str(redaction.PROJECT_ROOT), r.stderr)

    def test_sys_exit_with_partial_tail(self):
        r = run_code(f"redaction.install_stream_redaction(True); sys.stdout.write('p=' + {self.P!r}); sys.exit(3)")
        self.assertEqual((r.returncode, r.stdout), (3, "p=Source" + B + "x.cpp"))

    def test_mixed_newlines_and_explicit_flush_order(self):
        r = run_code("redaction.install_stream_redaction(True)\n"
                     f"sys.stdout.write('a\\n' + {self.P!r}[:5]); sys.stdout.flush(); sys.stdout.write({self.P!r}[5:] + '\\nb')")
        # An explicit flush in mid-path writes the held fragment early. Pinned limit: only that fragment, never the whole path.
        self.assertNotIn(self.P, r.stdout)
        self.assertTrue(r.stdout.startswith("a\n"))
        self.assertTrue(r.stdout.endswith("\nb"))

    def test_parser_error_after_install_is_redacted(self):
        missing = redaction.PROJECT_ROOT / "no_such_dir_bo17" / "x.log"
        r = run("suite_log_report.py", missing, "--redact")  # parser.error runs after install_stream_redaction
        self.assertEqual(r.returncode, 2)
        self.assertNotIn(str(redaction.PROJECT_ROOT), r.stderr)
        self.assertIn("no_such_dir_bo17", r.stderr)

    def test_argparse_usage_error_before_install_is_unchanged(self):
        r = run("suite_log_report.py", "x.log", "--redact", "--no-such-flag")
        self.assertEqual(r.returncode, 2)
        self.assertIn("unrecognized arguments", r.stderr)


class Bo18ManyMainsOneProcess(TempCase):
    TOOLS = ("suite_log_report", "summarize_framework_log", "plot_framework_timeline")

    def call(self, module, argv):
        out, err = io.StringIO(), io.StringIO()
        saved = sys.argv
        sys.argv = [module + ".py", *map(str, argv)]
        try:
            with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
                try:
                    code = importlib.import_module(module).main()
                except SystemExit as exc:
                    code = exc.code
                after = (sys.stdout, sys.stderr)
            return code, out.getvalue() + err.getvalue(), after, (out, err)
        finally:
            sys.argv = saved

    def test_on_off_transitions_leave_no_stale_wrapper(self):
        suite = self.dir / "s.log"
        suite.write_text("Test Completed. Result={Success} Name={A} Path={X.A}\nTEST COMPLETE. EXIT CODE: 0\n", encoding="utf-8")
        fw = self.dir / "fw.log"
        fw.write_text("[FrameworkProof] decision card=A\n", encoding="utf-8")
        tl = self.dir / "tl.log"
        tl.write_text("[2026.11.12-10.00.00:000][  1]LogTemp: [FrameworkProof] decision card=A\n", encoding="utf-8")
        args = {"suite_log_report": [suite, "--json"], "summarize_framework_log": [fw], "plot_framework_timeline": [tl]}
        before = (sys.stdout, sys.stderr)
        for redact in (True, False, True, False):
            for module in self.TOOLS:
                with self.subTest(module=module, redact=redact):
                    code, text, after, originals = self.call(module, args[module] + (["--redact"] if redact else []))
                    self.assertEqual(code, 0, text)
                    self.assertEqual(after, originals, "main must restore the streams it was given (no stale wrapper)")
                    if redact:
                        self.assertEqual(self.leaks(text), [])
                    else:
                        self.assertTrue(self.leaks(text), "plain run after a redacted run must print verbatim paths")
        self.assertEqual((sys.stdout, sys.stderr), before)
        self.assertNotIsInstance(sys.stdout, redaction._RedactingStream)


class Bo19NoPartialArtifacts(TempCase):
    def test_evidence_summary_missing_evidence_dir(self):
        out = self.dir / "o.csv"
        for extra in ((), ("--redact",)):
            r = run("evidence_summary.py", "--root", redaction.PROJECT_ROOT, "--evidence", self.dir / "absent", "--output", out, *extra)
            self.assertEqual(r.returncode, 2)
            self.assertFalse(out.exists())
            if extra:
                self.assertEqual(self.leaks(r.stdout + r.stderr), [])

    def test_evidence_summary_unreadable_log_leaves_no_csv(self):
        evidence = self.dir / "ev"
        (evidence / "run1" / "editor_raw.log").mkdir(parents=True)  # a directory where a log is expected: the read fails
        out = self.dir / "o.csv"
        for extra in ((), ("--redact",)):
            r = run("evidence_summary.py", "--root", redaction.PROJECT_ROOT, "--evidence", evidence, "--output", out, *extra)
            self.assertNotEqual(r.returncode, 0)
            self.assertFalse(out.exists(), "no partial CSV")
            self.assertEqual([p.name for p in self.dir.iterdir() if p.name.startswith("o.csv") or p.suffix == ".tmp"], [],
                             "no temp leftovers next to the output")
            if extra:
                self.assertEqual(self.leaks(r.stdout + r.stderr), [])

    def test_token_coverage_missing_log_fail_closed(self):
        root = self.dir / "root"
        val = root / "Docs/BossCombatReview/Execution/Antigravity/Reviews/validate_framework_proof_logs.py"
        val.parent.mkdir(parents=True)
        val.write_text('SCHEMAS = {"decision": 1}\n', encoding="utf-8")
        good = self.dir / "g.log"
        good.write_text("[FrameworkProof] decision x\n", encoding="utf-8")
        manifest = self.dir / "m.json"
        for extra in ((), ("--redact",)):
            r = run("token_coverage.py", "--root", root, "--samples-output", manifest, good, self.dir / "absent.log", *extra)
            self.assertEqual(r.returncode, 2)
            self.assertFalse(manifest.exists())
            if extra:
                self.assertEqual(self.leaks(r.stdout + r.stderr), [])


class Bo20NearMissMatrix(unittest.TestCase):
    CASES = [
        # (input, expected output, note)
        ("/homework/x.txt", "/homework/x.txt", "near-miss: not /home/"),
        ("/Home/u/x.txt", "/Home/u/x.txt", "case-sensitive roots: /Home is not masked (pinned limit)"),
        ("/usr", "/usr", "bare root without a child segment is not masked"),
        ("/data2/x.log", "/data2/x.log", "unlisted root (pinned limit)"),
        ("/var/log/x.log", "<external>/x.log", "listed root"),
        ("/Game/Maps/L_Arena.L_Arena", "/Game/Maps/L_Arena.L_Arena", "Unreal content mount"),
        ("/AdvancedARPGCombat/Blueprints/BP_X.BP_X_C", "/AdvancedARPGCombat/Blueprints/BP_X.BP_X_C", "plugin mount"),
        ("/Script/Engine.Actor", "/Script/Engine.Actor", "script path"),
        ("D:" + B + "My Files" + B + "x.log", "<external>/My Files" + B + "x.log", "space outside known roots: masked only up to the space (pinned limit)"),
        ("x=/opt/My App/bin", "x=<external>/My App/bin", "POSIX path with a space: same pinned limit"),
    ]

    def test_redact_text_matrix(self):
        for raw, want, note in self.CASES:
            with self.subTest(note=note):
                self.assertEqual(redaction.redact_text(raw), want)

    def test_matrix_through_two_tools(self):
        with tempfile.TemporaryDirectory() as tmp:
            d = Path(tmp)
            log = d / "fw.log"
            log.write_text("".join(f"[FrameworkProof] decision card=A reason={raw}\n" for raw, _, _ in self.CASES[:8]), encoding="utf-8")
            r = run("summarize_framework_log.py", log, "--redact")
            self.assertEqual(r.returncode, 0)
            tl = d / "tl.log"
            tl.write_text("".join(f"[2026.11.12-10.00.0{i}:000][  1]LogTemp: [FrameworkProof] decision reason={raw}\n"
                                  for i, (raw, _, _) in enumerate(self.CASES[:8])), encoding="utf-8")
            r2 = run("plot_framework_timeline.py", tl, "--redact")
            self.assertEqual(r2.returncode, 0)
            for raw, want, _ in self.CASES[:8]:
                if raw == want:
                    self.assertIn(raw, r2.stdout, "preserved tokens survive the tool")
                else:
                    self.assertNotIn(raw, r2.stdout)


if __name__ == "__main__":
    unittest.main()
