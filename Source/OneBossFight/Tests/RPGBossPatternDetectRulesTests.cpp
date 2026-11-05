// Copyright One Boss Fight. All Rights Reserved.
#include "Player/RPGBossPatternDetectRules.h"
#include "Misc/AutomationTest.h"

#if WITH_DEV_AUTOMATION_TESTS
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FBossPatternDetectRules,"OneBossFight.Framework.PatternDetect.Rules",EAutomationTestFlags::EditorContext|EAutomationTestFlags::ProductFilter)
bool FBossPatternDetectRules::RunTest(const FString&)
{
    using namespace RPGBossPatternDetect;FState S;
    TestFalse(TEXT("first observation is not a repeat"),Observe(S,TEXT("BackDodge"),3));TestEqual(TEXT("first count"),S.Consecutive,1);
    TestFalse(TEXT("second observation below threshold"),Observe(S,TEXT("BackDodge"),3));TestTrue(TEXT("third matching observation reaches threshold"),Observe(S,TEXT("BackDodge"),3));
    TestFalse(TEXT("different pattern starts a fresh streak"),Observe(S,TEXT("Roll"),2));TestEqual(TEXT("changed pattern count"),S.Consecutive,1);
    TestFalse(TEXT("empty pattern resets"),Observe(S,NAME_None,2));TestTrue(TEXT("reset cleared identity"),S.LastPattern.IsNone()&&S.Consecutive==0);
    TestFalse(TEXT("threshold one is rejected safely"),Observe(S,TEXT("Roll"),1));TestFalse(TEXT("unbounded threshold is rejected safely"),Observe(S,TEXT("Roll"),101));
    FState Long;for(int32 I=0;I<1000;++I)Observe(Long,TEXT("Same"),2);TestEqual(TEXT("streak counter is bounded"),Long.Consecutive,100);
    return true;
}
#endif
