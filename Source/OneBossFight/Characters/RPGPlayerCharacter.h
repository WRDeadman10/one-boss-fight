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

/**
 * Player character: camera-relative movement, sprint, jump and look through Enhanced Input.
 * Input assets are assigned on a Blueprint subclass; no key is hardcoded here.
 */
UCLASS()
class ONEBOSSFIGHT_API ARPGPlayerCharacter : public ARPGCharacterBase
{
	GENERATED_BODY()

public:
	ARPGPlayerCharacter();

	USpringArmComponent* GetCameraBoom() const { return CameraBoom; }
	UCameraComponent* GetFollowCamera() const { return FollowCamera; }

	/** True while sprint input is held. Stamina gating is added with the combat milestone. */
	UFUNCTION(BlueprintPure, Category = "Movement")
	bool IsSprinting() const { return bSprinting; }

	UFUNCTION(BlueprintCallable, Category = "Movement")
	void StartSprint();

	UFUNCTION(BlueprintCallable, Category = "Movement")
	void StopSprint();

protected:
	virtual void SetupPlayerInputComponent(UInputComponent* PlayerInputComponent) override;
	virtual void PawnClientRestart() override;

	void Move(const FInputActionValue& Value);
	void Look(const FInputActionValue& Value);

	/** Jog speed in cm/s. */
	UPROPERTY(EditDefaultsOnly, Category = "Movement", meta = (ClampMin = "0"))
	float WalkSpeed = 400.f;

	/** Sprint speed in cm/s. */
	UPROPERTY(EditDefaultsOnly, Category = "Movement", meta = (ClampMin = "0"))
	float SprintSpeed = 650.f;

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

private:
	UPROPERTY(VisibleAnywhere, Category = "Camera")
	TObjectPtr<USpringArmComponent> CameraBoom;

	UPROPERTY(VisibleAnywhere, Category = "Camera")
	TObjectPtr<UCameraComponent> FollowCamera;

	bool bSprinting = false;
};
