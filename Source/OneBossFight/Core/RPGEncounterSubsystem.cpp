// Copyright One Boss Fight. All Rights Reserved.

#include "Core/RPGEncounterSubsystem.h"
#include "OneBossFight.h"
#include "Boss/RPGBossAttackData.h"
#include "Boss/RPGBossCombatComponent.h"
#include "Characters/RPGBossCharacter.h"
#include "Characters/RPGPlayerCharacter.h"
#include "Combat/RPGAttributeComponent.h"
#include "Combat/RPGCombatComponent.h"
#include "Combat/RPGMeleeTraceComponent.h"
#include "Combat/RPGTargetLockComponent.h"
#include "Components/CapsuleComponent.h"
#include "Engine/World.h"
#include "GameFramework/Controller.h"

void URPGEncounterSubsystem::RegisterBoss(ARPGBossCharacter* NewBoss)
{
	Boss = NewBoss;
	if (NewBoss)
	{
		NewBoss->GetAttributes()->OnDeath.AddUniqueDynamic(this, &URPGEncounterSubsystem::HandleBossDied);
	}
}

void URPGEncounterSubsystem::RegisterPlayer(ARPGPlayerCharacter* NewPlayer)
{
	Player = NewPlayer;
	if (NewPlayer)
	{
		PlayerStart = NewPlayer->GetActorTransform();
		NewPlayer->GetAttributes()->OnDeath.AddUniqueDynamic(this, &URPGEncounterSubsystem::HandlePlayerDied);
	}
}

void URPGEncounterSubsystem::SetState(ERPGEncounterState NewState)
{
	if (State != NewState)
	{
		State = NewState;
		UE_LOG(LogOneBossFight, Log, TEXT("Encounter state -> %s"), *UEnum::GetValueAsString(NewState));
		OnEncounterStateChanged.Broadcast(NewState);
	}
}

bool URPGEncounterSubsystem::StartEncounter()
{
	ARPGBossCharacter* BossActor = Boss.Get();
	ARPGPlayerCharacter* PlayerActor = Player.Get();
	if (State != ERPGEncounterState::Idle || !BossActor || !PlayerActor || PlayerActor->GetCombat()->IsDead())
	{
		return false;
	}

	if (!BossActor->GetBossCombat()->Engage(PlayerActor))
	{
		return false;
	}
	SetState(ERPGEncounterState::Active);
	return true;
}

void URPGEncounterSubsystem::HandlePlayerDied()
{
	if (State != ERPGEncounterState::Active)
	{
		return;
	}
	SetState(ERPGEncounterState::Defeat);

	if (UWorld* World = GetWorld())
	{
		World->GetTimerManager().SetTimer(RetryTimer, this, &URPGEncounterSubsystem::ResetEncounter, FMath::Max(RetryDelay, 0.01f), false);
	}
}

void URPGEncounterSubsystem::HandleBossDied()
{
	if (State == ERPGEncounterState::Active)
	{
		SetState(ERPGEncounterState::Victory);
	}
}

void URPGEncounterSubsystem::ResetEncounter()
{
	if (UWorld* World = GetWorld())
	{
		World->GetTimerManager().ClearTimer(RetryTimer);
	}

	if (ARPGPlayerCharacter* PlayerActor = Player.Get())
	{
		PlayerActor->ResetCombatant();
		PlayerActor->SetActorTransform(PlayerStart, false, nullptr, ETeleportType::TeleportPhysics);
		if (AController* Controller = PlayerActor->GetController())
		{
			Controller->SetControlRotation(PlayerStart.Rotator());
		}
	}
	if (ARPGBossCharacter* BossActor = Boss.Get())
	{
		BossActor->ResetCombatant();
	}

	++ResetCount;
	SetState(ERPGEncounterState::Idle);
	OnEncounterReset.Broadcast();

	FString Reason;
	if (!VerifyResetInvariants(Reason))
	{
		UE_LOG(LogOneBossFight, Warning, TEXT("Encounter reset left stale state: %s"), *Reason);
	}
}

bool URPGEncounterSubsystem::VerifyResetInvariants(FString& OutReason) const
{
	TArray<FString> Problems;

	if (State != ERPGEncounterState::Idle)
	{
		Problems.Add(TEXT("encounter not idle"));
	}

	if (const ARPGBossCharacter* BossActor = Boss.Get())
	{
		const URPGAttributeComponent* Attr = BossActor->GetAttributes();
		const URPGCombatComponent* Combat = BossActor->GetCombat();
		const URPGBossCombatComponent* Brain = BossActor->GetBossCombat();

		if (Attr->IsDead() || !FMath::IsNearlyEqual(Attr->GetHealth(), Attr->MaxHealth)) { Problems.Add(TEXT("boss health not full")); }
		if (!FMath::IsNearlyEqual(Attr->GetPoise(), Attr->MaxPoise)) { Problems.Add(TEXT("boss poise not full")); }
		if (Brain->GetBossState() != ERPGBossState::Dormant) { Problems.Add(TEXT("boss not dormant")); }
		if (Brain->GetPhase() != 1 || Brain->GetPhaseTransitionCount() != 0) { Problems.Add(TEXT("boss phase not reset")); }
		if (Brain->GetTarget()) { Problems.Add(TEXT("boss still has a target")); }
		if (Brain->GetCurrentAttackIndex() != INDEX_NONE) { Problems.Add(TEXT("boss attack still in progress")); }
		for (int32 Index = 0; Index < Brain->Attacks.Num(); ++Index)
		{
			if (Brain->GetCooldownRemaining(Index) > 0.f) { Problems.Add(TEXT("boss attack cooldown left")); break; }
		}
		if (Combat->GetState() != ERPGCombatState::Locomotion) { Problems.Add(TEXT("boss combat state not locomotion")); }
		if (Combat->IsHitWindowOpen() || BossActor->GetMeleeTrace()->IsSwinging()) { Problems.Add(TEXT("boss hit window open")); }
		if (!Combat->IsInvulnerable()) { Problems.Add(TEXT("dormant boss is hittable")); }
		if (BossActor->GetCapsuleComponent()->GetCollisionEnabled() != ECollisionEnabled::QueryAndPhysics) { Problems.Add(TEXT("boss collision off")); }
	}

	if (const ARPGPlayerCharacter* PlayerActor = Player.Get())
	{
		const URPGAttributeComponent* Attr = PlayerActor->GetAttributes();
		const URPGCombatComponent* Combat = PlayerActor->GetCombat();

		if (Attr->IsDead() || !FMath::IsNearlyEqual(Attr->GetHealth(), Attr->MaxHealth)) { Problems.Add(TEXT("player health not full")); }
		if (!FMath::IsNearlyEqual(Attr->GetStamina(), Attr->MaxStamina)) { Problems.Add(TEXT("player stamina not full")); }
		if (!FMath::IsNearlyEqual(Attr->GetPoise(), Attr->MaxPoise)) { Problems.Add(TEXT("player poise not full")); }
		if (Combat->GetState() != ERPGCombatState::Locomotion) { Problems.Add(TEXT("player combat state not locomotion")); }
		if (Combat->IsHitWindowOpen() || PlayerActor->GetMeleeTrace()->IsSwinging()) { Problems.Add(TEXT("player hit window open")); }
		if (Combat->IsInvulnerable()) { Problems.Add(TEXT("player still invulnerable")); }
		if (Combat->GetBufferedAction() != ERPGBufferedAction::None) { Problems.Add(TEXT("player input still buffered")); }
		if (PlayerActor->GetTargetLock()->IsLocked()) { Problems.Add(TEXT("player still locked on")); }
		if (PlayerActor->IsSprinting()) { Problems.Add(TEXT("player still sprinting")); }
		if (PlayerActor->GetCapsuleComponent()->GetCollisionEnabled() != ECollisionEnabled::QueryAndPhysics) { Problems.Add(TEXT("player collision off")); }
	}

	OutReason = FString::Join(Problems, TEXT("; "));
	return Problems.IsEmpty();
}
