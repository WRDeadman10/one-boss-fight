// Copyright One Boss Fight. All Rights Reserved.

#include "Characters/RPGPlayerCharacter.h"
#include "OneBossFight.h"
#include "Camera/CameraComponent.h"
#include "Camera/PlayerCameraManager.h"
#include "Combat/RPGAttributeComponent.h"
#include "Combat/RPGCombatComponent.h"
#include "Combat/RPGTargetLockComponent.h"
#include "Components/CapsuleComponent.h"
#include "Core/RPGEncounterSubsystem.h"
#include "EnhancedInputComponent.h"
#include "EnhancedInputSubsystems.h"
#include "Engine/LocalPlayer.h"
#include "GameFramework/CharacterMovementComponent.h"
#include "GameFramework/PlayerController.h"
#include "GameFramework/SpringArmComponent.h"

ARPGPlayerCharacter::ARPGPlayerCharacter()
{
	// Ticks only to turn sprint into a stamina drain while the character is actually moving.
	PrimaryActorTick.bCanEverTick = true;

	CameraBoom = CreateDefaultSubobject<USpringArmComponent>(TEXT("CameraBoom"));
	CameraBoom->SetupAttachment(GetRootComponent());
	CameraBoom->SetRelativeLocation(FVector(0.f, 0.f, 60.f));
	CameraBoom->TargetArmLength = 450.f;
	CameraBoom->bUsePawnControlRotation = true;
	CameraBoom->bEnableCameraLag = true;
	CameraBoom->CameraLagSpeed = 20.f;

	FollowCamera = CreateDefaultSubobject<UCameraComponent>(TEXT("FollowCamera"));
	FollowCamera->SetupAttachment(CameraBoom, USpringArmComponent::SocketName);
	FollowCamera->bUsePawnControlRotation = false;

	TargetLock = CreateDefaultSubobject<URPGTargetLockComponent>(TEXT("TargetLock"));

	UCharacterMovementComponent* Movement = GetCharacterMovement();
	Movement->MaxWalkSpeed = WalkSpeed;
	Movement->JumpZVelocity = 500.f;
	Movement->AirControl = 0.2f;
	Movement->BrakingDecelerationWalking = 2000.f;

	GetCombat()->TeamId = 0;
}

void ARPGPlayerCharacter::BeginPlay()
{
	Super::BeginPlay();
	GetAttributes()->OnStaminaDepleted.AddUniqueDynamic(this, &ARPGPlayerCharacter::HandleStaminaDepleted);

	if (URPGEncounterSubsystem* Encounter = GetWorld()->GetSubsystem<URPGEncounterSubsystem>())
	{
		Encounter->RegisterPlayer(this);
	}
}

void ARPGPlayerCharacter::Tick(float DeltaSeconds)
{
	Super::Tick(DeltaSeconds);

	const bool bMoving = GetVelocity().SizeSquared2D() > FMath::Square(100.f);
	GetAttributes()->SetStaminaDrain(bSprinting && bMoving ? SprintStaminaPerSecond : 0.f);
}

void ARPGPlayerCharacter::PawnClientRestart()
{
	Super::PawnClientRestart();

	APlayerController* PlayerController = Cast<APlayerController>(GetController());
	if (!PlayerController)
	{
		return;
	}

	if (PlayerController->PlayerCameraManager)
	{
		PlayerController->PlayerCameraManager->ViewPitchMin = MinCameraPitch;
		PlayerController->PlayerCameraManager->ViewPitchMax = MaxCameraPitch;
	}

	ULocalPlayer* LocalPlayer = PlayerController->GetLocalPlayer();
	UEnhancedInputLocalPlayerSubsystem* InputSubsystem =
		LocalPlayer ? LocalPlayer->GetSubsystem<UEnhancedInputLocalPlayerSubsystem>() : nullptr;
	if (!InputSubsystem)
	{
		return;
	}

	if (!DefaultMappingContext)
	{
		UE_LOG(LogOneBossFight, Warning, TEXT("%s has no DefaultMappingContext assigned; the player cannot be controlled."), *GetName());
		return;
	}

	// Re-registered on every (re)possession so retry/respawn never stacks duplicate contexts.
	InputSubsystem->RemoveMappingContext(DefaultMappingContext);
	InputSubsystem->AddMappingContext(DefaultMappingContext, 0);
}

void ARPGPlayerCharacter::SetupPlayerInputComponent(UInputComponent* PlayerInputComponent)
{
	Super::SetupPlayerInputComponent(PlayerInputComponent);

	UEnhancedInputComponent* EnhancedInput = Cast<UEnhancedInputComponent>(PlayerInputComponent);
	if (!EnhancedInput)
	{
		UE_LOG(LogOneBossFight, Error, TEXT("Enhanced Input is required; set the project's default input component class to EnhancedInputComponent."));
		return;
	}

	if (MoveAction)
	{
		EnhancedInput->BindAction(MoveAction, ETriggerEvent::Triggered, this, &ARPGPlayerCharacter::Move);
	}
	if (LookAction)
	{
		EnhancedInput->BindAction(LookAction, ETriggerEvent::Triggered, this, &ARPGPlayerCharacter::Look);
	}
	if (JumpAction)
	{
		EnhancedInput->BindAction(JumpAction, ETriggerEvent::Started, this, &ACharacter::Jump);
		EnhancedInput->BindAction(JumpAction, ETriggerEvent::Completed, this, &ACharacter::StopJumping);
	}
	if (SprintAction)
	{
		EnhancedInput->BindAction(SprintAction, ETriggerEvent::Started, this, &ARPGPlayerCharacter::StartSprint);
		EnhancedInput->BindAction(SprintAction, ETriggerEvent::Completed, this, &ARPGPlayerCharacter::StopSprint);
	}
	if (LightAttackAction)
	{
		EnhancedInput->BindAction(LightAttackAction, ETriggerEvent::Started, this, &ARPGPlayerCharacter::LightAttack);
	}
	if (HeavyAttackAction)
	{
		EnhancedInput->BindAction(HeavyAttackAction, ETriggerEvent::Started, this, &ARPGPlayerCharacter::HeavyAttack);
	}
	if (DodgeAction)
	{
		EnhancedInput->BindAction(DodgeAction, ETriggerEvent::Started, this, &ARPGPlayerCharacter::Dodge);
	}
	if (LockOnAction)
	{
		EnhancedInput->BindAction(LockOnAction, ETriggerEvent::Started, this, &ARPGPlayerCharacter::ToggleLockOn);
	}
}

bool ARPGPlayerCharacter::CanJumpInternal_Implementation() const
{
	return Super::CanJumpInternal_Implementation() && GetCombat()->CanMove();
}

void ARPGPlayerCharacter::Move(const FInputActionValue& Value)
{
	// Attacks, rolls and staggers own the character's movement.
	if (!Controller || !GetCombat()->CanMove())
	{
		return;
	}

	const FVector2D Axis = Value.Get<FVector2D>();

	// Camera-relative: move along the controller's yaw only, ignoring pitch.
	const FRotator YawRotation(0.f, Controller->GetControlRotation().Yaw, 0.f);
	const FRotationMatrix YawMatrix(YawRotation);

	AddMovementInput(YawMatrix.GetUnitAxis(EAxis::X), Axis.Y);
	AddMovementInput(YawMatrix.GetUnitAxis(EAxis::Y), Axis.X);
}

void ARPGPlayerCharacter::Look(const FInputActionValue& Value)
{
	const FVector2D Axis = Value.Get<FVector2D>();

	// While locked on, a mouse flick switches targets instead of moving the camera.
	if (TargetLock->HandleLookInput(Axis.X))
	{
		return;
	}

	AddControllerYawInput(Axis.X * LookSensitivity);
	AddControllerPitchInput(Axis.Y * LookSensitivity);
}

void ARPGPlayerCharacter::LightAttack()
{
	GetCombat()->RequestLightAttack();
}

void ARPGPlayerCharacter::HeavyAttack()
{
	GetCombat()->RequestHeavyAttack();
}

void ARPGPlayerCharacter::Dodge()
{
	// Dodge along the held movement direction; with no input the combat component steps backward.
	GetCombat()->RequestDodge(GetCharacterMovement()->GetCurrentAcceleration());
}

void ARPGPlayerCharacter::ToggleLockOn()
{
	TargetLock->ToggleLock();
}

void ARPGPlayerCharacter::StartSprint()
{
	if (GetAttributes()->GetStamina() <= 0.f)
	{
		return;
	}
	bSprinting = true;
	GetCharacterMovement()->MaxWalkSpeed = SprintSpeed;
}

void ARPGPlayerCharacter::StopSprint()
{
	bSprinting = false;
	GetCharacterMovement()->MaxWalkSpeed = WalkSpeed;
	GetAttributes()->SetStaminaDrain(0.f);
}

void ARPGPlayerCharacter::HandleStaminaDepleted()
{
	StopSprint();
}

void ARPGPlayerCharacter::HandleDeath()
{
	Super::HandleDeath();
	StopSprint();
	TargetLock->ClearTarget();
}

void ARPGPlayerCharacter::ResetCombatant()
{
	Super::ResetCombatant();
	StopSprint();
	TargetLock->ClearTarget();
}
