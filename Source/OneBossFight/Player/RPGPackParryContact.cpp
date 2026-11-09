// Copyright One Boss Fight. All Rights Reserved.

#include "Player/RPGPackParryContact.h"
#include "Animation/AnimInstance.h"
#include "Animation/AnimMontage.h"
#include "Components/SkeletalMeshComponent.h"
#include "Kismet/GameplayStatics.h"
#include "Pack/RPGBlueprintCall.h"
#include "Player/RPGBossEncounter.h"
#include "Player/RPGAttackTracker.h"
#include "Player/RPGPlayerParry.h"
#include "Player/RPGBossDamage.h"
#include "Player/RPGTraceGuard.h"

DEFINE_LOG_CATEGORY_STATIC(LogRPGPackParryContact, Log, All);

namespace
{
	const TCHAR* ParryGradeName(RPGParryGrade::EGrade Grade)
	{
		switch (Grade)
		{
		case RPGParryGrade::EGrade::Perfect: return TEXT("Perfect");
		case RPGParryGrade::EGrade::Good: return TEXT("Good");
		case RPGParryGrade::EGrade::Late: return TEXT("Late");
		default: return TEXT("None");
		}
	}
}

URPGPackParryContact::URPGPackParryContact()
{
	PrimaryComponentTick.bCanEverTick = true;
	PrimaryComponentTick.bStartWithTickEnabled = true;
	PrimaryComponentTick.TickGroup = TG_PostUpdateWork;
}

void URPGPackParryContact::BeginPlay()
{
	Super::BeginPlay();
	if (URPGAttackTracker* Tracker = GetOwner() ? GetOwner()->FindComponentByClass<URPGAttackTracker>() : nullptr)
	{
		AddTickPrerequisiteComponent(Tracker);
	}
	Target.Resolve(GetOwner());
}

bool URPGPackParryContact::ReadInvulnerabilityTag(AActor* Player, bool& bOutInvulnerable) const
{
	const FGameplayTag Tag = FGameplayTag::RequestGameplayTag(TEXT("Status.Invulnerable"), false);
	UFunction* HasTag = Player ? Player->FindFunction(TEXT("HasMatchingGameplayTag")) : nullptr;
	if (!Tag.IsValid() || !HasTag) return false;
	bool bRead = false;
	const bool bCalled = RPGPack::CallBlueprintFunction(Player, HasTag,
		[&Tag](UFunction& F, uint8* P) { RPGPack::SetTag(F, P, TEXT("TagToCheck"), Tag); },
		[&](UFunction& F, uint8* P)
		{
			for (TFieldIterator<FBoolProperty> It(&F); It; ++It)
			{
				if (It->HasAnyPropertyFlags(CPF_ReturnParm | CPF_OutParm))
				{
					bOutInvulnerable = It->GetPropertyValue_InContainer(P);
					bRead = true;
					break;
				}
			}
		});
	return bCalled && bRead;
}

FString URPGPackParryContact::CurrentAttackKey(AActor* Boss, const URPGAttackTracker* Tracker, double WorldTime) const
{
	const URPGBossEncounter* Encounter = Boss ? Boss->FindComponentByClass<URPGBossEncounter>() : nullptr;
	const uint64 Generation = Encounter ? Encounter->GetParticipantGeneration() : 0;
	const uint32 BossId = Boss ? Boss->GetUniqueID() : 0;
	const FName Move = Tracker ? Tracker->GetCurrentMove() : NAME_None;
	const int32 Instance = Tracker ? Tracker->GetAttackInstance() : 0;
	if (!Move.IsNone() && Instance > 0)
	{
		return RPGPackParry::BuildAttackKey(Generation, BossId, Move, Instance, NAME_None, 0.0);
	}
	USkeletalMeshComponent* Mesh = Boss ? Boss->FindComponentByClass<USkeletalMeshComponent>() : nullptr;
	UAnimInstance* Anim = Mesh ? Mesh->GetAnimInstance() : nullptr;
	UAnimMontage* Montage = Anim ? Anim->GetCurrentActiveMontage() : nullptr;
	if (!Anim || !Montage) return FString();
	const float Rate = Anim->Montage_GetPlayRate(Montage);
	const float Position = Anim->Montage_GetPosition(Montage);
	if (!FMath::IsFinite(Rate) || Rate <= SMALL_NUMBER || !FMath::IsFinite(Position)) return FString();
	const double StartWorld = WorldTime - static_cast<double>(Position / Rate);
	return RPGPackParry::BuildAttackKey(Generation, BossId, NAME_None, 0, Montage->GetFName(), StartWorld);
}

void URPGPackParryContact::ClearEncounterState(uint64 NewGeneration, AActor* NewPlayer)
{
	EncounterGeneration = NewGeneration;
	ObservedPlayer = NewPlayer;
	PreviousHitSet.Reset();
	Candidates.Reset();
	ObservedAttackKeys.Reset();
	bWasTraceActive = false;
	bHasPreviousParrySample = false;
	bPreviousParryWindowOpen = false;
	PreviousParryGrade = RPGParryGrade::EGrade::None;
}

void URPGPackParryContact::LogSkip(FName Reason, AActor* Hit, double WorldTime, const FString& Detail)
{
	const double* LastTime = LastSkipLogTimes.Find(Reason);
	if (LastTime && WorldTime - *LastTime < 1.0)
	{
		return;
	}
	LastSkipLogTimes.Add(Reason, WorldTime);
	UE_LOG(LogRPGPackParryContact, Display, TEXT("[PARRY] skip reason=%s hit=%s%s%s"), *Reason.ToString(), *GetNameSafe(Hit),
		Detail.IsEmpty() ? TEXT("") : TEXT(" detail="), Detail.IsEmpty() ? TEXT("") : *Detail);
}

void URPGPackParryContact::TickComponent(float DeltaTime, ELevelTick TickType, FActorComponentTickFunction* ThisTickFunction)
{
	Super::TickComponent(DeltaTime, TickType, ThisTickFunction);
	AActor* Boss = GetOwner();
	APawn* Player = UGameplayStatics::GetPlayerPawn(this, 0);
	const URPGBossEncounter* Encounter = Boss ? Boss->FindComponentByClass<URPGBossEncounter>() : nullptr;
	const uint64 Generation = Encounter ? Encounter->GetParticipantGeneration() : 0;
	const double Now = GetWorld() ? GetWorld()->GetTimeSeconds() : 0.0;
	if (!Player)
	{
		LogSkip(TEXT("player_unavailable"), nullptr, Now);
		return;
	}
	if (EncounterGeneration != Generation || ObservedPlayer.Get() != Player) ClearEncounterState(Generation, Player);
	URPGPlayerParry* Parry = Player->FindComponentByClass<URPGPlayerParry>();
	URPGAttackTracker* Tracker = Boss ? Boss->FindComponentByClass<URPGAttackTracker>() : nullptr;

	// Resolve/re-snapshot the pack-owned target each tick; the observer remains enabled in Shipping.
	if (!Target.IsValid()) Target.Resolve(Boss);
	const bool bTargetResolved = Target.IsValid();
	UObject* TargetObject = Target.Object.Get();
	UObject* CollisionObject = Target.Collision.Get();
	if (!bHasLoggedTargetState || bLastLoggedTargetResolved != bTargetResolved ||
		LastLoggedTargetObject.Get() != TargetObject || LastLoggedCollisionObject.Get() != CollisionObject)
	{
		bHasLoggedTargetState = true;
		bLastLoggedTargetResolved = bTargetResolved;
		LastLoggedTargetObject = TargetObject;
		LastLoggedCollisionObject = CollisionObject;
		UE_LOG(LogRPGPackParryContact, Display, TEXT("[PARRY] observer_target state=%s target=%s collision=%s"),
			bTargetResolved ? TEXT("resolved") : TEXT("unresolved"), *GetNameSafe(TargetObject), *GetNameSafe(CollisionObject));
	}
	const bool bTraceActive = Target.IsValid() && Target.IsActive();
	if (bTraceActive != bWasTraceActive)
	{
		UE_LOG(LogRPGPackParryContact, Display, TEXT("[PARRY] trace_edge state=%s target=%s hitSet=%d"),
			bTraceActive ? TEXT("active") : TEXT("inactive"), *GetNameSafe(TargetObject), Target.GetHitSetNum());
	}
	TArray<AActor*> HitActors;
	if (bTraceActive) Target.GetHitSet(HitActors);
	URPGTraceGuard* Guard = Boss ? Boss->FindComponentByClass<URPGTraceGuard>() : nullptr;
	TArray<TWeakObjectPtr<AActor>> CurrentHitSet;
	CurrentHitSet.Reserve(HitActors.Num());
	for (AActor* Hit : HitActors) if (Hit) CurrentHitSet.Add(Hit);

	if (bTraceActive && !bWasTraceActive)
	{
		PreviousHitSet.Reset();
		if (Guard)
		{
			for (const TWeakObjectPtr<AActor>& Carried : Guard->GetCarriedAtOpen()) if (Carried.IsValid()) PreviousHitSet.Add(Carried);
		}
	}
	const bool bWindowOpen = Parry && Parry->IsWindowOpen();
	const bool bCandidateWindow = bWindowOpen || (bHasPreviousParrySample && bPreviousParryWindowOpen);
	const RPGParryGrade::EGrade CandidateGrade = bWindowOpen ? Parry->GradeNow() : PreviousParryGrade;
	bool bInvulnerable = false;
	bool bInvulnKnown = false;
	double HealthBefore = 0.0;
	bool bHealthKnown = false;
	if (bTraceActive && HitActors.Contains(Player) && !PreviousHitSet.Contains(TWeakObjectPtr<AActor>(Player)))
	{
		bInvulnKnown = ReadInvulnerabilityTag(Player, bInvulnerable);
		bHealthKnown = RPGPack::ReadAttribute(Player, TEXT("Attribute.Health"), false, HealthBefore);
	}
	if (!bTargetResolved) LogSkip(TEXT("target_unresolved"), nullptr, Now);
	else if (!bTraceActive) LogSkip(TEXT("trace_inactive"), nullptr, Now);
	if (bTraceActive)
	{
		for (AActor* Hit : HitActors)
		{
			if (!Hit)
			{
				LogSkip(TEXT("null_hit_actor"), nullptr, Now);
				continue;
			}
			if (Hit != Player)
			{
				LogSkip(TEXT("non_player_contact"), Hit, Now);
				continue;
			}
			if (PreviousHitSet.Contains(TWeakObjectPtr<AActor>(Player)))
			{
				LogSkip(TEXT("already_in_hitset"), Hit, Now);
				continue;
			}
			const bool bWallSeed = Guard && Guard->IsSeed(Hit);
			const bool bCarried = Guard && Guard->GetCarriedAtOpen().Contains(TWeakObjectPtr<AActor>(Hit));
			UE_LOG(LogRPGPackParryContact, Display,
				TEXT("[PARRY] hitset_insert actor=%s windowKnown=%d windowNow=%d windowPrevious=%d invulnKnown=%d invulnerable=%d healthKnown=%d hp=%.2f grade=%s seed=%d carried=%d"),
				*GetNameSafe(Hit), Parry ? 1 : 0, bWindowOpen ? 1 : 0, bPreviousParryWindowOpen ? 1 : 0,
				bInvulnKnown ? 1 : 0, bInvulnerable ? 1 : 0, bHealthKnown ? 1 : 0, HealthBefore,
				ParryGradeName(CandidateGrade), bWallSeed ? 1 : 0, bCarried ? 1 : 0);
			if (bWallSeed) { LogSkip(TEXT("wall_seed"), Hit, Now); continue; }
			if (bCarried) { LogSkip(TEXT("carried_hit"), Hit, Now); continue; }
			if (!Parry) { LogSkip(TEXT("parry_component_missing"), Hit, Now); continue; }
			if (!bInvulnKnown) { LogSkip(TEXT("invulnerability_unknown"), Hit, Now); continue; }
			if (!RPGPackParry::CanStartCandidate(bCandidateWindow, bInvulnerable))
			{
				LogSkip(bInvulnerable ? TEXT("dodge_invulnerable") : TEXT("native_window_closed"), Hit, Now);
				continue;
			}
			if (!bHealthKnown) { LogSkip(TEXT("health_unknown_at_insert"), Hit, Now); continue; }
			if (CandidateGrade == RPGParryGrade::EGrade::None) { LogSkip(TEXT("grade_unavailable"), Hit, Now); continue; }
			const FString AttackKey = CurrentAttackKey(Boss, Tracker, Now);
			if (AttackKey.IsEmpty()) { LogSkip(TEXT("attack_key_unresolved"), Hit, Now); continue; }
			if (ObservedAttackKeys.Contains(AttackKey)) { LogSkip(TEXT("duplicate_attack_key"), Hit, Now, AttackKey); continue; }
			ObservedAttackKeys.Add(AttackKey);
			FCandidate& Candidate = Candidates.AddDefaulted_GetRef();
			Candidate.AttackKey = AttackKey;
			Candidate.InsertedAt = Now;
			Candidate.PlayerHealthBefore = HealthBefore;
			Candidate.Grade = CandidateGrade;
			UE_LOG(LogRPGPackParryContact, Display, TEXT("[PARRY] candidate key=%s window=%d previous=%d invulnerable=0 hp=%.2f"), *AttackKey, bWindowOpen ? 1 : 0, (!bWindowOpen && bPreviousParryWindowOpen) ? 1 : 0, HealthBefore);
		}
	}

	for (int32 Index = Candidates.Num() - 1; Index >= 0; --Index)
	{
		FCandidate& Candidate = Candidates[Index];
		double HealthNow = 0.0;
		const bool bHealthNowKnown = RPGPack::ReadAttribute(Player, TEXT("Attribute.Health"), false, HealthNow);  // Lead fix C-1148: C4456 shadowing
		const RPGPackParry::ECandidateDecision Decision = RPGPackParry::EvaluateCandidate(bHealthNowKnown, Candidate.PlayerHealthBefore, HealthNow, Now - Candidate.InsertedAt);
		if (Decision == RPGPackParry::ECandidateDecision::Pending) continue;
		if (Decision == RPGPackParry::ECandidateDecision::Confirmed && URPGPlayerParry::NotifyParried(Player, Boss, Candidate.AttackKey, Generation, Candidate.Grade))
		{
			++ConfirmedContactCount;
			UE_LOG(LogRPGPackParryContact, Display, TEXT("[PARRY] confirmed key=%s hp=%.2f->%.2f"), *Candidate.AttackKey, Candidate.PlayerHealthBefore, HealthNow);
		}
		else
		{
			++RejectedContactCount;
			UE_LOG(LogRPGPackParryContact, Display, TEXT("[PARRY] rejected key=%s decision=%d healthKnown=%d"), *Candidate.AttackKey, static_cast<int32>(Decision), bHealthNowKnown ? 1 : 0);
		}
		Candidates.RemoveAtSwap(Index, 1, EAllowShrinking::No);
	}

	PreviousHitSet = MoveTemp(CurrentHitSet);
	bWasTraceActive = bTraceActive;
	if (Parry)
	{
		bHasPreviousParrySample = true;
		bPreviousParryWindowOpen = Parry->IsWindowOpen();
		PreviousParryGrade = bPreviousParryWindowOpen ? Parry->GradeNow() : RPGParryGrade::EGrade::None;
	}
}
