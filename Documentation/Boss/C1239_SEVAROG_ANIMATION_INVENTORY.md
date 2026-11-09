# C1239 Sevarog Animation Asset Inventory & Move List Plan

**Authority:** Claude Lead Directive `[C-1239]` (2026-11-10)  
**Execution Reference:** `Docs/BossCombatReview/Execution/Claude/P_C1239_SEVAROGPROBE/probe_sevarog.log` (Engine Commandlet run under C-1155 engine lock, exit 0, 0 Content changes)  
**Source Script:** `Scripts/Editor/probe_sevarog_animations.py` (guarded 5.5 safe inspection wrappers)  
**Strict Discipline:** Plan-only deliverable; zero runtime wiring; zero asset mutations. Owner rule: Sevarog uses his OWN animations, strictly no retargeting.

---

## 1. Engine Probe Execution Summary

The headless commandlet probe was executed by Claude Lead under lock C-1155 against all 55 targeted animation assets under `/Game/ParagonSevarog/Characters/Heroes/Sevarog/Animations/`.

- **Log File:** `Docs/BossCombatReview/Execution/Claude/P_C1239_SEVAROGPROBE/probe_sevarog.log` (lines 1152–1217)
- **Status:** Exit code 0, 0 Python errors, 0 Content modifications (`pre_content.txt` == `post_content.txt`).
- **Assets Probed:** 3 Montages (Category A), 28 Melee Sequences (Category B), 11 Ability Sequences (Category C), 10 Reaction/Stagger Sequences (Category D), 4 Evolution Sequences (Category E).
- **Core Findings:**
  1. **Root Motion:** All inspected sequences return `root_motion=False`. Locomotion and attacks are fundamentally in-place animations driven by character movement / capsule translation.
  2. **Montage Assembly:** Montages `Swing1_Medium_Montage`, `Swing2_Medium_Montage`, and `LevelStart_Montage` each possess exactly 1 section (`Default`). No multi-section composite exists natively.
  3. **Notify Presence:** Raw sequences possess `0 notifies`. Existing montages possess legacy Paragon notifies (`AnimNotify_PlayParticleEffect` on `LevelStart_Montage`; 2 unnamed/skeleton notifies on Swing montages).

---

## 2. Category A: Existing Montages

| Asset Name | Log Line | Play Length (s) | Num Sections | Section Names | Root Motion | Notifies |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `Swing1_Medium_Montage` | 1154–1155 | 1.133317 | 1 | `[0] 'Default'` | `n/a` | 2 notifies: `[Unknown, Unknown]` |
| `Swing2_Medium_Montage` | 1156–1157 | 1.133317 | 1 | `[0] 'Default'` | `n/a` | 2 notifies: `[Unknown, Unknown]` |
| `LevelStart_Montage` | 1158–1159 | 5.000000 | 1 | `[0] 'Default'` | `n/a` | 1 notify: `[AnimNotify_PlayParticleEffect]` |

*Notes on Unknown notifies:* These are native Paragon skeleton/named notifies or FX cues without a typed C++ `UAnimNotify` class object. `probe_sevarog_animations.py` has been updated with a guarded `notify_name` read for Claude's rerun.

---

## 3. Category B: Primary Melee Sequences (28 Assets)

All 28 sequences have `root_motion=False` and `0 notifies` (raw animation sequences).

| Asset Name | Log Line | Play Length (s) | Combat Profile / Speed Tier |
| :--- | :--- | :--- | :--- |
| `Swing1_FAST_v2` | 1163 | 0.533333 | Fast light swing (Tier 1 speed) |
| `Swing1_FAST_120fps` | 1166 | 0.600000 | Fast light swing (120fps sampled) |
| `Swing1_120fps` | 1165 | 1.000000 | Standard light swing (120fps sampled) |
| `Swing1_Medium` | 1161 | 1.133333 | Standard medium horizontal swing |
| `Swing1_Slow_120fps` | 1167 | 1.500000 | Heavy windup swing (120fps sampled) |
| `Swing1_Slow` | 1162 | 1.700000 | Delayed heavy horizontal swing |
| `Swing1Start_120fps` | 1168 | 0.333333 | Attack startup gesture |
| `Swing1_Return2Idle` | 1164 | 2.000000 | Recovery transition to idle |
| `Swing1_Return2Idle_120fps` | 1169 | 2.100000 | Recovery transition to idle (120fps) |
| `Swing2_FAST_v2` | 1172 | 0.533333 | Fast backhand follow-up (Tier 1 speed) |
| `Swing2_FAST_120fps` | 1175 | 0.600000 | Fast backhand follow-up (120fps) |
| `Swing2_120fps` | 1174 | 1.000000 | Standard backhand swing (120fps) |
| `Swing2_Medium` | 1170 | 1.133333 | Standard medium backhand swing |
| `Swing2_Slow_120fps` | 1176 | 1.533333 | Heavy windup backhand (120fps) |
| `Swing2_Slow` | 1171 | 1.700000 | Delayed heavy backhand swing |
| `Swing2_Return2Idle` | 1173 | 2.533333 | Extended recovery transition |
| `Swing2_Return2Idle_120fps` | 1177 | 2.866667 | Extended recovery transition (120fps) |
| `Swing3_FAST_v2` | 1180 | 0.533333 | Fast overhead downward strike |
| `Swing3_FAST_120fps` | 1183 | 0.800000 | Fast overhead downward strike (120fps) |
| `Swing3_120fps` | 1182 | 1.000000 | Standard overhead smash (120fps) |
| `Swing3_Medium` | 1178 | 1.133333 | Standard medium overhead smash |
| `Swing3_Slow_120fps` | 1184 | 1.500000 | Delayed heavy overhead smash (120fps) |
| `Swing3_Slow` | 1179 | 1.700000 | Maximum delay overhead slam (1.70 s) |
| `Swing3_Return2Idle` | 1181 | 1.233333 | Quick recovery transition |
| `Swing3_Return2Idle_Medium` | 1186 | 1.266667 | Medium recovery transition |
| `Swing3_Return2Idle_120fps` | 1185 | 0.866667 | Snappy recovery transition (120fps) |
| `Swing_In_Air` | 1187 | 1.600000 | Aerial jump hammer smash |
| `Swing_In_Air_120fps` | 1188 | 1.833333 | Aerial jump hammer smash (120fps) |

---

## 4. Category C: Signature Abilities & Specials (11 Assets)

All 11 sequences have `root_motion=False` and `0 notifies`.

| Asset Name | Log Line | Play Length (s) | Combat Profile / Ability Role |
| :--- | :--- | :--- | :--- |
| `Ultimate_Swing_120fps` | 1190 | 2.633333 | Signature 360-degree massive hammer sweep |
| `Ultimate_Targeting` | 1191 | 0.866667 | Pre-ultimate aiming gesture |
| `Ultimate_Targeting_Loop` | 1192 | 2.233333 | Pre-ultimate continuous charge loop |
| `Ultimate_Targeting_pose` | 1193 | 0.033333 | Aim pose frame |
| `Subjugation` | 1194 | 2.866667 | Ground strike summoning dark root / snare ring |
| `Soul_Siphon` | 1195 | 1.833333 | Frontal cone soul drain channel |
| `Soul_Siphon_Targeting` | 1196 | 0.366667 | Siphon targeting gesture |
| `Soul_Siphon_Targeting_Loop` | 1197 | 1.533333 | Siphon targeting loop |
| `Speedburst` | 1198 | 1.266667 | Phantom dash / ethereal gap closer |
| `Cast` | 1199 | 1.300000 | One-handed arcane summoning cast |
| `Bound` | 1200 | 0.033333 | Pose frame |

---

## 5. Category D: Reactions, Staggers & Defeat (10 Assets)

All 10 sequences have `root_motion=False` and `0 notifies`.

| Asset Name | Log Line | Play Length (s) | Reaction Role |
| :--- | :--- | :--- | :--- |
| `Hitreact_Front` | 1202 | 1.766667 | Flinch from frontal hit |
| `Hitreact_Back` | 1203 | 1.900000 | Flinch from rear hit |
| `Hitreact_Left` | 1204 | 1.966667 | Flinch from left hit |
| `Hitreact_Right` | 1205 | 1.566667 | Flinch from right hit |
| `Stun_Start` | 1206 | 1.700000 | Poise break / posture break start |
| `Stun_Loop` | 1207 | 2.033333 | Vulnerable groggy loop |
| `Stun_End` | 1208 | 0.733333 | Recovery from posture break |
| `Knock_back` | 1209 | 2.666667 | Forward knockback recovery |
| `Knock_back_bwd` | 1210 | 2.666667 | Backward knockback recovery |
| `Death_front` | 1211 | 0.966667 | Defeat collapse sequence |

---

## 6. Category E: Soul Armor Progression (4 Assets)

All 4 sequences are 1-frame (0.033333 s) static configuration poses (`root_motion=False`, 0 notifies).

| Asset Name | Log Line | Play Length (s) | Visual Evolution Tier |
| :--- | :--- | :--- | :--- |
| `Stage_1` | 1213 | 0.033333 | Base cloak & basic hammer |
| `Stage_2` | 1214 | 0.033333 | Shoulder spikes added |
| `Stage_3` | 1215 | 0.033333 | Large pauldrons & crown spikes |
| `Stage_4` | 1216 | 0.033333 | Fully ascended wraith with ornate pauldrons |

---

## 7. Sevarog Soulslike Move List Plan (Elden Ring / Souls Archetype Mapping)

In accordance with the Owner rule: **Sevarog uses his OWN animations, strictly no retargeting.**  
All sequences listed below are verified in `probe_sevarog.log`.

```
===================================================================================================
SEVAROG MOVE LIST ARCHITECTURE (PROPOSED PLAN - 0 RUNTIME WIRING)
===================================================================================================

[MOVE 1] CLOSE MELEE COMBO (A1: Quick Right-to-Left Cleave -> A2: Backhand Follow-up)
- Role: Standard close-range pressure punishing greedy melee attacks.
- Component Sequences:
  * A1 Swing: Swing1_Medium (1.133 s) [Line 1161]
    - Estimated Timing: Windup 0.00..0.38 s, Active 0.38..0.52 s, Recovery 0.52..1.13 s.
  * A2 Swing: Swing2_Medium (1.133 s) [Line 1170]
    - Estimated Timing: Windup 0.00..0.35 s, Active 0.35..0.48 s, Recovery 0.48..1.13 s.
- Montages: Standalone single-section montages AM_Sevarog_A1 and AM_Sevarog_A2 (or native Swing1/2_Medium_Montage).

[MOVE 2] DELAYED HEAVY SLAM (A3: Roll-Catch Overhead Smash)
- Role: Classic Souls delayed punishment. Telegraphed windup forcing deliberate dodge timing.
- Component Sequence: Swing3_Slow (1.700 s) [Line 1179]
  - Estimated Timing: Heavy Windup 0.00..1.15 s, Active Slam 1.15..1.30 s, Ground Recovery 1.30..1.70 s.
- Combat Feel: Heavy weapon impact causing high stamina drain on block.

[MOVE 3] GAP CLOSER / PHANTOM SURGE (A4: Ethereal Rush -> Strike)
- Role: Closes distance when the player rolls backward or kites at mid/long range.
- Component Sequences:
  * Dash Phase: Speedburst (1.267 s) [Line 1198]
  * Follow-up Swing: Swing1_FAST_v2 (0.533 s) [Line 1163] or Swing1_FAST_120fps (0.600 s) [Line 1166]
- Movement Integration: In-place animation paired with root-motion or CharacterMovement capsule launch.

[MOVE 4] AREA DENIAL / RANGED HEX (A5: Subjugation Ground Rupture)
- Role: Ranged/AoE attack punishing ranged healing or passive spacing.
- Component Sequence: Subjugation (2.867 s) [Line 1194]
  - Telegraphed hammer raise, ground strike at ~1.20 s, ethereal shadow ring spawns under player.
- Combat Feel: Player must dodge roll on circle detonation (similar to Radagon ground stomp / ER gravity well).

[MOVE 5] SIGNATURE ABILITY / PHASE 2 ULTIMATE (A6: Colossal 360 Cleave)
- Role: Phase 2 signature move. Massive radial knockback clearing melee attackers.
- Component Sequence: Ultimate_Swing_120fps (2.633 s) [Line 1190]
  - Windup: 0.00..1.20 s with shadow gathering.
  - Active: 1.20..1.45 s (360-degree sweep).
  - Recovery: 1.45..2.63 s.

[MOVE 6] LIFE DRAIN / PUNISH HEX (A7: Soul Siphon)
- Role: Punishes turtling behind shield; channels unblockable or stamina-shredding soul drain cone.
- Component Sequence: Soul_Siphon (1.833 s) [Line 1195]
  - Active siphon cone forward; heals boss for partial damage dealt.

[ENCOUNTER START & STAGGER / POISE ARCHITECTURE]
- Intro / Awaken: LevelStart_Montage (5.000 s) [Line 1158]
- Posture Break / Stagger:
  * Start: Stun_Start (1.700 s) [Line 1206]
  * Vulnerable Critical Window: Stun_Loop (2.033 s) [Line 1207]
  * Recovery: Stun_End (0.733 s) [Line 1208]
- Defeat / Death: Death_front (0.967 s) [Line 1211]
```

---

## 8. Compliance & Next Steps

1. **Checklist Provenance:** This inventory satisfies Step 4 of `Documentation/Boss/NEW_BOSS_CHECKLIST.md` (Montage & Sequence Inventory from programmatic engine readback).
2. **Strict Safety:** Zero runtime assets were mutated; probe was read-only.
3. **Pending Actions:**
   - Claude Lead to rerun `probe_sevarog_animations.py` with the new guarded `notify_name` read to resolve the 2 Unknown notifies on `Swing1/2_Medium_Montage`.
   - Codex to draft the `URPGBossDefinition` data-only plan based on Section 7.
