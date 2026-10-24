// Copyright One Boss Fight. All Rights Reserved.

#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "RPGBossRemains.generated.h"

class UMaterialInstanceDynamic;
class UMaterialInterface;
class UNiagaraSystem;
class UStaticMesh;
class UStaticMeshComponent;
class UWorld;

namespace RPGBossRemainsRules
{
	struct FSample
	{
		float Dissolve = 0.f;
		bool bFinished = false;
	};

	inline FSample Sample(float ElapsedSeconds, float FormSeconds)
	{
		const float SafeDuration = FMath::Max(FormSeconds, KINDA_SMALL_NUMBER);
		const float Dissolve = FMath::Clamp(ElapsedSeconds / SafeDuration, 0.f, 1.f);
		return { Dissolve, Dissolve >= 1.f };
	}
}

/** Persistent statue that replaces a confirmed dead boss after the pack destroys its actor. */
UCLASS(NotBlueprintable)
class ONEBOSSFIGHT_API ARPGBossRemains : public AActor
{
	GENERATED_BODY()

public:
	ARPGBossRemains();

	static void PreloadAssets(UStaticMesh*& OutMesh, UMaterialInterface*& OutMaterial, UNiagaraSystem*& OutBurst);
	static ARPGBossRemains* Spawn(UWorld* World, const FTransform& Transform, UStaticMesh* InMesh, UMaterialInterface* InMaterial, UNiagaraSystem* InBurst);
	static void DestroyForWorld(UWorld* World);

	UFUNCTION(BlueprintPure, Category = "Remains")
	float GetDissolve() const { return Dissolve; }

	UFUNCTION(BlueprintPure, Category = "Remains")
	int32 GetSlotCount() const { return SlotCount; }

	UFUNCTION(BlueprintPure, Category = "Remains")
	bool IsFullyFormed() const { return bFinished; }

	virtual void Tick(float DeltaSeconds) override;

private:
	void Initialize(UStaticMesh* InMesh, UMaterialInterface* InMaterial, UNiagaraSystem* InBurst);
	void ApplyMaterials();
	void ApplyDissolve(float Value);
	static float GetFormSeconds();

	UPROPERTY(VisibleAnywhere)
	TObjectPtr<UStaticMeshComponent> Mesh;

	UPROPERTY(Transient)
	TObjectPtr<UStaticMesh> LoadedMesh;

	UPROPERTY(Transient)
	TObjectPtr<UMaterialInterface> LoadedMaterial;

	UPROPERTY(Transient)
	TObjectPtr<UNiagaraSystem> LoadedBurst;

	UPROPERTY(Transient)
	TArray<TObjectPtr<UMaterialInstanceDynamic>> Materials;

	float Elapsed = 0.f;
	float Dissolve = 0.f;
	int32 SlotCount = 0;
	bool bFinished = false;
};
