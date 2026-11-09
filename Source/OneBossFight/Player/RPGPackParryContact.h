// Copyright One Boss Fight. All Rights Reserved.

#pragma once

#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "Pack/RPGPackTrace.h"
#include "Player/RPGPackParryRules.h"
#include "Player/RPGParryGradeRules.h"
#include "RPGPackParryContact.generated.h"

class URPGAttackTracker;

/** Converts confirmed pack-trace parries into the same native reward used by project-resolver parries. */
UCLASS(ClassGroup = (Boss))
class ONEBOSSFIGHT_API URPGPackParryContact : public UActorComponent
{
	GENERATED_BODY()

public:
	URPGPackParryContact();

	UFUNCTION(BlueprintPure, Category = "Parry|PackContact")
	int32 GetConfirmedContactCount() const { return ConfirmedContactCount; }

	UFUNCTION(BlueprintPure, Category = "Parry|PackContact")
	int32 GetRejectedContactCount() const { return RejectedContactCount; }

protected:
	virtual void BeginPlay() override;
	virtual void TickComponent(float DeltaTime, ELevelTick TickType, FActorComponentTickFunction* ThisTickFunction) override;

private:
	struct FCandidate
	{
		FString AttackKey;
		double InsertedAt = 0.0;
		double PlayerHealthBefore = 0.0;
		RPGParryGrade::EGrade Grade = RPGParryGrade::EGrade::None;
	};

	bool ReadInvulnerabilityTag(AActor* Player, bool& bOutInvulnerable) const;
	FString CurrentAttackKey(AActor* Boss, const URPGAttackTracker* Tracker, double WorldTime) const;
	void ClearEncounterState(uint64 NewGeneration, AActor* NewPlayer);
	void LogSkip(FName Reason, AActor* Hit, double WorldTime, const FString& Detail = FString());

	RPGPackTrace::FTarget Target;
	TWeakObjectPtr<AActor> ObservedPlayer;
	TArray<TWeakObjectPtr<AActor>> PreviousHitSet;
	TArray<FCandidate> Candidates;
	TSet<FString> ObservedAttackKeys;
	uint64 EncounterGeneration = MAX_uint64;
	bool bWasTraceActive = false;
	bool bHasPreviousParrySample = false;
	bool bPreviousParryWindowOpen = false;
	RPGParryGrade::EGrade PreviousParryGrade = RPGParryGrade::EGrade::None;
	bool bHasLoggedTargetState = false;
	bool bLastLoggedTargetResolved = false;
	TWeakObjectPtr<UObject> LastLoggedTargetObject;
	TWeakObjectPtr<UObject> LastLoggedCollisionObject;
	TMap<FName, double> LastSkipLogTimes;
	int32 ConfirmedContactCount = 0;
	int32 RejectedContactCount = 0;
};
