// Copyright One Boss Fight. All Rights Reserved.

#include "Player/RPGBossBleed.h"
#include "Pack/RPGBlueprintCall.h"
#include "Player/RPGBossEncounter.h"
#include "Player/RPGBossPhases.h"
#include "Player/RPGBossStagger.h"
#include "Player/RPGFlipbookEffect.h"
#include "NiagaraFunctionLibrary.h"
#include "NiagaraSystem.h"
#include "Engine/World.h"
#include "Kismet/GameplayStatics.h"
#include "Sound/SoundBase.h"

DEFINE_LOG_CATEGORY_STATIC(LogRPGBleed, Log, All);

using namespace RPGPack;

namespace
{
	constexpr const TCHAR* HealthTag = TEXT("Attribute.Health");
}

URPGBossBleed::URPGBossBleed()
{
	PrimaryComponentTick.bCanEverTick = false;
	ProcEffect = TSoftObjectPtr<UNiagaraSystem>(FSoftObjectPath(TEXT("/Game/BloodPack/Hit/Niagara/NS_BulletHit_Med.NS_BulletHit_Med")));
	ProcSound = TSoftObjectPtr<USoundBase>(FSoftObjectPath(TEXT("/Game/AdvancedARPGCombat/MeleeCombatSystem/DemoAssets/SoundFX/A_Guardian_ImpactL_Cue.A_Guardian_ImpactL_Cue")));
}

void URPGBossBleed::BeginPlay()
{
	Super::BeginPlay();
	State.Threshold = InitialThreshold;
	LoadedEffect = ProcEffect.LoadSynchronous();
	LoadedSound = ProcSound.LoadSynchronous();
	LoadedBloodFlipbook = ARPGFlipbookEffect::LoadMaterial(ERPGEFlipbookKind::BloodBurst);
	if (!LoadedEffect || !LoadedSound)
	{
		UE_LOG(LogRPGBleed, Warning, TEXT("%s: the bleed proc effect (%d) or sound (%d) did not load: a proc will be silent"), *GetOwner()->GetName(), LoadedEffect ? 1 : 0, LoadedSound ? 1 : 0);
	}
}

RPGBleedRules::FConfig URPGBossBleed::MakeConfig() const
{
	RPGBleedRules::FConfig Config;
	Config.InitialThreshold = InitialThreshold;
	Config.ThresholdIncrease = ThresholdIncrease;
	Config.ThresholdMax = ThresholdMax;
	Config.HpFraction = HpFraction;
	return Config;
}

RPGBleedRules::EResult URPGBossBleed::AddBuildup(float Amount, const TCHAR* Source)
{
	using namespace RPGBleedRules;
	double Health = 1.0;
	const bool bDead = ReadAttribute(GetOwner(), HealthTag, false, Health) && Health <= 0.0;
	const URPGBossEncounter* Encounter = GetOwner()->FindComponentByClass<URPGBossEncounter>();
	const URPGBossPhases* Phases = GetOwner()->FindComponentByClass<URPGBossPhases>();
	const EResult Result = Apply(State, MakeConfig(), Amount, bDead, Encounter && Encounter->IsDormant(), Phases && Phases->IsInTransition(), ProcFrame == GFrameCounter);
	LastResult = Name(Result);
	switch (Result)
	{
	case EResult::Proc:
		UE_LOG(LogRPGBleed, Log, TEXT("%s: bleed +%.0f (%s) crossed the threshold: proc %d, next threshold %.0f"), *GetOwner()->GetName(), Amount, Source, State.Procs, State.Threshold);
		DoProc();
		break;
	case EResult::Added:
		UE_LOG(LogRPGBleed, Log, TEXT("%s: bleed +%.0f (%s): %.0f of %.0f"), *GetOwner()->GetName(), Amount, Source, State.Buildup, State.Threshold);
		break;
	case EResult::IgnoredAmount:
		break;
	default:
		++Ignored;
		UE_LOG(LogRPGBleed, Log, TEXT("%s: bleed +%.0f (%s) ignored: %s"), *GetOwner()->GetName(), Amount, Source, Name(Result));
		break;
	}
	return Result;
}

FString URPGBossBleed::AddBuildupForTest(float Amount)
{
#if UE_BUILD_SHIPPING
	return TEXT("unavailable in Shipping");
#else
	return RPGBleedRules::Name(AddBuildup(Amount, TEXT("test")));
#endif
}

void URPGBossBleed::DoProc()
{
	ProcFrame = GFrameCounter;
	double Health = 0.0, Max = 0.0;
	if (!ReadAttribute(GetOwner(), HealthTag, false, Health) || !ReadAttribute(GetOwner(), HealthTag, true, Max))
	{
		return;
	}
	const float Damage = RPGBleedRules::ProcDamage(static_cast<float>(Max), static_cast<float>(Health), MakeConfig());
	LastProcDamage = Damage;
	WriteAttribute(GetOwner(), HealthTag, Health - Damage);
	// The health lost is not a hit: the stance break's critical multiplier must not see it (Freeze 20.2).
	if (URPGBossStagger* Stagger = GetOwner()->FindComponentByClass<URPGBossStagger>())
	{
		Stagger->AcknowledgeHealthLoss(Damage);
	}
	UE_LOG(LogRPGBleed, Log, TEXT("%s: bleed proc: health %.1f -> %.1f (%.1f, %.1f percent of %.0f)"), *GetOwner()->GetName(), Health, Health - Damage, Damage, Max > 0.0 ? 100.0 * Damage / Max : 0.0, Max);
	const FVector Where = GetOwner()->GetActorLocation() + FVector(0.f, 0.f, EffectHeight);
	if (LoadedEffect)
	{
		UNiagaraFunctionLibrary::SpawnSystemAtLocation(GetWorld(), LoadedEffect, Where, FRotator::ZeroRotator, FVector(2.f));
	}
	ARPGFlipbookEffect::Spawn(GetWorld(), Where, ERPGEFlipbookKind::BloodBurst, LoadedBloodFlipbook);
	if (LoadedSound)
	{
		UGameplayStatics::PlaySoundAtLocation(this, LoadedSound, Where, 1.2f, 0.7f);
	}
}

void URPGBossBleed::ResetBleed()
{
	State.Buildup = 0.f;
	State.Threshold = InitialThreshold;
	ProcFrame = MAX_uint64;
}
