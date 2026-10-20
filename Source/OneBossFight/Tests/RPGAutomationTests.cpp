// Copyright One Boss Fight. All Rights Reserved.

#include "Misc/AutomationTest.h"
#include "Misc/PackageName.h"
#include <limits>

#if WITH_DEV_AUTOMATION_TESTS

#include "Arena/RPGArenaDressing.h"
#include "Arena/RPGEmberField.h"
#include "Arena/RPGFireSource.h"
#include "Arena/RPGGreyboxArena.h"
#include "Benchmark/RPGFrameStats.h"
#include "Player/RPGDodgeTiming.h"
#include "Player/RPGBossStagger.h"
#include "Player/RPGBossPhases.h"
#include "UI/RPGBossHud.h"
#include "Blueprint/UserWidget.h"
#include "Animation/AnimMontage.h"
#include "InputAction.h"
#include "AssetRegistry/AssetRegistryModule.h"
#include "AssetRegistry/IAssetRegistry.h"
#include "Components/InstancedStaticMeshComponent.h"
#include "Components/PointLightComponent.h"
#include "Materials/MaterialInterface.h"
#include "Components/SkeletalMeshComponent.h"
#include "Engine/Blueprint.h"
#include "Engine/BlueprintGeneratedClass.h"
#include "Engine/Engine.h"
#include "Engine/Level.h"
#include "Engine/SkeletalMesh.h"
#include "Engine/StaticMesh.h"
#include "Engine/World.h"
#if WITH_EDITOR
#include "StaticMeshCompiler.h"
#endif
#include "GameFramework/Character.h"
#include "GameFramework/GameModeBase.h"
#include "Modules/ModuleManager.h"
#include "UObject/Package.h"

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
// Arena art pass and content wiring (need the project's content, so editor context only)
// ---------------------------------------------------------------------------------------------

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FRPGArenaArtPassTest, "OneBossFight.Arena.ArtPass",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::ProductFilter)

bool FRPGArenaArtPassTest::RunTest(const FString& Parameters)
{
	const FString MeshRoot = TEXT("/Game/OneBossFight/Environment/Meshes/");
	auto LoadMesh = [&MeshRoot](const TCHAR* Name)
	{
		return LoadObject<UStaticMesh>(nullptr, *(MeshRoot + Name + TEXT(".") + Name));
	};
	UStaticMesh* Pillar = LoadMesh(TEXT("SM_Pillar_Intact"));
	UStaticMesh* Wall = LoadMesh(TEXT("SM_Wall_Curved_Intact"));
	UStaticMesh* Arch = LoadMesh(TEXT("SM_Entrance_Arch"));
	if (!TestNotNull(TEXT("pillar mesh"), Pillar) || !TestNotNull(TEXT("wall mesh"), Wall) || !TestNotNull(TEXT("arch mesh"), Arch))
	{
		return false;
	}
	UStaticMesh* Props[] = {LoadMesh(TEXT("SM_Pillar_Cracked")), LoadMesh(TEXT("SM_Pillar_Broken")), LoadMesh(TEXT("SM_Wall_Curved_Damaged")), LoadMesh(TEXT("SM_Arena_Brazier")),
		LoadMesh(TEXT("SM_Arena_Rubble_Cluster"))};
#if WITH_EDITOR
	// Static meshes compile asynchronously in the editor; an instanced component whose mesh is still compiling creates no collision bodies, so the traces below
	// would pass through the pillars and braziers (slower derived data cache, slower compile).
	FStaticMeshCompilingManager::Get().FinishAllCompilation();
#endif

	RPGTests::FScopedTestWorld Scope;
	UWorld* World = Scope.World;
	ARPGGreyboxArena* Arena = World ? World->SpawnActor<ARPGGreyboxArena>(FVector::ZeroVector, FRotator::ZeroRotator) : nullptr;
	if (!TestNotNull(TEXT("arena"), Arena))
	{
		return false;
	}
	Arena->PillarIntact = Pillar;
	Arena->PillarCracked = Props[0];
	Arena->PillarBroken = Props[1];
	Arena->WallIntact = Wall;
	Arena->WallDamaged = Props[2];
	Arena->EntranceArch = Arch;
	Arena->Brazier = Props[3];
	Arena->Rubble = Props[4];
	Arena->RerunConstructionScripts();

	FHitResult Hit;

	// The floor is unchanged.
	TestTrue(TEXT("floor hit"), World->LineTraceSingleByChannel(Hit, FVector(0.f, 0.f, 500.f), FVector(0.f, 0.f, -500.f), ECC_Visibility));
	TestEqual(TEXT("floor top at Z=0"), Hit.ImpactPoint.Z, 0.0, 1.0);

	// Pillar 0 (intact) blocks at its own radius from the ring position.
	const FVector PillarBase = Arena->GetPillarBaseLocation(0);
	const bool bPillar = World->LineTraceSingleByChannel(Hit, PillarBase + FVector(-500.f, 0.f, 300.f), PillarBase + FVector(500.f, 0.f, 300.f), ECC_Visibility);
	TestTrue(TEXT("art pillar blocks"), bPillar);
	if (bPillar)
	{
		const double NearFace = PillarBase.X - Hit.ImpactPoint.X;
		TestTrue(*FString::Printf(TEXT("pillar near face %.0f cm from its base is within 100-200 cm"), NearFace), NearFace > 100.0 && NearFace < 200.0);
	}

	// The wall stops a trace between two pillars (above the brazier height), close to the arena radius.
	const double Angle = 2.0 * PI * 0.5 / Arena->PillarCount;
	const FVector Direction(FMath::Cos(Angle), FMath::Sin(Angle), 0.f);
	const bool bWall = World->LineTraceSingleByChannel(Hit, Direction * (Arena->ArenaRadius - 600.f) + FVector(0.f, 0.f, 200.f),
		Direction * (Arena->ArenaRadius + 600.f) + FVector(0.f, 0.f, 200.f), ECC_Visibility);
	TestTrue(TEXT("art wall blocks"), bWall);
	if (bWall)
	{
		const double Distance = Hit.ImpactPoint.Size2D();
		TestTrue(*FString::Printf(TEXT("wall face at %.0f cm is within 40 cm of the arena radius"), Distance), FMath::Abs(Distance - Arena->ArenaRadius) < 40.0);
	}

	// The wall is closed all the way round for a fighter: 96 sphere sweeps (30 cm radius, so hairline seams between
	// segments do not count) at three heights. Holes in the top of damaged segments are fine, holes at body height are not.
	int32 Gaps = 0;
	for (const float Height : {40.f, 100.f, 150.f})
	{
		for (int32 Index = 0; Index < 96; ++Index)
		{
			const double Around = 2.0 * PI * Index / 96.0;
			const FVector Out(FMath::Cos(Around), FMath::Sin(Around), 0.f);
			const FVector Start = Out * (Arena->ArenaRadius - 200.f) + FVector(0.f, 0.f, Height);
			const FVector End = Out * (Arena->ArenaRadius + 400.f) + FVector(0.f, 0.f, Height);
			if (!World->SweepSingleByChannel(Hit, Start, End, FQuat::Identity, ECC_Visibility, FCollisionShape::MakeSphere(30.f)))
			{
				++Gaps;
				AddInfo(FString::Printf(TEXT("wall gap at %.1f degrees, height %.0f"), 360.0 * Index / 96.0, Height));
			}
		}
	}
	TestEqual(TEXT("no body-sized gaps in the wall ring"), Gaps, 0);

	// Entrance arch: the doorway is open (the trace reaches the wall behind it) and a column of the arch blocks.
	const FVector ArchCenter = FVector(FMath::Cos(FMath::DegreesToRadians(Arena->ArchAngleDegrees)), FMath::Sin(FMath::DegreesToRadians(Arena->ArchAngleDegrees)), 0.f) * (Arena->ArenaRadius * Arena->ArchRadiusFraction);
	const bool bDoor = World->LineTraceSingleByChannel(Hit, ArchCenter + FVector(400.f, 0.f, 200.f), ArchCenter + FVector(-400.f, 0.f, 200.f), ECC_Visibility);
	AddInfo(FString::Printf(TEXT("arch centre %s; doorway trace hit=%d at %s"), *ArchCenter.ToString(), bDoor, *Hit.ImpactPoint.ToString()));
	TestTrue(TEXT("the doorway of the arch is open at head height"), !bDoor || Hit.ImpactPoint.X < ArchCenter.X - 110.0);
	const bool bColumn = World->LineTraceSingleByChannel(Hit, ArchCenter + FVector(400.f, 460.f, 200.f), ArchCenter + FVector(-400.f, 460.f, 200.f), ECC_Visibility);
	TestTrue(TEXT("an arch column blocks"), bColumn);
	return true;
}


// ---------------------------------------------------------------------------------------------
// Arena dressing: the instanced decoration actor builds one component per set, and a fire source carries a light and flickers it
// ---------------------------------------------------------------------------------------------

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FRPGArenaDressingTest, "OneBossFight.Arena.Dressing",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::ProductFilter)

bool FRPGArenaDressingTest::RunTest(const FString& Parameters)
{
	RPGTests::FScopedTestWorld Scope;
	UWorld* World = Scope.World;
	if (!TestNotNull(TEXT("test world"), World))
	{
		return false;
	}
	UStaticMesh* Cube = LoadObject<UStaticMesh>(nullptr, TEXT("/Engine/BasicShapes/Cube.Cube"));
	if (!TestNotNull(TEXT("engine cube"), Cube))
	{
		return false;
	}

	ARPGArenaDressing* Dressing = World->SpawnActor<ARPGArenaDressing>(FVector::ZeroVector, FRotator::ZeroRotator);
	if (!TestNotNull(TEXT("dressing spawned"), Dressing))
	{
		return false;
	}
	FRPGDressingSet Solid;
	Solid.Mesh = Cube;
	Solid.bCollision = true;
	Solid.Instances = {FTransform(FVector(500.f, 0.f, 50.f)), FTransform(FVector(0.f, 500.f, 50.f)), FTransform(FVector(-500.f, 0.f, 50.f))};
	FRPGDressingSet Loose;
	Loose.Mesh = Cube;
	Loose.bCollision = false;
	Loose.Instances = {FTransform(FVector(0.f, -500.f, 50.f))};
	FRPGDressingSet Hanging;
	Hanging.Mesh = Cube;
	Hanging.SwayDegrees = 6.f;
	Hanging.SwayPivot = FVector(0.f, 0.f, 50.f);
	Hanging.Instances = {FTransform(FVector(0.f, 900.f, 300.f))};
	Dressing->Sets = {Solid, Loose, Hanging};
	Dressing->Rebuild();
	TestEqual(TEXT("instance count over all sets"), Dressing->GetInstanceCount(), 5);

	TArray<UInstancedStaticMeshComponent*> Components;
	Dressing->GetComponents(Components);
	TestEqual(TEXT("one instanced component per set"), Components.Num(), 3);
	int32 Solids = 0;
	for (const UInstancedStaticMeshComponent* Component : Components)
	{
		Solids += Component->GetCollisionEnabled() == ECollisionEnabled::NoCollision ? 0 : 1;
	}
	TestEqual(TEXT("only the solid set collides"), Solids, 1);
	{
		// The hanging set swings: after some ticks its instance has left the resting transform.
		for (int32 Step = 0; Step < 30; ++Step)
		{
			Dressing->Tick(0.1f);
		}
		bool bMoved = false;
		for (const UInstancedStaticMeshComponent* Component : Components)
		{
			if (Component->Mobility == EComponentMobility::Movable && Component->GetInstanceCount() == 1)
			{
				FTransform Now;
				Component->GetInstanceTransform(0, Now, /*bWorldSpace=*/false);
				bMoved = !Now.GetRotation().Equals(FQuat::Identity, 0.001f);
			}
		}
		TestTrue(TEXT("a swaying set moves in the wind"), bMoved);
	}
	Dressing->Rebuild();
	Components.Reset();
	Dressing->GetComponents(Components);
	TestEqual(TEXT("rebuilding does not pile up components"), Components.Num(), 3);

	ARPGFireSource* Fire = World->SpawnActor<ARPGFireSource>(FVector(0.f, 0.f, 100.f), FRotator::ZeroRotator);
	if (!TestNotNull(TEXT("fire source spawned"), Fire))
	{
		return false;
	}
	UPointLightComponent* Light = Fire->FindComponentByClass<UPointLightComponent>();
	if (TestNotNull(TEXT("fire has a light"), Light))
	{
		float Lowest = Light->Intensity;
		float Highest = Light->Intensity;
		for (int32 Step = 0; Step < 40; ++Step)
		{
			Fire->Tick(0.25f);
			Lowest = FMath::Min(Lowest, Light->Intensity);
			Highest = FMath::Max(Highest, Light->Intensity);
		}
		TestTrue(TEXT("the light flickers over 10 s"), Highest - Lowest > Fire->BaseIntensity * 0.05f);
		TestTrue(TEXT("the light stays warm and lit"), Lowest > 0.f);
	}

	// Embers: one instanced mesh, every ember alive after many frames, and they rise
	ARPGEmberField* Embers = World->SpawnActor<ARPGEmberField>(FVector::ZeroVector, FRotator::ZeroRotator);
	if (TestNotNull(TEXT("ember field spawned"), Embers))
	{
		Embers->Mesh = Cube;
		Embers->Count = 24;
		Embers->FireSources = {FVector(500.f, 0.f, 100.f)};
		Embers->Rebuild();
		UInstancedStaticMeshComponent* EmberInstances = Embers->FindComponentByClass<UInstancedStaticMeshComponent>();
		if (TestNotNull(TEXT("ember instances"), EmberInstances))
		{
			TestEqual(TEXT("one instance per ember"), EmberInstances->GetInstanceCount(), 24);
			for (int32 Step = 0; Step < 120; ++Step)
			{
				Embers->Tick(0.1f);
			}
			TestEqual(TEXT("embers respawn instead of vanishing"), EmberInstances->GetInstanceCount(), 24);
			FTransform Sample;
			EmberInstances->GetInstanceTransform(0, Sample, /*bWorldSpace=*/false);
			TestTrue(TEXT("embers stay within a sane box"), Sample.GetLocation().Size() < 12000.0);
		}
	}

	// The tracked arena materials the dressing script needs
	TestNotNull(TEXT("roman floor material instance"), LoadObject<UMaterialInterface>(nullptr, TEXT("/Game/OneBossFight/Environment/Materials/MI_Arena_RomanFloor.MI_Arena_RomanFloor")));
	return true;
}

// ---------------------------------------------------------------------------------------------
// Pack content wiring: the pack's own mannequin player and great-sword boss in the arena (editor context: needs the project's content)
// ---------------------------------------------------------------------------------------------

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FRPGPackWiringTest, "OneBossFight.Content.PackWiring",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::ProductFilter)

bool FRPGPackWiringTest::RunTest(const FString& Parameters)
{
	const FString Blueprints = TEXT("/Game/AdvancedARPGCombat/MeleeCombatSystem/Blueprints/");

	// The pack game mode spawns the pack's own player (an earlier retarget pointed it at a Greystone Blueprint).
	const UBlueprint* GameModeBlueprint = LoadObject<UBlueprint>(nullptr, *(Blueprints + TEXT("BP_AdvancedGameMode.BP_AdvancedGameMode")));
	if (TestNotNull(TEXT("BP_AdvancedGameMode"), GameModeBlueprint) && TestNotNull(TEXT("game mode class"), GameModeBlueprint->GeneratedClass.Get()))
	{
		const AGameModeBase* GameMode = Cast<AGameModeBase>(GameModeBlueprint->GeneratedClass->GetDefaultObject());
		const UClass* PawnClass = GameMode ? GameMode->DefaultPawnClass.Get() : nullptr;
		TestEqual(TEXT("default pawn is the pack player"), PawnClass ? PawnClass->GetName() : FString(), FString(TEXT("BP_CombatPlayerCharacter_C")));
	}

	// The pack player wears the pack mannequin.
	const UBlueprint* PlayerBlueprint = LoadObject<UBlueprint>(nullptr, *(Blueprints + TEXT("BP_CombatPlayerCharacter.BP_CombatPlayerCharacter")));
	if (TestNotNull(TEXT("BP_CombatPlayerCharacter"), PlayerBlueprint) && PlayerBlueprint->GeneratedClass)
	{
		const ACharacter* Player = Cast<ACharacter>(PlayerBlueprint->GeneratedClass->GetDefaultObject());
		const USkeletalMesh* Mesh = Player && Player->GetMesh() ? Player->GetMesh()->GetSkeletalMeshAsset() : nullptr;
		TestTrue(TEXT("pack player uses the combat mannequin mesh"), Mesh && Mesh->GetName().Contains(TEXT("CombatMannequin")));
	}

	// The dodge timing component (Player/RPGDodgeTiming) names these pack assets and the montage map variable of the dodge ability by path: fail loudly if a pack re-import moves them.
	const URPGDodgeTiming* DodgeDefaults = GetDefault<URPGDodgeTiming>();
	TestNotNull(TEXT("dodge action IA_Dodge"), DodgeDefaults->DodgeAction.LoadSynchronous());
	TestNotNull(TEXT("quick dodge montage"), DodgeDefaults->QuickMontage.LoadSynchronous());
	TestNotNull(TEXT("full dodge montage"), DodgeDefaults->FullMontage.LoadSynchronous());
	// Phase two (Player/RPGBossPhases) names its transition clip, the immunity effect and the pack magic enemy's fireball ability by path.
	const URPGBossPhases* PhaseDefaults = GetDefault<URPGBossPhases>();
	TestNotNull(TEXT("phase two transition montage"), PhaseDefaults->TransitionMontage.LoadSynchronous());
	TestNotNull(TEXT("phase two immunity effect"), PhaseDefaults->ImmunityEffect.LoadSynchronous());
	TestNotNull(TEXT("phase two fireball ability"), PhaseDefaults->FireballAbility.LoadSynchronous());
	// Master Design Freeze values (30.1, 36): phase two at 60 %, no legacy fireball, double tap window 0.30 s, critical only from the riposte.
	TestEqual(TEXT("phase two threshold is 0.60"), PhaseDefaults->PhaseTwoHealthFraction, 0.6f);
	TestFalse(TEXT("legacy fireball is off"), PhaseDefaults->bFireballEnabled);
	TestEqual(TEXT("double tap window is 0.30 s"), DodgeDefaults->DoubleTapWindow, 0.30f);
	TestFalse(TEXT("no blanket critical while the boss is down"), GetDefault<URPGBossStagger>()->bCriticalOnEveryHit);

	// Sounds the subsystem and the dressing script assign by path: concrete footsteps, the placeholder boss music, the fire crackle and the wind bed.
	for (const TCHAR* Sound : {TEXT("/Game/Essential_Foosteps_SK/CUE/Concrete/Footstep_Concrete_Boots_Walk_1_Cue"), TEXT("/Game/Essential_Foosteps_SK/CUE/Concrete/Footstep_Concrete_Boots_Jog_8_Cue"),
		TEXT("/Game/Essential_Foosteps_SK/CUE/Concrete/Footstep_Concrete_Boots_Run_8_Cue"), TEXT("/Game/Essential_Foosteps_SK/CUE/Concrete/Footstep_Concrete_Boots_Land_4_Cue"),
		TEXT("/Game/StarterContent/Audio/Starter_Music_Cue"), TEXT("/Game/StarterContent/Audio/Fire01_Cue"), TEXT("/Game/StarterContent/Audio/Starter_Wind05")})
	{
		TestTrue(*FString::Printf(TEXT("sound %s exists"), Sound), FPackageName::DoesPackageExist(Sound));
	}

	// The boss stance break (Player/RPGBossStagger) names its clips and the pack's immunity effect by path.
	const URPGBossStagger* StaggerDefaults = GetDefault<URPGBossStagger>();
	TestNotNull(TEXT("stance break fall montage"), StaggerDefaults->FallMontage.LoadSynchronous());
	TestNotNull(TEXT("stance break get-up montage"), StaggerDefaults->GetUpMontage.LoadSynchronous());
	TestNotNull(TEXT("hit stun immunity effect"), StaggerDefaults->ImmunityEffect.LoadSynchronous());
	// The boss HUD (UI/RPGBossHud) loads the pack's display font by path and hides the pack's own boss bar through the boss Blueprint's "Boss HUD" widget variable.
	TestTrue(TEXT("Cinzel display font exists"), FPackageName::DoesPackageExist(TEXT("/Game/AdvancedARPGCombat/MeleeCombatSystem/UI/Fonts/Cinzel/Cinzel")));
	if (const UBlueprint* BossBlueprint = LoadObject<UBlueprint>(nullptr, *(Blueprints + TEXT("AI/Enemies/ExampleGreatswordBoss/BP_ExampleGreatSwordBoss.BP_ExampleGreatSwordBoss"))))
	{
		bool bHasHudVariable = false;
		for (TFieldIterator<FObjectProperty> It(BossBlueprint->GeneratedClass); It; ++It)
		{
			bHasHudVariable |= It->PropertyClass && It->PropertyClass->IsChildOf(UUserWidget::StaticClass()) && It->GetName().Contains(TEXT("HUD"));
		}
		TestTrue(TEXT("the pack boss has its HUD widget variable (the boss HUD collapses it)"), bHasHudVariable);
	}
	else
	{
		AddError(TEXT("BP_ExampleGreatSwordBoss is missing"));
	}
	const URPGBossHud* HudDefaults = GetDefault<URPGBossHud>();
	TestTrue(TEXT("the pack's boss bar is hidden by default"), HudDefaults->bHidePackBar);
	TestFalse(TEXT("the boss HUD has a name"), HudDefaults->BossName.IsEmpty());
	if (const UBlueprint* DodgeAbility = LoadObject<UBlueprint>(nullptr, *(Blueprints + TEXT("Abilities/Player/GA_Player_Dodge.GA_Player_Dodge"))))
	{
		TestNotNull(TEXT("GA_Player_Dodge has the montage map variable"), DodgeAbility->GeneratedClass ? DodgeAbility->GeneratedClass->FindPropertyByName(DodgeDefaults->MontageMapName) : nullptr);
	}
	else
	{
		AddError(TEXT("GA_Player_Dodge is missing"));
	}

	// No pack asset may depend on the retargeted Greystone or the Sevarog copies: the pack's abilities, combat styles and animation Blueprints once pointed at them,
	// which broke the mannequin (animations of another skeleton) and filled the log with Blueprint errors.
	IAssetRegistry& Registry = FModuleManager::LoadModuleChecked<FAssetRegistryModule>(TEXT("AssetRegistry")).Get();
	TArray<FAssetData> PackAssets;
	Registry.GetAssetsByPath(TEXT("/Game/AdvancedARPGCombat"), PackAssets, /*bRecursive=*/true);
	TestTrue(TEXT("pack assets are in the registry"), PackAssets.Num() > 1000);
	int32 Leaks = 0;
	for (const FAssetData& Asset : PackAssets)
	{
		TArray<FName> Dependencies;
		Registry.GetDependencies(Asset.PackageName, Dependencies, UE::AssetRegistry::EDependencyCategory::Package);
		for (const FName& Dependency : Dependencies)
		{
			const FString Name = Dependency.ToString();
			if (Name.StartsWith(TEXT("/Game/OneBossFight/GreystonePack")) || Name.StartsWith(TEXT("/Game/OneBossFight/SevarogPack")))
			{
				AddError(FString::Printf(TEXT("%s depends on %s"), *Asset.PackageName.ToString(), *Name));
				++Leaks;
			}
		}
	}
	TestEqual(TEXT("pack assets that depend on the Greystone or Sevarog copies"), Leaks, 0);

	// The arena level: one pack great-sword boss with the great-sword boss data (the boss Blueprint defaults to the sword mob's data: sword mob montages, 100 HP),
	// and none of the retired Sevarog pawns.
	UPackage* LevelPackage = LoadPackage(nullptr, TEXT("/Game/OneBossFight/Levels/L_SevarogArena"), LOAD_None);
	UWorld* Level = LevelPackage ? UWorld::FindWorldInPackage(LevelPackage) : nullptr;
	if (TestNotNull(TEXT("L_SevarogArena"), Level))
	{
		int32 Bosses = 0;
		for (const AActor* Actor : Level->PersistentLevel->Actors)
		{
			if (!Actor)
			{
				continue;
			}
			const FString ClassName = Actor->GetClass()->GetName();
			TestFalse(*FString::Printf(TEXT("%s is not a retired Sevarog pawn"), *Actor->GetName()), ClassName == TEXT("BP_SevarogBossPack_C") || ClassName == TEXT("BP_SevarogBoss_C"));
			if (ClassName == TEXT("BP_ExampleGreatSwordBoss_C"))
			{
				++Bosses;
				FString Info;
				if (const FProperty* Property = Actor->GetClass()->FindPropertyByName(TEXT("EnemyInfoRef")))
				{
					Property->ExportText_InContainer(0, Info, Actor, Actor, nullptr, PPF_None);
				}
				TestTrue(TEXT("boss uses the great-sword boss data"), Info.Contains(TEXT("ExampleGreatSwordBoss")));
			}
		}
		TestEqual(TEXT("pack great-sword bosses in the arena"), Bosses, 1);
	}
	return true;
}

#endif // WITH_DEV_AUTOMATION_TESTS
