// Copyright One Boss Fight. All Rights Reserved.

#pragma once

#include "CoreMinimal.h"
#include "UObject/UnrealType.h"

/**
 * Reads variables of the pack's Blueprint objects by their exact names (the pack's names carry spaces and question marks: "bCollisionEnabled?", "Attack Data"). Every function returns the fallback when the object or the
 * variable is missing or has another type, so a pack update that renames something degrades the feature instead of crashing it (the PackWiring test guards the names that matter).
 */
namespace RPGPackReflect
{
	inline const FProperty* Find(const UObject* Object, const TCHAR* Name)
	{
		return Object ? Object->GetClass()->FindPropertyByName(FName(Name)) : nullptr;
	}

	inline UObject* ReadObject(const UObject* Object, const TCHAR* Name)
	{
		const FObjectProperty* Property = CastField<FObjectProperty>(Find(Object, Name));
		return Property ? Property->GetObjectPropertyValue(Property->ContainerPtrToValuePtr<void>(Object)) : nullptr;
	}

	inline bool ReadBool(const UObject* Object, const TCHAR* Name, bool bFallback = false)
	{
		const FBoolProperty* Property = CastField<FBoolProperty>(Find(Object, Name));
		return Property ? Property->GetPropertyValue_InContainer(Object) : bFallback;
	}

	inline int32 ReadByte(const UObject* Object, const TCHAR* Name, int32 Fallback = -1)
	{
		const FProperty* Property = Find(Object, Name);
		if (const FByteProperty* Byte = CastField<FByteProperty>(Property))
		{
			return Byte->GetPropertyValue_InContainer(Object);
		}
		if (const FEnumProperty* Enum = CastField<FEnumProperty>(Property))
		{
			return static_cast<int32>(Enum->GetUnderlyingProperty()->GetSignedIntPropertyValue(Enum->ContainerPtrToValuePtr<void>(Object)));
		}
		return Fallback;
	}

	inline float ReadFloat(const UObject* Object, const TCHAR* Name, float Fallback = -1.f)
	{
		const FNumericProperty* Property = CastField<FNumericProperty>(Find(Object, Name));
		return Property ? static_cast<float>(Property->GetFloatingPointPropertyValue(Property->ContainerPtrToValuePtr<void>(Object))) : Fallback;
	}

	/** True when the array variable has an element whose exported text names the asset (an array of structs holding a montage reference prints its asset path). */
	inline bool ArrayMentions(const UObject* Object, const TCHAR* ArrayName, const FString& AssetName)
	{
		const FArrayProperty* Array = CastField<FArrayProperty>(Find(Object, ArrayName));
		if (!Array)
		{
			return false;
		}
		const FString Needle = AssetName + TEXT(".") + AssetName;
		FScriptArrayHelper Helper(Array, Array->ContainerPtrToValuePtr<void>(Object));
		for (int32 Index = 0; Index < Helper.Num(); ++Index)
		{
			FString Text;
			Array->Inner->ExportTextItem_Direct(Text, Helper.GetRawPtr(Index), nullptr, nullptr, PPF_None);
			if (Text.Contains(Needle))
			{
				return true;
			}
		}
		return false;
	}
}
