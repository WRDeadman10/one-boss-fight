# Executor Watchdog Design: BOSS-EXE-007 & BOSS-ANM-007

**Date:** 2026-11-01  
**Author:** Antigravity (offline review for Tech Lead Claude)  
**Scope:** Resolving the shared missing watchdog in `URPGFrameworkMoveExecutor` for `BOSS-EXE-007` ("Watchdog reset") and `BOSS-ANM-007` ("Notify-end independence").  
**Status:** Design Proposal (No Source code modified).

---

## 1. Problem Statement & Shared Architectural Root Cause

Both `BOSS-EXE-007` and `BOSS-ANM-007` are currently retained as **PARTIAL** in Ledger v3.11 due to the identical missing runtime capability:
1. **`BOSS-EXE-007` (Watchdog reset):**
   * *Canonical Observable:* `"Suppressed MontageEnd / NotifyEnd automatically aborts card after Timeout = RecoveryEndSeconds + 0.5s."`
   * *Current State:* `RPGBossMoveModelTests.cpp:114` asserts that `RPGBossMoveModel` transitions to `ERPGBossMoveModelState::Idle` when local time crosses `RecoveryEndSeconds`. However, in the live engine executor ([`Source/OneBossFight/Boss/RPGFrameworkMoveExecutor.cpp:111-125`](file:///c:/UnrealProject/OneBossFight/Source/OneBossFight/Boss/RPGFrameworkMoveExecutor.cpp#L111-L125)), the only timeout check is `Now - StartWorldSeconds > Profile->WalkTimeoutSeconds` (a 10-second catch-all for navigation failure). If a montage stalls or suppresses natural blend-out, no $T = \text{RecoveryEndSeconds} + 0.5\text{s}$ watchdog aborts the card.
2. **`BOSS-ANM-007` (Notify-end independence):**
   * *Canonical Observable:* `"Attack state recovery and cleanup cannot stall if animation notify is dropped or montage interrupted prematurely."`
   * *Current State:* Mid-attack interruption (e.g. stance break) is verified live in PIE ([`Claude/F8/pie_run1/editor_raw.log:1619`](file:///c:/UnrealProject/OneBossFight/Docs/BossCombatReview/Execution/Claude/F8/pie_run1/editor_raw.log#L1619)), immediately executing clean model and montage abort. However, stall independence in the presence of a *dropped or frozen animation notify* is not proven because no watchdog forces card termination if the animation asset fails to complete.

Both requirements are satisfied by introducing an explicit **card-level watchdog timer** inside `URPGFrameworkMoveExecutor`.

---

## 2. Technical Architecture & Where the Timer Lives

### A. Member Location in `URPGFrameworkMoveExecutor`
The timer must live directly in `URPGFrameworkMoveExecutor` ([`Source/OneBossFight/Boss/RPGFrameworkMoveExecutor.h:58-65`](file:///c:/UnrealProject/OneBossFight/Source/OneBossFight/Boss/RPGFrameworkMoveExecutor.h#L58-L65)), because the executor owns the playback lifecycle, the world clock (`StartWorldSeconds`), and the `StopOwned()` montage abort authority.

```cpp
// Source/OneBossFight/Boss/RPGFrameworkMoveExecutor.h (private section):
double CardWatchdogTimeoutSeconds = 0.0; // BOSS-EXE-007 / BOSS-ANM-007: RecoveryEndSeconds / PlayRate + 0.5s
```

### B. Initialization at `StartCard`
In [`Source/OneBossFight/Boss/RPGFrameworkMoveExecutor.cpp:88-103`](file:///c:/UnrealProject/OneBossFight/Source/OneBossFight/Boss/RPGFrameworkMoveExecutor.cpp#L88-L103) (`StartCard`):
```cpp
const float Rate = FMath::Max(0.01f, Card->Spec().PlayRate);
CardWatchdogTimeoutSeconds = double(Card->Spec().RecoveryEndSeconds / Rate) + 0.5;
```
- Accounts for card `PlayRate` scaling so the timeout remains strictly 0.5s of world time past the expected recovery end.
- Resets on every new card execution.

### C. Evaluation in `TickComponent`
In [`Source/OneBossFight/Boss/RPGFrameworkMoveExecutor.cpp:111-125`](file:///c:/UnrealProject/OneBossFight/Source/OneBossFight/Boss/RPGFrameworkMoveExecutor.cpp#L111-L125) (`TickComponent`), right after world clock monotonicity checks:
```cpp
const double ElapsedPlayback = Now - StartWorldSeconds;
if (ElapsedPlayback > CardWatchdogTimeoutSeconds)
{
    UE_LOG(LogTemp, Display, TEXT("[FrameworkProof] watchdog_timeout instance=%llu elapsedSeconds=%g timeoutSeconds=%g recoveryEndSeconds=%g playRate=%g"),
        Token.InstanceId, ElapsedPlayback, CardWatchdogTimeoutSeconds, double(Card->Spec().RecoveryEndSeconds), double(Card->Spec().PlayRate));
    Abort(TEXT("Framework.Playback.WatchdogTimeout"));
    return;
}
```

---

## 3. Telemetry Schema & Structured Log Tokens

Two structured tokens provide unambiguous, machine-verifiable telemetry:

1. **`watchdog_timeout` (New Token #54 in `validate_framework_proof_logs.py`):**
   ```text
   [FrameworkProof] watchdog_timeout instance=<uint64> elapsedSeconds=<float> timeoutSeconds=<float> recoveryEndSeconds=<float> playRate=<float>
   ```
   *Regex:* `^instance=\d+ elapsedSeconds=[^\s]+ timeoutSeconds=[^\s]+ recoveryEndSeconds=[^\s]+ playRate=[^\s]+$`

2. **`cleanup` (Existing Token #75):**
   ```text
   [FrameworkProof] cleanup reason=Framework.Playback.WatchdogTimeout modelIdle=1 ownedMontageStopped=1
   ```
   Emitted automatically by `URPGFrameworkMoveExecutor::Abort()` ([`RPGFrameworkMoveExecutor.cpp:78-86`](file:///c:/UnrealProject/OneBossFight/Source/OneBossFight/Boss/RPGFrameworkMoveExecutor.cpp#L78-L86)), confirming:
   - `modelIdle=1` (MoveModel aborted cleanly to Idle).
   - `ownedMontageStopped=1` (Transient montage playback halted).

---

## 4. Verification Plan: Unit Test & Live PIE Proof Hook

### A. Automation Test (`RPGFrameworkRuntimeTests.cpp`)
Add test `OneBossFight.Framework.Runtime.ExecutorWatchdog` in [`Source/OneBossFight/Tests/RPGFrameworkRuntimeTests.cpp`](file:///c:/UnrealProject/OneBossFight/Source/OneBossFight/Tests/RPGFrameworkRuntimeTests.cpp):
1. Spawn framework boss and move executor.
2. Initialize card with `RecoveryEndSeconds = 1.0s`, `PlayRate = 1.0` (expected timeout = 1.5s).
3. Start card.
4. Advance world clock to $t = 1.2\text{s}$ (past recovery end, but within 0.5s margin); assert `executor->IsIdle() == false`.
5. Advance world clock to $t = 1.55\text{s}$ without calling montage finish.
6. Tick executor. Assert:
   - `executor->IsIdle() == true`
   - `executor->DidFinish() == false`
   - Model state is `ERPGBossMoveModelState::Idle`.

### B. Live PIE Scenario Hook (`L_SevarogFrameworkProofEXE007`)
1. **Non-Shipping Test Hook CVar:**
   ```cpp
   #if !UE_BUILD_SHIPPING
   static TAutoConsoleVariable<int32> CVarBossProofSuppressMontageEnd(
       TEXT("rpg.BossProofSuppressMontageEnd"),
       0,
       TEXT("1: Suppress montage natural end / loop montage to force watchdog timeout."),
       ECVF_Default);
   #endif
   ```
2. **PIE Driver Execution:**
   - Run PIE with `-SuppressMontageEnd` (sets `rpg.BossProofSuppressMontageEnd 1`).
   - Boss executes attack 1 (`SwingSlow_F5`, `RecoveryEndSeconds = 1.65s`).
   - Normal montage blend-out is suppressed at $t = 1.65\text{s}$.
   - At $t = 2.15\text{s}$, executor logs `watchdog_timeout instance=1 elapsedSeconds=2.1502 timeoutSeconds=2.1500 ...`.
   - Executor logs `cleanup reason=Framework.Playback.WatchdogTimeout modelIdle=1 ownedMontageStopped=1`.
   - Boss AI transitions cleanly to next attack (or idle), proving zero stall.

---

## 5. Ledger Impact & Graduation Criteria

Implementing and proving this single mechanism concurrently graduates **both** remaining engine-only PARTIAL rows to **WITNESSED**:
1. `BOSS-EXE-007`: Witnessed by the live `watchdog_timeout` firing at strictly $\text{RecoveryEndSeconds} + 0.5\text{s}$.
2. `BOSS-ANM-007`: Witnessed by proving attack state recovery and cleanup cannot stall when animation notifies / montage ends are suppressed.

**New Census Projection:**
- **WITNESSED:** **42** (51.2%)
- **PARTIAL:** **16** (19.5%)
- **NOT YET:** **24** (29.3%)
