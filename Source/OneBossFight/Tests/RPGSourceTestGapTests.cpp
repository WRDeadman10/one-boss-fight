// Copyright One Boss Fight. All Rights Reserved.

#include "Misc/AutomationTest.h"
#include "Arena/RPGPerfSwitches.h"
#include "Benchmark/RPGBenchmarkRunner.h"
#include "Pack/RPGHideBones.h"
#include "Player/RPGCameraProbe.h"
#include "Player/RPGBossInterrupt.h"
#include "Player/RPGPlayerParry.h"
#include "Player/RPGRiposteInput.h"
#include "UI/RPGFlaskHud.h"
#include "HAL/IConsoleManager.h"

#if WITH_DEV_AUTOMATION_TESTS

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FRPGPlayerParryComponentContractTest,
    "OneBossFight.Player.Parry.ComponentContract", EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)
bool FRPGPlayerParryComponentContractTest::RunTest(const FString& Parameters)
{
    URPGPlayerParry* Parry = NewObject<URPGPlayerParry>();
    TestNotNull(TEXT("parry component constructs"), Parry);
    if (!Parry) return false;
    TestTrue(TEXT("first press opens the timing window"), Parry->Press());
    TestTrue(TEXT("window is open at its opening instant"), Parry->IsWindowOpen());
    TestEqual(TEXT("accepted and rejected attempts are counted"), Parry->PressCount, 1);
    TestFalse(TEXT("a second press during cooldown is rejected"), Parry->Press());
    TestEqual(TEXT("the rejected attempt is counted"), Parry->PressCount, 2);

    AActor* Player = NewObject<AActor>();
    URPGPlayerParry* OwnedParry = NewObject<URPGPlayerParry>(Player);
    if (Player && OwnedParry)
    {
        Player->AddInstanceComponent(OwnedParry);
        OwnedParry->Press();
        URPGPlayerParry::NotifyParried(Player);
        TestEqual(TEXT("one confirmed contact increments the successful-parry counter exactly once"), OwnedParry->ParriedCount, 1);
        TestEqual(TEXT("the successful contact records its timing grade"), OwnedParry->LastGradeName(), FString(TEXT("Perfect")));
    }
    else
    {
        AddError(TEXT("could not create the actor-owned parry fixture"));
    }

    URPGPlayerParry* Invalid = NewObject<URPGPlayerParry>();
    Invalid->WindowSeconds = 0.f;
    TestFalse(TEXT("non-positive window cannot open"), Invalid->Press());
    TestFalse(TEXT("invalid window remains closed"), Invalid->IsWindowOpen());
    return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FRPGCameraProbeWorldSupportTest,
    "OneBossFight.Camera.Probe.WorldSupport", EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)
bool FRPGCameraProbeWorldSupportTest::RunTest(const FString& Parameters)
{
    URPGCameraProbe* Probe = NewObject<URPGCameraProbe>();
    TestNotNull(TEXT("camera probe constructs"), Probe);
    if (!Probe) return false;
    TestTrue(TEXT("supports standalone game worlds"), Probe->DoesSupportWorldType(EWorldType::Game));
    TestTrue(TEXT("supports PIE worlds"), Probe->DoesSupportWorldType(EWorldType::PIE));
    TestFalse(TEXT("does not tick editor worlds"), Probe->DoesSupportWorldType(EWorldType::Editor));
    return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FRPGRiposteInputDefaultsTest,
    "OneBossFight.Player.RiposteInput.Defaults", EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)
bool FRPGRiposteInputDefaultsTest::RunTest(const FString& Parameters)
{
    URPGRiposteInput* Input = NewObject<URPGRiposteInput>();
    TestNotNull(TEXT("riposte input component constructs"), Input);
    if (!Input) return false;
    TestEqual(TEXT("press count starts at zero"), Input->GetPressCount(), 0);
    TestEqual(TEXT("accepted riposte count starts at zero"), Input->GetAcceptedCount(), 0);
    TestTrue(TEXT("light attack action path is configured"), Input->LightAttackAction.ToSoftObjectPath().ToString().EndsWith(TEXT("IA_NormalAttack.IA_NormalAttack")));
    return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FRPGHideBonesDefaultsTest,
    "OneBossFight.Pack.HideBones.Defaults", EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)
bool FRPGHideBonesDefaultsTest::RunTest(const FString& Parameters)
{
    URPGHideBones* HideBones = NewObject<URPGHideBones>();
    TestNotNull(TEXT("hide-bones component constructs"), HideBones);
    if (!HideBones) return false;
    TestTrue(TEXT("default component hides no bones"), HideBones->BoneNames.IsEmpty());
    return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FRPGFlaskHudInitialStateTest,
    "OneBossFight.UI.FlaskHud.InitialState", EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)
bool FRPGFlaskHudInitialStateTest::RunTest(const FString& Parameters)
{
    URPGFlaskHud* Hud = NewObject<URPGFlaskHud>();
    TestNotNull(TEXT("flask HUD component constructs"), Hud);
    if (!Hud) return false;
    TestEqual(TEXT("count is unavailable before the live pack item is read"), Hud->GetFlaskCount(), -1);
    TestEqual(TEXT("maximum is unset before BeginPlay"), Hud->GetFlaskMaximum(), 0);
    TestEqual(TEXT("fill state is unavailable before initialization"), Hud->GetFlaskFillState(), FString(TEXT("Unavailable")));
    TestFalse(TEXT("overlay is hidden before widget creation"), Hud->IsOverlayShown());
    return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FRPGBenchmarkRunnerNoWorldTest,
    "OneBossFight.Benchmark.RunnerNoWorld", EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)
bool FRPGBenchmarkRunnerNoWorldTest::RunTest(const FString& Parameters)
{
    ARPGBenchmarkRunner* Runner = NewObject<ARPGBenchmarkRunner>();
    TestNotNull(TEXT("benchmark runner constructs"), Runner);
    if (!Runner) return false;
    TestFalse(TEXT("runner is idle initially"), Runner->IsRunning());
    TestEqual(TEXT("default warmup remains five seconds"), Runner->WarmupSeconds, 5.f);
    TestEqual(TEXT("default recording duration remains sixty seconds"), Runner->DurationSeconds, 60.f);
    Runner->StartBenchmark();
    TestFalse(TEXT("start without a world is a safe no-op"), Runner->IsRunning());
    Runner->AbortBenchmark();
    TestFalse(TEXT("abort while idle remains a no-op"), Runner->IsRunning());
    return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FRPGPerfFireRadiusScaleClampTest,
    "OneBossFight.Performance.FireRadiusScaleClamp", EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)
bool FRPGPerfFireRadiusScaleClampTest::RunTest(const FString& Parameters)
{
#if UE_BUILD_SHIPPING
    TestEqual(TEXT("Shipping fixes the experiment scale at authored radius"), RPGPerf::FireRadiusScale(), 1.f);
#else
    IConsoleVariable* Variable = IConsoleManager::Get().FindConsoleVariable(TEXT("rpg.Perf.FireRadiusScale"));
    TestNotNull(TEXT("Development experiment CVar is registered"), Variable);
    if (!Variable) return false;
    const float Previous = Variable->GetFloat();
    Variable->Set(2.f, ECVF_SetByCode);
    TestEqual(TEXT("scale clamps to its upper bound"), RPGPerf::FireRadiusScale(), 1.25f);
    Variable->Set(0.1f, ECVF_SetByCode);
    TestEqual(TEXT("scale clamps to its lower bound"), RPGPerf::FireRadiusScale(), 0.25f);
    Variable->Set(1.f, ECVF_SetByCode);
    TestEqual(TEXT("one preserves the authored radius"), RPGPerf::FireRadiusScale(), 1.f);
    Variable->Set(Previous, ECVF_SetByCode);
#endif
    return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FRPGBossInterruptNoComponentsTest,
    "OneBossFight.Combat.InterruptNoComponents", EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)
bool FRPGBossInterruptNoComponentsTest::RunTest(const FString& Parameters)
{
    AActor* EmptyBoss = NewObject<AActor>();
    TestNotNull(TEXT("empty actor fixture constructs"), EmptyBoss);
    if (!EmptyBoss) return false;
    RPGBossInterrupt::CancelOffence(EmptyBoss, TEXT("automation empty-fixture"));
    RPGBossInterrupt::CancelOffence(EmptyBoss, TEXT("automation repeated empty-fixture"));
    TestTrue(TEXT("empty-fixture cancellation is safe and repeatable"), true);
    RPGBossInterrupt::CancelOffence(nullptr, TEXT("automation null-fixture"));
    TestTrue(TEXT("null actor cancellation is a safe no-op"), true);
    return true;
}

#endif
