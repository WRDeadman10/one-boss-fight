// Copyright One Boss Fight. All Rights Reserved.

#include "Core/RPGGameMode.h"
#include "Characters/RPGPlayerCharacter.h"
#include "Core/RPGHUD.h"

ARPGGameMode::ARPGGameMode()
{
	DefaultPawnClass = ARPGPlayerCharacter::StaticClass();
	HUDClass = ARPGHUD::StaticClass();
}
