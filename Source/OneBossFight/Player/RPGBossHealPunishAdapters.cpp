// Copyright One Boss Fight. All Rights Reserved.
#include "Player/RPGBossHealPunishAdapters.h"
#include "Components/ActorComponent.h"
#include "GameFramework/Actor.h"
#include "Player/RPGBossHealPunish.h"

namespace RPGBossHealPunishAdapters
{
	namespace
	{
		bool CheckConfigurable(const UActorComponent& Component, FString& Error)
		{
			if (!IsValid(&Component) || Component.IsBeingDestroyed())
			{
				Error = TEXT("InvalidComponent: HealPunish target is destroyed or being destroyed");
				return false;
			}
			if (Component.GetClass() != URPGBossHealPunish::StaticClass())
			{
				Error = TEXT("WrongComponentClass: expected exact URPGBossHealPunish");
				return false;
			}
			if (Component.HasBegunPlay())
			{
				Error = TEXT("ComponentBegunPlay: HealPunish target already began play");
				return false;
			}
			if (Component.IsRegistered())
			{
				Error = TEXT("ComponentAlreadyRegistered: HealPunish must be configured before registration");
				return false;
			}
			const AActor* Owner = Component.GetOwner();
			if (!Owner || !IsValid(Owner) || Owner->IsActorBeingDestroyed())
			{
				Error = TEXT("InvalidOwner: HealPunish has no live owner");
				return false;
			}
			if (Owner->HasActorBegunPlay() || Owner->IsActorBeginningPlay())
			{
				Error = TEXT("OwnerBegunPlay: HealPunish owner already began or is beginning play");
				return false;
			}
			return true;
		}

		bool Refuse(FString& Error, const TCHAR* Token, const TCHAR* Field)
		{
			Error = FString::Printf(TEXT("%s: %s"), Token, Field);
			return false;
		}
	}


	bool ValidateHealPunish(const FRPGHealPunishConfig& Record, FString& OutError)
	{
		OutError.Reset();
		struct FScalar
		{
			const TCHAR* Field;
			float Value;
		};
		const FScalar Scalars[] = {{FieldMinRange, Record.MinRange}, {FieldMaxRange, Record.MaxRange}, {FieldCooldown, Record.Cooldown}, {FieldDamage, Record.Damage}, {FieldFlightTime, Record.FlightTime}, {FieldMinSpeed, Record.MinSpeed}, {FieldMaxSpeed, Record.MaxSpeed}, {FieldJavelinRadius, Record.JavelinRadius}, {FieldJavelinMaxRange, Record.JavelinMaxRange}, {FieldAimHeight, Record.AimHeight}};
		for (const FScalar& S : Scalars)
		{
			if (!FMath::IsFinite(S.Value))
			{
				return Refuse(OutError, TEXT("InvalidPunish.NotFinite"), S.Field);
			}
		}
		if (Record.MinRange < 0.f)
		{
			return Refuse(OutError, TEXT("InvalidPunish.Negative"), FieldMinRange);
		}
		if (Record.MinRange > MaxAuthoredMagnitude)
		{
			return Refuse(OutError, TEXT("InvalidPunish.AboveCeiling"), FieldMinRange);
		}
		if (Record.MaxRange <= 0.f)
		{
			return Refuse(OutError, TEXT("InvalidPunish.NotPositive"), FieldMaxRange);
		}
		if (Record.MaxRange > MaxAuthoredMagnitude)
		{
			return Refuse(OutError, TEXT("InvalidPunish.AboveCeiling"), FieldMaxRange);
		}
		if (Record.MaxRange <= Record.MinRange)
		{
			return Refuse(OutError, TEXT("InvalidPunish.MaxNotAboveMin"), FieldMaxRange);
		}
		if (Record.Cooldown < 0.f)
		{
			return Refuse(OutError, TEXT("InvalidPunish.Negative"), FieldCooldown);
		}
		if (Record.Cooldown > MaxAuthoredMagnitude)
		{
			return Refuse(OutError, TEXT("InvalidPunish.AboveCeiling"), FieldCooldown);
		}
		if (Record.Damage < 0.f)
		{
			return Refuse(OutError, TEXT("InvalidPunish.Negative"), FieldDamage);
		}
		if (Record.FlightTime < MinAuthoredFlightTime)
		{
			return Refuse(OutError, TEXT("InvalidPunish.BelowFlightTimeFloor"), FieldFlightTime);
		}
		if (Record.FlightTime > MaxAuthoredMagnitude)
		{
			return Refuse(OutError, TEXT("InvalidPunish.AboveCeiling"), FieldFlightTime);
		}
		if (Record.MinSpeed <= 0.f)
		{
			return Refuse(OutError, TEXT("InvalidPunish.NotPositive"), FieldMinSpeed);
		}
		if (Record.MinSpeed > MaxAuthoredMagnitude)
		{
			return Refuse(OutError, TEXT("InvalidPunish.AboveCeiling"), FieldMinSpeed);
		}
		if (Record.MaxSpeed <= 0.f)
		{
			return Refuse(OutError, TEXT("InvalidPunish.NotPositive"), FieldMaxSpeed);
		}
		if (Record.MaxSpeed > MaxAuthoredMagnitude)
		{
			return Refuse(OutError, TEXT("InvalidPunish.AboveCeiling"), FieldMaxSpeed);
		}
		if (Record.MinSpeed > Record.MaxSpeed)
		{
			return Refuse(OutError, TEXT("InvalidPunish.MinSpeedAboveMax"), FieldMinSpeed);
		}
		if (Record.JavelinRadius <= 0.f)
		{
			return Refuse(OutError, TEXT("InvalidPunish.NotPositive"), FieldJavelinRadius);
		}
		if (Record.JavelinRadius > MaxAuthoredMagnitude)
		{
			return Refuse(OutError, TEXT("InvalidPunish.AboveCeiling"), FieldJavelinRadius);
		}
		if (Record.JavelinMaxRange <= 0.f)
		{
			return Refuse(OutError, TEXT("InvalidPunish.NotPositive"), FieldJavelinMaxRange);
		}
		if (Record.JavelinMaxRange > MaxAuthoredMagnitude)
		{
			return Refuse(OutError, TEXT("InvalidPunish.AboveCeiling"), FieldJavelinMaxRange);
		}
		if (Record.SpawnSockets.IsEmpty())
		{
			return Refuse(OutError, TEXT("InvalidDependency.Missing"), FieldSpawnSockets);
		}
		for (int32 Index = 0;Index < Record.SpawnSockets.Num();++Index)
		{
			const FName Name = Record.SpawnSockets[Index];
			bool bInvalid = Name.IsNone();
			for (const TCHAR C : Name.ToString())
			{
				bInvalid = bInvalid || FChar::IsWhitespace(C) || FChar::IsControl(C);
			}
			if (bInvalid)
			{
				OutError = FString::Printf(TEXT("InvalidDependency.Malformed: %s[%d]"), FieldSpawnSockets, Index);
				return false;
			}
		}
		if (Record.AimHeight < -MaxAuthoredMagnitude)
		{
			return Refuse(OutError, TEXT("InvalidPunish.BelowFloor"), FieldAimHeight);
		}
		if (Record.AimHeight > MaxAuthoredMagnitude)
		{
			return Refuse(OutError, TEXT("InvalidPunish.AboveCeiling"), FieldAimHeight);
		}
		return true;
	}

	bool ConfigureHealPunish(UActorComponent& Component, const FRPGParticipantConfig& Config, FString& OutError)
	{
		OutError.Reset();
		if (!CheckConfigurable(Component, OutError) || !ValidateHealPunish(Config.HealPunish, OutError))
		{
			return false;
		}
		URPGBossHealPunish* Punish = CastChecked<URPGBossHealPunish>(&Component);
		const FRPGHealPunishConfig& Record = Config.HealPunish;
		Punish->bEnabled = Record.bEnabled;
		Punish->MinRange = Record.MinRange;
		Punish->MaxRange = Record.MaxRange;
		Punish->Cooldown = Record.Cooldown;
		Punish->Damage = Record.Damage;
		Punish->FlightTime = Record.FlightTime;
		Punish->MinSpeed = Record.MinSpeed;
		Punish->MaxSpeed = Record.MaxSpeed;
		Punish->JavelinRadius = Record.JavelinRadius;
		Punish->JavelinMaxRange = Record.JavelinMaxRange;
		Punish->SpawnSockets = Record.SpawnSockets;
		Punish->AimHeight = Record.AimHeight;
		Punish->bRespondToHeal = Record.bRespondToHeal;
		Punish->bCancelJavelinsOnInterrupt = Record.bCancelJavelinsOnInterrupt;
		return true;
	}
	FRPGComponentPlan MakeHealPunishPlan()
	{
		FRPGComponentPlan Plan;
		Plan.Class = URPGBossHealPunish::StaticClass();
		Plan.InstanceName = TEXT("RPGBossHealPunish");
		Plan.RequiredFields = {FieldbEnabled, FieldMinRange, FieldMaxRange, FieldCooldown, FieldDamage, FieldFlightTime, FieldMinSpeed, FieldMaxSpeed, FieldJavelinRadius, FieldJavelinMaxRange, FieldSpawnSockets, FieldAimHeight, FieldbRespondToHeal, FieldbCancelJavelinsOnInterrupt};
		Plan.Configure = &ConfigureHealPunish;
		return Plan;
	}
}
