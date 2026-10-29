# Domain Proposal Sheet: URPGBossDeath (DD25 Proposal)

## 1. Component Overview & Source Locations
- **Header:** `Source/OneBossFight/Player/RPGBossDeath.h:42` (`class ONEBOSSFIGHT_API URPGBossDeath : public UActorComponent`)
- **Implementation:** `Source/OneBossFight/Player/RPGBossDeath.cpp`
- **Class Group:** `ClassGroup = (Boss)` (`RPGBossDeath.h:41`)
- **Primary Function:** Implements the boss's custom death presentation (G2-9, A-12) under Antigravity's `AN_Boss01_DeathLegend` animation (3.5 s total duration: boss collapses to knees by 2.5 s and holds slumped pose through the final second; `RPGBossDeath.h:29-31`). 
- **Dual Mode Architecture:**
  - `PackMontage` (`ERPGBossDeathMode::PackMontage` = 0): Reflects into the live pack death ability (`GA_EnemyRagdollDeath_C`) and writes `AM_Boss01_DeathLegend` into its `DeathMontages` array; the pack ability plays the montage and triggers its death flow (`RPGBossDeath.h:23-25`, `:32-34`).
  - `OwnClip` (`ERPGBossDeathMode::OwnClip` = 1): Plays `AN_Boss01_DeathLegend` directly through `RPGBossClips::Play`, pauses the pose at `HoldAtSeconds` (default 3.0 s), and suppresses the pack's physics ragdoll simulation each tick to prevent the corpse from being thrown (`RPGBossDeath.h:26-27`, `:34-36`).
- **Pack Lifecycle Contract (KI-083):**
  - The pack's ragdoll death ability destroys the dead boss actor approximately 4.35 s after death (`RPGBossDeath.h:30`, `:100`, `:126`).
  - `EndPlay` spawns static boss remains (`ARPGBossRemains::Spawn`) upon actor destruction (`RPGBossDeath.cpp:117-125`).

---

## 2. Real Authored Header Declarations (12 Authored Fields)
Directly extracted from `Source/OneBossFight/Player/RPGBossDeath.h`:

```cpp
// Source/OneBossFight/Player/RPGBossDeath.h:50-51
UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Death")
ERPGBossDeathMode DeathMode = ERPGBossDeathMode::PackMontage;

// Source/OneBossFight/Player/RPGBossDeath.h:53-55
/** The clip of OwnClip mode (Antigravity, on the mannequin skeleton). */
UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Death")
TSoftObjectPtr<UAnimSequence> DeathClip;

// Source/OneBossFight/Player/RPGBossDeath.h:57-59
/** The montage of PackMontage mode, made from the clip by Scripts/Editor/make_death_montage.py. */
UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Death")
TSoftObjectPtr<UAnimMontage> DeathMontage;

// Source/OneBossFight/Player/RPGBossDeath.h:61-63
/** Class name of the pack's death ability instance (a Blueprint instance in the boss's ability system component) and the name of its montage array. */
UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Death")
FName PackDeathAbilityClassName = TEXT("GA_EnemyRagdollDeath_C");

// Source/OneBossFight/Player/RPGBossDeath.h:65-66
UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Death")
FName PackDeathMontagesName = TEXT("DeathMontages");

// Source/OneBossFight/Player/RPGBossDeath.h:68-70
/** PackMontage: seconds between two looks at the ability's array (a pack that rebuilt its ability instances is caught here); the first look is one frame after BeginPlay and one frame after every encounter reset. */
UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Death", meta = (ClampMin = "0.1"))
float PackPollSeconds = 1.f;

// Source/OneBossFight/Player/RPGBossDeath.h:72-74
/** PackMontage: above 0 it is written into the EndTimeMultiplier field of the DeathMontages entry (the pack ends the ability at that fraction of the montage); 0 leaves the pack struct's own default. */
UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Death", meta = (ClampMin = "0.0"))
float PackEndTimeMultiplier = 0.f;

// Source/OneBossFight/Player/RPGBossDeath.h:76-78
/** Clip position (seconds) where the final pose is frozen: the clip is 3.5 s long and its frames are identical from 2.5 s on, so the pause shows the same pose as the end. */
UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Death", meta = (ClampMin = "0.1"))
float HoldAtSeconds = 3.f;

// Source/OneBossFight/Player/RPGBossDeath.h:80-82
/** Seconds from the death until the collapse is over (the clip is on its knees at 2.5 s): the state is "dying" until then and "dead" after. */
UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Death", meta = (ClampMin = "0.1"))
float DyingSeconds = 2.5f;

// Source/OneBossFight/Player/RPGBossDeath.h:84-85
UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Death", meta = (ClampMin = "0.0"))
float BlendInSeconds = 0.1f;

// Source/OneBossFight/Player/RPGBossDeath.h:87-89
/** OwnClip: how many times the clip is started again when something stops the montage (the pack's death flow, another clip) before the component gives up (it does not fight the pack for ever). */
UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Death", meta = (ClampMin = "0"))
int32 MaxClipRestarts = 8;

// Source/OneBossFight/Player/RPGBossDeath.h:91-93
/** PackMontage only: the death montage is paused at HoldAtSeconds and the ragdoll kept off, as in OwnClip. Off by default: the pack's ability may wait for the montage to end before it destroys the boss, and a paused montage would then keep the boss for ever. */
UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Death")
bool bGuardPackDeath = false;
```

---

## 3. Editor Metadata Audit (`ClampMin` is Not a Runtime Guard)

Five float fields and one integer field declare `meta = (ClampMin = ...)`:
- `PackPollSeconds`: `meta = (ClampMin = "0.1")` (`RPGBossDeath.h:69`)
- `PackEndTimeMultiplier`: `meta = (ClampMin = "0.0")` (`RPGBossDeath.h:73`)
- `HoldAtSeconds`: `meta = (ClampMin = "0.1")` (`RPGBossDeath.h:77`)
- `DyingSeconds`: `meta = (ClampMin = "0.1")` (`RPGBossDeath.h:81`)
- `BlendInSeconds`: `meta = (ClampMin = "0.0")` (`RPGBossDeath.h:84`)
- `MaxClipRestarts`: `meta = (ClampMin = "0")` (`RPGBossDeath.h:88`)

> [!IMPORTANT]
> **Editor metadata is NOT native runtime enforcement.**  
> `RPGBossDeath.cpp` performs ZERO runtime clamping (`FMath::Clamp`, `FMath::Max`) on `PackPollSeconds`, `PackEndTimeMultiplier`, `HoldAtSeconds`, `DyingSeconds`, `BlendInSeconds`, or `MaxClipRestarts` when reading them from the component. Negative, NaN, Infinite, or sub-ClampMin values pass directly into arithmetic comparisons unless guarded by the typed record contract.

---

## 4. Native Implementation & Execution Semantics (`RPGBossDeath.cpp`)

### 4.1 Lifecycle & Constructor
- **Constructor Defaults:**
  - `PrimaryComponentTick.bCanEverTick = true;` (`RPGBossDeath.cpp:33`).
  - `PrimaryComponentTick.bStartWithTickEnabled = true;` (`RPGBossDeath.cpp:34`).
  - `PrimaryComponentTick.TickInterval = 0.f;` (`RPGBossDeath.cpp:35`).
  - `DeathClip = TEXT("/Game/OneBossFight/Boss01/Animations/AN_Boss01_DeathLegend.AN_Boss01_DeathLegend")` (`RPGBossDeath.cpp:37`).
  - `DeathMontage = TEXT("/Game/OneBossFight/Boss01/Animations/AM_Boss01_DeathLegend.AM_Boss01_DeathLegend")` (`RPGBossDeath.cpp:38`).
- **Tick Prerequisites in `BeginPlay`:**
  - Sets `NextPackPoll = 0.0;` (`RPGBossDeath.cpp:100`).
  - Adds tick prerequisite components: `Stagger` (`:106`), `Posture` (`:110`), and `Phases` (`:114`) tick before `Death`, ensuring lethal hit state is observed on the same frame.
- **Synchronous Asset Preload on First Tick (`Preload`):**
  - First tick invokes `Preload()` (`RPGBossDeath.cpp:328`).
  - If `DeathMode == ERPGBossDeathMode::OwnClip`, synchronously loads `DeathClip.LoadSynchronous()` (`:136`, `:166`).
  - If `DeathMode == ERPGBossDeathMode::PackMontage`, synchronously loads `DeathMontage.LoadSynchronous()` (`:149`, `:170`).
- **Teardown in `EndPlay`:**
  - If actor destroyed while `State == EState::Dead`, invokes `ARPGBossRemains::Spawn(...)` (`RPGBossDeath.cpp:123`).
  - Sets `bEnding = true; bGuardActive = false;` (`:127-128`), completely releasing mesh physics and montage handles (respecting KI-083 pack destruction).

### 4.2 Pack Ability Reflection & Injection (`ApplyPackMontage`)
- In `PackMontage` mode, `PollPack(Now)` executes when `Now >= NextPackPoll` (`RPGBossDeath.cpp:219`).
- Next poll scheduled as: `NextPackPoll = Now + PackPollSeconds;` (`RPGBossDeath.cpp:223`).
- `ApplyPackMontage()` reflects into the live ability instance:
  - Finds `GA_EnemyRagdollDeath_C` on boss ASC (`:230`).
  - Finds array property `DeathMontages` (`:238`).
  - Supports both direct object arrays (`UAnimMontage*`) and pack struct arrays (`F_AbilityMontage`) via reflection (`:244-272`).
  - Empties array and inserts `[DeathMontage]` (`:295-300`).
  - If `PackEndTimeMultiplier > 0.f`, reflects into `EndTimeMultiplier` float property and assigns it (`:301-310`).

### 4.3 Death Edge Detection & Animation Flow
- Reads `Attribute.Health` via `RPGPack::ReadAttribute` (`RPGBossDeath.cpp:331`).
- Requires `bSeenAlive = true;` (`Health > 0.0`) before recognizing death (`:334-337`) to screen against PIE initialization zero-health transients (KI-081).
- Transition to `Dying` state (`BeginDeath`, `:362`):
  - Calls `URPGBossDormantWake::StopFor(GetOwner(), TEXT("death"))` (`:364`).
  - Preloads static remains assets (`ARPGBossRemains::PreloadAssets`, `:372`).
  - In `OwnClip` mode, launches `AN_Boss01_DeathLegend` via `RPGBossClips::Play` (`:380`, `:440`).
- State progression in `TickDeath` (`:416-429`):
  - `Age = Now - DeathTime;` (`:419`).
  - When `Age >= DyingSeconds`, transitions state from `Dying` to `Dead` (`:420-423`).
  - If `bGuardActive`:
    - `KeepPhysicsOff(Character)` (`:458`): checks `Mesh->IsAnySimulatingPhysics()`. If pack ragdoll enabled simulation, shuts it off (`SetAllBodiesSimulatePhysics(false)`, `SetSimulatePhysics(false)`) and teleports mesh back to capsule socket (`:464-474`).
    - `KeepClip(Character, Age)` (`:484`): if montage position reaches `HoldAtSeconds`, pauses montage (`Anim->Montage_Pause(Montage)`) (`:492-498`). If montage is stopped prematurely, restarts clip up to `MaxClipRestarts` times (`:508-522`).

---

## 5. Non-Finite Arithmetic & Degenerate Timing Analysis

`URPGBossDeath` contains 6 timing fields (5 floats, 1 int) directly involved in arithmetic and control flow:

| Field | Type | Native Arithmetic / Usage | Degenerate & Non-Finite Risks | Proposed Authored Bound |
| :--- | :--- | :--- | :--- | :--- |
| `PackPollSeconds` | `float` | `NextPackPoll = Now + PackPollSeconds` (`:223`) | NaN/Inf corrupts future poll time; `<= 0.0` causes poll to fire every single tick; huge value disables polling forever | Finite, strictly positive (`> 0.0f`), ceiling `1.0e6f` |
| `PackEndTimeMultiplier` | `float` | Written directly to pack struct property (`:307`) | NaN/Inf corrupts pack ability timing; negative multiplier produces undefined pack montage termination | Finite, non-negative (`>= 0.0f`), ceiling `1.0e6f` (`0.0` = pack default) |
| `HoldAtSeconds` | `float` | `Position >= HoldAtSeconds` (`:492`), clamped restart (`:519`) | NaN makes comparison always false (pause never triggers); `<= 0.0` freezes clip on frame 0 before collapse occurs | Finite, strictly positive (`> 0.0f`), ceiling `1.0e6f` |
| `DyingSeconds` | `float` | `Age >= DyingSeconds` (`:420`) | NaN prevents transition to `Dead`; `<= 0.0` marks corpse dead before animation begins | Finite, strictly positive (`> 0.0f`), ceiling `1.0e6f` |
| `BlendInSeconds` | `float` | Passed to `RPGBossClips::Play(..., BlendIn, ...)` (`:440`) | NaN/Inf causes montage playback failure; negative value causes invalid animation blend | Finite, non-negative (`>= 0.0f`), ceiling `1.0e6f` |
| `MaxClipRestarts` | `int32` | `RestartsThisDeath >= MaxClipRestarts` (`:508`) | Negative integer disables restarts completely; excessive value causes infinite restart loop fighting pack | Integer within `[0, 1000]` |

### Arithmetic Magnitude Ceiling (`MaxAuthoredMagnitude = 1.0e6f`):
- Consistent with DD21 (`Shockwave`) and DD22 (`HealPunish`), a `1.0e6f` ceiling (1 million seconds ≈ 11.5 days) screens float-extreme / overflow values without constraining gameplay tuning.
- For `PackEndTimeMultiplier`, `1.0e6` represents 1 million times montage length, which safely bounds any valid multiplier while rejecting float overflows.
- For `MaxClipRestarts`, an integer ceiling of `1000` bounds restart loops.

---

## 6. What Can Be Validated Structurally vs What Stays UNRESOLVED

### 6.1 Structurally Validated Offline (Typed Record Contract)
1. **`DeathMode` (Enum):**
   - Valid uint8 value corresponding to `ERPGBossDeathMode` (`0` = `PackMontage`, `1` = `OwnClip`).
2. **`DeathClip` (Soft Sequence Reference):**
   - In `OwnClip` mode: required (`InvalidDependency.Missing`), well-formed soft path per A-184 engine macros (`InvalidDependency.Malformed`).
   - In `PackMontage` mode: optional / ignored (or validated if set).
3. **`DeathMontage` (Soft Montage Reference):**
   - In `PackMontage` mode: required (`InvalidDependency.Missing`), well-formed soft path per A-184 engine macros (`InvalidDependency.Malformed`).
   - In `OwnClip` mode: optional / ignored.
4. **`PackDeathAbilityClassName` (FName):**
   - Not None, non-empty (`InvalidDependency.Missing`).
   - No whitespace or control characters (`InvalidDependency.Malformed`).
5. **`PackDeathMontagesName` (FName):**
   - Not None, non-empty (`InvalidDependency.Missing`).
   - No whitespace or control characters (`InvalidDependency.Malformed`).
6. **Numeric Timing Domains (Finite First):**
   - All 5 floats finite first (`InvalidDeath.NotFinite`).
   - `PackPollSeconds`: `> 0.0f`, `<= 1.0e6f` (`InvalidDeath.NotPositive`, `InvalidDeath.AboveCeiling`).
   - `PackEndTimeMultiplier`: `>= 0.0f`, `<= 1.0e6f` (`InvalidDeath.Negative`, `InvalidDeath.AboveCeiling`).
   - `HoldAtSeconds`: `> 0.0f`, `<= 1.0e6f` (`InvalidDeath.NotPositive`, `InvalidDeath.AboveCeiling`).
   - `DyingSeconds`: `> 0.0f`, `<= 1.0e6f` (`InvalidDeath.NotPositive`, `InvalidDeath.AboveCeiling`).
   - `BlendInSeconds`: `>= 0.0f`, `<= 1.0e6f` (`InvalidDeath.Negative`, `InvalidDeath.AboveCeiling`).
   - `MaxClipRestarts`: integer `>= 0`, `<= 1000` (`InvalidDeath.Negative`, `InvalidDeath.AboveCeiling`).
7. **Booleans:**
   - `bGuardPackDeath`: boolean (`true` or `false`).

### 6.2 UNRESOLVED Runtime Behavior (Typed Record Does NOT Prove)
- **Asset Existence on Disk:** That `AN_Boss01_DeathLegend` or `AM_Boss01_DeathLegend` exists, is cooked, or loads on disk.
- **Animation Timing Coherence:** That the animation file is actually 3.5 s long or that its collapse finishes at 2.5 s.
- **Pack Death Ability Presence:** That Blueprint `GA_EnemyRagdollDeath_C` exists, is granted to the ASC, or has a `DeathMontages` array property.
- **Attribute System Health Readback:** That `Attribute.Health` exists on the boss ability system component or reaches zero.
- **Remains Mesh Spawning:** That `ARPGBossRemains` meshes, materials, and Niagara bursts load or spawn in the level.
- **Actor Destruction Timing:** That the pack actually destroys the boss actor after ~4.35 s (KI-083).

---

## 7. Lifecycle Facts for the Configure Guard
- **Lifecycle Checks:**
  - Component must be exact class `URPGBossDeath::StaticClass()`.
  - Component must not be registered (`!Component.IsRegistered()`).
  - Component must not have begun play (`!Component.HasBegunPlay()`).
  - Owner actor must be live and not begun or beginning play (`!Owner->HasActorBegunPlay() && !Owner->IsActorBeginningPlay()`).
- **Assignment Safety:**
  - It is completely safe to assign the 12 authored fields before registration.
  - The constructor sets default paths and flags (`bStartWithTickEnabled = true`, `TickInterval = 0.f`), but performs ZERO disk IO, ZERO asset loads, and ZERO actor queries.
  - `Preload()` and `PollPack()` only execute during `BeginPlay` and `TickComponent`.
  - Assigning the 12 fields before registration completely configures the component before any tick or preload can execute.

---

## 8. Proposed Validation Contract, Order, and Diagnostic Tokens

Following the accepted DD19-DD22 pattern:

### (1) Float Finite Checks (Declaration Order)
All 5 floats finite first:
1. `PackPollSeconds` -> `InvalidDeath.NotFinite: Death.PackPollSeconds`
2. `PackEndTimeMultiplier` -> `InvalidDeath.NotFinite: Death.PackEndTimeMultiplier`
3. `HoldAtSeconds` -> `InvalidDeath.NotFinite: Death.HoldAtSeconds`
4. `DyingSeconds` -> `InvalidDeath.NotFinite: Death.DyingSeconds`
5. `BlendInSeconds` -> `InvalidDeath.NotFinite: Death.BlendInSeconds`

### (2) Float & Int Domain Bounds (Declaration Order)
6. `PackPollSeconds`: `> 0.0f` (`InvalidDeath.NotPositive`), `<= 1.0e6f` (`InvalidDeath.AboveCeiling`)
7. `PackEndTimeMultiplier`: `>= 0.0f` (`InvalidDeath.Negative`), `<= 1.0e6f` (`InvalidDeath.AboveCeiling`)
8. `HoldAtSeconds`: `> 0.0f` (`InvalidDeath.NotPositive`), `<= 1.0e6f` (`InvalidDeath.AboveCeiling`)
9. `DyingSeconds`: `> 0.0f` (`InvalidDeath.NotPositive`), `<= 1.0e6f` (`InvalidDeath.AboveCeiling`)
10. `BlendInSeconds`: `>= 0.0f` (`InvalidDeath.Negative`), `<= 1.0e6f` (`InvalidDeath.AboveCeiling`)
11. `MaxClipRestarts`: `>= 0` (`InvalidDeath.Negative`), `<= 1000` (`InvalidDeath.AboveCeiling`)

### (3) Syntactic FNames
12. `PackDeathAbilityClassName`: not None (`InvalidDependency.Missing: Death.PackDeathAbilityClassName`), no whitespace/control (`InvalidDependency.Malformed: Death.PackDeathAbilityClassName`)
13. `PackDeathMontagesName`: not None (`InvalidDependency.Missing: Death.PackDeathMontagesName`), no whitespace/control (`InvalidDependency.Malformed: Death.PackDeathMontagesName`)

### (4) Mode-Dependent Soft Path References
14. If `DeathMode == ERPGBossDeathMode::OwnClip` (or both validated):
    - `DeathClip`: not null (`InvalidDependency.Missing: Death.DeathClip`), well-formed soft path (`InvalidDependency.Malformed: Death.DeathClip`)
15. If `DeathMode == ERPGBossDeathMode::PackMontage` (or both validated):
    - `DeathMontage`: not null (`InvalidDependency.Missing: Death.DeathMontage`), well-formed soft path (`InvalidDependency.Malformed: Death.DeathMontage`)

### (5) Enum & Boolean Values
16. `DeathMode`: must be valid enum `0` (`PackMontage`) or `1` (`OwnClip`)
17. `bGuardPackDeath`: accepts `true` and `false`
