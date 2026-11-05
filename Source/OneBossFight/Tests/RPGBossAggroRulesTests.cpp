// Copyright One Boss Fight. All Rights Reserved.
#include "Player/RPGBossAggroRules.h"
#include "Misc/AutomationTest.h"
#include <limits>

#if WITH_DEV_AUTOMATION_TESTS
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FBossAggroRules,"OneBossFight.Framework.Aggro.Rules",EAutomationTestFlags::EditorContext|EAutomationTestFlags::ProductFilter)
bool FBossAggroRules::RunTest(const FString&)
{
    using namespace RPGBossAggro;
    EBand B=Step(EBand::Balanced,200.,false,false); TestTrue(TEXT("near range enters close band"),B==EBand::Close);
    TestTrue(TEXT("close band persists inside exit threshold"),Step(B,275.,false,false)==EBand::Close);
    B=Step(B,310.,false,false); TestTrue(TEXT("close band exits after hysteresis threshold"),B==EBand::Balanced);
    B=Step(B,750.,false,false); TestTrue(TEXT("far range enters far band"),B==EBand::Far);
    TestTrue(TEXT("far band persists above exit threshold"),Step(B,650.,false,false)==EBand::Far);
    B=Step(B,550.,false,false); TestTrue(TEXT("far band exits below hysteresis threshold"),B==EBand::Balanced);
    TestTrue(TEXT("behavior can request close/far preference"),Step(EBand::Balanced,500.,true,false)==EBand::Close&&Step(EBand::Balanced,500.,false,true)==EBand::Far);
    TestTrue(TEXT("dodge rate enters far at the enter threshold"),Step(EBand::Balanced,500.,false,false,.6)==EBand::Far);
    TestTrue(TEXT("dodge rate holds far above the lower exit threshold"),Step(EBand::Far,500.,false,false,.4)==EBand::Far);
    TestTrue(TEXT("dodge rate exits far at the hysteresis threshold"),Step(EBand::Far,500.,false,false,.3)==EBand::Balanced);
    TestTrue(TEXT("dodge rate below enter does not flap from balanced"),Step(EBand::Balanced,500.,false,false,.5)==EBand::Balanced);
    TestTrue(TEXT("contradictory behavior and invalid range preserve state"),Step(EBand::Balanced,500.,true,true)==EBand::Balanced&&Step(EBand::Far,-1.,false,false)==EBand::Far);
    TestTrue(TEXT("NaN range preserves the current band"),Step(EBand::Close,std::numeric_limits<double>::quiet_NaN(),false,false)==EBand::Close);
    TestTrue(TEXT("infinite dodge rate preserves the current band"),Step(EBand::Far,500.,false,false,std::numeric_limits<double>::infinity())==EBand::Far);
    return true;
}
#endif
