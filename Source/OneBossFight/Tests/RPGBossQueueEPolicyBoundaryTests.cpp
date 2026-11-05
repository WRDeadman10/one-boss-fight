// Copyright One Boss Fight. All Rights Reserved.
#include "Player/RPGBossAggroRules.h"
#include "Misc/AutomationTest.h"

#if WITH_DEV_AUTOMATION_TESTS
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FBossAggroInvalidConfigPreservesState,
    "OneBossFight.Framework.Aggro.InvalidConfigPreservesState",
    EAutomationTestFlags::EditorContext|EAutomationTestFlags::ProductFilter)
bool FBossAggroInvalidConfigPreservesState::RunTest(const FString&)
{
    RPGBossAggro::FConfig Config; Config.ExitCloseCm=Config.EnterCloseCm;
    TestTrue(TEXT("invalid threshold ordering preserves the current Far band"),RPGBossAggro::Step(RPGBossAggro::EBand::Far,200.,false,false,Config)==RPGBossAggro::EBand::Far);
    return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FBossAggroBehaviorOverrideAtBoundaries,
    "OneBossFight.Framework.Aggro.BehaviorOverrideAtBoundaries",
    EAutomationTestFlags::EditorContext|EAutomationTestFlags::ProductFilter)
bool FBossAggroBehaviorOverrideAtBoundaries::RunTest(const FString&)
{
    using RPGBossAggro::EBand;
    TestTrue(TEXT("hugging keeps Close at the exact close exit range"),RPGBossAggro::Step(EBand::Close,300.,true,false)==EBand::Close);
    TestTrue(TEXT("kiting keeps Far at the exact far exit range"),RPGBossAggro::Step(EBand::Far,600.,false,true)==EBand::Far);
    return true;
}
#endif
