// Copyright One Boss Fight. All Rights Reserved.
#pragma once

#include "Kismet/BlueprintFunctionLibrary.h"
#include "RPGGreystoneRuntimeRetargetLibrary.generated.h"

class UAnimBlueprint;
class UBlueprint;

/** Editor-only, idempotent authoring for Greystone's runtime Retarget Pose From Mesh path. */
UCLASS()
class ONEBOSSFIGHTEDITOR_API URPGGreystoneRuntimeRetargetLibrary : public UBlueprintFunctionLibrary
{
	GENERATED_BODY()

public:
	/** Read-only preflight. Never creates or saves an asset. */
	UFUNCTION(BlueprintCallable, Category="OneBossFight|Greystone Retarget")
	static bool PlanGreystoneRuntimeRetarget(FString& OutReport, FString& OutError);

	/** Create or validate the editor-only Greystone AnimBP at its fixed allowlisted path. */
	UFUNCTION(BlueprintCallable, Category="OneBossFight|Greystone Retarget")
	static bool CreateGreystoneRuntimeRetargetAnimBlueprint(FString& OutAssetPath, FString& OutError);

	/** Configure the child player BP's hidden canonical source mesh and visible retargeted mesh. */
	UFUNCTION(BlueprintCallable, Category="OneBossFight|Greystone Retarget")
	static bool ConfigureGreystonePlayerBlueprint(UBlueprint* PlayerBlueprint, FString& OutReport, FString& OutError);

	/** Read local SCS templates and inherited component override templates without relying on Python exposing BP SimpleConstructionScript. */
	UFUNCTION(BlueprintCallable, Category="OneBossFight|Greystone Retarget")
	static bool GetGreystonePlayerComponentInventory(UBlueprint* PlayerBlueprint, TArray<FString>& OutRows, FString& OutError);
};
