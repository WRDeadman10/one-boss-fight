// Copyright One Boss Fight. All Rights Reserved.
#pragma once

#include "CoreMinimal.h"

/** Pure decisions for optional presentation previews. No object loading or engine state. */
namespace RPGPresentationRules
{
	inline bool IsTier2PreviewEnabledForBuild(bool bDevelopmentBuild, int32 CVarValue)
	{
		return bDevelopmentBuild && CVarValue != 0;
	}

	/** An empty configured path or observed path never matches. */
	inline bool MatchesOptionalTrackerMontagePath(const FString& OptionalPath, const FString& ObjectPath)
	{
		return !OptionalPath.IsEmpty() && !ObjectPath.IsEmpty() && OptionalPath == ObjectPath;
	}
}
