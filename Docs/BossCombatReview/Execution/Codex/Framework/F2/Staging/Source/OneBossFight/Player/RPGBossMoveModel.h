// Copyright One Boss Fight. All Rights Reserved.
#pragma once
#include "Player/RPGBossMoveCard.h"

/** Pure value inputs. IDs are caller-owned identities, not proof of live actors/worlds. */
struct FRPGBossDecisionSnapshot
{
    uint64 EncounterId = 0, Generation = 0, TargetId = 0, FrameId = 0;
    FName PhaseId;
    double ClockSeconds = 0.0, RangeCm = 0.0, SignedYawDegrees = 0.0;
    bool bTargetValid = false, bNeutral = false;
};
struct FRPGBossAttackToken
{
    uint64 EncounterId = 0, Generation = 0, InstanceId = 0;
    bool operator==(const FRPGBossAttackToken& Other) const
    { return EncounterId==Other.EncounterId && Generation==Other.Generation && InstanceId==Other.InstanceId; }
};
enum class ERPGBossMoveModelState : uint8 { Idle, Committed, Active, Recovery };
enum class ERPGBossMoveModelEvent : uint8 { Open, Close, Recovery, Finished, Aborted };
struct FRPGBossMoveModelEvent
{
    ERPGBossMoveModelEvent Kind;
    FRPGBossAttackToken Token;
    FName WindowId, HitGroup;
    double LocalSeconds = 0.0;
};
/** NO world/actor/playback/damage ownership; pure scheduling proposal, not a runtime capability. */
class ONEBOSSFIGHT_API FRPGBossMoveModel final
{
public:
    FRPGBossMoveModel() = default;
    FRPGBossMoveModel(const FRPGBossMoveModel&) = delete;
    FRPGBossMoveModel& operator=(const FRPGBossMoveModel&) = delete;
    bool Initialize(uint64 EncounterId, uint64 Generation, FString& Error);
    /** One candidate, deterministic hard filters; no random choice, fallback or forced starts. */
    bool IsEligible(const TSharedPtr<const FRPGCompiledBossMoveCard>& Card,
        const FRPGBossDecisionSnapshot& Snapshot, FString& Error) const;
    bool Start(const TSharedPtr<const FRPGCompiledBossMoveCard>& Card,
        const FRPGBossDecisionSnapshot& Snapshot, FRPGBossAttackToken& OutToken,
        TArray<FRPGBossMoveModelEvent>& Events, FString& Error);
    /** Clock is monotonic wall seconds. Paused calls consume wall time without advancing montage-local time. */
    bool Advance(const FRPGBossAttackToken& Token, double ClockSeconds, bool bPaused,
        TArray<FRPGBossMoveModelEvent>& Events, FString& Error);
    /** Idempotent for current/already-finished token; stale token never aborts a newer attack. */
    bool Abort(const FRPGBossAttackToken& Token, TArray<FRPGBossMoveModelEvent>& Events, FString& Error);
    /** Explicit monotonic generation change. Aborts owned attack first, never resets instance counter. */
    bool ResetGeneration(uint64 Generation, TArray<FRPGBossMoveModelEvent>& Events, FString& Error);
    bool AcceptsCallback(const FRPGBossAttackToken& Token) const;
    ERPGBossMoveModelState State() const { return CurrentState; }
    double LocalSeconds() const { return LocalTime; }
    bool HeadingCommitted() const;
    const FRPGBossAttackToken& ActiveToken() const { return CurrentToken; }
private:
    void Cross(double Before, double After, bool bIncludeStart, TArray<FRPGBossMoveModelEvent>& Events);
    void Emit(ERPGBossMoveModelEvent Kind, const FRPGBossMoveWindow* Window, double Time,
        TArray<FRPGBossMoveModelEvent>& Events) const;
    void CloseAndClear(TArray<FRPGBossMoveModelEvent>& Events, bool bAborted);
    uint64 Encounter = 0, Epoch = 0, NextInstance = 0, LastStartFrame = 0;
    bool bInitialized = false, bHasStarted = false;
    double LastClock = 0.0, LocalTime = 0.0;
    FRPGBossAttackToken CurrentToken;
    ERPGBossMoveModelState CurrentState = ERPGBossMoveModelState::Idle;
    TSharedPtr<const FRPGCompiledBossMoveCard> CurrentCard;
    TSet<FName> OpenWindows;
};
