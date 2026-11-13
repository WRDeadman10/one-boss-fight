// Copyright One Boss Fight. All Rights Reserved.

#pragma once

#include "CoreMinimal.h"

namespace RPGPackParry
{
	enum class ECandidateDecision : uint8
	{
	Pending,
	Confirmed,
	Rejected
	};

	/** The native parry timer is authoritative; the mirrored Blueprint tag is diagnostic only. */
	inline bool CanStartCandidate(bool bWindowOpenNowOrPrevious, bool bInvulnerableNowOrPrevious)
	{
		return bWindowOpenNowOrPrevious && !bInvulnerableNowOrPrevious;
	}

	/** Wait for the full health-observation interval. Unknown health or any observed loss fails closed. */
	inline ECandidateDecision EvaluateCandidate(bool bHealthKnown, double HealthBefore, double HealthNow,
		double ElapsedSeconds, double RequiredSeconds = 0.1, double LossTolerance = 0.001)
	{
		if (!FMath::IsFinite(ElapsedSeconds) || !FMath::IsFinite(RequiredSeconds) || RequiredSeconds < 0.0 ||
			!FMath::IsFinite(LossTolerance) || LossTolerance < 0.0)
		{
			return ECandidateDecision::Rejected;
		}
		if (ElapsedSeconds < RequiredSeconds)
		{
			return ECandidateDecision::Pending;
		}
		if (!bHealthKnown || !FMath::IsFinite(HealthBefore) || !FMath::IsFinite(HealthNow))
		{
			return ECandidateDecision::Rejected;
		}
		return HealthNow < HealthBefore - LossTolerance ? ECandidateDecision::Rejected : ECandidateDecision::Confirmed;
	}

	/** Tracked identity is boss+generation+attack-instance; untracked identity uses boss+montage start centiseconds. */
	inline FString BuildAttackKey(uint64 Generation, uint32 BossId, FName Move, int32 AttackInstance,
		FName Montage, double MontageStartWorldSeconds)
	{
		if (BossId == 0)
		{
			return FString();
		}
		if (!Move.IsNone() && AttackInstance > 0)
		{
			return FString::Printf(TEXT("G%llu|B%u|M%s|I%d"), static_cast<unsigned long long>(Generation), BossId, *Move.ToString(), AttackInstance);
		}
		if (Montage.IsNone() || !FMath::IsFinite(MontageStartWorldSeconds))
		{
			return FString();
		}
		const int64 StartCentiseconds = FMath::RoundToInt64(MontageStartWorldSeconds * 100.0);
		return FString::Printf(TEXT("G%llu|B%u|U%s|T%lld"), static_cast<unsigned long long>(Generation), BossId, *Montage.ToString(), static_cast<long long>(StartCentiseconds));
	}

	/** Shared once-per-contact-key gate used by pack-trace and project-resolver parries. */
	class FRewardDeduplicator
	{
	public:
		bool TryAccept(uint64 Generation, const FString& AttackKey)
		{
			if (AttackKey.IsEmpty())
			{
				return false;
			}
			if (!bHasGeneration || CurrentGeneration != Generation)
			{
				CurrentGeneration = Generation;
				bHasGeneration = true;
				AcceptedKeys.Reset();
			}
			if (AcceptedKeys.Contains(AttackKey))
			{
				return false;
			}
			AcceptedKeys.Add(AttackKey);
			return true;
		}

		void Reset()
		{
			bHasGeneration = false;
			AcceptedKeys.Reset();
		}

	private:
		uint64 CurrentGeneration = 0;
		bool bHasGeneration = false;
		TSet<FString> AcceptedKeys;
	};
}
