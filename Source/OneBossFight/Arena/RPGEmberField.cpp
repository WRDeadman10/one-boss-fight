// Copyright One Boss Fight. All Rights Reserved.

#include "Arena/RPGEmberField.h"
#include "Components/InstancedStaticMeshComponent.h"
#include "Components/SceneComponent.h"
#include "Engine/StaticMesh.h"
#include "Materials/MaterialInterface.h"

namespace
{
	// Engine basic shapes are 100 uu across.
	constexpr float BasicShapeSize = 100.f;
}

ARPGEmberField::ARPGEmberField()
{
	PrimaryActorTick.bCanEverTick = true;
	PrimaryActorTick.bStartWithTickEnabled = true;
	USceneComponent* Root = CreateDefaultSubobject<USceneComponent>(TEXT("Root"));
	SetRootComponent(Root);
}

void ARPGEmberField::Rebuild()
{
#if WITH_EDITOR // RerunConstructionScripts exists only in editor builds (the packaged game target failed to compile without this guard)
	RerunConstructionScripts();
#endif
}

void ARPGEmberField::Respawn(FEmber& Ember, bool bRandomAge)
{
	const bool bFromFire = !FireSources.IsEmpty() && Random.FRand() < FireShare;
	if (bFromFire)
	{
		const FVector Source = FireSources[Random.RandRange(0, FireSources.Num() - 1)];
		const float Angle = Random.FRandRange(0.f, 2.f * PI);
		const float Spread = Random.FRandRange(0.f, 35.f);
		Ember.Position = Source + FVector(FMath::Cos(Angle) * Spread, FMath::Sin(Angle) * Spread, Random.FRandRange(0.f, 40.f));
		Ember.RiseSpeed = Random.FRandRange(RiseSpeedMin, RiseSpeedMax);
	}
	else
	{
		// Ash in the open air: slow, low, anywhere over the floor.
		const float Angle = Random.FRandRange(0.f, 2.f * PI);
		const float Radius = ArenaRadius * FMath::Sqrt(Random.FRand());
		Ember.Position = FVector(FMath::Cos(Angle) * Radius, FMath::Sin(Angle) * Radius, Random.FRandRange(60.f, 600.f));
		Ember.RiseSpeed = Random.FRandRange(RiseSpeedMin * 0.15f, RiseSpeedMin * 0.5f);
	}
	Ember.Life = Random.FRandRange(LifeMin, LifeMax);
	Ember.Age = bRandomAge ? Random.FRandRange(0.f, Ember.Life) : 0.f;
	Ember.Size = Random.FRandRange(SizeMin, SizeMax);
	Ember.Phase = Random.FRandRange(0.f, 2.f * PI);
	Ember.Frequency = Random.FRandRange(0.8f, 2.4f);
	if (bRandomAge)
	{
		Ember.Position += FVector(0.f, 0.f, Ember.RiseSpeed * Ember.Age); // as if it had been rising already
	}
}

void ARPGEmberField::OnConstruction(const FTransform& Transform)
{
	Super::OnConstruction(Transform);
	if (Instances)
	{
		Instances->DestroyComponent();
		Instances = nullptr;
	}
	Embers.Reset();
	if (!Mesh)
	{
		return;
	}
	Instances = NewObject<UInstancedStaticMeshComponent>(this, NAME_None, RF_Transient);
	Instances->SetMobility(EComponentMobility::Movable);
	Instances->SetStaticMesh(Mesh);
	Instances->SetCollisionEnabled(ECollisionEnabled::NoCollision);
	Instances->SetCastShadow(false);
	Instances->bAffectDistanceFieldLighting = false;
	Instances->bAffectDynamicIndirectLighting = false;
	Instances->SetCanEverAffectNavigation(false);
	Instances->SetGenerateOverlapEvents(false);
	if (Material)
	{
		Instances->SetMaterial(0, Material);
	}
	Instances->SetupAttachment(GetRootComponent());
	Instances->RegisterComponent();
	AddInstanceComponent(Instances);

	Random.Initialize(Seed);
	Embers.SetNum(Count);
	TArray<FTransform> Transforms;
	Transforms.Reserve(Count);
	for (FEmber& Ember : Embers)
	{
		Respawn(Ember, /*bRandomAge=*/true);
		Transforms.Add(FTransform(FRotator::ZeroRotator, Ember.Position, FVector(Ember.Size / BasicShapeSize)));
	}
	Instances->AddInstances(Transforms, /*bShouldReturnIndices=*/false, /*bWorldSpace=*/false);
}

void ARPGEmberField::Tick(float DeltaSeconds)
{
	Super::Tick(DeltaSeconds);
	if (!Instances || Embers.IsEmpty())
	{
		return;
	}
	Clock += DeltaSeconds;
	TArray<FTransform> Transforms;
	Transforms.Reserve(Embers.Num());
	for (FEmber& Ember : Embers)
	{
		Ember.Age += DeltaSeconds;
		if (Ember.Age >= Ember.Life)
		{
			Respawn(Ember, /*bRandomAge=*/false);
		}
		const float T = Clock * Ember.Frequency + Ember.Phase;
		Ember.Position += FVector(
			Wind.X + Sway * FMath::Sin(T),
			Wind.Y + Sway * FMath::Cos(T * 0.83f),
			Ember.RiseSpeed + 25.f * FMath::Sin(T * 0.6f)) * DeltaSeconds;
		// Swell in, glow, shrink out: a sine over the life gives a soft start and end.
		const float Fade = FMath::Sin(PI * FMath::Clamp(Ember.Age / Ember.Life, 0.f, 1.f));
		Transforms.Add(FTransform(FRotator::ZeroRotator, Ember.Position, FVector(FMath::Max(0.001f, Ember.Size * Fade) / BasicShapeSize)));
	}
	Instances->BatchUpdateInstancesTransforms(0, Transforms, /*bWorldSpace=*/false, /*bMarkRenderStateDirty=*/true, /*bTeleport=*/true);
}
