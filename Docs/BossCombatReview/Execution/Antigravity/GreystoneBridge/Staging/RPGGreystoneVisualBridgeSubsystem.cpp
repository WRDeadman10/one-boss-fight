#include "RPGGreystoneVisualBridgeSubsystem.h"

#include "RPGGreystoneVisualBridgeComponent.h"
#include "Engine/World.h"
#include "GameFramework/PlayerController.h"
#include "GameFramework/Pawn.h"

bool URPGGreystoneVisualBridgeSubsystem::ShouldCreateSubsystem(UObject* Outer) const
{
    UWorld* World = Cast<UWorld>(Outer);
    if (!World)
    {
        return false;
    }

    // Only instantiate in Game or PIE worlds (skip editor preview worlds)
    return World->IsGameWorld();
}

void URPGGreystoneVisualBridgeSubsystem::OnWorldBeginPlay(UWorld& InWorld)
{
    Super::OnWorldBeginPlay(InWorld);

    // Auto-inject on player 0 pawn if available at world start
    if (APlayerController* PC = InWorld.GetFirstPlayerController())
    {
        if (APawn* Pawn = PC->GetPawn())
        {
            InjectBridge(Pawn);
        }
    }
}

URPGGreystoneVisualBridgeComponent* URPGGreystoneVisualBridgeSubsystem::InjectBridge(APawn* TargetPawn)
{
    if (!TargetPawn)
    {
        return nullptr;
    }

    // Check if bridge is already installed
    URPGGreystoneVisualBridgeComponent* Existing = TargetPawn->FindComponentByClass<URPGGreystoneVisualBridgeComponent>();
    if (Existing)
    {
        return Existing;
    }

    URPGGreystoneVisualBridgeComponent* BridgeComp = NewObject<URPGGreystoneVisualBridgeComponent>(TargetPawn, TEXT("GreystoneVisualBridge"));
    if (!BridgeComp)
    {
        return nullptr;
    }

    BridgeComp->RegisterComponent();
    return BridgeComp;
}

void URPGGreystoneVisualBridgeSubsystem::RemoveBridge(APawn* TargetPawn)
{
    if (!TargetPawn)
    {
        return;
    }

    if (URPGGreystoneVisualBridgeComponent* BridgeComp = TargetPawn->FindComponentByClass<URPGGreystoneVisualBridgeComponent>())
    {
        BridgeComp->DestroyComponent();
    }
}
