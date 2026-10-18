// Copyright One Boss Fight. All Rights Reserved.

#include "Core/RPGHUD.h"
#include "Characters/RPGBossCharacter.h"
#include "Characters/RPGPlayerCharacter.h"
#include "Combat/RPGAttributeComponent.h"
#include "Combat/RPGCombatComponent.h"
#include "Combat/RPGWeaponData.h"
#include "Core/RPGEncounterSubsystem.h"
#include "Engine/Canvas.h"
#include "Engine/Engine.h"
#include "Engine/World.h"

void ARPGHUD::DrawBar(float X, float Y, float Width, float Height, float Fraction, const FLinearColor& Fill)
{
	Canvas->K2_DrawBox(FVector2D(X - 2.f, Y - 2.f), FVector2D(Width + 4.f, Height + 4.f), 1.f, FLinearColor(0.f, 0.f, 0.f, 0.8f));
	DrawRect(FLinearColor(0.f, 0.f, 0.f, 0.6f), X, Y, Width, Height);
	DrawRect(Fill, X, Y, Width * FMath::Clamp(Fraction, 0.f, 1.f), Height);
}

void ARPGHUD::DrawCenteredText(const FString& Text, float Y, float Scale, const FLinearColor& Color)
{
	float Width = 0.f;
	float Height = 0.f;
	UFont* Font = GEngine->GetLargeFont();
	GetTextSize(Text, Width, Height, Font, Scale);
	DrawText(Text, Color, (Canvas->SizeX - Width) * 0.5f, Y, Font, Scale);
}

void ARPGHUD::DrawHUD()
{
	Super::DrawHUD();
	if (!Canvas)
	{
		return;
	}

	const float Scale = Canvas->SizeY / 1080.f;

	if (const ARPGPlayerCharacter* Player = Cast<ARPGPlayerCharacter>(GetOwningPawn()))
	{
		const URPGAttributeComponent* Attr = Player->GetAttributes();
		const float X = 60.f * Scale;
		const float Y = Canvas->SizeY - 110.f * Scale;
		DrawBar(X, Y, 420.f * Scale, 18.f * Scale, Attr->GetHealthFraction(), FLinearColor(0.75f, 0.1f, 0.1f));
		DrawBar(X, Y + 30.f * Scale, 320.f * Scale, 12.f * Scale, Attr->GetStaminaFraction(), FLinearColor(0.2f, 0.65f, 0.25f));
		if (const URPGWeaponData* Weapon = Player->GetCombat()->Weapon)
		{
			DrawText(Weapon->DisplayName.ToString(), FLinearColor(0.85f, 0.85f, 0.8f), X, Y + 52.f * Scale, GEngine->GetSmallFont(), Scale);
		}
	}

	const URPGEncounterSubsystem* Encounter = GetWorld() ? GetWorld()->GetSubsystem<URPGEncounterSubsystem>() : nullptr;
	if (!Encounter)
	{
		return;
	}

	const ERPGEncounterState State = Encounter->GetState();
	if (const ARPGBossCharacter* Boss = Encounter->GetBoss())
	{
		if (State == ERPGEncounterState::Active || State == ERPGEncounterState::Defeat || State == ERPGEncounterState::Victory)
		{
			const float Width = 900.f * Scale;
			const float X = (Canvas->SizeX - Width) * 0.5f;
			const float Y = Canvas->SizeY - 150.f * Scale;
			DrawText(Boss->BossName.ToString(), FLinearColor(0.9f, 0.85f, 0.7f), X, Y - 34.f * Scale, GEngine->GetMediumFont(), Scale);
			DrawBar(X, Y, Width, 16.f * Scale, Boss->GetAttributes()->GetHealthFraction(), FLinearColor(0.7f, 0.15f, 0.12f));
		}
	}

	if (State == ERPGEncounterState::Defeat)
	{
		DrawCenteredText(TEXT("YOU DIED"), Canvas->SizeY * 0.42f, 3.f * Scale, FLinearColor(0.7f, 0.08f, 0.08f));
	}
	else if (State == ERPGEncounterState::Victory)
	{
		DrawCenteredText(TEXT("ENEMY FELLED"), Canvas->SizeY * 0.42f, 3.f * Scale, FLinearColor(0.9f, 0.75f, 0.3f));
	}
}
