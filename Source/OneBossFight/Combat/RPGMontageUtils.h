// Copyright One Boss Fight. All Rights Reserved.

#pragma once

#include "CoreMinimal.h"
#include "Kismet/BlueprintFunctionLibrary.h"
#include "RPGMontageUtils.generated.h"

class UAnimMontage;

/**
 * Authoring helpers for editor scripts. Python cannot reach a montage's slot tracks, and montages made
 * from a sequence default to "DefaultSlot", which third-party AnimBPs (Paragon) do not contain.
 */
UCLASS()
class ONEBOSSFIGHT_API URPGMontageUtils : public UBlueprintFunctionLibrary
{
	GENERATED_BODY()

public:
	/** Moves every slot track of the montage to SlotName and marks the package dirty. Returns the track count changed. */
	UFUNCTION(BlueprintCallable, Category = "RPG|Authoring")
	static int32 SetMontageSlot(UAnimMontage* Montage, FName SlotName);

	/** First slot name on the montage, or None. For verifying imported montages. */
	UFUNCTION(BlueprintPure, Category = "RPG|Authoring")
	static FName GetMontageSlot(const UAnimMontage* Montage);
};
