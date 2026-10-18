// Copyright One Boss Fight. All Rights Reserved.

#pragma once

#include "CoreMinimal.h"
#include "Subsystems/WorldSubsystem.h"
#include "Containers/Ticker.h"
#include "TimerManager.h"
#include "RPGEncounterSubsystem.generated.h"

class ARPGBossCharacter;
class ARPGPlayerCharacter;

UENUM(BlueprintType)
enum class ERPGEncounterState : uint8
{
	/** Waiting at the arena entrance; the boss is dormant. */
	Idle,
	/** Boss engaged. */
	Active,
	/** Boss dead. */
	Victory,
	/** Player dead; a retry is pending. */
	Defeat
};

DECLARE_DYNAMIC_MULTICAST_DELEGATE_OneParam(FRPGEncounterStateChangedSignature, ERPGEncounterState, NewState);
DECLARE_MULTICAST_DELEGATE(FRPGEncounterResetDelegate);

/**
 * Runs the fight loop for one boss: start (trigger volume), win, lose, automatic retry, and the reset that
 * puts everything back exactly as it was at the arena entrance. VerifyResetInvariants() checks that nothing
 * stale survives a reset; it runs after every reset and in the automation tests.
 */
UCLASS()
class ONEBOSSFIGHT_API URPGEncounterSubsystem : public UWorldSubsystem
{
	GENERATED_BODY()

public:
	/** Seconds from the player's death to the automatic reset. */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Encounter", meta = (ClampMin = "0"))
	float RetryDelay = 4.f;

	/** World time scale during the victory slow motion. 1 disables it. */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Encounter|Presentation", meta = (ClampMin = "0.05", ClampMax = "1"))
	float VictorySlowMoScale = 0.25f;

	/** Real seconds the victory slow motion lasts. */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Encounter|Presentation", meta = (ClampMin = "0"))
	float VictorySlowMoSeconds = 2.5f;

	UPROPERTY(BlueprintAssignable, Category = "Encounter")
	FRPGEncounterStateChangedSignature OnEncounterStateChanged;

	/** Triggers re-arm themselves from this. */
	FRPGEncounterResetDelegate OnEncounterReset;

	UFUNCTION(BlueprintPure, Category = "Encounter")
	ERPGEncounterState GetState() const { return State; }

	UFUNCTION(BlueprintPure, Category = "Encounter")
	ARPGBossCharacter* GetBoss() const { return Boss.Get(); }

	UFUNCTION(BlueprintPure, Category = "Encounter")
	ARPGPlayerCharacter* GetPlayer() const { return Player.Get(); }

	UFUNCTION(BlueprintPure, Category = "Encounter")
	int32 GetResetCount() const { return ResetCount; }

	void RegisterBoss(ARPGBossCharacter* NewBoss);

	/** Remembers where the player starts so a retry returns there. */
	void RegisterPlayer(ARPGPlayerCharacter* NewPlayer);

	/** Wakes the boss against the player. Only from Idle. */
	UFUNCTION(BlueprintCallable, Category = "Encounter")
	bool StartEncounter();

	/** Puts player and boss back to the start. Works from any state. */
	UFUNCTION(BlueprintCallable, Category = "Encounter")
	void ResetEncounter();

	/** True if everything that must be clean after a reset is clean; otherwise OutReason says what is not. */
	bool VerifyResetInvariants(FString& OutReason) const;

	virtual void Deinitialize() override;

private:
	UFUNCTION()
	void HandlePlayerDied();

	UFUNCTION()
	void HandleBossDied();

	void SetState(ERPGEncounterState NewState);
	void StartVictorySlowMo();
	void EndVictorySlowMo();
	bool OnSlowMoTick(float DeltaTime);

	ERPGEncounterState State = ERPGEncounterState::Idle;
	TWeakObjectPtr<ARPGBossCharacter> Boss;
	TWeakObjectPtr<ARPGPlayerCharacter> Player;
	FTransform PlayerStart;
	FTimerHandle RetryTimer;
	int32 ResetCount = 0;
	FTSTicker::FDelegateHandle SlowMoTicker;
};
