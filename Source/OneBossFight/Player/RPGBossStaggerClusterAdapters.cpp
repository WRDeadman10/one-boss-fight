// Copyright One Boss Fight. All Rights Reserved.

#include "Player/RPGBossStaggerClusterAdapters.h"
#include "Components/ActorComponent.h"
#include "GameFramework/Actor.h"
#include "Player/RPGBossStagger.h"
#include "Player/RPGBossStaggerPolicyAdapters.h"
#include "UObject/SoftObjectPath.h"

namespace RPGBossStaggerClusterAdapters
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

		/** Structure of a soft path as text; no registry query and no load. Returns an empty string when well-formed, else the reason. */
		FString PathProblem(const FSoftObjectPath& Path, bool bClassPath)
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
			if (bClassPath && !Text.StartsWith(TEXT("/Script/"), ESearchCase::CaseSensitive))
			{
				// A class path is either a native class under /Script/ (module.class) or a generated Blueprint class ending in _C.
				const FString Asset = Leaf.Mid(Dot + 1);
				if (Asset.Len() <= 2 || !Asset.EndsWith(TEXT("_C"), ESearchCase::CaseSensitive))
				{
					return TEXT("a class path must name a generated class ending in _C or a native class under /Script/");
				}
			}
			return FString();
		}

		/** One reference: Required refuses a null path (Missing); a path that is set must be well-formed whether or not it is required. Returns false and fills OutError. */
		bool CheckReference(const TCHAR* Field, const FSoftObjectPath& Path, bool bRequired, bool bClassPath, FString& OutError)
		{
			if (Path.IsNull())
			{
				if (bRequired)
				{
					OutError = FString::Printf(TEXT("InvalidDependency.Missing: %s is required here and is not set"), Field);
					return false;
				}
				return true;
			}
			const FString Problem = PathProblem(Path, bClassPath);
			if (!Problem.IsEmpty())
			{
				OutError = FString::Printf(TEXT("%s: %s=%s, %s"), bClassPath && Problem.StartsWith(TEXT("a class path")) ? TEXT("InvalidDependency.NotClassPath") : TEXT("InvalidDependency.Malformed"), Field, *Path.ToString(), *Problem);
				return false;
			}
			return true;
		}
	}

	bool ValidateStaggerProfile(const FRPGStaggerProfileConfig& Profile, FString& OutError)
	{
		OutError.Reset();
		// (1) Hit stun ability class name: must not be None.
		if (Profile.HitStunAbilityClassName.IsNone())
		{
			OutError = FString::Printf(TEXT("InvalidStaggerProfile.NoHitStunClass: %s is None"), FieldHitStunAbilityClassName);
			return false;
		}
		// (2) References, in field order.
		// FallMontage and GetUpMontage required when !bUseClips (the montages are then the stagger).
		// FallClip and DownClip required when bUseClips.
		// RipostePlayerClip and RiposteBossClip required when bUseRiposteClips.
		// ImmunityEffect always required.
		return CheckReference(FieldFallMontage, Profile.FallMontage.ToSoftObjectPath(), /*bRequired=*/!Profile.bUseClips, /*bClassPath=*/false, OutError)
			&& CheckReference(FieldGetUpMontage, Profile.GetUpMontage.ToSoftObjectPath(), /*bRequired=*/!Profile.bUseClips, /*bClassPath=*/false, OutError)
			&& CheckReference(FieldFallClip, Profile.FallClip.ToSoftObjectPath(), /*bRequired=*/Profile.bUseClips, /*bClassPath=*/false, OutError)
			&& CheckReference(FieldDownClip, Profile.DownClip.ToSoftObjectPath(), /*bRequired=*/Profile.bUseClips, /*bClassPath=*/false, OutError)
			&& CheckReference(FieldRipostePlayerClip, Profile.RipostePlayerClip.ToSoftObjectPath(), /*bRequired=*/Profile.bUseRiposteClips, /*bClassPath=*/false, OutError)
			&& CheckReference(FieldRiposteBossClip, Profile.RiposteBossClip.ToSoftObjectPath(), /*bRequired=*/Profile.bUseRiposteClips, /*bClassPath=*/false, OutError)
			&& CheckReference(FieldImmunityEffect, Profile.ImmunityEffect.ToSoftObjectPath(), /*bRequired=*/true, /*bClassPath=*/true, OutError);
		// (3) bCriticalOnEveryHit: both true and false are structurally valid.
	}

	bool ValidateStaggerCluster(const FRPGParticipantConfig& Config, FString& OutError)
	{
		OutError.Reset();
		return RPGBossStaggerPolicyAdapters::ValidateStaggerPolicy(Config.StaggerPolicy, OutError)
			&& ValidateStaggerProfile(Config.StaggerProfile, OutError);
	}

	bool ConfigureStaggerCluster(UActorComponent& Component, const FRPGParticipantConfig& Config, FString& OutError)
	{
		OutError.Reset();
		if (!CheckConfigurable(Component, URPGBossStagger::StaticClass(), OutError) || !ValidateStaggerCluster(Config, OutError))
		{
			return false;
		}
		URPGBossStagger* Stagger = CastChecked<URPGBossStagger>(&Component);
		// The 14 stagger policy fields (exactly as ConfigureStaggerPolicy writes them).
		const FRPGStaggerPolicyConfig& Policy = Config.StaggerPolicy;
		Stagger->StaggerSeconds = Policy.StaggerSeconds;
		Stagger->FreezeAtPosition = Policy.FreezeAtPosition;
		Stagger->CriticalMultiplier = Policy.CriticalMultiplier;
		Stagger->RiposteRange = Policy.RiposteRange;
		Stagger->RiposteConeDegrees = Policy.RiposteConeDegrees;
		Stagger->RiposteFacingDegrees = Policy.RiposteFacingDegrees;
		Stagger->RiposteArmSeconds = Policy.RiposteArmSeconds;
		Stagger->RipostePlayerStartGap = Policy.RipostePlayerStartGap;
		Stagger->RiposteAlignSeconds = Policy.RiposteAlignSeconds;
		Stagger->RiposteImpactSeconds = Policy.RiposteImpactSeconds;
		Stagger->RiposteBaseDamage = Policy.RiposteBaseDamage;
		Stagger->CooldownSeconds = Policy.CooldownSeconds;
		Stagger->GetUpRate = Policy.GetUpRate;
		Stagger->bHoldPostureAtZero = Policy.bHoldPostureAtZero;
		// The 11 stagger profile fields.
		const FRPGStaggerProfileConfig& Profile = Config.StaggerProfile;
		Stagger->bUseClips = Profile.bUseClips;
		Stagger->bUseRiposteClips = Profile.bUseRiposteClips;
		Stagger->bCriticalOnEveryHit = Profile.bCriticalOnEveryHit;
		Stagger->HitStunAbilityClassName = Profile.HitStunAbilityClassName;
		Stagger->FallMontage = Profile.FallMontage;
		Stagger->GetUpMontage = Profile.GetUpMontage;
		Stagger->FallClip = Profile.FallClip;
		Stagger->DownClip = Profile.DownClip;
		Stagger->RipostePlayerClip = Profile.RipostePlayerClip;
		Stagger->RiposteBossClip = Profile.RiposteBossClip;
		Stagger->ImmunityEffect = Profile.ImmunityEffect;
		return true;
	}

	FRPGComponentPlan MakeStaggerClusterPlan()
	{
		FRPGComponentPlan Plan;
		Plan.Class = URPGBossStagger::StaticClass();
		Plan.InstanceName = TEXT("RPGBossStagger");
		Plan.RequiredFields = {
			RPGBossStaggerPolicyAdapters::FieldStaggerSeconds,
			RPGBossStaggerPolicyAdapters::FieldFreezeAtPosition,
			RPGBossStaggerPolicyAdapters::FieldCriticalMultiplier,
			RPGBossStaggerPolicyAdapters::FieldRiposteRange,
			RPGBossStaggerPolicyAdapters::FieldRiposteConeDegrees,
			RPGBossStaggerPolicyAdapters::FieldRiposteFacingDegrees,
			RPGBossStaggerPolicyAdapters::FieldRiposteArmSeconds,
			RPGBossStaggerPolicyAdapters::FieldRipostePlayerStartGap,
			RPGBossStaggerPolicyAdapters::FieldRiposteAlignSeconds,
			RPGBossStaggerPolicyAdapters::FieldRiposteImpactSeconds,
			RPGBossStaggerPolicyAdapters::FieldRiposteBaseDamage,
			RPGBossStaggerPolicyAdapters::FieldCooldownSeconds,
			RPGBossStaggerPolicyAdapters::FieldGetUpRate,
			RPGBossStaggerPolicyAdapters::FieldHoldPostureAtZero,
			FieldUseClips,
			FieldUseRiposteClips,
			FieldCriticalOnEveryHit,
			FieldHitStunAbilityClassName,
			FieldFallMontage,
			FieldGetUpMontage,
			FieldFallClip,
			FieldDownClip,
			FieldRipostePlayerClip,
			FieldRiposteBossClip,
			FieldImmunityEffect
		};
		Plan.Configure = [](UActorComponent& Component, const FRPGParticipantConfig& Config, FString& OutError)
		{
			return ConfigureStaggerCluster(Component, Config, OutError);
		};
		return Plan;
	}
}
