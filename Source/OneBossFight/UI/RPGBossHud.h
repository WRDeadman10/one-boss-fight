// Copyright One Boss Fight. All Rights Reserved.

#pragma once

#include "CoreMinimal.h"
#include "Blueprint/UserWidget.h"
#include "Components/ActorComponent.h"
#include "RPGBossHud.generated.h"

class UBorder;
class UCanvasPanel;
class UCanvasPanelSlot;
class UProgressBar;
class UTextBlock;
class URPGBossEncounter;
class URPGBossPhases;
class URPGBossPosture;
class URPGBossStagger;

/** What the boss HUD shows this frame. The component fills it, the widget draws it and owns no game state. */
struct FRPGBossHudState
{
	bool bShowBar = false;
	float Health = 1.f;
	float Posture = 1.f;
	bool bPostureFlash = false;
	bool bPrompt = false;
	FText Name;
	FText Subtitle;
	FText Prompt;
	/** The player's build line (M13: "Build: Strength (Claymore)"), shown top centre while a build is chosen, also while the boss sleeps. */
	FText BuildLine;
	bool bShowBuild = false;
};

/** Boss health bar with name plate and phase subtitle, thin posture bar with a flash on a break, riposte prompt and a centre banner. The tree is built in C++ (no Widget Blueprint to keep in sync). */
UCLASS()
class ONEBOSSFIGHT_API URPGBossHudWidget : public UUserWidget
{
	GENERATED_BODY()

public:
	void Apply(const FRPGBossHudState& State);

	/** Shows a centre banner: fades in 0.6 s, holds HoldSeconds, fades out 1.0 s (real time, so slow motion does not stretch it). The widget runs the fade itself. */
	void SetBanner(const FText& Text, const FLinearColor& Color, float HoldSeconds);
	void ClearBanner();

	/** The boss is gone (destroyed after its death): drop the bar and prompt, let a running banner finish, then remove the widget from the screen. */
	void Detach();

	/** Victory retry (Freeze L11: victory exposes retry/reset): after DelaySeconds a line appears and R (or the gamepad Y button) reloads the level. Survives Detach. */
	void EnableRetry(const FText& Text, float DelaySeconds);
	void DisableRetry();

	UFUNCTION(BlueprintPure, Category = "Hud")
	bool IsRetryShown() const;

	/** Tests: what the widget currently shows. */
	UFUNCTION(BlueprintPure, Category = "Hud")
	bool IsBarShown() const;

	UFUNCTION(BlueprintPure, Category = "Hud")
	bool IsPromptShown() const;

	UFUNCTION(BlueprintPure, Category = "Hud")
	float GetBarPercent() const;

	UFUNCTION(BlueprintPure, Category = "Hud")
	FText GetBannerText() const;

	/** Tests: the build line is on screen, and its text. */
	UFUNCTION(BlueprintPure, Category = "Hud")
	bool IsBuildLineShown() const;

	UFUNCTION(BlueprintPure, Category = "Hud")
	FText GetBuildLineText() const;

protected:
	virtual TSharedRef<SWidget> RebuildWidget() override;
	virtual void NativeTick(const FGeometry& MyGeometry, float InDeltaTime) override;

private:
	UTextBlock* AddText(UCanvasPanel* Canvas, const TCHAR* WidgetName, const FVector2D& Anchor, const FVector2D& Alignment, const FVector2D& Position, int32 FontSize, const FLinearColor& Color);
	UProgressBar* AddBar(UCanvasPanel* Canvas, const TCHAR* WidgetName, const FVector2D& Position, const FVector2D& Size, const FLinearColor& Fill, float BackgroundAlpha);

	UPROPERTY(Transient)
	TObjectPtr<UBorder> Plate;
	UPROPERTY(Transient)
	TObjectPtr<UProgressBar> TrailBar;
	UPROPERTY(Transient)
	TObjectPtr<UProgressBar> HealthBar;
	UPROPERTY(Transient)
	TObjectPtr<UProgressBar> PostureBar;
	UPROPERTY(Transient)
	TObjectPtr<UTextBlock> NameText;
	UPROPERTY(Transient)
	TObjectPtr<UTextBlock> SubtitleText;
	UPROPERTY(Transient)
	TObjectPtr<UTextBlock> PromptText;
	UPROPERTY(Transient)
	TObjectPtr<UTextBlock> BannerTextBlock;
	UPROPERTY(Transient)
	TObjectPtr<UTextBlock> RetryTextBlock;
	UPROPERTY(Transient)
	TObjectPtr<UTextBlock> BuildTextBlock;

	float BannerAlpha() const;

	FRPGBossHudState Current;
	FText Banner;
	FLinearColor BannerColor = FLinearColor::White;
	double BannerStart = -1.0;
	float BannerHold = 0.f;
	float Trail = 1.f;
	bool bBuilt = false;
	bool bDetached = false;
	bool bRetryEnabled = false;
	double RetryShowAt = 0.0;
	FText RetryText;
};

DECLARE_DYNAMIC_MULTICAST_DELEGATE_OneParam(FRPGVictoryDelegate, int32, Generation);

/**
 * Encounter presentation owner for the pack's boss (Freeze 18.2, 18.3 and 32): decides the encounter state from the boss itself and drives the HUD.
 *   Dormant   the boss sleeps (or the encounter was reset): no bar;
 *   Fighting  name banner on waking, bar, posture bar, phase subtitle, riposte prompt while a riposte would be accepted;
 *   Victory   the boss has died after being seen alive: "<name> falls" banner and OnVictory, broadcast exactly once per encounter generation.
 * A reset (generation change) clears the banner, the bar and the victory latch, so the next fight can end in a new victory. Attached by RPGPlayerMovesSubsystem; nothing in the pack is edited.
 */
UCLASS(ClassGroup = (Boss))
class ONEBOSSFIGHT_API URPGBossHud : public UActorComponent
{
	GENERATED_BODY()

public:
	URPGBossHud();

	/** Provisional name (the boss is a placeholder until the concept is chosen). */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Hud")
	FText BossName = NSLOCTEXT("RPG", "BossName", "Ember Warden");

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Hud")
	FText PhaseTwoSubtitle = NSLOCTEXT("RPG", "PhaseTwoSubtitle", "Embers Unbound");

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Hud")
	FText PromptText = NSLOCTEXT("RPG", "RipostePrompt", "LIGHT ATTACK  -  RIPOSTE");

	/** Seconds the name banner holds after it faded in (it fades in 0.6 s and out 1.0 s). */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Hud", meta = (ClampMin = "0.0"))
	float NameBannerSeconds = 2.2f;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Hud", meta = (ClampMin = "0.0"))
	float VictoryBannerSeconds = 4.f;

	/** Victory (Freeze 18.2, L11): the player's input is disabled (no combat action can run) and a retry line appears after this many seconds. */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Hud")
	bool bLockPlayerOnVictory = true;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Hud", meta = (ClampMin = "0.0"))
	float RetryDelaySeconds = 3.f;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Hud")
	FText RetryText = NSLOCTEXT("RPG", "RetryText", "PRESS  R  OR  Y  TO FACE IT AGAIN");

	UFUNCTION(BlueprintPure, Category = "Encounter")
	bool IsPlayerLocked() const { return bPlayerLocked; }

	/** Collapse the pack's own boss bar (its Blueprint variable "Boss HUD") so only this HUD shows. */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Hud")
	bool bHidePackBar = true;

	/** Broadcast once when the boss dies (per encounter generation). Music, the arena and the retry prompt can listen. */
	UPROPERTY(BlueprintAssignable, Category = "Encounter")
	FRPGVictoryDelegate OnVictory;

	UFUNCTION(BlueprintPure, Category = "Encounter")
	int32 GetVictoryCount() const { return VictoryCount; }

	/** "Dormant", "Fighting" or "Victory". */
	UFUNCTION(BlueprintPure, Category = "Encounter")
	FString GetStateName() const;

	UFUNCTION(BlueprintPure, Category = "Hud")
	URPGBossHudWidget* GetWidget() const { return Widget; }

	UFUNCTION(BlueprintPure, Category = "Hud")
	bool IsPromptShown() const { return Last.bPrompt; }

	UFUNCTION(BlueprintPure, Category = "Hud")
	bool IsPostureFlashing() const { return Last.bPostureFlash; }

protected:
	virtual void TickComponent(float DeltaTime, ELevelTick TickType, FActorComponentTickFunction* ThisTickFunction) override;
	virtual void EndPlay(const EEndPlayReason::Type EndPlayReason) override;

private:
	enum class EState : uint8 { Dormant, Fighting, Victory };

	void FindParts();
	void EnsureWidget();
	void HidePackBar();

	UPROPERTY(Transient)
	TObjectPtr<URPGBossHudWidget> Widget;
	UPROPERTY(Transient)
	TObjectPtr<URPGBossEncounter> Encounter;
	UPROPERTY(Transient)
	TObjectPtr<URPGBossPhases> Phases;
	UPROPERTY(Transient)
	TObjectPtr<URPGBossPosture> Posture;
	UPROPERTY(Transient)
	TObjectPtr<URPGBossStagger> Stagger;

	FRPGBossHudState Last;
	EState State = EState::Dormant;
	int32 LastGeneration = -1;
	int32 VictoryFiredGeneration = -1;
	int32 VictoryCount = 0;
	bool bSeenAlive = false;
	bool bWasStaggered = false;
	bool bPlayerLocked = false;
	double FlashEnd = 0.0;
	double NextPackBarCheck = 0.0;
};
