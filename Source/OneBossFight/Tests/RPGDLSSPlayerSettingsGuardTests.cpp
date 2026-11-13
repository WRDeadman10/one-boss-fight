// Copyright One Boss Fight. All Rights Reserved.
// BL-73 (lane BL, X-2193): RPGDLSSPlayerSettingsRules::Resolve falls back to TSR for an unknown EPlayerMode, including when DLSS is supported.
// All declared modes (supported / unsupported) and Off are already covered by RPGDLSSPlayerSettingsRulesTests.cpp. Asserts existing behaviour only.
#include "Player/RPGDLSSPlayerSettingsRules.h"
#include "Misc/AutomationTest.h"

#if WITH_DEV_AUTOMATION_TESTS
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FRPGDLSSPlayerSettingsGuardsTest, "OneBossFight.Player.DLSSPlayerSettingsGuards", EAutomationTestFlags::EditorContext | EAutomationTestFlags::ProductFilter)
bool FRPGDLSSPlayerSettingsGuardsTest::RunTest(const FString&)
{
    using namespace RPGDLSSPlayerSettingsRules;
    TestTrue(TEXT("control: supported Quality resolves to Quality"), Resolve(EPlayerMode::Quality, true) == ERuntimeMode::Quality);
    TestTrue(TEXT("unknown mode with DLSS supported falls back to TSR"), Resolve(static_cast<EPlayerMode>(99), true) == ERuntimeMode::TSR);
    TestTrue(TEXT("unknown mode without DLSS falls back to TSR"), Resolve(static_cast<EPlayerMode>(99), false) == ERuntimeMode::TSR);
    return true;
}
#endif
