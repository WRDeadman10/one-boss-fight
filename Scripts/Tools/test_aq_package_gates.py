"""Offline contracts for AQ Development-package evidence boundaries."""

from __future__ import annotations

import pathlib
import re
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[2]
GATES = re.sub(
    r"\s+",
    " ",
    (ROOT / "Documentation/Boss/AQ_C21_C25_PACKAGE_GATES.md").read_text(encoding="utf-8"),
).lower()
KNOWN = (ROOT / "Documentation/KNOWN_ISSUES.md").read_text(encoding="utf-8")


def issue_row(issue_id: str) -> str:
    match = re.search(rf"(?m)^- {re.escape(issue_id)} \(.*$", KNOWN)
    if match is None:
        raise AssertionError(f"missing {issue_id} row in KNOWN_ISSUES.md")
    return match.group(0)


class AqPackageGatesContract(unittest.TestCase):
    def test_all_four_known_issue_rows_retain_package_open_status(self):
        expected = {
            "KI-193": ("PARTIAL", "package proof remains open"),
            "KI-196": ("package open", "Proven in PIE"),
            "KI-198": ("package open", "Proven in PIE"),
            "KI-199": ("package open", "root cause not isolated"),
        }
        for issue_id, markers in expected.items():
            with self.subTest(issue_id=issue_id):
                row = issue_row(issue_id).lower()
                for marker in markers:
                    self.assertIn(marker.lower(), row)

    def test_gate_separates_pie_source_cook_and_package_evidence(self):
        text = GATES
        for marker in (
            "does not establish that a staged development package",
            "authoritative cooked/staged manifest",
            "native build, editor pie",
            "separate identified case",
            "never aggregate pie and package evidence",
        ):
            self.assertIn(marker, text)

    def test_camera_gate_is_conditional_on_owner_choice_and_combined_run(self):
        text = GATES
        self.assertIn("only after owner selection", text)
        self.assertIn("c-1090 result covers only that attack-mode case", text)
        self.assertIn("additional combined scenarios and package evidence remain open", text)
        self.assertIn("does not depend on development-only diagnostic", text)

    def test_package_records_build_and_artifact_identity(self):
        text = GATES
        for marker in (
            "uat command and arguments",
            "sha-256",
            "cooked content manifest/export",
            "complete uat cook/package logs",
            "wrong package identity",
            "development package acceptance does not imply shipping",
        ):
            self.assertIn(marker, text)

    def test_ki193_required_cook_list_path_exists(self):
        self.assertTrue((ROOT / "Scripts/Tools/er_tier2_required_cook_assets.txt").is_file())
        self.assertIn("scripts/tools/er_tier2_required_cook_assets.txt", GATES)


if __name__ == "__main__":
    unittest.main()
