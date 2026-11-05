#!/usr/bin/env python3
"""Regression checks for cross-tool handoff documentation contracts."""
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]


class CrossToolDocumentationTests(unittest.TestCase):
    def test_c4_workflow_local_links_resolve(self):
        document = ROOT / "Documentation/Boss/C4_DESIGNER_WORKFLOW.md"
        self.assertTrue(document.is_file())
        links = re.findall(r"\[[^\]]+\]\(([^)]+)\)", document.read_text(encoding="utf-8"))
        local = [link for link in links if not link.startswith(("http://", "https://", "#", "mailto:"))]
        missing = [link for link in local if not (document.parent / link.split("#", 1)[0]).resolve().is_file()]
        self.assertTrue(local, "expected at least one local documentation/source link")
        self.assertEqual(missing, [])

    def test_c4_command_examples_match_current_runner_and_tool_switches(self):
        c4 = (ROOT / "Documentation/Boss/C4_DESIGNER_WORKFLOW.md").read_text(encoding="utf-8")
        f4 = (ROOT / "Docs/BossCombatReview/Execution/Claude/F4/run_pie.ps1").read_text(encoding="utf-8")
        c1 = (ROOT / "Docs/BossCombatReview/Execution/Claude/C1/new_boss.py").read_text(encoding="utf-8")
        c3 = (ROOT / "Docs/BossCombatReview/Execution/Claude/C3/new_weapon.py").read_text(encoding="utf-8")
        self.assertIn("-Map \"/Game/OneBossFight/FrameworkProof/<unique-map-name>\"", c4)
        self.assertIn("-OutDir \"C:\\UnrealProject\\OneBossFight\\Docs\\BossCombatReview\\Execution\\Claude\\F4\\runs\\<unique-run-name>\"", c4)
        self.assertIn("-Task \"F4_<unique-task-name>\"", c4)
        for switch in ("[Parameter(Mandatory=$true)][string]$Map", "[Parameter(Mandatory=$true)][string]$OutDir", "[Parameter(Mandatory=$true)][string]$Task"):
            self.assertIn(switch, f4)
        self.assertIn("--dry-run", c4)
        self.assertIn("--dry-run", c1)
        self.assertIn("without `--apply`", c4)
        self.assertIn("[--apply]", c3)

    def test_c4_preserves_no_overwrite_and_reference_safety_rules(self):
        c4 = (ROOT / "Documentation/Boss/C4_DESIGNER_WORKFLOW.md").read_text(encoding="utf-8").casefold()
        self.assertIn("use unique new destinations", c4)
        self.assertIn("refuses existing destinations", c4)
        self.assertIn("never overwrite or delete an existing referenced package", c4)
        self.assertIn("preserve partial outputs", c4)
        self.assertIn("no step suggests deleting a referenced package", c4)


if __name__ == "__main__":
    unittest.main()
