// Copyright One Boss Fight. All Rights Reserved.
// Lead fix (C-864): the probe class is URPGBossTrackerTickOrderProbe (RPGBossTrackerTickOrderFixtures.h); this file used a stale name.

#include "Tests/RPGBossTrackerTickOrderFixtures.h"
#include "Player/RPGBossTrackerTickPrerequisite.h"
#include "Engine/Engine.h"
#include "Engine/World.h"
#include "GameFramework/Actor.h"
#if WITH_DEV_AUTOMATION_TESTS
#include "Misc/AutomationTest.h"
#endif

URPGBossTrackerTickOrderProbe::URPGBossTrackerTickOrderProbe()
{
	PrimaryComponentTick.bCanEverTick = true;
}

void URPGBossTrackerTickOrderProbe::TickComponent(float DeltaTime, ELevelTick TickType, FActorComponentTickFunction* ThisTickFunction)
{
	Super::TickComponent(DeltaTime, TickType, ThisTickFunction);
	++FrameState;
}

URPGBossTrackerTickConsumerProbe::URPGBossTrackerTickConsumerProbe()
{
	PrimaryComponentTick.bCanEverTick = true;
}

void URPGBossTrackerTickConsumerProbe::BeginPlay()
{
	Super::BeginPlay();
	if (AActor* Owner = GetOwner())
	{
		RPGBossTrackerTickPrerequisite::Add(*this, BoundTracker, Owner->FindComponentByClass<URPGBossTrackerTickOrderProbe>());
	}
}

void URPGBossTrackerTickConsumerProbe::TickComponent(float DeltaTime, ELevelTick TickType, FActorComponentTickFunction* ThisTickFunction)
{
	Super::TickComponent(DeltaTime, TickType, ThisTickFunction);
	if (AActor* Owner = GetOwner())
	{
		if (const URPGBossTrackerTickOrderProbe* Tracker = Owner->FindComponentByClass<URPGBossTrackerTickOrderProbe>())
		{
			ObservedFrameState = Tracker->FrameState;
		}
	}
}

#if WITH_DEV_AUTOMATION_TESTS

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FRPGBossTrackerTickPrerequisiteSameFrameTest,
	"OneBossFight.Boss.TickOrder.TrackerPrerequisiteSameFrame",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FRPGBossTrackerTickPrerequisiteSameFrameTest::RunTest(const FString& Parameters)
{
	if (!GEngine)
	{
		AddError(TEXT("GEngine is required to create the transient test world"));
		return false;
	}
	UWorld* World = UWorld::CreateWorld(EWorldType::Game, false);
	if (!World)
	{
		AddError(TEXT("Could not create transient game world"));
		return false;
	}
	FWorldContext& Context = GEngine->CreateNewWorldContext(EWorldType::Game);
	Context.SetCurrentWorld(World);
	World->InitializeActorsForPlay(FURL());

	AActor* Owner = World->SpawnActor<AActor>();
	if (!Owner)
	{
		GEngine->DestroyWorldContext(World);
		World->DestroyWorld(false);
		AddError(TEXT("Could not spawn tick-order fixture actor"));
		return false;
	}
	// Deliberately register the consumer first, reproducing the data-route order.
	URPGBossTrackerTickConsumerProbe* Consumer = NewObject<URPGBossTrackerTickConsumerProbe>(Owner, TEXT("ConsumerFirst"));
	URPGBossTrackerTickOrderProbe* Tracker = NewObject<URPGBossTrackerTickOrderProbe>(Owner, TEXT("TrackerSecond"));
	Consumer->RegisterComponent();
	Tracker->RegisterComponent();
	Owner->DispatchBeginPlay();
	World->SetBegunPlay(true);
	World->Tick(LEVELTICK_All, 1.f / 60.f);

	TestEqual(TEXT("consumer sees tracker state advanced in this frame"), Consumer->ObservedFrameState, 1);
	TestEqual(TEXT("tracker advanced exactly once"), Tracker->FrameState, 1);

	Owner->Destroy();
	GEngine->DestroyWorldContext(World);
	World->DestroyWorld(false);
	return true;
}

#endif // WITH_DEV_AUTOMATION_TESTS
