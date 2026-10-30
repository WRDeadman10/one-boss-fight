#pragma once

#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "RPGGreystoneVisualBridgeComponent.generated.h"

class USkeletalMeshComponent;
class AActor;

/**
 * Strategy for weapon bridge arbitration between visual mesh and gameplay traces.
 */
UENUM(BlueprintType)
enum class EGreystoneWeaponBridgeOption : uint8
{
    /** Option A: Re-attach pack weapon actor to Greystone visual socket (affects trace reach/timing). */
    OptionA_ReattachPackWeaponToGreystone UMETA(DisplayName = "Option A: Reattach Pack Weapon"),

    /** Option B: Keep pack weapon on hidden mannequin (gameplay parity), attach visual proxy to Greystone. */
    OptionB_VisualProxyWeaponOnGreystone  UMETA(DisplayName = "Option B: Visual Proxy Weapon")
};

/**
 * Component that attaches and drives the Paragon Greystone visual mesh from
 * the underlying hidden Combat Mannequin gameplay pawn via RetargetPoseFromMesh.
 */
UCLASS(ClassGroup=(Custom), meta=(BlueprintSpawnableComponent))
class ONEBOSSFIGHT_API URPGGreystoneVisualBridgeComponent : public UActorComponent
{
    GENERATED_BODY()

public:
    URPGGreystoneVisualBridgeComponent();

    virtual void BeginPlay() override;
    virtual void EndPlay(const EEndPlayReason::Type EndPlayReason) override;

    /** Explicitly initializes the visual bridge on the target character. */
    UFUNCTION(BlueprintCallable, Category = "VisualBridge")
    bool InitializeBridge(
        EGreystoneWeaponBridgeOption WeaponOption = EGreystoneWeaponBridgeOption::OptionB_VisualProxyWeaponOnGreystone);

    /** Resolves active weapon socket name from the equipped pack weapon or character. */
    UFUNCTION(BlueprintCallable, Category = "VisualBridge")
    FName ResolvePackWeaponSocketName() const;

    /** Returns the instantiated Greystone visual mesh component. */
    UFUNCTION(BlueprintPure, Category = "VisualBridge")
    USkeletalMeshComponent* GetGreystoneMesh() const { return GreystoneMeshComponent; }

    /** Returns the underlying hidden mannequin mesh component. */
    UFUNCTION(BlueprintPure, Category = "VisualBridge")
    USkeletalMeshComponent* GetMannequinMesh() const { return MannequinMeshComponent; }

protected:
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "VisualBridge")
    TObjectPtr<USkeletalMeshComponent> GreystoneMeshComponent;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "VisualBridge")
    TObjectPtr<USkeletalMeshComponent> MannequinMeshComponent;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "VisualBridge")
    EGreystoneWeaponBridgeOption ActiveWeaponOption;

private:
    void ConfigureHiddenMannequin();
    void ApplyWeaponBridge();
};
