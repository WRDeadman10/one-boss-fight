// Copyright One Boss Fight. All Rights Reserved.

#pragma once

#include "CoreMinimal.h"
#include "Player/RPGEncounterBinding.h"

/**
 * Typed native adapter for the stagger and riposte scalar policy (DD7 package 01): FRPGStaggerPolicyConfig -> exactly fourteen public fields of URPGBossStagger, thirteen floats and one bool, with the names of
 * the native component:
 *
 *   StaggerSeconds, FreezeAtPosition, CriticalMultiplier, RiposteRange, RiposteConeDegrees, RiposteFacingDegrees, RiposteArmSeconds, RipostePlayerStartGap,
 *   RiposteAlignSeconds, RiposteImpactSeconds, RiposteBaseDamage, CooldownSeconds, GetUpRate, bHoldPostureAtZero
 *
 * Nothing else is assigned. bCriticalOnEveryHit and the test knobs, bUseClips and bUseRiposteClips, the clip, montage, effect and class references (FallClip, DownClip, the riposte clips, FallMontage, GetUpMontage,
 * ImmunityEffect, HitStunAbilityClassName), the cached loaded clips, the phase, the timers, the counters, health, poise and held state are never touched. The asset dependencies and the mode policy are still open
 * and need a later reviewed profile package: this scalar policy is NOT the full stagger profile and not a ready cluster, and nothing here substitutes a source path.
 *
 * One validator, two users: ValidateStaggerPolicy is called by the definition compiler (RPGCombatHydration::CompileParticipantImpl) and by ConfigureStaggerPolicy, so a policy that the compiler accepts is exactly a
 * policy the assignment accepts. An invalid value is refused by name and never clamped or replaced by a default. Checks run in this order: (1) EVERY scalar finite; (2) the generic domains, in field order;
 * (3) the native capability of the critical multiplier.
 *   - not negative (zero keeps the native immediate, empty-window or no-cooldown meaning): StaggerSeconds, FreezeAtPosition, RiposteRange, RiposteArmSeconds, RipostePlayerStartGap, RiposteImpactSeconds,
 *     RiposteBaseDamage, CooldownSeconds;
 *   - strictly positive, because the native code divides by them (T / RiposteAlignSeconds, Length / GetUpRate): RiposteAlignSeconds, GetUpRate;
 *   - within [0, 360] degrees, so the angular full-cone meaning is kept without an invented editor floor: RiposteConeDegrees, RiposteFacingDegrees;
 *   - CriticalMultiplier at least 1: the native critical hit takes Health - Loss * (CriticalMultiplier - 1), so a multiplier below 1 would ADD health. That is a capability of the native backend, classified as
 *     UnsupportedNativeCritical, not a balancing decision. Exactly 1 is valid.
 * No timing or clip-length bound is invented: clip and montage compatibility, an impact before the clip duration and the numerical safety of a play rate need later dependency and runtime proof. The native
 * ClampMin and ClampMax values are editor metadata and are not runtime rules here. Assigning an unwired record approves no tuning and enables nothing.
 *
 * ConfigureStaggerPolicy checks the component and the whole policy first and writes only afterwards: a failure leaves every field as it was. It creates no object, registers nothing, begins nothing, plays no montage,
 * starts no timer, reads no attribute and looks up no actor. The plan is an UNWIRED assignment fragment with the legacy instance name; it is not inserted into the DD5 preflight, makes no claim that an encounter is
 * ready and suppresses no legacy component.
 *
 * Failures are named: the message starts with one of these tokens.
 *   InvalidComponent, WrongComponentClass, ComponentBegunPlay, ComponentAlreadyRegistered, InvalidOwner, OwnerBegunPlay,
 *   InvalidStagger.NotFinite, InvalidStagger.Negative, InvalidStagger.NotPositive, InvalidStagger.AngleOutOfRange, UnsupportedNativeCritical
 */
namespace RPGBossStaggerPolicyAdapters
{
	/** The native critical hit subtracts Loss * (multiplier - 1) from health; below this value it would add health. */
	constexpr float NativeCriticalMultiplierFloor = 1.f;

	/** The manifest paths of the fourteen typed inputs, "StaggerPolicy.<native field name>" (metadata membership only, not provenance and not proof of a value). */
	inline constexpr const TCHAR* FieldStaggerSeconds = TEXT("StaggerPolicy.StaggerSeconds");
	inline constexpr const TCHAR* FieldFreezeAtPosition = TEXT("StaggerPolicy.FreezeAtPosition");
	inline constexpr const TCHAR* FieldCriticalMultiplier = TEXT("StaggerPolicy.CriticalMultiplier");
	inline constexpr const TCHAR* FieldRiposteRange = TEXT("StaggerPolicy.RiposteRange");
	inline constexpr const TCHAR* FieldRiposteConeDegrees = TEXT("StaggerPolicy.RiposteConeDegrees");
	inline constexpr const TCHAR* FieldRiposteFacingDegrees = TEXT("StaggerPolicy.RiposteFacingDegrees");
	inline constexpr const TCHAR* FieldRiposteArmSeconds = TEXT("StaggerPolicy.RiposteArmSeconds");
	inline constexpr const TCHAR* FieldRipostePlayerStartGap = TEXT("StaggerPolicy.RipostePlayerStartGap");
	inline constexpr const TCHAR* FieldRiposteAlignSeconds = TEXT("StaggerPolicy.RiposteAlignSeconds");
	inline constexpr const TCHAR* FieldRiposteImpactSeconds = TEXT("StaggerPolicy.RiposteImpactSeconds");
	inline constexpr const TCHAR* FieldRiposteBaseDamage = TEXT("StaggerPolicy.RiposteBaseDamage");
	inline constexpr const TCHAR* FieldCooldownSeconds = TEXT("StaggerPolicy.CooldownSeconds");
	inline constexpr const TCHAR* FieldGetUpRate = TEXT("StaggerPolicy.GetUpRate");
	inline constexpr const TCHAR* FieldHoldPostureAtZero = TEXT("StaggerPolicy.bHoldPostureAtZero");

	/** Checks the typed policy without touching any component; OutError is cleared first and carries a named failure on false. */
	ONEBOSSFIGHT_API bool ValidateStaggerPolicy(const FRPGStaggerPolicyConfig& Policy, FString& OutError);

	/** Assigns the fourteen fields of Config.StaggerPolicy to a URPGBossStagger (exact class). Writes nothing unless every check passed. */
	ONEBOSSFIGHT_API bool ConfigureStaggerPolicy(UActorComponent& Component, const FRPGParticipantConfig& Config, FString& OutError);

	/** Unwired plan fragment: class URPGBossStagger, the legacy instance name "RPGBossStagger", the fourteen typed field paths as required fields (in field order). */
	ONEBOSSFIGHT_API FRPGComponentPlan MakeStaggerPolicyPlan();
}
