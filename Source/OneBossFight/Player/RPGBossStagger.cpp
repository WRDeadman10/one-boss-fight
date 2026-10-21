// Copyright One Boss Fight. All Rights Reserved.

#include "Player/RPGBossStagger.h"
#include "Player/RPGBossEncounter.h"
#include "Player/RPGBossInterrupt.h"
#include "Player/RPGBossPhases.h"
#include "Player/RPGBossPosture.h"
#include "Pack/RPGBlueprintCall.h"
#include "AIController.h"
#include "Animation/AnimInstance.h"
#include "Animation/AnimMontage.h"
#include "BrainComponent.h"
#include "Components/SkeletalMeshComponent.h"
#include "Engine/World.h"
#include "GameFramework/Character.h"
#include "GameFramework/CharacterMovementComponent.h"
#include "UObject/UnrealType.h"

DEFINE_LOG_CATEGORY_STATIC(LogRPGStagger, Log, All);

using namespace RPGPack;

namespace
{
	constexpr const TCHAR* HealthTag = TEXT("Attribute.Health");
	constexpr const TCHAR* PoiseTag = TEXT("Attribute.Poise");

	UObject* FindControllerComponent(AController* Controller, const TCHAR* ClassName)
	{
		if (!Controller)
		{
			return nullptr;
		}
		TInlineComponentArray<UActorComponent*> Components(Controller);
		for (UActorComponent* Component : Components)
		{
			if (Component && Component->GetClass()->GetName() == ClassName)
			{
				return Component;
			}
		}
		return nullptr;
	}
}

URPGBossStagger::URPGBossStagger()
{
	PrimaryComponentTick.bCanEverTick = true;
	PrimaryComponentTick.bStartWithTickEnabled = true;
	PrimaryComponentTick.TickInterval = 0.f;

	FallMontage = TSoftObjectPtr<UAnimMontage>(FSoftObjectPath(TEXT("/Game/AdvancedARPGCombat/MeleeCombatSystem/Animations/2handed/KnockdownStart_Anim_Montage.KnockdownStart_Anim_Montage")));
	GetUpMontage = TSoftObjectPtr<UAnimMontage>(FSoftObjectPath(TEXT("/Game/AdvancedARPGCombat/MeleeCombatSystem/Animations/2handed/Knockdown_Getup_Anim_Montage.Knockdown_Getup_Anim_Montage")));
	ImmunityEffect = TSoftClassPtr<UObject>(FSoftObjectPath(TEXT("/Game/AdvancedARPGCombat/MeleeCombatSystem/Blueprints/GameplayEffects/GE_HitStunImmune.GE_HitStunImmune_C")));
}

UAnimInstance* URPGBossStagger::GetAnimInstance() const
{
	const ACharacter* Character = Cast<ACharacter>(GetOwner());
	return Character && Character->GetMesh() ? Character->GetMesh()->GetAnimInstance() : nullptr;
}

void URPGBossStagger::TickComponent(float DeltaTime, ELevelTick TickType, FActorComponentTickFunction* ThisTickFunction)
{
	Super::TickComponent(DeltaTime, TickType, ThisTickFunction);
	const UWorld* World = GetWorld();
	if (!World)
	{
		return;
	}
	const double Now = World->GetTimeSeconds();
	if (!CachedHitStun.IsValid())
	{
		CachedHitStun = FindAbilityByClassName(GetOwner(), HitStunAbilityClassName);
	}
	UObject* HitStun = CachedHitStun.Get();
	const bool bActive = HitStun && IsAbilityInstanceActive(HitStun);

	if (Phase == EPhase::Idle)
	{
		if (bActive && !bWasActive)
		{
			// The pack's poise gate started its hit stun: that is the break request. It goes through the same gate as the test hooks.
			bWasActive = bActive;
			RequestBreak(false);
			return;
		}
		bWasActive = bActive;
		return;
	}
	bWasActive = bActive;

	UAnimInstance* Anim = GetAnimInstance();
	UAnimMontage* Fall = FallMontage.Get();
	UAnimMontage* GetUp = GetUpMontage.Get();
	const double Elapsed = Now - PhaseStart;
	ApplyCritical();
	if (Phase == EPhase::Idle) // the boss died: ApplyCritical ended the stagger
	{
		return;
	}
	if (Phase == EPhase::Down)
	{
		if (Anim && Fall && !bFrozen && Anim->Montage_IsPlaying(Fall) && Anim->Montage_GetPosition(Fall) >= FreezeAtPosition)
		{
			Anim->Montage_Pause(Fall); // stay on the ground
			bFrozen = true;
		}
		if (Elapsed >= StaggerSeconds)
		{
			if (Anim && GetUp)
			{
				Anim->Montage_Play(GetUp, 1.f);
			}
			Phase = EPhase::GetUp;
			PhaseStart = Now;
			UE_LOG(LogRPGStagger, Log, TEXT("%s: down for %.2f s, %d critical hits, getting up"), *GetOwner()->GetName(), Elapsed, CriticalHitCount);
		}
		return;
	}
	// Getting up
	if (!Anim || !GetUp || !Anim->Montage_IsPlaying(GetUp) || Elapsed > GetUp->GetPlayLength() + 0.5)
	{
		EndStagger(true);
	}
}

bool URPGBossStagger::EndPackFlinch()
{
	UObject* Asc = FindComponentByClassName(GetOwner(), TEXT("BP_AdvancedAbilitySystemComponent_C"));
	UObject* HitStun = CachedHitStun.Get();
	if (!Asc || !HitStun)
	{
		return false;
	}
	const bool bWasPlaying = IsAbilityInstanceActive(HitStun);
	CallBlueprintFunction(Asc, TEXT("End Ability"),
		[&](UFunction& F, uint8* P)
		{
			if (const FObjectProperty* Object = CastField<FObjectProperty>(F.FindPropertyByName(TEXT("AbilityToEnd"))))
			{
				Object->SetObjectPropertyValue(Object->ContainerPtrToValuePtr<void>(P), HitStun);
			}
		},
		[](UFunction&, uint8*) {});
	return bWasPlaying;
}

float URPGBossStagger::GetCooldownRemaining() const
{
	return GetWorld() ? static_cast<float>(FMath::Max(0.0, CooldownEnd - GetWorld()->GetTimeSeconds())) : 0.f;
}

int32 URPGBossStagger::GetDroppedBreakCount(const FString& Reason) const
{
	if (Reason == TEXT("transition")) { return DroppedTransition; }
	if (Reason == TEXT("dead")) { return DroppedDead; }
	if (Reason == TEXT("dormant")) { return DroppedDormant; }
	if (Reason == TEXT("staggered")) { return DroppedStaggered; }
	if (Reason == TEXT("cooldown")) { return DroppedCooldown; }
	return 0;
}

RPGBossRules::EBreakResult URPGBossStagger::RequestBreak(bool bIgnoreCooldown)
{
	using namespace RPGBossRules;
	const UWorld* World = GetWorld();
	const double Now = World ? World->GetTimeSeconds() : 0.0;
	FFlags Flags;
	double Health = 1.0;
	Flags.bDead = ReadAttribute(GetOwner(), HealthTag, false, Health) && Health <= 0.0;
	const URPGBossEncounter* Encounter = GetOwner()->FindComponentByClass<URPGBossEncounter>();
	const URPGBossPhases* Phases = GetOwner()->FindComponentByClass<URPGBossPhases>();
	Flags.bDormant = Encounter && Encounter->IsDormant();
	Flags.bTransition = Phases && Phases->IsInTransition();
	Flags.bStaggered = Phase != EPhase::Idle;
	Flags.bCooldown = Now < CooldownEnd;
	const EBreakResult Result = ResolveBreak(Flags, bIgnoreCooldown);
	LastBreakResult = Name(Result);
	switch (Result)
	{
	case EBreakResult::Started:
		StartStagger();
		return Result;
	case EBreakResult::Dead:
		++DroppedDead;
		EndPackFlinch(); // no hit stun after a lethal hit (Freeze 1269): the flinch must not play over the death clip
		break;
	case EBreakResult::Dormant:
		++DroppedDormant;
		break;
	case EBreakResult::Transition:
		++DroppedTransition;
		if (EndPackFlinch())
		{
			UE_LOG(LogRPGStagger, Warning, TEXT("%s: the pack flinch was active during the phase transition (the immunity effect did not hold), ended"), *GetOwner()->GetName());
		}
		break;
	case EBreakResult::AlreadyStaggered:
		++DroppedStaggered;
		break;
	case EBreakResult::Cooldown:
		++DroppedCooldown;
		break;
	}
	UE_LOG(LogRPGStagger, Log, TEXT("%s: stance break dropped: %s%s"), *GetOwner()->GetName(), Name(Result), Result == EBreakResult::Cooldown ? *FString::Printf(TEXT(" (%.1f s left)"), CooldownEnd - Now) : TEXT(""));
	return Result;
}

void URPGBossStagger::StartStagger()
{
	const double Now = GetWorld()->GetTimeSeconds();
	Phase = EPhase::Down;
	PhaseStart = Now;
	bFrozen = false;
	++StaggerCount;
	CriticalHitCount = 0;
	bRiposteUsed = false;
	RiposteArmedUntil = -1.0;

	// Freeze 17.3 items 2 and 3: the break disables the boss's own attack windows, blade, wave and projectiles, and records what it cancelled.
	RPGBossInterrupt::CancelOffence(GetOwner(), TEXT("stance break"));
	if (bHoldPostureAtZero)
	{
		if (URPGBossPosture* Posture = GetOwner()->FindComponentByClass<URPGBossPosture>())
		{
			Posture->BeginHold(URPGBossPosture::EHold::Zero);
		}
	}

	UObject* Asc = FindComponentByClassName(GetOwner(), TEXT("BP_AdvancedAbilitySystemComponent_C"));
	// The flinch ability would end its montage under ours: end it first.
	EndPackFlinch();
	// Temporary immunity (4 s) so further hits do not replay a flinch over the pose.
	if (Asc)
	{
		if (UClass* Effect = ImmunityEffect.LoadSynchronous())
		{
			CallBlueprintFunction(Asc, TEXT("Apply Gameplay Effect by Class"),
				[&](UFunction& F, uint8* P)
				{
					if (const FClassProperty* ClassProp = CastField<FClassProperty>(F.FindPropertyByName(TEXT("GameplayEffectClass"))))
					{
						ClassProp->SetPropertyValue_InContainer(P, Effect);
					}
					if (const FNumericProperty* Level = CastField<FNumericProperty>(F.FindPropertyByName(TEXT("Level"))))
					{
						Level->SetIntPropertyValue(Level->ContainerPtrToValuePtr<void>(P), static_cast<int64>(1));
					}
				},
				[](UFunction&, uint8*) {});
		}
	}
	HoldBehaviour();
	if (ACharacter* Character = Cast<ACharacter>(GetOwner()))
	{
		if (UCharacterMovementComponent* Movement = Character->GetCharacterMovement())
		{
			Movement->StopMovementImmediately();
		}
	}
	if (UAnimInstance* Anim = GetAnimInstance())
	{
		if (UAnimMontage* Fall = FallMontage.LoadSynchronous())
		{
			Anim->Montage_Play(Fall, 1.f); // stops whatever the boss was playing
		}
	}
	double Health = 0.0;
	LastHealth = ReadAttribute(GetOwner(), HealthTag, false, Health) ? Health : -1.0;
	UE_LOG(LogRPGStagger, Log, TEXT("%s: poise break %d, stance break for %.1f s, hits are critical x%.1f (every hit: %d)"), *GetOwner()->GetName(), StaggerCount, StaggerSeconds, CriticalMultiplier, bCriticalOnEveryHit);
}

void URPGBossStagger::EndStagger(bool bResumeBehaviour, bool bClearCooldown)
{
	const double Now = GetWorld() ? GetWorld()->GetTimeSeconds() : 0.0;
	Phase = EPhase::Idle;
	LastEndTime = Now;
	CooldownEnd = bClearCooldown ? 0.0 : Now + CooldownSeconds;
	bFrozen = false;

	if (UObject* Asc = FindComponentByClassName(GetOwner(), TEXT("BP_AdvancedAbilitySystemComponent_C")))
	{
		if (UClass* Effect = ImmunityEffect.Get())
		{
			CallBlueprintFunction(Asc, TEXT("Remove Active Gameplay Effect By Class"),
				[&](UFunction& F, uint8* P)
				{
					if (const FClassProperty* ClassProp = CastField<FClassProperty>(F.FindPropertyByName(TEXT("GameplayEffectClass"))))
					{
						ClassProp->SetPropertyValue_InContainer(P, Effect);
					}
				},
				[](UFunction&, uint8*) {});
		}
	}
	// Poise starts full again (Freeze 714): the hold ends with a refill; without the posture component the direct write is the fallback.
	URPGBossPosture* Posture = GetOwner()->FindComponentByClass<URPGBossPosture>();
	if (Posture && Posture->GetHoldName() != TEXT("None"))
	{
		Posture->EndHold(true);
	}
	else
	{
		double MaxPoise = 0.0;
		if (ReadAttribute(GetOwner(), PoiseTag, true, MaxPoise))
		{
			WriteAttribute(GetOwner(), PoiseTag, MaxPoise);
		}
	}
	if (bResumeBehaviour)
	{
		// A phase transition that crossed its threshold during the break starts now, with the behaviour still held: one hand-off, never a gap and never two montages (Freeze 770).
		URPGBossPhases* Phases = GetOwner()->FindComponentByClass<URPGBossPhases>();
		if (Phases && Phases->TryStartQueuedTransition(bBehaviourHeld))
		{
			bBehaviourHeld = false; // the phase component owns the hold now
		}
		else
		{
			ResumeBehaviour();
		}
	}
	UE_LOG(LogRPGStagger, Log, TEXT("%s: stance break over (%d critical hits), resume behaviour %d"), *GetOwner()->GetName(), CriticalHitCount, bResumeBehaviour);
}

bool URPGBossStagger::IsRiposteArmed() const
{
	const UWorld* World = GetWorld();
	return Phase == EPhase::Down && !bRiposteUsed && World && World->GetTimeSeconds() <= RiposteArmedUntil;
}

const TCHAR* URPGBossStagger::CheckRiposte(const AActor* Player, double& OutDistance) const
{
	const AActor* Boss = GetOwner();
	OutDistance = 0.0;
	if (!GetWorld() || !Boss || !Player)
	{
		return TEXT("no boss or player");
	}
	if (Phase != EPhase::Down)
	{
		return TEXT("boss is not down");
	}
	if (bRiposteUsed)
	{
		return TEXT("riposte already used in this stance break");
	}
	const FVector ToPlayer = (Player->GetActorLocation() - Boss->GetActorLocation()) * FVector(1.f, 1.f, 0.f);
	OutDistance = ToPlayer.Size();
	if (OutDistance > RiposteRange)
	{
		return TEXT("too far");
	}
	const FVector Direction = ToPlayer.GetSafeNormal();
	const FVector BossForward = (Boss->GetActorForwardVector() * FVector(1.f, 1.f, 0.f)).GetSafeNormal();
	if (FVector::DotProduct(BossForward, Direction) < FMath::Cos(FMath::DegreesToRadians(RiposteConeDegrees * 0.5f)))
	{
		return TEXT("not in front of the boss");
	}
	const FVector PlayerForward = (Player->GetActorForwardVector() * FVector(1.f, 1.f, 0.f)).GetSafeNormal();
	if (FVector::DotProduct(PlayerForward, -Direction) < FMath::Cos(FMath::DegreesToRadians(RiposteFacingDegrees * 0.5f)))
	{
		return TEXT("player not facing the boss");
	}
	return nullptr;
}

bool URPGBossStagger::IsRiposteAvailable(const AActor* Player) const
{
	double Distance = 0.0;
	return CheckRiposte(Player, Distance) == nullptr;
}

bool URPGBossStagger::TryRiposte(const AActor* Player)
{
	double Distance = 0.0;
	if (const TCHAR* Reason = CheckRiposte(Player, Distance))
	{
		++RiposteRejectCount;
		LastRiposteResult = Reason;
		UE_LOG(LogRPGStagger, Log, TEXT("riposte rejected: %s"), Reason);
		return false;
	}
	RiposteArmedUntil = GetWorld()->GetTimeSeconds() + RiposteArmSeconds;
	LastRiposteResult = TEXT("accepted");
	UE_LOG(LogRPGStagger, Log, TEXT("riposte accepted at %.0f cm, the next hit within %.1f s is critical x%.1f"), Distance, RiposteArmSeconds, CriticalMultiplier);
	return true;
}

FString URPGBossStagger::ForceBreakForTest()
{
	bWasActive = true; // the pack's hit stun edge must not be read as a second request
	return RPGBossRules::Name(RequestBreak(true));
}

FString URPGBossStagger::TryBreakForTest()
{
	bWasActive = true;
	return RPGBossRules::Name(RequestBreak(false));
}

void URPGBossStagger::AbortStagger()
{
	// A reset leaves nothing behind (Freeze 18.3 line 791): the cooldown, the riposte and the posture hold go in every case, also when no break is running.
	CooldownEnd = 0.0;
	RiposteArmedUntil = -1.0;
	bRiposteUsed = false;
	if (Phase != EPhase::Idle)
	{
		if (UAnimInstance* Anim = GetAnimInstance())
		{
			Anim->Montage_Stop(0.1f, FallMontage.Get());
			Anim->Montage_Stop(0.1f, GetUpMontage.Get());
		}
		EndStagger(false, true);
		bBehaviourHeld = false; // the caller decides what the behaviour does next
	}
	if (URPGBossPosture* Posture = GetOwner()->FindComponentByClass<URPGBossPosture>())
	{
		Posture->EndHold(true);
	}
}

void URPGBossStagger::EndPlay(const EEndPlayReason::Type EndPlayReason)
{
	Phase = EPhase::Idle;
	Super::EndPlay(EndPlayReason);
}

void URPGBossStagger::ApplyCritical()
{
	double Health = 0.0;
	if (!ReadAttribute(GetOwner(), HealthTag, false, Health))
	{
		return;
	}
	if (Health <= 0.0)
	{
		UE_LOG(LogRPGStagger, Log, TEXT("%s: died during the stance break"), *GetOwner()->GetName());
		if (UAnimInstance* Anim = GetAnimInstance())
		{
			// Only our two clips: a plain Montage_Stop() would also stop the pack's death clip.
			Anim->Montage_Stop(0.1f, FallMontage.Get());
			Anim->Montage_Stop(0.1f, GetUpMontage.Get());
		}
		EndStagger(false);
		return;
	}
	if (LastHealth >= 0.0 && Health > LastHealth + 1.0)
	{
		// Health went up while the boss was down: the pack reset the encounter (the player died and respawned). Stand the boss up and hand it back to its behaviour.
		UE_LOG(LogRPGStagger, Log, TEXT("%s: health rose %.0f -> %.0f during the stance break (encounter reset), ending it"), *GetOwner()->GetName(), LastHealth, Health);
		if (UAnimInstance* Anim = GetAnimInstance())
		{
			Anim->Montage_Stop(0.2f, FallMontage.Get());
			Anim->Montage_Stop(0.2f, GetUpMontage.Get());
		}
		LastHealth = Health;
		EndStagger(true);
		return;
	}
	if (!bCriticalOnEveryHit && IsRiposteArmed() && LastHealth >= 0.0 && Health < LastHealth - 0.01)
	{
		// The riposte hit (Freeze 17.4): the multiplier applies to this hit only, once per stance break.
		const double Loss = LastHealth - Health;
		const double NewHealth = FMath::Max(0.0, Health - Loss * (CriticalMultiplier - 1.0));
		WriteAttribute(GetOwner(), HealthTag, NewHealth);
		bRiposteUsed = true;
		RiposteArmedUntil = -1.0;
		++RiposteCount;
		++CriticalHitCount;
		UE_LOG(LogRPGStagger, Log, TEXT("riposte hit: lost %.0f, took %.0f in total (health %.0f -> %.0f)"), Loss, Loss + (Health - NewHealth), LastHealth, NewHealth);
		Health = NewHealth;
	}
	if (bCriticalOnEveryHit && Phase == EPhase::Down && LastHealth >= 0.0 && Health < LastHealth - 0.01)
	{
		const double Loss = LastHealth - Health;
		const double NewHealth = FMath::Max(0.0, Health - Loss * (CriticalMultiplier - 1.0));
		WriteAttribute(GetOwner(), HealthTag, NewHealth);
		++CriticalHitCount;
		UE_LOG(LogRPGStagger, Log, TEXT("critical hit: lost %.0f, took %.0f in total (health %.0f -> %.0f)"), Loss, Loss + (Health - NewHealth), LastHealth, NewHealth);
		Health = NewHealth;
	}
	LastHealth = Health;
}

void URPGBossStagger::HoldBehaviour()
{
	const APawn* Pawn = Cast<APawn>(GetOwner());
	AAIController* Controller = Pawn ? Cast<AAIController>(Pawn->GetController()) : nullptr;
	if (!Controller)
	{
		return;
	}
	if (UObject* Manager = FindControllerComponent(Controller, TEXT("BP_BehaviorManagerComponent_C")))
	{
		CallBlueprintFunction(Manager, TEXT("StopBehaviorLogic"),
			[](UFunction& F, uint8* P)
			{
				if (const FStrProperty* Reason = CastField<FStrProperty>(F.FindPropertyByName(TEXT("Reason"))))
				{
					Reason->SetPropertyValue_InContainer(P, FString(TEXT("Stance break")));
				}
			},
			[](UFunction&, uint8*) {});
	}
	else if (Controller->BrainComponent)
	{
		Controller->BrainComponent->StopLogic(TEXT("Stance break"));
	}
	bBehaviourHeld = true;
}

void URPGBossStagger::ResumeBehaviour()
{
	const APawn* Pawn = Cast<APawn>(GetOwner());
	AAIController* Controller = Pawn ? Cast<AAIController>(Pawn->GetController()) : nullptr;
	if (!Controller || !bBehaviourHeld)
	{
		return;
	}
	if (UObject* Manager = FindControllerComponent(Controller, TEXT("BP_BehaviorManagerComponent_C")))
	{
		CallBlueprintFunction(Manager, TEXT("SetBehaviorDisabled"),
			[](UFunction& F, uint8* P)
			{
				for (TFieldIterator<FBoolProperty> It(&F); It; ++It)
				{
					if (!It->HasAnyPropertyFlags(CPF_OutParm))
					{
						It->SetPropertyValue_InContainer(P, false);
						break;
					}
				}
			},
			[](UFunction&, uint8*) {});
	}
	if (Controller->BrainComponent)
	{
		Controller->BrainComponent->RestartLogic();
	}
	bBehaviourHeld = false;
}
