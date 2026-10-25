// Copyright One Boss Fight. All Rights Reserved.

#pragma once

#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "Blueprint/UserWidget.h"
#include "Input/Events.h"
#include "Input/Reply.h"
#include "Templates/Atomic.h"
#include "RPGBuildSelect.generated.h"

class UCanvasPanel;
class UImage;
class UTextBlock;
class UTexture2D;
class UInputComponent;
class FRPGBuildSelectKeyListener;

UCLASS()
class ONEBOSSFIGHT_API URPGBuildSelectWidget : public UUserWidget
{
	GENERATED_BODY()

public:
	URPGBuildSelectWidget(const FObjectInitializer& ObjectInitializer);

	void SetSelector(class URPGBuildSelect* InSelector);

protected:
	virtual TSharedRef<SWidget> RebuildWidget() override;
	virtual FReply NativeOnMouseButtonDown(const FGeometry& InGeometry, const FPointerEvent& InMouseEvent) override;
	virtual FReply NativeOnKeyDown(const FGeometry& InGeometry, const FKeyEvent& InKeyEvent) override;

private:
	class URPGBuildSelect* Selector = nullptr;
	UTextBlock* TitleText = nullptr;
	TArray<UTextBlock*> Rows;
	TArray<UImage*> Icons;
};

/** Pre-fight build chooser (G3-5): a raw B-key panel that delegates every choice to URPGBuildLoadout. */
UCLASS(ClassGroup = (Player))
class ONEBOSSFIGHT_API URPGBuildSelect : public UActorComponent
{
	GENERATED_BODY()

public:
	URPGBuildSelect();
	bool Open();
	void Close();
	FString Pick(FName Build);

	UFUNCTION(BlueprintPure, Category = "Build Select")
	bool IsOpen() const { return bOpen; }

	UFUNCTION(BlueprintCallable, Category = "Build Select")
	bool OpenForTest();

	UFUNCTION(BlueprintCallable, Category = "Build Select")
	void CloseForTest();

	UFUNCTION(BlueprintCallable, Category = "Build Select")
	FString PickForTest(FName Build);

	UFUNCTION(BlueprintPure, Category = "Build Select")
	FString GetLastPickResult() const { return LastPickResult; }

	UFUNCTION(BlueprintPure, Category = "Build Select")
	FString GetRowText(int32 Row) const;

	/** Optional art for one build row. A missing texture leaves its existing text-only row intact. */
	UTexture2D* GetRowIcon(int32 Row) const;

	void OnWidgetRowClicked(int32 Row);

protected:
	virtual void BeginPlay() override;
	virtual void EndPlay(const EEndPlayReason::Type EndPlayReason) override;
	virtual void TickComponent(float DeltaTime, ELevelTick TickType, FActorComponentTickFunction* ThisTickFunction) override;

private:
	friend class FRPGBuildSelectKeyListener;

	bool CanOpen(FString& OutWhy) const;
	void Toggle();
	void EnsureWidget();
	void RegisterKeyListener();
	void UnregisterKeyListener();
	void NoteBKeyDown();
	bool ConsumeBKeyDown();
	class URPGBuildLoadout* GetLoadout() const;
	class APlayerController* GetController() const;
	void LoadRowIcons();

	UPROPERTY(Transient)
	TObjectPtr<URPGBuildSelectWidget> Widget;

	UPROPERTY(Transient)
	TArray<TObjectPtr<UTexture2D>> RowIcons;
	TSharedPtr<FRPGBuildSelectKeyListener> KeyListener;
	TAtomic<bool> bBKeyPending = false;
	bool bOpen = false;
	FString LastPickResult = TEXT("not picked");
};
