// Copyright One Boss Fight. All Rights Reserved.

#include "Arena/RPGGreyboxArena.h"
#include "Components/InstancedStaticMeshComponent.h"
#include "Components/SceneComponent.h"
#include "Components/StaticMeshComponent.h"
#include "Engine/StaticMesh.h"
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

	// Instances are in root-local space (the root is unscaled).
	Pillars->ClearInstances();
	Walls->ClearInstances();

	const FVector PillarScale(PillarRadius * 2.f / BasicShapeSize, PillarRadius * 2.f / BasicShapeSize, PillarHeight / BasicShapeSize);
	for (int32 Index = 0; Index < PillarCount; ++Index)
	{
		const FVector Location = GetPillarLocalBase(Index) + FVector(0.f, 0.f, PillarHeight * 0.5f);
		Pillars->AddInstance(FTransform(FRotator::ZeroRotator, Location, PillarScale), /*bWorldSpace=*/false);
	}

	// Wall segments: local X is radial (thickness), local Y is tangential (chord), local Z is height.
	const float WallCenterRadius = ArenaRadius + WallThickness * 0.5f;
	const float Circumference = 2.f * PI * WallCenterRadius;
	const float Chord = Circumference / static_cast<float>(FMath::Max(WallSegmentCount, 1)) * 1.02f; // slight overlap, no gaps
	const FVector WallScale(WallThickness / BasicShapeSize, Chord / BasicShapeSize, WallHeight / BasicShapeSize);
	for (int32 Index = 0; Index < WallSegmentCount; ++Index)
	{
		const float Angle = 2.f * PI * static_cast<float>(Index) / static_cast<float>(WallSegmentCount);
		const FVector Location(FMath::Cos(Angle) * WallCenterRadius, FMath::Sin(Angle) * WallCenterRadius, WallHeight * 0.5f);
		const FRotator Rotation(0.f, FMath::RadiansToDegrees(Angle), 0.f);
		Walls->AddInstance(FTransform(Rotation, Location, WallScale), /*bWorldSpace=*/false);
	}
}
