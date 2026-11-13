"""BK-311..315 (C, implementer; X-2147): output-alias edge cases for the five report writers.

311/312 summarize_packaged_metrics aliasing a cited source_log (same path, hard link; every one of several logs);
313 Windows junction aliases; 314 samefile raising OSError (injected in a runpy wrapper) must fail closed. Real CLI
subprocesses with cwd = temp fixture root; no production data, lock, pack, asset, Unreal, build or PIE.
"""
import json
import os
import subprocess
import sys
import tempfile
import textwrap
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
VALIDATOR_REL = Path("Docs/BossCombatReview/Execution/Antigravity/Reviews/validate_framework_proof_logs.py")
ALIAS_MSG = "INCONCLUSIVE: report destination aliases an evidence input"

WRAPPER = textwrap.dedent("""
    import pathlib, runpy, sys
    tools, script, mode = sys.argv[1], sys.argv[2], sys.argv[3]
    sys.path.insert(0, tools)
    if mode == "samefile_oserror":
        def samefile(self, other):
            raise OSError(5, "synthetic samefile failure")
        pathlib.Path.samefile = samefile
    sys.argv = [script] + sys.argv[4:]
    runpy.run_path(script, run_name="__main__")
""")


def junction_reason():
    if os.name != "nt":
        return "directory junctions are Windows-only"
    try:
        import _winapi
        with tempfile.TemporaryDirectory() as tmp:
            real, link = Path(tmp) / "r", Path(tmp) / "j"
            real.mkdir()
            _winapi.CreateJunction(str(real), str(link))
            os.rmdir(link)
        return None
    except (ImportError, OSError, AttributeError) as error:
        return f"host cannot create junctions: {error!r}"


JUNCTION_SKIP = junction_reason()


class Fixture(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)
        validator = self.root / VALIDATOR_REL
        validator.parent.mkdir(parents=True)
        validator.write_text('SCHEMAS = {"ProbeToken": {}}\n'
                             'def validate_log_file(path):\n'
                             '    return {"syntax_failures": [], "semantic_violations": []}\n', encoding="utf-8")
        self.log = self.root / "ev" / "run1" / "editor_raw.log"
        self.log.parent.mkdir(parents=True)
        self.log.write_text("[FrameworkProof] ProbeToken a=1\n", encoding="utf-8")
        (self.root / "Source").mkdir()
        (self.root / "Source" / "a.cpp").write_text("int a;\n", encoding="utf-8")
        self.receipt = self.root / "receipt.json"
        self.receipt.write_text("{}", encoding="utf-8")
        self.wrapper = self.root / "wrapper.py"
        self.wrapper.write_text(WRAPPER, encoding="utf-8")

    def tearDown(self):
        self._tmp.cleanup()

    def cli(self, script, *args, mode="none"):
        return subprocess.run([sys.executable, str(self.wrapper), str(HERE), str(HERE / script), mode,
                               *map(str, args)], capture_output=True, text=True, cwd=self.root, timeout=120)

    def metrics_receipt(self, logs):
        """A receipt whose samples cite `logs` (relative to the receipt directory)."""
        samples = [{"source_log": os.path.relpath(log, self.receipt.parent)} for log in logs]
        self.receipt.write_text(json.dumps({"samples": samples}), encoding="utf-8")

    def assert_refused(self, result, victims, fragment):
        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        self.assertIn(fragment, result.stderr)
        self.assertEqual(result.stdout, "")
        for victim, before in victims.items():
            self.assertEqual(victim.read_bytes(), before, f"{victim.name} changed")
        self.assertEqual(list(self.root.rglob("*.tmp")), [])


class Bk311And312PackagedMetricsSourceLogs(Fixture):
    def setUp(self):
        super().setUp()
        self.logs = []
        for i in range(3):
            p = self.root / "logs" / f"capture_{i}.log"
            p.parent.mkdir(exist_ok=True)
            p.write_bytes(f"capture {i}\n".encode())
            self.logs.append(p)
        self.metrics_receipt(self.logs)

    def snapshot(self):
        return {p: p.read_bytes() for p in [self.receipt, *self.logs]}

    def test_every_cited_log_same_path_is_refused(self):
        for log in self.logs:
            with self.subTest(log=log.name):
                before = self.snapshot()
                result = self.cli("summarize_packaged_metrics.py", "receipt.json", "--report-json", log)
                self.assert_refused(result, before, ALIAS_MSG)

    def test_every_cited_log_hard_link_is_refused(self):
        for log in self.logs:
            with self.subTest(log=log.name):
                alias = self.root / f"hl_{log.name}"
                os.link(log, alias)
                before = self.snapshot()
                result = self.cli("summarize_packaged_metrics.py", "receipt.json", "--report-json", alias)
                self.assert_refused(result, before, ALIAS_MSG)
                self.assertTrue(os.path.samefile(alias, log))   # link not broken: nothing was written

    def test_refusal_message_does_not_name_the_aliased_input(self):
        """Observation (non-blocking): the refusal is generic; it does not say WHICH evidence path is aliased."""
        result = self.cli("summarize_packaged_metrics.py", "receipt.json", "--report-json", self.logs[1])
        self.assertEqual(result.stderr.strip(), ALIAS_MSG)


@unittest.skipIf(JUNCTION_SKIP, JUNCTION_SKIP or "")
class Bk313JunctionAlias(Fixture):
    def setUp(self):
        super().setUp()
        import _winapi
        self.jev = self.root / "j_ev"           # junction -> ev/run1 (the log's directory)
        self.jsrc = self.root / "j_src"         # junction -> Source
        self.jroot = self.root / "j_root"       # junction -> fixture root (receipt's directory)
        for link, real in ((self.jev, self.log.parent), (self.jsrc, self.root / "Source"), (self.jroot, self.root)):
            _winapi.CreateJunction(str(real), str(link))

    def tearDown(self):
        for link in (self.jev, self.jsrc, self.jroot):
            if link.exists():
                os.rmdir(link)                  # junction entry only, never the referent
        super().tearDown()

    def test_output_through_a_junction_to_an_input_is_refused(self):
        cases = [
            ("summarize_encounter_cost.py", ["receipt.json", "--report-json", self.jroot / "receipt.json"],
             self.receipt, ALIAS_MSG),
            ("summarize_packaged_metrics.py", ["receipt.json", "--report-json", self.jroot / "receipt.json"],
             self.receipt, ALIAS_MSG),
            ("evidence_summary.py", ["--root", ".", "--evidence", "ev", "--output", self.jev / "editor_raw.log"],
             self.log, "aliases an input"),
            ("token_coverage.py", ["--root", ".", "--samples-output", self.jev / "editor_raw.log", str(self.log)],
             self.log, "aliases an input"),
            ("make_source_manifest.py", [self.jsrc / "a.cpp", "--root", "."], self.root / "Source" / "a.cpp",
             "Source"),
            ("make_source_manifest.py", [self.jsrc / "new.txt", "--root", "."], self.root / "Source" / "a.cpp",
             "output must be outside the scanned Source directory"),
        ]
        for script, args, victim, fragment in cases:
            with self.subTest(script=script, output=str(args[-1] if script != "make_source_manifest.py" else args[0])):
                before = {victim: victim.read_bytes()}
                result = self.cli(script, *args)
                self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
                self.assertIn(fragment, result.stderr)
                self.assertEqual(victim.read_bytes(), before[victim])
                self.assertFalse((self.root / "Source" / "new.txt").exists())


class Bk314SamefileOSErrorFailsClosed(Fixture):
    """samefile is only reached when the output already exists, so every case targets an EXISTING separate file."""

    def test_samefile_failure_never_writes(self):
        out = self.root / "out"
        out.mkdir()
        old = b"OLD-OUTPUT\n"
        cases = [
            ("summarize_encounter_cost.py", ["receipt.json", "--report-json", out / "cost.json"], 1),
            ("summarize_packaged_metrics.py", ["receipt.json", "--report-json", out / "metrics.json"], 2),
            ("evidence_summary.py", ["--root", ".", "--evidence", "ev", "--output", out / "summary.csv"], 1),
            ("token_coverage.py", ["--root", ".", "--samples-output", out / "samples.json", str(self.log)], 1),
            ("make_source_manifest.py", [out / "manifest.txt", "--root", "."], 1),
        ]
        inputs = [self.receipt, self.log, self.root / "Source" / "a.cpp"]
        for script, args, expected in cases:
            with self.subTest(script=script):
                target = Path(args[args.index("--report-json") + 1] if "--report-json" in args else
                              args[args.index("--output") + 1] if "--output" in args else
                              args[args.index("--samples-output") + 1] if "--samples-output" in args else args[0])
                target.write_bytes(old)
                before = {p: p.read_bytes() for p in inputs}
                result = self.cli(script, *args, mode="samefile_oserror")
                self.assertEqual(result.returncode, expected, result.stdout + result.stderr)
                if expected == 2:   # packaged_metrics catches it explicitly
                    self.assertIn("INCONCLUSIVE: cannot safely compare report/evidence paths", result.stderr)
                else:               # the others propagate: uncaught traceback, still before any write
                    self.assertIn("OSError: [Errno 5] synthetic samefile failure", result.stderr)
                self.assertEqual(target.read_bytes(), old, "output must not be written")
                self.assertEqual({p: p.read_bytes() for p in inputs}, before)
                self.assertEqual(list(self.root.rglob("*.tmp")), [])
                self.assertNotIn("logs=", result.stdout)
                self.assertNotIn("files=", result.stdout)
                self.assertNotIn("sample_manifest=", result.stdout)


if __name__ == "__main__":
    unittest.main()
