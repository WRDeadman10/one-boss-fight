// Copyright One Boss Fight. All Rights Reserved.

#pragma once

#include "CoreMinimal.h"
#include "Player/RPGEncounterBinding.h"

/**
 * Typed native adapter for the whole URPGBossStagger authoring cluster (DD10 package 01). One call validates and assigns, atomically, every authoring field the component has:
 *
 *   stagger scalar policy (DD7): StaggerSeconds, FreezeAtPosition, CriticalMultiplier, RiposteRange, RiposteConeDegrees, RiposteFacingDegrees, RiposteArmSeconds, RipostePlayerStartGap,
 *                                RiposteAlignSeconds, RiposteImpactSeconds, RiposteBaseDamage, CooldownSeconds, GetUpRate, bHoldPostureAtZero
 *   stagger profile (new):       bUseClips, bUseRiposteClips, bCriticalOnEveryHit, HitStunAbilityClassName, FallMontage, GetUpMontage, FallClip, DownClip, RipostePlayerClip, RiposteBossClip, ImmunityEffect
 *
 * Twenty-five fields, one write block, only after the lifecycle check and the WHOLE cluster passed. The earlier DD7 adapter wrote only the 14 scalar fields; two plans for one component class are
 * refused by the preflight, so this combined fragment is the one that a later wiring package may register instead. It reuses the DD7 validator (ValidateStaggerPolicy) and the same lifecycle boundary,
 * so the scalar policy is validated exactly as before and the fourteen fields it owns receive the same values (the tests compare the result against the older adapter as an oracle).
 * It creates no object, registers nothing, begins nothing, ticks nothing, LOADS NOTHING (the seven asset references are soft paths assigned as paths; the native BeginPlay loads them later),
 * mutates no tag and never touches the loaded objects, queues, generations, clocks, flags, counters or any attribute.
 *
 * The new record FRPGStaggerProfileConfig carries the native field names and the native constructor defaults as authoring defaults of the NEW asset fields (old schema 1 definitions receive
 * them additively; they are not proof of any serialized or live value and never a fallback for an invalid one).
 *
 * Validation order of the cluster (first failure wins, every failure named with its field path; nothing is clamped, trimmed or replaced):
 *   (1) the stagger policy (ValidateStaggerPolicy tokens), (2) the stagger profile.
 * Stagger profile validation:
 *   - HitStunAbilityClassName not None (InvalidStaggerProfile.NoHitStunClass).
 *   - References, in field order: FallMontage, GetUpMontage, FallClip, DownClip, RipostePlayerClip, RiposteBossClip, ImmunityEffect.
 *     Checked for path structure only (no asset registry query and no load): starts with '/', <package>.<asset>, no whitespace/control/':', class paths end in '_C' or native '/Script/'.
 *     Required (InvalidDependency.Missing): FallMontage and GetUpMontage when bUseClips is false; FallClip and DownClip when bUseClips is true; RipostePlayerClip and RiposteBossClip when bUseRiposteClips is true; ImmunityEffect always.
 *     A set optional reference must still be well-formed (InvalidDependency.Malformed, InvalidDependency.NotClassPath).
 *   - bCriticalOnEveryHit: both true and false are structurally valid.
 *
 * Failures are named: the message starts with one of these tokens.
 *   InvalidComponent, WrongComponentClass, ComponentBegunPlay, ComponentAlreadyRegistered, InvalidOwner, OwnerBegunPlay,
 *   InvalidStagger.* / UnsupportedNativeCritical (see RPGBossStaggerPolicyAdapters.h),
 *   InvalidStaggerProfile.NoHitStunClass, InvalidDependency.Missing, InvalidDependency.Malformed, InvalidDependency.NotClassPath
 *
 * The fragment is UNWIRED: it is not added to the DD5 preflight and claims no readiness; it is not the wake, not a reservation and not activation.
 */
namespace RPGBossStaggerClusterAdapters
{
	/** The manifest paths of the eleven new typed profile inputs, "<record>.<native field name>" (metadata membership only, not provenance and not proof of a value). */
	inline constexpr const TCHAR* FieldUseClips = TEXT("StaggerProfile.bUseClips");
	inline constexpr const TCHAR* FieldUseRiposteClips = TEXT("StaggerProfile.bUseRiposteClips");
	inline constexpr const TCHAR* FieldCriticalOnEveryHit = TEXT("StaggerProfile.bCriticalOnEveryHit");
	inline constexpr const TCHAR* FieldHitStunAbilityClassName = TEXT("StaggerProfile.HitStunAbilityClassName");
	inline constexpr const TCHAR* FieldFallMontage = TEXT("StaggerProfile.FallMontage");
	inline constexpr const TCHAR* FieldGetUpMontage = TEXT("StaggerProfile.GetUpMontage");
	inline constexpr const TCHAR* FieldFallClip = TEXT("StaggerProfile.FallClip");
	inline constexpr const TCHAR* FieldDownClip = TEXT("StaggerProfile.DownClip");
	inline constexpr const TCHAR* FieldRipostePlayerClip = TEXT("StaggerProfile.RipostePlayerClip");
	inline constexpr const TCHAR* FieldRiposteBossClip = TEXT("StaggerProfile.RiposteBossClip");
	inline constexpr const TCHAR* FieldImmunityEffect = TEXT("StaggerProfile.ImmunityEffect");

	/** Checks the typed stagger profile record without touching any component; OutError is cleared first and carries a named failure on false. */
	ONEBOSSFIGHT_API bool ValidateStaggerProfile(const FRPGStaggerProfileConfig& Profile, FString& OutError);

	/** The whole stagger cluster in the documented order (policy then profile). */
	ONEBOSSFIGHT_API bool ValidateStaggerCluster(const FRPGParticipantConfig& Config, FString& OutError);

	/** Assigns the twenty-five fields of the cluster to a URPGBossStagger (exact class). Writes nothing unless every check passed. */
	ONEBOSSFIGHT_API bool ConfigureStaggerCluster(UActorComponent& Component, const FRPGParticipantConfig& Config, FString& OutError);

	/** Unwired plan fragment: class URPGBossStagger, legacy instance name "RPGBossStagger", 25 required paths: 14 StaggerPolicy.* in order, then 11 StaggerProfile.* in order. */
	ONEBOSSFIGHT_API FRPGComponentPlan MakeStaggerClusterPlan();
}
