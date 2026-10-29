# Native Derivation Dossier: RPGBossDeath

## 1. Component Overview & File Locations
- **Header:** `Source/OneBossFight/Player/RPGBossDeath.h`
- **Source:** `Source/OneBossFight/Player/RPGBossDeath.cpp`
- **Class:** `URPGBossDeath` (`UActorComponent`)
- **Primary Function:** Governs boss death presentation (G2-9, A-12, KI-083). Supports two operating modes:
  1. `PackMontage`: Injects authored montage (`AM_Boss01_DeathLegend`) into the pack's `GA_EnemyRagdollDeath_C` ability via reflection, letting the pack drive the death sequence.
  2. `OwnClip`: Plays `AN_Boss01_DeathLegend` directly through `RPGBossClips`, holds the kneeling pose at `HoldAtSeconds`, and disables mesh physics simulation to prevent ragdoll collapse.
  Spawns `ARPGBossRemains` on actor destruction during `EndPlay()`.

---

## 2. Exact Public Authored Fields
Directly extracted from `Source/OneBossFight/Player/RPGBossDeath.h`:

```cpp
// Source/OneBossFight/Player/RPGBossDeath.h:51
UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Death")
ERPGBossDeathMode DeathMode = ERPGBossDeathMode::PackMontage;

// Source/OneBossFight/Player/RPGBossDeath.h:55
UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Death")
TSoftObjectPtr<UAnimSequence> DeathClip;

// Source/OneBossFight/Player/RPGBossDeath.h:59
UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Death")
TSoftObjectPtr<UAnimMontage> DeathMontage;

// Source/OneBossFight/Player/RPGBossDeath.h:63
UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Death")
FName PackDeathAbilityClassName = TEXT("GA_EnemyRagdollDeath_C");

// Source/OneBossFight/Player/RPGBossDeath.h:66
UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Death")
FName PackDeathMontagesName = TEXT("DeathMontages");

// Source/OneBossFight/Player/RPGBossDeath.h:70
UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Death", meta = (ClampMin = "0.1"))
float PackPollSeconds = 1.f;

// Source/OneBossFight/Player/RPGBossDeath.h:74
UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Death", meta = (ClampMin = "0.0"))
float PackEndTimeMultiplier = 0.f;

// Source/OneBossFight/Player/RPGBossDeath.h:78
UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Death", meta = (ClampMin = "0.1"))
float HoldAtSeconds = 3.f;

// Source/OneBossFight/Player/RPGBossDeath.h:82
UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Death", meta = (ClampMin = "0.1"))
float DyingSeconds = 2.5f;

// Source/OneBossFight/Player/RPGBossDeath.h:85
UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Death", meta = (ClampMin = "0.0"))
float BlendInSeconds = 0.1f;

// Source/OneBossFight/Player/RPGBossDeath.h:89
UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Death", meta = (ClampMin = "0"))
int32 MaxClipRestarts = 8;

// Source/OneBossFight/Player/RPGBossDeath.h:93
UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Death")
bool bGuardPackDeath = false;
```

*Constructor Soft Path Initializers (`Source/OneBossFight/Player/RPGBossDeath.cpp:37-38`):*
```cpp
DeathClip = TSoftObjectPtr<UAnimSequence>(FSoftObjectPath(TEXT("/Game/OneBossFight/Boss01/Animations/AN_Boss01_DeathLegend.AN_Boss01_DeathLegend")));
DeathMontage = TSoftObjectPtr<UAnimMontage>(FSoftObjectPath(TEXT("/Game/OneBossFight/Boss01/Animations/AM_Boss01_DeathLegend.AM_Boss01_DeathLegend")));
```

Total authored fields: **12**.

---

## 3. Code Readings & Extreme Handling (Read From Code)

### `DeathMode` (`ERPGBossDeathMode`, default `PackMontage`)
- **Read Locations:**
  - `Source/OneBossFight/Player/RPGBossDeath.cpp:69`: in `GetDeathModeName()`.
  - `Source/OneBossFight/Player/RPGBossDeath.cpp:164`: `if (DeathMode == ERPGBossDeathMode::OwnClip) { GetClip(); } else { GetMontage(); }` in `Preload()`.
  - `Source/OneBossFight/Player/RPGBossDeath.cpp:343`: `if (DeathMode == ERPGBossDeathMode::PackMontage) { PollPack(Now); }` in `TickComponent()`.
  - `Source/OneBossFight/Player/RPGBossDeath.cpp:377`: `if (DeathMode == ERPGBossDeathMode::OwnClip)` in `BeginDeath()`.
  - `Source/OneBossFight/Player/RPGBossDeath.cpp:403`: in `EndDeathState()`.
  - `Source/OneBossFight/Player/RPGBossDeath.cpp:503`: `if (DeathMode != ERPGBossDeathMode::OwnClip) { return; }` in `KeepClip()`.
- **Extremes (Read From Code):**
  - Enum has two valid states: `ERPGBossDeathMode::PackMontage` (0) and `ERPGBossDeathMode::OwnClip` (1). In `PackMontage`, the component delegates playback to the pack ability and polls. In `OwnClip`, the component plays the clip directly and guards the mesh.

### `DeathClip` (`TSoftObjectPtr<UAnimSequence>`)
- **Read Location:**
  - `Source/OneBossFight/Player/RPGBossDeath.cpp:137`: `LoadedClip = DeathClip.LoadSynchronous();` in `GetClip()`.
- **Extremes (Read From Code):**
  - Invalid / Empty Path: Returns `nullptr` and logs warning (`RPGBossDeath.cpp:140`). In `OwnClip` mode, `StartOwnClip()` fails (`RPGBossDeath.cpp:435`), `bGuardActive` is set to false, and the pack's default death runs unguarded.

### `DeathMontage` (`TSoftObjectPtr<UAnimMontage>`)
- **Read Location:**
  - `Source/OneBossFight/Player/RPGBossDeath.cpp:151`: `LoadedMontage = DeathMontage.LoadSynchronous();` in `GetMontage()`.
- **Extremes (Read From Code):**
  - Invalid / Empty Path: Returns `nullptr` and logs warning (`RPGBossDeath.cpp:154`). In `PackMontage` mode, `ApplyPackMontage()` records `NotePackMiss(TEXT("the death montage did not load"))` (`RPGBossDeath.cpp:237`), leaving the ability array untouched.

### `PackDeathAbilityClassName` (`FName`, default `TEXT("GA_EnemyRagdollDeath_C")`)
- **Read Location:**
  - `Source/OneBossFight/Player/RPGBossDeath.cpp:229`: `UObject* Ability = FindAbilityByClassName(GetOwner(), PackDeathAbilityClassName);` in `ApplyPackMontage()`.
- **Extremes (Read From Code):**
  - `NAME_None` or unassigned: `FindAbilityByClassName` returns `nullptr`; `NotePackMiss()` logs that no ability was found; pack montage cannot be injected.

### `PackDeathMontagesName` (`FName`, default `TEXT("DeathMontages")`)
- **Read Location:**
  - `Source/OneBossFight/Player/RPGBossDeath.cpp:239`: `const FArrayProperty* Array = FindFProperty<FArrayProperty>(Ability->GetClass(), PackDeathMontagesName);` in `ApplyPackMontage()`.
- **Extremes (Read From Code):**
  - `NAME_None` or unassigned: Property not found on ability class; returns pack miss; montage array remains untouched.

### `PackPollSeconds` (`float`, default `1.f`)
- **Read Location:**
  - `Source/OneBossFight/Player/RPGBossDeath.cpp:223`: `NextPackPoll = Now + PackPollSeconds;` in `PollPack()`.
- **Extremes (Read From Code):**
  - `<= 0.0f`: `NextPackPoll` is set to current or past time. `ApplyPackMontage()` executes on every single frame, incurring heavy reflection overhead (`FindFProperty`, `FScriptArrayHelper`, `TFieldIterator`).
  - Huge (`>= 3600.f`): If the pack ability instance is reconstructed mid-fight, it will not be updated within the session.

### `PackEndTimeMultiplier` (`float`, default `0.f`)
- **Read Locations:**
  - `Source/OneBossFight/Player/RPGBossDeath.cpp:296`: `if (PackEndTimeMultiplier > 0.f)` in `ApplyPackMontage()`.
  - `Source/OneBossFight/Player/RPGBossDeath.cpp:303`: `Number->SetFloatingPointPropertyValue(..., static_cast<double>(PackEndTimeMultiplier));`
- **Extremes (Read From Code):**
  - `<= 0.0f`: The check `PackEndTimeMultiplier > 0.f` evaluates false; the pack struct's existing `EndTimeMultiplier` default is left unchanged.
  - `> 0.0f`: Overwrites the `EndTimeMultiplier` field on the live `F_AbilityMontage` struct.

### `HoldAtSeconds` (`float`, default `3.f`)
- **Read Locations:**
  - `Source/OneBossFight/Player/RPGBossDeath.cpp:446`: `if (StartAt >= HoldAtSeconds) { Anim->Montage_Pause(Montage); bPoseHeld = true; ... }` in `StartOwnClip()`.
  - `Source/OneBossFight/Player/RPGBossDeath.cpp:494`: `if (!bPoseHeld && Anim->Montage_GetPosition(Montage) >= HoldAtSeconds) { Anim->Montage_Pause(Montage); ... }` in `KeepClip()`.
  - `Source/OneBossFight/Player/RPGBossDeath.cpp:519`: `const float StartAt = FMath::Clamp(static_cast<float>(Age), 0.f, HoldAtSeconds);` in `KeepClip()`.
- **Extremes (Read From Code):**
  - `<= 0.0f`: The animation pauses on frame 0; boss freezes upright at the moment of death.
  - Exceeds clip length: Montage finishes naturally; if non-looping, blends out or snaps to reference pose before pause is reached.

### `DyingSeconds` (`float`, default `2.5f`)
- **Read Location:**
  - `Source/OneBossFight/Player/RPGBossDeath.cpp:419`: `if (State == EState::Dying && Age >= DyingSeconds) { State = EState::Dead; ... }` in `TickDeath()`.
- **Extremes (Read From Code):**
  - `<= 0.0f`: State transitions from `Dying` to `Dead` on the first tick after death is detected.
  - Huge: Boss stays in `Dying` state indefinitely.

### `BlendInSeconds` (`float`, default `0.1f`)
- **Read Location:**
  - `Source/OneBossFight/Player/RPGBossDeath.cpp:439`: `RPGBossClips::Play(Character, Clip, StartAt > 0.f ? 0.f : BlendInSeconds, 0.f, 1.f, 1, StartAt);` in `StartOwnClip()`.
- **Extremes (Read From Code):**
  - `0.0f`: Instant snap cut into death clip without cross-fade.
  - Huge (`>= 5.0f`): Excessive cross-fade time results in slow, unreadable blending between combat pose and death animation.

### `MaxClipRestarts` (`int32`, default `8`)
- **Read Location:**
  - `Source/OneBossFight/Player/RPGBossDeath.cpp:508`: `if (RestartsThisDeath >= MaxClipRestarts) { ... return; }` in `KeepClip()`.
- **Extremes (Read From Code):**
  - `<= 0`: If the pack's death flow or ragdoll stops the montage once, the component will never attempt to restart it.
  - Huge (`>= 1000`): Keeps fighting external montage stoppers continuously every frame.

### `bGuardPackDeath` (`bool`, default `false`)
- **Read Location:**
  - `Source/OneBossFight/Player/RPGBossDeath.cpp:389`: `bGuardActive = bGuardPackDeath;` in `BeginDeath()` under `PackMontage` mode.
- **Extremes (Read From Code):**
  - `false`: Under `PackMontage`, `bGuardActive` is false; physics is not suppressed and montage is not frozen, letting the pack's native ragdoll proceed.
  - `true`: Forces `KeepPhysicsOff()` and `KeepClip()` even when using `PackMontage` mode.

---

## 4. External Dependencies
Directly cited from `Source/OneBossFight/Player/RPGBossDeath.cpp`:

1. **Tick Prerequisites (`URPGBossStagger`, `URPGBossPosture`, `URPGBossPhases`):**
   - Lookup: `Source/OneBossFight/Player/RPGBossDeath.cpp:103-114`:
     ```cpp
     if (URPGBossStagger* Stagger = GetOwner()->FindComponentByClass<URPGBossStagger>()) { AddTickPrerequisiteComponent(Stagger); }
     if (URPGBossPosture* Posture = GetOwner()->FindComponentByClass<URPGBossPosture>()) { AddTickPrerequisiteComponent(Posture); }
     if (URPGBossPhases* Phases = GetOwner()->FindComponentByClass<URPGBossPhases>()) { AddTickPrerequisiteComponent(Phases); }
     ```
   - Purpose: Ensures components that can trigger death tick before `RPGBossDeath`, preventing free ragdoll frames.

2. **`URPGBossEncounter` (Component Lookup):**
   - Lookup: `Source/OneBossFight/Player/RPGBossDeath.cpp:212`: `const URPGBossEncounter* Encounter = GetOwner()->FindComponentByClass<URPGBossEncounter>();`
   - Reads: `Encounter->GetResetCount()`. Forces immediate poll on reset count change.

3. **`URPGBossDormantWake` (Static Call):**
   - Call: `Source/OneBossFight/Player/RPGBossDeath.cpp:362`: `URPGBossDormantWake::StopFor(GetOwner(), TEXT("death"));`

4. **`ARPGBossRemains` (Static Lifecycle Calls):**
   - Call: `Source/OneBossFight/Player/RPGBossDeath.cpp:123`: `ARPGBossRemains::Spawn(...)` in `EndPlay()`.
   - Call: `Source/OneBossFight/Player/RPGBossDeath.cpp:372`: `ARPGBossRemains::PreloadAssets(...)` in `BeginDeath()`.
   - Call: `Source/OneBossFight/Player/RPGBossDeath.cpp:399`: `ARPGBossRemains::DestroyForWorld(GetWorld())` in `EndDeathState()`.

5. **`RPGBossClips` (Playback Helper):**
   - Call: `Source/OneBossFight/Player/RPGBossDeath.cpp:439`: `RPGBossClips::Play(...)`.

6. **Ability System Reflection (`Pack/RPGBlueprintCall.h`):**
   - Lookup: `Source/OneBossFight/Player/RPGBossDeath.cpp:229`: `FindAbilityByClassName(GetOwner(), PackDeathAbilityClassName)`.
   - Reflection: Uses `FindFProperty<FArrayProperty>`, `FScriptArrayHelper`, `TFieldIterator<FProperty>` to inspect and mutate the pack's `F_AbilityMontage` array in-memory.

7. **Authored Soft Paths:**
   - `DeathClip`: `TSoftObjectPtr<UAnimSequence>`
   - `DeathMontage`: `TSoftObjectPtr<UAnimMontage>`
   - Both provable structurally offline via soft path syntax and filesystem existence checks.

---

## 5. Proposed Typed Domain

| Field | Type | Domain / Constraints | Label | Derivation Reason |
|---|---|---|---|---|
| `DeathMode` | `ERPGBossDeathMode` | `PackMontage`, `OwnClip` | **NATIVE-DERIVED** | Header enum definition (`RPGBossDeath.h:20-27`). |
| `DeathClip` | `TSoftObjectPtr<UAnimSequence>` | Valid soft path, ends with `.AN_Boss01_DeathLegend` or matching object name | **NATIVE-DERIVED** | Synchronously loaded in `GetClip()` (`RPGBossDeath.cpp:137`). |
| `DeathMontage` | `TSoftObjectPtr<UAnimMontage>` | Valid soft path, ends with `.AM_Boss01_DeathLegend` or matching object name | **NATIVE-DERIVED** | Synchronously loaded in `GetMontage()` (`RPGBossDeath.cpp:151`). |
| `PackDeathAbilityClassName` | `FName` | Non-empty `FName`, matches `^[A-Za-z0-9_]+$` | **NATIVE-DERIVED** | Target class for ability reflection (`RPGBossDeath.cpp:229`). |
| `PackDeathMontagesName` | `FName` | Non-empty `FName`, matches `^[A-Za-z0-9_]+$` | **NATIVE-DERIVED** | Target array property for reflection (`RPGBossDeath.cpp:239`). |
| `PackPollSeconds` | `float` | `0.1f <= PackPollSeconds <= 60.0f` (finite) | **NATIVE-DERIVED** | Header `ClampMin="0.1"`. Controls reflection poll frequency (`RPGBossDeath.cpp:223`). |
| `PackEndTimeMultiplier` | `float` | `0.0f <= PackEndTimeMultiplier <= 10.0f` (finite) | **NATIVE-DERIVED** | Header `ClampMin="0.0"`. `0.0f` skips overwrite (`RPGBossDeath.cpp:296`). |
| `HoldAtSeconds` | `float` | `0.1f <= HoldAtSeconds <= 30.0f` (finite) | **NATIVE-DERIVED** | Header `ClampMin="0.1"`. Position to freeze montage (`RPGBossDeath.cpp:446, 494`). |
| `DyingSeconds` | `float` | `0.1f <= DyingSeconds <= 30.0f` (finite) | **NATIVE-DERIVED** | Header `ClampMin="0.1"`. Transition time from Dying to Dead (`RPGBossDeath.cpp:419`). |
| `BlendInSeconds` | `float` | `0.0f <= BlendInSeconds <= 2.0f` (finite) | **NATIVE-DERIVED** | Header `ClampMin="0.0"`. Blend duration for `RPGBossClips::Play()` (`RPGBossDeath.cpp:439`). |
| `MaxClipRestarts` | `int32` | `0 <= MaxClipRestarts <= 50` | **NATIVE-DERIVED** | Header `ClampMin="0"`. Maximum restart attempts (`RPGBossDeath.cpp:508`). |
| `bGuardPackDeath` | `bool` | `{true, false}` | **NATIVE-DERIVED** | Guard toggle in `PackMontage` mode (`RPGBossDeath.cpp:389`). |

*Unresolved Items:*
- Health attribute tag `DeathHealthTag` is hardcoded as `TEXT("Attribute.Health")` in anonymous namespace (`RPGBossDeath.cpp:28`). It is not an authored property.
- Mesh placement and remains assets are handled via runtime caches (`ARPGBossRemains`), not authored fields.

---

## 6. Lifecycle Facts & Configure Guard Rules
- **Component Tick:** `PrimaryComponentTick.bCanEverTick = true; PrimaryComponentTick.TickInterval = 0.f;` (`RPGBossDeath.cpp:33-35`).
- **BeginPlay (`RPGBossDeath.cpp:97-115`):**
  - Resets `NextPackPoll = 0.0; LastResetCount = -1;`.
  - Registers tick prerequisite components (`Stagger`, `Posture`, `Phases`).
- **First Tick Preload (`RPGBossDeath.cpp:327-329`):**
  - First tick invokes `Preload()`, which synchronously loads `DeathClip` (if `OwnClip`) or `DeathMontage` (if `PackMontage`).
- **EndPlay (`RPGBossDeath.cpp:117-130`):**
  - If `State == EState::Dead` and destroyed, spawns `ARPGBossRemains`. Sets `bEnding = true; bGuardActive = false;`.
- **Runtime State Fields (MUST NOT be overwritten or touched during runtime configure):**
  - `bool bEnding`, `bSeenAlive`, `bPreloaded`, `bClipTried`, `bMontageTried` (`RPGBossDeath.h:184-188`)
  - `EState State`, `double DeathTime`, `double NextPackPoll`, `int32 LastResetCount` (`RPGBossDeath.h:189-192`)
  - `int32 DeathCount`, `ClipPlayCount`, `ClipRestartCount`, `RestartsThisDeath`, `PoseHoldCount`, `PhysicsOffCount`, `PackSetCount`, `PackMissCount` (`RPGBossDeath.h:193-200`)
  - `bool bPoseHeld`, `bGuardActive` (`RPGBossDeath.h:201-203`)
  - `FString LastPackResult`, `TWeakObjectPtr<UAnimMontage> ClipMontage` (`RPGBossDeath.h:204-205`)
  - Mesh placement variables: `bMeshPlacementKnown`, `MeshParent`, `MeshSocket`, `MeshRelativeLocation`, `MeshRelativeRotation`, `bRemainsTransformKnown`, `LastRemainsTransform` (`RPGBossDeath.h:208-214`)
  - Transient asset pointers: `LoadedRemainsMesh`, `LoadedRemainsMaterial`, `LoadedRemainsBurst`, `LoadedClip`, `LoadedMontage` (`RPGBossDeath.h:216-230`)
- **Configure Guard Constraint:** Changing `DeathMode` or soft paths while `State != EState::Alive` is prohibited; could result in mismatched physics/montage cleanup or dangling pose holds.
