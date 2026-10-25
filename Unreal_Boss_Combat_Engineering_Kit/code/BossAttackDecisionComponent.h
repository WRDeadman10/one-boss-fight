#pragma once
// Utility evaluator example. NOT a complete boss AI. Needs owner, awareness,
// cooldown/history injection and integration with executor and BT.
#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "BossCombatTypes.h"
#include "BossAttackDecisionComponent.generated.h"

class UBossAttackData;

UCLASS(ClassGroup=(Custom), meta=(BlueprintSpawnableComponent))
class UBossAttackDecisionComponent : public UActorComponent
{
    GENERATED_BODY()
public:
    UBossAttackDecisionComponent();

    UFUNCTION(BlueprintCallable, Category="Boss|Decision")
    UBossAttackData* SelectBestAttack(
        const FBossCombatContext& Context,
        const TArray<UBossAttackData*>& AttackPool,
        TArray<FBossDecisionCandidate>& OutTrace) const;

    // Cooldowns belong to authoritative combat state. This map is an example
    // of data required; update it on attack START not on attempted choices.
    UPROPERTY(BlueprintReadWrite, Category="Boss|Decision")
    TMap<FName, float> NextReadyWorldTimeSeconds;

private:
    bool IsEligible(const UBossAttackData* Attack, const FBossCombatContext& Ctx,
                    FString& OutReason) const;
    float Score(const UBossAttackData* Attack, const FBossCombatContext& Ctx) const;
};
