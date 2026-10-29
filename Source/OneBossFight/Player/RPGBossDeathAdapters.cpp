// Copyright One Boss Fight. All Rights Reserved.
#include "Player/RPGBossDeathAdapters.h"
#include "Components/ActorComponent.h"
#include "GameFramework/Actor.h"
#include "Misc/PackageName.h"
#include "Player/RPGBossDeath.h"
#include "UObject/SoftObjectPath.h"

namespace RPGBossDeathAdapters
{
	namespace
	{
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

		// PathProblem/CheckRequiredReference restated privately, byte-equivalent
		// policy from accepted RPGBossBleedAdapters.cpp. Frozen Bleed is unchanged.
		FString PathProblem(const FSoftObjectPath& Path)
		{
			const FString Text = Path.ToString();
			if (Text.IsEmpty() || Text[0] != TEXT('/'))
			{
				return TEXT("it must start with '/'");
			}
			for (const TCHAR C : Text)
			{
				if (FChar::IsWhitespace(C) || C < 32)
				{
					return TEXT("it contains whitespace or a control character");
				}
				if (C == TEXT(':'))
				{
					return TEXT("it names a sub-object");
				}
			}
			int32 LastSlash = INDEX_NONE;
			Text.FindLastChar(TEXT('/'), LastSlash);
			const FString Leaf = Text.Mid(LastSlash + 1);
			int32 Dot = INDEX_NONE;
			if (!Leaf.FindChar(TEXT('.'), Dot) || Dot <= 0 || Dot >= Leaf.Len() - 1)
			{
				return TEXT("it must end in <package>.<asset>");
			}
			if (LastSlash <= 0)
			{
				return TEXT("it has no package folder");
			}
			// Text-only engine checks deliberately do not require a mounted root or
			// query the asset registry. Synthetic paths remain legal; malformed
			// package segments or object names must not slip through as defaults.
			FText Reason;
			const FString Package = Text.Left(LastSlash + 1) + Leaf.Left(Dot);
			if (!FPackageName::IsValidTextForLongPackageName(Package, &Reason))
			{
				return Reason.ToString();
			}
			if (!FName::IsValidXName(Leaf.Mid(Dot + 1), INVALID_OBJECTNAME_CHARACTERS, &Reason))
			{
				return Reason.ToString();
			}
			return FString();
		}

		/** One required reference: null is Missing, a set path must be well-formed (Malformed). Returns false and fills OutError. */
		bool CheckRequiredReference(const TCHAR* Field, const FSoftObjectPath& Path, FString& OutError)
		{
			if (Path.IsNull())
			{
				OutError = FString::Printf(TEXT("InvalidDependency.Missing: %s is required and is not set"), Field);
				return false;
			}
			const FString Problem = PathProblem(Path);
			if (!Problem.IsEmpty())
			{
				OutError = FString::Printf(TEXT("InvalidDependency.Malformed: %s=%s, %s"), Field, *Path.ToString(), *Problem);
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

	bool ValidateDeath(const FRPGDeathConfig& Record, FString& OutError)
	{
		OutError.Reset();
		struct FScalar
		{
			const TCHAR* Field;
			float Value;
		};
		const FScalar Scalars[] = {
			{FieldPackPollSeconds, Record.PackPollSeconds},
			{FieldPackEndTimeMultiplier, Record.PackEndTimeMultiplier},
			{FieldHoldAtSeconds, Record.HoldAtSeconds},
			{FieldDyingSeconds, Record.DyingSeconds},
			{FieldBlendInSeconds, Record.BlendInSeconds},
		};
		for (const FScalar& Scalar : Scalars)
		{
			if (!FMath::IsFinite(Scalar.Value))
			{
				return Refuse(OutError, TEXT("InvalidDeath.NotFinite"), Scalar.Field);
			}
		}
		if (Record.DeathMode != ERPGBossDeathMode::PackMontage && Record.DeathMode != ERPGBossDeathMode::OwnClip)
		{
			return Refuse(OutError, TEXT("InvalidDeath.BadMode"), FieldDeathMode);
		}
		if (Record.PackPollSeconds <= 0.f)
		{
			return Refuse(OutError, TEXT("InvalidDeath.NotPositive"), FieldPackPollSeconds);
		}
		if (Record.PackPollSeconds > MaxAuthoredMagnitude)
		{
			return Refuse(OutError, TEXT("InvalidDeath.AboveCeiling"), FieldPackPollSeconds);
		}
		if (Record.PackEndTimeMultiplier < 0.f)
		{
			return Refuse(OutError, TEXT("InvalidDeath.Negative"), FieldPackEndTimeMultiplier);
		}
		if (Record.PackEndTimeMultiplier > MaxAuthoredMagnitude)
		{
			return Refuse(OutError, TEXT("InvalidDeath.AboveCeiling"), FieldPackEndTimeMultiplier);
		}
		if (Record.HoldAtSeconds <= 0.f)
		{
			return Refuse(OutError, TEXT("InvalidDeath.NotPositive"), FieldHoldAtSeconds);
		}
		if (Record.HoldAtSeconds > MaxAuthoredMagnitude)
		{
			return Refuse(OutError, TEXT("InvalidDeath.AboveCeiling"), FieldHoldAtSeconds);
		}
		if (Record.DyingSeconds <= 0.f)
		{
			return Refuse(OutError, TEXT("InvalidDeath.NotPositive"), FieldDyingSeconds);
		}
		if (Record.DyingSeconds > MaxAuthoredMagnitude)
		{
			return Refuse(OutError, TEXT("InvalidDeath.AboveCeiling"), FieldDyingSeconds);
		}
		if (Record.BlendInSeconds < 0.f)
		{
			return Refuse(OutError, TEXT("InvalidDeath.Negative"), FieldBlendInSeconds);
		}
		if (Record.BlendInSeconds > MaxAuthoredMagnitude)
		{
			return Refuse(OutError, TEXT("InvalidDeath.AboveCeiling"), FieldBlendInSeconds);
		}
		if (Record.MaxClipRestarts < 0)
		{
			return Refuse(OutError, TEXT("InvalidDeath.Negative"), FieldMaxClipRestarts);
		}
		if (Record.MaxClipRestarts > MaxAuthoredRestarts)
		{
			return Refuse(OutError, TEXT("InvalidDeath.AboveCeiling"), FieldMaxClipRestarts);
		}
		if (Record.PackDeathAbilityClassName.IsNone())
		{
			return Refuse(OutError, TEXT("InvalidDependency.Missing"), FieldPackDeathAbilityClassName);
		}
		for (const TCHAR C : Record.PackDeathAbilityClassName.ToString())
		{
			if (FChar::IsWhitespace(C) || FChar::IsControl(C))
			{
				return Refuse(OutError, TEXT("InvalidDependency.Malformed"), FieldPackDeathAbilityClassName);
			}
		}
		if (Record.PackDeathMontagesName.IsNone())
		{
			return Refuse(OutError, TEXT("InvalidDependency.Missing"), FieldPackDeathMontagesName);
		}
		for (const TCHAR C : Record.PackDeathMontagesName.ToString())
		{
			if (FChar::IsWhitespace(C) || FChar::IsControl(C))
			{
				return Refuse(OutError, TEXT("InvalidDependency.Malformed"), FieldPackDeathMontagesName);
			}
		}
		if (!CheckRequiredReference(FieldDeathClip, Record.DeathClip.ToSoftObjectPath(), OutError))
		{
			return false;
		}
		if (!CheckRequiredReference(FieldDeathMontage, Record.DeathMontage.ToSoftObjectPath(), OutError))
		{
			return false;
		}
		return true;
	}

	bool ConfigureDeath(UActorComponent& Component, const FRPGParticipantConfig& Config, FString& OutError)
	{
		OutError.Reset();
		if (!CheckConfigurable(Component, URPGBossDeath::StaticClass(), OutError) || !ValidateDeath(Config.Death, OutError))
		{
			return false;
		}
		URPGBossDeath* Death = CastChecked<URPGBossDeath>(&Component);
		Death->DeathMode = Config.Death.DeathMode;
		Death->DeathClip = Config.Death.DeathClip;
		Death->DeathMontage = Config.Death.DeathMontage;
		Death->PackDeathAbilityClassName = Config.Death.PackDeathAbilityClassName;
		Death->PackDeathMontagesName = Config.Death.PackDeathMontagesName;
		Death->PackPollSeconds = Config.Death.PackPollSeconds;
		Death->PackEndTimeMultiplier = Config.Death.PackEndTimeMultiplier;
		Death->HoldAtSeconds = Config.Death.HoldAtSeconds;
		Death->DyingSeconds = Config.Death.DyingSeconds;
		Death->BlendInSeconds = Config.Death.BlendInSeconds;
		Death->MaxClipRestarts = Config.Death.MaxClipRestarts;
		Death->bGuardPackDeath = Config.Death.bGuardPackDeath;
		return true;
	}

	FRPGComponentPlan MakeDeathPlan()
	{
		FRPGComponentPlan Plan;
		Plan.Class = URPGBossDeath::StaticClass();
		Plan.InstanceName = TEXT("RPGBossDeath");
		Plan.RequiredFields = {FieldDeathMode, FieldDeathClip, FieldDeathMontage, FieldPackDeathAbilityClassName, FieldPackDeathMontagesName, FieldPackPollSeconds, FieldPackEndTimeMultiplier, FieldHoldAtSeconds, FieldDyingSeconds, FieldBlendInSeconds, FieldMaxClipRestarts, FieldbGuardPackDeath};
		Plan.Configure = &ConfigureDeath;
		return Plan;
	}
}
