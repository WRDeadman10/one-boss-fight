// Copyright One Boss Fight. All Rights Reserved.

#pragma once

#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "RPGAttributeComponent.generated.h"

DECLARE_DYNAMIC_MULTICAST_DELEGATE_ThreeParams(FRPGAttributeChangedSignature, float, Current, float, Max, float, Delta);
DECLARE_DYNAMIC_MULTICAST_DELEGATE(FRPGAttributeEventSignature);

/**
 * Health, stamina and poise for one combatant. This is the only place those values change.
 *
 * - Stamina: spent by actions, regenerates after a delay, can also drain continuously (sprint).
 * - Poise: depleted by hits; reaching zero is a "poise break" (reported to the caller, then refilled),
 *   and it refills after a quiet period.
 *
 * Time is advanced by TickAttributes(), so behavior is deterministic and testable without a running world.
 * The component only ticks while something needs updating.
 */
UCLASS(ClassGroup = (Combat), meta = (BlueprintSpawnableComponent))
class ONEBOSSFIGHT_API URPGAttributeComponent : public UActorComponent
{
	GENERATED_BODY()

public:
	URPGAttributeComponent();

	// ---- Configuration -------------------------------------------------------------------

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Attributes", meta = (ClampMin = "1"))
	float MaxHealth = 100.f;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Attributes", meta = (ClampMin = "1"))
	float MaxStamina = 100.f;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Attributes", meta = (ClampMin = "1"))
	float MaxPoise = 40.f;

	/** Stamina regained per second once the regen delay has passed. */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Attributes", meta = (ClampMin = "0"))
	float StaminaRegenPerSecond = 40.f;

	/** Seconds after the last stamina use before regeneration starts. */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Attributes", meta = (ClampMin = "0"))
	float StaminaRegenDelay = 0.8f;

	/** Seconds after the last poise damage before poise is fully restored. */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Attributes", meta = (ClampMin = "0"))
	float PoiseResetDelay = 4.f;

	// ---- Queries -------------------------------------------------------------------------

	UFUNCTION(BlueprintPure, Category = "Attributes")
	float GetHealth() const;

	UFUNCTION(BlueprintPure, Category = "Attributes")
	float GetStamina() const;

	UFUNCTION(BlueprintPure, Category = "Attributes")
	float GetPoise() const;

	UFUNCTION(BlueprintPure, Category = "Attributes")
	float GetHealthFraction() const { return GetHealth() / MaxHealth; }

	UFUNCTION(BlueprintPure, Category = "Attributes")
	float GetStaminaFraction() const { return GetStamina() / MaxStamina; }

	UFUNCTION(BlueprintPure, Category = "Attributes")
	bool IsDead() const { return bDead; }

	// ---- Mutation (the single authoritative path) ----------------------------------------

	/** Reduces health. Returns the damage actually applied (clamped to remaining health). Broadcasts OnDeath once. */
	UFUNCTION(BlueprintCallable, Category = "Attributes")
	float ApplyDamage(float Amount);

	/** Restores health, up to the maximum. Does nothing when dead. */
	UFUNCTION(BlueprintCallable, Category = "Attributes")
	void Heal(float Amount);

	/**
	 * Spends stamina for an action. Souls-style rule: the action is allowed whenever stamina is above zero,
	 * even if the cost exceeds what is left (stamina then drops to zero). Fails only at zero stamina.
	 * A cost of zero or less always succeeds.
	 */
	UFUNCTION(BlueprintCallable, Category = "Attributes")
	bool TryConsumeStamina(float Cost);

	/** Spends stamina unconditionally (blocking a hit). Returns true if stamina is now zero. */
	UFUNCTION(BlueprintCallable, Category = "Attributes")
	bool ForceConsumeStamina(float Amount);

	/** Removes poise. Returns true on a poise break: poise is then refilled and the caller should stagger. */
	UFUNCTION(BlueprintCallable, Category = "Attributes")
	bool ApplyPoiseDamage(float Amount);

	/** Continuous stamina drain in units per second (sprint). Zero stops it. Ends at zero stamina with OnStaminaDepleted. */
	UFUNCTION(BlueprintCallable, Category = "Attributes")
	void SetStaminaDrain(float PerSecond);

	/** Restores every value to its maximum and clears death. Used for retry and for the training dummy. */
	UFUNCTION(BlueprintCallable, Category = "Attributes")
	void ResetAttributes();

	/** Advances regeneration, drain and poise reset. Called by the component tick; callable directly in tests. */
	void TickAttributes(float DeltaTime);

	// ---- Events --------------------------------------------------------------------------

	UPROPERTY(BlueprintAssignable, Category = "Attributes")
	FRPGAttributeChangedSignature OnHealthChanged;

	UPROPERTY(BlueprintAssignable, Category = "Attributes")
	FRPGAttributeChangedSignature OnStaminaChanged;

	UPROPERTY(BlueprintAssignable, Category = "Attributes")
	FRPGAttributeChangedSignature OnPoiseChanged;

	UPROPERTY(BlueprintAssignable, Category = "Attributes")
	FRPGAttributeEventSignature OnDeath;

	UPROPERTY(BlueprintAssignable, Category = "Attributes")
	FRPGAttributeEventSignature OnStaminaDepleted;

protected:
	virtual void TickComponent(float DeltaTime, ELevelTick TickType, FActorComponentTickFunction* ThisTickFunction) override;

private:
	/** Current values start at the maximums the first time they are read, so per-instance Max overrides are honored. */
	void EnsureInitialized() const;
	void SetStamina(float NewValue);
	void SetPoise(float NewValue);
	bool NeedsTick() const;
	void RefreshTickState();

	mutable bool bInitialized = false;
	mutable float Health = 0.f;
	mutable float Stamina = 0.f;
	mutable float Poise = 0.f;

	bool bDead = false;
	float StaminaDrainPerSecond = 0.f;
	float TimeSinceStaminaUse = 0.f;
	float TimeSincePoiseDamage = 0.f;
};
