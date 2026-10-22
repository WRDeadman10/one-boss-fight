// Copyright One Boss Fight. All Rights Reserved.

#include "Player/RPGBossPosture.h"
#include "Pack/RPGBlueprintCall.h"
#include "Player/RPGBossEncounter.h"
#include "Player/RPGBossMath.h"
#include "Player/RPGBossRules.h"
#include "Player/RPGBossStagger.h"
#include "Engine/World.h"
#include "UObject/UnrealType.h"

DEFINE_LOG_CATEGORY_STATIC(LogRPGPosture, Log, All);

using namespace RPGPack;

namespace
{
	constexpr const TCHAR* PoiseTag = TEXT("Attribute.Poise");
	constexpr const TCHAR* HealthTag = TEXT("Attribute.Health");

	void SetDouble(UObject* Object, const TCHAR* Name, double Value)
	{
		if (const FNumericProperty* Property = CastField<FNumericProperty>(Object->GetClass()->FindPropertyByName(Name)))
		{
			Property->SetFloatingPointPropertyValue(Property->ContainerPtrToValuePtr<void>(Object), Value);
		}
	}
}

URPGBossPosture::URPGBossPosture()
{
	PrimaryComponentTick.bCanEverTick = true;
	PrimaryComponentTick.TickInterval = 0.05f;
}

void URPGBossPosture::BeginPlay()
{
	Super::BeginPlay();
	Posture = PostureMax;
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
			// The pack's own regeneration of its poise (delay 4 s, 20 per second) is switched off: the attribute is pinned full here, the posture pool is ours.
			SetDouble(Object, TEXT("StatRegenCoolDown"), 1.0e9);
			SetDouble(Object, TEXT("InitialRegenRate"), 0.0);
			SetDouble(Object, TEXT("CurrentRegenRate"), 0.0);
			UE_LOG(LogRPGPosture, Log, TEXT("%s: posture pool of %.0f points is the component's own: %.1f s regeneration delay, %.1f per second; the pack's poise is pinned full (%d)"), *GetOwner()->GetName(), PostureMax, RegenDelaySeconds, RegenPerSecond, bPinPackPoise ? 1 : 0);
			return true;
		}
	}
	return false;
}

bool URPGBossPosture::IsDeadOrDormant() const
{
	double Health = 1.0;
	if (ReadAttribute(GetOwner(), HealthTag, false, Health) && Health <= 0.0)
	{
		return true;
	}
	const URPGBossEncounter* Encounter = GetOwner()->FindComponentByClass<URPGBossEncounter>();
	return Encounter && Encounter->IsDormant();
}

void URPGBossPosture::PinPackPoise()
{
	double Now = 0.0, Max = 0.0;
	if (ReadAttribute(GetOwner(), PoiseTag, false, Now) && ReadAttribute(GetOwner(), PoiseTag, true, Max) && Now < Max - 0.01)
	{
		WriteAttribute(GetOwner(), PoiseTag, Max);
	}
}

URPGBossPosture::EDrainResult URPGBossPosture::ApplyPostureDamage(float Amount, const TCHAR* Source)
{
	if (Amount <= 0.f || Posture < 0.f || IsDeadOrDormant())
	{
		return EDrainResult::Ignored;
	}
	if (Hold != EHold::None)
	{
		++SuppressedDrains;
		UE_LOG(LogRPGPosture, Log, TEXT("%s: posture damage %.1f (%s) ignored during the %s hold"), *GetOwner()->GetName(), Amount, Source, *GetHoldName());
		return EDrainResult::Held;
	}
	const float Before = Posture;
	Posture = FMath::Max(0.f, Posture - Amount);
	++DrainCount;
	LastDrainAmount = Amount;
	LastDrainSource = Source;
	LastDrainTime = GetWorld() ? GetWorld()->GetTimeSeconds() : 0.0;
	UE_LOG(LogRPGPosture, Log, TEXT("%s: posture %.1f -> %.1f (-%.1f, %s)"), *GetOwner()->GetName(), Before, Posture, Amount, Source);
	if (Posture <= 0.f)
	{
		// The pool reached zero: one request for the stance break through the same gate as every other source (dead, dormant, transition, already down, cooldown).
		++BreakRequests;
		if (URPGBossStagger* Stagger = GetOwner()->FindComponentByClass<URPGBossStagger>())
		{
			LastBreakResult = RPGBossRules::Name(Stagger->RequestBreak(false));
		}
		else
		{
			LastBreakResult = TEXT("no stagger component");
		}
	}
	return EDrainResult::Applied;
}

void URPGBossPosture::SetPostureForTest(float Value)
{
	const float Clamped = FMath::Clamp(Value, 0.f, PostureMax);
	if (Hold != EHold::None)
	{
		HeldValue = Clamped;
	}
	if (Clamped < Posture)
	{
		++DrainCount;
		LastDrainTime = GetWorld() ? GetWorld()->GetTimeSeconds() : 0.0;
	}
	Posture = Clamped;
}

void URPGBossPosture::ResetPool()
{
	Hold = EHold::None;
	HeldValue = 0.f;
	Posture = PostureMax;
	LastDrainTime = -1.0;
}

void URPGBossPosture::RefillAfterBreak()
{
	if (Hold != EHold::None)
	{
		EndHold(true);
		return;
	}
	Posture = PostureMax;
	LastDrainTime = GetWorld() ? GetWorld()->GetTimeSeconds() : 0.0;
	UE_LOG(LogRPGPosture, Log, TEXT("%s: posture refilled to %.1f after the stance break (no hold was running)"), *GetOwner()->GetName(), Posture);
}

void URPGBossPosture::NotePackStunSuppressed()
{
	++PackStunSuppressed;
	UE_LOG(LogRPGPosture, Warning, TEXT("%s: the pack's hit stun started although its poise is pinned (two heavy hits inside one pin interval): ended, not a stance break (the pool of %.1f decides), %d so far"), *GetOwner()->GetName(), Posture, PackStunSuppressed);
	if (bConfigured)
	{
		PinPackPoise();
	}
}

void URPGBossPosture::BeginHold(EHold Mode)
{
	if (Hold != EHold::None || Mode == EHold::None)
	{
		return;
	}
	Hold = Mode;
	HeldValue = Mode == EHold::Zero ? 0.f : FMath::Max(Posture, 0.f);
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
	Posture = bRefill ? PostureMax : HeldValue;
	// Regeneration waits the normal delay from here.
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
	if (bPinPackPoise && bConfigured)
	{
		PinPackPoise();
	}
	if (Posture < 0.f)
	{
		Posture = PostureMax;
	}
	if (Hold != EHold::None)
	{
		Posture = HeldValue; // held: no regeneration
		return;
	}
	// Regeneration (Freeze 17.2): starts RegenDelaySeconds after the last drain, adds RegenPerSecond, never above the maximum. A stance break holds the pool at zero (the early return above), so a pool at zero
	// that reaches this line is one whose break request was dropped (a cooldown, the hold switched off): it comes back too instead of staying empty.
	const double WorldTime = GetWorld() ? GetWorld()->GetTimeSeconds() : 0.0;
	Posture = RPGBossMath::RegenStep(Posture, PostureMax, WorldTime, LastDrainTime, RegenDelaySeconds, RegenPerSecond, DeltaTime, true);
}
