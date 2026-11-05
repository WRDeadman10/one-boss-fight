// Copyright One Boss Fight. All Rights Reserved.
#include "Misc/AutomationTest.h"

#if WITH_DEV_AUTOMATION_TESTS

#include "Boss/RPGFrameworkBossCharacter.h"
#include "Boss/RPGFrameworkProofFixture.h"
#include "Engine/Engine.h"
#include "Engine/World.h"
#include "GameFramework/PlayerController.h"

namespace
{
struct FRestartMatrixWorld
{
    UWorld* World=nullptr;
    FRestartMatrixWorld()
    {
        if (!GEngine) return;
        World=UWorld::CreateWorld(EWorldType::Game,false);
        if (World)
        {
            FWorldContext& Context=GEngine->CreateNewWorldContext(EWorldType::Game);
            Context.SetCurrentWorld(World);
            World->InitializeActorsForPlay(FURL());
        }
    }
    ~FRestartMatrixWorld()
    {
        if (World)
        {
            GEngine->DestroyWorldContext(World);
            World->DestroyWorld(false);
        }
    }
    FRestartMatrixWorld(const FRestartMatrixWorld&)=delete;
    FRestartMatrixWorld& operator=(const FRestartMatrixWorld&)=delete;
};
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FBossRestartFailedTerminalIdempotence,
    "OneBossFight.Framework.EncounterRestart.FailedTerminalIdempotence",
    EAutomationTestFlags::EditorContext|EAutomationTestFlags::ProductFilter)
bool FBossRestartFailedTerminalIdempotence::RunTest(const FString&)
{
    FRestartMatrixWorld Scope;
    if (!TestNotNull(TEXT("transient test world is available"),Scope.World)) return false;
    ARPGFrameworkBossCharacter* Boss=Scope.World->SpawnActor<ARPGFrameworkBossCharacter>(FVector(0,0,300),FRotator::ZeroRotator);
    if (!TestNotNull(TEXT("boss actor spawns"),Boss)) return false;
    // Fail() logs its fail-closed ERROR token once by design; the duplicate call below must not log again.
    AddExpectedError(TEXT("token=restart-matrix failure fixture"),EAutomationExpectedErrorFlags::Contains,1);
    Boss->Fail(TEXT("restart-matrix failure fixture"));
    TestTrue(TEXT("public failure entry reaches Failed state"),Boss->Failed());
    const uint64 FailedGeneration=Boss->CurrentGeneration();
    Boss->Fail(TEXT("duplicate restart-matrix failure"));
    TestTrue(TEXT("duplicate terminal failure remains Failed"),Boss->Failed());
    TestEqual(TEXT("duplicate terminal failure does not advance generation"),Boss->CurrentGeneration(),FailedGeneration);
    FString Error;
    TestFalse(TEXT("uninitialized failed boss cannot restart"),Boss->RestartEncounter(FailedGeneration+1,Error));
    TestEqual(TEXT("restart refusal reports state precondition"),Error,FString(TEXT("Framework.Boss.RestartState")));
    TestEqual(TEXT("failed boss generation stays unchanged after refusal"),Boss->CurrentGeneration(),FailedGeneration);
    return true;
}

#endif
