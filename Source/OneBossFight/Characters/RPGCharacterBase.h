// Copyright One Boss Fight. All Rights Reserved.

#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Character.h"
#include "RPGCharacterBase.generated.h"

/**
 * Shared base for the player and bosses.
 * Health/stamina/poise live in a dedicated attribute component (added in the combat milestone);
 * this class only owns movement defaults that every combatant shares.
 */
UCLASS(Abstract)
class ONEBOSSFIGHT_API ARPGCharacterBase : public ACharacter
{
	GENERATED_BODY()

public:
	ARPGCharacterBase();
};
