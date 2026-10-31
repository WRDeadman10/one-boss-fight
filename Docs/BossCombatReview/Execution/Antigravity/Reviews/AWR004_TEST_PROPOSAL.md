# AWR-004 Cone Boundary Hysteresis Analysis & Design (v2.0)

## 1. Requirement & Ledger Context

### Canonical Requirements (requirements.json)
- **ID**: `BOSS-AWR-004`
- **Title**: `Signed angle and hysteresis`
- **Behavior**: *"Tail swipes answer positions behind him, and frontal or flank positioning changes certain sword/hammer continuations in detailed player observations."*
- **Verify**: *"Orbit across front/side/rear boundaries while an attack finishes; verify stable branch selection without oscillation."*

### Ledger Specification (witness_status_v3.json)
- **ID**: `BOSS-AWR-004`
- **Title**: `Signed angle and hysteresis`
- **Status**: `PARTIAL`
- **Observable**: *"TestMoveModelSelectsBestMatchingCandidate evaluates FrontConeDegrees; signed yaw boundary hysteresis tested against threshold angles."*
- **Notes**: *"MoveModel tests (model_tests:60) verify FrontConeDegrees evaluation with signed yaw at -60 and +60 deg; hysteresis buffer on cone boundary not yet implemented."*
- **Baseline Citation**: `Source/OneBossFight/Tests/RPGBossMoveModelTests.cpp:60`

---

## 2. Call Chain Analysis: Can a Discrete-Attack Boss Show Hysteresis?

### Verified Runtime Call Chain
1. **Decision Gate in Boss Character** (`Source/OneBossFight/Boss/RPGFrameworkBossCharacter.cpp:147-155`):
   When entering neutral (`!bStartedMove && !bPhaseHold`), the boss computes `S.SignedYawDegrees` from target position and invokes `Selector.Select(Executor->Model(), S, Decision)` on line 155.
2. **Selector Candidate Evaluation** (`Source/OneBossFight/Player/RPGBossMoveSelector.cpp:40`):
   Iterates configured candidates and checks hard eligibility via `Model.IsEligible(C.Card, S, Error)`.
3. **MoveModel Hard Filter** (`Source/OneBossFight/Player/RPGBossMoveModel.cpp:24-36`):
   - Line 24 requires idle state: `if (!S.bNeutral || CurrentState!=ERPGBossMoveModelState::Idle) return Refuse(Error,TEXT("MoveModel.State"));`
   - Line 35 evaluates knife-edge cone: `if (FMath::Abs(S.SignedYawDegrees)>0.5*Card->Spec().FrontConeDegrees) return Refuse(Error,TEXT("MoveModel.Cone"));`
4. **Execution Start** (`Source/OneBossFight/Boss/RPGFrameworkBossCharacter.cpp:181-182`):
   Starts the chosen card via `Executor->StartCard(...)` and notes start time via `Selector.NoteStarted(Decision.ChosenIndex, S.ClockSeconds)`.
5. **Model Playback State** (`Source/OneBossFight/Player/RPGBossMoveModel.cpp:51-54`):
   `Start` transitions `CurrentState = ERPGBossMoveModelState::Committed`. The attack executes for its full duration (typically 1.0s to 2.5s). `Selector.Select` is **never called** during playback.
6. **Model Cleanup on Idle** (`Source/OneBossFight/Player/RPGBossMoveModel.cpp:82`, `Source/OneBossFight/Player/RPGBossMoveModel.cpp:128`):
   When the move finishes or aborts, line 82 and line 128 explicitly reset state:
   `CurrentState=ERPGBossMoveModelState::Idle; CurrentCard.Reset(); OpenWindows.Reset();`

### Architectural Finding: Hysteresis over What?
In a continuous per-tick controller (e.g. character steering or turret tracking), hysteresis prevents high-frequency flickering between states across adjacent ticks.
However, in this discrete combat engine:
- **Decisions are discrete events separated by full attack durations (1.0s to 3.0s).**
  Between attack $N$ and attack $N+1$, the player moves, dodges, or repositions across several meters. Instantaneous yaw from seconds ago has zero physical relevance to whether the target is in the front cone now.
- **The model is strictly reset to null on Idle.**
  Because `CurrentCard` is reset to null whenever `CurrentState == Idle` (`Source/OneBossFight/Player/RPGBossMoveModel.cpp:82`, `Source/OneBossFight/Player/RPGBossMoveModel.cpp:128`), any logic attempting to read `CurrentCard` inside `IsEligible` is fundamentally invalid and would crash with a null dereference.
- **The only continuous per-tick yaw evaluation occurs during repositioning turn-in-place** (`Source/OneBossFight/Boss/RPGFrameworkBossCharacter.cpp:161-168`):
  When target is in range band but no card is eligible (`INDEX_NONE`), line 166 steps boss yaw toward the player at `RepositionTurnDegPerSecond`. This is a monotonic turn into the cone, not rapid boundary oscillation.
- **Soulslike design intent**:
  The FromSoftware combat observable (*"Orbit across front/side/rear boundaries while an attack finishes; verify stable branch selection without oscillation"*) is answered by **discrete directional attack families** (rear tail-swipes vs frontal swings) and **combo branch context gates** (`COM-003` turn-around branches), evaluated atomically at the decision gate snapshot, not by a stateful angular hysteresis margin on a continuous cone check.

---

## 3. Minimal Design (If Implemented in Selector)

If angle hysteresis across consecutive decisions is desired, **the memory belongs strictly in `FRPGBossMoveSelector`**, not in `RPGBossMoveModel`.

### Architecture & Null-Safety
1. **No Pointer Dereferencing**: `FRPGBossMoveSelector` already manages `Recent` and `LastStartClock`. It maintains an integer `int32 LastChosenIndex = INDEX_NONE;`.
2. **Explicit Config**: `FRPGBossSelectorConfig` adds `float ConeHysteresisDegrees = 0.f;` (e.g. `2.5f`).
3. **Model Signature**: `RPGBossMoveModel::IsEligible` accepts an optional `double ExtraHalfConeDegrees = 0.0`:
   ```cpp
   // In Source/OneBossFight/Player/RPGBossMoveModel.cpp:35
   if (FMath::Abs(S.SignedYawDegrees) > (0.5 * Card->Spec().FrontConeDegrees + ExtraHalfConeDegrees))
       return Refuse(Error, TEXT("MoveModel.Cone"));
   ```
4. **Selector Query** (`Source/OneBossFight/Player/RPGBossMoveSelector.cpp:40`):
   ```cpp
   const double ExtraCone = (I == LastChosenIndex) ? double(Config.ConeHysteresisDegrees) : 0.0;
   if (!Model.IsEligible(C.Card, S, Error, ExtraCone)) T.Refusal = Error;
   ```
5. **State Update**: In `NoteStarted(int32 Index, double ClockSeconds)`, set `LastChosenIndex = Index`. In `Reset()`, set `LastChosenIndex = INDEX_NONE`.

### Hand-Computed Verification Values
For test card `C` (`FrontConeDegrees = 120.0`, nominal half-cone = `60.0` deg, `ConeHysteresisDegrees = 2.5` deg):
- **Unlatched Candidate (`I != LastChosenIndex`)**:
  - `SignedYawDegrees = 60.0`: `|60.0| <= 60.0` -> **PASS (Eligible)**
  - `SignedYawDegrees = -60.0`: `|-60.0| <= 60.0` -> **PASS (Eligible)**
  - `SignedYawDegrees = 60.01`: `|60.01| > 60.0` -> **FAIL (`MoveModel.Cone`)**
  - `SignedYawDegrees = -60.01`: `|-60.01| > 60.0` -> **FAIL (`MoveModel.Cone`)**
- **Incumbent Candidate (`I == LastChosenIndex`)**:
  - Effective threshold: `60.0 + 2.5 = 62.5` deg.
  - `SignedYawDegrees = 61.5`: `|61.5| <= 62.5` -> **PASS (Eligible via Hysteresis)**
  - `SignedYawDegrees = -62.0`: `|-62.0| <= 62.5` -> **PASS (Eligible via Hysteresis)**
  - `SignedYawDegrees = 62.5`: `|62.5| <= 62.5` -> **PASS (Eligible at Boundary)**
  - `SignedYawDegrees = 62.51`: `|62.51| > 62.5` -> **FAIL (`MoveModel.Cone`)**

---

## 4. Engineering Recommendation: Retain PARTIAL

**We recommend leaving `BOSS-AWR-004` as PARTIAL in the ledger.**

### Rationale:
1. **Zero Observable Gameplay Impact**: In discrete combat where attacks take 1.0s to 3.0s, angular hysteresis between attacks is a phantom feature that never fires in practice because player displacement across seconds exceeds any small degree buffer.
2. **Model Purity**: Keeping `RPGBossMoveModel::IsEligible` strictly mathematical, memoryless, and stateless maintains clean architecture. Adding hysteresis parameters pollutes the interface for no gameplay benefit.
3. **Honest Ledger Documentation**: The row's current status (**PARTIAL**) truthfully documents that symmetric front-cone evaluation is 100% verified (`Source/OneBossFight/Tests/RPGBossMoveModelTests.cpp:60`), while artificial tick-to-tick cone hysteresis is unneeded in a discrete-action boss architecture.
