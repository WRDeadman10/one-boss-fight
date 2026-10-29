// Copyright One Boss Fight. All Rights Reserved.

#include "Player/RPGBossDormantWakeAdapters.h"
#include "Components/ActorComponent.h"
#include "GameFramework/Actor.h"
#include "Player/RPGBossDormantWake.h"
#include "UObject/SoftObjectPath.h"

namespace RPGBossDormantWakeAdapters
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

		/** Structure of a soft path as text; no registry query and no load. Returns an empty string when well-formed, else the reason. (The same structural policy as the phases and stagger clusters, without
		 *  the class-path rule: these are animation sequences.) */
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
	}

	bool ValidateDormantWake(const FRPGDormantWakeConfig& DormantWake, FString& OutError)
	{
		OutError.Reset();
		// Field order: the dormant clip first, then the wake clip; the first failure wins.
		return CheckRequiredReference(FieldDormantClip, DormantWake.DormantClip.ToSoftObjectPath(), OutError)
			&& CheckRequiredReference(FieldWakeClip, DormantWake.WakeClip.ToSoftObjectPath(), OutError);
	}

	bool ConfigureDormantWake(UActorComponent& Component, const FRPGParticipantConfig& Config, FString& OutError)
	{
		OutError.Reset();
		// Every check, lifecycle first, then the whole record, happens before the one write block.
		if (!CheckConfigurable(Component, URPGBossDormantWake::StaticClass(), OutError) || !ValidateDormantWake(Config.DormantWake, OutError))
		{
			return false;
		}
		URPGBossDormantWake* DormantWake = CastChecked<URPGBossDormantWake>(&Component);
		// The two private fields, through the friend declaration of this function; soft paths only, nothing is loaded.
		DormantWake->DormantClip = Config.DormantWake.DormantClip;
		DormantWake->WakeClip = Config.DormantWake.WakeClip;
		return true;
	}

	FRPGComponentPlan MakeDormantWakePlan()
	{
		FRPGComponentPlan Plan;
		Plan.Class = URPGBossDormantWake::StaticClass();
		Plan.InstanceName = TEXT("RPGBossDormantWake");
		Plan.RequiredFields = {FieldDormantClip, FieldWakeClip};
		Plan.Configure = &ConfigureDormantWake;
		return Plan;
	}
}
