// Copyright One Boss Fight. All Rights Reserved.
#include "Player/RPGBossReactiveDodgeRules.h"
#include "Misc/AutomationTest.h"
#include <limits>

#if WITH_DEV_AUTOMATION_TESTS
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FBossReactiveDodgeRules,"OneBossFight.Framework.ReactiveDodge.Rules",EAutomationTestFlags::EditorContext|EAutomationTestFlags::ProductFilter)
bool FBossReactiveDodgeRules::RunTest(const FString&)
{
    using namespace RPGBossReactiveDodge;FConfig C;TestTrue(TEXT("default configuration valid"),IsValid(C));
    TestEqual(TEXT("light attack never triggers reactive dodge"),Chance(false,100),0.);TestEqual(TEXT("below hit threshold has no chance"),Chance(true,1,C),0.);
    const double AtThreshold=Chance(true,2,C),After=Chance(true,5,C);TestTrue(TEXT("chance increases with recent hits"),AtThreshold>0.&&After>AtThreshold);TestTrue(TEXT("chance clamps at configured ceiling"),Chance(true,100,C)==C.MaxChance);
    TestTrue(TEXT("roll at zero evades when chance is positive"),ShouldDodge(true,2,0.,C));TestTrue(TEXT("roll below chance evades"),ShouldDodge(true,2,AtThreshold*.5,C));TestFalse(TEXT("roll at chance does not evade"),ShouldDodge(true,2,AtThreshold,C));
    TestFalse(TEXT("non-finite random roll fails closed"),ShouldDodge(true,5,std::numeric_limits<double>::quiet_NaN(),C));
    C.HitsToStart=0;C.BaseChance=0.;C.ChancePerHit=.1;C.MaxChance=1.;
    TestEqual(TEXT("maximum recent-hit count does not overflow"),Chance(true,std::numeric_limits<int32>::max(),C),1.);
    C.MaxChance=1.1;TestFalse(TEXT("chance above one is invalid"),IsValid(C));TestEqual(TEXT("invalid config has no chance"),Chance(true,5,C),0.);
    return true;
}
#endif
