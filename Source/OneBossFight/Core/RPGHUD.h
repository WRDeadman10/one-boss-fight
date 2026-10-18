// Copyright One Boss Fight. All Rights Reserved.

#pragma once

#include "CoreMinimal.h"
#include "GameFramework/HUD.h"
#include "RPGHUD.generated.h"

/**
 * Minimal canvas HUD: player health and stamina, the boss bar while an encounter runs, and the YOU DIED /
 * ENEMY FELLED banners. Code-drawn so it has no asset dependencies; replaced by UMG in the polish milestone.
 */
UCLASS()
class ONEBOSSFIGHT_API ARPGHUD : public AHUD
{
	GENERATED_BODY()

public:
	virtual void DrawHUD() override;

private:
	void DrawBar(float X, float Y, float Width, float Height, float Fraction, const FLinearColor& Fill);
	void DrawCenteredText(const FString& Text, float Y, float Scale, const FLinearColor& Color);
};
