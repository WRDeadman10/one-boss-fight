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
        InConfig.RepeatMemory<1 || InConfig.RepeatMemory>8 || !FMath::IsFinite(InConfig.TieBand) || InConfig.TieBand<0.f || InConfig.TieBand>0.5f)
        return Refuse(Error,TEXT("Selector.Config"));
    if (InCandidates.Num()==0) return Refuse(Error,TEXT("Selector.NoCandidates"));
    TSet<FName> Ids;
    for (const auto& C:InCandidates)
    {
        if (!C.Card) return Refuse(Error,TEXT("Selector.NullCard"));
        if (!FMath::IsFinite(C.CooldownSeconds) || C.CooldownSeconds<0.f || C.CooldownSeconds>1.e6f ||
            !FMath::IsFinite(C.Weight) || C.Weight<=0.f || C.Weight>1.e6f ||
            !FMath::IsFinite(C.KiteMultiplier) || C.KiteMultiplier<=0.f || C.KiteMultiplier>1.e6f || !FMath::IsFinite(C.HugMultiplier) || C.HugMultiplier<=0.f || C.HugMultiplier>1.e6f ||
            !FMath::IsFinite(C.BackDodgeMultiplier) || C.BackDodgeMultiplier<=0.f || C.BackDodgeMultiplier>1.e6f ||
            !FMath::IsFinite(C.GreedMultiplier) || C.GreedMultiplier<=0.f || C.GreedMultiplier>1.e6f)
            return Refuse(Error,TEXT("Selector.Domain"));
        bool bDuplicate=false; Ids.Add(C.Card->Spec().MoveId,&bDuplicate);
        if (bDuplicate) return Refuse(Error,TEXT("Selector.DuplicateMoveId"));
    }
    Config=InConfig; Candidates=InCandidates; LastStartClock.Init(-1.0,Candidates.Num()); Recent.Reset(); ConeInside.Reset();
    bInitialized=true; return true;
}
bool FRPGBossMoveSelector::Select(const FRPGBossMoveModel& Model, const FRPGBossDecisionSnapshot& S,
    FRPGBossSelectorDecision& Out, const FRPGBossSelectorContext& Context) const
{
    Out=FRPGBossSelectorDecision();
    if (!bInitialized) return false;
    for (int32 I=0;I<Candidates.Num();++I)
    {
        const auto& C=Candidates[I]; const auto& Spec=C.Card->Spec();
        FRPGBossSelectorTrace T; T.Index=I; T.MoveId=Spec.MoveId;
        FString Error;
        FRPGBossDecisionSnapshot ModelSnapshot=S;
        const bool bConeMemoryEnabled=FMath::IsFinite(Context.ConeHysteresisDegrees)&&Context.ConeHysteresisDegrees>0.0;
        if (bConeMemoryEnabled) ModelSnapshot.ConeHoldSlackDegrees=ConeInside.FindRef(I)?Context.ConeHysteresisDegrees:0.0;
        else { ModelSnapshot.ConeHoldSlackDegrees=0.0; ConeInside.Reset(); }
        const bool bModelEligible=Model.IsEligible(C.Card,ModelSnapshot,Error);
        if (!bModelEligible)
        {
            T.Refusal=Error;   // stage 1: the model's named hard filters
            if (bConeMemoryEnabled && Error==TEXT("MoveModel.Cone")) ConeInside.Add(I,false);
        }
        else if (bConeMemoryEnabled) ConeInside.Add(I,true);
        if (bModelEligible && LastStartClock[I]>=0.0 && S.ClockSeconds-LastStartClock[I]<C.CooldownSeconds)
            T.Refusal=TEXT("Selector.Cooldown");
        if (bModelEligible && T.Refusal.IsEmpty())
        {
            // stage 2: range preference is 1 at the middle of the card's range and 0.5 at its edges; a recently started card is scaled down.
            const double Mid=0.5*(Spec.MinRangeCm+Spec.MaxRangeCm), Half=0.5*(Spec.MaxRangeCm-Spec.MinRangeCm);
            const double RangeFactor=Half>0.0 ? 1.0-0.5*FMath::Min(1.0,FMath::Abs(S.RangeCm-Mid)/Half) : 1.0;
            const double Repeat=Recent.Contains(I) ? Config.RepeatPenalty : 1.0;
            const double Pattern=(Context.bKiting ? double(C.KiteMultiplier) : 1.0)*(Context.bHugging ? double(C.HugMultiplier) : 1.0)*(Context.bBackDodging ? double(C.BackDodgeMultiplier) : 1.0)*(Context.bGreedy ? double(C.GreedMultiplier) : 1.0);   // BOSS-PHS-005, AWR-008
            T.bEligible=true; T.Score=float(C.Weight*RangeFactor*Repeat*Pattern);
            if (Out.ChosenIndex==INDEX_NONE || T.Score>Out.Score) { Out.ChosenIndex=I; Out.MoveId=Spec.MoveId; Out.Score=T.Score; }
        }
        Out.Traces.Add(T);
    }
    // BOSS-SEL-005: with TieBand > 0 one eligible card of the top tier (score >= best * (1 - TieBand)) is picked with a seeded stream; TieBand 0 keeps the deterministic rule.
    if (Config.TieBand>0.f && Out.ChosenIndex!=INDEX_NONE)
    {
        TArray<int32> Tier; const float Threshold=Out.Score*(1.f-Config.TieBand);
        for (const FRPGBossSelectorTrace& T:Out.Traces) if (T.bEligible && T.Score>=Threshold) Tier.Add(T.Index);
        if (Tier.Num()>1)
        {
            FRandomStream Stream(Config.TieSeed+StartedCount);
            const int32 Pick=Tier[Stream.RandRange(0,Tier.Num()-1)];
            Out.ChosenIndex=Pick; Out.MoveId=Out.Traces[Pick].MoveId; Out.Score=Out.Traces[Pick].Score;
        }
    }
    return true;
}
void FRPGBossMoveSelector::NoteStarted(int32 Index, double ClockSeconds)
{
    if (!bInitialized || !Candidates.IsValidIndex(Index) || !FMath::IsFinite(ClockSeconds) || ClockSeconds<0.0) return;
    LastStartClock[Index]=ClockSeconds; ++StartedCount;
    Recent.Remove(Index); Recent.Add(Index);
    while (Recent.Num()>Config.RepeatMemory) Recent.RemoveAt(0);
}
void FRPGBossMoveSelector::Reset()
{
    if (!bInitialized) return;
    LastStartClock.Init(-1.0,Candidates.Num()); Recent.Reset(); StartedCount=0; ConeInside.Reset();
}
