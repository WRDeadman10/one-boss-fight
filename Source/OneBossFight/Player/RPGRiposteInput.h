// Copyright One Boss Fight. All Rights Reserved.

#pragma once

#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "UObject/SoftObjectPtr.h"
#include "RPGRiposteInput.generated.h"

class UInputAction;
struct FInputActionInstance;

/**
 * Riposte input for the pack's player (Master Design Freeze 17.4). Listens to the pack's Light Attack action (IA_NormalAttack) next to the pack's own handling and, on every press, asks the stance-broken boss
 * (URPGBossStagger::TryRiposte) whether the press is a valid riposte: boss down, within range, in front of it, player facing it, not used yet. A valid press arms the critical multiplier for the first
 * hit that follows. The pack still plays its normal attack for the press (a stand-in for the synchronized execution clip, which needs the paired animation from the art list, A-11).
 * Attached to the pack player by RPGPlayerMovesSubsystem.
 */
UCLASS(ClassGroup = (Player))
class ONEBOSSFIGHT_API URPGRiposteInput : public UActorComponent
{
	GENERATED_BODY()

public:
	URPGRiposteInput();

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Riposte")
	TSoftObjectPtr<UInputAction> LightAttackAction;

	UFUNCTION(BlueprintPure, Category = "Riposte")
	int32 GetPressCount() const { return PressCount; }

	UFUNCTION(BlueprintPure, Category = "Riposte")
	int32 GetAcceptedCount() const { return AcceptedCount; }

protected:
	virtual void BeginPlay() override;
	virtual void TickComponent(float DeltaTime, ELevelTick TickType, FActorComponentTickFunction* ThisTickFunction) override;

private:
	bool TryBind();
	void OnLightAttack(const FInputActionInstance& Instance);

	bool bBound = false;
	int32 PressCount = 0;
	int32 AcceptedCount = 0;
};
