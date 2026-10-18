// Copyright One Boss Fight. All Rights Reserved.

#include "Combat/RPGTargetLockComponent.h"
#include "Characters/RPGPlayerCharacter.h"
#include "Combat/RPGAttributeComponent.h"
#include "Combat/RPGCombatComponent.h"
#include "Engine/World.h"
#include "EngineUtils.h"
#include "GameFramework/CharacterMovementComponent.h"
#include "GameFramework/Controller.h"

URPGTargetLockComponent::URPGTargetLockComponent()
{
	PrimaryComponentTick.bCanEverTick = true;
	PrimaryComponentTick.bStartWithTickEnabled = false;
	// Camera aim must be settled before the spring arm and character movement read the control rotation.
	PrimaryComponentTick.TickGroup = TG_PrePhysics;
}

// -------------------------------------------------------------------------------------------------
// Pure selection helpers
// -------------------------------------------------------------------------------------------------

int32 URPGTargetLockComponent::ChooseByViewAlignment(const FVector& ViewOrigin, const FVector& ViewForward, const TArray<FVector>& Points)
{
	int32 BestIndex = INDEX_NONE;
	float BestDot = -2.f;
	const FVector Forward = ViewForward.GetSafeNormal();
	for (int32 Index = 0; Index < Points.Num(); ++Index)
	{
		const float Dot = FVector::DotProduct(Forward, (Points[Index] - ViewOrigin).GetSafeNormal());
		if (Dot > BestDot)
		{
			BestDot = Dot;
			BestIndex = Index;
		}
	}
	return BestIndex;
}

int32 URPGTargetLockComponent::ChooseBySide(const FVector& ViewOrigin, const FVector& CurrentPoint, const TArray<FVector>& Points, float Direction)
{
	if (FMath::IsNearlyZero(Direction))
	{
		return INDEX_NONE;
	}

	const float CurrentYaw = (CurrentPoint - ViewOrigin).Rotation().Yaw;
	int32 BestIndex = INDEX_NONE;
	float BestAbsDelta = TNumericLimits<float>::Max();
	for (int32 Index = 0; Index < Points.Num(); ++Index)
	{
		// Yaw grows clockwise seen from above, so a positive delta is to the right.
		const float Delta = FMath::FindDeltaAngleDegrees(CurrentYaw, (Points[Index] - ViewOrigin).Rotation().Yaw);
		if (FMath::IsNearlyZero(Delta, 0.5f) || (Delta > 0.f) != (Direction > 0.f))
		{
			continue;
		}
		if (FMath::Abs(Delta) < BestAbsDelta)
		{
			BestAbsDelta = FMath::Abs(Delta);
			BestIndex = Index;
		}
	}
	return BestIndex;
}

// -------------------------------------------------------------------------------------------------
// Target acquisition
// -------------------------------------------------------------------------------------------------

FVector URPGTargetLockComponent::GetViewOrigin() const
{
	return GetOwner()->GetActorLocation() + FVector(0.f, 0.f, PivotHeightOffset);
}

FVector URPGTargetLockComponent::GetTargetPoint(const AActor* Target) const
{
	return Target->GetActorLocation() + FVector(0.f, 0.f, TargetHeightOffset);
}

bool URPGTargetLockComponent::IsValidTarget(const AActor* Target, float MaxDistance) const
{
	if (!Target || Target == GetOwner() || Target->IsActorBeingDestroyed())
	{
		return false;
	}

	const URPGCombatComponent* TargetCombat = Target->FindComponentByClass<URPGCombatComponent>();
	const URPGCombatComponent* OwnerCombat = GetOwner()->FindComponentByClass<URPGCombatComponent>();
	if (!TargetCombat || TargetCombat->IsDead())
	{
		return false;
	}
	if (OwnerCombat && OwnerCombat->TeamId == TargetCombat->TeamId)
	{
		return false;
	}
	if (FVector::Dist(GetOwner()->GetActorLocation(), Target->GetActorLocation()) > MaxDistance)
	{
		return false;
	}

	// Line of sight: level geometry between the camera pivot and the target breaks it.
	FHitResult Hit;
	FCollisionQueryParams Params(SCENE_QUERY_STAT(RPGLockOnSight), false, GetOwner());
	Params.AddIgnoredActor(Target);
	return !GetWorld()->LineTraceSingleByChannel(Hit, GetViewOrigin(), GetTargetPoint(Target), ECC_Visibility, Params);
}

void URPGTargetLockComponent::GatherCandidates(TArray<FCandidate>& OutCandidates) const
{
	UWorld* World = GetWorld();
	if (!World)
	{
		return;
	}

	for (TActorIterator<ARPGCharacterBase> It(World); It; ++It)
	{
		if (IsValidTarget(*It, MaxLockDistance))
		{
			FCandidate Candidate;
			Candidate.Actor = *It;
			Candidate.Point = GetTargetPoint(*It);
			OutCandidates.Add(Candidate);
		}
	}
}

bool URPGTargetLockComponent::ToggleLock()
{
	if (IsLocked())
	{
		ClearTarget();
		return false;
	}

	TArray<FCandidate> Candidates;
	GatherCandidates(Candidates);
	if (Candidates.IsEmpty())
	{
		return false;
	}

	// View direction comes from the controller, i.e. where the camera looks.
	const APawn* Pawn = Cast<APawn>(GetOwner());
	const FVector Forward = (Pawn && Pawn->GetController()) ? Pawn->GetControlRotation().Vector() : GetOwner()->GetActorForwardVector();

	TArray<FVector> Points;
	for (const FCandidate& Candidate : Candidates)
	{
		Points.Add(Candidate.Point);
	}
	const int32 Best = ChooseByViewAlignment(GetViewOrigin(), Forward, Points);
	if (Best == INDEX_NONE)
	{
		return false;
	}

	SetTarget(Candidates[Best].Actor);
	return true;
}

bool URPGTargetLockComponent::SwitchTarget(float Direction)
{
	AActor* Current = LockedTarget.Get();
	if (!Current || TimeSinceSwitch < SwitchCooldown)
	{
		return false;
	}

	TArray<FCandidate> Candidates;
	GatherCandidates(Candidates);
	Candidates.RemoveAll([Current](const FCandidate& Candidate) { return Candidate.Actor == Current; });

	TArray<FVector> Points;
	for (const FCandidate& Candidate : Candidates)
	{
		Points.Add(Candidate.Point);
	}
	const int32 Best = ChooseBySide(GetViewOrigin(), GetTargetPoint(Current), Points, Direction);
	if (Best == INDEX_NONE)
	{
		return false;
	}

	SetTarget(Candidates[Best].Actor);
	return true;
}

bool URPGTargetLockComponent::HandleLookInput(float AxisX)
{
	if (!IsLocked())
	{
		return false;
	}
	if (FMath::Abs(AxisX) >= SwitchFlickThreshold)
	{
		SwitchTarget(AxisX);
	}
	return true;
}

void URPGTargetLockComponent::ClearTarget()
{
	SetTarget(nullptr);
}

void URPGTargetLockComponent::SetTarget(AActor* NewTarget)
{
	AActor* Old = LockedTarget.Get();
	LockedTarget = NewTarget;
	TimeSinceSwitch = 0.f;

	ApplyBodyOrientation(NewTarget != nullptr);
	SetComponentTickEnabled(NewTarget != nullptr);

	if (Old != NewTarget)
	{
		OnTargetChanged.Broadcast(NewTarget);
	}
}

void URPGTargetLockComponent::ApplyBodyOrientation(bool bLocked) const
{
	// Locked: strafe facing the target. Free: face the movement direction.
	if (const ACharacter* Character = Cast<ACharacter>(GetOwner()))
	{
		UCharacterMovementComponent* Movement = Character->GetCharacterMovement();
		Movement->bOrientRotationToMovement = !bLocked;
		Movement->bUseControllerDesiredRotation = bLocked;
	}
}

void URPGTargetLockComponent::TickComponent(float DeltaTime, ELevelTick TickType, FActorComponentTickFunction* ThisTickFunction)
{
	Super::TickComponent(DeltaTime, TickType, ThisTickFunction);
	TimeSinceSwitch += DeltaTime;

	AActor* Target = LockedTarget.Get();
	if (!IsValidTarget(Target, BreakDistance))
	{
		ClearTarget();
		return;
	}

	APawn* Pawn = Cast<APawn>(GetOwner());
	AController* Controller = Pawn ? Pawn->GetController() : nullptr;
	if (!Controller)
	{
		return;
	}

	FRotator Desired = (GetTargetPoint(Target) - GetViewOrigin()).Rotation();
	Desired.Pitch = FMath::Clamp(Desired.Pitch, MinLockPitch, MaxLockPitch);
	Desired.Roll = 0.f;
	Controller->SetControlRotation(FMath::RInterpTo(Controller->GetControlRotation(), Desired, DeltaTime, CameraInterpSpeed));

	// Sprinting turns the body toward the movement direction (running away); a dodge keeps its own heading.
	const ARPGPlayerCharacter* Player = Cast<ARPGPlayerCharacter>(GetOwner());
	const URPGCombatComponent* Combat = GetOwner()->FindComponentByClass<URPGCombatComponent>();
	const bool bDodging = Combat && Combat->GetState() == ERPGCombatState::Dodging;
	const bool bSprinting = Player && Player->IsSprinting();
	if (const ACharacter* Character = Cast<ACharacter>(GetOwner()))
	{
		UCharacterMovementComponent* Movement = Character->GetCharacterMovement();
		Movement->bOrientRotationToMovement = bSprinting && !bDodging;
		Movement->bUseControllerDesiredRotation = !bSprinting && !bDodging;
	}
}
