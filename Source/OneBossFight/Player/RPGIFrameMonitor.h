// Copyright One Boss Fight. All Rights Reserved.

#pragma once

#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "RPGIFrameMonitor.generated.h"

class UAnimMontage;

/**
 * Observes the player's dodge invulnerability (SPEC M2, Freeze 11.3 and 11.4, tests D12 and D13).
 * The pack's ANS_iFrames notify state adds Status.Invulnerable to the player when it begins and removes it when it ends; nothing else reports it. This component:
 *   - measures every invulnerability interval in MONTAGE seconds with the effective play rate (a record: montage, rate, start and end position, expected window read from the montage asset), so the windows of the quick
 *     dash and the full roll can be compared with the pack data at 30, 60 and 120 FPS;
 *   - tells a tag that a dodge montage set ("montage owned": it rose while the montage was inside its ANS_iFrames window) from a tag somebody else set (tests inject it: "foreign"), and never touches a foreign tag;
 *   - cleans up (Freeze 491 to 493, 800): a montage-owned tag that outlives its montage by more than StaleGraceSeconds, or the death of the player, or an encounter reset, removes the tag (idempotent: the pack's own later
 *     removal is a harmless repeat). The pack already ends the notify state when a montage is interrupted; this is the safety net the Freeze asks for, with a counter so it can be seen when it was needed.
 * Attached to the pack player by RPGPlayerMovesSubsystem. It only observes unless a stale tag is found.
 */
UCLASS(ClassGroup = (Player))
class ONEBOSSFIGHT_API URPGIFrameMonitor : public UActorComponent
{
	GENERATED_BODY()

public:
	URPGIFrameMonitor();

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "IFrame")
	bool bEnabled = true;

	/** A montage-owned tag still set this long after its montage ended or after the montage position passed the window end (plus one frame) is removed. */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "IFrame", meta = (ClampMin = "0.0"))
	float StaleGraceSeconds = 0.1f;

	/** Class name of the pack's notify state. */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "IFrame")
	FName NotifyStateClassName = TEXT("ANS_iFrames_C");

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "IFrame", meta = (ClampMin = "1"))
	int32 MaxRecords = 64;

	/** Records closed since the last clear, and the fields of one (0 = oldest kept, -1 = newest). Field names: Montage (text), Rate, ExpectedStart, ExpectedEnd, StartPos, EndPos, StartTime, EndTime, StartDelta, EndDelta,
	 *  Owned (0 or 1), Closed (0 or 1), Reason (text), FrameStep. */
	UFUNCTION(BlueprintPure, Category = "IFrame")
	int32 GetRecordCount() const { return Records.Num(); }

	UFUNCTION(BlueprintPure, Category = "IFrame")
	double GetRecordNumber(int32 Index, const FString& Field) const;

	UFUNCTION(BlueprintPure, Category = "IFrame")
	FString GetRecordText(int32 Index, const FString& Field) const;

	UFUNCTION(BlueprintCallable, Category = "IFrame")
	void ClearRecords();

	/** True while Status.Invulnerable is set, and a line saying where it came from ("Status.Invulnerable via Dodge_Small_Forward_Roll_Montage at 0.213 of window 0.107 to 0.490, rate 1.30"). */
	UFUNCTION(BlueprintPure, Category = "IFrame")
	bool IsInvulnerableNow() const { return bTag; }

	UFUNCTION(BlueprintPure, Category = "IFrame")
	FString GetSourceText() const;

	/** The tag fell while the montage position was inside its window (not at its end): something removed it early. */
	UFUNCTION(BlueprintPure, Category = "IFrame")
	int32 GetUnexpectedDropCount() const { return UnexpectedDrops; }

	/** Tags the watchdog removed (stale), cleared by death, by an encounter reset. */
	UFUNCTION(BlueprintPure, Category = "IFrame")
	int32 GetStaleClearedCount() const { return StaleCleared; }

	UFUNCTION(BlueprintPure, Category = "IFrame")
	int32 GetDeathClearCount() const { return DeathCleared; }

	UFUNCTION(BlueprintPure, Category = "IFrame")
	int32 GetResetClearCount() const { return ResetCleared; }

	/** Called by the encounter reset: a montage-owned tag goes (a respawned player is a new pawn with a new component). */
	void OnEncounterReset();

	/** Tests: the next tag edge (or a tag that is already set) is treated as montage-owned although no montage is playing, to exercise the stale watchdog. */
	UFUNCTION(BlueprintCallable, Category = "IFrame")
	void DebugForceOwned(bool bOwned);

	/** The component of the first player pawn, or null. */
	static URPGIFrameMonitor* Find(const UObject* WorldContext);

protected:
	virtual void TickComponent(float DeltaTime, ELevelTick TickType, FActorComponentTickFunction* ThisTickFunction) override;
	virtual void EndPlay(const EEndPlayReason::Type EndPlayReason) override;

private:
	struct FRecord
	{
		FString Montage;
		float Rate = 1.f;
		float ExpectedStart = -1.f;
		float ExpectedEnd = -1.f;
		float StartPos = 0.f;
		float EndPos = 0.f;
		double StartTime = 0.0;
		double EndTime = 0.0;
		float FrameStep = 0.f;
		bool bOwned = false;
		bool bClosed = false;
		FString Reason;
		FString EndMontage;      // the montage that was playing when the record closed (a forced roll replaces the quick dodge's montage under one continuous tag)
		float EndExpectedEnd = -1.f; // that montage's window end in montage seconds
	};

	bool ReadWindow(const UAnimMontage* Montage, float& OutStart, float& OutEnd) const;
	void RemoveTag(const TCHAR* Reason);
	void CloseRecord(const TCHAR* Reason, float EndPos);
	const FRecord* Get(int32 Index) const;

	TArray<FRecord> Records;
	bool bTag = false;
	bool bOpen = false;
	bool bForceOwned = false;
	bool bOwnedNow = false;
	double TagSince = 0.0;
	double MontageGoneSince = -1.0;
	float LastPos = 0.f;
	double LastPosTime = 0.0; // world time of LastPos: the montage position is extrapolated from it when the montage is gone (a blend-out)
	float LastWindowEnd = -1.f; // window end of the last montage seen (the falling edge may be seen after the montage is gone)
	float LastRate = 1.f;
	float LastStep = 0.f;
	FString LastMontage;
	int32 UnexpectedDrops = 0;
	int32 StaleCleared = 0;
	int32 DeathCleared = 0;
	int32 ResetCleared = 0;
	bool bWasAlive = true;
	TMap<TWeakObjectPtr<const UAnimMontage>, FVector2D> WindowCache; // montage -> (start, end); (-1, -1) when it has none
};
