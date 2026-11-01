// Copyright One Boss Fight. All Rights Reserved.
#include "Player/RPGBossMoveCard.h"
#include "Misc/AutomationTest.h"
#include <limits>

#if WITH_DEV_AUTOMATION_TESTS
namespace BossMoveCardFixture
{
// Pure invented descriptors, NOT assets to load or gameplay timings. No object creation.
struct FInput
{
    FRPGBossMoveCardSpec S;
    FRPGBossMoveMetadata M;
    FInput()
    {
        S.Schema = 1; S.MoveId = TEXT("SyntheticSweep"); S.FamilyId = TEXT("SyntheticFamily"); S.PhaseId = TEXT("SyntheticPhase");
        S.Skeleton = TSoftObjectPtr<USkeleton>(FSoftObjectPath(TEXT("/Game/OneBossFight/Data/TypedABIFixtures/F1/Skeleton.Skeleton")));
        S.Sequence = TSoftObjectPtr<UAnimSequence>(FSoftObjectPath(TEXT("/Game/OneBossFight/Data/TypedABIFixtures/F1/Sequence.Sequence")));
        S.SlotName = TEXT("SyntheticSlot"); S.PlayRate = 1.25f;
        S.CommitSeconds = .2f; S.ActiveStartSeconds = .4f; S.ActiveEndSeconds = .8f; S.RecoveryEndSeconds = 1.2f;
        S.TrackDegreesPerSecond = 90.f; S.MinRangeCm = 25.f; S.MaxRangeCm = 350.f; S.FrontConeDegrees = 120.f; S.HPDamage = 17.f;
        FRPGBossMoveWindow W; W.WindowId = TEXT("ContactA"); W.HitGroup = TEXT("SharedSwing");
        W.StartSeconds = .4f; W.EndSeconds = .6f; W.SocketA = TEXT("WeaponBase"); W.SocketB = TEXT("WeaponTip"); W.RadiusCm = 8.f;
        S.Windows.Add(W);
        W.WindowId = TEXT("ContactB"); W.StartSeconds = .6f; W.EndSeconds = .8f; S.Windows.Add(W);
        M.AnimationPath = S.Sequence.ToSoftObjectPath(); M.SkeletonPath = S.Skeleton.ToSoftObjectPath();
        M.AnimationSkeletonPath = M.MeshSkeletonPath = M.SkeletonPath; M.ClipLengthSeconds = 1.5;
        M.Slots.Add(S.SlotName); M.SocketOrBoneNames.Add(W.SocketA); M.SocketOrBoneNames.Add(W.SocketB);
    }
};
bool Has(const FRPGBossMoveIssues& R, const TCHAR* Token)
{
    for (const FString& Error : R.Errors) if (Error.StartsWith(Token)) return true;
    return false;
}
}
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FBossMoveCardPositive, "OneBossFight.Framework.MoveCard.Positive", EAutomationTestFlags::EditorContext | EAutomationTestFlags::ProductFilter)
bool FBossMoveCardPositive::RunTest(const FString&)
{
    using namespace BossMoveCardFixture;
    FInput F; TSharedPtr<const FRPGCompiledBossMoveCard> Out;
    TestTrue(TEXT("nondefault card with shared hit-group, distinct touching windows"), RPGBossMoveCards::CompileMetadata(F.S,F.M,Out).IsValid());
    if (!Out) { AddError(TEXT("Missing compiled preview")); return false; }
    TestFalse(TEXT("metadata fixture is never resolved asset capability"), Out->HasResolvedAssets());
    TestEqual(TEXT("nondefault rate copied"), Out->Spec().PlayRate, 1.25f);
    TestEqual(TEXT("nondefault damage copied"), Out->Spec().HPDamage, 17.f);
    TestEqual(TEXT("two explicit windows"), Out->Spec().Windows.Num(), 2);
    F.S.Sequence.Reset(); F.S.Montage = TSoftObjectPtr<UAnimMontage>(FSoftObjectPath(TEXT("/Game/OneBossFight/Data/TypedABIFixtures/F1/Montage.Montage")));
    F.M.AnimationPath = F.S.Montage.ToSoftObjectPath(); F.S.SectionName = TEXT("SyntheticSection"); F.M.Sections.Add(F.S.SectionName);
    TestTrue(TEXT("explicit montage section accepted"), RPGBossMoveCards::Validate(F.S,F.M).IsValid());
    F.S.CommitSeconds = 0.f; F.S.TrackDegreesPerSecond = 0.f; F.S.MinRangeCm = F.S.MaxRangeCm = 0.f;
    F.S.FrontConeDegrees = 360.f; F.S.HPDamage = 0.f; F.S.RecoveryEndSeconds = F.S.ActiveEndSeconds; F.M.ClipLengthSeconds = F.S.ActiveEndSeconds;
    TestTrue(TEXT("inclusive domain and timeline endpoints"), RPGBossMoveCards::Validate(F.S,F.M).IsValid());
    return true;
}
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FBossMoveCardNumbers, "OneBossFight.Framework.MoveCard.Numbers", EAutomationTestFlags::EditorContext | EAutomationTestFlags::ProductFilter)
bool FBossMoveCardNumbers::RunTest(const FString&)
{
    using namespace BossMoveCardFixture;
    const float Values[] = {-1.f, 1000001.f, std::numeric_limits<float>::infinity(), std::numeric_limits<float>::quiet_NaN()};
    using FMember = float FRPGBossMoveCardSpec::*;
    const FMember Fields[] = {&FRPGBossMoveCardSpec::PlayRate,&FRPGBossMoveCardSpec::CommitSeconds,&FRPGBossMoveCardSpec::ActiveStartSeconds,&FRPGBossMoveCardSpec::ActiveEndSeconds,&FRPGBossMoveCardSpec::RecoveryEndSeconds,&FRPGBossMoveCardSpec::TrackDegreesPerSecond,&FRPGBossMoveCardSpec::MinRangeCm,&FRPGBossMoveCardSpec::MaxRangeCm,&FRPGBossMoveCardSpec::FrontConeDegrees,&FRPGBossMoveCardSpec::HPDamage};
    for (FMember Field : Fields) for (float Value : Values)
    {
        FInput F; F.S.*Field = Value;
        const auto R = RPGBossMoveCards::Validate(F.S,F.M);
        TestTrue(TEXT("every scalar rejects nonfinite/negative/over-ceiling"), Has(R,FMath::IsFinite(Value) ? TEXT("MoveCard.Domain") : TEXT("MoveCard.NonFinite")));
    }
    for (float Value : Values)
    {
        FInput F; F.M.ClipLengthSeconds = Value;
        TestFalse(TEXT("bad descriptor length rejected"), RPGBossMoveCards::Validate(F.S,F.M).IsValid());
        for (int32 N=0;N<3;++N)
        {
            FInput W; float* Field = N==0 ? &W.S.Windows[1].StartSeconds : N==1 ? &W.S.Windows[1].EndSeconds : &W.S.Windows[1].RadiusCm; *Field=Value;
            TestFalse(TEXT("late window scalar rejected"), RPGBossMoveCards::Validate(W.S,W.M).IsValid());
        }
    }
    FInput Z; Z.S.PlayRate=0.f; TestTrue(TEXT("zero play rate"), Has(RPGBossMoveCards::Validate(Z.S,Z.M),TEXT("MoveCard.Domain")));
    Z=FInput(); Z.M.ClipLengthSeconds=0; TestFalse(TEXT("zero clip length"),RPGBossMoveCards::Validate(Z.S,Z.M).IsValid());
    Z=FInput(); Z.S.Windows[1].RadiusCm=0; TestFalse(TEXT("zero radius"),RPGBossMoveCards::Validate(Z.S,Z.M).IsValid());
    Z=FInput(); Z.S.TrackDegreesPerSecond=Z.S.HPDamage=Z.S.MaxRangeCm=1000000.f;
    TestTrue(TEXT("inclusive ceiling without clamp"),RPGBossMoveCards::Validate(Z.S,Z.M).IsValid());
    return true;
}
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FBossMoveCardRejections, "OneBossFight.Framework.MoveCard.Rejections", EAutomationTestFlags::EditorContext | EAutomationTestFlags::ProductFilter)
bool FBossMoveCardRejections::RunTest(const FString&)
{
    using namespace BossMoveCardFixture;
    auto Reject=[this](TFunction<void(FInput&)> Change,const TCHAR* Token)
    { FInput F; Change(F); TestTrue(Token,Has(RPGBossMoveCards::Validate(F.S,F.M),Token)); };
    Reject([](FInput& F){F.S.Schema=0;},TEXT("MoveCard.Identity"));
    Reject([](FInput& F){F.S.MoveId=NAME_None;},TEXT("MoveCard.Identity"));
    Reject([](FInput& F){F.S.FamilyId=NAME_None;},TEXT("MoveCard.Identity"));
    Reject([](FInput& F){F.S.PhaseId=NAME_None;},TEXT("MoveCard.Identity"));
    Reject([](FInput& F){F.S.Sequence.Reset();},TEXT("MoveCard.AnimationSource"));
    Reject([](FInput& F){F.S.Montage=TSoftObjectPtr<UAnimMontage>(F.S.Sequence.ToSoftObjectPath());},TEXT("MoveCard.AnimationSource"));
    Reject([](FInput& F){F.M.AnimationPath=FSoftObjectPath();},TEXT("MoveCard.AnimationIdentity"));
    Reject([](FInput& F){F.S.Skeleton.Reset();},TEXT("MoveCard.SkeletonIdentity"));
    Reject([](FInput& F){F.M.SkeletonPath=FSoftObjectPath();},TEXT("MoveCard.SkeletonIdentity"));
    Reject([](FInput& F){F.M.AnimationSkeletonPath=FSoftObjectPath();},TEXT("MoveCard.SkeletonIdentity"));
    Reject([](FInput& F){F.M.MeshSkeletonPath=FSoftObjectPath();},TEXT("MoveCard.SkeletonIdentity"));
    Reject([](FInput& F){F.M.Slots.Empty();},TEXT("MoveCard.Slot"));
    Reject([](FInput& F){F.S.SectionName=TEXT("Absent");},TEXT("MoveCard.Section"));
    Reject([](FInput& F){F.S.bUsesRootMotion=true;},TEXT("MoveCard.UnsupportedRootMotion"));
    Reject([](FInput& F){F.M.bRootMotion=true;},TEXT("MoveCard.UnsupportedRootMotion"));
    Reject([](FInput& F){F.S.CommitSeconds=.5f;},TEXT("MoveCard.Timeline"));
    Reject([](FInput& F){F.S.ActiveEndSeconds=F.S.ActiveStartSeconds;},TEXT("MoveCard.Timeline"));
    Reject([](FInput& F){F.S.RecoveryEndSeconds=.7f;},TEXT("MoveCard.Timeline"));
    Reject([](FInput& F){F.M.ClipLengthSeconds=1.f;},TEXT("MoveCard.Timeline"));
    Reject([](FInput& F){F.S.MinRangeCm=400.f;},TEXT("MoveCard.Eligibility"));
    Reject([](FInput& F){F.S.FrontConeDegrees=361.f;},TEXT("MoveCard.Eligibility"));
    Reject([](FInput& F){F.S.Windows.Empty();},TEXT("MoveCard.Window"));
    Reject([](FInput& F){F.S.Windows[1].WindowId=F.S.Windows[0].WindowId;},TEXT("MoveCard.WindowIdentity"));
    Reject([](FInput& F){F.S.Windows[1].HitGroup=NAME_None;},TEXT("MoveCard.WindowIdentity"));
    Reject([](FInput& F){F.S.Windows[1].StartSeconds=.59f;},TEXT("MoveCard.Window"));
    Reject([](FInput& F){F.S.Windows[0].StartSeconds=.3f;},TEXT("MoveCard.Window"));
    Reject([](FInput& F){F.S.Windows[1].EndSeconds=.9f;},TEXT("MoveCard.Window"));
    Reject([](FInput& F){F.S.Windows[1].SocketB=F.S.Windows[1].SocketA;},TEXT("MoveCard.Socket"));
    Reject([](FInput& F){F.M.SocketOrBoneNames.Remove(F.S.Windows[1].SocketB);},TEXT("MoveCard.Socket"));
    // BOSS-HIT-010: a secondary window may overlap in time and must share a hit group with a direct window.
    {FInput F;F.S.Windows[1].bSecondary=true;F.S.Windows[1].StartSeconds=F.S.Windows[0].StartSeconds;F.S.Windows[1].HitGroup=F.S.Windows[0].HitGroup;TestTrue(TEXT("overlapping secondary window of the same group is valid"),RPGBossMoveCards::Validate(F.S,F.M).IsValid());}
    Reject([](FInput& F){F.S.Windows[1].bSecondary=true;F.S.Windows[1].HitGroup=TEXT("OtherGroup");},TEXT("MoveCard.Window"));
    Reject([](FInput& F){for(auto& W:F.S.Windows)W.bSecondary=true;},TEXT("MoveCard.Window"));
    Reject([](FInput& F){F.S.Windows[1].StartSeconds=F.S.Windows[0].StartSeconds;},TEXT("MoveCard.Window"));   // two DIRECT windows still may not overlap
    // BOSS-HIT-011: a ring window (no sockets) validates with its five numbers, and is refused without them or with a blade.
    auto MakeRing=[](FInput& F){auto& W=F.S.Windows[1];W.bSecondary=true;W.HitGroup=F.S.Windows[0].HitGroup;W.SocketA=W.SocketB=NAME_None;W.RadiusCm=0.f;W.bRing=true;W.RingStartRadiusCm=60.f;W.RingSpeedCmPerSecond=400.f;W.RingThicknessCm=40.f;W.RingHeightCm=50.f;};
    {FInput F;MakeRing(F);TestTrue(TEXT("ring window without sockets is valid"),RPGBossMoveCards::Validate(F.S,F.M).IsValid());}
    Reject([&](FInput& F){MakeRing(F);F.S.Windows[1].RingSpeedCmPerSecond=0.f;},TEXT("MoveCard.Domain"));
    Reject([&](FInput& F){MakeRing(F);F.S.Windows[1].RingThicknessCm=-1.f;},TEXT("MoveCard.Domain"));
    Reject([&](FInput& F){MakeRing(F);F.S.Windows[1].RingHeightCm=std::numeric_limits<float>::quiet_NaN();},TEXT("MoveCard.NonFinite"));
    Reject([&](FInput& F){MakeRing(F);F.S.Windows[1].SocketA=F.S.Windows[0].SocketA;},TEXT("MoveCard.Window"));
    // BOSS-HIT-012: a grab window is a blade window with a known attach socket and a release time after its end, inside the recovery; one per card.
    auto MakeGrab=[](FInput& F){auto& W=F.S.Windows[0];W.bGrab=true;W.GrabAttachSocket=W.SocketA;W.GrabReleaseSeconds=1.f;};
    {FInput F;MakeGrab(F);TestTrue(TEXT("grab window is valid"),RPGBossMoveCards::Validate(F.S,F.M).IsValid());}
    Reject([&](FInput& F){MakeGrab(F);F.S.Windows[0].GrabAttachSocket=NAME_None;},TEXT("MoveCard.Grab"));
    Reject([&](FInput& F){MakeGrab(F);F.S.Windows[0].GrabAttachSocket=TEXT("NotASocket");},TEXT("MoveCard.Grab"));
    Reject([&](FInput& F){MakeGrab(F);F.S.Windows[0].GrabReleaseSeconds=F.S.Windows[0].EndSeconds;},TEXT("MoveCard.Grab"));
    Reject([&](FInput& F){MakeGrab(F);F.S.Windows[0].GrabReleaseSeconds=F.S.RecoveryEndSeconds+.1f;},TEXT("MoveCard.Grab"));
    Reject([&](FInput& F){MakeGrab(F);F.S.Windows[1].bGrab=true;F.S.Windows[1].GrabAttachSocket=F.S.Windows[1].SocketA;F.S.Windows[1].GrabReleaseSeconds=1.f;},TEXT("MoveCard.Grab"));
    Reject([&](FInput& F){MakeGrab(F);F.S.Windows[0].GrabReleaseSeconds=std::numeric_limits<float>::quiet_NaN();},TEXT("MoveCard.NonFinite"));
    // BOSS-ANM-006: the warp is off at 0/0; with a budget it needs a window after the commit inside the active end and budgets within 1000 cm / 180 degrees.
    auto MakeWarp=[](FInput& F){F.S.WarpStartSeconds=F.S.CommitSeconds;F.S.WarpEndSeconds=F.S.ActiveStartSeconds;F.S.WarpMaxDistanceCm=150.f;F.S.WarpMaxAngleDegrees=45.f;F.S.WarpStandoffCm=80.f;};
    {FInput F;MakeWarp(F);TestTrue(TEXT("warp window and budgets are valid"),RPGBossMoveCards::Validate(F.S,F.M).IsValid());}
    Reject([&](FInput& F){MakeWarp(F);F.S.WarpStartSeconds=F.S.CommitSeconds-.1f;},TEXT("MoveCard.Warp"));
    Reject([&](FInput& F){MakeWarp(F);F.S.WarpEndSeconds=F.S.WarpStartSeconds;},TEXT("MoveCard.Warp"));
    Reject([&](FInput& F){MakeWarp(F);F.S.WarpEndSeconds=F.S.ActiveEndSeconds+.1f;},TEXT("MoveCard.Warp"));
    Reject([&](FInput& F){MakeWarp(F);F.S.WarpMaxDistanceCm=1000.5f;},TEXT("MoveCard.Warp"));
    Reject([&](FInput& F){MakeWarp(F);F.S.WarpMaxAngleDegrees=181.f;},TEXT("MoveCard.Warp"));
    Reject([&](FInput& F){MakeWarp(F);F.S.WarpMaxDistanceCm=-1.f;},TEXT("MoveCard.Domain"));
    Reject([&](FInput& F){MakeWarp(F);F.S.WarpStandoffCm=std::numeric_limits<float>::quiet_NaN();},TEXT("MoveCard.NonFinite"));
    // BOSS-ANM-003: the windup hold is off at 0/0; on it needs a window after the commit and before the active start, 0 < min <= max <= 3.
    auto MakeHold=[](FInput& F){F.S.HoldAtSeconds=.3f;F.S.HoldMinSeconds=.4f;F.S.HoldMaxSeconds=.9f;F.S.HoldSeed=5;};
    {FInput F;MakeHold(F);TestTrue(TEXT("hold window is valid"),RPGBossMoveCards::Validate(F.S,F.M).IsValid());}
    Reject([&](FInput& F){MakeHold(F);F.S.HoldAtSeconds=F.S.CommitSeconds-.1f;},TEXT("MoveCard.Hold"));
    Reject([&](FInput& F){MakeHold(F);F.S.HoldAtSeconds=F.S.ActiveStartSeconds;},TEXT("MoveCard.Hold"));
    Reject([&](FInput& F){MakeHold(F);F.S.HoldMinSeconds=0.f;},TEXT("MoveCard.Hold"));
    Reject([&](FInput& F){MakeHold(F);F.S.HoldMaxSeconds=.3f;},TEXT("MoveCard.Hold"));
    Reject([&](FInput& F){MakeHold(F);F.S.HoldMaxSeconds=3.1f;},TEXT("MoveCard.Hold"));
    Reject([&](FInput& F){MakeHold(F);F.S.HoldMaxSeconds=std::numeric_limits<float>::quiet_NaN();},TEXT("MoveCard.NonFinite"));
    // BOSS-PAC-004 / QA-007: a cue has an id, a visual AND a sound; two cues differ in both; a release cue needs the hold.
    auto MakeCue=[](FInput& F){FRPGBossCue A;A.CueId=TEXT("Release");A.bAtHoldRelease=true;A.Visual=ERPGBossCueVisual::HitSpark;A.Sound=TSoftObjectPtr<USoundBase>(FSoftObjectPath(TEXT("/Game/ParagonSevarog/Characters/Heroes/Sevarog/Sounds/SoundCues/Sevarog_Effort_Attack.Sevarog_Effort_Attack")));
        FRPGBossCue B;B.CueId=TEXT("Recovery");B.TimeSeconds=F.S.ActiveEndSeconds;B.Visual=ERPGBossCueVisual::DodgeDust;B.Sound=TSoftObjectPtr<USoundBase>(FSoftObjectPath(TEXT("/Game/ParagonSevarog/Characters/Heroes/Sevarog/Sounds/SoundCues/Sevarog_Effort_BreathingLowHealth.Sevarog_Effort_BreathingLowHealth")));F.S.Cues={A,B};};
    {FInput F;MakeHold(F);MakeCue(F);TestTrue(TEXT("a hold with a release cue and a recovery cue is valid"),RPGBossMoveCards::Validate(F.S,F.M).IsValid());}
    Reject([&](FInput& F){MakeCue(F);},TEXT("MoveCard.Cue"));   // the release cue without a hold
    Reject([&](FInput& F){MakeHold(F);MakeCue(F);F.S.Cues[1].Sound.Reset();},TEXT("MoveCard.Cue"));
    Reject([&](FInput& F){MakeHold(F);MakeCue(F);F.S.Cues[1].Visual=ERPGBossCueVisual::None;},TEXT("MoveCard.Cue"));
    Reject([&](FInput& F){MakeHold(F);MakeCue(F);F.S.Cues[1].CueId=NAME_None;},TEXT("MoveCard.Cue"));
    Reject([&](FInput& F){MakeHold(F);MakeCue(F);F.S.Cues[1].TimeSeconds=F.S.RecoveryEndSeconds+.1f;},TEXT("MoveCard.Cue"));
    Reject([&](FInput& F){MakeHold(F);MakeCue(F);F.S.Cues[1].Visual=F.S.Cues[0].Visual;},TEXT("MoveCard.CueDistinct"));
    Reject([&](FInput& F){MakeHold(F);MakeCue(F);F.S.Cues[1].Sound=F.S.Cues[0].Sound;},TEXT("MoveCard.CueDistinct"));
    Reject([&](FInput& F){MakeHold(F);MakeCue(F);F.S.Cues[1].CueId=F.S.Cues[0].CueId;},TEXT("MoveCard.CueDistinct"));
    Reject([&](FInput& F){MakeHold(F);MakeCue(F);for(int32 I=0;I<8;++I){FRPGBossCue X=F.S.Cues[1];X.CueId=FName(*FString::Printf(TEXT("X%d"),I));F.S.Cues.Add(X);}},TEXT("MoveCard.Cue"));
    return true;
}
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FBossMoveCardSnapshot, "OneBossFight.Framework.MoveCard.SnapshotAndFailure", EAutomationTestFlags::EditorContext | EAutomationTestFlags::ProductFilter)
bool FBossMoveCardSnapshot::RunTest(const FString&)
{
    using namespace BossMoveCardFixture;
    FInput F; TSharedPtr<const FRPGCompiledBossMoveCard> Out;
    TestTrue(TEXT("preview constructed"),RPGBossMoveCards::CompileMetadata(F.S,F.M,Out).IsValid());
    if (!Out) return false;
    const auto Frozen=Out;
    F.S.HPDamage=999.f; F.S.Windows.Empty(); F.M.Slots.Empty();
    TestEqual(TEXT("source mutation cannot change snapshot"),Frozen->Spec().HPDamage,17.f);
    TestEqual(TEXT("nested windows copied"),Frozen->Spec().Windows.Num(),2);
    TestTrue(TEXT("metadata copied"),Frozen->Metadata().Slots.Contains(TEXT("SyntheticSlot")));
    TestFalse(TEXT("late invalid compile rejected"),RPGBossMoveCards::CompileMetadata(F.S,F.M,Out).IsValid());
    TestFalse(TEXT("stale output cleared on failure"),Out.IsValid());
    F=FInput(); RPGBossMoveCards::CompileMetadata(F.S,F.M,Out);
    const auto R=RPGBossMoveCards::CompileResolved(F.S,nullptr,nullptr,nullptr,Out);
    TestFalse(TEXT("no loaded dependencies fails closed"),R.IsValid());
    TestFalse(TEXT("resolved failure clears stale preview"),Out.IsValid());
    TestFalse(TEXT("default unconfigured draft invalid"),RPGBossMoveCards::Validate(FRPGBossMoveCardSpec(),FRPGBossMoveMetadata()).IsValid());
    return true;
}
#endif
