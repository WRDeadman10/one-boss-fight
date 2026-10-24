// Copyright One Boss Fight. All Rights Reserved.

#include "UI/RPGFlaskHud.h"

#include "Blueprint/WidgetTree.h"
#include "Components/CanvasPanel.h"
#include "Components/CanvasPanelSlot.h"
#include "Components/Image.h"
#include "Components/TextBlock.h"
#include "Engine/Texture2D.h"
#include "GameFramework/Pawn.h"
#include "GameFramework/PlayerController.h"
#include "Pack/RPGBlueprintCall.h"
#include "Styling/CoreStyle.h"
#include "UObject/SoftObjectPath.h"
#include "UObject/UnrealType.h"

namespace
{
	const FProperty* FieldByPrefix(const UStruct* Struct, const TCHAR* Prefix)
	{
		if (!Struct)
		{
			return nullptr;
		}
		for (TFieldIterator<FProperty> It(Struct); It; ++It)
		{
			if (It->GetName().StartsWith(Prefix))
			{
				return *It;
			}
		}
		return nullptr;
	}

	bool ReadInteger(const FProperty* Property, const void* Container, int32& OutValue)
	{
		if (const FNumericProperty* Number = CastField<FNumericProperty>(Property))
		{
			const void* Value = Number->ContainerPtrToValuePtr<void>(Container);
			OutValue = Number->IsFloatingPoint() ? FMath::RoundToInt(Number->GetFloatingPointPropertyValue(Value)) : static_cast<int32>(Number->GetSignedIntPropertyValue(Value));
			return true;
		}
		return false;
	}

	UCanvasPanelSlot* AddCanvasChild(UCanvasPanel* Canvas, UWidget* Widget, const FVector2D& Position, const FVector2D& Size, const FVector2D& Alignment)
	{
		UCanvasPanelSlot* Slot = Canvas->AddChildToCanvas(Widget);
		Slot->SetAnchors(FAnchors(0.f, 1.f));
		Slot->SetAlignment(Alignment);
		Slot->SetPosition(Position);
		Slot->SetSize(Size);
		return Slot;
	}
}

TSharedRef<SWidget> URPGFlaskHudWidget::RebuildWidget()
{
	if (WidgetTree && !WidgetTree->RootWidget)
	{
		UCanvasPanel* Canvas = WidgetTree->ConstructWidget<UCanvasPanel>(UCanvasPanel::StaticClass(), TEXT("FlaskHudCanvas"));
		WidgetTree->RootWidget = Canvas;
		PlateImage = WidgetTree->ConstructWidget<UImage>(UImage::StaticClass(), TEXT("FlaskPlate"));
		FlaskImage = WidgetTree->ConstructWidget<UImage>(UImage::StaticClass(), TEXT("FlaskIcon"));
		CountText = WidgetTree->ConstructWidget<UTextBlock>(UTextBlock::StaticClass(), TEXT("FlaskCount"));
		CountText->SetFont(FSlateFontInfo(FCoreStyle::GetDefaultFontStyle("Bold", 32)));
		CountText->SetColorAndOpacity(FSlateColor(FLinearColor(0.95f, 0.79f, 0.39f)));
		CountText->SetJustification(ETextJustify::Center);
		CountText->SetShadowOffset(FVector2D(2.f, 2.f));
		CountText->SetShadowColorAndOpacity(FLinearColor(0.f, 0.f, 0.f, 0.9f));
		PlateImage->SetVisibility(ESlateVisibility::HitTestInvisible);
		FlaskImage->SetVisibility(ESlateVisibility::HitTestInvisible);
		CountText->SetVisibility(ESlateVisibility::HitTestInvisible);
		AddCanvasChild(Canvas, PlateImage, FVector2D(22.f, -22.f), FVector2D(160.f, 96.f), FVector2D(0.f, 1.f));
		AddCanvasChild(Canvas, FlaskImage, FVector2D(33.f, -33.f), FVector2D(68.f, 74.f), FVector2D(0.f, 1.f));
		AddCanvasChild(Canvas, CountText, FVector2D(117.f, -70.f), FVector2D(64.f, 44.f), FVector2D(0.5f, 0.5f));
	}
	return Super::RebuildWidget();
}

void URPGFlaskHudWidget::Apply(RPGFlaskHudRules::EFill Fill, int32 Count, UTexture2D* Plate, UTexture2D* Full, UTexture2D* Half, UTexture2D* Empty)
{
	if (!PlateImage || !FlaskImage || !CountText)
	{
		return;
	}
	UTexture2D* Flask = Fill == RPGFlaskHudRules::EFill::Full ? Full : Fill == RPGFlaskHudRules::EFill::Half ? Half : Fill == RPGFlaskHudRules::EFill::Empty ? Empty : nullptr;
	if (!Plate || !Flask)
	{
		SetVisibility(ESlateVisibility::Collapsed);
		return;
	}
	PlateImage->SetBrushFromTexture(Plate, true);
	FlaskImage->SetBrushFromTexture(Flask, true);
	CountText->SetText(FText::AsNumber(Count));
	SetVisibility(ESlateVisibility::HitTestInvisible);
}

URPGFlaskHud::URPGFlaskHud()
{
	PrimaryComponentTick.bCanEverTick = true;
	PrimaryComponentTick.TickInterval = 0.2f;
}

void URPGFlaskHud::BeginPlay()
{
	Super::BeginPlay();
	LoadArt();
	Refresh();
}

void URPGFlaskHud::EndPlay(const EEndPlayReason::Type EndPlayReason)
{
	if (Widget)
	{
		Widget->RemoveFromParent();
		Widget = nullptr;
	}
	Super::EndPlay(EndPlayReason);
}

void URPGFlaskHud::TickComponent(float DeltaTime, ELevelTick TickType, FActorComponentTickFunction* ThisTickFunction)
{
	Super::TickComponent(DeltaTime, TickType, ThisTickFunction);
	Refresh();
}

void URPGFlaskHud::LoadArt()
{
	auto Load = [](const TCHAR* Path) { return TSoftObjectPtr<UTexture2D>(FSoftObjectPath(Path)).LoadSynchronous(); };
	PlateTexture = Load(TEXT("/Game/OneBossFight/UI/Art/T_Boss01_FlaskPlate.T_Boss01_FlaskPlate"));
	FullTexture = Load(TEXT("/Game/OneBossFight/UI/Art/T_Boss01_Flask_Full.T_Boss01_Flask_Full"));
	HalfTexture = Load(TEXT("/Game/OneBossFight/UI/Art/T_Boss01_Flask_Half.T_Boss01_Flask_Half"));
	EmptyTexture = Load(TEXT("/Game/OneBossFight/UI/Art/T_Boss01_Flask_Empty.T_Boss01_Flask_Empty"));
	bArtReady = PlateTexture && FullTexture && HalfTexture && EmptyTexture;
}

void URPGFlaskHud::EnsureWidget()
{
	if (Widget || !bArtReady)
	{
		return;
	}
	const APawn* Pawn = Cast<APawn>(GetOwner());
	APlayerController* Controller = Pawn ? Cast<APlayerController>(Pawn->GetController()) : nullptr;
	if (Controller && Controller->IsLocalController())
	{
		Widget = CreateWidget<URPGFlaskHudWidget>(Controller, URPGFlaskHudWidget::StaticClass());
		if (Widget)
		{
			Widget->AddToViewport(60);
		}
	}
}

void URPGFlaskHud::Refresh()
{
	int32 Count = -1;
	if (!bArtReady || !ReadHealthPotionCount(Count))
	{
		return;
	}
	FlaskCount = Count;
	StartingCount = FMath::Max(StartingCount, Count);
	EnsureWidget();
	if (Widget)
	{
		Widget->Apply(RPGFlaskHudRules::DecideFill(FlaskCount, StartingCount), FlaskCount, PlateTexture, FullTexture, HalfTexture, EmptyTexture);
	}
}

void URPGFlaskHud::RefreshForTest()
{
	Refresh();
}

bool URPGFlaskHud::ReadHealthPotionCount(int32& OutCount) const
{
	OutCount = -1;
	UObject* Equipment = RPGPack::FindComponentByClassName(GetOwner(), TEXT("BP_EquipmentComponent_C"));
	const FArrayProperty* Slots = Equipment ? CastField<FArrayProperty>(Equipment->GetClass()->FindPropertyByName(TEXT("EquipmentSlots"))) : nullptr;
	const FStructProperty* SlotStruct = Slots ? CastField<FStructProperty>(Slots->Inner) : nullptr;
	const FArrayProperty* Items = SlotStruct ? CastField<FArrayProperty>(FieldByPrefix(SlotStruct->Struct, TEXT("Items_"))) : nullptr;
	const FStructProperty* ItemStruct = Items ? CastField<FStructProperty>(Items->Inner) : nullptr;
	const FObjectPropertyBase* ItemObject = ItemStruct ? CastField<FObjectPropertyBase>(FieldByPrefix(ItemStruct->Struct, TEXT("Item_"))) : nullptr;
	const FProperty* Amount = ItemStruct ? FieldByPrefix(ItemStruct->Struct, TEXT("Amount_")) : nullptr;
	if (!Slots || !Items || !ItemObject || !Amount)
	{
		return false;
	}
	FScriptArrayHelper SlotArray(Slots, Slots->ContainerPtrToValuePtr<void>(Equipment));
	for (int32 SlotIndex = 0; SlotIndex < SlotArray.Num(); ++SlotIndex)
	{
		FScriptArrayHelper ItemArray(Items, Items->ContainerPtrToValuePtr<void>(SlotArray.GetRawPtr(SlotIndex)));
		for (int32 ItemIndex = 0; ItemIndex < ItemArray.Num(); ++ItemIndex)
		{
			void* ItemData = ItemArray.GetRawPtr(ItemIndex);
			UObject* Item = ItemObject->GetObjectPropertyValue(ItemObject->ContainerPtrToValuePtr<void>(ItemData));
			if (!Item || !Item->GetName().Contains(TEXT("HealthPotion")))
			{
				continue;
			}
			return ReadInteger(Amount, ItemData, OutCount);
		}
	}
	return false;
}
