// Copyright One Boss Fight. All Rights Reserved.

#include "Boss/RPGBossCombatComponent.h"
#include "Animation/AnimInstance.h"
#include "Animation/AnimMontage.h"
#include "OneBossFight.h"
#include "Boss/RPGBossAttackData.h"
#include "Combat/RPGAttributeComponent.h"
#include "Combat/RPGCombatComponent.h"
#include "Components/SkeletalMeshComponent.h"
#include "DrawDebugHelpers.h"
#include "GameFramework/Character.h"
#include "HAL/IConsoleManager.h"

URPGBossCombatComponent::URPGBossCombatComponent()
{
	PrimaryComponentTick.bCanEverTick = true;
	PrimaryComponentTick.bStartWithTickEnabled = false;
	Random.Initialize(FMath::Rand());
}

void URPGBossCombatComponent::OnRegister()
{
	Super::OnRegister();
	// A boss starts out untouchable until the encounter engages it.
	if (URPGCombatComponent* Combat = GetCombat())
	{
		Combat->SetExternalInvulnerable(BossState != ERPGBossState::Combat);
	}
}

URPGCombatComponent* URPGBossCombatComponent::GetCombat() const
{
	return GetOwner() ? GetOwner()->FindComponentByClass<URPGCombatComponent>() : nullptr;
}

URPGAttributeComponent* URPGBossCombatComponent::EnsureBound()
{
	URPGAttributeComponent* Attributes = GetOwner() ? GetOwner()->FindComponentByClass<URPGAttributeComponent>() : nullptr;
	if (Attributes && !bBound)
	{
		bBound = true;
		Attributes->OnHealthChanged.AddUniqueDynamic(this, &URPGBossCombatComponent::HandleHealthChanged);
		Attributes->OnDeath.AddUniqueDynamic(this, &URPGBossCombatComponent::HandleDeath);
	}
	CooldownRemaining.SetNumZeroed(Attacks.Num());
	return Attributes;
}

// -------------------------------------------------------------------------------------------------
// Pure selection helpers
// -------------------------------------------------------------------------------------------------

int32 URPGBossCombatComponent::ComputePhase(const TArray<float>& Thresholds, float HealthFraction)
{
	int32 Phase = 1;
	for (const float Threshold : Thresholds)
	{
		if (HealthFraction <= Threshold)
		{
			++Phase;
		}
	}
	return Phase;
}

int32 URPGBossCombatComponent::ChooseAttack(const TArray<TObjectPtr<URPGBossAttackData>>& Attacks, const TArray<float>& CooldownRemaining,
	const FRPGAttackSelectionContext& Context, float RandomUnit)
{
	TArray<int32, TInlineAllocator<16>> Eligible;
	float TotalWeight = 0.f;
	for (int32 Index = 0; Index < Attacks.Num(); ++Index)
	{
		const URPGBossAttackData* Data = Attacks[Index];
		if (!Data || Data->Weight <= 0.f)
		{
			continue;
		}
		if (Context.Distance < Data->MinRange || Context.Distance > Data->MaxRange)
		{
			continue;
		}
		if (Context.AngleDegrees > Data->MaxAngle)
		{
			continue;
		}
		if (Context.Phase < Data->MinPhase || Context.Phase > Data->MaxPhase)
		{
			continue;
		}
		if (CooldownRemaining.IsValidIndex(Index) && CooldownRemaining[Index] > 0.f)
		{
			continue;
		}
		if (Index == Context.LastAttackIndex && Context.ConsecutiveRepeats >= Data->MaxConsecutiveRepeats)
		{
			continue;
		}
		Eligible.Add(Index);
		TotalWeight += Data->Weight;
	}

	if (Eligible.IsEmpty())
	{
		return INDEX_NONE;
	}

	float Pick = FMath::Clamp(RandomUnit, 0.f, 0.999999f) * TotalWeight;
	for (const int32 Index : Eligible)
	{
		Pick -= Attacks[Index]->Weight;
		if (Pick < 0.f)
		{
			return Index;
		}
	}
	return Eligible.Last();
}

// -------------------------------------------------------------------------------------------------
// Flow
// -------------------------------------------------------------------------------------------------

void URPGBossCombatComponent::SetBossState(ERPGBossState NewState)
{
	const ERPGBossState OldState = BossState;
	BossState = NewState;

	// Untouchable except while actually fighting (or dead, where the combat component refuses hits itself).
	if (URPGCombatComponent* Combat = GetCombat())
	{
		Combat->SetExternalInvulnerable(NewState != ERPGBossState::Combat && NewState != ERPGBossState::Dead);
	}

	UpdateTickState();
	if (OldState != NewState)
	{
		UE_LOG(LogOneBossFight, Log, TEXT("%s boss state %s -> %s (phase %d)"), *GetNameSafe(GetOwner()),
			*UEnum::GetValueAsString(OldState), *UEnum::GetValueAsString(NewState), CurrentPhase);
		OnBossStateChanged.Broadcast(OldState, NewState);
	}
}

void URPGBossCombatComponent::UpdateTickState()
{
	if (IsRegistered())
	{
		const bool bNeedsTick = BossState == ERPGBossState::Entrance || BossState == ERPGBossState::Combat
			|| BossState == ERPGBossState::PhaseTransition;
		SetComponentTickEnabled(bNeedsTick);
	}
}

float URPGBossCombatComponent::PlayMontageOnOwner(UAnimMontage* Montage) const
{
	const ACharacter* Character = Cast<ACharacter>(GetOwner());
	USkeletalMeshComponent* Mesh = Character ? Character->GetMesh() : nullptr;
	UAnimInstance* AnimInstance = Mesh ? Mesh->GetAnimInstance() : nullptr;
	if (!Montage || !AnimInstance)
	{
		return 0.f;
	}
	return FMath::Max(0.f, AnimInstance->Montage_Play(Montage, 1.f));
}

bool URPGBossCombatComponent::Engage(AActor* NewTarget)
{
	if (BossState != ERPGBossState::Dormant || !NewTarget)
	{
		return false;
	}

	EnsureBound();
	Target = NewTarget;
	StateTimer = EntranceDuration;
	const float MontageLength = PlayMontageOnOwner(EntranceMontage);
	if (MontageLength > 0.f)
	{
		StateTimer = MontageLength;
	}
	SetBossState(ERPGBossState::Entrance);
	return true;
}

void URPGBossCombatComponent::ResetBoss()
{
	EnsureBound();
	Target.Reset();
	CurrentPhase = 1;
	PhaseTransitionCount = 0;
	CooldownRemaining.Init(0.f, Attacks.Num());
	LastAttackIndex = INDEX_NONE;
	ConsecutiveRepeats = 0;
	CurrentAttackIndex = INDEX_NONE;
	bAttackInProgress = false;
	bHitWindowSeen = false;
	DecisionTimer = 0.f;
	StateTimer = 0.f;
	SetBossState(ERPGBossState::Dormant);
}

void URPGBossCombatComponent::HandleHealthChanged(float Current, float Max, float Delta)
{
	// Only damage taken while fighting can start a phase. Several hits in one frame start it once: the first
	// one makes the boss untouchable and leaves Combat, so the rest never reach this check.
	if (BossState != ERPGBossState::Combat || Delta >= 0.f || Current <= 0.f || Max <= 0.f)
	{
		return;
	}

	const int32 NewPhase = ComputePhase(PhaseHealthThresholds, Current / Max);
	if (NewPhase > CurrentPhase)
	{
		StartPhaseTransition(NewPhase);
	}
}

void URPGBossCombatComponent::HandleDeath()
{
	bAttackInProgress = false;
	SetBossState(ERPGBossState::Dead);
}

void URPGBossCombatComponent::StartPhaseTransition(int32 NewPhase)
{
	const int32 OldPhase = CurrentPhase;
	CurrentPhase = NewPhase;
	++PhaseTransitionCount;
	bAttackInProgress = false;

	// Drop whatever the boss was doing (attack, stagger) before the roar.
	if (URPGCombatComponent* Combat = GetCombat())
	{
		Combat->ResetCombat();
	}

	StateTimer = PhaseTransitionDuration;
	const float MontageLength = PlayMontageOnOwner(PhaseTransitionMontage);
	if (MontageLength > 0.f)
	{
		StateTimer = MontageLength;
	}
	SetBossState(ERPGBossState::PhaseTransition);
	OnPhaseChanged.Broadcast(OldPhase, NewPhase);
}

void URPGBossCombatComponent::FinishTimedState()
{
	DecisionTimer = RandomReactionDelay();
	SetBossState(ERPGBossState::Combat);
}

float URPGBossCombatComponent::RandomReactionDelay()
{
	return Random.FRandRange(FMath::Min(ReactionDelayMin, ReactionDelayMax), FMath::Max(ReactionDelayMin, ReactionDelayMax));
}

// -------------------------------------------------------------------------------------------------
// Ticking
// -------------------------------------------------------------------------------------------------

void URPGBossCombatComponent::TickComponent(float DeltaTime, ELevelTick TickType, FActorComponentTickFunction* ThisTickFunction)
{
	Super::TickComponent(DeltaTime, TickType, ThisTickFunction);
	TickBoss(DeltaTime);
}

void URPGBossCombatComponent::TickBoss(float DeltaTime)
{
	EnsureBound();
	switch (BossState)
	{
	case ERPGBossState::Entrance:
		if (AActor* Current = Target.Get())
		{
			TurnToward(Current->GetActorLocation(), IdleTurnRate, DeltaTime);
		}
		[[fallthrough]];
	case ERPGBossState::PhaseTransition:
		StateTimer -= DeltaTime;
		if (StateTimer <= 0.f)
		{
			FinishTimedState();
		}
		break;
	case ERPGBossState::Combat:
		TickCombatState(DeltaTime);
		break;
	default:
		break;
	}
}

void URPGBossCombatComponent::TurnToward(const FVector& WorldLocation, float DegreesPerSecond, float DeltaTime) const
{
	AActor* Owner = GetOwner();
	if (!Owner || DegreesPerSecond <= 0.f)
	{
		return;
	}

	const FVector ToTarget = (WorldLocation - Owner->GetActorLocation()).GetSafeNormal2D();
	if (ToTarget.IsNearlyZero())
	{
		return;
	}
	const float DesiredYaw = ToTarget.Rotation().Yaw;
	const float NewYaw = FMath::FixedTurn(Owner->GetActorRotation().Yaw, DesiredYaw, DegreesPerSecond * DeltaTime);
	Owner->SetActorRotation(FRotator(0.f, NewYaw, 0.f));
}

void URPGBossCombatComponent::TickCombatState(float DeltaTime)
{
	AActor* Owner = GetOwner();
	URPGCombatComponent* Combat = GetCombat();
	if (!Owner || !Combat)
	{
		return;
	}

	for (float& Cooldown : CooldownRemaining)
	{
		Cooldown = FMath::Max(0.f, Cooldown - DeltaTime);
	}

	AActor* Current = Target.Get();
	const URPGCombatComponent* TargetCombat = Current ? Current->FindComponentByClass<URPGCombatComponent>() : nullptr;
	const bool bTargetAlive = Current && (!TargetCombat || !TargetCombat->IsDead());
	const ERPGCombatState CombatState = Combat->GetState();

	if (bAttackInProgress)
	{
		const bool bStillAttacking = CombatState == ERPGCombatState::Attacking
			|| CombatState == ERPGCombatState::Recovery || CombatState == ERPGCombatState::ComboWindow;
		if (bStillAttacking)
		{
			const URPGBossAttackData* Data = Attacks.IsValidIndex(CurrentAttackIndex) ? Attacks[CurrentAttackIndex].Get() : nullptr;
			if (!bHitWindowSeen)
			{
				if (Combat->IsHitWindowOpen())
				{
					// Committed: from here the boss no longer turns. A lunge launches now.
					bHitWindowSeen = true;
					if (Data && Data->LungeSpeed > 0.f)
					{
						if (ACharacter* Character = Cast<ACharacter>(Owner))
						{
							Character->LaunchCharacter(Owner->GetActorForwardVector() * Data->LungeSpeed, true, false);
						}
					}
				}
				else if (Data && bTargetAlive && CombatState == ERPGCombatState::Attacking)
				{
					TurnToward(Current->GetActorLocation(), Data->TrackingTurnRate, DeltaTime);
				}
			}
			return;
		}

		// The attack ended, or was interrupted (stagger, death).
		bAttackInProgress = false;
		const URPGBossAttackData* Finished = Attacks.IsValidIndex(CurrentAttackIndex) ? Attacks[CurrentAttackIndex].Get() : nullptr;
		const float Pause = (CombatState == ERPGCombatState::Locomotion && Finished) ? Finished->RecoveryPause : 0.f;
		DecisionTimer = Pause + RandomReactionDelay();
	}

	// Staggered or dead: nothing to decide until control returns.
	if (CombatState != ERPGCombatState::Locomotion || !bTargetAlive)
	{
		return;
	}

	TurnToward(Current->GetActorLocation(), IdleTurnRate, DeltaTime);

	DecisionTimer -= DeltaTime;
	if (DecisionTimer > 0.f)
	{
		return;
	}

	const FVector ToTarget = Current->GetActorLocation() - Owner->GetActorLocation();
	const FVector ToTarget2D = ToTarget.GetSafeNormal2D();

	FRPGAttackSelectionContext Context;
	Context.Distance = ToTarget.Size2D();
	Context.AngleDegrees = FMath::RadiansToDegrees(FMath::Acos(FMath::Clamp(
		FVector::DotProduct(Owner->GetActorForwardVector().GetSafeNormal2D(), ToTarget2D), -1.f, 1.f)));
	Context.Phase = CurrentPhase;
	Context.LastAttackIndex = LastAttackIndex;
	Context.ConsecutiveRepeats = ConsecutiveRepeats;

	const int32 Choice = ChooseAttack(Attacks, CooldownRemaining, Context, Random.FRand());
	if (Choice != INDEX_NONE)
	{
		ExecuteAttack(Choice);
	}
	else if (Context.Distance > PreferredDistance)
	{
		// Nothing allowed from here: close the distance.
		if (APawn* Pawn = Cast<APawn>(Owner))
		{
			Pawn->AddMovementInput(ToTarget2D, 1.f);
		}
	}
}

void URPGBossCombatComponent::ExecuteAttack(int32 Index)
{
	URPGCombatComponent* Combat = GetCombat();
	const URPGBossAttackData* Data = Attacks.IsValidIndex(Index) ? Attacks[Index].Get() : nullptr;
	if (!Combat || !Data || !Combat->StartCustomAttack(Data->Attack))
	{
		return;
	}

	CooldownRemaining.SetNumZeroed(Attacks.Num());
	CooldownRemaining[Index] = Data->Cooldown;

	if (Index == LastAttackIndex)
	{
		++ConsecutiveRepeats;
	}
	else
	{
		LastAttackIndex = Index;
		ConsecutiveRepeats = 1;
	}

	CurrentAttackIndex = Index;
	bAttackInProgress = true;
	bHitWindowSeen = false;

	if (const AActor* Current = Target.Get())
	{
		UE_LOG(LogOneBossFight, Log, TEXT("%s attack '%s' (phase %d, distance %.0f)"), *GetNameSafe(GetOwner()),
			*Data->AttackName.ToString(), CurrentPhase, FVector::Dist2D(GetOwner()->GetActorLocation(), Current->GetActorLocation()));
	}

#if ENABLE_DRAW_DEBUG
	// rpg.Combat.Debug 1: show the attack's reach as an arc on the ground for the telegraph.
	const IConsoleVariable* DebugVar = IConsoleManager::Get().FindConsoleVariable(TEXT("rpg.Combat.Debug"));
	if (DebugVar && DebugVar->GetInt() > 0 && GetWorld())
	{
		const AActor* Owner = GetOwner();
		const FVector Base = Owner->GetActorLocation() - FVector(0.f, 0.f, 90.f);
		DrawDebugCircleArc(GetWorld(), Base, Data->MaxRange, Owner->GetActorForwardVector(),
			FMath::DegreesToRadians(Data->MaxAngle), 24, FColor::Red, false, 1.5f, 0, 3.f);
		DrawDebugString(GetWorld(), Base + FVector(0.f, 0.f, 40.f), Data->AttackName.ToString(), nullptr, FColor::White, 1.5f);
	}
#endif
}
