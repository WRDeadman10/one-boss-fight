"""BK-271..275 (C, implementer; X-2122): failure semantics of atomic_io callers (O1-O4 from BK-246..250).

O1 callers run as subprocesses with --editor/--output inside a throwaway OS temp dir. O2-O4 run main() in-process
with atomic_io writes injected to fail or aimed at temp paths. No project output, lock, pack, asset, Unreal, build
or PIE is touched.
"""
import contextlib
import io
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import atomic_io  # noqa: E402
import new_rule_scaffold  # noqa: E402
import summarize_encounter_cost  # noqa: E402
import summarize_packaged_metrics  # noqa: E402

O1_CALLERS = (("inventory_editor_asset_writers.py", "inventory"), ("audit_editor_save_safety.py", "audit"))


def run_cli(script, *args):
    return subprocess.run([sys.executable, str(HERE / script), *map(str, args)], capture_output=True, text=True,
                          timeout=120)


def snapshot(folder):
    return {str(p.relative_to(folder)): (p.read_bytes() if p.is_file() else "<dir>")
            for p in sorted(Path(folder).rglob("*"))}


def call_main(fn, argv=None):
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        try:
            code = fn(argv) if argv is not None else fn()
            raised = None
        except BaseException as error:  # captured, classified by the test
            code, raised = None, error
    return code, out.getvalue(), err.getvalue(), raised


class O1Fixture(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self._tmp.name)
        self.editor = self.dir / "Scripts" / "Editor"
        self.editor.mkdir(parents=True)
        (self.editor / "a.py").write_text("x = 1\n", encoding="utf-8")
        (self.dir / "blocker").write_text("keep", encoding="utf-8")
        (self.dir / "exists.md").write_text("old", encoding="utf-8")

    def tearDown(self):
        self._tmp.cleanup()


class Bk272O1ExistingVsParentIsFile(O1Fixture):
    def test_existing_destination_is_refused_as_existing(self):
        for script, word in O1_CALLERS:
            with self.subTest(script=script):
                before = snapshot(self.dir)
                r = run_cli(script, "--editor", self.editor, "--output", self.dir / "exists.md")
                self.assertEqual(r.returncode, 2, r.stderr)
                self.assertEqual(r.stdout.splitlines()[0], f"REFUSED existing {word} output: {self.dir / 'exists.md'}")
                self.assertEqual(r.stderr, "")
                self.assertEqual(snapshot(self.dir), before)

    def test_parent_component_that_is_a_file_is_not_called_existing(self):
        """O1 fix: formerly printed 'REFUSED existing ... output' although the output path does not exist."""
        for script, word in O1_CALLERS:
            with self.subTest(script=script):
                before = snapshot(self.dir)
                out = self.dir / "blocker" / "out.md"
                r = run_cli(script, "--editor", self.editor, "--output", out)
                self.assertEqual(r.returncode, 2, r.stderr)
                first = r.stdout.splitlines()[0]
                self.assertTrue(first.startswith(f"REFUSED cannot create {word} output: {out}: "), first)
                self.assertNotIn("existing", first)
                self.assertEqual(r.stderr, "")
                self.assertEqual(snapshot(self.dir), before)  # nothing written, blocker untouched, no temp

    def test_new_destination_still_written(self):
        for script, _ in O1_CALLERS:
            with self.subTest(script=script):
                out = self.dir / f"new_{script}.md"
                r = run_cli(script, "--editor", self.editor, "--output", out)
                self.assertEqual(r.returncode, 0, r.stderr)
                self.assertEqual(r.stdout.splitlines()[0], f"WROTE {out}")
                self.assertTrue(out.read_text(encoding="utf-8").startswith("# "))


class Bk273O2ScaffoldPartialCreate(unittest.TestCase):
    ARGV = ["--name", "SyntheticProbe", "--requirement-id", "BOSS-TST-271", "--slug", "probe"]

    def run_scaffold(self, root, fail_on=None):
        real = atomic_io.atomic_create_text
        calls = []

        def create(path, text):
            calls.append(Path(path).name)
            if fail_on is not None and len(calls) == fail_on:
                raise OSError(f"synthetic failure on create #{fail_on}")
            return real(path, text)

        argv = ["new_rule_scaffold.py", *self.ARGV, "--output-root", str(root)]
        with mock.patch.object(new_rule_scaffold, "atomic_create_text", create), mock.patch.object(sys, "argv", argv):
            return call_main(new_rule_scaffold.main)

    def files(self, root):
        return sorted(p.name for p in Path(root).rglob("*") if p.is_file())

    def test_failure_on_create_2_and_3_leaves_survivors_and_rerun_refuses(self):
        for fail_on, survivors in ((2, 1), (3, 2)):
            with self.subTest(fail_on=fail_on), tempfile.TemporaryDirectory() as tmp:
                code, out, err, raised = self.run_scaffold(tmp, fail_on)
                self.assertIsNone(code)
                self.assertIsInstance(raised, OSError)                 # propagates -> CLI traceback, exit 1
                self.assertEqual(len(self.files(tmp)), survivors)      # NOT all-or-none
                self.assertEqual(len(out.strip().splitlines()), survivors)  # only published paths were printed
                self.assertNotIn("Scaffold created", out)              # no false success claim
                code2, out2, err2, raised2 = self.run_scaffold(tmp)    # rerun
                self.assertEqual(code2, 2)
                self.assertIn("Refusing to overwrite existing scaffold target(s):", err2)
                self.assertEqual(err2.count("\n- "), survivors)
                self.assertEqual(len(self.files(tmp)), survivors)      # rerun does not complete the set

    def test_contract_text_does_not_promise_an_atomic_set(self):
        source = (HERE / "new_rule_scaffold.py").read_text(encoding="utf-8").lower()
        for phrase in ("atomic set", "all-or-none", "all or none", "rollback", "transaction"):
            self.assertNotIn(phrase, source)

    def test_clean_run_creates_all_three(self):
        with tempfile.TemporaryDirectory() as tmp:
            code, out, err, raised = self.run_scaffold(tmp)
            self.assertEqual((code, raised), (0, None))
            self.assertEqual(len(self.files(tmp)), 3)
            self.assertIn("Scaffold created", out)


class Bk274O3O4ReportWriteFailures(unittest.TestCase):
    """The write is injected to fail with OSError; summarize() is replaced by a fixed PASS report so the test
    isolates write/print ordering (the receipt contents are irrelevant to that)."""

    PASS = {"schema": "synthetic", "status": "PASS"}

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self._tmp.name)
        self.receipt = self.dir / "receipt.json"
        self.receipt.write_text(json.dumps({"samples": []}), encoding="utf-8")
        self.report = self.dir / "report.json"

    def tearDown(self):
        self._tmp.cleanup()

    def run_with_failing_write(self, module, argv):
        with mock.patch.object(module, "summarize", return_value=dict(self.PASS)), \
                mock.patch.object(module, "atomic_write_text", side_effect=OSError("synthetic write failure")):
            return call_main(module.main, argv)

    def test_pass_report_with_failing_write_is_never_a_success(self):
        for module in (summarize_encounter_cost, summarize_packaged_metrics):
            with self.subTest(module=module.__name__):
                code, out, err, raised = self.run_with_failing_write(
                    module, [str(self.receipt), "--report-json", str(self.report)])
                self.assertIsNone(code)
                self.assertIsInstance(raised, OSError)   # uncaught -> traceback, exit 1 (not 0, not the 0/2 codes)
                self.assertEqual(out, "")                # write happens BEFORE print on the normal path
                self.assertFalse(self.report.exists())

    def test_o3_read_failure_path_prints_before_the_write(self):
        missing = self.dir / "missing.json"
        with mock.patch.object(summarize_encounter_cost, "atomic_write_text",
                               side_effect=OSError("synthetic write failure")):
            code, out, err, raised = call_main(summarize_encounter_cost.main,
                                               [str(missing), "--report-json", str(self.report)])
        self.assertIsInstance(raised, OSError)
        printed = json.loads(out)
        self.assertEqual(printed["status"], "INCONCLUSIVE")   # stdout holds a NON-success report
        self.assertTrue(printed["issues"][0].startswith("cannot read valid UTF-8 receipt"))
        self.assertFalse(self.report.exists())

    def test_real_write_failure_under_temp_paths(self):
        """Non-injected: --report-json under a parent that is a file -> the real atomic_io error propagates."""
        (self.dir / "blocker").write_text("keep", encoding="utf-8")
        bad = self.dir / "blocker" / "report.json"
        for module in (summarize_encounter_cost, summarize_packaged_metrics):
            with self.subTest(module=module.__name__), mock.patch.object(module, "summarize",
                                                                         return_value=dict(self.PASS)):
                code, out, err, raised = call_main(module.main, [str(self.receipt), "--report-json", str(bad)])
                self.assertIsInstance(raised, (FileExistsError, NotADirectoryError))
                self.assertEqual(out, "")
                self.assertEqual((self.dir / "blocker").read_text(encoding="utf-8"), "keep")

    def test_successful_write_then_print(self):
        for module in (summarize_encounter_cost, summarize_packaged_metrics):
            with self.subTest(module=module.__name__), mock.patch.object(module, "summarize",
                                                                         return_value=dict(self.PASS)):
                report = self.dir / f"{module.__name__}.json"
                code, out, err, raised = call_main(module.main, [str(self.receipt), "--report-json", str(report)])
                self.assertEqual((code, raised), (0, None))
                self.assertEqual(json.loads(report.read_text(encoding="utf-8")), self.PASS)
                self.assertEqual(json.loads(out), self.PASS)


if __name__ == "__main__":
    unittest.main()
