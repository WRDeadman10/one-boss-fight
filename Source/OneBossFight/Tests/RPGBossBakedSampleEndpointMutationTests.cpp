// Copyright One Boss Fight. All Rights Reserved.
#include "Player/RPGBossMoveCard.h"
#include "Misc/AutomationTest.h"
#include <cmath>
#include <limits>

#if WITH_DEV_AUTOMATION_TESTS
namespace BossBakedSampleEndpointFixture
{
struct FInput
{
    FRPGBossMoveCardSpec Spec;
    FRPGBossMoveMetadata Metadata;
    FInput()
    {
        Spec.Schema=1; Spec.MoveId=TEXT("SyntheticBakedEndpoint"); Spec.FamilyId=TEXT("SyntheticFamily"); Spec.PhaseId=TEXT("SyntheticPhase");
        Spec.Skeleton=TSoftObjectPtr<USkeleton>(FSoftObjectPath(TEXT("/Game/OneBossFight/Data/TypedABIFixtures/F1/Skeleton.Skeleton")));
        Spec.Sequence=TSoftObjectPtr<UAnimSequence>(FSoftObjectPath(TEXT("/Game/OneBossFight/Data/TypedABIFixtures/F1/Sequence.Sequence")));
        Spec.SlotName=TEXT("SyntheticSlot"); Spec.PlayRate=1.f; Spec.CommitSeconds=.2f; Spec.ActiveStartSeconds=.4f;
        Spec.ActiveEndSeconds=.8f; Spec.RecoveryEndSeconds=1.2f; Spec.TrackDegreesPerSecond=90.f;
        Spec.MinRangeCm=25.f; Spec.MaxRangeCm=350.f; Spec.FrontConeDegrees=120.f; Spec.HPDamage=17.f;
        FRPGBossMoveWindow Window; Window.WindowId=TEXT("Contact"); Window.HitGroup=TEXT("Swing");
        Window.StartSeconds=.4f; Window.EndSeconds=.8f; Window.SocketA=TEXT("WeaponBase"); Window.SocketB=TEXT("WeaponTip"); Window.RadiusCm=8.f;
        FRPGBakedBladeSample First; First.TimeSeconds=Window.StartSeconds; First.BaseCS=FVector(0.,0.,0.); First.TipCS=FVector(60.,0.,0.);
        FRPGBakedBladeSample Last; Last.TimeSeconds=Window.EndSeconds; Last.BaseCS=FVector(10.,0.,0.); Last.TipCS=FVector(70.,0.,0.);
        Window.BakedSamples={First,Last}; Spec.Windows.Add(Window);
        Metadata.AnimationPath=Spec.Sequence.ToSoftObjectPath(); Metadata.SkeletonPath=Spec.Skeleton.ToSoftObjectPath();
        Metadata.AnimationSkeletonPath=Metadata.MeshSkeletonPath=Metadata.SkeletonPath; Metadata.ClipLengthSeconds=1.5;
        Metadata.Slots.Add(Spec.SlotName); Metadata.SocketOrBoneNames={TEXT("WeaponBase"),TEXT("WeaponTip")};
    }
};
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FBossBakedSampleEndpointMutationTest,
    "OneBossFight.Framework.MoveCard.BakedSampleEndpointMutation",
    EAutomationTestFlags::EditorContext | EAutomationTestFlags::ProductFilter)

bool FBossBakedSampleEndpointMutationTest::RunTest(const FString&)
{
    using namespace BossBakedSampleEndpointFixture;
    FInput Input;
    TestTrue(TEXT("samples at both exact window endpoints cover the interval"),
        RPGBossMoveCards::Validate(Input.Spec, Input.Metadata).IsValid());
    Input.Spec.Windows[0].BakedSamples[0].TimeSeconds=std::nextafter(
        Input.Spec.Windows[0].StartSeconds, std::numeric_limits<float>::infinity()); // lead fix: TimeSeconds is a float, a double step below float precision rounds back to the same value
    TestFalse(TEXT("a first sample immediately after the window start leaves a coverage gap"),
        RPGBossMoveCards::Validate(Input.Spec, Input.Metadata).IsValid());
    return true;
}
#endif
