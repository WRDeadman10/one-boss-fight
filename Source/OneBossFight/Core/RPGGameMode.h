// Copyright One Boss Fight. All Rights Reserved.

#pragma once

#include "CoreMinimal.h"
#include "GameFramework/GameModeBase.h"
#include "RPGGameMode.generated.h"

/**
 * Base game mode. Blueprint subclasses (e.g. BP_RPGGameMode) pick the concrete pawn
 * so art, input assets and movement tuning stay in content.
 */
UCLASS()
class ONEBOSSFIGHT_API ARPGGameMode : public AGameModeBase
{
	GENERATED_BODY()

public:
	ARPGGameMode();
};
