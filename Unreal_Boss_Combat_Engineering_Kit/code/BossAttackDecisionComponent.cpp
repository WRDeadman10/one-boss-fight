#include "BossAttackDecisionComponent.h"
#include "BossAttackData.h"
#include "Engine/World.h"

UBossAttackDecisionComponent::UBossAttackDecisionComponent()
{
    PrimaryComponentTick.bCanEverTick = false; // Only evaluate at authorized gates.
}

bool UBossAttackDecisionComponent::IsEligible(const UBossAttackData* A,
    const FBossCombatContext& C, FString& Why) const
{
    if (!IsValid(A) || !IsValid(A->Montage)) { Why = TEXT("MissingAssetOrMontage"); return false; }
    if (!IsValid(C.TargetActor)) { Why = TEXT("InvalidTarget"); return false; }
    if (C.Phase < A->MinimumPhase) { Why = TEXT("Phase"); return false; }
    if (A->bRequiresLOS && !C.bHasLineOfSight) { Why = TEXT("NoLOS"); return false; }
    if (C.DistanceCm < A->MinRangeCm || C.DistanceCm > A->MaxRangeCm)
    { Why = TEXT("Range"); return false; }
    const float AbsYaw = FMath::Abs(C.SignedYawDeg);
    if (AbsYaw < A->MinAbsoluteYawDeg || AbsYaw > A->MaxAbsoluteYawDeg)
    { Why = TEXT("Angle"); return false; }
    const float* NextReady = NextReadyWorldTimeSeconds.Find(A->AttackID);
    if (NextReady && C.TimestampS < *NextReady)
    { Why = TEXT("Cooldown"); return false; }
    return true;
}

float UBossAttackDecisionComponent::Score(const UBossAttackData* A,
    const FBossCombatContext& C) const
{
    const float RangeTolerance = FMath::Max(100.f, A->MaxRangeCm - A->MinRangeCm);
    const float RangeFit = 1.f - FMath::Clamp(
        FMath::Abs(C.DistanceCm - A->PreferredRangeCm) / RangeTolerance, 0.f, 1.f);
    const float AbsYaw = FMath::Abs(C.SignedYawDeg);
    const float AngleCenter = (A->MinAbsoluteYawDeg + A->MaxAbsoluteYawDeg) * 0.5f;
    const float AngleFit = 1.f - FMath::Clamp(
        FMath::Abs(AbsYaw - AngleCenter) / FMath::Max(15.f, A->MaxAbsoluteYawDeg), 0.f, 1.f);
    const float Opportunity = FMath::Clamp(C.TargetRecoveryRemainingS, 0.f, 1.f);
    // Starter weights: extend with spacing, phase, recent-history and reaction factors.
    return FMath::Max(0.f, A->BaseWeight * (0.50f * RangeFit + 0.30f * AngleFit
                                            + 0.20f * Opportunity));
}

UBossAttackData* UBossAttackDecisionComponent::SelectBestAttack(
    const FBossCombatContext& C, const TArray<UBossAttackData*>& Pool,
    TArray<FBossDecisionCandidate>& OutTrace) const
{
    OutTrace.Reset();
    UBossAttackData* Best = nullptr;
    float BestScore = -FLT_MAX;
    for (UBossAttackData* A : Pool)
    {
        FBossDecisionCandidate Entry;
        Entry.AttackID = A ? A->AttackID : NAME_None;
        FString Why;
        Entry.bEligible = IsEligible(A, C, Why);
        Entry.RejectionReason = Why;
        if (Entry.bEligible)
        {
            Entry.Score = Score(A, C);
            if (Entry.Score > BestScore)
            { Best = A; BestScore = Entry.Score; }
        }
        OutTrace.Add(MoveTemp(Entry));
    }
    // Deterministic best-choice V0. For more varied combat implement seeded,
    // bounded weighted sampling across near-best candidates, as in doc 03.
    return Best;
}
