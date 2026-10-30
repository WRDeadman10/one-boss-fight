// Copyright One Boss Fight. All Rights Reserved.
#include "Player/RPGBossFrameworkProfile.h"
#include "Player/RPGDamageResolver.h"
#include "Player/RPGBossSweepSampling.h"
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
    auto F5=[&P](){Fill(*P);P->FixtureLabel=TEXT("F5 fixture");P->bDamageEnabled=true;P->HitStepCm=15.f;P->HitMaxSubsteps=8;P->RepeatPenalty=.2f;P->RepeatMemory=2;P->AttackCount=2;
        FRPGBossProfileCard C;C.Card=P->Card;C.CooldownSeconds=1.f;C.Weight=1.f;P->Card.Reset();P->Cards.Reset();P->Cards.Add(C);};
    F5();TestTrue(TEXT("explicit F5 profile valid"),RPGFramework::ValidateProfile(*P,Error));
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
    Refused(WithSamples([](auto& L){L.Last().TimeSeconds=L.Last().TimeSeconds-.05f;}),TEXT("last sample before the window end"));
    Refused(WithSamples([](auto& L){L.Last().TimeSeconds=1.71f;}),TEXT("sample beyond the clip length"));
    Refused(WithSamples([](auto& L){L[1].BaseCS.X=std::numeric_limits<double>::quiet_NaN();}),TEXT("non-finite sample"));
    Refused(WithSamples([](auto& L){L[1].TipCS.Z=2.e5;}),TEXT("sample beyond the domain"));
    return true;
}
#endif
