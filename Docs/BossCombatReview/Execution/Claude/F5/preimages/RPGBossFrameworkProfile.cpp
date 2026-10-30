// Copyright One Boss Fight. All Rights Reserved.
#include "Player/RPGBossFrameworkProfile.h"
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
bool ValidateProfile(const URPGBossFrameworkProfile& P,FString& Error)
{
    Error.Reset();
    auto Fail=[&](const TCHAR* E){Error=E;return false;};
    const bool bF3=P.FixtureLabel==TEXT("F3 fixture"), bF4=P.FixtureLabel==TEXT("F4 fixture");
    if (!(bF3||bF4) || bF4!=P.bDamageEnabled || P.Mesh.IsNull() || P.AnimClass.IsNull() || P.TargetPawnClass.IsNull() || P.Card.IsNull())
        return Fail(TEXT("Framework.Profile.Identity"));
    if (P.bDamageEnabled && (!FMath::IsFinite(P.HitStepCm) || P.HitStepCm<=0.f || P.HitStepCm>1.e6f || P.HitMaxSubsteps<1 || P.HitMaxSubsteps>64))
        return Fail(TEXT("Framework.Profile.Domain"));
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
    UClass* Target=P->TargetPawnClass.LoadSynchronous(); URPGBossMoveCard* Asset=P->Card.LoadSynchronous();
    if (!IsValid(Mesh)||!IsValid(Anim)||!IsValid(Target)||!IsValid(Asset)||!Anim->IsChildOf(UAnimInstance::StaticClass())||
        !Target->IsChildOf(APawn::StaticClass())||Anim->HasAnyClassFlags(CLASS_Abstract)||Target->HasAnyClassFlags(CLASS_Abstract))
    {Error=TEXT("Framework.Profile.Dependency");return false;}
    const auto& S=Asset->Spec;
    if (!S.Montage.IsNull()||S.Sequence.IsNull()||!S.SectionName.IsNone()||S.SlotName!=TEXT("FullBody")||
        S.ActiveStartSeconds<=P->BlendInSeconds||S.RecoveryEndSeconds+P->BlendOutSeconds>1.e6f)
    {Error=TEXT("Framework.Profile.SequenceTelemetryOnly");return false;}
    // F3 cards are telemetry only; an F4 card must damage, by less than the target's health (one hit never kills the proof target).
    if (P->bDamageEnabled?!(S.HPDamage>0.f&&S.HPDamage<P->TargetHealth):S.HPDamage!=0.f)
    {Error=P->bDamageEnabled?TEXT("Framework.Profile.DamageCard"):TEXT("Framework.Profile.SequenceTelemetryOnly");return false;}
    USkeleton* Skeleton=S.Skeleton.LoadSynchronous(); UAnimSequence* Sequence=S.Sequence.LoadSynchronous();
    const auto* Generated=Cast<UAnimBlueprintGeneratedClass>(Anim);
    if(!Generated||Generated->GetTargetSkeleton()!=Skeleton) {Error=TEXT("Framework.Profile.AnimSkeleton");return false;}
    TSharedPtr<const FRPGCompiledBossMoveCard> Card;
    const auto Issues=RPGBossMoveCards::CompileResolved(S,Skeleton,Sequence,Mesh,Card);
    if (!Issues.IsValid()||!Card||!Card->HasResolvedAssets())
    {Error=Issues.Errors.IsEmpty()?TEXT("Framework.Profile.ResolvedCard"):FString::Join(Issues.Errors,TEXT(";"));return false;}
    if(P->BandMinCm<S.MinRangeCm||P->BandMaxCm>S.MaxRangeCm||S.RecoveryEndSeconds+P->BlendOutSeconds>Card->Metadata().ClipLengthSeconds)
    {Error=TEXT("Framework.Profile.CardBandOrBlendTail");return false;}
    auto D=MakeUnique<FRPGFrameworkDependencies>(); D->Profile.Reset(P); D->Mesh.Reset(Mesh); D->AnimClass.Reset(Anim); D->TargetClass.Reset(Target); D->Card=Card;
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
