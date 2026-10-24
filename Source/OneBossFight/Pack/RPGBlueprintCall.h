// Copyright One Boss Fight. All Rights Reserved.

#pragma once

#include "CoreMinimal.h"
#include "GameplayTagContainer.h"
#include "UObject/ObjectKey.h"
#include "UObject/UnrealType.h"

DECLARE_LOG_CATEGORY_EXTERN(LogRPGPack, Log, All);

/** Helpers for calling the Advanced ARPG pack, which is Blueprint only, by function name through reflection. */
namespace RPGPack
{
	inline UObject* FindComponentByClassName(const AActor* Actor, const TCHAR* ClassName);

	struct FAttributeCallCacheEntry
	{
		TWeakObjectPtr<AActor> Actor;
		TWeakObjectPtr<UObject> Component;
		TMap<FName, TWeakObjectPtr<UFunction>> Functions;
	};

	inline TMap<FObjectKey, FAttributeCallCacheEntry>& AttributeCallCache()
	{
		static TMap<FObjectKey, FAttributeCallCacheEntry> Cache;
		return Cache;
	}

	inline bool IsCurrentAttributeComponent(const FAttributeCallCacheEntry& Entry, const AActor* Actor)
	{
		const UActorComponent* Component = Cast<UActorComponent>(Entry.Component.Get());
		return Entry.Actor.Get() == Actor && Component && Component->GetOwner() == Actor;
	}

	inline FAttributeCallCacheEntry& GetAttributeCallCacheEntry(const AActor* Actor)
	{
		TMap<FObjectKey, FAttributeCallCacheEntry>& Cache = AttributeCallCache();
		for (auto It = Cache.CreateIterator(); It; ++It)
		{
			if (!It.Value().Actor.IsValid() || !It.Value().Component.IsValid())
			{
				It.RemoveCurrent();
			}
		}

		FAttributeCallCacheEntry& Entry = Cache.FindOrAdd(FObjectKey(Actor));
		if (!IsCurrentAttributeComponent(Entry, Actor))
		{
			Entry.Actor = const_cast<AActor*>(Actor);
			Entry.Component = FindComponentByClassName(Actor, TEXT("BP_AttributesComponent_C"));
			Entry.Functions.Reset();
		}
		return Entry;
	}

	inline UFunction* FindCachedAttributeFunction(const AActor* Actor, const TCHAR* FunctionName)
	{
		if (!Actor)
		{
			return nullptr;
		}
		FAttributeCallCacheEntry& Entry = GetAttributeCallCacheEntry(Actor);
		UObject* Attributes = Entry.Component.Get();
		if (!Attributes)
		{
			return nullptr;
		}

		const FName Name(FunctionName);
		if (const TWeakObjectPtr<UFunction>* CachedFunction = Entry.Functions.Find(Name))
		{
			if (UFunction* Function = CachedFunction->Get())
			{
				return Function;
			}
		}

		UFunction* Function = Attributes->FindFunction(Name);
		if (!Function)
		{
			UE_LOG(LogRPGPack, Warning, TEXT("%s has no function '%s'"), *Attributes->GetName(), FunctionName);
			return nullptr;
		}
		Entry.Functions.Add(Name, Function);
		return Function;
	}

	inline UObject* FindCachedAttributesComponent(const AActor* Actor)
	{
		return Actor ? GetAttributeCallCacheEntry(Actor).Component.Get() : nullptr;
	}

	inline bool CallBlueprintFunction(UObject* Target, UFunction* Function, TFunctionRef<void(UFunction&, uint8*)> Fill, TFunctionRef<void(UFunction&, uint8*)> Read)
	{
		if (!Target || !Function)
		{
			return false;
		}
		uint8* Params = static_cast<uint8*>(FMemory_Alloca(Function->ParmsSize));
		FMemory::Memzero(Params, Function->ParmsSize);
		for (TFieldIterator<FProperty> It(Function); It && It->HasAnyPropertyFlags(CPF_Parm); ++It)
		{
			It->InitializeValue_InContainer(Params);
		}
		Fill(*Function, Params);
		Target->ProcessEvent(Function, Params);
		Read(*Function, Params);
		for (TFieldIterator<FProperty> It(Function); It && It->HasAnyPropertyFlags(CPF_Parm); ++It)
		{
			It->DestroyValue_InContainer(Params);
		}
		return true;
	}

	/** Calls a Blueprint function by name. Fill sets the inputs, Read gets the outputs; returns false if the function is missing. */
	inline bool CallBlueprintFunction(UObject* Target, const TCHAR* FunctionName, TFunctionRef<void(UFunction&, uint8*)> Fill, TFunctionRef<void(UFunction&, uint8*)> Read)
	{
		if (!Target)
		{
			return false;
		}
		UFunction* Function = Target->FindFunction(FName(FunctionName));
		if (!Function)
		{
			UE_LOG(LogRPGPack, Warning, TEXT("%s has no function '%s'"), *Target->GetName(), FunctionName);
			return false;
		}
		return CallBlueprintFunction(Target, Function, Fill, Read);
	}

	inline void SetTag(UFunction& Function, uint8* Params, const TCHAR* ParamName, const FGameplayTag& Tag)
	{
		if (const FStructProperty* Prop = CastField<FStructProperty>(Function.FindPropertyByName(ParamName)))
		{
			*Prop->ContainerPtrToValuePtr<FGameplayTag>(Params) = Tag;
		}
	}

	inline double ReadNumber(UFunction& Function, uint8* Params, const TCHAR* ParamName)
	{
		if (const FNumericProperty* Prop = CastField<FNumericProperty>(Function.FindPropertyByName(ParamName)))
		{
			const void* Value = Prop->ContainerPtrToValuePtr<void>(Params);
			return Prop->IsFloatingPoint() ? Prop->GetFloatingPointPropertyValue(Value) : static_cast<double>(Prop->GetSignedIntPropertyValue(Value));
		}
		return 0.0;
	}

	/** First component of the actor whose class name matches (pack classes are Blueprints, so they cannot be named in C++). */
	inline UObject* FindComponentByClassName(const AActor* Actor, const TCHAR* ClassName)
	{
		if (!Actor)
		{
			return nullptr;
		}
		TInlineComponentArray<UActorComponent*> Components(Actor);
		for (UActorComponent* Component : Components)
		{
			if (Component && Component->GetClass()->GetName() == ClassName)
			{
				return Component;
			}
		}
		return nullptr;
	}

	/** The ability instance of the actor's ability system component whose class has this name (for example GA_GS_Boss_HitStun_C), or null. */
	inline UObject* FindAbilityByClassName(const AActor* Actor, FName ClassName)
	{
		UObject* Asc = FindComponentByClassName(Actor, TEXT("BP_AdvancedAbilitySystemComponent_C"));
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
			if (Ability && Ability->GetClass()->GetFName() == ClassName)
			{
				return Ability;
			}
		}
		return nullptr;
	}

	/** Calls the pack's "IsAbilityActive?" on an ability instance. */
	inline bool IsAbilityInstanceActive(UObject* Ability)
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

	/** Reads a current attribute value from the pack's attribute component. */
	inline bool ReadAttribute(const AActor* Actor, const TCHAR* AttributeTag, bool bMax, double& Value)
	{
		UObject* Attributes = FindCachedAttributesComponent(Actor);
		const FGameplayTag Tag = FGameplayTag::RequestGameplayTag(FName(AttributeTag), false);
		if (!Attributes || !Tag.IsValid())
		{
			return false;
		}
		Value = 0.0;
		return CallBlueprintFunction(Attributes, FindCachedAttributeFunction(Actor, bMax ? TEXT("GetMaxAttributeValue") : TEXT("Get Current Attribute Value")),
			[&](UFunction& F, uint8* P) { SetTag(F, P, TEXT("AttributeTag"), Tag); }, [&](UFunction& F, uint8* P) { Value = ReadNumber(F, P, TEXT("Value")); });
	}

	inline bool WriteAttribute(const AActor* Actor, const TCHAR* AttributeTag, double Value)
	{
		UObject* Attributes = FindCachedAttributesComponent(Actor);
		const FGameplayTag Tag = FGameplayTag::RequestGameplayTag(FName(AttributeTag), false);
		if (!Attributes || !Tag.IsValid())
		{
			return false;
		}
		return CallBlueprintFunction(Attributes, FindCachedAttributeFunction(Actor, TEXT("Set Current Attribute Value")),
			[&](UFunction& F, uint8* P)
			{
				SetTag(F, P, TEXT("AttributeTag"), Tag);
				if (const FNumericProperty* Number = CastField<FNumericProperty>(F.FindPropertyByName(TEXT("Value"))))
				{
					Number->SetFloatingPointPropertyValue(Number->ContainerPtrToValuePtr<void>(P), Value);
				}
			},
			[](UFunction&, uint8*) {});
	}

	/** Sets the MAXIMUM of an attribute (the pack's "Set Max Attribute Value"): the first numeric input parameter is the value. */
	inline bool WriteMaxAttribute(const AActor* Actor, const TCHAR* AttributeTag, double Value)
	{
		UObject* Attributes = FindCachedAttributesComponent(Actor);
		const FGameplayTag Tag = FGameplayTag::RequestGameplayTag(FName(AttributeTag), false);
		if (!Attributes || !Tag.IsValid())
		{
			return false;
		}
		return CallBlueprintFunction(Attributes, FindCachedAttributeFunction(Actor, TEXT("Set Max Attribute Value")),
			[&](UFunction& F, uint8* P)
			{
				SetTag(F, P, TEXT("AttributeTag"), Tag);
				for (TFieldIterator<FProperty> It(&F); It; ++It)
				{
					if (It->HasAnyPropertyFlags(CPF_Parm) && !It->HasAnyPropertyFlags(CPF_ReturnParm))
					{
						if (const FNumericProperty* Number = CastField<FNumericProperty>(*It))
						{
							Number->SetFloatingPointPropertyValue(Number->ContainerPtrToValuePtr<void>(P), Value);
							break;
						}
					}
				}
			},
			[](UFunction&, uint8*) {});
	}

	/** Activates the actor's abilities that carry the given gameplay tag (for example Ability.Melee). bForce passes the pack's bForceActivation. */
	inline bool TryActivateByTag(const AActor* Actor, const TCHAR* AbilityTag, bool bForce = false)
	{
		UObject* Asc = FindComponentByClassName(Actor, TEXT("BP_AdvancedAbilitySystemComponent_C"));
		const FGameplayTag Tag = FGameplayTag::RequestGameplayTag(FName(AbilityTag), false);
		if (!Asc || !Tag.IsValid())
		{
			return false;
		}
		bool bSuccess = false;
		CallBlueprintFunction(Asc, TEXT("Try Activate Abilities By Tag"),
			[&](UFunction& F, uint8* P)
			{
				if (const FStructProperty* Prop = CastField<FStructProperty>(F.FindPropertyByName(TEXT("AbilityTags"))))
				{
					*Prop->ContainerPtrToValuePtr<FGameplayTagContainer>(P) = FGameplayTagContainer(Tag);
				}
				if (bForce)
				{
					// The pack's input "bForceActivation" skips the activation checks (state, blocked tags); scripted tests use it to start a move on a frozen boss.
					if (const FBoolProperty* Force = CastField<FBoolProperty>(F.FindPropertyByName(TEXT("bForceActivation"))))
					{
						Force->SetPropertyValue_InContainer(P, true);
					}
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
}
