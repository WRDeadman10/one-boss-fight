// Copyright One Boss Fight. All Rights Reserved.

#pragma once

#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "RPGBossEncounter.generated.h"

/**
 * Encounter flow for the pack's boss: a beginning (the gate) and a reset.
 *   - Dormant: the boss stands at home with its behaviour held (the AI controller exists, the pack's abilities were granted at BeginPlay) until the player comes within
 *     GateRadius or hurts it. Then its behaviour runs and the pack's tree takes over (it equips its weapon and attacks).
 *   - Reset: when the player has a new pawn (death and respawn) the boss is made to forget: any stance break is aborted, its behaviour held, its target and combat state
 *     cleared, perception forgotten, montages and movement stopped, it is moved back to where the level placed it, health and poise are full, and it is dormant again.
 * The pack resets the boss's health and poise at a respawn by itself but leaves it where it stood, still in combat; this finishes the job.
 * Attached to the pack boss by RPGPlayerMovesSubsystem; no pack asset is edited.
 */
UCLASS(ClassGroup = (Boss))
class ONEBOSSFIGHT_API URPGBossEncounter : public UActorComponent
{
	GENERATED_BODY()

public:
	URPGBossEncounter();

	/** The boss sleeps until the player is this close (cm, horizontal) or damages it. 0 = no gate (it fights at once as the pack does). */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Encounter", meta = (ClampMin = "0"))
	float GateRadius = 1200.f;

	/** Test drivers only: while true a dormant boss never wakes (not by distance and not by damage), so a scripted attack can be played at close range without the pack AI joining in. */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Encounter")
	bool bTestFreeze = false;

	/** Move the boss back to its start and make it dormant when the player respawns. */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Encounter")
	bool bResetOnPlayerRespawn = true;

	/** The boss's maximum (and starting) health (M14, owner 2026-10-23: a 2 to 4 minute duel; the pack's own value is 500). Applied once at the start and kept by every reset (a reset refills to the maximum). 0 or less = the pack's value. */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Encounter")
	float BossMaxHealth = 2000.f;

	UFUNCTION(BlueprintPure, Category = "Encounter")
	bool IsDormant() const { return bDormant; }

	UFUNCTION(BlueprintPure, Category = "Encounter")
	int32 GetResetCount() const { return ResetCount; }

	/** Resets refused because the boss was dying (a dead boss stays dead; the pack destroys it a few seconds after the death); tests. */
	UFUNCTION(BlueprintPure, Category = "Encounter")
	int32 GetDeathResetRefusals() const { return DeathResetRefusals; }

	/**
	 * Encounter generation (Freeze 32.2). Starts at 1 and goes up on every reset. A timer, montage callback or projectile that outlives the fight it was made for stores the generation
	 * it started in and drops itself when this value has changed (IsCurrentGeneration).
	 */
	UFUNCTION(BlueprintPure, Category = "Encounter")
	int32 GetGeneration() const { return Generation; }

	UFUNCTION(BlueprintPure, Category = "Encounter")
	bool IsCurrentGeneration(int32 Token) const { return Token == Generation; }

	UFUNCTION(BlueprintPure, Category = "Encounter")
	FTransform GetHomeTransform() const { return HomeTransform; }

	/** Test drivers only: stops (true) or resumes (false) the pack's behaviour of an awake boss, keeping its weapon drawn. While stopped it only does what a test starts (StartMove). */
	UFUNCTION(BlueprintCallable, Category = "Encounter")
	void HoldForTest(bool bHold);

	/** Tests: runs the encounter reset as if the player had died and respawned. */
	UFUNCTION(BlueprintCallable, Category = "Encounter")
	void ResetForTest();

	/** Wakes the boss now (tests and scripted encounters). */
	UFUNCTION(BlueprintCallable, Category = "Encounter")
	void Wake();

protected:
	virtual void BeginPlay() override;
	virtual void TickComponent(float DeltaTime, ELevelTick TickType, FActorComponentTickFunction* ThisTickFunction) override;

private:
	void Sleep();
	void ResetEncounter();
	/** Stops the pack's behaviour (tree, perception reactions) while the boss sleeps; keeps the AI controller so the abilities granted at BeginPlay stay valid. Returns false until the controller's behaviour exists. */
	bool HoldBehaviour();
	void ResumeBehaviour();

	FTransform HomeTransform;
	bool bDormant = false;
	bool bHeld = false;
	bool bWantsHold = false;
	int32 ResetCount = 0;
	bool bMaxHealthApplied = false;
	float StartupTime = 0.f; // seconds since BeginPlay: the pack finishes its own attribute set-up a moment after the first write (probe 2026-10-23: current health read 500 half a second after the write of 2000)
	static constexpr float StartupEnforceSeconds = 4.f;
	int32 DeathResetRefusals = 0;
	int32 Generation = 1;
	float DormantTime = 0.f;
	double HealthBaseline = -1.0;
	TWeakObjectPtr<const APawn> TrackedPlayer;
};
