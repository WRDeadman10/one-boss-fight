// Copyright One Boss Fight. All Rights Reserved.
// BQ-16 (Queue BQ batch 4; KI-065): the A6 leap's landing point is chosen by the pack and was never validated against the arena. The
// opt-in URPGBossShockwave::LandingArenaRadiusCm (0 = off, the default) makes Launch() start no wave for a landing outside the
// configured arena. This pins the pure decision. Live landing positions and the arena centre/radius to configure stay ENG. Written, not compiled/run.
#include "Player/RPGBossShockwave.h"
#include "Misc/AutomationTest.h"
#include <limits>

#if WITH_DEV_AUTOMATION_TESTS
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FShockwaveLandingTest, "OneBossFight.Boss.ShockwaveLandingBounds", EAutomationTestFlags::EditorContext | EAutomationTestFlags::ProductFilter)
bool FShockwaveLandingTest::RunTest(const FString&)
{
	const FVector Center(100.f, 200.f, 0.f);
	const float NaN = std::numeric_limits<float>::quiet_NaN();
	TestTrue(TEXT("off (radius 0): always allowed, behaviour unchanged"), URPGBossShockwave::IsLandingAllowed(FVector(1.e6f, 0.f, 0.f), Center, 0.f));
	TestTrue(TEXT("negative radius treated as off"), URPGBossShockwave::IsLandingAllowed(FVector(1.e6f, 0.f, 0.f), Center, -5.f));
	TestTrue(TEXT("inside the arena"), URPGBossShockwave::IsLandingAllowed(FVector(400.f, 200.f, 0.f), Center, 500.f));
	TestTrue(TEXT("exactly on the edge (<=)"), URPGBossShockwave::IsLandingAllowed(FVector(600.f, 200.f, 0.f), Center, 500.f));
	TestFalse(TEXT("outside the arena: no wave"), URPGBossShockwave::IsLandingAllowed(FVector(601.f, 200.f, 0.f), Center, 500.f));
	TestTrue(TEXT("height is ignored (2D distance)"), URPGBossShockwave::IsLandingAllowed(FVector(100.f, 200.f, 5000.f), Center, 500.f));
	TestFalse(TEXT("NaN radius fails closed"), URPGBossShockwave::IsLandingAllowed(Center, Center, NaN));
	TestFalse(TEXT("infinite radius fails closed"), URPGBossShockwave::IsLandingAllowed(Center, Center, std::numeric_limits<float>::infinity()));
	TestFalse(TEXT("X-2338: -inf radius fails closed (not treated as off)"), URPGBossShockwave::IsLandingAllowed(FVector(1.e6f, 0.f, 0.f), Center, -std::numeric_limits<float>::infinity()));
	TestFalse(TEXT("NaN landing fails closed"), URPGBossShockwave::IsLandingAllowed(FVector(NaN, 0.f, 0.f), Center, 500.f));
	const URPGBossShockwave* Defaults = GetDefault<URPGBossShockwave>();
	TestTrue(TEXT("class default keeps the check off"), Defaults && Defaults->LandingArenaRadiusCm == 0.f);
	return true;
}
#endif
