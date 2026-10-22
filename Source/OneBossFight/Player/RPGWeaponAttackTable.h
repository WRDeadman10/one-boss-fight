// Copyright One Boss Fight. All Rights Reserved.

#pragma once

#include "CoreMinimal.h"
#include "Engine/DataAsset.h"
#include "Player/RPGAttackKind.h"
#include "RPGWeaponAttackTable.generated.h"

/**
 * What one kind of attack of one weapon does to the boss and costs the player (Gate 3, Freeze 5, 20 and 36). One row per (weapon, kind); the weapon is the asset name of the pack's combat style
 * (SwordCombatStyle, ClaymoreCombatStyle, DualSwordCombatStyle, TwinbladeCombatStyle); an empty weapon name is a row for every weapon.
 */
USTRUCT(BlueprintType)
struct ONEBOSSFIGHT_API FRPGWeaponAttackRow
{
	GENERATED_BODY()

	/** The pack's combat style asset name. None: any weapon. */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Attack")
	FName Weapon;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Attack")
	ERPGAttackKind Kind = ERPGAttackKind::Light;

	/** Posture points the hit takes from the boss's posture pool (Freeze 17.2: the pool is 100). */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Attack", meta = (ClampMin = "0.0"))
	float PostureDamage = 0.f;

	/** Stamina the swing costs. Negative: leave the pack's own cost (15 per swing). */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Attack")
	float StaminaCost = -1.f;

	/** Bleed buildup points per hit (Freeze 20.2: 20 per hit for the dexterity build). */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Attack", meta = (ClampMin = "0.0"))
	float BleedBuildup = 0.f;

	/** Hyperarmor window in seconds from the start of the attack montage (Freeze 20.1: only the authored part of the downswing, HP damage still applies). Negative start: none. */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Attack")
	float HyperArmorStart = -1.f;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Attack")
	float HyperArmorEnd = -1.f;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Attack")
	FString Note;

	bool HasHyperArmor() const { return HyperArmorStart >= 0.f && HyperArmorEnd > HyperArmorStart; }
};

/**
 * The weapon attack table (Gate 3, M8): the single owner of the per-weapon, per-attack numbers (Freeze 20.3: "store weapon values in data, not if statements"). The constructor fills the Freeze starting values so a
 * new asset starts right; the asset in Content/OneBossFight/Data holds what the owner tunes (Scripts/Editor/make_weapon_table.py creates it once and never overwrites it). Lookup order: the exact (weapon, kind) row,
 * then the row of the kind for any weapon, then Fallback.
 */
UCLASS(BlueprintType)
class ONEBOSSFIGHT_API URPGWeaponAttackTable : public UPrimaryDataAsset
{
	GENERATED_BODY()

public:
	URPGWeaponAttackTable();

	/** The pack's own behaviour for a (weapon, kind) without a row: 20 posture (what the pack takes from the boss's poise per light hit), the pack's stamina cost, no bleed. */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Table")
	FRPGWeaponAttackRow Fallback;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Table")
	TArray<FRPGWeaponAttackRow> Rows;

	/** The row for the weapon and kind. Returns true when a row of the table matched (exact or any-weapon); false when Fallback was returned. */
	bool Find(FName Weapon, ERPGAttackKind Kind, FRPGWeaponAttackRow& OutRow) const;

	/** Puts the Freeze starting values into Rows and Fallback (called by the constructor). */
	void FillDefaults();

	/** The asset at the project path when it exists, else a transient table with the defaults (logged once). */
	static URPGWeaponAttackTable* LoadOrDefault();

	static const TCHAR* AssetPath() { return TEXT("/Game/OneBossFight/Data/DA_WeaponAttacks.DA_WeaponAttacks"); }
};
