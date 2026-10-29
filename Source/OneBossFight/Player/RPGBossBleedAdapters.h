// Copyright One Boss Fight. All Rights Reserved.

#pragma once

#include "CoreMinimal.h"
#include "Player/RPGEncounterBinding.h"

/**
 * Typed native adapter for the bleed status policy (DD19 package 01): FRPGBleedConfig -> exactly seven public fields of URPGBossBleed, five floats and two soft object references, with the names of the native
 * component:
 *
 *   InitialThreshold, ThresholdIncrease, ThresholdMax, HpFraction, EffectHeight, ProcEffect, ProcSound
 *
 * Nothing else is assigned. The runtime state (the buildup, the threshold in force, the proc counter, the proc frame, the ignored counter, the last proc damage and the last result), the loaded effect, sound and
 * blood flipbook, the owner's health and posture and every other component are never touched: no threshold is seeded (the native BeginPlay and ResetBleed do that from InitialThreshold), no buildup is added,
 * no timer starts and no proc happens. Nothing is loaded, resolved or queried (no asset registry) by the validation or the assignment: the two references are assigned as PATHS.
 *
 * One validator, two users: ValidateBleed is called by the definition compiler (RPGCombatHydration::CompileParticipantImpl) and by ConfigureBleed, so at the record level a record that the compiler accepts is
 * exactly a record the assignment accepts (the assignment adds the lifecycle checks of the component and its owner). The contract is structural and authored, not a balance retune; an invalid value is refused by
 * name and never clamped, defaulted or repaired. The native ClampMin and ClampMax values are editor metadata and are NOT runtime minimums here. Checks run in this order: (1) EVERY scalar finite, in field order;
 * (2) the domains, in field order; (3) the two references, ProcEffect first.
 *   - InitialThreshold strictly positive (the first proc needs a buildup above zero);
 *   - ThresholdIncrease not negative (zero keeps a constant threshold);
 *   - ThresholdMax at least InitialThreshold (the native proc takes Min(Threshold + Increase, Max), so a maximum below the start would lower the threshold after the first proc); equal is valid;
 *   - HpFraction within [0, 1] (zero is a proc that takes no health, one the whole maximum; the native proc never takes the last point);
 *   - EffectHeight finite and SIGNED: no height floor is invented (a negative value places the burst below the origin);
 *   - ProcEffect and ProcSound REQUIRED: a set top-level soft reference that starts with '/', has a package folder and a <package>.<asset> leaf, carries no whitespace, control character or sub-object (':'),
 *     checked for path STRUCTURE only, including engine text-only package and object-name validation. Empty/repeated path segments, invalid package characters and object names with extra dots are refused.
 *     A mount need not be registered: this is a lexical check, not a mounted-root, asset-registry, existence or class check.
 * THAT A PATH NAMES AN EXISTING OR COOKED ASSET, THAT IT IS A NIAGARA SYSTEM OR A SOUND, THAT THE BURST IS VISIBLE OR AUDIBLE AND THAT THE NUMBERS FEEL RIGHT ARE UNRESOLVED INTEGRATION CHECKS, not something
 * a well-formed record proves. Assigning an unwired record approves no tuning and enables nothing.
 *
 * ConfigureBleed checks the component (exact class, live, not begun, not registered) and its owner (live, not begun, not beginning play) and the whole record first, and writes only afterwards: a failure leaves
 * every field as it was. It creates no object, registers nothing, begins nothing, ticks nothing, loads nothing and looks up no actor. The plan is an UNWIRED fragment with the legacy instance name; it is NOT
 * added to the DD5 preflight, the preparation or the reservation registry, claims no readiness, makes the participant no complete bundle and suppresses no legacy component.
 *
 * Failures are named: the message starts with one of these tokens.
 *   InvalidComponent, WrongComponentClass, ComponentBegunPlay, ComponentAlreadyRegistered, InvalidOwner, OwnerBegunPlay,
 *   InvalidBleed.NotFinite, InvalidBleed.NotPositive, InvalidBleed.Negative, InvalidBleed.ThresholdMaxBelowInitial, InvalidBleed.FractionOutOfRange,
 *   InvalidDependency.Missing, InvalidDependency.Malformed
 */
namespace RPGBossBleedAdapters
{
	/** The manifest paths of the seven typed inputs, "Bleed.<native field name>" (metadata membership only, not provenance and not proof of a value). */
	inline constexpr const TCHAR* FieldInitialThreshold = TEXT("Bleed.InitialThreshold");
	inline constexpr const TCHAR* FieldThresholdIncrease = TEXT("Bleed.ThresholdIncrease");
	inline constexpr const TCHAR* FieldThresholdMax = TEXT("Bleed.ThresholdMax");
	inline constexpr const TCHAR* FieldHpFraction = TEXT("Bleed.HpFraction");
	inline constexpr const TCHAR* FieldEffectHeight = TEXT("Bleed.EffectHeight");
	inline constexpr const TCHAR* FieldProcEffect = TEXT("Bleed.ProcEffect");
	inline constexpr const TCHAR* FieldProcSound = TEXT("Bleed.ProcSound");

	/** Checks the typed record without touching any component; OutError is cleared first and carries a named failure on false. */
	ONEBOSSFIGHT_API bool ValidateBleed(const FRPGBleedConfig& Bleed, FString& OutError);

	/** Assigns the seven fields of Config.Bleed to a URPGBossBleed (exact class). Writes nothing unless every check passed. */
	ONEBOSSFIGHT_API bool ConfigureBleed(UActorComponent& Component, const FRPGParticipantConfig& Config, FString& OutError);

	/** Unwired plan fragment: class URPGBossBleed, the legacy instance name "RPGBossBleed", the seven typed field paths as required fields (in record field order). */
	ONEBOSSFIGHT_API FRPGComponentPlan MakeBleedPlan();
}
