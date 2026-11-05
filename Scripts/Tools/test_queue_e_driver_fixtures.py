"""Offline source-contract fixtures for the D84-D88 audit findings.

These checks read maintained source and the generated ID index. They never
invoke PowerShell, Unreal, the editor bridge, or process operations.
"""
import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def read_project_file(relative_path):
    return (ROOT / relative_path).read_text(encoding="utf-8", errors="replace")


class QueueEDriverFixtures(unittest.TestCase):
    def test_e61_automation_id_index_has_unique_registered_ids(self):
        index = read_project_file("Documentation/Boss/AUTOMATION_TEST_ID_INDEX_D84.md")
        ids = re.findall(r"^\| `([^`]+)` \|", index, flags=re.MULTILINE)
        self.assertTrue(ids, "expected automation-ID rows in the D84 index")
        self.assertEqual(len(ids), len(set(ids)), "duplicate IDs in generated index")
        source = read_project_file("Scripts/Tools/list_automation_tests.py")
        self.assertIn("IMPLEMENT_(?:SIMPLE_)?AUTOMATION_TEST", source)

    def test_e62_benchmark_timeout_is_bounded_and_cleans_owned_tree(self):
        source = read_project_file("Scripts/RunBenchmark.ps1")
        self.assertRegex(source, r"ValidateRange\(1,\s*7200\).*TimeoutSeconds")
        self.assertRegex(source, r"WaitForExit\(\$TimeoutSeconds\s*\*\s*1000\)")
        self.assertRegex(source, r"taskkill\.exe\s+/PID\s+\$Process\.Id\s+/T\s+/F")

    def test_e63_experiment_sampler_cleanup_is_in_finally(self):
        source = read_project_file("Scripts/RunPerfExperiments.ps1")
        match = re.search(r"(?ms)^\s*try\s*\{(?P<body>.*?)^\s*finally\s*\{(?P<cleanup>.*?)^\s*\}", source)
        self.assertIsNotNone(match, "benchmark invocation needs a finally cleanup block")
        self.assertIn("& powershell @rargs", match.group("body"))
        self.assertIn("Stop-Process -Id $smi.Id", match.group("cleanup"))

    def test_e64_editor_runner_exits_nonzero_for_noncompleted_task(self):
        source = read_project_file("Scripts/run_in_editor.py")
        self.assertIn("task_result", source)
        self.assertRegex(source, r"(?i)(failed|error|cancelled)")
        self.assertRegex(source, r"sys\.exit\(1\)|raise SystemExit\(1\)")

    def test_e65_benchmark_collection_checks_archive_and_copy_failure_policy(self):
        source = read_project_file("Scripts/BenchKit_Collect.ps1")
        self.assertIn("$ErrorActionPreference = 'Stop'", source)
        self.assertRegex(source, r"(?i)archive was not created")
        self.assertIn("$archive.Entries.Count -eq 0", source)
        self.assertRegex(source, r"(?i)Run folders: \$n")


if __name__ == "__main__":
    unittest.main()
