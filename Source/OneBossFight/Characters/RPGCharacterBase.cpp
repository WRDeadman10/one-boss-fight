// Copyright One Boss Fight. All Rights Reserved.

#include "Characters/RPGCharacterBase.h"
#include "Combat/RPGAttributeComponent.h"
#include "Combat/RPGCombatComponent.h"
#include "Combat/RPGMeleeTraceComponent.h"
#include "Components/CapsuleComponent.h"
#include "Components/SkeletalMeshComponent.h"
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

	Attributes = CreateDefaultSubobject<URPGAttributeComponent>(TEXT("Attributes"));
	Combat = CreateDefaultSubobject<URPGCombatComponent>(TEXT("Combat"));
	MeleeTrace = CreateDefaultSubobject<URPGMeleeTraceComponent>(TEXT("MeleeTrace"));
}

void ARPGCharacterBase::BeginPlay()
{
	Super::BeginPlay();
	Attributes->OnDeath.AddUniqueDynamic(this, &ARPGCharacterBase::HandleDeath);
}

void ARPGCharacterBase::HandleDeath()
{
	GetCapsuleComponent()->SetCollisionEnabled(ECollisionEnabled::NoCollision);
	GetCharacterMovement()->DisableMovement();
}

void ARPGCharacterBase::ResetCombatant()
{
	GetCapsuleComponent()->SetCollisionEnabled(ECollisionEnabled::QueryAndPhysics);
	GetCharacterMovement()->SetMovementMode(MOVE_Walking);
	Attributes->ResetAttributes();
	Combat->ResetCombat();
}
