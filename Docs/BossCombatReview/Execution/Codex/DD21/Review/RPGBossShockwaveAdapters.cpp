// Copyright One Boss Fight. All Rights Reserved.
#include "Player/RPGBossShockwaveAdapters.h"
#include "Components/ActorComponent.h"
#include "GameFramework/Actor.h"
#include "Player/RPGBossShockwave.h"

namespace RPGBossShockwaveAdapters
{
	namespace
	{
		bool CheckConfigurable(const UActorComponent& Component, FString& Error)
		{
			if (!IsValid(&Component) || Component.IsBeingDestroyed())
			{
				Error = TEXT("InvalidComponent: Shockwave target is destroyed or being destroyed");
				return false;
			}
			if (Component.GetClass() != URPGBossShockwave::StaticClass())
			{
				Error = TEXT("WrongComponentClass: expected exact URPGBossShockwave");
				return false;
			}
			if (Component.HasBegunPlay())
			{
				Error = TEXT("ComponentBegunPlay: Shockwave target already began play");
				return false;
			}
			if (Component.IsRegistered())
			{
				Error = TEXT("ComponentAlreadyRegistered: Shockwave must be configured before registration");
				return false;
			}
			const AActor* Owner = Component.GetOwner();
			if (!Owner || !IsValid(Owner) || Owner->IsActorBeingDestroyed())
			{
				Error = TEXT("InvalidOwner: Shockwave has no live owner");
				return false;
			}
			if (Owner->HasActorBegunPlay() || Owner->IsActorBeginningPlay())
			{
				Error = TEXT("OwnerBegunPlay: Shockwave owner already began or is beginning play");
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


	bool ValidateShockwave(const FRPGShockwaveConfig& Record, FString& OutError)
	{
		OutError.Reset();
		struct FScalar { const TCHAR* Field; float Value; };
		const FScalar Scalars[] = {{FieldDamage,Record.Damage},{FieldStartRadius,Record.StartRadius},
			{FieldMaxRadius,Record.MaxRadius},{FieldSpeed,Record.Speed},{FieldThickness,Record.Thickness},{FieldJumpClearance,Record.JumpClearance}};
		for (const FScalar& S : Scalars)
		{
			if (!FMath::IsFinite(S.Value)) { return Refuse(OutError,TEXT("InvalidShockwave.NotFinite"),S.Field); }
		}
		if (Record.Damage<0.f) { return Refuse(OutError,TEXT("InvalidShockwave.Negative"),FieldDamage); }
		if (Record.StartRadius<0.f) { return Refuse(OutError,TEXT("InvalidShockwave.Negative"),FieldStartRadius); }
		if (Record.StartRadius>MaxAuthoredMagnitude) { return Refuse(OutError,TEXT("InvalidShockwave.AboveCeiling"),FieldStartRadius); }
		if (Record.MaxRadius<=0.f) { return Refuse(OutError,TEXT("InvalidShockwave.NotPositive"),FieldMaxRadius); }
		if (Record.MaxRadius>MaxAuthoredMagnitude) { return Refuse(OutError,TEXT("InvalidShockwave.AboveCeiling"),FieldMaxRadius); }
		if (Record.MaxRadius<=Record.StartRadius) { return Refuse(OutError,TEXT("InvalidShockwave.MaxNotAboveStart"),FieldMaxRadius); }
		if (Record.Speed<=0.f) { return Refuse(OutError,TEXT("InvalidShockwave.NotPositive"),FieldSpeed); }
		if (Record.Speed>MaxAuthoredMagnitude) { return Refuse(OutError,TEXT("InvalidShockwave.AboveCeiling"),FieldSpeed); }
		if (Record.Thickness<=0.f) { return Refuse(OutError,TEXT("InvalidShockwave.NotPositive"),FieldThickness); }
		if (Record.Thickness>MaxAuthoredMagnitude) { return Refuse(OutError,TEXT("InvalidShockwave.AboveCeiling"),FieldThickness); }
		if (Record.JumpClearance<=0.f) { return Refuse(OutError,TEXT("InvalidShockwave.NotPositive"),FieldJumpClearance); }
		if (Record.JumpClearance>MaxAuthoredMagnitude) { return Refuse(OutError,TEXT("InvalidShockwave.AboveCeiling"),FieldJumpClearance); }
		if (Record.MoveId.IsNone()) { return Refuse(OutError,TEXT("InvalidDependency.Missing"),FieldMoveId); }
		for (const TCHAR C : Record.MoveId.ToString())
		{
			if (FChar::IsWhitespace(C)||FChar::IsControl(C)) { return Refuse(OutError,TEXT("InvalidDependency.Malformed"),FieldMoveId); }
		}
		return true;
	}

	bool ConfigureShockwave(UActorComponent& Component, const FRPGParticipantConfig& Config, FString& OutError)
	{
		OutError.Reset();
		if (!CheckConfigurable(Component, OutError) || !ValidateShockwave(Config.Shockwave, OutError))
		{
			return false;
		}
		URPGBossShockwave* Sweep = CastChecked<URPGBossShockwave>(&Component);
		const FRPGShockwaveConfig& Record = Config.Shockwave;
		Sweep->bEnabled = Record.bEnabled;
		Sweep->MoveId = Record.MoveId;
		Sweep->Damage = Record.Damage;
		Sweep->StartRadius = Record.StartRadius;
		Sweep->MaxRadius = Record.MaxRadius;
		Sweep->Speed = Record.Speed;
		Sweep->Thickness = Record.Thickness;
		Sweep->JumpClearance = Record.JumpClearance;
		return true;
	}

	FRPGComponentPlan MakeShockwavePlan()
	{
		FRPGComponentPlan Plan;
		Plan.Class = URPGBossShockwave::StaticClass();
		Plan.InstanceName = TEXT("RPGBossShockwave");
		Plan.RequiredFields = {FieldEnabled, FieldMoveId, FieldDamage, FieldStartRadius, FieldMaxRadius,
			FieldSpeed, FieldThickness, FieldJumpClearance};
		Plan.Configure = &ConfigureShockwave;
		return Plan;
	}
}
