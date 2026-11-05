// Copyright One Boss Fight. All Rights Reserved.
#include "Player/RPGBossPunishLimiterRules.h"
#include "Misc/AutomationTest.h"

#if WITH_DEV_AUTOMATION_TESTS
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FBossPunishLimiterRules,"OneBossFight.Framework.PunishLimiter.Rules",EAutomationTestFlags::EditorContext|EAutomationTestFlags::ProductFilter)
bool FBossPunishLimiterRules::RunTest(const FString&)
{
    using namespace RPGBossPunishLimiter;FState S;constexpr int32 Max=3;
    TestTrue(TEXT("first use available"),CanUse(S,Max));for(int32 I=0;I<Max;++I)TestTrue(TEXT("record each allowed use"),RecordUse(S,Max));
    TestEqual(TEXT("use count reaches cap"),S.Uses,Max);TestFalse(TEXT("no use after cap"),CanUse(S,Max));TestFalse(TEXT("over-cap record refused"),RecordUse(S,Max));TestEqual(TEXT("refusal does not increment"),S.Uses,Max);
    Reset(S);TestTrue(TEXT("fight reset restores budget"),CanUse(S,Max)&&S.Uses==0);
    S.Uses=-1;TestFalse(TEXT("corrupt negative use count fails closed"),CanUse(S,Max));TestFalse(TEXT("invalid zero budget fails closed"),CanUse(FState(),0));
    return true;
}
#endif
