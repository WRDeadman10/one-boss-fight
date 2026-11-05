// Copyright One Boss Fight. All Rights Reserved.
#include "Player/RPGBossMoveCard.h"
#include "Misc/AutomationTest.h"
#include <cmath>
#include <limits>

#if WITH_DEV_AUTOMATION_TESTS
namespace BossMoveCardHoldEndFixture
{
struct FInput
{
    FRPGBossMoveCardSpec Spec;
    FRPGBossMoveMetadata Metadata;
    FInput()
    {
        Spec.Schema=1; Spec.MoveId=TEXT("HoldEndBoundary"); Spec.FamilyId=TEXT("SyntheticFamily"); Spec.PhaseId=TEXT("SyntheticPhase");
        Spec.Skeleton=TSoftObjectPtr<USkeleton>(FSoftObjectPath(TEXT("/Game/OneBossFight/Data/TypedABIFixtures/F1/Skeleton.Skeleton")));
        Spec.Sequence=TSoftObjectPtr<UAnimSequence>(FSoftObjectPath(TEXT("/Game/OneBossFight/Data/TypedABIFixtures/F1/Sequence.Sequence")));
        Spec.SlotName=TEXT("SyntheticSlot"); Spec.PlayRate=1.f; Spec.CommitSeconds=.2f; Spec.ActiveStartSeconds=.4f;
        Spec.ActiveEndSeconds=.8f; Spec.RecoveryEndSeconds=1.2f; Spec.TrackDegreesPerSecond=90.f;
        Spec.MinRangeCm=25.f; Spec.MaxRangeCm=350.f; Spec.FrontConeDegrees=120.f; Spec.HPDamage=17.f;
        FRPGBossMoveWindow W; W.WindowId=TEXT("Contact"); W.HitGroup=TEXT("Swing"); W.StartSeconds=.4f; W.EndSeconds=.8f;
        W.SocketA=TEXT("WeaponBase"); W.SocketB=TEXT("WeaponTip"); W.RadiusCm=8.f; Spec.Windows.Add(W);
        Spec.HoldAtSeconds=std::nextafter(Spec.ActiveStartSeconds, 0.f); Spec.HoldMinSeconds=.2f; Spec.HoldMaxSeconds=.3f; Spec.HoldSeed=7;
        Metadata.AnimationPath=Spec.Sequence.ToSoftObjectPath(); Metadata.SkeletonPath=Spec.Skeleton.ToSoftObjectPath();
        Metadata.AnimationSkeletonPath=Metadata.MeshSkeletonPath=Metadata.SkeletonPath; Metadata.ClipLengthSeconds=1.5;
        Metadata.Slots.Add(Spec.SlotName); Metadata.SocketOrBoneNames={TEXT("WeaponBase"),TEXT("WeaponTip")};
    }
};
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FBossMoveCardHoldEndBoundaryTest,
    "OneBossFight.Framework.MoveCard.HoldEndBoundary",
    EAutomationTestFlags::EditorContext | EAutomationTestFlags::ProductFilter)

bool FBossMoveCardHoldEndBoundaryTest::RunTest(const FString&)
{
    using namespace BossMoveCardHoldEndFixture;
    FInput Input;
    TestTrue(TEXT("hold immediately before active start is valid"), RPGBossMoveCards::Validate(Input.Spec, Input.Metadata).IsValid());
    Input.Spec.HoldAtSeconds=Input.Spec.ActiveStartSeconds;
    TestFalse(TEXT("hold at the active start boundary is refused"), RPGBossMoveCards::Validate(Input.Spec, Input.Metadata).IsValid());
    return true;
}
#endif
