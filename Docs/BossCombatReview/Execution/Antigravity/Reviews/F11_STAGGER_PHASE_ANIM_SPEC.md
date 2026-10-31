# F11 Specification: Boss Stance Break Stagger & Phase 2 Transition Animations

> **Status:** REVIEW DRAFT v3 (Offline specification for Lead Claude review per [C-517], [C-519], [C-520])  
> **Authority:** Owner Decision 3 (Option B: Reuse existing animations on boss skeleton, [C-515] / [C-516] / [C-517] / [C-519] / [C-520])  
> **Applicability:** `URPGBossFrameworkProfile`, `ARPGFrameworkBossCharacter`, `URPGFrameworkMoveExecutor`, `RPGFramework` runtime module  

---

## 1. Executive Summary & Verified Repository Citations

This specification defines the runtime data contracts, dual-layer validation architecture (pure unit-testable rules vs engine asset checks), state machine transitions, duration contracts, edge-case interleavings, unit test matrix, and PIE proof criteria for **Slice F11** (Boss Stance Break Stagger & Phase 2 Transition Animations).

Under Owner Decision 3 ([C-515] / [C-516] / [C-519] / [C-520]), the boss visual presentation transitions from the logic-only freeze-in-place placeholder to reusing existing skeletal animations native to the Paragon Sevarog skeleton (`Content/ParagonSevarog/Characters/Heroes/Sevarog/Animations/`):
- **Stagger Sequence:** `Stun_Start` -> `Stun_Loop` -> `Stun_End` (all native `UAnimSequence` assets).
- **Phase 2 Transition:** Authored transition sequence candidate (`Ultimate_Targeting`, `Soul_Siphon`, `Subjugation`, or `LevelStart_Montage`).
- **Death Authority:** Lethal hits remain governed by Slice F6a death authority (boss character destroyed); death animation is out of scope for F11.

### Verified Repository Citations:
1. `Documentation/DECISIONS.md:1258` (F8 C448):
   "No stagger animation yet (the boss freezes in place): known limit."
2. `Source/OneBossFight/Player/RPGBossFrameworkProfile.h:56-60`:
   `UPROPERTY(EditAnywhere) float PostureMax=0.f;`  
   `UPROPERTY(EditAnywhere) float PlayerPostureHitAmount=0.f;`  
   `UPROPERTY(EditAnywhere) float StaggerSeconds=0.f;`  
   `UPROPERTY(EditAnywhere) float PostureRegenDelaySeconds=0.f;`  
   `UPROPERTY(EditAnywhere) float PostureRegenPerSecond=0.f;`
3. `Source/OneBossFight/Player/RPGBossFrameworkProfile.h:52-53`:
   `UPROPERTY(EditAnywhere) float PhaseTwoFraction=0.f;`  
   `UPROPERTY(EditAnywhere) FName PhaseTwoId;`
4. `Source/OneBossFight/Boss/RPGFrameworkBossCharacter.h:57`:
   `double Posture=0., LastPostureDrain=-1., StaggerEndsAt=0.; bool bStaggered=false, bStaggerAbortedAttack=false;`
5. `Source/OneBossFight/Boss/RPGFrameworkBossCharacter.cpp:82-132` (`ARPGFrameworkBossCharacter::Tick`):
   Stagger active check in `Tick()` (lines 93-103): suppresses movement (`StopMovementImmediately()`), suppresses selector, evaluates `StaggerEndsAt`.
6. `Source/OneBossFight/Boss/RPGFrameworkBossCharacter.cpp:106-116` (`ARPGFrameworkBossCharacter::Tick`):
   Phase 2 evaluation gate at neutral decision point (`bArrived && !bStartedMove && !bStaggered`) via `RPGBossRules::ResolveTransition`.
7. `Source/OneBossFight/Boss/RPGFrameworkBossCharacter.cpp:217-226` (`ARPGFrameworkBossCharacter::StartStagger`):
   Stance break handling: stops walk, aborts running attack via `Executor->Abort(TEXT("StanceBreak"))`, arms `StaggerEndsAt`.
8. `Source/OneBossFight/Boss/RPGFrameworkBossCharacter.cpp:227-241` (`ARPGFrameworkBossCharacter::EndStagger`):
   Stagger recovery: calls `RecoverAfterAbort()`, refills posture to `PostureMax`, re-issues `WalkToBand()` if `!bArrived`.
9. `Source/OneBossFight/Boss/RPGFrameworkMoveExecutor.cpp:94`:
   Dynamic montage playback:  
   `OwnedMontage=Anim->PlaySlotAnimationAsDynamicMontage(Sequence,Card->Spec().SlotName,Profile->BlendInSeconds,Profile->BlendOutSeconds,Card->Spec().PlayRate,1,-1.f,0.f);`
10. `Source/OneBossFight/Boss/RPGFrameworkMoveExecutor.cpp:34`:
    Anim slot node verification:  
    `if (!IsValid(Instance)||Instance->GetClass()!=D.AnimClass.Get()||!RPGFramework::HasSlotNode(Instance,First->Spec().SlotName))`

---

## 2. Profile Field Names, Types & Slot Routing

In `Source/OneBossFight/Player/RPGBossFrameworkProfile.h`, four optional animation sequence soft object references and one slot configuration property are added to `URPGBossFrameworkProfile`:

```cpp
/** F11 Stance break / stagger animation sequences (optional, soft references).
 *  When unset, preserves F8 logic-only freeze-in-place behavior byte-identical.
 *  When set, plays Start on break, loops Loop during the middle window, and plays End to finish with StaggerSeconds. */
UPROPERTY(EditAnywhere, Category="Framework|Animation")
TSoftObjectPtr<UAnimSequence> StaggerStartAnim;

UPROPERTY(EditAnywhere, Category="Framework|Animation")
TSoftObjectPtr<UAnimSequence> StaggerLoopAnim;

UPROPERTY(EditAnywhere, Category="Framework|Animation")
TSoftObjectPtr<UAnimSequence> StaggerEndAnim;

/** F11 Phase 2 transition sequence (optional, soft reference).
 *  When set, played once when the neutral gate latches PhaseTwoId; holds selector for its duration. */
UPROPERTY(EditAnywhere, Category="Framework|Animation")
TSoftObjectPtr<UAnimSequence> PhaseTransitionAnim;

/** F11 Anim slot name for dynamic montage playback (default: FullBody).
 *  Default matches the combat cards' SlotName and the boss AnimBP slot.
 *  Validated non-empty when any F11 animation sequence is set. */
UPROPERTY(EditAnywhere, Category="Framework|Animation")
FName AnimSlotName = TEXT("FullBody");
```

### Execution Architecture:
All clips on the Paragon Sevarog skeleton are native `UAnimSequence` assets. Dynamic playback leverages the proven runtime path in `RPGFrameworkMoveExecutor.cpp:94`:
```cpp
AnimInstance->PlaySlotAnimationAsDynamicMontage(
    Sequence,
    Profile->AnimSlotName,
    Profile->BlendInSeconds,
    Profile->BlendOutSeconds,
    PlayRate,
    LoopCount,
    -1.f,
    0.f
);
```

Slot verification in `RPGFramework::ResolveDependencies` verifies that `Profile->AnimSlotName` exists as a slot node in the boss AnimInstance via `RPGFramework::HasSlotNode(AnimInstance, Profile->AnimSlotName)`, logging:
`[FrameworkProof] slot_graph name=FullBody nodeClass=AnimNode_Slot verified=1 label=<ProfileLabel>`

---

## 3. Dual-Layer Validation Architecture (Pure vs Engine)

To allow Lead Claude to unit-test all validation rules in `RPGFrameworkRuntimeTests.cpp` without requiring Unreal engine asset loading or disk files, validation is partitioned into two clear layers:

### 3.1 Layer 1: Pure Structural & Mathematical Validator (Unit-Testable in C++)
Operates entirely on plain values (floats and FNames) passed via a plain parameter struct:

```cpp
struct FRPGBossStaggerAnimPureParams
{
    float StartLength = 0.f;
    float LoopLength = 0.f;
    float EndLength = 0.f;
    float StaggerSeconds = 0.f;
    FName StartSkeleton;
    FName LoopSkeleton;
    FName EndSkeleton;
    FName ExpectedSkeleton;
    FName AnimSlotName = TEXT("FullBody");
    bool bHasSlotNode = true;

    // Phase transition properties:
    float PhaseTransitionLength = 0.f;
    FName PhaseTransitionSkeleton;
    float PhaseTwoFraction = 0.f;
    FName PhaseTwoId;
};

bool ValidateStaggerAnimPure(const FRPGBossStaggerAnimPureParams& P, FString& OutError);
```

Pure Fail-Closed Rules:
1. **Triplet Coherence:** Stagger clips must be configured as a complete triplet. Either all three lengths are positive (`StartLength > 0 && LoopLength > 0 && EndLength > 0`), or all three are zero.  
   Token: `Framework.Profile.StaggerAnim.CoherentSet`
2. **Skeleton Match:** If stagger clips are set, each clip's skeleton must equal `ExpectedSkeleton` (`StartSkeleton == ExpectedSkeleton`, etc.).  
   Token: `Framework.Profile.StaggerAnim.SkeletonMismatch`
3. **Duration Budget (`TooShort`):** The total stagger time must accommodate entry and exit clips: `StartLength + EndLength <= StaggerSeconds`.  
   Token: `Framework.Profile.StaggerAnim.TooShort`
4. **Loop Length Validity:** If middle window `(StaggerSeconds - StartLength - EndLength) > 0`, requires `LoopLength > 0`.  
   Token: `Framework.Profile.StaggerAnim.InvalidLoopLength`
5. **Slot Name Non-Empty:** If any stagger or phase animation is set, requires `!AnimSlotName.IsNone()`.  
   Token: `Framework.Profile.StaggerAnim.SlotNameEmpty`
6. **Slot Node Existence:** If any stagger or phase animation is set, requires `bHasSlotNode == true`.  
   Token: `Framework.Profile.StaggerAnim.SlotNotFound`
7. **Phase Transition Skeleton:** If `PhaseTransitionLength > 0`, requires `PhaseTransitionSkeleton == ExpectedSkeleton`.  
   Token: `Framework.Profile.PhaseTransitionAnim.SkeletonMismatch`
8. **Phase Transition Phaseless Check:** If `PhaseTransitionLength > 0`, requires `PhaseTwoFraction > 0.0f` and `!PhaseTwoId.IsNone()`.  
   Token: `Framework.Profile.PhaseTransitionAnim.Phaseless`

### 3.2 Layer 2: Engine Asset Resolution (Editor & Preflight)
Runs in editor commandlets, Python preflight (`validate_boss_config.py`), and `RPGFramework::ResolveProfile`:
- Soft path resolution: checks whether each configured soft object pointer resolves to an existing `UAnimSequence` on disk.
- Tokens: `Framework.Profile.StaggerAnim.StartLoad`, `Framework.Profile.StaggerAnim.LoopLoad`, `Framework.Profile.StaggerAnim.EndLoad`, `Framework.Profile.PhaseTransitionAnim.Load`.
- When resolved, extracts `SequenceLength` and `Skeleton->GetFName()`, passing them to Layer 1 `ValidateStaggerAnimPure`.

---

## 4. Duration Contract & Pure State Machine

### 4.1 Duration Contract (Deterministic Time-Based Evaluation)
`StaggerSeconds` remains the authoritative **TOTAL** stagger duration, preserving existing F8 proof timing byte-identical.
To eliminate timing drift from engine tick jitter and montage blend curves, the stagger state machine has **zero dependency on `OnMontageEnded` events**. The current stagger sub-state is evaluated as a pure, deterministic function of elapsed time:

```
dt = now - staggerStart
middleDuration = StaggerSeconds - StartLength - EndLength
endStart = StaggerSeconds - EndLength
LoopCount = ceil(middleDuration / LoopLength)
```

The sub-state `S(dt)` is defined over `dt`:
- `0.0 <= dt < StartLength`: State = **Start**. Play `StaggerStartAnim` (one-shot, dynamic montage).
- `StartLength <= dt < endStart`: State = **Loop**. Play `StaggerLoopAnim` (dynamic montage with `LoopCount = ceil(middleDuration / LoopLength)`).
- `endStart <= dt < StaggerSeconds`: State = **End**. At `dt == endStart`, stop loop montage with `BlendOut`; play `StaggerEndAnim` (one-shot, dynamic montage).
- `dt >= StaggerSeconds`: State = **Finished**. Execute `EndStagger()`, refill posture to `PostureMax`, and resume neutral decision gate.

### 4.2 Hand-Calculated Timeline Example
Parameters:
- `StartLength = 0.8 s`
- `LoopLength = 0.5 s`
- `EndLength = 0.6 s`
- `StaggerSeconds = 3.0 s`

Calculations:
- `middleDuration = 3.0 - 0.8 - 0.6 = 1.6 s`
- `endStart = 3.0 - 0.6 = 2.4 s`
- `LoopCount = ceil(1.6 / 0.5) = ceil(3.2) = 4`

Timeline:
- `t = 0.00 s`: `StartStagger()`. Play `StaggerStartAnim`. State = **Start**.
- `t = 0.79 s`: Elapsed in `[0.0, 0.8)`. State = **Start**.
- `t = 0.80 s`: Elapsed reaches 0.8 s. Play `StaggerLoopAnim` with `LoopCount = 4`. State = **Loop**.
- `t = 2.39 s`: Elapsed in `[0.8, 2.4)`. State = **Loop**.
- `t = 2.40 s`: Elapsed reaches `endStart = 2.4 s`. Stop loop montage with `BlendOut`. Play `StaggerEndAnim`. State = **End**.
- `t = 3.00 s`: Elapsed reaches `StaggerSeconds = 3.0 s`. `EndStagger()`. Posture refilled to `PostureMax`. State = **Finished** / Neutral gate.

---

## 5. Phase Transition Duration Rule & Selector Hold

### 5.1 Selector Suppression During Phase Transition
When the neutral gate detects `Health <= MaxHealth * PhaseTwoFraction` and `!bPhaseTwoLatched`:
- If `PhaseTransitionAnim` is configured:
  1. `bPhaseTwoLatched = true`.
  2. Enter state `PhaseTransition`.
  3. Store `PhaseTransitionEndsAt = now + PhaseTransitionLength`.
  4. Play `PhaseTransitionAnim` as a dynamic montage in slot `AnimSlotName`.
  5. Emit log: `[FrameworkProof] phase_anim state=Triggered sequence=<Name> slot=<Slot> from=<Phase1> to=<Phase2> duration=<L_phase>`.
  6. **Selector Hold:** In `ARPGFrameworkBossCharacter::Tick()`, while in state `PhaseTransition` (`now < PhaseTransitionEndsAt`), movement is stopped (`StopMovementImmediately()`) and card selection is **suppressed** (selector is NOT called; no card can begin).
  7. When `now >= PhaseTransitionEndsAt`:
     State `PhaseTransition` finishes.
     Emit log: `[FrameworkProof] phase_anim state=Finished phase=<Phase2>`.
     Normal neutral decision gate runs, selecting candidate cards from `PhaseTwoId`.
- If `PhaseTransitionAnim` is null / unset:
  `bPhaseTwoLatched = true`, `CurrentPhaseId = PhaseTwoId`. Selection occurs immediately on the same tick (byte-identical F6c parity).

---

## 6. Interleaving & Edge Cases

1. **Mid-Attack Stance Break:**
   - Active attack instance is immediately aborted via `Executor->Abort(TEXT("StanceBreak"))`.
   - Damaging swept windows are closed immediately; no lingering damage or trace occurs.
   - Attack animation is stopped immediately.
   - `StaggerStartAnim` begins at `dt = 0`.
   - `bStaggerAbortedAttack` is set to `true`.
   - When `EndStagger()` completes at `dt >= StaggerSeconds`, `Executor->RecoverAfterAbort()` re-arms the executor in the same encounter generation.

2. **Phase Gate Deferred Behind Stagger:**
   - Damage crossing `PhaseTwoFraction` while in `Start`, `Loop`, or `End` does NOT interrupt stagger.
   - The stagger cycle completes fully (`Start -> Loop -> End -> Finished`).
   - The neutral gate evaluates phase transition on the tick immediately following `EndStagger()`, triggering `PhaseTransitionAnim`.

3. **Stance Break During Phase Transition Sequence:**
   - The transition clip is a normal action (no invented hyperarmor).
   - If posture drains to zero while `PhaseTransitionAnim` is playing:
     * The transition sequence is immediately aborted via the existing stagger path (`Executor->Abort(TEXT("StanceBreak"))` / stop montage).
     * `bStaggered = true`, `StaggerEndsAt = now + StaggerSeconds`.
     * `bPhaseTwoLatched` remains `true` (phase transition does not un-latch).
     * The stagger sequence (`Start -> Loop -> End`) plays out completely.
     * When stagger finishes, the transition animation is **NOT replayed**; the boss proceeds directly into Phase 2 combat selection.

4. **Lethal Hit / Death while Staggered:**
   - Per F6a rules, `Dead` outranks `Staggered` in `ResolveBreak` and `ApplyHit`.
   - Lethal damage arriving while in `Start`, `Loop`, or `End` terminates stagger immediately.
   - Active stagger animations are stopped immediately.
   - Boss delegates to F6a death authority (character destroyed, `boss_dead`, `RESULT BossDefeated`).
   - Stagger timer is cleared, and no recovery logic runs.

5. **Encounter Restart while Staggered:**
   - `RestartEncounter()` terminates active animations immediately.
   - `bStaggered = false`, `bStaggerAbortedAttack = false`, `Posture = PostureMax`, sub-state resets to `None`.

6. **Fallback when Unset (Byte-Identical F8 Parity):**
   - If `StaggerStartAnim`, `StaggerLoopAnim`, and `StaggerEndAnim` are null, the boss freezes in place with identical timing and identical log lines (`stance_break`, `stagger_recovery`, `postureRefilled`), maintaining 100% backwards compatibility with Slice F8 (C448).

---

## 7. Pure Logic Unit Test Matrix (19 Cases)

The following 19 unit tests validate pure validation rules and state machine transitions in `RPGFrameworkRuntimeTests.cpp`:

1. `Test_01_PureValidation_UnsetAnims_Passes`:  
   Params with all lengths zero and null anim names pass validation cleanly.
2. `Test_02_PureValidation_IncoherentTriplet_Refused`:  
   Params with `StartLength > 0` but `LoopLength == 0` or `EndLength == 0` fails with `Framework.Profile.StaggerAnim.CoherentSet`.
3. `Test_03_PureValidation_TooShort_Refused`:  
   Params with `StartLength = 1.8`, `EndLength = 1.5`, `StaggerSeconds = 3.0` (sum 3.3 > 3.0) fails with `Framework.Profile.StaggerAnim.TooShort`.
4. `Test_04_PureValidation_MismatchedSkeleton_Refused`:  
   Params with `StartSkeleton != ExpectedSkeleton` fails with `Framework.Profile.StaggerAnim.SkeletonMismatch`.
5. `Test_05_PureValidation_EmptySlotName_Refused`:  
   Params with stagger clips configured but `AnimSlotName = NAME_None` fails with `Framework.Profile.StaggerAnim.SlotNameEmpty`.
6. `Test_06_PureValidation_SlotNodeNotFound_Refused`:  
   Params with `bHasSlotNode = false` fails with `Framework.Profile.StaggerAnim.SlotNotFound`.
7. `Test_07_PureValidation_PhaselessTransitionAnim_Refused`:  
   Params with `PhaseTransitionLength > 0` but `PhaseTwoFraction == 0.0` fails with `Framework.Profile.PhaseTransitionAnim.Phaseless`.
8. `Test_08_PureValidation_PhaseTransitionSkeletonMismatch_Refused`:  
   Params with `PhaseTransitionSkeleton != ExpectedSkeleton` fails with `Framework.Profile.PhaseTransitionAnim.SkeletonMismatch`.
9. `Test_09_StateEvaluation_TimeWindow_Start`:  
   Evaluating state at `dt = 0.0 s` and `dt = 0.79 s` with `StartLength = 0.8 s` returns `EBossStaggerState::Start`.
10. `Test_10_StateEvaluation_TimeWindow_Loop`:  
    Evaluating state at `dt = 0.80 s` and `dt = 2.39 s` with `StartLength = 0.8 s`, `EndLength = 0.6 s`, `StaggerSeconds = 3.0 s` returns `EBossStaggerState::Loop`.
11. `Test_11_StateEvaluation_TimeWindow_End`:  
    Evaluating state at `dt = 2.40 s` and `dt = 2.99 s` returns `EBossStaggerState::End`, and at `dt >= 3.00 s` triggers `EndStagger()`.
12. `Test_12_LoopCountCalculation`:  
    Verifies `middleDuration = 1.6 s`, `LoopLength = 0.5 s` yields `LoopCount = ceil(1.6 / 0.5) = 4`, and loop stops at `dt = 2.4 s`.
13. `Test_13_Interleaving_StaggerAbortsRunningAttack`:  
    Stance break arriving while `bStartedMove == true` invokes `Executor->Abort(TEXT("StanceBreak"))`, sets `bStaggerAbortedAttack = true`, and verifies `RecoverAfterAbort()` runs at `EndStagger()`.
14. `Test_14_Interleaving_PhaseGateDeferredUntilStaggerEnd`:  
    Injecting damage dropping health below `PhaseTwoFraction` while in `Loop` does not trigger phase transition; phase transition triggers only after returning to neutral.
15. `Test_15_Interleaving_DeathDuringStagger_DefersToF6a`:  
    Applying lethal hit while in `Start` or `Loop` stops stagger clips immediately, cancels stagger timer, and delegates to F6a death authority without playing `StaggerEndAnim`.
16. `Test_16_Interleaving_RestartEncounter_ResetsAllAnimStates`:  
    Invoking `RestartEncounter()` while staggered terminates animation playback, restores posture to `PostureMax`, and clears stagger flags.
17. `Test_17_PhaseTransition_HoldsSelectionForExactDuration`:  
    When Phase 2 latches with `PhaseTransitionLength = 2.0 s`, card selection is refused at `dt = 1.99 s` and allowed at `dt = 2.00 s`.
18. `Test_18_PhaseTransition_UnsetClip_ImmediateSelectionParity`:  
    When `PhaseTransitionAnim` is unset, phase latch and card selection occur immediately on the same tick (F6c parity).
19. `Test_19_Interleaving_StanceBreakDuringPhaseTransition_AbortsWithoutReplay`:  
    Stance break during `PhaseTransitionAnim` aborts the sequence, plays stagger sequence, preserves `bPhaseTwoLatched = true`, and does not replay transition after recovery.

---

## 8. PIE Acceptance Checklist & Log Tokens

### 8.1 Required Log Tokens (Prefix `[FrameworkProof]`):
- Slot Graph Verification: `[FrameworkProof] slot_graph name=FullBody nodeClass=AnimNode_Slot verified=1 label=<ProfileLabel>`
- Stagger Start: `[FrameworkProof] stagger_anim state=Start sequence=<Name> slot=<Slot> duration=<Seconds>`
- Stagger Loop: `[FrameworkProof] stagger_anim state=Loop sequence=<Name> slot=<Slot> loopCount=<Count>`
- Stagger End: `[FrameworkProof] stagger_anim state=End sequence=<Name> slot=<Slot>`
- Stagger Finish: `[FrameworkProof] stagger_anim state=Finished postureRefilled=<Value>`
- Phase Transition Trigger: `[FrameworkProof] phase_anim state=Triggered sequence=<Name> slot=<Slot> from=<Phase1> to=<Phase2> duration=<Seconds>`
- Phase Transition Complete: `[FrameworkProof] phase_anim state=Finished phase=<Phase2>`
- Phase Transition Abort: `[FrameworkProof] phase_anim state=Aborted reason=StanceBreak phase=<Phase2>`

### 8.2 PIE Acceptance Checklist:
1. **Windowed PIE Execution:** Driver runs in windowed editor (`run_editor_script.ps1 -NullRhi 0`) per Owner Decision 2 (`KI-144`).
2. **AnimBP Slot Verification:** Proof log confirms `slot_graph name=FullBody verified=1`.
3. **Deterministic Stance Break Proof:** Boss receives posture drain to 0; proof log confirms `stagger_anim state=Start` -> `state=Loop` -> `state=End` -> `state=Finished`.
4. **Mid-Attack Abort Proof:** Boss stance breaks during attack execution; log confirms `stance_break state=MidAttack` and clean transition to `stagger_anim state=Start`.
5. **Phase 2 Transition Proof:** Boss takes damage crossing `PhaseTwoFraction`; log confirms `phase_anim state=Triggered`, holds selection for transition length, and emits `phase_anim state=Finished` before Phase 2 card selection.
6. **Clean Tear-Down:** Zero memory faults, zero `EXCEPTION_INT_DIVIDE_BY_ZERO`, clean exit code 0.
