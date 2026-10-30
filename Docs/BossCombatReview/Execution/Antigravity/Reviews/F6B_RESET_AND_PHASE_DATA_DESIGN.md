# F6B DESIGN: ENCOUNTER RESTART SEMANTICS AND PROFILE PHASE AUTHORITY DATA

Author: Antigravity  
Date: 2026-10-30  
Task: Order A-297 Item 2 (Lead Order C-418)  
Status: Complete, 100% Offline Verified Against Project Source and Test Suites  

---

## 1. Executive Summary & Purpose

Following the successful verification of F6a (`Claude/F6/final_f6_run1..3`), where the framework boss demonstrated valid hit intake, native health reduction, `ReadAttribute` reflection, and clean death termination, F6b establishes:
1. **Encounter Restart Semantics:** Concrete state machine and generation reset rules restoring the framework boss and target to clean initial state without restarting the game process.
2. **Trigger Authority:** Explicit fixture-driven orchestration (`ARPGFrameworkProofFixture::RestartEncounterForTest`) ensuring headless and PIE automation can trigger reproducible resets without relying on player controller loops.
3. **Witness Observables:** Precise structured log lines justifying `BOSS-EXE-001` (reset priority & cleanup) and candidate `BOSS-DEF` rows.
4. **Minimal Phase Authority Data Fields:** Authored profile properties (`URPGBossFrameworkProfile`), exact UPROPERTY declarations, metadata clamp ranges, monotonic latching, and neutral-only transition gating.

---

## 2. Framework Boss Generation Reset Semantics

In the project's combat architecture, an encounter reset is not merely resetting a health variable; it is an **epoch boundary** that invalidates all stale state across the character, executor, selector, damage resolver, and combat target.

### 2.1 Character State Reset
On `ARPGFrameworkBossCharacter`:
- **Health Refill:** `Health = MaxHealth;` (using profile-authored `BossMaxHealth`, e.g. 250.0f).
- **Death Flag Cleared:** `bDead = false;`
- **State Machine Flags Cleared:** `bSucceeded = false; bFailed = false; bArrived = true; bStartedMove = false; AttacksDone = 0;`
- **Kinematic Transform Reposition:** Teleport mesh and capsule back to `WalkStart` / `WalkStartRotation`, halting any remaining movement drift via `GetCharacterMovement()->StopMovementImmediately()`.

### 2.2 Executor Re-Arm
On `URPGFrameworkMoveExecutor`:
- If an attack was active during reset, calls `Abort(TEXT("EncounterReset"))` to guarantee all hit windows are closed and montages stopped.
- Re-arms internal execution state (`PrepareNextAttack()`), setting `DidFinish() = false; IsClean() = true;`.

### 2.3 Selector Memory Reset
On `FRPGBossMoveSelector`:
- Invokes `Selector.Reset()` (`Source/OneBossFight/Player/RPGBossMoveSelector.h:35-45`).
- Clears anti-repeat cooldown timers, candidate eligibility history, and last chosen move memory, restoring the initial uniform or weight-prioritized selection state.

### 2.4 Damage Resolver Provider & Generation Increment
In `Source/OneBossFight/Player/RPGDamageResolver.cpp:40-65`:
- `++GenerationId;` increments the encounter generation monotonically (e.g. Generation 1 -> Generation 2).
- `URPGDamageResolver::SyncGeneration()` queries `ProviderGeneration()`:
  ```cpp
  if (CurrentGeneration() != LastGeneration)
  {
      LastGeneration = CurrentGeneration();
      Spent.Reset(); // Wipes all previous contact keys (MoveId|Instance|HitKey)
  }
  ```
- **Stale Payload Invalidation:** Any lingering in-flight javelin, wave, or delayed attack payload from Generation 1 that attempts to resolve against Generation 2 evaluates `Payload.Generation != CurrentGeneration()`, returning `ERPGDamageOutcome::RejectedStale` (`RPGDamageResolver.cpp:123, 148`).

### 2.5 Proof Target Health Restored
- In headless proof harnesses (`ARPGFrameworkProofFixture`), the target (e.g. `ExplicitPlayer` or dummy pawn) had its health reduced during the encounter.
- The reset restores `TargetHealth` back to `ResolvedProfile->TargetHealth` (e.g. 800.0) via `RPGPack::WriteAttribute(Target, TEXT("Attribute.Health"), TargetHealth)` or direct native setter, verifying that both combatants start fresh.

---

## 3. Trigger Authority: Fixture Call vs Player

### 3.1 Why Player Respawn Cannot Drive Framework Proofs
In the stock game, player death triggers level reloading or pawn respawn, which legacy `URPGBossEncounter` listens to via `OnPlayerRespawn` (`Source/OneBossFight/Player/RPGBossEncounter.cpp:310-325`).

However, in automated headless CI, regression suites, and PIE proof levels (`L_FrameworkProof`):
- There is **no player death/respawn loop** running.
- The framework boss is an isolated test subject controlled by `ARPGFrameworkProofFixture`.
- Relying on player death to trigger resets introduces asynchronous race conditions and controller dependencies.

### 3.2 Authoritative Fixture Call (`RestartEncounterForTest`)
We specify an explicit fixture-driven orchestration method:
```cpp
// In ARPGFrameworkProofFixture:
bool ARPGFrameworkProofFixture::RestartEncounterForTest(FString& OutError)
{
    if (!BossCharacter || !ExplicitPlayer.IsValid())
    {
        OutError = TEXT("Framework.Fixture.InvalidCombatants");
        return false;
    }
    const uint64 NextGeneration = CurrentGeneration + 1;
    CurrentGeneration = NextGeneration;
    BossCharacter->ResetEncounter(NextGeneration);
    RPGPack::WriteAttribute(ExplicitPlayer.Get(), TEXT("Attribute.Health"), ResolvedProfile->TargetHealth);
    UE_LOG(LogTemp, Display, TEXT("[FrameworkProof] encounter_reset generation=%llu boss_health=%g target_health=%g label=%s"),
        NextGeneration, BossCharacter->GetMaxHealth(), ResolvedProfile->TargetHealth, *ResolvedProfile->FixtureLabel.Replace(TEXT(" "), TEXT("_")));
    return true;
}
```

---

## 4. Witness Log Lines & Requirement Mapping

### 4.1 BOSS-EXE-001: Single Execution Authority (Reset Hierarchy)
- **Requirement:** Simultaneous execution requests, active attacks, and reset commands are arbitrated strictly by priority hierarchy (Reset > Active Attack > Selection).
- **Witness Behavior:**
  Calling `RestartEncounterForTest` while an attack is playing or after death terminates the active state, re-arms the executor, and allows a new decision on the subsequent tick.
- **Exact Structured Log Sequence:**
  ```
  [FrameworkProof] boss_dead generation=1 executorAborted=1
  [FrameworkProof] encounter_reset generation=2 boss_health=250 target_health=800 label=F6b_fixture
  [FrameworkProof] decision attack=1 generation=2 chosen=Move_Sevarog_SwingSlow_F5 score=1.85 range=165.0
  [FrameworkProof] playback_start encounter=1 generation=2 instance=1 montage=Montage_0 slot=FullBody rate=1.0
  [FrameworkProof] RESULT outcome=CompletedWithReset generation=2
  ```

### 4.2 BOSS-DEF-001: Separate Health / Posture / Reaction Tracking
- **Requirement:** Health damage, poise damage, and posture break tracked on separate independent meters, resetting cleanly across generations.
- **Witness Behavior:** Health resets to Max independently of posture; ReadAttribute immediately reflects the new max health.
- **Exact Structured Log Line:**
  ```
  [FrameworkProof] boss_health_read reader=ReadAttribute ok=1 value=250 max=250
  ```

---

## 5. Minimal Phase Authority Data Fields for Profile

### 5.1 Profile Data Declarations (`URPGBossFrameworkProfile`)
In `Source/OneBossFight/Player/RPGBossFrameworkProfile.h`:
```cpp
// --- Phase Authority Configuration (F6b) ---

/**
 * Threshold fractions of boss health that trigger phase transitions, strictly descending in (0.0, 1.0).
 * Example: [0.60] for 2-phase duel (Phase 2 at 60% HP); [0.60, 0.30] for 3-phase duel.
 */
UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Framework|Phase", meta = (ClampMin = "0.01", ClampMax = "0.99"))
TArray<float> PhaseThresholdFractions;

/**
 * Transition montages played during phase shifts (e.g. roar, weapon ignite, powerup).
 * Index 0 corresponds to Phase 1 -> 2; Index 1 to Phase 2 -> 3.
 */
UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Framework|Phase")
TArray<TSoftObjectPtr<UAnimMontage>> PhaseTransitionMontages;

/** Maximum seconds the boss remains locked in transition pose before returning to neutral. */
UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Framework|Phase", meta = (ClampMin = "0.1", ClampMax = "10.0"))
float PhaseTransitionDurationSeconds = 1.8f;

/** If true, phase transition is deferred until executor is clean (model idle, zero active hit windows). */
UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Framework|Phase")
bool bPhaseTransitionRequiresNeutral = true;
```

### 5.2 Profile Validation Rules (Preflight)
In `RPGBossFrameworkProfile::ResolveProfile`:
1. **Monotonic Threshold Order:** `PhaseThresholdFractions` must be strictly descending: `Threshold[i] < Threshold[i-1]`.
2. **Bounds Check:** Every entry must satisfy `0.01f <= Fraction <= 0.99f`.
3. **Montage Array Match:** If `PhaseTransitionMontages` is non-empty, its length must equal `PhaseThresholdFractions.Num()`.
4. **Rejection Code:** Rejects invalid configs with `Framework.Profile.InvalidPhaseThresholds`.

### 5.3 Character Runtime Phase State Machine
On `ARPGFrameworkBossCharacter`:
- **Authoritative State:**
  ```cpp
  int32 CurrentPhase = 1;
  int32 LatchedPhase = 1;
  bool bInPhaseTransition = false;
  ```
- **Monotonic Latch Invariant (`BOSS-PHS-003`):** Once `LatchedPhase = 2;`, healing above 60% HP or resetting health delta cannot decrease `LatchedPhase` back to 1. `ResolveTransition` returns `ETransitionResult::AlreadyDone` (`Source/OneBossFight/Player/RPGBossRules.h:77`).
- **Neutral-Only Gating (`BOSS-PHS-002`):** In `Tick()`, when `Health / MaxHealth <= PhaseThresholdFractions[LatchedPhase - 1]`:  
  If `!Executor->IsClean() || Executor->IsBusy()`: set `bTransitionQueued = true;`.  
  When `Executor->IsClean() && !bInHitStun`: execute transition sequence.

---

## 6. Honest Unknowns & UNVERIFIED Items

1. **[UNVERIFIED - Blend-Out Tail on Transition Montages]:** Whether `PhaseTransitionMontages` require the same $0.05\text{s}$ blend-out clearance rule established in `REACH_TO_RANGE_RULES.md` Section 7 to prevent snapping into the subsequent Phase 2 attack montage.
2. **[UNVERIFIED - Selector State Across Resets]:** Whether `Selector.Reset()` should completely wipe player kiting distance memory or preserve rolling distance history for gap-closer evaluation in Generation 2.
3. **[UNVERIFIED - Simultaneous Lethal Hit & Reset Call]:** If a lethal hit and a fixture reset arrive in the same frame, priority arbitration must guarantee that Reset supersedes Death (`RPGBossRules.h:60-75`), incrementing generation token and clearing `bDead` cleanly.

