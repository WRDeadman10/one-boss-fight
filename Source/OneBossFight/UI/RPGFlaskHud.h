// Copyright One Boss Fight. All Rights Reserved.

#pragma once

#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "Blueprint/UserWidget.h"
#include "UI/RPGFlaskHudRules.h"
#include "RPGFlaskHud.generated.h"

class UCanvasPanel;
class UImage;
class UTextBlock;
class UTexture2D;

UCLASS()
class ONEBOSSFIGHT_API URPGFlaskHudWidget : public UUserWidget
{
	GENERATED_BODY()

public:
	void Apply(RPGFlaskHudRules::EFill Fill, int32 Count, UTexture2D* Plate, UTexture2D* Full, UTexture2D* Half, UTexture2D* Empty);

protected:
	virtual TSharedRef<SWidget> RebuildWidget() override;

private:
	UPROPERTY(Transient)
	TObjectPtr<UImage> PlateImage;
	UPROPERTY(Transient)
	TObjectPtr<UImage> FlaskImage;
	UPROPERTY(Transient)
	TObjectPtr<UTextBlock> CountText;
};

/** Own HUD overlay for the pack health-potion stack. It reads the live HealthPotion item amount by reflection and never changes the pack widget or item. */
UCLASS(ClassGroup = (Player))
class ONEBOSSFIGHT_API URPGFlaskHud : public UActorComponent
{
	GENERATED_BODY()

public:
	URPGFlaskHud();

	UFUNCTION(BlueprintPure, Category = "Flask HUD")
	int32 GetFlaskCount() const { return FlaskCount; }

	UFUNCTION(BlueprintPure, Category = "Flask HUD")
	int32 GetFlaskMaximum() const { return StartingCount; }

	UFUNCTION(BlueprintPure, Category = "Flask HUD")
	FString GetFlaskFillState() const { return RPGFlaskHudRules::FillName(RPGFlaskHudRules::DecideFill(FlaskCount, StartingCount)); }

	UFUNCTION(BlueprintPure, Category = "Flask HUD")
	bool IsOverlayShown() const { return Widget && Widget->GetVisibility() != ESlateVisibility::Collapsed; }

	/** Test driver hook: reads the pack item immediately; it never writes or consumes it. */
	UFUNCTION(BlueprintCallable, Category = "Flask HUD")
	void RefreshForTest();

protected:
	virtual void BeginPlay() override;
	virtual void EndPlay(const EEndPlayReason::Type EndPlayReason) override;
	virtual void TickComponent(float DeltaTime, ELevelTick TickType, FActorComponentTickFunction* ThisTickFunction) override;

private:
	void LoadArt();
	void EnsureWidget();
	void Refresh();
	bool ReadHealthPotionCount(int32& OutCount) const;

	UPROPERTY(Transient)
	TObjectPtr<URPGFlaskHudWidget> Widget;
	UPROPERTY(Transient)
	TObjectPtr<UTexture2D> PlateTexture;
	UPROPERTY(Transient)
	TObjectPtr<UTexture2D> FullTexture;
	UPROPERTY(Transient)
	TObjectPtr<UTexture2D> HalfTexture;
	UPROPERTY(Transient)
	TObjectPtr<UTexture2D> EmptyTexture;

	int32 FlaskCount = -1;
	int32 StartingCount = 0;
	bool bArtReady = false;
};
