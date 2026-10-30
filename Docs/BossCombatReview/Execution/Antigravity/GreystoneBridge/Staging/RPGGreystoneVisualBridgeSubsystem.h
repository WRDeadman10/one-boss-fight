#pragma once

#include "CoreMinimal.h"
#include "Subsystems/WorldSubsystem.h"
#include "RPGGreystoneVisualBridgeSubsystem.generated.h"

class URPGGreystoneVisualBridgeComponent;
class APawn;

/**
 * World subsystem responsible for runtime injection of the Greystone visual bridge
 * onto the player pawn at world start without modifying project Blueprints or level assets.
 */
UCLASS()
class ONEBOSSFIGHT_API URPGGreystoneVisualBridgeSubsystem : public UWorldSubsystem
{
    GENERATED_BODY()

public:
    virtual bool ShouldCreateSubsystem(UObject* Outer) const override;
    virtual void OnWorldBeginPlay(UWorld& InWorld) override;

    /** Injects the visual bridge component onto the specified pawn. */
    UFUNCTION(BlueprintCallable, Category = "VisualBridge")
    URPGGreystoneVisualBridgeComponent* InjectBridge(APawn* TargetPawn);

    /** Removes the visual bridge from the target pawn. */
    UFUNCTION(BlueprintCallable, Category = "VisualBridge")
    void RemoveBridge(APawn* TargetPawn);
};
