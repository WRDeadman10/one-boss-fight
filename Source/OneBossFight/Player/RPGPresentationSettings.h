// Copyright One Boss Fight. All Rights Reserved.

#pragma once

#include "CoreMinimal.h"
#include "UObject/Object.h"
#include "RPGPresentationSettings.generated.h"

/** Game-wide authored defaults for optional presentation features. */
UCLASS(Config=Game, DefaultConfig)
class ONEBOSSFIGHT_API URPGPresentationSettings : public UObject
{
	GENERATED_BODY()

public:
	/** Enables Tier 2 aura and parry-recoil presentation in all configurations unless Development overrides it. */
	UPROPERTY(Config, EditAnywhere, Category="Presentation")
	bool bTier2PresentationEnabled = true;
};
