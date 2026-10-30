#!/usr/bin/env python3
"""
validate_ki149_tier1.py
Pure offline validation rule for KI-149 Tier 1 (Preflight Phase Cooldown Starvation Guard).

Authority: Lead Order [C-434] / A-320; KI149_COOLDOWN_EXHAUSTION_DESIGN.md.
C++ Target Hook: RPGBossFrameworkProfile.cpp (alongside PhaseCards validation in RPGFramework::ResolveProfile).

Invariant Rule:
  For each phase present in the boss profile (Phase 1, Phase 2, etc.):
    ZeroCooldownCount >= 1  OR  PhaseCardinality >= AttackCount

  If neither condition holds for any phase:
    Reject preflight with token: 'Framework.Profile.PhaseCooldownStarvation'

Rationale:
  During an N-attack burst (AttackCount = N), an agent cannot be starved of selectable
  candidates by cooldowns if either:
    (a) At least one candidate in the phase has CooldownSeconds <= 0.0 (baseline 0-cd filler), OR
    (b) The phase pool contains at least N distinct cards (cardinality >= N), ensuring distinct
        choices exist across all consecutive attacks even under non-zero cooldowns.
"""

from typing import List, Dict, Any, Tuple, Optional


TOKEN_COOLDOWN_STARVATION = "Framework.Profile.PhaseCooldownStarvation"
TOKEN_EMPTY_CARDS = "Framework.Profile.EmptyCards"
TOKEN_INVALID_ATTACK_COUNT = "Framework.Profile.InvalidAttackCount"
TOKEN_PHASE_CARDS = "Framework.Profile.PhaseCards"


def validate_phase_deck_cardinality(
    cards: List[Dict[str, Any]],
    attack_count: int,
    phase_two_fraction: float = 0.0,
    phase_two_id: str = "Phase_2",
    default_phase_id: str = "Phase_1",
) -> Tuple[bool, str, Dict[str, Any]]:
    """
    Validates a boss profile deck against KI-149 cooldown starvation.

    Args:
        cards: List of card dicts, each containing at least:
               - 'MoveId' or 'CardId' (str)
               - 'CooldownSeconds' (float)
               - Optional 'PhaseId' (str, defaults to default_phase_id)
        attack_count: Authored burst attack count (P->AttackCount, int >= 1)
        phase_two_fraction: HP fraction threshold (float). If > 0.0, validates both phases.
        phase_two_id: Name of Phase 2 (P->PhaseTwoId, str)
        default_phase_id: Name of Phase 1 (str, defaults to 'Phase_1')

    Returns:
        (b_valid, error_token, diagnostic_report)
    """
    diagnostics: Dict[str, Any] = {
        "attack_count": attack_count,
        "phase_two_fraction": phase_two_fraction,
        "phase_two_id": phase_two_id,
        "default_phase_id": default_phase_id,
        "phases": {},
        "violating_phases": [],
    }

    if not cards:
        return False, TOKEN_EMPTY_CARDS, diagnostics

    if attack_count < 1:
        return False, TOKEN_INVALID_ATTACK_COUNT, diagnostics

    # Partition cards by PhaseId
    first_phase = cards[0].get("PhaseId", default_phase_id) or default_phase_id

    # If phased, establish expected phase set
    if phase_two_fraction > 0.0:
        expected_phases = [first_phase, phase_two_id]
        if first_phase == phase_two_id:
            return False, TOKEN_PHASE_CARDS, diagnostics
    else:
        # Collect distinct phases present
        distinct_phases = []
        for c in cards:
            pid = c.get("PhaseId", default_phase_id) or default_phase_id
            if pid not in distinct_phases:
                distinct_phases.append(pid)
        expected_phases = distinct_phases if distinct_phases else [default_phase_id]

    for phase in expected_phases:
        phase_cards = [
            c for c in cards
            if (c.get("PhaseId", default_phase_id) or default_phase_id) == phase
        ]
        cardinality = len(phase_cards)
        zero_cd_cards = [
            c for c in phase_cards
            if float(c.get("CooldownSeconds", 0.0)) <= 0.0
        ]
        zero_cd_count = len(zero_cd_cards)

        # Rule Invariant: zero_cd_count >= 1 OR cardinality >= attack_count
        b_phase_valid = (zero_cd_count >= 1) or (cardinality >= attack_count)

        phase_report = {
            "cardinality": cardinality,
            "zero_cooldown_count": zero_cd_count,
            "attack_count": attack_count,
            "satisfies_zero_cd_rule": zero_cd_count >= 1,
            "satisfies_cardinality_rule": cardinality >= attack_count,
            "is_valid": b_phase_valid,
            "card_ids": [c.get("MoveId") or c.get("CardId") or "Unknown" for c in phase_cards],
        }
        diagnostics["phases"][phase] = phase_report

        if not b_phase_valid:
            diagnostics["violating_phases"].append(phase)

    if diagnostics["violating_phases"]:
        return False, TOKEN_COOLDOWN_STARVATION, diagnostics

    return True, "", diagnostics


if __name__ == "__main__":
    import json
    import sys

    # Quick demo on standard 2-card vs 3-card deck
    sample_cards = [
        {"MoveId": "Move_SwingSlow", "PhaseId": "Phase_1", "CooldownSeconds": 1.0},
        {"MoveId": "Move_SwingMedium", "PhaseId": "Phase_1", "CooldownSeconds": 1.0},
    ]
    ok, err, rep = validate_phase_deck_cardinality(sample_cards, attack_count=3)
    print(f"AttackCount=3, 2 cards (cd=1.0): Valid={ok}, Error={err}")
    assert not ok and err == TOKEN_COOLDOWN_STARVATION
    print("Self-check passed.")
