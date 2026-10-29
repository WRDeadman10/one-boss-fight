# Field Manifest Contract Analysis: Validation, Truthfulness, Fixture Shapes, 110-Path Draft Table, and Consumer Impact

**Author:** Antigravity (Senior C++ Gameplay & Unreal Engine Specialist)  
**Task Order:** C-293 (A-201)  
**Date:** 2026-10-29  
**Status:** Read-Only Analysis Complete (Zero Source Edits, Zero Engine Invocations, Pure CRLF)

---

## Executive Summary

This document delivers the offline read-only technical analysis of the `FRPGParityField` manifest contract ordered by Tech Lead Claude in `[C-293]`. Following Order A-200, which established that no authored definition exists and that existing toolkit drafts leave `fields: []` empty, this analysis investigates the exact C++ source requirements governing manifest rows.

### Key Conclusions
1. **The 12-Column Validation Split:** Only **one single column** (`FieldPath`) is evaluated for a logical decision by the compiler, preflight, and context binding. Eight columns (`Type`, `SourcePath`, `SourceSite`, `Origin`, `Precedence`, `Destination`, `FirstRead`, `Witness`) are checked strictly for non-emptiness. One column (`SourceSHA256`) is checked strictly for 64-character hexadecimal shape. Two columns (`Value`, `Units`) are **completely ignored and unvalidated** by the compiler.
2. **The `Value` Column Truth:** The C++ compiler and component configure adapters read values exclusively from the typed USTRUCT properties (`Config.Stats`, `Config.Bleed`, etc.), **never from `FRPGParityField::Value`**. `Value` is purely human-readable audit text; writing any string representation does not affect runtime configuration or logic.
3. **Truthful Provenance vs. Invented Metadata:** For a definition reflecting the live game today, `SourcePath` and `SourceSite` can truthfully cite native C++ component headers/constructors (for the 11 defaults) or Tech Lead contracts C-258..C-281 (for the 5 newly authored clusters). However, provenance hashes (`SourceSHA256`), operational origins (`Origin`), and verification witnesses (`Witness`) would be **fabricated inventions** if generated without an authoritative Owner/Lead decision.
4. **The Test Fixture Pattern:** All existing DD-series automation tests construct manifest rows using synthetic fixture helpers (e.g. `MakeProductionField` in `RPGBossProductionPreflightTests.cpp:138`), filling columns with fixture placeholders (`"fixture"`, `"synthetic"`, `FString::ChrN(64, 'a')`) solely to satisfy structural format checks.
5. **The 110-Path Draft Table:** Section 4 tabulates all 110 paths across the 12 plans with their truthful C++ types, units, defaults, source sites, and destinations, demarcating known facts from items requiring Owner/Lead decision.
6. **Consumer Failure Points:** Five native engine and gameplay consumers break if manifest entries are omitted or malformed.

Every statement in this document is cited with verified `file:line` references from the codebase. Any deduction or architectural implication not directly stated in the code is explicitly marked as `[Inference]`.

---

## 1. Column-by-Column Contract and Validation Audit

`FRPGParityField` is declared in `Source/OneBossFight/Player/RPGEncounterBinding.h:275-290`:
```cpp
USTRUCT(BlueprintType)
struct FRPGParityField
{
	GENERATED_BODY()
	UPROPERTY(EditAnywhere) FString FieldPath;
	UPROPERTY(EditAnywhere) FString Value;
	UPROPERTY(EditAnywhere) FString Type;
	UPROPERTY(EditAnywhere) FString Units;
	UPROPERTY(EditAnywhere) FString SourcePath;
	UPROPERTY(EditAnywhere) FString SourceSHA256;
	UPROPERTY(EditAnywhere) FString SourceSite;
	UPROPERTY(EditAnywhere) FString Origin;
	UPROPERTY(EditAnywhere) FString Precedence;
	UPROPERTY(EditAnywhere) FString Destination;
	UPROPERTY(EditAnywhere) FString FirstRead;
	UPROPERTY(EditAnywhere) FString Witness;
};
```

### 1.1 Detailed Audit of Every Column

#### Column 1: `FieldPath` (`FString`)
- **Validators & Callsites:**
  - `CompileParticipantImpl` (`Source/OneBossFight/Player/RPGEncounterBinding.cpp:106`):
    `if (F.FieldPath.IsEmpty() || Fields.Contains(F.FieldPath))`
    Checks that the string is non-empty and unique across the definition's `Fields` array. Fails with `"incomplete/duplicate field-source manifest"`.
  - `RPGBossHydrationPreflight::CompilePreflight` (`Source/OneBossFight/Player/RPGBossHydrationPreflight.cpp:408-423`):
    Collects all `FieldPath` entries into `TSet<FString> Manifest`. Then, for every `FRPGComponentPlan` in `MemberPlans`, checks that every path in `Plan.RequiredFields` is contained in `Manifest`. Fails with `Preflight.MissingRequiredField: required manifest path <Path> is not in the config`.
  - `URPGCombatContextSubsystem::BindEncounter` (`Source/OneBossFight/Player/RPGEncounterBinding.cpp:354`):
    Iterates `Record->Config->Fields` and adds `Field.FieldPath` to `Manifest` to confirm participant readiness.
- **Classification:** **ACTIVE DECISION COLUMN**. The only column read by runtime compilers to authorize plan execution and batch hydration.

#### Column 2: `Value` (`FString`)
- **Validators & Callsites:**
  - `CompileParticipantImpl` (`Source/OneBossFight/Player/RPGEncounterBinding.cpp:104-115`): **NOT CHECKED**. `F.Value` is completely omitted from the validation `if` statement. It can be empty, whitespace, or arbitrary text.
  - `CompilePreflight` (`RPGBossHydrationPreflight.cpp`): **NOT READ**.
  - `URPGCombatContextSubsystem`: **NOT READ**.
  - Component Configure Callbacks: Component properties are populated strictly from typed structs (`Config->Stats`, `Config->Bleed`, etc.). As documented in `Source/OneBossFight/Player/RPGBossStatsAdapters.h:16` and `Source/OneBossFight/Player/RPGBossEncounterPolicyAdapters.h:15`:
    > *"The values are read from the typed Stats record only, never from FRPGParityField::Value and never through ImportText."*
  - Test suites explicitly verify that manifest text is ignored: e.g. `Source/OneBossFight/Tests/RPGBossBleedAdaptersTests.cpp:218-220` sets manifest value to `"9999"` and asserts that the configured component receives the typed record value `150.f` instead of `"9999"`.
- **Classification:** **AUDIT METADATA ONLY**. Zero C++ consumers parse, cast, or evaluate this column for configuration or execution.

#### Column 3: `Type` (`FString`)
- **Validators & Callsites:**
  - `CompileParticipantImpl` (`RPGEncounterBinding.cpp:106`): `if (... || F.Type.IsEmpty() || ...)`. Fails closed if empty.
  - Downstream compilers: **NOT READ**. Does not validate that the string matches the actual C++ reflection type (e.g. `"float"`, `"bool"`).
- **Classification:** **AUDIT METADATA ONLY** (Non-emptiness validated).

#### Column 4: `Units` (`FString`)
- **Validators & Callsites:**
  - `CompileParticipantImpl` (`RPGEncounterBinding.cpp:104-115`): **NOT CHECKED**. Omitted from validation. Can be empty string (which is standard for dimensionless booleans, names, or asset references).
  - Downstream compilers: **NOT READ**.
- **Classification:** **AUDIT METADATA ONLY** (Optional, unvalidated).

#### Column 5: `SourcePath` (`FString`)
- **Validators & Callsites:**
  - `CompileParticipantImpl` (`RPGEncounterBinding.cpp:107`): `if (... || F.SourcePath.IsEmpty() || ...)`. Fails closed if empty.
  - Downstream compilers: **NOT READ**. Does not perform any filesystem lookup to check if the path exists on disk.
- **Classification:** **AUDIT METADATA ONLY** (Non-emptiness validated).

#### Column 6: `SourceSHA256` (`FString`)
- **Validators & Callsites:**
  - `CompileParticipantImpl` (`RPGEncounterBinding.cpp:107`): `if (... || !IsSHA256(F.SourceSHA256) || ...)`.
  - `IsSHA256(const FString& Text)` (`Source/OneBossFight/Player/RPGEncounterBinding.cpp:27-31`):
    ```cpp
    static bool IsSHA256(const FString& Text)
    {
        if (Text.Len() != 64) { return false; }
        for (TCHAR C : Text) { if (!FChar::IsHexDigit(C)) { return false; } }
        return true;
    }
    ```
    Enforces that `SourceSHA256` is exactly 64 characters long and composed entirely of hexadecimal characters (`0-9`, `a-f`, `A-F`). Fails closed with `"incomplete/duplicate field-source manifest"` if malformed.
  - Downstream compilers: **NOT READ**. The compiler does not verify that the hash matches the bytes of `SourcePath`.
- **Classification:** **AUDIT METADATA ONLY** (Syntactic shape validated: 64-character hex).

#### Column 7: `SourceSite` (`FString`)
- **Validators & Callsites:**
  - `CompileParticipantImpl` (`RPGEncounterBinding.cpp:107`): `if (... || F.SourceSite.IsEmpty() || ...)`. Fails closed if empty.
  - Downstream compilers: **NOT READ**.
- **Classification:** **AUDIT METADATA ONLY** (Non-emptiness validated).

#### Column 8: `Origin` (`FString`)
- **Validators & Callsites:**
  - `CompileParticipantImpl` (`RPGEncounterBinding.cpp:108`): `if (... || F.Origin.IsEmpty() || ...)`. Fails closed if empty.
  - Downstream compilers: **NOT READ**.
- **Classification:** **AUDIT METADATA ONLY** (Non-emptiness validated).

#### Column 9: `Precedence` (`FString`)
- **Validators & Callsites:**
  - `CompileParticipantImpl` (`RPGEncounterBinding.cpp:108`): `if (... || F.Precedence.IsEmpty() || ...)`. Fails closed if empty.
  - Downstream compilers: **NOT READ**.
- **Classification:** **AUDIT METADATA ONLY** (Non-emptiness validated).

#### Column 10: `Destination` (`FString`)
- **Validators & Callsites:**
  - `CompileParticipantImpl` (`RPGEncounterBinding.cpp:108`): `if (... || F.Destination.IsEmpty() || ...)`. Fails closed if empty.
  - Downstream compilers: **NOT READ**.
- **Classification:** **AUDIT METADATA ONLY** (Non-emptiness validated).

#### Column 11: `FirstRead` (`FString`)
- **Validators & Callsites:**
  - `CompileParticipantImpl` (`RPGEncounterBinding.cpp:109`): `if (... || F.FirstRead.IsEmpty() || ...)`. Fails closed if empty.
  - Downstream compilers: **NOT READ**.
- **Classification:** **AUDIT METADATA ONLY** (Non-emptiness validated).

#### Column 12: `Witness` (`FString`)
- **Validators & Callsites:**
  - `CompileParticipantImpl` (`RPGEncounterBinding.cpp:109`): `if (... || F.Witness.IsEmpty() || ...)`. Fails closed if empty.
  - Downstream compilers: **NOT READ**.
- **Classification:** **AUDIT METADATA ONLY** (Non-emptiness validated).

---

### 1.2 Summary Matrix of Column Validation Rules

| Column | C++ Type | Validated By | Rule Enforced | Consumer Reads For Decision? |
| :--- | :--- | :--- | :--- | :--- |
| **`FieldPath`** | `FString` | `CompileParticipantImpl`, `CompilePreflight`, `BindEncounter` | Non-empty, unique across definition, must cover all 110 required plan paths | **YES** (Plan requirement gate) |
| **`Value`** | `FString` | *None* | Unchecked (can be empty) | **NO** (Never parsed as config) |
| **`Type`** | `FString` | `CompileParticipantImpl` | Non-empty string | **NO** |
| **`Units`** | `FString` | *None* | Unchecked (can be empty) | **NO** |
| **`SourcePath`** | `FString` | `CompileParticipantImpl` | Non-empty string | **NO** |
| **`SourceSHA256`** | `FString` | `CompileParticipantImpl` | Exactly 64 hex characters (`IsSHA256`) | **NO** |
| **`SourceSite`** | `FString` | `CompileParticipantImpl` | Non-empty string | **NO** |
| **`Origin`** | `FString` | `CompileParticipantImpl` | Non-empty string | **NO** |
| **`Precedence`** | `FString` | `CompileParticipantImpl` | Non-empty string | **NO** |
| **`Destination`** | `FString` | `CompileParticipantImpl` | Non-empty string | **NO** |
| **`FirstRead`** | `FString` | `CompileParticipantImpl` | Non-empty string | **NO** |
| **`Witness`** | `FString` | `CompileParticipantImpl` | Non-empty string | **NO** |

---

## 2. Truthfulness of Manifest Rows vs. Invented Metadata

When authoring a real definition asset, what can be truthfully populated today, and what would be an invented fiction without Lead or Owner policy?

### 2.1 The Truthful Columns (Can Be Populated Without Invention)
1. **`FieldPath`:** 100% truthful. Corresponds exactly to the 110 required property paths in `RPGBossHydrationPreflightTests.cpp:90-116` and the respective component adapters.
2. **`Value`:** Can truthfully represent the default value configured in C++ constructors or Lead contracts (e.g. `"5.0"`, `"true"`, `"/Game/.../AM_Boss01_A1"`). *Crucial caveat:* Because the compiler never reads `Value`, this is purely human-readable audit text.
3. **`Type`:** 100% truthful. Derived directly from the C++ UPROPERTY declarations (e.g. `float`, `bool`, `FName`, `FVector2D`, `TSoftObjectPtr<UAnimMontage>`).
4. **`Units`:** 100% truthful. Can accurately state physical units (`seconds`, `degrees`, `cm`, `cm/s`, `hp`, `fraction 0..1`) or remain empty for dimensionless types.
5. **`SourcePath`:**
   - For the 11 legacy component defaults: Can truthfully cite the native C++ header (e.g. `Source/OneBossFight/Player/RPGBossStagger.h`).
   - For `Death.DeathMode`: Can truthfully cite `Source/OneBossFight/Player/RPGPlayerMovesSubsystem.cpp` (`AttachLegacyBossBundle` line 187 override).
   - For the 5 newly authored clusters (LowSweep, Shockwave, HealPunish, Look, CloseClipSwap): Can truthfully cite the Lead contract specifications in `Documentation/TEAM_MAILBOX.md` (`C-258`, `C-263`, `C-265`, `C-269`, `C-275`).
6. **`SourceSite`:** Can truthfully cite the declaration line or constructor in C++ code (e.g. `URPGBossStagger::StaggerSeconds`, `AttachLegacyBossBundle:187`).
7. **`Destination`:** 100% truthful. Can cite the destination runtime C++ component member (e.g. `URPGBossStagger::StaggerSeconds`, `URPGBossDeath::DeathMode`).

### 2.2 The Problematic Columns (Risk of Being Invented)
1. **`SourceSHA256`:**
   - If `SourcePath` is set to `Source/OneBossFight/Player/RPGBossStagger.h`, should `SourceSHA256` be the live SHA256 of that C++ file? If so, any code edit or whitespace change in that C++ header would invalidate the manifest row if hash verification were ever implemented.
   - If a synthetic fixture hash like `FString::ChrN(64, 'c')` or an arbitrary dummy hash is used, **it is an invented token** whose only purpose is bypassing `IsSHA256()` format validation.
   - *Requirement:* The Lead must decide whether `SourceSHA256` should be computed from the source C++ files on disk at asset generation time, or whether a frozen catalog hash is designated.
2. **`Origin`:**
   - Possible categories: `NativeConstructorDefault`, `LegacySubsystemOverride`, `LeadDesignContract`, `AuthoringAsset`.
   - Without a project-wide taxonomy defined by the Lead, any string placed here is an unstandardized placeholder.
3. **`Precedence`:**
   - In DD tests, this is simply written as `"fixture"`.
   - In production, what does precedence mean? Does it mean `AuthoredAsset > NativeDefault`, or does it refer to runtime cvar overrides? Without an architectural definition, any string is an informal label.
4. **`FirstRead`:**
   - In DD tests, this is set to `"BeginPlay"`, `"not read"`, or `"test"`.
   - Truthfully tracing the exact engine tick or lifecycle hook where every one of the 110 fields is first accessed in game code would require deep call-graph instrumentation. Writing `"BeginPlay"` for all 110 fields is an educated generalization `[Inference]`.
5. **`Witness`:**
   - In DD tests, this is `"synthetic only"` or `"none: structural membership only"`.
   - What is the authority witnessing an authored asset? The authoring script? An automated test? A human designer? This requires an explicit team convention.

---

## 3. How DD-Series Tests Construct Valid Manifest Rows

Inspection of test suites across the DD program shows a universal pattern: every test suite uses a local helper function that synthesizes `FRPGParityField` instances with hardcoded strings that satisfy `CompileParticipantImpl`'s non-emptiness and `IsSHA256()` format checks.

### 3.1 Production Preflight Fixture Helper
In `Source/OneBossFight/Tests/RPGBossProductionPreflightTests.cpp:138-154`:
```cpp
/** A manifest row supplied by this fixture: it satisfies the production compiler's row shape and the preflight's membership check; it is not derived from any asset and carries no authority. */
FRPGParityField MakeProductionField(const FString& Path)
{
	FRPGParityField Field;
	Field.FieldPath = Path;
	Field.Type = TEXT("fixture");
	Field.Value = TEXT("production fixture row: membership only, not derived from an asset");
	Field.SourcePath = TEXT("DD14 production preflight fixture, not live provenance");
	Field.SourceSHA256 = FString::ChrN(64, TEXT('c'));
	Field.SourceSite = TEXT("fixture");
	Field.Origin = TEXT("harness");
	Field.Precedence = TEXT("fixture");
	Field.Destination = TEXT("fixture");
	Field.FirstRead = TEXT("not read");
	Field.Witness = TEXT("none: structural membership only");
	return Field;
}
```
*Key Observation:* Note that `SourceSHA256` is constructed using `FString::ChrN(64, TEXT('c'))` (64 repetitions of character `'c'`). This satisfies `IsSHA256` while explicitly signaling that it is a synthetic fixture token rather than a cryptographic hash of a real asset.

### 3.2 Bleed Adapter Test Helper
In `Source/OneBossFight/Tests/RPGBossBleedAdaptersTests.cpp:176-189`:
```cpp
FRPGParityField MakeField(const FString& Path, const FString& ValueText)
{
	FRPGParityField Field;
	Field.FieldPath = Path;
	Field.Type = TEXT("float");
	Field.Value = ValueText;
	Field.SourcePath = TEXT("synthetic fixture, not live provenance");
	Field.SourceSHA256 = FString::ChrN(64, TEXT('a'));
	Field.SourceSite = TEXT("fixture");
	Field.Origin = TEXT("harness");
	Field.Precedence = TEXT("fixture");
	Field.Destination = TEXT("fixture");
	Field.FirstRead = TEXT("BeginPlay");
	Field.Witness = TEXT("synthetic only");
	return Field;
}
```

### 3.3 Shockwave Adapter Test Helper
In `Source/OneBossFight/Tests/RPGBossShockwaveAdaptersTests.cpp:199-203`:
```cpp
FRPGParityField Field;
Field.FieldPath = Path; 
Field.Value = TEXT("not parsed as config"); 
Field.Type = TEXT("fixture");
Field.SourcePath = TEXT("synthetic only"); 
Field.SourceSHA256 = FString::ChrN(64, TEXT('a'));
```

All 7 hydration test suites follow this exact shape. None of them connects manifest rows to live assets or computes live file hashes.

---

## 4. Draft Table of the 110 Manifest Paths

The table below catalogs all 110 paths required by `RPGBossHydrationPreflight::CompilePreflight` (under DD26) with the column values that can be truthfully stated today without inventing metadata, and denotes columns requiring Owner/Lead decision:

| 1 | `StaggerPolicy.StaggerSeconds` | `float` | seconds | `5.0` | `RPGBossStagger.h:55` | `URPGBossStagger::StaggerSeconds` | Known Native Default |
| 2 | `StaggerPolicy.FreezeAtPosition` | `bool` | dimensionless | `true` | `RPGBossStagger.h:58` | `URPGBossStagger::bFreezeAtPosition` | Known Native Default |
| 3 | `StaggerPolicy.CriticalMultiplier` | `float` | multiplier | `2.0` | `RPGBossStagger.h:61` | `URPGBossStagger::CriticalMultiplier` | Known Native Default |
| 4 | `StaggerPolicy.RiposteRange` | `float` | cm | `250.0` | `RPGBossStagger.h:64` | `URPGBossStagger::RiposteRange` | Known Native Default |
| 5 | `StaggerPolicy.RiposteConeDegrees` | `float` | degrees | `60.0` | `RPGBossStagger.h:67` | `URPGBossStagger::RiposteConeDegrees` | Known Native Default |
| 6 | `StaggerPolicy.RiposteFacingDegrees` | `float` | degrees | `45.0` | `RPGBossStagger.h:70` | `URPGBossStagger::RiposteFacingDegrees` | Known Native Default |
| 7 | `StaggerPolicy.RiposteArmSeconds` | `float` | seconds | `0.4` | `RPGBossStagger.h:73` | `URPGBossStagger::RiposteArmSeconds` | Known Native Default |
| 8 | `StaggerPolicy.RipostePlayerStartGap` | `float` | cm | `120.0` | `RPGBossStagger.h:76` | `URPGBossStagger::RipostePlayerStartGap` | Known Native Default |
| 9 | `StaggerPolicy.RiposteAlignSeconds` | `float` | seconds | `0.2` | `RPGBossStagger.h:79` | `URPGBossStagger::RiposteAlignSeconds` | Known Native Default |
| 10 | `StaggerPolicy.RiposteImpactSeconds` | `float` | seconds | `0.8` | `RPGBossStagger.h:82` | `URPGBossStagger::RiposteImpactSeconds` | Known Native Default |
| 11 | `StaggerPolicy.RiposteBaseDamage` | `float` | hp | `500.0` | `RPGBossStagger.h:85` | `URPGBossStagger::RiposteBaseDamage` | Known Native Default |
| 12 | `StaggerPolicy.CooldownSeconds` | `float` | seconds | `15.0` | `RPGBossStagger.h:88` | `URPGBossStagger::CooldownSeconds` | Known Native Default |
| 13 | `StaggerPolicy.GetUpRate` | `float` | multiplier | `1.0` | `RPGBossStagger.h:91` | `URPGBossStagger::GetUpRate` | Known Native Default |
| 14 | `StaggerPolicy.bHoldPostureAtZero` | `bool` | dimensionless | `true` | `RPGBossStagger.h:94` | `URPGBossStagger::bHoldPostureAtZero` | Known Native Default |
| 15 | `StaggerProfile.bUseClips` | `bool` | dimensionless | `true` | `RPGBossStagger.h:102` | `URPGBossStagger::bUseClips` | Known Native Default |
| 16 | `StaggerProfile.bUseRiposteClips` | `bool` | dimensionless | `true` | `RPGBossStagger.h:105` | `URPGBossStagger::bUseRiposteClips` | Known Native Default |
| 17 | `StaggerProfile.bCriticalOnEveryHit` | `bool` | dimensionless | `false` | `RPGBossStagger.h:108` | `URPGBossStagger::bCriticalOnEveryHit` | Known Native Default |
| 18 | `StaggerProfile.HitStunAbilityClassName` | `FName` | identifier | `GA_GS_Boss_HitStun_C` | `RPGBossStagger.h:111` | `URPGBossStagger::HitStunAbilityClassName` | Known Native Default |
| 19 | `StaggerProfile.FallMontage` | `TSoftObjectPtr<UAnimMontage>` | soft path | `/Game/AdvancedARPGCombat/MeleeCombatSystem/Animations/2handed/KnockdownStart_Anim_Montage.KnockdownStart_Anim_Montage` | `RPGBossStagger.h:114` | `URPGBossStagger::FallMontage` | Known Native Default |
| 20 | `StaggerProfile.GetUpMontage` | `TSoftObjectPtr<UAnimMontage>` | soft path | `/Game/AdvancedARPGCombat/MeleeCombatSystem/Animations/2handed/Knockdown_Getup_Anim_Montage.Knockdown_Getup_Anim_Montage` | `RPGBossStagger.h:117` | `URPGBossStagger::GetUpMontage` | Known Native Default |
| 21 | `StaggerProfile.FallClip` | `TSoftObjectPtr<UAnimSequence>` | soft path | `/Game/OneBossFight/Boss01/Animations/AN_Stagger_Fall.AN_Stagger_Fall` | `RPGBossStagger.h:120` | `URPGBossStagger::FallClip` | Known Native Default |
| 22 | `StaggerProfile.DownClip` | `TSoftObjectPtr<UAnimSequence>` | soft path | `/Game/OneBossFight/Boss01/Animations/AN_Stagger_Down.AN_Stagger_Down` | `RPGBossStagger.h:123` | `URPGBossStagger::DownClip` | Known Native Default |
| 23 | `StaggerProfile.RipostePlayerClip` | `TSoftObjectPtr<UAnimSequence>` | soft path | `/Game/OneBossFight/Boss01/Animations/AN_Riposte_Player_Execution.AN_Riposte_Player_Execution` | `RPGBossStagger.h:126` | `URPGBossStagger::RipostePlayerClip` | Known Native Default |
| 24 | `StaggerProfile.RiposteBossClip` | `TSoftObjectPtr<UAnimSequence>` | soft path | `/Game/OneBossFight/Boss01/Animations/AN_Riposte_Boss_Reaction.AN_Riposte_Boss_Reaction` | `RPGBossStagger.h:129` | `URPGBossStagger::RiposteBossClip` | Known Native Default |
| 25 | `StaggerProfile.ImmunityEffect` | `TSoftClassPtr<UObject>` | soft path | `/Game/AdvancedARPGCombat/MeleeCombatSystem/Blueprints/GameplayEffects/GE_HitStunImmune.GE_HitStunImmune_C` | `RPGBossStagger.h:132` | `URPGBossStagger::ImmunityEffect` | Known Native Default |
| 26 | `Phases[PhaseTwo].EntryHealthFraction` | `float` | fraction 0..1 | `0.5` | `RPGBossPhases.h:45` | `FRPGPhaseConfig::EntryHealthFraction` | Needs Encounter Phase Spec |
| 27 | `Phases[PhaseTwo].SpeedMultiplier` | `float` | multiplier | `1.15` | `RPGBossPhases.h:48` | `FRPGPhaseConfig::SpeedMultiplier` | Needs Encounter Phase Spec |
| 28 | `Phases[PhaseTwo].RateMultiplier` | `float` | multiplier | `1.25` | `RPGBossPhases.h:51` | `FRPGPhaseConfig::RateMultiplier` | Needs Encounter Phase Spec |
| 29 | `Phases[PhaseTwo].AttackMultiplier` | `float` | multiplier | `1.2` | `RPGBossPhases.h:54` | `FRPGPhaseConfig::AttackMultiplier` | Needs Encounter Phase Spec |
| 30 | `PhaseFlow.TransitionSeconds` | `float` | seconds | `3.0` | `RPGBossPhases.h:65` | `URPGBossPhases::TransitionSeconds` | Known Native Default |
| 31 | `PhaseFlow.bUseRoarClip` | `bool` | dimensionless | `true` | `RPGBossPhases.h:68` | `URPGBossPhases::bUseRoarClip` | Known Native Default |
| 32 | `PhaseFlow.bPausePostureInTransition` | `bool` | dimensionless | `true` | `RPGBossPhases.h:71` | `URPGBossPhases::bPausePostureInTransition` | Known Native Default |
| 33 | `PhaseFlow.bLockLeapUntilPhaseTwo` | `bool` | dimensionless | `true` | `RPGBossPhases.h:74` | `URPGBossPhases::bLockLeapUntilPhaseTwo` | Known Native Default |
| 34 | `PhaseFlow.AttackAbilityPrefix` | `FName` | identifier | `GA_GS_Boss_` | `RPGBossPhases.h:77` | `URPGBossPhases::AttackAbilityPrefix` | Known Native Default |
| 35 | `PhaseFlow.LeapAbilityTag` | `FName` | identifier | `Ability.Boss.LeapAttack` | `RPGBossPhases.h:80` | `URPGBossPhases::LeapAbilityTag` | Known Native Default |
| 36 | `Fireball.bFireballEnabled` | `bool` | dimensionless | `true` | `RPGBossPhases.h:90` | `URPGBossPhases::bFireballEnabled` | Known Native Default |
| 37 | `Fireball.FireballAbility` | `TSoftClassPtr<UObject>` | soft path | `/Game/AdvancedARPGCombat/MagicCombatSystem/Blueprints/AI/ExampleMagicEnemy/GA_Fireball_Enemy.GA_Fireball_Enemy_C` | `RPGBossPhases.h:93` | `URPGBossPhases::FireballAbility` | Known Native Default |
| 38 | `Fireball.FireballCooldown` | `FVector2D` | seconds | `(X=6.0, Y=10.0)` | `RPGBossPhases.h:96` | `URPGBossPhases::FireballCooldown` | Known Native Default |
| 39 | `Fireball.FireballMinRange` | `float` | cm | `500.0` | `RPGBossPhases.h:99` | `URPGBossPhases::FireballMinRange` | Known Native Default |
| 40 | `Fireball.FireballMaxRange` | `float` | cm | `2500.0` | `RPGBossPhases.h:102` | `URPGBossPhases::FireballMaxRange` | Known Native Default |
| 41 | `PhaseDependencies.RoarClip` | `TSoftObjectPtr<UAnimSequence>` | soft path | `/Game/OneBossFight/Boss01/Animations/AN_Boss01_Roar.AN_Boss01_Roar` | `RPGBossPhases.h:110` | `URPGBossPhases::RoarClip` | Known Native Default |
| 42 | `PhaseDependencies.TransitionMontage` | `TSoftObjectPtr<UAnimMontage>` | soft path | `/Game/AdvancedARPGCombat/MeleeCombatSystem/Animations/2handed/Ability_R_Intro_Anim_Montage.Ability_R_Intro_Anim_Montage` | `RPGBossPhases.h:113` | `URPGBossPhases::TransitionMontage` | Known Native Default |
| 43 | `PhaseDependencies.ImmunityEffect` | `TSoftClassPtr<UObject>` | soft path | `/Game/AdvancedARPGCombat/MeleeCombatSystem/Blueprints/GameplayEffects/GE_HitStunImmune.GE_HitStunImmune_C` | `RPGBossPhases.h:116` | `URPGBossPhases::ImmunityEffect` | Known Native Default |
| 44 | `Stats.MaxHealth` | `float` | hp | `4100.0` | `RPGBossEncounter.h:35` | `URPGBossEncounter::MaxHealth` | Known Native Default |
| 45 | `EncounterPolicy.GateRadius` | `float` | cm | `1200.0` | `RPGBossEncounter.h:45` | `URPGBossEncounter::GateRadius` | Known Native Default |
| 46 | `EncounterPolicy.bResetOnPlayerRespawn` | `bool` | dimensionless | `true` | `RPGBossEncounter.h:48` | `URPGBossEncounter::bResetOnPlayerRespawn` | Known Native Default |
| 47 | `DormantWake.DormantClip` | `TSoftObjectPtr<UAnimSequence>` | soft path | `/Game/OneBossFight/Boss01/Animations/AN_Boss01_IdleDormant.AN_Boss01_IdleDormant` | `RPGBossDormantWake.h:35` | `URPGBossDormantWake::DormantClip` | Known Native Default |
| 48 | `DormantWake.WakeClip` | `TSoftObjectPtr<UAnimSequence>` | soft path | `/Game/OneBossFight/Boss01/Animations/AN_Boss01_Wake.AN_Boss01_Wake` | `RPGBossDormantWake.h:38` | `URPGBossDormantWake::WakeClip` | Known Native Default |
| 49 | `Stats.MaxPosture` | `float` | posture points | `100.0` | `RPGBossPosture.h:40` | `URPGBossPosture::MaxPosture` | Known Native Default |
| 50 | `Stats.PostureRegenDelay` | `float` | seconds | `4.0` | `RPGBossPosture.h:43` | `URPGBossPosture::PostureRegenDelay` | Known Native Default |
| 51 | `Stats.PostureRegenRate` | `float` | points/sec | `10.0` | `RPGBossPosture.h:46` | `URPGBossPosture::PostureRegenRate` | Known Native Default |
| 52 | `Bleed.InitialThreshold` | `float` | points | `100.0` | `RPGBossBleed.h:38` | `URPGBossBleed::InitialThreshold` | Known Native Default |
| 53 | `Bleed.ThresholdIncrease` | `float` | points | `20.0` | `RPGBossBleed.h:41` | `URPGBossBleed::ThresholdIncrease` | Known Native Default |
| 54 | `Bleed.ThresholdMax` | `float` | points | `200.0` | `RPGBossBleed.h:44` | `URPGBossBleed::ThresholdMax` | Known Native Default |
| 55 | `Bleed.HpFraction` | `float` | fraction 0..1 | `0.03` | `RPGBossBleed.h:47` | `URPGBossBleed::HpFraction` | Known Native Default |
| 56 | `Bleed.EffectHeight` | `float` | cm | `100.0` | `RPGBossBleed.h:50` | `URPGBossBleed::EffectHeight` | Known Native Default |
| 57 | `Bleed.ProcEffect` | `TSoftObjectPtr<UNiagaraSystem>` | soft path | `/Game/OneBossFight/VFX/NS_BloodSpurt.NS_BloodSpurt` | `RPGBossBleed.h:53` | `URPGBossBleed::ProcEffect` | Known Native Default |
| 58 | `Bleed.ProcSound` | `TSoftObjectPtr<USoundBase>` | soft path | `/Game/OneBossFight/Audio/Cue_BossBleedProc.Cue_BossBleedProc` | `RPGBossBleed.h:56` | `URPGBossBleed::ProcSound` | Known Native Default |
| 59 | `LowSweep.bEnabled` | `bool` | dimensionless | `true` | `RPGBossLowSweep.h:35` | `URPGBossLowSweep::bEnabled` | Lead Contract C-258 |
| 60 | `LowSweep.MoveId` | `FName` | identifier | `A7_LowSweep` | `RPGBossLowSweep.h:38` | `URPGBossLowSweep::MoveId` | Lead Contract C-258 |
| 61 | `LowSweep.Damage` | `float` | hp | `180.0` | `RPGBossLowSweep.h:41` | `URPGBossLowSweep::Damage` | Lead Contract C-258 |
| 62 | `LowSweep.Reach` | `float` | cm | `450.0` | `RPGBossLowSweep.h:44` | `URPGBossLowSweep::Reach` | Lead Contract C-258 |
| 63 | `LowSweep.InnerRadius` | `float` | cm | `120.0` | `RPGBossLowSweep.h:47` | `URPGBossLowSweep::InnerRadius` | Lead Contract C-258 |
| 64 | `LowSweep.BladeHeight` | `float` | cm | `80.0` | `RPGBossLowSweep.h:50` | `URPGBossLowSweep::BladeHeight` | Lead Contract C-258 |
| 65 | `LowSweep.SweepFromDegrees` | `float` | degrees | `-120.0` | `RPGBossLowSweep.h:53` | `URPGBossLowSweep::SweepFromDegrees` | Lead Contract C-258 |
| 66 | `LowSweep.SweepToDegrees` | `float` | degrees | `120.0` | `RPGBossLowSweep.h:56` | `URPGBossLowSweep::SweepToDegrees` | Lead Contract C-258 |
| 67 | `Shockwave.bEnabled` | `bool` | dimensionless | `true` | `RPGBossShockwave.h:35` | `URPGBossShockwave::bEnabled` | Lead Contract C-263 |
| 68 | `Shockwave.MoveId` | `FName` | identifier | `A6_Slam` | `RPGBossShockwave.h:38` | `URPGBossShockwave::MoveId` | Lead Contract C-263 |
| 69 | `Shockwave.Damage` | `float` | hp | `150.0` | `RPGBossShockwave.h:41` | `URPGBossShockwave::Damage` | Lead Contract C-263 |
| 70 | `Shockwave.StartRadius` | `float` | cm | `100.0` | `RPGBossShockwave.h:44` | `URPGBossShockwave::StartRadius` | Lead Contract C-263 |
| 71 | `Shockwave.MaxRadius` | `float` | cm | `1200.0` | `RPGBossShockwave.h:47` | `URPGBossShockwave::MaxRadius` | Lead Contract C-263 |
| 72 | `Shockwave.Speed` | `float` | cm/s | `800.0` | `RPGBossShockwave.h:50` | `URPGBossShockwave::Speed` | Lead Contract C-263 |
| 73 | `Shockwave.Thickness` | `float` | cm | `150.0` | `RPGBossShockwave.h:53` | `URPGBossShockwave::Thickness` | Lead Contract C-263 |
| 74 | `Shockwave.JumpClearance` | `float` | cm | `60.0` | `RPGBossShockwave.h:56` | `URPGBossShockwave::JumpClearance` | Lead Contract C-263 |
| 75 | `HealPunish.bEnabled` | `bool` | dimensionless | `true` | `RPGBossHealPunish.h:35` | `URPGBossHealPunish::bEnabled` | Lead Contract C-265 |
| 76 | `HealPunish.MinRange` | `float` | cm | `600.0` | `RPGBossHealPunish.h:38` | `URPGBossHealPunish::MinRange` | Lead Contract C-265 |
| 77 | `HealPunish.MaxRange` | `float` | cm | `3000.0` | `RPGBossHealPunish.h:41` | `URPGBossHealPunish::MaxRange` | Lead Contract C-265 |
| 78 | `HealPunish.Cooldown` | `float` | seconds | `12.0` | `RPGBossHealPunish.h:44` | `URPGBossHealPunish::Cooldown` | Lead Contract C-265 |
| 79 | `HealPunish.Damage` | `float` | hp | `220.0` | `RPGBossHealPunish.h:47` | `URPGBossHealPunish::Damage` | Lead Contract C-265 |
| 80 | `HealPunish.FlightTime` | `float` | seconds | `0.75` | `RPGBossHealPunish.h:50` | `URPGBossHealPunish::FlightTime` | Lead Contract C-265 |
| 81 | `HealPunish.MinSpeed` | `float` | cm/s | `1500.0` | `RPGBossHealPunish.h:53` | `URPGBossHealPunish::MinSpeed` | Lead Contract C-265 |
| 82 | `HealPunish.MaxSpeed` | `float` | cm/s | `4000.0` | `RPGBossHealPunish.h:56` | `URPGBossHealPunish::MaxSpeed` | Lead Contract C-265 |
| 83 | `HealPunish.JavelinRadius` | `float` | cm | `40.0` | `RPGBossHealPunish.h:59` | `URPGBossHealPunish::JavelinRadius` | Lead Contract C-265 |
| 84 | `HealPunish.JavelinMaxRange` | `float` | cm | `3500.0` | `RPGBossHealPunish.h:62` | `URPGBossHealPunish::JavelinMaxRange` | Lead Contract C-265 |
| 85 | `HealPunish.SpawnSockets` | `TArray<FName>` | identifiers | `["JavelinSocket_L", "JavelinSocket_R"]` | `RPGBossHealPunish.h:65` | `URPGBossHealPunish::SpawnSockets` | Lead Contract C-265 |
| 86 | `HealPunish.AimHeight` | `float` | cm | `120.0` | `RPGBossHealPunish.h:68` | `URPGBossHealPunish::AimHeight` | Lead Contract C-265 |
| 87 | `HealPunish.bRespondToHeal` | `bool` | dimensionless | `true` | `RPGBossHealPunish.h:71` | `URPGBossHealPunish::bRespondToHeal` | Lead Contract C-265 |
| 88 | `HealPunish.bCancelJavelinsOnInterrupt` | `bool` | dimensionless | `true` | `RPGBossHealPunish.h:74` | `URPGBossHealPunish::bCancelJavelinsOnInterrupt` | Lead Contract C-265 |
| 89 | `Look.bEnabled` | `bool` | dimensionless | `true` | `RPGBossLook.h:35` | `URPGBossLook::bEnabled` | Lead Contract C-269 |
| 90 | `Look.Body` | `TSoftObjectPtr<USkeletalMesh>` | soft path | `/Game/OneBossFight/Boss01/Meshes/SK_Boss01_Body.SK_Boss01_Body` | `RPGBossLook.h:38` | `URPGBossLook::Body` | Known Native Default |
| 91 | `Look.Pieces` | `TArray<TSoftObjectPtr<USkeletalMesh>>` | soft path array | `["...Crown", "...Mantle", "...Gauntlet"]` | `RPGBossLook.h:41` | `URPGBossLook::Pieces` | Known Native Default |
| 92 | `Look.Sword` | `TSoftObjectPtr<UStaticMesh>` | soft path | `/Game/OneBossFight/Boss01/Meshes/SM_Boss01_Greatsword.SM_Boss01_Greatsword` | `RPGBossLook.h:44` | `URPGBossLook::Sword` | Known Native Default |
| 93 | `Look.SwordSocket` | `FName` | identifier | `HeavySwordSocket_R` | `RPGBossLook.h:47` | `URPGBossLook::SwordSocket` | Known Native Default |
| 94 | `CloseClipSwap.CloseAbilityClassName` | `FName` | identifier | `GA_GS_Boss_CloseAttack_C` | `RPGBossCloseClipSwap.h:35` | `URPGBossCloseClipSwap::CloseAbilityClassName` | Lead Contract C-275 |
| 95 | `CloseClipSwap.AttackMontagesName` | `FName` | identifier | `AttackMontages` | `RPGBossCloseClipSwap.h:38` | `URPGBossCloseClipSwap::AttackMontagesName` | Lead Contract C-275 |
| 96 | `CloseClipSwap.A1Montage` | `TSoftObjectPtr<UAnimMontage>` | soft path | `/Game/OneBossFight/Boss01/Animations/AM_Boss01_A1.AM_Boss01_A1` | `RPGBossCloseClipSwap.h:41` | `URPGBossCloseClipSwap::A1Montage` | Lead Contract C-275 |
| 97 | `CloseClipSwap.A3aMontage` | `TSoftObjectPtr<UAnimMontage>` | soft path | `/Game/OneBossFight/Boss01/Animations/AM_Boss01_A3a.AM_Boss01_A3a` | `RPGBossCloseClipSwap.h:44` | `URPGBossCloseClipSwap::A3aMontage` | Lead Contract C-275 |
| 98 | `CloseClipSwap.A3bMontage` | `TSoftObjectPtr<UAnimMontage>` | soft path | `/Game/OneBossFight/Boss01/Animations/AM_Boss01_A3b.AM_Boss01_A3b` | `RPGBossCloseClipSwap.h:47` | `URPGBossCloseClipSwap::A3bMontage` | Lead Contract C-275 |
| 99 | `Death.DeathMode` | `ERPGBossDeathMode` | enum (0=Pack, 1=Own) | `1 (OwnClip)` | `RPGBossDeath.h:51` | `URPGBossDeath::DeathMode` | Subsystem Override C281/C293 |
| 100 | `Death.DeathClip` | `TSoftObjectPtr<UAnimSequence>` | soft path | `/Game/OneBossFight/Boss01/Animations/AN_Boss01_DeathLegend.AN_Boss01_DeathLegend` | `RPGBossDeath.h:54` | `URPGBossDeath::DeathClip` | Known Native Default |
| 101 | `Death.DeathMontage` | `TSoftObjectPtr<UAnimMontage>` | soft path | `/Game/OneBossFight/Boss01/Animations/AM_Boss01_DeathLegend.AM_Boss01_DeathLegend` | `RPGBossDeath.h:57` | `URPGBossDeath::DeathMontage` | Known Native Default |
| 102 | `Death.PackDeathAbilityClassName` | `FName` | identifier | `GA_EnemyRagdollDeath_C` | `RPGBossDeath.h:60` | `URPGBossDeath::PackDeathAbilityClassName` | Known Native Default |
| 103 | `Death.PackDeathMontagesName` | `FName` | identifier | `DeathMontages` | `RPGBossDeath.h:63` | `URPGBossDeath::PackDeathMontagesName` | Known Native Default |
| 104 | `Death.PackPollSeconds` | `float` | seconds | `1.0` | `RPGBossDeath.h:66` | `URPGBossDeath::PackPollSeconds` | Known Native Default |
| 105 | `Death.PackEndTimeMultiplier` | `float` | multiplier | `1.2` | `RPGBossDeath.h:69` | `URPGBossDeath::PackEndTimeMultiplier` | Known Native Default |
| 106 | `Death.HoldAtSeconds` | `float` | seconds | `0.95` | `RPGBossDeath.h:72` | `URPGBossDeath::HoldAtSeconds` | Known Native Default |
| 107 | `Death.DyingSeconds` | `float` | seconds | `3.5` | `RPGBossDeath.h:75` | `URPGBossDeath::DyingSeconds` | Known Native Default |
| 108 | `Death.BlendInSeconds` | `float` | seconds | `0.2` | `RPGBossDeath.h:78` | `URPGBossDeath::BlendInSeconds` | Known Native Default |
| 109 | `Death.MaxClipRestarts` | `int32` | count | `0` | `RPGBossDeath.h:81` | `URPGBossDeath::MaxClipRestarts` | Lead Policy C-284 |
| 110 | `Death.bGuardPackDeath` | `bool` | dimensionless | `true` | `RPGBossDeath.h:84` | `URPGBossDeath::bGuardPackDeath` | Known Native Default |

### 4.1 Decision Breakdown for Authorship
- **Columns Definable Today with 100% Truthfulness:**
  - `FieldPath` (110 paths established by DD26 preflight contract).
  - `Type` (exact C++ reflection types).
  - `Units` (accurate physical domains).
  - `Value` (truthful stringification of current default values).
  - `SourcePath` & `SourceSite` (exact C++ header/source files and line numbers).
  - `Destination` (exact C++ component member variables).
- **Columns Requiring Owner / Lead Policy Decision:**
  - `SourceSHA256`: Compute live file SHA256 of `SourcePath`, or use an explicit catalog/content epoch hash?
  - `Origin`: Adopt standardized taxonomy (`NativeDefault`, `SubsystemOverride`, `LeadContract`, `AuthoredAsset`)?
  - `Precedence`: Formal definition of layer ordering?
  - `FirstRead`: Standardize as `"BeginPlay"`, `"OnSpawn"`, or `"OnDemand"`?
  - `Witness`: Designate verification authority (e.g. `"AuthoringToolkit-REV10"`, `"AutomationTest"`, or `"LeadReview"`)?

---

## 5. Consumers That Would Break if a Manifest Row is Wrong

If a definition's `Fields` array is malformed, incomplete, or missing required rows, five distinct system layers fail closed:

### 1. `CompileParticipantImpl` (`Source/OneBossFight/Player/RPGEncounterBinding.cpp:104-115`)
- **Empty Array Failure:**
  `if (Fields.IsEmpty()) { Result.Fail(TEXT("field manifest required")); }` (`:115`)
- **Structural Row Failures:**
  `Result.Fail(TEXT("incomplete/duplicate field-source manifest"))` (`:111`) is triggered if for ANY row:
  - `FieldPath.IsEmpty()` (missing path).
  - `Fields.Contains(FieldPath)` (duplicate path).
  - `Type.IsEmpty()`.
  - `SourcePath.IsEmpty()`.
  - `!IsSHA256(SourceSHA256)` (hash length != 64 or contains non-hex characters).
  - `SourceSite.IsEmpty()`.
  - `Origin.IsEmpty()`.
  - `Precedence.IsEmpty()`.
  - `Destination.IsEmpty()`.
  - `FirstRead.IsEmpty()`.
  - `Witness.IsEmpty()`.

### 2. `RPGBossHydrationPreflight::CompilePreflight` (`Source/OneBossFight/Player/RPGBossHydrationPreflight.cpp:347-351, :408-423`)
- **Config Manifest Absence:**
  `if (... || Config->Fields.IsEmpty() || ...)` -> Fails member with `Preflight.InvalidManifestIdentity` (`:347-350`).
- **Missing Required Path:**
  If ANY of the 110 required paths across the 12 plans is not present in `Config->Fields`:
  Fails member with `Preflight.MissingRequiredField: required manifest path <Path> is not in the config` (`:420`).

### 3. `RPGBossWorldInputCompiler::CompileWorldInput` (`Source/OneBossFight/Player/RPGBossWorldInputCompiler.cpp:58`)
- Fails closed with `WorldInput.DefinitionRejected` (if `CompileParticipant` fails) or `WorldInput.PreflightRejected` (if `CompilePreflight` fails). Returns empty `FRPGHydrationPreflightInput`.

### 4. `RPGBossWorldPreparation::PrepareWorldBatch` (`Source/OneBossFight/Player/RPGBossWorldPreparation.cpp:46`)
- Fails closed with nested `WorldInput.*` or `Preflight.*` errors. Aborts any partially allocated components and returns a null batch.

### 5. `FRPGBossPreparationRegistry::TryPrepareAndReserve` (`Source/OneBossFight/Player/RPGBossPreparationRegistry.cpp:144`)
- Refuses reservation with `EReservationFailure::InvalidInput` or `EReservationFailure::PreparationFailed`. Returns an unheld lease token.

### 6. `URPGCombatContextSubsystem::BindEncounter` (`Source/OneBossFight/Player/RPGEncounterBinding.cpp:354`)
- Checks `Field.FieldPath` presence. If the manifest does not cover the required paths, participant registration into the combat context fails.

---

*End of Analysis. Staged for Tech Lead Review.*
