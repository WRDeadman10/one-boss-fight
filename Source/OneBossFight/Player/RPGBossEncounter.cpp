// Copyright One Boss Fight. All Rights Reserved.

#include "Player/RPGBossEncounter.h"
#include "Player/RPGBossBleed.h"
#include "Player/RPGBossDeath.h"
#include "Player/RPGBossRemains.h"
#include "Player/RPGBossPosture.h"
#include "Player/RPGIFrameMonitor.h"
#include "Player/RPGTraceGuard.h"
#include "Player/RPGBossStagger.h"
#include "Player/RPGBossPhases.h"
#include "Pack/RPGBlueprintCall.h"
#include "AIController.h"
#include "Animation/AnimInstance.h"
#include "BehaviorTree/BlackboardComponent.h"
#include "BrainComponent.h"
#include "Components/SkeletalMeshComponent.h"
#include "Engine/World.h"
#include "GameFramework/Character.h"
#include "GameFramework/CharacterMovementComponent.h"
#include "Kismet/GameplayStatics.h"
#include "Perception/AIPerceptionComponent.h"
#include "UObject/UnrealType.h"

DEFINE_LOG_CATEGORY_STATIC(LogRPGEncounter, Log, All);

using namespace RPGPack;

namespace
{
	constexpr const TCHAR* HealthTag = TEXT("Attribute.Health");
	constexpr const TCHAR* PoiseTag = TEXT("Attribute.Poise");

	AAIController* GetAIController(const AActor* Owner)
	{
		const APawn* Pawn = Cast<APawn>(Owner);
		return Pawn ? Cast<AAIController>(Pawn->GetController()) : nullptr;
	}

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

URPGBossEncounter::URPGBossEncounter()
{
	PrimaryComponentTick.bCanEverTick = true;
	PrimaryComponentTick.bStartWithTickEnabled = true;
	PrimaryComponentTick.TickInterval = 0.1f;
}

void URPGBossEncounter::BeginPlay()
{
	Super::BeginPlay();
	HomeTransform = GetOwner()->GetActorTransform();
	if (GateRadius > 0.f)
	{
		Sleep();
	}
}

void URPGBossEncounter::TickComponent(float DeltaTime, ELevelTick TickType, FActorComponentTickFunction* ThisTickFunction)
{
	Super::TickComponent(DeltaTime, TickType, ThisTickFunction);
	StartupTime += DeltaTime;
	if (bMaxHealthApplied && bDormant && StartupTime < StartupEnforceSeconds)
	{
		// The pack sets the current health from its own data (500) again after the first write: while the boss still sleeps at the start, nothing can have hurt it, so the full health is written until the pack has finished.
		double Max = 0.0, Current = 0.0;
		if (ReadAttribute(GetOwner(), HealthTag, true, Max) && ReadAttribute(GetOwner(), HealthTag, false, Current) && FMath::Abs(Max - BossMaxHealth) <= 0.5 && Current > 0.0 && Current < Max - 0.5)
		{
			WriteAttribute(GetOwner(), HealthTag, Max);
			UE_LOG(LogRPGEncounter, Log, TEXT("%s: start-up health %.0f restored to %.0f (the pack set it again)"), *GetOwner()->GetName(), Current, Max);
		}
	}
	if (!bMaxHealthApplied && BossMaxHealth > 1.f)
	{
		// The pack's attributes exist a moment after BeginPlay and the first PIE of an editor session reads health 0 (KI-081): wait for a living reading, then set the maximum and carry the current health over in proportion (a boss nobody has hurt is at its full new maximum).
		double Max = 0.0, Current = 0.0;
		if (ReadAttribute(GetOwner(), HealthTag, true, Max) && ReadAttribute(GetOwner(), HealthTag, false, Current) && Max > 0.0 && Current > 0.0)
		{
			double NewMax = 0.0;
			if (FMath::Abs(Max - BossMaxHealth) <= 0.5)
			{
				bMaxHealthApplied = true;
			}
			else if (WriteMaxAttribute(GetOwner(), HealthTag, BossMaxHealth) && ReadAttribute(GetOwner(), HealthTag, true, NewMax) && FMath::Abs(NewMax - BossMaxHealth) <= 0.5)
			{
				// Only a maximum that reads back as written lets the current health follow; otherwise the next tick tries again (a 2000 / 500 state is never written).
				bMaxHealthApplied = true;
				WriteAttribute(GetOwner(), HealthTag, Current * BossMaxHealth / Max);
				UE_LOG(LogRPGEncounter, Log, TEXT("%s: boss maximum health %.0f -> %.0f (health %.0f -> %.0f)"), *GetOwner()->GetName(), Max, static_cast<double>(BossMaxHealth), Current, Current * BossMaxHealth / Max);
			}
		}
	}
	if (bTestFreeze && !bDormant)
	{
		// The pack restarts its behaviour when it perceives the player again: keep it stopped for the whole test.
		HoldBehaviour();
		if (AAIController* Controller = GetAIController(GetOwner()))
		{
			if (Controller->BrainComponent && Controller->BrainComponent->IsRunning())
			{
				Controller->BrainComponent->StopLogic(TEXT("Test freeze"));
			}
		}
	}
	if (bWantsHold && !bHeld)
	{
		HoldBehaviour(); // the pack's controller creates its behaviour tree component a moment after BeginPlay
	}
	const APawn* Player = UGameplayStatics::GetPlayerPawn(this, 0);
	if (!Player)
	{
		return;
	}
	if (TrackedPlayer.IsValid() && TrackedPlayer.Get() != Player)
	{
		TrackedPlayer = Player;
		if (bResetOnPlayerRespawn)
		{
			ResetEncounter();
			return;
		}
	}
	TrackedPlayer = Player;

	if (bDormant)
	{
		if (bTestFreeze)
		{
			return; // scripted tests: the boss only does what the test starts
		}
		const double Distance = FVector::Dist2D(GetOwner()->GetActorLocation(), Player->GetActorLocation());
		// "Hurt" = health below what it was once the pack had initialised the attributes (they are not ready at BeginPlay).
		double Health = 0.0;
		bool bHurt = false;
		DormantTime += DeltaTime;
		if (DormantTime > 1.0 && StartupTime > StartupEnforceSeconds && ReadAttribute(GetOwner(), HealthTag, false, Health))
		{
			if (HealthBaseline < 0.0)
			{
				HealthBaseline = Health;
			}
			bHurt = Health < HealthBaseline - 0.5;
		}
		if (GateRadius <= 0.f || Distance <= GateRadius || bHurt)
		{
			Wake();
		}
	}
}

bool URPGBossEncounter::HoldBehaviour()
{
	AAIController* Controller = GetAIController(GetOwner());
	if (!Controller || !Controller->BrainComponent)
	{
		return false;
	}
	if (UObject* Manager = FindControllerComponent(Controller, TEXT("BP_BehaviorManagerComponent_C")))
	{
		CallBlueprintFunction(Manager, TEXT("StopBehaviorLogic"),
			[](UFunction& F, uint8* P)
			{
				if (const FStrProperty* Reason = CastField<FStrProperty>(F.FindPropertyByName(TEXT("Reason"))))
				{
					Reason->SetPropertyValue_InContainer(P, FString(TEXT("Boss dormant")));
				}
			},
			[](UFunction&, uint8*) {});
	}
	else
	{
		Controller->BrainComponent->StopLogic(TEXT("Boss dormant"));
	}
	bHeld = true;
	return true;
}

void URPGBossEncounter::ResumeBehaviour()
{
	AAIController* Controller = GetAIController(GetOwner());
	if (!Controller)
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

void URPGBossEncounter::Sleep()
{
	bDormant = true;
	DormantTime = 0.f;
	HealthBaseline = -1.0;
	bWantsHold = true;
	HoldBehaviour();
	UE_LOG(LogRPGEncounter, Log, TEXT("%s: dormant at %s (gate %.0f cm)"), *GetOwner()->GetName(), *GetOwner()->GetActorLocation().ToCompactString(), GateRadius);
}

void URPGBossEncounter::HoldForTest(bool bHold)
{
#if !UE_BUILD_SHIPPING
	bTestFreeze = bHold;
	if (bHold)
	{
		HoldBehaviour();
	}
	else
	{
		ResumeBehaviour();
	}
#endif
}

void URPGBossEncounter::ResetForTest()
{
#if !UE_BUILD_SHIPPING
	ResetEncounter();
#endif
}

void URPGBossEncounter::Wake()
{
	if (!bDormant)
	{
		return;
	}
	bDormant = false;
	bWantsHold = false;
	ResumeBehaviour();
	UE_LOG(LogRPGEncounter, Log, TEXT("%s: awake, the fight begins"), *GetOwner()->GetName());
}

void URPGBossEncounter::ResetEncounter()
{
	AActor* Owner = GetOwner();
	ARPGBossRemains::DestroyForWorld(Owner ? Owner->GetWorld() : nullptr);
	// A boss that is dying stays dead: the pack destroys it a few seconds after its death whatever is done, so a reset would only bring back a corpse-less ghost with the ragdoll's changes on it (review D).
	if (const URPGBossDeath* Death = Owner->FindComponentByClass<URPGBossDeath>(); Death && Death->IsDeathActive())
	{
		++DeathResetRefusals;
		UE_LOG(LogRPGEncounter, Log, TEXT("%s: encounter reset refused: the boss is dying (%s), the dead boss stays dead"), *Owner->GetName(), *Death->GetDeathStateName());
		return;
	}
	URPGTraceGuard::CloseFor(Owner, TEXT("reset")); // first: before the montage stops, the weapon is sheathed and the boss is teleported, so no stale sweep can run across the arena
	++ResetCount;
	++Generation; // every callback made for the old fight is stale from here on
	if (URPGIFrameMonitor* IFrames = URPGIFrameMonitor::Find(this))
	{
		IFrames->OnEncounterReset(); // a dodge's invulnerability does not survive the reset (Freeze 800)
	}
	UE_LOG(LogRPGEncounter, Log, TEXT("%s: encounter reset %d (generation %d, player respawned), from %s back to %s"), *Owner->GetName(), ResetCount, Generation, *Owner->GetActorLocation().ToCompactString(),
		*HomeTransform.GetLocation().ToCompactString());

	if (URPGBossStagger* Stagger = Owner->FindComponentByClass<URPGBossStagger>())
	{
		Stagger->AbortStagger();
	}
	if (URPGBossPhases* Phases = Owner->FindComponentByClass<URPGBossPhases>())
	{
		Phases->ResetPhases();
	}
	HoldBehaviour();
	// The boss forgets the player and stops being in combat. The AI controller stays (the pack's abilities hold references to its components).
	if (AAIController* Controller = GetAIController(Owner))
	{
		if (UBlackboardComponent* Blackboard = Controller->GetBlackboardComponent())
		{
			Blackboard->ClearValue(TEXT("TargetActor"));
			Blackboard->SetValueAsBool(TEXT("bCombatEnabled"), false);
		}
		if (UAIPerceptionComponent* Perception = Controller->GetAIPerceptionComponent())
		{
			Perception->ForgetAll();
		}
	}
	if (UObject* Combat = FindComponentByClassName(Owner, TEXT("BP_CombatComponent_C")))
	{
		CallBlueprintFunction(Combat, TEXT("ClearAllCombatTargets"), [](UFunction&, uint8*) {}, [](UFunction&, uint8*) {});
		CallBlueprintFunction(Combat, TEXT("SetCombatEnabled"),
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
	if (const ACharacter* Character = Cast<ACharacter>(Owner))
	{
		if (UAnimInstance* Anim = Character->GetMesh() ? Character->GetMesh()->GetAnimInstance() : nullptr)
		{
			Anim->Montage_Stop(0.1f);
		}
		if (UCharacterMovementComponent* Movement = Character->GetCharacterMovement())
		{
			Movement->StopMovementImmediately();
		}
	}
	Owner->SetActorTransform(HomeTransform, false, nullptr, ETeleportType::TeleportPhysics);

	double Max = 0.0;
	if (ReadAttribute(Owner, HealthTag, true, Max))
	{
		WriteAttribute(Owner, HealthTag, Max);
	}
	if (ReadAttribute(Owner, PoiseTag, true, Max))
	{
		WriteAttribute(Owner, PoiseTag, Max);
	}
	if (URPGBossPosture* Posture = Owner->FindComponentByClass<URPGBossPosture>())
	{
		Posture->ResetPool(); // the posture pool is the component's own (Gate 3, M9)
	}
	if (URPGBossBleed* Bleed = Owner->FindComponentByClass<URPGBossBleed>())
	{
		Bleed->ResetBleed();
	}
	if (GateRadius > 0.f)
	{
		Sleep();
	}
	else
	{
		ResumeBehaviour();
	}
}
