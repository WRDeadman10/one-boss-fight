// Copyright One Boss Fight. All Rights Reserved.
#include "Player/RPGBossMoveCard.h"
#include "Player/RPGBossChannelDrainRules.h"
#include "Player/RPGBossDefenseRules.h"
#include "Misc/AutomationTest.h"
#include <initializer_list>
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
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FBossMoveCardDamageBudget, "OneBossFight.Framework.MoveCard.DamageBudget", EAutomationTestFlags::EditorContext | EAutomationTestFlags::ProductFilter)
bool FBossMoveCardDamageBudget::RunTest(const FString&)
{
    using namespace BossMoveCardFixture;
    FInput F;
    TestEqual(TEXT("legacy card damage budget is its direct damage"), RPGBossMoveCards::DamageBudget(F.S), 17.0);
    F.S.AreaEffect.bEnabled=true; F.S.AreaEffect.Damage=12.f;
    F.S.ChannelDrain.bEnabled=true; F.S.ChannelDrain.StartSeconds=.2f; F.S.ChannelDrain.EndSeconds=.8f;
    F.S.ChannelDrain.TickIntervalSeconds=.2f; F.S.ChannelDrain.TickDamage=8.f;
    TestEqual(TEXT("budget conservatively sums direct, area and channel damage"), RPGBossMoveCards::DamageBudget(F.S), 53.0);
    F.S.AreaEffect.bEnabled=false; F.S.ChannelDrain.bEnabled=false;
    TestEqual(TEXT("disabled add-ons do not inflate the budget"), RPGBossMoveCards::DamageBudget(F.S), 17.0);
    return true;
}
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FBossMoveCardAreaEffect, "OneBossFight.Framework.MoveCard.AreaEffect", EAutomationTestFlags::EditorContext | EAutomationTestFlags::ProductFilter)
bool FBossMoveCardAreaEffect::RunTest(const FString&)
{
    using namespace BossMoveCardFixture;
    FInput F;
    // Legacy/direct-window cards remain valid with the new optional payload absent.
    TestTrue(TEXT("disabled add-on preserves existing card validity"), RPGBossMoveCards::Validate(F.S,F.M).IsValid());
    F.S.Windows.Empty();
    F.S.AreaEffect.bEnabled=true;
    F.S.AreaEffect.ReleaseSeconds=.8f;
    F.S.AreaEffect.DelaySeconds=.2f;
    F.S.AreaEffect.RadiusCm=180.f;
    F.S.AreaEffect.Damage=12.f;
    F.S.AreaEffect.SnareSeconds=1.f;
    F.S.AreaEffect.SnareSpeedScale=.45f;
    TestTrue(TEXT("valid effect-only card compiles without a blade window"), RPGBossMoveCards::Validate(F.S,F.M).IsValid());
    auto Reject=[&](auto Mutate,const TCHAR* Token)
    {
        FInput Case; Case.S.Windows.Empty(); Case.S.AreaEffect.bEnabled=true;
        Case.S.AreaEffect.ReleaseSeconds=.8f; Case.S.AreaEffect.DelaySeconds=.2f;
        Case.S.AreaEffect.RadiusCm=180.f; Case.S.AreaEffect.Damage=12.f;
        Case.S.AreaEffect.SnareSeconds=1.f; Case.S.AreaEffect.SnareSpeedScale=.45f;
        Mutate(Case.S.AreaEffect);
        TestTrue(FString::Printf(TEXT("invalid area-effect field reports %s"),Token),Has(RPGBossMoveCards::Validate(Case.S,Case.M),Token));
    };
    Reject([](FRPGBossAreaEffect& E){E.ReleaseSeconds=1.3f;},TEXT("MoveCard.AreaEffect"));
    Reject([](FRPGBossAreaEffect& E){E.DelaySeconds=-.1f;},TEXT("MoveCard.Domain"));
    Reject([](FRPGBossAreaEffect& E){E.RadiusCm=0.f;},TEXT("MoveCard.Domain"));
    Reject([](FRPGBossAreaEffect& E){E.SnareSpeedScale=1.1f;},TEXT("MoveCard.AreaEffect"));
    Reject([](FRPGBossAreaEffect& E){E.SnareSeconds=0.f;E.SnareSpeedScale=.45f;},TEXT("MoveCard.AreaEffect"));
    Reject([](FRPGBossAreaEffect& E){E.ReleaseSeconds=.199f;},TEXT("MoveCard.AreaEffect"));
    Reject([](FRPGBossAreaEffect& E){E.DelaySeconds=10.01f;},TEXT("MoveCard.AreaEffect"));
    Reject([](FRPGBossAreaEffect& E){E.RadiusCm=2000.01f;},TEXT("MoveCard.AreaEffect"));
    Reject([](FRPGBossAreaEffect& E){E.Damage=-.01f;},TEXT("MoveCard.Domain"));
    Reject([](FRPGBossAreaEffect& E){E.SnareSeconds=30.01f;},TEXT("MoveCard.AreaEffect"));
    Reject([](FRPGBossAreaEffect& E){E.SnareSpeedScale=-.01f;},TEXT("MoveCard.Domain"));
    // Boundary sweep: positive radius, delay cap, and release+delay must stay inside recovery.
    const float Radii[] = {.01f, 100.f, 2000.f, 2000.01f};
    for (float Radius : Radii)
    {
        FInput Case; Case.S.Windows.Empty(); Case.S.AreaEffect.bEnabled=true;
        Case.S.AreaEffect.ReleaseSeconds=.8f; Case.S.AreaEffect.DelaySeconds=.2f;
        Case.S.AreaEffect.RadiusCm=Radius; Case.S.AreaEffect.Damage=1.f;
        const bool bExpectedValid=Radius<=2000.f;
        TestEqual(FString::Printf(TEXT("area radius boundary %.2f"),Radius),RPGBossMoveCards::Validate(Case.S,Case.M).IsValid(),bExpectedValid);
    }
    for (float Delay : {0.f, .001f, 10.f, 10.01f})
    {
        FInput Case; Case.S.Windows.Empty(); Case.S.AreaEffect.bEnabled=true;
        Case.S.AreaEffect.ReleaseSeconds=.8f; Case.S.AreaEffect.DelaySeconds=Delay;
        Case.S.AreaEffect.RadiusCm=180.f; Case.S.AreaEffect.Damage=1.f;
        const bool bExpectedValid=(Delay<=10.f && .8f+Delay<=Case.S.RecoveryEndSeconds);
        TestEqual(FString::Printf(TEXT("area delay boundary %.3f"),Delay),RPGBossMoveCards::Validate(Case.S,Case.M).IsValid(),bExpectedValid);
    }
    using FAreaField=float FRPGBossAreaEffect::*;
    const FAreaField AreaFields[]={&FRPGBossAreaEffect::ReleaseSeconds,&FRPGBossAreaEffect::DelaySeconds,&FRPGBossAreaEffect::RadiusCm,&FRPGBossAreaEffect::Damage,&FRPGBossAreaEffect::SnareSeconds,&FRPGBossAreaEffect::SnareSpeedScale};
    for (FAreaField Field : AreaFields) for (float Bad : {std::numeric_limits<float>::quiet_NaN(),std::numeric_limits<float>::infinity()})
    {
        FInput Case; Case.S.Windows.Empty(); Case.S.AreaEffect.bEnabled=true;
        Case.S.AreaEffect.ReleaseSeconds=.8f; Case.S.AreaEffect.DelaySeconds=.2f; Case.S.AreaEffect.RadiusCm=180.f; Case.S.AreaEffect.Damage=1.f;
        (Case.S.AreaEffect).*(Field)=Bad;
        TestTrue(TEXT("every AreaEffect numeric member rejects NaN/Infinity"),Has(RPGBossMoveCards::Validate(Case.S,Case.M),TEXT("MoveCard.NonFinite")));
    }
    return true;
}
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FBossMoveCardChannelDrain, "OneBossFight.Framework.MoveCard.ChannelDrain", EAutomationTestFlags::EditorContext | EAutomationTestFlags::ProductFilter)
bool FBossMoveCardChannelDrain::RunTest(const FString&)
{
    using namespace BossMoveCardFixture;
    FInput F;
    TestTrue(TEXT("legacy card retains no-channel behavior"),RPGBossMoveCards::Validate(F.S,F.M).IsValid());
    F.S.Windows.Empty();
    F.S.RecoveryEndSeconds=1.5f;
    F.S.ChannelDrain.bEnabled=true; F.S.ChannelDrain.StartSeconds=.267f; F.S.ChannelDrain.EndSeconds=1.267f;
    F.S.ChannelDrain.TickIntervalSeconds=.25f; F.S.ChannelDrain.TickDamage=8.f; F.S.ChannelDrain.HealFraction=.35f;
    F.S.ChannelDrain.ConeRangeCm=600.f; F.S.ChannelDrain.ConeHalfAngleDegrees=50.f;
    TestTrue(TEXT("valid effect-only channel card"),RPGBossMoveCards::Validate(F.S,F.M).IsValid());
    auto Reject=[&](auto Mutate,const TCHAR* Token,const TCHAR* Label)
    {
        FInput Case; Case.S.Windows.Empty(); Case.S.RecoveryEndSeconds=1.5f; Case.S.ChannelDrain.bEnabled=true;
        Case.S.ChannelDrain.StartSeconds=.267f; Case.S.ChannelDrain.EndSeconds=1.267f;
        Case.S.ChannelDrain.TickIntervalSeconds=.25f; Case.S.ChannelDrain.TickDamage=8.f; Case.S.ChannelDrain.HealFraction=.35f;
        Case.S.ChannelDrain.ConeRangeCm=600.f; Case.S.ChannelDrain.ConeHalfAngleDegrees=50.f;
        Mutate(Case.S.ChannelDrain);
        TestTrue(FString::Printf(TEXT("%s is rejected"),Label),Has(RPGBossMoveCards::Validate(Case.S,Case.M),Token));
    };
    Reject([](FRPGBossChannelDrain& C){C.TickIntervalSeconds=0.f;},TEXT("MoveCard.Domain"),TEXT("zero tick interval"));
    Reject([](FRPGBossChannelDrain& C){C.EndSeconds=C.StartSeconds;},TEXT("MoveCard.ChannelDrain"),TEXT("empty channel timeline"));
    Reject([](FRPGBossChannelDrain& C){C.HealFraction=1.1f;},TEXT("MoveCard.ChannelDrain"),TEXT("heal fraction above one"));
    Reject([](FRPGBossChannelDrain& C){C.TickDamage=0.f;C.HealFraction=0.f;},TEXT("MoveCard.ChannelDrain"),TEXT("empty channel tick"));
    Reject([](FRPGBossChannelDrain& C){C.StartSeconds=.199f;},TEXT("MoveCard.ChannelDrain"),TEXT("channel starts before commit"));
    Reject([](FRPGBossChannelDrain& C){C.EndSeconds=1.501f;},TEXT("MoveCard.ChannelDrain"),TEXT("channel exceeds recovery"));
    Reject([](FRPGBossChannelDrain& C){C.TickIntervalSeconds=.001f;},TEXT("MoveCard.ChannelDrain"),TEXT("tick count exceeds maximum"));
    Reject([](FRPGBossChannelDrain& C){C.TickDamage=-.01f;},TEXT("MoveCard.Domain"),TEXT("negative tick damage"));
    Reject([](FRPGBossChannelDrain& C){C.ConeRangeCm=2000.1f;},TEXT("MoveCard.ChannelDrain"),TEXT("range above maximum"));
    Reject([](FRPGBossChannelDrain& C){C.ConeHalfAngleDegrees=180.1f;},TEXT("MoveCard.ChannelDrain"),TEXT("angle above maximum"));
    TestEqual(TEXT("heal uses accepted actual damage, capped by missing boss health"),RPGBossChannelDrain::CappedHeal(30.,.5,93.,100.),7.);
    TestEqual(TEXT("a partially accepted tick heals from resolved HP loss, not nominal tick damage"),RPGBossChannelDrain::CappedHeal(6.,.5,50.,100.),3.);
    TestEqual(TEXT("overkill is capped to actual missing health after using resolved HP loss"),RPGBossChannelDrain::CappedHeal(6.,.5,99.,100.),1.);
    TestEqual(TEXT("zero accepted HP does not heal"),RPGBossChannelDrain::CappedHeal(0.,.5,50.,100.),0.);
    TestEqual(TEXT("full boss cannot overheal"),RPGBossChannelDrain::CappedHeal(30.,.5,100.,100.),0.);
    TestEqual(TEXT("inclusive tick count survives float endpoint rounding"),RPGBossChannelDrain::TickCount(.267f,1.267f,.25f),4);
    TestEqual(TEXT("invalid cadence produces no ticks"),RPGBossChannelDrain::TickCount(.2,.8,0.),0);
    for (double Interval : {.01, .1, .25, 1., 65.})
    {
        const int32 Ticks=RPGBossChannelDrain::TickCount(0.,1.,Interval);
        TestTrue(FString::Printf(TEXT("tick count is bounded for interval %.2f"),Interval),Ticks>=0&&Ticks<=65);
        if (Interval>=.01&&Interval<=1.) TestTrue(FString::Printf(TEXT("positive channel interval yields ticks %.2f"),Interval),Ticks>=1);
    }
    for (double Accepted : {0., 1., 25., 1000.}) for (double Fraction : {.01, .5, 1.})
    {
        const double Heal=RPGBossChannelDrain::CappedHeal(Accepted,Fraction,75.,100.);
        TestTrue(TEXT("heal is nonnegative and bounded by accepted loss and missing health"),Heal>=0.&&Heal<=Accepted*Fraction&&Heal<=25.);
    }
    using FChannelField=float FRPGBossChannelDrain::*;
    const FChannelField ChannelFields[]={&FRPGBossChannelDrain::StartSeconds,&FRPGBossChannelDrain::EndSeconds,&FRPGBossChannelDrain::TickIntervalSeconds,&FRPGBossChannelDrain::TickDamage,&FRPGBossChannelDrain::HealFraction,&FRPGBossChannelDrain::ConeRangeCm,&FRPGBossChannelDrain::ConeHalfAngleDegrees};
    for (FChannelField Field : ChannelFields) for (float Bad : {std::numeric_limits<float>::quiet_NaN(),std::numeric_limits<float>::infinity()})
    {
        FInput Case; Case.S.Windows.Empty(); Case.S.RecoveryEndSeconds=1.5f; Case.S.ChannelDrain.bEnabled=true;
        Case.S.ChannelDrain.StartSeconds=.267f; Case.S.ChannelDrain.EndSeconds=1.267f; Case.S.ChannelDrain.TickIntervalSeconds=.25f;
        Case.S.ChannelDrain.TickDamage=8.f; Case.S.ChannelDrain.HealFraction=.35f; Case.S.ChannelDrain.ConeRangeCm=600.f; Case.S.ChannelDrain.ConeHalfAngleDegrees=50.f;
        (Case.S.ChannelDrain).*(Field)=Bad;
        TestTrue(TEXT("every ChannelDrain numeric member rejects NaN/Infinity"),Has(RPGBossMoveCards::Validate(Case.S,Case.M),TEXT("MoveCard.NonFinite")));
    }
    return true;
}
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FBossMoveCardNumbers, "OneBossFight.Framework.MoveCard.Numbers", EAutomationTestFlags::EditorContext | EAutomationTestFlags::ProductFilter)
bool FBossMoveCardNumbers::RunTest(const FString&)
{
    using namespace BossMoveCardFixture;
    const float Values[] = {-1.f, 1000001.f, std::numeric_limits<float>::infinity(), std::numeric_limits<float>::quiet_NaN()};
    using FMember = float FRPGBossMoveCardSpec::*;
    const FMember Fields[] = {&FRPGBossMoveCardSpec::PlayRate,&FRPGBossMoveCardSpec::CommitSeconds,&FRPGBossMoveCardSpec::ActiveStartSeconds,&FRPGBossMoveCardSpec::ActiveEndSeconds,&FRPGBossMoveCardSpec::RecoveryEndSeconds,&FRPGBossMoveCardSpec::TrackDegreesPerSecond,&FRPGBossMoveCardSpec::WarpStartSeconds,&FRPGBossMoveCardSpec::WarpEndSeconds,&FRPGBossMoveCardSpec::WarpMaxDistanceCm,&FRPGBossMoveCardSpec::WarpMaxAngleDegrees,&FRPGBossMoveCardSpec::WarpStandoffCm,&FRPGBossMoveCardSpec::HoldAtSeconds,&FRPGBossMoveCardSpec::HoldMinSeconds,&FRPGBossMoveCardSpec::HoldMaxSeconds,&FRPGBossMoveCardSpec::MinRangeCm,&FRPGBossMoveCardSpec::MaxRangeCm,&FRPGBossMoveCardSpec::FrontConeDegrees,&FRPGBossMoveCardSpec::MaxVerticalDeltaCm,&FRPGBossMoveCardSpec::HPDamage};
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
    FInput Phases;
    TestTrue(TEXT("empty additional phases preserve legacy card validation"),RPGBossMoveCards::Validate(Phases.S,Phases.M).IsValid());
    Phases.S.AdditionalPhaseIds={TEXT("PhaseTwo")};
    TestTrue(TEXT("one additional phase is valid"),RPGBossMoveCards::Validate(Phases.S,Phases.M).IsValid());
    TestTrue(TEXT("primary phase remains eligible"),RPGBossMoveCards::IsEligibleInPhase(Phases.S,Phases.S.PhaseId));
    TestTrue(TEXT("additional phase is eligible"),RPGBossMoveCards::IsEligibleInPhase(Phases.S,TEXT("PhaseTwo")));
    TestFalse(TEXT("unlisted phase is ineligible"),RPGBossMoveCards::IsEligibleInPhase(Phases.S,TEXT("PhaseThree")));
    auto RejectAdditionalPhase=[this](TArray<FName> Extra)
    { FInput F; F.S.AdditionalPhaseIds=MoveTemp(Extra); TestTrue(TEXT("invalid AdditionalPhaseIds rejected"),Has(RPGBossMoveCards::Validate(F.S,F.M),TEXT("MoveCard.AdditionalPhaseIds"))); };
    RejectAdditionalPhase({NAME_None});
    RejectAdditionalPhase({TEXT("SyntheticPhase")});
    RejectAdditionalPhase({TEXT("PhaseTwo"),TEXT("PhaseTwo")});
    RejectAdditionalPhase({TEXT("PhaseA"),TEXT("PhaseB"),TEXT("PhaseC"),TEXT("PhaseD"),TEXT("PhaseE")});
    // A single invalid entry must reject the whole mixed set; valid entries may not mask it.
    RejectAdditionalPhase({TEXT("PhaseTwo"),NAME_None});
    RejectAdditionalPhase({TEXT("PhaseTwo"),TEXT("PhaseThree"),TEXT("PhaseThree")});
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
    using FRingField=float FRPGBossMoveWindow::*;
    const FRingField RingFields[]={&FRPGBossMoveWindow::RingStartRadiusCm,&FRPGBossMoveWindow::RingSpeedCmPerSecond,&FRPGBossMoveWindow::RingThicknessCm,&FRPGBossMoveWindow::RingHeightCm};
    for(FRingField Field:RingFields)for(float Bad:{std::numeric_limits<float>::quiet_NaN(),std::numeric_limits<float>::infinity()})
    {FInput F;MakeRing(F);(F.S.Windows[1]).*(Field)=Bad;TestTrue(TEXT("every ring numeric member rejects NaN/Infinity"),Has(RPGBossMoveCards::Validate(F.S,F.M),TEXT("MoveCard.NonFinite")));}
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
    for(float Bad:{std::numeric_limits<float>::quiet_NaN(),std::numeric_limits<float>::infinity()})
    {FInput F;MakeHold(F);MakeCue(F);F.S.Cues[1].TimeSeconds=Bad;TestTrue(TEXT("cue timestamp rejects NaN/Infinity"),Has(RPGBossMoveCards::Validate(F.S,F.M),TEXT("MoveCard.NonFinite")));}
    Reject([&](FInput& F){MakeCue(F);},TEXT("MoveCard.Cue"));   // the release cue without a hold
    Reject([&](FInput& F){MakeHold(F);MakeCue(F);F.S.Cues[1].Sound.Reset();},TEXT("MoveCard.Cue"));
    Reject([&](FInput& F){MakeHold(F);MakeCue(F);F.S.Cues[1].Visual=ERPGBossCueVisual::None;},TEXT("MoveCard.Cue"));
    Reject([&](FInput& F){MakeHold(F);MakeCue(F);F.S.Cues[1].Visual=static_cast<ERPGBossCueVisual>(255);},TEXT("MoveCard.Cue"));
    Reject([&](FInput& F){MakeHold(F);MakeCue(F);F.S.Cues[1].CueId=NAME_None;},TEXT("MoveCard.Cue"));
    Reject([&](FInput& F){MakeHold(F);MakeCue(F);F.S.Cues[1].TimeSeconds=F.S.RecoveryEndSeconds+.1f;},TEXT("MoveCard.Cue"));
    Reject([&](FInput& F){MakeHold(F);MakeCue(F);F.S.Cues[1].Visual=F.S.Cues[0].Visual;},TEXT("MoveCard.CueDistinct"));
    Reject([&](FInput& F){MakeHold(F);MakeCue(F);F.S.Cues[1].Sound=F.S.Cues[0].Sound;},TEXT("MoveCard.CueDistinct"));
    Reject([&](FInput& F){MakeHold(F);MakeCue(F);F.S.Cues[1].CueId=F.S.Cues[0].CueId;},TEXT("MoveCard.CueDistinct"));
    Reject([&](FInput& F){MakeHold(F);MakeCue(F);for(int32 I=0;I<8;++I){FRPGBossCue X=F.S.Cues[1];X.CueId=FName(*FString::Printf(TEXT("X%d"),I));F.S.Cues.Add(X);}},TEXT("MoveCard.Cue"));
    // BOSS-DEF-005: a defensive card has no hit window and no damage, its move starts after a readable telegraph (0.25 s), a backstep stays within 250 cm; bWarpAway belongs to a defensive card.
    auto MakeBackstep=[](FInput& F){F.S.Windows.Reset();F.S.HPDamage=0.f;F.S.bDefensive=true;F.S.bWarpAway=true;F.S.WarpStartSeconds=.4f;F.S.WarpEndSeconds=.7f;F.S.WarpMaxDistanceCm=150.f;F.S.WarpStandoffCm=300.f;F.S.ActiveStartSeconds=.4f;F.S.CommitSeconds=.1f;F.S.ActiveEndSeconds=.7f;F.S.RecoveryEndSeconds=1.2f;};
    {FInput F;MakeBackstep(F);TestTrue(TEXT("a backstep card without hit windows is valid"),RPGBossMoveCards::Validate(F.S,F.M).IsValid());}
    Reject([&](FInput& F){MakeBackstep(F);F.S.bWarpAway=false;F.S.WarpMaxDistanceCm=0.f;F.S.WarpMaxAngleDegrees=30.f;},TEXT("MoveCard.Defensive"));
    {FInput F;MakeBackstep(F);F.S.bWarpAway=false;F.S.WarpMaxDistanceCm=150.f;TestTrue(TEXT("a forward defensive reposition with positive distance is valid"),RPGBossMoveCards::Validate(F.S,F.M).IsValid());}
    Reject([&](FInput& F){F.S.Windows.Reset();},TEXT("MoveCard.Window"));   // no hit window and not defensive
    Reject([&](FInput& F){MakeBackstep(F);F.S.HPDamage=5.f;},TEXT("MoveCard.Defensive"));
    {FInput F;MakeBackstep(F);F.S.WarpStartSeconds=.3125f;F.S.ActiveStartSeconds=.3125f;TestTrue(TEXT("a move that starts at exactly 0.25 real seconds (0.3125 card seconds at rate 1.25) is valid"),RPGBossMoveCards::Validate(F.S,F.M).IsValid());}
    Reject([&](FInput& F){MakeBackstep(F);F.S.WarpStartSeconds=.2f;F.S.ActiveStartSeconds=.2f;},TEXT("MoveCard.Defensive"));
    Reject([&](FInput& F){MakeBackstep(F);F.S.WarpMaxDistanceCm=251.f;},TEXT("MoveCard.Defensive"));
    Reject([&](FInput& F){MakeBackstep(F);F.S.Windows.Add(FRPGBossMoveWindow());},TEXT("MoveCard.Defensive"));
    Reject([&](FInput& F){F.S.bWarpAway=true;},TEXT("MoveCard.Defensive"));   // away-warp on an attack card
    for (double Rate : {.5, 1., 1.25, 2.})
    {
        const double AtThreshold=.25*Rate;
        TestTrue(FString::Printf(TEXT("forward/backstep telegraph accepts exact real-time threshold at rate %.2f"),Rate),RPGBossDefense::TelegraphOk(AtThreshold,Rate));
        TestFalse(FString::Printf(TEXT("telegraph below threshold fails at rate %.2f"),Rate),RPGBossDefense::TelegraphOk(AtThreshold-.001,Rate));
    }
    for (double Distance : {.001, 100., 250., 250.001})
        TestEqual(FString::Printf(TEXT("backstep distance bound %.3f"),Distance),RPGBossDefense::BackstepDistanceOk(Distance),Distance<=250.);
    for (bool bArea : {false,true}) for (bool bChannel : {false,true})
    {
        if (!bArea&&!bChannel) continue;
        FInput Case; Case.S.Windows.Empty();
        Case.S.HPDamage=0.f;
        if (bArea) { Case.S.AreaEffect.bEnabled=true; Case.S.AreaEffect.ReleaseSeconds=.8f; Case.S.AreaEffect.DelaySeconds=.1f; Case.S.AreaEffect.RadiusCm=100.f; Case.S.AreaEffect.Damage=1.f; }
        if (bChannel) { Case.S.ChannelDrain.bEnabled=true; Case.S.ChannelDrain.StartSeconds=.4f; Case.S.ChannelDrain.EndSeconds=.8f; Case.S.ChannelDrain.TickIntervalSeconds=.2f; Case.S.ChannelDrain.TickDamage=1.f; Case.S.ChannelDrain.ConeRangeCm=100.f; Case.S.ChannelDrain.ConeHalfAngleDegrees=30.f; }
        Case.S.bDefensive=true; Case.S.WarpMaxDistanceCm=100.f; Case.S.WarpStartSeconds=.4f; Case.S.WarpEndSeconds=.7f;
        TestFalse(TEXT("defensive card cannot also enable an attack add-on"),RPGBossMoveCards::Validate(Case.S,Case.M).IsValid());
    }
    FInput Both; Both.S.Windows.Empty(); Both.S.HPDamage=0.f;
    Both.S.AreaEffect.bEnabled=true; Both.S.AreaEffect.ReleaseSeconds=.8f; Both.S.AreaEffect.DelaySeconds=.1f; Both.S.AreaEffect.RadiusCm=100.f; Both.S.AreaEffect.Damage=1.f;
    Both.S.ChannelDrain.bEnabled=true; Both.S.ChannelDrain.StartSeconds=.4f; Both.S.ChannelDrain.EndSeconds=.8f; Both.S.ChannelDrain.TickIntervalSeconds=.2f; Both.S.ChannelDrain.TickDamage=1.f; Both.S.ChannelDrain.ConeRangeCm=100.f; Both.S.ChannelDrain.ConeHalfAngleDegrees=30.f;
    TestTrue(TEXT("two otherwise valid add-ons are explicitly mutually exclusive"),Has(RPGBossMoveCards::Validate(Both.S,Both.M),TEXT("MoveCard.ChannelDrain")));
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
    F=FInput(); TSharedPtr<const FRPGCompiledBossMoveCard> DefaultOff;
    TestTrue(TEXT("legacy card snapshot compiles with both add-ons disabled"),RPGBossMoveCards::CompileMetadata(F.S,F.M,DefaultOff).IsValid());
    if (DefaultOff)
    {
        TestFalse(TEXT("AreaEffect default remains disabled in snapshot"),DefaultOff->Spec().AreaEffect.bEnabled);
        TestFalse(TEXT("ChannelDrain default remains disabled in snapshot"),DefaultOff->Spec().ChannelDrain.bEnabled);
        F.S.AreaEffect.bEnabled=true; F.S.ChannelDrain.bEnabled=true;
        TestFalse(TEXT("late source opt-in does not mutate prior compiled snapshot"),DefaultOff->Spec().AreaEffect.bEnabled||DefaultOff->Spec().ChannelDrain.bEnabled);
    }
    return true;
}
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FBossMoveCardOptInDefaultsOff, "OneBossFight.Framework.MoveCard.OptInDefaultsOff", EAutomationTestFlags::EditorContext | EAutomationTestFlags::ProductFilter)
bool FBossMoveCardOptInDefaultsOff::RunTest(const FString&)
{
    const FRPGBossMoveCardSpec Defaults;
    TestFalse(TEXT("warp ease-in/out is disabled by default"), Defaults.WarpEaseInOut);
    TestFalse(TEXT("defensive warp-away is disabled by default"), Defaults.bWarpAway);
    TestFalse(TEXT("defensive mode is disabled by default"), Defaults.bDefensive);
    TestEqual(TEXT("warp start defaults to off"), Defaults.WarpStartSeconds, 0.f);
    TestEqual(TEXT("warp end defaults to off"), Defaults.WarpEndSeconds, 0.f);
    TestEqual(TEXT("warp distance defaults to off"), Defaults.WarpMaxDistanceCm, 0.f);
    TestEqual(TEXT("warp angle defaults to off"), Defaults.WarpMaxAngleDegrees, 0.f);
    TestEqual(TEXT("warp standoff defaults to off"), Defaults.WarpStandoffCm, 0.f);
    return true;
}
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FBossMoveCardValidationFuzz,"OneBossFight.Framework.MoveCard.ValidationFuzz",EAutomationTestFlags::EditorContext|EAutomationTestFlags::ProductFilter)
bool FBossMoveCardValidationFuzz::RunTest(const FString&)
{
    using namespace BossMoveCardFixture;FRandomStream Random(0x92A11);int32 Invalid=0;
    using FMember=float FRPGBossMoveCardSpec::*;
    const FMember Fields[]={&FRPGBossMoveCardSpec::PlayRate,&FRPGBossMoveCardSpec::CommitSeconds,&FRPGBossMoveCardSpec::ActiveStartSeconds,&FRPGBossMoveCardSpec::ActiveEndSeconds,&FRPGBossMoveCardSpec::RecoveryEndSeconds,&FRPGBossMoveCardSpec::TrackDegreesPerSecond,&FRPGBossMoveCardSpec::MinRangeCm,&FRPGBossMoveCardSpec::MaxRangeCm,&FRPGBossMoveCardSpec::FrontConeDegrees,&FRPGBossMoveCardSpec::HPDamage};
    for(int32 I=0;I<1000;++I)
    {
        FInput F;const int32 Kind=Random.RandRange(0,5);const float V=Kind==0?std::numeric_limits<float>::quiet_NaN():Kind==1?std::numeric_limits<float>::infinity():Kind==2?-1.f:Kind==3?1000001.f:Random.FRandRange(0.f,1000.f);
        F.S.*Fields[Random.RandRange(0,static_cast<int32>(UE_ARRAY_COUNT(Fields))-1)]=V;
        if((I%3)==0)F.S.Windows[1].RadiusCm=V;
        if((I%7)==0)F.S.Windows[1].StartSeconds=V;
        const FRPGBossMoveIssues Result=RPGBossMoveCards::Validate(F.S,F.M);
        if(!Result.IsValid())
        {
            ++Invalid;TestTrue(*FString::Printf(TEXT("invalid card fuzz case %d returns at least one named issue"),I),!Result.Errors.IsEmpty());
            for(const FString& Issue:Result.Errors)TestTrue(TEXT("issue uses a MoveCard token"),Issue.StartsWith(TEXT("MoveCard.")));
        }
    }
    TestTrue(TEXT("fuzz reaches invalid card cases"),Invalid>0);
    return true;
}
#endif
