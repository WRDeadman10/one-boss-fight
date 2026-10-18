// Copyright One Boss Fight. All Rights Reserved.

#include "Characters/RPGBossCharacter.h"
#include "Boss/RPGBossCombatComponent.h"
#include "Boss/RPGBossStateTree.h"
#include "Combat/RPGAttributeComponent.h"
#include "Combat/RPGCombatComponent.h"
#include "Core/RPGEncounterSubsystem.h"
#include "Engine/World.h"
#include "GameFramework/CharacterMovementComponent.h"

ARPGBossCharacter::ARPGBossCharacter()
{
	BossCombat = CreateDefaultSubobject<URPGBossCombatComponent>(TEXT("BossCombat"));
	StateTreeComponent = CreateDefaultSubobject<URPGBossStateTreeComponent>(TEXT("BossStateTree"));

	GetCombat()->TeamId = 1;
	GetAttributes()->MaxHealth = 1500.f;
	GetAttributes()->MaxPoise = 120.f;
	GetAttributes()->PoiseResetDelay = 6.f;

	// The boss component turns the body itself so attack tracking is exact.
	UCharacterMovementComponent* Movement = GetCharacterMovement();
	Movement->bOrientRotationToMovement = false;
	Movement->MaxWalkSpeed = 450.f;
	Movement->BrakingDecelerationWalking = 2000.f;

	AutoPossessAI = EAutoPossessAI::PlacedInWorldOrSpawned;
}

void ARPGBossCharacter::BeginPlay()
{
	Super::BeginPlay();
	HomeTransform = GetActorTransform();

	if (URPGEncounterSubsystem* Encounter = GetWorld()->GetSubsystem<URPGEncounterSubsystem>())
	{
		Encounter->RegisterBoss(this);
	}
}

void ARPGBossCharacter::ResetCombatant()
{
	Super::ResetCombatant();
	BossCombat->ResetBoss();
	SetActorTransform(HomeTransform, false, nullptr, ETeleportType::TeleportPhysics);
	GetCharacterMovement()->StopMovementImmediately();
}
