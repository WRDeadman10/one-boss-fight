// Copyright One Boss Fight. All Rights Reserved.

#include "Misc/AutomationTest.h"
#include "Misc/PackageName.h"

#if WITH_DEV_AUTOMATION_TESTS

#include "Player/RPGBuildLoadout.h"
#include "Player/RPGBuildRules.h"
#include "Player/RPGWeaponAttackTable.h"

// ---------------------------------------------------------------------------------------------
// Builds (Gate 3, M13): names, the style of each build, the console text, the weapon slot lock, the HUD line and the table rows of the three builds
// ---------------------------------------------------------------------------------------------

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FRPGBuildRulesTest, "OneBossFight.Build.Rules",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::ClientContext | EAutomationTestFlags::ProductFilter)

bool FRPGBuildRulesTest::RunTest(const FString& Parameters)
{
	using namespace RPGBuildRules;
	const ERPGBuild All[] = {ERPGBuild::Starter, ERPGBuild::Strength, ERPGBuild::Dex};

	// The table of builds: one row per build in the order of the enum, with the names the drivers and the console read.
	TestEqual(TEXT("three builds"), BuildCount, 3);
	for (int32 Index = 0; Index < BuildCount; ++Index)
	{
		TestTrue(*FString::Printf(TEXT("row %d is the build with that enumerator"), Index), RPGBuildRules::Entry(static_cast<ERPGBuild>(Index)).Build == static_cast<ERPGBuild>(Index));
	}
	TestEqual(TEXT("name of Starter"), FString(BuildName(ERPGBuild::Starter)), FString(TEXT("Starter")));
	TestEqual(TEXT("name of Strength"), FString(BuildName(ERPGBuild::Strength)), FString(TEXT("Strength")));
	TestEqual(TEXT("name of Dex"), FString(BuildName(ERPGBuild::Dex)), FString(TEXT("Dex")));

	// Which pack combat style (the key of the weapon attack table) belongs to which build: Strength is the claymore, Dex the dual swords, Starter the pack's sword.
	TestEqual(TEXT("Starter is the sword"), FString(StyleOfBuild(ERPGBuild::Starter)), FString(TEXT("SwordCombatStyle")));
	TestEqual(TEXT("Strength is the claymore"), FString(StyleOfBuild(ERPGBuild::Strength)), FString(TEXT("ClaymoreCombatStyle")));
	TestEqual(TEXT("Dex is the dual swords"), FString(StyleOfBuild(ERPGBuild::Dex)), FString(TEXT("DualSwordCombatStyle")));
	TestEqual(TEXT("Starter weapon actor"), FString(RPGBuildRules::Entry(ERPGBuild::Starter).ActorClass), FString(TEXT("BP_ToughSword_C")));
	TestEqual(TEXT("Strength weapon actor"), FString(RPGBuildRules::Entry(ERPGBuild::Strength).ActorClass), FString(TEXT("BP_KwangSword_C")));
	TestEqual(TEXT("Dex weapon actor"), FString(RPGBuildRules::Entry(ERPGBuild::Dex).ActorClass), FString(TEXT("BP_DualSteelSwords_C")));
	TestEqual(TEXT("Starter weapon ability"), FString(RPGBuildRules::Entry(ERPGBuild::Starter).AbilityClass), FString(TEXT("GA_Sword_Melee_C")));
	TestEqual(TEXT("Strength weapon ability"), FString(RPGBuildRules::Entry(ERPGBuild::Strength).AbilityClass), FString(TEXT("GA_Claymore_Melee_C")));
	TestEqual(TEXT("Dex weapon ability (the pack's spelling)"), FString(RPGBuildRules::Entry(ERPGBuild::Dex).AbilityClass), FString(TEXT("GA_DuaSword_Melee_C")));
	TestEqual(TEXT("the weapon slot is enumerator 11"), WeaponSlotEnumerator, 11);

	struct FStyleCase
	{
		const TCHAR* Style;
		bool bBuild;
		ERPGBuild Build;
	};
	const FStyleCase StyleCases[] =
	{
		{TEXT("SwordCombatStyle"), true, ERPGBuild::Starter},
		{TEXT("SwordAndShieldCombatStyle"), true, ERPGBuild::Starter}, // the merge of the sword with a shield counts as the starter
		{TEXT("ClaymoreCombatStyle"), true, ERPGBuild::Strength},
		{TEXT("DualSwordCombatStyle"), true, ERPGBuild::Dex},
		{TEXT("TwinbladeCombatStyle"), true, ERPGBuild::Dex}, // the spare dex weapon
		{TEXT("PolearmCombatStyle"), false, ERPGBuild::Starter},
		{TEXT("UnarmedCombatStyle"), false, ERPGBuild::Starter},
		{TEXT("MagicCombatStyle"), false, ERPGBuild::Starter},
		{TEXT("Banana"), false, ERPGBuild::Starter},
		{TEXT(""), false, ERPGBuild::Starter},
	};
	for (const FStyleCase& Case : StyleCases)
	{
		ERPGBuild Found = ERPGBuild::Starter;
		const bool bFound = BuildOfStyle(FName(Case.Style), Found);
		TestTrue(*FString::Printf(TEXT("style '%s' belongs to a build: %s"), Case.Style, Case.bBuild ? TEXT("yes") : TEXT("no")), bFound == Case.bBuild);
		if (Case.bBuild)
		{
			TestTrue(*FString::Printf(TEXT("style '%s' is the build %s"), Case.Style, BuildName(Case.Build)), bFound && Found == Case.Build);
		}
		for (ERPGBuild Build : All)
		{
			TestTrue(*FString::Printf(TEXT("style '%s' matches build %s only for its own build"), Case.Style, BuildName(Build)), StyleMatchesBuild(FName(Case.Style), Build) == (Case.bBuild && Case.Build == Build));
		}
	}
	for (ERPGBuild Build : All)
	{
		ERPGBuild Back = ERPGBuild::Starter;
		TestTrue(*FString::Printf(TEXT("the style of %s maps back to it"), BuildName(Build)), BuildOfStyle(FName(StyleOfBuild(Build)), Back) && Back == Build);
		TestTrue(*FString::Printf(TEXT("the item of %s is a pack weapon item"), BuildName(Build)), FString(RPGBuildRules::Entry(Build).ItemPath).StartsWith(TEXT("/Game/AdvancedARPGCombat/MeleeCombatSystem/Blueprints/Items/Weapons/")));
	}

	// The console text: any case, quotes and spaces ignored; empty, none and off mean no choice; anything else is invalid.
	struct FParseCase
	{
		const TCHAR* Text;
		EParse Result;
		ERPGBuild Build;
	};
	const FParseCase ParseCases[] =
	{
		{TEXT("Strength"), EParse::Build, ERPGBuild::Strength},
		{TEXT("strength"), EParse::Build, ERPGBuild::Strength},
		{TEXT("STR"), EParse::Build, ERPGBuild::Strength},
		{TEXT("Dex"), EParse::Build, ERPGBuild::Dex},
		{TEXT("dexterity"), EParse::Build, ERPGBuild::Dex},
		{TEXT("Starter"), EParse::Build, ERPGBuild::Starter},
		{TEXT("sword"), EParse::Build, ERPGBuild::Starter},
		{TEXT("  Dex  "), EParse::Build, ERPGBuild::Dex},
		{TEXT("\"Strength\""), EParse::Build, ERPGBuild::Strength},
		{TEXT(""), EParse::Empty, ERPGBuild::Starter},
		{TEXT("\"\""), EParse::Empty, ERPGBuild::Starter},
		{TEXT("   "), EParse::Empty, ERPGBuild::Starter},
		{TEXT("none"), EParse::Empty, ERPGBuild::Starter},
		{TEXT("Off"), EParse::Empty, ERPGBuild::Starter},
		{TEXT("banana"), EParse::Invalid, ERPGBuild::Starter},
		{TEXT("strengthdex"), EParse::Invalid, ERPGBuild::Starter},
		{TEXT("claymore"), EParse::Invalid, ERPGBuild::Starter},
		{TEXT("1"), EParse::Invalid, ERPGBuild::Starter},
	};
	for (const FParseCase& Case : ParseCases)
	{
		ERPGBuild Parsed = ERPGBuild::Starter;
		const EParse Result = RPGBuildRules::Parse(FString(Case.Text), Parsed);
		TestEqual(*FString::Printf(TEXT("parse of '%s'"), Case.Text), static_cast<int32>(Result), static_cast<int32>(Case.Result));
		if (Case.Result == EParse::Build)
		{
			TestTrue(*FString::Printf(TEXT("'%s' is the build %s"), Case.Text, BuildName(Case.Build)), Parsed == Case.Build);
		}
	}
	for (ERPGBuild Build : All)
	{
		ERPGBuild Parsed = ERPGBuild::Starter;
		TestTrue(*FString::Printf(TEXT("the name of %s parses back to it"), BuildName(Build)), RPGBuildRules::Parse(FString(BuildName(Build)), Parsed) == EParse::Build && Parsed == Build);
	}

	// The enumerator byte of the pack's equip call: 0 first (the owner's decision), then 1, then 0 again; never an out-of-range index and never the Unequip entry (3).
	TestEqual(TEXT("first call uses update type 0"), UpdateTypeForAttempt(1), 0);
	TestEqual(TEXT("second call uses update type 1"), UpdateTypeForAttempt(2), 1);
	TestEqual(TEXT("third call uses update type 0"), UpdateTypeForAttempt(3), 0);
	TestEqual(TEXT("fifth call uses update type 1 again"), UpdateTypeForAttempt(5), 1);
	TestEqual(TEXT("attempt 0 is clamped to the first"), UpdateTypeForAttempt(0), 0);
	TestEqual(TEXT("a negative attempt is clamped to the first"), UpdateTypeForAttempt(-4), 0);
	for (int32 Attempt = -2; Attempt < 30; ++Attempt)
	{
		const int32 Type = UpdateTypeForAttempt(Attempt);
		TestTrue(*FString::Printf(TEXT("update type of call %d is 0 or 1"), Attempt), Type == 0 || Type == 1);
	}

	// Q2: the weapon slot is locked while the boss is awake (present and not dormant), only when the lock is on.
	for (int32 Bits = 0; Bits < 8; ++Bits)
	{
		const bool bEnabled = (Bits & 1) != 0;
		const bool bPresent = (Bits & 2) != 0;
		const bool bDormant = (Bits & 4) != 0;
		TestTrue(*FString::Printf(TEXT("lock for enabled %d present %d dormant %d"), bEnabled ? 1 : 0, bPresent ? 1 : 0, bDormant ? 1 : 0), ShouldLockSlot(bEnabled, bPresent, bDormant) == (bEnabled && bPresent && !bDormant));
	}

	// The names of the decisions are stable (the log lines and the drivers read them).
	TestEqual(TEXT("name of Wait"), FString(DecisionName(EDecision::Wait)), FString(TEXT("Wait")));
	TestEqual(TEXT("name of Apply"), FString(DecisionName(EDecision::Apply)), FString(TEXT("Apply")));
	TestEqual(TEXT("name of Done"), FString(DecisionName(EDecision::Done)), FString(TEXT("Done")));
	TestEqual(TEXT("name of Defer"), FString(DecisionName(EDecision::Defer)), FString(TEXT("Defer")));
	TestEqual(TEXT("name of GiveUp"), FString(DecisionName(EDecision::GiveUp)), FString(TEXT("GiveUp")));

	// The HUD line (the truth rule): it names the weapon really held, with the suffix of what the loadout is doing about it.
	struct FLineCase
	{
		const TCHAR* Style;
		const TCHAR* Line;
	};
	const FLineCase LineCases[] =
	{
		{TEXT("SwordCombatStyle"), TEXT("Build: Starter (Sword)")},
		{TEXT("SwordAndShieldCombatStyle"), TEXT("Build: Starter (Sword and Shield)")},
		{TEXT("ClaymoreCombatStyle"), TEXT("Build: Strength (Claymore)")},
		{TEXT("DualSwordCombatStyle"), TEXT("Build: Dex (Dual Swords)")},
		{TEXT("TwinbladeCombatStyle"), TEXT("Build: Dex (Twinblades)")},
		{TEXT("PolearmCombatStyle"), TEXT("Build: Off-build (Polearm)")},
		{TEXT("MagicCombatStyle"), TEXT("Build: Off-build (Magic)")},
		{TEXT("None"), TEXT("Build: Unknown")},
	};
	for (const FLineCase& Case : LineCases)
	{
		TestEqual(*FString::Printf(TEXT("line of %s"), Case.Style), BuildLine(FName(Case.Style), EDecision::Done), FString(Case.Line));
		TestEqual(*FString::Printf(TEXT("line of %s while waiting"), Case.Style), BuildLine(FName(Case.Style), EDecision::Wait), FString(Case.Line) + TEXT(" - equipping..."));
		TestEqual(*FString::Printf(TEXT("line of %s while applying"), Case.Style), BuildLine(FName(Case.Style), EDecision::Apply), FString(Case.Line) + TEXT(" - equipping..."));
		TestEqual(*FString::Printf(TEXT("line of %s while deferred"), Case.Style), BuildLine(FName(Case.Style), EDecision::Defer), FString(Case.Line) + TEXT(" - next fight"));
		TestEqual(*FString::Printf(TEXT("line of %s after giving up"), Case.Style), BuildLine(FName(Case.Style), EDecision::GiveUp), FString(Case.Line) + TEXT(" - not equipped"));
	}
	// The line never names a build the player does not hold: an off-build weapon says none of the three build words, a build weapon says only its own.
	for (const FLineCase& Case : LineCases)
	{
		const FString Line = BuildLine(FName(Case.Style), EDecision::Done);
		ERPGBuild Held = ERPGBuild::Starter;
		const bool bBuildWeapon = BuildOfStyle(FName(Case.Style), Held);
		for (ERPGBuild Build : All)
		{
			const FString Word = FString::Printf(TEXT("Build: %s "), BuildName(Build));
			TestTrue(*FString::Printf(TEXT("line of %s names the build %s only when it is held"), Case.Style, BuildName(Build)), Line.StartsWith(Word) == (bBuildWeapon && Held == Build));
		}
	}

	// The three builds have a table row for every kind of attack (no Fallback is reachable), with the Freeze values (5, 20.1, 20.2): the builds differ only by the weapon the player holds.
	const URPGWeaponAttackTable* Table = GetDefault<URPGWeaponAttackTable>();
	struct FRowCase
	{
		ERPGBuild Build;
		ERPGAttackKind Kind;
		float Posture;
		float Stamina;
		float Bleed;
	};
	const FRowCase RowCases[] =
	{
		{ERPGBuild::Strength, ERPGAttackKind::Light, 18.f, -1.f, 0.f},
		{ERPGBuild::Strength, ERPGAttackKind::Strong, 30.f, 35.f, 0.f},
		{ERPGBuild::Strength, ERPGAttackKind::Charged, 38.f, 35.f, 0.f},
		{ERPGBuild::Strength, ERPGAttackKind::JumpLight, 18.f, -1.f, 0.f},
		{ERPGBuild::Strength, ERPGAttackKind::JumpHeavy, 38.f, 35.f, 0.f},
		{ERPGBuild::Strength, ERPGAttackKind::Knockdown, 38.f, 35.f, 0.f},
		{ERPGBuild::Dex, ERPGAttackKind::Light, 6.f, 10.f, 20.f},
		{ERPGBuild::Dex, ERPGAttackKind::Strong, 10.f, 10.f, 20.f},
		{ERPGBuild::Dex, ERPGAttackKind::Charged, 14.f, 10.f, 20.f},
		{ERPGBuild::Dex, ERPGAttackKind::JumpLight, 6.f, 10.f, 20.f},
		{ERPGBuild::Dex, ERPGAttackKind::JumpHeavy, 14.f, 10.f, 20.f},
		{ERPGBuild::Dex, ERPGAttackKind::Knockdown, 14.f, 10.f, 20.f},
		{ERPGBuild::Starter, ERPGAttackKind::Light, 18.f, -1.f, 0.f},
		{ERPGBuild::Starter, ERPGAttackKind::Strong, 30.f, -1.f, 0.f},
		{ERPGBuild::Starter, ERPGAttackKind::Charged, 38.f, -1.f, 0.f},
		{ERPGBuild::Starter, ERPGAttackKind::JumpLight, 18.f, -1.f, 0.f},
		{ERPGBuild::Starter, ERPGAttackKind::JumpHeavy, 38.f, -1.f, 0.f},
		{ERPGBuild::Starter, ERPGAttackKind::Knockdown, 38.f, -1.f, 0.f},
	};
	for (const FRowCase& Case : RowCases)
	{
		FRPGWeaponAttackRow Row;
		const FString What = FString::Printf(TEXT("%s %s"), BuildName(Case.Build), RPGAttackKindName(Case.Kind));
		TestTrue(*(What + TEXT(" has a row (no fallback)")), Table->Find(FName(StyleOfBuild(Case.Build)), Case.Kind, Row));
		TestEqual(*(What + TEXT(" posture")), Row.PostureDamage, Case.Posture);
		TestEqual(*(What + TEXT(" stamina (-1 keeps the pack's cost)")), Row.StaminaCost, Case.Stamina);
		TestEqual(*(What + TEXT(" bleed")), Row.BleedBuildup, Case.Bleed);
	}
	return true;
}

// ---------------------------------------------------------------------------------------------
// The apply state machine of the loadout: every combination of what it knows, against the invariants of the plan (M13_BUILDS_PLAN.md 2.3 and 5.4)
// ---------------------------------------------------------------------------------------------

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FRPGBuildDecideTest, "OneBossFight.Build.Decide",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::ClientContext | EAutomationTestFlags::ProductFilter)

bool FRPGBuildDecideTest::RunTest(const FString& Parameters)
{
	using namespace RPGBuildRules;
	int32 Combinations = 0;
	int32 Violations = 0;
	FString FirstViolation;
	auto Flag = [](bool bValue) { return bValue ? 1 : 0; };
	auto Violate = [&](const TCHAR* Rule, const FDecideInput& In, EDecision Decision)
	{
		if (Violations++ == 0)
		{
			FirstViolation = FString::Printf(TEXT("%s: decision %s for explicit %d known %d matches %d awake %d dead %d busy %d combat %d blocks %d attempts %d since %.1f"), Rule, DecisionName(Decision), Flag(In.bExplicit), Flag(In.bStyleKnown),
				Flag(In.bStyleMatches), Flag(In.bBossAwake), Flag(In.bPlayerDead), Flag(In.bPlayerBusy), Flag(In.bPlayerInCombat), Flag(In.bCombatBlocksApply), In.Attempts, In.SecondsSinceAttempt);
		}
	};

	const int32 AttemptValues[] = {0, 1, 2, 3, 4};
	const float SinceValues[] = {-1.f, 0.f, 3.9f, 4.f, 10.f};
	for (int32 Bits = 0; Bits < 256; ++Bits)
	{
		for (const int32 Attempts : AttemptValues)
		{
			for (const float Since : SinceValues)
			{
				FDecideInput In;
				In.bExplicit = (Bits & 1) != 0;
				In.bStyleKnown = (Bits & 2) != 0;
				In.bStyleMatches = (Bits & 4) != 0;
				In.bBossAwake = (Bits & 8) != 0;
				In.bPlayerDead = (Bits & 16) != 0;
				In.bPlayerBusy = (Bits & 32) != 0;
				In.bPlayerInCombat = (Bits & 64) != 0;
				In.bCombatBlocksApply = (Bits & 128) != 0;
				In.Attempts = Attempts;
				In.MaxAttempts = 3;
				In.SecondsSinceAttempt = Since;
				In.VerifySeconds = 4.f;
				const EDecision Decision = RPGBuildRules::Decide(In);
				++Combinations;

				const bool bBlockedByCombat = In.bCombatBlocksApply && In.bPlayerInCombat;
				const bool bVerifying = Attempts > 0 && Since >= 0.f && Since < 4.f;
				if (IsVerifying(In) != bVerifying)
				{
					Violate(TEXT("IsVerifying disagrees with the written rule"), In, Decision);
				}
				// A call (Apply) only when everything allows it.
				if (Decision == EDecision::Apply && (!In.bExplicit || In.bStyleMatches || !In.bStyleKnown || In.bPlayerDead || In.bBossAwake || In.bPlayerBusy || bBlockedByCombat || bVerifying || Attempts >= 3))
				{
					Violate(TEXT("an Apply that a rule forbids"), In, Decision);
				}
				// No choice, or the build's weapon already held: nothing to do, whatever else is going on (a default run calls nothing).
				if ((!In.bExplicit || In.bStyleMatches) != (Decision == EDecision::Done))
				{
					Violate(TEXT("Done exactly when there is no choice or the weapon matches"), In, Decision);
				}
				// GiveUp only after the attempts are used and the last call had its time.
				if (Decision == EDecision::GiveUp && (Attempts < 3 || bVerifying || !In.bExplicit || In.bStyleMatches))
				{
					Violate(TEXT("a GiveUp before the attempts are used"), In, Decision);
				}
				// Defer only for an awake boss and a request that still has attempts.
				if (Decision == EDecision::Defer && (!In.bBossAwake || Attempts >= 3 || bVerifying || !In.bExplicit || In.bStyleMatches))
				{
					Violate(TEXT("a Defer that a rule forbids"), In, Decision);
				}
				// A call that is being verified is waited for, never repeated, whatever the boss does.
				if (In.bExplicit && !In.bStyleMatches && bVerifying && Decision != EDecision::Wait)
				{
					Violate(TEXT("a call under verification must Wait"), In, Decision);
				}
				// The other direction: when nothing is in the way, the loadout acts.
				const bool bNeeds = In.bExplicit && !In.bStyleMatches && In.bStyleKnown && !In.bPlayerDead && !bVerifying;
				if (bNeeds && Attempts >= 3 && Decision != EDecision::GiveUp)
				{
					Violate(TEXT("used attempts must give up"), In, Decision);
				}
				if (bNeeds && Attempts < 3 && In.bBossAwake && Decision != EDecision::Defer)
				{
					Violate(TEXT("an awake boss defers"), In, Decision);
				}
				if (bNeeds && Attempts < 3 && !In.bBossAwake && !In.bPlayerBusy && !bBlockedByCombat && Decision != EDecision::Apply)
				{
					Violate(TEXT("a free player with a sleeping boss gets the call"), In, Decision);
				}
				if (bNeeds && Attempts < 3 && !In.bBossAwake && (In.bPlayerBusy || bBlockedByCombat) && Decision != EDecision::Wait)
				{
					Violate(TEXT("a busy player waits"), In, Decision);
				}
				if (In.bExplicit && !In.bStyleMatches && (!In.bStyleKnown || In.bPlayerDead) && Decision != EDecision::Wait)
				{
					Violate(TEXT("an unready pack or a dead player waits"), In, Decision);
				}
			}
		}
	}
	TestEqual(TEXT("combinations checked"), Combinations, 256 * 5 * 5);
	TestEqual(*FString::Printf(TEXT("no violation in %d combinations"), Combinations), Violations, 0);
	if (Violations > 0)
	{
		AddError(FString::Printf(TEXT("%d violations, the first: %s"), Violations, *FirstViolation));
	}

	// Walk of one request: the pack starts, the boss sleeps, the call is made, verified, repeated and abandoned; then the same request with a boss that wakes up.
	FDecideInput Walk;
	Walk.bExplicit = true;
	Walk.MaxAttempts = 2;
	Walk.VerifySeconds = 4.f;
	TestEqual(TEXT("pack not ready: wait"), static_cast<int32>(RPGBuildRules::Decide(Walk)), static_cast<int32>(EDecision::Wait));
	Walk.bStyleKnown = true;
	TestEqual(TEXT("ready, boss asleep: apply"), static_cast<int32>(RPGBuildRules::Decide(Walk)), static_cast<int32>(EDecision::Apply));
	Walk.Attempts = 1;
	Walk.SecondsSinceAttempt = 1.f;
	TestEqual(TEXT("call 1 is being verified: wait"), static_cast<int32>(RPGBuildRules::Decide(Walk)), static_cast<int32>(EDecision::Wait));
	Walk.SecondsSinceAttempt = 4.f;
	TestEqual(TEXT("call 1 did not change the style: apply again"), static_cast<int32>(RPGBuildRules::Decide(Walk)), static_cast<int32>(EDecision::Apply));
	Walk.Attempts = 2;
	Walk.SecondsSinceAttempt = 4.5f;
	TestEqual(TEXT("both calls used: give up"), static_cast<int32>(RPGBuildRules::Decide(Walk)), static_cast<int32>(EDecision::GiveUp));
	Walk.bStyleMatches = true;
	TestEqual(TEXT("the style changed late: done"), static_cast<int32>(RPGBuildRules::Decide(Walk)), static_cast<int32>(EDecision::Done));
	Walk.bStyleMatches = false;
	Walk.Attempts = 0;
	Walk.SecondsSinceAttempt = -1.f;
	Walk.bBossAwake = true;
	TestEqual(TEXT("a choice made in the fight is deferred"), static_cast<int32>(RPGBuildRules::Decide(Walk)), static_cast<int32>(EDecision::Defer));
	Walk.bBossAwake = false;
	TestEqual(TEXT("the fight is over: apply"), static_cast<int32>(RPGBuildRules::Decide(Walk)), static_cast<int32>(EDecision::Apply));
	return true;
}

// ---------------------------------------------------------------------------------------------
// Assets and defaults of the loadout: the weapon items and combat styles the builds name exist, a loadout with no choice calls nothing, a missing pack is reported and never crashes
// ---------------------------------------------------------------------------------------------

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FRPGBuildAssetsTest, "OneBossFight.Build.Assets",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::ProductFilter)

bool FRPGBuildAssetsTest::RunTest(const FString& Parameters)
{
	using namespace RPGBuildRules;
	// The weapon items the loadout loads by path (RPGBuildRules::Entry().ItemPath) and the combat style assets the weapon attack table is keyed by.
	for (const ERPGBuild Build : {ERPGBuild::Starter, ERPGBuild::Strength, ERPGBuild::Dex})
	{
		const FString Package = FPackageName::ObjectPathToPackageName(FString(RPGBuildRules::Entry(Build).ItemPath));
		TestTrue(*FString::Printf(TEXT("the weapon item of %s exists (%s)"), BuildName(Build), *Package), FPackageName::DoesPackageExist(Package));
	}
	for (const TCHAR* Style : {TEXT("/Game/AdvancedARPGCombat/MeleeCombatSystem/Blueprints/Weapons/Sword/SwordCombatStyle"), TEXT("/Game/AdvancedARPGCombat/MeleeCombatSystem/Blueprints/Weapons/Claymore/ClaymoreCombatStyle"),
		TEXT("/Game/AdvancedARPGCombat/MeleeCombatSystem/Blueprints/Weapons/DualSwords/DualSwordCombatStyle")})
	{
		TestTrue(*FString::Printf(TEXT("the combat style asset %s exists"), Style), FPackageName::DoesPackageExist(Style));
		TestEqual(*FString::Printf(TEXT("%s is named like the key of the weapon attack table"), Style), FPackageName::GetShortName(FString(Style)).Right(11), FString(TEXT("CombatStyle")));
	}

	// A loadout that was never told a build (the class defaults, no world): no choice, no call, an idle state, the line of an unknown weapon, the owner's defaults of the plan.
	const URPGBuildLoadout* Defaults = GetDefault<URPGBuildLoadout>();
	TestFalse(TEXT("no choice by default"), Defaults->HasChoice());
	TestEqual(TEXT("no pack call by default"), Defaults->GetApplyAttemptCount(), 0);
	TestEqual(TEXT("the chosen build is Starter by default"), Defaults->GetChosenBuildName(), FString(TEXT("Starter")));
	TestEqual(TEXT("the state is idle by default"), Defaults->GetStateName(), FString(TEXT("Idle")));
	TestEqual(TEXT("the weapon is unknown before the pack answers"), Defaults->GetBuildName(), FString(TEXT("Unknown")));
	TestEqual(TEXT("the line before the pack answers"), Defaults->GetBuildLine(), FString(TEXT("Build: Unknown")));
	TestEqual(TEXT("three calls before giving up"), Defaults->MaxAttempts, 3);
	TestEqual(TEXT("four seconds to verify a call"), Defaults->VerifySeconds, 4.f);
	TestTrue(TEXT("the weapon slot is locked in the fight by default (Q2)"), Defaults->bLockWeaponSlotInFight);
	TestFalse(TEXT("the equip does not wait for the combat mode to end by default"), Defaults->bApplyOnlyOutOfCombat);

	// The wiring check on a pack that is not there reports what is missing and does not crash (it never reads a null class).
	FString Missing;
	TestFalse(TEXT("no pack classes: the names are reported missing"), URPGBuildLoadout::CheckPackSignatures(nullptr, nullptr, Missing));
	TestTrue(TEXT("the report names the equip function"), Missing.Contains(TEXT("Update Equip Slot Item")));
	TestTrue(TEXT("the report names the style variable"), Missing.Contains(TEXT("CurrentCombatStyle")));
	return true;
}

#endif // WITH_DEV_AUTOMATION_TESTS
