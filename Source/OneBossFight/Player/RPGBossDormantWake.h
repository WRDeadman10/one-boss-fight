// Copyright One Boss Fight. All Rights Reserved.

#pragma once

#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "UObject/SoftObjectPtr.h"
#include "RPGBossDormantWake.generated.h"

class AActor;
class ACharacter;
class UAnimMontage;
class UAnimSequence;

/** Project-owned dormant loop and wake gate. The encounter owns whether the pack behaviour resumes; this component owns only the dynamic clips. */
UCLASS(ClassGroup = (Boss))
class ONEBOSSFIGHT_API URPGBossDormantWake : public UActorComponent
{
	GENERATED_BODY()

public:
	URPGBossDormantWake();

	static URPGBossDormantWake* Find(const AActor* Actor);
	static void StopFor(AActor* Actor, const TCHAR* Reason);

	/** Starts the looping dormant sequence when loaded. */
	void BeginDormant();
	/** Stops the dormant loop and starts wake once. True only when the encounter must defer its behaviour resume. */
	bool BeginWake();
	void StopClips(const TCHAR* Reason);

	UFUNCTION(BlueprintPure, Category = "Dormant Wake")
	bool IsWaking() const { return bWaking; }

	UFUNCTION(BlueprintPure, Category = "Dormant Wake")
	FString GetStageName() const;

	UFUNCTION(BlueprintPure, Category = "Dormant Wake")
	int32 GetDormantPlayCount() const { return DormantPlayCount; }

	UFUNCTION(BlueprintPure, Category = "Dormant Wake")
	int32 GetWakePlayCount() const { return WakePlayCount; }

protected:
	virtual void BeginPlay() override;
	virtual void EndPlay(const EEndPlayReason::Type EndPlayReason) override;
	virtual void TickComponent(float DeltaTime, ELevelTick TickType, FActorComponentTickFunction* ThisTickFunction) override;

private:
	UAnimSequence* GetDormantClip();
	UAnimSequence* GetWakeClip();
	ACharacter* GetBoss() const;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Dormant Wake", meta = (AllowPrivateAccess = "true"))
	TSoftObjectPtr<UAnimSequence> DormantClip;
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Dormant Wake", meta = (AllowPrivateAccess = "true"))
	TSoftObjectPtr<UAnimSequence> WakeClip;
	UPROPERTY(Transient)
	TObjectPtr<UAnimSequence> LoadedDormantClip;
	UPROPERTY(Transient)
	TObjectPtr<UAnimSequence> LoadedWakeClip;
	TWeakObjectPtr<UAnimMontage> DormantMontage;
	TWeakObjectPtr<UAnimMontage> WakeMontage;

	bool bWaking = false;
	double WakeStartedAt = -1.0;
	int32 DormantPlayCount = 0;
	int32 WakePlayCount = 0;
};
