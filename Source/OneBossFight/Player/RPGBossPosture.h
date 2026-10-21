// Copyright One Boss Fight. All Rights Reserved.

#pragma once

#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "RPGBossPosture.generated.h"

/**
 * (Regeneration note: the pack's own regeneration of this attribute is disabled at runtime and done here, because its timer never restarted reliably for the boss in tests.)
 * Boss posture (Master Design Freeze 17, Layer A): a hidden 100 point pool that player hits drain and that refills on its own.
 * The pool is the pack's poise attribute on the boss (Attribute.Poise, maximum 100; the pack's hit reaction gate already subtracts it per hit and at zero starts the hit stun that
 * URPGBossStagger turns into the stance break). This component owns the part the Freeze defines and the pack does not:
 *   - regeneration: starts RegenDelaySeconds after the last drain and then adds RegenPerSecond (the attribute's own regen timer is set to these values at runtime);
 *   - bookkeeping for tests and the debug overlay: posture, drain events, time since the last drain;
 *   - boss attacks never drain it (the pack only subtracts poise from the victim of a hit: the boss is never the victim of its own attacks).
 * The drain per hit is still the pack gate's number (20 light, 50 heavy); per weapon values (Freeze 20: 18 and 38 strength, 6 dex) come with the build work (TASKS G3-1).
 */
UCLASS(ClassGroup = (Boss))
class ONEBOSSFIGHT_API URPGBossPosture : public UActorComponent
{
	GENERATED_BODY()

public:
	URPGBossPosture();

	/** Seconds after the last drain before posture starts to come back (Freeze 17.2: 6.0). */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Posture", meta = (ClampMin = "0.0"))
	float RegenDelaySeconds = 6.f;

	/** Points per second once it regenerates (Freeze 17.2: 13). */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Posture", meta = (ClampMin = "0.0"))
	float RegenPerSecond = 13.f;

	UFUNCTION(BlueprintPure, Category = "Posture")
	float GetPosture() const { return Posture; }

	UFUNCTION(BlueprintPure, Category = "Posture")
	float GetMaxPosture() const { return MaxPosture; }

	/** Number of drains seen (a hit that lowered posture) and the world time of the last one. */
	UFUNCTION(BlueprintPure, Category = "Posture")
	int32 GetDrainCount() const { return DrainCount; }

	UFUNCTION(BlueprintPure, Category = "Posture")
	double GetLastDrainTime() const { return LastDrainTime; }

	/** True when the regeneration settings were written to the attribute. */
	UFUNCTION(BlueprintPure, Category = "Posture")
	bool IsConfigured() const { return bConfigured; }

	/** Hold policy (SPEC M4, Freeze 713 and 766): during a stance break the pool is held at 0 (more hits are ignored and counted, the pack's gate would otherwise refill it and cycle it); during the phase
	 *  transition it is pinned at the value it had (posture is paused). None = normal. */
	enum class EHold : uint8 { None, Zero, Pinned };

	/** Zero writes 0 now; Pinned keeps the current value. Does nothing when a hold is already running. */
	void BeginHold(EHold Mode);

	/** Ends the hold. bRefill writes the maximum (end of the get-up, Freeze 714). Regeneration waits RegenDelaySeconds after this call. No-op when nothing is held. */
	void EndHold(bool bRefill);

	UFUNCTION(BlueprintPure, Category = "Posture")
	FString GetHoldName() const;

	/** Hits that were written back to the held value (ignored posture damage). */
	UFUNCTION(BlueprintPure, Category = "Posture")
	int32 GetSuppressedDrainCount() const { return SuppressedDrains; }

protected:
	virtual void TickComponent(float DeltaTime, ELevelTick TickType, FActorComponentTickFunction* ThisTickFunction) override;

private:
	/** Writes RegenDelaySeconds and RegenPerSecond into the boss's poise attribute object (a Blueprint instance) by reflection. */
	bool ConfigureAttribute();

	EHold Hold = EHold::None;
	float HeldValue = 0.f;
	int32 SuppressedDrains = 0;
	float Posture = -1.f;
	float MaxPosture = 100.f;
	int32 DrainCount = 0;
	double LastDrainTime = -1.0;
	bool bConfigured = false;
};
