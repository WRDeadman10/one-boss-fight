// Copyright One Boss Fight. All Rights Reserved.

#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "RPGGreyboxArena.generated.h"

class UInstancedStaticMeshComponent;
class UMaterialInterface;
class UStaticMesh;
class UStaticMeshComponent;

/**
 * Procedural circular greybox arena built from engine primitives: a floor disc, a ring of
 * pillars and a low boundary wall. Everything is driven by the properties below, so the
 * arena can be resized for gameplay tests before final art replaces it.
 * Floor top surface sits at the actor's Z.
 *
 * Art pass: assigning the meshes under "Art" swaps the primitives for real pieces at the same footprint
 * (pillar ring, wall ring) and adds braziers, rubble and an entrance arch. Every art property is optional, so the
 * greybox keeps working (the automation tests run on it).
 */
UCLASS()
class ONEBOSSFIGHT_API ARPGGreyboxArena : public AActor
{
	GENERATED_BODY()

public:
	ARPGGreyboxArena();

	virtual void OnConstruction(const FTransform& Transform) override;

	/** Runs the construction again after the editor scripts changed properties (Python cannot call RerunConstructionScripts). */
	UFUNCTION(BlueprintCallable, CallInEditor, Category = "Editor")
	void Rebuild();

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

	/** Every pillar is the intact mesh except each CrackedEvery-th (cracked) and each BrokenEvery-th (broken). 0 disables. */
	UPROPERTY(EditAnywhere, Category = "Art|Variation", meta = (ClampMin = "0"))
	int32 CrackedEvery = 3;

	UPROPERTY(EditAnywhere, Category = "Art|Variation", meta = (ClampMin = "0"))
	int32 BrokenEvery = 5;

	/** Every DamagedWallEvery-th wall segment uses the damaged mesh. 0 disables. */
	UPROPERTY(EditAnywhere, Category = "Art|Variation", meta = (ClampMin = "0"))
	int32 DamagedWallEvery = 4;

	/** Pillars. Same footprint as the greybox cylinder ring; the intact mesh enables the art pass for pillars. */
	UPROPERTY(EditAnywhere, Category = "Art|Meshes")
	TObjectPtr<UStaticMesh> PillarIntact;

	UPROPERTY(EditAnywhere, Category = "Art|Meshes")
	TObjectPtr<UStaticMesh> PillarCracked;

	UPROPERTY(EditAnywhere, Category = "Art|Meshes")
	TObjectPtr<UStaticMesh> PillarBroken;

	/** Curved wall segments (one per WallSegmentCount step); the intact mesh enables the art pass for the wall. */
	UPROPERTY(EditAnywhere, Category = "Art|Meshes")
	TObjectPtr<UStaticMesh> WallIntact;

	UPROPERTY(EditAnywhere, Category = "Art|Meshes")
	TObjectPtr<UStaticMesh> WallDamaged;

	/** Placed between the pillars, on a ring at BrazierRingFraction of the arena radius. */
	UPROPERTY(EditAnywhere, Category = "Art|Props")
	TObjectPtr<UStaticMesh> Brazier;

	UPROPERTY(EditAnywhere, Category = "Art|Props", meta = (ClampMin = "0.1", ClampMax = "0.99"))
	float BrazierRingFraction = 0.78f;

	/** Scattered debris without collision, so it never snags a fighter. */
	UPROPERTY(EditAnywhere, Category = "Art|Props")
	TObjectPtr<UStaticMesh> Rubble;

	UPROPERTY(EditAnywhere, Category = "Art|Props", meta = (ClampMin = "0", ClampMax = "200"))
	int32 RubbleCount = 16;

	/** Seed for the rubble scatter (same seed, same arena). */
	UPROPERTY(EditAnywhere, Category = "Art|Props")
	int32 ScatterSeed = 7;

	/** Free-standing gate placed ArchRadiusFraction of the way to the wall at ArchAngleDegrees (180 = west, behind the player start). */
	UPROPERTY(EditAnywhere, Category = "Art|Props")
	TObjectPtr<UStaticMesh> EntranceArch;

	UPROPERTY(EditAnywhere, Category = "Art|Props", meta = (ClampMin = "0.1", ClampMax = "0.99"))
	float ArchRadiusFraction = 0.96f;

	UPROPERTY(EditAnywhere, Category = "Art|Props")
	float ArchAngleDegrees = 180.f;

	/** Materials for the floor disc, pillars, walls and the arch. Empty = keep the mesh's own materials. */
	UPROPERTY(EditAnywhere, Category = "Art|Materials")
	TObjectPtr<UMaterialInterface> FloorMaterial;

	UPROPERTY(EditAnywhere, Category = "Art|Materials")
	TObjectPtr<UMaterialInterface> PillarMaterial;

	UPROPERTY(EditAnywhere, Category = "Art|Materials")
	TObjectPtr<UMaterialInterface> WallMaterial;

	UPROPERTY(EditAnywhere, Category = "Art|Materials")
	TObjectPtr<UMaterialInterface> ArchMaterial;

	UPROPERTY(EditAnywhere, Category = "Art|Materials")
	TObjectPtr<UMaterialInterface> BrazierMaterial;

	UPROPERTY(EditAnywhere, Category = "Art|Materials")
	TObjectPtr<UMaterialInterface> RubbleMaterial;

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

	// Art-pass components. Empty (no mesh) until the properties above are set.
	UPROPERTY(VisibleAnywhere, Category = "Arena")
	TObjectPtr<UInstancedStaticMeshComponent> PillarsCracked;

	UPROPERTY(VisibleAnywhere, Category = "Arena")
	TObjectPtr<UInstancedStaticMeshComponent> PillarsBroken;

	UPROPERTY(VisibleAnywhere, Category = "Arena")
	TObjectPtr<UInstancedStaticMeshComponent> WallsDamaged;

	UPROPERTY(VisibleAnywhere, Category = "Arena")
	TObjectPtr<UInstancedStaticMeshComponent> Braziers;

	UPROPERTY(VisibleAnywhere, Category = "Arena")
	TObjectPtr<UInstancedStaticMeshComponent> Debris;

	UPROPERTY(VisibleAnywhere, Category = "Arena")
	TObjectPtr<UStaticMeshComponent> Arch;

	/** The primitives used when no art mesh is assigned. */
	UPROPERTY(Transient)
	TObjectPtr<UStaticMesh> GreyCylinder;

	UPROPERTY(Transient)
	TObjectPtr<UStaticMesh> GreyCube;
};
