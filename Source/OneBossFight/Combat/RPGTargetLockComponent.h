// Copyright One Boss Fight. All Rights Reserved.

#pragma once

#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "RPGTargetLockComponent.generated.h"

DECLARE_DYNAMIC_MULTICAST_DELEGATE_OneParam(FRPGTargetLockChangedSignature, AActor*, NewTarget);

/**
 * Soulslike lock-on for the player. Toggling picks the living enemy closest to the screen center that is in
 * range and in line of sight. While locked the controller (and so the camera) turns toward the target and
 * the body strafes facing it; a mouse flick switches to the next target left or right. The lock breaks when
 * the target dies, leaves BreakDistance, or is hidden behind geometry.
 */
UCLASS(ClassGroup = (Combat), meta = (BlueprintSpawnableComponent))
class ONEBOSSFIGHT_API URPGTargetLockComponent : public UActorComponent
{
	GENERATED_BODY()

public:
	URPGTargetLockComponent();

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Lock On", meta = (ClampMin = "0"))
	float MaxLockDistance = 2500.f;

	/** The lock breaks beyond this distance. Larger than MaxLockDistance so it does not flicker at the edge. */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Lock On", meta = (ClampMin = "0"))
	float BreakDistance = 3200.f;

	/** Height above the target's origin that the camera aims at. */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Lock On")
	float TargetHeightOffset = 120.f;

	/** Height above the owner's origin the camera orbits (matches the camera boom offset). */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Lock On")
	float PivotHeightOffset = 60.f;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Lock On", meta = (ClampMin = "0"))
	float CameraInterpSpeed = 10.f;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Lock On")
	float MinLockPitch = -30.f;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Lock On")
	float MaxLockPitch = 30.f;

	/** Raw mouse X delta in one frame that counts as a flick to switch targets. */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Lock On", meta = (ClampMin = "0"))
	float SwitchFlickThreshold = 6.f;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Lock On", meta = (ClampMin = "0"))
	float SwitchCooldown = 0.35f;

	UPROPERTY(BlueprintAssignable, Category = "Lock On")
	FRPGTargetLockChangedSignature OnTargetChanged;

	UFUNCTION(BlueprintPure, Category = "Lock On")
	bool IsLocked() const { return LockedTarget.IsValid(); }

	UFUNCTION(BlueprintPure, Category = "Lock On")
	AActor* GetTarget() const { return LockedTarget.Get(); }

	/** Locks the best target, or releases the current one. Returns true if now locked. */
	UFUNCTION(BlueprintCallable, Category = "Lock On")
	bool ToggleLock();

	UFUNCTION(BlueprintCallable, Category = "Lock On")
	void ClearTarget();

	/** Moves the lock to the neighbor on that side (positive = right). Returns true if the target changed. */
	UFUNCTION(BlueprintCallable, Category = "Lock On")
	bool SwitchTarget(float Direction);

	/** Feed mouse X while locked. Returns true when locked, meaning the camera must not also use it. */
	bool HandleLookInput(float AxisX);

	/** Index of the point closest to the view direction, or INDEX_NONE. Pure, for tests. */
	static int32 ChooseByViewAlignment(const FVector& ViewOrigin, const FVector& ViewForward, const TArray<FVector>& Points);

	/** Index of the nearest point on one side of the current one as seen from ViewOrigin, or INDEX_NONE. Pure, for tests. */
	static int32 ChooseBySide(const FVector& ViewOrigin, const FVector& CurrentPoint, const TArray<FVector>& Points, float Direction);

protected:
	virtual void TickComponent(float DeltaTime, ELevelTick TickType, FActorComponentTickFunction* ThisTickFunction) override;

private:
	struct FCandidate
	{
		AActor* Actor = nullptr;
		FVector Point = FVector::ZeroVector;
	};

	void GatherCandidates(TArray<FCandidate>& OutCandidates) const;
	bool IsValidTarget(const AActor* Target, float MaxDistance) const;
	FVector GetTargetPoint(const AActor* Target) const;
	FVector GetViewOrigin() const;
	void SetTarget(AActor* NewTarget);
	void ApplyBodyOrientation(bool bLocked) const;

	TWeakObjectPtr<AActor> LockedTarget;
	float TimeSinceSwitch = 100.f;
};
