// Copyright One Boss Fight. All Rights Reserved.

#include "Characters/RPGTrainingDummy.h"
#include "OneBossFight.h"
#include "Combat/RPGAttributeComponent.h"
#include "Combat/RPGCombatComponent.h"
#include "DrawDebugHelpers.h"
#include "Engine/World.h"
#include "TimerManager.h"

ARPGTrainingDummy::ARPGTrainingDummy()
{
	GetCombat()->TeamId = 1;
}

void ARPGTrainingDummy::BeginPlay()
{
	Super::BeginPlay();
	GetCombat()->OnHitReceived.AddUniqueDynamic(this, &ARPGTrainingDummy::HandleHitReceived);
}

void ARPGTrainingDummy::HandleHitReceived(const FRPGHitInfo& Hit, const FRPGHitResult& Result)
{
	const URPGAttributeComponent* Attr = GetAttributes();
	const TCHAR* Outcome = Result.bIgnoredInvulnerable ? TEXT("dodged")
		: Result.bBlocked ? TEXT("blocked")
		: Result.bKilled ? TEXT("killed")
		: Result.bPoiseBroken ? TEXT("poise break")
		: TEXT("hit");

	UE_LOG(LogOneBossFight, Log, TEXT("%s %s: %.0f damage, health %.0f/%.0f, poise %.0f"),
		*GetName(), Outcome, Result.DamageApplied, Attr->GetHealth(), Attr->MaxHealth, Attr->GetPoise());

#if ENABLE_DRAW_DEBUG
	const FString Text = FString::Printf(TEXT("-%.0f  %.0f/%.0f  %s"), Result.DamageApplied, Attr->GetHealth(), Attr->MaxHealth, Outcome);
	DrawDebugString(GetWorld(), FVector(0.f, 0.f, 120.f), Text, this, FColor::White, 1.5f, false, 1.2f);
#endif
}

void ARPGTrainingDummy::HandleDeath()
{
	Super::HandleDeath();
	if (ResetDelay > 0.f)
	{
		GetWorldTimerManager().SetTimer(ResetTimer, this, &ARPGTrainingDummy::ResetCombatant, ResetDelay, false);
	}
}
