// Copyright One Boss Fight. All Rights Reserved.

#include "Core/RPGGameMode.h"
#include "Characters/RPGPlayerCharacter.h"

ARPGGameMode::ARPGGameMode()
{
	DefaultPawnClass = ARPGPlayerCharacter::StaticClass();
}
