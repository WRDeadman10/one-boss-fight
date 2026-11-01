// Copyright One Boss Fight. All Rights Reserved.
#include "Player/RPGBossComboRules.h"
#include "Misc/AutomationTest.h"
#include <limits>

#if WITH_DEV_AUTOMATION_TESTS
namespace BossComboFixture
{
using namespace RPGBossCombo;
FComboEdge Edge(const TCHAR* To,float MinR,float MaxR,float Yaw,bool bAny,EOutcome Out=EOutcome::Hit)
{ FComboEdge E; E.To=To; E.MinRangeCm=MinR; E.MaxRangeCm=MaxR; E.MaxAbsYawDegrees=Yaw; E.bAnyOutcome=bAny; E.Outcome=Out; return E; }
FComboNode Node(const TCHAR* Id,const TCHAR* Move,TArray<FComboEdge> Edges={}) { FComboNode N; N.Id=Id; N.MoveId=Move; N.Edges=Edges; return N; }
// A (root): Hit within 0..250 cm and 60 deg -> B; Whiff -> C; Guarded -> D. B: anything within 0..300 cm -> E. C, D, E terminal. Longest path A-B-E = 3 nodes.
FComboGraph Valid()
{
    FComboGraph G; G.Root=TEXT("A"); G.MaxDepth=3;
    G.Nodes.Add(Node(TEXT("A"),TEXT("MoveA"),{Edge(TEXT("B"),0.f,250.f,60.f,false,EOutcome::Hit),Edge(TEXT("C"),0.f,1.e6f,180.f,false,EOutcome::Whiff),Edge(TEXT("D"),0.f,1.e6f,180.f,false,EOutcome::Guarded)}));
    G.Nodes.Add(Node(TEXT("B"),TEXT("MoveB"),{Edge(TEXT("E"),0.f,300.f,180.f,true)}));
    G.Nodes.Add(Node(TEXT("C"),TEXT("MoveC")));G.Nodes.Add(Node(TEXT("D"),TEXT("MoveD")));G.Nodes.Add(Node(TEXT("E"),TEXT("MoveE")));
    return G;
}
FComboGate Gate(uint64 Id,double Range,double Yaw,EOutcome Out=EOutcome::Hit) { FComboGate G; G.GateId=Id; G.RangeCm=Range; G.SignedYawDegrees=Yaw; G.Outcome=Out; G.bTargetValid=true; return G; }
}
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FBossComboValidate,"OneBossFight.Framework.Combo.Validate",EAutomationTestFlags::EditorContext|EAutomationTestFlags::ProductFilter)
bool FBossComboValidate::RunTest(const FString&)
{
    using namespace BossComboFixture;
    TestTrue(TEXT("valid graph"),Validate(Valid()).IsEmpty());
    TestEqual(TEXT("longest path in nodes"),LongestPath(Valid()),3);
    auto Token=[&](TFunction<void(FComboGraph&)> Edit){FComboGraph G=Valid();Edit(G);return Validate(G);};
    TestEqual(TEXT("no nodes"),Validate(FComboGraph()),FString(TEXT("Combo.Empty")));
    TestEqual(TEXT("root missing"),Token([](FComboGraph& G){G.Root=TEXT("Zed");}),FString(TEXT("Combo.Root")));
    TestEqual(TEXT("duplicate node"),Token([](FComboGraph& G){G.Nodes.Add(Node(TEXT("C"),TEXT("Other")));}),FString(TEXT("Combo.DuplicateNode")));
    TestEqual(TEXT("unknown edge target"),Token([](FComboGraph& G){G.Nodes[1].Edges[0].To=TEXT("Zed");}),FString(TEXT("Combo.UnknownNode")));
    TestEqual(TEXT("node without a move"),Token([](FComboGraph& G){G.Nodes[2].MoveId=NAME_None;}),FString(TEXT("Combo.UnknownNode")));
    TestEqual(TEXT("range band reversed"),Token([](FComboGraph& G){G.Nodes[0].Edges[0].MinRangeCm=300.f;}),FString(TEXT("Combo.EdgeDomain")));
    TestEqual(TEXT("yaw above 180"),Token([](FComboGraph& G){G.Nodes[0].Edges[0].MaxAbsYawDegrees=181.f;}),FString(TEXT("Combo.EdgeDomain")));
    TestEqual(TEXT("NaN range"),Token([](FComboGraph& G){G.Nodes[0].Edges[0].MaxRangeCm=std::numeric_limits<float>::quiet_NaN();}),FString(TEXT("Combo.EdgeDomain")));
    TestEqual(TEXT("cycle E -> A"),Token([](FComboGraph& G){G.Nodes[4].Edges.Add(Edge(TEXT("A"),0.f,100.f,180.f,true));}),FString(TEXT("Combo.Cycle")));
    TestEqual(TEXT("cycle between two nodes the root cannot reach"),Token([](FComboGraph& G){G.Nodes.Add(Node(TEXT("X"),TEXT("MoveX"),{Edge(TEXT("Y"),0.f,100.f,180.f,true)}));G.Nodes.Add(Node(TEXT("Y"),TEXT("MoveY"),{Edge(TEXT("X"),0.f,100.f,180.f,true)}));}),FString(TEXT("Combo.Cycle")));
    TestTrue(TEXT("an orphan node without a cycle stays valid"),Token([](FComboGraph& G){G.Nodes.Add(Node(TEXT("Z"),TEXT("MoveZ")));}).IsEmpty());
    TestEqual(TEXT("self loop"),Token([](FComboGraph& G){G.Nodes[2].Edges.Add(Edge(TEXT("C"),0.f,100.f,180.f,true));}),FString(TEXT("Combo.Cycle")));
    TestEqual(TEXT("four nodes deep with max depth 3"),Token([](FComboGraph& G){G.Nodes.Add(Node(TEXT("F"),TEXT("MoveF")));G.Nodes[4].Edges.Add(Edge(TEXT("F"),0.f,100.f,180.f,true));}),FString(TEXT("Combo.Depth")));
    TestEqual(TEXT("max depth 4 is outside 1..3"),Token([](FComboGraph& G){G.MaxDepth=4;}),FString(TEXT("Combo.MaxDepth")));
    TestEqual(TEXT("max depth 0 is outside 1..3"),Token([](FComboGraph& G){G.MaxDepth=0;}),FString(TEXT("Combo.MaxDepth")));
    TestTrue(TEXT("max depth 3 with three nodes is exactly enough"),Token([](FComboGraph& G){G.MaxDepth=3;}).IsEmpty());
    TestEqual(TEXT("max depth 2 is too small for a three node path"),Token([](FComboGraph& G){G.MaxDepth=2;}),FString(TEXT("Combo.Depth")));
    return true;
}
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FBossComboStep,"OneBossFight.Framework.Combo.Step",EAutomationTestFlags::EditorContext|EAutomationTestFlags::ProductFilter)
bool FBossComboStep::RunTest(const FString&)
{
    using namespace BossComboFixture;
    const FComboGraph G=Valid();
    // COM-001/006: walk the longest path A -> B -> E, then the terminal node finishes the combo.
    {
        FComboState S;S.Node=TEXT("A");
        FComboStep R=Step(G,S,Gate(1,100.,10.));TestTrue(TEXT("hit in front within range: continue"),R.Kind==EStep::Continue);TestEqual(TEXT("to B"),R.NextNode,FName(TEXT("B")));TestEqual(TEXT("depth 2"),S.Depth,2);
        R=Step(G,S,Gate(2,100.,170.));TestTrue(TEXT("B takes any outcome and any yaw: continue"),R.Kind==EStep::Continue);TestEqual(TEXT("to E"),R.NextNode,FName(TEXT("E")));TestEqual(TEXT("depth 3"),S.Depth,3);
        R=Step(G,S,Gate(3,100.,10.));TestTrue(TEXT("terminal node finishes"),R.Kind==EStep::Finished);
    }
    // COM-005: a gate id is consumed once; the duplicate is ignored and does not change the state.
    {
        FComboState S;S.Node=TEXT("A");Step(G,S,Gate(7,100.,10.));
        const FComboState After=S;FComboStep R=Step(G,S,Gate(7,100.,10.));
        TestTrue(TEXT("duplicate gate ignored"),R.Kind==EStep::Ignored);TestTrue(TEXT("state untouched"),S.Node==After.Node&&S.Depth==After.Depth&&S.LastGateId==After.LastGateId);
        TestEqual(TEXT("gate id 0 is refused"),Step(G,S,Gate(0,100.,10.)).Reason,FString(TEXT("Combo.GateId")));
    }
    // COM-003: only the snapshot of THIS gate counts: in front the combo continues, behind the boss it recovers.
    {
        FComboState Front;Front.Node=TEXT("A");TestTrue(TEXT("in front: continue"),Step(G,Front,Gate(1,100.,10.)).Kind==EStep::Continue);
        FComboState Behind;Behind.Node=TEXT("A");FComboStep R=Step(G,Behind,Gate(1,100.,170.));
        TestTrue(TEXT("rolled behind: recover"),R.Kind==EStep::Recover);TestEqual(TEXT("default recovery"),R.Reason,FString(TEXT("Combo.DefaultRecovery")));
    }
    // COM-004: whiff, guard and parry branch differently.
    {
        FComboState S;S.Node=TEXT("A");FComboStep R=Step(G,S,Gate(1,100.,10.,EOutcome::Whiff));TestEqual(TEXT("whiff -> C"),R.NextNode,FName(TEXT("C")));
        FComboState T;T.Node=TEXT("A");R=Step(G,T,Gate(1,100.,10.,EOutcome::Guarded));TestEqual(TEXT("guarded -> D"),R.NextNode,FName(TEXT("D")));
        FComboState U;U.Node=TEXT("A");R=Step(G,U,Gate(1,100.,10.,EOutcome::Parried));TestTrue(TEXT("parried: no edge, recover"),R.Kind==EStep::Recover);TestEqual(TEXT("default recovery"),R.Reason,FString(TEXT("Combo.DefaultRecovery")));
    }
    // COM-007: out of range recovers cleanly (hit at 300 cm, band is 0..250).
    {
        FComboState S;S.Node=TEXT("A");FComboStep R=Step(G,S,Gate(1,300.,10.));TestTrue(TEXT("out of range: recover"),R.Kind==EStep::Recover);TestEqual(TEXT("default recovery"),R.Reason,FString(TEXT("Combo.DefaultRecovery")));
        FComboState Edge;Edge.Node=TEXT("A");TestTrue(TEXT("exactly 250 cm is in"),Step(G,Edge,Gate(1,250.,60.)).Kind==EStep::Continue);
    }
    // Bad gates: invalid target and non-finite snapshot recover without a branch.
    {
        FComboState S;S.Node=TEXT("A");FComboGate Bad=Gate(1,100.,10.);Bad.bTargetValid=false;TestEqual(TEXT("invalid target"),Step(G,S,Bad).Reason,FString(TEXT("Combo.Target")));
        FComboState T;T.Node=TEXT("A");FComboGate Nan=Gate(1,std::numeric_limits<double>::quiet_NaN(),10.);TestEqual(TEXT("NaN range"),Step(G,T,Nan).Reason,FString(TEXT("Combo.Target")));
        FComboState U;U.Node=TEXT("Zed");TestEqual(TEXT("unknown current node"),Step(G,U,Gate(1,100.,10.)).Reason,FString(TEXT("Combo.UnknownNode")));
    }
    // COM-006: the depth guard stops a path longer than MaxDepth even if the graph were not validated (MaxDepth 2 on the A-B-E path).
    {
        FComboGraph Short=Valid();Short.MaxDepth=2;FComboState S;S.Node=TEXT("A");Step(Short,S,Gate(1,100.,10.));
        FComboStep R=Step(Short,S,Gate(2,100.,10.));TestTrue(TEXT("third node refused"),R.Kind==EStep::Recover);TestEqual(TEXT("depth token"),R.Reason,FString(TEXT("Combo.Depth")));
    }
    return true;
}
#endif
