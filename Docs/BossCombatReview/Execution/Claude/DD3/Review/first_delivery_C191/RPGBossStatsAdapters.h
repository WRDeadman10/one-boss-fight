// Copyright One Boss Fight. All Rights Reserved.

#pragma once

#include "CoreMinimal.h"
#include "Player/RPGEncounterBinding.h"

/**
 * Typed native adapters for the four boss stats (DD3 package 01): FRPGBossStatsConfig -> the public configuration fields of the legacy components.
 *
 *   Stats.MaxHealth         -> URPGBossEncounter::BossMaxHealth
 *   Stats.MaxPosture        -> URPGBossPosture::PostureMax
 *   Stats.PostureRegenDelay -> URPGBossPosture::RegenDelaySeconds
 *   Stats.PostureRegenRate  -> URPGBossPosture::RegenPerSecond
 *
 * The values are read from the typed Stats record only, never from FRPGParityField::Value and never through ImportText. Every helper checks the component and the WHOLE selected Stats record
 * first and writes only afterwards, so a failure leaves every field as it was. The helpers never create, register or begin play on a component, never touch a pack attribute and never seed a
 * runtime value (current posture, generation, counters, cached health, hold state): the component reads its configuration when it begins play, as it always did.
 *
 * These two plans are NOT a complete playable boss bundle. Using them does not make an encounter ready and does not suppress the legacy components; Phases, Stagger and the other components
 * follow in later packages, and the order in which plans are run belongs to the future cluster planner, not to this subset.
 *
 * Failures are named: the message starts with one of the tokens below, so a caller or a test can tell the cases apart without parsing prose.
 *   WrongComponentClass, ComponentBegunPlay, ComponentAlreadyRegistered, InvalidOwner, OwnerBegunPlay,
 *   InvalidStats.NotFinite, InvalidStats.NotPositive, InvalidStats.Negative, UnsupportedNativeHealthOverride
 */
namespace RPGBossStatsAdapters
{
	/**
	 * The native health override of URPGBossEncounter only runs for BossMaxHealth above this value (URPGBossEncounter::TickComponent: "BossMaxHealth > 1.f"; 0 or less means the pack's own value).
	 * A requested health in (0, this] therefore could never be applied: it is refused by name instead of being claimed as applied. This is a capability check of the backend for an explicit override,
	 * not a gameplay limit, and the generic definition compiler's own domain (positive) is not changed by it.
	 */
	constexpr float NativeHealthOverrideFloor = 1.f;

	/** The manifest field paths each plan requires (the typed inputs; manifest membership only, not proof of a raw value or a source hash). */
	inline constexpr const TCHAR* FieldMaxHealth = TEXT("Stats.MaxHealth");
	inline constexpr const TCHAR* FieldMaxPosture = TEXT("Stats.MaxPosture");
	inline constexpr const TCHAR* FieldPostureRegenDelay = TEXT("Stats.PostureRegenDelay");
	inline constexpr const TCHAR* FieldPostureRegenRate = TEXT("Stats.PostureRegenRate");

	/** Checks the complete Stats record (all four fields, in this order) without touching any component. Returns false and a named message for the first failure. */
	ONEBOSSFIGHT_API bool ValidateStats(const FRPGBossStatsConfig& Stats, FString& OutError);

	/** Assigns Stats.MaxHealth to the BossMaxHealth of a URPGBossEncounter (exact class). Writes nothing unless every check passed. */
	ONEBOSSFIGHT_API bool ConfigureEncounter(UActorComponent& Component, const FRPGParticipantConfig& Config, FString& OutError);

	/** Assigns the three posture stats to a URPGBossPosture (exact class). Writes nothing unless every check passed. */
	ONEBOSSFIGHT_API bool ConfigurePosture(UActorComponent& Component, const FRPGParticipantConfig& Config, FString& OutError);

	/** Plan for the existing FRPGComponentPlan mechanism: class URPGBossEncounter, instance name "RPGBossEncounter" (the legacy name), required field Stats.MaxHealth. */
	ONEBOSSFIGHT_API FRPGComponentPlan MakeEncounterPlan();

	/** Plan for the existing FRPGComponentPlan mechanism: class URPGBossPosture, instance name "RPGBossPosture" (the legacy name), required fields Stats.MaxPosture, Stats.PostureRegenDelay, Stats.PostureRegenRate. */
	ONEBOSSFIGHT_API FRPGComponentPlan MakePosturePlan();
}
