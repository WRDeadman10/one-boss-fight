// Copyright One Boss Fight. All Rights Reserved.

#include "Player/RPGMontageNotifyTiming.h"
#include "Animation/AnimMontage.h"
#include <cmath>

namespace RPGMontageNotifyTiming
{
	namespace
	{
		bool Finite(float Value) { return std::isfinite(Value); }
	}

	FRPGAttackTiming FAnnotation::ToAttackTiming(const FRPGAttackTiming& LegacyTiming) const
	{
		FRPGAttackTiming Result = LegacyTiming;
		Result.CommitTime = CommitTime;
		Result.ActiveStartTime = WindowStartTime;
		Result.ActiveEndTime = WindowEndTime;
		Result.RecoveryEndTime = RecoveryEndTime;
		Result.TrackTurnRate = TrackTurnRate;
		Result.bBranchStage = bBranchStage;
		Result.bAuthoredWindup = bAuthoredWindup;
		return Result;
	}

	bool Validate(const FAnnotation& A, FString& OutError)
	{
		OutError.Reset();
		if (A.MontageObjectPath.IsEmpty() || !A.MontageObjectPath.StartsWith(TEXT("/Game/")) || A.MoveId.IsNone())
		{
			OutError = TEXT("InvalidMontageNotifyTiming.Identity"); return false;
		}
		const float Values[] = { A.MontageLength, A.CommitTime, A.WindowStartTime, A.WindowEndTime,
			A.RecoveryEndTime, A.TrackTurnRate, A.BranchRange, A.BranchConeDegrees };
		for (float Value : Values)
		{
			if (!Finite(Value)) { OutError = TEXT("InvalidMontageNotifyTiming.NonFinite"); return false; }
		}
		if (A.MontageLength <= 0.f || A.CommitTime < 0.f || A.WindowStartTime < A.CommitTime
			|| A.WindowEndTime <= A.WindowStartTime || A.RecoveryEndTime < A.WindowEndTime || A.RecoveryEndTime > A.MontageLength
			|| A.TrackTurnRate < 0.f || A.BranchRange < 0.f || A.BranchConeDegrees < 10.f || A.BranchConeDegrees > 360.f
			)
		{
			OutError = TEXT("InvalidMontageNotifyTiming.OrderOrBounds"); return false;
		}
		return true;
	}

	bool CollectAnnotations(const UAnimMontage& Montage, TArray<FAnnotation>& OutAnnotations, FString& OutError)
	{
		OutAnnotations.Reset();
		OutError.Reset();
		const float MontageLength = Montage.GetPlayLength();
		for (const FAnimNotifyEvent& Event : Montage.Notifies)
		{
			const URPGANS_BossMoveTiming* Notify = Cast<URPGANS_BossMoveTiming>(Event.NotifyStateClass);
			if (!Notify) continue;

			FAnnotation A;
			A.MontageObjectPath = Montage.GetPathName();
			A.MoveId = Notify->MoveId;
			A.MontageLength = MontageLength;
			A.CommitTime = Notify->CommitTime;
			A.WindowStartTime = Notify->WindowStartTime;
			A.WindowEndTime = Notify->WindowEndTime;
			A.RecoveryEndTime = Notify->RecoveryEndTime;
			A.TrackTurnRate = Notify->TrackTurnRate;
			A.bBranchStage = Notify->bBranchStage;
			A.BranchRange = Notify->BranchRange;
			A.BranchConeDegrees = Notify->BranchConeDegrees;
			A.bAuthoredWindup = Notify->bAuthoredWindup;
			if (!Validate(A, OutError))
			{
				OutAnnotations.Reset();
				return false;
			}
			OutAnnotations.Add(MoveTemp(A));
		}
		return true;
	}

	bool SelectTiming(bool bEnabled, const TArray<FAnnotation>& Annotations, const FString& MontageObjectPath, FName MoveId,
		const FRPGAttackTiming& LegacyTiming, float LegacyBranchRange, float LegacyBranchConeDegrees, FRPGAttackTiming& OutTiming,
		float& OutBranchRange, float& OutBranchConeDegrees, FString& OutError)
	{
		OutError.Reset();
		OutTiming = LegacyTiming;
		OutBranchRange = LegacyBranchRange;
		OutBranchConeDegrees = LegacyBranchConeDegrees;
		if (!bEnabled || Annotations.IsEmpty()) return true;

		int32 MatchIndex = INDEX_NONE;
		for (int32 Index = 0; Index < Annotations.Num(); ++Index)
		{
			if (!Validate(Annotations[Index], OutError)) return false;
			for (int32 Other = 0; Other < Index; ++Other)
			{
				if (Annotations[Other].MontageObjectPath == Annotations[Index].MontageObjectPath && Annotations[Other].MoveId == Annotations[Index].MoveId)
				{
					OutError = TEXT("InvalidMontageNotifyTiming.DuplicateIdentity"); return false;
				}
			}
			if (Annotations[Index].MontageObjectPath == MontageObjectPath && Annotations[Index].MoveId == MoveId) MatchIndex = Index;
		}
		if (MatchIndex != INDEX_NONE)
		{
			OutTiming = Annotations[MatchIndex].ToAttackTiming(LegacyTiming);
			OutBranchRange = Annotations[MatchIndex].BranchRange;
			OutBranchConeDegrees = Annotations[MatchIndex].BranchConeDegrees;
		}
		return true;
	}

	bool FObserver::Begin(const FString& InMontageObjectPath, FName InMoveId)
	{
		Reset();
		if (!bEnabled || InMontageObjectPath.IsEmpty() || InMoveId.IsNone()) return false;
		MontageObjectPath = InMontageObjectPath;
		MoveId = InMoveId;
		bInitialized = true;
		return true;
	}

	bool FObserver::Sample(float Position, const FAnnotation& Annotation, EPhase& OutPhase)
	{
		FString Error;
		if (!bInitialized || !Validate(Annotation, Error) || !Finite(Position)
			|| Annotation.MontageObjectPath != MontageObjectPath || Annotation.MoveId != MoveId || Position < 0.f || Position > Annotation.MontageLength)
		{
			Reset(); return false;
		}
		const EPhase NewPhase = Position < Annotation.CommitTime ? EPhase::Tell
			: Position < Annotation.WindowStartTime ? EPhase::Committed
			: Position < Annotation.WindowEndTime ? EPhase::Active
			: Position < Annotation.RecoveryEndTime ? EPhase::Recovery : EPhase::Complete;
		if (bInitialized && Position < LastPosition) { Reset(); return false; }
		LastPosition = Position;
		Phase = NewPhase;
		OutPhase = NewPhase;
		return true;
	}

	void FObserver::Reset()
	{
		bInitialized = false;
		MontageObjectPath.Reset();
		MoveId = NAME_None;
		Phase = EPhase::Tell;
		LastPosition = -1.f;
	}

	bool FCache::Resolve(bool bEnabled, const UAnimMontage* Montage, uint64 AttackInstanceId, FName MoveId,
		const FRPGAttackTiming& LegacyTiming, float LegacyBranchRange, float LegacyBranchConeDegrees,
		FRPGAttackTiming& OutTiming, float& OutBranchRange, float& OutBranchConeDegrees, FString& OutError, bool& bOutWarnOnce)
	{
		bOutWarnOnce = false;
		OutError.Reset();
		if (!bEnabled || !Montage)
		{
			OutTiming = LegacyTiming; OutBranchRange = LegacyBranchRange; OutBranchConeDegrees = LegacyBranchConeDegrees; return true;
		}
		if (!bHasResult || CachedMontage.Get() != Montage || CachedAttackInstanceId != AttackInstanceId)
		{
			CachedMontage = Montage;
			CachedAttackInstanceId = AttackInstanceId;
			bHasResult = true;
			bCachedValid = true;
			bCachedWarned = false;
			CachedTiming = LegacyTiming;
			CachedBranchRange = LegacyBranchRange;
			CachedBranchConeDegrees = LegacyBranchConeDegrees;
			CachedError.Reset();
			TArray<FAnnotation> Annotations;
			FString Error;
			bCachedValid = CollectAnnotations(*Montage, Annotations, Error)
				&& SelectTiming(true, Annotations, Montage->GetPathName(), MoveId, LegacyTiming, LegacyBranchRange,
					LegacyBranchConeDegrees, CachedTiming, CachedBranchRange, CachedBranchConeDegrees, Error);
			if (!bCachedValid) CachedError = Error;
		}
		OutTiming = CachedTiming;
		OutBranchRange = CachedBranchRange;
		OutBranchConeDegrees = CachedBranchConeDegrees;
		OutError = CachedError;
		if (!bCachedValid && !bCachedWarned) { bCachedWarned = true; bOutWarnOnce = true; }
		return bCachedValid;
	}

	void FCache::Reset()
	{
		CachedMontage.Reset(); CachedAttackInstanceId = MAX_uint64; bHasResult = false; bCachedValid = true;
		bCachedWarned = false; CachedTiming = FRPGAttackTiming(); CachedBranchRange = 0.f;
		CachedBranchConeDegrees = 120.f; CachedError.Reset();
	}
}
