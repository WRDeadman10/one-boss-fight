// Copyright One Boss Fight. All Rights Reserved.

#include "Combat/RPGWeaponData.h"

const FRPGAttackData& URPGWeaponData::GetAttack(ERPGAttackType Type, int32 ComboIndex) const
{
	static const FRPGAttackData DefaultAttack;

	if (Type == ERPGAttackType::Heavy)
	{
		return HeavyAttack;
	}
	if (LightCombo.IsEmpty())
	{
		return DefaultAttack;
	}
	return LightCombo[FMath::Clamp(ComboIndex, 0, LightCombo.Num() - 1)];
}
