// Copyright One Boss Fight. All Rights Reserved.
#pragma once
#include "CoreMinimal.h"
#include "Player/RPGEncounterBinding.h"

/** C281/C284 UNWIRED AUTHORED RECORD CONTRACTS, not native guards or tuning.
 * Five floats finite first, then enum, numeric domains, names and BOTH soft paths.
 * PackEndTimeMultiplier zero means OFF; both mode values and guard bools legal.
 * Restarts int32 in [0,1000000] closes the per-death equality-branch increment
 * overflow reasoning. Cumulative ClipRestartCount, external time/Age narrowing
 * and playback/asset timing remain separate residual hazards, not certified.
 * Native Attach internally returns Existing without assigning Mode: typed mode
 * remains authoritative on reuse. No second-instance claim, race/reservation or
 * activation-order guarantee. Constructor enables tick; first Tick preloads only
 * the selected mode. Live pack ability reflection, ragdoll/pose behaviour and
 * KI-083 pack destruction/remains EndPlay behaviour are UNRESOLVED here.
 * Both paths required uniformly by authored choice, no mode fallback, load,
 * registry/mount/class/existence query. Full validation precedes all12 writes.
 * Same exact live/unregistered/not-begun component/live not-begun owner boundary.
 * No runtime state, loaded clips or remains touched, no BeginPlay/Tick/Attach,
 * pack ability, remains or test knob invoked. No Ready/legacy suppression.
 */
namespace RPGBossDeathAdapters
{
	inline constexpr float MaxAuthoredMagnitude = 1.0e6f;
	inline constexpr int32 MaxAuthoredRestarts = 1000000;
	inline constexpr const TCHAR* FieldDeathMode = TEXT("Death.DeathMode");
	inline constexpr const TCHAR* FieldDeathClip = TEXT("Death.DeathClip");
	inline constexpr const TCHAR* FieldDeathMontage = TEXT("Death.DeathMontage");
	inline constexpr const TCHAR* FieldPackDeathAbilityClassName = TEXT("Death.PackDeathAbilityClassName");
	inline constexpr const TCHAR* FieldPackDeathMontagesName = TEXT("Death.PackDeathMontagesName");
	inline constexpr const TCHAR* FieldPackPollSeconds = TEXT("Death.PackPollSeconds");
	inline constexpr const TCHAR* FieldPackEndTimeMultiplier = TEXT("Death.PackEndTimeMultiplier");
	inline constexpr const TCHAR* FieldHoldAtSeconds = TEXT("Death.HoldAtSeconds");
	inline constexpr const TCHAR* FieldDyingSeconds = TEXT("Death.DyingSeconds");
	inline constexpr const TCHAR* FieldBlendInSeconds = TEXT("Death.BlendInSeconds");
	inline constexpr const TCHAR* FieldMaxClipRestarts = TEXT("Death.MaxClipRestarts");
	inline constexpr const TCHAR* FieldbGuardPackDeath = TEXT("Death.bGuardPackDeath");
	ONEBOSSFIGHT_API bool ValidateDeath(const FRPGDeathConfig& Record, FString& OutError);
	ONEBOSSFIGHT_API bool ConfigureDeath(UActorComponent& Component, const FRPGParticipantConfig& Config, FString& OutError);
	ONEBOSSFIGHT_API FRPGComponentPlan MakeDeathPlan();
}
