// Copyright One Boss Fight. All Rights Reserved.
// BQ-04 (Queue BQ batch 1; KI-128 family): URPGBossPosture::ApplyPostureDamage now guards with RPGBossMath::IsValidDrainAmount.
// Before, the guard was `Amount <= 0.f`, which a NaN amount passes; `FMath::Max(0.f, Posture - NaN)` then returns NaN (0 >= NaN is false),
// permanently poisoning the posture pool. This pins the pure guard and the arithmetic hazard it closes. Written, not compiled/run
// (Lead C-1155 build required).
#include "Player/RPGBossMath.h"
#include "Math/UnrealMathUtility.h"
#include "Misc/AutomationTest.h"
#include <limits>

#if WITH_DEV_AUTOMATION_TESTS
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FPostureDrainFiniteTest, "OneBossFight.Framework.Posture.DrainAmountFinite", EAutomationTestFlags::EditorContext | EAutomationTestFlags::ProductFilter)
bool FPostureDrainFiniteTest::RunTest(const FString&)
{
	const float NaN = std::numeric_limits<float>::quiet_NaN();
	const float Inf = std::numeric_limits<float>::infinity();
	// The hazard the guard closes: Max(0, finite - NaN) is NaN, so the old `Amount <= 0` guard let NaN poison the pool.
	TestFalse(TEXT("NaN passes an `Amount <= 0` guard"), NaN <= 0.f);
	TestTrue(TEXT("Max(0, Posture - NaN) is NaN"), FMath::IsNaN(FMath::Max(0.f, 50.f - NaN)));
	// The guard: finite and positive only.
	TestFalse(TEXT("NaN refused"), RPGBossMath::IsValidDrainAmount(NaN));
	TestFalse(TEXT("+inf refused"), RPGBossMath::IsValidDrainAmount(Inf));
	TestFalse(TEXT("-inf refused"), RPGBossMath::IsValidDrainAmount(-Inf));
	TestFalse(TEXT("zero refused"), RPGBossMath::IsValidDrainAmount(0.f));
	TestFalse(TEXT("negative refused"), RPGBossMath::IsValidDrainAmount(-1.f));
	TestTrue(TEXT("positive accepted"), RPGBossMath::IsValidDrainAmount(20.f));
	TestTrue(TEXT("smallest positive accepted"), RPGBossMath::IsValidDrainAmount(std::numeric_limits<float>::denorm_min()));
	TestTrue(TEXT("largest finite accepted"), RPGBossMath::IsValidDrainAmount(std::numeric_limits<float>::max()));
	// Accepted amounts keep the pool finite and clamped (the arithmetic ApplyPostureDamage performs).
	TestTrue(TEXT("a FLT_MAX drain clamps to zero"), FMath::Max(0.f, 100.f - std::numeric_limits<float>::max()) == 0.f);
	// Framework boss sink (ApplyHit via ApplyPlayerAttackHit: Row.PostureDamage is not finite-checked upstream).
	TestTrue(TEXT("Min(Posture, NaN) is NaN without the sink guard"), FMath::IsNaN(FMath::Min(50.0, double(NaN))));
	TestTrue(TEXT("NaN row posture drains 0"), RPGBossMath::SanitizeDrainAmount(double(NaN)) == 0.);
	TestTrue(TEXT("+inf row posture drains 0"), RPGBossMath::SanitizeDrainAmount(double(Inf)) == 0.);
	TestTrue(TEXT("negative row posture drains 0"), RPGBossMath::SanitizeDrainAmount(-5.) == 0.);
	TestTrue(TEXT("zero stays zero (unchanged path)"), RPGBossMath::SanitizeDrainAmount(0.) == 0.);
	TestTrue(TEXT("finite positive passes through"), RPGBossMath::SanitizeDrainAmount(12.5) == 12.5);
	TestTrue(TEXT("sanitized drain keeps the pool finite"), FMath::IsFinite(50.0 - FMath::Min(50.0, RPGBossMath::SanitizeDrainAmount(double(NaN)))));
	// RegenStep (X-2325): NaN rate/Dt keeps the posture; finite overflow clamps to Max; normal steps unchanged.
	using RPGBossMath::RegenStep;
	TestTrue(TEXT("regen: NaN rate keeps posture"), RegenStep(40.f, 100.f, 20.0, 0.0, 6.f, NaN, 1.f) == 40.f);
	TestTrue(TEXT("regen: NaN dt keeps posture"), RegenStep(40.f, 100.f, 20.0, 0.0, 6.f, 13.f, NaN) == 40.f);
	TestTrue(TEXT("regen: finite overflow clamps to max"), RegenStep(40.f, 100.f, 20.0, 0.0, 6.f, std::numeric_limits<float>::max(), 10.f) == 100.f);
	TestTrue(TEXT("regen: +inf rate clamps to max"), RegenStep(40.f, 100.f, 20.0, 0.0, 6.f, Inf, 1.f) == 100.f);
	TestTrue(TEXT("regen: normal step unchanged"), RegenStep(40.f, 100.f, 20.0, 0.0, 6.f, 13.f, 1.f) == 53.f);
	TestTrue(TEXT("regen: -inf rate keeps posture"), RegenStep(40.f, 100.f, 20.0, 0.0, 6.f, -Inf, 1.f) == 40.f);
	TestTrue(TEXT("regen: result stays finite for NaN input"), FMath::IsFinite(RegenStep(40.f, 100.f, 20.0, 0.0, 6.f, NaN, NaN)));
	return true;
}
#endif
