// Copyright One Boss Fight. All Rights Reserved.

#include "Pack/RPGPackTrace.h"
#include "Components/PrimitiveComponent.h"
#include "GameFramework/Actor.h"
#include "GameplayTagContainer.h"
#include "Pack/RPGBlueprintCall.h"
#include "Engine/EngineTypes.h"
#include "Kismet/KismetSystemLibrary.h"

DEFINE_LOG_CATEGORY_STATIC(LogRPGTrace, Log, All);

using namespace RPGPack;

namespace
{
	TSet<FName> WarnedNames;

	void WarnOnce(const TCHAR* What)
	{
		const FName Key(What);
		if (!WarnedNames.Contains(Key))
		{
			WarnedNames.Add(Key);
			UE_LOG(LogRPGTrace, Warning, TEXT("pack trace: %s was not found on the live object"), What);
		}
	}

	FProperty* Find(UObject* Object, const TCHAR* Name)
	{
		FProperty* Property = Object ? FindFProperty<FProperty>(Object->GetClass(), Name) : nullptr;
		if (!Property)
		{
			WarnOnce(Name);
		}
		return Property;
	}

	// Every property and function the facade reads, in one place (the live check and the class check use the same lists).
	const TCHAR* const TargetProperties[] = {TEXT("bCollisionEnabled?"), TEXT("HitActors"), TEXT("CollisionSockets"), TEXT("CollisionRadius"), TEXT("CollisionRadiusModifier"), TEXT("CollisionObjectTypes"), TEXT("Current Collision Mesh"),
		TEXT("ActorsToIgnore"), TEXT("TargetTypeTag"), TEXT("LastSocketLocations"), TEXT("TargetAbility")};
	const TCHAR* const TargetFunctions[] = {TEXT("ClearHitActors"), TEXT("UpdateTraceLocations")};

	void CollectMissing(const UClass* TargetClass, const UClass* CollisionClass, FString& OutMissing)
	{
		for (const TCHAR* Name : TargetProperties)
		{
			if (!FindFProperty<FProperty>(TargetClass, Name))
			{
				OutMissing += FString(Name) + TEXT("; ");
			}
		}
		for (const TCHAR* Function : TargetFunctions)
		{
			if (!TargetClass->FindFunctionByName(FName(Function)))
			{
				OutMissing += FString(Function) + TEXT("(); ");
			}
		}
		if (!CollisionClass->FindFunctionByName(TEXT("DeactivateCollisionByTag")))
		{
			OutMissing += TEXT("DeactivateCollisionByTag(); ");
		}
	}

	double ReadDouble(UObject* Object, const TCHAR* Name, double Fallback)
	{
		if (const FNumericProperty* Property = CastField<FNumericProperty>(Find(Object, Name)))
		{
			const void* Value = Property->ContainerPtrToValuePtr<void>(Object);
			return Property->IsFloatingPoint() ? Property->GetFloatingPointPropertyValue(Value) : static_cast<double>(Property->GetSignedIntPropertyValue(Value));
		}
		return Fallback;
	}

	/** The hit actors array property of the target and its inner object property. */
	bool HitArray(UObject* Object, const FArrayProperty*& OutArray, const FObjectProperty*& OutInner)
	{
		OutArray = CastField<FArrayProperty>(Find(Object, TEXT("HitActors")));
		OutInner = OutArray ? CastField<FObjectProperty>(OutArray->Inner) : nullptr;
		return OutArray && OutInner;
	}
}

bool RPGPackTrace::FTarget::Resolve(const AActor* Boss, FName Tag)
{
	if (IsValid())
	{
		return true;
	}
	UObject* CollisionComponent = FindComponentByClassName(Boss, TEXT("BP_CollisionComponent_C"));
	if (!CollisionComponent)
	{
		return false; // the pack creates it at BeginPlay: try again later, no warning
	}
	const FArrayProperty* Created = CastField<FArrayProperty>(Find(CollisionComponent, TEXT("CreatedTargetTypes")));
	const FObjectProperty* Inner = Created ? CastField<FObjectProperty>(Created->Inner) : nullptr;
	if (!Inner)
	{
		return false;
	}
	const FGameplayTag Wanted = FGameplayTag::RequestGameplayTag(Tag, false);
	FScriptArrayHelper Array(Created, Created->ContainerPtrToValuePtr<void>(CollisionComponent));
	for (int32 Index = 0; Index < Array.Num(); ++Index)
	{
		UObject* Target = Inner->GetObjectPropertyValue(Array.GetRawPtr(Index));
		const FStructProperty* TagProperty = Target ? CastField<FStructProperty>(Find(Target, TEXT("TargetTypeTag"))) : nullptr;
		if (TagProperty && TagProperty->Struct == TBaseStructure<FGameplayTag>::Get())
		{
			const FGameplayTag* Value = TagProperty->ContainerPtrToValuePtr<FGameplayTag>(Target);
			if (Value && *Value == Wanted)
			{
				Collision = CollisionComponent;
				Object = Target;
				return true;
			}
		}
	}
	return false;
}

bool RPGPackTrace::FTarget::IsActive() const
{
	UObject* Target = Object.Get();
	if (!Target)
	{
		return false;
	}
	if (const FBoolProperty* Flag = CastField<FBoolProperty>(Find(Target, TEXT("bCollisionEnabled?"))))
	{
		return Flag->GetPropertyValue_InContainer(Target);
	}
	return false;
}

int32 RPGPackTrace::FTarget::GetHitSetNum() const
{
	UObject* Target = Object.Get();
	const FArrayProperty* Array = nullptr;
	const FObjectProperty* Inner = nullptr;
	if (!Target || !HitArray(Target, Array, Inner))
	{
		return 0;
	}
	return FScriptArrayHelper(Array, Array->ContainerPtrToValuePtr<void>(Target)).Num();
}

void RPGPackTrace::FTarget::GetHitSet(TArray<AActor*>& Out) const
{
	Out.Reset();
	UObject* Target = Object.Get();
	const FArrayProperty* ArrayProperty = nullptr;
	const FObjectProperty* Inner = nullptr;
	if (!Target || !HitArray(Target, ArrayProperty, Inner))
	{
		return;
	}
	FScriptArrayHelper Array(ArrayProperty, ArrayProperty->ContainerPtrToValuePtr<void>(Target));
	for (int32 Index = 0; Index < Array.Num(); ++Index)
	{
		if (AActor* Actor = Cast<AActor>(Inner->GetObjectPropertyValue(Array.GetRawPtr(Index))))
		{
			Out.Add(Actor);
		}
	}
}

bool RPGPackTrace::FTarget::HitSetContains(const AActor* Actor) const
{
	TArray<AActor*> Set;
	GetHitSet(Set);
	return Set.Contains(Actor);
}

bool RPGPackTrace::FTarget::HitSetAdd(AActor* Actor)
{
	UObject* Target = Object.Get();
	const FArrayProperty* ArrayProperty = nullptr;
	const FObjectProperty* Inner = nullptr;
	if (!Target || !Actor || !HitArray(Target, ArrayProperty, Inner) || HitSetContains(Actor))
	{
		return false;
	}
	FScriptArrayHelper Array(ArrayProperty, ArrayProperty->ContainerPtrToValuePtr<void>(Target));
	const int32 Index = Array.AddValue();
	Inner->SetObjectPropertyValue(Array.GetRawPtr(Index), Actor);
	return true;
}

bool RPGPackTrace::FTarget::HitSetRemove(AActor* Actor)
{
	UObject* Target = Object.Get();
	const FArrayProperty* ArrayProperty = nullptr;
	const FObjectProperty* Inner = nullptr;
	if (!Target || !HitArray(Target, ArrayProperty, Inner))
	{
		return false;
	}
	FScriptArrayHelper Array(ArrayProperty, ArrayProperty->ContainerPtrToValuePtr<void>(Target));
	for (int32 Index = 0; Index < Array.Num(); ++Index)
	{
		if (Inner->GetObjectPropertyValue(Array.GetRawPtr(Index)) == Actor)
		{
			Array.RemoveValues(Index, 1);
			return true;
		}
	}
	return false;
}

UPrimitiveComponent* RPGPackTrace::FTarget::GetMesh() const
{
	UObject* Target = Object.Get();
	if (const FObjectProperty* Mesh = Target ? CastField<FObjectProperty>(Find(Target, TEXT("Current Collision Mesh"))) : nullptr)
	{
		return Cast<UPrimitiveComponent>(Mesh->GetObjectPropertyValue_InContainer(Target));
	}
	return nullptr;
}

void RPGPackTrace::FTarget::GetSockets(TArray<FName>& Out) const
{
	Out.Reset();
	UObject* Target = Object.Get();
	const FArrayProperty* ArrayProperty = Target ? CastField<FArrayProperty>(Find(Target, TEXT("CollisionSockets"))) : nullptr;
	const FNameProperty* Inner = ArrayProperty ? CastField<FNameProperty>(ArrayProperty->Inner) : nullptr;
	if (!Inner)
	{
		return;
	}
	FScriptArrayHelper Array(ArrayProperty, ArrayProperty->ContainerPtrToValuePtr<void>(Target));
	for (int32 Index = 0; Index < Array.Num(); ++Index)
	{
		Out.Add(Inner->GetPropertyValue(Array.GetRawPtr(Index)));
	}
}

double RPGPackTrace::FTarget::GetBaseRadius() const
{
	return ReadDouble(Object.Get(), TEXT("CollisionRadius"), -1.0);
}

double RPGPackTrace::FTarget::GetRadiusModifier() const
{
	return ReadDouble(Object.Get(), TEXT("CollisionRadiusModifier"), 0.0);
}

bool RPGPackTrace::FTarget::HasAbility() const
{
	UObject* Target = Object.Get();
	const FObjectProperty* Ability = Target ? CastField<FObjectProperty>(Find(Target, TEXT("TargetAbility"))) : nullptr;
	return Ability && Ability->GetObjectPropertyValue_InContainer(Target) != nullptr;
}

bool RPGPackTrace::FTarget::GetStoredLocation(FName Socket, FVector& Out) const
{
	UObject* Target = Object.Get();
	const FMapProperty* Map = Target ? CastField<FMapProperty>(Find(Target, TEXT("LastSocketLocations"))) : nullptr;
	const FNameProperty* KeyProperty = Map ? CastField<FNameProperty>(Map->KeyProp) : nullptr;
	const FStructProperty* ValueProperty = Map ? CastField<FStructProperty>(Map->ValueProp) : nullptr;
	if (!KeyProperty || !ValueProperty || ValueProperty->Struct != TBaseStructure<FVector>::Get())
	{
		return false;
	}
	FScriptMapHelper Helper(Map, Map->ContainerPtrToValuePtr<void>(Target));
	for (int32 Index = 0, Remaining = Helper.Num(); Remaining > 0; ++Index)
	{
		if (!Helper.IsValidIndex(Index))
		{
			continue;
		}
		--Remaining;
		const FName Key = KeyProperty->GetPropertyValue(Helper.GetKeyPtr(Index));
		if (Key.ToString().EndsWith(Socket.ToString()))
		{
			Out = *reinterpret_cast<const FVector*>(Helper.GetValuePtr(Index));
			return true;
		}
	}
	return false;
}

void RPGPackTrace::FTarget::GetObjectChannels(TArray<TEnumAsByte<ECollisionChannel>>& Out) const
{
	Out.Reset();
	UObject* Target = Object.Get();
	const FArrayProperty* ArrayProperty = Target ? CastField<FArrayProperty>(Find(Target, TEXT("CollisionObjectTypes"))) : nullptr;
	const FByteProperty* Inner = ArrayProperty ? CastField<FByteProperty>(ArrayProperty->Inner) : nullptr;
	if (!Inner)
	{
		return;
	}
	FScriptArrayHelper Array(ArrayProperty, ArrayProperty->ContainerPtrToValuePtr<void>(Target));
	for (int32 Index = 0; Index < Array.Num(); ++Index)
	{
		const uint8 Query = Inner->GetPropertyValue(Array.GetRawPtr(Index)); // EObjectTypeQuery
		Out.Add(UEngineTypes::ConvertToCollisionChannel(static_cast<EObjectTypeQuery>(Query)));
	}
}

void RPGPackTrace::FTarget::GetActorsToIgnore(TArray<AActor*>& Out) const
{
	Out.Reset();
	UObject* Target = Object.Get();
	const FArrayProperty* ArrayProperty = Target ? CastField<FArrayProperty>(Find(Target, TEXT("ActorsToIgnore"))) : nullptr;
	const FObjectProperty* Inner = ArrayProperty ? CastField<FObjectProperty>(ArrayProperty->Inner) : nullptr;
	if (!Inner)
	{
		return;
	}
	FScriptArrayHelper Array(ArrayProperty, ArrayProperty->ContainerPtrToValuePtr<void>(Target));
	for (int32 Index = 0; Index < Array.Num(); ++Index)
	{
		if (AActor* Actor = Cast<AActor>(Inner->GetObjectPropertyValue(Array.GetRawPtr(Index))))
		{
			Out.Add(Actor);
		}
	}
}

bool RPGPackTrace::FTarget::Deactivate(FName Tag)
{
	UObject* Component = Collision.Get();
	const FGameplayTag Wanted = FGameplayTag::RequestGameplayTag(Tag, false);
	return Component && CallBlueprintFunction(Component, TEXT("DeactivateCollisionByTag"), [&Wanted](UFunction& F, uint8* P) { SetTag(F, P, TEXT("CollisionTargetTag"), Wanted); }, [](UFunction&, uint8*) {});
}

void RPGPackTrace::FTarget::ClearHitSet()
{
	if (UObject* Target = Object.Get())
	{
		CallBlueprintFunction(Target, TEXT("ClearHitActors"), [](UFunction&, uint8*) {}, [](UFunction&, uint8*) {});
	}
}

void RPGPackTrace::FTarget::RefreshPrevious()
{
	if (UObject* Target = Object.Get())
	{
		CallBlueprintFunction(Target, TEXT("UpdateTraceLocations"), [](UFunction&, uint8*) {}, [](UFunction&, uint8*) {});
	}
}

bool RPGPackTrace::CheckLiveNames(const AActor* Boss, FString& OutMissing)
{
	OutMissing.Reset();
	FTarget Target;
	if (!Target.Resolve(Boss))
	{
		OutMissing = TEXT("the boss's BP_CollisionComponent_C or its MainWeapon target type");
		return false;
	}
	CollectMissing(Target.Object.Get()->GetClass(), Target.Collision.Get()->GetClass(), OutMissing);
	return OutMissing.IsEmpty();
}

bool RPGPackTrace::CheckClassNames(FString& OutMissing)
{
	OutMissing.Reset();
	const UClass* TargetClass = LoadClass<UObject>(nullptr, TEXT("/Game/AdvancedARPGCombat/AdvancedCombatFramework/CoreCombatSystem/Collision/BP_EnemyAbilitySweepingTraceTarget.BP_EnemyAbilitySweepingTraceTarget_C"));
	const UClass* CollisionClass = LoadClass<UObject>(nullptr, TEXT("/Game/AdvancedARPGCombat/AdvancedCombatFramework/CollisionSystem/BP_CollisionComponent.BP_CollisionComponent_C"));
	if (!TargetClass || !CollisionClass)
	{
		OutMissing = TEXT("the pack's trace classes (BP_EnemyAbilitySweepingTraceTarget_C, BP_CollisionComponent_C) could not be loaded");
		return false;
	}
	CollectMissing(TargetClass, CollisionClass, OutMissing);
	return OutMissing.IsEmpty();
}
