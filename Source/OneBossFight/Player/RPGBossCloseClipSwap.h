// Copyright One Boss Fight. All Rights Reserved.

#pragma once

#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "UObject/SoftObjectPtr.h"
#include "RPGBossCloseClipSwap.generated.h"

class UAnimMontage;

/**
 * Replaces only the created pack close-attack ability's A1/A3 montage entries with project-owned authored montages.
 * The pack ability still selects the stage, provides attack data and owns its trace/follow-up notifies. A missing or
 * changed pack property fails open: its original montage entries are left untouched.
 */
UCLASS(ClassGroup = (Boss))
class ONEBOSSFIGHT_API URPGBossCloseClipSwap : public UActorComponent
{
	GENERATED_BODY()

public:
	URPGBossCloseClipSwap();

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Close clips")
	FName CloseAbilityClassName = TEXT("GA_GS_Boss_CloseAttack_C");

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Close clips")
	FName AttackMontagesName = TEXT("AttackMontages");

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Close clips")
	TSoftObjectPtr<UAnimMontage> A1Montage;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Close clips")
	TSoftObjectPtr<UAnimMontage> A3aMontage;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Close clips")
	TSoftObjectPtr<UAnimMontage> A3bMontage;

	UFUNCTION(BlueprintPure, Category = "Close clips")
	bool IsApplied() const { return bApplied; }

	UFUNCTION(BlueprintPure, Category = "Close clips")
	int32 GetAppliedEntryCount() const { return Swaps.Num(); }

	UFUNCTION(BlueprintPure, Category = "Close clips")
	int32 GetApplyCount() const { return ApplyCount; }

	UFUNCTION(BlueprintPure, Category = "Close clips")
	int32 GetRestoreCount() const { return RestoreCount; }

	UFUNCTION(BlueprintPure, Category = "Close clips")
	FString GetLastResult() const { return LastResult; }

	/** Tests: immediately tries the same validation and live-instance swap as the regular poll. */
	UFUNCTION(BlueprintCallable, Category = "Close clips")
	FString ApplyNowForTest();

	/** Tests: turns the component off/on without PIE property reconstruction; off restores the original pack entries. */
	UFUNCTION(BlueprintCallable, Category = "Close clips")
	void SetEnabledForTest(bool bOn);

protected:
	virtual void BeginPlay() override;
	virtual void TickComponent(float DeltaTime, ELevelTick TickType, FActorComponentTickFunction* ThisTickFunction) override;
	virtual void EndPlay(const EEndPlayReason::Type EndPlayReason) override;

private:
	struct FSwap
	{
		int32 Index = INDEX_NONE;
		TWeakObjectPtr<UAnimMontage> Original;
	};

	void Preload();
	bool TryApply();
	void Restore(const TCHAR* Why);
	UAnimMontage* ReplacementFor(FName PackMontageName) const;

	UPROPERTY(Transient)
	TObjectPtr<UAnimMontage> LoadedA1;
	UPROPERTY(Transient)
	TObjectPtr<UAnimMontage> LoadedA3a;
	UPROPERTY(Transient)
	TObjectPtr<UAnimMontage> LoadedA3b;

	TWeakObjectPtr<UObject> SwappedAbility;
	TArray<FSwap> Swaps;
	int32 LastResetCount = INDEX_NONE;
	float RetrySeconds = 0.f;
	int32 ApplyCount = 0;
	int32 RestoreCount = 0;
	bool bApplied = false;
	bool bEnabledForTest = true;
	bool bPermanentFailure = false;
	FString LastResult = TEXT("waiting");
};
