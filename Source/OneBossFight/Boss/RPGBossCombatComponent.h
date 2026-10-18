// Copyright One Boss Fight. All Rights Reserved.

#pragma once

#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "Math/RandomStream.h"
#include "RPGBossCombatComponent.generated.h"

class UAnimMontage;
class URPGAttributeComponent;
class URPGBossAttackData;
class URPGCombatComponent;

/** Top-level boss flow. The combat component below owns what the boss is doing inside Combat. */
UENUM(BlueprintType)
enum class ERPGBossState : uint8
{
	/** Waiting for the encounter. Cannot be hurt. */
	Dormant,
	/** Intro animation. Cannot be hurt. */
	Entrance,
	/** Fighting: choosing and performing attacks. */
	Combat,
	/** Roaring into the next phase. Cannot be hurt. */
	PhaseTransition,
	Dead
};

DECLARE_DYNAMIC_MULTICAST_DELEGATE_TwoParams(FRPGBossStateChangedSignature, ERPGBossState, OldState, ERPGBossState, NewState);
DECLARE_DYNAMIC_MULTICAST_DELEGATE_TwoParams(FRPGBossPhaseChangedSignature, int32, OldPhase, int32, NewPhase);

/** What the selector knows about the moment of decision. */
struct FRPGAttackSelectionContext
{
	float Distance = 0.f;
	float AngleDegrees = 0.f;
	int32 Phase = 1;
	/** Index chosen last, or INDEX_NONE. */
	int32 LastAttackIndex = INDEX_NONE;
	int32 ConsecutiveRepeats = 0;
};

/**
 * Boss brain: weighted attack selection plus the Dormant -> Entrance -> Combat -> PhaseTransition -> Dead flow.
 *
 * Selection filters the attack list by distance, facing arc, phase, cooldown and repeat limit, then picks among
 * what remains by weight. The random value is passed in, so the distribution is testable. Performing the attack
 * is delegated to the boss's URPGCombatComponent, so animation windows, hit detection, poise and death behave
 * exactly as they do for the player.
 *
 * Time is advanced by TickBoss(), callable directly in tests.
 */
UCLASS(ClassGroup = (Combat), meta = (BlueprintSpawnableComponent))
class ONEBOSSFIGHT_API URPGBossCombatComponent : public UActorComponent
{
	GENERATED_BODY()

public:
	URPGBossCombatComponent();

	// ---- Configuration -------------------------------------------------------------------

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Boss")
	TArray<TObjectPtr<URPGBossAttackData>> Attacks;

	/**
	 * Health fractions that start the next phase, descending. {0.5} gives two phases: phase 2 begins when
	 * health falls to 50 %.
	 */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Boss|Phases")
	TArray<float> PhaseHealthThresholds = {0.5f};

	/** Seconds the boss is untouchable and busy when a phase starts (used when there is no montage). */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Boss|Phases", meta = (ClampMin = "0"))
	float PhaseTransitionDuration = 3.f;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Boss|Phases")
	TObjectPtr<UAnimMontage> PhaseTransitionMontage;

	/** Seconds of intro (used when there is no montage). */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Boss|Entrance", meta = (ClampMin = "0"))
	float EntranceDuration = 3.f;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Boss|Entrance")
	TObjectPtr<UAnimMontage> EntranceMontage;

	/** Reaction time after the previous action before the boss decides what to do, random in [Min, Max]. */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Boss|Fairness", meta = (ClampMin = "0"))
	float ReactionDelayMin = 0.2f;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Boss|Fairness", meta = (ClampMin = "0"))
	float ReactionDelayMax = 0.5f;

	/** When no attack is allowed the boss walks toward the target until it is this close. */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Boss|Movement", meta = (ClampMin = "0"))
	float PreferredDistance = 250.f;

	/** Degrees per second the boss turns toward the target while walking or waiting. */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Boss|Movement", meta = (ClampMin = "0"))
	float IdleTurnRate = 180.f;

	// ---- Queries -------------------------------------------------------------------------

	UFUNCTION(BlueprintPure, Category = "Boss")
	ERPGBossState GetBossState() const { return BossState; }

	UFUNCTION(BlueprintPure, Category = "Boss")
	int32 GetPhase() const { return CurrentPhase; }

	/** How many phase transitions have started since the last reset. Never more than phases - 1. */
	UFUNCTION(BlueprintPure, Category = "Boss")
	int32 GetPhaseTransitionCount() const { return PhaseTransitionCount; }

	UFUNCTION(BlueprintPure, Category = "Boss")
	AActor* GetTarget() const { return Target.Get(); }

	/** Index into Attacks of the attack in progress, or INDEX_NONE. */
	UFUNCTION(BlueprintPure, Category = "Boss")
	int32 GetCurrentAttackIndex() const { return bAttackInProgress ? CurrentAttackIndex : INDEX_NONE; }

	UFUNCTION(BlueprintPure, Category = "Boss")
	float GetCooldownRemaining(int32 AttackIndex) const { return CooldownRemaining.IsValidIndex(AttackIndex) ? CooldownRemaining[AttackIndex] : 0.f; }

	/** Last state the boss StateTree reported entering (its mirror task calls NotifyStateTreeEntered). Dormant until it runs. */
	UFUNCTION(BlueprintPure, Category = "Boss")
	ERPGBossState GetMirroredState() const { return MirroredState; }

	/** How many times the StateTree has reported entering a state. Zero means no tree is running. */
	UFUNCTION(BlueprintPure, Category = "Boss")
	int32 GetStateTreeEnterCount() const { return StateTreeEnterCount; }

	/** Called by the StateTree mirror task. */
	void NotifyStateTreeEntered(ERPGBossState EnteredState)
	{
		MirroredState = EnteredState;
		++StateTreeEnterCount;
	}

	// ---- Control -------------------------------------------------------------------------

	/** Starts the entrance and then the fight against Target. Only from Dormant. */
	UFUNCTION(BlueprintCallable, Category = "Boss")
	bool Engage(AActor* NewTarget);

	/** Back to Dormant with phase 1, no cooldowns, no history and no target. Combat/attributes are reset by the character. */
	UFUNCTION(BlueprintCallable, Category = "Boss")
	void ResetBoss();

	/** Makes the random choices repeatable. */
	void SetRandomSeed(int32 Seed) { Random.Initialize(Seed); }

	/** Advances the boss. Called by the component tick; callable directly in tests. */
	void TickBoss(float DeltaTime);

	/**
	 * Picks an attack index or INDEX_NONE. RandomUnit is in [0, 1). Pure: reads only its arguments.
	 * CooldownRemaining must be parallel to Attacks (missing entries count as ready).
	 */
	static int32 ChooseAttack(const TArray<TObjectPtr<URPGBossAttackData>>& Attacks, const TArray<float>& CooldownRemaining,
		const FRPGAttackSelectionContext& Context, float RandomUnit);

	/** Phase (1-based) for a health fraction under the given thresholds. Pure. */
	static int32 ComputePhase(const TArray<float>& Thresholds, float HealthFraction);

	// ---- Events --------------------------------------------------------------------------

	UPROPERTY(BlueprintAssignable, Category = "Boss")
	FRPGBossStateChangedSignature OnBossStateChanged;

	UPROPERTY(BlueprintAssignable, Category = "Boss")
	FRPGBossPhaseChangedSignature OnPhaseChanged;

protected:
	virtual void OnRegister() override;
	virtual void TickComponent(float DeltaTime, ELevelTick TickType, FActorComponentTickFunction* ThisTickFunction) override;

private:
	URPGCombatComponent* GetCombat() const;
	/** Finds the attribute component and, on first use, subscribes to health and death. */
	URPGAttributeComponent* EnsureBound();

	UFUNCTION()
	void HandleHealthChanged(float Current, float Max, float Delta);

	UFUNCTION()
	void HandleDeath();

	void SetBossState(ERPGBossState NewState);
	void StartPhaseTransition(int32 NewPhase);
	void FinishTimedState();
	/** Plays the montage on the owner's mesh. Returns its length in seconds, or 0 if it could not play. */
	float PlayMontageOnOwner(UAnimMontage* Montage) const;
	void TickCombatState(float DeltaTime);
	void ExecuteAttack(int32 Index);
	void TurnToward(const FVector& WorldLocation, float DegreesPerSecond, float DeltaTime) const;
	void UpdateTickState();
	float RandomReactionDelay();

	ERPGBossState BossState = ERPGBossState::Dormant;
	int32 CurrentPhase = 1;
	int32 PhaseTransitionCount = 0;

	TWeakObjectPtr<AActor> Target;

	TArray<float> CooldownRemaining;
	int32 LastAttackIndex = INDEX_NONE;
	int32 ConsecutiveRepeats = 0;

	int32 CurrentAttackIndex = INDEX_NONE;
	bool bAttackInProgress = false;
	bool bHitWindowSeen = false;
	float DecisionTimer = 0.f;
	float StateTimer = 0.f;

	ERPGBossState MirroredState = ERPGBossState::Dormant;
	int32 StateTreeEnterCount = 0;

	FRandomStream Random;
	bool bBound = false;
};
