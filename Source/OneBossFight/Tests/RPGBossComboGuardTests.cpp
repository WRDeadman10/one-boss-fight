// Copyright One Boss Fight. All Rights Reserved.
// BL-18 (lane BL): RPGBossCombo cases confirmed untested (BL-01..05 audit): EdgeDomain for negative MinRangeCm / MaxAbsYawDegrees and infinite fields,
// a NAME_None node id, gate-id consumption when the Target check then fails, and an infinite gate yaw. Asserts existing behaviour only.
#include "Player/RPGBossComboRules.h"
#include "Misc/AutomationTest.h"
#include <limits>

#if WITH_DEV_AUTOMATION_TESTS
namespace BossComboGuardFixture
{
    using namespace RPGBossCombo;
    // Root A (move MA) -> B (move MB, terminal). Self-contained so it does not depend on another test file's fixture.
    inline FComboGraph Valid()
    {
        FComboGraph G; G.Root = TEXT("A"); G.MaxDepth = 3;
        FComboNode A; A.Id = TEXT("A"); A.MoveId = TEXT("MA");
        FComboEdge E; E.To = TEXT("B"); E.MinRangeCm = 0.f; E.MaxRangeCm = 500.f; E.MaxAbsYawDegrees = 90.f;
        A.Edges.Add(E);
        FComboNode B; B.Id = TEXT("B"); B.MoveId = TEXT("MB");
        G.Nodes = {A, B};
        return G;
    }
    inline FComboGate Gate(uint64 Id, double Range, double Yaw)
    {
        FComboGate Out; Out.GateId = Id; Out.RangeCm = Range; Out.SignedYawDegrees = Yaw; Out.bTargetValid = true; return Out;
    }
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FBossComboGuards, "OneBossFight.Framework.Combo.Guards", EAutomationTestFlags::EditorContext | EAutomationTestFlags::ProductFilter)
bool FBossComboGuards::RunTest(const FString&)
{
    using namespace BossComboGuardFixture;
    const float FInf = std::numeric_limits<float>::infinity();
    const double DInf = std::numeric_limits<double>::infinity();
    const FString EdgeDomain(TEXT("Combo.EdgeDomain"));

    TestTrue(TEXT("control: fixture graph is valid"), Validate(Valid()).IsEmpty());
    auto Token = [](TFunction<void(FComboGraph&)> Edit) { FComboGraph G = Valid(); Edit(G); return Validate(G); };

    // EdgeDomain: negative minimum range / yaw cone and infinite fields.
    TestEqual(TEXT("negative MinRangeCm"), Token([](FComboGraph& G) { G.Nodes[0].Edges[0].MinRangeCm = -1.f; }), EdgeDomain);
    TestEqual(TEXT("negative MaxAbsYawDegrees"), Token([](FComboGraph& G) { G.Nodes[0].Edges[0].MaxAbsYawDegrees = -1.f; }), EdgeDomain);
    TestEqual(TEXT("infinite MinRangeCm"), Token([FInf](FComboGraph& G) { G.Nodes[0].Edges[0].MinRangeCm = FInf; }), EdgeDomain);
    TestEqual(TEXT("infinite MaxRangeCm"), Token([FInf](FComboGraph& G) { G.Nodes[0].Edges[0].MaxRangeCm = FInf; }), EdgeDomain);
    TestEqual(TEXT("infinite MaxAbsYawDegrees"), Token([FInf](FComboGraph& G) { G.Nodes[0].Edges[0].MaxAbsYawDegrees = FInf; }), EdgeDomain);
    TestEqual(TEXT("infinite TempoPauseSeconds"), Token([FInf](FComboGraph& G) { G.Nodes[0].Edges[0].TempoPauseSeconds = FInf; }), EdgeDomain);
    // BL-86 note: +Inf MinRange / Yaw / Tempo above are also caught by Min>Max, >180 and >5, so only +Inf MaxRange pins an IsFinite clause.
    // NaN pins the remaining IsFinite clauses (NaN tempo and NaN MaxRange are already in RPGBossComboTests.cpp:38,45).
    const float FNaN = std::numeric_limits<float>::quiet_NaN();
    TestEqual(TEXT("NaN MinRangeCm (pins IsFinite)"), Token([FNaN](FComboGraph& G) { G.Nodes[0].Edges[0].MinRangeCm = FNaN; }), EdgeDomain);
    TestEqual(TEXT("NaN MaxAbsYawDegrees (pins IsFinite)"), Token([FNaN](FComboGraph& G) { G.Nodes[0].Edges[0].MaxAbsYawDegrees = FNaN; }), EdgeDomain);

    // A node whose id is NAME_None is refused as DuplicateNode (the root stays A, so the Root check passes first).
    TestEqual(TEXT("NAME_None node id"), Token([](FComboGraph& G) { FComboNode N; N.MoveId = TEXT("MZ"); G.Nodes.Add(N); }), FString(TEXT("Combo.DuplicateNode")));

    // Gate consumption: the id is stored BEFORE the target check, so a gate that fails Target is still consumed.
    {
        const FComboGraph G = Valid();
        FComboState S; S.Node = TEXT("A");
        FComboGate Bad = Gate(7, 100., 10.); Bad.bTargetValid = false;
        TestEqual(TEXT("invalid target recovers with Combo.Target"), Step(G, S, Bad).Reason, FString(TEXT("Combo.Target")));
        TestTrue(TEXT("the failed gate id is consumed"), S.LastGateId == uint64(7));
        TestTrue(TEXT("the node is unchanged"), S.Node == FName(TEXT("A")) && S.Depth == 1);
        const FComboStep Again = Step(G, S, Gate(7, 100., 10.));
        TestTrue(TEXT("replaying the consumed id (now with a valid target) is Ignored"), Again.Kind == EStep::Ignored);
        TestEqual(TEXT("ignored reason"), Again.Reason, FString(TEXT("Combo.GateConsumed")));
    }
    // An infinite gate yaw is Combo.Target (control: a finite yaw continues).
    {
        const FComboGraph G = Valid();
        FComboState Ok; Ok.Node = TEXT("A");
        TestTrue(TEXT("control: finite yaw continues"), Step(G, Ok, Gate(1, 100., 10.)).Kind == EStep::Continue);
        FComboState S; S.Node = TEXT("A");
        TestEqual(TEXT("+Inf yaw is Combo.Target"), Step(G, S, Gate(2, 100., DInf)).Reason, FString(TEXT("Combo.Target")));
        FComboState T; T.Node = TEXT("A");
        TestEqual(TEXT("-Inf yaw is Combo.Target"), Step(G, T, Gate(3, 100., -DInf)).Reason, FString(TEXT("Combo.Target")));
    }
    return true;
}
#endif
