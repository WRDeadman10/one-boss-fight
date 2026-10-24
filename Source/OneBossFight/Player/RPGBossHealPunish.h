// Copyright One Boss Fight. All Rights Reserved.

#pragma once

#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "Player/RPGBossJavelin.h"
#include "RPGBossHealPunish.generated.h"

/**
 * A5, the heal punish (Master Design Freeze 16 A5, 21, 32.3): drinking a flask within reach of the boss costs something, but never by cheating.
 *
 * Heal signal: the pack's heal ability (GA_ConsumeHealthPotion, ability tag Ability.UseItem) plays DrinkingPotion_Montage on the player. The start of that montage is the canonical "heal started" event (an edge, so
 * a montage that keeps playing is one event). The pack sets no heal-specific state tag (only the generic Status.ActionCommitted that every action sets), so no tag is added.
 *
 * On a heal start the boss evaluates ONE request. It is accepted only if all hold: the boss is alive and neutral (no attack tracked, nothing playing, not staggered, not in a phase transition, not dormant); the
 * player is alive and between MinRange and MaxRange cm (horizontal); a line from the boss to the player is not blocked by arena geometry; the cooldown is ready; no punish is already pending or flying. Otherwise
 * the request is discarded and counted (a committed attack is never interrupted: the heal only does what the slam does to it).
 * An accepted request starts the tracker's move A5 (the boss's own telegraph: the clip plays, the heading follows the player until the release). At the release (the tracker's active window opens) the
 * target is revalidated (alive, line of sight clear) and an ARPGBossJavelin is spawned at the boss's hand and flies towards where the player is at that moment; it is never placed at the player.
 * Cooldown (Cooldown seconds) starts at the release; repeated heal events never restart it. An encounter reset, the boss's death or an interrupted A5 before the release clears the pending request; a reset also
 * clears the cooldown (a new fight starts ready) and destroys flying javelins (they carry the generation).
 */
UCLASS(ClassGroup = (Boss))
class ONEBOSSFIGHT_API URPGBossHealPunish : public UActorComponent
{
	GENERATED_BODY()

public:
	URPGBossHealPunish();

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Punish")
	bool bEnabled = true;

	/** Distance window of the punish (cm, horizontal), Freeze 16: 400 to 1000. */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Punish", meta = (ClampMin = "0.0"))
	float MinRange = 400.f;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Punish", meta = (ClampMin = "0.0"))
	float MaxRange = 1000.f;

	/** Seconds between two javelins, counted from the release (Freeze: 4.0 s starting value). */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Punish", meta = (ClampMin = "0.0"))
	float Cooldown = 4.f;

	/** Health taken by a hit. The Freeze table says 30, written for a larger health pool: the pack player has 120 health, factor 0.4 gives 12. Deviation, see DELTA_AUDIT. */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Punish", meta = (ClampMin = "0.0"))
	float Damage = 12.f;

	/** Flight: seconds the javelin takes to reach the point where the player stood at the release, and the speed limits (cm per second) that keeps it readable at any distance. The Freeze asks for a punish that is
	 *  dodgeable on the heal exit: the drink animation lasts 1.13 s, the release is at about 0.45 s, and a dodge pressed at the exit starts to move about 0.2 s later (measured), so 1.2 s of flight lands it at about
	 *  1.65 s. (0.9 s landed it at 1.3 s: only a dodge pressed during the drink animation avoided it.) */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Punish", meta = (ClampMin = "0.05"))
	float FlightTime = 1.2f;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Punish", meta = (ClampMin = "1.0"))
	float MinSpeed = 450.f;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Punish", meta = (ClampMin = "1.0"))
	float MaxSpeed = 2500.f;

	/** Collision sphere radius and the range after which the javelin ends. */

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Punish", meta = (ClampMin = "1.0"))
	float JavelinRadius = 25.f;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Punish", meta = (ClampMin = "1.0"))
	float JavelinMaxRange = 3000.f;

	/** Where the javelin leaves the hand: this socket or bone of the boss's mesh (the Freeze asks Antigravity for a JavelinSpawn socket on hand_l), else the first one that exists, else a point above and in front of the boss. */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Punish")
	TArray<FName> SpawnSockets = {TEXT("JavelinSpawn"), TEXT("hand_l")};

	/** Height above the player's feet that the javelin aims at (cm): about the chest. */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Punish")
	float AimHeight = 100.f;

	/** The boss answers the heal on its own. Off in tests that start the heal themselves and check the decision. */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Punish")
	bool bRespondToHeal = true;

	/** Tests: reports a heal start as if the player's drink montage had begun (same path as the real one). */
	UFUNCTION(BlueprintCallable, Category = "Punish")
	void NotifyHealStartedForTest()
	{
#if !UE_BUILD_SHIPPING
		OnHealStarted();
#endif
	}

	/** True from an accepted heal until the javelin is released (or the attempt is cleared). */
	UFUNCTION(BlueprintPure, Category = "Punish")
	bool IsPending() const { return bPending; }

	UFUNCTION(BlueprintPure, Category = "Punish")
	float GetCooldownRemaining() const;

	/** Counters (tests). Heal events seen; requests accepted; discarded for each reason; javelins released; results. */
	UFUNCTION(BlueprintPure, Category = "Punish")
	int32 GetHealEventCount() const { return HealEvents; }

	UFUNCTION(BlueprintPure, Category = "Punish")
	int32 GetAcceptedCount() const { return Accepted; }

	UFUNCTION(BlueprintPure, Category = "Punish")
	int32 GetReleasedCount() const { return Released; }

	UFUNCTION(BlueprintPure, Category = "Punish")
	int32 GetDiscardedBusyCount() const { return DiscardedBusy; }

	UFUNCTION(BlueprintPure, Category = "Punish")
	int32 GetDiscardedRangeCount() const { return DiscardedRange; }

	UFUNCTION(BlueprintPure, Category = "Punish")
	int32 GetDiscardedSightCount() const { return DiscardedSight; }

	UFUNCTION(BlueprintPure, Category = "Punish")
	int32 GetDiscardedCooldownCount() const { return DiscardedCooldown; }

	UFUNCTION(BlueprintPure, Category = "Punish")
	int32 GetDiscardedPendingCount() const { return DiscardedPending; }

	UFUNCTION(BlueprintPure, Category = "Punish")
	int32 GetCancelledCount() const { return Cancelled; }

	UFUNCTION(BlueprintPure, Category = "Punish")
	int32 GetJavelinHitCount() const { return JavelinHits; }

	UFUNCTION(BlueprintPure, Category = "Punish")
	int32 GetJavelinDodgedCount() const { return JavelinDodged; }

	UFUNCTION(BlueprintPure, Category = "Punish")
	int32 GetJavelinWorldCount() const { return JavelinWorld; }

	/** The boss's offence is cancelled (a stance break or a phase transition, Freeze 17.3 item 2 and 18.1 line 766): the pending request is cleared and, when bCancelJavelinsOnInterrupt is on, javelins in flight end.
	 *  The cooldown is not touched (it starts at the release only). */
	void CancelAll(const TCHAR* Reason);

	/** Freeze 723 says projectiles are disabled when the boss breaks. Off = they fly on. */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Punish")
	bool bCancelJavelinsOnInterrupt = true;

	/** Called by the javelin. */
	void ReportJavelin(ERPGJavelinResult Result);

protected:
	virtual void TickComponent(float DeltaTime, ELevelTick TickType, FActorComponentTickFunction* ThisTickFunction) override;

private:
	void OnHealStarted();
	void ClearPending(const TCHAR* Reason);
	void Release();
	bool HasLineOfSight(const AActor* Boss, const AActor* Player, const FVector& From) const;
	FVector GetSpawnLocation() const;

	bool bPending = false;
	bool bStarted = false; // the tracker has shown the throw since the request was accepted
	bool bWasHealing = false;
	bool bDead = false;
	float DeathCheck = 0.f;
	double PendingSince = 0.0;
	double CooldownEnd = -1.0; // world time
	int32 LastInstance = -1;
	int32 SeenGeneration = 0;
	int32 HealEvents = 0;
	int32 Accepted = 0;
	int32 Released = 0;
	int32 DiscardedBusy = 0;
	int32 DiscardedRange = 0;
	int32 DiscardedSight = 0;
	int32 DiscardedCooldown = 0;
	int32 DiscardedPending = 0;
	int32 Cancelled = 0;
	int32 JavelinHits = 0;
	int32 JavelinDodged = 0;
	int32 JavelinWorld = 0;
	TWeakObjectPtr<const UAnimMontage> DrinkMontage;
	TArray<TWeakObjectPtr<ARPGBossJavelin>> Flying;
};
