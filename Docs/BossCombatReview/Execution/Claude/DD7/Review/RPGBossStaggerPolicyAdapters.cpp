// Copyright One Boss Fight. All Rights Reserved.

#include "Player/RPGBossStaggerPolicyAdapters.h"
#include "Components/ActorComponent.h"
#include "GameFramework/Actor.h"
#include "Player/RPGBossStagger.h"

namespace RPGBossStaggerPolicyAdapters
{
	namespace
	{
		/** The same lifecycle boundary as the accepted stats, phase and encounter policy adapters (restated here because those files must not change): a live component of exactly the expected class, unregistered
		 *  and not begun, under a live owner that has not begun play. Writes nothing. */
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

		enum class EDomain : uint8
		{
			NonNegative,        // zero keeps the native immediate, empty-window or no-cooldown meaning
			Positive,           // the native code divides by it
			Angle360,           // [0, 360] degrees
			CriticalCapability, // checked last, as a native capability
		};

		struct FScalar
		{
			const TCHAR* Path;
			float Value;
			EDomain Domain;
		};
	}

	bool ValidateStaggerPolicy(const FRPGStaggerPolicyConfig& Policy, FString& OutError)
	{
		OutError.Reset();
		// The thirteen scalars in field order. The bool needs no check.
		const FScalar Scalars[] = {
			{FieldStaggerSeconds, Policy.StaggerSeconds, EDomain::NonNegative},
			{FieldFreezeAtPosition, Policy.FreezeAtPosition, EDomain::NonNegative},
			{FieldCriticalMultiplier, Policy.CriticalMultiplier, EDomain::CriticalCapability},
			{FieldRiposteRange, Policy.RiposteRange, EDomain::NonNegative},
			{FieldRiposteConeDegrees, Policy.RiposteConeDegrees, EDomain::Angle360},
			{FieldRiposteFacingDegrees, Policy.RiposteFacingDegrees, EDomain::Angle360},
			{FieldRiposteArmSeconds, Policy.RiposteArmSeconds, EDomain::NonNegative},
			{FieldRipostePlayerStartGap, Policy.RipostePlayerStartGap, EDomain::NonNegative},
			{FieldRiposteAlignSeconds, Policy.RiposteAlignSeconds, EDomain::Positive},
			{FieldRiposteImpactSeconds, Policy.RiposteImpactSeconds, EDomain::NonNegative},
			{FieldRiposteBaseDamage, Policy.RiposteBaseDamage, EDomain::NonNegative},
			{FieldCooldownSeconds, Policy.CooldownSeconds, EDomain::NonNegative},
			{FieldGetUpRate, Policy.GetUpRate, EDomain::Positive},
		};

		// (1) Every scalar finite first: a NaN compares false with everything and must never reach a sign or range test.
		for (const FScalar& Scalar : Scalars)
		{
			if (!FMath::IsFinite(Scalar.Value))
			{
				OutError = FString::Printf(TEXT("InvalidStagger.NotFinite: %s=%s"), Scalar.Path, *LexToString(Scalar.Value));
				return false;
			}
		}
		// (2) The generic domains, in field order. Nothing is clamped.
		for (const FScalar& Scalar : Scalars)
		{
			switch (Scalar.Domain)
			{
			case EDomain::NonNegative:
				if (Scalar.Value < 0.f)
				{
					OutError = FString::Printf(TEXT("InvalidStagger.Negative: %s=%s, expected 0 or more"), Scalar.Path, *LexToString(Scalar.Value));
					return false;
				}
				break;
			case EDomain::Positive:
				if (Scalar.Value <= 0.f)
				{
					OutError = FString::Printf(TEXT("InvalidStagger.NotPositive: %s=%s, the native code divides by it"), Scalar.Path, *LexToString(Scalar.Value));
					return false;
				}
				break;
			case EDomain::Angle360:
				if (Scalar.Value < 0.f || Scalar.Value > 360.f)
				{
					OutError = FString::Printf(TEXT("InvalidStagger.AngleOutOfRange: %s=%s, expected degrees within 0 and 360"), Scalar.Path, *LexToString(Scalar.Value));
					return false;
				}
				break;
			case EDomain::CriticalCapability:
				break; // a native capability, checked after every generic domain
			}
		}
		// (3) The native capability: the critical hit takes Health - Loss * (CriticalMultiplier - 1), so a multiplier below 1 would add health. Refused by name, not a balancing decision.
		if (Policy.CriticalMultiplier < NativeCriticalMultiplierFloor)
		{
			OutError = FString::Printf(TEXT("UnsupportedNativeCritical: %s=%s, the native critical hit subtracts Loss*(multiplier-1) from health, so a value below %s would add health"),
				FieldCriticalMultiplier, *LexToString(Policy.CriticalMultiplier), *LexToString(NativeCriticalMultiplierFloor));
			return false;
		}
		return true;
	}

	bool ConfigureStaggerPolicy(UActorComponent& Component, const FRPGParticipantConfig& Config, FString& OutError)
	{
		OutError.Reset();
		// Every check, lifecycle first, then the whole policy, happens before the one write block.
		if (!CheckConfigurable(Component, URPGBossStagger::StaticClass(), OutError) || !ValidateStaggerPolicy(Config.StaggerPolicy, OutError))
		{
			return false;
		}
		URPGBossStagger* Stagger = CastChecked<URPGBossStagger>(&Component);
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
		return true;
	}

	FRPGComponentPlan MakeStaggerPolicyPlan()
	{
		FRPGComponentPlan Plan;
		Plan.Class = URPGBossStagger::StaticClass();
		Plan.InstanceName = TEXT("RPGBossStagger");
		Plan.RequiredFields = {FieldStaggerSeconds, FieldFreezeAtPosition, FieldCriticalMultiplier, FieldRiposteRange, FieldRiposteConeDegrees, FieldRiposteFacingDegrees, FieldRiposteArmSeconds,
			FieldRipostePlayerStartGap, FieldRiposteAlignSeconds, FieldRiposteImpactSeconds, FieldRiposteBaseDamage, FieldCooldownSeconds, FieldGetUpRate, FieldHoldPostureAtZero};
		Plan.Configure = &ConfigureStaggerPolicy;
		return Plan;
	}
}
