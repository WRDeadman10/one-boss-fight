// Copyright One Boss Fight. All Rights Reserved.

#pragma once

#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "RPGDamageResolver.generated.h"

/** What happened to one contact between a boss move and the player (SPEC M2, Freeze 12.1 and 21). */
UENUM(BlueprintType)
enum class ERPGDamageOutcome : uint8
{
	Overlap,              // the move's own geometry touched the player's capsule (a note, not a decision)
	Accepted,             // health taken once
	RejectedInvulnerable, // Status.Invulnerable at the moment of resolution (dodge i-frames): nothing changed, the hit is not spent
	RejectedDead,         // the player was already dead
	RejectedStale,        // the attacker is dead or the move belongs to an old encounter generation
	RejectedDuplicate,    // the same swing (move, instance, key) already hurt the player
	MissJumped,           // the player's feet were above the blade or wave (geometry verdict of the move)
	MissWorld,            // arena geometry stopped the move
	Superseded,           // another hit of the same move already hurt the player (the wave yields to the central hit)
	Failed                // the health attribute could not be written
};

/** What a boss move asks the resolver to do to the player. HP only: boss moves take no posture (Freeze 504); guard and hit reaction are not built (KI-065, KI-067, KI-068). */
USTRUCT(BlueprintType)
struct FRPGDamagePayload
{
	GENERATED_BODY()

	/** "A4", "A5", "A6". */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Damage")
	FName MoveId;

	/** URPGAttackTracker::GetAttackInstance() when the move started: repeated contacts of one swing hurt once. */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Damage")
	int32 AttackInstance = 0;

	/** Encounter generation when the move started; a payload of an older generation is stale (Freeze 32.2). */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Damage")
	int32 Generation = 0;

	/** A second authored stage of one instance that may hit again uses another key (Freeze 530). */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Damage")
	FName HitKey;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Damage")
	float HPDamage = 0.f;
};

USTRUCT(BlueprintType)
struct FRPGDamageResult
{
	GENERATED_BODY()

	UPROPERTY(BlueprintReadOnly, Category = "Damage")
	ERPGDamageOutcome Outcome = ERPGDamageOutcome::Failed;

	UPROPERTY(BlueprintReadOnly, Category = "Damage")
	float HPApplied = 0.f;

	UPROPERTY(BlueprintReadOnly, Category = "Damage")
	float HealthBefore = 0.f;

	UPROPERTY(BlueprintReadOnly, Category = "Damage")
	float HealthAfter = 0.f;

	/** The hit took the last health (Freeze 1267: nothing but the death follows). */
	UPROPERTY(BlueprintReadOnly, Category = "Damage")
	bool bLethal = false;
};

namespace RPGDamageRules
{
	inline const TCHAR* Name(ERPGDamageOutcome Outcome)
	{
		switch (Outcome)
		{
		case ERPGDamageOutcome::Overlap: return TEXT("Overlap");
		case ERPGDamageOutcome::Accepted: return TEXT("Accepted");
		case ERPGDamageOutcome::RejectedInvulnerable: return TEXT("RejectedInvulnerable");
		case ERPGDamageOutcome::RejectedDead: return TEXT("RejectedDead");
		case ERPGDamageOutcome::RejectedStale: return TEXT("RejectedStale");
		case ERPGDamageOutcome::RejectedDuplicate: return TEXT("RejectedDuplicate");
		case ERPGDamageOutcome::MissJumped: return TEXT("MissJumped");
		case ERPGDamageOutcome::MissWorld: return TEXT("MissWorld");
		case ERPGDamageOutcome::Superseded: return TEXT("Superseded");
		default: return TEXT("Failed");
		}
	}

	/** The decision order of one contact (Freeze 12.1 steps 1 to 4): the target must be alive, the attacker alive and of the current generation, the swing must not have hurt already, and only then the target's
	 *  invulnerability at this moment decides. Pure, so an automation test can run it without a world or the pack. */
	inline ERPGDamageOutcome Decide(bool bTargetAlive, bool bAttackerAlive, bool bGenerationCurrent, bool bDuplicate, bool bTargetInvulnerable)
	{
		if (!bTargetAlive) { return ERPGDamageOutcome::RejectedDead; }
		if (!bAttackerAlive || !bGenerationCurrent) { return ERPGDamageOutcome::RejectedStale; }
		if (bDuplicate) { return ERPGDamageOutcome::RejectedDuplicate; }
		if (bTargetInvulnerable) { return ERPGDamageOutcome::RejectedInvulnerable; }
		return ERPGDamageOutcome::Accepted;
	}
}

/**
 * The one place that lowers the player's health for the boss's own moves (A4 blade, A5 javelin, A6 wave). The pack has no entry point for damage without a weapon trace, so the health attribute is written here;
 * invulnerability is read here at the moment of resolution (Freeze 488: not from the montage, not from the move's geometry). Every contact leaves an audit entry, so "overlap" and "damage accepted" are told apart
 * (Freeze 489), and the overlay and the tests read them. A contact that is rejected never spends the hit: the move may touch the player again (the blade, the javelin). Pack weapon moves (A1, A2 stand-in, A3)
 * still reject at the pack's trace and are not audited here.
 */
UCLASS(ClassGroup = (Boss))
class ONEBOSSFIGHT_API URPGDamageResolver : public UActorComponent
{
	GENERATED_BODY()

public:
	URPGDamageResolver();

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Damage")
	bool bEnabled = true;

	/** Audit entries kept (the newest). */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Damage", meta = (ClampMin = "8"))
	int32 MaxAuditEntries = 64;

	/** Overlap notes of one swing closer than this (seconds) are one entry: a contact episode, not one entry per tick. */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Damage", meta = (ClampMin = "0.0"))
	float OverlapEpisodeGapSeconds = 0.25f;

	/** The resolver of this boss; added when missing so a move never skips the rules. */
	static URPGDamageResolver* FindOrAdd(AActor* Boss);

	/** Decides and applies one contact. Target is the player pawn. */
	FRPGDamageResult Resolve(AActor* Target, const FRPGDamagePayload& Payload);

	/** The move's own geometry touched the player (before any decision). Coalesced per swing. */
	void NoteOverlap(const FRPGDamagePayload& Payload);

	/** A geometry verdict of the move that is not a damage rule (jumped, world blocked, superseded): audit only. */
	void NoteMiss(const FRPGDamagePayload& Payload, ERPGDamageOutcome Outcome, FName Reason);

	/** Readers for tests and the overlay. */
	UFUNCTION(BlueprintPure, Category = "Damage")
	int32 GetAuditCount() const { return AuditTotal; }

	/** Text of an entry, 0 = oldest kept; "" when out of range. */
	UFUNCTION(BlueprintPure, Category = "Damage")
	FString GetAuditLine(int32 Index) const;

	UFUNCTION(BlueprintPure, Category = "Damage")
	FString GetLastOutcomeName() const { return LastOutcome; }

	/** Entries of this outcome (by name, e.g. "RejectedInvulnerable"), all moves or one move. */
	UFUNCTION(BlueprintPure, Category = "Damage")
	int32 GetOutcomeCount(const FString& OutcomeName) const;

	UFUNCTION(BlueprintPure, Category = "Damage")
	int32 GetMoveOutcomeCount(FName MoveId, const FString& OutcomeName) const;

	UFUNCTION(BlueprintCallable, Category = "Damage")
	void ClearAudit();

	/** One line for the debug overlay. */
	UFUNCTION(BlueprintPure, Category = "Damage")
	FString BuildSummaryLine() const;

	/** Tests (the hooks stay in every build: UHT does not evaluate the shipping switch): resolves a payload against the first player pawn. Returns the outcome name. Generation -1 = the current one. */
	UFUNCTION(BlueprintCallable, Category = "Damage")
	FString ResolveForTest(FName MoveId, int32 Instance, float HP, FName HitKey, int32 Generation = -1);

	UFUNCTION(BlueprintCallable, Category = "Damage")
	void NoteOverlapForTest(FName MoveId, int32 Instance, FName HitKey);

private:
	struct FEntry
	{
		int32 Index = 0;
		double Time = 0.0;
		FName Move;
		int32 Instance = 0;
		int32 Generation = 0;
		FName Key;
		ERPGDamageOutcome Outcome = ERPGDamageOutcome::Overlap;
		FName Reason;
		float HPRequested = 0.f;
		float HealthBefore = 0.f;
		float HealthAfter = 0.f;
	};

	static FString KeyOf(const FRPGDamagePayload& Payload);
	void Record(const FRPGDamagePayload& Payload, ERPGDamageOutcome Outcome, FName Reason, float HealthBefore, float HealthAfter);
	int32 CurrentGeneration() const;
	/** The duplicate set belongs to one encounter generation. */
	void SyncGeneration();

	TArray<FEntry> Audit;
	TSet<FString> Spent;       // swings that already hurt the player in this generation
	TMap<FString, double> LastOverlap;
	TMap<FString, int32> Counts; // "Move|Outcome" and "|Outcome"
	int32 AuditTotal = 0;
	int32 SeenGeneration = 0;
	FString LastOutcome;
};
