# Native Derivation Dossier: RPGBossCloseClipSwap

## 1. Component Overview & File Locations
- **Header:** `Source/OneBossFight/Player/RPGBossCloseClipSwap.h`
- **Rules Header:** `Source/OneBossFight/Player/RPGBossCloseClipSwapRules.h`
- **Source:** `Source/OneBossFight/Player/RPGBossCloseClipSwap.cpp`
- **Class:** `URPGBossCloseClipSwap` (`UActorComponent`)
- **Primary Function:** Injects authored animations into the pack's close attack ability (`GA_GS_Boss_CloseAttack_C`). Replaces A1 (`GS_Attack03_Montage` -> `AM_Boss01_A1`), A3a (`GS_Attack01_Montage` -> `AM_Boss01_A3a`), and A3b (`GS_Attack02_Montage` -> `AM_Boss01_A3b`) in the ability's `AttackMontages` struct array via live reflection, while intentionally preserving A1b (`GS_Attack04_Montage`) as the pack montage. Automatically restores original pack montages on encounter reset, boss death, or `EndPlay()`.

---

## 2. Exact Public Authored Fields
Directly extracted from `Source/OneBossFight/Player/RPGBossCloseClipSwap.h`:

```cpp
// Source/OneBossFight/Player/RPGBossCloseClipSwap.h:26
UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Close clips")
FName CloseAbilityClassName = TEXT("GA_GS_Boss_CloseAttack_C");

// Source/OneBossFight/Player/RPGBossCloseClipSwap.h:29
UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Close clips")
FName AttackMontagesName = TEXT("AttackMontages");

// Source/OneBossFight/Player/RPGBossCloseClipSwap.h:32
UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Close clips")
TSoftObjectPtr<UAnimMontage> A1Montage;

// Source/OneBossFight/Player/RPGBossCloseClipSwap.h:35
UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Close clips")
TSoftObjectPtr<UAnimMontage> A3aMontage;

// Source/OneBossFight/Player/RPGBossCloseClipSwap.h:38
UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Close clips")
TSoftObjectPtr<UAnimMontage> A3bMontage;
```

*Constructor Soft Path Initializers (`Source/OneBossFight/Player/RPGBossCloseClipSwap.cpp:43-45`):*
```cpp
A1Montage = TSoftObjectPtr<UAnimMontage>(FSoftObjectPath(TEXT("/Game/OneBossFight/Boss01/Animations/AM_Boss01_A1.AM_Boss01_A1")));
A3aMontage = TSoftObjectPtr<UAnimMontage>(FSoftObjectPath(TEXT("/Game/OneBossFight/Boss01/Animations/AM_Boss01_A3a.AM_Boss01_A3a")));
A3bMontage = TSoftObjectPtr<UAnimMontage>(FSoftObjectPath(TEXT("/Game/OneBossFight/Boss01/Animations/AM_Boss01_A3b.AM_Boss01_A3b")));
```

Total authored fields: **5**.

---

## 3. Code Readings & Extreme Handling (Read From Code)

### `CloseAbilityClassName` (`FName`, default `TEXT("GA_GS_Boss_CloseAttack_C")`)
- **Read Location:**
  - `Source/OneBossFight/Player/RPGBossCloseClipSwap.cpp:139`: `UObject* Ability = FindAbilityByClassName(GetOwner(), CloseAbilityClassName);` in `TryApply()`.
- **Extremes (Read From Code):**
  - `NAME_None` or unassigned: `FindAbilityByClassName` returns `nullptr`. `TryApply()` sets `LastResult = FString::Printf(TEXT("waiting for %s"), ...)` and returns false (`:143`). The component retries every 0.5s without crashing.

### `AttackMontagesName` (`FName`, default `TEXT("AttackMontages")`)
- **Read Locations:**
  - `Source/OneBossFight/Player/RPGBossCloseClipSwap.cpp:145`: `const FArrayProperty* Array = FindFProperty<FArrayProperty>(Ability->GetClass(), AttackMontagesName);` in `TryApply()`.
  - `Source/OneBossFight/Player/RPGBossCloseClipSwap.cpp:224`: in `Restore()`.
- **Extremes (Read From Code):**
  - `NAME_None` or unassigned: `FindFProperty` returns `nullptr`. Line 149 triggers:
    ```cpp
    bPermanentFailure = true;
    LastResult = FString::Printf(TEXT("%s has no validated %s F_AbilityMontage array; pack fallback retained"), ...);
    ```
    Sets `bPermanentFailure = true`; completely halts all further swap attempts for the lifetime of the component.

### `A1Montage` (`TSoftObjectPtr<UAnimMontage>`)
- **Read Locations:**
  - `Source/OneBossFight/Player/RPGBossCloseClipSwap.cpp:67`: `LoadedA1 = A1Montage.LoadSynchronous();` in `Preload()`.
  - `Source/OneBossFight/Player/RPGBossCloseClipSwap.cpp:80`: `if (PackMontageName == TEXT("GS_Attack03_Montage")) return LoadedA1.Get();` in `ReplacementFor()`.
- **Extremes (Read From Code):**
  - Invalid / Empty Path: `LoadedA1` is null. In `Preload()`, line 70 checks:
    ```cpp
    if (!LoadedA1 || !LoadedA3a || !LoadedA3b)
    {
        bPermanentFailure = true;
        LastResult = TEXT("an authored close montage did not load; pack fallback retained");
    }
    ```
    Sets `bPermanentFailure = true`. No montages are swapped; pack ability retains its original animations permanently.

### `A3aMontage` (`TSoftObjectPtr<UAnimMontage>`)
- **Read Locations:**
  - `Source/OneBossFight/Player/RPGBossCloseClipSwap.cpp:68`: `LoadedA3a = A3aMontage.LoadSynchronous();` in `Preload()`.
  - `Source/OneBossFight/Player/RPGBossCloseClipSwap.cpp:81`: `if (PackMontageName == TEXT("GS_Attack01_Montage")) return LoadedA3a.Get();` in `ReplacementFor()`.
- **Extremes (Read From Code):**
  - Invalid / Empty Path: `LoadedA3a` is null; triggers `bPermanentFailure = true` in `Preload()`.

### `A3bMontage` (`TSoftObjectPtr<UAnimMontage>`)
- **Read Locations:**
  - `Source/OneBossFight/Player/RPGBossCloseClipSwap.cpp:69`: `LoadedA3b = A3bMontage.LoadSynchronous();` in `Preload()`.
  - `Source/OneBossFight/Player/RPGBossCloseClipSwap.cpp:82`: `if (PackMontageName == TEXT("GS_Attack02_Montage")) return LoadedA3b.Get();` in `ReplacementFor()`.
- **Extremes (Read From Code):**
  - Invalid / Empty Path: `LoadedA3b` is null; triggers `bPermanentFailure = true` in `Preload()`.

---

## 4. Hardcoded Rules & External Dependencies
Directly cited from `Source/OneBossFight/Player/RPGBossCloseClipSwapRules.h` and `RPGBossCloseClipSwap.cpp`:

### Hardcoded Rules Mapping (`RPGBossCloseClipSwapRules.h:8-22`)
```cpp
namespace RPGBossCloseClipSwapRules
{
    inline FName ReplacementFor(FName PackMontageName)
    {
        if (PackMontageName == TEXT("GS_Attack03_Montage")) return TEXT("AM_Boss01_A1");
        if (PackMontageName == TEXT("GS_Attack01_Montage")) return TEXT("AM_Boss01_A3a");
        if (PackMontageName == TEXT("GS_Attack02_Montage")) return TEXT("AM_Boss01_A3b");
        return NAME_None; // GS_Attack04_Montage (A1b) intentionally remains the pack montage.
    }

    inline bool IsPackCloseMontage(FName Name)
    {
        return Name == TEXT("GS_Attack01_Montage") || Name == TEXT("GS_Attack02_Montage") || Name == TEXT("GS_Attack03_Montage") || Name == TEXT("GS_Attack04_Montage");
    }
}
```

### Strict Structural Assertions in `TryApply()`:
1. **Array Element Count (`RPGBossCloseClipSwap.cpp:155`):**
   - Requires `Entries.Num() == 4`. If not 4, sets `bPermanentFailure = true` and fails open.
2. **Pack Montage Identity (`RPGBossCloseClipSwap.cpp:169`):**
   - Every element must satisfy `RPGBossCloseClipSwapRules::IsPackCloseMontage(Current->GetFName())`. Any unexpected montage triggers `bPermanentFailure = true`.
3. **Exact 3 Replacements Mapped (`RPGBossCloseClipSwap.cpp:194`):**
   - Requires `Candidates.Num() == 3` and mappings for all three of `GS_Attack03_Montage`, `GS_Attack01_Montage`, and `GS_Attack02_Montage`.

### External Dependencies:
1. **`URPGBossEncounter` (Component Lookup & Prerequisite):**
   - Lookup: `Source/OneBossFight/Player/RPGBossCloseClipSwap.cpp:52, 110`.
   - Reads: `Encounter->GetResetCount()`, `Encounter->IsDormant()`. On reset count change, calls `Restore(TEXT("encounter reset"))` (`:113`).
2. **`URPGBossDeath` (Component Lookup):**
   - Lookup: `Source/OneBossFight/Player/RPGBossCloseClipSwap.cpp:120`: `Death->IsDeathActive()`. Calls `Restore(TEXT("boss death"))`.
3. **Gameplay Ability Reflection (`Pack/RPGBlueprintCall.h`):**
   - Direct memory mutation of `UObject* Ability` property buffer via `FScriptArrayHelper` and `FObjectPropertyBase::SetObjectPropertyValue` (`RPGBossCloseClipSwap.cpp:207`).
4. **Authored Soft Paths:**
   - `A1Montage`: `TSoftObjectPtr<UAnimMontage>`
   - `A3aMontage`: `TSoftObjectPtr<UAnimMontage>`
   - `A3bMontage`: `TSoftObjectPtr<UAnimMontage>`
   - All provable structurally offline via soft path validation.

---

## 5. Proposed Typed Domain

| Field | Type | Domain / Constraints | Label | Derivation Reason |
|---|---|---|---|---|
| `CloseAbilityClassName` | `FName` | Non-empty `FName`, matches `^[A-Za-z0-9_]+$` | **NATIVE-DERIVED** | Target class searched via `FindAbilityByClassName` (`RPGBossCloseClipSwap.cpp:139`). |
| `AttackMontagesName` | `FName` | Non-empty `FName`, matches `^[A-Za-z0-9_]+$` | **NATIVE-DERIVED** | Target property name searched via `FindFProperty` (`RPGBossCloseClipSwap.cpp:145`). |
| `A1Montage` | `TSoftObjectPtr<UAnimMontage>` | Valid soft path, non-empty, ends with `.AM_Boss01_A1` or matching object name | **NATIVE-DERIVED** | Synchronously loaded in `Preload()` (`RPGBossCloseClipSwap.cpp:67`). Null check triggers permanent failure. |
| `A3aMontage` | `TSoftObjectPtr<UAnimMontage>` | Valid soft path, non-empty, ends with `.AM_Boss01_A3a` or matching object name | **NATIVE-DERIVED** | Synchronously loaded in `Preload()` (`RPGBossCloseClipSwap.cpp:68`). Null check triggers permanent failure. |
| `A3bMontage` | `TSoftObjectPtr<UAnimMontage>` | Valid soft path, non-empty, ends with `.AM_Boss01_A3b` or matching object name | **NATIVE-DERIVED** | Synchronously loaded in `Preload()` (`RPGBossCloseClipSwap.cpp:69`). Null check triggers permanent failure. |

*Unresolved Items:*
- Hardcoded pack montage names (`GS_Attack01_Montage`, `GS_Attack02_Montage`, `GS_Attack03_Montage`, `GS_Attack04_Montage`) are fixed inside `RPGBossCloseClipSwapRules.h:10-21`. They are not configurable via profile properties.

---

## 6. Lifecycle Facts & Configure Guard Rules
- **Component Tick:** `PrimaryComponentTick.bCanEverTick = true; PrimaryComponentTick.TickInterval = 0.25f;` (`RPGBossCloseClipSwap.cpp:41-42`). Ticks at 4 Hz.
- **BeginPlay (`RPGBossCloseClipSwap.cpp:48-57`):**
  - Calls `Preload()` synchronously.
  - Registers tick prerequisite on `URPGBossEncounter`.
- **EndPlay (`RPGBossCloseClipSwap.cpp:59-63`):**
  - Calls `Restore(TEXT("EndPlay"))` to restore original pack montages into live ability memory.
- **Tick Polling Retry (`RPGBossCloseClipSwap.cpp:125-130`):**
  - Retries `TryApply()` every 0.5s until successfully applied or permanently failed.
- **Auto-Restore Triggers:**
  - Encounter reset (`LastResetCount != Encounter->GetResetCount()`)
  - Boss death (`Death->IsDeathActive()`)
  - Test toggle off (`SetEnabledForTest(false)`)
  - Component destruction (`EndPlay`)
- **Runtime State Fields (MUST NOT be overwritten or touched during runtime configure):**
  - `UPROPERTY(Transient) TObjectPtr<UAnimMontage> LoadedA1, LoadedA3a, LoadedA3b` (`RPGBossCloseClipSwap.h:80-85`)
  - `TWeakObjectPtr<UObject> SwappedAbility` (`RPGBossCloseClipSwap.h:87`)
  - `TArray<FSwap> Swaps` (`RPGBossCloseClipSwap.h:88`)
  - `int32 LastResetCount`, `float RetrySeconds`, `int32 ApplyCount`, `int32 RestoreCount` (`RPGBossCloseClipSwap.h:89-92`)
  - `bool bApplied`, `bEnabledForTest`, `bPermanentFailure`, `FString LastResult` (`RPGBossCloseClipSwap.h:93-96`)
- **Configure Guard Constraint:** If re-configured while `bApplied == true`, `Restore()` MUST be executed prior to mutating soft pointer paths or ability names; otherwise original pack montages cannot be restored into the previous ability instance, corrupting ability memory.
