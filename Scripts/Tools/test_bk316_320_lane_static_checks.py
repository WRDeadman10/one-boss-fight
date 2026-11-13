"""BK-316..320 (C, implementer; X-2151): static closeout checks for lane BK-271..320.

317: in each of the five report writers, the output-alias guard appears before every atomic_write_text call.
318: every lane test file (BK-271..315) builds its fixtures in tempfile.TemporaryDirectory and contains no hard-coded
absolute path or project output location. Source-only: nothing is executed or written.
"""
import ast
import re
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
LANE_TESTS = sorted(p for p in HERE.glob("test_bk*.py")
                    if (m := re.match(r"test_bk(\d+)_(\d+)_", p.name)) and 271 <= int(m.group(1)) <= 311)

GUARDS = {
    "summarize_encounter_cost.py": "output_aliases(args.report_json, [args.receipt])",
    "summarize_packaged_metrics.py": "aliases_evidence = report_path in evidence_paths",
    "evidence_summary.py": "output_aliases(output, [*logs, root / VALIDATOR_REL])",
    "token_coverage.py": "output_aliases(output, [*logs, validator])",
    "make_source_manifest.py": "output_aliases(args.output, scanned)",
}
FORBIDDEN_LITERALS = re.compile(r"^(?:[A-Za-z]:[\\/]|/c/|/Users/|\\\\)|UnrealProject|OneBossFight|\.uasset$|^Saved[\\/]|"
                                r"^Content[\\/]|^Documentation[\\/]")


class Bk317GuardBeforeWrite(unittest.TestCase):
    def test_guard_precedes_every_write(self):
        for script, guard in GUARDS.items():
            with self.subTest(script=script):
                lines = (HERE / script).read_text(encoding="utf-8").splitlines()
                guard_at = [i for i, l in enumerate(lines) if guard in l]
                writes = [i for i, l in enumerate(lines) if "atomic_write_text(" in l and "import" not in l]
                self.assertEqual(len(guard_at), 1, script)
                self.assertTrue(writes, script)
                self.assertLess(guard_at[0], min(writes), f"{script}: guard must precede every write")

    def test_manifest_source_containment_precedes_write(self):
        lines = (HERE / "make_source_manifest.py").read_text(encoding="utf-8").splitlines()
        contain = next(i for i, l in enumerate(lines) if "is_relative_to(source.resolve())" in l)
        write = next(i for i, l in enumerate(lines) if "atomic_write_text(" in l and "import" not in l)
        self.assertLess(contain, write)


class Bk318FixtureContainment(unittest.TestCase):
    def test_lane_has_nine_test_files(self):
        self.assertEqual(len(LANE_TESTS), 9, [p.name for p in LANE_TESTS])

    def test_every_lane_test_uses_temporary_directories(self):
        for path in LANE_TESTS:
            with self.subTest(test=path.name):
                self.assertIn("tempfile.TemporaryDirectory(", path.read_text(encoding="utf-8"))

    def test_no_hard_coded_absolute_or_project_output_paths(self):
        for path in LANE_TESTS:
            with self.subTest(test=path.name):
                tree = ast.parse(path.read_text(encoding="utf-8"))
                bad = [node.value for node in ast.walk(tree)
                       if isinstance(node, ast.Constant) and isinstance(node.value, str)
                       and FORBIDDEN_LITERALS.search(node.value)]
                self.assertEqual(bad, [])


if __name__ == "__main__":
    unittest.main()
