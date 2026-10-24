// Copyright One Boss Fight. All Rights Reserved.

#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "RPGFlipbookEffect.generated.h"

class UMaterialInterface;
class UMaterialInstanceDynamic;
class UStaticMeshComponent;
class UWorld;

UENUM()
enum class ERPGEFlipbookKind : uint8
{
	BloodBurst,
	HitSpark,
	DodgeDust
};

namespace RPGFlipbookRules
{
	struct FSample
	{
		int32 Frame = 0;
		bool bFinished = false;
	};

	/** Samples the 8 by 8, row-major sheet. The terminal sample is frame 63. */
	inline FSample Sample(float Elapsed, float Duration)
	{
		if (Duration <= KINDA_SMALL_NUMBER)
		{
			return { 63, true };
		}
		const float Progress = FMath::Clamp(Elapsed / FMath::Max(Duration, KINDA_SMALL_NUMBER), 0.f, 1.f);
		return { FMath::Clamp(FMath::FloorToInt(Progress * 63.f), 0, 63), Elapsed >= Duration };
	}
}

/** A short-lived camera-facing plane for the authored 8 by 8 combat effect sheets. */
UCLASS(NotBlueprintable)
class ONEBOSSFIGHT_API ARPGFlipbookEffect : public AActor
{
	GENERATED_BODY()

public:
	ARPGFlipbookEffect();

	/** Loads one of the three authored instances. Call during the owning combat component's BeginPlay, not at the hit frame. */
	static UMaterialInterface* LoadMaterial(ERPGEFlipbookKind Kind);
	/** Spawns and starts one effect. A missing material deliberately produces no actor. */
	static ARPGFlipbookEffect* Spawn(UWorld* World, const FVector& Location, ERPGEFlipbookKind Kind, UMaterialInterface* Material);

	virtual void Tick(float DeltaSeconds) override;

	UFUNCTION(BlueprintPure, Category = "Flipbook")
	FString GetEffectName() const;

	UFUNCTION(BlueprintPure, Category = "Flipbook")
	int32 GetFrameIndex() const { return FrameIndex; }

	UFUNCTION(BlueprintPure, Category = "Flipbook")
	float GetPlaybackSeconds() const { return PlaybackSeconds; }

private:
	void Initialize(ERPGEFlipbookKind InKind, UMaterialInterface* Material);

	UPROPERTY()
	TObjectPtr<UStaticMeshComponent> Plane;

	UPROPERTY(Transient)
	TObjectPtr<UMaterialInstanceDynamic> DynamicMaterial;

	ERPGEFlipbookKind EffectKind = ERPGEFlipbookKind::BloodBurst;
	float PlaybackSeconds = 0.6f;
	float Elapsed = 0.f;
	int32 FrameIndex = 0;
	bool bFinishing = false;
};
