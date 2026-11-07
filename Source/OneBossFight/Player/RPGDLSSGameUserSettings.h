// Copyright One Boss Fight. All Rights Reserved.

#pragma once

#include "CoreMinimal.h"
#include "GameFramework/GameUserSettings.h"
#include "RPGDLSSGameUserSettings.generated.h"

UENUM(BlueprintType)
enum class ERPGDLSSPlayerMode : uint8
{
	Off UMETA(DisplayName = "Off (TSR)"),
	DLAA UMETA(DisplayName = "DLAA"),
	Quality UMETA(DisplayName = "Quality"),
	Balanced UMETA(DisplayName = "Balanced"),
	Performance UMETA(DisplayName = "Performance")
};

/** Persistent player preference for DLSS Super Resolution. Off is the unchanged TSR fallback. */
UCLASS(Config = GameUserSettings)
class ONEBOSSFIGHT_API URPGDLSSGameUserSettings : public UGameUserSettings
{
	GENERATED_BODY()

public:
	UPROPERTY(Config, BlueprintReadOnly, Category = "Graphics|Upscaling")
	ERPGDLSSPlayerMode DLSSPlayerMode = ERPGDLSSPlayerMode::Off;

	UFUNCTION(BlueprintCallable, Category = "Graphics|Upscaling")
	void SetDLSSPlayerMode(ERPGDLSSPlayerMode NewMode);

	UFUNCTION(BlueprintPure, Category = "Graphics|Upscaling")
	ERPGDLSSPlayerMode GetDLSSPlayerMode() const { return DLSSPlayerMode; }

	virtual void ApplySettings(bool bCheckForCommandLineOverrides) override;

private:
	void ApplyDLSSPlayerMode();
};
