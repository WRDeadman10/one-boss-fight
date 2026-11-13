// Copyright One Boss Fight. All Rights Reserved.
// BL-10 (lane BL, X-2164): RPGBossAggro guard clauses verified untested in BL-01..05 (C-1420). EnterCloseCm<0 and ExitCloseCm==EnterCloseCm are already covered
// (RPGBossQueueEBoundaryTests.cpp:198,202; RPGBossQueueEPolicyBoundaryTests.cpp:11-12) and are deliberately not repeated. Asserts existing behaviour only.
#include "Player/RPGBossAggroRules.h"
#include "Misc/AutomationTest.h"
#include <limits>

#if WITH_DEV_AUTOMATION_TESTS
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FBossAggroGuards, "OneBossFight.Framework.Aggro.Guards", EAutomationTestFlags::EditorContext | EAutomationTestFlags::ProductFilter)
bool FBossAggroGuards::RunTest(const FString&)
{
    using namespace RPGBossAggro;
    const double NaN = std::numeric_limits<double>::quiet_NaN();
    const double Inf = std::numeric_limits<double>::infinity();

    // For each starting band, a range that WOULD move it with a valid config (positive controls below).
    struct FCase { EBand Start; double RangeCm; EBand MovesTo; };
    const FCase Cases[] = { {EBand::Balanced, 100., EBand::Close}, {EBand::Close, 500., EBand::Balanced}, {EBand::Far, 400., EBand::Balanced} };
    const FConfig Valid;
    for (const FCase& Case : Cases)
    {
        TestTrue(*FString::Printf(TEXT("control: band %d moves with a valid config"), int32(Case.Start)), Step(Case.Start, Case.RangeCm, false, false, 0., Valid) == Case.MovesTo);
        TestTrue(*FString::Printf(TEXT("negative finite dodge rate preserves band %d"), int32(Case.Start)), Step(Case.Start, Case.RangeCm, false, false, -.1, Valid) == Case.Start);
    }

    auto ExpectPreserved = [&](const TCHAR* What, const FConfig& C)
    {
        TestFalse(What, IsValid(C));
        for (const FCase& Case : Cases)
        {
            TestTrue(*FString::Printf(TEXT("%s preserves band %d"), What, int32(Case.Start)), Step(Case.Start, Case.RangeCm, false, false, 0., C) == Case.Start);
        }
    };

    // Each config field non-finite, one at a time (NaN, +Inf, -Inf).
    for (double Bad : {NaN, Inf, -Inf})
    {
        FConfig C;
        C = Valid; C.EnterCloseCm = Bad; ExpectPreserved(TEXT("non-finite EnterCloseCm"), C);
        C = Valid; C.ExitCloseCm = Bad; ExpectPreserved(TEXT("non-finite ExitCloseCm"), C);
        C = Valid; C.EnterFarCm = Bad; ExpectPreserved(TEXT("non-finite EnterFarCm"), C);
        C = Valid; C.ExitFarCm = Bad; ExpectPreserved(TEXT("non-finite ExitFarCm"), C);
        C = Valid; C.EnterDodgeRate = Bad; ExpectPreserved(TEXT("non-finite EnterDodgeRate"), C);
        C = Valid; C.ExitDodgeRate = Bad; ExpectPreserved(TEXT("non-finite ExitDodgeRate"), C);
        C = Valid; C.DodgeRateWindowSeconds = Bad; ExpectPreserved(TEXT("non-finite DodgeRateWindowSeconds"), C);
    }
    // Ordering / sign clauses, each isolated (every other clause stays valid).
    { FConfig C; C.ExitFarCm = C.ExitCloseCm; ExpectPreserved(TEXT("ExitFarCm equal to ExitCloseCm"), C); }
    { FConfig C; C.EnterFarCm = C.ExitFarCm; ExpectPreserved(TEXT("EnterFarCm equal to ExitFarCm"), C); }
    { FConfig C; C.ExitDodgeRate = -.1; ExpectPreserved(TEXT("negative ExitDodgeRate"), C); }
    { FConfig C; C.EnterDodgeRate = C.ExitDodgeRate; ExpectPreserved(TEXT("EnterDodgeRate equal to ExitDodgeRate"), C); }
    { FConfig C; C.DodgeRateWindowSeconds = 0.; ExpectPreserved(TEXT("DodgeRateWindowSeconds 0"), C); }
    { FConfig C; C.DodgeRateWindowSeconds = -1.; ExpectPreserved(TEXT("DodgeRateWindowSeconds negative"), C); }
    return true;
}
#endif
