// Copyright One Boss Fight. All Rights Reserved.

#include "Player/RPGBossEncounterPolicyAdapters.h"
#include "Components/ActorComponent.h"
#include "GameFramework/Actor.h"
#include "Player/RPGBossEncounter.h"

namespace RPGBossEncounterPolicyAdapters
{
	namespace
	{
		/** The same lifecycle boundary as the accepted stats and phase adapters (restated here because those files must not change): a live component of exactly the expected class, unregistered and not begun,
		 *  under a live owner that has not begun play. Writes nothing. */
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

	bool ValidateEncounterPolicy(const FRPGEncounterPolicyConfig& Policy, FString& OutError)
	{
		OutError.Reset();
		// Finite first: a NaN compares false with everything and must never reach the sign test. Zero is valid (the native meaning is no gate); a negative -0.0 is zero.
		if (!FMath::IsFinite(Policy.GateRadius))
		{
			OutError = FString::Printf(TEXT("InvalidPolicy.NotFinite: %s=%s"), FieldGateRadius, *LexToString(Policy.GateRadius));
			return false;
		}
		if (Policy.GateRadius < 0.f)
		{
			OutError = FString::Printf(TEXT("InvalidPolicy.Negative: %s=%s, expected 0 (no gate) or more"), FieldGateRadius, *LexToString(Policy.GateRadius));
			return false;
		}
		return true;
	}

	bool ConfigureEncounterPolicy(UActorComponent& Component, const FRPGParticipantConfig& Config, FString& OutError)
	{
		OutError.Reset();
		// Every check, lifecycle first, then the whole policy, happens before the one write block.
		if (!CheckConfigurable(Component, URPGBossEncounter::StaticClass(), OutError) || !ValidateEncounterPolicy(Config.EncounterPolicy, OutError))
		{
			return false;
		}
		URPGBossEncounter* Encounter = CastChecked<URPGBossEncounter>(&Component);
		Encounter->GateRadius = Config.EncounterPolicy.GateRadius;
		Encounter->bResetOnPlayerRespawn = Config.EncounterPolicy.bResetOnPlayerRespawn;
		return true;
	}

	FRPGComponentPlan MakeEncounterPolicyPlan()
	{
		FRPGComponentPlan Plan;
		Plan.Class = URPGBossEncounter::StaticClass();
		Plan.InstanceName = TEXT("RPGBossEncounter");
		Plan.RequiredFields = {FieldGateRadius, FieldResetOnPlayerRespawn};
		Plan.Configure = &ConfigureEncounterPolicy;
		return Plan;
	}
}
