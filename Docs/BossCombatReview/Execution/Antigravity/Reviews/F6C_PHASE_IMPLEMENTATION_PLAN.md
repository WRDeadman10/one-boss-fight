# F6c Phase Authority Implementation Plan (Order A-314)

**Document ID**: `F6C_PHASE_IMPLEMENTATION_PLAN.md`  
**Author**: Antigravity  
**Lead Order**: `[C-428]` / A-314  
**Context**: Phase transition authority, neutral gate integration, and MoveCard phase partitioning  
**Status**: APPROVED IMPLEMENTATION PLAN  

---

## 1. Executive Summary

This document specifies the exact C++ architecture for **F6c (Phase Authority & Transition Execution)**, building on `F6B_RESET_AND_PHASE_DATA_DESIGN.md`. It resolves the 4 core design questions posed by Lead Claude in `[C-428]`:

1. **Existing Transition Authority**: Which class holds the legacy threshold rule?  
   `RPGBossRules` in `Source/OneBossFight/Player/RPGBossRules.h:12-82`.
2. **Reusability & Purity**: Can the framework reuse it unchanged?  
   **YES**. `RPGBossRules::ResolveTransition` (`RPGBossRules.h:72-81`) is 100% pure, header-only, stateless, and has zero engine/UObject dependencies.
3. **Neutral-Only Gate & Tick Wiring**: How does it hook into `RPGFrameworkBossCharacter::Tick`?  
   Directly inside the neutral attack-decision block (`RPGFrameworkBossCharacter.cpp:85-108`) before populating `FRPGBossDecisionSnapshot::PhaseId` (currently hardcoded at line 89).
4. **Card Data & Selector Partitioning**: What data does a card need to belong to a phase?  
   `FRPGBossMoveCardSpec::PhaseId` (`RPGBossMoveCard.h:48`), already populated from JSON. `RPGBossMoveModel::IsEligible` (`RPGBossMoveModel.cpp:30`) already enforces `S.PhaseId == Card->Spec().PhaseId` and rejects mismatched cards with `MoveModel.Phase`.

---

## 2. Legacy Transition Authority: `RPGBossRules.h`

### 2.1 File Location & Declaration
- **Header**: `Source/OneBossFight/Player/RPGBossRules.h`
- **Namespace**: `RPGBossRules` (`RPGBossRules.h:12`)
- **Flags Struct**: `RPGBossRules::FFlags` (`RPGBossRules.h:14-22`)
  ```cpp
  struct FFlags
  {
      bool bDead = false;
      bool bDormant = false;
      bool bTransition = false;
      bool bStaggered = false;
      bool bPhaseTwo = false;
      bool bCooldown = false;
  };
  ```
- **Transition Result Enum**: `RPGBossRules::ETransitionResult` (`RPGBossRules.h:28`)
  ```cpp
  enum class ETransitionResult : uint8 {
      Start,
      NotReady,
      Dead,
      Dormant,
      AlreadyDone,
      AboveThreshold,
      QueuedBehindStagger
  };
  ```

### 2.2 Threshold Function Signature & Exact Semantics
- **Function**: `RPGBossRules::ResolveTransition` (`RPGBossRules.h:72-81`):
  ```cpp
  inline ETransitionResult ResolveTransition(const FFlags& F, double Health, double Max, float Fraction)
  {
      if (Max <= 0.0) { return ETransitionResult::NotReady; }
      if (Health <= 0.0 || F.bDead) { return ETransitionResult::Dead; }
      if (F.bDormant) { return ETransitionResult::Dormant; }
      if (F.bPhaseTwo) { return ETransitionResult::AlreadyDone; }
      if (Health / Max > Fraction) { return ETransitionResult::AboveThreshold; }
      if (F.bStaggered) { return ETransitionResult::QueuedBehindStagger; }
      return ETransitionResult::Start;
  }
  ```

### 2.3 Evaluation of Framework Reusability
- **Purity**: Zero side effects, zero heap allocations, zero virtual dispatches, completely `inline`.
- **Order of Evaluation**:
  1. `Max <= 0.0` -> `NotReady`
  2. `Health <= 0.0 || bDead` -> `Dead` (lethal hit takes precedence over phase transition)
  3. `bDormant` -> `Dormant`
  4. `bPhaseTwo` -> `AlreadyDone` (strictly idempotent: cannot re-trigger Phase 2 once started)
  5. `Health / Max > Fraction` -> `AboveThreshold` (boss remains in Phase 1)
  6. `bStaggered` -> `QueuedBehindStagger` (respects stance break priority; transition waits until recovery)
  7. Final return -> `Start` (transition commences!)
- **Verdict**: The framework reuses `RPGBossRules::ResolveTransition` **completely unchanged**.

---

## 3. Neutral-Only Gate Integration in `RPGFrameworkBossCharacter.cpp`

### 3.1 Current Architecture (`RPGFrameworkBossCharacter.cpp:79-115`)
In the current implementation:
- Boss walks to the combat band: `if (!bArrived && ...)` (line 84).
- When arrived, boss enters neutral state: `if (bArrived && !bStartedMove)` (line 85).
- Currently, line 89 hardcodes Phase 1:
  ```cpp
  S.PhaseId = Dependencies->FirstCard()->Spec().PhaseId; // Line 89
  ```
- Between consecutive attacks (lines 109-115):
  ```cpp
  if (bStartedMove && Executor->DidFinish() && Executor->IsClean() && Dependencies->Candidates.Num() > 0 && AttacksDone + 1 < Dependencies->Profile->AttackCount)
  {
      ++AttacksDone;
      if (!Executor->PrepareNextAttack()) { Fail(TEXT("Framework.Playback.NextAttack")); return; }
      bStartedMove = false; // Re-enters neutral on next tick!
      return;
  }
  ```

### 3.2 F6c Neutral Gate Hook
Because `bStartedMove == false` is only true when the boss is in neutral (either initial arrival or after an attack finishes cleanly), this block is **already** the exact neutral gate!

In F6c, `ARPGFrameworkBossCharacter` maintains authoritative phase state:
```cpp
// On ARPGFrameworkBossCharacter (RPGFrameworkBossCharacter.h):
FName CurrentPhaseId = FName(TEXT("Phase_1"));
bool bPhaseTwoStarted = false;
```

Inside `ARPGFrameworkBossCharacter::Tick` (at line 85, replacing line 89):
```cpp
    if (bArrived && !bStartedMove)
    {
        // --- F6c: Authoritative Phase Transition Check ---
        RPGBossRules::FFlags F;
        F.bDead = bDead;
        F.bDormant = false;
        F.bPhaseTwo = bPhaseTwoStarted;
        F.bStaggered = false; // or Executor->IsStaggered()

        const float PhaseThreshold = Dependencies->Profile->PhaseTwoFraction; // e.g. 0.6f
        const RPGBossRules::ETransitionResult Trans = RPGBossRules::ResolveTransition(F, Health, MaxHealth, PhaseThreshold);

        if (Trans == RPGBossRules::ETransitionResult::Start)
        {
            bPhaseTwoStarted = true;
            CurrentPhaseId = FName(TEXT("Phase_2"));
            UE_LOG(LogTemp, Display, TEXT("[FrameworkProof] phase transition started to %s at HP=%g/%g (frac=%g)"),
                *CurrentPhaseId.ToString(), Health, MaxHealth, Health / MaxHealth);

            // Optional: If PhaseTransitionCard is authored, execute transition montage;
            // Otherwise, immediately switch phase authority.
        }

        const FVector D = Target->GetActorLocation() - GetActorLocation();
        FRPGBossDecisionSnapshot S;
        S.EncounterId = EncounterId;
        S.Generation = GenerationId;
        S.TargetId = uint64(Target->GetUniqueID());
        S.FrameId = GFrameCounter;
        S.PhaseId = CurrentPhaseId; // <--- Dynamically wired to authoritative phase!
        S.ClockSeconds = GetWorld()->GetTimeSeconds();
        S.RangeCm = D.Size2D();
        S.SignedYawDegrees = FMath::FindDeltaAngleDegrees(GetActorRotation().Yaw, D.Rotation().Yaw);
        S.bTargetValid = S.bNeutral = true;
```

### 3.3 Encounter Reset Behavior (`RestartEncounter`)
In `RPGFrameworkBossCharacter.cpp:144-162`:
When `RestartEncounter(NewGeneration, Error)` is invoked:
- `CurrentPhaseId = FName(TEXT("Phase_1"));`
- `bPhaseTwoStarted = false;`
- `Health = MaxHealth;`
- `AttacksDone = 0;`
- `bStartedMove = false;`
- `Selector.Reset();`
Phase authority resets cleanly back to Phase 1 generation invariants.

---

## 4. Card Data & MoveModel Phase Partitioning

### 4.1 Card Specification Data
On `URPGBossMoveCard` (`Source/OneBossFight/Player/RPGBossMoveCard.h:48`):
```cpp
struct FRPGBossMoveCardSpec
{
    ...
    UPROPERTY(EditAnywhere) FName PhaseId; // Line 48
    ...
};
```
Every card carries `PhaseId`. In JSON authoring:
- Phase 1 Cards: `"PhaseId": "Phase_1"`
- Phase 2 Cards: `"PhaseId": "Phase_2"`

### 4.2 MoveModel Eligibility Check (`RPGBossMoveModel.cpp:30`)
When `Selector.Select(Executor->Model(), S, Decision)` iterates candidate cards (`RPGBossMoveSelector.cpp:35-52`), it evaluates `Model.IsEligible(C.Card, S, Error)`.

In `Source/OneBossFight/Player/RPGBossMoveModel.cpp:30`:
```cpp
if (S.PhaseId != Card->Spec().PhaseId) return Refuse(Error, TEXT("MoveModel.Phase"));
```
- When `S.PhaseId == Phase_1`: Any candidate with `PhaseId == Phase_2` is rejected with `MoveModel.Phase`.
- When `S.PhaseId == Phase_2`: Any candidate with `PhaseId == Phase_1` is rejected with `MoveModel.Phase`.
- Selector trace (`Decision.Traces`) logs:
  `[FrameworkProof] refusal attack=2 card=Move_Sevarog_SwingSlow_F7 reason=MoveModel.Phase`

Zero new C++ filtering code is needed in `RPGBossMoveSelector` or `RPGBossMoveModel`. The existing architecture handles phase filtering out of the box!

---

## 5. Summary of C++ Changes for F6c Implementation

1. **`RPGBossFrameworkProfile.h`**:
   - Add `UPROPERTY(EditAnywhere) float PhaseTwoFraction = 0.6f;` (default 60% HP).
2. **`RPGFrameworkBossCharacter.h`**:
   - Add `FName CurrentPhaseId = FName(TEXT("Phase_1"));`
   - Add `bool bPhaseTwoStarted = false;`
3. **`RPGFrameworkBossCharacter.cpp`**:
   - Include `#include "Player/RPGBossRules.h"`.
   - At line 85 (`if (bArrived && !bStartedMove)`), call `RPGBossRules::ResolveTransition`.
   - At line 89, set `S.PhaseId = CurrentPhaseId;`.
   - In `RestartEncounter` (line 144), reset `CurrentPhaseId = FName(TEXT("Phase_1")); bPhaseTwoStarted = false;`.
4. **Runtime Verification**:
   - Verify with 2 Phase 1 cards and 2 Phase 2 cards.
   - Assert that crossing below 60% HP switches `S.PhaseId` to `Phase_2` in the next neutral window, and only Phase 2 cards are selected.
