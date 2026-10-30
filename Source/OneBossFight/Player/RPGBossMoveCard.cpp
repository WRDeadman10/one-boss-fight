// Copyright One Boss Fight. All Rights Reserved.
#include "Player/RPGBossMoveCard.h"
#include "Animation/AnimMontage.h"
#include "Animation/AnimSequence.h"
#include "Animation/Skeleton.h"
#include "Engine/SkeletalMesh.h"

namespace RPGBossMoveCards
{
namespace
{
    constexpr double Ceiling = 1.0e6;
    void Fail(FRPGBossMoveIssues& R, const TCHAR* Token, const FString& Field)
    { R.Errors.Add(FString::Printf(TEXT("%s[%s]"), Token, *Field)); }
    bool Number(FRPGBossMoveIssues& R, const TCHAR* Name, double Value, bool Positive = false)
    {
        if (!FMath::IsFinite(Value)) { Fail(R, TEXT("MoveCard.NonFinite"), Name); return false; }
        if (Value < 0.0 || Value > Ceiling || (Positive && Value == 0.0))
        { Fail(R, TEXT("MoveCard.Domain"), Name); return false; }
        return true;
    }
}
struct FCompiler
{
    static void Publish(const FRPGBossMoveCardSpec& S, const FRPGBossMoveMetadata& M,
        TArray<TStrongObjectPtr<UObject>>&& Leases, TSharedPtr<const FRPGCompiledBossMoveCard>& Out)
    { Out = MakeShareable(new FRPGCompiledBossMoveCard(S, M, MoveTemp(Leases))); }
};
FRPGBossMoveIssues Validate(const FRPGBossMoveCardSpec& S, const FRPGBossMoveMetadata& M)
{
    FRPGBossMoveIssues R;
    if (S.Schema != 1 || S.MoveId.IsNone() || S.FamilyId.IsNone() || S.PhaseId.IsNone())
        Fail(R, TEXT("MoveCard.Identity"), TEXT("Schema/MoveId/FamilyId/PhaseId"));
    const bool bSequence = !S.Sequence.IsNull(), bMontage = !S.Montage.IsNull();
    if (bSequence == bMontage) Fail(R, TEXT("MoveCard.AnimationSource"), TEXT("exactly one sequence OR montage"));
    const FSoftObjectPath Requested = bSequence ? S.Sequence.ToSoftObjectPath() : S.Montage.ToSoftObjectPath();
    if (!Requested.IsValid() || Requested != M.AnimationPath)
        Fail(R, TEXT("MoveCard.AnimationIdentity"), TEXT("selected source vs resolved descriptor"));
    const FSoftObjectPath Expected = S.Skeleton.ToSoftObjectPath();
    if (!Expected.IsValid() || Expected != M.SkeletonPath || Expected != M.AnimationSkeletonPath || Expected != M.MeshSkeletonPath)
        Fail(R, TEXT("MoveCard.SkeletonIdentity"), TEXT("declared/resolved/animation/mesh skeleton"));
    if (S.SlotName.IsNone() || !M.Slots.Contains(S.SlotName)) Fail(R, TEXT("MoveCard.Slot"), TEXT("SlotName"));
    if (!S.SectionName.IsNone() && (!bMontage || !M.Sections.Contains(S.SectionName)))
        Fail(R, TEXT("MoveCard.Section"), TEXT("SectionName"));
    if (S.bUsesRootMotion || M.bRootMotion) Fail(R, TEXT("MoveCard.UnsupportedRootMotion"), TEXT("first backend is in-place only"));
    Number(R, TEXT("PlayRate"), S.PlayRate, true);
    Number(R, TEXT("ClipLengthSeconds"), M.ClipLengthSeconds, true);
    Number(R, TEXT("CommitSeconds"), S.CommitSeconds);
    Number(R, TEXT("ActiveStartSeconds"), S.ActiveStartSeconds);
    Number(R, TEXT("ActiveEndSeconds"), S.ActiveEndSeconds);
    Number(R, TEXT("RecoveryEndSeconds"), S.RecoveryEndSeconds);
    Number(R, TEXT("TrackDegreesPerSecond"), S.TrackDegreesPerSecond);
    Number(R, TEXT("MinRangeCm"), S.MinRangeCm);
    Number(R, TEXT("MaxRangeCm"), S.MaxRangeCm);
    Number(R, TEXT("FrontConeDegrees"), S.FrontConeDegrees);
    Number(R, TEXT("HPDamage"), S.HPDamage);
    if (S.FrontConeDegrees > 360.f || S.MaxRangeCm < S.MinRangeCm)
        Fail(R, TEXT("MoveCard.Eligibility"), TEXT("cone or range order"));
    if (!(S.CommitSeconds <= S.ActiveStartSeconds && S.ActiveStartSeconds < S.ActiveEndSeconds &&
        S.ActiveEndSeconds <= S.RecoveryEndSeconds && S.RecoveryEndSeconds <= M.ClipLengthSeconds))
        Fail(R, TEXT("MoveCard.Timeline"), TEXT("commit<=activeStart<activeEnd<=recoveryEnd<=clipLength"));
    if (S.Windows.IsEmpty()) Fail(R, TEXT("MoveCard.Window"), TEXT("no hit windows"));
    TSet<FName> Ids;
    double PreviousEnd = -1.0;
    for (int32 I = 0; I < S.Windows.Num(); ++I)
    {
        const FRPGBossMoveWindow& W = S.Windows[I];
        const FString Field = FString::Printf(TEXT("Windows[%d]"), I);
        if (W.WindowId.IsNone() || W.HitGroup.IsNone() || Ids.Contains(W.WindowId))
            Fail(R, TEXT("MoveCard.WindowIdentity"), Field);
        Ids.Add(W.WindowId); // repeated HitGroup is intentional: shared dedupe across windows.
        Number(R, *FString::Printf(TEXT("%s.StartSeconds"), *Field), W.StartSeconds);
        Number(R, *FString::Printf(TEXT("%s.EndSeconds"), *Field), W.EndSeconds);
        Number(R, *FString::Printf(TEXT("%s.RadiusCm"), *Field), W.RadiusCm, true);
        if (!(W.StartSeconds >= S.ActiveStartSeconds && W.StartSeconds < W.EndSeconds &&
            W.EndSeconds <= S.ActiveEndSeconds && W.StartSeconds >= PreviousEnd))
            Fail(R, TEXT("MoveCard.Window"), Field);
        PreviousEnd = W.EndSeconds;
        if (W.SocketA.IsNone() || W.SocketB.IsNone() || W.SocketA == W.SocketB ||
            !M.SocketOrBoneNames.Contains(W.SocketA) || !M.SocketOrBoneNames.Contains(W.SocketB))
            Fail(R, TEXT("MoveCard.Socket"), Field);
        if (W.BakedSamples.Num() > 0)
        {
            bool bBakedOk = W.BakedSamples.Num() >= 2;
            double PreviousTime = -1.0;
            for (const FRPGBakedBladeSample& B : W.BakedSamples)
            {
                if (!FMath::IsFinite(B.TimeSeconds) || B.TimeSeconds <= PreviousTime || B.TimeSeconds > M.ClipLengthSeconds ||
                    B.BaseCS.ContainsNaN() || B.TipCS.ContainsNaN() || B.BaseCS.GetAbsMax() > 1.e5 || B.TipCS.GetAbsMax() > 1.e5)
                { bBakedOk = false; break; }
                PreviousTime = B.TimeSeconds;
            }
            // The samples must cover the whole window (a sample at or before its start, one at or after its end).
            if (bBakedOk && (W.BakedSamples[0].TimeSeconds > W.StartSeconds || W.BakedSamples.Last().TimeSeconds < W.EndSeconds)) bBakedOk = false;
            if (!bBakedOk) Fail(R, TEXT("MoveCard.BakedSamples"), Field);
        }
    }
    return R;
}
FRPGBossMoveIssues CompileMetadata(const FRPGBossMoveCardSpec& S, const FRPGBossMoveMetadata& M,
    TSharedPtr<const FRPGCompiledBossMoveCard>& Out)
{
    Out.Reset();
    FRPGBossMoveIssues R = Validate(S, M);
    if (R.IsValid()) FCompiler::Publish(S, M, {}, Out);
    return R;
}
FRPGBossMoveIssues CompileResolved(const FRPGBossMoveCardSpec& S, USkeleton* Skeleton,
    UAnimSequenceBase* Animation, USkeletalMesh* Mesh, TSharedPtr<const FRPGCompiledBossMoveCard>& Out)
{
    Out.Reset(); FRPGBossMoveIssues R;
    if (!IsInGameThread()) { Fail(R, TEXT("MoveCard.NotGameThread"), TEXT("CompileResolved")); return R; }
    if (!IsValid(Skeleton) || !IsValid(Animation) || !IsValid(Mesh))
    { Fail(R, TEXT("MoveCard.ResolvedObject"), TEXT("skeleton/animation/mesh")); return R; }
    const bool bSequence = !S.Sequence.IsNull(), bMontage = !S.Montage.IsNull();
    if ((bSequence && !Animation->IsA<UAnimSequence>()) || (bMontage && !Animation->IsA<UAnimMontage>()))
    { Fail(R, TEXT("MoveCard.AnimationType"), TEXT("selected source type")); return R; }
    FRPGBossMoveMetadata M;
    M.AnimationPath = FSoftObjectPath(Animation);
    M.SkeletonPath = FSoftObjectPath(Skeleton);
    M.AnimationSkeletonPath = FSoftObjectPath(Animation->GetSkeleton());
    M.MeshSkeletonPath = FSoftObjectPath(Mesh->GetSkeleton());
    M.ClipLengthSeconds = Animation->GetPlayLength();
    M.bRootMotion = Animation->HasRootMotion();
    if (const UAnimMontage* Montage = Cast<UAnimMontage>(Animation))
    {
        for (const FSlotAnimationTrack& Track : Montage->SlotAnimTracks) M.Slots.Add(Track.SlotName);
        for (const FCompositeSection& Section : Montage->CompositeSections) M.Sections.Add(Section.SectionName);
    }
    else if (Skeleton->ContainsSlotName(S.SlotName)) { M.Slots.Add(S.SlotName); }
    for (const FRPGBossMoveWindow& W : S.Windows)
        for (FName Name : {W.SocketA, W.SocketB})
            if (Mesh->FindSocket(Name) || Mesh->GetRefSkeleton().FindBoneIndex(Name) != INDEX_NONE)
                M.SocketOrBoneNames.Add(Name);
    R = Validate(S, M);
    if (!R.IsValid()) return R;
    TArray<TStrongObjectPtr<UObject>> Leases;
    Leases.Emplace(Skeleton); Leases.Emplace(Animation); Leases.Emplace(Mesh);
    FCompiler::Publish(S, M, MoveTemp(Leases), Out);
    return R;
}
}
