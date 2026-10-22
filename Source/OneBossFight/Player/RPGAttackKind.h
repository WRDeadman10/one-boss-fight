// Copyright One Boss Fight. All Rights Reserved.

#pragma once

#include "CoreMinimal.h"
#include "RPGAttackKind.generated.h"

/** The kind of attack a hit came from, the key of the weapon attack table (Freeze 20: light, jumping heavy; the pack also has a ground heavy and a charged attack). */
UENUM(BlueprintType)
enum class ERPGAttackKind : uint8
{
	Unknown,
	Light,
	Strong,
	Charged,
	/** A light attack made in the air (the pack's falling attack). */
	JumpLight,
	/** A strong attack made in the air (the Freeze's jumping heavy, Scripts/air_heavy_selector.py). */
	JumpHeavy,
	Knockdown,
};

inline const TCHAR* RPGAttackKindName(ERPGAttackKind Kind)
{
	switch (Kind)
	{
	case ERPGAttackKind::Light: return TEXT("Light");
	case ERPGAttackKind::Strong: return TEXT("Strong");
	case ERPGAttackKind::Charged: return TEXT("Charged");
	case ERPGAttackKind::JumpLight: return TEXT("JumpLight");
	case ERPGAttackKind::JumpHeavy: return TEXT("JumpHeavy");
	case ERPGAttackKind::Knockdown: return TEXT("Knockdown");
	default: return TEXT("Unknown");
	}
}

/**
 * The kind of attack from the pack's attack data asset name and the stance. The pack has four melee attack data assets (Default = light, Strong, Charged, Knockdown) shared by all weapons (read by
 * Scripts/Editor/g3_dump_attack_data.py, confirmed by pie_hit_intake.py); the stance decides whether a light or strong attack is a jump attack. Header only so an automation test can check it.
 */
inline ERPGAttackKind RPGClassifyAttack(const FName& AttackDataName, bool bAirborne)
{
	const FString Name = AttackDataName.ToString();
	if (Name.StartsWith(TEXT("Default")))
	{
		return bAirborne ? ERPGAttackKind::JumpLight : ERPGAttackKind::Light;
	}
	if (Name.StartsWith(TEXT("Strong")))
	{
		return bAirborne ? ERPGAttackKind::JumpHeavy : ERPGAttackKind::Strong;
	}
	if (Name.StartsWith(TEXT("Charged")))
	{
		return ERPGAttackKind::Charged;
	}
	if (Name.StartsWith(TEXT("MeleeKnockdown")))
	{
		return ERPGAttackKind::Knockdown;
	}
	return ERPGAttackKind::Unknown;
}
