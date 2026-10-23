// Copyright One Boss Fight. All Rights Reserved.

#pragma once

#include "CoreMinimal.h"

/** The builds of Gate 3 (Freeze 5 and 20): the starter sword the pack gives, the strength build (claymore) and the dex build (dual swords). Not a UENUM: no Unreal object holds it, the console variable and the tests use the names. */
enum class ERPGBuild : uint8
{
	/** The pack's own sword: what the player has when no build was chosen. */
	Starter = 0,
	Strength = 1,
	Dex = 2,
};

/**
 * The rules of the build loadout (Gate 3, M13) with no Unreal object in them, so an automation test can check each one without a world: the names, which pack combat style and weapon item belongs to which build,
 * what the console text means, what the loadout does next (Wait, Apply, Done, Defer, GiveUp), when the weapon slot is locked, and the HUD line. The numbers of the builds (posture, stamina, bleed) are NOT here:
 * they live in the weapon attack table, keyed by the combat style name (Freeze 20.3); a build only decides which weapon the player holds.
 */
namespace RPGBuildRules
{
	constexpr int32 BuildCount = 3;

	/** The enumerator of the weapon slot in the pack's E_EquipSlots (read in the audit: the weapon item's default EquipSlot and the CycleRight quickslot, M13_BUILDS_PLAN.md 1.2 #11). */
	constexpr int32 WeaponSlotEnumerator = 11;

	/** Everything that says which weapon a build is. One row per build, in the order of the enum (a test checks it). */
	struct FBuildEntry
	{
		ERPGBuild Build;
		/** The text of the console variable rpg.Build and the build word of the HUD line. */
		const TCHAR* Name;
		/** The pack's combat style asset name (CurrentCombatStyle of the player's combat component): the key of the weapon attack table. */
		const TCHAR* Style;
		/** The pack's weapon item asset (a WeaponItem data asset under MeleeCombatSystem/Blueprints/Items/Weapons), loaded by the loadout. */
		const TCHAR* ItemPath;
		/** The class of the weapon actor the pack spawns for the item. */
		const TCHAR* ActorClass;
		/** The class of the weapon ability the pack grants while the weapon is equipped. */
		const TCHAR* AbilityClass;
		/** The weapon word of the HUD line. */
		const TCHAR* Weapon;
	};

	inline const FBuildEntry& Entry(ERPGBuild Build)
	{
		static const FBuildEntry Table[BuildCount] =
		{
			{ERPGBuild::Starter, TEXT("Starter"), TEXT("SwordCombatStyle"), TEXT("/Game/AdvancedARPGCombat/MeleeCombatSystem/Blueprints/Items/Weapons/ToughSword.ToughSword"), TEXT("BP_ToughSword_C"), TEXT("GA_Sword_Melee_C"), TEXT("Sword")},
			{ERPGBuild::Strength, TEXT("Strength"), TEXT("ClaymoreCombatStyle"), TEXT("/Game/AdvancedARPGCombat/MeleeCombatSystem/Blueprints/Items/Weapons/KwangSword.KwangSword"), TEXT("BP_KwangSword_C"), TEXT("GA_Claymore_Melee_C"), TEXT("Claymore")},
			{ERPGBuild::Dex, TEXT("Dex"), TEXT("DualSwordCombatStyle"), TEXT("/Game/AdvancedARPGCombat/MeleeCombatSystem/Blueprints/Items/Weapons/DualSteelSwords.DualSteelSwords"), TEXT("BP_DualSteelSwords_C"), TEXT("GA_DuaSword_Melee_C"), TEXT("Dual Swords")},
		};
		const int32 Index = FMath::Clamp(static_cast<int32>(Build), 0, BuildCount - 1);
		return Table[Index];
	}

	inline const TCHAR* BuildName(ERPGBuild Build) { return Entry(Build).Name; }

	/** The pack's combat style asset name of a build (SwordCombatStyle, ClaymoreCombatStyle, DualSwordCombatStyle). */
	inline const TCHAR* StyleOfBuild(ERPGBuild Build) { return Entry(Build).Style; }

	/**
	 * The build a pack combat style belongs to. The starter build is the sword and the sword with a shield (the pack merges them, the table has no row for the merge: it is treated as the starter), the strength build is
	 * the claymore, the dex build is the dual swords and the twinblades (the spare dex weapon, same table rows). False for every other style (polearm, unarmed, magic, bow, ...) and for none: the player holds an off-build weapon.
	 */
	inline bool BuildOfStyle(const FName& Style, ERPGBuild& OutBuild)
	{
		if (Style == FName(TEXT("SwordCombatStyle")) || Style == FName(TEXT("SwordAndShieldCombatStyle")))
		{
			OutBuild = ERPGBuild::Starter;
			return true;
		}
		if (Style == FName(TEXT("ClaymoreCombatStyle")))
		{
			OutBuild = ERPGBuild::Strength;
			return true;
		}
		if (Style == FName(TEXT("DualSwordCombatStyle")) || Style == FName(TEXT("TwinbladeCombatStyle")))
		{
			OutBuild = ERPGBuild::Dex;
			return true;
		}
		return false;
	}

	/** True when the style is one of the build's. */
	inline bool StyleMatchesBuild(const FName& Style, ERPGBuild Build)
	{
		ERPGBuild Found = ERPGBuild::Starter;
		return BuildOfStyle(Style, Found) && Found == Build;
	}

	// ---------------------------------------------------------------------------------------------
	// The console text
	// ---------------------------------------------------------------------------------------------

	enum class EParse : uint8
	{
		/** No choice (empty text, none, off): the loadout never calls the pack. */
		Empty,
		Build,
		Invalid,
	};

	/** Reads the text of rpg.Build: any case, quotes and spaces around it ignored. strength and str, dex and dexterity, starter and sword name the builds; empty, none and off mean no choice; anything else is Invalid. */
	inline EParse Parse(const FString& Text, ERPGBuild& OutBuild)
	{
		FString Key = Text.TrimStartAndEnd();
		Key = Key.TrimQuotes();
		Key = Key.TrimStartAndEnd().ToLower();
		if (Key.IsEmpty() || Key == TEXT("none") || Key == TEXT("off"))
		{
			return EParse::Empty;
		}
		if (Key == TEXT("strength") || Key == TEXT("str"))
		{
			OutBuild = ERPGBuild::Strength;
			return EParse::Build;
		}
		if (Key == TEXT("dex") || Key == TEXT("dexterity"))
		{
			OutBuild = ERPGBuild::Dex;
			return EParse::Build;
		}
		if (Key == TEXT("starter") || Key == TEXT("sword"))
		{
			OutBuild = ERPGBuild::Starter;
			return EParse::Build;
		}
		return EParse::Invalid;
	}

	// ---------------------------------------------------------------------------------------------
	// What the loadout does next
	// ---------------------------------------------------------------------------------------------

	enum class EDecision : uint8
	{
		/** Not now (the pack is still starting, the player is dead or busy, or the last call is still being verified): ask again at the next poll. */
		Wait,
		/** Call the pack's equip function now. */
		Apply,
		/** Nothing to do: no explicit choice, or the player already holds the build's weapon. */
		Done,
		/** The boss is awake: the choice stays pending until the fight resets or the boss is gone. */
		Defer,
		/** The attempts are used and the style did not change: stop, the player keeps the weapon he has. */
		GiveUp,
	};

	inline const TCHAR* DecisionName(EDecision Decision)
	{
		switch (Decision)
		{
		case EDecision::Wait: return TEXT("Wait");
		case EDecision::Apply: return TEXT("Apply");
		case EDecision::Done: return TEXT("Done");
		case EDecision::Defer: return TEXT("Defer");
		case EDecision::GiveUp: return TEXT("GiveUp");
		}
		return TEXT("?");
	}

	/** What the loadout knows at one poll. */
	struct FDecideInput
	{
		/** A build was chosen (console variable, key or test hook). False: the player's weapon is left alone, whatever it is. */
		bool bExplicit = false;
		/** The pack's combat and equipment components are ready, including a populated weapon slot. The style itself may be None: equipping is what restores an unarmed player. */
		bool bStyleKnown = false;
		/** The weapon the player holds belongs to the chosen build (StyleMatchesBuild). */
		bool bStyleMatches = false;
		/** The boss exists and is not dormant. No boss at all counts as dormant (the pack destroys a dead boss). */
		bool bBossAwake = false;
		bool bPlayerDead = false;
		/** The player is in a montage (a dodge, a swing, a hit stun, an equip clip of the pack). */
		bool bPlayerBusy = false;
		/** The pack's combat mode is on (the weapon is drawn). */
		bool bPlayerInCombat = false;
		/** Policy: when true the equip waits until the combat mode is off. Off by default (the pack's own quickslot works in combat mode too, probe 2026-10-22). */
		bool bCombatBlocksApply = false;
		/** Calls made for this request so far. */
		int32 Attempts = 0;
		int32 MaxAttempts = 3;
		/** Seconds since the last call, negative when none was made. */
		float SecondsSinceAttempt = -1.f;
		/** How long the style gets to change after a call before the call counts as failed. */
		float VerifySeconds = 4.f;
	};

	/** True while the last call is younger than VerifySeconds. */
	inline bool IsVerifying(const FDecideInput& In)
	{
		return In.Attempts > 0 && In.SecondsSinceAttempt >= 0.f && In.SecondsSinceAttempt < In.VerifySeconds;
	}

	/**
	 * The apply state machine of the loadout (M13_BUILDS_PLAN.md 2.3). Order of the checks:
	 *   no choice or the build's weapon already held -> Done; the pack is not ready or the player is dead -> Wait; a call younger than VerifySeconds -> Wait (the pack gets time);
	 *   the attempts are used -> GiveUp (never another call); the boss is awake -> Defer; the player is busy (or in combat when that blocks) -> Wait; otherwise Apply.
	 * Invariants (the tests check them over every combination): no choice never calls, an awake boss never gets a call, a dead or busy player never gets a call, a matching style never gets a call,
	 * no call while the last one is being verified, no call after MaxAttempts.
	 */
	inline EDecision Decide(const FDecideInput& In)
	{
		if (!In.bExplicit || In.bStyleMatches)
		{
			return EDecision::Done;
		}
		if (!In.bStyleKnown || In.bPlayerDead)
		{
			return EDecision::Wait;
		}
		if (IsVerifying(In))
		{
			return EDecision::Wait;
		}
		if (In.Attempts >= In.MaxAttempts)
		{
			return EDecision::GiveUp;
		}
		if (In.bBossAwake)
		{
			return EDecision::Defer;
		}
		if (In.bPlayerBusy || (In.bCombatBlocksApply && In.bPlayerInCombat))
		{
			return EDecision::Wait;
		}
		return EDecision::Apply;
	}

	/**
	 * The pack's E_EquipUpdateType byte of the n-th call (1 based) of one request. The enum is shown as Update, Replace, Internal Update, Unequip and its enumerator order was not read: the first call uses 0 (the owner's
	 * decision), the second 1, the third 0 again; the Unequip entry is never sent.
	 */
	inline int32 UpdateTypeForAttempt(int32 AttemptNumber)
	{
		static const int32 Sequence[3] = {0, 1, 0};
		const int32 Index = FMath::Max(AttemptNumber - 1, 0);
		return Sequence[Index % 3];
	}

	/** Q2 of the plan: the weapon slot is locked from the moment the boss is awake until it sleeps again or is gone (a dead boss is destroyed by the pack), so a quickslot press cannot leave the build. */
	inline bool ShouldLockSlot(bool bLockEnabled, bool bBossPresent, bool bBossDormant)
	{
		return bLockEnabled && bBossPresent && !bBossDormant;
	}

	// ---------------------------------------------------------------------------------------------
	// The HUD line (the truth rule: it names the weapon the player really holds, never the choice alone)
	// ---------------------------------------------------------------------------------------------

	/** The build and weapon of a combat style: Starter (Sword), Strength (Claymore), Dex (Dual Swords), Dex (Twinblades), Off-build (Polearm) for any other style, Unknown for none. */
	inline FString DescribeStyle(const FName& Style)
	{
		if (Style.IsNone())
		{
			return TEXT("Unknown");
		}
		if (Style == FName(TEXT("SwordAndShieldCombatStyle")))
		{
			return TEXT("Starter (Sword and Shield)");
		}
		if (Style == FName(TEXT("TwinbladeCombatStyle")))
		{
			return TEXT("Dex (Twinblades)");
		}
		ERPGBuild Build = ERPGBuild::Starter;
		if (BuildOfStyle(Style, Build))
		{
			return FString::Printf(TEXT("%s (%s)"), Entry(Build).Name, Entry(Build).Weapon);
		}
		FString Word = Style.ToString();
		if (Word.EndsWith(TEXT("CombatStyle")))
		{
			Word = Word.LeftChop(11); // the 11 characters of "CombatStyle"
		}
		return FString::Printf(TEXT("Off-build (%s)"), *Word);
	}

	/** The line of the HUD, for example "Build: Strength (Claymore)". The suffix says what the loadout is doing about a weapon that is not the chosen one. */
	inline FString BuildLine(const FName& ActualStyle, EDecision Last)
	{
		const TCHAR* Suffix = TEXT("");
		switch (Last)
		{
		case EDecision::Wait:
		case EDecision::Apply:
			Suffix = TEXT(" - equipping...");
			break;
		case EDecision::Defer:
			Suffix = TEXT(" - next fight");
			break;
		case EDecision::GiveUp:
			Suffix = TEXT(" - not equipped");
			break;
		case EDecision::Done:
			break;
		}
		return FString::Printf(TEXT("Build: %s%s"), *DescribeStyle(ActualStyle), Suffix);
	}
}
