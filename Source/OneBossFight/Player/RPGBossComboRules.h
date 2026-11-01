// Copyright One Boss Fight. All Rights Reserved.
#pragma once
#include "CoreMinimal.h"
/**
 * Combo graph rules of the framework boss (BOSS-COM-001, 003, 004, 005, 006, 007). Header only, no UObject, so the boss and the automation tests share them.
 * A graph is a directed acyclic graph of nodes (each plays one move card); a node without edges is terminal. At every branch gate the boss decides with ONLY the gate snapshot it is given
 * (fresh context): the first edge, in authored order, whose range band, yaw cone and hit outcome all match is taken. No match = default recovery. A gate id is consumed once.
 */
namespace RPGBossCombo
{
    enum class EOutcome : uint8 { Hit, Whiff, Guarded, Parried };
    struct FComboEdge
    {
        FName To;
        float MinRangeCm=0.f, MaxRangeCm=1.e6f, MaxAbsYawDegrees=180.f;
        bool bAnyOutcome=true; EOutcome Outcome=EOutcome::Hit;   // bAnyOutcome: the outcome does not matter
        float TempoPauseSeconds=0.f;   // BOSS-PAC-002: the boss waits this long (neutral) before the next card of the combo starts; 0..5
    };
    struct FComboNode { FName Id, MoveId; TArray<FComboEdge> Edges; };
    struct FComboGraph { FName Root; TArray<FComboNode> Nodes; int32 MaxDepth=3; };
    struct FComboGate { double RangeCm=0., SignedYawDegrees=0.; EOutcome Outcome=EOutcome::Hit; bool bTargetValid=false; uint64 GateId=0; };
    struct FComboState { FName Node; int32 Depth=1; uint64 LastGateId=0; };
    enum class EStep : uint8 { Continue, Recover, Finished, Ignored };
    struct FComboStep { EStep Kind=EStep::Recover; FName NextNode; FString Reason; float PauseSeconds=0.f; };

    inline int32 FindNode(const FComboGraph& G,FName Id) { for (int32 I=0;I<G.Nodes.Num();++I) if (G.Nodes[I].Id==Id) return I; return INDEX_NONE; }

    /** Longest root-to-terminal path counted in nodes; -1 when a cycle or an unknown node makes it undefined. */
    inline int32 LongestPathFrom(const FComboGraph& G,int32 Start)
    {
        TArray<int32> Memo; Memo.Init(0,G.Nodes.Num()); TArray<uint8> Color; Color.Init(0,G.Nodes.Num());   // 0 new, 1 visiting, 2 done
        TFunction<int32(int32)> Visit=[&](int32 I)->int32
        {
            if (Color[I]==2) return Memo[I];
            if (Color[I]==1) return -1;
            Color[I]=1; int32 Best=1;
            for (const FComboEdge& E:G.Nodes[I].Edges)
            {
                const int32 To=FindNode(G,E.To); if (To==INDEX_NONE) return -1;
                const int32 Sub=Visit(To); if (Sub<0) return -1;
                Best=FMath::Max(Best,1+Sub);
            }
            Color[I]=2; Memo[I]=Best; return Best;
        };
        return Start==INDEX_NONE ? -1 : Visit(Start);
    }
    inline int32 LongestPath(const FComboGraph& G) { return LongestPathFrom(G,FindNode(G,G.Root)); }

    /** Empty = valid, else the failure token. Order: Empty, MaxDepth (1..3), Root, DuplicateNode, UnknownNode, EdgeDomain, Cycle, Depth (longest path in nodes > MaxDepth). */
    inline FString Validate(const FComboGraph& G)
    {
        if (G.Nodes.Num()==0) return TEXT("Combo.Empty");
        if (G.MaxDepth<1 || G.MaxDepth>3) return TEXT("Combo.MaxDepth");
        if (FindNode(G,G.Root)==INDEX_NONE) return TEXT("Combo.Root");
        TSet<FName> Ids;
        for (const FComboNode& N:G.Nodes) { bool bDup=false; Ids.Add(N.Id,&bDup); if (N.Id.IsNone()||bDup) return TEXT("Combo.DuplicateNode"); }
        for (const FComboNode& N:G.Nodes)
        {
            if (N.MoveId.IsNone()) return TEXT("Combo.UnknownNode");
            for (const FComboEdge& E:N.Edges) if (!Ids.Contains(E.To)) return TEXT("Combo.UnknownNode");
        }
        for (const FComboNode& N:G.Nodes)
            for (const FComboEdge& E:N.Edges)
                if (!FMath::IsFinite(E.MinRangeCm)||!FMath::IsFinite(E.MaxRangeCm)||!FMath::IsFinite(E.MaxAbsYawDegrees)||E.MinRangeCm<0.f||E.MinRangeCm>E.MaxRangeCm||E.MaxAbsYawDegrees<0.f||E.MaxAbsYawDegrees>180.f||!FMath::IsFinite(E.TempoPauseSeconds)||E.TempoPauseSeconds<0.f||E.TempoPauseSeconds>5.f)
                    return TEXT("Combo.EdgeDomain");
        // A cycle anywhere in the graph is refused, also in nodes the root cannot reach (Codex X-374 finding 3).
        for (int32 I=0;I<G.Nodes.Num();++I) if (LongestPathFrom(G,I)<0) return TEXT("Combo.Cycle");
        const int32 Longest=LongestPath(G);
        if (Longest>G.MaxDepth) return TEXT("Combo.Depth");
        return FString();
    }

    /** One branch gate. A gate id already used is Ignored without touching the state; id 0 and an invalid target recover. */
    inline FComboStep Step(const FComboGraph& G,FComboState& S,const FComboGate& Gate)
    {
        FComboStep R; const int32 I=FindNode(G,S.Node);
        if (I==INDEX_NONE) { R.Reason=TEXT("Combo.UnknownNode"); return R; }
        if (Gate.GateId==0) { R.Reason=TEXT("Combo.GateId"); return R; }
        if (Gate.GateId==S.LastGateId) { R.Kind=EStep::Ignored; R.Reason=TEXT("Combo.GateConsumed"); return R; }
        S.LastGateId=Gate.GateId;
        if (!Gate.bTargetValid||!FMath::IsFinite(Gate.RangeCm)||!FMath::IsFinite(Gate.SignedYawDegrees)) { R.Reason=TEXT("Combo.Target"); return R; }
        const FComboNode& N=G.Nodes[I];
        if (N.Edges.Num()==0) { R.Kind=EStep::Finished; return R; }
        for (const FComboEdge& E:N.Edges)
        {
            if (Gate.RangeCm<E.MinRangeCm||Gate.RangeCm>E.MaxRangeCm||FMath::Abs(Gate.SignedYawDegrees)>E.MaxAbsYawDegrees) continue;
            if (!E.bAnyOutcome&&E.Outcome!=Gate.Outcome) continue;
            if (S.Depth+1>G.MaxDepth) { R.Reason=TEXT("Combo.Depth"); return R; }
            S.Node=E.To; ++S.Depth; R.Kind=EStep::Continue; R.NextNode=E.To; R.PauseSeconds=E.TempoPauseSeconds; return R;
        }
        R.Reason=TEXT("Combo.DefaultRecovery"); return R;
    }
}
