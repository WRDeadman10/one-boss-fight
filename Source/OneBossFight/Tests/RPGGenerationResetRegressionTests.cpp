// Copyright One Boss Fight. All Rights Reserved.
#include "Misc/AutomationTest.h"

#if WITH_DEV_AUTOMATION_TESTS

#include "Boss/RPGFrameworkBossCharacter.h"
#include "Engine/Engine.h"
#include "Engine/World.h"
#include "Player/RPGBossEncounter.h"
#include "Player/RPGBossStagger.h"
#include "Player/RPGHitIntake.h"
#include "TimerManager.h"
#include "GameFramework/Character.h"

namespace
{
struct FGenerationRegressionWorld
{
	UWorld* World = nullptr;
	FGenerationRegressionWorld()
	{
		if (!GEngine) return;
		World = UWorld::CreateWorld(EWorldType::Game, false);
		if (World)
		{
			FWorldContext& Context = GEngine->CreateNewWorldContext(EWorldType::Game);
			Context.SetCurrentWorld(World);
			World->InitializeActorsForPlay(FURL());
		}
	}
	~FGenerationRegressionWorld()
	{
		if (World)
		{
			GEngine->DestroyWorldContext(World);
			World->DestroyWorld(false);
		}
	}
	FGenerationRegressionWorld(const FGenerationRegressionWorld&) = delete;
	FGenerationRegressionWorld& operator=(const FGenerationRegressionWorld&) = delete;
	void TickNextFrame()
	{
		World->Tick(LEVELTICK_All, 0.016f);
	}
	void FlushNextTick()
	{
		// SetTimerForNextTick callbacks added while a timer-manager tick is unwinding can become due on the following world tick.
		for (int32 Index = 0; Index < 3; ++Index) TickNextFrame();
	}
};
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FKI172PendingHitGenerationResetOrdering,
	"OneBossFight.Player.KI172.PendingHitGenerationResetOrdering",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::ProductFilter)

bool FKI172PendingHitGenerationResetOrdering::RunTest(const FString&)
{
	FGenerationRegressionWorld Scope;
	if (!TestNotNull(TEXT("engine-backed transient world is available"), Scope.World)) return false;
	ARPGFrameworkBossCharacter* Boss = Scope.World->SpawnActor<ARPGFrameworkBossCharacter>(FVector(0, 0, 300), FRotator::ZeroRotator);
	ACharacter* Player = Scope.World->SpawnActor<ACharacter>(FVector(300, 0, 300), FRotator::ZeroRotator);
	if (!TestNotNull(TEXT("native-health boss is available"), Boss) || !TestNotNull(TEXT("player actor is available"), Player)) return false;

	URPGBossEncounter* Encounter = NewObject<URPGBossEncounter>(Boss, TEXT("GenerationRegressionEncounter"));
	Boss->AddInstanceComponent(Encounter);
	Encounter->RegisterComponent();
	URPGHitIntake* Intake = NewObject<URPGHitIntake>(Player, TEXT("GenerationRegressionHitIntake"));
	Player->AddInstanceComponent(Intake);
	Intake->RegisterComponent();
	Scope.World->BeginPlay();

	int32 BroadcastCount = 0;
	Intake->OnBossHit.AddLambda([&BroadcastCount](const FRPGHitRecord&) { ++BroadcastCount; });
	Intake->InjectBossPendingHitForTest(Boss, TEXT("RegressionWeapon"), ERPGAttackKind::Light, 1);
	Scope.FlushNextTick();
	TestEqual(TEXT("same-generation pending hit is recorded"), Intake->GetBossHitCount(), 1);
	TestEqual(TEXT("same-generation pending hit is broadcast"), BroadcastCount, 1);

	const uint64 GenerationBeforeReset = Encounter->GetParticipantGeneration();
	Intake->InjectBossPendingHitForTest(Boss, TEXT("RegressionWeapon"), ERPGAttackKind::Light, 1);
	Encounter->ResetForTest();
	TestTrue(TEXT("encounter reset advances participant generation"), Encounter->GetParticipantGeneration() > GenerationBeforeReset);
	// The real SetTimerForNextTick route passed above. Invoke its private target directly here because a second timer tick cannot be advanced deterministically inside this automation callback.
	Intake->FinalizePending();
	TestEqual(TEXT("old-generation pending hit is discarded after reset"), Intake->GetBossHitCount(), 1);
	TestEqual(TEXT("old-generation pending hit has no observer broadcast"), BroadcastCount, 1);

	Intake->InjectBossPendingHitForTest(Boss, TEXT("RegressionWeapon"), ERPGAttackKind::Light, 1);
	Intake->FinalizePending();
	TestEqual(TEXT("fresh-generation hit still finalizes"), Intake->GetBossHitCount(), 2);
	TestEqual(TEXT("fresh-generation hit still broadcasts"), BroadcastCount, 2);
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FKI173RiposteGenerationResetOrdering,
	"OneBossFight.Player.KI173.RiposteGenerationResetOrdering",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::ProductFilter)

bool FKI173RiposteGenerationResetOrdering::RunTest(const FString&)
{
	FGenerationRegressionWorld Scope;
	if (!TestNotNull(TEXT("engine-backed transient world is available"), Scope.World)) return false;
	ACharacter* Boss = Scope.World->SpawnActor<ACharacter>(FVector(0, 0, 300), FRotator::ZeroRotator);
	ACharacter* PlayerA = Scope.World->SpawnActor<ACharacter>(FVector(150, 0, 300), FRotator(0, 180, 0));
	ACharacter* PlayerB = Scope.World->SpawnActor<ACharacter>(FVector(150, 0, 300), FRotator(0, 180, 0));
	if (!TestNotNull(TEXT("boss character is available"), Boss) || !TestNotNull(TEXT("old-request player is available"), PlayerA) || !TestNotNull(TEXT("new-request player is available"), PlayerB)) return false;

	URPGBossEncounter* Encounter = NewObject<URPGBossEncounter>(Boss, TEXT("GenerationRegressionEncounter"));
	Boss->AddInstanceComponent(Encounter);
	Encounter->RegisterComponent();
	URPGBossStagger* Stagger = NewObject<URPGBossStagger>(Boss, TEXT("GenerationRegressionStagger"));
	Boss->AddInstanceComponent(Stagger);
	Stagger->RegisterComponent();
	Scope.World->BeginPlay();

	PlayerB->SetActorLocation(FVector(50, 0, 300)); // reset returns the boss to its captured home transform
	Stagger->Phase = URPGBossStagger::EPhase::Down;
	Stagger->bClipMode = true;
	Stagger->ClipStage = URPGBossStagger::EClipStage::Down;
	TestTrue(TEXT("old-generation riposte request is accepted"), Stagger->TryRiposte(PlayerA));
	const uint64 GenerationBeforeReset = Encounter->GetParticipantGeneration();
	Encounter->ResetForTest();
	TestTrue(TEXT("encounter reset advances generation before the next-tick callbacks"), Encounter->GetParticipantGeneration() > GenerationBeforeReset);

	// ResetEncounter aborts the old down state. Model a new stance break before the queued timer dispatches.
	Stagger->Phase = URPGBossStagger::EPhase::Down;
	Stagger->bClipMode = true;
	Stagger->ClipStage = URPGBossStagger::EClipStage::Down;
	Stagger->bRiposteUsed = false;
	TestTrue(TEXT("new-generation riposte request is accepted"), Stagger->TryRiposte(PlayerB));
	Scope.FlushNextTick();
	TestEqual(TEXT("stale callback is inert and only current request dispatches"), Stagger->RiposteStartDispatchCountForTest, 1);
	return true;
}

#endif
