// Copyright One Boss Fight. All Rights Reserved.

#include "UI/RPGBuildSelect.h"
#include "UI/RPGBuildSelectRules.h"
#include "Blueprint/WidgetTree.h"
#include "Components/CanvasPanel.h"
#include "Components/CanvasPanelSlot.h"
#include "Components/Image.h"
#include "Components/TextBlock.h"
#include "Components/InputComponent.h"
#include "CoreGlobals.h"
#include "Engine/World.h"
#include "Engine/Texture2D.h"
#include "Framework/Application/IInputProcessor.h"
#include "Framework/Application/SlateApplication.h"
#include "GameFramework/Character.h"
#include "GameFramework/CharacterMovementComponent.h"
#include "GameFramework/PlayerController.h"
#include "Input/Reply.h"
#include "Input/Events.h"
#include "InputCoreTypes.h"
#include "Kismet/GameplayStatics.h"
#include "Pack/RPGBlueprintCall.h"
#include "Player/RPGBossEncounter.h"
#include "Player/RPGBossPhases.h"
#include "Player/RPGBuildLoadout.h"
#include "Player/RPGPlayerMovesSubsystem.h"
#include "Styling/CoreStyle.h"
#include "EngineUtils.h"
#include "Misc/CoreMisc.h"
#include "UObject/SoftObjectPath.h"

class FRPGBuildSelectKeyListener final : public IInputProcessor
{
public:
	explicit FRPGBuildSelectKeyListener(URPGBuildSelect* InOwner)
		: Owner(InOwner)
	{
	}

	virtual void Tick(const float DeltaTime, FSlateApplication& SlateApp, TSharedRef<ICursor> Cursor) override
	{
	}

	virtual bool HandleKeyDownEvent(FSlateApplication& SlateApp, const FKeyEvent& InKeyEvent) override
	{
		if (!InKeyEvent.IsRepeat() && InKeyEvent.GetKey() == EKeys::B)
		{
			if (URPGBuildSelect* LiveOwner = Owner.Get())
			{
				LiveOwner->NoteBKeyDown();
			}
		}
		return false;
	}

	virtual const TCHAR* GetDebugName() const override
	{
		return TEXT("RPGBuildSelectKeyListener");
	}

private:
	TWeakObjectPtr<URPGBuildSelect> Owner;
};

namespace
{
	UTextBlock* AddText(UWidgetTree* Tree, UCanvasPanel* Canvas, const TCHAR* Name, const FVector2D& Position, int32 Size)
	{
		UTextBlock* Text = Tree->ConstructWidget<UTextBlock>(UTextBlock::StaticClass(), Name);
		Text->SetColorAndOpacity(FSlateColor(FLinearColor(0.93f, 0.8f, 0.45f)));
		Text->SetShadowOffset(FVector2D(2.f, 2.f));
		Text->SetShadowColorAndOpacity(FLinearColor(0.f, 0.f, 0.f, 0.85f));
		Text->SetFont(FSlateFontInfo(FCoreStyle::GetDefaultFontStyle("Bold", Size)));
		UCanvasPanelSlot* Slot = Canvas->AddChildToCanvas(Text);
		Slot->SetAnchors(FAnchors(0.5f, 0.25f));
		Slot->SetAlignment(FVector2D(0.5f, 0.f));
		Slot->SetPosition(Position);
		Slot->SetAutoSize(true);
		return Text;
	}

	UImage* AddIcon(UWidgetTree* Tree, UCanvasPanel* Canvas, const TCHAR* Name, const FVector2D& Position)
	{
		UImage* Image = Tree->ConstructWidget<UImage>(UImage::StaticClass(), Name);
		Image->SetVisibility(ESlateVisibility::HitTestInvisible);
		UCanvasPanelSlot* Slot = Canvas->AddChildToCanvas(Image);
		Slot->SetAnchors(FAnchors(0.5f, 0.25f));
		Slot->SetAlignment(FVector2D(1.f, 0.5f));
		Slot->SetPosition(Position);
		Slot->SetSize(FVector2D(32.f, 32.f));
		return Image;
	}
}

URPGBuildSelectWidget::URPGBuildSelectWidget(const FObjectInitializer& ObjectInitializer)
	: Super(ObjectInitializer)
{
	bIsFocusable = true;
}

void URPGBuildSelectWidget::SetSelector(URPGBuildSelect* InSelector)
{
	Selector = InSelector;
	for (int32 Row = 0; Row < Rows.Num(); ++Row)
	{
		Rows[Row]->SetText(FText::FromString(FString::Printf(TEXT("%d  %s"), Row + 1, *Selector->GetRowText(Row))));
		if (Icons.IsValidIndex(Row))
		{
			if (UTexture2D* Icon = Selector->GetRowIcon(Row))
			{
				Icons[Row]->SetBrushFromTexture(Icon, true);
				Icons[Row]->SetVisibility(ESlateVisibility::HitTestInvisible);
			}
			else
			{
				Icons[Row]->SetVisibility(ESlateVisibility::Collapsed);
			}
		}
	}
}

TSharedRef<SWidget> URPGBuildSelectWidget::RebuildWidget()
{
	if (WidgetTree && !WidgetTree->RootWidget)
	{
		UCanvasPanel* Canvas = WidgetTree->ConstructWidget<UCanvasPanel>(UCanvasPanel::StaticClass(), TEXT("BuildSelectCanvas"));
		WidgetTree->RootWidget = Canvas;
		TitleText = AddText(WidgetTree, Canvas, TEXT("BuildSelectTitle"), FVector2D(0.f, 0.f), 30);
		TitleText->SetText(FText::FromString(TEXT("CHOOSE YOUR BUILD")));
		for (int32 Row = 0; Row < 3; ++Row)
		{
			UTextBlock* Text = AddText(WidgetTree, Canvas, *FString::Printf(TEXT("BuildRow%d"), Row), FVector2D(0.f, 52.f + Row * 42.f), 20);
			Rows.Add(Text);
			Icons.Add(AddIcon(WidgetTree, Canvas, *FString::Printf(TEXT("BuildIcon%d"), Row), FVector2D(-112.f, 68.f + Row * 42.f)));
		}
	}
	return Super::RebuildWidget();
}

FReply URPGBuildSelectWidget::NativeOnMouseButtonDown(const FGeometry& InGeometry, const FPointerEvent& InMouseEvent)
{
	if (Selector && InMouseEvent.GetEffectingButton() == EKeys::LeftMouseButton)
	{
		const float LocalY = InGeometry.AbsoluteToLocal(InMouseEvent.GetScreenSpacePosition()).Y;
		const float RowsTop = InGeometry.GetLocalSize().Y * 0.25f + 52.f;
		const int32 Row = FMath::FloorToInt((LocalY - RowsTop) / 42.f);
		if (Rows.IsValidIndex(Row))
		{
			Selector->OnWidgetRowClicked(Row);
			return FReply::Handled();
		}
	}
	return Super::NativeOnMouseButtonDown(InGeometry, InMouseEvent);
}

FReply URPGBuildSelectWidget::NativeOnKeyDown(const FGeometry& InGeometry, const FKeyEvent& InKeyEvent)
{
	if (!Selector)
	{
		return Super::NativeOnKeyDown(InGeometry, InKeyEvent);
	}
	const FKey Key = InKeyEvent.GetKey();
	if (Key == EKeys::B || Key == EKeys::Escape)
	{
		Selector->Close();
		return FReply::Handled();
	}
	if (Key == EKeys::One || Key == EKeys::Two || Key == EKeys::Three)
	{
		Selector->OnWidgetRowClicked(Key == EKeys::One ? 0 : Key == EKeys::Two ? 1 : 2);
		return FReply::Handled();
	}
	return Super::NativeOnKeyDown(InGeometry, InKeyEvent);
}

URPGBuildSelect::URPGBuildSelect()
{
	PrimaryComponentTick.bCanEverTick = true;
	PrimaryComponentTick.TickInterval = 0.1f; // Slate records B edges; this tick consumes them ten times a second. No controller binding or per-frame component poll: both correlated with boss-AI stalls in pie_attack_rules (2026-10-23).
}

void URPGBuildSelect::BeginPlay()
{
	Super::BeginPlay();
	LoadRowIcons();
	bBKeyPending.Store(false);
	RegisterKeyListener();
}

void URPGBuildSelect::LoadRowIcons()
{
	static const TCHAR* Paths[] =
	{
		TEXT("/Game/OneBossFight/UI/Art/T_Boss01_Icon_Starter.T_Boss01_Icon_Starter"),
		TEXT("/Game/OneBossFight/UI/Art/T_Boss01_Icon_Strength.T_Boss01_Icon_Strength"),
		TEXT("/Game/OneBossFight/UI/Art/T_Boss01_Icon_Dex.T_Boss01_Icon_Dex")
	};
	RowIcons.Reset();
	for (const TCHAR* Path : Paths)
	{
		RowIcons.Add(TSoftObjectPtr<UTexture2D>(FSoftObjectPath(Path)).LoadSynchronous());
	}
}

UTexture2D* URPGBuildSelect::GetRowIcon(int32 Row) const
{
	return RowIcons.IsValidIndex(Row) ? RowIcons[Row].Get() : nullptr;
}

void URPGBuildSelect::EndPlay(const EEndPlayReason::Type EndPlayReason)
{
	UnregisterKeyListener();
	bBKeyPending.Store(false);
	Close();
	if (Widget)
	{
		Widget->RemoveFromParent();
		Widget = nullptr;
	}
	Super::EndPlay(EndPlayReason);
}

void URPGBuildSelect::TickComponent(float DeltaTime, ELevelTick TickType, FActorComponentTickFunction* ThisTickFunction)
{
	Super::TickComponent(DeltaTime, TickType, ThisTickFunction);
	if (!bOpen && ConsumeBKeyDown())
	{
		FString Why;
		if (CanOpen(Why))
		{
			Open();
		}
	}
	if (bOpen)
	{
		FString Why;
		if (!CanOpen(Why))
		{
			LastPickResult = Why;
			Close();
		}
	}
}

void URPGBuildSelect::RegisterKeyListener()
{
	UWorld* World = GetWorld();
	APlayerController* Controller = GetController();
	if (!World || !World->IsGameWorld() || !Controller || !Controller->IsLocalController()
		|| IsRunningDedicatedServer() || IsRunningCommandlet() || !FSlateApplication::IsInitialized())
	{
		return;
	}

	KeyListener = MakeShared<FRPGBuildSelectKeyListener>(this);
	if (!FSlateApplication::Get().RegisterInputPreProcessor(KeyListener))
	{
		KeyListener.Reset();
	}
}

void URPGBuildSelect::UnregisterKeyListener()
{
	if (KeyListener.IsValid() && FSlateApplication::IsInitialized())
	{
		FSlateApplication::Get().UnregisterInputPreProcessor(KeyListener);
	}
	KeyListener.Reset();
}

void URPGBuildSelect::NoteBKeyDown()
{
	bBKeyPending.Store(true);
}

bool URPGBuildSelect::ConsumeBKeyDown()
{
	return bBKeyPending.Exchange(false);
}

APlayerController* URPGBuildSelect::GetController() const
{
	const APawn* Pawn = Cast<APawn>(GetOwner());
	return Pawn ? Cast<APlayerController>(Pawn->GetController()) : nullptr;
}

URPGBuildLoadout* URPGBuildSelect::GetLoadout() const
{
	return GetOwner() ? GetOwner()->FindComponentByClass<URPGBuildLoadout>() : nullptr;
}

bool URPGBuildSelect::CanOpen(FString& OutWhy) const
{
	const ACharacter* Character = Cast<ACharacter>(GetOwner());
	const UCharacterMovementComponent* Movement = Character ? Character->GetCharacterMovement() : nullptr;
	double Health = 0.0;
	const bool bAlive = Character && RPGPack::ReadAttribute(Character, TEXT("Attribute.Health"), false, Health) && Health > 0.0;
	const bool bGrounded = Movement && Movement->IsMovingOnGround();
	const UWorld* World = GetWorld();
	URPGBossEncounter* Encounter = nullptr;
	URPGBossPhases* Phases = nullptr;
	if (World)
	{
		for (TActorIterator<APawn> It(World); It; ++It)
		{
			if (URPGPlayerMovesSubsystem::IsPackBoss(*It))
			{
				Encounter = It->FindComponentByClass<URPGBossEncounter>();
				Phases = It->FindComponentByClass<URPGBossPhases>();
				break;
			}
		}
	}
	const bool bDormant = Encounter && Encounter->IsDormant();
	const bool bTransition = Phases && Phases->IsInTransition();
	if (!RPGBuildSelectRules::CanOpen(bDormant, bAlive, bGrounded, bTransition))
	{
		OutWhy = !bDormant ? TEXT("the boss is awake") : !bAlive ? TEXT("the player is dead") : !bGrounded ? TEXT("the player is not grounded") : TEXT("the boss is transitioning");
		return false;
	}
	return true;
}

void URPGBuildSelect::EnsureWidget()
{
	if (Widget)
	{
		return;
	}
	if (APlayerController* Controller = GetController())
	{
		Widget = CreateWidget<URPGBuildSelectWidget>(Controller, URPGBuildSelectWidget::StaticClass());
		if (Widget)
		{
			Widget->AddToViewport(30);
			Widget->SetSelector(this);
		}
	}
}

void URPGBuildSelect::Toggle()
{
	if (bOpen)
	{
		Close();
	}
	else
	{
		Open();
	}
}

bool URPGBuildSelect::Open()
{
	FString Why;
	if (!CanOpen(Why))
	{
		LastPickResult = Why;
		return false;
	}
	EnsureWidget();
	if (!Widget)
	{
		LastPickResult = TEXT("the selector widget could not be created");
		return false;
	}
	bOpen = true;
	Widget->SetVisibility(ESlateVisibility::Visible);
	if (APlayerController* Controller = GetController())
	{
		FInputModeUIOnly InputMode;
		InputMode.SetWidgetToFocus(Widget->TakeWidget());
		InputMode.SetLockMouseToViewportBehavior(EMouseLockMode::DoNotLock);
		Controller->SetInputMode(InputMode);
		Controller->bShowMouseCursor = true;
	}
	LastPickResult = TEXT("opened");
	return true;
}

void URPGBuildSelect::Close()
{
	bBKeyPending.Store(false);
	if (!bOpen)
	{
		return; // Escape is bound on the controller for the whole game: a closed selector must not touch the input mode or the cursor
	}
	bOpen = false;
	if (Widget)
	{
		Widget->SetVisibility(ESlateVisibility::Collapsed);
	}
	if (APlayerController* Controller = GetController())
	{
		Controller->SetInputMode(FInputModeGameOnly());
		Controller->bShowMouseCursor = false;
	}
}

FString URPGBuildSelect::Pick(FName Build)
{
	ERPGBuild Parsed = ERPGBuild::Starter;
	if (!bOpen || !RPGBuildSelectRules::ParseBuild(Build, Parsed))
	{
		LastPickResult = bOpen ? TEXT("invalid build") : TEXT("not open");
		return LastPickResult;
	}
	URPGBuildLoadout* Loadout = GetLoadout();
	if (!Loadout)
	{
		LastPickResult = TEXT("no build loadout");
		return LastPickResult;
	}
	if (Loadout->HasChoice() && Loadout->GetChosenBuildName().Equals(Build.ToString(), ESearchCase::IgnoreCase))
	{
		LastPickResult = TEXT("Same");
		Close();
		return LastPickResult;
	}
	LastPickResult = Loadout->SetBuild(Build.ToString());
	Close();
	return LastPickResult;
}

FString URPGBuildSelect::GetRowText(int32 Row) const
{
	return RPGBuildSelectRules::RowText(Row);
}

void URPGBuildSelect::OnWidgetRowClicked(int32 Row)
{
	ERPGBuild Build = ERPGBuild::Starter;
	if (RPGBuildSelectRules::BuildForRow(Row, Build))
	{
		Pick(FName(RPGBuildRules::BuildName(Build)));
	}
}

bool URPGBuildSelect::OpenForTest()
{
#if UE_BUILD_SHIPPING
	return false;
#else
	return Open();
#endif
}

void URPGBuildSelect::CloseForTest()
{
#if !UE_BUILD_SHIPPING
	Close();
#endif
}

FString URPGBuildSelect::PickForTest(FName Build)
{
#if UE_BUILD_SHIPPING
	return TEXT("unavailable in Shipping");
#else
	return Pick(Build);
#endif
}
