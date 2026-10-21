// Copyright One Boss Fight. All Rights Reserved.

#include "Player/RPGTraceAudit.h"
#include "Animation/AnimInstance.h"
#include "Animation/AnimMontage.h"
#include "Components/CapsuleComponent.h"
#include "Components/SkeletalMeshComponent.h"
#include "Engine/World.h"
#include "GameFramework/Character.h"
#include "Kismet/GameplayStatics.h"
#include "Pack/RPGBlueprintCall.h"
#include "Player/RPGAttackTracker.h"
#include "Player/RPGBossDamage.h"
#include "Player/RPGBossEncounter.h"
#include "Player/RPGBossPhases.h"
#include "Player/RPGBossStagger.h"
#include "Player/RPGTraceGuard.h"

DEFINE_LOG_CATEGORY_STATIC(LogRPGTraceAudit, Log, All);

using namespace RPGPack;

URPGTraceAudit::URPGTraceAudit()
{
	PrimaryComponentTick.bCanEverTick = true;
	PrimaryComponentTick.TickGroup = TG_PostUpdateWork; // after the pack's sample of the frame
}

void URPGTraceAudit::BeginPlay()
{
	Super::BeginPlay();
	ResetCounters();
}

void URPGTraceAudit::ResetCounters()
{
	Windows.Reset();
	Totals.Reset();
	Instances.Reset();
	Previous.Reset();
	PrevSet.Reset();
	bActive = false;
	bPending = false;
	bInterrupted = false;
	OrdinalBase = 0;
}

void URPGTraceAudit::Bump(FName Name, double Amount)
{
	Totals.FindOrAdd(Name) += Amount;
	if (FWindow* W = Current())
	{
		if (bActive)
		{
			W->C.FindOrAdd(Name) += Amount;
		}
	}
}

void URPGTraceAudit::Peak(FName Name, double Value)
{
	double& Total = Totals.FindOrAdd(Name);
	Total = FMath::Max(Total, Value);
	if (FWindow* W = Current())
	{
		if (bActive)
		{
			double& Local = W->C.FindOrAdd(Name);
			Local = FMath::Max(Local, Value);
		}
	}
}

double URPGTraceAudit::Get(const TMap<FName, double>& Map, FName Name) const
{
	const double* Value = Map.Find(Name);
	return Value ? *Value : 0.0;
}

double URPGTraceAudit::GetCounter(FName Name) const
{
	return Get(Totals, Name);
}

double URPGTraceAudit::GetWindowCounter(int32 Ordinal, FName Name) const
{
	const int32 Index = Ordinal < 0 ? Windows.Num() + Ordinal : Ordinal - 1;
	return Windows.IsValidIndex(Index) ? Get(Windows[Index].C, Name) : -1.0;
}

double URPGTraceAudit::GetInstanceCounter(int32 Instance, FName Name) const
{
	const TMap<FName, double>* Map = Instances.Find(Instance);
	return Map ? Get(*Map, Name) : 0.0;
}

FString URPGTraceAudit::GetWindowSummary(int32 Ordinal) const
{
	const int32 Index = Ordinal < 0 ? Windows.Num() + Ordinal : Ordinal - 1;
	if (!Windows.IsValidIndex(Index))
	{
		return FString();
	}
	const FWindow& W = Windows[Index];
	return FString::Printf(TEXT("window %d %s instance %d: samples %.0f overlap %.0f inserted %.0f accepted %.0f (%.1f) rejected %.0f/%.0f peak step %.0f cm closed: %s at %.2f s after-interrupt %.0f"), W.Ordinal, *W.Move.ToString(), W.Instance,
		Get(W.C, TEXT("Samples")), Get(W.C, TEXT("OverlapSamples")), Get(W.C, TEXT("SetInsertions")), Get(W.C, TEXT("DamageAccepted")), Get(W.C, TEXT("DamageTaken")), Get(W.C, TEXT("RejectedInvulnerable")), Get(W.C, TEXT("RejectedOther")),
		Get(W.C, TEXT("PeakStepCm")), *W.CloseReason, W.ClosePos, Get(W.C, TEXT("SamplesAfterInterrupt")));
}

TArray<FString> URPGTraceAudit::BuildLines() const
{
	TArray<FString> Lines;
	const FWindow* W = Windows.Num() > 0 ? &Windows.Last() : nullptr;
	Lines.Add(FString::Printf(TEXT("  trace %s %s window %d of %d  sockets %.0f  radius %.0f+%.0f  hit set %d  ability %s"), bActive ? TEXT("ACTIVE") : TEXT("idle"), W ? *W->Move.ToString() : TEXT("-"), W ? W->Ordinal : 0, Windows.Num(),
		GetCounter(TEXT("Sockets")), GetCounter(TEXT("BaseRadius")), GetCounter(TEXT("Modifier")), GetHitSetCount(), GetCounter(TEXT("WindowsNoAbility")) > 0 ? TEXT("no") : TEXT("yes")));
	Lines.Add(FString::Printf(TEXT("  trace overlap samples %.0f | new in hit set %.0f | damage accepted %.0f (%.1f) | rejected: invulnerable %.0f, other %.0f | blocked by wall %d"), GetCounter(TEXT("OverlapSamples")), GetCounter(TEXT("SetInsertions")),
		GetCounter(TEXT("DamageAccepted")), GetCounter(TEXT("DamageTaken")), GetCounter(TEXT("RejectedInvulnerable")), GetCounter(TEXT("RejectedOther")),
		(GetOwner() && GetOwner()->FindComponentByClass<URPGTraceGuard>()) ? GetOwner()->FindComponentByClass<URPGTraceGuard>()->GetOccludedSampleCount() : 0));
	Lines.Add(FString::Printf(TEXT("  sweep peak step %.0f cm (capsule radius 42)  continuity %.1f cm  suspect %.0f  after-interrupt samples %.0f  last close: %s"), GetCounter(TEXT("PeakStepCm")), GetCounter(TEXT("MaxContinuityErrorCm")), GetCounter(TEXT("SuspectSweeps")),
		GetCounter(TEXT("SamplesAfterInterrupt")), *LastCloseText));
	return Lines;
}

void URPGTraceAudit::Close(const TCHAR* Reason)
{
	if (FWindow* W = Current())
	{
		W->CloseReason = Reason;
		const URPGAttackTracker* Tracker = GetOwner()->FindComponentByClass<URPGAttackTracker>();
		W->ClosePos = 0.f;
		if (const ACharacter* Character = Cast<ACharacter>(GetOwner()))
		{
			if (const UAnimInstance* Anim = Character->GetMesh() ? Character->GetMesh()->GetAnimInstance() : nullptr)
			{
				if (const UAnimMontage* Montage = Anim->GetCurrentActiveMontage())
				{
					W->ClosePos = Anim->Montage_GetPosition(Montage);
				}
			}
		}
		(void)Tracker;
		W->C.Add(TEXT("ClosePos"), W->ClosePos);
		LastCloseText = FString::Printf(TEXT("%s at %.2f s"), Reason, W->ClosePos);
		UE_LOG(LogRPGTraceAudit, Log, TEXT("trace window close (%s): %s"), Reason, *GetWindowSummary(W->Ordinal));
	}
	bActive = false;
	bPending = false;
	bInterrupted = false;
}

void URPGTraceAudit::TickComponent(float DeltaTime, ELevelTick TickType, FActorComponentTickFunction* ThisTickFunction)
{
	Super::TickComponent(DeltaTime, TickType, ThisTickFunction);
#if !UE_BUILD_SHIPPING
	AActor* Boss = GetOwner();
	UWorld* World = GetWorld();
	if (!bEnabled || !Boss || !World || !Target.Resolve(Boss, TargetTypeTag))
	{
		return;
	}
	const bool bNow = Target.IsActive();
	const ACharacter* Character = Cast<ACharacter>(Boss);
	const UAnimInstance* Anim = Character && Character->GetMesh() ? Character->GetMesh()->GetAnimInstance() : nullptr;
	const UAnimMontage* Montage = Anim ? Anim->GetCurrentActiveMontage() : nullptr;
	const URPGAttackTracker* Tracker = Boss->FindComponentByClass<URPGAttackTracker>();
	const URPGBossEncounter* Encounter = Boss->FindComponentByClass<URPGBossEncounter>();
	const int32 Generation = Encounter ? Encounter->GetGeneration() : 0;
	APawn* Player = UGameplayStatics::GetPlayerPawn(this, 0);
	double PlayerHealth = 0.0;
	const bool bHealthKnown = Player && ReadAttribute(Player, TEXT("Attribute.Health"), false, PlayerHealth);
	const double Now = World->GetTimeSeconds();

	// Health drops with no insertion waiting are not the trace's (a javelin, a wave, a test).
	if (bHealthKnown && LastPlayerHealth >= 0.0 && PlayerHealth < LastPlayerHealth - 0.001 && !bPending)
	{
		Totals.FindOrAdd(TEXT("UnattributedDamage")) += LastPlayerHealth - PlayerHealth;
		if (bInterrupted)
		{
			Bump(TEXT("DamageAfterInterrupt"), 1.0);
		}
	}

	if (bNow && !bActive)
	{
		// Open edge.
		bActive = true;
		bInterrupted = false;
		FWindow W;
		W.Ordinal = ++OrdinalBase;
		W.Instance = (Tracker && Tracker->GetCurrentMove() != NAME_None) ? Tracker->GetAttackInstance() : -1;
		W.Move = Tracker && Tracker->GetCurrentMove() != NAME_None ? Tracker->GetCurrentMove() : FName(TEXT("pack"));
		W.Generation = Generation;
		W.Montage = Montage ? Montage->GetName() : FString(TEXT("none"));
		W.OpenPos = (Anim && Montage) ? Anim->Montage_GetPosition(Montage) : 0.f;
		W.C.Add(TEXT("OpenPos"), W.OpenPos);
		Windows.Add(W);
		while (Windows.Num() > 64)
		{
			Windows.RemoveAt(0);
		}
		WindowMontage = W.Montage;
		WindowGeneration = Generation;
		LastMove = W.Move;
		Bump(TEXT("Windows"));
		TArray<FName> Sockets;
		Target.GetSockets(Sockets);
		Totals.FindOrAdd(TEXT("Sockets")) = Sockets.Num();
		Totals.FindOrAdd(TEXT("BaseRadius")) = Target.GetBaseRadius();
		Totals.FindOrAdd(TEXT("Modifier")) = Target.GetRadiusModifier();
		if (W.Instance < 0)
		{
			Bump(TEXT("WindowsOutsideTracker"));
		}
		if (!Target.HasAbility())
		{
			Bump(TEXT("WindowsNoAbility"));
		}
		if (const UPrimitiveComponent* Mesh = Target.GetMesh())
		{
			Previous.Reset();
			for (const FName& Socket : Sockets)
			{
				Previous.Add(Socket, Mesh->GetSocketLocation(Socket));
				FVector Stored;
				if (Target.GetStoredLocation(Socket, Stored))
				{
					Peak(TEXT("OpenRefreshErrorCm"), FVector::Dist(Stored, Mesh->GetSocketLocation(Socket)));
				}
			}
			if (Mesh->GetAttachSocketName() == TEXT("HeavySwordSheath_Back"))
			{
				Bump(TEXT("WindowsWhileSheathed"));
			}
		}
		// This tick runs after the pack's sweep of the same frame, so a member of the hit set at the open edge may be a hit of the window's first sample: only what the guard carried over from the
		// previous window of the same swing is known not to be new.
		PrevSet.Reset();
		if (const URPGTraceGuard* OpenGuard = Boss->FindComponentByClass<URPGTraceGuard>())
		{
			for (const TWeakObjectPtr<AActor>& Carried : OpenGuard->GetCarriedAtOpen())
			{
				PrevSet.Add(Carried.Get());
			}
		}
		TArray<AActor*> Set;
		Target.GetHitSet(Set);
		UE_LOG(LogRPGTraceAudit, Log, TEXT("trace window open: %s instance %d window %d generation %d at %.2f s, montage %s, radius %.0f+%.0f, sockets %d, ability %d, hit set %d"), *W.Move.ToString(), W.Instance, W.Ordinal, Generation, W.OpenPos, *W.Montage,
			Target.GetBaseRadius(), Target.GetRadiusModifier(), Sockets.Num(), Target.HasAbility() ? 1 : 0, Set.Num());
	}

	if (bActive && bNow)
	{
		// One sample (the pack has just run its sweep this frame).
		Bump(TEXT("Samples"));
		Peak(TEXT("MaxDt"), DeltaTime);
		double& MinDt = Totals.FindOrAdd(TEXT("MinDt"));
		MinDt = MinDt == 0.0 ? DeltaTime : FMath::Min(MinDt, static_cast<double>(DeltaTime));
		const UPrimitiveComponent* Mesh = Target.GetMesh();
		TArray<FName> Sockets;
		Target.GetSockets(Sockets);
		const double Radius = Target.GetBaseRadius() + Target.GetRadiusModifier();
		bool bOverlap = false;
		TArray<TEnumAsByte<ECollisionChannel>> Channels;
		Target.GetObjectChannels(Channels);
		TArray<AActor*> Ignore;
		Target.GetActorsToIgnore(Ignore);
		if (Mesh)
		{
			for (const FName& Socket : Sockets)
			{
				const FVector Cur = Mesh->GetSocketLocation(Socket);
				const FVector* Prev = Previous.Find(Socket);
				if (Prev)
				{
					const double Step = FVector::Dist(Cur, *Prev);
					Peak(TEXT("PeakStepCm"), Step);
					Peak(TEXT("PeakSpeedCmPerSec"), DeltaTime > KINDA_SMALL_NUMBER ? Step / DeltaTime : 0.0);
					if (Step > SuspectStepCm)
					{
						Bump(TEXT("SuspectSweeps"));
						UE_LOG(LogRPGTraceAudit, Warning, TEXT("suspect sweep: socket %s moved %.0f cm in one sample"), *Socket.ToString(), Step);
					}
					if (Player && Channels.Num() > 0)
					{
						FCollisionObjectQueryParams Objects;
						for (const TEnumAsByte<ECollisionChannel>& Channel : Channels)
						{
							Objects.AddObjectTypesToQuery(Channel);
						}
						FCollisionQueryParams Params(SCENE_QUERY_STAT(RPGTraceAuditSweep), false);
						Params.AddIgnoredActors(Ignore);
						Params.AddIgnoredActor(Boss);
						TArray<FHitResult> Hits;
						World->SweepMultiByObjectType(Hits, Cur, *Prev, FQuat::Identity, Objects, FCollisionShape::MakeSphere(static_cast<float>(Radius)), Params);
						for (const FHitResult& Hit : Hits)
						{
							bOverlap |= Hit.GetActor() == Player;
						}
					}
				}
				FVector Stored;
				if (Target.GetStoredLocation(Socket, Stored))
				{
					Peak(TEXT("MaxContinuityErrorCm"), FVector::Dist(Stored, Cur));
				}
				Previous.Add(Socket, Cur);
			}
		}
		if (bOverlap)
		{
			Bump(TEXT("OverlapSamples"));
		}

		// Hit set: new members.
		TArray<AActor*> Set;
		Target.GetHitSet(Set);
		for (AActor* Actor : Set)
		{
			if (PrevSet.Contains(Actor))
			{
				continue;
			}
			if (Actor == Boss)
			{
				Bump(TEXT("SelfInSet"));
			}
			else if (Actor == Player && Player)
			{
				const URPGTraceGuard* Guard = Boss->FindComponentByClass<URPGTraceGuard>();
				if (Guard && Guard->IsSeed(Player))
				{
					continue; // the wall gate's temporary seed, not a hit
				}
				Bump(TEXT("SetInsertions"));
				bPending = true;
				PendingTime = Now;
				PendingTicks = 0;
				PendingHealth = LastPlayerHealth >= 0.0 ? LastPlayerHealth : PlayerHealth;
				bPendingInvulnerable = RPGBossDamage::IsInvulnerable(Player);
			}
		}
		PrevSet.Reset();
		for (AActor* Actor : Set)
		{
			const URPGTraceGuard* SeedGuard = Boss->FindComponentByClass<URPGTraceGuard>();
			if (!(SeedGuard && SeedGuard->IsSeed(Actor)))
			{
				PrevSet.Add(Actor);
			}
		}

		// Outcome of the insertion.
		if (bPending)
		{
			++PendingTicks;
			if (bHealthKnown && PlayerHealth < PendingHealth - 0.001)
			{
				Bump(TEXT("DamageAccepted"));
				Bump(TEXT("DamageTaken"), PendingHealth - PlayerHealth);
				if (FWindow* W = Current())
				{
					TMap<FName, double>& I = Instances.FindOrAdd(W->Instance);
					I.FindOrAdd(TEXT("DamageAccepted")) += 1.0;
					I.FindOrAdd(TEXT("DamageTaken")) += PendingHealth - PlayerHealth;
				}
				bPending = false;
			}
			else if (Now - PendingTime >= ResolveWindowSeconds && PendingTicks >= 3)
			{
				Bump(bPendingInvulnerable ? TEXT("RejectedInvulnerable") : TEXT("RejectedOther"));
				bPending = false;
			}
		}
		if (FWindow* W = Current())
		{
			TMap<FName, double>& I = Instances.FindOrAdd(W->Instance);
			I.FindOrAdd(TEXT("Windows")) = Windows.Num() > 0 ? 1.0 : 0.0;
		}

		// Interrupt: the montage is no longer the window's, the boss died, the encounter is new, a stance break or a phase transition runs.
		const URPGBossStagger* Stagger = Boss->FindComponentByClass<URPGBossStagger>();
		const URPGBossPhases* Phases = Boss->FindComponentByClass<URPGBossPhases>();
		double BossHealth = 1.0;
		ReadAttribute(Boss, TEXT("Attribute.Health"), false, BossHealth);
		const bool bInterrupt = (Montage ? Montage->GetName() != WindowMontage : true) || BossHealth <= 0.0 || Generation != WindowGeneration || (Stagger && Stagger->IsStaggered()) || (Phases && Phases->IsInTransition());
		if (bInterrupt && !bInterrupted)
		{
			bInterrupted = true;
			InterruptFrame = GFrameCounter;
		}
		if (bInterrupted)
		{
			// A sample in the interrupt frame itself is tolerated: the pack may sample before the owner's code ran in the same frame.
			if (GFrameCounter > InterruptFrame)
			{
				Bump(TEXT("SamplesAfterInterrupt"));
			}
			Peak(TEXT("FramesToClose"), static_cast<double>(GFrameCounter - InterruptFrame));
		}
	}
	else if (!bNow && bActive)
	{
		// Close edge: classify.
		const URPGBossStagger* Stagger = Boss->FindComponentByClass<URPGBossStagger>();
		const URPGBossPhases* Phases = Boss->FindComponentByClass<URPGBossPhases>();
		double BossHealth = 1.0;
		ReadAttribute(Boss, TEXT("Attribute.Health"), false, BossHealth);
		const TCHAR* Reason = TEXT("notify end");
		if (BossHealth <= 0.0) { Reason = TEXT("boss dead"); }
		else if (Generation != WindowGeneration) { Reason = TEXT("reset"); }
		else if (Stagger && Stagger->IsStaggered()) { Reason = TEXT("stance break"); }
		else if (Phases && Phases->IsInTransition()) { Reason = TEXT("phase transition"); }
		else if (!Montage) { Reason = TEXT("montage stopped"); }
		else if (Montage->GetName() != WindowMontage) { Reason = TEXT("montage replaced"); }
		Close(Reason);
	}
	LastPlayerHealth = bHealthKnown ? PlayerHealth : -1.0;
#endif
}
