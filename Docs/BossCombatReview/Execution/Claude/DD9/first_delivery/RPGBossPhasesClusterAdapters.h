// Copyright One Boss Fight. All Rights Reserved.

#pragma once

#include "CoreMinimal.h"
#include "Player/RPGEncounterBinding.h"

/**
 * Typed native adapter for the whole URPGBossPhases authoring cluster (DD9 package 01). One call validates and assigns, atomically, every authoring field the component has:
 *
 *   selected phase (DD4):   PhaseTwoHealthFraction, MovementScale, AttackRateScale, DamageScale
 *   phase flow (DD8):       TransitionSeconds, bUseRoarClip, bPausePostureInTransition, bLockLeapUntilPhaseTwo, AttackAbilityPrefix, LeapAbilityTag
 *   fireball policy (new):  bFireballEnabled, FireballAbility, FireballCooldown, FireballMinRange, FireballMaxRange
 *   dependencies (new):     RoarClip, TransitionMontage, ImmunityEffect
 *
 * Eighteen fields, one write block, only after the lifecycle check and the WHOLE cluster passed. The earlier typed adapters each wrote a part of this component; two of their plans for one component class are
 * refused by the preflight and two sequential partial writes would not be atomic, so this combined fragment is the one that a later wiring package may register instead of them. It reuses their validators
 * (ValidatePhases, ValidatePhaseFlow) and the same lifecycle boundary, so a record they accept is accepted here and the ten fields they own receive the same values (the tests compare the result against the sequential
 * use of both older adapters as an oracle). It creates no object, registers nothing, begins nothing, ticks nothing, LOADS NOTHING (the three asset references are soft paths assigned as paths; the native BeginPlay
 * loads them later), mutates no tag and never touches the loaded objects, queues, generations, clocks, flags, counters or any attribute.
 *
 * The new records. FRPGFireballConfig and FRPGPhaseDependencyConfig carry the native field names and the native constructor defaults as authoring defaults of the NEW asset fields (old schema 1 definitions receive
 * them additively; they are not proof of any serialized or live value and never a fallback for an invalid one).
 *
 * Validation order of the cluster (first failure wins, every failure named with its field path; nothing is clamped, trimmed or replaced):
 *   (1) the selected phase (ValidatePhases tokens), (2) the phase flow (ValidatePhaseFlow tokens), (3) the fireball policy, (4) the dependencies.
 * Fireball policy, always validated whether or not the fireball is enabled: all five numbers finite (InvalidFireball.NotFinite, cooldown X then Y, then the two ranges); cooldown and ranges not negative
 * (InvalidFireball.Negative); the cooldown minimum not above the maximum (InvalidFireball.CooldownOrder, the native code would silently use the minimum for both) and the range minimum not above the maximum
 * (InvalidFireball.RangeOrder, such a window could never fire); the ability path is required only when the fireball is enabled (InvalidFireball.NoAbility) and, if set at all, must be a well-formed class path
 * (InvalidFireball.AbilityPath). Zero is valid everywhere; no ceiling is invented.
 * Dependencies: the structural form of a path only, with NO asset registry query and no load: it must be non-empty, start with '/', name an asset after the last '/' with a '.', carry no whitespace, control
 * character or sub-object ':' and a class path must end with "_C" (InvalidDependency.Malformed, InvalidDependency.NotClassPath). RoarClip is required when bUseRoarClip is true, TransitionMontage is required when it is
 * false (it is then the roar), ImmunityEffect is always required (InvalidDependency.Missing); an optional reference that is set must still be well-formed. THAT A PATH NAMES AN EXISTING OR COOKED ASSET, THAT THE
 * CLASS IS A GAMEPLAY EFFECT OR ABILITY, AND THAT THE CLIP FITS THE TRANSITION TIME ARE UNRESOLVED INTEGRATION CHECKS, not something a well-formed path proves.
 *
 * Failures are named: the message starts with one of these tokens.
 *   InvalidComponent, WrongComponentClass, ComponentBegunPlay, ComponentAlreadyRegistered, InvalidOwner, OwnerBegunPlay,
 *   InvalidPhase.* / UnsupportedNative* (selected phase, see RPGBossPhaseAdapters.h), InvalidPhaseFlow.* (see RPGBossPhaseFlowAdapters.h),
 *   InvalidFireball.NotFinite, InvalidFireball.Negative, InvalidFireball.CooldownOrder, InvalidFireball.RangeOrder, InvalidFireball.NoAbility, InvalidFireball.AbilityPath,
 *   InvalidDependency.Missing, InvalidDependency.Malformed, InvalidDependency.NotClassPath
 *
 * The fragment is UNWIRED: it is not added to the DD5 preflight and claims no readiness; it is not the stagger profile, not the wake, not a reservation and not activation.
 */
namespace RPGBossPhasesClusterAdapters
{
	/** The manifest paths of the eight new typed inputs, "<record>.<native field name>" (metadata membership only, not provenance and not proof of a value). */
	inline constexpr const TCHAR* FieldFireballEnabled = TEXT("Fireball.bFireballEnabled");
	inline constexpr const TCHAR* FieldFireballAbility = TEXT("Fireball.FireballAbility");
	inline constexpr const TCHAR* FieldFireballCooldown = TEXT("Fireball.FireballCooldown");
	inline constexpr const TCHAR* FieldFireballMinRange = TEXT("Fireball.FireballMinRange");
	inline constexpr const TCHAR* FieldFireballMaxRange = TEXT("Fireball.FireballMaxRange");
	inline constexpr const TCHAR* FieldRoarClip = TEXT("PhaseDependencies.RoarClip");
	inline constexpr const TCHAR* FieldTransitionMontage = TEXT("PhaseDependencies.TransitionMontage");
	inline constexpr const TCHAR* FieldImmunityEffect = TEXT("PhaseDependencies.ImmunityEffect");

	/** Checks the typed fireball record without touching any component; OutError is cleared first and carries a named failure on false. */
	ONEBOSSFIGHT_API bool ValidateFireball(const FRPGFireballConfig& Fireball, FString& OutError);

	/** Checks the typed dependency record (structure only, no registry, no load); bUseRoarClip comes from the phase flow record. */
	ONEBOSSFIGHT_API bool ValidatePhaseDependencies(const FRPGPhaseDependencyConfig& Dependencies, bool bUseRoarClip, FString& OutError);

	/** The whole cluster in the documented order. */
	ONEBOSSFIGHT_API bool ValidatePhasesCluster(const FRPGParticipantConfig& Config, FName SelectedPhaseId, FString& OutError);

	/** Assigns the eighteen fields of the cluster to a URPGBossPhases (exact class). Writes nothing unless every check passed. */
	ONEBOSSFIGHT_API bool ConfigurePhasesCluster(UActorComponent& Component, const FRPGParticipantConfig& Config, FName SelectedPhaseId, FString& OutError);

	/** Unwired plan fragment: class URPGBossPhases, the legacy instance name "RPGBossPhases", the selected id captured BY VALUE; required fields: the four phase paths (empty selection: none, the callback fails by
	 *  name), then the six PhaseFlow.* paths, the five Fireball.* paths and the three PhaseDependencies.* paths. */
	ONEBOSSFIGHT_API FRPGComponentPlan MakePhasesClusterPlan(FName SelectedPhaseId);
}
