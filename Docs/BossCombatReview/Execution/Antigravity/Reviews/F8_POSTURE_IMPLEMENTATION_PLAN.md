# Slice F8: Boss Posture and Stance Break Implementation Plan

**Document Version:** 1.0.0  
**Author:** Antigravity  
**Task Reference:** `[C-446]` (Lead Claude Order, 2026-10-31)  
**Status:** DELIVERED (Strict Offline Verification, Zero Source/Content/Config Edits, Pure CRLF)  
**Target Framework:** OneBossFight Sevarog Combat Framework (Slice F8 Posture / Stance Break Authority)

---

## 1. Executive Overview & Architecture Pattern

Slice F8 introduces authoritative Boss Posture and Stance Break mechanics to the Sevarog Combat Framework. In strict compliance with Tech Lead Claude's architectural mandate (`[C-446]`), this implementation mirrors the proven design pattern of Slice F6c (Phase Authority):
1. **Reuse Legacy Pure Rules Unchanged:** The pure priority resolution logic in `RPGBossRules::ResolveBreak` and `RPGBossRules::ResolveTransition` is reused directly without modification or wrapper drift.
2. **Framework Actor State Authority:** The framework character (`ARPGFrameworkBossCharacter`) natively owns its posture pool, stagger timers, cooldowns, and break latching, eliminating multi-component allocation overhead and pack Blueprint dependencies.
3. **Data-Driven Profile Contract:** All posture parameters (`PostureMax`, `PlayerPostureHitAmount`, `StaggerSeconds`, `PostureRegenDelaySeconds`, `PostureRegenRate`, `StaggerCooldownSeconds`) are authored in `URPGBossFrameworkProfile`, validated fail-closed at asset resolve time.
4. **Clean Mid-Attack Interruption:** When a stance break triggers while an attack montage is actively playing, the executor aborts cleanly via `URPGFrameworkMoveExecutor::Abort(TEXT("StanceBreak"))`, closing swept hit windows, stopping animation playback, and logging structured cleanup telemetry.
5. **Deterministic Multi-Generation PIE Verification:** Verified through automated PIE runs with explicit structured tokens (`[FrameworkProof] posture_drain`, `[FrameworkProof] stance_break`, `[FrameworkProof] stagger_recovery`), followed by automated log graders.

---

## 2. Legacy Authority: State, Thresholds, Regen & Cooldowns

### 2.1 Pure Rules Authority (`RPGBossRules.h`)
- **Priority Hierarchy:** Documented in `Source/OneBossFight/Player/RPGBossRules.h:8-10` per Master Design Freeze 21 (lines 889–905):
  $$\text{Dead (1)} > \text{Reset (2)} > \text{Phase Transition (3)} > \text{Accepted Riposte (4)} > \text{Stance Break (5)} > \text{Committed Attack (6)} > \text{Selection (7)}$$
- **State Flags:** `RPGBossRules::FFlags` (`RPGBossRules.h:14-22`):
  * `bDead`: Boss health $\le 0.0$.
  * `bDormant`: Boss dormant / encounter unstarted.
  * `bTransition`: Phase transition actively playing.
  * `bStaggered`: Boss currently down in stance break.
  * `bPhaseTwo`: Phase two already latched.
  * `bCooldown`: Stance break cooldown active.
- **Pure Stance Break Gate:** `RPGBossRules::ResolveBreak(const FFlags& F, bool bIgnoreCooldown)` (`RPGBossRules.h:60-68`):
  ```cpp
  if (F.bDead) { return EBreakResult::Dead; }
  if (F.bDormant) { return EBreakResult::Dormant; }
  if (F.bTransition) { return EBreakResult::Transition; }
  if (F.bStaggered) { return EBreakResult::AlreadyStaggered; }
  if (F.bCooldown && !bIgnoreCooldown) { return EBreakResult::Cooldown; }
  return EBreakResult::Started;
  ```
- **Pure Phase Transition Gate:** `RPGBossRules::ResolveTransition(...)` (`RPGBossRules.h:72-81`):
  * Returns `ETransitionResult::QueuedBehindStagger` when `F.bStaggered == true` (line 79). Stance break holds phase transition until the stagger concludes.

### 2.2 Legacy Component Responsibilities & Hardcoded vs Authored Values
- **`URPGBossPosture` (`Source/OneBossFight/Player/RPGBossPosture.h` & `.cpp`):**
  * Line 31: `PostureMax = 100.f` (Default design value).
  * Line 35: `RegenDelaySeconds = 6.f` (Seconds of idle time after last drain before regeneration begins).
  * Line 39: `RegenPerSecond = 13.f` (Regeneration rate).
  * Line 69: `ApplyPostureDamage(float Amount, const TCHAR* Source)`:
    - If `Hold != EHold::None` (during stance break or phase transition), posture drain is ignored (`EDrainResult::Held`, lines 77-83).
    - Clamped at zero: `Posture = FMath::Max(0.f, Posture - Amount);`.
    - If `Posture <= 0.f`: triggers `Stagger->RequestBreak(false)` (lines 92-104).
  * Line 80: `RefillAfterBreak()`: restores posture pool to `PostureMax` and restarts regen timer.
  * Line 97: `BeginHold(EHold Mode)`: holds pool at zero during stagger.
- **`URPGBossStagger` (`Source/OneBossFight/Player/RPGBossStagger.h` & `.cpp`):**
  * Line 36: `StaggerSeconds = 2.5f` (Down duration before get-up starts).
  * Line 44: `CriticalMultiplier = 2.5f` (Damage multiplier applied during critical window).
  * Line 134: `CooldownSeconds = 0.f` (Cooldown window post-stagger; 0 by default, Freeze 17.2).
  * Line 195 / Line 318: `RequestBreak(bool bIgnoreCooldown)`: queries `RPGBossRules::ResolveBreak`, dispatches `StartStagger()` on `EBreakResult::Started`.
  * Line 199 / Line 825: `AbortStagger()`: clears cooldown, cancels active montages, refills posture hold via `Posture->EndHold(true)`.

---

## 3. Posture Hit Intake for the Framework Boss

### 3.1 Live Hit Intake Plumbing
In `Source/OneBossFight/Player/RPGHitIntake.cpp:417-421`, player weapon contact delegates directly to the framework interface:
```cpp
// A boss with native health (the framework Sevarog) takes the hit directly: no pack damage execution, record, scaler or posture runs for it.
if (IRPGNativeBossHealth* Native = Cast<IRPGNativeBossHealth>(Target))
{
    Native->ApplyPlayerHit(1.0);
    return;
}
```
In `Source/OneBossFight/Player/RPGHitIntake.cpp:398-411`:
```cpp
void URPGHitIntake::InjectBossHitForTest(AActor* Boss)
{
    ...
    HandlePackHit(FHitResult(Boss, nullptr, Boss->GetActorLocation(), FVector::UpVector));
    ...
}
```

### 3.2 Framework Posture Hit Processing
- When `IRPGNativeBossHealth::ApplyPlayerHit(double Multiplier)` is invoked:
  * Health loss is calculated and applied: `Loss = FMath::Min(Health, double(P.PlayerHitDamage) * Multiplier); Health -= Loss;`
  * If `Health <= 0.0`: `Die()` is triggered immediately. Dead outranks stance break (Freeze 21).
  * If the boss remains alive (`Health > 0.0`) and posture is enabled (`PostureMax > 0.f`):
    - If `bStaggered == true`: Posture damage is ignored/held (`[FrameworkProof] posture_held reason=StaggerActive`).
    - If `bStaggered == false`: Posture damage is deducted:
      $$\text{Drain} = \min(\text{Posture}, \text{double}(\text{Profile}\to\text{PlayerPostureHitAmount}) \times \text{Multiplier})$$
      $$\text{Posture} = \max(0.0, \text{Posture} - \text{Drain})$$
      $$\text{LastPostureDrainTime} = \text{WorldTimeSeconds}$$
      `UE_LOG(LogTemp, Display, TEXT("[FrameworkProof] posture_drain damage=%g amount=%g postureBefore=%g postureAfter=%g max=%g"), Loss, Drain, BeforePosture, Posture, MaxPosture);`
    - If $\text{Posture} \le 0.0$:
      The boss evaluates `RPGBossRules::ResolveBreak`. If `Started`, triggers `StartStagger(P.StaggerSeconds)`.

---

## 4. Exact Framework Hooks & Execution Interruption

### 4.1 State Variables (`RPGFrameworkBossCharacter.h`)
```cpp
// Posture & Stance Break Authority (Slice F8)
double Posture = 0., MaxPosture = 0.;
bool bStaggered = false;
double StaggerStartedAt = 0.;
double StaggerDuration = 0.;
double LastPostureDrainTime = 0.;
double StaggerCooldownEnd = 0.;
bool bQueuedPhaseTransition = false;
```

### 4.2 Interruption of Active Attack (`RPGFrameworkMoveExecutor.cpp:207-215`)
When `StartStagger` fires while an attack is in progress (`bStartedMove == true`):
1. The boss immediately invokes:
   ```cpp
   Executor->Abort(TEXT("StanceBreak"));
   bStartedMove = false;
   ```
2. In `URPGFrameworkMoveExecutor::Abort(const FString& Reason)` (`RPGFrameworkMoveExecutor.cpp:207-215`):
   * `Model_.Abort(Token, Events, Error);` cleans up the move model, closing active hit windows.
   * `StopOwned(0.f);` halts active montage playback on the skeletal mesh without delay.
   * `OwnedMontage = nullptr; SetComponentTickEnabled(false);`
   * Emits structured cleanup:
     `[FrameworkProof] cleanup reason=StanceBreak modelIdle=1 ownedMontageStopped=1`
3. Movement is halted:
   ```cpp
   if (auto* AI = Cast<ARPGFrameworkBossController>(GetController())) AI->StopOwnedWalk();
   GetCharacterMovement()->StopMovementImmediately();
   ```
4. Telemetry emitted:
   `[FrameworkProof] stance_break duration=%g generation=%llu state=%s` (`state=MidAttack` or `state=Neutral`).

### 4.3 Tick Gating (`RPGFrameworkBossCharacter.cpp:81-149`)
In `ARPGFrameworkBossCharacter::Tick(float Delta)`:
1. **Active Stagger Update:**
   ```cpp
   if (bStaggered)
   {
       const double Now = GetWorld()->GetTimeSeconds();
       const double Elapsed = Now - StaggerStartedAt;
       if (Elapsed < StaggerDuration)
       {
           // Boss remains down; all attack selection and walking are bypassed.
           return;
       }
       // Stagger duration elapsed -> End Stagger
       bStaggered = false;
       Posture = MaxPosture; // Full refill on recovery (Freeze 714)
       StaggerCooldownEnd = Now + P.StaggerCooldownSeconds;
       UE_LOG(LogTemp, Display, TEXT("[FrameworkProof] stagger_recovery duration=%g postureRefilled=%g cooldown=%g"), Elapsed, Posture, P.StaggerCooldownSeconds);
       
       // Process phase transition queued during stagger
       if (bQueuedPhaseTransition || (bHittable && P.PhaseTwoFraction > 0.f && !bPhaseTwoLatched && (Health / MaxHealth <= P.PhaseTwoFraction)))
       {
           bPhaseTwoLatched = true;
           UE_LOG(LogTemp, Display, TEXT("[FrameworkProof] phase_transition attack=%d from=%s to=%s health=%g max=%g fraction=%g reason=QueuedBehindStagger"),
               AttacksDone + 1, *CurrentPhaseId.ToString(), *P.PhaseTwoId.ToString(), Health, MaxHealth, double(P.PhaseTwoFraction));
           CurrentPhaseId = P.PhaseTwoId;
           bQueuedPhaseTransition = false;
       }
       return; // Transition tick completed; resume neutral selection next tick
   }
   ```
2. **Posture Regeneration (when NOT staggered and NOT dead):**
   ```cpp
   if (Posture < MaxPosture && (GetWorld()->GetTimeSeconds() - LastPostureDrainTime > P.PostureRegenDelaySeconds))
   {
       const double RegenStep = double(P.PostureRegenRate) * Delta;
       Posture = FMath::Min(MaxPosture, Posture + RegenStep);
   }
   ```
3. **Phase Gate with Stagger Awareness:**
   If HP crosses below `PhaseTwoFraction` while `bStaggered == true`:
   `RPGBossRules::ResolveTransition` returns `ETransitionResult::QueuedBehindStagger`.
   The boss sets `bQueuedPhaseTransition = true;` and defers execution until `stagger_recovery`.

### 4.4 Encounter Restart & Death Hooks
- **`Die()` (`RPGFrameworkBossCharacter.cpp:178-188`):**
  * If `bStaggered == true`: `bStaggered = false;` (death supersedes stagger).
  * Executor aborts with `BossDead`, encounter terminates.
- **`RestartEncounter(NewGeneration)` (`RPGFrameworkBossCharacter.cpp:159-177`):**
  * Line 167: If `MaxPosture > 0.f`, resets `Posture = MaxPosture;`.
  * Resets `bStaggered = false; StaggerStartedAt = 0.; StaggerCooldownEnd = 0.; bQueuedPhaseTransition = false;`.
  * Line 174: Telemetry appends `bossPosture=%g`:
    `[FrameworkProof] encounter_reset generation=%llu oldState=%s executorRearmed=1 bossHealth=%g bossPosture=%g targetHealth=%g`

---

## 5. Profile Schema & Validation Contracts

### 5.1 Profile Struct Additions (`RPGBossFrameworkProfile.h`)
```cpp
// Posture & Stance Break (Slice F8)
UPROPERTY(EditAnywhere) float PostureMax = 0.f;
UPROPERTY(EditAnywhere) float PlayerPostureHitAmount = 0.f;
UPROPERTY(EditAnywhere) float StaggerSeconds = 0.f;
UPROPERTY(EditAnywhere) float PostureRegenDelaySeconds = 0.f;
UPROPERTY(EditAnywhere) float PostureRegenRate = 0.f;
UPROPERTY(EditAnywhere) float StaggerCooldownSeconds = 0.f;
```

### 5.2 Fail-Closed Validation Rules (`RPGBossFrameworkProfile.cpp`)
1. **Domain Checking (`Framework.Profile.Domain`):**
   * If `PostureMax > 0.f`:
     - `PostureMax` must be finite and $\le 1.0\times 10^6$.
     - `PlayerPostureHitAmount` must be $> 0.f$ and $\le \text{PostureMax}$.
     - `StaggerSeconds` must be $\ge 0.5f$ and $\le 100.f$.
     - `PostureRegenDelaySeconds` must be $\ge 0.f$ and $\le 1000.f$.
     - `PostureRegenRate` must be $\ge 0.f$ and $\le 1000.f$.
     - `StaggerCooldownSeconds` must be $\ge 0.f$ and $\le 1000.f$.
2. **Coupling Validation (`Framework.Profile.PostureCoupling`):**
   * If `PostureMax > 0.f`, the boss must be hittable (`BossMaxHealth > 0.f && PlayerHitDamage > 0.f`). An unhittable boss cannot author a posture pool.
3. **Opt-Out Zero State:**
   * If `PostureMax == 0.f`: all posture fields must be `0.f`, preserving full backward compatibility with F3b-F7 profiles.

---

## 6. Priority Hierarchy & State Interaction Matrix

| Current State | Incoming Event | Priority Check | Resolved Behavior |
|:---|:---|:---|:---|
| **Neutral** | Hit (Posture $\to 0$) | Stance Break vs Neutral | Enters `StaggerDown`. Montage playback deferred. `stance_break ... state=Neutral`. |
| **Attack Playing** | Hit (Posture $\to 0$) | Stance Break vs Attack | Executor aborts immediately (`Abort(StanceBreak)`). Hit windows closed. `stance_break ... state=MidAttack`. |
| **StaggerDown** | Hit (Damage taken) | Stagger Hold Active | Posture drain ignored (`posture_held`). Health damage applied normally. |
| **StaggerDown** | HP crosses Phase Fraction | `ResolveTransition` $\to$ `QueuedBehindStagger` | Stagger NOT interrupted. Phase transition latches and fires immediately upon `stagger_recovery`. |
| **StaggerDown** | Lethal Hit (HP $\to 0$) | `ResolveBreak` $\to$ `Dead` (Priority 1) | Stagger terminated immediately. `Die()` executes. `boss_dead` emitted. |
| **StaggerDown** | RestartEncounter | Reset (Priority 2) | Stagger cancelled. Posture refilled to `PostureMax`. Gen 2 restarts clean. |
| **StaggerRecovery** | Cooldown Active | `ResolveBreak` $\to$ `Cooldown` | If hits arrive within `StaggerCooldownSeconds`, break request dropped with reason `cooldown`. |

---

## 7. PIE Proof Test Cases & Verification Telemetry

### 7.1 Proposed Telemetry Token Specification
- `[FrameworkProof] posture_drain damage=%g amount=%g postureBefore=%g postureAfter=%g max=%g`
- `[FrameworkProof] posture_held reason=%s`
- `[FrameworkProof] stance_break duration=%g generation=%llu state=%s`
- `[FrameworkProof] stagger_recovery duration=%g postureRefilled=%g cooldown=%g`
- `[FrameworkProof] RESULT outcome=CompletedWithStagger acceptedHits=%d attacks=%d staggers=%d`

### 7.2 Six Core PIE Test Cases
1. **Case 1: Neutral Stance Break:**
   - In neutral band, fixture injects hits draining posture to 0.
   - Asserts `[FrameworkProof] stance_break duration=2.5 generation=1 state=Neutral`.
   - Asserts boss stays down for 2.5s, recovers, and emits `[FrameworkProof] stagger_recovery duration=2.5 postureRefilled=100`.
2. **Case 2: Mid-Attack Stance Break Interruption:**
   - Boss begins `playback_start instance=1`. Fixture injects hit at $t = 0.5\text{ s}$ draining posture to 0.
   - Asserts `[FrameworkProof] cleanup reason=StanceBreak modelIdle=1 ownedMontageStopped=1`.
   - Asserts active attack terminates cleanly and boss transitions to stagger.
3. **Case 3: Posture Idle Regeneration:**
   - Fixture injects 1 hit draining 34 points (Posture becomes 66).
   - Fixture waits for duration $> \text{PostureRegenDelaySeconds}$ without hitting.
   - Asserts posture refilled back to 100 via periodic telemetry without triggering a break.
4. **Case 4: Phase Transition Queued Behind Stagger:**
   - Phased profile (`PhaseTwoFraction = 0.50`). Hit 1 triggers stance break.
   - Hit 2 during stagger reduces health below 50%.
   - Asserts transition does NOT interrupt stagger (`QueuedBehindStagger`).
   - Asserts `phase_transition` fires immediately upon `stagger_recovery`.
5. **Case 5: Lethal Hit Preempts Stance Break:**
   - Boss at 20 HP, 20 Posture.
   - Lethal hit (40 damage, 40 posture) lands.
   - Asserts `boss_dead` fires immediately; `stance_break` is never emitted.
6. **Case 6: Multi-Generation Encounter Reset:**
   - Encounter restarted via `RestartEncounterForTest(2)` while boss is staggered.
   - Asserts `encounter_reset generation=2 ... bossPosture=100`, stagger state cleared, Gen 2 clean.

---

## 8. Explicit Verification Boundaries & Offline Limits

The following items cannot be formally certified in an offline, read-only analysis and are designated for Lead Claude's engine implementation phase:
1. **Visual Montage Playback Quality:** Live blend times and visual pose fidelity of mannequin/Sevarog knockdown and get-up montages without running an active engine render viewport.
2. **Synchronized Frontal Riposte System:** Paired player/boss synchronized execution clips (`AN_Riposte_Player_Front` and `AN_Riposte_Boss_Reaction`) belong to a subsequent Combat/Riposte slice and are explicitly excluded from core F8 posture authority.
3. **Pack Ability System Poise Reflection:** Direct reflection writes to `BP_PoiseExtendedAttribute_C` remain pack-specific; framework Sevarog relies entirely on native C++ posture authority.

---
*Authored by Antigravity under Lead Order `[C-446]`. Validated offline with pure unit tests.*
