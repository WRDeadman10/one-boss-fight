// Copyright One Boss Fight. All Rights Reserved.

#include "Player/RPGDodgeTiming.h"
#include "Player/RPGStartupChronology.h"
#include "Player/RPGFlipbookEffect.h"
#include "Pack/RPGBlueprintCall.h"
#include "Animation/AnimMontage.h"
#include "Components/CapsuleComponent.h"
#include "EnhancedInputComponent.h"
#include "GameFramework/Character.h"
#include "GameFramework/CharacterMovementComponent.h"
#include "GameFramework/Pawn.h"
#include "GameplayTagContainer.h"
#include "InputAction.h"
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
		TEXT("/Game/AdvancedARPGCombat/MeleeCombatSystem/Animations/Dodge/Dodge_To_Idle_Montage.Dodge_To_Idle_Montage")));
}

void URPGDodgeTiming::BeginPlay()
{
	RPGStartupChronology::AtComponentBeginPlay(*this);
	Super::BeginPlay();
	LoadedDodgeDustFlipbook = ARPGFlipbookEffect::LoadMaterial(ERPGEFlipbookKind::DodgeDust);
	TryBind();
}

void URPGDodgeTiming::TickComponent(float DeltaTime, ELevelTick TickType, FActorComponentTickFunction* ThisTickFunction)
{
	Super::TickComponent(DeltaTime, TickType, ThisTickFunction);
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
	if (!bBackwardWithoutInput)
	{
		return;
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
	UObject* Asc = FindComponentByClassName(GetOwner(), TEXT("BP_AdvancedAbilitySystemComponent_C"));
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
	bLastPressFull = LastPressGap <= DoubleTapWindow;
	LastPressTime = Now;
	++PressCount;
	UAnimMontage* Quick = QuickMontage.LoadSynchronous();
	UAnimMontage* Full = FullMontage.LoadSynchronous();
	if (!Quick || !Full)
	{
		return;
	}

	const bool bActive = IsAbilityActive(Ability);
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
