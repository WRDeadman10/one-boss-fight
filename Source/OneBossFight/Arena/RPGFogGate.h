// Copyright One Boss Fight. All Rights Reserved.

#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "RPGFogGate.generated.h"

class UBoxComponent;
class UInstancedStaticMeshComponent;
class UMaterialInterface;
class UStaticMesh;

/**
 * The fog gate across the arena doorway (the fog doors of the genre). It follows the boss encounter by itself:
 *   Idle    the boss sleeps or is reset: a thin mist (IdleAmount), the doorway is open;
 *   Closed  the boss is awake and alive: the mist thickens to full (FadeSeconds) and a collision box blocks the doorway, so the fight cannot be left;
 *   Cleared the boss is dead: the mist dissolves (FadeSeconds) and the doorway opens for good.
 * The state is read from the boss every 0.2 s (URPGBossEncounter dormant flag and the health attribute), not from events, so a missed event cannot leave the gate stuck.
 * The mist is a set of instanced fog cards (the sample's fog card mesh and gate material) that grow from nothing to full size, no material parameter needed.
 * In the editor viewport the gate shows closed so it can be seen; Rebuild builds the cards from the properties.
 */
UCLASS()
class ONEBOSSFIGHT_API ARPGFogGate : public AActor
{
	GENERATED_BODY()

public:
	ARPGFogGate();

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Gate")
	TObjectPtr<UStaticMesh> CardMesh;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Gate")
	TObjectPtr<UMaterialInterface> CardMaterial;

	/** Cards across the doorway (along the actor's local Y) and rows of three heights. */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Gate", meta = (ClampMin = "1"))
	int32 CardCount = 7;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Gate")
	float CardSpacing = 230.f;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Gate")
	float CardScale = 11.f;

	/** Half size of the blocking box (cm): thin along the walking direction, wide across the doorway, tall. */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Gate")
	FVector BlockerHalfExtent = FVector(30.f, 900.f, 400.f);

	/** Size of the mist while the boss sleeps (0 to 1 of the full size). */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Gate", meta = (ClampMin = "0.0", ClampMax = "1.0"))
	float IdleAmount = 0.35f;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Gate", meta = (ClampMin = "0.1"))
	float FadeSeconds = 1.5f;

	/** "Idle", "Closed" or "Cleared". */
	UFUNCTION(BlueprintPure, Category = "Gate")
	FString GetStateName() const;

	/** Current size of the mist (0 to 1) and whether the doorway is blocked right now. */
	UFUNCTION(BlueprintPure, Category = "Gate")
	float GetAmount() const { return Amount; }

	UFUNCTION(BlueprintPure, Category = "Gate")
	bool IsBlocking() const;

	/** Builds the cards from the properties (the editor calls it from the details panel). */
	UFUNCTION(BlueprintCallable, CallInEditor, Category = "Gate")
	void Rebuild();

protected:
	virtual void OnConstruction(const FTransform& Transform) override;
	virtual void BeginPlay() override;
	virtual void Tick(float DeltaSeconds) override;

private:
	enum class EState : uint8 { Idle, Closed, Cleared };

	EState ReadBossState();
	void ApplyAmount();

	UPROPERTY(VisibleAnywhere, Category = "Gate")
	TObjectPtr<UBoxComponent> Blocker;

	UPROPERTY(VisibleAnywhere, Category = "Gate")
	TObjectPtr<UInstancedStaticMeshComponent> Cards;

	EState State = EState::Idle;
	float Amount = 1.f;
	double NextRead = 0.0;
	bool bCleared = false;
	bool bSeenAlive = false;
};
