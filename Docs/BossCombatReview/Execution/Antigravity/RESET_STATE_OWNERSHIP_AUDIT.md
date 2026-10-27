# AG16: Reset Ownership of Captured Combat State Audit (Rev 03)

**Document Date:** 2026-10-27  
**Author:** Antigravity (Pair Programming AI Assistant)  
**Task Classification:** Work Order 16 (AG16) — Reset Ownership of Captured Combat State (Rev 03 Precision Fixes)  
**Governing Inputs:**
- Acceptance Directive: [`Docs/BossCombatReview/Execution/Codex/AG15_A142_ACCEPTANCE.md`](file:///c:/UnrealProject/OneBossFight/Docs/BossCombatReview/Execution/Codex/AG15_A142_ACCEPTANCE.md) (`SHA256: eda70805b54a0cf02f3eb8238f837ad9eefaf3e5aaf026fefb31365e9089218d`)
- Review & Corrections Directive: [`Docs/BossCombatReview/Execution/Codex/AG16_A143_REVIEW.md`](file:///c:/UnrealProject/OneBossFight/Docs/BossCombatReview/Execution/Codex/AG16_A143_REVIEW.md) (`SHA256: 21d04e135fe52959b7480eb2bd76c5b0e59f7f086265af65399848b595c390af`)
- Bounded Acceptance Directive: [`Docs/BossCombatReview/Execution/Codex/AG16_A144_ACCEPTANCE.md`](file:///c:/UnrealProject/OneBossFight/Docs/BossCombatReview/Execution/Codex/AG16_A144_ACCEPTANCE.md)
- Mailbox Directives: `[X-216]`, `[X-217]`, `[X-218]`, and `[X-219]` (2026-10-27 06:43:46 +05:30)

---

## 1. Executive Summary & Audit Scope

Per Codex directives `[X-216]`, `[X-217]`, `[X-219]`, and [`AG16_A144_ACCEPTANCE.md`](file:///c:/UnrealProject/OneBossFight/Docs/BossCombatReview/Execution/Codex/AG16_A144_ACCEPTANCE.md), this audit examines the reset ownership, capture timing, persistence, and destruction behavior of captured combat state across:
- [`URPGHitIntake`](file:///c:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGHitIntake.h) & [`FRPGDamageScaler`](file:///c:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGDamageScale.h) (boss hit intake, pending hit queues, damage scaling, health baselines)
- [`URPGSwingTracker`](file:///c:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGSwingTracker.h) (player swing tracking, captured rows, stamina extra, hyperarmor immunity)
- [`URPGBossEncounter`](file:///c:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGBossEncounter.h) (native encounter reset coordinator, player respawn tracking, boss state restore)
- [`URPGIFrameMonitor`](file:///c:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGIFrameMonitor.h) (player i-frame state resolved during encounter reset)

### Core Architectural Discoveries & Bounded Scope:
1. **Reset Coordinator Notification Scope:**
   The native encounter reset coordinator ([`URPGBossEncounter::ResetEncounter`](file:///c:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGBossEncounter.cpp#L297-L396)) directly resets components attached to the **boss actor** (`URPGBossStagger`, `URPGBossPhases`, `URPGBossPosture`, `URPGBossBleed`, `URPGBossDormantWake`, AIController/Blackboard/Perception, and pack attributes). In addition, it notifies the player-attached [`URPGIFrameMonitor`](file:///c:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGIFrameMonitor.cpp#L24-L27) via `URPGIFrameMonitor::Find(this)->OnEncounterReset()` (which resolves player pawn 0 via `UGameplayStatics::GetPlayerPawn`). However, `ResetEncounter()` contains **zero direct native C++ calls or reset notifications** to player-attached combat monitoring components ([`URPGHitIntake`](file:///c:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGHitIntake.h) or [`URPGSwingTracker`](file:///c:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGSwingTracker.h)). Note: Blueprint/ProcessEvent caller status is uninspected; no universal reset absence across all possible game layers is asserted.
2. **Indirect Reset Discovery via Health Heuristic in `URPGHitIntake::TrackBossHealth`:**
   Because `URPGBossEncounter` does not directly notify `URPGHitIntake`, the intake component discovers resets **indirectly** through a health jump heuristic in [`TrackBossHealth`](file:///c:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGHitIntake.cpp#L241-L245): `if (PrevBossHealth >= 0.0 && Health > PrevBossHealth + 0.5) { Scaler.Reset(); }`. Health sampling is governed by tick accumulation (`HealthSampleTimer += DeltaTime`), not guaranteed exact 10 Hz wall-clock intervals. If an encounter reset occurs while boss health does not register a >0.5 increase (e.g. boss was already at full health, or reading occurs before attribute write), this specific branch does not execute `Scaler.Reset()`.
3. **Conditional Cross-Reset Queue-to-Finalize Interleaving:**
   `URPGHitIntake::HandlePackHit` queues entries in `Pending` (`FPending` struct containing `FRPGHitRecord Record` and `TWeakObjectPtr<UObject> ActiveTarget`) and schedules `FinalizePending` via `GetTimerManager().SetTimerForNextTick`. `RPGBossEncounter::ResetEncounter()` does not clear `Pending` or cancel `bFinalizeScheduled`. If the scheduled next-tick delegate executes while target conditions allow, `FinalizePending` will process the batch against the live target. Post-reset damage or status application is strictly subject to incomplete conditional controls: target weak pointer validity, attack classification, montage merge deduplication, posture hold state, death/reset refusal, row resolution, and world/delegate lifetime across the tick boundary. A next-tick delegate is not a guaranteed next rendered frame.
4. **Captured Swing State & Dynamic Override Boundaries:**
   `URPGSwingTracker` captures swing data in `OnMontageStarted`, driven by `TickComponent` montage identity and backward position detection. It copies `FRPGWeaponAttackRow` values into `Current.Row`. Subsequent dynamic table modifications or `ClearCostOverrides()` do not rewrite captured `Current` fields. However, active hyperarmor remains conditional on ongoing montage identity/position updates (`UpdateHyperArmor`), and `Current` can be overwritten by subsequent detected montages or cleared by `ResetCounters()`. Calling `ResetCounters()` clears `Current` and `LastAttack` but does not clear `TrackedMontage`.
5. **Weak Pointer Validity vs Target Identity:**
   `URPGHitIntake::WatchedBoss` and `FRPGHitRecord::Target` use `TWeakObjectPtr<AActor>`. Per engine `WeakObjectPtr.h`, default `Get()` and `IsValid()` check object array serial numbers and validity flags (`bEvenIfGarbage=false`). Destroyed actors evaluate invalid once flagged. A still-live old boss actor retained in the level remains weak-valid, allowing stale target caching in `TrackBossHealth` until invalidated. When `WatchedBoss.Get()` evaluates null, `BossSearchTimer += DeltaTime` throttles searches against an accumulated 0.5s threshold (which may trigger in less than 0.5s depending on prior accumulation). Valid object pointer identity does not constitute encounter instance or generation association.

---

## 2. Inspected Input Receipts

The audit scope is strictly bounded to the native combat components, rule helpers, and reset implementations:

| File Path | SHA256 Hash | Bytes | Role in Combat Reset Dataflow |
|:---|:---|:---:|:---|
| [`Source/OneBossFight/Player/RPGHitIntake.h`](file:///c:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGHitIntake.h) | `9cc7604a0cda61f3c8e5e94c84526019eccb28ea0e04852307d027206340121c` | 9,431 | `FRPGHitRecord`, `FPending`, `Pending` queue, `WatchedBoss`, `Scaler` declarations |
| [`Source/OneBossFight/Player/RPGHitIntake.cpp`](file:///c:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGHitIntake.cpp) | `f2d0bd281924c4d29509214c1344234e1a8b2f476a77e51e00a045e73ae4a3db` | 20,867 | `HandlePackHit`, `FinalizePending`, `TrackBossHealth` (health sampling, scaler reset) |
| [`Source/OneBossFight/Player/RPGDamageScale.h`](file:///c:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGDamageScale.h) | `d8c8f882225d5a4ecfdddf9ff7d010f12e09314932daf2cad4c3c72e86fb36e6` | 2,947 | `FRPGDamageScaler` struct, `Losses`, `Hits`, `Window = 0.35s`, `Reset()`, `Prune()` |
| [`Source/OneBossFight/Player/RPGSwingTracker.h`](file:///c:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGSwingTracker.h) | `98efb272ddcdc6c7cc76840ead6e70e1030132071e9dd931e86c5118d5f0ae79` | 9,165 | `FRPGSwing Current`, `LastAttack`, `bHyperArmor`, `ResetCounters` declarations |
| [`Source/OneBossFight/Player/RPGSwingTracker.cpp`](file:///c:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGSwingTracker.cpp) | `ae1f6e0727cfd3c6ad7c9890ececd8880938247e504de179ace799e960088e51` | 12,848 | `OnMontageStarted`, `TickComponent`, `UpdateHyperArmor`, `ClearCostOverrides`, `EndPlay` |
| [`Source/OneBossFight/Player/RPGBossEncounter.h`](file:///c:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGBossEncounter.h) | `4f3ab203562ef2d3a2d18828feaf5f437a5a7eaff1054e9b6ce60e9150cae9d6` | 5,359 | Boss encounter manager, `ResetEncounter`, `int32 Generation = 1`, `TrackedPlayer` |
| [`Source/OneBossFight/Player/RPGBossEncounter.cpp`](file:///c:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGBossEncounter.cpp) | `dc149393f2fff1788ea22daf42db0b14f85ac36f58ad59c459b44ee94600c96d` | 12,526 | `ResetEncounter` implementation, boss component reset call chain |
| [`Source/OneBossFight/Player/RPGBossPhases.h`](file:///c:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGBossPhases.h) | `0887f37564a28564261b81ad21a1baf2a4c6f6adae99a3a49c3c15622225a69a` | 8,607 | Phase component declaration, `ResetPhases`, `RemovePhaseTwoBuffs` |
| [`Source/OneBossFight/Player/RPGBossPhases.cpp`](file:///c:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGBossPhases.cpp) | `c43615412e1f345d6ed75cc6d6a6b0d9ece6acaaac612e545b42cc24087f7a06` | 21,965 | `ResetPhases` implementation, inverse rate scaling, montage stop |
| [`Source/OneBossFight/Player/RPGBossPosture.h`](file:///c:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGBossPosture.h) | `bca70f5816a45733f0ea2d5550651da7192ba179a5e31d736eab90fd46cd3ff8` | 7,551 | Posture component declaration, `ResetPool` |
| [`Source/OneBossFight/Player/RPGBossPosture.cpp`](file:///c:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGBossPosture.cpp) | `b26e184b0410e858d1c504e0b374dbc9e8f4c6b6399b05617559bb6909e88e41` | 7,435 | `ResetPool` implementation (`Hold=None`, `HeldValue=0`, `Posture=PostureMax`, `LastDrainTime=-1`) |
| [`Source/OneBossFight/Player/RPGIFrameMonitor.h`](file:///c:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGIFrameMonitor.h) | `eeb7d15832488722971db5f8e2a6990b981c1fe5ea731d96fb4fc221af0c1c63` | 6,417 | Player i-frame monitor, `Find(WorldContext)`, `OnEncounterReset` |
| [`Source/OneBossFight/Player/RPGIFrameMonitor.cpp`](file:///c:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGIFrameMonitor.cpp) | `46c694c8841dbcfca3f85239e6a356d418a3ff08e3966edee431c7b669ce6c11` | 10,087 | `Find` implementation (resolves player pawn 0), `OnEncounterReset` |
| [`Docs/BossCombatReview/Execution/Codex/AG15_A142_ACCEPTANCE.md`](file:///c:/UnrealProject/OneBossFight/Docs/BossCombatReview/Execution/Codex/AG15_A142_ACCEPTANCE.md) | `eda70805b54a0cf02f3eb8238f837ad9eefaf3e5aaf026fefb31365e9089218d` | 5,725 | Codex AG15 acceptance & AG16 assignment terms |
| [`Docs/BossCombatReview/Execution/Antigravity/ADVERSARIAL_OBSERVER_ASSOCIATION_REVIEW.md`](file:///c:/UnrealProject/OneBossFight/Docs/BossCombatReview/Execution/Antigravity/ADVERSARIAL_OBSERVER_ASSOCIATION_REVIEW.md) | `e0f5689bf6938e0932d74bde7c1c1c14b811792f875908374290801098273afe` | 26,769 | AG15 report with precision citations updated |

---

## 3. State Inventory & Ownership Mapping

The table below catalogs captured combat fields across the audited components, mapping ownership, capture triggers, reset sites, destruction semantics, and encounter/generation awareness:

| Component / Struct | State Field / Object | State Classification | Owner & Lifetime | Capture / Ingestion Trigger | Reset / Clear Site & Trigger | Destruction Behavior (`EndPlay`) | Generation / Target Identity Checked? |
|:---|:---|:---|:---|:---|:---|:---|:---|
| `URPGHitIntake` | `TArray<FPending> Pending` | In-Flight Gameplay Queue | Member of `URPGHitIntake` (attached to player pawn). Contains `Record` and weak `ActiveTarget`. | Populated in `HandlePackHit` on collision `OnHit`. | Cleared in `FinalizePending` (`Batch = MoveTemp(Pending); Pending.Reset()`) or `ResetCounters()`. **Not cleared by `ResetEncounter()`.** | Discarded on actor destruction. No explicit timer clear in `EndPlay`. | **Target Checked, Generation Unchecked.** `FinalizePending` checks `Record.Target.Get()` and `Entry.ActiveTarget.Get()`, but does not associate with encounter generation. |
| `URPGHitIntake` | `bool bFinalizeScheduled` | Latched Async Flag | Member of `URPGHitIntake`. | Set to `true` in `HandlePackHit` when scheduling next-tick timer. | Set to `false` at entry of `FinalizePending`. **Not reset by `ResetEncounter()`.** | Flag discarded with component. Next-tick UObject delegate handle abandoned if intake is destroyed. | **NO.** Operates purely as a boolean throttle. |
| `URPGHitIntake` | `FRPGDamageScaler Scaler` | Temporal Scaling State | Member of `URPGHitIntake` (`Scaler.Hits`, `Scaler.Losses`). | `OnHit` called in `FinalizePending`; `OnLoss` called in `TrackBossHealth`. | Cleared in `Scaler.Reset()` when `Health > PrevBossHealth + 0.5` in `TrackBossHealth`, or via `ResetCounters()`. Pruned by `Window = 0.35s`. | Discarded on actor destruction. | **NO.** Stores timestamps and floats only; no target actor or generation tag. |
| `URPGHitIntake` | `TWeakObjectPtr<AActor> WatchedBoss` | Target Actor Cache | Member of `URPGHitIntake`. | Resolved in `TrackBossHealth` via `TActorIterator<ACharacter>` / `IsPackBoss`. | Re-queried in `TrackBossHealth` only if `!WatchedBoss.Get()`, throttled against an accumulated 0.5s `BossSearchTimer`. | Cleared on component destruction. | **Weak Object Checked, Identity Unchecked.** Checks `WatchedBoss.Get()` for UObject validity; does not detect replacement if old actor remains alive. |
| `URPGHitIntake` | `double PrevBossHealth` | Health Tracking Baseline | Member of `URPGHitIntake`. | Updated at end of `TrackBossHealth` upon valid attribute read. | Set to `-1.0` on constructor or new boss acquisition in `TrackBossHealth`. **Not cleared by `ResetCounters()`.** | Discarded on component destruction. | **NO.** Tracks raw double value without associating with encounter instance. |
| `URPGHitIntake` | `double HotUntil` | Sampling Rate Throttle | Member of `URPGHitIntake`. | Set to `Time + 0.35 + 0.1` in `HandlePackHit`. | Expires naturally when `World->GetTimeSeconds() > HotUntil`. **Not cleared by `ResetCounters()`.** | Discarded on component destruction. | **NO.** Pure time threshold. |
| `URPGSwingTracker` | `FRPGSwing Current` | Active Swing State | Member of `URPGSwingTracker` (attached to player pawn). | Captured in `OnMontageStarted` upon montage start/restart. | Cleared in `ResetCounters()`. Overwritten on next `OnMontageStarted`. **Not cleared when montage ends (`!Montage`).** | Discarded on component destruction. | **NO.** Does not track encounter generation. |
| `URPGSwingTracker` | `FRPGSwing LastAttack` | Historical Attack Cache | Member of `URPGSwingTracker`. | Captured from `Current` in `OnMontageStarted` if `Swing.IsAttack()`. | Cleared in `ResetCounters()`. | Discarded on component destruction. | **NO.** Retains last attack swing indefinitely. |
| `URPGSwingTracker` | `bool bHyperArmor` | Active Immunity Flag | Member of `URPGSwingTracker`. | Set via `SetHyperArmor(true)` in `UpdateHyperArmor`. | Set to `false` in `UpdateHyperArmor` (window exit/no montage) or explicitly in `EndPlay()`. **Not cleared immediately in `ResetCounters()`.** | Calls `SetHyperArmor(false)` in `EndPlay()` if `bHyperArmor` was true. | **NO.** Tracks animation position locally. |
| `URPGSwingTracker` | `TMap<ERPGAttackKind, FVector2D> HyperArmorOverrides` | Test Configuration | Member of `URPGSwingTracker`. | Injected via `SetHyperArmorOverrideForTest`. | Cleared in `ClearCostOverrides()`. | Discarded on component destruction. | **NO.** Test harness storage. |
| `URPGSwingTracker` | `TMap<ERPGAttackKind, float> CostOverrides` | Test Configuration | Member of `URPGSwingTracker`. | Injected via `SetCostOverrideForTest`. | Cleared in `ClearCostOverrides()`. | Discarded on component destruction. | **NO.** Test harness storage. |
| `URPGBossEncounter` | `int32 Generation = 1` | Local Lifecycle Token | Member of `URPGBossEncounter` (attached to boss actor). | Incremented in `ResetEncounter()` (`++Generation`). | Starts at `1`; increments monotonically per reset. | Discarded on boss actor destruction. | **Local token only.** Not published to `URPGCombatContextSubsystem` or player components. |
| `URPGBossEncounter` | `TWeakObjectPtr<const APawn> TrackedPlayer` | Player Tracking Cache | Member of `URPGBossEncounter`. | Set in `TickComponent` to `Player`. | **Not nulled in `ResetEncounter()`.** In `TickComponent`, checks `TrackedPlayer.IsValid() && TrackedPlayer.Get() != Player`. | Discarded on boss actor destruction. | **Weak Object Checked.** Requires previous valid player reference distinct from current to trigger `bResetOnPlayerRespawn`. |
| `URPGIFrameMonitor` | `TWeakObjectPtr<AActor> WatchedPlayer` | Player i-Frame Monitor | Attached to player pawn 0. | Initialized in `BeginPlay`. | `OnEncounterReset()` called by `URPGBossEncounter::ResetEncounter()`. | Discarded on actor destruction. | **Player Pawn Resolved.** Resolved via `URPGIFrameMonitor::Find(WorldContext)` (cpp:24-27). |

---

## 4. Native Reset Call Chain vs Indirect Discovery

### 4.1. The Native `ResetEncounter()` Call Chain
In [`Source/OneBossFight/Player/RPGBossEncounter.cpp:297-396`](file:///c:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGBossEncounter.cpp#L297-L396), `ResetEncounter()` executes:

```
URPGBossEncounter::ResetEncounter()
├── URPGBossDormantWake::StopFor(Owner)
├── ARPGBossRemains::DestroyForWorld(GetWorld())
├── URPGBossDeath check (if dying, refuse reset)
├── URPGTraceGuard::CloseFor(Owner, "reset")
├── Increment ResetCount, Increment Generation (++Generation; starts at 1)
├── URPGIFrameMonitor::Find(this)->OnEncounterReset()  <-- Resolves Player Pawn 0 (RPGIFrameMonitor.cpp:24-27)
├── URPGBossStagger::AbortStagger()
├── URPGBossPhases::ResetPhases()
│     └── RemovePhaseTwoBuffs() (inverts attack rates, restores move speed)
├── HoldBehaviour()
├── AAIController / Blackboard / Perception (clears TargetActor, bCombatEnabled=false, ForgetAll)
├── BP_CombatComponent_C reflection calls (ClearAllCombatTargets, SetCombatEnabled=false)
├── AnimInstance::Montage_Stop(0.1f)
├── CharacterMovement::StopMovementImmediately()
├── Teleport boss to HomeTransform
├── WriteAttribute(Owner, Attribute.Health, Max)   <-- Refills Boss Health to Max
├── WriteAttribute(Owner, Attribute.Poise, Max)    <-- Refills Boss Poise to Max
├── URPGBossPosture::ResetPool()                   <-- Hold=None, HeldValue=0, Posture=PostureMax, LastDrainTime=-1
├── URPGBossBleed::ResetBleed()
└── Sleep() or ResumeBehaviour()
```

### 4.2. Bounded Native Caller Scope & Absence of Direct Player Notification
- **Direct Native Call Search:** Inspection of the entire native C++ codebase confirms that `ResetEncounter()` contains **zero direct calls or notifications** to `URPGHitIntake`, `URPGSwingTracker`, or `URPGBuildLoadout`. (It does notify `URPGIFrameMonitor` on player pawn 0 via `URPGIFrameMonitor::Find(this)`).
- **Zero Direct Native Callers of `ResetCounters()`:** Searching all native C++ files confirms that `URPGHitIntake::ResetCounters()` and `URPGSwingTracker::ResetCounters()` have **zero direct callers in `Source/`**. They exist as public utility methods callable by reflection, test harnesses, or potential Blueprint scripts. (Direct inspection was bounded to native C++; Blueprint/ProcessEvent callers are unknown without asset bytecode analysis).
- **Hit Intake `ResetCounters()` Clearing Scope:** In [`RPGHitIntake.cpp:537-549`](file:///c:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGHitIntake.cpp#L537-L549), `ResetCounters()` resets `Pending`, `MergedHitCount`, `SwingKindOverrideCount`, `ScaledHitCount`, `HealthAdjustTotal`, `Scaler.Reset()`, `BossHitCount`, `OtherHitCount`, `LastRecord`, and `Lines`. It does **not** clear `PrevBossHealth`, `WatchedBoss`, `HotUntil`, `BossSearchTimer`, `HealthSampleTimer`, or `bFinalizeScheduled`. If a next-tick finalize delegate was already scheduled, the callback will still fire and process whatever queue then exists.
- **Living Reset vs Component Destruction:** When the player respawns or the boss resets while both player and boss actor instances remain alive, no `EndPlay()` or `BeginPlay()` is invoked on the player pawn's components. Internal component state remains intact unless modified by local execution paths.

### 4.3. The Indirect Health Refill Discovery Mechanism in `TrackBossHealth`
In [`RPGHitIntake.cpp:198-255`](file:///c:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGHitIntake.cpp#L198-L255):
- `TrackBossHealth` resolves `AActor* Boss = WatchedBoss.Get()`. If null, it advances `BossSearchTimer += DeltaTime`, throttling searches against an accumulated 0.5s threshold before iterating characters via `URPGPlayerMovesSubsystem::IsPackBoss(*It)`. Upon acquiring a boss, it initializes `PrevBossHealth = -1.0;`.
- Health sampling is governed by tick accumulation (`HealthSampleTimer += DeltaTime`), triggering at ~10 Hz when idle, or every frame while `World->GetTimeSeconds() <= HotUntil`.
- Resets are detected indirectly via:
  ```cpp
  if (PrevBossHealth >= 0.0 && Health > PrevBossHealth + 0.5)
  {
      // A gain is an encounter reset (the refill) or a heal: whatever the scaler still holds belongs to the old fight (a pending scaled hit would refund 61 percent of the first loss of the next one).
      Scaler.Reset();
  }
  ```
- **Conditional Reset Boundary:**
  1. The heuristic triggers strictly on observed positive health gains `> 0.5`.
  2. If an encounter resets when the boss is already at maximum health (e.g. player died before inflicting damage, or reset during dormant wake), `Health == PrevBossHealth`. This branch does not execute `Scaler.Reset()`. However, this does not mean `Scaler` arrays necessarily hold active entries; empty arrays remain empty.
  3. `Pending` entries and `bFinalizeScheduled` are **never cleared** by `TrackBossHealth`; the heuristic operates exclusively on `Scaler`.

---

## 5. Four Minimal Discriminating Unrun Cases

To evaluate the behavioral boundaries of captured combat state across encounter resets without executing intrusive runs, four minimal discriminating unrun cases are specified with explicit conditional gates:

### Case 1: Interleaving Between Hit Queue and Finalize (`HandlePackHit` -> `ResetEncounter` -> `FinalizePending`)
- **Hypothesized Interleaving:** Player strikes the boss in Frame N. `HandlePackHit` pushes an `FPending` entry (`Record` + weak `ActiveTarget`) into `Pending` and schedules `FinalizePending` via `SetTimerForNextTick`. In the same frame N, player death or external trigger invokes `RPGBossEncounter::ResetEncounter()`, restoring boss posture and health to full. In Frame N+1, the timer fires `FinalizePending()`.
- **Conditional Execution Path in Source:**
  1. `ResetEncounter()` does not clear `Pending` or cancel `bFinalizeScheduled`.
  2. On Frame N+1, `FinalizePending()` pops the batch via `MoveTemp(Pending)`.
  3. Deduplication check: if multiple entries share the same montage in the batch, entries after the first are skipped (`MergedHitCount++`).
  4. Target check: `FinalizePending` evaluates `if (AActor* ScaledBoss = Record.Target.Get())` and `if (AActor* Boss = Record.Target.Get())` (cpp:494, 512, 520). If the boss actor is still valid (not destroyed/pending kill), these checks **pass**.
  5. Posture/Bleed application: if `Boss->FindComponentByClass<URPGBossPosture>()` exists, it calls `Posture->ApplyPostureDamage(...)`.
  6. **Conditional Outcome Subject to Incomplete Controls:** Posture damage and bleed buildup would be deducted from the reset boss subject to incomplete conditional controls: (a) target actor remaining weak-valid, (b) hit not merged by same-montage deduplication, (c) boss not refusing damage in death state, (d) posture hold/refill state not absorbing or resetting the damage, (e) row/table resolution and bleed override, and (f) world and delegate remaining valid across tick boundary. A next-tick delegate is not a guaranteed next rendered frame, and execution depends on world and delegate lifetime.
- **Required Observations for Future Verification (Unrun):**
  - Record private queue count via dedicated test fixture before and after `ResetEncounter()`.
  - Observe execution order of next-tick timer delegate versus encounter reset completion.
  - Read back `URPGBossPosture::Posture` and `URPGBossBleed` state on Frame N+2 to observe whether pre-reset hit damage was applied post-reset.

### Case 2: Health Loss Arriving After Reset While `Scaler` Retains State
- **Hypothesized Interleaving:** Player strikes boss with Starter Sword (`HealthDamageMultiplier = 0.39f`). `FinalizePending` registers `Scaler.OnHit(Time, 0.39f)`. Before the pack's corresponding health loss is sampled, `ResetEncounter()` runs while boss health is at or near max, such that `Health > PrevBossHealth + 0.5` is false on the subsequent sample.
- **Conditional Execution Path in Source:**
  1. `Scaler.Reset()` is not called by the health-jump branch.
  2. Non-empty condition: `Scaler.Hits` retains `FHit { Time, 0.39f }` **only if** a scaled hit was actually waiting and not previously matched or pruned.
  3. Window constraint: `Prune(Time)` in `OnHit`/`OnLoss` discards entries older than `Window = 0.35s`. If more than 0.35s elapses before the next loss, the entry is pruned with zero effect. An idle array may physically retain entries until `Prune` is invoked on the next call.
  4. Matching formula: if a pack loss arrives within 0.35s, `Scaler.OnLoss` matches the waiting `FHit`, returning `Adjust = Amount * (1.0 - 0.39) = 0.61 * Amount`.
  5. Adjustment clamp: `AdjustBossHealth` calls `FRPGDamageScaler::Apply(Health, Adjust, MaxHealth)`. The adjustment is clamped to `MaxHealth` and cannot revive a dead boss (`Health <= 0.0`).
- **Required Observations for Future Verification (Unrun):**
  - Record `Scaler.Hits.Num()` and `Scaler.Losses.Num()` immediately post-reset with known pre-reset state.
  - Verify elapsed time between pre-reset hit and post-reset loss against the 0.35s window.
  - Read `AdjustBossHealth` log output on the subsequent encounter's opening strike.

### Case 3: Captured Swing vs Mid-Swing Table / Override Changes
- **Hypothesized Interleaving:** Player initiates an attack montage. In `TickComponent`, `OnMontageStarted` executes, calls `Table->Find()`, and copies `FRPGWeaponAttackRow` into `Current.Row`. Mid-swing (before animation position reaches `HyperArmorEnd`), an external caller modifies `Table->Rows` or calls `ClearCostOverrides()`.
- **Conditional Execution Path in Source:**
  1. Table decoupling: `Current` holds a value copy of `FRPGWeaponAttackRow`. Modifying `Table->Rows` mid-swing does not alter `Current.Row`.
  2. Override clearing: `ClearCostOverrides()` clears `HyperArmorOverrides` and `CostOverrides`. It does not modify `Current.Row`.
  3. Hyperarmor dynamics: `UpdateHyperArmor(Montage, Position)` evaluates window boundaries each tick. If active montage ends, `TickComponent` calls `UpdateHyperArmor(nullptr, 0.f)`, clearing hyperarmor.
  4. ResetCounters impact: calling `ResetCounters()` mid-swing clears `Current` and `LastAttack`, but does not clear `TrackedMontage`, and does not immediately call `SetHyperArmor(false)`. Hyperarmor is dropped on the subsequent tick when `UpdateHyperArmor` runs without a matching attack row, or in `EndPlay()`.
  5. **Conditional Outcome:** In-flight captured swing values are isolated from table edits, but active hyperarmor is not unconditionally guaranteed throughout the swing; it remains subject to montage continuity, interruption, and component lifecycle.
- **Required Observations for Future Verification (Unrun):**
  - Record `Current.Row.HyperArmorStart/End` before and after table modification.
  - Inspect `bHyperArmor` state and `IsPlayerHitStunBlockedByImmunity()` across montage playback.
  - Trace `ResetCounters()` execution during an active swing to observe tick-delayed hyperarmor removal and confirm that `TrackedMontage` remains set until montage transition.

### Case 4: Target Replacement and Weak Reference Caching (`WatchedBoss` & `TrackedPlayer`)
- **Hypothesized Interleaving:** Boss actor is destroyed or replaced with a new instance (e.g. arena reload or phase replacement), while the player pawn and `URPGHitIntake` persist.
- **Conditional Execution Path in Source:**
  1. Control A (Still-Live Old Actor): if the previous boss actor remains valid in memory (e.g. deactivated/hidden but not destroyed), `WatchedBoss.Get()` returns a valid pointer. `TrackBossHealth` does not re-query, maintaining a stale target cache.
  2. Control B (Destroyed Old Actor): per engine `TWeakObjectPtr::IsValid()`, once an actor is marked pending kill / garbage, `WatchedBoss.Get()` returns `nullptr`.
  3. Acquisition throttle: once `WatchedBoss.Get()` evaluates null, `TrackBossHealth` does not search immediately; it accumulates `BossSearchTimer += DeltaTime` and throttles the `TActorIterator` search against an accumulated 0.5s threshold (which may trigger sooner if time has already accumulated).
  4. Baseline reset: upon acquiring the new boss actor, `TrackBossHealth` explicitly assigns `PrevBossHealth = -1.0;`, ensuring health loss is not evaluated against the prior boss's health on the first frame.
  5. Player tracking contrast: `URPGBossEncounter::TickComponent` checks `TrackedPlayer.IsValid() && TrackedPlayer.Get() != Player`. If `TrackedPlayer` is invalid, the reset branch is bypassed; it assigns `TrackedPlayer = Player;` without triggering reset.
- **Required Observations for Future Verification (Unrun):**
  - Test Control A: replace boss while keeping old actor valid; observe whether `WatchedBoss` re-queries and read back weak identity and selected actor.
  - Test Control B: destroy old boss; observe the accumulated search delay before new boss acquisition.
  - Verify `PrevBossHealth` reset to `-1.0` upon new boss acquisition.

---

## 6. Architectural Observations & Unapproved Proposals

Without altering existing pack flows, the following architectural alternatives are recorded as unapproved design options only:

1. **Explicit Reset Event Notification:**
   - Option: Introduce an event dispatcher on `URPGBossEncounter` (or subsystem) notifying registered combat components of encounter reset.
   - Allows `URPGHitIntake` and `URPGSwingTracker` to clear pending queues and scalers deterministically without relying on health jump heuristics.
2. **Explicit Timer Handle Tracking in `URPGHitIntake`:**
   - Option: Store `FTimerHandle FinalizeTimerHandle` instead of relying solely on `bFinalizeScheduled`.
   - Allows canceling pending next-tick delegates upon component reset or encounter boundary.
3. **Preservation of Legacy Extraction Boundaries:**
   - The decoupled design preserves loose coupling between player adapters and boss actors. Any future synchronization should avoid hard-coding boss class types or breaking passive monitoring guarantees.

---

## 7. Conclusion & Scope Verification

- **Offline Reset Audit Complete (Rev 03):** Precision updates applied to reflect player i-frame reset notification, incomplete conditional controls, accumulated search thresholds, and tick accumulation vs wall-clock timing.
- **Zero Forbidden Edits:** No edits to `Source/`, `Config/`, `Scripts/`, Unreal assets, or Codex drafts.
- **Zero Prohibited Executions:** No Unreal Editor, PIE, build, packaging, or `UnrealPak` commands were executed.
- **Git Authority Preserved:** In strict accordance with `RULE[c:\UnrealProject\OneBossFight\AGENTS.md]`, no git commits or pushes were performed.
