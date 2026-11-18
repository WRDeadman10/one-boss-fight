// Copyright One Boss Fight. All Rights Reserved.

#pragma once

#include "Player/RPGNativeBossHealth.h"
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

	inline FString GetPropertyTypeName(const FProperty* Prop)
	{
		if (!Prop)
		{
			return TEXT("<none>");
		}
		if (const FStructProperty* StructProp = CastField<FStructProperty>(Prop))
		{
			return StructProp->Struct ? StructProp->Struct->GetName() : TEXT("FStructProperty");
		}
		return Prop->GetCPPType(nullptr, 0);
	}

	inline bool SetTag(UFunction& Function, uint8* Params, const TCHAR* ParamName, const FGameplayTag& Tag, FString* OutParamName = nullptr, FString* OutParamType = nullptr)
	{
		const FProperty* Found = Function.FindPropertyByName(ParamName);
		if (Found)
		{
			if (const FStructProperty* StructProp = CastField<FStructProperty>(Found))
			{
				if (StructProp->HasAnyPropertyFlags(CPF_Parm) && !StructProp->HasAnyPropertyFlags(CPF_OutParm | CPF_ReturnParm) && StructProp->Struct == TBaseStructure<FGameplayTag>::Get())
				{
					if (OutParamName) { *OutParamName = StructProp->GetName(); }
					if (OutParamType) { *OutParamType = GetPropertyTypeName(StructProp); }
					*StructProp->ContainerPtrToValuePtr<FGameplayTag>(Params) = Tag;
					return true;
				}
			}
			if (OutParamName) { *OutParamName = Found->GetName(); }
			if (OutParamType) { *OutParamType = GetPropertyTypeName(Found); }
			return false;
		}

		// Fallback: search for input FGameplayTag parameters across the function; must find exactly one candidate
		const FStructProperty* SingleCandidate = nullptr;
		int32 CandidateCount = 0;
		for (TFieldIterator<FProperty> It(&Function); It; ++It)
		{
			if (It->HasAnyPropertyFlags(CPF_Parm) && !It->HasAnyPropertyFlags(CPF_OutParm | CPF_ReturnParm))
			{
				if (const FStructProperty* StructProp = CastField<FStructProperty>(*It))
				{
					if (StructProp->Struct == TBaseStructure<FGameplayTag>::Get())
					{
						SingleCandidate = StructProp;
						++CandidateCount;
					}
				}
			}
		}

		if (CandidateCount == 1 && SingleCandidate)
		{
			if (OutParamName) { *OutParamName = SingleCandidate->GetName(); }
			if (OutParamType) { *OutParamType = GetPropertyTypeName(SingleCandidate); }
			*SingleCandidate->ContainerPtrToValuePtr<FGameplayTag>(Params) = Tag;
			return true;
		}

		if (CandidateCount > 1)
		{
			if (OutParamName) { *OutParamName = TEXT("<ambiguous_multiple_gameplay_tag_params>"); }
			if (OutParamType) { *OutParamType = TEXT("FGameplayTag"); }
			return false;
		}

		if (OutParamName) { *OutParamName = TEXT("<none>"); }
		if (OutParamType) { *OutParamType = TEXT("<none>"); }
		return false;
	}

	inline double ReadNumber(UFunction& Function, uint8* Params, const TCHAR* ParamName)
	{
		if (const FNumericProperty* Prop = CastField<FNumericProperty>(Function.FindPropertyByName(ParamName)))
		{
			if (Prop->HasAnyPropertyFlags(CPF_Parm) && Prop->HasAnyPropertyFlags(CPF_OutParm | CPF_ReturnParm))
			{
				const void* Value = Prop->ContainerPtrToValuePtr<void>(Params);
				return Prop->IsFloatingPoint() ? Prop->GetFloatingPointPropertyValue(Value) : static_cast<double>(Prop->GetSignedIntPropertyValue(Value));
			}
		}
		if (const FNumericProperty* RetProp = CastField<FNumericProperty>(Function.GetReturnProperty()))
		{
			if (RetProp->HasAnyPropertyFlags(CPF_Parm) && RetProp->HasAnyPropertyFlags(CPF_OutParm | CPF_ReturnParm))
			{
				const void* Value = RetProp->ContainerPtrToValuePtr<void>(Params);
				return RetProp->IsFloatingPoint() ? RetProp->GetFloatingPointPropertyValue(Value) : static_cast<double>(RetProp->GetSignedIntPropertyValue(Value));
			}
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

	enum class EAttributeReadStatus : uint8
	{
		Valid,
		InvocationFailed,
		SchemaMismatch
	};

	struct FAttributeReadDiagnostic
	{
		EAttributeReadStatus Status = EAttributeReadStatus::InvocationFailed;
		double Value = 0.0;
		double MaxValue = 0.0;
		bool bMaxValueReadable = false;
		bool bInputTagBound = false;
		FString InputParamName;
		FString InputParamType;
		FString ComponentClass;
		FString FunctionName;
		FString OutputParamName;
		FString OutputParamType;
		uint64 OutputParamFlags = 0;
	};

	/** Reads an attribute value from the pack's attribute component with detailed reflection schema validation. */
	inline bool ReadAttributeDetailed(const AActor* Actor, const TCHAR* AttributeTag, bool bMax, FAttributeReadDiagnostic& OutDiagnostic)
	{
		OutDiagnostic = FAttributeReadDiagnostic();

		// A boss with native health (the framework Sevarog) answers for itself: every boss-health reader sees it through here.
		if (AttributeTag && FCString::Stricmp(AttributeTag, TEXT("Attribute.Health")) == 0)
		{
			if (const IRPGNativeBossHealth* Native = Cast<const IRPGNativeBossHealth>(Actor))
			{
				OutDiagnostic.ComponentClass = TEXT("IRPGNativeBossHealth");
				OutDiagnostic.FunctionName = TEXT("ReadNativeHealth");
				OutDiagnostic.OutputParamName = TEXT("NativeHealth");
				OutDiagnostic.OutputParamType = TEXT("double");
				OutDiagnostic.bInputTagBound = false;
				OutDiagnostic.InputParamName = TEXT("native_na");
				OutDiagnostic.InputParamType = TEXT("native_na");
				double NativeVal = 0.0;
				if (Native->ReadNativeHealth(bMax, NativeVal))
				{
					OutDiagnostic.Status = EAttributeReadStatus::Valid;
					OutDiagnostic.Value = NativeVal;
					double NativeMaxVal = 0.0;
					if (Native->ReadNativeHealth(true, NativeMaxVal))
					{
						OutDiagnostic.MaxValue = NativeMaxVal;
						OutDiagnostic.bMaxValueReadable = true;
					}
					return true;
				}
				OutDiagnostic.Status = EAttributeReadStatus::InvocationFailed;
				return false;
			}
		}

		UObject* Attributes = FindCachedAttributesComponent(Actor);
		const FGameplayTag Tag = FGameplayTag::RequestGameplayTag(FName(AttributeTag), false);
		if (!Attributes || !Tag.IsValid())
		{
			OutDiagnostic.Status = EAttributeReadStatus::InvocationFailed;
			if (Attributes)
			{
				OutDiagnostic.ComponentClass = Attributes->GetClass()->GetName();
			}
			return false;
		}

		OutDiagnostic.ComponentClass = Attributes->GetClass()->GetName();
		const TCHAR* DesiredFuncName = bMax ? TEXT("GetMaxAttributeValue") : TEXT("Get Current Attribute Value");
		UFunction* Function = FindCachedAttributeFunction(Actor, DesiredFuncName);
		if (!Function)
		{
			OutDiagnostic.Status = EAttributeReadStatus::InvocationFailed;
			return false;
		}
		OutDiagnostic.FunctionName = Function->GetName();

		// Inspect function properties for the numeric output parameter (must be marked CPF_OutParm or CPF_ReturnParm)
		auto IsNumericOutParam = [](const FProperty* Prop) -> const FNumericProperty*
		{
			if (Prop && Prop->HasAnyPropertyFlags(CPF_Parm) && Prop->HasAnyPropertyFlags(CPF_OutParm | CPF_ReturnParm))
			{
				return CastField<FNumericProperty>(Prop);
			}
			return nullptr;
		};

		const FProperty* CandidateProp = Function->FindPropertyByName(TEXT("Value"));
		const FNumericProperty* NumericProp = IsNumericOutParam(CandidateProp);

		if (!NumericProp)
		{
			const FProperty* RetProp = Function->GetReturnProperty();
			if (const FNumericProperty* RetNumeric = IsNumericOutParam(RetProp))
			{
				CandidateProp = RetProp;
				NumericProp = RetNumeric;
			}
		}

		if (!NumericProp)
		{
			OutDiagnostic.Status = EAttributeReadStatus::SchemaMismatch;
			if (!CandidateProp)
			{
				CandidateProp = Function->FindPropertyByName(TEXT("Value"));
			}
			if (!CandidateProp)
			{
				CandidateProp = Function->GetReturnProperty();
			}
			if (!CandidateProp)
			{
				for (TFieldIterator<FProperty> It(Function); It; ++It)
				{
					if (It->HasAnyPropertyFlags(CPF_Parm) && It->HasAnyPropertyFlags(CPF_OutParm | CPF_ReturnParm))
					{
						CandidateProp = *It;
						break;
					}
				}
			}
			if (CandidateProp)
			{
				OutDiagnostic.OutputParamName = CandidateProp->GetName();
				OutDiagnostic.OutputParamType = GetPropertyTypeName(CandidateProp);
				OutDiagnostic.OutputParamFlags = CandidateProp->GetPropertyFlags();
			}
			UE_LOG(LogRPGPack, Warning, TEXT("ReadAttribute schema mismatch on %s::%s: function has no numeric 'Value' out-parameter or return-parameter (observed property '%s', flags=0x%llx)"),
				*Attributes->GetClass()->GetName(), *Function->GetName(), CandidateProp ? *CandidateProp->GetName() : TEXT("<none>"),
				CandidateProp ? static_cast<unsigned long long>(CandidateProp->GetPropertyFlags()) : 0ULL);
			return false;
		}

		OutDiagnostic.OutputParamName = NumericProp->GetName();
		OutDiagnostic.OutputParamType = GetPropertyTypeName(NumericProp);
		OutDiagnostic.OutputParamFlags = NumericProp->GetPropertyFlags();

		bool bTagBound = false;
		double ExtractedValue = 0.0;
		const bool bCalled = CallBlueprintFunction(Attributes, Function,
			[&](UFunction& F, uint8* P)
			{
				bTagBound = SetTag(F, P, TEXT("AttributeTag"), Tag, &OutDiagnostic.InputParamName, &OutDiagnostic.InputParamType);
			},
			[&](UFunction& F, uint8* P)
			{
				const void* ContainerVal = NumericProp->ContainerPtrToValuePtr<void>(P);
				ExtractedValue = NumericProp->IsFloatingPoint()
					? NumericProp->GetFloatingPointPropertyValue(ContainerVal)
					: static_cast<double>(NumericProp->GetSignedIntPropertyValue(ContainerVal));
			});

		OutDiagnostic.bInputTagBound = bTagBound;
		if (!bTagBound)
		{
			OutDiagnostic.Status = EAttributeReadStatus::SchemaMismatch;
			UE_LOG(LogRPGPack, Warning, TEXT("ReadAttribute schema mismatch on %s::%s: could not bind input tag '%s' (observed input param '%s', type '%s')"),
				*Attributes->GetClass()->GetName(), *Function->GetName(), AttributeTag,
				*OutDiagnostic.InputParamName, *OutDiagnostic.InputParamType);
			return false;
		}

		if (!bCalled)
		{
			OutDiagnostic.Status = EAttributeReadStatus::InvocationFailed;
			return false;
		}

		OutDiagnostic.Status = EAttributeReadStatus::Valid;
		OutDiagnostic.Value = ExtractedValue;

		if (bMax)
		{
			OutDiagnostic.MaxValue = ExtractedValue;
			OutDiagnostic.bMaxValueReadable = true;
		}
		else
		{
			UFunction* MaxFunc = FindCachedAttributeFunction(Actor, TEXT("GetMaxAttributeValue"));
			if (MaxFunc)
			{
				const FProperty* MaxCandidate = MaxFunc->FindPropertyByName(TEXT("Value"));
				const FNumericProperty* MaxNumeric = IsNumericOutParam(MaxCandidate);
				if (!MaxNumeric)
				{
					MaxNumeric = IsNumericOutParam(MaxFunc->GetReturnProperty());
				}
				if (MaxNumeric)
				{
					double MaxExtracted = 0.0;
					bool bMaxTagBound = false;
					const bool bMaxCalled = CallBlueprintFunction(Attributes, MaxFunc,
						[&](UFunction& F, uint8* P)
						{
							bMaxTagBound = SetTag(F, P, TEXT("AttributeTag"), Tag);
						},
						[&](UFunction& F, uint8* P)
						{
							const void* ContainerVal = MaxNumeric->ContainerPtrToValuePtr<void>(P);
							MaxExtracted = MaxNumeric->IsFloatingPoint()
								? MaxNumeric->GetFloatingPointPropertyValue(ContainerVal)
								: static_cast<double>(MaxNumeric->GetSignedIntPropertyValue(ContainerVal));
						});
					if (bMaxCalled && bMaxTagBound && FMath::IsFinite(MaxExtracted))
					{
						OutDiagnostic.MaxValue = MaxExtracted;
						OutDiagnostic.bMaxValueReadable = true;
					}
				}
			}
		}

		return true;
	}

	/** Reads a current attribute value from the pack's attribute component. */
	inline bool ReadAttribute(const AActor* Actor, const TCHAR* AttributeTag, bool bMax, double& Value)
	{
		FAttributeReadDiagnostic Diag;
		const bool bOk = ReadAttributeDetailed(Actor, AttributeTag, bMax, Diag);
		if (bOk && Diag.Status == EAttributeReadStatus::Valid)
		{
			Value = Diag.Value;
			return true;
		}
		Value = 0.0;
		return false;
	}

	/** Safely inspects the player's current combat style asset marker without mutation. */
	inline FString GetPlayerCombatStyleDiagnostic(const AActor* PlayerPawn)
	{
		if (!PlayerPawn)
		{
			return TEXT("null_player");
		}
		const UObject* Combat = FindComponentByClassName(PlayerPawn, TEXT("BP_CombatComponent_C"));
		if (!Combat)
		{
			return TEXT("no_combat_comp");
		}
		const FProperty* Prop = Combat->GetClass()->FindPropertyByName(FName(TEXT("CurrentCombatStyle")));
		if (!Prop)
		{
			return TEXT("no_style_prop");
		}
		const FObjectProperty* ObjProp = CastField<FObjectProperty>(Prop);
		if (!ObjProp)
		{
			return TEXT("style_not_object");
		}
		const UObject* Style = ObjProp->GetObjectPropertyValue(ObjProp->ContainerPtrToValuePtr<void>(Combat));
		return Style ? Style->GetName() : TEXT("None");
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
