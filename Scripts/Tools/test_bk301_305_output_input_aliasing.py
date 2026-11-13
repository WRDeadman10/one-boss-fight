"""BK-301..305 (C, implementer; X-2138): output-path aliasing against inputs for the five atomic_write_text callers.

Real CLI subprocesses on synthetic temp fixtures. Each case aims the output at one of the caller's own inputs - by
the same path or through a hard link - and checks exit/stdout/stderr and that the input bytes survive. No
production file, lock, pack, asset, Unreal, build or PIE.
"""
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
VALIDATOR_REL = Path("Docs/BossCombatReview/Execution/Antigravity/Reviews/validate_framework_proof_logs.py")


class Fixture(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)
        self.validator = self.root / VALIDATOR_REL
        self.validator.parent.mkdir(parents=True)
        self.validator.write_text('SCHEMAS = {"ProbeToken": {}}\n'
                                  'def validate_log_file(path):\n'
                                  '    return {"syntax_failures": [], "semantic_violations": []}\n', encoding="utf-8")
        self.log = self.root / "ev" / "run1" / "editor_raw.log"
        self.log.parent.mkdir(parents=True)
        self.log.write_text("[FrameworkProof] ProbeToken a=1\n", encoding="utf-8")
        self.source_file = self.root / "Source" / "a.cpp"
        self.source_file.parent.mkdir()
        self.source_file.write_text("int a;\n", encoding="utf-8")
        self.receipt = self.root / "receipt.json"
        self.receipt.write_text("{}", encoding="utf-8")

    def tearDown(self):
        self._tmp.cleanup()

    def cli(self, script, *args):
        return subprocess.run([sys.executable, str(HERE / script), *map(str, args)], capture_output=True, text=True,
                              cwd=self.root, timeout=120)

    def cases(self, out_for):
        """(script, args, victim input, expected stderr fragment) with the output aimed via out_for(victim)."""
        r = self.root
        return [
            ("summarize_encounter_cost.py", [self.receipt, "--report-json", out_for(self.receipt)], self.receipt,
             "INCONCLUSIVE: report destination aliases an evidence input"),
            ("summarize_packaged_metrics.py", [self.receipt, "--report-json", out_for(self.receipt)], self.receipt,
             "INCONCLUSIVE: report destination aliases an evidence input"),
            ("evidence_summary.py", ["--root", r, "--evidence", r / "ev", "--output", out_for(self.log)], self.log,
             "output aliases an input; refusing to overwrite it"),
            ("token_coverage.py", ["--root", r, "--samples-output", out_for(self.log), self.log], self.log,
             "--samples-output aliases an input; refusing to overwrite it"),
            ("make_source_manifest.py", [out_for(self.source_file), "--root", r], self.source_file,
             "output aliases a scanned Source file; refusing to overwrite it"),
        ]

    def assert_refused(self, script, args, victim, fragment):
        before = victim.read_bytes()
        result = self.cli(script, *args)
        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        self.assertIn(fragment, result.stderr)
        self.assertEqual(victim.read_bytes(), before, f"{script} destroyed its input")
        self.assertEqual(list(self.root.rglob("*.tmp")), [])
        return result


class Bk302To304SamePathAlias(Fixture):
    def test_output_equal_to_an_input_is_refused_and_input_survives(self):
        for script, args, victim, fragment in self.cases(lambda victim: victim):
            with self.subTest(script=script):
                result = self.assert_refused(script, args, victim, fragment)
                if script.startswith("summarize_"):
                    self.assertEqual(result.stdout, "")

    def test_validator_alias_is_refused_for_scanning_callers(self):
        r = self.root
        for script, args in (("evidence_summary.py", ["--root", r, "--evidence", r / "ev", "--output", self.validator]),
                             ("token_coverage.py", ["--root", r, "--samples-output", self.validator, self.log])):
            with self.subTest(script=script):
                self.assert_refused(script, args, self.validator, "aliases an input")


class Bk305HardLinkAlias(Fixture):
    def test_hard_link_to_an_input_is_refused(self):
        def link_to(victim):
            alias = self.root / f"alias_{victim.name}"
            if not alias.exists():
                os.link(victim, alias)
            return alias
        for script, args, victim, fragment in self.cases(link_to):
            with self.subTest(script=script):
                self.assert_refused(script, args, victim, fragment)


class Bk305NonAliasStillWorks(Fixture):
    def test_source_manifest_output_inside_source_is_refused_before_write(self):
        output = self.root / "Source" / "generated-manifest.txt"
        before = self.source_file.read_bytes()
        result = self.cli("make_source_manifest.py", output, "--root", self.root)
        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        self.assertIn("output must be outside the scanned Source directory", result.stderr)
        self.assertFalse(output.exists())
        self.assertEqual(self.source_file.read_bytes(), before)

    def test_separate_outputs_are_written(self):
        out = self.root / "out"
        out.mkdir()
        r = self.root
        runs = {
            "summarize_encounter_cost.py": ([self.receipt, "--report-json", out / "cost.json"], 2),
            "summarize_packaged_metrics.py": ([self.receipt, "--report-json", out / "metrics.json"], 2),
            "evidence_summary.py": (["--root", r, "--evidence", r / "ev", "--output", out / "summary.csv"], 0),
            "token_coverage.py": (["--root", r, "--samples-output", out / "samples.json", self.log], 0),
            "make_source_manifest.py": ([out / "manifest.txt", "--root", r], 0),
        }
        for script, (args, code) in runs.items():
            with self.subTest(script=script):
                result = self.cli(script, *args)
                self.assertEqual(result.returncode, code, result.stdout + result.stderr)
        self.assertEqual(sorted(p.name for p in out.iterdir()),
                         ["cost.json", "manifest.txt", "metrics.json", "samples.json", "summary.csv"])


if __name__ == "__main__":
    unittest.main()
