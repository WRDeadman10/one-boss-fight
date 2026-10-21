// Copyright One Boss Fight. All Rights Reserved.

#include "Player/RPGBossHealPunish.h"
#include "Animation/AnimInstance.h"
#include "Animation/AnimMontage.h"
#include "Components/SkeletalMeshComponent.h"
#include "Engine/World.h"
#include "GameFramework/Character.h"
#include "Kismet/GameplayStatics.h"
#include "Pack/RPGBlueprintCall.h"
#include "Player/RPGAttackTracker.h"
#include "Player/RPGBossDamage.h"
#include "Player/RPGBossEncounter.h"

DEFINE_LOG_CATEGORY_STATIC(LogRPGHealPunish, Log, All);

using namespace RPGPack;

namespace
{
	// The tracker move of the throw and how long the boss waits for its clip to start before the request is dropped (a vetoed or replaced start).
	const FName ThrowMove(TEXT("A5"));
	constexpr float StartGraceSeconds = 0.5f;
}

URPGBossHealPunish::URPGBossHealPunish()
{
	PrimaryComponentTick.bCanEverTick = true;
}

float URPGBossHealPunish::GetCooldownRemaining() const
{
	return GetWorld() ? static_cast<float>(FMath::Max(0.0, CooldownEnd - GetWorld()->GetTimeSeconds())) : 0.f;
}

FVector URPGBossHealPunish::GetSpawnLocation() const
{
	const ACharacter* Boss = Cast<ACharacter>(GetOwner());
	const USkeletalMeshComponent* Mesh = Boss ? Boss->GetMesh() : nullptr;
	if (Mesh)
	{
		for (const FName& Socket : SpawnSockets)
		{
			if (Mesh->DoesSocketExist(Socket))
			{
				return Mesh->GetSocketLocation(Socket);
			}
		}
	}
	return Boss ? Boss->GetActorLocation() + Boss->GetActorForwardVector() * 100.f + FVector(0.f, 0.f, 120.f) : FVector::ZeroVector;
}

bool URPGBossHealPunish::HasLineOfSight(const AActor* Boss, const AActor* Player, const FVector& From) const
{
	FCollisionQueryParams Params(SCENE_QUERY_STAT(RPGHealPunishLos), false);
	Params.AddIgnoredActor(Boss);
	Params.AddIgnoredActor(Player);
	FHitResult Hit;
	return !GetWorld()->LineTraceSingleByObjectType(Hit, From, Player->GetActorLocation(), RPGBossDamage::WorldBlockers(), Params);
}

void URPGBossHealPunish::ClearPending(const TCHAR* Reason)
{
	if (bPending)
	{
		++Cancelled;
		UE_LOG(LogRPGHealPunish, Log, TEXT("%s: pending punish cleared (%s)"), *GetOwner()->GetName(), Reason);
	}
	bPending = false;
}

void URPGBossHealPunish::CancelAll(const TCHAR* Reason)
{
	ClearPending(Reason);
	bStarted = false;
	int32 Ended = 0;
	for (const TWeakObjectPtr<ARPGBossJavelin>& Javelin : Flying)
	{
		if (ARPGBossJavelin* Live = Javelin.Get())
		{
			if (bCancelJavelinsOnInterrupt)
			{
				Live->Cancel(Reason);
				++Ended;
			}
		}
	}
	Flying.Reset();
	if (Ended > 0)
	{
		UE_LOG(LogRPGHealPunish, Log, TEXT("%s: %d javelin(s) in flight cancelled (%s)"), *GetOwner()->GetName(), Ended, Reason);
	}
}

void URPGBossHealPunish::OnHealStarted()
{
	++HealEvents;
	const ACharacter* Boss = Cast<ACharacter>(GetOwner());
	const ACharacter* Player = Cast<ACharacter>(UGameplayStatics::GetPlayerPawn(this, 0));
	URPGAttackTracker* Tracker = Boss ? Boss->FindComponentByClass<URPGAttackTracker>() : nullptr;
	if (!bEnabled || !bRespondToHeal || !Boss || !Player || !Tracker)
	{
		return;
	}
	// The order of the checks is the order the Freeze lists them (16 A5): one punish at a time, the boss in a state that may start a move, then range, sight and cooldown.
	if (bPending)
	{
		++DiscardedPending;
		UE_LOG(LogRPGHealPunish, Log, TEXT("%s: heal %d ignored: a punish is already pending"), *Boss->GetName(), HealEvents);
		return;
	}
	if (!Tracker->IsNeutral() || !RPGBossDamage::IsAlive(Boss) || !RPGBossDamage::IsAlive(Player))
	{
		// A committed attack, a stance break, a phase transition, sleep or death: the special response is dropped and the state resolves normally. Nothing is interrupted.
		++DiscardedBusy;
		UE_LOG(LogRPGHealPunish, Log, TEXT("%s: heal %d ignored: the boss is not in a state that may start a move (%s)"), *Boss->GetName(), HealEvents, *Tracker->GetPhaseName());
		return;
	}
	const float Distance = FVector::Dist2D(Boss->GetActorLocation(), Player->GetActorLocation());
	if (Distance < MinRange || Distance > MaxRange)
	{
		++DiscardedRange;
		UE_LOG(LogRPGHealPunish, Log, TEXT("%s: heal %d ignored: player at %.0f cm, window %.0f to %.0f"), *Boss->GetName(), HealEvents, Distance, MinRange, MaxRange);
		return;
	}
	if (!HasLineOfSight(Boss, Player, GetSpawnLocation()))
	{
		++DiscardedSight;
		UE_LOG(LogRPGHealPunish, Log, TEXT("%s: heal %d ignored: no line of sight"), *Boss->GetName(), HealEvents);
		return;
	}
	if (GetCooldownRemaining() > 0.f)
	{
		++DiscardedCooldown;
		UE_LOG(LogRPGHealPunish, Log, TEXT("%s: heal %d ignored: cooldown %.1f s left"), *Boss->GetName(), HealEvents, GetCooldownRemaining());
		return;
	}
	if (!Tracker->StartMove(ThrowMove, false))
	{
		++DiscardedBusy;
		UE_LOG(LogRPGHealPunish, Log, TEXT("%s: heal %d ignored: the throw could not start"), *Boss->GetName(), HealEvents);
		return;
	}
	bPending = true;
	bStarted = false;
	PendingSince = GetWorld()->GetTimeSeconds();
	++Accepted;
	UE_LOG(LogRPGHealPunish, Log, TEXT("%s: heal %d accepted at %.0f cm: the boss telegraphs the throw"), *Boss->GetName(), HealEvents, Distance);
}

void URPGBossHealPunish::Release()
{
	const ACharacter* Boss = Cast<ACharacter>(GetOwner());
	const ACharacter* Player = Cast<ACharacter>(UGameplayStatics::GetPlayerPawn(this, 0));
	bPending = false;
	if (!Boss || !Player || !RPGBossDamage::IsAlive(Player))
	{
		++Cancelled;
		UE_LOG(LogRPGHealPunish, Log, TEXT("punish cancelled at the release: no valid target"));
		return;
	}
	const FVector From = GetSpawnLocation();
	if (!HasLineOfSight(Boss, Player, From))
	{
		++Cancelled;
		UE_LOG(LogRPGHealPunish, Log, TEXT("punish cancelled at the release: line of sight is blocked"));
		return;
	}
	// The cooldown starts here, at the release, and only here (repeated heal events never touch it).
	CooldownEnd = GetWorld()->GetTimeSeconds() + Cooldown;
	++Released;
	Flying.RemoveAll([](const TWeakObjectPtr<ARPGBossJavelin>& Old) { return !Old.IsValid(); });
	const FVector Target(Player->GetActorLocation().X, Player->GetActorLocation().Y, RPGBossDamage::FeetZ(Player) + AimHeight);
	const FVector Direction = (Target - From).GetSafeNormal();
	const URPGBossEncounter* Encounter = Boss->FindComponentByClass<URPGBossEncounter>();
	const float Speed = FMath::Clamp(FVector::Dist(From, Target) / FlightTime, MinSpeed, MaxSpeed);
	FActorSpawnParameters Parameters;
	Parameters.SpawnCollisionHandlingOverride = ESpawnActorCollisionHandlingMethod::AlwaysSpawn;
	if (ARPGBossJavelin* Javelin = GetWorld()->SpawnActor<ARPGBossJavelin>(ARPGBossJavelin::StaticClass(), From, Direction.Rotation(), Parameters))
	{
		Javelin->Launch(this, Direction, Speed, JavelinRadius, Damage, JavelinMaxRange, Encounter ? Encounter->GetGeneration() : 0);
		Flying.Add(Javelin);
	}
	UE_LOG(LogRPGHealPunish, Log, TEXT("%s: javelin %d released from (%.0f, %.0f, %.0f) towards the player at %.0f cm, speed %.0f cm/s, cooldown %.1f s"), *Boss->GetName(), Released, From.X, From.Y, From.Z, FVector::Dist(From, Target), Speed, Cooldown);
}

void URPGBossHealPunish::ReportJavelin(ERPGJavelinResult Result)
{
	switch (Result)
	{
	case ERPGJavelinResult::Hit: ++JavelinHits; break;
	case ERPGJavelinResult::Dodged: ++JavelinDodged; break;
	case ERPGJavelinResult::HitWorld: ++JavelinWorld; break;
	default: break;
	}
}

void URPGBossHealPunish::TickComponent(float DeltaTime, ELevelTick TickType, FActorComponentTickFunction* ThisTickFunction)
{
	Super::TickComponent(DeltaTime, TickType, ThisTickFunction);
	AActor* Boss = GetOwner();
	if (!bEnabled || !Boss)
	{
		return;
	}
	DeathCheck += DeltaTime;
	if (DeathCheck >= 0.1f)
	{
		DeathCheck = 0.f;
		double Health = 1.0;
		if (ReadAttribute(Boss, TEXT("Attribute.Health"), false, Health))
		{
			bDead = Health <= 0.0;
		}
	}
	// A new fight (generation change) starts with no pending request and a ready cooldown; the javelins in flight end themselves on the same token.
	const URPGBossEncounter* Encounter = Boss->FindComponentByClass<URPGBossEncounter>();
	const int32 Generation = Encounter ? Encounter->GetGeneration() : 0;
	if (Generation != SeenGeneration)
	{
		SeenGeneration = Generation;
		ClearPending(TEXT("encounter reset"));
		CooldownEnd = -1.0;
	}
	if (bDead)
	{
		ClearPending(TEXT("boss dead"));
		return;
	}

	// Heal start: the edge of the player's DrinkingPotion montage.
	const ACharacter* Player = Cast<ACharacter>(UGameplayStatics::GetPlayerPawn(this, 0));
	UAnimInstance* PlayerAnim = Player && Player->GetMesh() ? Player->GetMesh()->GetAnimInstance() : nullptr;
	if (!DrinkMontage.IsValid())
	{
		DrinkMontage = LoadObject<UAnimMontage>(nullptr, TEXT("/Game/AdvancedARPGCombat/MeleeCombatSystem/Animations/DrinkingPotion_Montage.DrinkingPotion_Montage"));
	}
	const bool bHealing = PlayerAnim && DrinkMontage.IsValid() && PlayerAnim->Montage_IsPlaying(DrinkMontage.Get());
	if (bHealing && !bWasHealing)
	{
		OnHealStarted();
	}
	bWasHealing = bHealing;

	if (!bPending)
	{
		return;
	}
	const URPGAttackTracker* Tracker = Boss->FindComponentByClass<URPGAttackTracker>();
	if (!Tracker)
	{
		return;
	}
	const bool bThrowing = Tracker->GetCurrentMove() == ThrowMove;
	if (bThrowing && Tracker->IsActiveWindow() && Tracker->GetAttackInstance() != LastInstance)
	{
		LastInstance = Tracker->GetAttackInstance();
		Release();
	}
	else if (bThrowing)
	{
		bStarted = true;
	}
	else if (bStarted)
	{
		ClearPending(TEXT("the throw was interrupted before the release"));
	}
	else if (GetWorld()->GetTimeSeconds() - PendingSince > StartGraceSeconds)
	{
		ClearPending(TEXT("the throw never started"));
	}
}
