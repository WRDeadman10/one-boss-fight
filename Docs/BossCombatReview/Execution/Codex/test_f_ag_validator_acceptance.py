#!/usr/bin/env python3
"""Validate the lead-accepted F-AG5 raw logs with the production log validator."""
import json
import re
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT / "Docs/BossCombatReview/Execution/Antigravity/Reviews"))
import validate_framework_proof_logs as validator


class FAgValidatorAcceptanceTests(unittest.TestCase):
    def test_all_four_closing_mov001_runs_validate_and_match_their_range_case(self):
        evidence = ROOT / "Docs/BossCombatReview/Execution/Claude/B_FAG5_MOV001"
        cases = (
            ("Melee100", "Move_Sevarog_Melee_FAG5", "102.87"),
            ("Close250", "Move_Sevarog_Close_FAG5", "254.76"),
            ("Medium375", "Move_Sevarog_BandMedium_MOV001", "380.00"),
            ("Gap700", "Move_Sevarog_BandGap_MOV001", "701.92"),
        )
        for name, expected_card, expected_range in cases:
            with self.subTest(case=name):
                run_dir = evidence / name
                raw_log = run_dir / "editor_raw.log"
                result_path = run_dir / "result.json"
                self.assertTrue(raw_log.is_file(), f"Missing raw log: {raw_log}")
                self.assertTrue(result_path.is_file(), f"Missing runner result: {result_path}")
                result = json.loads(result_path.read_text(encoding="utf-8"))
                self.assertEqual(result.get("exit_code"), 0)
                self.assertFalse(result.get("timed_out"))

                validation = validator.validate_log_file(raw_log)
                self.assertEqual(validation["syntax_failures"], [])
                self.assertEqual(validation["semantic_violations"], [])
                log = raw_log.read_text(encoding="utf-8", errors="replace")
                decisions = re.findall(r"\[FrameworkProof\] decision [^\r\n]*chosen=([^\s]+)[^\r\n]*range=([0-9.]+)", log)
                self.assertTrue(decisions, "Missing parseable FrameworkProof decision")
                self.assertIn(expected_card, [card for card, _ in decisions])
                selected_range = next(float(distance) for card, distance in decisions if card == expected_card)
                self.assertAlmostEqual(selected_range, float(expected_range), delta=0.5)
                self.assertIn("[FrameworkProof] RESULT outcome=CompletedWithDamage", log)


if __name__ == "__main__":
    unittest.main()
