// Copyright One Boss Fight. All Rights Reserved.

#include "Misc/AutomationTest.h"
#include "Misc/PackageName.h"
#include "Misc/FileHelper.h"
#include "Misc/ConfigCacheIni.h"
#include "HAL/FileManager.h"
#include "Internationalization/Regex.h"
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
#include "Player/RPGBossRules.h"
#include "Player/RPGBossMath.h"
#include "Player/RPGHitIntake.h"
#include "Player/RPGWeaponAttackTable.h"
#include "Player/RPGSwingRules.h"
#include "Player/RPGBleedRules.h"
#include "Player/RPGBossBleed.h"
#include "Player/RPGBossPosture.h"
#include "Player/RPGBossShockwave.h"
#include "Pack/RPGPackTrace.h"
#include "Player/RPGDamageResolver.h"
#include "Player/RPGLegend.h"
#include "Audio/RPGBossMusic.h"
#include "Player/RPGAttackTracker.h"
#include "Player/RPGBossHealPunish.h"
#include "Player/RPGBossLowSweep.h"
#include "UI/RPGBossHud.h"
#include "Player/RPGCameraRig.h"
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
// Damage resolver decision order (Freeze 12.1)
// ---------------------------------------------------------------------------------------------

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FRPGDamageDecideTest, "OneBossFight.Combat.DamageResolver.Decide",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::ClientContext | EAutomationTestFlags::ProductFilter)

bool FRPGDamageDecideTest::RunTest(const FString& Parameters)
{
	// All 32 combinations against the written order: dead target, stale attacker or generation, duplicate swing, invulnerable target, else accepted.
	for (int32 Bits = 0; Bits < 32; ++Bits)
	{
		const bool bTargetAlive = (Bits & 1) != 0;
		const bool bAttackerAlive = (Bits & 2) != 0;
		const bool bCurrent = (Bits & 4) != 0;
		const bool bDuplicate = (Bits & 8) != 0;
		const bool bInvulnerable = (Bits & 16) != 0;
		ERPGDamageOutcome Expected = ERPGDamageOutcome::Accepted;
		if (!bTargetAlive) { Expected = ERPGDamageOutcome::RejectedDead; }
		else if (!bAttackerAlive || !bCurrent) { Expected = ERPGDamageOutcome::RejectedStale; }
		else if (bDuplicate) { Expected = ERPGDamageOutcome::RejectedDuplicate; }
		else if (bInvulnerable) { Expected = ERPGDamageOutcome::RejectedInvulnerable; }
		TestEqual(*FString::Printf(TEXT("decision for flags %d"), Bits), static_cast<int32>(RPGDamageRules::Decide(bTargetAlive, bAttackerAlive, bCurrent, bDuplicate, bInvulnerable)), static_cast<int32>(Expected));
	}
	// A rejected contact for invulnerability is never an accepted one, and the names are stable (the drivers read them).
	TestEqual(TEXT("name of RejectedInvulnerable"), FString(RPGDamageRules::Name(ERPGDamageOutcome::RejectedInvulnerable)), FString(TEXT("RejectedInvulnerable")));
	TestEqual(TEXT("name of Accepted"), FString(RPGDamageRules::Name(ERPGDamageOutcome::Accepted)), FString(TEXT("Accepted")));
	TestEqual(TEXT("A4 damage 20 (0.4 of the Freeze 50)"), GetDefault<URPGBossLowSweep>()->Damage, 20.f);
	TestEqual(TEXT("A5 damage 12 (0.4 of the Freeze 30)"), GetDefault<URPGBossHealPunish>()->Damage, 12.f);
	return true;
}

// ---------------------------------------------------------------------------------------------
// Boss state priority rules (Freeze 21): stance break versus phase transition
// ---------------------------------------------------------------------------------------------

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FRPGTransitionRulesTest, "OneBossFight.Boss.TransitionRules",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::ClientContext | EAutomationTestFlags::ProductFilter)

bool FRPGTransitionRulesTest::RunTest(const FString& Parameters)
{
	using namespace RPGBossRules;
	// All 32 combinations of the five flags a break looks at, with and without the cooldown being ignored, against the written order.
	for (int32 Bits = 0; Bits < 32; ++Bits)
	{
		FFlags F;
		F.bDead = (Bits & 1) != 0;
		F.bDormant = (Bits & 2) != 0;
		F.bTransition = (Bits & 4) != 0;
		F.bStaggered = (Bits & 8) != 0;
		F.bCooldown = (Bits & 16) != 0;
		for (const bool bIgnoreCooldown : {false, true})
		{
			EBreakResult Expected = EBreakResult::Started;
			if (F.bDead) { Expected = EBreakResult::Dead; }
			else if (F.bDormant) { Expected = EBreakResult::Dormant; }
			else if (F.bTransition) { Expected = EBreakResult::Transition; }
			else if (F.bStaggered) { Expected = EBreakResult::AlreadyStaggered; }
			else if (F.bCooldown && !bIgnoreCooldown) { Expected = EBreakResult::Cooldown; }
			TestEqual(*FString::Printf(TEXT("break flags %d ignore cooldown %d"), Bits, bIgnoreCooldown ? 1 : 0), static_cast<int32>(ResolveBreak(F, bIgnoreCooldown)), static_cast<int32>(Expected));
		}
	}

	// The phase two check at the Freeze threshold (0.60 of 500 health = 300).
	FFlags Idle;
	TestEqual(TEXT("300 of 500 starts (at or below)"), static_cast<int32>(ResolveTransition(Idle, 300.0, 500.0, 0.6f)), static_cast<int32>(ETransitionResult::Start));
	TestEqual(TEXT("300.5 of 500 is above"), static_cast<int32>(ResolveTransition(Idle, 300.5, 500.0, 0.6f)), static_cast<int32>(ETransitionResult::AboveThreshold));
	TestEqual(TEXT("health 0 is dead"), static_cast<int32>(ResolveTransition(Idle, 0.0, 500.0, 0.6f)), static_cast<int32>(ETransitionResult::Dead));
	TestEqual(TEXT("no maximum is not ready"), static_cast<int32>(ResolveTransition(Idle, 100.0, 0.0, 0.6f)), static_cast<int32>(ETransitionResult::NotReady));
	FFlags Down;
	Down.bStaggered = true;
	TestEqual(TEXT("below the threshold during a break is queued"), static_cast<int32>(ResolveTransition(Down, 250.0, 500.0, 0.6f)), static_cast<int32>(ETransitionResult::QueuedBehindStagger));
	TestEqual(TEXT("above the threshold during a break is above"), static_cast<int32>(ResolveTransition(Down, 400.0, 500.0, 0.6f)), static_cast<int32>(ETransitionResult::AboveThreshold));
	FFlags Done;
	Done.bPhaseTwo = true;
	TestEqual(TEXT("phase two already begun never starts again"), static_cast<int32>(ResolveTransition(Done, 100.0, 500.0, 0.6f)), static_cast<int32>(ETransitionResult::AlreadyDone));
	FFlags Asleep;
	Asleep.bDormant = true;
	TestEqual(TEXT("a dormant boss does not start"), static_cast<int32>(ResolveTransition(Asleep, 100.0, 500.0, 0.6f)), static_cast<int32>(ETransitionResult::Dormant));
	FFlags DeadFlag;
	DeadFlag.bDead = true;
	TestEqual(TEXT("the dead flag wins over a crossing"), static_cast<int32>(ResolveTransition(DeadFlag, 100.0, 500.0, 0.6f)), static_cast<int32>(ETransitionResult::Dead));

	// Defaults that other rules rely on.
	TestEqual(TEXT("stagger seconds 2.5"), GetDefault<URPGBossStagger>()->StaggerSeconds, 2.5f);
	TestEqual(TEXT("stagger cooldown 0 (decision G0-5)"), GetDefault<URPGBossStagger>()->CooldownSeconds, 0.f);
	TestEqual(TEXT("transition seconds 1.8"), GetDefault<URPGBossPhases>()->TransitionSeconds, 1.8f);
	return true;
}

// ---------------------------------------------------------------------------------------------
// Boss rules with numbers (G2-16): posture regeneration, riposte geometry, low sweep geometry, Freeze defaults
// ---------------------------------------------------------------------------------------------

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FRPGPostureRegenTest, "OneBossFight.Boss.PostureRegen",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::ClientContext | EAutomationTestFlags::ProductFilter)

bool FRPGPostureRegenTest::RunTest(const FString& Parameters)
{
	using namespace RPGBossMath;
	// Freeze 17.2: 100 points, regeneration starts 6 s after the last drain, 13 per second, never above the maximum.
	const URPGBossPosture* Defaults = GetDefault<URPGBossPosture>();
	TestEqual(TEXT("regeneration delay 6 s"), Defaults->RegenDelaySeconds, 6.f);
	TestEqual(TEXT("regeneration 13 per second"), Defaults->RegenPerSecond, 13.f);

	TestEqual(TEXT("5.99 s after the drain: nothing"), RegenStep(40.f, 100.f, 5.99, 0.0, 6.f, 13.f, 1.f), 40.f);
	TestEqual(TEXT("exactly 6.00 s after the drain: starts"), RegenStep(40.f, 100.f, 6.0, 0.0, 6.f, 13.f, 1.f), 53.f);
	TestEqual(TEXT("one second of regeneration adds 13"), RegenStep(40.f, 100.f, 20.0, 0.0, 6.f, 13.f, 1.f), 53.f);
	TestEqual(TEXT("0.05 s tick adds 0.65"), RegenStep(40.f, 100.f, 20.0, 0.0, 6.f, 13.f, 0.05f), 40.65f);
	TestEqual(TEXT("never above the maximum"), RegenStep(95.f, 100.f, 20.0, 0.0, 6.f, 13.f, 1.f), 100.f);
	TestEqual(TEXT("at the maximum nothing changes"), RegenStep(100.f, 100.f, 20.0, 0.0, 6.f, 13.f, 1.f), 100.f);
	TestEqual(TEXT("at zero (a stance break holds it) nothing regenerates"), RegenStep(0.f, 100.f, 20.0, 0.0, 6.f, 13.f, 1.f), 0.f);
	TestEqual(TEXT("at zero with nothing holding it (a dropped break) it comes back after the delay"), RegenStep(0.f, 100.f, 20.0, 0.0, 6.f, 13.f, 1.f, true), 13.f);
	TestEqual(TEXT("at zero with nothing holding it, still inside the delay: nothing"), RegenStep(0.f, 100.f, 5.99, 0.0, 6.f, 13.f, 1.f, true), 0.f);
	TestEqual(TEXT("never drained (-1) regenerates at once"), RegenStep(40.f, 100.f, 0.5, -1.0, 6.f, 13.f, 1.f), 53.f);

	// A drain to 40 at t = 0, simulated at 20 ticks per second: flat for 6 s, then 13 per second, full after 4.62 s more (60 / 13).
	float Posture = 40.f;
	float AtFive = -1.f, AtEight = -1.f, AtEleven = -1.f;
	for (int32 Step = 1; Step <= 300; ++Step)
	{
		const double Time = Step * 0.05;
		Posture = RegenStep(Posture, 100.f, Time, 0.0, 6.f, 13.f, 0.05f);
		if (Step == 100) { AtFive = Posture; }
		if (Step == 160) { AtEight = Posture; }
		if (Step == 220) { AtEleven = Posture; }
	}
	TestEqual(TEXT("40 at 5 s"), AtFive, 40.f);
	TestTrue(*FString::Printf(TEXT("about 66 at 8 s (got %.2f)"), AtEight), FMath::IsNearlyEqual(AtEight, 40.f + 13.f * 2.f, 1.f));
	TestEqual(TEXT("full at 11 s"), AtEleven, 100.f);
	TestEqual(TEXT("full at 15 s"), Posture, 100.f);

	// A second drain restarts the delay: drained again at t = 3 (to 30), the regeneration starts at 9 s, not 6 s.
	float Second = 30.f;
	float At8 = -1.f, At10 = -1.f;
	for (int32 Step = 61; Step <= 200; ++Step)
	{
		Second = RegenStep(Second, 100.f, Step * 0.05, 3.0, 6.f, 13.f, 0.05f);
		if (Step == 160) { At8 = Second; }
		if (Step == 200) { At10 = Second; }
	}
	TestEqual(TEXT("second drain at 3 s: still 30 at 8 s"), At8, 30.f);
	TestTrue(*FString::Printf(TEXT("second drain at 3 s: about 43 at 10 s (got %.2f)"), At10), FMath::IsNearlyEqual(At10, 30.f + 13.f, 1.f));
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FRPGRiposteGeometryTest, "OneBossFight.Boss.RiposteGeometry",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::ClientContext | EAutomationTestFlags::ProductFilter)

bool FRPGRiposteGeometryTest::RunTest(const FString& Parameters)
{
	using namespace RPGBossMath;
	// Freeze: 150 cm, 120 degree front cone, the player faces the boss within 120 degrees.
	const URPGBossStagger* Defaults = GetDefault<URPGBossStagger>();
	TestEqual(TEXT("riposte range 150"), Defaults->RiposteRange, 150.f);
	TestEqual(TEXT("riposte cone 120"), Defaults->RiposteConeDegrees, 120.f);
	TestEqual(TEXT("riposte facing 120"), Defaults->RiposteFacingDegrees, 120.f);
	TestEqual(TEXT("arm window 1.2 s"), Defaults->RiposteArmSeconds, 1.2f);
	TestEqual(TEXT("critical x2.5"), Defaults->CriticalMultiplier, 2.5f);

	const FVector Boss(0.f, 0.f, 0.f);
	const FVector BossForward(1.f, 0.f, 0.f);
	const FVector FaceBoss(-1.f, 0.f, 0.f);
	auto Verdict = [&](const FVector& Player, const FVector& PlayerForward)
	{
		return static_cast<int32>(RiposteGeometry(Boss, BossForward, Player, PlayerForward, 150.f, 120.f, 120.f));
	};
	const int32 Accept = static_cast<int32>(ERiposteVerdict::Accept);
	TestEqual(TEXT("100 cm in front, facing the boss"), Verdict(FVector(100.f, 0.f, 0.f), FaceBoss), Accept);
	TestEqual(TEXT("exactly 150 cm is in"), Verdict(FVector(150.f, 0.f, 0.f), FaceBoss), Accept);
	TestEqual(TEXT("150.5 cm is too far"), Verdict(FVector(150.5f, 0.f, 0.f), FaceBoss), static_cast<int32>(ERiposteVerdict::TooFar));
	TestEqual(TEXT("height is ignored (500 cm up)"), Verdict(FVector(100.f, 0.f, 500.f), FaceBoss), Accept);
	// Cone: 60 degrees is the half angle.
	const auto At = [](float Degrees, float Distance) { return FVector(FMath::Cos(FMath::DegreesToRadians(Degrees)), FMath::Sin(FMath::DegreesToRadians(Degrees)), 0.f) * Distance; };
	TestEqual(TEXT("59 degrees off the boss's front is inside the cone"), Verdict(At(59.f, 100.f), -At(59.f, 1.f)), Accept);
	TestEqual(TEXT("-59 degrees too"), Verdict(At(-59.f, 100.f), -At(-59.f, 1.f)), Accept);
	TestEqual(TEXT("61 degrees is outside"), Verdict(At(61.f, 100.f), -At(61.f, 1.f)), static_cast<int32>(ERiposteVerdict::NotInFront));
	TestEqual(TEXT("behind the boss"), Verdict(FVector(-100.f, 0.f, 0.f), FVector(1.f, 0.f, 0.f)), static_cast<int32>(ERiposteVerdict::NotInFront));
	// Facing: the player looks 59 degrees away from the boss is fine, 61 is not.
	const FVector Player(100.f, 0.f, 0.f);
	TestEqual(TEXT("player turned 59 degrees from the boss"), Verdict(Player, At(180.f + 59.f, 1.f)), Accept);
	TestEqual(TEXT("player turned 61 degrees from the boss"), Verdict(Player, At(180.f + 61.f, 1.f)), static_cast<int32>(ERiposteVerdict::NotFacing));
	TestEqual(TEXT("player facing away"), Verdict(Player, FVector(1.f, 0.f, 0.f)), static_cast<int32>(ERiposteVerdict::NotFacing));
	// Order of the checks: too far wins over the cone; the cone wins over the facing.
	TestEqual(TEXT("far and behind: too far"), Verdict(FVector(-400.f, 0.f, 0.f), FVector(1.f, 0.f, 0.f)), static_cast<int32>(ERiposteVerdict::TooFar));
	TestEqual(TEXT("behind and facing away: not in front"), Verdict(FVector(-100.f, 0.f, 0.f), FVector(-1.f, 0.f, 0.f)), static_cast<int32>(ERiposteVerdict::NotInFront));
	// The reason texts the drivers read.
	TestTrue(TEXT("accepted has no reason"), RiposteReason(ERiposteVerdict::Accept) == nullptr);
	TestEqual(TEXT("reason too far"), FString(RiposteReason(ERiposteVerdict::TooFar)), FString(TEXT("too far")));
	TestEqual(TEXT("reason not in front"), FString(RiposteReason(ERiposteVerdict::NotInFront)), FString(TEXT("not in front of the boss")));
	TestEqual(TEXT("reason not facing"), FString(RiposteReason(ERiposteVerdict::NotFacing)), FString(TEXT("player not facing the boss")));
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FRPGBossMoveNumbersTest, "OneBossFight.Boss.MoveNumbers",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::ClientContext | EAutomationTestFlags::ProductFilter)

bool FRPGBossMoveNumbersTest::RunTest(const FString& Parameters)
{
	using namespace RPGBossMath;
	// A4 low sweep: ring 60 to 380 cm, blade 40 cm high, swinging from 90 to -90 degrees.
	const URPGBossLowSweep* Sweep = GetDefault<URPGBossLowSweep>();
	TestEqual(TEXT("A4 reach 380"), Sweep->Reach, 380.f);
	TestEqual(TEXT("A4 inner radius 60"), Sweep->InnerRadius, 60.f);
	TestEqual(TEXT("A4 blade height 40"), Sweep->BladeHeight, 40.f);
	TestEqual(TEXT("A4 from 90"), Sweep->SweepFromDegrees, 90.f);
	TestEqual(TEXT("A4 to -90"), Sweep->SweepToDegrees, -90.f);
	const float R = 34.f; // the player capsule
	TestTrue(TEXT("250 cm straight ahead is touched"), SweepTouches(250.f, R, 380.f, 60.f, 0.f, 90.f, -90.f));
	TestTrue(TEXT("414 cm (capsule edge at 380) is touched"), SweepTouches(414.f, R, 380.f, 60.f, 0.f, 90.f, -90.f));
	TestFalse(TEXT("420 cm is out of reach"), SweepTouches(420.f, R, 380.f, 60.f, 0.f, 90.f, -90.f));
	TestFalse(TEXT("20 cm (inside the inner radius even with the capsule)"), SweepTouches(20.f, R, 380.f, 60.f, 0.f, 90.f, -90.f));
	TestTrue(TEXT("40 cm (capsule edge past 60) is touched"), SweepTouches(40.f, R, 380.f, 60.f, 0.f, 90.f, -90.f));
	TestFalse(TEXT("a player on the boss's position never counts"), SweepTouches(0.f, R, 380.f, 0.f, 0.f, 90.f, -90.f));
	// Angles: the arc is widened by asin(34 / 250) = 7.8 degrees at 250 cm.
	TestTrue(TEXT("95 degrees at 250 cm is inside the widened arc"), SweepTouches(250.f, R, 380.f, 60.f, 95.f, 90.f, -90.f));
	TestFalse(TEXT("100 degrees at 250 cm is outside"), SweepTouches(250.f, R, 380.f, 60.f, 100.f, 90.f, -90.f));
	TestFalse(TEXT("behind the boss (180) is never touched"), SweepTouches(250.f, R, 380.f, 60.f, 180.f, 90.f, -90.f));
	TestTrue(TEXT("a reversed arc (from -90 to 90) covers the same angles"), SweepTouches(250.f, R, 380.f, 60.f, 0.f, -90.f, 90.f));
	TestTrue(TEXT("a blade that moved only from 10 to 20 touches 15"), SweepTouches(250.f, R, 380.f, 60.f, 15.f, 10.f, 20.f));
	TestFalse(TEXT("a blade that moved only from 10 to 20 does not touch 40"), SweepTouches(250.f, R, 380.f, 60.f, 40.f, 10.f, 20.f));

	// A5 heal punish: range 400 to 1000, cooldown 4 s, damage 12, flight 1.2 s.
	const URPGBossHealPunish* Punish = GetDefault<URPGBossHealPunish>();
	TestEqual(TEXT("A5 min range 400"), Punish->MinRange, 400.f);
	TestEqual(TEXT("A5 max range 1000"), Punish->MaxRange, 1000.f);
	TestEqual(TEXT("A5 cooldown 4"), Punish->Cooldown, 4.f);
	TestEqual(TEXT("A5 flight time 1.2"), Punish->FlightTime, 1.2f);

	// A6 leap wave: one ring from 200 to 1100 cm at 1000 cm/s, 180 cm thick, 48 damage, jumpable from 50 cm.
	const URPGBossShockwave* Wave = GetDefault<URPGBossShockwave>();
	TestEqual(TEXT("A6 damage 48"), Wave->Damage, 48.f);
	TestEqual(TEXT("A6 start radius 200"), Wave->StartRadius, 200.f);
	TestEqual(TEXT("A6 max radius 1100"), Wave->MaxRadius, 1100.f);
	TestEqual(TEXT("A6 speed 1000"), Wave->Speed, 1000.f);
	TestEqual(TEXT("A6 thickness 180"), Wave->Thickness, 180.f);
	TestEqual(TEXT("A6 jump clearance 50"), Wave->JumpClearance, 50.f);
	TestTrue(TEXT("the wave reaches its maximum in 0.9 s (1100 - 200) / 1000"), FMath::IsNearlyEqual((Wave->MaxRadius - Wave->StartRadius) / Wave->Speed, 0.9f, 0.001f));
	return true;
}

// ---------------------------------------------------------------------------------------------
// Hit intake (Gate 3, M7): the kind of attack from the pack's attack data name and the stance
// ---------------------------------------------------------------------------------------------

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FRPGAttackClassifyTest, "OneBossFight.Hit.Classify",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::ClientContext | EAutomationTestFlags::ProductFilter)

bool FRPGAttackClassifyTest::RunTest(const FString& Parameters)
{
	auto Kind = [](const TCHAR* Name, bool bAirborne) { return static_cast<int32>(RPGClassifyAttack(FName(Name), bAirborne)); };
	TestEqual(TEXT("default data on the ground is a light attack"), Kind(TEXT("DefaultMeleeAttackData"), false), static_cast<int32>(ERPGAttackKind::Light));
	TestEqual(TEXT("default data in the air is a jump light"), Kind(TEXT("DefaultMeleeAttackData"), true), static_cast<int32>(ERPGAttackKind::JumpLight));
	TestEqual(TEXT("strong data on the ground is a strong attack"), Kind(TEXT("StrongMeleeAttackData"), false), static_cast<int32>(ERPGAttackKind::Strong));
	TestEqual(TEXT("strong data in the air is the jumping heavy"), Kind(TEXT("StrongMeleeAttackData"), true), static_cast<int32>(ERPGAttackKind::JumpHeavy));
	TestEqual(TEXT("charged data is a charged attack on the ground"), Kind(TEXT("ChargedMeleeAttackData"), false), static_cast<int32>(ERPGAttackKind::Charged));
	TestEqual(TEXT("charged data in the air stays charged"), Kind(TEXT("ChargedMeleeAttackData"), true), static_cast<int32>(ERPGAttackKind::Charged));
	TestEqual(TEXT("knockdown data"), Kind(TEXT("MeleeKnockdownAttackData"), false), static_cast<int32>(ERPGAttackKind::Knockdown));
	TestEqual(TEXT("no data is unknown"), Kind(TEXT("None"), false), static_cast<int32>(ERPGAttackKind::Unknown));
	TestEqual(TEXT("another asset is unknown"), Kind(TEXT("FireBallAttackData"), true), static_cast<int32>(ERPGAttackKind::Unknown));
	TestEqual(TEXT("names are stable (the drivers read them)"), FString(RPGAttackKindName(ERPGAttackKind::JumpHeavy)), FString(TEXT("JumpHeavy")));
	return true;
}

// ---------------------------------------------------------------------------------------------
// Weapon attack table (Gate 3, M8): the Freeze starting values and the lookup order
// ---------------------------------------------------------------------------------------------

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FRPGWeaponTableTest, "OneBossFight.Hit.WeaponTable",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::ClientContext | EAutomationTestFlags::ProductFilter)

bool FRPGWeaponTableTest::RunTest(const FString& Parameters)
{
	// The defaults of a fresh table (the class constructor), whatever the project asset holds: the Freeze starting values (5, 20.1, 20.2).
	const URPGWeaponAttackTable* Defaults = GetDefault<URPGWeaponAttackTable>();
	FRPGWeaponAttackRow Row;
	TestTrue(TEXT("strength light row exists"), Defaults->Find(TEXT("ClaymoreCombatStyle"), ERPGAttackKind::Light, Row));
	TestEqual(TEXT("strength light posture 18"), Row.PostureDamage, 18.f);
	TestTrue(TEXT("strength jump heavy row exists"), Defaults->Find(TEXT("ClaymoreCombatStyle"), ERPGAttackKind::JumpHeavy, Row));
	TestEqual(TEXT("strength jump heavy posture 38"), Row.PostureDamage, 38.f);
	TestEqual(TEXT("strength jump heavy stamina 35"), Row.StaminaCost, 35.f);
	TestEqual(TEXT("strength has no bleed"), Row.BleedBuildup, 0.f);
	TestTrue(TEXT("dex light row exists"), Defaults->Find(TEXT("DualSwordCombatStyle"), ERPGAttackKind::Light, Row));
	TestEqual(TEXT("dex light posture 6"), Row.PostureDamage, 6.f);
	TestEqual(TEXT("dex stamina 10"), Row.StaminaCost, 10.f);
	TestEqual(TEXT("dex bleed 20 per hit"), Row.BleedBuildup, 20.f);
	TestTrue(TEXT("dex jump heavy row exists"), Defaults->Find(TEXT("DualSwordCombatStyle"), ERPGAttackKind::JumpHeavy, Row));
	TestEqual(TEXT("dex jump heavy posture 14"), Row.PostureDamage, 14.f);
	TestTrue(TEXT("the starter sword has a row"), Defaults->Find(TEXT("SwordCombatStyle"), ERPGAttackKind::Light, Row));
	TestEqual(TEXT("the starter sword keeps the pack's stamina cost"), Row.StaminaCost, -1.f);
	// The hyperarmor windows (M13/M14): the Strength build's strong, jump heavy and charged swings carry one inside the montage, nothing else does.
	auto HasWindow = [&](const URPGWeaponAttackTable* Table, const TCHAR* Weapon, ERPGAttackKind Kind, float& OutStart, float& OutEnd)
	{
		FRPGWeaponAttackRow R;
		Table->Find(Weapon, Kind, R);
		OutStart = R.HyperArmorStart;
		OutEnd = R.HyperArmorEnd;
		return R.HasHyperArmor();
	};
	float WinStart = 0.f, WinEnd = 0.f;
	TestTrue(TEXT("the strength jump heavy has a hyperarmor window"), HasWindow(Defaults, TEXT("ClaymoreCombatStyle"), ERPGAttackKind::JumpHeavy, WinStart, WinEnd));
	TestTrue(TEXT("it opens before the strike (the first trace window opens at 0.432 s) and closes with it (0.618 s)"), WinStart < 0.432f && WinStart > 0.2f && FMath::IsNearlyEqual(WinEnd, 0.618f, 0.001f));
	TestTrue(TEXT("the strength strong has the same window"), HasWindow(Defaults, TEXT("ClaymoreCombatStyle"), ERPGAttackKind::Strong, WinStart, WinEnd) && FMath::IsNearlyEqual(WinEnd, 0.618f, 0.001f));
	TestTrue(TEXT("the strength charged has a window that ends inside the swing (the effect lasts 4 s, the montage 2.7 s)"), HasWindow(Defaults, TEXT("ClaymoreCombatStyle"), ERPGAttackKind::Charged, WinStart, WinEnd) && WinEnd <= 1.1f && WinEnd > WinStart);
	TestFalse(TEXT("the strength light has none"), HasWindow(Defaults, TEXT("ClaymoreCombatStyle"), ERPGAttackKind::Light, WinStart, WinEnd));
	TestFalse(TEXT("the strength jump light has none"), HasWindow(Defaults, TEXT("ClaymoreCombatStyle"), ERPGAttackKind::JumpLight, WinStart, WinEnd));
	TestFalse(TEXT("the starter sword's jump heavy has none"), HasWindow(Defaults, TEXT("SwordCombatStyle"), ERPGAttackKind::JumpHeavy, WinStart, WinEnd));
	TestFalse(TEXT("the dual swords' jump heavy has none"), HasWindow(Defaults, TEXT("DualSwordCombatStyle"), ERPGAttackKind::JumpHeavy, WinStart, WinEnd));
	// The asset of the project holds the same windows (an overwrite of the asset must not drop them silently: Scripts/Editor/set_weapon_windows.py writes them).
	if (const URPGWeaponAttackTable* Asset = LoadObject<URPGWeaponAttackTable>(nullptr, URPGWeaponAttackTable::AssetPath(), nullptr, LOAD_NoWarn))
	{
		float AssetStart = 0.f, AssetEnd = 0.f;
		TestTrue(TEXT("the asset's strength jump heavy has the window"), HasWindow(Asset, TEXT("ClaymoreCombatStyle"), ERPGAttackKind::JumpHeavy, AssetStart, AssetEnd) && AssetEnd > AssetStart && AssetEnd <= 5.f);
		TestTrue(TEXT("the asset's strength strong has the window"), HasWindow(Asset, TEXT("ClaymoreCombatStyle"), ERPGAttackKind::Strong, AssetStart, AssetEnd) && AssetEnd <= 5.f);
		TestTrue(TEXT("the asset's strength charged has the window"), HasWindow(Asset, TEXT("ClaymoreCombatStyle"), ERPGAttackKind::Charged, AssetStart, AssetEnd) && AssetEnd <= 5.f);
		TestFalse(TEXT("the asset's starter sword jump heavy has none"), HasWindow(Asset, TEXT("SwordCombatStyle"), ERPGAttackKind::JumpHeavy, AssetStart, AssetEnd));
	}
	else
	{
		AddWarning(TEXT("the weapon attack table asset is not in the project: its hyperarmor windows were not checked"));
	}
	// The Freeze arithmetic, from the table's rows and the posture component's own pool: three strength jump heavies (3 x 38 = 114) break it, six lights (6 x 18 = 108) do and five do not (90), a dex light needs 17 hits.
	const float PoolMax = GetDefault<URPGBossPosture>()->PostureMax;
	TestEqual(TEXT("the posture pool is 100 points (Freeze 17.2)"), PoolMax, 100.f);
	auto HitsToBreak = [&](const TCHAR* Weapon, ERPGAttackKind Kind)
	{
		FRPGWeaponAttackRow R;
		Defaults->Find(Weapon, Kind, R);
		return R.PostureDamage > 0.f ? FMath::CeilToInt(PoolMax / R.PostureDamage) : 0;
	};
	TestEqual(TEXT("three strength jump heavies break the pool"), HitsToBreak(TEXT("ClaymoreCombatStyle"), ERPGAttackKind::JumpHeavy), 3);
	TestEqual(TEXT("six strength lights break the pool"), HitsToBreak(TEXT("ClaymoreCombatStyle"), ERPGAttackKind::Light), 6);
	TestEqual(TEXT("a dex light needs 17 hits (6 x 17 = 102, 16 x 6 = 96)"), HitsToBreak(TEXT("DualSwordCombatStyle"), ERPGAttackKind::Light), 17);

	// The lookup order on a table of our own: the exact row, then the row of the kind for any weapon, then Fallback.
	URPGWeaponAttackTable* Table = NewObject<URPGWeaponAttackTable>(GetTransientPackage());
	Table->Rows.Reset();
	FRPGWeaponAttackRow Exact;
	Exact.Weapon = TEXT("A");
	Exact.Kind = ERPGAttackKind::Light;
	Exact.PostureDamage = 11.f;
	FRPGWeaponAttackRow Any;
	Any.Kind = ERPGAttackKind::Light;
	Any.PostureDamage = 7.f;
	Table->Rows.Add(Any);
	Table->Rows.Add(Exact);
	Table->Fallback.PostureDamage = 3.f;
	TestTrue(TEXT("exact row found"), Table->Find(TEXT("A"), ERPGAttackKind::Light, Row));
	TestEqual(TEXT("exact row wins over the any-weapon row"), Row.PostureDamage, 11.f);
	TestTrue(TEXT("another weapon finds the any-weapon row"), Table->Find(TEXT("B"), ERPGAttackKind::Light, Row));
	TestEqual(TEXT("any-weapon row value"), Row.PostureDamage, 7.f);
	TestFalse(TEXT("a kind without a row falls back"), Table->Find(TEXT("A"), ERPGAttackKind::Strong, Row));
	TestEqual(TEXT("fallback value"), Row.PostureDamage, 3.f);
	TestTrue(TEXT("the fallback row names what was asked"), Row.Weapon == FName(TEXT("A")) && Row.Kind == ERPGAttackKind::Strong);
	TestTrue(TEXT("no weapon name finds the any-weapon row, not the exact row of a weapon"), Table->Find(NAME_None, ERPGAttackKind::Light, Row));
	TestEqual(TEXT("and its value is the any-weapon value"), Row.PostureDamage, 7.f);
	return true;
}

// ---------------------------------------------------------------------------------------------
// Swing rules (Gate 3, M10 and M11): the hyperarmor window of a swing, the stamina on top of the pack's cost, the refresh of the timed effect
// ---------------------------------------------------------------------------------------------

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FRPGSwingRulesTest, "OneBossFight.Swing.Rules",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::ClientContext | EAutomationTestFlags::ProductFilter)

bool FRPGSwingRulesTest::RunTest(const FString& Parameters)
{
	using namespace RPGSwingRules;
	// The window of a swing: the row's, replaced by a test override, none when neither has one.
	FRPGWeaponAttackRow Row;
	float Start = 9.f, End = 9.f;
	ResolveWindow(Row, nullptr, Start, End);
	TestTrue(TEXT("a row without a window gives no window"), Start < 0.f && End < 0.f);
	Row.HyperArmorStart = 0.2f;
	Row.HyperArmorEnd = 0.5f;
	ResolveWindow(Row, nullptr, Start, End);
	TestTrue(TEXT("a row's window is used"), FMath::IsNearlyEqual(Start, 0.2f) && FMath::IsNearlyEqual(End, 0.5f));
	const FVector2D Override(0.05, 1.5);
	ResolveWindow(Row, &Override, Start, End);
	TestTrue(TEXT("an override wins over the row"), FMath::IsNearlyEqual(Start, 0.05f) && FMath::IsNearlyEqual(End, 1.5f));
	FRPGWeaponAttackRow NoWindow;
	ResolveWindow(NoWindow, &Override, Start, End);
	TestTrue(TEXT("an override opens a window on a row without one"), FMath::IsNearlyEqual(Start, 0.05f) && FMath::IsNearlyEqual(End, 1.5f));
	Row.HyperArmorEnd = 0.1f; // end before start: no window (HasHyperArmor)
	ResolveWindow(Row, nullptr, Start, End);
	TestTrue(TEXT("a row whose end is not after its start gives no window"), Start < 0.f && End < 0.f);

	// When the window wants the effect (both ends inclusive).
	TestTrue(TEXT("window open at its start"), WindowOpen(0.2f, 0.5f, 0.2f));
	TestTrue(TEXT("window open at its end"), WindowOpen(0.2f, 0.5f, 0.5f));
	TestFalse(TEXT("window closed just before"), WindowOpen(0.2f, 0.5f, 0.19f));
	TestFalse(TEXT("window closed just after"), WindowOpen(0.2f, 0.5f, 0.51f));
	TestFalse(TEXT("no start: never open"), WindowOpen(-1.f, 0.5f, 0.3f));
	TestFalse(TEXT("end not after start: never open"), WindowOpen(0.3f, 0.3f, 0.3f));

	// Stamina on top of the pack's 15: the table's rows through the rule (Freeze 5: strength heavies 35, dex 10; the starter sword keeps the pack's cost).
	const URPGWeaponAttackTable* Defaults = GetDefault<URPGWeaponAttackTable>();
	FRPGWeaponAttackRow Found;
	Defaults->Find(TEXT("ClaymoreCombatStyle"), ERPGAttackKind::JumpHeavy, Found);
	TestEqual(TEXT("a strength jump heavy takes 20 more than the pack's 15"), StaminaExtra(Found.StaminaCost, 15.f, 100.0), 20.f);
	Defaults->Find(TEXT("DualSwordCombatStyle"), ERPGAttackKind::Light, Found);
	TestEqual(TEXT("a dex light gives 5 back"), StaminaExtra(Found.StaminaCost, 15.f, 100.0), -5.f);
	Defaults->Find(TEXT("SwordCombatStyle"), ERPGAttackKind::Strong, Found);
	TestEqual(TEXT("the starter sword leaves the pack's cost"), StaminaExtra(Found.StaminaCost, 15.f, 100.0), 0.f);
	TestEqual(TEXT("a cost equal to the pack's changes nothing"), StaminaExtra(15.f, 15.f, 100.0), 0.f);
	TestEqual(TEXT("never below zero: 12 stamina left, 20 more wanted"), StaminaExtra(35.f, 15.f, 12.0), 12.f);
	TestEqual(TEXT("no stamina left: nothing more to take"), StaminaExtra(35.f, 15.f, 0.0), 0.f);
	TestEqual(TEXT("a negative stamina value takes nothing"), StaminaExtra(35.f, 15.f, -3.0), 0.f);
	TestEqual(TEXT("giving back is not limited by the stamina left"), StaminaExtra(10.f, 15.f, 0.0), -5.f);

	// The pack's timed effect (4 s): applied again when it is old enough and the window is still open.
	TestFalse(TEXT("2.9 s old: not yet"), NeedsRefresh(12.9, 10.0, 3.f));
	TestTrue(TEXT("3.0 s old: again"), NeedsRefresh(13.0, 10.0, 3.f));
	TestFalse(TEXT("a refresh time of zero switches it off"), NeedsRefresh(100.0, 10.0, 0.f));
	return true;
}

// ---------------------------------------------------------------------------------------------
// Bleed (Gate 3, M12): the status rules of the dexterity build (Freeze 20.2 and 36)
// ---------------------------------------------------------------------------------------------

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FRPGBleedRulesTest, "OneBossFight.Boss.Bleed",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::ClientContext | EAutomationTestFlags::ProductFilter)

bool FRPGBleedRulesTest::RunTest(const FString& Parameters)
{
	using namespace RPGBleedRules;
	// The Freeze 36 registry values are the component's defaults.
	const URPGBossBleed* Defaults = GetDefault<URPGBossBleed>();
	TestEqual(TEXT("initial threshold 100"), Defaults->InitialThreshold, 100.f);
	TestEqual(TEXT("threshold increase 20"), Defaults->ThresholdIncrease, 20.f);
	TestEqual(TEXT("threshold maximum 200"), Defaults->ThresholdMax, 200.f);
	TestEqual(TEXT("proc takes 10.5 percent"), Defaults->HpFraction, 0.105f);

	const FConfig Config;
	FState State;
	// Five hits of 20 proc once (Freeze 5: "five valid buildup applications"); four do not.
	for (int32 Hit = 1; Hit <= 4; ++Hit)
	{
		TestEqual(*FString::Printf(TEXT("hit %d adds"), Hit), static_cast<int32>(Apply(State, Config, 20.f, false, false, false, false)), static_cast<int32>(EResult::Added));
	}
	TestEqual(TEXT("80 of 100 after four hits"), State.Buildup, 80.f);
	TestEqual(TEXT("the fifth hit procs"), static_cast<int32>(Apply(State, Config, 20.f, false, false, false, false)), static_cast<int32>(EResult::Proc));
	TestEqual(TEXT("the buildup is reset"), State.Buildup, 0.f);
	TestEqual(TEXT("the next threshold is 120"), State.Threshold, 120.f);
	TestEqual(TEXT("one proc counted"), State.Procs, 1);
	// The thresholds rise by 20 and stop at 200: hits needed per proc are 5, 6, 7, 8, 9, 10, 10.
	const int32 Expected[] = {6, 7, 8, 9, 10, 10};
	for (int32 Index = 0; Index < 6; ++Index)
	{
		int32 Hits = 0;
		EResult Result = EResult::Added;
		while (Result != EResult::Proc && Hits < 50)
		{
			Result = Apply(State, Config, 20.f, false, false, false, false);
			++Hits;
		}
		TestEqual(*FString::Printf(TEXT("proc %d needs %d hits"), Index + 2, Expected[Index]), Hits, Expected[Index]);
	}
	TestEqual(TEXT("the threshold stays at the maximum 200"), State.Threshold, 200.f);
	TestEqual(TEXT("seven procs counted"), State.Procs, 7);

	// Nothing builds up on a dead boss, a sleeping boss, during the phase transition, or in the frame of a proc; nothing without an amount.
	FState Fresh;
	TestEqual(TEXT("dead is ignored"), static_cast<int32>(Apply(Fresh, Config, 20.f, true, false, false, false)), static_cast<int32>(EResult::IgnoredDead));
	TestEqual(TEXT("dormant is ignored"), static_cast<int32>(Apply(Fresh, Config, 20.f, false, true, false, false)), static_cast<int32>(EResult::IgnoredDormant));
	TestEqual(TEXT("the phase transition is ignored"), static_cast<int32>(Apply(Fresh, Config, 20.f, false, false, true, false)), static_cast<int32>(EResult::IgnoredTransition));
	TestEqual(TEXT("the frame of a proc is ignored"), static_cast<int32>(Apply(Fresh, Config, 20.f, false, false, false, true)), static_cast<int32>(EResult::IgnoredSameFrame));
	TestEqual(TEXT("no amount is ignored"), static_cast<int32>(Apply(Fresh, Config, 0.f, false, false, false, false)), static_cast<int32>(EResult::IgnoredAmount));
	TestEqual(TEXT("an ignored hit leaves the buildup at 0"), Fresh.Buildup, 0.f);
	// Dead wins over the others (the order of the checks).
	TestEqual(TEXT("dead wins over dormant and transition"), static_cast<int32>(Apply(Fresh, Config, 20.f, true, true, true, true)), static_cast<int32>(EResult::IgnoredDead));
	// A crossing with a surplus procs once and resets to 0 (no carry over).
	FState Surplus;
	Surplus.Buildup = 90.f;
	TestEqual(TEXT("90 + 30 crosses 100 once"), static_cast<int32>(Apply(Surplus, Config, 30.f, false, false, false, false)), static_cast<int32>(EResult::Proc));
	TestEqual(TEXT("no carry over"), Surplus.Buildup, 0.f);

	// The burst: 10.5 percent of the maximum health, never the last point.
	TestEqual(TEXT("10.5 percent of 500 is 52.5"), ProcDamage(500.f, 500.f, Config), 52.5f);
	TestEqual(TEXT("with 40 health left the proc leaves 1"), ProcDamage(500.f, 40.f, Config), 39.f);
	TestEqual(TEXT("with half a point left it takes nothing"), ProcDamage(500.f, 0.5f, Config), 0.f);
	TestEqual(TEXT("names are stable (the drivers read them)"), FString(Name(EResult::Proc)), FString(TEXT("proc")));
	return true;
}

// ---------------------------------------------------------------------------------------------
// Legend pass (SPEC_M3): camera shake scale, time dilation bookkeeping, defaults
// ---------------------------------------------------------------------------------------------

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FRPGLegendShakeScaleTest, "OneBossFight.Legend.ShakeScale",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::ClientContext | EAutomationTestFlags::ProductFilter)

bool FRPGLegendShakeScaleTest::RunTest(const FString& Parameters)
{
	TestNearlyEqual(TEXT("at the epicentre"), RPGLegend::ShakeScale(0.f, 500.f, 2500.f, 1.5f), 1.f);
	TestNearlyEqual(TEXT("at the inner radius"), RPGLegend::ShakeScale(500.f, 500.f, 2500.f, 1.5f), 1.f);
	TestNearlyEqual(TEXT("halfway, falloff 1.5"), RPGLegend::ShakeScale(1500.f, 500.f, 2500.f, 1.5f), FMath::Pow(0.5f, 1.5f), 0.0001f);
	TestNearlyEqual(TEXT("halfway, falloff 1"), RPGLegend::ShakeScale(1500.f, 500.f, 2500.f, 1.f), 0.5f, 0.0001f);
	TestNearlyEqual(TEXT("halfway, falloff 2"), RPGLegend::ShakeScale(1500.f, 500.f, 2500.f, 2.f), 0.25f, 0.0001f);
	TestNearlyEqual(TEXT("at the outer radius"), RPGLegend::ShakeScale(2500.f, 500.f, 2500.f, 1.5f), 0.f);
	TestNearlyEqual(TEXT("beyond the outer radius"), RPGLegend::ShakeScale(9000.f, 500.f, 2500.f, 1.5f), 0.f);
	TestNearlyEqual(TEXT("a negative distance counts as zero"), RPGLegend::ShakeScale(-5.f, 500.f, 2500.f, 1.5f), 1.f);
	// Outer at or below Inner is a cliff, never a division by zero.
	TestNearlyEqual(TEXT("cliff inside"), RPGLegend::ShakeScale(400.f, 500.f, 500.f, 1.5f), 1.f);
	TestNearlyEqual(TEXT("cliff outside"), RPGLegend::ShakeScale(501.f, 500.f, 500.f, 1.5f), 0.f);
	TestNearlyEqual(TEXT("inverted radii are a cliff too"), RPGLegend::ShakeScale(501.f, 500.f, 100.f, 1.5f), 0.f);
	// The slam at the player's usual distance (600 cm) is nearly full, at 1500 cm it is a third.
	const FRPGShakeSettings Slam = GetDefault<URPGBossLegend>()->Slam;
	TestTrue(TEXT("slam at 600 cm is above 0.9"), RPGLegend::ShakeScale(600.f, Slam.InnerRadius, Slam.OuterRadius, Slam.Falloff) > 0.9f);
	const float Far = RPGLegend::ShakeScale(1500.f, Slam.InnerRadius, Slam.OuterRadius, Slam.Falloff);
	TestTrue(TEXT("slam at 1500 cm is between 0.2 and 0.4"), Far > 0.2f && Far < 0.4f);
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FRPGLegendDilationScopeTest, "OneBossFight.Legend.DilationScope",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::ClientContext | EAutomationTestFlags::ProductFilter)

bool FRPGLegendDilationScopeTest::RunTest(const FString& Parameters)
{
	FRPGDilationScope Scope;
	TestFalse(TEXT("idle"), Scope.bActive);
	TestTrue(TEXT("the first request starts the effect"), Scope.Begin(0.25f, 100.0, 1.2, 1.f));
	TestNearlyEqual(TEXT("saved is what the first request saw"), Scope.Saved, 1.f);
	TestNearlyEqual(TEXT("applied is absolute"), Scope.Applied, 0.25f);
	// A second request 0.5 s later sees the already dilated world: it must not capture 0.25 as the value to restore, and must not multiply.
	TestFalse(TEXT("the second request only extends"), Scope.Begin(0.25f, 100.5, 1.2, 0.25f));
	TestNearlyEqual(TEXT("saved stays 1"), Scope.Saved, 1.f);
	TestNearlyEqual(TEXT("applied stays 0.25 (never 0.0625)"), Scope.Applied, 0.25f);
	TestEqual(TEXT("the deadline moved to the later one"), Scope.DeadlineReal, 101.7);
	// A request that would end sooner never shortens it.
	Scope.Begin(0.25f, 100.6, 0.01, 0.25f);
	TestEqual(TEXT("the deadline never moves earlier"), Scope.DeadlineReal, 101.7);
	TestFalse(TEXT("not expired just before"), Scope.Expired(101.69));
	TestTrue(TEXT("expired at the deadline"), Scope.Expired(101.7));
	TestNearlyEqual(TEXT("end returns the saved value"), Scope.End(), 1.f);
	TestFalse(TEXT("inactive after the end"), Scope.bActive);
	TestFalse(TEXT("an inactive scope is never expired"), Scope.Expired(1000.0));

	// 20 random sequences of requests and ends against a world value: after every end the world is back to what it was before the first request.
	FRandomStream Random(7);
	for (int32 Sequence = 0; Sequence < 20; ++Sequence)
	{
		float World = 1.f;
		FRPGDilationScope S;
		double Now = 0.0;
		for (int32 Step = 0; Step < 30; ++Step)
		{
			Now += Random.FRandRange(0.f, 0.5f);
			if (Random.FRand() < 0.6f)
			{
				if (S.Begin(Random.FRand() < 0.5f ? 0.05f : 0.25f, Now, Random.FRandRange(0.05f, 1.f), World))
				{
					World = S.Applied;
				}
			}
			else if (S.bActive)
			{
				World = S.End();
				TestNearlyEqual(*FString::Printf(TEXT("sequence %d step %d restored"), Sequence, Step), World, 1.f);
			}
		}
		if (S.bActive)
		{
			World = S.End();
		}
		TestNearlyEqual(*FString::Printf(TEXT("sequence %d ends restored"), Sequence), World, 1.f);
	}
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FRPGLegendDefaultsTest, "OneBossFight.Legend.Defaults",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::ClientContext | EAutomationTestFlags::ProductFilter)

bool FRPGLegendDefaultsTest::RunTest(const FString& Parameters)
{
	const URPGBossLegend* Legend = GetDefault<URPGBossLegend>();
	TestTrue(TEXT("hit stop 0.06 to 0.10 s (the Freeze task)"), Legend->HitStopSeconds >= 0.06f && Legend->HitStopSeconds <= 0.10f);
	TestTrue(TEXT("hit stop dilation is nearly frozen but above zero"), Legend->HitStopDilation > 0.f && Legend->HitStopDilation <= 0.1f);
	TestEqual(TEXT("slow motion scale 0.25"), Legend->SlowMotionScale, 0.25f);
	TestEqual(TEXT("slow motion 1.2 s"), Legend->SlowMotionSeconds, 1.2f);
	TestTrue(TEXT("no hit stop on a lethal riposte"), Legend->bSkipHitStopOnLethal);
	// A shake is applied after the camera spring arm (34 cm probe): its location amplitude stays far below it.
	TestTrue(TEXT("slam location amplitude under 10 cm"), Legend->Slam.LocationAmplitude.GetMax() <= 10.0);
	TestTrue(TEXT("roar location amplitude under 10 cm"), Legend->Roar.LocationAmplitude.GetMax() <= 10.0);
	TestTrue(TEXT("the roar is felt farther than the slam"), Legend->Roar.OuterRadius > Legend->Slam.OuterRadius);
	TestEqual(TEXT("the roar shake lasts as long as the roar clip (1.5 s)"), Legend->Roar.Duration, 1.5f);
	const URPGBossMusic* Music = GetDefault<URPGBossMusic>();
	TestTrue(TEXT("crossfade is above zero"), Music->CrossfadeSeconds > 0.f);
	TestTrue(TEXT("Phase 2 plays quieter than Phase 1 (it measures louder)"), Music->PhaseTwoVolume < Music->Volume);
	TestTrue(TEXT("the victory fade is shorter than the 4 s fade (the pack removes the boss about 3.5 s after death)"), Music->VictoryFadeOutSeconds < Music->FadeOutSeconds);
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

	// The weapon trace facade (Pack/RPGPackTrace, used by URPGTraceGuard and URPGTraceAudit) reads these names of the pack's trace classes by reflection: a pack update that renames one fails here, not silently in a fight.
	FString MissingTraceNames;
	const bool bTraceNames = RPGPackTrace::CheckClassNames(MissingTraceNames);
	TestTrue(*FString::Printf(TEXT("the pack's trace classes have every name the facade reads (missing: %s)"), *MissingTraceNames), bTraceNames);

	// The hit intake (Player/RPGHitIntake) binds to the player's OnHit(FHitResult) and reads the trace target's HitData and the attack data by name; the classifier names the four melee attack data assets.
	FString MissingHitNames;
	const bool bHitNames = URPGHitIntake::CheckPackNames(MissingHitNames);
	TestTrue(*FString::Printf(TEXT("the pack's hit classes have every name the hit intake reads (missing: %s)"), *MissingHitNames), bHitNames);

	// Sounds the subsystem and the dressing script assign by path: concrete footsteps, the placeholder boss music, the fire crackle and the wind bed.
	for (const TCHAR* Sound : {TEXT("/Game/Essential_Foosteps_SK/CUE/Concrete/Footstep_Concrete_Boots_Walk_1_Cue"), TEXT("/Game/Essential_Foosteps_SK/CUE/Concrete/Footstep_Concrete_Boots_Jog_8_Cue"),
		TEXT("/Game/Essential_Foosteps_SK/CUE/Concrete/Footstep_Concrete_Boots_Run_8_Cue"), TEXT("/Game/Essential_Foosteps_SK/CUE/Concrete/Footstep_Concrete_Boots_Land_4_Cue"),
		TEXT("/Game/StarterContent/Audio/Starter_Music_Cue"), TEXT("/Game/StarterContent/Audio/Fire01_Cue"), TEXT("/Game/StarterContent/Audio/Starter_Wind05")})
	{
		TestTrue(*FString::Printf(TEXT("sound %s exists"), Sound), FPackageName::DoesPackageExist(Sound));
	}
	// The two boss music tracks the subsystem loads by path (Scripts/Editor/import_audio.py puts them there).
	for (const TCHAR* Track : {TEXT("/Game/OneBossFight/Audio/MX_Boss01_Phase1"), TEXT("/Game/OneBossFight/Audio/MX_Boss01_Phase2")})
	{
		TestTrue(*FString::Printf(TEXT("boss music %s exists"), Track), FPackageName::DoesPackageExist(Track));
	}

	// The boss stance break (Player/RPGBossStagger) names its clips and the pack's immunity effect by path.
	const URPGBossStagger* StaggerDefaults = GetDefault<URPGBossStagger>();
	TestNotNull(TEXT("stance break fall montage"), StaggerDefaults->FallMontage.LoadSynchronous());
	TestNotNull(TEXT("stance break get-up montage"), StaggerDefaults->GetUpMontage.LoadSynchronous());
	TestNotNull(TEXT("hit stun immunity effect"), StaggerDefaults->ImmunityEffect.LoadSynchronous());
	// A4 low sweep and A5 heal punish (Player/RPGBossLowSweep, RPGBossHealPunish): the clips they play through the attack tracker, the pack's drink montage whose start is the heal signal, and the Freeze values.
	TestNotNull(TEXT("the pack's drink montage (the heal start signal of A5)"), LoadObject<UAnimMontage>(nullptr, TEXT("/Game/AdvancedARPGCombat/MeleeCombatSystem/Animations/DrinkingPotion_Montage.DrinkingPotion_Montage")));
	const URPGAttackTracker* TrackerDefaults = GetDefault<URPGAttackTracker>();
	for (const TCHAR* Move : {TEXT("A4"), TEXT("A5")})
	{
		const FRPGAttackTiming* Timing = TrackerDefaults->Attacks.FindByPredicate([Move](const FRPGAttackTiming& T) { return T.MoveId == FName(Move); });
		TestTrue(*FString::Printf(TEXT("%s is a tracked move with a clip"), Move), Timing && !Timing->ClipPath.IsEmpty());
		TestTrue(*FString::Printf(TEXT("the clip of %s exists"), Move), Timing && FPackageName::DoesPackageExist(FPackageName::ObjectPathToPackageName(Timing->ClipPath)));
	}
	const URPGBossHealPunish* PunishDefaults = GetDefault<URPGBossHealPunish>();
	TestEqual(TEXT("heal punish minimum range is 400 cm"), PunishDefaults->MinRange, 400.f);
	TestEqual(TEXT("heal punish maximum range is 1000 cm"), PunishDefaults->MaxRange, 1000.f);
	TestEqual(TEXT("heal punish cooldown is 4 s"), PunishDefaults->Cooldown, 4.f);
	// Dodgeable on the heal exit: the release (0.45 s) plus the flight lands after the 1.13 s drink animation plus the 0.2 s a dodge needs to start moving.
	TestTrue(TEXT("the javelin lands after the player can dodge"), 0.45f + PunishDefaults->FlightTime >= 1.13f + 0.2f);
	TestTrue(TEXT("the A4 blade is at most 40 cm high (a jump clears it)"), GetDefault<URPGBossLowSweep>()->BladeHeight <= 40.f);
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
	// Camera rig (Player/RPGCameraRig): a probe wider than the near clip distance and a limited upward pitch keep the camera off the floor.
	const URPGCameraRig* CameraDefaults = GetDefault<URPGCameraRig>();
	TestTrue(TEXT("camera probe is wider than the near clip plane"), CameraDefaults->ProbeSize >= 25.f);
	TestTrue(TEXT("camera looks up at most 45 degrees"), CameraDefaults->PitchMax <= 45.f && CameraDefaults->PitchMin >= -80.f);
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

// ---------------------------------------------------------------------------------------------
// Packaging (Gate 4 groundwork): every asset the C++ loads by path must be cooked
// ---------------------------------------------------------------------------------------------

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FRPGCookCoverageTest, "OneBossFight.Content.CookCoverage",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::ProductFilter)

bool FRPGCookCoverageTest::RunTest(const FString& Parameters)
{
	// The cooker finds an asset through the references of the assets it cooks. An asset that only C++ loads by a /Game path (LoadObject, a soft path in a component's defaults) has no such reference and is left out of a
	// packaged build, so the A4 sweep clip, the music or the weapon attack table would silently be missing there. Config/DefaultGame.ini lists the directories that are always cooked: every /Game path literal in the sources must be under one.
	TArray<FString> CookDirectories;
	TArray<FString> Entries;
	GConfig->GetArray(TEXT("/Script/UnrealEd.ProjectPackagingSettings"), TEXT("DirectoriesToAlwaysCook"), Entries, GGameIni);
	for (const FString& Entry : Entries)
	{
		int32 Start = INDEX_NONE;
		if (Entry.FindChar(TEXT('"'), Start))
		{
			const int32 End = Entry.Find(TEXT("\""), ESearchCase::CaseSensitive, ESearchDir::FromStart, Start + 1);
			if (End > Start)
			{
				CookDirectories.Add(Entry.Mid(Start + 1, End - Start - 1));
			}
		}
	}
	TestTrue(TEXT("Config/DefaultGame.ini lists directories to always cook"), CookDirectories.Num() > 0);

	// Path literals that are directory prefixes used for filtering, not assets that are loaded (the PackWiring test above).
	const TSet<FString> NotAssets = {TEXT("/Game/AdvancedARPGCombat"), TEXT("/Game/OneBossFight/GreystonePack"), TEXT("/Game/OneBossFight/SevarogPack")};
	TArray<FString> Files;
	IFileManager::Get().FindFilesRecursive(Files, *(FPaths::ProjectDir() / TEXT("Source/OneBossFight")), TEXT("*.cpp"), true, false);
	IFileManager::Get().FindFilesRecursive(Files, *(FPaths::ProjectDir() / TEXT("Source/OneBossFight")), TEXT("*.h"), true, false, /*bClearFileNames=*/false);
	TestTrue(TEXT("the sources are found next to the project"), Files.Num() > 20);
	const FRegexPattern Pattern(TEXT("\"(/Game/[^\"]+)\""));
	TSet<FString> Seen;
	int32 Checked = 0;
	for (const FString& File : Files)
	{
		FString Text;
		if (!FFileHelper::LoadFileToString(Text, *File))
		{
			continue;
		}
		FRegexMatcher Matcher(Pattern, Text);
		while (Matcher.FindNext())
		{
			FString Path = Matcher.GetCaptureGroup(1);
			int32 Format = INDEX_NONE;
			if (Path.FindChar(TEXT('%'), Format))
			{
				Path = Path.Left(Format); // "/Game/Dir/%s.%s": the directory part decides
			}
			if (Path.EndsWith(TEXT("/")) || NotAssets.Contains(Path) || Seen.Contains(Path))
			{
				continue;
			}
			Seen.Add(Path);
			++Checked;
			bool bCovered = false;
			for (const FString& Dir : CookDirectories)
			{
				if (Path.StartsWith(Dir + TEXT("/")))
				{
					bCovered = true;
					break;
				}
			}
			if (!bCovered)
			{
				AddError(FString::Printf(TEXT("%s is loaded by path in %s and is not under a directory of DirectoriesToAlwaysCook (Config/DefaultGame.ini): a packaged build would not contain it"), *Path, *FPaths::GetCleanFilename(File)));
			}
		}
	}
	TestTrue(*FString::Printf(TEXT("path literals were found (%d in %d files)"), Checked, Files.Num()), Checked > 30);
	return true;
}

#endif // WITH_DEV_AUTOMATION_TESTS
