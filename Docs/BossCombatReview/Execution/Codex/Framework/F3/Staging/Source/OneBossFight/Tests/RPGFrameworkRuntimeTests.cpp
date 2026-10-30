// Copyright One Boss Fight. All Rights Reserved.
#include "Player/RPGBossFrameworkProfile.h"
#include "Boss/RPGFrameworkMoveExecutor.h"
#include "Animation/AnimInstance.h"
#include "Animation/AnimSequence.h"
#include "Animation/Skeleton.h"
#include "Engine/SkeletalMesh.h"
#include "GameFramework/Pawn.h"
#include "Misc/AutomationTest.h"
#include <limits>
#if WITH_DEV_AUTOMATION_TESTS
namespace FrameworkRuntimeFixture
{
void Fill(URPGBossFrameworkProfile& P)
{
    P.FixtureLabel=TEXT("F3 fixture");P.Mesh=TSoftObjectPtr<USkeletalMesh>(FSoftObjectPath(TEXT("/Game/ParagonSevarog/Characters/Heroes/Sevarog/Meshes/Sevarog.Sevarog")));
    P.AnimClass=TSoftClassPtr<UAnimInstance>(FSoftObjectPath(TEXT("/Game/ParagonSevarog/Characters/Heroes/Sevarog/Sevarog_AnimBlueprint.Sevarog_AnimBlueprint_C")));
    P.TargetPawnClass=TSoftClassPtr<APawn>(FSoftObjectPath(TEXT("/Game/AdvancedARPGCombat/MeleeCombatSystem/Blueprints/BP_CombatPlayerCharacter.BP_CombatPlayerCharacter_C")));
    P.BandMinCm=250.f;P.BandMaxCm=350.f;P.WalkSpeedCmPerSecond=180.f;P.AcceptanceCm=5.f;P.WalkTimeoutSeconds=10.f;
    P.BlendInSeconds=P.BlendOutSeconds=.1f;P.CapsuleRadiusCm=40.f;P.CapsuleHalfHeightCm=100.f;P.bAlignmentAuthored=true;
    // Capsule/alignment here are synthetic validation controls, NOT approved visible Sevarog dimensions.
    P.Card=TSoftObjectPtr<URPGBossMoveCard>(FSoftObjectPath(TEXT("/Game/OneBossFight/FrameworkProof/DA_Sevarog_SwingProof.DA_Sevarog_SwingProof")));
}
URPGBossMoveCard* Card()
{
    auto* A=NewObject<URPGBossMoveCard>();auto& S=A->Spec;S.Schema=1;S.MoveId=TEXT("F3Swing");S.FamilyId=TEXT("F3Telemetry");S.PhaseId=TEXT("F3Phase");
    S.Skeleton=TSoftObjectPtr<USkeleton>(FSoftObjectPath(TEXT("/Game/ParagonSevarog/Characters/Heroes/Sevarog/Meshes/Sevarog_Skeleton.Sevarog_Skeleton")));
    S.Sequence=TSoftObjectPtr<UAnimSequence>(FSoftObjectPath(TEXT("/Game/ParagonSevarog/Characters/Heroes/Sevarog/Animations/Swing1_Slow.Swing1_Slow")));
    S.SlotName=TEXT("FullBody");S.PlayRate=1.f;S.CommitSeconds=.35f;S.ActiveStartSeconds=.65f;S.ActiveEndSeconds=1.05f;S.RecoveryEndSeconds=1.5f;
    S.MinRangeCm=250.f;S.MaxRangeCm=350.f;S.FrontConeDegrees=120.f;S.TrackDegreesPerSecond=90.f;S.HPDamage=0.f;
    FRPGBossMoveWindow W;W.WindowId=TEXT("Telemetry");W.HitGroup=TEXT("NoDamage");W.StartSeconds=.65f;W.EndSeconds=1.05f;W.SocketA=TEXT("weapon_r");W.SocketB=TEXT("root_weapon_end_r");W.RadiusCm=8.f;S.Windows.Add(W);return A;
}
}
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FFrameworkProfileDomains,"OneBossFight.Framework.Runtime.ProfileDomains",EAutomationTestFlags::EditorContext|EAutomationTestFlags::ProductFilter)
bool FFrameworkProfileDomains::RunTest(const FString&)
{
    using namespace FrameworkRuntimeFixture;
    TStrongObjectPtr<URPGBossFrameworkProfile> P(NewObject<URPGBossFrameworkProfile>());FString Error;Fill(*P);
    TestTrue(TEXT("explicit profile control valid"),RPGFramework::ValidateProfile(*P,Error));
    using Field=float URPGBossFrameworkProfile::*;
    const Field Fields[]={&URPGBossFrameworkProfile::BandMinCm,&URPGBossFrameworkProfile::BandMaxCm,&URPGBossFrameworkProfile::WalkSpeedCmPerSecond,&URPGBossFrameworkProfile::AcceptanceCm,&URPGBossFrameworkProfile::WalkTimeoutSeconds,&URPGBossFrameworkProfile::BlendInSeconds,&URPGBossFrameworkProfile::BlendOutSeconds,&URPGBossFrameworkProfile::CapsuleRadiusCm,&URPGBossFrameworkProfile::CapsuleHalfHeightCm};
    for(Field F:Fields)for(float V:{0.f,-1.f,1000001.f,std::numeric_limits<float>::infinity(),std::numeric_limits<float>::quiet_NaN()})
    {Fill(*P);P.Get()->*F=V;TestFalse(TEXT("all positive fields fail closed"),RPGFramework::ValidateProfile(*P,Error));}
    Fill(*P);P->bAlignmentAuthored=false;TestFalse(TEXT("alignment not guessed"),RPGFramework::ValidateProfile(*P,Error));
    Fill(*P);P->BandMinCm=P->BandMaxCm;TestFalse(TEXT("strict band order"),RPGFramework::ValidateProfile(*P,Error));
    Fill(*P);P->AcceptanceCm=50.f;TestFalse(TEXT("arrival tolerance must fit band"),RPGFramework::ValidateProfile(*P,Error));
    Fill(*P);P->AnimClass.Reset();TestFalse(TEXT("required animation class"),RPGFramework::ValidateProfile(*P,Error));
    return true;
}
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FFrameworkResolvedDependencies,"OneBossFight.Framework.Runtime.ResolvedDependencies",EAutomationTestFlags::EditorContext|EAutomationTestFlags::ProductFilter)
bool FFrameworkResolvedDependencies::RunTest(const FString&)
{
    using namespace FrameworkRuntimeFixture;
    TStrongObjectPtr<URPGBossMoveCard> A(Card());TStrongObjectPtr<URPGBossFrameworkProfile> P(NewObject<URPGBossFrameworkProfile>());Fill(*P);P->Card=A.Get();
    TUniquePtr<FRPGFrameworkDependencies> D;FString Error;
    TestTrue(TEXT("real existing sequence/mesh/class dependencies"),RPGFramework::ResolveProfile(P.Get(),D,Error));
    if(!D){AddError(Error);return false;}
    TestTrue(TEXT("positive resolved capability"),D->Card&&D->Card->HasResolvedAssets());TestEqual(TEXT("telemetry HP remains zero"),D->Card->Spec().HPDamage,0.f);
    TestTrue(TEXT("static playback gate accepts resolved card"),URPGFrameworkMoveExecutor::ValidatePlaybackCard(D->Card,Error));
    const auto Source=A->Spec;A->Spec.HPDamage=1.f;
    TestFalse(TEXT("telemetry lane refuses damage card"),RPGFramework::ResolveProfile(P.Get(),D,Error));TestFalse(TEXT("stale resolved output cleared"),D.IsValid());A->Spec=Source;
    TestFalse(TEXT("missing profile clears output"),RPGFramework::ResolveProfile(nullptr,D,Error));TestFalse(TEXT("no publication on failure"),D.IsValid());
    return true;
}
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FFrameworkPlaybackGuards,"OneBossFight.Framework.Runtime.PlaybackGuards",EAutomationTestFlags::EditorContext|EAutomationTestFlags::ProductFilter)
bool FFrameworkPlaybackGuards::RunTest(const FString&)
{
    using namespace FrameworkRuntimeFixture;TStrongObjectPtr<URPGBossMoveCard> A(Card());
    FRPGBossMoveMetadata M;M.AnimationPath=A->Spec.Sequence.ToSoftObjectPath();M.SkeletonPath=A->Spec.Skeleton.ToSoftObjectPath();M.AnimationSkeletonPath=M.MeshSkeletonPath=M.SkeletonPath;
    M.ClipLengthSeconds=1.7;M.Slots.Add(TEXT("FullBody"));M.SocketOrBoneNames.Add(TEXT("weapon_r"));M.SocketOrBoneNames.Add(TEXT("root_weapon_end_r"));
    TSharedPtr<const FRPGCompiledBossMoveCard> Preview;TestTrue(TEXT("valid pure metadata preview"),RPGBossMoveCards::CompileMetadata(A->Spec,M,Preview).IsValid());
    FString Error;TestFalse(TEXT("runtime MUST reject preview"),URPGFrameworkMoveExecutor::ValidatePlaybackCard(Preview,Error));TestEqual(TEXT("preview refusal token"),Error,FString(TEXT("Framework.Playback.UnresolvedPreview")));
    TStrongObjectPtr<URPGFrameworkMoveExecutor> E(NewObject<URPGFrameworkMoveExecutor>());FRPGFrameworkDependencies D;D.Card=Preview;
    TestFalse(TEXT("no owner target fallback or playback"),E->Initialize(nullptr,D,nullptr,1,1,Error));TestTrue(TEXT("rejected initialization stays clean"),E->IsClean());
    E->Abort(TEXT("isolated refusal cleanup"));E->Abort(TEXT("isolated repeat cleanup"));TestTrue(TEXT("repeat cleanup idempotent"),E->IsClean());
    TestFalse(TEXT("no fake positive slot graph"),RPGFramework::HasSlotNode(nullptr,TEXT("FullBody")));return true;
}
#endif
