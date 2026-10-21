// Copyright One Boss Fight. All Rights Reserved.

#include "Audio/RPGBossMusic.h"
#include "Components/AudioComponent.h"
#include "Kismet/GameplayStatics.h"
#include "Pack/RPGBlueprintCall.h"
#include "Player/RPGBossEncounter.h"
#include "Player/RPGBossPhases.h"
#include "Player/RPGLegend.h"
#include "Sound/SoundBase.h"

DEFINE_LOG_CATEGORY_STATIC(LogRPGMusic, Log, All);

URPGBossMusic::URPGBossMusic()
{
	PrimaryComponentTick.bCanEverTick = true;
	PrimaryComponentTick.TickInterval = 0.25f;
}

void URPGBossMusic::BeginPlay()
{
	Super::BeginPlay();
	Encounter = GetOwner() ? GetOwner()->FindComponentByClass<URPGBossEncounter>() : nullptr;
}

void URPGBossMusic::EndPlay(const EEndPlayReason::Type EndPlayReason)
{
	// The actor is going (the pack removes the boss a few seconds after its death): whatever still fades is cut now.
	if (PlayerPhase1)
	{
		PlayerPhase1->Stop();
	}
	if (PlayerPhase2)
	{
		PlayerPhase2->Stop();
	}
	Super::EndPlay(EndPlayReason);
}

FString URPGBossMusic::GetActiveTrackName() const
{
	switch (ActiveTrack)
	{
	case ETrack::Phase1: return TEXT("Phase1");
	case ETrack::Phase2: return TEXT("Phase2");
	default: return TEXT("None");
	}
}

bool URPGBossMusic::IsAnyComponentPlaying() const
{
	return (PlayerPhase1 && PlayerPhase1->IsPlaying()) || (PlayerPhase2 && PlayerPhase2->IsPlaying());
}

UAudioComponent* URPGBossMusic::EnsurePlayer(ETrack Track)
{
	TObjectPtr<UAudioComponent>& Slot = Track == ETrack::Phase2 ? PlayerPhase2 : PlayerPhase1;
	USoundBase* Sound = Track == ETrack::Phase2 ? PhaseTwoMusic.Get() : Music.Get();
	if (!Slot && Sound)
	{
		// One component per track, created at most once: a restart of a track that still fades out restarts the same component, so there is never a second voice. Null under -nosound.
		Slot = UGameplayStatics::CreateSound2D(this, Sound, Track == ETrack::Phase2 ? PhaseTwoVolume : Volume, 1.f, 0.f, nullptr, /*bPersistAcrossLevelTransition=*/false, /*bAutoDestroy=*/false);
	}
	return Slot;
}

void URPGBossMusic::StartTrack(ETrack Track)
{
	if (Track == ETrack::None || ActiveTrack != ETrack::None)
	{
		return;
	}
	if ((Track == ETrack::Phase1 && !Music) || (Track == ETrack::Phase2 && !PhaseTwoMusic))
	{
		return;
	}
	if (UAudioComponent* Player = EnsurePlayer(Track))
	{
		Player->FadeIn(FadeInSeconds, Track == ETrack::Phase2 ? PhaseTwoVolume : Volume, Track == ETrack::Phase2 ? PhaseTwoStartOffsetSeconds : 0.f);
	}
	ActiveTrack = Track;
	if (Track == ETrack::Phase1)
	{
		++StartCountPhase1;
	}
	else
	{
		++StartCountPhase2;
	}
	UE_LOG(LogRPGMusic, Log, TEXT("%s: music %s starts"), *GetOwner()->GetName(), *GetActiveTrackName());
}

void URPGBossMusic::SwapToPhaseTwo()
{
	if (ActiveTrack != ETrack::Phase1 || !PhaseTwoMusic)
	{
		return;
	}
	if (PlayerPhase1)
	{
		PlayerPhase1->FadeOut(CrossfadeSeconds, 0.f, EAudioFaderCurve::Sin);
	}
	if (UAudioComponent* Player = EnsurePlayer(ETrack::Phase2))
	{
		Player->FadeIn(CrossfadeSeconds, PhaseTwoVolume, PhaseTwoStartOffsetSeconds, EAudioFaderCurve::Sin);
	}
	ActiveTrack = ETrack::Phase2;
	++SwapCount;
	++StartCountPhase2;
	UE_LOG(LogRPGMusic, Log, TEXT("%s: music crossfades to Phase 2 over %.1f s"), *GetOwner()->GetName(), CrossfadeSeconds);
}

void URPGBossMusic::StopAll(bool bBossDead)
{
	if (ActiveTrack == ETrack::None)
	{
		return;
	}
	const float Seconds = bBossDead ? VictoryFadeOutSeconds : FadeOutSeconds;
	for (UAudioComponent* Player : {PlayerPhase1.Get(), PlayerPhase2.Get()})
	{
		if (Player && Player->IsPlaying())
		{
			Player->FadeOut(Seconds, 0.f);
		}
	}
	ActiveTrack = ETrack::None;
	++StopCount;
	UE_LOG(LogRPGMusic, Log, TEXT("%s: music stops (%s, fade %.1f s)"), *GetOwner()->GetName(), bBossDead ? TEXT("boss dead") : TEXT("reset or asleep"), Seconds);
}

void URPGBossMusic::StartForTest()
{
	StartTrack(ETrack::Phase1);
}

void URPGBossMusic::TickComponent(float DeltaTime, ELevelTick TickType, FActorComponentTickFunction* ThisTickFunction)
{
	Super::TickComponent(DeltaTime, TickType, ThisTickFunction);
	AActor* Boss = GetOwner();
	if (Boss && !Encounter)
	{
		Encounter = Boss->FindComponentByClass<URPGBossEncounter>(); // added after this component by the subsystem
	}
	if (Boss && !Phases)
	{
		Phases = Boss->FindComponentByClass<URPGBossPhases>();
	}
	if (!Boss || !Encounter)
	{
		return;
	}
	double Health = 1.0;
	const bool bHaveHealth = RPGPack::ReadAttribute(Boss, TEXT("Attribute.Health"), /*bMax=*/false, Health);
	const bool bDead = bHaveHealth && Health <= 0.0;

	// The track the fight asks for now. None while the boss sleeps or is dead (Freeze 783: music fades without restarting the combat theme), Phase 2 from the phase two threshold.
	// Once Phase 2 plays it stays until the fight ends: a console switch of rpg.Legend in the middle never swaps back.
	if (Encounter->IsDormant() || bDead)
	{
		StopAll(bDead);
		return;
	}
	const bool bSwapWanted = bSwapAtPhaseTwo && PhaseTwoMusic && URPGLegendSubsystem::IsLegendOn() && Phases && Phases->IsPhaseTwo();
	if (ActiveTrack == ETrack::None)
	{
		StartTrack(bSwapWanted ? ETrack::Phase2 : ETrack::Phase1); // a boss that wakes already in phase two starts straight on the climax
	}
	else if (ActiveTrack == ETrack::Phase1 && bSwapWanted)
	{
		SwapToPhaseTwo();
	}
}
