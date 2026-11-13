# BJ-A26..BJ-A30: Move Executor, Montage Notify Timing & Watchdog Audit

**Authority:** [`QUEUE_BJ_AG.md`](file:///C:/UnrealProject/OneBossFight/Documentation/Boss/QUEUE_BJ_AG.md) Batch 6 (`BJ-A26..BJ-A30`)  
**Scope:** Strictly read-only C++/test-source audit (`0` montage/PIE/build/engine/commit operations).

---

## 1. `BJ-A26`: Executor State Transitions & Terminal Callbacks (`RPGFrameworkMoveExecutor.cpp`)

Verified lifecycle state machine ([`RPGFrameworkMoveExecutor.cpp:100-287, 747-773`](file:///C:/UnrealProject/OneBossFight/Source/OneBossFight/Boss/RPGFrameworkMoveExecutor.cpp#L100-L287)):
- **`Idle -> StartCard` (`:125-180`):** Requires `bInitialized && !bAborted && OwnerBoss && Target && IsIdle() && !bFinished`; computes fatigue scale + `ParryFairTelegraph`, validates `CardWatchdogTimeoutSeconds` (`HoldMaxSeconds` added at `:151`), calls `Model_.Start`, plays dynamic montage, advances model at `0.0`, and acquires `LockMotion()`.
  - Conditional note (`Low`, `:155-158`): `SetComponentTickEnabled(true)` is enabled before `Sequence`/`Anim` & `Model_.Start` validation, though `TickComponent` safely early-returns on `!OwnedMontage` (`:184`).
- **Single Terminal Exit (`Finished` vs `Abort`):**
  - Clean completion (`:205-221`): crosses `RecoveryEnd` -> stops residual montage, releases grab (`CardEnded`), unlocks motion (`Finished`), restores play rate, sets `OwnedMontage = nullptr; bFinished = true`, disables tick. Re-armed strictly via `PrepareNextAttack()` (`:119-124`).
  - Abort (`:747-769`): guarded by `if (bAborted || bFinished) return;`, clears area snare, releases grab, saves `LastAbortedToken`, calls `Model_.Abort`, restores play rate before `Montage_Stop`, clears `OwnedMontage`, unlocks motion, disables tick (one-shot even under repeat-abort test hook `:760-767`). Recovery in same generation requires `RecoverAfterAbort()` (`:112-118`), or cross-generation via `Rearm(NewGeneration)` (`:100-111`).

---

## 2. `BJ-A27`: Montage Notify Timing Fallback & Backward Seeks (`RPGMontageNotifyTiming.cpp`, `RPGAttackTracker.cpp`)

- `RPGMontageNotifyTiming::Validate` (`:27-48`): enforces `/Game/` prefix, non-`None` `MoveId`, finite fields, `0 <= Commit <= WindowStart < WindowEnd <= RecoveryEnd <= MontageLength`, `TrackTurnRate >= 0`, `BranchRange >= 0`, `BranchConeDegrees in [10, 360]`.
- `SelectTiming` (`:83-113`) & `FCache::Resolve` (`:153-187`, called at `RPGAttackTracker.cpp:444-452`): `!bEnabled || Annotations.IsEmpty()` leaves `LegacyTiming` untouched; duplicate or invalid annotations fail `CollectAnnotations` / `SelectTiming`, latch `bCachedValid = false`, warn once (`bOutWarnOnce`), and preserve `CachedTiming = LegacyTiming`.
- `FObserver::Sample` (`:125-142`): backward seek `Position < LastPosition` triggers `Reset(); return false;` (`LastPosition = -1.f`).

---

## 3. `BJ-A28..BJ-A30`: Watchdog, Late Callback Identity & Test Mapping

- **Late Callback Identity (`RPGBossMoveModel.cpp:88-91`, `RPGFrameworkMoveExecutor.cpp:168-174`):** `AcceptsCallback(Token)` checks `bInitialized && CurrentState != Idle && Token.InstanceId != 0 && Token.EncounterId == Encounter && Token.Generation == Epoch && Token == CurrentToken`; `LastAbortedToken` is strictly refused (`MoveModel.StaleCallback`).
- **Watchdog Pre-Flight (`RPGFrameworkMoveExecutor.cpp:150-152, 193-197`):** Cards whose active clip `(ClipLength - BlendOut) / CardPlayRate` exceeds `CardWatchdogTimeoutSeconds` fail before playback (`WatchdogWindow`). During playback, `Now - StartWorldSeconds > CardWatchdogTimeoutSeconds` sets `bWatchdogFired = true` and calls `Abort("Framework.Playback.WatchdogTimeout")`.
- **Mapped Tests (`0` pure-rule defects):** `RPGBossExecutorHarnessTests.cpp` (`D8` active replacement refusal, `RecoverAfterAbort`, abort/rearm lifecycle), `RPGBossMoveModelTests.cpp`, `RPGBossAttackTrackerAdaptersTests.cpp:126-174` (`SelectTiming`/`CollectAnnotations`/`FObserver` fallback & backward seek), `RPGFrameworkRuntimeTests.cpp:513-525`.
