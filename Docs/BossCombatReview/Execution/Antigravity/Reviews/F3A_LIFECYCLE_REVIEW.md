# F3a Staged Source Lifecycle & Failure Paths Independent Review (A-252)

**Document Version:** 1.0.0  
**Author:** Antigravity (Independent Second Review)  
**Task Reference:** `[C-387]`, Order A-252  
**Target Codebase:** Codex Staged F3a Source (`Docs/BossCombatReview/Execution/Codex/Framework/F3/Staging/Source/OneBossFight/**`, 15 destinations)  
**Scope:** Lifecycle and failure paths only (finish, early montage stop, target destroyed, possession change, world end, timeout, clock reversal, generation reset, EndPlay).  
**Rules:** Concrete defects only with file:line and triggering sequence; zero style commentary; C-381 instance-reservation defect omitted per instructions.  

---

## 1. Concrete Defect Catalog

### Defect 1: Non-Idempotent `URPGFrameworkMoveExecutor::Abort()` Causes Duplicate Cleanup Emissions and Double Model Aborts on Level Teardown / Destruction
- **Files & Lines:**
  - `Source/OneBossFight/Boss/RPGFrameworkMoveExecutor.cpp:112-118`
  - `Source/OneBossFight/Boss/RPGFrameworkBossCharacter.cpp:94`
  - `Source/OneBossFight/Boss/RPGFrameworkMoveExecutor.cpp:121-122`
- **Triggering Sequence:**
  1. An active attack fails (e.g. `Fail(TEXT("Framework.Playback.EarlyStop"))`).
  2. `ARPGFrameworkBossCharacter::Fail` calls `Executor->Abort(Reason)`.
  3. `URPGFrameworkMoveExecutor::Abort` executes: sets `bAborted = true`, stops montage, and emits log: `[FrameworkProof] cleanup reason=<Reason> modelIdle=1 ownedMontageStopped=1`.
  4. Actor teardown / destruction occurs:
     - `ARPGFrameworkBossCharacter::EndPlay` (line 94) explicitly calls `Executor->Abort(TEXT("EndPlay"))`.
     - `URPGFrameworkMoveExecutor::Abort` executes a second time because it **lacks an idempotency guard** (`if (bAborted || IsIdle()) return;`).
     - A second cleanup log is emitted: `[FrameworkProof] cleanup reason=EndPlay modelIdle=1 ownedMontageStopped=1`.
     - `ARPGFrameworkBossCharacter::EndPlay` calls `Super::EndPlay(Reason)`, which cascades to `URPGFrameworkMoveExecutor::EndPlay` (line 122).
     - `URPGFrameworkMoveExecutor::EndPlay` calls `Abort(TEXT("EndPlay"))` a third time, emitting a duplicate cleanup line.
- **Contract Violated:** *"leave the boss inactive exactly once"*. `Abort` must early-out if already aborted or already idle, and `Token.InstanceId` must be cleared.

---

### Defect 2: Successful Move Completion Fails to Disable Component Tick, Permitting Post-Success Abort Logging on `EndPlay`
- **Files & Lines:**
  - `Source/OneBossFight/Boss/RPGFrameworkMoveExecutor.cpp:70-73`
  - `Source/OneBossFight/Boss/RPGFrameworkMoveExecutor.cpp:121-122`
- **Triggering Sequence:**
  1. Attack montage completes normally: `Model.State() == ERPGBossMoveModelState::Idle` and `!Anim->Montage_IsActive(OwnedMontage)`.
  2. Line 71 executes: `OwnedMontage = nullptr; bFinished = true; UE_LOG(..., "cleanup reason=Finished modelIdle=1 ownedMontageStopped=1");`
  3. `SetComponentTickEnabled(false)` is **omitted**.
  4. The executor component continues ticking every frame (short-circuiting on line 60 `!OwnedMontage`).
  5. When the world ends or level unloads, `URPGFrameworkMoveExecutor::EndPlay` runs line 122: `Abort(TEXT("EndPlay"))`.
  6. Because `bAborted` was false, `Abort()` executes and logs: `[FrameworkProof] cleanup reason=EndPlay modelIdle=1 ownedMontageStopped=1`.
- **Contract Violated:** A successfully finished move (`reason=Finished`) is subsequently re-cleaned with `reason=EndPlay`. `SetComponentTickEnabled(false)` must be called upon normal finish, and `Abort` must ignore finished moves (`bFinished`).

---

### Defect 3: Navigation Controller `MoveTo` Synchronous Completion / Failure Drops Callback Due to Unset `OwnedRequest`
- **Files & Lines:**
  - `Source/OneBossFight/Boss/RPGFrameworkBossController.cpp:21-27`
  - `Source/OneBossFight/Boss/RPGFrameworkBossController.cpp:30-34`
- **Triggering Sequence:**
  1. `WalkToBand` dispatches pathfinding via `const FPathFollowingRequestResult R = MoveTo(Request, &Path);` (line 22).
  2. If `PathFollowingComponent` completes synchronously during `MoveTo()` (e.g. immediate failure, path blocked, or instant arrival), `OnMoveCompleted(RequestID, Result)` is dispatched **synchronously from within `MoveTo()`**.
  3. `OnMoveCompleted` line 33 checks: `if (OwnedRequest == FAIRequestID::InvalidRequest || RequestID != OwnedRequest) return;`.
  4. At this point, line 25 (`OwnedRequest = R.MoveId;`) has **not executed yet**. `OwnedRequest` is still `FAIRequestID::InvalidRequest`.
  5. The synchronous completion callback is dropped.
  6. While line 27 explicitly checks `R.Code == AlreadyAtGoal`, if `MoveTo` fails synchronously (or aborts an active move), the callback is lost, and `OwnedRequest` is latched to an ID that will never fire again, hanging the navigation phase until timeout.
- **Contract Violated:** Stale/unlatched token race on synchronous engine dispatch.

---

### Defect 4: Loss of Possession Leaves Navigation Running and Allows Orphaned Callback to Drive Character
- **Files & Lines:**
  - `Source/OneBossFight/Boss/RPGFrameworkBossController.h:13-17`
  - `Source/OneBossFight/Boss/RPGFrameworkBossController.cpp:30-38`
  - `Source/OneBossFight/Boss/RPGFrameworkBossCharacter.cpp:68-80`
- **Triggering Sequence:**
  1. Boss character is walking to band under `ARPGFrameworkBossController`.
  2. Controller is unpossessed (e.g. `AController::UnPossess()` during player possession or AI controller destruction).
  3. `ARPGFrameworkBossController` **does not override `OnUnPossess()`**, leaving path following active in the controller.
  4. When path following completes, `OnMoveCompleted` runs: `BossOwner` is still valid, so line 36 calls `BossOwner->WalkArrived()` on a pawn the controller **no longer possesses**.
  5. Concurrently, `ARPGFrameworkBossCharacter::Tick` does not verify `GetController() == ExpectedController`, allowing the unpossessed character to initiate combat moves without a valid controller.
- **Contract Violated:** *"possession change ... must stop the owned move request, and leave the boss inactive exactly once"*. `OnUnPossess()` must abort path following and clear `BossOwner`.

---

### Defect 5: Missing Generation Reset Handling Causes Valid Resets to Fail as Critical Errors
- **Files & Lines:**
  - `Source/OneBossFight/Boss/RPGFrameworkMoveExecutor.h:19-27`
  - `Source/OneBossFight/Boss/RPGFrameworkMoveExecutor.cpp:89-91`
  - `Source/OneBossFight/Player/RPGBossMoveModel.cpp:84`
- **Triggering Sequence:**
  1. Boss starts an attack under generation $G$ with `Token.Generation = G`.
  2. Encounter or fixture triggers a Generation Reset ($G \to G+1$) via `Model.ResetGeneration(G+1)`.
  3. `URPGFrameworkMoveExecutor` exposes zero API or hook for generation reset.
  4. On the next tick, `AdvanceObservedLocal` checks `Token.Generation == Epoch`, which fails.
  5. `AdvanceObservedLocal` returns `false` with error `MoveModel.StaleCallback`.
  6. Line 90 calls `Fail(*Error)`, which logs: `[FrameworkProof] ERROR token=MoveModel.StaleCallback bossInactive=1`.
  7. A legitimate generation reset is treated as an unexpected system fault rather than cleanly stopping the owned montage and returning to idle.
- **Contract Violated:** *"generation reset ... must stop the owned montage, close model windows, stop the owned move request, and leave the boss inactive exactly once; and every engine callback must be ignored when it belongs to an old request/token."*

---

### Defect 6: Semantic Coupling Bug: Using Navigation `WalkTimeoutSeconds` for Combat Attack Playback
- **Files & Lines:**
  - `Source/OneBossFight/Boss/RPGFrameworkMoveExecutor.cpp:65`
  - `Source/OneBossFight/Player/RPGBossFrameworkProfile.h:22`
- **Triggering Sequence:**
  1. During attack playback, line 65 enforces: `Now - StartWorldSeconds > Profile->WalkTimeoutSeconds`.
  2. `Profile->WalkTimeoutSeconds` is explicitly designed and tuned for walking traversal across the arena floor, not attack montage duration.
  3. If an attack sequence with long recovery or slow play rate (e.g. `Subjugation` at 2.87s) runs under a strict walk timeout (e.g. 2.0s), the attack prematurely aborts mid-swing with `Framework.Playback.TimeoutOrClock`.
  4. Attack timeout must be derived from `Card->Spec().RecoveryEndSeconds + WatchdogTolerance` rather than the navigation walk timeout.
- **Contract Violated:** Attack watchdog timeout must be governed by attack card bounds.

---

### Defect 7: Incomplete Token Invalidation in `URPGFrameworkMoveExecutor::Abort()`
- **Files & Lines:**
  - `Source/OneBossFight/Boss/RPGFrameworkMoveExecutor.cpp:115-116`
- **Triggering Sequence:**
  1. `URPGFrameworkMoveExecutor::Abort` calls `Model.Abort(Token, Events, Error)`.
  2. Line 116 sets `bAborted = true; OwnedMontage = nullptr; SetComponentTickEnabled(false);`.
  3. `Token.InstanceId` is **never reset to 0**.
  4. Any subsequent call or inspection treats `Token` as non-zero/valid rather than cleared.
- **Contract Violated:** Aborted requests must fully invalidate active tokens (`Token = FRPGBossAttackToken()`).

---

## 2. Review Verdict

The staged F3a code provides strong foundational validation, but contains **7 concrete lifecycle and failure path defects** surrounding non-idempotent aborts, tick leaks after completion, synchronous navigation completion loss, unhandled unpossession, unhandled generation resets, and semantic timeout coupling. 
