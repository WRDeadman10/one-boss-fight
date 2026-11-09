# C1228: Ember Warden Montage & Notify Inventory

**Document ID:** `C1228_EMBER_NOTIFY_INVENTORY.md`  
**Task Reference:** `C-1228b` (read-only audit per `[C-1228]`)  
**Scope:** Authoritative inventory of Ember Warden's (`Boss01`) montages, composite sections, existing anim notifies / notify states, and exact mapping to `URPGAttackTracker` combat timing windows (tell/tracking, commitment, active trace, parry contact, and recovery).  
**Constraint Discipline:** Read-only audit. Zero asset modifications, zero pack asset mutations, zero C++ logic modifications.

---

## 1. Executive Summary & Purpose

Per directive `[C-1228]`, this document establishes the comprehensive reference inventory of all animation montages and dynamic montage sequences authored for or utilized by the boss **Ember Warden** (`Boss01`).

This inventory directly supports task `C-1228a` (Codex's montage-notify timing observer and validator in `RPGMontageNotifyTiming`) by documenting:
1. Exact asset paths and composite section breakdowns on disk.
2. In-asset anim notify and anim notify state timings (start, duration, class).
3. Exact mapping to the production timing windows in `Source/OneBossFight/Player/RPGAttackTracker.cpp`, citing specific C++ source lines.
4. Parry contact frames and mechanical behavior across directional slashes, ground slams, and ranged attacks.

---

## 2. Master Montage & Move Mapping Table

| Move ID | Asset Name | Asset Type | Length | Sections | Existing Notifies | Tracker Commit | Tracker Active | Parry Window | Tracker Source Line |
| :--- | :--- | :--- | :--- | :---: | :--- | :---: | :---: | :---: | :--- |
| **A1** | [`AM_Boss01_A1`](file:///c:/UnrealProject/OneBossFight/Content/OneBossFight/Boss01/Animations/AM_Boss01_A1.uasset) | Montage | 1.200 s | 1 | Rotation, Sound, Trace, DisableMov | 0.33 s | 0.35 .. 0.50 s | 0.35 .. 0.50 s | [`RPGAttackTracker.cpp:66`](file:///c:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGAttackTracker.cpp#L66) |
| **A2** | [`AM_Boss01_A2`](file:///c:/UnrealProject/OneBossFight/Content/OneBossFight/Boss01/Animations/AM_Boss01_A2.uasset) | Partial Montage (Raise Only) | 0.600 s | 1 | `AN_Boss01_A2_Raise` only (unassembled) | N/A (unwired) | N/A | Ground slam tell only (unwired) | [`RPGAttackTracker.cpp:35-44`](file:///c:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGAttackTracker.cpp#L35-L44) |
| **A3a** | [`AM_Boss01_A3a`](file:///c:/UnrealProject/OneBossFight/Content/OneBossFight/Boss01/Animations/AM_Boss01_A3a.uasset) | Montage | 0.800 s | 1 | Rotation, Sound, Trace, FollowUp, EndAbi | 0.38 s | 0.40 .. 0.60 s | 0.40 .. 0.60 s | [`RPGAttackTracker.cpp:68`](file:///c:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGAttackTracker.cpp#L68) |
| **A3b** | [`AM_Boss01_A3b`](file:///c:/UnrealProject/OneBossFight/Content/OneBossFight/Boss01/Animations/AM_Boss01_A3b.uasset) | Montage | 1.333 s | 1 | Rotation, Sound, Trace, EndAbi, DisableMov | 0.13 s | 0.15 .. 0.40 s | 0.15 .. 0.40 s | [`RPGAttackTracker.cpp:69`](file:///c:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGAttackTracker.cpp#L69) |
| **A4** | [`AN_Boss01_A4_LowSweep`](file:///c:/UnrealProject/OneBossFight/Content/OneBossFight/Boss01/Animations/AN_Boss01_A4_LowSweep.uasset) | Dynamic Montage | 1.767 s | 1 (dyn) | Programmatic (`URPGBossLowSweep`) | 0.40 s | 0.60 .. 0.90 s | Sweep (jump only) | [`RPGAttackTracker.cpp:86-95`](file:///c:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGAttackTracker.cpp#L86-L95) |
| **A5** | [`AN_Boss01_A5_JavelinThrow`](file:///c:/UnrealProject/OneBossFight/Content/OneBossFight/Boss01/Animations/AN_Boss01_A5_JavelinThrow.uasset) | Dynamic Montage | 1.000 s | 1 (dyn) | Programmatic (`URPGBossHealPunish`) | 0.45 s | 0.45 .. 0.50 s | Projectile deflect | [`RPGAttackTracker.cpp:99-108`](file:///c:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGAttackTracker.cpp#L99-L108) |
| **A1b** *(stand-in)* | `GS_Attack04_Montage` | Pack Montage | 1.467 s | 1 | Rotation, Sound, Trace, DisableMov | 0.12 s | 0.16 .. 0.46 s | 0.16 .. 0.46 s | [`RPGAttackTracker.cpp:67`](file:///c:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGAttackTracker.cpp#L67) |
| **A2** *(stand-in)* | `GS_ChargedAttack_Montage` | Pack Montage | 3.400 s | 1 | DisableMov, 2x Trace, 2x Sound | 1.68 s | 1.93 .. 2.11 s | Ground slam (unparryable) | [`RPGAttackTracker.cpp:35-44`](file:///c:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGAttackTracker.cpp#L35-L44) |
| **A6** *(stand-in)* | `GS_LeapAttack_Montage` | Pack Montage | 1.867 s | 1 | 2x Rotation, Trace | 0.16 s | 0.75 .. 1.17 s | Ground landing | [`RPGAttackTracker.cpp:74-82`](file:///c:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGAttackTracker.cpp#L74-L82) |
| **Parry Recoil** | [`AM_Boss01_ParryRecoil`](file:///c:/UnrealProject/OneBossFight/Content/OneBossFight/Boss01/Animations/AM_Boss01_ParryRecoil.uasset) | Montage | 0.600 s | 1 | `ANS_InputBuffer_C` (0.000..0.296 s) | N/A | Stun Reaction | Parry Result | [`RPGTier2BossPresentation.cpp:20,59-68`](file:///c:/UnrealProject/OneBossFight/Source/OneBossFight/Boss/RPGTier2BossPresentation.cpp#L20) |
| **Death** | [`AM_Boss01_DeathLegend`](file:///c:/UnrealProject/OneBossFight/Content/OneBossFight/Boss01/Animations/AM_Boss01_DeathLegend.uasset) | Montage | 3.400 s | 1 | No blend out (pose frozen at 2.50 s+) | N/A | Death State | Defeated State | [`RPGBossDeath.cpp:38,227-312`](file:///c:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGBossDeath.cpp#L38) |
| **Phase Roar** | [`AN_Boss01_PhaseRoar`](file:///c:/UnrealProject/OneBossFight/Content/OneBossFight/Boss01/Animations/AN_Boss01_PhaseRoar.uasset) | Sequence Clip | 1.800 s | 1 | Played via `RPGBossClips::Play` | N/A | Phase Transition | Invulnerable | [`RPGBossPhases.cpp:56,301-305`](file:///c:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGBossPhases.cpp#L56) |

---

## 3. Detailed Per-Montage Specification

### 3.1. `AM_Boss01_A1` — Quick Slash (Move `A1`)
- **Asset Path:** `/Game/OneBossFight/Boss01/Animations/AM_Boss01_A1.AM_Boss01_A1`
- **Source Sequence:** `AN_Boss01_A1_QuickSlash` (Length: 1.200 s, Rate Scale: 1.00)
- **Blend In / Out:** 0.25 s blend-in, 0.25 s blend-out
- **Sections:** 1 composite section:
  - `Default` / `AN_Boss01_A1_QuickSlash`: [0.000 s .. 1.200 s]
- **Authored Anim Notifies & States:**
  1. `[state] ANS_DisableMovement_C` at `0.000 s` for `0.500 s` (0.000 s .. 0.500 s)
  2. `[state] ANS_SetDesiredRotation_C` at `0.000 s` for `0.330 s` (0.000 s .. 0.330 s)
  3. `AnimNotify_PlaySound` at `0.330 s` (`A_Hammer_Swing_Cue` audio cue)
  4. `[state] ANS_CollisionTrace_C` at `0.350 s` for `0.150 s` (0.350 s .. 0.500 s)
- **`RPGAttackTracker.cpp` Mapping:**
  - Registered at: [`Source/OneBossFight/Player/RPGAttackTracker.cpp:66`](file:///c:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGAttackTracker.cpp#L66)
  - Lookup binding: [`Source/OneBossFight/Player/RPGAttackTracker.cpp:141`](file:///c:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGAttackTracker.cpp#L141)
  - Ability swap route: [`Source/OneBossFight/Player/RPGBossCloseClipSwap.cpp:43`](file:///c:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGBossCloseClipSwap.cpp#L43) and [`RPGBossCloseClipSwapRules.h:12`](file:///c:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGBossCloseClipSwapRules.h#L12) (swaps pack `GS_Attack03_Montage`)
  - **Tell / Windup Window:** `0.000 s .. 0.330 s` (`TrackTurnRate = 360.0 deg/s`, `bAuthoredWindup = true`)
  - **Commitment Point (`CommitTime`):** `0.330 s` (heading locks; aligns with end of `ANS_SetDesiredRotation_C` and sound tell at 0.330 s)
  - **Active Window (`ActiveStartTime` .. `ActiveEndTime`):** `0.350 s .. 0.500 s` (exact match with `ANS_CollisionTrace_C` [0.350 .. 0.500 s])
  - **Parry Contact Window:** `0.350 s .. 0.500 s` (parryable on blade contact; primary parry contact at ~0.350 s)
  - **Recovery Window (`RecoveryEndTime`):** `0.500 s .. 1.200 s` (`RecoveryEndTime = 1.20f`)

---

### 3.2. `AM_Boss01_A2` — Delayed Overhead Slam (Move `A2`, Partial / Unassembled Montage)
- **Asset Path:** `/Game/OneBossFight/Boss01/Animations/AM_Boss01_A2.AM_Boss01_A2`
- **Asset Play Length:** `0.600000 s` (Verified via C-1235 Lead read-only probe `probe_a2_length.log`)
- **Montage Sections (1 section):**
  - Section 0 (`Default`): `0.000 s .. 0.600 s` playing source sequence `AN_Boss01_A2_Raise` only (initial weapon raise tell).
- **Source Sequences on Disk (3 sequences):**
  1. `AN_Boss01_A2_Raise`: `0.000 s .. 0.600 s` (duration 0.600 s) — initial weapon lift tell (the only sequence wired into `AM_Boss01_A2`).
  2. `AN_Boss01_A2_ApexHold`: `0.600 s .. 1.767 s` (duration 1.167 s) — apex hold / delayed tell (standalone sequence on disk; not wired into montage).
  3. `AN_Boss01_A2_Slam`: `1.767 s .. 3.134 s` (duration 1.367 s) — power descent and ground impact (standalone sequence on disk; not wired into montage).
  *Origin of the 3.134 s Composite Assumption:* Summing the durations of the 3 raw source sequences yields 0.600 + 1.167 + 1.367 = 3.134 s. However, downstream sequences `ApexHold` and `Slam` were never spliced into `AM_Boss01_A2`.
- **Authoring & Timing Compatibility (REJECTED per C-1235):**
  - Table values (`CommitTime=1.68`, `ActiveStartTime=1.93`, `ActiveEndTime=2.11`, `RecoveryEndTime=3.14`) cannot live on a 0.600 s montage.
  - Attempting to author these times on `AM_Boss01_A2` causes the validator to fail with `OrderOrBounds` (window start 1.93 s > montage length 0.600 s).
- **Production Routing:**
  - Registered as `OptionalTrackerMontagePath` at [`Source/OneBossFight/Player/RPGAttackTracker.cpp:38`](file:///c:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGAttackTracker.cpp#L38).
  - In live combat, Move A2 uses the pack stand-in `GS_ChargedAttack_Montage` (3.400 s) with native table timings (`RPGAttackTracker.cpp:35-44`).
  - Splicing `AM_Boss01_A2` into a complete composite montage is parked as an art task.

---

### 3.3. `AM_Boss01_A3a` — Combo Slash 1 (Move `A3a`)
- **Asset Path:** `/Game/OneBossFight/Boss01/Animations/AM_Boss01_A3a.AM_Boss01_A3a`
- **Source Sequence:** `AN_Boss01_A3a_Combo1` (Length: 0.800 s, Rate Scale: 1.00)
- **Blend In / Out:** 0.25 s blend-in, 0.25 s blend-out
- **Sections:** 1 composite section:
  - `Default` / `AN_Boss01_A3a_Combo1`: [0.000 s .. 0.800 s]
- **Authored Anim Notifies & States:**
  1. `[state] ANS_DisableMovement_C` at `0.000 s` for `0.600 s` (0.000 s .. 0.600 s)
  2. `[state] ANS_SetDesiredRotation_C` at `0.000 s` for `0.380 s` (0.000 s .. 0.380 s)
  3. `AnimNotify_PlaySound` at `0.380 s` (audio tell)
  4. `[state] ANS_CollisionTrace_C` at `0.400 s` for `0.200 s` (0.400 s .. 0.600 s)
  5. `AN_PerformFollowUp_C` at `0.750 s` (signals ability system to chain into A3b)
  6. `AN_EndAnimatingAbility_C` at `0.780 s`
- **`RPGAttackTracker.cpp` Mapping:**
  - Registered at: [`Source/OneBossFight/Player/RPGAttackTracker.cpp:68`](file:///c:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGAttackTracker.cpp#L68)
  - Lookup binding: [`Source/OneBossFight/Player/RPGAttackTracker.cpp:141`](file:///c:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGAttackTracker.cpp#L141)
  - Ability swap route: [`Source/OneBossFight/Player/RPGBossCloseClipSwap.cpp:44`](file:///c:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGBossCloseClipSwap.cpp#L44) and [`RPGBossCloseClipSwapRules.h:13`](file:///c:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGBossCloseClipSwapRules.h#L13) (swaps pack `GS_Attack01_Montage`)
  - **Tell / Windup Window:** `0.000 s .. 0.380 s` (`TrackTurnRate = 360.0 deg/s`, `bAuthoredWindup = true`)
  - **Commitment Point (`CommitTime`):** `0.380 s` (heading locks; exact match with `ANS_SetDesiredRotation_C` end and audio tell at 0.380 s)
  - **Active Window (`ActiveStartTime` .. `ActiveEndTime`):** `0.400 s .. 0.600 s` (exact match with `ANS_CollisionTrace_C` [0.400 .. 0.600 s])
  - **Parry Contact Window:** `0.400 s .. 0.600 s` (parryable on active slash; earliest contact at 0.400 s)
  - **Recovery Window (`RecoveryEndTime`):** `0.600 s .. 0.800 s` (`RecoveryEndTime = 0.80f`)

---

### 3.4. `AM_Boss01_A3b` — Combo Slash 2 Follow-Up (Move `A3b`)
- **Asset Path:** `/Game/OneBossFight/Boss01/Animations/AM_Boss01_A3b.AM_Boss01_A3b`
- **Source Sequence:** `AN_Boss01_A3b_Combo2` (Length: 1.3333 s / 40 frames @ 30 FPS, Rate Scale: 1.00)
- **Blend In / Out:** 0.25 s blend-in, 0.25 s blend-out
- **Sections:** 1 composite section:
  - `Default` / `AN_Boss01_A3b_Combo2`: [0.000 s .. 1.333 s]
- **Authored Anim Notifies & States:**
  1. `[state] ANS_DisableMovement_C` at `0.000 s` for `0.400 s` (0.000 s .. 0.400 s)
  2. `[state] ANS_SetDesiredRotation_C` at `0.000 s` for `0.130 s` (0.000 s .. 0.130 s)
  3. `AnimNotify_PlaySound` at `0.130 s` (audio tell)
  4. `[state] ANS_CollisionTrace_C` at `0.150 s` for `0.250 s` (0.150 s .. 0.400 s)
  5. `AN_EndAnimatingAbility_C` at `1.313 s`
- **`RPGAttackTracker.cpp` Mapping:**
  - Registered at: [`Source/OneBossFight/Player/RPGAttackTracker.cpp:69`](file:///c:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGAttackTracker.cpp#L69)
  - Lookup binding: [`Source/OneBossFight/Player/RPGAttackTracker.cpp:141`](file:///c:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGAttackTracker.cpp#L141)
  - Branch evaluation: [`Source/OneBossFight/Player/RPGAttackTracker.cpp:449-467`](file:///c:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGAttackTracker.cpp#L449-L467) (`BranchAllowedNow()` validates range \(\le 400\text{ cm}\) and frontal cone \(\le 120^\circ\))
  - Ability swap route: [`Source/OneBossFight/Player/RPGBossCloseClipSwap.cpp:45`](file:///c:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGBossCloseClipSwap.cpp#L45) and [`RPGBossCloseClipSwapRules.h:14`](file:///c:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGBossCloseClipSwapRules.h#L14) (swaps pack `GS_Attack02_Montage`)
  - **Tell / Windup Window:** `0.000 s .. 0.130 s` (`TrackTurnRate = 360.0 deg/s`, `bBranchStage = true`, `bAuthoredWindup = true`)
  - **Commitment Point (`CommitTime`):** `0.130 s` (heading locks; exact match with `ANS_SetDesiredRotation_C` end and audio tell at 0.130 s)
  - **Active Window (`ActiveStartTime` .. `ActiveEndTime`):** `0.150 s .. 0.400 s` (exact match with `ANS_CollisionTrace_C` [0.150 .. 0.400 s])
  - **Parry Contact Window:** `0.150 s .. 0.400 s` (parryable on return slash contact; earliest contact at 0.150 s)
  - **Recovery Window (`RecoveryEndTime`):** `0.400 s .. 1.3333 s` (`RecoveryEndTime = 1.3333f`; ability ends at 1.313 s)

---

### 3.5. `AN_Boss01_A4_LowSweep` — 360 Low Sweep Dynamic Montage (Move `A4`)
- **Asset Path:** `/Game/OneBossFight/Boss01/Animations/AN_Boss01_A4_LowSweep.AN_Boss01_A4_LowSweep`
- **Asset Type:** `UAnimSequence` (played as dynamic runtime montage)
- **Sequence Length:** `1.767 s`
- **Dynamic Montage Construction:** Generated dynamically via `URPGAttackTracker::PlayClip` into the boss default slot
- **Notifies / Hit Logic:** Non-trace damage managed by `URPGBossLowSweep` component
- **`RPGAttackTracker.cpp` Mapping:**
  - Registered at: [`Source/OneBossFight/Player/RPGAttackTracker.cpp:86-95`](file:///c:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGAttackTracker.cpp#L86-L95)
  - Dynamic clip match logic: [`Source/OneBossFight/Player/RPGAttackTracker.cpp:128-142`](file:///c:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGAttackTracker.cpp#L128-L142)
  - Dynamic playback invocation: [`Source/OneBossFight/Player/RPGAttackTracker.cpp:170-205`](file:///c:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGAttackTracker.cpp#L170-L205)
  - **Tell / Windup Window:** `0.000 s .. 0.400 s` (`TrackTurnRate = 180.0 deg/s`; crouching telegraph per Freeze 16)
  - **Commitment Point (`CommitTime`):** `0.400 s` (heading locks 0.20 s before blade crosses floor)
  - **Active Window (`ActiveStartTime` .. `ActiveEndTime`):** `0.600 s .. 0.900 s` (blade crosses floor plane)
  - **Parry Contact Window:** Unparryable low horizontal sweep (jump / vertical evasion required per Freeze 16)
  - **Recovery Window (`RecoveryEndTime`):** `0.900 s .. 1.750 s` (`RecoveryEndTime = 1.75f`)

---

### 3.6. `AN_Boss01_A5_JavelinThrow` — Estus Punish Javelin Throw Dynamic Montage (Move `A5`)
- **Asset Path:** `/Game/OneBossFight/Boss01/Animations/AN_Boss01_A5_JavelinThrow.AN_Boss01_A5_JavelinThrow`
- **Asset Type:** `UAnimSequence` (played as dynamic runtime montage)
- **Sequence Length:** `1.000 s`
- **Dynamic Montage Construction:** Generated dynamically via `URPGAttackTracker::PlayClip`
- **Notifies / Release Logic:** Release triggered at active window start by `URPGBossHealPunish`, spawning projectile `ARPGBossJavelin`
- **`RPGAttackTracker.cpp` Mapping:**
  - Registered at: [`Source/OneBossFight/Player/RPGAttackTracker.cpp:99-108`](file:///c:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGAttackTracker.cpp#L99-L108)
  - Dynamic clip match logic: [`Source/OneBossFight/Player/RPGAttackTracker.cpp:128-142`](file:///c:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGAttackTracker.cpp#L128-L142)
  - Dynamic playback invocation: [`Source/OneBossFight/Player/RPGAttackTracker.cpp:170-205`](file:///c:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGAttackTracker.cpp#L170-L205)
  - **Tell / Windup Window:** `0.000 s .. 0.450 s` (`TrackTurnRate = 240.0 deg/s`; 0.40 s telegraph per Freeze 16)
  - **Commitment Point (`CommitTime`):** `0.450 s` (heading locks at throw release)
  - **Active Window (`ActiveStartTime` .. `ActiveEndTime`):** `0.450 s .. 0.500 s` (release frame; javelin leaves hand and enters autonomous ballistic flight)
  - **Parry Contact Window:** Ranged projectile deflect (parry occurs on incoming javelin impact with player shield/parry volume during flight, not against boss mesh)
  - **Recovery Window (`RecoveryEndTime`):** `0.500 s .. 0.950 s` (`RecoveryEndTime = 0.95f`)

---

### 3.7. `AM_Boss01_ParryRecoil` — Boss Parry Stun & Recoil Montage
- **Asset Path:** `/Game/OneBossFight/Boss01/Animations/AM_Boss01_ParryRecoil.AM_Boss01_ParryRecoil`
- **Source Sequence:** `AN_Boss01_ParryRecoil` (Length: 0.600 s, Rate Scale: 1.00)
- **Blend In / Out:** 0.25 s blend-in, 0.25 s blend-out
- **Sections:** 1 composite section:
  - `Default` / `AN_Boss01_ParryRecoil`: [0.000 s .. 0.600 s]
- **Authored Anim Notifies & States:**
  1. `[state] ANS_InputBuffer_C` at `0.000 s` for `0.296 s` (0.000 s .. 0.296 s; verified per `[C-988]` / `AB-A05`)
- **C++ Source Mapping:**
  - Asset path definition: [`Source/OneBossFight/Boss/RPGTier2BossPresentation.cpp:20`](file:///c:/UnrealProject/OneBossFight/Source/OneBossFight/Boss/RPGTier2BossPresentation.cpp#L20)
  - Playback implementation: [`Source/OneBossFight/Boss/RPGTier2BossPresentation.cpp:59-68`](file:///c:/UnrealProject/OneBossFight/Source/OneBossFight/Boss/RPGTier2BossPresentation.cpp#L59-L68)
  - Triggered by player parry: [`Source/OneBossFight/Player/RPGPlayerParry.cpp:174-188`](file:///c:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGPlayerParry.cpp#L174-L188)
  - Sevarog director fallback: [`Source/OneBossFight/Player/RPGSevarogDirector.cpp:244-252`](file:///c:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGSevarogDirector.cpp#L244-L252)
  - Gate rule: [`RPGTier2BossRules.h:14`](file:///c:/UnrealProject/OneBossFight/Source/OneBossFight/Boss/RPGTier2BossRules.h#L14) (`ShouldPlayParryRecoil(bTier2Enabled, bSuccessfulParry)`)
  - **Timing & Mechanics:** Plays when player successfully parries an incoming boss attack; recoils boss backwards for 0.600 s; opens input buffer 0.000..0.296 s; cancels active attack montage.

---

### 3.8. `AM_Boss01_DeathLegend` — Ember Warden Legend Death Montage
- **Asset Path:** `/Game/OneBossFight/Boss01/Animations/AM_Boss01_DeathLegend.AM_Boss01_DeathLegend`
- **Source Sequence:** `AN_Boss01_DeathLegend` (Length: 3.400 s)
- **Asset Properties:** `enable_auto_blend_out = false` (configured via `Scripts/Editor/make_death_montage.py` so final defeated pose remains frozen on ground)
- **Sections:** 1 composite section:
  - `Default` / `AN_Boss01_DeathLegend`: [0.000 s .. 3.400 s]
- **C++ Source Mapping:**
  - Soft path definition: [`Source/OneBossFight/Player/RPGBossDeath.cpp:38`](file:///c:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGBossDeath.cpp#L38)
  - Loading & montage resolution: [`Source/OneBossFight/Player/RPGBossDeath.cpp:146-172`](file:///c:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGBossDeath.cpp#L146-L172)
  - Pack array substitution: [`Source/OneBossFight/Player/RPGBossDeath.cpp:227-312`](file:///c:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGBossDeath.cpp#L227-L312) (`ApplyPackMontage()` sets pack `GA_EnemyRagdollDeath`'s `DeathMontages` array)
  - Pose freezing logic: [`Source/OneBossFight/Player/RPGBossDeath.cpp:491-496`](file:///c:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGBossDeath.cpp#L491-L496) (pauses anim instance at `HoldAtSeconds = 2.50f` to hold pose indefinitely)
  - Header declaration: [`Source/OneBossFight/Player/RPGBossDeath.h:48-52`](file:///c:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGBossDeath.h#L48-L52)

---

### 3.9. `AN_Boss01_PhaseRoar` — Phase 2 Transition Roar
- **Asset Path:** `/Game/OneBossFight/Boss01/Animations/AN_Boss01_PhaseRoar.AN_Boss01_PhaseRoar`
- **Asset Type:** `UAnimSequence` (Length: 1.800 s)
- **C++ Source Mapping:**
  - Soft path definition: [`Source/OneBossFight/Player/RPGBossPhases.cpp:56`](file:///c:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGBossPhases.cpp#L56)
  - Playback: [`Source/OneBossFight/Player/RPGBossPhases.cpp:301-305`](file:///c:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGBossPhases.cpp#L301-L305) via `RPGBossClips::Play(Character, Clip, 0.15f, 0.25f)`
  - Header declaration: [`Source/OneBossFight/Player/RPGBossPhases.h:47`](file:///c:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGBossPhases.h#L47)
  - **Timing & Function:** Fires when boss drops below 60% health. Plays 1.800 s roar animation while invulnerable, triggering Phase 2 aura activation (`NS_Boss_PhaseTwoAura_BoostLite_Authored`).

---

## 4. Pack Stand-In Montages Tracked in `RPGAttackTracker.cpp`

For complete traceability, three pack montages continue to serve as stand-in moves or fallbacks in `URPGAttackTracker`:

1. **`GS_Attack04_Montage` (`A1b` — Chained Quick Slash Follow-Up):**
   - Pack Path: `/Game/AdvancedARPGCombat/MeleeCombatSystem/Animations/AI/GreatswordBoss/GS_Attack04_Montage`
   - Length: 1.467 s
   - Notifies: `ANS_DisableMovement_C` (0.000..1.467 s), `ANS_SetDesiredRotation_C` (0.000..0.279 s), `AnimNotify_PlaySound` (0.159 s), `ANS_CollisionTrace_C` (0.162..0.465 s)
   - Source Line: [`Source/OneBossFight/Player/RPGAttackTracker.cpp:67`](file:///c:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGAttackTracker.cpp#L67)
   - Windows: `CommitTime = 0.12f`, `ActiveStartTime = 0.16f`, `ActiveEndTime = 0.46f`, `RecoveryEndTime = 1.25f`, `bBranchStage = true`, `bAuthoredWindup = false`

2. **`GS_ChargedAttack_Montage` (`A2` Fallback Stand-In):**
   - Pack Path: `/Game/AdvancedARPGCombat/MeleeCombatSystem/Animations/AI/GreatswordBoss/GS_ChargedAttack_Montage`
   - Length: 3.400 s
   - Notifies: `ANS_DisableMovement_C` (0.000..4.933 s), `ANS_CollisionTrace_C` (1.567..1.760 s & 1.925..2.104 s), `AnimNotify_PlaySound` (1.593 s & 1.817 s)
   - Source Line: [`Source/OneBossFight/Player/RPGAttackTracker.cpp:35-44`](file:///c:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGAttackTracker.cpp#L35-L44)
   - Windows: `CommitTime = 1.68f`, `ActiveStartTime = 1.93f`, `ActiveEndTime = 2.11f`, `RecoveryEndTime = 3.14f`, `TrackTurnRate = 120.0 deg/s`

3. **`GS_LeapAttack_Montage` (`A6` — Phase 2 Leap Slam):**
   - Pack Path: `/Game/AdvancedARPGCombat/MeleeCombatSystem/Animations/AI/GreatswordBoss/GS_LeapAttack_Montage`
   - Length: 1.867 s
   - Notifies: `ANS_SetDesiredRotation_C` (0.000..0.157 s & 0.691..0.832 s), `ANS_CollisionTrace_C` (0.754..1.175 s)
   - Source Line: [`Source/OneBossFight/Player/RPGAttackTracker.cpp:74-82`](file:///c:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGAttackTracker.cpp#L74-L82)
   - Windows: `CommitTime = 0.16f` (heading locks at 0.16 s so boss does not steer in flight per Freeze 16), `ActiveStartTime = 0.75f`, `ActiveEndTime = 1.17f`, `RecoveryEndTime = 1.80f`, `TrackTurnRate = 120.0 deg/s`

---

## 5. Architectural Alignment with `RPGMontageNotifyTiming` (`C-1228a`)

Codex's montage-notify timing observer (`RPGMontageNotifyTiming`, task `C-1228a`) consumes these exact coordinates:

```cpp
namespace RPGMontageNotifyTiming
{
    struct FAnnotation
    {
        FString MontageObjectPath;
        FName MoveId = NAME_None;
        float MontageLength = 0.f;
        float TellStartTime = -1.f;
        float CommitTime = -1.f;
        float WindowStartTime = -1.f;
        float WindowEndTime = -1.f;
        float ParryContactTime = -1.f;
        float RecoveryEndTime = -1.f;
        float TrackTurnRate = 0.f;
        bool bIgnorePlayerIFrames = false;
        bool bBranchStage = false;
        float BranchRange = 0.f;
        float BranchConeDegrees = 120.f;
        bool bAuthoredWindup = false;
    };
}
```

### Direct Annotation Mapping Coordinates:
- **`A1` (`AM_Boss01_A1`):**
  - `MontageLength = 1.200f`, `TellStartTime = 0.000f`, `CommitTime = 0.330f`, `WindowStartTime = 0.350f`, `WindowEndTime = 0.500f`, `ParryContactTime = 0.350f`, `RecoveryEndTime = 1.200f`, `TrackTurnRate = 360.f`, `bAuthoredWindup = true`
- **`A2` (`AM_Boss01_A2`):**
  - `MontageLength = 3.134f`, `TellStartTime = 0.000f`, `CommitTime = 1.680f`, `WindowStartTime = 1.930f`, `WindowEndTime = 2.110f`, `ParryContactTime = -1.f` (ground slam unparryable), `RecoveryEndTime = 3.140f`, `TrackTurnRate = 120.f`, `bAuthoredWindup = true`
- **`A3a` (`AM_Boss01_A3a`):**
  - `MontageLength = 0.800f`, `TellStartTime = 0.000f`, `CommitTime = 0.380f`, `WindowStartTime = 0.400f`, `WindowEndTime = 0.600f`, `ParryContactTime = 0.400f`, `RecoveryEndTime = 0.800f`, `TrackTurnRate = 360.f`, `bAuthoredWindup = true`
- **`A3b` (`AM_Boss01_A3b`):**
  - `MontageLength = 1.3333f`, `TellStartTime = 0.000f`, `CommitTime = 0.130f`, `WindowStartTime = 0.150f`, `WindowEndTime = 0.400f`, `ParryContactTime = 0.150f`, `RecoveryEndTime = 1.3333f`, `TrackTurnRate = 360.f`, `bBranchStage = true`, `BranchRange = 400.f`, `BranchConeDegrees = 120.f`, `bAuthoredWindup = true`

---

## 6. Audit Verification & Integrity

- **Asset State:** Read-only verified via in-engine dumps and source tree inspections.
- **Link Check:** Validated clean (`broken_links=0`).
- **Offline Suite:** Validated 52/52 tests PASS.
- **Git State:** 0 mutations to assets, 0 remote push.


---

## 7. C-1229c Cross-Check: ANS_CollisionTrace vs RPGAttackTracker Active Windows (A1, A3a, A3b)

Per directive [C-1229], this section audits and cross-checks the authored in-montage ANS_CollisionTrace_C active damage windows against the native URPGAttackTracker table values (ActiveStartTime and ActiveEndTime) for close attacks **A1**, **A3a**, and **A3b**, documenting any timing discrepancy exceeding the \(0.02	ext{ s}\) (\(20	ext{ ms}\) / \(1.2	ext{ frames}\) @ 60 FPS) audit threshold.

### 7.1. Authored Project Montages Cross-Check Table

| Move ID | Authored Project Montage | In-Asset ANS_CollisionTrace_C Window | RPGAttackTracker.cpp Table Window | Start Delta (\(\Delta\)) | End Delta (\(\Delta\)) | Discrepancy > 0.02 s? | Audit Finding |
| :---: | :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **A1** | [AM_Boss01_A1](file:///c:/UnrealProject/OneBossFight/Content/OneBossFight/Boss01/Animations/AM_Boss01_A1.uasset) | **0.350 s .. 0.500 s**<br>*(start 0.350s, dur 0.150s)* | **0.350 s .. 0.500 s**<br>*(line 66: 0.35f .. 0.50f)* | **0.000 s** (0.0 ms) | **0.000 s** (0.0 ms) | **NONE (0.0 ms)** | **PERFECT MATCH** (0.00 frames) |
| **A3a** | [AM_Boss01_A3a](file:///c:/UnrealProject/OneBossFight/Content/OneBossFight/Boss01/Animations/AM_Boss01_A3a.uasset) | **0.400 s .. 0.600 s**<br>*(start 0.400s, dur 0.200s)* | **0.400 s .. 0.600 s**<br>*(line 68: 0.40f .. 0.60f)* | **0.000 s** (0.0 ms) | **0.000 s** (0.0 ms) | **NONE (0.0 ms)** | **PERFECT MATCH** (0.00 frames) |
| **A3b** | [AM_Boss01_A3b](file:///c:/UnrealProject/OneBossFight/Content/OneBossFight/Boss01/Animations/AM_Boss01_A3b.uasset) | **0.150 s .. 0.400 s**<br>*(start 0.150s, dur 0.250s)* | **0.150 s .. 0.400 s**<br>*(line 69: 0.15f .. 0.40f)* | **0.000 s** (0.0 ms) | **0.000 s** (0.0 ms) | **NONE (0.0 ms)** | **PERFECT MATCH** (0.00 frames) |

**Conclusion on Authored Assets:** There are **ZERO (0) discrepancies** exceeding \(0.02	ext{ s}\) across the authored Ember Warden close attack montages. The C++ URPGAttackTracker configuration lines (RPGAttackTracker.cpp:66-69) were authored with exact mathematical parity to the project's custom animation notifies (AuthoredWindup = true).

---

### 7.2. Historical Context: Pack Stand-In Montages vs RPGAttackTracker Windows

When running under fallback mode or before the RPGBossCloseClipSwap component replaces the ability montages, the pack's stand-in montages (GS_Attack01_Montage .. GS_Attack03_Montage) exhibit substantial divergence from the intended Soulslike combat windows:

| Move ID | Pack Stand-In Montage | In-Asset Pack ANS_CollisionTrace_C Window | Intended Tracker Table Window | Start Mismatch (\(\Delta\)) | End Mismatch (\(\Delta\)) | Mismatch > 0.02 s? | Architectural Remedy |
| :---: | :--- | :---: | :---: | :---: | :---: | :---: | :--- |
| **A1** | GS_Attack03_Montage | **0.115 s .. 0.418 s**<br>*(start 0.115s, dur 0.303s)* | **0.350 s .. 0.500 s** | **+0.235 s** (+235 ms / +14.1 frames) | **+0.082 s** (+82 ms / +4.9 frames) | **YES (+235 ms)** | Swapped with AM_Boss01_A1 via RPGBossCloseClipSwap; telegraph dilated via 
pg.CloseTelegraph (0.4s) |
| **A3a** | GS_Attack01_Montage | **0.166 s .. 0.469 s**<br>*(start 0.166s, dur 0.303s)* | **0.400 s .. 0.600 s** | **+0.234 s** (+234 ms / +14.0 frames) | **+0.131 s** (+131 ms / +7.9 frames) | **YES (+234 ms)** | Swapped with AM_Boss01_A3a via RPGBossCloseClipSwap |
| **A3b** | GS_Attack02_Montage | **0.141 s .. 0.444 s**<br>*(start 0.141s, dur 0.303s)* | **0.150 s .. 0.400 s** | **+0.009 s** (+9 ms / +0.5 frames) | **-0.044 s** (-44 ms / -2.6 frames) | **YES (-44 ms on End)** | Swapped with AM_Boss01_A3b via RPGBossCloseClipSwap |

This explains why RPGBossCloseClipSwapRules explicitly maps GS_Attack03_Montage -> AM_Boss01_A1, GS_Attack01_Montage -> AM_Boss01_A3a, and GS_Attack02_Montage -> AM_Boss01_A3b: the authored clips lengthen the tell from a hasty 0.11-0.16s to a readable 0.35-0.40s.

---

## 8. C-1230c Proposed `URPGANS_BossMoveTiming` Parameter Values (Draft — No Asset Mutation)

**Authority:** Claude Lead Directive `[C-1230]` (2026-11-09).  
**Status:** DRAFT ONLY. Zero assets modified. No `URPGANS_BossMoveTiming` notify states added to any `.uasset`. Applying them to assets requires a formal Lead verdict and engine lock.

The following table defines the proposed parameter values for `URPGANS_BossMoveTiming` notify states to be authored on the three core Ember Warden attack montages (`AM_Boss01_A1`, `AM_Boss01_A3a`, and `AM_Boss01_A3b`), derived directly from the verified C1228 inventory and authoritative `URPGAttackTracker` rows:

### 8.1. Proposed Parameter Table

| Parameter Field | Type | `AM_Boss01_A1` (`A1`) | `AM_Boss01_A3a` (`A3a`) | `AM_Boss01_A3b` (`A3b`) | Origin / Rationale |
| :--- | :---: | :---: | :---: | :---: | :--- |
| **`MoveId`** | `FName` | `A1` | `A3a` | `A3b` | Exact move identifier matching `RPGAttackTracker.cpp` rows |
| **`CommitTime`** | `float` | **0.330 s** | **0.380 s** | **0.130 s** | Aligns with end of `ANS_SetDesiredRotation_C` and audio tell |
| **`WindowStartTime`** | `float` | **0.350 s** | **0.400 s** | **0.150 s** | Exact start of `ANS_CollisionTrace_C` active damage window |
| **`WindowEndTime`** | `float` | **0.500 s** | **0.600 s** | **0.400 s** | Exact end of `ANS_CollisionTrace_C` active damage window |
| **`RecoveryEndTime`** | `float` | **1.200 s** | **0.800 s** | **1.3333 s** | End of ability animation / blend out to idle |
| **`TrackTurnRate`** | `float` | **360.0 deg/s** | **360.0 deg/s** | **360.0 deg/s** | Native tracker turn rate for close attacks (`RPGAttackTracker.cpp:61`) |
| **`bBranchStage`** | `bool` | `false` | `false` | **`true`** | A3b is the follow-up combo branch stage requiring frontal player check |
| **`BranchRange`** | `float` | `0.0 cm` *(unused)* | `0.0 cm` *(unused)* | **400.0 cm** | Native default branch proximity threshold (`FRPGAttackTrackerConfig`, `RPGAttackTracker.h:162`) |
| **`BranchConeDegrees`** | `float` | `120.0 deg` *(default)* | `120.0 deg` *(default)* | **120.0 deg** | Native frontal cone arc for A3b branch check (`RPGAttackTracker.cpp:481`) |
| **`bAuthoredWindup`** | `bool` | `true` | `true` | `true` | Flags move as having authored readable windup (bypasses stand-in dilation) |

### 8.2. Target Asset Insertion Tracks

When authorized by Lead for application:
1. **`AM_Boss01_A1`** (`/Game/OneBossFight/Boss01/Animations/AM_Boss01_A1`):
   - Place `URPGANS_BossMoveTiming` on a dedicated Notify Track from `0.000 s` to `1.200 s` (span of entire montage).
   - Parameters: `MoveId=A1`, `CommitTime=0.330`, `WindowStartTime=0.350`, `WindowEndTime=0.500`, `RecoveryEndTime=1.200`, `TrackTurnRate=360.0`, `bBranchStage=false`, `bAuthoredWindup=true`.
2. **`AM_Boss01_A3a`** (`/Game/OneBossFight/Boss01/Animations/AM_Boss01_A3a`):
   - Place `URPGANS_BossMoveTiming` from `0.000 s` to `0.800 s`.
   - Parameters: `MoveId=A3a`, `CommitTime=0.380`, `WindowStartTime=0.400`, `WindowEndTime=0.600`, `RecoveryEndTime=0.800`, `TrackTurnRate=360.0`, `bBranchStage=false`, `bAuthoredWindup=true`.
3. **`AM_Boss01_A3b`** (`/Game/OneBossFight/Boss01/Animations/AM_Boss01_A3b`):
   - Place `URPGANS_BossMoveTiming` from `0.000 s` to `1.3333 s`.
   - Parameters: `MoveId=A3b`, `CommitTime=0.130`, `WindowStartTime=0.150`, `WindowEndTime=0.400`, `RecoveryEndTime=1.3333`, `TrackTurnRate=360.0`, `bBranchStage=true`, `BranchRange=400.0`, `BranchConeDegrees=120.0`, `bAuthoredWindup=true`.

### 8.3. C-1235 Read-Only Audit: `AM_Boss01_A2` Montage Length & Authoring Rejection

**Authority:** Claude Lead Directives `[C-1233]`, `[C-1234]`, `[C-1235]` (2026-11-10).  
**Status:** REJECTED / PARKED. Zero asset modifications. Do not author `AM_Boss01_A2`.

#### 8.3.1. Asset Probe Readback vs Historical Assumption
Claude Lead's C-1235 engine probe (`Docs/BossCombatReview/Execution/Claude/B_C1235_EMBERA2/probe_a2_length.log`) verified the ground truth:
```
[A2Probe] AM_Boss01_A1 play_length=1.200000 sections=1
[A2Probe] AM_Boss01_A2 play_length=0.600000 sections=1
[A2Probe] AM_Boss01_A3a play_length=0.800000 sections=1
[A2Probe] AM_Boss01_A3b play_length=1.333333 sections=1
```
- **Asset Ground Truth:** `AM_Boss01_A2` is 0.600 s long with exactly 1 section (`Default`, playing `AN_Boss01_A2_Raise`).
- **Discrepancy Root Cause:** The 3.134 s composite claim in earlier drafts resulted from summing the lengths of three individual asset sequences on disk (`AN_Boss01_A2_Raise` [0.600 s] + `AN_Boss01_A2_ApexHold` [1.167 s] + `AN_Boss01_A2_Slam` [1.367 s] = 3.134 s). Crucially, the latter two sequences were never spliced together into `AM_Boss01_A2`.
- **Validation Failure:** Authoring native table timings (Commit=1.68 s, Active=1.93..2.11 s, Recovery=3.14 s) onto a 0.600 s montage triggers `URPGMontageNotifyTiming` validation failure (`INVALID OrderOrBounds: ActiveStartTime (1.93) > MontageLength (0.60)`).
- **Resolution:**
  - `AM_Boss01_A2` authoring is **REJECTED** and removed from `Scripts/Editor/author_ember_move_timing.py`.
  - A2 timing remains native table-driven (`RPGAttackTracker.cpp:41-50`) playing through pack stand-in `GS_ChargedAttack_Montage` (3.400 s).
  - Full composite assembly of `AM_Boss01_A2` is parked as an art task.
