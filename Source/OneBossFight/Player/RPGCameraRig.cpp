// Copyright One Boss Fight. All Rights Reserved.

#include "Player/RPGCameraRig.h"
#include "Camera/CameraComponent.h"
#include "Camera/PlayerCameraManager.h"
#include "Components/CapsuleComponent.h"
#include "DrawDebugHelpers.h"
#include "Engine/World.h"
#include "GameFramework/Character.h"
#include "GameFramework/PlayerController.h"
#include "GameFramework/SpringArmComponent.h"

DEFINE_LOG_CATEGORY_STATIC(LogRPGCamera, Log, All);

static TAutoConsoleVariable<int32> CVarCameraDebug(TEXT("rpg.CameraDebug"), 0, TEXT("1 draws the camera pivot, the arm, the camera and the clearance below it."), ECVF_Default);

URPGCameraRig::URPGCameraRig()
{
	PrimaryComponentTick.bCanEverTick = true;
	PrimaryComponentTick.TickInterval = 0.f;
	PrimaryComponentTick.TickGroup = TG_PrePhysics; // before the camera is evaluated at the end of the frame, so a clamped pitch is the one that is drawn
}

void URPGCameraRig::BeginPlay()
{
	Super::BeginPlay();
	Apply();
}

void URPGCameraRig::Apply()
{
	ACharacter* Character = Cast<ACharacter>(GetOwner());
	if (!Character)
	{
		return;
	}
	Boom = Character->FindComponentByClass<USpringArmComponent>();
	Camera = Character->FindComponentByClass<UCameraComponent>();
	if (!Boom)
	{
		return;
	}
	if (bAttachBoomToCapsule && Character->GetCapsuleComponent() && Boom->GetAttachParent() != Character->GetCapsuleComponent())
	{
		// The boom sat on the skeletal mesh (97 cm above its origin, the mesh sits 97 cm below the capsule centre): the capsule centre is the same place and does not follow the animation or a ragdoll.
		const FVector PivotWorld = Boom->GetComponentLocation();
		Boom->AttachToComponent(Character->GetCapsuleComponent(), FAttachmentTransformRules::KeepWorldTransform);
		UE_LOG(LogRPGCamera, Log, TEXT("%s: camera boom moved from the mesh to the capsule (pivot stays at %.0f, %.0f, %.0f)"), *Character->GetName(), PivotWorld.X, PivotWorld.Y, PivotWorld.Z);
	}
	Boom->bDoCollisionTest = true;
	Boom->ProbeSize = ProbeSize;
	Boom->ProbeChannel = ProbeChannel;
	Boom->bEnableCameraLag = LagSpeed > 0.f;
	Boom->CameraLagSpeed = LagSpeed;
	Boom->CameraLagMaxDistance = LagMaxDistance;
	ApplyPitchLimits();
	bApplied = true;
	UE_LOG(LogRPGCamera, Log, TEXT("%s: camera rig applied: arm %.0f cm, probe %.0f cm, pitch %.0f to %.0f, lag %.0f (max %.0f cm)"), *Character->GetName(), Boom->TargetArmLength, ProbeSize, PitchMin, PitchMax, LagSpeed, LagMaxDistance);
}

void URPGCameraRig::ApplyPitchLimits() const
{
	const APawn* Pawn = Cast<APawn>(GetOwner());
	APlayerController* Controller = Pawn ? Cast<APlayerController>(Pawn->GetController()) : nullptr;
	if (APlayerCameraManager* Manager = Controller ? Controller->PlayerCameraManager : nullptr)
	{
		// Mouse and stick input is clamped by the camera manager's limits ...
		Manager->ViewPitchMin = PitchMin;
		Manager->ViewPitchMax = PitchMax;
	}
	if (Controller)
	{
		// ... but SetControlRotation (the pack's lock-on, scripted cameras) is not, so the control pitch is clamped here as well.
		FRotator Rotation = Controller->GetControlRotation();
		const float Pitch = FRotator::NormalizeAxis(Rotation.Pitch);
		const float Clamped = FMath::Clamp(Pitch, PitchMin, PitchMax);
		if (!FMath::IsNearlyEqual(Pitch, Clamped, 0.01f))
		{
			Rotation.Pitch = Clamped;
			Controller->SetControlRotation(Rotation);
		}
	}
}

float URPGCameraRig::GetClearanceBelowCamera() const
{
	const UWorld* World = GetWorld();
	if (!World || !Camera)
	{
		return -1.f;
	}
	const FVector Location = Camera->GetComponentLocation();
	FHitResult Hit;
	FCollisionQueryParams Params(SCENE_QUERY_STAT(RPGCameraClearance), false, GetOwner());
	if (World->LineTraceSingleByChannel(Hit, Location + FVector(0.f, 0.f, 300.f), Location - FVector(0.f, 0.f, 1500.f), ProbeChannel, Params))
	{
		return Location.Z - Hit.ImpactPoint.Z;
	}
	return -1.f;
}

void URPGCameraRig::TickComponent(float DeltaTime, ELevelTick TickType, FActorComponentTickFunction* ThisTickFunction)
{
	Super::TickComponent(DeltaTime, TickType, ThisTickFunction);
	if (!bApplied || !Boom)
	{
		Apply(); // the controller may not have existed at BeginPlay
		return;
	}
	if (bAttachBoomToCapsule)
	{
		// The pack's death and ragdoll logic attaches the boom to the mesh again (the mesh then falls to the floor with the body, and the camera with it): put it back on the capsule centre.
		const ACharacter* Character = Cast<ACharacter>(GetOwner());
		UCapsuleComponent* Capsule = Character ? Character->GetCapsuleComponent() : nullptr;
		if (Capsule && Boom->GetAttachParent() != Capsule)
		{
			Boom->AttachToComponent(Capsule, FAttachmentTransformRules::SnapToTargetNotIncludingScale);
			Boom->SetRelativeLocation(FVector::ZeroVector);
			UE_LOG(LogRPGCamera, Log, TEXT("%s: camera boom was attached to another component again, moved back to the capsule"), *GetOwner()->GetName());
		}
	}
	if (!Boom->bDoCollisionTest)
	{
		// The pack's death logic switches the arm's collision test off (the camera then goes wherever the pitch sends it, under the floor included). Keep it on.
		Boom->bDoCollisionTest = true;
	}
	if (Boom->ProbeSize != ProbeSize)
	{
		Boom->ProbeSize = ProbeSize;
	}
	ApplyPitchLimits(); // a controller change (respawn) brings a new camera manager state; this is a few assignments
#if !UE_BUILD_SHIPPING
	if (CVarCameraDebug.GetValueOnGameThread() > 0 && Camera)
	{
		const UWorld* World = GetWorld();
		const FVector Pivot = Boom->GetComponentLocation();
		const FVector Eye = Camera->GetComponentLocation();
		DrawDebugSphere(World, Pivot, 8.f, 8, FColor::Yellow, false, -1.f);
		DrawDebugLine(World, Pivot, Eye, FColor::Cyan, false, -1.f, 0, 1.5f);
		DrawDebugSphere(World, Eye, ProbeSize, 12, FColor::Green, false, -1.f);
		const float Clearance = GetClearanceBelowCamera();
		if (Clearance >= 0.f)
		{
			DrawDebugLine(World, Eye, Eye - FVector(0.f, 0.f, Clearance), Clearance < ProbeSize ? FColor::Red : FColor::White, false, -1.f, 0, 1.f);
		}
	}
#endif
}
