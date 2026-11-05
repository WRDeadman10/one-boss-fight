// Copyright One Boss Fight. All Rights Reserved.
#include "Player/RPGBossWarpCurveRules.h"
#include "Misc/AutomationTest.h"

#if WITH_DEV_AUTOMATION_TESTS
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FBossWarpCurveRules,"OneBossFight.Framework.WarpCurve.Rules",EAutomationTestFlags::EditorContext|EAutomationTestFlags::ProductFilter)
bool FBossWarpCurveRules::RunTest(const FString&)
{
    using namespace RPGBossWarpCurve;
    for(ECurve C:{ECurve::Linear,ECurve::Smooth,ECurve::Overshoot}){TestEqual(TEXT("curve starts at zero"),Fraction(0.,C),0.);TestEqual(TEXT("curve ends at same total displacement"),Fraction(1.,C),1.);}
    TestEqual(TEXT("linear midpoint"),Fraction(.5,ECurve::Linear),.5);TestEqual(TEXT("smooth midpoint"),Fraction(.5,ECurve::Smooth),.5);
    TestTrue(TEXT("overshoot curve passes the endpoint before returning to it"),Fraction(.5,ECurve::Overshoot)>1.);
    TestEqual(TEXT("time clamps before start"),Fraction(-1.,ECurve::Linear),0.);TestEqual(TEXT("time clamps after end"),Fraction(2.,ECurve::Smooth),1.);
    TestEqual(TEXT("invalid overshoot amount fails closed"),Fraction(.5,ECurve::Overshoot,1.),0.);
    return true;
}
#endif
