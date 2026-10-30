// Copyright One Boss Fight. All Rights Reserved.

#include "Player/RPGDamageResolver.h"
#include "Engine/World.h"
#include "GameFramework/Character.h"
#include "Kismet/GameplayStatics.h"
#include "Pack/RPGBlueprintCall.h"
#include "Player/RPGBossDamage.h"
#include "Player/RPGBossEncounter.h"

DEFINE_LOG_CATEGORY_STATIC(LogRPGDamage, Log, All);

using namespace RPGPack;

URPGDamageResolver::URPGDamageResolver()
{
	PrimaryComponentTick.bCanEverTick = false;
}

URPGDamageResolver* URPGDamageResolver::FindOrAdd(AActor* Boss)
{
	if (!Boss)
	{
		return nullptr;
	}
	if (URPGDamageResolver* Existing = Boss->FindComponentByClass<URPGDamageResolver>())
	{
		return Existing;
	}
	URPGDamageResolver* Created = NewObject<URPGDamageResolver>(Boss, TEXT("RPGDamageResolver"));
	Created->RegisterComponent();
	return Created;
}

FString URPGDamageResolver::KeyOf(const FRPGDamagePayload& Payload)
{
	return FString::Printf(TEXT("%s|%d|%s"), *Payload.MoveId.ToString(), Payload.AttackInstance, *Payload.HitKey.ToString());
}

int32 URPGDamageResolver::CurrentGeneration() const
{
	if (ProviderGeneration)
	{
		return ProviderGeneration();
	}
	const URPGBossEncounter* Encounter = GetOwner() ? GetOwner()->FindComponentByClass<URPGBossEncounter>() : nullptr;
	return Encounter ? Encounter->GetGeneration() : 0;
}

void URPGDamageResolver::SetLifeProvider(TFunction<bool()> InIsAlive, TFunction<int32()> InGeneration)
{
	// Both or none: a half provider would mix the framework's life with the legacy generation.
	if (!InIsAlive || !InGeneration)
	{
		ClearLifeProvider();
		return;
	}
	ProviderIsAlive = MoveTemp(InIsAlive);
	ProviderGeneration = MoveTemp(InGeneration);
}

void URPGDamageResolver::ClearLifeProvider()
{
	ProviderIsAlive = nullptr;
	ProviderGeneration = nullptr;
}

void URPGDamageResolver::SyncGeneration()
{
	const int32 Generation = CurrentGeneration();
	if (Generation != SeenGeneration)
	{
		SeenGeneration = Generation;
		Spent.Reset();
		LastOverlap.Reset();
	}
}

void URPGDamageResolver::Record(const FRPGDamagePayload& Payload, ERPGDamageOutcome Outcome, FName Reason, float HealthBefore, float HealthAfter)
{
	FEntry Entry;
	Entry.Index = AuditTotal++;
	Entry.Time = GetWorld() ? GetWorld()->GetTimeSeconds() : 0.0;
	Entry.Move = Payload.MoveId;
	Entry.Instance = Payload.AttackInstance;
	Entry.Generation = Payload.Generation;
	Entry.Key = Payload.HitKey;
	Entry.Outcome = Outcome;
	Entry.Reason = Reason;
	Entry.HPRequested = Payload.HPDamage;
	Entry.HealthBefore = HealthBefore;
	Entry.HealthAfter = HealthAfter;
	Audit.Add(Entry);
	while (Audit.Num() > MaxAuditEntries)
	{
		Audit.RemoveAt(0);
	}
	LastOutcome = RPGDamageRules::Name(Outcome);
	++Counts.FindOrAdd(FString::Printf(TEXT("%s|%s"), *Payload.MoveId.ToString(), RPGDamageRules::Name(Outcome)));
	++Counts.FindOrAdd(FString::Printf(TEXT("|%s"), RPGDamageRules::Name(Outcome)));
	UE_LOG(LogRPGDamage, Log, TEXT("%s: %s instance %d generation %d: %s%s (health %.1f -> %.1f, asked %.1f)"), *GetOwner()->GetName(), *Payload.MoveId.ToString(), Payload.AttackInstance, Payload.Generation,
		RPGDamageRules::Name(Outcome), Reason.IsNone() ? TEXT("") : *FString::Printf(TEXT(" (%s)"), *Reason.ToString()), HealthBefore, HealthAfter, Payload.HPDamage);
}

void URPGDamageResolver::NoteOverlap(const FRPGDamagePayload& Payload)
{
	if (!bEnabled || !GetWorld())
	{
		return;
	}
	SyncGeneration();
	const FString Key = KeyOf(Payload);
	const double Now = GetWorld()->GetTimeSeconds();
	double* Last = LastOverlap.Find(Key);
	const bool bNewEpisode = !Last || Now - *Last > OverlapEpisodeGapSeconds;
	LastOverlap.Add(Key, Now);
	if (bNewEpisode)
	{
		Record(Payload, ERPGDamageOutcome::Overlap, NAME_None, 0.f, 0.f);
	}
}

void URPGDamageResolver::NoteMiss(const FRPGDamagePayload& Payload, ERPGDamageOutcome Outcome, FName Reason)
{
	if (bEnabled)
	{
		SyncGeneration();
		Record(Payload, Outcome, Reason, 0.f, 0.f);
	}
}

FRPGDamageResult URPGDamageResolver::Resolve(AActor* Target, const FRPGDamagePayload& Payload)
{
	FRPGDamageResult Result;
	if (!bEnabled || !Target || !GetWorld())
	{
		Result.Outcome = ERPGDamageOutcome::Failed;
		return Result;
	}
	SyncGeneration();
	const FString Key = KeyOf(Payload);
	double Before = 0.0;
	const bool bHaveHealth = ReadAttribute(Target, TEXT("Attribute.Health"), false, Before);
	Result.HealthBefore = static_cast<float>(Before);
	Result.HealthAfter = Result.HealthBefore;
	const bool bTargetAlive = bHaveHealth && Before > 0.0 && !RPGBossDamage::HasTag(Target, TEXT("Status.Dead"));
	const bool bAttackerAlive = ProviderIsAlive ? ProviderIsAlive() : RPGBossDamage::IsAlive(GetOwner());
	const bool bCurrent = Payload.Generation == CurrentGeneration();
	const bool bDuplicate = Spent.Contains(Key);
	// The invulnerability is read here, at the moment the damage would be applied (Freeze 488), and only when the earlier rules did not already reject.
	const bool bInvulnerable = bTargetAlive && bAttackerAlive && bCurrent && !bDuplicate && RPGBossDamage::IsInvulnerable(Target);
	Result.Outcome = RPGDamageRules::Decide(bTargetAlive, bAttackerAlive, bCurrent, bDuplicate, bInvulnerable);
	FName Reason = NAME_None;
	switch (Result.Outcome)
	{
	case ERPGDamageOutcome::Accepted:
	{
		double HealthBefore = 0.0, HealthAfter = 0.0;
		if (RPGBossDamage::HurtPlayer(Target, Payload.HPDamage, HealthBefore, HealthAfter))
		{
			Spent.Add(Key); // a rejected contact never spends the hit: only an accepted one does
			Result.HPApplied = static_cast<float>(HealthBefore - HealthAfter);
			Result.HealthAfter = static_cast<float>(HealthAfter);
			Result.bLethal = HealthAfter <= 0.0; // Freeze 1267: a lethal hit is followed by nothing but the death (no reaction is requested for boss moves in any case)
		}
		else
		{
			Result.Outcome = ERPGDamageOutcome::Failed;
			Reason = TEXT("health attribute not writable");
		}
		break;
	}
	case ERPGDamageOutcome::RejectedStale:
		Reason = bAttackerAlive ? TEXT("old generation") : TEXT("attacker dead");
		break;
	case ERPGDamageOutcome::RejectedInvulnerable:
		Reason = TEXT("Status.Invulnerable");
		break;
	default:
		break;
	}
	Record(Payload, Result.Outcome, Reason, Result.HealthBefore, Result.HealthAfter);
	return Result;
}

FString URPGDamageResolver::GetAuditLine(int32 Index) const
{
	if (!Audit.IsValidIndex(Index))
	{
		return FString();
	}
	const FEntry& E = Audit[Index];
	return FString::Printf(TEXT("#%d t=%.2f %s inst %d gen %d %s%s health %.1f -> %.1f asked %.1f"), E.Index, E.Time, *E.Move.ToString(), E.Instance, E.Generation, RPGDamageRules::Name(E.Outcome),
		E.Reason.IsNone() ? TEXT("") : *FString::Printf(TEXT(" (%s)"), *E.Reason.ToString()), E.HealthBefore, E.HealthAfter, E.HPRequested);
}

int32 URPGDamageResolver::GetOutcomeCount(const FString& OutcomeName) const
{
	const int32* Count = Counts.Find(FString::Printf(TEXT("|%s"), *OutcomeName));
	return Count ? *Count : 0;
}

int32 URPGDamageResolver::GetMoveOutcomeCount(FName MoveId, const FString& OutcomeName) const
{
	const int32* Count = Counts.Find(FString::Printf(TEXT("%s|%s"), *MoveId.ToString(), *OutcomeName));
	return Count ? *Count : 0;
}

void URPGDamageResolver::ClearAudit()
{
	Audit.Reset();
	Counts.Reset();
	LastOverlap.Reset();
	AuditTotal = 0;
	LastOutcome.Reset();
}

FString URPGDamageResolver::BuildSummaryLine() const
{
	return FString::Printf(TEXT("  DAMAGE  accepted %d  rejected invulnerable %d  duplicate %d  stale %d  dead %d  overlaps %d  last: %s"), GetOutcomeCount(TEXT("Accepted")), GetOutcomeCount(TEXT("RejectedInvulnerable")),
		GetOutcomeCount(TEXT("RejectedDuplicate")), GetOutcomeCount(TEXT("RejectedStale")), GetOutcomeCount(TEXT("RejectedDead")), GetOutcomeCount(TEXT("Overlap")), Audit.Num() > 0 ? *GetAuditLine(Audit.Num() - 1) : TEXT("-"));
}

FString URPGDamageResolver::ResolveForTest(FName MoveId, int32 Instance, float HP, FName HitKey, int32 Generation)
{
#if UE_BUILD_SHIPPING
	return TEXT("unavailable in Shipping");
#else
	FRPGDamagePayload Payload;
	Payload.MoveId = MoveId;
	Payload.AttackInstance = Instance;
	Payload.HitKey = HitKey;
	Payload.HPDamage = HP;
	Payload.Generation = Generation >= 0 ? Generation : CurrentGeneration();
	const FRPGDamageResult Result = Resolve(UGameplayStatics::GetPlayerPawn(this, 0), Payload);
	return RPGDamageRules::Name(Result.Outcome);
#endif
}

void URPGDamageResolver::NoteOverlapForTest(FName MoveId, int32 Instance, FName HitKey)
{
#if !UE_BUILD_SHIPPING
	FRPGDamagePayload Payload;
	Payload.MoveId = MoveId;
	Payload.AttackInstance = Instance;
	Payload.HitKey = HitKey;
	Payload.Generation = CurrentGeneration();
	NoteOverlap(Payload);
#endif
}
