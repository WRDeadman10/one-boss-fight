// Copyright One Boss Fight. All Rights Reserved.

#include "Player/RPGBossPhases.h"
#include "Player/RPGBossEncounter.h"
#include "Player/RPGHitIntake.h"
#include "Player/RPGBossInterrupt.h"
#include "Player/RPGBossClips.h"
#include "Player/RPGBossPosture.h"
#include "Player/RPGBossStagger.h"
#include "Pack/RPGBlueprintCall.h"
#include "AIController.h"
#include "Animation/AnimInstance.h"
#include "Animation/AnimMontage.h"
#include "BrainComponent.h"
#include "Components/SkeletalMeshComponent.h"
#include "Engine/World.h"
#include "GameFramework/Character.h"
#include "GameFramework/CharacterMovementComponent.h"
#include "Kismet/GameplayStatics.h"
#include "UObject/UnrealType.h"

DEFINE_LOG_CATEGORY_STATIC(LogRPGPhases, Log, All);

using namespace RPGPack;

namespace
{
	constexpr const TCHAR* HealthTag = TEXT("Attribute.Health");
	constexpr const TCHAR* AttackTag = TEXT("Attribute.Attack");

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

URPGBossPhases::URPGBossPhases()
{
	PrimaryComponentTick.bCanEverTick = true;
	PrimaryComponentTick.bStartWithTickEnabled = true;
	PrimaryComponentTick.TickInterval = 0.1f;

	RoarClip = TSoftObjectPtr<UAnimSequence>(FSoftObjectPath(TEXT("/Game/OneBossFight/Boss01/Animations/AN_Boss01_PhaseRoar.AN_Boss01_PhaseRoar")));
	TransitionMontage = TSoftObjectPtr<UAnimMontage>(FSoftObjectPath(TEXT("/Game/AdvancedARPGCombat/MeleeCombatSystem/Animations/2handed/Ability_R_Intro_Anim_Montage.Ability_R_Intro_Anim_Montage")));
	ImmunityEffect = TSoftClassPtr<UObject>(FSoftObjectPath(TEXT("/Game/AdvancedARPGCombat/MeleeCombatSystem/Blueprints/GameplayEffects/GE_HitStunImmune.GE_HitStunImmune_C")));
	FireballAbility = TSoftClassPtr<UObject>(FSoftObjectPath(TEXT("/Game/AdvancedARPGCombat/MagicCombatSystem/Blueprints/AI/ExampleMagicEnemy/GA_Fireball_Enemy.GA_Fireball_Enemy_C")));
}

void URPGBossPhases::BeginPlay()
{
	Super::BeginPlay();
	LoadedImmunityEffect = ImmunityEffect.LoadSynchronous();
	LoadedRoarClip = RoarClip.LoadSynchronous();
	LoadedTransitionMontage = TransitionMontage.LoadSynchronous();
	if (const ACharacter* Character = Cast<ACharacter>(GetOwner()))
	{
		BaseWalkSpeed = Character->GetCharacterMovement() ? Character->GetCharacterMovement()->MaxWalkSpeed : 0.f;
	}
	// When a hit breaks posture and crosses the threshold in the same frame, the break must be seen first (the transition is then queued behind it, Freeze 1201): the stance break component ticks before this one.
	// Since Gate 3 the pool's break request is made one frame after the pack's hit event (RPGHitIntake finishes its record on the next tick), so a threshold crossing also waits for the intake (TickComponent).
	if (const URPGBossStagger* Stagger = GetOwner()->FindComponentByClass<URPGBossStagger>())
	{
		AddTickPrerequisiteComponent(const_cast<URPGBossStagger*>(Stagger));
	}
}

RPGBossRules::ETransitionResult URPGBossPhases::ResolveNow() const
{
	const AActor* Owner = GetOwner();
	const URPGBossEncounter* Encounter = Owner->FindComponentByClass<URPGBossEncounter>();
	const URPGBossStagger* Stagger = Owner->FindComponentByClass<URPGBossStagger>();
	RPGBossRules::FFlags Flags;
	Flags.bDormant = Encounter && Encounter->IsDormant();
	Flags.bStaggered = Stagger && Stagger->IsStaggered();
	Flags.bPhaseTwo = bPhaseTwo;
	Flags.bTransition = bTransition;
	double Health = 0.0, Max = 0.0;
	if (!ReadAttribute(Owner, HealthTag, false, Health) || !ReadAttribute(Owner, HealthTag, true, Max))
	{
		return RPGBossRules::ETransitionResult::NotReady; // unreadable: treated as not crossed
	}
	return RPGBossRules::ResolveTransition(Flags, Health, Max, PhaseTwoHealthFraction);
}

bool URPGBossPhases::IsTransitionQueued() const
{
	return ResolveNow() == RPGBossRules::ETransitionResult::QueuedBehindStagger;
}

bool URPGBossPhases::TryStartQueuedTransition(bool bBehaviourAlreadyHeld)
{
	if (ResolveNow() != RPGBossRules::ETransitionResult::Start)
	{
		return false;
	}
	++QueuedStarts;
	UE_LOG(LogRPGPhases, Log, TEXT("%s: the transition queued behind the stance break starts now (behaviour already held: %d)"), *GetOwner()->GetName(), bBehaviourAlreadyHeld ? 1 : 0);
	StartTransition(bBehaviourAlreadyHeld);
	return true;
}

void URPGBossPhases::TickComponent(float DeltaTime, ELevelTick TickType, FActorComponentTickFunction* ThisTickFunction)
{
	Super::TickComponent(DeltaTime, TickType, ThisTickFunction);
	const UWorld* World = GetWorld();
	if (!World)
	{
		return;
	}
	const double Now = World->GetTimeSeconds();
	AActor* Owner = GetOwner();
	if (bLockLeapUntilPhaseTwo && !bPhaseTwo && !bLeapBlocked)
	{
		SetLeapBlocked(true); // phase one, and again after a reset
	}
	const URPGBossEncounter* Encounter = Owner->FindComponentByClass<URPGBossEncounter>();
	const URPGBossStagger* Stagger = Owner->FindComponentByClass<URPGBossStagger>();
	const bool bDormant = Encounter && Encounter->IsDormant();
	const bool bStaggered = Stagger && Stagger->IsStaggered();

	if (bTransition)
	{
		if (Now >= TransitionEnd)
		{
			FinishTransition();
		}
		return;
	}
	if (bDormant)
	{
		return;
	}
	double Health = 0.0, Max = 0.0;
	if (!ReadAttribute(Owner, HealthTag, false, Health) || !ReadAttribute(Owner, HealthTag, true, Max) || Max <= 0.0 || Health <= 0.0)
	{
		return;
	}
	if (!bPhaseTwo)
	{
		// A hit of the player that is still on its way into the posture pool (its record is finished next frame) may break the boss in the frame it crosses the threshold: the break must be seen first, so wait for it
		// (Freeze 21 and 1201: the crossing is then queued behind the break instead of starting the roar over a break that was earned).
		if (const APawn* Player = UGameplayStatics::GetPlayerPawn(World, 0))
		{
			if (const URPGHitIntake* Intake = Player->FindComponentByClass<URPGHitIntake>())
			{
				if (Intake->HasPendingRecords())
				{
					return;
				}
			}
		}
		// The Freeze 21 rule: a crossing during a stance break is queued (it starts from the end of the break, TryStartQueuedTransition), otherwise it starts now.
		if (ResolveNow() == RPGBossRules::ETransitionResult::Start)
		{
			StartTransition(false);
		}
		return;
	}
	// The pack's behaviour sets MaxWalkSpeed on every state change (walk, sprint): scale whatever it sets.
	if (ACharacter* Character = Cast<ACharacter>(Owner))
	{
		if (UCharacterMovementComponent* Movement = Character->GetCharacterMovement())
		{
			if (!FMath::IsNearlyEqual(Movement->MaxWalkSpeed, LastSetSpeed, 0.5f))
			{
				LastSetSpeed = Movement->MaxWalkSpeed * MovementScale;
				Movement->MaxWalkSpeed = LastSetSpeed;
			}
		}
	}
	if (!bStaggered && bFireballEnabled)
	{
		TryFireball(Now);
	}
}

bool URPGBossPhases::SetLeapBlocked(bool bBlocked)
{
	UObject* Asc = FindComponentByClassName(GetOwner(), TEXT("BP_AdvancedAbilitySystemComponent_C"));
	if (!Asc)
	{
		return false;
	}
	const FGameplayTag Tag = FGameplayTag::RequestGameplayTag(LeapAbilityTag, false);
	if (!Tag.IsValid())
	{
		UE_LOG(LogRPGPhases, Warning, TEXT("leap ability tag %s is not a registered tag"), *LeapAbilityTag.ToString());
		return false;
	}
	const bool bCalled = CallBlueprintFunction(Asc, bBlocked ? TEXT("AddBlockedAbilityTags") : TEXT("RemoveBlockedAbilityTags"),
		[&](UFunction& F, uint8* P)
		{
			if (const FStructProperty* Container = CastField<FStructProperty>(F.FindPropertyByName(bBlocked ? TEXT("TagsToAdd") : TEXT("TagsToRemove"))))
			{
				Container->ContainerPtrToValuePtr<FGameplayTagContainer>(P)->AddTag(Tag);
			}
		},
		[](UFunction&, uint8*) {});
	if (bCalled)
	{
		bLeapBlocked = bBlocked;
		UE_LOG(LogRPGPhases, Log, TEXT("%s: leap %s (%s)"), *GetOwner()->GetName(), bBlocked ? TEXT("blocked until phase two") : TEXT("unlocked"), *LeapAbilityTag.ToString());
	}
	return bCalled;
}

void URPGBossPhases::RemoveImmunity()
{
	if (bImmunityApplied)
	{
		bImmunityApplied = false;
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
	}
}

void URPGBossPhases::StartTransition(bool bHeldAlready)
{
	const UWorld* World = GetWorld();
	bPhaseTwo = true;
	bTransition = true;
	++PhaseTwoCount;
	LastTransitionStart = World->GetTimeSeconds();
	TransitionEnd = LastTransitionStart + TransitionSeconds;
	// Freeze 18.1 (line 766): the transition blocks attack selection, clears active windows and pending punishes, and pauses posture.
	RPGBossInterrupt::CancelOffence(GetOwner(), TEXT("phase transition"));
	if (bPausePostureInTransition)
	{
		if (URPGBossPosture* Posture = GetOwner()->FindComponentByClass<URPGBossPosture>())
		{
			Posture->BeginHold(URPGBossPosture::EHold::Pinned);
		}
	}
	if (bHeldAlready)
	{
		bHeld = true; // the stance break that just ended still holds the behaviour: this transition takes the hold over
	}
	else
	{
		HoldBehaviour();
	}
	if (UObject* Asc = FindComponentByClassName(GetOwner(), TEXT("BP_AdvancedAbilitySystemComponent_C")))
	{
		if (UClass* Effect = ImmunityEffect.LoadSynchronous())
		{
			bImmunityApplied = true;
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
		else
		{
			UE_LOG(LogRPGPhases, Warning, TEXT("%s: the hit stun immunity effect class did not load: the roar can be interrupted"), *GetOwner()->GetName());
		}
	}
	if (const ACharacter* Character = Cast<ACharacter>(GetOwner()))
	{
		if (UCharacterMovementComponent* Movement = Character->GetCharacterMovement())
		{
			Movement->StopMovementImmediately();
		}
		if (UAnimInstance* Anim = Character->GetMesh() ? Character->GetMesh()->GetAnimInstance() : nullptr)
		{
			UAnimSequence* Clip = bUseRoarClip ? RoarClip.LoadSynchronous() : nullptr;
			UAnimMontage* Roar = Clip ? nullptr : TransitionMontage.LoadSynchronous();
			if (Clip && RPGBossClips::Play(Character, Clip, 0.15f, 0.25f))
			{
				RoarSourceName = Clip->GetName(); // the project's own roar (frame 0 is the combat idle, the clip is 1.8 s like TransitionSeconds)
			}
			else if (Roar || (Roar = TransitionMontage.LoadSynchronous()))
			{
				Anim->Montage_Play(Roar, 1.f);
				RoarSourceName = Roar->GetName();
			}
			else
			{
				RoarSourceName = TEXT("none");
				UE_LOG(LogRPGPhases, Warning, TEXT("%s: neither the roar clip nor the roar montage loaded, the transition runs silent for %.1f s"), *GetOwner()->GetName(), TransitionSeconds);
			}
		}
	}
	UE_LOG(LogRPGPhases, Log, TEXT("%s: phase two begins (transition %.1f s)"), *GetOwner()->GetName(), TransitionSeconds);
}

void URPGBossPhases::FinishTransition()
{
	bTransition = false;
	// The protection ends with the roar (Freeze 771); the posture pool stays at the pinned value and regenerates RegenDelaySeconds from now.
	RemoveImmunity();
	if (URPGBossPosture* Posture = GetOwner()->FindComponentByClass<URPGBossPosture>())
	{
		Posture->EndHold(false);
	}
	double Health = 1.0;
	if (ReadAttribute(GetOwner(), HealthTag, false, Health) && Health <= 0.0)
	{
		// Death wins (Freeze 18.2): a boss that died during the roar gets no buffs and its behaviour is not resumed.
		UE_LOG(LogRPGPhases, Log, TEXT("%s: died during the phase transition, no phase two buffs"), *GetOwner()->GetName());
		return;
	}
	ApplyPhaseTwoBuffs();
	if (bLockLeapUntilPhaseTwo && bLeapBlocked)
	{
		SetLeapBlocked(false); // the transition has finished: the leap becomes selectable
	}
	ResumeBehaviour();
	const double Now = GetWorld()->GetTimeSeconds();
	NextFireball = Now + FMath::RandRange(FireballCooldown.X, FMath::Max(FireballCooldown.X, FireballCooldown.Y));
	UE_LOG(LogRPGPhases, Log, TEXT("%s: phase two: speed x%.2f, attack rate x%.2f, damage x%.2f, first fireball in %.1f s"), *GetOwner()->GetName(), MovementScale, AttackRateScale, DamageScale, NextFireball - Now);
}

void URPGBossPhases::ApplyPhaseTwoBuffs()
{
	if (bBuffsApplied)
	{
		return;
	}
	bBuffsApplied = true;
	if (const ACharacter* Character = Cast<ACharacter>(GetOwner()))
	{
		if (UCharacterMovementComponent* Movement = Character->GetCharacterMovement())
		{
			LastSetSpeed = Movement->MaxWalkSpeed * MovementScale;
			Movement->MaxWalkSpeed = LastSetSpeed;
		}
	}
	ScaleAttackRates(AttackRateScale);
	double Attack = 0.0;
	if (ReadAttribute(GetOwner(), AttackTag, false, Attack) && Attack > 0.0)
	{
		AppliedAttack = Attack * (DamageScale - 1.0);
		WriteAttribute(GetOwner(), AttackTag, Attack + AppliedAttack);
	}
}

void URPGBossPhases::RemovePhaseTwoBuffs()
{
	if (!bBuffsApplied)
	{
		return;
	}
	bBuffsApplied = false;
	if (const ACharacter* Character = Cast<ACharacter>(GetOwner()))
	{
		if (UCharacterMovementComponent* Movement = Character->GetCharacterMovement())
		{
			Movement->MaxWalkSpeed = Movement->MaxWalkSpeed / MovementScale;
		}
	}
	LastSetSpeed = 0.f;
	ScaleAttackRates(1.f / AttackRateScale);
	double Attack = 0.0;
	if (AppliedAttack > 0.0 && ReadAttribute(GetOwner(), AttackTag, false, Attack))
	{
		WriteAttribute(GetOwner(), AttackTag, FMath::Max(0.0, Attack - AppliedAttack));
	}
	AppliedAttack = 0.0;
}

void URPGBossPhases::ScaleAttackRates(float Factor)
{
	UObject* Asc = FindComponentByClassName(GetOwner(), TEXT("BP_AdvancedAbilitySystemComponent_C"));
	const FArrayProperty* Created = Asc ? FindFProperty<FArrayProperty>(Asc->GetClass(), TEXT("CreatedAbilities")) : nullptr;
	const FObjectProperty* Inner = Created ? CastField<FObjectProperty>(Created->Inner) : nullptr;
	if (!Inner)
	{
		return;
	}
	int32 Scaled = 0;
	FScriptArrayHelper Abilities(Created, Created->ContainerPtrToValuePtr<void>(Asc));
	for (int32 Index = 0; Index < Abilities.Num(); ++Index)
	{
		UObject* Ability = Inner->GetObjectPropertyValue(Abilities.GetRawPtr(Index));
		const FString Name = Ability ? Ability->GetClass()->GetName() : FString();
		if (!Ability || !Name.StartsWith(AttackAbilityPrefix) || Name.Contains(TEXT("HitStun")) || Name.Contains(TEXT("EnterCombat")) || Name.Contains(TEXT("ExitCombat")) || Name.Contains(TEXT("TurnInPlace")))
		{
			continue;
		}
		// Every array of the pack's F_AbilityMontage structs on the ability (AttackMontages): scale the play rate field of each element.
		for (TFieldIterator<FArrayProperty> It(Ability->GetClass()); It; ++It)
		{
			const FStructProperty* Element = CastField<FStructProperty>(It->Inner);
			if (!Element || !Element->Struct || !Element->Struct->GetName().Contains(TEXT("AbilityMontage")))
			{
				continue;
			}
			const FNumericProperty* RateField = nullptr;
			for (TFieldIterator<FProperty> Field(Element->Struct); Field; ++Field)
			{
				if (const FNumericProperty* Number = CastField<FNumericProperty>(*Field))
				{
					if (Number->IsFloatingPoint() && Number->GetName().StartsWith(TEXT("PlayRate")))
					{
						RateField = Number;
						break;
					}
				}
			}
			if (!RateField)
			{
				continue;
			}
			FScriptArrayHelper Entries(*It, It->ContainerPtrToValuePtr<void>(Ability));
			for (int32 E = 0; E < Entries.Num(); ++E)
			{
				void* Value = RateField->ContainerPtrToValuePtr<void>(Entries.GetRawPtr(E));
				RateField->SetFloatingPointPropertyValue(Value, RateField->GetFloatingPointPropertyValue(Value) * Factor);
				++Scaled;
			}
		}
	}
	UE_LOG(LogRPGPhases, Log, TEXT("%s: scaled %d attack montage play rates by x%.3f"), *GetOwner()->GetName(), Scaled, Factor);
}

void URPGBossPhases::TryFireball(double Now)
{
	if (Now < NextFireball)
	{
		return;
	}
	const APawn* Player = UGameplayStatics::GetPlayerPawn(this, 0);
	const ACharacter* Character = Cast<ACharacter>(GetOwner());
	UAnimInstance* Anim = Character && Character->GetMesh() ? Character->GetMesh()->GetAnimInstance() : nullptr;
	if (!Player || !Anim)
	{
		return;
	}
	const double Distance = FVector::Dist2D(Character->GetActorLocation(), Player->GetActorLocation());
	if (Distance < FireballMinRange || Distance > FireballMaxRange || Anim->IsAnyMontagePlaying())
	{
		NextFireball = Now + 0.5; // try again soon
		return;
	}
	UClass* Ability = FireballAbility.LoadSynchronous();
	UObject* Asc = FindComponentByClassName(GetOwner(), TEXT("BP_AdvancedAbilitySystemComponent_C"));
	if (!Ability || !Asc)
	{
		NextFireball = Now + 5.0; // the class did not load (a package that is not cooked): back off instead of a synchronous load on every tick
		UE_LOG(LogRPGPhases, Warning, TEXT("%s: no fireball: the ability class (%d) or the ability system (%d) is missing, trying again in 5 s"), *GetOwner()->GetName(), Ability ? 1 : 0, Asc ? 1 : 0);
		return;
	}
	if (!bFireballGiven)
	{
		bFireballGiven = CallBlueprintFunction(Asc, TEXT("Give Ability"),
			[&](UFunction& F, uint8* P)
			{
				if (const FClassProperty* ClassProp = CastField<FClassProperty>(F.FindPropertyByName(TEXT("AbilityClass"))))
				{
					ClassProp->SetPropertyValue_InContainer(P, Ability);
				}
				if (const FNumericProperty* Level = CastField<FNumericProperty>(F.FindPropertyByName(TEXT("Level"))))
				{
					Level->SetIntPropertyValue(Level->ContainerPtrToValuePtr<void>(P), static_cast<int64>(1));
				}
			},
			[](UFunction&, uint8*) {});
	}
	bool bSuccess = false;
	CallBlueprintFunction(Asc, TEXT("Try Activate Ability by Class"),
		[&](UFunction& F, uint8* P)
		{
			if (const FClassProperty* ClassProp = CastField<FClassProperty>(F.FindPropertyByName(TEXT("InAbilityClass"))))
			{
				ClassProp->SetPropertyValue_InContainer(P, Ability);
			}
			if (const FBoolProperty* Force = CastField<FBoolProperty>(F.FindPropertyByName(TEXT("bForceActivation"))))
			{
				Force->SetPropertyValue_InContainer(P, true);
			}
		},
		[&](UFunction& F, uint8* P)
		{
			for (TFieldIterator<FBoolProperty> It(&F); It; ++It)
			{
				if (It->HasAnyPropertyFlags(CPF_OutParm) && !It->HasAnyPropertyFlags(CPF_ReferenceParm))
				{
					bSuccess = It->GetPropertyValue_InContainer(P);
				}
			}
		});
	NextFireball = Now + FMath::RandRange(FireballCooldown.X, FMath::Max(FireballCooldown.X, FireballCooldown.Y));
	if (bSuccess)
	{
		++FireballCount;
	}
	UE_LOG(LogRPGPhases, Log, TEXT("%s: fireball at %.0f cm -> %d (%d so far), next in %.1f s"), *GetOwner()->GetName(), Distance, bSuccess, FireballCount, NextFireball - Now);
}

void URPGBossPhases::ResetPhases()
{
	if (bTransition)
	{
		bTransition = false;
		if (const ACharacter* Character = Cast<ACharacter>(GetOwner()))
		{
			if (UAnimInstance* Anim = Character->GetMesh() ? Character->GetMesh()->GetAnimInstance() : nullptr)
			{
				Anim->Montage_Stop(0.1f, TransitionMontage.Get());
			}
		}
		bHeld = false; // the encounter reset holds and resumes the behaviour itself
	}
	RemovePhaseTwoBuffs();
	RemoveImmunity();
	if (URPGBossPosture* Posture = GetOwner()->FindComponentByClass<URPGBossPosture>())
	{
		Posture->EndHold(true);
	}
	if (bPhaseTwo)
	{
		UE_LOG(LogRPGPhases, Log, TEXT("%s: back to phase one"), *GetOwner()->GetName());
	}
	bPhaseTwo = false;
}

void URPGBossPhases::HoldBehaviour()
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
					Reason->SetPropertyValue_InContainer(P, FString(TEXT("Phase two")));
				}
			},
			[](UFunction&, uint8*) {});
	}
	else if (Controller->BrainComponent)
	{
		Controller->BrainComponent->StopLogic(TEXT("Phase two"));
	}
	bHeld = true;
}

void URPGBossPhases::ResumeBehaviour()
{
	const APawn* Pawn = Cast<APawn>(GetOwner());
	AAIController* Controller = Pawn ? Cast<AAIController>(Pawn->GetController()) : nullptr;
	if (!Controller || !bHeld)
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
	bHeld = false;
}
