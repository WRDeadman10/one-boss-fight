"""BO-31..34 (C, implementer; per X-2254): argv pre-scan parity with argparse, and nested-scope cleanup. Synthetic only.

  BO-31  `_resolves_to` agrees with argparse's own option resolution (the oracle is `parser._parse_optional`, ambiguity
         surfacing as a SystemExit) across aliases, prefix collisions, `=value`, single-dash options and prefix_chars.
  BO-32  argv boundaries: repeated flags, positionals, a bare `--`, explicit `argv=` injection, and `--redact` as an
         option's value.
  BO-33  nested scopes with *different* caller-owned wrappers on stdout and stderr, through return, exception and
         SystemExit.
  BO-34  tool mains under `allow_abbrev=False`: early activation follows the parser (an abbreviation does not enable;
         the exact flag does).
"""
import argparse
import contextlib
import importlib
import io
import itertools
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import redaction  # noqa: E402

B = "\\"


def oracle(parser, token, action):
    """True when argparse itself resolves `token` to `action`. Ambiguity (argparse calls error -> SystemExit) means False."""
    err = io.StringIO()
    try:
        with contextlib.redirect_stderr(err):
            result = parser._parse_optional(token)
    except SystemExit:
        return False
    if not result:
        return False
    if isinstance(result, list):  # Python 3.12+: a list of candidate tuples
        return len(result) == 1 and result[0][0] is action
    return result[0] is action


def make_parser(extra_options, allow_abbrev=True, prefix_chars="-"):
    p = argparse.ArgumentParser(allow_abbrev=allow_abbrev, prefix_chars=prefix_chars, add_help=False)
    for names in extra_options:
        p.add_argument(*names, action="store_true")
    with contextlib.ExitStack():
        redaction.add_redact_argument(p, argv=[])
    return p, p._option_string_actions["--redact"]


class Bo31ParityWithArgparse(unittest.TestCase):
    OPTION_SETS = [
        [],
        [("--root",)],
        [("--require-complete-run",), ("--root",)],          # --re ambiguous, --red unique
        [("--redaction-level",)],                             # --redac ambiguous; exact --redact still resolves
        [("--rep", "--report")],                              # aliases sharing the --re prefix
        [("-r", "--recursive")],                              # single-dash alias and --re collision
        [("--redact-paths-only",)],                           # a longer option starting with the full flag
        [("--x",), ("--y",), ("--json",), ("--allow-partial",)],
    ]
    TOKENS = ["--r", "--re", "--red", "--reda", "--redac", "--redact", "--redact=1", "--reda=x", "--re=x", "--redactx",
              "-r", "---redact", "--REDACT", "redact", "-redact", "--rec", "--report"]

    def test_parity_matrix(self):
        mismatches = []
        for options, abbrev in itertools.product(self.OPTION_SETS, (True, False)):
            p, action = make_parser(options, allow_abbrev=abbrev)
            for token in self.TOKENS:
                want, got = oracle(p, token, action), redaction._resolves_to(p, token, action)
                if want != got:
                    mismatches.append((options, abbrev, token, want, got))
        self.assertEqual(mismatches, [], "pre-scan must resolve exactly as argparse does")

    def test_bare_double_dash_is_separator_not_prefix(self):
        """argparse's _parse_optional would resolve a bare `--` as a prefix of --redact, but parse_args consumes `--` as the
        positional separator before option resolution. The pre-scan matches real parsing and never treats `--` as the flag."""
        p, action = make_parser([])
        self.assertTrue(oracle(p, "--", action), "documents the oracle quirk")
        self.assertFalse(redaction._resolves_to(p, "--", action))
        ns, _ = p.parse_known_args(["--"])
        self.assertFalse(ns.redact, "real parsing: `--` alone does not set --redact")

    def test_non_dash_prefix_chars_never_pre_enable(self):
        # With prefix_chars="+", argparse treats "--redact" as a positional name, so no token can resolve to it as a flag.
        p = argparse.ArgumentParser(prefix_chars="+")
        saved = sys.stdout
        try:
            redaction.add_redact_argument(p, argv=["--redact"])
            self.assertIs(sys.stdout, saved)
        finally:
            redaction.install_stream_redaction(False)
            sys.stdout = saved


class Bo32ArgvBoundaries(unittest.TestCase):
    def setUp(self):
        self.saved = (sys.stdout, sys.stderr)

    def tearDown(self):
        sys.stdout, sys.stderr = self.saved

    def enabled_after(self, argv, options=(("--root",),), root_takes_value=False):
        sys.stdout, sys.stderr = io.StringIO(), io.StringIO()
        before = sys.stdout
        p = argparse.ArgumentParser(add_help=False)
        for names in options:
            if root_takes_value:
                p.add_argument(*names)
            else:
                p.add_argument(*names, action="store_true")
        p.add_argument("files", nargs="*")
        redaction.add_redact_argument(p, argv=argv)
        on = isinstance(sys.stdout, redaction._RedactingStream)
        # Cross-check with argparse: does the parsed namespace really have redact=True?
        try:
            with contextlib.redirect_stderr(io.StringIO()):
                ns, _ = p.parse_known_args(argv)
            parsed = bool(ns.redact)
        except SystemExit:
            parsed = None
        redaction.install_stream_redaction(False)
        self.assertIs(sys.stdout, before)
        return on, parsed

    def test_boundaries(self):
        cases = {
            ("--redact", "--redact"): True,                 # repeated
            ("a.log", "--redact", "b.log"): True,            # among positionals
            ("--", "--redact"): False,                       # after bare --: positional
            ("a.log", "--", "--reda"): False,
            ("--redact", "--", "x"): True,
            (): False,
            ("--reda",): True,
            ("--redact=1",): True,                           # argparse later rejects the value; activation is harmless
        }
        for argv, want in cases.items():
            with self.subTest(argv=argv):
                on, parsed = self.enabled_after(list(argv))
                self.assertEqual(on, want)
                if parsed is not None:
                    self.assertEqual(on, parsed, "early activation must match argparse's parsed value")

    def test_redact_as_an_option_value(self):
        # `--root --redact`: argparse does not take an option-looking token as a value, so --redact is the flag
        # (and --root errors out for a missing value). Pre-enabling matches what argparse sees.
        on, parsed = self.enabled_after(["--root", "--redact"], root_takes_value=True)
        self.assertTrue(on)
        self.assertIsNone(parsed, "argparse errors: --root expected one argument")
        on, parsed = self.enabled_after(["--root=--redact"], root_takes_value=True)
        self.assertFalse(on, "an =value is part of the --root token, not a flag")
        self.assertFalse(parsed)

    def test_explicit_argv_overrides_sys_argv(self):
        saved_argv = sys.argv
        try:
            sys.argv = ["tool.py", "--redact"]
            self.assertEqual(self.enabled_after([])[0], False, "explicit argv=[] wins over sys.argv")
            sys.argv = ["tool.py"]
            self.assertEqual(self.enabled_after(["--redact"])[0], True)
        finally:
            sys.argv = saved_argv


class Bo33NestedScopesDifferentWrappers(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self._tmp.name).resolve()
        self.log = self.dir / "fw.log"
        self.log.write_text(f"[FrameworkProof] decision card=A source={self.dir}\n", encoding="utf-8")
        self.saved = (sys.stdout, sys.stderr, sys.argv)

    def tearDown(self):
        sys.stdout, sys.stderr, sys.argv = self.saved
        self._tmp.cleanup()

    def leaks(self, text):
        return str(self.dir).lower() in text.lower()

    def run_main(self, argv, inject=None):
        mod = importlib.import_module("summarize_framework_log")
        original = mod.summarize
        if inject is not None:
            def failing(*a, **k):
                raise inject
            mod.summarize = failing
        sys.argv = ["summarize_framework_log.py", str(self.log), *argv]
        try:
            return ("return", mod.main())
        except SystemExit as exc:
            return ("exit", exc.code)
        except Exception as exc:  # noqa: BLE001
            return ("raise", exc)
        finally:
            mod.summarize = original

    def test_caller_wraps_stdout_only(self):
        out, err = io.StringIO(), io.StringIO()
        caller_out = redaction._RedactingStream(out)
        sys.stdout, sys.stderr = caller_out, err
        self.assertEqual(self.run_main([]), ("return", 0))
        self.assertIs(sys.stdout, caller_out)
        self.assertIs(sys.stderr, err)
        self.assertEqual(self.run_main(["--redact"]), ("return", 0))
        self.assertIs(sys.stdout, caller_out, "main adds only the missing stderr wrapper and removes it afterwards")
        self.assertIs(sys.stderr, err)
        kind, value = self.run_main(["--redact"], inject=RuntimeError(f"boom {self.dir}"))
        self.assertEqual((kind, value), ("exit", 1), "main's own stderr wrapper prints the redacted traceback")
        self.assertIn("RuntimeError: boom <tmp>/", err.getvalue())
        self.assertFalse(self.leaks(err.getvalue()))
        self.assertEqual((sys.stdout, sys.stderr), (caller_out, err))
        caller_out.flush()
        self.assertFalse(self.leaks(out.getvalue()))

    def test_caller_wraps_both_with_distinct_wrappers(self):
        out, err = io.StringIO(), io.StringIO()
        caller_out, caller_err = redaction._RedactingStream(out), redaction._RedactingStream(err)
        sys.stdout, sys.stderr = caller_out, caller_err
        kind, value = self.run_main(["--redact"], inject=RuntimeError(f"boom {self.dir}"))
        self.assertEqual(kind, "raise", "caller-owned stderr: main does not convert; the caller's excepthook path decides")
        self.assertEqual((sys.stdout, sys.stderr), (caller_out, caller_err))
        kind, value = self.run_main(["--redact"], inject=SystemExit(7))
        self.assertEqual((kind, value), ("exit", 7), "SystemExit passes through unchanged")
        self.assertEqual((sys.stdout, sys.stderr), (caller_out, caller_err))
        self.assertEqual(self.run_main([]), ("return", 0))
        caller_out.flush()
        caller_err.flush()
        self.assertFalse(self.leaks(out.getvalue() + err.getvalue()))


class Bo34AllowAbbrevFalse(unittest.TestCase):
    """Run all seven real tool mains in a subprocess where every ArgumentParser defaults to allow_abbrev=False (X-2256).

    The harness wraps `redaction.add_redact_argument` and, right after it returns (before parse_args), writes a marker
    `PREENABLED=<bool>` straight to file descriptor 1, bypassing any wrapper. That observes early activation directly
    for every tool, including tools whose argparse error does not echo the extra path."""
    HARNESS = ("import argparse, os, runpy, sys\n"
               "sys.path.insert(0, {here!r})\n"
               "import redaction\n"
               "_init = argparse.ArgumentParser.__init__\n"
               "def init(self, *a, **k):\n"
               "    k.setdefault('allow_abbrev', False)\n"
               "    _init(self, *a, **k)\n"
               "argparse.ArgumentParser.__init__ = init\n"
               "_add = redaction.add_redact_argument\n"
               "def add(parser, argv=None):\n"
               "    _add(parser, argv)\n"
               "    os.write(1, ('PREENABLED=%s\\n' % isinstance(sys.stdout, redaction._RedactingStream)).encode())\n"
               "redaction.add_redact_argument = add\n"
               "sys.argv = [{script!r}] + {argv!r}\n"
               "runpy.run_path({script!r}, run_name='__main__')\n")
    # Minimum argv each parser needs; the extra absolute path comes last. Tools with a nargs='*'/'+' positional
    # (token_coverage, summarize_framework_log) consume it as a log, so argparse does not echo it there.
    REQ = {"proof_report": ["a.log", "E.md"], "asset_provenance": ["a.py"], "evidence_summary": ["--output", "o.csv"],
           "token_coverage": ["--root", "."], "suite_log_report": ["a.log"], "summarize_framework_log": [],
           "plot_framework_timeline": ["a.log"]}
    ECHOES = {"proof_report", "asset_provenance", "evidence_summary", "suite_log_report", "plot_framework_timeline"}

    def run_tool(self, tool, argv):
        code = self.HARNESS.format(here=str(HERE), script=str(HERE / f"{tool}.py"), argv=[str(a) for a in argv])
        return subprocess.run([sys.executable, "-c", code], capture_output=True, text=True, timeout=120)

    @staticmethod
    def marker(result):
        lines = [l for l in result.stdout.splitlines() if l.startswith("PREENABLED=")]
        return lines[0].split("=", 1)[1] if lines else None

    def test_all_seven_mains(self):
        tools = ("proof_report", "asset_provenance", "evidence_summary", "token_coverage", "suite_log_report",
                 "summarize_framework_log", "plot_framework_timeline")
        with tempfile.TemporaryDirectory() as tmp:
            d = Path(tmp).resolve()
            bogus = str(d / "bogus.txt")
            for tool in tools:
                with self.subTest(tool=tool):
                    abbrev = self.run_tool(tool, self.REQ[tool] + ["--reda", bogus])
                    self.assertEqual(self.marker(abbrev), "False", f"{tool}: rejected abbreviation must not pre-enable\n{abbrev.stderr[-300:]}")
                    self.assertEqual(abbrev.returncode, 2)
                    self.assertIn("unrecognized arguments", abbrev.stderr)
                    self.assertIn("--reda", abbrev.stderr, "argparse rejects the abbreviation under allow_abbrev=False")
                    exact = self.run_tool(tool, self.REQ[tool] + ["--redact", bogus])
                    self.assertEqual(self.marker(exact), "True", f"{tool}: the exact flag must pre-enable\n{exact.stderr[-300:]}")
                    self.assertNotIn(str(d).lower(), (exact.stdout + exact.stderr).lower(), f"{tool}: no leak with the exact flag")
                    if tool in self.ECHOES:
                        self.assertIn(str(d), abbrev.stderr, "no early activation: verbatim output, as without the flag")
                        self.assertEqual(exact.returncode, 2)


if __name__ == "__main__":
    unittest.main()
