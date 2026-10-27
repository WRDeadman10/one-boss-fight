// Copyright One Boss Fight. All Rights Reserved.

#pragma once

#include "CoreMinimal.h"
#include "Player/RPGEncounterBinding.h"

/**
 * Typed native adapter for the phase flow policy (DD8 package 01): FRPGPhaseFlowConfig -> exactly six public fields of URPGBossPhases, with the names of the native component:
 *
 *   TransitionSeconds, bUseRoarClip, bPausePostureInTransition, bLockLeapUntilPhaseTwo, AttackAbilityPrefix, LeapAbilityTag
 *
 * Nothing else is assigned. The selected phase record (PhaseTwoHealthFraction, MovementScale, AttackRateScale, DamageScale) belongs to the phase adapter and is never touched here, and neither are the
 * fireball fields (enable, ability, cooldown, range), the soft asset references (roar clip, transition montage, immunity effect, fireball ability), the cached loaded objects, the queues, generations, transition
 * clocks, phase flags, the leap blocked state, the counters or any attribute. This record closes the phase flow authoring fields only; it is NOT the phase presentation dependency profile, not a complete phase
 * policy and not activation.
 *
 * One validator, two users: ValidatePhaseFlow is called by the definition compiler (RPGCombatHydration::CompileParticipantImpl) and by ConfigurePhaseFlow, so a record that the compiler accepts is exactly a
 * record the assignment accepts. Checks run in this order, each failure named with its field path; an invalid value is refused and NEVER replaced by a default:
 *   (1) TransitionSeconds finite; (2) TransitionSeconds not negative (zero is valid; the native transition end is LastTransitionStart + TransitionSeconds, so no invented editor floor such as the native
 *   ClampMin is applied); (3) AttackAbilityPrefix neither empty nor only whitespace; (4) LeapAbilityTag not None.
 * Authored values are never trimmed, normalized or replaced, no gameplay tag is requested or registered, and no manifest Value text is read. The prefix and the tag state an explicit identity only: that an
 * ability class matches the prefix or that the tag is registered is an UNRESOLVED integration check before activation, not something a non-empty value proves. No bound is derived from a montage or clip duration:
 * the compatibility of the roar and the hold with the real clips needs later dependency and runtime proof.
 *
 * ConfigurePhaseFlow checks the component and the whole record first and writes only afterwards: a failure leaves every field as it was. It creates no object, registers nothing, begins nothing, ticks nothing,
 * loads nothing, mutates no tag, looks up no actor and invokes no callback. The plan is an UNWIRED assignment fragment with the legacy instance name; it is not added to the DD5 preflight and must not be combined
 * sequentially with the phase adapter's plan (two plans for one component class are refused, and two sequential partial writes would not be atomic). A later combined Phases plan has to validate the selected
 * phase, this flow record and the dependency record in full before writing to the one component once. This fragment claims no readiness and suppresses no legacy component.
 *
 * Failures are named: the message starts with one of these tokens.
 *   InvalidComponent, WrongComponentClass, ComponentBegunPlay, ComponentAlreadyRegistered, InvalidOwner, OwnerBegunPlay,
 *   InvalidPhaseFlow.NotFinite, InvalidPhaseFlow.Negative, InvalidPhaseFlow.EmptyPrefix, InvalidPhaseFlow.NoLeapTag
 */
namespace RPGBossPhaseFlowAdapters
{
	/** The manifest paths of the six typed inputs, "PhaseFlow.<native field name>" (metadata membership only, not provenance and not proof of a value). */
	inline constexpr const TCHAR* FieldTransitionSeconds = TEXT("PhaseFlow.TransitionSeconds");
	inline constexpr const TCHAR* FieldUseRoarClip = TEXT("PhaseFlow.bUseRoarClip");
	inline constexpr const TCHAR* FieldPausePostureInTransition = TEXT("PhaseFlow.bPausePostureInTransition");
	inline constexpr const TCHAR* FieldLockLeapUntilPhaseTwo = TEXT("PhaseFlow.bLockLeapUntilPhaseTwo");
	inline constexpr const TCHAR* FieldAttackAbilityPrefix = TEXT("PhaseFlow.AttackAbilityPrefix");
	inline constexpr const TCHAR* FieldLeapAbilityTag = TEXT("PhaseFlow.LeapAbilityTag");

	/** Checks the typed record without touching any component; OutError is cleared first and carries a named failure on false. */
	ONEBOSSFIGHT_API bool ValidatePhaseFlow(const FRPGPhaseFlowConfig& Flow, FString& OutError);

	/** Assigns the six fields of Config.PhaseFlow to a URPGBossPhases (exact class). Writes nothing unless every check passed. */
	ONEBOSSFIGHT_API bool ConfigurePhaseFlow(UActorComponent& Component, const FRPGParticipantConfig& Config, FString& OutError);

	/** Unwired plan fragment: class URPGBossPhases, the legacy instance name "RPGBossPhases", the six typed field paths as required fields (in field order). */
	ONEBOSSFIGHT_API FRPGComponentPlan MakePhaseFlowPlan();
}
