// Copyright One Boss Fight. All Rights Reserved.
// C335 STAGED ONLY: reads saved definitions without modifying them; no gameplay activation.
#include "Misc/AutomationTest.h"
#if WITH_DEV_AUTOMATION_TESTS
#include "Components/SkeletalMeshComponent.h"
#include "Engine/Engine.h"
#include "Engine/SkeletalMesh.h"
#include "Engine/World.h"
#include "EngineUtils.h"
#include "GameFramework/Character.h"
#include "Misc/CommandLine.h"
#include "Misc/Parse.h"
#include "Player/RPGBossHydrationPreflight.h"
#include "Player/RPGBossStagger.h"
#include "Player/RPGBossPhases.h"
#include "Player/RPGBossEncounter.h"
#include "Player/RPGBossDormantWake.h"
#include "Player/RPGBossPosture.h"
#include "Player/RPGBossBleed.h"
#include "Player/RPGBossLowSweep.h"
#include "Player/RPGBossShockwave.h"
#include "Player/RPGBossHealPunish.h"
#include "Player/RPGBossLook.h"
#include "Player/RPGBossCloseClipSwap.h"
#include "Player/RPGBossDeath.h"
#include "UObject/StrongObjectPtr.h"

namespace AuthoredDraftPreflightTests
{
    struct FWorldScope
    {
        UWorld* World = nullptr;
        FWorldScope()
        {
            if (GEngine)
            {
                World = UWorld::CreateWorld(EWorldType::Game, false);
                if (World)
                {
                    GEngine->CreateNewWorldContext(EWorldType::Game).SetCurrentWorld(World);
                    World->InitializeActorsForPlay(FURL());
                }
            }
        }
        ~FWorldScope()
        {
            if (World)
            {
                GEngine->DestroyWorldContext(World);
                World->DestroyWorld(false);
            }
        }
        FWorldScope(const FWorldScope&) = delete;
        FWorldScope& operator=(const FWorldScope&) = delete;
        ACharacter* Spawn(USkeletalMesh* Mesh, const FVector& Location)
        {
            if (!World || !Mesh) return nullptr;
            ACharacter* Actor = World->SpawnActorDeferred<ACharacter>(ACharacter::StaticClass(), FTransform(Location));
            if (Actor)
            {
                Actor->GetMesh()->SetSkeletalMeshAsset(Mesh);
                Actor->FinishSpawning(FTransform(Location));
            }
            return Actor;
        }
    };

    // Identity/lifecycle and context-count snapshot; not a snapshot of arbitrary pack state.
    TArray<FString> Snapshot(UWorld* World)
    {
        TArray<FString> Rows;
        for (TActorIterator<AActor> It(World); It; ++It)
        {
            AActor* Actor = *It;
            Rows.Add(FString::Printf(TEXT("actor=%s begun=%d"), *Actor->GetPathName(), Actor->HasActorBegunPlay()));
            TArray<UActorComponent*> Components;
            Actor->GetComponents(Components);
            for (UActorComponent* Component : Components)
            {
                Rows.Add(FString::Printf(TEXT("component=%s owner=%s registered=%d begun=%d"),
                    *Component->GetPathName(), *GetPathNameSafe(Component->GetOwner()), Component->IsRegistered(), Component->HasBegunPlay()));
            }
        }
        if (const URPGCombatContextSubsystem* Context = World->GetSubsystem<URPGCombatContextSubsystem>())
        {
            Rows.Add(FString::Printf(TEXT("context bound=%d ready=%d"), Context->GetBoundCount(), Context->GetReadyCount()));
        }
        Rows.Sort();
        return Rows;
    }
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FRPGAuthoredDraftProductionPreflightTest,
    "OneBossFight.Binding.AuthoredDraft.SavedProductionPreflight",
    EAutomationTestFlags::EditorContext | EAutomationTestFlags::ProductFilter)
bool FRPGAuthoredDraftProductionPreflightTest::RunTest(const FString& Parameters)
{
    using namespace AuthoredDraftPreflightTests;
    // Explicit identities and hash, never fabricated from the definition or manifest Value strings.
    FString ManifestHash;
    FParse::Value(FCommandLine::Get(), TEXT("DD27jManifestHash="), ManifestHash);
    bool bHashValid = ManifestHash.Len() == 64;
    for (TCHAR C : ManifestHash) bHashValid &= FChar::IsHexDigit(C);
    if (!TestTrue(TEXT("explicit DD27jManifestHash must be 64 hexadecimal digits; operator pins its actual source"), bHashValid)) return false;
    const FName SelectedPhase(TEXT("PhaseTwo"));
    const TCHAR* BossPath = TEXT("/Game/OneBossFight/Data/TypedABIFixtures/AuthoringPreview/BossDrafts/DA_Boss_EmberWarden_Draft.DA_Boss_EmberWarden_Draft");
    const TCHAR* PlayerPath = TEXT("/Game/OneBossFight/Data/TypedABIFixtures/AuthoringPreview/BossDrafts/DA_Player_Hero_Draft_V2.DA_Player_Hero_Draft_V2");
    TStrongObjectPtr<URPGBossDefinition> BossDefinition(LoadObject<URPGBossDefinition>(nullptr, BossPath));
    TStrongObjectPtr<URPGBossDefinition> PlayerDefinition(LoadObject<URPGBossDefinition>(nullptr, PlayerPath));
    AddInfo(FString::Printf(TEXT("[DD27j] loaded boss=%s player=%s manifest=%s phase=%s"),
        *GetPathNameSafe(BossDefinition.Get()), *GetPathNameSafe(PlayerDefinition.Get()), *ManifestHash, *SelectedPhase.ToString()));
    if (!TestNotNull(TEXT("saved Ember Warden definition"), BossDefinition.Get()) ||
        !TestNotNull(TEXT("saved Hero definition; no transient replacement"), PlayerDefinition.Get())) return false;
    const auto Content = RPGCombatRegistry::Legacy();
    if (!TestTrue(TEXT("explicit legacy content lease; not GI provenance"), Content.IsValid())) return false;
    TSharedPtr<const FRPGParticipantConfig> BossConfig, PlayerConfig;
    // Stop at the first actual failed compiler stage; no definition mutation or synthetic factory.
    const FRPGHydrationResult BossResult = RPGCombatHydration::CompileParticipant(*BossDefinition, Content, ManifestHash, BossConfig);
    AddInfo(FString::Printf(TEXT("[DD27j] stage=BossCompile ready=%d output=%d"), BossResult.IsReady(), BossConfig.IsValid()));
    for (const FString& Error : BossResult.Errors) AddError(Error);
    if (!TestTrue(TEXT("saved boss production compile"), BossResult.IsReady() && BossConfig.IsValid())) return false;
    const FRPGHydrationResult PlayerResult = RPGCombatHydration::CompileParticipant(*PlayerDefinition, Content, ManifestHash, PlayerConfig);
    AddInfo(FString::Printf(TEXT("[DD27j] stage=HeroCompile ready=%d output=%d fields=%d"), PlayerResult.IsReady(), PlayerConfig.IsValid(), PlayerDefinition->Fields.Num()));
    for (const FString& Error : PlayerResult.Errors) AddError(Error);
    if (!TestTrue(TEXT("saved Hero production compile; zero rows answered by actual compiler"), PlayerResult.IsReady() && PlayerConfig.IsValid())) return false;
    if (!TestTrue(TEXT("production configs share explicit epoch, no synthetic flag"), !BossConfig->bSyntheticFixture && !PlayerConfig->bSyntheticFixture &&
        BossConfig->Content.Get() == Content.Get() && PlayerConfig->Content.Get() == Content.Get())) return false;
    const bool bHasPhase = BossDefinition->Phases.ContainsByPredicate([SelectedPhase](const FRPGPhaseConfig& P) { return P.PhaseId == SelectedPhase; });
    if (!TestTrue(TEXT("saved definition contains explicitly selected PhaseTwo"), bHasPhase)) return false;

    // Read pack class CDO meshes; never spawn a pack Blueprint or rewrite the saved definitions.
    UClass* BossClass = LoadClass<ACharacter>(nullptr, TEXT("/Game/AdvancedARPGCombat/MeleeCombatSystem/Blueprints/AI/Enemies/ExampleGreatswordBoss/BP_ExampleGreatSwordBoss.BP_ExampleGreatSwordBoss_C"));
    UClass* PlayerClass = LoadClass<ACharacter>(nullptr, TEXT("/Game/AdvancedARPGCombat/MeleeCombatSystem/Blueprints/BP_CombatPlayerCharacter.BP_CombatPlayerCharacter_C"));
    const ACharacter* BossDefault = BossClass ? Cast<ACharacter>(BossClass->GetDefaultObject()) : nullptr;
    const ACharacter* PlayerDefault = PlayerClass ? Cast<ACharacter>(PlayerClass->GetDefaultObject()) : nullptr;
    USkeletalMesh* BossMesh = BossDefault && BossDefault->GetMesh() ? BossDefault->GetMesh()->GetSkeletalMeshAsset() : nullptr;
    USkeletalMesh* PlayerMesh = PlayerDefault && PlayerDefault->GetMesh() ? PlayerDefault->GetMesh()->GetSkeletalMeshAsset() : nullptr;
    if (!TestNotNull(TEXT("observed pack boss CDO mesh"), BossMesh) || !TestNotNull(TEXT("observed pack player CDO mesh"), PlayerMesh)) return false;
    FWorldScope Scope;
    if (!TestNotNull(TEXT("isolated headless world"), Scope.World)) return false;
    ACharacter* Boss = Scope.Spawn(BossMesh, FVector::ZeroVector);
    ACharacter* Player = Scope.Spawn(PlayerMesh, FVector(1000.f, 0.f, 0.f));
    if (!TestNotNull(TEXT("native boss fixture actor"), Boss) || !TestNotNull(TEXT("native target fixture actor"), Player)) return false;
    if (!TestTrue(TEXT("world and participants never begun"), !Scope.World->HasBegunPlay() && !Boss->HasActorBegunPlay() && !Player->HasActorBegunPlay())) return false;
    FRPGHydrationPreflightInput Input;
    Input.ExpectedWorld = Scope.World;
    Input.EncounterInstance = FGuid::NewGuid();
    Input.ExpectedContent = Content;
    FRPGHydrationPreflightRequest BossRequest;
    BossRequest.Actor = Boss; BossRequest.Slot = TEXT("Boss"); BossRequest.TargetSlot = TEXT("Player");
    BossRequest.Role = ERPGPreflightRole::BossCore; BossRequest.Config = BossConfig; BossRequest.SelectedPhaseId = SelectedPhase;
    FRPGHydrationPreflightRequest PlayerRequest;
    PlayerRequest.Actor = Player; PlayerRequest.Slot = TEXT("Player"); PlayerRequest.TargetSlot = TEXT("Boss");
    PlayerRequest.Role = ERPGPreflightRole::TargetOnly; PlayerRequest.Config = PlayerConfig;
    Input.Requests.Add(BossRequest); Input.Requests.Add(PlayerRequest);
    const TArray<FString> Before = Snapshot(Scope.World);
    TSharedPtr<const FRPGHydrationPreflightPlan> Plan;
    const FRPGHydrationResult Preflight = RPGBossHydrationPreflight::CompilePreflight(Input, Plan);
    AddInfo(FString::Printf(TEXT("[DD27j] stage=Preflight ready=%d output=%d"), Preflight.IsReady(), Plan.IsValid()));
    for (const FString& Error : Preflight.Errors) AddError(Error);
    const bool bUnchanged = TestTrue(TEXT("preflight changed no observed actor/component lifecycle identity or context counts"), Before == Snapshot(Scope.World));
    if (!Preflight.IsReady() || !Plan.IsValid())
    {
        TestFalse(TEXT("failed preflight publishes no plan"), Plan.IsValid());
        return false;
    }
    bool bOk = bUnchanged;
    bOk &= TestEqual(TEXT("two participants"), Plan->Participants.Num(), 2);
    bOk &= TestFalse(TEXT("not a complete playable bundle"), Plan->IsCompletePlayableBundle());
    bOk &= TestFalse(TEXT("not a reservation"), Plan->IsReservation());
    bOk &= TestFalse(TEXT("not Ready"), Plan->IsReady());
    if (Plan->Participants.Num() != 2) return false;
    const TArray<UClass*> Expected{URPGBossStagger::StaticClass(), URPGBossPhases::StaticClass(), URPGBossEncounter::StaticClass(),
        URPGBossDormantWake::StaticClass(), URPGBossPosture::StaticClass(), URPGBossBleed::StaticClass(), URPGBossLowSweep::StaticClass(),
        URPGBossShockwave::StaticClass(), URPGBossHealPunish::StaticClass(), URPGBossLook::StaticClass(), URPGBossCloseClipSwap::StaticClass(), URPGBossDeath::StaticClass()};
    const auto& BossPlan = Plan->Participants[0].Plans;
    bOk &= TestEqual(TEXT("exact twelve boss plans"), BossPlan.Num(), 12);
    bOk &= TestEqual(TEXT("no target-only boss plans"), Plan->Participants[1].Plans.Num(), 0);
    TSet<UClass*> Classes; TSet<FName> Names; TSet<FString> Required;
    for (int32 I = 0; I < BossPlan.Num(); ++I)
    {
        const FRPGComponentPlan& P = BossPlan[I];
        AddInfo(FString::Printf(TEXT("[DD27j] plan[%d] class=%s name=%s"), I, *GetPathNameSafe(P.Class), *P.InstanceName.ToString()));
        if (Expected.IsValidIndex(I)) bOk &= TestTrue(TEXT("independent native class order"), P.Class == Expected[I]);
        Classes.Add(P.Class); Names.Add(P.InstanceName);
        for (const FString& Field : P.RequiredFields) { Required.Add(Field); AddInfo(TEXT("[DD27j] required=") + Field); }
    }
    bOk &= TestEqual(TEXT("twelve unique classes"), Classes.Num(), 12);
    bOk &= TestEqual(TEXT("twelve unique instance names"), Names.Num(), 12);
    bOk &= TestEqual(TEXT("110 distinct required paths"), Required.Num(), 110);
    AddInfo(TEXT("[DD27j] scope=ExpandedNativeSubsetPreflight; no Configure, registration, activation, save or gameplay claim"));
    return bOk;
}
#endif
