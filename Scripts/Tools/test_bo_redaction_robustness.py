"""BO-21..25 (C, implementer; per X-2247): redaction robustness across all seven KI-167 tool mains. Synthetic only.

  BO-21  an injected failure (a RuntimeError carrying an absolute path, raised just after the tool installs redaction):
         under --redact, a redacted traceback and SystemExit(1); by default, the original exception propagates.
  BO-22  SystemExit / parser.error exits across the seven tools: exit code kept, streams restored, no path leak.
  BO-23  caller-owned wrappers: a main inside a caller's redaction neither unwraps nor double-wraps it, loses no output,
         and repeated mains leave no stale state.
  BO-24  display_path: root vs sibling-prefix folders, relative roots, `..` segments and symlink boundaries.
  BO-25  line-buffered stress: multi-line, Unicode and large-but-bounded records on stdout and stderr with no loss
         or duplication.
"""
import contextlib
import importlib
import io
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import redaction  # noqa: E402

B = "\\"
TOOLS = ("proof_report", "asset_provenance", "evidence_summary", "token_coverage", "suite_log_report",
         "summarize_framework_log", "plot_framework_timeline")


class TempCase(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self._tmp.name).resolve()

    def tearDown(self):
        self._tmp.cleanup()

    def leaks(self, text):
        low = text.lower()
        return [f for f in {str(self.dir), str(self.dir).replace(B, "/"), str(self.dir).replace(B, B * 2)} if f.lower() in low]

    def call_main(self, module, argv):
        """Run module.main() in-process with captured streams. Returns (outcome, exit code or exception, text, streams_after, originals)."""
        mod = importlib.import_module(module)
        out, err = io.StringIO(), io.StringIO()
        saved_argv = sys.argv
        sys.argv = [module + ".py", *map(str, argv)]
        try:
            with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
                try:
                    result = ("return", mod.main())
                except SystemExit as exc:
                    result = ("exit", exc.code)
                except Exception as exc:  # noqa: BLE001
                    result = ("raise", exc)
                after = (sys.stdout, sys.stderr)
        finally:
            sys.argv = saved_argv
        return result[0], result[1], out.getvalue() + err.getvalue(), after, (out, err)

    def argv_for(self, module):
        """Arguments that parse successfully. The files need not exist, because the injected failure fires first."""
        p = self.dir / "in.log"
        return {"proof_report": [p, self.dir / "E.md"], "asset_provenance": [self.dir / "a.py"],
                "evidence_summary": ["--output", self.dir / "o.csv"], "token_coverage": ["--root", self.dir],
                "suite_log_report": [p], "summarize_framework_log": [p], "plot_framework_timeline": [p]}[module]


class Bo21InjectedFailure(TempCase):
    def inject(self, module):
        """Two injection points. With --redact, right after the tool installs its wrapper. Without it, right after argument
        parsing: since BO-23, tools no longer call install when the flag is absent."""
        import argparse
        mod = importlib.import_module(module)
        original = mod.install_stream_redaction
        original_parse = argparse.ArgumentParser.parse_args
        secret = str(self.dir / "boom" / "secret.txt")

        def failing_install(redact):
            original(redact)
            raise RuntimeError(f"injected failure at {secret}")

        def failing_parse(parser, *a, **k):
            args = original_parse(parser, *a, **k)
            if not getattr(args, "redact", False):
                raise RuntimeError(f"injected failure at {secret}")
            return args
        mod.install_stream_redaction = failing_install
        argparse.ArgumentParser.parse_args = failing_parse
        self.addCleanup(setattr, mod, "install_stream_redaction", original)
        self.addCleanup(setattr, argparse.ArgumentParser, "parse_args", original_parse)

    def test_all_seven_mains(self):
        for module in TOOLS:
            with self.subTest(module=module):
                self.inject(module)
                kind, value, text, after, originals = self.call_main(module, self.argv_for(module) + ["--redact"])
                self.assertEqual((kind, value), ("exit", 1), text)
                self.assertIn("RuntimeError: injected failure at <tmp>/", text)
                self.assertIn("Traceback (most recent call last)", text)
                self.assertEqual(self.leaks(text), [])
                self.assertEqual(after, originals, "streams restored after a redacted failure")
                kind, value, text, after, originals = self.call_main(module, self.argv_for(module))
                self.assertEqual(kind, "raise", "default: the original exception propagates")
                self.assertIsInstance(value, RuntimeError)
                self.assertEqual(after, originals)


class Bo22ExitsAcrossTools(TempCase):
    def failing_argv(self, module):
        missing = self.dir / "missing.log"
        return {"proof_report": [missing, self.dir / "E.md"], "asset_provenance": [self.dir / "missing.py"],
                "evidence_summary": ["--evidence", self.dir / "nodir", "--output", self.dir / "o.csv"],
                "token_coverage": ["--root", self.dir / "noroot"], "suite_log_report": [missing],
                "summarize_framework_log": [missing], "plot_framework_timeline": [missing]}[module]

    def test_failure_exits(self):
        expected = {"proof_report": ("exit", 2), "asset_provenance": ("exit", 2), "evidence_summary": ("exit", 2),
                    "token_coverage": ("exit", 1), "suite_log_report": ("exit", 2), "summarize_framework_log": ("return", 1),
                    "plot_framework_timeline": ("exit", 2)}
        for module in TOOLS:
            with self.subTest(module=module):
                kind, value, text, after, originals = self.call_main(module, self.failing_argv(module) + ["--redact"])
                self.assertEqual((kind, value), expected[module], text)
                self.assertEqual(self.leaks(text), [], text)
                self.assertEqual(after, originals)
                self.assertNotIsInstance(sys.stdout, redaction._RedactingStream)
                kind2, value2, text2, after2, originals2 = self.call_main(module, self.failing_argv(module))
                self.assertEqual(after2, originals2)
                if expected[module][0] != "exit" or module != "token_coverage":
                    self.assertEqual((kind2, value2), expected[module], "same exit without --redact")


class Bo23CallerOwnedWrappers(TempCase):
    def setUp(self):
        super().setUp()
        self.log = self.dir / "fw.log"
        self.log.write_text(f"[FrameworkProof] decision card=A source={self.dir}\n", encoding="utf-8")

    def test_main_inside_caller_redaction(self):
        mod = importlib.import_module("summarize_framework_log")
        sink = io.StringIO()
        saved = (sys.stdout, sys.stderr)
        saved_argv = sys.argv
        try:
            sys.stdout = sys.stderr = sink
            redaction.install_stream_redaction(True)  # caller-owned wrapper
            caller_wrapper = sys.stdout
            for extra in ([], ["--redact"], [], ["--redact"]):  # repeated mains, with and without their own flag
                sys.argv = ["summarize_framework_log.py", str(self.log), *extra]
                self.assertEqual(mod.main(), 0)
                self.assertIs(sys.stdout, caller_wrapper, "the caller's wrapper survives the main")
            print("caller tail without newline", end="")
            redaction.install_stream_redaction(False)
        finally:
            sys.stdout, sys.stderr = saved
            sys.argv = saved_argv
        text = sink.getvalue()
        self.assertEqual(self.leaks(text), [], "a main without --redact must not unwrap the caller's redaction")
        self.assertEqual(text.count("token counts:"), 4, "no lost or duplicated output")
        self.assertTrue(text.endswith("caller tail without newline"))


class Bo24DisplayPath(TempCase):
    def test_sibling_prefix_is_not_inside_root(self):
        root = self.dir / "proj"
        sibling = self.dir / "proj2" / "x.log"
        sibling.parent.mkdir(parents=True)
        root.mkdir()
        sibling.write_text("x", encoding="utf-8")
        self.assertEqual(redaction.display_path(sibling, True, root), "<external>/x.log")
        self.assertEqual(redaction.display_path(root / "a" / "b.log", True, root), "a/b.log")

    def test_dotdot_and_relative_root(self):
        root = self.dir / "proj"
        (root / "sub").mkdir(parents=True)
        escaping = root / "sub" / ".." / ".." / "outside.log"
        self.assertEqual(redaction.display_path(escaping, True, root), "<external>/outside.log")
        inside = root / "sub" / ".." / "in.log"
        self.assertEqual(redaction.display_path(inside, True, root), "in.log")
        cwd = os.getcwd()
        try:
            os.chdir(self.dir)
            self.assertEqual(redaction.display_path(Path("proj") / "in.log", True, Path("proj")), "in.log")
        finally:
            os.chdir(cwd)

    def test_symlink_boundaries(self):
        root = self.dir / "proj"
        outside = self.dir / "outside"
        root.mkdir()
        outside.mkdir()
        (outside / "t.log").write_text("x", encoding="utf-8")
        link_in = root / "link_to_outside"
        try:
            link_in.symlink_to(outside, target_is_directory=True)
        except (OSError, NotImplementedError) as exc:
            self.skipTest(f"symlinks unavailable here: {exc}")
        # A link inside the root that points outside resolves outside: no repo-relative claim, no absolute path.
        self.assertEqual(redaction.display_path(link_in / "t.log", True, root), "<external>/t.log")
        link_out = outside / "link_to_root"
        link_out.symlink_to(root, target_is_directory=True)
        (root / "r.log").write_text("x", encoding="utf-8")
        self.assertEqual(redaction.display_path(link_out / "r.log", True, root), "r.log")

    def test_default_is_verbatim(self):
        p = self.dir / "a" / ".." / "b.log"
        self.assertEqual(redaction.display_path(p, False), str(p))


class Bo25LineBufferStress(unittest.TestCase):
    def test_multiline_unicode_large_records(self):
        root = str(redaction.PROJECT_ROOT)
        code = (
            "import sys; sys.path.insert(0, %r); import redaction; redaction.install_stream_redaction(True)\n"
            "R = %r\n"
            "big = 'x' * 200000\n"
            "for i in range(2000):\n"
            "    sys.stdout.write(f'line {i} é漢🙂 ' + R + chr(92) + f'f{i}.log\\n' if i %% 2 else f'multi {i}\\nsecond {i} ' + R + '\\n')\n"
            "    if i %% 250 == 0:\n"
            "        sys.stderr.write(f'err {i} ' + R)\n"
            "        sys.stderr.write(' tail\\n')\n"
            "sys.stdout.write('BIG ' + big + ' ' + R + ' END\\n')\n"
            "sys.stdout.write('no newline tail ' + R)\n"
        ) % (str(HERE), root)
        env = dict(os.environ, PYTHONIOENCODING="utf-8")
        r = subprocess.run([sys.executable, "-c", code], capture_output=True, timeout=120, env=env)
        # Windows text-mode streams translate LF to CRLF; normalize before counting records.
        crlf, lf = chr(13) + chr(10), chr(10)
        out, err = r.stdout.decode("utf-8").replace(crlf, lf), r.stderr.decode("utf-8").replace(crlf, lf)
        self.assertEqual(r.returncode, 0, err[-500:])
        self.assertNotIn(root.lower(), (out + err).lower())
        lines = out.split("\n")
        self.assertEqual(sum(1 for l in lines if l.startswith("line ")), 1000)
        self.assertEqual(sum(1 for l in lines if l.startswith("multi ")), 1000)
        self.assertEqual(sum(1 for l in lines if l.startswith("second ")), 1000)
        self.assertIn("line 1 é漢🙂 f1.log", out)
        self.assertIn("BIG " + "x" * 200000 + "  END", out)
        self.assertTrue(out.endswith("no newline tail "), out[-80:])
        self.assertEqual(err.count("tail\n"), 8)
        self.assertEqual(len(set(l for l in lines if l.startswith("line "))), 1000, "no duplicated records")


if __name__ == "__main__":
    unittest.main()
