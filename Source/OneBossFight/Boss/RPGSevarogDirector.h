// Copyright One Boss Fight. All Rights Reserved.

#pragma once

#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "Animation/AnimMontage.h"
#include "NiagaraSystem.h"
#include "RPGSevarogDirector.generated.h"

/**
 * Boss director for Sevarog on the Advanced ARPG pack. The pack has no phase logic, no boss entrance gate and no ranged scheduling,
 * so this component adds them without touching the pack's behaviour tree:
 *  - Gate: the pack's behaviour is held (stopped and disabled) until the player comes within GateRadius. The AI controller exists from the start, because the pack's
 *    abilities read it when they are granted at BeginPlay.
 *  - Phase two: at PhaseTwoHealthFraction of max health it activates the roar ability once and speeds the pawn up.
 *  - Reset: when the player respawns after dying, the boss returns home with full health and sleeps again behind the gate.
 *  - Lightning: in phase two it activates the lightning ability now and then when the player is at mid range and the pawn is idle.
 * Everything in the pack is a Blueprint, so health and abilities are reached by calling Blueprint functions by name.
 */
UCLASS(ClassGroup = (Boss), meta = (BlueprintSpawnableComponent))
class ONEBOSSFIGHT_API URPGSevarogDirector : public UActorComponent
{
	GENERATED_BODY()

public:
	URPGSevarogDirector();

	/** The AI controller is only created when the player is this close (cm). 0 = no gate. */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Gate")
	float GateRadius = 1800.f;

	/** Phase two starts at or below this fraction of max health. */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Phase", meta = (ClampMin = "0.0", ClampMax = "1.0"))
	float PhaseTwoHealthFraction = 0.5f;

	/** Walk speed multiplier in phase two. */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Phase", meta = (ClampMin = "1.0"))
	float PhaseTwoSpeedScale = 1.25f;

	/** Roar montage played once on entering phase two (played directly on the mesh: the pack's enter-combat ability cannot restart while in combat). */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Phase")
	TObjectPtr<UAnimMontage> PhaseRoarMontage;

	/** Blueprint ability class (enter combat) activated when the gate opens, so the entrance plays. */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Gate")
	TSubclassOf<UObject> EntranceAbility;

	/** The behaviour stays held this long (seconds) after the entrance starts, so the pack's tree does not cut it off. */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Gate", meta = (ClampMin = "0"))
	float EntranceHoldSeconds = 4.2f;

	/** Blueprint ability class used for the ranged lightning attack (phase two only). */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Lightning")
	TSubclassOf<UObject> LightningAbility;

	/** Ground ring shown at the strike spot from the start of the cast until the bolt lands. */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Lightning")
	TObjectPtr<UNiagaraSystem> StrikeTelegraphEffect;

	/** Thunder effect spawned on the strike spot when the bolt arrives. */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Lightning")
	TObjectPtr<UNiagaraSystem> StrikeBoltEffect;

	/** Class name prefix of the projectile Blueprint the lightning ability fires (it is moved above the strike spot when it spawns). */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Lightning")
	FString StrikeProjectileClassPrefix = TEXT("BP_SevBolt");

	/** Height above the strike spot where the bolt starts (cm). */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Lightning", meta = (ClampMin = "200"))
	float StrikeHeight = 1400.f;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Lightning", meta = (ClampMin = "0.1"))
	float StrikeTelegraphScale = 1.2f;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Lightning")
	float LightningMinRange = 500.f;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Lightning")
	float LightningMaxRange = 1500.f;

	/** Seconds between lightning attempts, random between the two values. */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Lightning")
	FVector2D LightningCooldown = FVector2D(6.f, 10.f);

	/** Gameplay tag of the health attribute in the pack's attribute component. */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Phase")
	FName HealthAttributeTag = TEXT("Attribute.Health");

	/** Starts a lightning strike now (tests and scripted fights), ignoring range, idle and cooldown checks. */
	UFUNCTION(BlueprintCallable, Category = "Lightning")
	bool TriggerLightning();

	UFUNCTION(BlueprintPure, Category = "Phase")
	bool IsPhaseTwo() const { return bPhaseTwo; }

	UFUNCTION(BlueprintPure, Category = "Gate")
	bool IsGateOpen() const { return bGateOpen; }

protected:
	virtual void BeginPlay() override;
	virtual void EndPlay(const EEndPlayReason::Type EndPlayReason) override;
	virtual void TickComponent(float DeltaTime, ELevelTick TickType, FActorComponentTickFunction* ThisTickFunction) override;

private:
	UObject* FindOwnerComponentByClassName(const TCHAR* ClassName);
	bool ReadHealth(float& Current, float& Max);
	bool ActivateAbility(TSubclassOf<UObject> AbilityClass, bool bForce = false);
	void EnterPhaseTwo();
	bool TryLightning(const APawn* Player, bool bIgnoreConditions = false);
	void ResetEncounter();
	/** Stops the pack's behaviour (tree, perception reactions) while the boss sleeps; keeps the AI controller so the abilities granted at BeginPlay stay valid. */
	void HoldBehavior();
	void ReleaseBehavior();
	/** Lets the pack's behaviour run (after the entrance). */
	void ResumeBehavior();
	void OnActorSpawned(AActor* Actor);

	TWeakObjectPtr<const APawn> TrackedPlayer;
	FTransform HomeTransform;
	float BaseWalkSpeed = 0.f;
	bool bGateOpen = false;
	bool bBehaviorHeld = false;
	float EntranceTimer = -1.f;
	FDelegateHandle SpawnHandle;
	FVector StrikeLocation = FVector::ZeroVector;
	float StrikePendingTime = 0.f;
	bool bPhaseTwo = false;
	bool bDead = false;
	float LightningTimer = 0.f;
	float CheckTimer = 0.f;
};
