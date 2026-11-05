// Copyright One Boss Fight. All Rights Reserved.
#pragma once

#include "CoreMinimal.h"
#include "Engine/DataAsset.h"
#include "Player/RPGEncounterBinding.h"
#include "RPGBossEncounterDefinition.generated.h"

/** Authored selection for one encounter. It stores configuration, never actor references. */
UCLASS(BlueprintType)
class ONEBOSSFIGHT_API URPGBossEncounterDefinition : public UPrimaryDataAsset
{
	GENERATED_BODY()

public:
	UPROPERTY(EditAnywhere, Category="Encounter") int32 Schema = 1;
	/** Stable encounter identity copied to the transient binding; invalid IDs are refused. */
	UPROPERTY(EditAnywhere, Category="Encounter") FGuid EncounterInstance;
	/** Explicit caller-supplied membership hash required by the unchanged world input compiler. */
	UPROPERTY(EditAnywhere, Category="Encounter") FString StableManifestHash;
	UPROPERTY(EditAnywhere, Category="Encounter") FName BossSlot;
	UPROPERTY(EditAnywhere, Category="Encounter") FName PlayerSlot;
	/** Phase-transition record to configure; the fight starts in its implicit base phase. */
	UPROPERTY(EditAnywhere, Category="Encounter") FName InitialBossPhase;
	UPROPERTY(EditAnywhere, Category="Definitions") TSoftObjectPtr<URPGBossDefinition> BossDefinition;
	UPROPERTY(EditAnywhere, Category="Definitions") TSoftObjectPtr<URPGBossDefinition> PlayerDefinition;

	/** Structural validation only. Definition contents are validated by the accepted compiler before registration. */
	bool ValidateSelectionRecord(FString& OutError) const;
};
