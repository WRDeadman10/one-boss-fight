// Copyright One Boss Fight. All Rights Reserved.
#include "Player/RPGBossComboRules.h"
#include "Misc/AutomationTest.h"
#include "Misc/FileHelper.h"
#include "Misc/Paths.h"
#include "Serialization/JsonReader.h"
#include "Serialization/JsonSerializer.h"

#if WITH_DEV_AUTOMATION_TESTS
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FBossComboParriedSample, "OneBossFight.Framework.Combo.ParriedSample", EAutomationTestFlags::EditorContext | EAutomationTestFlags::ProductFilter)
bool FBossComboParriedSample::RunTest(const FString&)
{
    const FString Path = FPaths::Combine(FPaths::ProjectDir(), TEXT("Docs/BossCombatReview/Execution/Codex/Samples/combo_parried_branch.json"));
    FString Text; TestTrue(TEXT("sample JSON is readable"), FFileHelper::LoadFileToString(Text, *Path));
    TSharedPtr<FJsonObject> Json; const TSharedRef<TJsonReader<>> Reader = TJsonReaderFactory<>::Create(Text);
    TestTrue(TEXT("sample JSON parses"), FJsonSerializer::Deserialize(Reader, Json) && Json.IsValid());
    if (!Json.IsValid()) return false;
    using namespace RPGBossCombo;
    FComboGraph Graph; Graph.Root = FName(*Json->GetStringField(TEXT("root"))); Graph.MaxDepth = Json->GetIntegerField(TEXT("maxDepth"));
    const TArray<TSharedPtr<FJsonValue>> Nodes = Json->GetArrayField(TEXT("nodes"));
    for (const TSharedPtr<FJsonValue>& Value : Nodes)
    {
        const TSharedPtr<FJsonObject> NodeJson = Value->AsObject(); FComboNode Node;
        Node.Id = FName(*NodeJson->GetStringField(TEXT("id"))); Node.MoveId = FName(*NodeJson->GetStringField(TEXT("moveId")));
        for (const TSharedPtr<FJsonValue>& EdgeValue : NodeJson->GetArrayField(TEXT("edges")))
        {
            const TSharedPtr<FJsonObject> E = EdgeValue->AsObject(); FComboEdge Edge;
            Edge.To = FName(*E->GetStringField(TEXT("to"))); Edge.MinRangeCm = E->GetNumberField(TEXT("minRangeCm")); Edge.MaxRangeCm = E->GetNumberField(TEXT("maxRangeCm"));
            Edge.MaxAbsYawDegrees = E->GetNumberField(TEXT("maxAbsYawDegrees")); Edge.bAnyOutcome = E->GetBoolField(TEXT("anyOutcome"));
            Edge.Outcome = E->GetStringField(TEXT("outcome")) == TEXT("Parried") ? EOutcome::Parried : EOutcome::Hit;
            Edge.TempoPauseSeconds = E->GetNumberField(TEXT("tempoPauseSeconds")); Node.Edges.Add(Edge);
        }
        Graph.Nodes.Add(MoveTemp(Node));
    }
    TestTrue(TEXT("loaded graph is valid"), Validate(Graph).IsEmpty());
    FComboState State; State.Node = Graph.Root; FComboGate Gate; Gate.RangeCm = 200.; Gate.SignedYawDegrees = 10.; Gate.Outcome = EOutcome::Parried; Gate.bTargetValid = true; Gate.GateId = 1;
    const FComboStep StepResult = Step(Graph, State, Gate);
    TestTrue(TEXT("Parried result reaches the declared follow-up"), StepResult.Kind == EStep::Continue && StepResult.NextNode == FName(TEXT("ParryFollow")));
    return true;
}
#endif
