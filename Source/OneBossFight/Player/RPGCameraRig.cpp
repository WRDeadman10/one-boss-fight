// Copyright One Boss Fight. All Rights Reserved.

#include "Player/RPGCameraRig.h"
#include "Camera/CameraComponent.h"
#include "Camera/PlayerCameraManager.h"
#include "Components/CapsuleComponent.h"
#include "Components/PrimitiveComponent.h"
#include "Components/SkeletalMeshComponent.h"
#include "Components/StaticMeshComponent.h"
#include "DrawDebugHelpers.h"
#include "Engine/World.h"
#include "EngineUtils.h"
#include "EnhancedPlayerInput.h"
#include "GameFramework/Character.h"
#include "GameFramework/PlayerController.h"
#include "GameFramework/SpringArmComponent.h"
#include "InputAction.h"
#include "Player/RPGPlayerMovesSubsystem.h"

DEFINE_LOG_CATEGORY_STATIC(LogRPGCamera, Log, All);

static TAutoConsoleVariable<int32> CVarCameraDebug(TEXT("rpg.CameraDebug"), 0, TEXT("1 draws the camera pivot, the arm, the camera and the clearance below it."), ECVF_Default);

#if !UE_BUILD_SHIPPING
static TAutoConsoleVariable<int32> CVarCameraBossBlocks(TEXT("rpg.Camera.BossBlocks"), 0,
	TEXT("Development camera experiment: 1 makes the live pack boss capsule block ECC_Camera; 0 restores its authored response."), ECVF_Default);
static TAutoConsoleVariable<int32> CVarCameraHideBossInside(TEXT("rpg.Camera.HideBossInside"), 0,
	TEXT("Development camera experiment: 1 hides boss mesh primitives only for the local player camera while inside the boss capsule."), ECVF_Default);
static TAutoConsoleVariable<int32> CVarCameraLockOnFraming(TEXT("rpg.Camera.LockOnFraming"), 0,
	TEXT("Development camera experiment: 1 gently frames the pack boss in front while preserving manual camera input."), ECVF_Default);
#endif

namespace
{
	constexpr float CameraHideEnterMarginCm = 5.f;
	constexpr float CameraHideExitMarginCm = 10.f;
	constexpr float CameraHideMinimumSeconds = 0.35f;
	constexpr float LockOnManualInputGraceSeconds = 0.35f;
	constexpr float LockOnLookInputDeadzone = 0.25f;
	constexpr float LockOnYawMinimumDegreesPerSecond = 60.f;
	constexpr float LockOnYawDegreesPerSecondPerDegreeError = 6.f;
	constexpr float LockOnYawMaximumDegreesPerSecond = 360.f;

	bool IsFiniteCameraBounds(const FVector& Origin, const FVector& Extent)
	{
		return FMath::IsFinite(Origin.X) && FMath::IsFinite(Origin.Y) && FMath::IsFinite(Origin.Z)
			&& FMath::IsFinite(Extent.X) && FMath::IsFinite(Extent.Y) && FMath::IsFinite(Extent.Z)
			&& Extent.X >= 0.f && Extent.Y >= 0.f && Extent.Z >= 0.f;
	}

	bool IsPointWithinCameraCapsule(const FVector& Point, const FVector& Center, const FVector& Up,
		float Radius, float HalfHeight, float MarginCm)
	{
		const float EffectiveRadius = Radius + MarginCm;
		const float SegmentHalfLength = FMath::Max(0.f, HalfHeight - Radius);
		if (!FMath::IsFinite(EffectiveRadius) || !FMath::IsFinite(SegmentHalfLength) || EffectiveRadius <= 0.f)
		{
			return false;
		}
		const FVector SegmentStart = Center - Up * SegmentHalfLength;
		const FVector SegmentEnd = Center + Up * SegmentHalfLength;
		const FVector ClosestPoint = FMath::ClosestPointOnSegment(Point, SegmentStart, SegmentEnd);
		return FVector::DistSquared(Point, ClosestPoint) <= FMath::Square(EffectiveRadius);
	}
}

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

void URPGCameraRig::EndPlay(const EEndPlayReason::Type EndPlayReason)
{
	RestoreBossCameraCollisionOption();
	RestoreBossHideInsideOption();
	RestoreLockOnFramingOption();
	Super::EndPlay(EndPlayReason);
}

void URPGCameraRig::ApplyBossCameraCollisionOption()
{
#if !UE_BUILD_SHIPPING
	const bool bEnabled = CVarCameraBossBlocks.GetValueOnGameThread() != 0;
	if (!bEnabled)
	{
		RestoreBossCameraCollisionOption();
		return;
	}

	UWorld* World = GetWorld();
	if (!World)
	{
		RestoreBossCameraCollisionOption();
		return;
	}

	// Re-resolve while the experiment is enabled so a still-live old boss cannot
	// remain cached across encounter replacement or a reset that respawns it.
	UCapsuleComponent* Capsule = nullptr;
	for (TActorIterator<APawn> It(World); It; ++It)
	{
		if (URPGPlayerMovesSubsystem::IsPackBoss(*It))
		{
			if (ACharacter* PackBoss = Cast<ACharacter>(*It))
			{
				Capsule = PackBoss->GetCapsuleComponent();
				if (Capsule)
				{
					break;
				}
			}
		}
	}
	if (!Capsule)
	{
		RestoreBossCameraCollisionOption();
		return;
	}

	if (BossCameraCapsule.Get() != Capsule)
	{
		RestoreBossCameraCollisionOption();
		BossCameraCapsule = Capsule;
		OriginalBossCameraResponse = Capsule->GetCollisionResponseToChannel(ECC_Camera);
		bHasOriginalBossCameraResponse = true;
		if (AActor* BossOwner = Capsule->GetOwner())
		{
			UE_LOG(LogRPGCamera, Log, TEXT("BossBlocks enabled for %s (authored ECC_Camera response=%d)"),
				*BossOwner->GetName(), static_cast<int32>(OriginalBossCameraResponse.GetValue()));
		}
	}

	if (Capsule->GetCollisionResponseToChannel(ECC_Camera) != ECR_Block)
	{
		Capsule->SetCollisionResponseToChannel(ECC_Camera, ECR_Block);
	}
#endif
}

void URPGCameraRig::RestoreBossCameraCollisionOption()
{
	if (bHasOriginalBossCameraResponse)
	{
		if (UCapsuleComponent* Capsule = BossCameraCapsule.Get())
		{
			if (Capsule->GetCollisionResponseToChannel(ECC_Camera) == ECR_Block)
			{
				Capsule->SetCollisionResponseToChannel(ECC_Camera, OriginalBossCameraResponse);
				if (AActor* BossOwner = Capsule->GetOwner())
				{
					UE_LOG(LogRPGCamera, Log, TEXT("BossBlocks restored %s ECC_Camera response=%d"),
						*BossOwner->GetName(), static_cast<int32>(OriginalBossCameraResponse.GetValue()));
				}
			}
		}
	}
	BossCameraCapsule.Reset();
	bHasOriginalBossCameraResponse = false;
}

void URPGCameraRig::ApplyBossHideInsideOption()
{
#if !UE_BUILD_SHIPPING
	const bool bEnabled = CVarCameraHideBossInside.GetValueOnGameThread() != 0;
	if (!bEnabled)
	{
		RestoreBossHideInsideOption();
		return;
	}

	ACharacter* Player = Cast<ACharacter>(GetOwner());
	APlayerController* PlayerController = Player ? Cast<APlayerController>(Player->GetController()) : nullptr;
	UWorld* World = GetWorld();
	if (!PlayerController || !PlayerController->IsLocalController() || !World || !Camera)
	{
		RestoreBossHideInsideOption();
		return;
	}

	ACharacter* PackBoss = nullptr;
	for (TActorIterator<APawn> It(World); It; ++It)
	{
		if (URPGPlayerMovesSubsystem::IsPackBoss(*It))
		{
			PackBoss = Cast<ACharacter>(*It);
			if (PackBoss)
			{
				break;
			}
		}
	}
	if (!PackBoss)
	{
		RestoreBossHideInsideOption();
		return;
	}

	if (BossHideActor.Get() != PackBoss || BossHideController.Get() != PlayerController)
	{
		RestoreBossHideInsideOption();
	}

	const bool bAlreadyHiddenByThisRig = BossHideActor.Get() == PackBoss
		&& BossHideController.Get() == PlayerController && bBossHideActive;
	const float MarginCm = bAlreadyHiddenByThisRig ? CameraHideExitMarginCm : -CameraHideEnterMarginCm;
	const FVector CameraLocation = Camera->GetComponentLocation();
	if (!IsFiniteCameraBounds(CameraLocation, FVector::ZeroVector))
	{
		RestoreBossHideInsideOption();
		return;
	}
	UCapsuleComponent* BossCapsule = PackBoss->GetCapsuleComponent();
	if (!BossCapsule || !BossCapsule->IsRegistered())
	{
		RestoreBossHideInsideOption();
		return;
	}
	float CapsuleRadius = 0.f;
	float CapsuleHalfHeight = 0.f;
	BossCapsule->GetScaledCapsuleSize(CapsuleRadius, CapsuleHalfHeight);
	const FVector CapsuleCenter = BossCapsule->GetComponentLocation();
	const FVector CapsuleUp = BossCapsule->GetUpVector().GetSafeNormal();
	if (!IsFiniteCameraBounds(CapsuleCenter, FVector(CapsuleRadius, CapsuleHalfHeight, 0.f)) || CapsuleUp.IsNearlyZero())
	{
		RestoreBossHideInsideOption();
		return;
	}
	TInlineComponentArray<UPrimitiveComponent*> Components(PackBoss);
	TArray<UPrimitiveComponent*> MeshComponents;
	for (UPrimitiveComponent* Component : Components)
	{
		if (!Component || (!Cast<USkeletalMeshComponent>(Component) && !Cast<UStaticMeshComponent>(Component)))
		{
			continue;
		}
		if (!Component->IsRegistered() || !Component->IsVisible())
		{
			continue;
		}

		MeshComponents.Add(Component);
	}

	const bool bInsideBossCapsule = IsPointWithinCameraCapsule(CameraLocation, CapsuleCenter, CapsuleUp,
		CapsuleRadius, CapsuleHalfHeight, MarginCm);
	if (MeshComponents.IsEmpty())
	{
		RestoreBossHideInsideOption();
		return;
	}
	if (!bInsideBossCapsule)
	{
		const double NowSeconds = World->GetTimeSeconds();
		if (!bBossHideActive || NowSeconds - BossHideStartedSeconds >= CameraHideMinimumSeconds)
		{
			RestoreBossHideInsideOption();
			return;
		}
		// Keep the local hide briefly after leaving the grown capsule to prevent a
		// one-frame reveal/blink on fast spring-arm movement.
		return;
	}
	if (!bBossHideActive)
	{
		BossHideStartedSeconds = World->GetTimeSeconds();
		const float CameraToBossCm = FVector::Distance(CameraLocation, PackBoss->GetActorLocation());
		UE_LOG(LogRPGCamera, Log, TEXT("HideBossInside enter meshes=%d camera_to_boss_cm=%.1f"),
			MeshComponents.Num(), CameraToBossCm);
	}
	bBossHideActive = true;
	BossHideActiveMeshCount = MeshComponents.Num();

	BossHideActor = PackBoss;
	BossHideController = PlayerController;
	for (UPrimitiveComponent* Component : MeshComponents)
	{
		const bool bAlreadyHidden = PlayerController->HiddenPrimitiveComponents.ContainsByPredicate(
			[Component](const TWeakObjectPtr<UPrimitiveComponent>& Existing) { return Existing.Get() == Component; });
		if (!bAlreadyHidden)
		{
			PlayerController->HiddenPrimitiveComponents.Add(Component);
			BossHideAddedComponents.Add(Component);
		}
	}
#endif
}

void URPGCameraRig::RestoreBossHideInsideOption()
{
	if (bBossHideActive)
	{
		const AActor* Boss = BossHideActor.Get();
		const float CameraToBossCm = Camera && IsValid(Boss)
			? FVector::Distance(Camera->GetComponentLocation(), Boss->GetActorLocation())
			: -1.f;
		UE_LOG(LogRPGCamera, Log, TEXT("HideBossInside exit_or_restore meshes=%d camera_to_boss_cm=%.1f"),
			BossHideActiveMeshCount, CameraToBossCm);
	}
	if (APlayerController* PlayerController = BossHideController.Get())
	{
		for (const TWeakObjectPtr<UPrimitiveComponent>& WeakComponent : BossHideAddedComponents)
		{
			if (UPrimitiveComponent* Component = WeakComponent.Get())
			{
				PlayerController->HiddenPrimitiveComponents.RemoveSingle(Component);
			}
		}
	}
	BossHideAddedComponents.Reset();
	BossHideActiveMeshCount = 0;
	bBossHideActive = false;
	BossHideStartedSeconds = 0.0;
	BossHideActor.Reset();
	BossHideController.Reset();
}

void URPGCameraRig::ApplyLockOnFramingOption(float DeltaTime)
{
#if !UE_BUILD_SHIPPING
	const bool bEnabled = CVarCameraLockOnFraming.GetValueOnGameThread() != 0;
	if (!bEnabled)
	{
		RestoreLockOnFramingOption();
		return;
	}

	ACharacter* Player = Cast<ACharacter>(GetOwner());
	APlayerController* PlayerController = Player ? Cast<APlayerController>(Player->GetController()) : nullptr;
	UWorld* World = GetWorld();
	if (!Player || !PlayerController || !PlayerController->IsLocalController() || !World || !Boom || DeltaTime <= 0.f)
	{
		RestoreLockOnFramingOption();
		return;
	}

	ACharacter* PackBoss = nullptr;
	for (TActorIterator<APawn> It(World); It; ++It)
	{
		if (URPGPlayerMovesSubsystem::IsPackBoss(*It))
		{
			PackBoss = Cast<ACharacter>(*It);
			if (PackBoss)
			{
				break;
			}
		}
	}
	if (!PackBoss)
	{
		RestoreLockOnFramingOption();
		return;
	}
	if (!LockOnLookAction)
	{
		LockOnLookAction = LoadObject<UInputAction>(nullptr,
			TEXT("/Game/AdvancedARPGCombat/MeleeCombatSystem/Blueprints/Input/InputActions/IA_Look.IA_Look"));
	}
	const UEnhancedPlayerInput* EnhancedPlayerInput = Cast<UEnhancedPlayerInput>(PlayerController->PlayerInput);
	if (!LockOnLookAction || !EnhancedPlayerInput)
	{
		// Fail open to the authored camera if the real look action cannot be read;
		// never infer player intent from another system's ControlRotation writes.
		RestoreLockOnFramingOption();
		return;
	}
	if (!bHasOriginalLockOnUsePawnControlRotation)
	{
		OriginalLockOnUsePawnControlRotation = Boom->bUsePawnControlRotation;
		bHasOriginalLockOnUsePawnControlRotation = true;
	}
	Boom->bUsePawnControlRotation = true;

	const FRotator ControlRotation = PlayerController->GetControlRotation();
	if (LockOnTarget.Get() != PackBoss)
	{
		LockOnTarget = PackBoss;
		LockOnManualInputSecondsRemaining = 0.f;
	}

	const FVector2D LookValue = EnhancedPlayerInput->GetActionValue(LockOnLookAction).Get<FVector2D>();
	if (LookValue.Size() > LockOnLookInputDeadzone)
	{
		LockOnManualInputSecondsRemaining = LockOnManualInputGraceSeconds;
	}
	else
	{
		LockOnManualInputSecondsRemaining = FMath::Max(0.f, LockOnManualInputSecondsRemaining - DeltaTime);
	}

	FRotator DesiredRotation = ControlRotation;
	FVector ToBoss = PackBoss->GetActorLocation() - Player->GetActorLocation();
	ToBoss.Z = 0.f;
	if (!ToBoss.IsNearlyZero() && LockOnManualInputSecondsRemaining <= 0.f)
	{
		const float TargetYaw = FMath::RadiansToDegrees(FMath::Atan2(ToBoss.Y, ToBoss.X));
		const float YawDelta = FMath::FindDeltaAngleDegrees(ControlRotation.Yaw, TargetYaw);
		const float YawSpeed = FMath::Clamp(
			FMath::Abs(YawDelta) * LockOnYawDegreesPerSecondPerDegreeError,
			LockOnYawMinimumDegreesPerSecond,
			LockOnYawMaximumDegreesPerSecond);
		DesiredRotation.Yaw = FMath::FixedTurn(ControlRotation.Yaw, TargetYaw, YawSpeed * DeltaTime);
	}
	DesiredRotation.Pitch = FMath::Clamp(FRotator::NormalizeAxis(DesiredRotation.Pitch), PitchMin, PitchMax);
	if (!DesiredRotation.Equals(ControlRotation, 0.001f))
	{
		PlayerController->SetControlRotation(DesiredRotation);
	}
	// The input action, not ControlRotation deltas, owns the manual grace period;
	// this avoids mistaking pack camera-assist writes for player input.
#endif
}

void URPGCameraRig::RestoreLockOnFramingOption()
{
	if (bHasOriginalLockOnUsePawnControlRotation)
	{
		if (USpringArmComponent* SpringArm = Boom.Get())
		{
			SpringArm->bUsePawnControlRotation = OriginalLockOnUsePawnControlRotation;
		}
	}
	bHasOriginalLockOnUsePawnControlRotation = false;
	LockOnTarget.Reset();
	LockOnManualInputSecondsRemaining = 0.f;
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
	ApplyBossCameraCollisionOption(); // non-Shipping experiment; default off and restores the capsule's authored response
	ApplyBossHideInsideOption(); // non-Shipping experiment; controller-local primitive hide only
	ApplyLockOnFramingOption(DeltaTime); // non-Shipping experiment; rate-limited lock-on yaw follows the boss through ControlRotation
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
