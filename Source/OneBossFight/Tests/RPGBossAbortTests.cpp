// Copyright One Boss Fight. All Rights Reserved.
#include "Player/RPGBossTrackRules.h"
#include "Misc/AutomationTest.h"

#if WITH_DEV_AUTOMATION_TESTS
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FBossAbortIdempotent,"OneBossFight.Framework.Abort.GrabIdempotent",EAutomationTestFlags::EditorContext|EAutomationTestFlags::ProductFilter)
bool FBossAbortIdempotent::RunTest(const FString&)
{
    // BOSS-EXE-006: aborting twice is aborting once. The hold of a grab reports its interrupt ONCE; a second interrupt, or a release after it, reports nothing.
    using namespace RPGBossTrack;
    FGrabState S; GrabStep(S,true,.5,1.,false);
    TestTrue(TEXT("the first interrupt frees the victim"),GrabStep(S,false,.6,0.,true)==EGrabEvent::Interrupted&&!S.bHeld);
    TestTrue(TEXT("the second interrupt does nothing"),GrabStep(S,false,.6,0.,true)==EGrabEvent::None&&!S.bHeld);
    TestTrue(TEXT("the release time passing after an interrupt does nothing either"),GrabStep(S,false,2.,0.,false)==EGrabEvent::None&&!S.bHeld);
    GrabStep(S,true,.5,1.,false); GrabStep(S,false,1.,0.,false);
    TestTrue(TEXT("an interrupt after a normal release does nothing"),GrabStep(S,false,1.1,0.,true)==EGrabEvent::None&&!S.bHeld);
    return true;
}
#endif
