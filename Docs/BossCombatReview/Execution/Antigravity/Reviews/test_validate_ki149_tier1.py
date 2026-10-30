#!/usr/bin/env python3
"""
test_validate_ki149_tier1.py
Comprehensive unit test suite for KI-149 Tier 1 Preflight Phase Cooldown Starvation Guard.

Verifies:
  1. Starvation rejection when cardinality < AttackCount and no 0-cooldown filler exists.
  2. Acceptance when zero-cooldown filler exists (zero_cd >= 1) even if cardinality < AttackCount.
  3. Acceptance when cardinality >= AttackCount even if all cards have positive cooldowns.
  4. Multi-phase profiles (Phase 1 vs Phase 2 isolation and independent guard evaluation).
  5. Exact reproduction of the F6c / KI-149 failure scenario.
  6. Edge cases (AttackCount=1, negative cooldowns, empty decks, invalid attack counts).
"""

import unittest
from pathlib import Path
import sys

# Ensure module import from local directory
current_dir = Path(__file__).resolve().parent
if str(current_dir) not in sys.path:
    sys.path.insert(0, str(current_dir))

from validate_ki149_tier1 import (
    validate_phase_deck_cardinality,
    TOKEN_COOLDOWN_STARVATION,
    TOKEN_EMPTY_CARDS,
    TOKEN_INVALID_ATTACK_COUNT,
    TOKEN_PHASE_CARDS,
)


class TestValidateKI149Tier1(unittest.TestCase):
    """Test suite for validate_phase_deck_cardinality."""

    def test_01_two_cards_attack_count_three_starvation(self):
        """2 cards with positive cooldowns and AttackCount=3 must REJECT (KI-149 root cause)."""
        cards = [
            {"MoveId": "Move_SwingSlow", "PhaseId": "Phase_1", "CooldownSeconds": 1.0},
            {"MoveId": "Move_SwingMedium", "PhaseId": "Phase_1", "CooldownSeconds": 1.0},
        ]
        valid, token, diag = validate_phase_deck_cardinality(cards, attack_count=3)
        self.assertFalse(valid)
        self.assertEqual(token, TOKEN_COOLDOWN_STARVATION)
        self.assertIn("Phase_1", diag["violating_phases"])
        self.assertEqual(diag["phases"]["Phase_1"]["cardinality"], 2)
        self.assertEqual(diag["phases"]["Phase_1"]["zero_cooldown_count"], 0)

    def test_02_zero_cd_filler_allows_low_cardinality(self):
        """2 cards where one has CooldownSeconds=0.0 must PASS even with AttackCount=3."""
        cards = [
            {"MoveId": "Move_SwingSlow", "PhaseId": "Phase_1", "CooldownSeconds": 1.0},
            {"MoveId": "Move_SwingFiller", "PhaseId": "Phase_1", "CooldownSeconds": 0.0},
        ]
        valid, token, diag = validate_phase_deck_cardinality(cards, attack_count=3)
        self.assertTrue(valid)
        self.assertEqual(token, "")
        self.assertEqual(diag["phases"]["Phase_1"]["zero_cooldown_count"], 1)
        self.assertTrue(diag["phases"]["Phase_1"]["satisfies_zero_cd_rule"])

    def test_03_cardinality_equals_attack_count_passes(self):
        """3 cards with positive cooldowns and AttackCount=3 must PASS (cardinality >= AttackCount)."""
        cards = [
            {"MoveId": "Move_SwingSlow", "PhaseId": "Phase_1", "CooldownSeconds": 1.0},
            {"MoveId": "Move_SwingMedium", "PhaseId": "Phase_1", "CooldownSeconds": 1.0},
            {"MoveId": "Move_HeavySlam", "PhaseId": "Phase_1", "CooldownSeconds": 1.0},
        ]
        valid, token, diag = validate_phase_deck_cardinality(cards, attack_count=3)
        self.assertTrue(valid)
        self.assertEqual(token, "")
        self.assertTrue(diag["phases"]["Phase_1"]["satisfies_cardinality_rule"])

    def test_04_cardinality_greater_than_attack_count_passes(self):
        """4 cards with positive cooldowns and AttackCount=3 must PASS."""
        cards = [
            {"MoveId": "Move_A", "PhaseId": "Phase_1", "CooldownSeconds": 2.0},
            {"MoveId": "Move_B", "PhaseId": "Phase_1", "CooldownSeconds": 2.0},
            {"MoveId": "Move_C", "PhaseId": "Phase_1", "CooldownSeconds": 2.0},
            {"MoveId": "Move_D", "PhaseId": "Phase_1", "CooldownSeconds": 2.0},
        ]
        valid, token, diag = validate_phase_deck_cardinality(cards, attack_count=3)
        self.assertTrue(valid)
        self.assertEqual(token, "")

    def test_05_phased_both_phases_satisfy_cardinality(self):
        """Phased profile where Phase 1 has 3 cards and Phase 2 has 3 cards must PASS."""
        cards = [
            {"MoveId": "P1_A", "PhaseId": "Phase_1", "CooldownSeconds": 1.0},
            {"MoveId": "P1_B", "PhaseId": "Phase_1", "CooldownSeconds": 1.0},
            {"MoveId": "P1_C", "PhaseId": "Phase_1", "CooldownSeconds": 1.0},
            {"MoveId": "P2_A", "PhaseId": "Phase_2", "CooldownSeconds": 1.0},
            {"MoveId": "P2_B", "PhaseId": "Phase_2", "CooldownSeconds": 1.0},
            {"MoveId": "P2_C", "PhaseId": "Phase_2", "CooldownSeconds": 1.0},
        ]
        valid, token, diag = validate_phase_deck_cardinality(
            cards, attack_count=3, phase_two_fraction=0.5, phase_two_id="Phase_2"
        )
        self.assertTrue(valid)
        self.assertEqual(token, "")
        self.assertEqual(len(diag["violating_phases"]), 0)

    def test_06_phased_phase_two_starvation_rejected(self):
        """Phased profile where Phase 1 has 3 cards but Phase 2 has 2 cards must REJECT on Phase 2."""
        cards = [
            {"MoveId": "P1_A", "PhaseId": "Phase_1", "CooldownSeconds": 1.0},
            {"MoveId": "P1_B", "PhaseId": "Phase_1", "CooldownSeconds": 1.0},
            {"MoveId": "P1_C", "PhaseId": "Phase_1", "CooldownSeconds": 1.0},
            {"MoveId": "P2_A", "PhaseId": "Phase_2", "CooldownSeconds": 1.0},
            {"MoveId": "P2_B", "PhaseId": "Phase_2", "CooldownSeconds": 1.0},
        ]
        valid, token, diag = validate_phase_deck_cardinality(
            cards, attack_count=3, phase_two_fraction=0.5, phase_two_id="Phase_2"
        )
        self.assertFalse(valid)
        self.assertEqual(token, TOKEN_COOLDOWN_STARVATION)
        self.assertEqual(diag["violating_phases"], ["Phase_2"])
        self.assertTrue(diag["phases"]["Phase_1"]["is_valid"])
        self.assertFalse(diag["phases"]["Phase_2"]["is_valid"])

    def test_07_phased_phase_one_starvation_rejected(self):
        """Phased profile where Phase 1 has 2 cards and Phase 2 has 3 cards must REJECT on Phase 1."""
        cards = [
            {"MoveId": "P1_A", "PhaseId": "Phase_1", "CooldownSeconds": 1.0},
            {"MoveId": "P1_B", "PhaseId": "Phase_1", "CooldownSeconds": 1.0},
            {"MoveId": "P2_A", "PhaseId": "Phase_2", "CooldownSeconds": 1.0},
            {"MoveId": "P2_B", "PhaseId": "Phase_2", "CooldownSeconds": 1.0},
            {"MoveId": "P2_C", "PhaseId": "Phase_2", "CooldownSeconds": 1.0},
        ]
        valid, token, diag = validate_phase_deck_cardinality(
            cards, attack_count=3, phase_two_fraction=0.5, phase_two_id="Phase_2"
        )
        self.assertFalse(valid)
        self.assertEqual(token, TOKEN_COOLDOWN_STARVATION)
        self.assertEqual(diag["violating_phases"], ["Phase_1"])
        self.assertFalse(diag["phases"]["Phase_1"]["is_valid"])
        self.assertTrue(diag["phases"]["Phase_2"]["is_valid"])

    def test_08_phased_phase_two_zero_filler_passes(self):
        """Phased profile where Phase 2 has 2 cards but one has 0-cd filler must PASS."""
        cards = [
            {"MoveId": "P1_A", "PhaseId": "Phase_1", "CooldownSeconds": 1.0},
            {"MoveId": "P1_B", "PhaseId": "Phase_1", "CooldownSeconds": 1.0},
            {"MoveId": "P1_C", "PhaseId": "Phase_1", "CooldownSeconds": 1.0},
            {"MoveId": "P2_A", "PhaseId": "Phase_2", "CooldownSeconds": 1.0},
            {"MoveId": "P2_Filler", "PhaseId": "Phase_2", "CooldownSeconds": 0.0},
        ]
        valid, token, diag = validate_phase_deck_cardinality(
            cards, attack_count=3, phase_two_fraction=0.5, phase_two_id="Phase_2"
        )
        self.assertTrue(valid)
        self.assertEqual(token, "")

    def test_09_negative_cooldown_treated_as_zero(self):
        """Negative cooldown (<= 0.0) is treated as non-gated filler and passes."""
        cards = [
            {"MoveId": "Move_A", "PhaseId": "Phase_1", "CooldownSeconds": 1.5},
            {"MoveId": "Move_B", "PhaseId": "Phase_1", "CooldownSeconds": -0.1},
        ]
        valid, token, diag = validate_phase_deck_cardinality(cards, attack_count=3)
        self.assertTrue(valid)
        self.assertEqual(token, "")
        self.assertEqual(diag["phases"]["Phase_1"]["zero_cooldown_count"], 1)

    def test_10_attack_count_one_always_passes_single_card(self):
        """When AttackCount=1, a single card with positive cooldown passes (cardinality 1 >= 1)."""
        cards = [
            {"MoveId": "Move_A", "PhaseId": "Phase_1", "CooldownSeconds": 5.0},
        ]
        valid, token, diag = validate_phase_deck_cardinality(cards, attack_count=1)
        self.assertTrue(valid)
        self.assertEqual(token, "")

    def test_11_empty_cards_rejected(self):
        """Empty card list returns Framework.Profile.EmptyCards."""
        valid, token, _ = validate_phase_deck_cardinality([], attack_count=3)
        self.assertFalse(valid)
        self.assertEqual(token, TOKEN_EMPTY_CARDS)

    def test_12_invalid_attack_count_rejected(self):
        """Attack count < 1 returns Framework.Profile.InvalidAttackCount."""
        cards = [{"MoveId": "Move_A", "CooldownSeconds": 1.0}]
        valid, token, _ = validate_phase_deck_cardinality(cards, attack_count=0)
        self.assertFalse(valid)
        self.assertEqual(token, TOKEN_INVALID_ATTACK_COUNT)

    def test_13_exact_f6c_fixture_reproduction(self):
        """
        Exact F6c baseline profile test:
        Phase 1: SwingSlow (cd=1.0), SwingMedium (cd=1.0)
        Phase 2: SwingMedium_P2 (cd=1.0), AntiGreed_P2 (cd=1.0)
        AttackCount = 3
        Both phases have cardinality=2 < 3 and zero_cd=0 -> Both violate and reject!
        """
        f6c_cards = [
            {"MoveId": "Move_Sevarog_SwingSlow", "PhaseId": "Phase_1", "CooldownSeconds": 1.0},
            {"MoveId": "Move_Sevarog_SwingMedium", "PhaseId": "Phase_1", "CooldownSeconds": 1.0},
            {"MoveId": "Move_Sevarog_SwingMedium_F7_P2", "PhaseId": "Phase_2", "CooldownSeconds": 1.0},
            {"MoveId": "Move_Sevarog_AntiGreed_F7_P2", "PhaseId": "Phase_2", "CooldownSeconds": 1.0},
        ]
        valid, token, diag = validate_phase_deck_cardinality(
            f6c_cards, attack_count=3, phase_two_fraction=0.5, phase_two_id="Phase_2"
        )
        self.assertFalse(valid)
        self.assertEqual(token, TOKEN_COOLDOWN_STARVATION)
        self.assertEqual(sorted(diag["violating_phases"]), ["Phase_1", "Phase_2"])


if __name__ == "__main__":
    unittest.main()
