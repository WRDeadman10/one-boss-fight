// Copyright One Boss Fight. All Rights Reserved.

#include "Combat/RPGMeleeTraceComponent.h"
#include "Combat/RPGCombatComponent.h"
#include "Combat/RPGWeaponData.h"
#include "DrawDebugHelpers.h"
#include "Engine/World.h"
#include "GameFramework/Character.h"
#include "HAL/IConsoleManager.h"

static TAutoConsoleVariable<int32> CVarCombatDebug(
	TEXT("rpg.Combat.Debug"), 0,
	TEXT("1 = draw melee sweeps and combat state text above combatants."),
	ECVF_Cheat);

URPGMeleeTraceComponent::URPGMeleeTraceComponent()
{
	PrimaryComponentTick.bCanEverTick = true;
	PrimaryComponentTick.bStartWithTickEnabled = false;
	// After animation has produced this frame's bone transforms.
	PrimaryComponentTick.TickGroup = TG_PostUpdateWork;
}

void URPGMeleeTraceComponent::OnRegister()
{
	Super::OnRegister();

	URPGCombatComponent* Combat = GetOwner() ? GetOwner()->FindComponentByClass<URPGCombatComponent>() : nullptr;
	if (Combat && BoundCombat.Get() != Combat)
	{
		Combat->OnHitWindowChanged.AddUObject(this, &URPGMeleeTraceComponent::HandleHitWindowChanged);
		BoundCombat = Combat;
	}
}

void URPGMeleeTraceComponent::OnUnregister()
{
	if (URPGCombatComponent* Combat = BoundCombat.Get())
	{
		Combat->OnHitWindowChanged.RemoveAll(this);
	}
	BoundCombat.Reset();
	Super::OnUnregister();
}

void URPGMeleeTraceComponent::HandleHitWindowChanged(bool bOpen)
{
	if (bOpen)
	{
		const URPGCombatComponent* Combat = BoundCombat.Get();
		BeginSwing(Combat ? Combat->BuildOutgoingHit() : FRPGHitInfo());
	}
	else
	{
		EndSwing();
	}
}

void URPGMeleeTraceComponent::BeginSwing(const FRPGHitInfo& Template)
{
	bSwinging = true;
	SwingTemplate = Template;
	HitActors.Reset();

	// Start from the pose of the previous frame so the first sweep covers motion since the window opened.
	float Radius = 0.f;
	bHavePrevious = GetSamplePoints(PreviousPoints, Radius);

	if (IsRegistered())
	{
		SetComponentTickEnabled(true);
	}
}

void URPGMeleeTraceComponent::EndSwing()
{
	bSwinging = false;
	bHavePrevious = false;
	if (IsRegistered())
	{
		SetComponentTickEnabled(false);
	}
}

void URPGMeleeTraceComponent::TickComponent(float DeltaTime, ELevelTick TickType, FActorComponentTickFunction* ThisTickFunction)
{
	Super::TickComponent(DeltaTime, TickType, ThisTickFunction);
	if (!bSwinging)
	{
		return;
	}

	TArray<FVector, TInlineAllocator<8>> Current;
	float Radius = 0.f;
	if (!GetSamplePoints(Current, Radius))
	{
		return;
	}

	const bool bCanSweepFromPrevious = bHavePrevious && PreviousPoints.Num() == Current.Num();
	for (int32 Index = 0; Index < Current.Num(); ++Index)
	{
		// Zero-length on the first frame is an overlap test at the current pose.
		const FVector Start = bCanSweepFromPrevious ? PreviousPoints[Index] : Current[Index];
		ProcessSweep(Start, Current[Index], Radius);
	}

	PreviousPoints = Current;
	bHavePrevious = true;
}

USceneComponent* URPGMeleeTraceComponent::ResolveTraceComponent() const
{
	const AActor* Owner = GetOwner();
	if (!Owner)
	{
		return nullptr;
	}

	const URPGCombatComponent* Combat = BoundCombat.Get();
	const FName WantedName = (Combat && Combat->Weapon) ? Combat->Weapon->TraceComponentName : NAME_None;
	if (WantedName != NAME_None)
	{
		TInlineComponentArray<USceneComponent*> Components(Owner);
		for (USceneComponent* Component : Components)
		{
			if (Component->GetFName() == WantedName)
			{
				return Component;
			}
		}
	}

	const ACharacter* Character = Cast<ACharacter>(Owner);
	return Character ? static_cast<USceneComponent*>(Character->GetMesh()) : Owner->GetRootComponent();
}

bool URPGMeleeTraceComponent::GetSamplePoints(TArray<FVector, TInlineAllocator<8>>& OutPoints, float& OutRadius) const
{
	OutPoints.Reset();
	const AActor* Owner = GetOwner();
	if (!Owner)
	{
		return false;
	}

	const URPGCombatComponent* Combat = BoundCombat.Get();
	const URPGWeaponData* Weapon = Combat ? Combat->Weapon.Get() : nullptr;
	const USceneComponent* TraceComponent = ResolveTraceComponent();

	if (Weapon && TraceComponent && Weapon->TraceBaseSocket != NAME_None && Weapon->TraceTipSocket != NAME_None)
	{
		const FVector Base = TraceComponent->GetSocketLocation(Weapon->TraceBaseSocket);
		const FVector Tip = TraceComponent->GetSocketLocation(Weapon->TraceTipSocket);
		const int32 Samples = FMath::Clamp(Weapon->TraceSamples, 1, 8);
		for (int32 Index = 0; Index < Samples; ++Index)
		{
			const float Alpha = Samples == 1 ? 1.f : static_cast<float>(Index) / (Samples - 1);
			OutPoints.Add(FMath::Lerp(Base, Tip, Alpha));
		}
		OutRadius = Weapon->TraceRadius;
		return true;
	}

	// No weapon sockets configured: a sphere in front of the owner keeps combat usable on dummies and tests.
	OutPoints.Add(Owner->GetActorLocation() + Owner->GetActorForwardVector() * FallbackReach);
	OutRadius = FallbackRadius;
	return true;
}

int32 URPGMeleeTraceComponent::ProcessSweep(const FVector& Start, const FVector& End, float Radius)
{
	UWorld* World = GetWorld();
	AActor* Owner = GetOwner();
	if (!World || !Owner)
	{
		return 0;
	}

#if ENABLE_DRAW_DEBUG
	if (CVarCombatDebug.GetValueOnGameThread() > 0)
	{
		DrawDebugLine(World, Start, End, FColor::Red, false, 0.5f, 0, 1.f);
		DrawDebugSphere(World, End, Radius, 8, FColor::Orange, false, 0.1f);
	}
#endif

	FCollisionQueryParams Params(SCENE_QUERY_STAT(RPGMeleeSweep), /*bTraceComplex=*/false, Owner);
	TArray<FHitResult> Hits;
	World->SweepMultiByObjectType(Hits, Start, End, FQuat::Identity, FCollisionObjectQueryParams(ECC_Pawn),
		FCollisionShape::MakeSphere(Radius), Params);

	const URPGCombatComponent* OwnerCombat = BoundCombat.Get();
	int32 NewHits = 0;
	for (const FHitResult& Hit : Hits)
	{
		AActor* Target = Hit.GetActor();
		if (!Target || HitActors.Contains(Target))
		{
			continue;
		}

		URPGCombatComponent* TargetCombat = Target->FindComponentByClass<URPGCombatComponent>();
		if (!TargetCombat || (OwnerCombat && TargetCombat->TeamId == OwnerCombat->TeamId))
		{
			continue;
		}

		// Recorded even if the target ignores it (i-frames): one chance per swing, never a second after they end.
		HitActors.Add(Target);

		FRPGHitInfo Info = SwingTemplate;
		Info.Instigator = Owner;
		Info.HitLocation = Hit.ImpactPoint.IsZero() ? FVector(Hit.Location) : FVector(Hit.ImpactPoint);
		Info.HitDirection = (Target->GetActorLocation() - Owner->GetActorLocation()).GetSafeNormal2D();

		const FRPGHitResult Result = TargetCombat->ProcessIncomingHit(Info);
		OnTargetHit.Broadcast(Target, Result);
		++NewHits;
	}
	return NewHits;
}
