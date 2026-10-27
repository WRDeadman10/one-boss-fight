// Copyright One Boss Fight. All Rights Reserved.

#pragma once

#include "CoreMinimal.h"
#include "Player/RPGEncounterBinding.h"

/**
 * Typed native adapter for the encounter policy (DD6 package 01): FRPGEncounterPolicyConfig -> the two public policy fields of URPGBossEncounter.
 *
 *   EncounterPolicy.GateRadius            -> URPGBossEncounter::GateRadius            (cm, horizontal; 0 = no gate, the native meaning)
 *   EncounterPolicy.bResetOnPlayerRespawn -> URPGBossEncounter::bResetOnPlayerRespawn
 *
 * Only these two fields are assigned. BossMaxHealth belongs to the stats adapter and is never touched here, and neither are bTestFreeze, the tracked pawn, the home transform, the generation, the dormant,
 * held or waking state, the counters, any cached attribute or any clock. The values come from the typed policy record only, never from FRPGParityField::Value and never through ImportText.
 *
 * One validator, two users: ValidateEncounterPolicy is called by the definition compiler (RPGCombatHydration::CompileParticipantImpl) and by ConfigureEncounterPolicy, so a policy that the compiler accepts is
 * exactly a policy the assignment accepts. A policy is valid when GateRadius is finite and not negative. Fractional positive values are valid and no maximum or floor is imposed (the editor metadata of the
 * native property is not a runtime rule). An invalid value is refused by name and NEVER replaced by the authoring default.
 *
 * The authoring defaults of the new asset field (1200 cm, true) match the native declarations of URPGBossEncounter. They are defaults of FRPGEncounterPolicyConfig for newly authored or old schema 1
 * definitions that have no serialized value; they are not proof of a serialized or live actor value and not a fallback for invalid input.
 *
 * ConfigureEncounterPolicy checks the component and the whole policy first and writes only afterwards: a failure leaves every field as it was. It never creates, registers or begins play on a component,
 * runs no behavior and discovers no actor. The plan is an UNWIRED assignment fragment: it must not be put into a plan list together with the stats adapter's encounter plan (the existing hydration
 * mechanism refuses two plans for one component class). A future combined plan has to apply the stats and this policy to the one encounter component exactly once, with every validation done before any
 * write. This fragment makes no claim that an encounter is ready and suppresses no legacy component.
 *
 * Failures are named: the message starts with one of these tokens.
 *   InvalidComponent, WrongComponentClass, ComponentBegunPlay, ComponentAlreadyRegistered, InvalidOwner, OwnerBegunPlay, InvalidPolicy.NotFinite, InvalidPolicy.Negative
 */
namespace RPGBossEncounterPolicyAdapters
{
	/** The manifest paths of the two typed inputs (metadata membership only, not provenance and not proof of a value). */
	inline constexpr const TCHAR* FieldGateRadius = TEXT("EncounterPolicy.GateRadius");
	inline constexpr const TCHAR* FieldResetOnPlayerRespawn = TEXT("EncounterPolicy.bResetOnPlayerRespawn");

	/** Checks the typed policy without touching any component; OutError is cleared first and carries a named failure on false. */
	ONEBOSSFIGHT_API bool ValidateEncounterPolicy(const FRPGEncounterPolicyConfig& Policy, FString& OutError);

	/** Assigns Config.EncounterPolicy to a URPGBossEncounter (exact class). Writes nothing unless every check passed. */
	ONEBOSSFIGHT_API bool ConfigureEncounterPolicy(UActorComponent& Component, const FRPGParticipantConfig& Config, FString& OutError);

	/** Unwired plan fragment: class URPGBossEncounter, the legacy instance name "RPGBossEncounter", the two typed field paths as required fields. */
	ONEBOSSFIGHT_API FRPGComponentPlan MakeEncounterPolicyPlan();
}
