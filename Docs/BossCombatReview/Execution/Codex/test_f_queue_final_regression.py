#!/usr/bin/env python3
"""Run the offline behavior and handoff-contract suites prepared for Queue F."""
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
SUITES = (
    "Docs/BossCombatReview/Execution/Codex/C2/test_receipt_schema.py",
    "Docs/BossCombatReview/Execution/Codex/C2/test_profile_success_contract.py",
    "Docs/BossCombatReview/Execution/Codex/C2/test_profile_preflight_failure_context.py",
    "Docs/BossCombatReview/Execution/Codex/C2/test_missing_selection_dispatch.py",
    "Docs/BossCombatReview/Execution/Codex/C2/test_anim_blueprint_compile_failure_context.py",
    "Docs/BossCombatReview/Execution/Codex/C2/test_dispatch_failure_propagation.py",
    "Docs/BossCombatReview/Execution/Codex/C3/test_c3_registration_validation.py",
    "Docs/BossCombatReview/Execution/Codex/C3/test_new_weapon_destination_preflight.py",
    "Docs/BossCombatReview/Execution/Codex/C3/test_c3_catalog_add.py",
    "Docs/BossCombatReview/Execution/Codex/C5/test_validate_weapon_inventory.py",
    "Docs/BossCombatReview/Execution/Antigravity/Reviews/test_validate_weapon_config.py",
    "Docs/BossCombatReview/Execution/Antigravity/Reviews/test_reopen_c5_weapon_data_audit.py",
    "Docs/BossCombatReview/Execution/Codex/test_f_ag_package_tokens.py",
    "Docs/BossCombatReview/Execution/Codex/test_f_ag_validator_acceptance.py",
    "Docs/BossCombatReview/Execution/Codex/test_f_ag_expected_sheet_lint.py",
    "Docs/BossCombatReview/Execution/Codex/test_f_cross_tool_docs.py",
)


class FQueueFinalRegressionTests(unittest.TestCase):
    def test_offline_queue_f_suites(self):
        for relative_path in SUITES:
            with self.subTest(suite=relative_path):
                result = subprocess.run(
                    [sys.executable, str(ROOT / relative_path)],
                    cwd=ROOT, capture_output=True, text=True, timeout=90,
                )
                self.assertEqual(
                    result.returncode, 0,
                    f"{relative_path} failed\nSTDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}",
                )


if __name__ == "__main__":
    unittest.main()
