// Copyright One Boss Fight. All Rights Reserved.
#include "Player/RPGBossBakeFreshnessRules.h"
#include "Misc/AutomationTest.h"

#if WITH_DEV_AUTOMATION_TESTS
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FBossBakeFreshnessRules,"OneBossFight.Framework.BakeFreshness.Rules",EAutomationTestFlags::EditorContext|EAutomationTestFlags::ProductFilter)
bool FBossBakeFreshnessRules::RunTest(const FString&)
{
    using namespace RPGBossBakeFreshness;TestTrue(TEXT("matching nonzero fingerprints are fresh"),IsFresh(0x1234,0x1234));
    TestFalse(TEXT("changed source fingerprint is stale"),IsFresh(0x1234,0x5678));TestFalse(TEXT("missing current fingerprint is unknown"),IsFresh(0,0x1234));
    TestFalse(TEXT("missing baked fingerprint is unknown"),IsFresh(0x1234,0));return true;
}
#endif
