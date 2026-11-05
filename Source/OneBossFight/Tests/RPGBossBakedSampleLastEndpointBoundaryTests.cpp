// Copyright One Boss Fight. All Rights Reserved.
#include "Player/RPGBossMoveCard.h"
#include "Misc/AutomationTest.h"
#include <cmath>
#include <limits>

#if WITH_DEV_AUTOMATION_TESTS
namespace BossBakedLastEndpointFixture
{
struct FInput
{
    FRPGBossMoveCardSpec Spec;
    FRPGBossMoveMetadata Metadata;
    FInput()
    {
        Spec.Schema=1; Spec.MoveId=TEXT("BakedLastEndpoint"); Spec.FamilyId=TEXT("SyntheticFamily"); Spec.PhaseId=TEXT("SyntheticPhase");
        Spec.Skeleton=TSoftObjectPtr<USkeleton>(FSoftObjectPath(TEXT("/Game/OneBossFight/Data/TypedABIFixtures/F1/Skeleton.Skeleton")));
        Spec.Sequence=TSoftObjectPtr<UAnimSequence>(FSoftObjectPath(TEXT("/Game/OneBossFight/Data/TypedABIFixtures/F1/Sequence.Sequence")));
        Spec.SlotName=TEXT("SyntheticSlot"); Spec.PlayRate=1.f; Spec.CommitSeconds=.2f; Spec.ActiveStartSeconds=.4f;
        Spec.ActiveEndSeconds=.8f; Spec.RecoveryEndSeconds=1.2f; Spec.TrackDegreesPerSecond=90.f;
        Spec.MinRangeCm=25.f; Spec.MaxRangeCm=350.f; Spec.FrontConeDegrees=120.f; Spec.HPDamage=17.f;
        FRPGBossMoveWindow W; W.WindowId=TEXT("Contact"); W.HitGroup=TEXT("Swing"); W.StartSeconds=.4f; W.EndSeconds=.8f;
        W.SocketA=TEXT("WeaponBase"); W.SocketB=TEXT("WeaponTip"); W.RadiusCm=8.f;
        FRPGBakedBladeSample First; First.TimeSeconds=W.StartSeconds; First.BaseCS=FVector(0.,0.,0.); First.TipCS=FVector(60.,0.,0.);
        FRPGBakedBladeSample Last; Last.TimeSeconds=W.EndSeconds; Last.BaseCS=FVector(10.,0.,0.); Last.TipCS=FVector(70.,0.,0.);
        W.BakedSamples={First,Last}; Spec.Windows.Add(W);
        Metadata.AnimationPath=Spec.Sequence.ToSoftObjectPath(); Metadata.SkeletonPath=Spec.Skeleton.ToSoftObjectPath();
        Metadata.AnimationSkeletonPath=Metadata.MeshSkeletonPath=Metadata.SkeletonPath; Metadata.ClipLengthSeconds=1.5;
        Metadata.Slots.Add(Spec.SlotName); Metadata.SocketOrBoneNames={TEXT("WeaponBase"),TEXT("WeaponTip")};
    }
};
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FBossBakedSampleLastEndpointBoundaryTest,
    "OneBossFight.Framework.MoveCard.BakedLastEndpointBoundary",
    EAutomationTestFlags::EditorContext | EAutomationTestFlags::ProductFilter)

bool FBossBakedSampleLastEndpointBoundaryTest::RunTest(const FString&)
{
    using namespace BossBakedLastEndpointFixture;
    FInput Input;
    TestTrue(TEXT("sample at exact window end completes interval coverage"), RPGBossMoveCards::Validate(Input.Spec, Input.Metadata).IsValid());
    Input.Spec.Windows[0].BakedSamples.Last().TimeSeconds=std::nextafter(
        Input.Spec.Windows[0].EndSeconds, -std::numeric_limits<float>::infinity()); // lead fix: TimeSeconds is a float (same lesson as C-707)
    TestFalse(TEXT("last sample immediately before the window end leaves a coverage gap"), RPGBossMoveCards::Validate(Input.Spec, Input.Metadata).IsValid());
    return true;
}
#endif
