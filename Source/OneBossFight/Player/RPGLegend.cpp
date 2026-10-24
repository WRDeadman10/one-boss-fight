// Copyright One Boss Fight. All Rights Reserved.

#include "Player/RPGLegend.h"
#include "Camera/CameraModifier_CameraShake.h"
#include "Camera/PlayerCameraManager.h"
#include "Components/CapsuleComponent.h"
#include "Engine/World.h"
#include "GameFramework/Character.h"
#include "GameFramework/PlayerController.h"
#include "HAL/IConsoleManager.h"
#include "HAL/PlatformTime.h"
#include "Kismet/GameplayStatics.h"
#include "Pack/RPGBlueprintCall.h"
#include "Player/RPGAttackTracker.h"
#include "Player/RPGBossEncounter.h"
#include "Player/RPGBossPhases.h"
#include "Player/RPGBossStagger.h"
#include "UI/RPGBossHud.h"

DEFINE_LOG_CATEGORY_STATIC(LogRPGLegend, Log, All);

static TAutoConsoleVariable<int32> CVarRPGLegend(TEXT("rpg.Legend"), 1,
	TEXT("Legend pass: 1 (default) hit stop, slow motion, camera shake and the music swap are on, 0 = none of them starts (counted as suppressed; the music itself still follows the encounter)."), ECVF_Default);

static TAutoConsoleVariable<float> CVarRPGLegendShakeScale(TEXT("rpg.LegendShakeScale"), 1.f,
	TEXT("Global multiplier of every camera shake of the legend pass, 0 to 1 (accessibility, tuning without a build)."), ECVF_Default);

using namespace RPGPack;

namespace
{
	/** The local player's camera manager (single player), or null. */
	APlayerCameraManager* LocalCameraManager(const UWorld* World)
	{
		const APlayerController* Controller = World ? World->GetFirstPlayerController() : nullptr;
		return Controller ? Controller->PlayerCameraManager.Get() : nullptr;
	}
}

// ---------------------------------------------------------------------------------------------
// URPGLegendSubsystem
// ---------------------------------------------------------------------------------------------

bool URPGLegendSubsystem::ShouldCreateSubsystem(UObject* Outer) const
{
	const UWorld* World = Cast<UWorld>(Outer);
	return World && World->IsGameWorld();
}

URPGLegendSubsystem* URPGLegendSubsystem::Get(const UObject* WorldContext)
{
	const UWorld* World = WorldContext ? WorldContext->GetWorld() : nullptr;
	return World ? World->GetSubsystem<URPGLegendSubsystem>() : nullptr;
}

bool URPGLegendSubsystem::IsLegendOn()
{
	return CVarRPGLegend.GetValueOnGameThread() != 0;
}

float URPGLegendSubsystem::GetShakeScaleCVar()
{
	return FMath::Clamp(CVarRPGLegendShakeScale.GetValueOnGameThread(), 0.f, 1.f);
}

void URPGLegendSubsystem::Deinitialize()
{
	CancelAll(TEXT("world teardown")); // PIE end, level reload by OpenLevel, editor quit: time is never left dilated
	if (TickerHandle.IsValid())
	{
		FTSTicker::GetCoreTicker().RemoveTicker(TickerHandle);
		TickerHandle.Reset();
	}
	Super::Deinitialize();
}

bool URPGLegendSubsystem::CheckRequest(const URPGBossEncounter* Encounter, int32 Generation)
{
	if (!IsLegendOn())
	{
		++SuppressedCount;
		return false;
	}
	// Cosmetic feedback ranks last (Freeze 21, item 8): never in a dormant fight, never for a fight that has been reset.
	if (!Encounter || Encounter->IsDormant() || Encounter->GetGeneration() != Generation)
	{
		++RefusedCount;
		return false;
	}
	return true;
}

void URPGLegendSubsystem::EnsureTicker()
{
	if (!TickerHandle.IsValid())
	{
		// Interval 0: every frame, in REAL time (the ticker is not dilated), so a 0.08 s hit stop is 0.08 s at 30, 60 or 120 FPS to within one frame.
		TickerHandle = FTSTicker::GetCoreTicker().AddTicker(FTickerDelegate::CreateUObject(this, &URPGLegendSubsystem::TickEffects), 0.f);
	}
}

bool URPGLegendSubsystem::RequestHitStop(AActor* First, AActor* Second, float RealSeconds, float Dilation, const URPGBossEncounter* Encounter, int32 Generation)
{
	if (!CheckRequest(Encounter, Generation) || !GetWorld())
	{
		return false;
	}
	HitStop.Begin(Dilation, FPlatformTime::Seconds(), RealSeconds, 1.f); // a second request only moves the deadline; the applied value stays absolute
	for (AActor* Actor : {First, Second})
	{
		if (!Actor)
		{
			continue;
		}
		const bool bKnown = Stopped.ContainsByPredicate([Actor](const FStoppedActor& Entry) { return Entry.Actor.Get() == Actor; });
		if (!bKnown)
		{
			FStoppedActor Entry;
			Entry.Actor = Actor;
			Entry.Saved = Actor->CustomTimeDilation; // captured once: never an already dilated value
			Stopped.Add(Entry);
		}
		Actor->CustomTimeDilation = HitStop.Applied;
	}
	RequestOwner = Encounter;
	RequestGeneration = Generation;
	EnsureTicker();
	return true;
}

bool URPGLegendSubsystem::RequestSlowMotion(float Scale, float RealSeconds, const URPGBossEncounter* Encounter, int32 Generation)
{
	UWorld* World = GetWorld();
	if (!CheckRequest(Encounter, Generation) || !World)
	{
		return false;
	}
	if (SlowMotion.Begin(Scale, FPlatformTime::Seconds(), RealSeconds, UGameplayStatics::GetGlobalTimeDilation(World)))
	{
		UGameplayStatics::SetGlobalTimeDilation(World, SlowMotion.Applied);
		const float Now = UGameplayStatics::GetGlobalTimeDilation(World);
		if (!FMath::IsNearlyEqual(Now, SlowMotion.Applied, 0.01f))
		{
			UE_LOG(LogRPGLegend, Warning, TEXT("legend: the world clamped the slow motion scale %.3f to %.3f"), SlowMotion.Applied, Now);
			SlowMotion.Applied = Now;
		}
	}
	RequestOwner = Encounter;
	RequestGeneration = Generation;
	EnsureTicker();
	return true;
}

void URPGLegendSubsystem::RestoreHitStop(const TCHAR* Reason)
{
	for (const FStoppedActor& Entry : Stopped)
	{
		if (AActor* Actor = Entry.Actor.Get())
		{
			if (!FMath::IsNearlyEqual(Actor->CustomTimeDilation, HitStop.Applied, 0.001f))
			{
				UE_LOG(LogRPGLegend, Warning, TEXT("legend: %s had custom time dilation %.3f during the hit stop (we set %.3f): someone else changed it, restored anyway (%s)"), *Actor->GetName(), Actor->CustomTimeDilation, HitStop.Applied, Reason);
			}
			Actor->CustomTimeDilation = Entry.Saved; // the guarantee wins: back to what it was before the first request
		}
	}
	Stopped.Reset();
	HitStop.End();
	++RestoreCount;
}

void URPGLegendSubsystem::RestoreSlowMotion(const TCHAR* Reason)
{
	UWorld* World = GetWorld();
	const float Applied = SlowMotion.Applied;
	const float Saved = SlowMotion.End();
	if (World)
	{
		const float Now = UGameplayStatics::GetGlobalTimeDilation(World);
		if (FMath::IsNearlyEqual(Now, Applied, 0.02f))
		{
			UGameplayStatics::SetGlobalTimeDilation(World, Saved);
		}
		else
		{
			UE_LOG(LogRPGLegend, Log, TEXT("legend: global time dilation is %.3f, not the %.3f we set: left alone (%s)"), Now, Applied, Reason); // a console slomo, for one
		}
	}
	++RestoreCount;
}

void URPGLegendSubsystem::CancelAll(const TCHAR* Reason)
{
	const bool bHitStop = HitStop.bActive;
	const bool bSlow = SlowMotion.bActive;
	if (bHitStop)
	{
		RestoreHitStop(Reason);
	}
	if (bSlow)
	{
		RestoreSlowMotion(Reason);
	}
	if (APlayerCameraManager* Camera = LocalCameraManager(GetWorld()))
	{
		Camera->StopAllInstancesOfCameraShake(URPGSlamCameraShake::StaticClass(), true);
		Camera->StopAllInstancesOfCameraShake(URPGRoarCameraShake::StaticClass(), true);
	}
	if (bHitStop || bSlow)
	{
		++CancelCount;
		UE_LOG(LogRPGLegend, Log, TEXT("legend: cancelled (%s), hit stop %d slow motion %d"), Reason, bHitStop ? 1 : 0, bSlow ? 1 : 0);
	}
}

bool URPGLegendSubsystem::TickEffects(float DeltaSeconds)
{
	if (!IsLegendOn())
	{
		CancelAll(TEXT("rpg.Legend 0"));
	}
	else if (HitStop.bActive || SlowMotion.bActive)
	{
		const URPGBossEncounter* Owner = RequestOwner.Get();
		if (!Owner)
		{
			CancelAll(TEXT("the boss is gone"));
		}
		else if (Owner->GetGeneration() != RequestGeneration)
		{
			CancelAll(TEXT("encounter reset"));
		}
	}
	const double Now = FPlatformTime::Seconds();
	if (HitStop.Expired(Now))
	{
		RestoreHitStop(TEXT("expired"));
	}
	if (SlowMotion.Expired(Now))
	{
		RestoreSlowMotion(TEXT("expired"));
	}
	if (!HitStop.bActive && !SlowMotion.bActive)
	{
		TickerHandle.Reset(); // returning false removes this ticker
		return false;
	}
	return true;
}

// ---------------------------------------------------------------------------------------------
// URPGBossLegend
// ---------------------------------------------------------------------------------------------

URPGBossLegend::URPGBossLegend()
{
	PrimaryComponentTick.bCanEverTick = true;
	PrimaryComponentTick.TickGroup = TG_PostUpdateWork; // after the tracker, phases, stagger and HUD have ticked in the frame
	// Slam: the struct defaults (a thump: instant onset, linear decay, a vertical bump, 5 cm at most: far under the 34 cm spring arm probe).
	// Roar: a swelling rumble that ends with the 1.5 s clip, felt across the arena.
	Roar.Duration = 1.5f;
	Roar.BlendIn = 0.25f;
	Roar.BlendOut = 0.5f;
	Roar.LocationAmplitude = FVector(1.0, 1.5, 2.0);
	Roar.LocationFrequency = FVector(17.0, 21.0, 24.0);
	Roar.RotationAmplitude = FRotator(0.7, 0.5, 0.5);
	Roar.RotationFrequency = FRotator(19.0, 15.0, 13.0);
	Roar.InnerRadius = 1500.f;
	Roar.OuterRadius = 4500.f;
	Roar.Falloff = 1.f;
}

bool URPGBossLegend::FindParts()
{
	AActor* Boss = GetOwner();
	if (!Boss)
	{
		return false;
	}
	// Added after the HUD and the debug components, but looked up lazily like the HUD does: a part that is not there yet is simply not polled yet.
	if (!Encounter)
	{
		Encounter = Boss->FindComponentByClass<URPGBossEncounter>();
	}
	if (!Tracker)
	{
		Tracker = Boss->FindComponentByClass<URPGAttackTracker>();
	}
	if (!Phases)
	{
		Phases = Boss->FindComponentByClass<URPGBossPhases>();
	}
	if (!Stagger)
	{
		Stagger = Boss->FindComponentByClass<URPGBossStagger>();
	}
	if (!Hud)
	{
		Hud = Boss->FindComponentByClass<URPGBossHud>();
	}
	return Encounter != nullptr;
}

bool URPGBossLegend::EffectsAllowed(bool bAllowDead)
{
	if (!bEnabled || !URPGLegendSubsystem::IsLegendOn())
	{
		++SuppressedCount;
		return false;
	}
	if (!Encounter || Encounter->IsDormant())
	{
		return false;
	}
	if (!bAllowDead)
	{
		double Health = 1.0;
		if (ReadAttribute(GetOwner(), TEXT("Attribute.Health"), false, Health) && Health <= 0.0)
		{
			return false; // death outranks every effect (Freeze 21)
		}
	}
	return true;
}

bool URPGBossLegend::PlayShake(TSubclassOf<UCameraShakeBase> ShakeClass, const FRPGShakeSettings& Settings, const FVector& Epicentre, int32& Counter)
{
	APlayerCameraManager* Camera = LocalCameraManager(GetWorld());
	if (!Camera)
	{
		++ShakeNotStartedCount;
		return false;
	}
	const float Distance = static_cast<float>(FVector::Dist(Epicentre, Camera->GetCameraLocation()));
	const float Scale = RPGLegend::ShakeScale(Distance, Settings.InnerRadius, Settings.OuterRadius, Settings.Falloff) * GlobalShakeScale * URPGLegendSubsystem::GetShakeScaleCVar();
	LastShakeDistance = Distance;
	LastShakeScale = Scale;
	if (Scale < MinShakeScale)
	{
		++ShakeTooFarCount;
		return false;
	}
	FAddCameraShakeParams Params(Scale, ECameraShakePlaySpace::CameraLocal);
	const FRPGShakeSettings Copy = Settings; // the shake instance outlives this call
	Params.Initializer = FOnInitializeCameraShake::CreateLambda([Copy](UCameraShakeBase* Shake) { RPGLegend::ApplyShakeSettings(Shake, Copy); });
	if (!Camera->StartCameraShake(ShakeClass, Params))
	{
		++ShakeNotStartedCount; // no camera shake modifier on this camera manager
		return false;
	}
	++Counter;
	return true;
}

bool URPGBossLegend::HandleSlam(FName Move)
{
	if (!EffectsAllowed(false))
	{
		return false;
	}
	const ACharacter* Character = Cast<ACharacter>(GetOwner());
	const float HalfHeight = Character && Character->GetCapsuleComponent() ? Character->GetCapsuleComponent()->GetScaledCapsuleHalfHeight() : 0.f;
	const FVector Feet = GetOwner()->GetActorLocation() - FVector(0.0, 0.0, HalfHeight);
	const bool bPlayed = PlayShake(URPGSlamCameraShake::StaticClass(), Slam, Feet, SlamShakeCount);
	UE_LOG(LogRPGLegend, Verbose, TEXT("legend: slam shake for %s (%s), scale %.2f at %.0f cm"), *Move.ToString(), bPlayed ? TEXT("started") : TEXT("not started"), LastShakeScale, LastShakeDistance);
	return bPlayed;
}

bool URPGBossLegend::HandleRoar()
{
	if (!EffectsAllowed(false))
	{
		return false;
	}
	return PlayShake(URPGRoarCameraShake::StaticClass(), Roar, GetOwner()->GetActorLocation(), RoarShakeCount);
}

bool URPGBossLegend::HandleHitStop(bool bLethal)
{
	if (!EffectsAllowed(true) || (bLethal && bSkipHitStopOnLethal))
	{
		return false;
	}
	URPGLegendSubsystem* Time = URPGLegendSubsystem::Get(this);
	if (!Time || !Encounter)
	{
		return false;
	}
	if (!Time->RequestHitStop(GetOwner(), UGameplayStatics::GetPlayerPawn(this, 0), HitStopSeconds, HitStopDilation, Encounter, Encounter->GetGeneration()))
	{
		return false;
	}
	++HitStopCount;
	return true;
}

bool URPGBossLegend::HandleSlowMotion()
{
	if (!EffectsAllowed(true))
	{
		return false;
	}
	URPGLegendSubsystem* Time = URPGLegendSubsystem::Get(this);
	if (!Time || !Encounter)
	{
		return false;
	}
	if (!Time->RequestSlowMotion(SlowMotionScale, SlowMotionSeconds, Encounter, Encounter->GetGeneration()))
	{
		return false;
	}
	++SlowMotionCount;
	if (APlayerCameraManager* Camera = LocalCameraManager(GetWorld()))
	{
		Camera->StopAllInstancesOfCameraShake(URPGRoarCameraShake::StaticClass(), false); // death outranks the roar: it blends out
	}
	return true;
}

void URPGBossLegend::TickComponent(float DeltaTime, ELevelTick TickType, FActorComponentTickFunction* ThisTickFunction)
{
	Super::TickComponent(DeltaTime, TickType, ThisTickFunction);
	if (!FindParts())
	{
		return;
	}
	const int32 Generation = Encounter->GetGeneration();
	if (Generation != LastGeneration)
	{
		if (LastGeneration != 0)
		{
			if (URPGLegendSubsystem* Time = URPGLegendSubsystem::Get(this))
			{
				Time->CancelAll(TEXT("encounter reset"));
			}
		}
		LastGeneration = Generation;
	}
	// The counters of the sources never go down: the key of an event is the value its effect was made for. The first poll of a part records the current value (nothing fires for the past).
	if (Phases && !bRoarPrimed)
	{
		LastRoarCount = Phases->GetPhaseTwoCount();
		bRoarPrimed = true;
	}
	if (Stagger && !bRiposteKeyPrimed)
	{
		LastRiposteCount = Stagger->GetRiposteCount();
		bRiposteKeyPrimed = true;
	}
	if (Hud && !bVictoryPrimed)
	{
		LastVictoryCount = Hud->GetVictoryCount();
		bVictoryPrimed = true;
	}

	// 1. Slam (A2, A6): once per attack instance, from the first frame the instance has reached its active window (a frame hitch that skips Active still fires; a vetoed or interrupted attack never does).
	if (Tracker)
	{
		const FName Move = Tracker->GetCurrentMove();
		if ((Move == TEXT("A2") || Move == TEXT("A6")) && Tracker->HasReachedActive() && Tracker->GetAttackInstance() != LastSlamInstance)
		{
			LastSlamInstance = Tracker->GetAttackInstance();
			HandleSlam(Move);
		}
	}
	// 2. Roar: once per fight (the phase two counter).
	if (Phases && bRoarPrimed && Phases->GetPhaseTwoCount() != LastRoarCount)
	{
		LastRoarCount = Phases->GetPhaseTwoCount();
		HandleRoar();
	}
	// 3. Riposte hit: the stagger component counts the riposte when the critical hit is applied.
	if (Stagger && bRiposteKeyPrimed && Stagger->GetRiposteCount() != LastRiposteCount)
	{
		LastRiposteCount = Stagger->GetRiposteCount();
		double Health = 1.0;
		const bool bLethal = ReadAttribute(GetOwner(), TEXT("Attribute.Health"), false, Health) && Health <= 0.0;
		HandleHitStop(bLethal);
	}
	// 4. Kill: the HUD fires its victory once per generation.
	if (Hud && bVictoryPrimed && Hud->GetVictoryCount() != LastVictoryCount)
	{
		LastVictoryCount = Hud->GetVictoryCount();
		HandleSlowMotion();
	}
}

bool URPGBossLegend::IsHitStopActive() const
{
	const URPGLegendSubsystem* Time = URPGLegendSubsystem::Get(this);
	return Time && Time->IsHitStopActive();
}

bool URPGBossLegend::IsSlowMotionActive() const
{
	const URPGLegendSubsystem* Time = URPGLegendSubsystem::Get(this);
	return Time && Time->IsSlowMotionActive();
}

int32 URPGBossLegend::GetCancelCount() const
{
	const URPGLegendSubsystem* Time = URPGLegendSubsystem::Get(this);
	return Time ? Time->GetCancelCount() : 0;
}

int32 URPGBossLegend::GetRestoreCount() const
{
	const URPGLegendSubsystem* Time = URPGLegendSubsystem::Get(this);
	return Time ? Time->GetRestoreCount() : 0;
}

int32 URPGBossLegend::GetTimeSuppressedCount() const
{
	const URPGLegendSubsystem* Time = URPGLegendSubsystem::Get(this);
	return Time ? Time->GetSuppressedCount() : 0;
}

bool URPGBossLegend::FireSlamForTest(FName Move)
{
#if UE_BUILD_SHIPPING
	return false;
#else
	FindParts();
	return Encounter && HandleSlam(Move);
#endif
}

bool URPGBossLegend::FireRoarForTest()
{
#if UE_BUILD_SHIPPING
	return false;
#else
	FindParts();
	return Encounter && HandleRoar();
#endif
}

bool URPGBossLegend::FireHitStopForTest(bool bLethal)
{
#if UE_BUILD_SHIPPING
	return false;
#else
	FindParts();
	return Encounter && HandleHitStop(bLethal);
#endif
}

bool URPGBossLegend::FireSlowMotionForTest()
{
#if UE_BUILD_SHIPPING
	return false;
#else
	FindParts();
	return Encounter && HandleSlowMotion();
#endif
}
