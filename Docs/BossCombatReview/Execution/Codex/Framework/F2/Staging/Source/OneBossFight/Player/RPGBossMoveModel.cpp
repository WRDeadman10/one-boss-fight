// Copyright One Boss Fight. All Rights Reserved.
#include "Player/RPGBossMoveModel.h"

namespace
{
    bool Refuse(FString& Error, const TCHAR* Token) { Error=Token; return false; }
}
bool FRPGBossMoveModel::Initialize(uint64 EncounterId, uint64 Generation, FString& Error)
{
    Error.Reset();
    if (bInitialized) return Refuse(Error,TEXT("MoveModel.AlreadyInitialized"));
    if (!EncounterId || !Generation) return Refuse(Error,TEXT("MoveModel.Identity"));
    Encounter=EncounterId; Epoch=Generation; bInitialized=true; return true;
}
bool FRPGBossMoveModel::IsEligible(const TSharedPtr<const FRPGCompiledBossMoveCard>& Card,
    const FRPGBossDecisionSnapshot& S, FString& Error) const
{
    Error.Reset();
    if (!bInitialized || S.EncounterId!=Encounter || S.Generation!=Epoch)
        return Refuse(Error,TEXT("MoveModel.Generation"));
    if (!Card || !RPGBossMoveCards::Validate(Card->Spec(),Card->Metadata()).IsValid())
        return Refuse(Error,TEXT("MoveModel.Card"));
    if (!S.bTargetValid || !S.TargetId) return Refuse(Error,TEXT("MoveModel.Target"));
    if (!S.bNeutral || CurrentState!=ERPGBossMoveModelState::Idle)
        return Refuse(Error,TEXT("MoveModel.State"));
    if (!FMath::IsFinite(S.ClockSeconds) || S.ClockSeconds<0.0 ||
        !FMath::IsFinite(S.RangeCm) || S.RangeCm<0.0 || S.RangeCm>1.e6 ||
        !FMath::IsFinite(S.SignedYawDegrees) || FMath::Abs(S.SignedYawDegrees)>180.0)
        return Refuse(Error,TEXT("MoveModel.SnapshotDomain"));
    if (S.PhaseId!=Card->Spec().PhaseId) return Refuse(Error,TEXT("MoveModel.Phase"));
    if (S.RangeCm<Card->Spec().MinRangeCm || S.RangeCm>Card->Spec().MaxRangeCm)
        return Refuse(Error,TEXT("MoveModel.Range"));
    // FrontConeDegrees is the FULL cone width; signed yaw admits left and right symmetrically.
    if (FMath::Abs(S.SignedYawDegrees)>0.5*Card->Spec().FrontConeDegrees)
        return Refuse(Error,TEXT("MoveModel.Cone"));
    if (bHasStarted && (S.FrameId<=LastStartFrame || S.ClockSeconds<LastClock))
        return Refuse(Error,TEXT("MoveModel.StaleDecision"));
    return true;
}
bool FRPGBossMoveModel::Start(const TSharedPtr<const FRPGCompiledBossMoveCard>& Card,
    const FRPGBossDecisionSnapshot& S, FRPGBossAttackToken& OutToken,
    TArray<FRPGBossMoveModelEvent>& Events, FString& Error)
{
    OutToken={}; Events.Reset();
    if (!IsEligible(Card,S,Error)) return false;
    if (NextInstance==MAX_uint64) return Refuse(Error,TEXT("MoveModel.InstanceExhausted"));
    CurrentCard=Card; CurrentToken={Encounter,Epoch,++NextInstance}; OutToken=CurrentToken;
    LastClock=S.ClockSeconds; LastStartFrame=S.FrameId; bHasStarted=true; LocalTime=0.0;
    CurrentState=ERPGBossMoveModelState::Committed; OpenWindows.Reset();
    Cross(0.0,0.0,true,Events); return true;
}
void FRPGBossMoveModel::Emit(ERPGBossMoveModelEvent Kind,const FRPGBossMoveWindow* W,double Time,
    TArray<FRPGBossMoveModelEvent>& Events) const
{
    FRPGBossMoveModelEvent E; E.Kind=Kind; E.Token=CurrentToken; E.LocalSeconds=Time;
    if (W) { E.WindowId=W->WindowId; E.HitGroup=W->HitGroup; }
    Events.Add(E);
}
void FRPGBossMoveModel::Cross(double Before,double After,bool bIncludeStart,
    TArray<FRPGBossMoveModelEvent>& Events)
{
    const auto& S=CurrentCard->Spec();
    auto Crossed=[Before,After,bIncludeStart](double T)
    { return T<=After && (T>Before || (bIncludeStart && T==Before)); };
    if (After>=S.ActiveStartSeconds) CurrentState=ERPGBossMoveModelState::Active;
    // Validated windows are ordered/non-overlapping; emit both edges even if a long step skips the whole span.
    for (const auto& W:S.Windows)
    {
        if (Crossed(W.StartSeconds)) { OpenWindows.Add(W.WindowId); Emit(ERPGBossMoveModelEvent::Open,&W,W.StartSeconds,Events); }
        if (Crossed(W.EndSeconds)) { OpenWindows.Remove(W.WindowId); Emit(ERPGBossMoveModelEvent::Close,&W,W.EndSeconds,Events); }
    }
    if (Crossed(S.ActiveEndSeconds))
    { CurrentState=ERPGBossMoveModelState::Recovery; Emit(ERPGBossMoveModelEvent::Recovery,nullptr,S.ActiveEndSeconds,Events); }
    else if (After>=S.ActiveEndSeconds) CurrentState=ERPGBossMoveModelState::Recovery;
    if (Crossed(S.RecoveryEndSeconds))
    {
        Emit(ERPGBossMoveModelEvent::Finished,nullptr,S.RecoveryEndSeconds,Events);
        CurrentState=ERPGBossMoveModelState::Idle; CurrentCard.Reset(); OpenWindows.Reset();
    }
}
bool FRPGBossMoveModel::AcceptsCallback(const FRPGBossAttackToken& Token) const
{
    return bInitialized && CurrentState!=ERPGBossMoveModelState::Idle && Token.InstanceId!=0 &&
        Token.EncounterId==Encounter && Token.Generation==Epoch && Token==CurrentToken;
}
bool FRPGBossMoveModel::Advance(const FRPGBossAttackToken& Token,double ClockSeconds,bool bPaused,
    TArray<FRPGBossMoveModelEvent>& Events,FString& Error)
{
    Events.Reset(); Error.Reset();
    if (!AcceptsCallback(Token)) return Refuse(Error,TEXT("MoveModel.StaleCallback"));
    if (!FMath::IsFinite(ClockSeconds) || ClockSeconds<LastClock)
    { CloseAndClear(Events,true); return Refuse(Error,TEXT("MoveModel.Clock")); }
    const double Delta=ClockSeconds-LastClock;
    const double Next=LocalTime+(bPaused ? 0.0 : Delta*CurrentCard->Spec().PlayRate);
    if (!FMath::IsFinite(Next))
    { CloseAndClear(Events,true); return Refuse(Error,TEXT("MoveModel.ClockOverflow")); }
    LastClock=ClockSeconds;
    if (Next==LocalTime) return true;
    const double Before=LocalTime; LocalTime=Next;
    Cross(Before,Next,false,Events); return true;
}
void FRPGBossMoveModel::CloseAndClear(TArray<FRPGBossMoveModelEvent>& Events,bool bAborted)
{
    if (CurrentState==ERPGBossMoveModelState::Idle) return;
    for (const auto& W:CurrentCard->Spec().Windows)
        if (OpenWindows.Contains(W.WindowId)) Emit(ERPGBossMoveModelEvent::Close,&W,LocalTime,Events);
    if (bAborted) Emit(ERPGBossMoveModelEvent::Aborted,nullptr,LocalTime,Events);
    OpenWindows.Reset(); CurrentCard.Reset(); CurrentState=ERPGBossMoveModelState::Idle;
}
bool FRPGBossMoveModel::Abort(const FRPGBossAttackToken& Token,
    TArray<FRPGBossMoveModelEvent>& Events,FString& Error)
{
    Events.Reset(); Error.Reset();
    if (!bInitialized || !Token.InstanceId || Token.EncounterId!=Encounter || Token.Generation!=Epoch || !(Token==CurrentToken))
        return Refuse(Error,TEXT("MoveModel.StaleCallback"));
    CloseAndClear(Events,true); return true;
}
bool FRPGBossMoveModel::ResetGeneration(uint64 Generation,
    TArray<FRPGBossMoveModelEvent>& Events,FString& Error)
{
    Events.Reset(); Error.Reset();
    if (!bInitialized || Generation<=Epoch) return Refuse(Error,TEXT("MoveModel.Generation"));
    CloseAndClear(Events,true); Epoch=Generation; return true;
}
bool FRPGBossMoveModel::HeadingCommitted() const
{
    return CurrentCard && CurrentState!=ERPGBossMoveModelState::Idle && LocalTime>=CurrentCard->Spec().CommitSeconds;
}
