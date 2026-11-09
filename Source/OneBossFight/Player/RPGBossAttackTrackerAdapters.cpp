// Copyright One Boss Fight. All Rights Reserved.
#include "Player/RPGBossAttackTrackerAdapters.h"
#include "Player/RPGAttackTracker.h"
#include "GameFramework/Actor.h"

namespace RPGBossAttackTrackerAdapters
{
	namespace
	{
		bool CheckConfigurable(const UActorComponent& Component, FString& OutError)
		{
			if (!IsValid(&Component) || Component.IsBeingDestroyed())
			{
				OutError = TEXT("InvalidComponent: AttackTracker is destroyed or being destroyed");
				return false;
			}
			if (Component.GetClass() != URPGAttackTracker::StaticClass())
			{
				OutError = TEXT("WrongComponentClass: expected exact URPGAttackTracker");
				return false;
			}
			if (Component.HasBegunPlay())
			{
				OutError = TEXT("ComponentBegunPlay: AttackTracker configuration was already read");
				return false;
			}
			if (Component.IsRegistered())
			{
				OutError = TEXT("ComponentAlreadyRegistered: AttackTracker must be configured before registration");
				return false;
			}
			const AActor* Owner = Component.GetOwner();
			if (!Owner || !IsValid(Owner) || Owner->IsActorBeingDestroyed())
			{
				OutError = TEXT("InvalidOwner: AttackTracker has no live owner");
				return false;
			}
			if (Owner->HasActorBegunPlay() || Owner->IsActorBeginningPlay())
			{
				OutError = FString::Printf(TEXT("OwnerBegunPlay: owner %s already began or is beginning play"), *Owner->GetName());
				return false;
			}
			return true;
		}
	}

	bool IsNativeDefault(const FRPGAttackTrackerConfig& Config)
	{
		const FRPGAttackTrackerConfig Defaults;
		if (Config.Attacks.Num() != Defaults.Attacks.Num() || Config.bEnabled != Defaults.bEnabled
			|| Config.bVetoIllegalStarts != Defaults.bVetoIllegalStarts || Config.BranchRange != Defaults.BranchRange
			|| Config.BranchConeDegrees != Defaults.BranchConeDegrees) { return false; }
		for (int32 Index = 0; Index < Config.Attacks.Num(); ++Index)
		{
			const FRPGAttackTiming& A = Config.Attacks[Index];
			const FRPGAttackTiming& B = Defaults.Attacks[Index];
			if (A.MoveId != B.MoveId || A.MontageName != B.MontageName || A.FallbackMontageName != B.FallbackMontageName
				|| A.MontagePath != B.MontagePath || A.bAuthoredWindup != B.bAuthoredWindup || A.CommitTime != B.CommitTime
				|| A.ActiveStartTime != B.ActiveStartTime || A.ActiveEndTime != B.ActiveEndTime || A.RecoveryEndTime != B.RecoveryEndTime
				|| A.TrackTurnRate != B.TrackTurnRate || A.bBranchStage != B.bBranchStage || A.ClipPath != B.ClipPath) { return false; }
		}
		return true;
	}

	bool ValidateAttackTracker(const FRPGAttackTrackerConfig& Config, FString& OutError)
	{
		OutError.Reset();
		if (!FMath::IsFinite(Config.BranchRange) || Config.BranchRange < 0.f)
		{
			OutError = FString::Printf(TEXT("InvalidAttackTracker.BranchRange: expected finite and >= 0 (%s)"), FieldBranchRange);
			return false;
		}
		if (!FMath::IsFinite(Config.BranchConeDegrees) || Config.BranchConeDegrees < 10.f || Config.BranchConeDegrees > 360.f)
		{
			OutError = FString::Printf(TEXT("InvalidAttackTracker.BranchConeDegrees: expected finite in [10,360] (%s)"), FieldBranchConeDegrees);
			return false;
		}
		// Identity first, over the whole table: an empty or duplicate MoveId is reported before any per-attack check
		// (lead fix BUILD-216: otherwise a later entry's duplicate was masked by an earlier entry's reference check).
		TSet<FName> MoveIds;
		for (int32 Index = 0; Index < Config.Attacks.Num(); ++Index)
		{
			const FRPGAttackTiming& Attack = Config.Attacks[Index];
			const FString Prefix = FString::Printf(TEXT("AttackTracker.Attacks[%d]"), Index);
			if (Attack.MoveId.IsNone())
			{
				OutError = FString::Printf(TEXT("InvalidAttackTracker.MoveId: empty at %s"), *Prefix);
				return false;
			}
			if (MoveIds.Contains(Attack.MoveId))
			{
				OutError = FString::Printf(TEXT("InvalidAttackTracker.DuplicateMoveId: duplicate at %s"), *Prefix);
				return false;
			}
			MoveIds.Add(Attack.MoveId);
		}
		for (int32 Index = 0; Index < Config.Attacks.Num(); ++Index)
		{
			const FRPGAttackTiming& Attack = Config.Attacks[Index];
			const FString Prefix = FString::Printf(TEXT("AttackTracker.Attacks[%d]"), Index);
			const float Times[] = {Attack.CommitTime, Attack.ActiveStartTime, Attack.ActiveEndTime, Attack.RecoveryEndTime, Attack.TrackTurnRate};
			for (float Time : Times)
			{
				if (!FMath::IsFinite(Time) || Time < 0.f)
				{
					OutError = FString::Printf(TEXT("InvalidAttackTracker.Timing: expected finite and >= 0 at %s"), *Prefix);
					return false;
				}
			}
			if (Attack.CommitTime > Attack.ActiveStartTime || Attack.ActiveStartTime > Attack.ActiveEndTime || Attack.ActiveEndTime > Attack.RecoveryEndTime)
			{
				OutError = FString::Printf(TEXT("InvalidAttackTracker.Order: commit <= active start <= active end <= recovery at %s"), *Prefix);
				return false;
			}
			// Native defaults intentionally preserve the old constructor table's reference semantics.
			// Several legacy entries identify clips through runtime lookup and have no serialized montage path.
			if (!IsNativeDefault(Config) && (Attack.MontageName.IsEmpty() || (Attack.ClipPath.IsEmpty() && Attack.MontagePath.IsEmpty() && Attack.FallbackMontageName.IsEmpty())))
			{
				OutError = FString::Printf(TEXT("InvalidAttackTracker.Reference: montage identity required at %s"), *Prefix);
				return false;
			}
		}
		if (Config.Attacks.IsEmpty())
		{
			OutError = FString::Printf(TEXT("InvalidAttackTracker.Empty: at least one move is required (%s)"), FieldAttacks);
			return false;
		}
		return true;
	}

	bool ConfigureAttackTracker(UActorComponent& Component, const FRPGParticipantConfig& Config, FString& OutError)
	{
		OutError.Reset();
		if (Component.GetClass() != URPGAttackTracker::StaticClass())
		{
			OutError = TEXT("WrongComponentClass: expected URPGAttackTracker exact class");
			return false;
		}
		if (!CheckConfigurable(Component, OutError))
		{
			return false;
		}
		if (!ValidateAttackTracker(Config.AttackTracker, OutError)) { return false; }
		URPGAttackTracker* Tracker = CastChecked<URPGAttackTracker>(&Component);
		Tracker->Attacks = Config.AttackTracker.Attacks;
		Tracker->bEnabled = Config.AttackTracker.bEnabled;
		Tracker->bVetoIllegalStarts = Config.AttackTracker.bVetoIllegalStarts;
		Tracker->BranchRange = Config.AttackTracker.BranchRange;
		Tracker->BranchConeDegrees = Config.AttackTracker.BranchConeDegrees;
		Tracker->bUseMontageNotifyTimings = Config.bUseMontageNotifyTimings;
		return true;
	}

	FRPGComponentPlan MakeAttackTrackerPlan()
	{
		FRPGComponentPlan Plan;
		Plan.Class = URPGAttackTracker::StaticClass();
		Plan.InstanceName = TEXT("RPGAttackTracker");
		Plan.RequiredFields = {FieldAttacks, FieldEnabled, FieldVetoIllegalStarts, FieldBranchRange, FieldBranchConeDegrees};
		Plan.Configure = &ConfigureAttackTracker;
		return Plan;
	}
}
