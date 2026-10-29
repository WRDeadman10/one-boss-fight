// Copyright One Boss Fight. All Rights Reserved.
#include "Player/RPGBossLookAdapters.h"
#include "Components/ActorComponent.h"
#include "GameFramework/Actor.h"
#include "Misc/PackageName.h"
#include "Player/RPGBossLook.h"
#include "UObject/SoftObjectPath.h"

namespace RPGBossLookAdapters
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

	}

	bool ValidateLook(const FRPGLookConfig& Record, FString& OutError)
	{
		OutError.Reset();
		if (!CheckRequiredReference(FieldBody, Record.Body.ToSoftObjectPath(), OutError))
		{
			return false;
		}
		TSet<FSoftObjectPath> SeenPieces;
		for (int32 Index = 0; Index < Record.Pieces.Num(); ++Index)
		{
			const FString Field = FString::Printf(TEXT("%s[%d]"), FieldPieces, Index);
			const FSoftObjectPath Path = Record.Pieces[Index].ToSoftObjectPath();
			if (!CheckRequiredReference(*Field, Path, OutError))
			{
				return false;
			}
			if (SeenPieces.Contains(Path))
			{
				OutError = FString::Printf(TEXT("InvalidDependency.Duplicate: %s=%s"), *Field, *Path.ToString());
				return false;
			}
			SeenPieces.Add(Path);
		}
		if (!CheckRequiredReference(FieldSword, Record.Sword.ToSoftObjectPath(), OutError))
		{
			return false;
		}
		if (Record.SwordSocket.IsNone())
		{
			OutError = FString::Printf(TEXT("InvalidDependency.Missing: %s is required"), FieldSwordSocket);
			return false;
		}
		for (const TCHAR C : Record.SwordSocket.ToString())
		{
			if (FChar::IsWhitespace(C) || FChar::IsControl(C))
			{
				OutError = FString::Printf(TEXT("InvalidDependency.Malformed: %s contains whitespace or control"), FieldSwordSocket);
				return false;
			}
		}
		return true;
	}

	bool ConfigureLook(UActorComponent& Component, const FRPGParticipantConfig& Config, FString& OutError)
	{
		OutError.Reset();
		if (!CheckConfigurable(Component, URPGBossLook::StaticClass(), OutError) || !ValidateLook(Config.Look, OutError))
		{
			return false;
		}
		URPGBossLook* Look = CastChecked<URPGBossLook>(&Component);
		Look->bEnabled = Config.Look.bEnabled;
		Look->Body = Config.Look.Body;
		Look->Pieces = Config.Look.Pieces;
		Look->Sword = Config.Look.Sword;
		Look->SwordSocket = Config.Look.SwordSocket;
		return true;
	}

	FRPGComponentPlan MakeLookPlan()
	{
		FRPGComponentPlan Plan;
		Plan.Class = URPGBossLook::StaticClass();
		Plan.InstanceName = TEXT("RPGBossLook");
		Plan.RequiredFields = {FieldbEnabled, FieldBody, FieldPieces, FieldSword, FieldSwordSocket};
		Plan.Configure = &ConfigureLook;
		return Plan;
	}
}
