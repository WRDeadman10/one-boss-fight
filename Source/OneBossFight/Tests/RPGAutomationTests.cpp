// Copyright One Boss Fight. All Rights Reserved.

#include "Misc/AutomationTest.h"

#if WITH_DEV_AUTOMATION_TESTS

#include "Arena/RPGGreyboxArena.h"
#include "Benchmark/RPGFrameStats.h"
#include "Characters/RPGPlayerCharacter.h"
#include "Engine/Engine.h"
#include "Engine/World.h"
#include "GameFramework/CharacterMovementComponent.h"
#include "Camera/CameraComponent.h"
#include "GameFramework/SpringArmComponent.h"

namespace RPGTests
{
	/** Minimal game world for headless tests; destroyed with the scope. */
	struct FScopedTestWorld
	{
		UWorld* World = nullptr;

		FScopedTestWorld()
		{
			World = UWorld::CreateWorld(EWorldType::Game, /*bInformEngineOfWorld=*/false);
			FWorldContext& Context = GEngine->CreateNewWorldContext(EWorldType::Game);
			Context.SetCurrentWorld(World);
			World->InitializeActorsForPlay(FURL());
		}

		~FScopedTestWorld()
		{
			if (World)
			{
				GEngine->DestroyWorldContext(World);
				World->DestroyWorld(/*bInformEngineOfWorld=*/false);
			}
		}
	};
}

// ---------------------------------------------------------------------------------------------
// Frame statistics
// ---------------------------------------------------------------------------------------------

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FRPGFrameStatsPercentilesTest, "OneBossFight.Benchmark.FrameStats.Percentiles",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::ClientContext | EAutomationTestFlags::ProductFilter)

bool FRPGFrameStatsPercentilesTest::RunTest(const FString& Parameters)
{
	// 90 fast frames (5 ms) and 10 slow frames (20 ms).
	TArray<double> Frames;
	for (int32 Index = 0; Index < 90; ++Index) { Frames.Add(5.0); }
	for (int32 Index = 0; Index < 10; ++Index) { Frames.Add(20.0); }

	const FRPGFrameStats Stats = FRPGFrameStats::Compute(Frames);

	TestEqual(TEXT("frame count"), Stats.FrameCount, 100);
	TestEqual(TEXT("average ms"), Stats.AverageMs, 6.5);
	TestEqual(TEXT("median ms"), Stats.MedianMs, 5.0);
	TestEqual(TEXT("p95 ms"), Stats.P95Ms, 20.0);
	TestEqual(TEXT("p99 ms"), Stats.P99Ms, 20.0);
	TestEqual(TEXT("min ms"), Stats.MinMs, 5.0);
	TestEqual(TEXT("max ms"), Stats.MaxMs, 20.0);
	TestEqual(TEXT("frames over 120 FPS budget"), Stats.FramesOverBudget, 10);
	TestEqual(TEXT("average FPS is frames / seconds"), Stats.AverageFPS, 100.0 / 0.65, 0.001);

	// Average passes 120 FPS but spikes break the p99 gate: the strict gate must fail.
	TestTrue(TEXT("average alone would pass"), Stats.AverageFPS >= 120.0);
	TestFalse(TEXT("p99 gate fails, so target is not met"), Stats.MeetsTarget(120.0));
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FRPGFrameStatsGateTest, "OneBossFight.Benchmark.FrameStats.Gate",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::ClientContext | EAutomationTestFlags::ProductFilter)

bool FRPGFrameStatsGateTest::RunTest(const FString& Parameters)
{
	// Steady 7 ms frames (~142 FPS) pass both gates.
	TArray<double> Steady;
	Steady.Init(7.0, 500);
	TestTrue(TEXT("steady 7 ms frames meet 120 FPS"), FRPGFrameStats::Compute(Steady).MeetsTarget(120.0));

	// Steady 9 ms frames (~111 FPS) fail.
	TArray<double> Slow;
	Slow.Init(9.0, 500);
	TestFalse(TEXT("steady 9 ms frames miss 120 FPS"), FRPGFrameStats::Compute(Slow).MeetsTarget(120.0));

	// Empty input is safe and never passes.
	const FRPGFrameStats Empty = FRPGFrameStats::Compute(TArray<double>());
	TestEqual(TEXT("empty frame count"), Empty.FrameCount, 0);
	TestFalse(TEXT("empty never meets target"), Empty.MeetsTarget(120.0));

	// Single sample: every percentile equals it.
	TArray<double> One;
	One.Add(4.0);
	const FRPGFrameStats Single = FRPGFrameStats::Compute(One);
	TestEqual(TEXT("single p99"), Single.P99Ms, 4.0);
	TestEqual(TEXT("single median"), Single.MedianMs, 4.0);
	return true;
}

// ---------------------------------------------------------------------------------------------
// Arena collision
// ---------------------------------------------------------------------------------------------

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FRPGArenaCollisionTest, "OneBossFight.Arena.Collision",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::ClientContext | EAutomationTestFlags::ProductFilter)

bool FRPGArenaCollisionTest::RunTest(const FString& Parameters)
{
	RPGTests::FScopedTestWorld Scope;
	UWorld* World = Scope.World;
	if (!TestNotNull(TEXT("test world"), World))
	{
		return false;
	}

	ARPGGreyboxArena* Arena = World->SpawnActor<ARPGGreyboxArena>(FVector::ZeroVector, FRotator::ZeroRotator);
	if (!TestNotNull(TEXT("arena spawned"), Arena))
	{
		return false;
	}

	FHitResult Hit;

	// Floor: a downward trace at the center hits at Z = 0 (floor top).
	const bool bFloorHit = World->LineTraceSingleByChannel(Hit, FVector(0.f, 0.f, 500.f), FVector(0.f, 0.f, -500.f), ECC_Visibility);
	TestTrue(TEXT("floor is hit by a downward trace"), bFloorHit);
	if (bFloorHit)
	{
		TestEqual(TEXT("floor top surface at Z=0"), Hit.ImpactPoint.Z, 0.0, 1.0);
	}

	// Pillar 0: a horizontal trace toward the pillar hits its near face (a distance of PillarRadius from the base).
	const FVector PillarBase = Arena->GetPillarBaseLocation(0);
	const FVector TraceStart = PillarBase + FVector(-400.f, 0.f, 200.f);
	const FVector TraceEnd = PillarBase + FVector(400.f, 0.f, 200.f);
	const bool bPillarHit = World->LineTraceSingleByChannel(Hit, TraceStart, TraceEnd, ECC_Visibility);
	TestTrue(TEXT("pillar is hit by a horizontal trace"), bPillarHit);
	if (bPillarHit)
	{
		TestEqual(TEXT("pillar near face"), Hit.ImpactPoint.X, static_cast<double>(PillarBase.X - Arena->PillarRadius), 5.0);
	}

	// Boundary wall: a trace from inside to outside at angle 0 must be stopped at the wall's inner face.
	// Pillar 0 sits at the same angle, so offset the trace to the gap between segments' height, away from the pillar.
	const double Angle = 2.0 * PI * 0.5 / Arena->PillarCount; // halfway between pillar 0 and 1
	const FVector Direction(FMath::Cos(Angle), FMath::Sin(Angle), 0.f);
	const FVector WallStart = Direction * (Arena->ArenaRadius - 600.f) + FVector(0.f, 0.f, 100.f);
	const FVector WallEnd = Direction * (Arena->ArenaRadius + 600.f) + FVector(0.f, 0.f, 100.f);
	const bool bWallHit = World->LineTraceSingleByChannel(Hit, WallStart, WallEnd, ECC_Visibility);
	TestTrue(TEXT("wall blocks the way out"), bWallHit);
	if (bWallHit)
	{
		TestEqual(TEXT("wall inner face at arena radius"), Hit.ImpactPoint.Size2D(), static_cast<double>(Arena->ArenaRadius), 10.0);
	}

	// Outside the wall's height, the path is open (jumping alone cannot clear it).
	const bool bAboveWall = World->LineTraceSingleByChannel(
		Hit, Direction * (Arena->ArenaRadius - 600.f) + FVector(0.f, 0.f, Arena->WallHeight + 100.f),
		Direction * (Arena->ArenaRadius + 600.f) + FVector(0.f, 0.f, Arena->WallHeight + 100.f), ECC_Visibility);
	TestFalse(TEXT("above the wall height is open"), bAboveWall);
	return true;
}

// ---------------------------------------------------------------------------------------------
// Player character
// ---------------------------------------------------------------------------------------------

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FRPGPlayerCharacterTest, "OneBossFight.Characters.Player.Defaults",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::ClientContext | EAutomationTestFlags::ProductFilter)

bool FRPGPlayerCharacterTest::RunTest(const FString& Parameters)
{
	RPGTests::FScopedTestWorld Scope;
	UWorld* World = Scope.World;
	if (!TestNotNull(TEXT("test world"), World))
	{
		return false;
	}

	FActorSpawnParameters SpawnParams;
	SpawnParams.SpawnCollisionHandlingOverride = ESpawnActorCollisionHandlingMethod::AlwaysSpawn;
	ARPGPlayerCharacter* Player = World->SpawnActor<ARPGPlayerCharacter>(FVector(0.f, 0.f, 200.f), FRotator::ZeroRotator, SpawnParams);
	if (!TestNotNull(TEXT("player spawned"), Player))
	{
		return false;
	}

	TestNotNull(TEXT("camera boom"), Player->GetCameraBoom());
	TestNotNull(TEXT("follow camera"), Player->GetFollowCamera());
	TestTrue(TEXT("camera boom follows control rotation"), Player->GetCameraBoom()->bUsePawnControlRotation);
	TestFalse(TEXT("camera does not rotate with the pawn directly"), Player->GetFollowCamera()->bUsePawnControlRotation);
	TestFalse(TEXT("body does not use controller yaw"), Player->bUseControllerRotationYaw);
	TestTrue(TEXT("body orients to movement"), Player->GetCharacterMovement()->bOrientRotationToMovement);

	const float WalkSpeed = Player->GetCharacterMovement()->MaxWalkSpeed;
	TestFalse(TEXT("not sprinting initially"), Player->IsSprinting());

	Player->StartSprint();
	TestTrue(TEXT("sprinting after start"), Player->IsSprinting());
	TestTrue(TEXT("sprint is faster than walk"), Player->GetCharacterMovement()->MaxWalkSpeed > WalkSpeed);

	Player->StopSprint();
	TestFalse(TEXT("not sprinting after stop"), Player->IsSprinting());
	TestEqual(TEXT("walk speed restored"), Player->GetCharacterMovement()->MaxWalkSpeed, WalkSpeed);
	return true;
}

#endif // WITH_DEV_AUTOMATION_TESTS
