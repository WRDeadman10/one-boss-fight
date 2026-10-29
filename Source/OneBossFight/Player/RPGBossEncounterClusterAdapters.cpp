// Copyright One Boss Fight. All Rights Reserved.

#include "Player/RPGBossEncounterClusterAdapters.h"
#include "Components/ActorComponent.h"
#include "GameFramework/Actor.h"
#include "Player/RPGBossEncounter.h"
#include "Player/RPGBossEncounterPolicyAdapters.h"
#include "Player/RPGBossStatsAdapters.h"

namespace RPGBossEncounterClusterAdapters
{
	namespace
	{
		/** The same lifecycle boundary as the accepted typed adapters (restated here because those files must not change): a live component of exactly the expected class, unregistered and not begun, under a live
		 *  owner that has not begun play. Writes nothing. */
		bool CheckConfigurable(const UActorComponent& Component, const UClass* Expected, FString& OutError)
		{
			// First, before any other state is trusted: DestroyComponent flags the component as being destroyed, ends its play, unregisters it, removes it from its owner and marks it garbage, yet the object
			// stays allocated until a garbage collection runs and its owner can stay valid. Such a dead component passes every later check. Only public state of a live reference is read.
			if (!IsValid(&Component) || Component.IsBeingDestroyed())
			{
				OutError = FString::Printf(TEXT("InvalidComponent: %s is destroyed or being destroyed"), *Component.GetName());
				return false;
			}
			if (Component.GetClass() != Expected)
			{
				OutError = FString::Printf(TEXT("WrongComponentClass: expected %s, got %s"), *Expected->GetName(), *Component.GetClass()->GetName());
				return false;
			}
			if (Component.HasBegunPlay())
			{
				OutError = FString::Printf(TEXT("ComponentBegunPlay: %s already began play, its configuration was already read"), *Component.GetName());
				return false;
			}
			if (Component.IsRegistered())
			{
				OutError = FString::Printf(TEXT("ComponentAlreadyRegistered: %s is registered, configuration must be assigned before registration"), *Component.GetName());
				return false;
			}
			const AActor* Owner = Component.GetOwner();
			if (!Owner || !IsValid(Owner) || Owner->IsActorBeingDestroyed())
			{
				OutError = FString::Printf(TEXT("InvalidOwner: %s has no valid owner actor"), *Component.GetName());
				return false;
			}
			if (Owner->HasActorBegunPlay() || Owner->IsActorBeginningPlay())
			{
				OutError = FString::Printf(TEXT("OwnerBegunPlay: owner %s already began play"), *Owner->GetName());
				return false;
			}
			return true;
		}
	}

	bool ValidateEncounterCluster(const FRPGParticipantConfig& Config, FString& OutError)
	{
		OutError.Reset();
		// The complete four-stat record first (the native health override capability, the posture and regeneration rules), then the policy; each reports its exact existing token and path.
		return RPGBossStatsAdapters::ValidateStats(Config.Stats, OutError)
			&& RPGBossEncounterPolicyAdapters::ValidateEncounterPolicy(Config.EncounterPolicy, OutError);
	}

	bool ConfigureEncounterCluster(UActorComponent& Component, const FRPGParticipantConfig& Config, FString& OutError)
	{
		OutError.Reset();
		// Every check, lifecycle first, then the whole cluster, happens before the one write block: no older mutating callback is run, so no partial write can happen.
		if (!CheckConfigurable(Component, URPGBossEncounter::StaticClass(), OutError) || !ValidateEncounterCluster(Config, OutError))
		{
			return false;
		}
		URPGBossEncounter* Encounter = CastChecked<URPGBossEncounter>(&Component);
		Encounter->BossMaxHealth = Config.Stats.MaxHealth;
		Encounter->GateRadius = Config.EncounterPolicy.GateRadius;
		Encounter->bResetOnPlayerRespawn = Config.EncounterPolicy.bResetOnPlayerRespawn;
		return true;
	}

	FRPGComponentPlan MakeEncounterClusterPlan()
	{
		FRPGComponentPlan Plan;
		Plan.Class = URPGBossEncounter::StaticClass();
		Plan.InstanceName = TEXT("RPGBossEncounter");
		Plan.RequiredFields = {RPGBossStatsAdapters::FieldMaxHealth, RPGBossEncounterPolicyAdapters::FieldGateRadius, RPGBossEncounterPolicyAdapters::FieldResetOnPlayerRespawn};
		Plan.Configure = &ConfigureEncounterCluster;
		return Plan;
	}
}
