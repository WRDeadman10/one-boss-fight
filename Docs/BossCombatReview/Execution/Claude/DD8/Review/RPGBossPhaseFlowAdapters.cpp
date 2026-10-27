// Copyright One Boss Fight. All Rights Reserved.

#include "Player/RPGBossPhaseFlowAdapters.h"
#include "Components/ActorComponent.h"
#include "GameFramework/Actor.h"
#include "Player/RPGBossPhases.h"

namespace RPGBossPhaseFlowAdapters
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
	}

	bool ValidatePhaseFlow(const FRPGPhaseFlowConfig& Flow, FString& OutError)
	{
		OutError.Reset();
		// (1) Finite first: a NaN compares false with everything and must never reach the sign test.
		if (!FMath::IsFinite(Flow.TransitionSeconds))
		{
			OutError = FString::Printf(TEXT("InvalidPhaseFlow.NotFinite: %s=%s"), FieldTransitionSeconds, *LexToString(Flow.TransitionSeconds));
			return false;
		}
		// (2) Not negative. Zero is valid and no editor floor is applied; a negative -0.0 is zero.
		if (Flow.TransitionSeconds < 0.f)
		{
			OutError = FString::Printf(TEXT("InvalidPhaseFlow.Negative: %s=%s, expected 0 or more"), FieldTransitionSeconds, *LexToString(Flow.TransitionSeconds));
			return false;
		}
		// (3) The prefix: identity only. Neither empty nor only whitespace; the authored value itself is never trimmed or changed (the trimmed copy is used for this test alone).
		if (Flow.AttackAbilityPrefix.TrimStartAndEnd().IsEmpty())
		{
			OutError = FString::Printf(TEXT("InvalidPhaseFlow.EmptyPrefix: %s is empty or only whitespace"), FieldAttackAbilityPrefix);
			return false;
		}
		// (4) The tag: identity only. Not None; no gameplay tag is requested or registered, and nothing says that the tag exists.
		if (Flow.LeapAbilityTag.IsNone())
		{
			OutError = FString::Printf(TEXT("InvalidPhaseFlow.NoLeapTag: %s is None"), FieldLeapAbilityTag);
			return false;
		}
		return true;
	}

	bool ConfigurePhaseFlow(UActorComponent& Component, const FRPGParticipantConfig& Config, FString& OutError)
	{
		OutError.Reset();
		// Every check, lifecycle first, then the whole record, happens before the one write block.
		if (!CheckConfigurable(Component, URPGBossPhases::StaticClass(), OutError) || !ValidatePhaseFlow(Config.PhaseFlow, OutError))
		{
			return false;
		}
		URPGBossPhases* Phases = CastChecked<URPGBossPhases>(&Component);
		const FRPGPhaseFlowConfig& Flow = Config.PhaseFlow;
		Phases->TransitionSeconds = Flow.TransitionSeconds;
		Phases->bUseRoarClip = Flow.bUseRoarClip;
		Phases->bPausePostureInTransition = Flow.bPausePostureInTransition;
		Phases->bLockLeapUntilPhaseTwo = Flow.bLockLeapUntilPhaseTwo;
		Phases->AttackAbilityPrefix = Flow.AttackAbilityPrefix; // as authored, not trimmed
		Phases->LeapAbilityTag = Flow.LeapAbilityTag;           // as authored, no tag registration
		return true;
	}

	FRPGComponentPlan MakePhaseFlowPlan()
	{
		FRPGComponentPlan Plan;
		Plan.Class = URPGBossPhases::StaticClass();
		Plan.InstanceName = TEXT("RPGBossPhases");
		Plan.RequiredFields = {FieldTransitionSeconds, FieldUseRoarClip, FieldPausePostureInTransition, FieldLockLeapUntilPhaseTwo, FieldAttackAbilityPrefix, FieldLeapAbilityTag};
		Plan.Configure = &ConfigurePhaseFlow;
		return Plan;
	}
}
