// Copyright One Boss Fight. All Rights Reserved.

#pragma once

#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "Combat/RPGCombatTypes.h"
#include "RPGMeleeTraceComponent.generated.h"

class URPGCombatComponent;
class USceneComponent;

DECLARE_DYNAMIC_MULTICAST_DELEGATE_TwoParams(FRPGTargetHitSignature, AActor*, Target, const FRPGHitResult&, Result);

/**
 * Damage detection for melee attacks.
 *
 * While the combat component's hit window is open, every frame this sweeps spheres from each sample point's
 * previous position to its current one along the weapon's base-to-tip line, so a fast swing cannot skip over a
 * target between frames at any frame rate. A target is hit at most once per swing (one hit window); the hit
 * is delivered through URPGCombatComponent::ProcessIncomingHit, the only damage path.
 */
UCLASS(ClassGroup = (Combat), meta = (BlueprintSpawnableComponent))
class ONEBOSSFIGHT_API URPGMeleeTraceComponent : public UActorComponent
{
	GENERATED_BODY()

public:
	URPGMeleeTraceComponent();

	/** Used when the weapon data names no sockets: a sphere this far in front of the owner. */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Trace", meta = (ClampMin = "0"))
	float FallbackReach = 100.f;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Trace", meta = (ClampMin = "1"))
	float FallbackRadius = 50.f;

	UPROPERTY(BlueprintAssignable, Category = "Combat")
	FRPGTargetHitSignature OnTargetHit;

	bool IsSwinging() const { return bSwinging; }

	/** Starts a swing: forgets previous victims and arms the per-frame sweep. Template carries damage values. */
	void BeginSwing(const FRPGHitInfo& Template);

	/** Disarms the sweep. The hit list stays readable until the next swing. */
	void EndSwing();

	/**
	 * Sweeps a sphere from Start to End and applies a hit to every combatant not yet hit this swing and not on
	 * the owner's team. Returns how many were newly hit. Exposed so tests can drive exact frame steps.
	 */
	int32 ProcessSweep(const FVector& Start, const FVector& End, float Radius);

	const TSet<TWeakObjectPtr<AActor>>& GetHitActors() const { return HitActors; }

protected:
	virtual void OnRegister() override;
	virtual void OnUnregister() override;
	virtual void TickComponent(float DeltaTime, ELevelTick TickType, FActorComponentTickFunction* ThisTickFunction) override;

private:
	void HandleHitWindowChanged(bool bOpen);

	/** Current sample points on the weapon line and the sweep radius. False if nothing could be resolved. */
	bool GetSamplePoints(TArray<FVector, TInlineAllocator<8>>& OutPoints, float& OutRadius) const;
	USceneComponent* ResolveTraceComponent() const;

	bool bSwinging = false;
	bool bHavePrevious = false;
	FRPGHitInfo SwingTemplate;
	TArray<FVector, TInlineAllocator<8>> PreviousPoints;
	TSet<TWeakObjectPtr<AActor>> HitActors;
	TWeakObjectPtr<URPGCombatComponent> BoundCombat;
};
