// Copyright One Boss Fight. All Rights Reserved.

#include "Arena/RPGArenaDressing.h"
#include "Arena/RPGPerfSwitches.h"
#include "Components/InstancedStaticMeshComponent.h"
#include "Components/SceneComponent.h"
#include "Engine/StaticMesh.h"
#include "Materials/MaterialInterface.h"

ARPGArenaDressing::ARPGArenaDressing()
{
	PrimaryActorTick.bCanEverTick = true;
	PrimaryActorTick.bStartWithTickEnabled = true;
	USceneComponent* Root = CreateDefaultSubobject<USceneComponent>(TEXT("Root"));
	Root->SetMobility(EComponentMobility::Static);
	SetRootComponent(Root);
}

int32 ARPGArenaDressing::GetInstanceCount() const
{
	int32 Count = 0;
	for (const FRPGDressingSet& Set : Sets)
	{
		Count += Set.Instances.Num();
	}
	return Count;
}

void ARPGArenaDressing::OnConstruction(const FTransform& Transform)
{
	Super::OnConstruction(Transform);

	// Rebuild from scratch: construction runs on every property change in the editor.
	for (UInstancedStaticMeshComponent* Old : Built)
	{
		if (Old)
		{
			Old->DestroyComponent();
		}
	}
	Built.Reset();
	Swaying.Reset();

	for (int32 SetIndex = 0; SetIndex < Sets.Num(); ++SetIndex)
	{
		const FRPGDressingSet& Set = Sets[SetIndex];
		if (!Set.Mesh || Set.Instances.IsEmpty())
		{
			continue;
		}
		UInstancedStaticMeshComponent* Component = NewObject<UInstancedStaticMeshComponent>(this, NAME_None, RF_Transient);
		Component->SetMobility(Set.SwayDegrees > 0.f ? EComponentMobility::Movable : EComponentMobility::Static);
		Component->SetStaticMesh(Set.Mesh);
		Component->SetCollisionEnabled(Set.bCollision ? ECollisionEnabled::QueryAndPhysics : ECollisionEnabled::NoCollision);
		if (Set.bCollision)
		{
			Component->SetCollisionProfileName(TEXT("BlockAll"));
		}
		Component->SetCastShadow(Set.bCastShadow);
		if (Set.MaterialOverride)
		{
			Component->SetMaterial(0, Set.MaterialOverride);
		}
		Component->SetupAttachment(GetRootComponent());
		Component->RegisterComponent();
		AddInstanceComponent(Component);
		Component->AddInstances(Set.Instances, /*bShouldReturnIndices=*/false, /*bWorldSpace=*/false);
		Built.Add(Component);
		if (Set.SwayDegrees > 0.f)
		{
			FSwaying Sway;
			Sway.Component = Component;
			Sway.Rest = Set.Instances;
			Sway.Degrees = Set.SwayDegrees;
			Sway.Pivot = Set.SwayPivot;
			Swaying.Add(MoveTemp(Sway));
		}
	}
}

void ARPGArenaDressing::Rebuild()
{
#if WITH_EDITOR // RerunConstructionScripts exists only in editor builds (the packaged game target failed to compile without this guard)
	RerunConstructionScripts();
#endif
}

void ARPGArenaDressing::Tick(float DeltaSeconds)
{
	Super::Tick(DeltaSeconds);
#if !UE_BUILD_SHIPPING
	// performance experiments (rpg.Perf.*): see RPGPerfSwitches.h
	for (UInstancedStaticMeshComponent* Component : Built)
	{
		if (!Component)
		{
			continue;
		}
		const bool bMist = Component->GetStaticMesh() && Component->GetStaticMesh()->GetName().Contains(TEXT("FogCard"));
		Component->SetVisibility(RPGPerf::DressingAll() && (RPGPerf::DressingMist() || !bMist));
		if (!RPGPerf::DressingShadows())
		{
			Component->SetCastShadow(false);
		}
	}
#endif
	if (Swaying.IsEmpty())
	{
		return;
	}
	Clock += DeltaSeconds;
	for (const FSwaying& Set : Swaying)
	{
		if (!Set.Component)
		{
			continue;
		}
		TArray<FTransform> Moved;
		Moved.Reserve(Set.Rest.Num());
		for (int32 Index = 0; Index < Set.Rest.Num(); ++Index)
		{
			const FTransform& Rest = Set.Rest[Index];
			// A slow swell and a faster flutter, a different phase per instance (from its position, so it survives rebuilds).
			const float Phase = Rest.GetLocation().X * 0.0031f + Rest.GetLocation().Y * 0.0047f;
			const float Wave = 0.7f * FMath::Sin(Clock * 0.9f + Phase) + 0.3f * FMath::Sin(Clock * 2.3f + Phase * 1.7f);
			const FQuat Swing(Rest.GetUnitAxis(EAxis::Y), FMath::DegreesToRadians(Set.Degrees * Wave));
			const FVector Hang = Rest.TransformPosition(Set.Pivot);
			Moved.Add(FTransform(Swing * Rest.GetRotation(), Hang + Swing.RotateVector(Rest.GetLocation() - Hang), Rest.GetScale3D()));
		}
		Set.Component->BatchUpdateInstancesTransforms(0, Moved, /*bWorldSpace=*/false, /*bMarkRenderStateDirty=*/true, /*bTeleport=*/true);
	}
}
