"""BK-276..280 (C, implementer; X-2124): CLI failure semantics of the five atomic_write_text (replace) callers.

Each caller runs as a real subprocess on synthetic fixtures in a throwaway OS temp dir. For the failure case a tiny
runpy wrapper replaces os.replace with a PermissionError BEFORE the script runs, so the genuine atomic_io path is
exercised: temp written and fsynced, publication refused, temp cleaned. No production data, lock, asset, Unreal,
build or PIE. The synthetic validator below is a stub with the two names the callers read (SCHEMAS, validate_log_file).
"""
import json
import subprocess
import sys
import tempfile
import textwrap
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
VALIDATOR_REL = Path("Docs/BossCombatReview/Execution/Antigravity/Reviews/validate_framework_proof_logs.py")
OLD = b"OLD-DESTINATION-BYTES\n"

WRAPPER = textwrap.dedent("""
    import os, runpy, sys
    tools, script, mode = sys.argv[1], sys.argv[2], sys.argv[3]
    sys.path.insert(0, tools)
    if mode == "fail":
        def refuse(*args, **kwargs):
            raise PermissionError(13, "synthetic replace failure")
        os.replace = refuse
    sys.argv = [script] + sys.argv[4:]
    runpy.run_path(script, run_name="__main__")
""")


def temps(folder):
    return sorted(str(p.relative_to(folder)) for p in Path(folder).rglob("*.tmp"))


class Fixture(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)
        validator = self.root / VALIDATOR_REL
        validator.parent.mkdir(parents=True)
        validator.write_text('SCHEMAS = {"ProbeToken": {}}\n'
                             'def validate_log_file(path):\n'
                             '    return {"syntax_failures": [], "semantic_violations": []}\n', encoding="utf-8")
        evidence = self.root / "evidence" / "run1"
        evidence.mkdir(parents=True)
        (evidence / "editor_raw.log").write_text("[FrameworkProof] ProbeToken a=1\n", encoding="utf-8")
        (self.root / "Source").mkdir()
        (self.root / "Source" / "a.cpp").write_text("int a;\n", encoding="utf-8")
        (self.root / "receipt.json").write_text("{}", encoding="utf-8")
        self.out = self.root / "out" / "result.txt"
        self.out.parent.mkdir()

    def tearDown(self):
        self._tmp.cleanup()

    def run_caller(self, script, args, mode):
        self.out.write_bytes(OLD)
        wrapper = self.root / "wrapper.py"
        wrapper.write_text(WRAPPER, encoding="utf-8")
        r = subprocess.run([sys.executable, str(wrapper), str(HERE), str(HERE / script), mode, *map(str, args)],
                           capture_output=True, text=True, cwd=self.root, timeout=120)
        return r

    def callers(self):
        r, o = self.root, self.out
        return {
            "evidence_summary.py": ["--root", r, "--evidence", r / "evidence", "--output", o],
            "make_source_manifest.py": [o, "--root", r],
            "token_coverage.py": ["--root", r, "--samples-output", o, r / "evidence" / "run1" / "editor_raw.log"],
            "summarize_encounter_cost.py": [r / "receipt.json", "--report-json", o],
            "summarize_packaged_metrics.py": [r / "receipt.json", "--report-json", o],
        }


class Bk277InjectedReplaceFailure(Fixture):
    def test_old_bytes_intact_exit_1_traceback_no_temp(self):
        for script, args in self.callers().items():
            with self.subTest(script=script):
                r = self.run_caller(script, args, "fail")
                self.assertEqual(r.returncode, 1, r.stdout + r.stderr)
                self.assertIn("PermissionError: [Errno 13] synthetic replace failure", r.stderr)
                self.assertEqual(self.out.read_bytes(), OLD)       # prior destination untouched
                self.assertEqual(temps(self.root), [])             # atomic_io removed its temp


class Bk279NoFalseSuccessOnStdout(Fixture):
    # Lines each caller prints ONLY after a successful publication.
    SUCCESS_MARKERS = {
        "evidence_summary.py": "logs=",
        "make_source_manifest.py": "files=",
        "token_coverage.py": "sample_manifest=",
    }

    def test_publication_lines_absent_after_failure(self):
        for script, args in self.callers().items():
            with self.subTest(script=script):
                r = self.run_caller(script, args, "fail")
                marker = self.SUCCESS_MARKERS.get(script)
                if marker:
                    self.assertNotIn(marker, r.stdout)
                if script == "token_coverage.py":
                    # Pre-write summary IS printed (not a publication claim); exit 1 alone is ambiguous with
                    # "observed without schema", the traceback on stderr distinguishes it.
                    self.assertIn("logs_scanned=1 schemas=1 observed=1", r.stdout)
                elif script.startswith("summarize_"):
                    self.assertEqual(r.stdout, "")  # write precedes print on these paths (receipt is valid JSON)
                else:
                    self.assertEqual(r.stdout, "")

    def test_success_path_publishes_and_claims(self):
        expected_exit = {"summarize_encounter_cost.py": 2, "summarize_packaged_metrics.py": 2}  # {} -> INCONCLUSIVE
        for script, args in self.callers().items():
            with self.subTest(script=script):
                r = self.run_caller(script, args, "ok")
                self.assertEqual(r.returncode, expected_exit.get(script, 0), r.stdout + r.stderr)
                self.assertNotEqual(self.out.read_bytes(), OLD)    # replaced
                marker = self.SUCCESS_MARKERS.get(script)
                if marker:
                    self.assertIn(marker, r.stdout)
                if script.startswith("summarize_"):
                    self.assertEqual(json.loads(self.out.read_text(encoding="utf-8"))["status"], "INCONCLUSIVE")
                self.assertEqual(temps(self.root), [])


class Bk276OrderingContracts(unittest.TestCase):
    """Static: in every replace caller the publication line is printed after atomic_write_text."""

    def test_print_after_write(self):
        cases = {"evidence_summary.py": "logs=", "make_source_manifest.py": "files=",
                 "token_coverage.py": "sample_manifest="}
        for script, marker in cases.items():
            with self.subTest(script=script):
                lines = (HERE / script).read_text(encoding="utf-8").splitlines()
                write = max(i for i, l in enumerate(lines) if "atomic_write_text(" in l and "import" not in l)
                claim = next(i for i, l in enumerate(lines) if marker in l and "print(" in l)
                self.assertGreater(claim, write)


if __name__ == "__main__":
    unittest.main()
