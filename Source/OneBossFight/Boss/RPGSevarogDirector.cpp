// Copyright One Boss Fight. All Rights Reserved.

#include "Boss/RPGSevarogDirector.h"
#include "Pack/RPGBlueprintCall.h"
#include "Animation/AnimInstance.h"
#include "Components/SkeletalMeshComponent.h"
#include "GameFramework/Character.h"
#include "AIController.h"
#include "BehaviorTree/BlackboardComponent.h"
#include "BrainComponent.h"
#include "Perception/AIPerceptionComponent.h"
#include "GameFramework/CharacterMovementComponent.h"
#include "GameFramework/Pawn.h"
#include "GameplayTagContainer.h"
#include "Engine/World.h"
#include "Kismet/GameplayStatics.h"
#include "NiagaraFunctionLibrary.h"
#include "TimerManager.h"
#include "UObject/UnrealType.h"

DEFINE_LOG_CATEGORY_STATIC(LogSevarogDirector, Log, All);

using namespace RPGPack;

URPGSevarogDirector::URPGSevarogDirector()
{
	PrimaryComponentTick.bCanEverTick = true;
	PrimaryComponentTick.bStartWithTickEnabled = true;
	PrimaryComponentTick.TickInterval = 0.1f;
}

void URPGSevarogDirector::BeginPlay()
{
	Super::BeginPlay();

	const APawn* Pawn = Cast<APawn>(GetOwner());
	bGateOpen = GateRadius <= 0.f || !Pawn;
	LightningTimer = FMath::RandRange(LightningCooldown.X, FMath::Max(LightningCooldown.X, LightningCooldown.Y));
	HomeTransform = GetOwner()->GetActorTransform();
	if (UWorld* World = GetWorld())
	{
		SpawnHandle = World->AddOnActorSpawnedHandler(FOnActorSpawned::FDelegate::CreateUObject(this, &URPGSevarogDirector::OnActorSpawned));
	}
	if (const ACharacter* Character = Cast<ACharacter>(GetOwner()))
	{
		BaseWalkSpeed = Character->GetCharacterMovement() ? Character->GetCharacterMovement()->MaxWalkSpeed : 0.f;
	}
}

void URPGSevarogDirector::EndPlay(const EEndPlayReason::Type EndPlayReason)
{
	if (UWorld* World = GetWorld())
	{
		World->RemoveOnActorSpawnedHandler(SpawnHandle);
	}
	Super::EndPlay(EndPlayReason);
}

void URPGSevarogDirector::OnActorSpawned(AActor* Actor)
{
	// The lightning ability fires its projectile from the scythe; the strike moves it above the spot marked at the start of the cast and sends it straight down.
	if (StrikePendingTime <= 0.f || !Actor || !Actor->GetClass()->GetName().StartsWith(StrikeProjectileClassPrefix))
	{
		return;
	}
	StrikePendingTime = 0.f;
	Actor->SetActorLocationAndRotation(StrikeLocation + FVector(0.f, 0.f, StrikeHeight), FRotator(-90.f, 0.f, 0.f), false, nullptr, ETeleportType::TeleportPhysics);

	double Speed = 2500.0;
	if (const FNumericProperty* Prop = CastField<FNumericProperty>(Actor->GetClass()->FindPropertyByName(TEXT("InitialSpeed"))))
	{
		const void* Value = Prop->ContainerPtrToValuePtr<void>(Actor);
		Speed = Prop->IsFloatingPoint() ? Prop->GetFloatingPointPropertyValue(Value) : static_cast<double>(Prop->GetSignedIntPropertyValue(Value));
	}
	const float Delay = FMath::Max(0.1f, StrikeHeight / static_cast<float>(FMath::Max(Speed, 100.0)));
	if (StrikeBoltEffect && GetWorld())
	{
		const FVector Where = StrikeLocation;
		TWeakObjectPtr<UNiagaraSystem> Effect = StrikeBoltEffect;
		TWeakObjectPtr<UWorld> WeakWorld = GetWorld();
		FTimerHandle Handle;
		GetWorld()->GetTimerManager().SetTimer(Handle, FTimerDelegate::CreateLambda([Effect, WeakWorld, Where]()
		{
			if (Effect.IsValid() && WeakWorld.IsValid())
			{
				UNiagaraFunctionLibrary::SpawnSystemAtLocation(WeakWorld.Get(), Effect.Get(), Where);
			}
		}), Delay, false);
	}
	UE_LOG(LogSevarogDirector, Log, TEXT("Lightning strike: bolt moved above %s, lands in %.2f s"), *StrikeLocation.ToCompactString(), Delay);
}

UObject* URPGSevarogDirector::FindOwnerComponentByClassName(const TCHAR* ClassName)
{
	TInlineComponentArray<UActorComponent*> Components(GetOwner());
	for (UActorComponent* Component : Components)
	{
		if (Component && Component->GetClass()->GetName() == ClassName)
		{
			return Component;
		}
	}
	return nullptr;
}

bool URPGSevarogDirector::ReadHealth(float& Current, float& Max)
{
	UObject* Attributes = FindOwnerComponentByClassName(TEXT("BP_AttributesComponent_C"));
	if (!Attributes)
	{
		return false;
	}
	const FGameplayTag Tag = FGameplayTag::RequestGameplayTag(HealthAttributeTag, false);
	if (!Tag.IsValid())
	{
		return false;
	}
	double Value = 0.0, MaxValue = 0.0;
	const bool bOk = CallBlueprintFunction(Attributes, TEXT("Get Current Attribute Value"), [&](UFunction& F, uint8* P) { SetTag(F, P, TEXT("AttributeTag"), Tag); },
		[&](UFunction& F, uint8* P) { Value = ReadNumber(F, P, TEXT("Value")); })
		&& CallBlueprintFunction(Attributes, TEXT("GetMaxAttributeValue"), [&](UFunction& F, uint8* P) { SetTag(F, P, TEXT("AttributeTag"), Tag); },
		[&](UFunction& F, uint8* P) { MaxValue = ReadNumber(F, P, TEXT("Value")); });
	Current = static_cast<float>(Value);
	Max = static_cast<float>(MaxValue);
	return bOk && Max > 0.f;
}

bool URPGSevarogDirector::ActivateAbility(TSubclassOf<UObject> AbilityClass, bool bForce)
{
	UObject* Asc = FindOwnerComponentByClassName(TEXT("BP_AdvancedAbilitySystemComponent_C"));
	if (!Asc || !AbilityClass)
	{
		return false;
	}
	bool bSuccess = false;
	CallBlueprintFunction(Asc, TEXT("Try Activate Ability by Class"),
		[&](UFunction& F, uint8* P)
		{
			if (const FClassProperty* ClassProp = CastField<FClassProperty>(F.FindPropertyByName(TEXT("InAbilityClass"))))
			{
				ClassProp->SetPropertyValue_InContainer(P, AbilityClass);
			}
			else if (const FObjectProperty* ObjProp = CastField<FObjectProperty>(F.FindPropertyByName(TEXT("InAbilityClass"))))
			{
				ObjProp->SetObjectPropertyValue(ObjProp->ContainerPtrToValuePtr<void>(P), AbilityClass);
			}
			if (const FBoolProperty* Force = CastField<FBoolProperty>(F.FindPropertyByName(TEXT("bForceActivation"))))
			{
				Force->SetPropertyValue_InContainer(P, bForce);
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
	return bSuccess;
}

void URPGSevarogDirector::EnterPhaseTwo()
{
	bPhaseTwo = true;
	if (ACharacter* Character = Cast<ACharacter>(GetOwner()))
	{
		if (UCharacterMovementComponent* Movement = Character->GetCharacterMovement())
		{
			Movement->MaxWalkSpeed *= PhaseTwoSpeedScale;
		}
	}
	float RoarLength = 0.f;
	if (const ACharacter* Character = Cast<ACharacter>(GetOwner()))
	{
		if (UAnimInstance* Anim = Character->GetMesh() ? Character->GetMesh()->GetAnimInstance() : nullptr)
		{
			if (PhaseRoarMontage)
			{
				RoarLength = Anim->Montage_Play(PhaseRoarMontage, 1.f); // stops whatever attack montage is running
			}
		}
	}
	UE_LOG(LogSevarogDirector, Log, TEXT("%s enters phase two (roar %.2f s)"), *GetOwner()->GetName(), RoarLength);
}

namespace
{
	AAIController* GetAIController(const APawn* Pawn)
	{
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

void URPGSevarogDirector::HoldBehavior()
{
	AAIController* Controller = GetAIController(Cast<APawn>(GetOwner()));
	if (!Controller)
	{
		return;
	}
	if (!Controller->BrainComponent)
	{
		return; // the pack's controller has not created its behaviour tree component yet
	}
	const bool bRunning = Controller->BrainComponent->IsRunning();
	if (!bRunning && bBehaviorHeld)
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
					Reason->SetPropertyValue_InContainer(P, FString(TEXT("Sevarog gate")));
				}
			},
			[](UFunction&, uint8*) {});
	}
	else if (Controller->BrainComponent)
	{
		Controller->BrainComponent->StopLogic(TEXT("Sevarog gate"));
	}
	bBehaviorHeld = true;
}

void URPGSevarogDirector::ReleaseBehavior()
{
	APawn* Pawn = Cast<APawn>(GetOwner());
	if (!GetAIController(Pawn))
	{
		// No controller (AutoPossessAI off): create it now and run what the pack's pawn BeginPlay would have run.
		if (Pawn)
		{
			Pawn->SpawnDefaultController();
			if (AController* Spawned = Pawn->GetController())
			{
				CallBlueprintFunction(Spawned, TEXT("InitializeController"), [](UFunction&, uint8*) {}, [](UFunction&, uint8*) {});
			}
		}
		bBehaviorHeld = false;
		return;
	}
	// Entrance first, with the behaviour still held, then the pack's tree takes over.
	if (EntranceAbility && EntranceHoldSeconds > 0.f && ActivateAbility(EntranceAbility, true))
	{
		EntranceTimer = EntranceHoldSeconds;
		UE_LOG(LogSevarogDirector, Log, TEXT("Entrance started, behaviour resumes in %.1f s"), EntranceHoldSeconds);
		return;
	}
	ResumeBehavior();
}

void URPGSevarogDirector::ResumeBehavior()
{
	AAIController* Controller = GetAIController(Cast<APawn>(GetOwner()));
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
	bBehaviorHeld = false;
}

void URPGSevarogDirector::ResetEncounter()
{
	APawn* Pawn = Cast<APawn>(GetOwner());
	if (!Pawn)
	{
		return;
	}
	// Keep the controller (the pack's abilities hold references to its components); stop the behaviour and make the boss forget the player.
	EntranceTimer = -1.f;
	HoldBehavior();
	if (AAIController* Controller = GetAIController(Pawn))
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
	if (UObject* Combat = FindOwnerComponentByClassName(TEXT("BP_CombatComponent_C")))
	{
		CallBlueprintFunction(Combat, TEXT("ClearAllCombatTargets"), [](UFunction&, uint8*) {}, [](UFunction&, uint8*) {});
	}
	if (const ACharacter* Character = Cast<ACharacter>(Pawn))
	{
		if (UAnimInstance* Anim = Character->GetMesh() ? Character->GetMesh()->GetAnimInstance() : nullptr)
		{
			Anim->Montage_Stop(0.1f);
		}
		if (UCharacterMovementComponent* Movement = Character->GetCharacterMovement())
		{
			Movement->StopMovementImmediately();
			if (BaseWalkSpeed > 0.f)
			{
				Movement->MaxWalkSpeed = BaseWalkSpeed;
			}
		}
	}
	Pawn->SetActorTransform(HomeTransform, false, nullptr, ETeleportType::TeleportPhysics);

	// Full health again.
	if (UObject* Attributes = FindOwnerComponentByClassName(TEXT("BP_AttributesComponent_C")))
	{
		float Current = 0.f, Max = 0.f;
		const FGameplayTag Tag = FGameplayTag::RequestGameplayTag(HealthAttributeTag, false);
		if (ReadHealth(Current, Max) && Tag.IsValid())
		{
			CallBlueprintFunction(Attributes, TEXT("Set Current Attribute Value"),
				[&](UFunction& F, uint8* P)
				{
					SetTag(F, P, TEXT("AttributeTag"), Tag);
					if (const FNumericProperty* Value = CastField<FNumericProperty>(F.FindPropertyByName(TEXT("Value"))))
					{
						Value->SetFloatingPointPropertyValue(Value->ContainerPtrToValuePtr<void>(P), static_cast<double>(Max));
					}
				},
				[](UFunction&, uint8*) {});
		}
	}
	// Combat off, so the entrance plays again when the gate reopens.
	if (UObject* Combat = FindOwnerComponentByClassName(TEXT("BP_CombatComponent_C")))
	{
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

	bPhaseTwo = false;
	bGateOpen = GateRadius <= 0.f;
	LightningTimer = FMath::RandRange(LightningCooldown.X, FMath::Max(LightningCooldown.X, LightningCooldown.Y));
	UE_LOG(LogSevarogDirector, Log, TEXT("%s reset after the player respawned"), *Pawn->GetName());
}

bool URPGSevarogDirector::TryLightning(const APawn* Player, bool bIgnoreConditions)
{
	const ACharacter* Character = Cast<ACharacter>(GetOwner());
	if (!Character || !Player || !LightningAbility)
	{
		return false;
	}
	const float Distance = FVector::Dist2D(Character->GetActorLocation(), Player->GetActorLocation());
	if (!bIgnoreConditions && (Distance < LightningMinRange || Distance > LightningMaxRange))
	{
		return false;
	}
	const UAnimInstance* Anim = Character->GetMesh() ? Character->GetMesh()->GetAnimInstance() : nullptr;
	if (!bIgnoreConditions && (!Anim || Anim->IsAnyMontagePlaying()))
	{
		return false;
	}
	if (ActivateAbility(LightningAbility))
	{
		// The spot under the player now: the bolt lands there, so he can step away during the cast.
		FHitResult Floor;
		const FVector Feet = Player->GetActorLocation();
		StrikeLocation = GetWorld()->LineTraceSingleByChannel(Floor, Feet, Feet - FVector(0.f, 0.f, 600.f), ECC_Visibility) ? Floor.ImpactPoint : Feet - FVector(0.f, 0.f, 90.f);
		StrikePendingTime = 3.f;
		if (StrikeTelegraphEffect)
		{
			UNiagaraFunctionLibrary::SpawnSystemAtLocation(GetWorld(), StrikeTelegraphEffect, StrikeLocation + FVector(0.f, 0.f, 5.f), FRotator::ZeroRotator, FVector(StrikeTelegraphScale));
		}
		LightningTimer = FMath::RandRange(LightningCooldown.X, FMath::Max(LightningCooldown.X, LightningCooldown.Y));
		UE_LOG(LogSevarogDirector, Log, TEXT("Lightning strike at %.0f cm"), Distance);
		return true;
	}
	return false;
}

bool URPGSevarogDirector::TriggerLightning()
{
	return TryLightning(UGameplayStatics::GetPlayerPawn(this, 0), true);
}

void URPGSevarogDirector::TickComponent(float DeltaTime, ELevelTick TickType, FActorComponentTickFunction* ThisTickFunction)
{
	Super::TickComponent(DeltaTime, TickType, ThisTickFunction);
	if (bDead)
	{
		return;
	}

	APawn* Pawn = Cast<APawn>(GetOwner());
	const APawn* Player = UGameplayStatics::GetPlayerPawn(this, 0);
	if (!Pawn || !Player)
	{
		return;
	}

	if (TrackedPlayer.IsValid() && TrackedPlayer.Get() != Player)
	{
		TrackedPlayer = Player;
		if (bGateOpen)
		{
			ResetEncounter();
			return;
		}
	}
	TrackedPlayer = Player;

	if (!bGateOpen)
	{
		HoldBehavior();
		if (FVector::Dist2D(Pawn->GetActorLocation(), Player->GetActorLocation()) <= GateRadius)
		{
			bGateOpen = true;
			ReleaseBehavior();
			UE_LOG(LogSevarogDirector, Log, TEXT("Gate opened: %s wakes up"), *Pawn->GetName());
		}
		return;
	}

	if (EntranceTimer >= 0.f)
	{
		EntranceTimer -= DeltaTime;
		if (EntranceTimer < 0.f)
		{
			ResumeBehavior();
			UE_LOG(LogSevarogDirector, Log, TEXT("Entrance over: behaviour resumed"));
		}
	}

	StrikePendingTime = FMath::Max(0.f, StrikePendingTime - DeltaTime);

	CheckTimer += DeltaTime;
	if (CheckTimer >= 0.25f)
	{
		CheckTimer = 0.f;
		float Current = 0.f, Max = 0.f;
		if (ReadHealth(Current, Max))
		{
			if (Current <= 0.f)
			{
				bDead = true;
				return;
			}
			if (!bPhaseTwo && Current / Max <= PhaseTwoHealthFraction)
			{
				EnterPhaseTwo();
			}
		}
	}

	if (bPhaseTwo)
	{
		LightningTimer -= DeltaTime;
		if (LightningTimer <= 0.f)
		{
			TryLightning(Player);
			LightningTimer = FMath::Max(LightningTimer, 0.5f); // retry soon when conditions were not met
		}
	}
}
