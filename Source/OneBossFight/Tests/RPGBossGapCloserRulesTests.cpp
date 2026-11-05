// Copyright One Boss Fight. All Rights Reserved.
#include "Player/RPGBossGapCloserRules.h"
#include "Misc/AutomationTest.h"
#include <limits>

#if WITH_DEV_AUTOMATION_TESTS
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FBossGapCloserRules,"OneBossFight.Framework.GapCloser.Rules",EAutomationTestFlags::EditorContext|EAutomationTestFlags::ProductFilter)
bool FBossGapCloserRules::RunTest(const FString&)
{
    using namespace RPGBossGapCloser;TestFalse(TEXT("inside exit range does not start chase"),ShouldClose(false,500.,250.,600.));
    TestTrue(TEXT("beyond exit range starts chase"),ShouldClose(false,601.,250.,600.));TestTrue(TEXT("active chase persists above enter range"),ShouldClose(true,251.,250.,600.));
    TestFalse(TEXT("active chase stops at enter boundary"),ShouldClose(true,250.,250.,600.));TestFalse(TEXT("invalid reversed hysteresis fails closed"),ShouldClose(false,700.,600.,250.));
    TestFalse(TEXT("NaN range fails closed"),ShouldClose(false,std::numeric_limits<double>::quiet_NaN(),250.,600.));return true;
}
#endif
