// Copyright One Boss Fight. All Rights Reserved.

#pragma once

#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "UObject/SoftObjectPtr.h"
#include "RPGBossLook.generated.h"

class USkeletalMesh;
class USkeletalMeshComponent;
class UStaticMesh;
class UStaticMeshComponent;

/**
 * The boss's final look (G2-15): Antigravity's body (SK_Boss01_Body) with the crown, the mantle, the brazier gauntlet and the hero greatsword in its hand. The pack boss mesh stays what drives the fight (animation, montages, physics asset,
 * collision, the pack's weapon trace sockets, the ragdoll) and only stops being drawn; the new body and its pieces are skeletal mesh components attached to it that follow its pose (leader pose component, same bone names), so "the same fight plays"
 * with another face. The greatsword is a static mesh attached to the body's configured bone/socket with a per-boss relative offset. The followers inherit the pack mesh's scale.
 * Attached to the pack boss by RPGPlayerMovesSubsystem; off with bEnabled or SetEnabledForTest(false) (the pack mesh is shown again, the pieces are destroyed).
 */
UCLASS(ClassGroup = (Boss))
class ONEBOSSFIGHT_API URPGBossLook : public UActorComponent
{
	GENERATED_BODY()

public:
	URPGBossLook();

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Look")
	bool bEnabled = true;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Look")
	TSoftObjectPtr<USkeletalMesh> Body;

	/** Crown, mantle and gauntlet: skeletal pieces on the same skeleton that follow the pack mesh's pose. */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Look")
	TArray<TSoftObjectPtr<USkeletalMesh>> Pieces;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Look")
	TSoftObjectPtr<UStaticMesh> Sword;

	/** A bone or socket name on the body mesh. */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Look")
	FName SwordSocket = TEXT("hand_r");

	/** Optional per-boss sword pose relative to SwordSocket; identity preserves the pre-offset attachment behavior. */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Look")
	FTransform SwordAttachOffset = FTransform(FRotator(19.84f, -1.84f, -10.48f), FVector::ZeroVector);

	UFUNCTION(BlueprintPure, Category = "Look")
	bool IsApplied() const { return bApplied; }

	/** Pieces applied (the body not counted) and the sword's component, for tests. */
	UFUNCTION(BlueprintPure, Category = "Look")
	int32 GetPieceCount() const { return PieceCount; }

	UFUNCTION(BlueprintPure, Category = "Look")
	UStaticMeshComponent* GetSwordComponent() const { return SwordComponent; }

	UFUNCTION(BlueprintPure, Category = "Look")
	USkeletalMeshComponent* GetBodyComponent() const { return BodyComponent; }

	/** How many of the pack's own weapon meshes (the static mesh "Weapon Mesh", SM_KwangSword, a child of the pack mesh) the look has hidden; tests. */
	UFUNCTION(BlueprintPure, Category = "Look")
	int32 GetHiddenPackWeaponCount() const { return HiddenPackWeapons.Num(); }

	/** Test drivers only (Python must not change a component property in PIE: KI-083): switches the look on or off now. */
	UFUNCTION(BlueprintCallable, Category = "Look")
	void SetEnabledForTest(bool bOn);

	/** Draws the pack mesh again and destroys the body, the pieces and the sword. Safe to call twice. */
	void Revert();

protected:
	virtual void BeginPlay() override;
	virtual void EndPlay(const EEndPlayReason::Type EndPlayReason) override;
	virtual void TickComponent(float DeltaTime, ELevelTick TickType, FActorComponentTickFunction* ThisTickFunction) override;

private:
	/** Builds the look; idempotent. Runs one frame after BeginPlay (the pack's Blueprint sets its mesh at the start). */
	void Apply();
	/** Reassert hidden render state after the pack's equip/wake Blueprint shows its child weapon. */
	void HidePackWeapons();

	bool bApplied = false;
	int32 PieceCount = 0;
	bool bSavedHidden = false;
	uint8 SavedTickOption = 0;

	UPROPERTY(Transient)
	TObjectPtr<USkeletalMeshComponent> BodyComponent;

	UPROPERTY(Transient)
	TObjectPtr<UStaticMeshComponent> SwordComponent;

	UPROPERTY(Transient)
	TArray<TObjectPtr<USkeletalMeshComponent>> PieceComponents;

	/** The pack's own weapon meshes the look hid, and whether each one was already hidden before (restored by Revert). */
	UPROPERTY(Transient)
	TArray<TObjectPtr<UStaticMeshComponent>> HiddenPackWeapons;

	TArray<bool> PackWeaponWasHidden;
	TArray<bool> PackWeaponWasVisible;
};
