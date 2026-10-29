# Domain Proposal Sheet: URPGBossDeath (DD25 Proposal)

> **DOCUMENT STATUS: REVISED PER LEAD REVIEW [C-274]**  
> **Component Under Review:** `URPGBossDeath`  
> **Source Header:** `Source/OneBossFight/Player/RPGBossDeath.h`  
> **Source Implementation:** `Source/OneBossFight/Player/RPGBossDeath.cpp`  
> **Supporting Files:** `Source/OneBossFight/Player/RPGBossClips.h`, `Source/OneBossFight/Player/RPGBossRemains.h/.cpp`  
> **Original Submission:** Antigravity under order `A-192` in `[A-192]`.  
> **Lead Review:** Returned with 6 specific corrections in `[C-274]`.  
> **Audit Hygiene:** The original A-192 proposal text is preserved in Section 9 below for historical audit; baseline also staged under `NativeDerivation/original_A192/`.

---

## 1. Corrections Applied Per Lead Review [C-274]

1. **Substantive Correction on `PackEndTimeMultiplier` Semantics:**
   - In `RPGBossDeath.cpp:296`, the runtime guard is `if (PackEndTimeMultiplier > 0.f)` and the property write is at `:303`.
   - A value of `0.0f` or less natively means "do not inject the multiplier" (the default `0.0f` is the documented OFF state).
   - `NaN` fails the `> 0.f` comparison in the identical manner.
   - Therefore, negative and `NaN` are natively **ignored** (skipped), not undefined behavior.
   - The proposed authored contract is finite-first (`NotFinite`), non-negative (`Negative` rejected: `>= 0.0f`, with `0.0f` documented as OFF), and bounded above by standard magnitude ceiling `1.0e6f` (`AboveCeiling`).

2. **Line Citations Re-verified (`grep -n` against `RPGBossDeath.cpp` and `RPGBossClips.h`):**
   - `DyingSeconds`: transition condition is at `RPGBossDeath.cpp:419` (`if (State == EState::Dying && Age >= DyingSeconds)`).
   - `BlendInSeconds`: evaluated at `RPGBossDeath.cpp:439` as `StartAt > 0.f ? 0.f : BlendInSeconds` passed to `RPGBossClips::Play`, whose `BlendIn` parameter is declared at `Source/OneBossFight/Player/RPGBossClips.h:52`.
   - `HoldAtSeconds`: evaluated at `RPGBossDeath.cpp:446` (`if (StartAt >= HoldAtSeconds)`), `RPGBossDeath.cpp:494` (`if (!bPoseHeld && Anim->Montage_GetPosition(Montage) >= HoldAtSeconds)`), and `RPGBossDeath.cpp:519` (`const float StartAt = FMath::Clamp(static_cast<float>(Age), 0.f, HoldAtSeconds);`).
   - `PackPollSeconds`: evaluated at `RPGBossDeath.cpp:223` (`NextPackPoll = Now + PackPollSeconds;`).
   - `MaxClipRestarts`: evaluated at `RPGBossDeath.cpp:508` (`if (RestartsThisDeath >= MaxClipRestarts)`) and `RPGBossDeath.cpp:510` (`if (RestartsThisDeath == MaxClipRestarts)`).
   - `ARPGBossRemains::Spawn`: invoked at `RPGBossDeath.cpp:123`.
   - `KeepPhysicsOff`: defined at `RPGBossDeath.cpp:458`.
   - `KeepClip`: defined at `RPGBossDeath.cpp:484`.
   - `Preload`: defined at `RPGBossDeath.cpp:160` (mode check at `:164-171`).
   - `PollPack`: defined at `RPGBossDeath.cpp:210` (called during alive ticks at `:345`).
   - `BeginDeath`: defined at `RPGBossDeath.cpp:360` (mode branch at `:377`, `:386`).

3. **Accurate Arithmetic of `HoldAtSeconds` in `FMath::Clamp`:**
   - In `RPGBossDeath.cpp:519`, the clip restart position is computed via `FMath::Clamp(static_cast<float>(Age), 0.f, HoldAtSeconds)`.
   - In Unreal Engine, `FMath::Clamp(X, Min, Max)` evaluates `X < Min ? Min : (X > Max ? Max : X)`. If `HoldAtSeconds < 0.f`, the bounds are inverted (`Min = 0.f` > `Max = HoldAtSeconds`). Any positive `Age` (which is `> Max`) returns `HoldAtSeconds` (a negative value).
   - That negative value is passed as `StartAt` into `RPGBossClips::Play(..., StartTime = StartAt)` at `:521`, which forwards to `UAnimInstance::PlaySlotAnimationAsDynamicMontage(..., InTimeToStartMontageAt = StartAt)` at `RPGBossClips.h:59`, yielding invalid negative start time in engine animation evaluation.
   - Furthermore, at `:446` (`StartAt >= HoldAtSeconds`) and `:494` (`Position >= HoldAtSeconds`), if `HoldAtSeconds <= 0.f`, any position `>= 0.f` immediately freezes the montage on frame 0 before playback begins.
   - This native clamping and pause inversion is the mathematical reason for a strictly positive floor `HoldAtSeconds > 0.0f` (not the editor `ClampMin = "0.1"` metadata).

4. **`MaxClipRestarts` Semantics & Authored Choice Ceiling:**
   - In `RPGBossDeath.cpp:508-515`:
     ```cpp
     if (RestartsThisDeath >= MaxClipRestarts)
     {
         if (RestartsThisDeath == MaxClipRestarts)
         {
             ++RestartsThisDeath;
             UE_LOG(LogRPGBossDeath, Warning, TEXT("%s: the death clip was stopped %d times, not started again..."), *Character->GetName(), MaxClipRestarts);
         }
         return;
     }
     ```
   - If `MaxClipRestarts == 0`: initial `RestartsThisDeath` (0) satisfies `>= 0` and `== 0`, increments to 1, logs the warning once, and disables all restarts immediately.
   - If `MaxClipRestarts < 0` (e.g. -1): initial `RestartsThisDeath` (0) satisfies `>= -1`, but `0 == -1` is false. Restarts are disabled silently, and the warning never logs.
   - Therefore, the valid domain is `MaxClipRestarts >= 0` (`Negative` rejected).
   - An upper integer ceiling of `1000` is designated explicitly as an **AUTHORED CHOICE** to screen out pathological configuration or runaway restart loops in corrupted animation states.

5. **Boundary Classification:**
   - Authored boundaries are labelled strictly as NATIVE-DERIVED (when derived directly from native .cpp invariants) or AUTHORED CHOICE (when selecting policy bounds such as ceilings).

6. **Mode-Dependent Required Paths vs Uniform Contract:**
   - In `RPGBossDeath.cpp:164-171`:
     ```cpp
     if (DeathMode == ERPGBossDeathMode::OwnClip)
     {
         GetClip();
     }
     else
     {
         GetMontage();
     }
     ```
   - When `DeathMode == ERPGBossDeathMode::OwnClip`, only `DeathClip` is queried and loaded (`:166`, `:380`, `:435`). `DeathMontage` is never loaded or queried; an empty `DeathMontage` produces zero runtime warnings.
   - When `DeathMode == ERPGBossDeathMode::PackMontage`, only `DeathMontage` is queried and loaded (`:170`, `:220`, `:388`). `DeathClip` is never loaded or queried; an empty `DeathClip` produces zero runtime warnings.
   - **Contract Proposal:** We propose the **Uniform Requirement (require BOTH paths)** as the simpler and safer authored contract. Pre-validating both soft paths ensures that switching `DeathMode` during testing or authoring never exposes dormant broken references, avoids conditional schema branching, and enforces complete asset verification offline. (The alternate mode-dependent contract is also documented in Section 6).

---

## 2. Component Overview & Source Locations

`URPGBossDeath` orchestrates the boss defeat sequence when health reaches zero. The component supports two distinct execution architectures:
1. `PackMontage`: Injects a custom death montage into the pack's live `GA_EnemyRagdollDeath_C` ability via reflection, letting the pack execute its montage and ragdoll flow.
2. `OwnClip`: Bypasses the pack's animation flow entirely, directly playing sequence `AN_Boss01_DeathLegend` via `RPGBossClips::Play`, suppressing the pack's ragdoll simulation every tick (`KeepPhysicsOff`), and freezing the pose at `HoldAtSeconds` (`KeepClip`).

### Source Locations:
- Header: `Source/OneBossFight/Player/RPGBossDeath.h`
- Implementation: `Source/OneBossFight/Player/RPGBossDeath.cpp`
- Clips Helper: `Source/OneBossFight/Player/RPGBossClips.h`
- Remains Persistent Actor: `Source/OneBossFight/Player/RPGBossRemains.h` and `.cpp`

---

## 3. Real Authored Header Declarations (12 Authored Fields)

From `Source/OneBossFight/Player/RPGBossDeath.h:51-93`:

| Field Name | C++ Type | Header Default | Editor Metadata |
|---|---|---|---|
| `DeathMode` | `ERPGBossDeathMode` | `ERPGBossDeathMode::PackMontage` (`:51`) | None |
| `DeathClip` | `TSoftObjectPtr<UAnimSequence>` | `AN_Boss01_DeathLegend` (`RPGBossDeath.cpp:37`) | None |
| `DeathMontage` | `TSoftObjectPtr<UAnimMontage>` | `AM_Boss01_DeathLegend` (`RPGBossDeath.cpp:38`) | None |
| `PackDeathAbilityClassName` | `FName` | `TEXT("GA_EnemyRagdollDeath_C")` (`:63`) | None |
| `PackDeathMontagesName` | `FName` | `TEXT("DeathMontages")` (`:66`) | None |
| `PackPollSeconds` | `float` | `1.f` (`:70`) | `ClampMin = "0.1"` |
| `PackEndTimeMultiplier` | `float` | `0.f` (`:74`) | `ClampMin = "0.0"` |
| `HoldAtSeconds` | `float` | `3.f` (`:78`) | `ClampMin = "0.1"` |
| `DyingSeconds` | `float` | `2.5f` (`:82`) | `ClampMin = "0.1"` |
| `BlendInSeconds` | `float` | `0.1f` (`:85`) | `ClampMin = "0.0"` |
| `MaxClipRestarts` | `int32` | `8` (`:89`) | `ClampMin = "0"` |
| `bGuardPackDeath` | `bool` | `false` (`:93`) | None |

---

## 4. Editor Metadata Audit (`ClampMin` is Not a Runtime Guard)

All 6 `meta = (ClampMin = ...)` declarations above are **Unreal Editor property metadata only**.
Inspection of `RPGBossDeath.cpp` reveals:
- Zero calls to `FMath::Clamp` on `PackPollSeconds`, `PackEndTimeMultiplier`, `DyingSeconds`, or `BlendInSeconds`.
- The only clamp in the file is `FMath::Clamp(static_cast<float>(Age), 0.f, HoldAtSeconds)` at `:519`.
- Therefore, all scalar boundaries must be enforced natively in the typed profile adapter (`ValidateDeath`) rather than relying on editor metadata.

---

## 5. Native Implementation & Execution Semantics (`RPGBossDeath.cpp`)

### 5.1 Lifecycle & Constructor
- **Constructor (`RPGBossDeath.cpp:31-39`):**
  - Enables tick: `bCanEverTick = true`, `bStartWithTickEnabled = true`, `TickInterval = 0.f`.
  - Assigns hardcoded default paths for `DeathClip` (`AN_Boss01_DeathLegend`) and `DeathMontage` (`AM_Boss01_DeathLegend`).
- **`Attach()` (`:41-55`):** Static attach helper; sets `DeathMode`.
- **`Preload()` (`:160-173`):** Called on first tick (`:162`).
  - If `DeathMode == ERPGBossDeathMode::OwnClip`: calls `GetClip()`, synchronously loading `DeathClip` (`:137`).
  - If `DeathMode == ERPGBossDeathMode::PackMontage`: calls `GetMontage()`, synchronously loading `DeathMontage` (`:151`).
  - Only the asset required by the selected mode is loaded.
- **`EndPlay()` (`:117-128`):**
  - Evaluates `if (!bEnding && State == EState::Dead && EndPlayReason == EEndPlayReason::Destroyed)` (`:119`).
  - Spawns persistent remains via `ARPGBossRemains::Spawn(World, LastRemainsTransform, LoadedRemainsMesh, LoadedRemainsMaterial, LoadedRemainsBurst)` (`:123`).
  - Marks `bEnding = true` (`:127`).

### 5.2 Pack Ability Reflection & Injection (`ApplyPackMontage`)
- In `PackMontage` mode, `PollPack()` runs during alive ticks (`:343-346`) every `PackPollSeconds` (`:223`).
- Looks up live ability instance matching `PackDeathAbilityClassName` (`GA_EnemyRagdollDeath_C`) in owner's Ability System Component (`:212`).
- Inspects property named `PackDeathMontagesName` (`DeathMontages`) (`:239`). Handles either `TArray<UAnimMontage*>` or `TArray<F_AbilityMontage>` struct array.
- Multiplier injection (`:296-304`):
  - `if (PackEndTimeMultiplier > 0.f)`: writes `PackEndTimeMultiplier` into the `EndTimeMultiplier` float field of the live struct element.
  - If `<= 0.f` or `NaN`: skipped entirely. `0.0f` is the documented OFF state.

### 5.3 Death Edge Detection & Animation Flow
- Edge detection (`:331-350`): Monitors `Attribute.Health`. Requires `bSeenAlive = true` (`:334`) to prevent false triggers during PIE initialization (KI-081).
- Upon health reaching zero: `BeginDeath()` (`:360`).
- **`OwnClip` Flow (`:377-385`):**
  - Starts clip via `StartOwnClip(Character, 0.f)` (`:380`), calling `RPGBossClips::Play` (`:439`).
  - Evaluates `StartAt > 0.f ? 0.f : BlendInSeconds` (`:439`). Initial start passes `BlendInSeconds`.
  - In `TickDeath()`:
    - Calls `KeepPhysicsOff(Character)` (`:426`, `:458-482`): disables mesh physics simulation and snaps mesh relative transform back to capsule if ragdoll simulation activated.
    - Calls `KeepClip(Character, Age)` (`:427`, `:484-522`):
      - Checks `Anim->Montage_GetPosition(Montage) >= HoldAtSeconds` (`:494`); when reached, calls `Anim->Montage_Pause(Montage)` (`:496`) and sets `bPoseHeld = true`.
      - If montage is stopped prematurely by pack ability, checks `RestartsThisDeath >= MaxClipRestarts` (`:508`). If within limit, restarts clip at `StartAt = FMath::Clamp(static_cast<float>(Age), 0.f, HoldAtSeconds)` (`:519`).
- **State Transition to `Dead` (`:419-424`):**
  - `if (State == EState::Dying && Age >= DyingSeconds)`: transitions `State = EState::Dead`.
- **KI-083 Destruction Contract:**
  - The pack's death ability destroys the boss actor ~4.35s after death.
  - While alive or dying, `KeepPhysicsOff` and `KeepClip` maintain visual pose.
  - In `EndPlay`, `ARPGBossRemains::Spawn` spawns a static remains actor matching `LastRemainsTransform` (`:123`), persisting the pose in the arena permanently.

---

## 6. Non-Finite Arithmetic & Degenerate Timing Analysis

### 6.1 Analysis of Authored Numeric Properties

1. **`PackPollSeconds` (`float`, default `1.f`, editor metadata `ClampMin = "0.1"`):**
   - Runtime usage: `NextPackPoll = Now + PackPollSeconds` (`:223`).
   - If `NaN` or `Inf`: `NextPackPoll` becomes non-finite; comparisons `Now < NextPackPoll` fail or produce undefined behavior.
   - If `<= 0.f`: `NextPackPoll <= Now`, causing reflection polling to execute every single tick, degrading performance.
   - Proposed domain: strictly positive (`PackPollSeconds > 0.0f`), finite, ceiling `1.0e6f`.

2. **`PackEndTimeMultiplier` (`float`, default `0.f`, editor metadata `ClampMin = "0.0"`):**
   - Runtime usage: `if (PackEndTimeMultiplier > 0.f)` (`:296`).
   - If `<= 0.f` or `NaN`: condition evaluates false; injection is skipped natively. `0.0f` is the documented OFF state.
   - If positive: written into pack ability property (`:303`).
   - Proposed domain: non-negative (`PackEndTimeMultiplier >= 0.0f`), finite, ceiling `1.0e6f`.

3. **`HoldAtSeconds` (`float`, default `3.f`, editor metadata `ClampMin = "0.1"`):**
   - Runtime usage:
     - `:446`: `if (StartAt >= HoldAtSeconds)` -> immediately pauses montage.
     - `:494`: `if (!bPoseHeld && Anim->Montage_GetPosition(Montage) >= HoldAtSeconds)` -> freezes pose.
     - `:519`: `const float StartAt = FMath::Clamp(static_cast<float>(Age), 0.f, HoldAtSeconds);`.
   - If `HoldAtSeconds < 0.f`: inverts `FMath::Clamp(Age, 0.f, HoldAtSeconds)` bounds (`Min > Max`). Any positive `Age` returns `HoldAtSeconds` (negative), passing negative start time into `PlaySlotAnimationAsDynamicMontage`.
   - If `HoldAtSeconds <= 0.f`: pose freezes instantly on frame 0 before sequence plays.
   - If `NaN`: comparison `Position >= HoldAtSeconds` always evaluates false; clip never freezes.
   - Proposed domain: strictly positive (`HoldAtSeconds > 0.0f`), finite, ceiling `1.0e6f`.

4. **`DyingSeconds` (`float`, default `2.5f`, editor metadata `ClampMin = "0.1"`):**
   - Runtime usage: `if (State == EState::Dying && Age >= DyingSeconds)` (`:419`).
   - If `<= 0.f`: state transitions to `Dead` on the very first tick.
   - If `NaN`: comparison `Age >= DyingSeconds` is always false; component never transitions to `Dead`, and remains are never spawned in `EndPlay` (`:119`).
   - Proposed domain: strictly positive (`DyingSeconds > 0.0f`), finite, ceiling `1.0e6f`.

5. **`BlendInSeconds` (`float`, default `0.1f`, editor metadata `ClampMin = "0.0"`):**
   - Runtime usage: passed to `RPGBossClips::Play(..., BlendInSeconds, ...)` (`:439`).
   - If `< 0.f`: negative blend duration passed to Unreal animation system produces undefined montage blending.
   - If `NaN`: non-finite blend duration in montage playback.
   - Proposed domain: non-negative (`BlendInSeconds >= 0.0f`), finite, ceiling `1.0e6f`.

6. **`MaxClipRestarts` (`int32`, default `8`, editor metadata `ClampMin = "0"`):**
   - Runtime usage: `if (RestartsThisDeath >= MaxClipRestarts)` (`:508`) with equality warning check (`:510`).
   - If `== 0`: disables restarts immediately; logs warning once.
   - If `< 0`: disables restarts immediately; warning never logs (silent cutoff).
   - Proposed domain: non-negative (`MaxClipRestarts >= 0`).
   - Integer ceiling: upper bound of `1000` designated as **AUTHORED CHOICE** to prevent runaway restart loops.

---

## 7. What Can Be Validated Structurally vs What Stays UNRESOLVED

### 7.1 Structurally Validated Offline (Typed Record Contract)
1. **Float Finite-First:** All 5 float properties must be finite (`FMath::IsFinite`).
2. **Scalar Bounds:**
   - `PackPollSeconds > 0.0f` and `<= 1.0e6f`
   - `PackEndTimeMultiplier >= 0.0f` and `<= 1.0e6f`
   - `HoldAtSeconds > 0.0f` and `<= 1.0e6f`
   - `DyingSeconds > 0.0f` and `<= 1.0e6f`
   - `BlendInSeconds >= 0.0f` and `<= 1.0e6f`
   - `MaxClipRestarts >= 0` and `<= 1000` (Authored Choice ceiling)
3. **Syntactic FNames:** `PackDeathAbilityClassName` and `PackDeathMontagesName` non-empty, no whitespace/control characters.
4. **Soft Path Lexical Syntax:** Verified against A-184 engine macros (`INVALID_OBJECTNAME_CHARACTERS`, `INVALID_LONGPACKAGE_CHARACTERS`).
5. **Path Requirement Policy:**
   - **Approach B (Proposed - Uniform Requirement):** Both `DeathClip` and `DeathMontage` must be non-empty and syntactically valid soft paths.
   - **Approach A (Mode-Dependent):** If `DeathMode == OwnClip`, require `DeathClip`; if `DeathMode == PackMontage`, require `DeathMontage`.

### 7.2 UNRESOLVED Runtime Behavior (Typed Record Does NOT Prove)
- Whether `DeathClip` or `DeathMontage` exists on disk or loads successfully.
- Whether live `GA_EnemyRagdollDeath_C` ability instance exists in owner ASC.
- Whether pack's `DeathMontages` property exists or has expected element layout.
- Physical placement and socket attachment of character mesh (`KeepPhysicsOff`).
- Static remains Niagara burst effect and mesh validity in `ARPGBossRemains`.

---

## 8. Lifecycle Facts for the Configure Guard

- **Safe Pre-Registration Assignment:** Yes. `URPGBossDeath` performs zero work in its constructor beyond field initialization (`:31-39`). Synchronous loading and polling occur only in `Preload()` (`:160`) and `TickComponent()` (`:319`).
- **Constructor Defaults:**
  - `DeathClip = /Game/OneBossFight/Boss01/Animations/AN_Boss01_DeathLegend.AN_Boss01_DeathLegend`
  - `DeathMontage = /Game/OneBossFight/Boss01/Animations/AM_Boss01_DeathLegend.AM_Boss01_DeathLegend`
  - `PackDeathAbilityClassName = GA_EnemyRagdollDeath_C`
  - `PackDeathMontagesName = DeathMontages`

---

## 9. Proposed Validation Contract, Order, and Diagnostic Tokens

### (1) Float Finite Checks (Declaration Order)
For each float field in header declaration order (`PackPollSeconds`, `PackEndTimeMultiplier`, `HoldAtSeconds`, `DyingSeconds`, `BlendInSeconds`):
- If not finite: `Refuse(TEXT("InvalidDeath.NotFinite"), TEXT("Death.<Field> is not finite"));`

### (2) Float & Int Domain Bounds (Declaration Order)
1. `PackPollSeconds`:
   - If `<= 0.0f`: `Refuse(TEXT("InvalidDeath.NotPositive"), TEXT("Death.PackPollSeconds must be greater than zero"));`
   - If `> 1.0e6f`: `Refuse(TEXT("InvalidDeath.AboveCeiling"), TEXT("Death.PackPollSeconds exceeds magnitude ceiling"));`
2. `PackEndTimeMultiplier`:
   - If `< 0.0f`: `Refuse(TEXT("InvalidDeath.Negative"), TEXT("Death.PackEndTimeMultiplier cannot be negative"));`
   - If `> 1.0e6f`: `Refuse(TEXT("InvalidDeath.AboveCeiling"), TEXT("Death.PackEndTimeMultiplier exceeds magnitude ceiling"));`
3. `HoldAtSeconds`:
   - If `<= 0.0f`: `Refuse(TEXT("InvalidDeath.NotPositive"), TEXT("Death.HoldAtSeconds must be greater than zero"));`
   - If `> 1.0e6f`: `Refuse(TEXT("InvalidDeath.AboveCeiling"), TEXT("Death.HoldAtSeconds exceeds magnitude ceiling"));`
4. `DyingSeconds`:
   - If `<= 0.0f`: `Refuse(TEXT("InvalidDeath.NotPositive"), TEXT("Death.DyingSeconds must be greater than zero"));`
   - If `> 1.0e6f`: `Refuse(TEXT("InvalidDeath.AboveCeiling"), TEXT("Death.DyingSeconds exceeds magnitude ceiling"));`
5. `BlendInSeconds`:
   - If `< 0.0f`: `Refuse(TEXT("InvalidDeath.Negative"), TEXT("Death.BlendInSeconds cannot be negative"));`
   - If `> 1.0e6f`: `Refuse(TEXT("InvalidDeath.AboveCeiling"), TEXT("Death.BlendInSeconds exceeds magnitude ceiling"));`
6. `MaxClipRestarts`:
   - If `< 0`: `Refuse(TEXT("InvalidDeath.Negative"), TEXT("Death.MaxClipRestarts cannot be negative"));`
   - If `> 1000`: `Refuse(TEXT("InvalidDeath.AboveCeiling"), TEXT("Death.MaxClipRestarts exceeds authored ceiling (1000)"));`

### (3) Syntactic FNames
1. `PackDeathAbilityClassName`:
   - If empty: `Refuse(TEXT("InvalidDependency.Missing"), TEXT("Death.PackDeathAbilityClassName is required"));`
   - If whitespace/control characters: `Refuse(TEXT("InvalidDependency.Malformed"), TEXT("Death.PackDeathAbilityClassName is malformed"));`
2. `PackDeathMontagesName`:
   - If empty: `Refuse(TEXT("InvalidDependency.Missing"), TEXT("Death.PackDeathMontagesName is required"));`
   - If whitespace/control characters: `Refuse(TEXT("InvalidDependency.Malformed"), TEXT("Death.PackDeathMontagesName is malformed"));`

### (4) Soft Path References (Uniform Contract)
1. `DeathClip`:
   - If empty: `Refuse(TEXT("InvalidDependency.Missing"), TEXT("Death.DeathClip is required"));`
   - If malformed soft path: `Refuse(TEXT("InvalidDependency.Malformed"), TEXT("Death.DeathClip is malformed"));`
2. `DeathMontage`:
   - If empty: `Refuse(TEXT("InvalidDependency.Missing"), TEXT("Death.DeathMontage is required"));`
   - If malformed soft path: `Refuse(TEXT("InvalidDependency.Malformed"), TEXT("Death.DeathMontage is malformed"));`

---

## 10. Historical Audit: Original A-192 Proposal Text

<details>
<summary>Click to expand original A-192 proposal text (preserved for audit)</summary>

```markdown
# Domain Proposal Sheet: URPGBossDeath (DD25 Proposal - Original A-192 Submission)

## 1. Component Overview & Source Locations
Source files: `Source/OneBossFight/Player/RPGBossDeath.h`, `Source/OneBossFight/Player/RPGBossDeath.cpp`
Supporting: `Source/OneBossFight/Player/RPGBossClips.h`, `Source/OneBossFight/Player/RPGBossRemains.h/.cpp`

## 2. Real Authored Header Declarations (12 Authored Fields)
From RPGBossDeath.h:51-93:
- DeathMode (ERPGBossDeathMode, def PackMontage)
- DeathClip (TSoftObjectPtr<UAnimSequence>)
- DeathMontage (TSoftObjectPtr<UAnimMontage>)
- PackDeathAbilityClassName (FName, def GA_EnemyRagdollDeath_C)
- PackDeathMontagesName (FName, def DeathMontages)
- PackPollSeconds (float, def 1.f, ClampMin = 0.1)
- PackEndTimeMultiplier (float, def 0.f, ClampMin = 0.0)
- HoldAtSeconds (float, def 3.f, ClampMin = 0.1)
- DyingSeconds (float, def 2.5f, ClampMin = 0.1)
- BlendInSeconds (float, def 0.1f, ClampMin = 0.0)
- MaxClipRestarts (int32, def 8, ClampMin = 0)
- bGuardPackDeath (bool, def false)

## 3. Editor Metadata Audit (ClampMin is Not a Runtime Guard)
All 6 ClampMin declarations are editor property metadata only. RPGBossDeath.cpp performs zero runtime clamping on these properties.

## 4. Native Implementation & Execution Semantics (RPGBossDeath.cpp)
Constructor sets tick enabled and hardcoded asset paths.
Preload synchronously loads clip or montage based on DeathMode.
EndPlay spawns ARPGBossRemains static mesh actor and burst Niagara effect.
Reflection injects montage and multiplier into GA_EnemyRagdollDeath_C.
OwnClip directly plays AN_Boss01_DeathLegend, suppresses ragdoll physics (KeepPhysicsOff), and pauses pose at HoldAtSeconds (KeepClip).

## 5. Non-Finite Arithmetic & Degenerate Timing Analysis
PackPollSeconds <= 0.0 polls every tick.
PackEndTimeMultiplier negative/NaN yields undefined behavior.
HoldAtSeconds <= 0.0 pauses on frame 0; NaN never pauses.
DyingSeconds <= 0.0 transitions to Dead on frame 0; NaN never transitions.
BlendInSeconds negative/NaN invalid blend.
MaxClipRestarts negative disables restarts.
Standard 1.0e6f ceiling on all floats; 1000 on MaxClipRestarts.

## 6. What Can Be Validated Structurally vs What Stays UNRESOLVED
Structurally validated: finite-first, bounds, non-empty FNames, soft-path syntax.
UNRESOLVED: disk presence, live ability instance, bone placement, remains mesh.

## 7. Lifecycle Facts for the Configure Guard
Safe to assign before registration/BeginPlay. Constructor sets defaults.

## 8. Proposed Validation Contract, Order, and Diagnostic Tokens
Float finite checks in declaration order (NotFinite).
Float/int domain bounds in declaration order (NotPositive, Negative, AboveCeiling).
Syntactic FNames (Missing, Malformed).
Mode-dependent soft paths (Missing, Malformed).
```

</details>
