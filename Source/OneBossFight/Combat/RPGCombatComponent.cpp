// Copyright One Boss Fight. All Rights Reserved.

#include "Combat/RPGCombatComponent.h"
#include "Animation/AnimInstance.h"
#include "Animation/AnimMontage.h"
#include "Characters/RPGCharacterBase.h"
#include "Combat/RPGAttributeComponent.h"
#include "Components/SkeletalMeshComponent.h"
#include "Engine/OverlapResult.h"
#include "Engine/World.h"
#include "GameFramework/Character.h"

URPGCombatComponent::URPGCombatComponent()
{
	PrimaryComponentTick.bCanEverTick = true;
	PrimaryComponentTick.bStartWithTickEnabled = false;
}

void URPGCombatComponent::BeginPlay()
{
	Super::BeginPlay();
	GetAttributes();
}

URPGAttributeComponent* URPGCombatComponent::GetAttributes()
{
	AActor* Owner = GetOwner();
	URPGAttributeComponent* Attributes = Owner ? Owner->FindComponentByClass<URPGAttributeComponent>() : nullptr;
	if (Attributes && !bBoundToAttributes)
	{
		bBoundToAttributes = true;
		Attributes->OnDeath.AddUniqueDynamic(this, &URPGCombatComponent::OnDeathFromAttributes);
	}
	return Attributes;
}

void URPGCombatComponent::OnDeathFromAttributes()
{
	Die();
}

// -------------------------------------------------------------------------------------------------
// State
// -------------------------------------------------------------------------------------------------

void URPGCombatComponent::SetState(ERPGCombatState NewState)
{
	const ERPGCombatState OldState = State;
	State = NewState;

	// Windows belong to the action that opened them; a new state starts with all of them closed.
	if (bHitWindowOpen)
	{
		bHitWindowOpen = false;
		OnHitWindowChanged.Broadcast(false);
	}
	bComboWindowOpen = false;
	bCancelWindowOpen = false;
	bInvulnerable = false;

	if (OldState != NewState)
	{
		OnStateChanged.Broadcast(OldState, NewState);
	}
	UpdateTickState();
}

void URPGCombatComponent::UpdateTickState()
{
	if (IsRegistered())
	{
		SetComponentTickEnabled(FallbackKind != EFallbackKind::None || BufferedAction != ERPGBufferedAction::None);
	}
}

void URPGCombatComponent::BeginFallback(EFallbackKind Kind, float Duration)
{
	FallbackKind = Kind;
	FallbackElapsed = 0.f;
	FallbackDuration = Duration;
	UpdateTickState();
}

// -------------------------------------------------------------------------------------------------
// Animation-driven windows
// -------------------------------------------------------------------------------------------------

void URPGCombatComponent::SetHitWindow(bool bOpen)
{
	const bool bInAttack = State == ERPGCombatState::Attacking || State == ERPGCombatState::Recovery;
	if (bOpen)
	{
		if (!bInAttack || bHitWindowOpen)
		{
			return;
		}
		bHitWindowOpen = true;
		OnHitWindowChanged.Broadcast(true);
		return;
	}

	if (!bHitWindowOpen)
	{
		return;
	}
	bHitWindowOpen = false;
	OnHitWindowChanged.Broadcast(false);
	if (State == ERPGCombatState::Attacking)
	{
		SetState(ERPGCombatState::Recovery);
	}
}

void URPGCombatComponent::SetComboWindow(bool bOpen)
{
	if (bOpen)
	{
		if (State != ERPGCombatState::Attacking && State != ERPGCombatState::Recovery)
		{
			return;
		}
		SetState(ERPGCombatState::ComboWindow);
		bComboWindowOpen = true;
		TryConsumeBuffer();
		return;
	}

	if (State == ERPGCombatState::ComboWindow)
	{
		SetState(ERPGCombatState::Recovery);
	}
}

void URPGCombatComponent::SetInvulnerable(bool bInvulnerableNow)
{
	bInvulnerable = bInvulnerableNow && State != ERPGCombatState::Dead;
}

void URPGCombatComponent::SetCancelWindow(bool bOpen)
{
	if (State != ERPGCombatState::Attacking && State != ERPGCombatState::Recovery)
	{
		return;
	}
	bCancelWindowOpen = bOpen;
	if (bOpen)
	{
		TryConsumeBuffer();
	}
}

void URPGCombatComponent::EndCurrentAction()
{
	if (State == ERPGCombatState::Dead)
	{
		return;
	}

	FallbackKind = EFallbackKind::None;
	SetState(bBlockHeld ? ERPGCombatState::Blocking : ERPGCombatState::Locomotion);
	TryConsumeBuffer();
}

// -------------------------------------------------------------------------------------------------
// Requests
// -------------------------------------------------------------------------------------------------

bool URPGCombatComponent::RequestLightAttack()
{
	if (State == ERPGCombatState::Dead || State == ERPGCombatState::Staggered)
	{
		return false;
	}
	if (State == ERPGCombatState::Locomotion || State == ERPGCombatState::Blocking || State == ERPGCombatState::ComboWindow)
	{
		return StartAttack(ERPGAttackType::Light);
	}
	Buffer(ERPGBufferedAction::LightAttack);
	return false;
}

bool URPGCombatComponent::RequestHeavyAttack()
{
	if (State == ERPGCombatState::Dead || State == ERPGCombatState::Staggered)
	{
		return false;
	}
	if (State == ERPGCombatState::Locomotion || State == ERPGCombatState::Blocking || State == ERPGCombatState::ComboWindow)
	{
		return StartAttack(ERPGAttackType::Heavy);
	}
	Buffer(ERPGBufferedAction::HeavyAttack);
	return false;
}

bool URPGCombatComponent::RequestDodge(FVector Direction)
{
	if (State == ERPGCombatState::Dead || State == ERPGCombatState::Staggered)
	{
		return false;
	}
	if (CanDodgeNow())
	{
		return StartDodge(Direction);
	}
	BufferedDodgeDirection = Direction;
	Buffer(ERPGBufferedAction::Dodge);
	return false;
}

bool URPGCombatComponent::CanDodgeNow() const
{
	switch (State)
	{
	case ERPGCombatState::Locomotion:
	case ERPGCombatState::Blocking:
	case ERPGCombatState::ComboWindow:
	case ERPGCombatState::Recovery:
		return true;
	case ERPGCombatState::Attacking:
		return bCancelWindowOpen;
	default:
		return false;
	}
}

bool URPGCombatComponent::StartBlock()
{
	bBlockHeld = true;
	if (State == ERPGCombatState::Locomotion)
	{
		SetState(ERPGCombatState::Blocking);
	}
	return State == ERPGCombatState::Blocking;
}

void URPGCombatComponent::StopBlock()
{
	bBlockHeld = false;
	if (State == ERPGCombatState::Blocking)
	{
		SetState(ERPGCombatState::Locomotion);
		TryConsumeBuffer();
	}
}

void URPGCombatComponent::Buffer(ERPGBufferedAction Action)
{
	BufferedAction = Action;
	BufferTimeRemaining = InputBufferSeconds;
	UpdateTickState();
}

void URPGCombatComponent::TryConsumeBuffer()
{
	if (BufferedAction == ERPGBufferedAction::None)
	{
		return;
	}

	const bool bFreeToAct = State == ERPGCombatState::Locomotion || State == ERPGCombatState::Blocking
		|| State == ERPGCombatState::ComboWindow;

	bool bAllowed = false;
	bool bStarted = false;
	switch (BufferedAction)
	{
	case ERPGBufferedAction::LightAttack:
		bAllowed = bFreeToAct;
		bStarted = bAllowed && StartAttack(ERPGAttackType::Light);
		break;
	case ERPGBufferedAction::HeavyAttack:
		bAllowed = bFreeToAct;
		bStarted = bAllowed && StartAttack(ERPGAttackType::Heavy);
		break;
	case ERPGBufferedAction::Dodge:
		bAllowed = CanDodgeNow();
		bStarted = bAllowed && StartDodge(BufferedDodgeDirection);
		break;
	default:
		break;
	}

	// An allowed-but-failed action (no stamina) is dropped instead of retried every window.
	if (bStarted || bAllowed)
	{
		BufferedAction = ERPGBufferedAction::None;
		UpdateTickState();
	}
}

// -------------------------------------------------------------------------------------------------
// Actions
// -------------------------------------------------------------------------------------------------

bool URPGCombatComponent::StartAttack(ERPGAttackType Type)
{
	int32 NextIndex = 0;
	if (Type == ERPGAttackType::Light && State == ERPGCombatState::ComboWindow && CurrentAttackType == ERPGAttackType::Light)
	{
		const int32 ChainLength = Weapon ? FMath::Max(1, Weapon->GetLightComboLength()) : 1;
		NextIndex = (ComboIndex + 1) % ChainLength;
	}

	const FRPGAttackData Attack = Weapon ? Weapon->GetAttack(Type, NextIndex) : FRPGAttackData();

	URPGAttributeComponent* Attributes = GetAttributes();
	if (Attributes && !Attributes->TryConsumeStamina(Attack.StaminaCost))
	{
		return false;
	}

	++ActionId;
	CurrentAttack = Attack;
	CurrentAttackType = Type;
	ComboIndex = NextIndex;
	BufferedAction = ERPGBufferedAction::None;
	FallbackKind = EFallbackKind::None;

	StopActionMontage();
	SetState(ERPGCombatState::Attacking);
	if (!PlayActionMontage(Attack.Montage, Attack.PlayRate))
	{
		BeginFallback(EFallbackKind::Attack, Attack.FallbackDuration / FMath::Max(Attack.PlayRate, 0.1f));
	}
	return true;
}

bool URPGCombatComponent::StartDodge(const FVector& Direction)
{
	URPGAttributeComponent* Attributes = GetAttributes();
	if (Attributes && !Attributes->TryConsumeStamina(DodgeStaminaCost))
	{
		return false;
	}

	++ActionId;
	BufferedAction = ERPGBufferedAction::None;
	FallbackKind = EFallbackKind::None;

	StopActionMontage();
	SetState(ERPGCombatState::Dodging);

	if (ACharacter* Character = Cast<ACharacter>(GetOwner()))
	{
		FVector Flat = FVector(Direction.X, Direction.Y, 0.f);
		if (Flat.Normalize())
		{
			Character->SetActorRotation(Flat.Rotation());
		}
		else
		{
			// No input: step backward away from where the character faces.
			Flat = -Character->GetActorForwardVector();
			Flat.Z = 0.f;
			Flat.Normalize();
		}
		Character->LaunchCharacter(Flat * DodgeSpeed, /*bXYOverride=*/true, /*bZOverride=*/false);
	}

	const ARPGCharacterBase* Base = Cast<ARPGCharacterBase>(GetOwner());
	UAnimMontage* Montage = Base ? Base->GetDodgeMontage() : nullptr;
	if (!PlayActionMontage(Montage, 1.f))
	{
		BeginFallback(EFallbackKind::Dodge, DodgeDuration);
	}
	return true;
}

bool URPGCombatComponent::StartCustomAttack(const FRPGAttackData& Attack)
{
	if (State != ERPGCombatState::Locomotion && State != ERPGCombatState::Blocking)
	{
		return false;
	}

	++ActionId;
	CurrentAttack = Attack;
	CurrentAttackType = ERPGAttackType::Light;
	ComboIndex = 0;
	BufferedAction = ERPGBufferedAction::None;
	FallbackKind = EFallbackKind::None;

	StopActionMontage();
	SetState(ERPGCombatState::Attacking);
	if (!PlayActionMontage(Attack.Montage, Attack.PlayRate))
	{
		BeginFallback(EFallbackKind::Attack, Attack.FallbackDuration / FMath::Max(Attack.PlayRate, 0.1f));
	}
	return true;
}

int32 URPGCombatComponent::ApplyRadialHit(const FVector& Center, float Radius)
{
	UWorld* World = GetWorld();
	AActor* Owner = GetOwner();
	if (!World || !Owner || Radius <= 0.f)
	{
		return 0;
	}

	FCollisionQueryParams Params(SCENE_QUERY_STAT(RPGRadialHit), false, Owner);
	TArray<FOverlapResult> Overlaps;
	World->OverlapMultiByObjectType(Overlaps, Center, FQuat::Identity, FCollisionObjectQueryParams(ECC_Pawn),
		FCollisionShape::MakeSphere(Radius), Params);

	TSet<AActor*> Seen;
	int32 Hits = 0;
	for (const FOverlapResult& Overlap : Overlaps)
	{
		AActor* Target = Overlap.GetActor();
		if (!Target || Seen.Contains(Target))
		{
			continue;
		}
		Seen.Add(Target);

		URPGCombatComponent* TargetCombat = Target->FindComponentByClass<URPGCombatComponent>();
		if (!TargetCombat || TargetCombat->TeamId == TeamId)
		{
			continue;
		}

		FRPGHitInfo Info = BuildOutgoingHit();
		Info.HitLocation = Target->GetActorLocation();
		Info.HitDirection = (Target->GetActorLocation() - Center).GetSafeNormal2D();
		TargetCombat->ProcessIncomingHit(Info);
		++Hits;
	}
	return Hits;
}

void URPGCombatComponent::Stagger()
{
	if (State == ERPGCombatState::Dead)
	{
		return;
	}

	++ActionId;
	BufferedAction = ERPGBufferedAction::None;
	FallbackKind = EFallbackKind::None;

	StopActionMontage();
	SetState(ERPGCombatState::Staggered);

	const ARPGCharacterBase* Base = Cast<ARPGCharacterBase>(GetOwner());
	UAnimMontage* Montage = Base ? Base->GetHitReactMontage() : nullptr;
	if (!PlayActionMontage(Montage, 1.f))
	{
		BeginFallback(EFallbackKind::Stagger, StaggerDuration);
	}
}

void URPGCombatComponent::Die()
{
	if (State == ERPGCombatState::Dead)
	{
		return;
	}

	++ActionId;
	BufferedAction = ERPGBufferedAction::None;
	FallbackKind = EFallbackKind::None;
	bBlockHeld = false;

	StopActionMontage();
	SetState(ERPGCombatState::Dead);

	if (URPGAttributeComponent* Attributes = GetAttributes())
	{
		Attributes->SetStaminaDrain(0.f);
	}

	const ARPGCharacterBase* Base = Cast<ARPGCharacterBase>(GetOwner());
	PlayActionMontage(Base ? Base->GetDeathMontage() : nullptr, 1.f);
}

void URPGCombatComponent::ResetCombat()
{
	++ActionId;
	BufferedAction = ERPGBufferedAction::None;
	FallbackKind = EFallbackKind::None;
	bBlockHeld = false;
	ComboIndex = 0;
	CurrentAttack = FRPGAttackData();

	StopActionMontage();
	if (const ACharacter* Character = Cast<ACharacter>(GetOwner()))
	{
		if (USkeletalMeshComponent* Mesh = Character->GetMesh())
		{
			Mesh->bPauseAnims = false;
		}
	}
	SetState(ERPGCombatState::Locomotion);
}

// -------------------------------------------------------------------------------------------------
// Damage path
// -------------------------------------------------------------------------------------------------

FRPGHitResult URPGCombatComponent::ProcessIncomingHit(const FRPGHitInfo& Hit)
{
	FRPGHitResult Result;
	if (State == ERPGCombatState::Dead)
	{
		return Result;
	}
	if (IsInvulnerable())
	{
		Result.bIgnoredInvulnerable = true;
		OnHitReceived.Broadcast(Hit, Result);
		return Result;
	}

	URPGAttributeComponent* Attributes = GetAttributes();
	Result.bProcessed = true;

	float Damage = Hit.Damage;
	bool bGuardBroken = false;

	if (State == ERPGCombatState::Blocking && !Hit.bUnblockable)
	{
		// Only hits from the front are blocked.
		const FVector Forward = GetOwner()->GetActorForwardVector().GetSafeNormal2D();
		const FVector FromAttacker = (-Hit.HitDirection).GetSafeNormal2D();
		if (FVector::DotProduct(Forward, FromAttacker) > 0.f)
		{
			Result.bBlocked = true;
			Damage *= BlockDamageMultiplier;
			if (Attributes)
			{
				bGuardBroken = Attributes->ForceConsumeStamina(Hit.Damage * BlockStaminaPerDamage);
			}
		}
	}

	if (Attributes)
	{
		Result.DamageApplied = Attributes->ApplyDamage(Damage);
		Result.bKilled = Attributes->IsDead();
	}

	if (!Result.bKilled)
	{
		if (Result.bBlocked)
		{
			// A blocked hit never builds poise damage, but an empty stamina bar breaks the guard.
			if (bGuardBroken)
			{
				Result.bPoiseBroken = true;
				Stagger();
			}
		}
		else if (Attributes && Attributes->ApplyPoiseDamage(Hit.PoiseDamage))
		{
			Result.bPoiseBroken = true;
			Stagger();
		}
	}

	OnHitReceived.Broadcast(Hit, Result);
	return Result;
}

FRPGHitInfo URPGCombatComponent::BuildOutgoingHit() const
{
	FRPGHitInfo Info;
	Info.Instigator = GetOwner();
	Info.Damage = CurrentAttack.Damage;
	Info.PoiseDamage = CurrentAttack.PoiseDamage;
	Info.bUnblockable = CurrentAttack.bUnblockable;
	return Info;
}

// -------------------------------------------------------------------------------------------------
// Ticking and montages
// -------------------------------------------------------------------------------------------------

void URPGCombatComponent::TickComponent(float DeltaTime, ELevelTick TickType, FActorComponentTickFunction* ThisTickFunction)
{
	Super::TickComponent(DeltaTime, TickType, ThisTickFunction);
	TickCombat(DeltaTime);
}

void URPGCombatComponent::TickCombat(float DeltaTime)
{
	if (BufferedAction != ERPGBufferedAction::None)
	{
		BufferTimeRemaining -= DeltaTime;
		if (BufferTimeRemaining <= 0.f)
		{
			BufferedAction = ERPGBufferedAction::None;
		}
	}

	if (FallbackKind != EFallbackKind::None)
	{
		FallbackElapsed += DeltaTime;

		if (FallbackKind == EFallbackKind::Attack)
		{
			const FVector2D Hit = CurrentAttack.FallbackHitWindow;
			const bool bWantHit = FallbackElapsed >= Hit.X && FallbackElapsed < Hit.Y;
			if (bWantHit != bHitWindowOpen)
			{
				SetHitWindow(bWantHit);
			}

			const FVector2D Combo = CurrentAttack.FallbackComboWindow;
			const bool bWantCombo = FallbackElapsed >= Combo.X && FallbackElapsed < Combo.Y;
			if (bWantCombo != bComboWindowOpen)
			{
				SetComboWindow(bWantCombo);
			}
		}
		else if (FallbackKind == EFallbackKind::Dodge)
		{
			const bool bWantIFrames = FallbackElapsed >= DodgeIFrames.X && FallbackElapsed < DodgeIFrames.Y;
			if (bWantIFrames != bInvulnerable)
			{
				SetInvulnerable(bWantIFrames);
			}
		}

		// The windows above may have changed state or ended the action; only finish if it is still ours.
		if (FallbackKind != EFallbackKind::None && FallbackElapsed >= FallbackDuration)
		{
			EndCurrentAction();
		}
	}

	UpdateTickState();
}

bool URPGCombatComponent::PlayActionMontage(UAnimMontage* Montage, float PlayRate)
{
	const ACharacter* Character = Cast<ACharacter>(GetOwner());
	USkeletalMeshComponent* Mesh = Character ? Character->GetMesh() : nullptr;
	UAnimInstance* AnimInstance = Mesh ? Mesh->GetAnimInstance() : nullptr;
	if (!Montage || !AnimInstance)
	{
		return false;
	}

	if (AnimInstance->Montage_Play(Montage, PlayRate) <= 0.f)
	{
		return false;
	}

	FOnMontageBlendingOutStarted BlendingOut;
	BlendingOut.BindUObject(this, &URPGCombatComponent::OnMontageBlendingOut, ActionId);
	AnimInstance->Montage_SetBlendingOutDelegate(BlendingOut, Montage);
	return true;
}

void URPGCombatComponent::StopActionMontage()
{
	const ACharacter* Character = Cast<ACharacter>(GetOwner());
	USkeletalMeshComponent* Mesh = Character ? Character->GetMesh() : nullptr;
	if (UAnimInstance* AnimInstance = Mesh ? Mesh->GetAnimInstance() : nullptr)
	{
		AnimInstance->Montage_Stop(0.1f);
	}
}

void URPGCombatComponent::OnMontageBlendingOut(UAnimMontage* Montage, bool bInterrupted, int32 ForActionId)
{
	if (ForActionId != ActionId)
	{
		return; // A newer action already took over.
	}

	if (State == ERPGCombatState::Dead)
	{
		// Hold the last pose of the death animation instead of blending back to idle.
		if (const ACharacter* Character = Cast<ACharacter>(GetOwner()))
		{
			if (USkeletalMeshComponent* Mesh = Character->GetMesh())
			{
				Mesh->bPauseAnims = true;
			}
		}
		return;
	}
	EndCurrentAction();
}
