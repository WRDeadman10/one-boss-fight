// Copyright One Boss Fight. All Rights Reserved.

#pragma once

#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "Engine/EngineTypes.h"
#include "RPGCameraRig.generated.h"

class USpringArmComponent;
class UCameraComponent;
class UCapsuleComponent;

/**
 * Camera set-up of the pack player (a spring arm "CameraBoom" with a "FollowCamera", both inside BP_CombatPlayerCharacter). The pack's camera has four weaknesses that let it end up in the ground:
 *   1. Probe size 12 cm: the camera centre may sit 12 cm over a surface, which is inside the camera's near clip distance, so the floor cuts through the picture. A bigger probe keeps the lens clear.
 *   2. No pitch limit (the camera manager allows +-89.9 degrees): looking up swings the arm down into the floor, the spring arm collision pulls the camera in to 90 cm and the view ends up in the player's belly.
 *   3. Camera lag with no distance limit: the lagged arm origin can trail far behind (and below) a fast moving player, and the collision sweep starts from that lagged origin.
 *   4. The boom is attached to the animated skeletal mesh, not to the capsule: when the pack ragdolls the mesh (death) the pivot falls with it to the floor.
 * This component applies the settings once the player exists (no pack asset is edited), moves the boom onto the capsule at the same place, and keeps the pitch limits. The spring arm's own collision stays the only
 * obstruction handling (no second correction fights it). rpg.CameraDebug 1 draws the pivot, the camera, the arm and the clearance below the camera.
 */
UCLASS(ClassGroup = (Camera))
class ONEBOSSFIGHT_API URPGCameraRig : public UActorComponent
{
	GENERATED_BODY()

public:
	URPGCameraRig();

	/** Radius of the sweep from the pivot to the camera (cm). The camera centre never gets closer than this to a surface; keep it above the camera's near clip plane (about 10 cm) with some margin. */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Collision", meta = (ClampMin = "1.0"))
	float ProbeSize = 34.f;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Collision")
	TEnumAsByte<ECollisionChannel> ProbeChannel = ECC_Camera;

	/** Lowest and highest control pitch (degrees; negative looks down). Looking up is limited most, because that swings the camera towards the floor. */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Pitch", meta = (ClampMin = "-89.0", ClampMax = "0.0"))
	float PitchMin = -70.f;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Pitch", meta = (ClampMin = "0.0", ClampMax = "89.0"))
	float PitchMax = 32.f;

	/** Follow lag of the arm origin (higher = tighter) and the farthest it may trail the pivot (cm, 0 = unlimited). */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Follow", meta = (ClampMin = "0.0"))
	float LagSpeed = 10.f;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Follow", meta = (ClampMin = "0.0"))
	float LagMaxDistance = 60.f;

	/** Attach the boom to the capsule (same world place) instead of the animated mesh, so a ragdoll or an animation cannot carry the pivot away. */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Follow")
	bool bAttachBoomToCapsule = true;

	/** Height of the camera centre above the floor straight below it (cm), or a negative number when nothing is below. For tests and the debug view. */
	UFUNCTION(BlueprintPure, Category = "Camera")
	float GetClearanceBelowCamera() const;

	UFUNCTION(BlueprintPure, Category = "Camera")
	bool IsApplied() const { return bApplied; }

protected:
	virtual void BeginPlay() override;
	virtual void TickComponent(float DeltaTime, ELevelTick TickType, FActorComponentTickFunction* ThisTickFunction) override;

private:
	void Apply();
	void ApplyPitchLimits() const;

	UPROPERTY(Transient)
	TObjectPtr<USpringArmComponent> Boom;
	UPROPERTY(Transient)
	TObjectPtr<UCameraComponent> Camera;
	bool bApplied = false;
};
