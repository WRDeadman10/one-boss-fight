// Copyright One Boss Fight. All Rights Reserved.

#pragma once

#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "Pack/RPGPackTrace.h"
#include "RPGTraceGuard.generated.h"

/**
 * Enforcement around the pack's weapon trace on the boss (SPEC M1, Freeze 13.1 items 8 and 9, 12.2, 13.2 walls). The pack's trace (ANS_CollisionTrace -> BP_SweepingSocketTraceTarget) is left as it is; this component does the three
 * things the pack does not:
 *   1. closes the trace at once when the boss is interrupted by something that is not a notify end (stance break, phase transition, encounter reset, death), by calling the pack's own DeactivateCollisionByTag;
 *   2. keeps the hit set across the windows of one attack instance (the A2 stand-in opens two windows in one swing: one damage event per instance, Freeze 12.2);
 *   3. stops a hit through a wall: while a line from the boss to the player is blocked by arena geometry the player is put into the hit set for one pack sample (a temporary seed that is removed again before the next check),
 *      so the pack's own filter rejects the contact.
 * It runs after the boss's animation update and before the pack's sample of the same frame. Nothing is written to a pack asset. Attached by RPGPlayerMovesSubsystem.
 */
UCLASS(ClassGroup = (Boss))
class ONEBOSSFIGHT_API URPGTraceGuard : public UActorComponent
{
	GENERATED_BODY()

public:
	URPGTraceGuard();

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Trace")
	bool bEnabled = true;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Trace")
	FName TargetTypeTag = TEXT("TargetType.MainWeapon");

	/** CloseTraceNow acts on a stance break, a phase transition, an encounter reset and the boss's death. */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Trace")
	bool bCloseOnInterrupt = true;

	/** Arena geometry between the boss and the player blocks the pack's trace (Freeze 560). Off = the pack's original behaviour (measurements). */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Trace")
	bool bBlockThroughWalls = true;

	/** The hit set is carried from one trace window to the next while the attack instance is the same (Freeze 12.2). */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Trace")
	bool bDedupePerInstance = true;

	/** Ends the pack trace now. Reason "reset" also clears the hit set. Idempotent; never opens a trace. */
	UFUNCTION(BlueprintCallable, Category = "Trace")
	void CloseTraceNow(FName Reason);

	/** The guard of this boss closes its trace (no-op when the boss has none). Called by the interrupt owners. */
	static void CloseFor(AActor* Boss, FName Reason);

	UFUNCTION(BlueprintPure, Category = "Trace")
	bool IsPackTraceActive() const;

	/** True while this actor sits in the pack's hit set only because the wall gate put it there for one sample (the audit must not count that as a hit). */
	bool IsSeed(const AActor* Actor) const { return Actor && TempSeed.Get() == Actor; }

	/** The actors this guard put into the pack's hit set at the last window open (the carry of the same attack instance): the audit does not count them as hits. */
	const TArray<TWeakObjectPtr<AActor>>& GetCarriedAtOpen() const { return OpenCarried; }

	UFUNCTION(BlueprintPure, Category = "Trace")
	int32 GetCloseCount() const { return CloseCount; }

	UFUNCTION(BlueprintPure, Category = "Trace")
	int32 GetOccludedSampleCount() const { return OccludedSamples; }

	UFUNCTION(BlueprintPure, Category = "Trace")
	int32 GetCarryCount() const { return CarryCount; }

	UFUNCTION(BlueprintPure, Category = "Trace")
	int32 GetWindowCount() const { return WindowId; }

	/** Largest distance between a socket's stored previous position and its current position at the last window open (cm): 0 proves the pack refreshed the previous positions at the open (Freeze 549). */
	UFUNCTION(BlueprintPure, Category = "Trace")
	float GetOpenRefreshErrorCm() const { return OpenRefreshError; }

	/** True when the pack's trace object and the names the guard needs were found. */
	UFUNCTION(BlueprintPure, Category = "Trace")
	bool IsResolved() const { return Target.IsValid(); }

	/** The pack names (variables and functions of the live trace object) that were not found; "" when all are there. For the pre-flight check of the drivers and the content wiring test. */
	UFUNCTION(BlueprintCallable, Category = "Trace")
	FString GetMissingPackNames() const;

protected:
	virtual void BeginPlay() override;
	virtual void TickComponent(float DeltaTime, ELevelTick TickType, FActorComponentTickFunction* ThisTickFunction) override;

private:
	RPGPackTrace::FTarget Target;
	TWeakObjectPtr<AActor> TempSeed;
	int32 SeedWindow = 0;
	TArray<TWeakObjectPtr<AActor>> LastSet;
	TArray<TWeakObjectPtr<AActor>> OpenCarried;
	bool bWasActive = false;
	int32 WindowId = 0;
	int32 LastWindowInstance = -1;
	int32 CloseCount = 0;
	int32 OccludedSamples = 0;
	int32 CarryCount = 0;
	float OpenRefreshError = 0.f;
};
