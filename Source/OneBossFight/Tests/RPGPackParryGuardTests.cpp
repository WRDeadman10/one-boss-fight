// Copyright One Boss Fight. All Rights Reserved.
// BL-76 (lane BL): RPGPackParry::EvaluateCandidate rejects a negative or non-finite RequiredSeconds / LossTolerance once the wait is over, and confirms at
// the exact LossTolerance boundary (HealthNow == HealthBefore - tolerance). Every rejection below would be Confirmed without its guard. Existing pending,
// confirmed, loss, unknown-health and NaN health/elapsed cases are not repeated. Asserts existing behaviour only.
#include "Player/RPGPackParryRules.h"
#include "Misc/AutomationTest.h"
#include <limits>

#if WITH_DEV_AUTOMATION_TESTS
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FRPGPackParryGuardsTest, "OneBossFight.Parry.PackParryGuards", EAutomationTestFlags::EditorContext | EAutomationTestFlags::ProductFilter)
bool FRPGPackParryGuardsTest::RunTest(const FString&)
{
    using namespace RPGPackParry;
    const double NaN = std::numeric_limits<double>::quiet_NaN();
    const double Inf = std::numeric_limits<double>::infinity();

    TestTrue(TEXT("control: unchanged health after the wait is confirmed"), EvaluateCandidate(true, 100., 100., .11) == ECandidateDecision::Confirmed);

    TestTrue(TEXT("negative RequiredSeconds is rejected"), EvaluateCandidate(true, 100., 100., .11, -1.) == ECandidateDecision::Rejected);
    TestTrue(TEXT("NaN RequiredSeconds is rejected"), EvaluateCandidate(true, 100., 100., .11, NaN) == ECandidateDecision::Rejected);
    // A health GAIN (102 from 100) would be confirmed with a -1 tolerance (102 < 101 is false) without the guard.
    TestTrue(TEXT("negative LossTolerance is rejected"), EvaluateCandidate(true, 100., 102., .11, .1, -1.) == ECandidateDecision::Rejected);
    TestTrue(TEXT("NaN LossTolerance is rejected"), EvaluateCandidate(true, 100., 100., .11, .1, NaN) == ECandidateDecision::Rejected);
    TestTrue(TEXT("+Inf LossTolerance is rejected"), EvaluateCandidate(true, 100., 100., .11, .1, Inf) == ECandidateDecision::Rejected);

    // Exact tolerance boundary (0.5 is exact in binary): a loss of exactly the tolerance confirms, a larger loss rejects.
    TestTrue(TEXT("loss exactly equal to the tolerance confirms"), EvaluateCandidate(true, 100., 99.5, .11, .1, .5) == ECandidateDecision::Confirmed);
    TestTrue(TEXT("loss beyond the tolerance rejects"), EvaluateCandidate(true, 100., 99.25, .11, .1, .5) == ECandidateDecision::Rejected);
    return true;
}
#endif
