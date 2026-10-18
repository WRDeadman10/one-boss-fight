// Copyright One Boss Fight. All Rights Reserved.

#pragma once

#include "CoreMinimal.h"
#include "Characters/RPGCharacterBase.h"
#include "InputActionValue.h"
#include "RPGPlayerCharacter.generated.h"

class UCameraComponent;
class USpringArmComponent;
class UInputAction;
class UInputMappingContext;
class URPGTargetLockComponent;

/**
 * Player character: camera-relative movement, sprint, jump, look, and combat input (light/heavy attack,
 * dodge, lock-on) through Enhanced Input. Input assets are assigned on a Blueprint subclass; no key is
 * hardcoded here.
 */
UCLASS()
class ONEBOSSFIGHT_API ARPGPlayerCharacter : public ARPGCharacterBase
{
	GENERATED_BODY()

public:
	ARPGPlayerCharacter();

	USpringArmComponent* GetCameraBoom() const { return CameraBoom; }
	UCameraComponent* GetFollowCamera() const { return FollowCamera; }
	URPGTargetLockComponent* GetTargetLock() const { return TargetLock; }

	/** True while sprint input is held and stamina remains. */
	UFUNCTION(BlueprintPure, Category = "Movement")
	bool IsSprinting() const { return bSprinting; }

	UFUNCTION(BlueprintCallable, Category = "Movement")
	void StartSprint();

	UFUNCTION(BlueprintCallable, Category = "Movement")
	void StopSprint();

	virtual void ResetCombatant() override;

protected:
	virtual void BeginPlay() override;
	virtual void Tick(float DeltaSeconds) override;
	virtual void SetupPlayerInputComponent(UInputComponent* PlayerInputComponent) override;
	virtual void PawnClientRestart() override;
	virtual bool CanJumpInternal_Implementation() const override;
	virtual void HandleDeath() override;

	void Move(const FInputActionValue& Value);
	void Look(const FInputActionValue& Value);
	void LightAttack();
	void HeavyAttack();
	void Dodge();
	void ToggleLockOn();

	UFUNCTION()
	void HandleStaminaDepleted();

	/** Jog speed in cm/s. */
	UPROPERTY(EditDefaultsOnly, Category = "Movement", meta = (ClampMin = "0"))
	float WalkSpeed = 400.f;

	/** Sprint speed in cm/s. */
	UPROPERTY(EditDefaultsOnly, Category = "Movement", meta = (ClampMin = "0"))
	float SprintSpeed = 650.f;

	/** Stamina drained per second while sprinting and moving. */
	UPROPERTY(EditDefaultsOnly, Category = "Movement", meta = (ClampMin = "0"))
	float SprintStaminaPerSecond = 12.f;

	/** Multiplier applied to look input; tune per device. */
	UPROPERTY(EditDefaultsOnly, Category = "Camera", meta = (ClampMin = "0"))
	float LookSensitivity = 1.f;

	UPROPERTY(EditDefaultsOnly, Category = "Camera")
	float MinCameraPitch = -70.f;

	UPROPERTY(EditDefaultsOnly, Category = "Camera")
	float MaxCameraPitch = 50.f;

	UPROPERTY(EditDefaultsOnly, Category = "Input")
	TObjectPtr<UInputMappingContext> DefaultMappingContext;

	/** Axis2D: X = right, Y = forward. */
	UPROPERTY(EditDefaultsOnly, Category = "Input")
	TObjectPtr<UInputAction> MoveAction;

	/**
	 * Axis2D: X = yaw (right positive), Y = pitch (up positive).
	 * Map raw mouse/stick values; do not negate in the mapping context. Requires
	 * bEnableLegacyInputScales=False (see DefaultInput.ini) so the sign is not flipped by the controller.
	 */
	UPROPERTY(EditDefaultsOnly, Category = "Input")
	TObjectPtr<UInputAction> LookAction;

	UPROPERTY(EditDefaultsOnly, Category = "Input")
	TObjectPtr<UInputAction> JumpAction;

	UPROPERTY(EditDefaultsOnly, Category = "Input")
	TObjectPtr<UInputAction> SprintAction;

	UPROPERTY(EditDefaultsOnly, Category = "Input|Combat")
	TObjectPtr<UInputAction> LightAttackAction;

	UPROPERTY(EditDefaultsOnly, Category = "Input|Combat")
	TObjectPtr<UInputAction> HeavyAttackAction;

	UPROPERTY(EditDefaultsOnly, Category = "Input|Combat")
	TObjectPtr<UInputAction> DodgeAction;

	UPROPERTY(EditDefaultsOnly, Category = "Input|Combat")
	TObjectPtr<UInputAction> LockOnAction;

private:
	UPROPERTY(VisibleAnywhere, Category = "Camera")
	TObjectPtr<USpringArmComponent> CameraBoom;

	UPROPERTY(VisibleAnywhere, Category = "Camera")
	TObjectPtr<UCameraComponent> FollowCamera;

	UPROPERTY(VisibleAnywhere, Category = "Combat")
	TObjectPtr<URPGTargetLockComponent> TargetLock;

	bool bSprinting = false;
	bool bSprintWanted = false;
};
