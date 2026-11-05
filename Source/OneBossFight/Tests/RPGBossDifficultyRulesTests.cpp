// Copyright One Boss Fight. All Rights Reserved.
#include "Player/RPGBossDifficultyRules.h"
#include "Misc/AutomationTest.h"
#include <limits>

#if WITH_DEV_AUTOMATION_TESTS
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FBossDifficultyRules,"OneBossFight.Framework.Difficulty.Rules",EAutomationTestFlags::EditorContext|EAutomationTestFlags::ProductFilter)
bool FBossDifficultyRules::RunTest(const FString&)
{
    using namespace RPGBossDifficulty;FConfig C;TestTrue(TEXT("default config valid"),IsValid(C));
    const FScales Easy=Evaluate(0.,C),Hard=Evaluate(1.,C);TestEqual(TEXT("easy begins at low endpoints"),Easy.Damage,C.DamageMin);TestEqual(TEXT("hard reaches damage endpoint"),Hard.Damage,C.DamageMax);
    TestEqual(TEXT("hard reaches speed endpoint"),Hard.Speed,C.SpeedMax);TestEqual(TEXT("hard reaches telegraph endpoint"),Hard.Telegraph,C.TelegraphMax);
    FScales Previous=Easy;for(int32 I=1;I<=1000;++I){const FScales Now=Evaluate(double(I)/1000.,C);TestTrue(TEXT("three difficulty scales are monotonic and bounded"),Now.Damage>=Previous.Damage&&Now.Speed>=Previous.Speed&&Now.Telegraph>=Previous.Telegraph&&Now.Damage<=3.&&Now.Speed<=2.&&Now.Telegraph<=2.);Previous=Now;}
    TestEqual(TEXT("invalid difficulty returns neutral scales"),Evaluate(std::numeric_limits<double>::quiet_NaN(),C).Damage,1.);
    C.SpeedMax=3.;TestFalse(TEXT("out-of-bound config rejected"),IsValid(C));return true;
}
#endif
