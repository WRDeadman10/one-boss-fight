// Copyright One Boss Fight. All Rights Reserved.

#include "Player/RPGBossDormantWake.h"
#include "HAL/IConsoleManager.h"

#include "Animation/AnimInstance.h"
#include "Animation/AnimSequence.h"
#include "Components/SkeletalMeshComponent.h"
#include "Engine/World.h"
#include "GameFramework/Character.h"
#include "Player/RPGBossClips.h"
#include "Player/RPGBossEncounter.h"
#include "Player/RPGBossDormantWakeRules.h"
#include "UObject/SoftObjectPath.h"

URPGBossDormantWake::URPGBossDormantWake()
{
	PrimaryComponentTick.bCanEverTick = true;
	PrimaryComponentTick.TickInterval = 0.05f;
	DormantClip = TSoftObjectPtr<UAnimSequence>(FSoftObjectPath(TEXT("/Game/OneBossFight/Boss01/Animations/AN_Boss01_DormantIdle.AN_Boss01_DormantIdle")));
	WakeClip = TSoftObjectPtr<UAnimSequence>(FSoftObjectPath(TEXT("/Game/OneBossFight/Boss01/Animations/AN_Boss01_Wake.AN_Boss01_Wake")));
}

URPGBossDormantWake* URPGBossDormantWake::Find(const AActor* Actor)
{
	return Actor ? Actor->FindComponentByClass<URPGBossDormantWake>() : nullptr;
}

void URPGBossDormantWake::StopFor(AActor* Actor, const TCHAR* Reason)
{
	if (URPGBossDormantWake* Clips = Find(Actor))
	{
		Clips->StopClips(Reason);
	}
}

void URPGBossDormantWake::BeginPlay()
{
	Super::BeginPlay();
	LoadedDormantClip = DormantClip.LoadSynchronous();
	LoadedWakeClip = WakeClip.LoadSynchronous();
	if (URPGBossEncounter* Encounter = GetOwner() ? GetOwner()->FindComponentByClass<URPGBossEncounter>() : nullptr)
	{
		AddTickPrerequisiteComponent(Encounter);
		if (Encounter->IsDormant())
		{
			BeginDormant();
		}
	}
}

void URPGBossDormantWake::EndPlay(const EEndPlayReason::Type EndPlayReason)
{
	StopClips(TEXT("end play"));
	Super::EndPlay(EndPlayReason);
}

ACharacter* URPGBossDormantWake::GetBoss() const
{
	return Cast<ACharacter>(GetOwner());
}

UAnimSequence* URPGBossDormantWake::GetDormantClip()
{
	if (!LoadedDormantClip)
	{
		LoadedDormantClip = DormantClip.LoadSynchronous();
	}
	return LoadedDormantClip;
}

UAnimSequence* URPGBossDormantWake::GetWakeClip()
{
	if (!LoadedWakeClip)
	{
		LoadedWakeClip = WakeClip.LoadSynchronous();
	}
	return LoadedWakeClip;
}

void URPGBossDormantWake::BeginDormant()
{
	StopClips(TEXT("sleep"));
	if (ACharacter* Boss = GetBoss())
	{
		DormantMontage = RPGBossClips::Play(Boss, GetDormantClip(), 0.15f, 0.15f, 1.f, 9999);
		if (DormantMontage.IsValid())
		{
			++DormantPlayCount;
		}
	}
}

#if !UE_BUILD_SHIPPING
// Test sessions: rpg.WakeClip 0 skips the 3.5 s wake clip so that the older drivers, which attack right after Wake(), keep their timings (Scripts/RunDrivers.ps1 runs Scripts/Editor/wake_clip_off.py; pie_dormant_wake.py switches it on itself). Shipping always plays it.
static TAutoConsoleVariable<int32> CVarWakeClip(TEXT("rpg.WakeClip"), 1, TEXT("0 skips the authored wake clip (tests only)."), ECVF_Default);
#endif

bool URPGBossDormantWake::BeginWake()
{
#if !UE_BUILD_SHIPPING
	if (CVarWakeClip.GetValueOnGameThread() == 0)
	{
		// Test switch: no wake clip, but the authored dormant loop must not outlive the sleep: a looping montage left on an awake boss keeps the tracker non-neutral (an unforced A5 punish is refused: pie_damage_path M2, 2026-10-25).
		if (ACharacter* SleepingBoss = GetBoss())
		{
			if (UAnimInstance* Anim = SleepingBoss->GetMesh() ? SleepingBoss->GetMesh()->GetAnimInstance() : nullptr)
			{
				if (DormantMontage.IsValid())
				{
					Anim->Montage_Stop(0.1f, DormantMontage.Get());
				}
			}
		}
		DormantMontage = nullptr;
		return false;
	}
#endif
	StopClips(TEXT("wake"));
	ACharacter* Boss = GetBoss();
	WakeMontage = RPGBossClips::Play(Boss, GetWakeClip(), 0.1f, 0.1f);
	if (!WakeMontage.IsValid())
	{
		return false;
	}
	bWaking = true;
	WakeStartedAt = GetWorld() ? GetWorld()->GetTimeSeconds() : 0.0;
	++WakePlayCount;
	return true;
}

void URPGBossDormantWake::StopClips(const TCHAR* Reason)
{
	if (ACharacter* Boss = GetBoss())
	{
		if (UAnimInstance* Anim = Boss->GetMesh() ? Boss->GetMesh()->GetAnimInstance() : nullptr)
		{
			if (DormantMontage.IsValid())
			{
				Anim->Montage_Stop(0.1f, DormantMontage.Get());
			}
			if (WakeMontage.IsValid())
			{
				Anim->Montage_Stop(0.1f, WakeMontage.Get());
			}
		}
	}
	DormantMontage = nullptr;
	WakeMontage = nullptr;
	bWaking = false;
	WakeStartedAt = -1.0;
	if (URPGBossEncounter* Encounter = GetOwner() ? GetOwner()->FindComponentByClass<URPGBossEncounter>() : nullptr)
	{
		Encounter->CancelWake();
	}
}

FString URPGBossDormantWake::GetStageName() const
{
	if (bWaking)
	{
		return TEXT("wake");
	}
	return DormantMontage.IsValid() ? TEXT("dormant") : TEXT("none");
}

void URPGBossDormantWake::TickComponent(float DeltaTime, ELevelTick TickType, FActorComponentTickFunction* ThisTickFunction)
{
	Super::TickComponent(DeltaTime, TickType, ThisTickFunction);
	URPGBossEncounter* Encounter = GetOwner() ? GetOwner()->FindComponentByClass<URPGBossEncounter>() : nullptr;
	ACharacter* Boss = GetBoss();
	UAnimInstance* Anim = Boss && Boss->GetMesh() ? Boss->GetMesh()->GetAnimInstance() : nullptr;
	if (!Encounter || !Anim)
	{
		return;
	}
	if (Encounter->IsDormant())
	{
		if (!DormantMontage.IsValid() || !Anim->Montage_IsPlaying(DormantMontage.Get()))
		{
			BeginDormant();
		}
		return;
	}
	if (!bWaking)
	{
		return;
	}
	const float Elapsed = GetWorld() ? static_cast<float>(GetWorld()->GetTimeSeconds() - WakeStartedAt) : 0.f;
	const bool bPlaying = WakeMontage.IsValid() && Anim->Montage_IsPlaying(WakeMontage.Get());
	const float Expected = LoadedWakeClip ? LoadedWakeClip->GetPlayLength() : 0.f;
	if (RPGBossDormantWakeRules::ShouldFinishWake(bPlaying, Elapsed, Expected))
	{
		WakeMontage = nullptr;
		bWaking = false;
		WakeStartedAt = -1.0;
		Encounter->FinishWake();
	}
}
