// Copyright One Boss Fight. All Rights Reserved.
#include "Player/RPGBossComboRules.h"
#include "Misc/AutomationTest.h"

#if WITH_DEV_AUTOMATION_TESTS
namespace BossComboProperty
{
using namespace RPGBossCombo;
FComboGraph MakeGraph(FRandomStream& Random)
{
    FComboGraph G; G.Root=TEXT("N0"); G.MaxDepth=3;
    constexpr int32 MiddleCount=4, EndCount=4;
    FComboNode Root; Root.Id=TEXT("N0"); Root.MoveId=TEXT("M0");
    for (int32 I=0;I<MiddleCount;++I)
    {
        FComboEdge E; E.To=FName(*FString::Printf(TEXT("N%d"),I+1)); E.MinRangeCm=0.f; E.MaxRangeCm=float(Random.RandRange(50,1000)); E.MaxAbsYawDegrees=float(Random.RandRange(30,180));
        E.bAnyOutcome=(Random.RandRange(0,1)!=0); E.Outcome=static_cast<EOutcome>(Random.RandRange(0,3)); E.TempoPauseSeconds=float(Random.RandRange(0,500))/100.f; Root.Edges.Add(E);
    }
    G.Nodes.Add(Root);
    for (int32 I=0;I<MiddleCount;++I)
    {
        FComboNode Mid; Mid.Id=FName(*FString::Printf(TEXT("N%d"),I+1)); Mid.MoveId=FName(*FString::Printf(TEXT("M%d"),I+1));
        FComboEdge E; E.To=FName(*FString::Printf(TEXT("N%d"),MiddleCount+1+Random.RandRange(0,EndCount-1))); E.MinRangeCm=0.f; E.MaxRangeCm=float(Random.RandRange(50,1200)); E.MaxAbsYawDegrees=float(Random.RandRange(30,180));
        E.bAnyOutcome=(Random.RandRange(0,1)!=0); E.Outcome=static_cast<EOutcome>(Random.RandRange(0,3)); E.TempoPauseSeconds=float(Random.RandRange(0,500))/100.f; Mid.Edges.Add(E);
        G.Nodes.Add(Mid);
    }
    for (int32 I=0;I<EndCount;++I)
    {
        FComboNode End; End.Id=FName(*FString::Printf(TEXT("N%d"),MiddleCount+1+I)); End.MoveId=FName(*FString::Printf(TEXT("M%d"),MiddleCount+1+I)); G.Nodes.Add(End);
    }
    return G;
}
}
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FBossComboProperty,"OneBossFight.Framework.Combo.Property",EAutomationTestFlags::EditorContext|EAutomationTestFlags::ProductFilter)
bool FBossComboProperty::RunTest(const FString&)
{
    using namespace RPGBossCombo;
    FRandomStream Random(0x51A7);
    for (int32 Case=0;Case<1000;++Case)
    {
        const FComboGraph G=BossComboProperty::MakeGraph(Random);
        TestTrue(TEXT("generated graph validates"),Validate(G).IsEmpty());
        FComboState State; State.Node=G.Root;
        TSet<FName> Visited; Visited.Add(State.Node);
        for (uint64 GateId=1;GateId<=4;++GateId)
        {
            FComboGate Gate; Gate.GateId=GateId; Gate.RangeCm=double(Random.RandRange(0,1200)); Gate.SignedYawDegrees=double(Random.RandRange(-180,180)); Gate.Outcome=static_cast<EOutcome>(Random.RandRange(0,3)); Gate.bTargetValid=true;
            const FName Previous=State.Node;
            const FComboStep Result=Step(G,State,Gate);
            if (Result.Kind==EStep::Continue)
            {
                bool bDeclared=false;
                for (int32 I=0;I<G.Nodes[FindNode(G,Previous)].Edges.Num();++I) bDeclared|=G.Nodes[FindNode(G,Previous)].Edges[I].To==Result.NextNode;
                TestTrue(TEXT("Step only returns a declared reachable edge"),bDeclared);
                TestFalse(TEXT("Step never loops to an earlier or visited node"),Visited.Contains(Result.NextNode));
                TestTrue(TEXT("generated topological graph moves forward"),FindNode(G,Result.NextNode)>FindNode(G,Previous));
                Visited.Add(Result.NextNode);
            }
            else
            {
                TestTrue(TEXT("non-continue result cannot supply an unreachable next node"),Result.NextNode.IsNone());
                break;
            }
        }
    }
    return true;
}
#endif
