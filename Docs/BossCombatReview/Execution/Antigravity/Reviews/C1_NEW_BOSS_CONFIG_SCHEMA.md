# C1: `new_boss.py` Configuration Schema & Validation Specification

**Author:** Antigravity (Pair Programming Agent)  
**Lead / Reviewer:** Claude (Boss Combat Lead)  
**Date:** 2026-10-31  
**Task Order:** `[C-468]` (Track C1: Python-First `new_boss.py` Config Schema & Offline Validator)  
**Status:** DELIVERED (Schema Specification, Pure-Python Validator & Test Harness)  

---

## 1. Overview & Purpose

Following Lead Claude's architectural direction in `[C-468]`, Track C1 adopts a **Python-first editor utility** architecture for creating new framework-compliant bosses:
- **`new_boss.py <config.json>`**: A thin, deterministic wrapper executed via Unreal Editor (`-ExecutePythonScript`) wrapping existing proven authoring components (`create_*_content.py` patterns, `bake_blade_path.py`, `author_move_cards.py`, `create_proof_level.py`).
- **`validate_boss_config.py`**: A 100% offline, pure-Python preflight validator with **zero engine dependency** that verifies the input configuration against all C++ domain rules, asset requirements, and safety gates before touching the Unreal Editor.

This document defines:
1. The formal JSON Configuration Schema for `new_boss.py`.
2. Exact mapping between schema fields, domain constraints, and C++ validation failure tokens in `RPGBossFrameworkProfile.cpp` and `RPGBossMoveCard.cpp`.
3. The baseline positive configuration (Sevarog F10 equivalent proof).
4. 10 negative test scenarios demonstrating exact rejection tokens.

---

## 2. Complete Configuration Schema

A complete configuration file represents a single boss definition and proof map harness in JSON format:

```json
{
  "boss_name": "Sevarog",
  "destination_package_dir": "/Game/OneBossFight/FrameworkProof",
  "fixture_label": "F5 fixture",
  "damage_enabled": true,
  "mesh_path": "/Game/ParagonSevarog/Characters/Heroes/Sevarog/Meshes/Sevarog.Sevarog",
  "anim_class_path": "/Game/ParagonSevarog/Characters/Heroes/Sevarog/Sevarog_AnimBlueprint.Sevarog_AnimBlueprint_C",
  "target_pawn_class_path": "/Game/AdvancedARPGCombat/MeleeCombatSystem/Blueprints/BP_CombatPlayerCharacter.BP_CombatPlayerCharacter_C",
  "band_min_cm": 150.0,
  "band_max_cm": 180.0,
  "walk_speed_cm_per_second": 180.0,
  "acceptance_cm": 5.0,
  "walk_timeout_seconds": 10.0,
  "blend_in_seconds": 0.1,
  "blend_out_seconds": 0.04,
  "capsule_radius_cm": 60.0,
  "capsule_half_height_cm": 165.0,
  "target_health": 800.0,
  "hit_step_cm": 15.0,
  "hit_max_substeps": 8,
  "repeat_penalty": 0.2,
  "repeat_memory": 2,
  "attack_count": 2,
  "boss_max_health": 1000.0,
  "player_hit_damage": 100.0,
  "phase_two_fraction": 0.5,
  "phase_two_id": "Phase_Two",
  "posture_max": 100.0,
  "player_posture_hit_amount": 25.0,
  "stagger_seconds": 3.0,
  "posture_regen_delay_seconds": 5.0,
  "posture_regen_per_second": 10.0,
  "bleed_buildup_per_hit": 25.0,
  "bleed_initial_threshold": 100.0,
  "bleed_threshold_increase": 50.0,
  "bleed_threshold_max": 300.0,
  "bleed_hp_fraction": 0.15,
  "alignment_authored": true,
  "mesh_relative_transform": {
    "location": [0.0, 0.0, -165.0],
    "rotation": [0.0, 0.0, -90.0],
    "scale": [1.0, 1.0, 1.0]
  },
  "cards": [
    {"move_id": "Move_Sevarog_SwingSlow_F7_R2", "cooldown_seconds": 3.0, "weight": 1.0},
    {"move_id": "Move_Sevarog_AntiGreed_F7_R2", "cooldown_seconds": 2.5, "weight": 1.0},
    {"move_id": "Move_Sevarog_SwingMedium_F7_P2_R2", "cooldown_seconds": 0.8, "weight": 1.0},
    {"move_id": "Move_Sevarog_AntiGreed_F7_P2_R2", "cooldown_seconds": 1.8, "weight": 1.0}
  ],
  "proof_level": {
    "level_name": "L_SevarogFrameworkProofF10",
    "boss_spawn_location": [500.0, 0.0, 170.0],
    "player_start_location": [0.0, 0.0, 100.0]
  },
  "pie_driver": {
    "task_name": "PIE_Sevarog_F10_Proof",
    "timeout_seconds": 240,
    "flags": ["-Restart", "-DiagLong", "-RealBuild Dex", "-RealSwing 0.0:Light,1.0:Light"]
  }
}
```

---

### Card Asset Resolution Architecture
> [!NOTE]
> In the authored `config.json`, the `cards` array lists existing, authored move card assets by `move_id`, along with selector tuning (`cooldown_seconds`, `weight`).
> `new_boss.py` (lines 65-88) loads each card asset from `<destination_package_dir>/Cards/<move_id>`, reads its native `URPGBossMoveCardSpec` properties (`MoveId`, `PhaseId`, `MinRangeCm`, `MaxRangeCm`, `ActiveStartSeconds`, `RecoveryEndSeconds`, `HPDamage`), queries the animation sequence asset for `ClipLengthSeconds`, and populates an internal `spec` dictionary on each card entry.
> `validate_boss_config.py` runs on this **resolved configuration**, verifying ranges, tails, phase pools, and damage budgets against the resolved animation data.

## 3. Field & Validation Token Mapping

| Category | Field Name | Type / Format | C++ Reference & Failure Token | Exact Rule Enforced |
| :--- | :--- | :--- | :--- | :--- |
| **Safety** | `destination_package_dir` | String path | `Framework.BossConfig.DestinationExists` | Preflight check: refuses if target Profile (`DA_<boss>_Profile`) or Proof Level (`L_<boss>FrameworkProof`) already exist on disk (cards are reused, not overwritten). |
| **Identity**| `fixture_label` | `"F3 fixture"` \| `"F4 fixture"` \| `"F5 fixture"` | `RPGBossFrameworkProfile.cpp:24-27`<br>`Framework.Profile.Identity` | Declares fixture capability tier. |
| **Identity**| `damage_enabled` | Boolean | `RPGBossFrameworkProfile.cpp:25`<br>`Framework.Profile.Identity` | Must equal `true` for F4/F5; `false` for F3. |
| **Identity**| `mesh_path`, `anim_class_path`, `target_pawn_class_path` | Soft asset paths | `RPGBossFrameworkProfile.cpp:25`<br>`Framework.Profile.Identity` | Non-empty asset references. |
| **Identity**| `cards` vs `card` | Array vs Object | `RPGBossFrameworkProfile.cpp:26`<br>`Framework.Profile.Identity` | F5 requires `cards.length >= 1` and `card == null`. F3/F4 require `card != null` and `cards.length == 0`. |
| **Sweep** | `hit_step_cm`, `hit_max_substeps` | Float, Int | `RPGBossFrameworkProfile.cpp:28-29`<br>`Framework.Profile.Domain` | If `damage_enabled`: $0 < \text{hit\_step} \le 10^6$ and $\text{substeps} \in [1, 64]$. |
| **Boss HP** | `boss_max_health`, `player_hit_damage` | Float, Float | `RPGBossFrameworkProfile.cpp:30-32`<br>`Framework.Profile.Domain` | Both $0.0$ (unhittable) OR both $> 0.0$; $\text{player\_hit\_damage} \le \text{boss\_max\_health}$. |
| **Geometry**| `band_min_cm`, `band_max_cm`, `acceptance_cm`, `capsule_radius_cm`, `capsule_half_height_cm` | Floats | `RPGBossFrameworkProfile.cpp:69-70`<br>`Framework.Profile.Geometry` | $\text{BandMin} < \text{BandMax}$, $\text{Acceptance} < 0.5 \times (\text{BandMax} - \text{BandMin})$, $\text{Radius} \le \text{HalfHeight}$. |
| **Alignment**| `alignment_authored`, `mesh_relative_transform` | Bool, Object | `RPGBossFrameworkProfile.cpp:71-73`<br>`Framework.Profile.Alignment` | `alignment_authored == true`, scale min $> 0$, coordinates finite $\le 10^6$, no NaNs. |
| **Phases** | `phase_two_fraction`, `phase_two_id` | Float, FName | `RPGBossFrameworkProfile.cpp:34-36`<br>`Framework.Profile.Phase` | If fraction $\ne 0$ or ID $\ne \text{None}$: requires F5, hittable boss, fraction $\in (0, 1)$, ID valid. |
| **Posture** | `posture_max`, `player_posture_hit_amount`, `stagger_seconds`, `posture_regen_delay_seconds`, `posture_regen_per_second` | 5 Floats | `RPGBossFrameworkProfile.cpp:38-46`<br>`Framework.Profile.Posture` | All 5 zero (off) OR coherent set: F5, hittable boss, $\text{hit\_amount} \le \text{posture\_max}$, $\text{stagger} \in [0.5, 60.0]$. |
| **Bleed** | `bleed_buildup_per_hit`, `bleed_initial_threshold`, `bleed_threshold_increase`, `bleed_threshold_max`, `bleed_hp_fraction` | 5 Floats | `RPGBossFrameworkProfile.cpp:49-57`<br>`Framework.Profile.Bleed` | All 5 zero (off) OR coherent set: F5, hittable boss, $\text{initial} \ge 1.0$, $\text{max} \ge \text{initial}$, $\text{fraction} \in (0, 1]$. |
| **Selector**| `repeat_penalty`, `repeat_memory`, `attack_count` | Float, Int, Int | `RPGBossFrameworkProfile.cpp:61-62`<br>`Framework.Profile.Domain` | Penalty $\in (0, 1]$, memory $\in [1, 8]$, attack count $\in [1, 8]$. |
| **Starvation**| `PhasePoolCannotStarve` | Evaluated across card cooldowns | `RPGBossFrameworkProfile.cpp:13-18, 125`<br>`Framework.Profile.PhaseCooldownStarvation` | KI-149 Starvation Rule: each phase pool must offer a card on every attack ($\text{pool.len} \ge \text{AttackCount}$ or any $\text{cooldown} \le 0$). |
| **Card Band**| `MinRangeCm`, `MaxRangeCm`, `RecoveryEndSeconds`, `ClipLengthSeconds` | Card Spec Floats | `RPGBossFrameworkProfile.cpp:103-104`<br>`Framework.Profile.CardBandOrBlendTail` | For every card: $\text{BandMin} \ge \text{Card.MinRange}$, $\text{BandMax} \le \text{Card.MaxRange}$, and $\text{RecoveryEnd} + \text{BlendOut} \le \text{ClipLength}$. |
| **Phase Cards**| `PhaseId` across cards | Card Spec FNames | `RPGBossFrameworkProfile.cpp:118-122`<br>`Framework.Profile.PhaseCards` | When Phase Two active: Phase 1 $\ne$ Phase 2, every card belongs to Phase 1 or 2, both phases have $\ge 1$ card. |
| **Damage Budget**| Card `HPDamage` vs `TargetHealth` | Card Spec Floats | `RPGBossFrameworkProfile.cpp:128`<br>`Framework.Profile.DamageBudget` | $\max(\text{Card.HPDamage}) \times \text{AttackCount} < \text{TargetHealth}$. Target dummy must survive run. |

---

## 4. 10 Negative Failure Scenarios & Exact Failure Tokens

The offline test harness [`test_validate_boss_config.py`](file:///C:/UnrealProject/OneBossFight/Docs/BossCombatReview/Execution/Antigravity/Reviews/test_validate_boss_config.py) tests and enforces 10 distinct failure modes:

### Scenario 1: Unsafe Overwrite Attempt
- **Fault**: Generated asset already exists in `existing_destinations` set.
- **Expected Token**: `Framework.BossConfig.DestinationExists[/Game/OneBossFight/FrameworkProof/DA_Sevarog_Profile]`
- **Defense**: Prevents accidental asset stomping.

### Scenario 2: Identity Mismatch (Empty F5 Cards)
- **Fault**: `fixture_label = "F5 fixture"`, but `cards = []`.
- **Expected Token**: `Framework.Profile.Identity`
- **Defense**: Enforces F5 selector contract (`Cards.Num() >= 1 && Card.IsNull()`).

### Scenario 3: Inverted Combat Band
- **Fault**: `band_min_cm = 200.0`, `band_max_cm = 100.0`.
- **Expected Token**: `Framework.Profile.Geometry`
- **Defense**: Enforces $\text{BandMin} < \text{BandMax}$.

### Scenario 4: Acceptance Greater Than Half Band Thickness
- **Fault**: $\text{Band} = [150, 180]$ (thickness $30\text{ cm}$), but `acceptance_cm = 25.0` (exceeds $15\text{ cm}$).
- **Expected Token**: `Framework.Profile.Geometry`
- **Defense**: Enforces $\text{AcceptanceCm} < 0.5 \times (\text{BandMax} - \text{BandMin})$ to prevent arrival oscillation.

### Scenario 5: Unauthored Mesh Alignment
- **Fault**: `alignment_authored = false`.
- **Expected Token**: `Framework.Profile.Alignment[Unauthored]`
- **Defense**: Forces explicit designer acknowledgement of character coordinate frame alignment.

### Scenario 6: Incoherent Posture Tuning
- **Fault**: `posture_max = 0.0`, but `player_posture_hit_amount = 25.0`.
- **Expected Token**: `Framework.Profile.Posture`
- **Defense**: Posture values must all be zero (off) or a strictly coherent positive set.

### Scenario 7: Incoherent Bleed Tuning
- **Fault**: `bleed_initial_threshold = 0.5` (below $1.0\text{ hit}$ minimum).
- **Expected Token**: `Framework.Profile.Bleed`
- **Defense**: Initial hemorrhage threshold must require $\ge 1.0$ hit buildup.

### Scenario 8: Combat Band Outside Card Envelope
- **Fault**: `band_min_cm = 80.0`, but Card 0 `MinRangeCm = 100.0`.
- **Expected Token**: `Framework.Profile.CardBandOrBlendTail[Card[0]]`
- **Defense**: Prevents boss closing to a distance where the selected card cannot reach.

### Scenario 9: Phase Two Declared But Uncovered by Cards
- **Fault**: `phase_two_fraction = 0.5`, `phase_two_id = "Phase_Three_Uncovered"`, with no cards tagged with that Phase ID.
- **Expected Token**: `Framework.Profile.PhaseCards`
- **Defense**: Guarantees that phase transition will not leave the selector with an empty pool.

### Scenario 10: KI-149 Cooldown Starvation
- **Fault**: `attack_count = 3`, but Phase Two has only 2 cards with positive cooldowns ($2.5\text{ s}$ and $3.5\text{ s}$).
- **Expected Token**: `Framework.Profile.PhaseCooldownStarvation`
- **Defense**: Invariant proof that the selector can never starve on consecutive attacks in any phase.

---

## 5. Offline Test Results

The pure-Python test harness passes 11/11 checks (1 positive baseline + 10 negative rejection scenarios):

```
=== Running test_validate_boss_config.py ===
[PASS] Test 1: Positive Baseline (Sevarog F10 equivalent) -> 0 errors
[PASS] Negative 1: Framework.BossConfig.DestinationExists detected
[PASS] Negative 2: Framework.Profile.Identity detected (empty F5 cards)
[PASS] Negative 3: Framework.Profile.Geometry detected (BandMin >= BandMax)
[PASS] Negative 4: Framework.Profile.Geometry detected (Acceptance >= half thickness)
[PASS] Negative 5: Framework.Profile.Alignment detected (Unauthored)
[PASS] Negative 6: Framework.Profile.Posture detected (Incoherent posture)
[PASS] Negative 7: Framework.Profile.Bleed detected (Initial threshold < 1.0)
[PASS] Negative 8: Framework.Profile.CardBandOrBlendTail detected (BandMin < CardMin)
[PASS] Negative 9: Framework.Profile.PhaseCards detected (Phase Two uncovered)
[PASS] Negative 10: Framework.Profile.PhaseCooldownStarvation detected (KI-149 Starvation)

Result: 11/11 tests passed.
```
