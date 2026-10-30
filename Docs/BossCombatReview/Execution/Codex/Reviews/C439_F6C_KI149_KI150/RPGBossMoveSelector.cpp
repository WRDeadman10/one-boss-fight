// Copyright One Boss Fight. All Rights Reserved.
#include "Player/RPGBossMoveSelector.h"

namespace
{
    bool Refuse(FString& Error, const TCHAR* Token) { Error=Token; return false; }
}
bool FRPGBossMoveSelector::Initialize(const FRPGBossSelectorConfig& InConfig,
    const TArray<FRPGBossSelectorCandidate>& InCandidates, FString& Error)
{
    Error.Reset();
    if (bInitialized) return Refuse(Error,TEXT("Selector.AlreadyInitialized"));
    if (!FMath::IsFinite(InConfig.RepeatPenalty) || InConfig.RepeatPenalty<=0.f || InConfig.RepeatPenalty>1.f ||
        InConfig.RepeatMemory<1 || InConfig.RepeatMemory>8)
        return Refuse(Error,TEXT("Selector.Config"));
    if (InCandidates.Num()==0) return Refuse(Error,TEXT("Selector.NoCandidates"));
    TSet<FName> Ids;
    for (const auto& C:InCandidates)
    {
        if (!C.Card) return Refuse(Error,TEXT("Selector.NullCard"));
        if (!FMath::IsFinite(C.CooldownSeconds) || C.CooldownSeconds<0.f || C.CooldownSeconds>1.e6f ||
            !FMath::IsFinite(C.Weight) || C.Weight<=0.f || C.Weight>1.e6f)
            return Refuse(Error,TEXT("Selector.Domain"));
        bool bDuplicate=false; Ids.Add(C.Card->Spec().MoveId,&bDuplicate);
        if (bDuplicate) return Refuse(Error,TEXT("Selector.DuplicateMoveId"));
    }
    Config=InConfig; Candidates=InCandidates; LastStartClock.Init(-1.0,Candidates.Num()); Recent.Reset();
    bInitialized=true; return true;
}
bool FRPGBossMoveSelector::Select(const FRPGBossMoveModel& Model, const FRPGBossDecisionSnapshot& S,
    FRPGBossSelectorDecision& Out) const
{
    Out=FRPGBossSelectorDecision();
    if (!bInitialized) return false;
    for (int32 I=0;I<Candidates.Num();++I)
    {
        const auto& C=Candidates[I]; const auto& Spec=C.Card->Spec();
        FRPGBossSelectorTrace T; T.Index=I; T.MoveId=Spec.MoveId;
        FString Error;
        if (!Model.IsEligible(C.Card,S,Error)) T.Refusal=Error;   // stage 1: the model's named hard filters
        else if (LastStartClock[I]>=0.0 && S.ClockSeconds-LastStartClock[I]<C.CooldownSeconds) T.Refusal=TEXT("Selector.Cooldown");
        else
        {
            // stage 2: range preference is 1 at the middle of the card's range and 0.5 at its edges; a recently started card is scaled down.
            const double Mid=0.5*(Spec.MinRangeCm+Spec.MaxRangeCm), Half=0.5*(Spec.MaxRangeCm-Spec.MinRangeCm);
            const double RangeFactor=Half>0.0 ? 1.0-0.5*FMath::Min(1.0,FMath::Abs(S.RangeCm-Mid)/Half) : 1.0;
            const double Repeat=Recent.Contains(I) ? Config.RepeatPenalty : 1.0;
            T.bEligible=true; T.Score=float(C.Weight*RangeFactor*Repeat);
            if (Out.ChosenIndex==INDEX_NONE || T.Score>Out.Score) { Out.ChosenIndex=I; Out.MoveId=Spec.MoveId; Out.Score=T.Score; }
        }
        Out.Traces.Add(T);
    }
    return true;
}
void FRPGBossMoveSelector::NoteStarted(int32 Index, double ClockSeconds)
{
    if (!bInitialized || !Candidates.IsValidIndex(Index) || !FMath::IsFinite(ClockSeconds) || ClockSeconds<0.0) return;
    LastStartClock[Index]=ClockSeconds;
    Recent.Remove(Index); Recent.Add(Index);
    while (Recent.Num()>Config.RepeatMemory) Recent.RemoveAt(0);
}
void FRPGBossMoveSelector::Reset()
{
    if (!bInitialized) return;
    LastStartClock.Init(-1.0,Candidates.Num()); Recent.Reset();
}
