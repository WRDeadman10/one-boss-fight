// Copyright One Boss Fight. All Rights Reserved.

#include "Misc/AutomationTest.h"

#if WITH_DEV_AUTOMATION_TESTS

#include "Player/RPGAttackKind.h"
#include "Player/RPGBleedRules.h"
#include "Player/RPGBossMath.h"
#include "Player/RPGBossRules.h"
#include "Player/RPGBuildRules.h"
#include "Player/RPGSwingRules.h"

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FRPGCodexAttackKindEdgesTest, "OneBossFight.Codex.AttackKindEdges",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::ClientContext | EAutomationTestFlags::ProductFilter)

bool FRPGCodexAttackKindEdgesTest::RunTest(const FString& Parameters)
{
	// Invariant: attack-data prefixes are matched case-insensitively (FString::StartsWith) and stance only changes Default and Strong.
	TestEqual(TEXT("Default airborne is jump light"), static_cast<uint8>(RPGClassifyAttack(TEXT("DefaultMelee"), true)), static_cast<uint8>(ERPGAttackKind::JumpLight));
	TestEqual(TEXT("Strong airborne is jump heavy"), static_cast<uint8>(RPGClassifyAttack(TEXT("StrongAttack"), true)), static_cast<uint8>(ERPGAttackKind::JumpHeavy));
	TestEqual(TEXT("Charged ignores stance"), static_cast<uint8>(RPGClassifyAttack(TEXT("ChargedAttack"), true)), static_cast<uint8>(ERPGAttackKind::Charged));
	TestEqual(TEXT("Knockdown ignores stance"), static_cast<uint8>(RPGClassifyAttack(TEXT("MeleeKnockdown"), true)), static_cast<uint8>(ERPGAttackKind::Knockdown));
	TestEqual(TEXT("a lowercase prefix still matches (StartsWith ignores case)"), static_cast<uint8>(RPGClassifyAttack(TEXT("defaultMelee"), false)), static_cast<uint8>(ERPGAttackKind::Light));
	TestEqual(TEXT("an unrelated name is unknown"), static_cast<uint8>(RPGClassifyAttack(TEXT("OtherAttack"), false)), static_cast<uint8>(ERPGAttackKind::Unknown));
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FRPGCodexBossMathEdgesTest, "OneBossFight.Codex.BossMathEdges",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::ClientContext | EAutomationTestFlags::ProductFilter)

bool FRPGCodexBossMathEdgesTest::RunTest(const FString& Parameters)
{
	using namespace RPGBossMath;
	// Invariant: an unheld zero pool regenerates, while a held zero pool remains empty.
	TestEqual(TEXT("held zero remains zero"), RegenStep(0.f, 100.f, 10.0, 0.0, 6.f, 13.f, 1.f), 0.f);
	TestEqual(TEXT("unheld zero regenerates after delay"), RegenStep(0.f, 100.f, 6.0, 0.0, 6.f, 13.f, 1.f, true), 13.f);
	TestEqual(TEXT("delay boundary regenerates"), RegenStep(50.f, 100.f, 6.0, 0.0, 6.f, 13.f, 1.f), 63.f);
	TestEqual(TEXT("regen caps at maximum"), RegenStep(95.f, 100.f, 9.0, 0.0, 6.f, 13.f, 1.f), 100.f);

	const FVector Boss = FVector::ZeroVector;
	TestEqual(TEXT("range equality is accepted"), static_cast<uint8>(RiposteGeometry(Boss, FVector::ForwardVector, FVector(150.f, 0.f, 99.f), FVector(-1.f, 0.f, 0.f), 150.f, 120.f, 120.f)), static_cast<uint8>(ERiposteVerdict::Accept));
	TestEqual(TEXT("beyond range is refused first"), static_cast<uint8>(RiposteGeometry(Boss, FVector::ForwardVector, FVector(150.01f, 0.f, 0.f), FVector::ForwardVector, 150.f, 120.f, 120.f)), static_cast<uint8>(ERiposteVerdict::TooFar));
	TestTrue(TEXT("sweep angular tolerance includes edge contact"), SweepTouches(200.f, 42.f, 250.f, 50.f, 12.f, 0.f, 0.f));
	TestFalse(TEXT("sweep rejects a capsule outside reach"), SweepTouches(300.f, 42.f, 250.f, 50.f, 0.f, -90.f, 90.f));
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FRPGCodexBossRulesEdgesTest, "OneBossFight.Codex.BossRulesEdges",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::ClientContext | EAutomationTestFlags::ProductFilter)

bool FRPGCodexBossRulesEdgesTest::RunTest(const FString& Parameters)
{
	using namespace RPGBossRules;
	// Invariant: terminal states outrank all lower-priority break and transition states.
	FFlags Flags;
	Flags.bDead = true;
	Flags.bDormant = true;
	Flags.bTransition = true;
	TestEqual(TEXT("dead outranks every break state"), static_cast<uint8>(ResolveBreak(Flags, false)), static_cast<uint8>(EBreakResult::Dead));
	TestEqual(TEXT("dead health outranks dormant transition"), static_cast<uint8>(ResolveTransition(Flags, 0.0, 500.0, 0.6f)), static_cast<uint8>(ETransitionResult::Dead));

	Flags = FFlags{};
	Flags.bCooldown = true;
	TestEqual(TEXT("cooldown rejects a normal break"), static_cast<uint8>(ResolveBreak(Flags, false)), static_cast<uint8>(EBreakResult::Cooldown));
	TestEqual(TEXT("ignore cooldown starts the break"), static_cast<uint8>(ResolveBreak(Flags, true)), static_cast<uint8>(EBreakResult::Started));
	Flags.bStaggered = true;
	TestEqual(TEXT("threshold equality queues behind a break"), static_cast<uint8>(ResolveTransition(Flags, 300.0, 500.0, 0.6f)), static_cast<uint8>(ETransitionResult::QueuedBehindStagger));
	Flags.bStaggered = false;
	TestEqual(TEXT("threshold equality starts when free"), static_cast<uint8>(ResolveTransition(Flags, 300.0, 500.0, 0.6f)), static_cast<uint8>(ETransitionResult::Start));
	TestEqual(TEXT("no maximum is not ready"), static_cast<uint8>(ResolveTransition(Flags, 1.0, 0.0, 0.6f)), static_cast<uint8>(ETransitionResult::NotReady));
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FRPGCodexBleedEdgesTest, "OneBossFight.Codex.BleedEdges",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::ClientContext | EAutomationTestFlags::ProductFilter)

bool FRPGCodexBleedEdgesTest::RunTest(const FString& Parameters)
{
	using namespace RPGBleedRules;
	// Invariant: zero buildup is ignored before actor-state gates, and a threshold proc resets exactly once.
	FState State;
	FConfig Config;
	TestEqual(TEXT("zero amount wins precedence"), static_cast<uint8>(Apply(State, Config, 0.f, true, true, true, true)), static_cast<uint8>(EResult::IgnoredAmount));
	TestEqual(TEXT("dead boss ignores positive buildup"), static_cast<uint8>(Apply(State, Config, 20.f, true, false, false, false)), static_cast<uint8>(EResult::IgnoredDead));
	State.Buildup = 80.f;
	TestEqual(TEXT("threshold equality procs"), static_cast<uint8>(Apply(State, Config, 20.f, false, false, false, false)), static_cast<uint8>(EResult::Proc));
	TestEqual(TEXT("proc clears buildup"), State.Buildup, 0.f);
	TestEqual(TEXT("proc raises threshold once"), State.Threshold, 120.f);
	TestEqual(TEXT("same-frame follow-up does not build"), static_cast<uint8>(Apply(State, Config, 20.f, false, false, false, true)), static_cast<uint8>(EResult::IgnoredSameFrame));
	TestEqual(TEXT("proc damage leaves the final health point"), ProcDamage(500.f, 20.f, Config), 19.f);
	TestEqual(TEXT("proc damage is zero at one health"), ProcDamage(500.f, 1.f, Config), 0.f);
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FRPGCodexSwingRulesEdgesTest, "OneBossFight.Codex.SwingRulesEdges",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::ClientContext | EAutomationTestFlags::ProductFilter)

bool FRPGCodexSwingRulesEdgesTest::RunTest(const FString& Parameters)
{
	using namespace RPGSwingRules;
	// Invariant: a valid hyperarmor interval includes both endpoints and never opens when inverted.
	TestTrue(TEXT("window includes its start"), WindowOpen(0.2f, 0.6f, 0.2f));
	TestTrue(TEXT("window includes its end"), WindowOpen(0.2f, 0.6f, 0.6f));
	TestFalse(TEXT("inverted window is closed"), WindowOpen(0.6f, 0.2f, 0.4f));
	TestFalse(TEXT("negative start is closed"), WindowOpen(-1.f, 0.6f, 0.f));
	TestEqual(TEXT("negative wanted cost keeps pack cost"), StaminaExtra(-1.f, 15.f, 100.0), 0.f);
	TestEqual(TEXT("extra cost clamps to available stamina"), StaminaExtra(35.f, 15.f, 4.0), 4.f);
	TestEqual(TEXT("cheaper desired cost refunds the difference"), StaminaExtra(10.f, 15.f, 100.0), -5.f);
	TestFalse(TEXT("refresh is false before boundary"), NeedsRefresh(2.99, 0.0, 3.f));
	TestTrue(TEXT("refresh is true at boundary"), NeedsRefresh(3.0, 0.0, 3.f));
	TestFalse(TEXT("zero refresh interval is disabled"), NeedsRefresh(99.0, 0.0, 0.f));
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FRPGCodexBuildRulesEdgesTest, "OneBossFight.Codex.BuildRulesEdges",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::ClientContext | EAutomationTestFlags::ProductFilter)

bool FRPGCodexBuildRulesEdgesTest::RunTest(const FString& Parameters)
{
	using namespace RPGBuildRules;
	// Invariant: malformed input never chooses a build, and retry boundaries never repeat a call early.
	ERPGBuild Build = ERPGBuild::Starter;
	TestEqual(TEXT("quoted whitespace alias parses"), static_cast<uint8>(Parse(TEXT("  \"dexterity\"  "), Build)), static_cast<uint8>(EParse::Build));
	TestEqual(TEXT("alias resolves to dex"), static_cast<uint8>(Build), static_cast<uint8>(ERPGBuild::Dex));
	TestEqual(TEXT("unknown build is invalid"), static_cast<uint8>(Parse(TEXT("great axe"), Build)), static_cast<uint8>(EParse::Invalid));
	TestEqual(TEXT("high enum clamps to dex"), FString(BuildName(static_cast<ERPGBuild>(99))), FString(TEXT("Dex")));

	FDecideInput In;
	In.bExplicit = true;
	In.bStyleKnown = true;
	In.VerifySeconds = 4.f;
	In.Attempts = 1;
	In.SecondsSinceAttempt = 3.99f;
	TestTrue(TEXT("just-before boundary verifies"), IsVerifying(In));
	In.SecondsSinceAttempt = 4.f;
	TestFalse(TEXT("verification ends at boundary"), IsVerifying(In));
	TestEqual(TEXT("free sleeping state applies"), static_cast<uint8>(Decide(In)), static_cast<uint8>(EDecision::Apply));
	In.bBossAwake = true;
	TestEqual(TEXT("awake boss defers"), static_cast<uint8>(Decide(In)), static_cast<uint8>(EDecision::Defer));
	TestEqual(TEXT("update sequence wraps to first"), UpdateTypeForAttempt(4), 0);
	TestTrue(TEXT("lock needs enabled, present, awake boss"), ShouldLockSlot(true, true, false));
	TestFalse(TEXT("dormant boss does not lock"), ShouldLockSlot(true, true, true));
	TestEqual(TEXT("off-build HUD says what is held"), BuildLine(TEXT("MagicCombatStyle"), EDecision::Done), FString(TEXT("Build: Off-build (Magic)")));
	return true;
}

#endif
