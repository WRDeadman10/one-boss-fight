// Copyright One Boss Fight. All Rights Reserved.

#include "Misc/AutomationTest.h"

#if WITH_DEV_AUTOMATION_TESTS

#include "Arena/RPGGreyboxArena.h"
#include "Benchmark/RPGFrameStats.h"
#include "Characters/RPGPlayerCharacter.h"
#include "Characters/RPGTrainingDummy.h"
#include "Combat/RPGAttributeComponent.h"
#include "Combat/RPGCombatComponent.h"
#include "Combat/RPGMeleeTraceComponent.h"
#include "Combat/RPGTargetLockComponent.h"
#include "Combat/RPGWeaponData.h"
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

	template <typename T>
	T* SpawnCombatant(UWorld* World, const FVector& Location, const FRotator& Rotation = FRotator::ZeroRotator)
	{
		FActorSpawnParameters Params;
		Params.SpawnCollisionHandlingOverride = ESpawnActorCollisionHandlingMethod::AlwaysSpawn;
		return World->SpawnActor<T>(Location, Rotation, Params);
	}

	/** A hit with the given damage and poise damage, coming from the +X side so a target facing +X is hit head-on. */
	FRPGHitInfo MakeHit(float Damage, float PoiseDamage)
	{
		FRPGHitInfo Hit;
		Hit.Damage = Damage;
		Hit.PoiseDamage = PoiseDamage;
		Hit.HitDirection = FVector(-1.f, 0.f, 0.f);
		return Hit;
	}
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

// ---------------------------------------------------------------------------------------------
// Combat: attributes
// ---------------------------------------------------------------------------------------------

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FRPGAttributesTest, "OneBossFight.Combat.Attributes",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::ClientContext | EAutomationTestFlags::ProductFilter)

bool FRPGAttributesTest::RunTest(const FString& Parameters)
{
	URPGAttributeComponent* Attr = NewObject<URPGAttributeComponent>(GetTransientPackage());
	TestEqual(TEXT("health starts full"), Attr->GetHealth(), 100.f);
	TestEqual(TEXT("stamina starts full"), Attr->GetStamina(), 100.f);
	TestEqual(TEXT("poise starts full"), Attr->GetPoise(), 40.f);

	// Health: damage is clamped and reported; non-positive damage does nothing.
	TestEqual(TEXT("damage applied"), Attr->ApplyDamage(30.f), 30.f);
	TestEqual(TEXT("health after damage"), Attr->GetHealth(), 70.f);
	TestEqual(TEXT("negative damage ignored"), Attr->ApplyDamage(-5.f), 0.f);
	Attr->Heal(500.f);
	TestEqual(TEXT("heal clamps to max"), Attr->GetHealth(), 100.f);

	// Stamina: spend, wait out the delay, regenerate.
	TestTrue(TEXT("spend 30"), Attr->TryConsumeStamina(30.f));
	TestEqual(TEXT("stamina after spend"), Attr->GetStamina(), 70.f);
	Attr->TickAttributes(0.5f);
	TestEqual(TEXT("no regen inside the delay"), Attr->GetStamina(), 70.f);
	Attr->TickAttributes(0.4f);
	TestTrue(TEXT("regen after the delay"), Attr->GetStamina() > 70.f);

	// An action is allowed with any stamina left; it just empties the bar. Zero stamina refuses.
	TestTrue(TEXT("overspend allowed while stamina > 0"), Attr->TryConsumeStamina(1000.f));
	TestEqual(TEXT("stamina emptied"), Attr->GetStamina(), 0.f);
	TestFalse(TEXT("refused at zero stamina"), Attr->TryConsumeStamina(1.f));
	TestTrue(TEXT("zero cost always allowed"), Attr->TryConsumeStamina(0.f));

	// Continuous drain stops at zero.
	Attr->ResetAttributes();
	Attr->SetStaminaDrain(50.f);
	Attr->TickAttributes(1.f);
	TestEqual(TEXT("drained half"), Attr->GetStamina(), 50.f, 0.01f);
	Attr->TickAttributes(1.f);
	TestEqual(TEXT("drained to zero"), Attr->GetStamina(), 0.f, 0.01f);
	Attr->TickAttributes(5.f);
	TestEqual(TEXT("drain stopped, regen starts only after the delay"), Attr->GetStamina() > 0.f, true);

	// Poise: builds toward a break, which reports once and refills; quiet time also refills it.
	Attr->ResetAttributes();
	TestFalse(TEXT("first poise hit holds"), Attr->ApplyPoiseDamage(15.f));
	TestEqual(TEXT("poise after first hit"), Attr->GetPoise(), 25.f);
	TestFalse(TEXT("second poise hit holds"), Attr->ApplyPoiseDamage(15.f));
	TestTrue(TEXT("third poise hit breaks"), Attr->ApplyPoiseDamage(15.f));
	TestEqual(TEXT("poise refilled after the break"), Attr->GetPoise(), 40.f);
	Attr->ApplyPoiseDamage(10.f);
	Attr->TickAttributes(4.1f);
	TestEqual(TEXT("poise resets after quiet time"), Attr->GetPoise(), 40.f);

	// Death happens once and blocks further changes until reset.
	Attr->ResetAttributes();
	TestEqual(TEXT("lethal damage clamps"), Attr->ApplyDamage(1000.f), 100.f);
	TestTrue(TEXT("dead"), Attr->IsDead());
	TestEqual(TEXT("no damage after death"), Attr->ApplyDamage(10.f), 0.f);
	Attr->Heal(50.f);
	TestEqual(TEXT("no heal after death"), Attr->GetHealth(), 0.f);
	TestFalse(TEXT("no stamina use when dead"), Attr->TryConsumeStamina(5.f));
	Attr->ResetAttributes();
	TestFalse(TEXT("reset clears death"), Attr->IsDead());
	TestEqual(TEXT("reset restores health"), Attr->GetHealth(), 100.f);
	return true;
}

// ---------------------------------------------------------------------------------------------
// Combat: state machine
// ---------------------------------------------------------------------------------------------

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FRPGCombatAttackChainTest, "OneBossFight.Combat.StateMachine.AttackChain",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::ClientContext | EAutomationTestFlags::ProductFilter)

bool FRPGCombatAttackChainTest::RunTest(const FString& Parameters)
{
	RPGTests::FScopedTestWorld Scope;
	ARPGTrainingDummy* Actor = RPGTests::SpawnCombatant<ARPGTrainingDummy>(Scope.World, FVector(0.f, 0.f, 100.f));
	if (!TestNotNull(TEXT("combatant spawned"), Actor))
	{
		return false;
	}
	URPGCombatComponent* Combat = Actor->GetCombat();
	URPGAttributeComponent* Attr = Actor->GetAttributes();

	URPGWeaponData* Weapon = NewObject<URPGWeaponData>(GetTransientPackage());
	Weapon->LightCombo.SetNum(3);
	Combat->Weapon = Weapon;

	TestEqual(TEXT("starts in locomotion"), Combat->GetState(), ERPGCombatState::Locomotion);

	// A stale notify outside an attack must not arm the trace.
	Combat->SetHitWindow(true);
	TestFalse(TEXT("hit window ignored outside an attack"), Combat->IsHitWindowOpen());

	TestTrue(TEXT("light attack starts"), Combat->RequestLightAttack());
	TestEqual(TEXT("attacking"), Combat->GetState(), ERPGCombatState::Attacking);
	TestEqual(TEXT("first chain index"), Combat->GetComboIndex(), 0);
	TestEqual(TEXT("stamina spent once"), Attr->GetStamina(), 80.f);

	Combat->TickCombat(0.3f);
	TestTrue(TEXT("hit window open mid-swing"), Combat->IsHitWindowOpen());
	TestEqual(TEXT("still attacking"), Combat->GetState(), ERPGCombatState::Attacking);

	// Pressing again too early is refused but remembered (within the 0.4 s buffer time).
	TestFalse(TEXT("second press refused while attacking"), Combat->RequestLightAttack());
	TestEqual(TEXT("press buffered"), Combat->GetBufferedAction(), ERPGBufferedAction::LightAttack);
	TestEqual(TEXT("buffer costs nothing"), Attr->GetStamina(), 80.f);

	// The combo window opens, the buffered press is consumed, and the chain advances.
	Combat->TickCombat(0.25f);
	TestFalse(TEXT("hit window closed"), Combat->IsHitWindowOpen());
	TestEqual(TEXT("chain advanced"), Combat->GetComboIndex(), 1);
	TestEqual(TEXT("second attack running"), Combat->GetState(), ERPGCombatState::Attacking);
	TestEqual(TEXT("buffer consumed"), Combat->GetBufferedAction(), ERPGBufferedAction::None);
	TestEqual(TEXT("second attack spent stamina"), Attr->GetStamina(), 60.f);

	// Open combo window with no buffered press: the state waits, a later press continues the chain.
	Combat->TickCombat(0.55f);
	TestEqual(TEXT("waiting in combo window"), Combat->GetState(), ERPGCombatState::ComboWindow);
	TestTrue(TEXT("press inside combo window"), Combat->RequestLightAttack());
	TestEqual(TEXT("third chain index"), Combat->GetComboIndex(), 2);

	Combat->TickCombat(0.55f);
	TestTrue(TEXT("press inside combo window again"), Combat->RequestLightAttack());
	TestEqual(TEXT("chain wraps to the start"), Combat->GetComboIndex(), 0);

	// No press: the action ends and control returns.
	Combat->TickCombat(1.f);
	TestEqual(TEXT("back to locomotion"), Combat->GetState(), ERPGCombatState::Locomotion);
	TestFalse(TEXT("no windows left open"), Combat->IsHitWindowOpen());

	// Out of stamina: refused, and not buffered (it would never become possible within the buffer time).
	Attr->ForceConsumeStamina(1000.f);
	TestFalse(TEXT("no stamina, no attack"), Combat->RequestLightAttack());
	TestEqual(TEXT("still locomotion"), Combat->GetState(), ERPGCombatState::Locomotion);
	TestEqual(TEXT("nothing buffered"), Combat->GetBufferedAction(), ERPGBufferedAction::None);

	// A buffered press expires.
	Attr->ResetAttributes();
	Combat->RequestHeavyAttack();
	Combat->RequestLightAttack();
	TestEqual(TEXT("buffered while attacking"), Combat->GetBufferedAction(), ERPGBufferedAction::LightAttack);
	Combat->TickCombat(0.1f);
	TestEqual(TEXT("still buffered at 0.1s"), Combat->GetBufferedAction(), ERPGBufferedAction::LightAttack);
	Combat->TickCombat(0.35f);
	TestEqual(TEXT("expired after the buffer time"), Combat->GetBufferedAction(), ERPGBufferedAction::None);
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FRPGCombatDodgeTest, "OneBossFight.Combat.StateMachine.Dodge",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::ClientContext | EAutomationTestFlags::ProductFilter)

bool FRPGCombatDodgeTest::RunTest(const FString& Parameters)
{
	RPGTests::FScopedTestWorld Scope;
	ARPGTrainingDummy* Actor = RPGTests::SpawnCombatant<ARPGTrainingDummy>(Scope.World, FVector(0.f, 0.f, 100.f));
	if (!TestNotNull(TEXT("combatant spawned"), Actor))
	{
		return false;
	}
	URPGCombatComponent* Combat = Actor->GetCombat();
	URPGAttributeComponent* Attr = Actor->GetAttributes();

	// An attack cannot be dodge-cancelled until its cancel window opens.
	TestTrue(TEXT("attack starts"), Combat->RequestLightAttack());
	TestFalse(TEXT("dodge refused mid-attack"), Combat->RequestDodge(FVector(1.f, 0.f, 0.f)));
	TestEqual(TEXT("dodge buffered"), Combat->GetBufferedAction(), ERPGBufferedAction::Dodge);
	TestEqual(TEXT("still attacking"), Combat->GetState(), ERPGCombatState::Attacking);

	Combat->SetCancelWindow(true);
	TestEqual(TEXT("cancel window starts the buffered dodge"), Combat->GetState(), ERPGCombatState::Dodging);
	TestEqual(TEXT("stamina: attack 20 + dodge 25"), Attr->GetStamina(), 55.f);

	// I-frames: not at the start, then on, then off.
	TestFalse(TEXT("no i-frames at the very start"), Combat->IsInvulnerable());
	Combat->TickCombat(0.1f);
	TestTrue(TEXT("i-frames active"), Combat->IsInvulnerable());

	const FRPGHitResult Dodged = Combat->ProcessIncomingHit(RPGTests::MakeHit(30.f, 0.f));
	TestTrue(TEXT("hit ignored during i-frames"), Dodged.bIgnoredInvulnerable);
	TestEqual(TEXT("no damage during i-frames"), Attr->GetHealth(), 100.f);

	Combat->TickCombat(0.3f);
	TestFalse(TEXT("i-frames over"), Combat->IsInvulnerable());
	const FRPGHitResult Late = Combat->ProcessIncomingHit(RPGTests::MakeHit(30.f, 0.f));
	TestEqual(TEXT("damage after i-frames"), Late.DamageApplied, 30.f);

	// The dodge ends by itself and returns control; stamina was charged exactly once.
	Combat->TickCombat(0.3f);
	TestEqual(TEXT("back to locomotion"), Combat->GetState(), ERPGCombatState::Locomotion);
	TestFalse(TEXT("no i-frames after the dodge"), Combat->IsInvulnerable());
	TestEqual(TEXT("stamina charged once"), Attr->GetStamina(), 55.f);

	// No stamina, no dodge.
	Attr->ForceConsumeStamina(1000.f);
	TestFalse(TEXT("dodge needs stamina"), Combat->RequestDodge(FVector::ZeroVector));
	TestEqual(TEXT("stayed in locomotion"), Combat->GetState(), ERPGCombatState::Locomotion);
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FRPGCombatDamagePathTest, "OneBossFight.Combat.StateMachine.DamagePath",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::ClientContext | EAutomationTestFlags::ProductFilter)

bool FRPGCombatDamagePathTest::RunTest(const FString& Parameters)
{
	RPGTests::FScopedTestWorld Scope;
	ARPGTrainingDummy* Actor = RPGTests::SpawnCombatant<ARPGTrainingDummy>(Scope.World, FVector(0.f, 0.f, 100.f));
	if (!TestNotNull(TEXT("combatant spawned"), Actor))
	{
		return false;
	}
	URPGCombatComponent* Combat = Actor->GetCombat();
	URPGAttributeComponent* Attr = Actor->GetAttributes();

	// Poise: two small hits are absorbed, the third breaks poise and staggers.
	TestFalse(TEXT("hit 1 no stagger"), Combat->ProcessIncomingHit(RPGTests::MakeHit(10.f, 15.f)).bPoiseBroken);
	TestFalse(TEXT("hit 2 no stagger"), Combat->ProcessIncomingHit(RPGTests::MakeHit(10.f, 15.f)).bPoiseBroken);
	TestEqual(TEXT("not staggered yet"), Combat->GetState(), ERPGCombatState::Locomotion);
	TestTrue(TEXT("hit 3 breaks poise"), Combat->ProcessIncomingHit(RPGTests::MakeHit(10.f, 15.f)).bPoiseBroken);
	TestEqual(TEXT("staggered"), Combat->GetState(), ERPGCombatState::Staggered);
	TestEqual(TEXT("three hits of 10"), Attr->GetHealth(), 70.f);

	// A staggered character cannot act, and refused inputs are not buffered.
	TestFalse(TEXT("no attack while staggered"), Combat->RequestLightAttack());
	TestFalse(TEXT("no dodge while staggered"), Combat->RequestDodge(FVector::ZeroVector));
	TestEqual(TEXT("nothing buffered"), Combat->GetBufferedAction(), ERPGBufferedAction::None);
	TestFalse(TEXT("cannot move while staggered"), Combat->CanMove());
	Combat->TickCombat(0.8f);
	TestEqual(TEXT("recovers from stagger"), Combat->GetState(), ERPGCombatState::Locomotion);

	// Blocking from the front: reduced damage, stamina pays, no poise damage.
	Actor->ResetCombatant();
	TestTrue(TEXT("block starts"), Combat->StartBlock());
	const FRPGHitResult Blocked = Combat->ProcessIncomingHit(RPGTests::MakeHit(50.f, 30.f));
	TestTrue(TEXT("hit blocked"), Blocked.bBlocked);
	TestEqual(TEXT("blocked damage is reduced"), Blocked.DamageApplied, 10.f, 0.01f);
	TestEqual(TEXT("stamina paid for the block"), Attr->GetStamina(), 60.f, 0.01f);
	TestEqual(TEXT("poise untouched by a block"), Attr->GetPoise(), 40.f);
	TestEqual(TEXT("still blocking"), Combat->GetState(), ERPGCombatState::Blocking);

	// A hit from behind ignores the block.
	FRPGHitInfo FromBehind = RPGTests::MakeHit(20.f, 0.f);
	FromBehind.HitDirection = FVector(1.f, 0.f, 0.f);
	const FRPGHitResult Behind = Combat->ProcessIncomingHit(FromBehind);
	TestFalse(TEXT("back hit not blocked"), Behind.bBlocked);
	TestEqual(TEXT("back hit full damage"), Behind.DamageApplied, 20.f);

	// Unblockable hits go through too.
	FRPGHitInfo Grab = RPGTests::MakeHit(20.f, 0.f);
	Grab.bUnblockable = true;
	TestFalse(TEXT("unblockable not blocked"), Combat->ProcessIncomingHit(Grab).bBlocked);

	// Empty stamina breaks the guard.
	Actor->ResetCombatant();
	Combat->StartBlock();
	Attr->ForceConsumeStamina(95.f);
	TestTrue(TEXT("guard break"), Combat->ProcessIncomingHit(RPGTests::MakeHit(20.f, 0.f)).bPoiseBroken);
	TestEqual(TEXT("guard break staggers"), Combat->GetState(), ERPGCombatState::Staggered);

	// Death: lethal hit reports once, then everything is refused until reset.
	Actor->ResetCombatant();
	const FRPGHitResult Lethal = Combat->ProcessIncomingHit(RPGTests::MakeHit(500.f, 0.f));
	TestTrue(TEXT("killed"), Lethal.bKilled);
	TestEqual(TEXT("dead state"), Combat->GetState(), ERPGCombatState::Dead);
	TestFalse(TEXT("dead target ignores hits"), Combat->ProcessIncomingHit(RPGTests::MakeHit(10.f, 0.f)).bProcessed);
	TestFalse(TEXT("dead cannot attack"), Combat->RequestLightAttack());
	TestFalse(TEXT("dead cannot dodge"), Combat->RequestDodge(FVector::ZeroVector));
	Combat->SetHitWindow(true);
	TestFalse(TEXT("dead cannot open a hit window"), Combat->IsHitWindowOpen());

	Actor->ResetCombatant();
	TestEqual(TEXT("reset returns to locomotion"), Combat->GetState(), ERPGCombatState::Locomotion);
	TestEqual(TEXT("reset restores health"), Attr->GetHealth(), 100.f);
	TestFalse(TEXT("reset clears death"), Attr->IsDead());
	return true;
}

// ---------------------------------------------------------------------------------------------
// Combat: hit detection
// ---------------------------------------------------------------------------------------------

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FRPGMeleeHitDetectionTest, "OneBossFight.Combat.HitDetection.OneHitPerSwing",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::ClientContext | EAutomationTestFlags::ProductFilter)

bool FRPGMeleeHitDetectionTest::RunTest(const FString& Parameters)
{
	RPGTests::FScopedTestWorld Scope;
	UWorld* World = Scope.World;
	ARPGPlayerCharacter* Attacker = RPGTests::SpawnCombatant<ARPGPlayerCharacter>(World, FVector(0.f, 0.f, 100.f));
	ARPGTrainingDummy* Target = RPGTests::SpawnCombatant<ARPGTrainingDummy>(World, FVector(300.f, 0.f, 100.f));
	if (!TestNotNull(TEXT("attacker spawned"), Attacker) || !TestNotNull(TEXT("target spawned"), Target))
	{
		return false;
	}
	URPGMeleeTraceComponent* Melee = Attacker->GetMeleeTrace();
	URPGAttributeComponent* TargetAttr = Target->GetAttributes();
	const FVector From(0.f, 0.f, 100.f);
	const FVector To(400.f, 0.f, 100.f);

	Melee->BeginSwing(RPGTests::MakeHit(25.f, 5.f));
	TestEqual(TEXT("first sweep hits the target"), Melee->ProcessSweep(From, To, 20.f), 1);
	TestEqual(TEXT("damage applied once"), TargetAttr->GetHealth(), 75.f);
	TestEqual(TEXT("same swing never hits twice"), Melee->ProcessSweep(From, To, 20.f), 0);
	TestEqual(TEXT("health unchanged by the repeat"), TargetAttr->GetHealth(), 75.f);
	TestEqual(TEXT("one actor in the swing's hit list"), Melee->GetHitActors().Num(), 1);

	// A new swing may hit the same target again.
	Melee->EndSwing();
	Melee->BeginSwing(RPGTests::MakeHit(25.f, 5.f));
	TestEqual(TEXT("next swing hits again"), Melee->ProcessSweep(From, To, 20.f), 1);
	TestEqual(TEXT("second swing damage"), TargetAttr->GetHealth(), 50.f);

	// The attacker's own body never counts.
	Melee->EndSwing();
	Melee->BeginSwing(RPGTests::MakeHit(25.f, 5.f));
	TestEqual(TEXT("sweep around the owner hits nothing"), Melee->ProcessSweep(FVector(-100.f, 0.f, 100.f), FVector(100.f, 0.f, 100.f), 20.f), 0);

	// I-frames: the hit is spent without damage, and does not land after they end.
	Target->ResetCombatant();
	Melee->EndSwing();
	Melee->BeginSwing(RPGTests::MakeHit(25.f, 5.f));
	Target->GetCombat()->SetInvulnerable(true);
	TestEqual(TEXT("dodged hit still consumes the swing"), Melee->ProcessSweep(From, To, 20.f), 1);
	TestEqual(TEXT("no damage through i-frames"), TargetAttr->GetHealth(), 100.f);
	Target->GetCombat()->SetInvulnerable(false);
	TestEqual(TEXT("no second chance after i-frames end"), Melee->ProcessSweep(From, To, 20.f), 0);
	TestEqual(TEXT("still undamaged"), TargetAttr->GetHealth(), 100.f);

	// Dead targets are not hit.
	Melee->EndSwing();
	Target->GetCombat()->Die();
	Melee->BeginSwing(RPGTests::MakeHit(25.f, 5.f));
	Melee->ProcessSweep(From, To, 20.f);
	TestEqual(TEXT("dead target takes no damage"), TargetAttr->GetHealth(), 100.f);
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FRPGMeleeTeamTest, "OneBossFight.Combat.HitDetection.Teams",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::ClientContext | EAutomationTestFlags::ProductFilter)

bool FRPGMeleeTeamTest::RunTest(const FString& Parameters)
{
	RPGTests::FScopedTestWorld Scope;
	ARPGTrainingDummy* A = RPGTests::SpawnCombatant<ARPGTrainingDummy>(Scope.World, FVector(0.f, 0.f, 100.f));
	ARPGTrainingDummy* B = RPGTests::SpawnCombatant<ARPGTrainingDummy>(Scope.World, FVector(300.f, 0.f, 100.f));
	if (!TestNotNull(TEXT("A spawned"), A) || !TestNotNull(TEXT("B spawned"), B))
	{
		return false;
	}

	URPGMeleeTraceComponent* Melee = A->GetMeleeTrace();
	Melee->BeginSwing(RPGTests::MakeHit(25.f, 5.f));
	TestEqual(TEXT("same team is not hit"), Melee->ProcessSweep(FVector(0.f, 0.f, 100.f), FVector(400.f, 0.f, 100.f), 20.f), 0);
	TestEqual(TEXT("same team takes no damage"), B->GetAttributes()->GetHealth(), 100.f);

	B->GetCombat()->TeamId = 0;
	TestEqual(TEXT("other team is hit"), Melee->ProcessSweep(FVector(0.f, 0.f, 100.f), FVector(400.f, 0.f, 100.f), 20.f), 1);
	TestEqual(TEXT("other team takes damage"), B->GetAttributes()->GetHealth(), 75.f);
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FRPGMeleeFrameRateTest, "OneBossFight.Combat.HitDetection.FrameRateIndependent",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::ClientContext | EAutomationTestFlags::ProductFilter)

bool FRPGMeleeFrameRateTest::RunTest(const FString& Parameters)
{
	RPGTests::FScopedTestWorld Scope;
	ARPGPlayerCharacter* Attacker = RPGTests::SpawnCombatant<ARPGPlayerCharacter>(Scope.World, FVector(-2000.f, 0.f, 100.f));
	ARPGTrainingDummy* Target = RPGTests::SpawnCombatant<ARPGTrainingDummy>(Scope.World, FVector(300.f, 0.f, 100.f));
	if (!TestNotNull(TEXT("attacker spawned"), Attacker) || !TestNotNull(TEXT("target spawned"), Target))
	{
		return false;
	}
	URPGMeleeTraceComponent* Melee = Attacker->GetMeleeTrace();

	// One weapon point crosses the target from x=-200 to x=800. Whatever the number of frames it is
	// split into (1 frame = a 1000 cm jump, 480 = very high FPS), the target is hit exactly once.
	const FVector Start(-200.f, 0.f, 100.f);
	const FVector End(800.f, 0.f, 100.f);
	for (const int32 Frames : {1, 2, 8, 60, 120, 240, 480})
	{
		Target->ResetCombatant();
		Melee->EndSwing();
		Melee->BeginSwing(RPGTests::MakeHit(25.f, 5.f));

		int32 TotalHits = 0;
		FVector Previous = Start;
		for (int32 Frame = 1; Frame <= Frames; ++Frame)
		{
			const FVector Current = FMath::Lerp(Start, End, static_cast<float>(Frame) / Frames);
			TotalHits += Melee->ProcessSweep(Previous, Current, 20.f);
			Previous = Current;
		}

		TestEqual(*FString::Printf(TEXT("%d frames: one hit"), Frames), TotalHits, 1);
		TestEqual(*FString::Printf(TEXT("%d frames: damage once"), Frames), Target->GetAttributes()->GetHealth(), 75.f);
	}
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FRPGHitWindowTest, "OneBossFight.Combat.HitDetection.WindowArmsTrace",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::ClientContext | EAutomationTestFlags::ProductFilter)

bool FRPGHitWindowTest::RunTest(const FString& Parameters)
{
	RPGTests::FScopedTestWorld Scope;
	ARPGPlayerCharacter* Attacker = RPGTests::SpawnCombatant<ARPGPlayerCharacter>(Scope.World, FVector(0.f, 0.f, 100.f));
	if (!TestNotNull(TEXT("attacker spawned"), Attacker))
	{
		return false;
	}
	URPGCombatComponent* Combat = Attacker->GetCombat();
	URPGMeleeTraceComponent* Melee = Attacker->GetMeleeTrace();

	TestFalse(TEXT("trace idle at rest"), Melee->IsSwinging());
	Combat->RequestLightAttack();
	TestFalse(TEXT("trace idle before the window"), Melee->IsSwinging());
	Combat->TickCombat(0.3f);
	TestTrue(TEXT("trace armed in the hit window"), Melee->IsSwinging());
	Combat->TickCombat(0.25f);
	TestFalse(TEXT("trace disarmed after the window"), Melee->IsSwinging());

	// Interrupting an attack mid-window disarms the trace.
	Combat->EndCurrentAction();
	Combat->RequestLightAttack();
	Combat->TickCombat(0.3f);
	TestTrue(TEXT("armed again"), Melee->IsSwinging());
	Combat->Stagger();
	TestFalse(TEXT("stagger disarms the trace"), Melee->IsSwinging());
	return true;
}

// ---------------------------------------------------------------------------------------------
// Lock-on
// ---------------------------------------------------------------------------------------------

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FRPGLockOnSelectionTest, "OneBossFight.Combat.LockOn.Selection",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::ClientContext | EAutomationTestFlags::ProductFilter)

bool FRPGLockOnSelectionTest::RunTest(const FString& Parameters)
{
	const FVector Origin = FVector::ZeroVector;
	const FVector Forward(1.f, 0.f, 0.f);

	// The point closest to the view direction wins, even if another is nearer or behind.
	const TArray<FVector> Points = {FVector(1000.f, 100.f, 0.f), FVector(500.f, -500.f, 0.f), FVector(-200.f, 0.f, 0.f)};
	TestEqual(TEXT("best aligned"), URPGTargetLockComponent::ChooseByViewAlignment(Origin, Forward, Points), 0);
	TestEqual(TEXT("no points"), URPGTargetLockComponent::ChooseByViewAlignment(Origin, Forward, TArray<FVector>()), static_cast<int32>(INDEX_NONE));

	// Switching picks the nearest neighbor on the requested side.
	const FVector Current(1000.f, 0.f, 0.f);
	const TArray<FVector> Neighbors = {FVector(1000.f, -400.f, 0.f), FVector(1000.f, 400.f, 0.f), FVector(1000.f, 900.f, 0.f)};
	TestEqual(TEXT("switch right"), URPGTargetLockComponent::ChooseBySide(Origin, Current, Neighbors, 1.f), 1);
	TestEqual(TEXT("switch left"), URPGTargetLockComponent::ChooseBySide(Origin, Current, Neighbors, -1.f), 0);

	const TArray<FVector> OnlyLeft = {FVector(1000.f, -400.f, 0.f)};
	TestEqual(TEXT("nothing on the right"), URPGTargetLockComponent::ChooseBySide(Origin, Current, OnlyLeft, 1.f), static_cast<int32>(INDEX_NONE));
	TestEqual(TEXT("zero direction"), URPGTargetLockComponent::ChooseBySide(Origin, Current, Neighbors, 0.f), static_cast<int32>(INDEX_NONE));
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FRPGLockOnToggleTest, "OneBossFight.Combat.LockOn.Toggle",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::ClientContext | EAutomationTestFlags::ProductFilter)

bool FRPGLockOnToggleTest::RunTest(const FString& Parameters)
{
	RPGTests::FScopedTestWorld Scope;
	UWorld* World = Scope.World;
	ARPGPlayerCharacter* Player = RPGTests::SpawnCombatant<ARPGPlayerCharacter>(World, FVector(0.f, 0.f, 100.f));
	ARPGTrainingDummy* Dummy = RPGTests::SpawnCombatant<ARPGTrainingDummy>(World, FVector(800.f, 0.f, 100.f));
	if (!TestNotNull(TEXT("player spawned"), Player) || !TestNotNull(TEXT("dummy spawned"), Dummy))
	{
		return false;
	}
	URPGTargetLockComponent* Lock = Player->GetTargetLock();

	TestFalse(TEXT("not locked at start"), Lock->IsLocked());
	TestTrue(TEXT("lock acquires the dummy"), Lock->ToggleLock());
	TestTrue(TEXT("locked"), Lock->IsLocked());
	TestTrue(TEXT("target is the dummy"), Lock->GetTarget() == Dummy);
	TestTrue(TEXT("body strafes toward the target"), Player->GetCharacterMovement()->bUseControllerDesiredRotation);
	TestFalse(TEXT("body no longer follows movement"), Player->GetCharacterMovement()->bOrientRotationToMovement);

	TestFalse(TEXT("toggle releases"), Lock->ToggleLock());
	TestFalse(TEXT("released"), Lock->IsLocked());
	TestTrue(TEXT("movement orientation restored"), Player->GetCharacterMovement()->bOrientRotationToMovement);

	// A dead target cannot be locked; an out-of-range one neither.
	Dummy->GetCombat()->Die();
	TestFalse(TEXT("dead target not lockable"), Lock->ToggleLock());
	Dummy->ResetCombatant();
	Dummy->SetActorLocation(FVector(9000.f, 0.f, 100.f));
	TestFalse(TEXT("far target not lockable"), Lock->ToggleLock());
	Dummy->SetActorLocation(FVector(800.f, 0.f, 100.f));
	TestTrue(TEXT("lockable again in range"), Lock->ToggleLock());

	// Same team is never a target.
	Lock->ClearTarget();
	Dummy->GetCombat()->TeamId = 0;
	TestFalse(TEXT("ally not lockable"), Lock->ToggleLock());
	return true;
}

#endif // WITH_DEV_AUTOMATION_TESTS
