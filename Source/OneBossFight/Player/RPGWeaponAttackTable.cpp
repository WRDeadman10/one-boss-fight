// Copyright One Boss Fight. All Rights Reserved.

#include "Player/RPGWeaponAttackTable.h"
#include "UObject/Package.h"

DEFINE_LOG_CATEGORY_STATIC(LogRPGWeaponTable, Log, All);

namespace
{
	FRPGWeaponAttackRow Make(const TCHAR* Weapon, ERPGAttackKind Kind, float Posture, float Stamina, float Bleed, const TCHAR* Note)
	{
		FRPGWeaponAttackRow Row;
		Row.Weapon = Weapon;
		Row.Kind = Kind;
		Row.PostureDamage = Posture;
		Row.StaminaCost = Stamina;
		Row.BleedBuildup = Bleed;
		Row.Note = Note;
		return Row;
	}

	/** The hyperarmor window of a row (seconds of the attack montage). The numbers are measured (g3_probe_montages.py, 2026-10-22, M13_BUILDS_PLAN.md appendix): the window opens 0.08 s before the first weapon trace window of the montage and closes with the last one. */
	FRPGWeaponAttackRow WithWindow(FRPGWeaponAttackRow Row, float Start, float End, const TCHAR* Montage)
	{
		Row.HyperArmorStart = Start;
		Row.HyperArmorEnd = End;
		Row.Note += FString::Printf(TEXT("; hyperarmor %s %.3f-%.3f"), Montage, Start, End);
		return Row;
	}
}

URPGWeaponAttackTable::URPGWeaponAttackTable()
{
	FillDefaults();
}

void URPGWeaponAttackTable::FillDefaults()
{
	Fallback = Make(TEXT(""), ERPGAttackKind::Unknown, 20.f, -1.f, 0.f, TEXT("no row: the pack's own numbers (20 poise per hit, its own stamina cost, no bleed)"));
	Rows.Reset();
	// Strength archetype (Freeze 5 and 20.1): light 18, jumping heavy 38, stamina 35 per heavy swing. The ground strong, charged and jump light values are proposals (tunable): the Freeze gives only light and jumping heavy.
	const TCHAR* Strength[] = {TEXT("ClaymoreCombatStyle"), TEXT("SwordCombatStyle")};
	for (const TCHAR* Weapon : Strength)
	{
		const bool bStarter = FString(Weapon) == TEXT("SwordCombatStyle");
		const float Heavy = bStarter ? -1.f : 35.f; // the starter sword keeps the pack's stamina cost
		Rows.Add(Make(Weapon, ERPGAttackKind::Light, 18.f, -1.f, 0.f, TEXT("Freeze 20.1")));
		// The Strength build's downswing carries hyperarmor (Freeze 5, 20.1, M3: the jumping heavy); the pack plays one montage for the strong and the jump heavy (Ability_E_Anim_Montage, trace 0.432 to 0.618) and ChargedAttack_Montage for the charged (0.503 to 1.005). The starter sword has none.
		const bool bWindow = !bStarter;
		FRPGWeaponAttackRow Strong = Make(Weapon, ERPGAttackKind::Strong, 30.f, Heavy, 0.f, TEXT("proposal"));
		FRPGWeaponAttackRow Charged = Make(Weapon, ERPGAttackKind::Charged, 38.f, Heavy, 0.f, TEXT("proposal"));
		FRPGWeaponAttackRow JumpHeavy = Make(Weapon, ERPGAttackKind::JumpHeavy, 38.f, Heavy, 0.f, TEXT("Freeze 20.1"));
		Rows.Add(bWindow ? WithWindow(Strong, 0.352f, 0.618f, TEXT("Ability_E_Anim_Montage")) : Strong);
		Rows.Add(bWindow ? WithWindow(Charged, 0.423f, 1.005f, TEXT("ChargedAttack_Montage")) : Charged);
		Rows.Add(Make(Weapon, ERPGAttackKind::JumpLight, 18.f, -1.f, 0.f, TEXT("proposal")));
		Rows.Add(bWindow ? WithWindow(JumpHeavy, 0.352f, 0.618f, TEXT("Ability_E_Anim_Montage")) : JumpHeavy);
		Rows.Add(Make(Weapon, ERPGAttackKind::Knockdown, 38.f, Heavy, 0.f, TEXT("proposal")));
	}
	// Dexterity archetype (Freeze 5 and 20.2): light 6, jumping heavy 14, stamina 10 per swing, bleed 20 per hit.
	const TCHAR* Dexterity[] = {TEXT("DualSwordCombatStyle"), TEXT("TwinbladeCombatStyle")};
	for (const TCHAR* Weapon : Dexterity)
	{
		Rows.Add(Make(Weapon, ERPGAttackKind::Light, 6.f, 10.f, 20.f, TEXT("Freeze 20.2")));
		Rows.Add(Make(Weapon, ERPGAttackKind::Strong, 10.f, 10.f, 20.f, TEXT("proposal")));
		Rows.Add(Make(Weapon, ERPGAttackKind::Charged, 14.f, 10.f, 20.f, TEXT("proposal")));
		Rows.Add(Make(Weapon, ERPGAttackKind::JumpLight, 6.f, 10.f, 20.f, TEXT("proposal")));
		Rows.Add(Make(Weapon, ERPGAttackKind::JumpHeavy, 14.f, 10.f, 20.f, TEXT("Freeze 5")));
		Rows.Add(Make(Weapon, ERPGAttackKind::Knockdown, 14.f, 10.f, 20.f, TEXT("proposal")));
	}
}

bool URPGWeaponAttackTable::Find(FName Weapon, ERPGAttackKind Kind, FRPGWeaponAttackRow& OutRow) const
{
	const FRPGWeaponAttackRow* AnyWeapon = nullptr;
	for (const FRPGWeaponAttackRow& Row : Rows)
	{
		if (Row.Kind != Kind)
		{
			continue;
		}
		if (Row.Weapon == Weapon && !Weapon.IsNone())
		{
			OutRow = Row;
			return true;
		}
		if (Row.Weapon.IsNone() && !AnyWeapon)
		{
			AnyWeapon = &Row;
		}
	}
	if (AnyWeapon)
	{
		OutRow = *AnyWeapon;
		return true;
	}
	OutRow = Fallback;
	OutRow.Weapon = Weapon;
	OutRow.Kind = Kind;
	return false;
}

URPGWeaponAttackTable* URPGWeaponAttackTable::LoadOrDefault()
{
	if (URPGWeaponAttackTable* Asset = LoadObject<URPGWeaponAttackTable>(nullptr, AssetPath(), nullptr, LOAD_NoWarn))
	{
		return Asset;
	}
	// One transient table with the defaults for the whole session (rooted: nothing else holds it).
	static TWeakObjectPtr<URPGWeaponAttackTable> Transient;
	if (!Transient.IsValid())
	{
		URPGWeaponAttackTable* Table = NewObject<URPGWeaponAttackTable>(GetTransientPackage(), TEXT("RPGWeaponAttackTable_Default"));
		Table->AddToRoot();
		Transient = Table;
		UE_LOG(LogRPGWeaponTable, Warning, TEXT("%s is not in the project (run Scripts/Editor/make_weapon_table.py): the built-in defaults are used"), AssetPath());
	}
	return Transient.Get();
}
