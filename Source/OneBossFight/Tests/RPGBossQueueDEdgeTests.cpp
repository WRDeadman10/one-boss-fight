// Copyright One Boss Fight. All Rights Reserved.
#include "Misc/AutomationTest.h"

#if WITH_DEV_AUTOMATION_TESTS

#include "Player/RPGBossArenaEdgeRules.h"
#include "Player/RPGBossLeashRules.h"
#include "Player/RPGBossStuckRecoveryRules.h"
#include "Player/RPGBossStuckRules.h"
#include "Player/RPGBossTrackRules.h"
#include <cmath>
#include <limits>

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FBossQueueDEdgeBoundaries,
	"OneBossFight.Framework.QueueDEdgeBoundaries",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::ProductFilter)

bool FBossQueueDEdgeBoundaries::RunTest(const FString&)
{
	using namespace RPGBossStuck;
	FStuck ZeroDelta;
	Update(ZeroDelta, 1., 0., 0.);
	TestFalse(TEXT("zero delta time does not complete detector window"), IsStuck(ZeroDelta, .5, .3));
	Update(ZeroDelta, 1., 0., .3);
	TestTrue(TEXT("zero-delta sample can recover when elapsed window is later supplied"), IsStuck(ZeroDelta, .5, .3));
	FStuck JustEarly; JustEarly.AccumExpected=1.; JustEarly.Window=std::nextafter(.3, 0.);
	TestFalse(TEXT("stuck detector excludes the representable time immediately below threshold"), IsStuck(JustEarly, .5, .3));
	FStuck Exact; Exact.AccumExpected=1.; Exact.Window=.3;
	TestTrue(TEXT("stuck detector includes exact observation threshold"), IsStuck(Exact, .5, .3));
	FStuck JustLate; JustLate.AccumExpected=1.; JustLate.Window=std::nextafter(.3, std::numeric_limits<double>::infinity());
	TestTrue(TEXT("stuck detector includes the representable time immediately above threshold"), IsStuck(JustLate, .5, .3));

	using namespace RPGBossTrack;
	FTurnLatch AtLatch; AtLatch.Dir=1; AtLatch.LastDir=1;
	const float At150=StepYawLatched(0.f,-150.f,30.f,1.f,false,AtLatch);
	TestEqual(TEXT("exact 150-degree back-axis threshold keeps prior turn"), At150, 30.f);
	TestEqual(TEXT("exact latch boundary does not count a reversal"), AtLatch.Flips, 0);
	FTurnLatch BelowLatch; BelowLatch.Dir=1; BelowLatch.LastDir=1;
	const float Below150=std::nextafterf(-150.f, 0.f);
	StepYawLatched(0.f,Below150,30.f,1.f,false,BelowLatch);
	TestEqual(TEXT("just inside 150-degree boundary releases latch"), BelowLatch.Dir, -1);
	TestEqual(TEXT("released latch counts one direction reversal"), BelowLatch.Flips, 1);
	FTurnLatch AboveLatch; AboveLatch.Dir=1; AboveLatch.LastDir=1;
	const float Above150=std::nextafterf(-150.f,-std::numeric_limits<float>::infinity());
	StepYawLatched(0.f,Above150,30.f,1.f,false,AboveLatch);
	TestEqual(TEXT("just beyond 150-degree boundary keeps prior turn"), AboveLatch.Dir, 1);

	using namespace RPGBossStuckRecovery;
	TestTrue(TEXT("recovery budget allows the last attempt below cap"), CanRecover(true,false,7,8));
	TestFalse(TEXT("recovery budget refuses at cap"), CanRecover(true,false,8,8));
	TestFalse(TEXT("recovery budget refuses configured cap above eight"), CanRecover(true,false,0,9));

	const FVector Center=FVector::ZeroVector;
	TestFalse(TEXT("arena radius equality remains inside"), RPGBossLeashRules::IsOutsideArena(FVector(250.,0.,0.),Center,250.));
	TestFalse(TEXT("next representable radius value below equality remains inside"), RPGBossLeashRules::IsOutsideArena(FVector(std::nextafter(250.,0.),0.,0.),Center,250.));
	TestTrue(TEXT("next representable distance above radius is outside"), RPGBossLeashRules::IsOutsideArena(FVector(std::nextafter(250.,std::numeric_limits<double>::infinity()),0.,0.),Center,250.));
	const double NaN = std::numeric_limits<double>::quiet_NaN();
	const double Infinity = std::numeric_limits<double>::infinity();
	TestTrue(TEXT("NaN position fails closed as outside"), RPGBossLeashRules::IsOutsideArena(FVector(NaN,0.,0.),Center,250.));
	TestTrue(TEXT("infinite position fails closed as outside"), RPGBossLeashRules::IsOutsideArena(FVector(Infinity,0.,0.),Center,250.));
	TestTrue(TEXT("NaN center fails closed as outside"), RPGBossLeashRules::IsOutsideArena(FVector::ZeroVector,FVector(0.,NaN,0.),250.));
	TestTrue(TEXT("infinite center fails closed as outside"), RPGBossLeashRules::IsOutsideArena(FVector::ZeroVector,FVector(0.,0.,Infinity),250.));
	TestTrue(TEXT("NaN radius fails closed as outside"), RPGBossLeashRules::IsOutsideArena(FVector::ZeroVector,Center,NaN));
	TestTrue(TEXT("infinite radius fails closed as outside"), RPGBossLeashRules::IsOutsideArena(FVector::ZeroVector,Center,Infinity));
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FBossLeashLargeFiniteCoordinate,
	"OneBossFight.Framework.Leash.LargeFiniteCoordinate",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::ProductFilter)
bool FBossLeashLargeFiniteCoordinate::RunTest(const FString&)
{
	const FVector Center=FVector::ZeroVector;
	TestTrue(TEXT("large finite horizontal displacement is outside the arena"),
		RPGBossLeashRules::IsOutsideArena(FVector(1.e9,0.,0.),Center,250.));
	return true;
}

#endif
