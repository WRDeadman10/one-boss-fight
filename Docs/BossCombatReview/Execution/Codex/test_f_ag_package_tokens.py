#!/usr/bin/env python3
"""Verify F-AG expected sheets only require registered FrameworkProof tokens."""
import re
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
REVIEWS = ROOT / "Docs/BossCombatReview/Execution/Antigravity/Reviews"
sys.path.insert(0, str(REVIEWS))
import validate_framework_proof_logs as validator


class FAgPackageTokenTests(unittest.TestCase):
    def test_expected_package_tokens_are_registered_and_accept_sample_payloads(self):
        codex = ROOT / "Docs/BossCombatReview/Execution/Codex"
        expected_files = (
            codex / "F_AG2_AG3_COM004_EXPECTED.md",
            codex / "F_AG4_HIT008_BLOCK_EXPECTED.md",
            codex / "F_AG5_MOV001_EXPECTED.md",
        )
        token_lines = {}
        for path in expected_files:
            self.assertTrue(path.is_file(), f"Missing expected sheet: {path}")
            text = path.read_text(encoding="utf-8")
            for token in re.findall(r"\[FrameworkProof\]\s+([A-Za-z][A-Za-z0-9_]*)", text):
                token_lines.setdefault(token, []).append(path.name)

        samples = {
            "guard_hook_armed": "mode=3 seconds=12",
            "guard_tags": "since=0.1 statusBlocking=1 stateBlocking=1 abilityParry=0 abilityBlock=0",
            "guard_state": "instance=1 window=Hit guard=Guarded outcome=ERPGDamageOutcome::Accepted",
            "parry_press": "n=1 t=0.1 opened=1 windowSeconds=0.25",
            "parry_reaction": "posture=0",
            "combo_gate": "gate=1 node=A outcome=Guarded range=100 yaw=0 result=Continue next=D reason=",
            "combo_step": "node=D move=Move_Sevarog_HeavySlam_F7 depth=2",
            "RESULT": "outcome=CompletedWithDamage acceptedHits=1 attacks=1",
            "guard_chip": "incoming=80 applied=20",
            "hit": "instance=1 window=Hit key=Hit outcome=ERPGDamageOutcome::Accepted hpApplied=20 healthBefore=800 healthAfter=780",
            "candidate": "attack=1 card=Move_Sevarog_Melee_FAG5 score=1",
            "refusal": "attack=1 card=Move_Sevarog_BandGap_MOV001 reason=MoveModel.Range",
            "decision": "attack=1 chosen=Move_Sevarog_Melee_FAG5 score=1 range=100",
        }
        self.assertEqual(set(token_lines), set(samples), "Update this test when an expected sheet adds/removes package tokens")
        for token, payload in samples.items():
            with self.subTest(token=token):
                self.assertIn(token, validator.SCHEMAS, f"{token} in {token_lines[token]} has no registered schema")
                valid, parsed_token, _, error = validator.validate_line(f"[FrameworkProof] {token} {payload}")
                self.assertTrue(valid, f"{token} sample rejected: {error}")
                self.assertEqual(parsed_token, token)


if __name__ == "__main__":
    unittest.main()
