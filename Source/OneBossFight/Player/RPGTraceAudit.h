// Copyright One Boss Fight. All Rights Reserved.

#pragma once

#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "Pack/RPGPackTrace.h"
#include "RPGTraceAudit.generated.h"

/**
 * Observer of the pack's weapon trace on the boss (SPEC M1, Freeze 489, 550, 917, tests H01 to H11). It changes nothing: each frame it reads the live pack trace object and counts, per trace window and in total,
 * the trace samples, the samples whose sweep overlapped the player (a shadow of the pack's own sphere sweep), the insertions of the player into the pack's hit set, and what happened to each insertion
 * (damage accepted, or rejected for invulnerability or another reason). "Trace overlap" and "damage accepted" are therefore separate numbers (Freeze 489). It also measures the sweep (largest step per frame,
 * speed, the continuity of the pack's stored previous positions), and how many pack samples ran after the boss was interrupted (stance break, phase transition, reset, death, a replaced montage).
 * Counters are read by name (GetCounter) from the PIE drivers and by the overlay. Compiled to nothing in Shipping builds. Attached by RPGPlayerMovesSubsystem.
 */
UCLASS(ClassGroup = (Boss))
class ONEBOSSFIGHT_API URPGTraceAudit : public UActorComponent
{
	GENERATED_BODY()

public:
	URPGTraceAudit();

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Trace")
	bool bEnabled = true;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Trace")
	FName TargetTypeTag = TEXT("TargetType.MainWeapon");

	/** After the player entered the hit set, a health drop inside this many seconds is its damage. */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Trace", meta = (ClampMin = "0.05"))
	float ResolveWindowSeconds = 0.25f;

	/** A single socket step longer than this (cm) counts as a suspect sweep (a teleport or stale data). */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Trace", meta = (ClampMin = "10.0"))
	float SuspectStepCm = 800.f;

	/** Totals since ResetCounters, by name: Windows, Samples, OverlapSamples, SetInsertions, DamageAccepted, DamageTaken, RejectedInvulnerable, RejectedOther, UnattributedDamage, SelfInSet, SelfOverlapSamples, SuspectSweeps,
	 *  PeakStepCm, PeakSpeedCmPerSec, MaxContinuityErrorCm, MaxSocketGapCm, SamplesAfterInterrupt, FramesToClose, DamageAfterInterrupt, WindowsOutsideTracker, WindowsWhileSheathed, WindowsNoAbility,
	 *  OpenRefreshErrorCm (largest at any window open), Sockets, BaseRadius, Modifier, MinDt, MaxDt. */
	UFUNCTION(BlueprintPure, Category = "Trace")
	double GetCounter(FName Name) const;

	/** Counters of one window (1 = the first since ResetCounters, -1 = the last). Same names as GetCounter. */
	UFUNCTION(BlueprintPure, Category = "Trace")
	double GetWindowCounter(int32 Ordinal, FName Name) const;

	/** Counters of one attack instance (the tracker's instance number): Windows, SetInsertions, DamageAccepted, DamageTaken. */
	UFUNCTION(BlueprintPure, Category = "Trace")
	double GetInstanceCounter(int32 Instance, FName Name) const;

	UFUNCTION(BlueprintPure, Category = "Trace")
	int32 GetWindowCount() const { return Windows.Num(); }

	/** One line about a window ("window 1 A3a instance 12: samples 18 overlap 14 ..."), 1-based, -1 = last. */
	UFUNCTION(BlueprintPure, Category = "Trace")
	FString GetWindowSummary(int32 Ordinal) const;

	UFUNCTION(BlueprintPure, Category = "Trace")
	bool IsTraceActive() const { return bActive; }

	UFUNCTION(BlueprintPure, Category = "Trace")
	int32 GetHitSetCount() const { return Target.IsValid() ? Target.GetHitSetNum() : 0; }

	/** True when the pack's trace object was found. */
	UFUNCTION(BlueprintPure, Category = "Trace")
	bool IsResolved() const { return Target.IsValid(); }

	UFUNCTION(BlueprintCallable, Category = "Trace")
	void ResetCounters();

	/** The three overlay lines (Freeze 489, 917). */
	TArray<FString> BuildLines() const;

protected:
	virtual void BeginPlay() override;
	virtual void TickComponent(float DeltaTime, ELevelTick TickType, FActorComponentTickFunction* ThisTickFunction) override;

private:
	struct FWindow
	{
		int32 Ordinal = 0;
		int32 Instance = -1;
		FName Move;
		int32 Generation = 0;
		FString Montage;
		FString CloseReason;
		float OpenPos = 0.f;
		float ClosePos = 0.f;
		TMap<FName, double> C; // counters of this window
	};

	void Bump(FName Name, double Amount = 1.0);
	void Peak(FName Name, double Value);
	void Close(const TCHAR* Reason);
	FWindow* Current() { return Windows.Num() > 0 ? &Windows.Last() : nullptr; }
	double Get(const TMap<FName, double>& Map, FName Name) const;

	RPGPackTrace::FTarget Target;
	TArray<FWindow> Windows;
	TMap<FName, double> Totals;
	TMap<int32, TMap<FName, double>> Instances;
	TMap<FName, FVector> Previous;
	TArray<TWeakObjectPtr<AActor>> PrevSet;
	bool bActive = false;
	int32 OrdinalBase = 0;
	// outcome of the player's insertion into the hit set
	bool bPending = false;
	double PendingTime = 0.0;
	double PendingHealth = 0.0;
	bool bPendingInvulnerable = false;
	int32 PendingTicks = 0;
	double LastPlayerHealth = -1.0;
	// interrupt tracking
	bool bInterrupted = false;
	uint64 InterruptFrame = 0;
	FString WindowMontage;
	int32 WindowGeneration = 0;
	FName LastMove;
	FString LastCloseText;
};
