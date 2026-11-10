// Copyright One Boss Fight. All Rights Reserved.
#pragma once

#include "Kismet/BlueprintFunctionLibrary.h"
#include "RPGMontageWrapperLibrary.generated.h"

class UAnimMontage;
class UAnimSequence;
class USkeleton;

/** Editor-only creation of isolated retarget montage wrappers. */
UCLASS()
class ONEBOSSFIGHTEDITOR_API URPGMontageWrapperLibrary : public UBlueprintFunctionLibrary
{
	GENERATED_BODY()

public:
	/** Duplicate the source montage's authored structure and notify data, replacing every segment sequence. */
	UFUNCTION(BlueprintCallable, Category="OneBossFight|Animation Authoring")
	static UAnimMontage* CreateRetargetWrapper(UAnimMontage* Source, UAnimSequence* TargetSequence,
		USkeleton* TargetSkeleton, FString PackagePath, FString& OutError);

	/** Create a non-saving retarget copy in the transient package for source-vs-target validation. */
	UFUNCTION(BlueprintCallable, Category="OneBossFight|Animation Authoring")
	static UAnimMontage* CreateTransientRetargetWrapper(UAnimMontage* Source, UAnimSequence* TargetSequence,
		USkeleton* TargetSkeleton, FString& OutError);

	/** One deterministic row per notify, including notify timing, notify track, montage slots, and segment references/lengths. */
	UFUNCTION(BlueprintCallable, Category="OneBossFight|Animation Authoring")
	static TArray<FString> DescribeMontageNotifies(const UAnimMontage* Montage);
};
