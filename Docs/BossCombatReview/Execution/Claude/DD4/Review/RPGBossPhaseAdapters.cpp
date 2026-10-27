// Copyright One Boss Fight. All Rights Reserved.

#include "Player/RPGBossPhaseAdapters.h"
#include "Components/ActorComponent.h"
#include "GameFramework/Actor.h"
#include "Player/RPGBossPhases.h"

namespace RPGBossPhaseAdapters
{
	namespace
	{
		/** The same lifecycle boundary as the accepted stats adapters: the component is alive, exactly the expected class, unregistered and not begun, under a live owner that has not begun play. Writes nothing. */
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

		bool IsNotFinite(FName PhaseId, const TCHAR* Field, float Value, FString& OutError)
		{
			if (FMath::IsFinite(Value))
			{
				return false;
			}
			OutError = FString::Printf(TEXT("InvalidPhase.NotFinite: %s=%s"), *PhaseFieldPath(PhaseId, Field), *LexToString(Value));
			return true;
		}

		/** The selected record when the selection and the set are acceptable, else nullptr and a named message. Selection is by id only. */
		const FRPGPhaseConfig* SelectRecord(const TArray<FRPGPhaseConfig>& Phases, FName SelectedPhaseId, FString& OutError)
		{
			if (SelectedPhaseId.IsNone())
			{
				OutError = TEXT("InvalidPhase.NoSelection: no phase id was selected (never the first, the last or index 0)");
				return nullptr;
			}
			if (Phases.IsEmpty())
			{
				OutError = FString::Printf(TEXT("InvalidPhase.NoRecords: the config has no phase record, selected '%s'"), *SelectedPhaseId.ToString());
				return nullptr;
			}
			int32 Matches = 0;
			const FRPGPhaseConfig* Selected = nullptr;
			for (const FRPGPhaseConfig& Phase : Phases)
			{
				if (Phase.PhaseId == SelectedPhaseId)
				{
					++Matches;
					if (!Selected)
					{
						Selected = &Phase;
					}
				}
			}
			if (Matches == 0)
			{
				OutError = FString::Printf(TEXT("InvalidPhase.NotFound: no record has the id '%s' (%d record(s) in the config)"), *SelectedPhaseId.ToString(), Phases.Num());
				return nullptr;
			}
			// Capability of this backend: one transition. An extra record, or a duplicate of the selected id, is refused by name; nothing is silently picked.
			if (Matches > 1 || Phases.Num() > NativeTransitionRecords)
			{
				OutError = FString::Printf(TEXT("UnsupportedNativePhaseSet: %d record(s), %d with the id '%s'; the native backend represents exactly %d transition"), Phases.Num(), Matches, *SelectedPhaseId.ToString(), NativeTransitionRecords);
				return nullptr;
			}
			return Selected;
		}
	}

	FString PhaseFieldPath(FName PhaseId, const TCHAR* Field)
	{
		return FString::Printf(TEXT("Phases[%s].%s"), *PhaseId.ToString(), Field);
	}

	bool ValidatePhases(const TArray<FRPGPhaseConfig>& Phases, FName SelectedPhaseId, FString& OutError)
	{
		OutError.Reset();
		const FRPGPhaseConfig* Record = SelectRecord(Phases, SelectedPhaseId, OutError);
		if (!Record)
		{
			return false;
		}
		// Finite first for all four fields: a NaN compares false with everything and must never reach a sign test.
		if (IsNotFinite(SelectedPhaseId, FieldEntryHealthFraction, Record->EntryHealthFraction, OutError) || IsNotFinite(SelectedPhaseId, FieldSpeedMultiplier, Record->SpeedMultiplier, OutError)
			|| IsNotFinite(SelectedPhaseId, FieldRateMultiplier, Record->RateMultiplier, OutError) || IsNotFinite(SelectedPhaseId, FieldAttackMultiplier, Record->AttackMultiplier, OutError))
		{
			return false;
		}
		// Generic validity: the threshold is a health fraction above 0 and at most 1, the multipliers are positive. No rule that a multiplier must be at least 1.
		if (Record->EntryHealthFraction <= 0.f || Record->EntryHealthFraction > 1.f)
		{
			OutError = FString::Printf(TEXT("InvalidPhase.ThresholdOutOfRange: %s=%s, expected above 0 and at most 1"), *PhaseFieldPath(SelectedPhaseId, FieldEntryHealthFraction), *LexToString(Record->EntryHealthFraction));
			return false;
		}
		const struct { const TCHAR* Field; float Value; } Multipliers[] = {
			{FieldSpeedMultiplier, Record->SpeedMultiplier}, {FieldRateMultiplier, Record->RateMultiplier}, {FieldAttackMultiplier, Record->AttackMultiplier}};
		for (const auto& Multiplier : Multipliers)
		{
			if (Multiplier.Value <= 0.f)
			{
				OutError = FString::Printf(TEXT("InvalidPhase.NotPositive: %s=%s"), *PhaseFieldPath(SelectedPhaseId, Multiplier.Field), *LexToString(Multiplier.Value));
				return false;
			}
		}
		// Native arithmetic, separate from validity. The native reset divides by speed and by rate, so a value whose float inverse is not finite cannot be reversed: refused, never clamped.
		if (!FMath::IsFinite(1.f / Record->SpeedMultiplier))
		{
			OutError = FString::Printf(TEXT("UnsupportedNativeInverse: %s=%s has no finite inverse, the native reset divides by it"), *PhaseFieldPath(SelectedPhaseId, FieldSpeedMultiplier), *LexToString(Record->SpeedMultiplier));
			return false;
		}
		if (!FMath::IsFinite(1.f / Record->RateMultiplier))
		{
			OutError = FString::Printf(TEXT("UnsupportedNativeInverse: %s=%s has no finite inverse, the native reset scales by it"), *PhaseFieldPath(SelectedPhaseId, FieldRateMultiplier), *LexToString(Record->RateMultiplier));
			return false;
		}
		// The native reset subtracts the applied attack only when it is positive, so a factor below the floor would be applied and never reversed.
		if (Record->AttackMultiplier < NativeDamageScaleFloor)
		{
			OutError = FString::Printf(TEXT("UnsupportedNativeDamageScale: %s=%s, the native reset reverses an attack increase only (factor at least %s)"), *PhaseFieldPath(SelectedPhaseId, FieldAttackMultiplier), *LexToString(Record->AttackMultiplier), *LexToString(NativeDamageScaleFloor));
			return false;
		}
		return true;
	}

	bool ConfigurePhases(UActorComponent& Component, const FRPGParticipantConfig& Config, FName SelectedPhaseId, FString& OutError)
	{
		OutError.Reset();
		// Every check, lifecycle first, then the selection and the whole record, happens before the one write block.
		if (!CheckConfigurable(Component, URPGBossPhases::StaticClass(), OutError) || !ValidatePhases(Config.Phases, SelectedPhaseId, OutError))
		{
			return false;
		}
		const FRPGPhaseConfig* Record = SelectRecord(Config.Phases, SelectedPhaseId, OutError); // validated just now: exactly one record with this id
		if (!Record)
		{
			return false;
		}
		URPGBossPhases* Phases = CastChecked<URPGBossPhases>(&Component);
		Phases->PhaseTwoHealthFraction = Record->EntryHealthFraction;
		Phases->MovementScale = Record->SpeedMultiplier;
		Phases->AttackRateScale = Record->RateMultiplier;
		Phases->DamageScale = Record->AttackMultiplier;
		return true;
	}

	FRPGComponentPlan MakePhasePlan(FName SelectedPhaseId)
	{
		FRPGComponentPlan Plan;
		Plan.Class = URPGBossPhases::StaticClass();
		Plan.InstanceName = TEXT("RPGBossPhases");
		if (!SelectedPhaseId.IsNone())
		{
			Plan.RequiredFields = {PhaseFieldPath(SelectedPhaseId, FieldEntryHealthFraction), PhaseFieldPath(SelectedPhaseId, FieldSpeedMultiplier),
				PhaseFieldPath(SelectedPhaseId, FieldRateMultiplier), PhaseFieldPath(SelectedPhaseId, FieldAttackMultiplier)};
		}
		// The id is captured by value: a later change of the caller's variable cannot change which phase this plan configures.
		Plan.Configure = [SelectedPhaseId](UActorComponent& Component, const FRPGParticipantConfig& Config, FString& OutError)
		{
			return ConfigurePhases(Component, Config, SelectedPhaseId, OutError);
		};
		return Plan;
	}
}
