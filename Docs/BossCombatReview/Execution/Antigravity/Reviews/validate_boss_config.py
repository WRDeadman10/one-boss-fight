#!/usr/bin/env python3
# Copyright One Boss Fight. All Rights Reserved.
"""
validate_boss_config.py
=======================
Pure-Python offline configuration validator for new_boss.py (Track C1).
Zero engine dependency, zero unreal imports.

Mirrors the exact domain rules and validation failure tokens from:
- Source/OneBossFight/Player/RPGBossFrameworkProfile.cpp (lines 13-146)
- Source/OneBossFight/Player/RPGBossMoveCard.cpp (lines 10-140)

Checks:
1. Anti-overwrite gate (Framework.BossConfig.DestinationExists)
2. Identity requirements (Framework.Profile.Identity)
3. Locomotion, HitSweep, and Float domains (Framework.Profile.Domain)
4. Geometric inequalities (Framework.Profile.Geometry)
5. Alignment transform validity (Framework.Profile.Alignment)
6. Phase definitions & two-phase coherence (Framework.Profile.Phase, Framework.Profile.PhaseCards)
7. Posture coherent set rules (Framework.Profile.Posture)
8. Bleed coherent set rules (Framework.Profile.Bleed)
9. KI-149 Starvation prevention (Framework.Profile.PhaseCooldownStarvation)
10. Range band & blend tail coverage (Framework.Profile.CardBandOrBlendTail)
11. Damage card & total run survival budget (Framework.Profile.DamageCard, Framework.Profile.DamageBudget)
"""

import math
from typing import List, Dict, Any, Optional, Set

CEILING = 1.0e6


def phase_pool_cannot_starve(cooldowns: List[float], attack_count: int) -> bool:
    """
    Pure C++ mirror of RPGFramework::PhasePoolCannotStarve (RPGBossFrameworkProfile.cpp:13-18).
    Returns True if a pool of cards with these cooldowns can always offer a card
    on each of attack_count consecutive attacks.
    """
    if attack_count < 1:
        return False
    if len(cooldowns) >= attack_count:
        return True
    for c in cooldowns:
        if math.isfinite(c) and c <= 0.0:
            return True
    return False


def is_valid_number(val: Any, positive: bool = False, min_val: float = 0.0, max_val: float = CEILING) -> bool:
    """Helper to check finite float domain."""
    if val is None or isinstance(val, bool):
        return False
    try:
        fval = float(val)
    except (ValueError, TypeError):
        return False
    if not math.isfinite(fval):
        return False
    if positive and fval <= 0.0:
        return False
    if fval < min_val or fval > max_val:
        return False
    return True


def validate_boss_config(config: Dict[str, Any], existing_destinations: Optional[Set[str]] = None) -> List[str]:
    """
    Validates a complete boss configuration dictionary.
    Returns list of error tokens. Empty list indicates 100% valid config.
    """
    errors: List[str] = []

    # 1. Anti-Overwrite Check (Framework.BossConfig.DestinationExists)
    dest_dir = config.get("destination_package_dir", "")
    boss_name = config.get("boss_name", "")
    expected_profile_path = f"{dest_dir}/DA_{boss_name}_Profile"
    expected_level_path = f"{dest_dir}/L_{boss_name}FrameworkProof"

    if existing_destinations:
        if expected_profile_path in existing_destinations:
            errors.append(f"Framework.BossConfig.DestinationExists[{expected_profile_path}]")
        if expected_level_path in existing_destinations:
            errors.append(f"Framework.BossConfig.DestinationExists[{expected_level_path}]")

    # 2. Identity Check (Framework.Profile.Identity, RPGBossFrameworkProfile.cpp:24-27)
    fixture_label = config.get("fixture_label", "")
    b_f3 = (fixture_label == "F3 fixture")
    b_f4 = (fixture_label == "F4 fixture")
    b_f5 = (fixture_label == "F5 fixture")
    b_damage = bool(config.get("damage_enabled", False))

    mesh_path = config.get("mesh_path", "")
    anim_class_path = config.get("anim_class_path", "")
    target_pawn_class_path = config.get("target_pawn_class_path", "")

    cards = config.get("cards", [])
    single_card = config.get("card", None)

    identity_ok = True
    if not (b_f3 or b_f4 or b_f5):
        identity_ok = False
    if (b_f4 or b_f5) != b_damage:
        identity_ok = False
    if not mesh_path or not anim_class_path or not target_pawn_class_path:
        identity_ok = False
    if b_f5:
        if len(cards) < 1 or single_card is not None:
            identity_ok = False
    else:
        if single_card is None or len(cards) > 0:
            identity_ok = False

    if not identity_ok:
        errors.append("Framework.Profile.Identity")

    # 3. Hit Sweep Domain (Framework.Profile.Domain, lines 28-29)
    if b_damage:
        hit_step = config.get("hit_step_cm", 0.0)
        hit_substeps = config.get("hit_max_substeps", 0)
        if not is_valid_number(hit_step, positive=True, max_val=CEILING) or not isinstance(hit_substeps, int) or hit_substeps < 1 or hit_substeps > 64:
            errors.append("Framework.Profile.Domain[HitSweep]")

    # 4. Boss Health & Player Damage Domain (Framework.Profile.Domain, lines 30-32)
    boss_max_hp = float(config.get("boss_max_health", 0.0))
    player_hit_dmg = float(config.get("player_hit_damage", 0.0))
    if (boss_max_hp > 0.0) != (player_hit_dmg > 0.0):
        errors.append("Framework.Profile.Domain[BossHealthMismatch]")
    elif not math.isfinite(boss_max_hp) or not math.isfinite(player_hit_dmg) or boss_max_hp < 0.0 or player_hit_dmg < 0.0 or boss_max_hp > CEILING or player_hit_dmg > boss_max_hp:
        errors.append("Framework.Profile.Domain[BossHealthBounds]")

    # 5. Locomotion & Target Health Domain (Framework.Profile.Domain, lines 67-68)
    domain_fields = [
        "band_min_cm", "band_max_cm", "walk_speed_cm_per_second", "acceptance_cm",
        "walk_timeout_seconds", "blend_in_seconds", "blend_out_seconds",
        "capsule_radius_cm", "capsule_half_height_cm", "target_health"
    ]
    for df in domain_fields:
        if not is_valid_number(config.get(df), positive=True):
            errors.append(f"Framework.Profile.Domain[{df}]")

    # 6. Selector Domain (Framework.Profile.Domain, lines 61-66)
    if b_f5:
        repeat_penalty = config.get("repeat_penalty", 0.0)
        repeat_memory = config.get("repeat_memory", 0)
        attack_count = config.get("attack_count", 0)
        if not is_valid_number(repeat_penalty, positive=True, min_val=0.0001, max_val=1.0) or not isinstance(repeat_memory, int) or repeat_memory < 1 or repeat_memory > 8 or not isinstance(attack_count, int) or attack_count < 1 or attack_count > 8:
            errors.append("Framework.Profile.Domain[Selector]")

        for i, c in enumerate(cards):
            c_card = c.get("spec", c.get("card", c.get("spec_path", None)))
            cd = c.get("cooldown_seconds", 0.0)
            wt = c.get("weight", 0.0)
            if c_card is None or not is_valid_number(cd, min_val=0.0, max_val=CEILING) or not is_valid_number(wt, positive=True, max_val=CEILING):
                errors.append(f"Framework.Profile.Domain[Cards[{i}]]")

    # 7. Geometry Domain (Framework.Profile.Geometry, lines 69-70)
    b_min = float(config.get("band_min_cm", 0.0))
    b_max = float(config.get("band_max_cm", 0.0))
    acc = float(config.get("acceptance_cm", 0.0))
    c_rad = float(config.get("capsule_radius_cm", 0.0))
    c_half = float(config.get("capsule_half_height_cm", 0.0))

    if not (b_min < b_max and acc < (b_max - b_min) * 0.5 and c_rad <= c_half):
        errors.append("Framework.Profile.Geometry")

    # 8. Alignment Check (Framework.Profile.Alignment, lines 71-73)
    if not config.get("alignment_authored", False):
        errors.append("Framework.Profile.Alignment[Unauthored]")
    else:
        tf = config.get("mesh_relative_transform", {})
        scale = tf.get("scale", [0.0, 0.0, 0.0])
        loc = tf.get("location", [0.0, 0.0, 0.0])
        if (len(scale) != 3 or min(scale) <= 0.0 or max(map(abs, scale)) > CEILING or
            len(loc) != 3 or max(map(abs, loc)) > CEILING or
            any(not math.isfinite(x) for x in scale + loc)):
            errors.append("Framework.Profile.Alignment[Transform]")

    # 9. Phase Rules (Framework.Profile.Phase, lines 34-36)
    p2_frac = float(config.get("phase_two_fraction", 0.0))
    p2_id = config.get("phase_two_id", "")
    if p2_frac != 0.0 or (p2_id and p2_id != "None"):
        if not b_f5 or boss_max_hp <= 0.0 or not math.isfinite(p2_frac) or p2_frac <= 0.0 or p2_frac >= 1.0 or not p2_id or p2_id == "None":
            errors.append("Framework.Profile.Phase")

    # 10. Posture Rules (Framework.Profile.Posture, lines 38-46)
    posture_vals = [
        config.get("posture_max", 0.0),
        config.get("player_posture_hit_amount", 0.0),
        config.get("stagger_seconds", 0.0),
        config.get("posture_regen_delay_seconds", 0.0),
        config.get("posture_regen_per_second", 0.0),
    ]
    if any(v != 0.0 for v in posture_vals):
        p_ok = b_f5 and boss_max_hp > 0.0
        for v in posture_vals:
            p_ok = p_ok and is_valid_number(v, min_val=0.0, max_val=CEILING)
        p_ok = p_ok and (posture_vals[0] > 0.0) and (posture_vals[1] > 0.0) and (posture_vals[1] <= posture_vals[0]) and (0.5 <= posture_vals[2] <= 60.0)
        if not p_ok:
            errors.append("Framework.Profile.Posture")

    # 11. Bleed Rules (Framework.Profile.Bleed, lines 49-57)
    bleed_vals = [
        config.get("bleed_buildup_per_hit", 0.0),
        config.get("bleed_initial_threshold", 0.0),
        config.get("bleed_threshold_increase", 0.0),
        config.get("bleed_threshold_max", 0.0),
        config.get("bleed_hp_fraction", 0.0),
    ]
    if any(v != 0.0 for v in bleed_vals):
        b_ok = b_f5 and boss_max_hp > 0.0
        for v in bleed_vals:
            b_ok = b_ok and is_valid_number(v, min_val=0.0, max_val=CEILING)
        b_ok = b_ok and (bleed_vals[0] > 0.0) and (bleed_vals[1] >= 1.0) and (bleed_vals[3] >= bleed_vals[1]) and (0.0 < bleed_vals[4] <= 1.0)
        if not b_ok:
            errors.append("Framework.Profile.Bleed")

    # 12. Resolved Cards Cross-Checks (RPGBossFrameworkProfile.cpp:87-130)
    target_health = float(config.get("target_health", 0.0))
    blend_in = float(config.get("blend_in_seconds", 0.0))
    blend_out = float(config.get("blend_out_seconds", 0.0))
    attack_count = int(config.get("attack_count", 1)) if b_f5 else 1

    active_cards = cards if b_f5 else ([{"spec": single_card, "cooldown_seconds": 0.0, "weight": 1.0}] if single_card else [])

    worst_hit = 0.0
    phase_pools: Dict[str, List[float]] = {}

    for i, c_entry in enumerate(active_cards):
        spec = c_entry.get("spec", {})
        hp_dmg = float(spec.get("HPDamage", 0.0))
        c_min_range = float(spec.get("MinRangeCm", 0.0))
        c_max_range = float(spec.get("MaxRangeCm", 0.0))
        act_start = float(spec.get("ActiveStartSeconds", 0.0))
        rec_end = float(spec.get("RecoveryEndSeconds", 0.0))
        clip_len = float(spec.get("ClipLengthSeconds", 0.0))
        phase_id = str(spec.get("PhaseId", ""))
        cd = float(c_entry.get("cooldown_seconds", 0.0))

        worst_hit = max(worst_hit, hp_dmg)

        # Damage Card check (lines 95-96)
        if b_damage:
            if not (hp_dmg > 0.0 and hp_dmg < target_health):
                errors.append(f"Framework.Profile.DamageCard[Card[{i}]]")
        else:
            if hp_dmg != 0.0:
                errors.append(f"Framework.Profile.SequenceTelemetryOnly[Card[{i}]]")

        # Blend timing check (line 92)
        if act_start <= blend_in or rec_end + blend_out > CEILING:
            errors.append(f"Framework.Profile.SequenceTelemetryOnly[BlendTiming[{i}]]")

        # Card Band & Blend Tail (lines 103-104)
        if b_min < c_min_range or b_max > c_max_range or rec_end + blend_out > clip_len:
            errors.append(f"Framework.Profile.CardBandOrBlendTail[Card[{i}]]")

        # Group into phase pools
        if phase_id:
            phase_pools.setdefault(phase_id, []).append(cd)

    # Damage budget across total attack run (line 128)
    if b_f5 and worst_hit * attack_count >= target_health:
        errors.append("Framework.Profile.DamageBudget")

    # Phase Cards & Cooldown Starvation Check (lines 118-126)
    if b_f5 and p2_frac > 0.0:
        if len(active_cards) > 0:
            first_card_phase = str(active_cards[0].get("spec", {}).get("PhaseId", ""))
            in_one = sum(1 for c in active_cards if str(c.get("spec", {}).get("PhaseId", "")) == first_card_phase)
            in_two = sum(1 for c in active_cards if str(c.get("spec", {}).get("PhaseId", "")) == p2_id)
            other_phases = [str(c.get("spec", {}).get("PhaseId", "")) for c in active_cards if str(c.get("spec", {}).get("PhaseId", "")) not in (first_card_phase, p2_id)]

            if first_card_phase == p2_id or in_one < 1 or in_two < 1 or len(other_phases) > 0:
                errors.append("Framework.Profile.PhaseCards")
            else:
                pool_one = phase_pools.get(first_card_phase, [])
                pool_two = phase_pools.get(p2_id, [])
                if not phase_pool_cannot_starve(pool_one, attack_count) or not phase_pool_cannot_starve(pool_two, attack_count):
                    errors.append("Framework.Profile.PhaseCooldownStarvation")

    return errors
