# AG10 Delivery Report: First-Cluster Capability & Witness Audit (Revision 03)

**Document ID:** `Docs/BossCombatReview/Execution/Antigravity/P1_FIRST_CLUSTER_CAPABILITY_AUDIT.md`  
**Revision:** Rev 03 (incorporating receipt reconciliation, handoff addendum, target-edge contract, and wording corrections from `[X-199]`, `[X-200]`, `[X-201]`, and `Docs/BossCombatReview/Execution/Codex/AG10_A131_REVIEW.md`)  
**Author:** Antigravity (Assistant)  
**Assigned By:** Codex Technical Lead (`[X-196]`, `[X-198]`, `[X-200]`, `[X-201]`)  
**Work Order:** AG10 (Independent First-Cluster Capability & Witness Review)  
**Date:** 2026-10-27  
**Execution Environment:** Windows / Pure Offline Source Audit (No Engine, No PIE, No Source/ Edits)

---

## 1. Pinned Source Hash Registry

All evaluations, line citations, and witness specifications in this audit are strictly pinned against the following frozen files:

### Codex Step2Preparation Inputs:
| Document / Script | Repository Path | Current SHA256 Hash | Notes / History |
| :--- | :--- | :--- | :--- |
| **09 Parity Crosswalk** | `Docs/BossCombatReview/Execution/Codex/Step2Preparation/09_FIRST_CLUSTER_TYPED_PARITY_CROSSWALK.md` | `13b747fdcfba9951af5a0062e46499cd037d821aed94ac9e7e60eb1dcc03fd13` | Updated snapshot with Codex `[X-199]` handoff addendum (historical pre-addendum pin was `138d2946...`) |
| **14 Phase Reversal Contract** | `Docs/BossCombatReview/Execution/Codex/Step2Preparation/14_PHASE_REVERSAL_PARITY_CONTRACT.md` | `4d67c93f69b8a1578cc76b2380ca599ff3256cae1d0638e8620676d47595e5a5` | Updated snapshot with Codex `[X-199]` handoff addendum (historical pre-addendum pin was `cb87cdf3...`) |
| **15 Health Application Contract** | `Docs/BossCombatReview/Execution/Codex/Step2Preparation/15_HEALTH_APPLICATION_PARITY_CONTRACT.md` | `aa11c4cf97c9b22d98fcdb128680c07777399d54ef061c876fa6c0f3b01f304b` | Frozen input pin |
| **16 Topology Contract** | `Docs/BossCombatReview/Execution/Codex/Step2Preparation/16_BINDING_DIAGNOSTIC_TOPOLOGY_CONTRACT.md` | `8109ada9c596176beb34961389f8ae949e342f4d052a43f39e3c5b214553234d` | Updated snapshot with Codex `[X-201]` target-edge addendum (historical pre-addendum pin was `0f15fc15...`) |
| **Topology Checks Script** | `Docs/BossCombatReview/Execution/Codex/Step2Preparation/binding_topology_contract_checks.py` | `64588923c44a9c666fdee58d59a16c2e3905a28f82b17101c1fd53e2cf7328e4` | Frozen input pin (4/4 PASS, 12 adversarial subcases) |

### C++ Source Files Audited (Independently Verified from Disk Reads):
| Source / Header File | Repository Path | Exact Raw SHA256 Hash |
| :--- | :--- | :--- |
| **RPGBossEncounter.cpp** | `Source/OneBossFight/Player/RPGBossEncounter.cpp` | `dc149393f2fff1788ea22daf42db0b14f85ac36f58ad59c459b44ee94600c96d` |
| **RPGBossEncounter.h** | `Source/OneBossFight/Player/RPGBossEncounter.h` | `4f3ab203562ef2d3a2d18828feaf5f437a5a7eaff1054e9b6ce60e9150cae9d6` |
| **RPGBossPhases.cpp** | `Source/OneBossFight/Player/RPGBossPhases.cpp` | `c43615412e1f345d6ed75cc6d6a6b0d9ece6acaaac612e545b42cc24087f7a06` |
| **RPGBossPhases.h** | `Source/OneBossFight/Player/RPGBossPhases.h` | `0887f37564a28564261b81ad21a1baf2a4c6f6adae99a3a49c3c15622225a69a` |
| **RPGBossPosture.cpp** | `Source/OneBossFight/Player/RPGBossPosture.cpp` | `b26e184b0410e858d1c504e0b374dbc9e8f4c6b6399b05617559bb6909e88e41` |
| **RPGBossPosture.h** | `Source/OneBossFight/Player/RPGBossPosture.h` | `bca70f5816a45733f0ea2d5550651da7192ba179a5e31d736eab90fd46cd3ff8` |
| **RPGBossStagger.cpp** | `Source/OneBossFight/Player/RPGBossStagger.cpp` | `c711d766b4fecb6999c638cf5d8720ca422ba758223f941ea437ebac5b474c98` |
| **RPGBossStagger.h** | `Source/OneBossFight/Player/RPGBossStagger.h` | `7cfaaadbc33934d1dfe66560c0ff8c7fb47ac9e05399a5445b8c1e9a18c3695b` |
| **RPGBossMath.h** | `Source/OneBossFight/Player/RPGBossMath.h` | `89ff1aa3c367da2fe84de1583da889dd623bddd11787c416d43792f15cc2ebf0` |
| **RPGBossRules.h** | `Source/OneBossFight/Player/RPGBossRules.h` | `e16744219deffffab4de69ddd62e5333c1b59ac43cc670c9e777aee3fd397395` |
| **RPGEncounterBinding.cpp**| `Source/OneBossFight/Player/RPGEncounterBinding.cpp` | `2fe63bcb78261b9bdd15be33607ea3c696ae33227989facc5b67e15cd91110dc` |
| **RPGEncounterBinding.h** | `Source/OneBossFight/Player/RPGEncounterBinding.h` | `4330f8c416cd75284e829856b5d1cba7001c5ee62f40bdc7b1bf98a8dbf94a80` |
| **RPGBlueprintCall.h** | `Source/OneBossFight/Pack/RPGBlueprintCall.h` | `08ca6403cb85eef36ed15c755a2163fb17f8bcfdb81043b640765d5145b8e19c` |

*Receipt Note:* Previous citations in `[A-131]` referencing five hypothetical preparation files are withdrawn; those files do not exist under `Docs/BossCombatReview/Execution` and are not required AG10 outputs.

---

## 2. First-Cluster Capability & Assumption Audit

Every claim from Codex `09`, `14`, `15`, and `16` has been cross-examined against actual C++ source declarations and logic. Findings are categorized into:
- **Legacy Behavior to Preserve**: Existing native behavior in `Source/OneBossFight/Player` that migration must reproduce rather than alter.
- **Unsupported Adapter Domain (Design Options Under Review)**: General inputs accepted by scaffold schemas that native logic cannot support without explicit capability handling or rejection.
- **Contract Boundary / Witness Requirement**: Independent verification standard needed to prove parity.

---

### Area A: Health Application & Asynchronous Hydration (`09`, `15`)

#### Claim A.1: `bHydrated` reflects component registration, not effective pack health.
- **Source Finding:** **CONFIRMED.** In [`RPGEncounterBinding.cpp:333-340`](file:///c:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGEncounterBinding.cpp#L333-L340), `bHydrated` is assigned strictly from `Ready = Participant->IsRegistered() && Components->IsRegistered()`. `URPGCombatParticipant::IsReady` checks only `bHydrated && !bPoisoned`. Neither path verifies whether the pack's `BP_AttributesComponent_C` has finished asynchronous startup or whether attributes have reached their intended values.
- **Classification:** **Unsupported Adapter Domain (False Conflation).** Structural readiness must not be reported as effective gameplay hydration.
- **Witness Required:** Observe pack attribute readings before/after registration and wait for actual positive attribute readback.

#### Claim A.2: `BossMaxHealth > 1.f` override threshold vs typed compiler `MaxHealth > 0.f`.
- **Source Finding:** **CONFIRMED (QUALIFIED).** In [`RPGBossEncounter.cpp:90`](file:///c:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGBossEncounter.cpp#L90), the override application branch requires `BossMaxHealth > 1.f` AND positive readbacks (`Max > 0.0 && Current > 0.0`). In [`RPGEncounterBinding.cpp:38`](file:///c:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGEncounterBinding.cpp#L38), `CompileParticipantImpl` accepts any finite `Stats.MaxHealth > 0.f`. Any value in `(0.0, 1.0]` compiles successfully under the scaffold, but silently bypasses the native health override at runtime, leaving the currently effective pack values (historical default 500, but whatever the pack effectively reads). If maximum read is already within 0.5 of target, it sets `bMaxHealthApplied = true` without writing.
- **Classification:** **Unsupported Adapter Domain (Design Options Under Review).** Handling for values in `(0.0, 1.0]` (whether via input guarding or documenting legacy bypass) remains a proposed design option pending decision.
- **Witness Required:** Probe `MaxHealth` values across boundaries: `0.0` (compiler reject), `0.5` (native bypass witness), `1.0` (native bypass witness), `1.001` (native override branch entered), `2000.0` (standard).

#### Claim A.3: Setter dispatch success vs caller attribute readback.
- **Source Finding:** **CONFIRMED (QUALIFIED).** `WriteAttribute` and `WriteMaxAttribute` in [`RPGBlueprintCall.h:222-268`](file:///c:/UnrealProject/OneBossFight/Source/OneBossFight/Pack/RPGBlueprintCall.h#L222-L268) return `bool` indicating whether `CallBlueprintFunction` dispatched successfully into the reflection layer. Neither helper performs an attribute readback itself. However, the *caller* in [`RPGBossEncounter.cpp:101`](file:///c:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGBossEncounter.cpp#L101) explicitly verifies maximum readback:
  ```cpp
  WriteMaxAttribute(GetOwner(), HealthTag, BossMaxHealth) && ReadAttribute(GetOwner(), HealthTag, true, NewMax) && FMath::Abs(NewMax - BossMaxHealth) <= 0.5
  ```
  Once verified within `0.5`, it sets `bMaxHealthApplied = true` and writes proportional current health (`:105`), but performs no readback check on that final current write.
- **Classification:** **Legacy Implementation Fact / Contract Boundary.** `bMaxHealthApplied == true` proves maximum readback at write time, but does not prove current health readback, nor does it guarantee maximum is not overwritten later.
- **Witness Required:** Explicit independent readback of current health via `ReadAttribute(Owner, HealthTag, false, Current)` following the write.

#### Claim A.4: Startup dormancy restoration lifetime (`StartupEnforceSeconds = 4.f`) and `GateRadius = 0` synthetic fixtures.
- **Source Finding:** **CONFIRMED (QUALIFIED).** In [`RPGBossEncounter.cpp:80-88`](file:///c:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGBossEncounter.cpp#L80-L88), startup restoration only executes if `bMaxHealthApplied && bDormant && StartupTime < 4.f`. In [`RPGBossEncounter.cpp:70-73`](file:///c:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGBossEncounter.cpp#L70-L73), `Sleep()` is called on `BeginPlay` only if `GateRadius > 0.f`. Synthetic test fixtures setting `GateRadius = 0.f` omit this initial call to `Sleep()`. Although dormancy remains a mutable property, `GateRadius = 0.f` fixtures omit the ordinary initial dormancy that Boss01 experiences, thus bypassing the startup restoration branch on spawn.
- **Classification:** **Legacy Behavior to Preserve / Synthetic Fixture Limitation.** Gated boss behavior and non-gated synthetic behavior are distinct execution paths.
- **Witness Required:** Execute separate witnesses for gated (`GateRadius = 1200.f`) and non-gated (`GateRadius = 0.f`) startup sequences.

#### Claim A.5: Reset restores current health from readable pack MAXIMUM, not configured `BossMaxHealth`.
- **Source Finding:** **CONFIRMED.** In [`RPGBossEncounter.cpp:371-375`](file:///c:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGBossEncounter.cpp#L371-L375), `ResetEncounter` executes:
  ```cpp
  double Max = 0.0;
  if (ReadAttribute(Owner, HealthTag, true, Max))
  {
      WriteAttribute(Owner, HealthTag, Max);
  }
  ```
  It does not re-invoke `WriteMaxAttribute(Owner, HealthTag, BossMaxHealth)`, nor does it reset `bMaxHealthApplied` or `StartupTime` (`StartupTime` continues accumulating).
- **Classification:** **Legacy Behavior to Preserve.** If pack maximum health was externally modified during combat, reset refills health to that modified maximum, not to initial 2000.
- **Witness Required:** Observe pack maximum before reset, current health after reset, and verify that `StartupTime` is not reset to 0.

---

### Area B: Phase Effects Reversibility & Array Membership (`09`, `14`)

#### Claim B.1: `BaseWalkSpeed` is sampled at `BeginPlay` but never used for removal/reset.
- **Source Finding:** **CONFIRMED.** In [`RPGBossPhases.cpp:70`](file:///c:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGBossPhases.cpp#L70), `BaseWalkSpeed` is sampled in `BeginPlay`. Full-text search across `RPGBossPhases.cpp` reveals zero other references to `BaseWalkSpeed`. In [`RPGBossPhases.cpp:384`](file:///c:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGBossPhases.cpp#L384), `RemovePhaseTwoBuffs` performs arithmetic division:
  ```cpp
  Movement->MaxWalkSpeed = Movement->MaxWalkSpeed / MovementScale;
  ```
  It divides the *current* speed by `MovementScale`. If external systems wrote to `MaxWalkSpeed` during Phase 2, removal divides that external speed, rather than restoring `BaseWalkSpeed`.
- **Classification:** **Legacy Behavior to Preserve.** Removal is inverse arithmetic under assumed invariants, not a cache restoration.
- **Witness Required:** Capture speed before Phase 2, after Phase 2 apply, and after reset/removal; test with and without intervening pack speed writes.

#### Claim B.2: Asymmetric damage removal for `DamageScale < 1.0` (subunit damage).
- **Source Finding:** **CONFIRMED (CONDITIONAL DEDUCTION).** In [`RPGBossPhases.cpp:368`](file:///c:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGBossPhases.cpp#L368):
  `AppliedAttack = Attack * (DamageScale - 1.0);`
  If `DamageScale = 0.5`, `AppliedAttack = 100 * (0.5 - 1.0) = -50.0`.
  In [`RPGBossPhases.cpp:390`](file:///c:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGBossPhases.cpp#L390):
  ```cpp
  if (AppliedAttack > 0.0 && ReadAttribute(GetOwner(), AttackTag, false, Attack))
  {
      WriteAttribute(GetOwner(), AttackTag, FMath::Max(0.0, Attack - AppliedAttack));
  }
  AppliedAttack = 0.0;
  ```
  Because `AppliedAttack = -50.0`, the guard `AppliedAttack > 0.0` fails. The reduction is never restored, and `AppliedAttack` is zeroed. Attack remains degraded at 50 in code arithmetic. This is a source deduction; Boss01 default is 1.25, so this domain is unexercised in production.
- **Classification:** **Unsupported Adapter Domain (Design Options Under Review).** Scaffold schema currently accepts any positive `DamageScale > 0.f`, whereas native code reversal arithmetic only restores properly when `DamageScale >= 1.0`. Supported-domain design options (such as adapter-level input guarding for `DamageScale >= 1.0` or implementing signed delta restoration) remain proposals pending architectural decision.
- **Witness Required:** Observe and classify capability gaps under `DamageScale < 1.0` during phase reversal without presupposing a chosen gate implementation.

#### Claim B.3: Dynamic membership in `ScaleAttackRates` operates over current `CreatedAbilities`.
- **Source Finding:** **CONFIRMED (CONDITIONAL DEDUCTION).** In [`RPGBossPhases.cpp:407-446`](file:///c:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGBossPhases.cpp#L407-L446), `ScaleAttackRates(Factor)` reflects over `CreatedAbilities` at execution time. On Phase 2 start, it multiplies by `AttackRateScale`; on removal, it multiplies by `1.f / AttackRateScale`. If an ability was granted during Phase 2, removal divides its rate even though it was never scaled up. If an ability was destroyed, inverse traversal cannot restore that destroyed object.
- **Classification:** **Unsupported Adapter Domain / Runtime Assumption.** Reversibility relies on the assumption of static ability set membership across the phase lifecycle.
- **Witness Required:** Pin per-ability instance identities and play rate properties across the full phase transition and reset cycle under stated static-membership assumptions.

#### Claim B.4: `Scaled` log count is an iteration counter; `Montage_GetPlayRate` is a queried scalar.
- **Source Finding:** **CONFIRMED.** In [`RPGBossPhases.cpp:445`](file:///c:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGBossPhases.cpp#L445), `++Scaled;` increments inside the inner property loop for each `PlayRate` property found in struct arrays. It counts struct fields visited, not unique montages or confirmed effective playback rates. Furthermore, `Montage_GetPlayRate` is a queried scalar property from the active montage instance, not proof of complete effective simulation rate under time dilation, blend-outs, or external play rate modifiers.
- **Classification:** **Contract Boundary.** Log count and queried play rate alone do not constitute simulation rate proof.
- **Witness Required:** Compare queried `Montage_GetPlayRate` against independently observed timeline progression deltas.

---

### Area C: Posture Pool & Seeding (`09`, `14`)

#### Claim C.1: Posture initialization, sentinel `LastDrainTime = -1.0`, and delay enforcement.
- **Source Finding:** **CONFIRMED (CORRECTED).** In [`RPGBossPosture.cpp:39, 140-145, 148-156`](file:///c:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGBossPosture.cpp#L39):
  - `BeginPlay`: `Posture = PostureMax;`
  - `ResetPool`: `Hold = EHold::None; HeldValue = 0.f; Posture = PostureMax; LastDrainTime = -1.0;`
  - `RefillAfterBreak`: `Posture = PostureMax; LastDrainTime = WorldTime;`
  In [`RPGBossMath.h:17-25`](file:///c:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGBossMath.h#L17-L25):
  ```cpp
  inline float RegenStep(float Posture, float Max, double WorldTime, double LastDrainTime, float Delay, float PerSecond, float Dt, bool bFromZero = false)
  {
      if ((Posture <= 0.f && !bFromZero) || Posture >= Max)
      {
          return Posture;
      }
      if (LastDrainTime >= 0.0 && WorldTime - LastDrainTime < Delay)
      {
          return Posture;
      }
      return FMath::Min(Max, Posture + PerSecond * Dt);
  }
  ```
  *Correction:* Full pools (`Posture >= Max`) return immediately; no visible regeneration occurs at full pool. When a normal hit drains posture, `Drain()` in [`RPGBossPosture.cpp:105`](file:///c:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGBossPosture.cpp#L105) immediately updates:
  ```cpp
  LastDrainTime = GetWorld() ? GetWorld()->GetTimeSeconds() : 0.0;
  ```
  This sets `LastDrainTime >= 0.0` before the next `TickComponent`, so `RegenStep` enforces `WorldTime - LastDrainTime < Delay` (6 seconds) from that drain. `LastDrainTime = -1.0` is a sentinel indicating *no drain has yet occurred in this reset cycle*. It does NOT cause immediate regeneration upon a subsequent normal drain.
- **Classification:** **Legacy Behavior to Preserve.** `LastDrainTime` is private runtime state and must not be serialized into immutable configs.
- **Witness Required:** Observe `LastDrainTime = -1.0` sentinel initialization separately from damaged-pool timing following an actual drain.

#### Claim C.2: Component tick cadence (`TickInterval = 0.05f`).
- **Source Finding:** **CONFIRMED (QUALIFIED).** In [`RPGBossPosture.cpp:33`](file:///c:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGBossPosture.cpp#L33), `PrimaryComponentTick.TickInterval = 0.05f`. This is the *configured target component tick cadence* (20 Hz), not an absolute guarantee of exact 50ms executions under varying frame rates, pauses, or tick scheduling. `RPGBossMath::RegenStep` consumes supplied `DeltaTime`.
- **Classification:** **Legacy Implementation Fact.** Posture regeneration targets a 50ms tick cadence.
- **Witness Required:** Sample posture pool and record tick timestamps and delta times alongside calculated regeneration progression, without asserting an exact 50ms/10ms threshold.

---

### Area D: Stagger Prerequisites, Handoff & Ordering (`09`, `14`)

#### Claim D.1: Stagger component is an explicit prerequisite for the proposed first-cluster capability, while preserving legacy optional branching.
- **Source Finding:** **CONFIRMED (QUALIFIED).**
  1. In [`RPGBossPhases.cpp:74-77`](file:///c:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGBossPhases.cpp#L74-L77), `RPGBossPhases::BeginPlay` executes:
     ```cpp
     if (const URPGBossStagger* Stagger = GetOwner()->FindComponentByClass<URPGBossStagger>())
     {
         AddTickPrerequisiteComponent(const_cast<URPGBossStagger*>(Stagger));
     }
     ```
     This dynamically adds a tick prerequisite if `URPGBossStagger` is present. It does not fail or crash if absent, preserving optional legacy branch semantics. However, for full first-cluster parity where posture break and phase transitions interact, this prerequisite ensures stance break logic ticks before phase transition logic.
  2. In [`RPGBossEncounter.cpp:319-322`](file:///c:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGBossEncounter.cpp#L319-L322), `ResetEncounter` uses a conditional lookup:
     ```cpp
     if (URPGBossStagger* Stagger = Owner->FindComponentByClass<URPGBossStagger>())
     {
         Stagger->AbortStagger();
     }
     if (URPGBossPhases* Phases = Owner->FindComponentByClass<URPGBossPhases>())
     {
         Phases->ResetPhases();
     }
     ```
  3. In [`RPGEncounterBinding.h:17-35`](file:///c:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGEncounterBinding.h#L17-L35), `FRPGParticipantConfig` defines only `Stats` and `Phases`. There are NO typed fields for Stagger or Riposte (`StaggerSeconds`, `FreezeAtPosition`, `CriticalMultiplier`, `RiposteRange`, `RiposteConeDegrees`, `RiposteArmSeconds`).
- **Classification:** **Architecture Dependency / Proposed Cluster Capability Boundary.** Stagger is a runtime prerequisite for the proposed complete first-cluster capability, though native code maintains optional component lookup branching. Configuration is currently outside the typed participant schema.
- **Witness Required:** Verify tick ordering (`Stagger` ticks before `Phases` when both present) and verify `AbortStagger` is called prior to `ResetPhases` on encounter reset.

#### Claim D.2: Stagger-to-Phase Handoff and Reset Lifecycle Details (`[X-199]` Addendum).
- **Source Finding:** **CONFIRMED.** Per detailed source analysis of [`RPGBossStagger.cpp:432-485`](file:///c:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGBossStagger.cpp#L432-L485) and [`RPGBossPosture.cpp:148-178`](file:///c:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGBossPosture.cpp#L148-L178):
  1. `RPGBossStagger.cpp:432-485` marks Phase Idle, sets cooldown, removes immunity, and calls `Posture.RefillAfterBreak` at line 465 **before** attempting queued phase transition at line 479.
  2. If transition starts, it clears its own `bBehaviourHeld` at line 481 without calling `ResumeBehaviour`; otherwise it resumes. This bool handoff is behavior ownership, distinct from posture's hold enum.
  3. `Posture.RefillAfterBreak:148-156` ends an existing hold with refill, or sets full pool and current `LastDrainTime` when no hold. `Phases.StartTransition:254-281` begins Pinned posture hold (when enabled) and inherits or acquires behavior hold. The default queued path is therefore NOT a direct Zero-to-Pinned hold preserving zero; it refills, then pins that refilled current pool.
  4. `Posture.BeginHold:168-178` ignores requests if any hold is already present (it is not a nested or reference-counted API).
  5. Reset path: `Encounter:325` is preceded by `Stagger.AbortStagger:321`. `AbortStagger:825-840` calls `EndStagger(false, true)` if active (no queued phase/resume), clears its behavior flag, then `EndHold(true)`. Phase reset later removes buffs/immunity and ends hold; Encounter eventually calls `ResetPool:382`, whose final `LastDrainTime = -1.0` supersedes intermediate `EndHold` timestamps.
  6. Break-before-phase behavior depends on pending intake deferral and end-of-stagger handoff, not tick prerequisite alone.
- **Classification:** **Proposed Cluster Handoff Contract / Legacy Behavior to Preserve.** Handoff and reset sequences must preserve exact component ordering and sentinel precedence.
- **Witness Required:** Formulate witness `WIT-STAG-01` to capture refill-before-phase, behavior bool handoff, hold transition, and reset abort sequences.

---

### Area E: Binding Diagnostic Topology & Target Edge Contract (`16`)

#### Claim E.1: Prior 4-unique-key / 1-encounter check yielded false confidence; topology requires 1 world, 2 encounters, 2 Boss/Player pairs sharing positive `uint32` generations.
- **Source Finding:** **CONFIRMED.** Verified by running `binding_topology_contract_checks.py:54-89` (4 unit tests, 12 adversarial subcases PASS). The test `test_original_unique_count_false_pass` proves that 4 unique keys sharing 1 encounter and invalid slots passed the old counter check but are rejected by `validate_topology`.
- **Classification:** **Offline Diagnostic Contract Improvement.**
- **Witness Required:** Enforce `validate_topology` in future driver repairs.

#### Claim E.2: Diagnostic structure vs native actor association.
- **Source Finding:** **CONFIRMED.** In `binding_topology_contract_checks.py:10`, `actor` is an arbitrary string path (e.g. `"/Fixture/Actor0"`). The helper validates string structure and key relationships; it does not verify Unreal actor pointers, class instances, or live component attachments.
- **Classification:** **Contract Boundary.** Diagnostic topology validation is necessary but not sufficient for gameplay binding proof.
- **Witness Required:** In-editor verification matching candidate actor pointers to registered `URPGCombatParticipant` component owners.

#### Claim E.3: Rejection witness requires exposed catalog/coordinator diagnostics, not nonexistent `get_rejection_count()`.
- **Source Finding:** **CONFIRMED.** In [`RPGEncounterBinding.h:84-90`](file:///c:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGEncounterBinding.h#L84-L90), `FRPGHydrationResult` records errors via `Fail(Message)`. Neither `RPGEncounterBinding.h` nor `RPGCombatCatalog.h` exposes a `get_rejection_count()` method. Furthermore, `FRPGHydrationResult::Errors` is internal C++ struct state, not currently exported as a readable Python hook in the staged driver or coordinator.
- **Classification:** **Specification Correction / Reachability Boundary.** Native test results and runtime coordinator export must be distinguished.
- **Witness Required:** In C++ tests, assert `Result.IsReady() == false` and non-empty `Result.Errors`. In Python/editor tests, await exposed coordinator diagnostic reporting.

#### Claim E.4: Target-edge and whole-encounter publication boundaries (`[X-201]` Addendum).
- **Source Finding:** **CONFIRMED.** In [`RPGEncounterBinding.cpp:185-236`](file:///c:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGEncounterBinding.cpp#L185-L236):
  1. `BindEncounter` (`:185`) stores `TargetSlot` and (`:189`) checks only that the target slot exists in the encounter slots. It does not verify reciprocal edges (e.g. Boss targeting Player and Player targeting Boss) or guard against self-targeting intent.
  2. `ResolveTarget` (`:214-223`) requires both source and destination records to be hydrated in the same world-session/encounter, but performs no attack authorization check.
  3. `ResolveEncounter` (`:226-236`) returns the requester's own encounter component once its own record is hydrated. This is inert per-record scaffold behavior, distinct from whole-encounter publication barriers where lookups are held until all participants are ready.
- **Classification:** **Coverage Limit / Future Witness Scope.** Structural topology alone does not prove target-edge correctness or whole-encounter readiness. Boss/Player reciprocity is specific to two-duel fixture expectations, not a universal global schema policy.
- **Witness Required:** Define explicit target-edge validation in fixture metadata (source/target actor+slot pairs, self-edge rejection, partial partner hydration).

---

## 3. Replacement-Operator Unrun Witness Matrix

The following matrix organizes all required independent observations into concrete witness procedures, mapped directly to migration packets and project gate boundaries. **All cases are currently UNRUN** (awaiting resumed operator execution in Unreal Editor / PIE):

| Witness ID | Target Mechanism | Specific Independent Observations Required | Associated Packet | Governing Gate Boundary |
| :--- | :--- | :--- | :---: | :---: |
| **WIT-HLTH-01** | Normal Gated Health Application | Capture `BossMaxHealth` write from Tick; verify `NewMax` readback within 0.5; verify subsequent `Current` readback; record dormancy and wake timing. | Packet D0 | DD-1 Step 2 / Gate 2 |
| **WIT-HLTH-02** | Target Max Pre-Existing | Set pack max to 2000 prior to encounter tick; verify `bMaxHealthApplied` is set without proportional current write; record current health preservation. | Packet D0 | DD-1 Step 2 / Gate 2 |
| **WIT-HLTH-03** | Health Bypass Domain `(0, 1]` | Pass `Stats.MaxHealth = 0.5` and `1.0`; observe native encounter tick bypasses override, leaving effective pack values; observe and classify capability gap across domain `(0.0, 1.0]`. | Packet D0 | DD-1 Step 2 / Gate 2 |
| **WIT-HLTH-04** | Startup Dormancy Enforcement | Compare `GateRadius = 1200` (initial dormancy active; restoration runs for 4s) vs `GateRadius = 0` (initial dormancy omitted; no startup restoration). | Packet D0 | DD-1 Step 2 / Gate 2 |
| **WIT-HLTH-05** | Repeated Reset Health Restoration | Observe pack max before reset and current health after reset; confirm current is restored from *current* pack max, not configured 2000; verify `StartupTime` is not reset. | Packet D0 | DD-1 Step 2 / Gate 2 |
| **WIT-PHSE-01** | Full Phase Transition & Reversal | Under assumptions of stable ability membership and no external speed writes: record movement speed, `AppliedAttack`, and per-ability play rates before apply, after apply, before reset, and after reset; confirm restoration. | Packet D0 | DD-1 Step 2 / Gate 2 |
| **WIT-PHSE-02** | Intervening Pack Speed Write | Inject an external speed write during Phase 2; observe that removal divides current speed rather than restoring `BaseWalkSpeed`. | Packet D0 | DD-1 Step 2 / Gate 2 |
| **WIT-PHSE-03** | Subunit Damage Factor (`< 1.0`) | Pass `DamageScale = 0.5`; observe `AppliedAttack = -50.0`; verify removal fails to restore attack (`AppliedAttack > 0` guard); observe and classify capability gap under subunit damage scaling without presupposing an approved gate. | Packet D0 | DD-1 Step 2 / Gate 2 |
| **WIT-PHSE-04** | Dynamic Ability Set Mutation | Add a synthetic ability during Phase 2; observe that removal divides its rate; remove an ability during Phase 2; observe unmatched membership. | Packet D0 | DD-1 Step 2 / Gate 2 |
| **WIT-POST-01** | Posture Sentinel vs Damaged Timing | Observe `LastDrainTime = -1.0` sentinel on reset at full pool (no visible regen); apply damage via `Drain()` and verify `LastDrainTime` is set to drain timestamp, enforcing `DelaySeconds = 6s` before regen. | Packet D0 | DD-1 Step 2 / Gate 2 |
| **WIT-POST-02** | Configured Posture Cadence | Sample posture pool during regeneration; record tick timestamps and deltas alongside calculated progression; compare against configured `TickInterval = 0.05f`. | Packet D0 | DD-1 Step 2 / Gate 2 |
| **WIT-STAG-01** | Stagger Handoff & Abort Sequence | Verify optional component check and tick prerequisite (`URPGBossStagger` ticks before `URPGBossPhases`); verify `RefillAfterBreak` executes before queued `StartTransition`; verify behavior bool handoff without `ResumeBehaviour`; verify `AbortStagger()` executes before `ResetPhases()` and final `ResetPool` sets `LastDrainTime = -1.0`, superseding intermediate `EndHold` timestamps. | Packet D0 | DD-1 Step 2 / Gate 2 |
| **WIT-TOPO-01** | 4-Actor 2-Encounter Topology & Target Edges | Execute `validate_topology` across 2 encounters and 4 participants; verify rejection of single-encounter, foreign world, and slot reuse mutations; verify fixture specifies source/target actor+slot edges and rejects self-edges. | Packet F | DD-1 Step 2 / Gate 2 |
| **WIT-TOPO-02** | Candidate Actor to Key & Edge Resolution | Match candidate actor pointers to registered `URPGCombatParticipant` keys; verify identity persistence and resolved target edges across duel cycles. | Packet F | DD-1 Step 2 / Gate 2 |
| **WIT-TOPO-03** | Invalid Mode Rejection Witness | Provide invalid catalog config; in native C++ verify `FRPGHydrationResult::IsReady() == false` and `Errors` populated; in Python await exposed coordinator diagnostic reporting. | Packet G | DD-1 Step 2 / Gate 2 |
| **WIT-CVAR-01** | Catalog CVar Isolation & Restoration | Snapshot `CatalogSource`, `CatalogTestInvalid`, `CatalogTestFourth`, `CatalogPath` before test; verify clean restoration after GI teardown. | Packet G | Gate 0 / Gate 4 |

---

## 4. Synthesis & Architectural Boundaries for Step 2

Based on this audit, the following boundaries are established for the replacement operator and future adapter implementation:

1. **Extraction Parity Must Preserve Native Idiosyncrasies:**
   - Native code divides current speed by `MovementScale` on removal; it does not restore `BaseWalkSpeed`.
   - Native code refills health on reset from the currently readable pack maximum; it does not reapply `BossMaxHealth`.
   - Native code enforces startup health restoration only while dormant (`GateRadius > 0`) during the first 4 seconds.
   - Native code targets a 50ms tick cadence (`TickInterval = 0.05f`) for posture regeneration.
   - Native code executes `Stagger->AbortStagger()` before `Phases->ResetPhases()` on reset.
   *Adapters must not alter these behaviors under the guise of "cleanup" during Phase 1 extraction.*

2. **Scaffold Inputs & Proposed Capability Boundaries (Design Options Under Review):**
   - *Proposal under review:* Scaffold may reject `Stats.MaxHealth <= 1.0` before passing to native components, or document it as legacy bypass.
   - *Proposal under review:* Scaffold may reject `DamageScale < 1.0` until asymmetric restoration logic is separately designed and approved.
   - *Proposal under review:* Adapter must assume static ability set membership across Phase 2 unless dynamic tracking is explicitly designed.
   - *Grounding:* Participant generations are positive `uint32` (`1..4294967295`) per `FRPGParticipantKey`.

3. **Topology Verification Is Structural, Not Target-Edge or Runtime Parity:**
   - The 4-actor 2-encounter topology helper (`binding_topology_contract_checks.py`) guarantees key structure and slot consistency, but does not validate target edges or whole-encounter publication barriers. Runtime proof requires live actor pointer matching in PIE and explicit target-edge metadata.
