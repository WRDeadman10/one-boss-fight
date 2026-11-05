// Copyright One Boss Fight. All Rights Reserved.

#include "Player/RPGPlayerParry.h"
#include "EnhancedInputComponent.h"
#include "GameFramework/Pawn.h"
#include "Engine/World.h"
#include "GameplayTagContainer.h"
#include "Pack/RPGBlueprintCall.h"
#include "Player/RPGParryCostRules.h"

DEFINE_LOG_CATEGORY_STATIC(LogRPGParry, Log, All);

#if !UE_BUILD_SHIPPING
static TAutoConsoleVariable<float> CVarParryStaminaCost(TEXT("rpg.ParryStaminaCost"), 0.f, TEXT("Test hook (parry stamina proof): when above 0 and the component's StaminaCost is 0, the component adopts this cost at the next press."));
#endif

URPGPlayerParry::URPGPlayerParry()
{
	PrimaryComponentTick.bCanEverTick = true;
	PrimaryComponentTick.bStartWithTickEnabled = true;
	ParryAction = TSoftObjectPtr<UInputAction>(FSoftObjectPath(TEXT("/Game/AdvancedARPGCombat/MeleeCombatSystem/Blueprints/Input/InputActions/IA_Parry.IA_Parry")));
}

void URPGPlayerParry::BeginPlay()
{
	Super::BeginPlay();
	TryBind();
}

void URPGPlayerParry::TickComponent(float DeltaTime, ELevelTick TickType, FActorComponentTickFunction* ThisTickFunction)
{
	Super::TickComponent(DeltaTime, TickType, ThisTickFunction);
	if (!bBound)
	{
		TryBind(); // the pawn's input component exists a little after BeginPlay
	}
	if (bTagOn && !IsWindowOpen())
	{
		SetParryTag(false, TEXT("WindowClosed"));
	}
	if (bCostPending && !IsWindowOpen()) FinishStaminaCost();
}

double URPGPlayerParry::Now() const
{
	return GetWorld() ? GetWorld()->GetTimeSeconds() : 0.0;
}

bool URPGPlayerParry::TryBind()
{
	const APawn* Pawn = Cast<APawn>(GetOwner());
	UEnhancedInputComponent* Input = Pawn ? Cast<UEnhancedInputComponent>(Pawn->InputComponent) : nullptr;
	UInputAction* Action = ParryAction.LoadSynchronous();
	if (!Input || !Action)
	{
		return false;
	}
	Input->BindAction(Action, ETriggerEvent::Started, this, &URPGPlayerParry::OnParryPressed);
	bBound = true;
	UE_LOG(LogRPGParry, Log, TEXT("%s: parry window bound to %s (window %.2f s, cooldown %.2f s)"), *GetOwner()->GetName(), *Action->GetName(), WindowSeconds, CooldownSeconds);
	return true;
}

void URPGPlayerParry::OnParryPressed()
{
	Press();
}

bool URPGPlayerParry::Press()
{
	if (bCostPending) return false; // do not let a second attempt overwrite a pending refund/rollback
#if !UE_BUILD_SHIPPING
	if (StaminaCost <= 0.f && CVarParryStaminaCost.GetValueOnGameThread() > 0.f)
	{
		StaminaCost = CVarParryStaminaCost.GetValueOnGameThread();
	}
#endif
	if (!FMath::IsFinite(StaminaCost) || StaminaCost < 0.f) return false;
	++PressCount;
	double Before = 0.;
	const bool bCharge = StaminaCost > 0.f;
	if (bCharge)
	{
		if (!RPGPack::ReadAttribute(GetOwner(), TEXT("Attribute.Stamina"), false, Before) || !RPGParryCost::CanPress(Before, StaminaCost))
		{
			UE_LOG(LogRPGParry, Display, TEXT("[FrameworkProof] parry_stamina before=%g after=%g parried=0"), Before, Before);
			return false;
		}
		if (!RPGPack::WriteAttribute(GetOwner(), TEXT("Attribute.Stamina"), RPGParryCost::StaminaAfter(Before, StaminaCost, false)))
		{
			UE_LOG(LogRPGParry, Display, TEXT("[FrameworkProof] parry_stamina before=%g after=%g parried=0"), Before, Before);
			return false;
		}
	}
	const bool bOpened = RPGParry::Press(State, Now(), WindowSeconds, CooldownSeconds);
	if (bOpened)
	{
		if (bCharge) { bCostPending = true; bPendingParried = false; StaminaBeforeCost = Before; PaidStaminaCost = StaminaCost; }
		SetParryTag(true, TEXT("Press"));
	}
	else if (bCharge)
	{
		bCostPending = true; bPendingParried = false; bRollbackPending = true;
		StaminaBeforeCost = Before; PaidStaminaCost = StaminaCost; RefundRetries = 0;
		FinishStaminaCost();
	}
	UE_LOG(LogRPGParry, Display, TEXT("[FrameworkProof] parry_press n=%d t=%.4f opened=%d windowSeconds=%g"), PressCount, Now(), bOpened ? 1 : 0, WindowSeconds);
	return bOpened;
}

bool URPGPlayerParry::IsWindowOpen() const
{
	return RPGParry::IsOpen(State, Now(), WindowSeconds);
}

RPGParryGrade::EGrade URPGPlayerParry::GradeNow() const
{
	return RPGParryGrade::Grade(Now() - State.OpenedAt, WindowSeconds);
}

FString URPGPlayerParry::LastGradeName() const
{
	switch (LastGrade)
	{
	case RPGParryGrade::EGrade::Perfect: return TEXT("Perfect");
	case RPGParryGrade::EGrade::Good: return TEXT("Good");
	case RPGParryGrade::EGrade::Late: return TEXT("Late");
	default: return TEXT("None");
	}
}

bool URPGPlayerParry::IsParrying(const AActor* Actor)
{
	const URPGPlayerParry* Parry = Actor ? Actor->FindComponentByClass<URPGPlayerParry>() : nullptr;
	return Parry && Parry->IsWindowOpen();
}

void URPGPlayerParry::NotifyParried(AActor* Actor)
{
	if (URPGPlayerParry* Parry = Actor ? Actor->FindComponentByClass<URPGPlayerParry>() : nullptr)
	{
		Parry->LastGrade = Parry->GradeNow();
		if (Parry->bCostPending) Parry->bPendingParried = true;
	}
}

void URPGPlayerParry::FinishStaminaCost()
{
	if (!bCostPending) return;
	double After = 0.;
	if (bRollbackPending)
	{
		if (!RPGPack::WriteAttribute(GetOwner(), TEXT("Attribute.Stamina"), StaminaBeforeCost) && ++RefundRetries < 5)
		{
			return; // keep bCostPending: the next tick (or EndPlay retry) restores the rejected press cost
		}
	}
	else if (bPendingParried)
	{
		if (!RPGPack::ReadAttribute(GetOwner(), TEXT("Attribute.Stamina"), false, After))
		{
			if (++RefundRetries < 5) return; // a transiently unavailable attribute must not discard the parry refund immediately
		}
		else
		{
			double Max = 0.;
			if (RPGPack::ReadAttribute(GetOwner(), TEXT("Attribute.Stamina"), true, Max) && FMath::IsFinite(Max)) After = RPGParryCost::ParryRefund(After, Max, PaidStaminaCost);
			else After += PaidStaminaCost * .5;
			if (!RPGPack::WriteAttribute(GetOwner(), TEXT("Attribute.Stamina"), After) && ++RefundRetries < 5) return;
		}
	}
	RefundRetries = 0;
	if (RPGPack::ReadAttribute(GetOwner(), TEXT("Attribute.Stamina"), false, After))
	{
		UE_LOG(LogRPGParry, Display, TEXT("[FrameworkProof] parry_stamina before=%g after=%g parried=%d"), StaminaBeforeCost, After, bPendingParried ? 1 : 0);
	}
	bCostPending = false;
	bPendingParried = false;
	bRollbackPending = false;
}

void URPGPlayerParry::EndPlay(const EEndPlayReason::Type EndPlayReason)
{
	for (int32 Attempt = 0; bCostPending && Attempt < 5; ++Attempt) FinishStaminaCost();
	for (int32 Attempt = 0; bTagOn && Attempt < 5; ++Attempt) SetParryTag(false, TEXT("EndPlay"));
	Super::EndPlay(EndPlayReason);
}

void URPGPlayerParry::SetParryTag(bool bOn, const TCHAR* Reason)
{
	const FGameplayTag Tag = FGameplayTag::RequestGameplayTag(TEXT("Status.ParryActive"), false);
	if (!Tag.IsValid())
	{
		return;
	}
	const TCHAR* Function = bOn ? TEXT("AddOwnedGameplayTag") : TEXT("RemoveOwnedGameplayTag");
	const TCHAR* Param = bOn ? TEXT("TagToAdd") : TEXT("TagToRemove");
	const bool bCalled = RPGPack::CallBlueprintFunction(GetOwner(), Function, [&Tag, Param](UFunction& F, uint8* P) { RPGPack::SetTag(F, P, Param, Tag); }, [](UFunction&, uint8*) {});
	bTagOn = bOn ? bCalled : !bCalled; // audit X-441 #15: a failed removal keeps ownership so a later tick or EndPlay retries
	UE_LOG(LogRPGParry, Display, TEXT("[FrameworkProof] parry_tag state=%s call=%s reason=%s"), bOn ? TEXT("added") : TEXT("removed"), bCalled ? TEXT("ok") : TEXT("failed"), Reason);
}
