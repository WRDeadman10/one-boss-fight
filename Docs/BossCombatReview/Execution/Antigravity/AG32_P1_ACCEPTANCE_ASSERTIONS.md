# AG-32: P1 Telegraph & Readability Acceptance Test Assertions (Revision 2)

**Document ID:** `AG32_P1_ACCEPTANCE_ASSERTIONS` (Rev 02)  
**Date:** 2026-10-26  
**Author:** Antigravity (Visual & Technical Animation Investigator)  
**Work Order:** `Docs/BossCombatReview/Execution/TASK_BOARD.md` (Task **A-T2**, audited per Claude `[C-139]`)  
**Governing Specifications:** [`AG3_TELEGRAPH_READABILITY_SPEC.md`](file:///c:/UnrealProject/OneBossFight/Docs/BossCombatReview/Execution/Antigravity/AG3_TELEGRAPH_READABILITY_SPEC.md), [`AG31_CAPTURE_VERDICT_TABLE.md`](file:///c:/UnrealProject/OneBossFight/Docs/BossCombatReview/Execution/Antigravity/AG31_CAPTURE_VERDICT_TABLE.md)  
**Citations & Sources:** `Claude/Evidence/E-007_CAP01_A5_release_timing.md`, `Claude/Evidence/E-008_CAP02_A4_query_vs_visible_blade.md`

---

## 1. Executive Summary & Epistemological Boundaries

This specification operationalizes the perceptual and mechanical readability requirements authored in `AG3_TELEGRAPH_READABILITY_SPEC.md` into **driver-checkable, mathematically bounded assertions**. 

Each assertion evaluates live engine combat state directly against existing native C++ debug hooks exposed on `URPGAttackTracker`, `URPGCombatDebug`, `URPGBossEncounter`, `URPGBossPhases`, and `URPGBossStagger`. Every hook citation is permanently anchored to its exact header declaration and C++ implementation (`file:line`).

> [!IMPORTANT]
> **Strict Separation of Design Freeze vs PROPOSED Feel Decisions:**
> In accordance with Claude's review (`[C-139]`), every numeric tolerance and threshold is tagged with its authoritative source (e.g. `E-007:3-7`, `E-008:7-13`, `AG3:68-90`, or Master Design Freeze sections). Where a threshold represents an Antigravity proposal rather than frozen project data, it is explicitly marked **`PROPOSED (feel decision for owner signoff)`** and aggregated in the Owner Questions table below.

---

## 2. Top-Level Owner Questions: PROPOSED Feel Decisions

The following table aggregates all proposed tolerance thresholds across the boss inventory for project owner review and signoff:

| Move ID | Parameter / Threshold | Nominal Value | PROPOSED Pass Tolerance | Governing Context / Rationale | Owner Decision Needed |
|---|---|---|---|---|---|
| **A1** | Commitment Position | $0.330\text{ s}$ (`AG3:66`) | $\pm 0.033\text{ s}$ (1 frame @ 30fps) | `PROPOSED`: Standard frame tolerance | Is $\pm 33.3\text{ ms}$ acceptable margin for A1 commit? |
| **A1** | Reaction Lead Margin | $330.0\text{ ms}$ (`AG3:68`) | $\ge 300.0\text{ ms}$ (`PROPOSED`) | Standard human reaction is $250\text{--}350\text{ ms}$ (`AG3:68`) | Does $300\text{ ms}$ minimum lead feel responsive from idle? |
| **A1** | Post-Commit Yaw Drift | $0.0^\circ$ (Locked) | $\le 2.0^\circ$ (`PROPOSED`) | Strict soulslike heading lock | Is $\le 2.0^\circ$ max drift strict enough for commit locking? |
| **A1b** | Combo Reaction Window | $200\text{--}250\text{ ms}$ (`AG3:90`) | $\ge 180.0\text{ ms}$ (`PROPOSED`) | Justified by combo anticipation | Does $180\text{ ms}$ minimum reaction window feel fair on follow-up? |
| **A2** | Apex Hold Lead Duration | None in freeze (`AG31:69`) | $\ge 400.0\text{ ms}$ (`PROPOSED`) | Heavy charged attack telegraph | Should heavy slam have minimum $400\text{ ms}$ unreactable floor? |
| **A2** | Recovery Punish Window | None in freeze (`AG31:85`)| $\ge 800.0\text{ ms}$ (`PROPOSED`) | Vulnerable grounded weapon rest | Is an $800\text{ ms}$ punish opening desired for heavy slam? |
| **A3a** | Floor Drag Heading Drift | $0.0^\circ$ (Locked) | $\le 2.0^\circ$ (`PROPOSED`) | Floor drag rotational stability | Is $\le 2.0^\circ$ drift acceptable during drag windup? |
| **A3b** | Follow-up Commit Window | $0.130\text{ s}$ (`AG3:150`)| $\pm 0.033\text{ s}$ (`PROPOSED`) | Rapid second stage strike | Is $130\text{ ms}$ commit acceptable given spatial branch check? |
| **A4** | Jump Clearance Height | None in freeze (`AG3:177`)| Player $Z > 50\text{ cm}$ (`PROPOSED`)| Standard jump counterplay height | Is $50\text{ cm}$ capsule clearance sufficient to clear low sweep? |
| **A4** | Query Reach Overreach | $380\text{ cm}$ query vs $312\text{ cm}$ tip | Overreach $= 68\text{ cm}$ (`E-008:10`) | Candidate P4 defect pending capture | Keep $68\text{ cm}$ buffer or shrink query to match physical blade? |
| **A5** | Hand Release vs Code | $0.40\text{ s}$ vs $0.45\text{ s}$ | Delta $= 0.050\text{ s}$ (`E-007:7`) | 1 to 1.4 frames @ 20fps (`E-007:3`) | Does 50ms sub-frame release offset feel noticeable in play? |
| **A6** | Shockwave Jump Height | None in freeze (`AG3:217`)| Player $Z > 50\text{ cm}$ (`PROPOSED`)| Jump clearance over expanding ring | Is $50\text{ cm}$ jump clearance standard for shockwave ring? |

---

## 3. C++ Debug Hook Infrastructure & Citation Matrix

The following native C++ inspection endpoints serve as the authoritative telemetry sources for all P1 readability assertions:

| C++ Class | Method Signature | Header Anchor | Source Anchor | Telemetry Function & Assertion Role |
|---|---|---|---|---|
| `URPGAttackTracker` | `bool StartMove(FName MoveId, bool bForce)` | [`RPGAttackTracker.h:96`](file:///c:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGAttackTracker.h#L96) | [`RPGAttackTracker.cpp:234`](file:///c:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGAttackTracker.cpp#L234) | Triggers tracked move; returns false if boss is busy/vetoed |
| `URPGAttackTracker` | `bool IsNeutral() const` | [`RPGAttackTracker.h:100`](file:///c:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGAttackTracker.h#L100) | [`RPGAttackTracker.cpp:138`](file:///c:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGAttackTracker.cpp#L138) | Verifies boss is free to act (not busy, staggered, waking, transition) |
| `URPGAttackTracker` | `float GetPosition() const` | [`RPGAttackTracker.h:104`](file:///c:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGAttackTracker.h#L104) | Inlined | Reads live montage playback position (seconds) |
| `URPGAttackTracker` | `bool GetTiming(FName MoveId, FRPGAttackTiming& OutTiming) const` | [`RPGAttackTracker.h:107`](file:///c:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGAttackTracker.h#L107) | [`RPGAttackTracker.cpp:124`](file:///c:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGAttackTracker.cpp#L124) | Extracts configured Commit, Active, and Recovery boundaries |
| `URPGAttackTracker` | `FString GetPhaseName() const` | [`RPGAttackTracker.h:152`](file:///c:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGAttackTracker.h#L152) | [`RPGAttackTracker.cpp:213`](file:///c:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGAttackTracker.cpp#L213) | Returns `"None"`, `"Windup"`, `"Committed"`, `"Active"`, `"Recovery"` |
| `URPGAttackTracker` | `bool IsActiveWindow() const` | [`RPGAttackTracker.h:155`](file:///c:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGAttackTracker.h#L155) | Inlined | True during active damage query frames |
| `URPGAttackTracker` | `float GetCommittedYaw() const` | [`RPGAttackTracker.h:161`](file:///c:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGAttackTracker.h#L161) | Inlined | World yaw (degrees) locked at the commitment point |
| `URPGAttackTracker` | `float GetMaxYawDriftAfterCommit() const` | [`RPGAttackTracker.h:175`](file:///c:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGAttackTracker.h#L175) | Inlined | Peak yaw deviation after commit point (must remain $\le 2.0^\circ$) |
| `URPGAttackTracker` | `float GetLastCommitPosition() const` | [`RPGAttackTracker.h:179`](file:///c:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGAttackTracker.h#L179) | Inlined | Montage position where heading was locked |
| `URPGAttackTracker` | `float GetLastActiveStartPosition() const` | [`RPGAttackTracker.h:182`](file:///c:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGAttackTracker.h#L182) | Inlined | Montage position where damage window began |
| `URPGAttackTracker` | `float GetLastStageWindupSeconds() const` | [`RPGAttackTracker.h:188`](file:///c:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGAttackTracker.h#L188) | Inlined | Measured duration of windup stage before commit |
| `URPGAttackTracker` | `int32 GetIllegalStartCount() const` | [`RPGAttackTracker.h:116`](file:///c:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGAttackTracker.h#L116) | Inlined | Starts vetoed by priority rule (stagger, transition, dormant) |
| `URPGAttackTracker` | `int32 GetDoubleLaunchCount() const` | [`RPGAttackTracker.h:119`](file:///c:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGAttackTracker.h#L119) | Inlined | Attacks started while previous attack still active |
| `URPGAttackTracker` | `int32 GetBranchAllowedCount() const` | [`RPGAttackTracker.h:134`](file:///c:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGAttackTracker.h#L134) | Inlined | Combo stage branches permitted by spatial check |
| `URPGAttackTracker` | `int32 GetBranchDeniedCount() const` | [`RPGAttackTracker.h:137`](file:///c:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGAttackTracker.h#L137) | Inlined | Combo stage branches denied by out-of-cone or out-of-range |
| `URPGCombatDebug` | `FString DebugBossMontageAnimName() const` | [`RPGCombatDebug.h:68`](file:///c:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGCombatDebug.h#L68) | [`RPGCombatDebug.cpp:115`](file:///c:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGCombatDebug.cpp#L115) | Verifies active animation asset driving boss mesh |
| `URPGCombatDebug` | `TArray<FString> DebugBossMontageInstances() const` | [`RPGCombatDebug.h:75`](file:///c:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGCombatDebug.h#L75) | [`RPGCombatDebug.cpp:125`](file:///c:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGCombatDebug.cpp#L125) | Inspects blending montage instances and blend weights |
| `URPGCombatDebug` | `void DebugRefillPlayer() const` | [`RPGCombatDebug.h:79`](file:///c:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGCombatDebug.h#L79) | [`RPGCombatDebug.cpp:155`](file:///c:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGCombatDebug.cpp#L155) | Refills player health/stamina for repeatable testing |
| `URPGBossEncounter` | `bool IsDormant() const` | [`RPGBossEncounter.h:42`](file:///c:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGBossEncounter.h#L42) | Inlined | Asserts boss dormancy state |
| `URPGBossEncounter` | `bool IsWaking() const` | [`RPGBossEncounter.h:46`](file:///c:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGBossEncounter.h#L46) | Inlined | Asserts boss waking sequence progress |
| `URPGBossEncounter` | `void HoldForTest(bool bHold)` | [`RPGBossEncounter.h:70`](file:///c:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGBossEncounter.h#L70) | [`RPGBossEncounter.cpp:256`](file:///c:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGBossEncounter.cpp#L256) | Locks/unlocks AI behaviour tree for deterministic test driver runs |
| `URPGBossPhases` | `bool IsInTransition() const` | [`RPGBossPhases.h:99`](file:///c:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGBossPhases.h#L99) | Inlined | Detects active phase transition sequence |
| `URPGBossPhases` | `void ResetPhases()` | [`RPGBossPhases.h:109`](file:///c:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGBossPhases.h#L109) | [`RPGBossPhases.cpp:526`](file:///c:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGBossPhases.cpp#L526) | Restores boss to phase 1 (clears immunity, posture pin, roar) |
| `URPGBossStagger` | `bool IsStaggered() const` | [`RPGBossStagger.h:95`](file:///c:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGBossStagger.h#L95) | Inlined | Asserts boss stance-break vulnerability state |

---

## 4. Move-by-Move Acceptance Assertions

### 4.1 Move A1: Quick Slash (`AM_Boss01_A1` / `AN_Boss01_A1_QuickSlash`)

* **Target Animation Asset:** `/Game/OneBossFight/Boss01/Animations/AM_Boss01_A1`
* **Governing Specification:** `AG3:56-76`

| Assertion ID | Acceptance Assertion Statement | Inspection Hook | Expected Value & Tolerance | Defect Diagnosis on Failure |
|---|---|---|---|---|
| **A1-ASSERT-01** | Montage selection binds correct asset | `URPGCombatDebug::DebugBossMontageAnimName()` | Equals `"AM_Boss01_A1"` or `"AN_Boss01_A1_QuickSlash"` (Source: Asset Registry) | Asset Binding Misalignment |
| **A1-ASSERT-02** | Commitment timestamp alignment | `URPGAttackTracker::GetLastCommitPosition()` | $0.330\text{ s} \pm 0.033\text{ s}$ (Source: `AG3:66`; $\pm 33\text{ms}$ is `PROPOSED`) | Premature / Late Heading Lock |
| **A1-ASSERT-03** | Total reaction lead duration | `GetLastCommitPosition() - 0.0s` | $\ge 0.300\text{ s}$ (Source: `AG3:68` baseline $330\text{ ms}$; $\ge 300\text{ms}$ `PROPOSED`) | Unreactable Twitch Attack ($< 250\text{ ms}$) |
| **A1-ASSERT-04** | Active damage window start | `URPGAttackTracker::GetLastActiveStartPosition()` | $0.350\text{ s} \pm 0.033\text{ s}$ (Source: `AG3:67`; $\pm 33\text{ms}$ is `PROPOSED`) | Premature Damage Infliction |
| **A1-ASSERT-05** | Post-commit heading drift | `URPGAttackTracker::GetMaxYawDriftAfterCommit()` | $\le 2.0^\circ$ (`PROPOSED` soulslike lock threshold) | Soulslike Turn-Tracking Defect |

---

### 4.2 Move A1b: Quick Slash Combo Follow-up (`AN_Boss01_A1b_QuickSlashCombo`)

* **Target Animation Asset:** `AN_Boss01_A1b_QuickSlashCombo`
* **Governing Specification:** `AG3:79-97`

| Assertion ID | Acceptance Assertion Statement | Inspection Hook | Expected Value & Tolerance | Defect Diagnosis on Failure |
|---|---|---|---|---|
| **A1b-ASSERT-01** | Execution requires A1 precursor | `URPGAttackTracker::GetAttackInstance()` | Increments only following active A1 (Source: `AG3:95`) | Illegal Standalone A1b Launch |
| **A1b-ASSERT-02** | Combo commit timing | `URPGAttackTracker::GetLastCommitPosition()` | $0.200\text{ s} \pm 0.033\text{ s}$ (Source: `AG3:88`; $\pm 33\text{ms}$ is `PROPOSED`) | Combo Timing Drift |
| **A1b-ASSERT-03** | Combo reaction lead margin | `GetLastCommitPosition() - 0.0s` | $200.0\text{--}250.0\text{ ms}$ (Source: `AG3:90`; $\ge 180\text{ms}$ is `PROPOSED`) | Unavoidable Combo Trap ($< 150\text{ ms}$) |
| **A1b-ASSERT-04** | Active damage window start | `URPGAttackTracker::GetLastActiveStartPosition()` | $0.250\text{ s} \pm 0.033\text{ s}$ (Source: `AG3:89`; $\pm 33\text{ms}$ is `PROPOSED`) | Phantom Pre-Swing Damage |
| **A1b-ASSERT-05** | Heading lock after commit | `URPGAttackTracker::GetMaxYawDriftAfterCommit()` | $\le 2.0^\circ$ (`PROPOSED` threshold) | Excessive Tracking on Follow-up |

---

### 4.3 Move A2: Heavy Overhead Slam / Charged Attack (`GS_ChargedAttack` / Authored Trio)

* **Target Animation Asset:** `GS_ChargedAttack_Montage` / (`AN_Boss01_A2_Raise`, `AN_Boss01_A2_Slam`)
* **Governing Specification:** `AG3:99-118`, `AG31:60-73`

| Assertion ID | Acceptance Assertion Statement | Inspection Hook | Expected Value & Tolerance | Defect Diagnosis on Failure |
|---|---|---|---|---|
| **A2-ASSERT-01** | Apex hold windup lead duration | `URPGAttackTracker::GetLastStageWindupSeconds()` | $\ge 400.0\text{ ms}$ (`PROPOSED`: NO SOURCE IN FREEZE; `AG31:69`) | Unreactable Heavy Attack ($< 350\text{ ms}$) |
| **A2-ASSERT-02** | Heading lock during apex hold | `URPGAttackTracker::GetMaxYawDriftAfterCommit()` | $\le 1.5^\circ$ (`PROPOSED` heavy attack threshold) | Mid-Air Tracking Snapping |
| **A2-ASSERT-03** | Active damage window start | `URPGAttackTracker::GetLastActiveStartPosition()` | Matches active notify onset ($\pm 0.033\text{ s}$ `PROPOSED`) | Desync between Visual Slam and Trace |
| **A2-ASSERT-04** | Recovery punish vulnerability | Grounded weapon rest interval | $\ge 800.0\text{ ms}$ (`PROPOSED`: NO SOURCE IN FREEZE; `AG31:85`) | Unpunishable Boss Recovery ($< 650\text{ ms}$) |
| **A2-ASSERT-05** | Early AI cancel prohibition | `URPGAttackTracker::GetPhaseName()` | Remains `"Recovery"` for $\ge 650\text{ ms}$ (`PROPOSED` threshold) | Illegal Super-Armor Recovery Cancel |

---

### 4.4 Move A3a: Heavy Underhand Sweep (`AM_Boss01_A3a` / `AN_Boss01_A3a_Combo1`)

* **Target Animation Asset:** `AM_Boss01_A3a`
* **Governing Specification:** `AG3:120-138`

| Assertion ID | Acceptance Assertion Statement | Inspection Hook | Expected Value & Tolerance | Defect Diagnosis on Failure |
|---|---|---|---|---|
| **A3a-ASSERT-01** | Tracking commitment position | `URPGAttackTracker::GetLastCommitPosition()` | $0.380\text{ s} \pm 0.033\text{ s}$ (Source: `AG3:129`; $\pm 33\text{ms}$ is `PROPOSED`) | Premature Drag Commitment |
| **A3a-ASSERT-02** | Reaction telegraph lead | Windup to commit interval | $380.0\text{ ms} \pm 33.3\text{ ms}$ (Source: `AG3:36`; $\pm 33\text{ms}$ is `PROPOSED`) | Insufficient Underhand Cue |
| **A3a-ASSERT-03** | Active trace window onset | `URPGAttackTracker::GetLastActiveStartPosition()` | $0.400\text{ s} \pm 0.033\text{ s}$ (Source: `AG3:130`; $\pm 33\text{ms}$ is `PROPOSED`) | Active Trace Window Drift |
| **A3a-ASSERT-04** | Floor drag heading stability | `URPGAttackTracker::GetMaxYawDriftAfterCommit()` | $\le 2.0^\circ$ (`PROPOSED` threshold) | Floor Drag Tracking Error |

---

### 4.5 Move A3b: Overhead Hammer-Strike Combo (`AM_Boss01_A3b` / `AN_Boss01_A3b_Combo2`)

* **Target Animation Asset:** `AM_Boss01_A3b`
* **Governing Specification:** `AG3:141-158`, Freeze Section 16 A3 (`RPGAttackTracker.h:121-127`)

| Assertion ID | Acceptance Assertion Statement | Inspection Hook | Expected Value & Tolerance | Defect Diagnosis on Failure |
|---|---|---|---|---|
| **A3b-ASSERT-01** | Branch spatial gating (Range) | `URPGAttackTracker::BranchRange` | Player distance $\le 400.0\text{ cm}$ (Source: Freeze Section 16 A3) | Out-of-Range Attack Chaining |
| **A3b-ASSERT-02** | Branch spatial gating (Cone) | `URPGAttackTracker::BranchConeDegrees` | Frontal cone $\pm 60.0^\circ$ ($120.0^\circ$ total; Freeze Section 16 A3) | Blind 360-Degree Combo Branching |
| **A3b-ASSERT-03** | Out-of-cone branch rejection | `URPGAttackTracker::GetBranchDeniedCount()` | Increments by 1; montage stopped at $0.0\text{ s}$ | Phantom Branch Denial Failure |
| **A3b-ASSERT-04** | Within-cone branch acceptance | `URPGAttackTracker::GetBranchAllowedCount()` | Increments by 1; montage proceeds | False Branch Veto |
| **A3b-ASSERT-05** | Commit position on branch | `URPGAttackTracker::GetLastCommitPosition()` | $0.130\text{ s} \pm 0.033\text{ s}$ (Source: `AG3:150`; $\pm 33\text{ms}$ is `PROPOSED`) | Follow-up Timing Drift |

---

### 4.6 Move A4: Ground Low Sweep (`AN_Boss01_A4_LowSweep` / `RPGBossLowSweep`)

* **Target Animation Asset:** `AN_Boss01_A4_LowSweep`
* **Governing Specification:** `AG3:161-179`, `AG31:41-57`, `E-008:7-13`

| Assertion ID | Acceptance Assertion Statement | Inspection Hook | Expected Value & Tolerance | Defect Diagnosis on Failure |
|---|---|---|---|---|
| **A4-ASSERT-01** | Low sweep heading commit | `URPGAttackTracker::GetLastCommitPosition()` | $0.400\text{ s} \pm 0.033\text{ s}$ (Source: `AG3:171`; $\pm 33\text{ms}$ is `PROPOSED`) | Premature / Late Sweep Heading Lock |
| **A4-ASSERT-02** | Active query window duration | Active query duration in montage | $[0.609, 0.879]\text{ s}$ (Source: `E-008:10`, 12 ticks; duration $0.270\text{ s}$) | Query Window Duration Misalignment |
| **A4-ASSERT-03** | Jump counterplay clearance | Player $Z$-elevation $> 50.0\text{ cm}$ | 0 damage taken when player jumps at $0.33\text{ s}$ (`PROPOSED`) | Unjumpable Low Sweep (Hitbox Too Tall) |
| **A4-ASSERT-04** | Query reach vs visible blade | `RPGBossLowSweep::Reach` vs Tip | $380\text{ cm}$ query vs $312\text{ cm}$ tip ($68\text{ cm}$ delta per `E-008:10`) | Overreach Discrepancy (P4 Candidate) |
| **A4-ASSERT-05** | Floor dip reference stability | Visible tip $Z$ elevation vs floor | Measured dip at $[0.730, 0.807]\text{ s}$ (Source: `E-008:12`) | Candidate Ground Clipping Defect |

---

### 4.7 Move A5: Gauntlet Ember Javelin (`AN_Boss01_A5_JavelinThrow` / `RPGBossHealPunish`)

* **Target Animation Asset:** `AN_Boss01_A5_JavelinThrow`
* **Governing Specification:** `AG3:181-198`, `AG31:24-40`, `E-007:3-8`

| Assertion ID | Acceptance Assertion Statement | Inspection Hook | Expected Value & Tolerance | Defect Diagnosis on Failure |
|---|---|---|---|---|
| **A5-ASSERT-01** | Trigger response predicate | `URPGBossHealPunish` activation | Fires on player potion montage edge (Source: `E-007:8`) | Inactive / Unresponsive Heal Punish |
| **A5-ASSERT-02** | Distance engagement gating | Range between Player and Boss | Refuses if range $< 400\text{ cm}$ or $> 1000\text{ cm}$ (Source: `E-007:8`) | Out-of-Range Projectile Trigger |
| **A5-ASSERT-03** | Code active window release | Projectile spawn timestamp | $0.450\text{ s}$ nominal / $0.470\text{ s}$ sampled (Source: `E-007:3,5`) | Projectile Spawn Timing Drift |
| **A5-ASSERT-04** | Author intent vs code release | Temporal offset from sidecar marker | $0.050\text{ s}$ nominal / $0.070\text{ s}$ sampled (Source: `E-007:3,7`) | Sub-frame visual release desync |
| **A5-ASSERT-05** | Heading lock after release | `URPGAttackTracker::GetMaxYawDriftAfterCommit()` | Drift $= 0.00^\circ$ after release (Source: `E-007:5`) | Mid-Flight Javelin Homing Defect |

---

### 4.8 Move A6: Phase 2 Leap Slam (`GS_LeapAttack_Montage` / `RPGBossShockwave`)

* **Target Animation Asset:** `GS_LeapAttack_Montage`
* **Governing Specification:** `AG3:200-218`, Freeze Section 16 A6 (`RPGBossPhases.h:85-93`)

| Assertion ID | Acceptance Assertion Statement | Inspection Hook | Expected Value & Tolerance | Defect Diagnosis on Failure |
|---|---|---|---|---|
| **A6-ASSERT-01** | Phase 1 lock invariant | `URPGBossPhases::IsLeapBlocked()` | `True` during Phase 1 (Source: Freeze Section 16 A6) | Premature Phase 2 Leap in Phase 1 |
| **A6-ASSERT-02** | Phase 2 unlock invariant | `URPGBossPhases::IsLeapBlocked()` | `False` after phase transition completes (Freeze Section 16 A6) | Leap Remains Blocked in Phase 2 |
| **A6-ASSERT-03** | Airborne tracking freeze | `URPGAttackTracker::GetLastCommitPosition()` | $0.691\text{ s} \pm 0.033\text{ s}$ (Source: `AG3:210`; $\pm 33\text{ms}$ is `PROPOSED`) | Mid-Air Homing Snapping |
| **A6-ASSERT-04** | Ground impact & shockwave onset | Impact timestamp | $0.754\text{ s} \pm 0.033\text{ s}$ (Source: `AG3:211`; $\pm 33\text{ms}$ is `PROPOSED`) | Impact Visual / Damage Desync |
| **A6-ASSERT-05** | Jump shockwave clearance | Player $Z$-elevation $> 50.0\text{ cm}$ | 0 damage taken at radius $600\text{ cm}$ (`PROPOSED`) | Unjumpable Shockwave Ring |

---

## 5. Priority Invariants & State Machine Safety Assertions

The soulslike combat system enforces strict hierarchical priority (Master Design Freeze Section 21). Attacks may never preempt higher-priority defensive or transition states:

| Invariant ID | State Machine Invariant Statement | Native C++ Hook | Expected Evaluation | Rejection Defect |
|---|---|---|---|---|
| **PRI-ASSERT-01** | Stagger outranks attack initiation | `tracker.start_move(M, True)` while `stagger.is_staggered()` | Returns `False`; `GetIllegalStartCount()` increments (Freeze 21) | Attack Interrupted Stance Break |
| **PRI-ASSERT-02** | Phase transition outranks attack | `tracker.start_move(M, True)` while `phases.is_in_transition()` | Returns `False`; `GetIllegalStartCount()` increments (Freeze 21) | Attack Clipped Phase Transition Roar |
| **PRI-ASSERT-03** | Dormancy outranks attack | `tracker.start_move(M, True)` while `encounter.is_dormant()` | Returns `False`; `GetIllegalStartCount()` increments (Freeze 21) | Attack Fired While Sleeping |
| **PRI-ASSERT-04** | Waking sequence outranks attack | `tracker.start_move(M, True)` while `encounter.is_waking()` | Returns `False`; `GetIllegalStartCount()` increments (Freeze 21) | Attack Fired During Wake Animation |
| **PRI-ASSERT-05** | Double launch prevention | `tracker.start_move(M, True)` while `tracker.is_active_window()` | Returns `False`; `GetDoubleLaunchCount()` increments (Freeze 21) | Cancel-Stuck Animation Glitch |
| **PRI-ASSERT-06** | Zero illegal starts in clean combat | `URPGAttackTracker::GetIllegalStartCount()` | Exactly `0` at completion of natural duel | Spurious State Collisions |

---

## 6. Verification & Hash Anchor

| Deliverable File | Target Task | Governing Spec | SHA256 Status |
|---|---|---|---|
| [`AG32_P1_ACCEPTANCE_ASSERTIONS.md`](file:///c:/UnrealProject/OneBossFight/Docs/BossCombatReview/Execution/Antigravity/AG32_P1_ACCEPTANCE_ASSERTIONS.md) | **A-T2 (Rev 02)** | `AG3_TELEGRAPH_READABILITY_SPEC.md` | *(Updated below)* |
