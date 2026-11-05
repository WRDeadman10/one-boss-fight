// Copyright One Boss Fight. All Rights Reserved.
#include "Player/RPGBossTrackRules.h"
#include "Misc/AutomationTest.h"

#if WITH_DEV_AUTOMATION_TESTS
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FBossTrackRulesSweep,"OneBossFight.Framework.Track.Sweep",EAutomationTestFlags::EditorContext|EAutomationTestFlags::ProductFilter)
bool FBossTrackRulesSweep::RunTest(const FString&)
{
    using namespace RPGBossTrack;
    // A full heading sweep crossed with a broad range sweep catches wrap and domain edge cases without asserting subtraction boundaries.
    bool bYawFinite=true, bYawBounded=true;
    for (int32 Current=0;Current<360;++Current)
    {
        for (int32 Target=0;Target<360;++Target)
        {
            const float Next=StepYaw(float(Current),float(Target),180.f,1.f/60.f,false);
            bYawFinite&=FMath::IsFinite(Next);
            bYawBounded&=FMath::Abs(FMath::FindDeltaAngleDegrees(float(Current),Next))<=3.001f;
        }
    }
    TestTrue(TEXT("StepYaw is finite and within one tick's angular budget across the 360x360 grid"),bYawFinite&&bYawBounded);
    bool bWarpFinite=true, bWarpBounded=true, bWarpMonotonic=true, bGrabTransitions=true, bRingFinite=true;
    for (int32 Range=0;Range<=3600;Range+=10)
    {
        const double Needed=double(Range), Budget=137.25;
        double Previous=0.;
        for (int32 Tick=1;Tick<=12;++Tick)
        {
            const double Step=WarpStepCm(Needed,Budget,double(Tick)/60.,.2);
            bWarpFinite&=FMath::IsFinite(Step)&&Step>=0.;
            bWarpBounded&=Step<=Budget+1.e-9&&Step<=Needed+1.e-9;
            bWarpMonotonic&=Step+1.e-9>=Previous;
            Previous=Step;
        }
        FGrabState Grab;
        const EGrabEvent Caught=GrabStep(Grab,true,0.,.5,false);
        bGrabTransitions&=Caught==EGrabEvent::Caught&&Grab.bHeld;
        bGrabTransitions&=GrabStep(Grab,false,.25,.5,false)==EGrabEvent::None;
        bGrabTransitions&=GrabStep(Grab,false,.5,.5,false)==EGrabEvent::Released&&!Grab.bHeld;
        const double Radius=RingFront(20.,700.,double(Range)/1000.);
        bRingFinite&=FMath::IsFinite(Radius)&&Radius>=20.&&RingTouches(Radius-5.,Radius,10.,Radius-2.,2.,0.,50.)==RingTouches(Radius-5.,Radius,10.,Radius-2.,2.,0.,50.);
    }
    TestTrue(TEXT("warp is finite, bounded, and monotonic across the range grid"),bWarpFinite&&bWarpBounded&&bWarpMonotonic);
    TestTrue(TEXT("grab catches, holds, and releases across the range grid"),bGrabTransitions);
    TestTrue(TEXT("ring front/contact stay finite and deterministic across the range grid"),bRingFinite);
    return true;
}
#endif
