// Copyright One Boss Fight. All Rights Reserved.
#pragma once
#include "Player/RPGBossMoveModel.h"

/** Explicit selector numbers (design values, proposed): no hidden defaults, Initialize refuses zero. */
struct FRPGBossSelectorConfig
{
    float RepeatPenalty = 0.f;   // (0,1]: score factor of a card that is in the recent history
    int32 RepeatMemory = 0;      // 1..8: how many recently started cards count as recent
};
struct FRPGBossSelectorCandidate
{
    TSharedPtr<const FRPGCompiledBossMoveCard> Card;
    float CooldownSeconds = 0.f; // [0,1e6]: hard filter after a start of this card
    float Weight = 1.f;          // (0,1e6]: authored preference
};
/** One line per candidate: why it was refused (named token) or its score. */
struct FRPGBossSelectorTrace
{
    int32 Index = INDEX_NONE;
    FName MoveId;
    bool bEligible = false;
    FString Refusal;
    float Score = 0.f;
};
struct FRPGBossSelectorDecision
{
    int32 ChosenIndex = INDEX_NONE;  // INDEX_NONE = no candidate: the caller owns the fallback, this is not an error
    FName MoveId;
    float Score = 0.f;
    TArray<FRPGBossSelectorTrace> Traces;
};
/**
 * Deterministic two-stage selector. Stage 1 = hard filters (the move model's IsEligible, then the card cooldown), stage 2 = score
 * (weight x range preference x repeat factor), highest wins, ties go to the lowest index. No randomness, no world, no playback.
 */
class ONEBOSSFIGHT_API FRPGBossMoveSelector final
{
public:
    bool Initialize(const FRPGBossSelectorConfig& InConfig, const TArray<FRPGBossSelectorCandidate>& InCandidates, FString& Error);
    bool Select(const FRPGBossMoveModel& Model, const FRPGBossDecisionSnapshot& Snapshot, FRPGBossSelectorDecision& Out) const;
    /** The chosen card really started: cooldown clock and repeat history. */
    void NoteStarted(int32 Index, double ClockSeconds);
    /** Encounter reset: forget cooldown clocks and the repeat history (the clock of a new encounter may restart below the old start times). */
    void Reset();
    int32 CandidateCount() const { return Candidates.Num(); }
private:
    FRPGBossSelectorConfig Config;
    TArray<FRPGBossSelectorCandidate> Candidates;
    TArray<double> LastStartClock; // negative = never started
    TArray<int32> Recent;          // newest last
    bool bInitialized = false;
};
