// Copyright One Boss Fight. All Rights Reserved.

#include "Player/RPGBossShockwave.h"
#include "Components/CapsuleComponent.h"
#include "DrawDebugHelpers.h"
#include "Engine/World.h"
#include "GameFramework/Character.h"
#include "GameplayTagContainer.h"
#include "Kismet/GameplayStatics.h"
#include "Pack/RPGBlueprintCall.h"
#include "Player/RPGAttackTracker.h"
#include "Player/RPGBossEncounter.h"

DEFINE_LOG_CATEGORY_STATIC(LogRPGWave, Log, All);

using namespace RPGPack;

URPGBossShockwave::URPGBossShockwave()
{
	PrimaryComponentTick.bCanEverTick = true;
}

void URPGBossShockwave::LaunchForTest()
{
	Launch();
}

void URPGBossShockwave::Launch()
{
	const ACharacter* Boss = Cast<ACharacter>(GetOwner());
	if (!Boss)
	{
		return;
	}
	Origin = Boss->GetActorLocation();
	GroundZ = Origin.Z - (Boss->GetCapsuleComponent() ? Boss->GetCapsuleComponent()->GetScaledCapsuleHalfHeight() : 0.f);
	Radius = StartRadius;
	bActive = true;
	bResolved = false;
	bClearedBand = false;
	++LaunchCount;
	const URPGBossEncounter* Encounter = GetOwner()->FindComponentByClass<URPGBossEncounter>();
	LaunchGeneration = Encounter ? Encounter->GetGeneration() : 0;
	HealthAtLaunch = -1.0;
	if (const APawn* Player = UGameplayStatics::GetPlayerPawn(this, 0))
	{
		ReadAttribute(Player, TEXT("Attribute.Health"), false, HealthAtLaunch);
	}
	UE_LOG(LogRPGWave, Log, TEXT("%s: wave %d launched from (%.0f, %.0f), floor z %.0f, player health %.0f"), *GetOwner()->GetName(), LaunchCount, Origin.X, Origin.Y, GroundZ, HealthAtLaunch);
}

void URPGBossShockwave::Stop(const TCHAR* Reason)
{
	if (bActive)
	{
		UE_LOG(LogRPGWave, Log, TEXT("%s: wave ended (%s) at radius %.0f"), *GetOwner()->GetName(), Reason, Radius);
	}
	bActive = false;
}

void URPGBossShockwave::Resolve()
{
	const ACharacter* Player = Cast<ACharacter>(UGameplayStatics::GetPlayerPawn(this, 0));
	if (!Player || bResolved)
	{
		return;
	}
	const FVector ToPlayer = (Player->GetActorLocation() - Origin) * FVector(1.f, 1.f, 0.f);
	const float Distance = ToPlayer.Size();
	const float Inner = Radius - Thickness * 0.5f;
	const float Outer = Radius + Thickness * 0.5f;
	if (Distance > Outer)
	{
		return; // not reached yet
	}
	if (Distance < Inner)
	{
		// The band has passed over this spot. A player that was clear of the floor the whole time it crossed has jumped it; a player that started inside the landing zone is the central hit's business.
		if (bClearedBand)
		{
			++JumpedCount;
			UE_LOG(LogRPGWave, Log, TEXT("wave passed under the player (the player was clear of the floor while it crossed)"));
		}
		bResolved = true;
		return;
	}
	const float FeetZ = Player->GetActorLocation().Z - (Player->GetCapsuleComponent() ? Player->GetCapsuleComponent()->GetScaledCapsuleHalfHeight() : 0.f);
	if (FeetZ - GroundZ >= JumpClearance)
	{
		bClearedBand = true; // inside the band but high enough: decided when the band has passed
		return;
	}
	bResolved = true;
	double Health = 0.0;
	ReadAttribute(Player, TEXT("Attribute.Health"), false, Health);
	bool bInvulnerable = false;
	CallBlueprintFunction(const_cast<ACharacter*>(Player), TEXT("HasMatchingGameplayTag"),
		[](UFunction& F, uint8* P) { SetTag(F, P, TEXT("TagToCheck"), FGameplayTag::RequestGameplayTag(TEXT("Status.Invulnerable"), false)); },
		[&bInvulnerable](UFunction& F, uint8* P)
		{
			if (const FBoolProperty* Result = CastField<FBoolProperty>(F.FindPropertyByName(TEXT("ReturnValue"))))
			{
				bInvulnerable = Result->GetPropertyValue_InContainer(P);
			}
		});
	if (bInvulnerable)
	{
		++InvulnerableCount;
		UE_LOG(LogRPGWave, Log, TEXT("wave ignored: player invulnerable (dodge i-frames)"));
	}
	else if (HealthAtLaunch >= 0.0 && Health < HealthAtLaunch)
	{
		++CentralPriorityCount;
		UE_LOG(LogRPGWave, Log, TEXT("wave ignored: the move already hurt the player (health %.0f -> %.0f), the central hit has priority"), HealthAtLaunch, Health);
	}
	else
	{
		++HitCount;
		WriteAttribute(Player, TEXT("Attribute.Health"), FMath::Max(0.0, Health - Damage));
		UE_LOG(LogRPGWave, Log, TEXT("wave hit the player at %.0f cm (feet %.0f cm above the floor): health %.0f -> %.0f"), Distance, FeetZ - GroundZ, Health, FMath::Max(0.0, Health - Damage));
	}
}

void URPGBossShockwave::TickComponent(float DeltaTime, ELevelTick TickType, FActorComponentTickFunction* ThisTickFunction)
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
	const URPGBossEncounter* Encounter = Boss->FindComponentByClass<URPGBossEncounter>();
	if (bActive && (bDead || (Encounter && Encounter->GetGeneration() != LaunchGeneration)))
	{
		Stop(bDead ? TEXT("boss dead") : TEXT("encounter reset"));
	}
	const URPGAttackTracker* Tracker = Boss->FindComponentByClass<URPGAttackTracker>();
	if (!bActive && !bDead && Tracker && Tracker->GetCurrentMove() == MoveId && Tracker->IsActiveWindow() && Tracker->GetAttackInstance() != LastInstance)
	{
		LastInstance = Tracker->GetAttackInstance();
		Launch();
	}
	if (!bActive)
	{
		return;
	}
	Radius += Speed * DeltaTime;
	Resolve();
#if !UE_BUILD_SHIPPING
	DrawDebugCircle(GetWorld(), FVector(Origin.X, Origin.Y, GroundZ + 8.f), Radius, 64, FColor(255, 140, 40), false, -1.f, 0, 8.f, FVector(1, 0, 0), FVector(0, 1, 0), false);
#endif
	if (Radius > MaxRadius)
	{
		Stop(TEXT("max radius"));
	}
}
