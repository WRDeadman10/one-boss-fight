"""BO-46 (C, implementer; per X-2270): checks for run_bo_lane_tests.py. It does not run the full lane, which would recurse."""
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
sys.path.insert(0, str(HERE))
import run_bo_lane_tests as runner  # noqa: E402


def run(*args):
    return subprocess.run([sys.executable, str(HERE / "run_bo_lane_tests.py"), *args], capture_output=True, text=True, timeout=300)


class LaneRunner(unittest.TestCase):
    def test_every_listed_suite_exists(self):
        for name in runner.all_suites():
            with self.subTest(name=name):
                rel = Path(*name.split(".")).with_suffix(".py") if name.startswith("Scripts.") else Path(name + ".py")
                base = REPO if name.startswith("Scripts.") else HERE
                self.assertTrue((base / rel).is_file(), f"missing suite file for {name}")

    def test_every_bo_suite_file_is_listed(self):
        on_disk = {p.stem for p in HERE.glob("test_bo_*.py")}
        self.assertEqual(on_disk - set(runner.BO_SUITES), set(), "a new test_bo_* suite must be added to the runner")

    def test_only_one_suite_passes(self):
        r = run("--only", "test_bo_json_inputs")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertRegex(r.stdout, r"OK\s+test_bo_json_inputs\s+\d+ tests")
        self.assertIn("suites=1 ", r.stdout)
        self.assertIn("failing=0", r.stdout)

    def test_package_suite_runs_from_repo_root(self):
        r = run("--only", "Scripts.Tools.test_summarize_framework_log")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)

    def test_unknown_suite_is_a_usage_error(self):
        r = run("--only", "test_no_such_suite")
        self.assertEqual(r.returncode, 2)
        self.assertIn("unknown suite", r.stderr)

    def test_failing_suite_makes_the_runner_fail(self):
        with tempfile.TemporaryDirectory(dir=HERE) as tmp:
            name = Path(tmp).name
            bad = HERE / f"test_zz_bo_runner_probe_{name}.py"
            bad.write_text("import unittest\nclass T(unittest.TestCase):\n    def test_fail(self):\n        self.fail('probe')\n",
                           encoding="utf-8")
            try:
                row = runner.run_suite(bad.stem, timeout=120)
            finally:
                bad.unlink()
        self.assertEqual(row["status"], "FAIL")
        self.assertEqual(row["tests"], 1)

    def test_list(self):
        r = run("--list")
        self.assertEqual(r.returncode, 0)
        self.assertEqual(r.stdout.split(), runner.all_suites())


if __name__ == "__main__":
    unittest.main()
