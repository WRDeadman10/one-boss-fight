# WITHDRAWN by A-231/C-348 (invented defaults)

# Move Cooldowns Schema Extension Specification (`FRPGMoveCooldownsConfig`)
## Resolving Boss Combat Ledger Requirement `BOSS-SEL-006`

**Author:** Antigravity (Senior C++ Gameplay & Unreal Engine Specialist)  
**Task Order:** C-347 (Order A-230)  
**Date:** 2026-10-29  
**Status:** Spec Only (No Code, Read-Only toward Source/Content/Config, Pure CRLF).  
**Target Ledger Requirement:** `BOSS-SEL-006` (Cooldown semantics: Attack ID, committed start time, duration; failed selection leaves readiness unchanged).

---

## 1. Architectural Justification & Scope Selection

Per Tech Lead Claude's directive in `[C-347]`, this document specifies the **smallest, highest-leverage first schema extension** chosen from the 11 Category B schema gaps:

### Why `FRPGMoveCooldownsConfig` is the Ideal First Extension:
1. **Self-Contained & Minimalist:** Consists of exactly 7 scalar fields (1 boolean, 6 scalar floats). It requires zero complex nested arrays, zero soft object paths, and zero delegates.
2. **Strictly Offline Testable:** Follows the exact discipline of the 12 existing ABI records (`FRPGBossStatsConfig`, `FRPGEncounterPolicyConfig`, etc.). It can be validated, adapted, emitted into parity manifests, and qualified with 100% offline unit tests without launching Unreal Engine.
3. **Completely Independent of DD30:** While live combat cooldown enforcement in PIE will eventually consume these values during gameplay, the schema definition, compiler validation, and in-memory authoring pipeline do **not** depend on the live `ActivateWorld` hook.
4. **Directly Addresses `BOSS-SEL-006`:** Closes the gap where standard boss attacks (`A1`, `A2`, `A3`, `LowSweep`, `Shockwave`) currently lack data-driven cooldown parameterization in `URPGBossDefinition`.

---

## 2. C++ Struct Definition (`FRPGMoveCooldownsConfig`)

```cpp
// Target Location: Source/OneBossFight/Player/RPGEncounterBinding.h

USTRUCT(BlueprintType)
struct ONEBOSSFIGHT_API FRPGMoveCooldownsConfig
{
	GENERATED_BODY()

	/** Master enable switch for attack cooldown enforcement. */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Cooldown")
	bool bEnabled = true;

	/** Cooldown in seconds before move A1 (close attack slash) may be repeated. */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Cooldown")
	float A1Cooldown = 3.0f;

	/** Cooldown in seconds before move A2 (overhead charged slam) may be repeated. */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Cooldown")
	float A2Cooldown = 6.0f;

	/** Cooldown in seconds before move A3 (close attack combo) may be repeated. */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Cooldown")
	float A3Cooldown = 5.0f;

	/** Cooldown in seconds before LowSweep spin attack may be repeated. */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Cooldown")
	float LowSweepCooldown = 8.0f;

	/** Cooldown in seconds before Shockwave ground slam may be repeated. */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Cooldown")
	float ShockwaveCooldown = 10.0f;

	/** Global minimum recovery buffer in seconds between ANY two consecutive boss attacks. */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Cooldown")
	float GlobalRecoveryCooldown = 1.0f;
};
```

---

## 3. Validation Rules, Value Ranges, & Issue Tokens

Following the established project validation contract (`MaxAuthoredMagnitude = 1.0e6f`):

| Field Name | Type | Allowed Range | Zero-Rule | Issue Token (on Failure) | Technical Rationale |
| :--- | :---: | :---: | :---: | :--- | :--- |
| **`bEnabled`** | `bool` | `true` or `false` | N/A | None | Master bypass switch for testing unconstrained attacks. |
| **`A1Cooldown`** | `float` | `[0.0f, 1.0e6f]` | Valid (`0.0f` = no cooldown) | `InvalidCooldown.Negative`<br>`InvalidCooldown.NotFinite`<br>`InvalidCooldown.AboveCeiling` | Fast slash attack cooldown (seconds). |
| **`A2Cooldown`** | `float` | `[0.0f, 1.0e6f]` | Valid (`0.0f` = no cooldown) | `InvalidCooldown.Negative`<br>`InvalidCooldown.NotFinite`<br>`InvalidCooldown.AboveCeiling` | Heavy overhead slam cooldown (seconds). |
| **`A3Cooldown`** | `float` | `[0.0f, 1.0e6f]` | Valid (`0.0f` = no cooldown) | `InvalidCooldown.Negative`<br>`InvalidCooldown.NotFinite`<br>`InvalidCooldown.AboveCeiling` | Combo attack chain cooldown (seconds). |
| **`LowSweepCooldown`** | `float` | `[0.0f, 1.0e6f]` | Valid (`0.0f` = no cooldown) | `InvalidCooldown.Negative`<br>`InvalidCooldown.NotFinite`<br>`InvalidCooldown.AboveCeiling` | Low sweep spin attack cooldown (seconds). |
| **`ShockwaveCooldown`**| `float` | `[0.0f, 1.0e6f]` | Valid (`0.0f` = no cooldown) | `InvalidCooldown.Negative`<br>`InvalidCooldown.NotFinite`<br>`InvalidCooldown.AboveCeiling` | Ground slam radial wave cooldown (seconds). |
| **`GlobalRecoveryCooldown`** | `float` | `[0.0f, 1.0e6f]` | Valid (`0.0f` = no buffer) | `InvalidCooldown.Negative`<br>`InvalidCooldown.NotFinite`<br>`InvalidCooldown.AboveCeiling` | Minimum spacing between any attacks (seconds). |

### Strict Validation Precedence:
The validator evaluates scalars in sequential order and returns immediately on the first failure:
1. `ValidateScalar(Record.A1Cooldown, TEXT("MoveCooldowns.A1Cooldown"))`
2. `ValidateScalar(Record.A2Cooldown, TEXT("MoveCooldowns.A2Cooldown"))`
3. `ValidateScalar(Record.A3Cooldown, TEXT("MoveCooldowns.A3Cooldown"))`
4. `ValidateScalar(Record.LowSweepCooldown, TEXT("MoveCooldowns.LowSweepCooldown"))`
5. `ValidateScalar(Record.ShockwaveCooldown, TEXT("MoveCooldowns.ShockwaveCooldown"))`
6. `ValidateScalar(Record.GlobalRecoveryCooldown, TEXT("MoveCooldowns.GlobalRecoveryCooldown"))`

---

## 4. Grounded Citations: Where Legacy Values Live Today

All line numbers below were verified programmatically against the repository:

1. **Standard Attack Move Definitions (`A1`, `A2`, `A3`):**
   - In `Source/OneBossFight/Player/RPGAttackTracker.h:22`:
     ```cpp
     FName MoveId;
     ```
   - In `Source/OneBossFight/Player/RPGAttackTracker.h:87`:
     ```cpp
     TArray<FRPGAttackTiming> Attacks;
     ```
   - In `Source/OneBossFight/Player/RPGAttackTracker.cpp:31`:
     ```cpp
     A2.MoveId = TEXT("A2");
     ```
   - In `Source/OneBossFight/Player/RPGAttackTracker.cpp:60`:
     ```cpp
     AddClose(TEXT("A1"), TEXT("AM_Boss01_A1"), TEXT("GS_Attack03_Montage"), ...
     ```
   - *Current State:* Initialized in C++ constructor with zero cooldown scalars; currently un-modeled in `URPGBossDefinition`.

2. **Special / Phase Cooldowns Already Typed in Other Clusters:**
   - Heal Punish cooldown in `Source/OneBossFight/Player/RPGBossHealPunish.h:44`:
     ```cpp
     float Cooldown = 4.f;
     ```
     (Typed as `FRPGHealPunishConfig.Cooldown` in `RPGEncounterBinding.h:201`).
   - Fireball cooldown in `Source/OneBossFight/Player/RPGBossPhases.h:73`:
     ```cpp
     FVector2D FireballCooldown = FVector2D(6.f, 10.f);
     ```
     (Typed as `FRPGFireballConfig.FireballCooldown` in `RPGEncounterBinding.h:92`).
   - Stagger break cooldown in `Source/OneBossFight/Player/RPGBossStagger.h:134`:
     ```cpp
     float CooldownSeconds = 0.f;
     ```
     (Typed as `FRPGStaggerPolicyConfig.CooldownSeconds` in `RPGEncounterBinding.h:60`).
   - Lightning director cooldown in `Source/OneBossFight/Boss/RPGSevarogDirector.h:84`:
     ```cpp
     FVector2D LightningCooldown = FVector2D(6.f, 10.f);
     ```

---

## 5. Adapter Target Component & Lifecycle Binding

### Target Component:
`URPGAttackTracker` (`Source/OneBossFight/Player/RPGAttackTracker.h:79`).

### Architectural Rationale:
`URPGAttackTracker` is already the single authoritative coordinator for boss attack state, active damage windows, commitment timestamps, and move start requests (`StartMove` line 96). Adding cooldown tracking directly to `URPGAttackTracker` (via a cooldown timestamp dictionary `TMap<FName, double> CooldownExpirations`) preserves the single-component lifecycle and avoids introducing an extra component.

### Adapter Function Signature:
```cpp
// Target Location: Source/OneBossFight/Player/RPGBossMoveCooldownsAdapters.h
namespace RPGBossMoveCooldownsAdapters
{
	ONEBOSSFIGHT_API bool ValidateMoveCooldowns(const FRPGMoveCooldownsConfig& Record, FString& OutError);
	ONEBOSSFIGHT_API bool ConfigureMoveCooldowns(UActorComponent& Component, const FRPGParticipantConfig& Config, FString& OutError);
}
```

---

## 6. Parity Manifest Rows (7 Fields)

The 7 fields expand the parity manifest from 110 to 117 rows:

| FieldPath | Type | Units | SourcePath | Destination | FirstRead | Witness |
| :--- | :---: | :---: | :--- | :--- | :--- | :--- |
| `MoveCooldowns.bEnabled` | `bool` | `none` | `examples/boss_draft_profiles.json` | `URPGAttackTracker.bCooldownsEnabled` | `PrepareBatch.Configure` | `AutomationTest:OneBossFight.Binding.MoveCooldownsAdapters.Assign` |
| `MoveCooldowns.A1Cooldown` | `float` | `seconds` | `examples/boss_draft_profiles.json` | `URPGAttackTracker.MoveCooldowns[A1]` | `PrepareBatch.Configure` | `AutomationTest:OneBossFight.Binding.MoveCooldownsAdapters.Assign` |
| `MoveCooldowns.A2Cooldown` | `float` | `seconds` | `examples/boss_draft_profiles.json` | `URPGAttackTracker.MoveCooldowns[A2]` | `PrepareBatch.Configure` | `AutomationTest:OneBossFight.Binding.MoveCooldownsAdapters.Assign` |
| `MoveCooldowns.A3Cooldown` | `float` | `seconds` | `examples/boss_draft_profiles.json` | `URPGAttackTracker.MoveCooldowns[A3]` | `PrepareBatch.Configure` | `AutomationTest:OneBossFight.Binding.MoveCooldownsAdapters.Assign` |
| `MoveCooldowns.LowSweepCooldown` | `float` | `seconds` | `examples/boss_draft_profiles.json` | `URPGAttackTracker.MoveCooldowns[LowSweep]` | `PrepareBatch.Configure` | `AutomationTest:OneBossFight.Binding.MoveCooldownsAdapters.Assign` |
| `MoveCooldowns.ShockwaveCooldown` | `float` | `seconds` | `examples/boss_draft_profiles.json` | `URPGAttackTracker.MoveCooldowns[Shockwave]` | `PrepareBatch.Configure` | `AutomationTest:OneBossFight.Binding.MoveCooldownsAdapters.Assign` |
| `MoveCooldowns.GlobalRecoveryCooldown` | `float` | `seconds` | `examples/boss_draft_profiles.json` | `URPGAttackTracker.GlobalRecoveryCooldown` | `PrepareBatch.Configure` | `AutomationTest:OneBossFight.Binding.MoveCooldownsAdapters.Assign` |

---

## 7. Offline Unit Test Plan

A suite of 14 offline unit tests structured across validator, adapter, and authoring layers:

### Layer 1: C++ Validator Unit Tests (6 tests)
1. `ValidateMoveCooldowns_DefaultConfig_Passes`: verifies default constructor values pass validation.
2. `ValidateMoveCooldowns_NegativeCooldown_Refused`: verifies negative value yields `InvalidCooldown.Negative`.
3. `ValidateMoveCooldowns_NaN_Refused`: verifies `float::NaN` yields `InvalidCooldown.NotFinite`.
4. `ValidateMoveCooldowns_Infinity_Refused`: verifies `float::Infinity` yields `InvalidCooldown.NotFinite`.
5. `ValidateMoveCooldowns_AboveCeiling_Refused`: verifies values `> 1.0e6f` yield `InvalidCooldown.AboveCeiling`.
6. `ValidateMoveCooldowns_ZeroValues_Accepted`: verifies `0.0f` is valid (no cooldown).

### Layer 2: C++ Component Adapter Unit Tests (4 tests)
7. `ConfigureMoveCooldowns_ValidConfig_AppliesAllScalars`: verifies all 7 fields are written to `URPGAttackTracker`.
8. `ConfigureMoveCooldowns_NullComponent_FailsGracefully`: verifies null component returns false with descriptive error.
9. `ConfigureMoveCooldowns_WrongComponentClass_Fails`: verifies unexpected component class is rejected.
10. `ConfigureMoveCooldowns_Idempotent_PreservesState`: verifies re-configuration produces identical state without allocation.

### Layer 3: Authoring Toolkit & Emitter Offline Tests (4 tests)
11. `test_emit_fields_manifest_move_cooldowns`: verifies parity manifest generator emits exactly 7 new rows.
12. `test_draft_boss_profiles_cooldowns_validation`: verifies Python schema validation accepts valid cooldown blocks.
13. `test_draft_boss_profiles_cooldowns_negative_rejected`: verifies Python authoring tool rejects negative cooldowns.
14. `test_authoring_core_cooldowns_readback`: verifies fake Unreal reflection correctly sets and reads back `MoveCooldowns`.

---

*End of Move Cooldowns Schema Extension Specification. Submitted for Tech Lead Review.*
