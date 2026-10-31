// Copyright One Boss Fight. All Rights Reserved.
#include "Player/RPGBossFrameworkProfile.h"
#include "Player/RPGBossStaggerAnimRules.h"
#include "Animation/AnimInstance.h"
#include "Animation/AnimBlueprintGeneratedClass.h"
#include "Animation/AnimClassInterface.h"
#include "Animation/AnimSequence.h"
#include "Animation/Skeleton.h"
#include "Engine/SkeletalMesh.h"
#include "GameFramework/Pawn.h"
#include "UObject/UnrealType.h"
namespace RPGFramework
{
bool PhasePoolCannotStarve(const TArray<float>& Cooldowns,int32 AttackCount)
{
    if (AttackCount<1) return false;
    if (Cooldowns.Num()>=AttackCount) return true;
    for (float C:Cooldowns) if (FMath::IsFinite(C) && C<=0.f) return true;
    return false;
}
bool ValidateProfile(const URPGBossFrameworkProfile& P,FString& Error)
{
    Error.Reset();
    auto Fail=[&](const TCHAR* E){Error=E;return false;};
    const bool bF3=P.FixtureLabel==TEXT("F3 fixture"), bF4=P.FixtureLabel==TEXT("F4 fixture"), bF5=P.FixtureLabel==TEXT("F5 fixture");
    if (!(bF3||bF4||bF5) || (bF4||bF5)!=P.bDamageEnabled || P.Mesh.IsNull() || P.AnimClass.IsNull() || P.TargetPawnClass.IsNull() ||
        (bF5 ? (P.Cards.Num()<1||!P.Card.IsNull()) : (P.Card.IsNull()||P.Cards.Num()>0)))
        return Fail(TEXT("Framework.Profile.Identity"));
    if (P.bDamageEnabled && (!FMath::IsFinite(P.HitStepCm) || P.HitStepCm<=0.f || P.HitStepCm>1.e6f || P.HitMaxSubsteps<1 || P.HitMaxSubsteps>64))
        return Fail(TEXT("Framework.Profile.Domain"));
    if ((P.BossMaxHealth>0.f)!=(P.PlayerHitDamage>0.f) || !FMath::IsFinite(P.BossMaxHealth) || !FMath::IsFinite(P.PlayerHitDamage) || P.BossMaxHealth<0.f || P.PlayerHitDamage<0.f ||
        P.BossMaxHealth>1.e6f || P.PlayerHitDamage>P.BossMaxHealth)
        return Fail(TEXT("Framework.Profile.Domain"));
    // F6c: phases need the selector (F5), a hittable boss, a fraction strictly inside (0,1) and a named second phase; no fraction, no name.
    if (P.PhaseTwoFraction!=0.f || !P.PhaseTwoId.IsNone())
        if (!bF5 || P.BossMaxHealth<=0.f || !FMath::IsFinite(P.PhaseTwoFraction) || P.PhaseTwoFraction<=0.f || P.PhaseTwoFraction>=1.f || P.PhaseTwoId.IsNone())
            return Fail(TEXT("Framework.Profile.Phase"));
    // F8: posture needs the selector lane (F5) and a hittable boss; the five values are all zero (off) or a coherent set (token Framework.Profile.Posture).
    {
        const float Values[]={P.PostureMax,P.PlayerPostureHitAmount,P.StaggerSeconds,P.PostureRegenDelaySeconds,P.PostureRegenPerSecond};
        bool bAnyPosture=false; for (float V:Values) bAnyPosture|=(V!=0.f);
        if (bAnyPosture)
        {
            bool bOk=bF5&&P.BossMaxHealth>0.f; for (float V:Values) bOk&=(FMath::IsFinite(V)&&V>=0.f&&V<=1.e6f);
            bOk=bOk&&P.PostureMax>0.f&&P.PlayerPostureHitAmount>0.f&&P.PlayerPostureHitAmount<=P.PostureMax&&P.StaggerSeconds>=.5f&&P.StaggerSeconds<=60.f;
            if (!bOk) return Fail(TEXT("Framework.Profile.Posture"));
        }
    }
    // F11: stagger clips are all set or all empty, need posture (a stagger to play in), a slot name; the phase clip needs a second phase (assets are checked in ResolveProfile).
    {
        const bool bStart=!P.StaggerStartAnim.IsNull(), bLoop=!P.StaggerLoopAnim.IsNull(), bEnd=!P.StaggerEndAnim.IsNull(), bPhaseClip=!P.PhaseTransitionAnim.IsNull();
        if (bStart||bLoop||bEnd||bPhaseClip)
        {
            if (P.AnimSlotName.IsNone()) return Fail(TEXT("Framework.Profile.StaggerAnim.SlotNameEmpty"));
            if ((bStart||bLoop||bEnd)&&!(bStart&&bLoop&&bEnd)) return Fail(TEXT("Framework.Profile.StaggerAnim.CoherentSet"));
            if (bStart&&!(bF5&&P.PostureMax>0.f)) return Fail(TEXT("Framework.Profile.StaggerAnim.NoPosture"));
            if (bPhaseClip&&(!bF5||P.BossMaxHealth<=0.f||!(P.PhaseTwoFraction>0.f)||P.PhaseTwoId.IsNone())) return Fail(TEXT("Framework.Profile.PhaseTransitionAnim.Phaseless"));
        }
    }
    // F9: bleed needs the selector lane (F5) and a hittable boss; BleedBuildupPerHit 0 = off (the other four then 0 too), else a coherent set (token Framework.Profile.Bleed).
    {
        const float Values[]={P.BleedBuildupPerHit,P.BleedInitialThreshold,P.BleedThresholdIncrease,P.BleedThresholdMax,P.BleedHpFraction};
        bool bAnyBleed=false; for (float V:Values) bAnyBleed|=(V!=0.f);
        if (bAnyBleed)
        {
            bool bOk=bF5&&P.BossMaxHealth>0.f; for (float V:Values) bOk&=(FMath::IsFinite(V)&&V>=0.f&&V<=1.e6f);
            bOk=bOk&&P.BleedBuildupPerHit>0.f&&P.BleedInitialThreshold>=1.f&&P.BleedThresholdMax>=P.BleedInitialThreshold&&P.BleedHpFraction>0.f&&P.BleedHpFraction<=1.f;
            if (!bOk) return Fail(TEXT("Framework.Profile.Bleed"));
        }
    }
    if (bF5)
    {
        if (!FMath::IsFinite(P.RepeatPenalty) || P.RepeatPenalty<=0.f || P.RepeatPenalty>1.f || P.RepeatMemory<1 || P.RepeatMemory>8 || P.AttackCount<1 || P.AttackCount>8)
            return Fail(TEXT("Framework.Profile.Domain"));
        for (const FRPGBossProfileCard& C:P.Cards)
            if (C.Card.IsNull() || !FMath::IsFinite(C.CooldownSeconds) || C.CooldownSeconds<0.f || C.CooldownSeconds>1.e6f || !FMath::IsFinite(C.Weight) || C.Weight<=0.f || C.Weight>1.e6f)
                return Fail(TEXT("Framework.Profile.Domain"));
    }
    for (double V:{double(P.BandMinCm),double(P.BandMaxCm),double(P.WalkSpeedCmPerSecond),double(P.AcceptanceCm),double(P.WalkTimeoutSeconds),double(P.BlendInSeconds),double(P.BlendOutSeconds),double(P.CapsuleRadiusCm),double(P.CapsuleHalfHeightCm),double(P.TargetHealth)})
        if (!FMath::IsFinite(V) || V<=0.0 || V>1.e6) return Fail(TEXT("Framework.Profile.Domain"));
    if (!(P.BandMinCm<P.BandMaxCm && P.AcceptanceCm<(P.BandMaxCm-P.BandMinCm)*.5f && P.CapsuleRadiusCm<=P.CapsuleHalfHeightCm))
        return Fail(TEXT("Framework.Profile.Geometry"));
    if (!P.bAlignmentAuthored || P.MeshRelativeTransform.ContainsNaN() || !P.MeshRelativeTransform.IsValid() ||
        P.MeshRelativeTransform.GetScale3D().GetMin()<=0.f || P.MeshRelativeTransform.GetScale3D().GetAbsMax()>1.e6f || P.MeshRelativeTransform.GetTranslation().GetAbsMax()>1.e6f)
        return Fail(TEXT("Framework.Profile.Alignment"));
    return true;
}
bool ResolveProfile(URPGBossFrameworkProfile* P,TUniquePtr<FRPGFrameworkDependencies>& Out,FString& Error)
{
    Out.Reset(); Error.Reset();
    if (!IsInGameThread() || !IsValid(P)) {Error=TEXT("Framework.Profile.ObjectOrThread");return false;}
    if (!ValidateProfile(*P,Error)) return false;
    USkeletalMesh* Mesh=P->Mesh.LoadSynchronous(); UClass* Anim=P->AnimClass.LoadSynchronous();
    UClass* Target=P->TargetPawnClass.LoadSynchronous();
    if (!IsValid(Mesh)||!IsValid(Anim)||!IsValid(Target)||!Anim->IsChildOf(UAnimInstance::StaticClass())||
        !Target->IsChildOf(APawn::StaticClass())||Anim->HasAnyClassFlags(CLASS_Abstract)||Target->HasAnyClassFlags(CLASS_Abstract))
    {Error=TEXT("Framework.Profile.Dependency");return false;}
    // One card through every resolved-asset check; the same rules for the single F3/F4 card and each F5 candidate.
    auto ResolveCard=[&](URPGBossMoveCard* Asset,TSharedPtr<const FRPGCompiledBossMoveCard>& OutCard)->bool
    {
        if (!IsValid(Asset)) {Error=TEXT("Framework.Profile.Dependency");return false;}
        const auto& S=Asset->Spec;
        if (!S.Montage.IsNull()||S.Sequence.IsNull()||!S.SectionName.IsNone()||S.SlotName!=TEXT("FullBody")||
            S.ActiveStartSeconds<=P->BlendInSeconds||S.RecoveryEndSeconds+P->BlendOutSeconds>1.e6f)
        {Error=TEXT("Framework.Profile.SequenceTelemetryOnly");return false;}
        // F3 cards are telemetry only; an F4/F5 card must damage, by less than the target's health (one hit never kills the proof target).
        if (P->bDamageEnabled?!(S.HPDamage>0.f&&S.HPDamage<P->TargetHealth):S.HPDamage!=0.f)
        {Error=P->bDamageEnabled?TEXT("Framework.Profile.DamageCard"):TEXT("Framework.Profile.SequenceTelemetryOnly");return false;}
        USkeleton* Skeleton=S.Skeleton.LoadSynchronous(); UAnimSequence* Sequence=S.Sequence.LoadSynchronous();
        const auto* Generated=Cast<UAnimBlueprintGeneratedClass>(Anim);
        if(!Generated||Generated->GetTargetSkeleton()!=Skeleton) {Error=TEXT("Framework.Profile.AnimSkeleton");return false;}
        const auto Issues=RPGBossMoveCards::CompileResolved(S,Skeleton,Sequence,Mesh,OutCard);
        if (!Issues.IsValid()||!OutCard||!OutCard->HasResolvedAssets())
        {Error=Issues.Errors.IsEmpty()?TEXT("Framework.Profile.ResolvedCard"):FString::Join(Issues.Errors,TEXT(";"));return false;}
        if(P->BandMinCm<S.MinRangeCm||P->BandMaxCm>S.MaxRangeCm||S.RecoveryEndSeconds+P->BlendOutSeconds>OutCard->Metadata().ClipLengthSeconds)
        {Error=TEXT("Framework.Profile.CardBandOrBlendTail");return false;}
        return true;
    };
    auto D=MakeUnique<FRPGFrameworkDependencies>(); D->Profile.Reset(P); D->Mesh.Reset(Mesh); D->AnimClass.Reset(Anim); D->TargetClass.Reset(Target);
    if (P->Cards.Num()>0)
    {
        float WorstHit=0.f;
        for (const FRPGBossProfileCard& C:P->Cards)
        {
            FRPGFrameworkDependencies::FCandidate Candidate; Candidate.CooldownSeconds=C.CooldownSeconds; Candidate.Weight=C.Weight;
            if (!ResolveCard(C.Card.LoadSynchronous(),Candidate.Card)) return false;
            WorstHit=FMath::Max(WorstHit,Candidate.Card->Spec().HPDamage); D->Candidates.Add(Candidate);
        }
        // F6c: every card belongs to phase one (the first card's phase) or to PhaseTwoId, and each phase has at least one card.
        if (P->PhaseTwoFraction>0.f)
        {
            const FName One=D->Candidates[0].Card->Spec().PhaseId; int32 InOne=0,InTwo=0;
            for (const auto& C:D->Candidates){const FName Id=C.Card->Spec().PhaseId; if (Id==One) ++InOne; else if (Id==P->PhaseTwoId) ++InTwo; else {Error=TEXT("Framework.Profile.PhaseCards");return false;}}
            if (One==P->PhaseTwoId||InOne<1||InTwo<1) {Error=TEXT("Framework.Profile.PhaseCards");return false;}
            // KI-149: each phase pool must be able to offer a card on every attack (up to AttackCount of them can fall in one phase).
            TArray<float> PoolOne,PoolTwo; for (const auto& C:D->Candidates) (C.Card->Spec().PhaseId==One?PoolOne:PoolTwo).Add(C.CooldownSeconds);
            if (!PhasePoolCannotStarve(PoolOne,P->AttackCount)||!PhasePoolCannotStarve(PoolTwo,P->AttackCount)) {Error=TEXT("Framework.Profile.PhaseCooldownStarvation");return false;}
        }
        // The proof target must survive every attack of the run at the worst card damage.
        if (WorstHit*P->AttackCount>=P->TargetHealth) {Error=TEXT("Framework.Profile.DamageBudget");return false;}
    }
    else if (!ResolveCard(P->Card.LoadSynchronous(),D->Card)) return false;
    // F11: load the optional clips here (the explicit load boundary), check skeleton and lengths with the pure rules.
    if (!P->StaggerStartAnim.IsNull()||!P->StaggerLoopAnim.IsNull()||!P->StaggerEndAnim.IsNull()||!P->PhaseTransitionAnim.IsNull())
    {
        const auto* Generated=Cast<UAnimBlueprintGeneratedClass>(Anim);
        if (!Generated||!Generated->GetTargetSkeleton()) {Error=TEXT("Framework.Profile.AnimSkeleton");return false;}
        const FString BossSkeleton=Generated->GetTargetSkeleton()->GetPathName();
        auto LoadClip=[&](const TSoftObjectPtr<UAnimSequence>& Soft,TStrongObjectPtr<UAnimSequence>& Dest,const TCHAR* Token,float& Length,FString& SkeletonPath)->bool
        {
            Length=0.f; SkeletonPath.Reset(); if (Soft.IsNull()) return true;
            UAnimSequence* Clip=Soft.LoadSynchronous();
            if (!IsValid(Clip)||!IsValid(Clip->GetSkeleton())) {Error=Token;return false;}
            Dest.Reset(Clip); Length=Clip->GetPlayLength(); SkeletonPath=Clip->GetSkeleton()->GetPathName(); return true;
        };
        RPGStaggerAnim::FPureParams Params; Params.BossSkeleton=BossSkeleton; Params.Slot=P->AnimSlotName; Params.Total=P->StaggerSeconds;
        Params.bStart=!P->StaggerStartAnim.IsNull(); Params.bLoop=!P->StaggerLoopAnim.IsNull(); Params.bEnd=!P->StaggerEndAnim.IsNull();
        if (!LoadClip(P->StaggerStartAnim,D->StaggerStart,TEXT("Framework.Profile.StaggerAnim.StartLoad"),Params.StartLen,Params.StartSkeleton)||
            !LoadClip(P->StaggerLoopAnim,D->StaggerLoop,TEXT("Framework.Profile.StaggerAnim.LoopLoad"),Params.LoopLen,Params.LoopSkeleton)||
            !LoadClip(P->StaggerEndAnim,D->StaggerEnd,TEXT("Framework.Profile.StaggerAnim.EndLoad"),Params.EndLen,Params.EndSkeleton)) return false;
        const FString Failure=RPGStaggerAnim::Validate(Params);
        if (!Failure.IsEmpty()) {Error=Failure;return false;}
        float PhaseLen=0.f; FString PhaseSkeleton;
        if (!LoadClip(P->PhaseTransitionAnim,D->PhaseTransition,TEXT("Framework.Profile.PhaseTransitionAnim.Load"),PhaseLen,PhaseSkeleton)) return false;
        const FString PhaseFailure=RPGStaggerAnim::ValidatePhaseClip(!P->PhaseTransitionAnim.IsNull(),P->PhaseTwoFraction,P->PhaseTwoId,P->AnimSlotName,BossSkeleton,PhaseSkeleton);
        if (!PhaseFailure.IsEmpty()) {Error=PhaseFailure;return false;}
    }
    Out=MoveTemp(D);return true;
}
bool HasSlotNode(UAnimInstance* Instance,FName Slot)
{
    if (!IsValid(Instance)||Slot.IsNone()||!IsInGameThread()) return false;
    const IAnimClassInterface* Interface=IAnimClassInterface::GetFromClass(Instance->GetClass());
    if (!Interface) return false;
    // Read-only compiled graph introspection, exact reflected struct and typed FName property. No adapter writes or guessed function calls.
    for (const FStructProperty* P:Interface->GetAnimNodeProperties())
    {
        if (!P||!P->Struct||P->Struct->GetPathName()!=TEXT("/Script/AnimGraphRuntime.AnimNode_Slot")) continue;
        const FNameProperty* Name=FindFProperty<FNameProperty>(P->Struct,TEXT("SlotName"));
        if (Name && Name->GetPropertyValue_InContainer(P->ContainerPtrToValuePtr<void>(Instance))==Slot) return true;
    }
    return false;
}
}
