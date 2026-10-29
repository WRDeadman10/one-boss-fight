# Domain Proposal Sheet: URPGBossCloseClipSwap (DD24 Proposal)

## 1. Component Overview & Source Locations
- **Header:** `Source/OneBossFight/Player/RPGBossCloseClipSwap.h:18` (`class ONEBOSSFIGHT_API URPGBossCloseClipSwap : public UActorComponent`)
- **Implementation:** `Source/OneBossFight/Player/RPGBossCloseClipSwap.cpp`
- **Helper Rules:** `Source/OneBossFight/Player/RPGBossCloseClipSwapRules.h`
- **Class Group:** `ClassGroup = (Boss)` (`RPGBossCloseClipSwap.h:17`)
- **Primary Function:** Replaces only the created pack close-attack ability's (`GA_GS_Boss_CloseAttack_C`) A1 and A3 montage entries with project-owned authored montages (`AM_Boss01_A1`, `AM_Boss01_A3a`, `AM_Boss01_A3b`), leaving A1b (`GS_Attack04_Montage`) as the pack fallback (`RPGBossCloseClipSwap.h:11-14`, `RPGBossCloseClipSwapRules.h:10-16`). The pack ability continues selecting stages, providing attack data, and driving trace/follow-up notifies (`RPGBossCloseClipSwap.h:12-14`). A missing or changed pack property fails open: its original montage entries are left untouched (`RPGBossCloseClipSwap.h:13-14`).

---

## 2. Real Authored Header Declarations (5 Authored Fields)
Directly extracted from `Source/OneBossFight/Player/RPGBossCloseClipSwap.h`:

```cpp
// Source/OneBossFight/Player/RPGBossCloseClipSwap.h:25-26
UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Close clips")
FName CloseAbilityClassName = TEXT("GA_GS_Boss_CloseAttack_C");

// Source/OneBossFight/Player/RPGBossCloseClipSwap.h:28-29
UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Close clips")
FName AttackMontagesName = TEXT("AttackMontages");

// Source/OneBossFight/Player/RPGBossCloseClipSwap.h:31-32
UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Close clips")
TSoftObjectPtr<UAnimMontage> A1Montage;

// Source/OneBossFight/Player/RPGBossCloseClipSwap.h:34-35
UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Close clips")
TSoftObjectPtr<UAnimMontage> A3aMontage;

// Source/OneBossFight/Player/RPGBossCloseClipSwap.h:37-38
UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Close clips")
TSoftObjectPtr<UAnimMontage> A3bMontage;
```

### Editor Metadata Note:
- `ClampMin` and `ClampMax` are editor metadata specifiers that apply strictly to numeric properties (floats, integers).
- None of the 5 authored properties of `URPGBossCloseClipSwap` declare `meta = (ClampMin = ...)` or `meta = (ClampMax = ...)` in `Source/OneBossFight/Player/RPGBossCloseClipSwap.h`.
- There are ZERO numeric fields (float, double, int) in `URPGBossCloseClipSwap`.
- No arithmetic ceiling, finite check, or magnitude bound is needed or applicable to this component.

---

## 3. Native Implementation & Execution Semantics (`RPGBossCloseClipSwap.cpp`)

### 3.1 Lifecycle & Constructor
- **Tick Configuration in Constructor:**
  - `PrimaryComponentTick.bCanEverTick = true;` (`RPGBossCloseClipSwap.cpp:41`).
  - `PrimaryComponentTick.TickInterval = 0.25f;` (`RPGBossCloseClipSwap.cpp:42`).
  - Constructor sets default soft object paths:
    - `A1Montage = TEXT("/Game/OneBossFight/Boss01/Animations/AM_Boss01_A1.AM_Boss01_A1")` (`RPGBossCloseClipSwap.cpp:43`).
    - `A3aMontage = TEXT("/Game/OneBossFight/Boss01/Animations/AM_Boss01_A3a.AM_Boss01_A3a")` (`RPGBossCloseClipSwap.cpp:44`).
    - `A3bMontage = TEXT("/Game/OneBossFight/Boss01/Animations/AM_Boss01_A3b.AM_Boss01_A3b")` (`RPGBossCloseClipSwap.cpp:45`).
- **Deferred Preload in `BeginPlay`:**
  - `Super::BeginPlay();` (`RPGBossCloseClipSwap.cpp:50`).
  - Calls `Preload();` synchronously (`RPGBossCloseClipSwap.cpp:51`).
  - Finds `URPGBossEncounter` on owner; if found, caches `LastResetCount` and establishes tick dependency: `AddTickPrerequisiteComponent(Encounter);` (`RPGBossCloseClipSwap.cpp:52-56`).
- **Game-Thread Synchronous Asset Loading in `Preload()`:**
  - `LoadedA1 = A1Montage.LoadSynchronous();` (`RPGBossCloseClipSwap.cpp:67`).
  - `LoadedA3a = A3aMontage.LoadSynchronous();` (`RPGBossCloseClipSwap.cpp:68`).
  - `LoadedA3b = A3bMontage.LoadSynchronous();` (`RPGBossCloseClipSwap.cpp:69`).
  - **Permanent Failure Guard:**
    - If `!LoadedA1 || !LoadedA3a || !LoadedA3b`, sets `bPermanentFailure = true;` (`RPGBossCloseClipSwap.cpp:72`), logs warning (`:74`), and the component permanently locks out from any swap attempts.
- **Teardown in `EndPlay`:**
  - Calls `Restore(TEXT("EndPlay"));` (`RPGBossCloseClipSwap.cpp:61`), reverting live ability array entries back to original pack montages.

### 3.2 Polling, Live Ability Discovery, and In-Memory Mutation
- **`TickComponent` Polling Loop:**
  - Runs every `0.25f` seconds (`RPGBossCloseClipSwap.cpp:42`).
  - Checks `URPGBossEncounter::GetResetCount()`: on encounter reset, calls `Restore(TEXT("encounter reset"))` (`RPGBossCloseClipSwap.cpp:111-115`).
  - Early returns if `!bEnabledForTest || bPermanentFailure || (Encounter && Encounter->IsDormant())` (`RPGBossCloseClipSwap.cpp:117-120`).
  - Checks `URPGBossDeath::IsDeathActive()`: on death, calls `Restore(TEXT("boss death"))` and returns (`RPGBossCloseClipSwap.cpp:121-125`).
  - Polling throttle: advances `RetrySeconds += DeltaTime;` if `!bApplied && RetrySeconds >= 0.5f`, resets timer and calls `TryApply()` (`RPGBossCloseClipSwap.cpp:127-132`).
- **Live Reflection in `TryApply()`:**
  - Looks up live ability instance: `UObject* Ability = FindAbilityByClassName(GetOwner(), CloseAbilityClassName);` (`RPGBossCloseClipSwap.cpp:139`). If not yet granted, sets `LastResult = "waiting for ..."` and returns false (non-fatal, will retry).
  - Reflects into ability class: `FindFProperty<FArrayProperty>(Ability->GetClass(), AttackMontagesName);` (`RPGBossCloseClipSwap.cpp:145`).
  - Reflects into element struct: `FindMontageField(Array)` searches for an `FObjectPropertyBase` starting with `TEXT("AnimMontage")` whose class is a child of `UAnimMontage` (`RPGBossCloseClipSwap.cpp:20-38`, `:146`).
  - If array or montage field is missing: triggers permanent failure (`bPermanentFailure = true`, `:149`), logs warning, and abandons (`:150-152`).
  - Validates exact array length: `Entries.Num() != 4` triggers permanent failure (`RPGBossCloseClipSwap.cpp:155-160`).
  - Validates elements against pack rules: each element must be non-null and pass `RPGBossCloseClipSwapRules::IsPackCloseMontage(Current->GetFName())` (`:167-173`).
  - Validates exact replacement count: must map exactly 3 candidate swaps (`Candidates.Num() != 3`, `:194`) covering `GS_Attack03_Montage`, `GS_Attack01_Montage`, and `GS_Attack02_Montage` (`:195-197`).
  - Mutates live ability entries in memory: `MontageField->SetObjectPropertyValue(...)` (`RPGBossCloseClipSwap.cpp:207`).
  - Sets `bApplied = true;` and increments `ApplyCount;` (`RPGBossCloseClipSwap.cpp:211-212`).

---

## 4. What Can Be Validated Structurally vs What Stays UNRESOLVED

### 4.1 Structurally Validated Offline (Typed Record Contract)
1. **`CloseAbilityClassName` (FName):**
   - Syntactic identity: not `None`, non-empty (`InvalidDependency.Missing`).
   - Lexical structure: no whitespace, control characters, or invalid FName characters (`InvalidDependency.Malformed`).
2. **`AttackMontagesName` (FName):**
   - Syntactic identity: not `None`, non-empty (`InvalidDependency.Missing`).
   - Lexical structure: no whitespace, control characters, or invalid FName characters (`InvalidDependency.Malformed`).
3. **`A1Montage` (Soft Object Path):**
   - Required reference: not null, non-empty (`InvalidDependency.Missing`).
   - Structural soft path: starts with `'/'`, names a package folder, ends in `<package>.<asset>`, passes UE 5.5 `INVALID_OBJECTNAME_CHARACTERS` / `INVALID_LONGPACKAGE_CHARACTERS` macros (`InvalidDependency.Malformed`).
4. **`A3aMontage` (Soft Object Path):**
   - Required reference: not null, non-empty (`InvalidDependency.Missing`).
   - Structural soft path: well-formed per engine macros (`InvalidDependency.Malformed`).
5. **`A3bMontage` (Soft Object Path):**
   - Required reference: not null, non-empty (`InvalidDependency.Missing`).
   - Structural soft path: well-formed per engine macros (`InvalidDependency.Malformed`).
6. **Cross-Field Uniqueness (Authored Choice):**
   - Duplicate soft paths between `A1Montage`, `A3aMontage`, and `A3bMontage` are refused (`InvalidDependency.Duplicate`). Mapping identical replacement montages to different attack stages is an authoring defect that would collapse distinct combat timings.

### 4.2 UNRESOLVED Runtime Behavior (Typed Record Does NOT Prove)
- **Asset Existence on Disk:** That `AM_Boss01_A1`, `AM_Boss01_A3a`, or `AM_Boss01_A3b` exists, is cooked, or loads successfully (runtime load failure logs warning and retains pack fallback per `RPGBossCloseClipSwap.cpp:70-75`).
- **Animation Skeleton Compatibility:** That the replacement montages match the mannequin skeleton or have valid notify tracks.
- **Pack Ability Presence:** That the Blueprint class `GA_GS_Boss_CloseAttack_C` is actually loaded, granted to the boss ASC, or active in gameplay.
- **Pack Property Schema Parity:** That the live ability has an array named `AttackMontages` with exactly 4 entries of struct `F_AbilityMontage`.
- **Gameplay Attack Delivery:** That close attacks ever fire, that collision traces execute, or that damage notifies register on the player.

---

## 5. Lifecycle Facts for the Configure Guard
- **Lifecycle Checks:**
  - Component must be a live pointer of exact class `URPGBossCloseClipSwap::StaticClass()`.
  - Component must not be registered (`!Component.IsRegistered()`).
  - Component must not have begun play (`!Component.HasBegunPlay()`).
  - Owner actor must be live and not begun or beginning play (`!Owner->HasActorBegunPlay() && !Owner->IsActorBeginningPlay()`).
- **Assignment Safety:**
  - It is completely safe to assign the 5 authored fields before registration.
  - The constructor sets default paths and tick interval `0.25f`, but performs ZERO disk IO, ZERO asset loads, and ZERO object allocations.
  - `Preload()` and `TryApply()` only execute during `BeginPlay` and `TickComponent`.
  - Assigning the 5 fields before registration completely configures the component before any tick or preload can execute.

---

## 6. Proposed Validation Contract, Order, and Diagnostic Tokens

Following the accepted DD19-DD22 pattern:

| Step | Field | Constraint | Diagnostic Token |
| :--- | :--- | :--- | :--- |
| 1 | `CloseClipSwap.CloseAbilityClassName` | Not `None`, non-empty | `InvalidDependency.Missing: CloseClipSwap.CloseAbilityClassName` |
| 2 | `CloseClipSwap.CloseAbilityClassName` | No whitespace or control characters | `InvalidDependency.Malformed: CloseClipSwap.CloseAbilityClassName` |
| 3 | `CloseClipSwap.AttackMontagesName` | Not `None`, non-empty | `InvalidDependency.Missing: CloseClipSwap.AttackMontagesName` |
| 4 | `CloseClipSwap.AttackMontagesName` | No whitespace or control characters | `InvalidDependency.Malformed: CloseClipSwap.AttackMontagesName` |
| 5 | `CloseClipSwap.A1Montage` | Not null, non-empty | `InvalidDependency.Missing: CloseClipSwap.A1Montage` |
| 6 | `CloseClipSwap.A1Montage` | Well-formed soft path (A-184 engine macros) | `InvalidDependency.Malformed: CloseClipSwap.A1Montage` |
| 7 | `CloseClipSwap.A3aMontage` | Not null, non-empty | `InvalidDependency.Missing: CloseClipSwap.A3aMontage` |
| 8 | `CloseClipSwap.A3aMontage` | Well-formed soft path (A-184 engine macros) | `InvalidDependency.Malformed: CloseClipSwap.A3aMontage` |
| 9 | `CloseClipSwap.A3bMontage` | Not null, non-empty | `InvalidDependency.Missing: CloseClipSwap.A3bMontage` |
| 10 | `CloseClipSwap.A3bMontage` | Well-formed soft path (A-184 engine macros) | `InvalidDependency.Malformed: CloseClipSwap.A3bMontage` |
| 11 | Cross-Field Uniqueness | No identical soft paths among A1, A3a, A3b | `InvalidDependency.Duplicate: CloseClipSwap.<Field>` |

*Note on bEnabled:* `URPGBossCloseClipSwap` has no authored `bEnabled` property in `RPGBossCloseClipSwap.h` (it only has a test-only `bEnabledForTest` flag at `:94`). If the typed record adds `bEnabled` for pipeline consistency (as in `FRPGLookConfig` / `FRPGLowSweepConfig`), both boolean values (true and false) must be accepted without altering domain validation.
