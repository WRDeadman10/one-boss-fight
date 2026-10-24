// Copyright One Boss Fight. All Rights Reserved.

#include "Misc/AutomationTest.h"

#if WITH_DEV_AUTOMATION_TESTS

#include "Player/RPGAttackKind.h"
#include "Player/RPGBleedRules.h"
#include "Player/RPGBossMath.h"
#include "Player/RPGBossRules.h"
#include "Player/RPGBuildRules.h"
#include "Player/RPGDamageScale.h"
#include "Player/RPGSwingRules.h"
#include "Player/RPGTelegraphRules.h"
#include "UI/RPGBuildSelectRules.h"

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
	TestEqual(TEXT("proc damage leaves the final health point"), ProcDamage(500.f, 10.f, Config), 9.f);
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

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FRPGCodexBuildSelectRulesTest, "OneBossFight.Codex.BuildSelectRules",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::ClientContext | EAutomationTestFlags::ProductFilter)

bool FRPGCodexBuildSelectRulesTest::RunTest(const FString& Parameters)
{
	using namespace RPGBuildSelectRules;
	for (int32 Bits = 0; Bits < 16; ++Bits)
	{
		const bool bDormant = (Bits & 1) != 0;
		const bool bAlive = (Bits & 2) != 0;
		const bool bGrounded = (Bits & 4) != 0;
		const bool bTransition = (Bits & 8) != 0;
		TestEqual(*FString::Printf(TEXT("CanOpen truth-table row %d"), Bits), CanOpen(bDormant, bAlive, bGrounded, bTransition), bDormant && bAlive && bGrounded && !bTransition);
	}

	for (int32 Row = 0; Row < 3; ++Row)
	{
		ERPGBuild Build = ERPGBuild::Starter;
		TestTrue(*FString::Printf(TEXT("row %d selects a build"), Row), BuildForRow(Row, Build));
		TestEqual(*FString::Printf(TEXT("row %d selects the expected build"), Row), static_cast<uint8>(Build), static_cast<uint8>(static_cast<ERPGBuild>(Row)));
		TestFalse(*FString::Printf(TEXT("row %d text is not empty"), Row), RowText(Row).IsEmpty());
	}
	for (const int32 Row : {-1, 3})
	{
		ERPGBuild Build = ERPGBuild::Starter;
		TestFalse(*FString::Printf(TEXT("row %d is rejected"), Row), BuildForRow(Row, Build));
		TestTrue(*FString::Printf(TEXT("row %d text is empty"), Row), RowText(Row).IsEmpty());
	}

	const TCHAR* Names[] = {TEXT("starter"), TEXT("STRENGTH"), TEXT("dEx")};
	const ERPGBuild ExpectedBuilds[] = {ERPGBuild::Starter, ERPGBuild::Strength, ERPGBuild::Dex};
	for (int32 Index = 0; Index < UE_ARRAY_COUNT(Names); ++Index)
	{
		ERPGBuild Build = ERPGBuild::Starter;
		TestTrue(*FString::Printf(TEXT("%s parses regardless of case"), Names[Index]), ParseBuild(FName(Names[Index]), Build));
		TestEqual(*FString::Printf(TEXT("%s selects the expected build"), Names[Index]), static_cast<uint8>(Build), static_cast<uint8>(ExpectedBuilds[Index]));
	}
	ERPGBuild Build = ERPGBuild::Starter;
	TestFalse(TEXT("garbage build name is rejected"), ParseBuild(FName(TEXT("mace")), Build));
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FRPGCodexDamageScalerTest, "OneBossFight.Codex.DamageScaler",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::ClientContext | EAutomationTestFlags::ProductFilter)

bool FRPGCodexDamageScalerTest::RunTest(const FString& Parameters)
{
	FRPGDamageScaler LossFirst;
	TestEqual(TEXT("loss first waits for its hit"), LossFirst.OnLoss(1.0, 40.0), 0.0);
	TestEqual(TEXT("loss first returns the expected adjustment"), LossFirst.OnHit(1.0, 0.5f), 20.0);

	FRPGDamageScaler HitFirst;
	TestEqual(TEXT("hit first waits for its loss"), HitFirst.OnHit(1.0, 0.5f), 0.0);
	TestEqual(TEXT("hit first returns the same adjustment"), HitFirst.OnLoss(1.0, 40.0), 20.0);

	FRPGDamageScaler Unscaled;
	Unscaled.OnLoss(2.0, 30.0);
	TestEqual(TEXT("multiplier one claims without adjusting"), Unscaled.OnHit(2.0, 1.0f), 0.0);
	TestEqual(TEXT("a claimed unscaled loss cannot be reused"), Unscaled.OnHit(2.0, 0.5f), 0.0);

	FRPGDamageScaler SymmetricAfter;
	SymmetricAfter.OnLoss(3.0, 20.0);
	TestEqual(TEXT("hit just after loss is in the symmetric window"), SymmetricAfter.OnHit(3.0 + FRPGDamageScaler::Window - 0.01, 0.5f), 10.0);
	FRPGDamageScaler SymmetricBefore;
	SymmetricBefore.OnHit(4.0, 0.5f);
	TestEqual(TEXT("hit just before loss is in the symmetric window"), SymmetricBefore.OnLoss(4.0 + FRPGDamageScaler::Window - 0.01, 20.0), 10.0);

	FRPGDamageScaler Expired;
	Expired.OnLoss(5.0, 20.0);
	TestEqual(TEXT("expired loss does not match a later hit"), Expired.OnHit(5.0 + FRPGDamageScaler::Window + 0.01, 0.5f), 0.0);
	TestEqual(TEXT("expired loss was pruned"), Expired.Losses.Num(), 0);

	TestEqual(TEXT("adjustment cannot exceed max health"), FRPGDamageScaler::Apply(90.0, 20.0, 100.0), 100.0);
	TestEqual(TEXT("adjustment cannot reduce a living boss below one"), FRPGDamageScaler::Apply(5.0, -20.0, 100.0), 1.0);
	TestEqual(TEXT("adjustment does not revive a dead boss"), FRPGDamageScaler::Apply(0.0, 20.0, 100.0), 0.0);
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FRPGCodexTelegraphRulesTest, "OneBossFight.Codex.TelegraphRules",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::ClientContext | EAutomationTestFlags::ProductFilter)

bool FRPGCodexTelegraphRulesTest::RunTest(const FString& Parameters)
{
	using namespace RPGTelegraphRules;
	TestEqual(TEXT("zero target leaves the rate unchanged"), RateFor(0.17f, 0.f), 1.f);
	TestEqual(TEXT("target at active start leaves the rate unchanged"), RateFor(0.17f, 0.17f), 1.f);
	TestEqual(TEXT("target before active start leaves the rate unchanged"), RateFor(0.17f, 0.10f), 1.f);
	TestEqual(TEXT("zero active start leaves the rate unchanged"), RateFor(0.f, 0.40f), 1.f);
	TestTrue(TEXT("A3a reaches the requested 0.425 rate"), FMath::IsNearlyEqual(RateFor(0.17f, 0.40f), 0.425f));
	TestEqual(TEXT("the rate clamps to one tenth"), RateFor(0.02f, 0.50f), 0.1f);
	TestEqual(TEXT("A1 seen at 0.04 s still gets about its 0.35 s tell"), RateFor(0.12f, 0.35f, 0.04f), 0.08f / 0.31f, 0.0001f);
	TestEqual(TEXT("A1 seen 0.10 s late is clamped, not stopped"), RateFor(0.12f, 0.35f, 0.10f), 0.1f);
	TestTrue(TEXT("the rate never exceeds one"), RateFor(0.17f, 0.10f) <= 1.f);

	TestEqual(TEXT("zero cvar disables A3a"), TargetFor(TEXT("A3a"), 0.f), 0.f);
	TestEqual(TEXT("A1 caps at its Freeze target"), TargetFor(TEXT("A1"), 0.40f), 0.35f);
	TestEqual(TEXT("A1b caps at its Freeze target"), TargetFor(TEXT("A1b"), 0.40f), 0.35f);
	TestEqual(TEXT("A3a keeps the cvar target"), TargetFor(TEXT("A3a"), 0.40f), 0.40f);
	TestEqual(TEXT("A3b keeps the cvar target"), TargetFor(TEXT("A3b"), 0.40f), 0.40f);
	for (const FName MoveId : {FName(TEXT("A2")), FName(TEXT("A4")), FName(TEXT("Unknown"))})
	{
		TestEqual(*FString::Printf(TEXT("%s is not a close telegraph move"), *MoveId.ToString()), TargetFor(MoveId, 0.40f), 0.f);
	}
	// The rate is worked out from where the montage is when it is applied (the tracker sees a stage a frame or two late): the rest of the windup, 0.17 - 0.05, must take 0.40 - 0.05 real seconds.
	TestEqual(TEXT("a late start works out the rest of the windup"), RateFor(0.17f, 0.40f, 0.05f), 0.12f / 0.35f, 0.0001f);
	TestEqual(TEXT("position 0 is the plain ratio"), RateFor(0.17f, 0.40f, 0.f), 0.425f, 0.0001f);
	TestEqual(TEXT("a montage already past the active start is not stretched"), RateFor(0.17f, 0.40f, 0.17f), 1.f);
	TestEqual(TEXT("a montage already past the target is not stretched"), RateFor(0.17f, 0.10f, 0.12f), 1.f);
	TestEqual(TEXT("a negative position is refused"), RateFor(0.17f, 0.40f, -0.1f), 1.f);
	return true;
}

#endif
