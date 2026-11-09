// Copyright One Boss Fight. All Rights Reserved.
#pragma once

#include "CoreMinimal.h"

/** Pure decisions for optional presentation previews. No object loading or engine state. */
namespace RPGPresentationRules
{
	inline bool IsTier2PresentationEnabledForBuild(bool bDevelopmentBuild, bool bConfiguredDefault, int32 CVarValue)
	{
		if (!bDevelopmentBuild)
		{
			return bConfiguredDefault;
		}
		if (CVarValue == -1)
		{
			return bConfiguredDefault;
		}
		if (CVarValue == 0 || CVarValue == 1)
		{
			return CVarValue == 1;
		}
		return false;
	}

	/** An empty configured path or observed path never matches. */
	inline bool MatchesOptionalTrackerMontagePath(const FString& OptionalPath, const FString& ObjectPath)
	{
		return !OptionalPath.IsEmpty() && !ObjectPath.IsEmpty() && OptionalPath == ObjectPath;
	}
}
