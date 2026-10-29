// Copyright One Boss Fight. All Rights Reserved.
#pragma once

#include "CoreMinimal.h"
#include "Player/RPGEncounterBinding.h"

/**
 * UNWIRED typed configuration for URPGBossLowSweep, C257/C258.
 * The eight public authored fields are copied only after complete validation.
 * No runtime angle, counter, generation, enabled tick state or active flag is assigned.
 *
 * These are AUTHORED RECORD constraints chosen by C258, not existing native guards:
 * Damage >= 0; Reach > 0; 0 <= InnerRadius < Reach; BladeHeight > 0; both angles
 * within [-360,360]. No editor minimum of 1 is imposed on reach or height.
 * All SIX float fields are checked finite first (in declaration order), then the
 * domains in that order, then MoveId (not None, no whitespace/control character).
 * bEnabled may be either value; disabled records still validate completely.
 * Nothing is clamped, normalised, repaired or replaced by constructor defaults.
 *
 * Native SweepTouches uses raw Min/Max intervals: equal endpoints are a stationary
 * band and reversed endpoints are legal. This record's +/-360 limit is an authored
 * limit, NOT wrapped or multi-turn coverage. It also bounds native Lerp arithmetic.
 * Reach/InnerRadius are used with player capsule overlap; the native code itself
 * does not enforce their ordering. Native BladeHeight is a signed feet-plane test;
 * this record explicitly chooses to refuse zero/negative heights.
 *
 * MoveId is SYNTACTIC IDENTITY ONLY. Native Tick consumes URPGAttackTracker's
 * Attacks/GetTiming and active-window state; the record does not prove a matching
 * tracker entry, correct animation/timing or that a sweep ever fires.
 *
 * Configure checks exact class, live component, not registered/begun, live owner
 * not destroying/begun/beginning; all checks precede every write. It loads nothing,
 * creates/registers nothing, ticks/starts/cancels nothing and changes no tracker.
 * The plan is not inserted into preflight, preparation or reservations. It grants
 * no Ready/legacy suppression, complete-bundle, collision/damage or gameplay proof.
 * ComponentBegunPlay remains source-only in these fixtures: no LowSweep BeginPlay.
 */
namespace RPGBossLowSweepAdapters
{
	inline constexpr const TCHAR* FieldEnabled = TEXT("LowSweep.bEnabled");
	inline constexpr const TCHAR* FieldMoveId = TEXT("LowSweep.MoveId");
	inline constexpr const TCHAR* FieldDamage = TEXT("LowSweep.Damage");
	inline constexpr const TCHAR* FieldReach = TEXT("LowSweep.Reach");
	inline constexpr const TCHAR* FieldInnerRadius = TEXT("LowSweep.InnerRadius");
	inline constexpr const TCHAR* FieldBladeHeight = TEXT("LowSweep.BladeHeight");
	inline constexpr const TCHAR* FieldSweepFromDegrees = TEXT("LowSweep.SweepFromDegrees");
	inline constexpr const TCHAR* FieldSweepToDegrees = TEXT("LowSweep.SweepToDegrees");

	ONEBOSSFIGHT_API bool ValidateLowSweep(const FRPGLowSweepConfig& Record, FString& OutError);
	ONEBOSSFIGHT_API bool ConfigureLowSweep(UActorComponent& Component, const FRPGParticipantConfig& Config, FString& OutError);
	ONEBOSSFIGHT_API FRPGComponentPlan MakeLowSweepPlan();
}
