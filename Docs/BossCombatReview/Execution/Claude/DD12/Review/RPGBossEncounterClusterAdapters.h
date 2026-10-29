// Copyright One Boss Fight. All Rights Reserved.

#pragma once

#include "CoreMinimal.h"
#include "Player/RPGEncounterBinding.h"

/**
 * Typed native adapter for the whole encounter authoring cluster (DD12 package 01). The accepted stats and encounter policy adapters each describe a plan for the SAME native class and the SAME legacy
 * instance (URPGBossEncounter, "RPGBossEncounter"): inserting both would create the encounter twice (two plans for one class are refused by the preflight, and two sequential partial writes would not be atomic).
 * This combined fragment is the ONE encounter plan: one call validates and assigns, atomically, the three typed values the component has:
 *
 *   Stats.MaxHealth                        -> URPGBossEncounter::BossMaxHealth
 *   EncounterPolicy.GateRadius             -> URPGBossEncounter::GateRadius
 *   EncounterPolicy.bResetOnPlayerRespawn  -> URPGBossEncounter::bResetOnPlayerRespawn
 *
 * Three fields, one write block, only after the lifecycle check and the WHOLE cluster passed. It reuses the accepted validators without any change of domain: RPGBossStatsAdapters::ValidateStats on the
 * COMPLETE four-stat record (so the native health override capability, health above 1, and the posture positivity and regeneration rules still apply; the three posture writes stay with the posture plan) and
 * RPGBossEncounterPolicyAdapters::ValidateEncounterPolicy (the gate radius finite and not negative, zero meaning no gate). Order: the stats record first, then the policy, each with its exact existing token and path.
 * A mutating callback of the older adapters is never run before the whole cluster has been validated.
 *
 * It creates no object, registers nothing, begins nothing, ticks nothing, loads nothing, parses no manifest Value text, uses no reflection or ImportText, looks up no actor or target, writes and reads no pack
 * attribute, starts no timer, reset or dormancy and executes no health override. Every other native field and all runtime state (test freeze flag, dormancy, waking, generation, counters) stay as they were.
 * This is authoring assignment only: NOT an effective gate, reset or pack health proof, and NOT gameplay readiness. The plan is an UNWIRED fragment: it is not added to the DD5 preflight and the older stats and
 * policy encounter factories stay what they are (nothing here changes them).
 *
 * Failures are named: the message starts with one of these tokens.
 *   InvalidComponent, WrongComponentClass, ComponentBegunPlay, ComponentAlreadyRegistered, InvalidOwner, OwnerBegunPlay,
 *   InvalidStats.* / UnsupportedNativeHealthOverride (see RPGBossStatsAdapters.h), InvalidPolicy.* (see RPGBossEncounterPolicyAdapters.h)
 */
namespace RPGBossEncounterClusterAdapters
{
	/** Checks the stats record and then the encounter policy without touching any component; OutError is cleared first and carries the exact existing named failure on false. */
	ONEBOSSFIGHT_API bool ValidateEncounterCluster(const FRPGParticipantConfig& Config, FString& OutError);

	/** Assigns the three typed values to a URPGBossEncounter (exact class). Writes nothing unless every check passed. */
	ONEBOSSFIGHT_API bool ConfigureEncounterCluster(UActorComponent& Component, const FRPGParticipantConfig& Config, FString& OutError);

	/** Unwired plan fragment: class URPGBossEncounter, the legacy instance name "RPGBossEncounter", the three typed field paths as required fields (Stats.MaxHealth, EncounterPolicy.GateRadius, EncounterPolicy.bResetOnPlayerRespawn). */
	ONEBOSSFIGHT_API FRPGComponentPlan MakeEncounterClusterPlan();
}
