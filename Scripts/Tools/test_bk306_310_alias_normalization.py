"""BK-306..310 (C, implementer; X-2143): path-normalisation coverage of the five report writers' output-vs-input
alias guards (relative/absolute, ./ and .. segments, Windows case and 8.3/long spellings, symlinks) plus the
make_source_manifest Source-subtree refusal. Real CLI subprocesses (cwd = fixture root) on temp-only fixtures; no
project output, lock, pack, asset, Unreal, build or PIE.
"""
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
VALIDATOR_REL = Path("Docs/BossCombatReview/Execution/Antigravity/Reviews/validate_framework_proof_logs.py")


def symlink_reason():
    with tempfile.TemporaryDirectory() as tmp:
        target = Path(tmp) / "t"
        target.write_text("x")
        try:
            os.symlink(target, Path(tmp) / "l")
            return None
        except (OSError, NotImplementedError) as error:
            return f"host cannot create symlinks: {error!r}"


SYMLINK_SKIP = symlink_reason()


def swapcase_path(rel):
    return os.sep.join(part.swapcase() for part in Path(rel).parts)


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

    def spellings(self, victim):
        rel = os.path.relpath(victim, self.root)
        first = Path(rel).parts[0]
        out = {
            "absolute": str(victim),
            "relative": rel,
            "dot": os.path.join(".", rel),
            "dotdot": os.path.join(first, "..", rel),
            "long_realpath": os.path.realpath(victim),
        }
        if os.name == "nt":
            out["case_swapped"] = swapcase_path(rel)
        return out

    def writers(self, out):
        """(script, args, victim, refusal fragment) with the output spelled as `out` for its victim."""
        return [
            ("summarize_encounter_cost.py", ["receipt.json", "--report-json", out(self.receipt)], self.receipt,
             "aliases an evidence input"),
            ("summarize_packaged_metrics.py", ["receipt.json", "--report-json", out(self.receipt)], self.receipt,
             "aliases an evidence input"),
            ("evidence_summary.py", ["--root", ".", "--evidence", "ev", "--output", out(self.log)], self.log,
             "aliases an input"),
            ("token_coverage.py", ["--root", ".", "--samples-output", out(self.log), str(self.log)], self.log,
             "aliases an input"),
            ("make_source_manifest.py", [out(self.source_file), "--root", "."], self.source_file,
             "Source"),
        ]

    def assert_refused(self, script, args, victim, fragment, label):
        before = victim.read_bytes()
        result = self.cli(script, *args)
        self.assertEqual(result.returncode, 2, f"{label}: {result.stdout}{result.stderr}")
        self.assertIn(fragment, result.stderr, label)
        self.assertEqual(victim.read_bytes(), before, f"{script} [{label}] destroyed its input")
        self.assertEqual(list(self.root.rglob("*.tmp")), [], label)


class Bk307SpellingVariants(Fixture):
    def test_every_spelling_of_an_input_is_refused_for_all_five(self):
        names = list(self.spellings(self.receipt))
        for name in names:
            for script, args, victim, fragment in self.writers(lambda v, n=name: self.spellings(v)[n]):
                with self.subTest(spelling=name, script=script):
                    self.assert_refused(script, args, victim, fragment, name)


@unittest.skipIf(SYMLINK_SKIP, SYMLINK_SKIP or "")
class Bk308SymlinkAlias(Fixture):
    def test_symlink_to_an_input_is_refused_and_input_preserved(self):
        def link(victim):
            alias = self.root / f"link_{victim.name}"
            if not alias.exists():
                os.symlink(victim, alias)
            return str(alias)
        for script, args, victim, fragment in self.writers(link):
            with self.subTest(script=script):
                self.assert_refused(script, args, victim, fragment, "symlink")


class Bk309SourceSubtreeAndValidOutputs(Fixture):
    def test_new_manifest_under_source_is_refused_in_any_spelling(self):
        spellings = {"relative": os.path.join("Source", "new.txt"),
                     "dotdot": os.path.join("Source", "..", "Source", "sub", "new.txt"),
                     "absolute": str(self.root / "Source" / "new.txt")}
        if os.name == "nt":
            spellings["case_swapped"] = os.path.join("sOURCE", "new.txt")
        for name, spelling in spellings.items():
            with self.subTest(spelling=name):
                result = self.cli("make_source_manifest.py", spelling, "--root", ".")
                self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
                self.assertIn("output must be outside the scanned Source directory", result.stderr)
                self.assertEqual(sorted(p.name for p in (self.root / "Source").rglob("*")), ["a.cpp"])

    def test_ordinary_outputs_in_relative_and_dotted_spellings_are_written(self):
        (self.root / "out").mkdir()
        runs = {
            "summarize_encounter_cost.py": (["receipt.json", "--report-json", "./out/cost.json"], 2),
            "summarize_packaged_metrics.py": (["receipt.json", "--report-json", "out/../out/metrics.json"], 2),
            "evidence_summary.py": (["--root", ".", "--evidence", "ev", "--output", "out/summary.csv"], 0),
            "token_coverage.py": (["--root", ".", "--samples-output", "./out/samples.json", str(self.log)], 0),
            "make_source_manifest.py": (["out/manifest.txt", "--root", "."], 0),
            # a sibling whose name merely STARTS with "Source" is outside the Source directory
            "make_source_manifest.py#sibling": (["SourceManifest.txt", "--root", "."], 0),
        }
        for key, (args, code) in runs.items():
            with self.subTest(case=key):
                result = self.cli(key.split("#")[0], *args)
                self.assertEqual(result.returncode, code, result.stdout + result.stderr)
        self.assertEqual(sorted(p.name for p in (self.root / "out").iterdir()),
                         ["cost.json", "manifest.txt", "metrics.json", "samples.json", "summary.csv"])
        self.assertTrue((self.root / "SourceManifest.txt").is_file())


if __name__ == "__main__":
    unittest.main()
