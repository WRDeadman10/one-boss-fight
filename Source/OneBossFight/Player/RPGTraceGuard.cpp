// Copyright One Boss Fight. All Rights Reserved.

#include "Player/RPGTraceGuard.h"
#include "Components/SkeletalMeshComponent.h"
#include "Engine/World.h"
#include "GameFramework/Character.h"
#include "Kismet/GameplayStatics.h"
#include "Pack/RPGBlueprintCall.h"
#include "Player/RPGAttackTracker.h"
#include "Player/RPGBossDamage.h"

DEFINE_LOG_CATEGORY_STATIC(LogRPGTraceGuard, Log, All);

using namespace RPGPack;

URPGTraceGuard::URPGTraceGuard()
{
	PrimaryComponentTick.bCanEverTick = true;
	PrimaryComponentTick.TickGroup = TG_PrePhysics;
}

void URPGTraceGuard::BeginPlay()
{
	Super::BeginPlay();
	// After the boss's animation update and its notify dispatch of this frame, before the pack's trace sample (it ticks in the physics group).
	if (const ACharacter* Character = Cast<ACharacter>(GetOwner()))
	{
		if (USkeletalMeshComponent* Mesh = Character->GetMesh())
		{
			AddTickPrerequisiteComponent(Mesh);
		}
	}
}

void URPGTraceGuard::CloseFor(AActor* Boss, FName Reason)
{
	if (URPGTraceGuard* Guard = Boss ? Boss->FindComponentByClass<URPGTraceGuard>() : nullptr)
	{
		Guard->CloseTraceNow(Reason);
	}
}

bool URPGTraceGuard::IsPackTraceActive() const
{
	return Target.IsValid() && Target.IsActive();
}

FString URPGTraceGuard::GetMissingPackNames() const
{
	FString Missing;
	RPGPackTrace::CheckLiveNames(GetOwner(), Missing);
	return Missing;
}

void URPGTraceGuard::CloseTraceNow(FName Reason)
{
	if (!bEnabled || !bCloseOnInterrupt || !Target.IsValid())
	{
		return;
	}
	// A temporary seed of the wall gate goes with it.
	if (AActor* Seed = TempSeed.Get())
	{
		Target.HitSetRemove(Seed);
	}
	TempSeed.Reset();
	const bool bWasOpen = Target.IsActive();
	Target.Deactivate(TargetTypeTag);
	if (Reason == TEXT("reset"))
	{
		Target.ClearHitSet(); // nothing of the old fight is carried into the next (Freeze 795)
		LastSet.Reset();
	}
	if (bWasOpen)
	{
		++CloseCount;
		UE_LOG(LogRPGTraceGuard, Log, TEXT("%s: pack trace closed at once (%s)"), *GetOwner()->GetName(), *Reason.ToString());
	}
}

void URPGTraceGuard::TickComponent(float DeltaTime, ELevelTick TickType, FActorComponentTickFunction* ThisTickFunction)
{
	Super::TickComponent(DeltaTime, TickType, ThisTickFunction);
	AActor* Boss = GetOwner();
	if (!bEnabled || !Boss || !Target.Resolve(Boss, TargetTypeTag))
	{
		return;
	}
	// The temporary seed of the previous frame lived for exactly one pack sample: take it out before anything is evaluated again.
	if (AActor* Seed = TempSeed.Get())
	{
		if (SeedWindow == WindowId)
		{
			Target.HitSetRemove(Seed);
		}
	}
	TempSeed.Reset();

	const bool bActive = Target.IsActive();
	if (!bActive)
	{
		bWasActive = false;
		return;
	}
	const URPGAttackTracker* Tracker = Boss->FindComponentByClass<URPGAttackTracker>();
	if (!bWasActive)
	{
		// Open edge: a new window. The pack has just cleared its hit set and refreshed the previous positions (ActivateCollision).
		bWasActive = true;
		++WindowId;
		OpenRefreshError = 0.f;
		OpenCarried.Reset();
		if (const UPrimitiveComponent* Mesh = Target.GetMesh())
		{
			TArray<FName> Sockets;
			Target.GetSockets(Sockets);
			for (const FName& Socket : Sockets)
			{
				FVector Stored;
				if (Target.GetStoredLocation(Socket, Stored))
				{
					OpenRefreshError = FMath::Max(OpenRefreshError, static_cast<float>(FVector::Dist(Stored, Mesh->GetSocketLocation(Socket))));
				}
			}
		}
		const int32 Instance = (Tracker && Tracker->GetCurrentMove() != NAME_None) ? Tracker->GetAttackInstance() : -1;
		if (bDedupePerInstance && Instance >= 0 && Instance == LastWindowInstance)
		{
			// Another window of the same swing: whoever the swing already hit stays hit (one damage event per instance).
			for (const TWeakObjectPtr<AActor>& Old : LastSet)
			{
				if (AActor* Actor = Old.Get())
				{
					if (Target.HitSetAdd(Actor))
					{
						++CarryCount;
						OpenCarried.Add(Actor);
					}
				}
			}
		}
		LastWindowInstance = Instance;
	}

	// Remember the hit set of this window (the pack clears it only at the next activation).
	{
		TArray<AActor*> Set;
		Target.GetHitSet(Set);
		LastSet.Reset();
		for (AActor* Actor : Set)
		{
			LastSet.Add(Actor);
		}
	}

	// Death closes the trace (Freeze 779).
	double Health = 1.0;
	if (bCloseOnInterrupt && ReadAttribute(Boss, TEXT("Attribute.Health"), false, Health) && Health <= 0.0)
	{
		CloseTraceNow(TEXT("dead"));
		return;
	}

	// Walls (Freeze 560): a blocked line from the boss to the player puts the player into the hit set for this one pack sample.
	if (bBlockThroughWalls)
	{
		AActor* Player = UGameplayStatics::GetPlayerPawn(this, 0);
		if (Player && !Target.HitSetContains(Player))
		{
			FCollisionQueryParams Params(SCENE_QUERY_STAT(RPGTraceGuardLos), false);
			Params.AddIgnoredActor(Boss);
			Params.AddIgnoredActor(Player);
			FHitResult Hit;
			if (GetWorld()->LineTraceSingleByObjectType(Hit, Boss->GetActorLocation(), Player->GetActorLocation(), RPGBossDamage::WorldBlockers(), Params))
			{
				if (Target.HitSetAdd(Player))
				{
					TempSeed = Player;
					SeedWindow = WindowId;
					++OccludedSamples;
				}
			}
		}
	}
}
