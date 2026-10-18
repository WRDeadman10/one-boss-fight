// Copyright One Boss Fight. All Rights Reserved.

#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Character.h"
#include "RPGCharacterBase.generated.h"

class UAnimMontage;
class URPGAttributeComponent;
class URPGCombatComponent;
class URPGMeleeTraceComponent;

/**
 * Shared base for the player, bosses and training dummies: owns the attribute, combat and melee-trace
 * components and the montages the combat state machine plays (hit reaction, death, dodge).
 */
UCLASS(Abstract)
class ONEBOSSFIGHT_API ARPGCharacterBase : public ACharacter
{
	GENERATED_BODY()

public:
	ARPGCharacterBase();

	URPGAttributeComponent* GetAttributes() const { return Attributes; }
	URPGCombatComponent* GetCombat() const { return Combat; }
	URPGMeleeTraceComponent* GetMeleeTrace() const { return MeleeTrace; }

	UAnimMontage* GetHitReactMontage() const { return HitReactMontage; }
	UAnimMontage* GetDeathMontage() const { return DeathMontage; }
	UAnimMontage* GetDodgeMontage() const { return DodgeMontage; }

	/** Full retry/reset: health, stamina, poise, combat state, collision and animation. */
	UFUNCTION(BlueprintCallable, Category = "Combat")
	virtual void ResetCombatant();

protected:
	virtual void BeginPlay() override;

	/** Death hook; the base disables collision so a corpse is not hit again. Override for ragdoll, loot, etc. */
	UFUNCTION()
	virtual void HandleDeath();

	UPROPERTY(EditDefaultsOnly, Category = "Combat|Animation")
	TObjectPtr<UAnimMontage> HitReactMontage;

	UPROPERTY(EditDefaultsOnly, Category = "Combat|Animation")
	TObjectPtr<UAnimMontage> DeathMontage;

	UPROPERTY(EditDefaultsOnly, Category = "Combat|Animation")
	TObjectPtr<UAnimMontage> DodgeMontage;

private:
	UPROPERTY(VisibleAnywhere, Category = "Combat")
	TObjectPtr<URPGAttributeComponent> Attributes;

	UPROPERTY(VisibleAnywhere, Category = "Combat")
	TObjectPtr<URPGCombatComponent> Combat;

	UPROPERTY(VisibleAnywhere, Category = "Combat")
	TObjectPtr<URPGMeleeTraceComponent> MeleeTrace;
};
