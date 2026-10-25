// Copyright One Boss Fight. All Rights Reserved.

#include "Player/RPGBuildLoadout.h"
#include "Pack/RPGBlueprintCall.h"
#include "Pack/RPGPackReflect.h"
#include "Player/RPGBossEncounter.h"
#include "Player/RPGPlayerMovesSubsystem.h"
#include "Animation/AnimInstance.h"
#include "Components/SkeletalMeshComponent.h"
#include "EngineUtils.h"
#include "GameplayTagContainer.h"
#include "Engine/World.h"
#include "GameFramework/Character.h"
#include "HAL/IConsoleManager.h"
#include "UObject/UnrealType.h"

DEFINE_LOG_CATEGORY_STATIC(LogRPGBuild, Log, All);

static TAutoConsoleVariable<FString> CVarRPGBuild(TEXT("rpg.Build"), TEXT(""),
	TEXT("Build of the player (Gate 3): Starter (the pack's sword), Strength (claymore) or Dex (dual swords); empty = no choice, the player keeps the weapon the pack gives and nothing is called. The build is equipped while the boss sleeps; a choice made during the fight waits for the next one."),
	ECVF_Default);

using namespace RPGPack;
namespace Rules = RPGBuildRules;

namespace
{
	/** A field of a Blueprint struct by the start of its name: the pack's struct fields carry a number and a GUID (Items_17_<guid>), so they cannot be named in full. */
	const FProperty* FieldByPrefix(const UStruct* Struct, const TCHAR* Prefix)
	{
		for (TFieldIterator<FProperty> It(Struct); It; ++It)
		{
			if (It->GetName().StartsWith(Prefix))
			{
				return *It;
			}
		}
		return nullptr;
	}

	/** An integer or byte field (the pack's enum fields are bytes) of a struct in memory. */
	bool ReadIntField(const FProperty* Property, void* Container, int64& OutValue)
	{
		if (const FNumericProperty* Number = CastField<FNumericProperty>(Property))
		{
			OutValue = Number->GetSignedIntPropertyValue(Number->ContainerPtrToValuePtr<void>(Container));
			return true;
		}
		if (const FEnumProperty* Enum = CastField<FEnumProperty>(Property))
		{
			OutValue = Enum->GetUnderlyingProperty()->GetSignedIntPropertyValue(Enum->ContainerPtrToValuePtr<void>(Container));
			return true;
		}
		return false;
	}

	/** Sets a byte or integer parameter of a pack function by name (a call from C++ must set the enum bytes itself: they start at 0). */
	bool SetIntParam(UFunction& Function, uint8* Params, const TCHAR* Name, int64 Value)
	{
		const FProperty* Property = Function.FindPropertyByName(Name);
		if (const FNumericProperty* Number = CastField<FNumericProperty>(Property))
		{
			Number->SetIntPropertyValue(Number->ContainerPtrToValuePtr<void>(Params), Value);
			return true;
		}
		if (const FEnumProperty* Enum = CastField<FEnumProperty>(Property))
		{
			Enum->GetUnderlyingProperty()->SetIntPropertyValue(Enum->ContainerPtrToValuePtr<void>(Params), Value);
			return true;
		}
		return false;
	}

	/**
	 * The pack's Blueprint enums are plain bytes whose VALUE is the enumerator's position in the list, not the number in its name (NewEnumerator11 may be the byte 5): the weapon slot byte and the update type bytes are found
	 * from the enums at run time. The plan's numbers are only the fallback (review of M13). The report text is logged once and readable from tests.
	 */
	int32 GWeaponSlotByte = Rules::WeaponSlotEnumerator;
	bool GWeaponSlotResolved = false;
	int32 GUpdateByte = 0;
	int32 GReplaceByte = 1;
	bool GUpdateResolved = false;
	FString GEnumReport = TEXT("not read yet");

	const UEnum* EnumOfProperty(const FProperty* Property)
	{
		if (const FEnumProperty* Enum = CastField<FEnumProperty>(Property))
		{
			return Enum->GetEnum();
		}
		if (const FNumericProperty* Number = CastField<FNumericProperty>(Property))
		{
			return Number->GetIntPropertyEnum();
		}
		return nullptr;
	}

	/** The value of the enumerator with this internal name (NewEnumerator11) or, with bByDisplay, this display name (Update); the whole list goes into OutList. */
	bool FindEnumValue(const UEnum* Enum, const TCHAR* Name, bool bByDisplay, int64& OutValue, FString& OutList)
	{
		OutList.Reset();
		if (!Enum)
		{
			OutList = TEXT("no enum on the property");
			return false;
		}
		bool bFound = false;
		for (int32 Index = 0; Index < Enum->NumEnums(); ++Index)
		{
			const FString Short = Enum->GetNameStringByIndex(Index);
			const FString Display = Enum->GetDisplayNameTextByIndex(Index).ToString();
			OutList += FString::Printf(TEXT("%d=%s(%s) "), static_cast<int32>(Enum->GetValueByIndex(Index)), *Short, *Display);
			if (!bFound && (bByDisplay ? Display : Short).Equals(Name, ESearchCase::IgnoreCase))
			{
				OutValue = Enum->GetValueByIndex(Index);
				bFound = true;
			}
		}
		return bFound;
	}

	/** Finds the byte of the weapon slot (the enumerator NewEnumerator<WeaponSlotEnumerator> of the slot struct's EquipSlot_ enum) once. */
	void ResolveWeaponSlotByte(const UObject* Equipment)
	{
		if (GWeaponSlotResolved || !Equipment)
		{
			return;
		}
		const FArrayProperty* Slots = CastField<FArrayProperty>(Equipment->GetClass()->FindPropertyByName(TEXT("EquipmentSlots")));
		const FStructProperty* SlotInner = Slots ? CastField<FStructProperty>(Slots->Inner) : nullptr;
		const FProperty* TypeField = (SlotInner && SlotInner->Struct) ? FieldByPrefix(SlotInner->Struct, TEXT("EquipSlot_")) : nullptr;
		if (!TypeField)
		{
			return; // the pack is not ready: asked again at the next call
		}
		GWeaponSlotResolved = true;
		int64 Value = 0;
		FString List;
		const FString Name = FString::Printf(TEXT("NewEnumerator%d"), Rules::WeaponSlotEnumerator);
		if (FindEnumValue(EnumOfProperty(TypeField), *Name, false, Value, List))
		{
			GWeaponSlotByte = static_cast<int32>(Value);
			GEnumReport = FString::Printf(TEXT("weapon slot %s is the byte %d; E_EquipSlots: %s"), *Name, GWeaponSlotByte, *List);
			UE_LOG(LogRPGBuild, Log, TEXT("%s"), *GEnumReport);
		}
		else
		{
			GEnumReport = FString::Printf(TEXT("no enumerator %s in E_EquipSlots (%s): the byte %d (the number of the name) is used, probably the wrong slot"), *Name, *List, GWeaponSlotByte);
			UE_LOG(LogRPGBuild, Warning, TEXT("%s"), *GEnumReport);
		}
	}

	/** Finds the bytes of E_EquipUpdateType's Update and Replace entries (by display name) once, from the UpdateType parameter of Update Equip Slot Item. */
	void ResolveUpdateBytes(const UFunction& Function)
	{
		if (GUpdateResolved)
		{
			return;
		}
		const UEnum* Enum = EnumOfProperty(Function.FindPropertyByName(TEXT("UpdateType")));
		if (!Enum)
		{
			return;
		}
		GUpdateResolved = true;
		int64 Value = 0;
		FString List;
		const bool bUpdate = FindEnumValue(Enum, TEXT("Update"), true, Value, List);
		if (bUpdate)
		{
			GUpdateByte = static_cast<int32>(Value);
		}
		const bool bReplace = FindEnumValue(Enum, TEXT("Replace"), true, Value, List);
		if (bReplace)
		{
			GReplaceByte = static_cast<int32>(Value);
		}
		const FString Report = FString::Printf(TEXT("update types: Update=%d%s, Replace=%d%s; E_EquipUpdateType: %s"), GUpdateByte, bUpdate ? TEXT("") : TEXT(" (fallback)"), GReplaceByte, bReplace ? TEXT("") : TEXT(" (fallback)"), *List);
		GEnumReport += TEXT(" | ") + Report;
		UE_LOG(LogRPGBuild, Log, TEXT("%s"), *Report);
	}

	/** What the weapon slot of the equipment component holds now. The pointers point into the component's arrays: use them before anything calls the pack. */
	struct FWeaponSlotInfo
	{
		/** The slot's ActiveItemIndex (the item the pack uses now). */
		int32 ActiveIndex = 0;
		/** The index of the slot's weapon item: the first item that is not a catalyst (the player's default slot is the sword and the magic staff, probe 2026-10-22). The build replaces THIS item, never the staff. */
		int32 WeaponIndex = 0;
		int32 ItemCount = 0;
		/** The struct type of the slot's items (F_ItemSlot) and the active item in memory, the template of the new item. Null when the slot has no item. */
		const UScriptStruct* ItemStruct = nullptr;
		const void* Template = nullptr;
	};

	/** Finds the weapon slot (EquipSlot_ equals the weapon enumerator) in the component's EquipmentSlots array. */
	bool ReadWeaponSlot(UObject* Equipment, FWeaponSlotInfo& Out, FString& OutWhy)
	{
		ResolveWeaponSlotByte(Equipment);
		const FArrayProperty* Slots = CastField<FArrayProperty>(Equipment->GetClass()->FindPropertyByName(TEXT("EquipmentSlots")));
		const FStructProperty* SlotInner = Slots ? CastField<FStructProperty>(Slots->Inner) : nullptr;
		if (!SlotInner || !SlotInner->Struct)
		{
			OutWhy = TEXT("BP_EquipmentComponent_C has no EquipmentSlots array of structs");
			return false;
		}
		const FProperty* TypeField = FieldByPrefix(SlotInner->Struct, TEXT("EquipSlot_"));
		const FProperty* ActiveField = FieldByPrefix(SlotInner->Struct, TEXT("ActiveItemIndex_"));
		const FArrayProperty* ItemsField = CastField<FArrayProperty>(FieldByPrefix(SlotInner->Struct, TEXT("Items_")));
		const FStructProperty* ItemInner = ItemsField ? CastField<FStructProperty>(ItemsField->Inner) : nullptr;
		if (!TypeField || !ItemInner || !ItemInner->Struct)
		{
			OutWhy = TEXT("the equipment slot struct has no EquipSlot_ field or no Items_ array of structs");
			return false;
		}
		FScriptArrayHelper SlotArray(Slots, Slots->ContainerPtrToValuePtr<void>(Equipment));
		for (int32 Index = 0; Index < SlotArray.Num(); ++Index)
		{
			uint8* SlotData = SlotArray.GetRawPtr(Index);
			int64 Type = -1;
			if (!ReadIntField(TypeField, SlotData, Type) || Type != GWeaponSlotByte)
			{
				continue;
			}
			int64 Active = 0;
			if (ActiveField)
			{
				ReadIntField(ActiveField, SlotData, Active);
			}
			FScriptArrayHelper ItemArray(ItemsField, ItemsField->ContainerPtrToValuePtr<void>(SlotData));
			Out.ItemCount = ItemArray.Num();
			Out.ItemStruct = ItemInner->Struct.Get();
			Out.ActiveIndex = FMath::Max(static_cast<int32>(Active), 0);
			Out.WeaponIndex = Out.ActiveIndex;
			const FObjectPropertyBase* ItemObject = CastField<FObjectPropertyBase>(FieldByPrefix(ItemInner->Struct, TEXT("Item_")));
			for (int32 Item = 0; ItemObject && Item < Out.ItemCount; ++Item)
			{
				const UObject* Object = ItemObject->GetObjectPropertyValue(ItemObject->ContainerPtrToValuePtr<void>(ItemArray.GetRawPtr(Item)));
				if (Object && !Object->GetClass()->GetName().Contains(TEXT("Catalyst")))
				{
					Out.WeaponIndex = Item;
					break;
				}
			}
			Out.Template = Out.ItemCount > 0 ? ItemArray.GetRawPtr(FMath::Clamp(Out.WeaponIndex, 0, Out.ItemCount - 1)) : nullptr;
			return true;
		}
		OutWhy = FString::Printf(TEXT("EquipmentSlots has no slot of the byte %d (the weapon slot; %s)"), GWeaponSlotByte, *GEnumReport.Left(200));
		return false;
	}
}

URPGBuildLoadout::URPGBuildLoadout()
{
	PrimaryComponentTick.bCanEverTick = true;
	PrimaryComponentTick.TickInterval = 0.1f; // a poll, not a frame: the HUD and the apply need no per-frame answer
}

void URPGBuildLoadout::BeginPlay()
{
	Super::BeginPlay();
	StartTime = GetWorld() ? GetWorld()->GetTimeSeconds() : 0.0;
	AddEvent(FString::Printf(TEXT("started, rpg.Build is '%s'"), *CVarRPGBuild.GetValueOnGameThread()));
}

void URPGBuildLoadout::TickComponent(float DeltaTime, ELevelTick TickType, FActorComponentTickFunction* ThisTickFunction)
{
	Super::TickComponent(DeltaTime, TickType, ThisTickFunction);
	Poll();
}

// ---------------------------------------------------------------------------------------------
// Getters and test hooks
// ---------------------------------------------------------------------------------------------

FString URPGBuildLoadout::GetBuildName() const
{
	ERPGBuild Build = ERPGBuild::Starter;
	if (Rules::BuildOfStyle(ActualStyle, Build))
	{
		return Rules::BuildName(Build);
	}
	return ActualStyle.IsNone() ? FString(TEXT("Unknown")) : FString(TEXT("OffBuild"));
}

FString URPGBuildLoadout::GetChosenBuildName() const
{
	return Rules::BuildName(bExplicit ? Chosen : ERPGBuild::Starter);
}

FString URPGBuildLoadout::GetBuildLine() const
{
	return Rules::BuildLine(ActualStyle, LastDecision);
}

FString URPGBuildLoadout::GetStateName() const
{
	switch (LastDecision)
	{
	case Rules::EDecision::Done: return TEXT("Idle");
	case Rules::EDecision::Apply: return TEXT("Applying");
	case Rules::EDecision::Wait: return (Attempts > 0 && LastAttemptTime >= 0.0) ? TEXT("Applying") : TEXT("Waiting");
	case Rules::EDecision::Defer: return TEXT("Deferred");
	case Rules::EDecision::GiveUp: return TEXT("Failed");
	}
	return TEXT("Idle");
}

FString URPGBuildLoadout::GetPackEnumReport() const
{
	return GEnumReport;
}

FString URPGBuildLoadout::GetWeaponSlotReport() const
{
	UObject* Equipment = FindComponentByClassName(GetOwner(), TEXT("BP_EquipmentComponent_C"));
	if (!Equipment)
	{
		return TEXT("no equipment component");
	}
	ResolveWeaponSlotByte(Equipment);
	const FArrayProperty* Slots = CastField<FArrayProperty>(Equipment->GetClass()->FindPropertyByName(TEXT("EquipmentSlots")));
	const FStructProperty* SlotInner = Slots ? CastField<FStructProperty>(Slots->Inner) : nullptr;
	const FProperty* TypeField = (SlotInner && SlotInner->Struct) ? FieldByPrefix(SlotInner->Struct, TEXT("EquipSlot_")) : nullptr;
	const FArrayProperty* ItemsField = (SlotInner && SlotInner->Struct) ? CastField<FArrayProperty>(FieldByPrefix(SlotInner->Struct, TEXT("Items_"))) : nullptr;
	if (!TypeField || !ItemsField)
	{
		return TEXT("no EquipmentSlots array");
	}
	FScriptArrayHelper SlotArray(Slots, Slots->ContainerPtrToValuePtr<void>(Equipment));
	for (int32 Index = 0; Index < SlotArray.Num(); ++Index)
	{
		uint8* SlotData = SlotArray.GetRawPtr(Index);
		int64 Type = -1;
		if (!ReadIntField(TypeField, SlotData, Type) || Type != GWeaponSlotByte)
		{
			continue;
		}
		FString Text;
		SlotInner->ExportTextItem_Direct(Text, SlotData, nullptr, nullptr, PPF_None);
		return FString::Printf(TEXT("slot byte %d: %s"), GWeaponSlotByte, *Text.Left(2500));
	}
	return TEXT("no weapon slot in EquipmentSlots");
}

bool URPGBuildLoadout::IsWeaponSlotLocked() const
{
	// The lock is the quickslot ability blocked on the player's ability system component: our own flag says whether we hold the block (the count of the blocked tag is the component's).
	return bLocked;
}

bool URPGBuildLoadout::IsCombatEnabled() const
{
	const UObject* Combat = FindComponentByClassName(GetOwner(), TEXT("BP_CombatComponent_C"));
	return Combat && RPGPackReflect::ReadBool(Combat, TEXT("bIsCombatEnabled?"));
}

FString URPGBuildLoadout::GetEquippedActorClassName() const
{
	UObject* Equipment = FindComponentByClassName(GetOwner(), TEXT("BP_EquipmentComponent_C"));
	ResolveWeaponSlotByte(Equipment);
	FString Name;
	CallBlueprintFunction(Equipment, TEXT("Get Active Equipped Actor"),
		[](UFunction& F, uint8* P) { SetIntParam(F, P, TEXT("EquipSlot"), GWeaponSlotByte); },
		[&](UFunction& F, uint8* P)
		{
			if (const FObjectPropertyBase* Value = CastField<FObjectPropertyBase>(F.FindPropertyByName(TEXT("Value"))))
			{
				if (const UObject* Actor = Value->GetObjectPropertyValue(Value->ContainerPtrToValuePtr<void>(P)))
				{
					Name = Actor->GetClass()->GetName();
				}
			}
		});
	return Name;
}

bool URPGBuildLoadout::HasWeaponAbilityForTest(const FString& ClassName) const
{
	return FindAbilityByClassName(GetOwner(), FName(*ClassName)) != nullptr;
}

FString URPGBuildLoadout::SetBuild(const FString& Name)
{
	ERPGBuild Build = ERPGBuild::Starter;
	const Rules::EParse Parsed = Rules::Parse(Name, Build);
	if (Parsed == Rules::EParse::Invalid)
	{
		++InvalidRequestCount;
		NoteFailure(FString::Printf(TEXT("invalid %s"), *Name), FString::Printf(TEXT("rpg.Build '%s' is not a build (Starter, Strength, Dex or empty): ignored"), *Name));
		return TEXT("Invalid");
	}
	const bool bSame = (Parsed == Rules::EParse::Build) ? (bExplicit && Chosen == Build) : !bExplicit;
	// The same variable the console sets, with the console's priority, so the choice also survives a respawn (the next pawn's loadout reads it).
	if (IConsoleVariable* Variable = IConsoleManager::Get().FindConsoleVariable(TEXT("rpg.Build")))
	{
		Variable->Set(*Name, ECVF_SetByConsole);
	}
	Poll();
	if (bSame)
	{
		return TEXT("Same");
	}
	if (Parsed == Rules::EParse::Empty)
	{
		return TEXT("Cleared");
	}
	return LastDecision == Rules::EDecision::Defer ? TEXT("Deferred") : TEXT("Accepted");
}

FString URPGBuildLoadout::SetBuildForTest(const FString& Name)
{
#if UE_BUILD_SHIPPING
	return TEXT("unavailable in Shipping");
#else
	return SetBuild(Name);
#endif
}

FString URPGBuildLoadout::ApplyNowForTest()
{
#if UE_BUILD_SHIPPING
	return TEXT("unavailable in Shipping");
#else
	Poll();
	return Rules::DecisionName(LastDecision);
#endif
}

void URPGBuildLoadout::SetApplyOnlyOutOfCombatForTest(bool bOnlyOutOfCombat)
{
#if !UE_BUILD_SHIPPING
	bApplyOnlyOutOfCombat = bOnlyOutOfCombat;
#endif
}

void URPGBuildLoadout::SetLockWeaponSlotForTest(bool bLock)
{
#if !UE_BUILD_SHIPPING
	bLockWeaponSlotInFight = bLock;
#endif
}

void URPGBuildLoadout::ResetCountersForTest()
{
#if !UE_BUILD_SHIPPING
	ApplyCallCount = 0;
	ApplySuccessCount = 0;
	ApplyFailureCount = 0;
	DeferredCount = 0;
	InvalidRequestCount = 0;
	LockCount = 0;
	UnlockCount = 0;
	LockBreachCount = 0;
	Events.Reset();
#endif
}

// ---------------------------------------------------------------------------------------------
// The poll
// ---------------------------------------------------------------------------------------------

void URPGBuildLoadout::AddEvent(const FString& Text)
{
	const UWorld* World = GetWorld();
	Events.Add(FString::Printf(TEXT("%.1f s: %s"), World ? World->GetTimeSeconds() : 0.0, *Text));
	if (Events.Num() > 32)
	{
		Events.RemoveAt(0);
	}
	UE_LOG(LogRPGBuild, Log, TEXT("%s: %s"), *GetNameSafe(GetOwner()), *Text);
}

void URPGBuildLoadout::NoteFailure(const FString& Key, const FString& Message)
{
	LastResult = Message;
	if (!Warned.Contains(Key))
	{
		Warned.Add(Key);
		UE_LOG(LogRPGBuild, Warning, TEXT("%s: %s"), *GetNameSafe(GetOwner()), *Message);
	}
}

void URPGBuildLoadout::ResetRequest()
{
	Attempts = 0;
	CallFailureStreak = 0;
	LastAttemptTime = -1.0;
	LastDecision = Rules::EDecision::Done;
}

void URPGBuildLoadout::ReadChoice()
{
	const FString Text = CVarRPGBuild.GetValueOnGameThread();
	if (bChoiceRead && Text == ChoiceText)
	{
		return;
	}
	const bool bFirst = !bChoiceRead;
	bChoiceRead = true;
	ChoiceText = Text;
	ERPGBuild Build = ERPGBuild::Starter;
	switch (Rules::Parse(Text, Build))
	{
	case Rules::EParse::Empty:
		if (bExplicit)
		{
			bExplicit = false;
			ResetRequest();
			LastResult = TEXT("no build chosen");
			AddEvent(TEXT("the choice was cleared: the loadout calls nothing and the weapon stays as it is"));
		}
		break;
	case Rules::EParse::Build:
		if (bExplicit && Chosen == Build)
		{
			break; // the same build in another spelling
		}
		bExplicit = true;
		Chosen = Build;
		ResetRequest();
		LastResult = FString::Printf(TEXT("build %s chosen"), Rules::BuildName(Build));
		AddEvent(FString::Printf(TEXT("build %s chosen (rpg.Build '%s'%s)"), Rules::BuildName(Build), *Text, bFirst ? TEXT(", the value at the start") : TEXT("")));
		break;
	case Rules::EParse::Invalid:
		++InvalidRequestCount;
		NoteFailure(FString::Printf(TEXT("invalid %s"), *Text), FString::Printf(TEXT("rpg.Build '%s' is not a build (Starter, Strength, Dex or empty): ignored"), *Text));
		break;
	}
}

FName URPGBuildLoadout::ReadStyle() const
{
	const UObject* Combat = FindComponentByClassName(GetOwner(), TEXT("BP_CombatComponent_C"));
	const UObject* Style = Combat ? RPGPackReflect::ReadObject(Combat, TEXT("CurrentCombatStyle")) : nullptr;
	return Style ? Style->GetFName() : NAME_None;
}

bool URPGBuildLoadout::IsPlayerDead() const
{
	double Health = 0.0;
	return ReadAttribute(GetOwner(), TEXT("Attribute.Health"), /*bMax=*/false, Health) && Health <= 0.0;
}

bool URPGBuildLoadout::IsPlayerBusy() const
{
	const ACharacter* Character = Cast<ACharacter>(GetOwner());
	const USkeletalMeshComponent* Mesh = Character ? Character->GetMesh() : nullptr;
	const UAnimInstance* Anim = Mesh ? Mesh->GetAnimInstance() : nullptr;
	return Anim && Anim->GetCurrentActiveMontage() != nullptr;
}

URPGBossEncounter* URPGBuildLoadout::FindEncounter(double Now)
{
	if (const AActor* Boss = BossActor.Get())
	{
		return Boss->FindComponentByClass<URPGBossEncounter>();
	}
	const UWorld* World = GetWorld();
	if (!World || Now < NextBossSearch)
	{
		return nullptr;
	}
	NextBossSearch = Now + 0.5;
	for (TActorIterator<APawn> It(World); It; ++It)
	{
		if (URPGPlayerMovesSubsystem::IsPackBoss(*It))
		{
			if (URPGBossEncounter* Encounter = It->FindComponentByClass<URPGBossEncounter>())
			{
				BossActor = *It;
				return Encounter;
			}
		}
	}
	return nullptr;
}

bool URPGBuildLoadout::SyncLock(bool bBossPresent, bool bBossDormant)
{
	// Only while a build is chosen: with no choice the loadout calls nothing in the pack, so a default run is the run it always was.
	const bool bWant = Rules::ShouldLockSlot(bLockWeaponSlotInFight && bExplicit, bBossPresent, bBossDormant);
	if (bWant == bLocked)
	{
		LockFailureStreak = 0;
		return false;
	}
	if (LockFailureStreak >= FMath::Max(MaxAttempts, 1))
	{
		if (!bWant)
		{
			bLocked = false; // the pack cannot be asked to unlock: our own flag must not keep the equip waiting for ever
		}
		return false; // the pack would not take it: not asked again until the wish changes
	}
	if (!CallSetSlotDisabled(bWant))
	{
		++LockFailureStreak;
		NoteFailure(TEXT("lock"), FString::Printf(TEXT("%s the quickslot ability tag could not be called on the pawn's ability system component (Ability.Quickslot registered? AddBlockedAbilityTags there?)"), bWant ? TEXT("blocking") : TEXT("unblocking")));
		return false;
	}
	bLocked = bWant;
	LockFailureStreak = 0;
	if (bWant)
	{
		++LockCount;
	}
	else
	{
		++UnlockCount;
	}
	AddEvent(bWant ? TEXT("the boss is awake: the quickslot ability is blocked (the weapon cannot be cycled)") : TEXT("the boss sleeps or is gone (or no build is chosen): the quickslot ability is free again"));
	return true;
}

bool URPGBuildLoadout::CallSetSlotDisabled(bool bDisable)
{
	// The quickslot cycle is blocked on the player's ability system component: the pack's quickslot abilities all carry the ability tag Ability.Quickslot (GA_Quickslot), a blocked tag keeps them from activating, so the weapon cannot leave the build. Not the equipment slot's own disabled flags: the whole-slot flag
	// switches the weapon's hits off (probe 2026-10-22: 0 hits with every weapon) and the per item flag does not stop the cycle. The blocked tags are counted by the component: this is called only when the wish changes.
	UObject* Asc = FindComponentByClassName(GetOwner(), TEXT("BP_AdvancedAbilitySystemComponent_C"));
	const FGameplayTag Tag = FGameplayTag::RequestGameplayTag(FName(TEXT("Ability.Quickslot")), false);
	if (!Asc || !Tag.IsValid())
	{
		return false;
	}
	return CallBlueprintFunction(Asc, bDisable ? TEXT("AddBlockedAbilityTags") : TEXT("RemoveBlockedAbilityTags"),
		[&](UFunction& F, uint8* P)
		{
			if (const FStructProperty* Container = CastField<FStructProperty>(F.FindPropertyByName(bDisable ? TEXT("TagsToAdd") : TEXT("TagsToRemove"))))
			{
				Container->ContainerPtrToValuePtr<FGameplayTagContainer>(P)->AddTag(Tag);
			}
		},
		[](UFunction&, uint8*) {});
}

bool URPGBuildLoadout::CallEquip(ERPGBuild Build, int32 UpdateType, FString& OutResult)
{
	UObject* Equipment = FindComponentByClassName(GetOwner(), TEXT("BP_EquipmentComponent_C"));
	if (!Equipment)
	{
		OutResult = TEXT("the pawn has no BP_EquipmentComponent_C");
		return false;
	}
	const Rules::FBuildEntry& Wanted = Rules::Entry(Build);
	UObject* Item = LoadObject<UObject>(nullptr, Wanted.ItemPath, nullptr, LOAD_NoWarn);
	if (!Item)
	{
		OutResult = FString::Printf(TEXT("the weapon item %s did not load"), Wanted.ItemPath);
		return false;
	}
	// Everything the call needs is checked before it is made: a pack that changed must not get a half-built struct.
	const UFunction* Function = Equipment->FindFunction(FName(TEXT("Update Equip Slot Item")));
	const FStructProperty* NewItemParam = Function ? CastField<FStructProperty>(Function->FindPropertyByName(FName(TEXT("NewItem")))) : nullptr;
	const FObjectPropertyBase* ItemField = (NewItemParam && NewItemParam->Struct) ? CastField<FObjectPropertyBase>(FieldByPrefix(NewItemParam->Struct, TEXT("Item_"))) : nullptr;
	if (!NewItemParam || !ItemField)
	{
		OutResult = TEXT("Update Equip Slot Item has no NewItem struct parameter with an Item_ object field");
		return false;
	}
	const UClass* NeededClass = ItemField->PropertyClass.Get();
	if (!NeededClass || !Item->GetClass()->IsChildOf(NeededClass))
	{
		OutResult = FString::Printf(TEXT("the Item_ field holds %s, the weapon item %s is a %s"), NeededClass ? *NeededClass->GetName() : TEXT("?"), *Item->GetName(), *Item->GetClass()->GetName());
		return false;
	}
	FWeaponSlotInfo Slot;
	FString Why;
	if (!ReadWeaponSlot(Equipment, Slot, Why))
	{
		OutResult = Why;
		return false;
	}
	if (Slot.ItemCount > 1 && Slot.ActiveIndex != Slot.WeaponIndex)
	{
		// The player has cycled to another item (the magic staff): the weapon item is made active first (the pack's own cycle), replacing the active item would destroy the staff. The next poll makes the real call.
		CallBlueprintFunction(Equipment, TEXT("Next Equip Slot Active Index"), [&](UFunction& F, uint8* P) { SetIntParam(F, P, TEXT("InEquipSlotType"), GWeaponSlotByte); }, [](UFunction&, uint8*) {});
		OutResult = FString::Printf(TEXT("the active item is %d, the weapon item is %d: the pack was asked to cycle to the weapon item first"), Slot.ActiveIndex, Slot.WeaponIndex);
		return false;
	}
	const bool bCopyable = Slot.Template && Slot.ItemStruct == NewItemParam->Struct.Get();

	FString ItemText;
	bool bSuccess = false;
	bool bHaveSuccess = false;
	const bool bCalled = CallBlueprintFunction(Equipment, TEXT("Update Equip Slot Item"),
		[&](UFunction& F, uint8* P)
		{
			ResolveUpdateBytes(F);
			SetIntParam(F, P, TEXT("EquipSlotType"), GWeaponSlotByte);
			SetIntParam(F, P, TEXT("ItemIndex"), Slot.WeaponIndex); // the weapon item of the slot (active at this point) is replaced, never the staff
			SetIntParam(F, P, TEXT("UpdateType"), UpdateType == 0 ? GUpdateByte : GReplaceByte); // 0 = Update, else Replace: the bytes come from the pack's enum
			void* NewItem = NewItemParam->ContainerPtrToValuePtr<void>(P);
			if (bCopyable)
			{
				NewItemParam->Struct->CopyScriptStruct(NewItem, Slot.Template); // amount, index and flags of the item that is there now
			}
			ItemField->SetObjectPropertyValue(ItemField->ContainerPtrToValuePtr<void>(NewItem), Item);
			NewItemParam->ExportTextItem_Direct(ItemText, NewItem, nullptr, nullptr, PPF_None);
		},
		[&](UFunction& F, uint8* P)
		{
			if (const FBoolProperty* Success = CastField<FBoolProperty>(F.FindPropertyByName(TEXT("Success?"))))
			{
				bSuccess = Success->GetPropertyValue_InContainer(P);
				bHaveSuccess = true;
			}
		});
	if (!bCalled)
	{
		OutResult = TEXT("BP_EquipmentComponent_C has no function Update Equip Slot Item");
		return false;
	}
	OutResult = FString::Printf(TEXT("Update Equip Slot Item(slot byte %d, index %d of %d, update type %s = byte %d, item %s%s) returned %s; new item struct %s"), GWeaponSlotByte, Slot.WeaponIndex, Slot.ItemCount, UpdateType == 0 ? TEXT("Update") : TEXT("Replace"), UpdateType == 0 ? GUpdateByte : GReplaceByte, *Item->GetName(),
		bCopyable ? TEXT(", copied from the active item") : TEXT(", from the struct defaults"), bHaveSuccess ? (bSuccess ? TEXT("Success? true") : TEXT("Success? false")) : TEXT("no Success? output"), *ItemText.Left(300));
	return true;
}

void URPGBuildLoadout::Poll()
{
	AActor* Pawn = GetOwner();
	const UWorld* World = GetWorld();
	if (!Pawn || !World)
	{
		return;
	}
	const double Now = World->GetTimeSeconds();
	ReadChoice();

	// What the player holds and what the pack has.
	UObject* Combat = FindComponentByClassName(Pawn, TEXT("BP_CombatComponent_C"));
	UObject* Equipment = FindComponentByClassName(Pawn, TEXT("BP_EquipmentComponent_C"));
	if (!bWiringChecked && Combat && Equipment)
	{
		bWiringChecked = true;
		FString Missing;
		if (CheckPackSignatures(Combat->GetClass(), Equipment->GetClass(), Missing))
		{
			WiringReport = TEXT("ok");
		}
		else
		{
			WiringReport = FString::Printf(TEXT("missing: %s"), *Missing);
			NoteFailure(TEXT("wiring"), FString::Printf(TEXT("the pack changed, the loadout cannot find: %s"), *Missing));
		}
	}
	const FName Style = ReadStyle();
	if (Style != ActualStyle)
	{
		if (bLocked && !ActualStyle.IsNone())
		{
			++LockBreachCount;
		}
		AddEvent(FString::Printf(TEXT("combat style %s -> %s%s"), *ActualStyle.ToString(), *Style.ToString(), bLocked ? TEXT(" (the weapon slot is locked: the lock did not hold)") : TEXT("")));
		ActualStyle = Style;
	}

	// The boss: no boss at all counts as dormant (the pack destroys a dead one), a new fight (generation) starts the attempts again.
	const URPGBossEncounter* Encounter = FindEncounter(Now);
	const bool bBossPresent = Encounter != nullptr;
	const bool bBossDormant = !Encounter || Encounter->IsDormant();
	if (Encounter && Encounter->GetGeneration() != LastGeneration)
	{
		if (LastGeneration != 0)
		{
			ResetRequest();
			AddEvent(FString::Printf(TEXT("a new fight (generation %d): the attempts start again"), Encounter->GetGeneration()));
		}
		LastGeneration = Encounter->GetGeneration();
	}
	const bool bLockChanged = SyncLock(bBossPresent, bBossDormant);

	Rules::FDecideInput In;
	FWeaponSlotInfo WeaponSlot;
	FString WeaponSlotWhy;
	const bool bWeaponSlotReady = bExplicit && Equipment && ReadWeaponSlot(Equipment, WeaponSlot, WeaponSlotWhy);
	In.bExplicit = bExplicit;
	// Do not use CurrentCombatStyle as the readiness gate. On a cold spawn the pack can report None until the weapon item is equipped;
	// once EquipmentSlots has the weapon slot, Apply restores that item instead of waiting forever for a style that cannot appear by itself.
	In.bStyleKnown = Combat && bWeaponSlotReady && (Now - StartTime) >= StartupDelaySeconds;
	In.bStyleMatches = Rules::StyleMatchesBuild(Style, Chosen);
	In.bBossAwake = !bBossDormant;
	// The pack is only asked what the decision needs: with no choice nothing is read from it besides the style.
	In.bPlayerDead = bExplicit && IsPlayerDead();
	In.bPlayerBusy = bExplicit && IsPlayerBusy();
	In.bPlayerInCombat = bExplicit && IsCombatEnabled();
	In.bCombatBlocksApply = bApplyOnlyOutOfCombat;
	In.Attempts = Attempts;
	In.MaxAttempts = FMath::Max(MaxAttempts, 1);
	In.SecondsSinceAttempt = LastAttemptTime >= 0.0 ? static_cast<float>(Now - LastAttemptTime) : -1.f;
	In.VerifySeconds = VerifySeconds;
	Rules::EDecision Decision = Rules::Decide(In);
	if (Decision == Rules::EDecision::Apply && (bLockChanged || bLocked))
	{
		Decision = Rules::EDecision::Wait; // the slot is still disabled, or was enabled in this very poll: the pack gets a poll before the equip
	}

	if (Decision == Rules::EDecision::Done && bExplicit && In.bStyleMatches && Attempts > 0)
	{
		++ApplySuccessCount;
		LastResult = FString::Printf(TEXT("build %s equipped (style %s) after %d call(s)"), Rules::BuildName(Chosen), *Style.ToString(), Attempts);
		AddEvent(LastResult);
		ResetRequest();
	}
	if (Decision != LastDecision)
	{
		if (Decision == Rules::EDecision::Defer)
		{
			++DeferredCount;
			LastResult = FString::Printf(TEXT("build %s waits for the fight to end"), Rules::BuildName(Chosen));
			AddEvent(LastResult);
		}
		else if (Decision == Rules::EDecision::GiveUp)
		{
			++ApplyFailureCount;
			const FString Message = FString::Printf(TEXT("build %s gave up after %d call(s): the style is still %s (the last call: %s)"), Rules::BuildName(Chosen), Attempts, *Style.ToString(), *LastResult);
			NoteFailure(Message, Message);
			AddEvent(Message);
		}
	}
	LastDecision = Decision;

	if (Decision == Rules::EDecision::Apply)
	{
		const int32 UpdateType = Rules::UpdateTypeForAttempt(Attempts + 1);
		FString Result;
		const bool bCalled = CallEquip(Chosen, UpdateType, Result);
		if (bCalled)
		{
			CallFailureStreak = 0;
			++Attempts;
			++ApplyCallCount;
			LastAttemptTime = Now;
			LastResult = Result;
			AddEvent(FString::Printf(TEXT("call %d of %d for build %s: %s"), Attempts, MaxAttempts, Rules::BuildName(Chosen), *Result));
			AddEvent(FString::Printf(TEXT("style right after the call: %s (wanted %s)"), *ReadStyle().ToString(), Rules::StyleOfBuild(Chosen)));
		}
		else
		{
			// Nothing was called, so nothing is verified and no attempt is used: the pack may just not be ready (slot array, item). Only a failure that lasts (CallFailureLimit polls, 2 s) uses an attempt.
			LastAttemptTime = -1.0;
			if (++CallFailureStreak >= CallFailureLimit)
			{
				CallFailureStreak = 0;
				++Attempts;
			}
			NoteFailure(Result, FString::Printf(TEXT("call for build %s could not be made (%d of %d attempts used): %s"), Rules::BuildName(Chosen), Attempts, MaxAttempts, *Result));
			AddEvent(LastResult);
		}
	}
}

// ---------------------------------------------------------------------------------------------
// The pack names the loadout calls
// ---------------------------------------------------------------------------------------------

bool URPGBuildLoadout::CheckPackSignatures(const UClass* CombatClass, const UClass* EquipmentClass, FString& OutMissing)
{
	OutMissing.Reset();
	auto NeedProperty = [&OutMissing](const UClass* Class, const TCHAR* Name)
	{
		if (!Class || !Class->FindPropertyByName(FName(Name)))
		{
			OutMissing += FString::Printf(TEXT("%s.%s; "), Class ? *Class->GetName() : TEXT("?"), Name);
		}
	};
	auto NeedParam = [&OutMissing](const UClass* Class, const TCHAR* Function, const TCHAR* Param)
	{
		const UFunction* Found = Class ? Class->FindFunctionByName(FName(Function)) : nullptr;
		if (!Found || !Found->FindPropertyByName(FName(Param)))
		{
			OutMissing += FString::Printf(TEXT("%s(%s); "), Function, Param);
		}
	};

	NeedProperty(CombatClass, TEXT("CurrentCombatStyle"));
	NeedProperty(CombatClass, TEXT("bIsCombatEnabled?"));

	const FArrayProperty* Slots = EquipmentClass ? CastField<FArrayProperty>(EquipmentClass->FindPropertyByName(TEXT("EquipmentSlots"))) : nullptr;
	const FStructProperty* SlotInner = Slots ? CastField<FStructProperty>(Slots->Inner) : nullptr;
	if (!SlotInner || !SlotInner->Struct)
	{
		OutMissing += TEXT("BP_EquipmentComponent_C.EquipmentSlots (array of structs); ");
	}
	else
	{
		for (const TCHAR* Prefix : {TEXT("EquipSlot_"), TEXT("ActiveItemIndex_"), TEXT("Items_")})
		{
			if (!FieldByPrefix(SlotInner->Struct, Prefix))
			{
				OutMissing += FString::Printf(TEXT("equipment slot field %s*; "), Prefix);
			}
		}
		const FArrayProperty* Items = CastField<FArrayProperty>(FieldByPrefix(SlotInner->Struct, TEXT("Items_")));
		const FStructProperty* ItemInner = Items ? CastField<FStructProperty>(Items->Inner) : nullptr;
		if (!ItemInner || !ItemInner->Struct || !FieldByPrefix(ItemInner->Struct, TEXT("Item_")))
		{
			OutMissing += TEXT("item slot field Item_*; ");
		}
	}

	for (const TCHAR* Param : {TEXT("EquipSlotType"), TEXT("NewItem"), TEXT("ItemIndex"), TEXT("UpdateType"), TEXT("Success?")})
	{
		NeedParam(EquipmentClass, TEXT("Update Equip Slot Item"), Param);
	}

	for (const TCHAR* Param : {TEXT("InEquipSlot"), TEXT("Value")})
	{
		NeedParam(EquipmentClass, TEXT("Is Equip Slot Disabled?"), Param);
	}
	for (const TCHAR* Param : {TEXT("EquipSlot"), TEXT("Value")})
	{
		NeedParam(EquipmentClass, TEXT("Get Active Equipped Actor"), Param);
	}
	return OutMissing.IsEmpty();
}
