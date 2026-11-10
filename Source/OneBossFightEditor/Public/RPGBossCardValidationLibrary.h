// Copyright One Boss Fight. All Rights Reserved.
#pragma once

#include "Kismet/BlueprintFunctionLibrary.h"
#include "RPGBossCardValidationLibrary.generated.h"

class URPGBossFrameworkProfile;
class URPGBossMoveCard;
class USkeletalMesh;
struct FRPGBossMoveCardSpec;
struct FRPGBossMoveMetadata;

/** Editor-only, read-only access to the production C++ boss-card validators. */
UCLASS()
class ONEBOSSFIGHTEDITOR_API URPGBossCardValidationLibrary : public UBlueprintFunctionLibrary
{
	GENERATED_BODY()

public:
	/** Runs CompileResolved (which includes Validate) against already-authored card and mesh assets. */
	UFUNCTION(BlueprintCallable, Category="OneBossFight|Boss Validation")
	static bool ValidateMoveCard(URPGBossMoveCard* Card, USkeletalMesh* Mesh, TArray<FString>& OutDiagnostics);

	/** Runs ValidateProfile and ResolveProfile using the production profile path. */
	UFUNCTION(BlueprintCallable, Category="OneBossFight|Boss Validation")
	static bool ValidateFrameworkProfile(URPGBossFrameworkProfile* Profile, TArray<FString>& OutDiagnostics);

	/** Python-friendly, unambiguous report form for locked transient authoring dry-runs. */
	UFUNCTION(BlueprintCallable, Category="OneBossFight|Boss Validation")
	static FString ValidateMoveCardReport(URPGBossMoveCard* Card, USkeletalMesh* Mesh);

	/** Python-friendly, unambiguous report form for locked transient authoring dry-runs. */
	UFUNCTION(BlueprintCallable, Category="OneBossFight|Boss Validation")
	static FString ValidateFrameworkProfileReport(URPGBossFrameworkProfile* Profile);

	/** Native metadata contract used by the Editor automation test; it calls the same runtime validator. */
	static bool ValidateMoveCardMetadata(const FRPGBossMoveCardSpec& Spec, const FRPGBossMoveMetadata& Metadata,
		TArray<FString>& OutDiagnostics);
};
