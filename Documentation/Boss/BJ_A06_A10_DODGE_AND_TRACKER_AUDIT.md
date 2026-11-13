# BJ-A06..BJ-A10: Dodge Input, Owned I-Frame Lifecycle & Tracker Window Reset Audit

**Authority:** [`QUEUE_BJ_AG.md`](file:///C:/UnrealProject/OneBossFight/Documentation/Boss/QUEUE_BJ_AG.md) Batch 2 (`BJ-A06..BJ-A10`)  
**Scope:** Strictly read-only C++/test-source audit (`0` live actor/timer/engine/build/commit operations).

---

## 1. `BJ-A06`: Dodge Input Activation Ordering (`RPGDodgeTiming.cpp`, `RPGDodgeInputRules.h`, `RPGDodgeActivationRules.h`)

Traced `URPGDodgeTiming::OnDodgePressed` ([`RPGDodgeTiming.cpp:507-595`](file:///C:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGDodgeTiming.cpp#L507-L595)) and next-tick recovery ([`:142-187`](file:///C:/UnrealProject/OneBossFight/Source/OneBossFight/Player/RPGDodgeTiming.cpp#L142-L187)):

1. Guards `!World || !Ability` -> early return (`:511-514`).
2. Computes `LastPressGap`, `bLastPressFull`, increments `++PressCount` (`:516-519`). When `PressCount == 1` (`:520-550`), reads reflected `Can Activate Ability?` and arms `PendingDodgeActivationRetryPress = 1` + `PendingDodgeActivationRetryAfterTime = Now`.
3. Synchronously loads `QuickMontage` and `FullMontage`; returns early if either is null (`:551-556`).
4. Branches strictly:
   - `RPGDodgeInputRules::DecideTap(!HasNoDirectionInput(), true) == Backstep` AND `!(bActive && Selected == EKind::Full)` -> `Backstep` (`:560-571`).
   - Else `!bLastPressFull` -> `Quick` (`:572-578`).
   - Else `bActive && Selected == EKind::Full` -> `Ignored` (`:579-584`).
   - Else `Full` (calls `ForceFullRoll` when active, `:585-594`).
5. On a later tick (`World->GetTimeSeconds() > PendingDodgeActivationRetryAfterTime + KINDA_SMALL_NUMBER`, `:143-187`), retries at most once via `RPGDodgeActivationRules::ShouldRetryFirstPress(Press == 1, bCanActivate, bDiagnosticActive, bFirstRetryAttempted)`, setting `bFirstDodgeActivationRetryAttempted = true` BEFORE Blueprint re-entry (`:163`).
- **Edge Finding (`Low`, `RPGDodgeTiming.cpp:519-556`):** If `QuickMontage` or `FullMontage` fails to load (`:553`), `:555` returns *after* arming `PendingDodgeActivationRetryPress = 1`, allowing `TickComponent` to attempt a fallback activation without a valid clip.

---

## 2. `BJ-A07`: Owned `Status.Invulnerable` Lifecycle & Cleanup (`RPGIFrameMonitor.cpp`, `RPGOwnedTagCleanup.h`)

- **`OnEncounterReset()` (`RPGIFrameMonitor.cpp:147-156`):** Calls `RemoveTag("encounter reset")`. Only clears `bTag` and `bOwnedNow` if `RemoveTag` returns `true` (`:149`); otherwise preserves ownership flags for a later tick or `EndPlay`.
- **`EndPlay()` (`RPGIFrameMonitor.cpp:158-172`):** Calls `RemoveTag("EndPlay")`; on failure (`:163-166`), invokes `RPGOwnedTagCleanup::ScheduleAfterRemovalFailure(GetOwner(), "Status.Invulnerable", "RPGIFrameMonitor.EndPlay")` before clearing `bTag`/`bOwnedNow`.
- **Delayed Cleanup Findings (`RPGOwnedTagCleanup.h:27-67`):**
  1. **Medium (`RPGOwnedTagCleanup.h:37-67`):** `RetryUntilRemovalIssued` keys solely on `TWeakObjectPtr<AActor> WeakOwner` and `Tag` with zero encounter-generation or lease token; on a reused live actor across reset/dodge transitions, an overdue retry (`0.25s..4.0s`) can strip an active `Status.Invulnerable`.
  2. **Low (`RPGOwnedTagCleanup.h:21-66`):** Retries indefinitely every `4.0s` (`Exponent` clamped at `4`) while `Owner` stays alive if `RemoveOwnedGameplayTag` persistently fails.
  3. **Low (`RPGOwnedTagCleanup.h:27-35`):** Evaluates `CallBlueprintFunction(...)` invocation success only without reading return bool.

---

## 3. `BJ-A08`: Swing & Attack Tracker Window Resets (`RPGSwingTracker.cpp`, `RPGAttackTracker.cpp`)

- **`RPGSwingTracker` (`RPGSwingTracker.cpp:128-175, 291-325`):** Clears hyperarmor on `!Montage` (`:158-163`), `EndPlay` (`:130-133`), and failed refresh (`:319-322`), and starts a new swing on montage name change OR backward seek (`Position + KINDA_SMALL_NUMBER < LastMontagePosition`, `:167`). Edge (`Low`, `:167`): same-montage restart at exact `Position == 0.f` when `LastMontagePosition == 0.f` skips `OnMontageStarted`, preserving `Swing.Id`/`ApplyFailedSwing`.
- **`RPGAttackTracker` (`RPGAttackTracker.cpp:369-485`):** `End(...)` restores telegraph rate and resets `Phase = EPhase::None` / `TimingIndex = INDEX_NONE` on `!bEnabled`, `!Anim`, `bDead`, or `Index != TimingIndex` (`:382-426`). Edge (`Low`, `:418`): restart detection checks only `Index != TimingIndex` (not backward position seek on the same active `Index`).

---

## 4. `BJ-A09..BJ-A10`: Test Mapping & Bounded Disposition

- **Covered Pure Rules (`0` defects):** `RPGAutomationTests.cpp:480-490` (`ShouldRetryFirstPress`), `RPGDodgeInputRulesTests.cpp:12-32` (`DecideTap`), `RPGOwnedTagCleanupTests.cpp:10-31` (`ShouldRetry`, `RetryDelaySeconds`), `RPGAutomationTests.cpp:604-655` & `RPGCodexTests.cpp:108-119` (`RPGSwingRules`), `RPGBossAttackTrackerAdaptersTests.cpp:17-100`.
- **Lead Follow-Ups (Runtime/World-Dependent):** Two-generation live-actor reuse test for `RPGOwnedTagCleanup::RetryUntilRemovalIssued`, missing-montage retry guard at `RPGDodgeTiming.cpp:553`, and same-index montage backward-seek check at `RPGAttackTracker.cpp:418`. (`0` unrequested production edits.)
