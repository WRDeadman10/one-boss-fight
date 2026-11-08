// Copyright One Boss Fight. All Rights Reserved.

#include "Player/RPGDodgeTiming.h" 
#include "Player/RPGAirAttackRules.h"
#include "Player/RPGGuardCounterRules.h"
#include "Player/RPGDodgeInputRules.h"
#include "Player/RPGStartupChronology.h"
#include "Player/RPGFlipbookEffect.h"
#include "Player/RPGBossDamage.h"
#include "Pack/RPGBlueprintCall.h"
#include "Animation/AnimMontage.h"
#include "Components/CapsuleComponent.h"
#include "EnhancedInputComponent.h"
#include "GameFramework/Character.h"
#include "GameFramework/CharacterMovementComponent.h"
#include "GameFramework/Pawn.h"
#include "GameplayTagContainer.h"
#include "InputAction.h"
#include "Animation/AnimInstance.h"
#include "Components/SkeletalMeshComponent.h"
#include "Engine/World.h"
#include "UObject/UnrealType.h"

DEFINE_LOG_CATEGORY_STATIC(LogRPGDodge, Log, All);

using namespace RPGPack;

URPGDodgeTiming::URPGDodgeTiming()
{
	PrimaryComponentTick.bCanEverTick = true;
	PrimaryComponentTick.bStartWithTickEnabled = true;
	PrimaryComponentTick.TickInterval = 0.f; // every frame: the backward turn follows the dodge's root motion

	DodgeAction = TSoftObjectPtr<UInputAction>(FSoftObjectPath(TEXT("/Game/AdvancedARPGCombat/MeleeCombatSystem/Blueprints/Input/InputActions/IA_Dodge.IA_Dodge")));
	QuickMontage = TSoftObjectPtr<UAnimMontage>(FSoftObjectPath(
		TEXT("/Game/AdvancedARPGCombat/Characters/Heroes/Mannequins/Animations/Roll/Dodge_Small_Forward_Roll_Montage.Dodge_Small_Forward_Roll_Montage")));
	FullMontage = TSoftObjectPtr<UAnimMontage>(FSoftObjectPath(
		TEXT("/Game/AdvancedARPGCombat/MeleeCombatSystem/Animations/Dodge/Dodge_To_Idle_Montage.Dodge_To_Idle_Montage"))); EldenRingMappingContext = TSoftObjectPtr<UInputMappingContext>(FSoftObjectPath(TEXT("/Game/OneBossFight/Input/IMC_EldenRing.IMC_EldenRing"))); EldenRingLightAction = TSoftObjectPtr<UInputAction>(FSoftObjectPath(TEXT("/Game/OneBossFight/Input/IA_ER_Light.IA_ER_Light"))); EldenRingHeavyTapAction = TSoftObjectPtr<UInputAction>(FSoftObjectPath(TEXT("/Game/OneBossFight/Input/IA_ER_HeavyTap.IA_ER_HeavyTap"))); PackLightAction = TSoftObjectPtr<UInputAction>(FSoftObjectPath(TEXT("/Game/AdvancedARPGCombat/MeleeCombatSystem/Blueprints/Input/InputActions/IA_NormalAttack.IA_NormalAttack"))); PackStrongAction = TSoftObjectPtr<UInputAction>(FSoftObjectPath(TEXT("/Game/AdvancedARPGCombat/MeleeCombatSystem/Blueprints/Input/InputActions/IA_StrongAttack.IA_StrongAttack")));
	// Elden Ring player clips (owner 2026-11-07: "implement it in the game" after the reel). Assets are notify-authored,
	// Lead-verified (C-988/C-998/C-1004) and play only through the existing optional paths; clearing a field restores the pack behaviour.
	// Owner 2026-11-08: the hand-built AM_ER_Backstep_Back was rejected; the Mixamo "Standing Dodge Backward" retarget (root motion on the root bone,
	// trimmed to 0.567 s, A-640/C-1059) is the default backstep. The old asset stays in Content, unreferenced.
	BackstepMontage = TSoftObjectPtr<UAnimMontage>(FSoftObjectPath(TEXT("/Game/OneBossFight/Player/Animations/AM_ER_Backstep_Mixamo_V2.AM_ER_Backstep_Mixamo_V2")));
	GuardCounterMontage = TSoftObjectPtr<UAnimMontage>(FSoftObjectPath(TEXT("/Game/OneBossFight/Player/Animations/AM_ER_Attack_GuardCounter.AM_ER_Attack_GuardCounter")));
	AirLightMontage = TSoftObjectPtr<UAnimMontage>(FSoftObjectPath(TEXT("/Game/OneBossFight/Player/Animations/AM_ER_Attack_Air_Light.AM_ER_Attack_Air_Light")));
	AirHeavyMontage = TSoftObjectPtr<UAnimMontage>(FSoftObjectPath(TEXT("/Game/OneBossFight/Player/Animations/AM_ER_Attack_Air_Heavy_Plunge.AM_ER_Attack_Air_Heavy_Plunge")));
}

void URPGDodgeTiming::EndPlay(const EEndPlayReason::Type EndPlayReason)
{
	// Do not leave a temporary pack ability-array override behind if this component
	// leaves play before the montage starts or its normal tick restores the arrays.
	RestoreGuardCounterMontageOverride();
	LastSuccessfulGuardTime = -1.0e9;
	Super::EndPlay(EndPlayReason);
}

void URPGDodgeTiming::BeginPlay()
{
	RPGStartupChronology::AtComponentBeginPlay(*this);
	Super::BeginPlay();
	LoadedDodgeDustFlipbook = ARPGFlipbookEffect::LoadMaterial(ERPGEFlipbookKind::DodgeDust);
	if (!AirLightMontage.IsNull())
	{
		AirLightMontage.LoadSynchronous();
	}
	if (!AirHeavyMontage.IsNull())
	{
		AirHeavyMontage.LoadSynchronous();
	}
	TryBind();
}

void URPGDodgeTiming::TickComponent(float DeltaTime, ELevelTick TickType, FActorComponentTickFunction* ThisTickFunction)
{
	Super::TickComponent(DeltaTime, TickType, ThisTickFunction); TryAddEldenRingContext(); TickEldenRingInput();
	// The live BP_ExampleGreatSwordBoss does not host RPGFrameworkMoveExecutor.
	// Observe the pack's player-side reaction ability instead: GA_BlockReaction is
	// activated by a blocked hit and has a weapon-style-specific class name.
	// Require Status.Blocking at its rising edge so unrelated reactions cannot arm.
	AActor* GuardOwner = GetOwner();
	const double GuardMonitorNow = GetWorld() ? GetWorld()->GetTimeSeconds() : 0.0;
	if (GuardOwner && GuardMonitorNow - LastBlockReactionAbilitySearchTime >= 1.0)
	{
		CachedBlockReactionAbilities.Reset();
		UActorComponent* Asc = Cast<UActorComponent>(FindComponentByClassName(GuardOwner, TEXT("BP_AdvancedAbilitySystemComponent_C")));
		const FArrayProperty* Created = Asc ? FindFProperty<FArrayProperty>(Asc->GetClass(), TEXT("CreatedAbilities")) : nullptr;
		const FObjectProperty* Inner = Created ? CastField<FObjectProperty>(Created->Inner) : nullptr;
		if (Inner)
		{
			FScriptArrayHelper Abilities(Created, Created->ContainerPtrToValuePtr<void>(Asc));
			for (int32 Index = 0; Index < Abilities.Num(); ++Index)
			{
				UObject* Ability = Inner->GetObjectPropertyValue(Abilities.GetRawPtr(Index));
				if (Ability && RPGGuardCounterRules::IsBlockReactionAbilityClass(Ability->GetClass()->GetName()))
				{
					CachedBlockReactionAbilities.Add(Ability);
				}
			}
		}
		LastBlockReactionAbilitySearchTime = GuardMonitorNow;
	}
	bool bBlockReactionActive = false;
	for (const TWeakObjectPtr<UObject>& WeakAbility : CachedBlockReactionAbilities)
	{
		if (UObject* Ability = WeakAbility.Get())
		{
			bBlockReactionActive |= IsAbilityActive(Ability);
		}
	}
	if (GuardOwner && (bBlockReactionActive || GuardMonitorNow - LastGuardTagProbeTime >= 0.10))
	{
		bLastObservedBlocking = RPGBossDamage::HasTag(GuardOwner, TEXT("Status.Blocking"));
		LastGuardTagProbeTime = GuardMonitorNow;
	}
	if (GuardMonitorNow - LastGuardMonitorLogTime >= 1.0)
	{
		UE_LOG(LogRPGDodge, Verbose, TEXT("guard contact monitor reactionVariants=%d reactionActive=%d statusBlocking=%d"),
			CachedBlockReactionAbilities.Num(), bBlockReactionActive ? 1 : 0, bLastObservedBlocking ? 1 : 0);
		LastGuardMonitorLogTime = GuardMonitorNow;
	}
	if (RPGGuardCounterRules::IsNewBlockedContact(bLastObservedBlocking, bBlockReactionActive, bWasBlockReactionActive))
	{
		NotifySuccessfulGuardContact();
	}
	bWasBlockReactionActive = bBlockReactionActive;
	if (!bBound)
	{
		TryBind();
	}
	if (!CachedAbility.IsValid())
	{
		CachedAbility = FindDodgeAbility();
	}
	UObject* Ability = CachedAbility.Get();
	const bool bActive = Ability && IsAbilityActive(Ability);
	if (bActive && !bWasActive)
	{
		OnDodgeStarted();
	}
	bWasActive = bActive;
	if (!bBackwardWithoutInput)
	{
		return;
	}
	if (bTurning)
	{
		if (bActive)
		{
			StepBackwardTurn(DeltaTime);
		}
		else
		{
			bTurning = false;
		}
	}
}

void URPGDodgeTiming::OnDodgeStarted()
{
	if (const ACharacter* Walker = Cast<ACharacter>(GetOwner()))
	{
		// the dust belongs on the floor: the actor location is the capsule centre
		const float HalfHeight = Walker->GetCapsuleComponent() ? Walker->GetCapsuleComponent()->GetScaledCapsuleHalfHeight() : 90.f;
		ARPGFlipbookEffect::Spawn(GetWorld(), Walker->GetActorLocation() - FVector(0.f, 0.f, HalfHeight), ERPGEFlipbookKind::DodgeDust, LoadedDodgeDustFlipbook);
	}
	if (!bBackwardWithoutInput || Selected == EKind::Backstep)
	{
		return; // a backstep keeps the facing: the clip itself goes backward, no turn
	}
	const ACharacter* Character = Cast<ACharacter>(GetOwner());
	const UCharacterMovementComponent* Movement = Character ? Character->GetCharacterMovement() : nullptr;
	if (!Movement || Movement->GetLastInputVector().Size() >= NoInputThreshold)
	{
		bTurning = false;
		return;
	}
	// No direction input: away from the camera (the camera looks at the target when locked on).
	TurnTargetYaw = FRotator::NormalizeAxis(Character->GetControlRotation().Yaw + 180.f);
	bTurning = true;
	++BackwardTurnCount;
	UE_LOG(LogRPGDodge, Log, TEXT("dodge %d started with no direction input: turning to yaw %.0f (from %.0f) to dodge backward"), PressCount, TurnTargetYaw, Character->GetActorRotation().Yaw);
}

bool URPGDodgeTiming::HasNoDirectionInput() const
{
	const ACharacter* Character = Cast<ACharacter>(GetOwner());
	const UCharacterMovementComponent* Movement = Character ? Character->GetCharacterMovement() : nullptr;
	return Movement && Movement->GetLastInputVector().Size() < NoInputThreshold;
}

void URPGDodgeTiming::StepBackwardTurn(float DeltaTime)
{
	AActor* Owner = GetOwner();
	const float Current = Owner->GetActorRotation().Yaw;
	const float Next = FMath::FixedTurn(Current, TurnTargetYaw, BackwardTurnRate * DeltaTime);
	Owner->SetActorRotation(FRotator(0.f, Next, 0.f));
	if (FMath::Abs(FRotator::NormalizeAxis(TurnTargetYaw - Next)) < 1.f)
	{
		bTurning = false;
	}
}

bool URPGDodgeTiming::TryBind()
{
	if (bBound)
	{
		return true;
	}
	const APawn* Pawn = Cast<APawn>(GetOwner());
	UEnhancedInputComponent* Input = Pawn ? Cast<UEnhancedInputComponent>(Pawn->InputComponent) : nullptr;
	UInputAction* Action = DodgeAction.LoadSynchronous();
	if (!Input || !Action)
	{
		return false;
	}
	Input->BindAction(Action, ETriggerEvent::Started, this, &URPGDodgeTiming::OnDodgePressed);
	bBound = true;
	UE_LOG(LogRPGDodge, Log, TEXT("%s: dodge timing bound to %s (double tap window %.2f s)"), *GetOwner()->GetName(), *Action->GetName(), DoubleTapWindow);
	return true;
}

UObject* URPGDodgeTiming::FindDodgeAbility() const
{
	UActorComponent* Asc = Cast<UActorComponent>(FindComponentByClassName(GetOwner(), TEXT("BP_AdvancedAbilitySystemComponent_C")));
	const FArrayProperty* Created = Asc ? FindFProperty<FArrayProperty>(Asc->GetClass(), TEXT("CreatedAbilities")) : nullptr;
	const FObjectProperty* Inner = Created ? CastField<FObjectProperty>(Created->Inner) : nullptr;
	if (!Inner)
	{
		return nullptr;
	}
	FScriptArrayHelper Abilities(Created, Created->ContainerPtrToValuePtr<void>(Asc));
	for (int32 Index = 0; Index < Abilities.Num(); ++Index)
	{
		UObject* Ability = Inner->GetObjectPropertyValue(Abilities.GetRawPtr(Index));
		if (Ability && Ability->GetClass()->GetFName() == DodgeAbilityClassName)
		{
			return Ability;
		}
	}
	return nullptr;
}

bool URPGDodgeTiming::IsAbilityActive(UObject* Ability) const
{
	bool bActive = false;
	CallBlueprintFunction(Ability, TEXT("IsAbilityActive?"), [](UFunction&, uint8*) {},
		[&](UFunction& F, uint8* P)
		{
			for (TFieldIterator<FBoolProperty> It(&F); It; ++It)
			{
				if (It->HasAnyPropertyFlags(CPF_OutParm) && !It->HasAnyPropertyFlags(CPF_ReferenceParm))
				{
					bActive = It->GetPropertyValue_InContainer(P);
				}
			}
		});
	return bActive;
}

bool URPGDodgeTiming::ApplyClip(UObject* Ability, UAnimMontage* Montage, float PlayRate) const
{
	const FMapProperty* Map = Ability ? FindFProperty<FMapProperty>(Ability->GetClass(), MontageMapName) : nullptr;
	const FStructProperty* Value = Map ? CastField<FStructProperty>(Map->ValueProp) : nullptr;
	if (!Value || !Montage)
	{
		return false;
	}
	// The map value is the pack's F_AbilityMontage struct; its field names carry a generated suffix, so find the fields by type and name prefix.
	const FObjectProperty* MontageField = nullptr;
	const FNumericProperty* RateField = nullptr;
	for (TFieldIterator<FProperty> It(Value->Struct); It; ++It)
	{
		if (const FObjectProperty* Object = CastField<FObjectProperty>(*It))
		{
			if (!MontageField && Object->PropertyClass && Object->PropertyClass->IsChildOf(UAnimMontage::StaticClass()))
			{
				MontageField = Object;
			}
		}
		else if (const FNumericProperty* Number = CastField<FNumericProperty>(*It))
		{
			if (!RateField && Number->IsFloatingPoint() && Number->GetName().StartsWith(TEXT("PlayRate")))
			{
				RateField = Number;
			}
		}
	}
	if (!MontageField)
	{
		return false;
	}
	bool bApplied = false;
	FScriptMapHelper Entries(Map, Map->ContainerPtrToValuePtr<void>(Ability));
	for (int32 EntryIndex = 0; EntryIndex < Entries.GetMaxIndex(); ++EntryIndex)
	{
		if (!Entries.IsValidIndex(EntryIndex))
		{
			continue;
		}
		uint8* Struct = Entries.GetValuePtr(EntryIndex);
		MontageField->SetObjectPropertyValue(MontageField->ContainerPtrToValuePtr<void>(Struct), Montage);
		if (RateField)
		{
			RateField->SetFloatingPointPropertyValue(RateField->ContainerPtrToValuePtr<void>(Struct), static_cast<double>(PlayRate));
		}
		bApplied = true;
	}
	return bApplied;
}

bool URPGDodgeTiming::ForceFullRoll(UObject* Ability)
{
	UObject* Asc = FindComponentByClassName(GetOwner(), TEXT("BP_AdvancedAbilitySystemComponent_C"));
	if (!Asc || !Ability)
	{
		return false;
	}
	// A backward turn in progress carries on: the roll goes the same way the quick dodge was turning.
	// The key's release would dodge again through the pack's buffer: mark the dodge input consumed, the same call the pack's sprint makes.
	if (UObject* Buffer = FindComponentByClassName(GetOwner(), TEXT("BP_InputBufferComponent_C")))
	{
		const FGameplayTag Tag = FGameplayTag::RequestGameplayTag(DodgeInputTag, false);
		CallBlueprintFunction(Buffer, TEXT("Add Consumed Buffer Key"),
			[&](UFunction& F, uint8* P)
			{
				SetTag(F, P, TEXT("InputTag"), Tag);
				if (const FBoolProperty* Value = CastField<FBoolProperty>(F.FindPropertyByName(TEXT("Value"))))
				{
					Value->SetPropertyValue_InContainer(P, true);
				}
			},
			[](UFunction&, uint8*) {});
	}
	// End the quick dodge, then activate the ability again (it plays the montage with stop-all-montages, from the pawn's current position).
	CallBlueprintFunction(Asc, TEXT("End Ability"),
		[&](UFunction& F, uint8* P)
		{
			if (const FObjectProperty* Object = CastField<FObjectProperty>(F.FindPropertyByName(TEXT("AbilityToEnd"))))
			{
				Object->SetObjectPropertyValue(Object->ContainerPtrToValuePtr<void>(P), Ability);
			}
		},
		[](UFunction&, uint8*) {});
	bool bSuccess = false;
	CallBlueprintFunction(Asc, TEXT("Try Activate Ability by Class"),
		[&](UFunction& F, uint8* P)
		{
			if (const FClassProperty* ClassProp = CastField<FClassProperty>(F.FindPropertyByName(TEXT("InAbilityClass"))))
			{
				ClassProp->SetPropertyValue_InContainer(P, Ability->GetClass());
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
	return bSuccess;
}

FString URPGDodgeTiming::GetStageName() const
{
	if (!bWasActive)
	{
		return TEXT("None");
	}
	if (Selected == EKind::Backstep)
	{
		return TEXT("Backstep");
	}
	return Selected == EKind::Full ? TEXT("FullRoll") : TEXT("QuickEvade");
}

void URPGDodgeTiming::OnDodgePressed(const FInputActionInstance& Instance)
{
	const UWorld* World = GetWorld();
	UObject* Ability = FindDodgeAbility();
	if (!World || !Ability)
	{
		return;
	}
	const double Now = World->GetTimeSeconds();
	LastPressGap = Now - LastPressTime;
	bLastPressFull = bDoubleTapLongRoll && LastPressGap <= DoubleTapWindow;
	LastPressTime = Now;
	++PressCount;
	UAnimMontage* Quick = QuickMontage.LoadSynchronous();
	UAnimMontage* Full = FullMontage.LoadSynchronous();
	if (!Quick || !Full)
	{
		return;
	}

	const bool bActive = IsAbilityActive(Ability);
	// Elden Ring style backstep (optional clip): no direction input means a hop straight back that keeps facing, whatever the press gap. A running full roll is not interrupted.
	if (UAnimMontage* Backstep = BackstepMontage.IsNull() ? nullptr : BackstepMontage.LoadSynchronous())
	{
		if (RPGDodgeInputRules::DecideTap(!HasNoDirectionInput(), true) == RPGDodgeInputRules::EDodgeTapDecision::Backstep && !(bActive && Selected == EKind::Full))
		{
			Selected = EKind::Backstep;
			bLastPressFull = false;
			++BackstepCount;
			const bool bApplied = ApplyClip(Ability, Backstep, BackstepPlayRate);
			UE_LOG(LogRPGDodge, Log, TEXT("dodge press %d: backstep (no direction input, %s x%.2f, applied %d, dodge running %d)"), PressCount, *Backstep->GetName(), BackstepPlayRate, bApplied, bActive);
			return;
		}
	}
	if (!bLastPressFull)
	{
		Selected = EKind::Quick;
		const bool bApplied = ApplyClip(Ability, Quick, QuickPlayRate);
		UE_LOG(LogRPGDodge, Log, TEXT("dodge press %d: quick dodge (%s x%.2f, applied %d, dodge running %d)"), PressCount, *Quick->GetName(), QuickPlayRate, bApplied, bActive);
		return;
	}
	if (bActive && Selected == EKind::Full)
	{
		++IgnoredPressCount;
		UE_LOG(LogRPGDodge, Log, TEXT("dodge press %d: ignored, a full roll is already running"), PressCount);
		return;
	}
	Selected = EKind::Full;
	const bool bApplied = ApplyClip(Ability, Full, FullPlayRate);
	if (bActive)
	{
		++ForcedRollCount;
		const bool bForced = ForceFullRoll(Ability);
		UE_LOG(LogRPGDodge, Log, TEXT("dodge press %d: full roll over the running quick dodge (%s x%.2f, applied %d, activated %d)"), PressCount, *Full->GetName(), FullPlayRate, bApplied, bForced);
		return;
	}
	UE_LOG(LogRPGDodge, Log, TEXT("dodge press %d: full roll chosen, no dodge running, the pack dodges on release (%s, applied %d)"), PressCount, *Full->GetName(), bApplied);
}

// Owner 2026-11-06 Elden Ring gamepad attack inputs. Kept at the end of the file so existing line citations stay valid.
#include "EnhancedInputSubsystems.h"
#include "InputMappingContext.h"
#include "Engine/LocalPlayer.h"
#include "GameFramework/PlayerController.h"

void URPGDodgeTiming::TryAddEldenRingContext()
{
	if (bEldenRingContextAdded || EldenRingMappingContext.IsNull())
	{
		return;
	}
	const APawn* Pawn = Cast<APawn>(GetOwner());
	const APlayerController* Controller = Pawn ? Cast<APlayerController>(Pawn->GetController()) : nullptr;
	ULocalPlayer* LocalPlayer = Controller ? Controller->GetLocalPlayer() : nullptr;
	UEnhancedInputLocalPlayerSubsystem* InputSubsystem = LocalPlayer ? LocalPlayer->GetSubsystem<UEnhancedInputLocalPlayerSubsystem>() : nullptr;
	if (!InputSubsystem)
	{
		return; // not possessed yet, or not a local player: retried next tick
	}
	UInputMappingContext* Context = EldenRingMappingContext.LoadSynchronous();
	if (!Context)
	{
		UE_LOG(LogRPGDodge, Warning, TEXT("%s: Elden Ring input context %s did not load; the pack's attack inputs stay"), *GetOwner()->GetName(), *EldenRingMappingContext.ToString());
		bEldenRingContextAdded = true; // do not retry every tick
		return;
	}
	if (!InputSubsystem->HasMappingContext(Context))
	{
		InputSubsystem->AddMappingContext(Context, EldenRingMappingPriority);
	}
	bEldenRingContextAdded = true;
	UE_LOG(LogRPGDodge, Log, TEXT("%s: Elden Ring input context %s active at priority %d (R1 press light, R2 tap strong, R2 hold charged)"), *GetOwner()->GetName(), *Context->GetName(), EldenRingMappingPriority);
}

void URPGDodgeTiming::TickEldenRingInput()
{
	const UWorld* World = GetWorld();
	const double Now = World ? World->GetTimeSeconds() : 0.0;
	TickGuardCounterMontageOverride(Now);
	if (!bEldenRingContextAdded)
	{
		return;
	}
	APawn* Pawn = Cast<APawn>(GetOwner());
	if (!bEldenRingActionsBound)
	{
		UEnhancedInputComponent* Input = Pawn ? Cast<UEnhancedInputComponent>(Pawn->InputComponent) : nullptr;
		UInputAction* Light = EldenRingLightAction.LoadSynchronous();
		UInputAction* HeavyTap = EldenRingHeavyTapAction.LoadSynchronous();
		if (!Input || !Light || !HeavyTap)
		{
			return;
		}
		Input->BindAction(Light, ETriggerEvent::Triggered, this, &URPGDodgeTiming::OnEldenRingLight);
		Input->BindAction(HeavyTap, ETriggerEvent::Triggered, this, &URPGDodgeTiming::OnEldenRingHeavyTap);
		bEldenRingActionsBound = true;
	}
	if (Now >= InjectLightUntil && Now >= InjectStrongUntil)
	{
		return;
	}
	const APlayerController* Controller = Pawn ? Cast<APlayerController>(Pawn->GetController()) : nullptr;
	ULocalPlayer* LocalPlayer = Controller ? Controller->GetLocalPlayer() : nullptr;
	UEnhancedInputLocalPlayerSubsystem* InputSubsystem = LocalPlayer ? LocalPlayer->GetSubsystem<UEnhancedInputLocalPlayerSubsystem>() : nullptr;
	if (!InputSubsystem)
	{
		return;
	}
	// The pack reads its own actions as if the key were held for InjectSeconds (press and release), exactly like the PIE drivers press them.
	if (Now < InjectLightUntil)
	{
		if (UInputAction* Action = PackLightAction.LoadSynchronous())
		{
			InputSubsystem->InjectInputForAction(Action, FInputActionValue(true), {}, {});
		}
	}
	if (Now < InjectStrongUntil)
	{
		if (UInputAction* Action = PackStrongAction.LoadSynchronous())
		{
			InputSubsystem->InjectInputForAction(Action, FInputActionValue(true), {}, {});
		}
	}
}

void URPGDodgeTiming::OnEldenRingLight(const FInputActionInstance& Instance)
{
	const UWorld* World = GetWorld();
	const double Now = World ? World->GetTimeSeconds() : 0.0;
	const bool bNewInput = Now >= InjectLightUntil;
	const ACharacter* Character = Cast<ACharacter>(GetOwner());
	const UCharacterMovementComponent* Movement = Character ? Character->GetCharacterMovement() : nullptr;
	if (bNewInput && RPGAirAttackRules::Select(Movement && Movement->IsFalling(), false, !AirLightMontage.IsNull()) == RPGAirAttackRules::EAirAttackRoute::AirLight)
	{
		if (UAnimMontage* Montage = AirLightMontage.Get())
		{
			ApplyMontageArrayOverride(Montage, TEXT("FallingAttackMontages"), ERPGAttackKind::JumpLight);
		}
	}
	InjectLightUntil = Now + InjectSeconds;
	++EldenRingLightCount;
	UE_LOG(LogRPGDodge, Verbose, TEXT("Elden Ring R1 press: light attack replay %d"), EldenRingLightCount);
}

void URPGDodgeTiming::OnEldenRingHeavyTap(const FInputActionInstance& Instance)
{
	const UWorld* World = GetWorld();
	const double Now = World ? World->GetTimeSeconds() : 0.0;
	if (RPGGuardCounterRules::IsCounterPress(LastSuccessfulGuardTime, Now, GuardCounterWindowSeconds))
	{
		LastSuccessfulGuardTime = -1.0e9; // one counter attempt per successful block
		bool bMontageApplied = false;
		if (!GuardCounterMontage.IsNull())
		{
			if (UAnimMontage* Montage = GuardCounterMontage.LoadSynchronous())
			{
				bMontageApplied = ApplyGuardCounterMontageOverride(Montage);
			}
		}
		UE_LOG(LogRPGDodge, Log, TEXT("guard counter accepted after successful block montageApplied=%d fallback=%s"), bMontageApplied ? 1 : 0, bMontageApplied ? TEXT("none") : TEXT("pack strong attack"));
	}
	else if (Now >= InjectStrongUntil)
	{
		const ACharacter* Character = Cast<ACharacter>(GetOwner());
		const UCharacterMovementComponent* Movement = Character ? Character->GetCharacterMovement() : nullptr;
		if (RPGAirAttackRules::Select(Movement && Movement->IsFalling(), true, !AirHeavyMontage.IsNull()) == RPGAirAttackRules::EAirAttackRoute::AirHeavy)
		{
			if (UAnimMontage* Montage = AirHeavyMontage.Get())
			{
				ApplyMontageArrayOverride(Montage, TEXT("StrongAttackMontages"), ERPGAttackKind::JumpHeavy);
			}
		}
	}
	InjectStrongUntil = Now + InjectSeconds;
	++EldenRingStrongCount;
	UE_LOG(LogRPGDodge, Verbose, TEXT("Elden Ring R2 tap: strong attack replay %d"), EldenRingStrongCount);
}

void URPGDodgeTiming::NotifySuccessfulGuardContact()
{
	LastSuccessfulGuardTime = GetWorld() ? GetWorld()->GetTimeSeconds() : -1.0e9;
	UE_LOG(LogRPGDodge, Log, TEXT("successful guarded contact armed guard counter window %.2f s"), GuardCounterWindowSeconds);
}

bool URPGDodgeTiming::IsGuardCounterArmed() const
{
	const UWorld* World = GetWorld();
	return World && RPGGuardCounterRules::IsCounterPress(
		LastSuccessfulGuardTime, World->GetTimeSeconds(), GuardCounterWindowSeconds);
}

void URPGDodgeTiming::DebugArmGuardCounter()
{
#if !UE_BUILD_SHIPPING
	NotifySuccessfulGuardContact();
#endif
}

FString URPGDodgeTiming::DescribeGuardState() const
{
#if UE_BUILD_DEVELOPMENT
	const AActor* GuardOwner = GetOwner();
	if (!GuardOwner)
	{
		return TEXT("guard_state owner=missing");
	}

	FString AbilityRows = TEXT("none");
	FString BlockAbilityRows = TEXT("none");
	int32 AbilityCount = 0;
	UObject* AbilitySystem = FindComponentByClassName(GuardOwner, TEXT("BP_AdvancedAbilitySystemComponent_C"));
	const FArrayProperty* CreatedAbilities = AbilitySystem ? FindFProperty<FArrayProperty>(AbilitySystem->GetClass(), TEXT("CreatedAbilities")) : nullptr;
	const FObjectProperty* AbilityProperty = CreatedAbilities ? CastField<FObjectProperty>(CreatedAbilities->Inner) : nullptr;
	if (AbilityProperty)
	{
		TArray<FString> Rows;
		TArray<FString> BlockRows;
		FScriptArrayHelper Abilities(CreatedAbilities, CreatedAbilities->ContainerPtrToValuePtr<void>(AbilitySystem));
		for (int32 Index = 0; Index < Abilities.Num(); ++Index)
		{
			UObject* Ability = AbilityProperty->GetObjectPropertyValue(Abilities.GetRawPtr(Index));
			if (!Ability)
			{
				Rows.Add(FString::Printf(TEXT("[%d]=<null>"), Index));
				continue;
			}
			const FString ClassName = Ability->GetClass()->GetName();
			const bool bActive = IsAbilityActive(Ability);
			Rows.Add(FString::Printf(TEXT("[%d]=%s active=%d"), Index, *ClassName, bActive ? 1 : 0));
			if (ClassName.Contains(TEXT("block"), ESearchCase::IgnoreCase) || ClassName.Contains(TEXT("guard"), ESearchCase::IgnoreCase))
			{
				BlockRows.Add(FString::Printf(TEXT("%s active=%d"), *ClassName, bActive ? 1 : 0));
			}
		}
		AbilityCount = Rows.Num();
		AbilityRows = FString::Join(Rows, TEXT("; "));
		if (!BlockRows.IsEmpty())
		{
			BlockAbilityRows = FString::Join(BlockRows, TEXT("; "));
		}
	}
	else if (AbilitySystem)
	{
		AbilityRows = TEXT("CreatedAbilities property missing or not an object array");
	}
	else
	{
		AbilityRows = TEXT("ability system missing");
	}

	FGameplayTagContainer OwnedTags;
	bool bOwnedTagsRead = false;
	RPGPack::CallBlueprintFunction(const_cast<AActor*>(GuardOwner), TEXT("GetOwnedGameplayTags"),
		[](UFunction&, uint8*) {},
		[&](UFunction& Function, uint8* Params)
		{
			for (TFieldIterator<FStructProperty> It(&Function); It; ++It)
			{
				if (It->Struct == FGameplayTagContainer::StaticStruct() && It->HasAnyPropertyFlags(CPF_ReturnParm))
				{
					OwnedTags = *It->ContainerPtrToValuePtr<FGameplayTagContainer>(Params);
					bOwnedTagsRead = true;
					break;
				}
			}
		});
	if (!bOwnedTagsRead)
	{
		const FStructProperty* GameplayTagsProperty = FindFProperty<FStructProperty>(GuardOwner->GetClass(), TEXT("GameplayTags"));
		if (GameplayTagsProperty && GameplayTagsProperty->Struct == FGameplayTagContainer::StaticStruct())
		{
			OwnedTags = *GameplayTagsProperty->ContainerPtrToValuePtr<FGameplayTagContainer>(GuardOwner);
			bOwnedTagsRead = true;
		}
	}
	TArray<FString> TagRows;
	if (bOwnedTagsRead)
	{
		for (const FGameplayTag& Tag : OwnedTags.GetGameplayTagArray())
		{
			TagRows.Add(Tag.ToString());
		}
	}
	const FString TagList = bOwnedTagsRead ? (TagRows.IsEmpty() ? TEXT("<empty>") : FString::Join(TagRows, TEXT(", "))) : TEXT("GetOwnedGameplayTags missing/unreadable");
	const bool bBlocking = RPGBossDamage::HasTag(const_cast<AActor*>(GuardOwner), TEXT("Status.Blocking"));
	const bool bStateBlocking = RPGBossDamage::HasTag(const_cast<AActor*>(GuardOwner), TEXT("State.Blocking"));
	const bool bAbilityBlock = RPGBossDamage::HasTag(const_cast<AActor*>(GuardOwner), TEXT("Ability.Block"));
	return FString::Printf(TEXT("owner=%s abilityCount=%d abilities={%s} blockAbilities={%s} ownedTags={%s} statusBlocking=%d stateBlocking=%d abilityBlock=%d"),
		*GuardOwner->GetName(), AbilityCount, *AbilityRows, *BlockAbilityRows, *TagList,
		bBlocking ? 1 : 0, bStateBlocking ? 1 : 0, bAbilityBlock ? 1 : 0);
#else
	return TEXT("guard_state unavailable outside Development builds");
#endif
}

bool URPGDodgeTiming::ApplyGuardCounterMontageOverride(UAnimMontage* Montage)
{
	return ApplyMontageArrayOverride(Montage, TEXT("StrongAttackMontages"), ERPGAttackKind::Strong);
}

ERPGAttackKind URPGDodgeTiming::GetActiveMontageOverrideKind(const UAnimMontage* Montage) const
{
	const UAnimMontage* ActiveMontage = ActiveOverrideMontage.Get();
	return RPGResolveActiveMontageOverride(Montage, ActiveMontage, ActiveOverrideKind);
}

bool URPGDodgeTiming::ApplyMontageArrayOverride(UAnimMontage* Montage, FName ArrayName, ERPGAttackKind Kind)
{
	if (!Montage)
	{
		return false;
	}
	RestoreGuardCounterMontageOverride();
	UObject* Asc = FindComponentByClassName(GetOwner(), TEXT("BP_AdvancedAbilitySystemComponent_C"));
	const FArrayProperty* Created = Asc ? FindFProperty<FArrayProperty>(Asc->GetClass(), TEXT("CreatedAbilities")) : nullptr;
	const FObjectProperty* Inner = Created ? CastField<FObjectProperty>(Created->Inner) : nullptr;
	if (!Inner)
	{
		return false;
	}

	bool bAnyApplied = false;
	FScriptArrayHelper Abilities(Created, Created->ContainerPtrToValuePtr<void>(Asc));
	for (int32 Index = 0; Index < Abilities.Num(); ++Index)
	{
		UObject* Ability = Inner->GetObjectPropertyValue(Abilities.GetRawPtr(Index));
		if (!Ability || !Ability->GetClass()->FindPropertyByName(TEXT("AttackMontages")))
		{
			continue;
		}
		const FArrayProperty* MontageArray = FindFProperty<FArrayProperty>(Ability->GetClass(), ArrayName);
		if (!MontageArray || !MontageArray->Inner)
		{
			continue;
		}
		const FObjectPropertyBase* DirectObject = CastField<FObjectPropertyBase>(MontageArray->Inner);
		const FStructProperty* EntryStruct = CastField<FStructProperty>(MontageArray->Inner);
		const FObjectPropertyBase* MontageField = nullptr;
		FNumericProperty* PlayRateField = nullptr;
		if (EntryStruct && EntryStruct->Struct)
		{
			for (TFieldIterator<FProperty> Field(EntryStruct->Struct); Field; ++Field)
			{
				if (const FObjectPropertyBase* Object = CastField<FObjectPropertyBase>(*Field))
				{
					if (!MontageField && Object->GetName().StartsWith(TEXT("AnimMontage")) && Object->PropertyClass.Get() && Object->PropertyClass->IsChildOf(UAnimMontage::StaticClass()))
					{
						MontageField = Object;
					}
				}
				else if (FNumericProperty* Number = CastField<FNumericProperty>(*Field))
				{
					if (Number->IsFloatingPoint() && Number->GetName().StartsWith(TEXT("PlayRate")))
					{
						PlayRateField = Number;
					}
				}
			}
		}
		if (!DirectObject && !MontageField)
		{
			continue;
		}
		if (DirectObject && DirectObject->PropertyClass.Get() && !Montage->GetClass()->IsChildOf(DirectObject->PropertyClass.Get()))
		{
			continue;
		}

		FRPGGuardCounterArrayBackup Backup;
		Backup.Ability = Ability;
		Backup.PropertyName = ArrayName;
		MontageArray->ExportTextItem_Direct(Backup.ExportedArray, MontageArray->ContainerPtrToValuePtr<void>(Ability), nullptr, Ability, PPF_None);
		FScriptArrayHelper Entries(MontageArray, MontageArray->ContainerPtrToValuePtr<void>(Ability));
		if (Entries.Num() == 0)
		{
			continue;
		}
		Entries.EmptyValues();
		Entries.AddValue();
		uint8* Element = Entries.GetRawPtr(0);
		if (DirectObject)
		{
			DirectObject->SetObjectPropertyValue(Element, Montage);
		}
		else
		{
			MontageField->SetObjectPropertyValue(MontageField->ContainerPtrToValuePtr<void>(Element), Montage);
			if (PlayRateField)
			{
				PlayRateField->SetFloatingPointPropertyValue(PlayRateField->ContainerPtrToValuePtr<void>(Element), 1.0);
			}
		}
		GuardCounterArrayBackups.Add(MoveTemp(Backup));
		bAnyApplied = true;
	}
	if (!bAnyApplied)
	{
		RestoreGuardCounterMontageOverride();
		return false;
	}
	ActiveOverrideMontage = Montage;
	ActiveOverrideKind = Kind;
	bActiveOverrideStarted = false;
	GuardCounterOverrideEndTime = (GetWorld() ? GetWorld()->GetTimeSeconds() : 0.0) + 1.0;
	return true;
}

void URPGDodgeTiming::RestoreMontageArrayBackups()
{
	for (const FRPGGuardCounterArrayBackup& Backup : GuardCounterArrayBackups)
	{
		UObject* Ability = Backup.Ability.Get();
		const FArrayProperty* MontageArray = Ability && !Backup.PropertyName.IsNone() ? FindFProperty<FArrayProperty>(Ability->GetClass(), Backup.PropertyName) : nullptr;
		if (MontageArray && !Backup.ExportedArray.IsEmpty())
		{
			MontageArray->ImportText_Direct(*Backup.ExportedArray, MontageArray->ContainerPtrToValuePtr<void>(Ability), Ability, PPF_None, nullptr);
		}
	}
	GuardCounterArrayBackups.Reset();
}

void URPGDodgeTiming::RestoreGuardCounterMontageOverride()
{
	RestoreMontageArrayBackups();
	ActiveOverrideMontage.Reset();
	ActiveOverrideKind = ERPGAttackKind::Unknown;
	bActiveOverrideStarted = false;
	GuardCounterOverrideEndTime = -1.0;
}

void URPGDodgeTiming::TickGuardCounterMontageOverride(double Now)
{
	UAnimMontage* Montage = ActiveOverrideMontage.Get();
	if (!Montage)
	{
		if (!GuardCounterArrayBackups.IsEmpty())
		{
			RestoreGuardCounterMontageOverride();
		}
		return;
	}
	bool bPlaying = false;
	if (const ACharacter* Character = Cast<ACharacter>(GetOwner()))
	{
		TArray<USkeletalMeshComponent*> Meshes;
		Character->GetComponents<USkeletalMeshComponent>(Meshes);
		for (USkeletalMeshComponent* Mesh : Meshes)
		{
			if (UAnimInstance* Anim = Mesh ? Mesh->GetAnimInstance() : nullptr; Anim && Anim->Montage_IsPlaying(Montage))
			{
				bPlaying = true;
				break;
			}
		}
	}
	if (bPlaying)
	{
		bActiveOverrideStarted = true;
		// Restore the pack's arrays as soon as playback begins, but retain the
		// montage's semantic kind until that montage exits so the swing tracker
		// and hit intake can classify it on later ticks.
		RestoreMontageArrayBackups();
	}
	else if (bActiveOverrideStarted || Now >= GuardCounterOverrideEndTime)
	{
		RestoreGuardCounterMontageOverride();
	}
}
