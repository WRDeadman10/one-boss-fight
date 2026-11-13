// Copyright One Boss Fight. All Rights Reserved.
#include "Player/RPGNativeBossHealth.h"
#include "Boss/RPGFrameworkBossCharacter.h"
#include "UI/RPGBossHud.h"
#include "Misc/AutomationTest.h"
#include <limits>

#if WITH_DEV_AUTOMATION_TESTS
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FBossHealthPresentationSnapshot, "OneBossFight.BossHealth.PresentationSnapshot", EAutomationTestFlags::EditorContext | EAutomationTestFlags::ProductFilter)
bool FBossHealthPresentationSnapshot::RunTest(const FString&)
{
    using RPGBossHealthPresentation::Fraction;
    using RPGBossHealthPresentation::IsSnapshotValid;
    using RPGBossHealthPresentation::IsVictory;
    using RPGBossTerminalRules::ShouldAccept;
    TestTrue(TEXT("native and pack snapshots share positive finite contract"), IsSnapshotValid(75.0, 100.0));
    TestFalse(TEXT("zero maximum is rejected"), IsSnapshotValid(0.0, 0.0));
    TestFalse(TEXT("negative maximum is rejected"), IsSnapshotValid(10.0, -100.0));
    TestTrue(TEXT("finite overkill health remains a valid terminal snapshot"), IsSnapshotValid(-1.0, 100.0));
    TestFalse(TEXT("non-finite health is rejected"), IsSnapshotValid(std::numeric_limits<double>::quiet_NaN(), 100.0));
    TestFalse(TEXT("non-finite maximum is rejected"), IsSnapshotValid(10.0, std::numeric_limits<double>::infinity()));
    TestEqual(TEXT("health fraction clamps to full"), Fraction(120.0, 100.0), 1.f);
    TestEqual(TEXT("health fraction for partial health"), Fraction(25.0, 100.0), 0.25f);
    TestEqual(TEXT("negative overkill health clamps to empty bar"), Fraction(-1.0, 100.0), 0.f);
    TestFalse(TEXT("initial zero does not signal victory before alive was observed"), IsVictory(true, 0.0, false));
    TestTrue(TEXT("observed live participant at zero is terminal"), IsVictory(true, 0.0, true));
    TestFalse(TEXT("negative infinity cannot signal victory"), IsVictory(true, -std::numeric_limits<double>::infinity(), true));
    TestFalse(TEXT("missing provider never signals victory"), IsVictory(false, 0.0, true));
    TestTrue(TEXT("terminal event is accepted for the current live generation"), ShouldAccept(7, 7, 0, true, 0.0));
    TestFalse(TEXT("duplicate terminal event is refused for a completed generation"), ShouldAccept(7, 7, 7, true, 0.0));
    TestFalse(TEXT("terminal event is refused when completion state is already newer"), ShouldAccept(7, 7, 8, true, 0.0));
    TestFalse(TEXT("stale terminal event is refused after generation advance"), ShouldAccept(8, 7, 0, true, 0.0));
    TestFalse(TEXT("terminal event with positive health is refused"), ShouldAccept(7, 7, 0, true, 1.0));
    TestFalse(TEXT("retry stays hidden while disabled"), RPGBossRetryPresentation::ShouldShow(false, 10.0, 0.0));
    TestFalse(TEXT("retry stays hidden before its delay"), RPGBossRetryPresentation::ShouldShow(true, 2.99, 3.0));
    TestTrue(TEXT("retry appears at the authored delay boundary"), RPGBossRetryPresentation::ShouldShow(true, 3.0, 3.0));
    TestFalse(TEXT("retry fails closed on a non-finite clock"), RPGBossRetryPresentation::ShouldShow(true, std::numeric_limits<double>::infinity(), 3.0));
    ARPGFrameworkBossCharacter* TerminalBoss = NewObject<ARPGFrameworkBossCharacter>(GetTransientPackage());
    URPGBossHud* NativeHud = TerminalBoss ? NewObject<URPGBossHud>(TerminalBoss) : nullptr;
    TestNotNull(TEXT("transient native boss for HUD terminal route"), TerminalBoss);
    TestNotNull(TEXT("native HUD component"), NativeHud);
    if (TerminalBoss && NativeHud)
    {
        TerminalBoss->GenerationId = 7;
        TerminalBoss->bHittable = true;
        TerminalBoss->Health = 0.0;
        TerminalBoss->MaxHealth = 100.0;
        NativeHud->HandleNativeTerminal(TerminalBoss, 7);
        TestEqual(TEXT("HUD records the current autonomous generation's terminal callback"), NativeHud->NativeTerminalGeneration, uint64(7));
        TestTrue(TEXT("accepted terminal callback latches a previously alive fight"), NativeHud->bSeenAlive);
        NativeHud->HandleNativeTerminal(TerminalBoss, 7);
        TestEqual(TEXT("duplicate callback cannot advance HUD completion"), NativeHud->NativeTerminalGeneration, uint64(7));
        NativeHud->HandleNativeTerminal(TerminalBoss, 6);
        TestEqual(TEXT("stale callback cannot replace current HUD completion"), NativeHud->NativeTerminalGeneration, uint64(7));
        TestTrue(TEXT("terminal latch and zero health produce the existing victory state"), IsVictory(true, 0.0, NativeHud->bSeenAlive));

        TerminalBoss->GenerationId = 8;
        NativeHud->HandleNativeTerminal(TerminalBoss, 8);
        TestEqual(TEXT("replacement generation can complete after the prior generation"), NativeHud->NativeTerminalGeneration, uint64(8));
        NativeHud->HandleNativeTerminal(TerminalBoss, 7);
        TestEqual(TEXT("callback from the prior generation stays stale after replacement"), NativeHud->NativeTerminalGeneration, uint64(8));

        ARPGFrameworkBossCharacter* ReplacementBoss = NewObject<ARPGFrameworkBossCharacter>(GetTransientPackage());
        TestNotNull(TEXT("replacement actor for callback identity guard"), ReplacementBoss);
        if (ReplacementBoss)
        {
            ReplacementBoss->GenerationId = 9;
            NativeHud->HandleNativeTerminal(ReplacementBoss, 9);
            TestEqual(TEXT("old HUD refuses terminal callback from replacement actor"), NativeHud->NativeTerminalGeneration, uint64(8));
        }
    }
    const IRPGNativeBossHealth* Provider = Cast<IRPGNativeBossHealth>(ARPGFrameworkBossCharacter::StaticClass()->GetDefaultObject());
    TestNotNull(TEXT("framework boss exposes native health provider"), Provider);
    if (Provider)
    {
        double NativeHealth = 0.0;
        TestFalse(TEXT("uninitialized native boss has no readable health"), Provider->ReadNativeHealth(false, NativeHealth));
        TestFalse(TEXT("uninitialized native boss is not active"), Provider->IsNativeEncounterActive());
        TestEqual(TEXT("native generation comes from framework encounter owner"), Provider->NativeEncounterGeneration(), uint64(0));
    }
    return true;
}
#endif
