// Copyright One Boss Fight. All Rights Reserved.
#pragma once
#include "CoreMinimal.h"
#include "Player/RPGEncounterBinding.h"

/**
 * C262/C263/C264 UNWIRED authored Shockwave record; eight configuration writes only.
 * All SIX floats are finite-checked first, then authored domains in declaration
 * order, then syntactic MoveId. Disabled records still validate fully.
 * Damage>=0 has no ceiling: it is passed as health damage, not used to advance
 * the wave or band. StartRadius>=0, MaxRadius>0 and >StartRadius, Speed>0,
 * Thickness>0, JumpClearance>0; all five are <=MaxAuthoredMagnitude.
 * These are AUTHORED RECORD CONTRACTS, NOT native guards or tuning approval.
 * The native editor minimum1 does not impose a runtime floor; sub-1 is legal.
 *
 * The 1e6 (10km, or cm/s) ceiling screens float-extreme inputs, not arena balance.
 * Reasoning only: assuming a finite nonnegative DeltaTime below about1e30 seconds,
 * one Radius+Speed*DeltaTime step and Radius+Thickness*0.5 remain finite. The
 * native code still has NO finite guard and this does NOT cover unrestricted
 * DeltaTime, nonfinite world geometry or actual runtime safety/performance.
 * A valid record cannot have StartRadius==ceiling because MaxRadius must be
 * strictly greater and also <=ceiling. The per-field ceiling itself is inclusive.
 *
 * MoveId is SYNTACTIC IDENTITY ONLY: no tracker entry/window/firing resolution.
 * No runtime active/resolved flags, radius/origin/ground, counter/generation or
 * tick flag is assigned. Exact-class/lifecycle/whole-record validation precedes
 * every write; no load/create/register/BeginPlay/Tick/launch/cancel operation.
 * ComponentBegunPlay remains source-only in fixtures. The plan stays outside
 * preflight/preparation/reservations: no Ready/legacy suppression or activation.
 */
namespace RPGBossShockwaveAdapters
{
	inline constexpr float MaxAuthoredMagnitude = 1.0e6f;
	inline constexpr const TCHAR* FieldEnabled = TEXT("Shockwave.bEnabled");
	inline constexpr const TCHAR* FieldMoveId = TEXT("Shockwave.MoveId");
	inline constexpr const TCHAR* FieldDamage = TEXT("Shockwave.Damage");
	inline constexpr const TCHAR* FieldStartRadius = TEXT("Shockwave.StartRadius");
	inline constexpr const TCHAR* FieldMaxRadius = TEXT("Shockwave.MaxRadius");
	inline constexpr const TCHAR* FieldSpeed = TEXT("Shockwave.Speed");
	inline constexpr const TCHAR* FieldThickness = TEXT("Shockwave.Thickness");
	inline constexpr const TCHAR* FieldJumpClearance = TEXT("Shockwave.JumpClearance");
	ONEBOSSFIGHT_API bool ValidateShockwave(const FRPGShockwaveConfig& Record, FString& OutError);
	ONEBOSSFIGHT_API bool ConfigureShockwave(UActorComponent& Component, const FRPGParticipantConfig& Config, FString& OutError);
	ONEBOSSFIGHT_API FRPGComponentPlan MakeShockwavePlan();
}
