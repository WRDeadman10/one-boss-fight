// Copyright One Boss Fight. All Rights Reserved.

#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "RPGEmberField.generated.h"

class UInstancedStaticMeshComponent;
class UMaterialInterface;
class UStaticMesh;

/**
 * Glowing embers that rise from the braziers and drift across the arena on a light wind, plus a few motes of ash floating in the open.
 * One instanced mesh (a tiny emissive sphere), moved on the CPU every frame; each ember swells, glows and fades over its life, then respawns.
 * Ticks in the editor viewport too, so a screenshot shows them in motion. Filled by Scripts/Editor/dress_arena.py.
 */
UCLASS()
class ONEBOSSFIGHT_API ARPGEmberField : public AActor
{
	GENERATED_BODY()

public:
	ARPGEmberField();

	virtual void OnConstruction(const FTransform& Transform) override;
	virtual void Tick(float DeltaSeconds) override;
	virtual bool ShouldTickIfViewportsOnly() const override { return true; }

	UFUNCTION(BlueprintCallable, CallInEditor, Category = "Editor")
	void Rebuild();

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Embers")
	TObjectPtr<UStaticMesh> Mesh;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Embers")
	TObjectPtr<UMaterialInterface> Material;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Embers", meta = (ClampMin = "1", ClampMax = "2000"))
	int32 Count = 180;

	/** Where fires burn (actor-local, floor level of the flame). Most embers are born here. */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Embers")
	TArray<FVector> FireSources;

	/** Share of the embers that rise from a fire; the rest float as ash across the arena. */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Embers", meta = (ClampMin = "0", ClampMax = "1"))
	float FireShare = 0.8f;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Embers")
	float ArenaRadius = 2900.f;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Embers")
	float RiseSpeedMin = 70.f;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Embers")
	float RiseSpeedMax = 190.f;

	/** Steady wind, cm/s (x, y). */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Embers")
	FVector2D Wind = FVector2D(70.f, 30.f);

	/** Sideways wobble, cm/s. */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Embers")
	float Sway = 55.f;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Embers")
	float LifeMin = 4.f;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Embers")
	float LifeMax = 9.f;

	/** Ember diameter in cm at full size. */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Embers")
	float SizeMin = 1.2f;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Embers")
	float SizeMax = 3.2f;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Embers")
	int32 Seed = 3;

	UFUNCTION(BlueprintPure, Category = "Embers")
	int32 GetAliveCount() const { return Embers.Num(); }

private:
	struct FEmber
	{
		FVector Position = FVector::ZeroVector;
		float RiseSpeed = 100.f;
		float Age = 0.f;
		float Life = 5.f;
		float Size = 2.f;
		float Phase = 0.f;
		float Frequency = 1.f;
	};

	UPROPERTY(Transient)
	TObjectPtr<UInstancedStaticMeshComponent> Instances;

	TArray<FEmber> Embers;
	FRandomStream Random;
	float Clock = 0.f;

	void Respawn(FEmber& Ember, bool bRandomAge);
};
