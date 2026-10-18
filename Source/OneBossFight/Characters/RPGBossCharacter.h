// Copyright One Boss Fight. All Rights Reserved.

#pragma once

#include "CoreMinimal.h"
#include "Characters/RPGCharacterBase.h"
#include "RPGBossCharacter.generated.h"

class URPGBossCombatComponent;
class URPGBossStateTreeComponent;

/**
 * The boss. Shares attributes, damage and combat state with the player through ARPGCharacterBase; the boss
 * component adds attack selection, phases and the dormant/entrance/combat/dead flow. Registers itself with
 * the encounter subsystem, which engages and resets it.
 */
UCLASS()
class ONEBOSSFIGHT_API ARPGBossCharacter : public ARPGCharacterBase
{
	GENERATED_BODY()

public:
	ARPGBossCharacter();

	URPGBossCombatComponent* GetBossCombat() const { return BossCombat; }
	URPGBossStateTreeComponent* GetStateTreeComponent() const { return StateTreeComponent; }

	/** Shown on the boss health bar. */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Boss")
	FText BossName;

	/** Where the boss stands when the encounter is reset. Captured at BeginPlay. */
	const FTransform& GetHomeTransform() const { return HomeTransform; }
	void SetHomeTransform(const FTransform& NewHome) { HomeTransform = NewHome; }

	/** Full reset: health, combat, phase, AI state, position. */
	virtual void ResetCombatant() override;

protected:
	virtual void BeginPlay() override;

private:
	UPROPERTY(VisibleAnywhere, Category = "Boss")
	TObjectPtr<URPGBossCombatComponent> BossCombat;

	/** Runs the boss StateTree that mirrors the boss states. */
	UPROPERTY(VisibleAnywhere, Category = "Boss")
	TObjectPtr<URPGBossStateTreeComponent> StateTreeComponent;

	FTransform HomeTransform;
};
