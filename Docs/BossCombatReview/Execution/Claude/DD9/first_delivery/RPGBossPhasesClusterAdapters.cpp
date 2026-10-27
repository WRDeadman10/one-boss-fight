// Copyright One Boss Fight. All Rights Reserved.

#include "Player/RPGBossPhasesClusterAdapters.h"
#include "Components/ActorComponent.h"
#include "GameFramework/Actor.h"
#include "Player/RPGBossPhaseAdapters.h"
#include "Player/RPGBossPhaseFlowAdapters.h"
#include "Player/RPGBossPhases.h"
#include "UObject/SoftObjectPath.h"

namespace RPGBossPhasesClusterAdapters
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
			if (bClassPath)
			{
				const FString Asset = Leaf.Mid(Dot + 1);
				if (Asset.Len() <= 2 || !Asset.EndsWith(TEXT("_C"), ESearchCase::CaseSensitive))
				{
					return TEXT("a class path must name a generated class ending in _C");
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

	bool ValidateFireball(const FRPGFireballConfig& Fireball, FString& OutError)
	{
		OutError.Reset();
		// (1) Finite first, in field order, so that a NaN never reaches a comparison.
		const struct { const TCHAR* Field; double Value; } Numbers[] = {
			{FieldFireballCooldown, Fireball.FireballCooldown.X}, {FieldFireballCooldown, Fireball.FireballCooldown.Y},
			{FieldFireballMinRange, Fireball.FireballMinRange}, {FieldFireballMaxRange, Fireball.FireballMaxRange}};
		for (const auto& Number : Numbers)
		{
			if (!FMath::IsFinite(Number.Value))
			{
				OutError = FString::Printf(TEXT("InvalidFireball.NotFinite: %s has the value %s"), Number.Field, *LexToString(Number.Value));
				return false;
			}
		}
		// (2) Not negative; zero is valid.
		for (const auto& Number : Numbers)
		{
			if (Number.Value < 0.0)
			{
				OutError = FString::Printf(TEXT("InvalidFireball.Negative: %s has the value %s, expected 0 or more"), Number.Field, *LexToString(Number.Value));
				return false;
			}
		}
		// (3) Order of the two windows. The native cooldown uses max(X, Y) as the upper bound, which hides an inverted pair; a range window with the minimum above the maximum can never fire.
		if (Fireball.FireballCooldown.X > Fireball.FireballCooldown.Y)
		{
			OutError = FString::Printf(TEXT("InvalidFireball.CooldownOrder: %s=(%s, %s), the minimum is above the maximum"), FieldFireballCooldown, *LexToString(Fireball.FireballCooldown.X), *LexToString(Fireball.FireballCooldown.Y));
			return false;
		}
		if (Fireball.FireballMinRange > Fireball.FireballMaxRange)
		{
			OutError = FString::Printf(TEXT("InvalidFireball.RangeOrder: %s=%s is above %s=%s"), FieldFireballMinRange, *LexToString(Fireball.FireballMinRange), FieldFireballMaxRange, *LexToString(Fireball.FireballMaxRange));
			return false;
		}
		// (4) The ability: required only when the fireball is enabled; a path that is set must be a well-formed class path either way.
		const FSoftObjectPath Ability = Fireball.FireballAbility.ToSoftObjectPath();
		if (Ability.IsNull())
		{
			if (Fireball.bFireballEnabled)
			{
				OutError = FString::Printf(TEXT("InvalidFireball.NoAbility: %s is not set while %s is true"), FieldFireballAbility, FieldFireballEnabled);
				return false;
			}
			return true;
		}
		const FString Problem = PathProblem(Ability, /*bClassPath=*/true);
		if (!Problem.IsEmpty())
		{
			OutError = FString::Printf(TEXT("InvalidFireball.AbilityPath: %s=%s, %s"), FieldFireballAbility, *Ability.ToString(), *Problem);
			return false;
		}
		return true;
	}

	bool ValidatePhaseDependencies(const FRPGPhaseDependencyConfig& Dependencies, bool bUseRoarClip, FString& OutError)
	{
		OutError.Reset();
		// Field order. The roar clip is required when it is the roar, the montage when it is the roar instead; the immunity effect always.
		return CheckReference(FieldRoarClip, Dependencies.RoarClip.ToSoftObjectPath(), /*bRequired=*/bUseRoarClip, /*bClassPath=*/false, OutError)
			&& CheckReference(FieldTransitionMontage, Dependencies.TransitionMontage.ToSoftObjectPath(), /*bRequired=*/!bUseRoarClip, /*bClassPath=*/false, OutError)
			&& CheckReference(FieldImmunityEffect, Dependencies.ImmunityEffect.ToSoftObjectPath(), /*bRequired=*/true, /*bClassPath=*/true, OutError);
	}

	bool ValidatePhasesCluster(const FRPGParticipantConfig& Config, FName SelectedPhaseId, FString& OutError)
	{
		OutError.Reset();
		return RPGBossPhaseAdapters::ValidatePhases(Config.Phases, SelectedPhaseId, OutError)
			&& RPGBossPhaseFlowAdapters::ValidatePhaseFlow(Config.PhaseFlow, OutError)
			&& ValidateFireball(Config.Fireball, OutError)
			&& ValidatePhaseDependencies(Config.PhaseDependencies, Config.PhaseFlow.bUseRoarClip, OutError);
	}

	bool ConfigurePhasesCluster(UActorComponent& Component, const FRPGParticipantConfig& Config, FName SelectedPhaseId, FString& OutError)
	{
		OutError.Reset();
		// Every check, lifecycle first, then the whole cluster, happens before the one write block.
		if (!CheckConfigurable(Component, URPGBossPhases::StaticClass(), OutError) || !ValidatePhasesCluster(Config, SelectedPhaseId, OutError))
		{
			return false;
		}
		// Validated just now: exactly one record with this id.
		const FRPGPhaseConfig* Selected = Config.Phases.FindByPredicate([SelectedPhaseId](const FRPGPhaseConfig& Phase) { return Phase.PhaseId == SelectedPhaseId; });
		if (!Selected)
		{
			OutError = FString::Printf(TEXT("InvalidPhase.NotFound: no phase '%s' after validation"), *SelectedPhaseId.ToString());
			return false;
		}
		URPGBossPhases* Phases = CastChecked<URPGBossPhases>(&Component);
		// The selected phase (the same four assignments as RPGBossPhaseAdapters::ConfigurePhases).
		Phases->PhaseTwoHealthFraction = Selected->EntryHealthFraction;
		Phases->MovementScale = Selected->SpeedMultiplier;
		Phases->AttackRateScale = Selected->RateMultiplier;
		Phases->DamageScale = Selected->AttackMultiplier;
		// The phase flow (the same six assignments as RPGBossPhaseFlowAdapters::ConfigurePhaseFlow), strings and names as authored.
		const FRPGPhaseFlowConfig& Flow = Config.PhaseFlow;
		Phases->TransitionSeconds = Flow.TransitionSeconds;
		Phases->bUseRoarClip = Flow.bUseRoarClip;
		Phases->bPausePostureInTransition = Flow.bPausePostureInTransition;
		Phases->bLockLeapUntilPhaseTwo = Flow.bLockLeapUntilPhaseTwo;
		Phases->AttackAbilityPrefix = Flow.AttackAbilityPrefix;
		Phases->LeapAbilityTag = Flow.LeapAbilityTag;
		// The fireball policy.
		const FRPGFireballConfig& Fireball = Config.Fireball;
		Phases->bFireballEnabled = Fireball.bFireballEnabled;
		Phases->FireballAbility = Fireball.FireballAbility; // a soft path, nothing is loaded
		Phases->FireballCooldown = Fireball.FireballCooldown;
		Phases->FireballMinRange = Fireball.FireballMinRange;
		Phases->FireballMaxRange = Fireball.FireballMaxRange;
		// The dependency references, as soft paths.
		Phases->RoarClip = Config.PhaseDependencies.RoarClip;
		Phases->TransitionMontage = Config.PhaseDependencies.TransitionMontage;
		Phases->ImmunityEffect = Config.PhaseDependencies.ImmunityEffect;
		return true;
	}

	FRPGComponentPlan MakePhasesClusterPlan(FName SelectedPhaseId)
	{
		FRPGComponentPlan Plan;
		Plan.Class = URPGBossPhases::StaticClass();
		Plan.InstanceName = TEXT("RPGBossPhases");
		if (!SelectedPhaseId.IsNone())
		{
			Plan.RequiredFields = {RPGBossPhaseAdapters::PhaseFieldPath(SelectedPhaseId, RPGBossPhaseAdapters::FieldEntryHealthFraction), RPGBossPhaseAdapters::PhaseFieldPath(SelectedPhaseId, RPGBossPhaseAdapters::FieldSpeedMultiplier),
				RPGBossPhaseAdapters::PhaseFieldPath(SelectedPhaseId, RPGBossPhaseAdapters::FieldRateMultiplier), RPGBossPhaseAdapters::PhaseFieldPath(SelectedPhaseId, RPGBossPhaseAdapters::FieldAttackMultiplier)};
		}
		const TArray<FString> Rest = {RPGBossPhaseFlowAdapters::FieldTransitionSeconds, RPGBossPhaseFlowAdapters::FieldUseRoarClip, RPGBossPhaseFlowAdapters::FieldPausePostureInTransition,
			RPGBossPhaseFlowAdapters::FieldLockLeapUntilPhaseTwo, RPGBossPhaseFlowAdapters::FieldAttackAbilityPrefix, RPGBossPhaseFlowAdapters::FieldLeapAbilityTag,
			FieldFireballEnabled, FieldFireballAbility, FieldFireballCooldown, FieldFireballMinRange, FieldFireballMaxRange,
			FieldRoarClip, FieldTransitionMontage, FieldImmunityEffect};
		Plan.RequiredFields.Append(Rest);
		// The id is captured by value: a later change of the caller's variable cannot change which phase this plan configures.
		Plan.Configure = [SelectedPhaseId](UActorComponent& Component, const FRPGParticipantConfig& Config, FString& OutError)
		{
			return ConfigurePhasesCluster(Component, Config, SelectedPhaseId, OutError);
		};
		return Plan;
	}
}
