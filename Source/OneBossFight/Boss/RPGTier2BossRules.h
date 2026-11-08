// Copyright One Boss Fight. All Rights Reserved.
#pragma once

#include "CoreMinimal.h"

namespace RPGTier2BossRules
{
	inline bool ShouldShowAura(bool bTier2Enabled, double Health, double MaxHealth, bool bDormant)
	{
		return bTier2Enabled && !bDormant && FMath::IsFinite(Health) && FMath::IsFinite(MaxHealth)
			&& MaxHealth > 0. && Health > 0. && Health <= MaxHealth * 0.6;
	}

	inline bool ShouldPlayParryRecoil(bool bTier2Enabled, bool bSuccessfulParry)
	{
		return bTier2Enabled && bSuccessfulParry;
	}

	inline bool ShouldSpawnAura(bool bTier2Enabled, double Health, double MaxHealth, bool bDormant, bool bAuraActivatedThisPhase)
	{
		return !bAuraActivatedThisPhase && ShouldShowAura(bTier2Enabled, Health, MaxHealth, bDormant);
	}
}
