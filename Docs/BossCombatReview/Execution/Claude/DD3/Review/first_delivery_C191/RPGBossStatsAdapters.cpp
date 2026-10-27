// Copyright One Boss Fight. All Rights Reserved.

#include "Player/RPGBossStatsAdapters.h"
#include "Components/ActorComponent.h"
#include "GameFramework/Actor.h"
#include "Player/RPGBossEncounter.h"
#include "Player/RPGBossPosture.h"

namespace RPGBossStatsAdapters
{
	namespace
	{
		/** The component is exactly the expected class and still a plain, unregistered configuration target of an owner that has not begun play. Writes nothing. */
		bool CheckConfigurable(const UActorComponent& Component, const UClass* Expected, FString& OutError)
		{
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

		bool IsNotFinite(const TCHAR* Field, float Value, FString& OutError)
		{
			if (FMath::IsFinite(Value))
			{
				return false;
			}
			OutError = FString::Printf(TEXT("InvalidStats.NotFinite: %s=%s"), Field, *LexToString(Value));
			return true;
		}
	}

	bool ValidateStats(const FRPGBossStatsConfig& Stats, FString& OutError)
	{
		OutError.Reset();
		// Finite first for all four fields: a NaN compares false with everything and must never reach a sign test.
		if (IsNotFinite(FieldMaxHealth, Stats.MaxHealth, OutError) || IsNotFinite(FieldMaxPosture, Stats.MaxPosture, OutError)
			|| IsNotFinite(FieldPostureRegenDelay, Stats.PostureRegenDelay, OutError) || IsNotFinite(FieldPostureRegenRate, Stats.PostureRegenRate, OutError))
		{
			return false;
		}
		// Generic validity (the domain of the definition compiler, unchanged): health and posture maximum positive, regeneration delay and rate not negative.
		if (Stats.MaxHealth <= 0.f)
		{
			OutError = FString::Printf(TEXT("InvalidStats.NotPositive: %s=%s"), FieldMaxHealth, *LexToString(Stats.MaxHealth));
			return false;
		}
		if (Stats.MaxPosture <= 0.f)
		{
			OutError = FString::Printf(TEXT("InvalidStats.NotPositive: %s=%s"), FieldMaxPosture, *LexToString(Stats.MaxPosture));
			return false;
		}
		if (Stats.PostureRegenDelay < 0.f)
		{
			OutError = FString::Printf(TEXT("InvalidStats.Negative: %s=%s"), FieldPostureRegenDelay, *LexToString(Stats.PostureRegenDelay));
			return false;
		}
		if (Stats.PostureRegenRate < 0.f)
		{
			OutError = FString::Printf(TEXT("InvalidStats.Negative: %s=%s"), FieldPostureRegenRate, *LexToString(Stats.PostureRegenRate));
			return false;
		}
		// Native capability, separate from validity: the backend override never runs at or below the floor, so the request is refused rather than claimed as applied.
		if (Stats.MaxHealth <= NativeHealthOverrideFloor)
		{
			OutError = FString::Printf(TEXT("UnsupportedNativeHealthOverride: %s=%s, the native health override is applied only above %s"), FieldMaxHealth, *LexToString(Stats.MaxHealth), *LexToString(NativeHealthOverrideFloor));
			return false;
		}
		return true;
	}

	bool ConfigureEncounter(UActorComponent& Component, const FRPGParticipantConfig& Config, FString& OutError)
	{
		OutError.Reset();
		// Every check, including the stats of the posture component, happens before the one write.
		if (!CheckConfigurable(Component, URPGBossEncounter::StaticClass(), OutError) || !ValidateStats(Config.Stats, OutError))
		{
			return false;
		}
		CastChecked<URPGBossEncounter>(&Component)->BossMaxHealth = Config.Stats.MaxHealth;
		return true;
	}

	bool ConfigurePosture(UActorComponent& Component, const FRPGParticipantConfig& Config, FString& OutError)
	{
		OutError.Reset();
		// The whole Stats record is validated, health included, so that a bad value anywhere stops the first callback of a cluster before any component was written.
		if (!CheckConfigurable(Component, URPGBossPosture::StaticClass(), OutError) || !ValidateStats(Config.Stats, OutError))
		{
			return false;
		}
		URPGBossPosture* Posture = CastChecked<URPGBossPosture>(&Component);
		Posture->PostureMax = Config.Stats.MaxPosture;
		Posture->RegenDelaySeconds = Config.Stats.PostureRegenDelay;
		Posture->RegenPerSecond = Config.Stats.PostureRegenRate;
		return true;
	}

	FRPGComponentPlan MakeEncounterPlan()
	{
		FRPGComponentPlan Plan;
		Plan.Class = URPGBossEncounter::StaticClass();
		Plan.InstanceName = TEXT("RPGBossEncounter");
		Plan.RequiredFields = {FieldMaxHealth};
		Plan.Configure = &ConfigureEncounter;
		return Plan;
	}

	FRPGComponentPlan MakePosturePlan()
	{
		FRPGComponentPlan Plan;
		Plan.Class = URPGBossPosture::StaticClass();
		Plan.InstanceName = TEXT("RPGBossPosture");
		Plan.RequiredFields = {FieldMaxPosture, FieldPostureRegenDelay, FieldPostureRegenRate};
		Plan.Configure = &ConfigurePosture;
		return Plan;
	}
}
