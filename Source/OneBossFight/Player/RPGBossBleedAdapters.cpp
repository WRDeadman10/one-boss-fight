// Copyright One Boss Fight. All Rights Reserved.

#include "Player/RPGBossBleedAdapters.h"
#include "Components/ActorComponent.h"
#include "GameFramework/Actor.h"
#include "Misc/PackageName.h"
#include "Player/RPGBossBleed.h"
#include "UObject/SoftObjectPath.h"

namespace RPGBossBleedAdapters
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

		/** Structure of a soft path as text; no registry query and no load. Returns an empty string when well-formed, else the reason. (The same structural policy as the dormant wake and the phases and stagger
		 *  clusters, without a class-path rule: the Niagara system and the sound are plain assets.) */
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

		struct FScalar
		{
			const TCHAR* Path;
			float Value;
		};
	}

	bool ValidateBleed(const FRPGBleedConfig& Bleed, FString& OutError)
	{
		OutError.Reset();
		// The five scalars in field order.
		const FScalar Scalars[] = {
			{FieldInitialThreshold, Bleed.InitialThreshold},
			{FieldThresholdIncrease, Bleed.ThresholdIncrease},
			{FieldThresholdMax, Bleed.ThresholdMax},
			{FieldHpFraction, Bleed.HpFraction},
			{FieldEffectHeight, Bleed.EffectHeight},
		};
		// (1) Every scalar finite first: a NaN compares false with everything and must never reach a sign or range test.
		for (const FScalar& Scalar : Scalars)
		{
			if (!FMath::IsFinite(Scalar.Value))
			{
				OutError = FString::Printf(TEXT("InvalidBleed.NotFinite: %s=%s"), Scalar.Path, *LexToString(Scalar.Value));
				return false;
			}
		}
		// (2) The domains, in field order. Nothing is clamped. EffectHeight has no domain beyond being finite: it is signed.
		if (Bleed.InitialThreshold <= 0.f)
		{
			OutError = FString::Printf(TEXT("InvalidBleed.NotPositive: %s=%s, the first proc needs a buildup above zero"), FieldInitialThreshold, *LexToString(Bleed.InitialThreshold));
			return false;
		}
		if (Bleed.ThresholdIncrease < 0.f)
		{
			OutError = FString::Printf(TEXT("InvalidBleed.Negative: %s=%s, expected 0 or more"), FieldThresholdIncrease, *LexToString(Bleed.ThresholdIncrease));
			return false;
		}
		if (Bleed.ThresholdMax < Bleed.InitialThreshold)
		{
			OutError = FString::Printf(TEXT("InvalidBleed.ThresholdMaxBelowInitial: %s=%s is below %s=%s, the native proc would lower the threshold"),
				FieldThresholdMax, *LexToString(Bleed.ThresholdMax), FieldInitialThreshold, *LexToString(Bleed.InitialThreshold));
			return false;
		}
		if (Bleed.HpFraction < 0.f || Bleed.HpFraction > 1.f)
		{
			OutError = FString::Printf(TEXT("InvalidBleed.FractionOutOfRange: %s=%s, expected a fraction within 0 and 1"), FieldHpFraction, *LexToString(Bleed.HpFraction));
			return false;
		}
		// (3) The two references, the effect first. Structure only: no registry query and no load.
		return CheckRequiredReference(FieldProcEffect, Bleed.ProcEffect.ToSoftObjectPath(), OutError)
			&& CheckRequiredReference(FieldProcSound, Bleed.ProcSound.ToSoftObjectPath(), OutError);
	}

	bool ConfigureBleed(UActorComponent& Component, const FRPGParticipantConfig& Config, FString& OutError)
	{
		OutError.Reset();
		// Every check, lifecycle first, then the whole record, happens before the one write block.
		if (!CheckConfigurable(Component, URPGBossBleed::StaticClass(), OutError) || !ValidateBleed(Config.Bleed, OutError))
		{
			return false;
		}
		URPGBossBleed* Bleed = CastChecked<URPGBossBleed>(&Component);
		const FRPGBleedConfig& Record = Config.Bleed;
		// The seven public fields only; soft paths are assigned, nothing is loaded. No state, no loaded object, no threshold seed.
		Bleed->InitialThreshold = Record.InitialThreshold;
		Bleed->ThresholdIncrease = Record.ThresholdIncrease;
		Bleed->ThresholdMax = Record.ThresholdMax;
		Bleed->HpFraction = Record.HpFraction;
		Bleed->EffectHeight = Record.EffectHeight;
		Bleed->ProcEffect = Record.ProcEffect;
		Bleed->ProcSound = Record.ProcSound;
		return true;
	}

	FRPGComponentPlan MakeBleedPlan()
	{
		FRPGComponentPlan Plan;
		Plan.Class = URPGBossBleed::StaticClass();
		Plan.InstanceName = TEXT("RPGBossBleed");
		Plan.RequiredFields = {FieldInitialThreshold, FieldThresholdIncrease, FieldThresholdMax, FieldHpFraction, FieldEffectHeight, FieldProcEffect, FieldProcSound};
		Plan.Configure = &ConfigureBleed;
		return Plan;
	}
}
