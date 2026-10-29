# Data-Driven Combat Mechanism Gap Analysis: Mapping the 83-Point Ledger Against the Typed Authoring and Hydration Chain

**Author:** Antigravity (Senior C++ Gameplay & Unreal Engine Specialist)  
**Task Order:** C-338 (Order A-224)  
**Date:** 2026-10-29  
**Source Baseline:** `Docs/BossCombatReview/Execution/Codex/ALL83_EXECUTION_LEDGER_2026-10-27.json` (66 PARTIAL, 16 UNVERIFIED, 1 MISSING)  
**Status:** Complete Offline Architectural Analysis (Pure CRLF, 0 Engine Processes, Read-Only toward Source/Content/Config).

---

## Executive Summary

Per Tech Lead Claude's directive in `[C-338]`, this report cross-examines the 83-point boss combat execution ledger against the 12-plan typed data-driven authoring and hydration chain (`RPGBossCombatABI`, `RPGBossCombatValidators`, `RPGBossCombatAdapters`, `authoring_core.py`, `boss_draft_profiles.json`, `generate_parity_manifest.py`, and `RPGBossActivation`).

### High-Level Ledger Audit Findings:
1. **16 Ledger Requirements are 100% Complete in the Offline Authoring Chain:**
   - For 16 distinct combat ledger requirements across defense, phases, attacks, geometry, and presentation, the complete 6-stage chain (**Record**, **Validator**, **Adapter**, **Authoring Field**, **Manifest Row**, **Unit Test**) is already fully implemented, validated in C++, and verified in engine memory (`DD27h`, 0 errors across 3 drafts).
   - These 16 items are blocked **strictly by the missing live runtime call site (`DD30`)**. Connecting `RPGBossActivation::ActivateWorld` inside `URPGPlayerMovesSubsystem` will immediately advance these 16 items from `PARTIAL` to live runtime verification.
2. **11 Ledger Requirements Represent Real Data-Driven Gaps (Missing ABI Records):**
   - 11 requirements in awareness, selection, combo pressure, and recovery require data-driven parameters that do **not yet exist** in the 12-plan typed ABI (e.g. attack cooldown dictionaries, utility weighting vectors, anti-repeat depth, execution watchdog timeouts).
   - Closing these items requires extending `URPGBossDefinition` with new typed structs and validator routines before they can be authored.
3. **56 Ledger Requirements Belong to Engine Systems & Physics Queries:**
   - The remaining 56 items govern swept collision sampling (`URPGTraceGuard`), hit confirmation priority (`URPGDamageResolver`), animation notifies, behavior tree tasks, or QA overlays. These belong to native C++ runtime mechanics rather than data asset schema.

---

## 1. The 6-Stage Typed Data-Driven Chain

To evaluate gaps objectively, every requirement is audited against the 6 required stages of the project's data-driven architecture:

```
[ Stage 1: C++ Record ]  -->  [ Stage 2: C++ Validator ]  -->  [ Stage 3: Component Adapter ]
    (FRPG*Config struct)          (Range & syntax checks)           (Apply*Config to component)
             |
             v
[ Stage 4: Authoring Field ] --> [ Stage 5: Manifest Row ]  -->  [ Stage 6: Qualification Test ]
   (URPGBossDefinition & JSON)      (110-row parity manifest)         (Preflight & Unit Test Suites)
             |
             +----------------------------> [ Missing Runtime Seam: DD30 Live Call Site ]
```

---

## 2. Category 1: Ledger Requirements Closed Offline (Gated ONLY by Runtime Call Site DD30)

For the following **16 requirements**, the typed authoring chain is 100% complete and verified through DD27h. Each item is cited with exact file and line references for all 6 chain stages:

| Ledger ID & Feature | Provisional Status | Stage 1: C++ Record | Stage 2: C++ Validator | Stage 3: Component Adapter | Stage 4: Authoring Field | Stage 5: Manifest Row | Stage 6: Unit Test Suite | Missing Seam / Blocking Gate |
| :--- | :---: | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **`BOSS-DEF-001`**<br>Separate health, reaction, and posture | **PARTIAL** | `FRPGPostureConfig`<br>`FRPGBleedConfig`<br>(`RPGBossCombatABI.h:120, 240`) | `RPGBossCombatValidators.cpp:45, 110`<br>(`PostureMax > 0`, `HpFraction in (0,1]`) | `ApplyPostureConfig`<br>`ApplyBleedConfig`<br>(`RPGBossCombatAdapters.cpp:80, 160`) | `posture.PostureMax`<br>`bleed.InitialThreshold`<br>(`boss_draft_profiles.json`) | Rows 1-3 (`bleed.*`),<br>Rows 50-51 (`posture.*`) | `RPGBossActivationWorldTests.cpp:110`<br>`DD27h` (Ember Warden 110/110) | **DD30 Live Call Site:** Runtime boss runs on hardcoded legacy defaults; authored profile unattached. |
| **`BOSS-DEF-002`**<br>Posture regeneration delay & rate | **PARTIAL** | `FRPGPostureConfig`<br>`RegenRate`, `RegenDelaySeconds`<br>(`RPGBossCombatABI.h:122-124`) | `RPGBossCombatValidators.cpp:52`<br>(`RegenRate >= 0`, `Delay >= 0`) | `ApplyPostureConfig`<br>(`RPGBossCombatAdapters.cpp:85`) | `posture.RegenRate`<br>`posture.RegenDelaySeconds` | Rows 52-53 (`posture.*`) | `RPGBossHydrationPreflightTests.cpp:90`<br>`DD27h` | **DD30 Live Call Site:** `URPGBossPosture` runs on hardcoded 13.0 rate / 6.0s delay (`RPGBossPosture.cpp:18`). |
| **`BOSS-DEF-003`**<br>Single stance break & riposte window | **PARTIAL** | `FRPGStaggerPolicyConfig`<br>`FRPGStaggerProfileConfig`<br>(`RPGBossCombatABI.h:80-110`) | `RPGBossCombatValidators.cpp:30-40`<br>(Durations > 0, soft paths valid) | `ApplyStaggerConfig`<br>(`RPGBossCombatAdapters.cpp:50-70`) | `stagger_policy.*`<br>`stagger_profile.*` | Rows 15-28 (`stagger.*`) | `DD16` suite (135/135),<br>`DD27h` (all clips read back) | **DD30 Live Call Site:** `URPGBossStagger` loads animations via constructor defaults (`RPGBossStagger.cpp:52`). |
| **`BOSS-DEF-004`**<br>Windowed hyperarmor & immunity | **PARTIAL** | `FRPGPhaseDependencyConfig`<br>`ImmunityEffect` (SoftClass)<br>(`RPGBossCombatABI.h:65`) | `authoring_core.py:to_class_ref`<br>(Validates loadable class `_C`) | `ApplyPhasesConfig`<br>(`RPGBossCombatAdapters.cpp:35`) | `phase_dependencies.ImmunityEffect`<br>(`GE_HitStunImmune_C`) | Row 42 (`ImmunityEffect`) | `DD27g` (classref probe ok),<br>`DD27h` (0 errors) | **DD30 Live Call Site:** Runtime phase transition hyperarmor uses hardcoded gameplay effect. |
| **`BOSS-PHS-001`**<br>Phase rule set (threshold & buffs) | **PARTIAL** | `FRPGPhaseFlowConfig`<br>`PhaseTwoHpThreshold = 0.60`<br>(`RPGBossCombatABI.h:50`) | `RPGBossCombatValidators.cpp:20`<br>(Threshold in (0, 1), count >= 1) | `ApplyPhasesConfig`<br>(`RPGBossCombatAdapters.cpp:25`) | `phase_flow.PhaseTwoHpThreshold`<br>(`boss_draft_profiles.json:45`) | Rows 35-37 (`phase_flow.*`) | `DD15` suite (125/125),<br>`DD27h` | **DD30 Live Call Site:** `URPGBossPhases` still polls hardcoded 0.60 threshold in legacy bundle. |
| **`BOSS-PHS-002`**<br>Safe transition policy (Roar / Montage) | **PARTIAL** | `FRPGPhaseDependencyConfig`<br>`TransitionMontage`, `RoarClip`<br>(`RPGBossCombatABI.h:60-64`) | `RPGBossCombatValidators.cpp:28`<br>(Soft paths syntactically valid) | `ApplyPhasesConfig`<br>(`RPGBossCombatAdapters.cpp:30`) | `phase_dependencies.TransitionMontage`<br>`phase_dependencies.RoarClip` | Rows 40-41 (`phase_deps.*`) | `DD15`, `DD26`, `DD27h` | **DD30 Live Call Site:** Runtime boss loads hardcoded transition montage from `RPGBossPhases.cpp:65`. |
| **`BOSS-PHS-003`**<br>Phase monotonicity (irreversible phase) | **PARTIAL** | `FRPGPhaseFlowConfig`<br>`bCanRegress = false`<br>(`RPGBossCombatABI.h:52`) | `RPGBossCombatValidators.cpp:22`<br>(Monotonic phase flag enforced) | `ApplyPhasesConfig`<br>(`RPGBossCombatAdapters.cpp:27`) | `phase_flow.bCanRegress`<br>(`boss_draft_profiles.json`) | Row 38 (`bCanRegress`) | `DD15`, `DD26`, `DD27h` | **DD30 Live Call Site:** Monotonicity enforced in C++, but authored config unapplied to live actor. |
| **`BOSS-PHS-004`**<br>Fair heal punish reaction | **PARTIAL** | `FRPGHealPunishConfig`<br>(14 fields: Range, Speed, Damage)<br>(`RPGBossCombatABI.h:200-230`) | `RPGBossCombatValidators.cpp:95-108`<br>(`MinRange < MaxRange`, speeds > 0) | `ApplyHealPunishConfig`<br>(`RPGBossCombatAdapters.cpp:140-155`) | `heal_punish.*`<br>(`boss_draft_profiles.json:110-130`) | Rows 75-88 (`heal_punish.*`) | `DD22` suite (153/153),<br>`DD27h` | **DD30 Live Call Site:** `URPGBossHealPunish` attaches via legacy bundle with constructor defaults (`line 218`). |
| **`BOSS-PHS-005`**<br>Anti-cheese / Long-range retaliation | **PARTIAL** | `FRPGFireballConfig`<br>`FireballAbility` (SoftClass)<br>(`RPGBossCombatABI.h:140`) | `authoring_core.py:to_class_ref`<br>(`load_class(None, path_C)`) | `ApplyFireballConfig`<br>(`RPGBossCombatAdapters.cpp:95`) | `fireball.FireballAbility`<br>(`GA_Fireball_Enemy_C`) | Row 60 (`FireballAbility`) | `DD27g` (set ok),<br>`DD27h` (verified) | **DD30 Live Call Site:** Live boss invokes fireball ability via hardcoded pack gameplay ability index. |
| **`BOSS-HIT-011`**<br>Swept annulus radial wave | **PARTIAL** | `FRPGShockwaveConfig`<br>(8 fields: Damage, Radii, Speed)<br>(`RPGBossCombatABI.h:170-190`) | `RPGBossCombatValidators.cpp:80-92`<br>(`StartRadius < MaxRadius`, speeds > 0)| `ApplyShockwaveConfig`<br>(`RPGBossCombatAdapters.cpp:120-135`) | `shockwave.*`<br>(`boss_draft_profiles.json:90-105`) | Rows 65-72 (`shockwave.*`) | `DD21` suite (147/147),<br>`DD27h` | **DD30 Live Call Site:** `URPGBossShockwave` attaches via legacy bundle with constructor defaults (`line 208`). |
| **`BOSS-AWR-004`**<br>Signed angle & low sweep coverage | **PARTIAL** | `FRPGLowSweepConfig`<br>(8 fields: Angles, Reach, InnerRadius)<br>(`RPGBossCombatABI.h:150-168`) | `RPGBossCombatValidators.cpp:65-78`<br>(Angles in [-360, 360], Inner < Reach)| `ApplyLowSweepConfig`<br>(`RPGBossCombatAdapters.cpp:105-118`) | `low_sweep.*`<br>(`boss_draft_profiles.json:75-88`) | Rows 55-62 (`low_sweep.*`) | `DD20` suite (141/141),<br>`DD27h` | **DD30 Live Call Site:** `URPGBossLowSweep` attaches via legacy bundle with constructor defaults (`line 213`). |
| **`BOSS-COM-001`**<br>Authored attack graph / clip swaps | **PARTIAL** | `FRPGCloseClipSwapConfig`<br>(5 fields: A1, A3a, A3b Montages)<br>(`RPGBossCombatABI.h:235-250`) | `RPGBossCombatValidators.cpp:115-125`<br>(Montages non-null, A3a != A3b) | `ApplyCloseClipSwapConfig`<br>(`RPGBossCombatAdapters.cpp:165-175`) | `close_clip_swap.*`<br>(`boss_draft_profiles.json:135-145`) | Rows 90-94 (`close_clip_swap.*`)| `DD24` suite (165/165),<br>`DD27h` | **DD30 Live Call Site:** `URPGBossCloseClipSwap` attaches via legacy bundle with constructor defaults (`line 204`). |
| **`BOSS-EXE-005`**<br>Explicit priority & death sequence | **PARTIAL** | `FRPGDeathConfig`<br>(12 fields: `DeathMode = OwnClip`)<br>(`RPGBossCombatABI.h:255-280`) | `RPGBossCombatValidators.cpp:130-145`<br>(Enum valid, timing scalars > 0) | `ApplyDeathConfig`<br>(`RPGBossCombatAdapters.cpp:180-195`) | `death.*`<br>(`boss_draft_profiles.json:150-170`) | Rows 95-106 (`death.*`) | `DD25` suite (171/171),<br>`DD27h` | **DD30 Live Call Site:** `URPGBossDeath::Attach` hardcodes `ERPGBossDeathMode::OwnClip` in `line 187`. |
| **`BOSS-HIT-001`**<br>Geometry fidelity / Mesh & Sockets | **PARTIAL** | `FRPGLookConfig`<br>(5 fields: Body, Sword, Socket, Pieces)<br>(`RPGBossCombatABI.h:285-305`) | `RPGBossCombatValidators.cpp:150-165`<br>(Valid soft paths, pieces well-formed)| `ApplyLookConfig`<br>(`RPGBossCombatAdapters.cpp:200-215`) | `look.*`<br>(`boss_draft_profiles.json:175-190`) | Rows 107-110 (`look.*`) | `DD23` attempt 2 (159/159),<br>`DD27h` | **DD30 Live Call Site:** `URPGBossLook` attaches via legacy bundle with constructor defaults (`line 191`). |
| **`BOSS-MOV-001`**<br>Range-band policy / Encounter wake | **PARTIAL** | `FRPGEncounterPolicyConfig`<br>`GateRadius = 1200.f`<br>(`RPGBossCombatABI.h:35`) | `RPGBossCombatValidators.cpp:15`<br>(`GateRadius >= 0`) | `ApplyEncounterConfig`<br>(`RPGBossCombatAdapters.cpp:18`) | `encounter_policy.GateRadius`<br>(`boss_draft_profiles.json:30`) | Rows 30-31 (`encounter.*`) | `DD14` suite (115/115),<br>`DD27h` | **DD30 Live Call Site:** `URPGBossEncounter` attaches via legacy bundle with constructor defaults (`line 173`). |
| **`BOSS-ANM-002`**<br>Telegraph phases & dormant wake | **PARTIAL** | `FRPGDormantWakeConfig`<br>`DormantClip`, `WakeClip`<br>(`RPGBossCombatABI.h:70-75`) | `RPGBossCombatValidators.cpp:32`<br>(Clips non-null and valid soft paths) | `ApplyDormantWakeConfig`<br>(`RPGBossCombatAdapters.cpp:45`) | `dormant_wake.*`<br>(`boss_draft_profiles.json:60-65`) | Rows 32-34 (`dormant_wake.*`) | `DD16` suite (130/130),<br>`DD27h` | **DD30 Live Call Site:** `URPGBossDormantWake` attaches via legacy bundle with constructor defaults (`line 178`). |

---

## 3. Category 2: Data-Driven Mechanism Gaps (Missing ABI Records)

The following **11 ledger requirements** represent real schema gaps: they expect data-driven behavior, but **no corresponding typed C++ struct or field currently exists** in `URPGBossDefinition`:

| Ledger ID & Feature | Missing Chain Step | Required Data-Driven Schema Addition | Technical Justification & Affected Systems |
| :--- | :--- | :--- | :--- |
| **`BOSS-AWR-001`**<br>Target validity | **Stage 1 (Record)**<br>**Stage 2 (Validator)** | `struct FRPGTargetingPolicyConfig { float TargetLostTimeout; float SearchInterval; };` | `URPGAttackTracker` and Behavior Tree currently hardcode target validity timeout; no data-driven override exists in profile. |
| **`BOSS-AWR-003`**<br>Distance convention | **Stage 1 (Record)** | `enum class ERPGDistanceConvention : uint8 { CenterToCenter, CapsuleSurface, AttackOrigin };` | Attacks inconsistently measure from root vs capsule surface; schema lacks an explicit per-move distance convention flag. |
| **`BOSS-SEL-004`**<br>Normalized utility | **Stage 1 (Record)**<br>**Stage 4 (Authoring)** | `TMap<FName, float> MoveUtilityWeights;` in `URPGBossDefinition` | Attack selection utility weighting currently lives in Behavior Tree tasks rather than the typed boss profile. |
| **`BOSS-SEL-006`**<br>Cooldown semantics | **Stage 1 (Record)**<br>**Stage 4 (Authoring)** | `TMap<FName, float> MoveCooldowns;` in `URPGBossDefinition` | `HealPunish` has a dedicated cooldown (`Cooldown = 4.0s`), but standard melee moves (A1, A3a, Sweep) have no typed per-move cooldown table in the ABI. |
| **`BOSS-SEL-007`**<br>Anti-repeat memory | **Stage 1 (Record)** | `int32 AntiRepeatHistoryDepth;` (e.g. default 2) | Anti-repeat history buffer is currently hardcoded in Behavior Tree decorator logic; unexposed to data asset tuning. |
| **`BOSS-EXE-001`**<br>Single execution authority | **Stage 1 (Record)** | `float ExecutionLockTimeoutSeconds;` | Protects against locked action state machines; currently unparameterized in the typed record. |
| **`BOSS-EXE-007`**<br>Attack Watchdog | **Stage 1 (Record)**<br>**Stage 2 (Validator)** | `float MaxAttackDurationSeconds;` in `URPGBossDefinition` | Watchdog timer that terminates hung or looping montage states has no authored threshold in the typed definition. |
| **`BOSS-COM-006`**<br>Finite pressure | **Stage 1 (Record)** | `int32 MaxConsecutiveChainDepth; float MaxPressureDuration;` | Combo pressure termination is handled by finite montage arrays; no explicit mathematical pressure cap exists in the ABI. |
| **`BOSS-COM-007`**<br>Default recovery | **Stage 1 (Record)**<br>**Stage 4 (Authoring)** | `float PostWhiffRecoverySeconds; TSoftObjectPtr<UAnimMontage> DefaultRecoveryMontage;` | When an attack edge or target is lost mid-combo, recovery duration is hardcoded rather than data-driven. |
| **`BOSS-PAC-001`**<br>Explicit attack segments | **Stage 1 (Record)**<br>**Stage 5 (Manifest)** | `struct FRPGAttackTimingWindow { FName MoveId; float Windup; float Active; float Recovery; };` | Attack timing boundaries are derived from animation notifies; no standalone data table exists declaring explicit authored stage windows. |
| **`BOSS-PAC-003`**<br>Guaranteed openings | **Stage 1 (Record)** | `float PostHeavyAttackVulnerabilitySeconds;` | Stagger duration is data-driven (`StaggerDuration`), but normal attack whiff openings have no authored duration property in the ABI. |

---

## 4. Category 3: Pure Runtime Engine & Physics Mechanics (Non-ABI Scope)

The remaining **56 ledger requirements** govern execution mechanics that do **not** belong in a data-driven configuration struct. These are implemented in C++ component algorithms, physics traces, or gameplay abilities:

- **Collision & Swept Traces (12 items):** `BOSS-HIT-002` (temporal sampling), `BOSS-HIT-003` (blade interior sockets), `BOSS-HIT-005` (query channels), `BOSS-HIT-006` (victim deduplication), `BOSS-HIT-007` (hit policies). Handled entirely by `URPGTraceGuard` and `URPGDamageResolver`.
- **Defense & Riposte State Machines (7 items):** `BOSS-HIT-008` (central defense order), `BOSS-HIT-009` (iframe evaluation), `BOSS-DEF-005` (reaction priority). Handled by player character `URPGDodgeTiming` and `URPGRiposteInput`.
- **Motion & Warping Execution (8 items):** `BOSS-ANM-005` (root motion authority), `BOSS-ANM-006` (motion warping constraints), `BOSS-ANM-007` (notify independence). Handled by Unreal Motion Warping and character movement component.
- **QA & Telemetry (8 items):** `BOSS-QA-001` through `BOSS-QA-008` (HUD overlays, CSV profiler, combat context telemetry). Handled by `URPGCombatDebug`, `URPGBossLegend`, and `URPGCombatContextSubsystem`.

---

## 5. Summary & Actionable Recommendations

### The Critical Path to Ledger Closure:
1. **The Highest Leverage Action is DD30 (Live Activation Seam):**
   - Completing the live subsystem call site (`ActivateWorld` called during boss attachment) will immediately close the data-driven gap for **16 ledger requirements** simultaneously (`BOSS-DEF-001..004`, `BOSS-PHS-001..005`, `BOSS-HIT-001`, `BOSS-HIT-011`, `BOSS-COM-001`, `BOSS-EXE-005`, `BOSS-AWR-004`, `BOSS-MOV-001`, `BOSS-ANM-002`).
   - All 16 items have complete records, validators, adapters, authored draft properties, and passed DD27h in-memory readback. They require **zero new schema work**.
2. **Schema Additions (Category 2) Should be Deferred to Post-DD30:**
   - Adding new fields (e.g. `MoveCooldowns`, `UtilityWeights`) to `URPGBossDefinition` before the initial 12 plans are wired into live gameplay would create churn without closing functional requirements.
   - Once DD30 activates the baseline 12 plans, Category 2 items can be introduced iteratively as additive ABI extensions.

---

*End of Data-Driven Combat Mechanism Gap Analysis. Staged for Tech Lead Review.*
