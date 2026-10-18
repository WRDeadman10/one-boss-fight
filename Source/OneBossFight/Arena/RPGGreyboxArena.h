// Copyright One Boss Fight. All Rights Reserved.

#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "RPGGreyboxArena.generated.h"

class UInstancedStaticMeshComponent;
class UStaticMeshComponent;

/**
 * Procedural circular greybox arena built from engine primitives: a floor disc, a ring of
 * pillars and a low boundary wall. Everything is driven by the properties below, so the
 * arena can be resized for gameplay tests before final art replaces it.
 * Floor top surface sits at the actor's Z.
 */
UCLASS()
class ONEBOSSFIGHT_API ARPGGreyboxArena : public AActor
{
	GENERATED_BODY()

public:
	ARPGGreyboxArena();

	virtual void OnConstruction(const FTransform& Transform) override;

	/** World-space position of pillar Index on the ring (center of its base on the floor). */
	FVector GetPillarBaseLocation(int32 Index) const;

	/** Arena radius to the inside face of the wall, in cm. */
	UPROPERTY(EditAnywhere, Category = "Arena", meta = (ClampMin = "500"))
	float ArenaRadius = 3000.f;

	UPROPERTY(EditAnywhere, Category = "Arena", meta = (ClampMin = "10"))
	float FloorThickness = 100.f;

	UPROPERTY(EditAnywhere, Category = "Pillars", meta = (ClampMin = "0", ClampMax = "64"))
	int32 PillarCount = 12;

	/** Pillar ring radius as a fraction of ArenaRadius. */
	UPROPERTY(EditAnywhere, Category = "Pillars", meta = (ClampMin = "0.1", ClampMax = "0.99"))
	float PillarRingFraction = 0.9f;

	UPROPERTY(EditAnywhere, Category = "Pillars", meta = (ClampMin = "10"))
	float PillarRadius = 120.f;

	UPROPERTY(EditAnywhere, Category = "Pillars", meta = (ClampMin = "50"))
	float PillarHeight = 900.f;

	UPROPERTY(EditAnywhere, Category = "Wall", meta = (ClampMin = "8", ClampMax = "256"))
	int32 WallSegmentCount = 48;

	UPROPERTY(EditAnywhere, Category = "Wall", meta = (ClampMin = "10"))
	float WallThickness = 80.f;

	UPROPERTY(EditAnywhere, Category = "Wall", meta = (ClampMin = "50"))
	float WallHeight = 300.f;

	UStaticMeshComponent* GetFloorMesh() const { return FloorMesh; }

private:
	/** Pillar base in actor-local space. */
	FVector GetPillarLocalBase(int32 Index) const;

	UPROPERTY(VisibleAnywhere, Category = "Arena")
	TObjectPtr<UStaticMeshComponent> FloorMesh;

	UPROPERTY(VisibleAnywhere, Category = "Arena")
	TObjectPtr<UInstancedStaticMeshComponent> Pillars;

	UPROPERTY(VisibleAnywhere, Category = "Arena")
	TObjectPtr<UInstancedStaticMeshComponent> Walls;
};
