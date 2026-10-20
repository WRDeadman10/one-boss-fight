// Copyright One Boss Fight. All Rights Reserved.

#include "Arena/RPGGreyboxArena.h"
#include "Components/InstancedStaticMeshComponent.h"
#include "Components/SceneComponent.h"
#include "Components/StaticMeshComponent.h"
#include "Engine/StaticMesh.h"
#include "Materials/MaterialInterface.h"
#include "UObject/ConstructorHelpers.h"

namespace
{
	// Engine basic shapes are 100 x 100 x 100 uu; scale factors below assume that.
	constexpr float BasicShapeSize = 100.f;
}

ARPGGreyboxArena::ARPGGreyboxArena()
{
	PrimaryActorTick.bCanEverTick = false;

	static ConstructorHelpers::FObjectFinder<UStaticMesh> CylinderMesh(TEXT("/Engine/BasicShapes/Cylinder.Cylinder"));
	static ConstructorHelpers::FObjectFinder<UStaticMesh> CubeMesh(TEXT("/Engine/BasicShapes/Cube.Cube"));

	// Unscaled root so the scaled floor never distorts the pillar/wall instances.
	USceneComponent* Root = CreateDefaultSubobject<USceneComponent>(TEXT("Root"));
	Root->SetMobility(EComponentMobility::Static);
	SetRootComponent(Root);

	FloorMesh = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("Floor"));
	FloorMesh->SetupAttachment(Root);
	FloorMesh->SetMobility(EComponentMobility::Static);
	FloorMesh->SetCollisionProfileName(TEXT("BlockAll"));
	if (CylinderMesh.Succeeded())
	{
		FloorMesh->SetStaticMesh(CylinderMesh.Object);
	}

	Pillars = CreateDefaultSubobject<UInstancedStaticMeshComponent>(TEXT("Pillars"));
	Pillars->SetupAttachment(Root);
	Pillars->SetMobility(EComponentMobility::Static);
	Pillars->SetCollisionProfileName(TEXT("BlockAll"));
	if (CylinderMesh.Succeeded())
	{
		Pillars->SetStaticMesh(CylinderMesh.Object);
	}

	Walls = CreateDefaultSubobject<UInstancedStaticMeshComponent>(TEXT("Walls"));
	Walls->SetupAttachment(Root);
	Walls->SetMobility(EComponentMobility::Static);
	Walls->SetCollisionProfileName(TEXT("BlockAll"));
	if (CubeMesh.Succeeded())
	{
		Walls->SetStaticMesh(CubeMesh.Object);
	}
	GreyCylinder = CylinderMesh.Succeeded() ? CylinderMesh.Object : nullptr;
	GreyCube = CubeMesh.Succeeded() ? CubeMesh.Object : nullptr;

	// Art-pass components stay empty until their meshes are assigned.
	auto MakeInstances = [this, Root](const TCHAR* Name, bool bCollides)
	{
		UInstancedStaticMeshComponent* Component = CreateDefaultSubobject<UInstancedStaticMeshComponent>(Name);
		Component->SetupAttachment(Root);
		Component->SetMobility(EComponentMobility::Static);
		if (bCollides)
		{
			Component->SetCollisionProfileName(TEXT("BlockAll"));
		}
		else
		{
			Component->SetCollisionEnabled(ECollisionEnabled::NoCollision);
		}
		return Component;
	};
	PillarsCracked = MakeInstances(TEXT("PillarsCracked"), true);
	PillarsBroken = MakeInstances(TEXT("PillarsBroken"), true);
	WallsDamaged = MakeInstances(TEXT("WallsDamaged"), true);
	Braziers = MakeInstances(TEXT("Braziers"), true);
	Debris = MakeInstances(TEXT("Debris"), false);

	Arch = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("Arch"));
	Arch->SetupAttachment(Root);
	Arch->SetMobility(EComponentMobility::Static);
	Arch->SetCollisionProfileName(TEXT("BlockAll"));
}

FVector ARPGGreyboxArena::GetPillarLocalBase(int32 Index) const
{
	const float Angle = 2.f * PI * static_cast<float>(Index) / static_cast<float>(FMath::Max(PillarCount, 1));
	const float Ring = ArenaRadius * PillarRingFraction;
	return FVector(FMath::Cos(Angle) * Ring, FMath::Sin(Angle) * Ring, 0.f);
}

FVector ARPGGreyboxArena::GetPillarBaseLocation(int32 Index) const
{
	return GetActorTransform().TransformPosition(GetPillarLocalBase(Index));
}

void ARPGGreyboxArena::OnConstruction(const FTransform& Transform)
{
	Super::OnConstruction(Transform);

	// Floor: the basic cylinder is 100 uu in diameter and height. Its top face sits at the actor origin.
	FloorMesh->SetRelativeScale3D(FVector(ArenaRadius * 2.f / BasicShapeSize, ArenaRadius * 2.f / BasicShapeSize, FloorThickness / BasicShapeSize));
	FloorMesh->SetRelativeLocation(FVector(0.f, 0.f, -FloorThickness * 0.5f));

	// Floor material (the world-aligned stone material needs no UVs).
	if (FloorMaterial)
	{
		FloorMesh->SetMaterial(0, FloorMaterial);
	}

	// Instances are in root-local space (the root is unscaled).
	for (UInstancedStaticMeshComponent* Component : {Pillars.Get(), Walls.Get(), PillarsCracked.Get(), PillarsBroken.Get(), WallsDamaged.Get(), Braziers.Get(), Debris.Get()})
	{
		Component->ClearInstances();
	}

	const bool bArtPillars = PillarIntact != nullptr;
	const bool bArtWalls = WallIntact != nullptr;

	Pillars->SetStaticMesh(bArtPillars ? PillarIntact.Get() : GreyCylinder.Get());
	PillarsCracked->SetStaticMesh(bArtPillars ? PillarCracked.Get() : nullptr);
	PillarsBroken->SetStaticMesh(bArtPillars ? PillarBroken.Get() : nullptr);
	Walls->SetStaticMesh(bArtWalls ? WallIntact.Get() : GreyCube.Get());
	WallsDamaged->SetStaticMesh(bArtWalls ? WallDamaged.Get() : nullptr);
	if (PillarMaterial)
	{
		for (UInstancedStaticMeshComponent* Component : {Pillars.Get(), PillarsCracked.Get(), PillarsBroken.Get()})
		{
			Component->SetMaterial(0, PillarMaterial);
		}
	}
	if (WallMaterial)
	{
		Walls->SetMaterial(0, WallMaterial);
		WallsDamaged->SetMaterial(0, WallMaterial);
	}

	const FVector PillarScale(PillarRadius * 2.f / BasicShapeSize, PillarRadius * 2.f / BasicShapeSize, PillarHeight / BasicShapeSize);
	for (int32 Index = 0; Index < PillarCount; ++Index)
	{
		if (!bArtPillars)
		{
			const FVector Location = GetPillarLocalBase(Index) + FVector(0.f, 0.f, PillarHeight * 0.5f);
			Pillars->AddInstance(FTransform(FRotator::ZeroRotator, Location, PillarScale), /*bWorldSpace=*/false);
			continue;
		}

		// Art meshes have their origin on the floor and keep their own proportions.
		const float Angle = 360.f * static_cast<float>(Index) / static_cast<float>(FMath::Max(PillarCount, 1));
		if (EntranceArch && FMath::Abs(FRotator::NormalizeAxis(Angle - ArchAngleDegrees)) < 12.f)
		{
			continue; // the arch's doorway would otherwise open onto a pillar
		}
		const FTransform Placement(FRotator(0.f, Angle, 0.f), GetPillarLocalBase(Index));
		const bool bBroken = PillarBroken && BrokenEvery > 0 && Index % BrokenEvery == BrokenEvery - 1;
		const bool bCracked = PillarCracked && CrackedEvery > 0 && Index % CrackedEvery == 1;
		UInstancedStaticMeshComponent* Target = bBroken ? PillarsBroken.Get() : (bCracked ? PillarsCracked.Get() : Pillars.Get());
		Target->AddInstance(Placement, /*bWorldSpace=*/false);
	}

	// Wall segments: local X is radial (thickness), local Y is tangential (chord), local Z is height.
	const float WallCenterRadius = ArenaRadius + WallThickness * 0.5f;
	const float Circumference = 2.f * PI * WallCenterRadius;
	const float Chord = Circumference / static_cast<float>(FMath::Max(WallSegmentCount, 1)) * 1.02f; // slight overlap, no gaps
	const FVector WallScale(WallThickness / BasicShapeSize, Chord / BasicShapeSize, WallHeight / BasicShapeSize);
	for (int32 Index = 0; Index < WallSegmentCount; ++Index)
	{
		const float Angle = 2.f * PI * static_cast<float>(Index) / static_cast<float>(WallSegmentCount);
		const FRotator Rotation(0.f, FMath::RadiansToDegrees(Angle), 0.f);
		if (!bArtWalls)
		{
			const FVector Location(FMath::Cos(Angle) * WallCenterRadius, FMath::Sin(Angle) * WallCenterRadius, WallHeight * 0.5f);
			Walls->AddInstance(FTransform(Rotation, Location, WallScale), /*bWorldSpace=*/false);
			continue;
		}
		const FVector Location(FMath::Cos(Angle) * WallCenterRadius, FMath::Sin(Angle) * WallCenterRadius, 0.f);
		const bool bDamaged = WallDamaged && DamagedWallEvery > 0 && Index % DamagedWallEvery == DamagedWallEvery - 1;
		(bDamaged ? WallsDamaged.Get() : Walls.Get())->AddInstance(FTransform(Rotation, Location), /*bWorldSpace=*/false);
	}

	// Braziers between the pillars.
	Braziers->SetStaticMesh(Brazier);
	if (BrazierMaterial)
	{
		Braziers->SetMaterial(0, BrazierMaterial);
	}
	if (Brazier)
	{
		for (int32 Index = 0; Index < PillarCount; ++Index)
		{
			const float Angle = 2.f * PI * (static_cast<float>(Index) + 0.5f) / static_cast<float>(FMath::Max(PillarCount, 1));
			const float Ring = ArenaRadius * BrazierRingFraction;
			Braziers->AddInstance(FTransform(FRotator(0.f, FMath::RadiansToDegrees(Angle), 0.f),
				FVector(FMath::Cos(Angle) * Ring, FMath::Sin(Angle) * Ring, 0.f)), /*bWorldSpace=*/false);
		}
	}

	// Scattered rubble: no collision, never in the way.
	Debris->SetStaticMesh(Rubble);
	if (RubbleMaterial)
	{
		Debris->SetMaterial(0, RubbleMaterial);
	}
	if (Rubble)
	{
		FRandomStream Random(ScatterSeed);
		for (int32 Index = 0; Index < RubbleCount; ++Index)
		{
			const float Angle = Random.FRandRange(0.f, 2.f * PI);
			const float Radius = ArenaRadius * FMath::Sqrt(Random.FRandRange(0.02f, 0.72f));
			const float Scale = Random.FRandRange(0.8f, 1.5f);
			Debris->AddInstance(FTransform(FRotator(0.f, Random.FRandRange(0.f, 360.f), 0.f),
				FVector(FMath::Cos(Angle) * Radius, FMath::Sin(Angle) * Radius, 0.f), FVector(Scale)), /*bWorldSpace=*/false);
		}
	}

	// Entrance arch.
	Arch->SetStaticMesh(EntranceArch);
	Arch->SetVisibility(EntranceArch != nullptr);
	Arch->SetCollisionEnabled(EntranceArch ? ECollisionEnabled::QueryAndPhysics : ECollisionEnabled::NoCollision);
	if (EntranceArch)
	{
		const float Angle = FMath::DegreesToRadians(ArchAngleDegrees);
		const float Ring = ArenaRadius * ArchRadiusFraction;
		Arch->SetRelativeLocationAndRotation(FVector(FMath::Cos(Angle) * Ring, FMath::Sin(Angle) * Ring, 0.f), FRotator(0.f, ArchAngleDegrees, 0.f));
		if (ArchMaterial)
		{
			Arch->SetMaterial(0, ArchMaterial);
		}
	}
}

void ARPGGreyboxArena::Rebuild()
{
	RerunConstructionScripts();
}
