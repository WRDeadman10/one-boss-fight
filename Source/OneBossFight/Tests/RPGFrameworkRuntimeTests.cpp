// Copyright One Boss Fight. All Rights Reserved.
#include "Player/RPGBossFrameworkProfile.h"
#include "Player/RPGDamageResolver.h"
#include "Player/RPGBossSweepSampling.h"
#include "Player/RPGBossStaggerAnimRules.h"
#include "Player/RPGBossTrackRules.h"
#include "Player/RPGBossPunishRules.h"
#include "Player/RPGBossStrafeRules.h"
#include "Player/RPGBossRules.h"
#include "Player/RPGBossOverlayRules.h"
#include "Boss/RPGFrameworkMoveExecutor.h"
#include "Boss/RPGFrameworkBossCharacter.h"
#include "Boss/RPGBossNavigationDiagnostics.h"
#include "Animation/AnimInstance.h"
#include "Animation/AnimSequence.h"
#include "Animation/Skeleton.h"
#include "Engine/SkeletalMesh.h"
#include "GameFramework/Pawn.h"
#include "Misc/AutomationTest.h"
#include <cmath>
#include <limits>
#if WITH_DEV_AUTOMATION_TESTS
namespace FrameworkRuntimeFixture
{
void Fill(URPGBossFrameworkProfile& P)
{
    P.bAggroEnabled=false;P.bAlignmentAuthored=false;P.bArenaCenterAuthored=false;P.bArenaLeash=false;
    P.bDamageEnabled=false;P.bPhaseSupersedesStagger=false;P.bRangeBandPartition=false;P.MaxAbortedAttacks=0;
    P.HitStepCm=0.f;P.HitMaxSubsteps=0;P.BossMaxHealth=0.f;P.PlayerHitDamage=0.f;
    P.FixtureLabel=TEXT("F3 fixture");P.Mesh=TSoftObjectPtr<USkeletalMesh>(FSoftObjectPath(TEXT("/Game/ParagonSevarog/Characters/Heroes/Sevarog/Meshes/Sevarog.Sevarog")));
    P.AnimClass=TSoftClassPtr<UAnimInstance>(FSoftObjectPath(TEXT("/Game/ParagonSevarog/Characters/Heroes/Sevarog/Sevarog_AnimBlueprint.Sevarog_AnimBlueprint_C")));
    P.TargetPawnClass=TSoftClassPtr<APawn>(FSoftObjectPath(TEXT("/Game/AdvancedARPGCombat/MeleeCombatSystem/Blueprints/BP_CombatPlayerCharacter.BP_CombatPlayerCharacter_C")));
    P.BandMinCm=250.f;P.BandMaxCm=350.f;P.WalkSpeedCmPerSecond=180.f;P.AcceptanceCm=5.f;P.WalkTimeoutSeconds=10.f;
    P.BlendInSeconds=P.BlendOutSeconds=.1f;P.CapsuleRadiusCm=40.f;P.CapsuleHalfHeightCm=100.f;P.TargetHealth=800.f;P.bAlignmentAuthored=true;
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
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FFrameworkLiveTestBridgeNullProfile,"OneBossFight.Framework.Runtime.LiveTestBridgeNullProfile",EAutomationTestFlags::EditorContext|EAutomationTestFlags::ProductFilter)
bool FFrameworkLiveTestBridgeNullProfile::RunTest(const FString&)
{
    FString Error;
#if UE_BUILD_SHIPPING
    TestFalse(TEXT("shipping bridge initialization is a no-op"),ARPGFrameworkBossCharacter::StaticClass()->GetDefaultObject<ARPGFrameworkBossCharacter>()->InitializeWithProfileForTest(nullptr,nullptr,Error));
#else
    const bool bInitialized=ARPGFrameworkBossCharacter::StaticClass()->GetDefaultObject<ARPGFrameworkBossCharacter>()->InitializeWithProfileForTest(nullptr,nullptr,Error);
    TestFalse(TEXT("null profile is refused"),bInitialized);
    TestEqual(TEXT("null profile refusal is explicit"),Error,FString(TEXT("Framework.Boss.Profile")));
#endif
    return true;
}
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FFrameworkLiveTestBridgeSpawnRejectsInvalidInputs,"OneBossFight.Framework.Runtime.LiveTestBridgeSpawnRejectsInvalidInputs",EAutomationTestFlags::EditorContext|EAutomationTestFlags::ProductFilter)
bool FFrameworkLiveTestBridgeSpawnRejectsInvalidInputs::RunTest(const FString&)
{
#if UE_BUILD_SHIPPING
    TestNull(TEXT("shipping spawn bridge is a no-op"),ARPGFrameworkBossCharacter::SpawnFrameworkBossForTest(nullptr,ARPGFrameworkBossCharacter::StaticClass(),FVector::ZeroVector,FRotator::ZeroRotator));
#else
    TestNull(TEXT("null world is refused"),ARPGFrameworkBossCharacter::SpawnFrameworkBossForTest(nullptr,ARPGFrameworkBossCharacter::StaticClass(),FVector::ZeroVector,FRotator::ZeroRotator));
    TestNull(TEXT("null class is refused"),ARPGFrameworkBossCharacter::SpawnFrameworkBossForTest(nullptr,TSubclassOf<ARPGFrameworkBossCharacter>(),FVector::ZeroVector,FRotator::ZeroRotator));
#endif
    return true;
}
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FFrameworkProfileDomains,"OneBossFight.Framework.Runtime.ProfileDomains",EAutomationTestFlags::EditorContext|EAutomationTestFlags::ProductFilter)
bool FFrameworkProfileDomains::RunTest(const FString&)
{
    using namespace FrameworkRuntimeFixture;
    TStrongObjectPtr<URPGBossFrameworkProfile> P(NewObject<URPGBossFrameworkProfile>());FString Error;Fill(*P);
    TestTrue(TEXT("explicit profile control valid"),RPGFramework::ValidateProfile(*P,Error));
    using Field=float URPGBossFrameworkProfile::*;
    const Field Fields[]={&URPGBossFrameworkProfile::BandMinCm,&URPGBossFrameworkProfile::BandMaxCm,&URPGBossFrameworkProfile::WalkSpeedCmPerSecond,&URPGBossFrameworkProfile::AcceptanceCm,&URPGBossFrameworkProfile::WalkTimeoutSeconds,&URPGBossFrameworkProfile::BlendInSeconds,&URPGBossFrameworkProfile::BlendOutSeconds,&URPGBossFrameworkProfile::CapsuleRadiusCm,&URPGBossFrameworkProfile::CapsuleHalfHeightCm,&URPGBossFrameworkProfile::TargetHealth};
    for(Field F:Fields)for(float V:{0.f,-1.f,1000001.f,std::numeric_limits<float>::infinity(),std::numeric_limits<float>::quiet_NaN()})
    {Fill(*P);P.Get()->*F=V;TestFalse(TEXT("all positive fields fail closed"),RPGFramework::ValidateProfile(*P,Error));}
    Fill(*P);P->bAlignmentAuthored=false;TestFalse(TEXT("alignment not guessed"),RPGFramework::ValidateProfile(*P,Error));
    Fill(*P);P->MaxAbortedAttacks=0;TestTrue(TEXT("BQ-01 default abort budget keeps the control valid"),RPGFramework::ValidateProfile(*P,Error));
    Fill(*P);P->MaxAbortedAttacks=1;TestFalse(TEXT("BQ-01 abort budget needs the F5 fixture and attacks"),RPGFramework::ValidateProfile(*P,Error));
    Fill(*P);P->MaxAbortedAttacks=-1;TestFalse(TEXT("BQ-01 negative abort budget fails closed"),RPGFramework::ValidateProfile(*P,Error));
    Fill(*P);P->BandMinCm=P->BandMaxCm;TestFalse(TEXT("strict band order"),RPGFramework::ValidateProfile(*P,Error));
    Fill(*P);P->AcceptanceCm=50.f;TestFalse(TEXT("arrival tolerance must fit band"),RPGFramework::ValidateProfile(*P,Error));
    Fill(*P);P->AnimClass.Reset();TestFalse(TEXT("required animation class"),RPGFramework::ValidateProfile(*P,Error));
    Fill(*P);P->bRangeBandPartition=true;TestFalse(TEXT("range partition requires F5"),RPGFramework::ValidateProfile(*P,Error));TestEqual(TEXT("range partition lane token"),Error,FString(TEXT("Framework.Profile.Domain")));
    Fill(*P);P->FixtureLabel=TEXT("F4 fixture");P->bDamageEnabled=true;P->HitStepCm=15.f;P->HitMaxSubsteps=8;P->BossMaxHealth=1000.f;P->PlayerHitDamage=100.f;
    const bool bF4ControlValid=RPGFramework::ValidateProfile(*P,Error);
    TestTrue(FString::Printf(TEXT("F4 control profile valid with range partition off: %s"),*Error),bF4ControlValid);
    P->bRangeBandPartition=true;TestFalse(TEXT("range partition is refused in F4"),RPGFramework::ValidateProfile(*P,Error));TestEqual(TEXT("F4 lane token"),Error,FString(TEXT("Framework.Profile.Domain")));
    return true;
}
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FFrameworkProfileValidationFuzz,"OneBossFight.Framework.Runtime.ProfileValidationFuzz",EAutomationTestFlags::EditorContext|EAutomationTestFlags::ProductFilter)
bool FFrameworkProfileValidationFuzz::RunTest(const FString&)
{
    using namespace FrameworkRuntimeFixture;
    TStrongObjectPtr<URPGBossFrameworkProfile> P(NewObject<URPGBossFrameworkProfile>());
    using Field=float URPGBossFrameworkProfile::*;
    const Field Fields[]={&URPGBossFrameworkProfile::BandMinCm,&URPGBossFrameworkProfile::BandMaxCm,&URPGBossFrameworkProfile::WalkSpeedCmPerSecond,&URPGBossFrameworkProfile::AcceptanceCm,&URPGBossFrameworkProfile::WalkTimeoutSeconds,&URPGBossFrameworkProfile::TargetHealth,&URPGBossFrameworkProfile::ArenaRadiusCm,&URPGBossFrameworkProfile::GuardChipFraction,&URPGBossFrameworkProfile::ParryRecoveryScale,&URPGBossFrameworkProfile::SelectorTieBand};
    FRandomStream Random(0x91A11);int32 Valid=0,Rejected=0;
    {Fill(*P);FString Baseline;if(RPGFramework::ValidateProfile(*P,Baseline))++Valid;} // the unmodified fixture is valid: single-field fuzz alone rarely stays valid
    for(int32 I=0;I<2000;++I)
    {
        Fill(*P);const Field Pick=Fields[Random.RandRange(0,static_cast<int32>(UE_ARRAY_COUNT(Fields))-1)];
        const int32 Kind=Random.RandRange(0,5);
        P.Get()->*Pick=Kind==0?std::numeric_limits<float>::quiet_NaN():Kind==1?std::numeric_limits<float>::infinity():Kind==2?-1.e6f:Kind==3?1.e6f:Random.FRandRange(0.f,10000.f);
        FString Error;const bool bOk=RPGFramework::ValidateProfile(*P,Error);
        if(bOk){++Valid;TestTrue(TEXT("accepted profile has no stale error"),Error.IsEmpty());}
        else{++Rejected;TestTrue(*FString::Printf(TEXT("rejected profile %d returns a named token"),I),Error.StartsWith(TEXT("Framework.Profile.")));}
    }
    TestTrue(TEXT("fuzz covers both accepted and rejected values"),Valid>0&&Rejected>0);
    return true;
}
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FFrameworkProfileInstancesAreIndependent,"OneBossFight.Framework.Runtime.ProfileInstanceIsolation",EAutomationTestFlags::EditorContext|EAutomationTestFlags::ProductFilter)
bool FFrameworkProfileInstancesAreIndependent::RunTest(const FString&)
{
    TStrongObjectPtr<URPGBossFrameworkProfile> A(NewObject<URPGBossFrameworkProfile>()),B(NewObject<URPGBossFrameworkProfile>());
    TestNotNull(TEXT("first profile allocated"),A.Get());TestNotNull(TEXT("second profile allocated"),B.Get());
    if(!A.IsValid()||!B.IsValid())return false;
    A->ArenaCenterBias=.75f;A->SelectorTieBand=.2f;A->Cards.Reset();
    TestEqual(TEXT("second profile keeps default center bias"),B->ArenaCenterBias,0.f);
    TestEqual(TEXT("second profile keeps default selector tie"),B->SelectorTieBand,0.f);
    TestTrue(TEXT("second profile's default card list remains empty"),B->Cards.IsEmpty());
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
    A->Spec.HPDamage=17.f;Fill(*P);P->FixtureLabel=TEXT("F5 fixture");P->bDamageEnabled=true;P->HitStepCm=15.f;P->HitMaxSubsteps=8;P->RepeatPenalty=.2f;P->RepeatMemory=2;P->AttackCount=2;
    P->Card.Reset();P->Cards.Reset();for(int32 Index=0;Index<2;++Index){FRPGBossProfileCard Candidate;Candidate.Card=A.Get();Candidate.CooldownSeconds=1.f;Candidate.Weight=1.f;P->Cards.Add(Candidate);}
    TestFalse(TEXT("duplicate resolved card MoveIds are refused"),RPGFramework::ResolveProfile(P.Get(),D,Error));
    TestEqual(TEXT("duplicate MoveId has a named profile token"),Error,FString(TEXT("Framework.Profile.Combo.DuplicateMoveId")));
    TestFalse(TEXT("duplicate profile publishes no resolved output"),D.IsValid());
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
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FFrameworkDamageProfile,"OneBossFight.Framework.Runtime.DamageProfile",EAutomationTestFlags::EditorContext|EAutomationTestFlags::ProductFilter)
bool FFrameworkDamageProfile::RunTest(const FString&)
{
    using namespace FrameworkRuntimeFixture;
    TStrongObjectPtr<URPGBossFrameworkProfile> P(NewObject<URPGBossFrameworkProfile>());FString Error;
    auto F4=[&P](){Fill(*P);P->FixtureLabel=TEXT("F4 fixture");P->bDamageEnabled=true;P->HitStepCm=15.f;P->HitMaxSubsteps=8;};
    F4();TestTrue(TEXT("explicit F4 profile valid"),RPGFramework::ValidateProfile(*P,Error));
    for(float V:{0.f,-1.f,1000001.f,std::numeric_limits<float>::infinity(),std::numeric_limits<float>::quiet_NaN()}){F4();P->HitStepCm=V;TestFalse(TEXT("step domain"),RPGFramework::ValidateProfile(*P,Error));}
    for(int32 V:{0,-1,65}){F4();P->HitMaxSubsteps=V;TestFalse(TEXT("substep cap domain"),RPGFramework::ValidateProfile(*P,Error));}
    F4();P->bDamageEnabled=false;TestFalse(TEXT("F4 label needs the damage flag"),RPGFramework::ValidateProfile(*P,Error));
    Fill(*P);P->bDamageEnabled=true;TestFalse(TEXT("F3 label cannot carry the damage flag"),RPGFramework::ValidateProfile(*P,Error));
    Fill(*P);P->FixtureLabel=TEXT("F5 fixture");TestFalse(TEXT("unknown label"),RPGFramework::ValidateProfile(*P,Error));
    TSharedPtr<const FRPGCompiledBossMoveCard> Preview;
    TStrongObjectPtr<URPGBossMoveCard> A(Card());A->Spec.HPDamage=35.f;
    FRPGBossMoveMetadata M;M.AnimationPath=A->Spec.Sequence.ToSoftObjectPath();M.SkeletonPath=A->Spec.Skeleton.ToSoftObjectPath();M.AnimationSkeletonPath=M.MeshSkeletonPath=M.SkeletonPath;
    M.ClipLengthSeconds=1.7;M.Slots.Add(TEXT("FullBody"));M.SocketOrBoneNames.Add(TEXT("weapon_r"));M.SocketOrBoneNames.Add(TEXT("root_weapon_end_r"));
    TestTrue(TEXT("damage card metadata preview"),RPGBossMoveCards::CompileMetadata(A->Spec,M,Preview).IsValid());
    TestFalse(TEXT("preview still refused in damage mode"),URPGFrameworkMoveExecutor::ValidatePlaybackCard(Preview,Error,true));
    return true;
}
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FFrameworkLifeProvider,"OneBossFight.Framework.Damage.LifeProvider",EAutomationTestFlags::EditorContext|EAutomationTestFlags::ProductFilter)
bool FFrameworkLifeProvider::RunTest(const FString&)
{
    // Provider seam of the legacy resolver: unset by default, both functions or none.
    TStrongObjectPtr<URPGDamageResolver> R(NewObject<URPGDamageResolver>());
    TestFalse(TEXT("default: no provider (legacy rules)"),R->HasLifeProvider());
    R->SetLifeProvider([]{return true;},nullptr);TestFalse(TEXT("half provider refused"),R->HasLifeProvider());
    R->SetLifeProvider(nullptr,[]{return 1;});TestFalse(TEXT("other half refused"),R->HasLifeProvider());
    R->SetLifeProvider([]{return true;},[]{return 1;});TestTrue(TEXT("both set"),R->HasLifeProvider());
    R->ClearLifeProvider();TestFalse(TEXT("cleared"),R->HasLifeProvider());
    return true;
}
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FFrameworkSelectorProfile,"OneBossFight.Framework.Runtime.SelectorProfile",EAutomationTestFlags::EditorContext|EAutomationTestFlags::ProductFilter)
bool FFrameworkSelectorProfile::RunTest(const FString&)
{
    using namespace FrameworkRuntimeFixture;
    TStrongObjectPtr<URPGBossFrameworkProfile> P(NewObject<URPGBossFrameworkProfile>());FString Error;
    FRPGBossMoveCardSpec SharedPhaseCard; SharedPhaseCard.PhaseId=TEXT("Phase_1"); SharedPhaseCard.AdditionalPhaseIds.Add(TEXT("Phase_2"));
    TArray<float> SharedPoolOne,SharedPoolTwo;
    RPGFramework::AddCandidateCooldownToPhasePools(SharedPhaseCard,3.f,TEXT("Phase_1"),TEXT("Phase_2"),SharedPoolOne,SharedPoolTwo);
    TestEqual(TEXT("shared candidate contributes to Phase 1 pool"),SharedPoolOne.Num(),1);
    TestEqual(TEXT("shared candidate also contributes to Phase 2 pool"),SharedPoolTwo.Num(),1);
    SharedPhaseCard.AdditionalPhaseIds.Reset();
    SharedPoolOne.Reset();SharedPoolTwo.Reset();
    RPGFramework::AddCandidateCooldownToPhasePools(SharedPhaseCard,3.f,TEXT("Phase_1"),TEXT("Phase_2"),SharedPoolOne,SharedPoolTwo);
    TestEqual(TEXT("legacy candidate remains in its primary phase pool"),SharedPoolOne.Num(),1);
    TestEqual(TEXT("legacy candidate does not enter another phase pool"),SharedPoolTwo.Num(),0);
    auto F5=[&P](){Fill(*P);P->FixtureLabel=TEXT("F5 fixture");P->bDamageEnabled=true;P->HitStepCm=15.f;P->HitMaxSubsteps=8;P->RepeatPenalty=.2f;P->RepeatMemory=2;P->AttackCount=2;
        FRPGBossProfileCard C;C.Card=P->Card;C.CooldownSeconds=1.f;C.Weight=1.f;P->Card.Reset();P->Cards.Reset();P->Cards.Add(C);};
    F5();TestTrue(TEXT("explicit F5 profile valid"),RPGFramework::ValidateProfile(*P,Error));
    F5();P->bRangeBandPartition=true;TestTrue(TEXT("range partition remains available in F5"),RPGFramework::ValidateProfile(*P,Error));
    F5();P->Cards.Reset();TestFalse(TEXT("F5 needs at least one card"),RPGFramework::ValidateProfile(*P,Error));
    F5();P->Card=P->Cards[0].Card;TestFalse(TEXT("F5 cannot also carry the single card"),RPGFramework::ValidateProfile(*P,Error));
    for(int32 V:{0,-1,9}){F5();P->AttackCount=V;TestFalse(TEXT("attack count domain"),RPGFramework::ValidateProfile(*P,Error));}
    for(float V:{0.f,-1.f,1.5f,std::numeric_limits<float>::quiet_NaN()}){F5();P->RepeatPenalty=V;TestFalse(TEXT("repeat penalty domain"),RPGFramework::ValidateProfile(*P,Error));}
    for(int32 V:{0,9}){F5();P->RepeatMemory=V;TestFalse(TEXT("repeat memory domain"),RPGFramework::ValidateProfile(*P,Error));}
    F5();P->Cards[0].CooldownSeconds=-1.f;TestFalse(TEXT("cooldown domain"),RPGFramework::ValidateProfile(*P,Error));
    F5();P->Cards[0].Weight=0.f;TestFalse(TEXT("weight domain"),RPGFramework::ValidateProfile(*P,Error));
    F5();P->Cards[0].Card.Reset();TestFalse(TEXT("null candidate card"),RPGFramework::ValidateProfile(*P,Error));
    F5();P->bDamageEnabled=false;TestFalse(TEXT("F5 label needs the damage flag"),RPGFramework::ValidateProfile(*P,Error));
    Fill(*P);FRPGBossProfileCard C;C.Card=P->Card;P->Cards.Add(C);TestFalse(TEXT("F3 profile cannot carry a card list"),RPGFramework::ValidateProfile(*P,Error));
    return true;
}
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FFrameworkGuardChipProfile,"OneBossFight.Framework.Runtime.GuardChipProfile",EAutomationTestFlags::EditorContext|EAutomationTestFlags::ProductFilter)
bool FFrameworkGuardChipProfile::RunTest(const FString&)
{
    using namespace FrameworkRuntimeFixture;
    TStrongObjectPtr<URPGBossFrameworkProfile> P(NewObject<URPGBossFrameworkProfile>());FString Error;
    auto F5=[&P](){Fill(*P);P->FixtureLabel=TEXT("F5 fixture");P->bDamageEnabled=true;P->HitStepCm=15.f;P->HitMaxSubsteps=8;P->RepeatPenalty=.2f;P->RepeatMemory=2;P->AttackCount=2;
        FRPGBossProfileCard C;C.Card=P->Card;C.CooldownSeconds=1.f;C.Weight=1.f;P->Card.Reset();P->Cards.Reset();P->Cards.Add(C);};
    F5();TestTrue(TEXT("zero keeps guard chip disabled"),RPGFramework::ValidateProfile(*P,Error));
    F5();P->GuardChipFraction=.25f;TestTrue(TEXT("fraction inside range is valid"),RPGFramework::ValidateProfile(*P,Error));
    F5();P->GuardChipFraction=1.f;TestTrue(TEXT("full fraction boundary is valid"),RPGFramework::ValidateProfile(*P,Error));
    for(float V:{-.01f,1.01f,std::numeric_limits<float>::infinity(),std::numeric_limits<float>::quiet_NaN()})
    {F5();P->GuardChipFraction=V;TestFalse(TEXT("fraction outside [0,1] fails closed"),RPGFramework::ValidateProfile(*P,Error));TestEqual(TEXT("guard chip validation token"),Error,FString(TEXT("Framework.Profile.GuardChip")));}
    P.Reset(NewObject<URPGBossFrameworkProfile>());Fill(*P);P->GuardChipFraction=.25f;TestFalse(TEXT("enabled guard chip requires F5"),RPGFramework::ValidateProfile(*P,Error));TestEqual(TEXT("F5 lane token"),Error,FString(TEXT("Framework.Profile.GuardChip")));
    return true;
}
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FFrameworkParryRecoveryProfile,"OneBossFight.Framework.Runtime.ParryRecoveryProfile",EAutomationTestFlags::EditorContext|EAutomationTestFlags::ProductFilter)
bool FFrameworkParryRecoveryProfile::RunTest(const FString&)
{
    using namespace FrameworkRuntimeFixture;
    TStrongObjectPtr<URPGBossFrameworkProfile> P(NewObject<URPGBossFrameworkProfile>());FString Error;
    auto F5=[&P](){Fill(*P);P->FixtureLabel=TEXT("F5 fixture");P->bDamageEnabled=true;P->HitStepCm=15.f;P->HitMaxSubsteps=8;P->RepeatPenalty=.2f;P->RepeatMemory=2;P->AttackCount=2;
        FRPGBossProfileCard C;C.Card=P->Card;C.CooldownSeconds=1.f;C.Weight=1.f;P->Card.Reset();P->Cards.Reset();P->Cards.Add(C);};
    F5();TestTrue(TEXT("zero disables parry recovery"),RPGFramework::ValidateProfile(*P,Error));
    F5();P->ParryRecoveryScale=1.f;TestTrue(TEXT("positive recovery scale is valid in F5"),RPGFramework::ValidateProfile(*P,Error));
    F5();P->ParryRecoveryScale=3.f;TestTrue(TEXT("scale upper edge is valid"),RPGFramework::ValidateProfile(*P,Error));
    for(float V:{-.01f,3.01f,std::numeric_limits<float>::infinity(),std::numeric_limits<float>::quiet_NaN()})
    {F5();P->ParryRecoveryScale=V;TestFalse(TEXT("scale outside [0,3] fails closed"),RPGFramework::ValidateProfile(*P,Error));TestEqual(TEXT("parry recovery validation token"),Error,FString(TEXT("Framework.Profile.ParryRecovery")));}
    P.Reset(NewObject<URPGBossFrameworkProfile>());Fill(*P);P->ParryRecoveryScale=1.f;TestFalse(TEXT("enabled parry recovery requires F5"),RPGFramework::ValidateProfile(*P,Error));TestEqual(TEXT("F5 lane token"),Error,FString(TEXT("Framework.Profile.ParryRecovery")));
    return true;
}
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FFrameworkParryFairTelegraphProfile,"OneBossFight.Framework.Runtime.ParryFairTelegraphProfile",EAutomationTestFlags::EditorContext|EAutomationTestFlags::ProductFilter)
bool FFrameworkParryFairTelegraphProfile::RunTest(const FString&)
{
    using namespace FrameworkRuntimeFixture;
    TStrongObjectPtr<URPGBossFrameworkProfile> P(NewObject<URPGBossFrameworkProfile>());FString Error;
    auto F5=[&P](){Fill(*P);P->FixtureLabel=TEXT("F5 fixture");P->bDamageEnabled=true;P->HitStepCm=15.f;P->HitMaxSubsteps=8;P->RepeatPenalty=.2f;P->RepeatMemory=2;P->AttackCount=2;
        FRPGBossProfileCard C;C.Card=P->Card;C.CooldownSeconds=1.f;C.Weight=1.f;P->Card.Reset();P->Cards.Reset();P->Cards.Add(C);};
    F5();TestTrue(TEXT("default off is valid"),RPGFramework::ValidateProfile(*P,Error));
    F5();P->ParryFairTelegraph=true;TestTrue(TEXT("enabled with default minimum rate is valid"),RPGFramework::ValidateProfile(*P,Error));
    F5();P->ParryFairMinScale=1.f;TestTrue(TEXT("minimum scale upper edge is valid"),RPGFramework::ValidateProfile(*P,Error));
    for(float V:{0.f,-.1f,1.01f,std::numeric_limits<float>::infinity(),std::numeric_limits<float>::quiet_NaN()})
    {F5();P->ParryFairMinScale=V;TestFalse(TEXT("minimum rate scale must be in (0,1]"),RPGFramework::ValidateProfile(*P,Error));TestEqual(TEXT("telegraph validation token"),Error,FString(TEXT("Framework.Profile.ParryFairTelegraph")));}
    P.Reset(NewObject<URPGBossFrameworkProfile>());Fill(*P);P->ParryFairTelegraph=true;TestFalse(TEXT("enabled telegraph requires F5"),RPGFramework::ValidateProfile(*P,Error));TestEqual(TEXT("F5 lane token"),Error,FString(TEXT("Framework.Profile.ParryFairTelegraph")));
    return true;
}
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FFrameworkAggroProfile,"OneBossFight.Framework.Runtime.AggroProfile",EAutomationTestFlags::EditorContext|EAutomationTestFlags::ProductFilter)
bool FFrameworkAggroProfile::RunTest(const FString&)
{
    using namespace FrameworkRuntimeFixture;
    TStrongObjectPtr<URPGBossFrameworkProfile> P(NewObject<URPGBossFrameworkProfile>());FString Error;
    auto F5=[&P](){Fill(*P);P->FixtureLabel=TEXT("F5 fixture");P->bDamageEnabled=true;P->HitStepCm=15.f;P->HitMaxSubsteps=8;P->RepeatPenalty=.2f;P->RepeatMemory=2;P->AttackCount=2;
        FRPGBossProfileCard C;C.Card=P->Card;C.CooldownSeconds=1.f;C.Weight=1.f;P->Card.Reset();P->Cards.Reset();P->Cards.Add(C);};
    Fill(*P);TestTrue(TEXT("aggro disabled by default"),RPGFramework::ValidateProfile(*P,Error));
    F5();P->bAggroEnabled=true;P->DodgeSpeedCm=250.f;TestTrue(TEXT("enabled aggro with valid thresholds is accepted"),RPGFramework::ValidateProfile(*P,Error));
    F5();P->bAggroEnabled=true;P->DodgeSpeedCm=250.f;P->AggroEnterFarCm=P->AggroExitFarCm;TestFalse(TEXT("overlapping range thresholds are refused"),RPGFramework::ValidateProfile(*P,Error));TestEqual(TEXT("aggro validation token"),Error,FString(TEXT("Framework.Profile.Aggro")));
    F5();P->bAggroEnabled=true;P->DodgeSpeedCm=250.f;P->AggroDodgeEnterRate=P->AggroDodgeExitRate;TestFalse(TEXT("dodge thresholds need hysteresis"),RPGFramework::ValidateProfile(*P,Error));TestEqual(TEXT("dodge threshold token"),Error,FString(TEXT("Framework.Profile.Aggro")));
    P.Reset(NewObject<URPGBossFrameworkProfile>());Fill(*P);P->bAggroEnabled=true;P->DodgeSpeedCm=250.f;TestFalse(TEXT("enabled aggro requires F5"),RPGFramework::ValidateProfile(*P,Error));TestEqual(TEXT("F5 lane token"),Error,FString(TEXT("Framework.Profile.Aggro")));
    return true;
}
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FFrameworkFatigueProfile,"OneBossFight.Framework.Runtime.FatigueProfile",EAutomationTestFlags::EditorContext|EAutomationTestFlags::ProductFilter)
bool FFrameworkFatigueProfile::RunTest(const FString&)
{
    using namespace FrameworkRuntimeFixture;
    TStrongObjectPtr<URPGBossFrameworkProfile> P(NewObject<URPGBossFrameworkProfile>());FString Error;
    Fill(*P);TestTrue(TEXT("fatigue disabled by default is valid"),RPGFramework::ValidateProfile(*P,Error));
    auto F5=[&P](){Fill(*P);P->FixtureLabel=TEXT("F5 fixture");P->bDamageEnabled=true;P->HitStepCm=15.f;P->HitMaxSubsteps=8;P->RepeatPenalty=.2f;P->RepeatMemory=2;P->AttackCount=2;
        FRPGBossProfileCard C;C.Card=P->Card;C.CooldownSeconds=1.f;C.Weight=1.f;P->Card.Reset();P->Cards.Reset();P->Cards.Add(C);};
    F5();P->FatigueGraceWhiffs=2;P->FatigueFloor=.7f;TestTrue(TEXT("enabled fatigue on valid F5 profile"),RPGFramework::ValidateProfile(*P,Error));
    F5();P->FatigueGraceWhiffs=-1;P->FatigueFloor=.7f;TestFalse(TEXT("negative grace is rejected"),RPGFramework::ValidateProfile(*P,Error));TestEqual(TEXT("fatigue token"),Error,FString(TEXT("Framework.Profile.Fatigue")));
    F5();P->FatigueGraceWhiffs=2;P->FatigueFloor=0.f;TestFalse(TEXT("partial fatigue configuration is rejected"),RPGFramework::ValidateProfile(*P,Error));TestEqual(TEXT("fatigue token"),Error,FString(TEXT("Framework.Profile.Fatigue")));
    F5();P->FatigueGraceWhiffs=2;P->FatigueFloor=1.01f;TestFalse(TEXT("floor above one is rejected"),RPGFramework::ValidateProfile(*P,Error));TestEqual(TEXT("fatigue token"),Error,FString(TEXT("Framework.Profile.Fatigue")));
    P.Reset(NewObject<URPGBossFrameworkProfile>());Fill(*P);P->FatigueGraceWhiffs=2;P->FatigueFloor=.7f;TestFalse(TEXT("enabled fatigue requires F5"),RPGFramework::ValidateProfile(*P,Error));TestEqual(TEXT("F5 lane token"),Error,FString(TEXT("Framework.Profile.Fatigue")));
    return true;
}
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FFrameworkPhaseProfile,"OneBossFight.Framework.Runtime.PhaseProfile",EAutomationTestFlags::EditorContext|EAutomationTestFlags::ProductFilter)
bool FFrameworkPhaseProfile::RunTest(const FString&)
{
    using namespace FrameworkRuntimeFixture;
    TStrongObjectPtr<URPGBossFrameworkProfile> P(NewObject<URPGBossFrameworkProfile>());FString Error;
    auto Phased=[&P](){Fill(*P);P->FixtureLabel=TEXT("F5 fixture");P->bDamageEnabled=true;P->HitStepCm=15.f;P->HitMaxSubsteps=8;P->RepeatPenalty=.2f;P->RepeatMemory=2;P->AttackCount=2;
        FRPGBossProfileCard C;C.Card=P->Card;C.CooldownSeconds=1.f;C.Weight=1.f;P->Card.Reset();P->Cards.Reset();P->Cards.Add(C);
        P->BossMaxHealth=100.f;P->PlayerHitDamage=10.f;P->PhaseTwoFraction=.5f;P->PhaseTwoId=TEXT("Phase_2");};
    auto Refused=[&](const TCHAR* Why){TestFalse(Why,RPGFramework::ValidateProfile(*P,Error));TestEqual(*FString::Printf(TEXT("%s: token"),Why),Error,FString(TEXT("Framework.Profile.Phase")));};
    Phased();TestTrue(TEXT("explicit phased profile valid"),RPGFramework::ValidateProfile(*P,Error));
    Phased();P->PhaseTwoFraction=0.f;P->PhaseTwoId=NAME_None;TestTrue(TEXT("no phases stays valid"),RPGFramework::ValidateProfile(*P,Error));
    for(float V:{-.1f,1.f,1.5f,std::numeric_limits<float>::infinity(),std::numeric_limits<float>::quiet_NaN()}){Phased();P->PhaseTwoFraction=V;Refused(TEXT("fraction domain"));}
    Phased();P->PhaseTwoId=NAME_None;Refused(TEXT("fraction needs a phase name"));
    Phased();P->PhaseTwoFraction=0.f;Refused(TEXT("phase name needs a fraction"));
    Phased();P->BossMaxHealth=0.f;P->PlayerHitDamage=0.f;Refused(TEXT("phases need a hittable boss"));
    Fill(*P);P->Cards.Reset();P->bDamageEnabled=false;P->PhaseTwoFraction=.5f;P->PhaseTwoId=TEXT("Phase_2");P->BossMaxHealth=100.f;P->PlayerHitDamage=10.f;Refused(TEXT("phases need the selector lane"));
    return true;
}
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FFrameworkPhasePoolStarvation,"OneBossFight.Framework.Runtime.PhasePoolStarvation",EAutomationTestFlags::EditorContext|EAutomationTestFlags::ProductFilter)
bool FFrameworkPhasePoolStarvation::RunTest(const FString&)
{
    using RPGFramework::PhasePoolCannotStarve;
    TestFalse(TEXT("KI-149: two cooled cards, three attacks"),PhasePoolCannotStarve({3.f,2.5f},3));
    TestTrue(TEXT("a zero-cooldown card always offers"),PhasePoolCannotStarve({3.f,0.f},3));
    TestTrue(TEXT("cardinality equal to the attack count"),PhasePoolCannotStarve({3.f,2.5f},2));
    TestTrue(TEXT("cardinality above the attack count"),PhasePoolCannotStarve({3.f,2.5f,1.f},3));
    TestTrue(TEXT("one attack, one cooled card"),PhasePoolCannotStarve({3.f},1));
    TestFalse(TEXT("no cards"),PhasePoolCannotStarve({},1));
    TestFalse(TEXT("attack count below one"),PhasePoolCannotStarve({0.f,0.f},0));
    TestFalse(TEXT("non-finite cooldown is not a filler"),PhasePoolCannotStarve({std::numeric_limits<float>::quiet_NaN()},2));
    for(int32 Attacks=1;Attacks<=8;++Attacks)for(int32 Cards=0;Cards<=8;++Cards)
    {
        TArray<float> Positive;Positive.Init(2.f,Cards);
        TestEqual(*FString::Printf(TEXT("positive-cooldown pool cards=%d attacks=%d"),Cards,Attacks),PhasePoolCannotStarve(Positive,Attacks),Cards>=Attacks);
        if(Cards<Attacks){TArray<float> WithZero=Positive;WithZero.Add(0.f);TestTrue(*FString::Printf(TEXT("zero-cooldown filler cards=%d attacks=%d"),Cards,Attacks),PhasePoolCannotStarve(WithZero,Attacks));}
    }
    return true;
}
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FFrameworkPhasePoolAbortStarvation,"OneBossFight.Framework.Runtime.PhasePoolAbortStarvation",EAutomationTestFlags::EditorContext|EAutomationTestFlags::ProductFilter)
bool FFrameworkPhasePoolAbortStarvation::RunTest(const FString&)
{
    // BQ-01 / KI-155: the PARRY-profile trace - two cooled cards, two attacks, one parried abort - passes the attack-count rule
    // but starves on the retry; the abort-aware rule refuses it. Written, not compiled (Lead C-1155 build required).
    using RPGFramework::PhasePoolCannotStarve; using RPGFramework::PhasePoolCannotStarveWithAborts;
    TestTrue(TEXT("KI-155 trace passes the attack-count rule"),PhasePoolCannotStarve({3.f,3.f},2));
    TestFalse(TEXT("KI-155 trace: one abort starves two cooled cards"),PhasePoolCannotStarveWithAborts({3.f,3.f},2,1));
    TestTrue(TEXT("a third cooled card covers one abort"),PhasePoolCannotStarveWithAborts({3.f,3.f,3.f},2,1));
    TestTrue(TEXT("a zero-cooldown card covers any number of aborts"),PhasePoolCannotStarveWithAborts({3.f,0.f},2,5));
    TestTrue(TEXT("zero aborts equals the attack-count rule"),PhasePoolCannotStarveWithAborts({3.f,2.f},2,0)==PhasePoolCannotStarve({3.f,2.f},2));
    TestFalse(TEXT("negative abort budget refused"),PhasePoolCannotStarveWithAborts({0.f},1,-1));
    TestFalse(TEXT("attack count below one refused"),PhasePoolCannotStarveWithAborts({0.f},0,1));
    // X-2320: the compile-time decision actually fails closed for the KI-155 trace once a profile declares its abort budget.
    using RPGFramework::CooldownStarvationError;
    TestTrue(TEXT("unphased KI-155 trace refused with an abort budget"),CooldownStarvationError(false,{3.f,3.f},{},{},2,1)==TEXT("Framework.Profile.CooldownStarvation"));
    TestTrue(TEXT("unphased profile without an abort budget unchanged (opt-in)"),CooldownStarvationError(false,{3.f,3.f},{},{},2,0).IsEmpty());
    TestTrue(TEXT("unphased budget covered by a third card"),CooldownStarvationError(false,{3.f,3.f,3.f},{},{},2,1).IsEmpty());
    TestTrue(TEXT("phased: zero aborts keeps the KI-149 rule"),CooldownStarvationError(true,{},{3.f,3.f},{3.f,3.f},2,0).IsEmpty());
    TestTrue(TEXT("phased: one abort starves a two-card phase"),CooldownStarvationError(true,{},{3.f,3.f},{3.f,3.f,3.f},2,1)==TEXT("Framework.Profile.PhaseCooldownStarvation"));
    TestTrue(TEXT("phased: KI-149 refusal unchanged"),CooldownStarvationError(true,{},{3.f},{3.f,3.f},2,0)==TEXT("Framework.Profile.PhaseCooldownStarvation"));
    for(int32 Attacks=1;Attacks<=6;++Attacks)for(int32 Aborts=0;Aborts<=3;++Aborts)for(int32 Cards=0;Cards<=9;++Cards)
    {
        TArray<float> Cooled;Cooled.Init(2.f,Cards);
        TestTrue(*FString::Printf(TEXT("cooled cards=%d attacks=%d aborts=%d"),Cards,Attacks,Aborts),PhasePoolCannotStarveWithAborts(Cooled,Attacks,Aborts)==(Cards>=Attacks+Aborts));
    }
    return true;
}
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FFrameworkPostureProfile,"OneBossFight.Framework.Runtime.PostureProfile",EAutomationTestFlags::EditorContext|EAutomationTestFlags::ProductFilter)
bool FFrameworkPostureProfile::RunTest(const FString&)
{
    using namespace FrameworkRuntimeFixture;
    TStrongObjectPtr<URPGBossFrameworkProfile> P(NewObject<URPGBossFrameworkProfile>());FString Error;
    auto Postured=[&P](){Fill(*P);P->FixtureLabel=TEXT("F5 fixture");P->bDamageEnabled=true;P->HitStepCm=15.f;P->HitMaxSubsteps=8;P->RepeatPenalty=.2f;P->RepeatMemory=2;P->AttackCount=2;
        FRPGBossProfileCard C;C.Card=P->Card;C.CooldownSeconds=1.f;C.Weight=1.f;P->Card.Reset();P->Cards.Reset();P->Cards.Add(C);
        P->BossMaxHealth=100.f;P->PlayerHitDamage=10.f;P->PostureMax=100.f;P->PlayerPostureHitAmount=60.f;P->StaggerSeconds=1.f;P->PostureRegenDelaySeconds=6.f;P->PostureRegenPerSecond=13.f;};
    auto Refused=[&](const TCHAR* Why){TestFalse(Why,RPGFramework::ValidateProfile(*P,Error));TestEqual(*FString::Printf(TEXT("%s: token"),Why),Error,FString(TEXT("Framework.Profile.Posture")));};
    Postured();TestTrue(TEXT("explicit posture profile valid"),RPGFramework::ValidateProfile(*P,Error));
    Postured();P->PostureMax=0.f;P->PlayerPostureHitAmount=0.f;P->StaggerSeconds=0.f;P->PostureRegenDelaySeconds=0.f;P->PostureRegenPerSecond=0.f;TestTrue(TEXT("all zero = posture off"),RPGFramework::ValidateProfile(*P,Error));
    using Field=float URPGBossFrameworkProfile::*;
    const Field Fields[]={&URPGBossFrameworkProfile::PostureMax,&URPGBossFrameworkProfile::PlayerPostureHitAmount,&URPGBossFrameworkProfile::StaggerSeconds,&URPGBossFrameworkProfile::PostureRegenDelaySeconds,&URPGBossFrameworkProfile::PostureRegenPerSecond};
    for(Field F:Fields)for(float V:{-1.f,2.e6f,std::numeric_limits<float>::infinity(),std::numeric_limits<float>::quiet_NaN()}){Postured();P.Get()->*F=V;Refused(TEXT("value domain"));}
    Postured();P->PostureMax=0.f;Refused(TEXT("posture set without a maximum"));
    Postured();P->PlayerPostureHitAmount=0.f;Refused(TEXT("posture set without a hit amount"));
    Postured();P->PlayerPostureHitAmount=101.f;Refused(TEXT("hit larger than the pool"));
    Postured();P->StaggerSeconds=.49f;Refused(TEXT("stagger below the minimum"));
    Postured();P->StaggerSeconds=61.f;Refused(TEXT("stagger above the maximum"));
    Postured();P->BossMaxHealth=0.f;P->PlayerHitDamage=0.f;Refused(TEXT("posture needs a hittable boss"));
    Fill(*P);P->Cards.Reset();P->bDamageEnabled=false;P->BossMaxHealth=100.f;P->PlayerHitDamage=10.f;P->PostureMax=100.f;P->PlayerPostureHitAmount=60.f;P->StaggerSeconds=1.f;Refused(TEXT("posture needs the selector lane"));
    return true;
}
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FFrameworkBleedProfile,"OneBossFight.Framework.Runtime.BleedProfile",EAutomationTestFlags::EditorContext|EAutomationTestFlags::ProductFilter)
bool FFrameworkBleedProfile::RunTest(const FString&)
{
    using namespace FrameworkRuntimeFixture;
    TStrongObjectPtr<URPGBossFrameworkProfile> P(NewObject<URPGBossFrameworkProfile>());FString Error;
    auto Bleeding=[&P](){Fill(*P);P->FixtureLabel=TEXT("F5 fixture");P->bDamageEnabled=true;P->HitStepCm=15.f;P->HitMaxSubsteps=8;P->RepeatPenalty=.2f;P->RepeatMemory=2;P->AttackCount=2;
        FRPGBossProfileCard C;C.Card=P->Card;C.CooldownSeconds=1.f;C.Weight=1.f;P->Card.Reset();P->Cards.Reset();P->Cards.Add(C);
        P->BossMaxHealth=100.f;P->PlayerHitDamage=10.f;P->BleedBuildupPerHit=60.f;P->BleedInitialThreshold=100.f;P->BleedThresholdIncrease=20.f;P->BleedThresholdMax=200.f;P->BleedHpFraction=.2f;};
    auto Refused=[&](const TCHAR* Why){TestFalse(Why,RPGFramework::ValidateProfile(*P,Error));TestEqual(*FString::Printf(TEXT("%s: token"),Why),Error,FString(TEXT("Framework.Profile.Bleed")));};
    Bleeding();TestTrue(TEXT("explicit bleed profile valid"),RPGFramework::ValidateProfile(*P,Error));
    Bleeding();P->BleedBuildupPerHit=0.f;P->BleedInitialThreshold=0.f;P->BleedThresholdIncrease=0.f;P->BleedThresholdMax=0.f;P->BleedHpFraction=0.f;TestTrue(TEXT("all zero = bleed off"),RPGFramework::ValidateProfile(*P,Error));
    using Field=float URPGBossFrameworkProfile::*;
    const Field Fields[]={&URPGBossFrameworkProfile::BleedBuildupPerHit,&URPGBossFrameworkProfile::BleedInitialThreshold,&URPGBossFrameworkProfile::BleedThresholdIncrease,&URPGBossFrameworkProfile::BleedThresholdMax,&URPGBossFrameworkProfile::BleedHpFraction};
    for(Field F:Fields)for(float V:{-1.f,2.e6f,std::numeric_limits<float>::infinity(),std::numeric_limits<float>::quiet_NaN()}){Bleeding();P.Get()->*F=V;Refused(TEXT("value domain"));}
    Bleeding();P->BleedBuildupPerHit=0.f;Refused(TEXT("bleed set without a buildup"));
    Bleeding();P->BleedInitialThreshold=0.f;Refused(TEXT("threshold below one"));
    Bleeding();P->BleedThresholdMax=50.f;Refused(TEXT("maximum below the first threshold"));
    Bleeding();P->BleedHpFraction=0.f;Refused(TEXT("no health fraction"));
    Bleeding();P->BleedHpFraction=1.5f;Refused(TEXT("fraction above one"));
    Bleeding();P->BossMaxHealth=0.f;P->PlayerHitDamage=0.f;Refused(TEXT("bleed needs a hittable boss"));
    Fill(*P);P->Cards.Reset();P->bDamageEnabled=false;P->BossMaxHealth=100.f;P->PlayerHitDamage=10.f;P->BleedBuildupPerHit=60.f;P->BleedInitialThreshold=100.f;P->BleedThresholdMax=200.f;P->BleedHpFraction=.2f;Refused(TEXT("bleed needs the selector lane"));
    return true;
}
namespace FrameworkSweepFixture
{
// Synthetic out-and-back thrust, forward distance of the base from the target (component X): windup 115 cm, apex 13.67 cm at 0.267 s, retract 146 cm at 0.308 s.
FRPGBossMoveWindow Window(bool bBaked)
{
    FRPGBossMoveWindow W;W.WindowId=TEXT("Jab");W.HitGroup=TEXT("G");W.StartSeconds=.25f;W.EndSeconds=.3083f;W.SocketA=TEXT("weapon_r");W.SocketB=TEXT("root_weapon_end_r");W.RadiusCm=15.f;
    if(bBaked)
    {
        const double T[]={.25,.2583,.2667,.275,.2833,.2917,.3,.3083};const double X[]={115.,60.,13.67,60.,100.,125.,138.,146.};
        for(int32 I=0;I<8;++I){FRPGBakedBladeSample S;S.TimeSeconds=float(T[I]);S.BaseCS=FVector(X[I],0.,150.);S.TipCS=FVector(X[I]+70.,0.,150.);W.BakedSamples.Add(S);}
    }
    return W;
}
}
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FFrameworkSweepHitchCoverage,"OneBossFight.Framework.Runtime.SweepHitchCoverage",EAutomationTestFlags::EditorContext|EAutomationTestFlags::ProductFilter)
bool FFrameworkSweepHitchCoverage::RunTest(const FString&)
{
    using namespace FrameworkSweepFixture;
    // The two tick poses of a 72 ms hitch that skips the whole window: windup at 0.225 s, retraction at 0.298 s (live sockets read at those ticks).
    FRPGSweepPose Before;Before.A=FVector(115.,0.,150.);Before.B=FVector(185.,0.,150.);
    FRPGSweepPose After;After.A=FVector(146.,0.,150.);After.B=FVector(216.,0.,150.);
    TArray<FRPGSweepPose> Keys;bool bBaked=true;double Lo=0.,Hi=0.;
    TestTrue(TEXT("legacy lerp path runs"),RPGBossSweep::BuildKeyPoses(Window(false),.225,.298,Before,After,Keys,bBaked,Lo,Hi));
    TestFalse(TEXT("no samples = live sockets"),bBaked);
    float LerpMin=FLT_MAX;for(const auto& K:Keys)LerpMin=FMath::Min(LerpMin,float(K.A.X));
    TestTrue(TEXT("legacy chord misses the apex (base never nearer than 115 cm)"),LerpMin>100.f);
    TestTrue(TEXT("baked path runs"),RPGBossSweep::BuildKeyPoses(Window(true),.225,.298,Before,After,Keys,bBaked,Lo,Hi));
    TestTrue(TEXT("baked samples used"),bBaked);
    float BakedMin=FLT_MAX;for(const auto& K:Keys)BakedMin=FMath::Min(BakedMin,float(K.A.X));
    TestTrue(TEXT("baked path covers the apex across the same hitch"),BakedMin<=15.f);
    TestEqual(TEXT("overlap start is the window start"),Lo,double(.25f));TestEqual(TEXT("overlap end is the tick end"),Hi,.298);
    TestFalse(TEXT("no overlap, no poses"),RPGBossSweep::BuildKeyPoses(Window(true),.31,.33,Before,After,Keys,bBaked,Lo,Hi));
    TestFalse(TEXT("non-advancing tick, no poses"),RPGBossSweep::BuildKeyPoses(Window(true),.28,.28,Before,After,Keys,bBaked,Lo,Hi));
    return true;
}
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FFrameworkBakedSamplesValidation,"OneBossFight.Framework.Runtime.BakedSamplesValidation",EAutomationTestFlags::EditorContext|EAutomationTestFlags::ProductFilter)
bool FFrameworkBakedSamplesValidation::RunTest(const FString&)
{
    using namespace FrameworkRuntimeFixture;
    TStrongObjectPtr<URPGBossMoveCard> A(Card());
    FRPGBossMoveMetadata M;M.AnimationPath=A->Spec.Sequence.ToSoftObjectPath();M.SkeletonPath=A->Spec.Skeleton.ToSoftObjectPath();M.AnimationSkeletonPath=M.MeshSkeletonPath=M.SkeletonPath;
    M.ClipLengthSeconds=1.7;M.Slots.Add(TEXT("FullBody"));M.SocketOrBoneNames.Add(TEXT("weapon_r"));M.SocketOrBoneNames.Add(TEXT("root_weapon_end_r"));
    auto WithSamples=[&A](TFunction<void(TArray<FRPGBakedBladeSample>&)> Edit){FRPGBossMoveCardSpec S=A->Spec;auto& W=S.Windows[0];W.BakedSamples.Reset();
        for(int32 I=0;I<5;++I){FRPGBakedBladeSample B;B.TimeSeconds=W.StartSeconds-.01f+I*(W.EndSeconds-W.StartSeconds+.02f)/4.f;B.BaseCS=FVector(I*10.,0.,0.);B.TipCS=FVector(I*10.+60.,0.,0.);W.BakedSamples.Add(B);}
        Edit(W.BakedSamples);return S;};
    auto Refused=[&](const FRPGBossMoveCardSpec& S,const TCHAR* Why){const auto R=RPGBossMoveCards::Validate(S,M);TestFalse(Why,R.IsValid());bool bToken=false;for(const FString& E:R.Errors)bToken|=E.Contains(TEXT("MoveCard.BakedSamples"));TestTrue(*FString::Printf(TEXT("%s: named token"),Why),bToken);};
    TestTrue(TEXT("valid baked samples"),RPGBossMoveCards::Validate(WithSamples([](auto&){}),M).IsValid());
    TestTrue(TEXT("no samples stay valid (opt-in)"),RPGBossMoveCards::Validate(A->Spec,M).IsValid());
    Refused(WithSamples([](auto& L){L.SetNum(1);}),TEXT("one sample"));
    Refused(WithSamples([](auto& L){L[2].TimeSeconds=L[1].TimeSeconds;}),TEXT("times not strictly increasing"));
    Refused(WithSamples([](auto& L){L[0].TimeSeconds=L[0].TimeSeconds+.05f;}),TEXT("first sample after the window start"));
    Refused(WithSamples([](auto& L){L[0].TimeSeconds=-.5f;}),TEXT("negative first sample time"));
    Refused(WithSamples([](auto& L){L.Last().TimeSeconds=L.Last().TimeSeconds-.05f;}),TEXT("last sample before the window end"));
    Refused(WithSamples([](auto& L){L.Last().TimeSeconds=1.71f;}),TEXT("sample beyond the clip length"));
    Refused(WithSamples([](auto& L){L[1].BaseCS.X=std::numeric_limits<double>::quiet_NaN();}),TEXT("non-finite sample"));
    Refused(WithSamples([](auto& L){L[1].TipCS.Z=2.e5;}),TEXT("sample beyond the domain"));
    return true;
}
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FFrameworkSelectorTieProfile,"OneBossFight.Framework.Runtime.SelectorTieProfile",EAutomationTestFlags::EditorContext|EAutomationTestFlags::ProductFilter)
bool FFrameworkSelectorTieProfile::RunTest(const FString&)
{
    using namespace FrameworkRuntimeFixture;
    TStrongObjectPtr<URPGBossFrameworkProfile> P(NewObject<URPGBossFrameworkProfile>());FString Error;
    auto F5=[&](){Fill(*P);P->FixtureLabel=TEXT("F5 fixture");P->bDamageEnabled=true;P->HitStepCm=15.f;P->HitMaxSubsteps=8;P->RepeatPenalty=.2f;P->RepeatMemory=2;P->AttackCount=2;
        FRPGBossProfileCard C;C.Card=P->Card;C.CooldownSeconds=1.f;C.Weight=1.f;P->Card.Reset();P->Cards.Reset();P->Cards.Add(C);P->SelectorTieBand=0.f;P->SelectorTieSeed=0;};
    F5();TestTrue(TEXT("tie band off: valid"),RPGFramework::ValidateProfile(*P,Error));
    F5();P->SelectorTieBand=.1f;P->SelectorTieSeed=12345;TestTrue(TEXT("tie band 0.1 with a seed: valid"),RPGFramework::ValidateProfile(*P,Error));
    F5();P->SelectorTieBand=.5f;TestTrue(TEXT("tie band 0.5 is the upper edge: valid"),RPGFramework::ValidateProfile(*P,Error));
    for(float Bad:{-.1f,.51f,std::numeric_limits<float>::infinity(),std::numeric_limits<float>::quiet_NaN()}){F5();P->SelectorTieBand=Bad;TestFalse(TEXT("tie band outside [0,0.5]"),RPGFramework::ValidateProfile(*P,Error));TestEqual(TEXT("token"),Error,FString(TEXT("Framework.Profile.Domain")));}
    {TStrongObjectPtr<URPGBossFrameworkProfile> F3(NewObject<URPGBossFrameworkProfile>());Fill(*F3);TestTrue(TEXT("fresh F3 profile valid"),RPGFramework::ValidateProfile(*F3,Error));F3->SelectorTieBand=.1f;TestFalse(TEXT("tie band outside the F5 lane"),RPGFramework::ValidateProfile(*F3,Error));TestEqual(TEXT("token"),Error,FString(TEXT("Framework.Profile.Domain")));}
    return true;
}
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FFrameworkNeutralStrafeHoldProfile,"OneBossFight.Framework.Runtime.NeutralStrafeHoldProfile",EAutomationTestFlags::EditorContext|EAutomationTestFlags::ProductFilter)
bool FFrameworkNeutralStrafeHoldProfile::RunTest(const FString&)
{
    using namespace FrameworkRuntimeFixture;
    TStrongObjectPtr<URPGBossFrameworkProfile> P(NewObject<URPGBossFrameworkProfile>());FString Error;
    TestEqual(TEXT("minimum hold default retains literal .8"),P->NeutralStrafeMinHoldSeconds,.8);
    TestEqual(TEXT("maximum hold default retains literal 1.6"),P->NeutralStrafeMaxHoldSeconds,1.6);
    for(const double Elapsed:{0.,.79,1.6,2.41,10.})
        TestEqual(TEXT("profile defaults preserve seeded direction result"),RPGBossStrafe::DirectionAt(193,Elapsed,P->NeutralStrafeMinHoldSeconds,P->NeutralStrafeMaxHoldSeconds),RPGBossStrafe::DirectionAt(193,Elapsed,.8,1.6));
    auto F5=[&](){Fill(*P);P->FixtureLabel=TEXT("F5 fixture");P->bDamageEnabled=true;P->HitStepCm=15.f;P->HitMaxSubsteps=8;P->RepeatPenalty=.2f;P->RepeatMemory=2;P->AttackCount=2;
        FRPGBossProfileCard C;C.Card=P->Card;C.CooldownSeconds=1.f;C.Weight=1.f;P->Card.Reset();P->Cards={C};};
    F5();TestTrue(TEXT("default hold window is valid"),RPGFramework::ValidateProfile(*P,Error));
    for(double Bad:{std::numeric_limits<double>::quiet_NaN(),std::numeric_limits<double>::infinity(),0.})
    {F5();P->NeutralStrafeMinHoldSeconds=Bad;TestFalse(TEXT("invalid minimum hold is refused"),RPGFramework::ValidateProfile(*P,Error));}
    for(double Bad:{std::numeric_limits<double>::quiet_NaN(),std::numeric_limits<double>::infinity(),0.})
    {F5();P->NeutralStrafeMaxHoldSeconds=Bad;TestFalse(TEXT("invalid maximum hold is refused"),RPGFramework::ValidateProfile(*P,Error));}
    F5();P->NeutralStrafeMinHoldSeconds=.8;P->NeutralStrafeMaxHoldSeconds=std::nextafter(.8,1.);TestTrue(TEXT("adjacent greater maximum is valid"),RPGFramework::ValidateProfile(*P,Error));
    F5();P->NeutralStrafeMinHoldSeconds=.8;P->NeutralStrafeMaxHoldSeconds=std::nextafter(.8,0.);TestFalse(TEXT("adjacent lower maximum is refused"),RPGFramework::ValidateProfile(*P,Error));
    F5();P->NeutralStrafeMinHoldSeconds=.7;TestTrue(TEXT("valid authored hold window is accepted"),RPGFramework::ValidateProfile(*P,Error));
    Fill(*P);P->NeutralStrafeMinHoldSeconds=.7;TestFalse(TEXT("custom hold window is F5 only"),RPGFramework::ValidateProfile(*P,Error));
    return true;
}
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FFrameworkComboProfile,"OneBossFight.Framework.Runtime.ComboProfile",EAutomationTestFlags::EditorContext|EAutomationTestFlags::ProductFilter)
bool FFrameworkComboProfile::RunTest(const FString&)
{
    // Combo graph in the profile (token Framework.Profile.<RPGBossCombo token>); the graph rules themselves are tested in Framework.Combo.*.
    using namespace FrameworkRuntimeFixture;
    TStrongObjectPtr<URPGBossFrameworkProfile> P(NewObject<URPGBossFrameworkProfile>());FString Error;
    auto Edge=[](const TCHAR* To){FRPGBossComboEdgeData E;E.ToNode=To;return E;};
    auto Node=[&](const TCHAR* Id,const TCHAR* Move,TArray<FRPGBossComboEdgeData> Edges={}){FRPGBossComboNodeData N;N.NodeId=Id;N.MoveId=Move;N.Edges=Edges;return N;};
    auto F5=[&](){Fill(*P);P->FixtureLabel=TEXT("F5 fixture");P->bDamageEnabled=true;P->HitStepCm=15.f;P->HitMaxSubsteps=8;P->RepeatPenalty=.2f;P->RepeatMemory=2;P->AttackCount=3;
        FRPGBossProfileCard C;C.Card=P->Card;C.CooldownSeconds=1.f;C.Weight=1.f;P->Card.Reset();P->Cards.Reset();P->Cards.Add(C);
        P->ComboNodes.Reset();P->ComboRoot=NAME_None;P->ComboMaxDepth=3;};
    auto Chain=[&](){P->ComboRoot=TEXT("A");P->ComboNodes={Node(TEXT("A"),TEXT("MoveA"),{Edge(TEXT("B"))}),Node(TEXT("B"),TEXT("MoveB"))};};
    F5();TestTrue(TEXT("no combo: valid"),RPGFramework::ValidateProfile(*P,Error));
    F5();Chain();TestTrue(TEXT("two node chain: valid"),RPGFramework::ValidateProfile(*P,Error));
    F5();Chain();P->ComboNodes[1].Edges={Edge(TEXT("A"))};{const FString Token=RPGBossCombo::Validate(RPGFramework::BuildComboGraph(*P));TestEqual(TEXT("cycle seen by the pure rule"),Token,FString(TEXT("Combo.Cycle")));}
    TestFalse(TEXT("cycle refused"),RPGFramework::ValidateProfile(*P,Error));TestEqual(TEXT("cycle token"),Error,FString(TEXT("Framework.Profile.Combo.Cycle")));
    F5();Chain();P->ComboMaxDepth=1;TestFalse(TEXT("depth 2 path with max depth 1 refused"),RPGFramework::ValidateProfile(*P,Error));TestEqual(TEXT("depth token"),Error,FString(TEXT("Framework.Profile.Combo.Depth")));
    F5();Chain();P->ComboMaxDepth=4;TestFalse(TEXT("max depth 4 refused"),RPGFramework::ValidateProfile(*P,Error));TestEqual(TEXT("max depth token"),Error,FString(TEXT("Framework.Profile.Combo.MaxDepth")));
    F5();Chain();P->ComboRoot=TEXT("Zed");TestFalse(TEXT("unknown root refused"),RPGFramework::ValidateProfile(*P,Error));TestEqual(TEXT("root token"),Error,FString(TEXT("Framework.Profile.Combo.Root")));
    F5();P->ComboRoot=TEXT("A");TestFalse(TEXT("root without nodes refused"),RPGFramework::ValidateProfile(*P,Error));TestEqual(TEXT("empty token"),Error,FString(TEXT("Framework.Profile.Combo.Empty")));
    {TStrongObjectPtr<URPGBossFrameworkProfile> F3(NewObject<URPGBossFrameworkProfile>());Fill(*F3);F3->ComboRoot=TEXT("A");F3->ComboNodes={Node(TEXT("A"),TEXT("MoveA"))};TestFalse(TEXT("combo outside the F5 lane refused"),RPGFramework::ValidateProfile(*F3,Error));TestEqual(TEXT("lane token"),Error,FString(TEXT("Framework.Profile.Domain")));}
    return true;
}
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FFrameworkRepositionProfile,"OneBossFight.Framework.Runtime.RepositionProfile",EAutomationTestFlags::EditorContext|EAutomationTestFlags::ProductFilter)
bool FFrameworkRepositionProfile::RunTest(const FString&)
{
    using namespace FrameworkRuntimeFixture;
    TStrongObjectPtr<URPGBossFrameworkProfile> P(NewObject<URPGBossFrameworkProfile>());FString Error;
    auto F5=[&](){Fill(*P);P->FixtureLabel=TEXT("F5 fixture");P->bDamageEnabled=true;P->HitStepCm=15.f;P->HitMaxSubsteps=8;P->RepeatPenalty=.2f;P->RepeatMemory=2;P->AttackCount=2;
        FRPGBossProfileCard C;C.Card=P->Card;C.CooldownSeconds=1.f;C.Weight=1.f;P->Card.Reset();P->Cards.Reset();P->Cards.Add(C);P->RepositionMax=0;P->RepositionTurnDegPerSecond=0.f;};
    F5();TestTrue(TEXT("off by default: valid"),RPGFramework::ValidateProfile(*P,Error));
    for(int32 V:{1,3,8}){F5();P->RepositionMax=V;P->RepositionTurnDegPerSecond=180.f;TestTrue(TEXT("1..8 valid"),RPGFramework::ValidateProfile(*P,Error));}
    for(int32 V:{-1,9,100}){F5();P->RepositionMax=V;P->RepositionTurnDegPerSecond=180.f;TestFalse(TEXT("outside 0..8 refused"),RPGFramework::ValidateProfile(*P,Error));TestEqual(TEXT("token"),Error,FString(TEXT("Framework.Profile.Domain")));}
    F5();P->RepositionMax=2;TestFalse(TEXT("reposition without a turn rate refused"),RPGFramework::ValidateProfile(*P,Error));TestEqual(TEXT("token"),Error,FString(TEXT("Framework.Profile.Domain")));
    F5();P->RepositionTurnDegPerSecond=180.f;TestFalse(TEXT("turn rate without reposition refused"),RPGFramework::ValidateProfile(*P,Error));TestEqual(TEXT("token"),Error,FString(TEXT("Framework.Profile.Domain")));
    for(float V:{-1.f,721.f,std::numeric_limits<float>::quiet_NaN()}){F5();P->RepositionMax=2;P->RepositionTurnDegPerSecond=V;TestFalse(TEXT("turn rate outside (0,720] refused"),RPGFramework::ValidateProfile(*P,Error));TestEqual(TEXT("token"),Error,FString(TEXT("Framework.Profile.Domain")));}
    {TStrongObjectPtr<URPGBossFrameworkProfile> F3(NewObject<URPGBossFrameworkProfile>());Fill(*F3);F3->RepositionMax=2;F3->RepositionTurnDegPerSecond=180.f;TestFalse(TEXT("outside the F5 lane refused"),RPGFramework::ValidateProfile(*F3,Error));TestEqual(TEXT("lane token"),Error,FString(TEXT("Framework.Profile.Domain")));}
    return true;
}
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FFrameworkExecutorWatchdogRule,"OneBossFight.Framework.Runtime.ExecutorWatchdogRule",EAutomationTestFlags::EditorContext|EAutomationTestFlags::ProductFilter)
bool FFrameworkExecutorWatchdogRule::RunTest(const FString&)
{
    // BOSS-EXE-007: timeout covers both recovery and the montage's clip tail before adding 0.5 s of world-time tolerance.
    TestEqual(TEXT("1.65 s at rate 1"),RPGBossTrack::WatchdogTimeoutSeconds(1.65f,1.f),2.15,1.e-6);
    TestEqual(TEXT("1.65 s at rate 2 is faster"),RPGBossTrack::WatchdogTimeoutSeconds(1.65f,2.f),1.325,1.e-6);
    TestEqual(TEXT("0.4833 s at rate 0.5 is slower"),RPGBossTrack::WatchdogTimeoutSeconds(.4833f,.5f),0.4833/0.5+0.5,1.e-4);
    TestEqual(TEXT("clip natural end plus authored blend-out gets its own watchdog budget"),RPGBossTrack::WatchdogTimeoutSeconds(1.10333f,1.f,1.60333f,.1f),2.10333,1.e-5);
    TestEqual(TEXT("recovery plus authored blend-out determines the watchdog when later"),RPGBossTrack::WatchdogTimeoutSeconds(1.65f,1.f,1.2f,.1f),2.25,1.e-6);
    for(float Bad:{0.f,-1.f,std::numeric_limits<float>::quiet_NaN(),std::numeric_limits<float>::infinity()})
    {
        TestTrue(TEXT("bad recovery end is invalid"),RPGBossTrack::WatchdogTimeoutSeconds(Bad,1.f)<0.);
        TestTrue(TEXT("bad play rate is invalid"),RPGBossTrack::WatchdogTimeoutSeconds(1.65f,Bad)<0.);
    }
    return true;
}
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FFrameworkPhaseSupersedesProfile,"OneBossFight.Framework.Runtime.PhaseSupersedesProfile",EAutomationTestFlags::EditorContext|EAutomationTestFlags::ProductFilter)
bool FFrameworkPhaseSupersedesProfile::RunTest(const FString&)
{
    // BOSS-EXE-005: the opt-in needs the F5 lane, posture and a phase two threshold.
    using namespace FrameworkRuntimeFixture;
    TStrongObjectPtr<URPGBossFrameworkProfile> P(NewObject<URPGBossFrameworkProfile>());FString Error;
    auto F5=[&](){Fill(*P);P->FixtureLabel=TEXT("F5 fixture");P->bDamageEnabled=true;P->HitStepCm=15.f;P->HitMaxSubsteps=8;P->RepeatPenalty=.2f;P->RepeatMemory=2;P->AttackCount=2;
        FRPGBossProfileCard C;C.Card=P->Card;C.CooldownSeconds=1.f;C.Weight=1.f;P->Card.Reset();P->Cards.Reset();P->Cards.Add(C);P->bPhaseSupersedesStagger=false;};
    F5();P->bPhaseSupersedesStagger=true;TestFalse(TEXT("no posture and no phase two: refused"),RPGFramework::ValidateProfile(*P,Error));TestEqual(TEXT("token"),Error,FString(TEXT("Framework.Profile.Domain")));
    F5();TestTrue(TEXT("off by default: valid"),RPGFramework::ValidateProfile(*P,Error));
    return true;
}
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FFrameworkTurnLatch,"OneBossFight.Framework.Runtime.TurnLatch",EAutomationTestFlags::EditorContext|EAutomationTestFlags::ProductFilter)
bool FFrameworkTurnLatch::RunTest(const FString&)
{
    // BOSS-MOV-003: a target flickering across the back axis (+170 / -170 relative to a boss at yaw 0) must not make the turn reverse every tick.
    const float Tick=1.f/60.f;
    auto Run=[&](bool bLatch,float& EndYaw){RPGBossTrack::FTurnLatch L;float Yaw=0.f;for(int32 I=0;I<40;++I){Yaw=RPGBossTrack::StepYawLatched(Yaw,(I%2==0)?170.f:-170.f,180.f,Tick,false,L,bLatch);}EndYaw=Yaw;return L.Flips;};
    float EndOn=0.f,EndOff=0.f;const int32 FlipsOn=Run(true,EndOn),FlipsOff=Run(false,EndOff);
    TestEqual(TEXT("latched: no direction change while the target flickers across the back axis"),FlipsOn,0);
    TestTrue(TEXT("unlatched control: it reverses on most ticks"),FlipsOff>=30);
    TestTrue(TEXT("latched turn made real progress (3 deg per tick, 40 ticks = 120 deg)"),FMath::IsNearlyEqual(EndOn,120.f,.01f));
    TestTrue(TEXT("unlatched control barely moves"),FMath::Abs(EndOff)<10.f);
    // A target that really crosses to the other side (90 deg off the back axis) releases the latch.
    {RPGBossTrack::FTurnLatch L;float Yaw=0.f;Yaw=RPGBossTrack::StepYawLatched(Yaw,170.f,180.f,Tick,false,L);TestEqual(TEXT("started turning +"),L.Dir,1);
     Yaw=RPGBossTrack::StepYawLatched(Yaw,-90.f,180.f,Tick,false,L);TestEqual(TEXT("a real crossing turns the other way"),L.Dir,-1);TestEqual(TEXT("and counts as one change"),L.Flips,1);}
    // Reaching the target ends the turn and clears the latch; committed / bad input never turn.
    {RPGBossTrack::FTurnLatch L;float Yaw=RPGBossTrack::StepYawLatched(0.f,1.f,180.f,Tick,false,L);TestTrue(TEXT("inside one step the target is reached exactly"),FMath::IsNearlyEqual(Yaw,1.f,.001f));TestEqual(TEXT("latch cleared"),L.Dir,0);
     TestEqual(TEXT("committed never turns"),RPGBossTrack::StepYawLatched(30.f,200.f,90.f,1.f,true,L),30.f);
     TestEqual(TEXT("zero rate never turns"),RPGBossTrack::StepYawLatched(30.f,200.f,0.f,1.f,false,L),30.f);}
    return true;
}
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FFrameworkHyperArmor,"OneBossFight.Framework.Runtime.HyperArmor",EAutomationTestFlags::EditorContext|EAutomationTestFlags::ProductFilter)
bool FFrameworkHyperArmor::RunTest(const FString&)
{
    // BOSS-DEF-004: armor needs BOTH an armored card and the Active state.
    TestTrue(TEXT("armored card, active state: absorbed"),RPGBossRules::HyperArmorActive(true,true));
    TestFalse(TEXT("armored card, not active (commit / recovery / neutral): the hit counts"),RPGBossRules::HyperArmorActive(true,false));
    TestFalse(TEXT("plain card, active state: the hit counts"),RPGBossRules::HyperArmorActive(false,true));
    TestFalse(TEXT("plain card, not active: the hit counts"),RPGBossRules::HyperArmorActive(false,false));
    // The profile flag defaults to false and a card entry with armor stays valid.
    FRPGBossProfileCard Entry;TestFalse(TEXT("default is off"),Entry.bHyperArmor);
    return true;
}
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FFrameworkCenterBias,"OneBossFight.Framework.Runtime.CenterBias",EAutomationTestFlags::EditorContext|EAutomationTestFlags::ProductFilter)
bool FFrameworkCenterBias::RunTest(const FString&)
{
    // BOSS-MOV-002: the boss stands on the wall side (Away = -X), the centre lies +X from the target.
    const FVector Away(-1.,0.,0.),ToCenter(300.,0.,0.);
    auto Near=[&](const TCHAR* W,const FVector& V,double X,double Y){TestTrue(W,FMath::IsNearlyEqual(V.X,X,1.e-4)&&FMath::IsNearlyEqual(V.Y,Y,1.e-4));};
    Near(TEXT("bias 0 keeps the way the boss stands"),RPGBossTrack::CenterBiasedAway(Away,ToCenter,0.f),-1.,0.);
    Near(TEXT("bias 1 goes to the centre side"),RPGBossTrack::CenterBiasedAway(Away,ToCenter,1.f),1.,0.);
    Near(TEXT("bias above 1 is clamped"),RPGBossTrack::CenterBiasedAway(Away,ToCenter,5.f),1.,0.);
    Near(TEXT("half way between two perpendicular ways"),RPGBossTrack::CenterBiasedAway(FVector(0.,-1.,0.),FVector(1.,0.,0.),.5f),FMath::Sqrt(.5),-FMath::Sqrt(.5));
    Near(TEXT("opposite ways that cancel fall back to Away"),RPGBossTrack::CenterBiasedAway(Away,ToCenter,.5f),-1.,0.);
    Near(TEXT("no centre direction falls back to Away"),RPGBossTrack::CenterBiasedAway(Away,FVector::ZeroVector,1.f),-1.,0.);
    Near(TEXT("NaN bias falls back to Away"),RPGBossTrack::CenterBiasedAway(Away,ToCenter,std::numeric_limits<float>::quiet_NaN()),-1.,0.);
    // Profile domain: the bias needs an arena radius; fractions and bias are bounded.
    using namespace FrameworkRuntimeFixture;
    TStrongObjectPtr<URPGBossFrameworkProfile> P(NewObject<URPGBossFrameworkProfile>());FString Error;
    auto F5=[&](){Fill(*P);P->FixtureLabel=TEXT("F5 fixture");P->bDamageEnabled=true;P->HitStepCm=15.f;P->HitMaxSubsteps=8;P->RepeatPenalty=.2f;P->RepeatMemory=2;P->AttackCount=2;
        FRPGBossProfileCard C;C.Card=P->Card;C.CooldownSeconds=1.f;C.Weight=1.f;P->Card.Reset();P->Cards.Reset();P->Cards.Add(C);P->ArenaRadiusCm=300.f;P->ArenaCenterBias=0.f;P->CenterBiasStartFraction=.5f;P->bArenaCenterAuthored=false;};
    F5();P->ArenaCenterBias=1.f;TestTrue(TEXT("bias 1 with a radius is valid"),RPGFramework::ValidateProfile(*P,Error));
    for(float V:{-.1f,1.01f,std::numeric_limits<float>::quiet_NaN()}){F5();P->ArenaCenterBias=V;TestFalse(TEXT("bias outside 0..1 refused"),RPGFramework::ValidateProfile(*P,Error));}
    for(float V:{0.f,-.5f,1.01f}){F5();P->ArenaCenterBias=.5f;P->CenterBiasStartFraction=V;TestFalse(TEXT("start fraction outside (0,1] refused"),RPGFramework::ValidateProfile(*P,Error));}
    F5();P->ArenaRadiusCm=0.f;P->ArenaCenterBias=.5f;TestFalse(TEXT("bias without a radius refused"),RPGFramework::ValidateProfile(*P,Error));TestEqual(TEXT("token"),Error,FString(TEXT("Framework.Profile.Domain")));
    F5();P->bArenaCenterAuthored=true;P->ArenaCenter=FVector(250.,0.,0.);TestTrue(TEXT("authored centre with a radius is valid"),RPGFramework::ValidateProfile(*P,Error));
    F5();P->ArenaRadiusCm=0.f;P->bArenaCenterAuthored=true;TestFalse(TEXT("authored centre without a radius refused"),RPGFramework::ValidateProfile(*P,Error));
    return true;
}
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FFrameworkAntiCheeseProfile,"OneBossFight.Framework.Runtime.AntiCheeseProfile",EAutomationTestFlags::EditorContext|EAutomationTestFlags::ProductFilter)
bool FFrameworkAntiCheeseProfile::RunTest(const FString&)
{
    // BOSS-PHS-005: profile domain of the kiting / hugging detector and the per-card multipliers.
    using namespace FrameworkRuntimeFixture;
    TStrongObjectPtr<URPGBossFrameworkProfile> P(NewObject<URPGBossFrameworkProfile>());FString Error;
    auto F5=[&](){Fill(*P);P->FixtureLabel=TEXT("F5 fixture");P->bDamageEnabled=true;P->HitStepCm=15.f;P->HitMaxSubsteps=8;P->RepeatPenalty=.2f;P->RepeatMemory=2;P->AttackCount=2;
        FRPGBossProfileCard C;C.Card=P->Card;C.CooldownSeconds=1.f;C.Weight=1.f;P->Card.Reset();P->Cards.Reset();P->Cards.Add(C);P->AntiCheeseKiteRangeCm=0.f;P->AntiCheeseHugRangeCm=0.f;P->AntiCheeseStreak=2;};
    F5();TestTrue(TEXT("off by default: valid"),RPGFramework::ValidateProfile(*P,Error));
    F5();P->AntiCheeseKiteRangeCm=150.f;P->AntiCheeseHugRangeCm=60.f;P->Cards[0].KiteWeightMultiplier=2.f;P->Cards[0].HugWeightMultiplier=3.f;TestTrue(TEXT("kite 150, hug 60, multipliers valid"),RPGFramework::ValidateProfile(*P,Error));
    F5();P->AntiCheeseKiteRangeCm=150.f;P->AntiCheeseHugRangeCm=150.f;TestFalse(TEXT("hug threshold must be below the kite threshold"),RPGFramework::ValidateProfile(*P,Error));
    for(int32 V:{0,9,-1}){F5();P->AntiCheeseKiteRangeCm=150.f;P->AntiCheeseStreak=V;TestFalse(TEXT("streak outside 1..8 refused"),RPGFramework::ValidateProfile(*P,Error));}
    for(float V:{-1.f,std::numeric_limits<float>::quiet_NaN(),2.e5f}){F5();P->AntiCheeseKiteRangeCm=V;TestFalse(TEXT("bad kite range refused"),RPGFramework::ValidateProfile(*P,Error));}
    for(float V:{0.f,-1.f,101.f,std::numeric_limits<float>::quiet_NaN()}){F5();P->Cards[0].KiteWeightMultiplier=V;TestFalse(TEXT("multiplier outside (0,100] refused"),RPGFramework::ValidateProfile(*P,Error));}
    {TStrongObjectPtr<URPGBossFrameworkProfile> F3(NewObject<URPGBossFrameworkProfile>());Fill(*F3);F3->AntiCheeseKiteRangeCm=150.f;TestFalse(TEXT("outside the F5 lane refused"),RPGFramework::ValidateProfile(*F3,Error));}
    return true;
}
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FFrameworkReactionDelay,"OneBossFight.Framework.Runtime.ReactionDelay",EAutomationTestFlags::EditorContext|EAutomationTestFlags::ProductFilter)
bool FFrameworkReactionDelay::RunTest(const FString&)
{
    // BOSS-SEL-009: every drawn latency lies in the window; the draw is deterministic for a seed and count; bad windows are invalid.
    double Lo=1.e9,Hi=-1.e9;bool bInside=true;
    for(int32 Seed=0;Seed<200;++Seed)for(int32 Count=0;Count<5;++Count){const double L=RPGBossTrack::ReactionDelaySeconds(.2f,.4f,Seed,Count);bInside=bInside&&L>=.2&&L<=.4;Lo=FMath::Min(Lo,L);Hi=FMath::Max(Hi,L);}
    TestTrue(TEXT("1000 draws inside [0.2, 0.4]"),bInside);
    TestTrue(TEXT("the draws spread over the window (not a constant)"),Hi-Lo>.15);
    TestEqual(TEXT("deterministic for a seed and count"),RPGBossTrack::ReactionDelaySeconds(.2f,.4f,5,0),RPGBossTrack::ReactionDelaySeconds(.2f,.4f,5,0));
    TestTrue(TEXT("the count changes the draw"),RPGBossTrack::ReactionDelaySeconds(.2f,.4f,5,0)!=RPGBossTrack::ReactionDelaySeconds(.2f,.4f,5,1));
    TestEqual(TEXT("min == max is exactly that value"),RPGBossTrack::ReactionDelaySeconds(.3f,.3f,9,2),.3,1.e-6);
    for(const TPair<float,float>& Bad:{TPair<float,float>(0.f,.4f),TPair<float,float>(.5f,.4f),TPair<float,float>(.2f,6.f),TPair<float,float>(-.1f,.4f),TPair<float,float>(.2f,std::numeric_limits<float>::quiet_NaN())})
        TestTrue(TEXT("bad window is invalid"),RPGBossTrack::ReactionDelaySeconds(Bad.Key,Bad.Value,1,0)<0.);
    // Profile domain: both 0 = off; otherwise a valid window in the F5 lane.
    using namespace FrameworkRuntimeFixture;
    TStrongObjectPtr<URPGBossFrameworkProfile> P(NewObject<URPGBossFrameworkProfile>());FString Error;
    auto F5=[&](){Fill(*P);P->FixtureLabel=TEXT("F5 fixture");P->bDamageEnabled=true;P->HitStepCm=15.f;P->HitMaxSubsteps=8;P->RepeatPenalty=.2f;P->RepeatMemory=2;P->AttackCount=2;
        FRPGBossProfileCard C;C.Card=P->Card;C.CooldownSeconds=1.f;C.Weight=1.f;P->Card.Reset();P->Cards.Reset();P->Cards.Add(C);P->ReactionDelayMinSeconds=0.f;P->ReactionDelayMaxSeconds=0.f;};
    F5();TestTrue(TEXT("off by default"),RPGFramework::ValidateProfile(*P,Error));
    F5();P->ReactionDelayMinSeconds=.2f;P->ReactionDelayMaxSeconds=.4f;TestTrue(TEXT("0.2..0.4 valid"),RPGFramework::ValidateProfile(*P,Error));
    F5();P->ReactionDelayMinSeconds=.5f;P->ReactionDelayMaxSeconds=.4f;TestFalse(TEXT("min above max refused"),RPGFramework::ValidateProfile(*P,Error));TestEqual(TEXT("token"),Error,FString(TEXT("Framework.Profile.Domain")));
    F5();P->ReactionDelayMaxSeconds=.4f;TestFalse(TEXT("max without min refused"),RPGFramework::ValidateProfile(*P,Error));
    {TStrongObjectPtr<URPGBossFrameworkProfile> F3(NewObject<URPGBossFrameworkProfile>());Fill(*F3);F3->ReactionDelayMinSeconds=.2f;F3->ReactionDelayMaxSeconds=.4f;TestFalse(TEXT("outside the F5 lane refused"),RPGFramework::ValidateProfile(*F3,Error));}
    return true;
}
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FFrameworkLosMemory,"OneBossFight.Framework.Runtime.LosMemory",EAutomationTestFlags::EditorContext|EAutomationTestFlags::ProductFilter)
bool FFrameworkLosMemory::RunTest(const FString&)
{
    // BOSS-AWR-007: the memory rule. Sight lost at t=1 (last seen at (10,0,0)), regained at t=2.5; or the search runs out after 3 s.
    using namespace RPGBossTrack;
    FLosMemory M;
    TestTrue(TEXT("seen: nothing to report"),LosStep(M,true,0.,3.,FVector(10.,0.,0.))==ELosEvent::None);
    TestTrue(TEXT("sight lost"),LosStep(M,false,1.,3.,FVector(500.,0.,0.))==ELosEvent::Lost);
    TestTrue(TEXT("the last known position is the one of the last VISIBLE tick, not the hidden target"),M.LastKnown.Equals(FVector(10.,0.,0.)));
    TestTrue(TEXT("still searching: nothing new"),LosStep(M,false,2.,3.,FVector(600.,0.,0.))==ELosEvent::None);
    TestTrue(TEXT("sight regained"),LosStep(M,true,2.5,3.,FVector(20.,0.,0.))==ELosEvent::Regained);
    TestTrue(TEXT("memory refreshed at regain"),M.LastKnown.Equals(FVector(20.,0.,0.))&&!M.bLost);
    FLosMemory N;LosStep(N,true,0.,3.,FVector::ZeroVector);LosStep(N,false,1.,3.,FVector::ZeroVector);
    TestTrue(TEXT("2.99 s: not yet"),LosStep(N,false,3.99,3.,FVector::ZeroVector)==ELosEvent::None);
    TestTrue(TEXT("3.0 s: the search times out"),LosStep(N,false,4.,3.,FVector::ZeroVector)==ELosEvent::TimedOut);
    TestTrue(TEXT("and it is reported once"),LosStep(N,false,5.,3.,FVector::ZeroVector)==ELosEvent::None);
    TestTrue(TEXT("sight after a timeout is still a regain"),LosStep(N,true,6.,3.,FVector::ZeroVector)==ELosEvent::Regained);
    // Profile domain: 0 off, (0,30] valid, in the F5 lane.
    using namespace FrameworkRuntimeFixture;
    TStrongObjectPtr<URPGBossFrameworkProfile> P(NewObject<URPGBossFrameworkProfile>());FString Error;
    auto F5=[&](){Fill(*P);P->FixtureLabel=TEXT("F5 fixture");P->bDamageEnabled=true;P->HitStepCm=15.f;P->HitMaxSubsteps=8;P->RepeatPenalty=.2f;P->RepeatMemory=2;P->AttackCount=2;
        FRPGBossProfileCard C;C.Card=P->Card;C.CooldownSeconds=1.f;C.Weight=1.f;P->Card.Reset();P->Cards.Reset();P->Cards.Add(C);P->LosSearchSeconds=0.f;};
    F5();TestTrue(TEXT("off by default"),RPGFramework::ValidateProfile(*P,Error));
    for(float V:{.5f,3.f,30.f}){F5();P->LosSearchSeconds=V;TestTrue(TEXT("(0,30] valid"),RPGFramework::ValidateProfile(*P,Error));}
    for(float V:{-1.f,30.01f,std::numeric_limits<float>::quiet_NaN()}){F5();P->LosSearchSeconds=V;TestFalse(TEXT("outside (0,30] refused"),RPGFramework::ValidateProfile(*P,Error));}
    {TStrongObjectPtr<URPGBossFrameworkProfile> F3(NewObject<URPGBossFrameworkProfile>());Fill(*F3);F3->LosSearchSeconds=3.f;TestFalse(TEXT("outside the F5 lane refused"),RPGFramework::ValidateProfile(*F3,Error));}
    return true;
}
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FFrameworkSweptAnnulus,"OneBossFight.Framework.Runtime.SweptAnnulus",EAutomationTestFlags::EditorContext|EAutomationTestFlags::ProductFilter)
bool FFrameworkSweptAnnulus::RunTest(const FString&)
{
    // BOSS-HIT-011: the ring rule. Front = 60 + 400 t, band 40 cm thick, wave 50 cm high, target capsule radius 35 cm.
    using namespace RPGBossTrack;
    TestTrue(TEXT("front at t=0.5"),FMath::IsNearlyEqual(RingFront(60.,400.,.5),260.));
    TestTrue(TEXT("target inside the band"),RingTouches(240.,260.,40.,230.,35.,0.,50.));
    TestFalse(TEXT("target beyond the front"),RingTouches(240.,260.,40.,330.,35.,0.,50.));
    TestFalse(TEXT("target the band has already passed (no ghost damage)"),RingTouches(240.,260.,40.,100.,35.,0.,50.));
    TestFalse(TEXT("a target above the wave is missed"),RingTouches(240.,260.,40.,230.,35.,80.,50.));
    TestFalse(TEXT("NaN refused"),RingTouches(240.,260.,40.,std::numeric_limits<double>::quiet_NaN(),35.,0.,50.));
    // No invisible gaps: a target at ANY distance between the start and the end front is touched by exactly the tick whose span contains it, whatever the frame time.
    for (const double Dt:{1./240.,1./60.,1./30.,.2})
    {
        for (double D=60.;D<=460.;D+=1.7)
        {
            int32 Touched=0;
            for (double T=0.;T<1.;T+=Dt)
                if (RingTouches(RingFront(60.,400.,T),RingFront(60.,400.,FMath::Min(T+Dt,1.)),40.,D,0.,0.,50.)) ++Touched;
            if (Touched<1) {AddError(FString::Printf(TEXT("gap at dist %g with dt %g"),D,Dt));break;}
        }
    }
    return true;
}
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FFrameworkGrabFailSafe,"OneBossFight.Framework.Runtime.GrabFailSafe",EAutomationTestFlags::EditorContext|EAutomationTestFlags::ProductFilter)
bool FFrameworkGrabFailSafe::RunTest(const FString&)
{
    // BOSS-HIT-012: the hold rule. Catch at a contact, release at the release time, or AT ONCE on any interrupt; one catch per hold; the victim ends on the floor.
    using namespace RPGBossTrack;
    FGrabState S;
    TestTrue(TEXT("no contact: nothing"),GrabStep(S,false,.5,1.,false)==EGrabEvent::None&&!S.bHeld);
    TestTrue(TEXT("contact catches"),GrabStep(S,true,.5,1.,false)==EGrabEvent::Caught&&S.bHeld);
    TestTrue(TEXT("a second contact while held changes nothing"),GrabStep(S,true,.6,9.,false)==EGrabEvent::None&&S.ReleaseAt==1.);
    TestTrue(TEXT("before the release time: held"),GrabStep(S,false,.99,0.,false)==EGrabEvent::None&&S.bHeld);
    TestTrue(TEXT("at the release time: released"),GrabStep(S,false,1.,0.,false)==EGrabEvent::Released&&!S.bHeld);
    GrabStep(S,true,.5,1.,false);
    TestTrue(TEXT("an interrupt before the release time frees the victim at once"),GrabStep(S,false,.6,0.,true)==EGrabEvent::Interrupted&&!S.bHeld);
    TestTrue(TEXT("nothing is caught during an interrupt"),GrabStep(S,true,.7,1.,true)==EGrabEvent::None&&!S.bHeld);
    TestTrue(TEXT("a non finite release time never catches"),GrabStep(S,true,.7,std::numeric_limits<double>::quiet_NaN(),false)==EGrabEvent::None&&!S.bHeld);
    TestTrue(TEXT("grounded: capsule centre above the floor by half height and skin"),FMath::IsNearlyEqual(GroundedZ(10.,90.,2.),102.));
    return true;
}
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FFrameworkBoundedWarp,"OneBossFight.Framework.Runtime.BoundedWarp",EAutomationTestFlags::EditorContext|EAutomationTestFlags::ProductFilter)
bool FFrameworkBoundedWarp::RunTest(const FString&)
{
    // BOSS-ANM-006: the warp never exceeds its budgets, whatever is needed and however the window is cut into ticks; with room in the budget it ends exactly at the need.
    using namespace RPGBossTrack;
    TestTrue(TEXT("a tick that is half of the time left covers half of the need"),FMath::IsNearlyEqual(WarpStepCm(100.,150.,.1,.2),50.));
    TestTrue(TEXT("the budget caps the step"),FMath::IsNearlyEqual(WarpStepCm(400.,30.,.2,.2),30.));
    TestTrue(TEXT("nothing needed, nothing spent, no time"),WarpStepCm(0.,150.,.1,.2)==0.&&WarpStepCm(10.,0.,.1,.2)==0.&&WarpStepCm(10.,150.,0.,.2)==0.&&WarpStepCm(10.,150.,.1,0.)==0.);
    TestTrue(TEXT("NaN and infinity do nothing"),WarpStepCm(std::numeric_limits<double>::quiet_NaN(),150.,.1,.2)==0.&&WarpStepCm(std::numeric_limits<double>::infinity(),150.,.1,.2)==0.&&WarpStepDegrees(std::numeric_limits<double>::quiet_NaN(),45.,.1,.2)==0.);
    TestTrue(TEXT("the angle keeps its sign"),WarpStepDegrees(-90.,45.,.2,.2)==-45.&&WarpStepDegrees(30.,45.,.2,.2)==30.);
    for (const double Dt:{1./240.,1./60.,1./30.,.1})
        for (const double Need:{20.,148.,150.,151.,600.})
        {
            double Moved=0.;
            for (double T=0.;T<.4-1e-9;T+=Dt) Moved+=WarpStepCm(Need-Moved,150.-Moved,FMath::Min(Dt,.4-T),.4-T);   // the executor recomputes what is still needed every tick
            if (Moved>150.+1e-6) AddError(FString::Printf(TEXT("budget exceeded: need %g dt %g moved %g"),Need,Dt,Moved));
            if (Need<=150.&&!FMath::IsNearlyEqual(Moved,Need,1e-6)) AddError(FString::Printf(TEXT("did not end at the need: need %g dt %g moved %g"),Need,Dt,Moved));
        }
    return true;
}
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FFrameworkDodgeHistory,"OneBossFight.Framework.Runtime.DodgeHistory",EAutomationTestFlags::EditorContext|EAutomationTestFlags::ProductFilter)
bool FFrameworkDodgeHistory::RunTest(const FString&)
{
    // BOSS-AWR-008: classification of a dodge seen from the boss (the target stands +X of the boss), the history ring, and the profile domain.
    using namespace RPGBossTrack;
    const FVector ToTarget(100.,0.,0.);
    TestTrue(TEXT("moving away fast = Back"),ClassifyDodge(FVector(900.,0.,0.),ToTarget,600.f)==EDodgeDir::Back);
    TestTrue(TEXT("moving toward the boss = Forward"),ClassifyDodge(FVector(-900.,0.,0.),ToTarget,600.f)==EDodgeDir::Forward);
    TestTrue(TEXT("moving sideways = Side"),ClassifyDodge(FVector(0.,900.,0.),ToTarget,600.f)==EDodgeDir::Side);
    TestTrue(TEXT("60 degrees off the back axis is still Back (dot 0.5)"),ClassifyDodge(FVector(450.,779.4,0.),ToTarget,600.f)==EDodgeDir::Back);
    TestTrue(TEXT("below the speed threshold = None"),ClassifyDodge(FVector(500.,0.,0.),ToTarget,600.f)==EDodgeDir::None);
    TestTrue(TEXT("vertical speed does not count"),ClassifyDodge(FVector(0.,0.,2000.),ToTarget,600.f)==EDodgeDir::None);
    TestTrue(TEXT("no direction to the target = None"),ClassifyDodge(FVector(900.,0.,0.),FVector::ZeroVector,600.f)==EDodgeDir::None);
    TestTrue(TEXT("bad threshold = None"),ClassifyDodge(FVector(900.,0.,0.),ToTarget,-1.f)==EDodgeDir::None&&ClassifyDodge(FVector(900.,0.,0.),ToTarget,std::numeric_limits<float>::quiet_NaN())==EDodgeDir::None);
    FDodgeHistory H;H.Push(EDodgeDir::Back,3);H.Push(EDodgeDir::Side,3);TestEqual(TEXT("one back of two"),H.BackCount(),1);
    H.Push(EDodgeDir::Back,3);TestEqual(TEXT("two backs of three"),H.BackCount(),2);
    H.Push(EDodgeDir::Forward,3);TestEqual(TEXT("depth 3: the oldest (Back) fell out"),H.BackCount(),1);TestEqual(TEXT("ring size"),H.Dirs.Num(),3);
    H.Push(EDodgeDir::None,3);TestEqual(TEXT("None is not recorded"),H.Dirs.Num(),3);
    using namespace FrameworkRuntimeFixture;
    TStrongObjectPtr<URPGBossFrameworkProfile> P(NewObject<URPGBossFrameworkProfile>());FString Error;
    auto F5=[&](){Fill(*P);P->FixtureLabel=TEXT("F5 fixture");P->bDamageEnabled=true;P->HitStepCm=15.f;P->HitMaxSubsteps=8;P->RepeatPenalty=.2f;P->RepeatMemory=2;P->AttackCount=2;
        FRPGBossProfileCard C;C.Card=P->Card;C.CooldownSeconds=1.f;C.Weight=1.f;P->Card.Reset();P->Cards.Reset();P->Cards.Add(C);P->DodgeHistoryDepth=0;P->DodgeBackThreshold=2;P->DodgeSpeedCm=600.f;};
    F5();TestTrue(TEXT("off by default"),RPGFramework::ValidateProfile(*P,Error));
    F5();P->DodgeHistoryDepth=3;TestTrue(TEXT("depth 3 threshold 2 valid"),RPGFramework::ValidateProfile(*P,Error));
    for(int32 V:{-1,9}){F5();P->DodgeHistoryDepth=V;TestFalse(TEXT("depth outside 0..8 refused"),RPGFramework::ValidateProfile(*P,Error));}
    F5();P->DodgeHistoryDepth=3;P->DodgeBackThreshold=4;TestFalse(TEXT("threshold above the depth refused"),RPGFramework::ValidateProfile(*P,Error));
    F5();P->DodgeHistoryDepth=3;P->DodgeBackThreshold=0;TestFalse(TEXT("threshold 0 refused"),RPGFramework::ValidateProfile(*P,Error));
    for(float V:{0.f,-1.f,std::numeric_limits<float>::quiet_NaN()}){F5();P->DodgeHistoryDepth=3;P->DodgeSpeedCm=V;TestFalse(TEXT("bad speed refused"),RPGFramework::ValidateProfile(*P,Error));}
    {TStrongObjectPtr<URPGBossFrameworkProfile> F3(NewObject<URPGBossFrameworkProfile>());Fill(*F3);F3->DodgeHistoryDepth=3;TestFalse(TEXT("outside the F5 lane refused"),RPGFramework::ValidateProfile(*F3,Error));}
    return true;
}
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FFrameworkArenaProfile,"OneBossFight.Framework.Runtime.ArenaProfile",EAutomationTestFlags::EditorContext|EAutomationTestFlags::ProductFilter)
bool FFrameworkArenaProfile::RunTest(const FString&)
{
    using namespace FrameworkRuntimeFixture;
    TStrongObjectPtr<URPGBossFrameworkProfile> P(NewObject<URPGBossFrameworkProfile>());FString Error;
    auto F5=[&](){Fill(*P);P->FixtureLabel=TEXT("F5 fixture");P->bDamageEnabled=true;P->HitStepCm=15.f;P->HitMaxSubsteps=8;P->RepeatPenalty=.2f;P->RepeatMemory=2;P->AttackCount=2;
        FRPGBossProfileCard C;C.Card=P->Card;C.CooldownSeconds=1.f;C.Weight=1.f;P->Card.Reset();P->Cards.Reset();P->Cards.Add(C);P->ArenaRadiusCm=0.f;};
    F5();TestTrue(TEXT("off by default: valid"),RPGFramework::ValidateProfile(*P,Error));
    for(float V:{1.f,600.f,1.e6f}){F5();P->ArenaRadiusCm=V;TestTrue(TEXT("(0,1e6] valid"),RPGFramework::ValidateProfile(*P,Error));}
    for(float V:{-1.f,1.0001e6f,std::numeric_limits<float>::quiet_NaN(),std::numeric_limits<float>::infinity()}){F5();P->ArenaRadiusCm=V;TestFalse(TEXT("outside [0,1e6] or non-finite refused"),RPGFramework::ValidateProfile(*P,Error));TestEqual(TEXT("token"),Error,FString(TEXT("Framework.Profile.Domain")));}
    F5();P->bArenaLeash=true;TestFalse(TEXT("leash without an arena radius refused"),RPGFramework::ValidateProfile(*P,Error));TestEqual(TEXT("token"),Error,FString(TEXT("Framework.Profile.Domain")));
    F5();P->ArenaRadiusCm=250.f;P->bArenaLeash=true;TestTrue(TEXT("leash with an arena radius is valid"),RPGFramework::ValidateProfile(*P,Error));
    {TStrongObjectPtr<URPGBossFrameworkProfile> F3(NewObject<URPGBossFrameworkProfile>());Fill(*F3);F3->ArenaRadiusCm=600.f;TestFalse(TEXT("outside the F5 lane refused"),RPGFramework::ValidateProfile(*F3,Error));TestEqual(TEXT("token"),Error,FString(TEXT("Framework.Profile.Domain")));}
    return true;
}
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FFrameworkStaggerAnimRules,"OneBossFight.Framework.Runtime.StaggerAnimRules",EAutomationTestFlags::EditorContext|EAutomationTestFlags::ProductFilter)
bool FFrameworkStaggerAnimRules::RunTest(const FString&)
{
    // F11 pure rules (spec Antigravity/Reviews/F11_STAGGER_PHASE_ANIM_SPEC.md). Hand values: Start 0.8 s, End 0.6 s, Total 3.0 s -> End starts at 2.4 s, middle 1.6 s.
    using RPGStaggerAnim::EState;
    const float S=.8f,E=.6f,T=3.f;
    TestTrue(TEXT("t=0 Start"),RPGStaggerAnim::Evaluate(S,E,T,0.f)==EState::Start);
    TestTrue(TEXT("t=0.79 Start"),RPGStaggerAnim::Evaluate(S,E,T,.79f)==EState::Start);
    TestTrue(TEXT("t=0.80 Loop"),RPGStaggerAnim::Evaluate(S,E,T,.8f)==EState::Loop);
    TestTrue(TEXT("t=2.39 Loop"),RPGStaggerAnim::Evaluate(S,E,T,2.39f)==EState::Loop);
    TestTrue(TEXT("t=2.40 End"),RPGStaggerAnim::Evaluate(S,E,T,2.4f)==EState::End);
    TestTrue(TEXT("t=2.99 End"),RPGStaggerAnim::Evaluate(S,E,T,2.99f)==EState::End);
    TestTrue(TEXT("t=3.00 Finished"),RPGStaggerAnim::Evaluate(S,E,T,3.f)==EState::Finished);
    TestEqual(TEXT("loop count middle 1.6 / loop 0.5 = ceil 3.2 = 4"),RPGStaggerAnim::LoopCount(T,S,E,.5f),4);
    TestEqual(TEXT("loop count exact 1.6 / 0.8 = 2"),RPGStaggerAnim::LoopCount(T,S,E,.8f),2);
    TestEqual(TEXT("no middle, no loop"),RPGStaggerAnim::LoopCount(1.4f,S,E,.5f),0);
    TestEqual(TEXT("loop length zero, no loop"),RPGStaggerAnim::LoopCount(T,S,E,0.f),0);
    TestTrue(TEXT("phase hold at 1.99 of 2.0"),RPGStaggerAnim::PhaseHoldActive(2.f,1.99f));
    TestFalse(TEXT("phase hold over at 2.0"),RPGStaggerAnim::PhaseHoldActive(2.f,2.f));
    TestFalse(TEXT("no clip = no hold"),RPGStaggerAnim::PhaseHoldActive(0.f,0.f));
    TestFalse(TEXT("NaN clip length does not hold"),RPGStaggerAnim::PhaseHoldActive(std::numeric_limits<float>::quiet_NaN(),0.f));
    TestFalse(TEXT("infinite elapsed does not hold"),RPGStaggerAnim::PhaseHoldActive(2.f,std::numeric_limits<float>::infinity()));
    TestTrue(TEXT("NaN elapsed fails closed to Finished"),RPGStaggerAnim::Evaluate(S,E,T,std::numeric_limits<float>::quiet_NaN())==EState::Finished);
    TestTrue(TEXT("infinite elapsed fails closed to Finished"),RPGStaggerAnim::Evaluate(S,E,T,std::numeric_limits<float>::infinity())==EState::Finished);
    TestEqual(TEXT("infinite loop duration does not overflow count"),RPGStaggerAnim::LoopCount(T,S,E,std::numeric_limits<float>::infinity()),0);
    TestEqual(TEXT("oversized loop count fails closed"),RPGStaggerAnim::LoopCount(1.e30f,0.f,0.f,1.e-30f),0);
    RPGStaggerAnim::FPureParams P;P.BossSkeleton=P.StartSkeleton=P.LoopSkeleton=P.EndSkeleton=TEXT("SkeletonBoss");P.Slot=TEXT("FullBody");P.StartLen=S;P.LoopLen=.5f;P.EndLen=E;P.Total=T;P.bStart=P.bLoop=P.bEnd=true;
    TestTrue(TEXT("valid set"),RPGStaggerAnim::Validate(P).IsEmpty());
    RPGStaggerAnim::FPureParams None;TestTrue(TEXT("no clips = off = valid"),RPGStaggerAnim::Validate(None).IsEmpty());
    auto Token=[&](TFunction<void(RPGStaggerAnim::FPureParams&)> Edit){RPGStaggerAnim::FPureParams X=P;Edit(X);return RPGStaggerAnim::Validate(X);};
    TestEqual(TEXT("NaN stagger length is rejected"),Token([](auto& X){X.Total=std::numeric_limits<float>::quiet_NaN();}),FString(TEXT("Framework.Profile.StaggerAnim.TooShort")));
    TestEqual(TEXT("incoherent set"),Token([](auto& X){X.bEnd=false;}),FString(TEXT("Framework.Profile.StaggerAnim.CoherentSet")));
    TestEqual(TEXT("start skeleton"),Token([](auto& X){X.StartSkeleton=TEXT("SkeletonOther");}),FString(TEXT("Framework.Profile.StaggerAnim.StartSkeleton")));
    TestEqual(TEXT("loop skeleton"),Token([](auto& X){X.LoopSkeleton=TEXT("SkeletonOther");}),FString(TEXT("Framework.Profile.StaggerAnim.LoopSkeleton")));
    TestEqual(TEXT("end skeleton"),Token([](auto& X){X.EndSkeleton=TEXT("SkeletonOther");}),FString(TEXT("Framework.Profile.StaggerAnim.EndSkeleton")));
    TestEqual(TEXT("empty slot"),Token([](auto& X){X.Slot=NAME_None;}),FString(TEXT("Framework.Profile.StaggerAnim.SlotNameEmpty")));
    TestEqual(TEXT("too short 1.8 + 1.5 > 3.0"),Token([](auto& X){X.StartLen=1.8f;X.EndLen=1.5f;}),FString(TEXT("Framework.Profile.StaggerAnim.TooShort")));
    TestTrue(TEXT("exactly fits is valid"),Token([](auto& X){X.StartLen=1.5f;X.EndLen=1.5f;}).IsEmpty());
    TestEqual(TEXT("zero loop length"),Token([](auto& X){X.LoopLen=0.f;}),FString(TEXT("Framework.Profile.StaggerAnim.TooShort")));
    TestEqual(TEXT("no slot node in the AnimBP"),Token([](auto& X){X.bSlotNodePresent=false;}),FString(TEXT("Framework.Profile.StaggerAnim.SlotNode")));
    TestTrue(TEXT("no phase clip = valid"),RPGStaggerAnim::ValidatePhaseClip(false,0.f,NAME_None,NAME_None,TEXT("A"),TEXT("B")).IsEmpty());
    TestEqual(TEXT("phaseless clip"),RPGStaggerAnim::ValidatePhaseClip(true,0.f,TEXT("P2"),TEXT("FullBody"),TEXT("A"),TEXT("A")),FString(TEXT("Framework.Profile.PhaseTransitionAnim.Phaseless")));
    TestEqual(TEXT("phase clip foreign skeleton"),RPGStaggerAnim::ValidatePhaseClip(true,.5f,TEXT("P2"),TEXT("FullBody"),TEXT("A"),TEXT("B")),FString(TEXT("Framework.Profile.PhaseTransitionAnim.Skeleton")));
    TestTrue(TEXT("valid phase clip"),RPGStaggerAnim::ValidatePhaseClip(true,.5f,TEXT("P2"),TEXT("FullBody"),TEXT("A"),TEXT("A")).IsEmpty());
    TestEqual(TEXT("phase fraction one is invalid"),RPGStaggerAnim::ValidatePhaseClip(true,1.f,TEXT("P2"),TEXT("FullBody"),TEXT("A"),TEXT("A")),FString(TEXT("Framework.Profile.PhaseTransitionAnim.Phaseless")));
    TestEqual(TEXT("NaN phase fraction is invalid"),RPGStaggerAnim::ValidatePhaseClip(true,std::numeric_limits<float>::quiet_NaN(),TEXT("P2"),TEXT("FullBody"),TEXT("A"),TEXT("A")),FString(TEXT("Framework.Profile.PhaseTransitionAnim.Phaseless")));
    return true;
}
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FFrameworkStaggerAnimProfile,"OneBossFight.Framework.Runtime.StaggerAnimProfile",EAutomationTestFlags::EditorContext|EAutomationTestFlags::ProductFilter)
bool FFrameworkStaggerAnimProfile::RunTest(const FString&)
{
    using namespace FrameworkRuntimeFixture;
    TStrongObjectPtr<URPGBossFrameworkProfile> P(NewObject<URPGBossFrameworkProfile>());FString Error;
    const TCHAR* Dir=TEXT("/Game/ParagonSevarog/Characters/Heroes/Sevarog/Animations/");
    auto Clip=[Dir](const TCHAR* Name){return TSoftObjectPtr<UAnimSequence>(FSoftObjectPath(FString::Printf(TEXT("%s%s.%s"),Dir,Name,Name)));};
    auto Postured=[&](){Fill(*P);P->StaggerStartAnim.Reset();P->StaggerLoopAnim.Reset();P->StaggerEndAnim.Reset();P->PhaseTransitionAnim.Reset();P->AnimSlotName=TEXT("FullBody");P->PhaseTwoFraction=0.f;P->PhaseTwoId=NAME_None;P->FixtureLabel=TEXT("F5 fixture");P->bDamageEnabled=true;P->HitStepCm=15.f;P->HitMaxSubsteps=8;P->RepeatPenalty=.2f;P->RepeatMemory=2;P->AttackCount=2;
        FRPGBossProfileCard C;C.Card=P->Card;C.CooldownSeconds=1.f;C.Weight=1.f;P->Card.Reset();P->Cards.Reset();P->Cards.Add(C);
        P->BossMaxHealth=100.f;P->PlayerHitDamage=10.f;P->PostureMax=100.f;P->PlayerPostureHitAmount=60.f;P->StaggerSeconds=3.f;P->PostureRegenDelaySeconds=6.f;P->PostureRegenPerSecond=13.f;};
    auto Clips=[&](){P->StaggerStartAnim=Clip(TEXT("Stun_Start"));P->StaggerLoopAnim=Clip(TEXT("Stun_Loop"));P->StaggerEndAnim=Clip(TEXT("Stun_End"));};
    auto Refused=[&](const TCHAR* Why,const TCHAR* Token){TestFalse(Why,RPGFramework::ValidateProfile(*P,Error));TestEqual(*FString::Printf(TEXT("%s: token"),Why),Error,FString(Token));};
    TestEqual(TEXT("the default slot is the cards' slot"),P->AnimSlotName,FName(TEXT("FullBody")));
    Postured();TestTrue(TEXT("no clips: valid, F8 unchanged"),RPGFramework::ValidateProfile(*P,Error));
    Postured();Clips();TestTrue(TEXT("three stagger clips with posture: valid"),RPGFramework::ValidateProfile(*P,Error));
    Postured();Clips();P->StaggerEndAnim.Reset();Refused(TEXT("two of three clips"),TEXT("Framework.Profile.StaggerAnim.CoherentSet"));
    Postured();P->StaggerLoopAnim=Clip(TEXT("Stun_Loop"));Refused(TEXT("one of three clips"),TEXT("Framework.Profile.StaggerAnim.CoherentSet"));
    Postured();Clips();P->AnimSlotName=NAME_None;Refused(TEXT("empty slot name"),TEXT("Framework.Profile.StaggerAnim.SlotNameEmpty"));
    Postured();Clips();P->PostureMax=0.f;P->PlayerPostureHitAmount=0.f;P->StaggerSeconds=0.f;P->PostureRegenDelaySeconds=0.f;P->PostureRegenPerSecond=0.f;Refused(TEXT("stagger clips without posture"),TEXT("Framework.Profile.StaggerAnim.NoPosture"));
    Postured();P->PhaseTransitionAnim=Clip(TEXT("Ultimate_Targeting"));Refused(TEXT("phase clip without a second phase"),TEXT("Framework.Profile.PhaseTransitionAnim.Phaseless"));
    Postured();P->PhaseTransitionAnim=Clip(TEXT("Ultimate_Targeting"));P->PhaseTwoFraction=.5f;P->PhaseTwoId=TEXT("PhaseTwo");TestTrue(TEXT("phase clip with a second phase: valid"),RPGFramework::ValidateProfile(*P,Error));
    Postured();P->PhaseTransitionAnim=Clip(TEXT("Ultimate_Targeting"));P->PhaseTwoFraction=.5f;P->PhaseTwoId=TEXT("PhaseTwo");P->AnimSlotName=NAME_None;Refused(TEXT("phase clip with an empty slot"),TEXT("Framework.Profile.StaggerAnim.SlotNameEmpty"));
    return true;
}
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FFrameworkTrackYawCap,"OneBossFight.Framework.Runtime.TrackYawCap",EAutomationTestFlags::EditorContext|EAutomationTestFlags::ProductFilter)
bool FFrameworkTrackYawCap::RunTest(const FString&)
{
    // BOSS-ANM-004 staged rotation cap (RPGBossTrack::StepYaw). Hand values: cap 90 deg/s, one 60 Hz tick = 1.5 deg. (Targets are not exactly 180 deg away: that case has no defined short way.)
    const float Tick=1.f/60.f;
    auto Near=[this](const TCHAR* Why,float A,float B){TestTrue(Why,FMath::Abs(FMath::FindDeltaAngleDegrees(A,B))<1.e-3f);};
    Near(TEXT("one tick toward +90 turns 1.5 deg"),RPGBossTrack::StepYaw(0.f,90.f,90.f,Tick,false),1.5f);
    Near(TEXT("one tick toward -90 turns -1.5 deg"),RPGBossTrack::StepYaw(0.f,-90.f,90.f,Tick,false),-1.5f);
    Near(TEXT("a long step is capped at 90 deg in 1 s"),RPGBossTrack::StepYaw(0.f,170.f,90.f,1.f,false),90.f);
    Near(TEXT("inside the cap the target is reached exactly"),RPGBossTrack::StepYaw(0.f,1.f,90.f,Tick,false),1.f);
    Near(TEXT("wrap: 350 toward 10 goes the short way (+1.5)"),RPGBossTrack::StepYaw(350.f,10.f,90.f,Tick,false),351.5f);
    Near(TEXT("wrap: 10 toward 350 goes the short way (-1.5)"),RPGBossTrack::StepYaw(10.f,350.f,90.f,Tick,false),8.5f);
    Near(TEXT("committed heading never changes"),RPGBossTrack::StepYaw(30.f,200.f,90.f,1.f,true),30.f);
    Near(TEXT("zero rate never turns"),RPGBossTrack::StepYaw(30.f,200.f,0.f,1.f,false),30.f);
    Near(TEXT("negative rate never turns"),RPGBossTrack::StepYaw(30.f,200.f,-5.f,1.f,false),30.f);
    Near(TEXT("zero dt never turns"),RPGBossTrack::StepYaw(30.f,200.f,90.f,0.f,false),30.f);
    Near(TEXT("NaN rate never turns"),RPGBossTrack::StepYaw(30.f,200.f,std::numeric_limits<float>::quiet_NaN(),Tick,false),30.f);
    float Yaw=0.f,MaxStep=0.f;for(int32 I=0;I<60;++I){const float Next=RPGBossTrack::StepYaw(Yaw,170.f,90.f,Tick,false);MaxStep=FMath::Max(MaxStep,FMath::Abs(FMath::FindDeltaAngleDegrees(Yaw,Next)));Yaw=Next;}
    Near(TEXT("60 ticks (1 s) toward 170 turn exactly the cap, 90 deg"),Yaw,90.f);
    TestTrue(TEXT("no tick turned more than cap * dt (1.5 deg)"),MaxStep<=1.5f+1.e-3f);
    for(int32 I=0;I<60;++I)Yaw=RPGBossTrack::StepYaw(Yaw,170.f,90.f,Tick,true);
    Near(TEXT("after the commit 60 more ticks leave the yaw unchanged"),Yaw,90.f);
    return true;
}
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FFrameworkBossOverlayFormat,"OneBossFight.Framework.Runtime.BossOverlayFormat",EAutomationTestFlags::EditorContext|EAutomationTestFlags::ProductFilter)
bool FFrameworkBossOverlayFormat::RunTest(const FString&)
{
    // BOSS-QA-001: the exact overlay line (hand-written expected strings).
    RPGBossOverlay::FInput I;I.CardId=TEXT("SwingSlow");I.State=TEXT("Active");I.Phase=TEXT("Phase_1");I.Range=128.956;I.Cone=120.;I.bWindowOpen=true;I.Posture=40.;I.PostureMax=100.;I.Health=150.;I.MaxHealth=250.;
    TestEqual(TEXT("attack running"),RPGBossOverlay::Format(I),FString(TEXT("Card=SwingSlow State=Active Phase=Phase_1 Range=129cm Cone=120deg Window=Open Posture=40/100 Health=150/250 Stagger=0 PhaseHold=0")));
    RPGBossOverlay::FInput N;N.State=TEXT("Idle");N.Phase=TEXT("Phase_2");N.Range=300.;N.Posture=100.;N.PostureMax=100.;N.Health=50.;N.MaxHealth=250.;N.bStaggered=true;N.bPhaseHold=true;
    TestEqual(TEXT("no card, stagger and hold"),RPGBossOverlay::Format(N),FString(TEXT("Card=None State=Idle Phase=Phase_2 Range=300cm Cone=0deg Window=Closed Posture=100/100 Health=50/250 Stagger=1 PhaseHold=1")));
    RPGBossOverlay::FInput Bad=I;Bad.Range=std::numeric_limits<double>::quiet_NaN();Bad.Health=std::numeric_limits<double>::infinity();
    TestEqual(TEXT("non-finite values never print as numbers"),RPGBossOverlay::Format(Bad),FString(TEXT("Card=SwingSlow State=Active Phase=Phase_1 Range=n/acm Cone=120deg Window=Open Posture=40/100 Health=n/a/250 Stagger=0 PhaseHold=0")));
    TestEqual(TEXT("Num one digit"),RPGBossOverlay::Num(2.34,1),FString(TEXT("2.3")));
    TestEqual(TEXT("Num zero digits"),RPGBossOverlay::Num(0.4),FString(TEXT("0")));
    TestEqual(TEXT("Num NaN"),RPGBossOverlay::Num(std::numeric_limits<double>::quiet_NaN()),FString(TEXT("n/a")));
    TestEqual(TEXT("Num negative digit count is treated as zero"),RPGBossOverlay::Num(2.4,-1),FString(TEXT("2")));
    const double BadValues[]={std::numeric_limits<double>::quiet_NaN(),std::numeric_limits<double>::infinity(),-std::numeric_limits<double>::infinity()};
    for(int32 Index=0;Index<UE_ARRAY_COUNT(BadValues);++Index)
    {
        RPGBossOverlay::FInput Invalid=I;
        Invalid.Range=BadValues[Index];Invalid.Cone=BadValues[Index];Invalid.Posture=BadValues[Index];Invalid.PostureMax=BadValues[Index];Invalid.Health=BadValues[Index];Invalid.MaxHealth=BadValues[Index];
        const FString Rendered=RPGBossOverlay::Format(Invalid);
        TestTrue(*FString::Printf(TEXT("non-finite numeric column set %d is sanitized"),Index),Rendered.Contains(TEXT("n/a"))&&!Rendered.Contains(TEXT("nan"))&&!Rendered.Contains(TEXT("inf")));
    }
    return true;
}
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FFrameworkOverlayParry,"OneBossFight.Framework.Runtime.OverlayParry",EAutomationTestFlags::EditorContext|EAutomationTestFlags::ProductFilter)
bool FFrameworkOverlayParry::RunTest(const FString&)
{
    RPGBossOverlay::FInput I;I.State=TEXT("Idle");I.Phase=TEXT("Phase_1");I.bHasParryData=true;I.bParryWindowOpen=true;I.LastParryGrade=TEXT("Perfect");
    TestEqual(TEXT("parry state and last grade appear when available"),RPGBossOverlay::Format(I),FString(TEXT("Card=None State=Idle Phase=Phase_1 Range=0cm Cone=0deg Window=Closed Posture=0/0 Health=0/0 Stagger=0 PhaseHold=0 Parry=Open Grade=Perfect")));
    return true;
}
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FFrameworkPlayerActivity,"OneBossFight.Framework.Runtime.PlayerActivity",EAutomationTestFlags::EditorContext|EAutomationTestFlags::ProductFilter)
bool FFrameworkPlayerActivity::RunTest(const FString&)
{
    // BOSS-AWR-006: what counts as greedy. Heavy kinds are Strong, Charged and the jumping heavy; a light swing is no commitment; the flask wins over a heavy swing.
    using namespace RPGBossTrack;
    TestTrue(TEXT("strong, charged and jump heavy are heavy"),IsHeavyAttackKind(ERPGAttackKind::Strong)&&IsHeavyAttackKind(ERPGAttackKind::Charged)&&IsHeavyAttackKind(ERPGAttackKind::JumpHeavy));
    TestFalse(TEXT("light, jump light, knockdown and unknown are not"),IsHeavyAttackKind(ERPGAttackKind::Light)||IsHeavyAttackKind(ERPGAttackKind::JumpLight)||IsHeavyAttackKind(ERPGAttackKind::Knockdown)||IsHeavyAttackKind(ERPGAttackKind::Unknown));
    TestTrue(TEXT("nothing"),ClassifyPlayerActivity(false,false)==EPlayerActivity::None);
    TestTrue(TEXT("flask"),ClassifyPlayerActivity(true,false)==EPlayerActivity::Flask);
    TestTrue(TEXT("heavy commitment"),ClassifyPlayerActivity(false,true)==EPlayerActivity::HeavyCommit);
    TestTrue(TEXT("flask wins over heavy"),ClassifyPlayerActivity(true,true)==EPlayerActivity::Flask);
    return true;
}
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FFrameworkPunishProfile,"OneBossFight.Framework.Runtime.PunishProfile",EAutomationTestFlags::EditorContext|EAutomationTestFlags::ProductFilter)
bool FFrameworkPunishProfile::RunTest(const FString&)
{
    // BOSS-PAC-003 / PAC-005: the profile domain of the punish margin: off by default, (0,5] with both player montages and a reach in the F5 lane; a heavy finisher needs the margin on.
    using namespace FrameworkRuntimeFixture;
    TestTrue(TEXT("ordinary attack cards use the recovery punish gate"),RPGBossPunish::RequiresRecoveryPunishCheck(false,false,0.,true));
    TestFalse(TEXT("defensive cards do not use the attack recovery gate"),RPGBossPunish::RequiresRecoveryPunishCheck(true,false,0.,true));
    TestFalse(TEXT("narrow pure channel can be escaped without turning"),RPGBossPunish::RequiresRecoveryPunishCheck(false,true,45.,true));
    TestFalse(TEXT("fixed-facing pure channel can be escaped even with a full cone"),RPGBossPunish::RequiresRecoveryPunishCheck(false,true,180.,false));
    TestTrue(TEXT("full-cone tracking pure channel has no escape and keeps the gate"),RPGBossPunish::RequiresRecoveryPunishCheck(false,true,180.,true));
    TStrongObjectPtr<URPGBossFrameworkProfile> P(NewObject<URPGBossFrameworkProfile>());FString Error;
    auto F5=[&](){Fill(*P);P->FixtureLabel=TEXT("F5 fixture");P->bDamageEnabled=true;P->HitStepCm=15.f;P->HitMaxSubsteps=8;P->RepeatPenalty=.2f;P->RepeatMemory=2;P->AttackCount=2;
        FRPGBossProfileCard C;C.Card=P->Card;C.CooldownSeconds=1.f;C.Weight=1.f;P->Card.Reset();P->Cards.Reset();P->Cards.Add(C);P->PunishMarginSeconds=0.f;P->PlayerReachCm=0.f;P->PlayerLightMontage.Reset();P->PlayerHeavyMontage.Reset();};
    auto On=[&](){P->PunishMarginSeconds=.3f;P->PlayerReachCm=150.f;P->PlayerLightMontage=TSoftObjectPtr<UAnimMontage>(FSoftObjectPath(TEXT("/Game/AdvancedARPGCombat/MeleeCombatSystem/Animations/1Handed/Attack_PrimaryA_Montage.Attack_PrimaryA_Montage")));P->PlayerHeavyMontage=TSoftObjectPtr<UAnimMontage>(FSoftObjectPath(TEXT("/Game/AdvancedARPGCombat/MeleeCombatSystem/Animations/1Handed/ChargedAttack_Montage.ChargedAttack_Montage")));};
    F5();TestTrue(TEXT("off by default"),RPGFramework::ValidateProfile(*P,Error));
    F5();On();TestTrue(TEXT("on with both montages and a reach is valid"),RPGFramework::ValidateProfile(*P,Error));
    for(float V:{-.1f,5.01f,std::numeric_limits<float>::quiet_NaN()}){F5();On();P->PunishMarginSeconds=V;TestFalse(TEXT("margin outside [0,5] refused"),RPGFramework::ValidateProfile(*P,Error));}
    for(float V:{-1.f,2000.5f,std::numeric_limits<float>::quiet_NaN()}){F5();On();P->PlayerReachCm=V;TestFalse(TEXT("reach outside [0,2000] refused"),RPGFramework::ValidateProfile(*P,Error));}
    F5();On();P->PlayerLightMontage.Reset();TestFalse(TEXT("on without the light montage refused"),RPGFramework::ValidateProfile(*P,Error));
    F5();On();P->PlayerHeavyMontage.Reset();TestFalse(TEXT("on without the heavy montage refused"),RPGFramework::ValidateProfile(*P,Error));
    F5();P->Cards[0].bHeavyFinisher=true;TestFalse(TEXT("a heavy finisher with the margin off refused"),RPGFramework::ValidateProfile(*P,Error));
    F5();On();P->Cards[0].bHeavyFinisher=true;TestTrue(TEXT("a heavy finisher with the margin on is valid"),RPGFramework::ValidateProfile(*P,Error));
    {TStrongObjectPtr<URPGBossFrameworkProfile> F3(NewObject<URPGBossFrameworkProfile>());Fill(*F3);F3->PunishMarginSeconds=.3f;TestFalse(TEXT("outside the F5 lane refused"),RPGFramework::ValidateProfile(*F3,Error));}
    return true;
}
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FFrameworkNavigationDiagnosticFormatting,"OneBossFight.Framework.Runtime.NavigationDiagnosticFormatting",EAutomationTestFlags::EditorContext|EAutomationTestFlags::ProductFilter)
bool FFrameworkNavigationDiagnosticFormatting::RunTest(const FString&)
{
    using RPGBossNavigationDiagnostics::Format;
    const FVector Actor(10.f,20.f,300.f),Goal(110.f,220.f,0.f);
    const FString Success=Format(TEXT("LiveRoute"),9,42,EPathFollowingResult::Success,FPathFollowingResultFlags::Success,Actor,Goal);
    TestTrue(TEXT("success result includes route generation request and remaining ground distance"),Success.Contains(TEXT("route=LiveRoute generation=9 request=42 code=Success"))&&Success.Contains(TEXT("remainingCm=223.6")));
    TestTrue(TEXT("invalid result is explicit"),Format(TEXT("R"),1,1,EPathFollowingResult::Invalid,0,Actor,Goal).Contains(TEXT("code=Invalid")));
    TestTrue(TEXT("blocked result retains the blocked flag"),Format(TEXT("R"),1,2,EPathFollowingResult::Blocked,FPathFollowingResultFlags::Blocked,Actor,Goal).Contains(TEXT("code=Blocked codeValue=1 flags=0x0002")));
    TestTrue(TEXT("aborted result retains abort flags"),Format(TEXT("R"),2,3,EPathFollowingResult::Aborted,FPathFollowingResultFlags::UserAbort,Actor,Goal).Contains(TEXT("code=Aborted codeValue=3 flags=0x0008")));
    return true;
}
#endif
