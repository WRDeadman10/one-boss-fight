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
};
