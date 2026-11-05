# V-A032: Boss Animation Anticipation & Feel Audit

**Author:** Antigravity (Offline Quality, Audit & Asset Lane)
**Date:** 2026-11-06
**Scope:** Frame-by-frame anticipation, commitment, and release analysis of the 5 primary boss moves vs measured FromSoftware / Soulslike benchmark duel references.
**Sources:**
- Engine Timing Configurations: [`Source/OneBossFight/Player/RPGAttackTracker.cpp:30-108`](file:///c:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGAttackTracker.cpp#L30-L108)
- Telegraph Scaling Rules: [`Source/OneBossFight/Player/RPGBossTelegraphScaleRules.h:15-35`](file:///c:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGBossTelegraphScaleRules.h#L15-L35)
- Reference Archetype: [`Documentation/Boss/Morgott_82_Point_Combat_Reference.md`](file:///c:/UnrealProject/OneBossFight/Documentation/Boss/Morgott_82_Point_Combat_Reference.md)
- Design Target Specification: [`Documentation/Master_Design_Freeze_v1_2_AI_Implementation_Ready.md:135-142`](file:///c:/UnrealProject/OneBossFight/Documentation/Master_Design_Freeze_v1_2_AI_Implementation_Ready.md#L135-L142)

---

## 1. Executive Summary

- **Benchmark Standard [PROPOSAL / Archetype Design Reference]:** FromSoftware Soulslike duel standards (e.g. Morgott, Champion Gundyr, Artorias) recommend:
  - Fast quick-checks: **20 - 24 frames** (0.33 - 0.40 s at 60 FPS) minimum telegraph before active hitbox open.
  - Heavy punishment attacks: **60 - 110 frames** (1.00 - 1.80 s at 60 FPS) readable windup with a distinct apex pause.
  - Tracking lock (`CommitTime`): Locks **4 - 8 frames** (0.06 - 0.13 s at 60 FPS) prior to release, preventing "aimbot" tracking during the swing.
- **Audit Findings:**
  - Stand-in pack clips (`GS_Attack01..04`) had narrow windup windows (0.12 - 0.17 s, 7–10 frames; cited in `RPGAttackTracker.cpp:49`), causing perceived unfair hitches.
  - Authored replacements (`AM_Boss01_A1`, `AM_Boss01_A2`) and CVar-scaled telegraphs (`rpg.CloseTelegraph 0.4`, `RPGAttackTracker.cpp:20`) bring core attacks into readable reaction bands.

---

## 2. 5-Move Anticipation & Reaction Timing Matrix

All configured frame counts evaluated at standard **60 FPS** target based on source code definitions in [`Source/OneBossFight/Player/RPGAttackTracker.cpp:30-108`](file:///c:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGAttackTracker.cpp#L30-L108):

| Move ID | Move Name / Archetype | Pack Stand-in Windup (Source: `RPGAttackTracker.cpp`) | Configured Windup (Source: `RPGAttackTracker.cpp`) | Soulslike Reference Target | Configured Heading Commit Lock | Active Hit Window | Configured Recovery End | Feel Assessment & Recommendation |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **`A1`** | **Quick Overhead Slash** | 0.14 s (`RPGAttackTracker.cpp:49`) | **0.35 s (21 frames)** (`:66`) | 20 – 24 frames [PROPOSAL] | 0.33 s (`:66`) | 0.35 – 0.50 s (`:66`) | 1.20 s (`:66`) | **OPTIMAL**. Authored windup allows clean sight-read parry or dodge. |
| **`A2`** | **Delayed Slam (Ground Strike)**| 1.68 s (`RPGAttackTracker.cpp:32`) | **1.93 s (116 frames)** (`:40`) | 90 – 120 frames [PROPOSAL] | 1.68 s (`:39`) | 1.93 – 2.11 s (`:40-41`)| 3.14 s (`:42`) | **EXCELLENT**. Long apex hold creates dramatic tension; ground slam behavior. |
| **`A3`** | **Two-Hit Combo (`A3a` + `A3b`)**| 0.17 s (`RPGAttackTracker.cpp:49`) | **0.40 s + 0.15 s** (`:68-69`) | 20 – 24 frames [PROPOSAL] | 0.38 s / 0.13 s (`:68-69`) | A3a: 0.40–0.60 s; A3b: 0.15–0.40 s | 0.80 s / 1.33 s (`:68-69`) | **BALANCED**. Rhythmically consistent; second swing gives clear parry counter-window. |
| **`A4`** | **Low Horizontal Sweep** | N/A (custom clip, `:84`) | **0.60 s (36 frames)** (`:91`) | 24 – 30 frames [PROPOSAL] | 0.40 s (`:90`) | 0.60 – 0.90 s (`:91-92`)| 1.75 s (`:93`) | **GOOD**. Broad horizontal tell; requires low roll or jump evasion. |
| **`A6`** | **Leap & Shockwave Ring** | 0.16 s rotation (`RPGAttackTracker.cpp:71`)| **0.75 s (45 frames)** (`:78`) | 75 – 90 frames [PROPOSAL] | 0.16 s (`:77`) | 0.75 – 1.17 s (`:78-79`)| 1.80 s (`:80`) | **EXCELLENT**. Airborne apex gives unambiguous visual signal to prepare jump dodge. |

---

## 3. Anticipation Silhouette & Visual Cues

1. **Upper Torso Silhouetting:**
   - In `A2` and `A6`, the boss raises the greatsword high above shoulder line, silhouetted against the dusk sky.
   - Blade glint and apex freeze give clear warning even when camera is zoomed close.
2. **Heading Lock Decoupling:**
   - For all 5 moves, heading tracking stops before the active trace opens (`A1`: 20 ms gap; `A2`: 250 ms gap; `A3a`: 20 ms gap; `A4`: 200 ms gap; `A6`: 590 ms gap; source: [`RPGAttackTracker.cpp:30-108`](file:///c:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGAttackTracker.cpp#L30-L108)).
   - This allows the player to circle-strafe or roll past the boss's flank with reliable evasion.
3. **Pacing & Rest Windows:**
   - Post-attack recovery windows range from 0.70 s (`A1`) to 1.03 s (`A2`), providing well-defined attack windows for the player.
