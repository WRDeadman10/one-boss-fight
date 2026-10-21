// Copyright One Boss Fight. All Rights Reserved.

#include "Player/RPGBossPosture.h"
#include "Pack/RPGBlueprintCall.h"
#include "Engine/World.h"
#include "UObject/UnrealType.h"

DEFINE_LOG_CATEGORY_STATIC(LogRPGPosture, Log, All);

using namespace RPGPack;

namespace
{
	constexpr const TCHAR* PoiseTag = TEXT("Attribute.Poise");

	void SetDouble(UObject* Object, const TCHAR* Name, double Value)
	{
		if (const FNumericProperty* Property = CastField<FNumericProperty>(Object->GetClass()->FindPropertyByName(Name)))
		{
			Property->SetFloatingPointPropertyValue(Property->ContainerPtrToValuePtr<void>(Object), Value);
		}
	}

	double GetDouble(UObject* Object, const TCHAR* Name, double Fallback)
	{
		if (const FNumericProperty* Property = CastField<FNumericProperty>(Object->GetClass()->FindPropertyByName(Name)))
		{
			return Property->GetFloatingPointPropertyValue(Property->ContainerPtrToValuePtr<void>(Object));
		}
		return Fallback;
	}
}

URPGBossPosture::URPGBossPosture()
{
	PrimaryComponentTick.bCanEverTick = true;
	PrimaryComponentTick.TickInterval = 0.05f;
}

bool URPGBossPosture::ConfigureAttribute()
{
	UObject* Attributes = FindComponentByClassName(GetOwner(), TEXT("BP_AttributesComponent_C"));
	const FArrayProperty* Instances = Attributes ? FindFProperty<FArrayProperty>(Attributes->GetClass(), TEXT("ExtendedAttributeInstances")) : nullptr;
	const FObjectProperty* Inner = Instances ? CastField<FObjectProperty>(Instances->Inner) : nullptr;
	if (!Inner)
	{
		return false;
	}
	FScriptArrayHelper Array(Instances, Instances->ContainerPtrToValuePtr<void>(Attributes));
	for (int32 Index = 0; Index < Array.Num(); ++Index)
	{
		UObject* Object = Inner->GetObjectPropertyValue(Array.GetRawPtr(Index));
		if (Object && Object->GetClass()->GetName() == TEXT("BP_PoiseExtendedAttribute_C"))
		{
			// The pack's own regeneration (delay 4 s, 20 per second) is switched off for this attribute: this component regenerates it by the Freeze rule instead, one owner for the value.
			SetDouble(Object, TEXT("StatRegenCoolDown"), 1.0e9);
			SetDouble(Object, TEXT("InitialRegenRate"), 0.0);
			SetDouble(Object, TEXT("CurrentRegenRate"), 0.0);
			UE_LOG(LogRPGPosture, Log, TEXT("%s: pack poise regeneration disabled, posture regenerates here: %.1f s delay, %.1f per second"), *GetOwner()->GetName(), RegenDelaySeconds, RegenPerSecond);
			return true;
		}
	}
	return false;
}

void URPGBossPosture::BeginHold(EHold Mode)
{
	if (Hold != EHold::None || Mode == EHold::None)
	{
		return;
	}
	Hold = Mode;
	double Now = 0.0;
	if (Mode == EHold::Zero)
	{
		HeldValue = 0.f;
		WriteAttribute(GetOwner(), PoiseTag, 0.0);
	}
	else
	{
		HeldValue = ReadAttribute(GetOwner(), PoiseTag, false, Now) ? static_cast<float>(Now) : FMath::Max(Posture, 0.f);
	}
	Posture = HeldValue;
	UE_LOG(LogRPGPosture, Log, TEXT("%s: posture hold %s at %.1f"), *GetOwner()->GetName(), *GetHoldName(), HeldValue);
}

void URPGBossPosture::EndHold(bool bRefill)
{
	if (Hold == EHold::None)
	{
		return;
	}
	Hold = EHold::None;
	if (bRefill)
	{
		double Max = 0.0;
		if (ReadAttribute(GetOwner(), PoiseTag, true, Max))
		{
			WriteAttribute(GetOwner(), PoiseTag, Max);
			Posture = static_cast<float>(Max);
		}
	}
	else
	{
		Posture = HeldValue;
	}
	// Regeneration waits the normal delay from here (no drain is counted for the write above).
	LastDrainTime = GetWorld() ? GetWorld()->GetTimeSeconds() : 0.0;
	UE_LOG(LogRPGPosture, Log, TEXT("%s: posture hold ended (refill %d), posture %.1f, %d hits ignored so far"), *GetOwner()->GetName(), bRefill ? 1 : 0, Posture, SuppressedDrains);
}

FString URPGBossPosture::GetHoldName() const
{
	switch (Hold)
	{
	case EHold::Zero: return TEXT("Zero");
	case EHold::Pinned: return TEXT("Pinned");
	default: return TEXT("None");
	}
}

void URPGBossPosture::TickComponent(float DeltaTime, ELevelTick TickType, FActorComponentTickFunction* ThisTickFunction)
{
	Super::TickComponent(DeltaTime, TickType, ThisTickFunction);
	if (!bConfigured)
	{
		bConfigured = ConfigureAttribute(); // the pack creates its extended attributes a moment after BeginPlay
	}
	double Now = 0.0, Max = 0.0;
	if (!ReadAttribute(GetOwner(), PoiseTag, false, Now) || !ReadAttribute(GetOwner(), PoiseTag, true, Max))
	{
		return;
	}
	MaxPosture = static_cast<float>(Max);
	if (Hold != EHold::None)
	{
		// Held: whatever the pack wrote (a hit's drain, or its gate refilling the pool at zero) is put back. No drain counting, no regeneration.
		if (FMath::Abs(Now - HeldValue) > 0.01)
		{
			WriteAttribute(GetOwner(), PoiseTag, HeldValue);
			++SuppressedDrains;
		}
		Posture = HeldValue;
		return;
	}
	if (Posture >= 0.f && Now < Posture - 0.01)
	{
		++DrainCount;
		LastDrainTime = GetWorld() ? GetWorld()->GetTimeSeconds() : 0.0;
	}
	Posture = static_cast<float>(Now);

	// Regeneration (Freeze 17.2): starts RegenDelaySeconds after the last drain, adds RegenPerSecond, never above the maximum.
	const double WorldTime = GetWorld() ? GetWorld()->GetTimeSeconds() : 0.0;
	if (bConfigured && Posture < MaxPosture && Posture > 0.f && (LastDrainTime < 0.0 || WorldTime - LastDrainTime >= RegenDelaySeconds))
	{
		const float Next = FMath::Min(MaxPosture, Posture + RegenPerSecond * DeltaTime);
		WriteAttribute(GetOwner(), PoiseTag, Next);
		Posture = Next;
	}
}
