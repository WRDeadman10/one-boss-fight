// Copyright One Boss Fight. All Rights Reserved.

#include "Player/RPGBossStagger.h"
#include "Player/RPGBossMath.h"
#include "Player/RPGBossEncounter.h"
#include "Player/RPGBossInterrupt.h"
#include "Player/RPGBossClips.h"
#include "GameFramework/PlayerController.h"
#include "Components/CapsuleComponent.h"
#include "TimerManager.h"
#include "Player/RPGBossPhases.h"
#include "Player/RPGBossPosture.h"
#include "Pack/RPGBlueprintCall.h"
#include "AIController.h"
#include "Animation/AnimInstance.h"
#include "Animation/AnimMontage.h"
#include "BrainComponent.h"
#include "Components/SkeletalMeshComponent.h"
#include "Engine/World.h"
#include "GameFramework/Character.h"
#include "GameFramework/CharacterMovementComponent.h"
#include "UObject/UnrealType.h"

DEFINE_LOG_CATEGORY_STATIC(LogRPGStagger, Log, All);

using namespace RPGPack;

namespace
{
	constexpr const TCHAR* HealthTag = TEXT("Attribute.Health");
	constexpr const TCHAR* PoiseTag = TEXT("Attribute.Poise");

	UObject* FindControllerComponent(AController* Controller, const TCHAR* ClassName)
	{
		if (!Controller)
		{
			return nullptr;
		}
		TInlineComponentArray<UActorComponent*> Components(Controller);
		for (UActorComponent* Component : Components)
		{
			if (Component && Component->GetClass()->GetName() == ClassName)
			{
				return Component;
			}
		}
		return nullptr;
	}
}

URPGBossStagger::URPGBossStagger()
{
	PrimaryComponentTick.bCanEverTick = true;
	PrimaryComponentTick.bStartWithTickEnabled = true;
	PrimaryComponentTick.TickInterval = 0.f;

	FallMontage = TSoftObjectPtr<UAnimMontage>(FSoftObjectPath(TEXT("/Game/AdvancedARPGCombat/MeleeCombatSystem/Animations/2handed/KnockdownStart_Anim_Montage.KnockdownStart_Anim_Montage")));
	GetUpMontage = TSoftObjectPtr<UAnimMontage>(FSoftObjectPath(TEXT("/Game/AdvancedARPGCombat/MeleeCombatSystem/Animations/2handed/Knockdown_Getup_Anim_Montage.Knockdown_Getup_Anim_Montage")));
	ImmunityEffect = TSoftClassPtr<UObject>(FSoftObjectPath(TEXT("/Game/AdvancedARPGCombat/MeleeCombatSystem/Blueprints/GameplayEffects/GE_HitStunImmune.GE_HitStunImmune_C")));
	FallClip = TSoftObjectPtr<UAnimSequence>(FSoftObjectPath(TEXT("/Game/OneBossFight/Boss01/Animations/AN_Boss01_StaggerFall.AN_Boss01_StaggerFall")));
	DownClip = TSoftObjectPtr<UAnimSequence>(FSoftObjectPath(TEXT("/Game/OneBossFight/Boss01/Animations/AN_Boss01_StaggerDown.AN_Boss01_StaggerDown")));
	RipostePlayerClip = TSoftObjectPtr<UAnimSequence>(FSoftObjectPath(TEXT("/Game/OneBossFight/Boss01/Animations/AN_Riposte_Player_Front.AN_Riposte_Player_Front")));
	RiposteBossClip = TSoftObjectPtr<UAnimSequence>(FSoftObjectPath(TEXT("/Game/OneBossFight/Boss01/Animations/AN_Riposte_Boss_Reaction.AN_Riposte_Boss_Reaction")));
}

FString URPGBossStagger::GetClipStageName() const
{
	if (!bClipMode)
	{
		return TEXT("none");
	}
	switch (ClipStage)
	{
	case EClipStage::Fall: return TEXT("fall");
	case EClipStage::Down: return TEXT("down");
	case EClipStage::GetUp: return TEXT("getup");
	case EClipStage::Riposte: return TEXT("riposte");
	default: return TEXT("none");
	}
}

bool URPGBossStagger::StartClipFall()
{
	bClipMode = false;
	ClipStage = EClipStage::None;
	ClipMontage = nullptr;
	if (!bUseClips)
	{
		return false;
	}
	LoadedFall = FallClip.LoadSynchronous();
	LoadedDown = DownClip.LoadSynchronous();
	const ACharacter* Character = Cast<ACharacter>(GetOwner());
	if (!LoadedFall || !LoadedDown || !Character)
	{
		return false;
	}
	UAnimMontage* Montage = RPGBossClips::Play(Character, LoadedFall, 0.1f, 0.f); // no blend out: the kneel loop takes over at the last frame, which is the same pose
	if (!Montage)
	{
		return false;
	}
	ClipMontage = Montage;
	ClipStage = EClipStage::Fall;
	bClipMode = true;
	return true;
}

void URPGBossStagger::TickClipDown(UAnimInstance* Anim, double Elapsed, double Now)
{
	const ACharacter* Character = Cast<ACharacter>(GetOwner());
	const float FallLength = LoadedFall ? LoadedFall->GetPlayLength() : 0.7f;
	if (bRiposteRunning)
	{
		return; // the execution plays its own clips; the kneel loop resumes when it ends and the get-up starts after that
	}
	if (ClipStage == EClipStage::Fall && Anim)
	{
		UAnimMontage* Montage = ClipMontage.Get();
		const bool bPlaying = Montage && Anim->Montage_IsPlaying(Montage);
		// A montage that another system started over the fall (a boss attack that the attack tracker vetoes in the next frame) is left alone: the kneel starts when the fall is over, or when the fall was stopped and nothing else plays.
		if ((bPlaying && Anim->Montage_GetPosition(Montage) >= FallLength - 0.03f) || (!bPlaying && !Anim->GetCurrentActiveMontage()))
		{
			// The last frame of the fall is the first frame of the kneel (difference 0.0001): the swap shows nothing.
			ClipMontage = RPGBossClips::Play(Character, LoadedDown, 0.f, 0.15f, 1.f, 40);
			ClipStage = EClipStage::Down;
		}
	}
	else if (ClipStage == EClipStage::Down && Anim && !Anim->GetCurrentActiveMontage())
	{
		// The kneel loop was stopped by something else (a vetoed attack): the boss would stand up in its critical window. The loop starts again.
		ClipMontage = RPGBossClips::Play(Character, LoadedDown, 0.1f, 0.15f, 1.f, 40);
	}
	if (ClipStage == EClipStage::Down && Elapsed >= StaggerSeconds)
	{
		// The get-up is the fall backwards: from the kneel to the standing pose the fall started from.
		ClipMontage = RPGBossClips::Play(Character, LoadedFall, 0.1f, 0.2f, -GetUpRate, 1, FallLength); // blend in 0.1: the kneel loop (a replaced montage stops with the new one's blend in) leaves from any point of its loop
		ClipStage = EClipStage::GetUp;
		Phase = EPhase::GetUp;
		PhaseStart = Now;
		UE_LOG(LogRPGStagger, Log, TEXT("%s: down for %.2f s, %d critical hits, getting up (clip, rate -%.2f)"), *GetOwner()->GetName(), Elapsed, CriticalHitCount, GetUpRate);
	}
}

void URPGBossStagger::StopStaggerMontages(float BlendOut)
{
	if (UAnimInstance* Anim = GetAnimInstance())
	{
		// Only our montages: a plain Montage_Stop() would also stop the pack's death clip.
		// Montage_Stop with a null montage stops every montage of the boss, the pack's death clip included: each pointer is checked (a soft pointer is only resident when something loaded it).
		if (UAnimMontage* Fall = FallMontage.Get())
		{
			Anim->Montage_Stop(BlendOut, Fall);
		}
		if (UAnimMontage* GetUp = GetUpMontage.Get())
		{
			Anim->Montage_Stop(BlendOut, GetUp);
		}
		if (UAnimMontage* Clip = ClipMontage.Get())
		{
			Anim->Montage_Stop(BlendOut, Clip);
		}
	}
	bClipMode = false;
	ClipStage = EClipStage::None;
}

UAnimInstance* URPGBossStagger::GetAnimInstance() const
{
	const ACharacter* Character = Cast<ACharacter>(GetOwner());
	return Character && Character->GetMesh() ? Character->GetMesh()->GetAnimInstance() : nullptr;
}

void URPGBossStagger::BeginPlay()
{
	Super::BeginPlay();
	// Load the clips of the stance break and the riposte now: a synchronous load at the first break, riposte or phase change would block the game thread in the middle of the fight (audit A01, Gate 4 p99). The strong references keep them alive.
	LoadedFall = FallClip.LoadSynchronous();
	LoadedDown = DownClip.LoadSynchronous();
	LoadedRipostePlayer = RipostePlayerClip.LoadSynchronous();
	LoadedRiposteBoss = RiposteBossClip.LoadSynchronous();
}

void URPGBossStagger::TickComponent(float DeltaTime, ELevelTick TickType, FActorComponentTickFunction* ThisTickFunction)
{
	Super::TickComponent(DeltaTime, TickType, ThisTickFunction);
	const UWorld* World = GetWorld();
	if (!World)
	{
		return;
	}
	const double Now = World->GetTimeSeconds();
	if (!CachedHitStun.IsValid())
	{
		CachedHitStun = FindAbilityByClassName(GetOwner(), HitStunAbilityClassName);
	}
	UObject* HitStun = CachedHitStun.Get();
	const bool bActive = HitStun && IsAbilityInstanceActive(HitStun);
	if (bRiposteRunning)
	{
		TickRiposte(Now);
	}
	if (bRiposteExiting)
	{
		TickRiposteExit(Now);
	}

	if (Phase == EPhase::Idle)
	{
		if (bActive && !bWasActive)
		{
			bWasActive = bActive;
			URPGBossPosture* Posture = GetOwner()->FindComponentByClass<URPGBossPosture>();
			if (Posture && Posture->IsPackPoisePinned())
			{
				// The posture pool owns the stance break (Gate 3, M9) and the pack's poise is pinned full: a pack hit stun is the pack's own gate slipping through between two pins (two heavy hits inside 0.05 s took
				// its 100 to 0), not a break the pool earned. End the flinch and pin again; the table's drains decide.
				EndPackFlinch();
				Posture->NotePackStunSuppressed();
				return;
			}
			// No pool (or an unpinned pack poise): the pack's poise gate started its hit stun, that is the break request. It goes through the same gate as the test hooks.
			RequestBreak(false);
			return;
		}
		bWasActive = bActive;
		return;
	}
	bWasActive = bActive;

	UAnimInstance* Anim = GetAnimInstance();
	UAnimMontage* Fall = FallMontage.Get();
	UAnimMontage* GetUp = GetUpMontage.Get();
	const double Elapsed = Now - PhaseStart;
	ApplyCritical();
	if (Phase == EPhase::Idle) // the boss died: ApplyCritical ended the stagger
	{
		return;
	}
	if (Phase == EPhase::Down)
	{
		if (bClipMode)
		{
			TickClipDown(Anim, Elapsed, Now);
			return;
		}
		if (Anim && Fall && !bFrozen && Anim->Montage_IsPlaying(Fall) && Anim->Montage_GetPosition(Fall) >= FreezeAtPosition)
		{
			Anim->Montage_Pause(Fall); // stay on the ground
			bFrozen = true;
		}
		if (Elapsed >= StaggerSeconds)
		{
			if (Anim && GetUp)
			{
				Anim->Montage_Play(GetUp, 1.f);
			}
			Phase = EPhase::GetUp;
			PhaseStart = Now;
			UE_LOG(LogRPGStagger, Log, TEXT("%s: down for %.2f s, %d critical hits, getting up"), *GetOwner()->GetName(), Elapsed, CriticalHitCount);
		}
		return;
	}
	// Getting up
	if (bClipMode)
	{
		const UAnimMontage* Montage = ClipMontage.Get();
		const float Length = LoadedFall ? LoadedFall->GetPlayLength() : 0.7f;
		if (!Anim || !Montage || !Anim->Montage_IsPlaying(Montage) || Anim->Montage_GetPosition(Montage) <= 0.04f || Elapsed > Length / GetUpRate + 0.6)
		{
			EndStagger(true); // the backwards fall is at its last frames, the standing pose; it blends out by itself
		}
		return;
	}
	if (!Anim || !GetUp || !Anim->Montage_IsPlaying(GetUp) || Elapsed > GetUp->GetPlayLength() + 0.5)
	{
		EndStagger(true);
	}
}

bool URPGBossStagger::EndPackFlinch()
{
	UObject* Asc = FindComponentByClassName(GetOwner(), TEXT("BP_AdvancedAbilitySystemComponent_C"));
	UObject* HitStun = CachedHitStun.Get();
	if (!Asc || !HitStun)
	{
		return false;
	}
	const bool bWasPlaying = IsAbilityInstanceActive(HitStun);
	CallBlueprintFunction(Asc, TEXT("End Ability"),
		[&](UFunction& F, uint8* P)
		{
			if (const FObjectProperty* Object = CastField<FObjectProperty>(F.FindPropertyByName(TEXT("AbilityToEnd"))))
			{
				Object->SetObjectPropertyValue(Object->ContainerPtrToValuePtr<void>(P), HitStun);
			}
		},
		[](UFunction&, uint8*) {});
	return bWasPlaying;
}

float URPGBossStagger::GetCooldownRemaining() const
{
	return GetWorld() ? static_cast<float>(FMath::Max(0.0, CooldownEnd - GetWorld()->GetTimeSeconds())) : 0.f;
}

int32 URPGBossStagger::GetDroppedBreakCount(const FString& Reason) const
{
	if (Reason == TEXT("transition")) { return DroppedTransition; }
	if (Reason == TEXT("dead")) { return DroppedDead; }
	if (Reason == TEXT("dormant")) { return DroppedDormant; }
	if (Reason == TEXT("staggered")) { return DroppedStaggered; }
	if (Reason == TEXT("cooldown")) { return DroppedCooldown; }
	return 0;
}

RPGBossRules::EBreakResult URPGBossStagger::RequestBreak(bool bIgnoreCooldown)
{
	using namespace RPGBossRules;
	const UWorld* World = GetWorld();
	const double Now = World ? World->GetTimeSeconds() : 0.0;
	FFlags Flags;
	double Health = 1.0;
	Flags.bDead = ReadAttribute(GetOwner(), HealthTag, false, Health) && Health <= 0.0;
	const URPGBossEncounter* Encounter = GetOwner()->FindComponentByClass<URPGBossEncounter>();
	const URPGBossPhases* Phases = GetOwner()->FindComponentByClass<URPGBossPhases>();
	Flags.bDormant = Encounter && Encounter->IsDormant();
	Flags.bTransition = Phases && Phases->IsInTransition();
	Flags.bStaggered = Phase != EPhase::Idle;
	Flags.bCooldown = Now < CooldownEnd;
	const EBreakResult Result = ResolveBreak(Flags, bIgnoreCooldown);
	LastBreakResult = Name(Result);
	switch (Result)
	{
	case EBreakResult::Started:
		StartStagger();
		return Result;
	case EBreakResult::Dead:
		++DroppedDead;
		EndPackFlinch(); // no hit stun after a lethal hit (Freeze 1269): the flinch must not play over the death clip
		break;
	case EBreakResult::Dormant:
		++DroppedDormant;
		break;
	case EBreakResult::Transition:
		++DroppedTransition;
		if (EndPackFlinch())
		{
			UE_LOG(LogRPGStagger, Warning, TEXT("%s: the pack flinch was active during the phase transition (the immunity effect did not hold), ended"), *GetOwner()->GetName());
		}
		break;
	case EBreakResult::AlreadyStaggered:
		++DroppedStaggered;
		break;
	case EBreakResult::Cooldown:
		++DroppedCooldown;
		break;
	}
	UE_LOG(LogRPGStagger, Log, TEXT("%s: stance break dropped: %s%s"), *GetOwner()->GetName(), Name(Result), Result == EBreakResult::Cooldown ? *FString::Printf(TEXT(" (%.1f s left)"), CooldownEnd - Now) : TEXT(""));
	return Result;
}

void URPGBossStagger::StartStagger()
{
	const double Now = GetWorld()->GetTimeSeconds();
	Phase = EPhase::Down;
	PhaseStart = Now;
	bFrozen = false;
	++StaggerCount;
	CriticalHitCount = 0;
	bRiposteUsed = false;
	RiposteArmedUntil = -1.0;

	// Freeze 17.3 items 2 and 3: the break disables the boss's own attack windows, blade, wave and projectiles, and records what it cancelled.
	RPGBossInterrupt::CancelOffence(GetOwner(), TEXT("stance break"));
	if (bHoldPostureAtZero)
	{
		if (URPGBossPosture* Posture = GetOwner()->FindComponentByClass<URPGBossPosture>())
		{
			Posture->BeginHold(URPGBossPosture::EHold::Zero);
		}
	}

	UObject* Asc = FindComponentByClassName(GetOwner(), TEXT("BP_AdvancedAbilitySystemComponent_C"));
	// The flinch ability would end its montage under ours: end it first.
	EndPackFlinch();
	// Temporary immunity (4 s) so further hits do not replay a flinch over the pose.
	if (Asc)
	{
		if (UClass* Effect = ImmunityEffect.LoadSynchronous())
		{
			CallBlueprintFunction(Asc, TEXT("Apply Gameplay Effect by Class"),
				[&](UFunction& F, uint8* P)
				{
					if (const FClassProperty* ClassProp = CastField<FClassProperty>(F.FindPropertyByName(TEXT("GameplayEffectClass"))))
					{
						ClassProp->SetPropertyValue_InContainer(P, Effect);
					}
					if (const FNumericProperty* Level = CastField<FNumericProperty>(F.FindPropertyByName(TEXT("Level"))))
					{
						Level->SetIntPropertyValue(Level->ContainerPtrToValuePtr<void>(P), static_cast<int64>(1));
					}
				},
				[](UFunction&, uint8*) {});
		}
	}
	HoldBehaviour();
	if (ACharacter* Character = Cast<ACharacter>(GetOwner()))
	{
		if (UCharacterMovementComponent* Movement = Character->GetCharacterMovement())
		{
			Movement->StopMovementImmediately();
		}
	}
	if (UAnimInstance* Anim = GetAnimInstance())
	{
		if (!StartClipFall()) // the project's own fall clip (it stops whatever the boss was playing), else the pack's knockdown montage
		{
			if (UAnimMontage* Fall = FallMontage.LoadSynchronous())
			{
				Anim->Montage_Play(Fall, 1.f);
			}
		}
	}
	double Health = 0.0;
	LastHealth = ReadAttribute(GetOwner(), HealthTag, false, Health) ? Health : -1.0;
	UE_LOG(LogRPGStagger, Log, TEXT("%s: poise break %d, stance break for %.1f s, hits are critical x%.1f (every hit: %d)"), *GetOwner()->GetName(), StaggerCount, StaggerSeconds, CriticalMultiplier, bCriticalOnEveryHit);
}

void URPGBossStagger::EndStagger(bool bResumeBehaviour, bool bClearCooldown)
{
	if (bRiposteRunning)
	{
		EndRiposteExecution(false, TEXT("the stance break ended"));
	}
	const double Now = GetWorld() ? GetWorld()->GetTimeSeconds() : 0.0;
	Phase = EPhase::Idle;
	bClipMode = false; // the get-up clip (if one plays) blends out by itself
	ClipStage = EClipStage::None;
	LastEndTime = Now;
	CooldownEnd = bClearCooldown ? 0.0 : Now + CooldownSeconds;
	bFrozen = false;

	if (UObject* Asc = FindComponentByClassName(GetOwner(), TEXT("BP_AdvancedAbilitySystemComponent_C")))
	{
		if (UClass* Effect = ImmunityEffect.Get())
		{
			CallBlueprintFunction(Asc, TEXT("Remove Active Gameplay Effect By Class"),
				[&](UFunction& F, uint8* P)
				{
					if (const FClassProperty* ClassProp = CastField<FClassProperty>(F.FindPropertyByName(TEXT("GameplayEffectClass"))))
					{
						ClassProp->SetPropertyValue_InContainer(P, Effect);
					}
				},
				[](UFunction&, uint8*) {});
		}
	}
	// Poise starts full again (Freeze 714): the hold ends with a refill (or the pool is refilled when no hold was running); without the posture component the direct write is the fallback.
	URPGBossPosture* Posture = GetOwner()->FindComponentByClass<URPGBossPosture>();
	if (Posture)
	{
		Posture->RefillAfterBreak();
	}
	else
	{
		double MaxPoise = 0.0;
		if (ReadAttribute(GetOwner(), PoiseTag, true, MaxPoise))
		{
			WriteAttribute(GetOwner(), PoiseTag, MaxPoise);
		}
	}
	if (bResumeBehaviour)
	{
		// A phase transition that crossed its threshold during the break starts now, with the behaviour still held: one hand-off, never a gap and never two montages (Freeze 770).
		URPGBossPhases* Phases = GetOwner()->FindComponentByClass<URPGBossPhases>();
		if (Phases && Phases->TryStartQueuedTransition(bBehaviourHeld))
		{
			bBehaviourHeld = false; // the phase component owns the hold now
		}
		else
		{
			ResumeBehaviour();
		}
	}
	UE_LOG(LogRPGStagger, Log, TEXT("%s: stance break over (%d critical hits), resume behaviour %d"), *GetOwner()->GetName(), CriticalHitCount, bResumeBehaviour);
}

bool URPGBossStagger::IsRiposteArmed() const
{
	const UWorld* World = GetWorld();
	return Phase == EPhase::Down && !bRiposteUsed && World && World->GetTimeSeconds() <= RiposteArmedUntil;
}

const TCHAR* URPGBossStagger::CheckRiposte(const AActor* Player, double& OutDistance) const
{
	const AActor* Boss = GetOwner();
	OutDistance = 0.0;
	if (!GetWorld() || !Boss || !Player)
	{
		return TEXT("no boss or player");
	}
	if (Phase != EPhase::Down)
	{
		return TEXT("boss is not down");
	}
	if (bClipMode && ClipStage == EClipStage::Fall)
	{
		return TEXT("boss is still falling"); // the paired clips are made for the kneel: the interaction (and the HUD prompt) opens when the fall clip is over
	}
	if (bRiposteUsed)
	{
		return TEXT("riposte already used in this stance break");
	}
	double PlayerHealth = 1.0;
	if (ReadAttribute(Player, HealthTag, false, PlayerHealth) && PlayerHealth <= 0.0)
	{
		return TEXT("player is dead");
	}
	OutDistance = ((Player->GetActorLocation() - Boss->GetActorLocation()) * FVector(1.f, 1.f, 0.f)).Size();
	return RPGBossMath::RiposteReason(RPGBossMath::RiposteGeometry(Boss->GetActorLocation(), Boss->GetActorForwardVector(), Player->GetActorLocation(), Player->GetActorForwardVector(), RiposteRange, RiposteConeDegrees, RiposteFacingDegrees));
}

bool URPGBossStagger::IsRiposteAvailable(const AActor* Player) const
{
	double Distance = 0.0;
	return CheckRiposte(Player, Distance) == nullptr;
}

bool URPGBossStagger::TryRiposte(const AActor* Player)
{
	double Distance = 0.0;
	if (const TCHAR* Reason = CheckRiposte(Player, Distance))
	{
		++RiposteRejectCount;
		LastRiposteResult = Reason;
		UE_LOG(LogRPGStagger, Log, TEXT("riposte rejected: %s"), Reason);
		return false;
	}
	LastRiposteResult = TEXT("accepted");
	if (bUseRiposteClips && BeginRiposteExecution(Player))
	{
		UE_LOG(LogRPGStagger, Log, TEXT("riposte accepted at %.0f cm: the paired clips play, the critical hit (x%.1f) lands once at the impact"), Distance, CriticalMultiplier);
		return true;
	}
	RiposteArmedUntil = GetWorld()->GetTimeSeconds() + RiposteArmSeconds;
	UE_LOG(LogRPGStagger, Log, TEXT("riposte accepted at %.0f cm, the next hit within %.1f s is critical x%.1f"), Distance, RiposteArmSeconds, CriticalMultiplier);
	return true;
}

bool URPGBossStagger::BeginRiposteExecution(const AActor* PlayerActor)
{
	ACharacter* Player = Cast<ACharacter>(const_cast<AActor*>(PlayerActor));
	const ACharacter* Boss = Cast<ACharacter>(GetOwner());
	if (!Player || !Boss || !GetWorld() || !bClipMode || bRiposteRunning || ClipStage != EClipStage::Down)
	{
		return false; // the paired clips are made for the kneel of the stance break clips
	}
	LoadedRipostePlayer = RipostePlayerClip.LoadSynchronous();
	LoadedRiposteBoss = RiposteBossClip.LoadSynchronous();
	if (!LoadedRipostePlayer || !LoadedRiposteBoss)
	{
		return false;
	}
	RipostePlayer = Player;
	bRiposteRunning = true;
	bRiposteStarted = false;
	bRiposteImpactDone = false;
	bRiposteUsed = true; // once per stance break; further presses are rejected from now on
	GetWorld()->GetTimerManager().SetTimerForNextTick(FTimerDelegate::CreateUObject(this, &URPGBossStagger::StartRiposteClips));
	return true;
}

void URPGBossStagger::StartRiposteClips()
{
	ACharacter* Player = RipostePlayer.Get();
	ACharacter* Boss = Cast<ACharacter>(GetOwner());
	if (!bRiposteRunning || !Player || !Boss || Phase != EPhase::Down)
	{
		EndRiposteExecution(false, TEXT("could not start"), true);
		return;
	}
	const double Now = GetWorld()->GetTimeSeconds();
	// Lock the player: no input, no movement; the pack's own attack that the same press started is cut before its trace window opens.
	if (APlayerController* Controller = Cast<APlayerController>(Player->GetController()))
	{
		Player->DisableInput(Controller);
	}
	if (UCharacterMovementComponent* Movement = Player->GetCharacterMovement())
	{
		Movement->StopMovementImmediately();
	}
	if (UAnimInstance* PlayerAnim = Player->GetMesh() ? Player->GetMesh()->GetAnimInstance() : nullptr)
	{
		PlayerAnim->Montage_Stop(0.f);
	}
	// The strike ends 60 cm from the boss's centre, inside its capsule (radius ~63 cm, the player's 42): while the clips run the two capsules ignore each other, so the clip's own root motion is not stopped by the contact.
	if (UCapsuleComponent* PlayerCapsule = Player->GetCapsuleComponent())
	{
		PlayerCapsule->IgnoreActorWhenMoving(Boss, true);
		bRiposteIgnoring = true;
	}
	if (UCapsuleComponent* BossCapsule = Boss->GetCapsuleComponent())
	{
		BossCapsule->IgnoreActorWhenMoving(Player, true);
	}
	// Alignment: the player faces the boss and slides to the clip's start distance along the line from the boss (the clip then travels 90 cm by its root motion).
	const FVector BossLocation = Boss->GetActorLocation();
	FVector ToPlayer = (Player->GetActorLocation() - BossLocation) * FVector(1.f, 1.f, 0.f);
	ToPlayer = ToPlayer.IsNearlyZero() ? Boss->GetActorForwardVector() : ToPlayer.GetSafeNormal();
	RiposteAlignDone = 0.f;
	RiposteAlignFrom = Player->GetActorLocation();
	RiposteAlignTo = FVector(BossLocation.X + ToPlayer.X * RipostePlayerStartGap, BossLocation.Y + ToPlayer.Y * RipostePlayerStartGap, RiposteAlignFrom.Z);
	if (UWorld* World = GetWorld())
	{
		if (const UCapsuleComponent* Capsule = Player->GetCapsuleComponent())
		{
			// The slide back must not push the capsule through a wall or a pillar: it stops just short of what is in the way.
			FHitResult Hit;
			FCollisionQueryParams Params(SCENE_QUERY_STAT(RiposteAlign), false, Player);
			Params.AddIgnoredActor(Boss);
			if (World->SweepSingleByChannel(Hit, RiposteAlignFrom, RiposteAlignTo, FQuat::Identity, ECC_WorldStatic, FCollisionShape::MakeCapsule(Capsule->GetScaledCapsuleRadius(), Capsule->GetScaledCapsuleHalfHeight()), Params))
			{
				RiposteAlignTo = RiposteAlignFrom + (RiposteAlignTo - RiposteAlignFrom) * FMath::Max(0.f, Hit.Time - 0.02f);
			}
		}
	}
	const float FaceYaw = (-ToPlayer).Rotation().Yaw;
	Player->SetActorRotation(FRotator(0.f, FaceYaw, 0.f));
	if (APlayerController* Controller = Cast<APlayerController>(Player->GetController()))
	{
		Controller->SetControlRotation(FRotator(0.f, FaceYaw, 0.f));
	}
	// The paired clips.
	RipostePlayerMontage = RPGBossClips::Play(Player, LoadedRipostePlayer, 0.05f, 0.2f);
	UAnimMontage* BossMontage = RPGBossClips::Play(Boss, LoadedRiposteBoss, 0.1f, 0.f); // no blend out: the kneel loop takes over at the last frame, the same pose
	if (!RipostePlayerMontage.IsValid() || !BossMontage)
	{
		EndRiposteExecution(false, TEXT("a clip did not play"), true);
		return;
	}
	ClipMontage = BossMontage;
	ClipStage = EClipStage::Riposte;
	bRiposteStarted = true;
	RiposteStartTime = Now;
	RiposteEndTime = Now + FMath::Max(LoadedRipostePlayer->GetPlayLength(), LoadedRiposteBoss->GetPlayLength()) - 0.03;
}

void URPGBossStagger::TickRiposte(double Now)
{
	if (!bRiposteStarted)
	{
		return; // the start is one frame away
	}
	ACharacter* Player = RipostePlayer.Get();
	if (!Player)
	{
		EndRiposteExecution(false, TEXT("the player is gone"), true);
		return;
	}
	double PlayerHealth = 1.0;
	if (ReadAttribute(Player, HealthTag, false, PlayerHealth) && PlayerHealth <= 0.0)
	{
		EndRiposteExecution(false, TEXT("the player died"), true);
		return;
	}
	const double T = Now - RiposteStartTime;
	if (RiposteAlignDone < 1.f)
	{
		// The slide is added to the clip's own root motion (a delta per frame, never an absolute position: that would throw the root motion of the first 0.3 s away).
		const float Alpha = FMath::Clamp(static_cast<float>(T / RiposteAlignSeconds), 0.f, 1.f);
		if (Alpha > RiposteAlignDone)
		{
			Player->AddActorWorldOffset((RiposteAlignTo - RiposteAlignFrom) * (Alpha - RiposteAlignDone), false, nullptr, ETeleportType::TeleportPhysics);
			RiposteAlignDone = Alpha;
		}
	}
	if (!bRiposteImpactDone && T >= RiposteImpactSeconds)
	{
		ApplyRiposteImpact();
	}
	if (Now >= RiposteEndTime)
	{
		EndRiposteExecution(true, TEXT("clips over"));
	}
}

void URPGBossStagger::TickRiposteExit(double Now)
{
	ACharacter* Player = RipostePlayer.Get();
	const double Alpha = FMath::Clamp((Now - RiposteExitStart) / 0.25, 0.0, 1.0);
	if (!Player || Alpha >= 1.0)
	{
		if (Player)
		{
			Player->SetActorLocation(RiposteExitTo, false, nullptr, ETeleportType::TeleportPhysics);
		}
		bRiposteExiting = false;
		return;
	}
	Player->SetActorLocation(FMath::Lerp(RiposteExitFrom, RiposteExitTo, static_cast<float>(Alpha)), false, nullptr, ETeleportType::TeleportPhysics);
}

void URPGBossStagger::ApplyRiposteImpact()
{
	bRiposteImpactDone = true;
	double Health = 0.0;
	if (!ReadAttribute(GetOwner(), HealthTag, false, Health) || Health <= 0.0)
	{
		return;
	}
	// One designated damage event at the impact frame: the critical multiplier applies to the base hit once (Freeze 17.4). The baseline moves with it so ApplyCritical sees no second loss.
	const double Damage = RiposteBaseDamage * CriticalMultiplier;
	const double NewHealth = FMath::Max(0.0, Health - Damage);
	WriteAttribute(GetOwner(), HealthTag, NewHealth);
	LastHealth = NewHealth;
	if (NewHealth <= 0.0)
	{
		TryActivateByTag(GetOwner(), TEXT("Ability.Dead"), true); // writing the attribute alone does not start the pack's death ability (as DebugKillBoss)
	}
	++RiposteCount;
	++CriticalHitCount;
	++RiposteImpacts;
	RiposteArmedUntil = -1.0;
	UE_LOG(LogRPGStagger, Log, TEXT("riposte impact: %.0f x %.1f = %.0f damage, health %.0f -> %.0f (impact %d)"), RiposteBaseDamage, CriticalMultiplier, Damage, Health, NewHealth, RiposteImpacts);
}

void URPGBossStagger::EndRiposteExecution(bool bCompleted, const TCHAR* Why, bool bResumeKneel)
{
	if (!bRiposteRunning)
	{
		return;
	}
	bRiposteRunning = false;
	const bool bWasStarted = bRiposteStarted;
	bRiposteStarted = false;
	ACharacter* Player = RipostePlayer.Get();
	if (Player)
	{
		UAnimInstance* PlayerAnim = Player->GetMesh() ? Player->GetMesh()->GetAnimInstance() : nullptr;
		if (!bCompleted && PlayerAnim && RipostePlayerMontage.IsValid())
		{
			PlayerAnim->Montage_Stop(0.1f, RipostePlayerMontage.Get());
		}
		double BossHealth = 1.0;
		const bool bBossAlive = !ReadAttribute(GetOwner(), HealthTag, false, BossHealth) || BossHealth > 0.0;
		double PlayerHealth = 1.0;
		const bool bPlayerAlive = !ReadAttribute(Player, HealthTag, false, PlayerHealth) || PlayerHealth > 0.0;
		// The player's input comes back when both live; after the boss's death the HUD's victory lock owns it, after the player's death the reset does.
		if (bBossAlive && bPlayerAlive)
		{
			if (APlayerController* Controller = Cast<APlayerController>(Player->GetController()))
			{
				Player->EnableInput(Controller);
			}
		}
	}
	if (bRiposteIgnoring)
	{
		bRiposteIgnoring = false;
		ACharacter* Boss = Cast<ACharacter>(GetOwner());
		if (Player && Boss && Player->GetCapsuleComponent() && Boss->GetCapsuleComponent())
		{
			Player->GetCapsuleComponent()->IgnoreActorWhenMoving(Boss, false);
			Boss->GetCapsuleComponent()->IgnoreActorWhenMoving(Player, false);
			// Slide the player out to the capsules' contact distance (plus 3 cm) along the line from the boss, so the movement component does not push him out in one frame.
			const FVector BossLocation = Boss->GetActorLocation();
			FVector Out = (Player->GetActorLocation() - BossLocation) * FVector(1.f, 1.f, 0.f);
			const float Contact = Boss->GetCapsuleComponent()->GetScaledCapsuleRadius() + Player->GetCapsuleComponent()->GetScaledCapsuleRadius() + 3.f;
			if (Out.Size() < Contact && GetWorld())
			{
				Out = Out.IsNearlyZero() ? Boss->GetActorForwardVector() : Out.GetSafeNormal();
				RiposteExitFrom = Player->GetActorLocation();
				RiposteExitTo = FVector(BossLocation.X + Out.X * Contact, BossLocation.Y + Out.Y * Contact, RiposteExitFrom.Z);
				FHitResult Hit;
				FCollisionQueryParams Params(SCENE_QUERY_STAT(RiposteExit), false, Player);
				Params.AddIgnoredActor(Boss);
				if (GetWorld()->SweepSingleByChannel(Hit, RiposteExitFrom, RiposteExitTo, FQuat::Identity, ECC_WorldStatic, FCollisionShape::MakeCapsule(Player->GetCapsuleComponent()->GetScaledCapsuleRadius(), Player->GetCapsuleComponent()->GetScaledCapsuleHalfHeight()), Params))
				{
					RiposteExitTo = RiposteExitFrom + (RiposteExitTo - RiposteExitFrom) * FMath::Max(0.f, Hit.Time - 0.02f);
				}
				RiposteExitStart = GetWorld()->GetTimeSeconds();
				bRiposteExiting = true;
			}
		}
	}
	if (!bCompleted)
	{
		++RiposteAborts;
	}
	if (!bCompleted && bResumeKneel && !bRiposteImpactDone)
	{
		bRiposteUsed = false; // aborted before the impact by something on the player's side: the stance break keeps its riposte
	}
	if ((bCompleted || bResumeKneel) && Phase == EPhase::Down && bClipMode && LoadedDown)
	{
		ClipMontage = RPGBossClips::Play(Cast<ACharacter>(GetOwner()), LoadedDown, 0.f, 0.15f, 1.f, 40); // the reaction's last frame is the kneel's first frame
		ClipStage = EClipStage::Down;
	}
	UE_LOG(LogRPGStagger, Log, TEXT("%s: riposte execution over (%s, %s, started %d, impacts %d)"), *GetOwner()->GetName(), bCompleted ? TEXT("completed") : TEXT("aborted"), Why, bWasStarted ? 1 : 0, RiposteImpacts);
}

FString URPGBossStagger::ForceBreakForTest()
{
	bWasActive = true; // the pack's hit stun edge must not be read as a second request
	return RPGBossRules::Name(RequestBreak(true));
}

FString URPGBossStagger::TryBreakForTest()
{
	bWasActive = true;
	return RPGBossRules::Name(RequestBreak(false));
}

void URPGBossStagger::AbortStagger()
{
	// A reset leaves nothing behind (Freeze 18.3 line 791): the cooldown, the riposte and the posture hold go in every case, also when no break is running.
	CooldownEnd = 0.0;
	RiposteArmedUntil = -1.0;
	bRiposteUsed = false;
	if (Phase != EPhase::Idle)
	{
		StopStaggerMontages(0.1f);
		EndStagger(false, true);
		bBehaviourHeld = false; // the caller decides what the behaviour does next
	}
	if (URPGBossPosture* Posture = GetOwner()->FindComponentByClass<URPGBossPosture>())
	{
		Posture->EndHold(true);
	}
}

void URPGBossStagger::EndPlay(const EEndPlayReason::Type EndPlayReason)
{
	Phase = EPhase::Idle;
	Super::EndPlay(EndPlayReason);
}

void URPGBossStagger::AcknowledgeHealthLoss(double Loss)
{
	if (LastHealth >= 0.0)
	{
		LastHealth = FMath::Max(0.0, LastHealth - Loss);
	}
}

void URPGBossStagger::ApplyCritical()
{
	double Health = 0.0;
	if (!ReadAttribute(GetOwner(), HealthTag, false, Health))
	{
		return;
	}
	if (Health <= 0.0)
	{
		UE_LOG(LogRPGStagger, Log, TEXT("%s: died during the stance break"), *GetOwner()->GetName());
		StopStaggerMontages(0.1f); // only the stance break's own montages: a plain Montage_Stop() would also stop the pack's death clip
		EndStagger(false);
		return;
	}
	if (LastHealth >= 0.0 && Health > LastHealth + 1.0)
	{
		// Health went up while the boss was down: the pack reset the encounter (the player died and respawned). Stand the boss up and hand it back to its behaviour.
		UE_LOG(LogRPGStagger, Log, TEXT("%s: health rose %.0f -> %.0f during the stance break (encounter reset), ending it"), *GetOwner()->GetName(), LastHealth, Health);
		StopStaggerMontages(0.2f);
		LastHealth = Health;
		EndStagger(true);
		return;
	}
	if (!bCriticalOnEveryHit && IsRiposteArmed() && LastHealth >= 0.0 && Health < LastHealth - 0.01)
	{
		// The riposte hit (Freeze 17.4): the multiplier applies to this hit only, once per stance break.
		const double Loss = LastHealth - Health;
		const double NewHealth = FMath::Max(0.0, Health - Loss * (CriticalMultiplier - 1.0));
		WriteAttribute(GetOwner(), HealthTag, NewHealth);
		if (NewHealth <= 0.0)
		{
			TryActivateByTag(GetOwner(), TEXT("Ability.Dead"), true); // the bonus can take the last health: writing the attribute alone does not start the pack's death ability (review D)
		}
		bRiposteUsed = true;
		RiposteArmedUntil = -1.0;
		++RiposteCount;
		++CriticalHitCount;
		UE_LOG(LogRPGStagger, Log, TEXT("riposte hit: lost %.0f, took %.0f in total (health %.0f -> %.0f)"), Loss, Loss + (Health - NewHealth), LastHealth, NewHealth);
		Health = NewHealth;
	}
	if (bCriticalOnEveryHit && Phase == EPhase::Down && LastHealth >= 0.0 && Health < LastHealth - 0.01)
	{
		const double Loss = LastHealth - Health;
		const double NewHealth = FMath::Max(0.0, Health - Loss * (CriticalMultiplier - 1.0));
		WriteAttribute(GetOwner(), HealthTag, NewHealth);
		if (NewHealth <= 0.0)
		{
			TryActivateByTag(GetOwner(), TEXT("Ability.Dead"), true); // as above
		}
		++CriticalHitCount;
		UE_LOG(LogRPGStagger, Log, TEXT("critical hit: lost %.0f, took %.0f in total (health %.0f -> %.0f)"), Loss, Loss + (Health - NewHealth), LastHealth, NewHealth);
		Health = NewHealth;
	}
	LastHealth = Health;
}

void URPGBossStagger::HoldBehaviour()
{
	const APawn* Pawn = Cast<APawn>(GetOwner());
	AAIController* Controller = Pawn ? Cast<AAIController>(Pawn->GetController()) : nullptr;
	if (!Controller)
	{
		return;
	}
	if (UObject* Manager = FindControllerComponent(Controller, TEXT("BP_BehaviorManagerComponent_C")))
	{
		CallBlueprintFunction(Manager, TEXT("StopBehaviorLogic"),
			[](UFunction& F, uint8* P)
			{
				if (const FStrProperty* Reason = CastField<FStrProperty>(F.FindPropertyByName(TEXT("Reason"))))
				{
					Reason->SetPropertyValue_InContainer(P, FString(TEXT("Stance break")));
				}
			},
			[](UFunction&, uint8*) {});
	}
	else if (Controller->BrainComponent)
	{
		Controller->BrainComponent->StopLogic(TEXT("Stance break"));
	}
	bBehaviourHeld = true;
}

void URPGBossStagger::ResumeBehaviour()
{
	const APawn* Pawn = Cast<APawn>(GetOwner());
	AAIController* Controller = Pawn ? Cast<AAIController>(Pawn->GetController()) : nullptr;
	if (!Controller || !bBehaviourHeld)
	{
		return;
	}
	// A scripted test keeps the boss frozen for its whole length (URPGBossEncounter::bTestFreeze): a break ending must not restart the pack's behaviour behind it,
	// or the boss can start an attack in the frames before the encounter component stops the logic again.
	const URPGBossEncounter* Encounter = GetOwner()->FindComponentByClass<URPGBossEncounter>();
	if (Encounter && Encounter->bTestFreeze && !Encounter->IsDormant())
	{
		bBehaviourHeld = false;
		return;
	}
	if (UObject* Manager = FindControllerComponent(Controller, TEXT("BP_BehaviorManagerComponent_C")))
	{
		CallBlueprintFunction(Manager, TEXT("SetBehaviorDisabled"),
			[](UFunction& F, uint8* P)
			{
				for (TFieldIterator<FBoolProperty> It(&F); It; ++It)
				{
					if (!It->HasAnyPropertyFlags(CPF_OutParm))
					{
						It->SetPropertyValue_InContainer(P, false);
						break;
					}
				}
			},
			[](UFunction&, uint8*) {});
	}
	if (Controller->BrainComponent)
	{
		Controller->BrainComponent->RestartLogic();
	}
	bBehaviourHeld = false;
}
