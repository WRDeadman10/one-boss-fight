#include "RPGGreystoneVisualBridgeComponent.h"

#include "GameFramework/Character.h"
#include "Components/SkeletalMeshComponent.h"
#include "Components/CapsuleComponent.h"
#include "Engine/SkeletalMesh.h"
#include "UObject/ConstructorHelpers.h"

static const TCHAR* GreystoneMeshPath = TEXT("/Game/ParagonGreystone/Characters/Heroes/Greystone/Meshes/Greystone.Greystone");
static const TCHAR* GreystoneAnimBPPath = TEXT("/Game/OneBossFight/GreystonePack/ABP_Greystone_VisualBridge.ABP_Greystone_VisualBridge_C");

URPGGreystoneVisualBridgeComponent::URPGGreystoneVisualBridgeComponent()
    : GreystoneMeshComponent(nullptr)
    , MannequinMeshComponent(nullptr)
    , ActiveWeaponOption(EGreystoneWeaponBridgeOption::OptionB_VisualProxyWeaponOnGreystone)
{
    PrimaryComponentTick.bCanEverTick = false;
    bWantsInitializeComponent = true;
}

void URPGGreystoneVisualBridgeComponent::BeginPlay()
{
    Super::BeginPlay();
    InitializeBridge(ActiveWeaponOption);
}

void URPGGreystoneVisualBridgeComponent::EndPlay(const EEndPlayReason::Type EndPlayReason)
{
    if (GreystoneMeshComponent)
    {
        GreystoneMeshComponent->DestroyComponent();
        GreystoneMeshComponent = nullptr;
    }
    Super::EndPlay(EndPlayReason);
}

bool URPGGreystoneVisualBridgeComponent::InitializeBridge(EGreystoneWeaponBridgeOption WeaponOption)
{
    ActiveWeaponOption = WeaponOption;

    ACharacter* OwnerChar = Cast<ACharacter>(GetOwner());
    if (!OwnerChar)
    {
        UE_LOG(LogTemp, Warning, TEXT("[GreystoneBridge] Owner is not an ACharacter. Aborting."));
        return false;
    }

    MannequinMeshComponent = OwnerChar->GetMesh();
    if (!MannequinMeshComponent)
    {
        UE_LOG(LogTemp, Warning, TEXT("[GreystoneBridge] Owner character has no skeletal mesh. Aborting."));
        return false;
    }

    // 1. Instantiate Greystone visual skeletal mesh
    if (!GreystoneMeshComponent)
    {
        GreystoneMeshComponent = NewObject<USkeletalMeshComponent>(OwnerChar, TEXT("GreystoneVisualMesh"));
        if (!GreystoneMeshComponent)
        {
            return false;
        }

        GreystoneMeshComponent->SetupAttachment(OwnerChar->GetCapsuleComponent());
        GreystoneMeshComponent->SetRelativeTransform(MannequinMeshComponent->GetRelativeTransform());

        // Load mesh asset
        USkeletalMesh* GreystoneMesh = LoadObject<USkeletalMesh>(nullptr, GreystoneMeshPath);
        if (GreystoneMesh)
        {
            GreystoneMeshComponent->SetSkeletalMesh(GreystoneMesh);
        }

        // Set Anim Instance Class (ABP_Greystone_VisualBridge)
        UClass* AnimBPClass = LoadClass<UAnimInstance>(nullptr, GreystoneAnimBPPath);
        if (AnimBPClass)
        {
            GreystoneMeshComponent->SetAnimInstanceClass(AnimBPClass);
        }

        // 2. Enforce zero-tick latency ordering (ActorComponent.h:1139)
        // Greystone mesh must tick AFTER mannequin mesh to read updated bone transforms
        GreystoneMeshComponent->AddTickPrerequisiteComponent(MannequinMeshComponent);

        GreystoneMeshComponent->RegisterComponent();
    }

    // 3. Configure hidden mannequin
    ConfigureHiddenMannequin();

    // 4. Apply selected weapon bridge strategy
    ApplyWeaponBridge();

    UE_LOG(LogTemp, Log, TEXT("[GreystoneBridge] Successfully initialized Greystone visual bridge on '%s' (WeaponOption=%d)."),
        *OwnerChar->GetName(), static_cast<int32>(ActiveWeaponOption));
    return true;
}

void URPGGreystoneVisualBridgeComponent::ConfigureHiddenMannequin()
{
    if (!MannequinMeshComponent)
    {
        return;
    }

    // SkinnedMeshComponent.h:87 - Bone transforms must refresh continuously while hidden
    MannequinMeshComponent->VisibilityBasedAnimTickOption =
        EVisibilityBasedAnimTickOption::AlwaysTickPoseAndRefreshBones;

    // SceneComponent.h:210 - Invisible to camera
    MannequinMeshComponent->SetHiddenInGame(true);

    // PrimitiveComponent.h - Prevent duplicate overlapping shadows
    MannequinMeshComponent->SetCastShadow(false);
}

FName URPGGreystoneVisualBridgeComponent::ResolvePackWeaponSocketName() const
{
    // Inspect attached children on MannequinMeshComponent to find active weapon
    if (MannequinMeshComponent)
    {
        const TArray<USceneComponent*>& Children = MannequinMeshComponent->GetAttachChildren();
        for (USceneComponent* Child : Children)
        {
            if (Child && Child->GetAttachSocketName() != NAME_None)
            {
                // Found active socket
                return Child->GetAttachSocketName();
            }
        }
    }

    // Fallback: check standard pack weapon socket
    return FName(TEXT("WeaponSocket_R"));
}

void URPGGreystoneVisualBridgeComponent::ApplyWeaponBridge()
{
    FName SocketName = ResolvePackWeaponSocketName();

    if (ActiveWeaponOption == EGreystoneWeaponBridgeOption::OptionA_ReattachPackWeaponToGreystone)
    {
        // Option A: Re-parent weapon actor to Greystone visual socket
        if (MannequinMeshComponent && GreystoneMeshComponent)
        {
            const TArray<USceneComponent*>& Children = MannequinMeshComponent->GetAttachChildren();
            for (USceneComponent* Child : Children)
            {
                if (Child && Child->GetOwner() != GetOwner())
                {
                    // Found weapon actor's root component
                    Child->AttachToComponent(
                        GreystoneMeshComponent,
                        FAttachmentTransformRules::SnapToTargetNotIncludingScale,
                        SocketName);
                    UE_LOG(LogTemp, Log, TEXT("[GreystoneBridge] Option A: Reattached weapon '%s' to Greystone socket '%s'."),
                        *Child->GetOwner()->GetName(), *SocketName.ToString());
                    break;
                }
            }
        }
    }
    else
    {
        // Option B: Pack weapon stays on hidden mannequin to preserve 100% gameplay parity.
        // Implementer may attach a visual-only cosmetic proxy to GreystoneMeshComponent.
        UE_LOG(LogTemp, Log, TEXT("[GreystoneBridge] Option B: Weapon remains attached to hidden mannequin; 100%% gameplay parity preserved."));
    }
}
