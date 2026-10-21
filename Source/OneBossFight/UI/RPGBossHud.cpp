// Copyright One Boss Fight. All Rights Reserved.

#include "UI/RPGBossHud.h"
#include "Blueprint/WidgetTree.h"
#include "Components/Border.h"
#include "Components/CanvasPanel.h"
#include "Components/CanvasPanelSlot.h"
#include "Components/ProgressBar.h"
#include "Components/TextBlock.h"
#include "Engine/Font.h"
#include "Engine/World.h"
#include "GameFramework/PlayerController.h"
#include "Pack/RPGBlueprintCall.h"
#include "Player/RPGBossEncounter.h"
#include "Player/RPGBossPhases.h"
#include "Player/RPGBossPosture.h"
#include "Player/RPGBossStagger.h"
#include "Kismet/GameplayStatics.h"
#include "InputCoreTypes.h"
#include "Styling/CoreStyle.h"

DEFINE_LOG_CATEGORY_STATIC(LogRPGBossHud, Log, All);

namespace
{
	// The pack ships the Cinzel display font; the engine font is the fallback when the asset is missing.
	FSlateFontInfo MakeFont(int32 Size)
	{
		static TWeakObjectPtr<UObject> Cached;
		if (!Cached.IsValid())
		{
			Cached = LoadObject<UObject>(nullptr, TEXT("/Game/AdvancedARPGCombat/MeleeCombatSystem/UI/Fonts/Cinzel/Cinzel.Cinzel"));
		}
		if (Cached.IsValid())
		{
			return FSlateFontInfo(Cached.Get(), Size);
		}
		return FCoreStyle::GetDefaultFontStyle("Bold", Size);
	}
}

// ---------------------------------------------------------------------------------------------------------------------------------- widget

UTextBlock* URPGBossHudWidget::AddText(UCanvasPanel* Canvas, const TCHAR* WidgetName, const FVector2D& Anchor, const FVector2D& Alignment, const FVector2D& Position, int32 FontSize, const FLinearColor& Color)
{
	UTextBlock* Text = WidgetTree->ConstructWidget<UTextBlock>(UTextBlock::StaticClass(), WidgetName);
	Text->SetFont(MakeFont(FontSize));
	Text->SetColorAndOpacity(FSlateColor(Color));
	Text->SetShadowOffset(FVector2D(2.f, 2.f));
	Text->SetShadowColorAndOpacity(FLinearColor(0.f, 0.f, 0.f, 0.85f));
	Text->SetText(FText::GetEmpty());
	UCanvasPanelSlot* PanelSlot = Canvas->AddChildToCanvas(Text);
	PanelSlot->SetAnchors(FAnchors(Anchor.X, Anchor.Y));
	PanelSlot->SetAlignment(Alignment);
	PanelSlot->SetPosition(Position);
	PanelSlot->SetAutoSize(true);
	return Text;
}

UProgressBar* URPGBossHudWidget::AddBar(UCanvasPanel* Canvas, const TCHAR* WidgetName, const FVector2D& Position, const FVector2D& Size, const FLinearColor& Fill, float BackgroundAlpha)
{
	UProgressBar* Bar = WidgetTree->ConstructWidget<UProgressBar>(UProgressBar::StaticClass(), WidgetName);
	// The default style paints a light background behind the unfilled part: make it dark (or clear when another bar or the plate sits behind).
	Bar->WidgetStyle.BackgroundImage.TintColor = FSlateColor(FLinearColor(0.f, 0.f, 0.f, BackgroundAlpha));
	Bar->SetFillColorAndOpacity(Fill);
	Bar->SetPercent(1.f);
	UCanvasPanelSlot* PanelSlot = Canvas->AddChildToCanvas(Bar);
	PanelSlot->SetAnchors(FAnchors(0.5f, 1.f));
	PanelSlot->SetAlignment(FVector2D(0.5f, 1.f));
	PanelSlot->SetPosition(Position);
	PanelSlot->SetSize(Size);
	return Bar;
}

TSharedRef<SWidget> URPGBossHudWidget::RebuildWidget()
{
	if (WidgetTree && !WidgetTree->RootWidget)
	{
		UCanvasPanel* Canvas = WidgetTree->ConstructWidget<UCanvasPanel>(UCanvasPanel::StaticClass(), TEXT("RootCanvas"));
		WidgetTree->RootWidget = Canvas;

		// Bottom centre, the bar is 900 x 14 with a dark plate behind it; name left, subtitle right, above the bar.
		Plate = WidgetTree->ConstructWidget<UBorder>(UBorder::StaticClass(), TEXT("Plate"));
		Plate->SetBrushColor(FLinearColor(0.f, 0.f, 0.f, 0.62f));
		UCanvasPanelSlot* PlateSlot = Canvas->AddChildToCanvas(Plate);
		PlateSlot->SetAnchors(FAnchors(0.5f, 1.f));
		PlateSlot->SetAlignment(FVector2D(0.5f, 1.f));
		PlateSlot->SetPosition(FVector2D(0.f, -52.f));
		PlateSlot->SetSize(FVector2D(912.f, 40.f));

		// Plate spans -92..-52 from the bottom edge; the health bar sits in its upper part, the thin posture bar below it.
		TrailBar = AddBar(Canvas, TEXT("TrailBar"), FVector2D(0.f, -62.f), FVector2D(900.f, 14.f), FLinearColor(0.85f, 0.55f, 0.2f), 0.f);
		HealthBar = AddBar(Canvas, TEXT("HealthBar"), FVector2D(0.f, -62.f), FVector2D(900.f, 14.f), FLinearColor(0.62f, 0.07f, 0.06f), 0.f);
		PostureBar = AddBar(Canvas, TEXT("PostureBar"), FVector2D(0.f, -56.f), FVector2D(900.f, 4.f), FLinearColor(0.82f, 0.68f, 0.3f), 0.5f);

		NameText = AddText(Canvas, TEXT("BossName"), FVector2D(0.5f, 1.f), FVector2D(0.f, 1.f), FVector2D(-450.f, -96.f), 24, FLinearColor(0.92f, 0.87f, 0.74f));
		SubtitleText = AddText(Canvas, TEXT("BossSubtitle"), FVector2D(0.5f, 1.f), FVector2D(1.f, 1.f), FVector2D(450.f, -96.f), 15, FLinearColor(0.85f, 0.6f, 0.3f));
		PromptText = AddText(Canvas, TEXT("RipostePrompt"), FVector2D(0.5f, 0.66f), FVector2D(0.5f, 0.5f), FVector2D::ZeroVector, 22, FLinearColor(0.96f, 0.84f, 0.45f));
		BannerTextBlock = AddText(Canvas, TEXT("Banner"), FVector2D(0.5f, 0.4f), FVector2D(0.5f, 0.5f), FVector2D::ZeroVector, 62, FLinearColor::White);
		RetryTextBlock = AddText(Canvas, TEXT("Retry"), FVector2D(0.5f, 0.62f), FVector2D(0.5f, 0.5f), FVector2D::ZeroVector, 24, FLinearColor(0.93f, 0.88f, 0.75f));

		for (UWidget* Hidden : { static_cast<UWidget*>(Plate), static_cast<UWidget*>(TrailBar), static_cast<UWidget*>(HealthBar), static_cast<UWidget*>(PostureBar), static_cast<UWidget*>(NameText),
			static_cast<UWidget*>(SubtitleText), static_cast<UWidget*>(PromptText), static_cast<UWidget*>(BannerTextBlock), static_cast<UWidget*>(RetryTextBlock) })
		{
			Hidden->SetVisibility(ESlateVisibility::Collapsed);
		}
		bBuilt = true;
	}
	return Super::RebuildWidget();
}

void URPGBossHudWidget::Apply(const FRPGBossHudState& State)
{
	if (!bDetached)
	{
		Current = State;
	}
}

void URPGBossHudWidget::SetBanner(const FText& Text, const FLinearColor& Color, float HoldSeconds)
{
	Banner = Text;
	BannerColor = Color;
	BannerHold = HoldSeconds;
	BannerStart = GetWorld() ? GetWorld()->GetRealTimeSeconds() : 0.0;
}

void URPGBossHudWidget::ClearBanner()
{
	BannerStart = -1.0;
}

void URPGBossHudWidget::EnableRetry(const FText& Text, float DelaySeconds)
{
	bRetryEnabled = true;
	RetryText = Text;
	RetryShowAt = (GetWorld() ? GetWorld()->GetRealTimeSeconds() : 0.0) + DelaySeconds;
}

void URPGBossHudWidget::DisableRetry()
{
	bRetryEnabled = false;
}

bool URPGBossHudWidget::IsRetryShown() const
{
	return bRetryEnabled && GetWorld() && GetWorld()->GetRealTimeSeconds() >= RetryShowAt;
}

void URPGBossHudWidget::Detach()
{
	bDetached = true;
	Current = FRPGBossHudState();
}

float URPGBossHudWidget::BannerAlpha() const
{
	const UWorld* World = GetWorld();
	if (BannerStart < 0.0 || !World)
	{
		return 0.f;
	}
	const float Elapsed = static_cast<float>(World->GetRealTimeSeconds() - BannerStart);
	const float FadeIn = 0.6f;
	const float FadeOut = 1.0f;
	if (Elapsed < FadeIn)
	{
		return Elapsed / FadeIn;
	}
	if (Elapsed < FadeIn + BannerHold)
	{
		return 1.f;
	}
	return FMath::Max(0.f, 1.f - (Elapsed - FadeIn - BannerHold) / FadeOut);
}

void URPGBossHudWidget::NativeTick(const FGeometry& MyGeometry, float InDeltaTime)
{
	Super::NativeTick(MyGeometry, InDeltaTime);
	if (!bBuilt)
	{
		return;
	}
	const float Alpha = BannerAlpha();
	if (bDetached && Alpha <= 0.f && !bRetryEnabled)
	{
		RemoveFromParent();
		return;
	}
	const bool bRetry = IsRetryShown();
	RetryTextBlock->SetVisibility(bRetry ? ESlateVisibility::HitTestInvisible : ESlateVisibility::Collapsed);
	RetryTextBlock->SetText(RetryText);
	if (bRetry)
	{
		// The player's own input is disabled after a victory; these keys are read from the controller directly.
		if (APlayerController* Controller = GetOwningPlayer())
		{
			if (Controller->WasInputKeyJustPressed(EKeys::R) || Controller->WasInputKeyJustPressed(EKeys::Gamepad_FaceButton_Top))
			{
				bRetryEnabled = false;
				UE_LOG(LogRPGBossHud, Log, TEXT("retry: reloading the level"));
				UGameplayStatics::OpenLevel(this, FName(*UGameplayStatics::GetCurrentLevelName(this, true)));
				return;
			}
		}
	}
	const ESlateVisibility BarVisibility = Current.bShowBar ? ESlateVisibility::HitTestInvisible : ESlateVisibility::Collapsed;
	for (UWidget* Part : { static_cast<UWidget*>(Plate), static_cast<UWidget*>(TrailBar), static_cast<UWidget*>(HealthBar), static_cast<UWidget*>(PostureBar), static_cast<UWidget*>(NameText) })
	{
		Part->SetVisibility(BarVisibility);
	}
	SubtitleText->SetVisibility(Current.bShowBar && !Current.Subtitle.IsEmpty() ? ESlateVisibility::HitTestInvisible : ESlateVisibility::Collapsed);
	PromptText->SetVisibility(Current.bPrompt ? ESlateVisibility::HitTestInvisible : ESlateVisibility::Collapsed);
	BannerTextBlock->SetVisibility(Alpha > 0.01f ? ESlateVisibility::HitTestInvisible : ESlateVisibility::Collapsed);

	NameText->SetText(Current.Name);
	SubtitleText->SetText(Current.Subtitle);
	PromptText->SetText(Current.Prompt);
	BannerTextBlock->SetText(Banner);
	BannerTextBlock->SetColorAndOpacity(FSlateColor(BannerColor));
	BannerTextBlock->SetRenderOpacity(Alpha);

	// The trail follows the health down slowly (damage reads as a drain) and snaps up when health comes back (a reset).
	if (Current.Health >= Trail)
	{
		Trail = Current.Health;
	}
	else
	{
		Trail = FMath::Max(Current.Health, Trail - InDeltaTime * 0.35f);
	}
	HealthBar->SetPercent(Current.Health);
	TrailBar->SetPercent(Trail);
	PostureBar->SetPercent(Current.Posture);
	// Posture flashes white on a break, otherwise it turns from gold to red as it runs low.
	const FLinearColor Low(0.8f, 0.2f, 0.12f);
	const FLinearColor Full(0.82f, 0.68f, 0.3f);
	PostureBar->SetFillColorAndOpacity(Current.bPostureFlash ? FLinearColor(1.f, 1.f, 1.f) : FMath::Lerp(Low, Full, FMath::Clamp(Current.Posture, 0.f, 1.f)));
}

bool URPGBossHudWidget::IsBarShown() const
{
	return Current.bShowBar;
}

bool URPGBossHudWidget::IsPromptShown() const
{
	return Current.bPrompt;
}

float URPGBossHudWidget::GetBarPercent() const
{
	return HealthBar ? HealthBar->GetPercent() : -1.f;
}

FText URPGBossHudWidget::GetBannerText() const
{
	return BannerAlpha() > 0.01f ? Banner : FText::GetEmpty();
}

// ---------------------------------------------------------------------------------------------------------------------------------- component

URPGBossHud::URPGBossHud()
{
	PrimaryComponentTick.bCanEverTick = true;
}

FString URPGBossHud::GetStateName() const
{
	switch (State)
	{
	case EState::Fighting: return TEXT("Fighting");
	case EState::Victory: return TEXT("Victory");
	default: return TEXT("Dormant");
	}
}

void URPGBossHud::FindParts()
{
	AActor* Boss = GetOwner();
	if (!Boss)
	{
		return;
	}
	// The subsystem adds the other components after this one: look until they exist.
	if (!Encounter) { Encounter = Boss->FindComponentByClass<URPGBossEncounter>(); }
	if (!Phases) { Phases = Boss->FindComponentByClass<URPGBossPhases>(); }
	if (!Posture) { Posture = Boss->FindComponentByClass<URPGBossPosture>(); }
	if (!Stagger) { Stagger = Boss->FindComponentByClass<URPGBossStagger>(); }
}

void URPGBossHud::EnsureWidget()
{
	if (Widget)
	{
		return;
	}
	APlayerController* Controller = GetWorld() ? GetWorld()->GetFirstPlayerController() : nullptr;
	if (!Controller || !Controller->IsLocalController())
	{
		return;
	}
	Widget = CreateWidget<URPGBossHudWidget>(Controller, URPGBossHudWidget::StaticClass());
	if (Widget)
	{
		Widget->AddToViewport(20);
	}
}

void URPGBossHud::HidePackBar()
{
	// The pack's boss creates its own bar (the Blueprint variable "Boss HUD", class BP_BossHUD) with the pack's name for it. Ours replaces it, so collapse it by reflection.
	AActor* Boss = GetOwner();
	if (!Boss)
	{
		return;
	}
	for (TFieldIterator<FObjectProperty> It(Boss->GetClass()); It; ++It)
	{
		if (!It->PropertyClass || !It->PropertyClass->IsChildOf(UUserWidget::StaticClass()) || !It->GetName().Contains(TEXT("HUD")))
		{
			continue;
		}
		if (UUserWidget* PackBar = Cast<UUserWidget>(It->GetObjectPropertyValue_InContainer(Boss)))
		{
			if (PackBar->GetVisibility() != ESlateVisibility::Collapsed)
			{
				PackBar->SetVisibility(ESlateVisibility::Collapsed);
				UE_LOG(LogRPGBossHud, Log, TEXT("collapsed the pack's boss bar (%s)"), *It->GetName());
			}
		}
	}
}

void URPGBossHud::EndPlay(const EEndPlayReason::Type EndPlayReason)
{
	if (Widget)
	{
		// The pack destroys the boss a few seconds after its death: the victory banner must outlive it, so a dead boss hands the widget over to finish its fade.
		if (State == EState::Victory && EndPlayReason == EEndPlayReason::Destroyed)
		{
			Widget->Detach();
		}
		else
		{
			Widget->RemoveFromParent();
		}
		Widget = nullptr;
	}
	Super::EndPlay(EndPlayReason);
}

void URPGBossHud::TickComponent(float DeltaTime, ELevelTick TickType, FActorComponentTickFunction* ThisTickFunction)
{
	Super::TickComponent(DeltaTime, TickType, ThisTickFunction);
	const UWorld* World = GetWorld();
	AActor* Boss = GetOwner();
	FindParts();
	if (!World || !Boss || !Encounter)
	{
		return;
	}
	EnsureWidget();
	const double Now = World->GetRealTimeSeconds();
	if (bHidePackBar && Now >= NextPackBarCheck)
	{
		NextPackBarCheck = Now + 0.2;
		HidePackBar();
	}

	// A reset (generation change) clears everything that belongs to the old fight: banner, bar, victory latch.
	const int32 Generation = Encounter->GetGeneration();
	if (Generation != LastGeneration)
	{
		LastGeneration = Generation;
		bSeenAlive = false;
		bWasStaggered = false;
		FlashEnd = 0.0;
		if (Widget)
		{
			Widget->ClearBanner();
			Widget->DisableRetry();
		}
		if (bPlayerLocked)
		{
			APlayerController* LockController = World->GetFirstPlayerController();
			if (APawn* LockPawn = LockController ? LockController->GetPawn() : nullptr)
			{
				LockPawn->EnableInput(LockController);
			}
			bPlayerLocked = false;
		}
		State = EState::Dormant;
	}

	double Health = 0.0;
	double MaxHealth = 1.0;
	const bool bHaveHealth = RPGPack::ReadAttribute(Boss, TEXT("Attribute.Health"), /*bMax=*/false, Health) && RPGPack::ReadAttribute(Boss, TEXT("Attribute.Health"), /*bMax=*/true, MaxHealth) && MaxHealth > 0.0;
	if (bHaveHealth && Health > 0.0)
	{
		bSeenAlive = true;
	}
	const bool bDead = bHaveHealth && Health <= 0.0 && bSeenAlive;

	if (bDead)
	{
		if (State != EState::Victory)
		{
			State = EState::Victory;
			if (Widget)
			{
				Widget->SetBanner(FText::Format(NSLOCTEXT("RPG", "BossFalls", "{0}  FALLS"), BossName.ToUpper()), FLinearColor(0.92f, 0.76f, 0.3f), VictoryBannerSeconds);
			}
			if (VictoryFiredGeneration != Generation)
			{
				VictoryFiredGeneration = Generation;
				++VictoryCount;
				UE_LOG(LogRPGBossHud, Log, TEXT("victory (generation %d, count %d)"), Generation, VictoryCount);
				if (bLockPlayerOnVictory)
				{
					// Freeze 18.2 and L11: no combat action may run after the boss has fallen. The pawn's whole input is switched off; the controller stays alive for the retry keys.
					APlayerController* LockController = World->GetFirstPlayerController();
					if (APawn* LockPawn = LockController ? LockController->GetPawn() : nullptr)
					{
						LockPawn->DisableInput(LockController);
						bPlayerLocked = true;
					}
				}
				if (Widget)
				{
					Widget->EnableRetry(RetryText, RetryDelaySeconds);
				}
				OnVictory.Broadcast(Generation);
			}
		}
	}
	else if (Encounter->IsDormant())
	{
		State = EState::Dormant;
	}
	else if (State == EState::Dormant)
	{
		State = EState::Fighting;
		if (Widget)
		{
			Widget->SetBanner(BossName.ToUpper(), FLinearColor(0.93f, 0.88f, 0.75f), NameBannerSeconds);
		}
	}

	FRPGBossHudState Hud;
	Hud.bShowBar = State == EState::Fighting;
	Hud.Health = bHaveHealth ? FMath::Clamp(static_cast<float>(Health / MaxHealth), 0.f, 1.f) : 1.f;
	Hud.Name = BossName;
	Hud.Prompt = PromptText;
	Hud.Subtitle = Phases && Phases->IsPhaseTwo() ? PhaseTwoSubtitle : FText::GetEmpty();
	if (Posture && Posture->GetPosture() >= 0.f)
	{
		Hud.Posture = FMath::Clamp(Posture->GetPosture() / FMath::Max(1.f, Posture->GetMaxPosture()), 0.f, 1.f);
	}
	const bool bStaggered = Stagger && Stagger->IsStaggered();
	if (bStaggered && !bWasStaggered)
	{
		FlashEnd = Now + 0.7;
	}
	bWasStaggered = bStaggered;
	Hud.bPostureFlash = Now < FlashEnd;
	const APlayerController* Controller = World->GetFirstPlayerController();
	Hud.bPrompt = State == EState::Fighting && Stagger && Stagger->IsCriticalWindowOpen() && Controller && Stagger->IsRiposteAvailable(Controller->GetPawn());

	Last = Hud;
	if (Widget)
	{
		Widget->Apply(Hud);
	}
}
