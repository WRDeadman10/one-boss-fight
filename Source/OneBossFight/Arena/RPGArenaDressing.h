// Copyright One Boss Fight. All Rights Reserved.

#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "RPGArenaDressing.generated.h"

class UInstancedStaticMeshComponent;
class UMaterialInterface;
class UStaticMesh;

/** One mesh and every place it stands (actor-local transforms). */
USTRUCT(BlueprintType)
struct ONEBOSSFIGHT_API FRPGDressingSet
{
	GENERATED_BODY()

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Dressing")
	TObjectPtr<UStaticMesh> Mesh;

	/** Replaces the mesh's own material in slot 0 when set. */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Dressing")
	TObjectPtr<UMaterialInterface> MaterialOverride;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Dressing")
	TArray<FTransform> Instances;

	/** Props the fighters can bump into. Off for rubble and anything small. */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Dressing")
	bool bCollision = false;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Dressing")
	bool bCastShadow = true;

	/** Swings every instance about its mesh-local Y axis through this pivot, a few degrees back and forth in the wind (banners, chains). 0 = static. */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Dressing")
	float SwayDegrees = 0.f;

	/** Hanging point in mesh space (before instance scale), cm. */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Dressing")
	FVector SwayPivot = FVector::ZeroVector;
};

/**
 * Decoration layer for the arena: ruin walls, columns, rubble, props and set dressing as instanced static meshes.
 * It never owns collision that gameplay depends on (the greybox arena keeps that), unless a set asks for it.
 * The editor script Scripts/Editor/dress_arena.py fills Sets; the components are rebuilt on every construction.
 */
UCLASS()
class ONEBOSSFIGHT_API ARPGArenaDressing : public AActor
{
	GENERATED_BODY()

public:
	ARPGArenaDressing();

	virtual void OnConstruction(const FTransform& Transform) override;
	virtual void Tick(float DeltaSeconds) override;
	virtual bool ShouldTickIfViewportsOnly() const override { return true; }

	/** Runs the construction again after the editor scripts changed properties (Python cannot call RerunConstructionScripts). */
	UFUNCTION(BlueprintCallable, CallInEditor, Category = "Editor")
	void Rebuild();

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Dressing")
	TArray<FRPGDressingSet> Sets;

	/** Total instance count over all sets (for logs and tests). */
	UFUNCTION(BlueprintCallable, Category = "Dressing")
	int32 GetInstanceCount() const;

private:
	UPROPERTY(Transient)
	TArray<TObjectPtr<UInstancedStaticMeshComponent>> Built;

	/** Sets that sway: the component, its resting transforms and the swing. */
	struct FSwaying
	{
		TObjectPtr<UInstancedStaticMeshComponent> Component;
		TArray<FTransform> Rest;
		float Degrees = 0.f;
		FVector Pivot = FVector::ZeroVector;
	};
	TArray<FSwaying> Swaying;
	float Clock = 0.f;
};
