// Copyright One Boss Fight. All Rights Reserved.
#include "Misc/AutomationTest.h"

#if WITH_DEV_AUTOMATION_TESTS

#include "Player/RPGBossTrackRules.h"

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FBossLosDeadlineAcrossLeashDocumentation,
	"OneBossFight.Framework.LosMemory.AbsoluteDeadlineAcrossLeash",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::ProductFilter)

bool FBossLosDeadlineAcrossLeashDocumentation::RunTest(const FString&)
{
	RPGBossTrack::FLosMemory Memory;
	const FVector LastVisible(100., 200., 0.);
	TestEqual(TEXT("visibility loss starts search"),
		RPGBossTrack::LosStep(Memory, false, 10., 3., LastVisible), RPGBossTrack::ELosEvent::Lost);
	TestEqual(TEXT("lost timestamp is the original world time"), Memory.LostAt, 10.);

	// TickLos is skipped while the framework boss is leashed. The rule stores absolute world time,
	// so this models a 10-second leash interval with no LOS calls, not paused search time.
	TestEqual(TEXT("first hidden observation after leash immediately times out"),
		RPGBossTrack::LosStep(Memory, false, 20., 3., FVector::ZeroVector), RPGBossTrack::ELosEvent::TimedOut);
	TestTrue(TEXT("deadline remains reported once after the leash"), Memory.bTimedOut);
	TestEqual(TEXT("repeat hidden observation does not emit timeout twice"),
		RPGBossTrack::LosStep(Memory, false, 20.1, 3., FVector::ZeroVector), RPGBossTrack::ELosEvent::None);
	TestEqual(TEXT("visible target still reports regain after timeout"),
		RPGBossTrack::LosStep(Memory, true, 20.2, 3., FVector(300., 400., 0.)), RPGBossTrack::ELosEvent::Regained);
	TestEqual(TEXT("regain refreshes last known location"), Memory.LastKnown, FVector(300., 400., 0.));
	return true;
}

#endif
