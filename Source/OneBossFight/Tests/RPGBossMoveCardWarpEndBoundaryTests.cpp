// Copyright One Boss Fight. All Rights Reserved.
#include "Player/RPGBossMoveCard.h"
#include "Misc/AutomationTest.h"
#include <cmath>
#include <limits>

#if WITH_DEV_AUTOMATION_TESTS
namespace BossMoveCardWarpEndFixture
{
struct FInput
{
    FRPGBossMoveCardSpec Spec;
    FRPGBossMoveMetadata Metadata;
    FInput()
    {
        Spec.Schema=1; Spec.MoveId=TEXT("WarpEndBoundary"); Spec.FamilyId=TEXT("SyntheticFamily"); Spec.PhaseId=TEXT("SyntheticPhase");
        Spec.Skeleton=TSoftObjectPtr<USkeleton>(FSoftObjectPath(TEXT("/Game/OneBossFight/Data/TypedABIFixtures/F1/Skeleton.Skeleton")));
        Spec.Sequence=TSoftObjectPtr<UAnimSequence>(FSoftObjectPath(TEXT("/Game/OneBossFight/Data/TypedABIFixtures/F1/Sequence.Sequence")));
        Spec.SlotName=TEXT("SyntheticSlot"); Spec.PlayRate=1.f; Spec.CommitSeconds=.2f; Spec.ActiveStartSeconds=.4f;
        Spec.ActiveEndSeconds=.8f; Spec.RecoveryEndSeconds=1.2f; Spec.TrackDegreesPerSecond=90.f;
        Spec.MinRangeCm=25.f; Spec.MaxRangeCm=350.f; Spec.FrontConeDegrees=120.f; Spec.HPDamage=17.f;
        FRPGBossMoveWindow W; W.WindowId=TEXT("Contact"); W.HitGroup=TEXT("Swing"); W.StartSeconds=.4f; W.EndSeconds=.8f;
        W.SocketA=TEXT("WeaponBase"); W.SocketB=TEXT("WeaponTip"); W.RadiusCm=8.f; Spec.Windows.Add(W);
        Spec.WarpStartSeconds=Spec.CommitSeconds; Spec.WarpEndSeconds=Spec.ActiveEndSeconds;
        Spec.WarpMaxDistanceCm=150.f; Spec.WarpMaxAngleDegrees=45.f; Spec.WarpStandoffCm=80.f;
        Metadata.AnimationPath=Spec.Sequence.ToSoftObjectPath(); Metadata.SkeletonPath=Spec.Skeleton.ToSoftObjectPath();
        Metadata.AnimationSkeletonPath=Metadata.MeshSkeletonPath=Metadata.SkeletonPath; Metadata.ClipLengthSeconds=1.5;
        Metadata.Slots.Add(Spec.SlotName); Metadata.SocketOrBoneNames={TEXT("WeaponBase"),TEXT("WeaponTip")};
    }
};
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FBossMoveCardWarpEndBoundaryTest,
    "OneBossFight.Framework.MoveCard.WarpEndBoundary",
    EAutomationTestFlags::EditorContext | EAutomationTestFlags::ProductFilter)

bool FBossMoveCardWarpEndBoundaryTest::RunTest(const FString&)
{
    using namespace BossMoveCardWarpEndFixture;
    FInput Input;
    TestTrue(TEXT("warp ending exactly at active end is valid"), RPGBossMoveCards::Validate(Input.Spec, Input.Metadata).IsValid());
    Input.Spec.WarpEndSeconds=std::nextafter(Input.Spec.ActiveEndSeconds, std::numeric_limits<float>::infinity());
    TestFalse(TEXT("warp ending immediately beyond active end is refused"), RPGBossMoveCards::Validate(Input.Spec, Input.Metadata).IsValid());
    return true;
}
#endif
