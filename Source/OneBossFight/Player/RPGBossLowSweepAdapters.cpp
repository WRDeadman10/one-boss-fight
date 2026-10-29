// Copyright One Boss Fight. All Rights Reserved.
#include "Player/RPGBossLowSweepAdapters.h"
#include "Components/ActorComponent.h"
#include "GameFramework/Actor.h"
#include "Player/RPGBossLowSweep.h"

namespace RPGBossLowSweepAdapters
{
	namespace
	{
		bool CheckConfigurable(const UActorComponent& Component, FString& Error)
		{
			if (!IsValid(&Component) || Component.IsBeingDestroyed())
			{
				Error = TEXT("InvalidComponent: LowSweep target is destroyed or being destroyed");
				return false;
			}
			if (Component.GetClass() != URPGBossLowSweep::StaticClass())
			{
				Error = TEXT("WrongComponentClass: expected exact URPGBossLowSweep");
				return false;
			}
			if (Component.HasBegunPlay())
			{
				Error = TEXT("ComponentBegunPlay: LowSweep target already began play");
				return false;
			}
			if (Component.IsRegistered())
			{
				Error = TEXT("ComponentAlreadyRegistered: LowSweep must be configured before registration");
				return false;
			}
			const AActor* Owner = Component.GetOwner();
			if (!Owner || !IsValid(Owner) || Owner->IsActorBeingDestroyed())
			{
				Error = TEXT("InvalidOwner: LowSweep has no live owner");
				return false;
			}
			if (Owner->HasActorBegunPlay() || Owner->IsActorBeginningPlay())
			{
				Error = TEXT("OwnerBegunPlay: LowSweep owner already began or is beginning play");
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

	bool ValidateLowSweep(const FRPGLowSweepConfig& Record, FString& OutError)
	{
		OutError.Reset();
		struct FScalar { const TCHAR* Field; float Value; };
		const FScalar Scalars[] = {
			{FieldDamage, Record.Damage}, {FieldReach, Record.Reach},
			{FieldInnerRadius, Record.InnerRadius}, {FieldBladeHeight, Record.BladeHeight},
			{FieldSweepFromDegrees, Record.SweepFromDegrees}, {FieldSweepToDegrees, Record.SweepToDegrees}
		};
		for (const FScalar& Scalar : Scalars)
		{
			if (!FMath::IsFinite(Scalar.Value))
			{
				return Refuse(OutError, TEXT("InvalidLowSweep.NotFinite"), Scalar.Field);
			}
		}
		if (Record.Damage < 0.f)
		{
			return Refuse(OutError, TEXT("InvalidLowSweep.Negative"), FieldDamage);
		}
		if (Record.Reach <= 0.f)
		{
			return Refuse(OutError, TEXT("InvalidLowSweep.NotPositive"), FieldReach);
		}
		if (Record.InnerRadius < 0.f)
		{
			return Refuse(OutError, TEXT("InvalidLowSweep.Negative"), FieldInnerRadius);
		}
		if (Record.InnerRadius >= Record.Reach)
		{
			return Refuse(OutError, TEXT("InvalidLowSweep.InnerNotBelowReach"), FieldInnerRadius);
		}
		if (Record.BladeHeight <= 0.f)
		{
			return Refuse(OutError, TEXT("InvalidLowSweep.NotPositive"), FieldBladeHeight);
		}
		if (Record.SweepFromDegrees < -360.f || Record.SweepFromDegrees > 360.f)
		{
			return Refuse(OutError, TEXT("InvalidLowSweep.AngleOutOfRange"), FieldSweepFromDegrees);
		}
		if (Record.SweepToDegrees < -360.f || Record.SweepToDegrees > 360.f)
		{
			return Refuse(OutError, TEXT("InvalidLowSweep.AngleOutOfRange"), FieldSweepToDegrees);
		}
		if (Record.MoveId.IsNone())
		{
			return Refuse(OutError, TEXT("InvalidDependency.Missing"), FieldMoveId);
		}
		for (const TCHAR C : Record.MoveId.ToString())
		{
			if (FChar::IsWhitespace(C) || FChar::IsControl(C))
			{
				return Refuse(OutError, TEXT("InvalidDependency.Malformed"), FieldMoveId);
			}
		}
		return true;
	}

	bool ConfigureLowSweep(UActorComponent& Component, const FRPGParticipantConfig& Config, FString& OutError)
	{
		OutError.Reset();
		if (!CheckConfigurable(Component, OutError) || !ValidateLowSweep(Config.LowSweep, OutError))
		{
			return false;
		}
		URPGBossLowSweep* Sweep = CastChecked<URPGBossLowSweep>(&Component);
		const FRPGLowSweepConfig& Record = Config.LowSweep;
		Sweep->bEnabled = Record.bEnabled;
		Sweep->MoveId = Record.MoveId;
		Sweep->Damage = Record.Damage;
		Sweep->Reach = Record.Reach;
		Sweep->InnerRadius = Record.InnerRadius;
		Sweep->BladeHeight = Record.BladeHeight;
		Sweep->SweepFromDegrees = Record.SweepFromDegrees;
		Sweep->SweepToDegrees = Record.SweepToDegrees;
		return true;
	}

	FRPGComponentPlan MakeLowSweepPlan()
	{
		FRPGComponentPlan Plan;
		Plan.Class = URPGBossLowSweep::StaticClass();
		Plan.InstanceName = TEXT("RPGBossLowSweep");
		Plan.RequiredFields = {FieldEnabled, FieldMoveId, FieldDamage, FieldReach, FieldInnerRadius,
			FieldBladeHeight, FieldSweepFromDegrees, FieldSweepToDegrees};
		Plan.Configure = &ConfigureLowSweep;
		return Plan;
	}
}
