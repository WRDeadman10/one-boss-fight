// Copyright One Boss Fight. All Rights Reserved.

#pragma once

#include "CoreMinimal.h"
#include "Player/RPGEncounterBinding.h"

/**
 * Typed native adapter for ONE phase transition (DD4 package 01): a selected FRPGPhaseConfig -> the public configuration fields of URPGBossPhases.
 *
 *   EntryHealthFraction -> URPGBossPhases::PhaseTwoHealthFraction
 *   SpeedMultiplier     -> MovementScale
 *   RateMultiplier      -> AttackRateScale
 *   AttackMultiplier    -> DamageScale
 *
 * The record is chosen by an EXPLICIT phase id given by the caller (never the first, the last or index 0, never by parsing a manifest Value). The legacy component represents exactly one transition,
 * from the implicit base phase to phase two, so this backend accepts exactly one record, the selected one, and refuses a longer set by name; that is a capability limit of this backend, not a change to
 * the generic definition compiler or to the asset array, and not a phase policy or a feature claim. The future planner or authoring binding must supply the selected id.
 *
 * The values come from the typed record only. Every helper checks the component and the whole selected record first and writes only afterwards: a failure leaves every field as it was. The helpers never
 * create, register or begin play on a component, never touch a pack attribute, timer or trigger, and leave every other configuration field (transition seconds, clips and roar, immunity effect, leap lock,
 * fireball settings and their disabled default, ability prefix) and every runtime cache and state untouched. The native entry multiplies rates and the native removal uses the inverse; those algorithms
 * are not changed here. An isolated phase plan is NOT a valid complete playable boss cluster: it does not mark an encounter ready and does not suppress any legacy component.
 *
 * Native capability, checked after generic validity and named (a capability of the backend, not a gameplay limit):
 *  - Speed and rate: the native reset divides by them (1/x), so a value whose float inverse is not finite is refused. Fractional values below 1 are valid when the inverse is finite.
 *  - Damage: apply adds AppliedAttack = Attack*(DamageScale-1) and the native reset subtracts it only when AppliedAttack > 0 (RPGBossPhases.cpp 368 and 390). A factor below 1 would be applied and never
 *    reversed, so it is refused by name; exactly 1 (no change) and above 1 are valid. This is the explicit capability decision that Step2Preparation/14 asked for, kept in one constant
 *    (NativeDamageScaleFloor) so that it can be changed deliberately.
 * None of this proves the real ability-rate, movement or attribute round trip; that remains later runtime evidence.
 *
 * Failures are named: the message starts with one of these tokens.
 *   InvalidComponent, WrongComponentClass, ComponentBegunPlay, ComponentAlreadyRegistered, InvalidOwner, OwnerBegunPlay,
 *   InvalidPhase.NoSelection, InvalidPhase.NoRecords, InvalidPhase.NotFound, UnsupportedNativePhaseSet,
 *   InvalidPhase.NotFinite, InvalidPhase.ThresholdOutOfRange, InvalidPhase.NotPositive, UnsupportedNativeInverse, UnsupportedNativeDamageScale
 *
 * Manifest paths: the plan lists Phases[<id>].EntryHealthFraction, .SpeedMultiplier, .RateMultiplier and .AttackMultiplier as required fields. That is metadata membership of the four typed inputs the
 * adapter reads, not provenance and not proof of a raw value; with no selected id the list is empty and the callback fails by name instead.
 */
namespace RPGBossPhaseAdapters
{
	/** The legacy component has one transition (base phase to phase two). */
	constexpr int32 NativeTransitionRecords = 1;

	/** Native reset reverses an attack increase only (AppliedAttack > 0); a damage factor below this value could not be reversed. */
	constexpr float NativeDamageScaleFloor = 1.f;

	inline constexpr const TCHAR* FieldEntryHealthFraction = TEXT("EntryHealthFraction");
	inline constexpr const TCHAR* FieldSpeedMultiplier = TEXT("SpeedMultiplier");
	inline constexpr const TCHAR* FieldRateMultiplier = TEXT("RateMultiplier");
	inline constexpr const TCHAR* FieldAttackMultiplier = TEXT("AttackMultiplier");

	/** "Phases[<id>].<Field>": the manifest path of one typed input of the selected phase. */
	ONEBOSSFIGHT_API FString PhaseFieldPath(FName PhaseId, const TCHAR* Field);

	/** Checks the selection and the whole selected record without touching any component. Returns false and a named message for the first failure. */
	ONEBOSSFIGHT_API bool ValidatePhases(const TArray<FRPGPhaseConfig>& Phases, FName SelectedPhaseId, FString& OutError);

	/** Assigns the selected phase to a URPGBossPhases (exact class). Writes nothing unless every check passed. */
	ONEBOSSFIGHT_API bool ConfigurePhases(UActorComponent& Component, const FRPGParticipantConfig& Config, FName SelectedPhaseId, FString& OutError);

	/** Plan for the existing FRPGComponentPlan mechanism: class URPGBossPhases, instance name "RPGBossPhases" (the legacy name), the selected id captured BY VALUE. */
	ONEBOSSFIGHT_API FRPGComponentPlan MakePhasePlan(FName SelectedPhaseId);
}
