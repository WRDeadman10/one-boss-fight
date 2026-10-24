// Copyright One Boss Fight. All Rights Reserved.

#include "Player/RPGBossCloseClipSwap.h"
#include "Pack/RPGBlueprintCall.h"
#include "Player/RPGBossCloseClipSwapRules.h"
#include "Player/RPGBossDeath.h"
#include "Player/RPGBossEncounter.h"
#include "Animation/AnimMontage.h"
#include "UObject/UnrealType.h"
#include "Containers/Set.h"

DEFINE_LOG_CATEGORY_STATIC(LogRPGCloseClipSwap, Log, All);

using namespace RPGPack;

namespace
{
	const FObjectPropertyBase* FindMontageField(const FArrayProperty* Array)
	{
		const FStructProperty* Struct = Array ? CastField<FStructProperty>(Array->Inner) : nullptr;
		if (!Struct || !Struct->Struct)
		{
			return nullptr;
		}
		for (TFieldIterator<FProperty> It(Struct->Struct); It; ++It)
		{
			if (const FObjectPropertyBase* Candidate = CastField<FObjectPropertyBase>(*It))
			{
				if (Candidate->GetName().StartsWith(TEXT("AnimMontage")) && Candidate->PropertyClass && Candidate->PropertyClass->IsChildOf(UAnimMontage::StaticClass()))
				{
					return Candidate;
				}
			}
		}
		return nullptr;
	}
}

URPGBossCloseClipSwap::URPGBossCloseClipSwap()
{
	PrimaryComponentTick.bCanEverTick = true;
	PrimaryComponentTick.TickInterval = 0.25f;
	A1Montage = TSoftObjectPtr<UAnimMontage>(FSoftObjectPath(TEXT("/Game/OneBossFight/Boss01/Animations/AM_Boss01_A1.AM_Boss01_A1")));
	A3aMontage = TSoftObjectPtr<UAnimMontage>(FSoftObjectPath(TEXT("/Game/OneBossFight/Boss01/Animations/AM_Boss01_A3a.AM_Boss01_A3a")));
	A3bMontage = TSoftObjectPtr<UAnimMontage>(FSoftObjectPath(TEXT("/Game/OneBossFight/Boss01/Animations/AM_Boss01_A3b.AM_Boss01_A3b")));
}

void URPGBossCloseClipSwap::BeginPlay()
{
	Super::BeginPlay();
	Preload();
	if (URPGBossEncounter* Encounter = GetOwner()->FindComponentByClass<URPGBossEncounter>())
	{
		LastResetCount = Encounter->GetResetCount();
		AddTickPrerequisiteComponent(Encounter);
	}
}

void URPGBossCloseClipSwap::EndPlay(const EEndPlayReason::Type EndPlayReason)
{
	Restore(TEXT("EndPlay"));
	Super::EndPlay(EndPlayReason);
}

void URPGBossCloseClipSwap::Preload()
{
	LoadedA1 = A1Montage.LoadSynchronous();
	LoadedA3a = A3aMontage.LoadSynchronous();
	LoadedA3b = A3bMontage.LoadSynchronous();
	if (!LoadedA1 || !LoadedA3a || !LoadedA3b)
	{
		bPermanentFailure = true;
		LastResult = TEXT("an authored close montage did not load; pack fallback retained");
		UE_LOG(LogRPGCloseClipSwap, Warning, TEXT("%s: %s"), *GetOwner()->GetName(), *LastResult);
	}
}

UAnimMontage* URPGBossCloseClipSwap::ReplacementFor(FName PackMontageName) const
{
	if (PackMontageName == TEXT("GS_Attack03_Montage")) return LoadedA1.Get();
	if (PackMontageName == TEXT("GS_Attack01_Montage")) return LoadedA3a.Get();
	if (PackMontageName == TEXT("GS_Attack02_Montage")) return LoadedA3b.Get();
	return nullptr;
}

FString URPGBossCloseClipSwap::ApplyNowForTest()
{
#if UE_BUILD_SHIPPING
	return TEXT("unavailable in Shipping");
#else
	TryApply();
	return LastResult;
#endif
}

void URPGBossCloseClipSwap::SetEnabledForTest(bool bOn)
{
#if !UE_BUILD_SHIPPING
	bEnabledForTest = bOn;
	if (!bOn)
	{
		Restore(TEXT("test disabled"));
	}
#endif
}

void URPGBossCloseClipSwap::TickComponent(float DeltaTime, ELevelTick TickType, FActorComponentTickFunction* ThisTickFunction)
{
	Super::TickComponent(DeltaTime, TickType, ThisTickFunction);
	URPGBossEncounter* Encounter = GetOwner()->FindComponentByClass<URPGBossEncounter>();
	if (Encounter && LastResetCount != Encounter->GetResetCount())
	{
		Restore(TEXT("encounter reset"));
		LastResetCount = Encounter->GetResetCount();
	}
	if (!bEnabledForTest || bPermanentFailure || (Encounter && Encounter->IsDormant()))
	{
		return;
	}
	if (const URPGBossDeath* Death = GetOwner()->FindComponentByClass<URPGBossDeath>(); Death && Death->IsDeathActive())
	{
		Restore(TEXT("boss death"));
		return;
	}
	RetrySeconds += DeltaTime;
	if (!bApplied && RetrySeconds >= 0.5f)
	{
		RetrySeconds = 0.f;
		TryApply();
	}
}

bool URPGBossCloseClipSwap::TryApply()
{
	if (bPermanentFailure || bApplied)
	{
		return bApplied;
	}
	UObject* Ability = FindAbilityByClassName(GetOwner(), CloseAbilityClassName);
	if (!Ability)
	{
		LastResult = FString::Printf(TEXT("waiting for %s"), *CloseAbilityClassName.ToString());
		return false;
	}
	const FArrayProperty* Array = FindFProperty<FArrayProperty>(Ability->GetClass(), AttackMontagesName);
	const FObjectPropertyBase* MontageField = FindMontageField(Array);
	if (!Array || !MontageField)
	{
		bPermanentFailure = true;
		LastResult = FString::Printf(TEXT("%s has no validated %s F_AbilityMontage array; pack fallback retained"), *Ability->GetClass()->GetName(), *AttackMontagesName.ToString());
		UE_LOG(LogRPGCloseClipSwap, Warning, TEXT("%s: %s"), *GetOwner()->GetName(), *LastResult);
		return false;
	}
	FScriptArrayHelper Entries(Array, Array->ContainerPtrToValuePtr<void>(Ability));
	if (Entries.Num() != 4)
	{
		bPermanentFailure = true;
		LastResult = FString::Printf(TEXT("%s has %d %s entries, expected four; pack fallback retained"), *Ability->GetClass()->GetName(), Entries.Num(), *AttackMontagesName.ToString());
		UE_LOG(LogRPGCloseClipSwap, Warning, TEXT("%s: %s"), *GetOwner()->GetName(), *LastResult);
		return false;
	}

	TArray<FSwap> Candidates;
	TSet<FName> MappedPackMontages;
	for (int32 Index = 0; Index < Entries.Num(); ++Index)
	{
		uint8* Element = Entries.GetRawPtr(Index);
		UAnimMontage* Current = Cast<UAnimMontage>(MontageField->GetObjectPropertyValue(MontageField->ContainerPtrToValuePtr<void>(Element)));
		if (!Current || !RPGBossCloseClipSwapRules::IsPackCloseMontage(Current->GetFName()))
		{
			bPermanentFailure = true;
			LastResult = FString::Printf(TEXT("%s[%d] is %s, not a validated pack close montage; pack fallback retained"), *AttackMontagesName.ToString(), Index, *GetNameSafe(Current));
			UE_LOG(LogRPGCloseClipSwap, Warning, TEXT("%s: %s"), *GetOwner()->GetName(), *LastResult);
			return false;
		}
		const FName ReplacementName = RPGBossCloseClipSwapRules::ReplacementFor(Current->GetFName());
		if (!ReplacementName.IsNone())
		{
			UAnimMontage* Replacement = ReplacementFor(Current->GetFName());
			if (!Replacement || MappedPackMontages.Contains(Current->GetFName()))
			{
				bPermanentFailure = true;
				LastResult = FString::Printf(TEXT("%s has an invalid or duplicate authored close mapping; pack fallback retained"), *AttackMontagesName.ToString());
				UE_LOG(LogRPGCloseClipSwap, Warning, TEXT("%s: %s"), *GetOwner()->GetName(), *LastResult);
				return false;
			}
			FSwap& Swap = Candidates.AddDefaulted_GetRef();
			Swap.Index = Index;
			Swap.Original = Current;
			MappedPackMontages.Add(Current->GetFName());
			UE_LOG(LogRPGCloseClipSwap, Log, TEXT("%s: %s[%d] %s -> %s"), *GetOwner()->GetName(), *AttackMontagesName.ToString(), Index, *Current->GetName(), *Replacement->GetName());
		}
	}
	if (Candidates.Num() != 3
		|| !MappedPackMontages.Contains(TEXT("GS_Attack03_Montage"))
		|| !MappedPackMontages.Contains(TEXT("GS_Attack01_Montage"))
		|| !MappedPackMontages.Contains(TEXT("GS_Attack02_Montage")))
	{
		bPermanentFailure = true;
		LastResult = FString::Printf(TEXT("only %d authored close replacements mapped; pack fallback retained"), Candidates.Num());
		UE_LOG(LogRPGCloseClipSwap, Warning, TEXT("%s: %s"), *GetOwner()->GetName(), *LastResult);
		return false;
	}
	for (const FSwap& Swap : Candidates)
	{
		uint8* Element = Entries.GetRawPtr(Swap.Index);
		MontageField->SetObjectPropertyValue(MontageField->ContainerPtrToValuePtr<void>(Element), ReplacementFor(Swap.Original->GetFName()));
	}
	SwappedAbility = Ability;
	Swaps = MoveTemp(Candidates);
	bApplied = true;
	++ApplyCount;
	LastResult = TEXT("applied A1/A3a/A3b; A1b remains pack");
	return true;
}

void URPGBossCloseClipSwap::Restore(const TCHAR* Why)
{
	if (!bApplied)
	{
		return;
	}
	UObject* Ability = SwappedAbility.Get();
	const FArrayProperty* Array = Ability ? FindFProperty<FArrayProperty>(Ability->GetClass(), AttackMontagesName) : nullptr;
	const FObjectPropertyBase* MontageField = FindMontageField(Array);
	if (Ability && Array && MontageField)
	{
		FScriptArrayHelper Entries(Array, Array->ContainerPtrToValuePtr<void>(Ability));
		for (const FSwap& Swap : Swaps)
		{
			if (Entries.IsValidIndex(Swap.Index) && Swap.Original.IsValid())
			{
				MontageField->SetObjectPropertyValue(MontageField->ContainerPtrToValuePtr<void>(Entries.GetRawPtr(Swap.Index)), Swap.Original.Get());
			}
		}
		++RestoreCount;
		LastResult = FString::Printf(TEXT("restored pack close montages (%s)"), Why);
	}
	else
	{
		LastResult = FString::Printf(TEXT("could not restore old live ability (%s)"), Why);
	}
	Swaps.Reset();
	SwappedAbility.Reset();
	bApplied = false;
}
