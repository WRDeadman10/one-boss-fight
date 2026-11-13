"""BK-291..295 (C, implementer; X-2132): the five atomic_write_text callers under EARLY temp-stage faults
(os.fsync PermissionError; os.fdopen failure after the temp descriptor exists), as real subprocesses.

The runpy wrapper installs the fault before the script runs. For fdopen it records every descriptor it was handed
and, at interpreter exit (atexit runs after an uncaught traceback), prints FDCHECK lines stating whether each fd
is still open (os.fstat). Synthetic temp fixtures only; no production data, lock, pack, asset, Unreal, build or PIE.
"""
import json
import re
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
    import atexit, os, runpy, sys
    tools, script, mode = sys.argv[1], sys.argv[2], sys.argv[3]
    sys.path.insert(0, tools)
    handed = []
    if mode == "fsync":
        def fsync(fd):
            raise PermissionError(13, "synthetic fsync failure")
        os.fsync = fsync
    elif mode == "fdopen":
        def fdopen(fd, *args, **kwargs):
            handed.append(fd)
            raise OSError("synthetic fdopen failure")
        os.fdopen = fdopen
        def report():
            for fd in handed:
                try:
                    os.fstat(fd)
                    state = "OPEN"
                except OSError:
                    state = "closed"
                sys.stderr.write(f"FDCHECK fd={fd} {state}\\n")
        atexit.register(report)
    sys.argv = [script] + sys.argv[4:]
    runpy.run_path(script, run_name="__main__")
""")

CLAIM_MARKERS = {"evidence_summary.py": "logs=", "make_source_manifest.py": "files=",
                 "token_coverage.py": "sample_manifest="}


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
        (self.root / "evidence" / "run1").mkdir(parents=True)
        (self.root / "evidence" / "run1" / "editor_raw.log").write_text("[FrameworkProof] ProbeToken a=1\n",
                                                                         encoding="utf-8")
        (self.root / "Source").mkdir()
        (self.root / "Source" / "a.cpp").write_text("int a;\n", encoding="utf-8")
        (self.root / "receipt.json").write_text("{}", encoding="utf-8")
        self.out = self.root / "out" / "result.txt"
        self.out.parent.mkdir()
        self.wrapper = self.root / "wrapper.py"
        self.wrapper.write_text(WRAPPER, encoding="utf-8")

    def tearDown(self):
        self._tmp.cleanup()

    def callers(self):
        r, o = self.root, self.out
        return {
            "evidence_summary.py": ["--root", r, "--evidence", r / "evidence", "--output", o],
            "make_source_manifest.py": [o, "--root", r],
            "token_coverage.py": ["--root", r, "--samples-output", o, r / "evidence" / "run1" / "editor_raw.log"],
            "summarize_encounter_cost.py": [r / "receipt.json", "--report-json", o],
            "summarize_packaged_metrics.py": [r / "receipt.json", "--report-json", o],
        }

    def run_caller(self, script, args, mode):
        self.out.write_bytes(OLD)
        return subprocess.run([sys.executable, str(self.wrapper), str(HERE), str(HERE / script), mode,
                               *map(str, args)], capture_output=True, text=True, cwd=self.root, timeout=120)

    def assert_fail_closed(self, script, r, expected_error):
        self.assertEqual(r.returncode, 1, r.stdout + r.stderr)
        self.assertIn("Traceback (most recent call last)", r.stderr)
        self.assertIn(expected_error, r.stderr)
        self.assertEqual(self.out.read_bytes(), OLD)                      # previous destination intact
        self.assertEqual(temps(self.root), [])                            # temp removed
        marker = CLAIM_MARKERS.get(script)
        if marker:
            self.assertNotIn(marker, r.stdout)                            # BK-293: no publication claim
        if script == "token_coverage.py":
            self.assertIn("logs_scanned=1 schemas=1 observed=1", r.stdout)  # pre-write scan summary only
        else:
            self.assertEqual(r.stdout, "")


class Bk291FsyncFailure(Fixture):
    def test_fsync_permission_error_all_five(self):
        for script, args in self.callers().items():
            with self.subTest(script=script):
                r = self.run_caller(script, args, "fsync")
                self.assert_fail_closed(script, r, "PermissionError: [Errno 13] synthetic fsync failure")


class Bk292FdopenFailure(Fixture):
    def test_fdopen_failure_closes_descriptor_and_cleans_all_five(self):
        for script, args in self.callers().items():
            with self.subTest(script=script):
                r = self.run_caller(script, args, "fdopen")
                self.assert_fail_closed(script, r, "OSError: synthetic fdopen failure")
                checks = re.findall(r"FDCHECK fd=(\d+) (\w+)", r.stderr)
                self.assertEqual(len(checks), 1, r.stderr)                # exactly one temp descriptor handed
                self.assertEqual(checks[0][1], "closed", "atomic_io must close the unwrapped temp descriptor")


class Bk293ClaimMarkers(unittest.TestCase):
    def test_claim_lines_are_printed_after_the_write_in_source(self):
        for script, marker in CLAIM_MARKERS.items():
            with self.subTest(script=script):
                lines = (HERE / script).read_text(encoding="utf-8").splitlines()
                write = max(i for i, l in enumerate(lines) if "atomic_write_text(" in l and "import" not in l)
                claim = next(i for i, l in enumerate(lines) if marker in l and "print(" in l)
                self.assertGreater(claim, write)

    def test_token_coverage_summary_precedes_write_and_is_not_a_publication_marker(self):
        lines = (HERE / "token_coverage.py").read_text(encoding="utf-8").splitlines()
        summary = next(i for i, l in enumerate(lines) if 'print(f"logs_scanned=' in l)
        write = next(i for i, l in enumerate(lines) if "atomic_write_text(output" in l)
        self.assertLess(summary, write)
        self.assertNotIn("sample_manifest", lines[summary])


class Bk294ContractParity(unittest.TestCase):
    """atomic_io's documented failure contract (module docstring) vs what the callers observably get."""

    def test_contract_text_covers_the_observed_guarantees(self):
        doc = (HERE / "atomic_io.py").read_text(encoding="utf-8").split('"""')[1]
        for phrase in ("ORIGINAL exception propagates", "old content kept", "temp sibling is removed", "fdopen"):
            self.assertIn(phrase, doc)


if __name__ == "__main__":
    unittest.main()
