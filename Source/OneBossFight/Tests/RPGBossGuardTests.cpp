// Copyright One Boss Fight. All Rights Reserved.
#include "Player/RPGBossGuardRules.h"
#include "Misc/AutomationTest.h"
#include <limits>

#if WITH_DEV_AUTOMATION_TESTS
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FBossGuardRules,"OneBossFight.Framework.Guard.Rules",EAutomationTestFlags::EditorContext|EAutomationTestFlags::ProductFilter)
bool FBossGuardRules::RunTest(const FString&)
{
    // BOSS-COM-004 / BOSS-HIT-008: guard classification and the card outcome of the combo gate.
    using namespace RPGBossGuard;
    TestTrue(TEXT("no guard tags: None"),Classify(false,false)==EGuardState::None);
    TestTrue(TEXT("blocking: Guarded"),Classify(true,false)==EGuardState::Guarded);
    TestTrue(TEXT("parrying: Parried"),Classify(false,true)==EGuardState::Parried);
    TestTrue(TEXT("a parry inside a guard is a Parried"),Classify(true,true)==EGuardState::Parried);
    TestTrue(TEXT("names"),FString(Name(EGuardState::None))==TEXT("None")&&FString(Name(EGuardState::Guarded))==TEXT("Guarded")&&FString(Name(EGuardState::Parried))==TEXT("Parried"));
    TestTrue(TEXT("no accepted hit: Whiff"),CardOutcome(0,0,0)==ECardOutcome::Whiff);
    TestTrue(TEXT("a plain hit: Hit"),CardOutcome(1,0,0)==ECardOutcome::Hit);
    TestTrue(TEXT("a guarded hit: Guarded (it is also an accepted hit)"),CardOutcome(1,1,0)==ECardOutcome::Guarded);
    TestTrue(TEXT("a parried hit: Parried"),CardOutcome(1,0,1)==ECardOutcome::Parried);
    TestTrue(TEXT("parried beats guarded beats hit"),CardOutcome(3,1,1)==ECardOutcome::Parried&&CardOutcome(3,1,0)==ECardOutcome::Guarded);
    // BOSS-COM-004 test hook phase: the measured root-A contact at +0.433 s
    // moves into the 0.5 s pulse when the approved phase is +0.080 s.
    TestTrue(TEXT("phase shifts measured root-A contact into the parry pulse"),IsProofParryPulse(.433,.080));
    TestTrue(TEXT("zero phase preserves the original pulse window"),IsProofParryPulse(.050,0.));
    TestFalse(TEXT("phase-shifted pulse remains bounded to 100 ms"),IsProofParryPulse(.530,.080));   // .53+.08=.61, so the pulse position is .11 (clear of the boundary).
    TestFalse(TEXT("negative elapsed input cannot pulse"),IsProofParryPulse(-.01,.080));
    TestFalse(TEXT("nonfinite phase cannot pulse"),IsProofParryPulse(.433,std::numeric_limits<double>::infinity()));
    return true;
}
#endif
