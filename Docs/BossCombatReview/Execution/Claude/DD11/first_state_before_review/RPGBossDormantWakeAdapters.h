// Copyright One Boss Fight. All Rights Reserved.

#pragma once

#include "CoreMinimal.h"
#include "Player/RPGEncounterBinding.h"

/**
 * Typed native adapter for the dormant and wake clip references (DD11 package 01): FRPGDormantWakeConfig -> exactly two private fields of URPGBossDormantWake, with the names of the native component:
 *
 *   DormantClip, WakeClip
 *
 * Both are TSoftObjectPtr<UAnimSequence> assigned as PATHS: nothing is loaded, resolved or queried (no asset registry), and nothing is played. The native fields are private; the only seam is the exported
 * function ConfigureDormantWake, which URPGBossDormantWake declares as a friend (a forward declaration and one friend line in RPGBossDormantWake.h, no field made public, no setter, no reflected assignment,
 * no native logic or default changed). The loaded clip objects, the montage handles, the stage, the waking flag, the start time, the counters, the tick state and the encounter are never touched.
 *
 * One validator, two users: ValidateDormantWake is called by the definition compiler (RPGCombatHydration::CompileParticipantImpl) and by ConfigureDormantWake, so a record that the compiler accepts is exactly
 * a record the assignment accepts. Both references are REQUIRED (the native component has no use without them), checked for path STRUCTURE only: a set top-level soft reference that starts with '/', has a
 * package folder and a <package>.<asset> leaf, carries no whitespace, control character or sub-object (':'), and (it is an animation) no class-path rule. DormantClip is checked first, then WakeClip.
 * THAT A PATH NAMES AN EXISTING OR COOKED ASSET, THAT IT IS AN ANIMATION SEQUENCE, THAT IT FITS THE SKELETON OR THE TIMING, ARE UNRESOLVED INTEGRATION CHECKS, not something a well-formed path proves. An
 * invalid record is refused and NEVER replaced by a default. There is no enable flag and nothing here controls the existing test console variable rpg.WakeClip.
 *
 * ConfigureDormantWake checks the component (exact class, live, not begun, not registered) and its owner (live, not begun, not beginning play) and the whole record first, and writes only afterwards: a
 * failure leaves both references as they were. It creates no object, registers nothing, begins nothing, ticks nothing, loads nothing, looks up no actor and mutates no tag or console variable. The plan is an
 * UNWIRED fragment with the legacy instance name; it is not added to the DD5 preflight, claims no readiness and suppresses no legacy component.
 *
 * Failures are named: the message starts with one of these tokens.
 *   InvalidComponent, WrongComponentClass, ComponentBegunPlay, ComponentAlreadyRegistered, InvalidOwner, OwnerBegunPlay,
 *   InvalidDependency.Missing, InvalidDependency.Malformed
 */
namespace RPGBossDormantWakeAdapters
{
	/** The manifest paths of the two typed inputs, "DormantWake.<native field name>" (metadata membership only, not provenance and not proof of a value). */
	inline constexpr const TCHAR* FieldDormantClip = TEXT("DormantWake.DormantClip");
	inline constexpr const TCHAR* FieldWakeClip = TEXT("DormantWake.WakeClip");

	/** Checks the typed record without touching any component; OutError is cleared first and carries a named failure on false. */
	ONEBOSSFIGHT_API bool ValidateDormantWake(const FRPGDormantWakeConfig& DormantWake, FString& OutError);

	/** Assigns the two references of Config.DormantWake to a URPGBossDormantWake (exact class). Writes nothing unless every check passed. */
	ONEBOSSFIGHT_API bool ConfigureDormantWake(UActorComponent& Component, const FRPGParticipantConfig& Config, FString& OutError);

	/** Unwired plan fragment: class URPGBossDormantWake, the legacy instance name "RPGBossDormantWake", the two typed field paths as required fields (in field order). */
	ONEBOSSFIGHT_API FRPGComponentPlan MakeDormantWakePlan();
}
