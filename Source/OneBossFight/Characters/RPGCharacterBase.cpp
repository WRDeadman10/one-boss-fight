// Copyright One Boss Fight. All Rights Reserved.

#include "Characters/RPGCharacterBase.h"
#include "GameFramework/CharacterMovementComponent.h"

ARPGCharacterBase::ARPGCharacterBase()
{
	// Event-driven by default; derived classes opt in to Tick only when needed.
	PrimaryActorTick.bCanEverTick = false;

	// The controller aims the camera; the body turns toward its movement direction.
	bUseControllerRotationPitch = false;
	bUseControllerRotationYaw = false;
	bUseControllerRotationRoll = false;

	UCharacterMovementComponent* Movement = GetCharacterMovement();
	Movement->bOrientRotationToMovement = true;
	Movement->RotationRate = FRotator(0.f, 540.f, 0.f);
}
